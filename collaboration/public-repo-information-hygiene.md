# Public-Repository Information Hygiene

Normative law (owner direction 2026-09-24, v26 session). Every Qiven
GitHub repository is PUBLIC. Canonical records therefore MUST NOT
serialize machine-identity or recon-valuable literals. This law is a
collaboration contract on par with the file-authoring law; the
workspace hook router does not enforce it mechanically — the contract
is the primary carrier, review enforces it, and the cold-boot sweep
includes this file's vocabulary.

## Why (threat model, honestly stated)

The constitution (§14) has kept credentials, tokens and keys out of the
repositories — a secrets scan at 2026-09-24 HEAD found none. What DID
accumulate is reconnaissance material for TARGETED attacks against the
owner's machine: user-profile paths and the OS username, fixed
workspace/install roots, the VPN client identity and split-routing
policy, an installed-software inventory, and machine schedule
timestamps (sleep/wake/session activity). None of these is an attack by
itself; together they materially help spear-phishing (the repos reveal
the owner's exact workflows and vocabulary), post-exploitation
efficiency (an attacker with code execution learns exactly which files
mediate command execution), and unattended-window targeting. They also
rot: machine literals are dead info for any other environment, which
the BOOTSTRAP itself already forbids relying on.

## The law

1. Canonical records, views, state, and audits MUST NOT contain
   machine-identity literals. Use the placeholder vocabulary below plus
   a live-resolution instruction; the local authorized agent resolves
   them at use time.
2. Placeholder vocabulary (with the live-resolution procedure each):
   - `<workspace-root>` — the long-lived local Qiven workspace. Resolve:
     the parent directory of this repository's local checkout
     (`git rev-parse --show-toplevel` then `..`).
   - `<agent-state-dir>` — the ZCode platform's state directory under
     the user profile (sessions db, exec logs, config). Resolve: the
     platform's standard location; any local ZCode agent knows its own.
   - `<user-profile>` — the Windows user-profile root. Resolve:
     `%USERPROFILE%`. Never serialize its literal (it embeds the OS
     username).
   - `<python-install>` / `<tool-install-root>` — interpreter and
     managed tool installs. Resolve live: `where python` / the
     toolchain manifest / the operator's `{python}` task variable.
   - `<machine-name>` — resolve: `hostname`.
   - `<os-username>` — the Windows account name; resolve live
     (`whoami`). Never serialized (it can be an external identifier).
   - `<local-vpn-proxy>` — the VPN client's local proxy endpoint;
     resolve live from the machine's VPN/git configuration.
3. Not serialized even as examples: the OS username; the VPN client
   identity, routing policy or geo posture; installed-software
   inventories beyond what a task's live verification itself discovers;
   future/recurring schedule information. One-off historical event
   timestamps inside incident evidence are permitted (they are the
   evidence); schedule PATTERNS are not.
4. What stays public and serialized (no redaction): Git SHAs, PR
   numbers, public repository URLs, ADR/decision text, LLM
   provider/model/account attribution required by the commit-attribution
   law, harness task IDs (random UUIDs), and the environment LABEL
   `JasonPC` — a label, not a binding; the GitHub account already
   publishes the owner's name. The sensitive part was never the label;
   it is everything that BINDS the label to a real machine.
5. Evidence and audits: a transparent redaction pass may substitute
   placeholders for identity literals inside quoted material, and MUST
   add a dated redaction note at the document head when it does
   (originals remain in git history). Redaction never changes technical
   findings.
6. Past session checkpoints and git history are not rewritten
   (constitution §4). The history residual was RESOLVED 2026-09-24 by
   the owner's archival decision: full history preserved in the
   private archive repository, public main truncated to a boundary
   commit per `collaboration/repository-history-archival.md`
   (third-party-fork and GitHub PR-ref residuals disclosed there and
   accepted by the owner). Pre-boundary SHA references in records
   resolve against the archive named in the boundary commit.
7. Scope: this law governs every qiven-* repository's non-code records
   and, prospectively, code repositories' machine-absolute paths (a
   separate implementation obligation tracks code-side path hygiene —
   e.g., tools resolving roots relative to their repository rather than
   hard-coding a workspace layout).

## First application (2026-09-24)

Applied to the active surfaces in the same transaction: the environment
profile, view bindings/workflows, active ADR/memory/obligation/state
records, the current session checkpoint, and the affected audits
(with dated redaction notes). Past checkpoints (v6..v25) retain their
literals as history per clause 6.
