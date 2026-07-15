import ast
import builtins
import copy
import importlib
import json
import os
import re
import runpy
import socket
import subprocess
import sys
import unittest
import urllib.request
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import runtime.m15_learning_proof_evaluator as evaluator_module  # noqa: E402
from runtime.m15_learning_proof_evaluator import (  # noqa: E402
    ALLOWED_PURPOSES,
    AUTHORIZATION_OUTCOMES,
    LIFECYCLE_STATES,
    NON_AUTHORITATIVE_BOUNDARY_STATEMENT,
    SCHEMA_VERSION,
    SENSITIVITY_CLASSES,
    SOURCE_OWNERS,
    SOURCE_TYPES,
    SOVEREIGNTY_BOUNDARIES,
    evaluate_learning_proof,
)


SCHEMA_PATH = ROOT / "schemas" / "m15-learning-proof.schema.json"
FIXTURE_PATHS = {
    "approved": (
        ROOT
        / "examples"
        / "public-integration-pack-pilot"
        / "m15-learning-proof-approved-evaluation-only.json"
    ),
    "denied": (
        ROOT
        / "examples"
        / "public-integration-pack-pilot"
        / "m15-learning-proof-rejected-untrusted-correction.json"
    ),
    "quarantine": (
        ROOT
        / "examples"
        / "public-integration-pack-pilot"
        / "m15-learning-proof-contaminated-quarantine.json"
    ),
}
EVALUATOR_PATH = ROOT / "runtime" / "m15_learning_proof_evaluator.py"

EXPECTED_RESULT_FIELDS = {
    "valid",
    "schema_valid",
    "source_integrity_present",
    "source_integrity_format_valid",
    "classification_valid",
    "boundary_valid",
    "authorization_evidence_valid",
    "purpose_separation_valid",
    "lifecycle_valid",
    "contamination_state_valid",
    "authority_boundary_valid",
    "decision_proof_linkage_valid",
    "authorization_outcome",
    "authorized_purpose",
    "evidence_disposition",
    "findings",
}

EXPECTED_SOURCE_TYPES = (
    "prompt",
    "trace",
    "correction",
    "evaluation",
    "decision",
    "tool-output",
    "specification",
    "generated-artifact",
)
EXPECTED_SOURCE_OWNERS = (
    "organization",
    "employee",
    "customer",
    "provider",
    "shared",
    "unknown",
)
EXPECTED_SENSITIVITY_CLASSES = (
    "public",
    "internal",
    "confidential",
    "restricted",
)
EXPECTED_PURPOSES = (
    "ephemeral-inference",
    "evaluation",
    "memory",
    "skill",
    "training",
    "audit",
)
EXPECTED_BOUNDARIES = (
    "local",
    "organization",
    "tenant",
    "approved-provider",
    "external",
    "public",
)
EXPECTED_OUTCOMES = (
    "deny",
    "allow-ephemeral",
    "allow-evaluation-only",
    "allow-memory",
    "allow-skill",
    "allow-training",
    "quarantine",
    "require-review",
)
EXPECTED_LIFECYCLE_STATES = (
    "proposed",
    "verified",
    "quarantined",
    "active",
    "stale",
    "incompatible",
    "superseded",
    "revoked",
    "deletion-pending",
    "deleted",
)
FIXED_FALSE_AUTHORITY_CLAIMS = (
    "release_approved",
    "deployment_approved",
    "execution_authorized",
    "risk_accepted",
    "rollback_executed",
    "deletion_executed",
    "audit_closed",
    "waiver_granted",
    "authority_transferred",
    "learning_proof_sealed",
    "decision_proof_sealed",
)


