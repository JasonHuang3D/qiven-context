# Devkit

Genesis historical import status: **SLICE COMPLETE** for current architecture, repository lifecycle, major brownfield lessons, and known deferred residue.

## Current accepted state

- Verified main pin: `022aaac1e169d556015b52c32af255031a6de332` (`merge: reconcile Foundation managed drift in Devkit 0.1.2`).
- Devkit covers greenfield generation, safe managed-file synchronization, and brownfield adoption.
- Current merged C++ library template version: `0.1.2`.
- Managed snapshot: 16 shared paths.
- Bootstrap-only repository-owned paths: `.gitignore`, `README.md`, `CMakeLists.txt`, `.github/workflows/ci.yml`.
- The accepted 0.1.2 merge tree is exactly the locally validated candidate tree from `125632e8ebb66aa0f9c3302a1fc93d63356d8004`.
- qiven-foundation is formally adopted into this managed lifecycle; accepted Foundation main is `6c09151e1a52830c66e6c7a97b5b68740154f475`.

## Qiven Operator Phase 1 — active work paused for session rollover

The owner and jason-brother agreed that continuing to grow Windows CMD glue for `[RUN]/[OK]`, color, layout, `&&` chaining, parallel work, Git gates, and CI handling would create a second orchestration system by accident. The new boundary is a reusable Python engineering control layer with CMD/shell kept thin.

The intended stack is:

```text
CMD / shell
  -> tools/qiven.cmd
  -> tools/qiven.py
  -> shared Python Operator runtime
  -> Git / CMake / ctest / gh / repository tools
```

Devkit owns the reusable mechanism. Repository-specific policy is small and declarative, currently modeled as managed `.qiven/operator.json`. Generated/adopted repositories must still remain independently usable and must not call back into a live Devkit checkout.

Phase 1 deliberately limits itself to already-proven friction: process execution, fail-fast semantics, dependency/parallel scheduling, human layout/color/heartbeat, buffered failure logs, exact-HEAD checks, diff-check, real clean-tree verification, JSON machine output, and asynchronous CI dispatch semantics. Plugin frameworks, daemons, RPC, webhook servers, and large task DSLs are explicitly not required yet.

Active branch: `jason-brother/devkit-operator-phase1`.

Exact preserved Qiven-v1 closeout head: `ac816bb06fbe978c1b41a730104114e8f5778610`, tree `1716d0d1f1f0ab47051be86d9a017191d6e62d82`, 11 commits ahead and 0 behind accepted main.

Branch surface relative to main currently changes nine files: `README.md`, `docs/operator-design.md`, `templates/cpp-library/managed-files.cmake`, managed `.qiven/operator.json.in`, managed `tools/qiven.cmd.in`, `tools/qiven.py.in`, `tools/qiven_operator.py.in`, `tools/operator-test.py`, and `tools/test.cmd`.

The first prototype candidate `48a2f86cb466651a68956cf8fa4ee894d1dfeeb9` failed local Devkit tests. One narrow repair at `ac816bb06fbe978c1b41a730104114e8f5778610` preserved the existing managed-list fixture anchor by moving `tools/delete-all-branches-but-main.cmd` after the new Operator managed paths. The owner reran that exact head and reported that tests still fail.

No additional repair was attempted because Qiven-v1 hit the chat length boundary. **The exact remaining failing suite/log is not preserved in the final turn. Qiven-v2 must obtain or reproduce it before modifying the branch.** No merge, template `0.1.3` release, or consumer synchronization has occurred.

See `sessions/2026-09-14-qiven-v1-closeout.md` and `OBL-20260914T105500Z-7F31B2`.

## Architectural model

- `qiven-toolchain-win` owns pinned executable tools.
- `qiven-devkit` owns repository templates, engineering conventions, explicit new/adopt/sync lifecycle tooling, and—once accepted—the reusable Qiven Operator runtime/policy surface.
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

## Operator-facing engineering lessons

- Filesystem-root identity must use physical canonicalization where equivalence matters; lexical absolute paths were insufficient across Windows/macOS aliasing.
- Conflict preflight is intentionally all-conflicts-first, but adoption/sync are not crash-consistent filesystem transactions after mutation begins.
- Devkit managed templates must not automatically override semantically divergent brownfield files; semantic disposition precedes ownership.
- Evidence absent from canonical context may still be recoverable from authoritative Git history. Do not fabricate missing detail, but distinguish `not imported` from `not recoverable`.
- Large textual deletion during managed-file convergence is not itself proof of semantic loss: shared protocol may be deduplicated into stronger generic managed contracts while repository-specific rules remain in repository-owned architecture. Exact semantic review is still required before adoption.
- Human-facing lifecycle commands are engineering interfaces. Adoption `check/apply` output should eventually receive the same deliberate layout/status discipline as the test runner (`OBL-20260914T081146Z-6D2F31`), preferably through the shared Operator rather than more bespoke CMD formatting.
- Raw `git diff` / `git diff --cached` should not be required in routine user validation because pager behavior can look like a hang; exact diff review belongs to jason-brother.
- `.cmd`/`.bat` gates inside interactive CMD success chains require `call` and explicit failure codes; longer workflows should not rely on ever-growing shell chains.
- Successful-but-silent validation creates human ambiguity. Material stages need explicit observable start/success/failure output.
- `git status --short` is diagnostic output, not a clean-tree gate. Clean-tree verification must inspect porcelain output and fail when non-empty.
- Remote CI is asynchronous. Dispatch should return; do not use hard-coded sleeps and latest-run guessing to simulate synchronous semantics. Automatic continuation belongs to exact identity + server-side/event-driven coordination.

## Active residue

- **Open / active:** resume and complete Qiven Operator Phase 1 after Qiven-v1 rollover (`OBL-20260914T105500Z-7F31B2`).
- Improve human-facing adoption-plan/result layout when that surface is next touched; the shared Operator is now the preferred abstraction (`OBL-20260914T081146Z-6D2F31`).
- Revisit crash-consistent update mechanics if the managed surface or failure cost grows materially (`OBL-20260913T182338Z-B37E54`).

See `evidence/audits/genesis-devkit-slice.md`, `evidence/audits/foundation-managed-drift-reconstruction.md`, `evidence/audits/foundation-devkit-adoption.md`, and `sessions/2026-09-14-qiven-v1-closeout.md`.
