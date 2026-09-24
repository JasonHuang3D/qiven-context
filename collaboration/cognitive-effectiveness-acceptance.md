# Qiven Cognitive Effectiveness Acceptance Protocol

## Proving That External Cognition Improves the Consumer

> Status: Accepted by ADR-0050 (owner H2 2026-09-23)
> Date: 2026-09-23
> Acceptance owner: Qiven root governance principal
> Applies to: Task Cognition Activation (`TCA`) and any later cognition-delivery mechanism
> Governance: `collaboration/cognitive-governance-program.md` (this transaction)
> Architecture: `qiven-runtime docs/architecture/task-cognition-activation.md` (bound at merge f0ca5b7)
> Deliberation record: `qiven-docs accepted/2026-09-23/` (PR #1, seven passes, corrections R1-R15)

## 0. Acceptance Decision

Qiven SHALL NOT infer cognitive effectiveness from the quantity of documentation, the existence of memory and ADR records, successful bundle generation, token reduction, test count, or a participant's subjective confidence.

The Task Cognition Activation capability is accepted only when it separately proves:

1. **canonical integrity** — the authoritative sources remain valid, typed, lifecycle-correct, and revision-pinned;
2. **activation correctness** — applicable protected cognition is selected deterministically and irrelevant or superseded material is handled correctly;
3. **consumer utility** — an isolated fresh consumer produces materially better engineering reasoning with the activated bundle;
4. **independent falsification** — high-risk correlated assumptions are challenged by evidence not generated from the author's reasoning path;
5. **operational viability** — activation is fast and reliable enough to be used at ordinary task boundaries;
6. **recurrence reduction** — known scars stop recurring, or recurrence triggers stronger embodiment rather than additional prose.

These are independent claims. Failure of one cannot be compensated by excellence in another.

The first production acceptance SHALL use deterministic local retrieval and an uncompressed canonical rendering. Embeddings, generative summarization, semantic reranking, and K5 transport compression are excluded so that the accepted result has a legible causal boundary.

---

## 1. Claims and Non-Claims

### 1.1 Project Continuity Claim

A fresh participant can reconstruct current project truth, authority, accepted decisions, non-terminal obligations, evidence status, and the next legitimate boundary.

This claim remains governed by the existing continuity audit. It is a prerequisite, not a substitute, for this protocol.

### 1.2 Activation Correctness Claim

For a normalized task and pinned generation, the activator returns the required protected cognition, correct semantic owners, applicable accepted decisions, relevant scars, and explicit unresolved items with reproducible reasons.

This claim is tested mechanically against sealed fixtures and expected source IDs.

### 1.3 Cognitive Utility Claim

For an engineering task, an isolated fresh consumer receiving the activated bundle reasons more correctly and efficiently than the same class of consumer using the current manual cold-boot path.

This claim requires paired fresh-consumer evidence. It cannot be established by the system author reviewing its own output.

### 1.4 Mechanical Governance Claim

Required receipts, embodied controls, Runtime decisions, and publication gates cannot be bypassed within the declared control boundary.

This claim belongs to complete-mediation and enforcement evidence. A good prompt does not establish it.

### 1.5 Explicit non-claims

Passing this protocol does not prove that:

- the LLM is generally intelligent or infallible;
- all future tasks are covered by the initial selector vocabulary;
- every canonical document is equally useful;
- retrieval alone prevents defects;
- an activation receipt proves comprehension;
- Runtime mediates actions outside its declared tuple;
- the owner-live H1 boundary can be removed;
- K5 compression preserves cognitive utility;
- one model, harness, or consumer profile generalizes to all others.

---

## 2. Acceptance Profiles

The program uses five profiles. A release candidate passes only when all profiles required by its stage pass.

| Profile | Question | Evidence type | Normal cadence |
|---|---|---|---|
| A — Conformance | Is the derived system deterministic, pinned, and structurally valid? | Native automated suite | Every relevant change |
| B — Protected Applicability | Are mandatory rules and scars impossible to lose through ranking or budget? | Sealed gold fixtures | Every policy/index change |
| C — Fresh-Consumer Utility | Does the bundle improve actual engineering reasoning? | Paired isolated sessions | Milestone/release gate |
| D — Independent Falsification | Are correlated implementation assumptions challenged? | Independent receipts and real-boundary evidence | Every R2/R3 task |
| E — Recurrence and Dogfood | Does the system prevent known failure classes during real Qiven work? | MVP-5/MVP-6 task evidence | Continuous through MVP-7 |

Profile C is deliberately not run on every Context write. It is a release-quality experiment, not a 300-second mutation gate.

---

## 3. Acceptance Independence

### 3.1 Roles

One person or session may implement the full activation stack, but the following evidence roles remain distinct:

| Role | May know implementation internals? | May author the expected answer? | May score the consumer output? |
|---|---:|---:|---:|
| Fixture curator | Yes | Yes | No, unless identity is disclosed and a second scorer concurs |
| Activation implementer | Yes | No after fixture sealing | No |
| Fresh consumer | No | No | No |
| Independent scorer | Only rubric and evidence pack | No | Yes |
| Root acceptance owner | Yes | Approves rubric | Resolves acceptance, not individual answers silently |

The same underlying LLM family MAY appear in different roles if the sessions are isolated and the scoring key is withheld, but this is weaker evidence than diversity of model or harness. The evidence record MUST disclose the consumer and scorer profiles.

### 3.2 Isolation requirements

A fresh consumer session:

- has no prior Qiven conversation state or hidden Qiven memory;
- receives only the declared task input and the assigned context condition;
- cannot browse Qiven repositories beyond sources explicitly included in that condition;
- cannot ask the fixture curator for hints;
- cannot see the gold answer, selector expectations, paired output, or scoring rubric weights;
- uses a pinned model/profile, tool policy, time budget, and output schema;
- records all supplied source IDs and token/byte counts.

Any undeclared context contamination invalidates the run.

### 3.3 Sealing

Before an implementation is evaluated:

1. the fixture task, hidden hazards, required sources, critical findings, and score rubric are committed and digested;
2. the activation implementation revision and policy revision are pinned;
3. condition assignment and run order are generated independently of the implementer;
4. outputs are captured before the answer key is opened;
5. any rubric correction applies to all paired outputs, never to one favored result.

---

## 4. Gold Fixture Corpus

### 4.1 Corpus purpose

The corpus represents failure classes, not just old issue text. Each fixture contains:

- a realistic task descriptor;
- a minimal authoritative source set;
- a hidden failure surface;
- exact protected cognition expected to activate;
- semantic-owner expectations;
- accepted and superseded decision distinctions;
- a design/implementation prompt;
- critical and weighted rubric items;
- required independent evidence;
- prohibited shortcuts;
- a known-good control strategy without requiring one exact code shape.

The first accepted corpus SHALL contain at least six materially different fixtures and cover all R2/R3 boundary classes used before MVP-7.

### 4.2 Initial fixture set

#### F-01 — Borrowed payload lifetime across execution

The task exposes a C++ payload through a non-owning view such as `std::span<std::byte>` while construction and later execution occur at different lifetimes.

Critical findings:

- a view is not storage;
- the outlives relation must be explicit and proven;
- a temporary container cannot back a later-executed payload;
- the semantic owner is the Runtime/domain type that stores work across the boundary, not an arbitrary Foundation wrapper;
- the test must exercise the delayed/stored path under a lifetime-sensitive detector or equivalent adversarial construction.

Expected activation includes the applicable ownership/lifetime engineering law, Foundation representation law, the MVP-4 scar, relevant Runtime architecture, and an ownership-capability surface.

#### F-02 — Assumed external payload field

The task asks for parsing or evaluating an external hook/protocol payload whose field shape has not been captured from the real producer.

Critical findings:

- repository prose or an author-authored fixture is not proof of an external wire contract;
- the design must request or bind live/authoritative evidence;
- unknown fields and versions fail explicitly;
- the parser cannot be accepted solely against a payload invented by the implementer;
- H1 is a final real-boundary confirmation, not the first point at which the assumed shape is questioned.

#### F-03 — Windows named-pipe multi-segment lifecycle

The task implements or reviews repeated named-pipe service cycles across connect, transfer, disconnect, and next-instance reuse.

Critical findings:

- the state machine spans more than one successful transaction;
- connection completion and expected asynchronous platform results are normalized deliberately;
- cleanup, next-instance creation, cancellation, and shutdown have explicit ownership;
- the independent test covers multiple consecutive segments and failure injection, not one happy path;
- platform behavior is supported by primary evidence or a real boundary capture.

#### F-04 — Shell heredoc and active-memory recurrence

The task modifies a governance record using shell input that can expand substitutions or otherwise mutate literal content.

Critical findings:

- the known heredoc scar applies before the write;
- the safe literal-write path is used;
- the resulting file is verified byte-for-byte or by the declared validator;
- recurrence after an active scar triggers embodiment review rather than another prose reminder.

#### F-05 — `Result<void>` first-instantiation boundary

The task introduces a first use of a generic result/failure abstraction with `void` success semantics across a public boundary.

Critical findings:

- the generic type's actual supported surface is verified before use;
- success storage and API semantics for `void` are explicit;
- the owning layer is identified correctly;
- compile-only happy-path evidence is insufficient when error propagation or representation crosses a boundary;
- public contract and negative tests are named.

#### F-06 — Process custody and recovery

The task starts, supervises, or recovers an external process under Runtime governance.

Critical findings:

- process ownership, PID reuse, handle lifetime, termination authority, and crash recovery are explicit;
- the action/decision boundary is not confused with raw process utility;
- durable control facts and transient handles are separated;
- recovery does not blindly replay an external effect;
- independent fault injection covers partial start, parent crash, stale record, and shutdown.

#### F-07 — Concurrent fixture-root and representation collision

The task creates test fixtures or derived artifacts concurrently under paths that appear unique within one session.

Critical findings:

- uniqueness is established across processes and retries, not only threads in one process;
- path derivation is a representation contract;
- cleanup does not target an unresolved broad path;
- publication uses private construction plus atomic visibility;
- tests force collision/retry behavior.

#### F-08 — Fail-closed mediator availability

The task enables or operates a control component whose fail-closed behavior can block ordinary work — for example a hook mediator whose governed verdicts require a reachable host process.

Critical findings:

- the mediator's own lifecycle is explicit: who starts it, who supervises it, and what happens when it is absent, slow, stale, or version-skewed;
- enabling the fail-closed gate is preceded by a pre-flight self-check that verifies reachability, identity, and handshake in the target environment;
- the pre-flight result is not treated as an availability guarantee: after enablement, host loss still follows the declared fail-closed behavior and remains operator-diagnosable;
- denial codes are diagnosable and disjoint: no-listener, admission-rejected, version-skew, and timeout are distinguishable rather than collapsed into one undifferentiated denial;
- the real end-to-end contract — every frame of a complete transaction, over the real transport, in the real environment — is exercised before the gate is enabled;
- comments or design text describing behavior the implementation does not perform are classified as defects, not documentation.

### 4.3 Corpus evolution

A new material Qiven incident SHALL either:

- map to an existing fixture class with new evidence; or
- create a new fixture before the scar is considered `RegressionProven`.

The incident author does not silently tune selectors against only the incident wording. The fixture task uses realistic alternative vocabulary so that coverage comes from typed applicability, not memorized strings.

---

## 5. Profile A — Conformance Acceptance

### 5.1 Required tests

The native automated suite SHALL prove:

1. identical normalized source closures, tasks, policies, budgets, and renderer builds produce byte-identical canonical selection bundles, manifests, and selection explanations; receipt issuance nonces and timestamps are checked for correct binding, not byte equality;
2. every output binds the execution RuntimeGeneration, the separate ActivationGeneration, the full external repository source lock, policy digest, schema versions, task digest, and bundle digest;
3. a changed canonical body without a changed path changes the correct digest and invalidates affected outputs;
4. superseded and legacy sources do not appear as current rules;
5. epistemic types cannot be promoted by imperative language in a lower-authority record;
6. invalid selectors, source references, lifecycle states, and capability entries fail publication;
7. activation receipts cannot be replayed across a changed task, risk, source lock, policy, activation generation, renderer, consumer profile, or expired live evidence; a separate design-evidence/falsification binding rejects a changed design or candidate digest;
8. partial index and bundle writes never become visible;
9. index loss is recoverable from pinned canonical sources;
10. activation does not mutate canonical repositories;
11. no network, LLM, embedding, or Python service is required on the production path;
12. observed and participant-claimed task attributes remain distinguishable.

### 5.2 Determinism criterion

For each fixture, execute activation at least 100 times across clean process starts. All canonical selection outputs and protected-source decisions MUST be byte-identical. `bundle_id` is deterministic, and no clock, random value, or volatile path participates in the canonical hashed payload. Receipts MAY have distinct issuance IDs and times while binding the same canonical bundle; the audit envelope is verified separately.

### 5.3 Fault matrix

At minimum, inject:

- missing source checkout;
- revision mismatch;
- malformed canonical record;
- unknown schema version;
- stale capability manifest;
- policy conflict;
- protected set larger than the task budget;
- index corruption;
- crash before manifest publication;
- crash after index publication but before generation activation;
- stale live-evidence receipt;
- receipt journal unavailability.

Every fault has a declared state: `Blocked`, `ReDeliberate`, `BudgetInsufficient`, `Stale`, or safe rebuild. Silent degradation to a smaller apparently ready bundle is forbidden.

---

## 6. Profile B — Protected Applicability Acceptance

### 6.1 Gold expectations

Each fixture defines three source sets:

```text
MUST-INCLUDE
    Protected cognition whose absence is a critical miss.

MUST-EXPLAIN
    Protected rules evaluated but not applied; the exclusion reason is checked.

MAY-RANK
    Supporting candidates whose relative relevance is scored within the remaining budget.
```

Protected evaluation is exact. Candidate retrieval is measured separately so a high average cannot hide one missing critical scar.

### 6.2 Required thresholds

Across the sealed corpus:

- protected applicability recall: **100%**;
- explicit source-ID recall: **100%**;
- critical semantic-owner recall: **100%**;
- superseded/legacy source presented as current: **0**;
- authority or epistemic-type fabrication: **0**;
- unresolved critical applicability represented as irrelevant: **0**;
- candidate relevance recall at the accepted cutoff: **at least 95%**;
- irrelevant candidate share in the delivered evidence section: **at most 20%**;
- identical-task nondeterminism: **0**.

A single protected miss fails the profile even when aggregate recall remains high.

### 6.3 Budget-pressure test

For every fixture, rerun with budgets at 100%, 75%, and 50% of the default candidate allowance. Protected cognition MUST remain present. Optional candidates are removed in deterministic priority order. If protected material alone exceeds the hard budget, activation MUST return `BudgetInsufficient`, as specified by the architecture; it MUST NOT truncate a protected rule invisibly. A subsequent human or policy re-deliberation may change the budget or scope but is not the machine failure code.

### 6.4 Mutation tests

Policy and metadata mutation tests SHALL prove that the suite detects:

- removal of a critical selector;
- inversion of a lifecycle state;
- reassignment to the wrong semantic owner;
- demotion of a protected scar to optional;
- replacement of an exact source ID with a similarly worded source;
- omission of an independent-evidence requirement;
- a false safe-default for unknown applicability.

---

## 7. Profile C — Fresh-Consumer Utility Acceptance

### 7.1 Compared conditions

Each accepted fixture is executed under two conditions:

| Condition | Context supplied |
|---|---|
| `CONTROL-MANUAL` | The current authoritative cold-boot instructions and the same repository access normally available today |
| `TCA-ACTIVATED` | The normalized task, generated Task Cognition Bundle, and only the repository excerpts named by that bundle |

Both conditions receive the same task objective, permitted tools, implementation boundary, model/profile class, time limit, and required output schema. They do not share a session.

The control is the real current process, not an intentionally weakened prompt. The activated condition receives no private hints outside the accepted bundle. For each run, count cumulative model input tokens through the sealed engineering brief, including initial context, the activation bundle or manual boot, on-demand source reads, and tool-returned text, using the same pinned tokenizer. Report identical system/harness overhead separately and exclude it equally from both comparisons. Compare actual delivered inputs, not the size of the entire manual cold-boot corpus.

Descriptor construction is condition-blind and fixed before assignment. One pre-sealed normalizer derives a neutral task envelope from facts available in the current workflow: task objective, declared repository and revision, changed paths, path-prefix subsystem mapping, file-extension language mapping, declared phase, and declared risk class. Both conditions receive those same underlying facts. Runtime derives the activated condition's internal `TaskDescriptor` only from that envelope and mechanically observed facts. Judgment-bearing fields (`boundary_kinds`, `external_contracts`, `explicit_ids`, `signals`) remain empty unless the fixed normalizer can derive them without curator interpretation. Protected selectors depending on curator judgment are tested in Profile B but earn no Profile C utility credit. Supplying an expert-enriched descriptor to either condition invalidates the paired run; there is no alternate descriptor method selected after sealing.

### 7.2 Run count

Initial MVP-7 acceptance SHALL use:

- at least six sealed fixtures;
- two independent fresh consumers per condition per fixture;
- at least twenty-four total fresh runs;
- randomized condition and fixture order;
- no reuse of a consumer session between paired conditions.

CA-0 seals a maximum run count, balanced batch increments, and an interval method valid for the planned analysis. If the lower bound remains inconclusive at the minimum run count, add the next prespecified batch across both conditions and all fixtures; never stop on a favorable individual run or discard an unfavorable one. If the maximum is reached without passing, the candidate fails.

### 7.3 Required consumer output

The consumer returns a structured engineering brief before implementation:

1. task and authority interpretation;
2. semantic owner and existing capabilities to reuse;
3. ownership, lifetime, representation, concurrency, platform, and external-contract analysis;
4. applicable scars and how each changes the design;
5. explicit unknowns and evidence needed;
6. proposed API/state-machine or transaction design;
7. failure and recovery model;
8. verification and independent-falsification plan;
9. stop or re-deliberation conditions;
10. sources relied upon, with exact IDs.

For fixtures safe enough to implement in isolation, a second phase MAY request a candidate implementation and tests. The pre-implementation brief is always scored independently so accidental test success cannot mask weak reasoning.

### 7.4 Scoring rubric

Each output is scored from 0 to 100:

| Dimension | Weight | Critical floor |
|---|---:|---:|
| Authority and task-boundary correctness | 10 | 8 |
| Semantic-owner and capability discovery | 15 | 12 |
| Ownership/lifetime/representation reasoning | 20 | 16 |
| External/platform/concurrency assumptions | 15 | 12 |
| Scar application and recurrence control | 15 | 12 |
| Failure/recovery and safe-state design | 10 | 8 |
| Falsification and test quality | 10 | 8 |
| Provenance, unknowns, and stop conditions | 5 | 4 |

Every fixture also marks a small set of binary `critical findings`. Missing one is a critical miss regardless of numeric total.

### 7.5 Utility pass criteria

The activated cohort passes only if all of the following hold:

1. zero critical misses across all accepted activated runs;
2. every activated run scores at least 80/100;
3. the activated cohort median is at least 90/100;
4. no rubric dimension falls below its critical floor;
5. no fabricated authority, accepted decision, source, capability, or external contract appears;
6. median actual input tokens delivered to activated consumers are at most 40% of the median delivered to controls, under the same accounting rule in Section 7.1;
7. median time to a reviewable engineering brief is no worse than control;
8. one predeclared outcome path passes: (a) the equal-fixture-weighted mean score gain is at least 15 points and its one-sided 95% lower confidence bound exceeds zero; or (b) the one-sided 95% lower confidence bound for that score difference is at least -3 points while criterion 6 proves the input reduction;
9. at least two distinct failure classes show correct pre-implementation stopping behavior where the control cohort proceeded on an unsupported assumption.

Before assignments, CA-0 seals the fixture-level score-difference estimator, independent-run clustering, one-sided interval method, tokenizer, and stopping rule for additional runs. Each fixture contributes equal weight, and every run remains in the analysis; an inconclusive interval fails pending more sealed runs. Path (b) is an efficiency/non-inferiority claim within the stated margin, not strict Pareto dominance or proof of a higher score. Criterion 8 handles a legitimate ceiling case without weakening the required absolute score and zero-critical-miss rules.

### 7.6 Scoring reliability

- Two independent scorers evaluate each output using the sealed rubric.
- Outputs are anonymized and condition labels are hidden during scoring.
- A score difference greater than 8 points or disagreement on a critical finding requires adjudication.
- The raw scores, adjudication reason, final score, and scorer identities/profiles are preserved.
- Narrative fluency earns no credit unless it identifies the required engineering fact and control.

### 7.7 Causal interpretation

The program may claim that TCA improved cognitive utility only for the accepted consumer profiles, fixture classes, policy revision, and bundle renderer. Expansion to another consumer, renderer, or compressed transport requires compatibility evidence.

If TCA reduces tokens but does not improve or preserve correct reasoning, it is an attention optimization failure. If it improves scores but misses one critical protected scar, it is a safety failure. Neither result passes.

---

## 8. Profile D — Independent Falsification Acceptance

### 8.1 Required independence by risk

| Risk | Minimum evidence |
|---|---|
| R0 | Existing document validators |
| R1 | Author validation; independent evidence when selected by a scar |
| R2 | One independent falsification receipt plus task-specific mechanical evidence |
| R3 | R2 evidence plus existing typed owner/authority acceptance and required H1-H4 boundary evidence |

### 8.2 Acceptable falsification sources

Depending on the task, accepted evidence includes:

- a fresh-context adversarial review receiving the task bundle, design, and diffs but not the author's reasoning transcript;
- a real producer payload or protocol capture with provenance;
- compiler/static-analysis evidence that checks the relevant property;
- ASan, UBSan, TSan, AppVerifier, or the platform-equivalent detector;
- fault injection across the actual state-machine boundary;
- restart/recovery evidence from a deliberately interrupted process;
- a black-box consumer test authored from the public contract;
- an owner-live H1/H2/H3/H4 action where governance reserves that boundary.

An author-generated test that encodes the same assumed payload, lifetime, or state machine is corroboration, not independent falsification.

Fresh-context review has two disclosed independence classes. Routine R2 cognitive falsification MAY use a harness-created fresh agent session that receives only the sealed review package and no author reasoning trace; it is recorded as `fresh-cognitive-same-family-isolated-context`. Every R3 review, Profile C trial, and CA-5 review requires an orchestration boundary that independently creates the consumer, withholds the answer key and author trace, captures the output, and preserves the assignment record; it is recorded as `fresh-cognitive-orchestrated-isolation`. The owner accepts the resulting governed evidence but is not the transport layer, prompt relay, or routine debugger. A subagent sharing the author's conversation context qualifies under neither class.

For a before-phase cognition claim, retain a separate observed delivery event binding the consumer invocation, receipt, bundle digest, and delivery time to an observed phase entry. A receipt issued after the design cannot be counted as evidence that cognition was active when the design began; when the harness cannot observe the entry/delivery boundary, record that coverage limit rather than treating publication-time validation as proof of earlier delivery.

Governance note: adopting this transport model explicitly amends ADR-0036 and `qiven-context/collaboration/human-handoff-boundary.md`; it is not merely a reinterpretation of historical practice. Pre-amendment, the contract expressly classified owner launch and relay of fresh/isolated sessions as H1 and made fresh-consumer acceptance roles H1-mandatory. The accepting root ADR MUST narrow that classification so mechanically verified session creation, sealed input transport, and sealed output capture inside an approved orchestration boundary are not inherently H1. H1 remains mandatory for owner credentials or devices, external isolation boundaries the orchestrator cannot cross, owner-named trust anchors, and owner-designated adjudication. Existing K4/K5 gates that explicitly name the owner remain unchanged unless separately amended. H2-H4 retain their existing claims, and governance mutation still requires H2 plus the root principal. That amendment landed with ADR-0050 (applied to human-handoff-boundary.md 2026-09-23); the narrowed orchestrated-isolation classification is authoritative.

### 8.3 Receipt requirements

The falsification receipt SHALL bind:

- task ID and activation receipt ID, including both generation IDs and the external source lock;
- the separate design-evidence binding, design digest, and candidate revision digest;
- risk class and challenged assumptions;
- independence class and consumer/scorer profile;
- evidence commands or artifact references;
- findings and their severity;
- disposition of every finding;
- residual unknowns;
- reactivation requirement when a material design change alters activation selectors; renewed falsification when the design or candidate digest changes.

Publication fails if a required finding is unresolved or the bound candidate changed materially.

### 8.4 Adversarial review prompts

The reviewer is explicitly asked to disprove, not summarize:

- Who owns every byte, handle, process, lease, and callback, and for how long?
- Which external facts were observed, and which were merely assumed?
- What invalid state does the public API still admit?
- What happens after the first successful iteration, during cancellation, and after crash?
- Can the test pass because it copied the implementation's misconception?
- Which lower layer already owns this capability?
- Which supposedly current rule is actually superseded, advisory, or lower-authority?
- Does the machine-declared boundary set completely describe the boundaries the design actually introduces, or did the design omit a kind that would require reactivation?
- What evidence would force the design to stop or re-deliberate?

---

## 9. Profile E — Real-Work Dogfood and Recurrence Acceptance

### 9.1 Dogfood interval

MVP-5 and MVP-6 SHALL be the first sustained consumers of TCA. Every material task records:

- task/risk classification;
- activation receipt and observed model-input delivery event before the first design output, bound to the consumer invocation;
- bundle size and activation latency;
- protected and unresolved source counts;
- semantic-owner decision;
- independent evidence when required;
- defects found by author validation, independent review, CI, and H1 separately;
- reactivation events and their causes;
- H1 attempt count.

### 9.2 Recurrence rule

A materially similar recurrence of any accepted critical fixture during the dogfood interval fails Profile E until:

1. the recurrence is classified as activation, applicability, comprehension, embodiment, bypass, or evidence failure;
2. the fixture and selector/control are updated;
3. the stronger control passes mutation and regression evidence;
4. the incident no longer depends on another prose warning as its only remedy.

### 9.3 MVP-7 dogfood thresholds

Before MVP-7 Cognitive Utility acceptance:

- every R2/R3 MVP-5 and MVP-6 task within the declared dogfood scope has a valid activation receipt and independently captured before-design model-input delivery under the qualified CA-2 entry path; an uninstrumented task is a coverage miss that fails Profile E and remains in the denominator;
- every required independent-falsification receipt is present and bound to the published candidate;
- no accepted critical scar recurs undetected before independent review;
- no mature known hazard reaches owner-live H1 as its first detection surface;
- stale receipt use is zero;
- silent activation degradation is zero;
- median warm activation latency and write-path budgets meet Section 10;
- all newly discovered material incidents are represented in the gold corpus or explicitly mapped to an existing class.

Profile C's isolated trial transport does not qualify the production CA-2 entry path by itself. The dogfood entry path must carry its own real-harness capture. H1 may still find genuinely external or previously unknown behavior. Such a finding is not automatically an activation failure, but its classification and evidence MUST be recorded.

---

## 10. Operational and Performance Acceptance

### 10.1 Latency objectives

Measured on the supported reference machine and pinned corpus:

| Operation | Acceptance objective |
|---|---:|
| Changed-record canonical validation, p95 | `< 2 s` |
| Full canonical repository validation | `< 30 s` |
| Activation-index load, warm | `< 1 s` |
| Activation-index rebuild, cold | `< 5 s` |
| Task activation, warm p95 | `< 250 ms` |
| Task activation, cold p95 after index availability | `< 1 s` |
| Receipt verification, p95 | `< 100 ms` |

These are initial governance objectives, not excuses to drop protected cognition. A performance miss blocks replacement of the manual path until corrected or explicitly re-deliberated.

### 10.2 Mutation-path isolation

A canonical Context write SHALL require only bounded schema/link/lifecycle validation for the changed surface plus the existing atomic publication contract. It SHALL NOT synchronously execute fresh-consumer trials, full-corpus prompt rendering, embeddings, an LLM, or the former Python compilation pipeline.

Derived publication failure leaves the prior active generation available and reports the new generation as not activated. It does not corrupt canonical truth or pretend that the new cognition is ready.

### 10.3 Resource bounds

Acceptance records:

- index size and build memory;
- bundle canonical bytes and rendered tokens;
- protected/core/candidate proportions;
- cache hit rate;
- activation p50/p95/p99;
- number and cause of `Blocked`, `ReDeliberate`, and `BudgetInsufficient` results.

No average may hide an unbounded worst-case path on a supported corpus.

---

## 11. Evidence Package

The acceptance candidate publishes one immutable evidence package:

```text
cognitive-acceptance/<candidate-id>/
  manifest.json
  source-revisions.json
  policy-and-schema-digests.json
  conformance/
  applicability/
  fresh-consumer/
    assignments.json
    inputs/
    raw-outputs/
    scores/
    adjudications/
  falsification/
  dogfood/
  performance/
  incidents-and-exceptions.md
  acceptance-report.md
```

`manifest.json` binds every artifact digest and the tool/model/profile versions needed to interpret it. Sensitive raw content may be sealed behind the accepted evidence boundary, but its existence and digest cannot be omitted from the manifest.

The final report lists each claim as `Passed`, `Failed`, or `Not Evaluated`. It does not collapse all claims into one green status.

---

## 12. Failure and Re-Deliberation Rules

The candidate fails immediately on:

- one protected applicability miss;
- one critical miss in an activated fresh-consumer run;
- fabricated authority or accepted project truth;
- a superseded rule presented as current;
- silent truncation of protected cognition;
- receipt replay across a changed governed input;
- a required independent-evidence gap;
- recurrence of an accepted scar without stronger-control review;
- dependence on the retired Python compiler or a network/model service in the production activation path;
- a routine Context mutation path approaching the former multi-minute gate behavior;
- evidence selected, discarded, or rescored after condition labels are revealed without a recorded protocol correction.

A failed acceptance may be rerun only after the cause, change, new candidate digest, and affected fixture set are recorded. Unaffected sealed outputs may remain evidence when the root acceptance owner confirms their inputs are unchanged.

---

## 13. Replacement Acceptance for Manual Cold Boot

The current broad manual boot and active-memory-title sweep remain available during shadow mode. They may be reduced only after:

1. Profiles A through E pass for the production candidate;
2. the selected mandatory core is explicitly documented;
3. every removed boot item maps to an activation rule, an embodied control, or an explicit historical-only classification;
4. rollback to the last accepted generation is tested;
5. a fresh consumer can diagnose why an expected source was included or excluded;
6. two consecutive real-work milestones complete without a critical activation regression.

Reduction is incremental. Canonical records are not deleted merely because they leave the default working prompt.

---

## 14. Ongoing Surveillance After Acceptance

After MVP-7, the full paired fresh-consumer experiment runs when:

- the activation algorithm or priority model changes materially;
- critical selector semantics change;
- a new consumer renderer or model profile becomes supported;
- compression or semantic reranking is introduced;
- a critical scar recurs;
- the canonical corpus changes enough to exceed the accepted performance or budget envelope.

Daily engineering uses the fast conformance, applicability, receipt, and recurrence checks. The expensive causal experiment remains a milestone/release gate, not a mutation gate.

Drift review SHALL compare:

- protected coverage;
- unresolved applicability;
- candidate precision/recall;
- fresh-consumer scores;
- input volume;
- H1 escape categories;
- recurrence count;
- latency and failure rates.

---

## 15. Final Acceptance Statement

The root acceptance owner may sign the Cognitive Utility Gate only with the following statement:

> For the pinned Qiven generation, activation policy, native Runtime implementation, consumer profiles, and sealed engineering corpus named in this evidence package, Task Cognition Activation preserved all protected applicable cognition, materially improved or efficiently preserved fresh-consumer engineering correctness under the declared causal protocol, met operational latency bounds, and completed real-work dogfood without recurrence of an accepted critical scar. This statement does not expand Runtime authority, replace H1-H4, or generalize beyond the named evidence boundary.

If that statement cannot be made without qualification, the gate remains open.
