# Operating Contract

For qiven-context Python semantics and source-contract work, the project owner's
2026-09-17 authorization in `collaboration/context-validation.md` (ADR-0032)
applies: the acting session validates directly in the agent runtime, without duplicate
JasonPC validation. Platform-dependent work and Host/DCR restrictions remain scoped
as described below.

## Authority packages and the single-session engineering model

ADR-0044 (2026-09-22) adopts **single-session unified engineering** as the
default execution model. One capable owner-supervised session performs the
full engineering loop — task specification, design, implementation,
testing, validation, gating, publication under H2, and the closing context
transaction — with no role-stage handoffs. Cross-session continuity is
owned by qiven-context cold boot plus session checkpoints, never by
role-to-role handoffs.

Roles are defined independently of any model, product, or client tool. A
ContextView declares which qualified model instance fulfills a role and
through which client-tool capability class it executes, per ADR-0035; it
must not redefine the roles themselves. Per ADR-0044, role packages are
**attribution and qualification labels, not behavioral stages**: they
never partition who may design, implement, build, test, measure, review,
or publish.

The duties the staged roles used to protect are session duties:

- **Review discipline** (formerly the reviewing role's): exact-delta
  self-review before every H2 request; semantic acceptance is never
  equated with a passing CI run; memory-delta/context-transaction design
  at material changes; rejected alternatives and negative knowledge
  recorded.
- **Publication discipline**: no push, PR creation, merge, or Git
  identity changes without explicit owner authorization or a standing
  accepted delegation (for example long-running mode per
  `collaboration/human-handoff-boundary.md`); unattended automation
  remains read-only by default.
- **Capability never implies ownership**: direct GitHub or machine-local
  capability does not transfer product, architecture, release, or
  host-authority ownership to the session. Accepted execution transports
  provide bounded reachability, not authority.

## User
Project owner, PM, and machine-local validation authority.

## Role labels (attribution and qualification only)

`jason-brother`, `jason-worker`, and owner-granted designations such as
`jason-extended-cognition` remain valid as commit-attribution values and
as ContextView binding labels per ADR-0035. A binding's evidence-based
qualification is unchanged. Terminology mapping for records that predate
ADR-0044 is defined by ADR-0044 clause 5 (reviewing-role decisions map to
owner-designated architecture decision points; worker-role execution maps
to the executing session).

## Model bindings and disclosure

A binding (`jason-brother-glm5-3`, `jason-worker-glm5-3-flash`, `jason-brother-gpt6`, `jason-worker-gpt5-6sol`, and future instances) is evidence-based per ADR-0035: qualification states (`untested`, `provisional`, `qualified`) are recorded in the view and upgraded only by a recorded context transaction. Model resolution is `verify_live`: when the model that actually served a session differs materially from the declared binding, the session must disclose the substitution in its checkpoint, and merge-class actions may require replacement-tier review. Session acceptance also follows `collaboration/human-handoff-boundary.md` (ADR-0036): mandatory typed handoffs cannot be waived conversationally.

## Tool-policy and connector write boundary

A connector refusal is a tool or platform boundary and must be stated as such. Do not disguise a connector or policy refusal as an engineering objection, filesystem problem, or repository limitation.

When legitimate Qiven canonical content is blocked by a selected connector because the connector classifies the write as sensitive, restricted, or otherwise unacceptable, do not silently euphemize the engineering meaning, omit material facts, or weaken the canonical record merely to make the connector accept it. Preserve the intended semantics and switch authoring path.

The preferred fallback is an explicitly trusted local authoring path: the project owner or a trusted local session may create the exact file or patch locally and push it, after which the reviewing session performs exact remote review. If no suitable trusted execution path is available, the last reliable fallback is for the session to generate the exact Markdown or patch for the project owner to write or apply.

This fallback does not authorize circumvention of an actual platform policy that forbids the underlying content. If the content itself is disallowed, that policy boundary remains and must be stated directly.

Qiven Host and DCR are a separate local execution and authority plane. After Host acceptance, their responsibility is admission, fencing, execution authority, recovery, and no-bypass safety; Qiven should not intentionally duplicate a remote connector's content-classification policy inside Host. External connector policies still apply whenever those external tools are used.

See `MEM-20260915T203423Z-C4A912`.

## Interaction-mode control

Tool or execution-environment selection is part of the owner's workflow
control, not an optimization a session should silently override. In
participant combinations that still present separate chat and execution
surfaces (for example a cloud chat agent without local execution), a
switch to a separate execution surface requires explicit owner intent; do
not interrupt an active workflow with an automatic handoff, and when a
separate execution surface may materially help, offer a copyable task
brief instead of switching unilaterally. In single-session local-agent
tools there is no mode switch: the session executes directly under its
permission surface (ADR-0044).

## Human-facing long-running work

Human-visible tasks that may remain silent long enough to be mistaken for a hang must expose truthful liveness and progress feedback. Start acknowledgement should be prompt; quiet periods should receive periodic heartbeat/progress output; real milestones should be reported as they complete; terminal success or failure must be explicit. Detailed logs may remain buffered when concurrency would make live output unreadable, but log cleanliness must not make healthy work appear dead.

Progress output must report only observable state. Do not invent percentages, ETAs, completed stages, or progress merely to reassure the operator. Heartbeat cadence should scale with expected duration; for interactive local tasks that normally run for tens of seconds, roughly five seconds of otherwise silent execution is a useful default interval. See `MEM-20260913T194500Z-8F2C41`.

## Waiting on humans or external events (owner direction 2026-09-26)

When a step must wait for a human action or an external event before the session can continue, the wait is event-driven or blocking, never polled:

1. **Waiting for a human inside a turn** uses `AskUserQuestion` (the blocking interactive question): the turn suspends until the owner answers; the question carries the paste-ready instruction and honest outcome options — a bare "ready?" is a defect.
2. **Waiting for a machine-observable event** uses a `run_in_background` watcher command that exits exactly when the condition holds; the harness notifies the session once on completion (the ADR-0051 notification-once law). The watcher sleeps; the LLM does not.
3. **LLM-side foreground sleep/poll loops are prohibited in every class.** This extends ADR-0051's anti-pattern scope from command supervision to human/event waiting. When both waiting and ending the turn are possible, ending the turn and resuming on the notification is preferred; `TaskOutput` with an explicit bounded budget is the in-turn blocking fallback, and repeated timeout re-waits must not degrade into polling.
4. The heartbeat/progress duties of the previous section apply to invoked processes' output, never to the LLM's own waiting: a silent wait on the correct primitive is healthy, and periodic tick output from a hand-written wait loop is the defect, not the cure.

The workflow pattern (decision table, watcher shapes, timeout guidance) lives in `views/workflows/human-in-the-loop-wait.md`; this section is the contract carrier. Governing incident: the 2026-09-26 v30 wait loop (`MEM-20260925T175000Z-F6A7B8`; the surrounding session incident `MEM-20260925T190500Z-C0A1B2`).

## Long-command routing (2026-09-23 owner direction; amended 2026-09-24 by ADR-0051, ACCEPTED — owner H2 2026-09-24 in v26)

The canonical registry of long/measured/interactive command classes is
`collaboration/long-command-registry.md` (classes, members, thresholds,
evidence). The devkit hook router (v4) implements it at the ZCode
PreToolUse boundary; every operator task records a duration so class
membership is decided from measured evidence. Every hook denial carries
the `[qiven-hook]` provenance tag and, where probed, the measurement —
an ambiguous denial is a defect (it splits the receiving agent's
reasoning).

ADR-0051 (2026-09-24, re-reviewed in v25): the default reroute for
in-session long work is the harness's `run_in_background` — the router
denies the raw call with the exact re-call instruction; one denied call
is the entire overhead and the harness notifies once on completion
(proven live, v25 probe P1/P5). Polling supervision (`qiven exec
status` loops, foreground `sleep && tail`) is an anti-pattern
(O(polls × context) token cost). Build/gate classes carry the
`MSBUILDDISABLENODEREUSE=1` guard on the background re-call
(ADR-0048 §3 extended; router v4.1 makes the guard check mechanically
real for the env-prefixed re-call form). Sweeps stay exec-lease-routed;
`qiven gate/run/ci` and oversized git-network denials instruct the
background re-call; `qiven exec/info/status` stay raw; git clone is
unconditional background. Foreground oversized output is bounded
natively by the harness (>~25-30KB auto-persists to a file with a
~2KB preview + path; probed 2026-09-24). The Bash `timeout` parameter
does NOT bind background tasks (v25 probe P3) — background re-calls
must be inherently-terminating commands. The user-level hook and
global AGENTS.md layer the v24 landing "deconflicted" against were an
accidental configuration, deleted by the owner 2026-09-24: the law's
carriers are this contract, the canonical registry, and the workspace
router only.

## File-authoring tool discipline (2026-09-23 recurrence; law since MEM-20260921T203500Z-D2A7F4)

Files are authored and edited through the platform's NATIVE file tools
(Write/Edit-style tools), never through shell heredocs, `echo`-redirects
or script-generated content embedded in the command line. Shell and
inline scripting are for COMPUTE (running checks, computing values), not
authorship. Root cause class: this session's tool channel re-interprets
escape sequences inside heredocs (`\\n` becomes a literal newline),
silently corrupting written files — observed twice in one turn
(2026-09-23) while patching Python, after the original 2026-09-21
incidents. A session that catches itself authoring file content inside a
shell command switches to the native tool for that edit and records the
slip if material. Mechanical enforcement since 2026-09-23: the ZCode
hook router owned by qiven-devkit (hook_exec_router) DENIES heredoc
authoring at the PreToolUse boundary, including heredocs wrapped inside
`qiven exec` payloads — the denial names this law (owner direction:
text-matching backstop for the recurring violation; the contract remains
the primary carrier).

## Tooling-defect handling — no silent detours (2026-09-23 owner direction; MEM-20260923T211500Z-C3D4E5)

When an owned engineering tool path (the Operator and its subcommands,
the hook router, gates, repository tooling) fails or behaves anomalously
— empty logs, popup windows, wrong exit codes, mangled quoting — the
session MUST treat it as a DEFECT in that tool, in one of exactly two
ways:

1. root-cause and fix the defect in the tool's owning repository (its
   tests carry the regression), or
