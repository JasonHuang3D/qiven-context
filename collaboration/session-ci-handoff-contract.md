# Session Handoff and CI Contract

This contract records cross-session engineering rules that should survive project-specific handoff documents.

## Handoff generation ownership

A Chat session identified as Qiven-vX owns and maintains the handoff for the **next** session, Qiven-vX+1.

Therefore the current Qiven-v5 session must not continue appending live progress to `collaboration/v5-*-handoff.md`. Existing v5 handoff material is historical input to Qiven-v5 and remains frozen except for an explicit historical correction. Live v5 progress intended for future cold boot belongs in a v6 handoff document. The same rule applies recursively: a future Qiven-v6 session maintains v7 handoff material, and so on.

A handoff is not the authority for live repository state. Cold boot must still reconcile canonical Context state with live repository refs and CI evidence before mutation.

## CI repository visibility and zero-cost gate

Qiven repositories that require routine GitHub Actions CI should be public unless the project owner explicitly accepts a different billing model or a repository cannot truthfully be public.

For a public repository, routine CI may use GitHub **standard GitHub-hosted runners** because GitHub currently documents those runners as free and unlimited for public repositories. A runner being GitHub-hosted is not by itself sufficient: larger runners, GPU runners, and custom-image larger runners are billable even for public repositories and must not be introduced without an explicit billing review and project-owner approval.

Self-hosted runners do not consume GitHub-hosted runner minutes, but their machine, cloud, electricity, maintenance, and security costs remain external costs. They are not automatically preferable to standard hosted runners.

Before adding or materially changing CI runner labels, verify the current GitHub billing documentation rather than relying on this file as permanently current pricing evidence. The intended policy is zero incremental CI spend by default.

## CI hang cancellation semantics

Long-running CI must distinguish legitimate expensive work from a liveness failure. A workflow/job may be proactively cancelled when there is concrete evidence of a hang, deadlock, infinite wait, infinite loop, or comparable liveness failure. Evidence may include a step exceeding a previously established normal bound by a material margin, a known blocking call with no bounded completion path, or logs/state that identify a deadlocked or non-progressing execution.

Cancellation must be recorded truthfully as cancellation due to the identified or suspected liveness defect. Do not relabel a cancelled run as ordinary failure or as PASS. Preserve the exact run, head SHA, stuck step, and reason when the incident is relevant to design or acceptance.

Do not cancel merely because a job is slower than expected without evidence. When the cause is uncertain, investigate before classifying the run as a hang.

When the current execution tool exposes a safe exact-run cancellation action, jason-brother may cancel such a confirmed hanging CI run directly. If the available connector does not expose cancellation, state that tool boundary rather than pretending the run was cancelled.