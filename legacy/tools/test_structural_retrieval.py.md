# [SEALED] tools/test_structural_retrieval.py

> Museum piece (ADR-0040/ADR-0041, sealed 2026-09-21). Original
> location: `tools/test_structural_retrieval.py`. Do not execute — this is historical text
> only; the `.md` extension makes accidental execution impossible.

````python
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from hybrid_retriever import HybridHit  # noqa: E402
from structural_retriever import (  # noqa: E402
    DEFAULT_GRAPH_DEPTH,
    DEFAULT_GRAPH_SEED_TOP_K,
    StructuralRetriever,
    bidirectional_relation_graph,
    canonical_record_map,
    graph_channel_rank,
    infer_active_project_scopes,
    is_scope_compatible,
)


PHYSICS_OBLIGATION = "OBL-20260913T183819Z-9A4F21"
RETRIEVAL_ADR = "ADR-0022"
RETRIEVAL_LESSON = "MEM-20260914T124259Z-5C8E21"


class FakeHybridRetriever:
    semantic_model = "fake"

    def __init__(self, hits):
        self._hits = list(hits)

    def rank(self, query):
        return list(self._hits)


def make_hit(canonical_id: str, rank: int, score: float) -> HybridHit:
    return HybridHit(
        id=canonical_id,
        score=score,
        deterministic_rank=rank,
        semantic_rank=rank,
    )


class StructuralRetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = canonical_record_map(ROOT)

    def test_frozen_structural_constants(self):
        self.assertEqual(DEFAULT_GRAPH_SEED_TOP_K, 4)
        self.assertEqual(DEFAULT_GRAPH_DEPTH, 1)

    def test_gas_query_infers_qiven_gas_project_scope(self):
        active = infer_active_project_scopes(
            {
                "task": "Should the industrial gas backend use the native stack?",
                "topics": ["industrial-gas", "backend", "architecture"],
                "now": "2026-09-14T13:30:00Z",
            },
            ROOT,
        )
        self.assertIn("qiven-gas", active)

    def test_project_scope_rejects_cross_domain_physics_record(self):
        record = self.records[PHYSICS_OBLIGATION]
        self.assertFalse(is_scope_compatible(record, {"qiven-gas"}))
        self.assertTrue(is_scope_compatible(record, {"qiven-robotics"}))

    def test_explicit_id_overrides_scope_filter(self):
        record = self.records[PHYSICS_OBLIGATION]
        self.assertTrue(
            is_scope_compatible(
                record,
                {"qiven-gas"},
                explicit_ids={PHYSICS_OBLIGATION},
            )
        )

    def test_relation_graph_is_bidirectional_for_incoming_memory_edge(self):
        graph = bidirectional_relation_graph(self.records)
        self.assertIn(RETRIEVAL_ADR, graph[RETRIEVAL_LESSON])
        self.assertIn(RETRIEVAL_LESSON, graph[RETRIEVAL_ADR])

    def test_graph_channel_only_expands_one_hop_from_frozen_seeds(self):
        graph = bidirectional_relation_graph(self.records)
        positions = graph_channel_rank(
            graph,
            [RETRIEVAL_ADR],
            allowed_ids=set(self.records),
        )
        self.assertIn(RETRIEVAL_LESSON, positions)
        self.assertGreaterEqual(positions[RETRIEVAL_LESSON], 1)

    def test_structural_rank_filters_physics_distractor_from_gas_query(self):
        ids = [
            "ADR-0020",
            PHYSICS_OBLIGATION,
            "ADR-0017",
            "ADR-0018",
            "ADR-0003",
            RETRIEVAL_ADR,
            "MEM-20260913T170803Z-A61F2C",
            RETRIEVAL_LESSON,
            "ADR-0014",
        ]
        fake = FakeHybridRetriever(
            [
                make_hit(canonical_id, index, 0.040 - index * 0.001)
                for index, canonical_id in enumerate(ids, 1)
            ]
        )
        retriever = StructuralRetriever(ROOT, hybrid_retriever=fake)
        ranked = retriever.rank(
            {
                "task": "Should the industrial gas backend use the native stack?",
                "topics": ["industrial-gas", "backend", "architecture"],
                "now": "2026-09-14T13:30:00Z",
            }
        )
        ranked_ids = [hit.id for hit in ranked]
        self.assertIn("ADR-0020", ranked_ids)
        self.assertNotIn(PHYSICS_OBLIGATION, ranked_ids)

    def test_graph_evidence_can_promote_incoming_related_lesson(self):
        filler = [
            "ADR-0003",
            "ADR-0017",
            "ADR-0018",
            "MEM-20260913T170803Z-A61F2C",
            "ADR-0014",
            "ADR-0020",
            "MEM-20260913T194500Z-8F2C41",
        ]
        ordered = [RETRIEVAL_ADR, *filler, RETRIEVAL_LESSON]
        fake = FakeHybridRetriever(
            [
                make_hit(canonical_id, index, 0.040 - index * 0.001)
                for index, canonical_id in enumerate(ordered, 1)
            ]
        )
        retriever = StructuralRetriever(ROOT, hybrid_retriever=fake)
        ranked = retriever.rank(
            {
                "task": "Reason about retrieval reliability and prior cognition lessons",
                "topics": ["retrieval", "reliability"],
                "now": "2026-09-14T13:30:00Z",
            }
        )
        target = next(hit for hit in ranked if hit.id == RETRIEVAL_LESSON)
        self.assertIsNotNone(target.graph_rank)
        self.assertLessEqual(target.structural_rank, 8)


if __name__ == "__main__":
    unittest.main(verbosity=2)

````
