import copy
import io
import json
import re
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.external_evidence_admission_evaluator import (  # noqa: E402
    RFC3339_TIMESTAMP_PATTERN,
    evaluate_external_evidence_admission,
    sanitize_external_evidence_record,
)


SCHEMA_PATH = ROOT / "schemas" / "external-evidence-admission.schema.json"
FIXTURE_PATH = (
    ROOT
    / "examples"
    / "external-evidence-admission"
    / "twinkle-hub-fixtures.json"
)
EVALUATOR_PATH = ROOT / "runtime" / "external_evidence_admission_evaluator.py"

TRUSTED_THRESHOLDS = {
    "fixture-current-dataset": 604800,
    "pcc-tender": 2678400,
}


def trusted_policy_for(record, *, stale_result="degraded"):
    return {
        "policy_version": "aaos-external-evidence-admission-v1",
        "freshness_threshold_seconds": TRUSTED_THRESHOLDS.get(
            record.get("dataset_or_paper_identifier"), 0
        ),
        "admission_policy": {
            "stale_freshness_result": stale_result,
            "unknown_freshness_result": "rejected",
            "partial_extraction_result": "degraded",
            "fallback_required_result": "degraded",
        },
    }


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def resolve_ref(root_schema, ref):
    assert ref.startswith("#/"), f"unsupported ref: {ref}"
    value = root_schema
    for part in ref[2:].split("/"):
        value = value[part.replace("~1", "/").replace("~0", "~")]
    return value


def validate_subset(root_schema, schema, instance, path="$"):
    if "$ref" in schema:
        validate_subset(root_schema, resolve_ref(root_schema, schema["$ref"]), instance, path)
        return

    if "not" in schema:
        assert not schema_matches(
            root_schema, schema["not"], instance
        ), f"{path} matches forbidden schema"

    for branch in schema.get("allOf", []):
        condition = branch.get("if")
        if condition is None or schema_matches(root_schema, condition, instance):
            if "then" in branch:
                validate_subset(root_schema, branch["then"], instance, path)

    schema_type = schema.get("type")
    if schema_type is None and any(
        keyword in schema
        for keyword in ("properties", "required", "additionalProperties")
    ):
        schema_type = "object"
    if schema_type is None and any(
        keyword in schema for keyword in ("pattern", "minLength", "format")
    ):
        schema_type = "string"
    if isinstance(schema_type, list):
        errors = []
        for candidate_type in schema_type:
            try:
                validate_subset(
                    root_schema,
                    {**schema, "type": candidate_type},
                    instance,
                    path,
                )
                return
            except AssertionError as exc:
                errors.append(str(exc))
        raise AssertionError(f"{path} does not match any allowed type: {errors}")

    if schema_type == "object":
        assert isinstance(instance, dict), f"{path} must be object"
        for required in schema.get("required", []):
            assert required in instance, f"{path}.{required} is required"
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = set(instance) - set(properties)
            assert not extra, f"{path} has unexpected keys: {sorted(extra)}"
        for key, property_schema in properties.items():
            if key in instance:
                validate_subset(
                    root_schema,
                    property_schema,
                    instance[key],
                    f"{path}.{key}",
                )

    elif schema_type == "array":
        assert isinstance(instance, list), f"{path} must be array"
        if "minItems" in schema:
            assert len(instance) >= schema["minItems"], f"{path} has too few items"
        for index, item in enumerate(instance):
            if "items" in schema:
                validate_subset(
                    root_schema,
                    schema["items"],
                    item,
                    f"{path}[{index}]",
                )

    elif schema_type == "string":
        assert isinstance(instance, str), f"{path} must be string"
        if "minLength" in schema:
            assert len(instance) >= schema["minLength"], f"{path} is too short"
        if "pattern" in schema:
            assert re.fullmatch(schema["pattern"], instance), f"{path} has invalid format"
        if schema.get("format") == "date-time":
            normalized = (
                instance[:-1] + "+00:00"
                if instance.endswith(("Z", "z"))
                else instance
            )
            if len(normalized) > 10 and normalized[10] == "t":
                normalized = normalized[:10] + "T" + normalized[11:]
            try:
                parsed = datetime.fromisoformat(normalized)
            except ValueError as exc:
                raise AssertionError(f"{path} must be date-time") from exc
            assert parsed.tzinfo is not None, f"{path} must include timezone"

    elif schema_type == "integer":
        assert isinstance(instance, int) and not isinstance(
            instance, bool
        ), f"{path} must be integer"
        if "minimum" in schema:
            assert instance >= schema["minimum"], f"{path} is below minimum"

    elif schema_type == "boolean":
        assert isinstance(instance, bool), f"{path} must be boolean"

    elif schema_type == "null":
        assert instance is None, f"{path} must be null"

    if "const" in schema:
        assert instance == schema["const"], f"{path} must equal {schema['const']}"
    if "enum" in schema:
        assert instance in schema["enum"], f"{path} must be one of {schema['enum']}"


def schema_matches(root_schema, schema, instance):
    try:
        validate_subset(root_schema, schema, instance)
    except AssertionError:
        return False
    return True


class ExternalEvidenceAdmissionEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.schema = load_json(SCHEMA_PATH)
        self.fixture_set = load_json(FIXTURE_PATH)
        self.fixtures = {
            fixture["evidence_id"]: fixture
            for fixture in self.fixture_set["fixture_cases"]
        }

    def fixture(self, evidence_id):
        return copy.deepcopy(self.fixtures[evidence_id])

    def evaluate_record(self, fixture, *, stale_result="degraded"):
        return evaluate_external_evidence_admission(
            fixture,
            trusted_policy=trusted_policy_for(
                fixture, stale_result=stale_result
            ),
        )

    def evaluate(self, evidence_id):
        return self.evaluate_record(self.fixture(evidence_id))

    def test_fixtures_are_deterministic_schema_valid_and_offline(self):
        self.assertTrue(self.fixture_set["deterministic"])
        self.assertFalse(self.fixture_set["live_hub_calls"])
        self.assertEqual(
            self.fixture_set["upstream_issue_references"],
            [
                "https://github.com/ai-twinkle/Hub/issues/6",
                "https://github.com/ai-twinkle/Hub/issues/7",
                "https://github.com/ai-twinkle/Hub/issues/8",
            ],
        )

        for fixture in self.fixture_set["fixture_cases"]:
            with self.subTest(evidence_id=fixture["evidence_id"]):
                validate_subset(self.schema, self.schema, fixture)
                result = self.evaluate_record(fixture)
                self.assertTrue(result["external_evidence_admission_valid"])
                self.assertEqual(result["admission_findings"], [])

    def test_verified_evidence_is_eligible_but_not_sealed_by_evaluator(self):
        result = self.evaluate("hub-admission-verified-baseline-001")

        self.assertEqual(result["admission_result"], "verified")
        self.assertTrue(result["connection_assessment"]["passed"])
        self.assertTrue(result["freshness_assessment"]["passed"])
        self.assertTrue(result["extraction_assessment"]["passed"])
        self.assertTrue(result["decision_path_eligible"])
        self.assertTrue(result["decision_proof_sealing_eligible"])
        self.assertNotIn("decision_proof_sealed", result)
        self.assertNotIn("sealed_by_evaluator", result)

    def test_schema_valid_timestamps_canonicalize_without_rejection(self):
        timestamp_cases = [
            (
                "z",
                "2026-07-11T00:00:00Z",
                "2026-07-05T00:00:00Z",
                "2026-07-11T00:00:00Z",
                "2026-07-05T00:00:00Z",
            ),
            (
                "utc_offset",
                "2026-07-11T00:00:00+00:00",
                "2026-07-05T00:00:00+00:00",
                "2026-07-11T00:00:00Z",
                "2026-07-05T00:00:00Z",
            ),
            (
                "non_utc_offset",
                "2026-07-11T08:00:00+08:00",
                "2026-07-05T08:00:00+08:00",
                "2026-07-11T00:00:00Z",
                "2026-07-05T00:00:00Z",
            ),
            (
                "negative_known_offset",
                "2026-07-11T00:00:00-04:00",
                "2026-07-05T00:00:00-04:00",
                "2026-07-11T04:00:00Z",
                "2026-07-05T04:00:00Z",
            ),
            (
                "lowercase_designators",
                "2026-07-11t00:00:00z",
                "2026-07-05t00:00:00z",
                "2026-07-11T00:00:00Z",
                "2026-07-05T00:00:00Z",
            ),
            (
                "fractional_seconds",
                "2026-07-11T00:00:00.250001+00:00",
                "2026-07-05T00:00:00.125001+00:00",
                "2026-07-11T00:00:00.250001Z",
                "2026-07-05T00:00:00.125001Z",
            ),
        ]

        for (
            name,
            retrieved_at,
            source_published_at,
            expected_retrieved_at,
            expected_source_published_at,
        ) in timestamp_cases:
            with self.subTest(name=name):
                fixture = self.fixture("hub-admission-verified-baseline-001")
                fixture["retrieved_at"] = retrieved_at
                fixture["source_published_at"] = source_published_at

                validate_subset(self.schema, self.schema, fixture)
                result = self.evaluate_record(fixture)

                self.assertTrue(result["external_evidence_admission_valid"])
                self.assertEqual(result["admission_result"], "verified")
                self.assertEqual(result["admission_findings"], [])
                self.assertEqual(
                    result["storage_record"]["retrieved_at"],
                    expected_retrieved_at,
                )
                self.assertEqual(
                    result["storage_record"]["source_published_at"],
                    expected_source_published_at,
                )
                self.assertTrue(result["decision_path_eligible"])
                self.assertTrue(result["decision_proof_sealing_eligible"])

    def test_known_offset_profile_rejects_unknown_offset_and_unsupported_time(self):
        retrieved_pattern = self.schema["properties"]["retrieved_at"]["pattern"]
        published_pattern = self.schema["properties"]["source_published_at"][
            "pattern"
        ]
        self.assertEqual(retrieved_pattern, published_pattern)
        self.assertEqual(retrieved_pattern, RFC3339_TIMESTAMP_PATTERN.pattern)
        self.assertIsNone(
            re.search(retrieved_pattern, "2026-07-11T00:00:00Z\n")
        )
        self.assertIsNone(
            re.search(retrieved_pattern, "2026-07-11T00:00:00Z\r")
        )

        timestamp_cases = [
            (
                "unknown_retrieved_at",
                "retrieved_at",
                "2026-07-11T00:00:00-00:00",
                "2026-07-11T00:00:00Z",
                "unknown_local_offset_not_allowed",
            ),
            (
                "unknown_source_published_at",
                "source_published_at",
                "2026-07-05T00:00:00-00:00",
                "2026-07-05T00:00:00Z",
                "unknown_local_offset_not_allowed",
            ),
            (
                "leap_second_retrieved_at",
                "retrieved_at",
                "2026-07-11T00:00:60Z",
                None,
                "unexpected_or_unsafe_field_removed",
            ),
            (
                "leap_second_source_published_at",
                "source_published_at",
                "2026-07-05T00:00:60Z",
                None,
                "unexpected_or_unsafe_field_removed",
            ),
            (
                "over_precision_retrieved_at",
                "retrieved_at",
                "2026-07-11T00:00:00.1234567Z",
                None,
                "unexpected_or_unsafe_field_removed",
            ),
            (
                "over_precision_source_published_at",
                "source_published_at",
                "2026-07-05T00:00:00.1234567Z",
                None,
                "unexpected_or_unsafe_field_removed",
            ),
        ]

        for name, field, value, promoted_value, expected_finding in timestamp_cases:
            with self.subTest(name=name):
                fixture = self.fixture("hub-admission-verified-baseline-001")
                fixture[field] = value

                with self.assertRaises(AssertionError):
                    validate_subset(self.schema, self.schema, fixture)

                result = self.evaluate_record(fixture)
                serialized = json.dumps(result, sort_keys=True)

                self.assertTrue(result["external_evidence_admission_invalid"])
                self.assertEqual(result["admission_result"], "rejected")
                self.assertIn(expected_finding, result["admission_findings"])
                self.assertNotIn(value, serialized)
                if promoted_value is not None:
                    self.assertNotEqual(
                        result["storage_record"][field],
                        promoted_value,
                    )
                self.assertFalse(result["decision_path_eligible"])
                self.assertFalse(result["decision_proof_sealing_eligible"])

    def test_malformed_and_timezone_naive_timestamps_fail_closed(self):
        timestamp_cases = [
            ("malformed_retrieved_at", "retrieved_at", "not-a-date"),
            (
                "naive_retrieved_at_matching_fallback",
                "retrieved_at",
                "1970-01-01T00:00:00",
            ),
            (
                "non_rfc3339_retrieved_at",
                "retrieved_at",
                "2026-07-11 00:00:00+00:00",
            ),
            (
                "out_of_range_hour",
                "retrieved_at",
                "2026-07-11T24:00:00Z",
            ),
            (
                "out_of_range_offset_minute",
                "retrieved_at",
                "2026-07-11T00:00:00+00:60",
            ),
            (
                "out_of_range_offset_hour",
                "retrieved_at",
                "2026-07-11T00:00:00+24:00",
            ),
            (
                "malformed_source_published_at",
                "source_published_at",
                "not-a-date",
            ),
            (
                "naive_source_published_at",
                "source_published_at",
                "2026-07-05T00:00:00",
            ),
        ]

        for name, field, value in timestamp_cases:
            with self.subTest(name=name):
                fixture = self.fixture("hub-issue-6-partial-extraction-001")
                fixture[field] = value

                result = self.evaluate_record(fixture)

                self.assertTrue(result["external_evidence_admission_invalid"])
                self.assertEqual(result["admission_result"], "rejected")
                self.assertIn(
                    "unexpected_or_unsafe_field_removed",
                    result["admission_findings"],
                )
                self.assertFalse(result["decision_path_eligible"])
                self.assertFalse(result["decision_proof_sealing_eligible"])

    def test_timestamp_normalization_does_not_weaken_unsafe_change_detection(self):
        canary = "timestamp-canonicalization-secret-canary"
        mutation_cases = [
            (
                "secret_field",
                lambda item: item.update(access_token=canary),
                "secret_material_removed",
            ),
            (
                "unexpected_top_level_field",
                lambda item: item.update(debug_note="unexpected-field"),
                "unexpected_or_unsafe_field_removed",
            ),
            (
                "unexpected_nested_field",
                lambda item: item["source_identity"].update(
                    debug_note="unexpected-field"
                ),
                "unexpected_or_unsafe_field_removed",
            ),
            (
                "integer_for_boolean",
                lambda item: item.update(retrieval_succeeded=1),
                "unexpected_or_unsafe_field_removed",
            ),
            (
                "float_for_integer",
                lambda item: item.update(freshness_threshold_seconds=604800.0),
                "unexpected_or_unsafe_field_removed",
            ),
            (
                "boolean_for_integer",
                lambda item: item["extraction_metrics"].update(
                    item_count_reported=False
                ),
                "unexpected_or_unsafe_field_removed",
            ),
            (
                "unsupported_source_id_sentinel",
                lambda item: item["source_identity"].update(
                    source_id="redacted-source"
                ),
                "unexpected_or_unsafe_field_removed",
            ),
            (
                "unsupported_source_name_sentinel",
                lambda item: item["source_identity"].update(
                    source_name="redacted-source"
                ),
                "unexpected_or_unsafe_field_removed",
            ),
            (
                "unsupported_endpoint_sentinel",
                lambda item: item["source_identity"].update(
                    endpoint_reference=(
                        "urn:aaos:redacted:unsafe-endpoint-reference"
                    )
                ),
                "unexpected_or_unsafe_field_removed",
            ),
            (
                "unsupported_client_sentinel",
                lambda item: item["source_identity"].update(
                    client_type="redacted-client"
                ),
                "unexpected_or_unsafe_field_removed",
            ),
            (
                "unsupported_authentication_sentinel",
                lambda item: item["source_identity"].update(
                    authentication_mode="redacted-authentication-mode"
                ),
                "unexpected_or_unsafe_field_removed",
            ),
            (
                "unsafe_authoritative_reference_sentinel",
                lambda item: item.update(
                    authoritative_source_reference=(
                        "urn:aaos:redacted:unsafe-authoritative-reference"
                    )
                ),
                "unexpected_or_unsafe_field_removed",
            ),
            (
                "unsafe_raw_reference_sentinel",
                lambda item: item.update(
                    raw_or_pdf_fallback_reference=(
                        "not_available:unsafe_reference_removed"
                    )
                ),
                "unexpected_or_unsafe_field_removed",
            ),
            (
                "invalid_evidence_id_sentinel",
                lambda item: item.update(evidence_id="hub-invalid-evidence-id"),
                "unexpected_or_unsafe_field_removed",
            ),
            (
                "redacted_dataset_identifier_sentinel",
                lambda item: item.update(
                    dataset_or_paper_identifier="redacted-dataset-or-paper"
                ),
                "unexpected_or_unsafe_field_removed",
            ),
            (
                "redacted_source_batch_sentinel",
                lambda item: item.update(
                    source_batch_or_version="redacted-source-batch"
                ),
                "unexpected_or_unsafe_field_removed",
            ),
        ]

        for name, mutate, expected_finding in mutation_cases:
            with self.subTest(name=name):
                fixture = self.fixture("hub-admission-verified-baseline-001")
                fixture["retrieved_at"] = "2026-07-11T08:00:00+08:00"
                mutate(fixture)

                result = self.evaluate_record(fixture)
                serialized = json.dumps(result, sort_keys=True)

                self.assertTrue(result["external_evidence_admission_invalid"])
                self.assertEqual(result["admission_result"], "rejected")
                self.assertIn(expected_finding, result["admission_findings"])
                self.assertNotIn(canary, serialized)
                self.assertNotIn("debug_note", serialized)
                self.assertFalse(result["decision_path_eligible"])
                self.assertFalse(result["decision_proof_sealing_eligible"])

    def test_only_verified_evidence_may_be_sealing_eligible(self):
        for fixture in self.fixture_set["fixture_cases"]:
            with self.subTest(evidence_id=fixture["evidence_id"]):
                result = self.evaluate_record(fixture)
                if result["decision_proof_sealing_eligible"]:
                    self.assertEqual(result["admission_result"], "verified")
                if result["admission_result"] != "verified":
                    self.assertFalse(result["decision_proof_sealing_eligible"])

    def test_successful_retrieval_alone_does_not_imply_verified_evidence(self):
        evidence_ids = [
            "hub-issue-6-partial-extraction-001",
            "hub-issue-6-empty-extraction-001",
            "hub-issue-7-stale-dataset-001",
        ]

        for evidence_id in evidence_ids:
            with self.subTest(evidence_id=evidence_id):
                fixture = self.fixture(evidence_id)
                self.assertTrue(fixture["retrieval_succeeded"])
                result = self.evaluate_record(fixture)
                self.assertTrue(result["connection_assessment"]["passed"])
                self.assertNotEqual(result["admission_result"], "verified")
                self.assertFalse(result["decision_proof_sealing_eligible"])

    def test_stale_evidence_is_degraded_by_default_policy(self):
        result = self.evaluate("hub-issue-7-stale-dataset-001")

        self.assertEqual(result["freshness_assessment"]["status"], "stale")
        self.assertEqual(result["admission_result"], "degraded")
        self.assertTrue(result["degraded_storage_allowed"])
        self.assertEqual(result["storage_disposition"], "inspection_only")
        self.assertFalse(result["decision_path_eligible"])
        self.assertFalse(result["decision_proof_sealing_eligible"])
        self.assertIn("source_batch_stale", result["explicit_warnings"])

    def test_stale_evidence_is_rejected_by_strict_policy(self):
        fixture = self.fixture("hub-issue-7-stale-dataset-001")
        fixture["admission_policy"]["stale_freshness_result"] = "rejected"
        fixture["admission_result"] = "rejected"
        fixture["storage_disposition"] = "replay_metadata_only"

        result = self.evaluate_record(fixture, stale_result="rejected")

        self.assertTrue(result["external_evidence_admission_valid"])
        self.assertEqual(result["admission_result"], "rejected")
        self.assertTrue(result["rejected_from_governed_decision_path"])
        self.assertFalse(result["decision_path_eligible"])

    def test_partial_extraction_is_inspection_only_with_raw_pdf_reference(self):
        result = self.evaluate("hub-issue-6-partial-extraction-001")

        self.assertEqual(result["extraction_assessment"]["status"], "partial")
        self.assertEqual(result["admission_result"], "degraded")
        self.assertTrue(result["degraded_storage_allowed"])
        self.assertTrue(result["storage_record"]["raw_or_pdf_fallback_reference"])
        self.assertIn("raw_pdf_fallback_required", result["explicit_warnings"])
        self.assertFalse(result["decision_proof_sealing_eligible"])

    def test_empty_extraction_cannot_be_sealed_as_verified(self):
        result = self.evaluate("hub-issue-6-empty-extraction-001")

        self.assertEqual(result["extraction_assessment"]["status"], "empty")
        self.assertEqual(result["admission_result"], "rejected")
        self.assertFalse(result["decision_path_eligible"])
        self.assertFalse(result["decision_proof_sealing_eligible"])
        self.assertEqual(
            result["replay_failure_classification"]["extraction_failure"],
            "empty_extraction",
        )

    def test_incomplete_extraction_claimed_as_verified_fails_closed(self):
        fixture = self.fixture("hub-issue-6-partial-extraction-001")
        fixture["admission_result"] = "verified"
        fixture["decision_path_eligible"] = True
        fixture["decision_proof_sealing_eligible"] = True
        fixture["storage_disposition"] = "verified_evidence"

        result = self.evaluate_record(fixture)

        self.assertTrue(result["external_evidence_admission_invalid"])
        self.assertEqual(result["admission_result"], "rejected")
        self.assertFalse(result["decision_path_eligible"])
        self.assertFalse(result["decision_proof_sealing_eligible"])
        self.assertIn(
            "admission_result_more_permissive_than_policy",
            result["admission_findings"],
        )
        self.assertEqual(
            result["replay_failure_classification"]["governance_failure"],
            "governance_policy_failure",
        )

    def test_degraded_evidence_requires_warning_and_raw_source_reference(self):
        fixture = self.fixture("hub-issue-6-partial-extraction-001")
        fixture["explicit_warnings"] = []
        fixture["extraction_metrics"]["raw_source_available"] = False
        fixture["raw_or_pdf_fallback_reference"] = "not_available:no_raw_source"

        result = self.evaluate_record(fixture)

        self.assertEqual(result["admission_result"], "rejected")
        self.assertIn(
            "degraded_evidence_missing_explicit_warning",
            result["admission_findings"],
        )
        self.assertIn(
            "degraded_evidence_missing_raw_source_reference",
            result["admission_findings"],
        )
        self.assertFalse(result["decision_proof_sealing_eligible"])

    def test_self_downgrade_cannot_bypass_degraded_storage_requirements(self):
        fixture = self.fixture("hub-admission-verified-baseline-001")
        fixture["admission_result"] = "degraded"
        fixture["decision_path_eligible"] = False
        fixture["decision_proof_sealing_eligible"] = False
        fixture["storage_disposition"] = "inspection_only"
        fixture["explicit_warnings"] = []
        fixture["extraction_metrics"]["raw_source_available"] = False
        fixture[
            "raw_or_pdf_fallback_reference"
        ] = "not_available:no_degradation_source"

        result = self.evaluate_record(fixture)

        self.assertTrue(result["external_evidence_admission_invalid"])
        self.assertEqual(result["admission_result"], "rejected")
        self.assertIn(
            "degraded_evidence_missing_explicit_warning",
            result["admission_findings"],
        )
        self.assertIn(
            "degraded_evidence_missing_raw_source_reference",
            result["admission_findings"],
        )
        self.assertIn(
            "degraded_evidence_missing_dimension_reason",
            result["admission_findings"],
        )

    def test_candidate_cannot_override_trusted_threshold_or_policy(self):
        fixture = self.fixture("hub-issue-7-stale-dataset-001")
        fixture["freshness_threshold_seconds"] = 999999999
        fixture["freshness_status"] = "current"
        fixture["sanitized_error_category"] = "none"
        fixture["replay_failure_classification"]["source_failure"] = "none"
        fixture["admission_result"] = "verified"
        fixture["decision_path_eligible"] = True
        fixture["decision_proof_sealing_eligible"] = True
        fixture["storage_disposition"] = "verified_evidence"

        result = self.evaluate_record(fixture)

        self.assertTrue(result["external_evidence_admission_invalid"])
        self.assertEqual(result["freshness_assessment"]["status"], "stale")
        self.assertEqual(result["admission_result"], "rejected")
        self.assertIn("policy_snapshot_mismatch", result["admission_findings"])
        self.assertEqual(
            result["storage_record"]["freshness_threshold_seconds"],
            2678400,
        )

    def test_schema_invalid_source_identity_and_kind_fail_closed(self):
        mutations = [
            ("source_type", lambda item: item["source_identity"].update(source_type="not-mcp")),
            ("evidence_kind", lambda item: item.update(evidence_kind="mutable_dataset_v2")),
        ]

        for name, mutate in mutations:
            with self.subTest(name=name):
                fixture = self.fixture("hub-admission-verified-baseline-001")
                mutate(fixture)

                result = self.evaluate_record(fixture)

                self.assertTrue(result["external_evidence_admission_invalid"])
                self.assertEqual(result["admission_result"], "rejected")
                self.assertFalse(result["decision_path_eligible"])
                self.assertFalse(result["decision_proof_sealing_eligible"])
                self.assertIn(
                    "unexpected_or_unsafe_field_removed",
                    result["admission_findings"],
                )

    def test_failure_error_categories_require_matching_replay_domain(self):
        for error_category in (
            "freshness_check_failed",
            "extraction_integrity_failed",
            "model_interpretation_failed",
            "governance_policy_failed",
        ):
            with self.subTest(error_category=error_category):
                fixture = self.fixture("hub-admission-verified-baseline-001")
                fixture["sanitized_error_category"] = error_category

                result = self.evaluate_record(fixture)

                self.assertTrue(result["external_evidence_admission_invalid"])
                self.assertEqual(result["admission_result"], "rejected")
                self.assertIn(
                    "error_failure_classification_mismatch",
                    result["admission_findings"],
                )
                self.assertFalse(result["decision_proof_sealing_eligible"])

    def test_ready_retrieval_with_skipped_extraction_requires_fallback(self):
        fixture = self.fixture("hub-issue-8-oauth-failure-001")
        fixture["evidence_id"] = "hub-ready-extraction-not-attempted-001"
        fixture["dataset_or_paper_identifier"] = "ready-extraction-not-attempted"
        fixture["retrieval_succeeded"] = True
        fixture["connection_status"] = "ready"
        fixture["sanitized_error_category"] = "extraction_integrity_failed"
        fixture["explicit_warnings"] = ["raw_pdf_fallback_required"]
        fixture["extraction_metrics"]["raw_source_available"] = True
        fixture[
            "raw_or_pdf_fallback_reference"
        ] = "fixture://ready-source/raw-document.pdf"
        fixture["replay_failure_classification"]["source_failure"] = "none"
        fixture["replay_failure_classification"][
            "extraction_failure"
        ] = "fallback_required"
        fixture["admission_result"] = "degraded"
        fixture["storage_disposition"] = "inspection_only"

        result = self.evaluate_record(fixture)

        self.assertTrue(result["external_evidence_admission_valid"])
        self.assertEqual(result["admission_result"], "degraded")
        self.assertEqual(
            result["replay_failure_classification"]["extraction_failure"],
            "fallback_required",
        )
        self.assertFalse(result["decision_proof_sealing_eligible"])

    def test_auth_failure_is_distinguishable_from_source_absence(self):
        auth_result = self.evaluate("hub-issue-8-oauth-failure-001")

        source_absence = self.fixture("hub-issue-8-oauth-failure-001")
        source_absence["evidence_id"] = "hub-source-absence-001"
        source_absence["dataset_or_paper_identifier"] = "missing-source"
        source_absence["retrieval_succeeded"] = True
        source_absence["connection_status"] = "ready"
        source_absence["sanitized_error_category"] = "source_not_found"
        source_absence["explicit_warnings"] = ["source_not_found"]
        source_absence[
            "raw_or_pdf_fallback_reference"
        ] = "not_available:source_not_found"
        source_absence["replay_failure_classification"][
            "source_failure"
        ] = "source_absence"

        source_absence_result = self.evaluate_record(source_absence)

        self.assertTrue(source_absence_result["external_evidence_admission_valid"])
        self.assertEqual(
            auth_result["replay_failure_classification"]["source_failure"],
            "authentication_failure",
        )
        self.assertEqual(
            source_absence_result["replay_failure_classification"]["source_failure"],
            "source_absence",
        )
        self.assertNotEqual(
            auth_result["connection_assessment"]["status"],
            source_absence_result["connection_assessment"]["status"],
        )
        self.assertEqual(
            auth_result["replay_failure_classification"]["extraction_failure"],
            "none",
        )

    def test_replay_records_distinguish_all_failure_domains(self):
        source_result = self.evaluate("hub-issue-8-oauth-failure-001")
        extraction_result = self.evaluate("hub-issue-6-empty-extraction-001")

        model_fixture = self.fixture("hub-admission-verified-baseline-001")
        model_fixture["replay_failure_classification"][
            "model_failure"
        ] = "model_interpretation_failure"
        model_fixture[
            "sanitized_error_category"
        ] = "model_interpretation_failed"
        model_fixture["decision_path_eligible"] = False
        model_fixture["decision_proof_sealing_eligible"] = False
        model_result = self.evaluate_record(model_fixture)

        governance_fixture = self.fixture("hub-admission-verified-baseline-001")
        governance_fixture["replay_failure_classification"][
            "governance_failure"
        ] = "governance_policy_failure"
        governance_fixture[
            "sanitized_error_category"
        ] = "governance_policy_failed"
        governance_fixture["decision_path_eligible"] = False
        governance_fixture["decision_proof_sealing_eligible"] = False
        governance_result = self.evaluate_record(governance_fixture)

        self.assertTrue(model_result["external_evidence_admission_valid"])
        self.assertTrue(governance_result["external_evidence_admission_valid"])
        self.assertEqual(
            source_result["replay_failure_classification"]["source_failure"],
            "authentication_failure",
        )
        self.assertEqual(
            extraction_result["replay_failure_classification"]["extraction_failure"],
            "empty_extraction",
        )
        self.assertEqual(
            model_result["replay_failure_classification"]["model_failure"],
            "model_interpretation_failure",
        )
        self.assertEqual(
            governance_result["replay_failure_classification"][
                "governance_failure"
            ],
            "governance_policy_failure",
        )
        self.assertFalse(model_result["decision_path_eligible"])
        self.assertFalse(governance_result["decision_proof_sealing_eligible"])

    def test_rejected_evidence_never_influences_governed_decision_path(self):
        for evidence_id in [
            "hub-issue-6-empty-extraction-001",
            "hub-issue-8-oauth-failure-001",
        ]:
            with self.subTest(evidence_id=evidence_id):
                result = self.evaluate(evidence_id)
                self.assertEqual(result["admission_result"], "rejected")
                self.assertTrue(result["rejected_from_governed_decision_path"])
                self.assertFalse(result["decision_path_eligible"])
                self.assertFalse(result["decision_proof_sealing_eligible"])

    def test_claimed_status_mismatch_fails_closed(self):
        fixture = self.fixture("hub-issue-7-stale-dataset-001")
        fixture["freshness_status"] = "current"

        result = self.evaluate_record(fixture)

        self.assertTrue(result["external_evidence_admission_invalid"])
        self.assertEqual(result["admission_result"], "rejected")
        self.assertEqual(result["freshness_assessment"]["status"], "stale")
        self.assertIn("freshness_status_mismatch", result["admission_findings"])

    def test_replay_safe_metadata_is_preserved(self):
        fixture = self.fixture("hub-issue-7-stale-dataset-001")
        result = self.evaluate_record(fixture)
        stored = result["storage_record"]

        required_metadata = {
            "source_identity",
            "dataset_or_paper_identifier",
            "retrieved_at",
            "source_batch_or_version",
            "authoritative_source_reference",
            "connection_status",
            "freshness_status",
            "extraction_status",
            "admission_result",
            "sanitized_error_category",
            "raw_or_pdf_fallback_reference",
            "replay_failure_classification",
        }
        self.assertTrue(required_metadata.issubset(stored))
        self.assertEqual(stored["source_batch_or_version"], "20260302")

    def test_secret_material_is_absent_from_logs_serialization_and_errors(self):
        canary = "credential" + "-canary-issue-37"
        fixture = self.fixture("hub-admission-verified-baseline-001")
        fixture["access_token"] = canary
        fixture["authorization_code"] = canary
        fixture["client_secret"] = canary
        fixture["cookies"] = canary
        fixture["source_identity"]["raw_authorization_header"] = (
            f"Bearer {canary}"
        )
        fixture["source_identity"]["raw_authorization_headers"] = [
            f"Basic {canary}"
        ]
        fixture["source_identity"][
            "endpoint_reference"
        ] = f"https://example.invalid/mcp?access_token={canary}"

        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = self.evaluate_record(fixture)

        serialized = json.dumps(result, sort_keys=True)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "")
        self.assertNotIn(canary, serialized)
        self.assertNotIn(f"Bearer {canary}", serialized)
        self.assertNotIn(canary, str(result["admission_findings"]))
        self.assertTrue(result["external_evidence_admission_invalid"])
        self.assertEqual(result["admission_result"], "rejected")
        self.assertIn("secret_material_removed", result["admission_findings"])

    def test_all_persisted_fields_are_canonicalized_before_serialization(self):
        canary = "opaque-canary-value-issue-37"
        variants = []

        invalid_connection = self.fixture("hub-admission-verified-baseline-001")
        invalid_connection["connection_status"] = canary
        variants.append(invalid_connection)

        json_reference = self.fixture("hub-admission-verified-baseline-001")
        json_reference["source_identity"]["endpoint_reference"] = json.dumps(
            {"client_secret": canary}
        )
        variants.append(json_reference)

        skipped_freshness = self.fixture("hub-issue-6-partial-extraction-001")
        skipped_freshness["source_published_at"] = json.dumps(
            {"authorization_code": canary}
        )
        variants.append(skipped_freshness)

        skipped_extraction = self.fixture("hub-issue-8-oauth-failure-001")
        skipped_extraction["extraction_metrics"]["item_count_reported"] = json.dumps(
            {"access_token": canary}
        )
        variants.append(skipped_extraction)

        oauth_path = self.fixture("hub-admission-verified-baseline-001")
        oauth_path["source_identity"][
            "endpoint_reference"
        ] = f"https://example.invalid/ya29.{canary}"
        variants.append(oauth_path)

        oauth_source_name = self.fixture("hub-admission-verified-baseline-001")
        oauth_source_name["source_identity"]["source_name"] = f"ya29.{canary}"
        variants.append(oauth_source_name)

        client_secret_shape = self.fixture("hub-admission-verified-baseline-001")
        client_secret_shape["source_identity"]["client_type"] = f"GOCSPX-{canary}"
        variants.append(client_secret_shape)

        authorization_code_shape = self.fixture(
            "hub-admission-verified-baseline-001"
        )
        authorization_code_shape["source_identity"][
            "authentication_mode"
        ] = f"4/{canary}"
        variants.append(authorization_code_shape)

        cookie_shape = self.fixture("hub-admission-verified-baseline-001")
        cookie_shape["evidence_id"] = f"sessionid{canary}"
        variants.append(cookie_shape)

        for fixture in variants:
            with self.subTest(evidence_id=fixture["evidence_id"]):
                result = self.evaluate_record(fixture)
                serialized = json.dumps(result, sort_keys=True)

                self.assertNotIn(canary, serialized)
                self.assertTrue(result["external_evidence_admission_invalid"])
                self.assertEqual(result["admission_result"], "rejected")

    def test_hostile_mapping_exception_is_not_exposed(self):
        canary = "hostile-mapping-canary-37"

        class HostileMapping(dict):
            def items(self):
                raise RuntimeError(canary)

        result = evaluate_external_evidence_admission(
            HostileMapping(),
            trusted_policy=trusted_policy_for({}),
        )

        serialized = json.dumps(result, sort_keys=True)
        self.assertNotIn(canary, serialized)
        self.assertEqual(result["admission_result"], "rejected")
        self.assertIn("unsafe_input_rejected", result["admission_findings"])

    def test_malformed_candidates_fail_closed_without_echoing_secret_material(self):
        canary = "malformed" + "-credential-canary-37"
        candidates = [
            {"access_token": canary},
            [f"Authorization: Bearer {canary}"],
            {
                "source_identity": {
                    "endpoint_reference": f"https://fixture:{canary}@example.invalid/mcp"
                }
            },
            {"source_identity": {"source_name": f"Basic {canary}"}},
        ]

        for candidate in candidates:
            with self.subTest(candidate_type=type(candidate).__name__):
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    result = evaluate_external_evidence_admission(
                        candidate,
                        trusted_policy=trusted_policy_for({}),
                    )

                serialized = json.dumps(result, sort_keys=True)
                self.assertEqual(stdout.getvalue(), "")
                self.assertEqual(stderr.getvalue(), "")
                self.assertNotIn(canary, serialized)
                self.assertEqual(result["admission_result"], "rejected")
                self.assertFalse(result["decision_path_eligible"])
                self.assertFalse(result["decision_proof_sealing_eligible"])

    def test_checked_in_fixtures_contain_no_secret_material(self):
        fixture_text = FIXTURE_PATH.read_text(encoding="utf-8").lower()
        forbidden_names = {
            "access_token",
            "authorization_code",
            "client_secret",
            "raw_authorization_header",
            "raw_authorization_headers",
            "\"cookie\"",
            "\"cookies\"",
        }
        for forbidden in forbidden_names:
            self.assertNotIn(forbidden, fixture_text)

        for fixture in self.fixture_set["fixture_cases"]:
            self.assertEqual(sanitize_external_evidence_record(fixture), fixture)

    def test_schema_validator_enforces_conditionals_formats_and_source_type(self):
        degraded = self.fixture("hub-issue-6-partial-extraction-001")
        degraded["extraction_metrics"]["raw_source_available"] = False
        with self.assertRaises(AssertionError):
            validate_subset(self.schema, self.schema, degraded)

        bad_timestamp = self.fixture("hub-admission-verified-baseline-001")
        bad_timestamp["retrieved_at"] = "not-a-date"
        with self.assertRaises(AssertionError):
            validate_subset(self.schema, self.schema, bad_timestamp)

        bad_source = self.fixture("hub-admission-verified-baseline-001")
        bad_source["source_identity"]["source_type"] = "not-mcp"
        with self.assertRaises(AssertionError):
            validate_subset(self.schema, self.schema, bad_source)

    def test_evaluator_has_no_network_or_live_hub_client(self):
        source = EVALUATOR_PATH.read_text(encoding="utf-8")

        self.assertNotIn("import requests", source)
        self.assertNotIn("import urllib", source)
        self.assertNotIn("import socket", source)
        self.assertNotIn("http.client", source)
        self.assertNotIn("urlopen(", source)
        self.assertNotIn("requests.", source)
        self.assertNotIn("httpx.", source)


if __name__ == "__main__":
    unittest.main()
