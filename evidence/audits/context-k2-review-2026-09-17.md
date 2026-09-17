# ContextKernel K2 review and gate — 2026-09-17

## Scope

The owner authorized continuing after K1. Remote baseline is K1 merge
`fb0223cc18f71fac0d4ed2b492327a0657e12fb7`. jason-brother implements only ADR-0033's
K2 transaction/authority/idempotency batch under ADR-0032 portable validation and
ADR-0021 merge authority. GitHub remote remains canonical; Host is still paused.

## Engineering review

K2 separates request identity, live authentication, old-policy authorization,
atomic publication and recovery. An authenticated project's sandbox policy is
explicitly seeded rather than inferred from names in imported Git metadata.
Native revisions preserve predecessors; imported unknown authentication is not
retroactively upgraded. Native active manifests and historical source documents
are separated to prevent dual writable representations.

The storage choice here is a SQLite restart-capable reference adapter. It provides
cross-process writer serialization and one atomic receipt/result/head boundary.
It is not selected as the production storage product. Staged key reservations
survive crashes but are not canonical state. Definite rejection, unknown outcome
and access refusal have different return meanings. Replay lookup precedes stale
base checks. Same-key payload changes and project transaction-ID reuse fail.

Identity is checked again after semantic preparation, against existing governance.
The residual external-revocation-to-database-commit interval is explicitly retained
as a limitation; K2 does not claim cross-provider fencing. Source-format parsing
was moved out of the Git importer into a shared semantic boundary so commands do
not depend on the Git adapter to interpret registered metadata.

## Acceptance corpus and pending gate

The transaction suite covers two-writer and same-key races, receipt identity after
head advancement, changed requests, stale revisions/governance, missing evidence,
revocation and expiry, self-authorizing policy changes, reciprocal lifecycle
transactions, external evidence unknowns, abort/commit races and result access.
Actual child-process termination at three boundaries tests restart recovery;
known pre-commit failure proves no successor object publication. This is process
crash evidence, not power-loss or production-storage certification.

The exact implementation candidate must pass the integrated portable runner and
repository validation. This review is not a PASS claim; exact results, log digest
and final publication checks are recorded after the gate. K3 view/query equivalence
and K4 export/restore remain separate and are not started here.
