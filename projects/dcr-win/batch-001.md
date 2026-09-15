# Qiven DCR Windows — Phase 1 / Batch 001

Status: **ACTIVE DESIGN TARGET**

## Objective

Bootstrap the `qiven-dcr-win` product repository and implement the smallest headless native Windows supervisor skeleton that proves exact process-generation ownership and asynchronous stdout/stderr draining with synthetic fixtures.

Batch 001 is not the full DCR client. It establishes the runtime substrate that later batches will use around the official `@wonderwhy-er/desktop-commander remote` implementation.

## Language and build boundary

- C++20.
- Native Windows APIs are allowed directly at this product boundary.
- CMake + Ninja/MSVC follow the established Qiven Windows toolchain conventions.
- Adopt the current Qiven Devkit managed surface from repository bootstrap rather than inventing repository-local orchestration conventions.
- Do not add a general threading/networking subsystem to `qiven-foundation` in this batch.
- Do not create `qiven-runtime` or `qiven-net` merely to make the first implementation look abstract.

## Required runtime skeleton

The first executable is headless. A minimal console/test harness is acceptable for development, but no interactive console window is allowed to become the final lifecycle dependency.

Implement product-local concepts equivalent to:

```text
Supervisor
  -> ProcessGeneration
       -> Windows Job Object
       -> owned child process tree
       -> stdout pipe reader
       -> stderr pipe reader
       -> lifecycle/state events
```

The implementation must preserve exact generation identity across restart boundaries.

## Process ownership

The supervisor creates the child process itself and records the exact process-generation identity.

Use a Windows Job Object, or a stricter equivalent demonstrated by tests, so teardown targets only descendants belonging to the owned generation. Prefer `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` for the synthetic-fixture milestone while still implementing an orderly stop path before forced teardown.

Never enumerate and kill generic `node.exe`, `cmd.exe`, PowerShell, or Terminal processes by name.

## Pipe model

Create stdout and stderr pipes before launch and drain both concurrently.

Pipe readers must not call UI code and must not synchronously depend on disk flushing. Batch 001 may use a simple bounded test sink; the production byte-budgeted UI/disk fan-out belongs to Batch 002.

A synthetic child that produces enough output to fill ordinary OS pipe buffers must still complete when the supervisor is healthy.

## State model

Batch 001 must materialize at least:

```text
stopped
starting
running
stopping
faulted
```

The richer DCR-facing states (`authenticating_or_connecting`, `ready`, `degraded`, `recycle_pending`, `restarting`) remain Batch 002 work because they require the real official client and resource/liveness policy.

State transitions must be explicit and testable. Process exit is data; it must not be inferred from lack of log output.

## Cancellation and shutdown

The supervisor owns an explicit stop request.

Normal stop sequence:

1. request orderly child shutdown when the fixture/protocol supports it;
2. wait a bounded grace period;
3. close/terminate the owned generation if it does not exit;
4. drain/close pipes deterministically;
5. publish the terminal state and exit code/reason.

No infinite shutdown wait is allowed.

## Synthetic fixture

Add a purpose-built test child executable rather than using arbitrary shell commands as the primary acceptance fixture.

The fixture must support deterministic modes including:

- clean exit with chosen exit code;
- periodic stdout;
- periodic stderr;
- high-rate stdout/stderr;
- no-newline giant output chunks;
- sleep/hang until terminated;
- spawn-one-child mode to prove Job Object descendant ownership.

The fixture is test infrastructure, not production behavior.

## Batch 001 acceptance

A candidate head is acceptable only when automated tests demonstrate:

- exact child creation and generation identity;
- stdout and stderr are drained concurrently;
- a high-output fixture does not deadlock on pipe backpressure;
- fixture exit code is reported truthfully;
- orderly stop works;
- forced stop after grace timeout is bounded;
- descendant fixture processes are terminated with the owned generation;
- unrelated processes are untouched;
- repeated start/stop cycles do not reuse stale generation state;
- repository Debug and Release validation pass under the established Qiven local validation path;
- diff-check and clean-tree gates pass.

## Explicit non-goals

Batch 001 does **not** implement:

- Supabase/Auth/Realtime protocol compatibility;
- native DCR transport;
- DCR session authentication;
- production log rotation;
- production memory watchdog thresholds;
- automatic DCR restart/recycle policy;
- Win32 tray/window UI;
- Windows service installation;
- startup persistence;
- host configuration repair;
- generic cross-platform process abstraction.

## Batch 002 handoff

Batch 002 wraps the real official DCR client with the Batch 001 process substrate and implements the canonical `supervisor-resource-contract.md`: byte-bounded observability, memory pressure, bounded restart/backoff, real health/liveness dimensions, deterministic environment injection, and DCR-specific lifecycle states.