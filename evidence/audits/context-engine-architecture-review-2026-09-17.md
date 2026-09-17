# Context Engine architecture re-review — 2026-09-17

## Scope and authorization

The original local proposal was `1be137670cb2d50938fbb82cba5fb409e8e453b4`,
based on canonical R2 main `8f55259d99ea2a47e465a2604d2f22765a217bf6`.
Re-review identified five semantic gaps and two implementation-boundary issues.
The user explicitly agreed to revision and authorized direct push plus merge
after revision. The GitHub connector authenticated `JasonHuang3D`, the current
root principal under ADR-0031. This is account-level, not biological identity.

## Review disposition

| Finding | Resolution in ADR-0033 | Required future proof |
| --- | --- | --- |
| Bundle authorization exception | Section 6 forbids exceptions; separate operation envelope | K3 constant not_granted and independent execution admission |
| Ambiguous commit outcome | Sections 4/5/9 define atomic receipt/key/head publication and result lookup | K2 lost acknowledgement, restart and same-key races |
| Authorization/commit gap | Section 4 binds full request and requires old-policy admission and live checks | K2 revoked/stale/mismatched grants and self-authorization rejection |
| Digest cycle and imported authentication | Sections 2/3 define acyclic hash dependencies and explicit historical unknowns | K1 golden vectors and exact import provenance |
| Export availability versus determinism | Section 10 separates semantic and package manifests, completeness and quarantine | K4 availability, corruption and partial-recovery fixtures |
| View versus Bundle inputs | Section 7 separates view resolution from complete query/config-driven construction | K3 deterministic replay and budget/constraint parity |
| Oversized initial batch | Section 12 defines K1-K4 with individual gates | Separate exact-batch acceptance evidence |

## Acceptance limits and validation gate

Acceptance is for semantic architecture, not an implemented ContextKernel.
Existing portable regression tests validate repository consistency and existing
read behavior; they do not prove the new transaction, hashing or restore design.
No runtime code is changed. Architecture obligation OBL-20260916T125000Z-5A8C31
closes; K1 has not started. GitHub remains canonical and Host/DCR pauses remain.

Publication requires repository validation, diff whitespace validation and all
11 portable suites on the immutable revised candidate. The Windows-only suite
is inapplicable to this documentation/state-only change. Exact validation results
and publication identities are recorded in the publication commit/PR evidence.
Remote content must match the locally tested tree before canonical ref movement.
No force update or high-level GitHub contents mutation is permitted.
