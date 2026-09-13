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


ROOT = Path(__file__).resolve().parents[1]
MANDATORY_SOURCE_PATHS = (
    "MEMORY-CONSTITUTION.md",
    "collaboration/operating-contract.md",
    "state/current.md",
    "state/active-work.yaml",
)
CATEGORY_LAYOUT = {
    "decisions": ("decisions/index.yaml", "decisions"),
    "memory": ("memory/index.yaml", "memory/records"),
    "obligations": ("obligations/index.yaml", "obligations"),
}
NON_TERMINAL_OBLIGATION_STATUSES = frozenset({"open", "deferred", "blocked"})
TOKEN_RE = re.compile(r"[^\W_]+(?:-[^\W_]+)*", re.UNICODE)
ALTERNATIVE_RE = re.compile(r"\s+(?:or|或)\s+|\s*\|\s*", re.IGNORECASE)


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
    schema = _read_json(Path(root) / "schema/context-query.schema.json")
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(dict(query)),
        key=lambda item: tuple(str(x) for x in item.absolute_path),
    )
    if errors:
        details = "; ".join(error.message for error in errors)
        raise ValueError(f"invalid context query: {details}")


def prepare_query(query: Mapping[str, Any], root: Path = ROOT) -> dict[str, Any]:
    validate_query(query, root)
    prepared: dict[str, Any] = {"task": str(query["task"]).strip()}
    for key in ("topics", "scopes", "touches", "signals", "conditions", "changed", "include_ids"):
        prepared[key] = list(query.get(key, []))
    if "now" in query:
        prepared["now"] = query["now"]
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


def load_mandatory_sources(root: Path = ROOT) -> tuple[SourceDocument, ...]:
    root = Path(root)
    documents: list[SourceDocument] = []
    for relative in MANDATORY_SOURCE_PATHS:
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
    if pattern_tokens.issubset(candidate_tokens):
        return True
    if len(candidate_tokens) >= 2 and candidate_tokens.issubset(pattern_tokens):
        return True
    pattern_compounds = {token for token in pattern_tokens if "-" in token}
    candidate_compounds = {token for token in candidate_tokens if "-" in token}
    return bool(pattern_compounds & candidate_compounds)


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
            result="applicable" if matched else "not_triggered",
            explanation="Trigger target matches the task/touch scope." if matched else "No deterministic task/touch match for trigger target.",
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
            result="applicable" if matched else "not_triggered",
            explanation="Changed set matches trigger target." if matched else "Changed set does not match trigger target.",
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
        matched = trigger_value_matches(trigger_value, conditions)
        result.update(
            result="due" if matched else "not_triggered",
            explanation="Condition is explicitly asserted true by the query." if matched else "Condition is not explicitly asserted true by the query.",
        )
        return result

    result.update(result="unresolved", explanation=f"Unsupported trigger type: {trigger_type}.")
    return result