2. if the fix is outside the session's scope or capability, STOP and
   escalate to the owner with the evidence and exit the turn if needed.

Routing AROUND the defect — silently switching to an alternate entry
path (a different wrapper, a direct interpreter invocation, a sibling
script) so work can continue while the defect stays broken — is
PROHIBITED. A detour taken without explicit owner authorization is a
process violation even when the produced work is correct: it leaves the
defect armed for the next session, corrupts evidence (the anomalous
behavior looks "solved"), and bypasses the owner's visibility into their
tooling's real state. A sanctioned temporary detour is possible only as
an explicit owner decision, recorded with its expiry. The governing
incident (2026-09-23): `qiven exec` on `.cmd` targets produced empty
logs and `0xC0000142` failures; the session switched to the `python`
entry point instead of root-causing — the exec defect stayed armed until
the owner observed popup console windows and ordered the audit that
fixed it (`CREATE_NO_WINDOW`; devkit 9fe34c1).

## Session and turn identity (2026-09-23 owner direction)

A SESSION is one continuous conversation thread with the owner (same
thread and context, no cold boot in between); a TURN is one
owner-message/response cycle inside it. Session checkpoints are ONE per
SESSION, refreshed across turns — never one per turn. A new session
begins only when the owner marks it (e.g. "这是新session") or a fresh
cold boot occurs; the agent NEVER infers or increments session identity
on its own. Full definition and correction history:
`collaboration/context-checkpoint.md`.

