# Robotics

Genesis historical import status: **SLICE COMPLETE** for the current roadmap direction and staging boundaries. No qiven-robotics or qiven-physics implementation repository is asserted by this document.

## Product objective

Build a robotics/simulation product in the class of a MuJoCo-like simulator, with a long-term ambition to exceed clone-level capability as Qiven's math, geometry, scene, compute, and eventually physics layers mature.

## Durable boundaries

- Robotics/simulation is the product problem; a custom physics engine is not the prerequisite for starting it.
- Reuse shared native math/geometry/scene/compute layers where those boundaries are already justified.
- Evaluate mature external simulation/physics engines pragmatically before deciding Qiven must own deeper physics internals.
- A future `qiven-physics` layer should exist only when concrete simulator requirements demonstrate missing capabilities and a stable independent ownership boundary.
- Product/control-policy semantics remain above low-level math and physics representation layers.

## Deferred cognition

Before creating `qiven-physics` or committing to a custom native physics engine, document the simulator requirements that existing engines fail to satisfy, the responsibilities that belong to robotics versus shared compute/geometry versus physics, and the validation targets for the new layer. See `OBL-20260913T183819Z-9A4F21`.

## Evidence

See `memory/records/MEM-20260913T183819Z-C2D841.md`, `decisions/ADR-0017.md`, `decisions/ADR-0018.md`, and `evidence/audits/genesis-ecosystem-slice.md`.
