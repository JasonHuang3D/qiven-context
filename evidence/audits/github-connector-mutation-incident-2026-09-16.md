# GitHub connector mutation incident — 2026-09-16

## Summary

During Context v2 canonical-merge closeout, Chat repeatedly selected/invoked a high-level GitHub contents mutation action while intending a different repository operation. The connector then faithfully executed the invoked write, creating unintended files/commits. This was an assistant/tool-orchestration action-selection failure. Current evidence does not prove a GitHub backend defect.

The incident occurred after Context v2 candidate `37fdbb33eb527f7df56e2ed1de3f58115c5315be` had passed exact-head validation. No unintended file content remains in canonical `qiven-context/main`.

## Observed accidental mutations

1. `main`: accidental file `x` at commit `fababda2b70fe07159c264b9e704afa9763dc356`; explicitly removed by `7ece0fa51574e5b83ba13ceb449bc3513fde39d8`.
2. migration branch: accidental file `dummy` at commit `5506c4158289e3f2e620cae69a3eb45d36bcac49`; explicitly removed by `df281ca2e5261f2362b3cb9299eeffda4b383a60`. The immutable validated commit `37fdbb33...` remained available and authoritative as the tested candidate identity.
3. `main`: accidental file `THIS_SHOULD_NOT_BE_CREATED` at commit `3996e1e59948c847f4d0d853d91eee1903d015bd`; explicitly removed by `b76922f263685854de28213d786a36466b51cb5c`.
4. `main`: accidental file `STOP` at commit `55199d4cc76e81254b4c2d8f5283725ef8bce6cc`; explicitly removed by `f50cdea873e8c516f5f1cad4f135160fdb01fbd0`.

After the final repair, `main@f50cdea...` had tree `8e90a3d8381f3778c1bd7d54181bdb9282b721a0`, exactly matching the pre-incident/pre-v2-main tree. The accidental commits therefore remained only as auditable history, not as current file content.

## Recovery and final publication

The project owner then executed a human-controlled local Git merge script. Live GitHub verification established canonical `qiven-context/main` at merge commit `9b2bba53e61d80468f0a3d6bf9147c9295de0877` with tree `8dc5c93ea4b2a2d0362767415e019040053ed2a8`.

That merge has first parent `f50cdea873e8c516f5f1cad4f135160fdb01fbd0` and second parent the exact validated Context v2 candidate `37fdbb33eb527f7df56e2ed1de3f58115c5315be`. The merge tree exactly equals the validated candidate tree.

## Additional human-facing script defect

The local merge script itself exposed a separate usability defect: it was written as an automation-style fail-fast batch file with terminal `exit /b` paths, but was handed to a human who launched it by double-click. The transient CMD window therefore closed before the human could reliably inspect the final status. Read-only GitHub verification was required to confirm success.

This is now governed by `collaboration/human-facing-executable-contract.md`: direct human entrypoints default to visible terminal status plus `pause` on success and failure, with non-pausing behavior available only through an explicit automation mode.

## Current guardrail

High-level Chat-side GitHub contents mutation is suspended for canonical merges and other critical writes until explicitly requalified. Read-only connector use remains allowed. Critical mutations use a human-visible local Git path by default; low-level Git object/ref mutation is permissible only with explicit exact identities and reviewed ref semantics.

## Classification

- Materiality: high — canonical repository mutation path and exact-head acceptance integrity.
- Data loss: none observed.
- Canonical content corruption: none remaining.
- Root cause established: assistant/tool action-selection/invocation failure; no evidence sufficient to assign a connector backend defect.
- Follow-up: preserve the guardrail in active memory and Git workflow; requalify only through an isolated non-canonical test when there is a real need.
