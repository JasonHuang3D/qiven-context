"""Cross-platform process entry for qiven-context test suites only.

This module changes no production Context semantics.  It repairs fixture-runtime
assumptions before executing a suite:

* sqlite3.Connection's context manager commits/rolls back but does not own/close the
  connection.  Tests that use direct ``with sqlite3.connect(...)`` therefore need a
  closing connection on Windows, where an open handle blocks TemporaryDirectory
  cleanup.  Python 3.14 also reports these leaks explicitly as ResourceWarning.
* the K1 synthetic Git fixture mutates canonical Markdown through text mode.  Git is
  told to normalize committed text to LF so the synthetic commit uses the same
  canonical line ending as exact Git source snapshots on every OS.
* suite scripts are resolved to physical absolute paths before ``runpy`` execution.
  Tests that intentionally change cwd and spawn a fresh copy via ``__file__`` must
  therefore remain bound to the repository script rather than reinterpreting a
  relative ``tools/...`` path under the temporary cwd.

The normal public runner remains ``python tools/test_all.py``.
"""
from __future__ import annotations

import os
from pathlib import Path
import runpy
import sqlite3
import sys


class _ClosingConnection(sqlite3.Connection):
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


def _install_closing_sqlite_context() -> None:
    original = sqlite3.connect
    if getattr(original, "_qiven_test_closing", False):
        return

    def connect(*args, **kwargs):
        kwargs.setdefault("factory", _ClosingConnection)
        return original(*args, **kwargs)

    connect._qiven_test_closing = True
    sqlite3.connect = connect


def _append_git_config(key: str, value: str) -> None:
    raw = os.environ.get("GIT_CONFIG_COUNT", "0")
    try:
        count = int(raw)
    except ValueError as exc:
        raise RuntimeError(f"invalid inherited GIT_CONFIG_COUNT: {raw!r}") from exc
    os.environ[f"GIT_CONFIG_KEY_{count}"] = key
    os.environ[f"GIT_CONFIG_VALUE_{count}"] = value
    os.environ["GIT_CONFIG_COUNT"] = str(count + 1)


def main() -> int:
    if len(sys.argv) < 2:
        raise SystemExit("usage: test_entry.py TEST_SCRIPT [ARGS ...]")
    target = Path(sys.argv[1]).resolve()
    if not target.is_file():
        raise SystemExit(f"test target does not exist: {target}")

    _install_closing_sqlite_context()
    if target.name == "test_context_kernel.py":
        _append_git_config("core.autocrlf", "input")

    sys.argv = [str(target), *sys.argv[2:]]
    runpy.run_path(str(target), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
