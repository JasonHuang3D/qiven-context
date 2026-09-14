from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys


PYTHON = Path(r"C:\Env\python\3.14.7\python.exe")
CMAKE = Path(r"C:\Env\cmake\bin\cmake.exe")
NINJA = Path(r"C:\Env\ninja\ninja.exe")
VSWHERE = Path(r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe")
GIT = Path(r"C:\Program Files\Git\cmd\git.exe")
GH = Path(r"C:\Env\gh\bin\gh.exe")
SSH = Path(r"C:\Windows\System32\OpenSSH\ssh.exe")
KNOWN_HOSTS = Path(r"C:\Env\ssh\github_known_hosts")
REPO = Path(__file__).resolve().parents[1]


def environment() -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "GIT_TERMINAL_PROMPT": "0",
            "GCM_INTERACTIVE": "Never",
            "GH_PROMPT_DISABLED": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )
    return env


def run(argv: list[str], timeout: int = 20) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=REPO,
        env=environment(),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=timeout,
    )


class Report:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def ok(self, label: str, detail: str = "") -> None:
        suffix = f": {detail}" if detail else ""
        print(f"[ OK ] {label}{suffix}")

    def fail(self, label: str, detail: str) -> None:
        self.failures.append(label)
        print(f"[FAIL] {label}: {detail}", file=sys.stderr)

    def command(self, label: str, argv: list[str], pattern: str, allowed=(0,)) -> subprocess.CompletedProcess[str] | None:
        try:
            result = run(argv)
        except (OSError, subprocess.TimeoutExpired) as exc:
            self.fail(label, str(exc))
            return None
        combined = (result.stdout + result.stderr).strip()
        match = re.search(pattern, combined, re.IGNORECASE | re.MULTILINE)
        if result.returncode not in allowed or match is None:
            self.fail(label, f"exit={result.returncode}; output={combined[:400]!r}")
        else:
            self.ok(label, match.group(0).strip())
        return result


def effective_ssh(result: subprocess.CompletedProcess[str] | None) -> dict[str, str]:
    values: dict[str, str] = {}
    if result is None:
        return values
    for line in (result.stdout + result.stderr).splitlines():
        key, _, value = line.partition(" ")
        if value:
            values[key.casefold()] = value.strip()
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only JasonPC host contract preflight")
    parser.add_argument("--offline", action="store_true", help="skip live GitHub SSH connectivity")
    args = parser.parse_args()
    report = Report()

    print("JasonPC host preflight (read-only; noninteractive)")
    if os.name != "nt" or platform.machine().casefold() not in {"amd64", "x86_64"}:
        report.fail("Windows x64", f"os={os.name}, machine={platform.machine()}")
    else:
        report.ok("Windows x64", platform.platform())

    for label, path in (
        ("Python", PYTHON), ("CMake", CMAKE), ("Ninja", NINJA),
        ("vswhere", VSWHERE), ("Git", GIT), ("GitHub CLI", GH),
        ("OpenSSH", SSH), ("GitHub known-hosts", KNOWN_HOSTS),
    ):
        if path.is_file():
            report.ok(f"canonical {label}", str(path))
        else:
            report.fail(f"canonical {label}", f"missing {path}")

    if Path(sys.executable).resolve() != PYTHON.resolve():
        report.fail("preflight interpreter", f"expected {PYTHON}, got {sys.executable}")
    else:
        report.ok("preflight interpreter", sys.version.split()[0])

    report.command("CMake version", [str(CMAKE), "--version"], r"cmake version 4\.4\.3")
    report.command("Ninja version", [str(NINJA), "--version"], r"^1\.13\.2$")
    report.command("Git version", [str(GIT), "--version"], r"git version 2\.55\.0\.windows\.5")
    report.command("GitHub CLI version", [str(GH), "--version"], r"gh version 2\.100\.0")

    vs = report.command(
        "Visual Studio discovery",
        [str(VSWHERE), "-latest", "-products", "*", "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "-format", "json", "-utf8"],
        r'"installationVersion"\s*:\s*"17\.14\.37628\.2"',
    )
    if vs and vs.returncode == 0:
        try:
            instance = json.loads(vs.stdout)[0]
            installation = Path(instance["installationPath"])
            toolsets = sorted((installation / "VC" / "Tools" / "MSVC").glob("14.44.35207"))
            if toolsets:
                report.ok("MSVC toolset", str(toolsets[0]))
            else:
                report.fail("MSVC toolset", "14.44.35207 not found under selected instance")
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            report.fail("Visual Studio inventory", str(exc))

    sdk = Path(r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0")
    if sdk.is_dir():
        report.ok("Windows SDK", "10.0.26100.0")
    else:
        report.fail("Windows SDK", f"missing {sdk}")

    remote = report.command(
        "repository SSH remote",
        [str(GIT), "-c", "safe.directory=D:/JasonWork/qiven-context", "-C", str(REPO), "remote", "get-url", "origin"],
        r"^git@github\.com:[^\s]+\.git$",
    )
    del remote

    report.command("GitHub CLI auth", [str(GH), "auth", "status"], r"Logged in to github\.com account JasonHuang3D")
    ssh_config = report.command("effective GitHub SSH config", [str(SSH), "-G", "-o", "BatchMode=yes", "github.com"], r"^hostname ssh\.github\.com$")
    values = effective_ssh(ssh_config)
    expected = {
        "user": "git", "port": "443", "batchmode": "yes",
        "identitiesonly": "yes", "stricthostkeychecking": "true",
        "hostkeyalias": "github.com", "userknownhostsfile": "C:/env/ssh/github_known_hosts",
    }
    for key, wanted in expected.items():
        actual = values.get(key, "")
        if actual.casefold() == wanted.casefold():
            report.ok(f"SSH {key}", actual)
        else:
            report.fail(f"SSH {key}", f"expected {wanted!r}, got {actual!r}")
    proxy = values.get("proxycommand", "")
    if "connect.exe" in proxy.casefold() and "127.0.0.1:7897" in proxy:
        report.ok("SSH proxy command", proxy)
    else:
        report.fail("SSH proxy command", f"unexpected {proxy!r}")

    if args.offline:
        print("[SKIP] GitHub SSH connectivity: --offline requested")
    else:
        report.command(
            "GitHub SSH connectivity",
            [str(SSH), "-T", "-o", "BatchMode=yes", "-o", "NumberOfPasswordPrompts=0", "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=15", "git@github.com"],
            r"successfully authenticated, but GitHub does not provide shell access",
            allowed=(1,),
        )

    if report.failures:
        print(f"[FAIL] host preflight: {len(report.failures)} check(s) failed", file=sys.stderr)
        return 1
    report.ok("host preflight", "all required checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
