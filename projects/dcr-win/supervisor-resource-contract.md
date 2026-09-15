# Qiven DCR Windows — V1 Supervisor Resource Contract

Status: **Batch 000 provisional contract**. Hard invariants are architectural requirements; numeric thresholds are initial test values and may change with evidence.

## Purpose

V1 supervises the existing official `@wonderwhy-er/desktop-commander remote` runtime. It does not reinterpret DCR as an autonomous agent and does not own engineering objectives, validation scope, merge authority or release decisions.

The supervisor exists to put explicit Windows process, output, memory, disk and UI bounds around the official client while preserving truthful failure behavior.

## Hard invariants

### Exact process ownership

The supervisor owns one DCR process generation at a time and must identify the exact process tree it created. Lifecycle operations target that generation only.

Do not stop generic `node.exe`, `cmd.exe`, PowerShell or Terminal processes by executable name. On Windows the implementation should prefer an owned Job Object or an equivalently exact process-tree primitive, with graceful shutdown attempted before forced teardown.

A new restart creates a new generation identity. Events and diagnostics must retain the generation ID so output from different generations cannot be conflated.

### Pipe draining is independent of UI

DCR stdout and stderr are redirected away from an interactive console dependency and drained continuously.

A slow, blocked, hidden or closed UI must never stop pipe consumption. UI rendering is a subscriber to observability data, not the consumer that keeps transport execution alive.

Pipe-reader code must not synchronously wait for UI painting, disk flush, network work, or user interaction.

### Every in-memory queue is byte-bounded

No log/event/UI queue may be bounded only by item count, because a single item can be arbitrarily large.

Every queue has an explicit byte budget and an overflow policy. Overflow must increment an observable dropped/coalesced-byte/event counter; silent unbounded growth is forbidden.

Protocol result integrity must never depend on a human-display queue retaining every byte.

### Diagnostic logging is not protocol authority

Console/stdout text is diagnostic evidence. It is not the canonical source for tool-call completion, validation success, device identity or release authority.

The supervisor may parse diagnostic output for hints and presentation, but must not fabricate success when the actual bounded execution path is unavailable or ambiguous.

### Resource pressure is a state, not an excuse to lie

Soft resource pressure transitions the generation to an observable degraded/recycle-pending state.

A hard host-protection threshold may terminate the owned generation to protect JasonPC. If that interrupts an in-flight operation, the externally visible result is interrupted/failed/unavailable. It is never converted to success because the supervisor later restarted.

### Restart is bounded

Automatic recovery must have a bounded retry/backoff policy. A crash loop must converge to `faulted`, not an infinite autonomous repair loop.

The human CMD fallback remains valid when the supervisor or official DCR client cannot establish a trustworthy execution path.

## Lifecycle state model

The V1 supervisor exposes at least these states:

```text
stopped
starting
authenticating_or_connecting
ready
degraded
recycle_pending
restarting
stopping
faulted
```

`ready` requires more than a live parent PID. Process liveness, local-MCP availability and remote DCR liveness are separate health dimensions.

A stale control-plane `online` value is not sufficient readiness evidence. A recent successful ping or bounded execution result is stronger evidence when available.

## Output pipeline

The preferred flow is:

```text
child stdout/stderr
  -> always-drained OS pipes
  -> bounded ingestion chunks
  -> bounded diagnostic event stream
       -> bounded UI ring
       -> bounded rotating disk sink
       -> counters/health metrics
```

The disk writer and UI must not share a backpressure path with the child pipes.

If a diagnostic sink cannot keep up, the supervisor preserves transport/process liveness first, records explicit loss counters, and sheds diagnostic history according to the configured policy.

## Provisional V1 budgets

These values are initial engineering defaults for the first native supervisor tests, not immutable architecture.

### UI history

- retained human-visible payload budget: **4 MiB** total;
- oversized individual entries may be truncated/coalesced for display while retaining byte/drop counters;
- the UI should prefer recent state and recent lines over old scrollback.

### Disk diagnostics

- rotate at approximately **16 MiB** per file;
- retain at most **8 files** per active profile/generation family, approximately **128 MiB** total before metadata overhead;
- rotation is byte-based and must handle one logical line larger than a rotation target;
- local diagnostic logs are short-retention operational data, not a durable business record.

