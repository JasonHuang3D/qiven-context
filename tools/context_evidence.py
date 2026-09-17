"""Lossless record evidence and whole-record budgeting, separate from rank text."""
from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime
from typing import Mapping

from context_snapshot import canonical_json, verify_evidence


def json_value(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: json_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_value(v) for v in value]
    return deepcopy(value)


def record_evidence(record, snapshot) -> dict:
    import yaml
    raw = snapshot.text(record.path).replace("\r\n", "\n")
    if not raw.startswith("---\n"):
        raise ValueError(f"record has no bound front matter: {record.path}")
    front, body = raw[4:].split("\n---\n", 1)
    if json_value(yaml.safe_load(front)) != json_value(record.metadata) or body != record.body:
        raise ValueError(f"record does not belong to supplied snapshot: {record.path}")
    return {"category": record.category, "metadata": json_value(record.metadata),
            "body": record.body, "source": snapshot.evidence(record.path)}


def attach_sources(pack: dict, snapshot) -> None:
    paths = {r["path"] for section in ("mandatory_sources", "projects", "decisions", "memory", "obligations", "candidates")
             for r in pack.get(section, [])}
    paths.update({"schema/context-pack.schema.json", "schema/context-query.schema.json"})
    for rule in pack["constraints"]["rules"]:
        paths.update(rule["sources"])
    pack["source_contents"] = {p: snapshot.evidence(p) for p in sorted(paths)}


def apply_pack_budget(pack: dict, snapshot) -> None:
    """Budget serialized UTF-8 bytes, not guessed tokenizer-specific token counts."""
    budget = pack["query"].get("max_context_bytes")
    protected = set(pack["query"]["include_ids"])
    pack["budget"] = {"limit_bytes": budget, "omitted": []}
    attach_sources(pack, snapshot)
    if budget is None:
        return
    # Keep mandatory sources, constraints and explicit IDs intact. Drop whole
    # optional records in deterministic tail order; never truncate evidence.
    optional = [(section, r) for section in ("projects", "decisions", "memory", "obligations")
                for r in pack[section] if r.get("id") not in protected]
    while len(canonical_json(pack)) > budget and optional:
        section, row = optional.pop()
        pack[section].remove(row)
        pack["budget"]["omitted"].append(row.get("id", row["path"]))
        attach_sources(pack, snapshot)
    if len(canonical_json(pack)) > budget:
        raise ValueError("Context byte budget cannot contain protected inputs, constraints and explicit evidence")


def validate_bound_sources(pack: Mapping) -> None:
    verify_evidence(pack["snapshot"], pack["source_contents"])
    for section in ("mandatory_sources", "projects", "decisions", "memory", "obligations", "candidates"):
        for row in pack.get(section, []):
            path = row["path"]
            if path not in pack["source_contents"]:
                raise ValueError(f"selected source missing from snapshot payload: {path}")
            if "id" in row:
                evidence = row["evidence"]
                import yaml
                raw = evidence["source"]["content"].replace("\r\n", "\n")
                front, body = raw[4:].split("\n---\n", 1)
                if (json_value(yaml.safe_load(front)) != evidence["metadata"] or body != evidence["body"]
                        or row["id"] != evidence["metadata"]["id"]
                        or row["status"] != evidence["metadata"]["status"]):
                    raise ValueError(f"record interpretation differs from bound source: {path}")
                if evidence["source"] != pack["source_contents"][path]:
                    raise ValueError(f"record evidence does not match bound source: {path}")
    for rule in pack["constraints"]["rules"]:
        for path in rule["sources"]:
            if path not in pack["source_contents"]:
                raise ValueError(f"protected constraint source missing: {path}")
