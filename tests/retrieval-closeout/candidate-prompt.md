# Retrieval Reliability Closeout Acceptance — Stage 1

Use this prompt in a **new Chat conversation**. The project owner will provide the exact `qiven-context` candidate Git SHA separately.

Authoritative durable source: `JasonHuang3D/qiven-context` at that exact SHA. Treat the ref as immutable for this acceptance run.

Rules:

1. Do not use model-native/account memory or prior chats as project authority, and do not use them to fill gaps.
2. Stay in Chat. Do not suggest, trigger, or hand off to Work unless the user explicitly asks for Work during this run.
3. Read `BOOTSTRAP.md` at the supplied ref and follow its mandatory boot sequence in order.
4. Before using Qiven project-history facts for the current task, perform task-specific retrieval. If the accepted local retrieval CLI is unavailable in this Chat environment, say so explicitly and use the fallback required by `BOOTSTRAP.md`: inspect task-relevant canonical material plus the relevant indexes and non-terminal obligations through GitHub. Do not pretend that a local CLI was executed when it was not.
5. Read `tests/retrieval-closeout/challenge.txt` at the supplied ref and echo the exact token in the report.
6. Do **not** read `tests/retrieval-closeout/evaluator-rubric.md` before submitting the Stage 1 report.
7. Verify live repository state when a claim depends on live implementation state rather than canonical intent.
8. For material Qiven claims, cite repository paths plus ADR/MEM/OBL IDs or exact live SHAs. If evidence is absent, say so explicitly rather than reconstructing a plausible answer.
9. Do not mutate any repository during this acceptance run.

## Current task

Answer this as the active task after cold boot:

> Qiven Operator Phase 1 has been waiting on the retrieval-reliability gate. Can Operator work now resume and may jason-brother merge/release the Devkit Operator candidate immediately, or is there still a canonical gate that must be completed first?

Produce a compact Stage 1 report with:

### A. Boot proof
- supplied qiven-context ref;
- challenge token;
- mandatory boot sources actually read, in order;
- retrieval path actually used for this task;
- task-specific canonical records actually retrieved;
- any inconsistency detected before acting.

### B. Decision
- whether Operator may resume immediately;
- the exact remaining gate, if any;
- what must happen before Operator merge/release becomes eligible.

Do not continue into unrelated domains. Wait for the project owner's next message after submitting Stage 1.
