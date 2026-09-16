# Current State

## Active objective

Qiven engineering feature development is frozen while `qiven-context` migrates to the v2 continuity model on `jason-brother/context-v2-operating-model`. The migration reduces active write surfaces, reconciles known stale cognition, establishes GitHub-remote authority, and introduces Project Continuity acceptance.

## Context authority and governance

- Canonical project cognition is the GitHub remote `JasonHuang3D/qiven-context`; local clones are non-authoritative working copies.
- Current governance authentication trusts GitHub account-level identity. `JasonHuang3D` is the root governance principal. Qiven does not attempt biological-human authentication; accepted residual risks are recorded in `governance/authority.yaml`.
- `collaboration/` is normative only. Session continuity evidence belongs in `sessions/`.
- Manual ledger writes are frozen. `evidence/ci`, `evidence/handoffs`, and `evidence/research` are deprecated active surfaces. Curated durable evidence remains in `evidence/audits/`.
- Known conflicts must be canonicalized; superseded/legacy material remains historical but must not compete as active truth.

## Accepted engineering checkpoint

The latest formally accepted Host checkpoint remains `8e5b9dec64bf739af84e981df12afc1969599738`, the bounded owner-only Windows named-pipe transport/session lifecycle. Exact GitHub Actions run `35060483714` passed. Acceptance evidence is `evidence/audits/host-local-pipe-transport-acceptance-2026-09-16.md`.

## Preserved unaccepted Host candidate

`JasonHuang3D/qiven-host:jason-brother/host-batch-000` currently resolves remotely to `0e35bb111deb2faeec885ffc9664deab6049f693` (`host: add protocol dispatcher and protected NoOp`). Exact GitHub Actions run `35063639174` completed successfully for that SHA. The run was push-triggered, which is a process regression against ADR-0005. The candidate is **not formally accepted** because Host semantic acceptance was intentionally paused for the Context v2 migration.

A green CI run is validation evidence, not semantic acceptance.

## Safety gate and paused work

`OBL-20260915T163500Z-9D4C72` remains open. Mutating DCR or other remote-AI execution on JasonPC stays suspended until Host Batch 001 production authority integration proves the production mutation path cannot bypass Host.

Host feature work, Runtime process execution, DCR Windows Phase 1, and CAD are paused behind Context v2 continuity acceptance.

## Current continuity inconsistencies being removed

- v5/v6/v7 Chat handoffs were incorrectly stored under normative `collaboration/`; v2 moves them to `sessions/legacy/`.
- session evidence for Qiven-v2 through Qiven-v5 was not maintained. The gap is recorded; no fabricated backfill is allowed.
- `ledger/events` stopped after 2026-09-14 and is no longer a complete cognition history; v2 freezes it as legacy instead of pretending it remains authoritative.
- repository inventory previously cached stale SHAs while claiming `live_git` authority; v2 removes all live ref snapshots from canonical inventory.
- old active DCR/roadmap memory that predates the split-brain authority correction is superseded rather than left active.
- the root README and old checkpoint protocol contained obsolete Phase-0/future-work statements; v2 makes them timeless/current-contract documents.

## Next boundary

Complete repository/schema/invariant validation on the v2 candidate and run the first fresh-session Project Continuity acceptance. After Context v2 is accepted, reconcile the Host candidate `0e35bb...` by semantic review against its exact successful CI evidence before any further Host implementation.
