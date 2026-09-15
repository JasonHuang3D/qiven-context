# Qiven DCR Windows

Status: **ACTIVE PRODUCT TRACK — Phase 0 / Batch 000**.

## Product objective

Provide a stable Windows execution-transport client for Qiven so long-running Chat/Work development can drive JasonPC without depending on an unbounded foreground console, without repetitive human CMD relay turns, and without allowing transport/logging failure to become a product-development bottleneck.

The product is transport infrastructure with a concrete product completion boundary. It is not an autonomous engineering agent and does not receive product, validation-scope, merge, or release authority.

## Roadmap position

Qiven DCR Windows is inserted ahead of CAD because it directly improves the reliability and interaction throughput of every later product line. After the first transport milestone is complete, the roadmap resumes with CAD / floor-plan to semantic 3D, then industrial-gas management, robotics/simulation, and deeper native physics.

## Phase 0 / Batch 000 — Protocol + Failure Model Freeze

Before implementation, freeze the observed execution contract, protocol questions, and failure model. Batch 000 produces architecture and acceptance evidence, not a speculative networking framework.

Required reconnaissance includes:

- current official `@wonderwhy-er/desktop-commander remote` process tree and local MCP bridge;
- remote WebSocket/session endpoint behavior, authentication/device registration, heartbeat, reconnect and version semantics to the extent they are observable without weakening security;
- message framing/correlation and the boundary between protocol data and diagnostic stdout/stderr;
- child-process environment propagation, including the accepted `ProgramData=C:\ProgramData` repair for Windows OpenSSH;
- lifecycle states: starting, connected, degraded, reconnecting, stopping, stopped and failed;
- stale control-plane `online` state versus proven liveness by ping or successful bounded execution;
- Chat UI/backend execution decoupling: a UI send failure does not imply already-dispatched tool calls stopped;
- log flood, backpressure, memory growth, disk growth, slow UI, child-process hang, network loss and crash/restart behavior.

## V1 — Native Windows supervisor

The first implementation should supervise the existing official Node/NPM DCR client rather than immediately reimplement its wire protocol. The supervisor owns:

- exact child process-tree lifetime and graceful restart/stop;
- deterministic environment injection and canonical tool paths;
- asynchronous stdout/stderr draining;
- bounded in-memory queues and bounded UI history;
- rotating/spooled disk logs with explicit retention limits;
- health, heartbeat and connection-state observation;
- truthful exit/result propagation;
- a minimal native Win32 UI/tray surface for state, current activity, recent events and lifecycle control.

Transport must never block on human-visible logging. UI rendering may coalesce or drop display updates when overloaded, but execution/result integrity and durable logging policy must remain explicit.

## V2 — Native transport

A native WebSocket/session implementation is allowed only after Batch 000 reconnaissance demonstrates a sufficiently understood and testable protocol contract. V2 removes the supervised Node transport only when compatibility, reconnect, authentication, framing and failure semantics can be validated independently.

## Runtime and Foundation boundary

Do not move a general threading or networking framework into `qiven-foundation` merely because this product needs one. Implement product-local runtime/network behavior first. Extract a shared `qiven-runtime`, `qiven-net`, or a small Foundation primitive only when multiple real consumers demonstrate stable shared semantics and the dependency/ownership/failure-cost laws are satisfied.

Likely product-local concepts include cancellation, deadlines/timers, bounded queues, process supervision, asynchronous pipe draining, session state machines and network I/O. Their eventual repository placement is evidence-driven.

## Completion boundary for the first product milestone

Stop transport-first work and return to CAD when all of the following are true:

- JasonPC can remain available to Qiven without a human-managed scrollback-heavy console being the lifecycle dependency;
- large/continuous child output cannot cause unbounded client memory growth;
- log storage and UI history have explicit tested bounds;
- disconnect/reconnect and graceful restart behavior are observable and deterministic;
- the accepted Git/SSH and local validation workflows pass through the client with truthful exact-head evidence;
- the existing human CMD path remains a viable fallback;
- the client does not acquire autonomous engineering or release authority.

## Evidence

See `evidence/audits/dcr-acceptance-2026-09-15.md`, `MEM-20260915T092000Z-3C7A41`, and `ADR-0023`.