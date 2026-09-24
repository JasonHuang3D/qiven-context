from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def _devkit_tools() -> Path:
    """Resolve the Devkit operator (ADR-0046 shim consumption).

    Order: QIVEN_DEVKIT_ROOT env, then the workspace sibling layout.
    The consumed Devkit revision is pinned in .qiven/operator.json
    (devkit_pin); the pinned commit must be checked out (or fetched)
    for isolated use.
    """
    root = os.environ.get("QIVEN_DEVKIT_ROOT")
    if not root:
        sibling = Path(__file__).resolve().parents[2] / "qiven-devkit"
        root = str(sibling) if sibling.is_dir() else None
    if not root or not (Path(root) / "tools" / "qiven_operator.py").is_file():
        raise SystemExit(
            "[FAIL] qiven-devkit operator not found: set QIVEN_DEVKIT_ROOT to a "
            "devkit checkout (pinned per .qiven/operator.json devkit_pin) or "
            "place qiven-devkit beside this workspace (ADR-0046)."
        )
    return Path(root) / "tools"


os.environ["QIVEN_TARGET_ROOT"] = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(_devkit_tools()))
main = importlib.import_module("qiven_operator").main


if __name__ == "__main__":
    raise SystemExit(main())
