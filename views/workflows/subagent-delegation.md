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

| Class | Direction | What it is | Default at hook-free revisions |
| --- | --- | --- | --- |
| implement-brief | -> worker | write code to a precise spec | main session (owner-gated delegation) |
| explore | -> worker | heavy read-only research / sweeps | worker (routine) |
| fresh-review | -> worker | R2-class review round | worker (routine) |
| fresh-fix | -> worker | fix a triaged finding list | main session (owner-gated delegation) |
| fresh-verify | -> worker | round-2 verification of a fix batch | worker (routine) |

A subagent never substitutes for an H1/H2/H3/H4 handoff, never carries
governance authority, and never publishes (no push/PR/gate/merge);
its output is candidate evidence until the orchestrator triages it.

## Write-bearing default at hook-free revisions (owner direction 2026-09-26)

**Implementation and other write-bearing work is done by the MAIN
session by default; delegating it to a worker requires explicit owner
direction for that bounded case.** Read-only classes (explore,
fresh-review, fresh-verify, canary) remain routine delegations.

Rationale (measured, F1A2B3 + the platform fact MEM-20260926T195500Z-F1E2D3):

1. **The mechanical law layer is main-session-only.** No hook reaches a
   subagent: the heredoc-authoring absolute deny, long-class background
   routing, the build/gate node-reuse guard, sweep exec-lease custody —
   none of them fire inside a worker. A write-bearing worker operates
   with NO mechanical backstop; everything rides the brief and the ACK.
2. **The heredoc class is the proven recurrence.** Main sessions violated
   the file-authoring law twice under a behavioral rule before the hook
   made it mechanical (2026-09-21/23). Assuming workers behave better
   than the main agent did, without enforcement, is not evidence-based;
   and a worker's heredoc-corrupted file costs a full gate cycle to
   catch (post-hoc), where the main session's violation is prevented
   (pre-emptive).
3. **The risk asymmetry matches the value.** A review worker's worst
   failure is a wrong report — cheap to triage, nothing lands. A write
   worker's failure modes (corrupted files, foreground long builds
   burning the worker, unleased sweeps/network) hit the repository and
   the machine. Meanwhile the clean-context property that makes workers
   valuable is strongest for REVIEW (unbiased attention), and for
   implementation the complete spec must live in the brief anyway
   (clean-input law) — the main session, which authored the spec, loses
   little by implementing it.
