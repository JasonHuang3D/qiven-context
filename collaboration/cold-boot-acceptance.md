# Cold-Boot Acceptance Protocol

## Purpose

Batch 004 tests the core promise of `qiven-context`: a new reasoning session must be able to reconstruct enough Qiven project cognition from durable context plus live repositories to act safely, without relying on prior chat continuity or model-native memory as project authority.

This is an end-to-end acceptance test, not another unit test for the Context Compiler. Batch 003 already established deterministic retrieval and obligation evaluation. Batch 004 tests whether a fresh Chat session can use the durable system correctly.

## What counts as a cold boot

A valid candidate run starts in a new Chat conversation that has not participated in the current engineering session.

The candidate is instructed to:

- treat model-native/account memory and prior chats as non-authoritative and not use them to fill gaps;
- use the exact `qiven-context` Git ref supplied by the project owner as the durable cognition source;
- follow `BOOTSTRAP.md` in order;
- verify relevant live repositories rather than trusting stale recollection;
- cite canonical paths, ADR/MEM/OBL IDs, and live Git SHAs for material claims;
- report missing evidence or inconsistencies rather than inventing history;
- remain in Chat unless the user explicitly requests Work.

A current-session self-rehearsal is useful for debugging the protocol but cannot by itself pass Batch 004 because the current session is contaminated by prior conversation context.

## Acceptance dimensions

### 1. Boot discipline

The candidate must recover the Memory Constitution, Operating Contract, current state, active work, relevant obligations, decisions, and live repository state before recommending engineering action.

### 2. Current-state reconstruction

The candidate must identify Batch 004 — Cold-Boot Acceptance as active work and preserve the pause on Foundation managed-drift reconciliation, Foundation Devkit adoption, and Math Batch 008 until the cold-boot gate itself passes.

### 3. Obligation resurfacing

The candidate must surface relevant deferred/open work when a task touches its trigger boundary. It must distinguish relevance from a trigger actually being due/applicable.

### 4. Negative knowledge and restraint

The candidate must recover important "do not do this yet" decisions and must not fabricate unavailable details. In particular, a request for historical details that are known to be absent must produce an evidence-gap response, not a plausible reconstruction.

### 5. Question-scoped authority

The candidate must use live Git for current implementation/ref state, ADRs for accepted architecture, obligations for future gates, and audit/evidence for validation claims. Conflicts must be reported rather than silently resolved by one global precedence rule.

### 6. Collaboration continuity

The candidate must recover the user/jason-brother/jason-worker role split, Chat-first execution-mode control, the exact-head validation rule, and the conditional remote merge authorization in ADR-0021.

### 7. Selectivity

The candidate should retrieve enough context to answer each probe safely without dumping unrelated project domains into every answer.

## Candidate artifact

`tests/cold-boot/candidate-prompt.md` is the copyable instruction used in a fresh Chat. The project owner supplies the exact candidate Git SHA externally; the repository does not self-pin its own continuously changing head.

The candidate must read `tests/cold-boot/challenge.txt` from the supplied ref and echo the token in its report. The prompt intentionally does not contain the token. This is a lightweight proof that the tested session actually read the candidate repository state rather than answering entirely from account memory.

## Evaluation

The candidate response is evaluated against `tests/cold-boot/evaluator-rubric.md` only after the response is complete. The candidate prompt explicitly forbids reading the evaluator rubric before submission.

A PASS requires:

- every critical assertion in the rubric to pass;
- no critical fabricated fact or invented source;
- the exact challenge token to be recovered from the candidate ref;
- live repository verification to distinguish current live state from canonical intent;
- the historical evidence-gap probe to be handled without invention;
- the fresh session to stay in Chat and not initiate a Work handoff;
- the project owner and jason-brother to agree that the recovered context is sufficient to continue engineering safely.

Non-critical wording differences are acceptable. This is a semantic engineering acceptance test, not a text-similarity benchmark.

## Evidence and closeout

The candidate response, evaluator result, exact tested ref, live refs observed during the run, discrepancies, and any corrective changes must be preserved under `evidence/audits/` before Batch 004 is closed.

If the run fails because durable context is missing or retrieval is ambiguous, fix the durable system and repeat from a new Chat. Do not patch the candidate response manually and call the same run a pass.

After a clean cold-boot PASS is preserved, `OBL-20260913T152950Z-D4E5F6` may close and paused Foundation/Math progression may be reconsidered in the order recorded by active planning. Batch 004 itself must still receive the normal exact-head local validation and merge gate under ADR-0021.
