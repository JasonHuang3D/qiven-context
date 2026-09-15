from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from atomic_nli_class_probe import score_atom_bundle_classes  # noqa: E402
from nli_answerability_probe import NliClassProbabilities  # noqa: E402


class FakeClassBackend:
    def __init__(self, rows):
        self.rows = list(rows)

    def class_probabilities(self, premises, hypotheses):
        self.premises = list(premises)
        self.hypotheses = list(hypotheses)
        return list(self.rows)


class AtomicNliClassProbeTests(unittest.TestCase):
    def test_entailment_winner_marks_atom_supported(self):
        backend = FakeClassBackend(
            [
                NliClassProbabilities(0.2, 0.7, 0.1),
                NliClassProbabilities(0.6, 0.3, 0.1),
            ]
        )
        rows = score_atom_bundle_classes(
            backend,
            ["claim"],
            [("A", "neutral evidence"), ("B", "supporting evidence")],
        )
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0].supported)
        self.assertEqual(rows[0].record_id, "B")
        self.assertEqual(rows[0].probabilities.winner, "entailment")

    def test_neutral_winner_does_not_count_as_support(self):
        backend = FakeClassBackend(
            [NliClassProbabilities(0.3, 0.6, 0.1)]
        )
        rows = score_atom_bundle_classes(backend, ["claim"], [("A", "unknown evidence")])
        self.assertFalse(rows[0].supported)
        self.assertEqual(rows[0].probabilities.winner, "neutral")

    def test_all_atoms_are_scored_against_all_evidence(self):
        backend = FakeClassBackend(
            [
                NliClassProbabilities(0.7, 0.2, 0.1),
                NliClassProbabilities(0.1, 0.8, 0.1),
                NliClassProbabilities(0.2, 0.7, 0.1),
                NliClassProbabilities(0.8, 0.1, 0.1),
            ]
        )
        rows = score_atom_bundle_classes(
            backend,
            ["first", "second"],
            [("A", "one"), ("B", "two")],
        )
        self.assertEqual([row.record_id for row in rows], ["A", "B"])
        self.assertEqual(backend.hypotheses, ["first", "first", "second", "second"])

    def test_empty_atoms_are_rejected(self):
        backend = FakeClassBackend([])
        with self.assertRaisesRegex(ValueError, "at least one atomic claim"):
            score_atom_bundle_classes(backend, [], [("A", "evidence")])


if __name__ == "__main__":
    unittest.main(verbosity=2)
