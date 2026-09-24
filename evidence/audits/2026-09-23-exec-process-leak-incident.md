# Audit: 2026-09-23 post-session process leak (exec v1 custody gap)

Class: incident evidence (durable). Recorded 2026-09-23 by the v20
emergency-stabilization session (designation `jason-extended-cognition`,
long-running mode with delegated per-batch H2; owner direction: full
review of devkit tooling after the incident, architecture rebuild to
production grade, then governance records).

## Incident report (owner-observed)

After the v19 session (~90 minutes of continuous gate-driven work ending
2026-09-23 ~06:45 local / 2026-09-22 ~22:45 UTC):

- dozens of `msbuild.exe` and `cmd.exe` processes remained alive;
- one Git-for-Windows `find.exe` process kept working at >20% CPU
  ("ghost process", still scanning after the session was over);
- aggregate CPU stayed at ~70% after the session ended;
- exiting ZCode did NOT reclaim the processes;
- the machine had to be restarted to recover.

## Evidence

- Exec record stores (all records observed-to-completion by the v1
  operator, i.e. the primaries exited and were recorded `done`):
  - qiven-runtime: 139 records (2026-09-21: 1, 2026-09-22: 138) —
    dominated by `cmake` / `ctest` invocations (per-build Debug/Release
    gate cycles);
  - qiven-context: 17, qiven-devkit: 13, qiven-foundation: 5,
    qiven-math: 3.
- Code review of qiven-devkit `tools/qiven_operator.py` at `2cb1a35`
  (v1 exec): children spawned with creation flags only
  (`CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP |
  CREATE_BREAKAWAY_FROM_JOB`); NO Job Object anywhere; the only stop
  path an explicit `qiven exec stop` by an agent.
- Governing memory: MEM-20260923T212000Z-D4E5F6 (window discipline),
  MEM-20260921T114000Z-A3F8B5 (exec v1 design).

## Root cause analysis

Two independent leak channels:

1. **Unbounded descendant survival in exec/task execution (the
   architectural defect).**
   - `cmake --build` on the VS generator leaves MSBuild worker nodes
     alive after the build primary exits (node reuse `/nr:true`
     default). The operator observed the primary exit, recorded `done`,
     and the nodes leaked — invisible (hidden console), in no job,
     unbounded. One to several nodes per build × 138 exec runs in the
     window = the observed "dozens of msbuild processes".
   - v1 exec's "child continues past the operator timeout" had NO
     deadline: a run abandoned by a dead session lived forever.
   - `CREATE_BREAKAWAY_FROM_JOB` deliberately escaped any ancestor job,
     which is why exiting the IDE could not reclaim the processes.
2. **Raw shell tree sweeps were unclassified.** The ghost `find.exe`
   was a raw Git-Bash `find` over the workspace (multiple build trees,
   tens of thousands of files) invoked in a session shell call; the hook
   router's long-class table had no tree-sweep class, and the process
   survived session exit (observed).

The shared architectural flaw: process survival was implemented as an
UNBOUNDED property whose cleanup was BEHAVIORAL (the agent is expected
to call `exec stop`). Production custody must be MECHANICAL — the OS
bounds every tree's lifetime.

## Resolution (this batch)

- qiven-devkit PR #27 (merge `d1d2a3a`, batch commit `dd5843f`; design
  `docs/design/exec-custody.md`): exec v2 bounded process custody —
  per-run watchdog custodian holding a named `KILL_ON_JOB_CLOSE` Job
  Object it joins (custodian death = instant kernel tree-kill); hard
  lease `--max-lifetime` (default 3600 s, clamped [10, 86400]);
  completion reap of tree leftovers after a 1.5 s grace; per-task job
  custody for gate/run children (suspended-create → assign → resume);
  sweep piggybacked on every operator invocation; children spawn with
  `MSBUILDDISABLENODEREUSE=1` and never break away.
- Concurrency defects found and fixed during the rebuild (each now a
  named regression class): hand-rolled env blocks through raw
  `CreateProcessW` fail `WinError 87` (moved to `_winapi.CreateProcess`
  with dict env); fd numbers in `STARTUPINFO.hStd*` silently lose
  redirected output (osfhandle conversion); `bInheritHandles=TRUE`
  leaks the supervisor's stdio pipe into the child tree (a 1 s
  supervision budget blocked 13.8 s — own stdio de-inherited); atomic
  `os.replace` record rewrites collide with concurrent readers on
  Windows (writer+reader retry; a live watchdog must never crash on a
  transient collision).
- Hook router (same PR): segments lstripped before classification
  (closes OBL-20260923T224500Z-A7B8C9 — chained exec invocations);
  new long-class: filesystem tree sweeps (`find` path-argument forms,
  `grep -r/--recursive`, `dir /s`; the Windows text-filter `find /i
  "x" f` form stays raw).
- Validation: devkit gate:local PASS at exact head `dd5843f` (the gate
  itself executed through the new exec custody — dogfood); operator
  suite rewritten as 89 named checks including custody regression
  classes C1–C10, green on 4 consecutive runs (flake law); router table
  73 classification + 9 probe + provenance cases.
- Rollout: qiven-context consumes the operator via the ADR-0046 shim;
  its `devkit_pin` advanced to `d1d2a3a` (PR #120, merge `132b420`,
  gate:context-local PASS at exact head `2f15ad1`). Remaining sibling
  repositories carry their own snapshots and re-sync on their next
  touching batch (recorded obligation; their operators still show the
  v1 leak class if used intensively without exec v2).
- Standards: `docs/engineering/python-standard.md` (Devkit-canonical
  Python law; incident-derived) added; `operator-usage.md` exec section
  rewritten for custody semantics.

## Follow-ups recorded elsewhere

- ADR-0048 (proposed, this transaction): adopt the bounded-custody
  architecture as the law for any Qiven tool that spawns processes.
- OBL for sibling snapshot rollouts (qiven-runtime, qiven-foundation,
  qiven-math, qiven-toolchain-win, qiven-third-party-win).
- The workspace hook (`.zcode/config.json`) is currently owner-disabled;
  re-enabling it is an owner action (this session must not silently
  re-arm the owner's IDE configuration).
