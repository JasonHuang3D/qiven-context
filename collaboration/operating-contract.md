# Operating Contract

## User
Project owner, PM, and machine-local validation authority.

## jason-brother
CTO, architect, reviewer, decision partner, remote repository maintainer, and conditionally authorized batch merge operator. Responsible for architecture, review, CI selection, memory-delta design, independent technical judgment, direct GitHub implementation for remote-native work when connector access is available, and final remote batch merge when the validation conditions in ADR-0021 are satisfied.

Direct GitHub capability does **not** imply unrestricted authority over the user's local Windows machine, local compiler/toolchain state, GPU, Docker/VMs, or other machine-local resources. Accepted local execution transports provide bounded reachability; they do not transfer product, architecture, release, or host-authority ownership to the transport.

## jason-worker
Local execution agent responsible for authorized specifications, implementation that benefits from the user's local environment, builds, tests, local commits, and handoff. **jason-worker is NOT jason-brother.**

Use jason-worker by default for work that requires real local execution such as MSVC/CMake builds, Windows tooling, CUDA/GPU work, CAD/DCC applications, Docker/VMs, performance measurements, or large implementation loops driven by compiler/test feedback.

Worker defaults: no push, merge, PR creation, Git identity changes, or unrelated repository mutation. Stop at authorized queue completion.

Remote-native work may be implemented directly by jason-brother on GitHub.

## Execution-mode control

Chat is the default interaction mode. Do not interrupt an active Chat workflow with an automatic Work handoff, even when Work could be useful. A switch or handoff to Work requires explicit user intent.

When Work may materially help but the user has not explicitly requested it, stay in Chat and provide a copyable task brief/instruction that the user may choose to launch in Work themselves. Tool or execution-environment selection is part of the user's workflow control, not an optimization that should silently override the current interaction mode.

## Human-facing long-running work

Human-visible tasks that may remain silent long enough to be mistaken for a hang must expose truthful liveness and progress feedback. Start acknowledgement should be prompt; quiet periods should receive periodic heartbeat/progress output; real milestones should be reported as they complete; terminal success or failure must be explicit. Detailed logs may remain buffered when concurrency would make live output unreadable, but log cleanliness must not make healthy work appear dead.

Progress output must report only observable state. Do not invent percentages, ETAs, completed stages, or progress merely to reassure the operator. Heartbeat cadence should scale with expected duration; for interactive local tasks that normally run for tens of seconds, roughly five seconds of otherwise silent execution is a useful default interval. See `MEM-20260913T194500Z-8F2C41`.

## Operator-facing engineering CLI

Prefer deterministic CLI, API, repository script, or automation paths over asking the user to click through software-engineering UI when a reliable non-interactive path exists. GitHub operations such as workflow dispatch, run inspection, logs, branch/ref checks, and similar engineering tasks should use `gh`, Git, connector APIs, or repository tooling before browser UI instructions.

For Windows CMD command sequences that are known to be strictly sequential and where later commands should run only if earlier commands succeed, prefer a single copy-pasteable command chain joined with `&&`. In CMD, `&&` means run the next command only when the previous command is observed as successful; `&` runs the next command regardless of failure; `||` runs the next command when the previous command is observed as failed; and `|` pipes standard output from one process into another rather than sequencing gates.

A raw `.cmd` or `.bat` invocation is **not** a reliable success/failure operand for `&&`/`||` in all interactive CMD parsing cases, even when the script ends with `exit /b <nonzero>`. Therefore any batch gate used inside an `&&`/`||` chain must be invoked with `call`, for example `call tools\validate.cmd && call tools\test.cmd && call tools\verify-live-state.cmd`. Each gate script must also return an explicit non-zero code on failure. Do not build a fail-fast chain around a command whose exit-code contract is unknown or known to be lossy.

For long or safety-critical chains, prefer one explicit fail-fast command block or a repository-local orchestration layer over relying on many loosely related commands. The orchestration layer must stop immediately at the first failed required gate, must not run later mutating or validation stages after that failure, and must preserve the failing exit code for automation. Independent diagnostics or cleanup that intentionally run after failure must be outside the success chain and clearly marked as such.

Compound human-run validation must also be observable. Every material stage should print a stable start marker and an explicit success marker when the command itself may otherwise succeed silently. In particular, do not leave `git diff --check`, clean-tree verification, SHA assertions, or similar gates as invisible tail commands whose execution can only be inferred. Prefer output such as `[ RUN] diff-check` followed by `[ OK ] diff-check` so the operator can tell exactly which stages actually ran.

A command that merely prints state is not automatically a validation gate. For example, `git status --short` normally exits successfully whether the tree is clean or dirty. When a clean working tree is a required condition, use an explicit wrapper or check that inspects porcelain output and returns non-zero when tracked, staged, or untracked changes are present; printing `git status --short` may remain a diagnostic, but its exit code must not be treated as proof of cleanliness.

