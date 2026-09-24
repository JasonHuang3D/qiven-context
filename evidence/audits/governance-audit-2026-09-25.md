# Periodic Governance Audit — 2026-09-25 (v28 session)

Trigger: OBL-20260922T160000Z-C8D4E2 (five ADRs since the 2026-09-22
pass). SEVEN ADRs stood accepted since that pass when this audit began
(0047, 0048, 0049, 0050, 0051, 0052 — plus 0053 accepted by owner H2
in this session's first transaction, batched with this audit as the
ADR's Status note declared). Executed under long-running mode with
standing-delegated per-batch H2 (owner opening instruction v28).

## Method (per the institutionalized 2026-09-22 method)

1. Fresh-review worker subagent (R2 class) read EVERY active surface:
   root contracts (4), all 30 collaboration/ files, all 10 views/
   files, state/ (4), governance/ (3), memory + obligations + decisions
   indexes, and ADR-0047..0053 in full — with a mandatory 8-section
   brief per ADR-0053 §5a (role card v1). Canary §5b run FIRST
   (knows_qiven=no, nonce V28-CANARY-T1, leakage_check=no, artifact
   `.generated-temp/canary/v28-turn1.md` verified) — the
   orchestration boundary held.
2. Orchestrator triage of every worker finding (load-bearing claims
   re-verified against the tree; external canonical homes
   spot-verified by the orchestrator — all exist, see below).
3. Programmatic staleness sweep (orchestrator): YAML health of all
   state/views/governance/index files (PASS); cross-file duplicate
   `##` section titles (4 hits, all generic heading names in unrelated
   documents — benign, no divergent rule definitions, matching the
   worker's C3-none verdict); active-text reference existence check
   (all apparent misses were sweep-regex prefix artifacts; every
   reference resolves, including `legacy/` paths).

## Findings (triaged: 11 genuine, 0 false positives)

Classes: C1 contradiction / C2 drift / C3 duplication / C4 gap.

| ID | Class | Sev | Finding | Disposition |
| --- | --- | --- | --- | --- |
| C2-1 | drift | P2 | operating-contract.md long-command heading + rule 5 said ADR-0051 "PROPOSED" after its acceptance | FIXED this batch (ACCEPTED wording) |
| C2-2 | drift | P2 | long-command-registry.md header said ADR-0051 PROPOSED / ratification pending | FIXED this batch |
| C2-3 | drift | P2 | state/current.md still described ADR-0053 as proposed and counted SIX audit-due ADRs | FIXED in the v28 closing state transaction (same session) |
| C2-4 | drift | P2 | state/active-work.yaml current_candidate/next_boundary described the pre-acceptance world | FIXED in the v28 closing state transaction |
| C2-5 | drift | P2-borderline | views/workflows/long-running.md directed delegated-H2 receipts into "each PR" (PR objects retired for qiven-context 2026-09-24) | FIXED this batch (receipt vehicle named per repo) |
| C2-6 | drift | P3 | views/workflows/supervised-agent.md PR-language stale for qiven-context (3 spots) | FIXED this batch (repo-law qualified) |
| C2-7 | drift | P3 | views/README.md layout tree omitted subagent-delegation.md | FIXED this batch |
| C2-8 | drift | P3 | views/humans/jason.yaml used_by omitted extended-cognition-jason | FIXED this batch |
| C2-9 | drift | P3 | cognitive-effectiveness-acceptance.md described the pre-ADR-0050-amendment contract as "current" | FIXED this batch (historical wording) |
| C2-10 | drift | P3-borderline | state/repositories.yaml qiven-workspace role cited the pre-acceptance trust-policy state | FIXED this batch (typed BaselineConflict + routine-advance named as the operative blockers) |
| C4-1 | gap | P2-borderline | decisions/ADR-0049.md frontmatter carried a DUPLICATE `sources:` key (YAML last-key-wins silently shadowed the first provenance block) | FIXED this batch: mechanically merged into ONE sources key with all four items in original order; lifecycle fields (status/supersedes/superseded_by) untouched — record-integrity repair under delegated H2, disclosed here and in the commit message for owner veto |

C1 (contradictions): none. C3 (duplication): none beyond benign
generic headings. Index integrity: decisions 53/53, memory 80/80,
obligations 44/44 referenced files exist; no orphans.

## ADR-by-ADR verification (0047-0053)

For each ADR: frontmatter status == decisions/index.yaml (all match);
named canonical homes existence-checked — in-tree homes by the worker,
cross-repository homes by the orchestrator: devkit
`docs/engineering/python-standard.md` + `docs/engineering/h1-kit.md`,
runtime `docs/architecture/task-cognition-activation.md` +
`runtime-mvp-roadmap-amendment.md`, qiven-docs `accepted/2026-09-23/`
(5 files) and `accepted/2026-09-24/` (3 files), qiven-workspace control
repository (remote main == admitted revision 1743d921, verified at
cold boot), evidence/audits incident files (3) — ALL EXIST.
Supersede chains: all seven carry empty supersedes/superseded_by
consistent with their texts (0052 supersedes an ADR-0046 *endpoint* by
prose, not a whole-ADR supersede — consistent).

## ADR-0053 landing verification (dual-purpose with this audit)

Landed at aeda32e / main c4c4983 BEFORE this audit's delegation round:
zcode-jason.yaml roles section (advisory table + boot layering +
delegation trigger table + red line), extended-cognition-jason.yaml
recall pointer (mount-gap found and closed during landing — an
extended-cognition session loads THAT view), subagent-delegation.md
(classes, 8-section brief template, role card v1, canary, orchestrator
duties, heuristics, platform facts). LIVE EXERCISE this audit: canary
PASS (above); fresh-review worker (semantic audit) — 11/11 findings
genuine, acknowledgment section surfaced its own deviations honestly
(Glob-unavailable fallback; /tmp listing slip, self-deleted);
fresh-fix worker (remediation) — 12/12 edits applied with one
wrapping-adaptive anchor disclosed with observed text. Both briefs
contained all 8 mandatory sections. The §5a mechanism (template +
acknowledgment + triage) worked end to end on first live use.

Worker consumption: reviewer ~3.85M subagent tokens / 75 tool uses /
~7.2 min; fixer ~0.56M / 28 / ~2.7 min; canary ~0.03M. Orchestrator
input cost: two briefs + two reports. (Attribution: both workers and
the canary ran as GLM-5.3-served general-purpose subagents on the
offpeak plan, foreground.)

## Remediation receipts

This batch (branch jason-extended-cognition/v28-governance-audit):
C2-1/2/5/6/7/8/9/10 + C4-1 fixed; gate PASS at the exact head; merged
to main. C2-3/C2-4 ride the v28 closing state transaction (the state
surfaces are rewritten there anyway; recording-only, no semantic gap
remains once it lands). No finding was deferred beyond this session.

## Abstentions

The worker did not audit ADR-0001..0046 bodies, memory/obligation
record bodies, sessions/, evidence/ content, legacy/, or tools/ (out
of its brief; index-existence checks covered the record classes).
Platform facts (hook router live behavior) verified by direct
invocation during this session, not by the worker.
