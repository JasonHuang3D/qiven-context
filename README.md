# qiven-context

`qiven-context` is Qiven's durable, Git-versioned project cognition and continuity repository. Its purpose is to let the project survive session loss, turn failures, model/provider replacement, agent replacement, representation/transport replacement, and authorized human-operator changes without making any one conversation or model-native memory authoritative.

The canonical repository is `JasonHuang3D/qiven-context` on GitHub. GitHub remote state is the current trust anchor for repository identity and project-governance authentication. Local clones are working copies and may be stale, contaminated, or disposable.

## Active semantic surfaces

- `collaboration/` — normative project-wide operating, continuity, validation and handoff contracts.
- `state/` — compact current operational state; never a historical transcript.
- `decisions/` — ADRs and their lifecycle.
- `memory/` — durable facts, lessons, invariants, risks, protocols, and negative knowledge.
- `obligations/` — explicit future work, commitments, revisit triggers, and validation gaps.
- `projects/` — durable project/domain models.
- `views/` — participant-specific ContextView material: human/agent adaptation, environment profiles, and workflow profiles that must not redefine project truth.
- `sessions/` — bounded session-checkpoint continuity evidence for recent work. No canonical project cognition may exist only here.
- `evidence/audits/` — curated durable evidence and incident/acceptance records.
- `schema/` — record contracts.
- `generated/` — rebuildable derived context and ignored local handoff outputs only.
- `tools/`, `tests/`, `benchmarks/` — validation and derived retrieval machinery.

Historical `ledger/` data and the placeholder `evidence/ci`, `evidence/handoffs`, and `evidence/research` buckets are retained only as explicit legacy/deprecated history. They are not active write surfaces.

## Continuity model

Project truth is identity-independent. A `ContextView<Agent, Human>` may adapt presentation, workflow, environment knowledge, and interaction to a concrete participant combination without changing that truth. Mutation depends on explicit project authority. Current authentication is intentionally account-level: GitHub authenticates the `JasonHuang3D` root principal; Qiven does not attempt to prove biological identity.

Project Continuity defines **what a fresh consumer must reconstruct**. The delivery path is a separate profile and must be named by any acceptance claim:

- **remote cold boot** reads an exact canonical GitHub Context ref;
- **session checkpoint continuity** carries bounded progress evidence between sessions;
- **Canonical Artifact Handoff** crosses an isolation boundary through one self-describing export-derived artifact before live repository verification;
- **Human Succession** proves takeover by a different authorized human operator.

Passing one profile does not prove the others. ContextKernel K4 specifically requires Canonical Artifact Handoff under `collaboration/context-handoff-contract.md`; K5, after K4 acceptance, is the separate lossless token-efficient transport optimization and must preserve the K4 semantic closure exactly.

Current ChatGPT + Jason adaptation lives under `views/chatgpt-jason.yaml`; it references JasonPC environment and local-execution workflow profiles. Different agents, humans, or machines may use different views while reading the same canonical ProjectContext.

Conflicts are preserved when discovered but are not a permanent operating mode. When evidence permits, conflicting active records must be reconciled into one current canonical interpretation while displaced records remain historically available as superseded, archived, retired, or legacy material.

Start with `BOOTSTRAP.md`. Project Continuity reconstruction is defined in `collaboration/project-continuity-acceptance.md`; Canonical Artifact Handoff isolation is defined separately in `collaboration/context-handoff-contract.md`. Validation authority and its task-specific limits are defined in `collaboration/context-validation.md`.

Never store credentials, tokens, private keys, recovery codes, or other secrets in this repository.
