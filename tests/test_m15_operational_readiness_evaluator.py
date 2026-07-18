import ast
import copy
import hashlib
import json
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import runtime.m15_operational_readiness_evaluator as evaluator_module
from runtime.m15_operational_readiness_evaluator import (
    BLOCKED,
    EXPECTED_MAINTAINED_ARTIFACT_DIGESTS,
    EXPECTED_SCENARIO_TITLES,
    EXPECTED_TRACK_COUNTS,
    EXPECTED_TYPE_COUNTS,
    EXPECTED_VERIFICATION_COMMANDS,
    MAINTAINED_MAIN_SHA,
    NON_AUTHORITATIVE_BOUNDARY_STATEMENT,
    NOT_READY,
    OUTCOMES,
    READY_FOR_COMPLETION_REVIEW,
    REQUIRED_ARTIFACTS,
    SYNTHETIC_SCENARIO_BOUNDARY_STATEMENT,
    evaluate_operational_readiness,
    evaluate_repository_operational_readiness,
    evaluate_synthetic_scenario,
)
from runtime.repository_artifact_digest import (
    RepositoryArtifactFileTypeError,
    RepositoryArtifactPathError,
    RepositoryArtifactTextError,
    canonicalize_utf8_repository_text,
    sha256_repository_file,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "examples" / "public-integration-pack-pilot"
MANIFEST_PATH = FIXTURE_ROOT / "m15-operational-readiness-manifest.json"
SCHEMA_PATH = ROOT / "schemas" / "m15-operational-readiness.schema.json"
CONTRACT_PATH = ROOT / "docs" / "learning-governance" / "m15-operational-readiness-contract.md"
EVALUATOR_PATH = ROOT / "runtime" / "m15_operational_readiness_evaluator.py"
SCENARIO_PATHS = sorted(FIXTURE_ROOT.glob("m15-operational-readiness-[0-9][0-9]-*.json"))


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_manifest():
    return load_json(MANIFEST_PATH)


def scenario(number: int):
    matches = [path for path in SCENARIO_PATHS if path.name.startswith(f"m15-operational-readiness-{number:02d}-")]
    if len(matches) != 1:
        raise AssertionError((number, matches))
    return load_json(matches[0])


def _json_equal(left, right):
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left == right
    return left == right


def _resolve_local_json_pointer(document, reference):
    if not reference.startswith("#/"):
        raise AssertionError(f"unsupported schema reference: {reference}")
    value = document
    for raw_token in reference[2:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        value = value[token]
    return value


def validate_draft_2020_12_subset(instance, schema, *, root_schema=None, path="$"):
    """Validate the dependency-free Draft 2020-12 subset used by the E1 schema."""

    root_schema = schema if root_schema is None else root_schema
    if schema is True:
        return []
    if schema is False:
        return [f"{path}: rejected by false schema"]

    errors = []
    if "$ref" in schema:
        target = _resolve_local_json_pointer(root_schema, schema["$ref"])
        return validate_draft_2020_12_subset(
            instance,
            target,
            root_schema=root_schema,
            path=path,
        )

    if "oneOf" in schema:
        branch_errors = [
            validate_draft_2020_12_subset(
                instance,
                branch,
                root_schema=root_schema,
                path=path,
            )
            for branch in schema["oneOf"]
        ]
        if sum(not branch for branch in branch_errors) != 1:
            errors.append(f"{path}: oneOf must match exactly one schema")

    if "const" in schema and not _json_equal(instance, schema["const"]):
        errors.append(f"{path}: const mismatch")
    if "enum" in schema and not any(_json_equal(instance, item) for item in schema["enum"]):
        errors.append(f"{path}: value is not in enum")

    expected_type = schema.get("type")
    type_matches = {
        "object": isinstance(instance, dict),
        "array": isinstance(instance, list),
        "string": isinstance(instance, str),
        "integer": isinstance(instance, int) and not isinstance(instance, bool),
        "boolean": isinstance(instance, bool),
    }
    if expected_type is not None and not type_matches[expected_type]:
        errors.append(f"{path}: expected {expected_type}")
        return errors

    if isinstance(instance, dict):
        properties = schema.get("properties", {})
        for name in schema.get("required", []):
            if name not in instance:
                errors.append(f"{path}: missing required property {name}")
        for name, value in instance.items():
            if name in properties:
                errors.extend(
                    validate_draft_2020_12_subset(
                        value,
                        properties[name],
                        root_schema=root_schema,
                        path=f"{path}.{name}",
                    )
                )
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: additional property {name}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: fewer than minItems")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: more than maxItems")
        if schema.get("uniqueItems") is True:
            for index, item in enumerate(instance):
                if any(_json_equal(item, prior) for prior in instance[:index]):
                    errors.append(f"{path}: duplicate array item at {index}")
        prefix_items = schema.get("prefixItems", [])
        for index, item_schema in enumerate(prefix_items[: len(instance)]):
            errors.extend(
                validate_draft_2020_12_subset(
                    instance[index],
                    item_schema,
                    root_schema=root_schema,
                    path=f"{path}[{index}]",
                )
            )
        remaining_items_schema = schema.get("items", True)
        if remaining_items_schema is False and len(instance) > len(prefix_items):
            errors.append(f"{path}: items after prefixItems are forbidden")
        elif isinstance(remaining_items_schema, dict):
            for index in range(len(prefix_items), len(instance)):
                errors.extend(
                    validate_draft_2020_12_subset(
                        instance[index],
                        remaining_items_schema,
                        root_schema=root_schema,
                        path=f"{path}[{index}]",
                    )
                )

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: shorter than minLength")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append(f"{path}: pattern mismatch")
    if (
        isinstance(instance, int)
        and not isinstance(instance, bool)
        and "minimum" in schema
        and instance < schema["minimum"]
    ):
        errors.append(f"{path}: below minimum")
    return errors


class M15OperationalReadinessContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_json(SCHEMA_PATH)
        cls.manifest = load_manifest()

    def test_01_schema_is_draft_2020_12_and_has_two_strict_document_kinds(self):
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(len(self.schema["oneOf"]), 2)
        self.assertFalse(self.schema["$defs"]["maintainedManifest"]["additionalProperties"])
        self.assertFalse(self.schema["$defs"]["syntheticScenario"]["additionalProperties"])

    def test_02_schema_distinguishes_git_commit_and_sha256_shapes(self):
        self.assertEqual(self.schema["$defs"]["gitCommitSha"]["pattern"], "^[0-9a-f]{40}$")
        self.assertEqual(self.schema["$defs"]["sha256"]["pattern"], "^[0-9a-f]{64}$")

    def test_03_schema_binds_supported_versions(self):
        properties = self.schema["$defs"]["maintainedManifest"]["properties"]
        self.assertEqual(properties["schema_version"]["const"], evaluator_module.MANIFEST_SCHEMA_VERSION)
        scenario_properties = self.schema["$defs"]["syntheticScenario"]["properties"]
        self.assertEqual(scenario_properties["schema_version"]["const"], evaluator_module.SCENARIO_SCHEMA_VERSION)

    def test_04_manifest_binds_issue_track_repository_and_main(self):
        self.assertEqual(self.manifest["issue"], "#242")
        self.assertEqual(self.manifest["track"], "E1")
        self.assertEqual(self.manifest["maintained_repository"], "aa-os/aaos-public")
        self.assertEqual(self.manifest["maintained_branch"], "main")
        self.assertEqual(self.manifest["maintained_main_commit_sha"], MAINTAINED_MAIN_SHA)

    def test_05_manifest_binds_exact_track_pr_heads_and_merges(self):
        expected = {
            "track-a": ("#232", "#233", "603a26890ceee940b0a3c9009e06d994f9f2f342", "6e0fa4e8fdf4a672581cd897d52743d0462f0d4b"),
            "track-b": ("#234", "#237", "270a5bbb536c6bf0726e95455d4bb61ac86d693e", "8e475518f2da6232ae9a6264d8e9c9f1e5fc514a"),
            "track-c": ("#238", "#239", "5f98f6c86e6b61d50b1c8183aca0736a3419c533", "2d8bab3a84675543c34231a9e04521379febdac1"),
            "track-d": ("#240", "#241", "3bec19e42693b757b9abbb077146ca9860d48c1e", MAINTAINED_MAIN_SHA),
        }
        observed = {
            item["track_id"]: (
                item["source_issue"],
                item["implementation_pr"],
                item["head_sha"],
                item["merge_sha"],
            )
            for item in self.manifest["source_track_bindings"]
        }
        self.assertEqual(observed, expected)

    def test_06_inventory_has_exact_track_counts(self):
        inventory = self.manifest["artifact_integrity_inventory"]
        self.assertEqual(inventory["artifact_count"], 67)
        self.assertEqual(inventory["track_artifact_counts"], EXPECTED_TRACK_COUNTS)
        observed = dict(
            sorted(
                __import__("collections").Counter(
                    item["track_id"] for item in inventory["artifacts"]
                ).items()
            )
        )
        self.assertEqual(observed, EXPECTED_TRACK_COUNTS)

    def test_07_inventory_has_exact_artifact_type_counts(self):
        inventory = self.manifest["artifact_integrity_inventory"]
        self.assertEqual(inventory["artifact_type_counts"], EXPECTED_TYPE_COUNTS)
        observed = dict(
            __import__("collections").Counter(
                item["artifact_type"] for item in inventory["artifacts"]
            )
        )
        self.assertEqual(observed, EXPECTED_TYPE_COUNTS)

    def test_08_inventory_paths_are_exactly_required_paths(self):
        paths = [item["relative_path"] for item in self.manifest["artifact_integrity_inventory"]["artifacts"]]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertEqual(set(paths), set(REQUIRED_ARTIFACTS))

    def test_09_inventory_excludes_e1_readme_and_historical_artifacts(self):
        paths = set(REQUIRED_ARTIFACTS)
        self.assertNotIn("README.md", paths)
        self.assertFalse(any("operational-readiness" in path for path in paths))
        self.assertFalse(any("historical" in path for path in paths))

    def test_10_every_inventory_entry_has_a_track_test_binding(self):
        for entry in self.manifest["artifact_integrity_inventory"]["artifacts"]:
            with self.subTest(path=entry["relative_path"]):
                self.assertEqual(entry["test_module"], REQUIRED_ARTIFACTS[entry["relative_path"]]["test_module"])
                self.assertFalse(entry["executable_by_evaluator"])

    def test_11_every_declared_digest_matches_maintained_canonical_text(self):
        self.assertEqual(
            set(EXPECTED_MAINTAINED_ARTIFACT_DIGESTS),
            set(REQUIRED_ARTIFACTS),
        )
        for entry in self.manifest["artifact_integrity_inventory"]["artifacts"]:
            with self.subTest(path=entry["relative_path"]):
                self.assertEqual(
                    entry["maintained_canonical_sha256"],
                    EXPECTED_MAINTAINED_ARTIFACT_DIGESTS[entry["relative_path"]],
                )
                self.assertEqual(
                    EXPECTED_MAINTAINED_ARTIFACT_DIGESTS[entry["relative_path"]],
                    sha256_repository_file(ROOT, entry["relative_path"], mode="text"),
                )

    def test_12_track_d_cross_control_matrix_is_bound_once(self):
        matches = [
            item
            for item in self.manifest["artifact_integrity_inventory"]["artifacts"]
            if item["artifact_type"] == "cross-control-matrix"
        ]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["relative_path"], "examples/public-integration-pack-pilot/m15-cross-control-matrix.json")

    def test_13_historical_digest_policy_is_separate_and_unmodified(self):
        inventory = self.manifest["artifact_integrity_inventory"]
        self.assertEqual(inventory["historical_digest_evidence_policy"], "preserved-separate-and-unmodified")
        self.assertEqual(inventory["canonicalization"], "strict-utf8-crlf-to-lf-only")

    def test_14_verification_command_ids_are_complete_and_unique(self):
        commands = self.manifest["verification_command_manifest"]["commands"]
        ids = [item["command_id"] for item in commands]
        self.assertEqual(len(ids), 13)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), set(EXPECTED_VERIFICATION_COMMANDS))

    def test_15_verification_command_argv_and_scopes_are_exact(self):
        commands = {
            item["command_id"]: item
            for item in self.manifest["verification_command_manifest"]["commands"]
        }
        for command_id, expected in EXPECTED_VERIFICATION_COMMANDS.items():
            with self.subTest(command_id=command_id):
                self.assertEqual(commands[command_id]["argv"], expected["argv"])
                self.assertEqual(commands[command_id]["test_scope"], expected["test_scope"])
                self.assertEqual(commands[command_id]["expected_exit_code"], 0)

    def test_16_verification_manifest_is_declarative_and_non_authoritative(self):
        verification = self.manifest["verification_command_manifest"]
        self.assertFalse(verification["executed_by_evaluator"])
        self.assertFalse(verification["execution_results_recorded"])
        self.assertFalse(verification["verification_results_are_completion_approval"])
        self.assertTrue(all(not item["executed_by_evaluator"] for item in verification["commands"]))

    def test_17_governance_boundary_keeps_tracker_m15_and_release_open(self):
        boundary = self.manifest["governance_boundary"]
        self.assertEqual(boundary["tracker_231_state"], "open")
        self.assertEqual(boundary["m15_state"], "active-and-incomplete")
        self.assertEqual(boundary["v0_14_0_state"], "unpublished")
        for field, value in boundary.items():
            if field not in {"tracker_231_state", "m15_state", "v0_14_0_state"}:
                self.assertIs(value, False, field)

    def test_18_only_three_outcomes_are_declared(self):
        self.assertEqual(self.manifest["allowed_outcomes"], list(OUTCOMES))
        self.assertEqual(self.manifest["declared_outcome"], READY_FOR_COMPLETION_REVIEW)

    def test_19_contract_preserves_exact_non_authoritative_boundaries(self):
        text = CONTRACT_PATH.read_text(encoding="utf-8")
        self.assertIn(NON_AUTHORITATIVE_BOUNDARY_STATEMENT, text)
        self.assertIn(SYNTHETIC_SCENARIO_BOUNDARY_STATEMENT, text)
        self.assertIn("Capability Pack sealing is undefined and out of scope for M15 Track B.", text)
        self.assertIn("Track D evidence grants no authority; Learning Proof and Decision Proof sealing remain AAOS-owned; AAOS remains the decision sovereignty layer.", text)

    def test_20_exactly_eighteen_standalone_scenarios_are_present(self):
        self.assertEqual(len(SCENARIO_PATHS), 18)
        documents = [load_json(path) for path in SCENARIO_PATHS]
        self.assertEqual(
            [document["scenario_id"] for document in documents],
            [f"m15-e1-{number:02d}" for number in range(1, 19)],
        )
        self.assertEqual(
            {document["scenario_id"]: document["title"] for document in documents},
            EXPECTED_SCENARIO_TITLES,
        )
        self.assertEqual(
            {document["notes"] for document in documents},
            {SYNTHETIC_SCENARIO_BOUNDARY_STATEMENT},
        )

    def test_21_manifest_and_well_formed_scenarios_validate_against_schema(self):
        self.assertEqual(validate_draft_2020_12_subset(self.manifest, self.schema), [])
        for number in range(1, 18):
            with self.subTest(number=number):
                self.assertEqual(
                    validate_draft_2020_12_subset(scenario(number), self.schema),
                    [],
                )

    def test_22_malformed_schema_version_scenario_is_schema_invalid(self):
        self.assertTrue(validate_draft_2020_12_subset(scenario(18), self.schema))

    def test_23_prefix_items_and_items_false_are_enforced(self):
        outcomes_schema = self.schema["$defs"]["maintainedManifest"]["properties"]["allowed_outcomes"]
        self.assertIs(outcomes_schema["items"], False)
        extra = copy.deepcopy(self.manifest)
        extra["allowed_outcomes"].append("unexpected")
        reordered = copy.deepcopy(self.manifest)
        reordered["allowed_outcomes"][0:2] = reversed(reordered["allowed_outcomes"][0:2])
        self.assertTrue(validate_draft_2020_12_subset(extra, self.schema))
        self.assertTrue(validate_draft_2020_12_subset(reordered, self.schema))

    def test_24_schema_accepts_nonempty_unique_blocker_lists(self):
        blocked = copy.deepcopy(self.manifest)
        blocked["known_repository_local_completion_blockers"] = ["synthetic-local-blocker"]
        blocked["declared_outcome"] = BLOCKED
        self.assertEqual(validate_draft_2020_12_subset(blocked, self.schema), [])

        empty = copy.deepcopy(blocked)
        empty["known_repository_local_completion_blockers"] = [""]
        duplicate = copy.deepcopy(blocked)
        duplicate["known_repository_local_completion_blockers"] *= 2
        self.assertTrue(validate_draft_2020_12_subset(empty, self.schema))
        self.assertTrue(validate_draft_2020_12_subset(duplicate, self.schema))


class M15OperationalReadinessMaintainedEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_manifest()

    def assert_blocked(self, result, finding_prefix=None):
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertFalse(result["ready_for_completion_review"])
        if finding_prefix:
            self.assertTrue(any(item.startswith(finding_prefix) for item in result["blocking_findings"]), result)

    def test_01_maintained_manifest_is_ready_for_completion_review(self):
        result = evaluate_operational_readiness(self.manifest, repository_root=ROOT)
        self.assertEqual(result["outcome"], READY_FOR_COMPLETION_REVIEW)
        self.assertTrue(result["ready_for_completion_review"])
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["evaluated_artifact_count"], 67)
        self.assertEqual(result["evaluated_verification_command_count"], 13)

    def test_02_repository_loader_uses_the_maintained_manifest(self):
        self.assertEqual(evaluate_repository_operational_readiness(ROOT)["outcome"], READY_FOR_COMPLETION_REVIEW)

    def test_03_default_repository_root_is_independent_of_process_cwd(self):
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as temporary:
            try:
                os.chdir(temporary)
                result = evaluate_repository_operational_readiness()
            finally:
                os.chdir(previous)
        self.assertEqual(result["outcome"], READY_FOR_COMPLETION_REVIEW)

    def test_04_evaluation_does_not_mutate_manifest_input(self):
        document = copy.deepcopy(self.manifest)
        before = copy.deepcopy(document)
        evaluate_operational_readiness(document, repository_root=ROOT)
        self.assertEqual(document, before)

    def test_05_findings_are_sorted_and_deduplicated(self):
        document = copy.deepcopy(self.manifest)
        document["maintained_main_commit_sha"] = "0" * 40
        document["governance_boundary"]["tag_created"] = True
        first = evaluate_operational_readiness(document, repository_root=ROOT)
        second = evaluate_operational_readiness(document, repository_root=ROOT)
        self.assertEqual(first, second)
        self.assertEqual(first["findings"], sorted(set(first["findings"])))

    def test_06_maintained_main_sha_mismatch_is_blocked(self):
        document = copy.deepcopy(self.manifest)
        document["maintained_main_commit_sha"] = "0" * 40
        self.assert_blocked(evaluate_operational_readiness(document, repository_root=ROOT), "maintained_main_sha_mismatch")

    def test_07_track_pr_head_or_merge_binding_mismatch_is_blocked(self):
        for field, value in (("implementation_pr", "#999"), ("head_sha", "0" * 40), ("merge_sha", "0" * 40)):
            document = copy.deepcopy(self.manifest)
            document["source_track_bindings"][0][field] = value
            with self.subTest(field=field):
                self.assert_blocked(evaluate_operational_readiness(document, repository_root=ROOT), "source_track_binding_mismatch:track-a")

    def test_08_missing_inventory_entry_is_blocked(self):
        document = copy.deepcopy(self.manifest)
        document["artifact_integrity_inventory"]["artifacts"].pop()
        self.assert_blocked(evaluate_operational_readiness(document, repository_root=ROOT), "artifact_entry_missing:")

    def test_09_duplicate_inventory_entry_is_blocked(self):
        document = copy.deepcopy(self.manifest)
        artifacts = document["artifact_integrity_inventory"]["artifacts"]
        artifacts[-1] = copy.deepcopy(artifacts[0])
        self.assert_blocked(evaluate_operational_readiness(document, repository_root=ROOT), "duplicate_artifact:")

    def test_10a_declared_digest_drift_is_blocked(self):
        document = copy.deepcopy(self.manifest)
        document["artifact_integrity_inventory"]["artifacts"][0]["maintained_canonical_sha256"] = "0" * 64
        self.assert_blocked(evaluate_operational_readiness(document, repository_root=ROOT), "artifact_declared_digest_mismatch:")

    def test_10b_declared_and_observed_digest_codrift_is_blocked(self):
        document = copy.deepcopy(self.manifest)
        document["artifact_integrity_inventory"]["artifacts"][0]["maintained_canonical_sha256"] = "0" * 64
        with mock.patch.object(evaluator_module, "sha256_repository_file", return_value="0" * 64):
            result = evaluate_operational_readiness(document, repository_root=ROOT)
        self.assert_blocked(result, "artifact_declared_digest_mismatch:")

    def test_11_track_pr_and_type_substitutions_are_blocked(self):
        for field, value in (("track_id", "track-d"), ("implementation_pr", "#241"), ("artifact_type", "fixture")):
            document = copy.deepcopy(self.manifest)
            document["artifact_integrity_inventory"]["artifacts"][0][field] = value
            with self.subTest(field=field):
                self.assert_blocked(evaluate_operational_readiness(document, repository_root=ROOT), f"artifact_{field}_binding_mismatch:")

    def test_12_incomplete_test_coverage_is_not_ready(self):
        document = copy.deepcopy(self.manifest)
        document["artifact_integrity_inventory"]["artifacts"][0]["test_module"] = "tests.test_m15_cross_control_regression_evaluator"
        result = evaluate_operational_readiness(document, repository_root=ROOT)
        self.assertEqual(result["outcome"], NOT_READY)
        self.assertIn("test_coverage_incomplete:track-a", result["readiness_findings"])

    def test_13_missing_verification_command_is_not_ready(self):
        document = copy.deepcopy(self.manifest)
        document["verification_command_manifest"]["commands"].pop()
        result = evaluate_operational_readiness(document, repository_root=ROOT)
        self.assertEqual(result["outcome"], NOT_READY)
        self.assertTrue(any(item.startswith("verification_command_missing:") for item in result["readiness_findings"]))

    def test_14_changed_verification_argv_is_not_ready(self):
        document = copy.deepcopy(self.manifest)
        document["verification_command_manifest"]["commands"][0]["argv"].append("unexpected")
        result = evaluate_operational_readiness(document, repository_root=ROOT)
        self.assertEqual(result["outcome"], NOT_READY)
        self.assertTrue(any(item.startswith("verification_command_invalid:") for item in result["readiness_findings"]))

    def test_15_verification_execution_claim_is_blocked(self):
        document = copy.deepcopy(self.manifest)
        document["verification_command_manifest"]["executed_by_evaluator"] = True
        self.assert_blocked(evaluate_operational_readiness(document, repository_root=ROOT), "verification_execution_claimed")

    def test_16_source_artifact_execution_claim_is_blocked(self):
        document = copy.deepcopy(self.manifest)
        document["artifact_integrity_inventory"]["artifacts"][0]["executable_by_evaluator"] = True
        self.assert_blocked(evaluate_operational_readiness(document, repository_root=ROOT), "artifact_execution_boundary_invalid:")

    def test_17_every_governance_escalation_is_blocked(self):
        boundary = self.manifest["governance_boundary"]
        state_fields = {
            "tracker_231_state": "closed",
            "m15_state": "complete",
            "v0_14_0_state": "published",
        }
        for field in boundary:
            document = copy.deepcopy(self.manifest)
            document["governance_boundary"][field] = state_fields.get(field, True)
            with self.subTest(field=field):
                self.assert_blocked(evaluate_operational_readiness(document, repository_root=ROOT))

    def test_18_known_repository_local_blocker_is_blocked(self):
        document = copy.deepcopy(self.manifest)
        document["known_repository_local_completion_blockers"] = ["synthetic-local-blocker"]
        self.assert_blocked(evaluate_operational_readiness(document, repository_root=ROOT), "unresolved_completion_blocker:")

    def test_19_extra_or_missing_manifest_fields_are_blocked(self):
        extra = copy.deepcopy(self.manifest)
        extra["unexpected"] = True
        missing = copy.deepcopy(self.manifest)
        missing.pop("parent_tracker")
        self.assert_blocked(evaluate_operational_readiness(extra, repository_root=ROOT), "manifest_shape_invalid")
        self.assert_blocked(evaluate_operational_readiness(missing, repository_root=ROOT), "manifest_shape_invalid")

    def test_20_unsupported_manifest_schema_is_blocked(self):
        document = copy.deepcopy(self.manifest)
        document["schema_version"] = "m15-operational-readiness/v2"
        self.assert_blocked(evaluate_operational_readiness(document, repository_root=ROOT), "schema_version_mismatch")

    def test_21_missing_track_d_matrix_is_blocked(self):
        document = copy.deepcopy(self.manifest)
        artifacts = document["artifact_integrity_inventory"]["artifacts"]
        artifacts[:] = [item for item in artifacts if item["artifact_type"] != "cross-control-matrix"]
        self.assert_blocked(evaluate_operational_readiness(document, repository_root=ROOT), "track_d_cross_control_matrix_not_bound")

    def test_22_historical_digest_policy_drift_is_blocked(self):
        document = copy.deepcopy(self.manifest)
        document["artifact_integrity_inventory"]["historical_digest_evidence_policy"] = "reinterpreted"
        self.assert_blocked(evaluate_operational_readiness(document, repository_root=ROOT), "historical_digest_evidence_policy_invalid")

    def test_23_declared_not_ready_cannot_be_promoted_by_clean_evidence(self):
        document = copy.deepcopy(self.manifest)
        document["declared_outcome"] = NOT_READY
        result = evaluate_operational_readiness(document, repository_root=ROOT)
        self.assertEqual(result["outcome"], NOT_READY)
        self.assertIn("declared_outcome_not_ready_for_review", result["readiness_findings"])

    def test_24_relative_repository_root_is_blocked(self):
        self.assert_blocked(evaluate_operational_readiness(self.manifest, repository_root=Path(".")), "repository_root_not_absolute")

    def test_25_missing_manifest_file_is_blocked(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = evaluate_repository_operational_readiness(Path(temporary).resolve())
        self.assert_blocked(result, "manifest_unreadable")

    def test_26_missing_artifact_error_is_classified_without_host_value(self):
        with mock.patch.object(evaluator_module, "sha256_repository_file", side_effect=FileNotFoundError("host-secret")):
            result = evaluate_operational_readiness(self.manifest, repository_root=ROOT)
        self.assert_blocked(result, "artifact_missing:")
        self.assertNotIn("host-secret", json.dumps(result))

    def test_27_unsafe_nonregular_and_text_errors_fail_closed(self):
        errors = (
            RepositoryArtifactPathError("unsafe"),
            RepositoryArtifactFileTypeError("not regular"),
            RepositoryArtifactTextError("lone carriage return"),
            UnicodeDecodeError("utf-8", b"\xff", 0, 1, "bad"),
            OSError("unreadable"),
        )
        prefixes = (
            "artifact_path_unsafe:",
            "artifact_not_regular:",
            "artifact_lone_carriage_return:",
            "artifact_malformed_utf8:",
            "artifact_unreadable:",
        )
        for error, prefix in zip(errors, prefixes):
            with self.subTest(prefix=prefix):
                with mock.patch.object(evaluator_module, "sha256_repository_file", side_effect=error):
                    result = evaluate_operational_readiness(self.manifest, repository_root=ROOT)
                self.assert_blocked(result, prefix)


class M15OperationalReadinessScenarioTests(unittest.TestCase):
    def assert_scenario(self, number, expected):
        document = scenario(number)
        before = copy.deepcopy(document)
        first = evaluate_synthetic_scenario(document)
        second = evaluate_synthetic_scenario(document)
        self.assertEqual(first, second)
        self.assertEqual(document, before)
        self.assertEqual(document["expected_outcome"], expected)
        self.assertEqual(first["outcome"], expected)
        self.assertIn(first["outcome"], OUTCOMES)

    def test_01_valid_maintained_main(self): self.assert_scenario(1, READY_FOR_COMPLETION_REVIEW)
    def test_02_maintained_main_binding_mismatch(self): self.assert_scenario(2, BLOCKED)
    def test_03_source_track_binding_mismatch(self): self.assert_scenario(3, BLOCKED)
    def test_04_incomplete_artifact_inventory(self): self.assert_scenario(4, BLOCKED)
    def test_05_artifact_integrity_failure(self): self.assert_scenario(5, BLOCKED)
    def test_06_internal_consistency_failure(self): self.assert_scenario(6, BLOCKED)
    def test_07_cross_control_matrix_unbound(self): self.assert_scenario(7, BLOCKED)
    def test_08_incomplete_test_coverage(self): self.assert_scenario(8, NOT_READY)
    def test_09_incomplete_verification_command_manifest(self): self.assert_scenario(9, NOT_READY)
    def test_10_verification_execution_claimed(self): self.assert_scenario(10, BLOCKED)
    def test_11_completion_approval_claim(self): self.assert_scenario(11, BLOCKED)
    def test_12_tracker_closure_claim(self): self.assert_scenario(12, BLOCKED)
    def test_13_m15_completion_claim(self): self.assert_scenario(13, BLOCKED)
    def test_14_readme_authorization_claim(self): self.assert_scenario(14, BLOCKED)
    def test_15_tag_authorization_or_creation_claim(self): self.assert_scenario(15, BLOCKED)
    def test_16_release_authorization_or_publication_claim(self): self.assert_scenario(16, BLOCKED)
    def test_17_known_repository_local_completion_blocker(self): self.assert_scenario(17, BLOCKED)
    def test_18_malformed_schema_version(self): self.assert_scenario(18, BLOCKED)

    def test_19_expected_outcome_is_not_trusted_for_classification(self):
        document = scenario(1)
        document["expected_outcome"] = BLOCKED
        self.assertEqual(evaluate_synthetic_scenario(document)["outcome"], READY_FOR_COMPLETION_REVIEW)

    def test_20_blocked_takes_precedence_over_not_ready(self):
        document = scenario(1)
        document["evidence_state"]["test_coverage_complete"] = False
        document["evidence_state"]["completion_approval_claimed"] = True
        result = evaluate_synthetic_scenario(document)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertTrue(result["readiness_findings"])
        self.assertTrue(result["blocking_findings"])

    def test_21_non_boolean_state_is_blocked(self):
        document = scenario(1)
        document["evidence_state"]["manifest_shape_valid"] = 1
        self.assertEqual(evaluate_synthetic_scenario(document)["outcome"], BLOCKED)

    def test_22_unknown_fields_fail_without_echoing_hostile_values(self):
        document = scenario(1)
        document["hostile-secret-value"] = "do-not-echo"
        result = evaluate_synthetic_scenario(document)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertNotIn("do-not-echo", json.dumps(result))

    def test_23_scenario_text_is_closed_and_cannot_assert_authority(self):
        cases = (
            (
                "notes",
                "Synthetic inert evidence only.",
                "scenario_notes_boundary_invalid",
            ),
            (
                "notes",
                "Synthetic inert, non-authoritative evidence only. M15 is complete and v0.14.0 is published.",
                "scenario_notes_boundary_invalid",
            ),
            (
                "notes",
                "Synthetic inert, non-authoritative evidence only. M15 has completed and v0.14.0 has been published.",
                "scenario_notes_boundary_invalid",
            ),
            (
                "title",
                "M15 has completed and v0.14.0 has been published",
                "scenario_title_invalid",
            ),
        )
        for field, value, finding in cases:
            document = scenario(1)
            document[field] = value
            with self.subTest(field=field, finding=finding):
                result = evaluate_synthetic_scenario(document)
                self.assertEqual(result["outcome"], BLOCKED)
                self.assertIn(finding, result["blocking_findings"])


class M15OperationalReadinessSafetyTests(unittest.TestCase):
    def test_01_canonical_text_hash_normalizes_only_crlf(self):
        self.assertEqual(canonicalize_utf8_repository_text(b"alpha\r\nbeta\r\n"), b"alpha\nbeta\n")
        self.assertEqual(
            hashlib.sha256(canonicalize_utf8_repository_text(b"alpha\r\nbeta\r\n")).hexdigest(),
            hashlib.sha256(b"alpha\nbeta\n").hexdigest(),
        )

    def test_02_canonical_text_rejects_lone_carriage_return(self):
        with self.assertRaises(RepositoryArtifactTextError):
            canonicalize_utf8_repository_text(b"alpha\rbeta")

    def test_03_canonical_text_preserves_terminal_newline_spaces_and_bom(self):
        self.assertNotEqual(
            canonicalize_utf8_repository_text(b"alpha"),
            canonicalize_utf8_repository_text(b"alpha\n"),
        )
        self.assertEqual(canonicalize_utf8_repository_text(b"alpha  \n"), b"alpha  \n")
        self.assertEqual(canonicalize_utf8_repository_text(b"\xef\xbb\xbfalpha\n"), b"\xef\xbb\xbfalpha\n")

    def test_04_repository_hash_is_checkout_line_ending_independent(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "crlf.txt").write_bytes(b"alpha\r\nbeta\r\n")
            (root / "lf.txt").write_bytes(b"alpha\nbeta\n")
            self.assertEqual(
                sha256_repository_file(root, "crlf.txt", mode="text"),
                sha256_repository_file(root, "lf.txt", mode="text"),
            )

    def test_05_static_imports_exclude_execution_and_network_modules(self):
        tree = ast.parse(EVALUATOR_PATH.read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        banned = {"subprocess", "socket", "requests", "urllib", "http", "runpy", "importlib"}
        self.assertFalse(imported & banned)

    def test_06_evaluator_does_not_import_track_a_d_evaluators(self):
        source = EVALUATOR_PATH.read_text(encoding="utf-8")
        for module_name in (
            "m15_learning_proof_evaluator",
            "m15_capability_memory_pack_evaluator",
            "m15_lineage_rollback_portability_evaluator",
            "m15_cross_control_regression_evaluator",
        ):
            self.assertNotIn(f"import {module_name}", source)

    def test_07_evaluator_has_no_file_write_calls(self):
        tree = ast.parse(EVALUATOR_PATH.read_text(encoding="utf-8"))
        banned_attributes = {"write_text", "write_bytes", "unlink", "rename", "replace", "mkdir", "rmdir"}
        called_attributes = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        self.assertFalse(called_attributes & banned_attributes)

    def test_08_repository_root_is_derived_from_evaluator_location(self):
        self.assertEqual(evaluator_module.REPOSITORY_ROOT, ROOT)
        self.assertTrue(evaluator_module.REPOSITORY_ROOT.is_absolute())

    def test_09_result_exposes_one_outcome_field_with_closed_vocabulary(self):
        result = evaluate_repository_operational_readiness(ROOT)
        self.assertEqual([key for key in result if key == "outcome"], ["outcome"])
        self.assertIn(result["outcome"], OUTCOMES)
        self.assertNotIn("status", result)

    def test_10_all_fixture_findings_are_sorted_and_deduplicated(self):
        for path in SCENARIO_PATHS:
            with self.subTest(path=path.name):
                result = evaluate_synthetic_scenario(load_json(path))
                self.assertEqual(result["findings"], sorted(set(result["findings"])))

    def test_11_contract_and_manifest_do_not_claim_track_e2_e3_or_e4(self):
        contract = CONTRACT_PATH.read_text(encoding="utf-8")
        self.assertIn("does not implement Track E2, E3, or E4", contract)
        self.assertEqual(load_manifest()["track"], "E1")

    def test_12_ready_for_review_is_never_completion_or_release_authority(self):
        result = evaluate_repository_operational_readiness(ROOT)
        self.assertEqual(result["outcome"], READY_FOR_COMPLETION_REVIEW)
        self.assertEqual(result["non_authoritative_boundary_statement"], NON_AUTHORITATIVE_BOUNDARY_STATEMENT)
        self.assertIn("not M15 completion approval", result["non_authoritative_boundary_statement"])
        self.assertIn("not", result["non_authoritative_boundary_statement"])


if __name__ == "__main__":
    unittest.main()
