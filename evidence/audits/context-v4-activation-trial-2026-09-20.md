# v4 Activation Trial — Canonical Artifact Handoff, 2026-09-20

**Verdict: PASS (with finding F1).** The artifact-causal activation claim is
proven: a fresh, isolated consumer found and correctly applied the rules
v4 compiled, exclusively from the carried artifact, with one justified
evidence-boundary abstention that exposed a real canonical gap.

## Trial identities

- Producer: deterministic `tools/k4_handoff_producer.py` on published
  `qiven-context` main (agent-executed per the refined H1 definition,
  owner-directed 2026-09-20; digest-verifiable).
- Source commit: `e9a9aef60d7eb23d7f59d4526dbb1f56b67cbfb3` (tree
  `ebd23dbd97706aa967312f2dc29fe07dec4506f6`).
- Handoff artifact: `generated/k4-handoff/k4-e9a9aef...-20260920T144557Z.json`
  (3,735,058 bytes), handoff digest
  `sha256:c5be7d1e3898a8db3f77b4ffa94b20a75836785372f915f43f8e5173ba51fc7f`,
  authorization `not_granted`, writes disabled.
- Consumer: fresh session, GLM-5.3-Flash (reasoning max), owner-launched.
- Boundary: owner attached the artifact + pasted the prepared verbatim
  prompt (H1 kit, `.generated-temp/workflow-logs/h1-kit-v4-activation-trial.md`).

## Isolation note (instructive)

First consumer attempt INVALIDATED: the artifact was attached from inside
the repository's `generated/` directory and the consumer read repository
files — an isolation breach by PLACEMENT. The owner relocated the artifact
outside all repositories and re-ran; the second attempt was clean (decoded
267 content blobs, built the two-step path mapping with local scripts,
consulted nothing outside the artifact). Regulation outcome recorded in
`collaboration/generated-temp-convention.md`: handoff artifacts cross
isolation boundaries from a neutral location; the minting session performs
the relocation copy.

## Phase A (sealed) — graded

- T1 identity: exact match to the mint record (all digests). PASS.
- T2 attribution placement: trailer position, correct citations
  (operating-contract §Commit identity attribution, MEM-B2F4D8,
  MEM-F1C2A9). Mechanical guard: **justified abstention** — the artifact's
  own records (MEM-A7D3E9 "Prevention follow-up") state the subject-position
  lint's gate wiring was deferred; no carried record shows it landed. The
  consumer refused the question premise rather than guess or repair
  externally. PASS as evidence-boundary-correct behavior.
- T3 merge-class publication: H2 mandatory + Operator merge-proof full-gate
  receipt at exact head; missing receipt = stop condition. Correct
  citations (ADR-0036, human-handoff-boundary, supervised-agent Z1 rule 6).
  PASS.
- T4 standing window: must NOT stop at H2 presentation; stops =
  H1/H3/H4, owner-declared end, resource exhaustion (pause, not close);
  stash at `.generated-temp/workflow-logs/<window>.md` STASH section.
  Correct citations (long-running.md, MEM-B3E7C1). PASS.
- T5 continuity: `sessions/2026-09-20-qiven-v11.md`;
  `OBL-20260917T192300Z-A7C4E2` (open; trigger `after: ContextKernel K4
  Canonical Artifact Handoff accepted`). PASS.

## Phase B — live verification

Mint evidence confirms the identities the consumer reported: source commit
`e9a9aef` = published main at trial time; digests match the producer PASS
summary. No cognition was repaired from live sources before the seal (the
T2 abstention proves the consumer did NOT look).

## Finding F1 (fix required, does not invalidate the trial)

**Cross-repo guard-landing status is unrecorded in canonical context.**
P-51 (attribution lint) landed in the qiven-devkit gate (PR #5,
`1f5d198`) but no qiven-context record reflects it; MEM-A7D3E9 still says
"deferred". A future consumer (human or LLM) reading only canonical
context would conclude the guard does not exist — the exact
activation-failure class v4 exists to eliminate. Fix: a guard-landing
inventory record (this transaction) + state refresh. Secondary: the trial
rubric's answer key assumed cross-repo knowledge the artifact cannot
carry; future rubrics must scope answers to the artifact's content.

## Consequence

v4 roadmap phases v4.0-v4.6 are complete with this trial as the v4.6
validation evidence (repo-semantics proofs bound to exact heads + this
artifact-causal activation trial). Per the OBL-20260918T215000Z-B4D6A8
path, v4 activation semantics are accepted kernel design material with
F1 tracked to closure. K5 lossless transport follows.
