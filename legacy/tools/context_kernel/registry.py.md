# [SEALED] tools/context_kernel/registry.py

> Museum piece (ADR-0040/ADR-0041, sealed 2026-09-21). Original
> location: `tools/context_kernel/registry.py`. Do not execute — this is historical text
> only; the `.md` extension makes accidental execution impossible.

````python
# Registered source schema v1 is pinned by content, not by a caller-supplied schema.
# A changed definition requires a reviewed registry version/migration.
REGISTRY = {
    'adr': ('decisions', 'adr', '3106fe4fb13f0c2743e3ba2d0ce91bf4665393851cb168d6215be4da0bcc5421'),
    'memory': ('memory/records', 'memory-record', '12d2aa2a57bf529f092835dd2d8a5b25029284161a4ffb6effabe709d57f3503'),
    'obligation': ('obligations', 'obligation', '48ca961a592f9bae4ab21b209b2939b9da34d3352b331850aeb3ed9f1914bab8'),
}

````
