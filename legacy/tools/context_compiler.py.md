# [SEALED] tools/context_compiler.py

> Museum piece (ADR-0040/ADR-0041, sealed 2026-09-21). Original
> location: `tools/context_compiler.py`. Do not execute — this is historical text
> only; the `.md` extension makes accidental execution impossible.

````python
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import unicodedata
from typing import Any, Iterable, Mapping

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from record_lifecycle import CURRENT_STATUSES, is_current, lifecycle_fields, record_is_eligible
from context_snapshot import SourceSnapshot, as_snapshot
from context_inputs import mandatory_paths, resolve_constraints
from context_evidence import record_evidence, apply_pack_budget


ROOT = Path(__file__).resolve().parents[1]
CATEGORY_LAYOUT = {
    "decisions": ("decisions/index.yaml", "decisions"),
    "memory": ("memory/index.yaml", "memory/records"),
    "obligations": ("obligations/index.yaml", "obligations"),
}
NON_TERMINAL_OBLIGATION_STATUSES = CURRENT_STATUSES["obligations"]
TOKEN_RE = re.compile(r"[^\W_]+(?:-[^\W_]+)*", re.UNICODE)
ALTERNATIVE_RE = re.compile(r"\s+(?:or|或)\s+|\s*\|\s*", re.IGNORECASE)
SELECTION_THRESHOLD = 20
GENERIC_TERMS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "be",
        "by",
        "change",
        "context",
        "design",
        "for",
        "from",
        "implement",
        "implementation",
        "in",
        "is",
        "of",
        "on",
        "or",
        "project",
        "qiven",
        "review",
        "the",
        "to",
        "update",
        "with",
    }
)


@dataclass(frozen=True)
class SourceDocument:
    path: str
    text: str


@dataclass(frozen=True)
class CanonicalRecord:
    category: str
    id: str
    path: str
    title: str
    status: str
    metadata: dict[str, Any]
    body: str


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_front_matter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError(f"{path}: missing front matter")
    raw, body = text[4:].split("\n---\n", 1)
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: front matter must be a mapping")
    return data, body


def validate_query(query: Mapping[str, Any], root: Path = ROOT) -> None:
    schema = json.loads(root.text("schema/context-query.schema.json")) if isinstance(root, SourceSnapshot) else _read_json(Path(root) / "schema/context-query.schema.json")
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(dict(query)),
        key=lambda item: tuple(str(x) for x in item.absolute_path),
    )
    if errors:
        details = "; ".join(error.message for error in errors)
        raise ValueError(f"invalid context query: {details}")


def prepare_query(query: Mapping[str, Any], root: Path = ROOT) -> dict[str, Any]:
    validate_query(query, root)
    prepared: dict[str, Any] = {"task": str(query["task"]).strip(), "record_mode": query.get("record_mode", "current")}
    for key in ("topics", "scopes", "touches", "signals", "conditions", "changed", "include_ids", "negative_conditions", "complete_inputs"):
        prepared[key] = list(query.get(key, []))
    for key in ("now", "view", "operation", "input_evidence", "max_context_bytes"):
        if key in query:
            from copy import deepcopy
            prepared[key] = deepcopy(query[key])
    for field in prepared["complete_inputs"]:
        if not prepared.get("input_evidence", {}).get(field):
            raise ValueError(f"complete_inputs requires an evidence reference for {field}")
    return prepared


def normalize_tokens(values: str | Iterable[str]) -> tuple[str, ...]:
    if isinstance(values, str):
        values = (values,)
    result: list[str] = []
    seen: set[str] = set()

    def add(token: str) -> None:
        token = token.casefold()
        if token and token not in seen:
            seen.add(token)
            result.append(token)

    for value in values:
        normalized = unicodedata.normalize("NFKC", str(value))
        for raw in TOKEN_RE.findall(normalized):
            token = raw.casefold()
            add(token)
            if "-" in token:
                for component in token.split("-"):
                    add(component)
    return tuple(result)


