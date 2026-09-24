from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[1]
HEARTBEAT_SECONDS = 5.0
POLL_SECONDS = 0.05
ANSI_GREEN = "\x1b[32m"
ANSI_RED = "\x1b[31m"
ANSI_YELLOW = "\x1b[33m"
ANSI_CYAN = "\x1b[36m"
ANSI_RESET = "\x1b[0m"


@dataclass
class SuiteRun:
    name: str
    script: str
    windows_only: bool = False
    # "repo" suites validate this repository's own canonical contracts;
    # "kernel" suites validate ContextKernel/compiler/retrieval/archive
    # semantics whose production successor is the Runtime program
    # (ADR-0037/ADR-0038; MEM-20260920T195644Z-B7E2F1). The default
    # publication gate runs repo suites only; kernel paths require the
    # context-kernel gate with the full suite set.
    group: str = "kernel"
    process: subprocess.Popen | None = None
    log_path: Path | None = None
    started_at: float = 0.0
    finished_at: float = 0.0
    returncode: int | None = None
    skipped: bool = False
    terminated: bool = False


SUITES = (
    # The Python ContextKernel reference suites (k1-k4, compiler, R1,
    # retrieval, archive, handoff) are SEALED by ADR-0040 (owner direction
    # 2026-09-21): never registered, never run. Their files remain in-tree
    # as sealed reference material.
    # repo group: contract checks for every commit (fast).
    # tools group: validator mutation tests and bootstrap resolution -
    # required only when repository tooling changes (context-tools gate).
    SuiteRun("repo-contract", "tools/test_repo_contract.py", group="repo"),
    SuiteRun("cold-boot-contract", "tools/test_cold_boot_contract.py", group="repo"),
    SuiteRun("validator-unit", "tools/test.py", group="tools"),
    SuiteRun("windows-python-resolution", "tools/test_windows_python.py", windows_only=True, group="tools"),
)


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().casefold() in {"1", "true", "yes", "on"}


def _enable_color() -> bool:
    if _env_flag("QIVEN_TEST_NO_COLOR") or not sys.stdout.isatty():
        return False
    if os.name != "nt":
        return True
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        return bool(kernel32.SetConsoleMode(handle, mode.value | 0x0004))
    except Exception:
        return False


COLOR = _enable_color()


def _paint(text: str, color: str) -> str:
    return f"{color}{text}{ANSI_RESET}" if COLOR else text


def _tag(kind: str) -> str:
    if kind == "ok":
        return _paint("[ OK ]", ANSI_GREEN)
    if kind == "fail":
        return _paint("[FAIL]", ANSI_RED)
    if kind == "wait":
        return _paint("[WAIT]", ANSI_YELLOW)
    if kind == "run":
        return _paint("[ RUN]", ANSI_CYAN)
    return f"[{kind.upper():>4}]"


def _child_environment() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return env


def _enabled_suites() -> list[SuiteRun]:
    result: list[SuiteRun] = []
    for source in SUITES:
        suite = SuiteRun(source.name, source.script, source.windows_only, group=source.group)
        if suite.windows_only and os.name != "nt":
            suite.skipped = True
        result.append(suite)
    return result


def _terminate_children(suites: list[SuiteRun]) -> None:
    alive = [suite for suite in suites if suite.process is not None and suite.process.poll() is None]
    for suite in alive:
        suite.process.terminate()
    deadline = time.monotonic() + 3.0
    for suite in alive:
        remaining = max(0.0, deadline - time.monotonic())
        try:
            suite.process.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            suite.process.kill()
    for suite in alive:
        try:
            suite.process.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            pass


def _status_text(returncode: int) -> str:
    return "PASS" if returncode == 0 else f"FAIL({returncode})"


def _heartbeat(active: list[SuiteRun], pending: set[str], now: float) -> None:
    running = [
        f"{suite.name} {max(0.0, now - suite.started_at):.0f}s"
        for suite in active
        if suite.name in pending
    ]
    completed = len(active) - len(pending)
    suffix = ", ".join(running) if running else "finishing"
    print(
        f"{_tag('wait')} be patient... {completed}/{len(active)} suites complete; running: {suffix}",
        flush=True,
    )


def _run_parallel(suites: list[SuiteRun], log_dir: Path) -> None:
    env = _child_environment()
    active: list[SuiteRun] = []
    handles = []
    try:
        for suite in suites:
            if suite.skipped:
                continue
            suite.log_path = log_dir / f"{suite.name}.log"
            handle = suite.log_path.open("w", encoding="utf-8", errors="replace")
            handles.append(handle)
            suite.started_at = time.monotonic()
            suite.process = subprocess.Popen(
                [sys.executable, suite.script],
                cwd=ROOT,
                env=env,
                stdout=handle,
                stderr=subprocess.STDOUT,
            )
            active.append(suite)

        names = ", ".join(suite.name for suite in active)
        print(f"{_tag('run')} started {len(active)} suites in parallel: {names}", flush=True)
        print(
            f"{_tag('run')} detailed logs are buffered; heartbeat every {HEARTBEAT_SECONDS:.0f}s.",
            flush=True,
        )

        pending = {suite.name for suite in active}
        next_heartbeat = time.monotonic() + HEARTBEAT_SECONDS
        while pending:
            for suite in active:
                if suite.name not in pending:
                    continue
                returncode = suite.process.poll()
                if returncode is not None:
                    suite.returncode = returncode
                    suite.finished_at = time.monotonic()
                    pending.remove(suite.name)
                    duration = max(0.0, suite.finished_at - suite.started_at)
                    tag = _tag("ok" if returncode == 0 else "fail")
                    print(
                        f"{tag} {suite.name}: {_status_text(returncode)} after {duration:.2f}s",
                        flush=True,
                    )
                    if returncode != 0 and pending:
                        # fail-fast: a known failed suite makes the remaining
                        # wall time wasted evidence (the slowest suite owns the
                        # batch); stop paying it (2026-09-21 gate review, P1)
                        print(
                            f"{_tag('fail')} early exit: terminating {len(pending)} remaining "
                            f"suite(s) after first failure ({suite.name}).",
                            flush=True,
                        )
                        _terminate_children(active)
                        now = time.monotonic()
                        for other in active:
                            if other.name in pending:
                                other.terminated = True
                                other.finished_at = now
                        pending.clear()

            now = time.monotonic()
            if pending and now >= next_heartbeat:
                _heartbeat(active, pending, now)
                while next_heartbeat <= now:
                    next_heartbeat += HEARTBEAT_SECONDS

            if pending:
                time.sleep(POLL_SECONDS)
    except KeyboardInterrupt:
        _terminate_children(active)
        raise
    finally:
        for handle in handles:
            handle.close()


