import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.skillopt_governance_evaluator import (  # noqa: E402
    advisor_review_triggers,
    detect_forbidden_authority_claims,
    evaluate_skillopt_governance,
)


ARTIFACT_SCHEMA_PATH = ROOT / "schemas" / "governed-skill-artifact.schema.json"
AUDIT_SCHEMA_PATH = ROOT / "schemas" / "skill-change-audit.schema.json"
EXAMPLE_PATH = (
    ROOT
    / "examples"
    / "skillopt-governance"
    / "governed-skill-artifact.json"
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

    elif schema_type == "number":
        assert isinstance(instance, (int, float)), f"{path} must be number"


class SkillOptGovernanceTests(unittest.TestCase):
    def setUp(self):
        self.artifact_schema = load_json(ARTIFACT_SCHEMA_PATH)
        self.audit_schema = load_json(AUDIT_SCHEMA_PATH)
        self.example = load_json(EXAMPLE_PATH)

    def test_example_matches_artifact_schema_subset(self):
        validate_subset(self.artifact_schema, self.example)

    def test_audit_schema_declares_required_evidence_fields(self):
        required = set(self.audit_schema["required"])

        self.assertIn("validation_evidence", required)
        self.assertIn("rollout_trace", required)
        self.assertIn("history_log", required)
        self.assertIn("replay_dataset", required)
        self.assertIn("deployment_gate_status", required)
        self.assertIn("rollback_readiness", required)

    def test_example_passes_boundary_checks_with_advisor_recommendation(self):
        result = evaluate_skillopt_governance(self.example)

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["violations"], [])
        self.assertIn("advisor_review_required", result["recommendations"])
        self.assertEqual(
            advisor_review_triggers(self.example),
            {"safety_behavior_change"},
        )

    def test_example_does_not_claim_forbidden_authority(self):
        self.assertEqual(detect_forbidden_authority_claims(self.example), set())

    def test_forbidden_skillopt_authority_claims_are_detected(self):
        record = copy.deepcopy(self.example)
        record["skillopt_outputs"] = [
            "deployment_approved",
            "risk_accepted",
            "identity_trust_changed",
            "governance_policy_rewritten",
            "audit_closed",
            "final_governance_judgment",
        ]

        result = evaluate_skillopt_governance(record)

        self.assertIn("forbidden_skillopt_authority_claim", result["violations"])
        self.assertIn("deployment_approved_by_skillopt", result["violations"])
        self.assertIn("risk_accepted_by_skillopt", result["violations"])
        self.assertIn("identity_trust_changed_by_skillopt", result["violations"])
        self.assertIn("governance_policy_rewritten_by_skillopt", result["violations"])
        self.assertIn("audit_closed_by_skillopt", result["violations"])
        self.assertIn(
            "final_governance_judgment_claimed_by_skillopt",
            result["violations"],
        )

    def test_missing_required_governance_evidence_is_detected(self):
        record = copy.deepcopy(self.example)
        record["rollback_plan"] = {"ready": False}
        record["replay_trace_refs"] = []
        record["validation_results"] = []
        record["evidence_hashes"] = []
        record["rejected_edits"] = []
        record["deployment_gate"] = {}

        result = evaluate_skillopt_governance(record)

        self.assertIn("missing_rollback_plan", result["violations"])
        self.assertIn("missing_replay_traces", result["violations"])
        self.assertIn("missing_validation_evidence", result["violations"])
        self.assertIn("missing_rejected_edit_history", result["violations"])
        self.assertIn("missing_deployment_gate", result["violations"])

    def test_missing_advisor_invocation_for_governance_sensitive_change_is_detected(self):
        record = copy.deepcopy(self.example)
        record["advisor_invocation"] = {"required": False}
        record["tool_use_impact"] = {
            "impact_level": "expanded",
            "expanded": True,
            "notes": "Expanded tool use for test coverage.",
        }
        record["data_access_impact"] = {
            "impact_level": "expanded",
            "expanded": True,
            "notes": "Expanded data access for test coverage.",
        }
        record["authority_impact"] = {
            "impact_level": "ambiguous",
            "boundary_changed": True,
            "notes": "Ambiguous authority boundary for test coverage.",
        }
        record["autonomy_impact"] = {
            "impact_level": "high",
            "increased": True,
            "notes": "Increased autonomy for test coverage.",
        }

        result = evaluate_skillopt_governance(record)

        self.assertIn("missing_advisor_invocation", result["violations"])
        self.assertIn("advisor_review_required", result["recommendations"])


if __name__ == "__main__":
    unittest.main()
