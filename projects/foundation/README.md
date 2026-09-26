# Foundation

Qiven Foundation: the low-level C++ foundation layer (ADR-0017 layer law;
explicit ownership/failure/allocation ADR-0008; separate representation
boundaries ADR-0009).

## Current state (2026-09-26)

- **Landed**: Phase I surface (platform/compiler/config/contracts
  primitives; checked arithmetic/span helpers; bounded byte
  cursor/writer + endian; the allocator/memory model incl.
  `AllocatorRef`/`Layout`/`LinearArena`/`SystemAllocator`/
  `OwnedAllocation`/`OwnedObject<T>`/`OwnedArray<T>`; `Result<T,Reason>`
  incl. `Result<void>`; fnv1a64 + SHA-256). The machine-readable
  inventory with per-row headers and contracts is the repository's
  `docs/architecture/capability-surface.yaml` — that file, not this
  entry, is the live surface record.
- **Admitted, not yet landed**: `byte_builder` (owning growing bounded
  byte accumulator; ADR-0024 admission 2026-09-24; lands with the RR-0
  implementation batch in qiven-runtime).
- **Admission law**: semantic owner + first real consumer (ADR-0024);
  the current architecture contract is the repository's
  `docs/architecture/foundation.md` (replaced 2026-09-26 per the
  accepted PR4 audit; bootstrap original preserved under the
  repository's `docs/legacy/architecture/`).
- **Workspace role**: the dependency provider for qiven-math /
  qiven-context-draft / qiven-runtime (WR-3 Profile E; workspace lock
  resolution, zero consumer re-pins).

## Entry points and evidence

- Repository: `JasonHuang3D/qiven-foundation` (README, architecture,
  capability inventory).
- Placement decisions: `decisions/ADR-0024.md` (semantic ownership),
  ADR-0008/0009/0017 here; ADR-0007 is superseded.
- History: Phase I import/adoption audits live under `evidence/audits/`
  (`genesis-foundation-slice.md`,
  `foundation-managed-drift-reconstruction.md`,
  `foundation-devkit-adoption.md`); the Phase-I-era project snapshot is
  preserved at `legacy/projects/foundation/README-phase-i.md` (its
  "current" pins are dated 2026-09-13 history — do not read them as
  live state).
