# Current State

Compact current operational state. Historical narrative lives in
`evidence/audits/`, `sessions/`, `memory/records/` and the ADRs; this
file carries the present, not the story.

## Active objective

**Runtime Production MVP program is executing** (owner direction
2026-09-22, v17 session; MVP-1..MVP-3 landed through the 2026-09-23 v19
session): ADR-0047 (ACCEPTED) adopts the Production MVP Architecture —
one enforced vertical slice under DeploymentProfile
`zcode-jason-context-record-mvp`, SQLite control journal (never domain
truth), delivery order MVP-0..MVP-7; program obligation front-loaded
(`OBL-20260922T155800Z-9A7B41`). **MVP-0** PASSED (PR #37 `eba554a`);
**MVP-1** PASSED (PR #43 `763ff26`); **MVP-2** PASSED (v19: qiven-context
PR #118 `662d563` — canonical `runtime/invocation-policy.yaml` with the
validator reference-check; runtime PR #46 `e22462b` — native cognition
publisher, DeploymentProfile, generation stale-marking, minimal
runtimectl); **MVP-3** PASSED (v19: runtime PR #47 `59ea55c` — RuntimeHost
composition root, authenticated owner-only IPC (HMAC frames, DPAPI
secret, replay guard), hardened process boundary (Job-Object tree
reclaim, env/executable allowlists), bootstrap app retired; anchor
refresh PR #48 `0044fe1`). The RCA proof program (component ADL §89,
RCA-0..RCA-16) remains COMPLETE. The v18 and v19 sessions ran in
long-running mode (owner-delegated per-batch H2).

The 2026-09-22 governance session (v16, ADR-0044 de-role-ing + full
canonical audit) is complete; v17 (program launch + MVP-0 + standards
v18) is complete; v18 (MVP-1 + exec window fix + heredoc deny +
no-detour law) is complete; v19 (MVP-2 + MVP-3 + closing transaction)
is complete; v20 (2026-09-23 emergency stabilization: post-session
process-leak incident fully root-caused and resolved — exec v2 bounded
process custody landed devkit PR #27 `d1d2a3a` + context shim pin
PR #120 `132b420`; **ADR-0048 ACCEPTED** by owner H2 2026-09-23T09:05Z
in the v21 session) is complete. The v21 session (2026-09-23,
designation jason-extended-cognition, long-running mode per owner
delegation "委托你H2") recorded the ADR-0048 acceptance and landed
MVP-4 end-to-end (design PR #49 + implementation PR #50, delegated
per-batch H2; exit-gate rows 2-5 proven locally, row 1 = owner-H1 kit
prepared).

The v22 session (2026-09-23/24, designation jason-extended-cognition,
per-action owner H2s): **ADR-0050 ACCEPTED** (owner H2 2026-09-23T18:56Z,
verbatim "ADR0050批准") — the Task Cognition Activation program and
independent falsification are law. The v23 session (2026-09-24,
designation jason-extended-cognition, **long-running mode** with
standing-delegated per-batch H2 per the owner's opening instruction)
executed the directed next boundary as six published batches: **CA-0
COMPLETE** (qiven-context PR #128 `5a3e9a3`: trial-3 incident record +
two scars + canonical source inventory + selector schema v1 + sealed
gold fixture corpus F-01..F-08 with digests + measured cold-boot baseline
+ ZCode pre-design ingress feasibility proof with a named residual + the
CA-0 exit report carrying the bounded CA-1 batch declaration; devkit PR
#30 `02951b6` task taxonomy + engineering-task-v1 schema; foundation PR
#19 `b15d17c` capability surface). **The MVP-4 corrective lane is
LOCALLY COMPLETE with TWO root causes fixed** — the connection-model
defect (one-frame serve loop vs hello+event client) AND the second cause
the preflight itself surfaced (the client install record contained only
the host exe, so every hook client denied a silently-dropped admission;
PR #54 `ec79d52` + #55 `f8354c8` + #56 `6ebf6ff`): serve loop extracted
to testable ipc/pipe_service (multi-frame per connection, whole-frame
deadline, typed admission surface, per-connection seq law, frame budget),
denial taxonomy split 120-124, dead ReplayGuard claim removed honestly
(nonce/timestamp window unwired — pre-MVP-5 obligation), Shutdown exits
the exe, h1_kit preflight (enable-gated functional self-check) PASS end
to end, adversarial fresh-context review found M1-M4 (all empirical,
all fixed and verified PUBLISH). **RR-0 decision core landed** (runtime
PR #57 `0b72e30`: inventory bound to exact revisions, ADR-0024 admission
of the owning bounded ByteBuilder, per-format prefix rulings, golden-
fixture plan); the mechanical consolidation is the next bounded batch
inside the still-open interval. **The real MVP-4 H1 rerun kit is
PREPARED and preflight-verified** (`h1-kits/qiven-runtime/mvp4-h1/
0.1.0-g6ebf6ff6`, gate PASS at head `6ebf6ff`; paste-ready owner steps
in the kit GUIDE + the v23 checkpoint) — awaiting owner hands.
**Substantive MVP-5 is FROZEN** until the real MVP-4 H1 pass, RR-0
completion, and CA-2 pass.

The v24 session (2026-09-24, designation jason-extended-cognition,
long-running mode, standing-delegated per-batch H2) diagnosed and landed the **token-economy /
long-command execution architecture (ADR-0051 PROPOSED)**: the
deny→exec→poll detour is retired (polling costs O(polls × live
context)); router v4 denies raw long-class calls with the exact
`run_in_background` re-call instruction + a router-enforced
`MSBUILDDISABLENODEREUSE=1` guard for build/gate classes; sweeps stay
exec-lease; oversized foreground output is bounded natively by the
harness (>~25-30KB auto-persists, ~2KB preview — probed). The
owner-observed exec leak was root-caused to the runtime v1 operator pin
(NOT an exec v2 failure) and closed: **runtime PR #58** rolled template
0.1.9 (exec v2 custody) + foundation pin `b15d17c` + the cognition-pin
per-process fixture fix. The v24 "user-level unblock + global
AGENTS.md rewrite" turned out to address an ACCIDENTAL configuration
layer — the owner deleted it personally (v25 direction) and the
ADR-0051 law carriers are now exactly: this contract, the canonical
registry, and the workspace router. **ADR-0051 acceptance is the
owner-H2 decision point of the window** (paste-ready block in the
v25 checkpoint); OBL-20260923T215500Z-D5E6F7 carries the background-
lifetime probes.

The v25 session (2026-09-24, designation jason-extended-cognition,
long-running mode, standing-delegated per-batch H2, owner-ordered
"noise round" re-review of ADR-0051 + full-workspace coverage) landed:
**(a) ADR-0051 re-reviewed and amended** — five noise points corrected
(accidental user-level layer struck; timeout-does-not-bind-background
proven and the false mitigation withdrawn; sibling inventory corrected
and completed; platform facts re-verified fresh; router v4.1 guard
enforcement fixed); **(b) the OBL-…-B9C1D3 custody rollout is
COMPLETE workspace-wide** — real v1 carriers were foundation, math and
context-draft (context-draft missing from every prior list;
toolchain-win/third-party-win carry no operator at all): foundation
PR #20 `f28b86b`, math PR #12 `518e511`, context-draft PR #40
`ea9af72` (operator.json customs byte-identical), plus the pin ripple
runtime PR #59 (re-pins foundation + draft); all gates PASS at exact
heads with receipts; **(c) router v4.1** (devkit PR #32): leading
`NAME=value` env assignments no longer escape gate-class
classification — the taught guard re-call now passes via the real
guard check, arbitrary env prefixes can no longer bypass the class
raw (found live in v25: a preemptively-guarded gate call ran raw);
**(d) fresh-session probes P1/P2/P3/P5** (OBL-…-D5E6F7):
notification-once PASS, TaskStop full-tree kill PASS, timeout NOT
binding background (45s ran natural under timeout=6000), natural
deny→re-call PASS; **P4 (session-end survival) armed** — a bounded
straggler probe is left running at v25 close for the next session to
check via tasklist (details in the v25 checkpoint).

The v26 session (2026-09-24, designation jason-extended-cognition,
**long-running mode entered turn 3** with standing-delegated per-batch
H2 per the owner's verbatim "现在开始这个会话委托你H2，直到我明确驳回授权")
landed the **Workspace Dependency Resolution program as law**:
qiven-docs PR #2 (five signed cross-LLM deliberation rounds: GPT-5.6
Sol author; GPT-6 Codex x3; GLM-5.3 x2, the last a convergence verdict)
was **accepted by owner adjudication** ("PR2 accepted"), merged
`4423635`, documents migrated to `accepted/2026-09-24/` (`7fe0df7`);
**ADR-0052 ACCEPTED** records the canonical adoption (ADR-0046 layer
model retained, its dependency-resolution endpoint superseded; TCA
CA-1 lock authoritative until WR-7; WR-0 sealed outputs gate every
authority-touching step; program stall/budget law) — this is the FIFTH
ADR accepted since the 2026-09-22 pass, so the **periodic governance
audit is now DUE**. The WR migration is tracked by
OBL-20260924T113000Z-E7F8A9 (WR-0 census + Profile B fixture + Profile
J baseline + sealed effort budget is the next bounded implementation
batch; control-repo creation and class cutovers are owner-gated).
**P4 re-adjudicated after power forensics**: the owner's challenge
was right that a power-down existed (Modern-Standby suspend
2026-09-23T23:23Z → wake 2026-09-24T09:31Z; boot-class queries miss
suspend-class transitions — MEM-20260924T113500Z-D8E9F0), but the
wake-completion argument proves the v25 probe died INSIDE the awake
window before the suspend: session-end kill strongly supported by
elimination, confounded as a clean proof → **P4B re-armed with the
mandatory power-timeline read-out protocol** (OBL-…-D5E6F7 stays open).
The **2026-09-24 mvp4 H1 kit pre-flight failure is sealed**
(evidence/audits/2026-09-24-mvp4-h1-kit-preflight-incident.md;
root cause: CWD-derived host profile default + kit shipped without
config/profiles; session-side verification environment ≠ owner-live
double-click environment — MEM-20260924T113000Z-C7D8E9; fix
owner-deferred; owner restored the workspace hook config to a minimal
safe state with the router disabled). v25 timestamp noise (+24h on
several Z-stamps) is corrected in the v26 checkpoint notes.

The v27 session (2026-09-25, designation jason-extended-cognition,
**long-running mode from turn 1** with standing-delegated per-batch H2
per the owner's opening instruction "全程委托你H2…完整执行和落地这一个
边界直到下一次H1，其中WR0获批同意WR1") executed the directed boundary:
**WR-0 sealed outputs owner-ACCEPTED and WR-1 AUTHORIZED; WR-1 DELIVERED
end-to-end in shadow mode.** Landed: devkit PR #35 (`1a54d59` — the
three workspace schemas + stdlib strict validator with duplicate-key
rejection, self-test S1-S13), PR #36 (`672694c` — the resolver: RFC 8785-
subset canonicalization with UTF-16 key ordering, domain-separated
sha256 WorkspaceGeneration, census blob+digest binding, WG-4 edge
validation, Profile B conflict detection order-independent, §11 typed
failure taxonomy incl. UntrustedControlRevision/BootstrapDevkitMismatch/
BaselineConflict, golden vectors with two independent implementations +
certutil three-way agreement, self-test R1-R11), PR #37 (`e4000ff` —
the REAL-bootstrap contract test B1-B7 with identity-before-import and
visible-SKIP self-containment; schema note fields; router
re-classification of the new launcher forms), plus a typed-
WorkspaceNotFound fix (P5 probe finding). **qiven-workspace control
repository PUBLISHED** (`JasonHuang3D/qiven-workspace`, public, `4b68079`):
manifest, sealed WR-0 census declarations bound to live main HEADs,
generation-bound lock (`sha256:687673bc…`, path-independence proven by
clone probe), stdlib bootstrap + thin qiven.cmd. Real-workspace probes
P1-P5 PASS (authoritative-without-policy → UntrustedControlRevision;
real bootstrap release with 12 validated edges; wrong devkit →
BootstrapDevkitMismatch BEFORE import; clone → identical generation;
absent control → typed WorkspaceNotFound after the fix). The baseline
devkit implementation split (context d1d2a3a4 vs managed snapshots vs
main) is reported as a typed baseline conflict — recorded, not resolved.
**Disclosed deviation**: control-repo skeleton 247 lines vs the sealed
≤200 row bound (47 over; bootstrap contract accounts for it; no product
semantics) — for the owner's WR-1 review; no authority cutover was
requested or made. Budget: 4 of 6 devkit PRs, 1 of 2 sessions. **The
control-repository trust policy is DRAFTED as proposed**
(governance/workspace-control-trust-policy.json): its owner-H2 acceptance
+ first admitted revision is THE next H1 stop; until then the control
repository is shadow-only. Router FINDING (pre-existing, disclosed):
path-prefixed `qiven.cmd gate` spellings escape gate-class (v4.1
prefix-anchored matcher) — follow-up devkit batch candidate.

**Turn 2 (same session, owner verbatim "H1通过，接受会话")**: the H1 stop
is PASSED and the session closeout / WR-1 outputs are ACCEPTED. The
trust policy is now ACCEPTED with admitted control revision
`1743d921…` (qiven-workspace main at window close); probes on the real
workspace prove the trust gate mechanically lifted (A1/A2: authoritative
mode now reaches the typed `BaselineConflict` on the recorded devkit
split — the honest state; no authoritative graph until WR-6/pin
reconciliation) and the admission list enforced (A3 negative control →
`UntrustedControlRevision`). Residuals recorded in the policy file: the
routine-advance rule is undefined and must be owner-ratified before the
first routine authoritative-consuming lock movement (WR-2+).

**Turn 3 (same session, owner verbatim "好的WR2 启动")**: **WR-2 DELIVERED
and closed** at exactly the sealed budget (2 devkit PRs / 1 session):
PR #39 (`d36ffb6` — shadow preflight + legacy-pin comparator with
per-class typed verdicts; unknown pin variables are typed
PinExtractionAmbiguous, never silently dropped) and PR #40 (`47c49a2` —
the sealed Profile B fixture wired as the PERMANENT regression with
outcomes 1-5 + K complement; the minimal candidate-declaration
validation for the architecture §5.1 overlay; the live wr2-report.md).
Live per-class verdicts on the real workspace: **Foundation / Draft /
ThirdParty classes at equality (cutover-eligible at WR-3/WR-4/WR-5)**;
the Devkit class is an explicit shadow discrepancy with a WR-6
disposition (context pin `d1d2a3a4` vs lock snapshot `3c638b5`, managed
snapshots non-comparable); census temporary records carry replacement
stages + the hard WR-8 gate; the CA-1 clause recorded N/A. Fresh
corroborating `qiven-math` gate PASS (legacy root+pin CMake path green
alongside the shadow layer). **Next owner decision point (the sealed
budget's): authorize the first class cutover — WR-3 Foundation — as the
Profile J pilot.**

**Turn 4 (same session, owner-directed orchestrated fresh-review round)**:
first exercise of the subagent workflow (fresh review → fresh fix →
fresh round-2 verification; R2 class per the ADR-0050 amendment; no
authority transfer; normal gate discipline). Round 1 found **8 genuine
issues (3×P2 + 5×P3, zero false positives)** incl. a shadow-extractor
hardcoding that could fake the WR-3 equality evidence; 7 fixed in devkit
PR #41 (`ef4ea30`, gate PASS at `405d0a8`, regressions R12-R15/SH8/S14,
authored by the fix subagent as `LLM: GLM-5.3-flash`); round 2 verified
7/7 RESOLVED, no regressions. F1 (bootstrap timeout typing) DEFERRED to
the routine-advance decision (fixing it would move the trust-admitted
control HEAD). Two new P3 observations recorded (managed-snapshot list
residue; census path coupling). Consumption CORRECTED (turn 5): the subagents
actually served GLM-5.3 — paid, modest — because a mid-session
subagent-model config change does not take effect (owner-verified
platform fact; the PR #41 flash trailer is corrected by record, history
untouched); orchestrator cost = three compact reports — the workflow
remains repeatable at negligible orchestrator cost.

**Turn 5 (same session)**: platform-fact correction recorded (above);
**ADR-0053 DRAFTED (proposed)** per owner direction — the three ZCode
roles concretized as a view-level advisory division of labor
(worker=subagent embodiment, briefed not booted, no governance;
brother=design/check/context-maintenance, cold boot, no governance;
extended-cognition=main-only, governance-context authority under owner
approval, human highest), ADR-0044's non-partition clause preserved,
one engineering law for all roles, no AGENTS.md role text, the
absolute no-LLM context-destruction red line (owner-hands-only class),
delegation law extending the ADR-0050 orchestration boundary to
implementation, and the recall mechanism (view trigger table + workflow
patterns; router nudge as a revisit candidate). No view/workflow files
land before owner acceptance; adjudication is batched with the DUE
governance audit in the owner's next fresh session.

**Turn 6 (same session)**: two rulings folded into the still-proposed
ADR-0053 — (1) the brief completeness law (§5a): mandatory brief
template with role card + scoped engineering-law reading list +
worker-side acknowledgment duty; worker cold boot REJECTED (would
destroy the clean-context/noise-exclusion property; worker reads
engineering law, never boots project cognition); (2) the preflight
freshness canary (§5b): routine boundary tripwire under the ADR-0050
orchestrated-boundary carve-out, honestly labeled (same-family,
instruction-scoped read-abstention; invalid for acceptance-grade
isolation classes), leakage ⇒ stop + owner escalation; hook variants
owner-hands in the UI. First live canary PASS (knows_qiven=no, sealed
artifact verified, ~28K tokens) — retroactively corroborating the
turn-4 boundary.

## Accepted engineering checkpoints

- ContextKernel K1-K4 (Python, sealed ADR-0040): K4 Canonical Artifact
  Handoff accepted at `decc769a`; Context v4 frozen 2026-09-21.
- C++ architecture + Runtime design + Component ADL: ADR-0039/ADR-0038
  landed; RCA-0..RCA-16 complete (foundation `38f0eb2`, runtime through
  `88475983`; RCA-14 H1 accepted).
- MVP-1 exit gate PASSED (v18): SQLite RuntimeJournal + recovery
  skeleton; all five §15 rows proven; crash-injection deterministic at
  all 7 journal commit points.
- MVP-2 exit gate PASSED (v19): all five §15 rows proven by real-git
  fixtures — dirty checkouts cannot affect a pinned generation; bundle
  tampering fails loading; revision vs content digests separately
  visible; generation change invalidates old unconsumed tokens
  (advance_generation stale extension); rich records ride byte-exact,
  never lossy-converted into the v8 snapshot. The K5 uncompressed
  delivery reference exists (bundle source files).
- MVP-3 exit gate PASSED (v19): owner-only DACL (readback-pinned) +
  client-image admission; replay/HMAC/bounds classes denied typed;
  mutation kinds deny typed 61; timed-out child TREES reclaimed
  (Job Object); 1.7 MB flood vs 1 MiB cap fails typed 73. The live
  cross-user connect is the recorded MVP-7 H1 runbook remainder.
- MVP-4 NOT ACCEPTED (reclassified 2026-09-23 per ADR-0050):
  implementation exists and rows 2-5 are locally proven, but the real-H1
  exit gate failed three owner trials; the bounded corrective lane
  (incident pack, connection-model decision, denial taxonomy split, kit
  pre-flight, real H1 rerun) owns closing it.

## Corrected continuity model

Project Continuity defines the reconstruction outcome; delivery
profiles are separate properties: remote cold boot (exact canonical
ref), session checkpoints (bounded progress evidence), Canonical
Artifact Handoff (isolation-boundary artifact causality), Human
Succession (operator replacement). A PASS names the profile tested.

## Authority and safety

- GitHub remote is canonical; local clones are non-authoritative
  working materializations; no authority cutover has occurred.
- Governance authentication is GitHub account level
  (`governance/authority.yaml`); root principal `github:JasonHuang3D`.
- qiven-host and qiven-dcr-win are SEALED (ADR-0043); machine-local
  governed mutation means the RuntimeHost execution-authority subsystem.
- ContextViews adapt interaction/environment/workflow and never override
  project truth or governance.

## Accepted governance state

- ADR-0035/0036: model/binding separation; typed handoffs H1-H4,
  no-verbal-waiver, unattended read-only default.
- ADR-0040/0041/0042: ContextKernel sealed; museum disarmament; legacy
  consolidation (`.generated-temp/` is the only generated-artifact
  location).
- ADR-0044 (2026-09-22): single-session unified engineering; role
  packages are attribution/qualification labels, not behavioral stages.
- Extended-cognition designation: no model binding (owner-invoked;
  switch-time live-model report) — ADR-0045.
- Long-running mode is the unified "continue unless H1" workflow
  (`views/workflows/long-running.md`; contract anchor in
  `collaboration/human-handoff-boundary.md`).
- ADR-0046 (2026-09-22): infrastructure layer model — toolchain ->
  devkit -> all repositories; engineering standards Devkit-canonical;
  qiven-context consumes the operator via shim+pin.
- ADR-0047 (accepted): Production MVP architecture; the qiven-context
  canonical machine-readable policy instance exists
  (`runtime/invocation-policy.yaml`, validator-pinned to the frozen v4
  rule table).
- ADR-0048 (ACCEPTED 2026-09-23T09:05Z, owner H2 in the v21 session):
  bounded process custody is the law for every Qiven tool that spawns
  processes (exec v2: watchdog + KILL_ON_JOB_CLOSE Job Object + lease;
  completion reap; sweep insurance). Governing incident evidence:
  `evidence/audits/2026-09-23-exec-process-leak-incident.md`.
- Devkit Python engineering standard is canonical
  (`qiven-devkit/docs/engineering/python-standard.md`, landed with the
  custody rebuild).
- ADR-0050 (accepted 2026-09-23T18:56Z, owner H2 in v22): TCA program +
  independent falsification. Canonical homes:
  `collaboration/cognitive-governance-program.md`,
  `collaboration/cognitive-effectiveness-acceptance.md`,
  `qiven-runtime docs/architecture/task-cognition-activation.md` and
  `runtime-mvp-roadmap-amendment.md` (bound at merge `f0ca5b7`);
  deliberation record qiven-docs PR #1 (seven passes, corrections
  R1-R15; accepted copies under qiven-docs `accepted/2026-09-23/`);
  companion selector manifest `runtime/cognition-landing-manifest.yaml`;
  handoff amendment applied to `collaboration/human-handoff-boundary.md`;
  program obligation `OBL-20260923T190500Z-D6E7F8`.
