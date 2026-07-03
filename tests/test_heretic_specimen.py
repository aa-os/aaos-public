import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.heretic_specimen_evaluator import (  # noqa: E402
    detect_forbidden_authority_claims,
    evaluate_heretic_specimen,
)


SCHEMA_PATH = ROOT / "schemas" / "high-risk-model-specimen.schema.json"
EXAMPLE_PATH = (
    ROOT
    / "examples"
    / "heretic-adversarial-specimen"
    / "high-risk-decensored-model.json"
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


class HereticSpecimenTests(unittest.TestCase):
    def setUp(self):
        self.schema = load_json(SCHEMA_PATH)
        self.example = load_json(EXAMPLE_PATH)

    def test_example_matches_schema_subset(self):
        validate_subset(self.schema, self.example)

    def test_example_passes_boundary_checks_with_review_recommendation(self):
        result = evaluate_heretic_specimen(self.example)

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["violations"], [])
        self.assertIn("advisor_review_required", result["recommendations"])
        self.assertIn("block_production_tools", result["recommendations"])

    def test_example_does_not_claim_forbidden_authority(self):
        self.assertEqual(detect_forbidden_authority_claims(self.example), set())

    def test_missing_required_risk_tags_are_detected(self):
        record = copy.deepcopy(self.example)
        record["risk_tags"] = ["adversarial_specimen", "no_production_tools"]

        result = evaluate_heretic_specimen(record)

        self.assertIn("missing_high_risk_tag", result["violations"])
        self.assertIn("missing_decensored_tag", result["violations"])

    def test_production_and_access_boundary_violations_are_detected(self):
        record = copy.deepcopy(self.example)
        record["allowed_environment"] = {
            "environment_type": "production_runtime",
            "network_access": True,
            "write_access": True,
            "credential_access": True,
            "production_tool_access": True,
        }

        result = evaluate_heretic_specimen(record)

        self.assertIn("production_environment_claim", result["violations"])
        self.assertIn("network_access_allowed", result["violations"])
        self.assertIn("write_access_allowed", result["violations"])
        self.assertIn("credential_access_allowed", result["violations"])
        self.assertIn("production_tool_access_allowed", result["violations"])
        self.assertIn("containment_required", result["recommendations"])

    def test_decision_and_policy_authority_claims_are_detected(self):
        record = copy.deepcopy(self.example)
        record["authority_claims"] = {
            "decision_router_authority": True,
            "policy_layer_modification": True,
        }

        result = evaluate_heretic_specimen(record)

        self.assertIn("decision_router_authority_claimed", result["violations"])
        self.assertIn("policy_modification_capability_claimed", result["violations"])

    def test_missing_trace_replay_fail_closed_rollback_and_advisor_are_detected(self):
        record = copy.deepcopy(self.example)
        record["trace_logging_required"] = False
        record["replay_required"] = False
        record["fail_closed_required"] = False
        record["containment_controls"]["full_trace_logging"] = False
        record["containment_controls"]["replay_ready_evidence"] = False
        record["containment_controls"]["fail_closed_enforced"] = False
        record["rollback_rule"] = {"required": False}
        record["advisor_invocation"] = {"required": False}

        result = evaluate_heretic_specimen(record)

        self.assertIn("missing_trace_logging", result["violations"])
        self.assertIn("missing_replay_requirement", result["violations"])
        self.assertIn("missing_fail_closed_requirement", result["violations"])
        self.assertIn("missing_rollback_rule", result["violations"])
        self.assertIn("missing_advisor_invocation", result["violations"])
        self.assertIn("fail_closed_required", result["recommendations"])


if __name__ == "__main__":
    unittest.main()
