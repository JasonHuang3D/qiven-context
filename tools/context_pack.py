from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker

from context_evidence import validate_bound_sources


ROOT = Path(__file__).resolve().parents[1]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_context_pack(pack: Mapping[str, Any], root: Path = ROOT) -> None:
    """Validate a generated pack without relying on remote schema resolution."""
    try:
        validate_bound_sources(pack)
        pack_schema = deepcopy(json.loads(pack["source_contents"]["schema/context-pack.schema.json"]["content"]))
        query_schema = json.loads(pack["source_contents"]["schema/context-query.schema.json"]["content"])
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid snapshot-bound context pack: {exc}") from exc

    # context-pack.schema.json keeps the canonical relative $ref for humans/tools.
    # Runtime validation in Phase 0 stays local and deterministic by inlining the
    # only external schema dependency before constructing the validator.
    pack_schema["properties"]["query"] = query_schema

    errors = sorted(
        Draft202012Validator(pack_schema, format_checker=FormatChecker()).iter_errors(dict(pack)),
        key=lambda item: tuple(str(part) for part in item.absolute_path),
    )
    if errors:
        details = "; ".join(error.message for error in errors)
        raise ValueError(f"invalid generated context pack: {details}")


def _reason_text(item: Mapping[str, Any]) -> str:
    reasons = item.get("reasons", []) or []
    return "; ".join(f"{reason['kind']}={reason['value']}" for reason in reasons)


def _render_source_section(
    title: str,
    items: list[Mapping[str, Any]],
    root: Path,
    *,
    show_trigger: bool = False,
    source_contents: Mapping | None = None,
) -> list[str]:
    lines = [f"## {title}", ""]
    if not items:
        lines.extend(["_No records selected._", ""])
        return lines

    for item in items:
        identity = item.get("id") or item.get("path")
        lines.append(f"### {identity}")
        lines.append("")
        lines.append(f"Source: `{item['path']}`")
        lines.append("")
        reasons = _reason_text(item)
        if reasons:
            lines.append(f"Selection: {reasons}")
            lines.append("")
        if "current_eligible" in item:
            lines.append(f"Lifecycle: status={item['status']}; current_eligible={item['current_eligible']}")
            lines.append("")
        if show_trigger:
            trigger = item["trigger"]
            trigger_value = f" value={trigger['value']}" if "value" in trigger else ""
            lines.append(
                f"Trigger: `{trigger['type']}`{trigger_value} -> **{trigger['result']}** — {trigger['explanation']}"
            )
            lines.append("")
            lines.append(f"Completion: {item['completion']}")
            lines.append("")
        lines.append(source_contents[str(item["path"])]["content"].rstrip())
        lines.extend(["", "---", ""])
    return lines


def render_context_markdown(pack: Mapping[str, Any], root: Path = ROOT) -> str:
    """Render an LLM/human-readable working pack from a validated manifest."""
    root = Path(root)
    validate_context_pack(pack, root)

    query = pack["query"]
    lines = [
        "# Qiven Generated Task Context",
        "",
        "> Derived working context only. Canonical truth remains in the referenced source files.",
        "",
        f"Generated at: `{pack['generated_at']}`",
        f"Snapshot: `{pack['snapshot']['id']}`; commit: `{pack['snapshot']['git_commit']}`",
        "",
        f"Task: {query['task']}",
        f"Record mode: {query.get('record_mode', 'current')}",
        "",
    ]

    selectors = []
    for key in ("topics", "scopes", "touches", "signals", "conditions", "changed", "include_ids"):
        values = query.get(key, []) or []
        if values:
            selectors.append(f"- {key}: {', '.join(f'`{value}`' for value in values)}")
    if selectors:
        lines.extend(["## Query Selectors", "", *selectors, ""])

    lines.extend(_render_source_section("Mandatory Operating Context", list(pack["mandatory_sources"]), root, source_contents=pack["source_contents"]))
    lines.extend(_render_source_section("Project Context", list(pack["projects"]), root, source_contents=pack["source_contents"]))
    lines.extend(_render_source_section("Decisions", list(pack["decisions"]), root, source_contents=pack["source_contents"]))
    lines.extend(_render_source_section("Canonical Memory", list(pack["memory"]), root, source_contents=pack["source_contents"]))
    lines.extend(
        _render_source_section(
            "Obligations (terminal records are inspection only)",
            list(pack["obligations"]),
            root,
            show_trigger=True,
            source_contents=pack["source_contents"],
        )
    )

    lines.extend(["## Protected constraints", "", "Execution authorization: not granted.", ""])
    for rule in pack["constraints"]["rules"]:
        lines.extend([f"### {rule['id']}: {rule['applicability']} / {rule['effect']}", ""])
        for path in rule["sources"]:
            lines.extend([f"Source: `{path}`", "", pack["source_contents"][path]["content"].rstrip(), ""])
    lines.extend(["## Diagnostics", ""])
    diagnostics = pack.get("diagnostics", []) or []
    if diagnostics:
        for diagnostic in diagnostics:
            source = f" [{diagnostic['source']}]" if diagnostic.get("source") else ""
            lines.append(
                f"- **{diagnostic['level']} / {diagnostic['code']}**{source}: {diagnostic['message']}"
            )
    else:
        lines.append("_No diagnostics._")
    lines.append("")

    return "\n".join(lines)


def write_context_pack(
    pack: Mapping[str, Any],
    output_prefix: Path,
    root: Path = ROOT,
) -> tuple[Path, Path]:
    """Write deterministic JSON plus Markdown derived artifacts."""
    root = Path(root)
    validate_context_pack(pack, root)
    prefix = Path(output_prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = prefix.with_suffix(".json")
    markdown_path = prefix.with_suffix(".md")

    json_path.write_text(
        json.dumps(pack, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(render_context_markdown(pack, root), encoding="utf-8")
    return json_path, markdown_path
