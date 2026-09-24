# Qiven DCR Windows — Phase 1 / Batch 001

Status: **ACTIVE — LOWER-LAYER PLACEMENT CORRECTION**

## Objective

Establish the smallest correct native runtime substrate required by the DCR Windows supervisor, then make `qiven-dcr-win` consume that substrate rather than owning generic process/runtime machinery itself.

Batch 001 is not the full DCR client. It proves exact Windows process-generation ownership, concurrent stdout/stderr draining, bounded stop semantics, and deterministic synthetic fixtures at their correct semantic layer before DCR-specific lifecycle policy is built above them.

This batch follows `ADR-0024` and `collaboration/software-engineering-philosophy.md`: correct downward semantic ownership outranks cosmetic repository independence or a product-local-first staging strategy.

## Layer placement gate

Before further product implementation, classify every required primitive:

- Foundation owns genuinely foundational vocabulary and primitives: types, contracts, checked arithmetic, platform boundaries, and any native-resource ownership primitive whose semantics are stable and broadly lower-level.
- Runtime owns generic process execution/supervision semantics: process generations, child-tree ownership, bounded stop, pipe draining, lifecycle observation, and only the synchronization/timer/cancellation primitives concretely required to express those contracts.
- `qiven-dcr-win` owns DCR-specific policy: official-client launch/environment, DCR health/liveness, recycle/backoff, DCR logging/observability policy, and UI.
- Networking remains a separate lower semantic concern and is not implemented in Batch 001 unless the batch acquires a concrete network requirement.

A generic capability must not remain in `qiven-dcr-win` merely because it was first discovered there.

## Dependency direction

The intended native direction for this milestone is:

```text
OS / standard library
    -> qiven-foundation
    -> qiven-runtime
    -> qiven-dcr-win
```

If the placement audit demonstrates that a small primitive belongs directly in Foundation, implement and validate it there first. Generic process supervision must not be exposed as a DCR product API.

Lower-layer changes are part of the current product objective when they are required for correct ownership. Keep each addition narrowly tied to the concrete Batch 001 contract; do not speculatively complete a general runtime framework.

## Language and build boundary

- C++20.
- Windows is the first proven backend for the runtime process contract.
- Native Windows APIs are allowed behind the lower-layer implementation boundary.
- CMake + MSVC follow established Qiven Windows toolchain conventions.
- Qiven Devkit managed surfaces remain the repository engineering baseline.
- Lower dependencies are resolved as existing source dependencies with exact CI integration pins; do not use network CMake fetching.

## Required runtime substrate

The lower runtime layer must provide concepts equivalent to:

```text
ProcessGeneration
    -> exact generation identity
    -> owned child process tree
    -> stdout drain
    -> stderr drain
    -> explicit exit/result observation
    -> bounded graceful/forced stop
```

On Windows, Job Objects are the preferred ownership primitive for the first backend. The root process should be placed under ownership before normal execution continues so descendants cannot escape the intended generation because of a launch race.

The contract must not enumerate and kill generic `node.exe`, `cmd.exe`, PowerShell, Terminal, or other unrelated processes by name.

## Pipe and resource model

Create stdout and stderr pipes before launch and drain both concurrently.

Readers must not synchronously depend on UI rendering or disk flushing. The runtime process layer may expose bounded observation data/callbacks required by its contract, but DCR-specific disk rotation and UI history belong above it.

A synthetic child that produces enough output to fill ordinary OS pipe buffers must still complete when the runtime is healthy. Tests must not retain or print the entire synthetic payload merely to prove drainage.

## State and result model

Generic runtime state must be explicit and testable. At minimum the process-generation contract distinguishes inactive/starting/running/stopping/terminal-or-faulted semantics without inferring exit from silence.

DCR-facing states such as `authenticating_or_connecting`, `ready`, `degraded`, `recycle_pending`, and `restarting` remain product policy for Batch 002.

Process exit code, forced termination, launch failure, wait failure, and pipe-drain failure are distinct observable facts and must not be collapsed into success/failure booleans when the distinction changes caller behavior.

## Cancellation and shutdown

Normal stop sequence is bounded:

1. request orderly child shutdown when the child protocol supports it;
2. wait a configured grace period;
3. terminate only the owned generation if it does not exit;
4. drain/close pipes and native resources deterministically;
5. publish terminal result/state truthfully.

No infinite shutdown wait is allowed.

## Synthetic fixture

Use a purpose-built test child executable rather than arbitrary shell commands as the primary acceptance fixture.

Fixture modes include clean chosen exit code, stdout/stderr output, simultaneous high-rate dual-stream output, no-newline giant output, orderly-stop cooperation, hang-until-terminated, and descendant spawning.

The fixture is test infrastructure, not production behavior.

## Batch 001 acceptance

A candidate stack is acceptable only when automated tests demonstrate:

- lower-layer semantic placement has been reviewed against ADR-0024;
- exact child creation and generation identity;
- stdout and stderr drain concurrently without pipe deadlock;
- high-output and giant-no-newline fixtures remain byte-bounded in observer memory;
- exit code/result is truthful;
- orderly stop works;
- forced stop after grace timeout is bounded;
- descendants are terminated with the owned generation;
- unrelated processes are untouched;
- repeated start/stop cycles do not reuse stale generation state;
- `qiven-dcr-win` consumes the lower runtime contract instead of carrying a duplicate generic implementation;
- lower dependency and product repositories pass their required Debug/Release local validation;
- consumer CI pins lower-layer integration to exact accepted SHAs;
- diff-check and clean-tree gates pass.

## Explicit non-goals

Batch 001 does **not** implement Supabase/Auth/Realtime compatibility, native DCR transport, production log rotation, final memory-watchdog thresholds, DCR-specific restart/recycle policy, Win32 tray/window UI, Windows service installation, startup persistence, host repair, or speculative cross-platform runtime completeness.

## Migration of the initial product-local spike

The initial `qiven-dcr-win` product-local `ProcessGeneration` implementation is evidence, not architecture. Reuse algorithms/tests where they already express the accepted contract, but move generic runtime semantics to the correct lower owner rather than polishing the product-local copy into a permanent API.

Do not preserve code merely because it already compiles. Preserve only semantics and tests that survive the placement correction.

## Batch 002 handoff

Batch 002 wraps the real official DCR client using the accepted lower runtime substrate and implements the DCR-specific supervisor resource contract: byte-bounded observability, memory pressure, bounded restart/backoff, real health/liveness dimensions, deterministic DCR environment injection, and DCR-specific lifecycle states.