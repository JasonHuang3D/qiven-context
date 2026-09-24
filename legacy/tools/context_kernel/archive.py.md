# [SEALED] tools/context_kernel/archive.py

> Museum piece (ADR-0040/ADR-0041, sealed 2026-09-21). Original
> location: `tools/context_kernel/archive.py`. Do not execute — this is historical text
> only; the `.md` extension makes accidental execution impossible.

````python
"""K4 canonical closure exports and read-only quarantine restoration.

Manifest identity excludes live availability. Delivery integrity is a separate
hash. This is not an authority/power-loss/operational-journal recovery protocol.
"""
from dataclasses import dataclass
from hashlib import sha256
import base64
import json
import re

from .model import KernelObject, MemoryStore
from .serialization import _check, _pairs
from .reads import KernelReadSnapshot
from .transactions import operation_scope, utc

FORMAT = 'qiven-canonical-context'
PROFILE = 'canonical-continuity-v1'
MAX_PACKAGE_BYTES = 256 * 1024 * 1024
MAX_CLOSURE_BYTES = 128 * 1024 * 1024
MAX_OBJECTS = 100000
SNAPSHOTS = ('ProjectSnapshot', 'SandboxSnapshot')
REVISIONS = ('RecordRevision', 'NativeRecordRevision')
EVIDENCE = ('EvidenceObject', 'ExternalEvidenceReference')


def encode(value):
    _check(value)
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    if len(raw) > MAX_PACKAGE_BYTES:
        raise ValueError('export exceeds package byte limit')
    return raw


def parse(raw):
    if type(raw) is not bytes or len(raw) > MAX_PACKAGE_BYTES:
        raise ValueError('invalid package bytes or size')
    value = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs)
    if encode(value) != raw:
        raise ValueError('noncanonical package encoding')
    return value


def digest(domain, value):
    return 'sha256:' + sha256(b'qiven.context.export\0v1\0' + domain.encode() + b'\0' + encode(value)).hexdigest()


def b64(raw):
    return base64.b64encode(raw).decode('ascii')


