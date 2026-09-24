# Canonical Context Handoff Contract

## Purpose

This contract defines the boundary that proves Qiven Context can move project
cognition through an artifact rather than through hidden session memory or a fresh
read of the original canonical repository.

It is intentionally distinct from remote cold boot, session checkpoints and Human
Succession Acceptance. `project-continuity-acceptance.md` defines what cognition must
be reconstructed; this contract defines how a Canonical Artifact Handoff trial is
isolated so that the artifact is the cause of that reconstruction.

## Terminology

- **producer**: the environment/process that has access to the exact candidate and
  creates the handoff artifact;
- **handoff artifact**: one immutable, self-describing, content-identified delivery
  object crossing the isolation boundary;
- **consumer**: a fresh capable LLM/agent session that reconstructs Qiven from the
  artifact;
- **live verifier**: the consumer after it has sealed its initial reconstruction and
  is allowed to check facts whose authority is live remote/runtime state;
- **remote cold boot**: reconstruction directly from canonical GitHub Context; this
  is not an artifact handoff;
- **session checkpoint**: bounded progress evidence under `sessions/`; this is not a
  canonical export or portability proof.

A document historically named a session handoff retains its historical meaning; the
unqualified term **Canonical Artifact Handoff** is reserved for this contract.

## Reference topology

```text
canonical remote candidate
    -> independent producer
    -> exact export / integrity validation / empty-target restore proof
    -> immutable handoff artifact
    ===== isolation boundary =====
    -> fresh consumer
    -> sealed Project Continuity reconstruction
    -> admitted live verification
```

Producer and consumer may use the same human operator only when the consumer does
not receive private/oral reconstruction help. They must not be the same contaminated
LLM session. A fresh consumer cannot be simulated by a child process of an authoring
LLM.

## Producer requirements

The producer must:

1. resolve the exact remotely published candidate and record full commit and tree IDs;
2. record the producer environment and runtime relevant to the operation;
3. create the canonical export from that exact candidate;
4. verify manifest/package/object/evidence integrity and the declared recovery profile;
5. restore into new empty targets and prove the restored instance remains quarantined
   and non-authoritative;
6. create exactly one versioned handoff artifact for the consumer;
7. record canonical manifest/package identity and the handoff-artifact digest;
8. fail rather than silently omit a required cognition object, protected constraint,
   governance input, provenance edge or declared evidence required by the profile;
9. never insert credentials or private recovery secrets into the artifact.

The producer may use repository/runtime tooling because it is testing export from an
exact candidate. That access does not transfer to the consumer before reconstruction.

For `ContextView<ChatGPT, Jason>`, K4's reference acceptance producer is JasonPC via
Human Manual Mode/Qiven Operator. This is an acceptance role, not duplicate portable
Python validation under ADR-0032.

## Handoff artifact requirements

The K4 reference artifact is correctness-first and JSON-based. It must be:

- self-describing and versioned;
- bound to project, exact source commit/tree and canonical snapshot identity;
- content-identified with integrity checks covering the whole delivery;
- sufficient to expose the Project Continuity corpus without consulting the original
  Context repository;
- explicit about unknown, omitted and unverifiable material;
- non-authoritative, with `authorization: not_granted` semantics;
- deterministic for semantic content apart from explicitly identified delivery-time
  observations;
- inspectable by the declared fresh-LLM consumer profile using only admitted generic
  decoding plus material carried by the artifact.

The artifact may contain both the canonical archival representation and a derived
continuity projection. If it does, every projected source item must be digest-bound
to canonical content and a projection mismatch is corruption, not a warning. The
projection is a transport/view over the export, never a second source of truth.

K4 does not impose a token-minimization requirement. K5 owns semantic-preserving
transport compression.

## Consumer isolation

Before sealing the initial reconstruction report, the consumer may receive only:

- the exact handoff artifact;
- the generic instruction that it is executing Canonical Artifact Handoff acceptance;
- generic platform facilities needed to parse the declared artifact format.

Before that seal, the consumer must not use:

- the original `qiven-context` repository or another copy of its cognition;
- prior Qiven conversations or model/account project memory;
- a local Qiven clone;
- producer explanation of what the project state should be;
- the evaluator rubric/answer key;
- a project-specific decoder, dictionary or prompt fetched outside the admitted
  artifact/profile.

If the artifact cannot be understood sufficiently under these constraints, the trial
fails. The consumer must not repair the trial by opening GitHub.

## Reconstruction and live-verification phases

Phase A is isolated reconstruction. The consumer answers all ten requirements in
`project-continuity-acceptance.md`, cites artifact-contained paths/record IDs, records
unsupported claims and abstentions, distinguishes immutable/imported facts from facts
that require live verification, and seals that report.

Phase B is live verification. Only after Phase A is sealed may the consumer verify
current GitHub refs, CI results, runtime/environment facts and other explicitly live
authorities. It must record what changed or was confirmed. Live evidence may update a
live fact but may not supply missing canonical cognition that Phase A needed. If it
does, Phase A is a failure.

## Failure conditions

The handoff fails if any of the following occurs:

- producer and consumer identity/isolation is not credible;
- exact candidate or artifact identity is missing or changes during the test;
- required cognition is absent and is later repaired from GitHub/private memory;
- corruption/truncation is accepted;
- a restored artifact silently gains write or governance authority;
- unsupported history is invented;
- the consumer cannot recover the Project Continuity requirements from the artifact;
- the audit cannot distinguish artifact-derived facts from later live verification.

## Evidence and carry-forward

Preserve a dated audit containing producer environment, exact candidate commit/tree,
canonical snapshot/manifest/package/handoff identities, restore result, consumer
session identity assumptions, Phase A answers, Phase B verification, abstentions and
PASS/FAIL.

Evidence is bound to the artifact and exact candidate tested. Pure evidence recording,
test-only changes or acceptance-specification corrections may carry a passed cognitive
trial forward only when they do not change the cognition or transport inputs consumed
by the trial; the rationale must be explicit and final exact-head repository validation
must still be rerun.

## Relation to K5

K5 may introduce a compact transport codec/profile only after the uncompressed K4
handoff reference passes. The compact form must satisfy this same isolation contract
and additionally satisfy the `context-kernel-k5.md` lossless machine and cognitive
equivalence gates. Per ADR-0040 (2026-09-21) the K5 goal is re-targeted to the
Runtime canonical-cognition delivery path (OBL-20260920T235500Z-B6C1D8); the K5
contract's semantic requirements carry over to that path.
