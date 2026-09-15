from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from hybrid_retriever import (  # noqa: E402
    DEFAULT_RRF_K,
    DEFAULT_TOP_K,
    DeterministicHit,
    HybridRetriever,
    reciprocal_rank,
)
from semantic_retriever import SemanticHit  # noqa: E402


class FakeSemantic:
    model_name = "fake-semantic"

    def __init__(self, ids):
        self.ids = list(ids)

    def rank(self, query):
        return [
            SemanticHit(id=value, category="memory", path=f"{value}.md", title=value, score=1.0 / index)
            for index, value in enumerate(self.ids, 1)
        ]


def deterministic_ranker(ids):
    rows = [DeterministicHit(id=value, category="memory", score=100 - index) for index, value in enumerate(ids)]

    def run(query, root):
        return rows

    return run


class HybridRetrievalTests(unittest.TestCase):
    def test_frozen_constants(self):
        self.assertEqual(DEFAULT_RRF_K, 60)
        self.assertEqual(DEFAULT_TOP_K, 8)

    def test_reciprocal_rank_is_monotonic(self):
        self.assertGreater(reciprocal_rank(1), reciprocal_rank(2))
        self.assertEqual(reciprocal_rank(None), 0.0)

    def test_rrf_rewards_agreement_across_channels(self):
        hybrid = HybridRetriever(
            ROOT,
            semantic_retriever=FakeSemantic(["B", "A", "C"]),
            deterministic_ranker=deterministic_ranker(["A", "B", "D"]),
        )
        ranked = hybrid.rank({"task": "fixture"})
        self.assertEqual(ranked[0].id, "A")
        self.assertEqual(ranked[1].id, "B")
        self.assertEqual(ranked[0].deterministic_rank, 1)
        self.assertEqual(ranked[0].semantic_rank, 2)

    def test_semantic_only_candidate_can_enter_fused_ranking(self):
        hybrid = HybridRetriever(
            ROOT,
            semantic_retriever=FakeSemantic(["SEM", "A", "B"]),
            deterministic_ranker=deterministic_ranker(["A", "B"]),
        )
        ids = [hit.id for hit in hybrid.rank({"task": "fixture"})]
        self.assertIn("SEM", ids)

    def test_explicit_id_is_preserved(self):
        hybrid = HybridRetriever(
            ROOT,
            semantic_retriever=FakeSemantic(["A", "B", "C"]),
            deterministic_ranker=deterministic_ranker(["A", "B", "C"]),
        )
        selected = hybrid.select_ids({"task": "fixture", "include_ids": ["C"]}, top_k=2)
        self.assertEqual(len(selected), 2)
        self.assertIn("C", selected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
