import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.m12_cross_consumer_traceability_evaluator import (  # noqa: E402
    evaluate_m12_cross_consumer_traceability,
)


TRACEABILITY_EXAMPLE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m12-cross-consumer-traceability-examples.json"
)


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class M12CrossConsumerTraceabilityEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.traceability = load_json(TRACEABILITY_EXAMPLE_PATH)

    def test_cross_consumer_traceability_artifact_passes(self):
        result = evaluate_m12_cross_consumer_traceability(self.traceability)

        self.assertTrue(result["cross_consumer_traceability_valid"])
        self.assertTrue(result["compliant_consumer_traceability_present"])
        self.assertTrue(result["traceability_linkage_complete"])
        self.assertTrue(result["authority_boundary_preserved"])
        self.assertTrue(result["sealed_nonsealed_semantics_preserved"])
        self.assertTrue(result["release_status_future_only"])
        self.assertEqual(result["traceability_findings"], [])
        self.assertEqual(result["missing_evidence"], [])

    def test_missing_168_reference_fails(self):
        record = copy.deepcopy(self.traceability)
        record["related_issue"] = ""

        result = evaluate_m12_cross_consumer_traceability(record)

        self.assertTrue(result["cross_consumer_traceability_invalid"])
        self.assertIn("missing_related_issue_168", result["traceability_findings"])

    def test_closes_168_language_fails(self):
        record = copy.deepcopy(self.traceability)
        record["tracker_issue_linkage"] = "Closes #168"

        result = evaluate_m12_cross_consumer_traceability(record)

        self.assertTrue(result["cross_consumer_traceability_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "tracker_issue_168_closure_claim_detected",
            result["traceability_findings"],
        )

    def test_missing_169_reference_fails(self):
        record = copy.deepcopy(self.traceability)
        record["m12_consumer_registry_pr"] = ""

        result = evaluate_m12_cross_consumer_traceability(record)

        self.assertTrue(result["cross_consumer_traceability_invalid"])
        self.assertIn(
            "missing_m12_consumer_registry_pr_169",
            result["traceability_findings"],
        )

    def test_missing_170_reference_fails(self):
        record = copy.deepcopy(self.traceability)
        record["m12_integration_ci_check_specimen_pr"] = ""

        result = evaluate_m12_cross_consumer_traceability(record)

        self.assertTrue(result["cross_consumer_traceability_invalid"])
        self.assertIn(
            "missing_m12_integration_ci_check_specimen_pr_170",
            result["traceability_findings"],
        )

    def test_v011_release_claim_fails(self):
        record = copy.deepcopy(self.traceability)
        record["release_status_path"]["v0_11_0_target_release_state"] = (
            "v0.11.0 is released."
        )

        result = evaluate_m12_cross_consumer_traceability(record)

        self.assertTrue(result["cross_consumer_traceability_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("v0_11_0_release_claim_detected", result["traceability_findings"])

    def test_m12_complete_claim_fails(self):
        record = copy.deepcopy(self.traceability)
        record["artifact_status"] = "m12_complete"

        result = evaluate_m12_cross_consumer_traceability(record)

        self.assertTrue(result["cross_consumer_traceability_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("m12_completion_claim_detected", result["traceability_findings"])

    def test_fewer_than_two_compliant_consumer_examples_fails(self):
        record = copy.deepcopy(self.traceability)
        record["compliant_consumer_traceability_examples"] = record[
            "compliant_consumer_traceability_examples"
        ][:1]

        result = evaluate_m12_cross_consumer_traceability(record)

        self.assertTrue(result["cross_consumer_traceability_invalid"])
        self.assertTrue(result["compliant_consumer_traceability_missing"])
        self.assertIn(
            "compliant_consumer_traceability_missing",
            result["traceability_findings"],
        )

    def test_missing_release_proof_linkage_fails(self):
        record = copy.deepcopy(self.traceability)
        record["release_proof_linkage"]["present"] = False

        result = evaluate_m12_cross_consumer_traceability(record)

        self.assertTrue(result["cross_consumer_traceability_invalid"])
        self.assertTrue(result["traceability_linkage_incomplete"])
        self.assertIn("release_proof_linkage_missing", result["traceability_findings"])

    def test_missing_integration_ci_check_reference_fails(self):
        record = copy.deepcopy(self.traceability)
        record["integration_ci_check_reference"] = ""

        result = evaluate_m12_cross_consumer_traceability(record)

        self.assertTrue(result["cross_consumer_traceability_invalid"])
        self.assertTrue(result["traceability_linkage_incomplete"])
        self.assertIn(
            "missing_integration_ci_check_reference",
            result["traceability_findings"],
        )

    def test_missing_aaos_authority_statement_fails(self):
        record = copy.deepcopy(self.traceability)
        record["decision_proof_sealing_boundary_statement"] = ""
        record["aaos_retained_authority_statement"] = ""
        record["sovereignty_statement"] = ""

        result = evaluate_m12_cross_consumer_traceability(record)

        self.assertTrue(result["cross_consumer_traceability_invalid"])
        self.assertIn(
            "missing_aaos_authority_boundary_statement",
            result["traceability_findings"],
        )

    def test_registry_inclusion_as_approval_fails(self):
        record = copy.deepcopy(self.traceability)
        record["registry_inclusion_boundary"] = "Registry inclusion is approval."

        result = evaluate_m12_cross_consumer_traceability(record)

        self.assertTrue(result["cross_consumer_traceability_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "registry_inclusion_approval_claim_detected",
            result["traceability_findings"],
        )

    def test_ci_pass_as_approval_fails(self):
        record = copy.deepcopy(self.traceability)
        record["ci_pass_boundary"] = "CI pass is approval."

        result = evaluate_m12_cross_consumer_traceability(record)

        self.assertTrue(result["cross_consumer_traceability_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("ci_pass_approval_claim_detected", result["traceability_findings"])

    def test_release_proof_linkage_as_release_approval_fails(self):
        record = copy.deepcopy(self.traceability)
        record["release_proof_boundary"] = (
            "Release proof linkage is release approval."
        )

        result = evaluate_m12_cross_consumer_traceability(record)

        self.assertTrue(result["cross_consumer_traceability_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "release_proof_release_approval_claim_detected",
            result["traceability_findings"],
        )

    def test_fail_closed_recommended_as_executed_fails(self):
        record = copy.deepcopy(self.traceability)
        record["fail_closed_boundary"] = (
            "fail_closed_recommended is fail_closed_executed."
        )

        result = evaluate_m12_cross_consumer_traceability(record)

        self.assertTrue(result["cross_consumer_traceability_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "fail_closed_execution_claim_detected",
            result["traceability_findings"],
        )

    def test_sealing_eligible_as_sealed_fails(self):
        record = copy.deepcopy(self.traceability)
        record["sealing_eligibility_boundary"] = "sealing_eligible is sealed."

        result = evaluate_m12_cross_consumer_traceability(record)

        self.assertTrue(result["cross_consumer_traceability_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "sealing_eligibility_sealed_claim_detected",
            result["traceability_findings"],
        )

    def test_final_governance_judgment_output_fails(self):
        record = copy.deepcopy(self.traceability)
        record["compliant_consumer_traceability_examples"][0][
            "traceability_outputs"
        ].append("final_governance_judgment")

        result = evaluate_m12_cross_consumer_traceability(record)

        self.assertTrue(result["cross_consumer_traceability_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "traceability_output_forbidden_authority_output_detected",
            result["traceability_findings"],
        )

    def test_audit_closed_output_fails(self):
        record = copy.deepcopy(self.traceability)
        record["compliant_consumer_traceability_examples"][1][
            "traceability_outputs"
        ].append("audit_closed")

        result = evaluate_m12_cross_consumer_traceability(record)

        self.assertTrue(result["cross_consumer_traceability_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "traceability_output_forbidden_authority_output_detected",
            result["traceability_findings"],
        )


if __name__ == "__main__":
    unittest.main()
