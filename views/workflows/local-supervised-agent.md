# Local Supervised Agent Workflow (capability class: local_supervised_agent)

This profile instantiates Qiven's local-execution contracts for a
`local_supervised_agent` tool — a foreground, owner-launched agent session on
JasonPC with shell, filesystem, Git, and authenticated `gh` reach (currently
ZCode desktop under `ContextView<ZCode, Jason>`). It is the capability-class
generalization of the ChatGPT view's Human Manual Mode: the human relay step
disappears because the agent is already local, but every engineering semantic —
exact identity, fail-fast gates, truthful liveness, bounded waiting, cleanup —
is inherited unchanged from the canonical contracts.

## Z1 — Supervised foreground execution (active)

The session runs where the owner can see and gate it. Rules:

1. **Mutating actions pass the session permission surface.** The owner launched
   the session and sees each action; a denied permission is a boundary and must
   be stated as such, not circumvented (same rule as the connector boundary in
   `collaboration/operating-contract.md`).
2. **Operator is still the engineering interface.** When a declared task/gate
   exists (`.qiven/operator.json`), prefer invoking it over ad-hoc chains.
   Machine view (`--json`) is legitimate for an agent caller; human view with
   `--verbose` remains required for owner-run acceptance gates such as the K4
   producer (that is an H1 handoff and stays with the owner per
   `collaboration/human-handoff-boundary.md`).
3. **Unattended automation is read-only by default.** Scheduled, idle-time, or
   background executions may read, retrieve, analyze, and rebuild bounded
   derived artifacts. They must not push, create PRs, merge, run acceptance
   roles, or touch governance. Local commits are permitted only inside an
   explicitly authorized task scope. See ADR-0036 and
   `collaboration/human-handoff-boundary.md`.
4. **Worker discipline by default.** No push, PR creation, or merge without
   explicit per-task owner authorization. A separately accepted standing
   authority may later widen this, mirroring the ADR-0021 requalification
   pattern; that widening is an ADR-level event, not a view-level default.
5. **Single-writer approximation.** Two agent sessions must not share one
   working copy concurrently. Concurrent sessions need separate worktrees or
   clones; canonical serialization goes through remote review until the Host
   broker exists. The 2026-09-16 split-brain incident is the governing evidence.
6. **Exact-head and precise-path discipline.** Validation and review bind to
   exact SHAs; a changed head revalidates. Publication uses precise low-level
   paths (`git push` of a named branch, `gh pr create`) — never ad-hoc
   contents-API writes as merge surrogates.
7. **Asynchronous CI and bounded waits are inherited verbatim** from
   `collaboration/session-ci-handoff-contract.md`: one immediate exact-identity
   status read after dispatch, no sleep/poll loops, bounded-wait default of
   three observations / 60 seconds.

## Typical loop

```text
authorize task (owner)
  -> local branch zcode/<name>
  -> implement; run gates (bootstrap/full-tests/diff-check/clean-tree)
  -> one coherent commit; exact head reported to owner
  -> owner review (H2), push, PR, merge on owner confirmation
  -> reconcile local main; cleanup per git-workflow.md
```

The owner review (H2) is satisfied by an explicit conversation confirmation or
by the owner merging in the GitHub UI; both are equivalent evidence for the
same exact delta.

## Z2 — Host-mediated execution (unchanged, fail-closed)

Workflow 2 semantics from `views/workflows/chatgpt-jason-local-execution.md`
apply unchanged: broker-mediated mutation waits for ADR-0026 Batch 001
acceptance and explicit re-enablement (`OBL-20260915T163500Z-9D4C72`). A local
supervised agent must not treat its foreground presence as a Host substitute.

## Environment binding

Uses `views/environments/jasonpc.yaml` and the view's human preferences
(`views/humans/jason.yaml`). Exact tool versions, interpreter paths, and VPN
state are live facts verified when a task depends on them. The DCR-specific
shell/SSH environment facts in `collaboration/dcr-operational-contract.md`
remain the reference for any future DCR transport work, not for this profile.

## Current state

Z1 is active for authorized tasks. Z2 remains fail-closed. Unattended
automation remains read-only by default.
