# Math

Genesis historical import status: **SLICE COMPLETE** for the current pre-Batch-008 architecture and preserved deferred reasoning.

## Current verified state

Pinned live main during Genesis:

`912ae067784fb5cd336925ff6f6d071b85297bff` — `merge: add qiven math vector core`

Implemented public vocabulary at this pin:

- `floating_scalar` for exactly unqualified `float` and `double`;
- `Vec2<T>`, `Vec3<T>`, `Vec4<T>` plus `f32`/`f64` aliases;
- aggregate, standard-layout, trivially-copyable compact representation;
- exact component equality;
- indexed component access with assertion preconditions;
- same-scalar vector arithmetic and scalar multiply/divide;
- C++20 header-only/interface-library consumption of qiven-foundation.

## Durable architecture

- qiven-math is a small deterministic external-semantics-free spatial algebra vocabulary, not a general GLM/Eigen replacement.
- geometry, CAD, units, dynamic/decomposition-heavy linalg, physics, robotics policy, and rendering conventions stay outside this layer.
- canonical vectors are dense scalar-aligned values and do not encode SIMD ABI or hidden lanes.
- coordinate conversions belong at domain/import/export/scene boundaries.
- exact `operator==` stays exact; approximate comparison requires explicit tolerance and no global epsilon.
- initial scalar policy is intentionally `float`/`double` only.
- qiven-foundation is resolved from an existing/local source tree rather than configure-time network acquisition.

## Deferred cognition

Math Batch 008 is intentionally paused until qiven-context cold-boot acceptance. Its preserved candidate contract includes dot/cross, length/length-squared, robust normalization, checked `try_normalize`, distance, and explicit-tolerance near comparison. The exact API/edge-case contract must be re-confirmed when the obligation triggers.

The scalar vocabulary should only broaden when a concrete units or numeric-integration consumer demonstrates the need.

## Evidence

See `evidence/audits/genesis-math-slice.md` and ADR-0013 through ADR-0016.
