import copy
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.cloudflare_security_audit_evaluator import (
    FORBIDDEN_ADAPTER_OUTPUTS,
    detect_forbidden_authority_claims,
    evaluate_cloudflare_security_audit,
)


SCHEMA_PATH = ROOT / "schemas" / "cloudflare-security-audit-evidence.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "cloudflare-security-audit" / "release-gate-triggered.json"


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


class CloudflareSecurityAuditTests(unittest.TestCase):
    def setUp(self):
        self.schema = load_json(SCHEMA_PATH)
        self.example = load_json(EXAMPLE_PATH)

    def test_schema_document_is_valid_json_schema_shape(self):
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(
            self.schema["$id"],
            "https://aa-os.org/schemas/cloudflare-security-audit-evidence.schema.json",
        )
        self.assertEqual(self.schema["type"], "object")
        self.assertFalse(self.schema["additionalProperties"])

    def test_release_gate_example_matches_schema(self):
        validate(self.example, self.schema)

    def test_example_does_not_claim_forbidden_authority(self):
        self.assertEqual(detect_forbidden_authority_claims(self.example), [])

    def test_forbidden_authority_claims_are_detected(self):
        for forbidden_output in FORBIDDEN_ADAPTER_OUTPUTS:
            record = copy.deepcopy(self.example)
            record["adapter_output"] = forbidden_output

            result = evaluate_cloudflare_security_audit(record)

            self.assertEqual(result["status"], "review_required")
            self.assertIn("fail_closed_recommended", result["recommendations"])
            self.assertIn(
                {"code": "forbidden_authority_claim", "claims": [forbidden_output]},
                result["violations"],
            )

    def test_high_severity_finding_triggers_release_gate_recommendation(self):
        result = evaluate_cloudflare_security_audit(self.example)

        self.assertIn("release_gate_triggered", result["recommendations"])
        self.assertTrue(self.example["release_gate"]["gate_triggered"])
        self.assertEqual(self.example["release_gate"]["adapter_recommendation"], "block_or_escalate")
        self.assertEqual(
            self.example["release_gate"]["final_release_decision"],
            "not_decided_by_adapter",
        )

    def test_missing_release_gate_for_high_severity_finding_is_violation(self):
        record = copy.deepcopy(self.example)
        record["release_gate"]["gate_triggered"] = False
        record["release_gate"]["adapter_recommendation"] = "continue"

        result = evaluate_cloudflare_security_audit(record)

        self.assertIn(
            {"code": "release_gate_required", "finding_ids": ["CF-AUDIT-HIGH-001"]},
            result["violations"],
        )
        self.assertIn(
            {"code": "release_gate_recommendation_required", "finding_ids": ["CF-AUDIT-HIGH-001"]},
            result["violations"],
        )

    def test_missing_replay_evidence_triggers_fail_closed_recommendation(self):
        record = copy.deepcopy(self.example)
        record["replay_packet"]["replay_ready"] = False
        record["replay_packet"]["evidence_hashes"] = []

        result = evaluate_cloudflare_security_audit(record)

        self.assertIn({"code": "missing_replay_evidence"}, result["violations"])
        self.assertIn("fail_closed_recommended", result["recommendations"])

    def test_human_review_required_for_high_or_critical_findings(self):
        result = evaluate_cloudflare_security_audit(self.example)

        self.assertTrue(self.example["human_review_handoff"]["required"])
        self.assertIn("human_review_required", result["recommendations"])

    def test_missing_human_review_for_high_or_critical_findings_is_violation(self):
        record = copy.deepcopy(self.example)
        record["human_review_handoff"]["required"] = False

        result = evaluate_cloudflare_security_audit(record)

        self.assertIn(
            {"code": "human_review_required", "finding_ids": ["CF-AUDIT-HIGH-001"]},
            result["violations"],
        )


if __name__ == "__main__":
    unittest.main()
