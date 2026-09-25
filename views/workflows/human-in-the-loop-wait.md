# Human-in-the-Loop Wait (ZCode Desktop)

> Status: workflow pattern under its contract carrier (owner direction
> 2026-09-26): the governing clause is `collaboration/operating-contract.md`
> §"Waiting on humans or external events". Scope: ZCode Desktop harness
> only; other agent families are untested. The contract clause changes no
> authority boundary (H1/H2 and typed handoffs are unaffected; a wait is
> not a handoff).

## The rule

When a step needs a human action or an external event before the LLM
can continue, the session uses exactly one of:

| Situation | Mechanism | Why |
| --- | --- | --- |
| The trigger is the owner replying ("I clicked", "done", an answer) | `AskUserQuestion` with the instruction as the question | The tool blocks; the turn suspends; the LLM resumes with the answer verbatim. No polling, no races. |
| The trigger is machine-observable (file appears, process spawns, port listens, log line) | A `run_in_background` watcher command that exits when the condition holds; end the turn; the harness notifies once on completion | The watcher sleeps, not the LLM. Same notification-once law as ADR-0051 background execution. |
| Both (human acts, machine observes the effect) | AskUserQuestion for the human part; the watcher armed beforehand or on resume confirms machine-side evidence | Keeps the human promise and the machine evidence separately attributable. |

## Watcher shape

```bash
# exits 0 exactly when the evidence file is non-empty, then prints it
while [ ! -s /path/to/evidence.jsonl ]; do sleep 2; done
cat /path/to/evidence.jsonl
```

- Always `run_in_background: true`; the harness returns an output-file
  path immediately and notifies once.
- Never poll from the foreground; never read a file a concurrent
  writer may be mid-writing from a poll loop (partial-read/TOCTOU).
- Bound the watcher itself (`for i in $(seq 1 150)` ~ 5 minutes at
  `sleep 2`), and let a timeout exit non-zero with a marker line so
  the notification distinguishes "event happened" from "gave up".
- Record the watcher task id (full `exec_<8hex>-<uuid>`); stop it with
  the full id if abandoning, and sweep for wrapper stragglers.

## AskUserQuestion shape

- The question carries the paste-ready instruction (what to click,
  what to send, what NOT to do - e.g. "do not log in any real
  account"), not a bare "ready?".
- Options enumerate the honest outcomes: done / failed / abandoning.
- The turn must not hold other work hostage while asking - ask as the
  last action of the turn; resume on the answer.

## Anti-pattern (forbidden)

Foreground `sleep`-loops that poll a file or process from inside the
turn. They hold the turn, race concurrent writers, emit heartbeat
noise, and multiply context cost per poll. (Observed once in v30:
12x20s loop watching an event file; it worked by luck and was
immediately ruled out by the owner.)

## Relationship to existing law

- A wait never substitutes a typed handoff: H1 remains H1 even if the
  session "waited" through it; the wait only structures turn timing.
- Background watchers inherit ADR-0051: inherently-terminating
  commands, no polling supervision, notification-once, TaskStop
  tree-kill with full task ids.
