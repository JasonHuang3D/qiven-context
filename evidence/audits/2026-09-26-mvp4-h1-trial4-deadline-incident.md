# MVP-4 H1 Trial 4 — all-deny-114 root cause (owner-directed diagnosis, 2026-09-26)

Owner ran the real H1 with kit `0.1.0-g7b3ce515` (2026-09-26 05:19-05:26
+0800). Symptom: every probe denied, codes "not right". Diagnosis this
session (v31, turn 5): reproduced byte-for-byte in a scratch root and
root-caused to a one-line protocol contract split.

## What the owner actually saw

Every probe — including P4, which must be ALLOWED — returned:

`[qiven-hook] deny 114 (host verdict): no registered runtime session for
this harness session (SessionStart must fire first)`

## Root cause chain (verified by reproduction + source)

1. Client (`apps/zcode_hook_main.cpp:103`): the session_start event
   carries a refresh-grade deadline of **9750 ms** (MVP-4 H-2: 10000 −
   250 margin); all other events 4750.
2. The client writes the event's deadline into the **hello frame** too
   (`src/adapter/zcode_hook.cpp:97`).
3. Host (`src/ipc/protocol.cpp:112-124`): deadline ceilings are
   per-request-kind — only `HookEvent+session_start` gets 10000; every
   other frame, **including hello**, is capped at 5000.
4. So the session_start connection's hello (9750) is rejected:
   "deadline_ms must be in (0, 5000]". The client reports this as an
   **advisory note** (exit 0, "session NOT registered") — invisible to
   the owner as a failure.
5. The session never registers (journal: sessions=0, zero
   session_registered events). Every subsequent pre_tool (hello 4750 —
   legal) reaches the host and hits the unknown-session gate → uniform
   deny 114, which fires BEFORE any scope/not_governed classification
   — hence P4 (outside scope, must allow) is denied too.

Same wire-contract class as MEM-20260924T032000Z-C1D2E3 (a contract
without an end-to-end test collapses failures into one undifferentiated
denial): the ceiling policy lives in one code path, the budget choice
in another file, and no test ever sent a refresh-grade deadline inside a
hello frame.

## Why preflight did not catch it

The kit preflight exercises ONLY a pre_tool round trip (deadline 4750 —
legal). It never drives the session_start registration path, so this
defect class is invisible to it. (Its "real pipe round trip" PASS is
also compatible with a deny-114 answer — any host verdict passes.)

## Evidence

- Owner trial: `h1-kits/qiven-runtime/mvp4-h1/0.1.0-g7b3ce515/evidence`
  (payload dump = inbound events only; journal-audit = lifecycle rows
  only; real journal `qiven-context/.qiven/runtime/journal.sqlite3`:
  34 lifecycle events, sessions=0, transactions=0).
- Reproduction (scratch root, verbatim payloads, paths rewritten):
  `.generated-temp/f1a2b3-experiments/h1-repro/` — S0 session_start
  handshake rejected (deadline text), P1-P4 all deny 114, journal
  isomorphic to the real trial. Script: `h1_repro.py` (same directory).

## Consequences recorded (owner directions, same turn)

1. The one-line fix (client hello deadline ≤ 5000, or host hello ceiling
   10000) + preflight session_start coverage + conformance
   hello-with-refresh-deadline case are FOLDED INTO the corrective work
   below — not landed as an isolated patch (owner direction: stop
   patching symptoms session by session).
2. **Owner direction (2026-09-26): the owner-live GUI H1 trial is
   RETIRED as the MVP-4 acceptance vehicle** (four trials, four
   infrastructure failures, each costing a day). The acceptance is
   replaced by a deterministic simulated full-loop rig (real ZCode CLI
   + mock LLM provider + real host + real hook binary + scripted
   scenarios). See the v31 checkpoint turn-5 program and
   OBL-20260926T234500Z-B4C5D6.
3. **Owner direction (2026-09-26): the "land first, revisit later"
   semantics is REVOKED for qiven C++** — Foundation must own the
   primitives every downstream consumer needs (first: a typed,
   canonicalized path value) before downstream feature work proceeds;
   ADR drafting is the next session's first transaction.
