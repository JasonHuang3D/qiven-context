# Context K1 review and acceptance boundary — 2026-09-17

## Remote baseline and authority

The owner reported work advanced in another account and explicitly authorized
review, direct remediation and continuation when coherent. jason-brother reviewed
remote main `3e1d1be` (full identity is bound in the publication parent) against
previous R1 merge `fa06d1475df85e4654838d133b2b2292bf305b34`.
The intervening work is R2 C07/C08 and revised accepted ADR-0033.
Portable Python validation follows ADR-0032 and batch merging follows ADR-0021.

## Findings and disposition

R2 correctly separates historical compiler behavior from the accepted R1 contract
and enforces reciprocal supersession. ADR-0033 correctly isolates semantic
ownership, authority, ambiguous commit outcomes, deterministic identity and staged
migration. No blocking architecture reversal is needed; K1 can proceed.

Two implementation failure classes are repaired in this batch:

1. R2's graph walker used recursion and consumed malformed relation elements after
   recording schema errors. A valid long chain could exceed recursion depth; a
   mapping inside a relation list could throw instead of returning diagnostics.
   A shared iterative, type-checked graph validator now serves repository and
   kernel import validation. This does not change accepted lifecycle semantics.
2. R1's Git capture used `git archive`, whose export attributes can omit or rewrite
   committed bytes. Exact import now uses raw tree/blob objects and disables Git
   replacement refs. Both old read tools and K1 use this same corrected source
   boundary. Import rejects links instead of following them.

## K1 implemented boundary

The versioned contract is `collaboration/context-kernel-k1.md`. K1 delivers a
registered immutable object model, canonical byte/digest rules, a single-owner
memory reference store and exact Git-tree import with lossless source recovery.
Canonical record schemas are content-pinned; unknown types, states and schemas
fail closed. Metadata/body, supersession and external source assertions survive.
Historical authentication and revision ancestry stay explicitly unknown. Import
receipts are separate from historical actions and never confer authority.

The suite includes fixed serialization vectors and rejection cases, a 2,500-record
lifecycle chain, real Git fixtures, export attributes, replace refs, invalid
schema/status/index/lifecycle, raw binary fidelity, object immutability, acyclic
object dependencies and import reproducibility. The exact candidate repository is
also imported using its full resolved commit ID. No historical Git depth is needed.

## Validation and publication

The implementation candidate receives one integrated portable regression gate plus
repository validation. The exact candidate SHA, test totals, raw output and any
failure are recorded in the acceptance closeout or merge evidence after execution.
This pre-validation review is not itself a PASS claim.

K2 is the next separate implementation boundary after K1 acceptance. K1 supplies
no durable receipts, concurrent commit, query-equivalence, complete backup/restore,
production storage, native executable or authority cutover proof. Host/DCR remains
paused and GitHub remote remains canonical.
