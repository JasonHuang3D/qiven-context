# DCR Operational Contract

This document consolidates the accepted operating rules for using Desktop Commander Remote (DCR) as Qiven's JasonPC execution transport. It is a cold-boot entry point, not a replacement for the underlying audit evidence and memory records.

## Authority boundary

DCR is transport, not engineering authority. `jason-brother` or an explicitly authorized Work task selects the repository, exact operation, validation scope, and stop conditions. Human CMD remains the fallback when DCR is unavailable or a capability has not been accepted.

Never infer machine-local authority merely because a DCR device is reachable. Work/Codex runner identity, DCR server identity, and DCR-launched child identity are separate execution boundaries.

## Liveness

`list_devices = online` is only a candidate control-plane state. Treat DCR as live only after `ping` succeeds or a deliberately tiny command succeeds through the intended device.

A UI status transition may lag reality. Do not infer that an owner-stopped DCR has restarted merely because device state still says online.

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

## Result fidelity and shell hazards

Do not treat wrapper output as trustworthy merely because it prints an exit code. Windows CMD `%ERRORLEVEL%` can be expanded before the command under test executes. For precise diagnostics prefer delayed expansion or an explicit process API such as Python `subprocess.run(..., shell=False)` with captured return code/stdout/stderr.

Shell quoting is itself a failure surface. Git's `GIT_SSH_COMMAND` is parsed by a shell; Windows backslash-heavy executable strings can be misparsed. Prefer validated forward-slash paths and explicit quoting. When a wrapper fails, classify it as a wrapper/probe-design failure unless host failure is independently evidenced.

GitHub's successful SSH authentication may intentionally return a non-shell status/message. Judge authentication semantically and verify the enclosing Git operation rather than equating `ssh -T` shell status with Git failure.

## Transport loss, request timeout, and UI/backend divergence

Transport loss does not prove that the local child stopped, and it does not prove that a mutation failed. A DCR request timeout can leave its spawned local process running to completion.

Likewise, Chat UI delivery failure does not prove backend tool execution stopped. A prior Qiven-v4 turn showed the UI report an error while already-dispatched GitHub/DCR calls continued and completed successfully.

After any transport interruption, request timeout, UI send failure, or uncertain tool return, do not replay the operation immediately. Reconcile first:

1. prove fresh DCR liveness;
2. inspect recent tool-call history when available;
3. inspect active terminal/process state;
4. inspect repository/filesystem state;
5. inspect exact remote Git state for mutations;
6. determine which atomic steps definitely completed;
7. resume only the missing steps.

This recovery rule applies equally when Clash/upstream networking fails, when the Chat turn ends, or when the DCR caller itself loses the response.

## Output and resource behavior

The official Desktop Commander 0.2.50 path is not safe to treat as an unbounded human console. Its remote device logs full tool arguments/results to the foreground console, and its local `TerminalManager` retains completed-session output with a per-session cap but no smaller aggregate byte budget/TTL found in the inspected implementation.

Therefore Qiven automation should avoid returning or printing large payloads unnecessarily. Prefer bounded summaries, file-backed diagnostics, byte-counted buffers, and explicit pagination. The Qiven DCR Windows product exists in part to supervise this transport with continuously drained pipes, byte-bounded observability, memory monitoring, exact process ownership, and controlled recycle.

## Mutation and validation discipline

DCR must execute the exact intended operation; it must not autonomously broaden scope or repair the host after an unexpected failure unless the current task explicitly authorizes diagnosis/remediation.

For exact-head validation, bind every result to the exact candidate SHA. If the branch head changes after validation, revalidate the new head. Fail closed on interactive credential/host-key/password prompts.

## Evidence map

Primary evidence and supporting records include:

- `evidence/audits/dcr-acceptance-2026-09-15.md`;
- `evidence/audits/dcr-windows-b000-output-retention-2026-09-15.md`;
- `MEM-20260915T092000Z-3C7A41`;
- `MEM-20260915T101200Z-91B4F0`;
- `MEM-20260915T114600Z-7D2F8C`;
- the Qiven-v4 transient-network/UI-backend reconciliation incidents recorded in active DCR Windows project history.
