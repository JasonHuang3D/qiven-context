from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from concrete_entailment_probe import (  # noqa: E402
    DEVELOPMENT_CLAIMS,
    score_claim_entailment,
)


class FakeNliBackend:
    def __init__(self, scores):
        self.scores = list(scores)
        self.calls = 0

    def entailment_probabilities(self, premises, hypotheses):
        self.calls += 1
        self.premises = list(premises)
        self.hypotheses = list(hypotheses)
        return list(self.scores)


class ConcreteEntailmentProbeTests(unittest.TestCase):
    def test_claim_entailment_scores_each_chunk_against_same_concrete_claim(self):
        backend = FakeNliBackend([0.2, 0.9, 0.5])
        rows = score_claim_entailment(
            backend,
            "The candidate answer is supported.",
            ["weak", "strong", "medium"],
        )
        self.assertEqual([row.text for row in rows], ["strong", "medium", "weak"])
        self.assertEqual(backend.hypotheses, ["The candidate answer is supported."] * 3)
        self.assertEqual(backend.premises, ["weak", "strong", "medium"])

    def test_empty_evidence_does_not_call_backend(self):
        backend = FakeNliBackend([])
        self.assertEqual(score_claim_entailment(backend, "supported claim", []), [])
        self.assertEqual(backend.calls, 0)

    def test_empty_claim_is_rejected(self):
        backend = FakeNliBackend([0.5])
        with self.assertRaisesRegex(ValueError, "claim must not be empty"):
            score_claim_entailment(backend, "   ", ["evidence"])

    def test_backend_cardinality_mismatch_is_rejected(self):
        backend = FakeNliBackend([0.5])
        with self.assertRaisesRegex(RuntimeError, "wrong number"):
            score_claim_entailment(backend, "claim", ["one", "two"])

    def test_development_claims_cover_observed_blind_v3_cases(self):
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
        self.assertEqual(set(DEVELOPMENT_CLAIMS), expected)
        self.assertTrue(all(value.strip() for value in DEVELOPMENT_CLAIMS.values()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
