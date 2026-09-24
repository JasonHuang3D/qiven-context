# Generated Temporary Artifacts Convention

## Purpose

A standardized location for tool-produced temporary artifacts (test outputs,
serialization snapshots, serialization golden files, trial artifacts,
profiling dumps, intermediate builds). These are files that:

- are produced by a tool or test during operation;
- have diagnostic or handoff value beyond the current process lifetime;
- must NOT be committed to the repository;
- must be findable and cleanly separable for cleanup.

## Location rule

```
${workspace}/.generated-temp/<tool-name>/<run-id>/
```

- `${workspace}` is the workspace root (for example `D:/JasonWork/`), or for
  CI/sandbox environments the directory containing the program/script.
- **Never hardcoded in code.** The path is passed as a parameter, environment
  variable, or configuration. Code receives a path; it does not construct one.
- `.generated-temp` starts with a dot: it is invisible in normal directory
  listings and universally git-ignored.

## Internal organization

```
.generated-temp/
├── artifact-trial/           # by tool name
│   └── 2026-09-20T041500Z/   # by run: UTC timestamp or explicit run ID
│       ├── snapshot.txt       # artifact payload
│       └── manifest.json      # metadata (tool version, source commit)
├── test-outputs/
│   └── <test-name>/<timestamp>/
├── profiling/
│   └── <tool-name>/<timestamp>/
└── ...
```

Rules:

1. **First level = tool name.** Each tool owns its subtree. No cross-tool
   file dumping.
2. **Second level = run identifier.** UTC timestamp
   (`YYYY-MM-DDTHHMMSSZ`) or an explicit run ID passed by the caller.
   Multiple runs of the same tool coexist without overwriting.
3. **No files at the `.generated-temp` root.** Everything lives inside a
   `tool-name/run-id/` pair.
4. **A tool that writes here MUST document its subtree in this file** (or in
   its own architecture docs) so cleanup scripts know what is safe to remove.

## Git and cleanup

- `.generated-temp/` is universally git-ignored (add to `.gitignore` in every
  repository that has a workspace-level `.generated-temp`).
- Cleanup is per-tool: `.generated-temp/<tool-name>/` can be removed
  independently without affecting other tools' artifacts.
- Retention policy: by default, artifacts are kept until manually cleaned.
  Tools MAY implement their own retention (for example, keep last N runs).

## Adding a new tool

1. Choose a tool name (lowercase, hyphens).
2. Document your subtree here or in your tool's docs.
3. Accept the output directory as a parameter; construct the default as
   `${workspace}/.generated-temp/<tool-name>/<timestamp>/`.
4. Add `.generated-temp/` to `.gitignore` if not already present.

---

## generated/ versus .generated-temp/ — ownership split (2026-09-20)

Two derived-output mechanisms exist; they are NOT redundant and must not
merge casually. Ownership rule:

- **`generated/`** (repository-level, git-ignored except its README):
  rebuildable DERIVED ARTIFACTS — deterministic, digest-bound outputs with
  durable value (K4 handoff artifacts, derived context packs). Large,
  kept until manually cleaned, produced by declared tools.
- **`.generated-temp/`**: EPHEMERAL tool state — logs, receipts, scratch,
  one-shot tooling. Per the rules above (tool-name/run-id layout).

**Scope follows binding**: ephemera that bind a REPOSITORY identity
(gate receipts for exact heads) live in that repository's
`.generated-temp/`; ephemera that bind a WINDOW or session (workflow
logs, stashed checkpoints, window tooling) live at the WORKSPACE root
`.generated-temp/`. A repository gains a `.generated-temp/` only when a
tool bound to it writes there (and then git-ignores it).

**Isolation-boundary rule for handoff artifacts (trial finding,
2026-09-20)**: an artifact that will be consumed across an isolation
boundary must NOT be handed over from inside any repository working tree
— placement inside the repo invited the consumer's first attempt to read
repository files (invalidated; see
`evidence/audits/context-v4-activation-trial-2026-09-20.md`). The MINTING
session performs the relocation copy to a neutral location
(`${workspace}/.generated-temp/handoff-out/`) before the human crosses
the boundary; storage of minted artifacts stays in `generated/`.
