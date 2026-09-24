# Human Manual Mode and Operator Contract

## Purpose

Human-assisted local execution is an engineering interface, not a request for a project owner to act as a shell-script interpreter. Qiven owns that interface through **Qiven Operator**. When an AI/agent needs human validation, execution, local CI help, or another machine-local action, the default semantic path is Human Manual Mode through Operator rather than ad-hoc shell choreography.

## Semantic boundary

The normative contract belongs to Operator behavior, not to a script extension or one operating system.

- `[RUN]`, `[WAIT]`, `[ OK ]`, and `[FAIL]` state output, truthful liveness, TTY-aware color, final PASS/FAIL summary, exact identity evidence, fail-fast sequencing, and machine-readable automation output belong to Qiven Operator.
- `.cmd`, `.bat`, PowerShell, POSIX shell, Python, or a native executable are implementation/launcher details below that semantic boundary. No file extension is a project-level human-interface requirement.
- Platform launchers may differ while preserving one Operator contract. The current Devkit Phase 1 implementation uses a thin Windows `tools\qiven.cmd` launcher over the shared Python runtime; a POSIX launcher should call the same Operator semantics rather than fork a second workflow.
- A raw helper script may exist below Operator for a repository task. It is not automatically a human interface merely because a human could launch it.

## Human Manual Mode

When local human assistance is required, the active ContextView supplies the human, environment, and workflow details. The agent should identify the repository, exact candidate identity, requested Operator action/profile, and the evidence needed back from the run. The human should normally need to invoke one short Operator command or an already-declared Operator task/gate, not assemble a multi-stage `&&` chain or save a one-off script supplied by Chat.

If a transient launcher window is deliberately used, its adapter must preserve the final result long enough for the human to observe it. This is a launcher responsibility, not a reason to impose `pause` or `.cmd` semantics on the cross-platform engineering contract. Prefer a persistent manual terminal/Operator surface for repeated work.

## Local materialization and hygiene

GitHub remote remains canonical. Workspace roots, machine/tool inventory, network policy, and scratch/materialization locations are ContextView environment/workflow concerns rather than project-global constants.

Do not create unmanaged repository clones in ambient OS temporary storage merely to validate a remote candidate. When isolated materialization is required, Operator should own the worktree/scratch lifecycle under a view-appropriate Qiven workspace location, bind it to the exact remote identity, and remove it deterministically when the operation completes. Failure evidence may be retained explicitly, but abandoned clones must not become human-memory cleanup debt.

## Bootstrap/emergency fallback

If Operator genuinely cannot perform a required action yet, use the smallest explicit bootstrap fallback necessary and record the missing Operator capability. Do not convert that fallback into a new permanent shell convention. Repeated human shell choreography is evidence that Operator policy/runtime is incomplete and should be improved.

## ContextView binding

This contract defines the generic Operator/Human Manual Mode semantics. Concrete workflow choices and environment details belong to the applicable view under `views/`. For the current ChatGPT + Jason collaboration, see `views/bindings/chatgpt-jason.yaml` and its referenced workflow/environment profiles; for desktop-resident local agents (ZCode), see `views/bindings/zcode-jason.yaml` and `views/workflows/supervised-agent.md`.

## Historical correction

The earlier 2026-09-16 rule that elevated direct-launch `.cmd/.bat` pause behavior into the primary human-facing contract was too low-level. It correctly identified that a transient console can hide the result, but it treated the symptom at the launcher layer and bypassed the already-accepted Qiven Operator orchestration architecture. Preserve human observability, but own it through Operator/manual-mode semantics rather than mandating one Windows script form.
