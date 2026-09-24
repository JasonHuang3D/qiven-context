# MVP-4 H1 Kit Incident — deny-118 total blockade (2026-09-23)

> **Redaction 2026-09-24** — public-repo information hygiene
> (`collaboration/public-repo-information-hygiene.md`): machine-identity
> literals are replaced with placeholders; originals remain in git
> history. Technical findings are unchanged.

## Report

Owner direction (2026-09-23, v21 session, verbatim summary): the MVP-4
H1 kit instructed the owner to hand-configure the workspace hooks; after
starting a fresh session, EVERY tool call returned
`[qiven] deny 118: hook payload oversize or unreadable (digest
unavailable)`. The owner disabled all hooks as the emergency stop and
returned to the session with the fix demands recorded here.

## Root cause

`extract_zcode_event` (MVP-4, PR #50) REQUIRED a session-identity
payload field (`session_id`/`sessionId`). The REAL ZCode hook payload
carries no such field:

- RCA-14 H1 evidence (`evidence/audits/rca14-real-adapter-h1-2026-09-22.md`)
  already recorded "no stable event id" as a day-one limitation;
- the live devkit exec router (parsing the same payloads all session)
  uses ONLY `tool_input.command`.

The extractor's assumed field names were never verified against a real
payload before the kit deployed them into the owner's live session.
Fail-closed then correctly denied everything — the failure mode worked
as designed; the DEFECT was shipping an unverified assumption as a
REQUIRED field.

Contributing defects (owner-identified):

1. The H1 kit was a prose document telling the owner to author config
   fragments and run inline commands — not a package. H1 semantically
   means a complete, tool-built, rollback-able package the owner's
   hands execute (deploy-like, through the H1 path).
2. The kit's inline commands were not shell-correct for the owner's
   actual environment (`cd <workspace-root>\qiven-runtime` fails in Git
   Bash, the ZCode session shell).
3. The RuntimeHost console produced no visible boot/serve output while
   writing `.qiven/` state — the human-facing output law was not applied
   to the owner-facing binary.

## Resolution (all landed 2026-09-23, v21 session)

- qiven-runtime PR #51 `62fe0ae` (batch head `e0614b8`, gate:local PASS
  27.8 s): no payload field required — identity (event/tool/session
  handle) comes from the trusted registration template (`--event/
  --tool/--session-handle` pinned per matcher entry); payload fields are
  corroborating evidence (contradiction denies); `--dump-stdin` payload
  probe; human-facing host output (staged boot with every durable path,
  per-connection lines, 30 s heartbeat); `tools/h1_kit.py` (deploy-grade
  kit packager); deny-118 regression case in `hook_conformance`.
- qiven-devkit PR #28 `b935926`: the H1 kit standard
  (`docs/engineering/h1-kit.md`) — executable acceptance packages law.
- ADR-0049 PROPOSED (this transaction): the workspace law codifying both.
- The workspace hook config was written DIRECTLY by the session
  (`<workspace-root>\.zcode\config.json`, owner instruction; the ZCode UI
  review is the enable gate). The generated kit sits at
  `<workspace-root>\h1-kits\qiven-runtime\mvp4-h1\0.1.0-ge0614b82\`.

## Lesson (recorded as MEM-20260923T115500Z-A1B2C3)

Assumptions about external contracts must never ship as REQUIRED fields
in an owner-live path; H1 kits are packages built by tools, not prose;
owner-facing commands are shell-labeled and shell-correct; owner-facing
binaries obey the human-facing output law.

## Trial 2 addendum (2026-09-23T12:45Z, same day)

The owner re-ran the regenerated kit; the FIRST Write denied 118 again.
The kit's --dump-stdin probe (mandated by this incident's fixes) captured
the payload: raw heap pointers (0x7FF8... residue), not JSON. SECOND,
independent root cause: zcode_hook_main assigned the temporary vector
from read_stdin_verbatim() to HookRun's SPAN member - the temporary died
at the semicolon, the span dangled into freed heap, and the extractor
read garbage. Fixed structurally in runtime PR #52 (787b664; batch head
db7972c, gate:local PASS 28.5 s): HookRun OWNS the payload bytes. Also
landed per owner direction: deny-source tagging (hook-client/no host
verdict vs host verdict - a client-side deny correctly never reaches the
host console) and ASCII-only owner-facing console output (the cp936
console mojibake'd UTF-8 em-dashes in the owner's host-console paste).
Kit regenerated at h1-kits/qiven-runtime/mvp4-h1/0.1.0-gdb7972c1.

Lesson folded into the record: the probe paid for itself exactly as
designed - the real bytes were in hand minutes after the report, no
guessing. Two coexisting bugs produced one symptom; the first fix was
correct but not sufficient.
