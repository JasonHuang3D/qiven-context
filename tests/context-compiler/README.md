# Context Compiler Test Plan

Batch 003 compiler tests must prove deterministic selection and obligation resurfacing, not just schema validity.

## Required regression scenarios

### Foundation demand-driven primitive

Query about adding or revisiting a Foundation scope-exit/defer primitive.

Expected behavior:

- select the Foundation project model;
- select ADR-0007 or equivalent Foundation small/downstream-demand-driven decision context;
- surface `OBL-20260913T181224Z-A3F690`;
- do not pull unrelated Gas or Robotics obligations merely because they are non-terminal.

### Foundation result/status boundary

Query about adding a public recoverable status/result API.

Expected behavior:

- surface `OBL-20260913T181224Z-9E27A4`;
- preserve the obligation as deferred/demand-triggered rather than presenting it as an already implemented primitive.

### Devkit adoption

Query scoped to Foundation Devkit adoption.

Expected behavior:

- select Devkit lifecycle ADRs;
- surface `OBL-20260913T182338Z-4F7C19` requiring semantic reconciliation of the thirteen managed drifts;
- preserve the crash-consistency limitation as relevant memory when the task concerns adoption/sync safety.

### Math Vec3 representation

Query about making `Vec3f` SIMD-friendly or `alignas(16)`.

Expected behavior:

- select ADR-0014;
- select the Batch 007 vector-core memory;
- explain selection through Math scope/title/content matches;
- do not convert the compact representation decision into an ABI/wire-format claim.

### Math Batch 008 resume

Query to resume vector algorithms.

Expected behavior:

- surface `OBL-20260913T182954Z-7B4E20`;
- report its cold-boot acceptance prerequisite rather than silently starting implementation.

### Gas detailed domain modeling

Query describing the first detailed industrial-gas domain-model batch.

Expected behavior:

- select the Gas project model and ADR-0020;
- evaluate `OBL-20260913T185050Z-21DCBC` as due/applicable when the query supplies the matching `before` signal;
- require original discovery evidence before detailed modeling.

### Workspace creation

Query about creating `qiven-workspace`.

Expected behavior:

- surface ADR-0018;
- surface `OBL-20260913T183819Z-2C7A11`;
- preserve the trigger that recurring multi-repository coordination pressure must exist.

### Trigger conservatism

Fixtures must cover every trigger type:

- `on_touch` -> applicable only on deterministic match;
- `before` -> due on explicit boundary signal; ambiguous input -> unresolved;
- `after` -> due only with explicit/canonical completion signal;
- `on_change` -> applicable only from `changed`;
- `on_date` -> deterministic against supplied `now`;
- `condition` -> due only from explicit `conditions`;
- `manual` -> always manual, never auto-due.

The test suite must distinguish `unresolved` from `not_triggered`.

## Determinism test

Compile the same fixture twice with identical repository content, query, and `now`. The machine-readable manifests must be byte-for-byte identical after any explicitly documented output-path normalization.

## Explainability test

Every non-mandatory selected record must contain at least one structured selection reason. A test should fail if a selected item appears only because of an opaque score.

## Negative-recall test

At least one fixture per project must assert that high-value but unrelated obligations are not included. Conservative capture does not justify dumping all canonical cognition into every task pack.

## Generated-artifact test

Generated pack files may exist under `generated/` without becoming canonical records or index entries. Repository validation must continue to ignore generated packs for canonical-ID scans while still allowing compiler-specific schema validation.