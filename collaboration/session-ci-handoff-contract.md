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

## Chat-side asynchronous CI rule

GitHub Actions dispatch is asynchronous. A Chat turn must not emulate synchronous RPC by repeatedly polling a workflow run until completion.

After dispatch, jason-brother may perform one immediate exact-identity status read when useful. If the exact run is still `queued` or `in_progress`, stop waiting in that turn and report the repository, workflow/run identity, exact head SHA, and last observed state. Verification resumes on a later user turn or through a server-side dependency/event mechanism; Chat-side sleep/poll loops are forbidden.

A later observation that the CI completed does not retroactively make an earlier Chat-side wait safe. The orchestration rule protects the Chat control plane independently of runner liveness.

## General bounded-wait rule

For non-CI external state where a same-turn retry is genuinely necessary, all repeated observation/retry behavior must have a hard bound before it begins. Unless a narrower operation-specific bound is already defined, the default Qiven Chat bound is:

- no more than three total attempts/observations of the same external condition in one turn; and
- no more than 60 seconds of wall-clock waiting for that condition in one turn;
- whichever bound is reached first terminates the wait.

Transient API/network retries count against the same budget. Do not reset the budget by changing wording, endpoint shape, or tool surface while waiting for the same underlying external condition.

When the bound is exhausted, end the wait, preserve exact correlation identifiers and the last known state, and return control to the project owner. Never keep a long-lived Chat turn open merely to await an asynchronous external result.

## Qiven-v5 Chat availability incident

On 2026-09-16 the project owner reported that the Qiven-v5 thread became unable to reload from ChatGPT Web, Windows, and iOS while the session was performing CI status waiting/polling. The owner also reported that OpenAI support could not cancel the affected chat thread and suggested deleting the session. Qiven does not infer the undocumented upstream mechanism or claim that polling was the proven internal root cause.

The engineering conclusion is narrower and sufficient: an unbounded or long-lived Chat-side wait can put the Qiven orchestration control plane at unacceptable risk, so the asynchronous-CI and bounded-wait rules above are mandatory regardless of upstream implementation details. See `evidence/audits/qiven-v5-chat-polling-availability-incident-2026-09-16.md`.