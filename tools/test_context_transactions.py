from __future__ import annotations
import base64
import copy
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
from threading import Barrier
import unittest
from context_kernel import KernelObject, import_git_snapshot
from context_kernel.sqlite_reference import SQLiteReference
from context_kernel.transactions import Authentication, BeforeCommitFailure, ContextTransactions

ROOT=Path(__file__).resolve().parents[1]
NOW=datetime(2026,9,17,15,0,tzinfo=timezone.utc)
STAMP='2026-09-17T15:00:00Z'
ACTIONS=frozenset(('create_record','revise_record','transition_record','relate','add_evidence',
                   'add_external_evidence','put_document','set_governance','read_result'))


class FixtureIdentity:
    """Explicit trusted test double; names below are fixture sessions, not credentials."""
    def __init__(self):
        self.revoked=set()
        self.expired=False
        self.calls=0
    def authenticate(self,session,project_id):
        self.calls+=1
        if session in self.revoked or session not in ('owner','writer','reader'):
            return None
        permissions=ACTIONS if session=='owner' else ACTIONS-{'set_governance'} if session=='writer' else frozenset({'read_result'})
        return Authentication(project_id,session,permissions,NOW+timedelta(days=-1 if self.expired else 1),'fixture-live-auth')


def engine(path,identity=None,fault=None):
    return ContextTransactions(SQLiteReference(path),identity or FixtureIdentity(),clock=lambda:NOW,fault=fault)


class TransactionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='context-k2-')
        cls.seed=Path(cls.temp.name)/'seed.db'
        commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD']).decode().strip()
        cls.imported=import_git_snapshot(ROOT,commit,project_id='qiven-context',
             repository='asserted:K2-fixture',actor_assertion='fixture importer')
        adapter=SQLiteReference(cls.seed)
        cls.policy={'project_id':'qiven-context','authority_scope':'reference-sandbox',
                    'grants':{'owner':sorted(ACTIONS),'writer':sorted(ACTIONS-{'set_governance'}),'reader':['read_result']}}
        adapter.bootstrap_quarantine(cls.imported,cls.policy)

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def setUp(self):
        self.case=tempfile.TemporaryDirectory(dir=self.temp.name)
        self.addCleanup(self.case.cleanup)
        self.path=Path(self.case.name)/'store.db'
        with sqlite3.connect(self.seed) as source, sqlite3.connect(self.path) as target:
            source.backup(target)
        self.identity=FixtureIdentity()
        self.kernel=engine(self.path,self.identity)
        self.adapter=self.kernel.adapter

    def snapshot(self):
        with self.adapter.connect() as db:
            head=self.adapter.head(db,'qiven-context')
            return head,self.adapter.get(db,head).payload

    def request(self,key='one',principal='owner'):
        head,base=self.snapshot()
        document=next(x['document'] for x in base['documents'] if x['path']=='state/current.md')
        return {'project_id':'qiven-context','transaction_id':'tx-'+key,'idempotency_key':key,
                'principal':principal,'base_snapshot':head,'governance_version':base['governance'],
                'semantic_time':STAMP,'expected_revisions':{},'evidence':[],'depends_on':[],
                'operations':[{'op':'put_document','path':'state/current.md','expected_document':document,
                               'content_base64':base64.b64encode(('# '+key+'\n').encode()).decode(),'rationale':'fixture state update'}]}

    def record_request(self,key='record',rid='ADR-0033'):
        request=self.request(key)
        _,base=self.snapshot()
        digest=next(x['revision'] for x in base['records'] if x['record_id']==rid)
        with self.adapter.connect() as db: record=self.adapter.get(db,digest).payload
        metadata=copy.deepcopy(record['metadata']); metadata['updated_at']=STAMP
        request['operations']=[{'op':'revise_record','record_kind':record['record_kind'],
                                'metadata':metadata,'body':record['body']+'\nFixture revision.\n','rationale':'test revision'}]
        request['expected_revisions']={rid:digest}
        request['evidence']=[base['evidence'][0]]
        return request

    def commit(self,p): return self.kernel.commit_transaction(p,p['principal'])

    def count(self,table,where='1'):
        with self.adapter.connect() as db:
            return db.execute(f'SELECT COUNT(*) FROM {table} WHERE {where}').fetchone()[0]

    def test_commit_binds_all_evidence_and_retains_predecessor(self):
        p=self.record_request(); old=self.snapshot()[0]
        out=self.commit(p)
        self.assertEqual(out.status,'committed')
        with self.adapter.connect() as db:
            receipt=self.adapter.get(db,out.receipt).payload
            decision=self.adapter.get(db,receipt['authority_decision']).payload
            revision=self.adapter.get(db,receipt['revision_digests'][0]).payload
            self.assertEqual(decision['request_digest'],KernelObject.create('TransactionRequest',p).digest)
            self.assertEqual(decision['base_snapshot'],old)
            self.assertEqual(decision['governance_version'],p['governance_version'])
            self.assertEqual(revision['predecessor_revision'],p['expected_revisions']['ADR-0033'])
            self.assertEqual(revision['creating_transaction'],p['transaction_id'])
            self.assertEqual(revision['principal'],'owner')
            self.assertEqual(self.adapter.get(db,old).payload['creating_transaction'],None)
        self.assertEqual(self.snapshot()[0],out.successor)

    def test_same_key_replay_after_head_advance_returns_original(self):
        p=self.request(); first=self.commit(p)
        second=self.commit(self.request('two'))
        self.assertEqual(second.status,'committed')
        self.assertEqual(self.commit(p),first)
        self.assertEqual(self.snapshot()[0],second.successor)
        self.assertEqual(self.count('attempts',"status='committed'"),2)

    def test_same_key_changed_payload_and_reused_transaction_id_rejected(self):
        p=self.request(); self.commit(p)
        changed=copy.deepcopy(p); changed['semantic_time']='2026-09-17T15:00:01Z'
        self.assertEqual(self.commit(changed).code,'idempotency_conflict')
        changed=self.request('different'); changed['transaction_id']=p['transaction_id']
        self.assertEqual(self.commit(changed).code,'transaction_id_conflict')

    def test_different_writers_on_same_base_only_one_commits(self):
        a=self.request('a'); b=self.request('b','writer'); barrier=Barrier(2)
        def run(p):
            barrier.wait()
            return engine(self.path).commit_transaction(p,p['principal'])
        with ThreadPoolExecutor(2) as pool: results=list(pool.map(run,[a,b]))
        self.assertEqual(sorted(r.status for r in results),['committed','not_committed'])
        self.assertIn('stale_base',[r.code for r in results])
        self.assertEqual(self.count('attempts',"status='committed'"),1)

    def test_same_key_concurrent_retries_publish_once(self):
        p=self.request(); barrier=Barrier(4)
        def run(_):
            barrier.wait()
            return engine(self.path).commit_transaction(p,'owner')
        with ThreadPoolExecutor(4) as pool: results=list(pool.map(run,range(4)))
        self.assertTrue(all(r==results[0] and r.status=='committed' for r in results))
        self.assertEqual(self.count('attempts'),1)

    def test_preconditions_and_missing_evidence_reject_without_head_change(self):
        before=self.snapshot()[0]
        for i,mutation,expected in (
            (1,lambda p:p['expected_revisions'].__setitem__('ADR-0033','sha256:'+'0'*64),'expected_revision_mismatch'),
            (2,lambda p:p.__setitem__('evidence',[]),'incomplete_evidence'),
            (3,lambda p:p.__setitem__('governance_version','sha256:'+'0'*64),'governance_version_mismatch'),
            (4,lambda p:p.__setitem__('evidence',['sha256:'+'0'*64]),'incomplete_evidence')):
            p=self.record_request(str(i));mutation(p)
            self.assertEqual(self.commit(p).code,expected)
        self.assertEqual(self.snapshot()[0],before)

    def test_validation_is_advisory_and_revocation_is_rechecked(self):
        p=self.request(); count=self.count('objects')
        self.assertEqual(self.kernel.validate_transaction(p,'owner').status,'advisory_valid')
        self.assertEqual(self.count('attempts'),0);self.assertEqual(self.count('objects'),count)
        self.identity.revoked.add('owner')
        self.assertEqual(self.commit(p).status,'access_denied')

    def test_revocation_between_preparation_and_publication(self):
        p=self.request(); head=self.snapshot()[0]
        self.kernel.fault=lambda stage:self.identity.revoked.add('owner') if stage=='before_authorization' else None
        out=self.commit(p)
        self.assertEqual((out.status,out.code),('not_committed','unauthorized'))
        self.assertEqual(self.snapshot()[0],head)

    def test_expired_identity_mismatched_principal_and_grant_rejected(self):
        p=self.request();self.identity.expired=True
        self.assertEqual(self.commit(p).status,'access_denied')
        self.identity.expired=False
        self.assertEqual(self.kernel.commit_transaction(p,'writer').status,'access_denied')
        p=self.request('reader','reader')
        self.assertEqual(self.commit(p).code,'unauthorized')

    def test_governance_cannot_authorize_its_own_installation(self):
        p=self.request(principal='writer');new=copy.deepcopy(self.policy);new['grants']['writer']=sorted(ACTIONS)
        p['operations']=[{'op':'set_governance','policy':new,'rationale':'attempt self authorization'}]
        before=self.snapshot()[0]
        self.assertEqual(self.commit(p).code,'unauthorized')
        self.assertEqual(self.snapshot()[0],before)

    def test_old_policy_authorizes_governance_change_and_new_policy_applies(self):
        stale=self.request('stale','writer'); p=self.request('policy');new=copy.deepcopy(self.policy)
        new['grants']['writer']=['read_result']
        p['operations']=[{'op':'set_governance','policy':new,'rationale':'owner revokes writer'}]
        self.assertEqual(self.commit(p).status,'committed')
        self.assertEqual(self.commit(stale).code,'stale_base')
        self.assertEqual(self.commit(self.request('later','writer')).code,'unauthorized')

    def test_invalid_lifecycle_is_atomic(self):
        p=self.record_request();p['operations'][0]['op']='transition_record'
        p['operations'][0]['metadata']['status']='superseded'
        before=self.snapshot()[0]
        self.assertEqual(self.commit(p).code,'invalid_lifecycle')
        self.assertEqual(self.snapshot()[0],before)

    def test_reciprocal_supersession_transaction(self):
        p=self.record_request();old=p['operations'][0];old['op']='transition_record'
        old['metadata']['status']='superseded'
        new=copy.deepcopy(old);new['op']='create_record';new['metadata']['id']='ADR-0099'
        new['metadata']['status']='accepted';new['metadata']['created_at']=STAMP
        new['metadata']['supersedes']=[];new['metadata']['superseded_by']=[]
        p['operations']=[new,old,{'op':'relate','relation':'supersedes','source':'ADR-0099','target':'ADR-0033','mode':'add','rationale':'fixture replacement'}]
        p['expected_revisions']['ADR-0099']=None
        out=self.commit(p);self.assertEqual(out.status,'committed')
        with self.adapter.connect() as db:
            for e in self.adapter.get(db,out.successor).payload['records']:
                if e['record_id']=='ADR-0033':
                    self.assertEqual(self.adapter.get(db,e['revision']).payload['metadata']['superseded_by'],['ADR-0099'])

    def test_new_evidence_and_external_unknown_are_preserved(self):
        p=self.request()
        p['operations']=[{'op':'add_evidence','media_type':'application/octet-stream','content_base64':base64.b64encode(b'\0raw\xff').decode()},
                         {'op':'add_external_evidence','media_type':'text/plain','reference':'fixture:unavailable','expected_content_digest':None}]
        out=self.commit(p);self.assertEqual(out.status,'committed')
        with self.adapter.connect() as db:
            values=[self.adapter.get(db,d) for d in self.adapter.get(db,out.successor).payload['evidence']]
            external=next(v for v in values if v.kind=='ExternalEvidenceReference')
            self.assertEqual(external.payload['availability'],'unverified')
            self.assertIsNone(external.payload['expected_content_digest'])

    def test_unknown_dependency_and_absent_result_do_not_claim_rollback(self):
        result=self.kernel.get_transaction_result('qiven-context','absent','owner')
        self.assertEqual(result.status,'outcome_unknown')
        p=self.request();p['depends_on']=['unresolved']
        self.assertEqual(self.commit(p).code,'dependency_outcome_unknown')

    def test_known_precommit_failure_rolls_back_successor_objects(self):
        p=self.request();before=self.snapshot()[0];objects=self.count('objects')
        def fault(stage):
            if stage=='before_commit':raise BeforeCommitFailure()
        self.kernel.fault=fault
        out=self.commit(p)
        self.assertEqual(out.status,'not_committed');self.assertEqual(self.snapshot()[0],before)
        self.assertEqual(self.count('objects'),objects+1) # only the staged request reservation
        self.assertEqual(engine(self.path).commit_transaction(p,'owner'),out)

    def test_lost_acknowledgement_returns_unknown_then_exact_receipt(self):
        p=self.request()
        def fault(stage):
            if stage=='after_commit':raise TimeoutError('fixture lost acknowledgement')
        self.kernel.fault=fault
        self.assertEqual(self.commit(p).status,'outcome_unknown')
        recovered=engine(self.path).commit_transaction(p,'owner')
        self.assertEqual(recovered.status,'committed')
        self.assertEqual(recovered,engine(self.path).get_transaction_result('qiven-context','one','owner'))
        self.assertEqual(self.count('attempts',"status='committed'"),1)

    def test_abort_is_durable_and_cannot_undo_committed(self):
        p=self.request();out=self.kernel.abort_transaction(p,'owner')
        self.assertEqual(out.code,'aborted');self.assertEqual(self.commit(p),out)
        p=self.request('commits');out=self.commit(p)
        self.assertEqual(self.kernel.abort_transaction(p,'owner'),out)
        self.assertEqual(self.snapshot()[0],out.successor)

    def test_result_access_is_principal_scoped_and_revocable(self):
        p=self.request();self.commit(p)
        self.assertEqual(self.kernel.get_transaction_result('qiven-context','one','writer').status,'outcome_unknown')
        self.identity.revoked.add('owner')
        self.assertEqual(self.kernel.get_transaction_result('qiven-context','one','owner').status,'access_denied')

    def test_process_crash_recovery_at_three_atomic_boundaries(self):
        for stage in ('after_reservation','before_commit','after_commit'):
            with self.subTest(stage=stage):
                p=self.request(stage);path=Path(self.case.name)/(stage+'.json');path.write_text(json.dumps(p))
                before=self.snapshot()[0]
                child=subprocess.run([sys.executable,__file__,'--crash',str(self.path),str(path),stage],capture_output=True,timeout=40)
                self.assertEqual(child.returncode,73,child.stderr.decode())
                fresh=engine(self.path)
                observed=fresh.get_transaction_result('qiven-context',stage,'owner')
                self.assertEqual(observed.status,'committed' if stage=='after_commit' else 'outcome_unknown')
                if stage!='after_commit':self.assertEqual(self.snapshot()[0],before)
                recovered=fresh.commit_transaction(p,'owner')
                self.assertEqual(recovered.status,'committed')
                self.assertEqual(fresh.commit_transaction(p,'owner'),recovered)
                self.assertEqual(self.snapshot()[0],recovered.successor)
        self.assertEqual(self.count('attempts',"status='committed'"),3)

    def test_conflicting_request_cannot_steal_pending_key(self):
        p=self.request()
        def fault(stage):
            if stage=='after_reservation':raise TimeoutError('stop after durable reservation')
        self.kernel.fault=fault
        self.assertEqual(self.commit(p).status,'outcome_unknown')
        changed=copy.deepcopy(p);changed['transaction_id']='different'
        self.assertEqual(engine(self.path).commit_transaction(changed,'owner').code,'idempotency_conflict')
        self.assertEqual(engine(self.path).commit_transaction(p,'owner').status,'committed')

    def test_same_key_is_scoped_by_authenticated_principal(self):
        first=self.commit(self.request('shared'))
        second=self.request('shared','writer');second['transaction_id']='writer-distinct-id'
        out=self.commit(second)
        self.assertEqual(out.status,'committed')
        self.assertNotEqual(out.receipt,first.receipt)
        self.assertEqual(self.kernel.get_transaction_result('qiven-context','shared','owner'),first)
        self.assertEqual(self.kernel.get_transaction_result('qiven-context','shared','writer'),out)

    def test_abort_races_commit_without_undoing_winner(self):
        p=self.request();barrier=Barrier(2)
        def run(abort):
            k=engine(self.path);barrier.wait()
            return k.abort_transaction(p,'owner') if abort else k.commit_transaction(p,'owner')
        with ThreadPoolExecutor(2) as pool: results=list(pool.map(run,[True,False]))
        self.assertEqual(results[0],results[1])
        self.assertIn(results[0].status,('committed','not_committed'))
        self.assertEqual(self.count('attempts'),1)

    def test_record_time_cannot_move_backward(self):
        p=self.record_request();p['semantic_time']='2000-01-01T00:00:00Z'
        p['operations'][0]['metadata']['updated_at']=p['semantic_time']
        self.assertEqual(self.commit(p).code,'record_time_regression')

    def test_unknown_operation_and_malformed_view_are_definite_rejections(self):
        p=self.request();p['operations'][0]['op']='run_shell'
        self.assertEqual(self.commit(p).code,'invalid_request')
        p=self.request('view');p['operations'][0].update(path='views/new.yaml',expected_document=None,
            content_base64=base64.b64encode(b'id: new\nstatus: active\nproject_context: []\n').decode())
        self.assertEqual(self.commit(p).code,'invalid_view')

    def test_invalid_namespace_cannot_bypass_governance(self):
        for i,path in enumerate(('governance/authority.yaml','../state/current.md','decisions/ADR-0033.md')):
            p=self.request(str(i));p['operations'][0]['path']=path
            self.assertEqual(self.commit(p).status,'not_committed')


if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--crash':
        path,request_file,stage=sys.argv[2:]
        def crash(point):
            if point==stage:os._exit(73)
        engine(path,fault=crash).commit_transaction(json.loads(Path(request_file).read_text()),'owner')
        raise SystemExit(74)
    unittest.main(verbosity=2)
