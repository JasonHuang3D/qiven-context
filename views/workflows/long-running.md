# Long-Running Mode — "Continue Unless H1" Workflow

Owner direction 2026-09-22: the essence of long-running mode is a
workflow that needs **only H1** — the session keeps working batch after
batch without per-batch owner review stops; H3/H4 boundaries apply where
they genuinely occur; per-batch H2 is satisfied through standing
delegation, not waived. This file is the single operational workflow for
that essence; it supersedes and unifies the former "overnight unattended
mode" (operating contract, 2026-09-19/20 practice) and the former
standing-window definition in this file. The contract anchor is the
Long-running mode section of `collaboration/human-handoff-boundary.md`
(ADR-0036 adjudication 2026-09-21).

## Entering and exiting

The owner explicitly opens the mode and states its scope (tasks,
repositories). The scope is the authorization boundary. Exit is by
explicit owner direction or window close; a fresh session never inherits
the mode. The mode is recorded in the session checkpoint.

## What may proceed and what stops

- **Proceeds**: implementation, refactoring, documentation, local gate
  runs, local commits on authorized task branches, and publication
  (push/PR/merge) with per-batch delegated-H2 receipts at exact heads
  (full-gate PASS + receipt recorded in each PR per the supervised-agent
  workflow). H2 presentation is asynchronous notification, never a stop:
  when a batch is ready, present it and immediately continue with the
  next work item.
- **Escalates to the owner** (a material round returns): governance
  mutation, ADR acceptance/ratification, qualification upgrades
  (owner-reserved, never delegated to the reviewing instance), and any
  specification-defect / decision-semantics / unexpected-failure round.
- **Stops (the only stops)**: H1 boundaries (isolation-crossing and
  owner-run trust-anchor work, including owner-designated adjudication
  points), H3/H4 where they genuinely apply, owner-declared end of the
  mode, or genuine resource exhaustion — which is a pause, not a close:
  the stash plus staged branches carry continuation.

## Working rules

1. **Gate discipline**: every published branch lands gate-PASS at its
   exact head; no gate is weakened to keep the mode moving. Changed
   heads revalidate.
2. **Checkpoint discipline is the interruption insurance.** The canonical
   session checkpoint (`sessions/`) is refreshed with a local commit at
   every material boundary — candidate staged, gate run, publication,
   blocker, next-action change — naming exact current task, staged
   branches with exact heads, gates run, pending H2/H1 items, and the
   exact next valid action.
3. **Workspace log**: every work item, gate result, and skipped item is
   recorded at `${workspace}/.generated-temp/workflow-logs/<window>.md`
   (per `collaboration/generated-temp-convention.md`).
4. **Five-minute skip**: any process unresponsive for more than five
   minutes is skipped and logged rather than waited on (the canonical
   hang contract's classification rules apply — heartbeat discriminates
   healthy long work from an apparent hang). No sleep/poll loops.
5. **No scope invention**: only tasks inside the owner's scope are
   executed; new work needs the owner to widen the scope.

## Stashed checkpoint (turn semantics)

- **Stashed checkpoint (fine grain, no git ceremony).** The workspace
  log carries a structured STASH section — exact current sub-task,
  uncommitted delta, next micro-action, staged branches with heads,
  pending H2/H1 items — updated as work proceeds. It is continuity
  insurance for interruption AND the pickup point for the next
  session/cold boot.
- **Canonical checkpoint (coarse grain, local commit).** `sessions/`
  refresh at staged-branch and publication boundaries, as above.
- **Stash guardrails.** Nothing that must survive the session may live
  ONLY in the stash (constitution §5): durable work rides staged
  branches and the canonical checkpoint. The canonical checkpoint names
  the active window and the stash path so a fresh session reads the
  stash FIRST when a window is active.

## Closing the mode

1. The session produces a summary of all work: branches, exact heads,
   gate evidence, publications with receipts — plus the next required H2
   item and its recommendation (standing owner instruction, 2026-09-20).
2. The owner reviews the closeout; anything rejected is preserved for
   rework or discarded.
3. Deferred owner-H2 classes (if any accumulated) are adjudicated.

## History

First exercised 2026-09-19/20 (overnight run: draft v3 phases 2-3,
foundation/math operator rolls) — codified then as the operating
contract's overnight section. Standing-window turn semantics amended
2026-09-20 (stashed-checkpoint incident). Contract anchor adjudicated
2026-09-21 (ADR-0036 long-running mode; delegated per-batch H2).
Unified into this single workflow by owner direction 2026-09-22; the
overnight concept is retired — this workflow covers overnight windows,
full days, and focused afternoons alike.
