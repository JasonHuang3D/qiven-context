# Qiven-v3 Cold-Boot Checkpoint

Closed at 2026-09-15 after Chat-mode local runtime transport validation.

## Purpose

This checkpoint preserves the end state of the Qiven Context invocation/runtime research so a fresh Chat can resume without reconstructing the work from model-native memory.

## Collaboration contract

- User is project owner / PM / local validation operator.
- `jason-brother` is CTO / architect / reviewer / decision partner.
- `jason-worker` is the separate local execution agent.
- Default product mode is Chat, not Work.
- Windows CMD is the normal human shell.
- Never modify `git user.name` or `git user.email`.

## Current qiven-context branch

Working branch:

`jason-brother/context-runtime-transport`

Before this checkpoint commit, exact head was:

`94e4836f75d69a595af60ac897d4a76d4628647d`

Resolve the live branch head before acting because this checkpoint commit advances it.

## Invocation research outcome

The tested Phase 1 Chat-mode topology is:

```text
ChatGPT Chat
  -> explicit @qiven Skill
  -> Remote Desktop Commander
  -> authorized JasonPC
  -> local qiven-context runtime
  -> Context Pack + Context Lease
  -> ChatGPT reasoning
```

Important accepted boundaries:

- Automatic Skill routing is not trusted.
- Explicit `@qiven` is required on each Qiven cognition turn in Phase 1.
- Skill activation by itself is insufficient; a fresh local runtime call is required.
- Fail closed if Remote Desktop Commander, JasonPC, local runtime execution, source cleanliness, or lease validation fails.
- Do not fall back to ChatGPT Memory, prior chat, GitHub, or web to simulate a successful cognition preflight.
- Concurrent Qiven turns remain unaccepted; use one active Qiven cognition turn at a time.
- Remote transport is high-latency, so production cognition must be coarse-grained: one remote call should perform the full local prepare operation rather than many chatty filesystem/process calls.

## Alternatives tested and rejected for the Chat-mode primary path

- Automatic Skill invocation: unreliable.
- GitHub mailbox/RPC: rejected as unnecessarily indirect and latency-sensitive.
- Custom MCP / private custom Plugin: not available as the practical Plus path tested here.
- WebMCP / Site Tools: local hello-world worked, but ordinary Chat cannot use it; it is a Work/future adapter rather than the current Chat-mode path.
- Skill-bundled scripts: not selected as canonical runtime because Qiven must keep one local implementation rather than duplicate runtime logic into the Skill package.

## Remote Desktop Commander result

Remote Desktop Commander is installed and connected to `JasonPC`.

Ordinary Chat successfully executed local commands and accessed:

`D:\JasonWork\qiven-context`

Network diagnosis found:

- Node `v22.11.0`, npm `10.9.0`, Desktop Commander `0.2.50`.
- Runtime path uses Clash mixed proxy `127.0.0.1:7897` through the current selected node.
- Local command execution is millisecond-scale; target HTTP baseline is sub-second to about one second.
- A full Remote MCP call may take about twenty seconds or more, so relay / connector orchestration dominates latency.
- No evidence justified changing Node, DNS, Clash node, or system networking.

## Local invocation probes

A diagnostic local probe exists outside the repository:

`D:\JasonWork\qiven-local-preflight-probe.py`

It proved:

`@qiven -> Skill -> Remote Desktop Commander -> JasonPC -> local Python -> fresh nonce`

The user validated a fresh result:

`[QIVEN_LOCAL_PREFLIGHT_OK:E166B1BDFA4548F9A767131CDFC0F358]`

with clean source and exit code 0.

A second local probe exists outside the repository:

`D:\JasonWork\qiven-full-preflight-probe.py`

It calls the canonical local `prepare_context()` path and emits one compact JSON result containing a real Context Lease plus selected record IDs.

Local direct execution successfully produced:

- `marker = QIVEN_CONTEXT_PREPARE_OK`
- `source_clean = true`
- a fresh `CTX-...` lease
- `ADR-0022`
- `ADR-0023`
- `OBL-20260914T183608Z-4D61B8`
- empty diagnostics

The user then validated the same chain from a fresh Chat through Skill v3 and Remote Desktop Commander:

`[QIVEN_CONTEXT_PREPARE_OK:CTX-5D5D4456A48C4AE3]`

with `diagnostics` empty.

Treat Invocation Reliability + local Execution Runtime + real Context Lease issuance as functionally established for the Phase 1 explicit-@qiven path. The Skill response did not echo every presentation field requested by the diagnostic contract, but that is a presentation-level follow-up, not a failure of the execution chain.

## Canonical records created from this research

- `ADR-0023` — use explicit `@qiven` plus Remote Desktop Commander as the Phase 1 Chat-mode execution transport.
- `MEM-20260914T183608Z-7C9E42` — remote cognition transport must be coarse-grained and explicitly invoked.
- `OBL-20260914T183608Z-4D61B8` — accept the local Chat-mode runtime transport before production lease use.
- `evidence/research/chat-invocation-runtime-2026-09-15.md` — detailed research trail.

## What is NOT yet accepted

Retrieval Reliability remains open.

Do not treat successful invocation/lease issuance as proof that the selected Context Pack is adequately precise. Blind-v3 testing already showed:

- held-out positive recall can succeed while forbidden adjacent records are still selected;
- negative/no-answer controls fail abstention;
- passage reranking improves some adjacent discrimination but does not provide a universal null gate;
- the open question is evidence sufficiency / answerability, not merely relevance ranking.

The pending NLI-style answerability probe was prepared earlier but intentionally paused while invocation architecture was resolved. Resume retrieval work from the frozen evidence, not from a new guess.

## Immediate Qiven-v3 resume sequence

1. Explicitly invoke `@qiven` in the fresh Chat.
2. Run the mandatory local Context prepare through Remote Desktop Commander; fail closed if it does not succeed.
3. Read this checkpoint and the selected canonical ADR/memory/obligation evidence returned by the local Context Pack as needed.
4. Confirm the live qiven-context branch/head and clean working tree.
5. Treat Invocation + local Execution + Context Lease issuance as established Phase 1 infrastructure.
6. Resume the unresolved Retrieval Reliability work, specifically answerability / null-gate measurement and held-out negative-control acceptance.
7. Do not resume Qiven Operator merge/release work until `OBL-20260914T124259Z-7A4D13` is accepted and closed.

## Cold-boot safety rule

The fresh Chat must not rely on this message, model-native memory, or previous conversation summaries as project authority. Use them only to locate the canonical runtime. Qiven project-history claims must follow a successful explicit `@qiven` local prepare and be grounded in the returned canonical evidence.