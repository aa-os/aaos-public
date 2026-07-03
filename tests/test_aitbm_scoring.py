import copy
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.aitbm_scoring_evaluator import (
    FORBIDDEN_ADAPTER_OUTPUTS,
    advisor_review_should_be_required,
    detect_forbidden_authority_claims,
    evaluate_aitbm_scoring,
)


SCHEMA_PATH = ROOT / "schemas" / "aitbm-scoring-evidence.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "aitbm-scoring" / "high-risk-stale-evidence.json"


class SchemaValidationError(AssertionError):
    pass


def load_json(path):
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def validate(instance, schema, path="$"):
    """Validate the schema subset used by AAOS public evidence records."""
    if "type" in schema:
        expected = schema["type"]
        type_checks = {
            "object": dict,
            "array": list,
            "string": str,
            "boolean": bool,
            "integer": int,
            "number": (int, float),
        }
        if expected in type_checks and not isinstance(instance, type_checks[expected]):
            raise SchemaValidationError(f"{path}: expected {expected}")

    if "const" in schema and instance != schema["const"]:
        raise SchemaValidationError(f"{path}: expected const {schema['const']!r}")

    if "enum" in schema and instance not in schema["enum"]:
        raise SchemaValidationError(f"{path}: {instance!r} not in enum")

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                raise SchemaValidationError(f"{path}: missing required {key}")

        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = sorted(set(instance) - set(properties))
            if extra:
                raise SchemaValidationError(f"{path}: unexpected properties {extra}")

        for key, subschema in properties.items():
            if key in instance:
                validate(instance[key], subschema, f"{path}.{key}")

    if isinstance(instance, list):
        min_items = schema.get("minItems")
        if min_items is not None and len(instance) < min_items:
            raise SchemaValidationError(f"{path}: expected at least {min_items} items")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(instance):
                validate(item, item_schema, f"{path}[{index}]")


class AITBMScoringTests(unittest.TestCase):
    def setUp(self):
        self.schema = load_json(SCHEMA_PATH)
        self.example = load_json(EXAMPLE_PATH)

    def test_schema_document_is_valid_json_schema_shape(self):
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(
            self.schema["$id"],
            "https://aa-os.org/schemas/aitbm-scoring-evidence.schema.json",
        )
        self.assertEqual(self.schema["type"], "object")
        self.assertFalse(self.schema["additionalProperties"])

    def test_high_risk_stale_example_matches_schema(self):
        validate(self.example, self.schema)

    def test_example_does_not_claim_forbidden_authority(self):
        self.assertEqual(detect_forbidden_authority_claims(self.example), [])

    def test_forbidden_authority_claims_are_detected(self):
        for forbidden_output in FORBIDDEN_ADAPTER_OUTPUTS:
            record = copy.deepcopy(self.example)
            record["adapter_output"] = forbidden_output

            result = evaluate_aitbm_scoring(record)

            self.assertEqual(result["status"], "review_required")
            self.assertIn("recommendation_to_fail_closed", result["recommendations"])
            self.assertIn("advisor_review_required", result["recommendations"])
            self.assertIn(
                {"code": "forbidden_authority_claim", "claims": [forbidden_output]},
                result["violations"],
            )

    def test_high_risk_stale_example_recommends_review_and_reassessment(self):
        result = evaluate_aitbm_scoring(self.example)

        self.assertEqual(result["status"], "review_required")
        self.assertIn({"code": "stale_evidence"}, result["violations"])
        self.assertIn({"code": "low_evidence_confidence"}, result["violations"])
        self.assertIn(
            {"code": "high_or_critical_risk_score", "rating": "high"},
            result["violations"],
        )
        self.assertIn("recommendation_to_review", result["recommendations"])
        self.assertIn("recommendation_to_retest", result["recommendations"])
        self.assertIn("recommendation_to_restrict", result["recommendations"])
        self.assertIn("human_approval_required", result["recommendations"])
        self.assertIn("recommendation_to_fail_closed", result["recommendations"])
        self.assertIn("advisor_review_required", result["recommendations"])

    def test_maturity_below_threshold_is_violation(self):
        result = evaluate_aitbm_scoring(self.example)

        self.assertIn({"code": "maturity_below_threshold"}, result["violations"])
        self.assertIn("recommendation_to_retest", result["recommendations"])

    def test_weak_containment_high_access_and_sensitive_data_restrict(self):
        result = evaluate_aitbm_scoring(self.example)

        self.assertIn({"code": "weak_containment_maturity"}, result["violations"])
        self.assertIn({"code": "high_tool_access"}, result["violations"])
        self.assertIn({"code": "high_data_sensitivity"}, result["violations"])
        self.assertIn("recommendation_to_restrict", result["recommendations"])

    def test_missing_reassessment_date_requires_advisor_review(self):
        record = copy.deepcopy(self.example)
        record["required_reassessment_date"] = ""

        result = evaluate_aitbm_scoring(record)

        self.assertIn({"code": "reassessment_missing_or_expired"}, result["violations"])
        self.assertTrue(advisor_review_should_be_required(record))
        self.assertIn("advisor_review_required", result["recommendations"])

    def test_missing_advisor_invocation_is_violation_when_triggered(self):
        record = copy.deepcopy(self.example)
        record["advisor_invocation"]["required"] = False

        result = evaluate_aitbm_scoring(record)

        self.assertIn({"code": "advisor_review_required"}, result["violations"])

    def test_adapter_final_decision_claim_is_violation(self):
        record = copy.deepcopy(self.example)
        record["decision_gate_result"]["final_decision"] = "decided_by_aaos_governance"

        result = evaluate_aitbm_scoring(record)

        self.assertIn({"code": "adapter_final_decision_claim"}, result["violations"])
        self.assertIn("recommendation_to_fail_closed", result["recommendations"])


if __name__ == "__main__":
    unittest.main()
