# Retrieval Blind v4 — Candidate Boundary and Cognition Acceptance

Validated on JasonPC by the project owner after candidate/reasoning separation was frozen at `affc09e2afb1a44d23ee3b9ff61e63a04edde1a4`. The blind-v4 benchmark and evaluator were committed afterward at `6881adf57ce680adcfd9ec86508f6b2977bb8d30`, before the frozen candidate was run against the cases.

## Automated retrieval result

The owner reported the JasonPC run as passing with:

- `positive_required_id_recall = 1.000`
- `positive_top1_required_rate = 1.000`
- `forbidden_top1_hits = 0`
- `mean_candidate_count = 3.000`
- automated retrieval acceptance: `PASS`

All eight positive cases placed the required canonical record at rank 1.

## Manual cognition result

Cognition was reviewed separately from retrieval. The review used the returned top-3 canonical candidate contents as evidence and applied the frozen rule: candidate presence is not proof; answer only when the evidence directly supports the requested Qiven fact or policy, otherwise abstain.

Positive cases — all answered from direct canonical support:

1. `worker-authority-is-not-release-authority` — `ADR-0004`
2. `focused-validation-needs-explicit-cto-scope` — `ADR-0006`
3. `passing-handoff-still-needs-remote-review` — `MEM-20260913T162546Z-E73124`
4. `devkit-conflict-atomic-is-not-crash-atomic` — `MEM-20260913T182338Z-D5E8A2`
5. `math-scalars-stay-float-double-until-demand` — `MEM-20260913T182954Z-A6D249`
6. `cad-is-building-semantic-not-arbitrary-dwg` — `ADR-0019`
7. `exact-validated-head-allows-jason-brother-merge` — `ADR-0021`
8. `task-switch-path-identity-needs-real-path` — `MEM-20260913T182338Z-92AD37`

Negative cases — all abstained because the returned candidates did not directly establish the requested answer:

1. `negative-generic-rust-borrow-checker` — candidates discuss Qiven architecture/ownership, not Rust ownership/borrowing language semantics.
2. `negative-generic-quaternion-slerp` — candidates discuss Qiven shared-core/math scope and dependency resolution, not quaternion SLERP mathematics.
3. `negative-unknown-cad-ifc-version` — CAD architecture establishes a provider-backed building-semantic pipeline and possible downstream targets, but no exact default IFC schema version.
4. `negative-unknown-foundation-allocation-cap` — Foundation records establish explicit size/alignment/allocation semantics and the Phase-I API surface, but no numeric maximum allocation size in bytes.

Manual cognition acceptance: `PASS` (`12/12` expected answer/abstain decisions).

## Conclusion

Blind-v4 supports the responsibility boundary introduced after blind-v3:

- retrieval is responsible for producing a small, provenance-preserving candidate evidence bundle with strong recall and ordering;
- retrieval score or candidate presence is not canonical truth and does not establish answerability;
- cognition is responsible for reading the returned canonical evidence and deciding whether it directly supports an answer;
- absence of direct support must produce abstention rather than project-history fabrication.

The generic multilingual NLI verifier experiments remain falsified and are not part of the accepted answerability path. No additional local NLI gate is justified by blind-v4.

This audit closes the retrieval-science question for the current candidate boundary. Any remaining work under the retrieval-reliability obligation should be integration/operational acceptance work, not further model or threshold experimentation.
