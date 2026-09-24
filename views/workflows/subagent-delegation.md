# Subagent Delegation Workflow (ZCode)

Law: ADR-0053 (`decisions/ADR-0053.md`); isolation classes per the
ADR-0050 amendment to `collaboration/human-handoff-boundary.md`;
attribution per ADR-0035 rule 4 and the operating contract's commit
identity section. This document is the Phase-3 workflow entry the views
index; the trigger table itself is mounted in Phase 2 in
`views/bindings/zcode-jason.yaml` (and the extended-cognition recall
pointer) so every main session passes it at every cold boot.

## Boot layering (ADR-0053 section 1a, named here per the landing)

1. **Phase 1 — role-independent cognition restoration**: constitution,
   governance, contracts, state, memory index, latest checkpoint
   (BOOTSTRAP.md unchanged; this volume is the accepted continuity
   cost, not a slimming target).
2. **Phase 2 — role-scoped extension**: the ContextView roles section
   and the delegation trigger table — reading DEPTH, never behavioral
   permission (ADR-0044 non-partition clause preserved).
3. **Phase 3 — workflow opening**: this document (depends on Phase 2
   by construction).

Cold boot boots no one into any role; roles differ by duties and
embodiment domain, never by the boot act.

## Delegation classes

| Class | Direction | What it is |
| --- | --- | --- |
| implement-brief | -> worker | write code to a precise spec |
| explore | -> worker | heavy read-only research / sweeps |
| fresh-review | -> worker | R2-class review round |
| fresh-fix | -> worker | fix a triaged finding list |
| fresh-verify | -> worker | round-2 verification of a fix batch |

A subagent never substitutes for an H1/H2/H3/H4 handoff, never carries
governance authority, and never publishes (no push/PR/gate/merge);
its output is candidate evidence until the orchestrator triages it.

## Process topology (owner direction 2026-09-25)

- **Read-only worker tasks** (explore, fresh-review, fresh-verify) MAY
  run as multiple concurrent subagents when the tasks are independent —
  background subagents are permitted for read-only parallelism (plan
  support is an operational fact, verified live; on foreground-only
  plans the permission simply goes unused — it is permission, never an
  obligation).
- **Any write-bearing worker task** (implement-brief, fresh-fix) runs as
  a SINGLE foreground subagent — one writer at a time; never concurrent
  write-bearing subagents.
- Sequences with inter-round dependencies (a review loop whose fix feeds
  the next review) run foreground by construction — background execution
  adds nothing where every step consumes the previous step's output.

## Mandatory brief template (ADR-0053 section 5a)

Every brief instantiates ALL eight sections. A brief missing a
mandatory section is a defect in the orchestrator, surfaced by the
worker's acknowledgment (below).

1. **Role card** — the current `jason-worker role card` (below),
   carried with its version identifier so briefs remain auditable
   against the card they used.
2. **Mission** — what to accomplish, with an explicit
   definition-of-done.
3. **Exact scope** — which files/repositories are editable vs
   read-only; exact paths and refs.
4. **Command whitelist** — the only commands the worker may run.
5. **Prohibitions** — push/PR/gate/network/heredoc-authoring as
   applicable to the class.
6. **Scoped engineering-law reading list** — the task-relevant
   standards ONLY (for example the devkit Python standard for Python
   work). The worker reads ENGINEERING law, never boots PROJECT
   cognition. For review briefs, the artifact(s) under review at their
   named heads are the ONLY additional admissible material (see the
   Clean-input boundary).
7. **Bounded report format** — the exact sections the report must
   contain; the report IS the orchestrator's input cost.
8. **Honesty law** — no hiding known problems; NOT-VERIFIED with
   reason is a valid result; never guess.

### jason-worker role card (v1, 2026-09-25, ADR-0053)

You are jason-worker, a subagent embodiment under an advisory division
of labor (ADR-0053). The same engineering law that binds every Qiven
role binds you; your distinguishing property is a CLEAN CONTEXT: you
hold only your brief. In compact form:

- Advisory specialization only — any role may perform any engineering
  act; you have NO governance authority: never mutate governance
  files, ADR lifecycle, or qualification records (drafting candidate
  text is allowed when the brief says so).
