# Retrieval Blind v3 — Atomic Evidence-Bundle Entailment Probe

Validated by the project owner on Windows after the concrete-entailment probe. The frozen selector candidate remained `be3f0545ef39f96736442735fae3ab1f4a3a0ff5`. Blind-v3 is already observed development evidence; this probe is diagnostic and is not acceptance evidence.

## Purpose

Test whether decomposing composite candidate answers into atomic claims and allowing each atom to draw support from a small top-3 retrieved evidence bundle resolves the failure of single-chunk concrete entailment.

## Result

Positive coverage floors:

- Foundation ownership/failure: `0.2475`
- Devkit consumer-edit conflict: `0.1241`
- Math exact equality / coordinate convention: `0.1775`
- Recurring ambiguity codification: `0.1769`
- Foundation support requires CI evidence: `0.1568`
- Toolchain ownership boundary: `0.1056`
- Automated record ID issuance: `0.1409`
- Old-Python fixture validation gap: `0.1318`

Negative coverage floors:

- generic C++ vector-growth claim: `0.0893`
- generic database-normalization claim: `0.0725`
- unknown workstation-temperature claim: `0.1116`
- unknown gas cloud-region claim: `0.0859`

The minimum positive floor is `0.1056`; the maximum negative floor is `0.1116`. Therefore there is still no scalar entailment threshold that preserves all observed positives while rejecting all observed negatives.

## What improved

Atomic decomposition materially repaired the composite-answer failure shape seen in the prior probe:

- The Math case now correctly finds both atoms in `ADR-0015`, with support `0.2548` for exact equality and `0.1775` for no baked-in handedness/up-axis.
- The Foundation ownership/failure case separates strongly, with floor `0.2475`.
- The ID-issuance and old-Python validation-gap cases both recover the correct obligation as support for each atom.

This supports the proposer/verifier direction: answer decomposition plus bundle-level coverage is substantially more faithful than asking one composite proposition against one chunk.

## Remaining failure shape

The remaining overlap is not a retrieval-recall or composite-answer problem. It is NLI calibration / class semantics:

- the false workstation-temperature claim receives entailment `0.1116` from `ADR-0022`, even though the evidence is unrelated and should semantically be **neutral**, not entailed;
- the weakest true positive, the toolchain manifest-ownership atom, receives only `0.1056` despite a directly relevant source.

Using raw entailment probability as a globally comparable scalar is therefore falsified even after atomic decomposition.

## Next narrow hypothesis

Do not tune another probability threshold on observed blind-v3. Instead test the model according to its native three-way NLI semantics: for each atomic claim/evidence pair, compare **entailment vs neutral vs contradiction** and treat support as a class decision (`entailment` must win), then measure whether every atom in a candidate answer obtains at least one entailment-class supporting span in the evidence bundle.

If three-way class semantics still cannot separate these observed positives and negatives, stop extending this NLI model path rather than stacking more heuristics.
