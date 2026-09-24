# CA-0 Exit Report — Consumer Contract and Causal Baseline (2026-09-24, v23)

Consolidates the CA-0 transaction against the roadmap amendment §4 CA-0
exit gate. CA-0 is contract-and-baseline work: no production activation
implementation (that is CA-1, bounded below).

## Exit-gate rows

| # | Gate row | Status | Evidence |
|---|---|---|---|
| 1 | All four claims have independent acceptance statements | PASS | Acceptance protocol §1 (Continuity §1.1, Activation Correctness §1.2, Cognitive Utility §1.3, Mechanical Governance §1.4 + non-claims §1.5); ADR-0050 Decision 1; landing manifest binds the four TCA docs |
| 2 | Six or more sealed fixtures cover known critical boundary classes | PASS | 8 sealed fixtures + rubric + digest manifest (evidence/cognition/fixtures/); classes per manifest coverage note |
| 3 | Current cold-boot cost and outcome baseline are reproducible | PASS (cost) / QUALIFIED (outcome) | baseline-cold-boot-2026-09-24.md: exact file lists + bytes at pinned revisions; token estimator stated (÷4, sealed rule: not reusable for Profile C); time-to-first-design has no instrumented timer — recorded as honest absence with the CA-2 metering obligation; first-pass quality baseline = MVP-4's 3 failed H1 attempts on mature hazard classes |
| 4 | Every initial protected rule has one canonical owner and exact source reference | PASS | Bootstrap set below (owner + source per rule); selector schema v1 (runtime/cognition/selector-schema.md) |
| 5 | Concrete controlled task-ingress design + real-harness feasibility evidence, or recorded blocker | PASS with named residual | ingress-feasibility-2026-09-24.md: documented `additionalContext` channel + live same-mechanism observation + paste-ready owner trial; residual = live injection needs owner-enabled config; sequencing NOT re-deliberated |
| 6 | No design assumes more prompt volume equals better attention | PASS | Governance program CG-10; roadmap risk table; Profile C criterion 6 (input REDUCTION as a pass condition) |
| 7 | The program has explicit non-goals and a rollback boundary | PASS | Governance program §13; roadmap §8 (rollback triggers) + §8.5 transition discipline |

Additional CA-0 work items disposition:

- Claims/taxonomy/task-schema vocabulary: risk classes R0-R3, phase
  vocabulary, boundary kinds — selector schema v1 + (devkit batch)
  engineering-task-v1 schema draft with the same vocabularies.
- Canonical source inventory by repository with ownership:
  runtime/cognition/source-inventory.yaml.
- MVP-4 failures mapped to incident scars and sealed fixtures: trial 1 →
  MEM-20260923T115500Z-A1B2C3 (+ ADR-0049) → fixture F-02; trial 2 →
  MEM-20260924T032100Z-D4E5F6 → fixture F-01; trial 3 →
  MEM-20260924T032000Z-C1D2E3 + incident audit 2026-09-24 → fixtures
  F-03/F-08.
- Old Python compiler recorded as sealed historical input: ADR-0040/0041
  (already law); roadmap §0 restates; no production path touches it.
- Root ADR + program obligation: ADR-0050 + OBL-20260923T190500Z-D6E7F8
  (landed in v22).
- MVP-4 corrective lane incident pack (declared program pack):
  runtime/cognition/mvp4-corrective-pack.yaml (recorded, revision-pinned,
  expiry = real-H1 pass).

## Protected bootstrap set (initial; one owner + exact source each)

| Rule | Owner repository | Exact source |
|---|---|---|
| TCA-GOV constitutional laws CG-1..CG-12 | qiven-context | collaboration/cognitive-governance-program.md §3 (+ §5-§11 sections per landing manifest) |
| TCA-ARCH activation pipeline/policy/lock | qiven-runtime | docs/architecture/task-cognition-activation.md §0/§7/§9/§10-§13/§17 @f0ca5b7 |
| TCA-ACCEPT profiles/fixtures/statistics | qiven-context | collaboration/cognitive-effectiveness-acceptance.md §2/§4-§8/§10 |
| TCA-ROADMAP sequencing + corrective lane | qiven-runtime | docs/architecture/runtime-mvp-roadmap-amendment.md §0/§4/§5.1/§8.5 @f0ca5b7 |
| Borrowed-lifetime scar | qiven-context | memory/records/MEM-20260924T032100Z-D4E5F6.md |
| Wire-contract scar | qiven-context | memory/records/MEM-20260924T032000Z-C1D2E3.md |
| Assumed-field/H1-kit scar | qiven-context | memory/records/MEM-20260923T115500Z-A1B2C3.md |
| Heredoc law | qiven-context | memory/records/MEM-20260921T203500Z-D2A7F4.md |
| Process custody law | qiven-context | qiven-context decisions/ADR-0048.md |
| Semantic ownership law | qiven-context | decisions/ADR-0024.md (+ foundation restatement) |
| H1-kit standard | qiven-devkit | docs/engineering/h1-kit.md |
| Handoff boundary H1-H4 + long-running | qiven-context | collaboration/human-handoff-boundary.md |
| Operating contract (authoring/exec/timeout laws) | qiven-context | collaboration/operating-contract.md |

