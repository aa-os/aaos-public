import ast
import copy
import hashlib
import inspect
import json
import os
import re
import shutil
import subprocess
import unittest
from collections import Counter
from pathlib import Path

import runtime.m15_release_proof_linkage_evaluator as evaluator_module
from runtime.m15_release_proof_linkage_evaluator import (
    BLOCKED,
    CANDIDATE_CHANGE_SET_PRESERVED,
    DRIFT_DETECTED,
    E1_CANDIDATE_SHA,
    E1_CANDIDATE_TREE_SHA,
    E1_EXTERNAL_RECEIPT_SHA256,
    E1_MERGE_SHA,
    E1_MERGE_TREE_SHA,
    E2_ISSUE_NUMBER,
    E2_PULL_REQUEST_NUMBER,
    EXACT_TREE_MATCH,
    EXPECTED_PATHS,
    EXPECTED_SCENARIO_TITLES,
    EXPECTED_VERIFICATION_COMMANDS,
    FUTURE_RELEASE_CANDIDATE_IDENTIFIER,
    FUTURE_RELEASE_CANDIDATE_STATE,
    NON_AUTHORITATIVE_BOUNDARY_STATEMENT,
    NOT_READY,
    PR_OBSERVATION_BOUNDARY_STATEMENT,
    PR_OBSERVATION_SCHEMA_VERSION,
    RELEASE_PROOF_LINKED,
    REQUIRED_FUTURE_PREREQUISITES,
    REQUIRED_LINKAGE_BLOCKERS,
    SCENARIO_BOUNDARY_STATEMENT,
    SOURCE_BASELINE_SHA,
    SOURCE_BASELINE_TREE_SHA,
    STARTING_MAIN_SHA,
    STARTING_MAIN_TREE_SHA,
    UNVERIFIED,
    VERIFICATION_RECEIPT_BOUNDARY_STATEMENT,
    VERIFICATION_RECEIPT_SCHEMA_VERSION,
    evaluate_path_continuity,
    evaluate_release_proof_linkage,
    evaluate_synthetic_scenario,
)
from runtime.repository_artifact_digest import canonicalize_utf8_repository_text


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "examples" / "public-integration-pack-pilot"
SCHEMA_PATH = ROOT / "schemas" / "m15-release-proof-linkage.schema.json"
CONTRACT_PATH = (
    ROOT / "docs" / "learning-governance" / "m15-release-proof-linkage-contract.md"
)
EVALUATOR_PATH = ROOT / "runtime" / "m15_release_proof_linkage_evaluator.py"
MANIFEST_PATH = FIXTURE_ROOT / "m15-release-proof-linkage-manifest.json"
CANDIDATE_PATH = FIXTURE_ROOT / "m15-release-proof-linkage-candidate-changed-paths.json"
MERGE_PATH = FIXTURE_ROOT / "m15-release-proof-linkage-merge-result-paths.json"
CONTINUITY_PATH = (
    FIXTURE_ROOT / "m15-release-proof-linkage-candidate-to-merge-continuity.json"
)
E1_RECEIPT_PATH = (
    FIXTURE_ROOT / "m15-release-proof-linkage-e1-external-receipt.json"
)
BOUNDARY_PATH = FIXTURE_ROOT / "m15-release-proof-linkage-release-boundaries.json"
SCENARIO_PATHS = sorted(
    FIXTURE_ROOT.glob("m15-release-proof-linkage-[0-9][0-9]-*.json")
)
ACTUAL_PYTHON_LAUNCHER = ".verification-python/python.exe"
SYNTHETIC_E2_CANDIDATE_SHA = "c" * 40
SYNTHETIC_E2_CANDIDATE_TREE_SHA = "d" * 40
SYNTHETIC_TRANSCRIPT_SHA256 = "a" * 64


