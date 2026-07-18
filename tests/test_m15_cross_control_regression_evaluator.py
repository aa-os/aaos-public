"""Focused deterministic tests for M15 Track D cross-control regression."""

from __future__ import annotations

import ast
import copy
import json
import re
import unittest
from pathlib import Path

from runtime.m15_capability_memory_pack_evaluator import evaluate_capability_memory_pack
from runtime.m15_cross_control_regression_evaluator import evaluate_cross_control_scenario
from runtime.m15_learning_proof_evaluator import evaluate_learning_proof
from runtime.m15_lineage_rollback_portability_evaluator import evaluate_lineage_rollback_portability


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "examples" / "public-integration-pack-pilot"
SCHEMA_PATH = ROOT / "schemas" / "m15-cross-control-regression.schema.json"
MATRIX_PATH = FIXTURE_ROOT / "m15-cross-control-matrix.json"
EVALUATOR_PATH = ROOT / "runtime" / "m15_cross_control_regression_evaluator.py"
CONTRACT_PATH = ROOT / "docs" / "learning-governance" / "m15-cross-control-regression-contract.md"


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def fixture(number: int):
    return load_json(FIXTURE_ROOT / f"m15-cross-control-{number:02d}.json")


def validate_schema_subset(instance, schema, root=None):
    """Validate the deterministic JSON Schema subset used by Track D."""
    root = schema if root is None else root
    if "$ref" in schema:
        target = root
        for part in schema["$ref"][2:].split("/"):
            target = target[part]
        return validate_schema_subset(instance, target, root)
    if "oneOf" in schema:
        matches = 0
        for option in schema["oneOf"]:
            try:
                validate_schema_subset(instance, option, root)
                matches += 1
            except AssertionError:
                pass
        assert matches == 1, f"oneOf matches={matches}"
        return
    expected_type = schema.get("type")
    type_map = {"object": dict, "array": list, "string": str, "boolean": bool}
    if expected_type in type_map:
        assert isinstance(instance, type_map[expected_type]) and not (expected_type != "boolean" and isinstance(instance, bool))
    if "const" in schema:
        assert instance == schema["const"]
    if "enum" in schema:
        assert instance in schema["enum"]
    if isinstance(instance, str):
        assert len(instance) >= schema.get("minLength", 0)
        assert len(instance) <= schema.get("maxLength", len(instance))
        if "pattern" in schema:
            assert re.search(schema["pattern"], instance)
    if isinstance(instance, list):
        assert len(instance) >= schema.get("minItems", 0)
        if "items" in schema:
            for item in instance:
                validate_schema_subset(item, schema["items"], root)
    if isinstance(instance, dict):
        assert set(schema.get("required", ())).issubset(instance)
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            assert set(instance).issubset(properties)
        for key, value in instance.items():
            if key in properties:
                validate_schema_subset(value, properties[key], root)


def assert_outcome(testcase: unittest.TestCase, number: int, expected: str):
    document = fixture(number)
    testcase.assertEqual(document["expected_outcome"], expected)
    first = evaluate_cross_control_scenario(document)
    second = evaluate_cross_control_scenario(copy.deepcopy(document))
    testcase.assertEqual(first, second)
    testcase.assertEqual(first["outcome"], expected)
    testcase.assertEqual(first["findings"], sorted(set(first["findings"])))
    return first