Enforcement note (roadmap §6.1): repository-gate rejection of protected-class
records lacking selector metadata begins only after a SEPARATE schema/
bootstrap gate transaction — not this transaction.

## Bounded CA-1 batch declaration (declared at CA-0 per the stall trigger)

**Scope** (TCA-ARCH §0/§10 pipeline, roadmap CA-1 work list):

1. task descriptor normalization (observed vs claimed provenance);
2. validation of `runtime/cognition-core.yaml` +
   `runtime/cognition-activation-policy.yaml` (qiven-context instances);
3. exact multi-repository source lock + immutable activation-index sidecar
   (own ActivationGeneration; never appended to the published
   qiven-cognition-bundle-v1);
4. P0/P1 protected evaluation without ranking; semantic-owner resolution
   over capability manifests; deterministic P3/P4 ranking;
5. TaskCognitionBundle construction + atomic publication;
   ContextActivationReceipt issue/persist/explain/invalidate/verify;
6. one-shot native commands over the production core;
7. conformance/determinism/budget/corruption/crash tests (Profile A +
   Profile B of the acceptance protocol).

**Explicit exclusions** (unchanged from roadmap CA-1): no Python production
dependency; no LLM/embedding/vector/network call; no generative
summarization; no K5 compression; no Runtime complete-mediation scope
expansion; no canonical mutation through the query path.

**Resource ceiling**: one implementation batch = at most 3 runtime PRs + 1
context policy-instance PR + 1 devkit schema PR, landed under long-running
delegated H2 with receipts; exceeding the ceiling without Profile A+B PASS
triggers the stall review, not silent extension.

**Exit evidence**: Profile A PASS (determinism, fault matrix) + Profile B
PASS (100% protected recall on the sealed corpus, budget-pressure,
mutation tests) at the exact candidate head.

**Stop condition (OBL stall trigger)**: if the batch closes or its exit
attempt fails without Profile A and B passing, further feature work stops
for a recorded program review.

## Multi-repository source lock scoping (inside CA-0's estimate)

- Locked repositories + path filters: qiven-context (memory/records,
  decisions, obligations, state, collaboration, runtime/cognition) +
  qiven-devkit (docs/engineering, docs/conventions, docs/schemas) +
  qiven-foundation (include/qiven, docs/architecture) + qiven-runtime
  (docs/architecture, include). qiven-docs deliberation records enter only
  when explicitly referenced by policy (P4).
- Lock record per repository: commit SHA + tree filter + per-file content
  digest (sha256), resolved from validated LOCAL checkouts pinned to exact
  revisions — no network fetch, dirty checkouts rejected (TCA-ARCH §9).
- Estimated corpus at seal: ~46 memory records + 45 ADRs + 5 open
  obligations + 26 collaboration docs + devkit/foundation/runtime surfaces
  (inventory file lists); measured corpus scale ≈ 300 KB core + policy
  instances — cold index build budget (< 5 s) is realistic for v1 full
  rebuild at this scale.
- Recovery: index/sidecar loss rebuilds from the pinned canonical sources;
  ActivationGeneration changes never mutate the execution RuntimeGeneration.

## Residual gaps recorded honestly

1. Profile C tokenizer + delivery metering pinned at trial time (baseline
   uses corpus accounting only).
2. Live `additionalContext` injection unobserved in this workspace until
   the owner-enabled trial (paste-ready in the feasibility record).
3. Devkit schema/task-taxonomy drafts and the foundation capability surface
   land as their own repository batches (same interval; separate receipts).
4. The roadmap's MVP-4 incident-specific assertions are now bound to exact
   artifacts (incident audit + scar records + revisions above); the H1
   rerun itself remains owner hands.
