# Devkit

Genesis historical import status: **SLICE COMPLETE** for current architecture, repository lifecycle, major brownfield lessons, and known deferred residue.

## Current state

- Verified main pin: `214dc5c933ef4f7db3fce9795a39d49ca382dfbf` (`merge: add brownfield repository adoption`).
- Devkit covers greenfield generation, safe managed-file synchronization, and brownfield adoption.
- Current C++ library template version: `0.1.1`.
- Managed snapshot: 16 shared paths.
- Bootstrap-only repository-owned paths: `.gitignore`, `README.md`, `CMakeLists.txt`, `.github/workflows/ci.yml`.

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

## Lessons and accepted limitations

- Filesystem-root identity must use physical canonicalization where equivalence matters; lexical absolute paths were insufficient across Windows/macOS aliasing.
- Conflict preflight is intentionally all-conflicts-first, but adoption/sync are not crash-consistent filesystem transactions after mutation begins.
- Devkit's current template must not automatically override semantically divergent brownfield files.

## Deferred residue

- Foundation adoption remains pending semantic review of 13 historically observed managed-file content drifts; their individual details are not reconstructed from the currently available evidence.
- Add a dedicated immediate post-adoption sync no-op assertion for the successful MISSING-path test when adoption tests are next touched.
- Revisit crash-consistent update mechanics if the managed surface or failure cost grows materially.

See `evidence/audits/genesis-devkit-slice.md` for extraction scope, provenance, and gaps.
