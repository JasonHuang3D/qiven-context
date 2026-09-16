from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys

EXPECTED_REPOS = {
    "git@github.com:JasonHuang3D/qiven-context.git",
    "https://github.com/JasonHuang3D/qiven-context.git",
    "https://github.com/JasonHuang3D/qiven-context",
}
KNOWN_NAMES = (
    "qiven-context-v2-acceptance",
    "qiven-context-v2-final-37fdbb33",
    "qiven-context-v2-canonical-merge",
    "qiven-context-guardrail-acceptance",
)


def run_git(path: Path, *args: str) -> tuple[int, str]:
    completed = subprocess.run(
        ["git", "-C", str(path), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.returncode, completed.stdout.strip()


def verify_repo(path: Path) -> tuple[bool, str]:
    rc, root = run_git(path, "rev-parse", "--show-toplevel")
    if rc != 0:
        return False, "not a Git working tree"
    try:
        if Path(root).resolve() != path.resolve():
            return False, f"Git root mismatch: {root}"
    except OSError as exc:
        return False, f"cannot resolve path: {exc}"
    rc, origin = run_git(path, "remote", "get-url", "origin")
    if rc != 0 or origin not in EXPECTED_REPOS:
        return False, f"unexpected origin: {origin or '<missing>'}"
    rc, dirty = run_git(path, "status", "--porcelain=v1", "--untracked-files=all")
    if rc != 0:
        return False, "git status failed"
    if dirty:
        return False, "working tree is dirty; preserved for review"
    return True, origin


def remove_verified(path: Path) -> tuple[str, str]:
    if not path.exists():
        return "missing", str(path)
    ok, detail = verify_repo(path)
    if not ok:
        return "preserved", f"{path} ({detail})"
    try:
        shutil.rmtree(path)
    except OSError as exc:
        return "failed", f"{path} ({exc})"
    return "deleted", str(path)


def main() -> int:
    temp_value = os.environ.get("TEMP") or os.environ.get("TMP")
    if not temp_value:
        print("[FAIL] TEMP/TMP is not defined")
        return 2
    temp = Path(temp_value)
    if not temp.is_dir():
        print(f"[FAIL] temp root is not a directory: {temp}")
        return 2

    candidates: list[Path] = [temp / name for name in KNOWN_NAMES]
    candidates.extend(sorted(temp.glob("qiven-context-branch-gc-*")))
    literal = temp / "%QV2%"
    if literal.exists():
        candidates.append(literal)

    seen: set[str] = set()
    results: list[tuple[str, str]] = []
    for candidate in candidates:
        key = str(candidate).casefold()
        if key in seen:
            continue
        seen.add(key)
        results.append(remove_verified(candidate))

    print("=== QIVEN-V6 TEMP CLEANUP ===")
    for status, detail in results:
        tag = {
            "deleted": "[ OK ]",
            "missing": "[ OK ]",
            "preserved": "[WARN]",
            "failed": "[FAIL]",
        }[status]
        print(f"{tag} {status}: {detail}")

    unresolved_literal = not literal.exists()
    if unresolved_literal:
        print("[WARN] No literal %QV2% directory was found under TEMP. Historical evidence did not establish its parent, so no broader filesystem deletion was attempted.")

    failures = [item for item in results if item[0] == "failed"]
    preserved = [item for item in results if item[0] == "preserved"]
    if failures:
        print(f"[FAIL] cleanup failed for {len(failures)} path(s)")
        return 1
    if preserved:
        print(f"[FAIL] cleanup preserved {len(preserved)} path(s) for human review")
        return 1
    print("[ OK ] known TEMP clone cleanup PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
