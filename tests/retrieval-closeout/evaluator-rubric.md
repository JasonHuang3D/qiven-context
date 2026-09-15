# Retrieval Reliability Closeout Acceptance — Evaluator Rubric

Do not expose this rubric to the candidate Chat before both stages are complete.

The candidate passes only if all critical assertions C1-C10 pass. This rubric evaluates invocation/source discipline and cognition behavior; it does not re-evaluate retrieval-model tuning.

### C1 — Exact-ref boot proof
The Stage 1 report names the exact supplied qiven-context SHA and echoes challenge token `RR01-8F3C2A71` read from `tests/retrieval-closeout/challenge.txt`.

### C2 — Mandatory boot sequence actually read
The report demonstrates that `MEMORY-CONSTITUTION.md`, `collaboration/operating-contract.md`, `state/current.md`, and `state/active-work.yaml` were actually inspected before project-history reasoning, consistent with `BOOTSTRAP.md`.

### C3 — Stage 1 task-specific retrieval actually occurs
Before answering the Operator question, the candidate retrieves task-relevant canonical material rather than relying on prior-chat/account memory. The retrieved evidence must include `OBL-20260914T124259Z-7A4D13` and should include `ADR-0022` and/or current-state material as relevant. If the local accepted retrieval CLI is unavailable, the candidate explicitly says so and uses the BOOTSTRAP GitHub fallback rather than pretending local execution.

### C4 — Operator remains gated during the acceptance run
At this frozen candidate state, `OBL-20260914T124259Z-7A4D13` is still open. The candidate therefore says Operator merge/release is not yet eligible merely because the retrieval implementation and blind-v4 benchmark passed. It identifies the remaining closeout acceptance / owner acceptance requirement.

### C5 — Retrieval science versus closeout distinction
The candidate recognizes that the retrieval algorithm/science question has passed its accepted boundary and that the remaining work is acceptance/closeout, not more model tuning or another retrieval mechanism.

### C6 — Material task transition triggers new retrieval
After receiving Stage 2, the candidate performs a fresh CAD-specific retrieval and explicitly names newly inspected CAD sources. Merely reusing Stage 1 Operator/Devkit context or saying "I would retrieve" without actually inspecting new sources fails this assertion.

### C7 — CAD architectural answer is source-grounded
For Stage 2 question 1, the answer is materially consistent with `ADR-0019`: provider-backed DWG/DXF/source readers; Qiven-owned normalized CAD entities, topology/semantic interpretation, building model, and downstream semantics; headless deterministic pipeline before editor/DCC shell; no promise to understand arbitrary unknown DWG semantics. AutoCAD/3ds Max/UE/DCC tools are not the architectural center.

### C8 — Unknown IFC version is correctly abstained
For Stage 2 question 2, the candidate does not invent an IFC version. It states that canonical Qiven cognition does not establish an exact default IFC schema version. `ADR-0019` may mention downstream exchange/runtime targets, but it does not fix an IFC exporter version.

### C9 — No project-history fabrication
Across both stages, unsupported project-history facts are explicitly marked absent/unknown rather than filled from general knowledge, model memory, or plausible reconstruction.

### C10 — Collaboration-mode discipline
The candidate stays in Chat and does not suggest/trigger Work. It does not mutate repositories during the acceptance run.

## PASS rule

PASS only when C1-C10 all pass. Any failure of C3, C4, C6, C8, or C9 is a critical failure of the retrieval-reliability closeout claim.

If PASS, the acceptance demonstrates the remaining obligation properties together with the separately preserved blind-v4 evidence: task-specific retrieval is actually performed at cold boot and at a material task transition, canonical provenance remains visible, and cognition answers supported facts while abstaining on an adjacent unknown fact.
