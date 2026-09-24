# ContextKernel K4 (historical program contract — accepted 2026-09-18; implementation sealed, ADR-0040)

> K4 Canonical Artifact Handoff was ACCEPTED (candidate decc769a...;
> audit evidence/audits/context-k4-handoff-acceptance-2026-09-18.md).
> The Python implementation referenced below is sealed museum material
> (ADR-0040); the acceptance evidence and the handoff contract
> (collaboration/context-handoff-contract.md) remain canonical.


K4's engineering implementation is `context_kernel.archive` plus the K4 handoff
surface. Formal K4 acceptance requires the Canonical Artifact Handoff profile in
`context-handoff-contract.md` and the Project Continuity reconstruction in
`project-continuity-acceptance.md`. A child process or remote GitHub cold boot is an
engineering/continuity proof for a different property, not the K4 handoff trial.
GitHub remains canonical. Restore and handoff never promote authority.

## Stable semantic manifest and variable delivery

Format `qiven-canonical-context`, version 1, carries a semantic manifest containing
project/snapshot identity, serialization version, sorted object digest/kind/size
entries, sorted committed transaction-ID-to-receipt mappings, raw evidence digest/
size descriptors and explicit external references. It enumerates all declared typed
object edges, revision predecessors, snapshot ancestry, import origins, existing
policy, authority decisions, requests and committed receipts. Unknown external
content digests stay null. Import's missing pre-Git revision history stays unknown.
No generic scan of arbitrary strings is used to infer graph edges.

The semantic manifest digest is SHA-256 of UTF-8 bytes
`qiven.context.export\0v1\0manifest\0` followed by canonical manifest JSON.
Package digest uses the same prefix with `package\0`, followed by the complete
canonical package without its package_digest field. Both are lowercase hex prefixed
with `sha256:`. Canonical JSON uses K1 primitive rules; package size is separately
bounded to 256 MiB. Object encodings stay unchanged and are delivered as strict
base64, keyed by their semantic IDs. This is not a database dump.

Delivery carries profile ID, asserted access-policy reference, explicit UTC
observation time, sorted included blob IDs and reasoned omissions. All canonical
objects must be present; bytes of evidence may be omitted explicitly. Changing
availability or delivery policy changes the package digest, not the semantic root.
An I/O/permission error is not silently interpreted as an absent blob; only explicit
not-found is omitted as unavailable. Corrupt bytes always fail.

Limits: 100,000 objects, 128 MiB object closure, 128 MiB raw evidence closure,
16 MiB/object and 8 MiB/evidence item. Exceeding a limit is explicit failure, not
truncation. Incremental backups are not implemented; complete exports remain the
reference mechanism.

## Recovery profile and quarantine

Profile `canonical-continuity-v1` requires every canonical object and all declared
raw evidence, including provenance ancestry. Every explicitly modeled external
reference needs locally delivered bytes matching its known digest for full recovery;
an unknown digest blocks full recovery. Imported metadata citations remain preserved
unverified assertions, not newly fetched/verified external evidence. The profile
recovers declared cognition/evidence; it does not prove the truth of every assertion.

Restore independently checks package digest, semantic manifest digest, object and
raw digests, typed graph closure and native transaction bindings. Missing canonical
objects, undeclared extras, duplicate keys/maps, unexplained omissions, cross-project
edges and unknown formats fail. Explicitly omitted raw evidence yields a partial,
quarantined in-memory result with diagnostics; it cannot initialize a runnable
adapter. Full delivery also validates the selected K3 read projection. Continuity
still requires the declared corpus and fresh-LLM gate, not just matching checksums.

Known private-key markers and explicit credential assignments block export/restore
until governed remediation; the source is never silently redacted. This bounded
screen does not certify arbitrary natural-language content as secret-free. The
caller owns access admission and content review. Policy labels are assertions, not
permission grants; credentials never belong in labels or canonical content.

## Read-only operational boundary

