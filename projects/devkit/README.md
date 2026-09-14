# Devkit

Genesis historical import status: **SLICE COMPLETE** for current architecture, repository lifecycle, major brownfield lessons, and known deferred residue.

## Current state

- Verified main pin: `214dc5c933ef4f7db3fce9795a39d49ca382dfbf` (`merge: add brownfield repository adoption`).
- Devkit covers greenfield generation, safe managed-file synchronization, and brownfield adoption.
- Current merged C++ library template version: `0.1.1`.
- Managed snapshot: 16 shared paths.
- Bootstrap-only repository-owned paths: `.gitignore`, `README.md`, `CMakeLists.txt`, `.github/workflows/ci.yml`.
- Active reconciliation branch `jason-brother/foundation-managed-drift-reconciliation` is preparing template `0.1.2`; it is not authoritative merged state until validated and merged.

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

The current live Foundation versus Devkit 0.1.1 reconstruction independently reproduces the same 3 exact / 13 conflict partition. See `evidence/audits/foundation-managed-drift-reconstruction.md` for semantic dispositions and provenance.

## Lessons and accepted limitations

- Filesystem-root identity must use physical canonicalization where equivalence matters; lexical absolute paths were insufficient across Windows/macOS aliasing.
- Conflict preflight is intentionally all-conflicts-first, but adoption/sync are not crash-consistent filesystem transactions after mutation begins.
- Devkit's current template must not automatically override semantically divergent brownfield files.
- Evidence absent from canonical context may still be recoverable from authoritative Git history. Do not fabricate missing detail, but distinguish `not imported` from `not recoverable`.

## Active residue

- Foundation adoption is blocked on semantic reconciliation of the thirteen managed conflicts. The dispositions are now recorded; upstream Devkit enrichment/hardening must be validated and merged before Foundation-side alignment.
- The reconciliation branch generalizes stronger shared engineering protocol from Foundation and hardens unsafe CMD conditional chaining in generated wrappers.
- Add a dedicated immediate post-adoption sync no-op assertion for the successful MISSING-path test when adoption tests are next touched.
- Revisit crash-consistent update mechanics if the managed surface or failure cost grows materially.

See `evidence/audits/genesis-devkit-slice.md` for the original extraction scope and `evidence/audits/foundation-managed-drift-reconstruction.md` for the live reconciliation.
