# Generated Context

`generated/` contains derived, rebuildable task-context artifacts produced by the Batch 003 context compiler.

No file in this directory is canonical project cognition. Generated packs may be deleted or overwritten at any time and must point back to canonical source paths/IDs.

The v1 compiler contract is defined in `collaboration/context-compiler.md` with machine-readable schemas in:

- `schema/context-query.schema.json`
- `schema/context-pack.schema.json`

The compiler will produce a deterministic machine-readable pack first; Markdown rendering for LLM consumption is a derived view of the same selection. With identical repository content, query, and resolved `now`, selection and trigger evaluation must be reproducible.

Generated packs must never be used as stronger evidence than the canonical records or evidence artifacts they summarize.