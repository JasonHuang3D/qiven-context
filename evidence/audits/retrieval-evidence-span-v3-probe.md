# Retrieval Blind v3 — Passage Evidence Probe

Validated by the project owner on Windows after blind-v3 failure, with the frozen selector candidate remaining `be3f0545ef39f96736442735fae3ab1f4a3a0ff5`.

## Purpose

Measure whether passage-level reranker evidence can distinguish topic relevance from evidence sufficiency without changing the selector.

## Key observations

- `foundation-ownership-must-stay-explicit`: required ADR-0008 had document score `4.0060` and best passage `2.3078`; forbidden ADR-0009 had document score `1.3222` but best passage `-0.6061`.
- `devkit-must-not-overwrite-consumer-edits`: required ADR-0012 had best passage `2.7010`; adjacent ADR-0010 had best passage `-1.3169`.
- `math-must-not-hide-global-epsilon`: ADR-0015 remained strongly separated with best passage `4.7091`.
- `toolchain-name-does-not-imply-every-host-tool`: required memory reached best passage `7.5828`.
- `automated-record-writer-needs-id-issuance`: required obligation reached best passage `4.4697`.
- `old-python-fixture-must-test-version-path`: required obligation reached best passage `2.9421`.

Passage relevance is not a sufficient null gate:

- `foundation-support-is-ci-evidence`: the correct portability/CI memory had document score `2.2071` but its best passage score was `-2.4760`; a passage-threshold-only selector would create a false negative.
- `negative-unknown-gas-cloud-region`: ADR-0020 remained topically close enough to receive document score `0.6619` and best passage score `0.3117` even though the record contains no cloud-region answer.
- Other negative controls had negative best-passage scores, but their separation alone does not establish a universal threshold.

## Interpretation

The probe supports using passage evidence as an additional explanatory signal, especially for separating adjacent records, but falsifies the hypothesis that reranker passage score alone can decide whether canonical cognition actually answers the query.

The next experiment must distinguish **relevance** from **evidence sufficiency / answerability**. Retrieval ranking remains frozen while an independent entailment-style probe measures whether candidate evidence supports the stronger proposition that the evidence is sufficient to answer the question.
