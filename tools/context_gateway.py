from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping
from uuid import uuid4

from jsonschema import Draft202012Validator, FormatChecker

from context_compiler import compile_context_pack, prepare_query


ROOT = Path(__file__).resolve().parents[1]
POLICY = "mandatory_turn_preflight"
IDENTITY_FIELDS = (
    "task",
    "topics",
    "scopes",
    "touches",
    "signals",
    "conditions",
    "changed",
    "include_ids",
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _run_git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"git {' '.join(args)} failed"
        raise ValueError(detail)
    return completed.stdout


def resolve_canonical_ref(root: Path = ROOT) -> str:
    root = Path(root)
    try:
        ref = _run_git(root, "rev-parse", "HEAD").strip().casefold()
    except ValueError as exc:
        raise ValueError(f"cannot resolve qiven-context canonical ref: {exc}") from exc
    if len(ref) != 40 or any(ch not in "0123456789abcdef" for ch in ref):
        raise ValueError(f"unexpected qiven-context canonical ref: {ref!r}")
    return ref


def require_clean_canonical_source(root: Path = ROOT) -> str:
    root = Path(root)
    ref = resolve_canonical_ref(root)
    try:
        porcelain = _run_git(root, "status", "--porcelain=v1", "--untracked-files=all")
    except ValueError as exc:
        raise ValueError(f"cannot inspect qiven-context working tree: {exc}") from exc
    if porcelain.strip():
        raise ValueError(
            "qiven-context working tree is not clean; refusing to issue a Context Lease whose canonical_ref would not describe the retrieved source"
        )
    return ref


def task_fingerprint(query: Mapping[str, Any], root: Path = ROOT) -> str:
    prepared = prepare_query(query, root)
    identity = {field: prepared.get(field, [] if field != "task" else "") for field in IDENTITY_FIELDS}
    return _sha256_text(_canonical_json(identity))


def pack_sha256(pack: Mapping[str, Any]) -> str:
    return _sha256_text(_canonical_json(dict(pack)))


def validate_context_lease(lease: Mapping[str, Any], root: Path = ROOT) -> None:
    schema = json.loads((Path(root) / "schema/context-lease.schema.json").read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(dict(lease)),
        key=lambda item: tuple(str(x) for x in item.absolute_path),
    )
    if errors:
        details = "; ".join(error.message for error in errors)
        raise ValueError(f"invalid context lease: {details}")


def prepare_context(
    query: Mapping[str, Any],
    root: Path = ROOT,
    *,
    previous_lease: Mapping[str, Any] | None = None,
    canonical_ref: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    root = Path(root)
    if previous_lease is not None:
        validate_context_lease(previous_lease, root)

    # Reliability rule: every host turn reaching this gateway performs retrieval.
    # Reuse may be added later as an optimization, but must never bypass preflight.
    # Production calls resolve and require a clean exact Git source. Tests may pass
    # canonical_ref explicitly to isolate lease logic from repository state.
    ref = canonical_ref.casefold() if canonical_ref is not None else require_clean_canonical_source(root)
    if len(ref) != 40 or any(ch not in "0123456789abcdef" for ch in ref):
        raise ValueError(f"invalid canonical ref: {ref!r}")

    pack = compile_context_pack(query, root)
    fingerprint = task_fingerprint(query, root)
    digest = pack_sha256(pack)
    if previous_lease is None:
        transition = "initial"
    elif previous_lease["task_fingerprint"] == fingerprint:
        transition = "same_task_refresh"
    else:
        transition = "task_transition"

    prepared_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    lease: dict[str, Any] = {
        "schema_version": 1,
        "lease_id": f"CTX-{uuid4().hex[:16].upper()}",
        "canonical_ref": ref,
        "source_clean": True,
        "prepared_at": prepared_at,
        "policy": POLICY,
        "retrieval_invoked": True,
        "task_fingerprint": fingerprint,
        "task": str(pack["query"]["task"]),
        "transition": transition,
        "pack_sha256": digest,
    }
    if previous_lease is not None:
        lease["previous_lease_id"] = str(previous_lease["lease_id"])

    validate_context_lease(lease, root)
    return pack, lease
