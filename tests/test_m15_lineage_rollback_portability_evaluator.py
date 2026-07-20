"""Deterministic tests for the M15 Track C lineage and portability evaluator."""

from __future__ import annotations

import ast
import builtins
import copy
import importlib
import json
import re
import socket
import subprocess
import unittest
from collections.abc import Mapping
from pathlib import Path
from unittest import mock

import runtime.m15_lineage_rollback_portability_evaluator as evaluator_module


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "m15-lineage-rollback-portability.schema.json"
EVALUATOR_PATH = ROOT / "runtime" / "m15_lineage_rollback_portability_evaluator.py"
CONTRACT_PATH = ROOT / "docs" / "learning-governance" / "m15-lineage-rollback-portability-contract.md"
README_PATH = ROOT / "README.md"
TRACK_A_SCHEMA_PATH = ROOT / "schemas" / "m15-learning-proof.schema.json"
TRACK_A_FIXTURE_PATH = ROOT / "examples" / "public-integration-pack-pilot" / "m15-learning-proof-approved-evaluation-only.json"
TRACK_B_SCHEMA_PATH = ROOT / "schemas" / "m15-capability-memory-pack.schema.json"
TRACK_B_FIXTURE_PATH = ROOT / "examples" / "public-integration-pack-pilot" / "m15-capability-pack-valid-verified.json"

FIXTURE_ROOT = ROOT / "examples" / "public-integration-pack-pilot"
FIXTURE_PATHS = {
    "complete_graph": FIXTURE_ROOT / "m15-lineage-rollback-portability-valid-complete-dependency-graph.json",
    "missing_downstream": FIXTURE_ROOT / "m15-lineage-rollback-portability-missing-downstream-dependency-declaration.json",
    "superseded": FIXTURE_ROOT / "m15-lineage-rollback-portability-superseded-learning-artifact-known-dependents.json",
    "revoked": FIXTURE_ROOT / "m15-lineage-rollback-portability-revoked-capability-pack-unresolved-downstream-use.json",
    "rollback_ready": FIXTURE_ROOT / "m15-lineage-rollback-portability-rollback-ready-complete-dependency-evidence.json",
    "rollback_blocked": FIXTURE_ROOT / "m15-lineage-rollback-portability-rollback-blocked-incompatible-dependent.json",
    "deletion_pending": FIXTURE_ROOT / "m15-lineage-rollback-portability-deletion-pending-unresolved-copies.json",
    "qualified_deleted": FIXTURE_ROOT / "m15-lineage-rollback-portability-qualified-deleted-no-physical-erasure.json",
    "false_erasure": FIXTURE_ROOT / "m15-lineage-rollback-portability-false-physical-provider-erasure-claim.json",
    "portability_success": FIXTURE_ROOT / "m15-lineage-rollback-portability-model-removal-drill-success.json",
    "portability_blocked": FIXTURE_ROOT / "m15-lineage-rollback-portability-model-removal-drill-provider-specific-blocker.json",
    "replacement_authorized": FIXTURE_ROOT / "m15-lineage-rollback-portability-replacement-model-use-incorrectly-authorized.json",
    "learning_authority": FIXTURE_ROOT / "m15-lineage-rollback-portability-learning-proof-rollback-authority.json",
    "decision_authority": FIXTURE_ROOT / "m15-lineage-rollback-portability-decision-proof-deletion-execution-authority.json",
}

