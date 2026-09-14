# Math

Genesis historical import status: **SLICE COMPLETE**. Math Batch 008 vector algorithms are also complete and merged.

## Current verified state

Current verified main:

`95c29339dd891843870d2b8e4962c86494dfd505` — `merge: complete Math Batch 008 vector algorithms`

Implemented public vocabulary at this pin:

- `floating_scalar` for exactly unqualified `float` and `double`;
- `Vec2<T>`, `Vec3<T>`, `Vec4<T>` plus `f32`/`f64` aliases;
- aggregate, standard-layout, trivially-copyable compact representation;
- exact component equality;
- indexed component access with assertion preconditions;
- same-scalar vector arithmetic and scalar multiply/divide;
- `dot` for Vec2/Vec3/Vec4 and right-hand-rule `cross` for Vec3;
- `length_squared`, robust max-component-scaled `length`, `normalize`, checked `try_normalize`, `distance`, and explicit-tolerance componentwise `is_near`;
- C++20 header-only/interface-library consumption of qiven-foundation;
- Devkit managed template state advanced to `0.1.2`.

The exact candidate `740daca418fce5981f4f40079c2322f2912545e6` passed local Windows Debug/Release build and test validation, formatting/diff checks, and clean-tree validation before no-ff merge. GitHub Actions run `34826905065` then passed the full manually selected cross-platform plan on the merged main: Windows MSVC Debug/Release, Linux GCC Debug/Release, Linux Clang Debug/Release, macOS AppleClang x64/arm64 Debug/Release, sanitizer/contracts coverage, and final CI Gate.

## Durable architecture

- qiven-math is a small deterministic external-semantics-free spatial algebra vocabulary, not a general GLM/Eigen replacement.
- geometry, CAD, units, dynamic/decomposition-heavy linalg, physics, robotics policy, and rendering conventions stay outside this layer.
- canonical vectors are dense scalar-aligned values and do not encode SIMD ABI or hidden lanes.
- coordinate conversions belong at domain/import/export/scene boundaries.
- exact `operator==` stays exact; approximate comparison requires explicit tolerance and no global epsilon.
- initial scalar policy is intentionally `float`/`double` only.
- qiven-foundation is resolved from an existing/local source tree rather than configure-time network acquisition.
- robust normalization uses max-component scaling; checked normalization rejects zero and non-finite input without mutating the output on failure.
- `length_squared` remains direct algebra and can overflow/underflow; robust behavior belongs to `length`/normalization rather than silently changing the algebraic primitive.

## Deferred cognition

The scalar vocabulary should only broaden when a concrete units or numeric-integration consumer demonstrates the need.

The Math CI workflow currently checks out an older Foundation commit even though current Foundation main has advanced. Batch 008 is still valid: the Math candidate was locally validated against current Foundation and the intervening Foundation work did not alter its public source API, while the exact merged Math tree passed the full cross-platform CI plan. The stale CI dependency pin is nevertheless a follow-up because future integration evidence should use the intended current/pinned Foundation baseline.

## Evidence

See `evidence/audits/genesis-math-slice.md`, ADR-0013 through ADR-0016, `OBL-20260913T182954Z-7B4E20`, and GitHub Actions run `34826905065`.
