# Current State

## Active objective

Qiven engineering feature development remains frozen while `qiven-context` completes Context v2 acceptance on `jason-brother/context-v2-operating-model`. The migration reduces active write surfaces, reconciles known stale cognition, establishes GitHub-remote authority, and makes fresh-session Project Continuity the routine highest-level Context gate.

## Context authority and governance

- Canonical project cognition is the GitHub remote `JasonHuang3D/qiven-context`; local clones are non-authoritative working copies.
- Current governance authentication trusts GitHub account-level identity. `JasonHuang3D` is the root governance principal. Qiven does not attempt biological-human authentication; accepted residual risks are recorded in `governance/authority.yaml`.
- `collaboration/` is normative only. Session continuity evidence belongs in `sessions/`.
- Manual ledger writes are frozen. `evidence/ci`, `evidence/handoffs`, and `evidence/research` are deprecated active surfaces. Curated durable evidence remains in `evidence/audits/`.
- Known conflicts must be canonicalized; superseded/legacy material remains historical but must not compete as active truth.

## Context v2 acceptance evidence

Exact predecessor candidate `8f854de4398053f68f9b571c1875a867b78836d0` passed the owner-controlled repository validation gate from a fresh detached clone: all full suites, diff checks, clean-tree, and final exact-head verification passed. Evidence is `evidence/audits/context-v2-exact-validation-2026-09-16.md`.

Fresh-session Project Continuity Run 001 against the same exact remote ref also passed. It reconstructed governance, accepted/candidate boundaries, blockers/obligations, superseded/legacy cognition, live GitHub/CI facts, inconsistencies, and the next valid action without prior conversation/model memory or invented history. Evidence is `evidence/audits/project-continuity-context-v2-run001-2026-09-16.md`.

Post-run review corrected one acceptance-spec defect: a fresh human operator is not required for every routine Context release. Fresh-human replaceability is now the separate higher-order Human Succession Acceptance contract. Because this correction does not change the project cognition/retrieval inputs reconstructed by Run 001, the blind continuity result carries forward; the corrected final candidate still requires a fresh exact-head repository validation before merge.

## Accepted engineering checkpoint

The latest formally accepted Host checkpoint remains `8e5b9dec64bf739af84e981df12afc1969599738`, the bounded owner-only Windows named-pipe transport/session lifecycle. Exact GitHub Actions run `35060483714` passed. Acceptance evidence is `evidence/audits/host-local-pipe-transport-acceptance-2026-09-16.md`.

## Preserved unaccepted Host candidate

`JasonHuang3D/qiven-host:jason-brother/host-batch-000` currently resolves remotely to `0e35bb111deb2faeec885ffc9664deab6049f693` (`host: add protocol dispatcher and protected NoOp`). Exact GitHub Actions run `35063639174` completed successfully for that SHA. The run was push-triggered, which is a process regression against ADR-0005. The candidate is **not formally accepted** because Host semantic acceptance was intentionally paused for the Context v2 migration.

A green CI run is validation evidence, not semantic acceptance.

## Safety gate and paused work

`OBL-20260915T163500Z-9D4C72` remains open. Mutating DCR or other remote-AI execution on JasonPC stays suspended until Host Batch 001 production authority integration proves the production mutation path cannot bypass Host.

Host feature work, Runtime process execution, DCR Windows Phase 1, and CAD remain paused until Context v2 is canonically accepted.

## Known continuity gaps

- session evidence for Qiven-v2 through Qiven-v5 was not maintained; no fabricated backfill is allowed;
- the v1 ledger stopped after 2026-09-14 and is frozen legacy rather than complete cognition history;
- `qiven-runtime` did not resolve as a GitHub repository during migration and no remote may be invented;
- qiven-host CI push-trigger behavior still conflicts with ADR-0005 and must be corrected before normal Host checkpoint CI resumes.

## Next boundary

Run `tools\validate-candidate.cmd <exact-corrected-head>` on the corrected Context v2 candidate. If it passes, perform Context v2 canonical acceptance/merge. Only then resume semantic review of Host candidate `0e35bb...`; do not start additional Host feature implementation first.
