# K4 handoff semantic-drift review — 2026-09-18

## Baseline reviewed

The project owner stopped mutation and requested a read-only review of the K4
candidate that existed before the review. The semantic baseline was commit
`232e26cf04182ed6627d8e400ff161231b220e85`. A later failure-clean CLI commit
`194fcfdcabc9b5661131e827298f12f02fd747ed` was treated separately while reviewing
the acceptance semantics.

## Findings

1. The existing Project Continuity contract originated as a remote GitHub cold-boot
   test. It did not define producer/artifact/consumer isolation.
2. K4 combined canonical export/restore with that pre-existing fresh-session test but
   did not add a normative handoff boundary.
3. The K4 candidate prompt let the fresh consumer fetch the remote candidate and run
   export/restore itself. This could mask an incomplete export by allowing project
   cognition to be reread from the original repository.
4. ADR-0032's agent-runtime Python validation exception was broad enough to be
   misread as removing JasonPC from K4. The exception correctly removes duplicate
   portable validation, but K4 may still require JasonPC as an independent artifact
   producer under the test topology.
5. `session-ci-handoff-contract.md` uses handoff for session progress/checkpoint
   continuity; it is not a canonical export handoff contract.
6. The archive package itself is self-contained for canonical objects/evidence and
   preserves exact source commit/tree provenance, but the reference fresh-process
   fixture still uses project runtime code. It proves package+runtime recovery, not
   artifact-only LLM continuity.
7. No later planned ContextKernel batch existed to supply the missing causal handoff
   proof. Therefore K4 itself must be corrected before acceptance.

## Disposition

ADR-0034 and `collaboration/context-handoff-contract.md` establish explicit continuity
profiles and make Canonical Artifact Handoff the K4 acceptance profile. Existing
remote-cold-boot evidence remains valid only for the remote continuity property it
actually tested.

K5 is introduced as the next optimization boundary: lossless semantic transport
compression measured in effective LLM input tokens, with deterministic machine
round-trip and paired fresh-LLM equivalence gates.

This audit is a semantic correction record, not a K4 PASS. K4 remains unaccepted
until its runtime/handoff artifact, JasonPC producer execution, isolated consumer
trial and final exact-head validation pass.