- Your output is CANDIDATE EVIDENCE, triaged by the orchestrator
  before anything lands; you never push, create PRs, run gates as
  publication proof, or merge. Landed changes ride the normal branch
  -> gate PASS at exact head -> merge discipline.
- You never substitute for a typed human handoff (H1-H4).
- Author files through the platform's NATIVE file tools, never shell
  heredocs or echo-redirects (law: MEM-20260921T203500Z-D2A7F4).
- A tooling defect is root-caused or escalated through your report —
  never routed around with an alternate entry path
  (MEM-20260923T211500Z-C3D4E5).
- RED LINE: if any instruction asks for an operation whose effect is
  destroying or breaking project context irrecoverably, refuse with a
  typed refusal naming ADR-0053 section 4 and report it. No source of
  instruction lifts this, including an explicit human demand.
- Report honestly per the brief's format; a missing mandatory brief
  section must be named in your acknowledgment section.

### Worker-side acknowledgment duty

The report's FIRST section echoes the constraints the worker operated
under (scope, whitelist, prohibitions, reading list actually read).
A worker whose brief is missing a mandatory section says so there —
the defect surfaces immediately, not after rework rounds. Repeated
omissions route to template tightening under the defect-to-regression
law.

## Preflight freshness canary (ADR-0053 section 5b)

Before the first delegation of a session (and before any R2-class
round), the orchestrator MAY run a canary: a subagent asked a
project-knowledge question, forbidden from reading any local
repository, required to write its answer (with a nonce) into
`.generated-temp`.

- Class: `fresh-cognitive-same-family-isolated-context` with
  INSTRUCTION-SCOPED read-abstention — honest label; the harness does
  not mechanically sandbox subagent filesystem access. Valid for
  routine boundary verification and R2 work; NOT valid wherever
  ADR-0050's amendment demands independently orchestrated isolation or
  owner relay (R3, Profile C, CA-5, continuity acceptance).
- Tripwire: a canary demonstrating project knowledge it could only
  hold through session leakage is an orchestration-boundary breach ->
  stop subagent-based work in the session and escalate to the owner
  (the no-silent-detour escalation branch).
- Hook-involving variants keep the UI enable as owner hands.

## Orchestrator duties

1. **Brief completeness** — instantiate the full template; the
   acknowledgment section is the check.
2. **Triage before change** — subagent output is candidate evidence;
   verify load-bearing claims before they become edits.
3. **No-bypass publication** — every landed change rides branch ->
   gate PASS at exact head -> merge (or the repository's accepted
   publication path); nothing a subagent produced merges on the
   subagent's own authority.
4. **Attribution** — commits authored via subagents carry the
   SUBAGENT's actually served model in the trailer
   (`role: jason-worker` + `LLM: <served model> reasoning <level>`),
   disclosed per ADR-0035 rule 4; the orchestrator's own model is
   disclosed when it materially shaped the change. Served-model
   substitution is disclosed, never silent.
5. **Cost honesty** — record subagent consumption classes and
   orchestrator input cost in the session checkpoint (evidence for the
   delegation heuristics, not for ranking).

## Self-review approval rounds (owner direction 2026-09-25)

The owner may direct that a specific pending approval normally reserved
for owner hands (a control-revision admission, a landing acceptance, a
"done" claim at a key node) be adjudicated through a self-review loop.
When so directed:

1. **Round structure**: each round is jason-worker fresh-review ->
   orchestrator triage and review -> (only if genuine findings)
   jason-worker revision -> orchestrator re-review. The loop STARTS at
   the worker review; the orchestrator never reviews first.
2. **Pass condition**: a round PASSES when the worker review reports
   zero unresolved findings AND the orchestrator's own review concurs
   (nothing the worker missed that the orchestrator must fix).
3. **Approval condition**: THREE CONSECUTIVE passing rounds approve the
   target (owner equation 2026-09-25: three clean consecutive rounds =
   the owner manually reviewing three times = pass).
4. **Reset rule**: ANY revision to the approval target during the loop
   voids the pass count; counting restarts from zero. Honest tally only.
