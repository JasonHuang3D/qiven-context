# Context Python Validation Authority

Accepted by the project owner on 2026-09-17 while authorizing R1 (C01-C06).
The acting architect/reviewer is the qualified session designated by the
active ContextView (ADR-0044; formerly the jason-brother role).

For qiven-context Python semantics, schemas and source contracts, the acting
session may implement, execute Python verification in the agent runtime, review
the exact published delta, and merge the validated candidate without duplicate
JasonPC validation. Run coherent batches and one integrated validation after
implementation; repeat only to resolve a concrete failure or validate a
materially changed candidate.

Record the candidate commit/source identity, interpreter/platform, executed gates,
results and excluded properties. Model doubles prove deterministic interfaces and
semantics, not ranking quality of downloaded models. Passing source/contract tests
does not establish arbitrary natural-language truth.

Use the normal portable test runner (`python tools/test_all.py`). Windows-only
entrypoint or resolver tests may be skipped on a non-Windows agent runtime when
those paths have not changed. Changes to Windows behavior, native tools, GPU,
performance or other machine-dependent properties require evidence from the
relevant environment; the owner remains the JasonPC execution authority.

This is a scoped exception to ADR-0021's machine-local validation requirement,
recorded in ADR-0032. It grants no DCR mutation authority, does not re-enable Host
Workflow 2, and does not waive exact candidate review or any task-specific gate.

## Acceptance-role clarification

"No duplicate JasonPC validation" applies to repeating portable Python/source tests.
It does not erase a machine, human, session or environment role that is itself part
of the property being tested.

In particular, K4 Canonical Artifact Handoff requires an independent producer and an
isolated fresh consumer. Under the current ChatGPT+Jason ContextView, JasonPC via
Human Manual Mode/Qiven Operator is the reference acceptance producer. Its job is to
materialize the exact candidate, generate/restore/verify the artifact and return
machine-readable handoff evidence. That is not a second implementation-validation
opinion and must not be replaced by the authoring LLM simply because the code is
portable.

Likewise, a fresh-LLM cognitive trial cannot be replaced by a child Python process,
a replay in the authoring session or a GitHub-based cold boot when the task-specific
profile requires artifact-only reconstruction.

For this scope, authoring in an agent-runtime working copy or directly on a remote
feature branch does not change the acting session's role or merge authority. No repeated
owner approval is required for ordinary commits, publication or validated batch
merge under the standing authorization. A coherent Context transaction is not a
rule limiting an entire implementation batch to one commit. Publish useful bounded
checkpoints when needed for continuity, and validate the final exact candidate.
The owner reaffirmed this interpretation on 2026-09-17 after cross-account K2
continuation; on 2026-09-18 the owner clarified that K4 handoff topology is a
separate acceptance requirement and authorized root correction of Context drift.
Concise batch reports should state result, evidence and next boundary.
