# Context Compiler — Deterministic Retrieval Contract

## Purpose

Batch 003 turns the canonical cognition captured by `qiven-context` into task-specific working context without making generated output canonical.

The compiler answers one operational question: given a concrete task, what current state, project knowledge, decisions, memory, and unfinished obligations should a new reasoning session see before acting?

The first implementation is deliberately deterministic, explainable, local, and rebuildable. It does not use embeddings, a vector database, a remote service, or model-native memory as a retrieval authority. This follows ADR-0003; semantic retrieval can be added later as a derived layer if deterministic retrieval proves insufficient.

## Non-goals

Batch 003 v1 does not:

- replace canonical Markdown/YAML/JSONL with a database;
- decide architectural truth by one global source-precedence rule;
- silently resolve contradictions;
- infer a trigger from vague semantic similarity;
- generate new canonical memories, ADRs, or obligations;
- mutate live project repositories;
- treat generated packs as evidence or project state;
- implement embeddings, vector search, graph databases, MCP, or an always-on service.

## Input contract

The compiler consumes a JSON query that conforms to `schema/context-query.schema.json`.

Required:

- `task`: the concrete task or question being prepared for.

Optional explicit selectors:

- `topics`: domain terms the caller wants included in lexical relevance matching;
- `scopes`: canonical/project scopes such as `qiven-foundation`, `qiven-devkit`, `qiven-math`, `qiven-context`, `qiven-cad`, `qiven-gas`, or `qiven-robotics`;
- `touches`: files, components, subsystems, or named areas the task will touch;
- `signals`: explicit lifecycle/event phrases used for deterministic trigger evaluation;
- `conditions`: explicit condition phrases known true for this compilation;
- `changed`: paths/components known to have changed, for `on_change` obligations;
- `include_ids`: canonical ADR/MEM/OBL IDs that the caller explicitly requires in the pack;
- `now`: an ISO-8601 timestamp used for reproducible `on_date` evaluation. When absent, the compiler may use the current UTC time and must record it in the generated pack.

The query is a selector, not canonical knowledge. A query must not be persisted as a fact merely because it was supplied to the compiler.

## Compilation pipeline

The compiler performs these stages in order.

### 1. Load mandatory operating context

Always load:

- `MEMORY-CONSTITUTION.md`;
- `collaboration/operating-contract.md`;
- `state/current.md`;
- `state/active-work.yaml`.

These establish how to interpret the rest of the pack. The compiler may summarize them in the rendered pack, but must retain source paths.

### 2. Build deterministic query terms

Normalize terms from `task`, `topics`, `scopes`, and `touches` by:

- Unicode case-folding;
- splitting on non-alphanumeric boundaries while preserving useful hyphenated repository names as whole terms as well as components;
- discarding empty tokens;
- de-duplicating terms without changing deterministic sort order.

No embeddings or model-generated synonyms are introduced in v1.

### 3. Select project documents

Project documents under `projects/<name>/` are selected when:

- their project scope is explicitly listed in `scopes`; or
- their project/repository name has lexical overlap with the normalized query terms.

Explicit scope selection outranks incidental lexical overlap for ordering, but it does not make the selected document more authoritative for unrelated questions.

### 4. Select ADRs and canonical memory

ADRs and memory records are ranked using only deterministic metadata/content signals.

V1 relevance signals, in descending priority:

1. explicit ID selection;
2. exact scope match;
3. exact tag match;
4. exact repository/project-name match;
5. title token overlap;
6. heading/body token overlap;
7. one-hop explicit `related` links from an already selected canonical record.

The implementation must expose why each record was selected. Numeric weights are implementation details but must be fixed, documented in code, and covered by tests; they must not be learned or model-generated.

Selection is relevance filtering, not truth resolution. If two relevant records conflict, both remain visible with their provenance/status so question-scoped authority can be reasoned about later.

### 5. Retrieve non-terminal obligations

Every obligation with status `open`, `deferred`, or `blocked` is considered by the obligation evaluator. Terminal obligations (`done`, `cancelled`, `superseded`) are excluded from normal task packs unless explicitly requested for historical analysis or reached through a relation that matters to the task.

For each considered non-terminal obligation, the compiler records:

- obligation ID and status;
- trigger type and target;
- evaluation result;
- relevance reason;
- completion condition;
- canonical source path.

An obligation is included in the task pack when at least one of the following is true:

