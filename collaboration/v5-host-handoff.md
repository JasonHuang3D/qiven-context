# Qiven v5 Host Handoff

This checkpoint exists so a fresh Chat session can resume Host Phase 0 / Batch 000 without relying on prior-conversation memory. At cold boot, resolve the live `qiven-context/main` ref rather than treating any self-recorded Context SHA as permanently current.

## Canonical cognition baseline

- Accepted Host architecture is ADR-0026, ADR-0027, and ADR-0029.
- Native Build System ownership is ADR-0028.
- Mutating DCR / remote AI execution remains suspended until Host Batch 001 proves the production closed path cannot bypass Host.
- `state/active-work.yaml` is the active execution pointer; this handoff records the durable remote implementation stack and the evidence needed to continue it.

## qiven-host remote state

Repository: `JasonHuang3D/qiven-host` (private).

Remote `main` intentionally remains the generated bootstrap `b3191735baa19c81db7da095ded1ac04f8116925`. Batch 000 is not complete and no Host merge to `main` is authorized merely because intermediate layers pass CI.

The active direct-development branch is `jason-brother/host-batch-000`. Its exact proven semantic stack is:

1. `7d7ff602affacd1839fbcf19709e4f2e326fe680` — `host: establish authority kernel semantics`.
2. `b1d1d28199c02b1d3d21fc3995ba0ec8c194f56d` — `host: add durable fence store`, parent exactly `7d7ff602...`; exact CI run `35018685694` passed Windows MSVC, Linux GCC, and macOS AppleClang in Debug and Release plus CI Gate.
3. `59ca1fa1bf9106b3b5cff5feef060957e825b75c` — `host: add bounded durable journal`, parent exactly `b1d1d281...`; exact CI run `35021345295` passed Windows/Linux/macOS Debug and Release plus CI Gate.
4. `888062f3042c6c39c6419d515c4a86405d1140ea` — `host: enforce owner-scoped broker singleton`, parent exactly `59ca1fa1...`; exact CI run `35021873826` passed Windows/Linux/macOS Debug and Release plus CI Gate. The Windows test includes a real eight-process acquisition race and proves exactly one accepted broker instance while the winner remains alive.
5. `2faecefb9f9e9b3c983eccc2e5a12836fc2f5a8e` — accepted broker-persistence orchestration head, parent chain `888062f... -> 7e13bbbc1526a65c2ebd87c37fb6af6751ebca60 -> 2faecefb...`; exact CI run `35054237070` passed Windows MSVC, Linux GCC, and macOS AppleClang in Debug and Release plus CI Gate. `7e13bbbc...` introduced the orchestration layer but is not the accepted checkpoint by itself: exact remote semantic review found that a wrong-session `Release` could move in-memory authority to `Quarantined` while its rejection path failed to persist that stronger phase. Correction `2faecefb...` persists rejection-induced phase changes before journaling the rejection and adds a Windows restart test proving `Quarantined` survives broker replacement.
6. `be3a22e7b90381b17451a10c5ed52d526c2d2a9d` — `host: add bounded protocol codec`, parent exactly `2faecefb...`; exact CI run `35055543391` passed Windows MSVC, Linux GCC, and macOS AppleClang in Debug and Release plus CI Gate. Pre-publication semantic review rejected an earlier unreferenced draft that exposed client-selected `BrokerSessionId`; the accepted checkpoint removes session identity from the wire and reserves it for Host-owned transport/session binding.

The earlier worker preservation branch `jason-worker/host-authority-kernel-batch-000` and WIP head `4a40a249c657b64564e41dfc2ab6735d73d3657e` remain historical evidence only. Do not resume from that FenceStore prototype; the direct-development stack above supersedes it for current implementation work.

## Proven Batch 000 layers

### AuthorityState

The kernel owns explicit `Ready`, `Leased`, `Reconciling`, and `Quarantined` phases; opaque execution/lease/operation/session identities; persistent generation and fencing epoch; strict request sequence and replay/idempotency semantics; competitor quarantine; disconnect reconciliation; and recovery as abandonment of prior authority plus fence advancement rather than a claim that uncertain work did not execute.

The broker-orchestration checkpoint also strengthened operation completion authority at the natural owner: `AuthorityState::complete` now authenticates the original broker session, execution, lease, fence, sequence, operation identity, and digest before consuming an admitted request. An original owner may finish an already-admitted operation to its safe boundary after a competitor has forced `Quarantined`; a competing caller cannot steal completion authority.

### FenceStore

