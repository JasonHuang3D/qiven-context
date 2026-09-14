from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from context_gateway import prepare_context, task_fingerprint, validate_context_lease  # noqa: E402
from retrieval_benchmark import evaluate_benchmark, load_benchmark  # noqa: E402
from semantic_retriever import SemanticRetriever, cosine_similarity  # noqa: E402


FIXED_REF = "a" * 40
FIXED_NOW = "2026-09-14T13:30:00Z"


class ContextLeaseTests(unittest.TestCase):
    def query(self, task: str = "Inspect retrieval") -> dict:
        return {"task": task, "topics": ["retrieval"], "now": FIXED_NOW}

    def test_prepare_context_emits_valid_proof_of_retrieval(self):
        pack, lease = prepare_context(self.query(), ROOT, canonical_ref=FIXED_REF)
        self.assertTrue(lease["retrieval_invoked"])
        self.assertTrue(lease["source_clean"])
        self.assertEqual(lease["policy"], "mandatory_turn_preflight")
        self.assertEqual(lease["transition"], "initial")
        self.assertEqual(lease["canonical_ref"], FIXED_REF)
        self.assertEqual(lease["task"], pack["query"]["task"])
        validate_context_lease(lease, ROOT)

    def test_same_task_refresh_still_invokes_retrieval_and_gets_new_lease(self):
        query = self.query("Continue the same retrieval task")
        first_pack, first = prepare_context(query, ROOT, canonical_ref=FIXED_REF)
        with mock.patch(
            "context_gateway.compile_context_pack",
            wraps=__import__("context_gateway").compile_context_pack,
        ) as compiler:
            second_pack, second = prepare_context(
                query,
                ROOT,
                previous_lease=first,
                canonical_ref=FIXED_REF,
            )
        self.assertEqual(compiler.call_count, 1)
        self.assertTrue(second["retrieval_invoked"])
        self.assertEqual(second["transition"], "same_task_refresh")
        self.assertEqual(second["previous_lease_id"], first["lease_id"])
        self.assertNotEqual(second["lease_id"], first["lease_id"])
        self.assertEqual(first_pack["query"], second_pack["query"])

    def test_changed_task_is_classified_as_transition(self):
        _, first = prepare_context(self.query("Operator dogfood"), ROOT, canonical_ref=FIXED_REF)
        _, second = prepare_context(
            self.query("Diagnose Windows interpreter trust"),
            ROOT,
            previous_lease=first,
            canonical_ref=FIXED_REF,
        )
        self.assertEqual(second["transition"], "task_transition")
        self.assertNotEqual(second["task_fingerprint"], first["task_fingerprint"])

    def test_now_does_not_change_task_identity(self):
        first = self.query("Stable task")
        second = dict(first)
        second["now"] = "2026-09-14T14:30:00Z"
        self.assertEqual(task_fingerprint(first, ROOT), task_fingerprint(second, ROOT))

    def test_invalid_previous_lease_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid context lease"):
            prepare_context(
                self.query(),
                ROOT,
                previous_lease={"lease_id": "fake"},
                canonical_ref=FIXED_REF,
            )


class FakeEmbeddingBackend:
    model_name = "fake-semantic-model"

    def embed_documents(self, texts):
        count = len(texts)
        return [[1.0, float(index + 1) / max(1, count)] for index in range(count)]

    def embed_query(self, text):
        return [1.0, 0.0]


class StubSemanticRetriever:
    model_name = "stub"

    def __init__(self, selected_ids):
        self.selected_ids = set(selected_ids)

    def select_ids(self, query, *, top_k=8):
        return set(sorted(self.selected_ids)[:top_k])