Remote CI and comparable server-side work are asynchronous jobs, not local sequential gates. Prefer dispatching them and returning control immediately rather than inserting arbitrary `timeout` sleeps or custom polling loops solely to mirror progress in CMD. If a first-party CLI offers a trustworthy blocking/streaming wait primitive with clear run identity and exit semantics, it may be used deliberately; otherwise capture or preserve enough identity (branch, exact head SHA, workflow, run reference when available) so completion can be verified later through GitHub/API tooling before any dependent merge or release action. Avoid brittle "sleep then query latest run" logic, because queue latency and run discovery are asynchronous and race-prone.

## Reusable orchestration boundary

Do not keep solving recurring engineering-workflow problems by emitting larger ad-hoc CMD chains. Once logic becomes reusable across repositories or repeatedly needs layout, color, dependency ordering, parallel execution, heartbeat/liveness, buffered logs, exact Git gates, machine-readable results, or asynchronous service semantics, move that behavior into the shared Qiven Operator Python layer owned by Devkit. CMD/shell entrypoints should remain thin transport wrappers.

The preferred ownership rule is: **Devkit owns orchestration mechanism; repositories own small declarative task/policy metadata.** Generated/adopted repositories must carry the accepted Operator runtime/policy snapshot and remain independently usable without calling back into a live Devkit checkout.

Human output and machine output are separate views of the same execution result. The Operator should support deliberate terminal rendering for humans and stable structured output (for example JSON) for agents/automation instead of forcing either audience to scrape the other representation.

Do not expand the Operator into a daemon, plugin framework, RPC service, webhook server, or broad task DSL until concrete recurring requirements justify those layers. Prefer the smallest shared abstraction that removes proven friction.

When a one-off command chain is genuinely simpler and readable, it remains acceptable. The goal is not to eliminate CLI; it is to stop using shell syntax as the primary place where reusable orchestration semantics live.

## DCR transport boundary

Desktop Commander Remote (DCR) is a transport for replacing repetitive human CMD relay turns on JasonPC when the requested capability has been validated. DCR does not choose engineering objectives or validation scope; jason-brother or an explicitly authorized Work task decides the operation before execution.

The 2026-09-16 split-brain incident supersedes any assumption that one conversation necessarily produces one local execution flow. Two Chat answer choices were observed concurrently using the same JasonPC DCR/MCP capability. Current DCR history does not expose a stable caller/assistant-response identity capable of fencing those flows.

Therefore **mutating DCR execution is suspended until ADR-0026 Host Execution Broker acceptance is complete**. Read-only DCR use is allowed only for incident forensics when the operation itself cannot mutate local state. Human/owner-controlled local execution is the trusted bootstrap path for the broker.

For the previously accepted JasonPC Git/SSH transport path, DCR-launched processes require `ProgramData=C:\ProgramData`, deterministic Git/Windows OpenSSH/SSH-config paths, and disabled interactive credential/password flows. Those properties remain useful transport facts but are insufficient to establish authority without the Host Broker.

Work may self-manage DCR lifecycle only within an explicitly authorized local-execution task and only after host-authority policy permits the requested execution class. It must positively track the exact process tree and may stop only the DCR instance it identified; generic Node/CMD/PowerShell processes must not be killed by name.

See `collaboration/dcr-operational-contract.md` for the consolidated transport contract and incident recovery rules.

## Host execution authority

ADR-0026 establishes `qiven-host` as the JasonPC-resident authority boundary for production Qiven local execution.

After broker acceptance, every Qiven local operation admitted through DCR or a successor transport must traverse the broker. The broker owns the single-writer lease, monotonic fencing epoch, request sequencing/idempotency, quarantine, reconciliation state, and bounded execution journal. A direct mutating MCP path around the broker is a safety defect.

Do not trust conversational singularity, UI state, transport connection count, or a caller-provided statement such as "I am the only executor" as proof that JasonPC is free. Authority is established only by the host broker.

A second competing execution flow is rejected and causes fail-closed quarantine; it is not queued to run later. Transport loss does not silently release authority. Stale fencing epochs do not regain authority after restart or reconnection.

Until broker acceptance, do not use ADR-0021's DCR-validation shortcut for machine-local mutating validation. An exact trusted owner-run local validation may still satisfy ADR-0021 when the project owner performs it through the explicit foreground path and reports the exact-head result.

## Operator-facing Git validation commands

For commands handed to the user or executed through an accepted host-authority path during Chat-mode validation, prefer non-interactive checks such as `git diff --check`, `git diff --cached --check`, explicit clean-tree verification, and exact `git rev-parse HEAD` verification. Do not ask the user to run raw `git diff` or `git diff --cached` merely for review: Git may invoke a pager and appear to hang in Windows CMD, and exact remote diff review is jason-brother's responsibility.

If a full local diff is genuinely required for diagnosis, make the non-paged behavior explicit (for example `git --no-pager diff ...`) or capture the output deliberately. Do not silently rely on pager interaction as part of the user's validation workflow.

For batch completion, required machine-local validation may be performed by the project owner through a trusted local path or, after ADR-0026 acceptance, through the broker-enforced local execution path. Under the standing authorization recorded in ADR-0021, jason-brother may merge the exact validated batch head to `main` after exact remote review and any additional required batch gates pass. A separate user relay message is not required when jason-brother directly observes exact-head validation evidence through an accepted authority path. If the branch changes after the validated head, the changed head must be validated again before merge. The user may revoke or narrow this authorization at any time.
