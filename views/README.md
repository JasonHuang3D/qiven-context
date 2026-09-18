# Context Views

`views/` contains participant-specific projections of Qiven Context. A ContextView adapts identity-independent project cognition to a concrete human/agent/environment/workflow combination without changing project truth.

Conceptually:

```cpp
ProjectContext project;
ContextView<Agent, Human> view(project, human, agent, environments, workflow, session);
```

A view may define:

- human/operator collaboration preferences and interaction rules;
- agent-family/runtime capability assumptions that must be verified live when version-sensitive;
- machine/environment profiles such as workspace roots, tool families, and network policy;
- workflow profiles such as Human Manual Mode and Host-mediated local execution.

A view may **not** override accepted architecture, decisions, obligations, governance authority, or live remote repository truth. If a different human, agent, or machine participates, select or create the appropriate view; do not reinterpret the project to fit the old view.

Current active views:

- `chatgpt-jason.yaml` — ChatGPT + Jason collaboration;
- `zcode-jason.yaml` — ZCode (GLM) + Jason collaboration;
- `environments/jasonpc.yaml` — JasonPC environment profile shared by both views;
- `workflows/chatgpt-jason-local-execution.md` — `cloud_terminal`/`cloud_desktop_hybrid` instantiation (Workflow 1 / Workflow 2);
- `workflows/local-supervised-agent.md` — `local_supervised_agent` instantiation for desktop-resident agents;
- `humans/jason.yaml` — Jason's interaction preferences (shared, preference-only).

Environment profiles intentionally separate durable owner-declared facts from live facts. Exact installed versions, mutable PATH state, VPN connectivity, branch heads, and other operational values must be verified when they matter rather than frozen here as authority.

## Two-layer model and view dimensions

Canonical context is LLM-, tool-, and human-independent. A view adds exactly
three adaptation dimensions over that canonical truth (ADR-0035):

1. **Role bindings** — which model instance currently fulfills each canonical
   role (`jason-brother`, `jason-worker`), declared as
   `<role>-<family><version>[-<variant>]` with provider, reasoning tier, and an
   evidence-based `qualification` state (`untested | provisional | qualified`).
   Model resolution is `verify_live`; serving-model substitution must be
   disclosed, never silent.
2. **Client tool** — the concrete client (`chatgpt-web`,
   `chatgpt-desktop-codex`, `zcode-desktop`, `claudecode`, ...) classified into
   a stable capability class (`cloud_terminal`, `cloud_desktop_hybrid`,
   `local_supervised_agent`, `host_mediated_agent`). Workflow profiles bind to
   capability classes, not tool names.
3. **Human preferences** — `humans/<id>.yaml` interaction preferences only;
   they never alter acceptance topology, typed handoffs, authority, or
   governance (`collaboration/human-handoff-boundary.md`).

A view may not redefine roles, re-scope authorities, waive handoffs, or
override live remote state.
