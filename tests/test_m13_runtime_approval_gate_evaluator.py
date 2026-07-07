import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.m13_runtime_approval_gate_evaluator import (  # noqa: E402
    evaluate_approval_gate_trace,
    evaluate_runtime_approval_gate_evidence,
)


APPROVAL_GATE_EVIDENCE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m13-runtime-enforced-approval-gate-evidence.json"
)


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def fixture_by_id(artifact, fixture_id):
    for fixture in artifact["regression_fixtures"]:
        if fixture["fixture_id"] == fixture_id:
            return fixture
    raise AssertionError(f"missing fixture {fixture_id}")


class M13RuntimeApprovalGateEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.artifact = load_json(APPROVAL_GATE_EVIDENCE_PATH)

    def evaluate(self, artifact=None):
        return evaluate_runtime_approval_gate_evidence(
            self.artifact if artifact is None else artifact
        )

    def test_runtime_approval_gate_evidence_passes(self):
        result = self.evaluate()

        self.assertTrue(result["runtime_approval_gate_evidence_valid"])
        self.assertTrue(result["approval_gate_modes_present"])
        self.assertTrue(result["required_enforced_gate_trace_fields_present"])
        self.assertTrue(result["regression_fixture_coverage_complete"])
        self.assertTrue(result["authority_boundary_preserved"])
        self.assertEqual(result["runtime_approval_gate_findings"], [])
        self.assertEqual(result["missing_evidence"], [])

    def test_missing_m13_tracker_issue_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["related_issue"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["runtime_approval_gate_evidence_invalid"])
        self.assertIn("missing_related_issue_176", result["runtime_approval_gate_findings"])

    def test_missing_runtime_approval_issue_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["runtime_approval_gate_issue"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["runtime_approval_gate_evidence_invalid"])
        self.assertIn(
            "missing_runtime_approval_gate_issue_171",
            result["runtime_approval_gate_findings"],
        )

    def test_missing_gate_mode_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["approval_gate_modes"] = [
            mode for mode in artifact["approval_gate_modes"] if mode["mode"] != "enforced"
        ]

        result = self.evaluate(artifact)

        self.assertTrue(result["runtime_approval_gate_evidence_invalid"])
        self.assertFalse(result["approval_gate_modes_present"])
        self.assertIn("approval_gate_modes_missing", result["runtime_approval_gate_findings"])

    def test_missing_required_trace_field_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["required_enforced_gate_trace_fields"].remove("approval_event_id")

        result = self.evaluate(artifact)

        self.assertTrue(result["runtime_approval_gate_evidence_invalid"])
        self.assertFalse(result["required_enforced_gate_trace_fields_present"])
        self.assertIn(
            "required_enforced_gate_trace_fields_missing",
            result["runtime_approval_gate_findings"],
        )

    def test_valid_halt_approval_release_execution_trace_passes(self):
        trace = fixture_by_id(
            self.artifact, "valid_halt_approval_release_execution_trace"
        )["trace"]

        result = evaluate_approval_gate_trace(trace)

        self.assertTrue(result["approval_gate_trace_valid"])
        self.assertTrue(result["enforced_gate_trace_valid"])
        self.assertTrue(result["enforcement_satisfied"])
        self.assertFalse(result["fail_closed_recommended"])
        self.assertEqual(result["trace_findings"], [])

    def test_observed_only_trace_is_observation_not_enforcement(self):
        trace = fixture_by_id(self.artifact, "observed_only_trace")["trace"]

        result = evaluate_approval_gate_trace(trace)

        self.assertTrue(result["approval_gate_trace_valid"])
        self.assertTrue(result["observed_trace_valid"])
        self.assertFalse(result["enforced_gate_trace_valid"])
        self.assertFalse(result["enforcement_satisfied"])
        self.assertFalse(result["review_required"])

    def test_post_facto_advisory_approval_fails_enforced_gate_verification(self):
        trace = fixture_by_id(self.artifact, "post_facto_advisory_approval")["trace"]

        result = evaluate_approval_gate_trace(trace)

        self.assertTrue(result["approval_gate_trace_invalid"])
        self.assertTrue(result["enforced_gate_trace_invalid"])
        self.assertTrue(result["fail_closed_recommended"])
        self.assertIn("post_facto_approval_detected", result["trace_findings"])

    def test_approval_state_only_trace_fails_enforced_gate_verification(self):
        trace = fixture_by_id(self.artifact, "approval_state_only_trace")["trace"]

        result = evaluate_approval_gate_trace(trace)

        self.assertTrue(result["approval_gate_trace_invalid"])
        self.assertTrue(result["enforced_gate_trace_invalid"])
        self.assertTrue(result["fail_closed_recommended"])
        self.assertIn("missing_enforced_trace_blocked_tool_call_id", result["trace_findings"])
        self.assertIn("approval_binding_missing", result["trace_findings"])

    def test_advisory_approval_claimed_as_enforced_fails(self):
        trace = copy.deepcopy(
            fixture_by_id(self.artifact, "post_facto_advisory_approval")["trace"]
        )
        trace["satisfies_enforced_approval"] = True

        result = evaluate_approval_gate_trace(trace)

        self.assertTrue(result["approval_gate_trace_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("advisory_trace_claimed_as_enforced", result["trace_findings"])

    def test_post_approval_ordering_fails(self):
        trace = copy.deepcopy(
            fixture_by_id(self.artifact, "valid_halt_approval_release_execution_trace")[
                "trace"
            ]
        )
        trace["approval_timestamp"] = "2026-07-07T09:31:10Z"

        result = evaluate_approval_gate_trace(trace)

        self.assertTrue(result["approval_gate_trace_invalid"])
        self.assertTrue(result["fail_closed_recommended"])
        self.assertIn("approval_ordering_invalid", result["trace_findings"])

    def test_missing_approval_binding_fails_closed(self):
        trace = copy.deepcopy(
            fixture_by_id(self.artifact, "valid_halt_approval_release_execution_trace")[
                "trace"
            ]
        )
        trace.pop("approval_binding")

        result = evaluate_approval_gate_trace(trace)

        self.assertTrue(result["approval_gate_trace_invalid"])
        self.assertTrue(result["fail_closed_recommended"])
        self.assertIn("approval_binding_missing", result["trace_findings"])

    def test_missing_gate_ordering_evidence_fails_closed(self):
        trace = copy.deepcopy(
            fixture_by_id(self.artifact, "valid_halt_approval_release_execution_trace")[
                "trace"
            ]
        )
        trace["gate_event"].pop("occurred_at")

        result = evaluate_approval_gate_trace(trace)

        self.assertTrue(result["approval_gate_trace_invalid"])
        self.assertTrue(result["fail_closed_recommended"])
        self.assertIn("gate_event_ordering_invalid", result["trace_findings"])

    def test_forbidden_authority_output_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["evaluator_outputs"] = ["release_approved"]

        result = self.evaluate(artifact)

        self.assertTrue(result["runtime_approval_gate_evidence_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "authority_transfer_claim_detected",
            result["runtime_approval_gate_findings"],
        )

    def test_m11_m12_reopen_claim_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["m12_status_boundary"] = "M12 reopened by this hardening artifact."

        result = self.evaluate(artifact)

        self.assertTrue(result["runtime_approval_gate_evidence_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "completed_milestone_reopen_claim_detected",
            result["runtime_approval_gate_findings"],
        )

    def test_missing_aaos_authority_statement_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["governance_boundary_statement"] = ""
        artifact["decision_proof_sealing_boundary_statement"] = ""
        artifact["aaos_retained_authority_statement"] = ""
        artifact["sovereignty_statement"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["runtime_approval_gate_evidence_invalid"])
        self.assertIn(
            "missing_aaos_authority_boundary_statement",
            result["runtime_approval_gate_findings"],
        )


if __name__ == "__main__":
    unittest.main()
