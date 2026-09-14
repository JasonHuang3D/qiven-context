# Chat-mode invocation and execution-runtime research — 2026-09-15

## Purpose

Identify a reliable way for Qiven cognition to execute the canonical local `qiven-context` runtime while preserving the user's normal ChatGPT Chat experience on the current Plus plan. The investigation deliberately separated invocation reliability, tool availability, execution transport, network latency, and retrieval correctness instead of treating "MCP exists" as proof that the whole path is reliable.

## Invocation experiments

### Automatic Skill routing

A diagnostic Skill named `qiven invocation probe` was created. Normal Qiven discussion without explicit Skill selection did not reliably invoke it. Explicit `@qiven invocation probe` did invoke it, while the next turn without `@` did not remain sticky.

Conclusion: automatic Skill routing is not a safety boundary. Phase 1 requires explicit per-turn `@qiven` invocation.

### Skill to GitHub live-read preflight

The Skill was required to live-read `probes/skill-preflight-v1.txt` through the connected GitHub app and echo an unknown nonce.

Observed sequence:

1. first explicit invocation returned the current nonce;
2. the nonce was rotated only in GitHub, without changing the Skill;
3. a fresh Chat returned the new nonce;
4. the `nonce=` line was then removed and the Skill returned `[QIVEN_PREFLIGHT_FAILED]` without continuing with Qiven history claims;
5. after restoring a new nonce, five serial fresh-Chat runs all passed;
6. a three-way concurrent run produced two passes and one failure where the Qiven/GitHub capability was not exposed to that Chat.

Conclusion: explicit Skill invocation and fail-closed behavior are viable, but concurrent/per-chat app exposure is not accepted as reliable. GitHub also remains repository I/O rather than an execution runtime.

## Product-surface experiments

### Private/custom Plugin or MCP

The current Plus surface can use published plugins/apps but does not provide the private self-import/custom-MCP workflow needed to make Qiven's own local runtime a first-class private app. Building a Qiven Plugin therefore does not solve the immediate Phase 1 problem for this account.

### WebMCP / Site Tools

A local WebMCP page registered a `hello_qiven` site tool. In the ChatGPT Desktop built-in browser the WebMCP API was available, the tool registered, and ChatGPT successfully called it with a fresh page-session nonce. However the usable surface was ChatGPT Work rather than normal Chat.

Conclusion: WebMCP is a valid future/Work adapter but is not the primary Chat-mode Qiven transport.

### Remote Desktop Commander

The published Remote Desktop Commander plugin was installed and a Remote MCP tunnel connected to `JasonPC`. In normal Chat mode it successfully executed:

- `cmd.exe /d /s /c "echo QIVEN_RUNTIME_OK"` -> stdout `QIVEN_RUNTIME_OK`, exit code `0`;
- `git rev-parse --show-toplevel` inside `D:\JasonWork\qiven-context` -> `D:/JasonWork/qiven-context`.

This establishes a practical Plus-compatible execution boundary from ChatGPT Chat to the authorized local Windows machine.

## Network and latency diagnosis

An initial npm failure was traced to stale user-level `.npmrc` entries pointing at the retired Shadowsocks proxy `127.0.0.1:1080`. The worker changed only npm's user proxy settings to the current Clash Verge mixed endpoint `http://127.0.0.1:7897`; npm/npx and Desktop Commander startup then passed.

A later layered latency investigation found:

- Node `v22.11.0`, npm `10.9.0`, Desktop Commander `0.2.50`;
- runtime path: Desktop Commander -> `127.0.0.1:7897` -> Clash/Mihomo -> selected Singapore node -> `mcp.desktopcommander.app:443`;
- proxied target HTTP median about `0.4045 s`, p95 about `1.1112 s`;
- direct HTTP median about `0.7764 s`, so direct was not preferable;
- local `echo` command median about `16 ms` and complete local task about `0.481 s`;
- one complete Remote tool call observed around `21.3 s`;
- Desktop Commander uses a persistent Supabase Realtime WebSocket/WSS path with heartbeat/recovery logic;
- no reconnect, stale-heartbeat, subscription-timeout, or channel-recreation event was captured during the measurement.

Conclusion: current Node, DNS, local execution, and selected Clash node do not explain the dominant tens-of-seconds latency. The primary overhead is in the remote relay / ChatGPT connector orchestration / result-return path. Remote Desktop Commander is usable but must be treated as a high-latency transport.

## Architecture implications

Phase 1 should use:

```text
ChatGPT Chat
  -> explicit @qiven Skill
  -> one coarse-grained Remote Desktop Commander call
  -> JasonPC local qiven-context runtime
  -> one machine-readable result containing Context Pack + Context Lease
  -> reasoning
```

The transport must not expose qiven-context as a chatty sequence of remote filesystem and subprocess calls. Internal retrieval, ranking, obligations, provenance, and lease creation must happen locally behind one stable command such as `qiven.context.prepare(...)`.

Until separately measured, concurrent Qiven runtime turns are not accepted. A failed or unavailable preflight must fail closed rather than fall back to model-native memory, stale chat context, or GitHub guesses.

## Local/remote source state discovered during the runtime probe

The authorized JasonPC clone was clean on `jason-brother/retrieval-reliability-phase1` at `6a78188db1dc751bf42f68dea730a494f80d6201`, while the remote experimental branch had advanced to `f86399ca415a631815d3007ae4d21c7d0b346295` through GitHub-side probe commits. A fetch from the Remote Desktop Commander process context failed against the SSH origin even though GitHub CLI authentication existed.

This discrepancy does not invalidate the execution-transport probe, but production Context Lease acceptance must not proceed until the local runtime source is intentionally synchronized to the accepted Qiven Context head.

## Next acceptance step

1. explicit `@qiven` must invoke Remote Desktop Commander in normal Chat;
2. Remote Desktop Commander must execute one local read-only preflight command on JasonPC;
3. the command must return a fresh nonce, exact local Git ref, branch, and clean-source state;
4. Skill must fail closed if that result is absent or invalid;
5. after this chain is stable, replace the diagnostic probe with the canonical `qiven.context.prepare(query, previous_lease?)` entry point and return Context Pack + Context Lease in one tool result.
