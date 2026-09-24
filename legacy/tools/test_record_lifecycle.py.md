# [SEALED] tools/test_record_lifecycle.py

> Museum piece (ADR-0040/ADR-0041, sealed 2026-09-21). Original
> location: `tools/test_record_lifecycle.py`. Do not execute — this is historical text
> only; the `.md` extension makes accidental execution impossible.

````python
"""Lifecycle conformance across real entrypoints; model scoring is deterministic."""
from pathlib import Path
import json
import shutil
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from context_compiler import compile_context_pack, load_canonical_store, prepare_query
from context_pack import render_context_markdown, validate_context_pack
from hybrid_retriever import HybridRetriever, deterministic_rank
from record_lifecycle import KNOWN_STATUSES, is_current, record_is_eligible
from rerank_retriever import RerankedRetriever
from retrieval_candidate_bundle import build_candidate_bundle
from semantic_retriever import SemanticRetriever
from structural_retriever import StructuralRetriever


class Embeddings:
    model_name = "deterministic-lifecycle-fixture"

    def __init__(self):
        self.embedded = []

    def embed_documents(self, texts):
        self.embedded.extend(texts)
        return [[1.0, 0.0] for _ in texts]

    def embed_query(self, text):
        return [1.0, 0.0]


class Scores:
    model_name = "deterministic-lifecycle-fixture"

    def score(self, query, documents):
        # Explicit inspection must survive even a very poor model score.
        return [-100.0 if "status: superseded" in doc else 1.0 for doc in documents]


class LifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="qiven-lifecycle-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        shutil.copytree(ROOT / "schema", cls.root / "schema")
        for path in ("MEMORY-CONSTITUTION.md", "collaboration/operating-contract.md",
                     "state/current.md", "state/active-work.yaml"):
            target = cls.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("fixture\n", encoding="utf-8")
        inputs = {"schema_version": 1, "mandatory": ["MEMORY-CONSTITUTION.md",
                  "collaboration/operating-contract.md", "state/current.md", "state/active-work.yaml"], "views": {}}
        (cls.root / "collaboration/context-inputs.yaml").write_text(yaml.safe_dump(inputs), encoding="utf-8")
        (cls.root / "governance").mkdir()
        rules = {"schema_version": 1, "rules": [{"id": "fixture", "when": {}, "effect": "require",
                 "sources": ["MEMORY-CONSTITUTION.md"]}]}
        (cls.root / "governance/context-constraints.yaml").write_text(yaml.safe_dump(rules), encoding="utf-8")
        cls.by_status = {}
        for category, states in KNOWN_STATUSES.items():
            folder = "memory/records" if category == "memory" else category
            (cls.root / folder).mkdir(parents=True, exist_ok=True)
            entries = []
            for number, status in enumerate(sorted(states), 1):
                prefix = {"decisions": "ADR", "memory": "MEM", "obligations": "OBL"}[category]
                rid = f"ADR-{number:04d}" if prefix == "ADR" else f"{prefix}-20260916T120000Z-{number:06X}"
                cls.by_status[category, status] = rid
                data = {"id": rid, "title": "Lifecycle fixture", "status": status,
                        "scope": ["qiven-test"], "tags": ["lifecycle"], "related": [],
                        "supersedes": [], "superseded_by": [], "completion": "Verified completion",
                        "trigger": {"type": "on_date", "value": "2000-01-01T00:00:00Z"}}
                target = cls.root / folder / f"{rid}.md"
                target.write_text("---\n" + yaml.safe_dump(data) + "---\n# Lifecycle fixture\n", encoding="utf-8")
                entries.append({"id": rid, "file": target.name, "title": data["title"], "status": status})
            (cls.root / category / "index.yaml").write_text(yaml.safe_dump({"records": entries}), encoding="utf-8")
        old = cls.by_status["decisions", "superseded"]
        current = cls.by_status["decisions", "accepted"]
        for rid, field, value in ((old, "superseded_by", current), (current, "supersedes", old),
                                  (current, "related", old)):
            target = cls.root / "decisions" / f"{rid}.md"
            _, front, body = target.read_text().split("---", 2)
            data = yaml.safe_load(front)
            data[field] = [value]
            target.write_text("---\n" + yaml.safe_dump(data) + "---" + body, encoding="utf-8")
        cls.records = [r for rows in load_canonical_store(cls.root).values() for r in rows]
        cls.current = {r.id for r in cls.records if is_current(r.category, r.status)}
        cls.all_ids = {r.id for r in cls.records}

    def query(self, **extra):
        return {"task": "Review lifecycle", "scopes": ["qiven-test"],
                "now": "2026-09-16T00:00:00Z", **extra}

    def stack(self):
        backend = Embeddings()
        semantic = SemanticRetriever(self.root, backend=backend)
        hybrid = HybridRetriever(self.root, semantic_retriever=semantic)
        rerank = RerankedRetriever(self.root, hybrid_retriever=hybrid, reranker_backend=Scores())
        structural = StructuralRetriever(self.root, hybrid_retriever=hybrid)
        return backend, semantic, hybrid, rerank, structural

    def check_entrypoints(self, query, expected):
        pack = compile_context_pack(query, self.root)
        validate_context_pack(pack, self.root)
        rows = [r for category in ("decisions", "memory", "obligations") for r in pack[category]]
        self.assertEqual({r["id"] for r in rows}, expected)
        _, semantic, hybrid, rerank, structural = self.stack()
        for name, hits in (("deterministic", deterministic_rank(query, self.root)),
                           ("semantic", semantic.rank(query)), ("hybrid", hybrid.rank(query)),
                           ("rerank", rerank.rank(query)), ("structural", structural.rank(query))):
            with self.subTest(entrypoint=name):
                self.assertEqual({h.id for h in hits}, expected)
        bundle = build_candidate_bundle(query, rerank, root=self.root, max_candidates=100)
        self.assertEqual({r["id"] for r in bundle["candidates"]}, expected)
        for r in rows + bundle["candidates"]:
            self.assertEqual(r["current_eligible"], r["id"] in self.current)
        return pack, bundle

    def test_status_policy_matches_schema_and_independent_current_contract(self):
        expected = {"decisions": {"accepted"}, "memory": {"active"},
                    "obligations": {"open", "deferred", "blocked"}}
        schemas = {"decisions": "adr", "memory": "memory-record", "obligations": "obligation"}
        for category, schema in schemas.items():
            data = json.loads((ROOT / "schema" / f"{schema}.schema.json").read_text())
            statuses = set(data["properties"]["status"]["enum"])
            self.assertEqual(statuses, KNOWN_STATUSES[category])
            for status in statuses:
                self.assertEqual(is_current(category, status), status in expected[category])

    def test_default_current_filters_every_noncurrent_state_and_relation_expansion(self):
        self.check_entrypoints(self.query(), self.current)

    def test_history_is_inclusive_without_promoting_records(self):
        pack, _ = self.check_entrypoints(self.query(record_mode="history"), self.all_ids)
        for row in pack["obligations"]:
            if not row["current_eligible"]:
                self.assertEqual(row["trigger"]["result"], "inactive")
        self.assertIn("current_eligible=False", render_context_markdown(pack, self.root))

    def test_every_explicit_noncurrent_id_is_inspectable_without_broadening_other_history(self):
        for rid in sorted(self.all_ids - self.current):
            with self.subTest(id=rid):
                self.check_entrypoints(self.query(include_ids=[rid]), self.current | {rid})

    def test_supersession_links_survive_pack_and_candidate_serialization(self):
        old = self.by_status["decisions", "superseded"]
        new = self.by_status["decisions", "accepted"]
        pack, bundle = self.check_entrypoints(self.query(include_ids=[old]), self.current | {old})
        for rows in (pack["decisions"], bundle["candidates"]):
            row = next(r for r in rows if r["id"] == old)
            self.assertEqual(row["status"], "superseded")
            self.assertEqual(row["superseded_by"], [new])
            self.assertFalse(row["current_eligible"])

    def test_explicit_low_rank_record_survives_candidate_ceiling(self):
        _, _, _, rerank, _ = self.stack()
        old = self.by_status["decisions", "superseded"]
        bundle = build_candidate_bundle(self.query(include_ids=[old]), rerank, root=self.root, max_candidates=1)
        self.assertEqual([r["id"] for r in bundle["candidates"]], [old])
        with self.assertRaisesRegex(ValueError, "explicit IDs exceed"):
            build_candidate_bundle(self.query(include_ids=[old, self.by_status["memory", "retracted"]]),
                                   rerank, root=self.root, max_candidates=1)

    def test_history_query_does_not_contaminate_reused_current_retriever(self):
        backend, semantic, hybrid, rerank, structural = self.stack()
        self.assertEqual(len(backend.embedded), len(self.current))
        for retriever in (semantic, hybrid, rerank, structural):
            retriever.rank(self.query(record_mode="history"))
            self.assertEqual({h.id for h in retriever.rank(self.query())}, self.current)
        self.assertEqual(len(backend.embedded), len(self.all_ids))

    def test_unknown_explicit_id_is_reported_without_substitution(self):
        query = self.query(include_ids=["ADR-9999"])
        pack, bundle = self.check_entrypoints(query, self.current)
        self.assertTrue(any(d["code"] == "unknown-explicit-id" for d in pack["diagnostics"]))
        self.assertEqual(bundle["diagnostics"], [{"code": "unknown-explicit-id", "id": "ADR-9999"}])

    def test_unknown_mode_or_status_is_rejected(self):
        with self.assertRaises(ValueError):
            prepare_query(self.query(record_mode="latest-ish"), self.root)
        with self.assertRaises(ValueError):
            is_current("memory", "unknown")

    def test_repository_default_pack_no_longer_includes_superseded_foundation_adr(self):
        pack = compile_context_pack({"task": "Add ScopeExit to Foundation", "scopes": ["qiven-foundation"]})
        ids = {r["id"] for r in pack["decisions"]}
        self.assertNotIn("ADR-0007", ids)
        self.assertIn("ADR-0024", ids)


if __name__ == "__main__":
    unittest.main(verbosity=2)

````
