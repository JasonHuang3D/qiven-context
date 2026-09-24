# Host protocol dispatcher semantic review — 2026-09-16

## Reviewed identities

- accepted Host transport checkpoint: `8e5b9dec64bf739af84e981df12afc1969599738`;
- original dispatcher + protected NoOp candidate: `0e35bb111deb2faeec885ffc9664deab6049f693`;
- original candidate CI: run `35063639174`, `completed/success`, but push-triggered under the known ADR-0005 workflow regression;
- correction commit: `49e69c02fe2ded0b9607ccb4090c21cde96b8a1c` on `jason-brother/host-batch-000`.

## Original candidate disposition

`0e35bb...` is **not semantically accepted as-is**.

Its normal Acquire/Query/NoOp/replay/conflict/sequence/Release behavior, competing Host-session quarantine, authority-aware disconnect, result mapping, Host-issued lease generation, and protected NoOp begin/finish path are coherent with the accepted authority/codec/transport model. Exact run `35063639174` proved the code built and tested on Windows MSVC, Linux GCC, and macOS AppleClang in Debug/Release.

The blocking defect was at the transport-session lifecycle boundary. `ProtocolDispatcher::dispatch` accepted a `BrokerSessionId` supplied by its caller, while Acquire could move `AuthorityBroker` to `Leased` before dispatcher `active_lease_` tracking became visible to `close_connection`. The candidate did not define or enforce a lifecycle contract that prevented same-connection close/retirement from racing that interval. Existing tests serialized the entire exchange and could not expose a close-before/stale-dispatch ordering.

For a fail-closed authority boundary, this cannot be left as an implicit caller convention.

## Correction

Commit `49e69c02fe2ded0b9607ccb4090c21cde96b8a1c` corrects the boundary without weakening the accepted transport:

- `dispatch` now receives `(OwnerPipeServer&, slot, frame, response)` and derives the Host-owned session from the transport slot rather than accepting a session argument;
- dispatch and close share one dispatcher lifecycle mutex, intentionally serializing this Batch 000 layer globally in line with the initial global single-writer/read-serialization policy;
- if close wins first, the slot is retired before the gate opens and a later stale frame cannot resolve a transport session or acquire authority;
- if dispatch wins first, successful Acquire and active-lease tracking complete before close can perform authority cleanup and retirement;
- a deterministic regression reads an Acquire frame, closes/retires the connection before dispatch, then proves the stale frame is rejected and broker authority remains Ready;
- the architecture document makes this lifecycle ownership explicit;
- scope/intent audit metadata is explicitly recorded as a still-open Batch 000 requirement rather than silently claimed complete.

The same correction commit also removes qiven-host automatic push/pull-request CI triggers, restores manual `workflow_dispatch` semantics from ADR-0005, and requires an exact `expected_sha` checked before expensive validation. Updating the branch did not create a new push-trigger CI run.

## Current disposition

`49e69c...` is the current Host dispatcher correction candidate. It has completed exact remote semantic/delta review but is **not accepted yet**. It requires a manually dispatched `full` CI run bound to `expected_sha=49e69c02fe2ded0b9607ccb4090c21cde96b8a1c`.

If exact CI passes, perform one final exact-identity review and accept/reject this dispatcher checkpoint. Acceptance of this checkpoint does not accept all Host Batch 000 and does not re-enable mutating DCR. ADR-0029 recovery and remaining Batch 000 requirements, including bounded scope/intent audit metadata, remain outstanding; Batch 001 production no-bypass remains the DCR re-enable boundary.
