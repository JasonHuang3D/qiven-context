# Retrieval Held-Out v2 — Structural Hybrid Failure

Validated by the project owner on Windows at exact qiven-context branch head `02d28b71a751fe755dc8193d8c13600e6adc32da`.

## Configuration

- benchmark: `benchmarks/retrieval/held-out-v2.yaml`
- structural algorithm frozen at `4ba2d2ed89f7b2d5a07a0456687ab4bcd1c617fa`
- final fixed top-k: `8`
- lexical/semantic RRF k: `60`
- relation graph seed top-k: `4`
- relation graph depth: `1`
- semantic model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- FastEmbed: `0.8.0`

No retrieval implementation changed between the frozen structural algorithm and this held-out run; only v1 evidence and the v2 benchmark were added.

## Result

- `critical_case_recall = 0.700`
- `required_id_recall = 0.846`
- `forbidden_hits = 3`
- `mean_extra_ids = 6.583`
- threshold result: **FAIL**

## Important failures

- `generated-repo-must-not-call-devkit`: required `ADR-0010` was base-hybrid rank 1 (`D=2`, `S=3`) but relation boosting pushed it to structural rank 10, outside fixed top-8.
- `windows-write-failure-is-layered`: required permissions memory remained selected, but the unrelated Python-interpreter memory was also selected and relation-boosted to structural rank 2.
- `workspace-must-be-earned`: required workspace obligation passed, but forbidden `ADR-0010` was graph-promoted to structural rank 4.
- `focused-validation-cannot-be-inferred`: required `ADR-0006` was base-hybrid rank 1 (`D=1`, `S=1`) but structural rank 9; forbidden merge-authorization `ADR-0021` was graph-promoted to rank 3.

## Interpretation

Two independent limitations were exposed.

First, fixed top-8 selection is over-inclusive. Most otherwise-correct cases emitted six or seven unapproved extras, so the retriever still lacks an evidence-driven stopping rule.

Second, treating the relation graph as an equal-weight rank channel is unsafe. Generic `related` edges encode useful context but do not mean that the neighbor answers the current question. Relation evidence can therefore amplify tangential records and even displace a record that lexical and semantic retrieval both ranked first.

The next experiment must not merely retune graph weight or top-k. The v2 benchmark is now development evidence because its failures have informed the next design. Final acceptance requires a new unseen benchmark after the next retrieval architecture is frozen.