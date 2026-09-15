from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from retrieval_acceptance import evaluate_acceptance, load_acceptance  # noqa: E402


@dataclass(frozen=True)
class FakeHit:
    id: str
    rerank_score: float
    rerank_rank: int
    hybrid_rank: int
    deterministic_rank: int | None = None
    semantic_rank: int | None = None
    graph_candidate: bool = False


class FakeRetriever:
    semantic_model = "fake-semantic"
    rerank_model = "fake-reranker"

    def __init__(self, selected_by_task: dict[str, set[str]], ranked_by_task: dict[str, list[FakeHit]]):
        self.selected_by_task = selected_by_task
        self.ranked_by_task = ranked_by_task

    def rank(self, query):
        return list(self.ranked_by_task.get(str(query["task"]), []))

    def select_ids(self, query):
        return set(self.selected_by_task.get(str(query["task"]), set()))


class RetrievalAcceptanceContractTests(unittest.TestCase):
    def test_blind_v3_is_frozen_against_cross_encoder_candidate(self):
        acceptance = load_acceptance(ROOT / "benchmarks/retrieval/blind-v3.yaml", ROOT)
        self.assertEqual(acceptance["name"], "blind-retrieval-v3")
        self.assertEqual(
            acceptance["frozen_candidate"],
            "be3f0545ef39f96736442735fae3ab1f4a3a0ff5",
        )
        positives = [case for case in acceptance["cases"] if case["kind"] == "positive"]
        negatives = [case for case in acceptance["cases"] if case["kind"] == "negative"]
        self.assertGreaterEqual(len(positives), 8)
        self.assertGreaterEqual(len(negatives), 4)
        self.assertEqual(acceptance["thresholds"]["negative_abstention_rate_min"], 1.0)
        self.assertEqual(acceptance["thresholds"]["positive_required_id_recall_min"], 1.0)

    def test_negative_case_cannot_claim_required_or_allowed_ids(self):
        source = yaml.safe_load((ROOT / "benchmarks/retrieval/blind-v3.yaml").read_text(encoding="utf-8"))
        negative = next(case for case in source["cases"] if case["kind"] == "negative")
        negative["required_ids"] = ["ADR-0001"]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.yaml"
            path.write_text(yaml.safe_dump(source, sort_keys=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "negative acceptance case .* must not require"):
                load_acceptance(path, ROOT)

    def test_positive_case_requires_at_least_one_id(self):
        source = yaml.safe_load((ROOT / "benchmarks/retrieval/blind-v3.yaml").read_text(encoding="utf-8"))
        positive = next(case for case in source["cases"] if case["kind"] == "positive")
        positive["required_ids"] = []
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.yaml"
            path.write_text(yaml.safe_dump(source, sort_keys=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "positive acceptance case .* must require"):
                load_acceptance(path, ROOT)

    def test_acceptance_distinguishes_recall_from_abstention(self):
        acceptance = {
            "name": "fixture",
            "frozen_candidate": "a" * 40,
            "thresholds": {
                "critical_case_success_min": 1.0,
                "positive_required_id_recall_min": 1.0,
                "forbidden_hits_max": 0,
                "mean_positive_extra_ids_max": 0.0,
                "negative_abstention_rate_min": 1.0,
            },
            "cases": [
                {
                    "id": "positive",
                    "kind": "positive",
                    "critical": True,
                    "query": {"task": "positive"},
                    "required_ids": ["ADR-0008"],
                    "forbidden_ids": [],
                    "allowed_extra_ids": [],
                },
                {
                    "id": "negative",
                    "kind": "negative",
                    "critical": True,
                    "query": {"task": "negative"},
                    "required_ids": [],
                    "forbidden_ids": [],
                    "allowed_extra_ids": [],
                },
            ],
        }
        retriever = FakeRetriever(
            {"positive": {"ADR-0008"}, "negative": set()},
            {
                "positive": [FakeHit("ADR-0008", 2.0, 1, 1)],
                "negative": [FakeHit("ADR-0010", -4.0, 1, 1)],
            },
        )
        result = evaluate_acceptance(acceptance, retriever)
        self.assertTrue(result["pass"])
        self.assertEqual(result["metrics"]["positive_required_id_recall"], 1.0)
        self.assertEqual(result["metrics"]["negative_abstention_rate"], 1.0)

    def test_nonempty_negative_selection_fails_abstention(self):
        acceptance = {
            "name": "fixture",
            "frozen_candidate": "a" * 40,
            "thresholds": {
                "critical_case_success_min": 1.0,
                "positive_required_id_recall_min": 1.0,
                "forbidden_hits_max": 0,
                "mean_positive_extra_ids_max": 0.0,
                "negative_abstention_rate_min": 1.0,
            },
            "cases": [
                {
                    "id": "negative",
                    "kind": "negative",
                    "critical": True,
                    "query": {"task": "negative"},
                    "required_ids": [],
                    "forbidden_ids": [],
                    "allowed_extra_ids": [],
                }
            ],
        }
        retriever = FakeRetriever(
            {"negative": {"ADR-0010"}},
            {"negative": [FakeHit("ADR-0010", -4.0, 1, 1)]},
        )
        result = evaluate_acceptance(acceptance, retriever)
        self.assertFalse(result["pass"])
        self.assertEqual(result["metrics"]["negative_abstention_rate"], 0.0)
        self.assertFalse(result["cases"][0]["pass"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
