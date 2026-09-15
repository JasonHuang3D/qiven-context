# Retrieval Open-Set v1 — Deterministic Baseline

Date: 2026-09-14
Validated branch: `jason-brother/retrieval-reliability-phase1`
Exact validated head: `79872e04107c49bd82810fd5de49737e3d9c7686`
Benchmark: `benchmarks/retrieval/open-set-v1.yaml`
Mode: deterministic

## Local validation

The project owner reported the full qiven-context regression suite PASS at the exact head above, including the new `retrieval-reliability` suite and the existing repository validator, Context Compiler, context acceptance, cold-boot contract, and Windows Python resolution suites.

## Benchmark result

| Metric | Result | Frozen threshold |
| --- | ---: | ---: |
| Critical-case recall | 0.500 | >= 1.000 |
| Required-ID recall | 1.000 | >= 0.950 |
| Forbidden hits | 3 | <= 0 |
| Mean extra IDs | 19.500 | <= 8.000 |

Threshold result: **FAIL**.

Per-case observations:

- `windows-interpreter-trust`: required recall 1.00, no forbidden hit, 31 extras.
- `silent-cli-liveness`: required recall 1.00, no forbidden hit, 23 extras.
- `exact-head-after-new-commit`: required recall 1.00, no forbidden hit, 15 extras.
- `gas-native-stack-boundary`: required recall 1.00, forbidden `OBL-20260913T183819Z-9A4F21`, 21 extras.
- `premature-native-physics`: required recall 1.00, forbidden `ADR-0020`, 22 extras.
- `vector-canonical-layout`: required recall 1.00, no forbidden hit, 10 extras.
- `devkit-crash-consistency`: required recall 1.00, no forbidden hit, 16 extras.
- `retrieval-miss-architecture`: required recall 1.00, forbidden `ADR-0020`, 18 extras.

## Interpretation

The deterministic retriever demonstrated perfect recall for the required canonical IDs in this frozen benchmark, but poor discrimination. The primary observed failure is not missing relevant cognition; it is over-selection: shared lexical/project terms cause unrelated records and cross-domain negative knowledge to enter the pack. This creates a high-noise context in which relevant evidence can be diluted even though it was technically retrieved.

This evidence therefore justifies evaluating an independent semantic ranking channel and later a hybrid/fusion path against the same frozen benchmark. The benchmark and thresholds must not be changed to accommodate the candidate implementation.
