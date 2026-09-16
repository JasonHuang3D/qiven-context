# Host Local Named-Pipe Transport Acceptance — 2026-09-16

## Scope

This acceptance closes the isolated Host Phase 0 / Batch 000 local named-pipe transport checkpoint. It does not accept protocol dispatch, protected operations, Runtime/DCR production adapters, recovery, or production no-bypass integration.

## Accepted baseline and candidate

Accepted predecessor:

- `4aca5b12031e0b9c2677738f67c929cb0bfa687d` — competing Host-session Acquire correction; exact CI `35057116028` PASS.

Accepted transport head:

- `8e5b9dec64bf739af84e981df12afc1969599738` — `test(host): bound pipe reuse connect race`.

The transport head is six commits ahead of `4aca5b12031e0b9c2677738f67c929cb0bfa687d` and adds the local-pipe transport implementation, architecture contract, and acceptance tests.

## Semantic acceptance

Qiven-v6 semantic review accepted the transport design and implementation against the handoff requirements. The accepted checkpoint establishes:

- owner-SID-scoped local Windows named-pipe endpoint with explicit owner-only DACL and remote-client rejection;
- exactly four pre-created V1 server instances as a hard resource bound;
- overlapped server/client pipe I/O rather than unbounded synchronous blocking I/O;
- explicit bounded deadlines for accept/read/write, with production default currently 5 seconds and narrower test deadlines;
- exact outstanding-operation cancellation using `CancelIoEx` on timeout, followed by completion drain before stack-owned `OVERLAPPED` storage is destroyed;
- Host-generated per-connection nonzero 128-bit `BrokerSessionId` retained server-side and excluded from protocol frames;
- `Retiring` lifecycle that preserves an accepted Host session after transport loss until future authority-side disconnect/reconciliation has been handled;
- fail-closed `Poisoned` lifecycle when clean disconnect/reuse cannot be proven;
- bounded protocol-frame reads/writes with oversized-message rejection and no partial publication;
- a 20-second CTest-level fuse so a future deadlock becomes an explicit test failure instead of an indefinitely running CI job;
- regression coverage for saturation, retirement/reuse, fresh session identity, peer disconnect, silent-client timeout, and poisoned-slot behavior;
- bounded client retry for the pipe-reuse connection race at the accepted head.

The checkpoint remains transport-only. It does not call `AuthorityBroker::disconnect` and does not interpret/dispatch protocol messages.

## Historical rejected evidence

- `d556587900fb5323bcb7316f519ba90a09e17979` / run `35057883517`: Windows Debug test-harness compile failure; not accepted.
- `e0ce63742034f20c71d24e9ee2d4078e220553bb` / run `35058068291`: synchronous-I/O design reached a non-terminating Windows Debug CTest and the run was cancelled; not accepted.

Those failures directly motivated the bounded overlapped-I/O design.

## Exact CI evidence

Accepted exact run:

- repository: `JasonHuang3D/qiven-host`
- branch: `jason-brother/host-batch-000`
- run: `35060483714`
- workflow: `CI / full`
- exact head SHA: `8e5b9dec64bf739af84e981df12afc1969599738`
- conclusion: `success`

Jobs accepted from that exact run:

- Validation plan — PASS
- Windows MSVC x64 — PASS, Debug build/test + Release build/test
- Linux GCC x64 — PASS, Debug build/test + Release build/test
- macOS AppleClang arm64 — PASS, Debug build/test + Release build/test
- CI Gate — PASS

The project owner explicitly accepted the Qiven-v6 semantic review before this record was written.

## Result

`8e5b9dec64bf739af84e981df12afc1969599738` plus exact run `35060483714` is the accepted Host local named-pipe transport checkpoint.

The immediate next isolated checkpoint is protocol dispatcher + protected `NoOp`, including authority-side use of the preserved Host-owned transport session and truthful disconnect/reconciliation handoff. Mutating DCR remains suspended; Host Phase 0 / Batch 001 remains the production no-bypass gate.
