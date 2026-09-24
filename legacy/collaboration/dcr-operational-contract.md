# [SEALED] DCR Operational Contract

This document consolidates the operating rules for Desktop Commander Remote (DCR) as Qiven's JasonPC transport. It is a cold-boot entry point, not a replacement for underlying audits, ADRs, and memory records.

## Authority boundary

DCR is transport, not engineering authority. `jason-brother` or an explicitly authorized Work task selects the repository, exact operation, validation scope, and stop conditions.

The 2026-09-16 concurrent-MCP incident invalidated one earlier implicit assumption: a single conversation/user intent must **not** be assumed to produce one local execution flow. A Chat/UI response branch, retry, delayed backend action, Work flow, or another MCP client may coexist unexpectedly.

Therefore conversational/UI singularity is not a safety boundary. ADR-0026 requires JasonPC host-side single-writer authority, leases, fencing, sequencing, and quarantine before mutating DCR execution resumes.

Until that broker passes acceptance, DCR use on JasonPC is restricted to read-only incident forensics. Human/owner-controlled local execution is the trusted bootstrap path for the broker.

## Execution identities

Never infer machine-local authority merely because a DCR device is reachable. At minimum, distinguish:

- AI/Chat/Work caller flow;
- transport/DCR server;
- DCR-launched child process;
- future Qiven Host Execution Broker transaction/lease.

Current DCR recent-call history does not expose a stable assistant-response identity capable of distinguishing two competing Chat response branches. Chronology is therefore not sufficient fencing or attribution.

## Liveness

`list_devices = online` is only a candidate control-plane state. Treat DCR as live only after `ping` succeeds or a deliberately tiny command succeeds through the intended device.

A UI status transition may lag reality. Do not infer that an owner-stopped DCR has restarted merely because device state still says online.

## Shell identity is explicit

Command text does not establish shell semantics. If a call depends on Windows CMD parsing or control flow such as `&&`, `call`, `%ERRORLEVEL%`, or batch-file behavior, the DCR execution request must explicitly select CMD.

Do not send a CMD chain through an ambient/default shell and infer host failure from the resulting parser error. PowerShell, CMD, Git's shell parsing, and direct process invocation are distinct execution boundaries.

## Canonical JasonPC Git/SSH environment

For the accepted Windows OpenSSH path, DCR-launched engineering commands that require SSH must establish `ProgramData=C:\ProgramData`. Desktop Commander Remote 0.2.50 / its MCP environment boundary omits `ProgramData`; JasonPC Windows OpenSSH 9.5 exits `255` before config/network/key processing when it is absent.

Use deterministic executable/config paths and non-interactive controls rather than ambient discovery:

- Git: `C:\Program Files\Git\cmd\git.exe`;
- SSH: `C:\Windows\System32\OpenSSH\ssh.exe`;
- SSH config: `C:\Users\61626\.ssh\config`;
- Python: `C:\Env\python\3.14.7\python.exe` until launcher behavior is separately deterministic;
- `GIT_TERMINAL_PROMPT=0`;
- `GCM_INTERACTIVE=Never`;
- SSH batch mode with zero password prompts and password/keyboard-interactive authentication disabled.

Do not weaken SSH key ACLs, host-key verification, or security controls to compensate for an execution-context mismatch.

## Lifecycle

An authorized local-execution task may self-start DCR in the active owner session without owner credentials, a service, scheduled task, or persistence. Lifecycle automation must track the exact process tree and terminate only the positively identified DCR instance. Never kill generic `node.exe`, `cmd.exe`, PowerShell, or Terminal processes by name.

A fresh restart is a legitimate in-process resource-reclamation boundary for the current official local MCP implementation, but restart policy must preserve truthful interruption semantics.

After ADR-0026 acceptance, DCR lifecycle readiness is separate from Host Broker authority readiness: a healthy transport still cannot execute without a valid broker lease/fencing epoch.

## Result fidelity and wrapper hazards

Do not treat wrapper output as trustworthy merely because it prints an exit code. Windows CMD `%ERRORLEVEL%` can be expanded before the command under test executes. For precise diagnostics prefer delayed expansion or an explicit process API such as Python `subprocess.run(..., shell=False)` with captured return code/stdout/stderr.

