"""Fast repository-contract validation for ordinary commits.

Runs the full validate_repository() against the real working tree once
(schema/front matter/index/lifecycle/layout invariants) plus the
cold-boot-independent read-only checks. This is the gate for text and
record transactions; the validator's own mutation tests live in
tools/test.py and run in the context-tools gate (ADR-0040-era change-
class gate split, extended 2026-09-21).
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_context import validate_repository  # noqa: E402


class RepoContractTests(unittest.TestCase):
    def test_repository_is_valid(self):
        errors = validate_repository(ROOT)
        self.assertEqual(errors, [], "repository contract violations")

    def test_validator_toolchain_smoke(self):
        # the fast path must be wired to the same validator the tools gate exercises
        from validate_context import REQUIRED  # noqa: F401
        self.assertTrue(callable(validate_repository))


if __name__ == "__main__":
    unittest.main(verbosity=2)
