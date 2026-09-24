# Qiven Museum — sealed executable history

Everything under `legacy/` is **sealed historical text** (ADRs 0040/0041,
owner direction 2026-09-21): the Python ContextKernel family, its
compiler/retrieval/archive/handoff tooling, suites and wrappers are
preserved as Markdown-wrapped source so they can be read as history but
never executed — not by a test runner, not by an operator gate, not by
accident. The cost this surface consumed is recorded in ADR-0040's
provenance; its successor is the frozen v4 specification
(`qiven-context-draft` @ `4cbc995`) and the `qiven-runtime` program.
