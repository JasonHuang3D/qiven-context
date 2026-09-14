# Retrieval Open-Set v1 — Structural Hybrid PASS

Validated by the project owner on Windows at exact qiven-context branch head `4ba2d2ed89f7b2d5a07a0456687ab4bcd1c617fa`.

## Configuration

- benchmark: `benchmarks/retrieval/open-set-v1.yaml`
- base fusion: equal-weight deterministic + semantic RRF
- semantic model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- FastEmbed: `0.8.0`
- final top-k: `8`
- RRF k: `60`
- graph seed top-k: `4`
- graph depth: `1`
- structural additions: explicit project-scope compatibility plus bidirectional one-hop canonical relation evidence

The FastEmbed runtime emitted its upstream mean-pooling warning for this model. The experiment intentionally measured the pinned current runtime rather than reverting pooling behavior after seeing benchmark results.

## Result

- `critical_case_recall = 1.000`
- `required_id_recall = 1.000`
- `forbidden_hits = 0`
- `mean_extra_ids = 5.250`
- frozen v1 threshold result: **PASS**

## Mechanism observations

- `gas-native-stack-boundary`: the forbidden native-physics obligation `OBL-20260913T183819Z-9A4F21` was removed by project-scope incompatibility (`scope=no`) while `ADR-0020` remained selected.
- `premature-native-physics`: the same obligation remained valid and ranked first when the task itself was in the robotics/native-physics domain.
- `retrieval-miss-architecture`: `MEM-20260914T124259Z-5C8E21` moved from hybrid rank 9 (`D=11`, `S=13`) to structural rank 5 because the relation graph supplied rank 3 evidence from the retrieval-reliability decision neighborhood.
- all eight frozen v1 cases passed with full required recall and zero forbidden hits.

## Interpretation

The v1 result supports the layered retrieval hypothesis: lexical evidence provides broad recall, semantic similarity improves discrimination, project-scope structure suppresses cross-domain false positives, and canonical relation evidence recovers relevant records that neither lexical nor semantic ranking places high enough alone.

This is not final acceptance of the retrieval substrate. The v1 benchmark was visible during development, and its `mean_extra_ids_max = 8` threshold is non-discriminating for a retriever that always returns at most eight IDs. Therefore v1 proves only that the frozen known cases are satisfied by this exact candidate. A held-out v2 benchmark with materially stronger noise constraints must be frozen and run without changing structural retrieval parameters before acceptance can be considered.
