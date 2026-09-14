# Devkit

Genesis historical import status: **SLICE COMPLETE** for current architecture, repository lifecycle, major brownfield lessons, and known deferred residue.

## Current state

- Verified main pin: `022aaac1e169d556015b52c32af255031a6de332` (`merge: reconcile Foundation managed drift in Devkit 0.1.2`).
- Devkit covers greenfield generation, safe managed-file synchronization, and brownfield adoption.
- Current merged C++ library template version: `0.1.2`.
- Managed snapshot: 16 shared paths.
- Bootstrap-only repository-owned paths: `.gitignore`, `README.md`, `CMakeLists.txt`, `.github/workflows/ci.yml`.
- The accepted 0.1.2 merge tree is exactly the locally validated candidate tree from `125632e8ebb66aa0f9c3302a1fc93d63356d8004`.
- qiven-foundation is now formally adopted into this managed lifecycle; accepted Foundation main is `6c09151e1a52830c66e6c7a97b5b68740154f475`.

## Architectural model

- `qiven-toolchain-win` owns pinned executable tools.
- `qiven-devkit` owns repository templates, engineering conventions, and explicit new/adopt/sync lifecycle tooling.
- Runtime repositories own their APIs, implementation, tests, domain architecture, bootstrap-only files, and intentional local divergence.
- A future `qiven-workspace` may own ecosystem composition; Devkit does not currently fill that role.
- Generated/adopted repositories remain independently usable and do not require a live Devkit checkout during normal development.

## Lifecycle safety

- New repositories are materialized snapshots.
- Adoption requires a clean Git root with HEAD and no existing `.qiven` ownership state.
- Adoption classifies managed paths as `EXACT`, `MISSING`, or `CONFLICT`; conflicts abort before normal mutation.
- Sync uses schema-2 generated state with managed-path SHA-256 hashes and preflights the union of old/new managed paths.
- Bootstrap-only files are outside synchronization ownership.
- The MISSING-path adoption fixture performs an immediate post-adoption sync and verifies all sixteen managed files plus `.qiven/repo.json` and `.qiven/generated-state.cmake` remain hash-stable. `OBL-20260913T182338Z-8A21D6` is complete.

## Foundation drift archaeology

The original Foundation-shaped adoption regression was recovered from qiven-devkit commit `118de43fc74c5bfd101e41008d5aa8fbe0f37345`. It records the exact historical 3/13 partition rather than merely the aggregate counts.

Historical exact paths:

- `.editorconfig`
- `.gitattributes`
- `tools/delete-all-branches-but-main.cmd`

Historical conflict paths:

- `.clang-format`
- `CMakePresets.json`
- `AGENTS.md`
- `docs/engineering/README.md`
- `docs/engineering/implementation-standard.md`
- `docs/engineering/testing-standard.md`
- `docs/engineering/worker-protocol.md`
- `docs/engineering/feature-spec.md`
- `tools/resolve-toolchain.cmd`
- `tools/format.cmd`
- `tools/format-check.cmd`
- `tools/gen-vs2022-x64.cmd`
- `tools/apply-jason-brother.cmd`

The pre-reconciliation live Foundation versus Devkit 0.1.1 reconstruction independently reproduced the same 3 exact / 13 conflict partition. See `evidence/audits/foundation-managed-drift-reconstruction.md` for semantic dispositions and provenance.

## Reconciliation and adoption outcome

Devkit 0.1.2 generalized the shared engineering protocol that was previously richer in Foundation while keeping repository-specific architecture repository-owned. It also hardened generated Windows CMD control flow, added a regression detector for unsafe ungrouped conditional chaining, introduced the dedicated MISSING-adoption sync no-op regression, and standardized human-facing test-runner output expectations.

Foundation then converged the thirteen former conflicts against this accepted surface. A real adoption check reached `16 EXACT / 0 MISSING / 0 CONFLICT`; formal adoption created only `.qiven/repo.json` and `.qiven/generated-state.cmake`; immediate sync left both ownership-state files byte-identical. Foundation main `6c09151e1a52830c66e6c7a97b5b68740154f475` is therefore formally Devkit-managed.

## Lessons and accepted limitations

- Filesystem-root identity must use physical canonicalization where equivalence matters; lexical absolute paths were insufficient across Windows/macOS aliasing.
- Conflict preflight is intentionally all-conflicts-first, but adoption/sync are not crash-consistent filesystem transactions after mutation begins.
- Devkit managed templates must not automatically override semantically divergent brownfield files; semantic disposition precedes ownership.
- Evidence absent from canonical context may still be recoverable from authoritative Git history. Do not fabricate missing detail, but distinguish `not imported` from `not recoverable`.
- Large textual deletion during managed-file convergence is not itself proof of semantic loss: shared protocol may be deduplicated into stronger generic managed contracts while repository-specific rules remain in repository-owned architecture. Exact semantic review is still required before adoption.
- Human-facing lifecycle commands are engineering interfaces. Adoption `check/apply` output should eventually receive the same deliberate layout/status discipline as the test runner (`OBL-20260914T081146Z-6D2F31`).

## Active residue

- Improve human-facing adoption-plan/result layout when that CLI presentation is next touched (`OBL-20260914T081146Z-6D2F31`).
- Revisit crash-consistent update mechanics if the managed surface or failure cost grows materially (`OBL-20260913T182338Z-B37E54`).

See `evidence/audits/genesis-devkit-slice.md`, `evidence/audits/foundation-managed-drift-reconstruction.md`, and `evidence/audits/foundation-devkit-adoption.md`.
