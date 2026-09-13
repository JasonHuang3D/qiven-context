# Git Workflow

- Remote-native branches created directly by jason-brother normally use `jason-brother/<name>`.
- Local-execution branches implemented by jason-worker normally use `jason-worker/<name>`.
- jason-worker commits locally and does not push by default; the user pushes worker branches for remote review.
- jason-brother may create/update remote branches and commits directly for authorized remote-native work when GitHub connector access is available.
- jason-brother reviews the exact remote delta and selects CI scope.
- CI executes deterministic requested validation.
- For each batch, the user runs the required machine-local validation and reports PASS/FAIL.
- After a PASS, jason-brother may merge the exact validated batch head to `main` under ADR-0021 after exact remote review and any additional required gates pass.
- If any commit is added after the validated head, that changed head requires validation again before merge.
- Prefer a normal no-fast-forward merge when preserving the batch boundary is useful. Never force-push or bypass required validation as merge machinery.
- Git `user.name` and `user.email` are never changed as workflow machinery.

Repository live state beats a remembered SHA. Exact remote commit review is required before CTO PASS and before an authorized remote merge.
