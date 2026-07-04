import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.decision_proof_sealing_evaluator import (  # noqa: E402
    detect_forbidden_sealing_claims,
    evaluate_adapter_release_traceability,
    evaluate_external_integration_readiness,
    evaluate_sealing_status,
)


SEALING_SCHEMA_PATH = ROOT / "schemas" / "decision-proof-sealing-status.schema.json"
INTEGRATION_SCHEMA_PATH = ROOT / "schemas" / "external-integration-readiness.schema.json"
SEALING_EXAMPLE_PATH = (
    ROOT / "examples" / "decision-proof-sealing-boundary" / "v0.8.0-sealing-boundary.json"
)
INTEGRATION_EXAMPLE_PATH = (
    ROOT / "examples" / "external-integration-readiness" / "evidence-consumer-readiness.json"
)
TRACEABILITY_EXAMPLE_PATH = (
    ROOT / "examples" / "adapter-to-release-proof-traceability" / "v0.8.0-traceability.json"
)


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_subset(schema, instance, path="$"):
    schema_type = schema.get("type")

    if schema_type == "object":
        assert isinstance(instance, dict), f"{path} must be object"
        for required in schema.get("required", []):
            assert required in instance, f"{path}.{required} is required"
        allowed_properties = set(schema.get("properties", {}))
        if schema.get("additionalProperties") is False:
            extra = set(instance) - allowed_properties
            assert not extra, f"{path} has unexpected keys: {sorted(extra)}"
        for key, property_schema in schema.get("properties", {}).items():
            if key in instance:
                validate_subset(property_schema, instance[key], f"{path}.{key}")

    elif schema_type == "array":
        assert isinstance(instance, list), f"{path} must be array"
        if "minItems" in schema:
            assert len(instance) >= schema["minItems"], f"{path} must have enough items"
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(instance):
                validate_subset(item_schema, item, f"{path}[{index}]")

    elif schema_type == "string":
        assert isinstance(instance, str), f"{path} must be string"
        if "const" in schema:
            assert instance == schema["const"], f"{path} must equal {schema['const']}"
        if "enum" in schema:
            assert instance in schema["enum"], f"{path} must be one of {schema['enum']}"

    elif schema_type == "boolean":
        assert isinstance(instance, bool), f"{path} must be boolean"


class DecisionProofSealingEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.sealing_schema = load_json(SEALING_SCHEMA_PATH)
        self.integration_schema = load_json(INTEGRATION_SCHEMA_PATH)
        self.sealing_example = load_json(SEALING_EXAMPLE_PATH)
        self.integration_example = load_json(INTEGRATION_EXAMPLE_PATH)
        self.traceability_example = load_json(TRACEABILITY_EXAMPLE_PATH)

    def test_examples_match_schemas(self):
        validate_subset(self.sealing_schema, self.sealing_example)
        validate_subset(self.integration_schema, self.integration_example)

    def test_examples_pass_evaluator(self):
        sealing_result = evaluate_sealing_status(self.sealing_example)
        integration_result = evaluate_external_integration_readiness(self.integration_example)
        traceability_result = evaluate_adapter_release_traceability(self.traceability_example)

        self.assertTrue(sealing_result["sealing_boundary_valid"])
        self.assertTrue(integration_result["integration_readiness_passed"])
        self.assertTrue(traceability_result["traceability_complete"])
        self.assertEqual(sealing_result["sealing_findings"], [])
        self.assertEqual(integration_result["sealing_findings"], [])
        self.assertEqual(traceability_result["sealing_findings"], [])

    def test_sealing_status_detects_missing_required_fields(self):
        record = copy.deepcopy(self.sealing_example)
        for field in [
            "sealing_boundary_statement",
            "sealing_status",
            "evidence_readiness_state",
            "sealing_eligibility_state",
            "final_sealing_authority_owner",
            "aaos_retained_authority_statement",
        ]:
            record.pop(field)

        result = evaluate_sealing_status(record)

        self.assertTrue(result["sealing_boundary_invalid"])
        self.assertIn("missing_sealing_boundary_statement", result["sealing_findings"])
        self.assertIn("missing_sealing_status", result["sealing_findings"])
        self.assertIn("missing_evidence_readiness_state", result["sealing_findings"])
        self.assertIn("missing_sealing_eligibility_state", result["sealing_findings"])
        self.assertIn("missing_final_sealing_authority_owner", result["sealing_findings"])
        self.assertIn("missing_aaos_retained_authority_statement", result["sealing_findings"])

    def test_forbidden_sealing_state_is_detected(self):
        record = copy.deepcopy(self.sealing_example)
        record["sealing_status"] = "sealed_by_adapter"

        result = evaluate_sealing_status(record)

        self.assertTrue(result["forbidden_sealing_state"])
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("decision_proof_sealed_outside_aaos", result["sealing_findings"])
        self.assertTrue(result["fail_closed_recommended"])

    def test_forbidden_outputs_are_detected(self):
        record = copy.deepcopy(self.sealing_example)
        record["unsafe_outputs"] = {
            "decision_proof_sealed": True,
            "audit_closed": True,
            "final_governance_judgment": True,
        }

        claims = detect_forbidden_sealing_claims(record)
        result = evaluate_sealing_status(record)

        self.assertIn("decision_proof_sealed", claims)
        self.assertIn("audit_closed", claims)
        self.assertIn("final_governance_judgment", claims)
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("decision_proof_sealed_outside_aaos", result["sealing_findings"])
        self.assertIn("audit_closed_outside_aaos", result["sealing_findings"])
        self.assertIn(
            "final_governance_judgment_made_outside_aaos",
            result["sealing_findings"],
        )

    def test_external_integration_readiness_detects_missing_boundaries(self):
        record = copy.deepcopy(self.integration_example)
        record["identity_boundary"]["defined"] = False
        record["authority_boundary"]["defined"] = False
        record["evidence_schema_compatibility"] = False
        record["replay_compatibility"] = False
        record["rollback_traceability"] = False
        record["escalation_semantics"] = False
        record["fail_closed_behavior"] = False
        record["decision_proof_sealing_boundary_preservation"] = False
        record["release_proof_linkage"] = False

        result = evaluate_external_integration_readiness(record)

        self.assertTrue(result["integration_readiness_failed"])
        self.assertIn("missing_external_integration_identity_boundary", result["sealing_findings"])
        self.assertIn("missing_external_integration_authority_boundary", result["sealing_findings"])
        self.assertIn("missing_evidence_schema_compatibility", result["sealing_findings"])
        self.assertIn("missing_replay_compatibility", result["sealing_findings"])
        self.assertIn("missing_rollback_traceability", result["sealing_findings"])
        self.assertIn("missing_escalation_semantics", result["sealing_findings"])
        self.assertIn("missing_fail_closed_behavior", result["sealing_findings"])
        self.assertIn(
            "missing_decision_proof_sealing_boundary_preservation",
            result["sealing_findings"],
        )
        self.assertIn("missing_release_proof_linkage", result["sealing_findings"])

    def test_traceability_detects_missing_release_proof_linkage(self):
        record = copy.deepcopy(self.traceability_example)
        record["adapter_to_release_proof_traceability"] = False
        record["release_proof_linkage"] = False
        record.pop("runtime_replay_packet")

        result = evaluate_adapter_release_traceability(record)

        self.assertTrue(result["traceability_incomplete"])
        self.assertIn("missing_adapter_to_release_proof_traceability", result["sealing_findings"])
        self.assertIn("missing_release_proof_linkage", result["sealing_findings"])
        self.assertIn("runtime_replay_packet", result["missing_evidence"])

    def test_safe_forbidden_lists_do_not_trigger_claims(self):
        claims = detect_forbidden_sealing_claims(self.integration_example)

        self.assertEqual(claims, set())


if __name__ == "__main__":
    unittest.main()
