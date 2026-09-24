"""Public qiven-context test runner; delegates suite bodies through test_entry."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "tools" / "test_entry.py"
_ORIGINAL_POPEN = subprocess.Popen


def _rewrite_test_command(args):
    if not isinstance(args, (list, tuple)) or len(args) < 2:
        return args
    executable = str(args[0])
    script = Path(str(args[1]))
    name = script.name
    if executable == sys.executable and name.startswith("test") and name not in {
        "test_entry.py", "test_all.py", "test_all_impl.py"
    }:
        return [executable, str(ENTRY), *map(str, args[1:])]
    return args


def _popen(args, *positional, **kwargs):
    return _ORIGINAL_POPEN(_rewrite_test_command(args), *positional, **kwargs)


subprocess.Popen = _popen
from test_all_impl import main


if __name__ == "__main__":
    raise SystemExit(main())
