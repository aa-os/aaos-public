import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.m13_final_completion_evaluator import (  # noqa: E402
    evaluate_m13_final_completion,
)


ARTIFACT_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m13-final-completion-release-state.json"
)
README_PATH = ROOT / "README.md"

FORBIDDEN_RESULT_KEYS = {
    "github_release_created",
    "release_tag_created_by_evaluator",
    "decision_proof_sealed_by_evaluator",
    "sealed_by_external_consumer",
    "authority_transferred",
    "risk_accepted_by_evaluator",
    "audit_closed_by_evaluator",
    "waiver_granted_by_evaluator",
    "final_governance_judgment_by_evaluator",
}


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_text(path):
    with path.open(encoding="utf-8") as handle:
        return handle.read()


class M13FinalCompletionEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.artifact = load_json(ARTIFACT_PATH)
        self.readme_text = load_text(README_PATH)

    def evaluate(self, artifact=None, readme_text=None):
        return evaluate_m13_final_completion(
            self.artifact if artifact is None else artifact,
            self.readme_text if readme_text is None else readme_text,
        )

    def test_valid_final_m13_completion_state_prepares_v012_release_state(self):
        result = self.evaluate()

        self.assertTrue(result["m13_final_completion_valid"])
        self.assertFalse(result["m13_final_completion_invalid"])
        self.assertTrue(result["m13_completion_declared"])
        self.assertTrue(result["issue_176_closes_on_merge"])
        self.assertTrue(result["repository_release_state_prepared"])
        self.assertTrue(result["github_release_pending_manual_publication"])
        self.assertEqual(result["final_completion_findings"], [])
        self.assertEqual(result["missing_evidence"], [])
        for forbidden_key in FORBIDDEN_RESULT_KEYS:
            self.assertNotIn(forbidden_key, result)

    def test_missing_177_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["runtime_approval_gate_evidence_pr"] = ""
        artifact["release_linkage_refs"]["runtime_enforced_approval_evidence_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn("missing_or_invalid_runtime_approval_gate_evidence_pr", result["final_completion_findings"])

    def test_missing_178_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["registry_drift_detection_pr"] = ""
        artifact["release_linkage_refs"]["registry_drift_detection_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn("missing_or_invalid_registry_drift_detection_pr", result["final_completion_findings"])

    def test_missing_194_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["authority_boundary_regression_fixtures_pr"] = ""
        artifact["release_linkage_refs"]["authority_boundary_regression_fixtures_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn(
            "missing_or_invalid_authority_boundary_regression_fixtures_pr",
            result["final_completion_findings"],
        )

    def test_missing_195_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["operational_readiness_checklist_pr"] = ""
        artifact["release_linkage_refs"]["operational_readiness_checklist_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn("missing_or_invalid_operational_readiness_checklist_pr", result["final_completion_findings"])

    def test_missing_196_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["external_consumer_onboarding_documentation_pr"] = ""
        artifact["release_linkage_refs"]["external_consumer_onboarding_documentation_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn(
            "missing_or_invalid_external_consumer_onboarding_documentation_pr",
            result["final_completion_findings"],
        )

    def test_missing_197_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["release_proof_linkage_specimen_pr"] = ""
        artifact["release_linkage_refs"]["release_proof_linkage_specimen_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn("missing_or_invalid_release_proof_linkage_specimen_pr", result["final_completion_findings"])

    def test_missing_198_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["completion_readiness_future_readme_path_pr"] = ""
        artifact["release_linkage_refs"]["completion_readiness_future_readme_path_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn(
            "missing_or_invalid_completion_readiness_future_readme_path_pr",
            result["final_completion_findings"],
        )

    def test_readme_missing_v012_release_entry_fails(self):
        readme_text = self.readme_text.replace(
            "- v0.12.0 — M13 External Consumer Registry Hardening and Operational Readiness\n",
            "",
        )

        result = self.evaluate(readme_text=readme_text)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn("readme_v0_12_0_release_entry_missing", result["final_completion_findings"])

    def test_readme_failing_to_declare_m13_complete_fails(self):
        readme_text = self.readme_text.replace(
            "M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11, M12, and M13 are complete.",
            "M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11, and M12 are complete.",
        )

        result = self.evaluate(readme_text=readme_text)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn("readme_m13_completion_status_missing", result["final_completion_findings"])

    def test_readme_leaving_m13_active_work_in_next_phase_fails(self):
        next_phase_heading = "## Next Phase"
        self.assertEqual(self.readme_text.count(next_phase_heading), 1)
        readme_text = self.readme_text.replace(
            next_phase_heading,
            (
                f"{next_phase_heading}\n\n"
                "M13 remains active work; final completion has not been declared."
            ),
            1,
        )
        self.assertNotEqual(readme_text, self.readme_text)

        result = self.evaluate(readme_text=readme_text)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn("readme_next_phase_m13_active_work_claim_detected", result["final_completion_findings"])

    def test_tracker_linkage_not_using_closes_176_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["tracker_issue_linkage"] = "Refs #176"
        artifact["release_linkage_refs"]["tracker_issue_linkage"] = "Refs #176"

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn("missing_or_invalid_tracker_issue_linkage", result["final_completion_findings"])

    def test_artifact_claiming_github_release_created_by_pr_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["github_release_created_by_pr"] = True

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn("github_release_created_by_pr_claim_detected", result["final_completion_findings"])

    def test_artifact_claiming_release_tag_created_by_pr_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["release_tag_created_by_pr"] = True

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn("release_tag_created_by_pr_claim_detected", result["final_completion_findings"])

    def test_evaluator_attempting_to_seal_decision_proof_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["evaluator_output"] = "decision_proof_sealed_by_evaluator"

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn("forbidden_evaluator_output_claim_detected", result["final_completion_findings"])

    def test_evaluator_attempting_to_transfer_authority_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["evaluator_output"] = "authority_transferred"

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn("forbidden_evaluator_output_claim_detected", result["final_completion_findings"])

    def test_evaluator_attempting_final_governance_judgment_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["evaluator_output"] = "final_governance_judgment_by_evaluator"

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn("forbidden_evaluator_output_claim_detected", result["final_completion_findings"])


if __name__ == "__main__":
    unittest.main()
