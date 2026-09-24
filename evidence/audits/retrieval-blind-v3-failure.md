# Retrieval Blind v3 — Failure Evidence

Validated by the project owner on Windows after the cross-encoder/adaptive candidate was frozen at `be3f0545ef39f96736442735fae3ab1f4a3a0ff5`.

## Configuration

- acceptance: `benchmarks/retrieval/blind-v3.yaml`
- semantic model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- rerank model: `BAAI/bge-reranker-base`
- semantic candidate pool top-k: `16`
- graph candidate expansion: one hop from the strongest base anchor only
- maximum selected records: `8`
- record-level rerank logit threshold: `0.0`
- fallback: if no non-explicit candidate reaches threshold, preserve reranker top-1

## Result

- `critical_case_success = 0.500`
- `positive_required_id_recall = 1.000`
- `forbidden_hits = 2`
- `mean_positive_extra_ids = 2.750`
- `negative_abstention_rate = 0.000`
- `mean_positive_selected_ids = 4.000`
- `mean_negative_selected_ids = 1.000`
- acceptance result: **FAIL**

## Positive-case observations

Positive recall remained perfect, so the high-recall candidate stage did not lose required cognition. However, record-level relevance was not selective enough:

- `foundation-ownership-must-stay-explicit`: required `ADR-0008` ranked first with score `4.0060`, but forbidden adjacent boundary decision `ADR-0009` also crossed the global threshold at `1.3222`.
- `devkit-must-not-overwrite-consumer-edits`: required `ADR-0012` ranked first at `3.4705`, but forbidden snapshot/independence decision `ADR-0010` also crossed threshold at `0.8653`.
- several otherwise-correct positive cases selected many extras, including `automated-record-writer-needs-id-issuance` and `old-python-fixture-must-test-version-path`, which each filled all eight available slots.

## Negative-case observations

All four negative controls failed to abstain:

- generic C++ vector-growth question: top false candidate `ADR-0017`, score `-2.3931`;
- generic database-normalization question: top false candidate `ADR-0020`, score `-4.0266`;
- unknown workstation-temperature fact: top false candidate `ADR-0022`, score `-2.4417`;
- unknown gas cloud-region fact: top false candidate `ADR-0020`, score `+0.6619`.

The first three failures are directly caused by the top-1 fail-safe when all scores are negative. The gas cloud-region case proves that deleting the fail-safe or using zero as a universal threshold is still insufficient: a topically related canonical record can receive a positive relevance logit while not containing the requested fact.

## Interpretation

The v3 result falsifies the hypothesis that record-level cross-encoder relevance plus a single global logit threshold is sufficient for reliable context selection and abstention.

The next question is evidence sufficiency, not candidate recall. A record may be topically relevant without containing evidence that answers the task. Before changing the production selector again, measure whether passage-level evidence scoring separates direct support from adjacent topical relevance and unknown-answer cases.

Blind v3 is now development evidence because its results have been observed. It must not serve as final acceptance for any selector subsequently designed from this failure. A later candidate requires a new unseen acceptance set.
