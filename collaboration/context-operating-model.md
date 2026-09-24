# Context v2 Operating Model

## Purpose

Qiven Context is project continuity infrastructure. Its first-order requirement is not merely session handoff: project cognition must remain usable after session loss, turn incidents, LLM or provider replacement, agent replacement, representation/transport replacement, and eventual transfer to another authorized human operator.

## Ownership boundaries

Canonical project truth is independent of the identity reading it. Agent capabilities may change retrieval/presentation. Human preferences may change explanation. Mutation authority is governed separately.

`collaboration/` contains normative project contracts only. Session-specific checkpoints and progress narratives belong under `sessions/`. Participant/environment/workflow adaptation belongs under `views/`.

## ContextView model

Qiven separates identity-independent project cognition from participant-specific operating context.

Conceptually:

```cpp
ProjectContext project;

template<CognitiveAgent Agent, HumanOperator Human>
struct ContextView {
    ProjectContext& project;
    HumanProfile human;
    AgentProfile agent;
    std::vector<EnvironmentProfile> environments;
    WorkflowProfile workflow;
    SessionState session;
};
```

The invariant is:

```text
Project truth is identity-independent.
Interaction is capability-dependent.
Authority is governance-dependent.
Environment and workflow are view-dependent.
Session state is ephemeral continuity.
```

A `ContextView<Agent, Human>` may adapt retrieval, presentation, local execution workflow, machine/tool inventory, and other participant-specific operating details. It must not override project architecture, accepted decisions, obligations, governance, or live remote authority.

Durable view material lives under `views/`. Current agent capabilities that can change by model/product/session are resolved live at cold boot rather than frozen as permanent project truth. Environment profiles may contain owner-declared durable facts such as workspace roots or installed tool families, but version-sensitive paths, versions, reachability, VPN state, and similar operational facts must be verified live when they matter.

If no matching view exists, a capable agent must still be able to boot the identity-independent `ProjectContext`; absence of a view is a loss of adaptation, not a loss of project truth.

## Continuity and handoff profiles

Project Continuity defines the semantic reconstruction outcome; the way cognition reaches a fresh consumer is an independent test dimension.

Qiven distinguishes:

- **remote cold boot** — reconstruct directly from exact canonical remote Context plus admitted live evidence;
- **session checkpoint continuity** — use bounded `sessions/` evidence to reduce loss between sessions, without making it canonical truth;
- **Canonical Artifact Handoff** — an independent producer emits one self-describing artifact that crosses an isolation boundary to a fresh consumer; canonical Context cannot be reread to fill artifact gaps before reconstruction is sealed;
- **Human Succession** — a different authorized human can take over without private recollection.

These properties compose but are not interchangeable. A PASS must name the profile actually tested. `collaboration/context-handoff-contract.md` owns artifact-handoff isolation. `collaboration/project-continuity-acceptance.md` owns the reconstruction semantics. `collaboration/human-succession-acceptance.md` owns human replacement.

## Active write surfaces

A material context transaction may write only the surfaces whose semantics actually changed:

- `decisions/` for durable architecture/process/governance choices;
- `memory/` for durable facts, lessons, invariants, risks, constraints, and negative knowledge;
- `obligations/` for unfinished work and resurfacing triggers;
- `projects/` for durable project/domain models;
- `state/` for compact current operational state;
- `views/` for participant-, environment-, and workflow-specific ContextView material that does not belong to identity-independent project truth;
- `sessions/` for bounded current-session continuity evidence;
- `evidence/audits/` for curated durable incident/acceptance/migration evidence;
- `governance/` for current project authority policy.

There is no requirement to touch every surface in every transaction.

## Material transaction triggers

Create a context transaction when at least one of the following occurs:

