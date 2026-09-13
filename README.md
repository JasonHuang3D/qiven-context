# qiven-context

`qiven-context` is Qiven's durable, Git-versioned repository for externalized project cognition. It preserves current state, accepted and rejected reasoning, unresolved and deferred work, validation gaps, risks, assumptions, lessons, incidents, collaboration rules, provenance, and revisit triggers independently of any model session.

It is not a C++ library, a qiven-devkit consumer, a generic notes repository, a vector database, an MCP/API service, or a transcript dump.

## Memory layers

- **L0 — Live world:** authoritative external reality such as Git, builds, tests, CI, and external systems.
- **L1 — Evidence archive:** raw or near-raw sessions, handoffs, CI results, audits, research, and source references.
- **L2 — Cognition ledger:** append-oriented events such as noticed, learned, questioned, decided, deferred, rejected, and superseded.
- **L3 — Canonical knowledge:** curated state, memory records, obligations, ADRs, project models, and collaboration protocol.
- **L4 — Working context:** derived, task-specific context packs. L4 is never canonical.

Evidence and canonical interpretation remain separate so interpretations can be corrected without destroying their sources. Generated context is derived and rebuildable. Private repository does not mean secret store: never commit credentials, tokens, private keys, recovery codes, or API keys.

## Cold boot and tooling

Start with [BOOTSTRAP.md](BOOTSTRAP.md). Use Python 3.11 or newer.

```text
tools\bootstrap.cmd
tools\validate.cmd
tools\test.cmd
tools\verify-live-state.cmd
```

POSIX equivalents are in `tools/*.sh`. Bootstrap creates the ignored repository-local `.venv`; validation never installs dependencies implicitly. Live-state verification reads local refs only and never fetches or switches branches.

On Windows, `tools\bootstrap.cmd` resolves Python in this order: an explicit `QIVEN_PYTHON`, executable candidates returned by `where python`, then a working `py` launcher as an optional fallback. Finding `python` or `py` on PATH is not sufficient: each candidate is executed and version checked for Python 3.11 or newer. For example, `set QIVEN_PYTHON=C:\path with spaces\python.exe` explicitly selects an interpreter; an invalid explicit selection fails without fallback.

This repository is currently **Phase 0**. Genesis historical import has **not** happened yet; it is Batch 002.
