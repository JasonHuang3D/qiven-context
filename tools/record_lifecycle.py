"""Shared lifecycle eligibility; relevance and authority are separate concerns."""
from __future__ import annotations

from typing import Any, Mapping, Protocol


CURRENT_STATUSES = {
    "decisions": frozenset({"accepted"}),
    "memory": frozenset({"active"}),
    "obligations": frozenset({"open", "deferred", "blocked"}),
}
KNOWN_STATUSES = {
    "decisions": CURRENT_STATUSES["decisions"] | {"proposed", "superseded", "rejected"},
    "memory": CURRENT_STATUSES["memory"] | {"superseded", "retracted", "archived"},
    "obligations": CURRENT_STATUSES["obligations"] | {"done", "cancelled", "superseded"},
}


class LifecycleRecord(Protocol):
    category: str
    id: str
    status: str
    metadata: Mapping[str, Any]


def is_current(category: str, status: str) -> bool:
    if category not in KNOWN_STATUSES or status not in KNOWN_STATUSES[category]:
        raise ValueError(f"unknown canonical lifecycle: {category}/{status}")
    return status in CURRENT_STATUSES[category]


def record_is_eligible(record: LifecycleRecord, query: Mapping[str, Any]) -> bool:
    mode = query.get("record_mode", "current")
    if mode not in {"current", "history"}:
        raise ValueError(f"unknown record_mode: {mode}")
    current = is_current(record.category, record.status)
    return current or mode == "history" or record.id in query.get("include_ids", [])


def lifecycle_fields(record: LifecycleRecord) -> dict[str, Any]:
    return {
        "current_eligible": is_current(record.category, record.status),
        "supersedes": list(record.metadata.get("supersedes", []) or []),
        "superseded_by": list(record.metadata.get("superseded_by", []) or []),
    }