The accepted persistence layer uses explicit fixed-width serialization and a two-slot internal storage revision separate from authority generation/fence. Windows durability uses `CreateFileW`, write-through intent, `WriteFile`, `FlushFileBuffers`, close, and read-back verification. A never-created root is `not_initialized`; an already-created root without a valid durable slot is `corrupt` and fails closed. CRC32 is corruption detection only, not authentication.

### BoundedJournal

The journal is bounded evidence rather than the authority source of truth. It retains two fixed-capacity segments, each with 64 fixed-width records; total retained file bytes are hard-bounded at 34,976. Records carry bounded identity digests, generation/fence/request sequence, event/outcome, a previous-record digest, SHA-256 integrity chaining, and CRC corruption detection. Rotation continuity and retained-history corruption fail closed. Wall-clock fields are diagnostic only.

### BrokerInstanceGuard

The Windows singleton is owner-scoped using `Global\\QivenHost.Broker.<SID>`. It uses named-object existence and guard-handle lifetime rather than mutex thread ownership. A second broker deterministically receives `already_running`; it is not admitted or queued. This singleton constrains broker-process multiplicity only; lease/fencing/sequence/quarantine remain separate execution-authority mechanisms. It does not claim protection against arbitrary malicious code with unrestricted same-user control.

### AuthorityBroker persistence orchestration

`AuthorityBroker` composes one primary in-process authority mutex, `AuthorityState`, `FenceStore`, and `BoundedJournal` without pretending the two durable stores form an atomic transaction. Fresh bootstrap requires both durable substrates to be absent; a later start that observes only one initialized substrate fails closed as inconsistent persistence. Persisted `Ready` restores as `Ready`; persisted `Leased` cannot resurrect its ephemeral lease and is durably converted to `Reconciling`; persisted `Reconciling` and `Quarantined` remain fail-closed.

Acquire persists `Leased` before returning a usable lease. Operation admission is durably journaled before it is exposed as admitted. Terminal operation evidence is journaled before a later release can return durable authority to `Ready`. Normal release first records an uncertain transition while durable state remains `Leased`, then persists `Ready`, then records successful transition completion; failure before the durable Ready write restarts conservatively from `Leased -> Reconciling`, while failure after a required durable write latches the running broker closed. Reconciling/quarantine transitions persist the fail-closed authority state before relying on journal evidence.

A rejected request is not assumed to leave authority unchanged. Exact review of `7e13bbbc...` caught a rejection path where wrong-session release had already changed `AuthorityState` to `Quarantined`; accepted correction `2faecefb...` compares pre/post phase and persists the stronger fail-closed state before returning the rejection. See `MEM-20260916T040700Z-D8A4C2`.

The authority mutex covers validation and required durable authority transitions only. Future protected test-operation execution remains outside that mutex between admission and completion so a competing flow can reach authority state and force quarantine while work is in flight. The broker checkpoint does not yet implement the protected operation itself.

### Bounded protocol codec

The accepted V1 normal-protocol codec follows ADR-0009 rather than serializing C++ object layout. It uses a 16-byte explicit header, `QVH0` family magic, protocol version 1, explicit message kind and payload length, little-endian fixed-width integers, exact per-message payload sizes, and a hard 256-byte total frame cap. Encoding and decoding use caller-owned fixed storage and do not allocate heap memory.

Normal V1 message kinds are only Acquire, ExecuteTestOperation, Release, and QueryStatus request/response pairs. `Reconcile` does not exist in this codec. Frames with bad magic, unsupported version, unknown kind, nonzero reserved bytes, wrong exact payload size, trailing bytes, invalid enum/boolean values, noncanonical padding, zero required identities, or zero required fence/sequence values are rejected before publication. Typed decode uses a candidate object and leaves caller output unchanged on failure.

`BrokerSessionId` is intentionally absent from every client wire message. Session identity protects same-connection ownership in `AuthorityState`; therefore the future owner-only transport/dispatcher must assign a fresh nonzero Host-owned session identity to each accepted connection and inject it into `AuthorityBroker` calls separately from decoded application messages. A stale or competing client must not be able to copy a session value from its application payload. See `MEM-20260916T042800Z-B71E3C`.

Acquire carries a caller execution identity plus bounded printable-ASCII scope/intent metadata, but the client does not choose a lease; a successful response returns a Host-issued opaque lease plus generation and fence. Execute carries execution/lease/fence/sequence/operation identity and currently only `NoOp`; replay digest is not caller-selected and must later be derived by the dispatcher from the canonical decoded request. Release carries execution/lease/fence. QueryStatus has an empty request and bounded status response. Stable protocol result codes are distinct from internal `AuthorityError`, broker, persistence, or native error enums.

