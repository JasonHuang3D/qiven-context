# Qiven Context Runtime — Mandatory Retrieval and Context Leases

## Purpose

The Context Compiler is not reliable infrastructure if a reasoning model must remember to invoke it. Qiven therefore separates retrieval capability from retrieval invocation policy.

The stable runtime entry point is conceptually:

```text
qiven.context.prepare(query, previous_lease?) -> context_pack + context_lease
```

`tools/prepare_context.py` is the Phase 1 local implementation of that contract. A future MCP server, native ChatGPT tool, desktop integration, or other host adapter should wrap this same operation rather than expose storage/index details directly to the model.

## Mandatory turn preflight

For Qiven engineering conversations, the safe baseline policy is **retrieve on every turn before project-history facts are used**. This deliberately avoids making a task-transition classifier part of the safety boundary.

A host may later cache or reuse retrieval work, but reuse is an optimization. It must not turn `tool exists` into `tool may be forgotten` or make a probabilistic transition detector the only reason retrieval occurs.

The host sequence is:

```text
user turn
  -> qiven.context.prepare(...)
  -> Context Pack + Context Lease
  -> reasoning model
```

not:

```text
user turn
  -> reasoning model
  -> maybe remembers to call retrieval
```

## Context Lease

Every successful preparation emits a schema-validated Context Lease that records:

- the exact qiven-context Git `canonical_ref` used by the retrieval runtime;
- `source_clean: true`, proving no uncommitted canonical source change was hidden behind that ref;
- `retrieval_invoked: true`;
- the `mandatory_turn_preflight` policy;
- a task fingerprint derived from all retrieval selectors except `now`;
- whether the previous lease represents an initial turn, a task transition, or a same-task refresh;
- a SHA-256 digest of the generated Context Pack;
- an optional link to the previous lease.

Each successful invocation receives a distinct lease ID and invocation timestamp even if the query and generated pack are otherwise identical. The lease is **proof of retrieval execution and identity**, not canonical project truth. Canonical truth remains in Markdown/YAML/JSONL/JSON Schema + Git.

## Task fingerprints

Task fingerprints are diagnostic identity, not a permission to skip retrieval. Two turns with the same fingerprint still run retrieval and produce `same_task_refresh`. A changed fingerprint produces `task_transition`.

This prevents the fingerprint algorithm from becoming another silent false-negative safety boundary. If future measurement demonstrates that reuse is worth the optimization, reuse policy must be independently accepted and tested.

## MCP / tool boundary

MCP is a suitable transport because it makes the operation discoverable to an LLM host, but transport does not by itself guarantee invocation. A future adapter should expose a small tool surface, preferably one primary method:

```text
qiven.context.prepare
```

The host policy, not the model's memory, must guarantee that the method is called at the required boundary. Internal retrieval may later combine structured selectors, lexical/BM25, semantic embeddings/vector search, relations/graph expansion, and reranking/fusion without changing the tool contract.

## Retrieval benchmark

`benchmarks/retrieval/open-set-v1.yaml` freezes the first paraphrase/cross-domain benchmark before semantic or hybrid retrieval is tuned. It includes:

- the Windows interpreter incident that originally exposed the retrieval miss;
- human CLI liveness;
- exact-head merge authorization;
- Gas/native-stack separation;
- native-physics restraint;
- Math canonical layout;
- Devkit crash consistency;
- the retrieval-reliability decision itself.

The benchmark defines thresholds before final semantic/hybrid comparison. `tools/retrieval_benchmark.py` measures the current deterministic baseline without changing thresholds. `--enforce` turns the frozen thresholds into a gate; normal measurement mode reports results without pretending the current baseline already satisfies them.

The owner-validated deterministic baseline at `79872e04107c49bd82810fd5de49737e3d9c7686` achieved required-ID recall 1.000 but failed the frozen benchmark because critical-case recall was 0.500, forbidden hits were 3, and mean extra IDs were 19.500. The evidence is preserved in `evidence/audits/retrieval-open-set-v1-deterministic-baseline.md`.

## Semantic experiment channel

The first semantic candidate is intentionally implemented as a replaceable ranking backend rather than a new source of truth or a Qdrant service dependency.

`tools/semantic_retriever.py` ranks the same canonical record universe with embeddings and selects a bounded top-K set. The first experiment backend is FastEmbed `0.8.0` with `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, using local ONNX inference. Model files are cached outside the repository under the user cache directory (or `QIVEN_FASTEMBED_CACHE`) so semantic experiments do not dirty canonical source state.

The semantic dependency is optional:

```text
tools\bootstrap-semantic.cmd
```

Core `validate.cmd` and `test.cmd` do not require FastEmbed or a downloaded model. Unit tests inject a fake embedding backend so semantic contract/ranking code remains regression-tested without network or model provisioning.

Measure semantic retrieval against the unchanged benchmark with:

```text
.venv\Scripts\python.exe tools\retrieval_benchmark.py --mode semantic
```

The initial semantic selector uses `top_k=8`, fixed before observing semantic benchmark results. That bound is not declared sufficient in advance; it is an experiment parameter. If semantic-only retrieval loses required recall or retains forbidden hits, the next step is a measured hybrid/fusion path rather than moving the benchmark thresholds.

A later semantic/hybrid batch must run against the same frozen benchmark plus an additional blind/held-out acceptance set before retrieval reliability can be declared sufficient.
