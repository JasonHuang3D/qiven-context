# Genesis Import Methodology

## Purpose

Genesis Import reconstructs durable Qiven project cognition from historical evidence without pretending the historical record is more complete or certain than it is.

The objective is not to produce a transcript summary. The objective is to recover the project state that a new `jason-brother` would need in order to reason continuously with the current team: accepted decisions, rejected alternatives, deferred obligations, validation gaps, risks, assumptions, lessons, incidents, project boundaries, and useful reasoning residue.

Genesis Import is a one-time historical reconstruction pass performed under the Memory Constitution. Future cognition should enter through normal context checkpoints so the loss window stays small.

## Non-goals

Genesis Import does not:

- treat model-native memory as authoritative evidence;
- convert every historical sentence into canonical memory;
- infer missing decisions merely because current code looks a certain way;
- upgrade a candidate, hypothesis, or implementation accident into an accepted architectural decision;
- rewrite history to make the project look more consistent than it actually was;
- delete contradictory evidence;
- import secrets or credentials;
- build context packs, embeddings, vector indexes, SQLite, MCP, or retrieval services.

## Evidence-first workflow

For each domain, use this order:

1. Identify source evidence.
2. Extract candidate cognition statements without changing their epistemic type.
3. Classify each candidate.
4. Cross-check it against stronger or independent evidence where available.
5. Promote it into canonical memory, an ADR, or an obligation only when the promotion rule is satisfied.
6. Preserve uncertainty, disagreement, temporal changes, and supersession explicitly.
7. Update indexes and relations.
8. Run repository validation before accepting the import slice.

A historical source may support several canonical records, and several historical sources may support one record.

## Question-scoped authority during import

Authority depends on the question being reconstructed.

- Current or historical code state: Git commits, repository files, diffs, and tags are primary.
- Actual validation results: CI runs, test logs, and recorded local validation evidence are primary.
- Explicit architecture or process decisions: direct user statements, accepted ADR-like discussion, and committed engineering protocol are primary.
- Worker execution outcomes: worker handoffs are evidence, but exact committed state and CI may contradict or refine them.
- Historical intent and rationale: contemporaneous conversation and engineering documents may be primary when code alone cannot answer why.
- Future work that must resurface: explicit deferral language and follow-up commitments become candidate obligations.

No source category receives universal precedence.

## Source-strength dimensions

Evaluate evidence on separate dimensions instead of using one global confidence score:

### Directness

- **direct**: the source explicitly states the cognition being imported;
- **derived**: the cognition is a conservative inference from direct evidence;
- **speculative**: the cognition requires assumptions not established by the evidence.

Speculative candidates must not become verified facts or accepted decisions.

### Independence

Multiple copies of the same handoff or summary do not count as independent corroboration. Prefer independent evidence such as a conversation statement plus a matching commit or CI run.

### Temporal proximity

Contemporaneous evidence is normally stronger for historical rationale than a later retrospective summary. A later correction or explicit supersession can still override the earlier interpretation while preserving the earlier record.

### Machine verifiability

Commit SHAs, repository files, CI runs, and test results are more mechanically verifiable than narrative recollection for claims about actual implementation or validation.

## Candidate classification rubric

Every extracted candidate must first be classified into one of these destinations.

### ADR candidate

Use an ADR when the evidence supports a durable architectural, repository, process, or system-design decision whose rationale and alternatives matter to future decisions.

Promote to an ADR only when:

- the choice was explicit enough to distinguish it from brainstorming;
- the decision affected or constrained later work;
- rationale can be reconstructed without inventing it;
- alternatives or trade-offs are known well enough to document honestly.

If those conditions are not met, keep it as ordinary memory rather than manufacturing an ADR.

### Canonical memory candidate

Use a memory record for durable cognition that does not need a full ADR lifecycle, including facts, observations, assumptions, hypotheses, constraints, invariants, protocols, risks, issues, debt, limitations, lessons, incidents, alternatives, rejected options, and open questions.

Preserve the original epistemic type. In particular:

- an observed pattern is not automatically an invariant;
- an anticipated repository is not automatically a committed roadmap item;
- an implementation currently present in Git is not automatically an architectural preference;
- an assistant proposal is not automatically a user-approved decision.

### Obligation candidate

Use an obligation when the historical cognition carries future resurfacing semantics.

Common cues include:

- later;
- not now;
- remember this;
- non-blocking;
- revisit;
- when we touch X;
- before release/freeze;
- validation still missing;
- if condition Y happens;
- we owe a follow-up;
- this is intentionally deferred.

A non-terminal obligation must have a meaningful trigger. If a trigger cannot be reconstructed, do not invent one; preserve the item as memory or an open question and mark the missing trigger as a Genesis gap.

