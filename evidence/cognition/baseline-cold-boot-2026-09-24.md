# Measured Manual Cold-Boot Baseline (2026-09-24, CA-0)

Purpose (roadmap CA-0): "measure the actual current cold-boot corpus and
model inputs delivered during ordinary task runs, task-specific additions,
time-to-first-design, and first-pass quality" — the CONTROL-MANUAL arm of
every future Profile C comparison (acceptance protocol §7.1) needs a
recorded, reproducible baseline.

## Accounting rule (sealed for CA-0; Profile C re-pin at trial time)

- Corpus size = `wc -c` over an exact named file list (below). Reproduce
  with the same list at the same revision.
- Token estimate = bytes ÷ 4 (English-prose approximation; stated as an
  estimator, not a tokenizer). Profile C trials MUST use the sealed pinned
  tokenizer of §7.1; this baseline's ÷4 figure is only for corpus-scale
  reasoning and MUST NOT be reused as trial accounting.
- "Delivered input" for future trials = cumulative model input actually
  delivered (boot + reads + tool text), never the size of the corpus on
  disk. Today's harness does not meter delivery; that metering is part of
  the CA-2 qualified ingress (see ingress-feasibility record). This document
  therefore records corpus-scale and process facts now, and the delivery
  metering obligation explicitly.

## Tier 1 — mandatory boot set (BOOTSTRAP.md cold-boot steps, this view)

Measured at qiven-context `90266a2` (+ v23 checkpoint):

| File | Bytes |
|---|---:|
| BOOTSTRAP.md | 6,260 |
| AGENTS.md | 721 |
| MEMORY-CONSTITUTION.md | 5,245 |
| governance/authority.yaml | 974 |
| collaboration/operating-contract.md | 24,846 |
| collaboration/human-handoff-boundary.md | 9,762 |
| collaboration/context-validation.md | 3,363 |
| collaboration/software-engineering-philosophy.md | 8,425 |
| collaboration/context-operating-model.md | 9,523 |
| collaboration/context-handoff-contract.md | 7,840 |
| state/current.md | 10,525 |
| state/active-work.yaml | 3,993 |
| state/repositories.yaml | 1,907 |
| state/roadmap.yaml | 909 |
| views/bindings/extended-cognition-jason.yaml | 4,744 |
| views/workflows/long-running.md | 5,052 |
| memory/index.yaml (title sweep) | 15,191 |
| latest session checkpoint (v22) | 4,009 |
| **Total** | **123,289** (~120 KiB; ≈30.8k tokens at ÷4) |

## Tier 2 — directed TCA-adjacent reading (v22 successor instruction)

| File | Bytes |
|---|---:|
| decisions/ADR-0050.md | 11,530 |
| collaboration/cognitive-governance-program.md | 32,990 |
| collaboration/cognitive-effectiveness-acceptance.md | 38,717 |
| runtime/cognition-landing-manifest.yaml | 3,731 |
| obligations/OBL-20260923T190500Z-D6E7F8.md | 3,788 |
| qiven-runtime task-cognition-activation.md @f0ca5b7 | 40,806 |
| qiven-runtime runtime-mvp-roadmap-amendment.md @f0ca5b7 | 46,121 |
| **Total** | **177,683** (~174 KiB; ≈44.4k tokens at ÷4) |

Combined T1+T2 ≈ 301 KB (≈75k tokens ÷4) BEFORE any task-specific record
retrieval (full memory/ADR/audit bodies), any repository code reading, or
any tool output.

## Corpus counts (same revision)

- memory records: 72 files (66 active titles swept every boot);
- decisions: 45 ADRs (lifecycle-aware retrieval);
- obligations: 5 open;
- collaboration contracts: 26 documents;
- evidence audits: curated, on-demand.

## Time-to-first-design and first-pass quality (process baseline)

No instrumented timer exists in the manual path (a CA-2 metering
obligation). Recorded process facts as the qualitative baseline:

- The v22→v23 successor cold boot (this session) read T1+T2 fully plus
  three repository surveys before the first design-relevant output;
  measured wall-clock is not recorded (honest absence, not a fabricated
  number).
- First-pass quality signal at the owner boundary: the MVP-4 program needed
  THREE real-H1 trials, all failing on mature known hazard classes
  (assumed payload field; borrowed lifetime; untested wire contract) —
  i.e., stored pain did not activate (ADR-0050 Context). H1-attempt counts
  per accepted boundary are the §11 metric; baseline for MVP-4 = 3 failed
  attempts, 0 passes.

## Reproducibility

Re-run `wc -c` over the two named lists at the named revisions
(qiven-context `90266a2`..CA-0-transaction; qiven-runtime `f0ca5b7`). File
identity: qiven-context 90266a2 = origin/main verified 2026-09-23T19:18Z.
