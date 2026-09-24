# Git Workflow

For qiven-context Python semantics and source-contract work, the project owner's
2026-09-17 authorization in `collaboration/context-validation.md` (ADR-0032)
applies: the acting session validates directly in the agent runtime, without duplicate
JasonPC validation. Platform-dependent work and Host/DCR restrictions remain scoped
as described below.

- Branches use the acting designation or capability namespace (for example `jason-extended-cognition/<name>`, `zcode/<name>`); the legacy label namespaces `jason-brother/<name>` and `jason-worker/<name>` remain valid (ADR-0044 labels).
- The session commits locally and does not push by default; publication follows the active ContextView and H2 discipline (ADR-0036) unless a separately accepted authority path explicitly permits the push.
- The session may create/update remote branches and commits directly for authorized remote-native work when GitHub connector access is available and the selected mutation path is currently accepted.
- GitHub remote state is authoritative for published repository identity; a local clone is a non-authoritative working copy/cache.
- The session reviews the exact remote delta before selecting validation scope.
- CI semantics (necessity criterion, explicit-dispatch-only, LLM-proposed/human-adjudicated dispatch, free-tier pinning, bounded observation, the qiven-runtime phantom-run anomaly) are owned by `collaboration/session-ci-handoff-contract.md`; the operative summary here: a run exists only through deliberate dispatch, `expected_sha` must bind the exact candidate when supported, CI is acceptance evidence for an exact reviewed candidate (never a remote debugging loop), and after dispatch at most one immediate exact-identity status read precedes recording identity and returning control.
- Required machine-local validation follows the active ContextView workflow: `views/workflows/chatgpt-jason-local-execution.md` (Human Manual Mode through Qiven Operator) for `chatgpt-jason`, or `views/workflows/supervised-agent.md` for `zcode-jason`; the same Operator task/gate surface is the engineering interface in both.
- Do not create unmanaged OS-temporary repository clones as routine validation materialization. Use the view-declared long-lived Qiven workspace plus Operator-owned exact-identity worktree/scratch lifecycle when isolation is needed.
- After required validation and exact remote review, the session may merge an exact validated batch head under ADR-0021 and the applicable H2 discipline when all additional gates are satisfied.
- If any commit is added after the validated head, that changed head requires validation again before merge.
- Prefer a normal no-fast-forward merge when preserving the batch boundary is useful. Never force-push or bypass required validation.
- After a checkpoint is canonically merged to `main`, reconcile local `main`, delete merged/outdated temporary local and remote branches under an identity-safe cleanup policy, and remove Operator-owned scratch/worktrees rather than accumulating hidden workstation state.
- Git `user.name` and `user.email` are never changed as workflow machinery.

A remembered SHA, local ref, cached state file, or workstation working copy never overrides live GitHub remote state.

## Current Chat-side GitHub mutation restriction

The 2026-09-16 Context v2 merge incident demonstrated repeated Chat-side action-selection/invocation failures in the high-level GitHub contents mutation path. The evidence does **not** establish GitHub repository corruption or a GitHub backend defect: the connector executed the concrete high-level write action that Chat invoked, while the invoked action did not match the engineering operation Chat intended.

Until this path is explicitly requalified, high-level Chat-side GitHub contents mutations are **not an accepted path for canonical merges or other critical repository writes**. Read-only GitHub connector operations remain allowed. For critical local mutation or human-assisted publication, use Human Manual Mode through Qiven Operator where the active ContextView and required capability permit it. A low-level Git object/ref path may be used only when the exact repository, base/head identities, tree, parent set, and ref update are explicitly bound and reviewed; an ad-hoc contents write must never be used as a surrogate for a merge.

Requalification must be deliberate and isolated from canonical branches. It must prove that the intended engineering action maps to the invoked connector action before the restriction is removed.
