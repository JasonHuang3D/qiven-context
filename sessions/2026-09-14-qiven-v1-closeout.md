# Qiven-v1 Closeout / Qiven-v2 Cold-Boot Handoff

Closed at 2026-09-14T10:55:00Z (2026-09-14 18:55 Asia/Shanghai).

## Purpose

This handoff preserves the end state of the long Qiven-v1 Chat session so a fresh Qiven-v2 Chat can resume without reconstructing the project from model-native memory. Treat repository evidence and the qiven-context cold-boot protocol as authoritative. Do not invent any missing failure detail from the final Devkit test run.

## Collaboration identity and protocol

- The user is project owner / PM and machine-local validation operator.
- `jason-brother` is the assistant role: CTO, architect, reviewer, decision partner, remote GitHub maintainer, and conditionally authorized merge operator.
- `jason-worker` is the local implementation/execution agent and is not jason-brother.
- Chat is the default mode. Do not hand off to Work unless the user explicitly requests it.
- Windows CMD is the user's normal local shell.
- Never change `git user.name` or `git user.email`.
- User validation is exact-head scoped. After the user validates an exact final head and says `all pass`, jason-brother performs exact remote review and may merge that exact head no-ff under ADR-0021. Any commit after validation invalidates the previous PASS.
- Prefer CLI/API/repository scripts over browser clicking for engineering operations when a reliable non-interactive path exists.

## Live accepted main refs at handoff

- qiven-foundation main: `6c09151e1a52830c66e6c7a97b5b68740154f475` — Foundation Phase I complete and formally Devkit-managed.
- qiven-devkit main: `022aaac1e169d556015b52c32af255031a6de332` — Devkit template 0.1.2 accepted.
- qiven-math main: `e38afb6b47f2052926fdc2a2de8cab0238cdfb23` — Math Batch 008 complete; later CI Foundation pin refresh merged.
- qiven-toolchain-win main: `a79825031e838d80354d31489c87327dd6adbfb7`.
- qiven-context main before this handoff branch: `ee30837d6f643c5cffb86f4ffe745a421737cb7f`.
- qiven-context working branch: `jason-brother/operator-cli-observability`; it intentionally contains unmerged durable process/context updates and this rollover handoff. Resolve and verify its live head before acting.

## Major completed work before the rollover

1. qiven-context Phase 0 / Batches 001-004 completed, including Genesis Import, Context Compiler / obligation retrieval, and Cold-Boot Acceptance.
2. Foundation managed drift was historically reconstructed and semantically reconciled. Foundation reached `16 EXACT / 0 MISSING / 0 CONFLICT`, then formal Devkit adoption added only `.qiven/repo.json` and `.qiven/generated-state.cmake`; immediate sync was byte-stable.
3. Math Batch 008 vector algorithms completed: dot/cross/length_squared, robust max-component-scaled length, normalize/try_normalize, distance, and explicit absolute-tolerance is_near. Exact candidate `740daca418fce5981f4f40079c2322f2912545e6` merged as `95c29339dd891843870d2b8e4962c86494dfd505`; full CI run `34826905065` passed.
4. Math CI's stale Foundation checkout pin was refreshed on candidate `8bdb928e681b3e1a68e89d0df637bc90508503e4`, full CI run `34830331391` passed, and it merged no-ff as Math main `e38afb6b47f2052926fdc2a2de8cab0238cdfb23`.

## Engineering-operator lessons established in Qiven-v1

The session progressively exposed that ad-hoc shell orchestration was becoming its own source of friction and ambiguity:

- Raw `git diff` / `git diff --cached` can invoke a pager in Windows CMD and appear hung; user-facing validation should use non-interactive checks, while exact diff review belongs to jason-brother.
- A raw `.cmd`/`.bat` inside an interactive CMD `&&` chain is not a sufficiently trustworthy gate. Chained batch gates require `call` and explicit nonzero failure codes.
- A successful-but-silent command such as `git diff --check` creates human ambiguity about whether it ran. Material human-facing stages need explicit start/success markers.
- `git status --short` is diagnostic output, not a clean-tree gate, because dirty status normally still exits 0. A real clean-tree gate must inspect porcelain output and fail when non-empty.
- Remote CI is asynchronous. Do not fake synchronous semantics with `timeout 5`, latest-run guessing, run-ID discovery races, or shell polling. A local command should dispatch and return. Later result verification should be exact-identity based; future automatic continuation should use server-side workflow dependencies, webhook/event-driven coordination, or another real asynchronous mechanism.

These lessons led to the next architectural step: stop growing CMD glue and build a reusable Python engineering orchestration layer.

## Qiven Operator Phase 1 — architectural decision

The agreed direction is a Qiven local engineering control plane implemented primarily in Python:

```text
CMD / shell = thin transport
        -> tools/qiven.cmd
        -> tools/qiven.py
        -> shared Python operator runtime
        -> Git / CMake / ctest / gh / repository tools
```

