# Retrieval Blind v3 — Native NLI-Class Probe Failure

Validated by the project owner on Windows against `jason-brother/retrieval-reliability@1533f638e3d75f110719d52cde6fe2bc2233c220`. The frozen selector candidate remained `be3f0545ef39f96736442735fae3ab1f4a3a0ff5`. Blind-v3 is already observed development evidence; this probe is diagnostic and is not acceptance evidence.

## Purpose

Give the current multilingual NLI verifier one final test using its native three-way semantics rather than another scalar threshold. For each atomic claim/evidence pair the ONNX model exposes `entailment`, `neutral`, and `contradiction`; an atom counts as supported only when at least one span in the top-3 evidence bundle has `entailment` as the winning class.

The predeclared stop condition was: if native class semantics still cannot preserve the known positive cases while abstaining on the negatives, stop extending this NLI-model path rather than adding more thresholds or heuristics.

## Result

All four negative controls correctly abstained because their best spans were classified as neutral:

- generic C++ vector-growth: neutral wins (`E=0.1098`, `N=0.8244`, `C=0.0658` on the stronger atom);
- generic database-normalization: neutral wins (`E=0.0725`, `N=0.8686`, `C=0.0589`);
- unknown workstation temperature: neutral wins (`E=0.1093`, `N=0.8060`, `C=0.0848`);
- unknown industrial-gas cloud region: neutral wins (`E=0.0859`, `N=0.8404`, `C=0.0737`).

However, all eight positive cases also produced an overall `ABSTAIN` because at least one required atom was classified as neutral. Representative failures include:

- Foundation explicit ownership/provenance atom: neutral wins (`E=0.2475`, `N=0.7001`, `C=0.0524`), although the ordinary-allocation-failure atom is correctly entailment (`E=0.5183`, `N=0.4674`, `C=0.0143`);
- Devkit consumer-edit protection atoms: both neutral;
- qiven-math exact-equality and no-baked-coordinate-convention atoms: both neutral despite the correct `ADR-0015` evidence;
- toolchain ownership-boundary atoms: both neutral despite the correct memory being the top retrieved record;
- old-Python validation-gap atoms: both neutral despite the correct open obligation being the top retrieved record.

Thus native three-way classification has excellent abstention on these observed negatives but unacceptable positive recall. The model behaves conservatively toward paraphrased normative/project statements and cannot serve as the Qiven answerability verifier.

## Stop decision

The predeclared falsification condition fired. Stop the `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli` answerability path here.

Do **not** continue with:

- another scalar threshold;
- different hand-written sufficient/insufficient hypotheses;
- more atomic-claim wording tweaks;
- class-margin heuristics;
- additional rules layered on this same NLI output.

The useful result is architectural: candidate retrieval and answerability reasoning are different responsibilities. Blind-v3 shows that the reranked retrieval path already places the required record first in every observed positive case, while the unresolved problem is whether a retrieved candidate actually answers the task. That should be tested at the cognition/reasoning boundary rather than by forcing a generic NLI classifier to replace the reasoning model.

## Reproducibility note

The FastEmbed warning about `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` using mean pooling does not represent a new dependency-version drift inside this probe: the frozen blind-v3 candidate itself pins `fastembed==0.8.0`. Preserve the warning as operational evidence, but do not treat it as a reason to invalidate this probe unless a future reconstruction demonstrates that the same pinned runtime resolves different model metadata/artifacts.
