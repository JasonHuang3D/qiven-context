# Generated Context

Generated context packs are derived artifacts. No generated context pack is canonical.

Batch 003 compiles task-specific working context from canonical state, project documents, ADRs, memory, and non-terminal obligations. Generated packs may be deleted or rebuilt at any time and must retain source paths/IDs back to canonical records.

The first compiler implementation is intentionally deterministic and local. Embeddings, vector databases, remote retrieval services, and model-native memory are not retrieval authorities in v1.

## Compile a task pack

On Windows after `tools\bootstrap.cmd`:

```cmd
tools\compile-context.cmd --query tests\fixtures\context-query-foundation-scope-exit.json --output-prefix generated\foundation-scope-exit
```

This writes both:

- `generated/foundation-scope-exit.json` — deterministic machine-readable manifest;
- `generated/foundation-scope-exit.md` — human/LLM-readable pack containing the selected canonical source material.

The Markdown renderer includes source paths, structured selection reasons, obligation trigger state, completion conditions, and the canonical source bodies. It is still derived working context: changes must be made to canonical source files, never by treating a generated pack as authoritative state.