def unb64(text, limit):
    if not isinstance(text, str) or len(text) > ((limit + 2) // 3) * 4:
        raise ValueError('encoded content exceeds limit')
    raw = base64.b64decode(text, validate=True)
    if len(raw) > limit or b64(raw) != text:
        raise ValueError('invalid content encoding')
    return raw


def screen_known_secrets(raw):
    # Deliberately bounded detection, not a claim to recognize arbitrary secrets.
    if re.search(rb'-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----', raw) or re.search(
            rb'(?im)^\s*(?:api_key|access_token|private_key|password)\s*:\s*["\']?[^\s"\']{8,}', raw):
        raise ValueError('known secret-bearing content requires governed remediation')


def closure(get_object, snapshot_digest, receipt_lookup):
    """Enumerate declared typed edges, including opaque transaction->receipt links."""
    objects, transactions, blobs, external = {}, {}, {}, []
    pending = [(snapshot_digest, SNAPSHOTS)]
    project = None
    total = 0

    def transaction(tx):
        key = receipt_lookup(project, tx)
        if not isinstance(key, str):
            raise ValueError('missing committed transaction receipt')
        if tx in transactions and transactions[tx] != key:
            raise ValueError('transaction receipt mapping conflict')
        transactions[tx] = key
        pending.append((key, ('TransactionReceipt',)))

    while pending:
        key, kinds = pending.pop()
        value = objects.get(key)
        if value is None:
            try:
                value = KernelObject(get_object(key).encoded)
            except KeyError as exc:
                raise ValueError('missing canonical object in export closure') from exc
            if value.digest != key:
                raise ValueError('export object digest mismatch')
        if value.kind not in kinds:
            raise ValueError('export object kind mismatch')
        if key in objects:
            continue
        total += len(value.encoded)
        if len(objects) >= MAX_OBJECTS or total > MAX_CLOSURE_BYTES:
            raise ValueError('semantic closure exceeds resource limit')
        objects[key] = value
        p = value.payload
        if project is None:
            project = p['project_id']
        if 'project_id' in p and p['project_id'] != project:
            raise ValueError('cross-project export reference')
        def edge(ref, allowed):
            if ref is not None: pending.append((ref, allowed))
        kind = value.kind
        if kind in SNAPSHOTS:
            for e in p['records']: edge(e['revision'], REVISIONS)
            for e in p['documents']: edge(e['document'], ('SourceDocument',))
            edge(p['base_snapshot'], SNAPSHOTS)
            if kind == 'ProjectSnapshot':
                edge(p['source']['commit_evidence'], ('EvidenceObject',))
            else:
                edge(p['import_origin'], ('ProjectSnapshot',))
                edge(p['governance'], ('ReferenceGovernance',))
                for e in p['evidence']: edge(e, EVIDENCE)
                if p['creating_transaction'] is not None: transaction(p['creating_transaction'])
        elif kind == 'SourceDocument':
            edge(p['evidence'], ('EvidenceObject',))
        elif kind == 'RecordRevision':
            edge(p['source_document'], ('SourceDocument',))
        elif kind == 'NativeRecordRevision':
            edge(p['predecessor_revision'], REVISIONS)
            edge(p['authority_decision'], ('AuthorityDecision',))
            for e in p['evidence']: edge(e, EVIDENCE)
            transaction(p['creating_transaction'])
        elif kind == 'AuthorityDecision':
            edge(p['request_digest'], ('TransactionRequest',))
            edge(p['base_snapshot'], ('SandboxSnapshot',))
            edge(p['governance_version'], ('ReferenceGovernance',))
        elif kind == 'TransactionRequest':
            edge(p['base_snapshot'], ('SandboxSnapshot',))
            edge(p['governance_version'], ('ReferenceGovernance',))
            for e in p['evidence']: edge(e, EVIDENCE)
            for e in p['expected_revisions'].values(): edge(e, REVISIONS)
            for tx in p['depends_on']: transaction(tx)
        elif kind == 'TransactionReceipt':
            if p['transaction_id'] in transactions and transactions[p['transaction_id']] != key:
                raise ValueError('receipt identity conflict')
            transactions[p['transaction_id']] = key
            edge(p['request_digest'], ('TransactionRequest',))
            edge(p['base_snapshot'], ('SandboxSnapshot',))
            edge(p['successor_snapshot'], ('SandboxSnapshot',))
            edge(p['authority_decision'], ('AuthorityDecision',))
            for e in p['revision_digests']: edge(e, ('NativeRecordRevision',))
        elif kind == 'EvidenceObject':
            raw_digest, size = p['content_digest'], p['size']
            if size > 8 * 1024 * 1024:
                raise ValueError('raw evidence exceeds per-item limit')
            if raw_digest in blobs and blobs[raw_digest] not in (None, size):
                raise ValueError('conflicting raw evidence size')
            blobs[raw_digest] = size
        elif kind == 'ExternalEvidenceReference':
            external.append({'object': key, 'content_digest': p['expected_content_digest']})
            if p['expected_content_digest'] is not None:
                blobs.setdefault(p['expected_content_digest'], None)
        elif kind != 'ReferenceGovernance':
            raise ValueError('unsupported export object kind')
    _bindings(objects, transactions)
    manifest = {'format': FORMAT, 'version': 1, 'serialization_version': 1,
                'project_id': project, 'snapshot': snapshot_digest,
                'objects': [{'digest': k, 'kind': v.kind, 'size': len(v.encoded)} for k, v in sorted(objects.items())],
                'transactions': [{'transaction_id': tx, 'receipt': ref} for tx, ref in sorted(transactions.items())],
                'blobs': [{'digest': k, 'size': size} for k, size in sorted(blobs.items())],
                'external_references': sorted(external, key=lambda e: e['object'])}
    return manifest, objects


def _bindings(objects, transactions):
    keys = set()
    for value in objects.values():
        p = value.payload
        if value.kind == 'TransactionReceipt':
            request = objects[p['request_digest']].payload
            decision = objects[p['authority_decision']].payload
            successor = objects[p['successor_snapshot']].payload
            if (any(p[k] != request[k] for k in ('project_id', 'transaction_id', 'principal', 'idempotency_key', 'base_snapshot'))
                    or decision['request_digest'] != p['request_digest']
                    or any(decision[k] != request[k] for k in ('project_id', 'principal', 'base_snapshot', 'governance_version'))
                    or decision['operation_scope'] != operation_scope(request)
                    or successor['creating_transaction'] != p['transaction_id']
                    or successor['base_snapshot'] != p['base_snapshot']
                    or objects[request['base_snapshot']].payload['governance'] != request['governance_version']):
                raise ValueError('transaction/authority/snapshot binding mismatch')
            key = (p['principal'], p['idempotency_key'])
            if key in keys: raise ValueError('duplicate retained idempotency key')
            keys.add(key)
            selected = {e['revision'] for e in successor['records']}
            if not set(p['revision_digests']) <= selected:
                raise ValueError('receipt revision absent from successor')
        elif value.kind == 'SandboxSnapshot' and p['creating_transaction'] is not None:
            if objects[transactions[p['creating_transaction']]].payload['successor_snapshot'] != value.digest:
                raise ValueError('snapshot creation receipt mismatch')
        elif value.kind == 'NativeRecordRevision':
            receipt = objects[transactions[p['creating_transaction']]].payload
            if (value.digest not in receipt['revision_digests'] or p['principal'] != receipt['principal']
                    or p['authority_decision'] != receipt['authority_decision']
                    or p['predecessor_revision'] != objects[receipt['request_digest']].payload['expected_revisions'].get(p['record_id'])):
                raise ValueError('native revision receipt mismatch')


@dataclass(frozen=True)
class CanonicalExport:
    encoded: bytes

    @property
    def value(self): return parse(self.encoded)


def export_snapshot(get_object, get_blob, snapshot, *, receipt_lookup=None,
                    access_policy, observed_at, omit=None):
    utc(observed_at)
    if not isinstance(access_policy, str) or not access_policy.strip():
        raise ValueError('explicit export access-policy reference required')
    manifest, objects = closure(get_object, snapshot, receipt_lookup or (lambda *_: None))
    omissions, raw_blobs = [], {}
    omit = {} if omit is None else dict(omit)
    if not set(omit) <= {e['digest'] for e in manifest['blobs']}:
        raise ValueError('unknown evidence omission')
    total = 0
    for obj in objects.values(): screen_known_secrets(obj.encoded)
    for entry in manifest['blobs']:
        key = entry['digest']
        if key in omit:
            if not isinstance(omit[key], str) or not omit[key].strip():
                raise ValueError('omission requires a reason')
            omissions.append({'digest': key, 'reason': omit[key]})
            continue
        try:
            raw = get_blob(key)
        except (KeyError, FileNotFoundError):
            omissions.append({'digest': key, 'reason': 'unavailable'})
            continue
        if (type(raw) is not bytes or len(raw) > 8 * 1024 * 1024
                or (entry['size'] is not None and len(raw) != entry['size'])
                or 'sha256:' + sha256(raw).hexdigest() != key):
            raise ValueError('export raw evidence integrity failure')
        total += len(raw)
        if total > MAX_CLOSURE_BYTES: raise ValueError('raw closure exceeds resource limit')
        screen_known_secrets(raw)
        raw_blobs[key] = b64(raw)
    content = {'manifest': manifest, 'manifest_digest': digest('manifest', manifest),
               'objects': {k: b64(v.encoded) for k, v in sorted(objects.items())},
               'delivery': {'profile': PROFILE, 'access_policy': access_policy, 'observed_at': observed_at,
                            'included': sorted(raw_blobs), 'omissions': omissions,
                            'instance_state': 'quarantined', 'operational_journal': 'not-exported'},
               'blobs': raw_blobs}
    return CanonicalExport(encode({**content, 'package_digest': digest('package', content)}))


def export_sqlite(adapter, project, *, snapshot=None, **kwargs):
    with adapter.connect() as db:
        adapter.begin_read(db)
        selected = snapshot or adapter.head(db, project)
        if adapter.get(db, selected).payload['project_id'] != project:
            raise ValueError('export project mismatch')
        def receipt_lookup(project_id, tx):
            row = db.execute("SELECT receipt FROM attempts WHERE project=? AND transaction_id=? AND status='committed'", (project_id, tx)).fetchone()
            return row['receipt'] if row else None
        return export_snapshot(lambda key: adapter.get(db, key), lambda key: adapter.blob(db, key),
                               selected, receipt_lookup=receipt_lookup, **kwargs)


@dataclass(frozen=True)
class RestoredArchive:
    store: MemoryStore
    snapshot: str
    manifest_digest: str
    report_bytes: bytes
    transactions: tuple

    @property
    def report(self): return parse(self.report_bytes)

    def to_sqlite(self, adapter):
        # Missing operational reservations/rejections MUST NOT enable fresh writes.
        if not self.report['complete']:
            raise ValueError('partial recovery cannot materialize a runnable adapter')
        with adapter.connect() as db:
            adapter.begin(db)
            try:
                if any(db.execute('SELECT 1 FROM ' + table + ' LIMIT 1').fetchone() for table in
                       ('objects', 'blobs', 'projects', 'attempts', 'write_blocks')):
                    raise ValueError('restore requires an empty adapter')
                for value in self.store.objects.values(): adapter.put(db, value)
                for key, raw in self.store._blobs.items(): adapter.put_blob(db, key, raw)
                project = self.store.get(self.snapshot).payload['project_id']
                for tx, receipt_key in self.transactions:
                    p = self.store.get(receipt_key).payload
                    db.execute('INSERT INTO attempts VALUES (?,?,?,?,?,?,?,?)',
                               (project, p['principal'], p['idempotency_key'], p['request_digest'], tx,
                                'committed', receipt_key, 'committed'))
                db.execute('INSERT INTO projects VALUES (?,?,?)', (project, self.snapshot, 'quarantined'))
                db.execute('INSERT INTO write_blocks VALUES (?,?)', (project, 'restored_read_only'))
                db.commit()
            except BaseException:
                db.rollback()
                raise
        return self.snapshot


def restore_export(raw):
    package = parse(raw)
    if set(package) != {'manifest', 'manifest_digest', 'objects', 'delivery', 'blobs', 'package_digest'}:
        raise ValueError('unsupported export envelope')
    content = {k: v for k, v in package.items() if k != 'package_digest'}
    if digest('package', content) != package['package_digest']:
        raise ValueError('package digest mismatch')
    manifest = package['manifest']
    if digest('manifest', manifest) != package['manifest_digest']:
        raise ValueError('semantic manifest digest mismatch')
    if (manifest.get('format') != FORMAT or type(manifest.get('version')) is not int
            or manifest['version'] != 1 or manifest.get('serialization_version') != 1):
        raise ValueError('unsupported export version')
    delivery = package['delivery']
    if (set(delivery) != {'profile', 'access_policy', 'observed_at', 'included', 'omissions', 'instance_state', 'operational_journal'}
            or delivery['profile'] != PROFILE or delivery['instance_state'] != 'quarantined'
            or delivery['operational_journal'] != 'not-exported'
            or not isinstance(delivery['access_policy'], str) or not delivery['access_policy'].strip()):
        raise ValueError('unsupported recovery profile/delivery')
    utc(delivery['observed_at'])
    if not isinstance(package['objects'], dict) or len(package['objects']) > MAX_OBJECTS:
        raise ValueError('invalid object delivery')
    store = MemoryStore()
    total = 0
    for key, text in package['objects'].items():
        encoded = unb64(text, 16 * 1024 * 1024)
        total += len(encoded)
        if total > MAX_CLOSURE_BYTES: raise ValueError('object delivery too large')
        screen_known_secrets(encoded)
        value = KernelObject(encoded)
        if value.digest != key: raise ValueError('delivered object digest mismatch')
        store.put(value)
    mappings = manifest['transactions']
    txs = {e['transaction_id']: e['receipt'] for e in mappings}
    if len(txs) != len(mappings): raise ValueError('duplicate transaction mapping')
    rebuilt, reachable = closure(store.get, manifest['snapshot'], lambda _, tx: txs.get(tx))
    if encode(rebuilt) != encode(manifest) or set(reachable) != set(package['objects']):
        raise ValueError('semantic closure missing, extra or inconsistent')
    declared = {e['digest']: e['size'] for e in manifest['blobs']}
    if not isinstance(package['blobs'], dict) or delivery['included'] != sorted(package['blobs']):
        raise ValueError('included evidence manifest mismatch')
    missing = {}
    for item in delivery['omissions']:
        if set(item) != {'digest', 'reason'} or not isinstance(item['reason'], str) or not item['reason'].strip() or item['digest'] in missing:
            raise ValueError('invalid omission diagnostic')
        missing[item['digest']] = item['reason']
    if (set(missing) & set(package['blobs']) or set(missing) | set(package['blobs']) != set(declared)):
        raise ValueError('undeclared or unexplained evidence omission')
    total = 0
    for key, text in package['blobs'].items():
        content = unb64(text, 8 * 1024 * 1024)
        total += len(content)
        if total > MAX_CLOSURE_BYTES: raise ValueError('raw delivery too large')
        screen_known_secrets(content)
        if (declared[key] is not None and len(content) != declared[key]) or store.put_blob(content) != key:
            raise ValueError('delivered raw evidence integrity mismatch')
    unknown = [e['object'] for e in manifest['external_references'] if e['content_digest'] is None]
    complete = not missing and not unknown
    if complete:
        # Validate current source/read closure; actual continuity query corpus is a
        # separate acceptance proof, not manufactured by a successful checksum.
        KernelReadSnapshot.capture(store.get, store.blob, manifest['snapshot'])
    report = {'profile': PROFILE, 'complete': complete, 'missing_evidence': missing,
              'unverifiable_external_references': unknown, 'instance_state': 'quarantined',
              'authorization': 'not_granted', 'writes_enabled': False,
              'operational_journal': 'not-restored', 'continuity': 'requires-corpus-validation'}
    return RestoredArchive(store, manifest['snapshot'], package['manifest_digest'], encode(report), tuple(sorted(txs.items())))

````
