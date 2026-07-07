import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.m12_multi_consumer_semantics_evaluator import (  # noqa: E402
    evaluate_m12_multi_consumer_semantics,
)


SEMANTICS_EXAMPLE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m12-multi-consumer-sealed-nonsealed-semantics.json"
)


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class M12MultiConsumerSemanticsEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.semantics = load_json(SEMANTICS_EXAMPLE_PATH)

    def test_multi_consumer_semantics_artifact_passes(self):
        result = evaluate_m12_multi_consumer_semantics(self.semantics)

        self.assertTrue(result["multi_consumer_semantics_valid"])
        self.assertTrue(result["sealed_nonsealed_semantics_preserved"])
        self.assertTrue(result["consumer_matrix_complete"])
        self.assertTrue(result["authority_boundary_preserved"])
        self.assertTrue(result["release_status_future_only"])
        self.assertEqual(result["semantics_findings"], [])
        self.assertEqual(result["missing_evidence"], [])

    def test_missing_168_reference_fails(self):
        record = copy.deepcopy(self.semantics)
        record["related_issue"] = ""

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertIn("missing_related_issue_168", result["semantics_findings"])

    def test_closes_168_language_fails(self):
        record = copy.deepcopy(self.semantics)
        record["tracker_issue_linkage"] = "Closes #168"

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "tracker_issue_168_closure_claim_detected",
            result["semantics_findings"],
        )

    def test_missing_169_reference_fails(self):
        record = copy.deepcopy(self.semantics)
        record["m12_consumer_registry_pr"] = ""

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertIn("missing_m12_consumer_registry_pr_169", result["semantics_findings"])

    def test_missing_170_reference_fails(self):
        record = copy.deepcopy(self.semantics)
        record["m12_integration_ci_check_specimen_pr"] = ""

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertIn(
            "missing_m12_integration_ci_check_specimen_pr_170",
            result["semantics_findings"],
        )

    def test_missing_172_reference_fails(self):
        record = copy.deepcopy(self.semantics)
        record["m12_cross_consumer_traceability_pr"] = ""

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertIn(
            "missing_m12_cross_consumer_traceability_pr_172",
            result["semantics_findings"],
        )

    def test_v011_release_claim_fails(self):
        record = copy.deepcopy(self.semantics)
        record["release_status_path"]["v0_11_0_target_release_state"] = (
            "v0.11.0 is released."
        )

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("v0_11_0_release_claim_detected", result["semantics_findings"])

    def test_m12_complete_claim_fails(self):
        record = copy.deepcopy(self.semantics)
        record["artifact_status"] = "m12_complete"

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("m12_completion_claim_detected", result["semantics_findings"])

    def test_fewer_than_three_consumer_types_fails(self):
        record = copy.deepcopy(self.semantics)
        record["multi_consumer_matrix"] = record["multi_consumer_matrix"][:2]

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertTrue(result["consumer_matrix_incomplete"])
        self.assertIn("consumer_matrix_incomplete", result["semantics_findings"])

    def test_missing_sealed_artifact_handling_fails(self):
        record = copy.deepcopy(self.semantics)
        record["multi_consumer_matrix"][0]["sealed_artifact_handling"] = ""

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertTrue(result["consumer_matrix_incomplete"])
        self.assertIn("missing_sealed_artifact_handling", result["semantics_findings"])

    def test_missing_non_sealed_artifact_handling_fails(self):
        record = copy.deepcopy(self.semantics)
        record["multi_consumer_matrix"][0]["non_sealed_artifact_handling"] = ""

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertTrue(result["consumer_matrix_incomplete"])
        self.assertIn("missing_non_sealed_artifact_handling", result["semantics_findings"])

    def test_consumer_reseals_aaos_sealed_artifact_fails(self):
        record = copy.deepcopy(self.semantics)
        record["multi_consumer_matrix"][0]["sealed_artifact_handling"] = (
            "Consumer re-seals AAOS-sealed artifact."
        )

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertTrue(result["sealed_nonsealed_semantics_violation"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "consumer_semantics_authority_claim_detected",
            result["semantics_findings"],
        )

    def test_consumer_converts_nonsealed_artifact_into_sealed_fails(self):
        record = copy.deepcopy(self.semantics)
        record["multi_consumer_matrix"][0]["non_sealed_artifact_handling"] = (
            "Consumer converts non-sealed artifact into sealed artifact."
        )

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertTrue(result["sealed_nonsealed_semantics_violation"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "consumer_semantics_authority_claim_detected",
            result["semantics_findings"],
        )

    def test_sealing_eligible_as_sealed_fails(self):
        record = copy.deepcopy(self.semantics)
        record["required_semantics"]["sealing_eligibility_boundary"] = (
            "sealing_eligible is sealed."
        )

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertTrue(result["sealed_nonsealed_semantics_violation"])
        self.assertIn(
            "sealing_eligibility_sealed_claim_detected",
            result["semantics_findings"],
        )

    def test_evidence_complete_as_sealed_fails(self):
        record = copy.deepcopy(self.semantics)
        record["required_semantics"]["evidence_complete_boundary"] = (
            "evidence_complete is sealed."
        )

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertTrue(result["sealed_nonsealed_semantics_violation"])
        self.assertIn("evidence_complete_sealed_claim_detected", result["semantics_findings"])

    def test_replay_ready_as_sealed_fails(self):
        record = copy.deepcopy(self.semantics)
        record["required_semantics"]["replay_ready_boundary"] = (
            "replay_ready is sealed."
        )

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertTrue(result["sealed_nonsealed_semantics_violation"])
        self.assertIn("replay_ready_sealed_claim_detected", result["semantics_findings"])

    def test_evaluator_findings_as_sealing_fails(self):
        record = copy.deepcopy(self.semantics)
        record["required_semantics"]["evaluator_findings_boundary"] = (
            "evaluator findings are sealing."
        )

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertTrue(result["sealed_nonsealed_semantics_violation"])
        self.assertIn(
            "evaluator_findings_sealing_claim_detected",
            result["semantics_findings"],
        )

    def test_governance_ci_findings_as_sealing_fails(self):
        record = copy.deepcopy(self.semantics)
        record["required_semantics"]["governance_ci_findings_boundary"] = (
            "governance CI findings are sealing."
        )

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertTrue(result["sealed_nonsealed_semantics_violation"])
        self.assertIn(
            "governance_ci_findings_sealing_claim_detected",
            result["semantics_findings"],
        )

    def test_release_proof_linkage_as_release_approval_fails(self):
        record = copy.deepcopy(self.semantics)
        record["required_semantics"]["release_proof_boundary"] = (
            "Release proof linkage is release approval."
        )

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "release_proof_release_approval_claim_detected",
            result["semantics_findings"],
        )

    def test_registry_inclusion_as_approval_fails(self):
        record = copy.deepcopy(self.semantics)
        record["required_semantics"]["registry_inclusion_boundary"] = (
            "Registry inclusion is approval."
        )

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "registry_inclusion_approval_claim_detected",
            result["semantics_findings"],
        )

    def test_ci_pass_as_approval_fails(self):
        record = copy.deepcopy(self.semantics)
        record["required_semantics"]["ci_pass_boundary"] = "CI pass is approval."

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("ci_pass_approval_claim_detected", result["semantics_findings"])

    def test_traceability_linkage_as_approval_fails(self):
        record = copy.deepcopy(self.semantics)
        record["required_semantics"]["traceability_linkage_boundary"] = (
            "Traceability linkage is approval."
        )

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "traceability_linkage_approval_claim_detected",
            result["semantics_findings"],
        )

    def test_fail_closed_recommended_as_executed_fails(self):
        record = copy.deepcopy(self.semantics)
        record["required_semantics"]["fail_closed_boundary"] = (
            "fail_closed_recommended is fail_closed_executed."
        )

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("fail_closed_execution_claim_detected", result["semantics_findings"])

    def test_final_governance_judgment_output_fails(self):
        record = copy.deepcopy(self.semantics)
        record["multi_consumer_matrix"][0]["semantics_outputs"].append(
            "final_governance_judgment"
        )

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "semantics_output_forbidden_authority_output_detected",
            result["semantics_findings"],
        )

    def test_audit_closed_output_fails(self):
        record = copy.deepcopy(self.semantics)
        record["multi_consumer_matrix"][1]["semantics_outputs"].append("audit_closed")

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "semantics_output_forbidden_authority_output_detected",
            result["semantics_findings"],
        )

    def test_missing_aaos_authority_statement_fails(self):
        record = copy.deepcopy(self.semantics)
        record["aaos_retained_authority_statement"] = ""
        record["governance_boundary_statement"] = ""
        record["required_semantics"]["decision_proof_sealing_boundary_statement"] = ""
        record["required_semantics"]["sovereignty_statement"] = ""

        result = evaluate_m12_multi_consumer_semantics(record)

        self.assertTrue(result["multi_consumer_semantics_invalid"])
        self.assertIn(
            "missing_aaos_authority_boundary_statement",
            result["semantics_findings"],
        )


if __name__ == "__main__":
    unittest.main()
