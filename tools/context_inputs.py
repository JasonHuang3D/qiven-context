"""Shared mandatory input resolution and non-ranked declared constraints."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

import yaml
from jsonschema import Draft202012Validator
from context_snapshot import safe_path

INPUT_MANIFEST = "collaboration/context-inputs.yaml"
CONSTRAINT_MANIFEST = "governance/context-constraints.yaml"


def read_yaml(root: Path, path: str):
    path = safe_path(path)
    target = root / path
    if not target.is_file():
        raise FileNotFoundError(f"missing required Context input: {path}")
    return yaml.safe_load(target.read_text(encoding="utf-8"))


def checked_yaml(root: Path, path: str, schema: str):
    data = read_yaml(root, path)
    validator = Draft202012Validator(json.loads((root / "schema" / schema).read_text(encoding="utf-8")))
    errors = list(validator.iter_errors(data))
    if errors:
        raise ValueError(f"invalid {path}: {errors[0].message}")
    return data


def _declared_constraint_sources(root: Path) -> set[str]:
    target = root / CONSTRAINT_MANIFEST
    if not target.is_file():
        return set()
    try:
        data = yaml.safe_load(target.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError):
        return set()
    if not isinstance(data, dict) or not isinstance(data.get("rules"), list):
        return set()
    result: set[str] = set()
    for rule in data["rules"]:
        if not isinstance(rule, dict) or not isinstance(rule.get("sources"), list):
            continue
        for value in rule["sources"]:
            if isinstance(value, str):
                try:
                    result.add(safe_path(value))
                except ValueError:
                    pass
    return result


def mandatory_paths(root: Path, query: Mapping | None = None) -> tuple[str, ...]:
    query = query or {}
    manifest = checked_yaml(root, INPUT_MANIFEST, "context-inputs.schema.json")
    paths = [INPUT_MANIFEST, *manifest["mandatory"]]
    view_id = query.get("view")
    if view_id:
        if view_id not in manifest["views"]:
            raise ValueError(f"unknown ContextView: {view_id}")
        view_path = manifest["views"][view_id]
        view = read_yaml(root, view_path)
        if (not isinstance(view, dict) or view.get("id") != view_id or view.get("status") != "active"
                or view.get("project_context", {}).get("override_allowed") is not False):
            raise ValueError("ContextView is inactive, mismatched, or permits project override")
        paths.append(view_path)
        environments = view.get("environments", [])
        workflows = view.get("workflows", {})
        if (not isinstance(environments, list) or not all(isinstance(p, str) for p in environments)
                or not isinstance(workflows, dict) or not all(isinstance(p, str) for p in workflows.values())):
            raise ValueError("invalid ContextView references")
        paths.extend(environments)
        paths.extend(workflows.values())
    paths = list(dict.fromkeys(safe_path(path) for path in paths))
    constraint_sources = _declared_constraint_sources(root)
    for path in paths:
        if not (root / path).is_file():
            if path in constraint_sources:
                raise FileNotFoundError(f"missing mandatory Context constraint source: {path}")
            raise FileNotFoundError(f"missing mandatory Context source: {path}")
    return tuple(paths)


def _applicability(when: Mapping, operation: Mapping) -> str:
    unknown = False
    for field, values in when.items():
        actual = operation.get(field)
        if actual is None:
            unknown = True
        elif actual not in values:
            return "not_applicable"
    return "unresolved" if unknown else "applicable"


def resolve_constraints(root: Path, query: Mapping, store: Mapping) -> dict:
    manifest = checked_yaml(root, CONSTRAINT_MANIFEST, "context-constraints.schema.json")
    if len({rule["id"] for rule in manifest["rules"]}) != len(manifest["rules"]):
        raise ValueError("duplicate constraint rule IDs")
    records = {record.path: record for rows in store.values() for record in rows}
    operation = query.get("operation", {})
    result = []
    for rule in manifest["rules"]:
        applicability = _applicability(rule["when"], operation)
        # Unknown applicable scope keeps the rule visible, independently of ranking.
        source_paths = []
        for path in rule["sources"]:
            path = safe_path(path)
            if not (root / path).is_file():
                raise FileNotFoundError(f"missing constraint source: {path}")
            record = records.get(path)
            if record is not None:
                from record_lifecycle import is_current
                if not is_current(record.category, record.status):
                    raise ValueError(f"constraint rule references a non-current record: {path}")
            source_paths.append(path)
        result.append({"id": rule["id"], "effect": rule["effect"],
                       "applicability": applicability,
                       "sources": source_paths if applicability != "not_applicable" else []})
    # Non-terminal before-obligations and explicit memory constraints are also
    # protected from relevance truncation. Scope applicability remains explicit.
    scopes = set(query.get("scopes", []))
    for record in records.values():
        metadata = record.metadata
        from record_lifecycle import is_current
        if not is_current(record.category, record.status):
            continue
        hard_memory = record.category == "memory" and metadata.get("kind") in {"constraint", "invariant", "protocol"}
        before = record.category == "obligations" and metadata.get("trigger", {}).get("type") == "before"
        commitment = record.category == "obligations" and metadata.get("kind") == "commitment"
        if not (hard_memory or before or commitment):
            continue
        record_scopes = set(metadata.get("scope", []))
        if "qiven" in record_scopes or record_scopes & scopes:
            applicability = "applicable"
        else:
            # Scope tags are not a completeness proof: absent overlap is unknown.
            applicability = "unresolved"
        result.append({"id": record.id, "effect": "review_required", "applicability": applicability,
                       "sources": [record.path]})
    return {"scope": "declared-rules-and-record-constraints", "authorization": "not_granted",
            "operation_declared": bool(operation),
            "status": "unresolved" if any(r["applicability"] == "unresolved" for r in result) else "resolved",
            "prohibited": any(r["applicability"] == "applicable" and r["effect"] == "prohibit" for r in result),
            "rules": result}