def query_terms(query: Mapping[str, Any]) -> tuple[str, ...]:
    values: list[str] = [str(query.get("task", ""))]
    for key in ("topics", "scopes", "touches"):
        values.extend(str(item) for item in query.get(key, []) or [])
    return normalize_tokens(values)


def load_mandatory_sources(root: Path = ROOT, query: Mapping[str, Any] | None = None) -> tuple[SourceDocument, ...]:
    root = Path(root)
    documents: list[SourceDocument] = []
    for relative in mandatory_paths(root, query):
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(f"missing mandatory context source: {relative}")
        documents.append(SourceDocument(relative, path.read_text(encoding="utf-8")))
    return tuple(documents)


def load_project_documents(root: Path = ROOT) -> tuple[SourceDocument, ...]:
    root = Path(root)
    documents: list[SourceDocument] = []
    for path in sorted((root / "projects").glob("*/README.md"), key=lambda item: item.as_posix()):
        documents.append(SourceDocument(path.relative_to(root).as_posix(), path.read_text(encoding="utf-8")))
    return tuple(documents)


def load_indexed_records(category: str, root: Path = ROOT) -> tuple[CanonicalRecord, ...]:
    if category not in CATEGORY_LAYOUT:
        raise ValueError(f"unsupported canonical category: {category}")
    root = Path(root)
    index_rel, folder_rel = CATEGORY_LAYOUT[category]
    index = yaml.safe_load((root / index_rel).read_text(encoding="utf-8")) or {}
    records: list[CanonicalRecord] = []
    for entry in sorted(index.get("records", []), key=lambda item: item["id"]):
        path = root / folder_rel / entry["file"]
        metadata, body = read_front_matter(path)
        if metadata.get("id") != entry.get("id"):
            raise ValueError(f"{index_rel}: indexed ID mismatch for {entry.get('id')}")
        if metadata.get("title") != entry.get("title"):
            raise ValueError(f"{index_rel}: stale title for {entry.get('id')}")
        if metadata.get("status") != entry.get("status"):
            raise ValueError(f"{index_rel}: stale status for {entry.get('id')}")
        records.append(
            CanonicalRecord(
                category=category,
                id=str(metadata["id"]),
                path=path.relative_to(root).as_posix(),
                title=str(metadata["title"]),
                status=str(metadata["status"]),
                metadata=metadata,
                body=body,
            )
        )
    return tuple(records)


def load_canonical_store(root: Path = ROOT) -> dict[str, tuple[CanonicalRecord, ...]]:
    return {category: load_indexed_records(category, root) for category in CATEGORY_LAYOUT}


def non_terminal_obligations(records: Iterable[CanonicalRecord]) -> tuple[CanonicalRecord, ...]:
    return tuple(
        sorted(
            (record for record in records if record.status in NON_TERMINAL_OBLIGATION_STATUSES),
            key=lambda record: record.id,
        )
    )


def _canonical_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def _split_alternatives(value: str) -> tuple[str, ...]:
    parts = tuple(part.strip() for part in ALTERNATIVE_RE.split(value) if part.strip())
    return parts or (value.strip(),)


def _lexical_match(pattern: str, candidate: str) -> bool:
    if not pattern or not candidate:
        return False
    if _canonical_text(pattern) == _canonical_text(candidate):
        return True
    pattern_tokens = set(normalize_tokens(pattern))
    candidate_tokens = set(normalize_tokens(candidate))
    if not pattern_tokens or not candidate_tokens:
        return False
    # Trigger matching is directional: the trigger target must be fully present
    # in the candidate evidence. A broad candidate such as "qiven-foundation"
    # must not satisfy a more specific trigger merely because its tokens are a
    # subset of the trigger phrase.
    return pattern_tokens.issubset(candidate_tokens)


def trigger_value_matches(value: str, candidates: Iterable[str]) -> bool:
    alternatives = _split_alternatives(value)
    return any(_lexical_match(alternative, candidate) for alternative in alternatives for candidate in candidates)


