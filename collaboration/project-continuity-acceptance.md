# Project Continuity Acceptance

## Goal

Demonstrate that Qiven can continue without relying on a particular session, model, provider, assistant identity, local clone, or original human recollection.

## Test subject

Use a fresh capable LLM/agent and a fresh authorized human operator with no prior Qiven conversation, no model-native project memory, no oral/private handoff, canonical GitHub `qiven-context`, and only the project repositories/live evidence that canonical context identifies.

A session checkpoint may be available as continuity evidence, but the test must not require any canonical fact to exist only there.

## Required reconstruction

The candidate must correctly establish, with provenance:

1. what Qiven is and what qiven-context is for;
2. the current governance trust boundary and who holds root project authority;
3. the engineering philosophy and material operating constraints;
4. the active objective and paused domains;
5. the latest accepted engineering checkpoint and its exact evidence;
6. any current unaccepted candidate and why it remains unaccepted;
7. active blockers and non-terminal obligations whose triggers matter now;
8. accepted, rejected, superseded, and legacy cognition relevant to the task;
9. which facts must be re-verified from live GitHub/CI/runtime state;
10. the next valid engineering action.

## Failure conditions

The continuity test fails if the candidate treats model memory or a local clone as authoritative, requires a missing prior chat to recover canonical project cognition, treats a superseded/legacy record as current, leaves a known resolvable canonical conflict unresolved, invents missing history or repository state, cannot identify project governance authority, confuses green CI with semantic acceptance, or cannot identify the exact next legitimate boundary.

## Acceptance evidence

Preserve each execution as a dated audit under `evidence/audits/`. The audit must state the exact qiven-context remote ref used, the challenge, sources retrieved, reconstruction result, unsupported claims/abstentions, and pass/fail result.

Context v2 is not fully accepted until at least one fresh-session execution of this contract passes after the migration candidate is remotely published.