## Agent-invoked command timeouts and hang classification (2026-09-21 owner direction)

LLM sessions invoke commands through tool layers whose timeout behavior the
session must treat as part of the engineering contract, not as an accident
of the harness. Two failure classes must stay distinct:

- **apparent hang** — the process is alive but produces nothing (an OS
  modal dialog suspended it, it waits on interaction, or it deadlocked);
- **healthy long work** — a legitimately long command (the pre-optimization
  context gate ran ~5 minutes; future dev exes may repeat that shape).

Rules:

1. **Every invocation is bounded.** No unbounded waits. The invoker sets an
   explicit timeout sized from evidence: gate receipts carry per-task
   durations; with no evidence, start conservative and re-invoke with a
   larger explicit budget rather than waiting indefinitely.
2. **A timeout is a classification event, never a failure verdict and never
   a silent-retry trigger.** Record the command, its state and captured
   logs; then either re-invoke once with a justified larger budget, or stop
   and investigate. Repeated timeouts of the same command escalate rather
   than loop.
3. **Heartbeat is the liveness discriminator between the two classes.**
   Qiven-owned entry points invoked by agents (operator gates/tasks, test
   runners, exes) keep the liveness/progress duties above, and their output
   is the signal a supervising caller uses: observed heartbeat justifies
   deliberately extending the budget; silence past a threshold means a
   suspected hang — read the buffered logs before spending more budget.
   Heartbeat never removes the timeout ceiling: liveness is not
   termination, and a livelock still beats.