def _parse_instant(value: str) -> datetime:
    value = value.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
    parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    if parsed.tzinfo is None:
        raise ValueError("timezone is required")
    return parsed.astimezone(timezone.utc)


def _closed_ledger_subjects(root: Path) -> tuple[str, ...]:
    subjects: list[str] = []
    for path in sorted((root / "ledger/events").glob("*.jsonl"), key=lambda item: item.name):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path.name}:{line_number}: invalid ledger JSON") from exc
            if event.get("action") == "closed" and event.get("subject"):
                subjects.append(str(event["subject"]))
    return tuple(subjects)


def evaluate_trigger(
    trigger: Mapping[str, Any],
    query: Mapping[str, Any],
    root: Path = ROOT,
    *,
    now: datetime | None = None,
) -> dict[str, str]:
    trigger_type = str(trigger.get("type", ""))
    value = trigger.get("value")
    result: dict[str, str] = {"type": trigger_type}
    if value is not None:
        result["value"] = str(value)

    task = str(query.get("task", ""))
    topics = [str(item) for item in query.get("topics", []) or []]
    scopes = [str(item) for item in query.get("scopes", []) or []]
    touches = [str(item) for item in query.get("touches", []) or []]
    signals = [str(item) for item in query.get("signals", []) or []]
    conditions = [str(item) for item in query.get("conditions", []) or []]
    changed = [str(item) for item in query.get("changed", []) or []]
    trigger_value = str(value or "")
    complete = set(query.get("complete_inputs", []))
    evidence = query.get("input_evidence", {})
    def absence_result(field):
        return "not_triggered" if field in complete and evidence.get(field) else "unresolved"


    if trigger_type == "manual":
        result.update(result="manual", explanation="Manual trigger requires an explicit human decision.")
        return result

    if not trigger_value:
        result.update(result="unresolved", explanation="Trigger value is missing; deterministic evaluation cannot proceed.")
        return result

    if trigger_type == "on_touch":
        candidates = [*touches, *scopes, *topics, task]
        matched = trigger_value_matches(trigger_value, candidates)
        result.update(
            result="applicable" if matched else absence_result("touches"),
            explanation="Trigger target matches the task/touch scope." if matched else "No match; absence requires an evidenced complete touches set.",
        )
        return result

    if trigger_type == "before":
        candidates = [*signals, *touches, task]
        matched = trigger_value_matches(trigger_value, candidates)
        result.update(
            result="due" if matched else "unresolved",
            explanation="Named before-boundary is explicitly present in task signals/touches." if matched else "Named before-boundary is not explicit enough to mark due.",
        )
        return result

    if trigger_type == "after":
        explicit = trigger_value_matches(trigger_value, signals)
        ledger = trigger_value_matches(trigger_value, _closed_ledger_subjects(Path(root)))
        matched = explicit or ledger
        result.update(
            result="due" if matched else "unresolved",
            explanation="After-prerequisite is explicitly complete in signals or the closed ledger." if matched else "No explicit completion evidence for after-prerequisite.",
        )
        return result

    if trigger_type == "on_change":
        matched = trigger_value_matches(trigger_value, changed)
        result.update(
            result="applicable" if matched else absence_result("changed"),
            explanation="Changed set matches trigger target." if matched else "No match; absence requires an evidenced complete changed set.",
        )
        return result

    if trigger_type == "on_date":
        try:
            due_at = _parse_instant(trigger_value)
            if now is None:
                now_value = query.get("now")
                now = _parse_instant(str(now_value)) if now_value else datetime.now(timezone.utc)
            elif now.tzinfo is None:
                raise ValueError("now must be timezone-aware")
            else:
                now = now.astimezone(timezone.utc)
        except (TypeError, ValueError) as exc:
            result.update(result="unresolved", explanation=f"Date trigger cannot be evaluated deterministically: {exc}.")
            return result
        is_due = now >= due_at
        result.update(
            result="due" if is_due else "not_triggered",
            explanation="Current time is at or after trigger time." if is_due else "Current time is before trigger time.",
        )
        return result

    if trigger_type == "condition":
        # Conditions are named assertions, not bags of words: "not X" must not match X.
        positive = _canonical_text(trigger_value) in {_canonical_text(x) for x in conditions}
        negative = _canonical_text(trigger_value) in {
            _canonical_text(str(x)) for x in query.get("negative_conditions", [])}
        if positive and negative:
            result.update(result="unresolved", explanation="Contradictory positive and negative condition assertions.")
        elif positive:
            result.update(result="due", explanation="Condition explicitly asserted true by caller; not authorization evidence.")
        elif negative:
            result.update(result="not_triggered", explanation="Condition explicitly asserted false by caller.")
        else:
            result.update(result=absence_result("conditions"),
                          explanation="Condition absent; only an evidenced complete condition set supports a negative result.")
        return result

    result.update(result="unresolved", explanation=f"Unsupported trigger type: {trigger_type}.")
    return result


