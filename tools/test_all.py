from __future__ import annotations

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


@dataclass
class SuiteRun:
    name: str
    script: str
    windows_only: bool = False
    process: subprocess.Popen | None = None
    log_path: Path | None = None
    started_at: float = 0.0
    finished_at: float = 0.0
    returncode: int | None = None
    skipped: bool = False


SUITES = (
    SuiteRun("repository-validator", "tools/test.py"),
    SuiteRun("context-compiler", "tools/test_context_compiler.py"),
    SuiteRun("context-acceptance", "tools/test_context_acceptance.py"),
    SuiteRun("windows-python-resolution", "tools/test_windows_python.py", windows_only=True),
)


def _child_environment() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return env


def _enabled_suites() -> list[SuiteRun]:
    result: list[SuiteRun] = []
    for source in SUITES:
        suite = SuiteRun(source.name, source.script, source.windows_only)
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
        f"[test] be patient... {completed}/{len(active)} suites complete; running: {suffix}",
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
        print(
            f"[test] started {len(active)} suites in parallel: {names}",
            flush=True,
        )
        print(
            f"[test] detailed suite output is buffered; heartbeat every {HEARTBEAT_SECONDS:.0f}s.",
            flush=True,
        )

        pending = set(suite.name for suite in active)
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
                    print(
                        f"[test] {suite.name}: {_status_text(returncode)} after {duration:.2f}s; detailed log buffered.",
                        flush=True,
                    )

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
    print(f"[test] running {len(enabled)} suites serially.", flush=True)
    for suite in suites:
        if suite.skipped:
            continue
        suite.log_path = log_dir / f"{suite.name}.log"
        suite.started_at = time.monotonic()
        print(f"[test] starting {suite.name}...", flush=True)
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
        print(
            f"[test] {suite.name}: {_status_text(completed.returncode)} after {duration:.2f}s; detailed log buffered.",
            flush=True,
        )


def _print_results(suites: list[SuiteRun], wall_seconds: float, serial: bool) -> int:
    failures = 0
    for suite in suites:
        if suite.skipped:
            print(f"\n=== {suite.name}: SKIP (non-Windows host) ===")
            continue
        duration = max(0.0, suite.finished_at - suite.started_at)
        passed = suite.returncode == 0
        status = "PASS" if passed else f"FAIL({suite.returncode})"
        print(f"\n=== {suite.name}: {status} [{duration:.2f}s] ===")
        if suite.log_path is not None and suite.log_path.exists():
            text = suite.log_path.read_text(encoding="utf-8", errors="replace")
            if text:
                print(text, end="" if text.endswith("\n") else "\n")
        if not passed:
            failures += 1
    mode = "serial" if serial else "parallel"
    print(f"\nTest suites complete: mode={mode}, wall={wall_seconds:.2f}s, failures={failures}")
    return 1 if failures else 0


def main() -> int:
    suites = _enabled_suites()
    serial = os.environ.get("QIVEN_TEST_SERIAL", "").strip().casefold() in {"1", "true", "yes", "on"}
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="qiven-context-tests-") as temp:
        log_dir = Path(temp)
        try:
            if serial:
                _run_serial(suites, log_dir)
            else:
                _run_parallel(suites, log_dir)
        except KeyboardInterrupt:
            print("\nTest run interrupted; child suites were terminated.", file=sys.stderr, flush=True)
            return 130
        wall_seconds = time.monotonic() - started
        return _print_results(suites, wall_seconds, serial)


if __name__ == "__main__":
    raise SystemExit(main())
