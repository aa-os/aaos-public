import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.m13_authority_boundary_regression_evaluator import (  # noqa: E402
    evaluate_authority_boundary_regression_fixtures,
)


FIXTURE_SET_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m13-authority-boundary-regression-fixtures.json"
)


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class M13AuthorityBoundaryRegressionEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.fixture_set = load_json(FIXTURE_SET_PATH)

    def evaluate(self, fixture_set=None):
        return evaluate_authority_boundary_regression_fixtures(
            self.fixture_set if fixture_set is None else fixture_set
        )

    def test_valid_authority_boundary_regression_fixture_set_passes(self):
        result = self.evaluate()

        self.assertTrue(result["authority_boundary_regression_fixtures_valid"])
        self.assertFalse(result["authority_boundary_regression_fixtures_invalid"])
        self.assertTrue(result["authority_domain_coverage_complete"])
        self.assertTrue(result["authority_boundary_preserved"])
        self.assertTrue(result["release_status_future_only"])
        self.assertEqual(result["authority_boundary_findings"], [])
        self.assertEqual(result["missing_evidence"], [])

    def test_missing_176_reference_fails(self):
        fixture_set = copy.deepcopy(self.fixture_set)
        fixture_set["related_issue"] = ""

        result = self.evaluate(fixture_set)

        self.assertTrue(result["authority_boundary_regression_fixtures_invalid"])
        self.assertIn("missing_related_issue_176", result["authority_boundary_findings"])

    def test_closes_176_language_fails(self):
        fixture_set = copy.deepcopy(self.fixture_set)
        fixture_set["tracker_issue_linkage"] = "Closes #176"

        result = self.evaluate(fixture_set)

        self.assertTrue(result["authority_boundary_regression_fixtures_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "tracker_issue_176_closure_claim_detected",
            result["authority_boundary_findings"],
        )

    def test_missing_177_reference_fails(self):
        fixture_set = copy.deepcopy(self.fixture_set)
        fixture_set["runtime_approval_gate_evidence_pr"] = ""

        result = self.evaluate(fixture_set)

        self.assertTrue(result["authority_boundary_regression_fixtures_invalid"])
        self.assertIn(
            "missing_runtime_approval_gate_evidence_pr_177",
            result["authority_boundary_findings"],
        )

    def test_missing_178_reference_fails(self):
        fixture_set = copy.deepcopy(self.fixture_set)
        fixture_set["registry_drift_detection_pr"] = ""

        result = self.evaluate(fixture_set)

        self.assertTrue(result["authority_boundary_regression_fixtures_invalid"])
        self.assertIn(
            "missing_registry_drift_detection_pr_178",
            result["authority_boundary_findings"],
        )

    def test_missing_171_closed_follow_up_reference_fails(self):
        fixture_set = copy.deepcopy(self.fixture_set)
        fixture_set["closed_runtime_approval_follow_up"] = ""

        result = self.evaluate(fixture_set)

        self.assertTrue(result["authority_boundary_regression_fixtures_invalid"])
        self.assertIn(
            "missing_closed_runtime_approval_follow_up_171",
            result["authority_boundary_findings"],
        )

    def test_v012_released_claim_fails(self):
        fixture_set = copy.deepcopy(self.fixture_set)
        fixture_set["future_release_tag_path"]["released"] = True

        result = self.evaluate(fixture_set)

        self.assertTrue(result["authority_boundary_regression_fixtures_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertFalse(result["release_status_future_only"])
        self.assertIn("v0_12_0_release_claim_detected", result["authority_boundary_findings"])

    def test_m13_complete_claim_fails(self):
        fixture_set = copy.deepcopy(self.fixture_set)
        fixture_set["m13_completion_status"] = "M13 is complete."

        result = self.evaluate(fixture_set)

        self.assertTrue(result["authority_boundary_regression_fixtures_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("m13_completion_claim_detected", result["authority_boundary_findings"])

    def test_missing_required_authority_domain_fails(self):
        fixture_set = copy.deepcopy(self.fixture_set)
        fixture_set["authority_domains"].remove("external_consumer_registry")

        result = self.evaluate(fixture_set)

        self.assertTrue(result["authority_boundary_regression_fixtures_invalid"])
        self.assertTrue(result["authority_domain_coverage_incomplete"])
        self.assertIn("authority_domain_coverage_incomplete", result["authority_boundary_findings"])

    def test_missing_registry_drift_positive_fixture_fails(self):
        fixture_set = copy.deepcopy(self.fixture_set)
        fixture_set["positive_authority_boundary_fixtures"] = [
            fixture
            for fixture in fixture_set["positive_authority_boundary_fixtures"]
            if fixture["fixture_id"] != "registry_drift_detection_preserves_authority"
        ]

        result = self.evaluate(fixture_set)

        self.assertTrue(result["authority_boundary_regression_fixtures_invalid"])
        self.assertIn(
            "registry_drift_positive_fixture_missing",
            result["authority_boundary_findings"],
        )

    def test_missing_runtime_approval_positive_fixture_fails(self):
        fixture_set = copy.deepcopy(self.fixture_set)
        fixture_set["positive_authority_boundary_fixtures"] = [
            fixture
            for fixture in fixture_set["positive_authority_boundary_fixtures"]
            if fixture["fixture_id"] != "runtime_enforced_approval_evidence_preserves_authority"
        ]

        result = self.evaluate(fixture_set)

        self.assertTrue(result["authority_boundary_regression_fixtures_invalid"])
        self.assertIn(
            "runtime_approval_positive_fixture_missing",
            result["authority_boundary_findings"],
        )

    def test_missing_release_proof_linkage_positive_fixture_fails(self):
        fixture_set = copy.deepcopy(self.fixture_set)
        fixture_set["positive_authority_boundary_fixtures"] = [
            fixture
            for fixture in fixture_set["positive_authority_boundary_fixtures"]
            if fixture["fixture_id"] != "release_proof_linkage_preserves_authority"
        ]

        result = self.evaluate(fixture_set)

        self.assertTrue(result["authority_boundary_regression_fixtures_invalid"])
        self.assertIn(
            "release_proof_linkage_positive_fixture_missing",
            result["authority_boundary_findings"],
        )

    def test_unmarked_negative_fixture_fails(self):
        fixture_set = copy.deepcopy(self.fixture_set)
        fixture_set["negative_regression_fixtures"][0]["negative_fixture"] = False

        result = self.evaluate(fixture_set)

        self.assertTrue(result["authority_boundary_regression_fixtures_invalid"])
        self.assertIn(
            "negative_fixture_unmarked_registry_inclusion_as_approval",
            result["authority_boundary_findings"],
        )

    def test_registry_inclusion_as_approval_fails(self):
        result = self.evaluate_with_boundary_claim(
            "registry_inclusion_boundary",
            "Registry inclusion is approval.",
        )

        self.assertIn("registry_inclusion_approval_claim_detected", result["authority_boundary_findings"])

    def test_no_drift_detected_as_approval_fails(self):
        result = self.evaluate_with_boundary_claim(
            "no_drift_boundary",
            "no_drift_detected is approval.",
        )

        self.assertIn("no_drift_approval_claim_detected", result["authority_boundary_findings"])

    def test_registry_drift_detector_approves_consumer_fails(self):
        result = self.evaluate_with_boundary_claim(
            "registry_inclusion_boundary",
            "Registry drift detector approves a consumer.",
        )

        self.assertIn(
            "registry_drift_consumer_approval_claim_detected",
            result["authority_boundary_findings"],
        )

    def test_registry_drift_detector_approves_release_fails(self):
        result = self.evaluate_with_boundary_claim(
            "release_proof_boundary",
            "Registry drift detector approves a release.",
        )

        self.assertIn(
            "registry_drift_release_approval_claim_detected",
            result["authority_boundary_findings"],
        )

    def test_registry_drift_detector_accepts_risk_fails(self):
        result = self.evaluate_with_boundary_claim(
            "registry_inclusion_boundary",
            "Registry drift detector accepts risk.",
        )

        self.assertIn(
            "registry_drift_risk_acceptance_claim_detected",
            result["authority_boundary_findings"],
        )

    def test_registry_drift_detector_executes_fail_closed_fails(self):
        result = self.evaluate_with_boundary_claim(
            "fail_closed_boundary",
            "Registry drift detector executes fail-closed.",
        )

        self.assertIn(
            "registry_drift_fail_closed_execution_claim_detected",
            result["authority_boundary_findings"],
        )

    def test_runtime_approval_evidence_approves_execution_fails(self):
        result = self.evaluate_with_boundary_claim(
            "runtime_approval_boundary",
            "Runtime approval evidence approves execution.",
        )

        self.assertIn(
            "runtime_approval_execution_approval_claim_detected",
            result["authority_boundary_findings"],
        )

    def test_runtime_approval_evidence_seals_decision_proof_fails(self):
        result = self.evaluate_with_boundary_claim(
            "runtime_approval_boundary",
            "Runtime approval evidence seals Decision Proof.",
        )

        self.assertIn(
            "runtime_approval_decision_proof_sealing_claim_detected",
            result["authority_boundary_findings"],
        )

    def test_integration_ci_pass_as_approval_fails(self):
        result = self.evaluate_with_boundary_claim("ci_pass_boundary", "CI pass is approval.")

        self.assertIn("ci_pass_approval_claim_detected", result["authority_boundary_findings"])

    def test_traceability_linkage_as_approval_fails(self):
        result = self.evaluate_with_boundary_claim(
            "traceability_linkage_boundary",
            "Traceability linkage is approval.",
        )

        self.assertIn(
            "traceability_linkage_approval_claim_detected",
            result["authority_boundary_findings"],
        )

    def test_release_proof_linkage_as_release_approval_fails(self):
        result = self.evaluate_with_boundary_claim(
            "release_proof_boundary",
            "Release proof linkage is release approval.",
        )

        self.assertIn(
            "release_proof_release_approval_claim_detected",
            result["authority_boundary_findings"],
        )

    def test_fail_closed_recommended_as_fail_closed_executed_fails(self):
        result = self.evaluate_with_boundary_claim(
            "fail_closed_boundary",
            "fail_closed_recommended is fail_closed_executed.",
        )

        self.assertIn("fail_closed_execution_claim_detected", result["authority_boundary_findings"])

    def test_sealing_eligible_as_sealed_fails(self):
        result = self.evaluate_with_boundary_claim(
            "sealing_eligibility_boundary",
            "sealing_eligible is sealed.",
        )

        self.assertIn(
            "sealing_eligibility_sealed_claim_detected",
            result["authority_boundary_findings"],
        )

    def test_evidence_complete_as_sealed_fails(self):
        result = self.evaluate_with_boundary_claim(
            "evidence_complete_boundary",
            "evidence_complete is sealed.",
        )

        self.assertIn("evidence_complete_sealed_claim_detected", result["authority_boundary_findings"])

    def test_replay_ready_as_sealed_fails(self):
        result = self.evaluate_with_boundary_claim("replay_ready_boundary", "replay_ready is sealed.")

        self.assertIn("replay_ready_sealed_claim_detected", result["authority_boundary_findings"])

    def test_evaluator_findings_as_sealing_fails(self):
        result = self.evaluate_with_boundary_claim(
            "evaluator_findings_boundary",
            "Evaluator findings are sealing.",
        )

        self.assertIn(
            "evaluator_findings_sealing_claim_detected",
            result["authority_boundary_findings"],
        )

    def test_governance_ci_findings_as_sealing_fails(self):
        result = self.evaluate_with_boundary_claim(
            "governance_ci_findings_boundary",
            "Governance CI findings are sealing.",
        )

        self.assertIn(
            "governance_ci_findings_sealing_claim_detected",
            result["authority_boundary_findings"],
        )

    def test_nonsealed_artifact_converted_into_sealed_artifact_fails(self):
        result = self.evaluate_with_boundary_claim(
            "non_sealed_conversion_boundary",
            "Non-sealed artifact is converted into sealed artifact.",
        )

        self.assertIn(
            "nonsealed_to_sealed_conversion_claim_detected",
            result["authority_boundary_findings"],
        )

    def test_aaos_sealed_artifact_resealed_fails(self):
        result = self.evaluate_with_boundary_claim(
            "aaos_sealed_reseal_boundary",
            "AAOS-sealed artifact is re-sealed by a registry, consumer, CI, evaluator, or traceability system.",
        )

        self.assertIn("aaos_sealed_reseal_claim_detected", result["authority_boundary_findings"])

    def test_onboarding_documentation_grants_authority_fails(self):
        result = self.evaluate_with_boundary_claim(
            "onboarding_documentation_boundary",
            "Onboarding documentation grants authority.",
        )

        self.assertIn(
            "onboarding_documentation_authority_grant_claim_detected",
            result["authority_boundary_findings"],
        )

    def test_readme_status_entry_grants_authority_fails(self):
        result = self.evaluate_with_boundary_claim(
            "readme_status_boundary",
            "README status entry grants authority.",
        )

        self.assertIn(
            "readme_status_authority_grant_claim_detected",
            result["authority_boundary_findings"],
        )

    def test_external_consumer_final_governance_authority_fails(self):
        result = self.evaluate_with_boundary_claim(
            "external_consumer_boundary",
            "External consumer becomes final governance authority.",
        )

        self.assertIn(
            "external_consumer_final_authority_claim_detected",
            result["authority_boundary_findings"],
        )

    def test_final_governance_judgment_output_fails(self):
        result = self.evaluate_with_output("final_governance_judgment")

        self.assertIn("authority_transfer_claim_detected", result["authority_boundary_findings"])

    def test_audit_closed_output_fails(self):
        result = self.evaluate_with_output("audit_closed")

        self.assertIn("authority_transfer_claim_detected", result["authority_boundary_findings"])

    def test_missing_aaos_authority_statement_fails(self):
        fixture_set = copy.deepcopy(self.fixture_set)
        fixture_set["governance_boundary_statement"] = ""
        fixture_set["decision_proof_sealing_boundary_statement"] = ""
        fixture_set["aaos_retained_authority_statement"] = ""
        fixture_set["sovereignty_statement"] = ""

        result = self.evaluate(fixture_set)

        self.assertTrue(result["authority_boundary_regression_fixtures_invalid"])
        self.assertIn(
            "missing_aaos_authority_boundary_statement",
            result["authority_boundary_findings"],
        )

    def evaluate_with_boundary_claim(self, key, claim):
        fixture_set = copy.deepcopy(self.fixture_set)
        fixture_set["semantic_boundaries"][key] = claim

        result = self.evaluate(fixture_set)

        self.assertTrue(result["authority_boundary_regression_fixtures_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        return result

    def evaluate_with_output(self, output):
        fixture_set = copy.deepcopy(self.fixture_set)
        fixture_set["detector_output"] = output

        result = self.evaluate(fixture_set)

        self.assertTrue(result["authority_boundary_regression_fixtures_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        return result


if __name__ == "__main__":
    unittest.main()
