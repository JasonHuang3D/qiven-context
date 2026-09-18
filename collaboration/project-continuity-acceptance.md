# Project Continuity Acceptance

## Goal

Demonstrate that Qiven can continue after session loss, turn incidents,
model/provider replacement or agent replacement without relying on model-native
project memory, a particular local clone, or private/oral project recollection.

This contract defines the **semantic reconstruction outcome**. It does not by itself
define how cognition is delivered to the fresh consumer. Every execution must name
one admitted delivery profile and obey that profile's input/isolation rules.

Human Succession is a separate higher-order property defined in
`collaboration/human-succession-acceptance.md`.

## Delivery profiles

### Remote cold boot

A fresh capable LLM/agent receives an exact remotely published `qiven-context` ref
and may read canonical Context plus the project repositories/live evidence that
Context identifies. This proves that canonical remote Context is sufficient for a
new reasoning session to continue safely.

The historical `collaboration/cold-boot-acceptance.md` and its preserved audits are
this profile. A PASS here does **not** prove that an exported backup/handoff artifact
is sufficient.

### Canonical artifact handoff

A fresh capable LLM/agent receives the handoff artifact produced under
`collaboration/context-handoff-contract.md`. Before sealing its initial
reconstruction, it may not reread canonical qiven-context cognition remotely or use
prior Qiven project memory to fill gaps. This proves portable artifact continuity and
is the mandatory profile for ContextKernel K4 acceptance.

After the isolated reconstruction is sealed, live verification may be performed only
for facts whose authority is live by contract. Live verification cannot repair a
missing canonical cognition input without causing the artifact-handoff phase to fail.

Additional transport profiles require an accepted contract naming their allowed
inputs and the property they prove. Passing one profile never silently proves another.

## Test subject

Use a fresh capable LLM/agent in a fresh session with no prior Qiven conversation and
no model-native Qiven project memory admitted as evidence. An authorized human operator may be the existing operator or a fresh operator; routine Project Continuity does not require a fresh human.

The human must not orally/private-message missing project cognition to the fresh
agent. The selected delivery profile determines which durable inputs are allowed.

A session checkpoint may be present as continuity evidence when the selected profile
contains it, but no canonical fact may exist only there.

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

The continuity test fails if the candidate:

- uses an input forbidden by the declared delivery profile;
- treats model memory, private human recollection or a local clone as authority;
- requires a missing prior chat to recover canonical project cognition;
- treats superseded/legacy material as current;
- leaves a known resolvable canonical conflict unresolved;
- invents missing history or repository state;
- cannot identify governance authority;
- confuses green CI or successful restore with semantic acceptance;
- cannot identify the exact next legitimate boundary; or
- claims a stronger continuity property than the executed profile proves.

## Acceptance evidence

Preserve each execution as a dated audit under `evidence/audits/`. The audit must
state:

- delivery profile;
- exact candidate/artifact identity;
- allowed inputs and any attempted/denied inputs;
- challenge and sources consumed;
- reconstruction result for all ten requirements;
- unsupported claims/abstentions;
- later live verification separately from isolated reconstruction when applicable;
- PASS/FAIL and the exact property that result establishes.

Continuity evidence is bound to the exact ref/artifact tested. A later candidate may
carry evidence forward without repeating the blind reconstruction only when the
intervening changes are limited to acceptance-specification correction, evidence
recording or tests and do not change the cognition/transport inputs consumed by the
trial. The carry-forward rationale must be explicit and final exact-head repository
validation must be rerun.

Context v2's historical remote-cold-boot acceptance remains evidence for remote
continuity. ContextKernel K4 is not accepted until at least one Canonical Artifact
Handoff profile execution passes and the final candidate passes exact-head repository
validation.
