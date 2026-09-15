# Retrieval Reliability Closeout Acceptance — Stage 2

Send this as the **next user message in the same fresh Chat conversation** after the Stage 1 report. Do not start another conversation for Stage 2.

Material task transition: stop reasoning from the Operator/Devkit task and switch to `qiven-cad`.

Before answering, follow `BOOTSTRAP.md` and perform a **new task-specific retrieval for this CAD task**. Explicitly list the canonical sources newly inspected for this transition. Do not merely reuse the Stage 1 Operator context. If the accepted local retrieval CLI is unavailable in this Chat environment, say so and use the BOOTSTRAP fallback through GitHub; do not pretend to have run a local command.

Do **not** read `tests/retrieval-closeout/evaluator-rubric.md`.

Answer both questions from canonical Qiven evidence only:

1. For the first CAD product, what architectural core and semantic boundary does Qiven intend? Is arbitrary unknown-DWG interpretation or an AutoCAD/DCC editor the architectural center?
2. Which exact IFC schema version is `qiven-cad` required to emit by default? Answer only if canonical Qiven cognition explicitly fixes that exact exporter-version requirement; otherwise state that canonical context does not establish an exact version and abstain from inventing one.

Keep the answer compact. Include the new retrieval sources and the relevant ADR/MEM/OBL IDs or repository paths that directly support each conclusion.
