# Genesis Import Audit — Math

## Scope

This slice reconstructs qiven-math's current architecture through Vector Core / Batch 007 and preserves the deferred reasoning required to resume Batch 008 without redesigning the same questions from scratch.

## Sources reviewed

Primary committed evidence:

- `JasonHuang3D/qiven-math@912ae067784fb5cd336925ff6f6d071b85297bff:README.md`
- `JasonHuang3D/qiven-math@912ae067784fb5cd336925ff6f6d071b85297bff:docs/architecture/math.md`
- `JasonHuang3D/qiven-math@912ae067784fb5cd336925ff6f6d071b85297bff:CMakeLists.txt`
- `JasonHuang3D/qiven-math@912ae067784fb5cd336925ff6f6d071b85297bff:include/qiven/math/scalar.hpp`
- `JasonHuang3D/qiven-math@912ae067784fb5cd336925ff6f6d071b85297bff:include/qiven/math/vec3.hpp`
- `JasonHuang3D/qiven-math@912ae067784fb5cd336925ff6f6d071b85297bff:tests/vector_core.cpp`
- commit `912ae067784fb5cd336925ff6f6d071b85297bff` (`merge: add qiven math vector core`).

Retrospective evidence:

- prior-session reconstruction of the qiven-foundation dependency decision;
- prior-session reconstruction of the planned Batch 008 vector-algorithm contract.

Retrospective evidence is explicitly labeled and is not treated as verbatim contemporaneous evidence.

## Promoted canonical records

- `ADR-0013` — keep qiven-math small, deterministic, and external-semantics-free;
- `ADR-0014` — keep canonical vectors compact/scalar-aligned rather than embedding SIMD ABI;
- `ADR-0015` — keep coordinate/tolerance semantics explicit at higher boundaries;
- `ADR-0016` — resolve Foundation as an existing/local source dependency without network CMake fetching;
- `MEM-20260913T182954Z-A6D249` — scalar vocabulary intentionally limited to float/double;
- `MEM-20260913T182954Z-3F8C71` — verified Batch 007 Vector Core surface;
- `OBL-20260913T182954Z-7B4E20` — resume Batch 008 only after qiven-context cold-boot acceptance;
- `OBL-20260913T182954Z-C91A5D` — revisit scalar broadening only on concrete integration demand.

## Rejected options recovered

The reviewed architecture and tests support rejection of these options for the canonical math layer:

- turning qiven-math into a general GLM/Eigen-style library;
- storing world/up-axis/handedness product conventions in canonical math values;
- global epsilon or approximate `operator==`;
- `alignas(16)` / hidden fourth lane / platform SIMD representation for canonical `Vec3f`;
- speculative generic scalar customization before a real units/numeric consumer exists;
- configure-time network FetchContent or equivalent hidden dependency acquisition for Foundation in the current phase.

These rejections are represented inside the corresponding ADRs rather than duplicated as separate memory records where the ADR preserves sufficient rationale.

## Reasoning residue recovered

Batch 008 candidate reasoning preserved without pretending it is already implemented:

- dot, Vec3 cross, length-squared, robust length, normalization, checked normalization, distance, and explicit-tolerance near comparison;
- preferred normalization by max-component scaling to reduce avoidable overflow/underflow;
- checked normalization should fail for zero/non-finite input and preserve output on failure;
- initial near comparison candidate is componentwise absolute tolerance, not global epsilon or implicit relative tolerance;
- pure operations may stay constexpr, while sqrt-dependent operations need not be forced into C++20 constexpr;
- fast-math is not part of the intended contract.

The exact API names and edge semantics must be re-confirmed when the Batch 008 obligation triggers.

## Non-promoted candidates

- Future matrix, quaternion, rigid-transform, and affine-transform types named in README/architecture remain planned vocabulary, not current implementation facts.
- Matrix storage order remains intentionally unspecified even though mathematical matrix conventions are documented.
- No geometry, units, CAD, physics, or rendering semantics were promoted into qiven-math because the architecture explicitly keeps them outside this layer.

## Gaps

The complete original discussion that chose every Batch 008 detail is not available here as a verbatim artifact. The current architecture and Vector Core are strongly Git-verifiable; Batch 008 algorithm details are therefore preserved as deferred candidate contract rather than upgraded to implemented facts or accepted API without re-confirmation.
