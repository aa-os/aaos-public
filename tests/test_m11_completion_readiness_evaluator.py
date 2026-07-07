import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.m11_completion_readiness_evaluator import (  # noqa: E402
    evaluate_m11_completion_readiness_checklist,
)


CHECKLIST_EXAMPLE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m11-completion-readiness-checklist.json"
)


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class M11CompletionReadinessEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.checklist = load_json(CHECKLIST_EXAMPLE_PATH)

    def test_completion_readiness_checklist_passes(self):
        result = evaluate_m11_completion_readiness_checklist(self.checklist)

        self.assertTrue(result["m11_completion_readiness_valid"])
        self.assertTrue(result["expected_output_coverage_complete"])
        self.assertTrue(result["release_status_path_present"])
        self.assertTrue(result["authority_boundary_preserved"])
        self.assertEqual(result["readiness_findings"], [])
        self.assertEqual(result["missing_evidence"], [])

    def test_completion_readiness_detects_missing_expected_output(self):
        record = copy.deepcopy(self.checklist)
        del record["expected_m11_output_coverage"][
            "integration_facing_examples"
        ]

        result = evaluate_m11_completion_readiness_checklist(record)

        self.assertTrue(result["m11_completion_readiness_invalid"])
        self.assertTrue(result["expected_output_coverage_incomplete"])
        self.assertIn(
            "missing_expected_output_integration_facing_examples",
            result["readiness_findings"],
        )

    def test_completion_readiness_detects_unrepresented_expected_output(self):
        record = copy.deepcopy(self.checklist)
        record["expected_m11_output_coverage"][
            "release_proof_linkage_for_pilot_package"
        ]["represented"] = False

        result = evaluate_m11_completion_readiness_checklist(record)

        self.assertTrue(result["m11_completion_readiness_invalid"])
        self.assertTrue(result["expected_output_coverage_incomplete"])
        self.assertIn(
            "expected_output_release_proof_linkage_for_pilot_package_not_represented",
            result["readiness_findings"],
        )

    def test_completion_readiness_detects_tracker_closure_language(self):
        record = copy.deepcopy(self.checklist)
        record["tracker_issue_linkage"] = "Closes #120"

        result = evaluate_m11_completion_readiness_checklist(record)

        self.assertTrue(result["m11_completion_readiness_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "tracker_issue_120_closure_claim_detected",
            result["readiness_findings"],
        )

    def test_completion_readiness_detects_v010_release_claim(self):
        record = copy.deepcopy(self.checklist)
        record["release_status_path"]["v0_10_0_completion_release_path"] = (
            "v0.10.0 is released."
        )

        result = evaluate_m11_completion_readiness_checklist(record)

        self.assertTrue(result["m11_completion_readiness_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "v0_10_0_release_claim_detected",
            result["readiness_findings"],
        )

    def test_completion_readiness_detects_m11_completion_claim(self):
        record = copy.deepcopy(self.checklist)
        record["readiness_state"] = "m11_complete"

        result = evaluate_m11_completion_readiness_checklist(record)

        self.assertTrue(result["m11_completion_readiness_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("m11_completion_claim_detected", result["readiness_findings"])

    def test_completion_readiness_requires_release_status_path(self):
        record = copy.deepcopy(self.checklist)
        record["release_status_path"]["present"] = False

        result = evaluate_m11_completion_readiness_checklist(record)

        self.assertTrue(result["m11_completion_readiness_invalid"])
        self.assertTrue(result["release_status_path_missing"])
        self.assertIn("release_status_path_missing", result["readiness_findings"])

    def test_completion_readiness_detects_release_approval_leakage(self):
        record = copy.deepcopy(self.checklist)
        record["release_status_path"]["release_proof_linkage_boundary"] = (
            "Release proof linkage approves release."
        )
        record["authority_boundary_checklist"]["release_proof_boundary"] = ""

        result = evaluate_m11_completion_readiness_checklist(record)

        self.assertTrue(result["m11_completion_readiness_invalid"])
        self.assertIn(
            "release_proof_linkage_implies_release_approval_boundary_missing",
            result["readiness_findings"],
        )

    def test_completion_readiness_detects_forbidden_output(self):
        record = copy.deepcopy(self.checklist)
        record["readiness_outputs"].append("release_approved")

        result = evaluate_m11_completion_readiness_checklist(record)

        self.assertTrue(result["m11_completion_readiness_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "forbidden_readiness_output_detected",
            result["readiness_findings"],
        )

    def test_completion_readiness_detects_authority_transfer_claim(self):
        record = copy.deepcopy(self.checklist)
        record["claimed_output"] = "sealed_by_external_consumer"

        result = evaluate_m11_completion_readiness_checklist(record)

        self.assertTrue(result["m11_completion_readiness_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "authority_transfer_claim_detected",
            result["readiness_findings"],
        )

    def test_completion_readiness_requires_fail_closed_and_sealing_boundaries(self):
        record = copy.deepcopy(self.checklist)
        record["authority_boundary_checklist"][
            "fail_closed_recommendation_boundary"
        ] = ""
        record["authority_boundary_checklist"]["sealing_eligibility_boundary"] = ""

        result = evaluate_m11_completion_readiness_checklist(record)

        self.assertTrue(result["m11_completion_readiness_invalid"])
        self.assertIn(
            "missing_authority_boundary_statement",
            result["readiness_findings"],
        )


if __name__ == "__main__":
    unittest.main()
