# Current State

## Active objective

Context v2 is canonical and the immediate objective is to make its `ContextView<ChatGPT, Jason>` + Qiven Operator workflow operational on JasonPC. The clean Context candidate is `jason-brother/context-v2-operator-runtime`; resolve its exact remote head live before validation. After this operational acceptance, Qiven-v6 closes and the next session begins the `qiven-context.exe` / Context Engine architecture obligation `OBL-20260916T125000Z-5A8C31`.

## Context authority and governance

- Canonical project cognition remains the GitHub remote `JasonHuang3D/qiven-context`; local repositories are non-authoritative working materializations.
- GitHub account-level identity remains the current governance authentication boundary.
- ContextView adapts interaction, environment, and workflow but cannot override identity-independent ProjectContext truth.
- GitHub remains canonical until a separately accepted Context Engine authority migration proves semantic equivalence, provenance, continuity, backup/restore, and governance behavior.

## ContextView<ChatGPT, Jason>

- `views/chatgpt-jason.yaml` composes the current view.
- `views/environments/jasonpc.yaml` records durable JasonPC facts such as `D:\JasonWork`, `C:\Env`, known Git/Python tool families, MSVC/Visual Studio 2022/Unreal Engine/Unity families, and Clash Verge routing intent. Mutable paths, versions, PATH and network state are live-verified when required.
- `views/workflows/chatgpt-jason-local-execution.md` owns Workflow 1 and Workflow 2.

Workflow 1 is active: ChatGPT may develop remotely, then Jason switches to Human Manual Mode and invokes Qiven Operator for local evidence/execution. Workflow 2 remains fail-closed until Host production authority is accepted; then Host invokes the same Operator task/gate surface.

## Operator operationalization

The clean Context candidate vendors Qiven Operator runtime and a qiven-context-specific `.qiven/operator.json`. Its `context-local` gate runs bootstrap, full tests, diff-check, and clean-tree; `--expect-head` adds exact-head binding. Task `cleanup-v6-temp` performs identity-safe cleanup of known Qiven-v6 temp clones and refuses to delete dirty or non-qiven-context repositories.

The generic Operator packaging candidate in qiven-devkit is `f5945df3c8c85b3fc49e228dcf7f88339567ff24` on `jason-brother/operator-generic-component`. It is not yet accepted and intentionally does not disturb the mature cpp-library template path before non-C++ use is proven.

## Safety and mutation guardrails

- `OBL-20260915T163500Z-9D4C72` remains open; mutating DCR/remote-AI execution on JasonPC is still suspended.
- High-level Chat-side GitHub contents mutation is still not accepted for critical writes after the 2026-09-16 action-selection incident. Low-level exact Git object/ref mutation remains the only Chat-side critical-write path currently admitted.
- `OBL-20260916T102700Z-7C2A91` tracks Qiven-v6 unmanaged temp-clone cleanup; human memory is not the cleanup mechanism.

## Preserved Host state

Latest formally accepted Host checkpoint remains `8e5b9dec64bf739af84e981df12afc1969599738`, CI run `35060483714`. Corrected unaccepted Host candidate `49e69c02fe2ded0b9607ccb4090c21cde96b8a1c` remains preserved and paused while Context v2 is operationalized and the next Context Engine architecture session takes priority.

## Next boundary

From the existing `D:\JasonWork\qiven-context` working copy, bootstrap the clean `jason-brother/context-v2-operator-runtime` branch, run Operator task `cleanup-v6-temp`, then run the Operator `context-local` gate against the exact remote branch head. Do not create another unmanaged temp clone. If that exact candidate passes and is canonically merged, close Qiven-v6; next session begins `qiven-context.exe` / Context Engine architecture rather than resuming Host implementation first.
