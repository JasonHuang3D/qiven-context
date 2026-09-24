# Qiven Memory Constitution

## 1. Project cognition must outlive its participants
Qiven context exists so project cognition survives session loss, turn incidents, model/provider replacement, agent replacement, and authorized human-operator changes. Model-native memory, one assistant identity, or one human's recollection is never authoritative project state.

## 2. Capture conservatively, canonicalize deliberately, retrieve selectively
Preserve material cognition and evidence, but do not accumulate competing active truth indefinitely. Capture, classify, canonicalize, supersede or resolve, retrieve, and periodically compact the active working set without deleting history.

## 3. Evidence and interpretation are different
Keep raw or durable evidence distinguishable from canonical interpretation. Canonical memory may be corrected without destroying supporting or contradictory historical evidence.

## 4. History is not overwritten
Retain superseded decisions and facts with temporal and lifecycle status. Changed current state does not justify deleting history.

## 5. Session independence is mandatory
Session checkpoints are continuity evidence, not the project source of truth. No fact, decision, obligation, invariant, authority rule, accepted checkpoint, or blocker that must survive the session may exist only in a session record.

## 6. Unfinished cognition is first-class
“Later,” “not now,” “remember this,” “non-blocking,” “revisit,” “if X happens,” and “validation still missing” must be representable as explicit obligations with triggers.

## 7. Negative knowledge is first-class
Preserve rejected alternatives and the reasons for rejection.

## 8. Epistemic types must not be collapsed
A hypothesis is not a fact, a candidate is not a decision, an observation is not automatically an invariant, and a passing CI run is not by itself semantic acceptance.

## 9. Provenance is required
Canonical knowledge must be traceable to one or more sources wherever practical. Accepted engineering checkpoints must identify the evidence that proves their acceptance boundary.

## 10. Authority is question-scoped
There is no simplistic global precedence chain. Current remote repository state answers what is published now; accepted ADRs/invariants answer architecture and policy; exact CI evidence answers validation; current state answers active operational intent; obligations answer future resurfacing; audits preserve durable evidence.

For `qiven-context` itself, the canonical repository authority is GitHub remote state. Local clones are non-authoritative working copies.

## 11. Conflict is transient epistemic state
A newly discovered contradiction must be preserved long enough to prevent silent resolution, then explicitly reconciled. Reconciliation identifies scope and time, establishes the current canonical interpretation when evidence permits, marks displaced records as superseded/archived/retired/legacy as appropriate, preserves rationale and provenance, and removes displaced records from default current-state retrieval.

An unresolved conflict may remain only when evidence is genuinely insufficient. It must then be represented explicitly as an open question, blocker, risk, or obligation rather than silently left as competing canonical truth.

## 12. Governance authority is explicit
Possession of a clone, local machine, repository credential, or reasoning capability is not by itself project governance authority. Current Qiven governance authentication trusts GitHub account-level authentication. The root governance principal is defined in `governance/authority.yaml`. Qiven does not claim to authenticate biological identity.

## 13. Derived indexes are never canonical
SQLite, FTS, BM25, embeddings, vector or graph indexes, generated context packs, and MCP/tool surfaces must remain rebuildable derived layers.

## 14. Private does not mean secret store
Never commit passwords, private keys, access tokens, API keys, recovery codes, or credentials.

## 15. Simplicity must be falsifiable, not assumed sufficient
Deferring a deeper mechanism is an engineering hypothesis, not proof that the mechanism is unnecessary. Foundational complexity deferrals must state observable failure signals, a falsification path, a revisit trigger, and a credible migration or comparison path.

## 16. Retrieval reliability includes invocation as well as ranking
A correct retrieval engine that is not invoked at a material task transition is operationally equivalent to a retrieval miss. Cold boot is not the only retrieval boundary.

## 17. Validation proves a candidate; it is not an apprenticeship loop
Apply mature engineering knowledge before implementation. Compiler, tests, experiments, and CI resolve genuine uncertainty and prove the reviewed candidate. Repeated validation failures in already-known hazard classes trigger design review rather than mechanical patch/CI repetition.

## 18. Continuity is testable
A fresh capable LLM and a fresh authorized human, with no prior conversation or model memory, must be able to reconstruct the project from canonical remote context plus live project evidence. The acceptance contract is `collaboration/project-continuity-acceptance.md`.
