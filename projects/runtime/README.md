# Qiven Runtime (Cognitive Control)

Status: **ACTIVE** — Runtime ADL program (ADR-0038 and the accepted
Component ADL landed 2026-09-21 in `qiven-runtime/docs/architecture/`).

## Mission

`qiven-runtime` is the trusted component system that converts observable
participant proposals into policy-derived, evidence-backed, exact-action
decisions at the boundary where Judgment becomes world-changing
Mechanism (ADR-0038). It consumes the frozen v4 semantics of
`qiven-context-draft` (@ `4cbc995`) as its immutable dependency, reads
canonical cognition through pinned Snapshots, and composes conjunctively
with `qiven-host` execution authority (ADR-0026).

The process/execution substrate this directory's model previously
described moved to `projects/process` (future `qiven-process`
repository) per ADR-0039.

## Next boundary

C++ interface/type design per Component ADL Section 90, then the
RCA-1..RCA-16 proof program. Day-one constraints: qiven-foundation
consumption (lower-layer preflight survey, pit P-49) and authenticated
adapter channels.
