# Qiven Runtime

Status: **ACTIVE DEPENDENCY WORK FOR DCR WINDOWS BATCH 001**.

## Mission

`qiven-runtime` owns shared native execution-runtime semantics that are lower than products and higher than Qiven Foundation.

It exists so products do not own or duplicate generic process/thread/timer/cancellation machinery merely because a product is the first place a requirement appeared.

The initial consumer is `qiven-dcr-win`, but the repository boundary is justified by semantic ownership, not consumer count.

## Initial dependency direction

```text
OS / C++ standard library
    -> qiven-foundation
    -> qiven-runtime
    -> qiven-dcr-win
```

Foundation provides foundational vocabulary, contracts, checked arithmetic/conversions, platform boundaries, and accepted low-level primitives. Runtime owns higher execution semantics. DCR owns DCR-specific policy.

## Phase 0 / Batch 001 — Process runtime substrate

The first Runtime batch is deliberately narrow. It implements and tests:

- exact process-generation identity;
- owned child-process-tree lifetime;
- concurrent stdout/stderr byte drainage;
- truthful launch/wait/exit status;
- bounded graceful/forced stop;
- deterministic native-resource cleanup;
- a Windows backend using `CreateProcessW`, Job Objects, and pipes;
- synthetic fixtures for high output, giant no-newline output, hangs, chosen exit codes, and descendants.

The first serious implementation must follow `collaboration/software-engineering-philosophy.md` and ADR-0024/ADR-0025. Reuse evidence from the initial DCR product-local spike, but do not preserve product-local namespace/API ownership.

## Foundation placement audit

Before finalizing Runtime implementation, inspect every lower primitive used by the process subsystem. If a primitive is intrinsically foundational and stable—rather than merely convenient to Runtime—implement and validate it in `qiven-foundation` first.

Likely audit subjects include owned native-handle lifetime, checked native-width conversions, and platform compile-time boundaries. This list is not permission to expand Foundation speculatively.

## Non-goals for the first batch

The first batch does not implement a general scheduler, coroutine runtime, thread pool, networking, TLS, WebSocket, IPC framework, plugin system, DCR policy, logging UI, or cross-platform support claims.

Threading/cancellation/timer APIs enter Runtime only when the concrete process or later networking contract requires them.

## Windows-first, not Windows-only architecture

Only the Windows backend is implemented and accepted initially because DCR Windows is the current consumer. Public semantics should avoid unnecessary Win32 leakage where a stable portable concept is already clear, but no Linux/macOS capability is claimed until CI continuously builds and tests it.

## Integration law

`qiven-runtime` resolves Foundation as an existing source dependency and pins CI integration to an exact accepted Foundation commit. `qiven-dcr-win` similarly pins Runtime to an exact accepted Runtime commit.

Network fetching during CMake configure is not part of the accepted dependency path.

## Acceptance handoff to DCR

DCR Batch 001 may resume product-level implementation only after the required Runtime process contract passes its Debug/Release validation and remote review, and the DCR repository consumes that exact accepted Runtime baseline without a duplicate generic process implementation.