- ADR-0051 (ACCEPTED 2026-09-24T~11:50Z, owner H2 in v26, verbatim
  "ADR0051批准"): harness-native background execution is the default
  session path for long commands (deny -> run_in_background re-call +
  node-reuse guard); Operator exec scoped to survival/durable/custody
  classes; oversized foreground output bounded natively. Residual R1
  (P4 session-end survival) remains open with outcome-independent
  mitigations. Workspace router registration re-enabled 11:43Z
  (effective for sessions started after).
- ADR-0052 (accepted 2026-09-24, owner adjudication of qiven-docs PR
  #2 in v26): Workspace Dependency Resolution program; ADR-0046 layer
  model retained with its dependency-resolution endpoint superseded;
  WR-0 sealed outputs gate every authority-touching step
  (OBL-20260924T113000Z-E7F8A9).
- Public-repo information hygiene is LAW (2026-09-24, owner direction,
  v26 turn 6; `collaboration/public-repo-information-hygiene.md`): all
  nine qiven repositories are public; canonical records carry
  placeholder categories + live-resolution procedures, never
  machine-identity literals; secrets scan clean; active surfaces
  redacted 2026-09-24; the git-history residual is an owner
  public-accept vs private decision (recorded in the law).
- Workspace control-repository trust policy ACCEPTED (2026-09-25, owner
  H1/H2 pass in v27 turn 2; `governance/workspace-control-trust-policy.json`):
  permitted control repository `JasonHuang3D/qiven-workspace`, admitted
  revision `1743d921…`; authoritative bootstrap additionally requires a
  compatible selection (the typed BaselineConflict on the context devkit
  pin is the standing blocker until WR-6/pin reconciliation); routine-
  advance rule pending owner ratification before routine authoritative
  lock movement.

## 2026-09-23 deny-118 incident correction wave (v21, owner-directed)

The first MVP-4 H1 kit (prose form) had the owner hand-configure hooks
and REQUIRED an assumed payload field the real harness never sends —
every tool call in a fresh owner session denied 118. Owner emergency-
disabled the hooks; corrections landed the same turn: runtime PR #51
`62fe0ae` (template-trust identity, human-facing host output,
the H1 kit package builder tool (qiven-runtime), deny-118 regression case), devkit
PR #28 `b935926` (the H1-kit standard), incident audit + MEM-
20260923T115500Z-A1B2C3 + ADR-0049 ACCEPTED by owner H2 2026-09-23T12:45Z (same-day, after trial 2). The
workspace config was written directly by the session (ZCode UI review
is the enable gate); the regenerated kit package is at
<workspace-root>/h1-kits/qiven-runtime/mvp4-h1/0.1.0-ge0614b82.

## Public history boundary (2026-09-24)

qiven-context's public history was truncated at owner direction: main
now begins at boundary commit `c6bf3e3` (tree identical to the archived
head `8d6c929`, 682 commits); the complete pre-boundary history plus
every preserved sealed-era work branch lives in the private archive
`JasonHuang3D/qiven-context-back-up-9-24-2026`. SHA references in
records dated before the boundary resolve against that archive; **PR
numbers in old records resolve to the archive's merge commits**
("Merge pull request #N" message-bound), because the PR objects died
with the owner's deletion of the old public repository. The owner then
resolved both disclosed residuals root-cure style: the third-party fork
(a family account) was deleted by the owner, and the old public
repository itself was deleted and RECREATED fresh (public, same name)
— `refs/pull/*` caches died with it. The new public repository carries
only the boundary line. **PR objects are RETIRED for qiven-context**
(owner direction 2026-09-24): publication = branch → gate PASS at exact
head → local merge to main → push; receipts ride the gate result +
merge commit + session checkpoint (human-handoff-boundary.md amendment).
qiven-docs keeps its PR-based cross-LLM deliberation law. The remaining
repositories follow per
`collaboration/repository-history-archival.md`
(OBL-20260924T140500Z-F0A1B2; code repos require the re-pin ripple).

## Next boundary

1. **WR-3 Foundation cutover decision** (the sealed budget's owner
   decision point 2; equality proven by the live WR-2 report): the
   first class cutover, doubling as the Profile J pilot measurement.
2. **Routine-advance rule** (owner decision before the first routine
   authoritative-consuming lock movement — now concretely needed by any
   WR-3 lock movement): ratify an admission-advance rule for control
   revisions or re-admit per movement — the standing residual recorded
   in the trust policy.
3. **Periodic governance audit DUE** (SIX ADRs accepted since the
   2026-09-22 pass: 0047/0048/0049/0050/0051/0052).
4. **The MVP-4 corrective lane** (owner-scheduled): rebuild/fix the H1
   kit (profile packaging or CWD-independent resolution; the sealed
   incident record names both defects), then the real H1 rerun (owner
   hands). Rows 2-5 of the original exit gate remain locally proven.
5. **RR-0 implementation batch** (still inside the open CA interval),
   then **CA-1** (its bounded batch, ceilings and stall trigger are
   unchanged by ADR-0052). MVP-5 stays FROZEN until CA-2.
6. Router follow-up candidate (disclosed finding): path-prefixed
   `qiven.cmd gate` spellings escape gate-class under the v4.1
   prefix-anchored matcher — a bounded devkit router batch.
7. Standing: managed template syncs need manual operator.json customs
   re-applied per bump (runtime and context-draft carry customs); the
   workspace router registration is enabled (effective for sessions
   started after 2026-09-24T11:43Z); git-network routing remains
   suspended at the router per owner direction 2026-09-24; qiven-context's
   devkit pin remains d1d2a3a (bump optional at next touching batch;
   census-recorded split, WR-6 reconciliation target; the standing
   typed BaselineConflict); the lock's devkit node records the WR-1
   snapshot while devkit main advanced during WR-2 (shadow comparison
   is snapshot-based and unaffected);
   the P4 probe lineage is TERMINALLY closed (see
   collaboration/agent-execution-topology.md §3 — no next-session probe
   duty exists).
