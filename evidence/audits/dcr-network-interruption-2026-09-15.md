# Qiven DCR / controller interruption recovery — 2026-09-15

## Incident

During Qiven DCR Windows Phase 1 / Batch 001 implementation, one long Chat turn ended while source files were being written. At the time, the project owner also observed loss of connectivity on the currently selected Clash upstream node and switched to another working node. The interruption was therefore initially attributed to network/DCR transport loss.

A follow-up turn produced stronger evidence: the owner had **not** refreshed/restarted DCR, and the same DCR local-MCP process retained its in-memory tool history. `get_recent_tool_calls` returned 244 retained calls including the exact final writes from the prior turn, while `list_sessions` reported no active terminal sessions.

Therefore the canonical root cause of the turn ending is **unknown**. A controller/Chat-turn execution boundary is now a plausible hypothesis, especially because multiple long turns have ended after similar wall-clock durations, but no fixed turn-duration limit has been proven. The incident must not be recorded as a confirmed DCR disconnect.

The interruption happened after `include/qiven/dcr_win/process_generation.hpp` had been fully written and after several later Batch 001 files had also been written. All completed filesystem mutations remained intact on JasonPC.

## Recovery evidence

Recovery did not replay the prior implementation sequence blindly.

The first recovery pass proved live DCR with `ping`, checked for surviving active sessions, reread the exact local filesystem state, and resumed from the last observed file boundary. The second follow-up then proved continuity of the *same* DCR process by recovering its retained tool-call history without a DCR refresh.

This demonstrates that Chat/controller lifetime, tool-call lifetime, DCR relay lifetime, DCR local-MCP lifetime, local process lifetime, filesystem state, and Git state are separate evidence domains.

## Durable recovery rule

For any unexpected controller/UI/tool/DCR interruption, do not infer downstream execution state from the visible Chat outcome.

After control returns:

- prove current DCR liveness with `ping` or a minimal bounded command, not only a cached `online` indicator;
- when DCR was not restarted, inspect recent DCR tool history as additional reconciliation evidence;
- inspect active DCR sessions/processes when an earlier call may still have been running;
- reconcile the relevant filesystem and Git state before retrying a mutation;
- resume from the last proven state;
- replay an operation only when reconciliation proves it did not already complete;
- keep human CMD as fallback when DCR cannot be restored promptly.

Long workflows should be designed under the assumption that the controller may disappear between any two externally visible steps.

## Atomicity consequence

A tool call can be in one of several states when the controller disappears: not dispatched, dispatched with unknown result, completed with response lost, or still executing independently. Therefore destructive or non-idempotent operations need either atomic semantics, a durable operation identity, or a post-interruption query that can prove whether the mutation happened.

Repository pushes, commits, branch updates, file writes, process launches, and validation runs should be followed by exact-state checks rather than relying on acknowledgement delivery alone.

## Architectural consequence

Qiven DCR Windows should eventually distinguish at least:

- controller/Chat availability;
- relay/control-plane connectivity;
- DCR server/local-MCP generation identity;
- owned local process-generation state;
- command/result state;
- durable side-effect state;
- recovery/reconciliation state.

The supervisor must not equate controller or relay loss with child termination, and recovery logic must tolerate an acknowledgement being lost after a side effect already completed.
