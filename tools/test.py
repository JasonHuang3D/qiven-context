from pathlib import Path
import shutil, tempfile, unittest, yaml, json, sys, re
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from validate_context import validate_repository

class ValidatorTests(unittest.TestCase):
    def copy(self):
        d=Path(tempfile.mkdtemp())/"repo"; shutil.copytree(ROOT,d,ignore=shutil.ignore_patterns(".venv","__pycache__")); self.addCleanup(shutil.rmtree,d.parent,ignore_errors=True); return d
    def errors(self,d): return "\n".join(validate_repository(d))
    def sample_memory(self,d,name="MEM-20260913T010203Z-A1B2C3"):
        p=d/"memory/records"/f"{name}.md"; p.write_text(f"""---\nid: {name}\nkind: observation\nstatus: active\ntitle: Sample\nscope: [test]\ntags: []\ncreated_at: '2026-09-13T01:02:03Z'\nupdated_at: '2026-09-13T01:02:03Z'\nepistemic: {{basis: observed, confidence: high}}\ntemporal: {{valid_from: null, valid_until: null}}\nsources: [{{type: user_statement, reference: test}}]\nrelated: []\nsupersedes: []\nsuperseded_by: []\n---\n# Sample\n""",encoding="utf-8"); idx=yaml.safe_load((d/"memory/index.yaml").read_text()); idx["records"].append({"id":name,"file":p.name,"title":"Sample","status":"active"}); (d/"memory/index.yaml").write_text(yaml.safe_dump(idx,sort_keys=False)); return p
    def test_valid_record(self): d=self.copy(); self.sample_memory(d); self.assertEqual(self.errors(d),"")
    def test_missing_front_matter(self): d=self.copy(); p=self.sample_memory(d); p.write_text("# Sample\n"); self.assertIn("missing front matter",self.errors(d))
    def test_invalid_kind(self): d=self.copy(); p=self.sample_memory(d); p.write_text(p.read_text().replace("kind: observation","kind: decision")); self.assertIn("not one of",self.errors(d))
    def test_filename_id_mismatch(self): d=self.copy(); p=self.sample_memory(d); p.rename(p.with_name("MEM-20260913T010203Z-FFFFFF.md")); self.assertIn("filename/id mismatch",self.errors(d))
    def test_duplicate_canonical_id(self): d=self.copy(); p=self.sample_memory(d); q=d/"memory/records/duplicate.md"; q.write_text(p.read_text()); self.assertIn("duplicate canonical ID",self.errors(d))
    def test_obligation_without_trigger(self): d=self.copy(); p=next((d/"obligations").glob("OBL-*.md")); txt=p.read_text(); txt=re.sub(r"trigger:\n(?:  .+\n)+(?=completion:)","",txt); p.write_text(txt); self.assertIn("trigger",self.errors(d))
    def test_manual_trigger_without_reason(self): d=self.copy(); p=next((d/"obligations").glob("OBL-*.md")); txt=p.read_text().replace("type: after","type: manual"); p.write_text(txt); self.assertIn("reason",self.errors(d))
    def test_invalid_adr_status(self): d=self.copy(); p=d/"decisions/ADR-0001.md"; p.write_text(p.read_text().replace("status: accepted","status: obsolete")); self.assertIn("not one of",self.errors(d))
    def test_missing_adr_heading(self): d=self.copy(); p=d/"decisions/ADR-0001.md"; p.write_text(p.read_text().replace("## Provenance","## Sources")); self.assertIn("missing ADR heading Provenance",self.errors(d))
    def test_bad_jsonl_event(self): d=self.copy(); p=next((d/"ledger/events").glob("*.jsonl")); p.write_text(p.read_text()+"{bad}\n"); self.assertIn("bad JSONL event",self.errors(d))
    def test_duplicate_ledger_event_id(self): d=self.copy(); p=next((d/"ledger/events").glob("*.jsonl")); first=p.read_text().splitlines()[0]; p.write_text(p.read_text()+first+"\n"); self.assertIn("duplicate ledger event ID",self.errors(d))
    def test_index_missing_record(self): d=self.copy(); idx=yaml.safe_load((d/"memory/index.yaml").read_text()); idx["records"].append({"id":"MEM-20260913T010203Z-A1B2C3","file":"missing.md","title":"x","status":"active"}); (d/"memory/index.yaml").write_text(yaml.safe_dump(idx)); self.assertIn("index points to missing record",self.errors(d))
    def test_unindexed_record(self): d=self.copy(); p=self.sample_memory(d); (d/"memory/index.yaml").write_text("schema_version: 1\nrecords: []\n"); self.assertIn("unindexed canonical record",self.errors(d))
    def test_invalid_sha(self): d=self.copy(); p=d/"state/repositories.yaml"; p.write_text(p.read_text().replace("f1880847e046425c7f3f3cad22a07d0008aad359","abc")); self.assertIn("does not match",self.errors(d))
    def test_invalid_timestamp(self): d=self.copy(); p=d/"state/active-work.yaml"; p.write_text(re.sub(r"updated_at: .+","updated_at: 'not-a-timestamp'",p.read_text())); self.assertIn("invalid timestamp",self.errors(d))
    def test_broken_internal_relation(self): d=self.copy(); p=self.sample_memory(d); p.write_text(p.read_text().replace("related: []","related: [ADR-9999]")); self.assertIn("broken internal relation",self.errors(d))

if __name__=="__main__":
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ValidatorTests))
    if not result.wasSuccessful(): raise SystemExit(1)
    errors=validate_repository(ROOT)
    if errors: print("Repository validation failed after unit tests:\n"+"\n".join(errors)); raise SystemExit(1)
    print("Unit tests and repository validation PASS")
