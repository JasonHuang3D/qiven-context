# [SEALED] tools/test_context_acceptance.py

> Museum piece (ADR-0040/ADR-0041, sealed 2026-09-21). Original
> location: `tools/test_context_acceptance.py`. Do not execute — this is historical text
> only; the `.md` extension makes accidental execution impossible.

````python
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from context_compiler import compile_context_pack  # noqa: E402
from context_pack import render_context_markdown, validate_context_pack  # noqa: E402


FIXTURES = ROOT / "tests" / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def ids(pack: dict, section: str) -> set[str]:
    return {str(item["id"]) for item in pack[section] if "id" in item}


class ContextCompilerAcceptanceTests(unittest.TestCase):
    def test_foundation_pack_is_selective_and_explainable(self):
        pack = compile_context_pack(load_fixture("context-query-foundation-scope-exit.json"))
        validate_context_pack(pack)

        self.assertIn("projects/foundation/README.md", {item["path"] for item in pack["projects"]})
        self.assertIn("ADR-0024", ids(pack, "decisions"))
        self.assertIn("OBL-20260913T181224Z-A3F690", ids(pack, "obligations"))

        self.assertNotIn("projects/gas/README.md", {item["path"] for item in pack["projects"]})
        self.assertNotIn("projects/robotics/README.md", {item["path"] for item in pack["projects"]})
        self.assertNotIn("ADR-0020", ids(pack, "decisions"))
        self.assertNotIn("OBL-20260913T185050Z-21DCBC", ids(pack, "obligations"))
        self.assertNotIn("OBL-20260913T183819Z-9A4F21", ids(pack, "obligations"))

        for section in ("projects", "decisions", "memory", "obligations"):
            for item in pack[section]:
                self.assertTrue(item["reasons"], f"{section} item lacks selection reasons: {item}")

    def test_math_pack_recalls_representation_contract_without_cross_domain_dump(self):
        pack = compile_context_pack(load_fixture("context-query-math-vec3f.json"))
        validate_context_pack(pack)

        self.assertIn("projects/math/README.md", {item["path"] for item in pack["projects"]})
        self.assertIn("ADR-0014", ids(pack, "decisions"))
        self.assertIn("MEM-20260913T182954Z-3F8C71", ids(pack, "memory"))
        self.assertNotIn("ADR-0020", ids(pack, "decisions"))
        self.assertNotIn("OBL-20260913T185050Z-21DCBC", ids(pack, "obligations"))
        self.assertNotIn("OBL-20260913T182338Z-4F7C19", ids(pack, "obligations"))

    def test_gas_pack_makes_source_recovery_boundary_due_without_native_noise(self):
        pack = compile_context_pack(load_fixture("context-query-gas-domain-model.json"))
        validate_context_pack(pack)

        self.assertIn("projects/gas/README.md", {item["path"] for item in pack["projects"]})
        self.assertIn("ADR-0020", ids(pack, "decisions"))
        obligation = next(
            item for item in pack["obligations"] if item["id"] == "OBL-20260913T185050Z-21DCBC"
        )
        self.assertEqual(obligation["trigger"]["result"], "due")
        self.assertTrue(any(reason["kind"] == "trigger_due" for reason in obligation["reasons"]))
        self.assertNotIn("OBL-20260913T181224Z-A3F690", ids(pack, "obligations"))
        self.assertNotIn("OBL-20260913T182954Z-7B4E20", ids(pack, "obligations"))

    def test_devkit_adoption_pack_preserves_closed_drift_guardrail_without_reopening_work(self):
        pack = compile_context_pack(load_fixture("context-query-devkit-adoption.json"))
        validate_context_pack(pack)

        self.assertIn("ADR-0012", ids(pack, "decisions"))
        self.assertIn("projects/devkit/README.md", {item["path"] for item in pack["projects"]})
        self.assertNotIn("OBL-20260913T182338Z-4F7C19", ids(pack, "obligations"))
        markdown = render_context_markdown(pack).casefold()
        self.assertIn("thirteen", markdown)
        self.assertIn("semantic disposition", markdown)

    def test_math_resume_pack_preserves_closed_batch_history_without_reopening_work(self):
        pack = compile_context_pack(
            {
                "task": "Review completed Math Batch 008 vector algorithms",
                "scopes": ["qiven-math"],
                "now": "2026-09-14T09:20:00Z",
            }
        )
        validate_context_pack(pack)

        self.assertIn("projects/math/README.md", {item["path"] for item in pack["projects"]})
        self.assertNotIn("OBL-20260913T182954Z-7B4E20", ids(pack, "obligations"))
        markdown = render_context_markdown(pack).casefold()
        self.assertIn("batch 008", markdown)
        self.assertIn("full cross-platform", markdown)

    def test_specific_on_touch_trigger_does_not_fire_from_broad_project_scope(self):
        broad = compile_context_pack(
            {
                "task": "Inspect Foundation APIs",
                "scopes": ["qiven-foundation"],
                "now": "2026-09-14T00:00:00Z",
            }
        )
        obligation = next(
            item for item in broad["obligations"] if item["id"] == "OBL-20260913T181224Z-9E27A4"
        )
        self.assertEqual(obligation["trigger"]["result"], "unresolved")

        exact = compile_context_pack(
            {
                "task": "Design structured recoverable status for Foundation",
                "scopes": ["qiven-foundation"],
                "touches": ["qiven-foundation/recoverable-structured-error-contract"],
                "now": "2026-09-14T00:00:00Z",
            }
        )
        obligation = next(
            item for item in exact["obligations"] if item["id"] == "OBL-20260913T181224Z-9E27A4"
        )
        self.assertEqual(obligation["trigger"]["result"], "applicable")

    def test_workspace_condition_remains_explicit(self):
        query = {
            "task": "Create qiven-workspace",
            "topics": ["workspace"],
            "now": "2026-09-14T00:00:00Z",
        }
        pack = compile_context_pack(query)
        obligation = next(
            item for item in pack["obligations"] if item["id"] == "OBL-20260913T183819Z-2C7A11"
        )
        self.assertEqual(obligation["trigger"]["result"], "unresolved")

        query["conditions"] = [
            "multi-native-repository version composition or coordinated validation becomes recurring manual coordination work"
        ]
        due_pack = compile_context_pack(query)
        due = next(
            item for item in due_pack["obligations"] if item["id"] == "OBL-20260913T183819Z-2C7A11"
        )
        self.assertEqual(due["trigger"]["result"], "due")

    def test_fixed_fixture_is_reproducible_as_manifest_and_markdown(self):
        query = load_fixture("context-query-foundation-scope-exit.json")
        first = compile_context_pack(query)
        second = compile_context_pack(query)
        self.assertEqual(first, second)
        self.assertEqual(render_context_markdown(first), render_context_markdown(second))

    def test_cli_emits_schema_valid_json_and_source_grounded_markdown(self):
        fixture = FIXTURES / "context-query-foundation-scope-exit.json"
        with tempfile.TemporaryDirectory(prefix="qiven-context-acceptance-") as temp:
            prefix = Path(temp) / "foundation"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "compile_context.py"),
                    "--query",
                    str(fixture),
                    "--output-prefix",
                    str(prefix),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout)
            json_path = prefix.with_suffix(".json")
            markdown_path = prefix.with_suffix(".md")
            self.assertTrue(json_path.is_file())
            self.assertTrue(markdown_path.is_file())

            pack = json.loads(json_path.read_text(encoding="utf-8"))
            validate_context_pack(pack)
            markdown = markdown_path.read_text(encoding="utf-8")
            self.assertIn("Source: `decisions/ADR-0024.md`", markdown)
            self.assertIn("OBL-20260913T181224Z-A3F690", markdown)
            self.assertIn("Selection:", markdown)
            self.assertIn("Trigger:", markdown)


if __name__ == "__main__":
    unittest.main(verbosity=2)

````
