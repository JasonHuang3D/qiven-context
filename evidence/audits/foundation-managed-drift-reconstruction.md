# Foundation managed-drift reconstruction

## Scope

This audit reconstructs the qiven-foundation versus qiven-devkit managed surface and records the semantic disposition required before brownfield adoption.

Live refs initially inspected:

- `qiven-foundation/main`: `f1880847e046425c7f3f3cad22a07d0008aad359`
- initial `qiven-devkit/main`: `214dc5c933ef4f7db3fce9795a39d49ca382dfbf`
- initial Devkit template version: `0.1.1`

Accepted upstream reconciliation:

- exact locally validated Devkit candidate: `125632e8ebb66aa0f9c3302a1fc93d63356d8004`
- accepted no-ff Devkit merge: `022aaac1e169d556015b52c32af255031a6de332`
- merge tree / validated candidate tree: `8a4f4e2237e9b7c251e207a185a4e0c7edd1ac4d`
- merged Devkit template version: `0.1.2`

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

Therefore the earlier statement "individual path details are not reconstructed" is superseded as an evidence-gap statement. It was true of the then-imported durable evidence, but the missing detail was recoverable from qiven-devkit Git history.

This does **not** retroactively turn the Batch 004 candidate's refusal to invent paths into hallucination: the candidate followed the frozen durable evidence and passed the intended anti-fabrication rubric. It does reveal a limitation in that probe: the fact was absent from qiven-context but not absent from the full permitted live/history source universe. The lesson is to distinguish **not imported into durable context** from **not recoverable from authoritative repositories**.

## Pre-reconciliation managed-surface classification

The Devkit 0.1.1 managed set had sixteen paths. The live reconstruction yielded **3 EXACT, 0 MISSING, 13 CONFLICT**, and the exact/current split matched the Foundation-shaped regression preserved in the original adoption implementation.

| Path | Pre-reconciliation class | Semantic disposition |
| --- | --- | --- |
| `.clang-format` | CONFLICT | Adopt Devkit content. Difference is layout/blank-line organization; formatting semantics are equivalent. |
| `.editorconfig` | EXACT | No action. |
| `.gitattributes` | EXACT | No action. |
| `CMakePresets.json` | CONFLICT | Adopt Devkit rendering for the Foundation parameters. Build/test preset semantics remain equivalent; difference is representation/description wording. |
| `AGENTS.md` | CONFLICT | **Drive Devkit template change.** Generalize shared worker/authority/safety/validation semantics while keeping repository architecture/domain rules repository-owned. |
| `docs/engineering/README.md` | CONFLICT | **Drive Devkit template change.** Preserve shared role/flow/precedence/protocol-evolution semantics in generalized form. |
| `docs/engineering/implementation-standard.md` | CONFLICT | **Drive Devkit template change.** Generalize shared C++ implementation discipline; keep Foundation-only architecture repository-owned. |
| `docs/engineering/testing-standard.md` | CONFLICT | **Drive Devkit template change.** Preserve risk-based testing, FULL/FOCUSED rules, baseline-failure classification, formatting/new-file handling, cross-platform limits, detector integrity, and human-facing runner quality. |
| `docs/engineering/worker-protocol.md` | CONFLICT | **Drive Devkit template change.** Preserve local-only branch stack, batch/usage boundaries, validation, blocker/handoff, and Chat-review workflow in generalized form. |
| `docs/engineering/feature-spec.md` | CONFLICT | **Drive Devkit template change.** Preserve the implementation-ready CTO specification contract while generalizing Foundation-specific examples. |
| `tools/resolve-toolchain.cmd` | CONFLICT | **Drive Devkit template fix.** Keep scoped environment/export design and use grouped/goto-safe error control flow. |
| `tools/format.cmd` | CONFLICT | Adopt Devkit structure after resolver fix; no Foundation-specific behavior needs ownership. |
| `tools/format-check.cmd` | CONFLICT | Adopt Devkit structure after resolver fix; no Foundation-specific behavior needs ownership. |
| `tools/gen-vs2022-x64.cmd` | CONFLICT | **Drive Devkit template fix.** Use grouped/goto-safe failure control flow and preserve parameterized solution naming. |
| `tools/apply-jason-brother.cmd` | CONFLICT | Adopt Devkit rendering; noninteractive failure handling is better suited to automation. |
| `tools/delete-all-branches-but-main.cmd` | EXACT | No action. |

The thirteen historical/current conflicting paths were:

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

## Why the thirteen conflicts were not one kind of drift

Treating all thirteen as "Foundation differs from template, therefore overwrite Foundation" would have destroyed useful semantics and imported unsafe Windows command-control patterns from the 0.1.1 templates.

The conflicts split into three categories:

1. **Representation-only / shared-template wins** — `.clang-format`, `CMakePresets.json`, `format.cmd`, `format-check.cmd`, `apply-jason-brother.cmd`.
2. **Foundation carried stronger shared engineering cognition** — root agent contract plus the five engineering protocol documents. These drove Devkit template enrichment before Foundation became managed.
3. **Devkit template defect/hardening** — `resolve-toolchain.cmd` and `gen-vs2022-x64.cmd` required safer CMD conditional control flow before adoption.

