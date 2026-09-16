from __future__ import annotations

from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from hybrid_retriever import HybridHit  # noqa: E402
from rerank_retriever import (  # noqa: E402
    DEFAULT_GRAPH_SEED_TOP_K,
    DEFAULT_RERANK_MODEL,
    DEFAULT_SEMANTIC_POOL_TOP_K,
    RerankedRetriever,
)


class FakeHybrid:
    semantic_model = "fake-semantic"

    def __init__(self, hits):
        self._hits = list(hits)

    def rank(self, query):
        return list(self._hits)


class FakeReranker:
    model_name = "fake-reranker"

    def __init__(self, scores):
        self.scores = dict(scores)

    def score(self, query, documents):
        result = []
        for document in documents:
            match = re.search(r"^id: (.+)$", document, flags=re.MULTILINE)
            if match is None:
                raise AssertionError("record text did not expose canonical id")
            result.append(float(self.scores.get(match.group(1), -10.0)))
        return result


def hit(canonical_id, *, d=None, s=None, score=1.0):
    return HybridHit(
        id=canonical_id,
        score=float(score),
        deterministic_rank=d,
        semantic_rank=s,
    )


class RerankRetrievalTests(unittest.TestCase):
    def test_frozen_candidate_constants(self):
        self.assertEqual(DEFAULT_RERANK_MODEL, "BAAI/bge-reranker-base")
        self.assertEqual(DEFAULT_SEMANTIC_POOL_TOP_K, 16)
        self.assertEqual(DEFAULT_GRAPH_SEED_TOP_K, 1)

    def test_deterministic_candidate_is_preserved_beyond_semantic_pool(self):
        retriever = RerankedRetriever(
            ROOT,
            hybrid_retriever=FakeHybrid(
                [
                    hit("ADR-0030", d=1, s=1),
                    hit("ADR-0009", d=20, s=40),
                ]
            ),
            reranker_backend=FakeReranker({}),
        )
        evidence = {item.id for item in retriever.candidate_evidence({"task": "fixture"})}
        self.assertIn("ADR-0009", evidence)

    def test_graph_expands_only_from_strongest_base_anchor(self):
        retriever = RerankedRetriever(
            ROOT,
            hybrid_retriever=FakeHybrid(
                [
                    hit("ADR-0022", d=1, s=1),
                    hit("ADR-0018", d=2, s=2),
                    hit("MEM-20260914T124259Z-5C8E21", d=None, s=30),
                    hit("ADR-0010", d=None, s=31),
                ]
            ),
            reranker_backend=FakeReranker({}),
        )
        evidence = {item.id: item for item in retriever.candidate_evidence({"task": "fixture"})}
        self.assertTrue(evidence["MEM-20260914T124259Z-5C8E21"].graph_candidate)
        self.assertNotIn("ADR-0010", evidence)

    def test_project_scope_filter_removes_cross_domain_physics_candidate(self):
        retriever = RerankedRetriever(
            ROOT,
            hybrid_retriever=FakeHybrid(
                [
                    hit("ADR-0020", d=1, s=1),
                    hit("OBL-20260913T183819Z-9A4F21", d=2, s=2),
                ]
            ),
            reranker_backend=FakeReranker({}),
        )
        evidence = {
            item.id
            for item in retriever.candidate_evidence(
                {"task": "industrial gas backend architecture", "scopes": ["qiven-gas"]}
            )
        }
        self.assertIn("ADR-0020", evidence)
        self.assertNotIn("OBL-20260913T183819Z-9A4F21", evidence)

    def test_rank_orders_candidates_by_cross_encoder_score(self):
        retriever = RerankedRetriever(
            ROOT,
            hybrid_retriever=FakeHybrid(
                [
                    hit("ADR-0030", d=1, s=1),
                    hit("ADR-0021", d=2, s=2),
                ]
            ),
            reranker_backend=FakeReranker({"ADR-0030": 0.2, "ADR-0021": 0.8}),
        )
        ranked = retriever.rank({"task": "authority question"})
        self.assertEqual([item.id for item in ranked[:2]], ["ADR-0021", "ADR-0030"])
        self.assertEqual([item.rerank_rank for item in ranked[:2]], [1, 2])


if __name__ == "__main__":
    unittest.main(verbosity=2)