Canonical snapshots and committed ancestry do not enumerate every pending/rejected
idempotency reservation in a running service. K4 therefore does not claim to restore
the complete operational journal. Included committed results are reconstructed, but
all new mutations are persistently blocked in the restored SQLite reference instance.
Known identical committed retries/result lookup remain available where the sandbox
policy admits them. Missing keys remain unknown, never reusable by implication.
No write-unlock/promotion API is provided.

Restoration requires an empty adapter and atomically publishes objects, evidence,
retained committed results, selected head and the read-only block. Failures roll
back all adapter changes. The CLI claims its database and source-directory targets
exclusively and removes invocation-owned outputs on ordinary exceptions; it does not
claim power-loss atomicity across the SQLite file and source directory. Imported Git
snapshots can be inspected through K3; they do not acquire native transaction
governance. Historical snapshots can be exported explicitly without importing later
receipts. Package hashes prove integrity, not signer identity or authority.

## K4 handoff artifact

The archival package remains the semantic backup primitive. K4 additionally requires
one versioned JSON handoff artifact suitable for the declared fresh-LLM consumer.
The handoff artifact must contain or bind:

- exact repository/commit/tree and ProjectSnapshot identity;
- canonical manifest and package digests;
- the complete canonical export needed by the recovery profile;
- a deterministic continuity/source projection exposing the artifact-contained
  Project Continuity corpus without requiring a qiven-context repository read;
- path/content digests for every projected source item and a root projection digest;
- explicit recovery completeness, unknown/external-reference diagnostics and
  `authorization: not_granted` / writes-disabled state;
- a digest covering the complete handoff delivery.

The projection is derived transport, not a second truth. Every projected byte must
match content already committed by the canonical export. Missing/extra/mismatched
projection content fails generation or consumption.

K4 is correctness-first. It does not require a compact representation; K5 owns
lossless token-efficient transport after this reference artifact is accepted.

## Engineering acceptance

The engineering suite covers import and native-history round trips,
availability-independent roots, missing/corrupt/extra objects, omission diagnostics,
unknown external references, nonempty-target rejection, retained receipts, persistent
read-only admission and known-secret rejection. A new Python process receives only
the package and fixed query corpus, disables Git reads and reconstructs 28 compiler/
bundle outputs. CLI failure-path coverage proves ordinary source-materialization
failures do not publish a restored database artifact.

The corrected K4 suite must additionally cover handoff generation/consumption:

- exact commit/tree/snapshot binding;
- projection-to-canonical-source digest equivalence;
- deterministic handoff digest for fixed semantic/delivery inputs;
- missing/extra/tampered projected sources;
- tampered package/manifest identities;
- incomplete recovery and unknown external references;
- no write/authority promotion;
- consumer reconstruction fixtures that do not read Git/original source material.

These automated tests are necessary but cannot themselves supply the fresh-LLM
cognitive PASS.

## Formal acceptance topology

1. Publish the exact K4 candidate remotely.
2. Complete the portable engineering gate on the exact candidate.
3. Under `ContextView<ChatGPT, Jason>`, use JasonPC Human Manual Mode/Qiven Operator
   as the independent producer. Produce and locally verify one exact handoff JSON and
   record commit/tree/platform/runtime/manifest/package/handoff identities.
4. Give that artifact to a fresh capable LLM session with no prior Qiven project
   memory. Before Phase A is sealed, the fresh consumer must not read qiven-context
   remotely or receive private reconstruction help.
5. The consumer reconstructs the ten Project Continuity requirements from the
   artifact and stops with a sealed Phase-A report.
6. Only then may the same fresh session perform Phase-B live verification for facts
   explicitly classified as live. It must not use GitHub to repair missing artifact
   cognition.
7. Preserve the dated audit and run final exact-head repository validation. Apply the
   continuity carry-forward rule only for changes that do not alter tested cognition
   or handoff inputs.

Until every step passes, K4 remains an engineering candidate and main remains at the
latest accepted pre-K4 checkpoint.
