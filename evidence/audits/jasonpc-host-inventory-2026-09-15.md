# JasonPC Host Inventory — 2026-09-15

## Provenance

- Observed locally on `JASONPC` through DCR at
  `2026-09-14T20:02:59.0632653Z` (`2026-09-15T04:02:59.0574855+08:00`).
- Repository: `D:\JasonWork\qiven-context`.
- DCR probe identity: `JASONPC\61626` for approved host probes; the restricted
  command sandbox separately identifies as `JASONPC\CodexSandboxOffline`.
- All probes were read-only. No software, system setting, environment variable,
  credential, SSH key, Git configuration, Visual Studio component, Clash
  setting, or `C:\Env` content was changed.
- Secrets were not captured. GitHub CLI reported only a masked token.

## Observed platform and shells

| Item | Observation |
| --- | --- |
| OS | Microsoft Windows 11 Pro, version `10.0.26200`, build `26200` |
| Architecture | 64-bit OS, `AMD64` process architecture |
| Host name | `JASONPC` |
| Human convention | 64-bit CMD via `C:\Windows\System32\cmd.exe`; repository operating rules use CMD syntax and `call` for batch gates |
| DCR shell | PowerShell Core `7.6.5`, 64-bit, working directory `D:\JasonWork\qiven-context` |
| DCR environment | Inherits the user and machine PATH, then adds Codex runtime paths before and after host entries; therefore resolution must not be assumed to match a minimal human CMD environment |

The sandbox identity triggered Git's dubious-ownership protection because the
checkout belongs to `JASONPC\61626`. The discovery session used only a
command-scoped `safe.directory` override; no Git configuration was changed.

## `C:\Env` layout relevant to Qiven

| Path | Observed role |
| --- | --- |
| `C:\Env\python\3.14.7` | Authoritative Python installation |
| `C:\Env\cmake\bin` | Authoritative CMake installation |
| `C:\Env\ninja\ninja.exe` | Authoritative Ninja executable |
| `C:\Env\gh\bin\gh.exe` | Canonical GitHub CLI selected by this contract |
| `C:\Env\ssh\github_known_hosts` | Pinned GitHub SSH host keys used with strict checking |
| `C:\Env\zlib\1.3.2` | Host zlib tree; observed but not selected by this contract |

## Tools and resolved paths

| Tool | Canonical/selected path | Observed version | PATH ambiguity |
| --- | --- | --- | --- |
| Python | `C:\Env\python\3.14.7\python.exe` | CPython `3.14.7`, 64-bit | `where python.exe` also returns the nonfunctional Microsoft Store alias. `py.exe -0p` also lists Python `3.9` at `C:\Users\61626\AppData\Local\Programs\Python\Python39\python.exe`. |
| Python launcher | `C:\Windows\py.exe` | launcher `3.9.6150.1013`; default runtime `3.14.7` | Launcher inventory contains both 3.9 and 3.14. |
| CMake | `C:\Env\cmake\bin\cmake.exe` | `4.4.3` | No second PATH candidate observed. |
| Ninja | `C:\Env\ninja\ninja.exe` | `1.13.2` | PATH contains the same directory twice with case variation. |
| Visual Studio | discovered by `C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe` | Visual Studio Community 2022 `17.14.40` (`17.14.37628.2`) | `vswhere.exe` is not on PATH; its canonical installer path must be used. |
| MSVC | `C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe` | toolset `14.44.35207`; compiler `19.44.35228` | Resolve through `vswhere` plus `VsDevCmd.bat`, not raw PATH. |
| Windows SDK | selected by `VsDevCmd.bat` | `10.0.26100.0` | Installed SDK bin versions also include 14393, 15063, 16299, 17134, 19041, and 22621; newest directory alone is not the selection contract. |
| Git | `C:\Program Files\Git\cmd\git.exe` | `2.55.0.windows.5` | DCR PATH also exposes Codex runtime Git `2.53.0.windows.3`. |
| GitHub CLI | `C:\Env\gh\bin\gh.exe` | `2.100.0` | PATH resolves `C:\Program Files\GitHub CLI\gh.exe` first; both observed copies report 2.100.0. |
| OpenSSH | `C:\Windows\System32\OpenSSH\ssh.exe` | OpenSSH for Windows `9.5p2`, LibreSSL `3.8.2` | No second PATH candidate observed. |

## Git, GitHub CLI, and SSH

- Repository fetch and push remotes are both
  `git@github.com:JasonHuang3D/qiven-context.git`.
