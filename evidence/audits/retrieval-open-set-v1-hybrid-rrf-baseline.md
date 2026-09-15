# Retrieval Open-Set v1 — Hybrid RRF Baseline

Validated by the project owner on Windows at exact qiven-context branch head `8b1db233c1d584b7328daf2f861de2ed7231c960`.

## Configuration

- benchmark: `benchmarks/retrieval/open-set-v1.yaml`
- mode: equal-weight Reciprocal Rank Fusion
- deterministic channel: current Context Compiler ordering
- semantic channel: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- FastEmbed: `0.8.0`
- semantic top-k: `8`
- RRF k: `60`
- hybrid final top-k: `8`

The FastEmbed runtime emitted its upstream warning that this model now uses mean pooling instead of the historical CLS behavior. The experiment intentionally measured the current pinned runtime rather than reverting pooling behavior to improve benchmark results.

## Result

- `critical_case_recall = 0.667`
- `required_id_recall = 0.889`
- `forbidden_hits = 1`
- `mean_extra_ids = 5.625`
- frozen threshold result: **FAIL**

## Case observations

- `windows-interpreter-trust`: PASS; required Python-environment memory hybrid rank 2 (`D=3`, `S=1`).
- `silent-cli-liveness`: PASS; required liveness memory hybrid rank 5 (`D=7`, `S=4`).
- `exact-head-after-new-commit`: PASS; ADR-0021 hybrid rank 1 (`D=1`, `S=1`).
- `gas-native-stack-boundary`: MISS because forbidden native-physics obligation was selected at hybrid rank 5 (`D=8`, `S=6`) while ADR-0020 remained rank 1.
- `premature-native-physics`: PASS; required physics obligation hybrid rank 1 (`D=1`, `S=1`).
- `vector-canonical-layout`: PASS; ADR-0014 hybrid rank 1 (`D=1`, `S=1`).
- `devkit-crash-consistency`: PASS; required crash-consistency memory hybrid rank 3 (`D=6`, `S=1`).
- `retrieval-miss-architecture`: MISS because `MEM-20260914T124259Z-5C8E21` landed just outside the final set at hybrid rank 9 (`D=11`, `S=13`), while ADR-0022 ranked 1.

## Interpretation

Equal-weight lexical/semantic fusion reduces noise slightly compared with semantic-only retrieval but does not recover the missing retrieval-reliability lesson and does not reject the cross-project native-physics distractor. The failure modes point to structural evidence not represented in either ranker: project-scope compatibility and explicit canonical relations.

This evidence freezes the RRF baseline before adding a structural retrieval channel. It must not be rewritten to reflect later structural or reranker results.
