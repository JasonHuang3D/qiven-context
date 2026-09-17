# ContextKernel K1 contract

K1 implements ADR-0033 section 12 in `tools/context_kernel/` as a portable Python
library. This is a semantic reference implementation, not a Windows executable,
a production database, a native transaction implementation or a cutover. GitHub
remote remains canonical. `MemoryStore` is single-owner, ephemeral, and has no
canonical head or authorization API. K2 owns transactional publication and races.

## Versioned identity

Serialization v1 supports exactly null, boolean, integers in
`[-9007199254740991, 9007199254740991]`, Unicode scalar strings, arrays and objects
with string keys. Floats (including NaN/Infinity), bytes, dates, surrogate code
points, implicit conversions and arbitrary Python objects are rejected. Strings
are preserved without Unicode normalization: NFC and NFD are different evidence.
Arrays preserve order. Object keys sort by Unicode scalar value, recursively.
Absent fields differ from explicit null. Protocol fields are always required;
optional source metadata retains its original absence/null distinction.

Encoding is UTF-8 JSON without BOM, spaces or trailing newline. Quote, backslash
and U+0000–U+001F are escaped using JSON's short escapes where defined and lowercase
`\u00xx` otherwise. Other Unicode scalar values are literal UTF-8. `/` is literal.
Integers use decimal without leading zeros or plus; zero is `0`. Deserialization
rejects duplicate keys, unsupported versions/types and noncanonical byte forms.
Maximum nesting is 64 and serialized object size is 16 MiB.

Every object is exactly `{kind, payload, serialization_version: 1}`. Its semantic
ID is `sha256:` plus lowercase SHA-256 of the bytes
`qiven.context.kernel\0v1\0` followed by its canonical JSON. The envelope's `kind`
is the type domain separator. No object contains its own digest. All envelope and
payload fields are hashed. Runtime duration, local clone paths and store locations
are not present in these payloads. Raw byte IDs use plain SHA-256 without the
semantic prefix and are explicitly typed `content_digest`, never object IDs.

The exhaustive hashed field/type registry is
`schema/context-kernel-object.schema.json`. Current objects are:

| Object | Hashed meaning |
| --- | --- |
| EvidenceObject | Raw content digest, byte length, media type |
| SourceDocument | Project identity, logical document path, evidence object ID |
| RecordRevision | Project/logical identity, registered kind/schema, complete source metadata and body, source document ID, explicit unknown historical authentication and absent revision ancestry |
| ProjectSnapshot | Project ID, null imported base, bounded history scope, asserted repository plus exact Git commit/tree and commit evidence, sorted record/document manifests |
| ImportReceipt | Snapshot ID, current import actor assertion/authentication, quarantined status, not_granted authorization, Git provenance and explicit diagnostics |

`ProjectId` and `RecordId` are validated value types, not independently hashed
objects. Native ContextTransaction/AuthorityDecision and query/view/bundle types
are reserved for K2/K3; they are rejected rather than represented as untyped
canonical objects in K1. Current view, governance, state and contract documents
are preserved losslessly as SourceDocuments.

Hash order is raw bytes → evidence → documents → record revisions → snapshot →
import receipt. The receipt does not participate in snapshot identity. Reimport
with another actor produces the same snapshot and a different receipt. Source Git
identity is asserted provenance and deliberately participates in snapshot identity;
identical trees in distinct commits need not have identical snapshot IDs.

## Exact Git import and preserved unknowns

`import_git_snapshot(root, full_commit_id, project_id=..., repository=...,
actor_assertion=...)` accepts only a full commit object ID, resolves it once and
reads raw `ls-tree`/`cat-file` blobs. Git replace refs and archive export attributes
do not change imported source. Symlinks and gitlinks inside the declared closure
are rejected. Read bounds are 8 MiB/file and 128 MiB/source snapshot.

The source closure is exactly `context_snapshot.SOURCE_ROOTS`. Every file in those
roots, including non-record evidence and historical documents, is preserved byte
for byte. This is not a complete Git backup: executable tools, tests, omitted roots
and Git ancestry are outside K1. `raw_sources()` reconstructs the imported source
mapping byte for byte. Full export packaging/restore is K4.

ADR, memory and obligation schemas are content-pinned in the kind registry.
Unknown schema/kind/status, duplicate YAML keys, aliases, invalid identity,
nonreciprocal/cyclic lifecycle graphs and missing mandatory inputs fail import.
Canonical metadata retains every supported field; no synthetic lifecycle fields
are inserted into the original payload. Raw commit bytes preserve author,
committer, parent and signature headers as source evidence only. The selected
commit's author is not attributed as creator of every record.

One imported tree proves visible revisions only. Earlier record revisions,
creating transactions, historical principals and authority decisions are unknown;
null predecessor means *not imported*, not proof that no predecessor exists.
External provenance references remain assertions with unverified availability.
The current import actor is separately recorded as an unverified assertion in the
receipt. No caller-supplied string is authentication and no import grants authority.
Future ancestry import and authenticated import admission require separate contracts.

## Fixed acceptance corpus

`tests/fixtures/context-kernel/k1-golden.json` fixes canonical byte strings and
semantic digests independently of the serializer under test. The suite verifies
Unicode ordering/normalization distinctions, absent/null, types and bad encodings;
immutable payloads; source byte restoration; pinned schemas/lifecycle/provenance;
quarantine/unknown authority; invalid source rejection; Git archive attributes;
replacement refs; dirty-worktree independence; and reproducible import across
clone locations/actor assertions. A real canonical commit is imported as a bounded
integration proof. This establishes K1 only, not K2 durability, K3 query equivalence,
K4 recovery completeness or model ranking quality.
