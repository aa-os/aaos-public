import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.public_integration_pack_evaluator import (  # noqa: E402
    detect_forbidden_authority_claims,
    evaluate_artifact_consumption_semantics,
    evaluate_external_evidence_consumer,
    evaluate_m11_pilot_traceability,
    evaluate_public_integration_pack,
    evaluate_registry_facing_traceability,
)


PACK_EXAMPLE_PATH = (
    ROOT / "examples" / "public-integration-pack-pilot" / "pilot-package.json"
)
CONSUMER_EXAMPLE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "external-evidence-consumer-specimen.json"
)
TRACEABILITY_EXAMPLE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m11-pilot-release-proof-linkage.json"
)
REGISTRY_TRACEABILITY_EXAMPLE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m11-registry-facing-traceability.json"
)


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class PublicIntegrationPackEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.pack = load_json(PACK_EXAMPLE_PATH)
        self.consumer = load_json(CONSUMER_EXAMPLE_PATH)
        self.traceability = load_json(TRACEABILITY_EXAMPLE_PATH)
        self.registry_traceability = load_json(REGISTRY_TRACEABILITY_EXAMPLE_PATH)

    def test_examples_pass_evaluator(self):
        pack_result = evaluate_public_integration_pack(self.pack)
        consumer_result = evaluate_external_evidence_consumer(self.consumer)
        semantics_result = evaluate_artifact_consumption_semantics(self.consumer)

        self.assertTrue(pack_result["public_integration_pack_valid"])
        self.assertTrue(consumer_result["external_consumer_valid"])
        self.assertTrue(semantics_result["artifact_consumption_semantics_present"])
        self.assertTrue(pack_result["release_proof_linkage_present"])
        self.assertTrue(consumer_result["release_proof_linkage_present"])
        self.assertTrue(pack_result["authority_boundary_preserved"])
        self.assertEqual(pack_result["integration_findings"], [])
        self.assertEqual(consumer_result["integration_findings"], [])

    def test_m11_traceability_examples_pass_evaluator(self):
        traceability_result = evaluate_m11_pilot_traceability(self.traceability)
        registry_result = evaluate_registry_facing_traceability(
            self.registry_traceability
        )

        self.assertTrue(traceability_result["m11_pilot_traceability_valid"])
        self.assertTrue(traceability_result["release_proof_linkage_present"])
        self.assertTrue(traceability_result["registry_traceability_present"])
        self.assertTrue(traceability_result["authority_boundary_preserved"])
        self.assertEqual(traceability_result["traceability_findings"], [])
        self.assertTrue(registry_result["m11_pilot_traceability_valid"])
        self.assertTrue(registry_result["release_proof_linkage_present"])
        self.assertTrue(registry_result["registry_traceability_present"])
        self.assertTrue(registry_result["authority_boundary_preserved"])
        self.assertEqual(registry_result["traceability_findings"], [])

    def test_public_pack_detects_missing_required_references(self):
        record = copy.deepcopy(self.pack)
        record["integration_boundary_contract"] = {}
        record["evidence_schema_reference"] = []
        record["release_proof_linkage"]["present"] = False
        record["adapter_registry_entry_reference"] = {}
        record["evaluator_check_reference"] = ""

        result = evaluate_public_integration_pack(record)

        self.assertTrue(result["public_integration_pack_invalid"])
        self.assertIn("missing_integration_boundary_contract", result["integration_findings"])
        self.assertIn("missing_evidence_schema_reference", result["integration_findings"])
        self.assertIn("release_proof_linkage_missing", result["integration_findings"])
        self.assertIn("missing_adapter_registry_entry_reference", result["integration_findings"])
        self.assertIn("missing_evaluator_check_reference", result["integration_findings"])

    def test_external_consumer_detects_missing_consumption_semantics(self):
        record = copy.deepcopy(self.consumer)
        del record["artifact_consumption_semantics"]["unsealed_evidence"]

        result = evaluate_external_evidence_consumer(record)

        self.assertTrue(result["external_consumer_invalid"])
        self.assertTrue(result["artifact_consumption_semantics_missing"])
        self.assertIn(
            "missing_consumption_semantics_for_unsealed_evidence",
            result["integration_findings"],
        )

    def test_external_consumer_detects_missing_final_aaos_authority(self):
        record = copy.deepcopy(self.consumer)
        record["final_aaos_owned_sealing_authority"]["owner"] = "external_consumer"
        record["final_aaos_owned_sealing_authority"]["delegated"] = True

        result = evaluate_external_evidence_consumer(record)

        self.assertTrue(result["external_consumer_invalid"])
        self.assertIn(
            "missing_final_aaos_owned_sealing_authority",
            result["integration_findings"],
        )

    def test_m11_traceability_detects_missing_release_links(self):
        record = copy.deepcopy(self.traceability)
        record["first_m11_pilot_pr"] = ""
        record["m11_readme_wip_sync_pr"] = ""
        record["release_proof_linkage"]["present"] = False
        record["registry_facing_traceability"] = ""

        result = evaluate_m11_pilot_traceability(record)

        self.assertTrue(result["m11_pilot_traceability_invalid"])
        self.assertTrue(result["release_proof_linkage_missing"])
        self.assertTrue(result["registry_traceability_missing"])
        self.assertIn("missing_first_m11_pilot_pr_121", result["traceability_findings"])
        self.assertIn(
            "missing_m11_readme_wip_sync_pr_131",
            result["traceability_findings"],
        )

    def test_m11_traceability_detects_tracker_closure_language(self):
        record = copy.deepcopy(self.traceability)
        record["tracker_issue_linkage"] = "Closes #120"

        result = evaluate_m11_pilot_traceability(record)

        self.assertTrue(result["m11_pilot_traceability_invalid"])
        self.assertIn(
            "tracker_issue_120_closure_claim_detected",
            result["traceability_findings"],
        )

    def test_m11_traceability_detects_v010_release_claim(self):
        record = copy.deepcopy(self.traceability)
        record["v0_10_0_future_completion_release_reservation"] = "v0.10.0 is released."

        result = evaluate_m11_pilot_traceability(record)

        self.assertTrue(result["m11_pilot_traceability_invalid"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "v0_10_0_release_claim_detected",
            result["traceability_findings"],
        )

    def test_registry_traceability_detects_authority_claims(self):
        record = copy.deepcopy(self.registry_traceability)
        record["claimed_registry_output"] = "sealed_by_registry"

        result = evaluate_registry_facing_traceability(record)

        self.assertTrue(result["authority_boundary_violation"])
        self.assertTrue(result["escalation_required"])
        self.assertTrue(result["fail_closed_recommended"])

    def test_forbidden_authority_claims_are_detected(self):
        record = copy.deepcopy(self.pack)
        record["claimed_output"] = "decision_proof_sealed"

        result = evaluate_public_integration_pack(record)

        self.assertTrue(result["authority_boundary_violation"])
        self.assertTrue(result["escalation_required"])
        self.assertTrue(result["fail_closed_recommended"])

    def test_forbidden_output_lists_are_safe_negative_context(self):
        claims = detect_forbidden_authority_claims(self.traceability)

        self.assertEqual(claims, set())


if __name__ == "__main__":
    unittest.main()
