from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from atomic_entailment_probe import DEVELOPMENT_ATOMS, score_atom_bundle  # noqa: E402


class FakeNliBackend:
    def __init__(self, scores):
        self.scores = list(scores)
        self.calls = 0

    def entailment_probabilities(self, premises, hypotheses):
        self.calls += 1
        self.premises = list(premises)
        self.hypotheses = list(hypotheses)
        return list(self.scores)


class AtomicEntailmentProbeTests(unittest.TestCase):
    def test_bundle_selects_best_evidence_per_atom(self):
        backend = FakeNliBackend([0.2, 0.8, 0.7, 0.1])
        rows = score_atom_bundle(
            backend,
            ["atom one", "atom two"],
            [("ADR-A", "evidence a"), ("ADR-B", "evidence b")],
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].record_id, "ADR-B")
        self.assertAlmostEqual(rows[0].entailment, 0.8)
        self.assertEqual(rows[1].record_id, "ADR-A")
        self.assertAlmostEqual(rows[1].entailment, 0.7)
        self.assertEqual(backend.hypotheses, ["atom one", "atom one", "atom two", "atom two"])

    def test_empty_evidence_returns_no_support_without_backend_call(self):
        backend = FakeNliBackend([])
        self.assertEqual(score_atom_bundle(backend, ["atom"], []), [])
        self.assertEqual(backend.calls, 0)

    def test_empty_atoms_are_rejected(self):
        backend = FakeNliBackend([])
        with self.assertRaisesRegex(ValueError, "at least one atomic claim"):
            score_atom_bundle(backend, ["  "], [("ADR", "evidence")])

    def test_backend_cardinality_mismatch_is_rejected(self):
        backend = FakeNliBackend([0.5])
        with self.assertRaisesRegex(RuntimeError, "wrong number"):
            score_atom_bundle(backend, ["a", "b"], [("ADR", "evidence")])

    def test_development_atoms_cover_observed_blind_v3_cases(self):
        expected = {
            "foundation-ownership-must-stay-explicit",
            "devkit-must-not-overwrite-consumer-edits",
            "math-must-not-hide-global-epsilon",
            "recurring-ambiguity-should-be-codified",
            "foundation-support-is-ci-evidence",
            "toolchain-name-does-not-imply-every-host-tool",
            "automated-record-writer-needs-id-issuance",
            "old-python-fixture-must-test-version-path",
            "negative-generic-cpp-vector-growth",
            "negative-generic-database-normalization",
            "negative-unknown-workstation-temperature",
            "negative-unknown-gas-cloud-region",
        }
        self.assertEqual(set(DEVELOPMENT_ATOMS), expected)
        self.assertTrue(all(atoms and all(atom.strip() for atom in atoms) for atoms in DEVELOPMENT_ATOMS.values()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
