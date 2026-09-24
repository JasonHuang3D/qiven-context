# Nine-Repository Audit — 2026-09-20 (overnight unattended run)

> **Redaction 2026-09-24** — public-repo information hygiene:
> machine-identity literals replaced with placeholders; originals
> remain in git history. Findings unchanged.

Scope: all nine `qiven-*` repositories under `<workspace-root>`. Checked: working
tree cleanliness, tracked artifacts, branch hygiene, commit attribution,
secrets, README/AGENTS presence, convention compliance, dependency direction.

## Findings

| # | Severity | Finding | Repository | State |
| --- | --- | --- | --- | --- |
| 1 | CRITICAL (contained) | Seven-branch publication swept two UNACCEPTED preserved Host commits onto origin/main. Contained: paused work preserved on `preserved-host-correction`, main rolled back, pointer re-published alone. | qiven-host | contained |
| 2 | high | 18 staged files, no remote, no branch | qiven-dcr-win | committed + pushed as backup, frozen |
| 3 | medium | Not a git repository | qiven-runtime | local repo created as preservation |
| 4 | medium | 15 stale local branches | context/devkit/host | deleted after uniqueness check |
| 5 | low | devkit merge message cited wrong PR number | qiven-devkit | recorded |
| 6 | low | draft naming deviations (PascalCase methods, k-prefix) | draft | V-4: renamed |
| 7 | info | Pre-convention commits lack attribution trailers | all | grandfathered |
| 8 | info | 22 secrets-scan hits are prose in contracts | context | none |

## Root cause of finding 1 (pit P-50)

Publication without computing the delta against the base the H2 named.
Rule: before any publication, `git log base..branch` MUST be reviewed and
match the H2'd delta exactly.
