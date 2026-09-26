"""Minimal representative repository fixture for validator mutation tests.

The mutation tests prove each validation rule FIRES (anti-vacuity,
pit P-51 discipline). That proof does not need the real 500-file
corpus: this module builds a microcosm (~70 small files) that keeps
the exact record IDs and lifecycle relations the tests reference, so
`validate_repository` walks the same code paths while the corpus cost
drops by two orders of magnitude (2026-09-21, owner direction: stop
churning the disk with full-repo copies).

The REAL repository is validated separately, once per commit, by
tools/test_repo_contract.py.
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COPY_TREES = ("schema", "collaboration", "views")
COPY_FILES = (
    "BOOTSTRAP.md",
    "README.md",
    "MEMORY-CONSTITUTION.md",
    "governance/authority.yaml",
    "governance/context-constraints.yaml",
    "runtime/invocation-policy.yaml",
    "state/repositories.yaml",
    "state/active-work.yaml",
    "state/roadmap.yaml",
    "state/current.md",
    "legacy/ledger/README.md",
    "legacy/evidence/ci/README.md",
    "legacy/evidence/handoffs/README.md",
    "legacy/evidence/research/README.md",
)
STUB_DIRS = (
    "sessions",
    "memory/records",
    "obligations/legacy",
    "decisions/legacy",
    "projects",
    "evidence/audits",
    "legacy/tools",
    "legacy/benchmarks",
    "legacy/generated",
    "legacy/sessions",
    "templates",
    "tests/fixtures",
    "tests/cold-boot",
    "tools",
    ".github/workflows",
)

ADR_TMPL = """---
id: {rid}
status: {status}
title: {title}
scope: [qiven]
tags: [fixture]
created_at: '2026-09-13T00:00:00Z'
updated_at: '2026-09-13T00:00:00Z'
sources:
  - type: user_statement
    reference: fixture
related: [{related}]
supersedes: [{supersedes}]
superseded_by: [{superseded_by}]
---
# {title}

## Context

Fixture.

## Decision

Fixture.

## Alternatives Considered

Fixture.

## Consequences

Fixture.

## Revisit Conditions

Fixture.

## Provenance

Fixture.
"""

MEM_TMPL = """---
id: {rid}
kind: observation
status: {status}
title: {title}
scope: [qiven]
tags: [fixture]
created_at: '2026-09-13T00:00:00Z'
updated_at: '2026-09-13T00:00:00Z'
epistemic: {{basis: verified, confidence: high}}
temporal: {{valid_from: '2026-09-13T00:00:00Z', valid_until: null}}
sources:
  - type: user_statement
    reference: fixture
related: []
supersedes: [{supersedes}]
superseded_by: [{superseded_by}]
---
# {title}

Fixture memory record.
"""

OBL_TMPL = """---
id: {rid}
kind: {kind}
status: {status}
title: {title}
statement: Fixture obligation statement.
why_it_exists: Fixture.
why_not_now: Fixture.
scope: [qiven]
tags: [fixture]
trigger:
  type: {trigger_type}
  value: fixture
completion: Fixture.
sources:
  - type: user_statement
    reference: fixture
related: []
supersedes: []
superseded_by: [{superseded_by}]
created_at: '2026-09-13T00:00:00Z'
updated_at: '2026-09-13T00:00:00Z'
---
# {title}

Fixture obligation.
"""

SESSION = """# Qiven-v1 Session Checkpoint

## Session identity

Fixture session.

## Exact current task

Fixture.

## Accepted refs and evidence

- fixture

## Unaccepted candidate refs

- fixture

## Pending asynchronous work

None.

## Known inconsistencies and evidence gaps

None.

## Next action

Fixture.
"""

ADRS = (
    # (id, status, title, related, supersedes, superseded_by)
    ("ADR-0001", "superseded", "Externalize cognition", "", "", "ADR-0003,ADR-0030"),
    ("ADR-0003", "accepted", "Keep semantic source data simple", "ADR-0001", "ADR-0001", ""),
    ("ADR-0026", "accepted", "Host single-writer authority", "", "MEM-20260915T092000Z-3C7A41", ""),
    ("ADR-0030", "accepted", "Participant-independent context", "", "ADR-0001", ""),
    ("ADR-0033", "accepted", "ContextKernel semantic authority", "", "", ""),
)
MEMS = (
    ("MEM-20260913T183819Z-C2D841", "superseded", "Older", "", "MEM-20260915T111500Z-42A7D1"),
    ("MEM-20260915T111500Z-42A7D1", "active", "Newer", "MEM-20260913T183819Z-C2D841", ""),
    ("MEM-20260915T092000Z-3C7A41", "superseded", "Superseded by ADR-0026", "", "ADR-0026"),
)
OBLIGATIONS = (
    ("OBL-20260913T010101Z-A1B2C3", "followup", "open", "on_touch", ""),
    ("OBL-20260913T020202Z-D4E5F6", "followup", "done", "condition", ""),
)


def build(destination: Path) -> None:
    destination.mkdir(parents=True)
    for tree in COPY_TREES:
        shutil.copytree(ROOT / tree, destination / tree,
                        ignore=shutil.ignore_patterns("__pycache__"))
    for rel in COPY_FILES:
        target = destination / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, target)
    for rel in STUB_DIRS:
        (destination / rel).mkdir(parents=True, exist_ok=True)

    for rid, status, title, related, supersedes, superseded_by in ADRS:
        (destination / "decisions" / f"{rid}.md").write_text(
            ADR_TMPL.format(rid=rid, status=status, title=title, related=related,
                            supersedes=supersedes, superseded_by=superseded_by),
            encoding="utf-8")
    for rid, status, title, supersedes, superseded_by in MEMS:
        (destination / "memory/records" / f"{rid}.md").write_text(
            MEM_TMPL.format(rid=rid, status=status, title=title,
                            supersedes=supersedes, superseded_by=superseded_by),
            encoding="utf-8")
    for rid, kind, status, trigger_type, superseded_by in OBLIGATIONS:
        (destination / "obligations" / f"{rid}.md").write_text(
            OBL_TMPL.format(rid=rid, kind=kind, status=status, title=f"Fixture {rid}",
                            trigger_type=trigger_type, superseded_by=superseded_by),
            encoding="utf-8")

    (destination / "decisions/index.yaml").write_text(
        "schema_version: 1\nrecords:\n"
        + "".join(f"  - {{id: {r[0]}, file: {r[0]}.md, title: {r[2]}, status: {r[1]}}}\n" for r in ADRS),
        encoding="utf-8")
    (destination / "memory/index.yaml").write_text(
        "schema_version: 1\nrecords:\n"
        + "".join(f"  - {{id: {r[0]}, file: {r[0]}.md, title: {r[2]}, status: {r[1]}}}\n" for r in MEMS),
        encoding="utf-8")
    (destination / "obligations/index.yaml").write_text(
        "schema_version: 1\nrecords:\n"
        + "".join(f"  - id: {r[0]}\n    file: {r[0]}.md\n    title: Fixture {r[0]}\n    status: {r[2]}\n" for r in OBLIGATIONS),
        encoding="utf-8")

    (destination / "sessions/2026-09-13-qiven-v1.md").write_text(SESSION, encoding="utf-8")

    ledger = destination / "legacy/ledger/events/2026-09-13.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    first = (ROOT / "legacy/ledger/events/2026-09-13.jsonl").read_text(
        encoding="utf-8").splitlines()[0]
    ledger.write_text(first + "\n", encoding="utf-8")
