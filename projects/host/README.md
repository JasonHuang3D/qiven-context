# Qiven Host

`qiven-host` is the JasonPC-resident execution-authority plane for AI-driven local engineering.

It exists because transport reachability is not authority. DCR, a future native transport, Work, Chat, or another MCP client may carry a request to JasonPC, but none of them may directly decide that the machine is free to execute it.

The host boundary is deliberately transport-independent:

```text
AI caller / orchestration
        -> transport
        -> qiven-host authority broker
        -> runtime / filesystem / Git adapters
        -> Windows
```

## Core invariant

At most one Qiven execution transaction may hold JasonPC authority at a time.

This is stronger than a process mutex. Every transaction has a unique execution identity, opaque lease, monotonic fencing epoch, and strict request sequence. A stale or competing caller cannot continue merely because it still has a live network connection or an old token.

The initial broker serializes reads and writes. Read concurrency may be introduced only after snapshot/isolation semantics prove that observation cannot race mutation and mislead engineering decisions.

## Failure posture

Ambiguity fails closed. A competing authority does not wait in a normal queue; it causes explicit rejection and quarantine. Transport loss does not release authority automatically. Broker restart does not make an old lease valid again.

The broker owns only local execution authority and recovery evidence. It does not own product architecture, Git merge/release authority, DCR protocol policy, or generic process semantics.

- generic process execution belongs to `qiven-runtime`;
- DCR-specific lifecycle/health/UI belongs to `qiven-dcr-win`;
- shared build/engineering mechanism belongs to Devkit;
- architecture/release authority remains with the project owner and jason-brother contract.

## Acceptance layers

- Phase 0 / Batch 000 accepts the transport-independent Authority Kernel using deterministic core and real local multiprocess tests.
- Phase 0 / Batch 001 integrates accepted Runtime and DCR production paths and proves production mutation cannot bypass Host.

Validation architecture follows semantic ownership just like code: a lower-layer batch proves only facts available at that layer. Batch 000 cannot re-enable mutating DCR; remote mutation remains suspended until Batch 001 passes and canonical state explicitly lifts the gate.
