# Repository History Archival and Public Truncation Procedure

Normative procedure (owner direction 2026-09-24, v26 session; first
execution: qiven-context, same day). Purpose: preserve the complete
commit history PRIVATELY while truncating the PUBLIC repository to a
single boundary commit, ending public accumulation of machine-identity
material (companion to `public-repo-information-hygiene.md`). The
procedure is general for every qiven repository, subject to the
code-repo sequencing rule (§7).

## 1. Backup gate (preconditions — all must hold before proceeding)

1. Working tree clean; repository gate PASS at the exact main head;
   the head SHA is recorded.
2. **Branch disposition complete**: every local and remote branch is
   either (a) an ancestor of main → delete freely, or (b) not merged →
   an explicit disposition is RECORDED: merge it, or classify it
   (sealed / superseded / draft) and PRESERVE it in the private
   archive before deletion. Irreversible deletion of unique work
   without a private copy is prohibited (this interprets the owner's
   "merge or decided deletion" rule).
3. Tags dispositioned (archived, then deleted from public).
4. Stashes and open PRs: none, or explicitly dispositioned (an open
   PR blocks its branch's deletion until closed).
5. **Fork survey**: third-party forks are recorded with their
   freshness; the owner accepts their (immutable-to-us) residual
   knowingly.
6. The archive repository name is fixed for the run:
   `<repo>-back-up-M-D-YYYY` (date of the run).

## 2. Archive step (private, full fidelity)

1. Create the private repository under the governance account.
2. Push `main` (full history) plus every preserved §1.2b branch ref
   under its own name, plus all tags.
3. VERIFY: commit count of the archive main equals the local count;
   every pushed ref resolves to the same SHA as local. Only after
   verification may truncation proceed.

## 3. Truncation step (public)

1. Create one orphan commit whose TREE is byte-identical to the main
   head, carrying the boundary message (below).
2. Force-push the orphan to public `main`.
3. Delete every other public branch and every public tag.
4. VERIFY: `git ls-remote` shows exactly `main`; the API branch list
   shows one branch; the default branch is `main`.

## 4. Local step

1. Reset local `main` to the orphan commit (full history remains
   reachable through the archive remote; an optional local
   `archive/pre-boundary-<date>` branch may keep it one hop away).
2. Delete dispositioned local branches; `git fetch --prune`.
3. Keep BOTH remotes: `origin` = public (truncated line),
   the archive remote = private (full history). Never push the
   archive's history to origin.

## 5. Boundary message (orphan commit)

States: this is a history boundary for `<repo>` on `<date>`; the tree
is identical to the archived head `<sha>`; the complete pre-boundary
history lives in the private archive `<archive-repo>`; SHA references
in records dated before the boundary resolve against that archive.

## 6. Residuals (disclosed, never silent)

- **Third-party forks** keep whatever history they forked; we cannot
  remove it. Record fork identity + freshness at gate time.
- **GitHub PR refs / API caches**: commits referenced by (closed) PRs
  can remain fetchable by direct SHA URL until GitHub garbage-collects.
  Full purge requires an owner-initiated GitHub support request
  (sensitive-data removal); optional, owner's call.
- **PR/issue comments** are not git refs; they persist independently
  and are out of this procedure's reach.
- Other machines' clones are owner-managed.

## 7. Code-repo sequencing rule (CRITICAL)

Truncating a repository that other repositories PIN (foundation,
context-draft, third-party-win, devkit) invalidates every consumer's
configure-time pin check (the new orphan root has a different SHA).
Each code repository's truncation batch MUST, in one coordinated
transaction: archive + truncate itself, re-pin every consumer to the
new root, and re-run the consumers' gates. Context (pinned by nobody
at configure time) may be truncated alone — which is why it goes
first. The per-repo wave is tracked as a canonical obligation.

## 8. First execution record (2026-09-24, qiven-context)

Gate: clean tree, gate PASS at `422a2b5`…; 30 remote branches — 20
merged (deleted), 10 sealed-era jason-brother work branches + 1
content-equivalent draft (session-v11, 0 unique patches) preserved in
the private archive then deleted; no tags, stashes, or open PRs.
Fork: one third-party fork (stale, created 2026-09-17) — residual
accepted with knowledge that it contains history only up to that
date. Archive: `JasonHuang3D/qiven-context-back-up-9-24-2026`
(private, verification receipts in the session checkpoint). Public:
truncated to the boundary orphan; single-branch verification done.
