# [SEALED] tools/test_context_kernel.py

> Museum piece (ADR-0040/ADR-0041, sealed 2026-09-21). Original
> location: `tools/test_context_kernel.py`. Do not execute — this is historical text
> only; the `.md` extension makes accidental execution impossible.

````python
from __future__ import annotations
import copy
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import yaml

from context_snapshot import SourceSnapshot, SOURCE_ROOTS
from context_kernel import KernelObject, ProjectId, RecordId, import_git_snapshot
from context_kernel.serialization import canonical_bytes, parse_canonical, semantic_digest
from context_kernel.import_git import _front
from lifecycle_graph import lifecycle_errors

ROOT = Path(__file__).resolve().parents[1]


class SerializationTests(unittest.TestCase):
    def test_fixed_golden_vectors(self):
        for vector in json.loads((ROOT/'tests/fixtures/context-kernel/k1-golden.json').read_text()):
            with self.subTest(vector=vector['name']):
                raw = canonical_bytes(vector['value'])
                self.assertEqual(raw.decode(), vector['canonical'])
                self.assertEqual(semantic_digest(raw), vector['digest'])
                self.assertEqual(parse_canonical(raw), vector['value'])

    def test_reject_unsupported_values_and_encodings(self):
        for value in (1.0, float('nan'), 2**53, b'bytes', {1:'key'}, '\ud800'):
            with self.subTest(value=repr(value)), self.assertRaises((ValueError, UnicodeError)):
                canonical_bytes(value)
        for raw in (b'{"x":1,"x":2}', b'{ "x":1}', b'1.0', b'-0', b'NaN', b'"\\u0061"', b'{}\n', b'\xef\xbb\xbf{}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                parse_canonical(raw)
        nested = []
        for _ in range(66): nested = [nested]
        with self.assertRaises(ValueError): canonical_bytes(nested)

    def test_object_domain_version_and_immutability(self):
        p={'media_type':'application/octet-stream','content_digest':'sha256:'+sha256(b'abc').hexdigest(),'size':3}
        value=KernelObject.create('EvidenceObject',p)
        p['size']=0
        changed=value.payload; changed['size']=0
        self.assertEqual(value.payload['size'],3)
        for kind in ('FutureKind','AuthorityDecision'):
            with self.assertRaises(ValueError): KernelObject.create(kind,p)
        v=value.value; v['serialization_version']=2
        with self.assertRaises(ValueError): KernelObject(canonical_bytes(v))
        with self.assertRaises(ValueError): ProjectId('../bad')
        with self.assertRaises(ValueError): RecordId('unregistered:1')

    def test_iterative_lifecycle_long_chain_and_malformed_inputs(self):
        records={str(i):{'status':'superseded' if i else 'accepted',
                         'supersedes':[str(i+1)] if i<2499 else [],
                         'superseded_by':[str(i-1)] if i else []} for i in range(2500)}
        self.assertEqual(lifecycle_errors(records),[])
        records['2499']['supersedes']=['0']
        self.assertTrue(any('cycle' in e for e in lifecycle_errors(records)))
        for bad in ({},[{}],None,False,7):
            self.assertTrue(lifecycle_errors({'x':{'status':'accepted','supersedes':bad}}))


class ImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='context-k1-fixtures-')
        cls.root=Path(cls.temp.name)/'source'; cls.root.mkdir()
        cls.base=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD^{commit}']).decode().strip()
        cls.source=SourceSnapshot.capture(ROOT,ref=cls.base)
        for path,raw in cls.source.files.items():
            p=cls.root/path; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(raw)
        cls.git('init','-q')
        cls.git('add','.')
        cls.head=cls.commit('fixed imported source')
        cls.imported=cls.ingest(cls.head)

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    @classmethod
    def git(cls,*args):
        return subprocess.check_output(['git','-C',str(cls.root),*args],stderr=subprocess.STDOUT).decode().strip()

    @classmethod
    def commit(cls,message):
        cls.git('add','.')
        env=dict(os.environ,GIT_AUTHOR_DATE='2000-01-01T00:00:00Z',GIT_COMMITTER_DATE='2000-01-01T00:00:00Z')
        subprocess.check_output(['git','-C',str(cls.root),'-c','user.name=Context Test Fixture',
                                 '-c','user.email=fixture@example.invalid','commit','-qm',message],env=env)
        return cls.git('rev-parse','HEAD')

    @classmethod
    def ingest(cls,commit,**kwargs):
        return import_git_snapshot(kwargs.pop('root',cls.root),commit,project_id='qiven-context',
                                   repository='asserted:fixture-repository',
                                   actor_assertion=kwargs.pop('actor','jason-brother'),**kwargs)

    def tearDown(self):
        # Only the isolated synthetic fixture is reset; never the user's repository.
        self.git('replace','-l')
        for oid in self.git('replace','-l').splitlines(): self.git('replace','-d',oid)
        self.git('reset','--hard',self.head)
        self.git('clean','-fd')

    def test_raw_round_trip_all_source_bytes(self):
        self.assertEqual(self.imported.raw_sources(),dict(self.source.files))
        self.assertTrue(self.imported.verify())

    def test_records_preserve_all_metadata_and_body(self):
        result=self.imported
        for entry in result.snapshot.payload['records']:
            p=result.store.get(entry['revision']).payload
            doc=result.store.get(p['source_document']).payload
            meta,body=_front(self.source.files[doc['path']])
            self.assertEqual((p['metadata'],p['body']),(meta,body))
            self.assertEqual(p['historical_authentication'],'unknown')
            self.assertIsNone(p['historical_principal'])
            self.assertIsNone(p['creating_transaction'])
            self.assertIsNone(p['predecessor_revision'])
            self.assertEqual(p['revision_history'],'not-imported')

    def test_object_round_trip_and_acyclic_digest_dependencies(self):
        result=self.imported
        levels={'EvidenceObject':0,'SourceDocument':1,'RecordRevision':2,'ProjectSnapshot':3,'ImportReceipt':4}
        edges={'EvidenceObject':[], 'SourceDocument':['evidence'],
               'RecordRevision':['source_document'], 'ProjectSnapshot':[], 'ImportReceipt':['snapshot']}
        for digest, value in result.store.objects.items():
            self.assertEqual(KernelObject(value.encoded).digest,digest)
            self.assertNotIn(digest,value.encoded.decode())
            p=value.payload
            refs=[p[k] for k in edges[value.kind]]
            if value.kind=='ProjectSnapshot':
                refs += [e['document'] for e in p['documents']]
                refs += [e['revision'] for e in p['records']]
            if value.kind in ('ProjectSnapshot','ImportReceipt'):
                refs.append(p['source']['commit_evidence'])
            for ref in refs:
                self.assertLess(levels[result.store.get(ref).kind],levels[value.kind])

    def test_receipt_never_authenticates_caller_or_promotes_authority(self):
        r=self.imported.store.get(self.imported.receipt_digest).payload
        self.assertEqual(r['actor_authentication'],'unknown')
        self.assertEqual(r['authorization'],'not_granted')
        self.assertEqual(r['instance_state'],'quarantined')
        self.assertEqual(self.imported.snapshot.payload['history_scope'],'selected-git-tree-only')
        self.assertFalse(hasattr(self.imported.store,'head'))

    def test_repeat_import_and_actor_independence(self):
        other=self.ingest(self.head,actor='different caller')
        self.assertEqual(other.snapshot_digest,self.imported.snapshot_digest)
        self.assertNotEqual(other.receipt_digest,self.imported.receipt_digest)

    def test_clone_location_does_not_change_identity(self):
        clone=Path(self.temp.name)/'relocated'
        subprocess.check_output(['git','clone','-q',str(self.root),str(clone)],stderr=subprocess.STDOUT)
        self.assertEqual(self.ingest(self.head,root=clone).snapshot_digest,self.imported.snapshot_digest)

    def test_dirty_working_tree_does_not_change_explicit_import(self):
        (self.root/'MEMORY-CONSTITUTION.md').write_text('changed but uncommitted')
        self.assertEqual(self.ingest(self.head).snapshot_digest,self.imported.snapshot_digest)
        with self.assertRaises(ValueError): SourceSnapshot.capture(self.root)
        with self.assertRaises(ValueError): self.ingest('HEAD')

    def test_export_attributes_do_not_drop_or_transform_raw_source(self):
        raw=b'\x00raw\xff\r\n$Format:%H$\n'
        (self.root/'evidence/audits/raw.bin').write_bytes(raw)
        (self.root/'.gitattributes').write_text('evidence/audits/raw.bin export-ignore\nMEMORY-CONSTITUTION.md export-subst\n')
        p=self.root/'MEMORY-CONSTITUTION.md'; p.write_bytes(p.read_bytes()+b'\n$Format:%H$\n')
        commit=self.commit('export attributes')
        result=self.ingest(commit)
        self.assertEqual(result.raw_sources()['evidence/audits/raw.bin'],raw)
        self.assertTrue(result.raw_sources()['MEMORY-CONSTITUTION.md'].endswith(b'$Format:%H$\n'))

    def test_git_replace_refs_cannot_change_exact_import(self):
        (self.root/'MEMORY-CONSTITUTION.md').write_text('replacement tree')
        replacement=self.commit('replacement')
        self.git('replace',self.head,replacement)
        self.assertEqual(self.ingest(self.head).snapshot_digest,self.imported.snapshot_digest)

    def test_missing_mandatory_source_fails(self):
        (self.root/'MEMORY-CONSTITUTION.md').unlink()
        with self.assertRaises((ValueError,FileNotFoundError)): self.ingest(self.commit('missing source'))

    def test_unsupported_schema_fails_without_using_supplied_definition(self):
        p=self.root/'schema/adr.schema.json'; p.write_text('{}')
        with self.assertRaisesRegex(ValueError,'unsupported registered'): self.ingest(self.commit('bad schema'))

    def test_unknown_record_status_fails(self):
        p=self.root/'decisions/ADR-0033.md'; p.write_text(p.read_text().replace('status: accepted','status: mystery',1))
        with self.assertRaisesRegex(ValueError,'unsupported record semantics'): self.ingest(self.commit('bad status'))

    def test_duplicate_metadata_cannot_be_silently_overwritten(self):
        p=self.root/'decisions/ADR-0033.md'; p.write_text(p.read_text().replace('status: accepted','status: rejected\nstatus: accepted',1))
        with self.assertRaisesRegex(ValueError,'duplicate'): self.ingest(self.commit('duplicate metadata'))

    def test_index_disagreement_is_not_silently_imported(self):
        p=self.root/'decisions/index.yaml'
        data=yaml.safe_load(p.read_text()); data['records'].pop()
        p.write_text(yaml.safe_dump(data))
        with self.assertRaisesRegex(ValueError,'index omits'): self.ingest(self.commit('missing index record'))

    def test_nonreciprocal_lifecycle_fails(self):
        p=self.root/'decisions/ADR-0033.md'; p.write_text(p.read_text().replace('supersedes: []','supersedes: [ADR-0003]',1))
        with self.assertRaisesRegex(ValueError,'invalid lifecycle'): self.ingest(self.commit('bad graph'))

    def test_symlink_in_source_closure_fails(self):
        os.symlink('outside',self.root/'evidence/link')
        with self.assertRaisesRegex(ValueError,'unsupported snapshot source mode'): self.ingest(self.commit('symlink'))

    def test_blob_corruption_is_detected(self):
        result=copy.deepcopy(self.imported)
        evidence=next(o for o in result.store.objects.values() if o.kind=='EvidenceObject')
        result.store._blobs[evidence.payload['content_digest']]=b'corrupt'
        with self.assertRaises(ValueError): result.verify()

    def test_exact_candidate_git_snapshot_import(self):
        result=self.ingest(self.base,root=ROOT)
        self.assertEqual(result.raw_sources(),dict(self.source.files))
        self.assertEqual(result.snapshot.payload['source']['commit'],self.base)


if __name__=='__main__': unittest.main(verbosity=2)

````
