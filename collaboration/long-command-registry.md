# Long-Command Registry (canonical)

Registry of record for command classes that agent sessions must NOT run
raw in the session shell (hang-contract rule 5,
`collaboration/operating-contract.md`; implementing detector: the Devkit
tools `hook_exec_router.py` (v4) and its pinned self-test
`hook_exec_router_test.py`, both under the qiven-devkit tools directory;
usage reference: the qiven-devkit conventions document
`operator-usage.md`). Owner direction 2026-09-23: the list lives HERE
(canonical, owner-governed) and the devkit router implements it; every
operator task records a duration
(`.generated-temp/operator/task-durations.jsonl` + gate receipts) so
class membership is decided from measured evidence, not guesswork.

**ADR-0051 amendment (2026-09-24, ACCEPTED — owner H2 2026-09-24 in
v26):** the default reroute
for in-session long work is the harness's `run_in_background` (one
re-call, one completion notification, ZERO polling). exec-detour +
status-poll loops and foreground `sleep && tail` loops are retired
anti-patterns: every intermediate round-trip re-sends the live session
context, so polling supervision costs O(polls x context). The Qiven
Operator exec remains the sanctioned path for CUSTODY classes only
(sweeps, survival-requiring runs, owner kits, >10-min Bash-ceiling
work). Foreground oversized output is bounded natively by the harness
(>~25-30KB auto-persists to a file, ~2KB preview + path returned;
probed 2026-09-24 — no custom post-hook exists or is possible).