def load_json(path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _schema_type_matches(value, expected_type):
    checks = {
        "null": value is None,
        "boolean": isinstance(value, bool),
        "object": isinstance(value, Mapping),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
    }
    return checks.get(expected_type, True)


def _resolve_local_reference(root_schema, reference):
    if not reference.startswith("#/"):
        raise AssertionError(f"unsupported non-local schema reference: {reference}")
    value = root_schema
    for encoded_part in reference[2:].split("/"):
        part = encoded_part.replace("~1", "/").replace("~0", "~")
        value = value[part]
    return value


def _is_rfc3339(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})",
        value,
    ):
        return False
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def validate_schema_subset(instance, schema, *, root_schema=None, path="$", quiet=False):
    """Validate the draft-2020-12 subset used by the checked-in M15 schema."""

    root_schema = schema if root_schema is None else root_schema
    errors = []

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
        branches = [
            validate_schema_subset(
                instance,
                branch,
                root_schema=root_schema,
                path=path,
                quiet=True,
            )
            for branch in schema["anyOf"]
        ]
        if all(branch_errors for branch_errors in branches):
            errors.append(f"{path}:anyOf")

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
            errors.append(f"{path}:oneOf")

    if "not" in schema and not validate_schema_subset(
        instance,
        schema["not"],
        root_schema=root_schema,
        path=path,
        quiet=True,
    ):
        errors.append(f"{path}:not")

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
            errors.append(f"{path}:type")
            return errors

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}:const")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}:enum")

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
            errors.append(f"{path}:minItems")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}:maxItems")
        if schema.get("uniqueItems"):
            normalized = [json.dumps(item, sort_keys=True) for item in instance]
            if len(normalized) != len(set(normalized)):
                errors.append(f"{path}:uniqueItems")
        item_schema = schema.get("items")
        if isinstance(item_schema, Mapping):
            for index, item in enumerate(instance):
                errors.extend(
                    validate_schema_subset(
                        item,
                        item_schema,
                        root_schema=root_schema,
                        path=f"{path}.{index}",
                        quiet=quiet,
                    )
                )

    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{path}:minLength")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{path}:maxLength")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append(f"{path}:pattern")
        if schema.get("format") == "date-time" and not _is_rfc3339(instance):
            errors.append(f"{path}:format:date-time")

    return errors


