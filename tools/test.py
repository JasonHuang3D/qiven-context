from pathlib import Path
import shutil, tempfile, unittest, yaml, json, sys, re
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from validate_context import validate_repository

class ValidatorTests(unittest.TestCase):
    def copy(self):
        d=Path(tempfile.mkdtemp())/"repo"; shutil.copytree(ROOT,d,ignore=shutil.ignore_patterns(".venv","__pycache__",".git")); self.addCleanup(shutil.rmtree,d.parent,ignore_errors=True); return d
    def errors(self,d): return "\n".join(validate_repository(d))
    def rewrite_front_matter(self,p,mutate):
        txt=p.read_text(encoding="utf-8"); raw,body=txt[4:].split("\n---\n",1); data=yaml.safe_load(raw); mutate(data); rendered=yaml.safe_dump(data,sort_keys=False,allow_unicode=True).rstrip(); p.write_text(f"---\n{rendered}\n---\n{body}",encoding="utf-8")
    def sample_memory(self,d,name="MEM-20260913T010203Z-A1B2C3"):
        p=d/"memory/records"/f"{name}.md"; p.write_text(f"""---
id: {name}
kind: observation
status: active
title: Sample
scope: [test]
tags: []
created_at: '2026-09-13T01:02:03Z'
updated_at: '2026-09-13T01:02:03Z'
epistemic: {{basis: observed, confidence: high}}
temporal: {{valid_from: '2026-09-13T01:02:03Z', valid_until: null}}
sources: [{{type: user_statement, reference: test}}]
related: []
supersedes: []
superseded_by: []
---
# Sample
""",encoding="utf-8"); idx=yaml.safe_load((d/"memory/index.yaml").read_text()); idx["records"].append({"id":name,"file":p.name,"title":"Sample","status":"active"}); (d/"memory/index.yaml").write_text(yaml.safe_dump(idx,sort_keys=False)); return p
    def test_valid_record(self): d=self.copy(); self.sample_memory(d); self.assertEqual(self.errors(d),"")
    def test_missing_front_matter(self): d=self.copy(); p=self.sample_memory(d); p.write_text("# Sample\n"); self.assertIn("missing front matter",self.errors(d))
    def test_invalid_kind(self): d=self.copy(); p=self.sample_memory(d); p.write_text(p.read_text().replace("kind: observation","kind: decision")); self.assertIn("not one of",self.errors(d))
    def test_filename_id_mismatch(self): d=self.copy(); p=self.sample_memory(d); p.rename(p.with_name("MEM-20260913T010203Z-FFFFFF.md")); self.assertIn("filename/id mismatch",self.errors(d))
    def test_duplicate_canonical_id(self): d=self.copy(); p=self.sample_memory(d); q=d/"memory/records/duplicate.md"; q.write_text(p.read_text()); self.assertIn("duplicate canonical ID",self.errors(d))
    def test_obligation_without_trigger(self):
        d=self.copy(); p=d/"obligations/OBL-20260913T152950Z-D4E5F6.md"; self.rewrite_front_matter(p,lambda data:data.pop("trigger")); self.assertIn("trigger",self.errors(d))
    def test_nonmanual_trigger_without_value(self):
        d=self.copy(); p=d/"obligations/OBL-20260913T152950Z-D4E5F6.md"; self.rewrite_front_matter(p,lambda data:data["trigger"].pop("value")); self.assertIn("'value' is a required property",self.errors(d))
    def test_manual_trigger_without_reason(self):
        d=self.copy(); p=d/"obligations/OBL-20260913T152950Z-D4E5F6.md"; self.rewrite_front_matter(p,lambda data:data.__setitem__("trigger",{"type":"manual"})); self.assertIn("reason",self.errors(d))
    def test_invalid_adr_status(self): d=self.copy(); p=d/"decisions/ADR-0001.md"; p.write_text(p.read_text().replace("status: accepted","status: obsolete")); self.assertIn("not one of",self.errors(d))
    def test_missing_adr_heading(self): d=self.copy(); p=d/"decisions/ADR-0001.md"; p.write_text(p.read_text().replace("## Provenance","## Sources")); self.assertIn("missing ADR heading Provenance",self.errors(d))
    def test_bad_jsonl_event(self): d=self.copy(); p=next((d/"ledger/events").glob("*.jsonl")); p.write_text(p.read_text()+"{bad}\n"); self.assertIn("bad JSONL event",self.errors(d))
    def test_duplicate_ledger_event_id(self): d=self.copy(); p=next((d/"ledger/events").glob("*.jsonl")); first=p.read_text().splitlines()[0]; p.write_text(p.read_text()+first+"\n"); self.assertIn("duplicate ledger event ID",self.errors(d))
    def test_index_missing_record(self): d=self.copy(); idx=yaml.safe_load((d/"memory/index.yaml").read_text()); idx["records"].append({"id":"MEM-20260913T010203Z-A1B2C3","file":"missing.md","title":"x","status":"active"}); (d/"memory/index.yaml").write_text(yaml.safe_dump(idx)); self.assertIn("index points to missing record",self.errors(d))
    def test_duplicate_index_id(self): d=self.copy(); self.sample_memory(d); idx=yaml.safe_load((d/"memory/index.yaml").read_text()); idx["records"].append(dict(idx["records"][0])); (d/"memory/index.yaml").write_text(yaml.safe_dump(idx,sort_keys=False)); self.assertIn("duplicate indexed ID",self.errors(d))
    def test_index_file_mismatch(self): d=self.copy(); self.sample_memory(d); q=self.sample_memory(d,"MEM-20260913T010204Z-B1C2D3"); idx=yaml.safe_load((d/"memory/index.yaml").read_text()); idx["records"][0]["file"]=q.name; (d/"memory/index.yaml").write_text(yaml.safe_dump(idx,sort_keys=False)); self.assertIn("indexed file mismatch",self.errors(d))
    def test_unindexed_record(self): d=self.copy(); self.sample_memory(d); (d/"memory/index.yaml").write_text("schema_version: 1\nrecords: []\n"); self.assertIn("unindexed canonical record",self.errors(d))
    def test_invalid_sha(self): d=self.copy(); p=d/"state/repositories.yaml"; p.write_text(p.read_text().replace("f1880847e046425c7f3f3cad22a07d0008aad359","abc")); self.assertIn("does not match",self.errors(d))
    def test_null_remote(self): d=self.copy(); p=d/"state/repositories.yaml"; p.write_text(re.sub(r"remote: https://github.com/JasonHuang3D/qiven-foundation.git","remote: null",p.read_text(),count=1)); self.assertIn("not of type 'string'",self.errors(d))
    def test_invalid_timestamp(self): d=self.copy(); p=d/"state/active-work.yaml"; p.write_text(re.sub(r"updated_at: .+","updated_at: 'not-a-timestamp'",p.read_text())); self.assertIn("invalid timestamp",self.errors(d))
    def test_memory_valid_from_not_null(self): d=self.copy(); p=self.sample_memory(d); p.write_text(p.read_text().replace("valid_from: '2026-09-13T01:02:03Z'","valid_from: null")); self.assertIn("not of type 'string'",self.errors(d))
    def test_sources_not_empty(self): d=self.copy(); p=self.sample_memory(d); p.write_text(p.read_text().replace("sources: [{type: user_statement, reference: test}]","sources: []")); self.assertIn("should be non-empty",self.errors(d))
    def test_broken_internal_relation(self): d=self.copy(); p=self.sample_memory(d); p.write_text(p.read_text().replace("related: []","related: [ADR-9999]")); self.assertIn("broken internal relation",self.errors(d))
    def test_generated_context_is_allowed(self): d=self.copy(); (d/"generated/GLOBAL_CONTEXT.md").write_text("# Derived\n"); self.assertEqual(self.errors(d),"")

if __name__=="__main__":
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ValidatorTests))
    if not result.wasSuccessful(): raise SystemExit(1)
    errors=validate_repository(ROOT)
    if errors: print("Repository validation failed after unit tests:\n"+"\n".join(errors)); raise SystemExit(1)
    print("Unit tests and repository validation PASS")