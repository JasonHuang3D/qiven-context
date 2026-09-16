# Context Checkpoint Protocol

This v2 protocol is a compatibility entry point. The normative transaction model is `collaboration/context-operating-model.md`.

A context checkpoint is created only for a material context transaction; ordinary turns do not require one. There is no mandatory all-category Memory Delta and no manual ledger dual-write.

The checkpoint sequence is: verify live evidence; classify durable cognition; reconcile lifecycle/conflicts; update only affected canonical records and audits; update compact operational state; update the current session checkpoint; validate schemas and v2 repository invariants; validate affected derived tooling; commit the coherent context transaction.

If an asynchronous external job remains nonterminal, persist exact correlation identity and return control rather than keeping the Chat turn alive by polling.

Historical `templates/MEMORY_DELTA.md` is retained only as a legacy capture worksheet; it is not a required transaction artifact.