def load_json(path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def _json_equal(left, right):
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    return left == right


def _resolve_local_json_pointer(schema, reference):
    if not reference.startswith("#/"):
        raise AssertionError(f"unsupported schema reference: {reference}")
    value = schema
    for token in reference[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        value = value[token]
    return value


def validate_draft_2020_12_subset(instance, schema, *, root_schema=None, path="$"):
    """Validate the Draft 2020-12 features used by the maintained E2 schema."""

    root_schema = schema if root_schema is None else root_schema
    if schema is True:
        return []
    if schema is False:
        return [f"{path}: rejected by false schema"]
    if "$ref" in schema:
        return validate_draft_2020_12_subset(
            instance,
            _resolve_local_json_pointer(root_schema, schema["$ref"]),
            root_schema=root_schema,
            path=path,
        )

    errors = []
    if "oneOf" in schema:
        branch_errors = [
            validate_draft_2020_12_subset(
                instance, branch, root_schema=root_schema, path=path
            )
            for branch in schema["oneOf"]
        ]
        if sum(not branch for branch in branch_errors) != 1:
            errors.append(f"{path}: oneOf must match exactly one schema")
        return errors
    if "const" in schema and not _json_equal(instance, schema["const"]):
        errors.append(f"{path}: const mismatch")
    if "enum" in schema and not any(
        _json_equal(instance, item) for item in schema["enum"]
    ):
        errors.append(f"{path}: enum mismatch")

    expected_type = schema.get("type")
    type_matches = {
        "object": isinstance(instance, dict),
        "array": isinstance(instance, list),
        "string": isinstance(instance, str),
        "integer": isinstance(instance, int) and not isinstance(instance, bool),
        "boolean": type(instance) is bool,
        "null": instance is None,
    }
    if expected_type is not None and not type_matches.get(expected_type, False):
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
        items_schema = schema.get("items", True)
        if items_schema is False and len(instance) > len(prefix_items):
            errors.append(f"{path}: additional array items")
        elif isinstance(items_schema, dict):
            start = len(prefix_items)
            for index, value in enumerate(instance[start:], start=start):
                errors.extend(
                    validate_draft_2020_12_subset(
                        value,
                        items_schema,
                        root_schema=root_schema,
                        path=f"{path}[{index}]",
                    )
                )

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: shorter than minLength")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{path}: longer than maxLength")
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


def build_external_pr_observation(
    *,
    candidate_head=SYNTHETIC_E2_CANDIDATE_SHA,
    candidate_tree=SYNTHETIC_E2_CANDIDATE_TREE_SHA,
    pull_request_number=E2_PULL_REQUEST_NUMBER,
    issue_number=E2_ISSUE_NUMBER,
    base_sha=STARTING_MAIN_SHA,
):
    return {
        "schema_version": PR_OBSERVATION_SCHEMA_VERSION,
        "document_type": "pull-request-candidate-observation",
        "repository": "aa-os/aaos-public",
        "issue_number": issue_number,
        "pull_request_number": pull_request_number,
        "base_sha": base_sha,
        "candidate_head_sha": candidate_head,
        "candidate_tree_sha": candidate_tree,
        "execution_subject_type": "pull-request-candidate-checkout",
        "observed_at": "2026-07-19T12:00:00Z",
        "observer": "synthetic-offline-observer",
        "evidence_reference": "synthetic-pr-observation:aa-os/aaos-public#249",
        "external_to_candidate_commit": True,
        "fetched_by_evaluator": False,
        "non_authoritative_boundary_statement": PR_OBSERVATION_BOUNDARY_STATEMENT,
    }


def build_external_e2_receipt(
    *,
    candidate_head=SYNTHETIC_E2_CANDIDATE_SHA,
    pull_request_number=E2_PULL_REQUEST_NUMBER,
):
    commands = []
    for command_id, expected in EXPECTED_VERIFICATION_COMMANDS.items():
        actual_argv = [ACTUAL_PYTHON_LAUNCHER, *expected["argv"][1:]]
        commands.append(
            {
                "command_id": command_id,
                "declared_logical_argv": list(expected["argv"]),
                "actual_argv": actual_argv,
                "execution_scope": expected["execution_scope"],
                "execution_candidate_head_sha": candidate_head,
                "executable_binding": {
                    "declared_launcher": "python",
                    "actual_launcher": ACTUAL_PYTHON_LAUNCHER,
                    "launcher_substitution_detected": True,
                    "launcher_substitution_declared": True,
                    "python_implementation": "CPython",
                    "python_version": "3.14.6",
                },
                "tests_observed": expected["minimum_tests_observed"],
                "passes": expected["minimum_tests_observed"],
                "failures": 0,
                "errors": 0,
                "skips": 0,
                "exit_code": 0,
                "execution_timestamp": "2026-07-19T12:00:00Z",
                "transcript_sha256": SYNTHETIC_TRANSCRIPT_SHA256,
                "evidence_reference": f"synthetic-external-receipt:{command_id}",
                "executed_by_evaluator": False,
                "verification_results_are_release_authority": False,
            }
        )
    return {
        "schema_version": VERIFICATION_RECEIPT_SCHEMA_VERSION,
        "document_type": "external-verification-execution-receipt",
        "repository": "aa-os/aaos-public",
        "issue_number": 248,
        "pull_request_number": pull_request_number,
        "source_main_base_sha": STARTING_MAIN_SHA,
        "execution_subject_type": "pull-request-candidate-checkout",
        "execution_candidate_reference": f"pull-request:#{pull_request_number}",
        "execution_candidate_head_sha": candidate_head,
        "command_receipt_count": len(commands),
        "commands": commands,
        "external_to_candidate_commit": True,
        "executed_by_evaluator": False,
        "non_authoritative_boundary_statement": VERIFICATION_RECEIPT_BOUNDARY_STATEMENT,
    }


def load_package():
    return {
        "manifest": load_json(MANIFEST_PATH),
        "candidate_path_manifest": load_json(CANDIDATE_PATH),
        "merge_path_manifest": load_json(MERGE_PATH),
        "continuity_record": load_json(CONTINUITY_PATH),
        "e1_receipt_linkage": load_json(E1_RECEIPT_PATH),
        "release_boundary_register": load_json(BOUNDARY_PATH),
        "pull_request_observation": build_external_pr_observation(),
        "external_verification_receipt": build_external_e2_receipt(),
    }


def evaluate_package(package):
    return evaluate_release_proof_linkage(
        package["manifest"],
        package["candidate_path_manifest"],
        package["merge_path_manifest"],
        package["continuity_record"],
        package["e1_receipt_linkage"],
        package["release_boundary_register"],
        package["pull_request_observation"],
        package["external_verification_receipt"],
    )


def git_bytes(*args):
    git = os.environ.get("AAOS_TEST_GIT_EXE") or shutil.which("git")
    if git is None:
        raise AssertionError("Git is required for read-only historical object tests")
    completed = subprocess.run(
        [git, *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout


def git_text(*args):
    return git_bytes(*args).decode("utf-8", errors="strict")


def git_tree(commit_sha):
    return git_text("show", "-s", "--format=%T", commit_sha).strip()


def git_parents(commit_sha):
    return git_text("show", "-s", "--format=%P", commit_sha).strip().split()


def git_ls_tree_entry(commit_sha, path):
    output = git_text("ls-tree", commit_sha, "--", path).strip()
    if not output:
        return None
    metadata, observed_path = output.split("\t", 1)
    mode, object_type, object_sha = metadata.split()
    return {
        "mode": mode,
        "object_type": object_type,
        "object_sha": object_sha,
        "path": observed_path,
    }


def canonical_git_blob_sha256(blob_sha):
    raw = git_bytes("cat-file", "blob", blob_sha)
    return hashlib.sha256(canonicalize_utf8_repository_text(raw)).hexdigest()


def git_candidate_changes():
    output = git_text(
        "diff-tree",
        "--no-commit-id",
        "--name-status",
        "-r",
        "-M",
        "-C",
        SOURCE_BASELINE_SHA,
        E1_CANDIDATE_SHA,
    )
    changes = []
    for line in output.splitlines():
        columns = line.split("\t")
        status = columns[0]
        if status.startswith(("R", "C")):
            previous_path, path = columns[1:]
        else:
            previous_path = None
            path = columns[1]
        changes.append((status, previous_path, path))
    return changes


class E2ContractAndSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_json(SCHEMA_PATH)
        cls.contract = CONTRACT_PATH.read_text(encoding="utf-8")

    def test_01_schema_is_strict_draft_2020_12_with_nine_document_kinds(self):
        self.assertEqual(
            self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema"
        )
        self.assertEqual(len(self.schema["oneOf"]), 9)
        for name in (
            "releaseProofManifest",
            "candidatePathManifest",
            "mergePathManifest",
            "continuityRecord",
            "e1ReceiptLinkage",
            "releaseBoundaryRegister",
            "pullRequestObservation",
            "externalVerificationReceipt",
            "syntheticScenario",
        ):
            self.assertFalse(self.schema["$defs"][name]["additionalProperties"])

    def test_02_schema_distinguishes_git_object_and_sha256_shapes(self):
        self.assertEqual(
            self.schema["$defs"]["gitObjectSha"]["pattern"], "^[0-9a-f]{40}$"
        )
        self.assertEqual(
            self.schema["$defs"]["sha256"]["pattern"], "^[0-9a-f]{64}$"
        )

    def test_03_all_maintained_records_validate_against_schema(self):
        for path in (
            MANIFEST_PATH,
            CANDIDATE_PATH,
            MERGE_PATH,
            CONTINUITY_PATH,
            E1_RECEIPT_PATH,
            BOUNDARY_PATH,
        ):
            with self.subTest(path=path.name):
                self.assertEqual(
                    validate_draft_2020_12_subset(load_json(path), self.schema), []
                )

    def test_04_all_standalone_scenarios_validate_against_schema(self):
        self.assertEqual(len(SCENARIO_PATHS), 40)
        for path in SCENARIO_PATHS:
            with self.subTest(path=path.name):
                self.assertEqual(
                    validate_draft_2020_12_subset(load_json(path), self.schema), []
                )

    def test_05_external_verification_receipt_contract_validates(self):
        receipt = build_external_e2_receipt()
        self.assertEqual(
            validate_draft_2020_12_subset(receipt, self.schema), []
        )

    def test_05b_external_pr_observation_contract_validates(self):
        observation = build_external_pr_observation()
        self.assertEqual(
            validate_draft_2020_12_subset(observation, self.schema), []
        )

    def test_06_schema_rejects_additional_properties(self):
        manifest = load_json(MANIFEST_PATH)
        manifest["unexpected"] = True
        self.assertTrue(validate_draft_2020_12_subset(manifest, self.schema))

    def test_07_schema_rejects_self_referential_candidate_head(self):
        manifest = load_json(MANIFEST_PATH)
        manifest["execution_candidate_head_sha"] = SYNTHETIC_E2_CANDIDATE_SHA
        self.assertTrue(validate_draft_2020_12_subset(manifest, self.schema))

    def test_08_schema_rejects_authorized_future_candidate(self):
        boundaries = load_json(BOUNDARY_PATH)
        boundaries["future_release_candidate"]["state"] = "approved"
        self.assertTrue(validate_draft_2020_12_subset(boundaries, self.schema))

    def test_09_contract_states_all_required_non_authoritative_boundaries(self):
        required_text = (
            "#231 remains Open",
            "M15 remains active and incomplete",
            "Track E3 and Track E4 are not implemented",
            "v0.14.0 remains unpublished",
            "Decision Proof sealing and Learning Proof sealing remain AAOS-owned",
            "AAOS remains the decision sovereignty layer",
            "does not create a tag or GitHub Release",
        )
        for text in required_text:
            with self.subTest(text=text):
                self.assertIn(text, self.contract)

    def test_10_contract_declares_caller_data_only_runtime_prohibitions(self):
        for text in (
            "accepts only caller-supplied inert mappings",
            "import `pathlib`",
            "inspect Git or invoke Git commands",
            "access GitHub or any network",
            "subprocess or shell execution",
            "calculate repository or receipt digests",
            "mutate files, caller mappings, Git, GitHub, or external state",
        ):
            with self.subTest(text=text):
                self.assertIn(text, self.contract)

    def test_11_schema_fixes_observation_and_receipt_to_pr_249(self):
        observation = build_external_pr_observation(pull_request_number=250)
        self.assertTrue(
            validate_draft_2020_12_subset(observation, self.schema)
        )
        receipt = build_external_e2_receipt(pull_request_number=250)
        self.assertTrue(validate_draft_2020_12_subset(receipt, self.schema))

    def test_12_contract_defines_observation_and_minimum_coverage_boundaries(self):
        for text in (
            "## External Pull-Request Candidate Observation",
            "human reviewer must independently compare",
            "does not query GitHub",
            "## Minimum Verification Coverage",
            "tests_observed >= minimum_tests_observed",
            "A count below the minimum fails closed",
        ):
            with self.subTest(text=text):
                self.assertIn(text, self.contract)


class HistoricalGitObjectEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate_manifest = load_json(CANDIDATE_PATH)
        cls.merge_manifest = load_json(MERGE_PATH)
        cls.continuity = load_json(CONTINUITY_PATH)

    def test_01_all_fixed_historical_objects_exist_with_expected_types(self):
        for sha, object_type in (
            (SOURCE_BASELINE_SHA, "commit"),
            (SOURCE_BASELINE_TREE_SHA, "tree"),
            (E1_CANDIDATE_SHA, "commit"),
            (E1_CANDIDATE_TREE_SHA, "tree"),
            (E1_MERGE_SHA, "commit"),
            (E1_MERGE_TREE_SHA, "tree"),
        ):
            with self.subTest(sha=sha):
                self.assertEqual(git_text("cat-file", "-t", sha).strip(), object_type)

    def test_02_source_candidate_and_merge_tree_bindings_are_observed(self):
        self.assertEqual(git_tree(SOURCE_BASELINE_SHA), SOURCE_BASELINE_TREE_SHA)
        self.assertEqual(git_tree(E1_CANDIDATE_SHA), E1_CANDIDATE_TREE_SHA)
        self.assertEqual(git_tree(E1_MERGE_SHA), E1_MERGE_TREE_SHA)

    def test_03_merge_parents_include_exact_source_baseline_and_candidate(self):
        self.assertEqual(
            git_parents(E1_MERGE_SHA), [SOURCE_BASELINE_SHA, E1_CANDIDATE_SHA]
        )
        self.assertEqual(
            self.continuity["merge_parent_shas"],
            [SOURCE_BASELINE_SHA, E1_CANDIDATE_SHA],
        )

    def test_04_starting_main_is_recorded_as_observed_e1_merge_result(self):
        self.assertEqual(STARTING_MAIN_SHA, E1_MERGE_SHA)
        self.assertEqual(STARTING_MAIN_TREE_SHA, git_tree(STARTING_MAIN_SHA))
        self.assertEqual(E1_CANDIDATE_TREE_SHA, E1_MERGE_TREE_SHA)

    def test_05_git_history_derives_exactly_39_changed_paths(self):
        changes = git_candidate_changes()
        self.assertEqual(len(changes), 39)
        self.assertEqual(Counter(status for status, _, _ in changes), {"A": 39})
        self.assertEqual(
            {path for _, _, path in changes},
            {entry["path"] for entry in self.candidate_manifest["paths"]},
        )

    def test_06_candidate_manifest_records_every_git_blob_digest_and_mode(self):
        for entry in self.candidate_manifest["paths"]:
            with self.subTest(path=entry["path"]):
                observed = git_ls_tree_entry(E1_CANDIDATE_SHA, entry["path"])
                self.assertIsNotNone(observed)
                self.assertEqual(observed["object_type"], "blob")
                self.assertEqual(observed["path"], entry["path"])
                self.assertEqual(observed["object_sha"], entry["candidate_blob_sha"])
                self.assertEqual(observed["mode"], entry["candidate_file_mode"])
                self.assertEqual(
                    canonical_git_blob_sha256(observed["object_sha"]),
                    entry["candidate_canonical_sha256"],
                )

    def test_07_merge_manifest_records_every_git_blob_digest_and_mode(self):
        for entry in self.merge_manifest["paths"]:
            with self.subTest(path=entry["path"]):
                observed = git_ls_tree_entry(E1_MERGE_SHA, entry["path"])
                self.assertIsNotNone(observed)
                self.assertEqual(observed["object_type"], "blob")
                self.assertEqual(observed["object_sha"], entry["merge_blob_sha"])
                self.assertEqual(observed["mode"], entry["merge_file_mode"])
                self.assertEqual(
                    canonical_git_blob_sha256(observed["object_sha"]),
                    entry["merge_canonical_sha256"],
                )

    def test_08_every_candidate_path_is_preserved_without_substitution(self):
        candidate = {entry["path"]: entry for entry in self.candidate_manifest["paths"]}
        merge = {entry["path"]: entry for entry in self.merge_manifest["paths"]}
        self.assertEqual(candidate.keys(), merge.keys())
        for path in candidate:
            with self.subTest(path=path):
                self.assertEqual(candidate[path]["path_id"], merge[path]["path_id"])
                self.assertEqual(
                    candidate[path]["candidate_blob_sha"], merge[path]["merge_blob_sha"]
                )
                self.assertEqual(
                    candidate[path]["candidate_canonical_sha256"],
                    merge[path]["merge_canonical_sha256"],
                )
                self.assertEqual(
                    candidate[path]["candidate_file_mode"],
                    merge[path]["merge_file_mode"],
                )

    def test_09_continuity_summary_reconciles_all_zero_drift_counts(self):
        self.assertEqual(self.continuity["preserved_path_count"], 39)
        self.assertTrue(self.continuity["complete_path_coverage"])
        self.assertEqual(self.continuity["missing_paths"], [])
        self.assertEqual(self.continuity["blob_mismatches"], [])
        self.assertEqual(self.continuity["digest_mismatches"], [])
        self.assertEqual(self.continuity["file_mode_mismatches"], [])
        self.assertEqual(self.continuity["unexpected_substitutions"], [])
        self.assertEqual(self.continuity["continuity_relation"], EXACT_TREE_MATCH)

    def test_10_e1_external_receipt_binding_is_exact_and_non_authoritative(self):
        receipt = load_json(E1_RECEIPT_PATH)
        self.assertEqual(receipt["source_pull_request_number"], 243)
        self.assertEqual(receipt["source_comment_id"], 5015070053)
        self.assertEqual(receipt["source_baseline_commit_sha"], SOURCE_BASELINE_SHA)
        self.assertEqual(receipt["candidate_commit_sha"], E1_CANDIDATE_SHA)
        self.assertEqual(receipt["command_count"], 13)
        self.assertEqual(
            receipt["canonical_receipt_json_sha256"], E1_EXTERNAL_RECEIPT_SHA256
        )
        self.assertFalse(receipt["treated_as_merge_approval"])
        self.assertFalse(receipt["fetched_by_evaluator"])


class MaintainedReleaseProofEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.package = load_package()

    def assert_blocked_after(self, mutation, finding_fragment=None):
        mutation(self.package)
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertFalse(result["release_proof_linked"])
        if finding_fragment is not None:
            self.assertTrue(
                any(finding_fragment in item for item in result["blocking_findings"]),
                result["blocking_findings"],
            )
        return result

    def test_01_complete_package_with_external_receipt_is_linked(self):
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], RELEASE_PROOF_LINKED)
        self.assertTrue(result["release_proof_linked"])
        self.assertEqual(result["continuity_relation"], EXACT_TREE_MATCH)
        self.assertEqual(result["candidate_changed_path_count"], 39)
        self.assertEqual(result["merge_result_path_count"], 39)
        self.assertEqual(result["preserved_path_count"], 39)
        self.assertTrue(result["external_pr_observation_validated"])
        self.assertEqual(result["observed_pull_request_number"], 249)
        self.assertEqual(
            result["observed_candidate_head_sha"],
            self.package["external_verification_receipt"][
                "execution_candidate_head_sha"
            ],
        )
        self.assertEqual(
            result["observed_candidate_tree_sha"],
            SYNTHETIC_E2_CANDIDATE_TREE_SHA,
        )
        self.assertTrue(result["external_verification_receipt_validated"])
        self.assertEqual(result["e2_linkage_blockers"], [])

    def test_02_linked_result_keeps_all_future_prerequisites_open_and_visible(self):
        result = evaluate_package(self.package)
        self.assertEqual(
            result["future_release_prerequisites"],
            list(REQUIRED_FUTURE_PREREQUISITES),
        )
        self.assertEqual(result["tracker_231_state"], "open")
        self.assertEqual(result["m15_state"], "active-and-incomplete")
        self.assertEqual(result["v0_14_0_state"], "unpublished")
        self.assertFalse(result["track_e3_implemented"])
        self.assertFalse(result["track_e4_implemented"])

    def test_03_missing_external_e2_receipt_is_not_ready(self):
        self.package["external_verification_receipt"] = None
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], NOT_READY)
        self.assertIn(
            "external_e2_verification_receipt_missing", result["readiness_findings"]
        )

    def test_04_candidate_head_mismatch_blocks(self):
        self.assert_blocked_after(
            lambda p: p["candidate_path_manifest"].__setitem__(
                "candidate_commit_sha", "d" * 40
            ),
            "candidate_manifest_binding_mismatch:candidate_commit_sha",
        )

    def test_05_candidate_tree_mismatch_blocks(self):
        self.assert_blocked_after(
            lambda p: p["candidate_path_manifest"].__setitem__(
                "candidate_tree_sha", "d" * 40
            ),
            "candidate_manifest_binding_mismatch:candidate_tree_sha",
        )

    def test_06_merge_commit_mismatch_blocks(self):
        self.assert_blocked_after(
            lambda p: p["merge_path_manifest"].__setitem__(
                "merge_commit_sha", "d" * 40
            ),
            "merge_manifest_binding_mismatch:merge_commit_sha",
        )

    def test_07_missing_merge_tree_blocks(self):
        self.assert_blocked_after(
            lambda p: p["continuity_record"].__setitem__("merge_tree_sha", None),
            "continuity_record_binding_mismatch:merge_tree_sha",
        )

    def test_08_required_candidate_path_missing_after_merge_blocks(self):
        self.package["merge_path_manifest"]["paths"].pop()
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn("incomplete-path-coverage", result["e2_linkage_blockers"])

    def test_09_candidate_merge_blob_mismatch_blocks(self):
        self.package["merge_path_manifest"]["paths"][0]["merge_blob_sha"] = "d" * 40
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn(
            "unexplained-digest-or-mode-drift", result["e2_linkage_blockers"]
        )

    def test_10_canonical_digest_mismatch_blocks(self):
        self.package["merge_path_manifest"]["paths"][0][
            "merge_canonical_sha256"
        ] = "d" * 64
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn(
            "unexplained-digest-or-mode-drift", result["e2_linkage_blockers"]
        )

    def test_11_file_mode_mismatch_blocks(self):
        self.package["merge_path_manifest"]["paths"][0]["merge_file_mode"] = "100755"
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn(
            "unexplained-digest-or-mode-drift", result["e2_linkage_blockers"]
        )

    def test_12_unexpected_path_substitution_blocks(self):
        self.package["merge_path_manifest"]["paths"][0]["path"] = "substitute.json"
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn("incomplete-path-coverage", result["e2_linkage_blockers"])

    def test_13_incomplete_candidate_manifest_blocks(self):
        self.package["candidate_path_manifest"]["paths"].pop()
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn("incomplete-path-coverage", result["e2_linkage_blockers"])

    def test_14_incomplete_merge_manifest_blocks(self):
        self.package["merge_path_manifest"]["paths"].pop(0)
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn("incomplete-path-coverage", result["e2_linkage_blockers"])

    def test_15_missing_e1_receipt_linkage_blocks(self):
        self.package["e1_receipt_linkage"] = {}
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn("missing-receipt-binding", result["e2_linkage_blockers"])

    def test_16_e1_receipt_digest_mismatch_blocks(self):
        self.package["e1_receipt_linkage"]["canonical_receipt_json_sha256"] = "d" * 64
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn("missing-receipt-binding", result["e2_linkage_blockers"])

    def test_17_e1_receipt_bound_to_another_candidate_blocks(self):
        self.package["e1_receipt_linkage"]["candidate_commit_sha"] = "d" * 40
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn("missing-receipt-binding", result["e2_linkage_blockers"])

    def test_18_e1_receipt_bound_to_another_baseline_blocks(self):
        self.package["e1_receipt_linkage"]["source_baseline_commit_sha"] = "d" * 40
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn("missing-receipt-binding", result["e2_linkage_blockers"])

    def test_19_e1_receipt_cannot_be_merge_approval(self):
        self.package["e1_receipt_linkage"]["treated_as_merge_approval"] = True
        self.assertEqual(evaluate_package(self.package)["outcome"], BLOCKED)

    def test_20_source_and_candidate_identity_conflation_blocks(self):
        self.package["manifest"]["historical_bindings"][
            "e1_candidate_commit_sha"
        ] = SOURCE_BASELINE_SHA
        self.assertEqual(evaluate_package(self.package)["outcome"], BLOCKED)

    def test_21_candidate_and_merge_identity_conflation_blocks(self):
        self.package["manifest"]["historical_bindings"][
            "e1_merge_commit_sha"
        ] = E1_CANDIDATE_SHA
        self.assertEqual(evaluate_package(self.package)["outcome"], BLOCKED)

    def test_22_omitted_linkage_blocker_blocks(self):
        self.package["release_boundary_register"]["e2_linkage_blockers"].pop()
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn("missing-continuity-evidence", result["e2_linkage_blockers"])

    def test_23_unresolved_linkage_blocker_blocks(self):
        self.package["release_boundary_register"]["e2_linkage_blockers"][0][
            "state"
        ] = "open"
        self.assertEqual(evaluate_package(self.package)["outcome"], BLOCKED)

    def test_24_future_release_prerequisite_cannot_be_silently_resolved(self):
        self.package["release_boundary_register"]["future_release_prerequisites"][0][
            "state"
        ] = "resolved"
        self.assertEqual(evaluate_package(self.package)["outcome"], BLOCKED)

    def test_25_tracker_231_cannot_be_closed(self):
        self.package["release_boundary_register"]["governance_boundary"][
            "tracker_231_state"
        ] = "closed"
        self.assertEqual(evaluate_package(self.package)["outcome"], BLOCKED)

    def test_26_m15_cannot_be_complete(self):
        self.package["release_boundary_register"]["governance_boundary"][
            "m15_state"
        ] = "complete"
        self.assertEqual(evaluate_package(self.package)["outcome"], BLOCKED)

    def test_27_readme_completion_cannot_be_authorized(self):
        self.package["release_boundary_register"]["governance_boundary"][
            "readme_completion_authorized"
        ] = True
        self.assertEqual(evaluate_package(self.package)["outcome"], BLOCKED)

    def test_28_v0_14_0_cannot_be_tagged(self):
        self.package["release_boundary_register"]["governance_boundary"][
            "v0_14_0_tag_state"
        ] = "tagged"
        self.assertEqual(evaluate_package(self.package)["outcome"], BLOCKED)

    def test_29_github_release_cannot_be_published_or_latest(self):
        governance = self.package["release_boundary_register"]["governance_boundary"]
        governance["github_release_state"] = "published"
        governance["github_release_latest"] = True
        self.assertEqual(evaluate_package(self.package)["outcome"], BLOCKED)

    def test_30_decision_or_learning_proof_sealing_claim_blocks(self):
        governance = self.package["release_boundary_register"]["governance_boundary"]
        governance["decision_proof_sealed"] = True
        governance["learning_proof_sealed"] = True
        self.assertEqual(evaluate_package(self.package)["outcome"], BLOCKED)

    def test_31_completion_release_risk_waiver_or_audit_authority_blocks(self):
        governance = self.package["release_boundary_register"]["governance_boundary"]
        for field in (
            "completion_approved",
            "release_candidate_approved",
            "tag_authorized",
            "github_release_authorized",
            "deployment_authorized",
            "risk_accepted",
            "audit_closed",
            "waiver_granted",
            "authority_transferred",
        ):
            governance[field] = True
        self.assertEqual(evaluate_package(self.package)["outcome"], BLOCKED)

    def test_32_external_receipt_bound_to_other_candidate_blocks(self):
        self.package["external_verification_receipt"][
            "execution_candidate_head_sha"
        ] = "d" * 40
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertFalse(result["external_verification_receipt_validated"])

    def test_33_external_receipt_command_coverage_must_be_complete(self):
        self.package["external_verification_receipt"]["commands"].pop()
        self.assertEqual(evaluate_package(self.package)["outcome"], BLOCKED)

    def test_34_external_receipt_argv_must_match_declaration(self):
        self.package["external_verification_receipt"]["commands"][0][
            "declared_logical_argv"
        ].append("unexpected")
        self.assertEqual(evaluate_package(self.package)["outcome"], BLOCKED)

    def test_35_external_receipt_failures_errors_skips_and_exit_fail_closed(self):
        command = self.package["external_verification_receipt"]["commands"][0]
        command.update(
            {
                "tests_observed": 4,
                "passes": 1,
                "failures": 1,
                "errors": 1,
                "skips": 1,
                "exit_code": 1,
            }
        )
        self.assertEqual(evaluate_package(self.package)["outcome"], BLOCKED)

    def test_36_external_receipt_is_never_execution_or_release_authority(self):
        command = self.package["external_verification_receipt"]["commands"][0]
        command["executed_by_evaluator"] = True
        command["verification_results_are_release_authority"] = True
        self.assertEqual(evaluate_package(self.package)["outcome"], BLOCKED)

    def test_37_evaluator_does_not_mutate_any_caller_mapping(self):
        original = copy.deepcopy(self.package)
        evaluate_package(self.package)
        self.assertEqual(self.package, original)

    def test_38_result_reports_all_prohibited_operations_as_not_performed(self):
        result = evaluate_package(self.package)
        for field in (
            "file_io_performed",
            "git_inspection_performed",
            "github_access_performed",
            "repository_digests_calculated",
            "verification_commands_executed",
            "external_state_mutated",
        ):
            with self.subTest(field=field):
                self.assertFalse(result[field])
        self.assertTrue(result["caller_data_only"])
        self.assertEqual(
            result["non_authoritative_boundary_statement"],
            NON_AUTHORITATIVE_BOUNDARY_STATEMENT,
        )

    def test_39_missing_external_pr_observation_is_not_ready(self):
        self.package["pull_request_observation"] = None
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], NOT_READY)
        self.assertIn(
            "external_pr_observation_missing", result["readiness_findings"]
        )
        self.assertFalse(result["external_pr_observation_validated"])
        self.assertFalse(result["external_verification_receipt_validated"])

    def test_40_observation_and_receipt_for_another_pr_are_blocked(self):
        observation = self.package["pull_request_observation"]
        observation["pull_request_number"] = 250
        receipt = self.package["external_verification_receipt"]
        receipt["pull_request_number"] = 250
        receipt["execution_candidate_reference"] = "pull-request:#250"
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn(
            "external_pr_observation_mismatch:pull_request_number",
            result["blocking_findings"],
        )

    def test_41_observation_and_receipt_candidate_head_mismatch_blocks(self):
        receipt = self.package["external_verification_receipt"]
        other_candidate = "b" * 40
        receipt["execution_candidate_head_sha"] = other_candidate
        for command in receipt["commands"]:
            command["execution_candidate_head_sha"] = other_candidate
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn(
            "external_e2_verification_receipt_observation_candidate_mismatch",
            result["blocking_findings"],
        )

    def test_42_observation_candidate_cannot_equal_base(self):
        self.package["pull_request_observation"][
            "candidate_head_sha"
        ] = STARTING_MAIN_SHA
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn(
            "external_pr_observation_candidate_equals_base",
            result["blocking_findings"],
        )

    def test_43_observation_extra_field_blocks(self):
        self.package["pull_request_observation"]["unexpected"] = True
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn(
            "external_pr_observation_shape_invalid", result["blocking_findings"]
        )

    def test_44_observation_claiming_evaluator_fetch_blocks(self):
        self.package["pull_request_observation"]["fetched_by_evaluator"] = True
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn(
            "external_pr_observation_fetched_by_evaluator",
            result["blocking_findings"],
        )

    def test_45_full_suite_one_test_cannot_link(self):
        command = next(
            item
            for item in self.package["external_verification_receipt"]["commands"]
            if item["command_id"] == "run_full_maintained_repository_suite"
        )
        command["tests_observed"] = 1
        command["passes"] = 1
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn(
            "external_e2_verification_test_coverage_below_minimum:"
            "run_full_maintained_repository_suite",
            result["blocking_findings"],
        )

    def test_46_e2_targeted_count_below_minimum_blocks(self):
        command = self.package["external_verification_receipt"]["commands"][0]
        minimum = EXPECTED_VERIFICATION_COMMANDS[command["command_id"]][
            "minimum_tests_observed"
        ]
        command["tests_observed"] = minimum - 1
        command["passes"] = minimum - 1
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn(
            "external_e2_verification_test_coverage_below_minimum:"
            "run_m15_e2_targeted_tests",
            result["blocking_findings"],
        )

    def test_47_count_exactly_at_minimum_links(self):
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], RELEASE_PROOF_LINKED)

    def test_48_count_above_minimum_links(self):
        command = self.package["external_verification_receipt"]["commands"][0]
        command["tests_observed"] += 1
        command["passes"] += 1
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], RELEASE_PROOF_LINKED)

    def test_49_count_arithmetic_mismatch_blocks(self):
        command = self.package["external_verification_receipt"]["commands"][0]
        command["passes"] -= 1
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn(
            "external_e2_verification_count_arithmetic_invalid:"
            "run_m15_e2_targeted_tests",
            result["blocking_findings"],
        )

    def test_50_failure_error_and_nonzero_exit_block(self):
        command = self.package["external_verification_receipt"]["commands"][0]
        command["passes"] -= 2
        command["failures"] = 1
        command["errors"] = 1
        command["exit_code"] = 1
        self.assertEqual(evaluate_package(self.package)["outcome"], BLOCKED)

    def test_51_skip_is_not_ready_and_cannot_link(self):
        command = self.package["external_verification_receipt"]["commands"][0]
        command["passes"] -= 1
        command["skips"] = 1
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], NOT_READY)
        self.assertIn(
            "external_e2_verification_skips_present:run_m15_e2_targeted_tests",
            result["readiness_findings"],
        )

    def test_52_observation_and_receipt_are_not_mutated(self):
        observation = copy.deepcopy(self.package["pull_request_observation"])
        receipt = copy.deepcopy(self.package["external_verification_receipt"])
        evaluate_package(self.package)
        self.assertEqual(self.package["pull_request_observation"], observation)
        self.assertEqual(self.package["external_verification_receipt"], receipt)

    def test_53_observation_must_be_commit_external(self):
        self.package["pull_request_observation"][
            "external_to_candidate_commit"
        ] = False
        result = evaluate_package(self.package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn(
            "external_pr_observation_not_commit_external",
            result["blocking_findings"],
        )


class PathContinuitySemanticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate = load_json(CANDIDATE_PATH)["paths"][0]
        cls.merge = load_json(MERGE_PATH)["paths"][0]

    def entries(self):
        return copy.deepcopy(self.candidate), copy.deepcopy(self.merge)

    def assert_preserved(self, candidate, merge):
        self.assertEqual(
            evaluate_path_continuity(candidate, merge),
            {"continuity_status": "preserved", "findings": []},
        )

    def test_01_addition_is_preserved(self):
        candidate, merge = self.entries()
        self.assert_preserved(candidate, merge)

    def test_02_modification_is_preserved_with_baseline_blob(self):
        candidate, merge = self.entries()
        candidate.update(
            {
                "change_type": "modification",
                "baseline_blob_sha": "b" * 40,
            }
        )
        merge["source_change_type"] = "modification"
        self.assert_preserved(candidate, merge)

    def test_03_rename_is_preserved_with_previous_path_and_baseline_blob(self):
        candidate, merge = self.entries()
        candidate.update(
            {
                "change_type": "rename",
                "previous_path": "synthetic/previous.json",
                "baseline_blob_sha": "b" * 40,
            }
        )
        merge["source_change_type"] = "rename"
        self.assert_preserved(candidate, merge)

    def test_04_deletion_is_preserved_only_as_absent(self):
        candidate, merge = self.entries()
        candidate.update(
            {
                "change_type": "deletion",
                "baseline_blob_sha": "b" * 40,
                "candidate_blob_sha": None,
                "candidate_canonical_sha256": None,
                "candidate_file_mode": None,
            }
        )
        merge.update(
            {
                "source_change_type": "deletion",
                "merge_blob_sha": None,
                "merge_canonical_sha256": None,
                "merge_file_mode": None,
                "presence_state": "absent",
            }
        )
        self.assert_preserved(candidate, merge)

    def test_05_required_non_deletion_path_missing_after_merge_drifts(self):
        candidate, merge = self.entries()
        merge["presence_state"] = "absent"
        result = evaluate_path_continuity(candidate, merge)
        self.assertEqual(result["continuity_status"], "drifted")
        self.assertIn("required_path_missing_after_merge", result["findings"])

    def test_06_blob_digest_and_mode_drift_are_independent_findings(self):
        candidate, merge = self.entries()
        merge["merge_blob_sha"] = "d" * 40
        merge["merge_canonical_sha256"] = "d" * 64
        merge["merge_file_mode"] = "100755"
        result = evaluate_path_continuity(candidate, merge)
        self.assertEqual(result["continuity_status"], "drifted")
        self.assertIn("blob_mismatch", result["findings"])
        self.assertIn("canonical_digest_mismatch", result["findings"])
        self.assertIn("file_mode_mismatch", result["findings"])

    def test_07_path_substitution_is_rejected(self):
        candidate, merge = self.entries()
        merge["path"] = "synthetic/substitute.json"
        result = evaluate_path_continuity(candidate, merge)
        self.assertEqual(result["continuity_status"], "drifted")
        self.assertIn("path_substitution", result["findings"])

    def test_08_change_type_semantics_fail_closed(self):
        candidate, merge = self.entries()
        candidate["change_type"] = "rename"
        merge["source_change_type"] = "rename"
        result = evaluate_path_continuity(candidate, merge)
        self.assertEqual(result["continuity_status"], "drifted")
        self.assertIn("rename_baseline_semantics_invalid", result["findings"])

    def test_09_candidate_or_merge_shape_with_extra_field_is_unverified(self):
        candidate, merge = self.entries()
        candidate["unexpected"] = True
        self.assertEqual(
            evaluate_path_continuity(candidate, merge),
            {
                "continuity_status": "unverified",
                "findings": ["candidate_path_shape_invalid"],
            },
        )


class SyntheticScenarioInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.by_number = {
            int(path.name.split("-")[4]): load_json(path) for path in SCENARIO_PATHS
        }

    def test_00_inventory_is_complete_standalone_and_synthetic(self):
        self.assertEqual(set(self.by_number), set(range(1, 41)))
        self.assertEqual(len(SCENARIO_PATHS), 40)
        self.assertEqual(len({path.name for path in SCENARIO_PATHS}), 40)
        for number, document in self.by_number.items():
            with self.subTest(number=number):
                self.assertTrue(document["synthetic"])
                self.assertEqual(document["document_type"], "synthetic-scenario")
                self.assertEqual(document["notes"], SCENARIO_BOUNDARY_STATEMENT)
                self.assertEqual(
                    document["title"],
                    EXPECTED_SCENARIO_TITLES[f"m15-e2-{number:02d}"],
                )

    def test_37_scenarios_contain_no_executable_payload_or_secret_fields(self):
        forbidden_keys = {
            "credential",
            "credentials",
            "password",
            "secret",
            "token",
            "api_key",
            "private_prompt",
            "executable",
            "command",
            "argv",
            "script",
        }

        def keys(value):
            if isinstance(value, dict):
                for key, nested in value.items():
                    yield key
                    yield from keys(nested)
            elif isinstance(value, list):
                for nested in value:
                    yield from keys(nested)

        for number, document in self.by_number.items():
            with self.subTest(number=number):
                self.assertFalse(set(keys(document)) & forbidden_keys)

    def test_38_required_first_30_issue_scenarios_are_present(self):
        required_fragments = {
            1: "Exact E1 candidate and merge tree match",
            2: "explained base advancement",
            3: "candidate head mismatch",
            4: "candidate tree mismatch",
            5: "merge commit mismatch",
            6: "merge tree is missing",
            7: "path is missing after merge",
            8: "blob mismatch",
            9: "canonical digest mismatch",
            10: "file mode mismatch",
            11: "path substitution",
            12: "Incomplete candidate",
            13: "Incomplete merge-result",
            14: "Missing E1 external receipt",
            15: "receipt digest mismatch",
            16: "another candidate",
            17: "another baseline",
            18: "merge approval",
            19: "human approval",
            20: "completion approval",
            21: "published release",
            22: "represented as tagged",
            23: "represented as published",
            24: "represented as closed",
            25: "represented as complete",
            26: "represented as authorized",
            27: "linkage blocker omitted",
            28: "Unverified continuity treated as linked",
            29: "identifier is missing",
            30: "Decision Proof or Learning Proof sealing",
        }
        for number, fragment in required_fragments.items():
            with self.subTest(number=number):
                self.assertIn(fragment.lower(), self.by_number[number]["title"].lower())

    def test_39_hardening_scenarios_are_present(self):
        required_fragments = {
            37: "observation is missing",
            38: "another PR",
            39: "candidate heads mismatch",
            40: "below maintained minimum",
        }
        for number, fragment in required_fragments.items():
            with self.subTest(number=number):
                self.assertIn(fragment.lower(), self.by_number[number]["title"].lower())


def _make_scenario_test(number):
    def test(self):
        document = self.by_number[number]
        original = copy.deepcopy(document)
        first = evaluate_synthetic_scenario(document)
        second = evaluate_synthetic_scenario(document)
        self.assertEqual(first, second)
        self.assertEqual(document, original)
        self.assertEqual(first["outcome"], document["expected_outcome"])
        self.assertEqual(first["continuity_relation"], document["expected_relation"])
        self.assertEqual(first["tracker_231_state"], "open")
        self.assertEqual(first["m15_state"], "active-and-incomplete")
        self.assertEqual(first["v0_14_0_state"], "unpublished")
        self.assertFalse(first["track_e3_implemented"])
        self.assertFalse(first["track_e4_implemented"])

    test.__name__ = f"test_{number:02d}_standalone_scenario"
    return test


for _scenario_number in range(1, 41):
    setattr(
        SyntheticScenarioInventoryTests,
        f"test_{_scenario_number:02d}_standalone_scenario",
        _make_scenario_test(_scenario_number),
    )


class RuntimeEvaluatorBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = EVALUATOR_PATH.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_01_public_evaluator_accepts_only_eight_caller_supplied_mappings(self):
        signature = inspect.signature(evaluate_release_proof_linkage)
        self.assertEqual(
            list(signature.parameters),
            [
                "manifest",
                "candidate_path_manifest",
                "merge_path_manifest",
                "continuity_record",
                "e1_receipt_linkage",
                "release_boundary_register",
                "pull_request_observation",
                "external_verification_receipt",
            ],
        )

    def test_02_runtime_has_no_file_git_github_network_or_process_imports(self):
        imported = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        banned = {
            "hashlib",
            "http",
            "io",
            "json",
            "os",
            "pathlib",
            "requests",
            "shutil",
            "socket",
            "subprocess",
            "urllib",
        }
        self.assertFalse(imported & banned, imported & banned)

    def test_03_runtime_has_no_file_process_network_digest_or_mutation_calls(self):
        banned_names = {
            "breakpoint",
            "compile",
            "eval",
            "exec",
            "open",
            "remove",
            "rename",
            "replace",
            "unlink",
        }
        banned_attributes = {
            "Popen",
            "check_call",
            "check_output",
            "connect",
            "create_connection",
            "digest",
            "hexdigest",
            "open",
            "read_bytes",
            "read_text",
            "request",
            "run",
            "sha256",
            "system",
            "urlopen",
            "write_bytes",
            "write_text",
        }
        names = set()
        attributes = set()
        for node in ast.walk(self.tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name):
                names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                attributes.add(node.func.attr)
        self.assertFalse(names & banned_names, names & banned_names)
        self.assertFalse(attributes & banned_attributes, attributes & banned_attributes)

    def test_04_runtime_does_not_reference_repository_paths_or_git_commands(self):
        forbidden_literals = (
            ".git/",
            "git diff",
            "git show",
            "git ls-tree",
            "github.com",
            "api.github",
        )
        for literal in forbidden_literals:
            with self.subTest(literal=literal):
                self.assertNotIn(literal, self.source.lower())

    def test_05_runtime_expected_path_inventory_is_exact_and_closed(self):
        candidate = load_json(CANDIDATE_PATH)
        self.assertEqual(len(EXPECTED_PATHS), 39)
        self.assertEqual(set(EXPECTED_PATHS), {row["path"] for row in candidate["paths"]})
        self.assertEqual(
            [EXPECTED_PATHS[path]["path_id"] for path in sorted(EXPECTED_PATHS)],
            [f"m15-e2-e1-path-{number:02d}" for number in range(1, 40)],
        )

    def test_06_runtime_verification_manifest_has_all_fourteen_required_groups(self):
        manifest = load_json(MANIFEST_PATH)
        commands = manifest["verification_command_manifest"]["commands"]
        self.assertEqual(len(EXPECTED_VERIFICATION_COMMANDS), 14)
        self.assertEqual(
            {command["command_id"] for command in commands},
            set(EXPECTED_VERIFICATION_COMMANDS),
        )
        self.assertTrue(all(command["executed_by_evaluator"] is False for command in commands))
        maintained = {command["command_id"]: command for command in commands}
        self.assertEqual(
            {
                command_id: expected["minimum_tests_observed"]
                for command_id, expected in EXPECTED_VERIFICATION_COMMANDS.items()
            },
            {
                command_id: command["minimum_tests_observed"]
                for command_id, command in maintained.items()
            },
        )

    def test_06b_verification_minima_are_not_lowered(self):
        self.assertEqual(
            {
                command_id: expected["minimum_tests_observed"]
                for command_id, expected in EXPECTED_VERIFICATION_COMMANDS.items()
            },
            {
                "run_m15_e2_targeted_tests": 116,
                "run_m15_e1_targeted_tests": 126,
                "run_m15_track_a_tests": 68,
                "run_m15_track_b_tests": 73,
                "run_m15_track_c_tests": 180,
                "run_m15_track_d_tests": 79,
                "run_m14_public_output_tests": 23,
                "run_m14_provenance_tests": 47,
                "run_m14_skill_admission_tests": 135,
                "run_external_evidence_admission_tests": 31,
                "run_m14_cross_control_authority_tests": 107,
                "run_decision_proof_ownership_tests": 30,
                "run_release_state_and_m15_status_tests": 17,
                "run_full_maintained_repository_suite": 1894,
            },
        )

    def test_07_runtime_outcomes_and_relations_are_closed(self):
        self.assertEqual(
            evaluator_module.OUTCOMES,
            (RELEASE_PROOF_LINKED, NOT_READY, BLOCKED),
        )
        self.assertEqual(
            evaluator_module.CONTINUITY_RELATIONS,
            (EXACT_TREE_MATCH, CANDIDATE_CHANGE_SET_PRESERVED, DRIFT_DETECTED, UNVERIFIED),
        )

    def test_08_future_candidate_is_identified_but_never_authorized(self):
        result = evaluate_package(load_package())
        self.assertEqual(
            result["future_release_candidate"],
            {
                "identifier": FUTURE_RELEASE_CANDIDATE_IDENTIFIER,
                "state": FUTURE_RELEASE_CANDIDATE_STATE,
            },
        )
        self.assertEqual(
            FUTURE_RELEASE_CANDIDATE_IDENTIFIER,
            "urn:aaos:m15:release-candidate:v0.14.0:unapproved",
        )
        self.assertEqual(FUTURE_RELEASE_CANDIDATE_STATE, "identified-not-authorized")

    def test_09_linkage_blocker_and_future_prerequisite_vocabularies_are_separate(self):
        self.assertEqual(len(REQUIRED_LINKAGE_BLOCKERS), 5)
        self.assertEqual(len(REQUIRED_FUTURE_PREREQUISITES), 7)
        self.assertFalse(set(REQUIRED_LINKAGE_BLOCKERS) & set(REQUIRED_FUTURE_PREREQUISITES))

    def test_10_evaluator_module_exports_no_repository_digest_helper(self):
        public_names = set(evaluator_module.__all__)
        self.assertFalse(
            public_names
            & {
                "canonicalize_utf8_repository_text",
                "sha256_repository_file",
                "git_bytes",
                "git_text",
            }
        )
