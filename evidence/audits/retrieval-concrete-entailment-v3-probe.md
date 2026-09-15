# Retrieval Blind v3 — Concrete Entailment Development Probe

Validated by the project owner on Windows against commit `6d52bed784ef46fd2550575714128594af7b9693`. The full repository suite passed with zero failures before the probes ran. The selector remained frozen at `be3f0545ef39f96736442735fae3ab1f4a3a0ff5`; blind-v3 is already observed development evidence and this probe is not acceptance evidence.

## Purpose

Test one narrower hypothesis after generic answerability NLI failed: instead of asking a meta-question such as whether evidence is sufficient, score whether candidate evidence entails a concrete proposed answer.

## Generic answerability result

The generic sufficient-vs-insufficient NLI formulation remains falsified as a universal null gate. Required positive margins ranged down to `0.0193`, while negative controls reached `0.0708`; forbidden `ADR-0009` reached `0.0857`, slightly above required `ADR-0008` at `0.0852`. No single scalar threshold can preserve required positives while rejecting unknown-answer negatives and adjacent forbidden records.

## Concrete-entailment observations

Required positive-record best entailment scores:

- Foundation ownership/failure rule: `ADR-0008 = 0.6332`; forbidden `ADR-0009 = 0.0780`.
- Devkit consumer-edit conflict rule: `ADR-0012 = 0.1678`; forbidden `ADR-0010 = 0.0633`.
- Math tolerance/coordinate rule: required `ADR-0015 = 0.0724`; forbidden adjacent `ADR-0014 = 0.1230`.
- Recurring ambiguity codification: required memory `0.1287`; forbidden memory `0.1012`.
- Foundation CI support evidence: required memory `0.2049`.
- Toolchain ownership boundary: required memory `0.2451`.
- Automated record ID issuance: required obligation `0.0666`; unrelated memory `0.0300`.
- Old-Python fixture validation gap: required obligation `0.1730`; unrelated memory `0.0887`.

Negative-control maximum entailment values among watched candidates:

- generic C++ vector-growth false claim: `0.0857`;
- generic database-normalization false claim: `0.0876`;
- unknown workstation-temperature false claim: `0.0605`;
- unknown gas cloud-region false claim: `0.0599`.

A threshold above the strongest negative (`0.0876`) would still reject two required positives (`ADR-0015 = 0.0724` and the ID-issuance obligation `0.0666`). More importantly, the math case directly reverses the desired adjacent-record ordering: forbidden `ADR-0014` scores `0.1230`, above required `ADR-0015` at `0.0724`.

## Interpretation

Concrete proposition verification is materially more discriminative than the generic meta-answerability hypothesis in several cases, especially unknown-answer negatives, but it is still not a universal scalar null gate when implemented as maximum entailment over individual evidence chunks.

The failure shape suggests two distinct remaining problems rather than another relevance-threshold problem:

1. composite candidate answers can require support from multiple evidence spans, while a single-chunk maximum under-scores a correct conjunction;
2. an adjacent topical record can weakly entail part of a composite claim and outrank the record that supplies the full answer.

If NLI work continues, the next narrow hypothesis should be **atomic claim decomposition plus evidence-bundle coverage**, not further tuning of one entailment threshold. The proposer/verifier architecture remains plausible, but neither generic sufficiency NLI nor single-chunk concrete entailment is accepted as the answerability gate.
