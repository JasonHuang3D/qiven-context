# Human Handoff Boundary

Accepted by ADR-0036 on 2026-09-18. This contract defines when unattended
automation is permitted and when a typed human handoff is mandatory. The
classification follows the objective class of the operation being claimed, not
the identity of the requester, the convenience of the moment, or any
conversational instruction to skip it.

## Principle

The evidence a claim requires is a property of the claim itself. A handoff
requirement therefore cannot be waived verbally; it can only be removed by
revising the governing contract through an accepted ADR. This mirrors the
existing acceptance-role rule in `collaboration/context-validation.md`: a
task-specific acceptance role cannot be replaced by the authoring session simply
because the mechanics are portable.

## Typed human handoffs

- **H1 — execution handoff**: the project owner physically runs the acceptance
  producer through the trusted local path (for example the K4
  `k4-handoff-acceptance` Operator gate). The producer role in an acceptance
  topology is always H1.
- **H2 — review handoff**: the owner or a delegated reviewer accepts the exact
  delta before merge-class publication. A merge confirmation given in conversation
  and a merge performed in the GitHub UI are both valid H2 evidence for the same
  exact delta.
- **H3 — authority handoff**: Human Succession under
  `collaboration/human-succession-acceptance.md`.
- **H4 — recovery-presence handoff**: the cryptographic local user presence
  required by ADR-0029 for Host recovery authority.

A handoff claim must name its type (H1-H4) and its evidence.

## Operation classification

| Operation class | Unattended automation | Required handoff | Verbal waiver |
| --- | --- | --- | --- |
| Read-only (remote reads, retrieval, analysis, audit) | permitted | not applicable | not applicable |
| Rebuildable derived artifacts (generated/, indexes, isolated scratch builds/tests) | permitted with bounded resources | not applicable | not applicable |
| Local commit on an authorized task branch | permitted inside the authorized scope | review may be deferred to publication | scope negotiable, discipline not |
| Push of a pre-authorized exact task branch (WIP durability) | not unattended-eligible | H2 before merge | branch scope negotiable |
| PR creation and merge-class publication | prohibited | H2 mandatory | invalid |
| Acceptance-topology roles (K4/K5 producer, fresh consumer, Human Succession) | impossible by definition | H1/H3 mandatory | invalid |
| Governance mutation (authority.yaml, constitution, ADR lifecycle) | prohibited | H2 plus root principal | invalid |

"Unattended" means scheduled, idle-time, or otherwise unsupervised execution
where the owner is not present in the interaction loop. Foreground execution in
an owner-launched, owner-visible session is not unattended; each mutating action
still passes the session's permission surface.

## No-verbal-waiver protocol

When a human instruction would exempt a mandatory handoff, the agent must:

1. decline the exemption and name the specific gate and the claim it protects;
2. offer the legitimate alternatives: descope the claim, or revise the governing
   contract through the ADR process;
3. record the exchange in the session checkpoint when the instruction is material.

An agent that silently performs a mandatory handoff because it was told to skip
it has produced an unprovable claim and must treat the result as non-accepted.

## Relation to existing boundaries

- The ADR-0026 Host broker and the DCR suspension (`OBL-20260915T163500Z-9D4C72`)
  govern remote-AI local mutation channels; this contract classifies the general
  operation surface and re-enables no channel.
- ADR-0035 binds roles to model instances; this contract binds claims to handoff
  types. Both are view-independent canonical rules.
- The K4 producer gate remains the reference H1 example; K5 must reuse the same
  producer topology for its acceptance trials.