4. **Revisit trigger:** when a harness revision wires hooks into child
   runtimes (the ZCode fork lane / PR #3 census input), this default is
   re-adjudicated on measured evidence — the constraint is the missing
   enforcement layer, not delegation itself.

Historical note: fresh-fix workers were used successfully before this
default (v27/v29), with orchestrator-run gates catching everything
before publish — the class stays lawful UNDER EXPLICIT OWNER DIRECTION;
it is the routine default that changed, because the enforcement gap is
now measured rather than assumed away.

## Process topology (owner direction 2026-09-25)

- **Read-only worker tasks** (explore, fresh-review, fresh-verify) MAY
  run as multiple concurrent subagents when the tasks are independent —
  background subagents are permitted for read-only parallelism (plan
  support is an operational fact, verified live; on foreground-only
  plans the permission simply goes unused — it is permission, never an
  obligation).
- **Any write-bearing worker task** (implement-brief, fresh-fix — both
  owner-gated by the Write-bearing default above) runs as a
  SINGLE foreground subagent — one writer at a time; never concurrent
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

## Transcript-provenance audit (mechanical, F1A2B3 law 2026-09-26)

Worker behavior is verified against the harness transcript record
(`~/.zcode/cli/db/db.sqlite`, `part.data`: tool calls carry exact
`state.input`/`state.output`/`state.error`; a live router denial
signature is `status:"error"` + error prefixed `[qiven-hook]`; reasoning
parts carry thinking; `session.parent_id` links subagents; parts persist
INCREMENTALLY during a run, so live capture by a bounded DB sampler is
feasible — measured 2026-09-26).

1. **Mechanical, never eyeballs**: the tool is
   `qiven-context/tools/scan_subagent_transcripts.py` (curated pollution
   taxonomy: loop-state, round-position, process-record paths; exact
   seed markers for detection trials; exit codes gate-compatible).
2. **When it runs**: after every approval-loop round, after every
   boundary-sensitive delegation (R2-class review/fix/verify, bait-class
   or compliance-sensitive work), and whenever a worker's honesty claim
   is load-bearing. Routine read-only exploration does not require a
   scan.
3. **What it proves**: actual files read and commands run (ground truth
   for bait/scope scoring), pollution markers per channel (brief text,
   tool I/O, reasoning), live hook denials (must be 0 inside workers),
   and seed-marker detection when pre-registered.
4. **ACK verification is mechanical**: the worker's ACK disclosure is
   compared against the transcript tool-input list — an ACK that omits
   an actually-opened file is a finding, not a style issue. Measured:
   8/8 honest ACKs in the F1A2B3 trials (including declined-temptation
   disclosure); the duty is auditable, take it as measured, not trusted.
5. **Provenance**: record worker session ids + scan JSON paths with the
   results; experiment-grade scans and pre-registrations live under
   workspace `.generated-temp`, load-bearing numbers land in
   `evidence/audits/`.

Measured evidence (2026-09-26 trials, k=3 A/B pairs + canary + b2, all
clean-brief workers resisted answer-key/process-record/fake-law/shortcut
baits 6/6 with zero unlisted reads; polluted-brief workers showed the
verdict-drift class below): `evidence/audits/subagent-boundary-experiments-2026-09-26.md`.

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
4. **Router/hook denial text — measured moot (F1A2B3, 2026-09-26)**: at
   this harness revision no hook fires inside subagent runtimes
   (MEM-20260926T195500Z-F1E2D3), so router denial text CANNOT reach a
   worker at all — 0 live denials across all 49 recorded subagent
   sessions (historical corpus + 8 experiment runs; every `[qiven-hook]`
   string in worker transcripts is file content or a test subject's
   stderr, never a router event). The spawn call itself is also unhooked
   (workspace PreToolUse matches Bash only; background spawn fails closed
   on plans without background agents). Consequence: **the brief is the
   only channel into a worker**; measured live, a clean self-contained
   brief held as the only correction channel with honest NOT-VERIFIED
   reporting under four classes of declined temptation (b2 trial). If a
   future harness revision wires hooks into child runtimes, re-open the
   denial-text-pollution question before treating router messages as a
   worker correction channel.

Measured drift evidence (F1A2B3 A/B trials, 2026-09-26): the same
artifact reviewed under a self-contained brief (k=3) produced zero
loop-state markers and 3/3 artifact-only verdicts; under a
process-record-laden brief (k=3, same artifact, same ambient files) all
three transcripts carried loop-state material, 2/3 VERDICTS themselves
contained round-position language ("does not pass round 2 as-is";
"per the loop rules ... the consecutive-pass count does not advance"),
and 3/3 spent report budget reconciling loop history instead of the
artifact. Ambient unlisted files were NOT the channel (6/6 workers
resisted answer-key/fake-law/shortcut baits under clean briefs) — **the
brief itself is the pollution channel**: loop framing, round positions,
and process records in a reading list leak into verdicts even when the
stated rules are identical. "Context on what changed" is not a lawful
reading-list entry; state the delta inline in the brief or not at all.

## Delegate-when heuristics

- Fresh-eyes value: reviewing a long session's own output; hunting
  known-defect classes the authoring session is biased about.
- Noise exclusion: long sessions benefit from offloading bounded
  read-only exploration (keeps the main context clean).
- Cheap/free subagent capacity exists (plan-dependent; on
  constrained plans subagents may be foreground-only — an operational
  fact, not a law).
- Write-bearing implementation: NOT a delegate-when — main session by
  default (the Write-bearing default above); owner direction required
  to delegate a bounded case.
- Do NOT delegate: governance authoring/adjudication, H1-preparation,
  cold boot itself, or anything whose acceptance role requires an
  independent producer/consumer topology beyond the R2 class.

## Platform facts in force (2026-09-25 owner-verified; 2026-09-26 live-reverified)

- Subagent-model configuration takes effect only for sessions started
  after the change — mid-session changes do NOT apply; attribute the
  actually served model, not the configured one.
- Foreground supervision on constrained plans: subagents run in the
  foreground (the orchestrator waits). Live-reverified 2026-09-26
  (offpeak idle plan): background agents fail closed with a typed error
  ("Idle-time tasks do not support background agents") — the read-only
  multiprocess permission above stays unused on such plans.
- No hook reaches subagent tool calls at this revision
  (MEM-20260926T195500Z-F1E2D3); the spawn call itself is unhooked where
  PreToolUse matchers cover Bash only — worker-side compliance rides the
  brief + ACK duty, verified by the mechanical transcript audit above.
- Transcript parts persist incrementally during subagent runs (session
  DB), so in-flight mechanical supervision via a bounded DB sampler is
  feasible when a round warrants it.
- Subagent transcript ids in the session DB are keyed
  `sess_subagent_agent_<uuid>`, while spawn results return
  `agent_<uuid>`: scan with `--session sess_subagent_agent_<uuid>` or
  resolve once via `--parent <orchestrator session id>` — the bare
  spawn-result id matches nothing (measured live in the 2026-09-26
  reviewer qualification on build 3.14.3.7762; the qualification
  session worked around it and this line bakes the mapping in).