EXPECTED_RESULT_KEYS = {
    "valid",
    "schema_valid",
    "record_identity_valid",
    "dependency_graph_valid",
    "dependency_graph_complete",
    "lineage_valid",
    "rollback_evidence_valid",
    "rollback_ready",
    "rollback_readiness",
    "deletion_evidence_valid",
    "deletion_complete_qualified",
    "deletion_status",
    "portability_evidence_valid",
    "portable_in_simulation",
    "portability_state",
    "cross_track_linkage_valid",
    "learning_proof_linkage_valid",
    "capability_memory_pack_linkage_valid",
    "decision_proof_linkage_valid",
    "sensitive_material_absent",
    "authority_boundary_valid",
    "evidence_disposition",
    "findings",
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _schema_type_matches(value, expected_type):
    if expected_type == "object":
        return isinstance(value, Mapping)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "null":
        return value is None
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    raise AssertionError(f"unsupported schema type: {expected_type}")


def _resolve_local_reference(root_schema, reference):
    if not reference.startswith("#/"):
        raise AssertionError(f"unsupported non-local schema reference: {reference}")
    value = root_schema
    for raw_token in reference[2:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        value = value[token]
    return value


def _unique_items(items):
    encoded = [json.dumps(item, sort_keys=True, separators=(",", ":")) for item in items]
    return len(encoded) == len(set(encoded))


def validate_schema_subset(instance, schema, *, root_schema=None, path="$", quiet=False):
    """Validate the draft-2020-12 subset used by the checked-in Track C schema."""

    root_schema = schema if root_schema is None else root_schema
    errors = []

    def add(label):
        errors.append(f"{path}:{label}")

    if "$ref" in schema:
        return validate_schema_subset(
            instance,
            _resolve_local_reference(root_schema, schema["$ref"]),
            root_schema=root_schema,
            path=path,
            quiet=quiet,
        )
    for nested_schema in schema.get("allOf", []):
        errors.extend(
            validate_schema_subset(
                instance,
                nested_schema,
                root_schema=root_schema,
                path=path,
                quiet=quiet,
            )
        )
    if "anyOf" in schema:
        matches = [
            not validate_schema_subset(
                instance,
                branch,
                root_schema=root_schema,
                path=path,
                quiet=True,
            )
            for branch in schema["anyOf"]
        ]
        if not any(matches):
            add("anyOf")
    if "oneOf" in schema:
        matches = sum(
            not validate_schema_subset(
                instance,
                branch,
                root_schema=root_schema,
                path=path,
                quiet=True,
            )
            for branch in schema["oneOf"]
        )
        if matches != 1:
            add("oneOf")
    if "not" in schema and not validate_schema_subset(
        instance,
        schema["not"],
        root_schema=root_schema,
        path=path,
        quiet=True,
    ):
        add("not")
    if "if" in schema:
        condition_matches = not validate_schema_subset(
            instance,
            schema["if"],
            root_schema=root_schema,
            path=path,
            quiet=True,
        )
        selected = schema.get("then") if condition_matches else schema.get("else")
        if selected is not None:
            errors.extend(
                validate_schema_subset(
                    instance,
                    selected,
                    root_schema=root_schema,
                    path=path,
                    quiet=quiet,
                )
            )

    expected_types = schema.get("type")
    if expected_types is not None:
        if isinstance(expected_types, str):
            expected_types = [expected_types]
        if not any(_schema_type_matches(instance, item) for item in expected_types):
            add("type")
            return errors
    if "const" in schema and instance != schema["const"]:
        add("const")
    if "enum" in schema and instance not in schema["enum"]:
        add("enum")

    if isinstance(instance, Mapping):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}.{key}:required")
        properties = schema.get("properties", {})
        for key, value in instance.items():
            child_path = f"{path}.{key}"
            if key in properties:
                errors.extend(
                    validate_schema_subset(
                        value,
                        properties[key],
                        root_schema=root_schema,
                        path=child_path,
                        quiet=quiet,
                    )
                )
            elif schema.get("additionalProperties") is False:
                errors.append(f"{child_path}:additionalProperties")
            elif isinstance(schema.get("additionalProperties"), Mapping):
                errors.extend(
                    validate_schema_subset(
                        value,
                        schema["additionalProperties"],
                        root_schema=root_schema,
                        path=child_path,
                        quiet=quiet,
                    )
                )
    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            add("minItems")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            add("maxItems")
        if schema.get("uniqueItems") and not _unique_items(instance):
            add("uniqueItems")
        item_schema = schema.get("items")
        if isinstance(item_schema, Mapping):
            for index, item in enumerate(instance):
                errors.extend(
                    validate_schema_subset(
                        item,
                        item_schema,
                        root_schema=root_schema,
                        path=f"{path}[{index}]",
                        quiet=quiet,
                    )
                )
    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            add("minLength")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            add("maxLength")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            add("pattern")
    return errors


class TrackCFixtureMixin:
    @classmethod
    def setUpClass(cls):
        cls.schema = load_json(SCHEMA_PATH)
        cls.fixtures = {name: load_json(path) for name, path in FIXTURE_PATHS.items()}

    def fixture(self, name="complete_graph"):
        return copy.deepcopy(self.fixtures[name])

    def evaluate(self, artifact):
        return evaluator_module.evaluate_lineage_rollback_portability(artifact)

    def mutated(self, mutator, *, fixture="complete_graph"):
        baseline = self.fixture(fixture)
        artifact = copy.deepcopy(baseline)
        mutator(artifact)
        self.assertNotEqual(artifact, baseline, "regression mutation must not be a no-op")
        return artifact

    def assert_valid(self, result):
        self.assertTrue(result["valid"], result["findings"])
        self.assertEqual(result["findings"], sorted(set(result["findings"])))

    def assert_invalid(self, result, finding=None):
        self.assertFalse(result["valid"], result["findings"])
        if finding is not None:
            self.assertIn(finding, result["findings"])
        self.assertEqual(result["findings"], sorted(set(result["findings"])))

    def assert_authority_rejected(self, field):
        artifact = self.mutated(
            lambda value: value["authority_claims"].__setitem__(field, True)
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result, f"authority_claim_must_be_false:{field}")
        self.assertFalse(result["authority_boundary_valid"])


class M15LineageRollbackPortabilityEvaluatorTests(TrackCFixtureMixin, unittest.TestCase):
    def test_01_schema_and_all_public_fixtures_are_structurally_valid(self):
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIs(self.schema["additionalProperties"], False)
        self.assertEqual(len(self.fixtures), 14)
        for name, artifact in self.fixtures.items():
            with self.subTest(name=name):
                self.assertEqual(validate_schema_subset(artifact, self.schema), [])
                self.assertTrue(self.evaluate(artifact)["schema_valid"])

    def test_02_schema_and_runtime_closed_vocabulary_match(self):
        properties = self.schema["properties"]
        self.assertEqual(properties["schema_version"]["const"], evaluator_module.SCHEMA_VERSION)
        self.assertEqual(properties["record_kind"]["enum"], list(evaluator_module.RECORD_KINDS))
        self.assertEqual(
            self.schema["$defs"]["graphArtifact"]["properties"]["artifact_type"]["enum"],
            list(evaluator_module.ARTIFACT_TYPES),
        )
        self.assertEqual(
            set(
                self.schema["$defs"]["rollbackEvidence"]["properties"][
                    "reason_codes"
                ]["items"]["enum"]
            ),
            set(evaluator_module.ROLLBACK_REASON_CODES),
        )
        self.assertEqual(
            set(
                self.schema["$defs"]["deletionEvidence"]["properties"][
                    "reason_codes"
                ]["items"]["enum"]
            ),
            set(evaluator_module.DELETION_REASON_CODES),
        )
        self.assertEqual(
            set(
                self.schema["$defs"]["portabilityDrill"]["properties"][
                    "reason_codes"
                ]["items"]["enum"]
            ),
            set(evaluator_module.PORTABILITY_REASON_CODES),
        )
        self.assertEqual(self.schema["$defs"]["digest"]["pattern"], "^[0-9a-f]{64}$")

    def test_03_result_contract_is_exact_and_typed(self):
        result = self.evaluate(self.fixture())
        self.assertEqual(set(result), EXPECTED_RESULT_KEYS)
        for key in EXPECTED_RESULT_KEYS - {
            "rollback_readiness",
            "deletion_status",
            "portability_state",
            "evidence_disposition",
            "findings",
        }:
            self.assertIs(type(result[key]), bool, key)
        for key in ("rollback_readiness", "deletion_status", "portability_state", "evidence_disposition"):
            self.assertIsInstance(result[key], str)
        self.assertIsInstance(result["findings"], list)

    def test_04_valid_complete_dependency_graph_is_complete_evidence(self):
        result = self.evaluate(self.fixture())
        self.assert_valid(result)
        self.assertTrue(result["dependency_graph_valid"])
        self.assertTrue(result["dependency_graph_complete"])
        self.assertEqual(result["evidence_disposition"], "complete-dependency-evidence")

    def test_05_missing_downstream_declaration_fails_closed(self):
        result = self.evaluate(self.fixture("missing_downstream"))
        self.assert_invalid(result)
        self.assertFalse(result["dependency_graph_valid"])
        self.assertTrue(any("inconsistent_" in item for item in result["findings"]))

    def test_06_superseded_learning_artifact_preserves_known_dependents(self):
        result = self.evaluate(self.fixture("superseded"))
        self.assert_valid(result)
        self.assertTrue(result["lineage_valid"])
        self.assertEqual(result["evidence_disposition"], "lineage-evidence")

    def test_07_revoked_capability_pack_keeps_unresolved_use_visible(self):
        result = self.evaluate(self.fixture("revoked"))
        self.assert_valid(result)
        self.assertTrue(result["lineage_valid"])
        self.assertFalse(result["dependency_graph_complete"])
        self.assertIn("unresolved_lineage_dependents_present", result["findings"])

    def test_08_rollback_ready_fixture_assesses_readiness_only(self):
        artifact = self.fixture("rollback_ready")
        result = self.evaluate(artifact)
        self.assert_valid(result)
        self.assertTrue(result["rollback_ready"])
        self.assertEqual(result["rollback_readiness"], "ready-for-human-review")
        self.assertIsNone(artifact["rollback_evidence"]["authorization_reference"])
        self.assertEqual(artifact["rollback_evidence"]["execution_state"], "not-executed")

    def test_09_incompatible_dependent_blocks_rollback_without_invalidating_evidence(self):
        result = self.evaluate(self.fixture("rollback_blocked"))
        self.assert_valid(result)
        self.assertFalse(result["rollback_ready"])
        self.assertEqual(result["rollback_readiness"], "blocked")
        self.assertIn("rollback_incompatible_dependents_present", result["findings"])

    def test_10_deletion_pending_preserves_unresolved_copies(self):
        result = self.evaluate(self.fixture("deletion_pending"))
        self.assert_valid(result)
        self.assertTrue(result["deletion_evidence_valid"])
        self.assertEqual(result["deletion_status"], "pending")
        self.assertIn("deletion_unresolved_dependencies_present", result["findings"])

    def test_11_qualified_deleted_fixture_makes_no_physical_erasure_claim(self):
        artifact = self.fixture("qualified_deleted")
        result = self.evaluate(artifact)
        self.assert_valid(result)
        self.assertTrue(result["deletion_complete_qualified"])
        claim_fields = [key for key in artifact["deletion_evidence"] if key.endswith("_claimed")]
        self.assertTrue(all(artifact["deletion_evidence"][key] is False for key in claim_fields))

    def test_12_false_physical_or_provider_erasure_claim_fails_closed(self):
        result = self.evaluate(self.fixture("false_erasure"))
        self.assert_invalid(result)
        self.assertFalse(result["deletion_evidence_valid"])
        self.assertIn(
            "qualified_independent_evidence_missing:physical_erasure_claimed",
            result["findings"],
        )
        self.assertIn(
            "qualified_independent_evidence_missing:provider_deletion_claimed",
            result["findings"],
        )

    def test_13_successful_model_removal_drill_is_simulation_only(self):
        artifact = self.fixture("portability_success")
        result = self.evaluate(artifact)
        self.assert_valid(result)
        self.assertTrue(result["portable_in_simulation"])
        self.assertEqual(result["portability_state"], "portable-in-simulation")
        self.assertTrue(artifact["portability_drill"]["simulation_only"])

    def test_14_provider_specific_dependency_blocks_portability(self):
        result = self.evaluate(self.fixture("portability_blocked"))
        self.assert_valid(result)
        self.assertFalse(result["portable_in_simulation"])
        self.assertEqual(result["portability_state"], "blocked")
        self.assertIn("portability_blockers_present", result["findings"])

    def test_15_replacement_model_authorization_fixture_fails_closed(self):
        result = self.evaluate(self.fixture("replacement_authorized"))
        self.assert_invalid(result)
        self.assertFalse(result["portability_evidence_valid"])
        self.assertFalse(result["authority_boundary_valid"])
        self.assertIn(
            "simulation_action_or_authority_forbidden:replacement_model_authorized",
            result["findings"],
        )

    def test_16_missing_track_c_identifier_fails_closed(self):
        artifact = self.mutated(lambda value: value.pop("track_c_record_id"))
        self.assert_invalid(self.evaluate(artifact))

    def test_17_malformed_graph_identifier_fails_closed(self):
        artifact = self.mutated(lambda value: value["dependency_graph"].__setitem__("graph_id", "graph-001"))
        self.assert_invalid(self.evaluate(artifact), "invalid_identifier:dependency_graph.graph_id")

    def test_18_malformed_artifact_version_fails_closed(self):
        artifact = self.mutated(lambda value: value["dependency_graph"]["artifacts"][0].__setitem__("artifact_version", " version with spaces "))
        self.assert_invalid(self.evaluate(artifact))

    def test_19_malformed_digest_fails_closed(self):
        artifact = self.mutated(lambda value: value["dependency_graph"].__setitem__("graph_integrity_digest", "sha256:abc"))
        self.assert_invalid(self.evaluate(artifact), "invalid_digest:dependency_graph.graph_integrity_digest")

    def test_20_unknown_artifact_type_fails_closed(self):
        artifact = self.mutated(lambda value: value["dependency_graph"]["artifacts"][0].__setitem__("artifact_type", "executable-tool"))
        self.assert_invalid(self.evaluate(artifact))

    def test_21_duplicate_artifact_identifier_fails_closed(self):
        artifact = self.mutated(lambda value: value["dependency_graph"]["artifacts"].append(copy.deepcopy(value["dependency_graph"]["artifacts"][0])))
        self.assert_invalid(self.evaluate(artifact))

    def test_22_inconsistent_dependency_digest_fails_closed(self):
        artifact = self.mutated(lambda value: value["dependency_graph"]["artifacts"][0]["downstream_dependents"][0].__setitem__("artifact_digest", "9999999999999999999999999999999999999999999999999999999999999999"))
        self.assert_invalid(self.evaluate(artifact))

    def test_23_incomplete_graph_requires_an_unresolved_declaration(self):
        artifact = self.mutated(lambda value: (value["dependency_graph"].__setitem__("completeness_declared", False), value["dependency_graph"].__setitem__("completeness_evidence_reference", None)))
        self.assert_invalid(self.evaluate(artifact), "incomplete_graph_requires_unresolved_dependency")

    def test_24_complete_graph_requires_completeness_evidence(self):
        artifact = self.mutated(lambda value: value["dependency_graph"].__setitem__("completeness_evidence_reference", None))
        self.assert_invalid(self.evaluate(artifact), "false_dependency_graph_completeness:evidence_missing")

    def test_25_complete_graph_cannot_contain_unresolved_dependencies(self):
        artifact = self.mutated(lambda value: value["dependency_graph"]["unresolved_dependencies"].append({"source_artifact_id": value["dependency_graph"]["artifacts"][0]["artifact_id"], "related_artifact_id": "urn:aaos:m15:artifact:synthetic:unresolved-001", "direction": "downstream", "reason_code": "unresolved-use"}))
        self.assert_invalid(self.evaluate(artifact), "false_dependency_graph_completeness:unresolved_dependencies_present")

    def test_26_supersession_requires_replacement_reference(self):
        artifact = self.mutated(lambda value: value["lineage_evidence"].__setitem__("replacement_reference", None), fixture="superseded")
        self.assert_invalid(self.evaluate(artifact), "supersession_replacement_reference_missing")

    def test_27_revocation_requires_evidence_reference(self):
        artifact = self.mutated(lambda value: value["lineage_evidence"].__setitem__("revocation_evidence_reference", None), fixture="revoked")
        self.assert_invalid(self.evaluate(artifact), "revocation_evidence_reference_missing")

    def test_28_revocation_requires_reason(self):
        artifact = self.mutated(lambda value: value["lineage_evidence"].__setitem__("reason", ""), fixture="revoked")
        self.assert_invalid(self.evaluate(artifact))

    def test_29_known_downstream_dependent_cannot_be_omitted(self):
        artifact = self.mutated(lambda value: value["lineage_evidence"]["known_downstream_dependents"].pop(), fixture="superseded")
        self.assert_invalid(self.evaluate(artifact), "known_downstream_dependents_do_not_match_graph")

    def test_30_lineage_does_not_claim_downstream_removal(self):
        artifact = self.mutated(lambda value: value["lineage_evidence"].__setitem__("downstream_removal_claimed", True), fixture="superseded")
        self.assert_invalid(self.evaluate(artifact), "lineage_cannot_claim_downstream_removal")

    def test_31_ready_rollback_cannot_hide_incompatible_dependent(self):
        artifact = self.fixture("rollback_ready")
        artifact["rollback_evidence"]["incompatible_dependents"] = [copy.deepcopy(artifact["rollback_evidence"]["affected_dependents"][0])]
        self.assert_invalid(self.evaluate(artifact), "rollback_readiness_with_incompatible_dependents")

    def test_32_ready_rollback_cannot_hide_unresolved_dependent(self):
        artifact = self.fixture("rollback_ready")
        artifact["rollback_evidence"]["unresolved_dependents"] = [copy.deepcopy(artifact["rollback_evidence"]["affected_dependents"][0])]
        self.assert_invalid(self.evaluate(artifact), "rollback_readiness_with_unresolved_dependents")

    def test_33_ready_rollback_requires_complete_dependency_evidence(self):
        artifact = self.fixture("rollback_ready")
        artifact["dependency_graph"]["completeness_declared"] = False
        artifact["dependency_graph"]["completeness_evidence_reference"] = None
        artifact["dependency_graph"]["unresolved_dependencies"] = [{"source_artifact_id": artifact["dependency_graph"]["artifacts"][0]["artifact_id"], "related_artifact_id": "urn:aaos:m15:artifact:synthetic:unknown-use", "direction": "downstream", "reason_code": "unresolved-use"}]
        self.assert_invalid(self.evaluate(artifact), "rollback_readiness_without_complete_dependency_evidence")

    def test_34_rollback_execution_claim_requires_execution_evidence(self):
        artifact = self.mutated(lambda value: value["rollback_evidence"].__setitem__("execution_state", "execution-claimed"), fixture="rollback_ready")
        self.assert_invalid(self.evaluate(artifact), "rollback_execution_claim_without_execution_evidence")

    def test_35_rollback_completion_requires_execution_evidence(self):
        artifact = self.mutated(lambda value: value["rollback_evidence"].__setitem__("completion_claim", True), fixture="rollback_ready")
        self.assert_invalid(self.evaluate(artifact), "rollback_completion_claim_without_execution_evidence")

    def test_36_deletion_completion_cannot_hide_unresolved_copy(self):
        artifact = self.fixture("qualified_deleted")
        artifact["deletion_evidence"]["known_copies"][0]["evidence_state"] = "deletion-pending"
        self.assert_invalid(self.evaluate(artifact), "deletion_completion_claim_with_unresolved_copies_or_dependents")

    def test_37_physical_erasure_claim_can_only_use_independently_verified_evidence(self):
        artifact = self.fixture("qualified_deleted")
        artifact["deletion_evidence"]["physical_erasure_claimed"] = True
        artifact["deletion_evidence"]["independent_deletion_evidence"].append({"evidence_type": "physical-erasure", "evidence_reference": "urn:aaos:m15:deletion-evidence:synthetic:physical-erasure-001", "evidence_digest": "7777777777777777777777777777777777777777777777777777777777777777", "qualification": "independently-verified"})
        artifact["deletion_evidence"]["reason_codes"].remove(
            "physical-erasure-not-proven"
        )
        self.assert_valid(self.evaluate(artifact))

    def test_38_provider_deletion_claim_can_only_use_independently_verified_evidence(self):
        artifact = self.fixture("qualified_deleted")
        artifact["deletion_evidence"]["provider_deletion_claimed"] = True
        artifact["deletion_evidence"]["deletion_scope"].append("provider-copy")
        artifact["deletion_evidence"]["evidence_qualification"] = (
            "qualified-external-deletion"
        )
        artifact["deletion_evidence"]["independent_deletion_evidence"].append({"evidence_type": "provider-deletion", "evidence_reference": "urn:aaos:m15:deletion-evidence:synthetic:provider-erasure-001", "evidence_digest": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "qualification": "independently-verified"})
        artifact["deletion_evidence"]["reason_codes"].remove(
            "provider-deletion-not-proven"
        )
        self.assert_valid(self.evaluate(artifact))

    def test_39_portable_state_cannot_hide_blocker(self):
        artifact = self.fixture("portability_blocked")
        artifact["portability_drill"]["portability_state"] = "portable-in-simulation"
        self.assert_invalid(self.evaluate(artifact), "portability_claimed_with_provider_specific_blocker")

    def test_40_provider_specific_graph_dependency_must_be_declared_in_drill(self):
        artifact = self.fixture("portability_success")
        artifact["dependency_graph"]["artifacts"][1]["provider_specific_dependency"] = True
        self.assert_invalid(self.evaluate(artifact), "provider_specific_dependencies_not_fully_identified")

    def test_41_unknown_top_level_field_fails_closed(self):
        artifact = self.mutated(lambda value: value.__setitem__("unexpected", "synthetic"))
        self.assert_invalid(self.evaluate(artifact), "unexpected_field:unexpected")

    def test_42_malformed_timestamp_fails_closed(self):
        artifact = self.mutated(lambda value: value.__setitem__("effective_timestamp", "2026-07-16 12:00:00"))
        self.assert_invalid(self.evaluate(artifact), "invalid_timestamp:effective_timestamp")

    def test_43_evaluation_does_not_mutate_input(self):
        artifact = self.fixture("revoked")
        baseline = copy.deepcopy(artifact)
        self.evaluate(artifact)
        self.assertEqual(artifact, baseline)

    def test_44_repeated_results_and_findings_are_deterministic(self):
        for name, artifact in self.fixtures.items():
            with self.subTest(name=name):
                expected = self.evaluate(copy.deepcopy(artifact))
                for _ in range(10):
                    self.assertEqual(self.evaluate(copy.deepcopy(artifact)), expected)
                self.assertEqual(expected["findings"], sorted(set(expected["findings"])))

    def test_45_evaluator_performs_no_network_access(self):
        tree = ast.parse(EVALUATOR_PATH.read_text(encoding="utf-8"))
        imported_roots = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names} | {(node.module or "").split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertTrue(imported_roots.isdisjoint({"socket", "urllib", "http", "requests", "aiohttp"}))
        blocked = AssertionError("network access attempted")
        with mock.patch.object(socket, "socket", side_effect=blocked), mock.patch.object(socket, "create_connection", side_effect=blocked), mock.patch.object(socket, "getaddrinfo", side_effect=blocked):
            self.evaluate(self.fixture())

    def test_46_evaluator_performs_no_subprocess_or_shell_execution(self):
        tree = ast.parse(EVALUATOR_PATH.read_text(encoding="utf-8"))
        imported_roots = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names} | {(node.module or "").split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertNotIn("subprocess", imported_roots)
        blocked = AssertionError("subprocess attempted")
        with mock.patch.object(subprocess, "run", side_effect=blocked), mock.patch.object(subprocess, "Popen", side_effect=blocked), mock.patch.object(subprocess, "call", side_effect=blocked), mock.patch.object(subprocess, "check_output", side_effect=blocked):
            self.evaluate(self.fixture())

    def test_47_evaluator_performs_no_dynamic_import_or_file_access(self):
        tree = ast.parse(EVALUATOR_PATH.read_text(encoding="utf-8"))
        imported_roots = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names} | {(node.module or "").split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertTrue(imported_roots.isdisjoint({"importlib", "json", "os", "pathlib", "runpy", "subprocess"}))
        blocked = AssertionError("dynamic import or file access attempted")
        with mock.patch.object(importlib, "import_module", side_effect=blocked), mock.patch.object(builtins, "open", side_effect=blocked):
            self.evaluate(self.fixture())

    def test_48_evaluator_performs_no_file_mutation(self):
        observed = [EVALUATOR_PATH, SCHEMA_PATH, *FIXTURE_PATHS.values()]
        before = {path: path.read_bytes() for path in observed}
        blocked = AssertionError("file mutation attempted")
        with mock.patch.object(Path, "write_text", side_effect=blocked), mock.patch.object(Path, "write_bytes", side_effect=blocked), mock.patch.object(Path, "unlink", side_effect=blocked), mock.patch.object(Path, "replace", side_effect=blocked):
            self.evaluate(self.fixture())
        self.assertEqual(before, {path: path.read_bytes() for path in observed})

    def test_49_sensitive_findings_never_echo_secret_value(self):
        secret = "sk-syntheticShouldNotEcho123"
        artifact = self.mutated(lambda value: value["extensions"].__setitem__("note", secret))
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["sensitive_material_absent"])
        self.assertNotIn(secret, json.dumps(result, sort_keys=True))

    def test_50_all_public_fixtures_contain_synthetic_data_only(self):
        forbidden_patterns = (
            re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"),
            re.compile(r"\bgh[pousr]_[A-Za-z0-9]{8,}\b"),
            re.compile(r"\bAKIA[A-Z0-9]{12,}\b"),
            re.compile(r"Bearer\s+\S+", re.IGNORECASE),
            re.compile(r"-----BEGIN"),
            re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
        )
        for name, fixture in self.fixtures.items():
            with self.subTest(name=name):
                serialized = json.dumps(fixture, sort_keys=True)
                for pattern in forbidden_patterns:
                    self.assertIsNone(pattern.search(serialized), pattern.pattern)
                self.assertNotIn("production-account", serialized.casefold())
                for match in re.findall(r'"(?:[^"]*(?:_id|_reference)|reference)"\s*:\s*"([^"]+)"', serialized):
                    self.assertIn("synthetic", match.casefold(), match)

    def test_51_boundary_statement_is_exact_everywhere(self):
        statement = evaluator_module.NON_AUTHORITATIVE_BOUNDARY_STATEMENT
        self.assertEqual(self.schema["properties"]["non_authoritative_boundary_statement"]["const"], statement)
        for artifact in self.fixtures.values():
            self.assertEqual(artifact["non_authoritative_boundary_statement"], statement)

    def test_52_non_mapping_input_returns_exact_unfavorable_shape(self):
        result = self.evaluate([])
        self.assertEqual(set(result), EXPECTED_RESULT_KEYS)
        self.assertFalse(result["valid"])
        self.assertEqual(result["findings"], ["artifact_must_be_mapping"])

    def test_53_track_c_runtime_imports_no_track_a_or_track_b_evaluator(self):
        tree = ast.parse(EVALUATOR_PATH.read_text(encoding="utf-8"))
        imported_modules = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}
        self.assertNotIn("runtime.m15_learning_proof_evaluator", imported_modules)
        self.assertNotIn("runtime.m15_capability_memory_pack_evaluator", imported_modules)

    def test_54_coherent_incomplete_graph_remains_bounded_evidence(self):
        result = self.evaluate(self.fixture("revoked"))
        self.assert_valid(result)
        self.assertTrue(result["dependency_graph_valid"])
        self.assertFalse(result["dependency_graph_complete"])

    def test_55_qualified_deleted_state_is_not_universal_erasure_proof(self):
        artifact = self.fixture("qualified_deleted")
        evidence = artifact["deletion_evidence"]
        self.assertEqual(evidence["completion_status"], "qualified-deleted")
        self.assertTrue(any(item["evidence_state"] == "retained" for item in evidence["derived_artifacts"] + evidence["downstream_dependents"]))
        self.assertFalse(evidence["all_derived_artifacts_deleted_claimed"])
        self.assertFalse(evidence["all_external_systems_deleted_claimed"])

    def test_56_identifier_minimum_length_matches_schema(self):
        artifact = self.mutated(
            lambda value: value.__setitem__("track_c_record_id", "urn:aaos:a")
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result, "invalid_identifier:track_c_record_id")
        self.assertFalse(result["schema_valid"])

    def test_57_malformed_nested_mappings_fail_closed_without_exceptions(self):
        mutations = (
            lambda value: value["dependency_graph"]["artifacts"][0][
                "downstream_dependents"
            ][0].__setitem__("artifact_digest", {}),
            lambda value: value["dependency_graph"]["artifacts"][0].__setitem__(
                "artifact_id", {}
            ),
            lambda value: value["dependency_graph"]["unresolved_dependencies"].append(
                {
                    "source_artifact_id": {},
                    "related_artifact_id": "urn:aaos:m15:artifact:synthetic:malformed-001",
                    "direction": "downstream",
                    "reason_code": "unresolved-use",
                }
            ),
        )
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                artifact = self.mutated(mutate)
                result = self.evaluate(artifact)
                self.assert_invalid(result)

    def test_58_rollback_reason_codes_use_the_closed_schema_vocabulary(self):
        artifact = self.fixture("rollback_ready")
        artifact["rollback_evidence"]["reason_codes"].append(
            "synthetic-unknown-reason"
        )
        self.assert_invalid(self.evaluate(artifact))

    def test_59_deletion_reason_codes_use_the_closed_schema_vocabulary(self):
        artifact = self.fixture("qualified_deleted")
        artifact["deletion_evidence"]["reason_codes"].append(
            "synthetic-unknown-reason"
        )
        self.assert_invalid(self.evaluate(artifact))

    def test_60_portability_reason_codes_use_the_closed_schema_vocabulary(self):
        artifact = self.fixture("portability_success")
        artifact["portability_drill"]["reason_codes"].append(
            "synthetic-unknown-reason"
        )
        self.assert_invalid(self.evaluate(artifact))

    def test_61_lineage_effective_timestamp_must_match_record_timestamp(self):
        artifact = self.mutated(
            lambda value: value["lineage_evidence"].__setitem__(
                "effective_timestamp", "2026-07-16T12:11:00Z"
            ),
            fixture="superseded",
        )
        self.assert_invalid(self.evaluate(artifact))

    def test_62_supersession_replacement_must_differ_from_affected_artifact(self):
        artifact = self.fixture("superseded")
        artifact["lineage_evidence"]["replacement_reference"] = copy.deepcopy(
            artifact["lineage_evidence"]["affected_artifact"]
        )
        self.assert_invalid(self.evaluate(artifact))

    def test_63_deletion_evidence_cannot_omit_a_graph_dependent(self):
        artifact = self.fixture("qualified_deleted")
        artifact["deletion_evidence"]["downstream_dependents"].pop()
        self.assert_invalid(self.evaluate(artifact))

    def test_64_qualified_deletion_cannot_omit_graph_unresolved_dependency(self):
        artifact = self.fixture("qualified_deleted")
        graph = artifact["dependency_graph"]
        target = artifact["deletion_evidence"]["target_artifact"]
        graph["completeness_declared"] = False
        graph["completeness_evidence_reference"] = None
        graph["unresolved_dependencies"].append(
            {
                "source_artifact_id": target["artifact_id"],
                "related_artifact_id": "urn:aaos:m15:copy:synthetic:unresolved-external-copy-001",
                "direction": "downstream",
                "reason_code": "unresolved-use",
            }
        )
        self.assert_invalid(self.evaluate(artifact))

    def test_65_qualified_deletion_cannot_hide_retained_in_scope_copy(self):
        artifact = self.fixture("qualified_deleted")
        artifact["deletion_evidence"]["known_copies"][0]["evidence_state"] = (
            "retained"
        )
        self.assert_invalid(self.evaluate(artifact))

    def test_66_external_deletion_scope_requires_qualified_external_evidence(self):
        artifact = self.fixture("qualified_deleted")
        evidence = artifact["deletion_evidence"]
        evidence["deletion_scope"].append("external-system")
        evidence["evidence_qualification"] = "qualified-external-deletion"
        self.assertFalse(
            any(
                item["evidence_type"] == "external-system-deletion"
                for item in evidence["independent_deletion_evidence"]
            )
        )
        self.assert_invalid(self.evaluate(artifact))

    def test_67_rollback_evidence_cannot_omit_graph_unresolved_dependent(self):
        artifact = self.fixture("rollback_ready")
        graph = artifact["dependency_graph"]
        rollback = artifact["rollback_evidence"]
        graph["completeness_declared"] = False
        graph["completeness_evidence_reference"] = None
        graph["unresolved_dependencies"].append(
            {
                "source_artifact_id": rollback["current_artifact"]["artifact_id"],
                "related_artifact_id": "urn:aaos:m15:artifact:synthetic:unresolved-rollback-dependent-001",
                "direction": "downstream",
                "reason_code": "unresolved-use",
            }
        )
        rollback["readiness_state"] = "insufficient-evidence"
        rollback["compatibility_assessment"] = "unknown"
        rollback["reason_codes"] = [
            "dependency-evidence-incomplete",
            "unresolved-dependent",
            "human-review-required",
            "authorization-not-recorded",
            "execution-not-attempted",
        ]
        self.assertEqual(rollback["unresolved_dependents"], [])
        self.assert_invalid(self.evaluate(artifact))

    def test_68_rollback_target_must_differ_from_current_artifact(self):
        artifact = self.fixture("rollback_ready")
        artifact["rollback_evidence"]["target_artifact"] = copy.deepcopy(
            artifact["rollback_evidence"]["current_artifact"]
        )
        self.assert_invalid(self.evaluate(artifact))

    def test_69_compatible_assessment_cannot_hide_incompatible_dependent(self):
        artifact = self.fixture("rollback_blocked")
        artifact["rollback_evidence"]["compatibility_assessment"] = "compatible"
        self.assertTrue(artifact["rollback_evidence"]["incompatible_dependents"])
        self.assert_invalid(self.evaluate(artifact))

    def test_70_ready_rollback_requires_complete_dependency_reason_code(self):
        artifact = self.fixture("rollback_ready")
        artifact["rollback_evidence"]["reason_codes"].remove(
            "dependency-evidence-complete"
        )
        self.assert_invalid(self.evaluate(artifact))

    def test_71_blocked_rollback_requires_incompatible_dependent_reason_code(self):
        artifact = self.fixture("rollback_blocked")
        artifact["rollback_evidence"]["reason_codes"].remove(
            "incompatible-dependent"
        )
        self.assert_invalid(self.evaluate(artifact))

    def test_72_portable_state_requires_complete_dependency_graph(self):
        artifact = self.fixture("portability_success")
        graph = artifact["dependency_graph"]
        graph["completeness_declared"] = False
        graph["completeness_evidence_reference"] = None
        graph["unresolved_dependencies"].append(
            {
                "source_artifact_id": graph["artifacts"][0]["artifact_id"],
                "related_artifact_id": "urn:aaos:m15:artifact:synthetic:unknown-portability-use-001",
                "direction": "downstream",
                "reason_code": "unresolved-use",
            }
        )
        self.assert_invalid(self.evaluate(artifact))

    def test_73_degraded_portability_cannot_hide_provider_blockers(self):
        artifact = self.fixture("portability_blocked")
        drill = artifact["portability_drill"]
        drill["portability_state"] = "degraded"
        drill["portability_blockers_visible"] = False
        drill["portability_blockers"] = []
        self.assertTrue(
            any(
                item["status"] == "blocking"
                for item in drill["provider_specific_dependencies"]
            )
        )
        self.assert_invalid(self.evaluate(artifact))

    def test_74_residual_risk_cannot_claim_physical_or_provider_erasure(self):
        artifact = self.fixture("qualified_deleted")
        artifact["deletion_evidence"]["residual_risk_statement"] = (
            "Physical erasure proven and provider-side deletion completed."
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["authority_boundary_valid"])

    def test_75_replacement_requirements_cannot_claim_authorized_execution(self):
        artifact = self.fixture("portability_success")
        artifact["portability_drill"]["replacement_model_requirements"] = [
            "Replacement model authorized and production workflow executed."
        ]
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["authority_boundary_valid"])

    def test_76_lineage_reason_cannot_claim_downstream_artifacts_removed(self):
        artifact = self.fixture("superseded")
        artifact["lineage_evidence"]["reason"] = (
            "all-downstream-artifacts-removed"
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["authority_boundary_valid"])

    def test_77_secret_object_key_is_redacted_from_findings(self):
        secret_key = "sk-THISISASECRETVALUE"
        artifact = self.mutated(
            lambda value: value["extensions"].__setitem__(secret_key, "synthetic")
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["sensitive_material_absent"])
        self.assertNotIn(secret_key, json.dumps(result, sort_keys=True))

    def test_78_backup_deletion_claim_requires_independent_evidence(self):
        artifact = self.fixture("qualified_deleted")
        artifact["deletion_evidence"]["backup_deletion_claimed"] = True
        self.assert_invalid(
            self.evaluate(artifact),
            "qualified_independent_evidence_missing:backup_deletion_claimed",
        )

    def test_79_cache_deletion_claim_requires_independent_evidence(self):
        artifact = self.fixture("qualified_deleted")
        artifact["deletion_evidence"]["cache_deletion_claimed"] = True
        self.assert_invalid(
            self.evaluate(artifact),
            "qualified_independent_evidence_missing:cache_deletion_claimed",
        )

    def test_80_training_data_removal_claim_requires_independent_evidence(self):
        artifact = self.fixture("qualified_deleted")
        artifact["deletion_evidence"]["training_data_removal_claimed"] = True
        self.assert_invalid(
            self.evaluate(artifact),
            "qualified_independent_evidence_missing:training_data_removal_claimed",
        )

    def test_81_model_unlearning_claim_requires_independent_evidence(self):
        artifact = self.fixture("qualified_deleted")
        artifact["deletion_evidence"]["model_unlearning_claimed"] = True
        self.assert_invalid(
            self.evaluate(artifact),
            "qualified_independent_evidence_missing:model_unlearning_claimed",
        )

    def test_82_every_portability_action_field_fails_closed(self):
        forbidden_fields = (
            "replacement_model_authorized",
            "provider_disconnected",
            "original_model_invoked",
            "replacement_model_invoked",
            "live_data_migrated",
            "provider_account_accessed",
            "credentials_used",
            "provider_settings_modified",
            "confidential_information_exported",
            "production_workflow_executed",
        )
        for field in forbidden_fields:
            with self.subTest(field=field):
                artifact = self.fixture("portability_success")
                artifact["portability_drill"][field] = True
                result = self.evaluate(artifact)
                self.assert_invalid(
                    result, f"simulation_action_or_authority_forbidden:{field}"
                )
                self.assertFalse(result["authority_boundary_valid"])

    def test_83_malformed_independent_evidence_type_fails_closed(self):
        artifact = self.fixture("qualified_deleted")
        artifact["deletion_evidence"]["independent_deletion_evidence"][0][
            "evidence_type"
        ] = {}
        self.assert_invalid(self.evaluate(artifact))

    def test_84_arbitrary_secret_key_is_redacted_from_every_finding(self):
        secret_key = "api_key_ACTUALSECRETVALUE123"
        artifact = self.mutated(
            lambda value: value["authority_claims"].__setitem__(secret_key, True)
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertNotIn(secret_key, json.dumps(result, sort_keys=True))

    def test_85_degraded_portability_cannot_hide_non_provider_blocker(self):
        artifact = self.fixture("portability_success")
        drill = artifact["portability_drill"]
        drill["portability_state"] = "degraded"
        drill["portability_blockers"] = ["synthetic-offline-adapter-gap"]
        drill["portability_blockers_visible"] = False
        self.assert_invalid(self.evaluate(artifact), "portability_blockers_not_visible")

    def test_86_universal_external_deletion_claim_is_not_supported(self):
        artifact = self.fixture("qualified_deleted")
        evidence = artifact["deletion_evidence"]
        evidence["all_external_systems_deleted_claimed"] = True
        evidence["deletion_scope"].append("external-system")
        evidence["evidence_qualification"] = "qualified-external-deletion"
        evidence["independent_deletion_evidence"].append(
            {
                "evidence_type": "external-system-deletion",
                "evidence_reference": "urn:aaos:m15:deletion-evidence:synthetic:external-system-001",
                "evidence_digest": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "qualification": "independently-verified",
            }
        )
        self.assert_invalid(
            self.evaluate(artifact),
            "universal_external_system_deletion_claim_not_supported",
        )

    def test_87_rollback_target_requires_exact_graph_binding(self):
        artifact = self.fixture("rollback_ready")
        target_id = artifact["rollback_evidence"]["target_artifact"]["artifact_id"]
        artifact["dependency_graph"]["artifacts"] = [
            item
            for item in artifact["dependency_graph"]["artifacts"]
            if item["artifact_id"] != target_id
        ]
        self.assert_invalid(
            self.evaluate(artifact),
            "rollback_target_artifact_graph_binding_mismatch",
        )

    def test_88_contradictory_reason_code_extras_fail_closed(self):
        cases = (
            ("rollback_ready", "rollback_evidence", "incompatible-dependent"),
            ("qualified_deleted", "deletion_evidence", "unresolved-copy"),
            (
                "portability_success",
                "portability_drill",
                "provider-specific-dependency",
            ),
        )
        for fixture, section, reason_code in cases:
            with self.subTest(fixture=fixture, reason_code=reason_code):
                artifact = self.fixture(fixture)
                artifact[section]["reason_codes"].append(reason_code)
                self.assert_invalid(self.evaluate(artifact))

    def test_89_runtime_enforces_schema_string_bounds(self):
        cases = []
        residual = self.fixture("qualified_deleted")
        residual["deletion_evidence"]["residual_risk_statement"] = "x" * 513
        cases.append(residual)
        requirements = self.fixture("portability_success")
        requirements["portability_drill"]["replacement_model_requirements"] = [
            "x" * 257
        ]
        cases.append(requirements)
        provider = self.fixture("portability_blocked")
        provider["portability_drill"]["provider_specific_dependencies"][0][
            "replacement_requirement"
        ] = "x" * 257
        cases.append(provider)
        for index, artifact in enumerate(cases):
            with self.subTest(index=index):
                result = self.evaluate(artifact)
                self.assert_invalid(result)
                self.assertFalse(result["schema_valid"])

    def test_90_duplicate_provider_dependency_fails_closed(self):
        artifact = self.fixture("portability_blocked")
        dependencies = artifact["portability_drill"][
            "provider_specific_dependencies"
        ]
        dependencies.append(copy.deepcopy(dependencies[0]))
        self.assert_invalid(self.evaluate(artifact))

    def test_91_erasure_claim_aliases_in_residual_risk_fail_closed(self):
        for statement in (
            "Provider erasure confirmed.",
            "Physical erasure independently attested.",
        ):
            with self.subTest(statement=statement):
                artifact = self.fixture("qualified_deleted")
                artifact["deletion_evidence"]["residual_risk_statement"] = statement
                result = self.evaluate(artifact)
                self.assert_invalid(result)
                self.assertFalse(result["authority_boundary_valid"])

    def test_92_schema_and_runtime_reject_unknown_local_offset(self):
        artifact = self.fixture()
        artifact["effective_timestamp"] = "2026-07-16T12:00:00-00:00"
        self.assertTrue(validate_schema_subset(artifact, self.schema))
        result = self.evaluate(artifact)
        self.assert_invalid(result, "invalid_timestamp:effective_timestamp")
        self.assertFalse(result["schema_valid"])

    def test_93_excessive_nesting_fails_closed_without_recursion_error(self):
        artifact = self.fixture()
        nested = artifact["extensions"]
        for _ in range(evaluator_module.MAX_NESTING_DEPTH + 2):
            nested["nested"] = {}
            nested = nested["nested"]
        self.assert_invalid(
            self.evaluate(artifact),
            "maximum_nesting_depth_exceeded",
        )

    def test_94_structured_authority_status_aliases_fail_closed(self):
        cases = (
            ("provider_erasure", "status", "verified"),
            ("backup_deletion", "outcome", "succeeded"),
            ("cache_deletion", "state", "done"),
            ("training_data_removal", "status", "achieved"),
            ("model_unlearning", "status", "certified"),
            ("governance", "status", "effective"),
            ("policy", "decision", "allow"),
            ("deployment", "status", "greenlit"),
            ("release", "status", "go"),
        )
        for subject, field, value in cases:
            with self.subTest(subject=subject, field=field, value=value):
                artifact = self.fixture()
                artifact["extensions"] = {subject: {field: value}}
                result = self.evaluate(artifact)
                self.assert_invalid(result)
                self.assertFalse(result["authority_boundary_valid"])

    def test_95_deletion_retention_boundary_must_match_graph(self):
        artifact = self.fixture("qualified_deleted")
        artifact["deletion_evidence"]["retention_boundary"] = "external"
        self.assert_invalid(
            self.evaluate(artifact),
            "deletion_retention_boundary_graph_mismatch",
        )

    def test_96_standalone_evidence_cannot_have_declared_dependency(self):
        artifact = self.fixture()
        dependent = next(
            item
            for item in artifact["dependency_graph"]["artifacts"]
            if item["upstream_dependencies"]
        )
        dependent["dependency_purpose"] = "standalone-evidence"
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertTrue(
            any(
                item.startswith(
                    "standalone_evidence_artifact_has_declared_dependency:"
                )
                for item in result["findings"]
            )
        )

    def test_97_complete_deletion_graphs_inventory_known_copies(self):
        for fixture in ("deletion_pending", "qualified_deleted", "false_erasure"):
            with self.subTest(fixture=fixture):
                artifact = self.fixture(fixture)
                graph = artifact["dependency_graph"]
                graph_ids = {item["artifact_id"] for item in graph["artifacts"]}
                copy_ids = {
                    item["artifact_id"]
                    for item in artifact["deletion_evidence"]["known_copies"]
                }
                self.assertTrue(copy_ids.issubset(graph_ids))

    def test_98_deletion_evidence_categories_are_disjoint(self):
        artifact = self.fixture("qualified_deleted")
        artifact["deletion_evidence"]["downstream_dependents"].append(
            copy.deepcopy(artifact["deletion_evidence"]["known_copies"][0])
        )
        self.assert_invalid(
            self.evaluate(artifact),
            "deletion_dependent_declared_in_multiple_categories",
        )

    def test_99_qualified_deletion_claims_require_matching_scope(self):
        cases = (
            ("provider_deletion_claimed", "provider-deletion", "provider-deletion-not-proven"),
            ("backup_deletion_claimed", "backup-deletion", None),
            ("cache_deletion_claimed", "cache-deletion", None),
            ("training_data_removal_claimed", "training-data-removal", None),
            ("model_unlearning_claimed", "model-unlearning", None),
        )
        for index, (field, evidence_type, negative_reason) in enumerate(cases):
            with self.subTest(field=field):
                artifact = self.fixture("qualified_deleted")
                evidence = artifact["deletion_evidence"]
                evidence[field] = True
                evidence["independent_deletion_evidence"].append(
                    {
                        "evidence_type": evidence_type,
                        "evidence_reference": f"urn:aaos:m15:deletion-evidence:synthetic:scope-gap-{index}",
                        "evidence_digest": f"{index + 10:064x}",
                        "qualification": "independently-verified",
                    }
                )
                if negative_reason is not None:
                    evidence["reason_codes"].remove(negative_reason)
                result = self.evaluate(artifact)
                self.assert_invalid(result)
                self.assertTrue(
                    any(
                        item.startswith(f"deletion_claim_scope_missing:{field}:")
                        for item in result["findings"]
                    )
                )

    def test_100_deletion_pending_qualification_matches_evidence_state(self):
        request_only = self.fixture("qualified_deleted")
        request_only["record_kind"] = "deletion-pending"
        request_only["deletion_evidence"]["completion_status"] = "pending"
        request_only["deletion_evidence"]["evidence_qualification"] = "request-only"
        request_only["deletion_evidence"]["reason_codes"] = [
            "deletion-request-recorded",
            "local-deletion-evidence-present",
            "physical-erasure-not-proven",
            "provider-deletion-not-proven",
            "residual-risk-remains",
        ]
        self.assert_invalid(
            self.evaluate(request_only),
            "request_only_deletion_cannot_include_deletion_evidence",
        )

        pending_unresolved = self.fixture("qualified_deleted")
        pending_unresolved["record_kind"] = "deletion-pending"
        pending_unresolved["deletion_evidence"]["completion_status"] = "pending"
        pending_unresolved["deletion_evidence"]["evidence_qualification"] = (
            "pending-unresolved"
        )
        pending_unresolved["deletion_evidence"]["reason_codes"] = [
            "deletion-request-recorded",
            "local-deletion-evidence-present",
            "physical-erasure-not-proven",
            "provider-deletion-not-proven",
            "residual-risk-remains",
        ]
        self.assert_invalid(
            self.evaluate(pending_unresolved),
            "pending_unresolved_qualification_without_unresolved_evidence",
        )

    def test_101_residual_risk_statement_cannot_deny_residual_risk(self):
        for statement in ("none", "No residual risk remains."):
            with self.subTest(statement=statement):
                artifact = self.fixture("qualified_deleted")
                artifact["deletion_evidence"]["residual_risk_statement"] = statement
                self.assert_invalid(
                    self.evaluate(artifact),
                    "residual_risk_statement_denies_required_qualification",
                )

    def test_102_portability_assessments_require_graph_evidence_types(self):
        required_types = {
            "learning-proof",
            "decision-proof",
            "capability-memory-pack",
            "private-evaluation",
            "organizational-memory",
            "export-manifest",
            "lifecycle-evidence",
        }
        for fixture in (
            "portability_success",
            "portability_blocked",
            "replacement_authorized",
        ):
            with self.subTest(fixture=fixture):
                artifact = self.fixture(fixture)
                graph_types = {
                    item["artifact_type"]
                    for item in artifact["dependency_graph"]["artifacts"]
                }
                self.assertTrue(required_types.issubset(graph_types))

        artifact = self.fixture("portability_success")
        artifact["dependency_graph"]["artifacts"] = [
            item
            for item in artifact["dependency_graph"]["artifacts"]
            if item["artifact_type"] != "export-manifest"
        ]
        self.assert_invalid(
            self.evaluate(artifact),
            "portability_assessment_graph_evidence_missing:export_manifests_available:export-manifest",
        )

    def test_103_cross_track_refs_cannot_be_lifecycle_authority_or_evidence(self):
        base = self.fixture("rollback_ready")
        linkage_refs = [
            item["reference"]
            for item in base["cross_track_linkage"].values()
            if isinstance(item, dict)
        ]
        for reference in linkage_refs:
            with self.subTest(role="rollback_authorization", reference=reference):
                artifact = self.fixture("rollback_ready")
                artifact["rollback_evidence"]["authorization_reference"] = reference
                artifact["rollback_evidence"]["reason_codes"].remove(
                    "authorization-not-recorded"
                )
                result = self.evaluate(artifact)
                self.assert_invalid(result)
                self.assertFalse(result["authority_boundary_valid"])

        artifact = self.fixture("rollback_ready")
        decision_ref = artifact["cross_track_linkage"]["decision_proof"]["reference"]
        artifact["rollback_evidence"]["execution_state"] = "execution-evidence-present"
        artifact["rollback_evidence"]["execution_evidence_reference"] = decision_ref
        artifact["rollback_evidence"]["reason_codes"].remove("execution-not-attempted")
        artifact["rollback_evidence"]["reason_codes"].append(
            "execution-evidence-present"
        )
        self.assert_invalid(self.evaluate(artifact))

        artifact = self.fixture("qualified_deleted")
        learning_ref = artifact["cross_track_linkage"]["learning_proof"]["reference"]
        artifact["deletion_evidence"]["authorization_reference"] = learning_ref
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["authority_boundary_valid"])

    def test_104_lifecycle_request_authorization_and_execution_roles_are_distinct(self):
        artifact = self.fixture("rollback_ready")
        rollback = artifact["rollback_evidence"]
        rollback["authorization_reference"] = rollback["rollback_request_id"]
        rollback["reason_codes"].remove("authorization-not-recorded")
        self.assert_invalid(
            self.evaluate(artifact),
            "rollback_reference_role_conflation:authorization_reference",
        )

        artifact = self.fixture("rollback_ready")
        rollback = artifact["rollback_evidence"]
        shared = "urn:aaos:m15:rollback-evidence:synthetic:shared-role-001"
        rollback["authorization_reference"] = shared
        rollback["execution_evidence_reference"] = shared
        rollback["execution_state"] = "execution-evidence-present"
        rollback["reason_codes"].remove("authorization-not-recorded")
        rollback["reason_codes"].remove("execution-not-attempted")
        rollback["reason_codes"].append("execution-evidence-present")
        self.assert_invalid(
            self.evaluate(artifact),
            "rollback_authorization_and_execution_evidence_must_differ",
        )

        artifact = self.fixture("qualified_deleted")
        deletion = artifact["deletion_evidence"]
        deletion["authorization_reference"] = deletion["deletion_request_id"]
        self.assert_invalid(
            self.evaluate(artifact),
            "deletion_reference_role_conflation:authorization_reference",
        )

    def test_105_independent_deletion_evidence_cannot_reuse_local_receipt(self):
        artifact = self.fixture("qualified_deleted")
        deletion = artifact["deletion_evidence"]
        local = deletion["independent_deletion_evidence"][0]
        deletion["deletion_scope"].append("provider-copy")
        deletion["evidence_qualification"] = "qualified-external-deletion"
        deletion["provider_deletion_claimed"] = True
        deletion["reason_codes"].remove("provider-deletion-not-proven")
        deletion["independent_deletion_evidence"].append(
            {
                "evidence_type": "provider-deletion",
                "evidence_reference": local["evidence_reference"],
                "evidence_digest": local["evidence_digest"],
                "qualification": "independently-verified",
            }
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertIn(
            "independent_deletion_evidence_reference_reused",
            result["findings"],
        )
        self.assertIn(
            "independent_deletion_evidence_digest_reused",
            result["findings"],
        )

    def test_106_active_machine_token_authority_aliases_fail_closed(self):
        aliases = (
            "rollback-performed",
            "deletion-satisfied",
            "audit-finished",
            "authority-delegated",
            "identity-valid",
            "deployment-operational",
            "release-live",
            "policy-active",
        )
        for alias in aliases:
            with self.subTest(alias=alias):
                artifact = self.fixture("revoked")
                artifact["dependency_graph"]["unresolved_dependencies"][0][
                    "reason_code"
                ] = alias
                result = self.evaluate(artifact)
                self.assert_invalid(result)
                self.assertFalse(result["authority_boundary_valid"])

    def test_107_negative_erasure_qualification_prose_remains_non_authoritative(self):
        statements = (
            "Physical erasure is not independently verified; provider deletion is not independently verified.",
            "Physical erasure is not independently proven; provider deletion remains unverified.",
            "No physical erasure or provider deletion is verified.",
        )
        for statement in statements:
            with self.subTest(statement=statement):
                artifact = self.fixture("qualified_deleted")
                artifact["deletion_evidence"]["residual_risk_statement"] = statement
                self.assert_valid(self.evaluate(artifact))

    def test_108_residual_risk_denial_aliases_fail_closed(self):
        statements = (
            "Residual risk is zero.",
            "No risks remain.",
            "All risk was eliminated.",
            "There is no remaining residual risk.",
            "Residual risks are fully mitigated.",
            "All residual risks have been eliminated.",
            "Residual risk has been eliminated.",
            "Residual risk is nil.",
            "All residual risk is gone.",
        )
        for statement in statements:
            with self.subTest(statement=statement):
                artifact = self.fixture("qualified_deleted")
                artifact["deletion_evidence"]["residual_risk_statement"] = statement
                self.assert_invalid(
                    self.evaluate(artifact),
                    "residual_risk_statement_denies_required_qualification",
                )

    def test_109_rollback_current_and_target_artifact_types_must_match(self):
        artifact = self.fixture("rollback_ready")
        capability_pack = next(
            item
            for item in artifact["dependency_graph"]["artifacts"]
            if item["artifact_type"] == "capability-memory-pack"
        )
        artifact["rollback_evidence"]["target_artifact"] = {
            "artifact_id": capability_pack["artifact_id"],
            "artifact_version": capability_pack["artifact_version"],
            "artifact_digest": capability_pack["artifact_digest"],
        }
        self.assert_invalid(
            self.evaluate(artifact),
            "rollback_current_target_artifact_type_mismatch",
        )

    def test_110_deletion_known_copy_category_binds_to_copy_artifact_type(self):
        artifact = self.fixture("qualified_deleted")
        deletion = artifact["deletion_evidence"]
        deletion["known_copies"][0], deletion["downstream_dependents"][0] = (
            deletion["downstream_dependents"][0],
            deletion["known_copies"][0],
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result, "deletion_known_copy_artifact_type_mismatch")
        self.assertIn(
            "deletion_copy_artifact_declared_outside_known_copies",
            result["findings"],
        )

    def test_111_replacement_model_requirements_can_state_inert_compatibility(self):
        requirements = (
            "Replacement model must accept valid JSON schemas.",
            "Replacement model must consume verified export manifests.",
            "Replacement model must preserve active degraded-mode flags.",
            "Replacement model must not be invoked.",
        )
        for requirement in requirements:
            with self.subTest(requirement=requirement):
                artifact = self.fixture("portability_success")
                artifact["portability_drill"]["replacement_model_requirements"] = [
                    requirement
                ]
                self.assert_valid(self.evaluate(artifact))

    def test_112_local_deletion_evidence_can_preserve_provider_erasure_boundary(self):
        statements = (
            "Verified local deletion evidence does not establish provider erasure.",
            "Local deletion was verified; provider deletion remains unverified.",
        )
        for statement in statements:
            with self.subTest(statement=statement):
                artifact = self.fixture("qualified_deleted")
                artifact["deletion_evidence"]["residual_risk_statement"] = statement
                self.assert_valid(self.evaluate(artifact))

    def test_113_request_only_deletion_cannot_hide_unresolved_evidence(self):
        artifact = self.fixture("deletion_pending")
        artifact["deletion_evidence"]["evidence_qualification"] = "request-only"
        self.assert_invalid(
            self.evaluate(artifact),
            "request_only_deletion_cannot_hide_unresolved_evidence",
        )

    def test_114_lineage_artifact_and_evidence_reference_roles_are_distinct(self):
        artifact = self.fixture("revoked")
        lineage = artifact["lineage_evidence"]
        lineage["revocation_evidence_reference"] = lineage["affected_artifact"][
            "artifact_id"
        ]
        self.assert_invalid(
            self.evaluate(artifact),
            "lineage_evidence_reference_role_conflation:revocation_evidence_reference",
        )

        artifact = self.fixture("revoked")
        lineage = artifact["lineage_evidence"]
        lineage["archival_evidence_reference"] = lineage[
            "revocation_evidence_reference"
        ]
        self.assert_invalid(
            self.evaluate(artifact),
            "lineage_archival_and_revocation_evidence_must_differ",
        )


class M15TrackCCrossTrackLinkageTests(TrackCFixtureMixin, unittest.TestCase):
    def test_01_linkage_uses_exact_track_a_and_track_b_public_identifiers(self):
        artifact = self.fixture()
        track_a = load_json(TRACK_A_FIXTURE_PATH)
        track_b = load_json(TRACK_B_FIXTURE_PATH)
        self.assertEqual(artifact["cross_track_linkage"]["learning_proof"]["reference"], track_a["learning_proof_id"])
        self.assertEqual(artifact["cross_track_linkage"]["capability_memory_pack"]["reference"], track_b["capability_pack_id"])

    def test_02_track_a_schema_version_is_bound_exactly(self):
        self.assertEqual(load_json(TRACK_A_SCHEMA_PATH)["properties"]["schema_version"]["const"], evaluator_module.LEARNING_PROOF_SCHEMA_VERSION)

    def test_03_track_b_schema_version_is_bound_exactly(self):
        self.assertEqual(load_json(TRACK_B_SCHEMA_PATH)["properties"]["schema_version"]["const"], evaluator_module.CAPABILITY_PACK_SCHEMA_VERSION)

    def test_04_learning_proof_identifier_mismatch_fails_closed(self):
        artifact = self.mutated(lambda value: value["cross_track_linkage"]["learning_proof"].__setitem__("reference", "urn:aaos:m15:learning-proof:synthetic:mismatch"))
        self.assert_invalid(self.evaluate(artifact), "learning_proof_graph_identifier_binding_missing")

    def test_05_learning_proof_version_mismatch_fails_closed(self):
        artifact = self.mutated(lambda value: value["dependency_graph"]["artifacts"][0].__setitem__("artifact_version", "m15-learning-proof/v2"))
        self.assert_invalid(self.evaluate(artifact), "learning_proof_graph_version_binding_mismatch")

    def test_06_learning_proof_digest_mismatch_fails_closed(self):
        artifact = self.mutated(lambda value: value["cross_track_linkage"]["learning_proof"].__setitem__("track_c_evidence_record_digest", "9999999999999999999999999999999999999999999999999999999999999999"))
        self.assert_invalid(self.evaluate(artifact), "learning_proof_graph_digest_binding_mismatch")

    def test_07_capability_pack_identifier_mismatch_fails_closed(self):
        artifact = self.mutated(lambda value: value["cross_track_linkage"]["capability_memory_pack"].__setitem__("reference", "urn:aaos:capability-pack:synthetic:mismatch"))
        self.assert_invalid(self.evaluate(artifact), "capability_memory_pack_graph_identifier_binding_missing")

    def test_08_capability_pack_version_mismatch_fails_closed(self):
        artifact = self.mutated(lambda value: value["dependency_graph"]["artifacts"][1].__setitem__("artifact_version", "m15-capability-memory-pack/v2"))
        self.assert_invalid(self.evaluate(artifact), "capability_memory_pack_graph_version_binding_mismatch")

    def test_09_capability_pack_digest_mismatch_fails_closed(self):
        artifact = self.mutated(lambda value: value["cross_track_linkage"]["capability_memory_pack"].__setitem__("track_c_evidence_record_digest", "9999999999999999999999999999999999999999999999999999999999999999"))
        self.assert_invalid(self.evaluate(artifact), "capability_memory_pack_graph_digest_binding_mismatch")

    def test_10_decision_proof_identifier_mismatch_fails_closed(self):
        artifact = self.mutated(lambda value: value["cross_track_linkage"]["decision_proof"].__setitem__("reference", "urn:aaos:decision-proof:synthetic:mismatch"))
        self.assert_invalid(self.evaluate(artifact), "decision_proof_graph_identifier_binding_missing")

    def test_11_learning_source_hash_is_not_reinterpreted_as_record_digest(self):
        artifact = self.fixture()
        linkage = artifact["cross_track_linkage"]["learning_proof"]
        track_a = load_json(TRACK_A_FIXTURE_PATH)
        self.assertEqual(linkage["source_integrity_hash"], track_a["source_integrity_hash"])
        self.assertNotEqual(linkage["source_integrity_hash"], linkage["track_c_evidence_record_digest"])

    def test_12_capability_derived_manifest_digest_is_not_whole_record_digest(self):
        artifact = self.fixture()
        linkage = artifact["cross_track_linkage"]["capability_memory_pack"]
        track_b = load_json(TRACK_B_FIXTURE_PATH)
        self.assertEqual(linkage["derived_spec_manifest_digest"], track_b["derived_spec_manifest"]["manifest_digest"])
        self.assertNotEqual(linkage["derived_spec_manifest_digest"], linkage["track_c_evidence_record_digest"])

    def test_13_learning_proof_cannot_be_rollback_authority(self):
        result = self.evaluate(self.fixture("learning_authority"))
        self.assert_invalid(result, "learning_proof_linkage_treated_as_authority")
        self.assertFalse(result["learning_proof_linkage_valid"])

    def test_14_decision_proof_cannot_be_deletion_execution_authority(self):
        result = self.evaluate(self.fixture("decision_authority"))
        self.assert_invalid(result, "decision_proof_linkage_treated_as_deletion_or_execution_authority")
        self.assertFalse(result["decision_proof_linkage_valid"])

    def test_15_capability_pack_cannot_be_installation_authority(self):
        artifact = self.mutated(lambda value: value["cross_track_linkage"]["capability_memory_pack"].__setitem__("usage", "installation-authority"))
        self.assert_invalid(self.evaluate(artifact), "capability_memory_pack_treated_as_installation_or_execution_authority")

    def test_16_linkage_purpose_must_remain_evidence_only(self):
        artifact = self.mutated(lambda value: value["cross_track_linkage"].__setitem__("linkage_purpose", "authority"))
        self.assert_invalid(self.evaluate(artifact), "invalid_linkage_purpose:cross_track_linkage.linkage_purpose")

    def test_17_all_learning_proof_authority_usages_fail_closed(self):
        for usage in (
            "rollback-authority",
            "deletion-authority",
            "installation-authority",
            "execution-authority",
        ):
            with self.subTest(usage=usage):
                artifact = self.fixture()
                artifact["cross_track_linkage"]["learning_proof"]["usage"] = usage
                result = self.evaluate(artifact)
                self.assert_invalid(result, "learning_proof_linkage_treated_as_authority")
                self.assertFalse(result["learning_proof_linkage_valid"])

    def test_18_all_capability_pack_authority_usages_fail_closed(self):
        for usage in ("installation-authority", "executable-authority"):
            with self.subTest(usage=usage):
                artifact = self.fixture()
                artifact["cross_track_linkage"]["capability_memory_pack"][
                    "usage"
                ] = usage
                result = self.evaluate(artifact)
                self.assert_invalid(
                    result,
                    "capability_memory_pack_treated_as_installation_or_execution_authority",
                )
                self.assertFalse(result["capability_memory_pack_linkage_valid"])

    def test_19_all_decision_proof_authority_usages_fail_closed(self):
        for usage in ("deletion-execution-authority", "execution-authority"):
            with self.subTest(usage=usage):
                artifact = self.fixture()
                artifact["cross_track_linkage"]["decision_proof"]["usage"] = usage
                result = self.evaluate(artifact)
                self.assert_invalid(
                    result,
                    "decision_proof_linkage_treated_as_deletion_or_execution_authority",
                )
                self.assertFalse(result["decision_proof_linkage_valid"])

    def test_20_learning_source_hash_cannot_reuse_track_c_record_digest(self):
        artifact = self.fixture()
        linkage = artifact["cross_track_linkage"]["learning_proof"]
        linkage["source_integrity_hash"] = linkage["track_c_evidence_record_digest"]
        self.assert_invalid(
            self.evaluate(artifact),
            "learning_proof_digest_role_conflation",
        )

    def test_21_capability_manifest_digest_cannot_reuse_track_c_record_digest(self):
        artifact = self.fixture()
        linkage = artifact["cross_track_linkage"]["capability_memory_pack"]
        linkage["derived_spec_manifest_digest"] = linkage[
            "track_c_evidence_record_digest"
        ]
        self.assert_invalid(
            self.evaluate(artifact),
            "capability_memory_pack_digest_role_conflation",
        )


class M15TrackCAuthorityBoundaryTests(TrackCFixtureMixin, unittest.TestCase):
    def test_01_release_approval_claim_fails_closed(self): self.assert_authority_rejected("release_approved")
    def test_02_governance_authority_claim_fails_closed(self): self.assert_authority_rejected("governance_authority_granted")
    def test_03_policy_authority_claim_fails_closed(self): self.assert_authority_rejected("policy_authority_granted")
    def test_04_identity_authority_claim_fails_closed(self): self.assert_authority_rejected("identity_authority_granted")
    def test_05_risk_acceptance_claim_fails_closed(self): self.assert_authority_rejected("risk_accepted")
    def test_06_deployment_approval_claim_fails_closed(self): self.assert_authority_rejected("deployment_approved")
    def test_07_rollback_authorization_claim_fails_closed(self): self.assert_authority_rejected("rollback_authorized")
    def test_08_rollback_execution_claim_fails_closed(self): self.assert_authority_rejected("rollback_executed")
    def test_09_deletion_authorization_claim_fails_closed(self): self.assert_authority_rejected("deletion_authorized")
    def test_10_deletion_execution_claim_fails_closed(self): self.assert_authority_rejected("deletion_executed")
    def test_11_production_execution_claim_fails_closed(self): self.assert_authority_rejected("production_execution_allowed")
    def test_12_audit_closure_claim_fails_closed(self): self.assert_authority_rejected("audit_closed")
    def test_13_waiver_claim_fails_closed(self): self.assert_authority_rejected("waiver_granted")
    def test_14_authority_transfer_claim_fails_closed(self): self.assert_authority_rejected("authority_transferred")
    def test_15_capability_pack_installation_claim_fails_closed(self): self.assert_authority_rejected("capability_pack_installed")
    def test_16_capability_pack_execution_claim_fails_closed(self): self.assert_authority_rejected("capability_pack_executable")
    def test_17_learning_proof_sealing_claim_fails_closed(self): self.assert_authority_rejected("learning_proof_sealed")
    def test_18_decision_proof_sealing_claim_fails_closed(self): self.assert_authority_rejected("decision_proof_sealed")

    def test_19_unknown_nested_authority_claim_fails_closed(self):
        artifact = self.mutated(lambda value: value["authority_claims"].__setitem__("custom_control", {"status": "denied", "rollback": {"state": "executed"}}))
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["authority_boundary_valid"])

    def test_20_governance_approval_prose_in_extension_fails_closed(self):
        artifact = self.mutated(lambda value: value["extensions"].__setitem__("note", "Governance approval granted"))
        self.assert_invalid(self.evaluate(artifact), "forbidden_authority_text:extensions.note")

    def test_21_tokenized_rollback_execution_in_extension_fails_closed(self):
        artifact = self.mutated(lambda value: value["extensions"].__setitem__("state", "rollback-executed"))
        self.assert_invalid(self.evaluate(artifact))

    def test_22_compact_deletion_authorization_in_extension_fails_closed(self):
        artifact = self.mutated(lambda value: value["extensions"].__setitem__("state", "deletionauthorized"))
        self.assert_invalid(self.evaluate(artifact))

    def test_23_learning_proof_sealed_extension_claim_fails_closed(self):
        artifact = self.mutated(lambda value: value["extensions"].__setitem__("learning_proof_sealing", "sealed"))
        self.assert_invalid(self.evaluate(artifact))

    def test_24_decision_proof_sealed_extension_claim_fails_closed(self):
        artifact = self.mutated(lambda value: value["extensions"].__setitem__("decision_proof_sealing", "sealed"))
        self.assert_invalid(self.evaluate(artifact))

    def test_25_capability_pack_installed_extension_claim_fails_closed(self):
        artifact = self.mutated(lambda value: value["extensions"].__setitem__("installation_authority", "granted"))
        self.assert_invalid(self.evaluate(artifact))

    def test_26_replacement_model_authorization_fails_authority_boundary(self):
        result = self.evaluate(self.fixture("replacement_authorized"))
        self.assertFalse(result["authority_boundary_valid"])

    def test_27_negative_outer_state_cannot_hide_affirmative_claim(self):
        artifact = self.mutated(lambda value: value["extensions"].__setitem__("rollback_authorization", {"status": "denied", "authority": "granted"}))
        self.assert_invalid(self.evaluate(artifact))

    def test_28_explicit_evidence_only_authority_fields_remain_negative(self):
        artifact = self.mutated(lambda value: value["extensions"].update({"rollback_authorization": "evidence_only", "deletion_execution": False}))
        self.assert_valid(self.evaluate(artifact))

    def test_29_historical_authority_words_in_snapshot_reference_are_inert(self):
        artifact = self.mutated(lambda value: value["dependency_graph"].__setitem__("graph_snapshot_reference", "urn:aaos:m15:snapshot:synthetic:rollback-authorized-history"))
        self.assert_valid(self.evaluate(artifact))

    def test_30_all_public_fixtures_keep_fixed_authority_claims_false(self):
        expected = set(evaluator_module.FIXED_FALSE_AUTHORITY_CLAIMS)
        for name, artifact in self.fixtures.items():
            with self.subTest(name=name):
                self.assertTrue(expected.issubset(artifact["authority_claims"]))
                self.assertTrue(all(artifact["authority_claims"][field] is False for field in expected))

    def test_31_compact_and_compound_authority_keys_fail_closed(self):
        cases = (
            {"nested": {"rollbackauthorized": True}},
            {"release-authorization-granted": True},
            {"audit-closure-granted": True},
            {"waiver-issued": True},
            {"learning-proof-sealing-completed": True},
            {"decisionproofsealing": {"status": "granted"}},
            {"capabilitypackinstalled": True},
        )
        for index, extension in enumerate(cases):
            with self.subTest(index=index, extension=extension):
                artifact = self.fixture()
                artifact["extensions"] = copy.deepcopy(extension)
                result = self.evaluate(artifact)
                self.assert_invalid(result)
                self.assertFalse(result["authority_boundary_valid"])

    def test_32_strict_non_goal_actions_cannot_be_relabelled_in_extensions(self):
        cases = (
            {"tool_installed": True},
            {"tool_registered": True},
            {"skill_installed": True},
            {"generated_capability_activated": True},
            {"model_invoked": True},
            {"original_model_invoked": True},
            {"training_started": True},
            {"fine_tuning_completed": True},
            {"credentials_used": True},
            {"network_called": True},
            {"subprocess_executed": True},
            {"live_data_migrated": True},
            {"confidential_information_exported": True},
            {"live_memory_accessed": True},
        )
        for extension in cases:
            with self.subTest(extension=extension):
                artifact = self.fixture()
                artifact["extensions"] = copy.deepcopy(extension)
                result = self.evaluate(artifact)
                self.assert_invalid(result)
                self.assertFalse(result["authority_boundary_valid"])

    def test_33_graph_references_cannot_supply_lifecycle_authorization(self):
        artifact = self.fixture("rollback_ready")
        rollback = artifact["rollback_evidence"]
        rollback["authorization_reference"] = artifact["dependency_graph"][
            "graph_snapshot_reference"
        ]
        rollback["reason_codes"].remove("authorization-not-recorded")
        result = self.evaluate(artifact)
        self.assert_invalid(
            result,
            "graph_reference_reused_as_lifecycle_evidence:rollback_evidence.authorization_reference",
        )
        self.assertFalse(result["authority_boundary_valid"])

        artifact = self.fixture("qualified_deleted")
        artifact["deletion_evidence"]["authorization_reference"] = artifact[
            "dependency_graph"
        ]["graph_snapshot_reference"]
        result = self.evaluate(artifact)
        self.assert_invalid(
            result,
            "graph_reference_reused_as_lifecycle_evidence:deletion_evidence.authorization_reference",
        )
        self.assertFalse(result["authority_boundary_valid"])


