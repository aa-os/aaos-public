import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.release_governance_evaluator import (  # noqa: E402
    REQUIRED_SYSTEMS,
    detect_forbidden_authority_claims,
    evaluate_adapter_registry,
    evaluate_cross_adapter_regression,
    evaluate_release_governance,
)


RELEASE_SCHEMA_PATH = ROOT / "schemas" / "release-governance-consistency.schema.json"
REGRESSION_SCHEMA_PATH = (
    ROOT / "schemas" / "cross-adapter-regression-evidence.schema.json"
)
RELEASE_EXAMPLE_PATH = (
    ROOT / "examples" / "release-governance" / "v0.6.0-consistency-check.json"
)
REGRESSION_EXAMPLE_PATH = (
    ROOT / "examples" / "cross-adapter-regression" / "sovereignty-regression-pack.json"
)
REGISTRY_PATH = ROOT / "registries" / "adapter-registry.yaml"


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


class ReleaseGovernanceEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.release_schema = load_json(RELEASE_SCHEMA_PATH)
        self.regression_schema = load_json(REGRESSION_SCHEMA_PATH)
        self.release_example = load_json(RELEASE_EXAMPLE_PATH)
        self.regression_example = load_json(REGRESSION_EXAMPLE_PATH)

    def test_examples_match_schemas(self):
        validate_subset(self.release_schema, self.release_example)
        validate_subset(self.regression_schema, self.regression_example)

    def test_release_consistency_example_passes(self):
        result = evaluate_release_governance(self.release_example)

        self.assertTrue(result["release_consistency_passed"])
        self.assertFalse(result["release_consistency_failed"])
        self.assertEqual(result["regression_findings"], [])
        self.assertEqual(result["missing_evidence"], [])

    def test_release_consistency_detects_required_mismatches(self):
        record = copy.deepcopy(self.release_example)
        record["readme_version_status"]["present"] = False
        record["milestone_completion_wording"]["matches"] = False
        record["issue_tracker_closure"]["closed"] = False
        record["closing_prs"][0]["merged"] = False
        record["release_tag"]["present"] = False
        record["release_title_consistency"]["matches"] = False
        record["release_body_consistency"]["governance_boundary_preserved"] = False
        record["next_phase_declaration"]["matches_expected"] = False

        result = evaluate_release_governance(record)

        self.assertTrue(result["release_consistency_failed"])
        self.assertIn("missing_readme_version", result["regression_findings"])
        self.assertIn("milestone_completion_mismatch", result["regression_findings"])
        self.assertIn("tracker_issue_not_closed", result["regression_findings"])
        self.assertIn("closing_pr_not_merged", result["regression_findings"])
        self.assertIn("missing_release_tag", result["regression_findings"])
        self.assertIn("release_title_mismatch", result["regression_findings"])
        self.assertIn("release_body_missing_governance_boundary", result["regression_findings"])
        self.assertIn("next_phase_mismatch", result["regression_findings"])

    def test_forbidden_outputs_are_detected_as_authority_claims(self):
        record = copy.deepcopy(self.release_example)
        record["runtime_output"] = {
            "release_approved": True,
            "decision_proof_sealed": True,
            "audit_closed": True,
        }

        claims = detect_forbidden_authority_claims(record)
        result = evaluate_release_governance(record)

        self.assertIn("release_approved", claims)
        self.assertIn("decision_proof_sealed", claims)
        self.assertIn("audit_closed", claims)
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("decision_proof_sealing_claimed_outside_aaos", result["regression_findings"])
        self.assertIn("audit_closure_claimed_outside_aaos", result["regression_findings"])

    def test_cross_adapter_regression_example_passes(self):
        result = evaluate_cross_adapter_regression(self.regression_example)

        self.assertTrue(result["release_consistency_passed"])
        self.assertEqual(result["regression_findings"], [])
        self.assertEqual(result["missing_evidence"], [])

    def test_cross_adapter_regression_requires_all_m1_to_m7_systems(self):
        record = copy.deepcopy(self.regression_example)
        record["included_systems"] = record["included_systems"][:-1]

        result = evaluate_cross_adapter_regression(record)

        self.assertTrue(result["release_consistency_failed"])
        self.assertIn(
            "cross_adapter_regression_missing_required_system",
            result["regression_findings"],
        )
        self.assertIn(
            "missing_system:open_tag_human_agent_workspace_adapter",
            result["missing_evidence"],
        )

    def test_cross_adapter_regression_detects_sovereignty_violations(self):
        record = copy.deepcopy(self.regression_example)
        record["included_systems"][0]["forbidden_authority_claims_detected"] = [
            "final_governance_authority"
        ]
        record["sovereignty_checks"]["all_forbidden_claims_absent"] = False
        record["sovereignty_checks"]["decision_proof_sealing_claimed_outside_aaos"] = True
        record["sovereignty_checks"]["audit_closure_claimed_outside_aaos"] = True

        result = evaluate_cross_adapter_regression(record)

        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("adapter_claims_forbidden_authority", result["regression_findings"])
        self.assertIn("decision_proof_sealing_claimed_outside_aaos", result["regression_findings"])
        self.assertIn("audit_closure_claimed_outside_aaos", result["regression_findings"])
        self.assertTrue(result["fail_closed_recommended"])

    def test_registry_contains_required_systems_and_boundary(self):
        registry_text = REGISTRY_PATH.read_text(encoding="utf-8")

        for adapter_id in REQUIRED_SYSTEMS:
            self.assertIn(f"adapter_id: {adapter_id}", registry_text)

        self.assertIn("registry_boundary:", registry_text)
        self.assertIn("final_governance_authority", registry_text)
        self.assertIn("aaos_retained_authority_statement", registry_text)

    def test_registry_evaluator_detects_missing_fields_and_authority_claims(self):
        registry = {
            "adapters": [
                {
                    "adapter_id": "bad_adapter",
                    "adapter_name": "Bad Adapter",
                    "final_governance_authority": True,
                }
            ]
        }

        result = evaluate_adapter_registry(registry)

        self.assertTrue(result["release_consistency_failed"])
        self.assertIn("adapter_registry_missing_required_fields", result["regression_findings"])
        self.assertIn("adapter_missing_aaos_retained_authority_statement", result["regression_findings"])
        self.assertIn("adapter_claims_forbidden_authority", result["regression_findings"])
        self.assertTrue(result["authority_boundary_violation"])


if __name__ == "__main__":
    unittest.main()
