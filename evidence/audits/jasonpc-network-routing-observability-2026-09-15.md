# JasonPC Network Routing and Download Observability — 2026-09-15

This note records host-operational feedback from the project owner while validating retrieval/NLI tooling on JasonPC. It is evidence for future tooling and host-contract work; it is not a new retrieval candidate record and does not change accepted architecture by itself.

## Owner-confirmed network fact

JasonPC runs Clash Verge in rule-based routing mode. Outbound Internet clients should send their traffic through the local Clash endpoint at `127.0.0.1:7897`; Clash then applies its own rules to choose direct versus proxied routing. In particular, access to servers outside mainland China must not assume direct connectivity.

Operational implication: future JasonPC commands and tools that perform Internet access should deliberately inherit or set the appropriate proxy environment/transport rather than relying on ambient direct networking. The proxy should be treated as a host execution fact, not hard-coded as a portable Qiven product invariant.

## Download observability feedback

During the 2026-09-15 NLI validation, Hugging Face model acquisition completed, but the command no longer displayed useful transfer progress such as percentage, bytes transferred, transfer rate, or ETA. The runtime also emitted an unauthenticated-HF-Hub warning.

For long-running network/model acquisition, human-facing Qiven tooling should provide liveness/progress feedback when the underlying client can expose it. Silent network waits are undesirable because they are difficult to distinguish from a stalled command.

This is an ergonomics/operability requirement, not a reason to interrupt Retrieval Reliability. Fix it when the next network/bootstrap path is touched rather than creating a separate workstream.
