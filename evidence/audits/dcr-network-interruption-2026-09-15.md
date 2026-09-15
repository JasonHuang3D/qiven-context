# Qiven DCR transient network interruption — 2026-09-15

## Incident

During Qiven DCR Windows Phase 1 / Batch 001 implementation, the active JasonPC DCR transport disappeared while source files were being written. The project owner identified the immediate external cause as loss of connectivity on the currently selected Clash upstream node. After switching to another working node, the owner started a fresh DCR connection.

The interruption happened after `include/qiven/dcr_win/process_generation.hpp` had been fully written and while `src/process_generation.cpp` was only partially written.

## Recovery evidence

After transport restoration, Qiven did not replay the prior implementation sequence blindly.

Recovery proceeded by:

1. proving live DCR with fresh `ping` calls;
2. confirming there were no surviving active DCR terminal sessions;
3. rereading the exact local files that existed under `D:\JasonWork\qiven-dcr-win`;
4. observing that the completed header and partial source file remained intact on JasonPC;
5. resuming from the actual filesystem boundary rather than assuming either total failure or total completion.

This demonstrates that a transport interruption and the lifecycle of already-dispatched/local work are separate facts.

## Durable recovery rule

For transient DCR/network loss, do not infer local execution state from Chat/UI transport state.

After connectivity returns:

- prove DCR liveness with `ping` or a minimal bounded command, not only a cached `online` indicator;
- inspect active DCR sessions/processes when an earlier call may still have been running;
- reconcile the relevant filesystem and Git state before retrying a mutation;
- resume from the last proven local state;
- replay an operation only when reconciliation proves it did not already complete;
- keep human CMD as the fallback when DCR cannot be restored promptly.

A network interruption is therefore a recoverable transport event unless evidence shows repository corruption, incomplete atomicity, or another product-level failure.

## Architectural consequence

Qiven DCR Windows must eventually represent connectivity loss explicitly and distinguish at least:

- control-plane connectivity;
- owned local process-generation state;
- command/result state;
- recovery/reconciliation state.

The supervisor must not equate relay disconnect with child termination or discard local evidence that may have completed while the control channel was unavailable.
