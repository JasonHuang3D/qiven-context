# Qiven Software Engineering Philosophy

This document defines the default engineering posture for Qiven across repositories, product lines, and execution agents. It is normative for architecture and implementation work unless a more specific accepted decision deliberately overrides it.

## 1. Start from semantic ownership, not local convenience

Before implementing a new capability in repository or layer `A`, determine where the capability naturally belongs in the dependency hierarchy.

If the capability is semantically lower-level than `A`, stable enough to state as a reusable contract, and consistent with the lower layer's mission, improve the lower owner `B` first and make `A` depend on `B`.

A correct downward dependency is a feature, not a defect. Avoiding a dependency is not an architectural goal by itself.

Do not copy a weaker local version into `A` merely to keep `A` temporarily self-contained when the capability already belongs in `B`.

## 2. Consumer count is evidence, not a placement prerequisite

Multiple consumers are useful evidence that an abstraction is shared, but they are not required before placing an abstraction in its correct semantic layer.

A single concrete downstream requirement can expose a genuine hole in Foundation, Runtime, Networking, Math, Geometry, or another lower shared layer. When semantic ownership is already clear, waiting for duplicated implementations in multiple products before fixing the lower layer is unnecessary rework.

The test is not "how many repositories need this today?" The test is "where does this contract naturally belong, and can that owner express it cleanly without absorbing higher-level semantics?"

## 3. Do not simulate a human apprenticeship curve

AI-led development must not deliberately reproduce the historical sequence by which human teams often reach a mature design: quick local implementation, accumulated debt, painful refactor, then extraction.

Qiven should use established engineering knowledge to make the first serious implementation as close to candidate-quality as practical.

Compiler feedback, tests, benchmarks, experiments, and dogfood are used to resolve facts that are genuinely uncertain: platform behavior, performance characteristics, undocumented external contracts, integration behavior, and defects. They are not an excuse to rediscover well-understood ownership, RAII, dependency direction, bounded-resource, concurrency, or failure-model principles through avoidable bad code.

A disposable experiment is appropriate only when the semantic contract is genuinely unknown. Such experiments must be isolated, clearly marked disposable, and must not silently become the product architecture.

## 4. Build the dependency hierarchy deliberately

The broad native dependency direction is:

```text
Operating system / standard library / deliberately selected mature third-party primitives
    -> Qiven Foundation
    -> shared native layers such as Runtime, Networking, Math, Units, Geometry, Scene, Compute
    -> product infrastructure
    -> product/domain semantics
    -> UI and workflow shells
```

Not every product must consume every layer. Dependencies are added only where the semantic relationship is real, but a real downward relationship should not be avoided for cosmetic independence.

When a needed abstraction does not fit an existing lower layer, create or refine the correct lower semantic layer rather than hiding a duplicate in the product. Repository boundaries follow semantic responsibility, not an arbitrary desire to minimize repository count.

## 5. Foundation is small because its semantics are strict, not because it must stay incomplete

Foundation remains low-level, predictable, explicit, low-dependency, and free of product/domain semantics. That constraint remains strong.

However, "keep Foundation small" must not be interpreted as "leave foundational holes in place until several products duplicate them." A primitive may enter Foundation from one concrete downstream requirement when it is intrinsically foundational and satisfies Foundation's ownership, failure, portability/platform-boundary, dependency, and cost laws.

Capabilities that are lower than a product but higher than Foundation should live in an appropriate shared layer such as Runtime or Networking rather than being forced into either Foundation or the product.

## 6. Performance is an architectural property

For low-level and shared native code, performance is part of correctness when the component exists to support long-running, high-throughput, or latency-sensitive systems.

Design must make important costs visible: allocation, copies, buffer growth, syscalls, context switches, synchronization, contention, cache behavior, thread ownership, blocking, wakeups, process lifetime, and network backpressure.

Prefer bounded memory and bounded queues, explicit ownership, amortized or predictable complexity, zero-copy or move semantics where they materially help, and OS/runtime primitives whose cost model is understood.

Do not add abstraction layers that hide material cost merely to make APIs look uniform.

## 7. Prefer mature lower primitives over local reinvention

The same dependency rule applies below Qiven. Qiven may and should use mature operating-system facilities, the C++ standard library, and well-established third-party libraries when they are the correct lower primitive and their dependency/cost/legal properties are acceptable.

Do not hand-roll a lower-quality replacement merely to claim fewer dependencies. Wrap or constrain an external primitive only when Qiven needs a stable semantic boundary, ownership model, safety property, test seam, or replaceability contract.

## 8. Lower-layer improvement is part of the current objective

When product work reveals a missing lower-layer primitive, improving that lower layer is not automatically "scope creep" or an infrastructure detour. It is part of completing the product correctly when the dependency is real.

Scope discipline still applies: add only the lower-layer capability required by the concrete objective and the natural adjacent contract needed to make it coherent. Do not turn one product requirement into speculative framework completion.

The lower-layer change should normally be implemented, reviewed, validated, and fixed to an exact integration baseline before the upper-layer consumer is finalized.

## 9. First implementation quality bar

The first non-disposable implementation should already aim for:

- correct semantic placement;
- explicit ownership and lifetime;
- explicit recoverable failure channels;
- RAII for owned native resources where C++ object lifetime fits the resource;
- bounded memory/resource behavior;
- concurrency contracts stated before synchronization is added;
- platform boundaries isolated deliberately;
- self-contained public headers and deliberate dependency exposure;
- tests that target semantic failure modes rather than implementation trivia;
- performance costs understood at the level appropriate to the component.

"We can refactor later" is not a design argument when the better placement or contract is already known.

## 10. When local implementation is still correct

A capability should remain local to `A` when its semantics are genuinely product-specific, when moving it down would force the lower layer to understand higher-level policy, when the stable abstraction is not yet knowable, or when a bounded experiment is explicitly gathering evidence needed to decide the contract.

The burden is therefore not "prove reuse before depending downward." The burden is "prove the lower layer is the natural semantic owner before moving the capability there."

## 11. AI engineering posture

jason-brother and jason-worker must reason from the broadest established engineering solution space available, not merely from the tools or abstractions already named in the current conversation.

They should actively look for lower-layer ownership, mature primitives, stronger algorithms, better data structures, more suitable OS facilities, and more appropriate repository boundaries before writing product-local code.

Known engineering knowledge should be applied directly. Experiments are for unknown facts. Validation is for proof. Neither should be used as theater to imitate avoidable human trial-and-error.