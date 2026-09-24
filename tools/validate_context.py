from __future__ import annotations
import json, re, sys
from datetime import datetime
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(__file__).resolve().parents[1]
REQUIRED=["README.md","BOOTSTRAP.md","MEMORY-CONSTITUTION.md","governance/authority.yaml","state","memory/records","obligations","decisions","projects","sessions","evidence/audits","legacy","legacy/tools","legacy/ledger/events","legacy/evidence/ci","legacy/evidence/handoffs","legacy/evidence/research","legacy/sessions","collaboration","collaboration/project-continuity-acceptance.md","collaboration/human-succession-acceptance.md","schema","templates","tests/fixtures","tests/cold-boot","tools","runtime/invocation-policy.yaml"]
HEADINGS=["Context","Decision","Alternatives Considered","Consequences","Revisit Conditions","Provenance"]
SESSION_HEADINGS=["Session identity","Exact current task","Accepted refs and evidence","Unaccepted candidate refs","Pending asynchronous work","Known inconsistencies and evidence gaps","Next action"]
INTERNAL=re.compile(r"^(?:MEM-\d{8}T\d{6}Z-[A-F0-9]{6}|OBL-\d{8}T\d{6}Z-[A-F0-9]{6}|ADR-\d{4})$")
SESSION_RE=re.compile(r"^\d{4}-\d{2}-\d{2}-qiven-v\d+\.md$")
LEGACY_LEDGER={"2026-09-13.jsonl","2026-09-14.jsonl"}
DEPRECATED_EVIDENCE=("legacy/evidence/ci","legacy/evidence/handoffs","legacy/evidence/research")

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

    event_dir=ROOT/"legacy/ledger/events"
    if event_dir.is_dir():
        actual={p.name for p in event_dir.glob("*.jsonl")}
        new=actual-LEGACY_LEDGER
        if new: errors.append(f"legacy/ledger/events: the museum forbids new manual ledger files: {', '.join(sorted(new))}")
    ledger_readme=ROOT/"legacy/ledger/README.md"
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
        from record_support import checked_yaml, mandatory_paths
        declaration = checked_yaml(ROOT, "collaboration/context-inputs.yaml", "context-inputs.schema.json")
        mandatory_paths(ROOT)
        for view in declaration["views"]:
            mandatory_paths(ROOT, {"view": view})
        checked_yaml(ROOT, "governance/context-constraints.yaml", "context-constraints.schema.json")
        # manifest completeness: every binding file must be declared (audit B2 - a
        # view missing from the manifest was never schema-validated)
        declared = set(declaration.get("views", {}).values())
        for binding in sorted((ROOT/"views"/"bindings").glob("*.yaml")):
            rel = binding.relative_to(ROOT).as_posix()
            if rel not in declared:
                errors.append(f"views manifest: {rel} exists but is not declared in collaboration/context-inputs.yaml")
        for rel in sorted(declared):
            if not (ROOT/rel).exists():
                errors.append(f"views manifest: declared view {rel} does not exist")
    except Exception as exc:
        errors.append(f"Context input declaration: {exc}")

    # duplicate section headings inside one active contract (audit A1 - a
    # divergent duplicate section survived because no detector existed)
    for contract in sorted((ROOT/"collaboration").glob("*.md")):
        seen = {}
        for num, line in enumerate(contract.read_text(encoding="utf-8").splitlines(), 1):
            if line.startswith("## "):
                heading = line[3:].strip()
                if heading in seen:
                    errors.append(f"{contract.relative_to(ROOT).as_posix()}: duplicate section heading '{heading}' (lines {seen[heading]} and {num})")
                else:
                    seen[heading] = num

    boot=(ROOT/"BOOTSTRAP.md").read_text(encoding="utf-8") if (ROOT/"BOOTSTRAP.md").is_file() else ""
    for required in ("governance/authority.yaml","collaboration/context-operating-model.md","state/repositories.yaml"):
        if required not in boot: errors.append(f"BOOTSTRAP.md: missing v2 mandatory source {required}")
    for legacy in ("legacy/evidence/ci","legacy/evidence/handoffs","legacy/evidence/research"):
        if legacy in boot: errors.append(f"BOOTSTRAP.md: deprecated source must not be an active bootstrap input: {legacy}")

