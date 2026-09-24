# Qiven v7 Host Handoff

This document is maintained by the **Qiven-v6** Chat session for the next Qiven-v7 cold boot. `collaboration/v6-host-handoff.md` is historical input to the current v6 session and is frozen except for explicit historical correction. See `collaboration/session-ci-handoff-contract.md`.

At cold boot, never treat this file as a permanent pin for live repository state. Reconcile `qiven-context/main`, `state/active-work.yaml`, the live Host branch, repository visibility, and exact CI evidence before mutation.

## Qiven-v6 takeover result

Qiven-v6 cold boot recovered the Qiven-v5 Host work from live GitHub state rather than replaying or continuing the prior Chat-side CI wait.

`JasonHuang3D/qiven-host` is live as a public repository. The active branch `jason-brother/host-batch-000` had advanced beyond the v6 handoff to exact head:

- `8e5b9dec64bf739af84e981df12afc1969599738` — `test(host): bound pipe reuse connect race`.

Exact GitHub Actions run `35060483714` for that SHA completed successfully with Validation plan, Windows MSVC x64 Debug/Release, Linux GCC x64 Debug/Release, macOS AppleClang arm64 Debug/Release, and CI Gate all passing.

The project owner explicitly accepted the Qiven-v6 semantic review. Therefore the accepted Host stack is now:

1. `7d7ff602affacd1839fbcf19709e4f2e326fe680` — AuthorityState semantics.
2. `b1d1d28199c02b1d3d21fc3995ba0ec8c194f56d` — durable FenceStore; exact CI `35018685694` PASS.
3. `59ca1fa1bf9106b3b5cff5feef060957e825b75c` — bounded durable journal; exact CI `35021345295` PASS.
4. `888062f3042c6c39c6419d515c4a86405d1140ea` — owner-scoped Windows broker singleton; exact CI `35021873826` PASS.
5. `2faecefb9f9e9b3c983eccc2e5a12836fc2f5a8e` — broker persistence orchestration; exact CI `35054237070` PASS.
6. `be3a22e7b90381b17451a10c5ed52d526c2d2a9d` — bounded V1 protocol codec; exact CI `35055543391` PASS.
7. `4aca5b12031e0b9c2677738f67c929cb0bfa687d` — competing Host-session Acquire correction; exact CI `35057116028` PASS.
8. `8e5b9dec64bf739af84e981df12afc1969599738` — bounded owner-only Windows named-pipe transport/session lifecycle; exact CI `35060483714` PASS.

Acceptance evidence is recorded in `evidence/audits/host-local-pipe-transport-acceptance-2026-09-16.md`.

## Transport invariants now accepted

The accepted transport uses owner-SID-scoped protected local named pipes, exactly four V1 server instances, overlapped bounded accept/read/write, explicit deadlines, exact `CancelIoEx` cancellation with completion drain, Host-owned per-connection `BrokerSessionId`, Retiring preservation until authority cleanup, fail-closed Poisoned handling when reuse cannot be proven, bounded protocol-sized message I/O, and a test-level timeout fuse.

The transport remains intentionally ignorant of protocol meaning and does not itself call `AuthorityBroker::disconnect`.

## Qiven Chat control-plane incident

The Qiven-v5 thread became unavailable to the project owner across ChatGPT Web, Windows, and iOS while the session was performing CI status waiting/polling. The owner reported that OpenAI support could not cancel the affected thread. The upstream internal mechanism is unknown and must not be invented.

Qiven-v6 therefore made the following cross-session rules mandatory in `collaboration/session-ci-handoff-contract.md`:

- Chat-side CI polling loops are forbidden;
- after CI dispatch, at most one immediate exact-identity status read may occur in the same turn;
- if still queued/in-progress, return exact repo/run/SHA/state and stop waiting;
- non-CI repeated external-state observation defaults to at most three total attempts/observations and 60 seconds wall-clock waiting in one turn, whichever comes first;
- transient API/network retries consume the same budget.

Incident evidence is preserved in `evidence/audits/qiven-v5-chat-polling-availability-incident-2026-09-16.md`.

## Immediate next engineering step

Advance Host Phase 0 / Batch 000 to **protocol dispatcher + protected `NoOp`** as the next isolated checkpoint.

The dispatcher checkpoint must consume the already accepted transport and codec rather than weakening or duplicating them. It should:

- accept one complete bounded transport frame from a Connected slot;
- validate/decode through the accepted V1 codec;
- inject the exact Host-owned `BrokerSessionId` out-of-band into authority calls rather than accepting session identity from the wire;
- route `Acquire`, protected `NoOp`, `Complete`/release semantics, and disconnect handling only as required by the frozen Batch 000 authority contract;
- preserve strict sequence/idempotency and fencing semantics already owned by `AuthorityBroker`;
- on transport loss/timeout, consume the preserved Retiring session and perform authority-side disconnect/reconciliation before allowing slot retirement/reuse;
- keep malformed/unauthorized messages fail-closed and never partially dispatch a prefix;
- keep normal IPC free of owner recovery / `Reconcile` ceremony;
- keep arbitrary filesystem/Git/process mutation and Runtime/DCR production adapters out of this checkpoint.

The protected `NoOp` is the first end-to-end proof that a decoded local request passes through Host transport, Host-owned session identity, authority admission/fencing, protected-operation lifecycle, response encoding, and cleanup without gaining arbitrary mutation capability.

After exact semantic review plus Windows/Linux/macOS Debug/Release CI PASS, record that checkpoint and continue Batch 000. Mutating DCR remains suspended until Batch 001 Production Authority Integration proves the production path cannot bypass Host.
