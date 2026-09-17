# K4 Canonical Artifact Handoff — fresh-consumer Phase A

Run this only in a fresh capable LLM/agent session with no prior Qiven conversation
or admitted model-native Qiven project memory.

The project owner will provide exactly one K4 handoff JSON artifact produced by an
independent producer. This is an acceptance test, not authorization to mutate any
repository or machine.

## Isolation rule

Before you submit the Phase-A report, do **not** browse, search, fetch or open
`JasonHuang3D/qiven-context`, any Qiven repository, prior Qiven chats, local Qiven
clones, evaluator rubrics or private producer notes. Do not ask the owner to explain
what the project state should be. If the artifact is insufficient, report failure;
do not repair it from GitHub.

Generic parsing/decoding needed by the declared self-describing artifact format is
allowed. Project-specific decoder/dictionary material is allowed only when it is
contained in or explicitly version-bound by the artifact profile itself.

## Phase A — artifact-only reconstruction

1. Record the artifact format/version, handoff digest, source repository/commit/tree,
   ProjectSnapshot identity, canonical manifest/package digests and recovery status.
2. Verify the artifact's internal integrity to the extent supported by the supplied
   self-describing format. Report any mismatch, unknown or unverifiable element.
3. Use only artifact-contained continuity/source material to reconstruct all ten
   numbered requirements in `collaboration/project-continuity-acceptance.md`:
   what Qiven/qiven-context are; governance/root authority; engineering philosophy;
   active objective/paused domains; latest accepted checkpoint/evidence; unaccepted
   candidate and why; active blockers/obligations; accepted/rejected/superseded/legacy
   cognition; facts requiring later live verification; and the next valid action.
4. Cite artifact-contained source paths and ADR/MEM/OBL IDs for material claims.
5. Separate snapshot/artifact facts from facts that are inherently live and therefore
   cannot yet be verified under Phase-A isolation.
6. Record unsupported claims and abstentions instead of guessing.

## Seal

Return a clearly marked `K4 HANDOFF PHASE A — SEALED` report with PASS/FAIL for
artifact-only reconstruction. Include the exact artifact identities above and a list
of facts deferred to live verification.

Stop after Phase A. Do not perform live GitHub/CI/runtime verification in the same
answer. Phase B is a later turn after this report is preserved.
