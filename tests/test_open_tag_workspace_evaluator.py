import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.open_tag_workspace_evaluator import (  # noqa: E402
    advisor_review_should_be_required,
    detect_forbidden_authority_claims,
    evaluate_open_tag_workspace,
)


ACTIVITY_SCHEMA_PATH = ROOT / "schemas" / "human-agent-activity-evidence.schema.json"
INJECTION_SCHEMA_PATH = (
    ROOT / "schemas" / "workspace-decision-contract-injection.schema.json"
)
ACTIVITY_EXAMPLE_PATH = (
    ROOT / "examples" / "open-tag-workspace" / "activity-replay.json"
)
RESPONSIBILITY_EXAMPLE_PATH = (
    ROOT / "examples" / "open-tag-workspace" / "responsibility-workflow-specimen.json"
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


class OpenTagWorkspaceEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.activity_schema = load_json(ACTIVITY_SCHEMA_PATH)
        self.injection_schema = load_json(INJECTION_SCHEMA_PATH)
        self.activity_example = load_json(ACTIVITY_EXAMPLE_PATH)
        self.responsibility_example = load_json(RESPONSIBILITY_EXAMPLE_PATH)

    def test_examples_match_schemas(self):
        validate_subset(
            self.activity_schema,
            self.activity_example["activity_evidence"][0],
        )
        validate_subset(
            self.injection_schema,
            self.activity_example["decision_contract_injection"],
        )
        validate_subset(
            self.activity_schema,
            self.responsibility_example["activity_evidence"],
        )

    def test_activity_replay_passes_with_advisor_recommendation(self):
        result = evaluate_open_tag_workspace(self.activity_example)

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["violations"], [])
        self.assertIn("advisor_review_required", result["recommendations"])
        self.assertTrue(advisor_review_should_be_required(self.activity_example))

    def test_examples_do_not_claim_forbidden_authority(self):
        self.assertEqual(detect_forbidden_authority_claims(self.activity_example), set())
        self.assertEqual(
            detect_forbidden_authority_claims(self.responsibility_example),
            set(),
        )

    def test_missing_decision_contract_fields_are_detected(self):
        record = copy.deepcopy(self.activity_example)
        record["decision_contract_injection"] = {
            "decision_id": "",
            "intent": "",
            "actor": "",
            "authority_source": "",
            "risk_class": "",
            "allowed_tools": [],
        }

        result = evaluate_open_tag_workspace(record)

        self.assertIn("missing_decision_id", result["violations"])
        self.assertIn("missing_intent", result["violations"])
        self.assertIn("missing_actor", result["violations"])
        self.assertIn("missing_authority_source", result["violations"])
        self.assertIn("missing_risk_class", result["violations"])
        self.assertIn("missing_allowed_tools", result["violations"])
        self.assertIn("missing_rollback_plan", result["violations"])
        self.assertIn("missing_execution_trace", result["violations"])
        self.assertIn("missing_replay_target", result["violations"])

    def test_missing_approval_rollback_trace_and_replay_are_detected(self):
        record = copy.deepcopy(self.activity_example)
        activity = record["activity_evidence"][0]
        activity["approval_state"] = "missing"
        activity["rollback_plan_ref"] = ""
        activity["execution_trace_ref"] = ""
        activity["replay_target_ref"] = ""
        record["decision_contract_injection"]["rollback_plan"] = {
            "required": True,
            "plan_ref": "",
            "owner": "AAOS",
        }
        record["decision_contract_injection"]["execution_trace"] = {
            "required": True,
            "trace_ref": "",
        }
        record["decision_contract_injection"]["replay_target"] = {
            "required": True,
            "target_ref": "",
        }

        result = evaluate_open_tag_workspace(record)

        self.assertIn("approval_required_but_missing_approval_state", result["violations"])
        self.assertIn("rollback_required_but_missing_rollback_plan", result["violations"])
        self.assertIn("missing_execution_trace", result["violations"])
        self.assertIn("missing_replay_target", result["violations"])

    def test_actor_agent_daemon_and_runtime_task_binding_are_detected(self):
        record = copy.deepcopy(self.activity_example)
        activity = record["activity_evidence"][0]
        activity["agent_id"] = activity["actor"]
        activity["task_id"] = ""

        result = evaluate_open_tag_workspace(record)

        self.assertIn("missing_actor_agent_daemon_separation", result["violations"])
        self.assertIn("runtime_adapter_event_without_task_binding", result["violations"])

    def test_task_execution_without_decision_contract_is_detected(self):
        record = copy.deepcopy(self.activity_example)
        record.pop("decision_contract_injection")
        record["activity_evidence"][0]["event_type"] = "task_execution_started"

        result = evaluate_open_tag_workspace(record)

        self.assertIn("task_execution_without_decision_contract", result["violations"])
        self.assertIn("missing_decision_id", result["violations"])

    def test_high_risk_and_governance_sensitive_events_require_advisor(self):
        record = copy.deepcopy(self.responsibility_example)
        record["activity_evidence"].pop("advisor_invocation")

        result = evaluate_open_tag_workspace(record)

        self.assertIn("high_risk_task_without_advisor_invocation", result["violations"])
        self.assertIn(
            "governance_sensitive_workspace_event_without_advisor_invocation",
            result["violations"],
        )

    def test_forbidden_authority_and_decision_proof_sealing_claims_are_detected(self):
        record = copy.deepcopy(self.activity_example)
        record["open_tag_outputs"] = [
            "policy_authority_changed",
            "decision_route_changed",
            "rollback_decision",
            "decision_proof_sealed",
        ]

        result = evaluate_open_tag_workspace(record)

        self.assertIn("forbidden_open_tag_authority_claim", result["violations"])
        self.assertIn("open_tag_claims_policy_authority", result["violations"])
        self.assertIn("open_tag_claims_decision_router_authority", result["violations"])
        self.assertIn("open_tag_claims_rollback_authority", result["violations"])
        self.assertIn(
            "open_tag_claims_decision_proof_sealing_authority",
            result["violations"],
        )
        self.assertIn("decision_proof_sealing_claimed_by_open_tag", result["violations"])


if __name__ == "__main__":
    unittest.main()
