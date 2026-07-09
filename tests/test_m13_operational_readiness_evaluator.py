import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.m13_operational_readiness_evaluator import (  # noqa: E402
    evaluate_m13_operational_readiness_checklist,
)


CHECKLIST_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m13-operational-readiness-checklist.json"
)


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def domain_by_id(checklist, domain_id):
    for domain in checklist["readiness_domains"]:
        if domain["domain_id"] == domain_id:
            return domain
    raise AssertionError(f"missing domain {domain_id}")


class M13OperationalReadinessEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.checklist = load_json(CHECKLIST_PATH)

    def evaluate(self, checklist=None):
        return evaluate_m13_operational_readiness_checklist(
            self.checklist if checklist is None else checklist
        )

    def test_valid_checklist_ready_for_review_without_authority_transfer(self):
        result = self.evaluate()

        self.assertTrue(result["operational_readiness_checklist_valid"])
        self.assertFalse(result["operational_readiness_checklist_invalid"])
        self.assertTrue(result["readiness_domain_coverage_complete"])
        self.assertFalse(result["readiness_domain_coverage_incomplete"])
        self.assertTrue(result["ready_for_review"])
        self.assertFalse(result["not_ready"])
        self.assertTrue(result["release_status_future_only"])
        self.assertEqual(result["operational_readiness_findings"], [])
        self.assertEqual(result["missing_evidence"], [])

    def test_missing_registry_drift_evidence_fails(self):
        checklist = copy.deepcopy(self.checklist)
        domain = domain_by_id(checklist, "registry_drift_detection_from_178_present")
        domain["represented"] = False
        domain["evidence_refs"] = []

        result = self.evaluate(checklist)

        self.assertTrue(result["operational_readiness_checklist_invalid"])
        self.assertTrue(result["not_ready"])
        self.assertIn(
            "registry_drift_detection_evidence_missing",
            result["operational_readiness_findings"],
        )

    def test_missing_runtime_approval_evidence_fails(self):
        checklist = copy.deepcopy(self.checklist)
        domain = domain_by_id(
            checklist, "runtime_enforced_approval_evidence_from_177_present"
        )
        domain["represented"] = False
        domain["evidence_refs"] = []

        result = self.evaluate(checklist)

        self.assertTrue(result["operational_readiness_checklist_invalid"])
        self.assertTrue(result["not_ready"])
        self.assertIn(
            "runtime_approval_evidence_missing",
            result["operational_readiness_findings"],
        )

    def test_onboarding_documentation_granting_authority_fails(self):
        checklist = copy.deepcopy(self.checklist)
        domain = domain_by_id(
            checklist, "onboarding_documentation_required_not_authority_granting"
        )
        domain["authority_granting"] = True

        result = self.evaluate(checklist)

        self.assertTrue(result["operational_readiness_checklist_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn(
            "onboarding_documentation_authority_grant_claim_detected",
            result["operational_readiness_findings"],
        )

    def test_release_proof_linkage_as_release_approval_fails(self):
        checklist = copy.deepcopy(self.checklist)
        checklist["semantic_boundaries"][
            "release_proof_boundary"
        ] = "Release proof linkage is release approval."

        result = self.evaluate(checklist)

        self.assertTrue(result["operational_readiness_checklist_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn(
            "release_proof_release_approval_claim_detected",
            result["operational_readiness_findings"],
        )

    def test_v012_marked_released_fails(self):
        checklist = copy.deepcopy(self.checklist)
        checklist["future_release_tag_path"]["released"] = True

        result = self.evaluate(checklist)

        self.assertTrue(result["operational_readiness_checklist_invalid"])
        self.assertFalse(result["release_status_future_only"])
        self.assertIn(
            "v0_12_0_release_claim_detected",
            result["operational_readiness_findings"],
        )

    def test_m13_marked_complete_fails(self):
        checklist = copy.deepcopy(self.checklist)
        checklist["m13_completion_status"] = "M13 is complete."

        result = self.evaluate(checklist)

        self.assertTrue(result["operational_readiness_checklist_invalid"])
        self.assertIn(
            "m13_completion_claim_detected",
            result["operational_readiness_findings"],
        )

    def test_tracker_176_closed_or_closes_language_fails(self):
        checklist = copy.deepcopy(self.checklist)
        checklist["tracker_issue_closure_state"] = "closed"

        result = self.evaluate(checklist)

        self.assertTrue(result["operational_readiness_checklist_invalid"])
        self.assertIn(
            "tracker_issue_176_not_marked_open",
            result["operational_readiness_findings"],
        )

        checklist = copy.deepcopy(self.checklist)
        checklist["tracker_issue_linkage"] = "Closes #176"

        result = self.evaluate(checklist)

        self.assertTrue(result["operational_readiness_checklist_invalid"])
        self.assertIn(
            "tracker_issue_176_closure_claim_detected",
            result["operational_readiness_findings"],
        )

    def test_evaluator_output_attempting_to_seal_decision_proof_fails(self):
        checklist = copy.deepcopy(self.checklist)
        checklist["evaluator_output"] = "decision_proof_sealed"

        result = self.evaluate(checklist)

        self.assertTrue(result["operational_readiness_checklist_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn(
            "authority_transfer_claim_detected",
            result["operational_readiness_findings"],
        )

    def test_evaluator_output_attempting_final_governance_judgment_fails(self):
        checklist = copy.deepcopy(self.checklist)
        checklist["evaluator_output"] = "final_governance_judgment"

        result = self.evaluate(checklist)

        self.assertTrue(result["operational_readiness_checklist_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn(
            "authority_transfer_claim_detected",
            result["operational_readiness_findings"],
        )


if __name__ == "__main__":
    unittest.main()
