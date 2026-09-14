# Foundation managed-drift reconstruction

## Scope

This audit reconstructs the **current** qiven-foundation versus qiven-devkit managed surface from live repository state. It does not pretend to recover the missing historical per-path rehearsal report.

Live refs inspected:

- `qiven-foundation/main`: `f1880847e046425c7f3f3cad22a07d0008aad359`
- `qiven-devkit/main`: `214dc5c933ef4f7db3fce9795a39d49ca382dfbf`
- Devkit template: `templates/cpp-library/managed-files.cmake`, template version `0.1.1`

Foundation adoption parameters are the ones documented by qiven-devkit:

- repository/project/target/solution: `qiven-foundation`
- alias: `qiven::foundation`
- C++ namespace: `qiven`
- test option: `QIVEN_BUILD_TESTS`

This is a live reconstruction. The earlier durable statement remains unchanged: the exact thirteen historical drift paths were not reconstructed from the old rehearsal evidence. The fact that the current live reconstruction again yields thirteen conflicts does not retroactively prove path-by-path identity with that missing historical report.

## Current managed-surface classification

The Devkit 0.1.1 managed set has sixteen paths. Current live reconstruction yields **3 EXACT, 0 MISSING, 13 CONFLICT**.

| Path | Current class | Semantic disposition |
| --- | --- | --- |
| `.clang-format` | CONFLICT | Adopt Devkit content. Difference is layout/blank-line organization; formatting semantics are equivalent. |
| `.editorconfig` | EXACT | No action. |
| `.gitattributes` | EXACT | No action. |
| `CMakePresets.json` | CONFLICT | Adopt Devkit rendering for the Foundation parameters. Build/test preset semantics remain equivalent; difference is representation/description wording. |
| `AGENTS.md` | CONFLICT | **Drive Devkit template change.** Foundation contains materially richer shared worker/authority/safety/validation semantics. Do not replace it with the current compressed Devkit contract. Generalize shared rules into the managed template while keeping repository architecture/domain rules repository-owned. |
| `docs/engineering/README.md` | CONFLICT | **Drive Devkit template change.** Preserve the richer shared role/flow/precedence/protocol-evolution semantics in generalized form. |
| `docs/engineering/implementation-standard.md` | CONFLICT | **Drive Devkit template change.** Foundation contains materially stronger shared C++ implementation discipline than the compressed template. Generalize shared rules; keep Foundation-only architecture in repository-owned architecture material. |
| `docs/engineering/testing-standard.md` | CONFLICT | **Drive Devkit template change.** Preserve risk-based semantic testing, FULL/FOCUSED rules, baseline-failure classification, formatting/new-file handling, cross-platform limits, and detector-integrity rules. |
| `docs/engineering/worker-protocol.md` | CONFLICT | **Drive Devkit template change.** Preserve the detailed local-only branch stack, batch/usage boundaries, validation, blocker/handoff, and Chat-review workflow in generalized form. |
| `docs/engineering/feature-spec.md` | CONFLICT | **Drive Devkit template change.** Preserve the implementation-ready CTO specification contract and generalize Foundation-specific examples where appropriate. |
| `tools/resolve-toolchain.cmd` | CONFLICT | **Drive Devkit template fix.** Keep Devkit's scoped environment/export design, but replace unsafe one-line conditional `& exit /b 1` constructs with grouped/goto-safe control flow. Current template can unconditionally exit because CMD command separators are outside the `if`. |
| `tools/format.cmd` | CONFLICT | Adopt Devkit structure after the resolver fix. Its compact failure grouping is semantically adequate; no Foundation-specific behavior needs ownership. |
| `tools/format-check.cmd` | CONFLICT | Adopt Devkit structure after the resolver fix. Its compact failure grouping is semantically adequate; no Foundation-specific behavior needs ownership. |
| `tools/gen-vs2022-x64.cmd` | CONFLICT | **Drive Devkit template fix.** Replace `if errorlevel 1 popd & exit /b 1` with grouped/goto-safe control flow; as written, CMD can execute the exit unconditionally. Preserve parameterized solution naming. |
| `tools/apply-jason-brother.cmd` | CONFLICT | Adopt Devkit rendering. It removes interactive `pause` from error paths and is better suited to automation; keep repository-name parameterization. |
| `tools/delete-all-branches-but-main.cmd` | EXACT | No action. |

## Why the thirteen conflicts are not one kind of drift

Treating all thirteen as "Foundation differs from template, therefore overwrite Foundation" would destroy useful semantics and would also import at least two Windows control-flow defects from the current Devkit templates.

The conflicts split into three categories:

1. **Representation-only / shared-template wins** — `.clang-format`, `CMakePresets.json`, `format.cmd`, `format-check.cmd`, `apply-jason-brother.cmd`.
2. **Foundation carries stronger shared engineering cognition** — root agent contract plus the five engineering protocol documents. These should drive a Devkit template enrichment before Foundation becomes managed.
3. **Devkit template defect** — `resolve-toolchain.cmd` and `gen-vs2022-x64.cmd` contain unsafe CMD conditional chaining that must be fixed upstream before adoption.

## Immediate next implementation order

1. Modify qiven-devkit managed templates according to the dispositions above, with Windows regression coverage for the two CMD control-flow defects.
2. Validate qiven-devkit locally and through its normal review/merge gate.
3. Re-run Foundation adoption `check` against the new Devkit main. The expected target state is `16 EXACT / 0 MISSING / 0 CONFLICT` after intentional Foundation-side reconciliation changes.
4. Only then run Foundation adoption `apply`, creating `.qiven` ownership state without overwriting unresolved semantics.

`OBL-20260913T182338Z-4F7C19` remains open until every conflict has an implemented and validated semantic disposition and the adoption check is clean.
