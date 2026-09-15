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

The earlier worker preservation branch `jason-worker/host-authority-kernel-batch-000` and WIP head `4a40a249c657b64564e41dfc2ab6735d73d3657e` remain historical evidence only. Do not resume from that FenceStore prototype; the direct-development stack above supersedes it for current implementation work.

## Proven Batch 000 layers

### AuthorityState

The kernel owns explicit `Ready`, `Leased`, `Reconciling`, and `Quarantined` phases; opaque execution/lease/operation/session identities; persistent generation and fencing epoch; strict request sequence and replay/idempotency semantics; competitor quarantine; disconnect reconciliation; and recovery as abandonment of prior authority plus fence advancement rather than a claim that uncertain work did not execute.

### FenceStore

The accepted persistence layer uses explicit fixed-width serialization and a two-slot internal storage revision separate from authority generation/fence. Windows durability uses `CreateFileW`, write-through intent, `WriteFile`, `FlushFileBuffers`, close, and read-back verification. A never-created root is `not_initialized`; an already-created root without a valid durable slot is `corrupt` and fails closed. CRC32 is corruption detection only, not authentication.

### BoundedJournal

The journal is bounded evidence rather than the authority source of truth. It retains two fixed-capacity segments, each with 64 fixed-width records; total retained file bytes are hard-bounded at 34,976. Records carry bounded identity digests, generation/fence/request sequence, event/outcome, a previous-record digest, SHA-256 integrity chaining, and CRC corruption detection. Rotation continuity and retained-history corruption fail closed. Wall-clock fields are diagnostic only.

### BrokerInstanceGuard

The Windows singleton is owner-scoped using `Global\\QivenHost.Broker.<SID>`. It uses named-object existence and guard-handle lifetime rather than mutex thread ownership. A second broker deterministically receives `already_running`; it is not admitted or queued. This singleton constrains broker-process multiplicity only; lease/fencing/sequence/quarantine remain separate execution-authority mechanisms. It does not claim protection against arbitrary malicious code with unrestricted same-user control.

## qiven-devkit prerequisite

- Validated Native Build System candidate branch: `jason-worker/native-build-system-0.2.0-closeout`.
- Exact candidate: `b39c449731bd23c5df150b3edb526b40272f424f`.
- Worker reported FULL validation PASS and clean tree before push.
- Direct Host development exposed a lower-owner CI-template defect: the generated workflow used a job-level `if:` expression that referenced `matrix.id` before the matrix context was available. The corrective Devkit branch is `jason-brother/native-build-system-0.2.0-ci-fix`; both cpp-app and cpp-library workflow templates were changed to explicit platform jobs. That Devkit fix is still a candidate and has not yet received exact FULL Devkit validation/merge acceptance.

## Direct-remote takeover and turn budget

`jason-worker` is no longer the primary owner of the long Host Batch 000 implementation loop. Repeated `USAGE_BUDGET_SOFT_STOP` and `RUN_LIMIT_REACHED` outcomes established that Work is a bounded local execution worker, not a reliable owner of a long multi-checkpoint engineering batch.

For the remainder of Host Batch 000, jason-brother should prefer direct GitHub-native implementation and exact remote review where the work is remote-native. JasonPC-only ceremonies or validation remain a separate trusted-owner step because mutating DCR is still forbidden. Do not use Desktop Commander mutation to bootstrap Host merely to avoid this restriction.

The project owner observed the same roughly 26-minute long-turn cutoff during direct GitHub-native remote development with no DCR execution in the turn. This weakens the hypothesis that DCR causes the cutoff. Treat the boundary as a Chat/tool-turn execution-window constraint for engineering purposes, while keeping the underlying product mechanism unproven. Create durable checkpoints continuously and target coherent checkpoint completion before approximately 20-22 minutes. See `MEM-20260915T135800Z-6B0D8A`.

## Connector write fallback

Direct GitHub writes may occasionally be rejected by connector safety/policy classification even when the intended Qiven canonical record is legitimate project documentation. Do not preserve connector success by euphemizing, omitting, or weakening material engineering semantics. State the tool boundary and move the authoring operation to a trusted local Work/owner path, then exact-review the pushed result. If that path is unavailable, generate the exact Markdown or patch for the project owner as the final reliable authoring fallback. This does not permit bypassing a policy that actually forbids the underlying content. See `MEM-20260915T203423Z-C4A912` and `collaboration/operating-contract.md`.

## Immediate next engineering step

Continue from exact Host checkpoint `888062f3042c6c39c6419d515c4a86405d1140ea` with broker orchestration and persistence ordering before adding normal IPC. The broker should own one primary in-process mutex, `AuthorityState`, `FenceStore`, and `BoundedJournal`, but must not hold the authority mutex across an arbitrary protected operation.

The next contract must explicitly handle partial durability rather than pretending FenceStore and BoundedJournal form one atomic filesystem transaction. If a durable admission/transition write succeeds and a later required durable write fails, the broker must fail closed and reject further authority until restart/recovery can reconcile persistent evidence. Restart must conservatively restore persisted `Ready` as `Ready`, but a persisted `Leased` state cannot resurrect its old ephemeral lease and should become durably `Reconciling`; persisted `Reconciling` and `Quarantined` remain fail-closed. An admitted protected operation whose terminal result is not durably known remains uncertain; absence of client success never proves the operation did not execute.

After broker orchestration, continue with the bounded protocol codec, owner-only local named-pipe transport, protected test operations, crash/failure injection, recovery authority, and full synthetic split-brain acceptance. Before implementing ADR-0029's real Windows Hello/WebAuthn recovery ceremony, re-verify the native Windows API contract and consent semantics; do not force WebAuthn if it cannot faithfully bind a trusted local recovery action and required user verification.

Batch 000 acceptance still does not re-enable mutating remote execution. Batch 001 remains the production Runtime/DCR integration and no-bypass gate.
