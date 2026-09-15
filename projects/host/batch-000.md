# Qiven Host — P0 / Batch 000 — Single-Writer Authority and Fencing Freeze

## Objective

Design, implement, and validate the minimum JasonPC-resident broker that makes concurrent AI/MCP execution fail closed before any normal product development resumes.

This batch is an authority-integrity batch, not a general remote-execution framework. Success means a duplicated, delayed, retried, or concurrently rendered upstream execution flow cannot produce two local writers or an ambiguous local authority state.

## Required architecture

The broker must expose one owner-scoped local IPC authority endpoint and enforce one active Qiven transaction globally.

Each transaction carries:

- unique execution id;
- opaque lease id;
- persistent monotonic fencing epoch;
- strictly increasing request sequence;
- idempotency/replay identity;
- bounded scope/intent metadata.

The broker must be single-instance on JasonPC and must own every child process it launches through a Windows Job Object. Direct filesystem/Git/process mutation through the production Qiven transport must not bypass the broker after acceptance.

## Required state machine

```text
ready
  -> leased
  -> ready          explicit normal completion
  -> reconciling    disconnect / uncertain completion
  -> quarantined    competing authority / stale fencing / protocol violation

reconciling|quarantined
  -> ready          explicit reconciliation only
```

No timeout may silently convert uncertainty into availability.

## Collision semantics

A second execution identity appearing while another lease is active must:

1. be rejected immediately;
2. never enter a normal FIFO queue for later mutation;
3. record a bounded collision event;
4. cause the broker to quarantine new work from both flows;
5. preserve/observe already-owned child work to a safe boundary;
6. require reconciliation before authority reopens.

The broker optimizes integrity over availability.

## Persistence and restart

The fencing epoch must survive broker restart. A lease or request from an earlier epoch must remain stale after restart even if the remote caller later reconnects.

Persistent state must be minimal, crash-safe, and owner-scoped. The implementation must not depend on a large mutable database merely to provide fencing.

## Journal

Record enough bounded evidence to reconcile uncertain operations:

- broker epoch and transaction/lease identity;
- request sequence and idempotency key/digest;
- operation category and bounded target metadata;
- process/job identity for spawned work;
- repository path plus pre/post branch, HEAD, and clean/dirty fingerprint when Git state is relevant;
- start/completion/failure/quarantine transitions;
- result digest/status.

Do not persist credentials, private-key material, bearer tokens, complete environment dumps, or unbounded stdout/stderr.

## Initial Windows boundary

The first accepted implementation targets JasonPC Windows only. It should run in the project owner's normal interactive security context, use owner-restricted local IPC, use a named mutex or equivalent OS primitive to enforce broker singleton ownership, and use Job Objects for process trees.

Do not introduce LocalSystem/elevated-service authority merely to make implementation easier.

## Relationship to Runtime and DCR

`qiven-runtime` remains the semantic owner of generic process execution. The broker may consume Runtime when the required accepted baseline exists; it must not move authority/fencing semantics into Runtime merely because it spawns processes.

`qiven-dcr-win` remains transport supervision/product policy. DCR or a future transport must call the broker rather than mutate JasonPC directly.

## Batch acceptance

Acceptance requires a real JasonPC test harness proving all of the following:

1. Broker singleton: a second broker instance cannot become active.
2. Exclusive lease: two independent clients racing to acquire authority produce exactly one lease holder.
3. Collision quarantine: the losing client is rejected and the broker quarantines subsequent work until explicit reconciliation.
4. Fencing: an old epoch cannot execute after lease replacement or broker restart.
5. Sequence: duplicate, skipped, reordered, or replayed mutation requests are rejected deterministically.
6. Uncertain disconnect: transport loss with possible in-flight work enters reconciliation rather than ready.
7. Child containment: descendants remain in the owned Job and forced cleanup cannot escape the generation boundary.
8. Repository evidence: a synthetic Git mutation records truthful pre/post identity and cannot run concurrently with another transaction.
9. Bypass test: the production DCR/Qiven execution path used for acceptance has no alternate direct mutating MCP route around the broker.
10. Split-brain dogfood: two deliberately concurrent caller processes simulating duplicated Chat response branches attempt mutations; at most one transaction can mutate, and the host ends either in a proven ready state or explicit quarantine—never ambiguous success.
11. Restart recovery: broker restart preserves fencing monotonicity and recovery state.
12. Output discipline: journal and broker memory remain bounded under large child output; payload retention is not the authority mechanism.

## Validation boundary

Until this batch is accepted, DCR remains read-only for incident forensics. The initial broker bootstrap and local validation must use the project owner's trusted foreground Windows path rather than unfenced DCR mutation.

No Devkit/native-build-system, Runtime, DCR Windows, or CAD implementation resumes before the authority-plane acceptance is complete and the incident-contaminated/incomplete worktrees have been reconciled.

## Stop condition

Stop Batch 000 when host-side single-writer/fencing acceptance passes and mutating DCR can be re-enabled only through the broker. Do not expand this batch into scheduling, multi-user tenancy, generalized RPC, distributed consensus, or remote orchestration.