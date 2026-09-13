# Genesis Import Audit — Foundation

## Scope

This slice reconstructs the durable architectural intent and deferred cognition of `qiven-foundation` at verified main pin:

`f1880847e046425c7f3f3cad22a07d0008aad359`

The goal is not to duplicate every public header into qiven-context. The goal is to preserve the architecture, current Phase I surface, and important `not now / revisit later` cognition that a future jason-brother needs in order to continue coherently.

## Primary committed evidence reviewed

- `docs/architecture/foundation.md`
- `AGENTS.md`
- `docs/engineering/worker-protocol.md`
- `README.md`
- `CMakeLists.txt`
- `.github/workflows/ci.yml`
- Phase I main commit `f1880847e046425c7f3f3cad22a07d0008aad359`

## Retrospective evidence used conservatively

- prior-session reconstruction that a generic ScopeExit/defer primitive was explicitly noticed and intentionally left out of Phase I because no concrete downstream need existed.

This retrospective item was not upgraded into a promise to implement the primitive. It became a deferred revisit obligation whose trigger is concrete repeated downstream demand.

## Promoted canonical records

Decisions:

- `ADR-0007` — keep Foundation small, foundational, and downstream-demand-driven;
- `ADR-0008` — make ownership, failure behavior, and allocation semantics explicit;
- `ADR-0009` — separate native C++ representation from ABI / IPC / wire / persistent boundaries.

Memory:

- `MEM-20260913T181224Z-F041D2` — verified Phase I public surface and build form;
- `MEM-20260913T181224Z-5BA4E1` — portability/CI contract at the verified pin.

Obligations:

- `OBL-20260913T181224Z-9E27A4` — design one common result/status abstraction when a real public API first needs structured recoverable status;
- `OBL-20260913T181224Z-A3F690` — reconsider ScopeExit/defer only when repeated real downstream cleanup patterns justify a Foundation primitive.

## Important negative knowledge preserved

Foundation is explicitly not:

- a miscellaneous `utils` repository;
- a product/domain layer;
- a wrapper around every OS or standard-library feature;
- a place to hide expensive work behind convenience APIs;
- a compatibility layer for preserving poor historical abstractions.

No mutable process-global default allocator is part of the Foundation model. Core semantics do not require exceptions or RTTI. Native object layout is not implicitly a transferable format or stable ABI.

## Non-promoted implementation details

The import did not create separate canonical records for every Phase I header or helper. Those details remain recoverable from Git at the pinned commit. The current surface is summarized only to support cold boot and architectural orientation.

The exact first historical date for each Foundation rule was not reconstructed where the evidence reviewed here did not establish it. The records use current materialization timestamps while their bodies identify the historical source pin.

## Residue pass

Recovered `not now` cognition:

1. a common Foundation result/status abstraction is intentionally deferred until a concrete API need exists;
2. ScopeExit/defer is not a Phase I primitive and should return only under concrete downstream pressure.

No additional Foundation-core deferred item from the reviewed evidence was promoted in this slice. Cross-domain integration residue — including Devkit adoption/reconciliation and Math dependency composition — belongs to later Genesis slices and the final cross-domain residue audit.

## Import status

Foundation core Genesis slice: **COMPLETE**.

Cross-domain residue audit: **PENDING**.