# runtime/invocation-policy.yaml is the machine instance of the frozen
# v4 InvocationPolicy (ADR-0047 section 7.3): the rule table is pinned to
# this mirror of the draft's default_invocation_policy() (qiven-context-draft
# pin 7583724) so the human-readable specification and the machine file
# cannot silently diverge. A deliberate rule change updates BOTH the spec
# and this mirror in one reviewable delta.
POLICY_VOCAB={
    "action":{"BeginTask","EnterDomain","CreateCppSymbol","IntroducePrimitive","ModifyArchitecture","ModifyPublicAPI","InvokeTool","RetryFailure","MakeCanonicalClaim","MakeLiveClaim","ModifyReferencedContract","Commit","Publish","AcceptCandidate"},
    "requirement":{"MandatoryRecall","SearchLowerLayer","VerifyCanonical","VerifyLive","InspectToolContract","InspectKnownPit","RunMechanicalCheck","RequestReview","AskHuman"},
    "boundary":{"BeforeJudgment","BeforeExecution"},
    "claim":{"LocalRecall","CanonicalFact","LiveFact","EvidenceInterpretation","Judgment"},
}
POLICY_DEFAULT_RULES=[
    ("CreateCppSymbol","MandatoryRecall","BeforeJudgment","naming policy"),
    ("IntroducePrimitive","SearchLowerLayer","BeforeJudgment","eligible lower layers"),
    ("InvokeTool","InspectToolContract","BeforeExecution","declared tool argv contract"),
    ("RetryFailure","InspectKnownPit","BeforeJudgment","failure fingerprint"),
    ("MakeCanonicalClaim","VerifyCanonical","BeforeJudgment","canonical record"),
    ("MakeLiveClaim","VerifyLive","BeforeJudgment","live source"),
    ("ModifyReferencedContract","MandatoryRecall","BeforeJudgment","reference integrity sweep (P-52)"),
    ("Commit","RunMechanicalCheck","BeforeExecution","attribution subject-position lint (P-51)"),
    ("Publish","RunMechanicalCheck","BeforeExecution","full default gate PASS receipt at exact head (P-53)"),
    ("Publish","RequestReview","BeforeExecution","H2 exact-delta review"),
    ("AcceptCandidate","RequestReview","BeforeExecution","content-bound H2 evidence"),
]

