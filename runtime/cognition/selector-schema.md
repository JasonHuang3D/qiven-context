# Cognition Activation Selector Schema v1

Status: CA-0 bootstrap (ADR-0050 / roadmap amendment §10: "CA-0 defines the
selector schema before gate enforcement"). Machine-readable records carrying
this metadata are validated by shape at the CA-0 bootstrap transaction; the
repository gate begins REJECTING newly created or materially revised
protected-class canonical records that lack valid selector metadata only
after the separately landed schema/bootstrap gate transaction (roadmap §6.1).

## Purpose

Selector metadata is the typed applicability contract between a canonical
record and the Task Cognition Activator. It is machine-readable, exact, and
deterministic: protected selection (P0/P1) may depend ONLY on these typed
fields, never on free-text matching over record bodies (governance program
CG-3; TCA architecture §7 — v1 selectors are exact/deterministic only).

## Record shape

A canonical record (or its companion manifest entry) carries:

```yaml
activation:
  schema_version: 1          # this schema
  record_id: <string>        # canonical ID (MEM-..., ADR-00NN, OBL-..., TCA-*)
  category: >                # exactly one
    core-governance | collaboration-contract | decision | scar | obligation |
    current-state | policy-instance | engineering-law | convention |
    task-schema | capability-surface | admission-law | architecture-contract |
    design-record | evidence | deliberation-record
  priority_class: P0-core | P1-protected | P2-required | P3-supporting | P4-on-demand
  lifecycle: active | superseded | legacy | retired
  selectors:
    phases:  [specify, design, implementation, review, acceptance]   # or [all]
    risk:    [R0, R1, R2, R3]                                        # or [all]
    repositories: [qiven-context, qiven-devkit, qiven-foundation, qiven-runtime, ...]
    path_prefixes: ['src/ipc/', 'docs/architecture/', ...]           # optional
    languages: [cpp, python, batch, cmake, markdown, yaml]           # optional
    boundary_kinds: >      # zero or more; the protected applicability core
      ownership | lifetime | representation | serialization | ipc | persistence |
      concurrency | platform | external-contract | security | process-custody |
      filesystem | git | cognition | governance | tooling | human-interface
    explicit_ids: [ADR-00NN, OBL-..., MEM-...]                       # optional triggers
  source:
    repository: <name>
    path: <root-relative path>
    anchor: <section/line anchor>       # e.g. '§5.3', 'L188-281'
  expected_controls: [<one-line control statements the rule expects>]
  independent_evidence: [mechanical, environmental, fresh-cognitive, owner-boundary]
```

## Laws

1. **Exact vocabulary.** Every enum value comes from the sets above. An
   unknown value is `unresolved` and FAILS VISIBLY at validation/activation —
   it is never treated as irrelevant (CG-3).
2. **Protected selection is typed-only.** P0/P1 selection evaluates
   `selectors` plus `explicit_ids` plus task facts (normalized
   `TaskDescriptor`: repositories, paths, phase, risk, boundary kinds,
   languages, named IDs). No regex over bodies, no similarity ranking for
   protected classes (CG-3; TCA-ARCH §7).
3. **One canonical owner.** Each rule names exactly one canonical source
   (`repository + path + anchor`). Companion surfaces point to it; they must
   not develop drifting paraphrases (governance program §6.1).
4. **Lifecycle coherence.** `lifecycle: superseded|legacy|retired` records
   can be selected ONLY as history (P4-on-demand); presenting them as current
   is a Profile B failure class.
5. **Selector bootstrap completeness.** The four TCA documents carry
   section-level selector metadata from birth via
   `runtime/cognition-landing-manifest.yaml`. The initial protected
   bootstrap set (scar records) is enumerated in the CA-0 exit report; new
   protected-class records after the enforcement transaction require valid
   `activation` metadata.
6. **Judgment-bearing fields stay empty until derivable.** Fields a fixed
   normalizer cannot derive from mechanical task facts (`boundary_kinds`
   beyond path/language mapping, `explicit_ids` beyond textual task IDs)
   remain empty; curator enrichment earns Profile B credit only, never
   Profile C utility credit (acceptance protocol §7.1).
7. **Mutation detection.** Changing a body without changing the path still
   changes the record content digest and invalidates derivatives bound to it
   (Profile A.3); selector edits change applicability and must revalidate
   fixtures (Profile B mutation classes).