1. a durable architecture, process, governance, continuity or handoff decision changes;
2. engineering knowledge is accepted, rejected, corrected, or superseded and is worth future reuse;
3. an obligation is created, changed, closed, cancelled, or superseded;
4. the active objective, accepted checkpoint, candidate, blocker, or pause changes materially;
5. a material incident occurs;
6. execution exits to asynchronous work whose identity must survive the turn;
7. the active task/domain/repository changes materially and continuity state must follow it;
8. a session rolls over or closes;
9. an active ContextView changes materially enough that a future agent/human would otherwise reconstruct the collaboration incorrectly.

Ordinary conversational turns do not require context commits.

## Transaction order

Use one coherent transaction:

1. verify live evidence;
2. classify durable cognition;
3. reconcile conflicts and lifecycle transitions;
4. update ADR/memory/obligation/audit/view records as needed;
5. update compact current operational state;
6. update this session's checkpoint;
7. validate repository invariants and affected derived tooling;
8. create one durable Git commit for the coherent transaction.

Do not maintain a parallel manual event log for the same semantics.

## Canonicalization

Conflict is a temporary epistemic state, not a permanent storage strategy.

When two active records conflict and evidence permits resolution:

- establish one current canonical interpretation for the relevant scope/time;
- mark displaced records with the appropriate lifecycle state;
- maintain reciprocal supersession/provenance where the record model supports it;
- keep historical bodies intact unless a factual correction itself must be recorded;
- remove legacy/superseded material from default current retrieval;
- preserve unresolved conflicts only when evidence is genuinely insufficient, and then represent them explicitly as open/blocking cognition.

Legacy means a mechanism or record surface is retained for history but no longer participates as an active write model. Superseded means the record was once valid but has an explicit successor. Archived/retired material remains historical and non-current.

## Sessions

Each session owns its own checkpoint: `sessions/YYYY-MM-DD-qiven-vN.md`.

A checkpoint contains only enough volatile continuity to bound loss after a chat/session incident: session identity; exact current task; accepted refs/evidence; unaccepted candidate refs; pending asynchronous work; known inconsistencies/evidence gaps; and exact next valid action.

It is not a transcript, a backup, or a Canonical Artifact Handoff. Durable cognition must be promoted to canonical surfaces before it can be relied on across sessions. Historical missing session records are not reconstructed from imagination.

## Legacy surfaces

All legacy surfaces are consolidated in the `legacy/` museum (ADR-0040/
ADR-0041/ADR-0042): sealed kernel/retrieval tooling as non-executable
Markdown (`legacy/tools/`), archived ADRs (`decisions/legacy/`), the
frozen v2 event ledger (`legacy/ledger/events/`), the deprecated
evidence placeholder buckets (`legacy/evidence/{ci,handoffs,research}/`),
historical Chat handoffs (`legacy/sessions/`), retired retrieval
benchmarks (`legacy/benchmarks/`), and former generated-output
conventions (`legacy/generated/`). Museum content is historical
evidence only: no new manual events or records may be written there,
and sealed executables must not be revived. `.generated-temp/` is the
only permitted generated-artifact location in the repository tree.

Existing derived tools may read frozen legacy data only for backward-compatible historical interpretation. No new canonical state may depend exclusively on a legacy surface.

## Remote authority

For current qiven-context truth, GitHub remote is authoritative and local clones are non-authoritative working copies. `state/repositories.yaml` is stable inventory only; it must not cache live branch heads, CI state, or observation timestamps.

A restored or handed-off artifact remains non-authoritative unless a separately governed authority cutover says otherwise. Integrity, continuity and authority are separate properties.

## Validation

Repository validation must enforce record schemas and operating invariants, including legacy write bans, collaboration/session separation, repository-inventory purity, active-session continuity, canonical lifecycle coherence, governance presence, ContextView reference integrity, and the existence/reference integrity of Project Continuity, Canonical Artifact Handoff and Human Succession contracts.

The routine highest-level semantic outcome is Project Continuity, but each execution must name its delivery profile. Remote cold boot is the ordinary operational profile. K4 specifically requires Canonical Artifact Handoff. Human Succession is the separate stronger benchmark for replacement of the authorized human operator and runs only when that property is intentionally being proved.
