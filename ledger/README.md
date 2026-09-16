# Legacy cognition ledger

**Status: frozen legacy.**

`ledger/events/2026-09-13.jsonl` and `ledger/events/2026-09-14.jsonl` are preserved as historical v1 evidence. They were never maintained as the sole authoritative write model and stopped being updated while canonical memory/state/ADR work continued.

Context v2 therefore does not backfill the missing dates and does not append new manual ledger events. Git history plus canonical records are the maintained write model.

Derived compatibility tooling may read these two historical files when interpreting old `after` triggers, but no new canonical state may depend exclusively on this legacy ledger.
