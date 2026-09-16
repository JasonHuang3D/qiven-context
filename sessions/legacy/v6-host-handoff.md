# Qiven v6 Host Handoff

This document is maintained by the **Qiven-v5** Chat session for the next Qiven-v6 cold boot. `collaboration/v5-host-handoff.md` is historical input to the current v5 session and is frozen except for explicit historical correction. See `collaboration/session-ci-handoff-contract.md`.

At cold boot, never treat this file as a permanent pin for live repository state. Resolve `qiven-context/main`, `state/current.md`, `state/active-work.yaml`, the live Host branch, and exact CI evidence before mutation.

## Canonical baseline inherited by v5

The accepted Host architecture remains ADR-0026, ADR-0027, and ADR-0029. ADR-0028 owns Native Build System layering. Mutating DCR / remote AI execution remains suspended until Host Phase 0 / Batch 001 proves that the production mutation path cannot bypass Host.

The exact accepted Host stack inherited into this session is:

1. `7d7ff602affacd1839fbcf19709e4f2e326fe680` — AuthorityState semantics.
2. `b1d1d28199c02b1d3d21fc3995ba0ec8c194f56d` — durable FenceStore; exact CI `35018685694` PASS.
3. `59ca1fa1bf9106b3b5cff5feef060957e825b75c` — bounded durable journal; exact CI `35021345295` PASS.
4. `888062f3042c6c39c6419d515c4a86405d1140ea` — owner-scoped Windows broker singleton; exact CI `35021873826` PASS.
5. `2faecefb9f9e9b3c983eccc2e5a12836fc2f5a8e` — accepted broker persistence orchestration; exact CI `35054237070` PASS.
6. `be3a22e7b90381b17451a10c5ed52d526c2d2a9d` — bounded V1 protocol codec; exact CI `35055543391` PASS.
7. `4aca5b12031e0b9c2677738f67c929cb0bfa687d` — competing Host-session Acquire correction; exact CI `35057116028` PASS. Different Host-owned `BrokerSessionId` is competing authority even if caller-controlled `ExecutionId` is copied; rejected competing Acquire durably quarantines, while same-session/same-execution duplicate Acquire remains Leased and returns `concurrent_execution`.

## Qiven-v5 session rules added after takeover

### Session handoff ownership

Qiven-vX maintains vX+1 handoff material. Current live progress belongs here in v6, not in the historical v5 handoff.

### CI cost boundary

`JasonHuang3D/qiven-host` was changed from private to public during Qiven-v5 and live repository metadata confirmed public visibility. Qiven repositories that require routine CI should be public by default so long as making them public is truthful and acceptable for the project.

Routine CI must remain zero-incremental-cost by default. GitHub currently documents standard GitHub-hosted runners as free and unlimited for public repositories. Larger/GPU/custom-image runners remain billable even for public repositories and require an explicit billing review before use. Re-verify current GitHub billing docs when runner labels or billing-relevant configuration changes.

### Hanging CI cancellation

A CI run with concrete liveness evidence may be cancelled proactively. Record exact run/SHA/stuck step and classify the outcome as cancellation due to the identified or suspected hang; never reinterpret it as PASS or generic test failure.

During the local-pipe checkpoint, exact run `35058068291` at Host head `e0ce63742034f20c71d24e9ee2d4078e220553bb` was cancelled by the project owner after Windows Debug `ctest` remained stuck. The run is historical failure evidence, not acceptance evidence.

The current GitHub connector surface used by jason-brother exposes run inspection, logs, and rerun actions but does not currently expose an exact-run cancel action. If a future connector surface exposes safe cancellation, jason-brother may directly cancel a confirmed hanging run under the contract above; otherwise state the tool boundary.

## Local named-pipe transport checkpoint — current status

The accepted base for transport work remains `4aca5b12031e0b9c2677738f67c929cb0bfa687d`.

An initial transport implementation `d556587900fb5323bcb7316f519ba90a09e17979` added owner-only Windows named-pipe transport, four bounded slots, Host-owned per-connection `BrokerSessionId`, Retiring lifecycle, and fail-closed Poisoned semantics for an untrustworthy pipe instance. Its first exact CI run `35057883517` failed in Windows Debug compile because the Windows transport test called a missing local `inspect()` helper. The core transport library itself compiled; the failure was test-harness-only.

A narrow test-only correction `e0ce63742034f20c71d24e9ee2d4078e220553bb` restored that helper. Linux/macOS passed, and Windows compiled past the previous failure, but Windows Debug `ctest` then failed to terminate and run `35058068291` was cancelled. Do **not** accept `d5565879...` or `e0ce6374...` as the transport checkpoint.

The hang exposed a stronger architectural defect: a fixed four-slot pool bounds handle/session count but synchronous blocking `ConnectNamedPipe`, `ReadFile`, and `WriteFile` do not bound time or slot occupation. A local client can connect and indefinitely withhold a complete message, permanently consuming a transport slot. This violates the Host liveness/resource contract even if memory and handle counts are bounded.

## Immediate next engineering step

Replace synchronous local-pipe I/O with bounded cancellable Windows overlapped I/O before accepting transport:

- create server/client handles for overlapped operation;
- give `accept`, `read`, and `write` an explicit bounded deadline, with a production default and narrower test deadline;
- on deadline, cancel the exact outstanding operation with `CancelIoEx` and drain completion before stack-owned `OVERLAPPED` storage is destroyed;
- preserve an already-issued Host session through `Retiring` after read/write timeout or disconnect so the future dispatcher can perform authority-side disconnect/reconciliation before slot reuse;
- retain `Poisoned` for native states where safe disconnect/reuse cannot be proven; a poisoned slot must not be washed back to Listening by `retire()`;
- ensure the acceptance harness itself uses bounded/overlapped raw I/O so tests cannot manufacture their own unbounded wait;
- add a silent-client regression proving a connected client that sends no complete message cannot block Host indefinitely.

Keep this checkpoint transport-only. Do not add protocol dispatch, production Runtime/DCR adapters, arbitrary filesystem/Git/process side effects, normal-protocol `Reconcile`, or recovery ceremony yet. After exact semantic review plus Windows/Linux/macOS Debug/Release CI PASS, record the accepted transport head here and advance to dispatcher + protected `NoOp`.

Batch 000 acceptance still does not re-enable mutating DCR. Batch 001 remains the production no-bypass gate.