## Accepted Devkit 0.1.2 reconciliation

The qiven-devkit reconciliation branch started from exact main `214dc5c933ef4f7db3fce9795a39d49ca382dfbf` and produced the locally validated exact head `125632e8ebb66aa0f9c3302a1fc93d63356d8004`.

That candidate:

- generalized the stronger shared agent/engineering protocol from Foundation into Devkit-managed templates while keeping repository architecture domain-owned;
- hardened generated `resolve-toolchain.cmd` and `gen-vs2022-x64.cmd` control flow;
- added a static regression detector for unsafe ungrouped `IF ... & exit /b` patterns in generated CMD templates;
- added a dedicated MISSING-path adoption immediate-sync no-op regression, satisfying `OBL-20260913T182338Z-8A21D6`;
- standardized human-facing test-runner layout, status tags, color/no-color behavior, buffered expected-failure logs, concise summaries, and verbose opt-in;
- advanced the managed template version from `0.1.1` to `0.1.2`.

The user locally validated that exact head. jason-brother then performed exact remote review and created no-ff merge `022aaac1e169d556015b52c32af255031a6de332`; its tree `8a4f4e2237e9b7c251e207a185a4e0c7edd1ac4d` exactly equals the validated candidate tree, with parents `[214dc5c933ef4f7db3fce9795a39d49ca382dfbf, 125632e8ebb66aa0f9c3302a1fc93d63356d8004]`.

## Foundation-side semantic preservation review

A Foundation reconciliation branch was created from exact main `f1880847e046425c7f3f3cad22a07d0008aad359`:

`jason-brother/foundation-managed-drift-reconciliation`

The first rendered convergence commit is `bb2f4b96c0d7960ece41d54f3244f88ef17df556`. It replaces exactly the thirteen former conflict paths with the Devkit 0.1.2 target rendering while leaving the three previously exact managed paths and all bootstrap/domain files untouched.

The raw diff is intentionally large because Foundation's managed protocol historically duplicated both shared engineering law and repository-specific architectural law. Before treating that textual shrinkage as safe, the pre-reconciliation Foundation contracts were reviewed against both the merged Devkit 0.1.2 managed protocol and the unchanged repository-owned `docs/architecture/foundation.md`.

Disposition of the apparent semantic deletion:

- Foundation mission, non-goals, dependency law, namespace/public-private boundaries, language baseline, error model, allocator/memory contracts, RTTI policy, representation/ABI law, supported-platform/CI contract, testing law, development-environment contract, and Foundation change rule remain in `docs/architecture/foundation.md`; they are repository architecture and should not be duplicated into a shared managed template merely to retain old wording.
- Shared authority, independent engineering judgment, scope boundaries, ownership/failure discipline, host safety, Git identity prohibition, branch-stack rules, validation profiles, baseline-failure handling, detector integrity, handoff/blocker behavior, and CTO review boundaries remain represented across Devkit 0.1.2 `AGENTS.md` and `docs/engineering/*`.
- Detailed Foundation examples and repeated prose were intentionally deduplicated where the generalized contract preserves the same governing behavior.
- The former "roughly one third of the Work allowance" soft-budget heuristic was deliberately generalized upstream to a finite authorized queue plus a conservative validation/handoff reserve when reliable usage information exists. This is an intentional shared-protocol simplification, not an accidental Foundation-only deletion; exact percentages must not be fabricated when the runtime does not expose reliable usage.
- Foundation-specific `windows.h` concern remains covered at the architectural level by the requirement to isolate platform-specific code and keep native/platform types out of public contracts, while the generalized implementation standard requires the least invasive native dependency and no platform-header leakage. The historical header-specific wording is not treated as separate managed ownership.

No unresolved Foundation domain/architecture contract was found to require a managed-file divergence after this review. This does **not** yet prove the rendered candidate is adoptable: the next authority is the real Devkit 0.1.2 brownfield `check` on the clean Foundation candidate working tree.

## Next gate

1. Sync local qiven-devkit `main` to exact merged ref `022aaac1e169d556015b52c32af255031a6de332`.
2. Sync local qiven-foundation reconciliation branch to exact candidate `bb2f4b96c0d7960ece41d54f3244f88ef17df556` and confirm the working tree is clean.
3. Run Devkit brownfield adoption `check` against that exact Foundation candidate. The required result is all sixteen managed paths `EXACT`, with `0 MISSING / 0 CONFLICT`, and no target mutation.
4. Run Foundation formatting / full Debug+Release validation and `git diff --check` on the reconciliation candidate.
5. Only after those gates pass may the Foundation reconciliation be accepted/merged. Actual adoption `apply` remains a separate subsequent step so `.qiven` ownership state is introduced only after the semantic reconciliation is proven clean.

`OBL-20260913T182338Z-4F7C19` remains open until the real adoption check is clean and the Foundation reconciliation candidate is validated. Foundation Devkit adoption itself remains the next distinct step after this obligation closes.
