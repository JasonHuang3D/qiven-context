# Foundation

Genesis core import status: **COMPLETE** for the Foundation architecture/ownership/representation slice. The later cross-domain residue audit may still add or relate records discovered elsewhere.

## Current verified state

- Live main pin tracked by qiven-context: `f1880847e046425c7f3f3cad22a07d0008aad359`.
- Qiven program state: Foundation Phase I complete; formal Devkit adoption is still pending.
- Build form at the verified pin: C++20 static library `qiven-foundation`, CMake alias `qiven::foundation`.
- Public C++ namespace root: `qiven::`; there is intentionally no `qiven::foundation` namespace.

## Durable architecture recovered by Genesis

- Foundation stays small, foundational, low-dependency, and downstream-demand-driven rather than becoming a general utilities repository (`ADR-0007`).
- Ownership, allocator provenance, raw-storage/object-lifetime separation, checked bounds arithmetic, and failure behavior are explicit (`ADR-0008`).
- Native C++ representation is local; ABI, IPC, shared-memory, wire, and persistent formats require deliberate transferable contracts (`ADR-0009`).
- Portability is enforced through explicit platform boundaries and continuously exercised CI targets.

## Phase I public vocabulary

At the verified pin the public surface includes platform/compiler/config/contracts/types primitives; checked arithmetic/integer/span helpers; bounded byte cursor/writer and endian conversion; and memory primitives including `AllocatorRef`, `Layout`, `LinearArena`, `SystemAllocator`, `OwnedAllocation`, `OwnedObject<T>`, and `OwnedArray<T>`.

## Deferred Foundation cognition recovered

- A common result/status abstraction is intentionally deferred until a real public API needs structured recoverable status; modules must not invent incompatible ad-hoc result vocabularies meanwhile.
- A generic ScopeExit/defer primitive was explicitly left out of Phase I and should be reconsidered only if repeated real downstream cleanup patterns justify Foundation ownership.

## Evidence

Primary source: `JasonHuang3D/qiven-foundation` architecture, CMake, agent/worker protocol, CI, and Phase I main commit at the verified pin. See `../../evidence/audits/genesis-foundation-slice.md` for the import audit.
