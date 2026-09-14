# Foundation managed-drift reconstruction

## Scope

This audit reconstructs the qiven-foundation versus qiven-devkit managed surface and records the semantic disposition required before brownfield adoption.

Live refs initially inspected:

- `qiven-foundation/main`: `f1880847e046425c7f3f3cad22a07d0008aad359`
- `qiven-devkit/main`: `214dc5c933ef4f7db3fce9795a39d49ca382dfbf`
- Devkit template: `templates/cpp-library/managed-files.cmake`, template version `0.1.1`

Foundation adoption parameters are the ones documented by qiven-devkit:

- repository/project/target/solution: `qiven-foundation`
- alias: `qiven::foundation`
- C++ namespace: `qiven`
- test option: `QIVEN_BUILD_TESTS`

## Historical path recovery

Genesis and the Batch 004 cold-boot candidate correctly preserved an evidence gap: qiven-context itself knew only `3 exact / 13 content drift / 0 missing` and did not contain the individual thirteen historical paths. During this reconciliation, however, direct qiven-devkit Git archaeology recovered stronger evidence that had not been imported into qiven-context.

The original brownfield-adoption implementation commit `118de43fc74c5bfd101e41008d5aa8fbe0f37345` contains `tools/adoption-test.cmake` with an explicit **Foundation-shaped regression**. It defines the three exact managed paths as:

- `.editorconfig`
- `.gitattributes`
- `tools/delete-all-branches-but-main.cmd`

and deliberately makes **every other path in `QIVEN_MANAGED_FILES` conflicting**. Because that same template manifest contains sixteen managed paths, this repository evidence reconstructs the historical thirteen-path conflict set directly rather than by guessing from the current tree.

Therefore the earlier statement "individual path details are not reconstructed" is now superseded as an evidence-gap statement. It was true of the then-imported durable evidence, but the missing detail was recoverable from qiven-devkit Git history.

This does **not** retroactively turn the Batch 004 candidate's refusal to invent paths into hallucination: the candidate followed the frozen durable evidence and passed the intended anti-fabrication rubric. It does reveal a limitation in that probe: the fact was absent from qiven-context but not absent from the full permitted live/history source universe. The lesson is to distinguish **not imported into durable context** from **not recoverable from authoritative repositories**.

## Current managed-surface classification

The Devkit 0.1.1 managed set has sixteen paths. Current live reconstruction yields **3 EXACT, 0 MISSING, 13 CONFLICT**, and the exact/current split matches the Foundation-shaped regression preserved in the original adoption implementation.

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
| `tools/resolve-toolchain.cmd` | CONFLICT | **Drive Devkit template fix.** Keep Devkit's scoped environment/export design, but replace unsafe one-line conditional `& exit /b 1` constructs with grouped/goto-safe control flow. |
| `tools/format.cmd` | CONFLICT | Adopt Devkit structure after the resolver fix. Its compact failure grouping is semantically adequate; no Foundation-specific behavior needs ownership. |
| `tools/format-check.cmd` | CONFLICT | Adopt Devkit structure after the resolver fix. Its compact failure grouping is semantically adequate; no Foundation-specific behavior needs ownership. |
| `tools/gen-vs2022-x64.cmd` | CONFLICT | **Drive Devkit template fix.** Replace ungrouped `if errorlevel 1 popd & exit /b 1` with grouped/goto-safe control flow. Preserve parameterized solution naming. |
| `tools/apply-jason-brother.cmd` | CONFLICT | Adopt Devkit rendering. It removes interactive `pause` from error paths and is better suited to automation; keep repository-name parameterization. |
| `tools/delete-all-branches-but-main.cmd` | EXACT | No action. |

The thirteen historical/current conflicting paths are therefore:

1. `.clang-format`
2. `CMakePresets.json`
3. `AGENTS.md`
4. `docs/engineering/README.md`
5. `docs/engineering/implementation-standard.md`
6. `docs/engineering/testing-standard.md`
7. `docs/engineering/worker-protocol.md`
8. `docs/engineering/feature-spec.md`
9. `tools/resolve-toolchain.cmd`
10. `tools/format.cmd`
11. `tools/format-check.cmd`
12. `tools/gen-vs2022-x64.cmd`
13. `tools/apply-jason-brother.cmd`

## Why the thirteen conflicts are not one kind of drift

Treating all thirteen as "Foundation differs from template, therefore overwrite Foundation" would destroy useful semantics and would also import unsafe Windows command-control patterns from the 0.1.1 templates.

The conflicts split into three categories:

1. **Representation-only / shared-template wins** — `.clang-format`, `CMakePresets.json`, `format.cmd`, `format-check.cmd`, `apply-jason-brother.cmd`.
2. **Foundation carries stronger shared engineering cognition** — root agent contract plus the five engineering protocol documents. These should drive Devkit template enrichment before Foundation becomes managed.
3. **Devkit template defect/hardening** — `resolve-toolchain.cmd` and `gen-vs2022-x64.cmd` contain ambiguous/unsafe CMD conditional chaining that should be fixed upstream before adoption.

## Devkit reconciliation implementation

A qiven-devkit reconciliation branch was created from exact main `214dc5c933ef4f7db3fce9795a39d49ca382dfbf`:

`jason-brother/foundation-managed-drift-reconciliation`

The branch:

- generalizes the stronger shared agent/engineering protocol from Foundation into Devkit-managed templates while keeping repository architecture domain-owned;
- hardens generated `resolve-toolchain.cmd` and `gen-vs2022-x64.cmd` control flow;
- adds a static regression detector for unsafe ungrouped `IF ... & exit /b` patterns in generated CMD templates;
- advances the managed template version from `0.1.1` to `0.1.2` and updates version-evolution fixtures.

These changes require local qiven-devkit validation before any merge or Foundation-side alignment.

## Immediate next implementation order

1. Validate the qiven-devkit reconciliation branch locally and complete its normal exact-head review/merge gate.
2. Render/reconcile Foundation's thirteen managed conflicts against the accepted Devkit 0.1.2 semantics, preserving Foundation-owned architecture/domain content outside the managed surface.
3. Commit and validate the Foundation reconciliation so the adoption `check` reaches `16 EXACT / 0 MISSING / 0 CONFLICT`.
4. Only then run Foundation adoption `apply`, creating `.qiven` ownership state without overwriting unresolved semantics.

`OBL-20260913T182338Z-4F7C19` remains open until every conflict has an implemented and validated semantic disposition and the adoption check is clean.
