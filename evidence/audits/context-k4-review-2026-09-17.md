# ContextKernel K4 engineering review and remaining acceptance gate

## 2026-09-18 semantic correction notice

This audit preserves the review state as it existed on 2026-09-17, but its original
statement that the then-current `tests/cold-boot/k4-candidate-prompt.md` was sufficient
for **formal K4 acceptance** is superseded by the later semantic-drift review,
ADR-0034 and `collaboration/context-handoff-contract.md`.

The earlier challenge inherited the remote-cold-boot topology: the fresh agent could
fetch the K4 candidate and perform export/restore itself. A PASS under that topology
may remain evidence of remote Project Continuity, but it cannot prove that the
canonical export/handoff artifact itself caused continuity. K4 now requires an
independent producer, one self-describing handoff artifact, isolated artifact-only
fresh-consumer Phase A, and only afterward Phase B live verification.

See `evidence/audits/context-k4-handoff-drift-review-2026-09-18.md`. This correction
does not rewrite the historical fact that no fresh-LLM trial had run when the review
below was authored, and it does not claim K4 PASS.

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

## Formal acceptance remains separate — historical wording

At the time this section was written, `collaboration/project-continuity-acceptance.md`
and ADR-0033 were interpreted to require a fresh capable LLM/agent session with no
prior Qiven conversation to reconstruct project cognition, and the then-current
`tests/cold-boot/k4-candidate-prompt.md` was identified as the runnable challenge.
A new Python process was correctly recognized as insufficient cognitive evidence.

The 2026-09-18 correction above narrows the disposition: fresh-session reconstruction
is still required, but K4 specifically requires the Canonical Artifact Handoff
delivery profile rather than a remote cold boot. The current Phase-A/Phase-B prompts
replace the historical challenge for K4 acceptance.

Keep the implementation on its remote feature branch until the corrected gate passes.
The accepted main checkpoint remains K3. Do not claim K4 accepted, select production
storage, resume Host, perform shadow dual-write or cut over authority. No routine
per-commit owner permission is required for the already authorized engineering
implementation, but the independent producer/artifact/consumer acceptance topology
must not be collapsed.
