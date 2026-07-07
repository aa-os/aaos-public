import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.m13_registry_drift_evaluator import (  # noqa: E402
    evaluate_registry_drift_specimen,
)


REGISTRY_DRIFT_SPECIMEN_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m13-registry-drift-detection-specimen.json"
)


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class M13RegistryDriftEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.specimen = load_json(REGISTRY_DRIFT_SPECIMEN_PATH)

    def evaluate(self, specimen=None):
        return evaluate_registry_drift_specimen(
            self.specimen if specimen is None else specimen
        )

    def test_valid_registry_drift_specimen_passes(self):
        result = self.evaluate()

        self.assertTrue(result["registry_drift_specimen_valid"])
        self.assertFalse(result["registry_drift_specimen_invalid"])
        self.assertTrue(result["drift_type_coverage_complete"])
        self.assertTrue(result["no_drift_detected"])
        self.assertTrue(result["registry_drift_detected"])
        self.assertTrue(result["authority_boundary_preserved"])
        self.assertTrue(result["release_status_future_only"])
        self.assertEqual(result["registry_drift_findings"], [])
        self.assertEqual(result["missing_evidence"], [])

    def test_missing_176_reference_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["related_issue"] = ""

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertIn("missing_related_issue_176", result["registry_drift_findings"])

    def test_closes_176_language_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["tracker_issue_linkage"] = "Closes #176"

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "tracker_issue_176_closure_claim_detected",
            result["registry_drift_findings"],
        )

    def test_missing_177_reference_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["runtime_approval_gate_evidence_pr"] = ""

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertIn(
            "missing_runtime_approval_gate_evidence_pr_177",
            result["registry_drift_findings"],
        )

    def test_missing_171_closed_follow_up_reference_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["closed_runtime_approval_follow_up"] = ""

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertIn(
            "missing_closed_runtime_approval_follow_up_171",
            result["registry_drift_findings"],
        )

    def test_v012_released_claim_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["future_release_tag_path"]["released"] = True

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertFalse(result["release_status_future_only"])
        self.assertIn("v0_12_0_release_claim_detected", result["registry_drift_findings"])

    def test_m13_complete_claim_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["m13_completion_status"] = "M13 is complete."

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("m13_completion_claim_detected", result["registry_drift_findings"])

    def test_missing_required_drift_type_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["drift_types"] = [
            item
            for item in specimen["drift_types"]
            if item["drift_type_id"] != "consumer_identity_drift"
        ]

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertTrue(result["drift_type_coverage_incomplete"])
        self.assertIn("drift_type_coverage_incomplete", result["registry_drift_findings"])

    def test_missing_no_drift_positive_example_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["positive_drift_examples"] = [
            item
            for item in specimen["positive_drift_examples"]
            if item["example_id"] != "no_drift_detected_external_evidence_dashboard_consumer"
        ]

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertFalse(result["no_drift_detected"])
        self.assertIn("no_drift_positive_example_missing", result["registry_drift_findings"])

    def test_missing_drift_detected_positive_example_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["positive_drift_examples"] = [
            item
            for item in specimen["positive_drift_examples"]
            if item["example_id"] != "drift_detected_authority_preserved_audit_export_consumer"
        ]

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertFalse(result["registry_drift_detected"])
        self.assertIn(
            "drift_detected_positive_example_missing",
            result["registry_drift_findings"],
        )

    def test_unmarked_negative_fixture_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["negative_drift_fixtures"][0]["negative_fixture"] = False

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertIn(
            "negative_fixture_unmarked_registry_inclusion_as_approval",
            result["registry_drift_findings"],
        )

    def test_registry_inclusion_as_approval_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["semantic_boundaries"]["registry_inclusion_boundary"] = (
            "Registry inclusion is approval."
        )

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "registry_inclusion_approval_claim_detected",
            result["registry_drift_findings"],
        )

    def test_no_drift_detected_as_release_approval_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["semantic_boundaries"]["no_drift_boundary"] = (
            "no_drift_detected is release approval."
        )

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "no_drift_release_approval_claim_detected",
            result["registry_drift_findings"],
        )

    def test_fail_closed_recommended_as_fail_closed_executed_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["semantic_boundaries"]["fail_closed_boundary"] = (
            "fail_closed_recommended is fail_closed_executed."
        )

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("fail_closed_execution_claim_detected", result["registry_drift_findings"])

    def test_sealing_eligible_as_sealed_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["semantic_boundaries"]["sealing_eligibility_boundary"] = (
            "sealing_eligible is sealed."
        )

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "sealing_eligibility_sealed_claim_detected",
            result["registry_drift_findings"],
        )

    def test_nonsealed_artifact_converted_into_sealed_artifact_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["semantic_boundaries"]["non_sealed_conversion_boundary"] = (
            "Drift detector converts non-sealed artifact into sealed artifact."
        )

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "nonsealed_to_sealed_conversion_claim_detected",
            result["registry_drift_findings"],
        )

    def test_aaos_sealed_artifact_resealed_by_consumer_or_registry_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["semantic_boundaries"]["aaos_sealed_reseal_boundary"] = (
            "Drift detector re-seals AAOS-sealed artifact."
        )

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "aaos_sealed_reseal_claim_detected",
            result["registry_drift_findings"],
        )

    def test_authority_transferred_to_external_consumer_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["semantic_boundaries"]["authority_transfer_boundary"] = (
            "Authority transferred to external consumer."
        )

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "authority_transfer_to_external_consumer_claim_detected",
            result["registry_drift_findings"],
        )

    def test_release_approved_output_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["detector_output"] = "release_approved"

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("authority_transfer_claim_detected", result["registry_drift_findings"])

    def test_risk_accepted_output_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["detector_output"] = "risk_accepted"

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("authority_transfer_claim_detected", result["registry_drift_findings"])

    def test_final_governance_judgment_output_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["detector_output"] = "final_governance_judgment"

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("authority_transfer_claim_detected", result["registry_drift_findings"])

    def test_audit_closed_output_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["detector_output"] = "audit_closed"

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("authority_transfer_claim_detected", result["registry_drift_findings"])

    def test_missing_aaos_authority_statement_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["governance_boundary_statement"] = ""
        specimen["decision_proof_sealing_boundary_statement"] = ""
        specimen["aaos_retained_authority_statement"] = ""
        specimen["sovereignty_statement"] = ""

        result = self.evaluate(specimen)

        self.assertTrue(result["registry_drift_specimen_invalid"])
        self.assertIn(
            "missing_aaos_authority_boundary_statement",
            result["registry_drift_findings"],
        )


if __name__ == "__main__":
    unittest.main()
