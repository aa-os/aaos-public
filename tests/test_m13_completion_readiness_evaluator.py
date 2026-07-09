import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.m13_completion_readiness_evaluator import (  # noqa: E402
    evaluate_m13_completion_readiness,
)


ARTIFACT_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m13-completion-readiness-future-readme-path.json"
)
README_PATH = ROOT / "README.md"


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_text(path):
    with path.open(encoding="utf-8") as handle:
        return handle.read()


class M13CompletionReadinessEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.artifact = load_json(ARTIFACT_PATH)
        self.readme_text = load_text(README_PATH)

    def evaluate(self, artifact=None, readme_text=None):
        return evaluate_m13_completion_readiness(
            self.artifact if artifact is None else artifact,
            self.readme_text if readme_text is None else readme_text,
        )

    def test_valid_completion_readiness_and_readme_future_path_ready_for_review(self):
        result = self.evaluate()

        self.assertTrue(result["completion_readiness_valid"])
        self.assertFalse(result["completion_readiness_invalid"])
        self.assertTrue(result["completion_readiness_coverage_complete"])
        self.assertTrue(result["completion_ready_for_review"])
        self.assertFalse(result["completion_not_ready"])
        self.assertTrue(result["readme_future_path_present"])
        self.assertTrue(result["release_status_future_only"])
        self.assertEqual(result["completion_readiness_findings"], [])
        self.assertEqual(result["missing_evidence"], [])

    def test_missing_177_runtime_approval_evidence_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["runtime_approval_gate_evidence_pr"] = ""
        artifact["release_linkage_refs"]["runtime_enforced_approval_evidence_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertTrue(result["completion_readiness_coverage_incomplete"])
        self.assertIn("missing_runtime_approval_gate_evidence_pr", result["completion_readiness_findings"])

    def test_missing_178_registry_drift_detection_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["registry_drift_detection_pr"] = ""
        artifact["release_linkage_refs"]["registry_drift_detection_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertTrue(result["completion_readiness_coverage_incomplete"])
        self.assertIn("missing_registry_drift_detection_pr", result["completion_readiness_findings"])

    def test_missing_194_authority_boundary_regression_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["authority_boundary_regression_fixtures_pr"] = ""
        artifact["release_linkage_refs"]["authority_boundary_regression_fixtures_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertTrue(result["completion_readiness_coverage_incomplete"])
        self.assertIn(
            "missing_authority_boundary_regression_fixtures_pr",
            result["completion_readiness_findings"],
        )

    def test_missing_195_operational_readiness_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["operational_readiness_checklist_pr"] = ""
        artifact["release_linkage_refs"]["operational_readiness_checklist_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertTrue(result["completion_readiness_coverage_incomplete"])
        self.assertIn("missing_operational_readiness_checklist_pr", result["completion_readiness_findings"])

    def test_missing_196_onboarding_documentation_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["external_consumer_onboarding_documentation_pr"] = ""
        artifact["release_linkage_refs"]["external_consumer_onboarding_documentation_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertTrue(result["completion_readiness_coverage_incomplete"])
        self.assertIn(
            "missing_external_consumer_onboarding_documentation_pr",
            result["completion_readiness_findings"],
        )

    def test_missing_197_release_proof_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["release_proof_linkage_specimen_pr"] = ""
        artifact["release_linkage_refs"]["release_proof_linkage_specimen_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertTrue(result["completion_readiness_coverage_incomplete"])
        self.assertIn("missing_release_proof_linkage_specimen_pr", result["completion_readiness_findings"])

    def test_readme_future_path_missing_fails(self):
        readme_text = self.readme_text.replace(
            "Future README status path: v0.12.0 / M13 remains a future-only path until a final completion PR.",
            "",
        )

        result = self.evaluate(readme_text=readme_text)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertFalse(result["readme_future_path_present"])
        self.assertIn("readme_future_status_path_missing", result["completion_readiness_findings"])

    def test_readme_declaring_m13_complete_fails(self):
        result = self.evaluate(readme_text=self.readme_text + "\nM13 complete\n")

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertIn("readme_m13_completion_claim_detected", result["completion_readiness_findings"])

    def test_readme_declaring_v012_released_fails(self):
        result = self.evaluate(readme_text=self.readme_text + "\nv0.12.0 released\n")

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertIn("readme_v0_12_0_released_claim_detected", result["completion_readiness_findings"])

    def test_readme_closes_176_language_fails(self):
        result = self.evaluate(readme_text=self.readme_text + "\nCloses #176\n")

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertIn(
            "readme_tracker_issue_176_closure_claim_detected",
            result["completion_readiness_findings"],
        )

    def test_completion_ready_for_review_as_m13_complete_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["semantic_boundaries"][
            "completion_ready_for_review_boundary"
        ] = "completion_ready_for_review is m13_complete."

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertIn(
            "completion_ready_for_review_m13_complete_claim_detected",
            result["completion_readiness_findings"],
        )

    def test_readme_future_path_present_as_released_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["semantic_boundaries"][
            "readme_future_path_boundary"
        ] = "readme_future_path_present is released."

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertIn(
            "readme_future_path_released_claim_detected",
            result["completion_readiness_findings"],
        )

    def test_release_ready_for_review_as_release_approved_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["semantic_boundaries"][
            "release_ready_for_review_boundary"
        ] = "release_ready_for_review is release_approved."

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertIn(
            "release_ready_for_review_approval_claim_detected",
            result["completion_readiness_findings"],
        )

    def test_evidence_complete_as_sealed_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["semantic_boundaries"][
            "evidence_complete_boundary"
        ] = "evidence_complete is sealed."

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertIn("evidence_complete_sealed_claim_detected", result["completion_readiness_findings"])

    def test_replay_ready_as_sealed_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["semantic_boundaries"]["replay_ready_boundary"] = "replay_ready is sealed."

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertIn("replay_ready_sealed_claim_detected", result["completion_readiness_findings"])

    def test_release_tag_marked_created_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["release_tag_created"] = True

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertFalse(result["release_status_future_only"])
        self.assertIn("release_tag_created_claim_detected", result["completion_readiness_findings"])

    def test_release_notes_marked_published_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["release_notes_published"] = True

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertFalse(result["release_status_future_only"])
        self.assertIn("release_notes_published_claim_detected", result["completion_readiness_findings"])

    def test_issue_176_closed_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["issue_176_closed"] = True

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertIn("issue_176_closed_claim_detected", result["completion_readiness_findings"])

    def test_evaluator_output_attempting_to_seal_decision_proof_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["evaluator_output"] = "decision_proof_sealed"

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn("authority_transfer_claim_detected", result["completion_readiness_findings"])

    def test_evaluator_output_attempting_final_governance_judgment_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["evaluator_output"] = "final_governance_judgment"

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn("authority_transfer_claim_detected", result["completion_readiness_findings"])


if __name__ == "__main__":
    unittest.main()
