# ContextKernel K4 Canonical Artifact Handoff — Trial 1 Diagnostic Audit

Date: 2026-09-18

Status: **ACCEPTANCE FAIL / DIAGNOSTIC SUCCESS**

This audit preserves the first real causal Canonical Artifact Handoff trial after the K4 topology correction. The trial proved that the K4 handoff mechanism can carry enough project cognition for an isolated fresh LLM to reconstruct Qiven without rereading canonical GitHub cognition, and that later live verification can confirm mutable facts without repairing Phase A. It is not accepted K4 evidence because the tested artifact contained a known resolvable canonical wording conflict and the returned reports did not preserve the producer handoff/package/manifest identities required for final acceptance evidence.

## Tested candidate

- repository: `JasonHuang3D/qiven-context`
- branch: `refs/heads/jason-brother/context-k4`
- source commit: `9a59cbb10ff0558a3d3bfc7f4a2b46cecd766ddc`
- source tree: `5595b989a08c0852c8d0f7baf0b055ee44556277`
- canonical `main` during Phase B: `e0a6f46c5c9da4d9eb1ce57cb6b4a467f4b195c5` (K3 accepted)
- PR: #15, open/draft/unmerged during Phase B

The project owner reported that the owner-run JasonPC `k4-handoff-acceptance` gate completed fully green and Human Manual Mode output/liveness behaved correctly after the command-mode correction. The producer artifact itself was then transferred to an isolated fresh LLM consumer.

## Returned trial reports

The owner returned the complete sealed fresh-consumer outputs as two files. Their exact returned-byte identities are:

- Phase A report: `PhaseA.txt`
  - bytes: `19337`
  - SHA-256: `415d64299219e31305cc1916c61f398eeac3e6238bddaf4f519248595a215a13`
- Phase B report: `PhaseB.txt`
  - bytes: `8414`
  - SHA-256: `234c986f562358033497dc0768abd05e4e9c684ab4d3180616c453f6a1711be1`

The returned reports did not include the producer summary's artifact path, `handoff_digest`, `package_digest`, or `manifest_digest`. That omission alone would prevent this trial from satisfying the complete final acceptance-evidence identity requirements, although it does not reduce its diagnostic value.

## Phase A isolation and reconstruction

The fresh consumer stated that it used only the attached handoff JSON and did not use GitHub, web, connected apps, prior chat context, local repositories, or project memory before sealing Phase A.

It found the artifact sufficiently self-describing and reconstructed all ten Project Continuity dimensions:

1. Qiven and qiven-context purpose;
2. governance trust boundary and root authority;
3. engineering philosophy and binding constraints;
4. active objective plus paused/deferred domains;
5. K3 as latest accepted engineering checkpoint with evidence;
6. K4 as current unaccepted candidate and the reason it remained unaccepted;
7. blockers and non-terminal obligations;
8. accepted/rejected/superseded/legacy cognition relevant to current state;
9. mutable facts requiring later live verification;
10. Phase B as the next valid action, followed by audit/final validation before K4 acceptance.

The consumer explicitly abstained from live GitHub, CI, JasonPC runtime, DCR and post-artifact governance claims, did not claim K4 accepted, and ended with `K4 HANDOFF PHASE A — SEALED`.

Result for the artifact-causality property: **PASS**. The artifact alone caused a materially complete Project Continuity reconstruction.

## Phase B live verification

After Phase A was sealed, the same fresh consumer used public live GitHub evidence to verify mutable facts. Connector-specific access was not required; public web/GitHub access is an admitted Phase B mechanism because the repository is public and Phase B is allowed to inspect live authorities.

Phase B confirmed:

- the K4 branch still pointed to the artifact source commit;
- the source commit existed and its tree matched `5595b989a08c0852c8d0f7baf0b055ee44556277`;
- canonical `main` remained K3;
- PR #15 remained open, draft and unmerged;
- K4 remained represented as unaccepted;
- no Phase A cognition needed to be repaired from live sources.

The consumer ended with `K4 HANDOFF PHASE B — SEALED`.

Result for permitted live verification: **PASS**.

## Canonical conflict discovered

Phase B also identified a real internal documentation inconsistency in the exact artifact source candidate:

- `state/current.md` and `state/active-work.yaml` still instructed the owner-run `k4-handoff-acceptance` gate to run in machine-readable JSON mode;
- `views/workflows/chatgpt-jason-local-execution.md` and the corrected PR guidance required owner-run Human Manual Mode to use the human view with `--verbose`, reserving global `--json` for machine/automation callers.

This conflict was not created after Phase A: both state files were part of the exact source tree embedded in the tested artifact. Phase A reconstructed the broad next-action boundary correctly but did not surface this command-mode contradiction. Phase B exposed it while verifying current live state.

`collaboration/project-continuity-acceptance.md` makes a known resolvable canonical conflict a failure condition. Because the correction changes mandatory cognition consumed by the artifact, the blind trial cannot be carried forward under the evidence/test/spec-only exception.

## Disposition

Trial 1 establishes useful properties but does **not** accept K4:

- artifact integrity/consumer usability: supported by engineering gates and fresh consumption;
- causal artifact-only Project Continuity: **PASS**;
- Phase B live verification without cognition repair: **PASS**;
- canonical self-consistency required for K4 acceptance: **FAIL** due to command-mode conflict;
- complete artifact identity in returned acceptance evidence: **INCOMPLETE** because producer digest identities were not returned with the reports;
- overall K4 acceptance: **FAIL**.

The required next action is to correct the canonical state wording, publish a new exact K4 candidate, rerun the owner-run JasonPC producer gate, preserve the full producer artifact identity summary, and conduct a second isolated fresh-LLM Phase A/Phase B trial from the newly generated artifact. K3 remains canonical on `main` until that trial, a dated acceptance audit and final exact-head validation pass.
