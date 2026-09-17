from __future__ import annotations
import json, re, sys
from datetime import datetime
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(__file__).resolve().parents[1]
REQUIRED=["README.md","BOOTSTRAP.md","MEMORY-CONSTITUTION.md","governance/authority.yaml","state","ledger/events","memory/records","obligations","decisions","projects","sessions","sessions/legacy","evidence/audits","evidence/ci","evidence/handoffs","evidence/research","collaboration","collaboration/project-continuity-acceptance.md","collaboration/human-succession-acceptance.md","schema","templates","generated","tests/fixtures","tests/cold-boot","tools"]
HEADINGS=["Context","Decision","Alternatives Considered","Consequences","Revisit Conditions","Provenance"]
SESSION_HEADINGS=["Session identity","Exact current task","Accepted refs and evidence","Unaccepted candidate refs","Pending asynchronous work","Known inconsistencies and evidence gaps","Next action"]
INTERNAL=re.compile(r"^(?:MEM-\d{8}T\d{6}Z-[A-F0-9]{6}|OBL-\d{8}T\d{6}Z-[A-F0-9]{6}|ADR-\d{4})$")
SESSION_RE=re.compile(r"^\d{4}-\d{2}-\d{2}-qiven-v\d+\.md$")
LEGACY_LEDGER={"2026-09-13.jsonl","2026-09-14.jsonl"}
DEPRECATED_EVIDENCE=("evidence/ci","evidence/handoffs","evidence/research")

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

def _operating_invariants(errors):
    readme=(ROOT/"README.md").read_text(encoding="utf-8") if (ROOT/"README.md").is_file() else ""
    if "Genesis historical import has **not** happened" in readme or "This repository is currently **Phase" in readme:
        errors.append("README.md: mutable phase/genesis state is forbidden in timeless README")

    for p in (ROOT/"collaboration").glob("v*-handoff.md"):
        errors.append(f"{p.relative_to(ROOT)}: session handoff is forbidden under normative collaboration/")

    for rel in DEPRECATED_EVIDENCE:
        folder=ROOT/rel
        if not folder.is_dir(): continue
        extras=[p.name for p in folder.iterdir() if p.name!="README.md"]
        if extras: errors.append(f"{rel}: deprecated active bucket contains non-README records: {', '.join(sorted(extras))}")
        readme_path=folder/"README.md"
        if readme_path.is_file() and "deprecated legacy" not in readme_path.read_text(encoding="utf-8").lower():
            errors.append(f"{rel}/README.md: missing explicit deprecated legacy status")

    event_dir=ROOT/"ledger/events"
    if event_dir.is_dir():
        actual={p.name for p in event_dir.glob("*.jsonl")}
        new=actual-LEGACY_LEDGER
        if new: errors.append(f"ledger/events: Context v2 forbids new manual ledger files: {', '.join(sorted(new))}")
    ledger_readme=ROOT/"ledger/README.md"
    if not ledger_readme.is_file() or "frozen legacy" not in ledger_readme.read_text(encoding="utf-8").lower():
        errors.append("ledger/README.md: legacy ledger must be explicitly frozen")

    repo_path=ROOT/"state/repositories.yaml"
    if repo_path.is_file():
        data=yaml.safe_load(repo_path.read_text(encoding="utf-8")) or {}
        forbidden={"main_sha","observed_at","authority","head_sha","ci_status"}
        for item in data.get("repositories",[]) or []:
            bad=forbidden.intersection(item or {})
            if bad: errors.append(f"state/repositories.yaml: live-state cache keys forbidden for {item.get('name','?')}: {', '.join(sorted(bad))}")

    sessions=[p for p in (ROOT/"sessions").glob("*.md") if SESSION_RE.match(p.name)]
    if not sessions:
        errors.append("sessions: at least one v2 active session checkpoint is required")
    else:
        latest=max(sessions,key=lambda p:(p.name[:10],int(re.search(r"-v(\d+)\.md$",p.name).group(1))))
        body=latest.read_text(encoding="utf-8")
        for h in SESSION_HEADINGS:
            if not re.search(rf"^## {re.escape(h)}\s*$",body,re.M): errors.append(f"{latest.relative_to(ROOT)}: missing session heading {h}")

    try:
        from context_inputs import checked_yaml, mandatory_paths
        declaration = checked_yaml(ROOT, "collaboration/context-inputs.yaml", "context-inputs.schema.json")
        mandatory_paths(ROOT)
        for view in declaration["views"]:
            mandatory_paths(ROOT, {"view": view})
        checked_yaml(ROOT, "governance/context-constraints.yaml", "context-constraints.schema.json")
    except Exception as exc:
        errors.append(f"Context input declaration: {exc}")

    boot=(ROOT/"BOOTSTRAP.md").read_text(encoding="utf-8") if (ROOT/"BOOTSTRAP.md").is_file() else ""
    for required in ("governance/authority.yaml","collaboration/context-operating-model.md","state/repositories.yaml"):
        if required not in boot: errors.append(f"BOOTSTRAP.md: missing v2 mandatory source {required}")
    for legacy in ("evidence/ci","evidence/handoffs","evidence/research"):
        if legacy in boot: errors.append(f"BOOTSTRAP.md: deprecated source must not be an active bootstrap input: {legacy}")

