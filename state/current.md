# Current State

## Active objective

Context v2, `ContextView<ChatGPT, Jason>`, and Qiven Operator Human Manual Mode are operational and canonical. Qiven-v6 is closed. The active objective is now `OBL-20260916T125000Z-5A8C31`: design `qiven-context.exe` / Context Engine as a semantic provider-consumer system with representation-independent storage, provenance, lifecycle, authority, migration, and backup/export behavior.

Architecture begins from semantic ownership and contracts rather than selecting a database product. GitHub remote `JasonHuang3D/qiven-context` remains canonical until a separately accepted authority migration proves semantic equivalence, provenance, continuity, backup/restore, and governance behavior.

## Accepted Context v2 operational checkpoint

- Context v2 and its post-v2 operating guardrails are canonical on `main`.
- The validated ContextView + Operator runtime candidate `a3ee448731ae26cce3cbf4afaa12d4d492769141` was accepted by canonical merge commit `35343c50c6df50d0ffc35664b24d029360787f35`.
- On 2026-09-16, Jason ran the declared Qiven Operator `cleanup-v6-temp` task from the long-lived `D:\JasonWork\qiven-context` working copy and reported `ALL PASS`.
- `OBL-20260916T102700Z-7C2A91` is complete. Normal validation uses the long-lived workspace plus Operator-owned scratch/worktrees rather than unmanaged ambient TEMP clones.

## Context authority and governance

- Canonical project cognition remains the GitHub remote; local repositories are non-authoritative working materializations.
- GitHub account-level identity remains the current governance authentication boundary.
- ContextView adapts interaction, environment, and workflow but cannot override identity-independent ProjectContext truth.
- Provider and consumer are semantic roles; human, agent, CI, repository, and runtime participants may occupy either role under explicit authority rules.

## ContextView<ChatGPT, Jason>

Workflow 1 is active: ChatGPT may develop remotely, then Jason switches to Human Manual Mode and invokes Qiven Operator for machine-local evidence or execution. Workflow 2 remains fail-closed until Host production authority is accepted.

## Safety and mutation guardrails

- `OBL-20260915T163500Z-9D4C72` remains open; mutating DCR/remote-AI execution on JasonPC is suspended.
- High-level Chat-side GitHub contents mutation remains unaccepted for critical writes. Low-level exact Git object/ref mutation is the admitted Chat-side critical-write path.
- The generic Operator packaging candidate in qiven-devkit remains unaccepted at `f5945df3c8c85b3fc49e228dcf7f88339567ff24`.
- The latest formally accepted Host checkpoint remains `8e5b9dec64bf739af84e981df12afc1969599738`, CI run `35060483714`. Corrected Host candidate `49e69c02fe2ded0b9607ccb4090c21cde96b8a1c` remains preserved and paused.

## Next boundary

Define the Context Engine semantic architecture: ContextKernel object model, provider command surface, AI-consumer query and ContextBundle surface, ContextView compilation, provenance and lifecycle semantics, transaction boundaries, storage abstraction, Git migration, deterministic backup/export/restore, and explicit authority-cutover criteria. Do not resume Host implementation first and do not canonicalize a storage technology before these semantics are accepted.
