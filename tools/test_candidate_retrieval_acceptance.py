from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from candidate_retrieval_acceptance import (  # noqa: E402
    evaluate_acceptance,
    load_candidate_acceptance,
)
from context_compiler import CanonicalRecord  # noqa: E402


class FakeRetriever:
    def __init__(self):
        self.records = {}
        for canonical_id in ("ADR-A", "ADR-B", "ADR-C", "ADR-D"):
            self.records[canonical_id] = CanonicalRecord(
                category="decisions",
                id=canonical_id,
                path=f"decisions/{canonical_id}.md",
                title=canonical_id,
                status="accepted",
                metadata={},
                body=f"canonical body for {canonical_id}",
            )

    def rank(self, query):
        task = str(query["task"])
        order = ["ADR-A", "ADR-B", "ADR-C"] if "positive" in task else ["ADR-D", "ADR-C", "ADR-B"]
        return [
            SimpleNamespace(
                id=canonical_id,
                rerank_score=1.0 / rank,
                rerank_rank=rank,
                hybrid_rank=rank,
                deterministic_rank=rank,
                semantic_rank=rank,
                graph_candidate=False,
                explicit=False,
            )
            for rank, canonical_id in enumerate(order, 1)
        ]


class CandidateRetrievalAcceptanceTests(unittest.TestCase):
    def test_metrics_measure_candidate_recall_top1_and_forbidden_top1(self):
        acceptance = {
            "name": "test",
            "frozen_candidate": "a" * 40,
            "max_candidates": 3,
            "thresholds": {
                "positive_required_id_recall_min": 1.0,
                "positive_top1_required_rate_min": 1.0,
                "forbidden_top1_hits_max": 0,
            },
            "cases": [
                {
                    "id": "positive-case",
                    "kind": "positive",
                    "critical": True,
                    "cognition_expectation": "answer",
                    "query": {"task": "positive task"},
                    "required_ids": ["ADR-A"],
                    "forbidden_ids": ["ADR-D"],
                },
                {
                    "id": "negative-case",
                    "kind": "negative",
                    "critical": True,
                    "cognition_expectation": "abstain",
                    "query": {"task": "negative task"},
                    "required_ids": [],
                    "forbidden_ids": [],
                },
            ],
        }
        result = evaluate_acceptance(acceptance, FakeRetriever(), root=ROOT)
        self.assertTrue(result["retrieval_pass"])
        self.assertEqual(result["metrics"]["positive_required_id_recall"], 1.0)
        self.assertEqual(result["metrics"]["positive_top1_required_rate"], 1.0)
        self.assertEqual(result["metrics"]["forbidden_top1_hits"], 0)
        self.assertEqual(result["cognition_status"], "manual-pending")
        self.assertEqual(result["cases"][1]["candidate_ids"], ["ADR-D", "ADR-C", "ADR-B"])

    def test_loader_rejects_wrong_cognition_expectation(self):
        payload = {
            "schema_version": 1,
            "name": "bad",
            "purpose": "test payload",
            "frozen_candidate": "a" * 40,
            "max_candidates": 3,
            "thresholds": {
                "positive_required_id_recall_min": 1.0,
                "positive_top1_required_rate_min": 1.0,
                "forbidden_top1_hits_max": 0,
            },
            "cases": [
                {
                    "id": "bad-positive",
                    "kind": "positive",
                    "critical": True,
                    "cognition_expectation": "abstain",
                    "query": {"task": "bad expectation"},
                    "required_ids": ["ADR-A"],
                    "forbidden_ids": [],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "acceptance.yaml"
            path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "cognition_expectation=answer"):
                load_candidate_acceptance(path, ROOT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
