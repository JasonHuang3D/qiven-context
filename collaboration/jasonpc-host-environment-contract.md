# JasonPC Host Environment Contract

## Purpose and scope

This document is the stable execution contract for Qiven and `jason-brother`
operations performed on `JASONPC` through Desktop Commander Remote (DCR). It
defines how automation selects tools and transports work; it is not a request to
keep every observed version forever. The dated inventory in
`evidence/audits/jasonpc-host-inventory-2026-09-15.md` records the mutable facts
observed when this contract was established.

## Shell boundary

- Human copy/paste instructions target 64-bit Windows CMD. Use `call` when a
  `.cmd` file participates in `&&` or `||` gating.
- DCR commands execute in 64-bit PowerShell Core. PowerShell syntax, profiles,
  aliases, and implicit command discovery are not part of the human CMD
  contract.
- Automation must invoke the required executable by its canonical absolute path
  below. Ambient `PATH` may be inspected, but it is not authority where more
  than one candidate exists.
- Commands must set or pass noninteractive controls before an operation that
  could authenticate: `GIT_TERMINAL_PROMPT=0`, `GCM_INTERACTIVE=Never`,
  `GH_PROMPT_DISABLED=1`, and SSH `BatchMode=yes` with zero password prompts.
- A login, credential, password-manager, host-key, consent, elevation, or other
  interactive UI prompt is a failed operation. Automation must stop rather than
  accept or work around it.

## Authoritative executables and discovery rules

| Capability | Canonical selection rule |
| --- | --- |
| Python | `C:\Env\python\3.14.7\python.exe`; repository `.venv` is acceptable only after it is proven to derive from a supported interpreter. `QIVEN_PYTHON`, when deliberately supplied, remains the repository resolver's explicit override. Never use the WindowsApps alias. |
| CMake | `C:\Env\cmake\bin\cmake.exe` |
| Ninja | `C:\Env\ninja\ninja.exe` |
| Visual Studio | Discover with `C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe`; require a complete, launchable VS 2022 instance and do not hard-code edition when discovery can supply the installation path. |
| MSVC and SDK | Enter an x64-host/x64-target environment using the selected instance's `Common7\Tools\VsDevCmd.bat`; record and validate `VCToolsVersion` and `WindowsSDKVersion`. Do not synthesize include/library paths. |
| Git | `C:\Program Files\Git\cmd\git.exe` |
| GitHub CLI | `C:\Env\gh\bin\gh.exe`; the separately installed `C:\Program Files\GitHub CLI\gh.exe` is a non-authoritative duplicate. |
| SSH | `C:\Windows\System32\OpenSSH\ssh.exe` and `ssh-add.exe` |

`C:\Env` is host-owned, read-only input to Qiven automation. Qiven may validate
its expected layout but must not create, repair, update, or delete anything
there. A missing canonical executable is a preflight failure, not permission to
fall back to another copy.

## Git and SSH transport policy

- Qiven GitHub repository remotes used by automation must use SSH, normally
  `git@github.com:<owner>/<repository>.git`. HTTPS Git remotes are rejected for
  automated repository access even if Git Credential Manager or `gh` could make
  them work.
- Use Windows OpenSSH explicitly. The user SSH config routes `github.com` to
  `ssh.github.com:443`, verifies the GitHub host key against
  `C:\Env\ssh\github_known_hosts`, and uses the existing Clash SOCKS endpoint
  through Git for Windows `connect.exe`.
- Strict host-key checking is mandatory. Do not use `accept-new`, disable host
  checking, rewrite `known_hosts`, or alter Clash/proxy settings.
- An SSH agent is not required on the observed host. The configured explicit
  identity file is the expected authentication path; automation must never read,
  print, copy, replace, or generate the key.
- `gh auth status` may be used as a noninteractive health check. Never print or
  persist tokens. Git transport remains SSH regardless of the GitHub CLI's
  keyring authentication.
- Git commands run by a restricted DCR identity may require the command-scoped
  option `-c safe.directory=D:/JasonWork/qiven-context`. Never add a global or
  system `safe.directory` entry as automation machinery.
- Existing Git identity is observational only. Automation must never change
  `user.name` or `user.email` at any scope.

## Fail-closed and mutation boundary

The host preflight is read-only. A missing path, unexpected remote transport,
failed version probe, failed auth check, untrusted host key, unavailable proxy,
or ambiguous canonical selection produces a non-zero result. It must not install
software, mutate `PATH`, edit the registry, change Git/GitHub/SSH credentials or
configuration, start an agent, repair Clash, alter Visual Studio, or write to
`C:\Env`.

For this repository, discovery output and contract updates may be written only
inside the checkout on a task branch. No automatic fetch, pull, push, checkout
of unrelated refs, merge, credential flow, or host repair is part of preflight.

Run the supported check from CMD as:

```cmd
call tools\host-preflight.cmd
```

Use `call tools\host-preflight.cmd --offline` only when network reachability is
intentionally outside the current validation scope. Offline mode still checks
the effective SSH policy and reports that connectivity was skipped; it is not
evidence that GitHub access works.
