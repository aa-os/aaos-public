import copy
import json
import unittest
from pathlib import Path

from runtime.public_integration_pack_evaluator import (
    detect_forbidden_authority_claims,
    evaluate_artifact_consumption_semantics,
    evaluate_external_evidence_consumer,
    evaluate_public_integration_pack,
)


ROOT = Path(__file__).resolve().parents[1]
PACK_EXAMPLE_PATH = (
    ROOT / "examples" / "public-integration-pack-pilot" / "pilot-package.json"
)
CONSUMER_EXAMPLE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "external-evidence-consumer-specimen.json"
)


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class PublicIntegrationPackEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.pack = load_json(PACK_EXAMPLE_PATH)
        self.consumer = load_json(CONSUMER_EXAMPLE_PATH)

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

    def test_forbidden_authority_claims_are_detected(self):
        record = copy.deepcopy(self.pack)
        record["claimed_output"] = "decision_proof_sealed"

        result = evaluate_public_integration_pack(record)

        self.assertTrue(result["authority_boundary_violation"])
        self.assertTrue(result["escalation_required"])
        self.assertTrue(result["fail_closed_recommended"])

    def test_forbidden_output_lists_are_safe_negative_context(self):
        claims = detect_forbidden_authority_claims(self.pack)

        self.assertEqual(claims, set())


if __name__ == "__main__":
    unittest.main()