class TrackDContractTests(unittest.TestCase):
    def test_schema_parses(self):
        schema = load_json(SCHEMA_PATH)
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIn("matrix", schema["$defs"])
        self.assertIn("scenario", schema["$defs"])

    def test_matrix_has_required_fields_and_unique_ids(self):
        matrix = load_json(MATRIX_PATH)
        validate_schema_subset(matrix, load_json(SCHEMA_PATH))
        required = {"control_id", "control_domain", "source_track", "source_artifact_type", "protected_boundary", "attempted_bypass", "required_external_control", "expected_outcome", "evidence_reference", "test_reference", "authority_boundary", "notes"}
        self.assertGreaterEqual(len(matrix["controls"]), 15)
        self.assertTrue(all(set(row) == required for row in matrix["controls"]))
        ids = [row["control_id"] for row in matrix["controls"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_matrix_preserves_release_state(self):
        matrix = load_json(MATRIX_PATH)
        self.assertEqual(matrix["tracker"], "#231-open")
        self.assertEqual(matrix["m15_status"], "active-incomplete")
        self.assertEqual(matrix["release_status"], "v0.14.0-unpublished")

    def test_exactly_twenty_four_standalone_fixtures(self):
        paths = sorted(FIXTURE_ROOT.glob("m15-cross-control-[0-9][0-9].json"))
        self.assertEqual(len(paths), 24)
        self.assertEqual([p.stem[-2:] for p in paths], [f"{i:02d}" for i in range(1, 25)])

    def test_all_fixtures_have_schema_contract_fields(self):
        required = {"schema_version", "scenario_id", "title", "source_track", "synthetic", "expected_outcome", "record", "notes"}
        schema = load_json(SCHEMA_PATH)
        for number in range(1, 25):
            document = fixture(number)
            validate_schema_subset(document, schema)
            self.assertEqual(set(document), required)
            self.assertEqual(document["schema_version"], "m15-cross-control-regression/v1")
            self.assertEqual(document["scenario_id"], f"m15-track-d-{number:02d}")
            self.assertIs(document["synthetic"], True)
            self.assertIsInstance(document["record"], dict)

    def test_contract_states_all_governing_owners(self):
        text = CONTRACT_PATH.read_text(encoding="utf-8")
        for phrase in ("Learning Proof sealing and Decision Proof sealing remain AAOS-owned", "AAOS remains the decision sovereignty layer", "Tracker #231 remains Open", "M15 remains active and incomplete", "v0.14.0 remains unpublished"):
            self.assertIn(phrase, text)

    def test_evaluator_has_no_unsafe_imports_or_calls(self):
        tree = ast.parse(EVALUATOR_PATH.read_text(encoding="utf-8"))
        imports = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in node.names}
        self.assertTrue(imports.isdisjoint({"socket", "subprocess", "requests", "urllib", "http", "importlib", "os", "pathlib"}))
        calls = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
        self.assertTrue(calls.isdisjoint({"eval", "exec", "compile", "open", "__import__"}))

    def test_does_not_mutate_input(self):
        document = fixture(18)
        before = copy.deepcopy(document)
        evaluate_cross_control_scenario(document)
        self.assertEqual(document, before)

    def test_findings_are_sorted_deduplicated_and_redacted(self):
        document = fixture(17)
        result = evaluate_cross_control_scenario(document)
        self.assertEqual(result["findings"], sorted(set(result["findings"])))
        serialized = json.dumps(result)
        self.assertNotIn(document["record"]["capability_manifest"]["diagnostic"], serialized)

    def test_malformed_root_fails_safely(self):
        result = evaluate_cross_control_scenario([])  # type: ignore[arg-type]
        self.assertEqual(result["outcome"], "reject")

    def test_cycle_fails_safely_without_mutation(self):
        document = fixture(1)
        document["record"]["cycle"] = document["record"]
        result = evaluate_cross_control_scenario(document)
        self.assertIn(result["outcome"], {"pass", "reject"})
        self.assertIs(document["record"]["cycle"], document["record"])

    def test_shared_container_is_safe_and_deterministic(self):
        document = fixture(1)
        shared = {"state": "evidence-only"}
        document["record"]["left"] = shared
        document["record"]["right"] = shared
        self.assertEqual(evaluate_cross_control_scenario(document), evaluate_cross_control_scenario(document))

    def test_deep_input_fails_safely(self):
        document = fixture(1)
        cursor = document["record"]
        for _ in range(80):
            cursor["nested"] = {}
            cursor = cursor["nested"]
        result = evaluate_cross_control_scenario(document)
        self.assertEqual(result["outcome"], "reject")
        self.assertIn("malformed:hostile-or-over-complex-input", result["findings"])


class TrackCompatibilityRegressionTests(unittest.TestCase):
    def test_track_a_valid_fixture_remains_valid(self):
        document = load_json(FIXTURE_ROOT / "m15-learning-proof-approved-evaluation-only.json")
        self.assertTrue(evaluate_learning_proof(document)["valid"])

    def test_track_a_rejected_fixture_remains_bounded(self):
        document = load_json(FIXTURE_ROOT / "m15-learning-proof-rejected-untrusted-correction.json")
        result = evaluate_learning_proof(document)
        self.assertTrue(result["valid"])
        self.assertEqual(result["authorization_outcome"], "deny")
        self.assertEqual(result["evidence_disposition"], "denied-evidence")

    def test_track_b_valid_fixture_remains_valid(self):
        document = load_json(FIXTURE_ROOT / "m15-capability-pack-valid-verified.json")
        self.assertTrue(evaluate_capability_memory_pack(document)["valid"])

    def test_track_b_revoked_fixture_remains_bounded(self):
        document = load_json(FIXTURE_ROOT / "m15-capability-pack-revoked.json")
        result = evaluate_capability_memory_pack(document)
        self.assertTrue(result["valid"])
        self.assertFalse(result["retrieval_eligible"])
        self.assertFalse(result["runtime_eligible"])
        self.assertEqual(result["evidence_disposition"], "revoked-evidence")

    def test_track_c_valid_fixture_remains_valid(self):
        document = load_json(FIXTURE_ROOT / "m15-lineage-rollback-portability-valid-complete-dependency-graph.json")
        self.assertTrue(evaluate_lineage_rollback_portability(document)["valid"])

    def test_track_c_authority_fixture_remains_bounded(self):
        document = load_json(FIXTURE_ROOT / "m15-lineage-rollback-portability-learning-proof-rollback-authority.json")
        self.assertFalse(evaluate_lineage_rollback_portability(document)["valid"])


class PublicOutputSafetyTests(unittest.TestCase):
    def test_fixture_02(self): assert_outcome(self, 2, "quarantine")
    def test_fixture_17(self): assert_outcome(self, 17, "quarantine")
    def test_nested_evidence_reference_is_inspected(self):
        document = fixture(1); document["record"]["evidence_references"] = [{"value": "Bearer SYNTHETIC123456"}]
        self.assertEqual(evaluate_cross_control_scenario(document)["outcome"], "quarantine")
    def test_schema_validity_does_not_exempt_sensitive_scan(self):
        document = fixture(1); document["record"]["verified_status"] = {"private_key": "synthetic"}
        self.assertEqual(evaluate_cross_control_scenario(document)["outcome"], "quarantine")


class ProvenanceHumanReviewTests(unittest.TestCase):
    def test_fixture_03(self): assert_outcome(self, 3, "reject")
    def test_fixture_15(self): assert_outcome(self, 15, "reject")
    def test_fixture_16(self): assert_outcome(self, 16, "reject")
    def test_schema_validation_cannot_authorize_merge(self):
        document = fixture(1); document["record"]["claim"] = "schema validation authorizes merge approval"
        self.assertEqual(evaluate_cross_control_scenario(document)["outcome"], "reject")


class AdmissionTests(unittest.TestCase):
    def test_fixture_04(self): assert_outcome(self, 4, "reject")
    def test_fixture_05(self): assert_outcome(self, 5, "reject")
    def test_fixture_06(self): assert_outcome(self, 6, "pass")
    def test_fixture_07(self): assert_outcome(self, 7, "reject")
    def test_fixture_08(self): assert_outcome(self, 8, "reject")
    def test_fixture_09(self): assert_outcome(self, 9, "reject")
    def test_runtime_compatibility_is_not_authorization(self):
        document = fixture(6); document["record"]["claim"] = "runtime compatibility treated as runtime authorization"
        self.assertEqual(evaluate_cross_control_scenario(document)["outcome"], "reject")
    def test_generated_specification_is_not_tool(self):
        document = fixture(6); document["record"]["claim"] = "generated specification treated as executable tool"
        self.assertEqual(evaluate_cross_control_scenario(document)["outcome"], "reject")


class EvidenceAdmissionTests(unittest.TestCase):
    def test_fixture_10(self): assert_outcome(self, 10, "reject")
    def test_fixture_11(self): assert_outcome(self, 11, "reject")
    def test_superseded_evidence_is_not_current(self):
        document = fixture(6); document["record"]["claim"] = "superseded evidence treated as current"
        self.assertEqual(evaluate_cross_control_scenario(document)["outcome"], "reject")
    def test_digest_drift_requires_readmission(self):
        document = fixture(6); document["record"]["claim"] = "dependency digest changed without re-admission"
        self.assertEqual(evaluate_cross_control_scenario(document)["outcome"], "reject")


class AuthorityBoundaryTests(unittest.TestCase):
    def test_fixture_12(self): assert_outcome(self, 12, "reject")
    def test_fixture_13(self): assert_outcome(self, 13, "reject")
    def test_fixture_14(self): assert_outcome(self, 14, "reject")
    def test_fixture_18(self): assert_outcome(self, 18, "reject")
    def test_fixture_21(self): assert_outcome(self, 21, "reject")
    def test_fixture_22(self): assert_outcome(self, 22, "reject")
    def test_valid_track_a_fixture_passes(self): assert_outcome(self, 1, "pass")
    def test_all_structured_authority_fields_fail_recursively(self):
        fields = ("governance_authority", "policy_authority", "identity_authority", "risk_accepted", "deployment_approved", "installation_approved", "package_admission_approved", "tool_registration_approved", "runtime_authorized", "rollback_authorized", "rollback_executed", "deletion_authorized", "deletion_executed", "provider_migration_approved", "replacement_model_authorized", "audit_closed", "waiver_approved", "authority_transferred", "learning_proof_sealed", "decision_proof_sealed", "m15_completed", "release_approved")
        for field in fields:
            document = fixture(1)
            document["record"]["extensions"] = {"nested": {field: True}}
            with self.subTest(field=field):
                self.assertEqual(evaluate_cross_control_scenario(document)["outcome"], "reject")


class DecisionProofOwnershipTests(unittest.TestCase):
    def test_fixture_19(self): assert_outcome(self, 19, "reject")
    def test_fixture_20(self): assert_outcome(self, 20, "reject")
    def test_linkage_is_not_verification(self):
        document = fixture(1); document["record"]["claim"] = "Decision Proof linkage treated as verification"
        self.assertEqual(evaluate_cross_control_scenario(document)["outcome"], "reject")
    def test_verification_is_not_sealing(self):
        document = fixture(1); document["record"]["claim"] = "Decision Proof verification treated as sealing"
        self.assertEqual(evaluate_cross_control_scenario(document)["outcome"], "reject")


class ReleaseM15StatusTests(unittest.TestCase):
    def test_fixture_23(self): assert_outcome(self, 23, "reject")
    def test_fixture_24(self): assert_outcome(self, 24, "reject")
    def test_matrix_keeps_tracker_open(self): self.assertEqual(load_json(MATRIX_PATH)["tracker"], "#231-open")
    def test_matrix_keeps_release_unpublished(self): self.assertEqual(load_json(MATRIX_PATH)["release_status"], "v0.14.0-unpublished")


class AllFixtureOutcomeTests(unittest.TestCase):
    def test_every_fixture_has_intended_deterministic_outcome(self):
        for number in range(1, 25):
            document = fixture(number)
            self.assertEqual(evaluate_cross_control_scenario(document)["outcome"], document["expected_outcome"], number)


if __name__ == "__main__":
    unittest.main()
