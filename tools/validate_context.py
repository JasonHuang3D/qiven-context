from __future__ import annotations
import json, re, sys
from datetime import datetime
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(__file__).resolve().parents[1]
REQUIRED=["README.md","BOOTSTRAP.md","MEMORY-CONSTITUTION.md","state","ledger/events","memory/records","obligations","decisions","projects","sessions","evidence","collaboration","schema","templates","generated","tests/fixtures","tests/cold-boot","tools"]
HEADINGS=["Context","Decision","Alternatives Considered","Consequences","Revisit Conditions","Provenance"]
INTERNAL=re.compile(r"^(?:MEM-\d{8}T\d{6}Z-[A-F0-9]{6}|OBL-\d{8}T\d{6}Z-[A-F0-9]{6}|ADR-\d{4})$")

def front(path):
    text=path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]: raise ValueError("missing front matter")
    raw,body=text[4:].split("\n---\n",1)
    return yaml.safe_load(raw),body
def schema(name): return json.loads((ROOT/"schema"/f"{name}.schema.json").read_text(encoding="utf-8"))
def validate_obj(obj,name,label,errors):
    for e in Draft202012Validator(schema(name),format_checker=FormatChecker()).iter_errors(obj): errors.append(f"{label}: {e.message}")
    timestamp_keys={"created_at","updated_at","observed_at","timestamp","valid_from","valid_until"}
    def check(value,path=""):
        if isinstance(value,dict):
            for key,item in value.items():
                if key in timestamp_keys and item is not None:
                    try:
                        if not isinstance(item,str) or not item.endswith("Z"): raise ValueError
                        datetime.fromisoformat(item[:-1]+"+00:00")
                    except (TypeError,ValueError): errors.append(f"{label}: invalid timestamp at {path+key}")
                check(item,path+key+".")
        elif isinstance(value,list):
            for i,item in enumerate(value): check(item,f"{path}{i}.")
    check(obj)

def validate_repository(root=ROOT):
    global ROOT
    old=ROOT; ROOT=Path(root); errors=[]
    try:
        for p in REQUIRED:
            if not (ROOT/p).exists(): errors.append(f"missing required path: {p}")
        for rel,sch in [("state/repositories.yaml","repositories-state"),("state/active-work.yaml","active-work-state"),("state/roadmap.yaml","roadmap-state")]:
            try: validate_obj(yaml.safe_load((ROOT/rel).read_text(encoding="utf-8")),sch,rel,errors)
            except Exception as e: errors.append(f"{rel}: {e}")
        ids={}; canonical={"memory":{},"obligations":{},"decisions":{}}
        specs=[("memory","memory/records","memory-record"),("obligations","obligations","obligation"),("decisions","decisions","adr")]
        for typ,folder,sch in specs:
            for p in (ROOT/folder).glob("*.md"):
                if p.name=="README.md": continue
                try:
                    data,body=front(p); validate_obj(data,sch,str(p.relative_to(ROOT)),errors); rid=data.get("id","")
                    if typ=="decisions":
                        if not p.name.startswith(rid): errors.append(f"{p.name}: filename/id mismatch")
                        for h in HEADINGS:
                            if not re.search(rf"^## {re.escape(h)}\s*$",body,re.M): errors.append(f"{p.name}: missing ADR heading {h}")
                    elif p.stem!=rid: errors.append(f"{p.name}: filename/id mismatch")
                    if not re.search(r"^# .+",body,re.M): errors.append(f"{p.name}: missing required body title")
                    if rid in ids: errors.append(f"duplicate canonical ID: {rid}")
                    ids[rid]=p; canonical[typ][rid]=p
                except Exception as e: errors.append(f"{p.relative_to(ROOT)}: {e}")
        event_ids=set()
        for p in (ROOT/"ledger/events").glob("*.jsonl"):
            for n,line in enumerate(p.read_text(encoding="utf-8").splitlines(),1):
                if not line.strip(): continue
                try:
                    obj=json.loads(line); validate_obj(obj,"ledger-event",f"{p.name}:{n}",errors); rid=obj.get("id","")
                    if rid in event_ids: errors.append(f"duplicate ledger event ID: {rid}")
                    if rid in ids: errors.append(f"duplicate canonical ID: {rid}")
                    event_ids.add(rid); ids[rid]=p
                except Exception as e: errors.append(f"{p.name}:{n}: bad JSONL event: {e}")
        for typ,index_rel,base in [("memory","memory/index.yaml","memory/records"),("obligations","obligations/index.yaml","obligations"),("decisions","decisions/index.yaml","decisions")]:
            try:
                idx=yaml.safe_load((ROOT/index_rel).read_text(encoding="utf-8")); validate_obj(idx,"index",index_rel,errors)
                indexed_ids=[]; indexed_files=[]
                for x in idx.get("records",[]):
                    rid=x["id"]; rel_file=x["file"]
                    if rid in indexed_ids: errors.append(f"{index_rel}: duplicate indexed ID {rid}")
                    if rel_file in indexed_files: errors.append(f"{index_rel}: duplicate indexed file {rel_file}")
                    indexed_ids.append(rid); indexed_files.append(rel_file)
                    target=ROOT/base/rel_file
                    if not target.is_file():
                        errors.append(f"{index_rel}: index points to missing record {rid}")
                        continue
                    expected=canonical[typ].get(rid)
                    if expected is None:
                        errors.append(f"{index_rel}: indexed ID has no canonical record {rid}")
                        continue
                    if target.resolve()!=expected.resolve():
                        errors.append(f"{index_rel}: indexed file mismatch for {rid}")
                    try:
                        data,_=front(expected)
                        if x.get("title")!=data.get("title"): errors.append(f"{index_rel}: stale title for {rid}")
                        if x.get("status")!=data.get("status"): errors.append(f"{index_rel}: stale status for {rid}")
                    except Exception:
                        pass
                indexed=set(indexed_ids)
                for rid in canonical[typ]:
                    if rid not in indexed: errors.append(f"{index_rel}: unindexed canonical record {rid}")
            except Exception as e: errors.append(f"{index_rel}: {e}")
        known=set(ids)
        for groups in canonical.values():
            for rid,p in groups.items():
                try: data,_=front(p)
                except Exception: continue
                for field in ("related","supersedes","superseded_by"):
                    for ref in data.get(field,[]) or []:
                        if INTERNAL.match(str(ref)) and ref not in known: errors.append(f"{p.name}: broken internal relation {ref}")
        return errors
    finally: ROOT=old

if __name__=="__main__":
    failures=validate_repository()
    if failures:
        print("VALIDATION FAILED")
        for x in failures: print(f"- {x}")
        sys.exit(1)
    print("Context repository validation PASS")
