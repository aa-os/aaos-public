import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.m12_release_readiness_evaluator import (  # noqa: E402
    evaluate_m12_release_readiness,
)


RELEASE_LINKAGE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m12-release-proof-linkage.json"
)
CHECKLIST_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m12-completion-readiness-checklist.json"
)


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class M12ReleaseReadinessEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.release_linkage = load_json(RELEASE_LINKAGE_PATH)
        self.checklist = load_json(CHECKLIST_PATH)

    def evaluate(self, release_linkage=None, checklist=None):
        return evaluate_m12_release_readiness(
            self.release_linkage if release_linkage is None else release_linkage,
            self.checklist if checklist is None else checklist,
        )

    def test_release_proof_linkage_and_readiness_checklist_pass(self):
        result = self.evaluate()

        self.assertTrue(result["m12_release_readiness_valid"])
        self.assertTrue(result["release_proof_linkage_present"])
        self.assertTrue(result["completion_readiness_candidate"])
        self.assertTrue(result["expected_output_coverage_complete"])
        self.assertTrue(result["authority_boundary_preserved"])
        self.assertTrue(result["release_status_future_only"])
        self.assertEqual(result["release_readiness_findings"], [])
        self.assertEqual(result["missing_evidence"], [])

    def test_missing_168_reference_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["related_issue"] = ""

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertIn("missing_release_related_issue_168", result["release_readiness_findings"])

    def test_closes_168_language_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["tracker_issue_linkage"] = "Closes #168"

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "tracker_issue_168_closure_claim_detected",
            result["release_readiness_findings"],
        )

    def test_missing_169_reference_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["consumer_registry_pr"] = ""

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertIn("missing_release_consumer_registry_pr_169", result["release_readiness_findings"])

    def test_missing_170_reference_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["integration_ci_check_specimen_pr"] = ""

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertIn(
            "missing_release_integration_ci_check_specimen_pr_170",
            result["release_readiness_findings"],
        )

    def test_missing_172_reference_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["cross_consumer_traceability_pr"] = ""

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertIn(
            "missing_release_cross_consumer_traceability_pr_172",
            result["release_readiness_findings"],
        )

    def test_missing_173_reference_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["multi_consumer_semantics_pr"] = ""

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertIn(
            "missing_release_multi_consumer_semantics_pr_173",
            result["release_readiness_findings"],
        )

    def test_v011_release_claim_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["future_release_tag_path"]["released"] = True

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertFalse(result["release_status_future_only"])
        self.assertIn("v0_11_0_release_claim_detected", result["release_readiness_findings"])

    def test_m12_complete_claim_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["m12_status_statement"] = "M12 is complete."

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("m12_completion_claim_detected", result["release_readiness_findings"])

    def test_missing_release_proof_linkage_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["release_proof_linkage"]["present"] = False

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertTrue(result["release_proof_linkage_missing"])
        self.assertIn("release_proof_linkage_missing", result["release_readiness_findings"])

    def test_release_proof_linkage_as_release_approval_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["release_proof_linkage"]["boundary_statement"] = (
            "Release proof linkage is release approval."
        )

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "release_proof_release_approval_claim_detected",
            result["release_readiness_findings"],
        )

    def test_missing_completion_readiness_checklist_fails(self):
        result = self.evaluate(checklist={})

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertFalse(result["expected_output_coverage_complete"])
        self.assertIn("completion_readiness_checklist_missing", result["release_readiness_findings"])

    def test_missing_expected_m12_output_item_fails(self):
        checklist = copy.deepcopy(self.checklist)
        checklist["expected_m12_output_checklist"] = [
            item
            for item in checklist["expected_m12_output_checklist"]
            if item["item_id"] != "cross_consumer_traceability_examples"
        ]

        result = self.evaluate(checklist=checklist)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertTrue(result["expected_output_coverage_incomplete"])
        self.assertIn("expected_output_coverage_incomplete", result["release_readiness_findings"])

    def test_readme_release_status_path_not_future_only_fails(self):
        checklist = copy.deepcopy(self.checklist)
        checklist["release_status_path"]["state"] = "release_status_current"

        result = self.evaluate(checklist=checklist)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertFalse(result["release_status_future_only"])
        self.assertIn("release_status_future_only_missing", result["release_readiness_findings"])

    def test_registry_inclusion_as_approval_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["semantic_boundaries"]["registry_inclusion_boundary"] = (
            "Registry inclusion is approval."
        )

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "registry_inclusion_approval_claim_detected",
            result["release_readiness_findings"],
        )

    def test_ci_pass_as_approval_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["semantic_boundaries"]["ci_pass_boundary"] = "CI pass is approval."

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("ci_pass_approval_claim_detected", result["release_readiness_findings"])

    def test_traceability_linkage_as_approval_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["semantic_boundaries"]["traceability_linkage_boundary"] = (
            "Traceability linkage is approval."
        )

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "traceability_linkage_approval_claim_detected",
            result["release_readiness_findings"],
        )

    def test_fail_closed_recommended_as_fail_closed_executed_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["semantic_boundaries"]["fail_closed_boundary"] = (
            "fail_closed_recommended is fail_closed_executed."
        )

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("fail_closed_execution_claim_detected", result["release_readiness_findings"])

    def test_sealing_eligible_as_sealed_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["semantic_boundaries"]["sealing_eligibility_boundary"] = (
            "sealing_eligible is sealed."
        )

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "sealing_eligibility_sealed_claim_detected",
            result["release_readiness_findings"],
        )

    def test_evidence_complete_as_sealed_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["semantic_boundaries"]["evidence_complete_boundary"] = (
            "evidence_complete is sealed."
        )

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("evidence_complete_sealed_claim_detected", result["release_readiness_findings"])

    def test_replay_ready_as_sealed_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["semantic_boundaries"]["replay_ready_boundary"] = (
            "replay_ready is sealed."
        )

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("replay_ready_sealed_claim_detected", result["release_readiness_findings"])

    def test_evaluator_findings_as_sealing_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["semantic_boundaries"]["evaluator_findings_boundary"] = (
            "evaluator findings are sealing."
        )

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "evaluator_findings_sealing_claim_detected",
            result["release_readiness_findings"],
        )

    def test_governance_ci_findings_as_sealing_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["semantic_boundaries"]["governance_ci_findings_boundary"] = (
            "governance CI findings are sealing."
        )

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "governance_ci_findings_sealing_claim_detected",
            result["release_readiness_findings"],
        )

    def test_final_governance_judgment_output_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["release_readiness_output"] = "final_governance_judgment"

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("authority_transfer_claim_detected", result["release_readiness_findings"])

    def test_audit_closed_output_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["release_readiness_output"] = "audit_closed"

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("authority_transfer_claim_detected", result["release_readiness_findings"])

    def test_missing_aaos_authority_statement_fails(self):
        release_linkage = copy.deepcopy(self.release_linkage)
        release_linkage["decision_proof_sealing_boundary_statement"] = ""
        release_linkage["aaos_retained_authority_statement"] = ""
        release_linkage["sovereignty_statement"] = ""

        result = self.evaluate(release_linkage=release_linkage)

        self.assertTrue(result["m12_release_readiness_invalid"])
        self.assertIn(
            "missing_aaos_authority_boundary_statement",
            result["release_readiness_findings"],
        )


if __name__ == "__main__":
    unittest.main()
