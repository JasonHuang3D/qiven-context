# Agent Execution Topology and Session/Turn Semantics

Normative semantic alignment between the human owner and LLM agents
(owner direction 2026-09-24, v26 session; the ZCode+Windows+GLM
instantiation is described concretely, the layer semantics are
platform-general). Companion to `collaboration/context-checkpoint.md`
(session/turn identity) and the operating contract's session-identity
section. Nothing here overrides typed-handoff or authority rules.

## 1. The topology (control authority is NOT cognition flow)

Two different arrow systems exist. Control authority points DOWNWARD
from the owner; cognition flows through the LLM, which holds NO
downward authority of its own — only the per-call tool surface the
harness grants.

~~~text
CONTROL AUTHORITY (each layer owns the one below it)
JasonPC hardware
 └─ Windows OS
     │  process tree · Job Objects · power transitions (Modern Standby)
     │  Task Manager · reboot/sleep
     └─ ZCode desktop agent (OS process family)
         │  UI: session list. "Close" = ARCHIVE (data preserved;
         │  session.time_archived is set). Delete = data removal under
         │  <agent-state-dir> (the platform state dir under the user
         │  profile; placeholder per public-repo information hygiene).
         │  No physical process ends at archive.
         │  Store: cli/db/db.sqlite (session/message/part/todo/...);
         │  a session ROW materializes at FIRST INPUT SEND
         │  (measured 2026-09-24: created ≈ first message, <0.2 s;
         │  an unsent draft creates no session row).
         │  Workspace hooks load at SESSION START only
         │  (.zcode/config.json snapshot; a mid-session flip changes
         │  nothing for the running session).
         │
         └─ harness (inside the agent)
             │  tool execution: Bash/Read/Write/Edit/TaskStop/... —
             │  the ONLY control surface granted to the LLM, per call.
             │  background tasks (run_in_background): harness child
             │  processes; each returns an output-file path immediately
             │  and re-invokes the model EXACTLY ONCE on completion —
             │  delivered as a turn-tail wake-up while the session
             │  lives. TaskStop tree-kills a task (the one lifecycle
             │  lever the LLM is granted, for its own tasks only).
             │  PreToolUse hook router (qiven) sits BETWEEN the model's
             │  call and the tool: deny-with-instruction is the only
             │  hook power (no call rewriting).
             │
             └─ granted per-call control ──▶ OS child processes
                  (bash.exe, gates/MSBuild, sleep.exe probes,
                   qiven-runtime-host, python, ...)

COGNITION FLOW (no authority travels along these arrows)
owner input ─▶ LLM (GLM-5.3 via provider API)
               │  STATELESS per call: every call — including every
               │  tool-call boundary — is a fresh model instance.
               │  In-conversation continuity = full context replay +
               │  KV-cache prefix hits. Nothing persists inside the
               │  model; "session"/"turn" reach it only as prompt
               │  content. This is exactly why Qiven exists: external
               │  continue cognition for requirements harsher than any
               │  in-conversation mechanism can meet.
               └─▶ tool calls ─▶ OS processes ─▶ results/notifications
                     ─▶ back up to the LLM ─▶ response to the owner

OWNER LEVERS (none of them LLM-reachable): every input prompt · UI
archive/delete · app quit · Task Manager kill · OS sleep/reboot.

EXTERNAL CONTINUE COGNITION (Qiven — wraps the entire stack above):
qiven-context · qiven-docs · views · session checkpoints. Survives app
quit, OS reboot, session deletion, LLM/provider replacement. Project
cognition is independent of every layer above by design.
~~~

## 2. Session and turn — the aligned semantics

- **Session** = the conversation object in the agent UI (one
  continuous thread). Store evidence: the session row materializes at
  first-input send; archive is data-preserving; deletion removes data.
  A session "exists" from its first sent input until its data is
  deleted — nothing else.
- **Turn** = one owner-input/response cycle. Precise boundary (owner
  direction 2026-09-24): a turn N spans from human input N being
  **sent** until human input N+1 is **sent**. Everything in between —
  including harness notification wake-ups (a background task
  completing re-invokes the model), sub-agent activity, and additional
  assistant response blocks the UI renders — is **turn-tail
  continuation of turn N**, not a new turn. UI rendering blocks are
  not turn boundaries.
- **"Close the session" in owner vocabulary** = "I stop giving input
  prompts to this session." It implies NO UI archive, NO deletion, and
  ends no process. The next session (a cold boot) begins at its own
  first input. Agent records must use this meaning; writing "session
  closed" records intent (per context-checkpoint.md), never a physical
  event.

## 3. Background-process lifetime — the reframed question

The former question "does a background task survive its SESSION" was
ill-posed under this topology: operational session end (stop inputting)
kills nothing — the conversation object and its process tree simply sit
there (P4B/P4C/P4D all completed naturally while their session
received no input, each re-invoking the model once). The real lifetime
boundaries are **physical lifecycle events**: application quit,
OS power transition, and owner manual kill — none LLM-controllable,
and the first two are the owner's routine levers. The v25 probe death
inside the awake window 2026-09-23T23:05–23:23Z is therefore attributed
to application-quit-class events (not further probed).

Consequence for ADR-0051 residual R1 (recorded in OBL-D5E6F7's
closure): sweeps and every survival-requiring run stay **terminally
exec-lease-routed** — Operator custody (detached, watchdog + Job
Object + lease) is the only mechanism in this topology that survives
application quit AND OS power transitions. No probe can change that;
the probe chain was terminated at owner direction 2026-09-24 (P4E
TaskStopped; the LLM's one granted lever, used on its own task).

## 4. Evidence anchors (2026-09-24)

- Store forensics (read-only): `cli/db/db.sqlite` — session rows
  created ≈ first message (<0.2 s across sampled sessions);
  `time_archived` a separate, nullable column; `tasks-index.sqlite`
  holds automations, not conversations.
- Probe family: P1/P2/P3/P5 (v25, proven); P4B 11:08→11:38Z, P4C
  11:31→12:01Z, P4D 12:01:08→12:31:08Z (DONE verified) — all natural
  in-session completions while no input arrived, each delivered one
  completion wake-up; P4E armed 12:32Z, TaskStopped at owner
  direction.
- Power forensics: Kernel-Power 42/107/187 + Power-Troubleshooter Id=1
  (MEM-20260924T113500Z-D8E9F0) — OS transitions are owner levers
  invisible to boot-class queries.
- Hook loading: config flip at 11:43:32Z did not arm the router in the
  session started at 10:23:57Z (session-start snapshot semantics;
  router logic independently verified healthy).
