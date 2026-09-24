# Cold-Boot Acceptance Protocol — Remote Profile

## Current scope classification

This protocol is the historical **remote cold-boot delivery profile** for Project Continuity. It proves that a fresh reasoning session can reconstruct Qiven from an exact canonical GitHub Context ref plus admitted live repositories/evidence. It does not prove Canonical Artifact Handoff, export portability, backup sufficiency or Human Succession.

For current reconstruction semantics use `collaboration/project-continuity-acceptance.md`. For producer/artifact/consumer isolation use `collaboration/context-handoff-contract.md`.

## Purpose

Batch 004 tested the core promise of `qiven-context`: a new reasoning session must be able to reconstruct enough Qiven project cognition from durable remote context plus live repositories to act safely, without relying on prior chat continuity or model-native memory as project authority.

This was an end-to-end acceptance test, not another unit test for the Context Compiler. Batch 003 had already established deterministic retrieval and obligation evaluation. Batch 004 tested whether a fresh Chat session could use the durable remote system correctly.

## What counts as a remote cold boot

A valid candidate run starts in a new Chat conversation that has not participated in the current engineering session.

The candidate is instructed to:

- treat model-native/account memory and prior chats as non-authoritative and not use them to fill gaps;
- use the exact `qiven-context` Git ref supplied by the project owner as the durable cognition source;
- follow `BOOTSTRAP.md` in order;
- verify relevant live repositories rather than trusting stale recollection;
- cite canonical paths, ADR/MEM/OBL IDs, and live Git SHAs for material claims;
- report missing evidence or inconsistencies rather than inventing history;
- remain in its current interaction surface unless the owner explicitly switches the execution topology (ADR-0044).

A current-session self-rehearsal is useful for debugging the protocol but cannot by itself pass a remote cold boot because the current session is contaminated by prior conversation context.

## Acceptance dimensions

### 1. Boot discipline

The candidate must recover the Memory Constitution, Operating Contract, current state, active work, relevant obligations, decisions, and live repository state before recommending engineering action.

### 2. Current-state reconstruction

The candidate must reconstruct the active work recorded by the exact candidate being tested rather than substitute remembered state.

### 3. Obligation resurfacing

The candidate must surface relevant deferred/open work when a task touches its trigger boundary and distinguish relevance from a trigger actually being due/applicable.

### 4. Negative knowledge and restraint

The candidate must recover important "do not do this yet" decisions and must not fabricate unavailable details. Known historical gaps produce an evidence-gap response, not a plausible reconstruction.

### 5. Question-scoped authority

The candidate must use live Git for current implementation/ref state, ADRs for accepted architecture, obligations for future gates, and audit/evidence for validation claims. Conflicts must be reported rather than silently resolved by one global precedence rule.

### 6. Collaboration continuity

The candidate must recover the current collaboration model (single-session unified engineering, ADR-0044), the publication/H2 discipline, exact-head validation rules and conditional merge authority from the exact Context snapshot.

### 7. Selectivity

The candidate should retrieve enough context to answer each probe safely without dumping unrelated project domains into every answer.

## Historical candidate artifact

`tests/cold-boot/candidate-prompt.md` was the copyable instruction for the remote-profile fresh Chat. The project owner supplied the exact candidate Git SHA externally. A challenge token in the supplied ref provided lightweight proof that the session actually read the candidate repository.

This mechanism intentionally depends on remote repository access and therefore must not be reused as the K4 Canonical Artifact Handoff proof.

## Evaluation

A PASS requires the critical semantic assertions, no material fabrication, exact candidate/challenge identity, live-state verification where required, correct evidence-gap handling and sufficient recovered context to continue safely.

Non-critical wording differences are acceptable. This is semantic engineering acceptance, not text-similarity scoring.

## Evidence and closeout

Preserve candidate response, evaluator result, exact tested ref, live refs observed, discrepancies and corrections under `evidence/audits/`.

A remote cold-boot PASS remains valid evidence for remote continuity only. Do not relabel it as artifact-handoff acceptance. If a future test needs portable artifact continuity, invoke `context-handoff-contract.md` instead.
