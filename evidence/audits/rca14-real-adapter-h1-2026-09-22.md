# RCA-14 Real-Harness Adapter Conformance — H1 Acceptance Record

> **Redaction 2026-09-24** — public-repo information hygiene:
> machine-identity literals replaced with placeholders; originals
> remain in git history. Findings unchanged.

## Classification

- Delivery profile: **real-harness adapter execution** (H1-designated,
  owner hands, 2026-09-21 designation; executed 2026-09-22).
- H1 evidence: owner attached the workspace hooks (client config, owner
  hands), started a NEW session (hooks do not hot-reload), drove real
  Bash tool calls, and relayed the evidence dump back VERBATIM twice.
  Owner confirmation in conversation ("看来成功了").

## Grading against the conformance rubric

Real-traffic PASS: F2/F3 (§14 completeness + materialization; three
proposals accepted, each with a DISTINCT verbatim payload sha256 —
per-call sensitivity on real hook payloads), F5 (§46 single correlated
observation; two real duplicates correctly rejected), F6/C-14
(§15 tri-state mapping: `observation 1 succeeded exit 0` from exit-code
facts), F8 (§13 activation: `activation 1 session-start`), F9 (§42
window declared via the CLI).

Test-level (not exercised by this run, proven in
qiven-runtime tests): F4 immutability, F7 claim routing, and the
Indeterminate leg of F6.

## Sealed evidence (owner relay, verbatim, second run)

```text
bridge-state <workspace-root>/qiven-runtime/.generated-temp/adapter-bridge/real-session.log
activation 1 session-start
proposal 1 Bash session 1 sha256 70c66938e307f96fefc0d47aefb992c96bbf44b223147a82fb8e5d71576125da
observation 1 succeeded exit 0
proposal 1 Bash session 1 sha256 abf8530d0ee8db581a0fd3a6888e73f16517abb940fe3de7efd529ad24ebcb0b
rejected-observation duplicate 1
proposal 1 Bash session 1 sha256 6e8d9ce85223f656e1c5c88abc2caa2a8ea25cae890e3a4686d0ca416102e999
rejected-observation duplicate 1
```

## Integrity cross-check

The owner's manual account (turn 2: one command; turn 3: two commands,
"certainly two") matches the ledger EXACTLY: 3 proposals + 1 accepted
observation + 2 §46 duplicate rejections. Per-event truthfulness of the
bridge ledger is thereby independently corroborated.

## Known day-one limitation (visible in the evidence, by design)

The kit's fixed `--action 1` correlates one proposal/observation pair
per session; subsequent observations are §46-rejected (`duplicate`).
Per-action correlation rides the hook payload once a stable event id is
available — recorded as follow-up work, not a defect.

## Verdict

**PASS.** RCA-14's real-harness execution is accepted: the four-channel
bridge, the verbatim digest binding, §46 single-observation and §15
tri-state all behave correctly on REAL harness traffic. Honesty scope:
the bridge ran advisory; no hard-enforcement claim about the real
harness exceeds this evidence. Component identity: qiven-runtime
`4c26bf2` (bridge + speak-fix), evidence produced by
`build/vs2022-x64/Release/qiven-adapter-bridge.exe`.
