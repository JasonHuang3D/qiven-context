# [SEALED] tools/test_retrieval_candidate_bundle.py

> Museum piece (ADR-0040/ADR-0041, sealed 2026-09-21). Original
> location: `tools/test_retrieval_candidate_bundle.py`. Do not execute — this is historical text
> only; the `.md` extension makes accidental execution impossible.

````python
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from context_compiler import load_canonical_store
from context_snapshot import as_snapshot  # noqa: E402
from retrieval_candidate_bundle import (  # noqa: E402
    CANDIDATE_ROLE,
    build_candidate_bundle,
)


class FakeRetriever:
    def __init__(self):
        self.snapshot = as_snapshot(ROOT)
        with self.snapshot.materialize() as frozen:
            self.records = {r.id: r for rows in load_canonical_store(frozen).values() for r in rows}
        self._hits = [
            self._hit("ADR-0003", 1, 4.2, deterministic_rank=1, semantic_rank=2),
            self._hit("MEM-20260913T170803Z-A61F2C", 2, 2.1, deterministic_rank=None, semantic_rank=1),
            self._hit("OBL-20260915T163500Z-9D4C72", 3, 0.4, deterministic_rank=3, semantic_rank=5),
            self._hit("ADR-0004", 4, -0.2, deterministic_rank=4, semantic_rank=7),
        ]

    @staticmethod
    def _hit(canonical_id, rank, score, *, deterministic_rank, semantic_rank):
        return SimpleNamespace(
            id=canonical_id,
            rerank_score=score,
            rerank_rank=rank,
            hybrid_rank=rank + 1,
            deterministic_rank=deterministic_rank,
            semantic_rank=semantic_rank,
            graph_candidate=rank == 3,
            explicit=rank == 1,
        )

    def rank(self, query):
        self.query = dict(query)
        return list(self._hits)


class RetrievalCandidateBundleTests(unittest.TestCase):
    def test_bundle_is_explicitly_untrusted_and_answerability_is_unresolved(self):
        bundle = build_candidate_bundle(
            {"task": "Which Qiven rule applies?", "scopes": ["qiven-test"]},
            FakeRetriever(),
            root=ROOT,
        )
        self.assertEqual(bundle["role"], CANDIDATE_ROLE)
        self.assertEqual(bundle["answerability"], "unresolved")
        self.assertIn("not selected truth", bundle["instruction"])
        self.assertIn("abstain", bundle["instruction"])

    def test_bundle_preserves_rank_order_and_caps_candidates(self):
        bundle = build_candidate_bundle(
            {"task": "Which Qiven rule applies?"},
            FakeRetriever(),
            root=ROOT,
        )
        self.assertEqual(
            [item["id"] for item in bundle["candidates"]],
            ["ADR-0003", "MEM-20260913T170803Z-A61F2C", "OBL-20260915T163500Z-9D4C72"],
        )
        self.assertEqual(bundle["max_candidates"], 3)

    def test_bundle_preserves_canonical_content_and_ranking_provenance(self):
        bundle = build_candidate_bundle(
            {"task": "Which Qiven rule applies?"},
            FakeRetriever(),
            root=ROOT,
            max_candidates=1,
        )
        candidate = bundle["candidates"][0]
        self.assertEqual(candidate["path"], "decisions/ADR-0003.md")
        self.assertIn("Source data remains inspectable", candidate["content"])
        self.assertEqual(candidate["candidate_rank"], 1)
        self.assertEqual(candidate["ranking"]["deterministic_rank"], 1)
        self.assertEqual(candidate["ranking"]["semantic_rank"], 2)
        self.assertTrue(candidate["ranking"]["explicit"])

    def test_invalid_candidate_ceiling_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "max_candidates must be >= 1"):
            build_candidate_bundle(
                {"task": "Which Qiven rule applies?"},
                FakeRetriever(),
                root=ROOT,
                max_candidates=0,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)

````
