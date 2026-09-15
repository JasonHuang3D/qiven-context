# Qiven DCR Windows Batch 000 — Output Retention Probe — 2026-09-15

## Scope

This audit records the second Batch 000 failure-model probe for the official `@wonderwhy-er/desktop-commander` 0.2.50 runtime on JasonPC. It focuses on local terminal-output retention and the resulting memory-growth boundary.

No live DCR process was intentionally driven to memory exhaustion. The high-output measurements were performed in an isolated Node harness that imported the same installed `TerminalManager` implementation. Synthetic output stayed inside that harness; only compact memory statistics were returned through DCR.

## Source-code findings

The installed `dist/terminal-manager.js` defines:

```text
MAX_BUFFERED_OUTPUT_CHARS = 50 * 1024 * 1024  // per session
MAX_LINE_CHARS            = 1 * 1024 * 1024
MAX_WAIT_OUTPUT_CHARS     = 2 * 1024 * 1024
```

The active-session line buffer evicts oldest lines once the per-session retained output exceeds approximately 50 MiB.

When a child process exits, the implementation copies the retained `outputLines` into `completedSessions`. It retains the last 100 completed sessions by count. A search of the installed implementation found no independent completed-session TTL and no smaller global retained-byte budget.

Therefore the local MCP has two materially different protection boundaries:

- the immediate wait/result buffer returned by `start_process` is bounded to roughly 2 MiB internally and observed around 1 MiB in the probe;
- completed process history can retain up to roughly 50 MiB for each of as many as 100 sessions by count.

The latter is a process-memory retention risk even when the model-facing result is small.

## Isolated retention probe

The harness loaded the official installed `TerminalManager`, launched synthetic child processes, and retained their completed-session history. It reported only memory statistics.

Observed process values:

| retained completed output | RSS | heap used | heap total |
| ---: | ---: | ---: | ---: |
| 0 MiB baseline | 119.7 MiB | 41.7 MiB | 78.5 MiB |
| 8 MiB | 136.0 MiB | 49.7 MiB | 86.5 MiB |
| 24 MiB cumulative | 158.5 MiB | 65.7 MiB | 102.7 MiB |
| 56 MiB cumulative | 208.2 MiB | 97.8 MiB | 134.7 MiB |
| about 105 MiB cumulative | 304.1 MiB | 161.9 MiB | 198.7 MiB |

The final child emitted 64 MiB, but the per-session retention cap reduced its retained contribution to about 50 MiB. The earlier completed sessions remained resident, producing about 105 MiB cumulative retained output.

The `start_process` wait result for each large-output child was only about 1 MiB. This confirms that model-facing output protection does not bound the MCP server's completed-session history.

These measurements demonstrate approximately monotonic resident-memory growth with retained completed output. They are not a claim that RSS equals retained-output bytes one-for-one; V8 allocation, duplicated strings, process runtime state and garbage-collection policy also contribute.

## Fresh-restart baseline

After the project owner restarted DCR, a new read-only process snapshot was taken through the fresh transport.

Observed Windows session-1 process working sets:

```text
npx wrapper              ~62.2 MiB
remote-device Node       ~99.6 MiB
local MCP Node           ~97.1 MiB
```

The local MCP and remote-device processes returned to roughly the same order of magnitude as the original reconnaissance baseline. A full DCR process restart is therefore an effective resource-reclamation boundary for in-process terminal history.

The isolated retention harness was a separate Node process, so its high-water allocation never contaminated the live DCR process. The fresh snapshot is used only as a restart/baseline observation, not as proof of a specific garbage-collection policy.

## Failure-model consequence

The primary large-output risk is not merely Windows Terminal scrollback. The official local MCP intentionally keeps bounded history per process session, but the aggregate completed-session history is count-bounded rather than byte-bounded.

A supervisor that only hides the console would therefore leave an internal retention path unresolved.

V1 must treat the official DCR process tree as a replaceable worker generation and use restart as a legitimate resource-reclamation action. Automatic restart must remain bounded and must not silently convert an in-flight operation into success.

Soft memory pressure should produce an observable `recycle_pending` state and wait for a conservative idle boundary. A hard host-protection threshold may terminate/restart the generation even if work is active, but that action must surface the affected call as interrupted/unavailable rather than completed.

## Logging consequence

The first reconnaissance already established that the remote-device process logs complete tool arguments and complete serialized results on normal console output. Combined with the terminal-manager retention behavior, V1 must separate four concerns:

1. protocol/result data;
2. child stdout/stderr draining;
3. bounded diagnostic log persistence;
4. bounded human-visible UI history.

None of the latter three may be allowed to become protocol authority or an unbounded backpressure path.

## Batch 000 design direction

The supervisor-first design remains preferred over immediately forking or replacing the official DCR client.

Initial V1 should keep the official package intact, monitor the exact process tree, drain output continuously, bound UI/disk queues, record memory pressure, and perform controlled process-generation recycle when necessary.

An upstream patch or maintained narrow fork that adds a completed-session TTL/global byte budget remains an option, but Batch 000 does not make a fork a prerequisite for the first stable Qiven transport milestone.

## Next acceptance work

Use a synthetic fake-DCR child under the future native supervisor to prove:

- slow or stopped UI rendering cannot block pipe draining;
- in-memory UI/log queues remain within configured byte budgets under continuous output;
- disk-log rotation cannot grow without bound;
- soft memory pressure becomes `recycle_pending` rather than an immediate destructive restart;
- hard memory pressure fails closed and returns truthful interruption state;
- restart creates a new process generation and does not accidentally terminate unrelated Node/CMD/PowerShell processes.