Shell quoting is itself a failure surface. Git's `GIT_SSH_COMMAND` is parsed by a shell; Windows backslash-heavy executable strings can be misparsed. Prefer validated forward-slash paths and explicit quoting. When a wrapper fails, classify it as a wrapper/probe-design failure unless host failure is independently evidenced.

GitHub's successful SSH authentication may intentionally return a non-shell status/message. Judge authentication semantically and verify the enclosing Git operation rather than equating `ssh -T` shell status with Git failure.

## Safe scripted edits

A read-modify-write helper is not automatically atomic. During Qiven-v4, a Python `Path.write_text(...)` call opened/truncated an existing test file and then raised on an invalid newline parameter, leaving a zero-byte target even though the edit command itself reported failure.

For nontrivial scripted replacement of an authoritative local file, prefer:

1. read source;
2. write a sibling temporary file;
3. validate the complete temporary result;
4. flush/close it;
5. replace the target atomically where the platform/filesystem permits;
6. verify the resulting file/diff.

Use dedicated edit primitives for surgical replacements when available. A failed editing process does not prove that the target file is unchanged.

## Generated CMake / Windows path boundary

Do not inject native Windows backslash paths directly into generated CMake source strings. Sequences such as `\U` can be parsed as invalid CMake escapes. Normalize host paths through CMake/path-aware mechanisms or forward-slash representation before embedding them in generated CMake code.

## Transport loss, request timeout, UI/backend divergence, and split-brain

Transport loss does not prove that the local child stopped, and it does not prove that a mutation failed. A DCR request timeout can leave its spawned local process running to completion.

Likewise, Chat UI delivery failure does not prove backend tool execution stopped. Qiven-v4 observed a UI send failure while already-dispatched GitHub/DCR calls continued and completed.

The 2026-09-16 incident adds a stronger case: two Chat answer choices were observed concurrently executing against the same JasonPC DCR/MCP capability. Even when each flow is internally sequential, two such flows can invalidate repository and validation assumptions.

After any transport interruption, request timeout, UI send failure, uncertain tool return, or suspected duplicate execution, do not replay the operation immediately. Reconcile first:

1. prove fresh transport liveness if DCR itself is being inspected;
2. inspect recent tool-call history when available, while remembering that it lacks caller-flow identity;
3. inspect active terminal/process state;
4. inspect repository/filesystem state;
5. inspect exact remote Git state for mutations;
6. determine which atomic steps definitely completed;
7. resume only the missing steps, and only when the authority plane is known safe.

If competing execution authority is suspected after the Host Broker is deployed, normal recovery is replaced by broker quarantine/reconciliation; no caller gets to decide unilaterally that the host is free.

## Output and resource behavior

The official Desktop Commander 0.2.50 path is not safe to treat as an unbounded human console. Its remote device logs full tool arguments/results to the foreground console, and its local `TerminalManager` retains completed-session output with a per-session cap but no smaller aggregate byte budget/TTL found in the inspected implementation.

Therefore Qiven automation should avoid returning or printing large payloads unnecessarily. Prefer bounded summaries, file-backed diagnostics, byte-counted buffers, and explicit pagination. The Qiven DCR Windows product exists in part to supervise this transport with continuously drained pipes, byte-bounded observability, memory monitoring, exact process ownership, and controlled recycle.

## Mutation and validation discipline

Before ADR-0026 broker acceptance, mutating DCR execution is suspended.

After broker acceptance, every production Qiven local call must traverse the broker and carry the active transaction lease, fencing epoch, and request sequence. A direct mutating DCR/MCP path around the broker is a safety defect, not a convenience fallback.

For exact-head validation, bind every result to the exact candidate SHA. If the branch head changes after validation, revalidate the new head. Fail closed on interactive credential/host-key/password prompts.

## Evidence map

Primary evidence and supporting records include:

- `evidence/audits/dcr-acceptance-2026-09-15.md`;
- `evidence/audits/dcr-windows-b000-output-retention-2026-09-15.md`;
- `evidence/audits/concurrent-mcp-split-brain-2026-09-16.md`;
- `ADR-0026`;
- `MEM-20260915T092000Z-3C7A41`;
- `MEM-20260915T101200Z-91B4F0`;
- `MEM-20260915T114600Z-7D2F8C`;
- `MEM-20260915T163500Z-5E7A91`.


> Archived to the museum 2026-09-21 (ADR-0043): the DCR transport
> program is retired. Preserved as historical evidence of the
> 2026-09-16 split-brain incident and the transport rules learned.
