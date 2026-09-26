#!/usr/bin/env python
"""Canonical reference-integrity sweep (pit P-52; A3/A4 in the activation inventory).

Twice on 2026-09-20 a rename left dangling references behind: the views
restructure updated the machine declaration but not a hardcoded test path
(masked by a scoped gate), and its own commit claimed "all stale path
references updated" while six remained on canonical main. This sweep makes
that failure class mechanical: every repo-relative path reference on a
NORMATIVE surface (contracts, governance, views, state, decisions, docs,
tooling, tests) must resolve to an existing file or directory.

Historical/evidence surfaces (memory/records bodies, sessions/, evidence/)
are deliberately out of scope: they record what was true at the time
(I-PM scoping precedent). Cross-repository and absolute references are
skipped (verify-live domain).

Usage:
    python tools/check_references.py            # gate mode, exit 1 on findings
    python tools/check_references.py --report   # list findings, exit 0
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Normative surfaces: rules and the machinery that enforces them. Test
# files are excluded: their synthetic paths are intentional fixtures, and
# real-path drift inside them is caught by their own execution.
SCAN_DIRS = ["collaboration", "governance", "views", "decisions", "state",
             "schema", "templates", "projects"]
SCAN_FILES = ["README.md", "BOOTSTRAP.md", "AGENTS.md", "MEMORY-CONSTITUTION.md"]

EXTENSIONS = {".md", ".yaml", ".yml", ".py", ".json", ".cmd", ".sh", ".cmake",
              ".cpp", ".hpp", ".txt"}

# Documented exemptions, each with its reason (review this list on fires).
EXEMPT_TOKENS = {
    # pattern placeholder for the session-naming convention
    "sessions/YYYY-MM-DD-qiven-vN.md",
    # cross-repository citations (devkit / math), not this repository's tree
    "tests/vector_core.cpp",
    "templates/cpp-library/managed-files.cmake",
    # cross-repository citations (qiven-runtime, the simulated-gate batch
    # OBL-20260926T234500Z-B4C5D6 item 4 / ADR-0055): the rig, its kit
    # regressions and its fixture corpus live in qiven-runtime's tree
    "tools/h1_sim_gate.py",
    "tools/h1_kit_test.py",
    "tests/fixtures/h1-sim/catalogue.json",
}
EXEMPT_FILES = {
    # describes the qiven-devkit repository's own tree, not this one
    "projects/devkit/README.md",
}

PATH_TOKEN = re.compile(
    r"\b((?:collaboration|governance|views|decisions|memory|obligations|legacy|"
    r"sessions|state|evidence|tools|tests|schema|templates|projects|"
    r"generated|benchmarks|docs)/[A-Za-z0-9_.\-/]+)"
)
TRAILING = ".,;:)'\"“”»]"


def clean(token: str) -> str:
    token = token.rstrip(TRAILING)
    token = re.sub(r"#\S+$", "", token)      # markdown anchors
    token = re.sub(r":\d+$", "", token)      # file:line citations
    token = re.sub(r"\s*\([^)]*\)$", "", token)  # trailing parenthetical notes
    return token.rstrip(TRAILING + "/")


def iter_targets():
    for d in SCAN_DIRS:
        base = ROOT / d
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*")):
            if p.is_file() and p.suffix in EXTENSIONS:
                yield p
    for name in SCAN_FILES:
        p = ROOT / name
        if p.is_file():
            yield p


def scan() -> list[str]:
    findings = []
    for path in iter_targets():
        rel = path.relative_to(ROOT).as_posix()
        if rel in EXEMPT_FILES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), 1):
            for match in PATH_TOKEN.finditer(line):
                token = clean(match.group(1))
                if not token or token.endswith("/"):
                    continue
                if "/." in token:            # dot-directories (temp artifacts)
                    continue
                if Path(token).suffix not in EXTENSIONS:
                    continue                 # prose fragments & bare dir lists
                if token in EXEMPT_TOKENS:
                    continue
                if token.startswith("docs/"):
                    continue                 # cross-repo: this repo has no docs/
                if (ROOT / token).exists():
                    continue
                if token.startswith("legacy/") and (ROOT / "decisions" / token).exists():
                    continue                 # decisions index rows are decisions/-relative
                findings.append(f"{rel}:{lineno}: dangling '{token}'")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="store_true",
                        help="list findings without failing")
    args = parser.parse_args()
    findings = scan()
    for f in findings:
        print(f)
    print(f"reference sweep: {len(findings)} dangling "
          f"({'report mode: exit code suppressed' if args.report else 'clean' if not findings else 'dangling findings fail the check'})")
    if findings and not args.report:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
