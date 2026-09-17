# ContextKernel K4 canonical export and recovery contract

K4's engineering implementation is `context_kernel.archive`. Formal K4 acceptance
also requires the fresh-session LLM trial in project-continuity-acceptance.md.
A child process is an engineering isolation proof, not that cognitive trial.
GitHub remains canonical. Restore does not promote authority.

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
back all adapter changes. Imported Git snapshots can be inspected through K3;
they do not acquire native transaction governance. Historical snapshots can be
exported explicitly without importing later receipts. Package hashes prove
integrity, not signer identity or authority.

## Acceptance and invocation

The fixed engineering suite covers import and native-history round trips,
availability-independent roots, missing/corrupt/extra objects, omission diagnostics,
unknown external references, nonempty-target rejection, retained receipts, persistent
read-only admission and known-secret rejection. A new Python process receives only
the package and fixed query corpus, disables Git reads and reconstructs 28 compiler/
bundle outputs (seven queries, two view selections, two entrypoints).

A separate fresh LLM session must reconstruct the ten points in
project-continuity-acceptance.md from the restored exact candidate plus admitted live
evidence. Its prompt is `tests/cold-boot/k4-candidate-prompt.md`. Until its dated audit
passes, K4 is an engineering candidate and main must not advance to K4 acceptance.

`python tools/context_archive.py export-git --commit FULL_SHA --repository
JasonHuang3D/qiven-context --output NEW_PACKAGE.json` creates a package.
`python tools/context_archive.py restore --input PACKAGE.json --database NEW.db
--sources NEW_DIRECTORY` restores read-only data and an inspectable source projection.
Outputs must be new paths. Neither command performs network publication or cutover.