- Git configuration affecting auth/transport:
  - system `credential.helper=manager`;
  - system `credential.https://dev.azure.com.usehttppath=true`;
  - global `credential.helper=manager-core`;
  - global `http.proxy=http://127.0.0.1:7897`;
  - no observed `core.sshCommand`, `ssh.variant`, URL rewrite, or scoped HTTPS
    proxy override;
  - global Git identity exists but was only observed and must never be changed by
    automation.
- `gh auth status` succeeded noninteractively for active account
  `JasonHuang3D`; Git operations protocol is `ssh`; scopes reported were
  `gist`, `read:org`, and `repo`. The credential source is the Windows keyring.
- No usable OpenSSH agent was present: `ssh-add -l` returned exit code `2` with
  `Error connecting to agent: No such file or directory`.
- Effective GitHub SSH settings, with `BatchMode=yes`, are `git@ssh.github.com`
  on port `443`, `IdentitiesOnly=yes`, host-key alias `github.com`, strict host
  checking, identity `~/.ssh/id_ed25519`, known-hosts file
  `C:/env/ssh/github_known_hosts`, 15-second connect timeout, and proxy command
  `C:/Program Files/Git/mingw64/bin/connect.exe -S 127.0.0.1:7897 %h %p`.
- The required Clash fact is limited to the existing SOCKS endpoint at
  `127.0.0.1:7897`. No Clash UI, process, files, or settings were inspected or
  changed.
- `ssh -T` with batch mode, zero password prompts, strict host-key checking, and
  a 15-second timeout reached GitHub and authenticated as `JasonHuang3D`.
  GitHub's expected “does not provide shell access” response returned SSH exit
  code `1`; the authenticated greeting is the success condition.

## Regeneration probes

Run from an already authorized DCR PowerShell session. These probes do not
repair failures. Keep authentication controls in the same process environment:

```powershell
$env:GIT_TERMINAL_PROMPT = '0'
$env:GCM_INTERACTIVE = 'Never'
$env:GH_PROMPT_DISABLED = '1'
Get-CimInstance Win32_OperatingSystem | Select Caption,Version,BuildNumber,OSArchitecture,CSName
$PSVersionTable
$env:ComSpec
Get-ChildItem -Force -LiteralPath C:\Env
Get-Command python,py,cmake,ninja,git,gh,ssh,ssh-add -All
cmd.exe /d /c 'for %T in (python.exe py.exe cmake.exe ninja.exe vswhere.exe git.exe gh.exe ssh.exe ssh-add.exe) do @echo -- %T & @where %T 2>&1'
C:\Env\python\3.14.7\python.exe -c "import platform,sys; print(sys.executable); print(platform.python_version()); print(platform.architecture()[0])"
C:\Windows\py.exe -0p
C:\Env\cmake\bin\cmake.exe --version
C:\Env\ninja\ninja.exe --version
& 'C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe' -all -products * -format json -utf8
cmd.exe /d /c 'call "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat" -no_logo -arch=x64 -host_arch=x64 && set VCToolsVersion && set WindowsSDKVersion && where cl.exe && cl.exe /Bv'
& 'C:\Program Files\Git\cmd\git.exe' --version
& 'C:\Env\gh\bin\gh.exe' --version
& 'C:\Env\gh\bin\gh.exe' auth status
& 'C:\Windows\System32\OpenSSH\ssh.exe' -V
& 'C:\Windows\System32\OpenSSH\ssh-add.exe' -l
& 'C:\Program Files\Git\cmd\git.exe' -c safe.directory=D:/JasonWork/qiven-context -C D:\JasonWork\qiven-context config --show-origin --show-scope --get-regexp '^(credential\.|core\.sshCommand$|ssh\.variant$|url\..*\.insteadOf$|http\..*proxy$|http\.proxy$|https\.proxy$|user\.name$|user\.email$)'
& 'C:\Windows\System32\OpenSSH\ssh.exe' -G -o BatchMode=yes github.com
& 'C:\Windows\System32\OpenSSH\ssh.exe' -T -o BatchMode=yes -o NumberOfPasswordPrompts=0 -o StrictHostKeyChecking=yes -o ConnectTimeout=15 git@github.com
& 'C:\Program Files\Git\cmd\git.exe' -c safe.directory=D:/JasonWork/qiven-context -C D:\JasonWork\qiven-context remote -v
```

For routine drift detection, run `call tools\host-preflight.cmd`; it emits a
concise pass/fail record and performs the same noninteractive GitHub SSH health
check unless `--offline` is explicitly supplied.
