"""R1 semantic failure modes, tested together after the implementation batch."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from context_compiler import compile_context_pack, evaluate_trigger, prepare_query
from context_pack import render_context_markdown, validate_context_pack
from context_snapshot import SourceSnapshot, canonical_json
from hybrid_retriever import HybridRetriever
from semantic_retriever import SemanticRetriever
from rerank_retriever import RerankedRetriever
from retrieval_candidate_bundle import build_candidate_bundle


class Embeddings:
    model_name = "r1-interface-fixture"
    def embed_documents(self, texts):
        return [[1.0, 0.0] for _ in texts]
    def embed_query(self, text):
        return [1.0, 0.0]


class Scores:
    model_name = "r1-interface-fixture"
    def score(self, query, documents):
        return [-100 if "DCR" in text else 1.0 for text in documents]


class R1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = SourceSnapshot.capture(ROOT)

    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="qiven-r1-fixture-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        for path, content in self.baseline.files.items():
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)

    def query(self, **extra):
        return {"task": "Review Context architecture", "scopes": ["qiven-context"],
                "now": "2026-09-17T00:00:00Z", **extra}

    def retriever(self, snapshot):
        semantic = SemanticRetriever(snapshot, backend=Embeddings())
        hybrid = HybridRetriever(snapshot, semantic_retriever=semantic)
        return RerankedRetriever(snapshot, hybrid_retriever=hybrid, reranker_backend=Scores())

    def test_mandatory_view_closure_is_shared_with_candidate_bundle(self):
        snapshot = SourceSnapshot.capture(self.root)
        query = self.query(view="chatgpt-jason")
        pack = compile_context_pack(query, snapshot)
        bundle = build_candidate_bundle(query, self.retriever(snapshot), root=snapshot, max_candidates=1)
        expected = {"governance/authority.yaml", "views/chatgpt-jason.yaml",
                    "views/environments/jasonpc.yaml", "views/workflows/chatgpt-jason-local-execution.md",
                    "collaboration/software-engineering-philosophy.md", "state/roadmap.yaml"}
        for output in (pack, bundle):
            self.assertTrue(expected <= {r["path"] for r in output["mandatory_sources"]})
            self.assertEqual(output["authorization"], "not_granted")
        self.assertEqual(pack["snapshot"], bundle["snapshot"])

    def test_missing_mandatory_source_fails_even_for_unrelated_task(self):
        (self.root / "governance/authority.yaml").unlink()
        with self.assertRaisesRegex(FileNotFoundError, "mandatory"):
            compile_context_pack({"task": "unrelated"}, self.root)

    def test_unknown_view_and_broken_view_reference_fail(self):
        with self.assertRaisesRegex(ValueError, "unknown ContextView"):
            compile_context_pack(self.query(view="unregistered"), self.root)
        (self.root / "views/environments/jasonpc.yaml").unlink()
        with self.assertRaises(FileNotFoundError):
            compile_context_pack(self.query(view="chatgpt-jason"), self.root)

    def test_constraint_survives_top1_and_is_not_permission(self):
        snapshot = SourceSnapshot.capture(self.root)
        query = self.query(operation={"action": "validate", "target": "jasonpc", "channel": "remote-ai"})
        bundle = build_candidate_bundle(query, self.retriever(snapshot), root=snapshot, max_candidates=1)
        self.assertLessEqual(len(bundle["candidates"]), 1)
        rule = next(r for r in bundle["constraints"]["rules"] if r["id"] == "jasonpc-remote-mutation-suspension")
        self.assertEqual(rule["applicability"], "applicable")
        self.assertTrue(bundle["constraints"]["prohibited"])
        self.assertTrue(all(p in bundle["source_contents"] for p in rule["sources"]))
        self.assertEqual(bundle["authorization"], "not_granted")

    def test_unknown_operation_retains_unresolved_constraint(self):
        pack = compile_context_pack(self.query(), self.root)
        rule = next(r for r in pack["constraints"]["rules"] if r["id"] == "jasonpc-remote-mutation-suspension")
        self.assertEqual(rule["applicability"], "unresolved")
        self.assertTrue(rule["sources"])
        self.assertEqual(pack["readiness"], "review_required")

    def test_missing_constraint_evidence_fails_closed(self):
        (self.root / "collaboration/context-validation.md").unlink()
        with self.assertRaisesRegex(FileNotFoundError, "constraint source"):
            compile_context_pack(self.query(operation={"action": "merge"}), self.root)

    def test_tiny_budget_fails_without_truncating_protected_material(self):
        with self.assertRaisesRegex(ValueError, "budget cannot contain"):
            compile_context_pack(self.query(max_context_bytes=1), self.root)
        snapshot = SourceSnapshot.capture(self.root)
        with self.assertRaisesRegex(ValueError, "budget cannot contain"):
            build_candidate_bundle(self.query(max_context_bytes=1), self.retriever(snapshot), root=snapshot)

    def test_evidence_preserves_all_metadata_and_original_source(self):
        rid = "MEM-20260913T170803Z-A61F2C"
        pack = compile_context_pack(self.query(include_ids=[rid]), self.root)
        row = next(r for r in pack["memory"] if r["id"] == rid)
        evidence = row["evidence"]
        raw = (self.root / row["path"]).read_text(encoding="utf-8")
        original = yaml.safe_load(raw.split("---", 2)[1])
        self.assertEqual(evidence["metadata"], original)
        for key in ("kind", "epistemic", "temporal", "sources", "supersedes", "superseded_by"):
            self.assertIn(key, evidence["metadata"])
        self.assertEqual(evidence["source"]["content"], raw)
        validate_context_pack(pack, self.root)

    def test_render_uses_selected_snapshot_after_working_source_changes(self):
        pack = compile_context_pack(self.query(include_ids=["ADR-0003"]), self.root)
        before = render_context_markdown(pack, self.root)
        (self.root / "decisions/ADR-0003.md").write_text("# incompatible replacement\n", encoding="utf-8")
        self.assertEqual(render_context_markdown(pack, self.root), before)

    def test_payload_tampering_is_detected(self):
        pack = compile_context_pack(self.query(include_ids=["ADR-0003"]), self.root)
        corrupt = deepcopy(pack)
        corrupt["source_contents"]["decisions/ADR-0003.md"]["content"] += "tampered"
        with self.assertRaisesRegex(ValueError, "snapshot evidence mismatch"):
            render_context_markdown(corrupt, self.root)
        corrupt = deepcopy(pack)
        row = next(r for r in corrupt["decisions"] if r["id"] == "ADR-0003")
        row["evidence"]["metadata"]["status"] = "rejected"
        with self.assertRaisesRegex(ValueError, "interpretation differs"):
            render_context_markdown(corrupt, self.root)

    def test_reused_retriever_remains_bound_to_old_snapshot(self):
        snapshot = SourceSnapshot.capture(self.root)
        retriever = self.retriever(snapshot)
        query = self.query(include_ids=["ADR-0003"])
        before = build_candidate_bundle(query, retriever, root=self.root)
        path = self.root / "decisions/ADR-0003.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nnew observation\n", encoding="utf-8")
        after = build_candidate_bundle(query, retriever, root=self.root)
        self.assertEqual(before, after)
        self.assertNotEqual(SourceSnapshot.capture(self.root).id, snapshot.id)

    def test_git_capture_uses_one_commit_and_rejects_dirty_default(self):
        def git(*args):
            return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.STDOUT).decode().strip()
        git("init", "-q")
        git("add", ".")
        git("-c", "user.name=Context Test Fixture", "-c", "user.email=fixture@example.invalid",
            "-c", "commit.gpgsign=false", "commit", "-qm", "fixture")
        snapshot = SourceSnapshot.capture(self.root)
        self.assertEqual(snapshot.commit, git("rev-parse", "HEAD"))
        (self.root / "MEMORY-CONSTITUTION.md").write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "sources differ"):
            SourceSnapshot.capture(self.root)
        self.assertEqual(SourceSnapshot.capture(self.root, ref=snapshot.commit).id, snapshot.id)

    def test_missing_false_and_conflicting_conditions_remain_distinct(self):
        trigger = {"type": "condition", "value": "host accepted"}
        self.assertEqual(evaluate_trigger(trigger, {"task": "x"})["result"], "unresolved")
        self.assertEqual(evaluate_trigger(trigger, {"task": "x", "negative_conditions": ["host accepted"]})["result"], "not_triggered")
        self.assertEqual(evaluate_trigger(trigger, {"task": "x", "conditions": ["not host accepted"]})["result"], "unresolved")
        self.assertEqual(evaluate_trigger(trigger, {"task": "x", "conditions": ["host accepted"],
                         "negative_conditions": ["host accepted"]})["result"], "unresolved")

    def test_closed_world_requires_explicit_completeness_and_evidence(self):
        query = self.query(conditions=[], complete_inputs=["conditions"])
        with self.assertRaisesRegex(ValueError, "evidence reference"):
            prepare_query(query, self.root)
        query["input_evidence"] = {"conditions": ["fixture: exhaustive checked conditions"]}
        prepared = prepare_query(query, self.root)
        self.assertEqual(evaluate_trigger({"type": "condition", "value": "missing"}, prepared)["result"], "not_triggered")
        for kind in ("on_touch", "on_change"):
            self.assertEqual(evaluate_trigger({"type": kind, "value": "missing"}, self.query())["result"], "unresolved")

    def test_fixed_snapshot_query_and_clock_reproduce_identical_payload(self):
        snapshot = SourceSnapshot.capture(self.root)
        self.assertEqual(canonical_json(compile_context_pack(self.query(), snapshot)),
                         canonical_json(compile_context_pack(self.query(), snapshot)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
