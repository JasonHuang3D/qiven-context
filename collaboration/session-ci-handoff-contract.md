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

Each session identified as Qiven-vX owns and maintains the checkpoint
(`sessions/YYYY-MM-DD-qiven-vN.md`) for the **next** session, Qiven-vX+1.
Live progress intended for future cold boot belongs in the next session's
checkpoint document, not in the previous one; the rule applies recursively.
(The historical v5-era `collaboration/v5-*-handoff.md` surface that
motivated this rule is retired; see `legacy/sessions/`.)

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

## Remote-CI necessity criterion (2026-09-21 owner direction; enriched 2026-09-22)

Remote CI is a **remote validation device**, not a default gate. Public
repository + free-tier GitHub-hosted runners is the standing deployment
shape, but remote CI is used only when one of these holds:

1. **Environment beyond the local device**: the validation genuinely
   needs an OS/compiler environment the local device does not have (for
   example, JasonPC has Windows 11 but no Linux or macOS).
2. **Clean-sandbox re-validation at a critical juncture**: even for a
   platform the local device covers, a critical node may warrant
   re-validation in a clean remote sandbox, independent of the local
   machine's accumulated state.

**Dispatch is LLM-proposed, human-adjudicated** (owner direction
2026-09-22): when a session judges that a CI run is needed under either
class, it proactively proposes the dispatch (repository, workflow, exact
head, validation unit) to the owner; the human decides. Sessions never
dispatch on their own judgment alone, and never treat the absence of a
run as a defect (explicit dispatch requirement below).

A platform-first repository is validated on its local platform device: for
example, a Windows-first runtime validated on JasonPC needs no remote CI for
that acceptance. Full remote cross-platform coverage is a deliberate
escalation — never a silent default, and never a retroactive
requirement added to an already locally-accepted batch.

**Free-tier is pinned** (owner direction 2026-09-22): CI runs exclusively
on the current provider's free tier (today: GitHub free CI for public
repositories — the public-repo rule above derives from this). When a run
materially changes runner labels, or before relying on a runner class not
used recently, live-verify that the previously used runners are still
free; paid runner classes require explicit owner acceptance of the cost.

## Explicit dispatch requirement (2026-09-21 owner direction)

Qiven repository workflows are **never** triggered by push, pull request,
schedule, or any other automation. Workflows are `workflow_dispatch`-only;
the reference shape is `qiven-foundation/.github/workflows/ci.yml`. A run
exists only because an operator deliberately started it (Qiven Operator
`ci start`, `gh workflow run`, or the GitHub Actions UI).

Consequences:

- After a push or PR creation, expect NO run to appear. Never observe, wait
  for, or "verify" a run that was assumed to be auto-triggered by a push.
- The bounded-observation budget below is PRECONDITIONED on confirmed run
  creation: the dispatch response or the immediate exact-identity read must
  actually locate the dispatched run (repository, workflow, run id, exact
  head). Observing without a dispatched run is a process defect even if the
  observations stay inside the budget.
- If the dispatched run cannot be located, that is a dispatch or identity
  failure to resolve or record — not a reason to keep observing for a
  hypothetical auto-trigger.

## Chat-side asynchronous CI rule

GitHub Actions dispatch is asynchronous. A Chat turn must not emulate synchronous RPC
by repeatedly polling until completion.

After a DELIBERATE dispatch (explicit dispatch requirement above), one immediate
exact-identity status read confirms the run was created. If the exact run remains
queued/in-progress after that, at most three total observations of the same run and
60 seconds wall-clock (whichever first) may be spent waiting in the same turn; when
exhausted, stop observing, record repository, workflow/run identity, exact head SHA
and last state, and proceed to the next step. Verification resumes on a later user
turn or through a server-side dependency/event mechanism; Chat-side sleep/poll
loops are forbidden.

## CI hang cancellation semantics

Long-running CI must distinguish legitimate expensive work from a liveness failure.
A workflow/job may be proactively cancelled when concrete evidence indicates a hang,
deadlock, infinite wait/loop or comparable failure. Preserve exact run, head SHA,
stuck step and reason. Cancellation is not PASS and must not be relabeled as an
ordinary test failure.

Do not cancel merely because a job is slower than expected without evidence. When
the cause is uncertain, investigate before classifying the run as hung. When the
current execution tool exposes a safe exact-run cancellation action, the session
may cancel a confirmed hanging run directly; otherwise state the tool boundary.

## Zero-job failing runs mean an INVALID workflow file (2026-09-22, resolved)

Diagnostic rule: a run that fails with **zero jobs** (`jobs
total_count = 0`) on any event means the workflow FILE is invalid —
GitHub records the run and fails it immediately at parse/evaluation
time. This is a file defect, not a platform anomaly. Read the failure
reason from the workflow page in the GitHub UI or via the check-run
annotations API (`gh api repos/<owner>/<repo>/check-runs/<id>/annotations`);
**`gh run list` / `gh run view` do NOT surface workflow-file validation
errors** — the CLI is not defective, its run listing simply does not
carry them, so a CLI-only investigation will misclassify the defect.

Case record: qiven-runtime's `ci.yml` used `matrix.id` in a job-level
`if:` — invalid because GitHub evaluates job-level conditions before
strategy expansion. Inherited from the devkit bootstrap-only CI
template (fixed: devkit PR #18), the file was invalid from repo
creation; every push carrying it created a zero-job failing run
(misclassified as a platform anomaly earlier on 2026-09-22 — three
re-registration remedies were correctly observed to change nothing,
because registration was never the problem). Fix: runtime PR #35 moved
per-unit gating to step level via `needs.plan.outputs[matrix.id]`;
the merge push of that fix produced no run at all — the definitive
verification. `MEM-20260922T183000Z-E7F8A9` carries the full scar.

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
