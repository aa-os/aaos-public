import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.m12_integration_ci_check_evaluator import (  # noqa: E402
    evaluate_m12_integration_ci_check_specimen,
)


SPECIMEN_EXAMPLE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m12-integration-ci-check-specimen.json"
)


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class M12IntegrationCICheckEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.specimen = load_json(SPECIMEN_EXAMPLE_PATH)

    def test_integration_ci_specimen_passes(self):
        result = evaluate_m12_integration_ci_check_specimen(self.specimen)

        self.assertTrue(result["integration_ci_specimen_valid"])
        self.assertTrue(result["integration_ci_check_passed"])
        self.assertTrue(result["consumer_registry_fields_valid"])
        self.assertTrue(result["authority_boundary_preserved"])
        self.assertTrue(result["sealed_nonsealed_semantics_preserved"])
        self.assertTrue(result["release_status_future_only"])
        self.assertEqual(result["integration_ci_findings"], [])
        self.assertEqual(result["missing_evidence"], [])

    def test_missing_168_reference_fails(self):
        record = copy.deepcopy(self.specimen)
        record["related_issue"] = ""

        result = evaluate_m12_integration_ci_check_specimen(record)

        self.assertTrue(result["integration_ci_specimen_invalid"])
        self.assertIn("missing_related_issue_168", result["integration_ci_findings"])

    def test_closes_168_language_fails(self):
        record = copy.deepcopy(self.specimen)
        record["tracker_issue_linkage"] = "Closes #168"

        result = evaluate_m12_integration_ci_check_specimen(record)

        self.assertTrue(result["integration_ci_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "tracker_issue_168_closure_claim_detected",
            result["integration_ci_findings"],
        )

    def test_missing_169_reference_fails(self):
        record = copy.deepcopy(self.specimen)
        record["first_m12_consumer_registry_pr"] = ""

        result = evaluate_m12_integration_ci_check_specimen(record)

        self.assertTrue(result["integration_ci_specimen_invalid"])
        self.assertIn(
            "missing_first_m12_consumer_registry_pr_169",
            result["integration_ci_findings"],
        )

    def test_v011_release_claim_fails(self):
        record = copy.deepcopy(self.specimen)
        record["release_status_path"]["v0_11_0_target_release_state"] = (
            "v0.11.0 is released."
        )

        result = evaluate_m12_integration_ci_check_specimen(record)

        self.assertTrue(result["integration_ci_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("v0_11_0_release_claim_detected", result["integration_ci_findings"])

    def test_m12_complete_claim_fails(self):
        record = copy.deepcopy(self.specimen)
        record["specimen_status"] = "m12_complete"

        result = evaluate_m12_integration_ci_check_specimen(record)

        self.assertTrue(result["integration_ci_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("m12_completion_claim_detected", result["integration_ci_findings"])

    def test_positive_output_release_approved_fails(self):
        record = copy.deepcopy(self.specimen)
        record["positive_ci_check_examples"][0]["ci_outputs"].append("release_approved")

        result = evaluate_m12_integration_ci_check_specimen(record)

        self.assertTrue(result["integration_ci_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "positive_ci_output_forbidden_authority_output_detected",
            result["integration_ci_findings"],
        )

    def test_positive_output_decision_proof_sealed_fails(self):
        record = copy.deepcopy(self.specimen)
        record["positive_ci_check_examples"][0]["ci_outputs"].append(
            "decision_proof_sealed"
        )

        result = evaluate_m12_integration_ci_check_specimen(record)

        self.assertTrue(result["integration_ci_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "positive_ci_output_forbidden_authority_output_detected",
            result["integration_ci_findings"],
        )

    def test_positive_output_fail_closed_executed_fails(self):
        record = copy.deepcopy(self.specimen)
        record["positive_ci_check_examples"][0]["ci_outputs"].append(
            "fail_closed_executed"
        )

        result = evaluate_m12_integration_ci_check_specimen(record)

        self.assertTrue(result["integration_ci_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "positive_ci_output_forbidden_authority_output_detected",
            result["integration_ci_findings"],
        )

    def test_registry_inclusion_as_approval_fails(self):
        record = copy.deepcopy(self.specimen)
        record["registry_inclusion_boundary"] = "Registry inclusion is approval."

        result = evaluate_m12_integration_ci_check_specimen(record)

        self.assertTrue(result["integration_ci_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "registry_inclusion_approval_claim_detected",
            result["integration_ci_findings"],
        )

    def test_ci_pass_as_approval_fails(self):
        record = copy.deepcopy(self.specimen)
        record["ci_pass_boundary"] = "CI pass is approval."

        result = evaluate_m12_integration_ci_check_specimen(record)

        self.assertTrue(result["integration_ci_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("ci_pass_approval_claim_detected", result["integration_ci_findings"])

    def test_release_proof_linkage_as_release_approval_fails(self):
        record = copy.deepcopy(self.specimen)
        record["release_proof_boundary"] = (
            "Release proof linkage is release approval."
        )

        result = evaluate_m12_integration_ci_check_specimen(record)

        self.assertTrue(result["integration_ci_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "release_proof_release_approval_claim_detected",
            result["integration_ci_findings"],
        )

    def test_fail_closed_recommended_as_executed_fails(self):
        record = copy.deepcopy(self.specimen)
        record["fail_closed_boundary"] = (
            "fail_closed_recommended is fail_closed_executed."
        )

        result = evaluate_m12_integration_ci_check_specimen(record)

        self.assertTrue(result["integration_ci_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "fail_closed_execution_claim_detected",
            result["integration_ci_findings"],
        )

    def test_sealing_eligible_as_sealed_fails(self):
        record = copy.deepcopy(self.specimen)
        record["sealing_eligibility_boundary"] = "sealing_eligible is sealed."

        result = evaluate_m12_integration_ci_check_specimen(record)

        self.assertTrue(result["integration_ci_specimen_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "sealing_eligibility_sealed_claim_detected",
            result["integration_ci_findings"],
        )

    def test_missing_aaos_authority_statement_fails(self):
        record = copy.deepcopy(self.specimen)
        record["decision_proof_sealing_boundary_statement"] = ""
        record["sovereignty_statement"] = ""

        result = evaluate_m12_integration_ci_check_specimen(record)

        self.assertTrue(result["integration_ci_specimen_invalid"])
        self.assertIn(
            "missing_integration_ci_authority_boundary_statement",
            result["integration_ci_findings"],
        )


if __name__ == "__main__":
    unittest.main()
