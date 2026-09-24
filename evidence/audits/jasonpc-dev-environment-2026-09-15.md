# JasonPC Development Environment Baseline — 2026-09-15

> **Redaction 2026-09-24** — public-repo information hygiene
> (`collaboration/public-repo-information-hygiene.md`): machine-identity
> literals (OS username, user-profile/workspace/install roots, VPN
> identity and local proxy details) are replaced with placeholders;
> originals remain in git history. Version observations are historical
> (2026-09-15), not a live inventory. Technical findings are unchanged.

## Purpose

This is dated execution evidence for the JasonPC development environment used by Qiven. It records what was observed on 2026-09-15; it does **not** freeze these versions as permanent project invariants. Toolchain upgrades remain allowed. When exact local validation depends on the host state, re-run a read-only inventory and record material changes rather than assuming this snapshot is still current.

## Provenance

- Human-facing shell: Windows CMD on JasonPC, observed by the project owner.
- DCR transport: Desktop Commander Remote device `JasonPC`, app version `0.2.50`, confirmed online and responsive by a live ping during the Qiven-v4 session.
- DCR execution probes were read-only. No software, environment variable, Git configuration, credential, Visual Studio component, SDK, PATH entry, or repository file on JasonPC was changed.
- The first two MSVC probe wrappers stopped because the probe commands treated normal MSVC stderr/version behavior as failure. No host repair was attempted. A final CMD-only probe validated the selected MSVC/SDK environment without invoking a compile.

## Platform

- Windows: `Microsoft Windows [Version 10.0.26200.9457]`
- Development root observed: `<workspace-root>`
- Existing repositories: `qiven-context`, `qiven-devkit`, `qiven-foundation`, `qiven-math`, `qiven-toolchain-win`

## Core tools observed through DCR

| Capability | Observed resolution / version |
| --- | --- |
| Git | `C:\Program Files\Git\cmd\git.exe`; `2.55.0.windows.5` |
| GitHub CLI | PATH exposes both `C:\Program Files\GitHub CLI\gh.exe` and `<tool-install-root>\gh\bin\gh.exe`; invoked `gh` reported `2.100.0`; `gh auth status` succeeded for `JasonHuang3D`, Git protocol `ssh` |
| CMake | `<tool-install-root>\cmake\bin\cmake.exe`; `4.4.3` |
| Python command | `<python-install>\python.exe` before the WindowsApps alias; `Python 3.14.7` |
| Python launcher | `C:\Windows\py.exe`; DCR process reported `Python 3.9.6` |
| Ninja | `<tool-install-root>\ninja\ninja.exe`; `1.13.2` |
| Node | `C:\Program Files\nodejs\node.exe`; `v22.11.0` |
| npm / npx | `C:\Program Files\nodejs\npm.cmd` / `npx.cmd`; `10.9.0` |

No credential/token value is recorded here. The live GitHub CLI probe only established that noninteractive authentication was healthy.

## Visual Studio, MSVC, and Windows SDK

The read-only probes selected:

- Visual Studio 2022 Community: `C:\Program Files\Microsoft Visual Studio\2022\Community`
- Visual Studio installation version: `17.14.37628.2`
- `VCToolsVersion=14.44.35207`
- x64 compiler: `C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe`
- compiler banner observed: Microsoft C/C++ `19.44.35228` for x64
- `WindowsSDKVersion=10.0.26100.0\`

Selection was validated by entering the x64 host/x64 target environment through `VsDevCmd.bat`; the probe did not modify Visual Studio or the SDK.

## Human CMD versus DCR environment difference

The project owner independently showed the normal foreground CMD environment resolving:

- `where python` -> `<python-install>\python.exe`, then the WindowsApps alias
- `python --version` -> `Python 3.14.7`
- `where py` -> `C:\Windows\py.exe`
- `py --version` -> `Python 3.14.7`

During the DCR probe, `python` resolved the same way and also reported `3.14.7`, but the same `C:\Windows\py.exe` launcher reported `3.9.6`.

This discrepancy is execution evidence that a DCR process must not be assumed to have identical launcher/environment semantics to the user's foreground CMD. Qiven validation should prefer an explicit known executable or a repository-owned resolver whose selection is itself validated. In particular, do not use the bare `py` launcher as an authority merely because it exists.

## DCR Git/SSH parity gap

The project owner's foreground CMD successfully fetched `jason-brother/jasonpc-dev-environment-baseline` from the repository's SSH origin. A DCR-launched CMD against the same checkout failed both `git fetch` and a later `git ls-remote` attempt with Git's generic `Could not read from remote repository` error.

Read-only DCR probes established that:

- the DCR command process identifies as `JASONPC\<os-username>` with `USERPROFILE=<user-profile>`;
- the checkout origin is `git@github.com:JasonHuang3D/qiven-context.git`;
- global Git config exposes `http.proxy=<local-vpn-proxy>`, but the SSH remote does not rely on that HTTP setting;
- `<user-profile>\.ssh\config` routes GitHub SSH to `ssh.github.com:443` through Git for Windows `connect.exe -S <local-vpn-proxy>`, with strict host-key checking and an explicit identity file;
- global Git config explicitly selects `C:/Windows/System32/OpenSSH/ssh.exe` through `core.sshCommand`.

These observations rule out the simplest explanation that DCR merely resolved a different SSH executable. They do **not** establish the root cause of the DCR-only remote-access failure. Several diagnostic command wrappers used during the probe also demonstrated Windows CMD quoting / `%ERRORLEVEL%` capture pitfalls; their printed exit-code values are not accepted as SSH-authentication evidence.

The accepted evidence is therefore limited to a capability gap: Human CMD Git/SSH remote access is currently proven working; DCR-launched Git/SSH remote access is currently proven failing. No proxy, SSH, Git, credential, key, or host configuration was changed in response.

## DCR operating observation

The project owner starts the current DCR transport in a foreground CMD with:

```cmd
npx @wonderwhy-er/desktop-commander@latest remote
```

The CMD remains visibly open while the underlying WebSocket/remote process is alive, and the owner can observe MCP calls and returned output there. Closing that foreground process makes JasonPC unavailable to the DCR transport.

For the initial Qiven-v4 dogfood, DCR is intentionally used only as a bounded substitute for the CMD chains that the owner previously copied and pasted manually. It is not authorized to become an autonomous local engineering agent. Unexpected failure, interactive requirements, device loss, or ambiguous output stops the DCR path and falls back to the established human-copy/paste CMD workflow.