### Internal supervisor queues

- each queue must declare its own byte cap;
- initial aggregate queued diagnostic payload target: **8 MiB or less** outside the UI ring;
- high-water marks, dropped bytes and dropped/coalesced events must be queryable.

### Memory pressure

At `ready`, capture a per-generation baseline working set for the remote-device and local-MCP roles after startup settles.

Initial policy:

- **soft pressure:** a critical child remains roughly **128 MiB above its ready baseline** for at least 15 seconds;
- soft pressure sets `degraded`/`recycle_pending` and requests recycle at a conservative idle boundary;
- **hard pressure:** a critical child reaches approximately **512 MiB working set**, or the owned DCR generation shows another explicit host-protection condition;
- hard pressure permits immediate generation termination/restart with truthful interruption semantics.

The 128/512 MiB values are deliberately provisional. The retention probe showed an isolated official `TerminalManager` process at about 304 MiB RSS after approximately 105 MiB of completed output history, while a fresh live local-MCP process was about 97 MiB working set. The first implementation must make these thresholds configurable and measurable.

## Conservative idle boundary

V1 cannot assume that parsing human console text proves no tool call is active.

Until a stronger machine-readable activity signal is available, automatic soft-pressure recycle must use a conservative conjunction such as:

- no known DCR-launched descendant work process;
- no recent stdout/stderr activity for a configured quiet window;
- no supervisor lifecycle transition already in progress;
- remote/local health state is stable enough to perform an orderly restart.

The first test value for the quiet window is **60 seconds**.

This is an operational heuristic, not protocol truth. A future machine-readable activity signal should replace it when available.

## Restart/backoff policy

Initial automatic restart behavior should be bounded to a small crash-recovery window, for example:

- immediate first restart after an unexpected process loss;
- then jittered delays that grow across subsequent failures;
- after **3 failed startup/recovery attempts within 10 minutes**, enter `faulted` and require explicit human/Qiven action.

Normal intentional recycle after a healthy idle boundary does not count as a crash-loop failure.

## Environment contract

The supervisor launches the official client with deterministic environment repair required by the accepted JasonPC contract.

For Git/SSH-capable DCR children, `ProgramData=C:\ProgramData` remains mandatory until upstream environment propagation is proven fixed. Canonical tool paths and noninteractive credential controls remain unchanged.

The supervisor must not mutate host PATH, registry, SSH keys, Git identity, Clash configuration, Visual Studio installation, or `C:\Env` to repair a failed launch.

## Security and data-retention boundary

DCR diagnostic output can contain command arguments, file excerpts and tool results. Therefore local diagnostic retention is potentially sensitive.

The product must not upload supervisor logs to a third party merely for convenience. Log files stay local unless the project owner explicitly chooses another destination.

The UI and diagnostic logs should expose enough context for debugging while avoiding duplicate long-term retention of large payloads that already belong to another authoritative artifact.

## Acceptance tests for V1

Before the first transport milestone is complete, tests must demonstrate all of the following with synthetic fixtures before equivalent live-DCR validation:

- a fake child can emit output much faster than the UI consumes without blocking the child;
- UI retained bytes never exceed the configured ring budget;
- disk logs rotate and total retained bytes remain bounded;
- a single giant line cannot bypass byte caps;
- stdout and stderr are drained concurrently;
- soft memory pressure becomes observable `recycle_pending` without killing active synthetic work;
- hard memory pressure produces truthful interruption and bounded restart;
- crash loops reach `faulted` after the configured retry budget;
- restart kills only the owned process generation;
- closing the UI does not terminate or stall transport unless the user explicitly chooses Exit;
- device/process health can distinguish parent-process liveness from proven remote/local readiness;
- the accepted qiven-context exact-head validation workflow succeeds through the supervised official client.

## Extraction rule

Threading, bounded queues, pipe I/O, process supervision, timers and networking discovered here remain product-local until another real Qiven consumer demonstrates the same stable semantics.

Do not create generic Foundation/runtime abstractions solely to satisfy this first product. Reuse is earned by repeated evidence.