import copy
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.cloudflare_security_audit_evaluator import (
    FORBIDDEN_ADAPTER_OUTPUTS,
    detect_forbidden_authority_claims,
    evaluate_cloudflare_security_audit,
)


SCHEMA_PATH = ROOT / "schemas" / "cloudflare-security-audit-evidence.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "cloudflare-security-audit" / "release-gate-triggered.json"


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


class CloudflareSecurityAuditTests(unittest.TestCase):
      def setUp(self):
                self.schema = load_json(SCHEMA_PATH)
        self.example = load_json(EXAMPLE_PATH)

    def test_schema_document_is_valid_json_schema_shape(self):
              self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(
                      self.schema["$id"],
                      "https://aa-os.org/schemas/cloudflare-security-audit-evidence.schema.json",
        )
        self.assertEqual(self.schema["type"], "object")
        self.assertFalse(self.schema["additionalProperties"])

    def test_release_gate_example_matches_schema(self):
              validate(self.example, self.schema)

    def test_example_does_not_claim_forbidden_authority(self):
              self.assertEqual(detect_forbidden_authority_claims(self.example), [])

    def test_forbidden_authority_claims_are_detected(self):
              for forbidden_output in FORBIDDEN_ADAPTER_OUTPUTS:
                            record = copy.deepcopy(self.example)
            record["adapter_output"] = forbidden_output

            result = evaluate_cloudflare_security_audit(record)

            self.assertEqual(result["status"], "review_required")
            self.assertIn("fail_closed_recommended", result["recommendations"])
            self.assertIn(
                              {"code": "forbidden_authority_claim", "claims": [forbidden_output]},
                              result["violations"],
            )

    def test_high_severity_finding_triggers_release_gate_recommendation(self):
              result = evaluate_cloudflare_security_audit(self.example)

        self.assertIn("release_gate_triggered", result["recommendations"])
        self.assertTrue(self.example["release_gate"]["gate_triggered"])
        self.assertEqual(self.example["release_gate"]["adapter_recommendation"], "block_or_escalate")
        self.assertEqual(
                      self.example["release_gate"]["final_release_decision"],
                      "not_decided_by_adapter",
        )

    def test_missing_release_gate_for_high_severity_finding_is_violation(self):
              record = copy.deepcopy(self.example)
        record["release_gate"]["gate_triggered"] = False
        record["release_gate"]["adapter_recommendation"] = "continue"

        result = evaluate_cloudflare_security_audit(record)

        self.assertIn(
                      {"code": "release_gate_required", "finding_ids": ["CF-AUDIT-HIGH-001"]},
                      result["violations"],
        )
        self.assertIn(
                      {"code": "release_gate_recommendation_required", "finding_ids": ["CF-AUDIT-HIGH-001"]},
                      result["violations"],
        )

    def test_missing_replay_evidence_triggers_fail_closed_recommendation(self):
              record = copy.deepcopy(self.example)
        record["replay_packet"]["replay_ready"] = False
        record["replay_packet"]["evidence_hashes"] = []

        result = evaluate_cloudflare_security_audit(record)

        self.assertIn({"code": "missing_replay_evidence"}, result["violations"])
        self.assertIn("fail_closed_recommended", result["recommendations"])

    def test_human_review_required_for_high_or_critical_findings(self):
              result = evaluate_cloudflare_security_audit(self.example)

        self.assertTrue(self.example["human_review_handoff"]["required"])
        self.assertIn("human_review_required", result["recommendations"])

    def test_missing_human_review_for_high_or_critical_findings_is_violation(self):
              record = copy.deepcopy(self.example)
        record["human_review_handoff"]["required"] = False

        result = evaluate_cloudflare_security_audit(record)

        self.assertIn(
                      {"code": "human_review_required", "finding_ids": ["CF-AUDIT-HIGH-001"]},
                      result["violations"],
        )


if __name__ == "__main__":
      unittest.main()
