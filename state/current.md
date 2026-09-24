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
records dated before the boundary resolve against that archive.
Disclosed residuals: one stale third-party fork (created 2026-09-17)
and GitHub PR-ref caches (full purge = owner support request, optional).
The remaining repositories follow per
`collaboration/repository-history-archival.md`
(OBL-20260924T140500Z-F0A1B2; code repos require the re-pin ripple).

## Next boundary

1. **Owner review of the WR-0 sealed outputs** (devkit PR #34: census,
   Profile B fixture, Profile J baseline, effort budget) gates WR-1
   (qiven-workspace creation); the cheaper no-repository subset remains
   compatible.
2. **Periodic governance audit DUE** (SIX ADRs accepted since the
   2026-09-22 pass: 0047/0048/0049/0050/0051/0052).
3. **The MVP-4 corrective lane** (owner-scheduled): rebuild/fix the H1
   kit (profile packaging or CWD-independent resolution; the sealed
   incident record names both defects), then the real H1 rerun (owner
   hands). Rows 2-5 of the original exit gate remain locally proven.
4. **RR-0 implementation batch** (still inside the open CA interval),
   then **CA-1** (its bounded batch, ceilings and stall trigger are
   unchanged by ADR-0052). MVP-5 stays FROZEN until CA-2.
5. Standing: managed template syncs need manual operator.json customs
   re-applied per bump (runtime and context-draft carry customs); the
   workspace router registration is enabled (effective for sessions
   started after 2026-09-24T11:43Z); git-network routing remains
   suspended at the router per owner direction 2026-09-24; qiven-context's
   devkit pin remains d1d2a3a (bump optional at next touching batch);
   the P4 probe lineage is TERMINALLY closed (see
   collaboration/agent-execution-topology.md §3 — no next-session probe
   duty exists).