def validate_repository(root=ROOT):
    global ROOT
    old=ROOT; ROOT=Path(root); errors=[]
    try:
        for p in REQUIRED:
            if not (ROOT/p).exists(): errors.append(f"missing required path: {p}")
        for rel,sch in [("governance/authority.yaml","governance-state"),("state/repositories.yaml","repositories-state"),("state/active-work.yaml","active-work-state"),("state/roadmap.yaml","roadmap-state")]:
            try: validate_obj(yaml.safe_load((ROOT/rel).read_text(encoding="utf-8")),sch,rel,errors)
            except Exception as e: errors.append(f"{rel}: {e}")

        ids={}; canonical={"memory":{},"obligations":{},"decisions":{}}; record_data={}
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
                    ids[rid]=p; canonical[typ][rid]=p; record_data[rid]=data
                    if data.get("status")=="superseded" and not (data.get("superseded_by") or []):
                        errors.append(f"{p.relative_to(ROOT)}: superseded record requires superseded_by provenance")
                    if data.get("status")!="superseded" and (data.get("superseded_by") or []):
                        errors.append(f"{p.relative_to(ROOT)}: only superseded records may declare superseded_by")
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
                    if not target.is_file(): errors.append(f"{index_rel}: index points to missing record {rid}"); continue
                    expected=canonical[typ].get(rid)
                    if expected is None: errors.append(f"{index_rel}: indexed ID has no canonical record {rid}"); continue
                    if target.resolve()!=expected.resolve(): errors.append(f"{index_rel}: indexed file mismatch for {rid}")
                    try:
                        data,_=front(expected)
                        if x.get("title")!=data.get("title"): errors.append(f"{index_rel}: stale title for {rid}")
                        if x.get("status")!=data.get("status"): errors.append(f"{index_rel}: stale status for {rid}")
                    except Exception: pass
                indexed=set(indexed_ids)
                for rid in canonical[typ]:
                    if rid not in indexed: errors.append(f"{index_rel}: unindexed canonical record {rid}")
            except Exception as e: errors.append(f"{index_rel}: {e}")

        known=set(ids)
        for groups in canonical.values():
            for rid,p in groups.items():
                data=record_data.get(rid)
                if data is None: continue
                for field in ("related","supersedes","superseded_by"):
                    for ref in data.get(field,[]) or []:
                        if INTERNAL.match(str(ref)) and str(ref) not in known: errors.append(f"{p.relative_to(ROOT)}: broken internal relation {field} -> {ref}")
                        if field not in {"supersedes","superseded_by"} or ref not in record_data: continue
                        if ref==rid:
                            errors.append(f"{p.relative_to(ROOT)}: self supersession is forbidden")
                            continue
                        reciprocal="superseded_by" if field=="supersedes" else "supersedes"
                        if rid not in (record_data[ref].get(reciprocal) or []):
                            errors.append(f"{p.relative_to(ROOT)}: non-reciprocal {field} relation {rid} -> {ref}")
                        if field=="supersedes" and record_data[ref].get("status")!="superseded":
                            errors.append(f"{p.relative_to(ROOT)}: supersedes target {ref} is not superseded")

        graph={rid:list(data.get("supersedes") or []) for rid,data in record_data.items()}
        visiting=set(); visited=set(); path=[]
        def visit(rid):
            if rid in visiting:
                start=path.index(rid)
                errors.append(f"supersession cycle: {' -> '.join(path[start:]+[rid])}")
                return
            if rid in visited: return
            visiting.add(rid); path.append(rid)
            for ref in graph.get(rid,[]):
                if ref in graph: visit(ref)
            path.pop(); visiting.remove(rid); visited.add(rid)
        for rid in sorted(graph): visit(rid)

        _operating_invariants(errors)
        return errors
    finally:
        ROOT=old

def main():
    errors=validate_repository(ROOT)
    if errors:
        print("Context validation FAILED")
        for e in errors: print(" -",e)
        return 1
    print("Context validation PASS")
    return 0

if __name__=="__main__": sys.exit(main())
