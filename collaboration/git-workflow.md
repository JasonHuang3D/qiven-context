# Git Workflow

- Remote-native branches created directly by jason-brother normally use `jason-brother/<name>`.
- Local-execution branches implemented by jason-worker normally use `jason-worker/<name>`.
- jason-worker commits locally and does not push by default; the user pushes worker branches for remote review unless a separately accepted authority path explicitly permits the push.
- jason-brother may create/update remote branches and commits directly for authorized remote-native work when GitHub connector access is available and the selected mutation path is currently accepted.
- GitHub remote state is authoritative for published repository identity; a local clone is a non-authoritative working copy/cache.
- jason-brother reviews the exact remote delta before selecting validation scope.
- WIP pushes provide remote durability only. They must not implicitly trigger expensive full CI.
- A checkpoint candidate receives explicit CI dispatch only after its architecture/semantics/delta have been reviewed enough to define the required validation plan.
- Where a workflow supports an `expected_sha` input, it must fail before expensive validation when the workflow SHA does not match the requested candidate SHA.
- CI executes the requested deterministic validation plan; CI does not infer architectural relevance from the diff.
- CI is acceptance evidence for an exact reviewed candidate, not a remote debugging loop.
- After CI dispatch, Chat may perform at most one immediate exact-identity status read. If the run remains queued/in-progress, report repository, workflow/run, exact SHA, scope, last status, and the direct GitHub run URL, then return control.
- Required machine-local validation follows the active ContextView workflow. In the current ChatGPT + Jason view this is `views/workflows/chatgpt-jason-local-execution.md`: Human Manual Mode through Qiven Operator while Host-mediated AI mutation is suspended; later the same Operator task/gate surface is invoked through the accepted Host authority path.
- Do not create unmanaged OS-temporary repository clones as routine validation materialization. Use the view-declared long-lived Qiven workspace plus Operator-owned exact-identity worktree/scratch lifecycle when isolation is needed.
- After required validation and exact remote review, jason-brother may merge an exact validated batch head under ADR-0021 when all additional gates are satisfied.
- If any commit is added after the validated head, that changed head requires validation again before merge.
- Prefer a normal no-fast-forward merge when preserving the batch boundary is useful. Never force-push or bypass required validation.
- After a checkpoint is canonically merged to `main`, reconcile local `main`, delete merged/outdated temporary local and remote branches under an identity-safe cleanup policy, and remove Operator-owned scratch/worktrees rather than accumulating hidden workstation state.
- Git `user.name` and `user.email` are never changed as workflow machinery.

A remembered SHA, local ref, cached state file, or workstation working copy never overrides live GitHub remote state.

## Current Chat-side GitHub mutation restriction

The 2026-09-16 Context v2 merge incident demonstrated repeated Chat-side action-selection/invocation failures in the high-level GitHub contents mutation path. The evidence does **not** establish GitHub repository corruption or a GitHub backend defect: the connector executed the concrete high-level write action that Chat invoked, while the invoked action did not match the engineering operation Chat intended.

Until this path is explicitly requalified, high-level Chat-side GitHub contents mutations are **not an accepted path for canonical merges or other critical repository writes**. Read-only GitHub connector operations remain allowed. For critical local mutation or human-assisted publication, use Human Manual Mode through Qiven Operator where the active ContextView and required capability permit it. A low-level Git object/ref path may be used only when the exact repository, base/head identities, tree, parent set, and ref update are explicitly bound and reviewed; an ad-hoc contents write must never be used as a surrogate for a merge.

Requalification must be deliberate and isolated from canonical branches. It must prove that the intended engineering action maps to the invoked connector action before the restriction is removed.
