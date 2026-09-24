# Context Views

`views/` contains participant-specific projections of Qiven Context. A ContextView adapts identity-independent project cognition to a concrete human/agent/environment/workflow combination without changing project truth.

## Directory layout

```
views/
├── README.md                          # this file
├── humans/                            # Human identity + preferences (shared across views)
│   └── jason.yaml
├── environments/                      # Device environment profiles (shared across views)
│   └── jasonpc.yaml
├── bindings/                          # Session bindings: WHO + WHICH TOOL + WHICH MODEL
│   ├── chatgpt-jason.yaml            # ChatGPT web/desktop + Jason
│   ├── zcode-jason.yaml              # ZCode desktop + Jason
│   └── extended-cognition-jason.yaml # Extended cognition designation + Jason
└── workflows/                         # Execution workflow profiles
    ├── chatgpt-jason-local-execution.md  # ChatGPT cloud/hybrid execution
    ├── supervised-agent.md               # local supervised agent (Z1)
    └── long-running.md                   # long-running development window
```

## The v3 architecture model

The draft (`qiven-context-draft`) clarified the four participants:

| Participant | What it is | Where defined |
|---|---|---|
| **Human** | The person (Jason); preferences, verified principal | `humans/jason.yaml` |
| **LLM** | The model instance; identity, serving disclosure | `bindings/*.yaml` |
| **LLMClientTool** | The relay (zcode-desktop, ChatGPT); NO cognition access | `bindings/*.yaml` |
| **Device** | The machine (JasonPC); environment facts, verify-live | `environments/jasonpc.yaml` |

A **binding** connects a Human + ClientTool (and normally a Model) into a session; owner-invoked designation views bind without a model (2026-09-22). Cognition (the Snapshot) is identity-independent and lives in the canonical repository, never in views.

## Rules

- A view may adapt interaction, environment, and workflow.
- A view may **not** override accepted architecture, decisions, obligations, governance, or live remote truth.
- Model resolution is `verify_live`; serving-model substitution is disclosed, never silent (ADR-0035).
- Role bindings use evidence-based qualification (`untested | provisional | qualified`); upgrade to `qualified` is owner-reserved. Exception: an explicitly owner-invoked designation view may carry no model binding (owner direction 2026-09-22) — the serving LLM reports the live model at designation switch instead.
- If no matching binding exists, fall back to the identity-independent ProjectContext; never invent a participant combination.