def dotted_name(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


class M15LearningProofEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_json(SCHEMA_PATH)
        cls.evaluator_source = EVALUATOR_PATH.read_text(encoding="utf-8")
        cls.evaluator_tree = ast.parse(cls.evaluator_source)

    def setUp(self):
        self.fixtures = {
            name: load_json(path) for name, path in FIXTURE_PATHS.items()
        }

    def fixture(self, name="approved"):
        return copy.deepcopy(self.fixtures[name])

    def evaluate(self, artifact):
        return evaluate_learning_proof(artifact)

    def assert_valid_evidence(self, result):
        self.assertTrue(result["valid"], result["findings"])
        for field in (
            "schema_valid",
            "source_integrity_present",
            "source_integrity_format_valid",
            "classification_valid",
            "boundary_valid",
            "authorization_evidence_valid",
            "purpose_separation_valid",
            "lifecycle_valid",
            "contamination_state_valid",
            "authority_boundary_valid",
            "decision_proof_linkage_valid",
        ):
            self.assertTrue(result[field], field)
        self.assertEqual(set(result), EXPECTED_RESULT_FIELDS)

    def assert_invalid(self, result, finding=None):
        self.assertFalse(result["valid"])
        self.assertTrue(result["findings"])
        if finding is not None:
            self.assertIn(finding, result["findings"])

    def assert_authority_claim_rejected(self, field):
        artifact = self.fixture()
        artifact["authority_claims"][field] = True
        result = self.evaluate(artifact)
        self.assert_invalid(result, f"authority_claim_must_be_false:{field}")
        self.assertFalse(result["schema_valid"])
        self.assertFalse(result["authority_boundary_valid"])
        self.assertTrue(
            any(
                finding.startswith("affirmative_forbidden_claim:authority_claims")
                and field in finding
                for finding in result["findings"]
            ),
            result["findings"],
        )

    def test_01_schema_and_all_public_fixtures_are_structurally_valid(self):
        self.assertEqual(
            self.schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        self.assertIs(self.schema["additionalProperties"], False)
        for name, fixture in self.fixtures.items():
            with self.subTest(name=name):
                self.assertEqual(
                    validate_schema_subset(fixture, self.schema),
                    [],
                )
                self.assertTrue(self.evaluate(fixture)["schema_valid"])

    def test_02_contract_enumeration_spellings_are_exact(self):
        expected = {
            "source_type": EXPECTED_SOURCE_TYPES,
            "source_owner": EXPECTED_SOURCE_OWNERS,
            "sensitivity": EXPECTED_SENSITIVITY_CLASSES,
            "requested_purpose": EXPECTED_PURPOSES,
            "processing_boundary": EXPECTED_BOUNDARIES,
            "retention_boundary": EXPECTED_BOUNDARIES,
            "authorization_outcome": EXPECTED_OUTCOMES,
            "lifecycle_state": EXPECTED_LIFECYCLE_STATES,
        }
        runtime_values = {
            "source_type": SOURCE_TYPES,
            "source_owner": SOURCE_OWNERS,
            "sensitivity": SENSITIVITY_CLASSES,
            "requested_purpose": ALLOWED_PURPOSES,
            "processing_boundary": SOVEREIGNTY_BOUNDARIES,
            "retention_boundary": SOVEREIGNTY_BOUNDARIES,
            "authorization_outcome": AUTHORIZATION_OUTCOMES,
            "lifecycle_state": LIFECYCLE_STATES,
        }
        for field, values in expected.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.schema["properties"][field]["enum"], list(values)
                )
                self.assertEqual(runtime_values[field], frozenset(values))
        self.assertEqual(SCHEMA_VERSION, "m15-learning-proof/v1")
        self.assertEqual(
            self.schema["properties"]["schema_version"]["const"], SCHEMA_VERSION
        )
        self.assertEqual(
            set(self.schema["properties"]["authorized_purpose"]["enum"]),
            set(EXPECTED_PURPOSES) | {None},
        )

    def test_03_result_field_contract_is_exact(self):
        result = self.evaluate(self.fixture())
        self.assertEqual(set(result), EXPECTED_RESULT_FIELDS)
        self.assertIsInstance(result["findings"], list)
        for field in EXPECTED_RESULT_FIELDS - {
            "authorization_outcome",
            "authorized_purpose",
            "evidence_disposition",
            "findings",
        }:
            self.assertIsInstance(result[field], bool, field)

    def test_04_approved_evaluation_only_fixture_is_valid(self):
        artifact = self.fixture("approved")
        result = self.evaluate(artifact)
        self.assert_valid_evidence(result)
        self.assertEqual(result["authorization_outcome"], "allow-evaluation-only")
        self.assertEqual(result["authorized_purpose"], "evaluation")
        self.assertEqual(result["evidence_disposition"], "evaluation-only-evidence")
        self.assertEqual(artifact["requested_purpose"], "evaluation")
        self.assertEqual(artifact["lifecycle_state"], "verified")
        self.assertTrue("synthetic" in artifact["source_reference"])
        self.assertRegex(artifact["source_integrity_hash"], r"^[0-9a-f]{64}$")
        self.assertTrue(all(value is False for value in artifact["authority_claims"].values()))
        self.assertNotIn(result["authorized_purpose"], {"memory", "skill", "training"})

    def test_05_denied_untrusted_correction_is_valid_denial_evidence(self):
        artifact = self.fixture("denied")
        result = self.evaluate(artifact)
        self.assert_valid_evidence(result)
        self.assertEqual(result["authorization_outcome"], "deny")
        self.assertIsNone(result["authorized_purpose"])
        self.assertEqual(result["evidence_disposition"], "denied-evidence")
        self.assertIn("authorization_denied", result["findings"])
        self.assertIn("self_asserted_trust_marker_ignored", result["findings"])
        self.assertTrue(all(value is False for value in artifact["authority_claims"].values()))

    def test_06_contaminated_quarantine_is_valid_quarantine_evidence(self):
        artifact = self.fixture("quarantine")
        result = self.evaluate(artifact)
        self.assert_valid_evidence(result)
        self.assertEqual(result["authorization_outcome"], "quarantine")
        self.assertIsNone(result["authorized_purpose"])
        self.assertEqual(result["evidence_disposition"], "quarantine-evidence")
        self.assertIn("contamination_quarantine_recorded", result["findings"])
        self.assertTrue(artifact["contamination_detected"])
        self.assertTrue(artifact["contamination_evidence_references"])
        for field in (
            "execution_authorized",
            "rollback_executed",
            "deletion_executed",
            "learning_proof_sealed",
            "decision_proof_sealed",
        ):
            self.assertIs(artifact["authority_claims"][field], False)

    def test_07_missing_identifier_fails_closed(self):
        artifact = self.fixture()
        artifact.pop("learning_proof_id")
        result = self.evaluate(artifact)
        self.assert_invalid(result, "required_field_missing:learning_proof_id")
        self.assertFalse(result["schema_valid"])

    def test_08_missing_source_hash_fails_closed(self):
        artifact = self.fixture()
        artifact.pop("source_integrity_hash")
        result = self.evaluate(artifact)
        self.assert_invalid(result, "source_integrity_hash_missing")
        self.assertFalse(result["schema_valid"])
        self.assertFalse(result["source_integrity_present"])
        self.assertFalse(result["source_integrity_format_valid"])

    def test_09_malformed_source_hash_fails_closed(self):
        artifact = self.fixture()
        artifact["source_integrity_hash"] = "sha256:not-a-digest"
        result = self.evaluate(artifact)
        self.assert_invalid(result, "source_integrity_hash_malformed")
        self.assertTrue(result["source_integrity_present"])
        self.assertFalse(result["source_integrity_format_valid"])

    def test_10_unknown_source_type_is_rejected(self):
        artifact = self.fixture()
        artifact["source_type"] = "trusted-correction"
        result = self.evaluate(artifact)
        self.assert_invalid(result, "source_type_unknown")
        self.assertFalse(result["classification_valid"])

    def test_11_unknown_boundary_is_rejected(self):
        artifact = self.fixture()
        artifact["processing_boundary"] = "global"
        result = self.evaluate(artifact)
        self.assert_invalid(result, "processing_boundary_unknown")
        self.assertFalse(result["boundary_valid"])

    def test_12_external_boundary_requires_explicit_evidence(self):
        artifact = self.fixture()
        artifact["processing_boundary"] = "external"
        artifact["boundary_evidence_reference"] = None
        result = self.evaluate(artifact)
        self.assert_invalid(result, "external_or_public_boundary_evidence_missing")
        self.assertFalse(result["boundary_valid"])

    def test_13_public_boundary_with_explicit_evidence_is_valid(self):
        artifact = self.fixture()
        artifact["retention_boundary"] = "public"
        artifact["boundary_evidence_reference"] = (
            "urn:aaos:m15:boundary-evidence:synthetic-public-evaluation-001"
        )
        result = self.evaluate(artifact)
        self.assert_valid_evidence(result)

    def test_14_unknown_lifecycle_state_is_rejected(self):
        artifact = self.fixture()
        artifact["lifecycle_state"] = "trusted"
        result = self.evaluate(artifact)
        self.assert_invalid(result, "lifecycle_state_unknown")
        self.assertFalse(result["lifecycle_valid"])

    def test_15_unsupported_schema_version_is_rejected(self):
        artifact = self.fixture()
        artifact["schema_version"] = "m15-learning-proof/v2"
        result = self.evaluate(artifact)
        self.assert_invalid(result, "schema_version_missing_or_unsupported")
        self.assertFalse(result["schema_valid"])

    def test_16_explicit_authority_basis_reference_is_required(self):
        artifact = self.fixture()
        artifact["authority_basis_reference"] = ""
        result = self.evaluate(artifact)
        self.assert_invalid(result, "authority_basis_reference_missing")
        self.assertFalse(result["authorization_evidence_valid"])

    def test_17_evaluation_only_plus_memory_conflict_is_rejected(self):
        artifact = self.fixture()
        artifact["authorized_purpose"] = "memory"
        result = self.evaluate(artifact)
        self.assert_invalid(result, "authorization_outcome_and_purpose_conflict")
        self.assertFalse(result["purpose_separation_valid"])

    def test_18_deny_plus_active_conflict_is_rejected(self):
        artifact = self.fixture("denied")
        artifact["lifecycle_state"] = "active"
        result = self.evaluate(artifact)
        self.assert_invalid(result, "denied_or_quarantined_artifact_active")
        self.assertFalse(result["lifecycle_valid"])

    def test_19_quarantine_plus_training_conflict_is_rejected(self):
        artifact = self.fixture("quarantine")
        artifact["requested_purpose"] = "training"
        artifact["authorized_purpose"] = "training"
        result = self.evaluate(artifact)
        self.assert_invalid(result, "authorization_outcome_and_purpose_conflict")
        self.assertIn("inactive_lifecycle_authorizes_new_persistence", result["findings"])
        self.assertFalse(result["purpose_separation_valid"])
        self.assertFalse(result["lifecycle_valid"])

    def test_20_revoked_artifact_cannot_authorize_new_persistence(self):
        artifact = self.fixture()
        artifact.update(
            {
                "requested_purpose": "memory",
                "authorized_purpose": "memory",
                "authorization_outcome": "allow-memory",
                "lifecycle_state": "revoked",
            }
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result, "inactive_lifecycle_authorizes_new_persistence")
        self.assertFalse(result["lifecycle_valid"])

    def test_21_deleted_status_without_deletion_evidence_is_rejected(self):
        artifact = self.fixture()
        artifact["lifecycle_state"] = "deleted"
        artifact["deletion_evidence_reference"] = None
        result = self.evaluate(artifact)
        self.assert_invalid(result, "deletion_evidence_reference_missing")
        self.assertFalse(result["lifecycle_valid"])
        self.assertIs(artifact["authority_claims"]["deletion_executed"], False)

    def test_22_decision_proof_cannot_automatically_become_memory(self):
        artifact = self.fixture()
        artifact["authority_claims"]["decision_proof_to_memory"] = True
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["authority_boundary_valid"])
        self.assertTrue(
            any("decision_proof_to_memory" in item for item in result["findings"]),
            result["findings"],
        )

    def test_23_decision_proof_reference_is_linkage_only_not_memory_authority(self):
        artifact = self.fixture()
        self.assertIsNotNone(artifact["related_decision_proof_reference"])
        result = self.evaluate(artifact)
        self.assert_valid_evidence(result)
        self.assertEqual(result["authorized_purpose"], "evaluation")
        self.assertIn("decision_proof_reference_is_linkage_only", result["findings"])

    def test_24_self_asserted_trusted_marker_never_becomes_authority(self):
        artifact = self.fixture("denied")
        self.assertEqual(artifact["source_self_asserted_trust_marker"], "trusted")
        result = self.evaluate(artifact)
        self.assert_valid_evidence(result)
        self.assertEqual(result["authorization_outcome"], "deny")
        self.assertIsNone(result["authorized_purpose"])
        self.assertIn("self_asserted_trust_marker_ignored", result["findings"])

    def test_25_labels_ownership_verification_and_schema_validity_do_not_infer_authority(self):
        artifact = self.fixture("denied")
        artifact["source_owner"] = "organization"
        artifact["source_self_asserted_trust_marker"] = "reviewer-verified"
        artifact["related_decision_proof_reference"] = (
            "urn:aaos:decision-proof:synthetic-denied-correction-001"
        )
        artifact["evaluator_findings"].extend(
            (
                "synthetic_identity_label_present",
                "synthetic_reviewer_label_present",
                "verification_success_observed",
                "schema_validity_observed",
            )
        )
        result = self.evaluate(artifact)
        self.assert_valid_evidence(result)
        self.assertEqual(result["authorization_outcome"], "deny")
        self.assertIsNone(result["authorized_purpose"])

    def test_26_release_approval_claim_is_rejected(self):
        self.assert_authority_claim_rejected("release_approved")

    def test_27_deployment_approval_claim_is_rejected(self):
        self.assert_authority_claim_rejected("deployment_approved")

    def test_28_execution_authorization_claim_is_rejected(self):
        self.assert_authority_claim_rejected("execution_authorized")

    def test_29_risk_acceptance_claim_is_rejected(self):
        self.assert_authority_claim_rejected("risk_accepted")

    def test_30_rollback_execution_claim_is_rejected(self):
        self.assert_authority_claim_rejected("rollback_executed")

    def test_31_audit_closure_claim_is_rejected(self):
        self.assert_authority_claim_rejected("audit_closed")

    def test_32_waiver_claim_is_rejected(self):
        self.assert_authority_claim_rejected("waiver_granted")

    def test_33_authority_transfer_claim_is_rejected(self):
        self.assert_authority_claim_rejected("authority_transferred")

    def test_34_learning_proof_sealed_claim_is_rejected(self):
        self.assert_authority_claim_rejected("learning_proof_sealed")

    def test_35_decision_proof_sealed_claim_is_rejected(self):
        self.assert_authority_claim_rejected("decision_proof_sealed")

    def test_36_negative_outer_state_cannot_hide_nested_affirmative_authority(self):
        artifact = self.fixture()
        artifact["authority_claims"]["release_approved"] = {
            "status": "denied",
            "nested": {"authority": "granted"},
        }
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["authority_boundary_valid"])
        self.assertTrue(
            any("authority_claims.release_approved" in item for item in result["findings"]),
            result["findings"],
        )
        self.assertTrue(
            any("nested.authority" in item for item in result["findings"]),
            result["findings"],
        )

    def test_37_unknown_nonempty_value_inside_authority_claims_fails_closed(self):
        artifact = self.fixture()
        artifact["authority_claims"]["future_authority_mode"] = "awaiting-council"
        result = self.evaluate(artifact)
        self.assert_invalid(result)
        self.assertFalse(result["authority_boundary_valid"])
        self.assertIn(
            "affirmative_forbidden_claim:authority_claims.future_authority_mode",
            result["findings"],
        )

    def test_38_no_network_access_static_or_behavioral(self):
        imported_roots = set()
        for node in ast.walk(self.evaluator_tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", 1)[0])
        self.assertTrue(
            imported_roots.isdisjoint(
                {"ftplib", "http", "requests", "socket", "urllib"}
            )
        )

        blocked = AssertionError("network access attempted")
        with (
            mock.patch.object(socket, "create_connection", side_effect=blocked),
            mock.patch.object(urllib.request, "urlopen", side_effect=blocked),
        ):
            self.assert_valid_evidence(self.evaluate(self.fixture()))

    def test_39_no_subprocess_or_shell_execution_static_or_behavioral(self):
        imported_roots = set()
        calls = set()
        for node in ast.walk(self.evaluator_tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", 1)[0])
            elif isinstance(node, ast.Call):
                calls.add(dotted_name(node.func))
        self.assertNotIn("subprocess", imported_roots)
        self.assertFalse(
            calls
            & {
                "os.popen",
                "os.system",
                "subprocess.call",
                "subprocess.check_call",
                "subprocess.check_output",
                "subprocess.Popen",
                "subprocess.run",
            }
        )

        blocked = AssertionError("subprocess or shell execution attempted")
        with (
            mock.patch.object(subprocess, "run", side_effect=blocked),
            mock.patch.object(subprocess, "Popen", side_effect=blocked),
            mock.patch.object(subprocess, "check_call", side_effect=blocked),
            mock.patch.object(subprocess, "check_output", side_effect=blocked),
            mock.patch.object(os, "system", side_effect=blocked),
        ):
            self.assert_valid_evidence(self.evaluate(self.fixture()))

    def test_40_no_dynamic_fixture_import_or_file_access_path(self):
        imported_modules = set()
        imported_roots = set()
        call_attributes = set()
        call_names = set()
        direct_call_names = set()
        for node in ast.walk(self.evaluator_tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_modules.add(alias.name)
                    imported_roots.add(alias.name.split(".", 1)[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.add(node.module)
                imported_roots.add(node.module.split(".", 1)[0])
            elif isinstance(node, ast.Call):
                call_names.add(dotted_name(node.func))
                if isinstance(node.func, ast.Attribute):
                    call_attributes.add(node.func.attr)
                elif isinstance(node.func, ast.Name):
                    call_attributes.add(node.func.id)
                    direct_call_names.add(node.func.id)

        self.assertEqual(
            {name for name in imported_modules if name.startswith("runtime.")},
            {"runtime.authority_semantics"},
        )
        self.assertTrue(
            imported_roots.isdisjoint(
                {"importlib", "json", "os", "pathlib", "runpy", "subprocess"}
            )
        )
        self.assertTrue(
            call_attributes.isdisjoint(
                {
                    "__import__",
                    "eval",
                    "exec",
                    "import_module",
                    "open",
                    "read_bytes",
                    "read_text",
                    "run_module",
                    "run_path",
                    "write_bytes",
                    "write_text",
                }
            ),
            call_names,
        )
        self.assertTrue(
            direct_call_names.isdisjoint({"__import__", "compile", "eval", "exec"})
        )

        blocked = AssertionError("dynamic import or file access attempted")
        with (
            mock.patch.object(importlib, "import_module", side_effect=blocked),
            mock.patch.object(runpy, "run_module", side_effect=blocked),
            mock.patch.object(runpy, "run_path", side_effect=blocked),
            mock.patch.object(builtins, "open", side_effect=blocked),
            mock.patch.object(builtins, "__import__", side_effect=blocked),
        ):
            self.assert_valid_evidence(self.evaluate(self.fixture()))

    def test_41_repeated_evaluation_is_deterministic(self):
        for name in FIXTURE_PATHS:
            with self.subTest(name=name):
                first = self.evaluate(self.fixture(name))
                second = self.evaluate(self.fixture(name))
                self.assertEqual(first, second)
                self.assertEqual(first["findings"], sorted(set(first["findings"])))

    def test_42_evaluation_does_not_mutate_input(self):
        for name in FIXTURE_PATHS:
            with self.subTest(name=name):
                artifact = self.fixture(name)
                before = copy.deepcopy(artifact)
                self.evaluate(artifact)
                self.assertEqual(artifact, before)

    def test_43_public_fixtures_contain_no_apparent_credentials_or_personal_data(self):
        forbidden_keys = {
            "access_token",
            "api_key",
            "authorization_header",
            "client_secret",
            "cookie",
            "date_of_birth",
            "email",
            "first_name",
            "full_name",
            "last_name",
            "password",
            "phone",
            "phone_number",
            "postal_address",
            "private_key",
            "raw_authorization_header",
            "ssn",
            "street_address",
        }
        secret_patterns = (
            re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
            re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
            re.compile(r"\bgh[pousr]_[A-Za-z0-9]{16,}\b"),
            re.compile(r"\bgithub_pat_[A-Za-z0-9_]{16,}\b"),
            re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
            re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{12,}"),
        )
        personal_patterns = (
            re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
            re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        )

        def walk(value):
            if isinstance(value, Mapping):
                for key, child in value.items():
                    yield str(key), child
                    yield from walk(child)
            elif isinstance(value, list):
                for child in value:
                    yield from walk(child)

        for name, path in FIXTURE_PATHS.items():
            fixture = self.fixtures[name]
            text = path.read_text(encoding="utf-8")
            with self.subTest(name=name):
                self.assertIn("synthetic", fixture["source_reference"])
                for key, _ in walk(fixture):
                    self.assertNotIn(key.casefold(), forbidden_keys)
                for pattern in secret_patterns + personal_patterns:
                    self.assertIsNone(pattern.search(text), pattern.pattern)

    def test_44_schema_subset_rejects_representative_contract_conflicts(self):
        evaluation_memory = self.fixture()
        evaluation_memory["authorized_purpose"] = "memory"
        self.assertTrue(validate_schema_subset(evaluation_memory, self.schema))

        deleted_without_evidence = self.fixture()
        deleted_without_evidence["lifecycle_state"] = "deleted"
        deleted_without_evidence["deletion_evidence_reference"] = None
        self.assertTrue(validate_schema_subset(deleted_without_evidence, self.schema))

        unknown_top_level = self.fixture()
        unknown_top_level["trusted_by_reviewer"] = True
        self.assertTrue(validate_schema_subset(unknown_top_level, self.schema))

    def test_45_non_authoritative_boundary_statement_is_exact(self):
        expected = (
            "This Learning Proof is evidence only; it grants no persistence, "
            "training, skill, tool, execution, rollback, deletion, sealing, or "
            "governance authority."
        )
        self.assertEqual(NON_AUTHORITATIVE_BOUNDARY_STATEMENT, expected)
        self.assertEqual(
            self.schema["properties"]["non_authoritative_boundary_statement"][
                "const"
            ],
            expected,
        )
        for artifact in self.fixtures.values():
            self.assertEqual(artifact["non_authoritative_boundary_statement"], expected)

    def test_46_detected_contamination_cannot_be_reclassified_as_training(self):
        artifact = self.fixture("quarantine")
        artifact.update(
            {
                "requested_purpose": "training",
                "authorized_purpose": "training",
                "authorization_outcome": "allow-training",
                "lifecycle_state": "verified",
            }
        )
        result = self.evaluate(artifact)
        self.assert_invalid(result, "contamination_requires_quarantine")
        self.assertFalse(result["schema_valid"])
        self.assertFalse(result["contamination_state_valid"])

    def test_47_self_asserted_marker_cannot_be_reused_as_authority_basis(self):
        artifact = self.fixture("denied")
        self_assertion = "urn:aaos:m15:authority-basis:self-asserted-trusted"
        artifact.update(
            {
                "source_self_asserted_trust_marker": self_assertion,
                "authority_basis_reference": self_assertion,
                "requested_purpose": "memory",
                "authorized_purpose": "memory",
                "authorization_outcome": "allow-memory",
                "lifecycle_state": "verified",
            }
        )
        result = self.evaluate(artifact)
        self.assert_invalid(
            result,
            "authority_basis_reuses_non_authoritative_field:"
            "source_self_asserted_trust_marker",
        )
        self.assertFalse(result["authorization_evidence_valid"])

    def test_48_source_reference_cannot_be_reused_as_boundary_evidence(self):
        artifact = self.fixture()
        reused = "urn:aaos:m15:boundary-evidence:source-label-only"
        artifact["source_reference"] = reused
        artifact["processing_boundary"] = "external"
        artifact["boundary_evidence_reference"] = reused
        result = self.evaluate(artifact)
        self.assert_invalid(
            result,
            "boundary_evidence_reuses_non_boundary_field:source_reference",
        )
        self.assertFalse(result["boundary_valid"])

    def test_49_prose_authority_claims_fail_closed(self):
        claims = (
            "release approval granted",
            "deployment approved by reviewer",
            "execution authorized for production",
            "risk acceptance granted",
            "rollback was executed",
            "audit is closed",
            "waiver was granted",
            "authority was transferred",
            "Learning Proof was sealed",
            "Decision Proof was sealed",
            "execution authorization granted",
            "release authorization granted",
            "deployment authorization granted",
            "audit closure granted",
            "authority transfer accepted",
            "Learning Proof sealing completed",
            "Decision Proof sealing confirmed",
            "waiver issued",
        )
        for claim in claims:
            with self.subTest(claim=claim):
                artifact = self.fixture()
                artifact["evaluator_findings"] = [claim]
                result = self.evaluate(artifact)
                self.assert_invalid(result)
                self.assertFalse(result["authority_boundary_valid"])
                self.assertTrue(
                    any(
                        item.startswith("affirmative_forbidden_prose_claim:")
                        or item.startswith("unrecognized_evaluator_finding:")
                        for item in result["findings"]
                    ),
                    result["findings"],
                )

    def test_50_non_string_enum_values_fail_closed_without_exception(self):
        fields = (
            "source_type",
            "source_owner",
            "sensitivity",
            "requested_purpose",
            "authorized_purpose",
            "authorization_outcome",
            "processing_boundary",
            "retention_boundary",
            "lifecycle_state",
        )
        for field in fields:
            with self.subTest(field=field):
                artifact = self.fixture()
                artifact[field] = []
                self.assert_invalid(self.evaluate(artifact))

    def test_51_boundary_statement_drift_is_schema_and_authority_invalid(self):
        artifact = self.fixture()
        artifact["non_authoritative_boundary_statement"] = "evidence"
        result = self.evaluate(artifact)
        self.assert_invalid(result, "non_authoritative_boundary_statement_invalid")
        self.assertFalse(result["schema_valid"])
        self.assertFalse(result["authority_boundary_valid"])

    def test_52_authority_basis_cannot_wrap_trusted_marker_as_suffix(self):
        artifact = self.fixture("denied")
        artifact.update(
            {
                "source_self_asserted_trust_marker": "trusted",
                "authority_basis_reference": (
                    "urn:aaos:m15:authority-basis:trusted"
                ),
                "requested_purpose": "memory",
                "authorized_purpose": "memory",
                "authorization_outcome": "allow-memory",
                "lifecycle_state": "verified",
            }
        )
        result = self.evaluate(artifact)
        self.assert_invalid(
            result,
            "authority_basis_derived_from_self_asserted_trust_marker",
        )
        self.assertFalse(result["authorization_evidence_valid"])

    def test_53_decision_proof_identifier_cannot_be_rewrapped_as_authority(self):
        artifact = self.fixture()
        decision_reference = artifact["related_decision_proof_reference"]
        decision_identifier = decision_reference.rsplit(":", 1)[-1]
        artifact.update(
            {
                "authority_basis_reference": (
                    "urn:aaos:m15:authority-basis:" + decision_identifier
                ),
                "requested_purpose": "memory",
                "authorized_purpose": "memory",
                "authorization_outcome": "allow-memory",
            }
        )
        result = self.evaluate(artifact)
        self.assert_invalid(
            result,
            "authority_basis_derived_from_non_authoritative_field:"
            "related_decision_proof_reference",
        )
        self.assertFalse(result["authorization_evidence_valid"])


if __name__ == "__main__":
    unittest.main()
