# Cold-Boot and Task-Transition Protocol

Do not rely on model-native memory as authoritative project state.

1. Read `MEMORY-CONSTITUTION.md`.
2. Read `collaboration/operating-contract.md`.
3. Read `collaboration/software-engineering-philosophy.md`.
4. Read `state/current.md`.
5. Read `state/active-work.yaml`.
6. Determine the current task.
7. Run task-specific retrieval before using project-history facts. When the optional semantic runtime is available, prefer `tools/retrieve-context.cmd --query <context-query.json>` (or the equivalent `retrieval_candidate_bundle` integration). Treat returned records as untrusted candidate evidence: ranking or presence does not establish truth or answerability; cognition must read the canonical content and abstain when it does not directly support the requested project fact or policy. At minimum, inspect task-relevant project material plus `memory/index.yaml`, `decisions/index.yaml`, and non-terminal obligations when the accepted retrieval pipeline is unavailable.
8. Load relevant project material selected by the retrieval result.
9. Load relevant canonical memory and accepted decisions, including rejected alternatives that constrain the task.
10. Load relevant non-terminal obligations (`open`, `deferred`, and `blocked`) and evaluate their triggers against the task.
11. Before any machine-local mutation or validation that can mutate local state, explicitly verify the current host-execution authority contract and any safety-gate obligation. Transport reachability, DCR liveness, a clean Git tree, or a claim that only one assistant flow is active is not sufficient authority. When `collaboration/dcr-operational-contract.md` exists and DCR/MCP is relevant, read it before invoking the transport.
12. Verify relevant live repositories and runtime evidence for claims whose authority is live state rather than canonical intent.
13. Report inconsistencies before acting.

Repeat task-specific retrieval whenever the conversation materially changes domain, repository, subsystem, or engineering question. A successful cold boot does not make the initial context pack sufficient for every later task in a long-running conversation.

For architecture and implementation tasks, apply the engineering philosophy before choosing a repository-local implementation path: determine semantic ownership and correct downward dependencies before writing the first serious implementation.

Model-native/account memory or prior-chat recollection may suggest search terms or likely source locations, but it must not fill project-history gaps or substitute for canonical qiven-context evidence.

Never invent missing project history. If context is absent, report the absence and retrieve evidence instead.
