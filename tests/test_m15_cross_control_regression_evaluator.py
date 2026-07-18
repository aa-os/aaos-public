"""Focused deterministic tests for M15 Track D cross-control regression."""

from __future__ import annotations

import ast
import copy
import json
import re
import unittest
from collections.abc import Mapping
from pathlib import Path
from unittest import mock

import runtime.m15_cross_control_regression_evaluator as track_d_module
from runtime.ai_authored_pr_provenance_evaluator import (
    REQUIRED_BOUNDARY_STATEMENTS as PROVENANCE_BOUNDARIES,
    evaluate_ai_authored_pr_provenance_fixture,
)
from runtime.external_evidence_admission_evaluator import evaluate_external_evidence_admission
from runtime.m14_cross_control_authority_boundary_evaluator import (
    REQUIRED_BOUNDARY_STATEMENTS as AUTHORITY_BOUNDARIES,
    evaluate_m14_cross_control_authority_boundary,
)
from runtime.m15_capability_memory_pack_evaluator import evaluate_capability_memory_pack
from runtime.m15_cross_control_regression_evaluator import (
    adapt_sensitive_record_to_public_output_gate,
    evaluate_cross_control_scenario,
    evaluate_source_control_composition,
)
from runtime.m15_learning_proof_evaluator import evaluate_learning_proof
from runtime.m15_lineage_rollback_portability_evaluator import evaluate_lineage_rollback_portability
from runtime.public_issue_exfiltration_gate_evaluator import (
    REQUIRED_BOUNDARY_STATEMENTS as PUBLIC_OUTPUT_BOUNDARIES,
    evaluate_public_issue_exfiltration_gate_fixture,
)
from runtime.skill_admission_evaluator import (
    REQUIRED_BOUNDARY_STATEMENTS as SKILL_BOUNDARIES,
    evaluate_fixture_case,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "examples" / "public-integration-pack-pilot"
SCHEMA_PATH = ROOT / "schemas" / "m15-cross-control-regression.schema.json"
MATRIX_PATH = FIXTURE_ROOT / "m15-cross-control-matrix.json"
EVALUATOR_PATH = ROOT / "runtime" / "m15_cross_control_regression_evaluator.py"
CONTRACT_PATH = ROOT / "docs" / "learning-governance" / "m15-cross-control-regression-contract.md"
PUBLIC_OUTPUT_FIXTURE_PATH = FIXTURE_ROOT / "m14-public-issue-exfiltration-gate-fixtures.json"
PROVENANCE_FIXTURE_PATH = FIXTURE_ROOT / "m14-ai-authored-pr-provenance-fixtures.json"
PROVENANCE_WORKFLOW_PATH = ROOT / ".github" / "workflows" / "m14-ai-pr-provenance.yml"
SKILL_FIXTURE_PATH = FIXTURE_ROOT / "m14-skill-admission-fixtures.json"
EXTERNAL_EVIDENCE_FIXTURE_PATH = ROOT / "examples" / "external-evidence-admission" / "twinkle-hub-fixtures.json"
M14_AUTHORITY_FIXTURE_PATH = FIXTURE_ROOT / "m14-cross-control-authority-boundary-regression-fixtures.json"

TRUSTED_EVIDENCE_POLICY = {
    "policy_version": "aaos-external-evidence-admission-v1",
    "freshness_threshold_seconds": 604800,
    "admission_policy": {
        "stale_freshness_result": "degraded",
        "unknown_freshness_result": "rejected",
        "partial_extraction_result": "degraded",
        "fallback_required_result": "degraded",
    },
}


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def fixture(number: int):
    return load_json(FIXTURE_ROOT / f"m15-cross-control-{number:02d}.json")


def public_output_source_result(record):
    adapter = adapt_sensitive_record_to_public_output_gate(record)
    source_fixture = load_json(PUBLIC_OUTPUT_FIXTURE_PATH)
    case = source_fixture["fixture_cases"][0]
    case.update(adapter["m14_public_output_fields"])
    case["output_gate_decision"] = "public_output_blocked"
    case["expected_result"] = "public_output_blocked"
    case["fail_closed_recommended"] = True
    case["human_review_required"] = True
    case["decision_proof_fields"]["output_gate_result"] = "public_output_blocked"
    case["decision_proof_fields"]["blocked_content_classes"] = adapter["blocked_content_classes"]
    source_result = evaluate_public_issue_exfiltration_gate_fixture(source_fixture)
    case_result = source_result["case_results"][0]
    return source_result, {
        "public_issue_exfiltration_gate_valid": source_result["public_issue_exfiltration_gate_valid"],
        "public_output_blocked": case_result["public_output_blocked"],
        "public_output_allowed": case_result["public_output_allowed"],
        "redaction_required": case_result["redaction_required"],
        "human_review_required": case_result["human_review_required"],
    }


def complete_source_control_outputs():
    public_result = evaluate_public_issue_exfiltration_gate_fixture(
        load_json(PUBLIC_OUTPUT_FIXTURE_PATH)
    )
    public_case = next(
        item
        for item in public_result["case_results"]
        if item["case_type"] == "allowed_public_only_issue_response_no_privileged_context"
    )
    provenance_result = evaluate_ai_authored_pr_provenance_fixture(
        load_json(PROVENANCE_FIXTURE_PATH),
        PROVENANCE_WORKFLOW_PATH.read_text(encoding="utf-8"),
    )
    evidence_fixture = load_json(EXTERNAL_EVIDENCE_FIXTURE_PATH)
    evidence_result = evaluate_external_evidence_admission(
        evidence_fixture["fixture_cases"][0], trusted_policy=TRUSTED_EVIDENCE_POLICY
    )
    authority_fixture = load_json(M14_AUTHORITY_FIXTURE_PATH)
    authority_result = evaluate_m14_cross_control_authority_boundary(
        authority_fixture, m14_source_artifacts(authority_fixture)
    )
    outputs = {
        "m14-public-output-exfiltration": {
            "public_issue_exfiltration_gate_valid": public_result["public_issue_exfiltration_gate_valid"],
            "public_output_blocked": public_case["public_output_blocked"],
            "public_output_allowed": public_case["public_output_allowed"],
            "redaction_required": public_case["redaction_required"],
            "human_review_required": public_case["human_review_required"],
        },
        "m14-ai-provenance": provenance_result,
        "m14-skill-admission": evaluate_fixture_case(
            load_json(SKILL_FIXTURE_PATH),
            "case_01_complete_synthetic_low_risk_jetson_diagnostic",
        ),
        "external-evidence-admission": evidence_result,
        "m14-cross-control-authority": authority_result,
    }
    return json.loads(json.dumps(outputs, sort_keys=True))


def m14_source_artifacts(fixture_document):
    return {
        path: (ROOT / path).read_text(encoding="utf-8")
        for item in fixture_document["source_artifact_manifest"]
        for path in item["source_paths"]
    }


class HostileMapping(Mapping):
    def __getitem__(self, key):
        raise RuntimeError("hostile")

    def __iter__(self):
        raise RuntimeError("hostile")

    def __len__(self):
        return 1

    def items(self):
        raise RuntimeError("hostile")


class MalformedItemsMapping(Mapping):
    def __getitem__(self, key):
        raise KeyError(key)

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 1

    def items(self):
        return [("not-a-pair",)]


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
        required = {"control_id", "source_control_id", "control_domain", "source_track", "source_artifact_type", "protected_boundary", "attempted_bypass", "required_external_control", "expected_outcome", "evidence_reference", "test_reference", "authority_boundary", "notes"}
        self.assertGreaterEqual(len(matrix["controls"]), 15)
        self.assertTrue(all(set(row) == required for row in matrix["controls"]))
        ids = [row["control_id"] for row in matrix["controls"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_source_control_bindings_are_exact_and_path_bound(self):
        matrix = load_json(MATRIX_PATH)
        bindings = {item["source_control_id"]: item for item in matrix["source_control_bindings"]}
        expected_paths = {
            "m14-public-output-exfiltration": {
                "runtime/public_issue_exfiltration_gate_evaluator.py",
                "tests/test_public_issue_exfiltration_gate_evaluator.py",
                "examples/public-integration-pack-pilot/m14-public-issue-exfiltration-gate-fixtures.json",
            },
            "m14-ai-provenance": {
                "runtime/ai_authored_pr_provenance_evaluator.py",
                "tests/test_ai_authored_pr_provenance_evaluator.py",
                "examples/public-integration-pack-pilot/m14-ai-authored-pr-provenance-fixtures.json",
                ".github/workflows/m14-ai-pr-provenance.yml",
            },
            "m14-skill-admission": {
                "runtime/skill_admission_evaluator.py",
                "tests/test_skill_admission_evaluator.py",
                "examples/public-integration-pack-pilot/m14-skill-admission-fixtures.json",
            },
            "external-evidence-admission": {
                "runtime/external_evidence_admission_evaluator.py",
                "tests/test_external_evidence_admission_evaluator.py",
                "schemas/external-evidence-admission.schema.json",
                "examples/external-evidence-admission/twinkle-hub-fixtures.json",
            },
            "m14-cross-control-authority": {
                "runtime/m14_cross_control_authority_boundary_evaluator.py",
                "tests/test_m14_cross_control_authority_boundary_evaluator.py",
                "examples/public-integration-pack-pilot/m14-cross-control-authority-boundary-regression-fixtures.json",
            },
        }
        self.assertEqual(set(bindings), set(expected_paths))
        for control_id, paths in expected_paths.items():
            binding = bindings[control_id]
            self.assertEqual(set(binding["source_artifact_paths"]), paths)
            self.assertEqual(binding["maintained_integrity_reference"], "path-binding:maintained-main")
            for path in paths:
                self.assertTrue((ROOT / path).is_file(), path)
        self.assertEqual(set(bindings["m14-public-output-exfiltration"]["required_boundary_statements"]), PUBLIC_OUTPUT_BOUNDARIES)
        self.assertEqual(set(bindings["m14-ai-provenance"]["required_boundary_statements"]), PROVENANCE_BOUNDARIES)
        self.assertEqual(set(bindings["m14-skill-admission"]["required_boundary_statements"]), SKILL_BOUNDARIES)
        self.assertEqual(set(bindings["m14-cross-control-authority"]["required_boundary_statements"]), AUTHORITY_BOUNDARIES)
        self.assertEqual(bindings["external-evidence-admission"]["source_schema_or_contract_version"], "aaos-external-evidence-admission-v1")
        self.assertEqual(
            bindings["m14-ai-provenance"]["source_schema_or_contract_version"],
            "unversioned-contract/source-pr-206/path-bound-maintained-main",
        )
        self.assertEqual(
            bindings["m14-cross-control-authority"]["source_schema_or_contract_version"],
            "unversioned-contract/source-pr-210/path-bound-maintained-main",
        )

    def test_every_matrix_row_references_a_bound_source_control(self):
        matrix = load_json(MATRIX_PATH)
        binding_ids = {item["source_control_id"] for item in matrix["source_control_bindings"]}
        self.assertTrue(all(row["source_control_id"] in binding_ids for row in matrix["controls"]))

    def test_every_matrix_and_adapter_test_reference_resolves(self):
        matrix = load_json(MATRIX_PATH)
        references = [item["adapter_test_reference"] for item in matrix["source_control_bindings"]]
        references.extend(item["test_reference"] for item in matrix["controls"])
        for reference in references:
            with self.subTest(reference=reference):
                class_name, method_name = reference.split(".", 1)
                test_class = globals().get(class_name)
                self.assertIsNotNone(test_class, reference)
                self.assertTrue(hasattr(test_class, method_name), reference)

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

    def test_source_control_composition_does_not_mutate_inputs(self):
        document = fixture(1)
        source_outputs = complete_source_control_outputs()
        document_before = copy.deepcopy(document)
        source_before = copy.deepcopy(source_outputs)
        result = evaluate_source_control_composition(document, source_outputs)
        self.assertEqual(result["outcome"], "pass")
        self.assertEqual(document, document_before)
        self.assertEqual(source_outputs, source_before)

    def test_all_bound_source_control_outputs_are_required(self):
        result = evaluate_source_control_composition(fixture(1), {})
        self.assertEqual(result["outcome"], "reject")
        self.assertEqual(
            {item["source_control_id"] for item in result["source_control_results"]},
            {
                "m14-public-output-exfiltration",
                "m14-ai-provenance",
                "m14-skill-admission",
                "external-evidence-admission",
                "m14-cross-control-authority",
            },
        )
        self.assertTrue(
            all(item["findings"] == ["missing-output"] for item in result["source_control_results"])
        )

    def test_cyclic_source_control_output_fails_closed(self):
        source_output = {}
        source_output["cycle"] = source_output
        result = evaluate_source_control_composition(
            fixture(1), {"m14-public-output-exfiltration": source_output}
        )
        self.assertEqual(result["outcome"], "reject")
        self.assertEqual(result["findings"], ["malformed:source-control-cyclic-container"])

    def test_shared_source_control_output_fails_closed(self):
        shared = {"state": "synthetic"}
        source_output = {"left": shared, "right": shared}
        result = evaluate_source_control_composition(
            fixture(1), {"m14-public-output-exfiltration": source_output}
        )
        self.assertEqual(result["outcome"], "reject")
        self.assertEqual(result["findings"], ["malformed:source-control-shared-container"])

    def test_findings_are_sorted_deduplicated_and_redacted(self):
        document = fixture(17)
        result = evaluate_cross_control_scenario(document)
        self.assertEqual(result["findings"], sorted(set(result["findings"])))
        serialized = json.dumps(result)
        self.assertNotIn(document["record"]["capability_manifest"]["diagnostic"], serialized)

    def test_secret_shaped_mapping_key_is_detected_and_redacted(self):
        document = fixture(1)
        secret_key = "sk-SYNTHETIC123456789"
        document["record"]["identifiers"] = {secret_key: "synthetic"}
        result = evaluate_cross_control_scenario(document)
        self.assertEqual(result["outcome"], "quarantine")
        self.assertNotIn(secret_key, json.dumps(result))
        self.assertTrue(
            any(
                "<redacted-key>" in finding and finding.endswith(":secret-shaped")
                for finding in result["findings"]
            )
        )

    def test_malformed_root_fails_safely(self):
        result = evaluate_cross_control_scenario([])  # type: ignore[arg-type]
        self.assertEqual(result["outcome"], "reject")

    def test_cycle_fails_safely_without_mutation(self):
        document = fixture(1)
        document["record"]["cycle"] = document["record"]
        result = evaluate_cross_control_scenario(document)
        self.assertEqual(result["outcome"], "reject")
        self.assertEqual(result["findings"], ["malformed:cyclic-container"])
        self.assertIs(document["record"]["cycle"], document["record"])

    def test_shared_container_fails_closed_deterministically(self):
        document = fixture(1)
        shared = {"state": "evidence-only"}
        document["record"]["left"] = shared
        document["record"]["right"] = shared
        first = evaluate_cross_control_scenario(document)
        second = evaluate_cross_control_scenario(document)
        self.assertEqual(first, second)
        self.assertEqual(first["outcome"], "reject")
        self.assertEqual(first["findings"], ["malformed:shared-container"])

    def test_cycle_outside_record_fails_closed_without_omitting_branch(self):
        document = fixture(1)
        document["review_metadata"] = document
        result = evaluate_cross_control_scenario(document)
        self.assertEqual(result["outcome"], "reject")
        self.assertEqual(result["findings"], ["malformed:cyclic-container"])

    def test_shared_container_across_top_level_branches_fails_closed(self):
        document = fixture(1)
        shared = {"state": "synthetic"}
        document["review_metadata"] = shared
        document["provenance_metadata"] = shared
        result = evaluate_cross_control_scenario(document)
        self.assertEqual(result["outcome"], "reject")
        self.assertEqual(result["findings"], ["malformed:shared-container"])

    def test_deep_input_fails_safely(self):
        document = fixture(1)
        cursor = document["record"]
        for _ in range(80):
            cursor["nested"] = {}
            cursor = cursor["nested"]
        result = evaluate_cross_control_scenario(document)
        self.assertEqual(result["outcome"], "reject")
        self.assertIn("malformed:nesting-limit", result["findings"])

    def test_container_limit_fails_closed(self):
        document = fixture(1)
        document["record"]["first"] = {}
        document["record"]["second"] = {}
        with mock.patch.object(track_d_module, "MAX_CONTAINERS", 2):
            result = evaluate_cross_control_scenario(document)
        self.assertEqual(result["outcome"], "reject")
        self.assertIn("malformed:container-limit", result["findings"])

    def test_hostile_mapping_fails_closed(self):
        document = fixture(1)
        document["record"] = HostileMapping()
        result = evaluate_cross_control_scenario(document)
        self.assertEqual(result["outcome"], "reject")
        self.assertEqual(result["findings"], ["malformed:hostile-mapping"])

    def test_malformed_mapping_items_fail_closed(self):
        result = evaluate_cross_control_scenario(MalformedItemsMapping())
        self.assertEqual(result["outcome"], "reject")
        self.assertEqual(result["findings"], ["malformed:hostile-mapping"])


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
    def test_fixture_02_confidential_prompt_is_detected_without_neighboring_secret(self):
        document = fixture(2)
        result = assert_outcome(self, 2, "quarantine")
        self.assertTrue(any(finding.endswith(":confidential-prompt") for finding in result["findings"]))
        self.assertNotIn("api_key", json.dumps(document))
        material = document["record"]["nested"]["prompt_specimen"]["content"]
        content_only = adapt_sensitive_record_to_public_output_gate({"payload": material})
        self.assertIn("sensitive:payload:confidential-prompt", content_only["findings"])

    def test_fixture_17(self): assert_outcome(self, 17, "quarantine")
    def test_nested_evidence_reference_is_inspected(self):
        document = fixture(1); document["record"]["evidence_references"] = [{"value": "Bearer SYNTHETIC123456"}]
        self.assertEqual(evaluate_cross_control_scenario(document)["outcome"], "quarantine")
    def test_schema_validity_does_not_exempt_sensitive_scan(self):
        document = fixture(1); document["record"]["verified_status"] = {"private_key": "synthetic"}
        self.assertEqual(evaluate_cross_control_scenario(document)["outcome"], "quarantine")

    def test_all_required_sensitive_categories_route_to_existing_m14_gate(self):
        cases = {
            "confidential-prompt": {"confidential_prompt_material": "synthetic"},
            "hidden-reasoning-trace": {"hidden_reasoning_trace": "synthetic"},
            "personal-identifier": {"personal_identifier": "synthetic-person"},
            "medical-identifier": {"patient_medical_identifier": "synthetic-patient"},
            "financial-identifier": {"brokerage_financial_identifier": "synthetic-account"},
            "private-evaluation": {"private_evaluation_content": "synthetic"},
            "provider-managed-memory": {"provider_managed_memory": "synthetic"},
            "production-account": {"production_account_information": "synthetic"},
            "internal-path": {"internal_private_file_path": "synthetic/path"},
            "private-configuration": {"private_configuration_excerpt": "synthetic"},
            "cross-repository-private-summary": {"cross_repo_private_summary": "synthetic"},
            "secret-shaped": {"diagnostic": "sk-SYNTHETIC123456789"},
        }
        for expected_category, record in cases.items():
            with self.subTest(category=expected_category):
                source_result, case_result = public_output_source_result(record)
                self.assertTrue(source_result["public_issue_exfiltration_gate_valid"])
                self.assertTrue(case_result["public_output_blocked"])
                self.assertTrue(case_result["redaction_required"])
                serialized = json.dumps(source_result)
                for value in record.values():
                    self.assertNotIn(str(value), serialized)


class ProvenanceHumanReviewTests(unittest.TestCase):
    def test_fixture_03(self): assert_outcome(self, 3, "reject")
    def test_fixture_15(self): assert_outcome(self, 15, "reject")
    def test_fixture_16(self): assert_outcome(self, 16, "reject")
    def test_schema_validation_cannot_authorize_merge(self):
        document = fixture(1); document["record"]["claim"] = "schema validation authorizes merge approval"
        self.assertEqual(evaluate_cross_control_scenario(document)["outcome"], "reject")


class SourceControlCompositionTests(unittest.TestCase):
    def test_track_a_blocked_by_existing_public_output_control(self):
        document = fixture(2)
        source_result, case_result = public_output_source_result(document["record"])
        self.assertTrue(source_result["public_issue_exfiltration_gate_valid"])
        self.assertTrue(case_result["public_output_blocked"])
        source_outputs = complete_source_control_outputs()
        source_outputs["m14-public-output-exfiltration"] = case_result
        result = evaluate_source_control_composition(document, source_outputs)
        self.assertEqual(result["outcome"], "quarantine")
        self.assertIn("source-control:m14-public-output-exfiltration:public-output-blocked", result["findings"])

    def test_provenance_success_cannot_complete_human_review(self):
        source_result = evaluate_ai_authored_pr_provenance_fixture(
            load_json(PROVENANCE_FIXTURE_PATH),
            PROVENANCE_WORKFLOW_PATH.read_text(encoding="utf-8"),
        )
        self.assertTrue(source_result["ai_pr_provenance_valid"])
        self.assertTrue(source_result["workflow_security_valid"])
        self.assertTrue(source_result["human_review_required"])
        document = fixture(1)
        document["record"]["review_metadata"] = {"human_review_completed": True}
        source_outputs = complete_source_control_outputs()
        source_outputs["m14-ai-provenance"] = json.loads(json.dumps(source_result, sort_keys=True))
        result = evaluate_source_control_composition(document, source_outputs)
        self.assertEqual(result["outcome"], "reject")
        self.assertIn("source-control:m14-ai-provenance:human-review-remains-required", result["findings"])

    def test_provenance_output_or_record_cannot_remove_human_review(self):
        source_outputs = complete_source_control_outputs()
        source_outputs["m14-ai-provenance"]["human_review_required"] = False
        document = fixture(1)
        document["record"]["review_metadata"] = {"human_review_required": False}
        result = evaluate_source_control_composition(document, source_outputs)
        self.assertEqual(result["outcome"], "reject")
        self.assertIn("source-control:m14-ai-provenance:human-review-boundary-weakened", result["findings"])
        self.assertIn("source-control:m14-ai-provenance:human-review-required-cannot-be-removed", result["findings"])

    def test_track_a_learning_proof_cannot_bypass_rejected_skill_admission(self):
        source_result = evaluate_fixture_case(
            load_json(SKILL_FIXTURE_PATH),
            "case_16_undeclared_mcp_access_blocked",
        )
        document = fixture(5)
        document["record"]["skill_admitted"] = True
        source_outputs = complete_source_control_outputs()
        source_outputs["m14-skill-admission"] = source_result
        result = evaluate_source_control_composition(document, source_outputs)
        self.assertEqual(result["outcome"], "reject")
        self.assertIn("source-control:m14-skill-admission:skill-admission-blocked", result["findings"])
        self.assertIn("source-control:m14-skill-admission:admission-cannot-be-promoted", result["findings"])

    def test_track_b_cannot_bypass_rejected_skill_admission(self):
        source_result = evaluate_fixture_case(
            load_json(SKILL_FIXTURE_PATH),
            "case_16_undeclared_mcp_access_blocked",
        )
        self.assertEqual(source_result["candidate_admission_state"], "candidate_blocked")
        document = fixture(6)
        document["record"]["package_admitted"] = True
        source_outputs = complete_source_control_outputs()
        source_outputs["m14-skill-admission"] = source_result
        result = evaluate_source_control_composition(document, source_outputs)
        self.assertEqual(result["outcome"], "reject")
        self.assertIn("source-control:m14-skill-admission:skill-admission-blocked", result["findings"])
        self.assertIn("source-control:m14-skill-admission:admission-cannot-be-promoted", result["findings"])

    def test_external_evidence_states_cannot_bypass_gate(self):
        source_fixture = load_json(EXTERNAL_EVIDENCE_FIXTURE_PATH)
        baseline = source_fixture["fixture_cases"][0]
        cases = {
            "incomplete": source_fixture["fixture_cases"][1],
            "stale": source_fixture["fixture_cases"][3],
            "altered": {**baseline, "source_digest": "synthetic-altered-digest"},
            "revoked": {**baseline, "revoked": True},
        }
        for case_name, candidate in cases.items():
            with self.subTest(case=case_name):
                source_result = evaluate_external_evidence_admission(
                    copy.deepcopy(candidate), trusted_policy=TRUSTED_EVIDENCE_POLICY
                )
                self.assertTrue(source_result["fail_closed"])
                self.assertFalse(source_result["decision_path_eligible"])
                inert_source_result = json.loads(json.dumps(source_result, sort_keys=True))
                source_outputs = complete_source_control_outputs()
                source_outputs["external-evidence-admission"] = inert_source_result
                result = evaluate_source_control_composition(fixture(6), source_outputs)
                self.assertEqual(result["outcome"], "reject")
                self.assertIn("source-control:external-evidence-admission:external-evidence-ineligible", result["findings"])

    def test_tracks_a_b_c_cannot_aggregate_authority(self):
        track_a = evaluate_learning_proof(load_json(FIXTURE_ROOT / "m15-learning-proof-approved-evaluation-only.json"))
        track_b = evaluate_capability_memory_pack(load_json(FIXTURE_ROOT / "m15-capability-pack-valid-verified.json"))
        track_c = evaluate_lineage_rollback_portability(load_json(FIXTURE_ROOT / "m15-lineage-rollback-portability-valid-complete-dependency-graph.json"))
        source_fixture = load_json(M14_AUTHORITY_FIXTURE_PATH)
        source_fixture["m15_track_composition"] = {
            "track_a": track_a,
            "track_b": track_b,
            "track_c": track_c,
            "risk_accepted": True,
        }
        source_result = evaluate_m14_cross_control_authority_boundary(
            source_fixture, m14_source_artifacts(source_fixture)
        )
        self.assertFalse(source_result["valid"])
        self.assertTrue(source_result["authority_violation_detected"])
        source_outputs = complete_source_control_outputs()
        source_outputs["m14-cross-control-authority"] = json.loads(json.dumps(source_result, sort_keys=True))
        result = evaluate_source_control_composition(fixture(21), source_outputs)
        self.assertEqual(result["outcome"], "reject")
        self.assertIn("source-control:m14-cross-control-authority:authority-composition-blocked", result["findings"])

    def test_safe_track_outputs_remain_non_authoritative(self):
        source_fixture = load_json(M14_AUTHORITY_FIXTURE_PATH)
        source_fixture["m15_track_composition"] = {
            "track_a": evaluate_learning_proof(load_json(FIXTURE_ROOT / "m15-learning-proof-approved-evaluation-only.json")),
            "track_b": evaluate_capability_memory_pack(load_json(FIXTURE_ROOT / "m15-capability-pack-valid-verified.json")),
            "track_c": evaluate_lineage_rollback_portability(load_json(FIXTURE_ROOT / "m15-lineage-rollback-portability-valid-complete-dependency-graph.json")),
        }
        source_result = evaluate_m14_cross_control_authority_boundary(
            source_fixture, m14_source_artifacts(source_fixture)
        )
        self.assertTrue(source_result["valid"])
        self.assertFalse(source_result["authority_violation_detected"])
        self.assertIn("composition_not_authoritative", source_result["outputs"])


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

    def test_existing_authority_control_rejects_linkage_promoted_to_verification(self):
        source_fixture = load_json(M14_AUTHORITY_FIXTURE_PATH)
        source_fixture["m15_decision_proof_linkage"] = {
            "track_a_reference": "urn:aaos:decision:synthetic-01",
            "decision_proof_verified": True,
        }
        source_result = evaluate_m14_cross_control_authority_boundary(
            source_fixture, m14_source_artifacts(source_fixture)
        )
        self.assertFalse(source_result["valid"])
        self.assertTrue(source_result["authority_violation_detected"])
        self.assertIn("authority_violation_detected", source_result["outputs"])
        source_outputs = complete_source_control_outputs()
        source_outputs["m14-cross-control-authority"] = json.loads(
            json.dumps(source_result, sort_keys=True)
        )
        result = evaluate_source_control_composition(fixture(19), source_outputs)
        self.assertEqual(result["outcome"], "reject")
        self.assertIn(
            "source-control:m14-cross-control-authority:authority-composition-blocked",
            result["findings"],
        )


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
