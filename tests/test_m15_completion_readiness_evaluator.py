import ast
import copy
import hashlib
import inspect
import json
import re
import subprocess
import unittest
from collections import Counter
from pathlib import Path

import runtime.m15_completion_readiness_evaluator as evaluator_module
from runtime.m15_completion_readiness_evaluator import (
    AUTHORIZED_HISTORICAL_COMPATIBILITY_REPAIRS,
    AUTHORIZED_PHASE_AWARE_COMPATIBILITY_REPAIR,
    AUTHORITY_BOUNDARY,
    BLOCKED,
    COMMAND_IDS,
    COMMAND_MINIMA,
    CRITERION_IDS,
    E3_AUTHORIZED_COMPATIBILITY_REPAIR,
    HISTORICAL_E1_ARTIFACT_BINDING,
    NOT_READY,
    READY,
    REQUIRED_BLOCKERS,
    REQUIRED_FUTURE_PREREQUISITES,
    evaluate_completion_readiness,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "examples" / "public-integration-pack-pilot"
SCHEMA_PATH = ROOT / "schemas" / "m15-completion-readiness.schema.json"
CONTRACT_PATH = (
    ROOT
    / "docs"
    / "learning-governance"
    / "m15-completion-readiness-contract.md"
)
EVALUATOR_PATH = ROOT / "runtime" / "m15_completion_readiness_evaluator.py"
README_PATH = ROOT / "README.md"

RECORD_PATHS = {
    "manifest": FIXTURE_ROOT / "m15-completion-readiness-manifest.json",
    "inventory": FIXTURE_ROOT / "m15-completion-readiness-track-evidence.json",
    "continuity": FIXTURE_ROOT / "m15-completion-readiness-e2-continuity.json",
    "external": FIXTURE_ROOT / "m15-completion-readiness-e2-external-evidence.json",
    "acceptance": FIXTURE_ROOT / "m15-completion-readiness-acceptance-coverage.json",
    "boundaries": FIXTURE_ROOT / "m15-completion-readiness-boundaries.json",
    "readme": FIXTURE_ROOT / "m15-completion-readiness-readme-observation.json",
}
SCENARIO_PATHS = sorted(
    FIXTURE_ROOT.glob("m15-completion-readiness-[0-9][0-9]-*.json")
)
SOURCE_MAIN_BASE_SHA = "f6d074fca2fedecbf654697719179440bc0680d3"
SOURCE_MAIN_BASE_TREE_SHA = "f13913426545b77616128223cd195487a415ffde"
E2_BASE_SHA = "27c92e290cf6ad60bada49b63fe1888511930980"
E2_CANDIDATE_SHA = "efc31e7d24c26d2cea2cb536a4cae257aababb5f"
E2_TREE_SHA = "f13913426545b77616128223cd195487a415ffde"
E2_MERGE_SHA = "f6d074fca2fedecbf654697719179440bc0680d3"
SYNTHETIC_CANDIDATE_SHA = "a" * 40
SYNTHETIC_CANDIDATE_TREE_SHA = "b" * 40
SYNTHETIC_TRANSCRIPT_SHA256 = "c" * 64
ACTUAL_PYTHON_LAUNCHER = ".verification-python/python.exe"

TRACK_EXPECTATIONS = {
    "track-a": (232, 233, 7),
    "track-b": (234, 237, 13),
    "track-c": (238, 239, 18),
    "track-d": (240, 241, 29),
    "track-e1": (242, 243, 39),
    "track-e2": (248, 249, 50),
}

EXPECTED_NEXT_PHASE = """## Next Phase

M15 Tracks A–E3 provide completion-readiness evidence for final human
review.

M15 remains active and incomplete. Completion readiness is not M15
completion. Track E4 and final human completion review remain required.

v0.14.0 remains unpublished. No v0.14.0 tag or GitHub Release is
authorized or created.

Decision Proof sealing remains AAOS-owned.

Learning Proof sealing remains AAOS-owned.

AAOS remains the decision sovereignty layer.
"""


def load_json(path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def canonical_text(value):
    normalized = value.replace(b"\r\n", b"\n")
    if b"\r" in normalized:
        raise AssertionError("lone carriage return in repository text")
    normalized.decode("utf-8")
    return normalized


def canonical_sha256(value):
    return hashlib.sha256(canonical_text(value)).hexdigest()


def canonical_json_sha256(value):
    return hashlib.sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def git_bytes(*args):
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        stderr=subprocess.PIPE,
    )


def git_text(*args):
    return git_bytes(*args).decode("utf-8").strip()


def level_two_section(value, title):
    data = canonical_text(value)
    marker = f"## {title}\n".encode("utf-8")
    start = data.find(marker)
    if start < 0:
        raise AssertionError(f"README section missing: {title}")
    next_start = data.find(b"\n## ", start + len(marker))
    if next_start < 0:
        return data[start:]
    return data[start : next_start + 1]


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
    """Validate every Draft 2020-12 feature used by the maintained E3 schema."""

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
                instance,
                branch,
                root_schema=root_schema,
                path=path,
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
        if schema.get("uniqueItems"):
            encoded = [
                json.dumps(item, ensure_ascii=False, sort_keys=True)
                for item in instance
            ]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{path}: duplicate array items")
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


def load_records():
    return {name: load_json(path) for name, path in RECORD_PATHS.items()}


def build_external_pr_observation(
    *,
    candidate_head=SYNTHETIC_CANDIDATE_SHA,
    candidate_tree=SYNTHETIC_CANDIDATE_TREE_SHA,
    pull_request_number=999,
):
    return {
        "schema_version": "m15-completion-readiness-pr-observation/v1",
        "document_kind": "pull-request-candidate-observation",
        "repository": "aa-os/aaos-public",
        "issue_number": 250,
        "pull_request_number": pull_request_number,
        "source_main_base_sha": SOURCE_MAIN_BASE_SHA,
        "source_main_base_tree_sha": SOURCE_MAIN_BASE_TREE_SHA,
        "candidate_head_sha": candidate_head,
        "candidate_tree_sha": candidate_tree,
        "execution_subject_type": "pull-request-candidate-checkout",
        "observed_at": "2026-07-19T13:00:00Z",
        "observer": "synthetic-offline-observer",
        "evidence_reference": "urn:aaos:synthetic:m15:e3:pr-observation:999",
        "external_to_candidate_commit": True,
        "fetched_by_evaluator": False,
        "non_authoritative_boundary_statement": AUTHORITY_BOUNDARY,
    }


def build_external_verification_receipt(manifest, observation):
    commands = []
    for declaration in manifest["verification_commands"]:
        observed = declaration["minimum_tests_observed"]
        declared_argv = list(declaration["declared_logical_argv"])
        commands.append(
            {
                "command_id": declaration["command_id"],
                "declared_logical_argv": declared_argv,
                "actual_argv": [ACTUAL_PYTHON_LAUNCHER, *declared_argv[1:]],
                "execution_scope": declaration["execution_scope"],
                "execution_candidate_head_sha": observation["candidate_head_sha"],
                "executable_binding": {
                    "declared_launcher": "python",
                    "actual_launcher": ACTUAL_PYTHON_LAUNCHER,
                    "launcher_substitution_detected": True,
                    "launcher_substitution_declared": True,
                    "python_implementation": "CPython",
                    "python_version": "3.14.6",
                },
                "tests_observed": observed,
                "minimum_tests_observed": observed,
                "passes": observed,
                "failures": 0,
                "errors": 0,
                "skips": 0,
                "exit_code": 0,
                "execution_timestamp": "2026-07-19T13:01:00Z",
                "transcript_sha256": SYNTHETIC_TRANSCRIPT_SHA256,
                "evidence_reference": (
                    "urn:aaos:synthetic:m15:e3:verification:"
                    + declaration["command_id"]
                ),
                "executed_by_evaluator": False,
                "verification_results_are_completion_authority": False,
                "verification_results_are_release_authority": False,
            }
        )
    return {
        "schema_version": "m15-completion-readiness-verification-receipt/v1",
        "document_kind": "external-verification-execution-receipt",
        "repository": "aa-os/aaos-public",
        "issue_number": 250,
        "pull_request_number": observation["pull_request_number"],
        "source_main_base_sha": SOURCE_MAIN_BASE_SHA,
        "execution_candidate_head_sha": observation["candidate_head_sha"],
        "observation_evidence_reference": observation["evidence_reference"],
        "command_receipt_count": len(commands),
        "commands": commands,
        "external_to_candidate_commit": True,
        "executed_by_evaluator": False,
        "verification_results_are_completion_authority": False,
        "verification_results_are_release_authority": False,
        "non_authoritative_boundary_statement": AUTHORITY_BOUNDARY,
    }


def load_package():
    package = load_records()
    package["observation"] = build_external_pr_observation()
    package["receipt"] = build_external_verification_receipt(
        package["manifest"], package["observation"]
    )
    return package


def evaluate_package(package):
    return evaluate_completion_readiness(
        package["manifest"],
        package["inventory"],
        package["continuity"],
        package["external"],
        package["acceptance"],
        package["boundaries"],
        package["readme"],
        package["observation"],
        package["receipt"],
    )


def _receipt_command(package, command_id="e3-targeted"):
    return next(
        item
        for item in package["receipt"]["commands"]
        if item["command_id"] == command_id
    )


def apply_scenario_mutation(package, mutation):
    if mutation == "none":
        return
    if mutation == "e2-merge-commit-mismatch":
        package["continuity"]["merge_sha"] = "d" * 40
    elif mutation == "e2-merge-tree-mismatch":
        package["continuity"]["merge_tree_sha"] = "d" * 40
    elif mutation == "e2-candidate-not-merge-parent":
        package["continuity"]["candidate_is_merge_parent"] = False
    elif mutation == "e2-path-drift":
        package["continuity"]["candidate_to_merge_changed_path_count"] = 1
    elif mutation == "e2-observation-missing":
        package["observation"] = {}
        package["receipt"] = {}
    elif mutation == "active-receipt-missing":
        package["receipt"] = {}
    elif mutation == "superseded-receipt-used":
        package["external"]["active_receipt_comment_id"] = 5015466792
        package["external"]["superseded_receipt_accepted_as_active"] = True
    elif mutation == "active-receipt-digest-mismatch":
        package["external"]["active_receipt_canonical_sha256"] = "d" * 64
    elif mutation.startswith("track-") and mutation.endswith("-evidence-missing"):
        track_id = mutation.removesuffix("-evidence-missing")
        package["inventory"]["artifacts"] = [
            artifact
            for artifact in package["inventory"]["artifacts"]
            if artifact["track_id"] != track_id
        ]
    elif mutation == "acceptance-criterion-omitted":
        package["acceptance"]["criteria"].pop()
        package["acceptance"]["all_criteria_covered"] = False
    elif mutation == "criterion-has-no-evidence":
        package["acceptance"]["criteria"][0]["evidence_references"] = []
        package["acceptance"]["all_criteria_covered"] = False
    elif mutation == "hidden-blocker":
        package["boundaries"]["blockers"].pop()
    elif mutation == "tracker-represented-closed":
        package["manifest"]["tracker_231_state"] = "closed"
    elif mutation == "m15-represented-complete":
        package["manifest"]["m15_state"] = "complete"
    elif mutation == "readme-says-v0-14-0-released":
        package["readme"]["v0_14_0_released_claim"] = True
    elif mutation == "readme-changes-releases":
        package["readme"]["releases_unchanged"] = False
    elif mutation == "readme-changes-current-status":
        package["readme"]["current_status_unchanged"] = False
    elif mutation == "tag-represented-authorized":
        package["manifest"]["tag_state"] = "authorized"
    elif mutation == "github-release-represented-published":
        package["manifest"]["github_release_state"] = "published"
    elif mutation == "track-e4-represented-complete":
        package["manifest"]["track_e4_implemented"] = True
    elif mutation == "readiness-treated-as-approval":
        package["manifest"]["completion_approved"] = True
    elif mutation == "decision-proof-sealing-claim":
        package["manifest"]["decision_proof_sealed"] = True
    elif mutation == "learning-proof-sealing-claim":
        package["manifest"]["learning_proof_sealed"] = True
    elif mutation == "verification-below-minimum":
        command = _receipt_command(package)
        command["tests_observed"] -= 1
        command["passes"] -= 1
    elif mutation == "verification-failure":
        command = _receipt_command(package)
        command["passes"] -= 1
        command["failures"] = 1
    elif mutation == "verification-error":
        command = _receipt_command(package)
        command["passes"] -= 1
        command["errors"] = 1
    elif mutation == "unexpected-skip":
        command = _receipt_command(package)
        command["passes"] -= 1
        command["skips"] = 1
    elif mutation == "nonzero-exit":
        _receipt_command(package)["exit_code"] = 1
    elif mutation == "pr-observation-receipt-candidate-mismatch":
        package["receipt"]["execution_candidate_head_sha"] = "d" * 40
        for command in package["receipt"]["commands"]:
            command["execution_candidate_head_sha"] = "d" * 40
    elif mutation == "runtime-execution-claim":
        package["manifest"]["verification_commands_executed"] = True
    elif mutation == "external-evidence-authority-claim":
        package["external"]["external_evidence_is_completion_authority"] = True
    else:
        raise AssertionError(f"unhandled scenario mutation: {mutation}")


class M15CompletionReadinessContractAndSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_json(SCHEMA_PATH)
        cls.records = load_records()

    def test_01_schema_is_draft_2020_12(self):
        self.assertEqual(
            self.schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )

    def test_02_schema_has_exactly_ten_document_kinds(self):
        self.assertEqual(len(self.schema["oneOf"]), 10)

    def test_03_every_object_definition_is_strict(self):
        object_definitions = [
            definition
            for definition in self.schema["$defs"].values()
            if definition.get("type") == "object"
        ]
        self.assertGreaterEqual(len(object_definitions), 15)
        for definition in object_definitions:
            self.assertIs(definition.get("additionalProperties"), False)
            self.assertEqual(
                set(definition.get("required", [])),
                set(definition.get("properties", {})),
            )

    def test_04_schema_closes_git_and_digest_formats(self):
        self.assertEqual(
            self.schema["$defs"]["gitObjectSha"]["pattern"],
            "^[0-9a-f]{40}$",
        )
        self.assertEqual(
            self.schema["$defs"]["sha256"]["pattern"],
            "^[0-9a-f]{64}$",
        )

    def test_05_schema_closes_outcomes(self):
        self.assertEqual(
            self.schema["$defs"]["outcome"]["enum"],
            [READY, NOT_READY, BLOCKED],
        )

    def test_06_schema_binds_exact_authority_boundary(self):
        self.assertEqual(
            self.schema["$defs"]["authorityBoundary"]["const"],
            AUTHORITY_BOUNDARY,
        )

    def test_07_all_maintained_records_are_schema_valid(self):
        for name, document in self.records.items():
            with self.subTest(name=name):
                self.assertEqual(
                    validate_draft_2020_12_subset(document, self.schema),
                    [],
                )

    def test_08_external_observation_is_schema_valid(self):
        observation = build_external_pr_observation()
        self.assertEqual(
            validate_draft_2020_12_subset(observation, self.schema),
            [],
        )

    def test_09_external_receipt_is_schema_valid(self):
        observation = build_external_pr_observation()
        receipt = build_external_verification_receipt(
            self.records["manifest"], observation
        )
        self.assertEqual(
            validate_draft_2020_12_subset(receipt, self.schema),
            [],
        )

    def test_10_schema_rejects_additional_property(self):
        document = copy.deepcopy(self.records["manifest"])
        document["m15_complete"] = True
        self.assertTrue(validate_draft_2020_12_subset(document, self.schema))

    def test_11_contract_contains_all_required_runtime_mappings(self):
        contract = CONTRACT_PATH.read_text(encoding="utf-8")
        for name in (
            "manifest",
            "track_evidence_inventory",
            "e2_continuity_record",
            "e2_external_evidence",
            "acceptance_coverage_matrix",
            "boundary_register",
            "readme_observation",
            "pull_request_observation",
            "external_verification_receipt",
        ):
            self.assertIn(name, contract)
        self.assertIn("## Authorized Phase-Aware Compatibility Repair", contract)
        self.assertIn("phase-aware historical README regression repair", contract)
        for repair in AUTHORIZED_HISTORICAL_COMPATIBILITY_REPAIRS:
            self.assertIn(f"`{repair['path']}`", contract)

    def test_12_contract_preserves_governance_state(self):
        contract = CONTRACT_PATH.read_text(encoding="utf-8")
        self.assertIn("Tracker #231 remains open", contract)
        self.assertIn("M15 remains active and incomplete", contract)
        self.assertIn("Track E4", contract)
        self.assertIn("v0.14.0 remains unpublished", contract)
        self.assertIn("Decision Proof sealing remains AAOS-owned", contract)
        self.assertIn("Learning Proof sealing remains AAOS-owned", contract)

    def test_13_scenario_inventory_has_37_standalone_documents(self):
        self.assertEqual(len(SCENARIO_PATHS), 37)
        self.assertEqual(
            [path.name.split("-")[3] for path in SCENARIO_PATHS],
            [f"{number:02d}" for number in range(1, 38)],
        )

    def test_14_all_scenarios_are_schema_valid(self):
        for path in SCENARIO_PATHS:
            with self.subTest(path=path.name):
                self.assertEqual(
                    validate_draft_2020_12_subset(load_json(path), self.schema),
                    [],
                )

    def test_15_all_scenarios_are_synthetic_inert_and_offline(self):
        for path in SCENARIO_PATHS:
            document = load_json(path)
            with self.subTest(path=path.name):
                self.assertIs(document["synthetic"], True)
                self.assertIs(document["inert"], True)
                self.assertIs(document["offline"], True)
                self.assertIs(document["deterministic"], True)

    def test_16_scenarios_contain_no_sensitive_or_executable_payload_flags(self):
        forbidden_flags = (
            "contains_secret",
            "contains_credential",
            "contains_personal_data",
            "contains_private_prompt",
            "contains_production_identifier",
            "contains_executable_payload",
            "contains_argv_or_command_payload",
        )
        for path in SCENARIO_PATHS:
            document = load_json(path)
            with self.subTest(path=path.name):
                for flag in forbidden_flags:
                    self.assertIs(document[flag], False)

    def test_17_scenarios_have_no_command_or_secret_shaped_keys(self):
        forbidden_keys = {
            "argv",
            "actual_argv",
            "declared_logical_argv",
            "command",
            "script",
            "shell",
            "password",
            "token",
            "secret",
            "credential",
            "private_prompt",
        }
        for path in SCENARIO_PATHS:
            document = load_json(path)
            self.assertFalse(forbidden_keys.intersection(document))


class M15CompletionReadinessGitEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = load_json(RECORD_PATHS["inventory"])
        cls.continuity = load_json(RECORD_PATHS["continuity"])

    def test_18_source_main_base_and_tree_match_actual_git(self):
        self.assertEqual(git_text("rev-parse", "origin/main"), SOURCE_MAIN_BASE_SHA)
        self.assertEqual(
            git_text("rev-parse", "origin/main^{tree}"),
            SOURCE_MAIN_BASE_TREE_SHA,
        )

    def test_19_e2_candidate_and_merge_are_commit_objects(self):
        self.assertEqual(git_text("cat-file", "-t", E2_CANDIDATE_SHA), "commit")
        self.assertEqual(git_text("cat-file", "-t", E2_MERGE_SHA), "commit")

    def test_20_e2_candidate_tree_matches_exact_binding(self):
        self.assertEqual(
            git_text("rev-parse", f"{E2_CANDIDATE_SHA}^{{tree}}"),
            E2_TREE_SHA,
        )

    def test_21_e2_merge_tree_matches_exact_binding(self):
        self.assertEqual(
            git_text("rev-parse", f"{E2_MERGE_SHA}^{{tree}}"),
            E2_TREE_SHA,
        )

    def test_22_e2_merge_parents_match_git_order(self):
        self.assertEqual(
            git_text("show", "-s", "--format=%P", E2_MERGE_SHA).split(),
            [E2_BASE_SHA, E2_CANDIDATE_SHA],
        )

    def test_23_e2_candidate_and_base_are_merge_parents(self):
        parents = self.continuity["merge_parents"]
        self.assertIn(E2_BASE_SHA, parents)
        self.assertIn(E2_CANDIDATE_SHA, parents)
        self.assertIs(self.continuity["base_is_merge_parent"], True)
        self.assertIs(self.continuity["candidate_is_merge_parent"], True)

    def test_24_e2_candidate_to_merge_diff_is_empty(self):
        self.assertEqual(
            git_text("diff", "--name-status", E2_CANDIDATE_SHA, E2_MERGE_SHA),
            "",
        )
        self.assertEqual(self.continuity["candidate_to_merge_changed_path_count"], 0)
        self.assertEqual(self.continuity["additional_merge_difference_count"], 0)

    def test_25_e2_candidate_is_merge_ancestor(self):
        completed = subprocess.run(
            ["git", "merge-base", "--is-ancestor", E2_CANDIDATE_SHA, E2_MERGE_SHA],
            cwd=ROOT,
            check=False,
        )
        self.assertEqual(completed.returncode, 0)

    def test_26_e2_relation_is_exact_tree_match(self):
        self.assertEqual(self.continuity["relation"], "exact_tree_match")
        self.assertEqual(
            self.continuity["candidate_tree_sha"],
            self.continuity["merge_tree_sha"],
        )

    def test_27_e2_active_and_superseded_receipts_are_distinct(self):
        self.assertEqual(self.continuity["active_observation_comment_id"], 5015690597)
        self.assertEqual(self.continuity["active_receipt_comment_id"], 5015694989)
        self.assertEqual(
            self.continuity["active_receipt_canonical_sha256"],
            "511226a39144791ec47043203878bd22d14ec546e71702c267b66cc47da6af2f",
        )
        self.assertEqual(self.continuity["superseded_receipt_comment_id"], 5015466792)
        self.assertEqual(
            self.continuity["superseded_receipt_classification"],
            "superseded-historical-evidence",
        )

    def test_28_inventory_has_exact_prior_material_counts(self):
        artifacts = self.inventory["artifacts"]
        counts = Counter(item["track_id"] for item in artifacts)
        self.assertEqual(len(artifacts), 156)
        self.assertEqual(dict(counts), {key: value[2] for key, value in TRACK_EXPECTATIONS.items()})
        self.assertEqual(sum(counts[track] for track in ("track-a", "track-b", "track-c", "track-d")), 67)
        self.assertEqual(counts["track-e1"], 39)
        self.assertEqual(counts["track-e2"], 50)

    def test_29_track_summaries_match_first_parent_git_history(self):
        for summary in self.inventory["track_summaries"]:
            with self.subTest(track=summary["track_id"]):
                parents = git_text("show", "-s", "--format=%P", summary["merge_sha"]).split()
                self.assertEqual(parents, [summary["base_sha"], summary["candidate_sha"]])
                self.assertEqual(
                    git_text("rev-parse", f"{summary['candidate_sha']}^{{tree}}"),
                    summary["candidate_tree_sha"],
                )
                self.assertEqual(
                    git_text("rev-parse", f"{summary['merge_sha']}^{{tree}}"),
                    summary["merge_tree_sha"],
                )
                paths = git_text(
                    "diff-tree",
                    "--no-commit-id",
                    "--name-only",
                    "-r",
                    summary["base_sha"],
                    summary["merge_sha"],
                ).splitlines()
                self.assertEqual(len(paths), summary["material_path_count"])

    def test_30_inventory_paths_match_all_first_parent_material_paths(self):
        expected = []
        for summary in self.inventory["track_summaries"]:
            expected.extend(
                git_text(
                    "diff-tree",
                    "--no-commit-id",
                    "--name-only",
                    "-r",
                    summary["base_sha"],
                    summary["merge_sha"],
                ).splitlines()
            )
        self.assertEqual(
            [item["repository_path"] for item in self.inventory["artifacts"]],
            expected,
        )

    def test_31_all_artifact_git_blobs_modes_digests_and_bindings_match(self):
        summaries = {
            item["track_id"]: item for item in self.inventory["track_summaries"]
        }
        authorized_repair_paths = {
            item["path"] for item in AUTHORIZED_HISTORICAL_COMPATIBILITY_REPAIRS
        }
        for artifact in self.inventory["artifacts"]:
            summary = summaries[artifact["track_id"]]
            with self.subTest(path=artifact["repository_path"]):
                entry = git_text(
                    "ls-tree",
                    summary["merge_sha"],
                    "--",
                    artifact["repository_path"],
                ).split()
                self.assertGreaterEqual(len(entry), 3)
                self.assertEqual(entry[0], artifact["git_file_mode"])
                self.assertEqual(entry[1], "blob")
                self.assertEqual(entry[2], artifact["git_blob_sha"])
                blob = git_bytes("cat-file", "blob", artifact["git_blob_sha"])
                self.assertEqual(canonical_sha256(blob), artifact["canonical_text_sha256"])
                working_blob = git_text(
                    "hash-object",
                    "--path=" + artifact["repository_path"],
                    "--",
                    artifact["repository_path"],
                )
                if artifact["repository_path"] in authorized_repair_paths:
                    self.assertNotEqual(working_blob, artifact["git_blob_sha"])
                else:
                    self.assertEqual(working_blob, artifact["git_blob_sha"])
                issue, pull_request, _ = TRACK_EXPECTATIONS[artifact["track_id"]]
                self.assertEqual(artifact["source_issue"], issue)
                self.assertEqual(artifact["implementation_pr"], pull_request)
                self.assertEqual(artifact["candidate_sha"], summary["candidate_sha"])
                self.assertEqual(artifact["merge_sha"], summary["merge_sha"])
                self.assertTrue(artifact["covering_test"])
                self.assertTrue(artifact["evidence_reference"])
                self.assertEqual(artifact["lifecycle_state"], "maintained")
                self.assertEqual(artifact["authority_boundary"], AUTHORITY_BOUNDARY)

    def test_32_inventory_binding_digest_is_canonical(self):
        payload = copy.deepcopy(self.inventory)
        expected = payload.pop("inventory_binding_sha256")
        self.assertEqual(canonical_json_sha256(payload), expected)

    def test_32a_historical_e1_binding_and_current_e3_repair_are_distinct(self):
        historical = HISTORICAL_E1_ARTIFACT_BINDING
        repair = E3_AUTHORIZED_COMPATIBILITY_REPAIR
        self.assertEqual(historical["path"], repair["path"])
        historical_blob = git_bytes(
            "cat-file",
            "blob",
            f"{historical['source_baseline_commit_sha']}:{historical['path']}",
        )
        current_bytes = (ROOT / repair["path"]).read_bytes()
        self.assertEqual(
            canonical_sha256(historical_blob),
            historical["historical_canonical_sha256"],
        )
        self.assertEqual(
            canonical_sha256(current_bytes),
            repair["current_candidate_canonical_sha256"],
        )
        self.assertNotEqual(
            historical["historical_canonical_sha256"],
            repair["current_candidate_canonical_sha256"],
        )
        inventory_row = next(
            item
            for item in self.inventory["artifacts"]
            if item["repository_path"] == historical["path"]
        )
        self.assertEqual(
            inventory_row["canonical_text_sha256"],
            historical["historical_canonical_sha256"],
        )


class M15CompletionReadinessReadmeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.observation = load_json(RECORD_PATHS["readme"])
        cls.base = git_bytes("show", f"{SOURCE_MAIN_BASE_SHA}:README.md")
        cls.candidate = README_PATH.read_bytes()

    def test_33_base_and_candidate_readme_digests_match_observation(self):
        self.assertEqual(
            canonical_sha256(self.base),
            self.observation["base_readme_canonical_sha256"],
        )
        self.assertEqual(
            canonical_sha256(self.candidate),
            self.observation["candidate_readme_canonical_sha256"],
        )

    def test_34_releases_section_is_unchanged(self):
        base = level_two_section(self.base, "Releases")
        candidate = level_two_section(self.candidate, "Releases")
        self.assertEqual(base, candidate)
        self.assertTrue(self.observation["releases_unchanged"])

    def test_35_current_status_section_is_unchanged(self):
        base = level_two_section(self.base, "Current Status")
        candidate = level_two_section(self.candidate, "Current Status")
        self.assertEqual(base, candidate)
        self.assertTrue(self.observation["current_status_unchanged"])

    def test_36_next_phase_is_exact_future_only_wording(self):
        section = level_two_section(self.candidate, "Next Phase").decode("utf-8")
        self.assertEqual(section, EXPECTED_NEXT_PHASE)
        self.assertTrue(self.observation["next_phase_changed"])
        self.assertTrue(self.observation["future_only_wording_valid"])

    def test_37_readme_observation_contains_no_completion_or_release_claim(self):
        for key in (
            "m15_complete_claim",
            "v0_14_0_released_claim",
            "tag_claim",
            "github_release_claim",
            "track_e4_completion_claim",
        ):
            self.assertIs(self.observation[key], False)


class M15CompletionReadinessRuntimeTests(unittest.TestCase):
    def test_38_valid_package_is_ready_for_final_human_review(self):
        result = evaluate_package(load_package())
        self.assertEqual(result["outcome"], READY)
        self.assertEqual(result["findings"], [])

    def test_39_result_preserves_exact_non_authoritative_state(self):
        result = evaluate_package(load_package())
        expected = {
            "caller_data_only": True,
            "file_io_performed": False,
            "git_inspection_performed": False,
            "github_access_performed": False,
            "network_access_performed": False,
            "repository_digests_calculated": False,
            "verification_commands_executed": False,
            "external_state_mutated": False,
            "m15_state": "active-and-incomplete",
            "tracker_231_state": "open",
            "track_e4_implemented": False,
            "v0_14_0_state": "unpublished",
            "tag_state": "not-authorized",
            "github_release_state": "not-created",
            "decision_proof_sealed": False,
            "learning_proof_sealed": False,
        }
        for key, value in expected.items():
            self.assertEqual(result[key], value)

    def test_40_outcome_vocabulary_is_closed(self):
        self.assertEqual(evaluator_module.OUTCOMES, (READY, NOT_READY, BLOCKED))

    def test_41_blocking_precedes_readiness(self):
        package = load_package()
        package["observation"] = {}
        package["manifest"]["m15_state"] = "complete"
        result = evaluate_package(package)
        self.assertTrue(result["readiness_findings"])
        self.assertTrue(result["blocking_findings"])
        self.assertEqual(result["outcome"], BLOCKED)

    def test_42_missing_pr_observation_is_not_ready(self):
        package = load_package()
        package["observation"] = {}
        package["receipt"] = {}
        self.assertEqual(evaluate_package(package)["outcome"], NOT_READY)

    def test_43_missing_receipt_is_not_ready(self):
        package = load_package()
        package["receipt"] = {}
        self.assertEqual(evaluate_package(package)["outcome"], NOT_READY)

    def test_44_partial_acceptance_coverage_does_not_pass(self):
        package = load_package()
        package["acceptance"]["criteria"][0]["coverage_state"] = "partial"
        package["acceptance"]["all_criteria_covered"] = False
        self.assertEqual(evaluate_package(package)["outcome"], NOT_READY)

    def test_45_missing_acceptance_evidence_does_not_pass(self):
        package = load_package()
        package["acceptance"]["criteria"][0]["evidence_references"] = []
        package["acceptance"]["all_criteria_covered"] = False
        self.assertEqual(evaluate_package(package)["outcome"], NOT_READY)

    def test_46_blocked_acceptance_criterion_blocks(self):
        package = load_package()
        package["acceptance"]["criteria"][0]["coverage_state"] = "blocked"
        package["acceptance"]["all_criteria_covered"] = False
        self.assertEqual(evaluate_package(package)["outcome"], BLOCKED)

    def test_47_hidden_blocker_blocks(self):
        package = load_package()
        package["boundaries"]["blockers"].pop()
        self.assertEqual(evaluate_package(package)["outcome"], BLOCKED)

    def test_48_unresolved_blocker_blocks(self):
        package = load_package()
        package["boundaries"]["blockers"][0]["state"] = "open"
        self.assertEqual(evaluate_package(package)["outcome"], BLOCKED)

    def test_49_resolved_blocker_requires_evidence(self):
        package = load_package()
        package["boundaries"]["blockers"][0]["evidence_references"] = []
        self.assertEqual(evaluate_package(package)["outcome"], BLOCKED)

    def test_50_all_future_prerequisites_remain_open_without_blocking_readiness(self):
        package = load_package()
        states = {
            item["prerequisite_id"]: item["state"]
            for item in package["boundaries"]["future_prerequisites"]
        }
        self.assertEqual(states, {item: "open" for item in REQUIRED_FUTURE_PREREQUISITES})
        self.assertEqual(evaluate_package(package)["outcome"], READY)

    def test_51_closed_future_prerequisite_blocks(self):
        package = load_package()
        package["boundaries"]["future_prerequisites"][0]["state"] = "completed"
        self.assertEqual(evaluate_package(package)["outcome"], BLOCKED)

    def test_52_superseded_receipt_cannot_be_active(self):
        package = load_package()
        apply_scenario_mutation(package, "superseded-receipt-used")
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertTrue(any("superseded" in finding for finding in result["findings"]))

    def test_53_exact_verification_minimum_passes(self):
        package = load_package()
        command = _receipt_command(package)
        self.assertEqual(command["tests_observed"], command["minimum_tests_observed"])
        self.assertEqual(evaluate_package(package)["outcome"], READY)

    def test_54_above_verification_minimum_passes(self):
        package = load_package()
        command = _receipt_command(package)
        command["tests_observed"] += 1
        command["passes"] += 1
        self.assertEqual(evaluate_package(package)["outcome"], READY)

    def test_55_below_verification_minimum_blocks(self):
        package = load_package()
        apply_scenario_mutation(package, "verification-below-minimum")
        self.assertEqual(evaluate_package(package)["outcome"], BLOCKED)

    def test_56_verification_failure_blocks(self):
        package = load_package()
        apply_scenario_mutation(package, "verification-failure")
        self.assertEqual(evaluate_package(package)["outcome"], BLOCKED)

    def test_57_verification_error_blocks(self):
        package = load_package()
        apply_scenario_mutation(package, "verification-error")
        self.assertEqual(evaluate_package(package)["outcome"], BLOCKED)

    def test_58_unexpected_skip_is_not_ready(self):
        package = load_package()
        apply_scenario_mutation(package, "unexpected-skip")
        self.assertEqual(evaluate_package(package)["outcome"], NOT_READY)

    def test_59_nonzero_exit_blocks(self):
        package = load_package()
        apply_scenario_mutation(package, "nonzero-exit")
        self.assertEqual(evaluate_package(package)["outcome"], BLOCKED)

    def test_60_count_arithmetic_mismatch_blocks(self):
        package = load_package()
        _receipt_command(package)["passes"] -= 1
        self.assertEqual(evaluate_package(package)["outcome"], BLOCKED)

    def test_61_pr_observation_and_receipt_candidate_must_match(self):
        package = load_package()
        package["receipt"]["execution_candidate_head_sha"] = "d" * 40
        self.assertEqual(evaluate_package(package)["outcome"], BLOCKED)

    def test_62_receipt_command_order_is_bound(self):
        package = load_package()
        package["receipt"]["commands"][0], package["receipt"]["commands"][1] = (
            package["receipt"]["commands"][1],
            package["receipt"]["commands"][0],
        )
        self.assertEqual(evaluate_package(package)["outcome"], BLOCKED)

    def test_63_receipt_argv_substitution_is_bound(self):
        package = load_package()
        _receipt_command(package)["actual_argv"][0] = "python"
        self.assertEqual(evaluate_package(package)["outcome"], BLOCKED)

    def test_64_invalid_rfc3339_utc_timestamp_blocks(self):
        package = load_package()
        package["observation"]["observed_at"] = "2026-02-30T25:00:00Z"
        self.assertEqual(evaluate_package(package)["outcome"], BLOCKED)

    def test_65_caller_mappings_are_not_mutated(self):
        package = load_package()
        before = copy.deepcopy(package)
        evaluate_package(package)
        self.assertEqual(package, before)

    def test_66_each_call_returns_a_new_result_mapping(self):
        package = load_package()
        first = evaluate_package(package)
        second = evaluate_package(package)
        self.assertEqual(first, second)
        self.assertIsNot(first, second)
        self.assertIsNot(first["findings"], second["findings"])

    def test_67_runtime_signature_has_exactly_nine_mappings(self):
        parameters = list(inspect.signature(evaluate_completion_readiness).parameters)
        self.assertEqual(
            parameters,
            [
                "manifest",
                "track_evidence_inventory",
                "e2_continuity_record",
                "e2_external_evidence",
                "acceptance_coverage_matrix",
                "boundary_register",
                "readme_observation",
                "pull_request_observation",
                "external_verification_receipt",
            ],
        )

    def test_68_runtime_ast_has_no_prohibited_imports(self):
        tree = ast.parse(EVALUATOR_PATH.read_text(encoding="utf-8"))
        prohibited = {
            "pathlib", "os", "io", "json", "hashlib", "subprocess", "socket",
            "urllib", "requests", "github", "git", "importlib",
        }
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertFalse(imported.intersection(prohibited))

    def test_69_runtime_ast_has_no_prohibited_calls(self):
        tree = ast.parse(EVALUATOR_PATH.read_text(encoding="utf-8"))
        prohibited = {"open", "eval", "exec", "compile", "__import__"}
        calls = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertFalse(calls.intersection(prohibited))

    def test_70_runtime_source_contains_no_network_or_process_api(self):
        source = EVALUATOR_PATH.read_text(encoding="utf-8")
        for token in ("subprocess.", "socket.", "urllib.", "requests.", "Path("):
            self.assertNotIn(token, source)


class M15CompletionReadinessCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = load_package()

    def test_71_all_six_track_bindings_are_present(self):
        self.assertEqual(
            tuple(item["track_id"] for item in self.package["inventory"]["track_summaries"]),
            tuple(TRACK_EXPECTATIONS),
        )
        self.assertEqual(
            self.package["manifest"]["authorized_phase_aware_compatibility_repair"],
            AUTHORIZED_PHASE_AWARE_COMPATIBILITY_REPAIR,
        )
        self.assertEqual(
            self.package["manifest"]["authorized_historical_compatibility_repairs"],
            list(AUTHORIZED_HISTORICAL_COMPATIBILITY_REPAIRS),
        )
        self.assertEqual(
            self.package["manifest"]["historical_e1_artifact_binding"],
            HISTORICAL_E1_ARTIFACT_BINDING,
        )
        self.assertEqual(
            self.package["manifest"]["e3_authorized_compatibility_repair"],
            E3_AUTHORIZED_COMPATIBILITY_REPAIR,
        )
        self.assertEqual(self.package["inventory"]["prior_material_artifact_count"], 156)
        self.assertTrue(
            all(
                item["counted_in_prior_material_artifact_inventory"] is False
                for item in AUTHORIZED_HISTORICAL_COMPATIBILITY_REPAIRS
            )
        )

    def test_72_all_six_track_material_counts_sum_to_156(self):
        self.assertEqual(sum(value[2] for value in TRACK_EXPECTATIONS.values()), 156)

    def test_73_all_six_source_issues_and_prs_are_bound(self):
        summaries = {
            item["track_id"]: item for item in self.package["inventory"]["track_summaries"]
        }
        for track_id, (issue, pull_request, _) in TRACK_EXPECTATIONS.items():
            self.assertEqual(summaries[track_id]["source_issue"], issue)
            self.assertEqual(summaries[track_id]["implementation_pr"], pull_request)

    def test_74_acceptance_matrix_has_all_16_criteria_in_order(self):
        self.assertEqual(
            tuple(item["criterion_id"] for item in self.package["acceptance"]["criteria"]),
            CRITERION_IDS,
        )
        self.assertTrue(self.package["acceptance"]["all_criteria_covered"])

    def test_75_blocker_register_is_complete_and_ordered(self):
        self.assertEqual(
            tuple(item["blocker_id"] for item in self.package["boundaries"]["blockers"]),
            REQUIRED_BLOCKERS,
        )

    def test_76_future_prerequisite_register_is_complete_and_ordered(self):
        self.assertEqual(
            tuple(
                item["prerequisite_id"]
                for item in self.package["boundaries"]["future_prerequisites"]
            ),
            REQUIRED_FUTURE_PREREQUISITES,
        )

    def test_77_verification_manifest_has_all_17_commands_in_order(self):
        self.assertEqual(
            tuple(
                item["command_id"]
                for item in self.package["manifest"]["verification_commands"]
            ),
            COMMAND_IDS,
        )

    def test_78_inherited_minimums_match_source_contract(self):
        expected = {
            "e2-targeted": 140,
            "e1-targeted": 132,
            "track-a": 68,
            "track-b": 73,
            "track-c": 181,
            "track-d": 79,
            "m14-public-output": 23,
            "m14-provenance": 47,
            "m14-skill-admission": 135,
            "external-evidence-admission": 31,
            "m14-cross-control-authority": 107,
            "decision-proof-ownership": 30,
            "release-m15-status": 18,
            "m14-final-completion": 110,
            "m14-completion-readiness": 112,
        }
        for command_id, minimum in expected.items():
            self.assertEqual(COMMAND_MINIMA[command_id], minimum)

    def test_79_e3_minimum_is_actual_nontrivial_suite_count(self):
        self.assertGreater(COMMAND_MINIMA["e3-targeted"], 1)

    def test_80_full_suite_minimum_adds_all_e3_tests_to_prior_baseline(self):
        count = sum(
            unittest.defaultTestLoader.loadTestsFromTestCase(test_case).countTestCases()
            for test_case in (
                M15CompletionReadinessContractAndSchemaTests,
                M15CompletionReadinessGitEvidenceTests,
                M15CompletionReadinessReadmeTests,
                M15CompletionReadinessRuntimeTests,
                M15CompletionReadinessCoverageTests,
            )
        )
        self.assertEqual(COMMAND_MINIMA["e3-targeted"], count)
        compatibility_repair_tests_added = (
            COMMAND_MINIMA["e1-targeted"]
            - 126
            + COMMAND_MINIMA["track-c"]
            - 180
        )
        self.assertEqual(
            COMMAND_MINIMA["full-maintained-suite"],
            1918 + count + compatibility_repair_tests_added,
        )


def _make_scenario_test(path):
    def test(self):
        scenario = load_json(path)
        package = load_package()
        apply_scenario_mutation(package, scenario["mutation"])
        first = evaluate_package(package)
        second = evaluate_package(copy.deepcopy(package))
        self.assertEqual(first, second)
        self.assertEqual(first["outcome"], scenario["expected_outcome"])

    return test


for _scenario_path in SCENARIO_PATHS:
    _scenario_document = load_json(_scenario_path)
    _scenario_number = _scenario_document["scenario_id"].rsplit("-", 1)[-1]
    _scenario_name = _scenario_document["title"].replace("-", "_")
    setattr(
        M15CompletionReadinessRuntimeTests,
        f"test_scenario_{_scenario_number}_{_scenario_name}",
        _make_scenario_test(_scenario_path),
    )


def _make_criterion_test(index):
    def test(self):
        row = self.package["acceptance"]["criteria"][index]
        self.assertEqual(row["criterion_id"], CRITERION_IDS[index])
        self.assertEqual(row["coverage_state"], "covered")
        self.assertIn(row["source_track"], {*TRACK_EXPECTATIONS, "cross-track", "track-e3"})
        for key in ("evidence_references", "artifact_references", "test_references"):
            self.assertTrue(row[key])
            self.assertTrue(all(isinstance(value, str) and value for value in row[key]))
        self.assertEqual(row["authority_boundary"], AUTHORITY_BOUNDARY)

    return test


for _criterion_index in range(16):
    setattr(
        M15CompletionReadinessCoverageTests,
        f"test_criterion_{_criterion_index + 1:02d}_is_fully_covered",
        _make_criterion_test(_criterion_index),
    )


def _make_command_test(command_id):
    def test(self):
        declaration = next(
            item
            for item in self.package["manifest"]["verification_commands"]
            if item["command_id"] == command_id
        )
        self.assertEqual(declaration["minimum_tests_observed"], COMMAND_MINIMA[command_id])
        self.assertGreater(declaration["minimum_tests_observed"], 0)
        self.assertEqual(declaration["declared_logical_argv"][0], "python")
        self.assertIn(
            declaration["execution_scope"],
            {
                "e3-candidate-validation",
                "inherited-regression",
                "candidate-full-suite-integration",
                "authorized-compatibility-regression",
            },
        )

    return test


for _command_id in COMMAND_IDS:
    setattr(
        M15CompletionReadinessCoverageTests,
        "test_command_" + _command_id.replace("-", "_") + "_is_bound",
        _make_command_test(_command_id),
    )


if __name__ == "__main__":
    unittest.main()
