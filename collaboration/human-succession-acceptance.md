# Human Succession Acceptance

## Goal

Demonstrate the stronger continuity property that Qiven can be transferred to a different authorized human operator without depending on the prior operator's private recollection, oral handoff, local machine state, or private conversation history.

This is a higher-order continuity benchmark, not a routine prerequisite for every Context release or for Context v2 acceptance. It is distinct from both remote cold boot and Canonical Artifact Handoff.

## Test subject

Use a fresh authorized human operator with no prior private Qiven knowledge. Authorization must already be legitimate under the current governance model; the test does not bootstrap or self-grant authority.

The human may use a capable LLM/agent, but that agent must not contribute hidden Qiven memory or private prior-session knowledge. Unless the invocation explicitly composes this benchmark with Canonical Artifact Handoff, the available basis is canonical GitHub `qiven-context`, the project repositories/live evidence that Context identifies, and normal public/tool-accessible engineering knowledge.

A successful Human Succession run therefore proves replacement of the human operator. It does not automatically prove that a standalone exported artifact is sufficient; that separate property belongs to `collaboration/context-handoff-contract.md`.

## Required outcome

The fresh operator must establish the same current project model required by Project Continuity Acceptance, understand the authority they actually possess, distinguish accepted state from candidates/history, identify blockers and obligations, and direct the next legitimate project action without a private handoff from the previous operator.

## Failure conditions

The test fails if successful takeover requires unpublished recollection from the prior operator, private chat history, a privileged local clone, invented authority, or hidden state not represented by the declared continuity delivery profile/live authorities.

## Invocation

Run Human Succession Acceptance when the project owner explicitly wants to prove human-operator replaceability, before or during a real governance transfer when useful, or when organizational/multi-operator requirements make this property operationally material.

It is not automatically required merely because qiven-context changes. If Human Succession is composed with Canonical Artifact Handoff, both profiles' restrictions apply and the audit must state that composition explicitly.

## Evidence

Preserve executions as dated audits under `evidence/audits/`, including exact Context ref or artifact, declared delivery profile, identity/authorization assumptions, available sources, reconstruction/takeover result, unsupported claims, and pass/fail disposition.
