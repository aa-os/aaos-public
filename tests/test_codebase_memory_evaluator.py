import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.codebase_memory_evaluator import (  # noqa: E402
    advisor_review_should_be_required,
    detect_forbidden_authority_claims,
    evaluate_codebase_memory,
)


GRAPH_SCHEMA_PATH = ROOT / "schemas" / "codebase-graph-evidence.schema.json"
PATCH_SCHEMA_PATH = ROOT / "schemas" / "patch-impact-evidence.schema.json"
EXAMPLE_PATH = (
    ROOT
    / "examples"
    / "codebase-decision-proof"
    / "api-handler-change.json"
)


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def resolve_ref(schema, ref):
    if not ref.startswith("#/$defs/"):
        raise AssertionError(f"Unsupported schema ref: {ref}")
    return schema["$defs"][ref.removeprefix("#/$defs/")]


def validate_subset(schema, instance, path="$", root_schema=None):
    root_schema = root_schema or schema
    if "$ref" in schema:
        schema = resolve_ref(root_schema, schema["$ref"])

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
                validate_subset(property_schema, instance[key], f"{path}.{key}", root_schema)

    elif schema_type == "array":
        assert isinstance(instance, list), f"{path} must be array"
        if "minItems" in schema:
            assert len(instance) >= schema["minItems"], f"{path} must have enough items"
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(instance):
                validate_subset(item_schema, item, f"{path}[{index}]", root_schema)

    elif schema_type == "string":
        assert isinstance(instance, str), f"{path} must be string"
        if "const" in schema:
            assert instance == schema["const"], f"{path} must equal {schema['const']}"
        if "enum" in schema:
            assert instance in schema["enum"], f"{path} must be one of {schema['enum']}"

    elif schema_type == "boolean":
        assert isinstance(instance, bool), f"{path} must be boolean"

    elif schema_type == "integer":
        assert isinstance(instance, int), f"{path} must be integer"

    elif schema_type == "number":
        assert isinstance(instance, (int, float)), f"{path} must be number"


class CodebaseMemoryEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.graph_schema = load_json(GRAPH_SCHEMA_PATH)
        self.patch_schema = load_json(PATCH_SCHEMA_PATH)
        self.example = load_json(EXAMPLE_PATH)

    def test_example_matches_graph_and_patch_schemas(self):
        validate_subset(
            self.graph_schema,
            self.example["codebase_graph_evidence"],
            root_schema=self.graph_schema,
        )
        validate_subset(
            self.patch_schema,
            self.example["patch_impact_evidence"],
            root_schema=self.patch_schema,
        )

    def test_example_passes_with_advisor_recommendation(self):
        result = evaluate_codebase_memory(self.example)

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["violations"], [])
        self.assertIn("advisor_review_required", result["recommendations"])
        self.assertTrue(advisor_review_should_be_required(self.example))

    def test_example_does_not_claim_forbidden_authority(self):
        self.assertEqual(detect_forbidden_authority_claims(self.example), set())

    def test_missing_graph_and_graph_refs_are_detected(self):
        record = copy.deepcopy(self.example)
        record["codebase_graph_evidence"] = {
            "repository_id": "",
            "commit_sha": "",
            "graph_hash": "",
            "replay_trace_ref": "",
            "evidence_freshness": {"status": "fresh", "evidence_age_days": 1, "max_age_days": 14},
        }

        result = evaluate_codebase_memory(record)

        self.assertIn("missing_graph_evidence", result["violations"])
        self.assertIn("missing_dependency_graph", result["violations"])
        self.assertIn("missing_call_graph", result["violations"])
        self.assertIn("missing_route_map", result["violations"])

    def test_stale_evidence_is_detected(self):
        record = copy.deepcopy(self.example)
        record["codebase_graph_evidence"]["evidence_freshness"] = {
            "status": "fresh",
            "evidence_age_days": 30,
            "max_age_days": 14,
            "assessed_at": "2026-07-04T00:00:00Z",
        }

        result = evaluate_codebase_memory(record)

        self.assertIn("stale_evidence", result["violations"])
        self.assertIn("advisor_review_required", result["recommendations"])

    def test_missing_patch_mappings_are_detected(self):
        record = copy.deepcopy(self.example)
        patch = record["patch_impact_evidence"]
        patch["affected_symbols"] = []
        patch["affected_tests"] = []
        patch["rollback_surface"] = {"complete": False}
        patch["replay_ready"] = False
        patch["trace_refs"] = []

        result = evaluate_codebase_memory(record)

        self.assertIn("missing_affected_symbol_mapping", result["violations"])
        self.assertIn("missing_affected_test_mapping", result["violations"])
        self.assertIn("missing_rollback_surface", result["violations"])
        self.assertIn("missing_replay_trace", result["violations"])

    def test_high_blast_radius_without_advisor_is_detected(self):
        record = copy.deepcopy(self.example)
        record["patch_impact_evidence"]["advisor_invocation"] = {"required": False}

        result = evaluate_codebase_memory(record)

        self.assertIn("high_blast_radius_without_advisor_invocation", result["violations"])
        self.assertIn(
            "governance_sensitive_surface_touched_without_advisor_invocation",
            result["violations"],
        )
        self.assertIn("missing_advisor_invocation", result["violations"])

    def test_forbidden_adapter_claims_and_decision_proof_sealing_are_detected(self):
        record = copy.deepcopy(self.example)
        record["adapter_outputs"] = [
            "code_change_approved",
            "code_change_blocked_by_adapter",
            "final_risk_classification",
            "rollback_decision",
            "decision_proof_sealed",
        ]

        result = evaluate_codebase_memory(record)

        self.assertIn("forbidden_adapter_authority_claim", result["violations"])
        self.assertIn("adapter_claims_approval_authority", result["violations"])
        self.assertIn("adapter_claims_block_authority", result["violations"])
        self.assertIn("adapter_claims_final_risk_classification", result["violations"])
        self.assertIn("adapter_claims_rollback_authority", result["violations"])
        self.assertIn("decision_proof_sealing_claimed_by_adapter", result["violations"])


if __name__ == "__main__":
    unittest.main()
