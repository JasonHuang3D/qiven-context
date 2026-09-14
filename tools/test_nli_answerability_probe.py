from __future__ import annotations

import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from nli_answerability_probe import (  # noqa: E402
    _softmax,
    default_cache_dir,
    nli_premise,
    question_text,
    score_answerability,
)


class FakeNliBackend:
    def entailment_probabilities(self, premises, hypotheses):
        self.premises = list(premises)
        self.hypotheses = list(hypotheses)
        return [0.9, 0.1, 0.2, 0.8]


class NliAnswerabilityProbeTests(unittest.TestCase):
    def test_softmax_is_normalized_and_monotonic(self):
        values = _softmax([3.0, 1.0, -2.0])
        self.assertAlmostEqual(sum(values), 1.0, places=7)
        self.assertGreater(values[0], values[1])
        self.assertGreater(values[1], values[2])

    def test_question_text_preserves_task_and_structured_hints(self):
        text = question_text(
            {
                "task": "Which Qiven rule applies?",
                "topics": ["validation", "worker"],
                "scopes": ["qiven-foundation"],
            }
        )
        self.assertIn("Which Qiven rule applies?", text)
        self.assertIn("topics: validation, worker", text)
        self.assertIn("scopes: qiven-foundation", text)

    def test_nli_premise_keeps_question_and_evidence_distinct(self):
        text = nli_premise("Where is it deployed?", "The product is a business system.")
        self.assertEqual(
            text,
            "Question: Where is it deployed?\nEvidence: The product is a business system.",
        )

    def test_answerability_margin_compares_sufficient_and_insufficient_hypotheses(self):
        backend = FakeNliBackend()
        rows = score_answerability(
            backend,
            {"task": "What does the record establish?"},
            ["strong evidence", "weak evidence"],
        )
        self.assertEqual([row.text for row in rows], ["strong evidence", "weak evidence"])
        self.assertAlmostEqual(rows[0].margin, 0.8)
        self.assertAlmostEqual(rows[1].margin, -0.6)
        self.assertEqual(len(backend.premises), 4)
        self.assertEqual(len(backend.hypotheses), 4)

    def test_cache_override_keeps_model_files_outside_repository(self):
        with patch.dict(os.environ, {"QIVEN_NLI_CACHE": r"D:\QivenCache\nli"}, clear=False):
            self.assertEqual(default_cache_dir(), Path(r"D:\QivenCache\nli"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