def _expanded_terms(values: str | Iterable[str]) -> set[str]:
    tokens = set(normalize_tokens(values))
    tokens.update(token.replace("-", "") for token in tuple(tokens) if "-" in token)
    return {token for token in tokens if token and token not in GENERIC_TERMS}


def _project_aliases(name: str) -> set[str]:
    aliases = _expanded_terms((name, f"qiven-{name}"))
    aliases.discard("qiven")
    return aliases


def _add_reason(reasons: list[dict[str, str]], kind: str, value: str) -> None:
    candidate = {"kind": kind, "value": value}
    if candidate not in reasons:
        reasons.append(candidate)


def _record_search_text(record: CanonicalRecord) -> str:
    fields = [record.title, record.body]
    for key in ("statement", "why_it_exists", "why_not_now", "completion"):
        value = record.metadata.get(key)
        if value:
            fields.append(str(value))
    return "\n".join(fields)


def _record_relevance(record: CanonicalRecord, query: Mapping[str, Any]) -> tuple[int, list[dict[str, str]]]:
    score = 0
    reasons: list[dict[str, str]] = []
    include_ids = {str(item) for item in query.get("include_ids", []) or []}
    if record.id in include_ids:
        score += 1000
        _add_reason(reasons, "explicit_id", record.id)

    explicit_scopes = {_canonical_text(str(item)) for item in query.get("scopes", []) or []}
    record_scopes = [str(item) for item in record.metadata.get("scope", []) or []]
    for scope in record_scopes:
        if _canonical_text(scope) in explicit_scopes:
            score += 120
            _add_reason(reasons, "scope_match", scope)
            break

    qterms = _expanded_terms(
        [
            str(query.get("task", "")),
            *(str(item) for item in query.get("topics", []) or []),
            *(str(item) for item in query.get("scopes", []) or []),
            *(str(item) for item in query.get("touches", []) or []),
        ]
    )

    project_hits: list[str] = []
    for scope in record_scopes:
        normalized = _canonical_text(scope)
        if normalized.startswith("qiven-"):
            project = normalized.removeprefix("qiven-")
            if _project_aliases(project) & qterms:
                project_hits.append(scope)
    if project_hits:
        score += 60
        _add_reason(reasons, "project_match", sorted(project_hits)[0])

    tag_hits: list[str] = []
    for tag in (str(item) for item in record.metadata.get("tags", []) or []):
        if _expanded_terms(tag) & qterms:
            tag_hits.append(tag)
    if tag_hits:
        score += 80
        _add_reason(reasons, "tag_match", ", ".join(sorted(tag_hits)[:3]))

    title_hits = sorted(_expanded_terms(record.title) & qterms)
    if title_hits:
        score += min(90, 30 * len(title_hits))
        _add_reason(reasons, "title_match", ", ".join(title_hits[:5]))

    content_hits = sorted(_expanded_terms(_record_search_text(record)) & qterms)
    content_only = [term for term in content_hits if term not in title_hits]
    if content_only:
        # Body/prose overlap is intentionally a weak booster. It must not select
        # a record by itself because cross-domain ADRs routinely mention other
        # repositories in context/alternatives. Stronger metadata/title signals
        # must carry a record across SELECTION_THRESHOLD.
        score += min(16, 4 * len(content_only))
        _add_reason(reasons, "content_match", ", ".join(content_only[:5]))

    return score, reasons


