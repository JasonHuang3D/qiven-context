# Qiven Cognitive Governance Program

## From Durable Project Memory to Operational Engineering Cognition

> Status: Accepted by ADR-0050 (owner H2 2026-09-23)
> Date: 2026-09-23
> Decision owner: Qiven root governance principal
> Applies to: `qiven-context`, `qiven-devkit`, `qiven-foundation`, `qiven-runtime`, and every Devkit-managed Qiven repository
> Companion documents:
> - `qiven-runtime docs/architecture/task-cognition-activation.md` (bound at merge f0ca5b7)
> - `collaboration/cognitive-effectiveness-acceptance.md` (this transaction)
> - `qiven-runtime docs/architecture/runtime-mvp-roadmap-amendment.md` (bound at merge f0ca5b7)
> Deliberation record: `qiven-docs accepted/2026-09-23/` (PR #1, seven passes, corrections R1-R15)

## 0. Executive Decision

Qiven SHALL treat **task-related knowledge activation** as a governed production capability, not as a voluntary reading habit of the current LLM session.

The canonical repositories already preserve substantial project cognition:

- `qiven-context` preserves memory, decisions, obligations, evidence, current state, authority, and collaboration contracts;
- `qiven-devkit` owns shared engineering standards and executable workflow discipline;
- `qiven-foundation` owns low-level reusable vocabulary and strict ownership, representation, failure, and cost laws;
- `qiven-runtime` owns the external cognitive-control and execution-control boundary.

The missing capability is not more durable prose. It is a reliable path from the current task to the small set of cognition that must govern that task **before** design, implementation, testing, review, or an owner-live trial begins.

Qiven SHALL therefore add a Runtime-era **Task Cognition Activation** capability with these properties:

1. Canonical project cognition remains complete, Git-versioned, and authority-preserving.
2. Active working cognition is task-specific, bounded, explainable, and pinned to exact source revisions.
3. Critical rules, known hazard classes, explicit obligations, and applicable accepted decisions are protected from ranking loss.
4. The current participant does not decide whether mandatory activation is necessary; policy and observed task boundaries do.
5. Repeated failures migrate from prose into types, APIs, validators, gates, tools, or runtime enforcement.
6. High-risk engineering work is independently falsified; one session may execute the full engineering loop, but it MUST NOT remain the sole epistemic judge of its own high-risk assumptions.
7. No claim that Qiven amplifies engineering cognition is accepted until an isolated fresh-consumer acceptance protocol demonstrates that outcome.
8. The retired Python Context compiler/retrieval implementation remains sealed. It SHALL NOT be revived as the production path.
9. Context mutation latency SHALL NOT absorb full task compilation. Canonical writes and derived cognition activation are separate transactions with explicit consistency rules.

This program does not weaken governance. It moves governance out of undifferentiated prompt volume and into task-time selection, mechanical constraints, and independent evidence.

---

## 1. Problem Statement

### 1.1 Qiven has durable pain, but not yet a complete pain pathway

Qiven already records institutional pain:

- an incident audit preserves what happened;
- a memory record preserves the reusable scar;
- an ADR preserves a durable judgment;
- a collaboration or Devkit standard preserves expected conduct;
- a lower-layer primitive or tool may embody the correction;
- a regression test may preserve one detected failure shape.

These are necessary, but they do not prove that a future participant will apply the scar at the correct moment.

For governance purposes, the following distinction is normative:

```text
Stored pain     = the project can recover a past failure and its lesson.
Activated pain  = the lesson is delivered before a materially similar action.
Embodied pain   = the materially similar error is difficult or impossible to repeat.
```

A memory record that is never selected for the current task is stored pain only. A rule that is selected but can still be ignored is activated but not embodied. A rule has completed its governance lifecycle only when its recurrence risk is reduced by a proportionate mechanical or independently verified control.

### 1.2 The current retrieval boundary is behaviorally dependent

The sealed Context compiler and retrieval program left task-specific retrieval to the reading participant until Runtime provides the replacement. That was a legitimate response to an expensive, superseded Python program whose gates consumed approximately 300 seconds per Context write. It also created an explicit temporary capability gap.

The gap has become material:

- cold boot requires a reading participant to inspect a large mandatory corpus;
- active memory titles are swept to compensate for missed invocation;
- task relevance is inferred by the same participant that will design, implement, test, and self-review;
- relevant lower-layer capabilities are discovered manually;
- high-risk assumptions can be reproduced in tests written by the same reasoning process;
- owner-live H1 trials become the first truly independent observation surface.

This structure contradicts the principle already accepted for action governance: consequential correctness MUST NOT depend on a participant voluntarily remembering to invoke its own control mechanism.

### 1.3 Continuity is not cognitive amplification

Project Continuity proves that a fresh consumer can reconstruct project truth, authority, state, accepted decisions, obligations, and the next legitimate boundary. That property is valuable and remains required.

It does not prove that a fresh consumer can:

- find the correct semantic owner before implementing;
- activate the relevant incident scars before repeating them;
- distinguish a genuinely unknown platform behavior from a mature known hazard;
- recognize an existing lower-layer primitive instead of duplicating it;
- formulate ownership and lifetime contracts before writing code;
- design tests that can falsify its own assumptions;
- produce a better first serious implementation than an unassisted session.

Qiven SHALL name these as separate claims:

```text
Project Continuity Claim
    A fresh consumer can reconstruct and continue the project safely.

Cognitive Utility Claim
    Activated Qiven cognition materially improves task reasoning and first-pass engineering quality.

Mechanical Governance Claim
    A governed action cannot bypass the declared control boundary.
```

Passing one claim does not silently establish another.

---

## 2. Governing Vocabulary

### 2.1 Canonical Cognition

Durable, authority-bearing project truth and evidence in canonical repositories. It includes accepted and historical records with lifecycle and provenance. It is complete with respect to the repository's declared model and is not constrained by an LLM prompt budget.

### 2.2 Active Working Cognition

The bounded, task-specific cognition delivered to one participant for one task phase. It is a derivative view, never a new source of truth.

### 2.3 Task Cognition Activation

The deterministic governed operation that maps an observed task descriptor and pinned canonical sources to an immutable `TaskCognitionBundle` plus a `ContextActivationReceipt`.

### 2.4 Protected Cognition

Material that cannot be silently removed by ranking or budget pressure when its deterministic applicability is established or unresolved in a safety-relevant way. It includes applicable governance, explicit IDs, current blockers, before-obligations, critical hazard records, and accepted decisions named by activation policy.

### 2.5 Candidate Cognition

Potentially relevant records ranked within the remaining budget after protected cognition is resolved. Candidate inclusion may use deterministic lexical and structural signals before any optional semantic reranking.

### 2.6 Scar

A durable incident-derived lesson that names a failure class, its evidence, its applicability boundary, and the control expected to prevent recurrence.

### 2.7 Embodied Control

A type, API, ownership model, compiler rule, static check, validator, test, operator behavior, hook, runtime admission rule, or other mechanism that reduces dependence on participant recollection.

### 2.8 Independent Falsification

Review or testing whose reasoning inputs are sufficiently independent from the authoring session that it can expose correlated assumptions. A fresh-context reviewer, a real external contract capture, sanitizers, adversarial fault injection, and an owner-live isolation-boundary test are examples. Re-running author-authored happy-path tests is not independent falsification.

---

## 3. Constitutional Laws

### CG-1 — Preserve all truth; activate only what the task needs

Canonical cognition SHALL remain lossless and historically complete. Active working cognition SHALL remain selective and bounded.

Lossless storage and selective activation are complementary. Qiven MUST NOT choose between deleting history and injecting the entire history into every task.

### CG-2 — Activation is externally triggered

Mandatory activation SHALL originate from observed task boundaries and activation policy, not participant confidence or voluntary recall.

At minimum, activation is reconsidered at:

- cold boot;
- material task transition;
- repository or subsystem transition;
- design start;
- implementation start;
- review start;
- discovery of an unexpected failure class;
- preparation for an owner-live or isolation-boundary acceptance step.

CA-2 MUST declare the exact harness, command, and publication boundaries it can observe and interlock. A design-start event cannot be inferred from a later commit. For an unobserved entry path the program records a coverage gap and withholds any before-design or no-bypass claim; a receipt issued after the fact cannot repair that gap. A harness delivery record, bound to the task, bundle digest, consumer invocation, and delivery time, is needed to claim that the bundle reached the consumer before the phase began. Even that record does not prove comprehension. CA-2 cannot pass with an empty coverage set: at least one MVP-5/MVP-6 R2/R3 task-entry path must demonstrate model-visible bundle delivery before the first design output. Uninstrumented work in the declared MVP-5/MVP-6 dogfood scope is a coverage failure, not a reason to shrink the denominator after observing results.

### CG-3 — Critical applicability is not a ranking problem

Known critical hazards and binding constraints use deterministic applicability rules. They MUST NOT depend exclusively on embedding similarity, LLM classification, or Top-K ranking.

When applicability cannot be resolved safely, the record remains visible as `unresolved`; it is not treated as irrelevant.

### CG-4 — Every inclusion and exclusion is explainable

For every selected non-core source, the activation result SHALL state why it was selected. For every protected rule considered but not applied, it SHALL state the deterministic reason.

Opaque similarity scores are insufficient evidence for mandatory governance.

### CG-5 — Repetition forces embodiment

The first material incident creates or updates the scar and regression evidence. A materially similar recurrence after an active scar exists triggers a mandatory control review.

The review MUST determine why the prior control failed:

- activation did not occur;
- applicability metadata was insufficient;
- the rule was present but operationally vague;
- the relevant type/API still admitted the invalid state;
- tests shared the implementation's assumption;
- the control existed but was bypassable;
- conflicting instructions weakened the rule.

After recurrence, adding another prose warning alone is insufficient unless the owner explicitly records why mechanical embodiment is impossible or disproportionate.

### CG-6 — Unified execution does not imply unified falsification

Single-session unified engineering remains the normal execution model. One capable session may specify, design, implement, validate, and publish under its authority surface.

For high-risk classes, the same session MUST NOT be the only source of falsification evidence. Independent evidence is required for:

- ownership and lifetime across asynchronous or stored borrows;
- external payload, protocol, ABI, or platform-contract assumptions;
- concurrency, process custody, leases, and crash recovery;
- security and complete-mediation claims;
- persistent, wire, or cross-process representation;
- a previously recurring scar;
- a change that weakens or replaces an existing embodied control.

### CG-7 — Known engineering knowledge is applied before validation

Validation proves a candidate and discovers genuinely uncertain behavior. It is not an apprenticeship loop for rediscovering mature ownership, RAII, bounds, failure-model, or representation principles.

A known hazard found only by late H1 evidence is classified as an upstream cognition/control failure even if H1 correctly prevents release.

### CG-8 — Derived cognition never becomes canonical authority

Activation indexes, compact packs, summaries, tokenized renderings, embeddings, FTS databases, graphs, and receipts are rebuildable derivatives. Canonical facts remain in their authoritative repositories.

Every derivative binds exact source revision and content digests.

### CG-9 — Latency is part of cognitive reliability

A control that makes every Context write cost several minutes creates pressure to skip, batch unsafely, detour, or disable it. Therefore activation and validation latency are governance properties.

The production design SHALL separate:

- canonical mutation validation;
- active-generation publication;
- task activation;
- expensive audit/benchmark work.

The old full Python compiler/gate model SHALL NOT be reinstated.

### CG-10 — Token compression is not attention selection

Lossless compact transport may reduce token cost, but it does not decide what deserves active attention. K5-style lossless transport work SHALL follow, not substitute for, demonstrated task activation.

### CG-11 — No cognitive-amplification claim without causal evidence

Qiven may claim continuity from continuity evidence. It may claim enforcement from complete-mediation evidence. It may claim cognitive amplification only when a fresh-consumer trial demonstrates that the activated bundle causally improves task outcomes under the acceptance protocol.

### CG-12 — The owner is not the routine debugger

H1 remains the authoritative real-boundary test where required. The system MUST minimize avoidable defects reaching H1. A mature known hazard first detected by the owner is a process-quality incident even when fail-closed behavior protects safety.

---

## 4. The Cognitive Governance Stack

| Layer | Canonical owner | Responsibility | Must not become |
|---|---|---|---|
| Evidence | Repository audit/evidence surfaces | Preserve observations and acceptance artifacts | Unquestioned interpretation |
| Memory | `qiven-context` | Preserve reusable facts, scars, constraints, protocols, and negative knowledge | An undifferentiated prompt dump |
| Decision | `qiven-context` ADRs | Preserve accepted judgments and supersession history | Runtime implementation detail |
| Engineering law | `qiven-devkit` | Define how engineering work is specified, designed, tested, validated, and published | Duplicate project truth |
| Foundational skill | `qiven-foundation` and proper lower semantic layers | Make reusable low-level correctness expressible and difficult to misuse | Product-domain grab bag |
| Task activation | `qiven-runtime` | Select, bind, deliver, and audit active working cognition | Canonical knowledge authority |
| Repository architecture | Each repository | Define domain/layer contracts and local public surfaces | Shared engineering-process canon |
| Falsification | Devkit workflow + independent evidence sources | Break correlated assumptions before owner-live acceptance | Ritual duplicate review |
| Execution control | `qiven-runtime` | Admit, deny, bind, execute, observe, and recover governed effects | A prompt-compliance system |

### 4.1 Ownership placement rule

A repeated word does not automatically belong in Foundation. Placement follows semantics:

- generic ownership, bounded byte access, checked arithmetic, and process-independent representation primitives may belong in Foundation;
- framed IPC messages and a hook invocation's payload lifetime belong in the IPC/Runtime layer that owns that contract;
- external harness semantics remain at the adapter boundary;
- engineering workflow belongs in Devkit;
- incident history belongs in Context.

The activation system SHALL surface this ownership map before implementation. It SHALL NOT flatten every recurring concept into Foundation.

---

## 5. Scar Governance Lifecycle

Every material scar proceeds through explicit states. These are cognition lifecycle states, not necessarily fields in one file format.

```text
Observed
  -> Recorded
  -> Classified
  -> ActivationBound
  -> MechanicallyEmbodied
  -> RegressionProven
  -> PromptRetired
```

### 5.1 Observed

Raw evidence exists, but no durable reusable interpretation has been accepted.

### 5.2 Recorded

An audit and/or memory record names the incident, observed symptom, root cause confidence, affected scope, and provenance.

### 5.3 Classified

The failure is classified as one of:

- genuinely unknown external/platform behavior;
- mature known engineering hazard;
- missing lower-layer capability;
- missing or ambiguous specification;
- activation/retrieval miss;
- correlated-test/review miss;
- enforcement bypass;
- operational/tooling defect.

Classification determines the next control. A genuinely unknown NPFS behavior may justify a platform regression fixture; a dangling borrowed span is a mature ownership hazard and demands an ownership-contract review.

### 5.4 ActivationBound

The scar has machine-readable applicability selectors and is protected for relevant tasks. It names the phase at which it must surface and the control/evidence expected.

### 5.5 MechanicallyEmbodied

The project has moved as much of the rule as practical into its semantic owner: a safer API, owning type, validation rule, generated artifact, hook, test harness, or operator mechanism.

### 5.6 RegressionProven

A deterministic test or independent evidence path demonstrates that the previous failure shape is now detected or impossible.

### 5.7 PromptRetired

Once a control is mechanically complete and regression-proven, the full scar body no longer needs default prompt inclusion. The activation bundle may include a compact invariant and evidence pointer. Historical records remain canonical and retrievable.

Prompt retirement is necessary to keep institutional learning from causing unbounded active-context growth.

---

## 6. Rule Placement and Duplication Law

### 6.1 One canonical rule body

A durable rule SHALL have one canonical normative body. Other surfaces point to it and may carry a compact machine selector, but MUST NOT develop independent paraphrases whose semantics can drift.

Recommended placement:

- incident narrative: audit;
- reusable scar and provenance: memory;
- accepted architectural/governance decision: ADR;
- shared engineering behavior: Devkit standard;
- implementation-specific architecture: owning repository;
- activation selector: canonical activation policy referencing the rule ID/path;
- mechanical enforcement: semantic owner;
- regression evidence: tests/audit.

### 6.2 Temporary duplication

Temporary duplication is permitted only as a migration control when:

- an old consumer cannot yet resolve the canonical pointer;
- the duplicate is marked with canonical source and expiry;
- validation detects divergence;
- an obligation names removal.

The current pattern of copying a missed memory rule into an always-read operating contract is an emergency repair, not the steady-state architecture.

---

## 7. Task Risk Classification

Activation policy SHALL classify tasks by observed characteristics rather than participant confidence.

### R0 — Documentary / non-semantic

Pure prose or metadata edits with no executable contract effect. Core context and local document rules are sufficient.

### R1 — Ordinary bounded implementation

Local implementation under an accepted contract with no new ownership, platform, concurrency, external-contract, or representation boundary.

Requires task activation and author self-review. Independent falsification is optional unless an applicable scar requires it.

### R2 — Contract-bearing implementation

Adds or changes public types, ownership/lifetime, failure channels, serialization, IPC, persistence, platform APIs, resource custody, concurrency, or security behavior.

Requires:

- protected task activation;
- explicit semantic-owner resolution;
- design-first evidence;
- named adversarial test spine;
- independent falsification before publication.

### R3 — Authority or production-boundary change

Changes governance, execution authority, complete mediation, recovery, canonical truth, acceptance topology, or owner-live deployment.

Requires R2 controls plus the existing typed owner handoff and governance authority rules. No activation receipt grants the authority that an H1/H2/H3/H4 boundary reserves.

Risk classification itself is auditable. Unknown classification defaults upward, not downward.

---

## 8. Engineering Phase Gates

### 8.1 Specify gate

Before a feature becomes implementation-ready, the task descriptor must identify:

- intent and exact scope;
- repositories and semantic layers touched;
- task risk class;
- public/external boundaries;
- ownership and lifetime concerns;
- platform and concurrency concerns;
- expected evidence and acceptance boundary.

The activation engine returns applicable scars, decisions, lower-layer capabilities, obligations, and unresolved questions. A critical unresolved item prevents `ReadyForDesign`.

### 8.2 Design gate

A design for R2/R3 work MUST include a cognition compliance map:

| Activated source | Design consequence | Test/evidence consequence |
|---|---|---|
| Record/ADR/standard ID | Exact type/API/ownership/failure decision | Named proof |

The map is not a prose restatement. It demonstrates that activated cognition changed the candidate design.

### 8.3 Implementation gate

The design-evidence record binds the design digest to an activation receipt issued before the design. A design edit invalidates the design and falsification bindings; it requires reactivation only when selector-bearing scope, boundary, risk, source revision, or required evidence changes.

### 8.4 Review gate

R2/R3 review receives:

- task descriptor;
- immutable task cognition bundle;
- activation receipt;
- design and compliance map;
- exact delta;
- validation evidence.

The independent reviewer is asked to falsify ownership, lifetime, external-contract, failure, representation, concurrency, and test assumptions. It does not merely verify formatting or repeat the author's narrative.

### 8.5 Owner-live gate

H1 remains a real-world truth boundary, not a substitute for upstream engineering discipline. Every avoidable mature hazard found at H1 produces a cognition/control incident classification.

---

## 9. Performance and Write-Path Governance

### 9.1 No 300-second routine Context gate

The production activation design SHALL NOT run the sealed Python compiler or its historical full semantic suites on every write.

Routine canonical mutation SHALL perform only the checks required to determine whether the candidate repository is structurally and semantically valid for the changed surfaces.

### 9.2 Separate transactions

```text
Canonical mutation transaction
    validate canonical records and cross-references
    commit exact Git state

Cognition publication transaction
    build/refresh immutable canonical bundle and derived activation index
    verify digests and policy references
    atomically activate a new RuntimeGeneration

Task activation transaction
    compile one bounded task bundle from one pinned generation
    issue receipt
```

If cognition publication fails after a valid canonical commit:

- the Git commit remains canonical domain truth;
- the previous RuntimeGeneration remains active;
- Runtime records a stale-generation barrier;
- new tasks that require the new commit fail visibly rather than reading a partial index;
- repair rebuilds the derivative from the canonical commit.

### 9.3 Initial performance objectives

These are release objectives to be measured and refined, not assumed facts:

- changed-record structural validation: p95 below 2 seconds at current Context scale;
- full repository contract validation: p95 below 30 seconds at current scale;
- native activation-index rebuild from an unchanged cached base: p95 below 1 second;
- cold full activation-index build: below 5 seconds at current scale;
- task activation from a warm pinned generation: p95 below 250 ms;
- no routine Context mutation invokes network access, embeddings, or a model.

Failure to meet a target does not authorize skipped validation. It triggers profiling and architecture review.

---

## 10. Independent Falsification Governance

### 10.1 Independence classes

| Class | Example | Independence value |
|---|---|---|
| Mechanical | compiler, sanitizer, schema validator, model checker, fault injector | High for represented properties |
| Environmental | real harness capture, real OS behavior, crash drill | High for external-contract facts |
| Fresh cognitive | fresh-context reviewer with task bundle and no author reasoning trace | High for correlated reasoning errors |
| Owner boundary | H1/H2/H3/H4 evidence | Authoritative for the reserved claim |
| Same-session self-review | author rereads design/code/tests | Necessary but not independent |

An R2/R3 feature must name which independent class proves each high-risk property.

### 10.2 Fresh review is scoped, not a return to role theater

Independent falsification does not restore multi-stage role personas. It is one evidence-producing operation at a risk boundary. The main session remains accountable for integrating findings and completing the task.

### 10.3 Correlated test detection

When local tests pass but a real boundary fails, the incident review SHALL inspect whether fixtures reproduced an invented contract or bypassed the real lifecycle. A new test that merely encodes the fixed implementation is insufficient; it must fail under the prior defective model.

---

## 11. Cognitive Governance Metrics

Qiven SHALL measure whether cognition is becoming operational rather than merely larger.

### 11.1 Required metrics

- activation latency and bundle size;
- protected records considered, included, unresolved, and excluded;
- candidate precision/recall against accepted task rubrics;
- exact source revisions and policy digests;
- task transitions without a valid activation receipt;
- previously recorded hazard recurrences;
- owner-caught mature hazards;
- H1 attempts per accepted boundary;
- independent-review findings by severity and class;
- rules promoted from prose to mechanism;
- rules eligible for prompt retirement;
- cognitive bundle token cost by consumer profile;
- first-pass design acceptance and rework rate.

### 11.2 Primary health indicators

The primary indicators are not record count or document coverage. They are:

1. recurrence rate of an active scar;
2. critical-rule recall before design;
3. independent-review escape rate;
4. owner-live avoidable-defect rate;
5. active-context cost per successful task.

### 11.3 Governance review trigger

A program-level review is mandatory when any of the following occurs:

- a critical active scar recurs;
- two owner-live attempts fail from mature known hazards;
- task activation omits an applicable protected record;
- a participant completes R2/R3 work without a valid receipt;
- activation cost causes a sanctioned workflow to be bypassed;
- the same author assumption appears in design, implementation, and tests;
- active-context size grows by more than 25% without a measured quality gain;
- CA-1 reaches the close of its declared implementation batch without passing Profile A and Profile B; further feature work then stops for a recorded program review rather than extending the transition silently. Session count and calendar time may be reported for planning, but they do not waive evidence or act as engineering truth.

---

## 12. Authority and Change Control

### 12.1 Root-governed changes

The following require the existing root governance/ADR acceptance boundary:

- changing the constitutional laws in this document;
- changing which record classes are protected from ranking;
- weakening independent falsification requirements;
- authorizing a derived index as canonical truth;
- changing acceptance claims or typed handoff semantics;
- removing fail-visible behavior for unresolved critical cognition.

### 12.2 Engineering changes

The following may proceed under the normal delegated engineering path when already authorized:

- performance improvements that preserve selection semantics;
- additional deterministic selectors;
- cache and index format changes with reproducibility proof;
- new renderers for consumer profiles;
- new regression tasks and evaluation cases;
- migration of a prose rule into a stronger mechanism.

### 12.3 Emergency corrections

An owner-live incident may authorize immediate fail-closed repair. The correction must still produce the audit, scar classification, regression, and governance reconciliation required by this program. Emergency speed does not turn the patch into a complete lesson.

---

## 13. Explicit Non-Goals

This program does not:

- revive the sealed Python ContextKernel/compiler/retrieval system;
- make an embedding or vector database authoritative;
- require a general-purpose agent platform;
- move project truth from Git-backed canonical records into Runtime databases;
- broaden the current Runtime complete-mediation claim without separate evidence;
- force every repeated noun into Foundation;
- replace typed human handoffs;
- guarantee that an LLM will never make an error;
- claim cognitive amplification from smaller prompts alone;
- require every Context write to regenerate every derived artifact synchronously.

---

## 14. Immediate Governance Actions

The roadmap companion defines exact sequencing. At governance level, the immediate decisions are:

1. Treat the MVP-4 H1 double failure as a program-level cognition/control signal, not merely two local defects.
2. Keep the Runtime control MVP architecture and its narrow enforcement claim intact.
3. Close reusable byte-representation debt through the separately accepted RR-0 semantic-ownership batch; do not count that remediation as evidence that cognition activation works.
4. Insert the `CA-0` through `CA-2` cognition-activation gates before substantive MVP-5 implementation proceeds.
5. Use MVP-5 and MVP-6 as dogfood consumers of the activation path.
6. Amend MVP-7 to require both the original control-loop evidence and a separate Cognitive Utility Gate.
7. Defer K5 lossless token compression until task activation is accepted on an uncompressed reference.
8. Remove the brute-force active-memory-title sweep and shrink mandatory boot prose only after the production activation path passes replacement acceptance.

---

## 15. Definition of Governance Success

This program succeeds when all of the following are true:

1. A fresh session receives a bounded task bundle without manually searching the entire cognition corpus.
2. The bundle includes every applicable protected rule and explains every inclusion.
3. The participant identifies the correct semantic owner and existing lower-layer capabilities before implementation.
4. A known ownership/lifetime or external-contract scar changes the design and test spine before code is written.
5. R2/R3 work carries independent falsification evidence.
6. Canonical Context writes remain fast enough that the control is routinely used rather than bypassed.
7. A failed derivative build cannot corrupt canonical truth or silently activate partial cognition.
8. Repeated scars migrate toward mechanism and leave the default prompt when safely embodied.
9. The owner is no longer the first detector of mature known hazard classes in routine H1 trials.
10. Isolated fresh-consumer trials demonstrate materially better engineering outcomes than the current full-manual-reading baseline.

The final principle is:

> Qiven cognition is not complete when knowledge is stored. It is complete when the right knowledge governs the right action at the right time, with evidence that it changed the outcome.
