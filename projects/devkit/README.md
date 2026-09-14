# Devkit

Genesis historical import status: **SLICE COMPLETE** for current architecture, repository lifecycle, major brownfield lessons, and known deferred residue.

## Current state

- Verified main pin: `022aaac1e169d556015b52c32af255031a6de332` (`merge: reconcile Foundation managed drift in Devkit 0.1.2`).
- Devkit covers greenfield generation, safe managed-file synchronization, and brownfield adoption.
- Current merged C++ library template version: `0.1.2`.
- Managed snapshot: 16 shared paths.
- Bootstrap-only repository-owned paths: `.gitignore`, `README.md`, `CMakeLists.txt`, `.github/workflows/ci.yml`.
- The accepted 0.1.2 merge tree is exactly the locally validated candidate tree from `125632e8ebb66aa0f9c3302a1fc93d63356d8004`.

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
- The MISSING-path adoption fixture now performs an immediate post-adoption sync and verifies all sixteen managed files plus `.qiven/repo.json` and `.qiven/generated-state.cmake` remain byte-for-byte hash-stable. `OBL-20260913T182338Z-8A21D6` is complete.

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

## Reconciliation outcome

Devkit 0.1.2 generalizes the shared engineering protocol that was previously richer in Foundation, while repository-specific architecture remains repository-owned. It also hardens generated Windows CMD control flow, adds a regression detector for unsafe ungrouped conditional chaining, introduces the dedicated MISSING-adoption sync no-op regression, and standardizes human-facing test-runner output expectations.

The Foundation-side reconciliation branch is now rendering the thirteen former conflicts against this merged 0.1.2 managed surface. Foundation architecture remains in `docs/architecture/foundation.md`; managed protocol files should no longer duplicate repository-specific mission, dependency, ABI, or domain contracts merely to preserve historical wording.

## Lessons and accepted limitations

- Filesystem-root identity must use physical canonicalization where equivalence matters; lexical absolute paths were insufficient across Windows/macOS aliasing.
- Conflict preflight is intentionally all-conflicts-first, but adoption/sync are not crash-consistent filesystem transactions after mutation begins.
- Devkit managed templates must not automatically override semantically divergent brownfield files; semantic disposition precedes ownership.
- Evidence absent from canonical context may still be recoverable from authoritative Git history. Do not fabricate missing detail, but distinguish `not imported` from `not recoverable`.
- Large textual deletion during managed-file convergence is not itself proof of semantic loss: shared protocol may be deduplicated into stronger generic managed contracts while repository-specific rules remain in repository-owned architecture. Exact semantic review is still required before adoption.

## Active residue

- `OBL-20260913T182338Z-4F7C19` remains open until Foundation's real adoption `check` against merged Devkit 0.1.2 reaches a clean managed surface and the semantic reconciliation is locally validated.
- Revisit crash-consistent update mechanics if the managed surface or failure cost grows materially (`OBL-20260913T182338Z-B37E54`).

See `evidence/audits/genesis-devkit-slice.md` for the original extraction scope and `evidence/audits/foundation-managed-drift-reconstruction.md` for the live reconciliation.
