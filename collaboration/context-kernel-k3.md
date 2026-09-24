# ContextKernel K3 (historical program contract — sealed, ADR-0040)

> Same seal classification as K1: accepted historical record; the Python
> program is museum material.


K3 owns a read-only bridge from immutable kernel objects to accepted R1 semantics.
It reuses the compiler, constraint and evidence machinery; it does not create a
second truth-selection implementation. Private directories are compatibility
projections, never writable authority. GitHub remains canonical.

## Read ports and projection

KernelReadSnapshot.capture pins an explicit snapshot using object/blob read ports.
The SQLite helper resolves a head once in a read transaction and detaches the
reachable read data before closing the connection. Queries use immutable bytes.
The caller owns store access admission; this library adds no remote endpoint.

Imported ProjectSnapshot reads preserve raw sources and Git provenance. Sandbox
reads use active documents and revisions only. Imported record bytes remain exact;
native revisions render JSON-compatible YAML front matter plus body. Indices are
derived from selected revisions. ReferenceGovernance renders explicitly as
quarantined sandbox policy, never as imported GitHub policy. Missing active inputs
never fall back to history. Kernel IDs and revision provenance remain separate
from projection hashes; sandbox projection has no claimed Git commit.

Wrong kinds/digests/project bindings, corrupt raw evidence, duplicate paths/IDs,
competing active representations, bad lifecycle and oversized sources fail reads.

## Views, query and derived ranking

resolve_view captures explicit UTC time, view ID, live assertions and completeness
evidence in immutable bytes. Assertions cannot override project data or authenticate
the caller. Every complete input set requires an evidence reference. Missing or
invalid referenced profiles fail; omitted view selects identity-independent context.

compile uses the existing deterministic compiler. bundle uses the existing candidate
builder with a snapshot-bound retriever. The K3 default is versioned lexical ranking
with ID tie-breaking. Model-backed ranking requires an explicit backend/config and
capture of ordered IDs/scores/metadata. Replay binds exact snapshot, prepared query
and config; mismatch, unknown/duplicate IDs, nonfinite scores or missing available
explicit IDs fail. Payloads are rehydrated from the snapshot, never from the index.
An unavailable supplied backend fails visibly without silently changing algorithms.

ContextBundle is an immutable envelope: v3 read payload, kernel/view/retrieval binding
and revision provenance. Both levels always say authorization: not_granted. Byte
budgets cover the complete compact UTF-8 JSON envelope. Whole optional rows may be
omitted with diagnostics; mandatory data, constraints and explicit IDs remain intact.
Compiler/projection/ranking versions are bound; real model quality is not claimed.

## Acceptance corpus

Compare old/new reads of an exact tree for default/selected views, current/history,
explicit IDs, protected constraints and unknown inputs. Exercise native revisions,
old-snapshot isolation, policy projection, input loss, corrupt objects/evidence,
invalid views, replay mismatch and protected budgets. Shared-compiler comparisons
prove adapter equivalence; independent assertions and existing R1 tests retain the
semantic oracle. Export/restore and production admission remain outside K3.
