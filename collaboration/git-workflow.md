# Git Workflow

- Remote-native branches created directly by jason-brother normally use `jason-brother/<name>`.
- Local-execution branches implemented by jason-worker normally use `jason-worker/<name>`.
- jason-worker commits locally and does not push by default; the user pushes worker branches for remote review.
- jason-brother may create/update remote branches and commits directly for authorized remote-native work when GitHub connector access is available.
- jason-brother reviews the exact remote delta and selects CI scope.
- CI executes deterministic requested validation.
- The user performs the final merge by default unless explicitly authorizing jason-brother to merge.
- Git `user.name` and `user.email` are never changed as workflow machinery.

Repository live state beats a remembered SHA. Exact remote commit review is required before CTO PASS.
