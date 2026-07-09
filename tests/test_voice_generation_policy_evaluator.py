import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.voice_generation_policy_evaluator import (  # noqa: E402
    evaluate_voice_generation_policy_fixture,
)


FIXTURE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "voxcpm-governed-voice-fixtures.json"
)

FORBIDDEN_RESULT_KEYS = {
    "voice_clone_approved",
    "impersonation_approved",
    "public_disclosure_approved",
    "regulated_deployment_approved",
    "consent_granted_by_evaluator",
    "risk_accepted",
    "fail_closed_executed",
    "rollback_executed",
    "audit_closed",
    "waiver_granted",
    "decision_proof_sealed",
    "sealed_by_voice_runtime",
    "sealed_by_evaluator",
    "authority_transferred",
    "final_governance_judgment",
    "m14_complete",
    "v0_13_0_released",
    "closes_201",
}


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class VoiceGenerationPolicyEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.fixture = load_json(FIXTURE_PATH)

    def evaluate(self, fixture=None):
        return evaluate_voice_generation_policy_fixture(
            self.fixture if fixture is None else fixture
        )

    def case_by_type(self, fixture, case_type):
        for case in fixture["fixture_cases"]:
            if case["case_type"] == case_type:
                return case
        raise AssertionError(f"Missing fixture case {case_type}")

    def case_result_by_type(self, result, case_type):
        for case_result in result["case_results"]:
            if case_result["case_type"] == case_type:
                return case_result
        raise AssertionError(f"Missing case result {case_type}")

    def assert_no_forbidden_result_keys(self, result):
        for forbidden_key in FORBIDDEN_RESULT_KEYS:
            self.assertNotIn(forbidden_key, result)

    def test_valid_multilingual_tts_case_passes_with_trace_and_disclosure_metadata(self):
        result = self.evaluate()
        case_result = self.case_result_by_type(result, "plain_multilingual_tts")
        case = self.case_by_type(self.fixture, "plain_multilingual_tts")

        self.assertTrue(result["voice_policy_fixture_valid"])
        self.assertTrue(case_result["voice_policy_case_pass"])
        self.assertTrue(case["trace_required"])
        self.assertTrue(case["replay_required"])
        self.assertTrue(case["disclosure_required"])
        self.assertTrue(case["output_label_required"])
        self.assertEqual(
            case["decision_proof_fields"]["disclosure_metadata"],
            "synthetic_voice_disclosure_present",
        )
        self.assert_no_forbidden_result_keys(result)

    def test_valid_natural_language_voice_design_without_reference_audio_passes(self):
        result = self.evaluate()
        case_result = self.case_result_by_type(
            result,
            "natural_language_voice_design_without_reference_audio",
        )
        case = self.case_by_type(
            self.fixture,
            "natural_language_voice_design_without_reference_audio",
        )

        self.assertTrue(result["voice_policy_fixture_valid"])
        self.assertTrue(case_result["voice_policy_case_pass"])
        self.assertFalse(case["protected_identity_risk"])
        self.assertFalse(case["impersonation_risk"])
        self.assertEqual(
            case["reference_audio_provenance"]["status"],
            "not_applicable_no_reference_audio",
        )

    def test_voice_cloning_without_consent_fails(self):
        fixture = copy.deepcopy(self.fixture)
        case = self.case_by_type(fixture, "voice_cloning_with_reference_audio")
        case["consent_evidence"] = {"status": "missing", "artifact_id": "missing"}
        case["decision_proof_fields"]["consent_artifact_id"] = "missing"
        case["decision_proof_fields"]["consent_scope"] = "missing"

        result = self.evaluate(fixture)

        self.assertTrue(result["voice_policy_fixture_invalid"])
        self.assertIn(
            "voice-case-003:voice_cloning_consent_missing",
            result["voice_policy_findings"],
        )

    def test_voice_cloning_without_reference_audio_provenance_fails(self):
        fixture = copy.deepcopy(self.fixture)
        case = self.case_by_type(fixture, "voice_cloning_with_reference_audio")
        case["reference_audio_provenance"] = {
            "status": "missing",
            "artifact_id": "missing",
            "hash": "missing",
        }
        case["decision_proof_fields"]["reference_audio_artifact_id"] = "missing"
        case["decision_proof_fields"]["reference_audio_hash"] = "missing"

        result = self.evaluate(fixture)

        self.assertTrue(result["voice_policy_fixture_invalid"])
        self.assertIn(
            "voice-case-003:reference_audio_provenance_missing",
            result["voice_policy_findings"],
        )

    def test_high_fidelity_cloning_without_prompt_audio_transcript_binding_fails(self):
        fixture = copy.deepcopy(self.fixture)
        case = self.case_by_type(
            fixture,
            "high_fidelity_cloning_with_prompt_audio_and_transcript",
        )
        case["prompt_audio_transcript_binding"]["bound"] = False
        case["prompt_audio_transcript_binding"]["prompt_audio_hash"] = "missing"
        case["prompt_audio_transcript_binding"]["prompt_transcript_hash"] = "missing"
        case["decision_proof_fields"]["prompt_audio_hash"] = "missing"
        case["decision_proof_fields"]["prompt_transcript_hash"] = "missing"

        result = self.evaluate(fixture)

        self.assertTrue(result["voice_policy_fixture_invalid"])
        self.assertIn(
            "voice-case-004:prompt_audio_transcript_binding_missing",
            result["voice_policy_findings"],
        )

    def test_streaming_generation_without_interrupt_capability_fails(self):
        fixture = copy.deepcopy(self.fixture)
        case = self.case_by_type(fixture, "streaming_generation")
        case["streaming_interrupt_required"] = False

        result = self.evaluate(fixture)

        self.assertTrue(result["voice_policy_fixture_invalid"])
        self.assertIn(
            "voice-case-005:streaming_interrupt_capability_missing",
            result["voice_policy_findings"],
        )

    def test_protected_identity_voice_request_fails_closed_or_requires_human_review(self):
        result = self.evaluate()
        case = self.case_by_type(self.fixture, "rejected_impersonation_scenario")
        case_result = self.case_result_by_type(result, "rejected_impersonation_scenario")

        self.assertTrue(case["protected_identity_risk"])
        self.assertTrue(case["fail_closed_recommended"] or case["human_review_required"])
        self.assertTrue(case_result["voice_policy_case_pass"])
        self.assertEqual(case["policy_gate_decision"], "fail_closed_recommended")

    def test_impersonation_scenario_fails_closed(self):
        result = self.evaluate()
        case = self.case_by_type(self.fixture, "rejected_impersonation_scenario")
        case_result = self.case_result_by_type(result, "rejected_impersonation_scenario")

        self.assertTrue(case["impersonation_risk"])
        self.assertTrue(case["fail_closed_recommended"])
        self.assertTrue(case["human_review_required"])
        self.assertTrue(case_result["voice_policy_case_pass"])
        self.assertEqual(case["expected_result"], "rejected_impersonation_scenario")

    def test_enterprise_voice_workflow_ready_for_review_but_not_approved(self):
        result = self.evaluate()
        case = self.case_by_type(
            self.fixture,
            "approved_enterprise_voice_workflow_with_trace_and_disclosure_metadata",
        )
        case_result = self.case_result_by_type(
            result,
            "approved_enterprise_voice_workflow_with_trace_and_disclosure_metadata",
        )

        self.assertTrue(case_result["voice_policy_case_pass"])
        self.assertTrue(result["ready_for_review"])
        self.assertEqual(case["policy_gate_decision"], "ready_for_review")
        self.assertEqual(case["expected_result"], "ready_for_review_not_approved")
        self.assertNotIn("voice_clone_approved", case["expected_result"])
        self.assert_no_forbidden_result_keys(result)

    def test_consent_evidence_present_treated_as_approval_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["bad_claim"] = "consent_evidence_present is approval"

        result = self.evaluate(fixture)

        self.assertTrue(result["voice_policy_fixture_invalid"])
        self.assertIn("consent_evidence_approval_claim_detected", result["voice_policy_findings"])

    def test_capability_detected_treated_as_permission_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["bad_claim"] = "capability_detected is permission"

        result = self.evaluate(fixture)

        self.assertTrue(result["voice_policy_fixture_invalid"])
        self.assertIn("capability_permission_claim_detected", result["voice_policy_findings"])

    def test_policy_gate_pass_treated_as_final_governance_judgment_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["bad_claim"] = "policy_gate_pass is final governance judgment"

        result = self.evaluate(fixture)

        self.assertTrue(result["voice_policy_fixture_invalid"])
        self.assertIn("policy_gate_final_judgment_claim_detected", result["voice_policy_findings"])

    def test_ready_for_review_treated_as_approval_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["bad_claim"] = "ready_for_review is approval"

        result = self.evaluate(fixture)

        self.assertTrue(result["voice_policy_fixture_invalid"])
        self.assertIn("ready_for_review_approval_claim_detected", result["voice_policy_findings"])

    def test_fail_closed_recommended_treated_as_executed_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["bad_claim"] = "fail_closed_recommended is fail_closed_executed"

        result = self.evaluate(fixture)

        self.assertTrue(result["voice_policy_fixture_invalid"])
        self.assertIn("fail_closed_execution_claim_detected", result["voice_policy_findings"])

    def test_evaluator_output_attempting_to_seal_decision_proof_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["evaluator_output"] = "decision_proof_sealed"

        result = self.evaluate(fixture)

        self.assertTrue(result["voice_policy_fixture_invalid"])
        self.assertIn(
            "forbidden_output_claim_detected:decision_proof_sealed",
            result["voice_policy_findings"],
        )

    def test_evaluator_output_attempting_to_transfer_authority_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["evaluator_output"] = "authority_transferred"

        result = self.evaluate(fixture)

        self.assertTrue(result["voice_policy_fixture_invalid"])
        self.assertIn(
            "forbidden_output_claim_detected:authority_transferred",
            result["voice_policy_findings"],
        )

    def test_evaluator_output_attempting_to_declare_m14_complete_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["evaluator_output"] = "m14_complete"

        result = self.evaluate(fixture)

        self.assertTrue(result["voice_policy_fixture_invalid"])
        self.assertIn(
            "forbidden_output_claim_detected:m14_complete",
            result["voice_policy_findings"],
        )

    def test_evaluator_output_attempting_to_release_v013_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["evaluator_output"] = "v0_13_0_released"

        result = self.evaluate(fixture)

        self.assertTrue(result["voice_policy_fixture_invalid"])
        self.assertIn(
            "forbidden_output_claim_detected:v0_13_0_released",
            result["voice_policy_findings"],
        )

    def test_evaluator_output_attempting_to_close_201_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["evaluator_output"] = "closes_201"

        result = self.evaluate(fixture)

        self.assertTrue(result["voice_policy_fixture_invalid"])
        self.assertIn(
            "forbidden_output_claim_detected:closes_201",
            result["voice_policy_findings"],
        )


if __name__ == "__main__":
    unittest.main()
