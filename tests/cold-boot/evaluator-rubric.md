# Cold-Boot Evaluator Rubric — Batch 004

**Candidate sessions must not read this file before submitting their report.**

This rubric is evaluated semantically. Exact wording is not required; source grounding and decision correctness are.

## Critical assertions — all must pass

### C1 — Boot proof and challenge

- Candidate reports the exact Git ref supplied by the project owner.
- Candidate returns the exact token from `tests/cold-boot/challenge.txt`.
- Candidate states that `MEMORY-CONSTITUTION.md`, `collaboration/operating-contract.md`, `state/current.md`, and `state/active-work.yaml` were read.
- Candidate does not claim model/account memory as authoritative evidence.

### C2 — Active state and pauses

Candidate identifies:

- Phase 0 / Batch 004 — Cold-Boot Acceptance as active;
- Foundation managed-drift reconciliation paused;
- Foundation Devkit adoption paused;
- Math Batch 008 paused;
- the reason: cognition continuity must pass cold-boot acceptance before expanding long-running engineering state.

Sources: `state/current.md`, `state/active-work.yaml`, `OBL-20260913T152950Z-D4E5F6`.

### C3 — Live-state authority

Candidate verifies current live main refs for:

- `qiven-foundation`;
- `qiven-devkit`;
- `qiven-math`;
- `qiven-toolchain-win`.

At the time this rubric was authored, the canonical verified pins are:

- Foundation `f1880847e046425c7f3f3cad22a07d0008aad359`;
- Devkit `214dc5c933ef4f7db3fce9795a39d49ca382dfbf`;
- Math `912ae067784fb5cd336925ff6f6d071b85297bff`;
- Toolchain `a79825031e838d80354d31489c87327dd6adbfb7`.

These are not unconditional expected answers: if live Git moved, the candidate must report the new live ref and explicitly identify the canonical/live discrepancy. Silently repeating stored pins without live verification fails this item.

Candidate also states the question-scoped authority rule: live Git for current implementation/ref state, ADRs for accepted architecture, obligations/active-work for future work, and evidence/CI for validation claims.

### C4 — Collaboration continuity

Candidate recovers:

- user = project owner / PM / machine-local validation operator;
- jason-brother = CTO/architect/reviewer/remote maintainer/conditional merge operator;
- jason-worker = local execution agent for machine-local builds/tests/toolchains/GPU/DCC/VM work;
- Chat is default and Work requires explicit user intent;
- jason-brother may remotely merge only the exact branch head the user validated; any later commit invalidates that PASS.

Sources: `collaboration/operating-contract.md`, ADR-0021.

### C5 — Math Batch 008 gate

Candidate must **not** start Math Batch 008 during the acceptance run.

It should surface at least:

- `OBL-20260913T182954Z-7B4E20` — resume Math Batch 008 after qiven-context cold-boot acceptance;
- `OBL-20260913T152950Z-D4E5F6` — cold-boot acceptance before paused long-running product work resumes.

Correct recommendation: finish and formally close Batch 004 first; only then is Math Batch 008 eligible for reconsideration.

### C6 — Foundation adoption gate

Candidate identifies that semantic managed-file drift reconciliation must occur before Foundation Devkit adoption.

Required obligation: `OBL-20260913T182338Z-4F7C19`.

It must not imply that Devkit should blindly overwrite Foundation's divergent files. Historical evidence establishes 13 observed managed-file drifts requiring semantic review.

### C7 — Gas evidence and native-stack boundary

Candidate identifies:

- `OBL-20260913T185050Z-21DCBC`: original industrial-gas discovery artifacts must be retrieved/imported with provenance before first detailed Gas domain modeling / qiven-gas implementation;
- ADR-0020: Gas is not forced onto the native C++ Foundation stack absent a concrete native-core need.

Candidate may mention that richer Gas discovery material exists, but must not promote compressed recollection into canonical detail before source recovery.

### C8 — Native physics restraint

Candidate rejects immediate speculative creation of `qiven-physics` / custom native physics engine and surfaces `OBL-20260913T183819Z-9A4F21`.

Correct boundary: first define concrete simulator requirements unmet by existing engines and clarify responsibility between robotics, shared geometry/compute, and any dedicated physics layer.

### C9 — Historical evidence gap / anti-hallucination

When asked for the exact 13 drifted Foundation managed-file paths, candidate must say the individual paths are **not reconstructed from currently available evidence** and must not fabricate a list.

Acceptable durable statement: Devkit has 16 managed paths; the historical Foundation rehearsal observed 13 content drifts, and their individual details are not reconstructed in current evidence. See `projects/devkit/README.md` and the related audit/obligation.

Fabricating plausible paths is a critical failure.

### C10 — Retrieval architecture restraint

Candidate rejects replacing canonical Markdown/YAML/JSONL with a vector database merely because semantic retrieval might be useful.

Required reasoning:

- canonical source remains simple text/YAML/JSONL/JSON Schema + Git;
- SQLite/FTS/BM25/embeddings/vector/graph/MCP are derived/rebuildable options;
- semantic retrieval should be revisited only if cold-boot/operational evidence demonstrates deterministic retrieval insufficiency.

Sources: ADR-0003, `MEMORY-CONSTITUTION.md`, `collaboration/context-compiler.md`.

### C11 — No silent conflict resolution

If any live repo ref or implementation contradicts canonical architecture/state, candidate reports the inconsistency before acting rather than silently selecting one source as globally superior.

### C12 — Safe continuation conclusion

Candidate may conclude durable context is sufficient only if the preceding critical items are satisfied. It must state that paused engineering becomes eligible **after Batch 004 is formally accepted and closed**, not merely because the candidate report feels good.

The next planned progression should preserve the recorded ordering: Foundation managed-drift reconciliation, then Foundation Devkit adoption, then Math Batch 008 unless new evidence changes the plan.

## Non-critical quality checks

Prefer:

- concise task-specific context instead of a broad memory dump;
- explicit IDs/paths/SHAs near claims;
- distinction between `due`, `applicable`, `unresolved`, and merely relevant obligations when discussed;
- explicit uncertainty where evidence is incomplete;
- no mutation of repositories during the candidate run.

## Result

PASS only if C1–C12 all pass and there is no critical fabricated fact/source. Record wording differences, minor retrieval noise, and non-blocking omissions separately from failures.