## qiven-devkit prerequisite

- Validated Native Build System candidate branch: `jason-worker/native-build-system-0.2.0-closeout`.
- Exact candidate: `b39c449731bd23c5df150b3edb526b40272f424f`.
- Worker reported FULL validation PASS and clean tree before push.
- Direct Host development exposed a lower-owner CI-template defect: the generated workflow used a job-level `if:` expression that referenced `matrix.id` before the matrix context was available. The corrective Devkit branch is `jason-brother/native-build-system-0.2.0-ci-fix`; both cpp-app and cpp-library workflow templates were changed to explicit platform jobs. That Devkit fix is still a candidate and has not yet received exact FULL Devkit validation/merge acceptance.

## Direct-remote takeover and turn budget

`jason-worker` is no longer the primary owner of the long Host Batch 000 implementation loop. Repeated `USAGE_BUDGET_SOFT_STOP` and `RUN_LIMIT_REACHED` outcomes established that Work is a bounded local execution worker, not a reliable owner of a long multi-checkpoint engineering batch.

For the remainder of Host Batch 000, jason-brother should prefer direct GitHub-native implementation and exact remote review where the work is remote-native. JasonPC-only ceremonies or validation remain a separate trusted-owner step because mutating DCR is still forbidden. Do not use Desktop Commander mutation to bootstrap Host merely to avoid this restriction.

The project owner observed the same roughly 26-minute long-turn cutoff during direct GitHub-native remote development with no DCR execution in the turn. This weakens the hypothesis that DCR causes the cutoff. Treat the boundary as a Chat/tool-turn execution-window constraint for engineering purposes, while keeping the underlying product mechanism unproven. Create durable checkpoints continuously and target coherent checkpoint completion before approximately 20-22 minutes. See `MEM-20260915T135800Z-6B0D8A`.

A green CI result is not itself checkpoint acceptance for authority code. The broker-orchestration work demonstrated why: the first orchestration head compiled and tested across the existing suite, but exact semantic review still found a crash/restart persistence omission on a rejected transition. Remote review must explicitly inspect fail-closed state changes, durable ordering, and restart interpretation before accepting an exact CI-proven head.

Protocol review adds the same lesson at a different boundary: an earlier codec draft was mechanically valid but put `BrokerSessionId` on the untrusted wire. It was rejected before branch publication. Authority identities must remain owned by the layer that can truthfully establish them; codec cleanliness and green tests do not make a caller-asserted transport identity trustworthy.

## Connector write fallback

Direct GitHub writes may occasionally be rejected by connector safety/policy classification even when the intended Qiven canonical record is legitimate project documentation. Do not preserve connector success by euphemizing, omitting, or weakening material engineering semantics. State the tool boundary and move the authoring operation to a trusted local Work/owner path, then exact-review the pushed result. If that path is unavailable, generate the exact Markdown or patch for the project owner as the final reliable authoring fallback. This does not permit bypassing a policy that actually forbids the underlying content. See `MEM-20260915T203423Z-C4A912` and `collaboration/operating-contract.md`.

## Immediate next engineering step

Continue from exact Host checkpoint `be3a22e7b90381b17451a10c5ed52d526c2d2a9d` with the owner-only bounded Windows named-pipe transport/session lifecycle as its own checkpoint before protected-operation dispatch.

The transport must keep its resource model bounded, reject remote clients, apply an owner-scoped local security boundary, and create a fresh nonzero Host-owned `BrokerSessionId` for each accepted connection. Session identity is not parsed from protocol frames. The transport design must preserve enough bounded concurrent connection capacity for a genuine second contender to reach later authority dispatch; do not hide split-brain by serializing all connection acceptance outside the authority state machine. Disconnect semantics must preserve the same Host-owned session identity so later dispatcher integration can move an active lease to reconciliation rather than silently release it.

This transport checkpoint must not add normal-protocol `Reconcile`, Runtime/DCR production adapters, arbitrary filesystem/Git/process side effects, or the real Windows Hello/WebAuthn recovery ceremony. After transport/session lifecycle is proven, continue with protocol dispatch + protected `NoOp`, crash/failure injection, recovery authority, and full synthetic split-brain acceptance.

Batch 000 acceptance still does not re-enable mutating remote execution. Batch 001 remains the production Runtime/DCR integration and no-bypass gate.
