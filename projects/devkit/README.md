# Devkit

Qiven Devkit: the infrastructure-tooling layer — repository templates,
engineering conventions and standards (ADR-0046 canonical), the Qiven
Operator runtime, the workspace resolver, and the ZCode hook router.

## Current state (2026-09-26)

- **Operator**: long landed and hardened — repository gates
  (`.qiven/operator.json` task/gate model), `qiven exec` v2 bounded
  process custody (ADR-0048: watchdog + Job-Object tree lifetime +
  lease), `qiven ci watch` (v31, identity-bound observation-only CI
  runner). The "Operator Phase 1" pause recorded in the old project
  entry is 2026-09-14 history.
- **Hook router**: `tools/hook_exec_router.py` at v4.3 (sweep split by
  inherent boundedness; live workspace-wide — the hook reads the
  working-copy script per call), enforcing ADR-0051 (deny →
  run_in_background re-call; exec-lease custody classes) and the
  heredoc-authorship deny.
- **Workspace resolver**: WR-1/WR-2/WR-3 landed
  (`tools/workspace_resolver.py`, `workspace_schemas.py`, the bootstrap
  in `qiven-workspace`; generation-bound lock, declarations, adapter).
- **Standards**: `docs/engineering/` (implementation, testing, H1-kit,
  Python standard, third-party dependencies) and `docs/conventions/`
  are Devkit-canonical per ADR-0046; templates rolled past 0.1.9 (exec
  v2 custody pin).
- **Devkit repair (PR4 audit) — ADJUDICATED and EXECUTED 2026-09-26**
  (owner verbatim "Devkit 修复批次裁定全部通过"): standards v2 landed
  (implementation-standard §16-§17 PR-1/PR-2; testing-standard §12 PR-3
  discriminating proof; design-first-workflow v2 — R2/R3 commit
  ordering, E4 boundary-semantics revision, PR-6 continuity trigger);
  the current operator contract published
  (`docs/operator-contract.md`; Phase-1 design museumed); entry points
  rewritten (README authority-resolution procedure, workspace reality,
  agent-entry shape, live-repository naming exemplars); the six §6.2
  consistency fixtures verified PASS at the candidate. The
  corresponding Context-side ADR-0044 dated scope note records the
  adjudication.

## Entry points and evidence

- Repository: `JasonHuang3D/qiven-devkit` (README, `docs/conventions/`,
  `docs/engineering/`, `docs/design/workspace-resolution*`).
- Governing decisions: ADR-0046 (layer model), ADR-0048 (custody),
  ADR-0051 (background execution), ADR-0052 (workspace endpoint),
  ADR-0053 §5a (delegation briefs).
- History: the Phase-1-era project snapshot (Operator Phase 1 pause,
  template 0.1.2 pins, the 0.1.2 adoption story) is preserved at
  `legacy/projects/devkit/README-phase1.md` — dated 2026-09-14 history,
  not current state.