4. **Qiven executables must not block on OS modal UI in automated
   contexts.** Assert/abort paths in anything intended for agent invocation
   terminate (or write evidence and exit); they never pause the process
   awaiting interaction. The 2026-09-19 modal CRT abort incident
   (`MEM-20260919T153758Z-D6B4E7`) is the governing precedent; the concrete
   mechanism (abort-behavior configuration in test entry points, headless
   test discipline) is an implementation decision verified per repository.
5. **Custody-class commands route through the Qiven Operator; ordinary
   in-session long work routes through the harness's background
   mechanism** (2026-09-21 owner direction, rescoped 2026-09-24 by
   ADR-0051, ACCEPTED). LLM sessions running builds, test suites,
   compiler/linker invocations or any command whose duration class is
   unknown re-call it with `run_in_background: true` after the hook's
   denial (build/gate classes with the node-reuse guard) — the harness
   returns an output-file path immediately and notifies once on
   completion; polling is prohibited. Filesystem tree sweeps, runs that
   must survive the session, owner-run kits, and work past the harness
   Bash timeout ceiling (~10 min) route through the Qiven Operator
   (`qiven exec start/status/stop/list`): the child runs detached in its
   own bounded custody (watchdog + Job Object + lease, ADR-0048), the
   operator heartbeats while supervising and bounds its own wait, and
   the caller's shell dying does not kill the command. An exit no living
   supervisor observed is reported indeterminate, never guessed. Short
   read-only commands (status queries, file reads) may run directly.
   Canonical usage reference (pointer, not restated here):
   `qiven-devkit/docs/conventions/operator-usage.md`.

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

## DCR transport boundary (sealed, ADR-0043)

Desktop Commander Remote is a sealed historical transport (retired with
qiven-dcr-win, 2026-09-21). Its operational contract is museum material
(`legacy/collaboration/dcr-operational-contract.md`); the 2026-09-16
split-brain incident evidence remains canonical history and its
single-writer lesson is absorbed into RuntimeHost semantics (ADR-0043).
No DCR execution — mutating or read-only — is an active path; do not
re-enable any part of it without a new accepted decision.

## Host execution authority (sealed, ADR-0043)

