# Human-Facing Executable Contract

## Purpose

A script handed directly to a human is an operator interface, not merely an automation primitive. If it may be launched from Explorer or another environment that creates a transient terminal, terminal lifetime and final-state visibility are part of the correctness contract.

## Default human mode

A human-facing `.cmd` or `.bat` entrypoint must assume it may be double-clicked.

- Every terminal success and failure path must converge on explicit final handlers rather than scattering bare `exit /b` statements through the main flow.
- The final handler must print an unmistakable terminal status block containing success/failure, the failing stage when applicable, and any identity that matters to the operation such as exact SHA/tree/run.
- The terminal must remain visible with `pause` before returning in default human mode, on both success and failure.
- The script must preserve the truthful exit code after the pause. A visible failure must still return non-zero; a visible success must return zero.
- Required stages should emit stable `[ RUN]`, `[ OK ]`, and `[FAIL]` markers so the human can tell what actually executed.

A typical structure is `main -> :success` or `main -> :fail`, with the final `exit /b` occurring only after the human-visible terminal block and pause.

## Automation mode

The same entrypoint may support non-interactive composition through an explicit switch such as `--no-pause` or another documented automation mode. Automation mode may omit `pause`, but it must preserve the same stage semantics and exit code.

Child/helper scripts that are not intended to be launched directly by a human may remain non-pausing. Their role must be clear, and a human-facing parent must not rely on a child window disappearing as its only failure signal.

## Orchestration boundary

Short one-off command chains remain acceptable when their behavior is obvious. Once a human operation has multiple validation stages, branching failure handling, cleanup, exact-identity gates, remote publication, or a need to preserve the final result, prefer a repository/local orchestration script over a long ad-hoc `&&` chain.

The orchestration must stop before later mutating stages when a required earlier gate fails. A final success marker may appear only after the operation's externally observable success condition has been verified; for example, a Git push workflow must verify the published remote ref before printing canonical success.

## Rationale

On 2026-09-16 a Context v2 canonical-merge script was correct as an automation-style fail-fast program but was handed to the project owner as a double-clickable human tool. Its terminal paths used `exit /b`, so the transient CMD window closed before the human could reliably inspect the final result. Remote read-only verification later proved the merge had succeeded, but the script itself failed the human-observability contract. This document makes that failure class non-repeatable by design.
