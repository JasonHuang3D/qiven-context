# R1 Context Read Contract

R1 implements C01-C06 as one source-read pipeline. Lifecycle rules remain in
`collaboration/record-lifecycle.md`; this contract adds mandatory context,
constraints, evidence preservation, snapshots and unknown-condition semantics.

## Required inputs and participant adaptation

`collaboration/context-inputs.yaml` is the shared ordered declaration used by the
compiler and by candidate-bundle construction. It includes the constitution,
governance, operating and engineering contracts, Context operating model, compact
state, repository inventory, roadmap and constraint declaration.

The optional query `view` selects a declared ContextView by ID. Its referenced
environment/workflow files must exist; an inactive, mismatched, unknown or
project-overriding view is rejected. With no selected view, identity-independent
ProjectContext is loaded. No authenticated human identity is inferred from query
text. Missing/malformed mandatory input fails the read rather than claiming ready.
The existing BOOTSTRAP order remains the human-readable boot procedure; it now
references the same manifest as the machine entrypoints.

## Protected constraints and budgets

`governance/context-constraints.yaml` declares deterministic applicability selectors
for `operation.action`, `operation.target` and `operation.channel`. These are
caller-described operation attributes, not authentication evidence. Rules whose
applicability is unknown remain visible. A missing source or a rule referencing a
non-current canonical record fails the read.

All current explicit memory constraints/invariants/protocols, non-terminal
before-obligations and commitments are also protected from ranking truncation.
Scope overlap supports applicability; lack of overlap does not prove irrelevance
and therefore retains the record as unresolved. This conservative coverage may
include excess context until stronger scope contracts are accepted.

Protected sources are separate from ranked candidates. `max_candidates` affects
ranked evidence only. Optional `max_context_bytes` limits canonical compact-JSON
UTF-8 bytes, not model-specific tokens or rendered Markdown. Whole optional
records may be omitted with IDs reported. Mandatory sources, applicable/unresolved
constraints and explicit IDs cannot be silently truncated. An insufficient budget
fails visibly. No tool call may treat either `context_loaded` or a resolved rule
set as execution permission: `authorization` is always `not_granted`.

Coverage is explicitly bounded to declared rules and typed constraint records.
Natural-language documents may contain additional duties; the engine does not
claim to have compiled all prose into a complete policy engine. Host/execution
admission remains independently enforced.

## Evidence versus ranking text

Ranking text remains a relevance representation. Delivered evidence preserves the
full record front matter and body, including epistemic kind/basis, temporal scope,
sources, lifecycle and relations. Missing metadata remains absent; it is not
invented or promoted from the caller query. Each record includes its raw source,
SHA-256 and snapshot identity. Consumers must interpret accepted decisions,
observations and hypotheses according to those preserved distinctions.

## Snapshot and reproducibility boundary

Git repositories are captured from one resolved immutable commit. Default reads
reject source changes relative to HEAD; an explicit `SourceSnapshot.capture(ref=...)`
selects that Git commit regardless of the working copy. Git commit/tree identity
is provenance, not proof that the ref is the current canonical remote; callers
still resolve canonical remote authority before boot or acceptance.

Non-Git exports/fixtures use a quiescent-directory capture with before/after digest
comparison, explicitly labelled non-authoritative. This mode requires writer
quiescence and is not a filesystem-wide atomic snapshot guarantee. Production
Git reads do not depend on that weaker guarantee.

Captured bytes are immutable in memory. Private temporary materialization supports
the existing file readers; ranking, selection and serialization share the same
snapshot. Retriever objects are snapshot-bound; a later source revision requires a
new object. Historical embeddings are lazy and remain scoped to that snapshot.

v3 packs and bundles carry a source manifest and bound content. Markdown rendering
checks hashes and uses included content; it never rereads selected source paths
from a changed working copy. Digest checks detect content inconsistency, not
malicious replacement of both payload and manifest. No signing/IAM is introduced.
Same snapshot, query, explicit time and deterministic ranking backend reproduce
the same evidence selection and payload. Runtime measurements remain external.

Source files are bounded to 8 MiB each and 128 MiB total; unsupported links and
oversized sources fail explicitly. These are operational limits, not claims about
project-scale capacity. Old v1/v2 derived packs must be regenerated.

## Unknown inputs and conditions

Optional query fields `negative_conditions`, `complete_inputs` and `input_evidence`
make absence distinguishable from falsity. Exact normalized condition names are
matched, not bag-of-word entailment; negated phrases do not assert the positive.
Contradictory positive/negative assertions yield `unresolved`.

No matching condition, touch or change yields `unresolved` unless the caller
explicitly declares that input set complete and supplies a supporting evidence
reference. An explicit negative condition gives `not_triggered`. Positive declared
conditions give `due`. Caller assertions remain caller assertions; these results
never grant authority or create canonical facts. Date comparisons remain
clock-based; unsupported dates are unresolved. Historical ledger completion is
still explicitly labelled historical evidence for the existing after-trigger.

## Batch validation

The R1 suite targets mandatory-input loss, View resolution, constraints outside
Top-K, insufficient budgets, evidence fidelity, snapshot mutation/reuse, payload
tampering, and three-valued inputs. It complements C01 cross-entrypoint lifecycle
coverage. No embedding/reranking model or frozen ranking parameter is changed.
Full Context validation is performed after the coherent implementation batch,
under `collaboration/context-validation.md`.