The separate qiven-host broker program is sealed; ADR-0026's invariants
(single-writer lease, monotonic fencing epochs, fail-closed quarantine,
reconciliation, bounded execution journal) are absorbed as
RuntimeHost-internal subsystem semantics behind
`IExecutionAuthorityPort` in qiven-runtime. Machine-local governed
mutation means: through the RuntimeHost execution-authority subsystem
(Runtime real-adapter batches). A direct mutating path around
RuntimeHost remains a safety defect. Do not trust conversational
singularity, UI state, or caller self-declaration as proof that JasonPC
is free of a competing execution flow.

## Operator-facing Git validation commands

For commands handed to the user or executed through an accepted host-authority path during Chat-mode validation, prefer non-interactive checks such as `git diff --check`, `git diff --cached --check`, explicit clean-tree verification, and exact `git rev-parse HEAD` verification. Do not ask the user to run raw `git diff` or `git diff --cached` merely for review: Git may invoke a pager and appear to hang in Windows CMD, and exact remote diff review is the reviewing session's responsibility.

If a full local diff is genuinely required for diagnosis, make the non-paged behavior explicit (for example `git --no-pager diff ...`) or capture the output deliberately. Do not silently rely on pager interaction as part of the user's validation workflow.

For batch completion, required machine-local validation may be performed by the project owner through a trusted local path or, after ADR-0026 acceptance, through the broker-enforced local execution path. Under the standing authorization recorded in ADR-0021, the session may merge the exact validated batch head to `main` after exact remote review and any additional required batch gates pass. A separate user relay message is not required when the session directly observes exact-head validation evidence through an accepted authority path. If the branch changes after the validated head, the changed head must be validated again before merge. The user may revoke or narrow this authorization at any time.

## Commit identity attribution

Git author/committer identity on Qiven repositories is the machine's configured
account (currently `JasonHuang` under the `github:JasonHuang3D` principal). An
LLM participant cannot self-provision an SSH/GitHub identity, so the account
identifies the machine and the governance principal — not the authoring
identity of the turn that produced a commit. Branch namespaces may still
express identity, but they are no longer its sole carrier: identity survives
merge only inside the commit message.

Every commit authored by an LLM participant therefore carries an attribution
trailer block as the LAST block of its message, after the conventional subject
and body:

```text
<conventional subject>

<body ...>

role: <authoring designation>
LLM: <serving model>  reasoning <level>
```

The conventional subject line stays first: `git log --oneline`, Forge commit
listings and merge notifications render the subject, so attribution must never
displace the engineering summary.

- `role` is the designation in effect for the authoring turns: a canonical role
  (`jason-brother`, `jason-worker`, `owner`) or an owner-granted session
  designation (for example `jason-extended-cognition`).
- `LLM` names the model that actually served the authoring turns; `reasoning`
  records the serving reasoning effort (for example `max`, `high`,
  `standard`). The ADR-0035 rule-4 disclosure duty applies unchanged: a
  served-model substitution is disclosed here, never silent.
- The trailer is attribution provenance, not an authority claim. Authority
  still flows from the governance principal, the active ContextView binding,
  and the governing policy gates; a trailer naming a role does not grant that
  role's authority and never substitutes for typed handoff evidence (H1-H4).
- Human-authored commits are exempt. When several models contribute to one
  transaction, each contribution is disclosed in the trailer or, when the
  split is material, in the session checkpoint.

Accepted 2026-09-19 by the project owner after the
`jason-extended-cognition/v3-design` commit on `qiven-context-draft`
demonstrated the format. Recorded as `MEM-20260919T113238Z-B2F4D8`.

## Long-running and unattended windows (ADR-0044 era)

The historical "Overnight unattended mode" section is superseded
(2026-09-22 owner direction): the overnight/standing-window concept and
the supervised long-running session mode are unified as ONE workflow —
`views/workflows/long-running.md` ("continue unless H1"). Its contract
anchor is the Long-running mode section of
`collaboration/human-handoff-boundary.md` (per-batch H2
standing-delegated with receipts and escalation duties; governance,
ADR acceptance and qualification upgrades remain owner H2; H1/H3/H4
unchanged). The original overnight practice (2026-09-19/20) is
historical evidence for that workflow.