Devkit owns the reusable mechanism; each managed repository carries small declarative policy, currently `.qiven/operator.json`. Generated/adopted repositories must remain independently usable and must not call back into a live Devkit checkout.

Phase 1 intentionally targets only already-proven friction: process execution, fail-fast semantics, parallel tasks, human layout, color/no-color behavior, heartbeat/liveness, buffered failure logs, exact-HEAD checks, diff-check, real clean-tree checking, JSON machine output, and asynchronous CI dispatch semantics. Do not expand yet into a plugin framework, daemon, RPC service, webhook server, or large task DSL.

The intended future interaction is approximately:

```cmd
tools\qiven.cmd gate
```

rather than jason-brother dynamically emitting a long mini-orchestration program in each chat turn.

## Exact unresolved Devkit state — STOP HERE BEFORE FIXING

Active Devkit branch:

`jason-brother/devkit-operator-phase1`

Latest exact remote head confirmed at handoff:

`ac816bb06fbe978c1b41a730104114e8f5778610`

Tree:

`1716d0d1f1f0ab47051be86d9a017191d6e62d82`

It is 11 commits ahead and 0 behind Devkit main `022aaac1e169d556015b52c32af255031a6de332`.

Current branch surface relative to main is nine changed files:

- `README.md`
- `docs/operator-design.md`
- `templates/cpp-library/managed-files.cmake`
- `templates/cpp-library/managed/.qiven/operator.json.in`
- `templates/cpp-library/managed/tools/qiven.cmd.in`
- `templates/cpp-library/managed/tools/qiven.py.in`
- `templates/cpp-library/managed/tools/qiven_operator.py.in`
- `tools/operator-test.py`
- `tools/test.cmd`

The first candidate head `48a2f86cb466651a68956cf8fa4ee894d1dfeeb9` failed the local Devkit test runner. One repair was then made in commit `ac816bb06fbe978c1b41a730104114e8f5778610` (`test: preserve managed-list fixture anchor`), which only reordered `tools/delete-all-branches-but-main.cmd` to remain the fixture anchor after adding the three new Operator managed files.

The user reran at exact HEAD `ac816bb06fbe978c1b41a730104114e8f5778610` and reported that tests still fail. The user explicitly instructed Qiven-v1 to stop repairing because the chat reached its conversation-length boundary.

**Critical anti-hallucination rule:** the exact remaining failing suite/log is not preserved in this final turn. Qiven-v2 must obtain the failure evidence from the user or reproduce it locally before modifying Devkit. Do not infer the remaining root cause merely from the repository diff.

No Operator branch merge has occurred. Devkit main remains 0.1.2. Do not bump/release 0.1.3 and do not sync Foundation/Math to this Operator surface until the prototype passes its real validation gates.

## Qiven-v2 immediate resume sequence

1. Execute the normal qiven-context cold boot, but include the live `jason-brother/operator-cli-observability` branch because main does not yet contain the rollover/process updates.
2. Read this handoff, `collaboration/operating-contract.md`, `state/current.md`, `state/active-work.yaml`, the open Operator obligation, and `projects/devkit/README.md`.
3. Verify live refs for qiven-context and qiven-devkit before acting.
4. Confirm Devkit Operator branch is still exact `ac816bb06fbe978c1b41a730104114e8f5778610` or report drift.
5. Obtain/reproduce the exact `tools\test.cmd` failure at that head. Do not make another speculative fix first.
6. Diagnose the root cause, make the smallest coherent repair, and issue a new exact head for local validation.
7. After Phase 1 is green, dogfood the generated Operator itself, then harden/version it as Devkit 0.1.3. Only after release validation should managed Operator files be synchronized into Foundation/Math in controlled repo-specific batches.

## Product / ecosystem context to retain

The broader Qiven direction remains: shared native engineering core first, then CAD -> semantic building/3D pipeline, industrial-gas management OS, and later robotics/simulation/native physics where justified. Foundation -> Math and Units independently; Geometry eventually consumes both. Do not create repos merely for conceptual neatness; split on real ownership/reuse boundaries. The current active engineering objective is Operator Phase 1, not a new product vertical.

## Interaction preference learned from Qiven-v1

The user wants the collaboration itself to become increasingly engineered: fewer manual copy/paste steps, fewer mouse-driven UI workflows, exact evidence, stable invariants, and reusable automation rather than repeated ad-hoc command composition. jason-brother should keep independent technical judgment and should surface broader/better engineering alternatives rather than staying trapped inside the user's initial tool framing.

## Conversation-length note

Qiven-v1 ended because the chat UI would no longer accept additional ordinary turns; the final user message was sent by editing the previous message. There is no reliable assistant-visible counter for “how many messages remain before this chat is forcibly terminated”. If asked in Qiven-v2, do not invent an exact remaining-turn count; explain that the product does not expose a trustworthy per-chat turns-remaining counter and use context size / responsiveness only as qualitative warning signals.
