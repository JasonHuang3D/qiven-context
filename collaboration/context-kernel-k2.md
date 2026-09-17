# ContextKernel K2 transaction contract

K2 implements ADR-0033's transaction, authority and idempotency boundary through
`ContextTransactions`. Its SQLiteReference adapter is a restart-capable conformance
mechanism, not a production database selection. Every instance/head/receipt is
explicitly scoped to a quarantined reference sandbox. It cannot publish Git refs,
execute Host operations, grant production authority or perform a cutover.

## Semantic ownership and identity

`transactions.py` owns validation, operation meaning, evidence, lifecycle and
admission. The adapter owns atomic persistence, compare-and-swap, result lookup
and serialization of competing writers. The injected identity port authenticates
the current session; the injected trusted clock checks expiry. Neither a principal
string inside a request nor an old advisory result is an authority grant.

K2 adds registered envelope kinds in `schema/context-kernel-transaction.schema.json`:
TransactionRequest, AuthorityDecision, NativeRecordRevision, SandboxSnapshot,
TransactionReceipt, ReferenceGovernance and ExternalEvidenceReference. K1's bytes,
version, imported objects and golden vectors are unchanged. The registry is extended
additively; unregistered kinds still fail. Every listed field is hashed using K1
serialization. Operation arrays preserve order; snapshot manifests sort by identity.

A request includes project, opaque project-unique transaction ID, principal-scoped
idempotency key, exact base snapshot, exact governance version, ordered operations,
expected revisions, evidence references, explicit semantic time and dependencies.
Its digest binds all those fields, including transaction ID and key. Retrying means
resending that exact immutable request. A different ID is a different request.

A commit-time AuthorityDecision binds request digest, project, principal, base,
old governance, ordered action/target scope, live authentication evidence and the
trusted check time. Hash dependencies are request → decision → native revisions →
successor snapshot → receipt. Revision predecessors and snapshot bases point only
backward; opaque transaction IDs do not reference their receipt hashes.

## Operations and invariants

- create_record/revise_record/transition_record carry complete registered metadata,
  body and rationale. Kind/logical identity/creation time do not change; updated
  time matches explicit semantic time and does not move backward. A revision cannot
  silently change lifecycle; transition_record is explicit. This covers obligations
  including completion and supersession without inventing a separate record family.
- relate adds/removes related or supersedes edges; supersedes updates its reciprocal
  edge. Every affected revision has an exact base precondition. The whole successor
  graph is checked, so reciprocal transitions may be expressed in one transaction.
- add_evidence stores immutable bounded bytes; add_external_evidence preserves a
  reference and known/unknown content digest without asserting availability.
- put_document replaces compact state, project documents or view declarations by
  exact document precondition. Paths are bounded to those namespaces. Active-work
  schema and top-level view identity/override/reference checks apply; view resolution
  and consumer compilation are still K3. Governance cannot bypass its dedicated op.
- set_governance uses the previous policy for admission. New grants never authorize
  their own installation. ReferenceGovernance grants project-wide named actions;
  it is a conformance policy, not an interpretation or replacement of GitHub ACLs.

Unsupported operations/kinds/schemas, missing evidence, stale revisions, invalid
lifecycle or invalid documents reject the entire transaction. Record mutations
require explicit evidence references; retained source assertions are not promoted
to verified facts. Temporary intermediate record states are never visible.

Bootstrap explicitly seeds a reference policy. It retains K1 import_origin and all
raw historical objects. Imported canonical record files, category indices and the
Git authority declaration stay historical under that origin, while the active
sandbox uses record revisions and its separate policy. They are not two writable
representations. K3 must build the compatible read projection; K2 makes no current
Git-tool/query equivalence claim.

## Concurrency, idempotency and failures

A durable pending reservation binds (project, authenticated principal, key) to the
complete request digest and binds the project transaction ID uniquely. Pending
requests/objects are staging, not canonical publication. SQLite BEGIN IMMEDIATE
serializes writers across connections/processes. Head CAS, newly reachable objects,
receipt and committed idempotency result publish in one database transaction.

Same-key identical requests return the stored committed result before checking
whether their original base is now stale. Changed payload/key reuse is rejected;
project transaction IDs cannot be rebound. Terminal rejections are also retained,
so changing a rejected request requires a new deliberate transaction, not silent
retry mutation. A pending same-key attempt can be recovered after process restart.

Outcomes are committed, not_committed, outcome_unknown and access_denied. Definite
pre-commit rejection does not move the head. Loss of acknowledgement or an adapter
exception with unresolved persistence returns outcome_unknown. Result lookup uses
the caller's authenticated principal and current read_result permission; absent or
pending is unknown, never proof of rollback. Access denial makes no assertion about
whether an earlier request committed. Abort serializes with commit and cannot undo
a completed transaction; it returns that committed receipt if commit already won.

Explicit depends_on transaction IDs must have committed results. Callers must stop
dependent mutation after outcome_unknown and use result lookup/same-key retry; a
new key is not a recovery protocol. The server cannot infer which acknowledgements
a caller actually received. It checks declared dependencies but does not claim to
detect undisclosed causal relationships from arbitrary operation text.

Advisory propose/validate does not persist or reserve anything. At commit, after
semantic preparation and while holding the writer lock, identity is reauthenticated
and old-policy admission is evaluated again. There is a residual interval while
immutable decision/revision/receipt objects are finalized and the database commits;
external revocation is not atomic with SQLite. K2 claims no stronger fencing.
Session credentials never enter requests or receipts; authentication evidence must
be a non-secret reference supplied by the trusted identity adapter.

## Validation boundary

The fixed suite races different writers and same-key retries; changes a key's
payload; replays after head advancement; revokes identity after advisory validation;
rejects expiry, mismatched principals/governance and self-authorizing updates;
checks lifecycle atomicity, evidence, abort races and explicit unknown dependencies.
Child-process os._exit injection covers reservation, before commit, and after commit
before acknowledgement. Reopening the file and same-key recovery must yield exactly
one receipt and matching head. A known pre-commit fault leaves no successor objects.

SQLite uses WAL and synchronous=FULL. Process-restart tests establish retained
receipts under that tested failure model, not hardware/power-loss certification,
network partitions or production filesystem durability. No memory-only test is
presented as crash-recovery proof. K3, K4 and production authority need their own
batch evidence.
