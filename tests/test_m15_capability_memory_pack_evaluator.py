"""Deterministic tests for the M15 Capability Memory Pack evaluator."""

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

import runtime.m15_capability_memory_pack_evaluator as evaluator_module


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "m15-capability-memory-pack.schema.json"
EVALUATOR_PATH = ROOT / "runtime" / "m15_capability_memory_pack_evaluator.py"
CONTRACT_PATH = ROOT / "docs" / "learning-governance" / "m15-capability-memory-pack-contract.md"
FIXTURE_PATHS = {
    "verified": ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m15-capability-pack-valid-verified.json",
    "stale": ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m15-capability-pack-stale-specification.json",
    "altered": ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m15-capability-pack-altered-graph.json",
    "incompatible": ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m15-capability-pack-incompatible-runtime.json",
    "revoked": ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m15-capability-pack-revoked.json",
    "source_digest_mismatch": ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m15-capability-pack-source-digest-mismatch.json",
    "altered_derived": ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m15-capability-pack-altered-derived-specification.json",
    "missing_license_boundary": ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m15-capability-pack-missing-license-usage-boundary-evidence.json",
    "executable_authority": ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m15-capability-pack-executable-authority-claim.json",
}

SCHEMA_VERSION = "m15-capability-memory-pack/v1"
LIFECYCLE_STATES = (
    "unverified",
    "verified",
    "stale",
    "incompatible",
    "quarantined",
    "superseded",
    "revoked",
)
COMPATIBILITY_RESULTS = ("compatible", "incompatible", "unknown")
REDISTRIBUTION_STATUSES = ("allowed", "restricted", "prohibited", "unknown")
LICENSE_REVIEW_STATUSES = ("reviewed", "review-required", "revoked")
EVIDENCE_DISPOSITIONS = (
    "verified-read-only",
    "stale-evidence",
    "quarantined-evidence",
    "incompatible-evidence",
    "revoked-evidence",
    "unverified-evidence",
)
ARTIFACT_ROLES = (
    "structured-spec",
    "workflow-graph",
    "examples",
    "error-taxonomy",
    "graph-snapshot",
    "verification-report",
)
SHA256_PATTERN = r"^[0-9a-f]{64}$"
BOUNDARY_STATEMENT = (
    "This Capability Memory Pack is evidence only; runtime eligibility means "
    "eligibility for independent policy review, not installation, registration, "
    "deployment, execution, risk acceptance, Learning Proof sealing, or Decision "
    "Proof sealing. Capability Pack sealing is undefined and out of scope for M15 "
    "Track B. A capability pack must not claim sealed status or sealing authority."
)
EXPECTED_RESULT_KEYS = {
    "valid",
    "schema_valid",
    "pack_identity_valid",
    "source_manifest_valid",
    "license_manifest_valid",
    "derived_manifest_valid",
    "artifact_inventory_valid",
    "artifact_digest_bindings_valid",
    "graph_binding_valid",
    "runtime_compatibility_valid",
    "lifecycle_valid",
    "revocation_state_valid",
    "sensitive_material_absent",
    "learning_proof_linkage_valid",
    "decision_proof_linkage_valid",
    "authority_boundary_valid",
    "retrieval_eligible",
    "runtime_eligible",
    "verified_pack_eligible",
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


def validate_schema_subset(
    instance,
    schema,
    *,
    root_schema=None,
    path="$",
    quiet=False,
):
    """Validate the draft-2020-12 subset used by the checked-in Track B schema."""

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
        required = schema.get("required", [])
        for key in required:
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
        if isinstance(schema.get("contains"), Mapping):
            matches = sum(
                not validate_schema_subset(
                    item,
                    schema["contains"],
                    root_schema=root_schema,
                    path=f"{path}[{index}]",
                    quiet=True,
                )
                for index, item in enumerate(instance)
            )
            if matches < schema.get("minContains", 1):
                add("minContains")
            if "maxContains" in schema and matches > schema["maxContains"]:
                add("maxContains")

    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            add("minLength")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            add("maxLength")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            add("pattern")

    return errors


class M15CapabilityMemoryPackEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_json(SCHEMA_PATH)
        cls.fixtures = {name: load_json(path) for name, path in FIXTURE_PATHS.items()}

    def fixture(self, name="verified"):
        return copy.deepcopy(self.fixtures[name])

    def evaluate(self, artifact):
        return evaluator_module.evaluate_capability_memory_pack(artifact)

    def mutated(self, mutator, *, fixture="verified"):
        baseline = self.fixture(fixture)
        artifact = copy.deepcopy(baseline)
        mutator(artifact)
        self.assertNotEqual(
            artifact,
            baseline,
            "regression mutation must not be a no-op",
        )
        return artifact

    def assert_invalid(self, result, finding=None):
        self.assertFalse(result["valid"], result["findings"])
        self.assertFalse(result["verified_pack_eligible"])
        if finding is not None:
            self.assertIn(finding, result["findings"])

    def assert_valid_record(self, result):
        self.assertTrue(result["valid"], result["findings"])
        self.assertEqual(result["findings"], sorted(set(result["findings"])))

    def assert_authority_claim_rejected(self, field):
        artifact = self.mutated(
            lambda value: value["authority_claims"].__setitem__(field, True)
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["authority_boundary_valid"])
        self.assertTrue(
            any(field in finding for finding in result["findings"]),
            result["findings"],
        )

    def test_01_schema_and_all_public_fixtures_are_structurally_valid(self):
        self.assertEqual(
            self.schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        self.assertIs(self.schema["additionalProperties"], False)
        for name, artifact in self.fixtures.items():
            with self.subTest(name=name):
                self.assertEqual(
                    validate_schema_subset(artifact, self.schema),
                    [],
                )
                self.assertTrue(self.evaluate(artifact)["schema_valid"])

    def test_02_contract_enumerations_roles_and_digest_pattern_are_exact(self):
        properties = self.schema["properties"]
        self.assertEqual(properties["schema_version"]["const"], SCHEMA_VERSION)
        self.assertEqual(properties["lifecycle_state"]["enum"], list(LIFECYCLE_STATES))
        self.assertEqual(
            properties["runtime_compatibility"]["properties"][
                "compatibility_mode"
            ]["enum"],
            ["exact"],
        )
        self.assertEqual(
            properties["runtime_compatibility"]["properties"][
                "compatibility_result"
            ]["enum"],
            list(COMPATIBILITY_RESULTS),
        )
        self.assertEqual(
            properties["license_manifest"]["properties"]["redistribution_status"][
                "enum"
            ],
            list(REDISTRIBUTION_STATUSES),
        )
        self.assertEqual(
            properties["license_manifest"]["properties"]["license_review_status"][
                "enum"
            ],
            list(LICENSE_REVIEW_STATUSES),
        )
        self.assertEqual(properties["evidence_disposition"]["enum"], list(EVIDENCE_DISPOSITIONS))
        self.assertEqual(
            self.schema["$defs"]["artifact_role"]["enum"],
            list(ARTIFACT_ROLES),
        )
        self.assertEqual(self.schema["$defs"]["digest"]["pattern"], SHA256_PATTERN)

    def test_03_evaluator_result_contract_is_exact_and_typed(self):
        result = self.evaluate(self.fixture())
        self.assertEqual(set(result), EXPECTED_RESULT_KEYS)
        for key in EXPECTED_RESULT_KEYS - {"findings", "evidence_disposition"}:
            self.assertIsInstance(result[key], bool, key)
        self.assertIsInstance(result["findings"], list)
        self.assertIsInstance(result["evidence_disposition"], str)

    def test_04_valid_verified_fixture_is_verified_pack_eligible(self):
        artifact = self.fixture()
        result = self.evaluate(artifact)
        self.assert_valid_record(result)
        for key in EXPECTED_RESULT_KEYS - {
            "findings",
            "evidence_disposition",
        }:
            self.assertTrue(result[key], key)
        self.assertEqual(result["evidence_disposition"], "verified-read-only")
        self.assertIs(artifact["authority_claims"]["execution_authorized"], False)
        self.assertIs(artifact["runtime_eligible"], True)

    def test_05_stale_fixture_is_valid_evidence_but_not_verified_eligible(self):
        result = self.evaluate(self.fixture("stale"))
        self.assert_valid_record(result)
        self.assertFalse(result["verified_pack_eligible"])
        self.assertFalse(result["runtime_eligible"])
        self.assertEqual(result["evidence_disposition"], "stale-evidence")
        self.assertIn("source_api_version_drift", result["findings"])

    def test_06_altered_graph_fixture_is_valid_quarantine_evidence(self):
        result = self.evaluate(self.fixture("altered"))
        self.assert_valid_record(result)
        self.assertFalse(result["graph_binding_valid"])
        self.assertFalse(result["retrieval_eligible"])
        self.assertFalse(result["runtime_eligible"])
        self.assertEqual(result["evidence_disposition"], "quarantined-evidence")
        self.assertIn("graph_snapshot_digest_mismatch", result["findings"])
        self.assertIn("graph_immutable_source_binding_mismatch", result["findings"])

    def test_07_incompatible_runtime_fixture_has_no_fallback(self):
        result = self.evaluate(self.fixture("incompatible"))
        self.assert_valid_record(result)
        self.assertFalse(result["runtime_compatibility_valid"])
        self.assertFalse(result["runtime_eligible"])
        self.assertEqual(result["evidence_disposition"], "incompatible-evidence")
        self.assertIn("runtime_version_mismatch", result["findings"])

    def test_08_revoked_fixture_is_valid_revocation_evidence(self):
        result = self.evaluate(self.fixture("revoked"))
        self.assert_valid_record(result)
        self.assertTrue(result["revocation_state_valid"])
        self.assertFalse(result["retrieval_eligible"])
        self.assertFalse(result["runtime_eligible"])
        self.assertEqual(result["evidence_disposition"], "revoked-evidence")
        for fixture_name in ("altered", "incompatible", "revoked"):
            with self.subTest(fixture=fixture_name, concurrent_api_drift=True):
                drifted = self.mutated(
                    lambda value: value["source_manifest"].__setitem__(
                        "upstream_api_version", "synthetic-api/v2"
                    ),
                    fixture=fixture_name,
                )
                drifted_result = self.evaluate(drifted)
                self.assert_valid_record(drifted_result)
                self.assertTrue(drifted_result["lifecycle_valid"])
                self.assertIn(
                    "source_api_version_drift",
                    drifted_result["findings"],
                )

    def test_09_unsupported_schema_version_fails_closed(self):
        artifact = self.mutated(
            lambda value: value.__setitem__(
                "schema_version", "m15-capability-memory-pack/v2"
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result, "schema_version_missing_or_unsupported")
        self.assertFalse(result["schema_valid"])

    def test_10_missing_pack_identifier_fails_closed(self):
        artifact = self.mutated(lambda value: value.pop("capability_pack_id"))
        result = self.evaluate(artifact)
        self.assert_invalid(result, "capability_pack_id_missing")
        self.assertFalse(result["pack_identity_valid"])
        whitespace_id = self.mutated(
            lambda value: value.__setitem__("capability_pack_id", " ")
        )
        whitespace_result = self.evaluate(whitespace_id)
        self.assert_invalid(whitespace_result)
        self.assertFalse(whitespace_result["schema_valid"])
        self.assertNotEqual(
            validate_schema_subset(whitespace_id, self.schema),
            [],
        )

    def test_11_malformed_digest_fails_closed(self):
        artifact = self.mutated(
            lambda value: value["source_manifest"].__setitem__(
                "manifest_digest", "sha256:" + "A" * 64
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["source_manifest_valid"])
        self.assertTrue(
            any(
                item.startswith("digest_malformed:source_manifest.manifest_digest")
                for item in result["findings"]
            ),
            result["findings"],
        )

    def test_12_missing_artifact_role_fails_closed(self):
        artifact = self.mutated(
            lambda value: value["artifact_inventory"].pop()
        )
        missing_role = next(
            role
            for role in ARTIFACT_ROLES
            if role not in {item["role"] for item in artifact["artifact_inventory"]}
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result, f"artifact_role_missing:{missing_role}")
        self.assertFalse(result["artifact_inventory_valid"])
        self.assertFalse(result["artifact_digest_bindings_valid"])
        if missing_role in {"graph-snapshot", "structured-spec", "workflow-graph"}:
            self.assertFalse(result["graph_binding_valid"])

    def test_13_duplicate_artifact_role_fails_closed(self):
        def duplicate(value):
            value["artifact_inventory"][-1]["role"] = value["artifact_inventory"][0][
                "role"
            ]

        artifact = self.mutated(duplicate)
        role = artifact["artifact_inventory"][0]["role"]
        result = self.evaluate(artifact)
        self.assert_invalid(result, f"duplicate_artifact_role:{role}")
        self.assertFalse(result["artifact_inventory_valid"])

    def test_14_executable_artifact_fails_closed(self):
        artifact = self.mutated(
            lambda value: value["artifact_inventory"][0].__setitem__(
                "executable", True
            )
        )
        role = artifact["artifact_inventory"][0]["role"]
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["artifact_inventory_valid"])
        self.assertTrue(
            any(
                item.startswith("executable_artifact_forbidden:") and role in item
                for item in result["findings"]
            ),
            result["findings"],
        )
        malformed_media_type = self.mutated(
            lambda value: value["artifact_inventory"][0].__setitem__(
                "media_type", "not a media type"
            )
        )
        malformed_result = self.evaluate(malformed_media_type)
        self.assert_invalid(malformed_result)
        self.assertFalse(malformed_result["artifact_inventory_valid"])
        self.assertFalse(malformed_result["schema_valid"])

    def test_15_source_manifest_digest_binding_mismatch_fails_closed(self):
        artifact = self.mutated(
            lambda value: value["derived_spec_manifest"].__setitem__(
                "source_manifest_digest", "0" * 64
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result, "derived_source_manifest_digest_mismatch")
        self.assertFalse(result["artifact_digest_bindings_valid"])
        for prerequisite in (
            "manifest_references",
            "source_manifest",
            "license_manifest",
            "derived_spec_manifest",
        ):
            with self.subTest(missing_prerequisite=prerequisite):
                missing = self.mutated(
                    lambda value, prerequisite=prerequisite: value.pop(
                        prerequisite
                    )
                )
                missing_result = self.evaluate(missing)
                self.assert_invalid(missing_result)
                self.assertFalse(
                    missing_result["artifact_digest_bindings_valid"]
                )
                if prerequisite == "source_manifest":
                    self.assertFalse(missing_result["graph_binding_valid"])
        for endpoint_value in (None, "malformed-digest"):
            with self.subTest(equal_invalid_endpoints=endpoint_value):
                def invalidate_equal_endpoints(value):
                    value["manifest_references"][
                        "source_manifest_digest"
                    ] = endpoint_value
                    value["source_manifest"]["manifest_digest"] = endpoint_value
                    value["derived_spec_manifest"][
                        "source_manifest_digest"
                    ] = endpoint_value

                equal_invalid = self.mutated(invalidate_equal_endpoints)
                equal_invalid_result = self.evaluate(equal_invalid)
                self.assert_invalid(equal_invalid_result)
                self.assertFalse(
                    equal_invalid_result["artifact_digest_bindings_valid"]
                )

    def test_16_license_manifest_digest_binding_mismatch_fails_closed(self):
        artifact = self.mutated(
            lambda value: value["derived_spec_manifest"].__setitem__(
                "license_manifest_digest", "0" * 64
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result, "derived_license_manifest_digest_mismatch")
        self.assertFalse(result["artifact_digest_bindings_valid"])

    def test_17_pack_source_manifest_reference_mismatch_fails_closed(self):
        artifact = self.mutated(
            lambda value: value["manifest_references"].__setitem__(
                "source_manifest_digest", "0" * 64
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["artifact_digest_bindings_valid"])

    def test_18_pack_license_manifest_reference_mismatch_fails_closed(self):
        artifact = self.mutated(
            lambda value: value["manifest_references"].__setitem__(
                "license_manifest_digest", "0" * 64
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["artifact_digest_bindings_valid"])

    def test_19_pack_derived_manifest_reference_mismatch_fails_closed(self):
        artifact = self.mutated(
            lambda value: value["manifest_references"].__setitem__(
                "derived_spec_manifest_digest", "0" * 64
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["artifact_digest_bindings_valid"])

    def test_20_derived_artifact_digest_mismatch_fails_closed(self):
        role = "examples"
        artifact = self.mutated(
            lambda value: value["derived_spec_manifest"]["artifact_digests"].__setitem__(
                role, "0" * 64
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result, f"derived_artifact_digest_mismatch:{role}")
        self.assertFalse(result["artifact_digest_bindings_valid"])

    def test_21_graph_source_manifest_binding_mismatch_fails_closed(self):
        artifact = self.mutated(
            lambda value: value["graph_binding"].__setitem__(
                "source_manifest_digest", "0" * 64
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result, "graph_source_manifest_digest_mismatch")
        self.assertFalse(result["graph_binding_valid"])

    def test_22_graph_immutable_source_binding_mismatch_fails_closed(self):
        artifact = self.mutated(
            lambda value: value["graph_binding"].__setitem__(
                "immutable_source_binding", "0" * 64
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result, "graph_immutable_source_binding_mismatch")
        self.assertFalse(result["graph_binding_valid"])

    def test_23_graph_snapshot_digest_mismatch_fails_closed(self):
        artifact = self.mutated(
            lambda value: value["graph_binding"].__setitem__(
                "graph_snapshot_digest", "0" * 64
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result, "graph_snapshot_digest_mismatch")
        self.assertFalse(result["graph_binding_valid"])

    def test_24_structured_spec_graph_binding_mismatch_fails_closed(self):
        artifact = self.mutated(
            lambda value: value["graph_binding"].__setitem__(
                "structured_spec_digest", "0" * 64
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result, "graph_structured_spec_digest_mismatch")
        self.assertFalse(result["graph_binding_valid"])

    def test_25_workflow_graph_binding_mismatch_fails_closed(self):
        artifact = self.mutated(
            lambda value: value["graph_binding"].__setitem__(
                "workflow_graph_digest", "0" * 64
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result, "graph_workflow_graph_digest_mismatch")
        self.assertFalse(result["graph_binding_valid"])

    def test_26_verified_state_with_api_version_drift_fails_closed(self):
        artifact = self.mutated(
            lambda value: value["derived_spec_manifest"].__setitem__(
                "source_api_version", "synthetic-api-v2"
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result, "source_api_version_drift")
        self.assertFalse(result["lifecycle_valid"])
        verified_adversarial_mutations = {
            "contamination": lambda value: value["lifecycle_evidence"].__setitem__(
                "contamination_detected", True
            ),
            "quarantine reason": lambda value: value[
                "lifecycle_evidence"
            ].__setitem__("quarantine_reason", "synthetic-integrity-alert"),
            "integrity evidence": lambda value: value["graph_binding"].__setitem__(
                "integrity_evidence_reference",
                "urn:aaos:synthetic-integrity-evidence:verified-conflict-001",
            ),
            "license review required": lambda value: value[
                "license_manifest"
            ].__setitem__("license_review_status", "review-required"),
            "redistribution restricted": lambda value: value[
                "license_manifest"
            ].__setitem__("redistribution_status", "restricted"),
            "license review evidence missing": lambda value: value[
                "license_manifest"
            ].__setitem__("review_evidence_reference", None),
        }
        for label, mutator in verified_adversarial_mutations.items():
            with self.subTest(label=label):
                adversarial = self.mutated(mutator)
                adversarial_result = self.evaluate(adversarial)
                self.assert_invalid(adversarial_result)
                self.assertFalse(adversarial_result["lifecycle_valid"])
                self.assertFalse(adversarial_result["verified_pack_eligible"])
        stale_review_without_evidence = self.mutated(
            lambda value: value["license_manifest"].__setitem__(
                "review_evidence_reference", None
            ),
            fixture="stale",
        )
        stale_review_result = self.evaluate(stale_review_without_evidence)
        self.assert_invalid(stale_review_result)
        self.assertFalse(stale_review_result["schema_valid"])
        self.assertNotEqual(
            validate_schema_subset(stale_review_without_evidence, self.schema),
            [],
        )

    def test_27_verified_state_with_runtime_version_mismatch_fails_closed(self):
        artifact = self.mutated(
            lambda value: value["runtime_compatibility"].__setitem__(
                "observed_runtime_version", "synthetic-runtime-v2"
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result, "runtime_version_mismatch")
        self.assertFalse(result["runtime_compatibility_valid"])
        self.assertFalse(result["lifecycle_valid"])

    def test_28_compatible_runtime_requires_evidence_reference(self):
        artifact = self.mutated(
            lambda value: value["runtime_compatibility"].__setitem__(
                "compatibility_evidence_reference", None
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result, "compatibility_evidence_reference_missing")
        self.assertFalse(result["runtime_compatibility_valid"])

    def test_29_stale_state_without_reason_fails_closed(self):
        artifact = self.mutated(
            lambda value: value["lifecycle_evidence"].__setitem__(
                "stale_reason", None
            ),
            fixture="stale",
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result, "stale_reason_missing")
        self.assertFalse(result["lifecycle_valid"])

    def test_30_stale_state_requires_explicit_version_drift(self):
        artifact = self.mutated(
            lambda value: value["lifecycle_evidence"].__setitem__(
                "version_drift_detected", False
            ),
            fixture="stale",
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["lifecycle_valid"])

    def test_31_incompatible_state_claiming_runtime_eligibility_fails_closed(self):
        artifact = self.mutated(
            lambda value: value.__setitem__("runtime_eligible", True),
            fixture="incompatible",
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result, "incompatible_runtime_eligibility_claim")
        self.assertFalse(result["runtime_eligible"])

    def test_32_quarantined_state_claiming_retrieval_eligibility_fails_closed(self):
        artifact = self.mutated(
            lambda value: value.__setitem__("retrieval_eligible", True),
            fixture="altered",
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result, "quarantined_retrieval_eligibility_claim")
        self.assertFalse(result["retrieval_eligible"])

    def test_33_quarantine_requires_an_integrity_or_contamination_signal(self):
        def clear_integrity_signals(value):
            inventory = {item["role"]: item["digest"] for item in value["artifact_inventory"]}
            value["graph_binding"].update(
                {
                    "graph_snapshot_digest": inventory["graph-snapshot"],
                    "structured_spec_digest": inventory["structured-spec"],
                    "workflow_graph_digest": inventory["workflow-graph"],
                    "source_manifest_digest": value["source_manifest"][
                        "manifest_digest"
                    ],
                    "immutable_source_binding": value["source_manifest"][
                        "immutable_commit_or_content_digest"
                    ],
                    "graph_altered": False,
                    "integrity_evidence_reference": None,
                }
            )
            value["lifecycle_evidence"]["contamination_detected"] = False

        artifact = self.mutated(clear_integrity_signals, fixture="altered")
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["lifecycle_valid"])

    def test_34_revoked_state_without_revocation_evidence_fails_closed(self):
        def remove_evidence(value):
            value["revocation"]["revocation_evidence_reference"] = None
            value["license_manifest"]["revocation_evidence_reference"] = None

        artifact = self.mutated(remove_evidence, fixture="revoked")
        result = self.evaluate(artifact)
        self.assert_invalid(result, "revocation_evidence_reference_missing")
        self.assertFalse(result["revocation_state_valid"])

    def test_35_revoked_state_requires_a_revoked_source_license_or_pack(self):
        def clear_revoked_status(value):
            value["source_manifest"]["source_status"] = "active"
            value["license_manifest"]["license_review_status"] = "reviewed"
            value["revocation"]["pack_status"] = "active"

        artifact = self.mutated(clear_revoked_status, fixture="revoked")
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["revocation_state_valid"])

    def test_36_superseded_state_without_successor_fails_closed(self):
        def supersede_without_successor(value):
            value["lifecycle_state"] = "superseded"
            value["lifecycle_evidence"]["superseded_by_reference"] = None
            value["runtime_eligible"] = False
            value["evidence_disposition"] = "stale-evidence"

        artifact = self.mutated(supersede_without_successor)
        result = self.evaluate(artifact)
        self.assert_invalid(result, "superseded_by_reference_missing")
        self.assertFalse(result["lifecycle_valid"])

    def test_37_unverified_state_cannot_claim_retrieval_eligibility(self):
        def mark_unverified(value):
            value["lifecycle_state"] = "unverified"
            value["runtime_eligible"] = False
            value["evidence_disposition"] = "unverified-evidence"

        artifact = self.mutated(mark_unverified)
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["retrieval_eligible"])
        self.assertFalse(result["lifecycle_valid"])

    def test_38_learning_proof_linkage_cannot_be_used_as_authority(self):
        null_linkage = self.mutated(
            lambda value: value.update(
                {
                    "related_learning_proof_reference": None,
                    "related_decision_proof_reference": None,
                }
            )
        )
        null_result = self.evaluate(null_linkage)
        self.assert_valid_record(null_result)
        self.assertTrue(null_result["learning_proof_linkage_valid"])
        self.assertTrue(null_result["decision_proof_linkage_valid"])

        def claim_authority(value):
            reference = value.get("related_learning_proof_reference")
            if reference is None:
                reference = "urn:aaos:m15:learning-proof:synthetic-capability-001"
                value["related_learning_proof_reference"] = reference
            value["extensions"]["installation_approval"] = {
                "state": "approved",
                "basis_reference": reference,
            }

        artifact = self.mutated(claim_authority)
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["learning_proof_linkage_valid"])
        self.assertFalse(result["authority_boundary_valid"])

        for key, claim in (
            ("learning_proof_authorization_reference", True),
            ("learningProofGrantsAuthority", True),
            ("learningproofgrantsauthority", "approved"),
            ("status", "learningProofGrantsAuthority"),
        ):
            with self.subTest(key=key):
                direct_claim = self.mutated(
                    lambda value, key=key, claim=claim: value[
                        "extensions"
                    ].__setitem__(key, claim)
                )
                direct_result = self.evaluate(direct_claim)
                self.assert_invalid(direct_result)
                self.assertFalse(direct_result["learning_proof_linkage_valid"])
        nested_claim = self.mutated(
            lambda value: value["extensions"].__setitem__(
                "learningProof", {"grantsAuthority": True}
            )
        )
        nested_result = self.evaluate(nested_claim)
        self.assert_invalid(nested_result)
        self.assertFalse(nested_result["learning_proof_linkage_valid"])
        for proof_action in ("allows", "enables"):
            with self.subTest(proof_action=proof_action):
                split_claim = self.mutated(
                    lambda value, proof_action=proof_action: value[
                        "extensions"
                    ].__setitem__("learning_proof", {proof_action: True})
                )
                split_result = self.evaluate(split_claim)
                self.assert_invalid(split_result)
                self.assertFalse(split_result["learning_proof_linkage_valid"])
        basis_claim = self.mutated(
            lambda value: value["extensions"].__setitem__(
                "installationDecision",
                {
                    "status": "approved",
                    "basis_reference": value[
                        "related_learning_proof_reference"
                    ],
                },
            )
        )
        basis_result = self.evaluate(basis_claim)
        self.assert_invalid(basis_result)
        self.assertFalse(basis_result["learning_proof_linkage_valid"])
        for neutral_label in (
            "decisionProofIncompleteEvidence",
            "learningProofPermittivityModel",
            "decisionProofMigrantDataset",
        ):
            with self.subTest(neutral_proof_label=neutral_label):
                neutral = self.mutated(
                    lambda value, neutral_label=neutral_label: value[
                        "extensions"
                    ].__setitem__("descriptive_label", neutral_label)
                )
                neutral_result = self.evaluate(neutral)
                self.assert_valid_record(neutral_result)
                self.assertTrue(neutral_result["authority_boundary_valid"])
                self.assertTrue(neutral_result["learning_proof_linkage_valid"])
                self.assertTrue(neutral_result["decision_proof_linkage_valid"])
        for wrapper, key in (
            ("learningProof", "migrant_dataset"),
            ("decisionProof", "fragrant_label"),
        ):
            with self.subTest(neutral_proof_wrapper=wrapper, key=key):
                neutral_nested = self.mutated(
                    lambda value, wrapper=wrapper, key=key: value[
                        "extensions"
                    ].__setitem__(wrapper, {key: "synthetic-read-only"})
                )
                nested_result = self.evaluate(neutral_nested)
                self.assert_valid_record(nested_result)
                self.assertTrue(nested_result["learning_proof_linkage_valid"])
                self.assertTrue(nested_result["decision_proof_linkage_valid"])

    def test_39_decision_proof_linkage_cannot_grant_execution_authority(self):
        def claim_authority(value):
            reference = value.get("related_decision_proof_reference")
            if reference is None:
                reference = "urn:aaos:decision-proof:synthetic-capability-001"
                value["related_decision_proof_reference"] = reference
            value["extensions"]["execution_authorization"] = {
                "state": "approved",
                "basis_reference": reference,
            }

        artifact = self.mutated(claim_authority)
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["decision_proof_linkage_valid"])
        self.assertFalse(result["authority_boundary_valid"])

        for key, claim in (
            ("decision_proof_execution_authority_reference", "approved"),
            ("decisionProofAuthorizesExecution", True),
            ("decisionproofgrantsexecutionauthority", "approved"),
            ("status", "decisionProofAuthorizesExecution"),
        ):
            with self.subTest(key=key):
                direct_claim = self.mutated(
                    lambda value, key=key, claim=claim: value[
                        "extensions"
                    ].__setitem__(key, claim)
                )
                direct_result = self.evaluate(direct_claim)
                self.assert_invalid(direct_result)
                self.assertFalse(direct_result["decision_proof_linkage_valid"])
        nested_claim = self.mutated(
            lambda value: value["extensions"].__setitem__(
                "decisionProof", {"authorizesExecution": True}
            )
        )
        nested_result = self.evaluate(nested_claim)
        self.assert_invalid(nested_result)
        self.assertFalse(nested_result["decision_proof_linkage_valid"])
        basis_claim = self.mutated(
            lambda value: value["extensions"].__setitem__(
                "executionDecision",
                {
                    "status": "approved",
                    "basis_reference": value[
                        "related_decision_proof_reference"
                    ],
                },
            )
        )
        basis_result = self.evaluate(basis_claim)
        self.assert_invalid(basis_result)
        self.assertFalse(basis_result["decision_proof_linkage_valid"])

    def test_40_installation_approval_claim_fails_closed(self):
        self.assert_authority_claim_rejected("installation_approved")

    def test_41_tool_registration_approval_claim_fails_closed(self):
        self.assert_authority_claim_rejected("tool_registration_approved")

    def test_42_deployment_approval_claim_fails_closed(self):
        self.assert_authority_claim_rejected("deployment_approved")

    def test_43_execution_authorization_claim_fails_closed(self):
        self.assert_authority_claim_rejected("execution_authorized")

    def test_44_production_execution_claim_fails_closed(self):
        self.assert_authority_claim_rejected("production_execution_allowed")

    def test_45_risk_acceptance_claim_fails_closed(self):
        self.assert_authority_claim_rejected("risk_accepted")

    def test_46_rollback_execution_claim_fails_closed(self):
        self.assert_authority_claim_rejected("rollback_executed")

    def test_47_audit_closure_claim_fails_closed(self):
        self.assert_authority_claim_rejected("audit_closed")

    def test_48_waiver_claim_fails_closed(self):
        self.assert_authority_claim_rejected("waiver_granted")

    def test_49_authority_transfer_claim_fails_closed(self):
        self.assert_authority_claim_rejected("authority_transferred")

    def test_50_capability_pack_sealed_claim_fails_closed(self):
        self.assert_authority_claim_rejected("capability_pack_sealed")

    def test_51_learning_proof_sealed_claim_fails_closed(self):
        self.assert_authority_claim_rejected("learning_proof_sealed")

    def test_52_decision_proof_sealed_claim_fails_closed(self):
        self.assert_authority_claim_rejected("decision_proof_sealed")

    def test_53_negative_outer_state_cannot_hide_nested_affirmative_claim(self):
        def hide_claim(value):
            value["extensions"]["deployment_approval"] = {
                "state": "denied",
                "details": {"execution_authorized": True},
            }

        artifact = self.mutated(hide_claim)
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["authority_boundary_valid"])
        self.assertTrue(
            any(
                "extensions.deployment_approval" in item
                for item in result["findings"]
            ),
            result["findings"],
        )
        inert_named_wrapper = self.mutated(
            lambda value: value["extensions"].__setitem__(
                "evidence_reference",
                {
                    "state": "denied",
                    "execution_authorized": True,
                },
            )
        )
        wrapper_result = self.evaluate(inert_named_wrapper)
        self.assert_invalid(wrapper_result)
        self.assertFalse(wrapper_result["authority_boundary_valid"])
        reversed_hidden_claim = self.mutated(
            lambda value: value["extensions"].__setitem__(
                "deployment_approval",
                {
                    "state": "denied",
                    "details": {"allowed_to_execute": True},
                },
            )
        )
        reversed_hidden_result = self.evaluate(reversed_hidden_claim)
        self.assert_invalid(reversed_hidden_result)
        self.assertFalse(reversed_hidden_result["authority_boundary_valid"])

    def test_54_unknown_nonempty_authority_claim_fails_closed(self):
        artifact = self.mutated(
            lambda value: value["authority_claims"].__setitem__(
                "custom_authority_decision", "pending"
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["authority_boundary_valid"])
        extension_claims = (
            ("execution_authorization_reference", True),
            ("deployment_approval_digest", "approved"),
            ("executionAuthorization", True),
            ("executionauthorization", "approved"),
            ("deploymentApproved", True),
            ("toolRegistrationApproved", True),
            ("capabilityPackSealed", True),
            ("learningProofSealed", True),
            ("decisionProofSealed", True),
            ("status", "executionAuthorized"),
            ("status", "executionauthorized"),
            ("status", "capabilitypacksealed"),
            ("authority_claim", True),
            ("authorization_claim", True),
            ("approval_status", "approved"),
            ("execution_status", "approved"),
            ("deployment_status", "approved"),
            ("installation_status", "approved"),
            ("tool_registration_status", "approved"),
            ("risk_status", "accepted"),
            ("sealing_status", "sealed"),
            ("execution_authority", "approved"),
            ("execution_granted", "approved"),
            ("execution_permission", True),
            ("deployment_permission", True),
            ("installation_permission", True),
            ("productionUseAllowed", True),
            ("production_use_allowed", True),
            ("toolRegistrationEnabled", True),
            ("auditComplete", True),
            ("current_execution_permission", True),
            ("observed_deployment_permission", True),
            ("current_production_use_allowed", True),
            ("observed_tool_registration_enabled", True),
            ("audit_complete_evidence", True),
            ("allowed_to_execute", True),
            ("execute_allowed", True),
            ("permission_to_execute", True),
            ("permissions", ["execute"]),
            ("can_execute", True),
            ("may_execute", True),
            ("tool_registered", True),
            ("capability_installed", True),
            ("allowed_actions", ["execute"]),
            ("run_allowed", True),
            ("use_in_production", True),
            ("tools_registered", True),
            ("execution_allows", True),
            ("deploymentAllows", True),
            ("executionEnables", True),
            ("deployment_enables", True),
        )
        for key, claim in extension_claims:
            with self.subTest(key=key, claim=claim):
                claimed = self.mutated(
                    lambda value, key=key, claim=claim: value[
                        "extensions"
                    ].__setitem__(key, claim)
                )
                claimed_result = self.evaluate(claimed)
                self.assert_invalid(claimed_result)
                self.assertFalse(claimed_result["authority_boundary_valid"])
        for neutral_label in (
            "synthetic-migrant-dataset",
            "fragrant-synthetic-example",
            "synthetic-permittivity-model",
        ):
            with self.subTest(neutral_label=neutral_label):
                neutral = self.mutated(
                    lambda value, neutral_label=neutral_label: value[
                        "extensions"
                    ].__setitem__("descriptive_label", neutral_label)
                )
                neutral_result = self.evaluate(neutral)
                self.assert_valid_record(neutral_result)
                self.assertTrue(neutral_result["authority_boundary_valid"])

    def test_55_apparent_api_key_is_rejected(self):
        artifact = self.mutated(
            lambda value: value["extensions"].__setitem__(
                "api_key_material", "sk-synthetic-test-only-00000000"
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["sensitive_material_absent"])
        sensitive_key_variants = (
            "database_password_value",
            "customer_access_token_value",
            "customer_api_key_value",
            "pass.word",
            "pass_word",
            "p-a-s-s-w-o-r-d",
            "access.token",
            "api.key",
            "private.key",
            "production.credential",
            "brokerage.account.number",
            "personal.identifier",
            "cert_material",
            "prod_credential",
            "broker_account_number",
            "personal_id",
            "ssn",
        )
        for key in sensitive_key_variants:
            with self.subTest(key=key):
                variant = self.mutated(
                    lambda value, key=key: value["extensions"].__setitem__(
                        key, "synthetic-public-fixture-placeholder"
                    )
                )
                variant_result = self.evaluate(variant)
                self.assert_invalid(variant_result)
                self.assertFalse(variant_result["sensitive_material_absent"])
        google_key = self.mutated(
            lambda value: value["extensions"].__setitem__(
                "material", "AI" + "za1234567890abcdefghijklmnopqrstuv"
            )
        )
        google_result = self.evaluate(google_key)
        self.assert_invalid(google_result)
        self.assertFalse(google_result["sensitive_material_absent"])

    def test_56_apparent_access_token_is_rejected(self):
        artifact = self.mutated(
            lambda value: value["extensions"].__setitem__(
                "access_token", "Bearer synthetic-test-token-00000000"
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["sensitive_material_absent"])
        slack_token = self.mutated(
            lambda value: value["extensions"].__setitem__(
                "material", "xox" + "b-123456789012-abcdefghijklmnop"
            )
        )
        slack_result = self.evaluate(slack_token)
        self.assert_invalid(slack_result)
        self.assertFalse(slack_result["sensitive_material_absent"])

    def test_57_apparent_password_is_rejected(self):
        artifact = self.mutated(
            lambda value: value["extensions"].__setitem__(
                "password", "synthetic-password-value"
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["sensitive_material_absent"])

    def test_58_apparent_private_key_is_rejected(self):
        artifact = self.mutated(
            lambda value: value["extensions"].__setitem__(
                "material",
                "-----BEGIN PRIVATE KEY----- synthetic-test-only",
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["sensitive_material_absent"])

    def test_59_apparent_certificate_material_is_rejected(self):
        artifact = self.mutated(
            lambda value: value["extensions"].__setitem__(
                "material",
                "-----BEGIN CERTIFICATE----- synthetic-test-only",
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["sensitive_material_absent"])

    def test_60_apparent_brokerage_account_identifier_is_rejected(self):
        artifact = self.mutated(
            lambda value: value["extensions"].__setitem__(
                "brokerage_account_number", "SYNTHETIC-ACCOUNT-0001"
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["sensitive_material_absent"])

    def test_61_apparent_personal_identifier_is_rejected(self):
        artifact = self.mutated(
            lambda value: value["extensions"].__setitem__(
                "personal_identifier", "000-00-0000"
            )
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["sensitive_material_absent"])

    def test_62_synthetic_secret_reference_remains_inert(self):
        artifact = self.mutated(
            lambda value: value["extensions"].__setitem__(
                "secret_reference_alias",
                "urn:aaos:synthetic-secret-reference:capability-pack-test-001",
            )
        )
        result = self.evaluate(artifact)
        self.assert_valid_record(result)
        self.assertTrue(result["sensitive_material_absent"])
        self.assertTrue(result["authority_boundary_valid"])
        rejected_alias_suffixes = (
            "password-supersecret",
            "access-token-secretvalue",
            "api-key-secretvalue",
            "private-key-secretvalue",
            "certificate-material-secret",
            "production-credential-secret",
            "brokerage-account-number-123456",
            "personal-identifier-12345",
            "sk-proj-1234567890abcdef",
            "s-k-proj-1234567890abcdef",
        )
        for suffix in rejected_alias_suffixes:
            with self.subTest(suffix=suffix):
                secret_like_alias = self.mutated(
                    lambda value, suffix=suffix: value[
                        "extensions"
                    ].__setitem__(
                        "secret_reference_alias",
                        "urn:aaos:synthetic-secret-reference:" + suffix,
                    )
                )
                alias_result = self.evaluate(secret_like_alias)
                self.assert_invalid(alias_result)
                self.assertFalse(alias_result["sensitive_material_absent"])
        malformed_alias = self.mutated(
            lambda value: value["extensions"].__setitem__(
                "secret_reference_alias",
                "urn:aaos:synthetic-secret-reference:",
            )
        )
        malformed_result = self.evaluate(malformed_alias)
        self.assert_invalid(malformed_result)
        self.assertFalse(malformed_result["sensitive_material_absent"])
        for alias in (
            "URN:AAOS:SYNTHETIC-SECRET-REFERENCE:foo",
            "not-a-valid-alias",
        ):
            with self.subTest(alias=alias):
                invalid_alias = self.mutated(
                    lambda value, alias=alias: value[
                        "extensions"
                    ].__setitem__("secret_reference_alias", alias)
                )
                invalid_alias_result = self.evaluate(invalid_alias)
                self.assert_invalid(invalid_alias_result)
                self.assertFalse(
                    invalid_alias_result["sensitive_material_absent"]
                )

    def test_63_evaluator_performs_no_network_access(self):
        tree = ast.parse(EVALUATOR_PATH.read_text(encoding="utf-8"))
        imported_roots = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            (node.module or "").split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertTrue(
            imported_roots.isdisjoint(
                {"socket", "urllib", "http", "requests", "aiohttp"}
            )
        )
        blocked = AssertionError("network access attempted")
        with (
            mock.patch.object(socket, "socket", side_effect=blocked),
            mock.patch.object(socket, "create_connection", side_effect=blocked),
            mock.patch.object(socket, "getaddrinfo", side_effect=blocked),
        ):
            self.assert_valid_record(self.evaluate(self.fixture()))

    def test_64_evaluator_performs_no_subprocess_or_shell_execution(self):
        tree = ast.parse(EVALUATOR_PATH.read_text(encoding="utf-8"))
        imported_roots = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            (node.module or "").split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertNotIn("subprocess", imported_roots)
        blocked = AssertionError("subprocess or shell execution attempted")
        with (
            mock.patch.object(subprocess, "run", side_effect=blocked),
            mock.patch.object(subprocess, "Popen", side_effect=blocked),
            mock.patch.object(subprocess, "call", side_effect=blocked),
            mock.patch.object(subprocess, "check_call", side_effect=blocked),
            mock.patch.object(subprocess, "check_output", side_effect=blocked),
        ):
            self.assert_valid_record(self.evaluate(self.fixture()))

    def test_65_evaluator_dynamically_imports_no_fixture_or_contract_file(self):
        tree = ast.parse(EVALUATOR_PATH.read_text(encoding="utf-8"))
        imported_roots = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            (node.module or "").split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertTrue(
            imported_roots.isdisjoint(
                {
                    "importlib",
                    "json",
                    "os",
                    "pathlib",
                    "runpy",
                    "subprocess",
                }
            )
        )
        imported_modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        self.assertNotIn("runtime.m15_learning_proof_evaluator", imported_modules)
        self.assertNotIn("runtime.repository_artifact_digest", imported_modules)
        blocked = AssertionError("dynamic import or file access attempted")
        with (
            mock.patch.object(importlib, "import_module", side_effect=blocked),
            mock.patch.object(builtins, "open", side_effect=blocked),
        ):
            self.assert_valid_record(self.evaluate(self.fixture()))

    def test_66_evaluation_mutates_no_input_or_file(self):
        artifact = self.fixture()
        baseline = copy.deepcopy(artifact)
        observed_paths = [EVALUATOR_PATH, SCHEMA_PATH, *FIXTURE_PATHS.values()]
        before = {path: path.read_bytes() for path in observed_paths}
        blocked = AssertionError("file mutation attempted")
        with (
            mock.patch.object(Path, "write_text", side_effect=blocked),
            mock.patch.object(Path, "write_bytes", side_effect=blocked),
            mock.patch.object(Path, "unlink", side_effect=blocked),
            mock.patch.object(Path, "rename", side_effect=blocked),
            mock.patch.object(Path, "replace", side_effect=blocked),
        ):
            self.assert_valid_record(self.evaluate(artifact))
        after = {path: path.read_bytes() for path in observed_paths}
        self.assertEqual(artifact, baseline)
        self.assertEqual(before, after)

    def test_67_repeated_results_and_findings_are_deterministic(self):
        for name, artifact in self.fixtures.items():
            with self.subTest(name=name):
                expected = self.evaluate(copy.deepcopy(artifact))
                for _ in range(10):
                    self.assertEqual(
                        self.evaluate(copy.deepcopy(artifact)),
                        expected,
                    )
                self.assertEqual(
                    expected["findings"],
                    sorted(set(expected["findings"])),
                )

    def test_68_all_public_fixtures_contain_synthetic_data_only(self):
        sensitive_key_tokens = {
            "password",
            "access_token",
            "api_key",
            "private_key",
            "certificate_material",
            "production_credential",
            "brokerage_account_number",
            "personal_identifier",
        }
        sensitive_patterns = (
            re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"),
            re.compile(r"\bgh[pousr]_[A-Za-z0-9]{8,}\b"),
            re.compile(r"\bAKIA[A-Z0-9]{12,}\b"),
            re.compile(r"Bearer\s+\S+", re.IGNORECASE),
            re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
            re.compile(r"-----BEGIN CERTIFICATE-----"),
            re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
            re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
        )

        def walk(value, path=()):
            if isinstance(value, Mapping):
                for key, child in value.items():
                    yield path + (str(key),), child
                    yield from walk(child, path + (str(key),))
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    yield from walk(child, path + (str(index),))

        for name, fixture in self.fixtures.items():
            with self.subTest(name=name):
                serialized = json.dumps(fixture, sort_keys=True)
                for pattern in sensitive_patterns:
                    self.assertIsNone(pattern.search(serialized), pattern.pattern)
                for path, value in walk(fixture):
                    key_token = re.sub(
                        r"[^a-z0-9]+", "_", path[-1].casefold()
                    ).strip("_")
                    self.assertNotIn(key_token, sensitive_key_tokens)
                    if (
                        isinstance(value, str)
                        and (
                            path[-1].endswith("_reference")
                            or path[-1]
                            in {"capability_pack_id", "source_reference", "path"}
                        )
                    ):
                        self.assertIn("synthetic", value.casefold(), (path, value))

    def test_69_source_digest_mismatch_fixture_is_quarantined_evidence(self):
        artifact = self.fixture("source_digest_mismatch")
        result = self.evaluate(artifact)
        self.assert_valid_record(result)
        self.assertTrue(result["schema_valid"])
        self.assertFalse(result["artifact_digest_bindings_valid"])
        self.assertTrue(result["graph_binding_valid"])
        self.assertTrue(result["lifecycle_valid"])
        self.assertFalse(result["retrieval_eligible"])
        self.assertFalse(result["runtime_eligible"])
        self.assertFalse(result["verified_pack_eligible"])
        self.assertEqual(result["evidence_disposition"], "quarantined-evidence")
        self.assertEqual(result["findings"], ["pack_source_manifest_digest_mismatch"])

    def test_70_altered_derived_specification_fixture_is_quarantined_evidence(self):
        artifact = self.fixture("altered_derived")
        result = self.evaluate(artifact)
        self.assert_valid_record(result)
        self.assertTrue(result["schema_valid"])
        self.assertFalse(result["artifact_digest_bindings_valid"])
        self.assertTrue(result["graph_binding_valid"])
        self.assertTrue(result["lifecycle_valid"])
        self.assertFalse(result["retrieval_eligible"])
        self.assertFalse(result["runtime_eligible"])
        self.assertFalse(result["verified_pack_eligible"])
        self.assertEqual(result["evidence_disposition"], "quarantined-evidence")
        self.assertEqual(
            result["findings"],
            ["derived_artifact_digest_mismatch:structured-spec"],
        )

    def test_71_missing_license_boundary_fixture_remains_unverified(self):
        artifact = self.fixture("missing_license_boundary")
        result = self.evaluate(artifact)
        self.assert_valid_record(result)
        self.assertTrue(result["schema_valid"])
        self.assertTrue(result["license_manifest_valid"])
        self.assertTrue(result["lifecycle_valid"])
        self.assertFalse(result["retrieval_eligible"])
        self.assertFalse(result["runtime_eligible"])
        self.assertFalse(result["verified_pack_eligible"])
        self.assertEqual(result["evidence_disposition"], "unverified-evidence")
        self.assertEqual(result["findings"], [])
        self.assertEqual(
            artifact["license_manifest"]["license_review_status"],
            "review-required",
        )
        self.assertEqual(
            artifact["license_manifest"]["redistribution_status"],
            "unknown",
        )
        self.assertIsNone(
            artifact["license_manifest"]["review_evidence_reference"]
        )

    def test_72_executable_authority_fixture_fails_closed(self):
        artifact = self.fixture("executable_authority")
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertTrue(result["schema_valid"])
        self.assertFalse(result["authority_boundary_valid"])
        self.assertFalse(result["lifecycle_valid"])
        self.assertFalse(result["retrieval_eligible"])
        self.assertFalse(result["runtime_eligible"])
        self.assertTrue(
            all(item["executable"] is False for item in artifact["artifact_inventory"])
        )
        self.assertTrue(
            all(value is False for value in artifact["authority_claims"].values())
        )
        self.assertEqual(
            result["findings"],
            [
                "affirmative_forbidden_claim:extensions.capability_pack_execution_authority",
                "verified_lifecycle_requirements_not_met",
            ],
        )

    def test_73_contract_preserves_m15_and_sealing_status_boundaries(self):
        contract = CONTRACT_PATH.read_text(encoding="utf-8")
        self.assertIn("Tracker #231 remains Open.", contract)
        self.assertIn("M15 remains active work and is not complete.", contract)
        self.assertIn(
            "`v0.14.0` remains a future release path and is not published.",
            contract,
        )
        self.assertIn(
            "Capability Pack sealing is undefined and out of scope for M15 Track B.",
            contract,
        )
        self.assertIn(
            "A capability pack must not claim sealed status or sealing authority.",
            contract,
        )
        self.assertNotIn(
            "Capability Pack sealing remains " + "AAOS-owned.",
            contract,
        )
        self.assertIn("Learning Proof sealing remains AAOS-owned.", contract)
        self.assertIn("Decision Proof sealing remains AAOS-owned.", contract)
        self.assertIn("AAOS remains the decision sovereignty layer.", contract)
        self.assertEqual(
            self.schema["properties"]["non_authoritative_boundary_statement"][
                "const"
            ],
            BOUNDARY_STATEMENT,
        )
        self.assertEqual(
            evaluator_module.NON_AUTHORITATIVE_BOUNDARY_STATEMENT,
            BOUNDARY_STATEMENT,
        )
        for artifact in self.fixtures.values():
            self.assertEqual(
                artifact["non_authoritative_boundary_statement"],
                BOUNDARY_STATEMENT,
            )


if __name__ == "__main__":
    unittest.main()
