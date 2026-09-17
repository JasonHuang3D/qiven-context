"""K3 immutable read projection and delivery. No head mutation or authority grant."""
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
from pathlib import Path
from types import MappingProxyType, SimpleNamespace

from context_compiler import (CATEGORY_LAYOUT, _record_relevance, compile_context_pack,
                              load_canonical_store, prepare_query)
from context_inputs import mandatory_paths
from context_evidence import attach_sources, validate_bound_sources
from context_snapshot import (SourceSnapshot, MAX_FILE_BYTES, MAX_SOURCE_BYTES,
                              canonical_json, digest_files, safe_path)
from lifecycle_graph import lifecycle_errors
from record_lifecycle import record_is_eligible
from retrieval_candidate_bundle import build_candidate_bundle
from .model import KernelObject
from .registry import REGISTRY
from .serialization import canonical_bytes
from .source_formats import _front
from .transactions import utc


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'),
                      allow_nan=False).encode('utf-8')


def fingerprint(value):
    return 'sha256:' + sha256(encoded(value)).hexdigest()


@dataclass(frozen=True)
class ReadValue:
    """Detached JSON value; callers cannot mutate nested canonical delivery state."""
    encoded: bytes

    @property
    def value(self):
        return json.loads(self.encoded)

    @property
    def digest(self):
        return fingerprint(self.value)


