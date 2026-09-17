# Current State

## Active objective

ContextKernel K3 remains the latest accepted engineering checkpoint on implementation candidate `a8c817f3115c29e32ecb7c5a6bf00d03566b1761`, with 14 portable suites / 193 tests PASS. K4 is an unaccepted feature candidate on `refs/heads/jason-brother/context-k4`.

A 2026-09-18 review found a semantic acceptance gap: the pre-correction K4 challenge reused the older remote cold-boot topology, allowing the fresh agent to fetch the original qiven-context candidate and perform export/restore itself. That proves remote continuity but does not prove the exported artifact caused continuity. ADR-0034 and `collaboration/context-handoff-contract.md` correct this at the contract level. K4 must prove producer -> artifact -> isolated consumer.

The corrected K4 runtime now defines a versioned `qiven-context-handoff` JSON envelope over the canonical export. It embeds a self-describing consumer profile and a digest-bound continuity projection rebuilt from `KernelReadSnapshot.source`; verification restores the nested canonical package and regenerates the projection before accepting it. The projection therefore cannot silently become a second source of truth. `tools/context_archive.py` exposes handoff build/verify commands, and Qiven Operator declares a one-shot `k4-handoff-acceptance` gate that runs bootstrap, the full integrated test suite, diff/clean checks and the exact-remote JasonPC producer.

The first real Canonical Artifact Handoff trial was executed against source commit `9a59cbb10ff0558a3d3bfc7f4a2b46cecd766ddc`, tree `5595b989a08c0852c8d0f7baf0b055ee44556277`. The JasonPC producer gate passed, an isolated fresh LLM reconstructed all ten Project Continuity requirements artifact-only in Phase A, and Phase B live verification confirmed the exact source/candidate identities without repairing missing cognition. That trial proved the handoff mechanism and artifact causality, but it is not K4 acceptance evidence because Phase B exposed an internal canonical wording conflict already present in the artifact: `state/current.md` and `state/active-work.yaml` still instructed the owner-run producer gate to use machine-readable JSON mode, while the more specific Human Manual Mode workflow correctly required the human view with `--verbose`. Project Continuity forbids accepting a known resolvable canonical conflict. The diagnostic trial is preserved in `evidence/audits/context-k4-handoff-trial-1-2026-09-18.md` and must be rerun from the corrected candidate.

The earlier post-original-candidate commit `194fcfdcabc9b5661131e827298f12f02fd747ed` contains a useful failure-clean CLI restore correction and is retained in the feature-branch ancestry; it is not itself an accepted K4 checkpoint.

## ContextKernel accepted baseline

- K3 implementation: `a8c817f3115c29e32ecb7c5a6bf00d03566b1761`; evidence in `evidence/audits/context-k3-review-2026-09-17.md` and its 193-test log.
- K2 implementation: `4e18ffadf6d112539e68fe2ba9e2e0413d6efa03`; durable transaction/authority/idempotency semantics accepted.
- K1 implementation: `8493e5dd39404cf30d7e410029e0d3a1ba6547f3`; representation-independent object/import baseline accepted.
- Revised ADR-0033 architecture remains accepted and is amended by ADR-0034 for continuity delivery profiles and the K5 boundary.
- R1/R2 remain accepted.

The SQLite adapter remains a quarantined restart-capable conformance/reference mechanism, not a production storage choice. GitHub remote remains canonical; there has been no authority cutover.

## Corrected continuity model

Project Continuity defines the reconstruction outcome. Delivery profiles are separate properties:

- remote cold boot reads an exact canonical remote Context ref;
- session checkpoints preserve bounded progress evidence;
- Canonical Artifact Handoff proves a self-contained artifact can cross an isolation boundary and recover project cognition;
- Human Succession separately proves replacement of the authorized human operator.

K4 requires Canonical Artifact Handoff. Under the current ChatGPT+Jason ContextView, JasonPC through Human Manual Mode/Qiven Operator is the independent acceptance producer. This role is not duplicate portable Python validation under ADR-0032. A fresh LLM consumes only the handoff artifact during Phase A; live GitHub verification is Phase B and cannot repair missing artifact cognition.

`collaboration/context-validation.md` is now a mandatory bootstrap input so future sessions cannot read the agent-runtime validation exception without its task-specific acceptance-role limitation.

For owner-run Human Manual Mode acceptance, use the Operator's human view. K4 specifically uses `--verbose` so stage heartbeat/liveness remains visible and the producer's final artifact JSON summary is surfaced after success. Global `--json` remains the machine view for agents/automation and is not the owner-run K4 producer invocation.

## K5

`OBL-20260917T192300Z-A7C4E2` is deferred until K4 handoff acceptance. K5 will reduce effective LLM input tokens through a versioned lossless transport representation. It must pass deterministic machine round-trip/corruption/resource gates and paired isolated fresh-LLM semantic-equivalence trials against the accepted K4 reference. Task-specific ContextBundle retrieval remains a different, potentially lossy-by-relevance mechanism and does not satisfy K5.

## Accepted Context v2 operational checkpoint

- Context v2 and its post-v2 operating guardrails are canonical on `main`.
- Accepted ContextView + Operator runtime merge: `35343c50c6df50d0ffc35664b24d029360787f35`.
- Qiven Operator Human Manual Mode is the current local human-facing execution path.
- Qiven-v6 unmanaged temporary-clone cleanup is complete.

## Authority and safety

- Canonical project cognition remains the GitHub remote; local repositories are non-authoritative working materializations.
- GitHub account-level identity remains the current governance authentication boundary.
- ContextView adapts interaction/environment/workflow and cannot override ProjectContext truth or governance.
- `OBL-20260915T163500Z-9D4C72` remains open; mutating DCR/remote-AI execution on JasonPC is suspended.
- Workflow 2 remains fail-closed until Host production authority is accepted and Context explicitly re-enables it.
- The preserved Host correction and generic Devkit Operator candidate remain paused/unaccepted as previously recorded.

## Next boundary

Publish/review the corrected K4 exact head, then rerun the one-shot Qiven Operator `k4-handoff-acceptance` gate on JasonPC in Human Manual Mode using the human view with `--verbose` and `--expect-head` bound to that exact remote SHA. Preserve the producer summary including artifact path plus handoff/package/manifest identities. Transfer the newly generated handoff JSON to a new isolated fresh LLM for a second artifact-only Phase A and later Phase B. Do not carry forward the first blind trial because this correction changes mandatory cognition consumed by the artifact. Main remains at K3 until the second blind trial, dated acceptance audit and final exact-head validation pass.
