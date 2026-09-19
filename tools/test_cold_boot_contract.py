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

    def front(self, relative: str) -> dict:
        text=self.read(relative); raw,_=text[4:].split("\n---\n",1); return yaml.safe_load(raw)

    def test_historical_batch004_challenge_remains_reproducible(self):
        challenge=self.read("tests/cold-boot/challenge.txt").strip(); prompt=self.read("tests/cold-boot/candidate-prompt.md")
        self.assertRegex(challenge,r"^CB04-[0-9A-F]{8}$"); self.assertNotIn(challenge,prompt); self.assertIn("tests/cold-boot/challenge.txt",prompt)

    def test_bootstrap_uses_v2_remote_authority_material_order_and_context_view(self):
        bootstrap=self.read("BOOTSTRAP.md")
        expected=(
            "canonical GitHub repository",
            "MEMORY-CONSTITUTION.md",
            "governance/authority.yaml",
            "collaboration/operating-contract.md",
            "collaboration/software-engineering-philosophy.md",
            "collaboration/context-operating-model.md",
            "state/current.md",
            "Resolve the applicable ContextView",
            "latest non-legacy session checkpoint",
            "Determine the current task",
            "Run task-specific retrieval",
            "Verify live GitHub/CI/runtime/environment facts",
            "Report and classify any inconsistency",
        )
        positions=[bootstrap.index(item) for item in expected]; self.assertEqual(positions,sorted(positions))
        self.assertIn("views/chatgpt-jason.yaml",bootstrap)
        self.assertIn("ContextView files tailor interaction, environment, and workflow",bootstrap)
        self.assertIn("Repeat task-specific retrieval whenever the conversation materially changes",bootstrap)
        self.assertIn("Local repositories are working copies",bootstrap)
        self.assertIn("Never invent missing history",bootstrap)

    def test_batch004_historical_completion_survives_v2_without_current_state_duplication(self):
        active=yaml.safe_load(self.read("state/active-work.yaml")); self.assertEqual(active["schema_version"],2)
        gate=self.front("obligations/OBL-20260913T152950Z-D4E5F6.md"); self.assertEqual(gate["status"],"done")
        self.assertTrue((ROOT/"evidence/audits/cold-boot-batch004-run001.md").is_file())
        self.assertTrue((ROOT/"evidence/audits/context-phase0-batch004-closeout.md").is_file())

    def test_project_continuity_contract_covers_v2_reconstruction_without_fresh_human_gate(self):
        contract=self.read("collaboration/project-continuity-acceptance.md")
        for required in (
            "fresh capable LLM/agent",
            "fresh session",
            "authorized human operator may be the existing operator or a fresh operator",
            "current governance trust boundary",
            "latest accepted engineering checkpoint",
            "current unaccepted candidate",
            "active blockers",
            "superseded, and legacy cognition",
            "next valid engineering action",
            "green CI",
            "semantic acceptance",
        ):
            self.assertIn(required,contract)
        self.assertNotIn("fresh authorized human operator with no prior Qiven conversation",contract)
        self.assertIn("human-succession-acceptance.md",contract)

    def test_human_succession_is_separate_higher_order_contract(self):
        contract=self.read("collaboration/human-succession-acceptance.md")
        for required in (
            "fresh authorized human operator",
            "no prior private Qiven knowledge",
            "does not bootstrap or self-grant authority",
            "not a routine prerequisite for every Context release",
        ):
            self.assertIn(required,contract)

    def test_operator_human_contract_is_cross_platform_and_view_bound(self):
        contract=self.read("collaboration/human-facing-executable-contract.md")
        for required in (
            "Qiven Operator",
            "[RUN]",
            "[WAIT]",
            "[ OK ]",
            "[FAIL]",
            "No file extension is a project-level human-interface requirement",
            "active ContextView",
            "views/chatgpt-jason.yaml",
        ):
            self.assertIn(required,contract)
        self.assertNotIn("A human-facing `.cmd` or `.bat` entrypoint must assume it may be double-clicked",contract)

    def test_context_view_separates_project_truth_from_jasonpc_workflow(self):
        model=self.read("collaboration/context-operating-model.md")
        self.assertIn("ContextView<Agent, Human>",model)
        self.assertIn("Environment and workflow are view-dependent",model)
        self.assertIn("views/",model)

        view=yaml.safe_load(self.read("views/chatgpt-jason.yaml"))
        self.assertEqual(view["id"],"chatgpt-jason")
        self.assertEqual(view["human"]["governance_principal"],"github:JasonHuang3D")
        self.assertEqual(view["agent"]["family"],"ChatGPT")
        self.assertFalse(view["project_context"]["override_allowed"])
        self.assertEqual(view["workflows"]["local_execution"],"views/workflows/chatgpt-jason-local-execution.md")
        self.assertIn("views/environments/jasonpc.yaml",view["environments"])

        env=yaml.safe_load(self.read("views/environments/jasonpc.yaml"))
        self.assertEqual(env["workspace"]["qiven_root"],r"D:\JasonWork")
        self.assertEqual(env["managed_environment"]["root"],r"C:\Env")
        self.assertEqual(env["network"]["vpn_client"],"Clash Verge")
        self.assertEqual(env["engineering_stack"]["exact_versions"],"verify_live")

        workflow=self.read("views/workflows/chatgpt-jason-local-execution.md")
        self.assertIn("Workflow 1",workflow)
        self.assertIn("Workflow 2",workflow)
        self.assertIn("ContextView<ChatGPT, Jason>",workflow)
        self.assertFalse((ROOT/"collaboration/local-execution-workflows.md").exists())

    def test_github_mutation_incident_guardrail_is_active(self):
        workflow=self.read("collaboration/git-workflow.md")
        self.assertIn("high-level Chat-side GitHub contents mutation",workflow)
        self.assertIn("not an accepted path for canonical merges",workflow)
        audit=self.read("evidence/audits/github-connector-mutation-incident-2026-09-16.md")
        self.assertIn("action-selection/invocation failure",audit)
        memory_index=yaml.safe_load(self.read("memory/index.yaml"))
        active={str(item["id"]) for item in memory_index["records"] if item.get("status")=="active"}
        superseded={str(item["id"]) for item in memory_index["records"] if item.get("status")=="superseded"}
        self.assertIn("MEM-20260916T095000Z-7C4E91",active)
        self.assertIn("MEM-20260916T102500Z-4F7A21",active)
        self.assertIn("MEM-20260916T095200Z-1D6B42",superseded)

    def test_current_session_checkpoint_has_required_continuity_fields(self):
        sessions=[p for p in (ROOT/"sessions").glob("*.md") if re.match(r"^\d{4}-\d{2}-\d{2}-qiven-v\d+\.md$",p.name)]
        checkpoint=max(sessions,key=lambda item:(item.name[:10],int(re.search(r"-v(\d+)\.md$",item.name).group(1)))).read_text(encoding="utf-8")
        required_headings=(
            "Session identity","Exact current task","Accepted refs and evidence","Unaccepted candidate refs",
            "Pending asynchronous work","Known inconsistencies and evidence gaps","Next action",
        )
        required_phrases=("Qiven-v2 through Qiven-v5","Do not synthesize them","ContextView<ChatGPT, Jason>")
        missing=[f"missing '## {heading}' heading" for heading in required_headings
                 if not re.search(rf"(?m)^## {re.escape(heading)}$",checkpoint)]
        missing+=[f"missing literal phrase {phrase!r}" for phrase in required_phrases
                  if phrase not in checkpoint]
        # report every gap in ONE failure: a one-assert-at-a-time chain costs a
        # full gate cycle (~3 minutes) per missing item (2026-09-19 odyssey)
        self.assertEqual(missing,[],"current session checkpoint continuity gaps")

    def test_governance_contract_is_remote_and_account_level(self):
        authority=yaml.safe_load(self.read("governance/authority.yaml"))
        self.assertEqual(authority["trust_provider"],"github")
        self.assertEqual(authority["canonical_context"]["remote_state"],"authoritative")
        self.assertEqual(authority["canonical_context"]["local_state"],"non_authoritative_working_copy")
        self.assertEqual(authority["root_principal"]["account"],"JasonHuang3D")
        self.assertEqual(authority["authentication_semantics"]["biological_identity_verification"],"out_of_scope")

    def test_historical_rubric_still_references_existing_canonical_ids(self):
        rubric=self.read("tests/cold-boot/evaluator-rubric.md")
        headings=re.findall(r"^### C(\d+) — ",rubric,flags=re.MULTILINE); self.assertEqual(headings,[str(i) for i in range(1,13)])
        obligation_index=yaml.safe_load(self.read("obligations/index.yaml")); decision_index=yaml.safe_load(self.read("decisions/index.yaml"))
        obligations={str(item["id"]) for item in obligation_index["records"]}; decisions={str(item["id"]) for item in decision_index["records"]}
        required_obligations={"OBL-20260913T152950Z-D4E5F6","OBL-20260913T182954Z-7B4E20","OBL-20260913T182338Z-4F7C19","OBL-20260913T185050Z-21DCBC","OBL-20260913T183819Z-9A4F21"}
        required_decisions={"ADR-0003","ADR-0020","ADR-0021"}
        self.assertTrue(required_obligations<=obligations); self.assertTrue(required_decisions<=decisions)

if __name__=="__main__": unittest.main(verbosity=2)
