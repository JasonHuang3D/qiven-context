# Canonical Record Lifecycle Query Contract

This contract defines C01 lifecycle eligibility for the compiler, semantic and
hybrid retrieval, structural and reranked retrieval, and candidate bundles. It
supersedes only the lifecycle-selection portions of the Batch 003 compiler
contract. It does not define authority, temporal validity, or task relevance.

## Shared qualification

`tools/record_lifecycle.py` owns the shared predicate. Unknown categories or
statuses are errors rather than silently current records.

| Category | Current-query eligible statuses |
| --- | --- |
| Decisions | accepted |
| Memory | active |
| Obligations | open, deferred, blocked |

`current_eligible` means eligibility by recorded lifecycle status at the supplied
repository snapshot. It is not proof of truth, authorization, temporal validity,
or relevance. In particular, an active hypothesis does not become a verified fact.

## Query modes and explicit inspection

- Omitted `record_mode`, or `record_mode: current`, searches current-qualified
  records. Relation expansion cannot reintroduce an excluded record.
- `record_mode: history` includes all known lifecycle states in the searched
  snapshot. Relevance and normal ranking still apply. This is inclusive inspection,
  not a historical as-of-time reconstruction and not a dump of every Git revision.
- `include_ids` explicitly admits the named records in either mode, without
  admitting other non-current records or changing any record's status. It does
  not substitute a successor for the requested identity.
- Unknown IDs receive diagnostics in compiled packs and candidate bundles.
- Candidate bundle limits must not silently evict an available explicitly requested
  ID. If explicit records alone exceed the limit, the caller must increase the
  limit; the request fails visibly instead of truncating them.

These rules determine admissibility, not identical ranking across algorithms.
Raw ranking hits are identifiers/scores to inspect, not self-contained knowledge.
Consumers use compiled records, candidate bundles, or the original records for
lifecycle interpretation.

## Output and compatibility

Compiled packs and candidate bundles use `schema_version: 2`. Canonical selections
carry the original `status`, `current_eligible`, `supersedes`, and `superseded_by`.
Missing replacement links remain empty; no relationship is inferred or fabricated.
Markdown packs display lifecycle qualification and include the original source.
Existing v1 derived packs should be regenerated; they are not canonical records.

Terminal obligations may be inspected but are never evaluated as outstanding
work. Their generated trigger has `type: inactive` and `result: inactive`; their
original source remains intact. Inspection does not reopen obligations.

Only lifecycle metadata is added here; broader evidence preservation belongs to
C04. Mandatory-context loading, authority enforcement, snapshot pinning, temporal
queries, and three-valued conditions remain separate work.

## Runtime and validation boundary

Current-query semantic embeddings retain the existing model input. Historical
records are embedded on first requested inspection and cached by record identity
within the retriever instance. Returning to a current query reapplies lifecycle
qualification; previously cached history cannot leak into the current results.
Retriever instances remain bound to their loaded repository materialization;
create a new instance after source mutation. Snapshot enforcement is C05.

`tools/test_record_lifecycle.py` checks all schema-defined states across the real
entrypoints with deterministic model backends, including relation leakage,
explicit inspection, terminal obligations, ceiling behavior, missing IDs, and
history-to-current reuse. These checks run in the normal Operator full-tests gate.
They prove lifecycle behavior, not model ranking quality or general recall.
