# Foundation

Genesis core import status: **COMPLETE** for the Foundation architecture/ownership/representation slice. The later cross-domain residue audit may still add or relate records discovered elsewhere.

## Current verified state

- Live main pin tracked by qiven-context: `6c09151e1a52830c66e6c7a97b5b68740154f475` (`merge: complete Foundation Devkit adoption`).
- Qiven program state: Foundation Phase I complete and formally adopted into qiven-devkit managed lifecycle at template version `0.1.2`.
- Devkit ownership metadata is present in `.qiven/repo.json` and `.qiven/generated-state.cmake`; the managed set contains sixteen shared paths under schema 2.
- Build form: C++20 static library `qiven-foundation`, CMake alias `qiven::foundation`.
- Public C++ namespace root: `qiven::`; there is intentionally no `qiven::foundation` namespace.

## Durable architecture recovered by Genesis

- Foundation stays small, foundational, low-dependency, and downstream-demand-driven rather than becoming a general utilities repository (`ADR-0007`).
- Ownership, allocator provenance, raw-storage/object-lifetime separation, checked bounds arithmetic, and failure behavior are explicit (`ADR-0008`).
- Native C++ representation is local; ABI, IPC, shared-memory, wire, and persistent formats require deliberate transferable contracts (`ADR-0009`).
- Portability is enforced through explicit platform boundaries and continuously exercised CI targets.

## Phase I public vocabulary

The public surface includes platform/compiler/config/contracts/types primitives; checked arithmetic/integer/span helpers; bounded byte cursor/writer and endian conversion; and memory primitives including `AllocatorRef`, `Layout`, `LinearArena`, `SystemAllocator`, `OwnedAllocation`, `OwnedObject<T>`, and `OwnedArray<T>`.

## Devkit adoption outcome

Foundation's historical managed drift was reconciled semantically before ownership was asserted. The thirteen conflicting managed paths were reviewed individually; stronger shared engineering protocol moved upstream into Devkit 0.1.2, Devkit CMD control-flow defects were fixed upstream, and representation-only drift converged Foundation to the accepted managed snapshot.

A real adoption check then reached `16 EXACT / 0 MISSING / 0 CONFLICT`. Formal adoption created only `.qiven/repo.json` and `.qiven/generated-state.cmake`. Immediate post-adoption sync was byte-for-byte no-op for both ownership-state files, and the accepted merge preserved the exact locally validated candidate tree. See `../../evidence/audits/foundation-managed-drift-reconstruction.md` and `../../evidence/audits/foundation-devkit-adoption.md`.

## Deferred Foundation cognition recovered

- A common result/status abstraction is intentionally deferred until a real public API needs structured recoverable status; modules must not invent incompatible ad-hoc result vocabularies meanwhile.
- A generic ScopeExit/defer primitive was explicitly left out of Phase I and should be reconsidered only if repeated real downstream cleanup patterns justify Foundation ownership.

## Evidence

Primary source: `JasonHuang3D/qiven-foundation` architecture, CMake, agent/worker protocol, CI, and current accepted main. See `../../evidence/audits/genesis-foundation-slice.md` for the original import audit and the adoption audits above for the later lifecycle transition.
