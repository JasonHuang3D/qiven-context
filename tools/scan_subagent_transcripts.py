"""Scan ZCode harness subagent transcripts for boundary-pollution markers.

Read-only analysis over the local ZCode session database
(``~/.zcode/cli/db/db.sqlite``): enumerates a subagent session's tool
calls (exact inputs/outputs), thinking (reasoning parts), and text, then
flags pollution markers per the clean-input boundary law
(views/workflows/subagent-delegation.md): loop-state vocabulary,
process-record paths, round-position reasoning. Exact seed markers
(``--seed-marker``) support pre-registered detection trials.

Exit codes: 0 = scan clean (or, with ``--expect-seeds``, all seeds
detected); 1 = findings present / seeds missing; 2 = environment or
usage error. Never mutates the database (opened read-only).
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_DB = Path.home() / ".zcode" / "cli" / "db" / "db.sqlite"

# Curated pollution taxonomy (clean-input boundary law). Each pattern is
# word-bounded / shape-specific to avoid incidental matches ("background"
# must not match "round"). Severity: high = loop-state or process-record
# channel proven live in the v29 incident; info = weaker signal, reported
# for triage without gating.
#
# Path-marker anchoring (2026-09-27 amendment): the qiven-runtime h1-sim
# fixture corpus legitimately SPELLS the governed-path vocabulary
# ({SIM_ROOT}/state/current.md, scratch-root gB/memory/records/...) because
# those relative paths are the test subject itself. A bare path-shape
# marker false-positives on that artifact vocabulary, so the two
# governed-path markers are anchored to the qiven-context repository name
# (absolute, relative and backslash forms all carry it); actual reads are
# ground-truthed by the tool_calls list regardless of content markers.
CURATED_MARKERS: list[tuple[str, str, re.Pattern[str]]] = [
    ("loop-state", "high", re.compile(r"\bpass count\b", re.I)),
    ("loop-state", "high", re.compile(r"\btally\b", re.I)),
    ("loop-state", "high", re.compile(r"\bresets? to (zero|0)\b", re.I)),
    ("loop-state", "high", re.compile(r"\bconsecutive pass", re.I)),
    ("loop-state", "high", re.compile(r"\b(final|last|terminal)\s+round\b", re.I)),
    ("loop-state", "high", re.compile(r"\bround \d+ of \d+", re.I)),
    ("loop-state", "high", re.compile(r"\b3-pass\b|\bthree[- ]pass\b", re.I)),
    ("loop-state", "high", re.compile(r"\bapproval loop\b", re.I)),
    ("round-position", "high", re.compile(r"\b(I am|this is) (on )?(round|the final)", re.I)),
    ("round-position", "info", re.compile(r"\bnext round\b", re.I)),
    ("process-record", "high", re.compile(r"[/\\]sessions[/\\]2026-", re.I)),
    ("process-record", "high", re.compile(r"[/\\]evidence[/\\]audits[/\\]", re.I)),
    ("process-record", "high",
     re.compile(r"qiven-context[/\\]state[/\\]current\.md\b", re.I)),
    ("process-record", "high",
     re.compile(r"qiven-context[/\\]memory[/\\]records[/\\]", re.I)),
    ("process-record", "high", re.compile(r"[/\\]obligations[/\\]OBL-", re.I)),
    ("process-record", "high", re.compile(r"[/\\]workflow-logs[/\\]", re.I)),
    ("process-record", "info", re.compile(r"\bqiven-v\d+\b", re.I)),
]

# Tool-input extraction per tool name: which input fields carry the
# worker's read/command surface (the ground truth for bait scoring).
INPUT_FIELDS: dict[str, list[str]] = {
    "Read": ["file_path"],
    "Write": ["file_path"],
    "Edit": ["file_path"],
    "Bash": ["command", "description"],
    "Grep": ["pattern", "path", "glob"],
    "Glob": ["pattern", "path"],
    "WebFetch": ["url", "prompt"],
    "WebSearch": ["query"],
    "Agent": ["prompt", "description"],
    "Task": ["prompt", "description"],
}

MAX_SNIPPET = 240


@dataclass
class Hit:
    channel: str
    marker: str
    severity: str
    snippet: str


@dataclass
class SessionScan:
    session_id: str
    title: str = ""
    created_at: int | None = None
    tool_calls: list[dict] = field(default_factory=list)
    hits: list[Hit] = field(default_factory=list)
    seed_found: dict[str, list[str]] = field(default_factory=dict)
    # hook_denials: tool calls BLOCKED live by a PreToolUse hook (status
    # == "error" and state.error prefixed "[qiven-hook]") — the only real
    # router-event signature. hook_text_mentions: the tag appearing in
    # outputs of COMPLETED calls (file content / test-subject stderr) —
    # not router events (B5 discriminator, F1A2B3).
    hook_denials: int = 0
    hook_text_mentions: int = 0

    @property
    def high_hits(self) -> list[Hit]:
        return [h for h in self.hits if h.severity == "high"]


def connect_ro(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise SystemExit(f"[FAIL] session database not found: {db_path}")
    return sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)


def resolve_sessions(con: sqlite3.Connection, args: argparse.Namespace) -> list[tuple[str, str, int | None]]:
    cur = con.cursor()
    rows: list[tuple[str, str, int | None]] = []
    if args.session:
        cur.execute(
            "select id, title, time_created from session where id like ? order by time_created",
            (args.session + "%",),
        )
        rows = [(r[0], r[1] or "", r[2]) for r in cur.fetchall()]
    elif args.parent:
        cur.execute(
            "select id, title, time_created from session where parent_id like ? order by time_created",
            (args.parent + "%",),
        )
        rows = [(r[0], r[1] or "", r[2]) for r in cur.fetchall()]
    elif args.all_subagents:
        cur.execute(
            "select id, title, time_created from session where parent_id is not null order by time_created"
        )
        rows = [(r[0], r[1] or "", r[2]) for r in cur.fetchall()]
    else:
        raise SystemExit("[FAIL] select sessions with --session/--parent/--all-subagents")
    if not rows:
        raise SystemExit("[FAIL] no matching sessions")
    return rows


def scan_channel(text: str, channel: str, out: list[Hit]) -> None:
    for name, severity, pattern in CURATED_MARKERS:
        m = pattern.search(text)
        if m:
            start = max(0, m.start() - 60)
            snippet = text[start : m.end() + 80].replace("\n", " ")
            out.append(Hit(channel, f"{name}:{m.group(0)}", severity, snippet[:MAX_SNIPPET]))


def scan_session(con: sqlite3.Connection, session_id: str, title: str, created: int | None,
                 seeds: list[str]) -> SessionScan:
    scan = SessionScan(session_id=session_id, title=title, created_at=created)
    cur = con.cursor()
    cur.execute(
        "select data from part where session_id = ? order by sequence", (session_id,)
    )
    all_text: list[str] = []
    for (raw,) in cur.fetchall():
        try:
            part = json.loads(raw)
        except json.JSONDecodeError:
            continue
        ptype = part.get("type")
        if ptype == "tool":
            tool = part.get("tool", "?")
            state = part.get("state") or {}
            entry = {
                "tool": tool,
                "input": state.get("input"),
                "status": state.get("status"),
            }
            scan.tool_calls.append(entry)
            fields = INPUT_FIELDS.get(tool)
            if fields and isinstance(state.get("input"), dict):
                for f in fields:
                    v = state["input"].get(f)
                    if isinstance(v, str) and v:
                        scan_channel(v, f"tool_input:{tool}.{f}", scan.hits)
                        all_text.append(v)
            out = state.get("output")
            if isinstance(out, str) and out:
                scan_channel(out, f"tool_output:{tool}", scan.hits)
                all_text.append(out)
                if "[qiven-hook]" in out:
                    scan.hook_text_mentions += 1
            err = state.get("error")
            if isinstance(err, str) and err.startswith("[qiven-hook]"):
                scan.hook_denials += 1
        elif ptype == "reasoning":
            text = _reasoning_text(part)
            if text:
                scan_channel(text, "reasoning", scan.hits)
                all_text.append(text)
        elif ptype == "text":
            text = part.get("text") or ""
            if text:
                scan_channel(text, "text", scan.hits)
                all_text.append(text)
    joined = "\n".join(all_text)
    for seed in seeds:
        if seed in joined:
            scan.seed_found.setdefault(seed, []).append("any-channel")
    return scan


def _reasoning_text(part: dict) -> str:
    for key in ("text", "reasoning", "content"):
        v = part.get(key)
        if isinstance(v, str) and v:
            return v
    state = part.get("state")
    if isinstance(state, dict):
        for key in ("text", "reasoning", "content"):
            v = state.get(key)
            if isinstance(v, str) and v:
                return v
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    select = parser.add_mutually_exclusive_group(required=True)
    select.add_argument("--session", help="subagent session id (prefix match)")
    select.add_argument("--parent", help="parent session id: scan all its subagents")
    select.add_argument("--all-subagents", action="store_true", help="scan every subagent session")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="session database path")
    parser.add_argument("--seed-marker", action="append", default=[],
                        help="exact marker string that MUST be detected (repeatable)")
    parser.add_argument("--expect-seeds", action="store_true",
                        help="exit 1 if any --seed-marker is absent from the scanned transcripts")
    parser.add_argument("--strict-curated", action="store_true",
                        help="exit 1 if any high-severity curated marker fires")
    parser.add_argument("--json-out", type=Path, help="write the full scan report as JSON")
    args = parser.parse_args()

    print(f"[ RUN] scan_subagent_transcripts db={args.db}")
    try:
        con = connect_ro(args.db)
    except SystemExit:
        raise
    except sqlite3.Error as exc:
        print(f"[FAIL] cannot open database: {exc}")
        return 2
    rows = resolve_sessions(con, args)

    report: list[dict] = []
    total_high = 0
    missing_seeds: list[str] = []
    for session_id, title, created in rows:
        scan = scan_session(con, session_id, title, created, args.seed_marker)
        total_high += len(scan.high_hits)
        for seed in args.seed_marker:
            if seed not in scan.seed_found:
                missing_seeds.append(f"{session_id[:24]}:{seed}")
        report.append({
            "session_id": session_id,
            "title": title[:120],
            "created_at": scan.created_at,
            "tool_call_count": len(scan.tool_calls),
            "tool_calls": scan.tool_calls,
            "hook_denials": scan.hook_denials,
            "hook_text_mentions": scan.hook_text_mentions,
            "high_hits": [h.__dict__ for h in scan.high_hits],
            "all_hits": [h.__dict__ for h in scan.hits],
            "seeds_detected": sorted(scan.seed_found),
        })
        verdict = "POLLUTED" if scan.high_hits else "clean"
        print(f"  session {session_id[:44]} tools={len(scan.tool_calls):4d} "
              f"high={len(scan.high_hits):2d} hookdeny={scan.hook_denials} "
              f"hooktext={scan.hook_text_mentions} -> {verdict}")
        for h in scan.high_hits:
            print(f"    [hit] {h.channel} {h.marker} :: {h.snippet[:150]}")
    con.close()

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                 encoding="utf-8")
        print(f"[ OK ] json report -> {args.json_out}")

    exit_code = 0
    if args.expect_seeds and missing_seeds:
        print(f"[FAIL] {len(missing_seeds)} seed marker(s) NOT detected:")
        for m in missing_seeds:
            print(f"    missing: {m}")
        exit_code = 1
    if args.strict_curated and total_high:
        print(f"[FAIL] {total_high} high-severity curated marker hit(s) across corpus")
        exit_code = 1
    if exit_code == 0:
        seeds_note = f" seeds={len(args.seed_marker)} all-detected" if args.expect_seeds else ""
        print(f"[ OK ] scan complete sessions={len(rows)} high_hits={total_high}{seeds_note}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
