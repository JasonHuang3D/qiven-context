"""Import an exact supported Git tree; never publish a canonical engine head."""
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import yaml
from jsonschema import Draft202012Validator, FormatChecker
from context_snapshot import SourceSnapshot, _git
from context_inputs import mandatory_paths, checked_yaml
from lifecycle_graph import lifecycle_errors
from .model import KernelObject, MemoryStore, ProjectId, RecordId

from .registry import REGISTRY


class StrictLoader(yaml.SafeLoader):
    pass


# Timestamps remain strings; aliases and duplicate keys cannot erase assertions.
StrictLoader.yaml_implicit_resolvers = {
    k: [(tag, rule) for tag, rule in rules if tag != 'tag:yaml.org,2002:timestamp']
    for k, rules in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def _mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str) or key in result:
            raise ValueError('duplicate or non-string YAML key')
        result[key] = loader.construct_object(value_node)
    return result


StrictLoader.add_constructor('tag:yaml.org,2002:map', _mapping)


def _front(raw):
    text = raw.decode('utf-8')
    if not text.startswith('---\n') or '\n---\n' not in text[4:]:
        raise ValueError('canonical record missing front matter')
    header, body = text[4:].split('\n---\n', 1)
    if any(isinstance(event, yaml.AliasEvent) for event in yaml.parse(header)):
        raise ValueError('YAML aliases are unsupported in registered records')
    metadata = yaml.load(header, Loader=StrictLoader)
    if not isinstance(metadata, dict):
        raise ValueError('canonical metadata must be a mapping')
    return metadata, body


@dataclass(frozen=True)
class ImportedSnapshot:
    store: MemoryStore
    snapshot_digest: str
    receipt_digest: str

    @property
    def snapshot(self):
        return self.store.get(self.snapshot_digest)

    def raw_sources(self):
        result = {}
        for entry in self.snapshot.payload['documents']:
            document = self.store.get(entry['document'])
            evidence = self.store.get(document.payload['evidence'])
            result[entry['path']] = self.store.blob(evidence.payload['content_digest'])
        return result

    def verify(self):
        """Prove closure/kinds/digests and raw-source agreement, not authority."""
        snapshot = self.snapshot.payload
        records = {}
        documents = {}
        for entry in snapshot['documents']:
            path = entry['path']
            doc = self.store.get(entry['document'])
            if doc.kind != 'SourceDocument' or doc.payload['path'] != path or doc.payload['project_id'] != snapshot['project_id']:
                raise ValueError('snapshot document binding mismatch')
            if path in documents:
                raise ValueError('duplicate document path')
            documents[path] = doc
        if list(documents) != sorted(documents):
            raise ValueError('document manifest is not sorted')
        document_digests = {d.digest for d in documents.values()}
        for entry in snapshot['records']:
            revision = self.store.get(entry['revision'])
            p = revision.payload
            if revision.kind != 'RecordRevision' or p['record_id'] != entry['record_id'] or p['project_id'] != snapshot['project_id']:
                raise ValueError('snapshot record binding mismatch')
            if p['record_id'] in records:
                raise ValueError('duplicate logical record')
            doc = self.store.get(p['source_document'])
            if doc.digest not in document_digests:
                raise ValueError('record document missing from closure')
            evidence = self.store.get(doc.payload['evidence'])
            meta, body = _front(self.store.blob(evidence.payload['content_digest']))
            if meta != p['metadata'] or body != p['body']:
                raise ValueError('raw record semantic mismatch')
            records[p['record_id']] = meta
        if list(records) != sorted(records):
            raise ValueError('record manifest is not sorted')
        if lifecycle_errors(records):
            raise ValueError('invalid imported lifecycle graph')
        # Every stored object is immutable and content-addressed; this store contains
        # exactly one imported closure, so no unvalidated orphan payload is hidden.
        for digest, value in self.store.objects.items():
            if KernelObject(value.encoded).digest != digest:
                raise ValueError('object digest mismatch')
            if value.kind == 'EvidenceObject':
                p = value.payload
                raw = self.store.blob(p['content_digest'])
                if len(raw) != p['size'] or 'sha256:' + sha256(raw).hexdigest() != p['content_digest']:
                    raise ValueError('raw evidence integrity mismatch')
        receipt = self.store.get(self.receipt_digest)
        if receipt.kind != 'ImportReceipt' or receipt.payload['snapshot'] != self.snapshot_digest or receipt.payload['source'] != snapshot['source']:
            raise ValueError('import receipt binding mismatch')
        commit_evidence = self.store.get(snapshot['source']['commit_evidence'])
        if commit_evidence.kind != 'EvidenceObject':
            raise ValueError('missing Git commit evidence')
        return True


