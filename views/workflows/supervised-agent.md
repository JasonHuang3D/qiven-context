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
   Canonical usage reference (pointer): `qiven-devkit/docs/conventions/
   operator-usage.md` — including `qiven exec`, the required path for long
   or unknown-duration commands (hang-contract rule 5 in
   `collaboration/operating-contract.md`).
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
4. **Publication discipline by default.** No push, PR creation, or merge
   without explicit owner authorization (or a standing accepted delegation
   such as long-running mode). A separately accepted standing
   authority may later widen this, mirroring the ADR-0021 requalification
   pattern; that widening is an ADR-level event, not a view-level default.
5. **Single-writer approximation.** Two agent sessions must not share one
   working copy concurrently. Concurrent sessions need separate worktrees or
   clones; canonical serialization goes through remote review until the Host
   broker exists. The 2026-09-16 split-brain incident is the governing evidence.
6. **Exact-head and precise-path discipline.** Validation and review bind to
   exact SHAs; a changed head revalidates. Publication uses precise low-level
   paths (`git push` of a named branch; `gh pr create` only where the
   repository's law keeps PRs, e.g. qiven-docs — qiven-context retired
   PR objects 2026-09-24) — never ad-hoc contents-API writes as merge
   surrogates. Before any merge-class
   publication, run the Operator `merge-proof` task: a full-gate PASS
   receipt for the exact head is required (P-53; the A3 masking class —
   a scoped gate is not the gate), and a missing receipt is a stop
   condition, not a warning.
7. **Asynchronous CI and bounded waits are inherited verbatim** from
   `collaboration/session-ci-handoff-contract.md`: runs are never
   push/automation-triggered — CI starts only by deliberate dispatch
   (Operator `ci start` / `gh workflow run`), one immediate exact-identity
   status read then confirms creation; after that, no sleep/poll loops,
   bounded-wait default of three observations / 60 seconds.

## Gate invocation for supervised agents (2026-09-19)

The operator's human view is also the right view for a supervised local agent:
`--verbose` staged output (`[ RUN]`/`[ OK ]` markers, heartbeats, buffered-log
summaries) is legible to the owner and the agent alike. Machine JSON is for
programmatic consumption only.

1. **Discover before invoking.** `tools\qiven.py --help`, then the
   subcommand's own `--help`. Subcommands: `info`, `gate`, `run`, `ci`. Global
   flags (`--json`, `--verbose`, `--no-color`) work before and after the
   subcommand.
2. **Gate and task shape.** `gate [name]` runs the named gate or, unnamed, the
   repository default gate; `run <task-name>...` executes one or more tasks.
   Unknown names come back with the available alternatives listed.
3. **Treat machine JSON as file-and-summary, never a live-stream filter
   target.** `--json` spills buffered suite logs to a durable file with a
   compact stdout summary (carrying `log_file`) once output exceeds the spill
   threshold; smaller outputs stay inline. Either way, parse the captured
   output or read the log file — piping the live stream through
   `tail`/``head`/text filters destroys evidence. In live sessions prefer the
   human view regardless.
4. **Windows path boundary.** A temp file written by the Git Bash shell must be
   addressed by its Windows path (`C:/Users/...`) when handed to Windows
   Python — `/tmp/...` is invisible to it.
5. **Scoped iteration.** Docs/memory/session/view-only transactions may use the
   `context-docs` gate (record, lifecycle and continuity suites plus
   diff/clean checks). The default `context-local` gate (repo-contract
   suites plus reference/diff/clean checks) is required on the final exact
   head before any merge-class publication. The Python ContextKernel
   reference suites and gates are SEALED (ADR-0040, owner direction
   2026-09-21): never registered, never run; sealed kernel code is not to
   be modified or "fixed" — changes to it are out of scope until an
   accepted decision unseals it. Ordinary text/record commits validate
   through the default gate only (fast repo-contract + cold-boot +
   reference/diff/clean). Changes to repository TOOLING (tools/*.py, the
   operator, bootstrap/toolchain wrappers) additionally require the
   `context-tools` gate (validator mutation tests + python resolution)
   at the exact head.

## Typical loop (single-session, ADR-0044)

```text
authorize task (owner)
  -> session: design; create branch if needed; author and commit changes
  -> session: run tests / gates at the exact head
  -> review of the exact delta (owner H2, or delegated reviewer per ADR-0036)
  -> session: publish (push; PR where the repository's law keeps them,
     otherwise branch merge per the 2026-09-24 qiven-context PR
     retirement) and reconcile local main;
     cleanup per git-workflow.md
```

## Execution-stage granularity (superseded by ADR-0044)

The 2026-09-18 owner direction that split authoring (brother-side) from
validation/publication (worker-side) within a batch is superseded by
ADR-0044 single-session unified engineering. The session both authors and
validates within one batch; a gate or test failure is a fix-and-revalidate
step inside the session (diagnose, correct, re-run the failed gate, then
any gate invalidated by the fix). What survives unchanged: validation and
review still bind to the exact head; a material round — a specification
defect, a decision-semantics question, an unexpected failure class, or an
owner-reserved gate — escalates to the owner rather than being
self-adjudicated.

## Delegated batch review

For a designated batch series, the owner may delegate the per-batch H2 review
to a delegated reviewer (ADR-0036 already admits a delegated reviewer as H2
evidence; long-running mode standing-delegates it). The batch's review receipt
(PR record where PRs remain; for qiven-context the gate PASS at the
exact head plus the branch-to-main merge commit and session checkpoint)
carries the review statement and exact head; escalation to the owner is
required when a round is material — a specification defect, a
decision-semantics question, an unexpected failure class, or any gate the
owner reserved (notably a qualification upgrade of the reviewing instance
itself, which stays owner-reserved to avoid reviewer self-certification).

Task batches may be pre-designed as an accepted obligation set: the session
(or the owner) materializes the specifications (exact edits, acceptance
criteria, sequencing triggers) as obligation records in one design
transaction; the executing session executes per obligation; each executed
round is reviewed against its specification before publication. A
specification defect found during execution returns to design review
rather than silently widening scope.

## Z2 — Host-mediated execution (sealed, ADR-0043)

qiven-host and the DCR transport are sealed and their programs retired
(ADR-0043, 2026-09-21); the archived OBL-20260915T163500Z-9D4C72 was
closed as moot. Machine-local governed mutation is henceforth
RuntimeHost-internal (Runtime real-execution-authority batches) — no
external broker re-enablement is pending, and a local supervised agent
must not treat its foreground presence as an execution-authority
substitute.

## Environment binding

Uses `views/environments/jasonpc.yaml` and the view's human preferences
(`views/humans/jason.yaml`). Exact tool versions, interpreter paths, and VPN
state are live facts verified when a task depends on them. The DCR-specific
shell/SSH environment facts in `legacy/collaboration/dcr-operational-contract.md` (sealed, ADR-0043)
remain the reference for any future DCR transport work, not for this profile.

## Current state

Z1 is active for authorized tasks (single-session, ADR-0044). Z2 is sealed
with the host program (ADR-0043). Unattended automation remains read-only
by default.
