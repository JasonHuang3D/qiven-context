# Current State

## Active objective

ContextKernel K3 is accepted on implementation candidate
`a8c817f3115c29e32ecb7c5a6bf00d03566b1761`: immutable kernel read projection,
resolved views, compatible queries/bundles, replay binding and full-envelope
protected budgets. Evidence: `evidence/audits/context-k3-review-2026-09-17.md`
and the 193-test log. No K4 implementation has started.

ContextKernel K2 is accepted on implementation candidate
`4e18ffadf6d112539e68fe2ba9e2e0413d6efa03`: immutable request identity, exact revision
preconditions, old-policy/live admission, atomic receipt/result/head publication,
idempotent retries and explicit unknown-outcome recovery. Evidence:
`evidence/audits/context-k2-review-2026-09-17.md` and its 175-test raw log.

The SQLite adapter is a restart-capable conformance mechanism in quarantined
reference namespaces, not a production storage decision. Child-process crash
fixtures prove the scoped recovery model. K1 import and historical unknown
provenance are preserved. GitHub remote remains canonical; no authority cutover.

R1, R2, K1 and revised ADR-0033 remain accepted. Under ADR-0032, jason-brother
validates portable Context Python/source-contract work directly in the agent runtime
without duplicate JasonPC validation. Machine-specific work still needs evidence
from its relevant environment.

## Accepted Context v2 operational checkpoint

- Context v2 and its post-v2 operating guardrails are canonical on `main`.
- The validated ContextView + Operator runtime candidate `a3ee448731ae26cce3cbf4afaa12d4d492769141` was accepted by canonical merge commit `35343c50c6df50d0ffc35664b24d029360787f35`.
- On 2026-09-16, Jason ran the declared Qiven Operator `cleanup-v6-temp` task from the long-lived `D:\JasonWork\qiven-context` working copy and reported `ALL PASS`.
- `OBL-20260916T102700Z-7C2A91` is complete. Normal validation uses the long-lived workspace plus Operator-owned scratch/worktrees rather than unmanaged ambient TEMP clones.

## Context authority and governance

- Canonical project cognition remains the GitHub remote; local repositories are non-authoritative working materializations.
- GitHub account-level identity remains the current governance authentication boundary.
- ContextView adapts interaction, environment, and workflow but cannot override identity-independent ProjectContext truth.
- Provider and consumer are semantic roles; human, agent, CI, repository, and runtime participants may occupy either role under explicit authority rules.

## ContextView<ChatGPT, Jason>

Workflow 1 remains active for JasonPC-dependent work. Portable Context Python/source-contract changes are implemented and validated directly by jason-brother under ADR-0032. Workflow 2 remains fail-closed until Host production authority is accepted.

## Safety and mutation guardrails

- `OBL-20260915T163500Z-9D4C72` remains open; mutating DCR/remote-AI execution on JasonPC is suspended.
- High-level Chat-side GitHub contents mutation remains unaccepted for critical writes. Low-level exact Git object/ref mutation is the admitted Chat-side critical-write path.
- The generic Operator packaging candidate in qiven-devkit remains unaccepted at `f5945df3c8c85b3fc49e228dcf7f88339567ff24`.
- The latest formally accepted Host checkpoint remains `8e5b9dec64bf739af84e981df12afc1969599738`, CI run `35060483714`. Corrected Host candidate `49e69c02fe2ded0b9607ccb4090c21cde96b8a1c` remains preserved and paused.

## Next boundary

K4 engineering implementation is on `jason-brother/context-k4`; it is not accepted.
Canonical export/restore and new-process reconstruction need their engineering gate,
followed by the fresh-LLM continuity trial required by ADR-0033 and
`collaboration/project-continuity-acceptance.md`. The exact challenge is
`tests/cold-boot/k4-candidate-prompt.md`. Canonical main remains at accepted K3 until
those gates pass. Restore grants no authority and enables no new writes.
