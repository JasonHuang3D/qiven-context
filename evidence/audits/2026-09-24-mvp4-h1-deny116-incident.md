# MVP-4 H1 Trial 3 Incident — deny-116 undifferentiated mediator failure (2026-09-23/24)

## Report

MVP-4 owner-live H1 trial 3 (2026-09-23, after the trial-2 fix kit at
`0.1.0-gdb7972c1`): with the fail-closed hook gate enabled in a fresh owner
session, governed tool calls denied with reason 116 (`host_unavailable`
class, hook-client source) even though the RuntimeHost process was up. The
denial text did not distinguish failure causes, and the client↔host wire
contract had never been exercised end-to-end by any test. Canonical program
record (ADR-0050 Context): "an unavailable fail-closed mediator with an
undifferentiated denial and an unobserved connection contract". The
owner-side per-call texts were not relayed verbatim; this record binds the
canonical symptom class to the code-level root cause below. If the H1 rerun
contradicts this analysis, this record is amended.

## Root cause (code audit 2026-09-24, v23, at qiven-runtime main `f0ca5b7`)

1. **Connection-model contradiction (the dominant defect).** The serve loop
   (`apps/runtime_host_main.cpp:188-281`) serves exactly ONE frame per
   connection: accept → admission → one `read_frame()` → `handle()` → one
   reply write → the loop-scoped `PipeConnection` is destroyed
   (`DisconnectNamedPipe` + `CloseHandle`, `src/ipc/named_pipe_server.cpp:249-256`)
   and the loop re-accepts. The hook client (`src/adapter/zcode_hook.cpp:82-158`,
   `transact`) sends TWO frames on ONE connection: Hello (`connection_seq=1`),
   reads the hello reply, then HookEvent (`connection_seq=2`) and reads that
   reply. After the hello reply the server destroys the connection; the
   client's second read hits `ERROR_BROKEN_PIPE` → "no reply from host" →
   `deny 116` **with a healthy host**. `apps/runtimectl_main.cpp` (one frame
   per connect) is the only client matching the server's model — which is why
   every local probe passed while the real hook denied.
2. **Admission-rejected has no reply surface.** The serve loop silently drops
   non-admitted client images (`runtime_host_main.cpp:209`, typed 62 class);
   the client then observes the same indistinguishable "no reply from host".
3. **Replay protection is dead in the live path.** `ReplayGuard` is
   constructed (`runtime_host_main.cpp:176-177`) but `replay.accept(...)` is
   never invoked; `FrameHeader::connection_seq` documents "strictly
   increasing per connection" (`include/qiven/runtime/ipc/framing.hpp:55`) —
   a wire designed for multi-frame connections the server never serves.
4. **No deadline anywhere.** Server and client use synchronous `PIPE_WAIT`
   handles with no read deadline; the timeout failure class is not diagnosable
   and the hook blocks until the harness `timeoutMs` kills it.

Test gap (correlated-test miss, scar class): no test sends multiple frames on
one connection; no end-to-end hook-client↔RuntimeHost pipe test exists
(`tests/host_lifecycle.cpp:206-243` does one frame each way, mirroring the
server's model; `tests/pipe_frame_security.cpp` never exchanges frames with
the server loop). `tools/h1_kit.py` preflight checks clean tree + gate
receipt + binary presence but performs no functional pipe round-trip, so the
defect passed preflight into the owner's live session.

## Classification (scar lifecycle §5.3)

- **Mature known engineering hazard** (untested external wire contract:
  correlation between the only matching client's shape and every test), plus
  **specification defect** (undifferentiated denial vocabulary collapses
  no-listener / admission-rejected / version-skew / secret-skew / timeout /
  broken-pipe into one 116).
- NOT genuinely unknown platform behavior: named-pipe connection semantics
  are documented and were already encoded in `framing.hpp`'s own contract.

## Corrective obligations (the bounded lane, roadmap amendment §5.1)

1. Explicit connection-model design decision (multi-frame per connection is
   the wire's declared contract), proven by a real-pipe multi-frame contract
   test that FAILS on the current one-frame serve loop.
2. Denial taxonomy split: no-listener, admission-rejected, version-skew,
   secret-skew, timeout, and post-reply disconnect become diagnosable,
   disjoint classes; admission rejection gains a typed reply surface.
3. Invoke `ReplayGuard` in the live serve path (or remove the dead claim);
   remove comments/design text the implementation does not honor.
4. Regressions that fail for the ACTUAL prior implementations (one-frame
   loop, silent admission drop, dead replay guard, undifferentiated 116).
5. Enable-gated kit pre-flight self-check: host reachability, identity, and
   handshake proven in the target environment BEFORE the live hook config is
   enabled (not an availability guarantee; fail-closed stands after enable).
6. Real H1 rerun until the original MVP-4 exit gate passes (owner hands).

## Lesson

A wire contract without an end-to-end test is an assumption wearing a
protocol's clothes: every transport failure collapses into one undifferentiated
denial, and the only client that matches the server's accident is the test
tool. Recorded as MEM-20260924T032000Z-C1D2E3. Trial-2's borrowed-lifetime
lesson is recorded as MEM-20260924T032100Z-D4E5F6.

## Addendum (2026-09-24, v23 corrective lane): the SECOND root cause

Fixing the connection model did not by itself make the live pipe work: the
corrective lane's enable-gated preflight (its first run, 2026-09-23T20:13Z)
surfaced a second, coexisting defect — the client install record
(`.qiven/runtime/clients.json`) contained ONLY the host exe (first boot had
registered `{self}` alone), so EVERY hook/runtimectl client denied
admission. Under the OLD serve loop this was a SILENT drop: with both
defects stacked, every real pre_tool denied 116 and the two causes were
indistinguishable. The typed admission surface (corrective decision D2)
made the second cause legible as an honest deny 121 with the rejected
image path — exactly the diagnosability the incident demanded. Fix:
qiven-runtime PR #56 `6ebf6ff` (boot merges the installation's
same-directory tool images into the record, idempotently; the owner-only
DACL remains the trust boundary). The preflight then PASSED end to end
(host boot → verdict round trip → authenticated-shutdown EXIT → typed-120
honesty probe; log 20260923T202019Z-00024304-236456). Two coexisting bugs,
one symptom — again the trial-2 pattern; the incident class is now
regression-proven (ipc_multiframe_contract, seven sections).
