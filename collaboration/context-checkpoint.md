# Context Checkpoint Protocol

This v2 protocol is a compatibility entry point. The normative transaction model is `collaboration/context-operating-model.md`.

**Session vs turn identity (owner direction 2026-09-23; correcting the v18/v19 misnumbering; refined 2026-09-24):**

- A **SESSION** is one continuous conversation thread with the owner —
  same thread and context, no cold boot in between. A **TURN** is one
  owner-message/response cycle inside a session. A session may span
  calendar days and many turns.
- **Turn boundary precision (owner direction 2026-09-24):** turn N
  spans from human input N being SENT until human input N+1 is SENT.
  Everything in between — including harness notification wake-ups (a
  completed background task re-invokes the model) and additional
  assistant response blocks the UI renders — is turn-tail continuation
  of turn N, not a new turn.
- **"Closing a session" in owner vocabulary (owner direction
  2026-09-24)** means "no further input prompts will be sent to this
  thread." It implies no UI archive, no deletion, and ends no process;
  the session row persists until its data is deleted. Store evidence:
  a session materializes at first-input send (<0.2 s), archive is a
  separate data-preserving operation. Full topology and semantics:
  `collaboration/agent-execution-topology.md`.
- A new session begins ONLY when (a) the owner explicitly marks it
  (e.g. "这是新session"), or (b) a fresh cold boot occurs (new
  conversation/context). The agent NEVER infers or increments session
  identity on its own — not from date changes, not from "session
  closed" phrasing, not from task completion. Declaring a session
  closed in a checkpoint records intent, not identity: if the owner
  keeps writing in the same thread, the SAME session continues and its
  checkpoint is extended (addendum sections), not succeeded.
- Checkpoint files: ONE per session, named
  `sessions/<session-start-date>-qiven-v<N>.md` (the date is the
  session START date even if the session spans days). Turn content is
  appended as addendum sections ("Turn N (date): ...") to the session's
  file across the session's context transactions. N increments only at
  a true session boundary.
- Incident record: the files museumed as
  `legacy/sessions/2026-09-23-qiven-v18-turn-file.md` and
  `legacy/sessions/2026-09-23-qiven-v19-turn-file.md` were created by
  the agent on turns of the v17 session (definition postdates them);
  their content is consolidated into
  `sessions/2026-09-22-qiven-v17.md` (owner direction 2026-09-23) and
  the copies are sealed history. Renamed `*-turn-file.md` so their
  numbers are not mistaken for real session ordinals — the
  owner-designated NEXT real session is **v18** (fresh conversation,
  2026-09-23). Do not renumber history.

**Checkpoint purpose (owner clarification 2026-09-22, MEM-20260922T184000Z-F2A3B4):** a session checkpoint is **turn-interruption insurance** — it bounds the loss when a turn ends unexpectedly (network drop, accidental stop, harness or provider failure) so the next turn or cold boot resumes from recorded state. Refresh is **event-driven** (material boundaries: candidate staged, gate run, publication, blocker, next-action change), **never time-budgeted** — no turn-duration limit exists for Qiven to plan around — and **not coupled to batch planning or development milestones**; project recovery itself runs through canonical state plus cold boot.

A context checkpoint is created only for a material context transaction; ordinary turns do not require one. There is no mandatory all-category Memory Delta and no manual ledger dual-write.

The checkpoint sequence is: verify live evidence; classify durable cognition; reconcile lifecycle/conflicts; update only affected canonical records and audits; update compact operational state; update the current session checkpoint; validate schemas and v2 repository invariants; validate affected derived tooling; commit the coherent context transaction.

If an asynchronous external job remains nonterminal, persist exact correlation identity and return control rather than blocking the interaction on polling (bounded-wait rules in `collaboration/session-ci-handoff-contract.md`).

Historical `templates/MEMORY_DELTA.md` is retained only as a legacy capture worksheet; it is not a required transaction artifact.
