import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.public_issue_exfiltration_gate_evaluator import (  # noqa: E402
    evaluate_public_issue_exfiltration_gate_fixture,
)


FIXTURE_SET_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m14-public-issue-exfiltration-gate-fixtures.json"
)


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class PublicIssueExfiltrationGateEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.fixture_set = load_json(FIXTURE_SET_PATH)

    def evaluate(self, fixture_set=None):
        return evaluate_public_issue_exfiltration_gate_fixture(
            self.fixture_set if fixture_set is None else fixture_set
        )

    def case_result(self, result, case_type):
        return next(
            case_result
            for case_result in result["case_results"]
            if case_result["case_type"] == case_type
        )

    def fixture_case(self, fixture_set, case_type):
        return next(
            case
            for case in fixture_set["fixture_cases"]
            if case["case_type"] == case_type
        )

    def assert_valid_blocked_case(self, case_type):
        result = self.evaluate()
        case_result = self.case_result(result, case_type)

        self.assertTrue(result["public_issue_exfiltration_gate_valid"])
        self.assertFalse(result["public_issue_exfiltration_gate_invalid"])
        self.assertTrue(case_result["case_valid"])
        self.assertTrue(case_result["untrusted_input_detected"])
        self.assertTrue(case_result["public_output_blocked"])
        self.assertFalse(case_result["public_output_allowed"])
        self.assertEqual(case_result["findings"], [])
        return case_result

    def assert_forbidden_output_rejected(self, output):
        fixture_set = copy.deepcopy(self.fixture_set)
        fixture_set["simulated_evaluator_output"] = output

        result = self.evaluate(fixture_set)

        self.assertTrue(result["public_issue_exfiltration_gate_invalid"])
        self.assertIn(
            f"forbidden_output_claim_detected:{output}",
            result["public_issue_exfiltration_gate_findings"],
        )

    def test_malicious_public_issue_requesting_private_repo_summary_is_blocked(self):
        self.assert_valid_blocked_case(
            "malicious_public_issue_requesting_private_repo_summary"
        )

    def test_public_pr_comment_prompt_injection_against_privileged_context_is_blocked(self):
        case_result = self.assert_valid_blocked_case(
            "public_pr_comment_prompt_injection_against_privileged_repo_context"
        )
        self.assertTrue(case_result["privileged_context_detected"])
        self.assertTrue(case_result["human_review_required"])

    def test_public_discussion_requesting_private_config_excerpt_is_blocked(self):
        self.assert_valid_blocked_case(
            "public_discussion_requesting_cross_repo_private_config_excerpt"
        )

    def test_public_issue_requesting_secret_like_strings_is_blocked(self):
        case_result = self.assert_valid_blocked_case(
            "public_issue_requesting_secret_like_strings_or_environment_variables"
        )
        self.assertTrue(case_result["redaction_required"])

    def test_public_issue_attempting_to_extract_internal_file_paths_is_blocked(self):
        self.assert_valid_blocked_case(
            "public_issue_attempting_to_extract_internal_file_paths"
        )

    def test_public_output_draft_containing_private_context_is_blocked(self):
        self.assert_valid_blocked_case(
            "public_output_draft_containing_private_context_derived_content"
        )

    def test_public_triggered_workflow_with_excessive_read_scope_requires_review(self):
        case_result = self.assert_valid_blocked_case(
            "public_triggered_workflow_with_excessive_read_scope"
        )
        self.assertTrue(case_result["human_review_required"])
        self.assertTrue(case_result["fail_closed_recommended"])
        self.assertTrue(case_result["rollback_recommended"])

    def test_privileged_context_plus_public_output_requires_human_review(self):
        result = self.evaluate()
        case_result = self.case_result(
            result,
            "human_review_required_for_privileged_context_and_public_output",
        )

        self.assertTrue(result["public_issue_exfiltration_gate_valid"])
        self.assertTrue(case_result["case_valid"])
        self.assertTrue(case_result["privileged_context_detected"])
        self.assertTrue(case_result["human_review_required"])
        self.assertFalse(case_result["public_output_allowed"])

    def test_public_only_issue_response_without_privileged_context_is_allowed(self):
        result = self.evaluate()
        case_result = self.case_result(
            result,
            "allowed_public_only_issue_response_no_privileged_context",
        )

        self.assertTrue(result["public_issue_exfiltration_gate_valid"])
        self.assertTrue(case_result["case_valid"])
        self.assertTrue(case_result["untrusted_input_detected"])
        self.assertFalse(case_result["privileged_context_detected"])
        self.assertTrue(case_result["public_output_allowed"])
        self.assertFalse(case_result["human_review_required"])

    def test_maintainer_reviewed_redacted_response_is_ready_but_not_approved(self):
        result = self.evaluate()
        case_result = self.case_result(
            result,
            "allowed_maintainer_reviewed_redacted_response",
        )

        self.assertTrue(result["public_issue_exfiltration_gate_valid"])
        self.assertTrue(case_result["case_valid"])
        self.assertTrue(case_result["ready_for_review"])
        self.assertTrue(case_result["human_review_required"])
        self.assertFalse(case_result["public_output_allowed"])
        self.assertNotIn("public_disclosure_approved", result)
        self.assertNotIn("public_disclosure_approved", case_result)

    def test_public_issue_input_not_classified_untrusted_input_fails(self):
        fixture_set = copy.deepcopy(self.fixture_set)
        case = self.fixture_case(
            fixture_set,
            "malicious_public_issue_requesting_private_repo_summary",
        )
        case["input_trust_classification"] = "trusted_input"
        case["decision_proof_fields"]["input_trust_classification"] = "trusted_input"

        result = self.evaluate(fixture_set)

        self.assertTrue(result["public_issue_exfiltration_gate_invalid"])
        self.assertIn(
            "public-exfil-case-001:public_trigger_not_classified_untrusted_input",
            result["public_issue_exfiltration_gate_findings"],
        )

    def test_private_context_access_allowed_for_public_trigger_fails(self):
        fixture_set = copy.deepcopy(self.fixture_set)
        case = self.fixture_case(
            fixture_set,
            "malicious_public_issue_requesting_private_repo_summary",
        )
        case["private_context_access_allowed"] = True
        case["decision_proof_fields"]["private_context_access_decision"] = "allowed"

        result = self.evaluate(fixture_set)

        self.assertTrue(result["public_issue_exfiltration_gate_invalid"])
        self.assertIn(
            "public-exfil-case-001:private_context_access_allowed_for_public_trigger",
            result["public_issue_exfiltration_gate_findings"],
        )

    def test_output_gate_pass_as_public_disclosure_approval_fails(self):
        fixture_set = copy.deepcopy(self.fixture_set)
        case = self.fixture_case(
            fixture_set,
            "allowed_public_only_issue_response_no_privileged_context",
        )
        case["invalid_boundary_claim"] = (
            "output_gate_pass is public disclosure approval."
        )

        result = self.evaluate(fixture_set)

        self.assertTrue(result["public_issue_exfiltration_gate_invalid"])
        self.assertIn(
            "output_gate_pass_approval_claim_detected",
            result["public_issue_exfiltration_gate_findings"],
        )

    def test_human_review_required_as_audit_closure_fails(self):
        fixture_set = copy.deepcopy(self.fixture_set)
        case = self.fixture_case(
            fixture_set,
            "human_review_required_for_privileged_context_and_public_output",
        )
        case["invalid_boundary_claim"] = "human_review_required is audit closure."

        result = self.evaluate(fixture_set)

        self.assertTrue(result["public_issue_exfiltration_gate_invalid"])
        self.assertIn(
            "human_review_audit_closure_claim_detected",
            result["public_issue_exfiltration_gate_findings"],
        )

    def test_fail_closed_recommended_as_executed_fails(self):
        fixture_set = copy.deepcopy(self.fixture_set)
        case = self.fixture_case(
            fixture_set,
            "malicious_public_issue_requesting_private_repo_summary",
        )
        case["invalid_boundary_claim"] = (
            "fail_closed_recommended is fail_closed_executed."
        )

        result = self.evaluate(fixture_set)

        self.assertTrue(result["public_issue_exfiltration_gate_invalid"])
        self.assertIn(
            "fail_closed_execution_claim_detected",
            result["public_issue_exfiltration_gate_findings"],
        )

    def test_rollback_recommended_as_executed_fails(self):
        fixture_set = copy.deepcopy(self.fixture_set)
        case = self.fixture_case(
            fixture_set,
            "malicious_public_issue_requesting_private_repo_summary",
        )
        case["invalid_boundary_claim"] = (
            "rollback_recommended is rollback_executed."
        )

        result = self.evaluate(fixture_set)

        self.assertTrue(result["public_issue_exfiltration_gate_invalid"])
        self.assertIn(
            "rollback_execution_claim_detected",
            result["public_issue_exfiltration_gate_findings"],
        )

    def test_evaluator_output_attempting_to_publish_private_repo_content_fails(self):
        self.assert_forbidden_output_rejected("private_repo_content_published")

    def test_evaluator_output_attempting_to_disclose_secrets_fails(self):
        self.assert_forbidden_output_rejected("secret_disclosed")

    def test_evaluator_output_attempting_to_seal_decision_proof_fails(self):
        self.assert_forbidden_output_rejected("decision_proof_sealed")

    def test_evaluator_output_attempting_to_transfer_authority_fails(self):
        self.assert_forbidden_output_rejected("authority_transferred")

    def test_evaluator_output_attempting_to_declare_m14_complete_fails(self):
        self.assert_forbidden_output_rejected("m14_complete")

    def test_evaluator_output_attempting_to_release_v0130_fails(self):
        self.assert_forbidden_output_rejected("v0_13_0_released")

    def test_evaluator_output_attempting_to_close_201_fails(self):
        self.assert_forbidden_output_rejected("closes_201")


if __name__ == "__main__":
    unittest.main()
