"""K4 handoff engineering proof; fresh-LLM acceptance remains separate."""
import base64
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from context_inputs import mandatory_paths
from context_kernel import import_git_snapshot
from context_kernel.archive import export_snapshot
from context_kernel.handoff import (build_handoff, verify_handoff, encode, digest,
                                    FORMAT, VERSION, CONSUMER_PROFILE)
from context_kernel.reads import KernelReadSnapshot
from test_context_transactions import STAMP

ROOT=Path(__file__).resolve().parents[1]


def resign(value):
    content={key:item for key,item in value.items() if key!='handoff_digest'}
    value['handoff_digest']=digest('handoff',content)
    return encode(value)


def projection_bytes(value):
    result={}
    for entry in value['continuity_projection']['files']:
        raw=(entry['content'].encode('utf-8') if entry['encoding']=='utf-8'
             else base64.b64decode(entry['content'],validate=True))
        result[entry['path']]=raw
    return result


class HandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='context-k4-handoff-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.head=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD']).decode().strip()
        cls.tree=subprocess.check_output(['git','-C',str(ROOT),'rev-parse',cls.head+'^{tree}']).decode().strip()
        cls.imported=import_git_snapshot(ROOT,cls.head,project_id='qiven-context',repository='JasonHuang3D/qiven-context',actor_assertion='fixture')
        cls.archive=export_snapshot(cls.imported.store.get,cls.imported.store.blob,cls.imported.snapshot_digest,
                                    access_policy='fixture:k4-handoff',observed_at=STAMP)
        cls.handoff=build_handoff(cls.archive)

    def test_exact_identity_projection_and_authority(self):
        verified=verify_handoff(self.handoff.encoded);value=verified.value
        self.assertEqual((value['format'],value['version']),(FORMAT,VERSION))
        self.assertEqual(value['consumer_profile']['id'],CONSUMER_PROFILE)
        self.assertEqual(value['source']['commit'],self.head)
        self.assertEqual(value['source']['tree'],self.tree)
        self.assertEqual(value['snapshot'],self.imported.snapshot_digest)
        self.assertEqual(value['manifest_digest'],self.archive.value['manifest_digest'])
        self.assertEqual(value['package_digest'],self.archive.value['package_digest'])
        self.assertEqual(value['authorization'],'not_granted');self.assertFalse(value['writes_enabled'])
        read=KernelReadSnapshot.capture(self.imported.store.get,self.imported.store.blob,self.imported.snapshot_digest)
        self.assertEqual(projection_bytes(value),dict(read.source.files))

    def test_plain_json_projection_contains_bootstrap_corpus(self):
        value=json.loads(self.handoff.encoded.decode('utf-8'))
        files={entry['path']:entry for entry in value['continuity_projection']['files']}
        for path in mandatory_paths(ROOT,{'view':'chatgpt-jason'}):
            self.assertIn(path,files);self.assertEqual(files[path]['encoding'],'utf-8')
            self.assertTrue(files[path]['content'])
        self.assertIn('collaboration/context-handoff-contract.md',files)
        self.assertIn('decisions/ADR-0034.md',files)

    def test_deterministic_for_same_canonical_export(self):
        self.assertEqual(build_handoff(self.archive).encoded,self.handoff.encoded)

    def test_outer_and_profile_tamper_fail_even_with_resign(self):
        value=self.handoff.value;value['source']['repository']='wrong/repository'
        with self.assertRaisesRegex(ValueError,'source identity'):verify_handoff(resign(value))
        value=self.handoff.value;value['consumer_profile']['phase_a']='allow_remote_reads'
        with self.assertRaisesRegex(ValueError,'consumer profile'):verify_handoff(resign(value))

    def test_unresigned_outer_tamper_fails_digest(self):
        value=self.handoff.value;value['source']['repository']='wrong/repository'
        with self.assertRaisesRegex(ValueError,'handoff digest'):verify_handoff(encode(value))

    def test_projection_tamper_missing_extra_and_digest_repair_fail(self):
        value=self.handoff.value
        entry=value['continuity_projection']['files'][0]
        entry['content']=entry['content']+'x'
        body={key:value['continuity_projection'][key] for key in ('version','source_snapshot_id','files')}
        value['continuity_projection']['projection_digest']=digest('projection',body)
        with self.assertRaisesRegex(ValueError,'projection differs|content integrity'):
            verify_handoff(resign(value))

        value=self.handoff.value;value['continuity_projection']['files'].pop()
        body={key:value['continuity_projection'][key] for key in ('version','source_snapshot_id','files')}
        value['continuity_projection']['projection_digest']=digest('projection',body)
        with self.assertRaisesRegex(ValueError,'projection differs'):verify_handoff(resign(value))

        value=self.handoff.value;value['continuity_projection']['files'].append(copy.deepcopy(value['continuity_projection']['files'][0]))
        body={key:value['continuity_projection'][key] for key in ('version','source_snapshot_id','files')}
        value['continuity_projection']['projection_digest']=digest('projection',body)
        with self.assertRaisesRegex(ValueError,'duplicate'):verify_handoff(resign(value))

    def test_nested_archive_tamper_cannot_be_hidden_by_outer_resign(self):
        value=self.handoff.value
        value['canonical_export']['delivery']['observed_at']='2026-09-17T20:00:00Z'
        with self.assertRaisesRegex(ValueError,'package digest'):verify_handoff(resign(value))

    def test_incomplete_export_cannot_be_handoff(self):
        key=self.archive.value['manifest']['blobs'][0]['digest']
        partial=export_snapshot(self.imported.store.get,self.imported.store.blob,self.imported.snapshot_digest,
                                access_policy='fixture',observed_at=STAMP,omit={key:'fixture omission'})
        with self.assertRaisesRegex(ValueError,'complete canonical recovery'):build_handoff(partial)

    def test_projection_entry_digest_is_checked_before_rebuild(self):
        value=self.handoff.value;entry=value['continuity_projection']['files'][0]
        entry['digest']='sha256:'+'0'*64
        body={key:value['continuity_projection'][key] for key in ('version','source_snapshot_id','files')}
        value['continuity_projection']['projection_digest']=digest('projection',body)
        with self.assertRaisesRegex(ValueError,'content integrity'):verify_handoff(resign(value))

    def test_cli_build_and_verify_exact_handoff(self):
        artifact=Path(self.temp.name)/'cli-handoff.json'
        built=subprocess.run([sys.executable,str(ROOT/'tools/context_archive.py'),'handoff-git',
            '--root',str(ROOT),'--commit',self.head,'--repository','JasonHuang3D/qiven-context',
            '--output',str(artifact)],capture_output=True,timeout=90)
        self.assertEqual(built.returncode,0,built.stderr.decode());first=json.loads(built.stdout)
        checked=subprocess.run([sys.executable,str(ROOT/'tools/context_archive.py'),'handoff-verify',
            '--input',str(artifact)],capture_output=True,timeout=90)
        self.assertEqual(checked.returncode,0,checked.stderr.decode());second=json.loads(checked.stdout)
        self.assertEqual(first['handoff_digest'],second['handoff_digest'])
        self.assertEqual(first['source_commit'],self.head)
        self.assertEqual(first['source_tree'],self.tree)

    def test_operator_declares_one_shot_jasonpc_acceptance_gate(self):
        config=json.loads((ROOT/'.qiven/operator.json').read_text())
        self.assertEqual(config['tasks']['k4-handoff-producer']['argv'],
                         ['.venv/Scripts/python.exe','tools/k4_handoff_producer.py'])
        self.assertEqual(config['gates']['k4-handoff-acceptance'],
                         ['bootstrap','full-tests','diff-check','clean-tree','k4-handoff-producer'])

    def test_fresh_process_verifies_without_git(self):
        path=Path(self.temp.name)/'handoff.json';path.write_bytes(self.handoff.encoded)
        process=subprocess.run([sys.executable,__file__,'--verify-only',str(path)],cwd=self.temp.name,
                               capture_output=True,timeout=90)
        self.assertEqual(process.returncode,0,process.stderr.decode())
        result=json.loads(process.stdout)
        self.assertEqual(result['handoff_digest'],self.handoff.value['handoff_digest'])
        self.assertGreater(result['files'],0)


if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--verify-only':
        import context_snapshot
        def forbidden(*args,**kwargs):raise AssertionError('Git must not participate in handoff consumption')
        context_snapshot._git=forbidden
        verified=verify_handoff(Path(sys.argv[2]).read_bytes())
        print(json.dumps({'handoff_digest':verified.handoff_digest,'files':len(verified.files)}))
    else:unittest.main(verbosity=2)
