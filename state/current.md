# Current State

## Active objective

ContextKernel K4 Canonical Artifact Handoff is accepted on implementation candidate `decc769aceb7043e0e7be48f8ba1c7bfe272e2e3`, tree `5a8491c9b7c2bb45564f381f43535d38dea2cc97`. The exact-head JasonPC producer, complete artifact identities, isolated fresh-consumer Phase A/B and evidence-closeout validation passed. Canonical publication is the exact validated merge of PR #15 to `main`.

A 2026-09-18 review found a semantic acceptance gap: the pre-correction K4 challenge reused the older remote cold-boot topology, allowing the fresh agent to fetch the original qiven-context candidate and perform export/restore itself. That proves remote continuity but does not prove the exported artifact caused continuity. ADR-0034 and `collaboration/context-handoff-contract.md` correct this at the contract level. K4 must prove producer -> artifact -> isolated consumer.

The corrected K4 runtime now defines a versioned `qiven-context-handoff` JSON envelope over the canonical export. It embeds a self-describing consumer profile and a digest-bound continuity projection rebuilt from `KernelReadSnapshot.source`; verification restores the nested canonical package and regenerates the projection before accepting it. The projection therefore cannot silently become a second source of truth. `tools/context_archive.py` exposes handoff build/verify commands, and Qiven Operator declares a one-shot `k4-handoff-acceptance` gate that runs bootstrap, the full integrated test suite, diff/clean checks and the exact-remote JasonPC producer.

The first real Canonical Artifact Handoff trial was executed against source commit `9a59cbb10ff0558a3d3bfc7f4a2b46cecd766ddc`, tree `5595b989a08c0852c8d0f7baf0b055ee44556277`. The JasonPC producer gate passed, an isolated fresh LLM reconstructed all ten Project Continuity requirements artifact-only in Phase A, and Phase B live verification confirmed the exact source/candidate identities without repairing missing cognition. That trial proved the handoff mechanism and artifact causality, but it is not K4 acceptance evidence because Phase B exposed an internal canonical wording conflict already present in the artifact: `state/current.md` and `state/active-work.yaml` still instructed the owner-run producer gate to use machine-readable JSON mode, while the more specific Human Manual Mode workflow correctly required the human view with `--verbose`. Project Continuity forbids accepting a known resolvable canonical conflict. The diagnostic trial is preserved in `evidence/audits/context-k4-handoff-trial-1-2026-09-18.md` and must be rerun from the corrected candidate.

The corrected second trial used exact candidate `decc769aceb7043e0e7be48f8ba1c7bfe272e2e3`. The owner-run JasonPC `k4-handoff-acceptance` gate passed on Windows 11 / Python 3.14.7 and produced a complete 3,199,824-byte artifact bound to snapshot `sha256:34829abf425aa1677d66e21ecdfcced7a99b608e540e3d87316834b93e6ca927` and handoff digest `sha256:22654511b2004ddbb9a8cba765ab89da7cc9a6f15070fdbe7ccfcc11b67c97b6`. A new fresh GPT-5.5 consumer using its lightest selected reasoning setting completed artifact-only Phase A, sealed it, and then completed Phase B live verification without repairing cognition or finding a contradiction. Full identities, report hashes and the acceptance rationale are preserved in `evidence/audits/context-k4-handoff-acceptance-2026-09-18.md`.

The earlier post-original-candidate commit `194fcfdcabc9b5661131e827298f12f02fd747ed` contains a useful failure-clean CLI restore correction and is retained in the feature-branch ancestry; it is not itself an accepted K4 checkpoint.

## ContextKernel accepted baseline

- K4 implementation: `decc769aceb7043e0e7be48f8ba1c7bfe272e2e3`; Canonical Artifact Handoff acceptance evidence in `evidence/audits/context-k4-handoff-acceptance-2026-09-18.md`.
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

`OBL-20260917T192300Z-A7C4E2` is now open because its K4-acceptance trigger is satisfied. K5 will reduce effective LLM input tokens through a versioned lossless transport representation. It must pass deterministic machine round-trip/corruption/resource gates and paired isolated fresh-LLM semantic-equivalence trials against the accepted K4 reference. Task-specific ContextBundle retrieval remains a different, potentially lossy-by-relevance mechanism and does not satisfy K5.

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

## Participant views and role bindings

ADR-0035 and ADR-0036 (2026-09-18) separate canonical roles from model instances and client-tool capability classes, and fix the typed human-handoff boundary (H1-H4, no-verbal-waiver, unattended automation read-only by default). `views/zcode-jason.yaml` is registered for ZCode (GLM) + Jason with bindings `jason-brother-glm5-3` (provisional; two delegated H2 review rounds recorded, upgrade owner-reserved against reviewer self-certification) and `jason-worker-glm5-3-flash` (qualified per OBL-20260918T164245Z-5D9B2E; evidence: merged transactions PR #16 `dec3e67e` and PR #17 `d134ce6`, exact-head gates PASS on Windows 11 / Python 3.14.7, first execution served by GLM-5.3-Flash after GLM-5.3 provider availability failures — disclosed per the ADR-0035 disclosure duty). Batch execution follows the delegated-review and execution-stage granularity rules in `views/workflows/local-supervised-agent.md`. `chatgpt-jason` remains active and semantically unchanged. The governance principal remains `github:JasonHuang3D`; there has been no authority cutover. `collaboration/human-handoff-boundary.md` joins the mandatory cold-boot input set.

## Next boundary

Execute the accepted F-series follow-up batches (F2 worker-flash qualification upgrade, then the F3-F5 cosmetic bundle), each as a worker-executed, brother-reviewed, owner-confirmed transaction per its obligation specification. Then implement K5 lossless semantic transport compression against the exact accepted K4 handoff reference. Establish pinned tokenizer measurements, deterministic round-trip/corruption/resource/security gates and paired isolated fresh-LLM semantic-equivalence trials before claiming improvement. Production storage, Host/DCR resumption and authority cutover remain separate.
