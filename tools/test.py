from pathlib import Path
import shutil, tempfile, unittest, yaml, json, sys, re
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from validate_context import validate_repository

class ValidatorTests(unittest.TestCase):
    fixture=None
    @classmethod
    def setUpClass(cls):
        # one microcosm fixture (validator_fixture); each test copies the
        # ~70-file representative corpus instead of the real 500-file tree
        import validator_fixture
        base=Path(tempfile.mkdtemp())/"fixture"; validator_fixture.build(base); cls.fixture=base
        cls.addClassCleanup(shutil.rmtree,base.parent,ignore_errors=True)
    def copy(self):
        d=Path(tempfile.mkdtemp())/"repo"; shutil.copytree(self.fixture,d); self.addCleanup(shutil.rmtree,d.parent,ignore_errors=True); return d
    def errors(self,d): return "\n".join(validate_repository(d))
    def rewrite_front_matter(self,p,mutate):
        txt=p.read_text(encoding="utf-8"); raw,body=txt[4:].split("\n---\n",1); data=yaml.safe_load(raw); mutate(data); rendered=yaml.safe_dump(data,sort_keys=False,allow_unicode=True).rstrip(); p.write_text(f"---\n{rendered}\n---\n{body}",encoding="utf-8")
    def nonterminal_obligation(self,d,require_nonmanual=False):
        for p in sorted((d/"obligations").glob("OBL-*.md")):
            txt=p.read_text(encoding="utf-8"); raw,_=txt[4:].split("\n---\n",1); data=yaml.safe_load(raw); trigger=data.get("trigger")
            if data.get("status") not in {"open","deferred","blocked"} or not isinstance(trigger,dict): continue
            if require_nonmanual and trigger.get("type")=="manual": continue
            return p
        self.fail("expected at least one non-terminal obligation with a trigger")
    def sample_memory(self,d,name="MEM-20260913T010203Z-A1B2C3"):
        p=d/"memory/records"/f"{name}.md"; p.write_text(f"""---\nid: {name}\nkind: observation\nstatus: active\ntitle: Sample\nscope: [test]\ntags: []\ncreated_at: '2026-09-13T01:02:03Z'\nupdated_at: '2026-09-13T01:02:03Z'\nepistemic: {{basis: observed, confidence: high}}\ntemporal: {{valid_from: '2026-09-13T01:02:03Z', valid_until: null}}\nsources: [{{type: user_statement, reference: test}}]\nrelated: []\nsupersedes: []\nsuperseded_by: []\n---\n# Sample\n""",encoding="utf-8"); idx=yaml.safe_load((d/"memory/index.yaml").read_text()); idx["records"].append({"id":name,"file":p.name,"title":"Sample","status":"active"}); (d/"memory/index.yaml").write_text(yaml.safe_dump(idx,sort_keys=False)); return p
    def test_repository_is_valid(self): self.assertEqual(self.errors(self.copy()),"")
    def test_valid_record(self): d=self.copy(); self.sample_memory(d); self.assertEqual(self.errors(d),"")
    def test_missing_front_matter(self): d=self.copy(); p=self.sample_memory(d); p.write_text("# Sample\n"); self.assertIn("missing front matter",self.errors(d))
    def test_invalid_kind(self): d=self.copy(); p=self.sample_memory(d); p.write_text(p.read_text().replace("kind: observation","kind: decision")); self.assertIn("not one of",self.errors(d))
    def test_filename_id_mismatch(self): d=self.copy(); p=self.sample_memory(d); p.rename(p.with_name("MEM-20260913T010203Z-FFFFFF.md")); self.assertIn("filename/id mismatch",self.errors(d))
    def test_duplicate_canonical_id(self): d=self.copy(); p=self.sample_memory(d); q=d/"memory/records/duplicate.md"; q.write_text(p.read_text()); self.assertIn("duplicate canonical ID",self.errors(d))
    def test_obligation_without_trigger(self): d=self.copy(); p=self.nonterminal_obligation(d); self.rewrite_front_matter(p,lambda data:data.pop("trigger")); self.assertIn("trigger",self.errors(d))
    def test_nonmanual_trigger_without_value(self): d=self.copy(); p=self.nonterminal_obligation(d,True); self.rewrite_front_matter(p,lambda data:data["trigger"].pop("value")); self.assertIn("'value' is a required property",self.errors(d))
    def test_invalid_adr_status(self): d=self.copy(); p=d/"decisions/ADR-0003.md"; p.write_text(p.read_text().replace("status: accepted","status: obsolete")); self.assertIn("not one of",self.errors(d))
    def test_missing_adr_heading(self): d=self.copy(); p=d/"decisions/ADR-0003.md"; p.write_text(p.read_text().replace("## Provenance","## Sources")); self.assertIn("missing ADR heading Provenance",self.errors(d))
    def test_bad_jsonl_event(self): d=self.copy(); p=next((d/"legacy/ledger/events").glob("*.jsonl")); p.write_text(p.read_text()+"{bad}\n"); self.assertIn("bad JSONL event",self.errors(d))
    def test_duplicate_ledger_event_id(self): d=self.copy(); p=next((d/"legacy/ledger/events").glob("*.jsonl")); first=p.read_text().splitlines()[0]; p.write_text(p.read_text()+first+"\n"); self.assertIn("duplicate ledger event ID",self.errors(d))
    def test_new_ledger_file_is_forbidden(self): d=self.copy(); (d/"legacy/ledger/events/2026-09-16.jsonl").write_text("",encoding="utf-8"); self.assertIn("forbids new manual ledger files",self.errors(d))
    def test_collaboration_handoff_is_forbidden(self): d=self.copy(); (d/"collaboration/v99-handoff.md").write_text("# bad\n"); self.assertIn("session handoff is forbidden",self.errors(d))
    def test_deprecated_evidence_bucket_rejects_new_record(self): d=self.copy(); (d/"legacy/evidence/ci/run.md").write_text("x"); self.assertIn("deprecated active bucket",self.errors(d))
    def test_repository_inventory_rejects_live_sha(self):
        d=self.copy(); p=d/"state/repositories.yaml"; data=yaml.safe_load(p.read_text()); data["repositories"][0]["main_sha"]="0"*40; p.write_text(yaml.safe_dump(data,sort_keys=False)); self.assertIn("main_sha",self.errors(d))
    def test_governance_provider_is_enforced(self): d=self.copy(); p=d/"governance/authority.yaml"; p.write_text(p.read_text().replace("trust_provider: github","trust_provider: local")); self.assertIn("github",self.errors(d))
    def test_missing_session_next_action(self):
        d=self.copy()
        sessions=[p for p in (d/"sessions").glob("*.md") if re.match(r"^\d{4}-\d{2}-\d{2}-qiven-v\d+\.md$",p.name)]
        p=max(sessions,key=lambda item:(item.name[:10],int(re.search(r"-v(\d+)\.md$",item.name).group(1))))
        p.write_text(p.read_text().replace("## Next action","## Later"))
        self.assertIn("missing session heading Next action",self.errors(d))
    def test_superseded_record_requires_successor(self): d=self.copy(); p=d/"decisions/ADR-0001.md"; self.rewrite_front_matter(p,lambda data:data.__setitem__("superseded_by",[])); self.assertIn("requires superseded_by",self.errors(d))
    def test_supersession_relation_must_be_reciprocal(self):
        d=self.copy(); p=d/"decisions/ADR-0026.md"
        self.rewrite_front_matter(p,lambda data:data.__setitem__("supersedes",[rid for rid in data["supersedes"] if rid!="MEM-20260915T092000Z-3C7A41"]))
        self.assertIn("non-reciprocal superseded_by relation",self.errors(d))
    def test_only_superseded_records_may_name_successors(self):
        d=self.copy(); p=d/"decisions/ADR-0003.md"
        self.rewrite_front_matter(p,lambda data:data.__setitem__("superseded_by",["ADR-0030"]))
        self.assertIn("only superseded records may declare superseded_by",self.errors(d))
    def test_supersedes_target_must_be_superseded(self):
        d=self.copy(); successor=d/"decisions/ADR-0030.md"; target=d/"decisions/ADR-0003.md"
        self.rewrite_front_matter(successor,lambda data:data.__setitem__("supersedes",data["supersedes"]+["ADR-0003"]))
        self.rewrite_front_matter(target,lambda data:data.__setitem__("superseded_by",["ADR-0030"]))
        self.assertIn("supersedes target ADR-0003 is not superseded",self.errors(d))
    def test_self_supersession_is_forbidden(self):
        d=self.copy(); p=d/"decisions/ADR-0030.md"
        self.rewrite_front_matter(p,lambda data:data.__setitem__("supersedes",data["supersedes"]+["ADR-0030"]))
        self.assertIn("self supersession is forbidden",self.errors(d))
    def test_supersession_graph_is_acyclic(self):
        d=self.copy(); older=d/"memory/records/MEM-20260913T183819Z-C2D841.md"; newer=d/"memory/records/MEM-20260915T111500Z-42A7D1.md"
        self.rewrite_front_matter(older,lambda data:data.__setitem__("supersedes",["MEM-20260915T111500Z-42A7D1"]))
        self.rewrite_front_matter(newer,lambda data:data.__setitem__("superseded_by",data["superseded_by"]+["MEM-20260913T183819Z-C2D841"]))
        self.assertIn("supersession cycle",self.errors(d))
    def test_superseded_obligation_requires_successor(self):
        d=self.copy(); p=next(p for p in (d/"obligations").glob("OBL-*.md") if "status: done" in p.read_text(encoding="utf-8"))
        self.rewrite_front_matter(p,lambda data:data.__setitem__("status","superseded"))
        self.assertIn("superseded_by",self.errors(d))
    def test_duplicate_supersession_relation_is_forbidden(self):
        d=self.copy(); p=d/"decisions/ADR-0030.md"
        self.rewrite_front_matter(p,lambda data:data.__setitem__("supersedes",data["supersedes"]+[data["supersedes"][0]]))
        self.assertIn("non-unique elements",self.errors(d))
    def test_malformed_lifecycle_relation_returns_diagnostics(self):
        d=self.copy(); p=d/"decisions/ADR-0033.md"
        self.rewrite_front_matter(p,lambda data:data.__setitem__("supersedes",[{}]))
        self.assertIn("must be a list of record IDs",self.errors(d))
    def test_index_missing_record(self): d=self.copy(); idx=yaml.safe_load((d/"memory/index.yaml").read_text()); idx["records"].append({"id":"MEM-20260913T010203Z-A1B2C3","file":"missing.md","title":"x","status":"active"}); (d/"memory/index.yaml").write_text(yaml.safe_dump(idx)); self.assertIn("index points to missing record",self.errors(d))
    def test_invalid_timestamp(self): d=self.copy(); p=d/"state/active-work.yaml"; p.write_text(re.sub(r"updated_at: .+","updated_at: 'not-a-timestamp'",p.read_text())); self.assertIn("invalid timestamp",self.errors(d))
    def test_broken_internal_relation(self): d=self.copy(); p=self.sample_memory(d); p.write_text(p.read_text().replace("related: []","related: [ADR-9999]")); self.assertIn("broken internal relation",self.errors(d))
    def test_default_retrieval_corpus_excludes_superseded_records(self):
        ids=set()
        for folder in ("decisions","decisions/legacy","memory/records","obligations","obligations/legacy"):
            for f in (ROOT/folder).glob("*.md"):
                if f.name=="README.md": continue
                text=f.read_text(encoding="utf-8")
                m=re.search(r"^id: ([A-Z]+-\S+)$",text,re.M)
                s=re.search(r"^status: (\S+)$",text,re.M)
                if m and (not s or s.group(1)!="superseded"): ids.add(m.group(1))
        self.assertNotIn("ADR-0001",ids); self.assertNotIn("ADR-0002",ids); self.assertNotIn("ADR-0007",ids)
        self.assertNotIn("MEM-20260915T092000Z-3C7A41",ids); self.assertNotIn("MEM-20260915T111500Z-42A7D1",ids)
        self.assertIn("ADR-0030",ids); self.assertIn("ADR-0031",ids)
    def test_plain_generated_dir_is_forbidden(self): d=self.copy(); (d/"generated").mkdir(); (d/"generated/GLOBAL_CONTEXT.md").write_text("# Derived\n"); self.assertIn("forbidden generated directory",self.errors(d))

if __name__=="__main__":
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ValidatorTests))
    if not result.wasSuccessful(): raise SystemExit(1)
    errors=validate_repository(ROOT)
    if errors: print("Repository validation failed after unit tests:\n"+"\n".join(errors)); raise SystemExit(1)
    print("Unit tests and repository validation PASS")