def import_git_snapshot(root, commit, *, project_id, repository, actor_assertion):
    """No branch aliases, local-root identity or authority inference at this port.

    Produces a fresh quarantine store. Importing one tree does not import Git
    ancestry or establish past record creators. Repository/actor are assertions.
    """
    project = ProjectId(project_id).value
    if not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', commit):
        raise ValueError('import requires a full exact Git commit ID')
    if not isinstance(repository, str) or not repository or not isinstance(actor_assertion, str) or not actor_assertion:
        raise ValueError('repository and import actor assertions are required')
    root = Path(root)
    source = SourceSnapshot.capture(root, ref=commit)
    if source.commit != commit:
        raise ValueError('resolved Git identity differs from request')
    # One immutable source closure is used for both declaration and record checks.
    with source.materialize() as frozen:
        mandatory_paths(frozen)
        declaration = checked_yaml(frozen, 'collaboration/context-inputs.yaml', 'context-inputs.schema.json')
        for view in declaration['views']:
            mandatory_paths(frozen, {'view': view})
    store = MemoryStore()

    def evidence(raw, media_type):
        return store.put(KernelObject.create('EvidenceObject', {
            'media_type': media_type, 'content_digest': store.put_blob(raw), 'size': len(raw)}))

    commit_raw = _git(root, 'cat-file', 'commit', commit)
    git_hash = sha256 if len(commit) == 64 else __import__('hashlib').sha1
    if git_hash(b'commit ' + str(len(commit_raw)).encode() + b'\0' + commit_raw).hexdigest() != commit:
        raise ValueError('Git commit content does not match requested identity')
    source_identity = {'repository': repository, 'commit': commit, 'tree': source.tree,
                       'commit_evidence': evidence(commit_raw, 'application/x-git-commit'),
                       'authentication': 'unknown'}
    validators = {}
    for kind, (_, schema_name, expected) in REGISTRY.items():
        raw = source.files.get(f'schema/{schema_name}.schema.json', b'')
        if sha256(raw).hexdigest() != expected:
            raise ValueError(f'unsupported registered source schema: {kind}')
        validators[kind] = Draft202012Validator(json.loads(raw), format_checker=FormatChecker())
    documents = []
    records = []
    metadata_by_id = {}
    record_paths = {}
    for path, raw in sorted(source.files.items()):
        doc = store.put(KernelObject.create('SourceDocument', {
            'project_id': project, 'path': path, 'evidence': evidence(raw, 'application/octet-stream')}))
        documents.append({'path': path, 'document': doc})
        parent = str(PurePosixPath(path).parent)
        for folder, _, _ in REGISTRY.values():
            if path.startswith(folder + '/') and path.endswith('.md') and parent != folder:
                raise ValueError('unsupported nested canonical record layout')
        kinds = [kind for kind, (folder, _, _) in REGISTRY.items() if parent == folder]
        if not kinds or not path.endswith('.md') or PurePosixPath(path).name == 'README.md':
            continue
        kind = kinds[0]
        metadata, body = _front(raw)
        violations = list(validators[kind].iter_errors(metadata))
        if violations:
            raise ValueError(f'{path}: unsupported record semantics: {violations[0].message}')
        rid = RecordId(metadata['id']).value
        if PurePosixPath(path).stem != rid or rid in metadata_by_id:
            raise ValueError('duplicate or mismatched logical record ID')
        metadata_by_id[rid] = metadata
        record_paths[rid] = (kind, path)
        revision = store.put(KernelObject.create('RecordRevision', {
            'project_id': project, 'record_id': rid, 'record_kind': kind,
            'record_schema': 'sha256:' + REGISTRY[kind][2], 'metadata': metadata, 'body': body,
            'source_document': doc, 'creating_transaction': None, 'predecessor_revision': None,
            'historical_authentication': 'unknown', 'historical_principal': None,
            'historical_authority_decision': None, 'revision_history': 'not-imported'}))
        records.append({'record_id': rid, 'revision': revision})
    for kind, (folder, _, _) in REGISTRY.items():
        index_path = 'memory/index.yaml' if kind == 'memory' else folder + '/index.yaml'
        raw = source.text(index_path)
        if any(isinstance(event, yaml.AliasEvent) for event in yaml.parse(raw)):
            raise ValueError('unsupported index aliases')
        index = yaml.load(raw, Loader=StrictLoader)
        if not isinstance(index, dict) or index.get('schema_version') != 1 or not isinstance(index.get('records'), list):
            raise ValueError('unsupported canonical index')
        seen = set()
        for entry in index['records']:
            if not isinstance(entry, dict) or not isinstance(entry.get('id'), str):
                raise ValueError('invalid index entry')
            rid = entry['id']
            if rid in seen or rid not in record_paths or record_paths[rid][0] != kind:
                raise ValueError('duplicate or unresolved canonical index record')
            seen.add(rid)
            meta = metadata_by_id[rid]
            if (entry.get('file') != PurePosixPath(record_paths[rid][1]).name
                    or entry.get('status') != meta['status'] or entry.get('title') != meta['title']):
                raise ValueError('canonical index differs from record')
        if seen != {rid for rid, (k, _) in record_paths.items() if k == kind}:
            raise ValueError('canonical index omits records')
    errors = lifecycle_errors(metadata_by_id)
    if errors:
        raise ValueError('invalid lifecycle: ' + '; '.join(errors))
    snapshot = store.put(KernelObject.create('ProjectSnapshot', {
        'project_id': project, 'base_snapshot': None, 'history_scope': 'selected-git-tree-only',
        'source': source_identity, 'records': sorted(records, key=lambda r: r['record_id']),
        'documents': documents}))
    receipt = store.put(KernelObject.create('ImportReceipt', {
        'snapshot': snapshot, 'import_actor_assertion': actor_assertion,
        'actor_authentication': 'unknown', 'authorization': 'not_granted',
        'instance_state': 'quarantined', 'source': source_identity,
        'diagnostics': ['Historical authentication, authority and revision ancestry are unknown.',
                        'External source references are preserved assertions; availability is not verified.',
                        'K1 imports the declared source roots, not executable tooling or a full Git backup.']}))
    result = ImportedSnapshot(store, snapshot, receipt)
    result.verify()
    return result
