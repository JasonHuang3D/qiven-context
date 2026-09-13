# Context Compiler Acceptance — Batch 003

## Status

Batch 003 implementation is functionally complete enough for its final exact-head validation gate, but it is **not closed yet**. This audit is part of the candidate final Batch 003 head. The Batch 003 obligation must remain open and Batch 004 must not become active until the project owner validates this exact head and reports PASS.

The last user-validated implementation baseline before this final acceptance slice was `b6f25fcfcd80ec3b0fbbef575507d7bd803ce6a2`. On that baseline the local gate passed, with parallel suite timings of approximately 2.08 s for context compiler tests, 13.70 s for repository validator tests, 15.95 s for Windows Python-resolution tests, and 15.97 s wall time.

## Acceptance contract

Batch 003 is ready to close only when all of the following hold on one exact branch head:

1. Query input is schema validated and compilation is deterministic for fixed repository state plus fixed `now`.
2. Mandatory operating context is always present with source paths.
3. Project documents, ADRs, and memory are selected by deterministic explainable rules rather than opaque model similarity.
4. Non-terminal obligations (`open`, `deferred`, `blocked`) are considered and selected when relevant, related, explicitly requested, due, or applicable.
5. Trigger evaluation preserves `due`, `applicable`, `not_triggered`, `manual`, and `unresolved` as distinct states and does not infer a more specific trigger from a merely broad project match.
6. Generated JSON validates against the context-pack schema using local deterministic schema resolution.
7. Generated Markdown preserves canonical source paths, selection reasons, obligation trigger state, completion condition, and the underlying selected source content.
8. Generated artifacts remain derived/rebuildable and do not become canonical records.
9. High-value real task regressions recover the intended context for Foundation, Devkit adoption, Math representation/Batch 008, Gas discovery boundaries, and workspace staging.
10. Negative-recall regressions prove that unrelated Gas, Robotics, Foundation, Devkit, or Math obligations are not dumped into every pack merely because they are non-terminal.
11. Windows/Unix CLI wrappers can emit the same JSON + Markdown pack model from a query file.
12. Repository validation, the full test suite, live-state verification, and `git diff --check origin/main...HEAD` all pass on the exact candidate head.

## Final acceptance regressions

The final slice adds dedicated fixtures for:

- Foundation ScopeExit;
- Math `Vec3f` representation;
- first detailed Gas domain-model / implementation boundary;
- Foundation Devkit adoption.

It also adds a separate `context-acceptance` test suite that verifies:

- Foundation packs surface ADR-0007 and the deferred ScopeExit obligation while excluding unrelated Gas/Robotics obligations;
- Math packs surface ADR-0014 and the Batch 007 vector-core memory while excluding unrelated Gas/Devkit obligations;
- Gas packs surface ADR-0020 and make original-discovery recovery due at the explicit implementation boundary;
- Devkit adoption packs surface the hash/conflict lifecycle decision and the semantic managed-drift obligation;
- Math Batch 008 remains gated while Batch 004 cold-boot acceptance is not explicitly complete;
- a specific `on_touch` trigger is not satisfied by a broad project scope alone;
- workspace creation remains condition-gated rather than becoming due merely because the task mentions `qiven-workspace`;
- the CLI emits schema-valid JSON and source-grounded Markdown;
- fixed queries remain reproducible.

## Conservative trigger correction

The final acceptance review found one subtle trigger-matching hazard in the pre-final implementation: lexical matching accepted the reverse subset direction and shared hyphenated compounds. That could let a broad candidate such as `qiven-foundation` satisfy a more specific trigger such as `qiven-foundation/recoverable-structured-error-contract`.

The trigger matcher is now directional: the complete trigger target must be present in the candidate evidence. This preserves the intended conservative rule that broad topical relevance may surface an obligation without falsely claiming that its specific trigger has fired.

## Out of scope

Batch 003 still does not introduce embeddings, vector databases, learned ranking, graph databases, MCP retrieval services, or model-generated synonym expansion. Those remain derived future options only if Batch 004 cold-boot acceptance demonstrates a concrete recall failure that deterministic retrieval cannot address cleanly.

## Closeout rule

After the exact candidate head passes the final local gate, close `OBL-20260913T152950Z-0A1B2C`, record the Batch 003 closeout checkpoint, transition active work to Batch 004 — Cold-Boot Acceptance, and merge the exact validated head to `main` under ADR-0021. Any commit added after the validated head invalidates that PASS for merge purposes.
