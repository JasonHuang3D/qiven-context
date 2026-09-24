# Audit: 2026-09-24 MVP-4 H1 kit pre-flight failure (kit `0.1.0-g6ebf6ff6`)

> **Redaction 2026-09-24** — public-repo information hygiene
> (`collaboration/public-repo-information-hygiene.md`): machine-identity
> literals are replaced with placeholders; originals remain in git
> history. Technical findings are unchanged.

Class: incident evidence (durable). Recorded 2026-09-24 by the v26
session (designation `jason-extended-cognition`, long-running mode with
standing-delegated per-batch H2). This is the sealed incident record the
qiven-docs PR #2 deliberation (accepted) referenced as the provenance
requirement for its §1.6 entrypoint-hazard evidence. The mvp4 fix itself
is owner-deferred ("mvp4不着急修复，只记录", 2026-09-24).

## Incident report (owner-observed)

The owner followed the kit GUIDE.md step 1 (copy the kit's `config.json`
over `<workspace-root>\.zcode\config.json`, without approving it in the ZCode
UI), then ran step 1.5 (`preflight.cmd` double-click, 2026-09-24
~10:12Z / 18:12 local). Pasted output (verbatim):

~~~text
[ RUN] MVP-4 H1 pre-flight self-check (enable-gated)
[ RUN] preflight: host boot + real-pipe round trip
[FAIL] host reachable BEFORE boot (existing host) -- exit 2: [qiven-hook] deny 120 (hook-client; no host verdict): no RuntimeHost listener on the installation pipe (pipe connect failed (os error 2)) -- fail-closed deny (nothing is governed while the host cannot be reached)
[FAIL] host exited during boot (exit 1); log: <workspace-root>\h1-kits\qiven-runtime\mvp4-h1\0.1.0-g6ebf6ff6\preflight-host.log
[FAIL] no verdict round trip within 20 s; last hook output: [qiven-hook] deny 120 (hook-client; no host verdict): no RuntimeHost listener on the installation pipe (pipe connect failed (os error 2)) -- fail-closed deny (nothing is governed while the host cannot be reached)
[FAIL] PREFLIGHT FAILED - do NOT approve the config; paste this window to the session
~~~

The owner then restored `<workspace-root>\.zcode\config.json` to a minimal
safe configuration by hand (router hook present with `enabled: false`;
neither the kit's trial config nor the pre-h1 backup shape).

## Evidence and root cause

- `preflight-host.log` (kit dir, mtime 2026-09-24 18:12 local):
  `qiven-runtime-host boot` resolved root
  `<workspace-root>\qiven-context`, profile
  `<workspace-root>\h1-kits\qiven-runtime\mvp4-h1\0.1.0-g6ebf6ff6\config\profiles\zcode-jason-context-record-mvp.yaml`,
  state `<workspace-root>\qiven-context\.qiven\runtime`, then
  `[FAIL] boot: host is not running: profile: <that path>` and exit 1.
- The kit has NO `config/` directory at all; its `manifest.json` never
  listed any profile file (verified against the on-disk kit and every
  sibling kit `ge0614b82`..`g6ebf6ff6`).
- Mechanism (verified against qiven-runtime main during the PR #2
  deliberation): `apps/runtime_host_main.cpp` computes the default
  profile from `std::filesystem::current_path()/config/profiles/...`
  BEFORE the argument loop, so `--root` re-points the governed root
  without re-pointing the profile; `tools/h1_kit.py` `cmd_preflight`
  launches the host with `--root` only (no `cwd`, no `--profile`),
  inheriting the caller's working directory; the generated
  `run-host.cmd` DOES `cd /d` into the runtime checkout (so GUIDE step
  2 would have resolved a profile), but `preflight.cmd` does not.
- Double-clicking `preflight.cmd` from Explorer sets the working
  directory to the kit folder -> profile resolves inside the kit ->
  file absent -> `RuntimeHost::boot` reaches the running-state check
  with `failure_detail = "profile: <path>"` (src/host/runtime_host.cpp
  `load_profile_file` failure) -> exit 1.
- The first `[FAIL] host reachable BEFORE boot (existing host)` line is
  the expected cold path printed with misleading `[FAIL]` severity
  (`verdict_round_trip` returns false and the code proceeds to boot);
  the third `[FAIL]` is downstream of the dead host.

## Why the v23 verification passed anyway

The v23 session verified the kit by running
`python tools/h1_kit.py preflight --kit ...` from the qiven-runtime
checkout, where the working directory contains
`config/profiles/zcode-jason-context-record-mvp.yaml`. The PASS evidence
was therefore valid only for the session-side invocation environment;
the owner-live double-click environment (working directory = kit folder,
package without `config/profiles/`) was never exercised.

## Classification

- Jurisdiction: ADR-0049 (H1-kit self-containment; tool-built packages
  complete for the owner-live path) + the MVP-4 corrective lane. It is
  NOT a workspace dependency-resolution defect (PR #2 §1.6
  reclassification, accepted): the profile is runtime configuration,
  not a cross-repository edge.
- Lesson recorded: MEM-20260924T113000Z-C7D8E9 (verification evidence is
  environment-scoped; owner-live entrypoint assumptions - working
  directory, package layout - must be part of the kit's own pre-flight).
- The runtime-side CWD-relative default profile and the pre-flight's
  `[FAIL]`-labeled expected cold path remain open defects in the mvp4
  corrective lane, owner-deferred.

## State after the incident

- Workspace hook config: owner-restored minimal safe config (router
  disabled). The ADR-0051 mechanical teacher is therefore currently
  inactive at the workspace layer; re-enabling is an owner decision.
- The governed checkout was never touched by the trial (no config
  approval happened); the journal at `.qiven/runtime/journal.sqlite3`
  carries the boot attempt only.
- MVP-4 remains NOT ACCEPTED; the real H1 rerun kit needs a rebuild or
  wrapper fix in its corrective lane before the next owner attempt.
