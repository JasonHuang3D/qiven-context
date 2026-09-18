# Session Handoff and CI Contract

## Terminology correction

This file uses **session handoff** in its historical engineering-checkpoint sense: a
bounded session prepares continuity evidence for a later session. It is not the
Canonical Artifact Handoff defined by `collaboration/context-handoff-contract.md`,
and it does not prove backup/export portability. Where the unqualified word
`handoff` would be ambiguous, use `session checkpoint` for this mechanism.

This contract records cross-session engineering rules that should survive
project-specific checkpoint documents.

## Session checkpoint generation ownership

A Chat session identified as Qiven-vX owns and maintains the checkpoint/handoff for
the **next** session, Qiven-vX+1.

Therefore the current Qiven-v5 session must not continue appending live progress to
`collaboration/v5-*-handoff.md`. Existing v5 handoff material is historical input to
Qiven-v5 and remains frozen except for an explicit historical correction. Live v5
progress intended for future cold boot belongs in a v6 handoff/checkpoint document.
The same rule applies recursively.

A session checkpoint is not the authority for live repository state. Cold boot must
still reconcile canonical Context state with live repository refs and CI evidence
before mutation. A session checkpoint also cannot substitute for a Canonical Artifact
Handoff acceptance trial.

## CI repository visibility and zero-cost gate

Qiven repositories that require routine GitHub Actions CI should be public unless
the project owner explicitly accepts a different billing model or a repository
cannot truthfully be public.

For a public repository, routine CI may use GitHub standard GitHub-hosted runners
when current GitHub policy makes them zero-incremental-cost for the project. Runner
pricing/policy is live external information and must be re-verified before materially
changing runner labels. Larger/GPU/custom-image runners must not be introduced under
an assumed zero-cost rule without current billing review and project-owner approval.

Self-hosted runners do not consume GitHub-hosted runner minutes, but their machine,
cloud, electricity, maintenance and security costs remain external costs. They are
not automatically preferable.

## CI hang cancellation semantics

Long-running CI must distinguish legitimate expensive work from a liveness failure.
A workflow/job may be proactively cancelled when concrete evidence indicates a hang,
deadlock, infinite wait/loop or comparable failure. Preserve exact run, head SHA,
stuck step and reason. Cancellation is not PASS and must not be relabeled as an
ordinary test failure.

Do not cancel merely because a job is slower than expected without evidence. When
the cause is uncertain, investigate before classifying the run as hung. When the
current execution tool exposes a safe exact-run cancellation action, jason-brother
may cancel a confirmed hanging run directly; otherwise state the tool boundary.

## Chat-side asynchronous CI rule

GitHub Actions dispatch is asynchronous. A Chat turn must not emulate synchronous RPC
by repeatedly polling until completion.

After dispatch, jason-brother may perform one immediate exact-identity status read
when useful. If the exact run remains queued/in-progress, stop waiting in that turn
and report repository, workflow/run identity, exact head SHA and last state.
Verification resumes on a later user turn or through a server-side dependency/event
mechanism; Chat-side sleep/poll loops are forbidden.

## General bounded-wait rule

For non-CI external state where same-turn retry is genuinely necessary, repeated
observation/retry must have a hard bound before it begins. Unless a narrower contract
exists, the default Qiven Chat bound is no more than three total observations of the
same condition and no more than 60 seconds wall-clock waiting, whichever occurs
first. Transient network/API retries count against the same budget.

When exhausted, preserve exact correlation identifiers/last state and return control
to the project owner. Never keep a long-lived Chat turn open merely to await an
asynchronous external result.

## Qiven-v5 Chat availability incident

On 2026-09-16 the project owner reported that the Qiven-v5 thread became unable to
reload from ChatGPT Web, Windows and iOS while the session was performing CI status
waiting/polling. OpenAI support reportedly could not cancel the affected chat and
suggested deletion. Qiven does not infer the undocumented upstream mechanism or claim
polling was the proven internal cause.

The engineering conclusion is narrower: an unbounded/long-lived Chat-side wait can
put the orchestration control plane at unacceptable risk, so the asynchronous-CI and
bounded-wait rules are mandatory. See
`evidence/audits/qiven-v5-chat-polling-availability-incident-2026-09-16.md`.
