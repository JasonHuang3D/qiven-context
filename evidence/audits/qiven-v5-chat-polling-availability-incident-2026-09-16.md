# Qiven-v5 Chat Polling / Thread Availability Incident — 2026-09-16

## Classification

This is a Qiven orchestration/control-plane incident, not a Host acceptance failure.

## Owner-observed impact

The project owner reported that the Qiven-v5 ChatGPT thread became unable to reload from ChatGPT Web, Windows app, and iOS app while the session was waiting on / polling CI state. The owner also reported contacting OpenAI support; support could not cancel the affected chat thread and suggested deleting the session.

This record does not infer undocumented ChatGPT backend state, locking behavior, scheduler behavior, or a proven upstream root cause. The cross-client thread-unavailability observation and support interaction are treated as owner-reported facts; upstream mechanism remains unknown.

## Repository / CI correlation

The affected Host work was `JasonHuang3D/qiven-host:jason-brother/host-batch-000`.

The live branch later resolved to exact head:

- `8e5b9dec64bf739af84e981df12afc1969599738` — `test(host): bound pipe reuse connect race`

Its exact GitHub Actions run:

- run `35060483714`
- workflow `CI / full`
- head SHA `8e5b9dec64bf739af84e981df12afc1969599738`
- final conclusion `success`
- Windows MSVC x64 Debug/Release PASS
- Linux GCC x64 Debug/Release PASS
- macOS AppleClang arm64 Debug/Release PASS
- CI Gate PASS

The run completed successfully after the Qiven-v5 handoff material had already been written. Therefore the final runner state does not support classifying this specific run as a CI hang. The failure mode relevant to this incident is the Chat-side waiting/orchestration pattern.

## Engineering conclusion

GitHub Actions is asynchronous and must remain asynchronous from the Chat control plane. Qiven Chat turns must not wait indefinitely, sleep/poll until completion, or emulate a synchronous RPC boundary around CI.

CI dispatch may be followed by at most one immediate exact-identity status read. If still queued/in-progress, the current turn returns control with exact run/SHA/status and later verification occurs on a later user turn or through a server-side event/dependency mechanism.

For non-CI repeated external-state observations, a default hard fuse applies unless a stricter operation-specific contract exists: at most three total attempts/observations and at most 60 seconds wall-clock waiting in one turn, whichever comes first. Transient transport/API retries consume the same budget.

This rule is independent of any theory about the ChatGPT upstream implementation. Protecting Qiven's long-lived conversational control plane is itself an engineering requirement.

## Recovery outcome

Qiven-v6 cold boot reconciled the live Host branch and exact CI evidence rather than replaying the prior wait. The transport candidate was recovered intact from GitHub, reviewed, and accepted separately from this incident.
