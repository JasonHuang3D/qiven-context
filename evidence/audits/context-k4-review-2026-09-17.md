# ContextKernel K4 engineering review and remaining acceptance gate

## Scope and K3 review

The owner reported K3 completed in another account and authorized continuation.
The live main was K3 merge `e0a6f46c5c9da4d9eb1ce57cb6b4a467f4b195c5`,
following K2 merge `6e0bcb01b9f7d008c0c09b6d01972e879bb3566e`.
K3's immutable source projection, shared compiler, view and ranking bindings and
193-test evidence were reviewed. No blocking K3 architecture reversal was found.

K4 implements canonical export/restore, exact closure/integrity validation,
completeness diagnostics and engineering continuity tests under ADR-0033. The
important operational correction is explicit: restoring canonical committed history
does not reconstruct all in-flight/rejected key reservations. Restored instances
therefore retain committed receipts but persistently reject new writes. This
prevents accidental key reuse while retaining the single-authority migration rule.

## Engineering gate

The reviewed implementation candidate must pass the integrated portable runner,
repository validation and a new-process restore/read comparison before it is
reported as engineering-complete. Exact candidate, totals and raw log will be
recorded after execution. This document is not yet a PASS claim.

## Formal acceptance remains separate

`collaboration/project-continuity-acceptance.md` and ADR-0033 require a fresh capable
LLM/agent session with no prior Qiven conversation to reconstruct project cognition.
A new Python process proves data/read isolation only. No fresh-LLM trial has been
run in this authoring session; it must not be manufactured from the author's own
knowledge or an automated replay. The exact runnable challenge is
`tests/cold-boot/k4-candidate-prompt.md`.

Keep the implementation on its remote feature branch until that gate passes.
The accepted main checkpoint remains K3. Do not claim K4 accepted, select production
storage, resume Host, perform shadow dual-write or cut over authority. No user
permission is needed for the already authorized engineering implementation, but a
truthful independent continuity execution is still required for acceptance.