**v25 fresh-session probe results (2026-09-24T22:45-46Z, oblig
OBL-…-D5E6F7):** notification-once and the natural deny→re-call flow
PROVEN (P1/P5); TaskStop kills the whole process tree (P2); **the Bash
`timeout` parameter does NOT bind background tasks** (P3: 45s task ran
to natural completion under timeout=6000) — a background re-call is
bounded only by its command's own duration, TaskStop, and (unproven)
session end. Router v4.1 (2026-09-24, devkit PR #32): leading
`NAME=value` assignments no longer escape gate-class classification —
the taught guard re-call form now passes via the REAL guard check, and
an arbitrary env prefix can no longer bypass the class raw.
Router v4.2 (2026-09-26, F1A2B3 follow-up): the env assignment may also
precede the `python` launcher (`MSBUILDDISABLENODEREUSE=1 python
tools/qiven.py gate|run|ci ...` is the TAUGHT re-call form for
python-launcher invocations and previously escaped the class entirely,
so the guard check never fired for it). `qiven ci watch` (2026-09-26)
is a member of this class by the same pattern: raw foreground calls are
denied with the background+guard teaching, and the guarded background
re-call passes; the guard is class-mandated but semantically inert for
watch (it never builds), and backgrounding is the designed shape — the
watch is inherently terminating (internal budget) and observes a
REMOTE run, so it needs neither the session shell nor exec custody.

**v4.3 amendment (2026-09-26, owner direction — token economy): sweeps
split by INHERENT BOUNDEDNESS.** A sweep-class denial that pushes the
model into whole-file Reads pollutes the live context and compounds the
compaction-loss problem; the harness's native output bounding
(>~25-30KB auto-persists, ~2KB preview) means a backgrounded scan never
floods context at all. Three subclasses (router v4.3, devkit `c83091e`):

1. **git tracked-file walks — RAW.** `git grep`, `git ls-files` walk
   tracked files only: structurally unable to enter .venv/
   node_modules/third-party checkouts. Zero round-trips, zero context
   cost. (Previously `git grep -rn` matched the sweep class through its
   `-r` flag.)
2. **Repo-scoped sweeps — deny→background.** Recursive `grep`/`find`/
   `dir /s` whose explicit path arguments ALL stay strictly inside the
   workspace root (the hook process cwd) and name no heavy directory
   component ({`.venv`, `node_modules`, `.git`, `qiven-third-party-win`}
   — membership here). Seconds-class by construction; the re-call
   teaching carries the in-command bound (`--exclude-dir=…`) because
   the Bash `timeout` parameter does NOT bind background tasks (P3).
   Syntactic scope bounds the ENTRY POINT, not the subtree contents —
   **owner-accepted residual:** a repo-scoped background sweep orphaned
   by a pathological session death is possible and tolerable
   (read-only, seconds-class; worst case a short-lived orphan process).
3. **Unbounded sweeps — deny→exec (lease custody), unchanged.** No
   explicit in-scope path (walks cwd wholesale), path arguments
   escaping the workspace root, or naming a heavy tree. The
   OBL-D5E6F7 reframing stands for this class: operational session end
   kills nothing, so an unbounded background sweep can outlive the
   session (the 2026-09-23 ghost class).

## Classes

| Class | Verdict | Members (2026-09-26) | Evidence |
| --- | --- | --- | --- |
| builds/toolchains | deny→background + node-reuse guard | `cmake -S/-B/--preset/--build/--install`, `ctest`, `msbuild`, `devenv`, `cl.exe`, `link.exe`, `dotnet build/test` | gate/build durations (minutes); MSBuild node fanout = the 2026-09-23 leak class (ADR-0048 §3 guard required on the background path) |
| git tracked-file walks | raw allow (v4.3) | `git grep …`, `git ls-files …` | tracked files only — inherently bounded; the whole-file-Read fallback a sweep denial induced was the measured context-pollution path (owner 2026-09-26) |
| filesystem sweeps, repo-scoped | deny→background (v4.3) | `grep -r`/`--recursive`, `find`, `dir /s` with explicit path args strictly inside the workspace root, naming no heavy component | seconds-class by construction; bound rides the command (P3); owner-accepted orphan residual above |
| filesystem sweeps, unbounded | deny→exec (lease custody; background NOT sufficient) | the same commands with NO explicit in-scope path (cwd wholesale), paths escaping the workspace root, or naming a heavy tree ({`.venv`, `node_modules`, `.git`, third-party}); the Windows text-FILTER `find /i "text" file` stays raw | the 2026-09-23 ghost find.exe incident (raw workspace scan survived the session at 20%+ CPU); OBL-D5E6F7 reframing: session end kills nothing |
| repo gate tools | deny→background | `format_sources.py`, format entrypoints, pinned formatter, `test_all.py`, `pytest`, deploy scripts | the 2026-09-23 vendored-amalgamation format hang |
| network acquisition | deny→background | curl-class transfer tools + PowerShell equivalents, `pip install/download`, `npm install/ci/run build`, `git clone`, `git submodule update/sync`, `gh run watch` | the raw transfer slip during SQLite acquisition |
| qiven gate/run/ci | deny→background + node-reuse guard | any `qiven gate|run|ci` at a command position (exec/info/status stay raw) | gate wall time blocks the session shell (owner 2026-09-23); gates may build C++ (node fanout); per-task timers refine this class from durations data |
| git network (push/fetch/pull) | MEASURED (currently SUSPENDED) | probe first: push = ahead-count vs upstream (>25 commits → deny) + `push --dry-run` (5 s budget); fetch/pull = `fetch --dry-run` (fast AND changeless → allow, else deny); oversized denials instruct the background re-call | owner 2026-09-23: pre-judge the payload; deny messages carry the measurement |
| interactive | deny (no exec form) | editors, git interactive/patch modes, `cmake --open` | the 2026-09-19 modal incident |
| heredoc authoring | deny (absolute; checked FIRST; exec payloads included — exec never launders it) | `<<` / `<<-` + delimiter at a command boundary on the quote-stripped surface (quoted prose mentioning heredoc syntax is not authoring; known accepted false positive: letter-variable bit-shift — rewrite it) | owner 2026-09-23: the file-authoring law (MEM-D2A7F4) was violated again after cold boot; the hook enforces it mechanically (devkit 9fe34c1) |

Rules:

- Every hook denial is prefixed `[qiven-hook]` and states its evidence
  ("measured: 137 commits ahead") — a denial without provenance confuses
  the receiving agent (owner 2026-09-23: no ambiguous denials). Denials
  are TEACHING instructions: the v4 messages name the exact re-call
  form (`run_in_background: true`; `MSBUILDDISABLENODEREUSE=1` prefix
  for build/gate classes).
- **The deny → re-call loop is the sanctioned pattern (ADR-0051):**
  one denied call is the entire overhead; the backgrounded re-call
  returns an output-file path immediately and the harness notifies once
  on completion. The model does NOT poll, does NOT sleep+tail, does
  NOT detour through exec for in-session work.
- **Node-reuse guard (build/gate classes)**: the background re-call
  must carry `MSBUILDDISABLENODEREUSE=1` (env prefix; propagates
  cmake→msbuild) or `/nr:false` / `/nodeReuse:false` for direct msbuild
  calls. The router denies again until present (mechanical, not
  behavioral). exec v2 children are covered internally
  (qiven_operator.py injects the env).
- **Segment whitespace tolerance (2026-09-23, closed
  OBL-20260923T224500Z-A7B8C9):** segments following `&&`/`;`/`|` arrive
  with leading whitespace and are lstripped before classification —
  chained exec invocations classify by their actual command position.
- Probe budgets: 5 s per git probe; hook total stays well under the
  60 s hook timeout.
- Thresholds (push 25 commits) are defaults; the owner adjusts them
  here and the devkit test table pins the implementation.
- Membership changes: owner decision recorded here; devkit PR updates
  router + tests in the same batch; durations data proposes, the owner
  disposes.
- `git fetch`/`git pull`/`git push` are NOT blanket classes — they are
  measured (see above). `git clone` is unconditional background (nothing
  local to probe).
- **SUSPENDED (owner direction 2026-09-24, temporary):** git-network
  routing is disabled at the router (`GIT_NETWORK_ROUTING_ENABLED = False`,
  devkit branch `jason-extended-cognition/router-git-suspend`, commit
  3065018) — raw git push/fetch/pull pass unprobed. Trigger: the git
  credential path failed for every non-TTY git process (exec child AND
  raw session shell alike: GCM dialog auto-cancel + obsolete
  `manager-core` helper in global gitconfig). The credential config was
  same-day repaired (github.com scoped to the gh credential helper), but
  the suspension stays until the owner explicitly reinstates the measured
  judgment. The probe implementation and its tests are unchanged
  underneath the flag.
- Sweeps routed to exec (the unbounded subclass) run under exec v2
  bounded custody (devkit d1d2a3a, PR #27; runtime row rolled
  2026-09-24, runtime PR #58): the run's lease bounds the sweep's
  lifetime mechanically — the ghost-process class cannot recur through
  the sanctioned path. The v4.3 subclasses (git tracked-file walks raw;
  repo-scoped background) are implemented in devkit `c83091e` with the
  pinned self-test table; membership changes remain owner decisions
  recorded here, with the devkit router + tests updated in the same
  batch.