### Evidence-only candidate

Some material should remain evidence only. Examples include transient troubleshooting output, duplicated statements, conversational filler, implementation detail already fully represented by Git, and claims whose provenance is too weak to promote safely.

Evidence-only does not mean unimportant; it means the material is not canonical cognition by itself.

## Promotion rules

### Evidence -> fact

Require direct evidence of the proposition. For implementation facts, prefer live or historical Git evidence. For validation facts, prefer CI/test evidence.

### Evidence -> decision / ADR

Require explicit choice or a clearly accepted operating rule. Do not infer acceptance solely from the absence of objections.

### Evidence -> rejected option

Require evidence that the option was actually considered and rejected, plus the rejection rationale when available. If only an alternative was mentioned, classify it as `alternative`, not `rejected_option`.

### Evidence -> invariant / protocol / constraint

Require evidence that the rule is intended to constrain future behavior, not merely describe a one-time implementation.

### Evidence -> hypothesis / candidate / assumption

Use these types when the historical statement was tentative or contingent. Preserve uncertainty rather than normalizing it away.

### Evidence -> obligation

Require explicit or strongly implied future resurfacing semantics. The import must preserve `why_not_now` and a trigger when known.

## Reasoning residue pass

After the normal domain import, perform a dedicated residue scan because these items are easy to omit from ordinary summaries.

Search for language and semantics equivalent to:

- later / afterward / eventually;
- not now / for now / first do X;
- remember / keep this in mind;
- non-blocking / not worth interrupting the mainline;
- TODO / follow-up / validation gap;
- maybe / possible / likely / consider;
- rejected / do not / avoid;
- if we later / once X exists / when touching Y;
- known limitation / accepted limitation / technical debt;
- concern / risk / unclear / unresolved.

For each residue item, determine whether it is already closed, superseded, still active, or merely historical context.

The residue pass must not promote vague conversational possibilities into obligations unless future resurfacing intent is present.

## Contradictions and supersession

Do not merge contradictory historical statements into one artificial consensus.

When evidence shows a decision changed:

- preserve the earlier record;
- mark it superseded when the schema permits;
- link the successor;
- retain dates and provenance.

When the contradiction cannot be resolved, create an observation, issue, or open question instead of choosing silently.

## Timestamp policy

Genesis import time is not the same as historical validity time.

- `created_at` and `updated_at` on newly created canonical records describe when the record was materialized in `qiven-context` unless reliable historical record-creation metadata is available and the schema semantics explicitly call for it.
- `temporal.valid_from` should represent when the cognition became valid only when that point can be supported; otherwise use the earliest defensible evidence time and explain uncertainty in the body.
- never fabricate precise historical timestamps from approximate conversation memory.

## Provenance policy

Every canonical record must point to the best available source references. Prefer stable references such as commit SHAs, repository paths at a ref, CI run IDs, handoff identifiers, or named session/checkpoint evidence.

A retrospective summary may be cited, but it must be identified as retrospective rather than silently treated as contemporaneous evidence.

If evidence is unavailable to the current tools, record the retrieval limitation instead of fabricating a source.

## YAML and serialization safety

Canonical Markdown front matter and structured YAML must never be constructed by unsafe string concatenation of arbitrary natural language.

Rules:

- use a YAML serializer whenever generation is automated;
- when writing manually, quote or block-scalar all natural-language values that may contain YAML-significant characters such as `: `, `#`, leading punctuation, or ambiguous scalar forms;
- run `tools\validate.cmd` before accepting every import slice;
- a passing visual review is not evidence that YAML is syntactically valid.

This rule exists because Batch 001 checkpoint validation caught malformed provenance caused by an unquoted `: ` sequence.

## Import slicing

Genesis Import should be committed in reviewable slices rather than one monolithic historical dump. Planned order:

1. collaboration, Git, CI, and worker protocol;
2. Foundation;
3. Devkit;
4. Math;
5. ecosystem roadmap and CAD / Robotics / Gas boundaries;
6. cross-domain deferred items, rejected options, validation gaps, risks, and reasoning residue;
7. final completeness audit and Genesis checkpoint.

Each slice must leave the repository valid before the next begins.

## Completeness standard

Genesis cannot guarantee perfect recovery of every historical thought because not all original conversations or raw artifacts may be accessible. Completion therefore means:

- every source in the Source Manifest has been reviewed to the extent available;
- each planned domain has received a normal extraction pass and a residue pass;
- unresolvable evidence gaps are recorded explicitly;
- open/deferred cognition discovered during import is represented as obligations where appropriate;
- no known high-value candidate remains unclassified without a documented reason;
- repository validation passes.

The system remains correctable after Genesis because evidence and canonical interpretation stay separate.
