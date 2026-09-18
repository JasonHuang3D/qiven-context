# Cold-Boot and Task-Transition Protocol

Do not rely on model-native memory, a prior chat, a local clone, or a remembered SHA as authoritative project state.

## Cold boot

1. Resolve the canonical GitHub repository `JasonHuang3D/qiven-context` and its remote `main` state.
2. Read `MEMORY-CONSTITUTION.md`.
3. Read `governance/authority.yaml`.
4. Read `collaboration/operating-contract.md` and `collaboration/human-handoff-boundary.md` (typed handoffs H1-H4, unattended-automation limits, and the no-verbal-waiver protocol, per ADR-0036).
5. Read `collaboration/context-validation.md`; its portable-validation exception does not waive task-specific acceptance roles or delivery-profile isolation.
6. Read `collaboration/software-engineering-philosophy.md`.
7. Read `collaboration/context-operating-model.md`.
8. Read `collaboration/context-handoff-contract.md`.
9. Read `state/current.md`, `state/active-work.yaml`, `state/repositories.yaml`, and `state/roadmap.yaml`.
10. Resolve the applicable ContextView for the current human/agent combination. View selection may use authenticated human identity plus current agent family/capabilities, but a view never overrides canonical project truth or governance. Registered views include `views/chatgpt-jason.yaml` (ChatGPT + Jason) and `views/zcode-jason.yaml` (ZCode + Jason); load the matching view with its referenced human-preference, environment, and workflow profiles. Role-to-model bindings in a view are resolved `verify_live` per ADR-0035; substitution or degradation of the serving model must be disclosed, never silently assumed. If no matching view exists, continue with the identity-independent ProjectContext rather than inventing one.
11. Read the latest non-legacy session checkpoint when one exists. Treat it as continuity evidence only; never let it override canonical records or live authority.
12. Determine the current task.
13. Run task-specific retrieval before using project-history facts. Prefer the accepted derived retrieval path when available. Retrieval results are candidate evidence, not truth.
14. Load task-relevant project material, canonical memory, accepted decisions, rejected alternatives, and non-terminal obligations.
15. Verify live GitHub/CI/runtime/environment facts for claims whose authority is live state. Resolve repository refs remotely; `state/repositories.yaml` is inventory, not a ref cache. ContextView environment profiles may describe durable roots/tool families, but exact versions, executable paths, VPN state, and mutable machine state must be verified when relevant.
16. Report and classify any inconsistency before acting. Reconcile known conflicts under the canonicalization rules instead of leaving competing active truth indefinitely.
17. Before machine-local mutation, re-evaluate the current Host/DCR execution-authority gate and the active ContextView workflow. Transport reachability or a clean local tree is never sufficient authority.

The machine input declaration is `collaboration/context-inputs.yaml`; compiler and candidate-bundle entrypoints resolve it through the same loader. See `collaboration/context-read-contract.md` for protected constraints, snapshot evidence and query semantics.

When a task concerns continuity, export, restore, backup, handoff or succession, declare the delivery/acceptance profile before acting. Remote cold boot, session checkpoint continuity, Canonical Artifact Handoff and Human Succession are different properties and must not substitute for one another. In particular, live GitHub reads allowed by a remote cold boot must not leak into the isolated phase of an artifact-handoff acceptance test.

Repeat task-specific retrieval whenever the conversation materially changes domain, repository, subsystem, or engineering question.

## Source discipline

- GitHub remote `qiven-context` is the canonical project-cognition repository.
- Local repositories are working copies and may be stale or contaminated.
- ContextView files tailor interaction, environment, and workflow for particular participants; they do not redefine project truth.
- Model/account memory and prior-chat recollection may suggest search terms, but cannot fill project-history gaps.
- Never invent missing history. Record absence or evidence gaps explicitly.
- Legacy/frozen surfaces are historical inputs only and must not be treated as active write models.

For architecture and implementation tasks, determine semantic ownership and known mature failure classes before the first serious implementation. CI is a checkpoint acceptance proof, not a remote debugger.

For the full continuity reconstruction standard, see `collaboration/project-continuity-acceptance.md`; for artifact isolation, see `collaboration/context-handoff-contract.md`.
