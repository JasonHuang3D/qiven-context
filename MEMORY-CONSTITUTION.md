# Qiven Memory Constitution

## 1. Capture generously, retrieve selectively
Preserve cognition conservatively. Solve token and context limits during retrieval, not by discarding knowledge during capture.

## 2. Evidence and interpretation are different
Keep raw evidence distinguishable from canonical interpretation. Canonical memory may be corrected without destroying evidence.

## 3. History is not overwritten
Retain superseded decisions and facts with temporal status. Changed current state does not justify deleting history.

## 4. Unfinished cognition is first-class
“Later,” “not now,” “remember this,” “non-blocking,” “revisit,” “if X happens,” and “validation still missing” must be representable as explicit obligations with triggers.

## 5. Negative knowledge is first-class
Preserve rejected alternatives and the reasons for rejection.

## 6. Epistemic types must not be collapsed
A hypothesis is not a fact, a candidate is not a decision, and an observation does not automatically become an invariant.

## 7. Provenance is required
Canonical knowledge must be traceable to one or more sources wherever practical.

## 8. Cold boot must be testable
A new LLM session must eventually be tested for correct reconstruction.

## 9. Live reality is question-scoped authority
There is no simplistic global precedence chain. “What code exists now?” is answered by live Git; accepted architecture by ADRs/invariants; actual CI by CI evidence; planned work by active-work state; rejection rationale by rejected-option memory/ADRs; and future resurfacing by obligations.

## 10. Conflict is information
If live code and an accepted ADR disagree, record and report a state inconsistency; do not silently choose.

## 11. Derived indexes are never canonical
SQLite, FTS, BM25, embeddings, vector or graph indexes, and MCP must remain rebuildable derived layers.

## 12. Private does not mean secret store
Never commit passwords, private keys, access tokens, API keys, recovery codes, or credentials. A future ingestion strategy may add redaction and secret scanning; Batch 001 does not claim such protection.
