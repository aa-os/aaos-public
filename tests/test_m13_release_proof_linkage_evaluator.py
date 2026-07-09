import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.m13_release_proof_linkage_evaluator import (  # noqa: E402
    evaluate_m13_release_proof_linkage,
)


SPECIMEN_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m13-release-proof-linkage-specimen.json"
)


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class M13ReleaseProofLinkageEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.specimen = load_json(SPECIMEN_PATH)

    def evaluate(self, specimen=None):
        return evaluate_m13_release_proof_linkage(
            self.specimen if specimen is None else specimen
        )

    def test_valid_future_only_release_proof_linkage_ready_for_review_without_authority_transfer(self):
        result = self.evaluate()

        self.assertTrue(result["release_proof_linkage_valid"])
        self.assertFalse(result["release_proof_linkage_invalid"])
        self.assertTrue(result["release_linkage_coverage_complete"])
        self.assertFalse(result["release_linkage_coverage_incomplete"])
        self.assertTrue(result["release_ready_for_review"])
        self.assertFalse(result["release_not_ready"])
        self.assertTrue(result["release_status_future_only"])
        self.assertEqual(result["release_proof_findings"], [])
        self.assertEqual(result["missing_evidence"], [])

    def test_missing_177_runtime_approval_evidence_linkage_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["runtime_approval_gate_evidence_pr"] = ""
        specimen["release_linkage_refs"]["runtime_enforced_approval_evidence_pr"] = ""

        result = self.evaluate(specimen)

        self.assertTrue(result["release_proof_linkage_invalid"])
        self.assertTrue(result["release_linkage_coverage_incomplete"])
        self.assertIn("missing_runtime_approval_gate_evidence_pr", result["release_proof_findings"])

    def test_missing_178_registry_drift_detection_linkage_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["registry_drift_detection_pr"] = ""
        specimen["release_linkage_refs"]["registry_drift_detection_pr"] = ""

        result = self.evaluate(specimen)

        self.assertTrue(result["release_proof_linkage_invalid"])
        self.assertTrue(result["release_linkage_coverage_incomplete"])
        self.assertIn("missing_registry_drift_detection_pr", result["release_proof_findings"])

    def test_missing_194_authority_boundary_regression_linkage_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["authority_boundary_regression_fixtures_pr"] = ""
        specimen["release_linkage_refs"]["authority_boundary_regression_fixtures_pr"] = ""

        result = self.evaluate(specimen)

        self.assertTrue(result["release_proof_linkage_invalid"])
        self.assertTrue(result["release_linkage_coverage_incomplete"])
        self.assertIn(
            "missing_authority_boundary_regression_fixtures_pr",
            result["release_proof_findings"],
        )

    def test_missing_195_operational_readiness_linkage_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["operational_readiness_checklist_pr"] = ""
        specimen["release_linkage_refs"]["operational_readiness_checklist_pr"] = ""

        result = self.evaluate(specimen)

        self.assertTrue(result["release_proof_linkage_invalid"])
        self.assertTrue(result["release_linkage_coverage_incomplete"])
        self.assertIn(
            "missing_operational_readiness_checklist_pr",
            result["release_proof_findings"],
        )

    def test_missing_196_onboarding_documentation_linkage_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["external_consumer_onboarding_documentation_pr"] = ""
        specimen["release_linkage_refs"][
            "external_consumer_onboarding_documentation_pr"
        ] = ""

        result = self.evaluate(specimen)

        self.assertTrue(result["release_proof_linkage_invalid"])
        self.assertTrue(result["release_linkage_coverage_incomplete"])
        self.assertIn(
            "missing_external_consumer_onboarding_documentation_pr",
            result["release_proof_findings"],
        )

    def test_release_proof_linkage_as_release_approval_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["semantic_boundaries"][
            "release_approval_boundary"
        ] = "Release proof linkage is release approval."

        result = self.evaluate(specimen)

        self.assertTrue(result["release_proof_linkage_invalid"])
        self.assertIn(
            "release_proof_release_approval_claim_detected",
            result["release_proof_findings"],
        )

    def test_release_ready_for_review_as_release_approved_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["semantic_boundaries"][
            "release_ready_for_review_boundary"
        ] = "release_ready_for_review is release_approved."

        result = self.evaluate(specimen)

        self.assertTrue(result["release_proof_linkage_invalid"])
        self.assertIn(
            "release_ready_for_review_approval_claim_detected",
            result["release_proof_findings"],
        )

    def test_release_proof_complete_as_released_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["semantic_boundaries"][
            "release_proof_complete_boundary"
        ] = "release_proof_complete is released."

        result = self.evaluate(specimen)

        self.assertTrue(result["release_proof_linkage_invalid"])
        self.assertIn(
            "release_proof_complete_released_claim_detected",
            result["release_proof_findings"],
        )

    def test_evidence_complete_as_sealed_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["semantic_boundaries"][
            "evidence_complete_boundary"
        ] = "evidence_complete is sealed."

        result = self.evaluate(specimen)

        self.assertTrue(result["release_proof_linkage_invalid"])
        self.assertIn("evidence_complete_sealed_claim_detected", result["release_proof_findings"])

    def test_replay_ready_as_sealed_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["semantic_boundaries"]["replay_ready_boundary"] = "replay_ready is sealed."

        result = self.evaluate(specimen)

        self.assertTrue(result["release_proof_linkage_invalid"])
        self.assertIn("replay_ready_sealed_claim_detected", result["release_proof_findings"])

    def test_v012_marked_released_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["future_release_tag_path"]["released"] = True

        result = self.evaluate(specimen)

        self.assertTrue(result["release_proof_linkage_invalid"])
        self.assertFalse(result["release_status_future_only"])
        self.assertIn("v0_12_0_release_claim_detected", result["release_proof_findings"])

    def test_release_tag_marked_created_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["release_tag_created"] = True

        result = self.evaluate(specimen)

        self.assertTrue(result["release_proof_linkage_invalid"])
        self.assertFalse(result["release_status_future_only"])
        self.assertIn("release_tag_created_claim_detected", result["release_proof_findings"])

    def test_release_notes_marked_published_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["release_notes_published"] = True

        result = self.evaluate(specimen)

        self.assertTrue(result["release_proof_linkage_invalid"])
        self.assertFalse(result["release_status_future_only"])
        self.assertIn("release_notes_published_claim_detected", result["release_proof_findings"])

    def test_m13_marked_complete_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["m13_complete"] = True

        result = self.evaluate(specimen)

        self.assertTrue(result["release_proof_linkage_invalid"])
        self.assertFalse(result["release_status_future_only"])
        self.assertIn("m13_completion_claim_detected", result["release_proof_findings"])

    def test_tracker_176_closed_or_closes_language_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["tracker_issue_closure_state"] = "closed"

        result = self.evaluate(specimen)

        self.assertTrue(result["release_proof_linkage_invalid"])
        self.assertIn("tracker_issue_176_not_marked_open", result["release_proof_findings"])

        specimen = copy.deepcopy(self.specimen)
        specimen["tracker_issue_linkage"] = "Closes #176"

        result = self.evaluate(specimen)

        self.assertTrue(result["release_proof_linkage_invalid"])
        self.assertIn(
            "tracker_issue_176_closure_claim_detected",
            result["release_proof_findings"],
        )

    def test_evaluator_output_attempting_to_seal_decision_proof_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["evaluator_output"] = "decision_proof_sealed"

        result = self.evaluate(specimen)

        self.assertTrue(result["release_proof_linkage_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn("authority_transfer_claim_detected", result["release_proof_findings"])

    def test_evaluator_output_attempting_final_governance_judgment_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["evaluator_output"] = "final_governance_judgment"

        result = self.evaluate(specimen)

        self.assertTrue(result["release_proof_linkage_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn("authority_transfer_claim_detected", result["release_proof_findings"])


if __name__ == "__main__":
    unittest.main()
