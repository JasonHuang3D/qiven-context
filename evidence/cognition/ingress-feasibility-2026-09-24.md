# Harness Ingress Feasibility — ZCode pre-design model-visible delivery (CA-0)

CA-0 exit-gate item (roadmap §4 CA-0): "inspect the real ZCode harness and
any approved orchestrator for a model-visible pre-design ingress with
task/invocation capture; distinguish SessionStart/tool interception from
input delivery and record a feasibility proof or blocker before promising a
before-design gate."

Verdict: **FEASIBLE with a named residual** — a documented, partially
observed model-visible input channel exists (`additionalContext` injection
at `SessionStart`/`UserPromptSubmit`); its live injection in THIS workspace
still needs an owner-enabled hook configuration (enable-gated per ADR-0049
workspace law), for which the paste-ready trial is specified below. This is
a proof with a bounded qualification step, not a blocker: sequencing does
NOT re-deliberate, and the before-design claim remains gated on CA-2's
qualified trial.

## Evidence (three layers)

1. **Documented harness contract.** The ZCode hook system (official
   zcode-guide plugin, diagnosing-hooks skill, v0.3.0,
   `.../zcode-guide/0.3.0/skills/diagnosing-hooks/SKILL.md`) specifies:
   - exactly seven hook events: `SessionStart`, `UserPromptSubmit`,
     `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PostToolUseFailure`,
     `Stop`;
   - hook stdout is parsed as JSON (strict schema) OR exit codes: 0 pass,
     2 block (deny for PreToolUse/PermissionRequest);
   - **"`additionalContext` is injected into the conversation"** — i.e., a
     hook can ADD model-visible input;
   - template variables `${ZCODE_SESSION_ID}` etc. are injected as
     environment variables — invocation-identity capture exists;
   - execution outcomes (fired/timed out/blocked, duration, error preview)
     are recorded in the ZCode log — an observation/capture surface.
2. **Live observation in this harness instance (2026-09-24, v23).** A
   `PreToolUse` (Bash) hook denial — exit 2, stderr text, provenance-tagged
   `[qiven-hook]` — reached the model verbatim as tool-result feedback (the
   devkit hook router denial observed at cold boot). This proves the hook
   → model-visible-text path for TOOL-INTERCEPTION feedback in this exact
   workspace.
3. **Residual (not yet observed live).** `additionalContext` injection at
   `SessionStart`/`UserPromptSubmit` has not been observed in this
   workspace: the only enabled configuration hook today is the PreToolUse
   Bash router, and adding an ingestion hook requires the owner-enable gate
   (ZCode UI review; ADR-0049 precedent — the session may write the config,
   the UI review enables).

## The distinction CA-0 requires (SessionStart/tool interception ≠ input delivery)

- `PreToolUse` denial text is FEEDBACK AFTER a tool call — it cannot
  precede a design and does not qualify as before-design delivery.
- `SessionStart` (matchers: startup/resume/clear/compact) and
  `UserPromptSubmit` fire BEFORE the model responds to the session's first
  task prompt; a hook emitting `additionalContext` there delivers input
  into the conversation ahead of the first design output. THAT is the
  model-visible pre-design ingress.
- Design-entry observability: the harness fires the hook at a defined
  event; the delivery record (hook run in the ZCode log + the bundle digest
  inside the injected context) binds delivery to a time BEFORE the first
  model response to the task prompt. What the harness cannot observe is
  "design start" semantics inside the model — hence CA-2's rule: capture is
  at task-entry (prompt submit), and any claim of before-DESIGN delivery is
  bounded by that capture, with unobserved entries recorded as coverage
  gaps (CG-2).

## Controlled ingress design (for CA-2 qualification)

```jsonc
// workspace .zcode/config.json (owner-enable-gated), hooks.events:
"UserPromptSubmit": [ { "hooks": [ {
  "type": "process",
  "command": "<repo-root>/.qiven/cognition/qiven-cognition-ingest.cmd",
  "args": [], "timeoutMs": 2000,
  "statusMessage": "task cognition preflight"
} ] } ]
```

The process hook (a thin wrapper over the future `qiven cognition prepare`
one-shot, CA-1): reads the prompt payload on stdin, derives the neutral
task envelope from mechanical facts (declared repository/revision, changed
paths where derivable, phase/risk only if declared), builds/selects the
pinned TaskCognitionBundle, and prints strict-schema JSON:

```json
{ "hookSpecificOutput": { "hookEventName": "UserPromptSubmit",
  "additionalContext": "<rendered bundle + receipt header>" } }
```

- Bounded: timeoutMs 2 s; on any failure the hook emits NOTHING (exit 0,
  empty) — the gate must not block ordinary prompts while unqualified
  (shadow mode, roadmap §8.1); blocking semantics arrive only with CA-2's
  publication gates.
- Capture: `${ZCODE_SESSION_ID}` + bundle/receipt digest ride the injected
  header; the ZCode hook log records the run; `qiven cognition
  verify-receipt` (CA-2) closes the loop.
- Ordering proof for CA-2: the injected context precedes the model's first
  response to the submitting prompt by harness construction; the trial must
  still CAPTURE this (log timestamps + output inspection), per "a
  harness delivery record ... is needed to claim that the bundle reached
  the consumer before the phase began" (CG-2).

## Owner paste-ready live trial (H1-preparation duty; the enable is owner-H1)

1. Owner reviews the added hook block in ZCode settings (UI review = enable
   gate).
2. Fresh session; first prompt: any ordinary engineering question.
3. Observe: the model's context contains the injected bundle header
   (visible when the model cites the receipt), and the ZCode log shows the
   hook fired with `additionalContext`.
4. Rollback: remove the hook block (one settings edit); nothing else
   changes (the hook is read-only ingestion).

## Non-goals

This record does not claim: comprehension (receipt ≠ understanding, CG-11);
coverage of uninstrumented entry paths (each is a coverage gap, CG-2);
blocking authority (CA-2 scope); or orchestrator-based R3 isolation (the
ADR-0050 amendment classes — a separate orchestration boundary, not the
workspace hook).
