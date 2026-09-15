# Retrieval Open-Set v1 — Semantic MiniLM Baseline

## Context

This evidence records the first semantic-only measurement against the frozen `benchmarks/retrieval/open-set-v1.yaml` benchmark. It is an experiment baseline, not acceptance of the semantic retriever as production policy.

The run was owner-reported from the Qiven-v2 validation sequence for `jason-brother/retrieval-reliability-phase1` after the semantic candidate was prepared. The returned excerpt begins at the semantic benchmark step rather than repeating the preceding `git rev-parse HEAD` line, so this file records the candidate association but does not treat the excerpt alone as independent exact-head proof.

## Retrieval candidate

- mode: semantic-only
- model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- FastEmbed requirement: `fastembed==0.8.0`
- semantic top-k: `8`
- model runtime: local ONNX through FastEmbed
- model cache: outside the repository

FastEmbed emitted a runtime warning that this model now uses mean pooling rather than the older CLS behaviour. Qiven does not pin an older FastEmbed merely to suppress that warning. The measured baseline is therefore explicitly the current FastEmbed 0.8.0 mean-pooling behaviour and the warning is part of experiment provenance.

## Owner-reported result

| Case | Outcome | Required recall | Forbidden hit | Extra IDs |
| --- | --- | ---: | --- | ---: |
| windows-interpreter-trust | PASS | 1.00 | none | 6 |
| silent-cli-liveness | PASS | 1.00 | none | 6 |
| exact-head-after-new-commit | PASS | 1.00 | none | 6 |
| gas-native-stack-boundary | MISS | 1.00 | `OBL-20260913T183819Z-9A4F21` | 6 |
| premature-native-physics | PASS | 1.00 | none | 7 |
| vector-canonical-layout | PASS | 1.00 | none | 7 |
| devkit-crash-consistency | PASS | 1.00 | none | 5 |
| retrieval-miss-architecture | MISS | 0.50 | none | 5 |

Aggregate metrics:

- critical_case_recall: `0.667`
- required_id_recall: `0.889`
- forbidden_hits: `1`
- mean_extra_ids: `6.000`
- frozen-threshold result: `FAIL`

The missed required ID was `MEM-20260914T124259Z-5C8E21` in `retrieval-miss-architecture`.

## Interpretation

The semantic channel materially improves selectivity compared with the deterministic baseline: mean extra IDs fell from `19.500` to `6.000` and forbidden hits fell from `3` to `1`. However, required recall fell from `1.000` to `0.889` and one critical memory was lost.

This is evidence for fusion/reranking rather than semantic replacement. The next experiment freezes equal-weight Reciprocal Rank Fusion over the deterministic and semantic ranks with `RRF k=60` and final `top_k=8` before observing hybrid benchmark results.
