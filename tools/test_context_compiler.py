from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from context_compiler import (  # noqa: E402
    compile_context_pack,
    evaluate_trigger,
    load_canonical_store,
    load_mandatory_sources,
    load_project_documents,
    non_terminal_obligations,
    normalize_tokens,
    prepare_query,
    query_terms,
)


class ContextCompilerCoreTests(unittest.TestCase):
    def test_normalize_preserves_hyphenated_repository_name_and_components(self):
        tokens = normalize_tokens("Qiven-Foundation scope_exit")
        self.assertEqual(tokens, ("qiven-foundation", "qiven", "foundation", "scope", "exit"))

    def test_prepare_query_fills_optional_lists_without_mutating_input(self):
        source = {"task": "Inspect Foundation"}
        prepared = prepare_query(source)
        self.assertEqual(source, {"task": "Inspect Foundation"})
        self.assertEqual(prepared["task"], "Inspect Foundation")
        for key in ("topics", "scopes", "touches", "signals", "conditions", "changed", "include_ids"):
            self.assertEqual(prepared[key], [])

    def test_prepare_query_rejects_unknown_fields(self):
        with self.assertRaisesRegex(ValueError, "invalid context query"):
            prepare_query({"task": "x", "surprise": True})

    def test_query_terms_are_deterministic_and_do_not_use_signals(self):
        query = prepare_query(
            {
                "task": "Change Vec3f in qiven-math",
                "topics": ["vector-core"],
                "scopes": ["qiven-math"],
                "touches": ["Vec3f"],
                "signals": ["must-not-enter-relevance-terms"],
            }
        )
        terms = query_terms(query)
        self.assertIn("qiven-math", terms)
        self.assertIn("vector-core", terms)
        self.assertNotIn("must-not-enter-relevance-terms", terms)
        self.assertEqual(terms, query_terms(query))

    def test_mandatory_sources_load_in_contract_order(self):
        documents = load_mandatory_sources()
        self.assertEqual(
            [document.path for document in documents],
            [
                "MEMORY-CONSTITUTION.md",
                "collaboration/operating-contract.md",
                "state/current.md",
                "state/active-work.yaml",
            ],
        )

    def test_project_documents_are_stably_sorted(self):
        documents = load_project_documents()
        paths = [document.path for document in documents]
        self.assertEqual(paths, sorted(paths))
        self.assertIn("projects/foundation/README.md", paths)
        self.assertIn("projects/math/README.md", paths)

    def test_canonical_store_loads_indexes_and_nonterminal_obligations(self):
        store = load_canonical_store()
        self.assertIn("decisions", store)
        self.assertIn("memory", store)
        self.assertIn("obligations", store)
        ids = [record.id for record in store["obligations"]]
        self.assertEqual(ids, sorted(ids))
        nonterminal = non_terminal_obligations(store["obligations"])
        self.assertTrue(nonterminal)
        self.assertTrue(all(record.status in {"open", "deferred", "blocked"} for record in nonterminal))
        self.assertNotIn("OBL-20260913T152950Z-A1B2C3", [record.id for record in nonterminal])

    def test_on_touch_matches_explicit_touch(self):
        result = evaluate_trigger(
            {"type": "on_touch", "value": "github-actions/concurrency"},
            {"task": "CI cleanup", "touches": ["github-actions/concurrency"]},
        )
        self.assertEqual(result["result"], "applicable")

    def test_on_touch_does_not_guess_from_weak_overlap(self):
        result = evaluate_trigger(
            {"type": "on_touch", "value": "repeated-downstream-scope-cleanup-patterns"},
            {"task": "Add ScopeExit to Foundation", "touches": []},
        )
        self.assertEqual(result["result"], "not_triggered")

    def test_before_requires_named_boundary(self):
        trigger = {"type": "before", "value": "qiven-gas implementation batch"}
        due = evaluate_trigger(trigger, {"task": "Start qiven-gas implementation batch", "signals": []})
        unknown = evaluate_trigger(trigger, {"task": "Think about gas architecture", "signals": []})
        self.assertEqual(due["result"], "due")
        self.assertEqual(unknown["result"], "unresolved")

    def test_after_accepts_explicit_completion_signal(self):
        result = evaluate_trigger(
            {"type": "after", "value": "Genesis Import"},
            {"task": "Build compiler", "signals": ["Genesis Import complete"]},
        )
        self.assertEqual(result["result"], "due")

    def test_after_uses_closed_ledger_without_inferring_absence(self):
        result = evaluate_trigger(
            {"type": "after", "value": "Context Phase 0 Batch 001"},
            {"task": "Historical check", "signals": []},
        )
        self.assertEqual(result["result"], "due")
        unresolved = evaluate_trigger(
            {"type": "after", "value": "A thing that never closed"},
            {"task": "Historical check", "signals": []},
        )
        self.assertEqual(unresolved["result"], "unresolved")

    def test_on_change_only_uses_changed_set(self):
        trigger = {"type": "on_change", "value": "tools/resolve-python.cmd"}
        no = evaluate_trigger(trigger, {"task": "Discuss resolver", "changed": []})
        yes = evaluate_trigger(trigger, {"task": "Unrelated", "changed": ["tools/resolve-python.cmd"]})
        self.assertEqual(no["result"], "not_triggered")
        self.assertEqual(yes["result"], "applicable")

    def test_on_date_is_reproducible_with_explicit_now(self):
        trigger = {"type": "on_date", "value": "2026-09-14T00:00:00Z"}
        before = evaluate_trigger(
            trigger,
            {"task": "date"},
            now=datetime(2026, 9, 13, 23, 59, tzinfo=timezone.utc),
        )
        after = evaluate_trigger(
            trigger,
            {"task": "date"},
            now=datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(before["result"], "not_triggered")
        self.assertEqual(after["result"], "due")

    def test_on_date_invalid_value_is_unresolved(self):
        result = evaluate_trigger(
            {"type": "on_date", "value": "someday"},
            {"task": "date", "now": "2026-09-14T00:00:00Z"},
        )
        self.assertEqual(result["result"], "unresolved")

    def test_condition_requires_explicit_true_condition(self):
        trigger = {"type": "condition", "value": "multi-repository composition is recurring"}
        no = evaluate_trigger(trigger, {"task": "workspace", "conditions": []})
        yes = evaluate_trigger(
            trigger,
            {"task": "workspace", "conditions": ["multi-repository composition is recurring"]},
        )
        self.assertEqual(no["result"], "not_triggered")
        self.assertEqual(yes["result"], "due")

    def test_manual_trigger_never_auto_fires(self):
        result = evaluate_trigger(
            {"type": "manual", "reason": "owner decision"},
            {"task": "anything", "conditions": ["owner decision"]},
        )
        self.assertEqual(result["result"], "manual")

    def test_foundation_scope_exit_pack_surfaces_boundary_and_deferred_obligation(self):
        pack = compile_context_pack(
            {
                "task": "Add ScopeExit to Foundation",
                "scopes": ["qiven-foundation"],
                "now": "2026-09-14T00:00:00Z",
            }
        )
        project_paths = [item["path"] for item in pack["projects"]]
        decision_ids = [item["id"] for item in pack["decisions"]]
        obligation_ids = [item["id"] for item in pack["obligations"]]
        self.assertIn("projects/foundation/README.md", project_paths)
        self.assertIn("ADR-0007", decision_ids)
        self.assertIn("OBL-20260913T181224Z-A3F690", obligation_ids)
        obligation = next(item for item in pack["obligations"] if item["id"] == "OBL-20260913T181224Z-A3F690")
        self.assertEqual(obligation["trigger"]["result"], "not_triggered")
        self.assertTrue(any(reason["kind"] in {"scope_match", "project_match", "title_match"} for reason in obligation["reasons"]))

    def test_math_vec3f_pack_surfaces_representation_adr(self):
        pack = compile_context_pack(
            {
                "task": "Change Vec3f to alignas(16)",
                "scopes": ["qiven-math"],
                "now": "2026-09-14T00:00:00Z",
            }
        )
        self.assertIn("ADR-0014", [item["id"] for item in pack["decisions"]])

    def test_gas_implementation_boundary_makes_discovery_obligation_due(self):
        boundary = "first detailed industrial-gas domain-model or qiven-gas implementation batch"
        pack = compile_context_pack(
            {
                "task": "Start detailed qiven-gas implementation",
                "scopes": ["qiven-gas"],
                "signals": [boundary],
                "now": "2026-09-14T00:00:00Z",
            }
        )
        obligation = next(item for item in pack["obligations"] if item["id"] == "OBL-20260913T185050Z-21DCBC")
        self.assertEqual(obligation["trigger"]["result"], "due")
        self.assertTrue(any(reason["kind"] == "trigger_due" for reason in obligation["reasons"]))

    def test_explicit_id_selects_unrelated_adr(self):
        pack = compile_context_pack(
            {
                "task": "Unrelated task",
                "include_ids": ["ADR-0014"],
                "now": "2026-09-14T00:00:00Z",
            }
        )
        selected = next(item for item in pack["decisions"] if item["id"] == "ADR-0014")
        self.assertTrue(any(reason["kind"] == "explicit_id" for reason in selected["reasons"]))

    def test_unknown_explicit_id_is_reported(self):
        pack = compile_context_pack(
            {
                "task": "Unknown ID",
                "include_ids": ["ADR-9999"],
                "now": "2026-09-14T00:00:00Z",
            }
        )
        self.assertTrue(any(item["code"] == "unknown-explicit-id" for item in pack["diagnostics"]))

    def test_fixed_now_produces_identical_pack(self):
        query = {
            "task": "Inspect Foundation allocator ownership",
            "scopes": ["qiven-foundation"],
            "now": "2026-09-14T00:00:00Z",
        }
        self.assertEqual(compile_context_pack(query), compile_context_pack(query))


if __name__ == "__main__":
    unittest.main(verbosity=2)
