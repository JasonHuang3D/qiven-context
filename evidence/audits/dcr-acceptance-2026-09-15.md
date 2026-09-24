# Desktop Commander Remote Acceptance — 2026-09-15

> **Redaction 2026-09-24** — public-repo information hygiene
> (`collaboration/public-repo-information-hygiene.md`): machine-identity
> literals (OS username, user-profile/install roots, VPN client name)
> are replaced with placeholders; originals remain in git history.
> Technical findings are unchanged.

## Result

DCR acceptance PASS on JasonPC. The accepted role is a bounded execution transport that can replace the project owner's repetitive CMD relay step while preserving Qiven authority and fail-closed semantics. The final DCR instance was gracefully stopped after acceptance and its tracked process tree was verified exited.

## Root cause

Desktop Commander Remote 0.2.50 launches its local MCP server with the MCP SDK Windows safe-environment whitelist. That environment included `USERPROFILE` but omitted `ProgramData`.

On JasonPC, Windows OpenSSH 9.5 exits `255` before normal config/network/key processing when `ProgramData` is absent. Controlled environment probes isolated the dependency: baseline and unrelated-variable variants remained `255`, while restoring `ProgramData=C:\ProgramData` changed the OpenSSH probe to success. The earlier DCR Git/SSH failure was therefore an execution-environment propagation bug, not a GitHub, VPN-client, key, ACL, host-key, user, or session failure.

The accepted repair is process-local only:

```text
ProgramData=C:\ProgramData
```

No persistent host/security configuration was changed.

## Execution boundaries proven

Three identities must remain distinct:

1. Work/Codex local runner may execute as restricted `JASONPC\codexsandboxoffline`; approved unsandboxed operations run as `JASONPC\<os-username>`.
2. Self-started DCR server process tree ran as `JASONPC\<os-username>` in active console session `1`.
3. DCR-launched acceptance children also ran as `JASONPC\<os-username>` in session `1`, with `USERPROFILE=<user-profile>`.

The DCR server and its children therefore used the owner's real interactive token/session rather than the restricted Codex sandbox token.

## Canonical DCR Git/SSH process contract

Before a DCR-launched Git/SSH operation, establish:

```text
ProgramData=C:\ProgramData
GIT_TERMINAL_PROMPT=0
GCM_INTERACTIVE=Never
GIT_SSH_COMMAND="C:/Windows/System32/OpenSSH/ssh.exe" -F "<user-profile>/.ssh/config" -o BatchMode=yes -o NumberOfPasswordPrompts=0 -o KbdInteractiveAuthentication=no -o PasswordAuthentication=no
```

Use deterministic paths:

- Git: `C:\Program Files\Git\cmd\git.exe`
- SSH: `C:\Windows\System32\OpenSSH\ssh.exe`
- SSH config: `<user-profile>\.ssh\config`
- Python: `<python-install>\python.exe`
- CMake: `<tool-install-root>\cmake\bin\cmake.exe`
- Ninja: `C:\Env\ninja\ninja.exe`
- MSVC environment: `C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat` with x64 host/target

Do not use bare `py` as an authority until its launcher discrepancy is separately resolved.

## Acceptance evidence

DCR effective SSH config resolved GitHub as `ssh.github.com:443`, strict host-key checking, the pinned known-hosts file, the explicit identity file, and Git for Windows `connect.exe -S <local-vpn-proxy>` as the VPN SOCKS ProxyCommand.

Fresh-process `git ls-remote git@github.com:JasonHuang3D/qiven-context.git` passed repeatedly with truthful exit `0`, including after a complete DCR restart. The observed `main` ref was `797d9834c7d88283f7d51353b1d79ea43c7a1b99`.

Through DCR, the selected Git, Python 3.14.7, CMake 4.4.3, Ninja 1.13.2, MSVC 19.44.35228 / VC tools 14.44.35207, and Windows SDK 10.0.26100.0 were successfully invoked.

A bounded qiven-context workflow also passed through DCR: remote ref fetch, exact-head assertion, repository validation, and truthful `DCR_ACCEPTANCE_PASS`. A separate head comparison correctly detected that the local `main` checkout lagged remote `main` and stopped rather than mutating it.

## Lifecycle acceptance

Work can self-start DCR in the active owner session with:

```cmd
npx @wonderwhy-er/desktop-commander@latest remote
```

No owner password, service, scheduled task, startup persistence, or persistent elevation is required. The exact DCR process tree can be tracked and gracefully stopped; acceptance included start, pass, graceful stop with all tracked PIDs exited, restart, fresh Git PASS, and another graceful stop.

## Fail-closed properties

Git terminal prompts and Git Credential Manager interaction are disabled. SSH batch mode disables password and keyboard-interactive prompts. Host-key checking remains strict. No SSH key, credential, Git identity, firewall, registry, proxy, or security ACL was weakened.

## Remaining limitations

- `ProgramData` restoration is currently a caller-side execution contract rather than an upstream Desktop Commander/MCP SDK fix.
- A caller that omits `ProgramData=C:\ProgramData` can still reproduce the OpenSSH failure.
- The `py` launcher discrepancy remains unresolved; use the explicit Python path.
- Restart across Windows logoff/reboot was not part of this acceptance.

An upstream fix should add `ProgramData` to the Windows safe-environment propagation used by Desktop Commander/MCP SDK.