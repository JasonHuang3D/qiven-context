# [SEALED] tools/test_context_archive.py

> Museum piece (ADR-0040/ADR-0041, sealed 2026-09-21). Original
> location: `tools/test_context_archive.py`. Do not execute — this is historical text
> only; the `.md` extension makes accidental execution impossible.

````python
"""K4 engineering proof. Fresh-process replay is NOT a fresh-LLM blind trial."""
import base64
import copy
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from context_kernel import KernelObject, import_git_snapshot
from context_kernel.archive import (export_snapshot, export_sqlite, restore_export,
    encode, digest, PROFILE)
from context_kernel.reads import KernelReadSnapshot
from context_kernel.sqlite_reference import SQLiteReference
from context_kernel.transactions import ContextTransactions
from test_context_transactions import FixtureIdentity, ACTIONS, NOW, STAMP

ROOT=Path(__file__).resolve().parents[1]


def sign(package):
    package['package_digest']=digest('package',{k:v for k,v in package.items() if k!='package_digest'})
    return encode(package)


def output_fingerprint(restored,queries):
    read=KernelReadSnapshot.capture(restored.store.get,restored.store.blob,restored.snapshot)
    output=[]
    for query in queries:
        for view in (None,'chatgpt-jason'):
            resolved=read.resolve_view(now=STAMP,view=view)
            output.append(sha256(read.compile(query,resolved).encoded).hexdigest())
            output.append(sha256(read.bundle(query,resolved,max_candidates=5).encoded).hexdigest())
    return output


class ArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='context-k4-')
        cls.addClassCleanup(cls.temp.cleanup)
        head=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD']).decode().strip()
        cls.imported=import_git_snapshot(ROOT,head,project_id='qiven-context',repository='asserted:k4-fixture',actor_assertion='fixture')
        cls.export=export_snapshot(cls.imported.store.get,cls.imported.store.blob,cls.imported.snapshot_digest,
                                   access_policy='fixture:canonical-continuity',observed_at=STAMP)
        cls.seed=Path(cls.temp.name)/'seed.db'
        SQLiteReference(cls.seed).bootstrap_quarantine(cls.imported,{'project_id':'qiven-context',
            'authority_scope':'reference-sandbox','grants':{'owner':sorted(ACTIONS)}})

    def setUp(self):
        self.case=tempfile.TemporaryDirectory(dir=self.temp.name);self.addCleanup(self.case.cleanup)
        self.path=Path(self.case.name)/'source.db'
        with sqlite3.connect(self.seed) as source,sqlite3.connect(self.path) as target:source.backup(target)
        self.adapter=SQLiteReference(self.path)
        self.kernel=ContextTransactions(self.adapter,FixtureIdentity(),clock=lambda:NOW)

    def export_db(self,**kw):
        return export_sqlite(self.adapter,'qiven-context',access_policy='fixture:canonical-continuity',observed_at=STAMP,**kw)

    def request(self,key,ops=None):
        with self.adapter.connect() as db:
            head=self.adapter.head(db,'qiven-context');base=self.adapter.get(db,head).payload
        document=next(d['document'] for d in base['documents'] if d['path']=='state/current.md')
        return {'project_id':'qiven-context','transaction_id':'k4-'+key,'idempotency_key':key,'principal':'owner',
                'base_snapshot':head,'governance_version':base['governance'],'semantic_time':STAMP,
                'expected_revisions':{},'evidence':[],'depends_on':[],
                'operations':ops or [{'op':'put_document','path':'state/current.md','expected_document':document,
                    'content_base64':base64.b64encode(('# '+key+'\n').encode()).decode(),'rationale':'K4 fixture'}]}

    def test_exact_round_trip_and_deterministic_manifest(self):
        restored=restore_export(self.export.encoded)
        self.assertTrue(restored.report['complete'])
        read=KernelReadSnapshot.capture(restored.store.get,restored.store.blob,restored.snapshot)
        self.assertEqual(dict(read.source.files),self.imported.raw_sources())
        again=export_snapshot(restored.store.get,restored.store.blob,restored.snapshot,
                              access_policy='fixture:canonical-continuity',observed_at=STAMP)
        self.assertEqual(again.encoded,self.export.encoded)
        self.assertEqual(restored.report['authorization'],'not_granted')
        self.assertFalse(restored.report['writes_enabled'])

    def test_availability_and_observation_change_package_not_semantic_manifest(self):
        key=self.export.value['manifest']['blobs'][0]['digest']
        partial=export_snapshot(self.imported.store.get,self.imported.store.blob,self.imported.snapshot_digest,
            access_policy='fixture:restricted',observed_at='2026-09-17T16:00:00Z',omit={key:'policy omission'})
        self.assertEqual(partial.value['manifest_digest'],self.export.value['manifest_digest'])
        self.assertNotEqual(partial.value['package_digest'],self.export.value['package_digest'])
        restored=restore_export(partial.encoded)
        self.assertFalse(restored.report['complete'])
        self.assertEqual(restored.report['missing_evidence'][key],'policy omission')
        target=SQLiteReference(Path(self.case.name)/'partial.db')
        with self.assertRaisesRegex(ValueError,'partial'):restored.to_sqlite(target)
        with target.connect() as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM projects').fetchone()[0],0)

    def test_unavailable_raw_evidence_is_explicit(self):
        key=self.export.value['manifest']['blobs'][0]['digest']
        def unavailable(k):
            if k==key:raise KeyError(k)
            return self.imported.store.blob(k)
        result=export_snapshot(self.imported.store.get,unavailable,self.imported.snapshot_digest,
                              access_policy='fixture',observed_at=STAMP)
        self.assertFalse(restore_export(result.encoded).report['complete'])
        self.assertEqual(result.value['manifest_digest'],self.export.value['manifest_digest'])

    def test_outer_tamper_and_semantic_tamper_are_independent(self):
        p=self.export.value;p['delivery']['observed_at']='2026-09-17T16:00:00Z'
        with self.assertRaisesRegex(ValueError,'package digest'):restore_export(encode(p))
        p=self.export.value;p['manifest']['snapshot']='sha256:'+'0'*64
        with self.assertRaisesRegex(ValueError,'semantic manifest'):restore_export(sign(p))

    def test_missing_required_object_cannot_be_redacted(self):
        p=self.export.value;key=p['manifest']['snapshot'];del p['objects'][key]
        with self.assertRaisesRegex(ValueError,'missing canonical'):restore_export(sign(p))

    def test_modified_object_with_rehashed_package_still_fails(self):
        p=self.export.value;key=p['manifest']['snapshot']
        value=json.loads(base64.b64decode(p['objects'][key]));value['payload']['project_id']='wrong'
        p['objects'][key]=base64.b64encode(encode(value)).decode()
        with self.assertRaisesRegex(ValueError,'object digest'):restore_export(sign(p))

    def test_missing_or_corrupt_raw_bytes_do_not_pass_full_recovery(self):
        p=self.export.value;key=next(iter(p['blobs']));del p['blobs'][key]
        with self.assertRaises(ValueError):restore_export(sign(p))
        p=self.export.value;p['blobs'][key]=base64.b64encode(b'corrupt').decode()
        with self.assertRaisesRegex(ValueError,'raw evidence'):restore_export(sign(p))

    def test_unknown_format_profile_and_duplicate_json_keys_fail(self):
        p=self.export.value;p['delivery']['profile']='unknown'
        with self.assertRaisesRegex(ValueError,'profile'):restore_export(sign(p))
        p=self.export.value;p['manifest']['version']=True;p['manifest_digest']=digest('manifest',p['manifest'])
        with self.assertRaises(ValueError):restore_export(sign(p))
        with self.assertRaisesRegex(ValueError,'duplicate'):restore_export(b'{"a":1,"a":2}')

    def test_extra_objects_and_fake_transaction_maps_fail(self):
        p=self.export.value
        value=KernelObject.create('ExternalEvidenceReference',{'reference':'fixture:orphan','media_type':'text/plain',
                   'expected_content_digest':None,'availability':'unverified'})
        p['objects'][value.digest]=base64.b64encode(value.encoded).decode()
        with self.assertRaisesRegex(ValueError,'closure'):restore_export(sign(p))
        p=self.export.value;p['manifest']['transactions']=[{'transaction_id':'fake','receipt':'sha256:'+'0'*64}]
        p['manifest_digest']=digest('manifest',p['manifest'])
        with self.assertRaisesRegex(ValueError,'closure'):restore_export(sign(p))

    def test_native_history_receipts_and_idempotency_survive_restore(self):
        a=self.request('a');first=self.kernel.commit_transaction(a,'owner')
        b=self.request('b');second=self.kernel.commit_transaction(b,'owner')
        self.assertEqual((first.status,second.status),('committed','committed'))
        restored=restore_export(self.export_db().encoded)
        self.assertTrue(restored.report['complete']);self.assertEqual(len(restored.transactions),2)
        target=SQLiteReference(Path(self.case.name)/'restored.db');restored.to_sqlite(target)
        read=KernelReadSnapshot.from_sqlite(target,'qiven-context')
        self.assertEqual(read.digest,second.successor)
        engine=ContextTransactions(target,FixtureIdentity(),clock=lambda:NOW)
        self.assertEqual(engine.commit_transaction(a,'owner'),first)
        self.assertEqual(engine.get_transaction_result('qiven-context','b','owner'),second)
        new=self.request('new')
        self.assertEqual(engine.commit_transaction(new,'owner').code,'restored_read_only')
        with target.connect() as db:self.assertEqual(target.head(db,'qiven-context'),second.successor)
        replay=export_sqlite(target,'qiven-context',access_policy='fixture:canonical-continuity',observed_at=STAMP)
        self.assertEqual(replay.value['manifest_digest'],self.export_db().value['manifest_digest'])

    def test_nonempty_adapter_is_unchanged_on_restore_rejection(self):
        before=KernelReadSnapshot.from_sqlite(self.adapter,'qiven-context').digest
        with self.assertRaisesRegex(ValueError,'empty'):restore_export(self.export.encoded).to_sqlite(self.adapter)
        self.assertEqual(KernelReadSnapshot.from_sqlite(self.adapter,'qiven-context').digest,before)

    def test_missing_native_receipt_prevents_export(self):
        p=self.request('receipt');self.assertEqual(self.kernel.commit_transaction(p,'owner').status,'committed')
        with self.adapter.connect() as db:
            head=self.adapter.head(db,'qiven-context')
            with self.assertRaisesRegex(ValueError,'receipt'):
                export_snapshot(lambda key:self.adapter.get(db,key),lambda key:self.adapter.blob(db,key),head,
                                access_policy='fixture',observed_at=STAMP)

    def test_unknown_external_evidence_blocks_full_recovery(self):
        p=self.request('external',[{'op':'add_external_evidence','reference':'fixture:external','media_type':'text/plain',
                                   'expected_content_digest':None}])
        self.assertEqual(self.kernel.commit_transaction(p,'owner').status,'committed')
        restored=restore_export(self.export_db().encoded)
        self.assertFalse(restored.report['complete'])
        self.assertTrue(restored.report['unverifiable_external_references'])

    def test_known_external_missing_then_available_preserves_manifest(self):
        raw=b'external fixture';key='sha256:'+sha256(raw).hexdigest()
        p=self.request('external-known',[{'op':'add_external_evidence','reference':'fixture:external','media_type':'text/plain',
                                        'expected_content_digest':key}])
        self.assertEqual(self.kernel.commit_transaction(p,'owner').status,'committed')
        missing=self.export_db()
        self.assertFalse(restore_export(missing.encoded).report['complete'])
        with self.adapter.connect() as db:self.adapter.put_blob(db,key,raw)
        available=self.export_db()
        self.assertEqual(missing.value['manifest_digest'],available.value['manifest_digest'])
        self.assertTrue(restore_export(available.encoded).report['complete'])

    def test_known_secret_content_requires_remediation(self):
        raw=b'-----BEGIN PRIVATE KEY-----\nfixture-only-not-a-real-key\n'
        p=self.request('secret',[{'op':'add_evidence','media_type':'text/plain','content_base64':base64.b64encode(raw).decode()}])
        self.assertEqual(self.kernel.commit_transaction(p,'owner').status,'committed')
        with self.assertRaisesRegex(ValueError,'secret-bearing'):self.export_db()

    def test_corrupt_source_blob_is_not_treated_as_missing(self):
        with self.assertRaisesRegex(ValueError,'integrity'):
            export_snapshot(self.imported.store.get,lambda _:b'corrupt',self.imported.snapshot_digest,
                            access_policy='fixture',observed_at=STAMP)

    def test_archive_cli_materializes_reviewable_read_only_sources(self):
        package=Path(self.case.name)/'cli-package.json';database=Path(self.case.name)/'cli.db'
        sources=Path(self.case.name)/'sources'
        head=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD']).decode().strip()
        export=subprocess.run([sys.executable,str(ROOT/'tools/context_archive.py'),'export-git',
            '--root',str(ROOT),'--commit',head,'--repository','asserted:cli-fixture','--output',str(package)],
            capture_output=True,timeout=60)
        self.assertEqual(export.returncode,0,export.stderr.decode())
        restore=subprocess.run([sys.executable,str(ROOT/'tools/context_archive.py'),'restore',
            '--input',str(package),'--database',str(database),'--sources',str(sources)],capture_output=True,timeout=60)
        self.assertEqual(restore.returncode,0,restore.stderr.decode())
        self.assertTrue(json.loads(restore.stdout)['complete'])
        self.assertEqual((sources/'MEMORY-CONSTITUTION.md').read_bytes(),self.imported.raw_sources()['MEMORY-CONSTITUTION.md'])
        with SQLiteReference(database).connect() as db:
            self.assertEqual(db.execute('SELECT reason FROM write_blocks').fetchone()[0],'restored_read_only')

    def test_fresh_process_read_reconstruction_without_git_or_original_store(self):
        package=Path(self.case.name)/'backup.json';package.write_bytes(self.export.encoded)
        queries=json.loads((ROOT/'tests/fixtures/context-kernel/k3-queries.json').read_text())
        query_file=Path(self.case.name)/'queries.json';query_file.write_text(json.dumps(queries))
        expected=output_fingerprint(restore_export(self.export.encoded),queries)
        process=subprocess.run([sys.executable,__file__,'--restore-only',str(package),str(query_file)],
                                capture_output=True,timeout=90,cwd=self.case.name)
        self.assertEqual(process.returncode,0,process.stderr.decode())
        self.assertEqual(json.loads(process.stdout),expected)
        self.assertEqual(len(expected),28)


if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--restore-only':
        # Child has no importer/store instance and Git invocation is explicitly unavailable.
        import context_snapshot
        def forbidden(*args,**kwargs):raise AssertionError('Git must not participate in recovery')
        context_snapshot._git=forbidden
        restored=restore_export(Path(sys.argv[2]).read_bytes())
        print(json.dumps(output_fingerprint(restored,json.loads(Path(sys.argv[3]).read_text()))))
    else:unittest.main(verbosity=2)

````