@dataclass(frozen=True)
class KernelReadSnapshot:
    digest: str
    source: SourceSnapshot
    provenance: ReadValue

    @classmethod
    def capture(cls, get_object, get_blob, digest):
        def get(key, kinds):
            obj = KernelObject(get_object(key).encoded)
            if obj.digest != key or obj.kind not in kinds:
                raise ValueError('read object digest/kind mismatch')
            return obj

        snapshot = get(digest, ('ProjectSnapshot', 'SandboxSnapshot'))
        p = snapshot.payload
        project = p['project_id']

        def document(key, path):
            doc = get(key, ('SourceDocument',)).payload
            if doc['project_id'] != project or doc['path'] != safe_path(path):
                raise ValueError('read document binding mismatch')
            ev = get(doc['evidence'], ('EvidenceObject',)).payload
            raw = get_blob(ev['content_digest'])
            if (type(raw) is not bytes or len(raw) != ev['size']
                    or 'sha256:' + sha256(raw).hexdigest() != ev['content_digest']):
                raise ValueError('read evidence integrity mismatch')
            return raw

        files = {d['path']: document(d['document'], d['path']) for d in p['documents']}
        revisions, metadata, paths = {}, {}, set()
        indices = {kind: [] for kind in REGISTRY}
        for entry in p['records']:
            rev = get(entry['revision'], ('RecordRevision', 'NativeRecordRevision'))
            r = rev.payload
            rid = entry['record_id']
            if r['record_id'] != rid or r['project_id'] != project:
                raise ValueError('read record binding mismatch')
            path = REGISTRY[r['record_kind']][0] + '/' + rid + '.md'
            if snapshot.kind == 'SandboxSnapshot' and path in files:
                raise ValueError('competing active record representation')
            if rev.kind == 'RecordRevision':
                raw = document(r['source_document'], path)
                meta, body = _front(raw)
                if meta != r['metadata'] or body != r['body']:
                    raise ValueError('read record/raw mismatch')
            else:
                raw = b'---\n' + canonical_bytes(r['metadata']) + b'\n---\n' + r['body'].encode('utf-8')
            if snapshot.kind == 'ProjectSnapshot' and files.get(path) != raw:
                raise ValueError('imported record missing from active documents')
            files[path] = raw
            paths.add(path)
            metadata[rid] = r['metadata']
            revisions[rid] = {'revision': rev.digest, 'kind': rev.kind,
                              'provenance': {k: v for k, v in r.items()
                                             if k not in ('metadata', 'body')}}
            indices[r['record_kind']].append({'id': rid, 'file': rid + '.md',
                'title': r['metadata']['title'], 'status': r['metadata']['status']})
        if lifecycle_errors(metadata):
            raise ValueError('read lifecycle corruption')
        for path in files:
            for folder, _, _ in REGISTRY.values():
                if path.startswith(folder + '/') and path.endswith('.md') and path.rsplit('/', 1)[-1] != 'README.md' and path not in paths:
                    raise ValueError('unmanifested canonical record')
        if snapshot.kind == 'SandboxSnapshot':
            for kind, entries in indices.items():
                index = 'memory/index.yaml' if kind == 'memory' else REGISTRY[kind][0] + '/index.yaml'
                if index in files:
                    raise ValueError('competing active index')
                files[index] = canonical_bytes({'schema_version': 1, 'records': entries})
            if 'governance/authority.yaml' in files:
                raise ValueError('competing active governance')
            policy = get(p['governance'], ('ReferenceGovernance',))
            if policy.payload['project_id'] != project:
                raise ValueError('read governance project mismatch')
            files['governance/authority.yaml'] = canonical_bytes({
                'kind': 'ReferenceGovernance', 'instance_state': 'quarantined',
                'policy_digest': policy.digest, 'policy': policy.payload,
                'authorization': 'not_granted'})
        if any(len(raw) > MAX_FILE_BYTES for raw in files.values()) or sum(map(len, files.values())) > MAX_SOURCE_BYTES:
            raise ValueError('read projection exceeds source limits')
        hashes = digest_files(files)
        schema_root = Path(__file__).resolve().parents[2] / 'schema'
        for name in ('context-query', 'context-pack', 'context-inputs', 'context-constraints'):
            if files.get('schema/' + name + '.schema.json') != (schema_root / (name + '.schema.json')).read_bytes():
                raise ValueError('unsupported read schema version')
        imported = snapshot.kind == 'ProjectSnapshot'
        source = SourceSnapshot('kernel:' + digest, 'git-commit' if imported else 'quiescent-directory',
            p['source']['commit'] if imported else None, p['source']['tree'] if imported else None,
            MappingProxyType(files), MappingProxyType(hashes), sha256(canonical_json(hashes)).hexdigest())
        with source.materialize() as root:
            mandatory_paths(root)
            loaded = load_canonical_store(root)
            actual = {r.id: r.metadata for rows in loaded.values() for r in rows}
            if actual != metadata:
                raise ValueError('read projection/index mismatch')
        return cls(digest, source, ReadValue(encoded({'project_id': project,
            'kernel_snapshot': digest, 'instance_state': 'quarantined',
            'projection_version': 1, 'revisions': revisions})))

    @classmethod
    def from_sqlite(cls, adapter, project, digest=None):
        with adapter.connect() as db:
            adapter.begin_read(db)
            selected = digest or adapter.head(db, project)
            result = cls.capture(lambda key: adapter.get(db, key),
                                 lambda key: adapter.blob(db, key), selected)
            if result.provenance.value['project_id'] != project:
                raise ValueError('read project mismatch')
            return result

    def resolve_view(self, *, now, view=None, live_inputs=None, complete_inputs=(), input_evidence=None):
        utc(now)
        live = {} if live_inputs is None else live_inputs
        evidence = {} if input_evidence is None else input_evidence
        if not isinstance(live, dict) or not isinstance(evidence, dict):
            raise ValueError('view inputs must be mappings')
        complete = list(complete_inputs)
        if any(not isinstance(k, str) or not k or not isinstance(evidence.get(k), str)
               or not evidence[k].strip() for k in complete) or len(set(complete)) != len(complete):
            raise ValueError('view completeness requires distinct named sets and evidence')
        with self.source.materialize() as root:
            paths = mandatory_paths(root, {'view': view} if view is not None else {})
        return ReadValue(canonical_bytes({'kind': 'ResolvedContextView', 'version': 1,
            'kernel_snapshot': self.digest, 'projection_id': self.source.id, 'view': view,
            'now': now, 'live_inputs': live, 'complete_inputs': complete,
            'input_evidence': evidence, 'mandatory_paths': list(paths),
            'authorization': 'not_granted'}))

    def _query(self, query, view):
        v = view.value
        if v.get('kind') != 'ResolvedContextView' or v['kernel_snapshot'] != self.digest or v['projection_id'] != self.source.id:
            raise ValueError('view snapshot mismatch')
        expected = self.resolve_view(now=v['now'], view=v['view'], live_inputs=v['live_inputs'],
            complete_inputs=v['complete_inputs'], input_evidence=v['input_evidence'])
        if expected.encoded != view.encoded:
            raise ValueError('resolved view binding mismatch')
        q = dict(query)
        for key in ('view', 'now'):
            if key in q and q[key] != v[key]:
                raise ValueError('query/view input mismatch')
            if v[key] is not None:
                q[key] = v[key]
        return prepare_query(q, self.source)

    def compile(self, query, view):
        q = self._query(query, view)
        unbounded = {k: v for k, v in q.items() if k != 'max_context_bytes'}
        pack = compile_context_pack(unbounded, self.source)
        return self._deliver(pack, q, view, {'backend': 'r1-deterministic', 'version': 1})

    def capture_ranking(self, query, view, retriever, config):
        q = self._query(query, view)
        if not isinstance(config, dict) or not isinstance(config.get('backend'), str) or not config['backend'] or config.get('version') != 1:
            raise ValueError('ranking requires versioned backend/config identity')
        canonical_bytes(config)
        if getattr(retriever, 'snapshot', None) is None or retriever.snapshot.manifest() != self.source.manifest():
            raise ValueError('ranking snapshot mismatch')
        hits = [asdict(hit) for hit in retriever.rank(q)]
        replay = ReadValue(encoded({'kind': 'RankingReplay', 'version': 1,
            'kernel_snapshot': self.digest, 'projection_id': self.source.id,
            'query': q, 'config': config, 'hits': hits}))
        self._replayer(q, replay, config)
        return replay

    def _records(self):
        with self.source.materialize() as root:
            return {r.id: r for rows in load_canonical_store(root).values() for r in rows}

    def _replayer(self, query, replay, config):
        p = replay.value
        if (p.get('kind') != 'RankingReplay' or p.get('version') != 1 or p['kernel_snapshot'] != self.digest
                or p['projection_id'] != self.source.id or p['query'] != query or p['config'] != config):
            raise ValueError('ranking replay binding mismatch')
        records = self._records()
        seen = set()
        from rerank_retriever import RerankHit
        hits = []
        for position, row in enumerate(p['hits'], 1):
            hit = RerankHit(**row)
            if (hit.id not in records or hit.id in seen or type(hit.rerank_rank) is not int or hit.rerank_rank != position
                    or type(hit.rerank_score) not in (int, float) or not math.isfinite(hit.rerank_score)
                    or type(hit.explicit) is not bool or hit.explicit != (hit.id in query['include_ids'])
                    or type(hit.graph_candidate) is not bool):
                raise ValueError('invalid ranking replay hit')
            for rank in (hit.hybrid_rank, hit.deterministic_rank, hit.semantic_rank):
                if rank is not None and (type(rank) is not int or rank < 1):
                    raise ValueError('invalid ranking metadata')
            seen.add(hit.id)
            hits.append(hit)
        if not set(query['include_ids']).intersection(records) <= seen:
            raise ValueError('ranking omitted explicit IDs')
        return SimpleNamespace(snapshot=self.source, records=records, rank=lambda _: hits)

    def bundle(self, query, view, *, max_candidates=3, replay=None, config=None):
        q = self._query(query, view)
        if type(max_candidates) is not int or max_candidates < 1:
            raise ValueError('invalid candidate ceiling')
        if replay is None:
            if config is not None:
                raise ValueError('custom ranking requires a captured replay')
            config = {'backend': 'kernel-lexical', 'version': 1}
            replay = self.capture_ranking(q, view, LexicalRanking(self.source), config)
        elif config is None:
            raise ValueError('replay requires expected config')
        active = self._replayer(q, replay, config)
        unbounded = {k: v for k, v in q.items() if k != 'max_context_bytes'}
        pack = build_candidate_bundle(unbounded, active, root=self.source, max_candidates=max_candidates)
        return self._deliver(pack, q, view, {'config': config, 'replay_digest': replay.digest})

    def _deliver(self, pack, query, view, retrieval):
        pack['query'] = query
        budget = query.get('max_context_bytes')
        pack['budget'] = {'limit_bytes': budget, 'omitted': []}
        output = {'kind': 'ContextBundle', 'version': 1, 'authorization': 'not_granted',
                  'binding': self.provenance.value, 'view': view.value,
                  'retrieval': retrieval, 'context': pack}
        explicit = set(query['include_ids'])
        optional = [(section, row) for section in ('projects', 'decisions', 'memory', 'obligations', 'candidates')
                    for row in pack.get(section, []) if row.get('id') not in explicit]
        attach_sources(pack, self.source)
        while budget is not None and len(encoded(output)) > budget and optional:
            section, row = optional.pop()
            pack[section].remove(row)
            pack['budget']['omitted'].append(row.get('id', row['path']))
            attach_sources(pack, self.source)
        if budget is not None and len(encoded(output)) > budget:
            raise ValueError('Context byte budget cannot contain protected kernel envelope')
        validate_bound_sources(pack)
        return ReadValue(encoded(output))


class LexicalRanking:
    """Versioned deterministic reference backend, not replacement model tuning."""
    def __init__(self, snapshot):
        self.snapshot = snapshot
        with snapshot.materialize() as root:
            self.records = {r.id: r for rows in load_canonical_store(root).values() for r in rows}

    def rank(self, query):
        from rerank_retriever import RerankHit
        prepared = prepare_query(query, self.snapshot)
        rows = [(r.id, _record_relevance(r, prepared)[0]) for r in self.records.values()
                if record_is_eligible(r, prepared)]
        rows.sort(key=lambda row: (-row[1], row[0]))
        return [RerankHit(rid, score, i, i, i, None, False, rid in prepared['include_ids'])
                for i, (rid, score) in enumerate(rows, 1)]