def select_project_documents(query: Mapping[str, Any], root: Path = ROOT) -> list[dict[str, Any]]:
    qterms = _expanded_terms(
        [
            str(query.get("task", "")),
            *(str(item) for item in query.get("topics", []) or []),
            *(str(item) for item in query.get("scopes", []) or []),
            *(str(item) for item in query.get("touches", []) or []),
        ]
    )
    explicit_scopes = {_canonical_text(str(item)) for item in query.get("scopes", []) or []}
    selected: list[tuple[int, dict[str, Any]]] = []
    for document in load_project_documents(root):
        project = Path(document.path).parent.name
        reasons: list[dict[str, str]] = []
        score = 0
        if project in explicit_scopes or f"qiven-{project}" in explicit_scopes:
            score += 120
            _add_reason(reasons, "scope_match", f"qiven-{project}")
        if _project_aliases(project) & qterms:
            score += 60
            _add_reason(reasons, "project_match", f"qiven-{project}")
        if score:
            selected.append(
                (
                    score,
                    {
                        "path": document.path,
                        "title": f"qiven-{project} project context",
                        "reasons": reasons,
                    },
                )
            )
    return [item for _, item in sorted(selected, key=lambda pair: (-pair[0], pair[1]["path"]))]


def _select_decisions_and_memory(
    store: Mapping[str, tuple[CanonicalRecord, ...]], query: Mapping[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], set[str]]:
    records = [record for record in (*store["decisions"], *store["memory"])
               if record_is_eligible(record, query)]
    by_id = {record.id: record for record in records}
    selected: dict[str, tuple[CanonicalRecord, int, list[dict[str, str]]]] = {}
    direct_ids: list[str] = []

    for record in records:
        score, reasons = _record_relevance(record, query)
        if score >= SELECTION_THRESHOLD:
            selected[record.id] = (record, score, reasons)
            direct_ids.append(record.id)

    for source_id in direct_ids:
        source = selected[source_id][0]
        for related_id in source.metadata.get("related", []) or []:
            related_id = str(related_id)
            target = by_id.get(related_id)
            if target is None or related_id in selected:
                continue
            selected[related_id] = (
                target,
                25,
                [{"kind": "related_record", "value": source_id}],
            )

    def materialize(category: str) -> list[dict[str, Any]]:
        rows: list[tuple[int, str, dict[str, Any]]] = []
        for record, score, reasons in selected.values():
            if record.category != category:
                continue
            rows.append(
                (
                    score,
                    record.id,
                    {
                        "id": record.id,
                        "path": record.path,
                        "title": record.title,
                        "status": record.status,
                        **lifecycle_fields(record),
                        "reasons": reasons,
                    },
                )
            )
        return [row for _, _, row in sorted(rows, key=lambda item: (-item[0], item[1]))]

    return materialize("decisions"), materialize("memory"), set(selected)


