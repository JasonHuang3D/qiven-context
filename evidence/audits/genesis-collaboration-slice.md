# Genesis Import Audit — Collaboration / Git / CI / Worker Protocol

## Scope

This slice reconstructs Qiven's collaboration authority model, Work-mode Git boundary, local validation profiles, manual GitHub CI policy, and two previously deferred CI follow-ups.

## Sources reviewed

Primary committed evidence:

- `JasonHuang3D/qiven-foundation@f1880847e046425c7f3f3cad22a07d0008aad359:AGENTS.md`
- `JasonHuang3D/qiven-foundation@f1880847e046425c7f3f3cad22a07d0008aad359:docs/engineering/worker-protocol.md`
- `JasonHuang3D/qiven-foundation@f1880847e046425c7f3f3cad22a07d0008aad359:.github/workflows/ci.yml`
- `JasonHuang3D/qiven-math@912ae067784fb5cd336925ff6f6d071b85297bff:.github/workflows/ci.yml`
- `JasonHuang3D/qiven-devkit@214dc5c933ef4f7db3fce9795a39d49ca382dfbf:.github/workflows/ci.yml`
- `JasonHuang3D/qiven-context@9cb7c45fbaf679970e2429fd73bd3aa9450a446b:collaboration/operating-contract.md`

Retrospective evidence:

- prior-session reconstruction of worker-protocol hardening;
- prior-session reconstruction of non-blocking CI observations.

Retrospective evidence was not treated as verbatim. Where possible it was corroborated by committed repository state.

## Promoted canonical records

- `ADR-0004` — separate architecture/release authority from local implementation execution;
- `ADR-0005` — select GitHub CI validation explicitly after remote review;
- `ADR-0006` — FULL local validation by default, FOCUSED only by explicit CTO scope;
- `MEM-20260913T180134Z-E3C993` — codify recurring workflow ambiguity rather than leaving it to session memory;
- `OBL-20260913T180134Z-C1A771` — verify real GitHub Actions concurrency cancellation;
- `OBL-20260913T180134Z-D2B882` — improve skipped matrix-job naming when CI presentation is next touched.

## Rejected or non-promoted candidates

- The exact historical date on which each collaboration rule first became accepted was not reconstructed because the current evidence set does not justify precise timestamps.
- Individual branch examples and transient batch-size examples remain in repository protocol evidence rather than becoming separate canonical memories.
- The implementation worker's complete procedural checklist was not duplicated into qiven-context because the committed Foundation protocol already remains the authoritative repository-local execution contract.

## Residue pass

Explicit deferred/non-blocking residue recovered in this slice:

1. real concurrency cancellation behavior has not received a dedicated overlapping-run acceptance test;
2. skipped matrix job naming/presentation can be confusing and should be reconsidered only when that CI area is next touched.

No additional collaboration-domain residue from the reviewed evidence was promoted in this slice.

## Gaps

The historical raw chat transcript that originally produced every worker-protocol revision is not fully available as a single verbatim evidence artifact in this import pass. The accepted rules are nevertheless strongly corroborated by the committed agent/worker protocol and current operating contract. Exact historical rationale beyond those committed documents remains recoverable only to the extent preserved by retrospective conversation context.
