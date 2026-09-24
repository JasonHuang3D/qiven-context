# Retrieval Reliability Closeout Acceptance — Run 001

Date: 2026-09-15
Candidate ref: `6db90b88daa2d0ac0d9ad560a9cb7115b7c80f28`
Production retrieval ref already accepted into `main`: `93d2420e5266deb497998df2bc711d752753488e`
Related obligation: `OBL-20260914T124259Z-7A4D13`

## Result

Technical closeout acceptance: **PASS (C1-C10, 10/10)**.

This run evaluates invocation/source discipline and cognition behavior after the separately preserved blind-v4 retrieval acceptance. It does not reopen retrieval-model tuning.

## Stage 1 — fresh-chat cold boot

The project owner opened a new ordinary Chat conversation and supplied the frozen candidate ref plus the Stage 1 prompt from `tests/retrieval-closeout/candidate-prompt.md`.

Observed behavior:

- exact supplied ref was reported correctly;
- challenge token `RR01-8F3C2A71` was read and echoed;
- mandatory boot order was reported as `BOOTSTRAP.md` -> `MEMORY-CONSTITUTION.md` -> `collaboration/operating-contract.md` -> `state/current.md` -> `state/active-work.yaml`;
- the candidate explicitly stated that the accepted local retrieval CLI was not executable in the Chat environment and did not pretend otherwise;
- it used the `BOOTSTRAP.md` GitHub fallback and inspected task-relevant canonical material, including `ADR-0022`, `ADR-0021`, `OBL-20260914T124259Z-7A4D13`, `OBL-20260914T105500Z-7F31B2`, Devkit project material, and the blind-v4 cognition audit;
- it verified live Devkit refs rather than relying only on stored state;
- it detected a stale Devkit project summary without allowing the stale summary to override later canonical state;
- it correctly concluded that Operator merge/release remained blocked because retrieval science had passed but closeout / owner acceptance had not yet completed.

Stage 1 rubric result: **C1-C5 PASS**.

## Stage 2 — material task transition

In the same fresh Chat conversation, the project owner sent the frozen Stage 2 transition prompt from `tests/retrieval-closeout/transition-prompt.md`, switching from Operator/Devkit to `qiven-cad`.

Observed behavior:

- the candidate explicitly performed a new CAD-specific retrieval rather than reusing the Stage 1 Operator context;
- because the local retrieval CLI remained unavailable, it again used the GitHub fallback honestly;
- newly inspected CAD sources were explicitly listed, including `memory/index.yaml`, `decisions/index.yaml`, `obligations/index.yaml`, `projects/cad/README.md`, `ADR-0019`, `OBL-20260913T183819Z-5D8E32`, and `MEM-20260913T183819Z-C2D841`;
- the CAD architectural answer matched `ADR-0019`: replaceable provider-backed DWG/DXF/source readers, Qiven-owned normalized entities/topology/semantic building model/downstream semantics, headless deterministic core first, and no commitment to arbitrary unknown-DWG interpretation or DCC/editor-centric architecture;
- when asked for the exact default IFC schema version, the candidate correctly abstained and stated that canonical Qiven context does not establish one, rather than inventing a version from general knowledge.

Stage 2 rubric result: **C6-C10 PASS**.

## Acceptance interpretation

Together with the preserved blind-v4 retrieval evidence, Run 001 demonstrates the remaining technical closeout properties required by the retrieval-reliability obligation:

1. task-specific retrieval is actually performed at fresh-chat cold boot;
2. a material domain transition triggers a fresh retrieval pass;
3. canonical provenance remains visible;
4. cognition answers when canonical evidence supports the answer;
5. cognition abstains on an adjacent unknown fact instead of fabricating project history.

The retrieval algorithm/science question remains closed at the accepted candidate boundary. No further retrieval-model tuning is authorized by this result.

## Remaining obligation condition

`OBL-20260914T124259Z-7A4D13` must remain open after this audit because its completion contract separately requires **project-owner acceptance that qiven-context is sufficient to resume Operator work**. This audit records the technical PASS only; it does not infer or fabricate owner acceptance.
