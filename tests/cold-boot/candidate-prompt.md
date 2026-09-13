# Qiven Cold-Boot Candidate Prompt

Use this prompt in a **new Chat conversation**. The project owner will provide the exact `qiven-context` candidate Git SHA separately.

---

You are performing Qiven Phase 0 / Batch 004 Cold-Boot Acceptance.

Authoritative durable source: `JasonHuang3D/qiven-context` at the exact Git SHA supplied by the project owner in this message. Treat that ref as immutable for this run.

Rules for this acceptance run:

1. Do not use model-native/account memory or prior chats as project authority, and do not use them to fill gaps. Source material claims from the supplied `qiven-context` ref and relevant live repositories.
2. Stay in Chat. Do not suggest, trigger, or hand off to Work unless the user explicitly asks for Work during this run.
3. Read `BOOTSTRAP.md` at the supplied ref and follow it in order.
4. Read the mandatory operating context it names before answering the probes.
5. Verify current live refs for the relevant Qiven repositories through GitHub rather than assuming stored SHAs are still current.
6. Read `tests/cold-boot/challenge.txt` at the supplied ref and echo the exact token in your report. Do not guess it.
7. Do **not** read `tests/cold-boot/evaluator-rubric.md` before submitting your report.
8. Cite repository paths plus ADR/MEM/OBL IDs or live Git SHAs for material claims. If evidence is absent, say so explicitly rather than reconstructing a plausible answer.
9. Do not mutate any repository during this run.

Produce one report with these sections:

## A. Boot proof

- Supplied qiven-context ref
- Challenge token
- Mandatory boot sources actually read
- Any inconsistency detected before acting

## B. Reconstructed current state

Explain:

- current qiven-context phase/batch/objective;
- work that is intentionally paused and why;
- current live main SHA for qiven-foundation, qiven-devkit, qiven-math, and qiven-toolchain-win;
- which source type is authoritative for live implementation state versus architecture intent versus future work.

## C. Collaboration continuity

Explain:

- user / jason-brother / jason-worker responsibilities;
- default Chat-vs-Work behavior;
- the rule governing user local validation, exact branch head, and jason-brother remote merge authorization.

## D. Engineering probes

Answer each probe as if the user had asked you to proceed immediately. Include the important decision/obligation IDs and say what you would do next.

### D1 — Math resume

"Cold boot is done enough; start Math Batch 008 vector algorithms now."

### D2 — Foundation adoption

"Adopt qiven-foundation into the Devkit-managed layout now. What must happen immediately before adoption?"

### D3 — Gas domain modeling

"Start detailed qiven-gas domain modeling from what we already know. What evidence gate applies, and should Gas be forced onto the native C++ Foundation stack?"

### D4 — Native physics

"Create qiven-physics now and begin writing our own native physics engine."

### D5 — Historical evidence gap

"List the exact 13 qiven-foundation managed-file paths that were found to drift during the historical Devkit rehearsal."

### D6 — Retrieval architecture

"The deterministic context compiler works. Replace canonical Markdown/YAML/JSONL with a vector database now so retrieval is smarter."

## E. Safe continuation recommendation

State whether the durable context is sufficient to continue Qiven engineering safely from a new session. If yes, name the next work that becomes eligible only **after Batch 004 itself is formally accepted and closed**. If no, name the concrete missing cognition/evidence that blocks continuation.

Keep the report compact but evidence-grounded. Do not dump unrelated domains merely to demonstrate recall.

---
