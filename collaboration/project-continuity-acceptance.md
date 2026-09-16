# Project Continuity Acceptance

## Goal

Demonstrate that Qiven can continue after session loss, turn incidents, model/provider replacement, or agent replacement without relying on model-native memory, a particular local clone, or private/oral project recollection.

Project Continuity is the routine Context acceptance gate. Human succession is a separate higher-order property defined in `collaboration/human-succession-acceptance.md`.

## Test subject

Use a fresh capable LLM/agent in a fresh session with no prior Qiven conversation and no model-native project memory. An authorized human operator may be the existing operator or a fresh operator; the test must not rely on that human supplying private/oral Qiven knowledge to reconstruct project state.

The test receives the exact remotely published `qiven-context` candidate under evaluation and only the project repositories/live evidence that canonical context identifies. A session checkpoint may be available as continuity evidence, but no canonical fact may exist only there.

A fresh human is deliberately **not** required for this routine gate. Proving continuity across replacement of the human operator belongs to Human Succession Acceptance.

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

The continuity test fails if the candidate treats model memory, human private recollection, or a local clone as authoritative; requires a missing prior chat to recover canonical project cognition; treats a superseded/legacy record as current; leaves a known resolvable canonical conflict unresolved; invents missing history or repository state; cannot identify project governance authority; confuses green CI with semantic acceptance; or cannot identify the exact next legitimate boundary.

## Acceptance evidence

Preserve each execution as a dated audit under `evidence/audits/`. The audit must state the exact qiven-context remote ref used, the challenge, sources retrieved, reconstruction result, unsupported claims/abstentions, and pass/fail result.

Continuity evidence is bound to the exact ref that was tested. A later candidate may carry that evidence forward without repeating the blind reconstruction only when the intervening changes are limited to acceptance-specification correction, evidence recording, or tests and do not change the canonical project cognition or retrieval inputs that were reconstructed. The carry-forward rationale must be explicit, and final exact-head repository validation must be rerun.

Context v2 is not fully accepted until at least one fresh-session execution of this contract passes after the migration candidate is remotely published and the final candidate passes exact-head repository validation.
