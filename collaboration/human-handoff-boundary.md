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

- **H1 — isolation-boundary handoff**: the project owner performs the
  operations that constitute or cross an isolation boundary, plus any act a
  contract explicitly marks owner-run as a trust anchor. Refined 2026-09-20
  by owner direction: H1 is defined by what genuinely requires the owner's
  hands and agency — (a) launching fresh/isolated sessions, (b) relaying
  material across those boundaries (artifact in, sealed output back),
  (c) owner-run trust-anchor execution where a contract names it,
  (d) owner-designated adjudication points: where the owner has explicitly
  instructed that a specific decision, ruling or acceptance requires them,
  reaching that point is an H1 stop (added 2026-09-21 by owner direction;
  the agent's duty there is the H1-preparation duty below — everything
  paste-ready with complete evidence — never self-adjudication). Mere
  mechanical execution of a deterministic, digest-verifiable program is NOT
  inherently H1: where the owner so directs, the agent may run it and hand
  the owner the artifact path and identity, and the owner's H1 duty narrows
  to verifying the artifact identity and crossing the boundary. The
  producer ROLE in an acceptance topology is unchanged — who types the
  command is the owner's choice, with an owner verification duty attached
  (confirm the digest/identity before handing the artifact to a consumer).
- **H2 — review handoff**: the owner or a delegated reviewer accepts the exact
  delta before merge-class publication. A merge confirmation given in conversation
  and a merge performed in the GitHub UI are both valid H2 evidence for the same
  exact delta.
- **H3 — authority handoff**: Human Succession under
  `collaboration/human-succession-acceptance.md`.
- **H4 — recovery-presence handoff**: the cryptographic local user presence
  required by ADR-0029 for Host recovery authority.

A handoff claim must name its type (H1-H4) and its evidence.

## Long-running mode (2026-09-21 owner direction)

The owner may place a session into **long-running mode**: an explicit,
session-scoped grant that the session continues batch after batch without
per-batch owner merge stops. Semantics (as adjudicated with the owner when
the mode was defined — the raw instruction was "only H1 is needed", which
alone is not coherent with this contract and is implemented as follows):

1. **Per-batch H2 is standing-delegated, not waived.** For ordinary
   engineering batches in the mode (implementation, tests, docs, state
   transactions), the session's reviewer satisfies H2 through exact-head
   full-gate PASS plus a merge-proof receipt recorded in each PR, per the
   delegated-review rule this contract already admits. Delegated H2 carries
   the same escalation duty: a material round returns to the owner.
2. **Non-delegable review classes remain owner H2 regardless of mode**:
   governance mutation (authority.yaml, constitution, ADR lifecycle —
   "H2 plus root principal"), acceptance/ratification of an ADR, and
   role/binding qualification upgrades (the reviewer self-certification ban
   is owner-reserved and cannot be delegated to the reviewing instance
   itself).
3. **H1 is unchanged and fully owner-only**, including clause (d)
   owner-designated adjudication points.
4. **Mode mechanics**: entered and exited only by explicit owner direction;
   recorded in the session checkpoint; a fresh session does NOT inherit the
   mode. Long-running mode is a supervised foreground mode — it is not
   unattended automation, and every other contract (unattended read-only
   default, single-writer, no-verbal-waiver, commit attribution) applies
   unchanged. The operational workflow (continue-unless-H1 turn semantics,
   checkpoint layers, stash) is `views/workflows/long-running.md`; this
   section is its contract anchor.

## Agent H1-preparation duty (2026-09-20)

When a step requires the owner's hands, the agent's obligation is to make
the owner's part convenient and improvisation-free:

1. **Everything paste-ready.** Exact file locations (absolute paths),
   complete verbatim prompts for the other side of the boundary (the owner
   copies one block, nothing more), exact relay instructions (what to
   attach, what to paste back, to whom), and — where a step must be
   owner-run — one copyable command line.
2. **Boundary isolation stated in the prompt itself.** The verbatim prompt
   for a fresh consumer carries its own isolation rules (what it may not
   consult before sealing), so correctness does not depend on the owner
   remembering them.
3. **Sealed outputs return to the agent for rubric grading.** Grading a
   sealed Phase A against a rubric is the authoring session's evaluator
   role; the answer key must not reach the consumer before it seals. The
   owner relays the sealed reply verbatim.
4. **The kit is one package.** Artifact path + identity + prompt + relay
   instructions are delivered together, and recorded in the session
   checkpoint so an interruption does not lose the H1 state.

## Operation classification

| Operation class | Unattended automation | Required handoff | Verbal waiver |
| --- | --- | --- | --- |
| Read-only (remote reads, retrieval, analysis, audit) | permitted | not applicable | not applicable |
| Rebuildable derived artifacts (generated/, indexes, isolated scratch builds/tests) | permitted with bounded resources | not applicable | not applicable |
| Local commit on an authorized task branch | permitted inside the authorized scope | review may be deferred to publication | scope negotiable, discipline not |
| Push of a pre-authorized exact task branch (WIP durability) | not unattended-eligible | none for the push itself; H2 before merge-class publication of the pushed branch | branch scope negotiable |
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

- Remote-AI local mutation channels are governed by the sealed host/DCR
  decision (ADR-0043, 2026-09-21): RuntimeHost absorbs execution
  authority and the DCR transport is retired; the archived
  OBL-20260915T163500Z-9D4C72 is moot. This contract classifies the
  general operation surface and re-enables no channel.
- ADR-0035 binds roles to model instances; this contract binds claims to handoff
  types. Both are view-independent canonical rules.
- The K4 producer gate remains the reference H1 example; K5 must reuse the same
  producer topology for its acceptance trials.

## Amendment: orchestrated fresh-review isolation (ADR-0050, 2026-09-23)

Accepted 2026-09-23 by owner H2 (ADR-0050). This amendment narrows the H1
classification this contract adopted (ADR-0036) for fresh-review trials;
it does not touch any other H1/H2/H3/H4 scope:

- Mechanically verified session creation, sealed input transport, and
  sealed output capture inside an approved orchestration boundary cease
  to be inherently H1. Cognitive-review isolation is produced by the
  orchestration boundary; the owner accepts the resulting governed
  evidence instead of transporting it.
- H1 remains mandatory for: owner-only credentials or devices; external
  isolation boundaries the orchestrator cannot cross; owner-named trust
  anchors; owner-designated adjudication points.
- Existing owner-named K4/K5 gates and all H2-H4 claims are unchanged.
- Two disclosed independence classes: routine R2 fresh review MAY use a
  harness-created fresh isolated-context session
  (`fresh-cognitive-same-family-isolated-context`); every R3 review,
  Profile C trial, and CA-5 review uses independently orchestrated
  isolation (`fresh-cognitive-orchestrated-isolation`). A subagent
  sharing the author's conversation context qualifies under neither
  class.
- Governance mutation (including any further change to this contract)
  still requires H2 plus the root principal.
