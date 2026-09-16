# Cold-Boot and Task-Transition Protocol

Do not rely on model-native memory, a prior chat, a local clone, or a remembered SHA as authoritative project state.

## Cold boot

1. Resolve the canonical GitHub repository `JasonHuang3D/qiven-context` and its remote `main` state.
2. Read `MEMORY-CONSTITUTION.md`.
3. Read `governance/authority.yaml`.
4. Read `collaboration/operating-contract.md`.
5. Read `collaboration/software-engineering-philosophy.md`.
6. Read `collaboration/context-operating-model.md`.
7. Read `state/current.md`, `state/active-work.yaml`, `state/repositories.yaml`, and `state/roadmap.yaml`.
8. Read the latest non-legacy session checkpoint when one exists. Treat it as continuity evidence only; never let it override canonical records or live authority.
9. Determine the current task.
10. Run task-specific retrieval before using project-history facts. Prefer the accepted derived retrieval path when available. Retrieval results are candidate evidence, not truth.
11. Load task-relevant project material, canonical memory, accepted decisions, rejected alternatives, and non-terminal obligations.
12. Verify live GitHub/CI/runtime facts for claims whose authority is live state. Resolve repository refs remotely; `state/repositories.yaml` is inventory, not a ref cache.
13. Report and classify any inconsistency before acting. Reconcile known conflicts under the canonicalization rules instead of leaving competing active truth indefinitely.
14. Before machine-local mutation, re-evaluate the current Host/DCR execution-authority gate. Transport reachability or a clean local tree is never sufficient authority.

Repeat task-specific retrieval whenever the conversation materially changes domain, repository, subsystem, or engineering question.

## Source discipline

- GitHub remote `qiven-context` is the canonical project-cognition repository.
- Local repositories are working copies and may be stale or contaminated.
- Model/account memory and prior-chat recollection may suggest search terms, but cannot fill project-history gaps.
- Never invent missing history. Record absence or evidence gaps explicitly.
- Legacy/frozen surfaces are historical inputs only and must not be treated as active write models.

For architecture and implementation tasks, determine semantic ownership and known mature failure classes before the first serious implementation. CI is a checkpoint acceptance proof, not a remote debugger.

For the full continuity acceptance standard, see `collaboration/project-continuity-acceptance.md`.
