# qiven-context

`qiven-context` is Qiven's durable, Git-versioned project cognition and continuity repository. Its purpose is to let the project survive session loss, turn failures, model/provider replacement, agent replacement, and authorized human-operator changes without making any one conversation or model-native memory authoritative.

The canonical repository is `JasonHuang3D/qiven-context` on GitHub. GitHub remote state is the current trust anchor for repository identity and project-governance authentication. Local clones are working copies and may be stale, contaminated, or disposable.

## Active semantic surfaces

- `collaboration/` — normative operating contracts only.
- `state/` — compact current operational state; never a historical transcript.
- `decisions/` — ADRs and their lifecycle.
- `memory/` — durable facts, lessons, invariants, risks, protocols, and negative knowledge.
- `obligations/` — explicit future work, commitments, revisit triggers, and validation gaps.
- `projects/` — durable project/domain models.
- `sessions/` — bounded continuity evidence for recent work. No canonical project cognition may exist only here.
- `evidence/audits/` — curated durable evidence and incident/acceptance records.
- `schema/` — record contracts.
- `generated/` — rebuildable derived context only.
- `tools/`, `tests/`, `benchmarks/` — validation and derived retrieval machinery.

Historical `ledger/` data and the placeholder `evidence/ci`, `evidence/handoffs`, and `evidence/research` buckets are retained only as explicit legacy/deprecated history. They are not active write surfaces.

## Continuity model

Project truth is identity-independent. Presentation may adapt to an agent's capabilities and a human's preferences. Mutation depends on explicit project authority. Current authentication is intentionally account-level: GitHub authenticates the `JasonHuang3D` root principal; Qiven does not attempt to prove biological identity.

Conflicts are preserved when discovered but are not a permanent operating mode. When evidence permits, conflicting active records must be reconciled into one current canonical interpretation while displaced records remain historically available as superseded, archived, retired, or legacy material.

Start with `BOOTSTRAP.md`. The highest-level acceptance target is the Project Continuity Test in `collaboration/project-continuity-acceptance.md`.

Never store credentials, tokens, private keys, recovery codes, or other secrets in this repository.
