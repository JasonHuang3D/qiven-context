# Qiven-v19 Session Checkpoint

> **MUSEUMED (2026-09-23, owner direction):** this file records TURNS
> of the **v17 session** (same conversation thread), not a real
> session. Its content is CONSOLIDATED into
> `sessions/2026-09-22-qiven-v17.md` (turns 2-5); this copy is sealed
> historical evidence only. Renamed `*-turn-file.md` so the number is
> not mistaken for a real session ordinal. Session/turn law:
> `collaboration/context-checkpoint.md`.

## Session identity

Continuation session (v18 thread, 2026-09-23) under the owner-granted
designation `jason-extended-cognition`; long-running mode re-affirmed
("委托你H2"). Live-model report unchanged from v18: GLM-5.3
(`bigmodel-offpeak-idle-plan`); variant/reasoning not introspectable.

## Exact current task

Owner review of the v18 deliverables — two items, both complete:

1. **Hook audit/cleanup + router rigor** (devkit PR #24):
   - `D:\JasonWork\.zcode\config.json` cleaned: the three DISABLED
     adapter-bridge H1 experiment entries (SessionStart/PreToolUse/
     PostToolUse, pointing at a build artifact with hardcoded
     session/action ids) removed; the permanent PreToolUse Bash →
     hook_exec_router.py entry kept. H1 history remains canonical in
     the RCA-14 audit file; live config carries no experiment residue.
   - Router v2 (47-case pinned self-test, gate task `router-tests`):
     added the format class (the sqlite3.c format hang), the network
     transfer class (a raw curl slip had passed v1), repo-clone/
     submodule, run-watch, deploy entrypoints; a separate INTERACTIVE
     verdict (editors, git patch modes, the GUI launcher — the
     2026-09-19 modal-incident class); the operator-mediated bypass
     tightened to command positions (`echo tools/qiven && cmake...`
     can no longer bypass). Live-verified: raw format and raw transfer
     commands now deny with guidance. operator-usage.md documents the
     class table + the observation boundary (git fetch/pull/push stay
     raw until a slow-remote incident).
   - Working note: the router's text scan also denies session commands
     whose PROSE mentions those tools (PR bodies, doc text) — authoring
     moved to file-based bodies/Edit; the router's job is correct.
2. **Third-party v2: workspace singleton** (devkit PR #24; NEW repo
   qiven-third-party-win main `3184538`; runtime PR #40 main `3192991`):
   - Standard v2: third-party code lives ONLY in the singleton
     (`qiven-third-party-win`, sibling, `-win` mirrors toolchain-win);
     per-repo third_party/ FORBIDDEN (runtime's v1 dir migrated).
     Classes normalized: S source-compiled (real target + scoped flag
     law), P prebuilt (IMPORTED GLOBAL + per-config locations +
     explicit config mapping — a CMakeLists is REQUIRED so Debug/
     Release link correctly), H header-only (INTERFACE), F
     fetched-once (acquisition into the singleton via the operator;
     consumer configure stays offline; FetchContent at consumers
     forbidden).
   - Consumption law: QIVEN_THIRD_PARTY_ROOT (env → sibling → fail) +
     exact-SHA consumer pin validated at configure (draft-pin
     discipline; runtime pins `3184538`) + optional spot-verification
     (runtime's gate verifies singleton pin + all digests).
   - cross-repo-cmake.md conventions: the ONE pattern for any target
     outside the consuming repo (resolution, pins, build placement, VS
     EXCLUDE_FROM_ALL pitfall, IMPORTED per-config law), forbidden
     list, live external registry. Section 8 of the standard answers
     the owner's "foundation as third-party" question honestly:
     sibling-source consumption is valid for CO-DEVELOPED first-party
     layers, wrong for third-party; foundation lacks a SHA pin today —
     recorded gap with a revisit trigger.
   - Migration found and fixed a real defect (singleton fix commit):
     package include dir must point at src/ (the lib compiled via
     quoted includes while consumers including <sqlite3.h> failed
     C1083 — caught by the consumer gate).
   - Deployment closed the loop: bundle 0.1.0-g3192991 rebuilt with
     sqlite3-LICENSE sourced from the singleton (40 files, smoke exit
     0, deploy-log appended); deploy_bundle.py + deployment.md synced.
   - New repo registered in state/repositories.yaml (workspace-third-
     party-singleton); singleton carries its own gate (provenance
     verify + configure smoke) and minimal self-contained tooling
     (operator adoption deferred, trigger recorded in its README).

SESSION CLOSED 2026-09-23 at task completion. MVP-1 remains owner-paced
and NOT started.

## Accepted refs and evidence

- devkit PR #24 merged, main `b9ee90ec`; gate local PASS (incl.
  router-tests, 47 cases).
- qiven-third-party-win main `318453834315a68fa85374dffa9a77ff73d6e71c`
  (initial `ef7be85d` + include-dir fix): singleton gate PASS
  (1 package, 5 digests, configure smoke).
- runtime PR #40 merged, main `31929918`; full gate PASS at branch
  head (singleton pin verified, 27/27 both configs); bundle
  `0.1.0-g31929918` validated with singleton-sourced licenses.
- Delegated-H2 receipts: PRs #24/#40 bodies. ADR acceptance: none this
  session (no ADR lifecycle events).

## Unaccepted candidate refs

- None open.

## Pending asynchronous work

- None.

## Known inconsistencies and evidence gaps

- Creating the qiven-third-party-win GitHub repository was executed
  under the delegated engineering H2 of this session (the owner's
  redesign direction required a singleton home). If the owner prefers
  a different repo identity/name, migration is mechanical (rename +
  registry + pins).
- The singleton's own tooling is minimal (verify + configure smoke);
  Devkit operator adoption deferred until it carries compiled code
  with tests or deploy receipts (trigger recorded in its README).
- git fetch/pull/push remain outside the router's long class by
  observation; first slow-remote incident moves them in (documented).
- Standing: draft template syncs need manual managed patches;
  Qiven-v2 through Qiven-v5 session records remain missing — Do not synthesize them.
  ContextView<ChatGPT, Jason> remains operational for ChatGPT sessions.

## Next action

Fresh session cold boot per BOOTSTRAP.md (context main >= v19 close;
runtime `31929918`; devkit `b9ee90ec`; singleton `3184538` registered
in repositories.yaml). MVP-1 remains the owner's call: when directed,
it begins with a journal design section under qiven-runtime
docs/design/ (design-first law), consuming the singleton's SQLite.
Nothing else is owed by any party.
