# Git Workflow

- Feature branches normally use `jason-worker/<name>`.
- Worker commits locally; user pushes.
- jason-brother reviews the exact remote delta and selects CI scope.
- CI executes deterministic requested validation.
- User merges after approval.
- Git `user.name` and `user.email` are never changed as workflow machinery.

Repository live state beats a remembered SHA. Exact remote commit review is required before CTO PASS.
