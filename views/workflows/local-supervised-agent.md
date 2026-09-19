# Local Supervised Agent Workflow (capability class: local_supervised_agent)

This profile instantiates Qiven's local-execution contracts for a
`local_supervised_agent` tool — a foreground, owner-launched agent session on
JasonPC with shell, filesystem, Git, and authenticated `gh` reach (currently
ZCode desktop under `ContextView<ZCode, Jason>`). It is the capability-class
generalization of the ChatGPT view's Human Manual Mode: the human relay step
disappears because the agent is already local, but every engineering semantic —
exact identity, fail-fast gates, truthful liveness, bounded waiting, cleanup —
is inherited unchanged from the canonical contracts.

## Z1 — Supervised foreground execution (active)

The session runs where the owner can see and gate it. Rules:

1. **Mutating actions pass the session permission surface.** The owner launched
   the session and sees each action; a denied permission is a boundary and must
   be stated as such, not circumvented (same rule as the connector boundary in
   `collaboration/operating-contract.md`).
2. **Operator is still the engineering interface.** When a declared task/gate
   exists (`.qiven/operator.json`), prefer invoking it over ad-hoc chains.
   Machine view (`--json`) is legitimate for an agent caller; human view with
   `--verbose` remains required for owner-run acceptance gates such as the K4
   producer (that is an H1 handoff and stays with the owner per
   `collaboration/human-handoff-boundary.md`).
3. **Unattended automation is read-only by default.** Scheduled, idle-time, or
   background executions may read, retrieve, analyze, and rebuild bounded
   derived artifacts. They must not push, create PRs, merge, run acceptance
   roles, or touch governance. Local commits are permitted only inside an
   explicitly authorized task scope. See ADR-0036 and
   `collaboration/human-handoff-boundary.md`.
4. **Worker discipline by default.** No push, PR creation, or merge without
   explicit per-task owner authorization. A separately accepted standing
   authority may later widen this, mirroring the ADR-0021 requalification
   pattern; that widening is an ADR-level event, not a view-level default.
5. **Single-writer approximation.** Two agent sessions must not share one
   working copy concurrently. Concurrent sessions need separate worktrees or
   clones; canonical serialization goes through remote review until the Host
   broker exists. The 2026-09-16 split-brain incident is the governing evidence.
6. **Exact-head and precise-path discipline.** Validation and review bind to
   exact SHAs; a changed head revalidates. Publication uses precise low-level
   paths (`git push` of a named branch, `gh pr create`) — never ad-hoc
   contents-API writes as merge surrogates.
7. **Asynchronous CI and bounded waits are inherited verbatim** from
   `collaboration/session-ci-handoff-contract.md`: one immediate exact-identity
   status read after dispatch, no sleep/poll loops, bounded-wait default of
   three observations / 60 seconds.

## Gate invocation for supervised agents (2026-09-19)

The operator's human view is also the right view for a supervised local agent:
`--verbose` staged output (`[ RUN]`/`[ OK ]` markers, heartbeats, buffered-log
summaries) is legible to the owner and the agent alike. Machine JSON is for
programmatic consumption only.

1. **Discover before invoking.** `tools\qiven.py --help`, then the
   subcommand's own `--help`. Global flags (`--json`, `--verbose`) precede the
   subcommand. Subcommands: `info`, `gate`, `run`, `ci`.
2. **Gate and task shape.** `gate` runs the repository default gate and takes
   no name argument; `run <task-name>` executes a single task.
3. **Never pipe machine JSON through filters in a live session.** `--json`
   emits one line whose buffered suite logs are lost the moment it passes
   through `tail`/`head`/text filters. Either run the human view, or capture
   the complete JSON to a file and parse that file.
4. **Windows path boundary.** A temp file written by the Git Bash shell must be
   addressed by its Windows path (`C:/Users/...`) when handed to Windows
   Python — `/tmp/...` is invisible to it.
5. **Scoped iteration.** Docs/memory/session/view-only transactions may use the
   `context-docs` gate (record, lifecycle and continuity suites plus
   diff/clean checks, ~90s instead of ~186s). The full default gate is
   required on the final exact head before any merge-class publication and for
   any tools/kernel change.

## Typical loop

```text
authorize task (owner)
  -> jason-brother: design; create branch if needed; author and commit changes
  -> jason-worker: run test / gate / push / PR (and merge after accepted review)
  -> review of the exact delta (owner H2, or delegated reviewer per ADR-0036)
  -> reconcile local main; cleanup per git-workflow.md
```

## Execution-stage granularity (2026-09-18 owner direction)

Within one batch, the brother-side instance authors: it designs, creates the
branch when necessary, and reads/writes/commits the changes — it does not run
tests, gates, push, or PR. The worker-side instance validates and publishes: it
runs the test suite and Operator gates, pushes, opens the PR, and merges after
the review is accepted. When a gate or test fails after a brother-authored
commit, the worker hands off to the brother, the brother corrects with a new
commit (still without running gates itself), and the worker revalidates and
publishes. Gate failures are handoff triggers, not worker-side fix opportunities.

## Delegated batch review

For a designated batch series, the owner may delegate the per-batch H2 review to
the brother-class reviewer (ADR-0036 already admits a delegated reviewer as H2
evidence). The PR record of each batch carries the review statement and exact
head; escalation to the owner is required when a round is material — a
specification defect, a decision-semantics question, an unexpected failure
class, or any gate the owner reserved (notably a qualification upgrade of the
reviewing instance itself, which stays owner-reserved to avoid reviewer
self-certification).

Task batches may be pre-designed as an accepted obligation set: jason-brother
materializes the specifications (exact edits, acceptance criteria, sequencing
triggers) as obligation records in one design transaction; jason-worker
executes per obligation; jason-brother reviews each executed round against its
specification before publication. A specification defect found during execution
returns to design review rather than silently widening worker scope.

## Z2 — Host-mediated execution (unchanged, fail-closed)

Workflow 2 semantics from `views/workflows/chatgpt-jason-local-execution.md`
apply unchanged: broker-mediated mutation waits for ADR-0026 Batch 001
acceptance and explicit re-enablement (`OBL-20260915T163500Z-9D4C72`). A local
supervised agent must not treat its foreground presence as a Host substitute.

## Environment binding

Uses `views/environments/jasonpc.yaml` and the view's human preferences
(`views/humans/jason.yaml`). Exact tool versions, interpreter paths, and VPN
state are live facts verified when a task depends on them. The DCR-specific
shell/SSH environment facts in `collaboration/dcr-operational-contract.md`
remain the reference for any future DCR transport work, not for this profile.

## Current state

Z1 is active for authorized tasks. Z2 remains fail-closed. Unattended
automation remains read-only by default.
