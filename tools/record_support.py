"""Survivor support for canonical record validation.

Extracted 2026-09-21 from the sealed context-kernel family
(context_inputs.py, lifecycle_graph.py; ADR-0040/ADR-0041) so the
repository validator stays self-contained. Keep this module minimal:
it exists only for validate_context.py and test.py.
"""
from __future__ import annotations

from pathlib import Path
from typing import Mapping

import json
import yaml
from jsonschema import Draft202012Validator

INPUT_MANIFEST = "collaboration/context-inputs.yaml"


def safe_path(path: str) -> str:
    from pathlib import PurePosixPath
    value = PurePosixPath(path)
    if not path or value.is_absolute() or ".." in value.parts or "\\" in path or ":" in path:
        raise ValueError(f"unsafe Context source path: {path!r}")
    return value.as_posix()


def read_yaml(root: Path, path: str):
    data = yaml.safe_load((root / path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a mapping")
    return data


def checked_yaml(root: Path, path: str, schema: str):
    data = read_yaml(root, path)
    validator = Draft202012Validator(json.loads((root / "schema" / schema).read_text(encoding="utf-8")))
    errors = list(validator.iter_errors(data))
    if errors:
        raise ValueError(f"invalid {path}: {errors[0].message}")
    return data


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
    for path in paths:
        if not (root / path).is_file():
            raise FileNotFoundError(f"missing mandatory Context source: {path}")
    return tuple(paths)


def lifecycle_errors(records):
    """Total, iterative validation of the canonical replacement graph.

    (copied unchanged from the sealed lifecycle_graph.py at seal time)
    """
    errors = []
    graph = {}
    relations = {}
    for rid, data in records.items():
        relations[rid] = {}
        for field in ("related", "supersedes", "superseded_by"):
            values = data.get(field, [])
            if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
                errors.append(f"{rid}: {field} must be a list of record IDs")
                values = []
            if field != "related" and len(values) != len(set(values)):
                errors.append(f"{rid}: duplicate {field} relation")
            relations[rid][field] = values
        successors = relations[rid]["superseded_by"]
        if data.get("status") == "superseded" and not successors:
            errors.append(f"{rid}: superseded record requires superseded_by provenance")
        if data.get("status") != "superseded" and successors:
            errors.append(f"{rid}: only superseded records may declare superseded_by")
        graph[rid] = relations[rid]["supersedes"]
    for rid, fields in relations.items():
        for field, values in fields.items():
            for ref in values:
                if ref not in records:
                    errors.append(f"{rid}: broken internal relation {field} -> {ref}")
                    continue
                if field == "related":
                    continue
                if rid == ref:
                    errors.append(f"{rid}: self supersession is forbidden")
                reciprocal = "superseded_by" if field == "supersedes" else "supersedes"
                if rid not in relations[ref][reciprocal]:
                    errors.append(f"{rid}: non-reciprocal {field} relation {rid} -> {ref}")
                if field == "supersedes" and records[ref].get("status") != "superseded":
                    errors.append(f"{rid}: supersedes target {ref} is not superseded")
    colors = {}
    for root in sorted(graph):
        if colors.get(root):
            continue
        colors[root] = 1
        stack = [(root, iter(graph[root]))]
        while stack:
            rid, children = stack[-1]
            ref = next(children, None)
            if ref is None:
                colors[rid] = 2
                stack.pop()
            elif ref in graph:
                if colors.get(ref) == 1:
                    errors.append(f"supersession cycle: {rid} -> {ref}")
                elif not colors.get(ref):
                    colors[ref] = 1
                    stack.append((ref, iter(graph[ref])))
    return errors
