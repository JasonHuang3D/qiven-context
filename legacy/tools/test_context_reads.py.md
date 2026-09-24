# [SEALED] tools/test_context_reads.py

> Museum piece (ADR-0040/ADR-0041, sealed 2026-09-21). Original
> location: `tools/test_context_reads.py`. Do not execute — this is historical text
> only; the `.md` extension makes accidental execution impossible.

````python
"""K3 adapter equivalence and independent failure-mode checks; no model download."""
import base64
import copy
from dataclasses import replace
import json
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import unittest

from context_compiler import compile_context_pack
from context_evidence import validate_bound_sources
from context_snapshot import SourceSnapshot
from context_kernel import KernelObject, import_git_snapshot
from context_kernel.reads import KernelReadSnapshot, LexicalRanking, ReadValue, encoded
from context_kernel.sqlite_reference import SQLiteReference
from context_kernel.transactions import ContextTransactions
from retrieval_candidate_bundle import build_candidate_bundle
from test_context_transactions import FixtureIdentity, ACTIONS, NOW, STAMP

ROOT = Path(__file__).resolve().parents[1]


class ReadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='context-k3-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.head = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip()
        cls.source = SourceSnapshot.capture(ROOT, ref=cls.head)
        cls.imported = import_git_snapshot(ROOT, cls.head, project_id='qiven-context',
            repository='asserted:k3-fixture', actor_assertion='fixture')
        cls.read = cls.capture(cls.imported.snapshot)
        cls.seed = Path(cls.temp.name) / 'seed.db'
        cls.policy = {'project_id': 'qiven-context', 'authority_scope': 'reference-sandbox',
                      'grants': {'owner': sorted(ACTIONS)}}
        SQLiteReference(cls.seed).bootstrap_quarantine(cls.imported, cls.policy)

    @classmethod
    def capture(cls, snapshot, get=None, blob=None):
        return KernelReadSnapshot.capture(
            get or (lambda key: snapshot if key == snapshot.digest else cls.imported.store.get(key)),
            blob or cls.imported.store.blob, snapshot.digest)

    def setUp(self):
        self.case = tempfile.TemporaryDirectory(dir=self.temp.name)
        self.addCleanup(self.case.cleanup)
        self.path = Path(self.case.name) / 'store.db'
        with sqlite3.connect(self.seed) as source, sqlite3.connect(self.path) as target:
            source.backup(target)
        self.adapter = SQLiteReference(self.path)
        self.kernel = ContextTransactions(self.adapter, FixtureIdentity(), clock=lambda: NOW)

    def view(self, read=None, **kwargs):
        return (read or self.read).resolve_view(now=STAMP, **kwargs)

    def query(self, **kwargs):
        return {'task': 'Review Context', **kwargs}

    def sandbox(self):
        return KernelReadSnapshot.from_sqlite(self.adapter, 'qiven-context')

    def request(self, operations, expected=None, evidence=None, key='read-test'):
        with self.adapter.connect() as db:
            digest = self.adapter.head(db, 'qiven-context')
            base = self.adapter.get(db, digest).payload
        return {'project_id': 'qiven-context', 'transaction_id': key, 'idempotency_key': key,
            'principal': 'owner', 'base_snapshot': digest, 'governance_version': base['governance'],
            'semantic_time': STAMP, 'expected_revisions': expected or {}, 'evidence': evidence or [],
            'depends_on': [], 'operations': operations}

    def test_exact_imported_source_and_old_new_query_corpus(self):
        self.assertEqual(dict(self.read.source.files), dict(self.source.files))
        corpus = json.loads((ROOT/'tests/fixtures/context-kernel/k3-queries.json').read_text())
        for query in corpus:
            for view_id in (None, 'chatgpt-jason'):
                with self.subTest(query=query, view=view_id):
                    view = self.view(view=view_id)
                    q = {**query, 'now': STAMP}
                    if view_id: q['view'] = view_id
                    old = compile_context_pack(q, self.source)
                    new = self.read.compile(query, view).value['context']
                    self.assertEqual(new, old)
                    validate_bound_sources(new)
                    self.assertEqual(new['authorization'], 'not_granted')

    def test_old_new_candidate_equivalence_and_protected_top1(self):
        q = self.query(operation={'action': 'execute', 'target': 'jasonpc', 'channel': 'remote-ai'})
        old = build_candidate_bundle({**q, 'now': STAMP}, LexicalRanking(self.source), root=self.source, max_candidates=1)
        new = self.read.bundle(q, self.view(), max_candidates=1).value
        self.assertEqual(new['context'], old)
        rule = next(r for r in old['constraints']['rules'] if r['id'] == 'jasonpc-remote-mutation-suspension')
        self.assertEqual(rule['effect'], 'prohibit')
        self.assertTrue(rule['sources'])
        self.assertEqual(new['authorization'], 'not_granted')

    def test_explicit_history_missing_id_and_ceiling(self):
        q = self.query(include_ids=['ADR-0001', 'ADR-9999'])
        pack = self.read.bundle(q, self.view(), max_candidates=1).value['context']
        self.assertEqual(pack['candidates'][0]['id'], 'ADR-0001')
        self.assertFalse(pack['candidates'][0]['current_eligible'])
        self.assertEqual(pack['diagnostics'], [{'code': 'unknown-explicit-id', 'id': 'ADR-9999'}])
        with self.assertRaisesRegex(ValueError, 'explicit IDs'):
            self.read.bundle(self.query(include_ids=['ADR-0001', 'ADR-0033']), self.view(), max_candidates=1)

    def test_view_inputs_are_detached_and_do_not_authenticate(self):
        live = {'capabilities': ['read']}
        view = self.view(live_inputs=live, complete_inputs=['capabilities'], input_evidence={'capabilities': 'fixture:observation'})
        live['capabilities'].append('write')
        altered = view.value; altered['authorization'] = 'granted'
        self.assertEqual(view.value['live_inputs']['capabilities'], ['read'])
        result = self.read.compile(self.query(), view)
        self.assertEqual(result.value['authorization'], 'not_granted')
        changed = result.value; changed['context']['authorization'] = 'granted'
        self.assertEqual(result.value['context']['authorization'], 'not_granted')
        with self.assertRaisesRegex(ValueError, 'completeness'):
            self.view(complete_inputs=['capabilities'])

    def test_view_time_and_query_mismatch_fail(self):
        for q in (self.query(view='chatgpt-jason'), self.query(now='2026-09-17T16:00:00Z')):
            with self.assertRaisesRegex(ValueError, 'mismatch'):
                self.read.compile(q, self.view())
        with self.assertRaises(ValueError): self.read.resolve_view(now='2026-09-17T15:00:00')
        with self.assertRaises(ValueError): self.view(view='missing-view')

    def test_repeated_read_bytes_are_identical(self):
        for method in (self.read.compile, self.read.bundle):
            self.assertEqual(method(self.query(), self.view()).encoded, method(self.query(), self.view()).encoded)

    def test_full_envelope_budget_and_protected_failure(self):
        q = self.query(include_ids=['ADR-0033'])
        full = self.read.bundle(q, self.view(), max_candidates=10)
        limited = self.read.bundle({**q, 'max_context_bytes': len(full.encoded)-200}, self.view(), max_candidates=10)
        self.assertLessEqual(len(limited.encoded), len(full.encoded)-200)
        self.assertTrue(limited.value['context']['budget']['omitted'])
        self.assertIn('ADR-0033', [r['id'] for r in limited.value['context']['candidates']])
        validate_bound_sources(limited.value['context'])
        for method in (self.read.compile, self.read.bundle):
            with self.assertRaisesRegex(ValueError, 'budget'):
                method(self.query(max_context_bytes=1), self.view())

    def test_native_revision_rehydrates_new_content_and_keeps_old_snapshot(self):
        old = self.sandbox()
        rid = 'ADR-0033'
        digest = old.provenance.value['revisions'][rid]['revision']
        with self.adapter.connect() as db:
            r = self.adapter.get(db, digest).payload
            base = self.adapter.get(db, old.digest).payload
        meta = r['metadata']; meta['updated_at'] = STAMP
        request = self.request([{'op': 'revise_record', 'record_kind': 'adr', 'metadata': meta,
            'body': r['body'] + '\nK3_NATIVE_SENTINEL\n', 'rationale': 'read fixture'}],
            {rid: digest}, [base['evidence'][0]])
        self.assertEqual(self.kernel.commit_transaction(request, 'owner').status, 'committed')
        new = self.sandbox()
        query = self.query(include_ids=[rid])
        before = old.compile(query, self.view(old)).value
        after = new.compile(query, self.view(new)).value
        self.assertNotIn('K3_NATIVE_SENTINEL', encoded(before).decode())
        self.assertIn('K3_NATIVE_SENTINEL', encoded(after).decode())
        self.assertNotEqual(old.digest, new.digest)
        self.assertEqual(after['binding']['revisions'][rid]['kind'], 'NativeRecordRevision')
        with self.assertRaisesRegex(ValueError, 'view snapshot'):
            new.compile(query, self.view(old))
        again = KernelReadSnapshot.from_sqlite(self.adapter, 'qiven-context', old.digest)
        self.assertEqual(before, again.compile(query, self.view(again)).value)

    def test_sandbox_governance_is_not_imported_github_policy(self):
        read = self.sandbox()
        policy = json.loads(read.source.text('governance/authority.yaml'))
        self.assertEqual(policy['kind'], 'ReferenceGovernance')
        self.assertEqual(policy['policy'], self.policy)
        self.assertNotIn('root_principal', policy)
        self.assertIsNone(read.source.commit)

    def test_missing_active_input_does_not_fall_back_to_import_origin(self):
        with self.adapter.connect() as db:
            base = self.adapter.get(db, self.adapter.head(db, 'qiven-context'))
            p = base.payload
            p['documents'] = [e for e in p['documents'] if e['path'] != 'state/current.md']
            broken = KernelObject.create('SandboxSnapshot', p)
            with self.assertRaises(FileNotFoundError):
                KernelReadSnapshot.capture(lambda key: broken if key == broken.digest else self.adapter.get(db, key),
                                           lambda key: self.adapter.blob(db, key), broken.digest)

    def test_invalid_live_view_update_fails_read(self):
        # K2 verifies references; K3 additionally checks the view selected by the manifest.
        read = self.sandbox()
        with self.adapter.connect() as db:
            base = self.adapter.get(db, read.digest).payload
        path = 'views/environments/jasonpc.yaml'
        doc = next(e['document'] for e in base['documents'] if e['path'] == path)
        # Root view removal tested by projecting a missing referenced profile.
        p = copy.deepcopy(base); p['documents'] = [e for e in p['documents'] if e['document'] != doc]
        obj = KernelObject.create('SandboxSnapshot', p)
        with self.adapter.connect() as db:
            projected = KernelReadSnapshot.capture(lambda key: obj if key == obj.digest else self.adapter.get(db, key),
                lambda key: self.adapter.blob(db, key), obj.digest)
        with self.assertRaises(FileNotFoundError): projected.resolve_view(now=STAMP, view='chatgpt-jason')

    def test_corrupt_object_and_blob_fail(self):
        with self.assertRaisesRegex(ValueError, 'digest/kind'):
            self.capture(self.imported.snapshot, get=lambda _: self.imported.store.get(self.imported.receipt_digest))
        with self.assertRaisesRegex(ValueError, 'evidence integrity'):
            self.capture(self.imported.snapshot, blob=lambda _: b'corrupt')

    def test_wrong_project_and_competing_active_representation_fail(self):
        with self.assertRaises(ValueError):
            KernelReadSnapshot.from_sqlite(self.adapter, 'wrong-project', self.sandbox().digest)
        with self.adapter.connect() as db:
            base = self.adapter.get(db, self.adapter.head(db, 'qiven-context')).payload
            original = self.imported.snapshot.payload
            base['documents'].append(next(d for d in original['documents'] if d['path'] == 'decisions/ADR-0033.md'))
            base['documents'].sort(key=lambda d: d['path'])
            bad = KernelObject.create('SandboxSnapshot', base)
            with self.assertRaisesRegex(ValueError, 'competing active'):
                KernelReadSnapshot.capture(lambda key: bad if key == bad.digest else self.adapter.get(db, key),
                                           lambda key: self.adapter.blob(db, key), bad.digest)

    def replay(self, query=None):
        q = query or self.query()
        config = {'backend': 'fixture-external', 'version': 1, 'model': 'fixed-double'}
        return self.read.capture_ranking(q, self.view(), LexicalRanking(self.read.source), config), config

    def test_captured_ranking_repeatability_and_config_binding(self):
        replay, config = self.replay()
        first = self.read.bundle(self.query(), self.view(), replay=replay, config=config)
        self.assertEqual(first.encoded, self.read.bundle(self.query(), self.view(), replay=replay, config=config).encoded)
        for q, c in ((self.query(task='different'), config), (self.query(), {**config, 'model': 'different'})):
            with self.assertRaisesRegex(ValueError, 'replay binding'):
                self.read.bundle(q, self.view(), replay=replay, config=c)

    def test_index_snapshot_mismatch_and_unavailable_backend_fail(self):
        ranker = LexicalRanking(self.source)
        ranker.snapshot = replace(self.source, id='0'*64)
        with self.assertRaisesRegex(ValueError, 'ranking snapshot'):
            self.read.capture_ranking(self.query(), self.view(), ranker, {'backend': 'fixture', 'version': 1})
        ranker.snapshot = self.source
        def unavailable(_): raise RuntimeError('backend unavailable')
        ranker.rank = unavailable
        with self.assertRaisesRegex(RuntimeError, 'unavailable'):
            self.read.capture_ranking(self.query(), self.view(), ranker, {'backend': 'fixture', 'version': 1})

    def test_replay_rejects_unknown_duplicate_and_nonfinite_hits(self):
        replay, config = self.replay()
        for mutate in (lambda p: p['hits'][0].update(id='ADR-9999'),
                       lambda p: p['hits'][1].update(id=p['hits'][0]['id']),
                       lambda p: p['hits'][0].update(rerank_rank=0)):
            p = replay.value; mutate(p)
            with self.assertRaisesRegex(ValueError, 'replay hit'):
                self.read.bundle(self.query(), self.view(), replay=ReadValue(encoded(p)), config=config)
        p = replay.value; p['hits'][0]['rerank_score'] = float('nan')
        with self.assertRaises(ValueError):
            self.read.bundle(self.query(), self.view(), replay=ReadValue(json.dumps(p).encode()), config=config)

    def test_replay_cannot_omit_explicit_or_inject_index_record_payload(self):
        query = self.query(include_ids=['ADR-0033'])
        replay, config = self.replay(query)
        p = replay.value; p['hits'] = []
        with self.assertRaisesRegex(ValueError, 'omitted explicit'):
            self.read.bundle(query, self.view(), replay=ReadValue(encoded(p)), config=config)
        backend = LexicalRanking(self.source)
        backend.records['ADR-0033'].metadata['title'] = 'INDEX_POISON'
        captured = self.read.capture_ranking(query, self.view(), backend, config)
        output = self.read.bundle(query, self.view(), replay=captured, config=config)
        self.assertNotIn('INDEX_POISON', output.encoded.decode())

    def test_unknown_conditions_remain_unknown_and_terminal_stays_inactive(self):
        output = self.read.compile(self.query(record_mode='history',
            include_ids=['OBL-20260916T125000Z-5A8C31']), self.view()).value['context']
        terminal = [r for r in output['obligations'] if not r['current_eligible']]
        self.assertTrue(terminal)
        for row in terminal:
            self.assertEqual(row['trigger']['result'], 'inactive')
        self.assertEqual(output['authorization'], 'not_granted')


if __name__ == '__main__':
    unittest.main()

````
