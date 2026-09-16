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

Current active view:

- `chatgpt-jason.yaml` — ChatGPT + Jason collaboration;
- `environments/jasonpc.yaml` — JasonPC environment profile used by that view;
- `workflows/chatgpt-jason-local-execution.md` — current Workflow 1 / Workflow 2 local-execution model.

Environment profiles intentionally separate durable owner-declared facts from live facts. Exact installed versions, mutable PATH state, VPN connectivity, branch heads, and other operational values must be verified when they matter rather than frozen here as authority.
