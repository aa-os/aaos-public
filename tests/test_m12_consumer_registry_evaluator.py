import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.m12_consumer_registry_evaluator import (  # noqa: E402
    evaluate_m12_consumer_registry,
)


REGISTRY_EXAMPLE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m12-consumer-registry-pattern.json"
)


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class M12ConsumerRegistryEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.registry = load_json(REGISTRY_EXAMPLE_PATH)

    def test_consumer_registry_pattern_passes(self):
        result = evaluate_m12_consumer_registry(self.registry)

        self.assertTrue(result["consumer_registry_valid"])
        self.assertTrue(result["required_registry_fields_present"])
        self.assertTrue(result["compliant_consumer_entry_present"])
        self.assertTrue(result["negative_consumer_fixture_present"])
        self.assertTrue(result["authority_boundary_preserved"])
        self.assertTrue(result["sealed_nonsealed_semantics_preserved"])
        self.assertTrue(result["release_status_future_only"])
        self.assertEqual(result["registry_findings"], [])
        self.assertEqual(result["missing_evidence"], [])

    def test_missing_required_fields_fail(self):
        record = copy.deepcopy(self.registry)
        del record["registry_scope"]
        del record["target_future_release"]

        result = evaluate_m12_consumer_registry(record)

        self.assertTrue(result["consumer_registry_invalid"])
        self.assertTrue(result["required_registry_fields_missing"])
        self.assertIn("missing_registry_scope", result["registry_findings"])
        self.assertIn(
            "missing_target_future_release_v0_11_0",
            result["registry_findings"],
        )

    def test_missing_compliant_consumer_entry_fails(self):
        record = copy.deepcopy(self.registry)
        record["consumer_entries"] = []

        result = evaluate_m12_consumer_registry(record)

        self.assertTrue(result["consumer_registry_invalid"])
        self.assertTrue(result["compliant_consumer_entry_missing"])
        self.assertIn("compliant_consumer_entry_missing", result["registry_findings"])

    def test_missing_negative_fixture_fails(self):
        record = copy.deepcopy(self.registry)
        record["negative_consumer_registry_fixtures"] = []

        result = evaluate_m12_consumer_registry(record)

        self.assertTrue(result["consumer_registry_invalid"])
        self.assertTrue(result["negative_consumer_fixture_missing"])
        self.assertIn("negative_consumer_fixture_missing", result["registry_findings"])

    def test_forbidden_authority_action_leakage_fails(self):
        record = copy.deepcopy(self.registry)
        record["consumer_entries"][0]["allowed_consumption_actions"].append(
            "seal_decision_proof"
        )

        result = evaluate_m12_consumer_registry(record)

        self.assertTrue(result["consumer_registry_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("forbidden_authority_action_allowed", result["registry_findings"])
        self.assertIn(
            "compliant_consumer_entry_claims_authority",
            result["registry_findings"],
        )

    def test_v011_release_claim_fails(self):
        record = copy.deepcopy(self.registry)
        record["release_status_path"]["v0_11_0_target_release_state"] = (
            "v0.11.0 is released."
        )

        result = evaluate_m12_consumer_registry(record)

        self.assertTrue(result["consumer_registry_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("v0_11_0_release_claim_detected", result["registry_findings"])

    def test_m12_complete_claim_fails(self):
        record = copy.deepcopy(self.registry)
        record["registry_status"] = "m12_complete"

        result = evaluate_m12_consumer_registry(record)

        self.assertTrue(result["consumer_registry_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("m12_completion_claim_detected", result["registry_findings"])

    def test_closes_168_language_fails(self):
        record = copy.deepcopy(self.registry)
        record["tracker_issue_linkage"] = "Closes #168"

        result = evaluate_m12_consumer_registry(record)

        self.assertTrue(result["consumer_registry_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "tracker_issue_168_closure_claim_detected",
            result["registry_findings"],
        )

    def test_registry_inclusion_as_approval_fails(self):
        record = copy.deepcopy(self.registry)
        record["registry_inclusion_boundary"] = "Registry inclusion is approval."

        result = evaluate_m12_consumer_registry(record)

        self.assertTrue(result["consumer_registry_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "registry_inclusion_approval_claim_detected",
            result["registry_findings"],
        )

    def test_ci_pass_as_approval_fails(self):
        record = copy.deepcopy(self.registry)
        record["ci_pass_boundary"] = "CI pass is approval."

        result = evaluate_m12_consumer_registry(record)

        self.assertTrue(result["consumer_registry_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("ci_pass_approval_claim_detected", result["registry_findings"])

    def test_release_proof_linkage_as_release_approval_fails(self):
        record = copy.deepcopy(self.registry)
        record["release_proof_boundary"] = (
            "Release proof linkage is release approval."
        )

        result = evaluate_m12_consumer_registry(record)

        self.assertTrue(result["consumer_registry_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "release_proof_release_approval_claim_detected",
            result["registry_findings"],
        )

    def test_fail_closed_recommended_as_executed_fails(self):
        record = copy.deepcopy(self.registry)
        record["fail_closed_boundary"] = (
            "fail_closed_recommended is fail_closed_executed."
        )

        result = evaluate_m12_consumer_registry(record)

        self.assertTrue(result["consumer_registry_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("fail_closed_execution_claim_detected", result["registry_findings"])

    def test_sealing_eligible_as_sealed_fails(self):
        record = copy.deepcopy(self.registry)
        record["sealed_nonsealed_consumption_semantics"][
            "sealing_eligibility_boundary"
        ] = "sealing_eligible is sealed."

        result = evaluate_m12_consumer_registry(record)

        self.assertTrue(result["consumer_registry_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "sealing_eligibility_sealed_claim_detected",
            result["registry_findings"],
        )

    def test_aaos_authority_statement_missing_fails(self):
        record = copy.deepcopy(self.registry)
        record["decision_proof_sealing_boundary_statement"] = ""
        record["aaos_retained_authority_statement"] = ""
        record["sovereignty_statement"] = ""

        result = evaluate_m12_consumer_registry(record)

        self.assertTrue(result["consumer_registry_invalid"])
        self.assertIn(
            "missing_aaos_authority_boundary_statement",
            result["registry_findings"],
        )


if __name__ == "__main__":
    unittest.main()
