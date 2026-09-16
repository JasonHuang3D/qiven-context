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

## Accepted local named-pipe transport checkpoint

The owner-only local Windows transport is accepted at exact Host head `8e5b9dec64bf739af84e981df12afc1969599738`. Exact GitHub Actions run `35060483714` passed Windows MSVC, Linux GCC, and macOS AppleClang in Debug and Release plus CI Gate. The repository was public and the workflow used only standard GitHub-hosted runner labels (`windows-2022`, `ubuntu-24.04`, `macos-15`).

The accepted head is six linear commits ahead of authority checkpoint `4aca5b12031e0b9c2677738f67c929cb0bfa687d`; exact compare changes only `CMakeLists.txt`, the Host architecture index, the local-pipe architecture contract, the local-pipe API/implementation, and its Windows acceptance test. No `AuthorityBroker`, protocol-dispatch implementation, Runtime/DCR adapter, filesystem/Git/process side effect, or recovery surface was added by this checkpoint.

### Security and identity

The endpoint is owner-scoped by current-user SID and uses an explicit protected DACL containing only the owner allow ACE. Every server instance rejects remote clients. The server pre-creates four bounded pipe instances and uses `FILE_FLAG_FIRST_PIPE_INSTANCE` on the first instance as endpoint defense in depth; `BrokerInstanceGuard` remains the canonical process singleton.

Each successful connection receives a fresh nonzero 128-bit `BrokerSessionId` from the Windows system-preferred CSPRNG. Session identity is Host-owned transport state and is never parsed from normal protocol frames. Connected, retiring, and poisoned sessions participate in collision checks. The future dispatcher must inject this exact Host-owned identity into `AuthorityBroker` calls out-of-band from decoded messages.

### Bounded peer-controlled I/O

The rejected synchronous transport proved that a bounded count of four slots is not sufficient when a peer can cause `ConnectNamedPipe`, `ReadFile`, or `WriteFile` to wait indefinitely. The accepted transport therefore creates server and client handles for overlapped I/O. Server accept/read/write and client read/write take explicit deadlines; the current production default is five seconds and tests may use narrower deadlines.

On timeout the exact outstanding operation is cancelled with `CancelIoEx`. The implementation handles the `ERROR_NOT_FOUND` completion race by re-reading completion before waiting. Because `OVERLAPPED` storage is stack-owned, an operation that remains pending after cancellation request is drained to kernel completion before the storage leaves scope. This is a bound on peer-controlled waiting, not a hard real-time guarantee under an arbitrarily failed Windows kernel or NPFS implementation. Do not overstate that distinction in future design or documentation.

The Windows local-pipe CTest has an independent 20-second timeout as an acceptance-harness liveness fuse. A future deadlock therefore becomes explicit failed-test evidence rather than an indefinitely running CI job; that fuse does not substitute for transport deadlines.

### Retiring and Poisoned ownership

Once Host publishes a session identity, transport failure cannot erase it. Timeout, disconnect, oversized input, empty message, or read/write failure first attempts to establish a cleanly disconnected native pipe state. A proven clean disconnect enters `Retiring` while preserving the exact `BrokerSessionId`. The future dispatcher must perform authority-side disconnect/reconciliation using that session before explicitly retiring and reusing the slot.

If native disconnect/reuse safety cannot be proven, the slot enters `Poisoned`. A poisoned slot preserves and exposes any published session identity for authority cleanup but rejects further I/O, accept, and retirement; it remains unavailable until server replacement. This deliberately sacrifices bounded capacity rather than reusing an OS object in an uncertain state.

### Acceptance-test findings and rejected heads

The path to the accepted head is itself useful negative knowledge:

- `d556587900fb5323bcb7316f519ba90a09e17979`, exact CI `35057883517`: first transport candidate; Windows Debug test compilation failed because the test omitted its local `inspect()` helper. Core transport compiled. Rejected.
- `e0ce63742034f20c71d24e9ee2d4078e220553bb`, exact CI `35058068291`: helper restored; Windows Debug `ctest` failed to terminate and the project owner cancelled the run. This falsified synchronous blocking transport despite bounded slot count. Rejected.
- `53bd8bb491aab94565e336a667580f3f3ea6f3f5`, exact CI `35059631796`: overlapped/deadline redesign plus 20-second CTest fuse; Windows local-pipe test now failed explicitly at the fuse rather than hanging the workflow. Rejected.
- `d5f8a5c6ae0d60dd2a03a351f2c0d57d0bf42523`, exact CI `35060003192`: corrected `CancelIoEx(ERROR_NOT_FOUND)` completion-race handling; broad stage markers localized the remaining failure to retire/reuse. Rejected.
- `659d2df44d28839547c0da89bb484971894dc90b`, exact CI `35060217069`: finer markers proved the replacement client `CreateFile` returned before the test stalled. Rejected as acceptance evidence, but it exposed test orchestration rather than product I/O as the remaining problem.
- `8e5b9dec64bf739af84e981df12afc1969599738`, exact CI `35060483714`: Windows acceptance harness now treats transient `ERROR_PIPE_BUSY` during a test-created reuse race with a test-only one-second bounded retry and uses explicit `ExitProcess(3)` diagnostics instead of CRT `abort()`. Production `connect_owner_pipe_client()` still returns `busy` immediately and does not queue or retry. Windows Debug/Release then passed the complete local-pipe acceptance alongside Linux/macOS and CI Gate. Accepted.

The accepted Windows tests cover protected owner-only DACL, duplicate-server rejection, bounded no-client accept timeout, four simultaneous accepted sessions, distinct nonzero Host session identities, fifth-client saturation, bounded frame exchange, oversized-message non-publication, Retiring session preservation and explicit reuse, peer-disconnect preservation, silent-client timeout, and injected invalid-handle poisoning with published-session preservation.

See `MEM-20260916T054300Z-2E8C47` for the durable liveness/session-preservation invariant.

## Immediate next engineering step

Continue Batch 000 from exact accepted Host checkpoint `8e5b9dec64bf739af84e981df12afc1969599738` with protocol dispatch + protected `NoOp` as a separate checkpoint.

The dispatcher must consume a successfully decoded normal-protocol message while injecting the transport-owned `BrokerSessionId` out-of-band. It must map QueryStatus, Acquire, operation admission/completion, Release, and connection loss to the already accepted `AuthorityBroker` semantics. Protected `NoOp` execution must occur outside the authority mutex after durable admission and before durable completion. A transport disconnect or timeout must use the preserved session to drive authority-side disconnect/reconciliation before the pipe slot is retired. Competing connections must remain able to reach authority logic so a different Host session deterministically quarantines rather than being serialized away at transport acceptance.

Normal IPC still must not expose `Reconcile`. Do not add Runtime/DCR production adapters, arbitrary filesystem/Git/process mutation, production child-process execution, or the Windows Hello/WebAuthn recovery ceremony in this checkpoint.

Batch 000 acceptance still does not re-enable mutating DCR. Batch 001 remains the production no-bypass gate.