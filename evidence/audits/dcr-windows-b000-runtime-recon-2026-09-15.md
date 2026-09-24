# Qiven DCR Windows Batch 000 — Runtime Reconnaissance — 2026-09-15

> **Redaction 2026-09-24** — public-repo information hygiene:
> machine-identity literals replaced with placeholders; originals
> remain in git history. Findings unchanged.

## Scope

This audit records read-only observations of the currently installed official Desktop Commander Remote client on JasonPC during Qiven DCR Windows Phase 0 / Batch 000. No credentials, auth tokens, SSH keys, host configuration, DCR package files, or Windows settings were modified.

Observed package:

- `@wonderwhy-er/desktop-commander` version `0.2.50`
- package cache root: `<user-profile>\AppData\Local\npm-cache\_npx\4b4c857f6efdfb61\node_modules\@wonderwhy-er\desktop-commander`
- package metadata declares `@modelcontextprotocol/sdk ^1.9.0` and `@supabase/supabase-js ^2.89.0`

## Process topology

The live owner-started path was observed in Windows session `1`, owned by `JASONPC\<os-username>`:

```text
interactive cmd.exe
  -> npx-cli.js @wonderwhy-er/desktop-commander@latest remote
     -> cmd.exe /c desktop-commander remote
        -> node.exe ...\desktop-commander\dist\index.js remote
           -> node.exe ...\desktop-commander\dist\index.js   # local MCP child
```

DCR-launched tool processes are children of the local MCP child. This confirms that the remote device process and local MCP server are distinct lifecycle boundaries.

## Remote entrypoint and persisted device state

`dist/npm-scripts/remote.js` constructs `MCPDevice` and starts it. Session persistence is enabled by default; `--no-persist-session` disables reuse. The device config path is derived from the user's home directory as:

```text
~/.desktop-commander-device/device.json
```

The audit did not read or record credential/token contents.

The default remote base URL in `device.js` is:

```text
https://mcp.desktopcommander.app
```

Startup fetches public Supabase connection metadata from `/api/mcp-info`, restores or authenticates a session, registers the device, subscribes its remote channel, publishes presence, and starts heartbeat maintenance.

## Local MCP bridge

`DesktopCommanderIntegration` launches the local MCP server over `StdioClientTransport`. The child environment is constructed as:

```text
{ ...getDefaultEnvironment(), ...config.env, DC_REMOTE_DEVICE: 'true' }
```

This is the exact boundary that previously omitted `ProgramData`, causing Windows OpenSSH 9.5 to exit `255`. The accepted Qiven DCR execution contract therefore still requires restoring `ProgramData=C:\ProgramData` for affected DCR-launched Git/SSH work until an upstream environment-propagation fix is proven.

The integration supervises local MCP disconnect/error events and attempts a controlled restart rather than assuming that a healthy remote channel proves the local MCP child is alive.

## Actual remote transport architecture

The current transport is not merely a raw application WebSocket carrying complete RPC messages.

`RemoteChannel` uses Supabase Auth + Supabase Realtime + database rows:

- private realtime channel name: `user:<user-id>`;
- device presence is keyed by device ID;
- remote calls arrive through a Realtime Broadcast `new_call` doorbell;
- the doorbell carries identifiers, while the device fetches the actual call row from `mcp_remote_calls`;
- call state is conditionally advanced from `pending` to `executing` in the database;
- completed/failed results are written back to the call row;
- a result doorbell is sent after the terminal row update, with server-side polling as recovery if that notification fails.

The device also retains a bounded in-process set of the most recent 100 call IDs to suppress duplicate delivery inside one process. The database claim supplies additional cross-process/restart observability. This exactly-once behavior must be treated as part of the V2 compatibility contract rather than as incidental implementation detail.

## Liveness and recovery behavior

Observed constants and logic in `remote-channel.js` include:

- broadcast-capable device `last_seen` heartbeat interval: 5 minutes;
- legacy/unflagged heartbeat interval: 15 seconds;
- channel joining wedge threshold: 30 seconds;
- confirmed Realtime heartbeat stale threshold: 75 seconds;
- channel recreate operation timeout: 45 seconds;
- transport capability withdrawal after 3 failed recreates;
- token refresh cadence: 45 minutes;
- reconnect uses jittered exponential backoff, rising from roughly 1–3 seconds toward roughly 15–45 seconds;
- unhealthy/half-open channels are explicitly destroyed and the underlying Realtime socket is disconnected before a fresh channel is created.

The implementation distinguishes cached channel state from proven socket liveness and explicitly detects a channel that still says `joined` after heartbeat proof has gone stale. This corroborates the Qiven rule that a control-plane `online` value alone is not sufficient liveness evidence.

## Logging / backpressure finding

A material V1 risk is directly visible in `device.js`.

For every incoming tool call, the current normal (non-debug) path logs the complete tool arguments:

```text
Received tool call <id>: <tool> JSON.stringify(tool_args) ...
```

After completion it logs the complete serialized tool result:

```text
Tool call <tool> completed: JSON.stringify(result)
```

These are ordinary `console.log` calls, not debug-only logging. Therefore a large tool result is duplicated into foreground console output even though the same result must also be persisted/transmitted through the remote-call path. There is no bounded human-display ring visible at this layer.

A one-time process snapshot during this audit showed the remote-server and local-MCP Node processes each around 100 MiB working set and the Windows Terminal process around 100 MiB. Those values are only a baseline and are **not** evidence of a leak. The architectural finding is independent of that snapshot: console output volume is currently proportional to full request/result payload size and has no product-level memory/display retention contract.

## Batch 000 architectural consequences

### V1 remains supervisor-first

The first Qiven implementation should supervise the official Node client rather than duplicate the complete Supabase/Auth/Realtime/database protocol immediately.

The native Windows supervisor must own:

- exact child process-tree lifetime;
- deterministic environment setup;
- pipe-based stdout/stderr capture rather than an unbounded interactive console dependency;
- bounded in-memory display buffers;
- explicit disk log rotation/retention;
- backpressure policy in which slow UI rendering cannot block transport/process execution;
- process and connection-health state exposed separately;
- graceful restart/stop and truthful terminal-state reporting.

UI history may be sampled/coalesced/dropped under overload if this is explicit and observable. Execution results and durable-log policy must not silently depend on UI consumption speed.

### V2 is a compatibility project, not a socket wrapper

A future native transport must reproduce or intentionally replace at least:

- session authentication and refresh;
- device registration and persisted identity semantics;
- Supabase Realtime private-channel authorization;
- presence publication and capability advertisement;
- broadcast doorbells;
- call-row fetch/state/result persistence;
- duplicate/exactly-once protections;
- result notification recovery;
- heartbeat, half-open detection, reconnect/backoff and capability withdrawal;
- clock-skew handling relevant to auth/session expiry.

V2 therefore remains deferred until these contracts are frozen and test fixtures exist.

## Next Batch 000 probes

The next reconnaissance should quantify output/backpressure behavior rather than assume it: drive controlled large-result calls through the official client, measure Node/terminal working-set and output behavior, and determine whether the official process itself buffers materially when stdout is redirected or drained at different rates. Those experiments should use synthetic bounded data and must not expose secrets or unrelated user files.