- its trigger evaluates `due` or `applicable`;
- its scope/tags/title lexically match the task;
- it is explicitly related to a selected ADR/memory record;
- the caller explicitly names its ID through `include_ids`.

The compiler must not silently drop a relevant `deferred` or `blocked` obligation merely because it is not currently `open`.

## Trigger evaluation v1

Trigger evaluation is intentionally conservative. V1 prefers `unresolved` over guessing.

### `on_touch`

`applicable` when the normalized trigger value matches an explicit `touches` item, scope, topic, or task term. Otherwise `not_triggered`.

### `before`

`due` only when the trigger value matches an explicit `signals` item or the task/touches describe that named boundary using deterministic lexical matching. If the match is ambiguous, return `unresolved` rather than inferring intent.

### `after`

`due` when the trigger value appears in explicit `signals` indicating the prerequisite is complete, or when canonical current state/ledger exposes an exact completed event that the implementation is explicitly coded to recognize. Do not infer completion from repository age or absence of work.

### `on_change`

`applicable` when the trigger value matches an item in `changed`. Otherwise `not_triggered`.

### `on_date`

Parse the trigger value as a supported ISO-8601 date/time. `due` when `now` is at or after the trigger time. Invalid or unsupported date syntax is `unresolved` and must be visible in diagnostics.

### `condition`

`due` only when the normalized trigger value is explicitly present in `conditions`. V1 does not ask a model to decide whether a natural-language condition is true.

### `manual`

Always `manual`; never automatically promoted to `due`.

## Trigger result vocabulary

The evaluator uses exactly these states:

- `due`: the obligation's stated temporal/logical boundary has been met;
- `applicable`: the current task directly touches the obligation's trigger area;
- `not_triggered`: deterministic input says the trigger does not currently fire;
- `manual`: explicit human decision is required;
- `unresolved`: available deterministic evidence is insufficient or invalid.

`unresolved` is not equivalent to `not_triggered`.

## Question-scoped authority

The compiler selects context; it does not create a universal authority ranking.

A generated pack must preserve enough metadata for the reasoning layer to distinguish questions such as:

- current implementation state -> live Git/repository evidence;
- validation outcome -> CI/local validation evidence;
- architecture intent -> accepted ADRs and explicit user decisions;
- local-machine incident -> scoped local observation;
- future work -> non-terminal obligations and their triggers.

When relevant sources disagree, the compiler should surface the disagreement rather than choose a winner based on a single global priority table.

## Output contract

Compilation produces a machine-readable manifest conforming to `schema/context-pack.schema.json`. A later renderer may produce Markdown for LLM consumption from the same manifest.

The pack contains:

- the normalized query and compilation timestamp;
- mandatory operating/state sources;
- selected project documents;
- selected ADRs;
- selected memory records;
- selected non-terminal obligations with trigger evaluations;
- selection reasons for every non-mandatory item;
- diagnostics, including unresolved triggers or missing references;
- source paths/IDs needed to inspect canonical truth directly.

Stable deterministic ordering is required so the same repository state + same query + same `now` produces the same manifest.

## Generated artifact rules

Everything under `generated/` is derived and rebuildable.

Generated packs:

- are never canonical;
- may be deleted or overwritten at any time;
- must not be used to update canonical records without returning to original sources;
- must not be cited as stronger evidence than the canonical/evidence records they summarize;
- must contain enough source references to let a reader inspect canonical material.

The canonical system remains Markdown/YAML/JSONL/JSON Schema + Git.

## Determinism and explainability requirements

Given identical canonical repository content, identical query JSON, and identical `now`, the compiler must produce identical machine-readable selection and trigger results.

For every selected non-mandatory item, the result must answer `why was this included?` with structured reasons rather than an opaque similarity score.

For every excluded or unresolved trigger that is inspected in a test, behavior must be reproducible without calling an LLM or network service.

## Batch 003 implementation sequence

1. Freeze this query/output/trigger contract.
2. Implement canonical loaders and deterministic normalization.
3. Implement obligation trigger evaluation.
4. Implement relevance scoring/selection with explainable reasons.
5. Emit machine-readable packs and Markdown rendering.
6. Add regression fixtures for Foundation, Devkit, Math, CAD/Gas/Robotics, and cross-domain obligations.
7. Validate generated-pack behavior before Batch 004 cold-boot acceptance.

Semantic retrieval is a later optimization only if Batch 004 demonstrates a real recall failure that deterministic retrieval cannot solve cleanly.