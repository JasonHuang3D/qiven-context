"""K2 transaction semantics. Adapter and live identity/clock are injected ports."""
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import base64
import json
from pathlib import Path
from typing import Protocol
import yaml
from jsonschema import Draft202012Validator, FormatChecker, ValidationError
from context_snapshot import safe_path, MAX_FILE_BYTES
from lifecycle_graph import lifecycle_errors
from .model import KernelObject, _RECORD_VALIDATORS
from .registry import REGISTRY
from .source_formats import StrictLoader


@dataclass(frozen=True)
class Authentication:
    project_id: str
    principal: str
    permissions: frozenset[str]
    expires_at: datetime
    evidence: str


class IdentityPort(Protocol):
    def authenticate(self, session, project_id: str) -> Authentication | None: ...


@dataclass(frozen=True)
class Outcome:
    status: str
    code: str
    receipt: str | None = None
    successor: str | None = None


class Rejected(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


class BeforeCommitFailure(Exception):
    """Conformance fault: definitely before any commit attempt."""


def utc(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError('semantic timestamps require UTC')
    return parsed


def _raw(encoded):
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError) as exc:
        raise Rejected('invalid_evidence_encoding') from exc
    if len(raw) > MAX_FILE_BYTES:
        raise Rejected('evidence_too_large')
    return raw


def evidence_object(raw, media_type):
    return KernelObject.create('EvidenceObject', {
        'media_type': media_type, 'content_digest': 'sha256:' + sha256(raw).hexdigest(), 'size': len(raw)})


def operation_scope(p):
    result = []
    for op in p['operations']:
        if op['op'] in ('create_record', 'revise_record', 'transition_record'):
            target = op['metadata'].get('id', '<invalid>')
        elif op['op'] == 'relate':
            target = op['source'] + '->' + op['target'] + ':' + op['relation']
        elif op['op'] == 'put_document':
            target = op['path']
        elif op['op'] == 'set_governance':
            target = 'governance'
        else:
            target = 'evidence'
        result.append({'action': op['op'], 'target': target})
    return result


class ContextTransactions:
    def __init__(self, adapter, identity: IdentityPort, *, clock=None, fault=None):
        self.adapter = adapter
        self.identity = identity
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.fault = fault or (lambda stage: None)

    def _auth(self, session, project, principal=None):
        auth = self.identity.authenticate(session, project)
        now = self.clock()
        if (not isinstance(auth, Authentication) or auth.project_id != project
                or (principal is not None and auth.principal != principal)
                or not auth.evidence or not isinstance(auth.permissions, frozenset)
                or not isinstance(auth.expires_at, datetime) or auth.expires_at.tzinfo is None
                or not isinstance(auth.principal, str) or not isinstance(auth.evidence, str)
                or auth.expires_at <= now):
            raise Rejected('unauthorized')
        return auth

    def _snapshot(self, db, digest, project):
        obj = self.adapter.get(db, digest)
        if obj.kind != 'SandboxSnapshot' or obj.payload['project_id'] != project:
            raise Rejected('snapshot_project_mismatch')
        return obj.payload

    def _policy(self, db, snapshot):
        value = self.adapter.get(db, snapshot['governance'])
        if value.kind != 'ReferenceGovernance' or value.payload['project_id'] != snapshot['project_id']:
            raise Rejected('invalid_governance')
        return value.payload

    @staticmethod
    def _permit(auth, policy, actions):
        grants = set(policy['grants'].get(auth.principal, []))
        if not set(actions) <= grants or not set(actions) <= auth.permissions:
            raise Rejected('unauthorized')

    def _access(self, db, session, project, principal=None):
        auth = self._auth(session, project, principal)
        current = self._snapshot(db, self.adapter.head(db, project), project)
        self._permit(auth, self._policy(db, current), ['read_result'])
        return auth

    def _outcome(self, db, row):
        if row is None or row['status'] == 'pending':
            return Outcome('outcome_unknown', 'pending_or_absent')
        if row['status'] == 'not_committed':
            return Outcome('not_committed', row['reason'])
        receipt = self.adapter.get(db, row['receipt'])
        p = receipt.payload
        if (receipt.kind != 'TransactionReceipt' or p['request_digest'] != row['request']
                or p['project_id'] != row['project'] or p['principal'] != row['principal']
                or p['idempotency_key'] != row['key'] or p['transaction_id'] != row['transaction_id']):
            raise ValueError('durable receipt binding mismatch')
        return Outcome('committed', 'committed', receipt.digest, p['successor_snapshot'])

    def get_transaction_result(self, project, key, session):
        try:
            with self.adapter.connect() as db:
                self.adapter.begin_read(db)
                auth = self._access(db, session, project)
                return self._outcome(db, self.adapter.lookup(db, project, auth.principal, key))
        except Rejected as exc:
            return Outcome('access_denied', exc.code)
        except Exception:
            return Outcome('outcome_unknown', 'storage_or_identity_unavailable')

    def _request(self, request):
        obj = request if isinstance(request, KernelObject) else KernelObject.create('TransactionRequest', request)
        obj = KernelObject(obj.encoded)
        if obj.kind != 'TransactionRequest':
            raise ValueError('expected transaction request')
        utc(obj.payload['semantic_time'])
        return obj

    def validate_transaction(self, request, session):
        """Advisory only: does not reserve keys, write objects or issue a grant."""
        try:
            request = self._request(request)
            p = request.payload
            with self.adapter.connect() as db:
                self.adapter.begin_read(db)
                auth = self._access(db, session, p['project_id'], p['principal'])
                if self.adapter.head(db, p['project_id']) != p['base_snapshot']:
                    raise Rejected('stale_base')
                base = self._snapshot(db, p['base_snapshot'], p['project_id'])
                self._permit(auth, self._policy(db, base), [op['op'] for op in p['operations']])
                self._prepare(db, request, base)
            return Outcome('advisory_valid', 'not_an_authority_grant')
        except Rejected as exc:
            return Outcome('not_committed', exc.code)
        except (ValueError, KeyError, TypeError, ValidationError, yaml.YAMLError):
            return Outcome('not_committed', 'invalid_request_or_evidence')
        except Exception:
            return Outcome('outcome_unknown', 'storage_or_identity_unavailable')

    propose_transaction = validate_transaction

    def commit_transaction(self, request, session, *, _abort=False):
        try:
            request = self._request(request)
        except (ValueError, TypeError, ValidationError):
            return Outcome('not_committed', 'invalid_request')
        p = request.payload
        commit_started = False
        try:
            # Reservation is durable and noncanonical. A crash leaves a resumable
            # pending key; it cannot free that key for a different request payload.
            with self.adapter.connect() as db:
                self.adapter.begin(db)
                self._access(db, session, p['project_id'], p['principal'])
                reserved = self.adapter.reserve(db, request)
                if reserved != 'ok':
                    db.rollback()
                    return Outcome('not_committed', reserved)
                db.commit()
            self.fault('after_reservation')
            with self.adapter.connect() as db:
                self.adapter.begin(db)
                self._access(db, session, p['project_id'], p['principal'])
                row = self.adapter.lookup(db, p['project_id'], p['principal'], p['idempotency_key'])
                if row['status'] != 'pending':
                    return self._outcome(db, row)  # BEFORE stale-base checks.
                try:
                    if _abort:
                        raise Rejected('aborted')
                    if self.adapter.head(db, p['project_id']) != p['base_snapshot']:
                        raise Rejected('stale_base')
                    base = self._snapshot(db, p['base_snapshot'], p['project_id'])
                    prepared = self._prepare(db, request, base)
                    self.fault('before_authorization')
                    # Old governance and LIVE authentication, not an advisory result
                    # or caller-supplied AuthorityDecision, admit this exact request.
                    auth = self._auth(session, p['project_id'], p['principal'])
                    self._permit(auth, self._policy(db, base), [op['op'] for op in p['operations']] + ['read_result'])
                    decision = KernelObject.create('AuthorityDecision', {
                        'project_id': p['project_id'], 'principal': auth.principal,
                        'request_digest': request.digest, 'base_snapshot': p['base_snapshot'],
                        'governance_version': p['governance_version'], 'operation_scope': operation_scope(p),
                        'checked_at': self.clock().astimezone(timezone.utc).isoformat().replace('+00:00', 'Z'),
                        'authentication_evidence': auth.evidence, 'decision': 'allow',
                        'authority_scope': 'reference-sandbox'})
                    snapshot, receipt, objects, blobs = self._finish(request, base, prepared, decision)
                    self.adapter.publish(db, request, snapshot, receipt, objects, blobs)
                    self.fault('before_commit')
                except (Rejected, BeforeCommitFailure) as exc:
                    # Roll back staged objects/head/result before recording a definite rejection.
                    db.rollback()
                    self.adapter.begin(db)
                    latest = self.adapter.lookup(db, p['project_id'], p['principal'], p['idempotency_key'])
                    if latest['status'] == 'pending':
                        self.adapter.reject(db, p, exc.code if isinstance(exc, Rejected) else 'injected_precommit_failure')
                        db.commit()
                    return self._outcome(db, self.adapter.lookup(db, p['project_id'], p['principal'], p['idempotency_key']))
                except (ValueError, KeyError, TypeError, ValidationError, yaml.YAMLError) as exc:
                    db.rollback()
                    self.adapter.begin(db)
                    self.adapter.reject(db, p, 'invalid_request_or_evidence')
                    db.commit()
                    return self._outcome(db, self.adapter.lookup(db, p['project_id'], p['principal'], p['idempotency_key']))
                commit_started = True
                db.commit()
            self.fault('after_commit')
            return Outcome('committed', 'committed', receipt.digest, snapshot.digest)
        except Rejected as exc:
            # Admission/access refusal does not assert anything about a possibly
            # earlier execution under this key.
            return Outcome('access_denied', exc.code)
        except Exception:
            return Outcome('outcome_unknown', 'commit_acknowledgement_unknown' if commit_started else 'pending_attempt_requires_recovery')

    def abort_transaction(self, request, session):
        return self.commit_transaction(request, session, _abort=True)

    def _prepare(self, db, request, base):
        p = request.payload
        if p['governance_version'] != base['governance']:
            raise Rejected('governance_version_mismatch')
        for dependency in p['depends_on']:
            if not self.adapter.dependency_committed(db, p['project_id'], dependency):
                raise Rejected('dependency_outcome_unknown')
        original = {e['record_id']: e['revision'] for e in base['records']}
        records = {rid: self.adapter.get(db, digest).payload for rid, digest in original.items()}
        for rid, rec in records.items():
            if rec['project_id'] != p['project_id'] or rec['record_id'] != rid:
                raise Rejected('record_binding_mismatch')
        touched = set()
        reasons = {}
        docs = {d['path']: d['document'] for d in base['documents']}
        objects = {}
        blobs = {}
        available_evidence = set(base['evidence'])
        governance = base['governance']
        changed_docs = set()

        def touch(rid, rationale):
            touched.add(rid)
            reasons.setdefault(rid, []).append(rationale)
            if rid not in p['expected_revisions'] or p['expected_revisions'][rid] != original.get(rid):
                raise Rejected('expected_revision_mismatch')

        def stage(value):
            objects[value.digest] = value
            return value.digest

        for op in p['operations']:
            action = op['op']
            if action in ('create_record', 'revise_record', 'transition_record'):
                rid = op['metadata'].get('id')
                if not isinstance(rid, str):
                    raise Rejected('invalid_record_id')
                touch(rid, op['rationale'])
                existing = records.get(rid)
                if (action == 'create_record') != (existing is None):
                    raise Rejected('record_existence_conflict')
                _RECORD_VALIDATORS[op['record_kind']].validate(op['metadata'])
                if existing:
                    if (existing['record_kind'] != op['record_kind']
                            or existing['metadata']['created_at'] != op['metadata']['created_at']):
                        raise Rejected('record_identity_change')
                    if utc(op['metadata']['updated_at']) < utc(existing['metadata']['updated_at']):
                        raise Rejected('record_time_regression')
                    if action == 'revise_record' and any(existing['metadata'].get(k, []) != op['metadata'].get(k, [])
                                                        for k in ('status', 'supersedes', 'superseded_by')):
                        raise Rejected('lifecycle_requires_explicit_transition')
                if utc(op['metadata']['updated_at']) != utc(p['semantic_time']):
                    raise Rejected('record_semantic_time_mismatch')
                if utc(op['metadata']['created_at']) > utc(op['metadata']['updated_at']):
                    raise Rejected('invalid_record_time')
                records[rid] = {'record_id': rid, 'record_kind': op['record_kind'],
                                'metadata': op['metadata'], 'body': op['body']}
            elif action == 'relate':
                a, b = op['source'], op['target']
                if a == b or a not in records or b not in records:
                    raise Rejected('invalid_relation_endpoint')
                pairs = [(a, b, op['relation'])]
                if op['relation'] == 'supersedes':
                    pairs.append((b, a, 'superseded_by'))
                for rid, target, field in pairs:
                    touch(rid, op['rationale'])
                    metadata = records[rid]['metadata']
                    values = list(metadata.get(field, []))
                    if (target in values) == (op['mode'] == 'add'):
                        raise Rejected('relation_existence_conflict')
                    if op['mode'] == 'add': values.append(target)
                    else: values.remove(target)
                    metadata[field] = values
                    metadata['updated_at'] = p['semantic_time']
            elif action == 'add_evidence':
                raw = _raw(op['content_base64'])
                value = evidence_object(raw, op['media_type'])
                stage(value); blobs[value.payload['content_digest']] = raw
                available_evidence.add(value.digest)
            elif action == 'add_external_evidence':
                value = KernelObject.create('ExternalEvidenceReference', {
                    'reference': op['reference'], 'media_type': op['media_type'],
                    'expected_content_digest': op['expected_content_digest'], 'availability': 'unverified'})
                available_evidence.add(stage(value))
            elif action == 'put_document':
                path = safe_path(op['path'])
                if path != op['path'] or not (path in ('state/current.md', 'state/active-work.yaml')
                                               or path.startswith(('projects/', 'views/'))):
                    raise Rejected('unsupported_document_namespace')
                if path in changed_docs or docs.get(path) != op['expected_document']:
                    raise Rejected('expected_document_mismatch')
                changed_docs.add(path)
                raw = _raw(op['content_base64'])
                raw.decode('utf-8')
                value = evidence_object(raw, 'application/octet-stream')
                stage(value); blobs[value.payload['content_digest']] = raw
                available_evidence.add(value.digest)
                docs[path] = stage(KernelObject.create('SourceDocument', {
                    'project_id': p['project_id'], 'path': path, 'evidence': value.digest}))
            elif action == 'set_governance':
                if op['policy']['project_id'] != p['project_id']:
                    raise Rejected('governance_project_mismatch')
                governance = stage(KernelObject.create('ReferenceGovernance', op['policy']))
        if touched != set(p['expected_revisions']):
            raise Rejected('unexpected_revision_preconditions')
        for rid in touched:
            if rid in original:
                previous = self.adapter.get(db, original[rid]).payload['metadata']
                if utc(records[rid]['metadata']['updated_at']) < utc(previous['updated_at']):
                    raise Rejected('record_time_regression')
            _RECORD_VALIDATORS[records[rid]['record_kind']].validate(records[rid]['metadata'])
        if lifecycle_errors({rid: rec['metadata'] for rid, rec in records.items()}):
            raise Rejected('invalid_lifecycle')
        if touched and not p['evidence']:
            raise Rejected('incomplete_evidence')
        for digest in p['evidence']:
            if digest not in available_evidence:
                raise Rejected('incomplete_evidence')
            value = objects.get(digest) or self.adapter.get(db, digest)
            if value.kind == 'EvidenceObject':
                raw = blobs.get(value.payload['content_digest'])
                if raw is None: raw = self.adapter.blob(db, value.payload['content_digest'])
                if len(raw) != value.payload['size']:
                    raise Rejected('incomplete_evidence')
            elif value.kind != 'ExternalEvidenceReference':
                raise Rejected('invalid_evidence_kind')
        self._validate_documents(db, docs, objects, blobs, changed_docs)
        return records, original, touched, reasons, docs, objects, blobs, governance, available_evidence

    def _validate_documents(self, db, docs, objects, blobs, changed):
        def content(path):
            doc = objects.get(docs[path]) or self.adapter.get(db, docs[path])
            evidence = objects.get(doc.payload['evidence']) or self.adapter.get(db, doc.payload['evidence'])
            digest = evidence.payload['content_digest']
            return blobs[digest] if digest in blobs else self.adapter.blob(db, digest)
        for path in changed:
            if not path.endswith(('.yaml', '.yml')):
                continue
            raw = content(path).decode('utf-8')
            if any(isinstance(event, yaml.AliasEvent) for event in yaml.parse(raw)):
                raise Rejected('unsupported_document_alias')
            data = yaml.load(raw, Loader=StrictLoader)
            if path == 'state/active-work.yaml':
                schema = json.loads((Path(__file__).resolve().parents[2]/'schema/active-work-state.schema.json').read_text())
                Draft202012Validator(schema, format_checker=FormatChecker()).validate(data)
            elif path.startswith('views/') and path.count('/') == 1:
                if (not isinstance(data, dict) or not isinstance(data.get('project_context'), dict)
                        or data['project_context'].get('override_allowed') is not False
                        or data.get('id') != Path(path).stem or data.get('status') != 'active'
                        or not isinstance(data.get('environments', []), list)
                        or not isinstance(data.get('workflows', {}), dict)):
                    raise Rejected('invalid_view')
                refs = list(data.get('environments', [])) + list(data.get('workflows', {}).values())
                if not all(isinstance(ref, str) for ref in refs):
                    raise Rejected('invalid_view')
                if any(ref not in docs for ref in refs):
                    raise Rejected('incomplete_view')

    def _finish(self, request, base, prepared, decision):
        p = request.payload
        records, original, touched, reasons, docs, objects, blobs, governance, evidence = prepared
        revisions = dict(original)
        objects[decision.digest] = decision
        for rid in sorted(touched):
            record = records[rid]
            value = KernelObject.create('NativeRecordRevision', {
                'project_id': p['project_id'], 'record_id': rid, 'record_kind': record['record_kind'],
                'record_schema': 'sha256:' + REGISTRY[record['record_kind']][2],
                'metadata': record['metadata'], 'body': record['body'],
                'creating_transaction': p['transaction_id'], 'predecessor_revision': original.get(rid),
                'principal': p['principal'], 'authority_decision': decision.digest,
                'evidence': p['evidence'], 'rationale': reasons[rid]})
            objects[value.digest] = value
            revisions[rid] = value.digest
        snapshot = KernelObject.create('SandboxSnapshot', {
            'project_id': p['project_id'], 'base_snapshot': p['base_snapshot'],
            'import_origin': base['import_origin'], 'governance': governance,
            'creating_transaction': p['transaction_id'], 'instance_state': 'quarantined',
            'records': [{'record_id': rid, 'revision': digest} for rid, digest in sorted(revisions.items())],
            'documents': [{'path': path, 'document': digest} for path, digest in sorted(docs.items())],
            'evidence': sorted(evidence)})
        receipt = KernelObject.create('TransactionReceipt', {
            'project_id': p['project_id'], 'transaction_id': p['transaction_id'], 'principal': p['principal'],
            'idempotency_key': p['idempotency_key'], 'request_digest': request.digest,
            'base_snapshot': p['base_snapshot'], 'successor_snapshot': snapshot.digest,
            'revision_digests': [revisions[rid] for rid in sorted(touched)],
            'authority_decision': decision.digest, 'outcome': 'committed', 'authority_scope': 'reference-sandbox'})
        return snapshot, receipt, list(objects.values()), blobs