class M15TrackCReleaseStateTests(TrackCFixtureMixin, unittest.TestCase):
    def assert_phase_aware_readme_state(self, readme):
        def section(heading, next_heading=None):
            start = readme.index(heading)
            if next_heading is None:
                return readme[start:]
            end = readme.index(next_heading, start + len(heading))
            return readme[start:end]

        releases = section("## Releases", "## Current Status")
        current_status = section("## Current Status", "## M5 Additions")
        next_phase = section("## Next Phase")
        normalized_next = re.sub(r"\s+", " ", next_phase).strip()

        release_lines = [
            line.strip() for line in releases.splitlines() if line.startswith("- v")
        ]
        self.assertTrue(any(line.startswith("- v0.13.0 ") for line in release_lines))
        self.assertFalse(any(line.startswith("- v0.14.0 ") for line in release_lines))
        self.assertIsNone(re.search(r"(?i)v0\.14\.0.*\b(?:released|latest)\b", releases))

        self.assertIn(
            "M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11, M12, M13, and M14 are complete.",
            current_status,
        )
        forbidden_status_patterns = (
            r"(?im)^\s*M15\s+is\s+complete[.!]?\s*$",
            r"(?im)^\s*M1\s*(?:[–-]|through)\s*M15\s+(?:are\s+)?complete[.!]?\s*$",
            r"(?im)^\s*v0\.14\.0\s+(?:is\s+)?published[.!]?\s*$",
            r"(?im)^\s*Track\s+E4\s+is\s+complete[.!]?\s*$",
            r"(?im)^\s*(?:tracker\s+)?#231\s+(?:is\s+)?closed[.!]?\s*$",
        )
        for pattern in forbidden_status_patterns:
            self.assertIsNone(re.search(pattern, current_status))

        future_promotion_patterns = (
            r"(?im)^\s*v0\.14\.0\s+is\s+released[.!]?\s*$",
            r"(?im)^\s*v0\.14\.0\s+tag\s+exists[.!]?\s*$",
            r"(?im)^\s*GitHub\s+Release\s+v0\.14\.0\s+is\s+published[.!]?\s*$",
            r"(?im)^\s*M15\s+is\s+complete[.!]?\s*$",
            r"(?im)^\s*Track\s+E4\s+is\s+complete[.!]?\s*$",
        )
        for pattern in future_promotion_patterns:
            self.assertIsNone(re.search(pattern, next_phase))

        self.assertIn("M15 remains active and incomplete", normalized_next)
        self.assertIn("Track E4 and final human completion review remain required", normalized_next)
        self.assertIn("v0.14.0 remains unpublished", normalized_next)
        self.assertIn(
            "No v0.14.0 tag or GitHub Release is authorized or created",
            normalized_next,
        )

    def test_01_tracker_231_remains_open_statement_is_exact(self):
        self.assertIn("Tracker #231 remains Open.", CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_02_m15_remains_active_and_incomplete_statement_is_exact(self):
        self.assertIn("M15 remains active work and is not complete.", CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_03_v0140_remains_unpublished_statement_is_exact(self):
        self.assertIn("`v0.14.0` remains a future release path and is not published.", CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_04_readme_latest_release_remains_v0130(self):
        readme = README_PATH.read_text(encoding="utf-8")
        self.assert_phase_aware_readme_state(readme)

    def test_05_learning_and_decision_proof_sealing_remain_aaos_owned(self):
        contract = CONTRACT_PATH.read_text(encoding="utf-8")
        self.assertIn("Learning Proof sealing remains AAOS-owned.", contract)
        self.assertIn("Decision Proof sealing remains AAOS-owned.", contract)

    def test_06_capability_pack_sealing_remains_undefined_and_out_of_scope(self):
        contract = CONTRACT_PATH.read_text(encoding="utf-8")
        self.assertIn("Capability Pack sealing remains undefined and out of scope for Track B.", contract)
        self.assertNotIn("Capability Pack sealing remains AAOS-owned.", contract)

    def test_07_aaos_remains_decision_sovereignty_layer(self):
        self.assertIn("AAOS remains the decision sovereignty layer.", CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_08_boundary_statement_matches_contract_schema_runtime_and_fixtures(self):
        statement = evaluator_module.NON_AUTHORITATIVE_BOUNDARY_STATEMENT
        self.assertIn(f"> {statement}", CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(self.schema["properties"]["non_authoritative_boundary_statement"]["const"], statement)
        for artifact in self.fixtures.values():
            self.assertEqual(artifact["non_authoritative_boundary_statement"], statement)

    def test_09_contract_does_not_claim_m15_completion(self):
        contract = CONTRACT_PATH.read_text(encoding="utf-8")
        self.assertNotIn("M15 is complete.", contract)
        self.assertNotIn("M15 completed.", contract)

    def test_10_contract_forbids_release_publication_and_tracker_closure(self):
        contract = CONTRACT_PATH.read_text(encoding="utf-8")
        self.assertIn("It does not modify README release or milestone declarations, close tracker #231, or claim M15 completion.", contract)
        self.assertIn("no network call", contract)

    def test_11_release_tracker_and_m15_completion_aliases_fail_closed(self):
        cases = (
            {"m15_complete": True},
            {"m15_status": {"result": "complete"}},
            {"tracker_231_closed": True},
            {"issue_231_status": "closed"},
            {"v0_14_0_published": True},
        )
        for extension in cases:
            with self.subTest(extension=extension):
                artifact = self.fixture()
                artifact["extensions"] = copy.deepcopy(extension)
                result = self.evaluate(artifact)
                self.assert_invalid(result)
                self.assertFalse(result["authority_boundary_valid"])

    def test_12_explicit_readme_completion_and_release_promotions_fail(self):
        readme = README_PATH.read_text(encoding="utf-8")
        next_phase_claims = (
            "v0.14.0 is released.",
            "v0.14.0 tag exists.",
            "GitHub Release v0.14.0 is published.",
            "M15 is complete.",
            "Track E4 is complete.",
        )
        for claim in next_phase_claims:
            with self.subTest(claim=claim):
                with self.assertRaises(AssertionError):
                    self.assert_phase_aware_readme_state(readme + "\n" + claim + "\n")

        release_entry = readme.replace(
            "## Current Status",
            "- v0.14.0 — unauthorized future release\n\n## Current Status",
            1,
        )
        with self.assertRaises(AssertionError):
            self.assert_phase_aware_readme_state(release_entry)

        for claim in (
            "M1–M15 are complete.",
            "v0.14.0 is published.",
            "tracker #231 is closed.",
        ):
            with self.subTest(current_status_claim=claim):
                mutated = readme.replace(
                    "## M5 Additions",
                    claim + "\n\n## M5 Additions",
                    1,
                )
                with self.assertRaises(AssertionError):
                    self.assert_phase_aware_readme_state(mutated)

    def test_12_negative_release_tracker_and_m15_statuses_remain_valid(self):
        cases = (
            {"m15_status": {"result": "incomplete"}},
            {"tracker_231": {"status": "open"}},
            {"issue_231": {"status": "open"}},
            {"v0_14_0": {"status": "unpublished"}},
            {"release": {"status": "unpublished"}},
            {"github_release": {"status": "not-created"}},
        )
        for extension in cases:
            with self.subTest(extension=extension):
                artifact = self.fixture()
                artifact["extensions"] = copy.deepcopy(extension)
                self.assert_valid(self.evaluate(artifact))


if __name__ == "__main__":
    unittest.main()
