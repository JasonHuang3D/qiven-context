# Retrieval Cross-Encoder Candidate — v1/v2 Development Pass

Validated by the project owner on Windows at exact qiven-context branch head `be3f0545ef39f96736442735fae3ab1f4a3a0ff5`.

## Frozen candidate

- first-stage deterministic channel: current Context Compiler direct matches
- first-stage semantic channel: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- semantic candidate pool top-k: `16`
- project-scope compatibility: hard filter with explicit-ID override
- relation graph: one hop from the strongest compatible base anchor; candidate-generation evidence only
- reranker: `BAAI/bge-reranker-base`
- final maximum selected IDs: `8`
- relevance logit threshold: `0.0`
- explicit include IDs: hard inclusion
- fallback: if no non-explicit candidate reaches the threshold, preserve reranker top-1

The semantic runtime emitted the existing FastEmbed warning that the MiniLM model uses mean pooling rather than its historical CLS behavior. The measured candidate intentionally uses the current pinned runtime behavior.

## held-out-v2 development result

- `critical_case_recall = 1.000`
- `required_id_recall = 1.000`
- `forbidden_hits = 0`
- `mean_extra_ids = 0.417`
- `mean_selected_ids = 1.833`
- `mean_candidate_ids = 27.250`
- threshold result: **PASS**

The previous v2 failures were corrected without changing the frozen v2 benchmark. Notably:

- `ADR-0010` became rerank rank 1 for the generated-repository independence question while the workspace obligation scored slightly below zero and was rejected;
- the Windows Python lesson scored strongly negative for the Windows permission-diagnosis question while the permission lesson ranked first;
- `ADR-0006` ranked first for the local validation-profile question while merge authorization scored strongly negative.

## open-set-v1 regression result

- `critical_case_recall = 1.000`
- `required_id_recall = 1.000`
- `forbidden_hits = 0`
- `mean_extra_ids = 0.125`
- `mean_selected_ids = 1.625`
- `mean_candidate_ids = 22.750`
- threshold result: **PASS**

## Remaining acceptance gap

The development pass does **not** establish abstention reliability. In `silent-cli-liveness`, the required record ranked first but had reranker logit `-2.3421`; it was retained only by the top-1 fallback that applies when every candidate is below the `0.0` threshold.

Therefore v1/v2 success does not prove that Qiven can distinguish:

- a task with one weak-but-real relevant historical record; from
- a task for which no canonical cognition should be injected at all.

A new blind acceptance contract must contain true negative/no-answer cases and measure abstention explicitly before this retrieval substrate can be accepted. The v1 and v2 benchmarks are now development/regression evidence, not final acceptance sets.
