# Genesis Import Audit — Ecosystem Roadmap / CAD / Gas / Robotics

## Scope

This slice reconstructs Qiven's cross-product dependency topology, repository-splitting policy, long-term product sequence, and the current architectural boundaries for CAD, industrial-gas management, robotics/simulation, and future native physics.

## Sources reviewed

Primary committed evidence:

- `JasonHuang3D/qiven-foundation@f1880847e046425c7f3f3cad22a07d0008aad359:docs/architecture/foundation.md`
- `JasonHuang3D/qiven-math@912ae067784fb5cd336925ff6f6d071b85297bff:docs/architecture/math.md`
- `JasonHuang3D/qiven-devkit@214dc5c933ef4f7db3fce9795a39d49ca382dfbf:README.md`
- current qiven-context short-horizon `state/roadmap.yaml`.

Retrospective evidence:

- prior-session reconstruction of the Qiven global roadmap;
- prior-session reconstruction of the CAD semantic pipeline and provider-boundary discussion;
- prior-session reconstruction of industrial-gas stack boundaries;
- prior-session reconstruction of robotics/simulator and future physics staging.

Repository discovery during this slice did not surface installed repositories named `qiven-cad`, `qiven-gas`, `qiven-robotics`, or `qiven-workspace`; therefore product documents here describe accepted direction and preserved reasoning, not implementation state.

## Important roadmap distinction

`state/roadmap.yaml` is the current execution queue: Context Phase 0, Foundation Devkit reconciliation/adoption, then Math Batch 008. It is not a complete long-term product roadmap. The longer CAD -> gas -> robotics/simulation -> deeper native-physics sequence is preserved separately as project cognition so short-horizon scheduling does not erase product intent.

## Promoted canonical records

- `ADR-0017` — layer the shared native core by semantic responsibility rather than force all verticals into one stack;
- `ADR-0018` — delay repository splits and qiven-workspace until real reuse/coordination pressure exists;
- `ADR-0019` — CAD is a provider-bounded building-semantic pipeline, not arbitrary DWG interpretation or DCC automation architecture;
- `ADR-0020` — industrial-gas product stack remains independent from the native C++ core unless domain requirements justify coupling;
- `MEM-20260913T183819Z-C2D841` — current long-term product sequence;
- `OBL-20260913T183819Z-2C7A11` — create qiven-workspace only on real orchestration pressure;
- `OBL-20260913T183819Z-5D8E32` — establish headless CAD/provider/semantic pipeline before editor-first implementation;
- `OBL-20260913T183819Z-9A4F21` — reconfirm robotics versus physics ownership before qiven-physics/custom-physics commitment.

## Rejected or deliberately bounded alternatives

- one universal C++ dependency graph for all Qiven products;
- making units depend on math merely for convenience;
- pre-creating the entire projected repository graph;
- treating arbitrary unknown DWG semantic understanding as the initial CAD scope;
- making AutoCAD/3ds Max/UE UI automation the core CAD architecture;
- starting robotics by first building a custom physics engine;
- treating future repository names as already-approved implementation commitments.

## Residue pass

Recovered future-triggered cognition:

1. qiven-workspace stays deferred until multi-repository coordination is repeatedly painful;
2. CAD must establish provider, normalized-entity, topology, building-model, and headless end-to-end contracts before editor-first work;
3. deeper native physics stays deferred until concrete simulator requirements justify a dedicated ownership boundary.

## Gaps

The detailed CAD algorithm/library shortlist, exact product milestones, robotics engine comparisons, and industrial-gas workflow model were not reconstructed as accepted architecture in this slice because the available evidence does not justify promoting every past exploration into canonical decisions. Those subjects should be recovered in later project-specific passes when stronger source evidence is available.
