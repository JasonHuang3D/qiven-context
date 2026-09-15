# Concurrent MCP / Chat Response Split-Brain Incident — 2026-09-16

## Severity

P0 / disaster-class execution-authority incident.

The project owner observed ChatGPT render two answer choices for one interaction and both choices concurrently execute against the same JasonPC DCR/MCP capability. Qiven had explicitly intended a single active execution flow; the host transport did not enforce that invariant.

This audit records the project-observable facts. It does **not** claim knowledge of the upstream ChatGPT internal mechanism that created the two UI choices.

## Immediate response

All product implementation was frozen. JasonPC was treated as forensic/read-only:

- no reset;
- no checkout for cleanup;
- no commit;
- no `git clean`;
- no branch repair;
- no local qiven-context write;
- no attempt to resume Devkit/Runtime/DCR implementation.

GitHub-native qiven-context recording remained permitted because it does not mutate JasonPC.

## DCR state after freeze

A read-only DCR session check reported no active terminal sessions.

A process inventory did not show obvious surviving Git/CMake/Python engineering children. Several Node/CMD processes remained consistent with the active DCR process tree, but process names alone were not treated as proof of ownership.

DCR recent-tool history can enumerate local tool calls but does not carry a stable caller/assistant-response identity that distinguishes two competing Chat response branches. Therefore the current transport cannot reconstruct authoritative per-branch ownership after a split-brain event.

That absence is itself a material finding: post-hoc chronology is not a substitute for host-side fencing.

## Repository snapshot observed read-only

A read-only status sweep observed:

- `qiven-context`: local `main` at historical `a0e67f950bb9bc5060a5d4f08c40d6204ae8c37e`, clean but stale relative to canonical GitHub main;
- `qiven-devkit`: `jason-brother/native-build-system` at `5c8fcb0370891033da174b72bb53f8e484367cb3` with the large uncommitted Devkit 0.2.0/native-build-system worktree;
- `qiven-foundation`: `jason-brother/foundation-devkit-0.1.3-rollout`, clean;
- `qiven-math`: `jason-brother/math-devkit-0.1.3-rollout`, clean;
- `qiven-runtime`: generated directory present but not a Git repository;
- `qiven-dcr-win`: unborn `main`/no HEAD, with partially staged source files plus untracked repository files and `*.tmp0` artifacts;
- `qiven-toolchain-win`: clean main.

These observations were preserved rather than repaired.

## Reflog correction

Subsequent read-only Git reflog evidence showed that the Foundation and Math rollout branches were **not created by this incident**. Foundation's rollout branch/commit/push dated earlier on 2026-09-15, and Math's rollout branch/commit/push also dated earlier. Therefore their current branch names must not be presented as proof of split-brain mutation.

Likewise, DCR recent history contains visible earlier operations that explain some qiven-dcr-win staging/build/temp-file state. Because DCR history lacks caller-flow identity, the incident cannot truthfully attribute every local anomaly or earlier error to one of the two concurrent Chat choices.

The supported conclusion is narrower and stronger: two execution authorities were observed concurrently at the UI/product level, while the host transport had no mechanism to distinguish, fence, or reject them.

## Remote-boundary observations

Canonical `qiven-context/main` was independently observed at `21128ab3b25dd7d924aa867c810d812526347306` when this incident branch was created.

The unfinished `qiven-devkit` native-build-system branch had not been pushed to its remote at incident freeze. Existing Foundation/Math rollout branches were already remote historical branches and are not evidence of new remote mutation from this incident.

No claim is made that all remote repositories were untouched until each exact ref is independently reconciled.

## Failed assumption

Before this incident Qiven's accepted DCR contract assumed that the authorized Chat/Work execution flow was singular. That assumption was procedural rather than host-enforced.

The incident proves that the following implication is unsafe:

```text
one user intent / one visible conversation
    => one local execution authority
```

Even perfect command-level fail-fast logic cannot protect a machine if two independent command sequences can concurrently enter the same filesystem and Git state.

## Required architectural correction

ADR-0026 establishes a JasonPC-resident Qiven Host Execution Broker with exclusive execution leases, monotonic fencing epochs, strict request sequencing/idempotency, quarantine on competing authority, durable bounded journaling, exact process-tree ownership, and no direct mutating DCR bypass.

The safety target is not merely mutual exclusion between two threads. It is prevention of **authority split-brain** across delayed, duplicated, retried, or concurrently rendered AI response flows.

## Temporary operating rule

Until the Host Execution Broker passes split-brain acceptance:

- mutating DCR execution is suspended;
- DCR may be used only for read-only incident forensics;
- JasonPC contaminated/incomplete worktrees are preserved for later reconciliation;
- remote GitHub-native context recording is allowed;
- any required local mutation to bootstrap the broker must go through an explicit owner-controlled trusted local path.

## Evidence limitations

The owner-observed dual-response execution is the decisive incident report. DCR history provides chronology but not caller identity. Git reflog provides repository chronology but cannot identify which upstream Chat response issued a command. Therefore this audit deliberately avoids assigning every historical mutation/error to a specific response branch.

That inability to attribute is one reason the new broker must journal execution identity before allowing local work.