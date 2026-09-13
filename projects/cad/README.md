# CAD

Genesis historical import status: **SLICE COMPLETE** for the current product direction and architecture boundaries. No qiven-cad implementation repository is asserted by this document.

## Product objective

Transform building-domain CAD/floor-plan source data into a semantic 3D result that can feed visualization, asset, scene, and runtime pipelines.

## Intended pipeline

DWG/DXF or another supported source
-> provider-specific parsing
-> normalized CAD entities
-> 2D topology
-> semantic building model
-> parametric 3D
-> mesh
-> exchange/runtime targets such as glTF, USD, or UE-oriented integration.

## Durable boundaries

- File-format/provider technology is replaceable behind an explicit source-provider boundary.
- Mature third-party parsing, geometry, optimization, UV, or meshing algorithms may be used; Qiven owns normalized data, semantics, contracts, and product behavior.
- Initial scope is building-domain interpretation, not arbitrary semantic understanding of every unknown DWG.
- AutoCAD, 3ds Max, Unreal Engine, or future DCC/editor tools are optional integrations, not the architecture of the semantic pipeline.
- Build and validate a headless deterministic pipeline/CLI before an editor-first shell.
- Performance work may use CPU/GPU libraries where justified, but acceleration choices must not redefine the semantic model.

## Deferred cognition

Before editor implementation, establish representative source fixtures, provider contracts, normalized entity semantics, topology rules, building-model contracts, and an end-to-end headless test path. See `OBL-20260913T183819Z-5D8E32`.

## Evidence

See `decisions/ADR-0019.md` and `evidence/audits/genesis-ecosystem-slice.md`.