def _run_serial(suites: list[SuiteRun], log_dir: Path) -> None:
    env = _child_environment()
    enabled = [suite for suite in suites if not suite.skipped]
    print(f"{_tag('run')} running {len(enabled)} suites serially.", flush=True)
    for suite in suites:
        if suite.skipped:
            continue
        suite.log_path = log_dir / f"{suite.name}.log"
        suite.started_at = time.monotonic()
        print(f"{_tag('run')} starting {suite.name}...", flush=True)
        with suite.log_path.open("w", encoding="utf-8", errors="replace") as handle:
            completed = subprocess.run(
                [sys.executable, suite.script],
                cwd=ROOT,
                env=env,
                stdout=handle,
                stderr=subprocess.STDOUT,
            )
        suite.finished_at = time.monotonic()
        suite.returncode = completed.returncode
        duration = max(0.0, suite.finished_at - suite.started_at)
        tag = _tag("ok" if completed.returncode == 0 else "fail")
        print(f"{tag} {suite.name}: {_status_text(completed.returncode)} after {duration:.2f}s", flush=True)
        if completed.returncode != 0:
            print(
                f"{_tag('fail')} early exit: not starting remaining suite(s) after first "
                f"failure ({suite.name}).",
                flush=True,
            )
            for remaining in suites:
                if not remaining.skipped and remaining.returncode is None:
                    remaining.terminated = True
            break


def _print_log(suite: SuiteRun) -> None:
    if suite.log_path is None or not suite.log_path.exists():
        return
    text = suite.log_path.read_text(encoding="utf-8", errors="replace")
    if text:
        print(text, end="" if text.endswith("\n") else "\n")


def _print_results(suites: list[SuiteRun], wall_seconds: float, serial: bool) -> int:
    failures = [suite for suite in suites if not suite.skipped and not suite.terminated and suite.returncode != 0]
    verbose = _env_flag("QIVEN_TEST_VERBOSE")

    print("\n=== TEST SUMMARY ===")
    for suite in suites:
        if suite.skipped:
            print(f"[SKIP] {suite.name}: non-Windows host")
            continue
        if suite.terminated:
            if suite.started_at:
                print(f"[CUT ] {suite.name:<28} terminated (early exit after failure)")
            else:
                print(f"[SKIP] {suite.name:<28} not started (early exit after failure)")
            continue
        duration = max(0.0, suite.finished_at - suite.started_at)
        tag = _tag("ok" if suite.returncode == 0 else "fail")
        print(f"{tag} {suite.name:<28} {duration:6.2f}s")

    if failures:
        print("\n=== FAILED SUITE LOGS ===")
        for suite in failures:
            print(f"\n{_tag('fail')} {suite.name} detailed output")
            print("-" * 72)
            _print_log(suite)
            print("-" * 72)
    elif verbose:
        print("\n=== VERBOSE SUITE LOGS ===")
        for suite in suites:
            if not suite.skipped:
                print(f"\n{_tag('ok')} {suite.name} detailed output")
                print("-" * 72)
                _print_log(suite)
                print("-" * 72)

    mode = "serial" if serial else "parallel"
    final_tag = _tag("fail" if failures else "ok")
    print(
        f"\n{final_tag} Test suites complete: mode={mode}, wall={wall_seconds:.2f}s, failures={len(failures)}"
    )
    if not failures and not verbose:
        print("      Set QIVEN_TEST_VERBOSE=1 to print passing-suite logs.")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="qiven-context suite runner")
    parser.add_argument(
        "--group",
        choices=("all", "repo", "tools"),
        default="all",
        help="suite group: repo = this repository's canonical contracts; "
        "tools = validator mutation tests and bootstrap resolution; "
        "all = every suite (required for tools/kernel-path changes)",
    )
    args = parser.parse_args()
    suites = _enabled_suites()
    if args.group != "all":
        suites = [suite for suite in suites if suite.group == args.group]
        print(f"[ RUN] group={args.group}: {len(suites)} suite(s)", flush=True)
        if not suites:
            # vacuous pass guard: an empty group selection must fail loudly,
            # never exit 0 through an empty batch (P-51 discipline)
            print("[FAIL] group selection matched zero suites", flush=True)
            return 1
    serial = _env_flag("QIVEN_TEST_SERIAL")
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="qiven-context-tests-", ignore_cleanup_errors=True) as temp:
        log_dir = Path(temp)
        try:
            if serial:
                _run_serial(suites, log_dir)
            else:
                _run_parallel(suites, log_dir)
        except KeyboardInterrupt:
            print(f"\n{_tag('fail')} Test run interrupted; child suites were terminated.", file=sys.stderr, flush=True)
            return 130
        wall_seconds = time.monotonic() - started
        return _print_results(suites, wall_seconds, serial)


if __name__ == "__main__":
    raise SystemExit(main())
