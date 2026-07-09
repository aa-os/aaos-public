import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.m13_external_consumer_onboarding_evaluator import (  # noqa: E402
    evaluate_m13_external_consumer_onboarding,
)


FIXTURE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m13-external-consumer-onboarding-fixtures.json"
)
DOC_PATH = ROOT / "docs" / "public-integration-pack" / "m13-external-consumer-onboarding.md"


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_text(path):
    with path.open(encoding="utf-8") as handle:
        return handle.read()


class M13ExternalConsumerOnboardingEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.fixture = load_json(FIXTURE_PATH)
        self.documentation_text = load_text(DOC_PATH)

    def evaluate(self, fixture=None, documentation_text=None):
        return evaluate_m13_external_consumer_onboarding(
            self.fixture if fixture is None else fixture,
            self.documentation_text if documentation_text is None else documentation_text,
        )

    def test_valid_onboarding_documentation_ready_for_review_without_authority_transfer(self):
        result = self.evaluate()

        self.assertTrue(result["onboarding_documentation_valid"])
        self.assertFalse(result["onboarding_documentation_invalid"])
        self.assertTrue(result["onboarding_boundary_preserved"])
        self.assertFalse(result["onboarding_boundary_violation"])
        self.assertTrue(result["onboarding_ready_for_review"])
        self.assertFalse(result["onboarding_not_ready"])
        self.assertTrue(result["release_status_future_only"])
        self.assertEqual(result["onboarding_findings"], [])
        self.assertEqual(result["missing_evidence"], [])

    def test_onboarding_documentation_granting_authority_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["documentation_output"] = (
            "External consumer onboarding documentation grants authority."
        )

        result = self.evaluate(fixture)

        self.assertTrue(result["onboarding_documentation_invalid"])
        self.assertTrue(result["onboarding_boundary_violation"])
        self.assertIn(
            "onboarding_documentation_authority_grant_claim_detected",
            result["onboarding_findings"],
        )

    def test_registry_inclusion_as_approval_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["semantic_boundaries"][
            "registry_inclusion_boundary"
        ] = "Registry inclusion is approval."

        result = self.evaluate(fixture)

        self.assertTrue(result["onboarding_documentation_invalid"])
        self.assertIn(
            "registry_inclusion_approval_claim_detected",
            result["onboarding_findings"],
        )

    def test_evidence_consumption_as_approval_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["semantic_boundaries"][
            "evidence_consumption_boundary"
        ] = "Evidence consumption is approval."

        result = self.evaluate(fixture)

        self.assertTrue(result["onboarding_documentation_invalid"])
        self.assertIn(
            "evidence_consumption_approval_claim_detected",
            result["onboarding_findings"],
        )

    def test_runtime_approval_evidence_as_execution_approval_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["semantic_boundaries"][
            "runtime_approval_evidence_boundary"
        ] = "Runtime approval evidence is execution approval."

        result = self.evaluate(fixture)

        self.assertTrue(result["onboarding_documentation_invalid"])
        self.assertIn(
            "runtime_approval_execution_approval_claim_detected",
            result["onboarding_findings"],
        )

    def test_operational_readiness_as_approval_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["semantic_boundaries"][
            "operational_readiness_boundary"
        ] = "Operational readiness is approval."

        result = self.evaluate(fixture)

        self.assertTrue(result["onboarding_documentation_invalid"])
        self.assertIn(
            "operational_readiness_approval_claim_detected",
            result["onboarding_findings"],
        )

    def test_onboarding_complete_as_approved_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["semantic_boundaries"][
            "onboarding_complete_boundary"
        ] = "onboarding_complete is approved."

        result = self.evaluate(fixture)

        self.assertTrue(result["onboarding_documentation_invalid"])
        self.assertIn(
            "onboarding_complete_approved_claim_detected",
            result["onboarding_findings"],
        )

    def test_evidence_complete_as_sealed_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["semantic_boundaries"][
            "evidence_complete_boundary"
        ] = "evidence_complete is sealed."

        result = self.evaluate(fixture)

        self.assertTrue(result["onboarding_documentation_invalid"])
        self.assertIn(
            "evidence_complete_sealed_claim_detected",
            result["onboarding_findings"],
        )

    def test_replay_ready_as_sealed_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["semantic_boundaries"]["replay_ready_boundary"] = "replay_ready is sealed."

        result = self.evaluate(fixture)

        self.assertTrue(result["onboarding_documentation_invalid"])
        self.assertIn(
            "replay_ready_sealed_claim_detected",
            result["onboarding_findings"],
        )

    def test_release_proof_linkage_as_release_approval_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["semantic_boundaries"][
            "release_proof_boundary"
        ] = "Release proof linkage is release approval."

        result = self.evaluate(fixture)

        self.assertTrue(result["onboarding_documentation_invalid"])
        self.assertIn(
            "release_proof_release_approval_claim_detected",
            result["onboarding_findings"],
        )

    def test_v012_marked_released_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["future_release_tag_path"]["released"] = True

        result = self.evaluate(fixture)

        self.assertTrue(result["onboarding_documentation_invalid"])
        self.assertFalse(result["release_status_future_only"])
        self.assertIn("v0_12_0_release_claim_detected", result["onboarding_findings"])

    def test_m13_marked_complete_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["m13_completion_status"] = "M13 is complete."

        result = self.evaluate(fixture)

        self.assertTrue(result["onboarding_documentation_invalid"])
        self.assertIn("m13_completion_claim_detected", result["onboarding_findings"])

    def test_tracker_176_closed_or_closes_language_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["tracker_issue_closure_state"] = "closed"

        result = self.evaluate(fixture)

        self.assertTrue(result["onboarding_documentation_invalid"])
        self.assertIn("tracker_issue_176_not_marked_open", result["onboarding_findings"])

        fixture = copy.deepcopy(self.fixture)
        fixture["tracker_issue_linkage"] = "Closes #176"

        result = self.evaluate(fixture)

        self.assertTrue(result["onboarding_documentation_invalid"])
        self.assertIn(
            "tracker_issue_176_closure_claim_detected",
            result["onboarding_findings"],
        )

    def test_documentation_output_attempting_to_seal_decision_proof_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["documentation_output"] = "decision_proof_sealed"

        result = self.evaluate(fixture)

        self.assertTrue(result["onboarding_documentation_invalid"])
        self.assertTrue(result["onboarding_boundary_violation"])
        self.assertIn("authority_transfer_claim_detected", result["onboarding_findings"])

    def test_documentation_output_attempting_final_governance_judgment_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["documentation_output"] = "final_governance_judgment"

        result = self.evaluate(fixture)

        self.assertTrue(result["onboarding_documentation_invalid"])
        self.assertTrue(result["onboarding_boundary_violation"])
        self.assertIn("authority_transfer_claim_detected", result["onboarding_findings"])


if __name__ == "__main__":
    unittest.main()