def _select_obligations(
    store: Mapping[str, tuple[CanonicalRecord, ...]],
    query: Mapping[str, Any],
    selected_context_ids: set[str],
    root: Path,
    now: datetime,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    selected: list[tuple[int, str, dict[str, Any]]] = []
    diagnostics: list[dict[str, str]] = []
    for record in store["obligations"]:
        if not record_is_eligible(record, query):
            continue

        score, reasons = _record_relevance(record, query)
        if is_current(record.category, record.status):
            trigger = evaluate_trigger(record.metadata.get("trigger", {}), query, root, now=now)
        else:
            # Inspecting a completed/cancelled obligation must never reopen it.
            trigger = {"type": "inactive", "result": "inactive",
                       "explanation": "Terminal obligation; trigger evaluation is disabled."}
        if trigger["result"] == "due":
            score += 240
            _add_reason(reasons, "trigger_due", trigger.get("value", trigger["type"]))
        elif trigger["result"] == "applicable":
            score += 180
            _add_reason(reasons, "trigger_applicable", trigger.get("value", trigger["type"]))

        # Relations are useful corroborating context, but they are deliberately
        # not an independent inclusion path for obligations. Broad ecosystem
        # ADRs can legitimately relate to many future obligations; allowing a
        # relation-only +40 to cross the selection threshold caused unrelated
        # Robotics/Physics work to leak into a Foundation task pack. An
        # obligation must first be relevant by its own task metadata/content,
        # be explicitly requested, or have a due/applicable trigger. Once it is
        # selected, related canonical records may improve ordering/explanation.
        if score < SELECTION_THRESHOLD:
            continue

        related_hits = sorted(
            str(item)
            for item in record.metadata.get("related", []) or []
            if str(item) in selected_context_ids
        )
        if related_hits:
            score += 40
            _add_reason(reasons, "related_record", related_hits[0])

        selected.append(
            (
                score,
                record.id,
                {
                    "id": record.id,
                    "path": record.path,
                    "title": record.title,
                    "status": record.status,
                    **lifecycle_fields(record),
                    "reasons": reasons,
                    "trigger": trigger,
                    "completion": str(record.metadata["completion"]),
                },
            )
        )

    rows = [row for _, _, row in sorted(selected, key=lambda item: (-item[0], item[1]))]
    return rows, diagnostics


def _format_utc(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("compilation time must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _compile_context_pack(
    query: Mapping[str, Any], root: Path, snapshot: SourceSnapshot, *, now: datetime | None = None
) -> dict[str, Any]:
    root = Path(root)
    prepared = prepare_query(query, root)
    if now is None:
        now = _parse_instant(str(prepared["now"])) if "now" in prepared else datetime.now(timezone.utc)
    elif now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    now = now.astimezone(timezone.utc)
    generated_at = _format_utc(now)
    prepared.setdefault("now", generated_at)

    store = load_canonical_store(root)
    decisions, memory, selected_context_ids = _select_decisions_and_memory(store, prepared)
    obligations, diagnostics = _select_obligations(store, prepared, selected_context_ids, root, now)

    all_ids = {record.id for records in store.values() for record in records}
    for requested_id in prepared.get("include_ids", []):
        if requested_id not in all_ids:
            diagnostics.append(
                {
                    "level": "warning",
                    "code": "unknown-explicit-id",
                    "message": f"Explicitly requested canonical ID does not exist: {requested_id}",
                }
            )

    mandatory_sources = [
        {
            "path": document.path,
            "reasons": [{"kind": "mandatory", "value": "always-loaded operating context"}],
        }
        for document in load_mandatory_sources(root, prepared)
    ]

    constraints = resolve_constraints(root, prepared, store)
    by_path = {r.path: r for rows in store.values() for r in rows}
    for rows in (decisions, memory, obligations):
        for row in rows:
            row["evidence"] = record_evidence(by_path[row["path"]], snapshot)
    pack = {
        "schema_version": 3,
        "snapshot": snapshot.manifest(),
        "constraints": constraints,
        "readiness": "review_required" if constraints["prohibited"] or constraints["status"] == "unresolved" else "context_loaded",
        "authorization": "not_granted",
        "generated_at": generated_at,
        "query": prepared,
        "mandatory_sources": mandatory_sources,
        "projects": select_project_documents(prepared, root),
        "decisions": decisions,
        "memory": memory,
        "obligations": obligations,
        "diagnostics": sorted(
            diagnostics,
            key=lambda item: (item["level"], item["code"], item["message"]),
        ),
    }

    apply_pack_budget(pack, snapshot)
    return pack


def compile_context_pack(query: Mapping[str, Any], root=ROOT, *, now: datetime | None = None) -> dict[str, Any]:
    snapshot = as_snapshot(root)
    with snapshot.materialize() as frozen:
        return _compile_context_pack(query, frozen, snapshot, now=now)

````