class SemanticRetrieverTests(unittest.TestCase):
    def test_cosine_similarity_handles_identical_and_orthogonal_vectors(self):
        self.assertAlmostEqual(cosine_similarity([1.0, 0.0], [1.0, 0.0]), 1.0)
        self.assertAlmostEqual(cosine_similarity([1.0, 0.0], [0.0, 1.0]), 0.0)

    def test_semantic_selection_is_bounded_and_deterministic_without_fastembed(self):
        retriever = SemanticRetriever(ROOT, backend=FakeEmbeddingBackend())
        query = {"task": "semantic fixture", "topics": ["retrieval"], "now": FIXED_NOW}
        first = retriever.select_ids(query, top_k=3)
        second = retriever.select_ids(query, top_k=3)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 3)

    def test_semantic_benchmark_path_uses_injected_retriever(self):
        benchmark = {
            "schema_version": 1,
            "name": "semantic-fixture",
            "thresholds": {
                "critical_case_recall_min": 1.0,
                "required_id_recall_min": 1.0,
                "forbidden_hits_max": 0,
                "mean_extra_ids_max": 8.0,
            },
            "cases": [
                {
                    "id": "semantic",
                    "critical": True,
                    "query": {"task": "fixture", "now": FIXED_NOW},
                    "required_ids": ["ADR-0022"],
                    "forbidden_ids": ["ADR-0014"],
                    "allowed_extra_ids": [],
                }
            ],
        }
        result = evaluate_benchmark(
            benchmark,
            ROOT,
            mode="semantic",
            semantic_retriever=StubSemanticRetriever({"ADR-0022"}),
        )
        self.assertEqual(result["mode"], "semantic")
        self.assertEqual(result["metrics"]["required_id_recall"], 1.0)
        self.assertEqual(result["metrics"]["forbidden_hits"], 0)
        self.assertTrue(result["pass"])


class RetrievalBenchmarkTests(unittest.TestCase):
    def test_frozen_open_set_benchmark_validates(self):
        benchmark = load_benchmark(ROOT / "benchmarks/retrieval/open-set-v1.yaml", ROOT)
        self.assertEqual(benchmark["name"], "open-set-retrieval-v1")
        self.assertGreaterEqual(len(benchmark["cases"]), 8)
        self.assertEqual(benchmark["thresholds"]["critical_case_recall_min"], 1.0)
        self.assertEqual(benchmark["thresholds"]["forbidden_hits_max"], 0)

    def test_benchmark_measurement_reports_current_baseline_without_moving_thresholds(self):
        benchmark = load_benchmark(ROOT / "benchmarks/retrieval/open-set-v1.yaml", ROOT)
        result = evaluate_benchmark(benchmark, ROOT)
        self.assertEqual(result["thresholds"], benchmark["thresholds"])
        self.assertEqual(len(result["cases"]), len(benchmark["cases"]))
        self.assertGreaterEqual(result["metrics"]["required_id_recall"], 0.0)
        self.assertLessEqual(result["metrics"]["required_id_recall"], 1.0)
        self.assertIn(result["pass"], {True, False})

    def test_benchmark_harness_can_prove_a_perfect_explicit_id_fixture(self):
        benchmark = {
            "schema_version": 1,
            "name": "fixture",
            "thresholds": {
                "critical_case_recall_min": 1.0,
                "required_id_recall_min": 1.0,
                "forbidden_hits_max": 0,
                "mean_extra_ids_max": 20.0,
            },
            "cases": [
                {
                    "id": "explicit",
                    "critical": True,
                    "query": {
                        "task": "fixture",
                        "include_ids": ["ADR-0022"],
                        "now": FIXED_NOW,
                    },
                    "required_ids": ["ADR-0022"],
                    "forbidden_ids": [],
                    "allowed_extra_ids": [],
                }
            ],
        }
        result = evaluate_benchmark(benchmark, ROOT)
        self.assertEqual(result["metrics"]["required_id_recall"], 1.0)
        self.assertTrue(result["cases"][0]["critical_pass"])

    def test_benchmark_schema_rejects_threshold_mutation_shape(self):
        source = yaml.safe_load(
            (ROOT / "benchmarks/retrieval/open-set-v1.yaml").read_text(encoding="utf-8")
        )
        del source["thresholds"]["required_id_recall_min"]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "broken.yaml"
            path.write_text(yaml.safe_dump(source, sort_keys=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid retrieval benchmark"):
                load_benchmark(path, ROOT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