def _invocation_policy_invariants(errors):
    path=ROOT/"runtime/invocation-policy.yaml"
    try:
        data=yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as e:
        errors.append(f"runtime/invocation-policy.yaml: {e}"); return
    if data.get("schema")!="qiven-invocation-policy-v1":
        errors.append("runtime/invocation-policy.yaml: schema must be qiven-invocation-policy-v1"); return
    policy=data.get("policy") or {}
    if policy.get("present") is not True:
        errors.append("runtime/invocation-policy.yaml: policy.present must be true (World B fail-closed state must not be the shipped instance)")
    rules=policy.get("rules") or []
    rows=[]
    for i,rule in enumerate(rules):
        for field,vocab in POLICY_VOCAB.items():
            if field in rule and rule[field] not in vocab:
                errors.append(f"runtime/invocation-policy.yaml: rules[{i}].{field}={rule[field]!r} is outside the frozen v4 vocabulary")
        if not isinstance(rule.get("subject"),str) or not rule.get("subject"):
            errors.append(f"runtime/invocation-policy.yaml: rules[{i}].subject must be a non-empty string")
        if not isinstance(rule.get("blocking"),bool):
            errors.append(f"runtime/invocation-policy.yaml: rules[{i}].blocking must be boolean")
        rows.append((rule.get("action"),rule.get("requirement"),rule.get("boundary"),rule.get("subject")))
    if rows!=POLICY_DEFAULT_RULES:
        errors.append("runtime/invocation-policy.yaml: rule table diverges from the pinned v4 default_invocation_policy mirror (update spec+mirror together)")
    kinds=[r.get("requirement") for r in rules]
    resolvers=data.get("resolvers") or []
    seen=set()
    for i,r in enumerate(resolvers):
        kind=r.get("requirement")
        if kind not in POLICY_VOCAB["requirement"]:
            errors.append(f"runtime/invocation-policy.yaml: resolvers[{i}].requirement={kind!r} outside the v4 vocabulary")
        if kind in seen:
            errors.append(f"runtime/invocation-policy.yaml: duplicate resolver for {kind}")
        seen.add(kind)
        if not isinstance(r.get("type"),str) or not r.get("type"):
            errors.append(f"runtime/invocation-policy.yaml: resolvers[{i}].type must be a non-empty string")
        if not isinstance(r.get("min_version"),int) or r.get("min_version",0)<1:
            errors.append(f"runtime/invocation-policy.yaml: resolvers[{i}].min_version must be an integer >= 1")
    missing=set(kinds)-seen
    if missing:
        errors.append(f"runtime/invocation-policy.yaml: rule kinds without a resolver: {', '.join(sorted(missing))}")
    fresh=data.get("freshness") or {}
    for key in ("evidence_ttl_ms","bundle_freshness_ms"):
        if not isinstance(fresh.get(key),int) or fresh.get(key,0)<=0:
            errors.append(f"runtime/invocation-policy.yaml: freshness.{key} must be a positive integer")
    enf=data.get("enforcement") or {}
    if enf.get("unsatisfied_before_judgment") not in ("deny","redeliberate"):
        errors.append("runtime/invocation-policy.yaml: enforcement.unsatisfied_before_judgment must be deny or redeliberate")
    if enf.get("unsatisfied_before_execution")!="deny":
        errors.append("runtime/invocation-policy.yaml: enforcement.unsatisfied_before_execution must be deny")


def validate_repository(root=ROOT):
    global ROOT
    old=ROOT; ROOT=Path(root); errors=[]
    try:
        for p in REQUIRED:
            if not (ROOT/p).exists(): errors.append(f"missing required path: {p}")
        for forbidden in ("generated",):
            if (ROOT/forbidden).is_dir(): errors.append(f"forbidden generated directory: {forbidden} (only .generated-temp is allowed; ADR-0042)")
        for rel,sch in [("governance/authority.yaml","governance-state"),("state/repositories.yaml","repositories-state"),("state/active-work.yaml","active-work-state"),("state/roadmap.yaml","roadmap-state")]:
            try: validate_obj(yaml.safe_load((ROOT/rel).read_text(encoding="utf-8")),sch,rel,errors)
            except Exception as e: errors.append(f"{rel}: {e}")

        ids={}; canonical={"memory":{},"obligations":{},"decisions":{}}; record_data={}
        specs=[("memory","memory/records","memory-record"),("obligations","obligations","obligation"),("decisions","decisions","adr")]
        for typ,folder,sch in specs:
            record_paths=list((ROOT/folder).glob("*.md"))
            if typ in ("decisions","obligations"):
                # archived records remain indexed canonical records with
                # terminal lifecycle (legacy/ museum, ADR-0039/0042 policy)
                record_paths+=list((ROOT/folder/"legacy").glob("*.md"))
            for p in record_paths:
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
        for p in (ROOT/"legacy/ledger/events").glob("*.jsonl"):
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

        from record_support import lifecycle_errors
        errors.extend(lifecycle_errors(record_data))

        _operating_invariants(errors)
        _invocation_policy_invariants(errors)
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
