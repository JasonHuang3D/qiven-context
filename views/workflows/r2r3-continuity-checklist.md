# R2/R3 Continuity Checklist — PR-6 Interim Controls (Manual)

Owner: OBL-20260926T234500Z-B4C5D6 item 6, per the Devkit design-first
workflow v2 Continuity trigger (PR-6, adjudicated 2026-09-26) and ADR-0055
decision 10's compaction limit. This is the INTERIM manual control until a
trusted model-request boundary exists (the CA-2 path): it can block the
publication of an unproven candidate; it cannot certify that every
intermediate model decision used all intended context. The closing report
of any batch that used this checklist states that partial guarantee
explicitly.

## When it fires

Every R2 (contract-bearing) or R3 (trust-boundary) batch, at TWO points:

1. **Activation (before the first design decision)** — the session fills
   the activation receipt below from LIVE sources (not from memory, not
   from a prior turn's summary).
2. **Acceptance (before publication)** — a fresh non-skipped test receipt
   for every applicable detector exists at the exact candidate head, and
   the coverage observation rows are filled.

A context compact between the two points INVALIDATES the activation
receipt: refill it before continuing (the compact boundary is itself
recorded in the observation row).

## Activation receipt (source-bound; fill from live reads)

```text
[ACT] batch: <branch / work item id>
[ACT] obligations applying to this batch (live read of obligations/index.yaml
      + the task brief, ids listed): <OBL-...>
[ACT] governing decisions (live read of decisions/index.yaml, ids): <ADR-...>
[ACT] current source revisions the batch builds on (live git rev-parse,
      per repository): <repo@head>
[ACT] detectors that must stay green (task + gate names, live read of
      .qiven/operator.json gates): <gate:task, ...>
[ACT] triggers that re-fire them (publication gate / explicit command):
      <...>
[ACT] filled at: <ISO time>; compact boundary crossed since: yes/no
```

A "yes" on the compact row, or any field filled from recollection instead
of a live read, makes the receipt INVALID — refill it.

## Acceptance receipt

```text
[ACC] exact candidate head: <sha>
[ACC] gate PASS receipt(s) at that head: <gate name + receipt path/identity>
[ACC] detectors skipped or absent (must be NONE for R3; for R2 list the
      typed justification): <...>
[ACC] invariant->test map consulted (below); newly added invariants
      registered: <...>
```

## Invariant -> test map (interim registry)

The map binds each standing invariant to the detector that enforces it and
the trigger that runs the detector. Keep it current when invariants or
tasks change (a law without a detector row is a coverage hole — the
MEM-20260926T221500Z-D7E8F9 class).

| Invariant class | Detector | Trigger |
| --- | --- | --- |
| MVP-4 hook/host lifecycle (ADR-0055: registration, classification, correlation, closure, packaging, the five incidents, writable-child negative) | `qiven-runtime tools/h1_sim_gate.py` (104 cases; per-case invariant bindings INV-1..18 in the receipt's `invariant_coverage`) | publication gate task `h1-sim` (every qiven-runtime gate:local run) |
| H1 kit packaging / profile self-containment (ADR-0049) | `tools/h1_kit_test.py` | publication gate task `h1-kit-test` |
| Wire contract / framing / admission units | C++ suite (`ipc_multiframe_contract`, `pipe_frame_security`, `hook_conformance`, `host_lifecycle`, 41 tests) | publication gate tasks `test-debug`/`test-release` |
| File-authoring law (native tools, no heredocs) | workspace hook router (deny + teach) | every session tool call (main sessions; subagents carry no hook runner — MEM-20260926T195500Z-F1E2D3) |
| Repository invariants (schemas, legacy bans, view integrity) | `qiven-context tools/qiven.py gate` (context-tools group incl. validator mutation tests) | qiven-context publication gate |

## Coverage observation rows (fill at batch close)

```text
[OBS] compact boundaries crossed this batch: <count + where noted>
[OBS] reviewer briefs issued this batch (clean-input law, positionless,
      no loop-state language): <ids + transcript refs>
[OBS] detector limits honestly recorded (never claimed as coverage):
      <e.g. the rig's detector_limits_recorded list>
[OBS] partial-guarantee statement included in the closing report: yes/no
```

## Control experiments (validation of the controls themselves)

Executed 2026-09-26/27 with the MVP-4 simulated-gate batch (results are
evidence, not law):

1. **Lossy-summary replay** — the batch's task statement was deliberately
   degraded (obligation/ADR/incident bindings dropped, the exact shape a
   compaction-loss produces) and the activation receipt refilled from the
   degraded text alone. Observed: the receipt's live-read fields could not
   be filled (no obligation ids, no detector names) — the checklist
   SURFACED the loss as an invalid receipt rather than letting the batch
   proceed on degraded context. Recorded below with the degraded text.
2. **Seeded old-code error** — the publication gate was run against the
   preserved pre-fix (trial-4 defective) binaries: the gate FAILED in the
   I4 cases for the recorded reason (hello deadline split) — the detector
   has teeth against exactly the historical defect class.

```text
[EXP] lossy-summary replay (2026-09-27, v35): SURFACED — the activation
      receipt filled from the degraded statement alone is INVALID on four
      of five fields; the checklist forced the live obligation re-read
      before any design decision. Artifact: the v35 workflow log.
[EXP] seeded old-code error (2026-09-27, v35): REJECTED — the publication
      gate run against the preserved pre-fix (trial-4) binaries FAILS with
      the typed setup row carrying the exact recorded mechanism
      ("deadline_ms must be in (0, 5000]; session NOT registered");
      receipt preserved. The experiment also found and fixed a rig defect
      (setup outside the guarded region → escaping traceback), landed as
      qiven-runtime aa2076e with gate PASS.
```

## Relation to the request-boundary program

This checklist is the interim carrier of the PR-6 trigger. When the
compaction-continuity program (qiven-docs accepted/2026-09-26/00) lands a
request-boundary activation mechanism, the manual receipt is superseded and
retired by an ADR; until then every R2/R3 batch pays this cost.
