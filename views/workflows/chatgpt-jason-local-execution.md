# ChatGPT + Jason Local Execution Workflow

For ordinary qiven-context Python semantics and source-contract work, the project
owner's 2026-09-17 authorization in `collaboration/context-validation.md`
(ADR-0032) applies: jason-brother validates directly in the agent runtime without
duplicate JasonPC validation. Task-specific acceptance roles and platform-dependent
properties remain scoped separately.

This workflow belongs to `ContextView<ChatGPT, Jason>`. It adapts Qiven's project
truth to Jason's current workstation and collaboration model; it is not a
project-global assumption for every future human or agent.

Qiven uses one local orchestration plane, Qiven Operator, with two authority/trigger
workflows.

## Workflow 1 — Remote AI + Human Manual Mode

ChatGPT may develop remotely against GitHub when local machine authority is
unavailable or unnecessary. GitHub remote state remains canonical.

When local validation, execution, local CI assistance, repository inspection or
another JasonPC action is required, ChatGPT asks Jason to switch to **Human Manual
Mode**. Human Manual Mode means:

1. operate from the long-lived local Qiven workspace (`D:\JasonWork` on JasonPC),
   not from ad-hoc `%TEMP%` repository clones;
2. use Qiven Operator as the human-facing engineering interface whenever the required
   capability exists;
3. ChatGPT supplies the repository, exact expected candidate identity, Operator
   action/profile and evidence needed back;
4. Operator owns state-oriented output, liveness, exact-head checks, validation
   sequencing, task isolation and cleanup of Operator-owned scratch/worktrees;
5. if Operator lacks a necessary capability, use only the minimum bootstrap fallback
   and record the missing capability as engineering debt.

Jason is an authority/physical-execution participant, not a substitute automation
engine. Human effort should be reduced to a short, legible trigger plus review of a
deterministic final summary.

### Human view versus machine view

Human Manual Mode uses the Operator's **human view** by default. Do not add global
`--json` to an owner-run acceptance command merely because the resulting evidence or
artifact is machine-readable: `--json` deliberately selects the machine view and
suppresses human `[RUN]` / `[WAIT]` / `[OK]` / `[FAIL]` rendering and heartbeat.

When an owner-run task must expose structured stdout from a successful child task,
use human view with `--verbose`; this preserves liveness while showing the child's
final machine-readable summary after that task completes. Reserve global `--json`
for agents/automation that require one stable final JSON object and do not require a
human progress display.

This distinction is part of the execution contract. A human-facing acceptance command
that is silent for its material duration because it was unnecessarily forced into
machine view is an invocation error, not acceptable Human Manual Mode evidence.

## Artifact-acceptance roles are not duplicate validation

ADR-0032 removes redundant JasonPC execution of portable Python/source tests. It does
not allow an acceptance topology to collapse producer and consumer into one
contaminated agent session.

For K4 Canonical Artifact Handoff, JasonPC is the reference **producer** under this
ContextView. Human Manual Mode/Qiven Operator must materialize the exact remote
candidate, generate and restore/verify the handoff artifact, and return one
machine-readable result identifying the artifact. A separate fresh LLM is the
**consumer**. The consumer performs artifact-only Phase A before any live repository
verification.

The required Operator task is part of the K4 implementation. Until that task exists,
use only a minimal explicit bootstrap fallback; do not reinterpret its absence as
permission to run the producer role inside the authoring LLM.

For an owner-run K4 producer trial, invoke the Operator in human view and use
`--verbose` so the producer's final JSON summary (including artifact path and digests)
is visible after successful completion while heartbeat remains visible during the
gate. Do not use global `--json` for that manual trial. The handoff artifact itself,
not the Operator terminal rendering mode, is the machine-readable object transferred
to the fresh consumer.

## Workflow 2 — AI-controlled JasonPC through Host

Workflow 2 is enabled only after the accepted qiven-host production authority path
satisfies the no-bypass safety gate and Context explicitly re-enables broker-mediated
remote mutation.

The intended call chain is:

```text
ChatGPT / AI
  -> remote transport (DCR or successor)
  -> Qiven Host execution authority
  -> Qiven Operator / declared repository task or gate
  -> JasonPC repository / toolchain / OS
```

AI may then develop locally for as long as useful and stable. Local repositories
under `D:\JasonWork` are working caches/materializations of GitHub state. Push is
normally needed when remote durability, cross-platform CI, remote review or
merge-to-main requires it rather than after every local edit.

After a checkpoint is canonically merged to `main`, the local workflow should
reconcile local `main`, delete merged/outdated temporary local and remote branches
under the accepted cleanup policy, and remove Operator-owned scratch/worktrees.
JasonPC must not accumulate an implicit archive that depends on Jason's memory to
clean.

## Shared invariant

Workflow 2 accelerates Workflow 1; it does not replace its engineering semantics.
Both use the same Operator tasks/gates and the same exact-identity, fail-fast, output,
cleanup and evidence rules. The caller/authority changes; the local engineering
operation does not.

Human Manual Mode remains the fallback when Host transport is unavailable, when
explicit human presence is required, or when a local action has not yet been admitted
to automated authority.

## Environment binding

This workflow uses `views/environments/jasonpc.yaml`. Stable workspace/environment
roots may be owner-declared there; exact tool versions, executable paths, mutable
environment state and VPN connectivity are live facts and must be verified when a
task depends on them.

## Current state

Workflow 1 is active now. Workflow 2 remains fail-closed behind
`OBL-20260915T163500Z-9D4C72` until Host Batch 001 production authority integration
proves there is no mutating bypass and Context explicitly re-enables it.