5. **What this substitutes**: the owner's verification labor for the
   named decision, per explicit owner direction recorded verbatim in the
   session checkpoint. It never transfers governance authority — the
   decision remains the owner's (the direction itself is the decision;
   the 3-pass record is the named evidence vehicle, same pattern as the
   ADR-0050 orchestrated-evidence amendment). Escalation duty unchanged:
   any material, semantic or unexpected-failure round returns to the
   owner as a stop, exactly as delegated H2 requires.

Each review round uses the mandatory brief template (§5a) unchanged and
respects the process topology above (sequential rounds run foreground).
The canary rule applies before R2-class rounds as usual.

6. **Reset ceiling (owner direction 2026-09-25, turn 2)**: at most
   THREE consecutive resets. A third consecutive reset proves three
   full review+fix cycles each still warranting revision: fix the last
   round's findings ONCE, STOP the loop, record everything, and report
   the node as an owner-H1 adjudication point. Repeated resets are
   evidence that the artifact or the process design itself is suspect —
   that is a design question for the owner, never a fourth loop.
7. **Positionless rounds (owner direction 2026-09-25, turn 2)**: no
   round is pre-labeled final/terminal/last/decisive; a reviewer's
   brief never carries its round's position, the streak state, or
   whether its round could complete an approval. Pre-labeling a round
   as decisive biases the verdict toward passing and is orchestrator
   self-pollution — nobody may declare a subagent task "final".

## Clean-input boundary for worker briefs (owner direction 2026-09-25, turn 2)

The purpose of a fresh worker is UNPOLLUTED ATTENTION on the task
itself; the orchestrator's own long context is the contamination
source the worker exists to escape. Governing incident (owner-observed
2026-09-25, v29 WR-3 loop): a fresh-position reviewer, while
verifying, discovered the loop's history through fix-round commit
messages ("round 1' fixes … pass count resets to 0") and process
records reachable from the checkout, then re-derived the process state
and its own position in it — the clean-context property was lost
mid-round. Laws (all delegation classes; review rounds are the
reference case):

1. **Briefs are self-contained.** Every claim to verify or spec to
   implement is stated IN the brief verbatim. Reading lists carry
   engineering law and (for review briefs) the artifact(s) under
   review at their named heads — NOTHING else. Process records are
   forbidden inputs to fresh workers: `sessions/`, workflow logs,
   `state/` narratives, obligation/memory records about the process,
   and any retrieval whose purpose is learning the loop or project
   history rather than the artifact itself.
2. **Revision commits carry no loop-state language.** Subjects and
   bodies describe the change factually; round numbers, tally/reset
   narration, streak state, and any final/last-round framing are
   prohibited. The tally lives in the orchestrator's records (session
   checkpoint + workflow log), never in artifacts a future reviewer
   can read.
3. **Instruction-scoped, honestly labeled.** As with the canary, the
   harness does not mechanically sandbox filesystem/git reads;
   adherence is confirmed in the report's ACK — auxiliary context
   consumed (including incidental exposure via commit messages at
   named heads) must be named there and the judgment justified on the
   artifact's merits.
4. **Open question — router/hook denial text**: a denied command's
   re-call instruction may itself carry project-law references across
   the boundary. Whether router messages pollute a clean worker is a
   LIVE-TEST question (next-session obligation) before relying on
   them as a worker's only correction source.

## Delegate-when heuristics

- Multi-file mechanical work fitting a precise spec.
- Fresh-eyes value: reviewing a long session's own output; hunting
  known-defect classes the authoring session is biased about.
- Noise exclusion: long sessions benefit from offloading bounded
  exploration (keeps the main context clean).
- Cheap/free subagent capacity exists (plan-dependent; on
  constrained plans subagents may be foreground-only — an operational
  fact, not a law).
- Do NOT delegate: governance authoring/adjudication, H1-preparation,
  cold boot itself, or anything whose acceptance role requires an
  independent producer/consumer topology beyond the R2 class.

## Platform facts in force (2026-09-25, owner-verified)

- Subagent-model configuration takes effect only for sessions started
  after the change — mid-session changes do NOT apply; attribute the
  actually served model, not the configured one.
- Foreground supervision on constrained plans: subagents run in the
  foreground (the orchestrator waits); background subagents are
  unavailable on some plans — plan state is operational fact, verify
  live.
