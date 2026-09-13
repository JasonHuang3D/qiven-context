from __future__ import annotations

from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
COLD_BOOT = ROOT / "tests" / "cold-boot"


class ColdBootContractTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_challenge_is_not_embedded_in_candidate_prompt(self):
        challenge = self.read("tests/cold-boot/challenge.txt").strip()
        prompt = self.read("tests/cold-boot/candidate-prompt.md")
        self.assertRegex(challenge, r"^CB04-[0-9A-F]{8}$")
        self.assertNotIn(challenge, prompt)
        self.assertIn("tests/cold-boot/challenge.txt", prompt)

    def test_candidate_prompt_requires_source_grounded_chat_cold_boot(self):
        prompt = self.read("tests/cold-boot/candidate-prompt.md")
        for required in (
            "BOOTSTRAP.md",
            "Do not use model-native/account memory",
            "Stay in Chat",
            "Do not suggest, trigger, or hand off to Work",
            "Do **not** read `tests/cold-boot/evaluator-rubric.md`",
            "Verify current live refs",
            "If evidence is absent, say so explicitly",
        ):
            self.assertIn(required, prompt)

    def test_bootstrap_retains_required_boot_order(self):
        bootstrap = self.read("BOOTSTRAP.md")
        expected = (
            "MEMORY-CONSTITUTION.md",
            "collaboration/operating-contract.md",
            "state/current.md",
            "state/active-work.yaml",
            "Determine the current task",
            "Load relevant project material",
            "Load relevant non-terminal obligations",
            "Load applicable decisions and rejected alternatives",
            "Verify relevant live repositories",
            "Report inconsistencies before acting",
        )
        positions = [bootstrap.index(item) for item in expected]
        self.assertEqual(positions, sorted(positions))

    def test_batch004_is_active_in_canonical_state(self):
        active = yaml.safe_load(self.read("state/active-work.yaml"))
        self.assertEqual(active["phase"], 0)
        self.assertEqual(active["batch"], 4)
        self.assertEqual(active["status"], "in_progress")
        self.assertEqual(active["objective"], "Cold-Boot Acceptance")
        self.assertEqual(
            active["paused_work"],
            [
                "Foundation managed-drift reconciliation",
                "Foundation Devkit adoption",
                "Math Batch 008 vector algorithms",
            ],
        )

    def test_rubric_covers_all_critical_assertions(self):
        rubric = self.read("tests/cold-boot/evaluator-rubric.md")
        headings = re.findall(r"^### C(\d+) — ", rubric, flags=re.MULTILINE)
        self.assertEqual(headings, [str(i) for i in range(1, 13)])

    def test_rubric_references_existing_canonical_ids(self):
        rubric = self.read("tests/cold-boot/evaluator-rubric.md")
        obligation_index = yaml.safe_load(self.read("obligations/index.yaml"))
        decision_index = yaml.safe_load(self.read("decisions/index.yaml"))
        obligations = {str(item["id"]) for item in obligation_index["records"]}
        decisions = {str(item["id"]) for item in decision_index["records"]}

        required_obligations = {
            "OBL-20260913T152950Z-D4E5F6",
            "OBL-20260913T182954Z-7B4E20",
            "OBL-20260913T182338Z-4F7C19",
            "OBL-20260913T185050Z-21DCBC",
            "OBL-20260913T183819Z-9A4F21",
        }
        required_decisions = {"ADR-0003", "ADR-0020", "ADR-0021"}
        self.assertTrue(required_obligations <= obligations)
        self.assertTrue(required_decisions <= decisions)
        for canonical_id in sorted(required_obligations | required_decisions):
            self.assertIn(canonical_id, rubric)


if __name__ == "__main__":
    unittest.main(verbosity=2)
