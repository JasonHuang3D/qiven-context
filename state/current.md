# Current State

## Active objective

Context v2 and the post-v2 operating guardrails are canonical on `JasonHuang3D/qiven-context/main`. The current engineering objective remains disposition of corrected Host dispatcher + protected NoOp candidate `49e69c02fe2ded0b9607ccb4090c21cde96b8a1c`, but the immediate local-validation boundary is to restore actual use of the existing Qiven Operator Human Manual Mode instead of continuing ad-hoc shell scripts and unmanaged temporary clones.

## Context authority and governance

- Canonical project cognition is the GitHub remote `JasonHuang3D/qiven-context`; local clones are non-authoritative working copies.
- Current governance authentication trusts GitHub account-level identity. `JasonHuang3D` is the root governance principal. Qiven does not attempt biological-human authentication.
- Context v2 Project Continuity acceptance passed and is canonical. Human Succession remains a separate higher-order benchmark, not a routine release gate.
- Manual ledger writes remain frozen; deprecated evidence buckets and legacy handoffs remain non-current.
- Known conflicts must be canonicalized; superseded/legacy material must not compete as active truth.

## Local execution workflows

`collaboration/local-execution-workflows.md` is the canonical local-execution model.

Workflow 1 is active now: remote AI may develop against GitHub, and whenever JasonPC evidence or execution is required the project owner switches to Human Manual Mode and invokes Qiven Operator. Operator, not ad-hoc shell choreography, owns human-facing progress/state, validation sequencing, exact identity, summaries, task isolation, and managed scratch/worktree cleanup.

Workflow 2 remains future/blocked: after Host Batch 001 proves production no-bypass and Context explicitly re-enables remote mutation, AI reaches the same Operator/task surface through remote transport -> Qiven Host. The caller/authority changes; local engineering semantics remain the same.

JasonPC's current long-lived Qiven workspace is `D:\JasonWork`. Unmanaged `%TEMP%` repository clones are not an accepted routine validation mechanism. `OBL-20260916T102700Z-7C2A91` tracks cleanup of Qiven-v6 temporary clone debt.

The earlier `.cmd/.bat`-centric human-facing rule is superseded. Platform launchers are thin adapters; the project-level contract is Operator/manual-mode behavior. The underlying transient-console observability lesson remains valid but does not define the architecture.

## GitHub mutation guardrail

The 2026-09-16 Chat-side GitHub mutation incident remains a durable constraint. High-level Chat-side GitHub contents mutation is not currently accepted for canonical merges or other critical writes until explicitly requalified. Read-only connector use remains allowed. Low-level Git object/ref mutation is allowed only with exact repository/base/head/tree/parent/ref semantics bound and reviewed.

## Accepted Host engineering checkpoint

The latest formally accepted Host checkpoint remains `8e5b9dec64bf739af84e981df12afc1969599738`, the bounded owner-only Windows named-pipe transport/session lifecycle. Exact GitHub Actions run `35060483714` passed.

## Host dispatcher semantic review

Original candidate `0e35bb111deb2faeec885ffc9664deab6049f693` is not accepted as-is despite exact CI run `35063639174` being green. Semantic review found an unbound dispatch/close lifecycle window.

Correction `49e69c02fe2ded0b9607ccb4090c21cde96b8a1c` binds dispatch to `(OwnerPipeServer, slot)`, derives the Host-owned session under a dispatcher lifecycle gate, serializes dispatch/close for this conservative Batch 000 layer, adds stale-frame-after-close regression coverage, and changes qiven-host CI to manual `workflow_dispatch` with required `expected_sha`.

The correction candidate has passed exact remote semantic/delta review but has not yet passed the new local/full validation + exact CI acceptance boundary.

## Safety gate and paused work

`OBL-20260915T163500Z-9D4C72` remains open. Mutating DCR or other remote-AI execution on JasonPC stays suspended until Host Batch 001 production authority integration proves that the production mutation path cannot bypass Host and Context explicitly re-enables it.

Runtime process execution, DCR Windows Phase 1 production integration, CAD, and later product work remain paused behind the Host authority boundary.

ADR-0026 bounded scope/intent audit metadata and ADR-0029 recovery authority remain outstanding Batch 000 work; acceptance of the dispatcher checkpoint will not imply full Batch 000 acceptance.

## Known continuity/process gaps

- `qiven-runtime` still has no verified GitHub remote and no remote may be invented;
- Qiven-v2 through Qiven-v5 session evidence remains a historical gap; no fabricated backfill is allowed;
- Qiven-v6 created unmanaged temporary qiven-context clones during ad-hoc validation; cleanup is explicitly tracked by `OBL-20260916T102700Z-7C2A91` and must not be delegated to human memory.

## Next boundary

Use/restore Qiven Operator as Workflow 1 for the next JasonPC-assisted operation. The first manual-mode cycle must reconcile the known Qiven-v6 temporary-clone debt and validate exact qiven-host candidate `49e69c02fe2ded0b9607ccb4090c21cde96b8a1c` from the long-lived Qiven workspace without creating another unmanaged `%TEMP%` clone. After local validation, use the accepted explicit CI path and perform final semantic disposition before any new Host feature work.
