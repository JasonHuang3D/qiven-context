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

## Acceptance corpus and gate

The transaction suite covers two-writer and same-key races, receipt identity after
head advancement, changed requests, stale revisions/governance, missing evidence,
revocation and expiry, self-authorizing policy changes, reciprocal lifecycle
transactions, external evidence unknowns, abort/commit races and result access.
Actual child-process termination at three boundaries tests restart recovery;
known pre-commit failure proves no successor object publication. This is process
crash evidence, not power-loss or production-storage certification.

PASS on exact implementation candidate
`4e18ffadf6d112539e68fe2ba9e2e0413d6efa03`, tree
`098967e48cd885da767c59346d39ad544bfafe59`.

Environment: Python 3.12.14, SQLite 3.53.1, Linux; repository-pinned PyYAML 6.0.2
and jsonschema 4.23.0 in the isolated agent dependency directory. No JasonPC execution.
`python tools/test_all.py`: 13 portable suites / 175 tests PASS, zero failures,
14.05 seconds elapsed. K2 adds 26 tests to the 149-test K1 baseline. The unchanged
Windows-only resolver suite is explicitly skipped on Linux. Repository validation
also PASS; the candidate worktree was asserted clean and diff whitespace checked.
The first integrated implementation gate passed without code repair/retest.

Verbatim output: `evidence/audits/context-k2-python-validation-2026-09-17.txt`.
SHA-256: `bbd9768cf92b6ad1301ca11a9872e92b5d7d95cadec82d1df42133d6bef92256`.

Acceptance closeout is restricted to this audit, raw log, compact current state,
active work and session continuity. Code, schemas, contracts and fixtures remain
identical to the fully tested implementation. Final exact-head repository validation
and local/remote tree and parent checks are recorded in the merge commit. The full
implementation evidence carries forward over that reviewed five-path closeout.

K2 is accepted for the reference transaction semantics and demonstrated process
restart model. K3 view/query equivalence and K4 export/restore are separate and have
not started. Production identity integration, external revocation fencing, power-loss
certification, production storage and authority cutover are not established here.
