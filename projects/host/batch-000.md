# Qiven Host — Phase 0 / Batch 000 — Authority Kernel

## Objective

Implement and validate Host's own authority semantics independently of future Runtime and DCR production integration.

## Owned acceptance boundary

Batch 000 proves a single owner-local Windows broker instance; one globally serialized execution lease; durable monotonic fencing; strict sequence and bounded idempotency; fail-closed quarantine and explicit reconciliation; crash-aware recovery; bounded journal; versioned bounded named-pipe IPC; and a narrow protected-operation gate.

The state model is `ready -> leased -> ready`, with uncertainty entering `reconciling` and competing authority or protocol/fencing violations entering `quarantined`. Neither timeout nor restart silently returns uncertain authority to ready. A competing client can reach the state machine while accepted work runs because arbitrary protected work executes without holding the authority-state mutex.

Deterministic core tests and real Windows multiprocess tests must cover singleton exclusion, racing acquisition, quarantine, stale fences across replacement and restart, sequence/replay behavior, disconnect uncertainty, in-flight collision, synthetic split-brain, malformed bounded IPC, journal bounds, restart recovery, and repeated lifecycle. Record acquire, no-op request, release, startup/recovery, and steady-state memory observations.

## Excluded integration

Batch 000 has no dependency on `qiven-runtime` and contains no production process supervision, Git, filesystem, or DCR adapter. Test orchestration and deterministic protected test operations are not production adapters. Production closed-path/no-bypass proof belongs to Batch 001.

## Safety gate

Passing Batch 000 does not re-enable mutating DCR or remote AI execution. The trusted owner-local path remains the only bootstrap path until Batch 001 passes.

## Recovery authority

Normal IPC does not expose Reconcile. A separate recovery surface accepts only challenge, assertion, and status messages. Only a current one-shot Windows Hello/WebAuthn assertion with required user verification may authorize `AbandonPriorAuthorityAndAdvanceFence`, durably advancing generation and fence before Ready while preserving prior uncertainty and journal evidence. Automated tests use a cryptographically faithful interface implementation; final JasonPC acceptance requires a real Windows Hello ceremony.
