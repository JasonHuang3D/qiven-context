# Retrieval Reliability — Clean Integration Scope

This note defines the clean integration boundary from accepted `main` after blind-v4 validated the candidate/reasoning split.

## Integrate

Production retrieval mechanism:

- semantic candidate retrieval;
- hybrid deterministic/semantic fusion;
- structural scope/relation filtering;
- cross-encoder reranking;
- small provenance-preserving candidate bundle marked as untrusted evidence;
- candidate-boundary acceptance harness and blind-v4 benchmark;
- optional semantic bootstrap/runtime dependency pin;
- focused unit coverage for the accepted mechanism.

Evidence retained in canonical history:

- deterministic, semantic, hybrid, structural, and reranker benchmark audits;
- blind-v3 failure and the answerability experiments that explain why retrieval-level answerability was rejected;
- blind-v4 retrieval + cognition acceptance;
- JasonPC network/progress observation relevant to semantic runtime downloads.

## Do not integrate

- Context Runtime / Context Lease / cognition-transport files;
- prepare/context gateway transport path;
- generic NLI, evidence-span, concrete-entailment, atomic-entailment, and NLI-class executable probe implementations or their unit tests;
- blind-v3 `select_ids()` answerability path as production behavior.

The experimental `jason-brother/retrieval-reliability` branch remains the archaeology source for those falsified experiments.

## Accepted boundary

Retrieval answers: **what canonical evidence should cognition read first?**

Retrieval does not answer: **is the task answerable or what proposition is true?**

Candidate presence and ranking scores are not project truth. Cognition must read canonical evidence, preserve provenance, and abstain when the candidate bundle does not directly support the requested project fact or policy.
