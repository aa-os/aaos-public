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

import runtime.m15_final_completion_evaluator as evaluator_module
from runtime.m15_final_completion_evaluator import (
    ACCEPTANCE_BINDING_FIELDS,
    ARTIFACT_BINDING_FIELDS,
    AUTHORITY_BOUNDARY,
    BLOCKED,
    COMMAND_IDS,
    COMPATIBILITY_REPAIR_BINDING_FIELDS,
    E4_PR_OBSERVATION_EVIDENCE_REFERENCE,
    E4_PULL_REQUEST_NUMBER,
    E4_VERIFICATION_RECEIPT_EVIDENCE_REFERENCE,
    EXPECTED_ACCEPTANCE_CRITERIA,
    EXPECTED_AUTHORIZED_COMPATIBILITY_REPAIRS,
    EXPECTED_ARTIFACT_BINDINGS,
    EXPECTED_VERIFICATION_COMMANDS,
    HUMAN_APPROVAL_AUTHORITY_SCOPE,
    HUMAN_APPROVAL_SCHEMA_VERSION,
    NON_AUTHORITATIVE_RELEASE_BOUNDARY,
    NOT_READY,
    PR_OBSERVATION_BOUNDARY,
    PR_OBSERVATION_SCHEMA_VERSION,
    READY,
    REQUIRED_BLOCKERS,
    REQUIRED_READINESS_FINDINGS,
    VERIFICATION_BOUNDARY,
    VERIFICATION_RECEIPT_SCHEMA_VERSION,
    evaluate_final_completion,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "examples" / "public-integration-pack-pilot"
SCHEMA_PATH = ROOT / "schemas" / "m15-final-completion.schema.json"
CONTRACT_PATH = (
    ROOT / "docs" / "learning-governance" / "m15-final-completion-contract.md"
)
EVALUATOR_PATH = ROOT / "runtime" / "m15_final_completion_evaluator.py"

RECORD_PATHS = {
    "manifest": FIXTURE_ROOT / "m15-final-completion-manifest.json",
    "inventory": FIXTURE_ROOT / "m15-final-completion-track-evidence.json",
    "continuity": FIXTURE_ROOT / "m15-final-completion-e3-continuity.json",
    "external": FIXTURE_ROOT / "m15-final-completion-e3-external-evidence.json",
    "acceptance": FIXTURE_ROOT / "m15-final-completion-acceptance-coverage.json",
    "transition": FIXTURE_ROOT / "m15-final-completion-transition-register.json",
    "readme": FIXTURE_ROOT / "m15-final-completion-readme-transition.json",
    "release": FIXTURE_ROOT / "m15-final-completion-release-preparation.json",
}
SCENARIO_PATHS = sorted(
    FIXTURE_ROOT.glob("m15-final-completion-[0-9][0-9]-*.json")
)

SOURCE_MAIN_BASE_SHA = "52ec76c17cd21ec519dfec45ced4ad720b82d80e"
SOURCE_MAIN_BASE_TREE_SHA = "97b239cbd175aac01b05a1fba2394b72c47a5360"
E4_MERGE_SHA = "01870f4b844c1cda2f157e7be7bdb66317fdc738"
E3_BASE_SHA = "f6d074fca2fedecbf654697719179440bc0680d3"
E3_CANDIDATE_SHA = "907d2361233c7b0405a41271d7b02fa6c1a0c62d"
E3_TREE_SHA = "97b239cbd175aac01b05a1fba2394b72c47a5360"
E3_MERGE_SHA = SOURCE_MAIN_BASE_SHA
E3_ACTIVE_OBSERVATION_COMMENT_ID = 5017872695
E3_ACTIVE_RECEIPT_COMMENT_ID = 5017894934
E3_ACTIVE_RECEIPT_SHA256 = (
    "660ffddc0644bbb6e11689ceaf77b5c47b4061241a04cba233f2607287e30cb4"
)
E3_SUPERSEDED_OBSERVATION_COMMENT_ID = 5016298363
E3_SUPERSEDED_RECEIPT_COMMENT_ID = 5016356607

SYNTHETIC_CANDIDATE_SHA = "a" * 40
SYNTHETIC_CANDIDATE_TREE_SHA = "b" * 40
SYNTHETIC_TRANSCRIPT_SHA256 = "c" * 64
SYNTHETIC_RECEIPT_SHA256 = "d" * 64
SYNTHETIC_README_SHA256 = "e" * 64
SYNTHETIC_COMPLETION_STATE_SHA256 = "f" * 64
ACTUAL_PYTHON_LAUNCHER = ".verification-python/python.exe"
GIT = os.environ.get("AAOS_TEST_GIT_EXE") or shutil.which("git")

TRACK_COUNTS = {
    "track-a": 7,
    "track-b": 13,
    "track-c": 18,
    "track-d": 29,
    "track-e1": 39,
    "track-e2": 50,
    "track-e3": 53,
}

EXPECTED_RELEASE_ENTRY = (
    "- v0.14.0 — M15 Learning Sovereignty and Evidence-Bound Capability Memory"
)
EXPECTED_NEXT_PHASE = """## Next Phase

M15 repository completion has occurred through the human-reviewed Track E4 merge.

Manual tag and GitHub Release publication remain separate, human-controlled
actions. The exact v0.14.0 tag target is the resulting E4 merge commit; this
repository state does not claim that the tag or GitHub Release already exists.

After publication, open `Post-release review: v0.14.0 / M15` and verify the
published target, release state, and candidate-to-merge continuity.

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
    if GIT is None:
        raise AssertionError("Git is required for immutable-object E4 tests")
    return subprocess.check_output(
        [GIT, *args],
        cwd=ROOT,
        stderr=subprocess.PIPE,
    )


def git_text(*args):
    return git_bytes(*args).decode("utf-8").strip()


def level_two_sections(value):
    data = canonical_text(value).decode("utf-8")
    matches = list(re.finditer(r"(?m)^## ([^\n]+)\n", data))
    sections = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(data)
        sections[match.group(1)] = data[match.start() : end]
    return sections


def level_two_section(value, title):
    sections = level_two_sections(value)
    if title not in sections:
        raise AssertionError(f"README section missing: {title}")
    return sections[title]


def current_baseline_section(value):
    releases = level_two_section(value, "Releases")
    marker = "Current baseline:\n"
    start = releases.find(marker)
    if start < 0:
        raise AssertionError("README Current baseline marker missing")
    return releases[start:]


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
    """Validate every Draft 2020-12 feature used by the maintained E4 schema."""

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
            errors.append(f"{path}: too few items")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: too many items")
        if schema.get("uniqueItems"):
            for index, item in enumerate(instance):
                if any(_json_equal(item, prior) for prior in instance[:index]):
                    errors.append(f"{path}: duplicate item")
                    break
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
            for index, value in enumerate(instance[len(prefix_items) :], len(prefix_items)):
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
            errors.append(f"{path}: too short")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{path}: too long")
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
    pull_request_number=E4_PULL_REQUEST_NUMBER,
    evidence_reference=E4_PR_OBSERVATION_EVIDENCE_REFERENCE,
):
    return {
        "schema_version": PR_OBSERVATION_SCHEMA_VERSION,
        "document_kind": "pull-request-candidate-observation",
        "repository": "aa-os/aaos-public",
        "issue_number": 252,
        "parent_tracker": 231,
        "pull_request_number": pull_request_number,
        "source_main_base_sha": SOURCE_MAIN_BASE_SHA,
        "source_main_base_tree_sha": SOURCE_MAIN_BASE_TREE_SHA,
        "candidate_head_sha": candidate_head,
        "candidate_tree_sha": candidate_tree,
        "execution_subject_type": "pull-request-candidate-checkout",
        "observed_at": "2026-07-20T09:00:00Z",
        "observer": "synthetic-offline-observer",
        "evidence_reference": evidence_reference,
        "external_to_candidate_commit": True,
        "fetched_by_evaluator": False,
        "non_authoritative_boundary_statement": PR_OBSERVATION_BOUNDARY,
    }


def build_external_verification_receipt(manifest, observation):
    commands = []
    for declaration in manifest["verification_commands"]:
        observed = declaration["minimum_tests_observed"]
        logical_argv = list(declaration["declared_logical_argv"])
        commands.append(
            {
                "command_id": declaration["command_id"],
                "declared_logical_argv": logical_argv,
                "actual_argv": [ACTUAL_PYTHON_LAUNCHER, *logical_argv[1:]],
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
                "execution_timestamp": "2026-07-20T09:01:00Z",
                "transcript_sha256": SYNTHETIC_TRANSCRIPT_SHA256,
                "evidence_reference": (
                    "urn:aaos:synthetic:m15:e4:verification:"
                    + declaration["command_id"]
                ),
                "executed_by_evaluator": False,
                "verification_results_are_completion_authority": False,
                "verification_results_are_release_authority": False,
            }
        )
    receipt = {
        "schema_version": VERIFICATION_RECEIPT_SCHEMA_VERSION,
        "document_kind": "external-verification-execution-receipt",
        "repository": "aa-os/aaos-public",
        "issue_number": 252,
        "parent_tracker": 231,
        "pull_request_number": E4_PULL_REQUEST_NUMBER,
        "source_main_base_sha": SOURCE_MAIN_BASE_SHA,
        "execution_candidate_head_sha": observation["candidate_head_sha"],
        "execution_candidate_tree_sha": observation["candidate_tree_sha"],
        "observation_evidence_reference": observation["evidence_reference"],
        "command_receipt_count": len(commands),
        "commands": commands,
        "evidence_reference": E4_VERIFICATION_RECEIPT_EVIDENCE_REFERENCE,
        "external_to_candidate_commit": True,
        "executed_by_evaluator": False,
        "verification_results_are_completion_authority": False,
        "verification_results_are_release_authority": False,
        "non_authoritative_boundary_statement": VERIFICATION_BOUNDARY,
    }
    receipt["canonical_payload_sha256"] = canonical_json_sha256(receipt)
    return receipt


def build_human_approval(observation, receipt, readme):
    return {
        "schema_version": HUMAN_APPROVAL_SCHEMA_VERSION,
        "document_kind": "commit-external-human-approval-observation",
        "repository": "aa-os/aaos-public",
        "issue_number": 252,
        "parent_tracker": 231,
        "pull_request_number": E4_PULL_REQUEST_NUMBER,
        "source_main_base_sha": SOURCE_MAIN_BASE_SHA,
        "candidate_head_sha": observation["candidate_head_sha"],
        "candidate_tree_sha": observation["candidate_tree_sha"],
        "pr_observation_reference": observation["evidence_reference"],
        "verification_receipt_reference": receipt["evidence_reference"],
        "verification_receipt_canonical_sha256": receipt[
            "canonical_payload_sha256"
        ],
        "reviewed_readme_transition_sha256": readme["candidate_readme_sha256"],
        "reviewed_completion_state_sha256": readme[
            "candidate_completion_state_sha256"
        ],
        "intended_merge_method": "merge-commit",
        "permitted_issue_closures": [252, 231],
        "explicit_authority_scope": HUMAN_APPROVAL_AUTHORITY_SCOPE,
        "approval_timestamp": "2026-07-20T09:02:00Z",
        "approver_identity": "synthetic-human-reviewer",
        "approver_type": "human",
        "authored_by_human": True,
        "external_to_candidate_commit": True,
        "candidate_head_frozen": True,
        "approved": True,
        "tag_creation_authorized": False,
        "github_release_publication_authorized": False,
        "risk_acceptance_authorized": False,
        "audit_closure_authorized": False,
        "waiver_authorized": False,
        "authority_transfer_authorized": False,
        "decision_proof_sealing_authorized": False,
        "learning_proof_sealing_authorized": False,
        "non_authoritative_release_publication_boundary": (
            NON_AUTHORITATIVE_RELEASE_BOUNDARY
        ),
    }


def load_package(*, include_approval=True):
    package = load_records()
    package["observation"] = build_external_pr_observation()
    package["receipt"] = build_external_verification_receipt(
        package["manifest"], package["observation"]
    )
    package["approval"] = (
        build_human_approval(
            package["observation"], package["receipt"], package["readme"]
        )
        if include_approval
        else {}
    )
    return package


def evaluate_package(package):
    return evaluate_final_completion(
        package["manifest"],
        package["inventory"],
        package["continuity"],
        package["external"],
        package["acceptance"],
        package["transition"],
        package["readme"],
        package["release"],
        package["observation"],
        package["receipt"],
        package["approval"],
    )


def receipt_command(package, command_id="e4-targeted"):
    return next(
        row
        for row in package["receipt"]["commands"]
        if row["command_id"] == command_id
    )


def apply_scenario_mutation(package, scenario):
    mutation = scenario["mutation"]
    target = mutation["target_document"]
    operation = mutation["operation"]
    value = mutation["synthetic_value"]
    if operation == "none":
        return
    if target == "e3-continuity-record":
        field = mutation["field_path"]
        package["continuity"][field] = value
        return
    if target == "e3-external-evidence":
        field = mutation["field_path"]
        if operation == "remove":
            package["external"].pop(field, None)
        elif field == "superseded_observation_accepted_as_active":
            package["external"][field] = value
            package["external"]["active_observation_comment_id"] = (
                E3_SUPERSEDED_OBSERVATION_COMMENT_ID
            )
            package["external"]["active_observation_is_superseded"] = True
        elif field == "superseded_receipt_accepted_as_active":
            package["external"][field] = value
            package["external"]["active_receipt_comment_id"] = (
                E3_SUPERSEDED_RECEIPT_COMMENT_ID
            )
            package["external"]["active_receipt_is_superseded"] = True
        else:
            package["external"][field] = value
        return
    if target == "track-evidence-inventory":
        field = mutation["field_path"]
        if field.startswith("artifacts.track-") and operation == "remove":
            track_id = field.split(".", 1)[1]
            package["inventory"]["artifacts"] = [
                row
                for row in package["inventory"]["artifacts"]
                if row["track_id"] != track_id
            ]
        elif operation == "rebaseline":
            row = next(
                row
                for row in package["inventory"]["artifacts"]
                if row["track_id"] == "track-e3"
            )
            row["canonical_text_sha256"] = value
        elif operation == "add-unapproved-path":
            row = copy.deepcopy(package["inventory"]["artifacts"][-1])
            row["repository_path"] = value
            package["inventory"]["artifacts"].append(row)
        else:
            raise AssertionError(f"unsupported inventory mutation: {mutation}")
        return
    if target == "acceptance-coverage-matrix":
        field = mutation["field_path"]
        if operation == "remove":
            criterion_id = field.split(".")[-1]
            package["acceptance"]["criteria"] = [
                row
                for row in package["acceptance"]["criteria"]
                if row["criterion_id"] != criterion_id
            ]
        elif field.endswith("criterion_text"):
            package["acceptance"]["criteria"][0]["criterion_text"] = value
        elif field.endswith("evidence_references[0]"):
            package["acceptance"]["criteria"][0]["evidence_references"][0] = value
        else:
            raise AssertionError(f"unsupported acceptance mutation: {mutation}")
        return
    if target == "transition-register":
        condition_id = mutation["field_path"].split(".")[-1]
        package["transition"]["blocking_conditions"] = [
            row
            for row in package["transition"]["blocking_conditions"]
            if row["condition_id"] != condition_id
        ]
        return
    if target == "human-approval-observation":
        if mutation["field_path"] == "$":
            package["approval"] = {}
        else:
            field = mutation["field_path"]
            package["approval"][field] = value
            if field == "approver_type":
                package["approval"]["authored_by_human"] = False
        return
    if target == "final-completion-manifest":
        field_aliases = {
            "pre_merge_tracker_231_state": "tracker_231_state_before_merge",
            "pre_merge_issue_252_state": "issue_252_state_before_merge",
            "pre_merge_m15_state": "m15_state_before_merge",
        }
        field = field_aliases.get(mutation["field_path"], mutation["field_path"])
        package["manifest"][field] = value
        return
    if target == "release-preparation-record":
        field = mutation["field_path"]
        field_aliases = {
            "release_target.tag_state_before_merge": "tag_state_before_merge",
            "release_target.github_release_state_before_merge": (
                "github_release_state_before_merge"
            ),
            "release_target.tag_target_rule": "tag_target_rule",
        }
        field = field_aliases.get(field, field)
        if operation == "remove":
            package["release"].pop(field, None)
        else:
            package["release"][field] = value
        return
    if target == "readme-transition-observation":
        aliases = {
            "release_entry_reviewed": "v0_14_0_release_state_entry_present",
            "current_status_transition_reviewed": "current_status_changed",
            "tag_exists_claim": "v0_14_0_tag_exists_claim",
            "github_release_exists_claim": "github_release_published_claim",
        }
        package["readme"][aliases[mutation["field_path"]]] = value
        return
    if target == "external-verification-receipt":
        field = mutation["field_path"]
        if field.startswith("commands[0]."):
            package["receipt"]["commands"][0][field.split(".", 1)[1]] = value
        elif field == "execution_candidate_head_sha":
            package["receipt"][field] = value
            for command in package["receipt"]["commands"]:
                command["execution_candidate_head_sha"] = value
        else:
            package["receipt"][field] = value
        return
    if target == "runtime-result":
        package["manifest"][mutation["field_path"]] = value
        return
    raise AssertionError(f"unhandled scenario mutation: {mutation}")


class M15FinalCompletionContractAndSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_json(SCHEMA_PATH)
        cls.records = load_records()

    def test_001_schema_is_draft_2020_12(self):
        self.assertEqual(
            self.schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )

    def test_002_schema_has_exactly_twelve_document_kinds(self):
        self.assertEqual(len(self.schema["oneOf"]), 12)

    def test_003_every_object_definition_is_closed_and_fully_required(self):
        definitions = [
            definition
            for definition in self.schema["$defs"].values()
            if definition.get("type") == "object"
        ]
        self.assertGreaterEqual(len(definitions), 15)
        for definition in definitions:
            with self.subTest(title=definition.get("title")):
                self.assertIs(definition.get("additionalProperties"), False)
                self.assertEqual(
                    set(definition.get("required", [])),
                    set(definition.get("properties", {})),
                )

    def test_004_schema_closes_git_digest_and_timestamp_formats(self):
        self.assertEqual(
            self.schema["$defs"]["gitSha"]["pattern"],
            "^[0-9a-f]{40}$",
        )
        self.assertEqual(
            self.schema["$defs"]["sha256"]["pattern"],
            "^[0-9a-f]{64}$",
        )
        self.assertIn("Z$", self.schema["$defs"]["rfc3339Utc"]["pattern"])

    def test_005_schema_closes_outcomes(self):
        self.assertEqual(
            self.schema["$defs"]["outcome"]["enum"],
            [READY, NOT_READY, BLOCKED],
        )

    def test_006_schema_binds_exact_authority_boundary(self):
        self.assertEqual(
            self.schema["$defs"]["authorityBoundary"]["const"],
            AUTHORITY_BOUNDARY,
        )

    def test_007_all_maintained_records_are_schema_valid(self):
        for name, document in self.records.items():
            with self.subTest(name=name):
                self.assertEqual(
                    validate_draft_2020_12_subset(document, self.schema),
                    [],
                )

    def test_008_schema_rejects_an_additional_manifest_property(self):
        document = copy.deepcopy(self.records["manifest"])
        document["evaluator_is_human_approval"] = True
        self.assertTrue(validate_draft_2020_12_subset(document, self.schema))

    def test_009_contract_names_all_eleven_runtime_inputs(self):
        contract = CONTRACT_PATH.read_text(encoding="utf-8")
        for phrase in (
            "final completion manifest",
            "Track A-E3 evidence inventory",
            "E3 continuity record",
            "E3 external-evidence record",
            "acceptance-coverage matrix",
            "transition register",
            "README transition observation",
            "release-preparation record",
            "pull-request observation",
            "external verification receipt",
            "human approval observation",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, contract)

    def test_010_contract_separates_completion_from_publication(self):
        contract = CONTRACT_PATH.read_text(encoding="utf-8")
        self.assertIn("Manual v0.14.0 publication", contract)
        self.assertIn("tag target is never the candidate head", contract)
        self.assertIn("Publication remains separate", contract)

    def test_011_contract_prohibits_generated_human_approval(self):
        contract = CONTRACT_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "Codex, CI, an evaluator, a bot, or a generated artifact cannot be the human",
            contract,
        )

    def test_012_contract_preserves_aaos_owned_sealing(self):
        contract = CONTRACT_PATH.read_text(encoding="utf-8")
        self.assertIn("Decision Proof sealing remains AAOS-owned", contract)
        self.assertIn("Learning Proof sealing remains AAOS-owned", contract)
        self.assertIn("AAOS remains the decision sovereignty layer", contract)

    def test_013_scenario_inventory_has_sixty_standalone_documents(self):
        self.assertEqual(len(SCENARIO_PATHS), 60)
        self.assertEqual(
            [path.name.split("-")[3] for path in SCENARIO_PATHS],
            [f"{number:02d}" for number in range(1, 61)],
        )

    def test_014_all_scenarios_are_schema_valid(self):
        for path in SCENARIO_PATHS:
            with self.subTest(path=path.name):
                self.assertEqual(
                    validate_draft_2020_12_subset(load_json(path), self.schema),
                    [],
                )

    def test_015_all_scenarios_are_synthetic_inert_offline_and_deterministic(self):
        for path in SCENARIO_PATHS:
            document = load_json(path)
            with self.subTest(path=path.name):
                self.assertIs(document["synthetic"], True)
                self.assertIs(document["inert"], True)
                self.assertIs(document["offline"], True)
                self.assertIs(document["deterministic"], True)

    def test_016_all_scenarios_have_no_sensitive_or_executable_payload(self):
        flags = (
            "contains_secret",
            "contains_credential",
            "contains_personal_data",
            "contains_private_prompt",
            "contains_production_identifier",
            "contains_executable_payload",
            "contains_live_github_mutation",
        )
        for path in SCENARIO_PATHS:
            document = load_json(path)
            with self.subTest(path=path.name):
                for flag in flags:
                    self.assertIs(document[flag], False)

    def test_017_scenarios_do_not_embed_command_or_secret_shaped_keys(self):
        forbidden = {
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
            with self.subTest(path=path.name):
                self.assertFalse(forbidden.intersection(load_json(path)))

    def test_017a_external_pr_observation_is_schema_valid_and_bound_to_pr_253(self):
        observation = build_external_pr_observation()
        self.assertEqual(
            validate_draft_2020_12_subset(observation, self.schema),
            [],
        )
        self.assertEqual(observation["pull_request_number"], 253)
        self.assertIn("pull/253", observation["evidence_reference"])

    def test_017b_external_verification_receipt_is_schema_valid(self):
        observation = build_external_pr_observation()
        receipt = build_external_verification_receipt(
            self.records["manifest"], observation
        )
        self.assertEqual(
            validate_draft_2020_12_subset(receipt, self.schema),
            [],
        )
        payload = copy.deepcopy(receipt)
        expected = payload.pop("canonical_payload_sha256")
        self.assertEqual(canonical_json_sha256(payload), expected)

    def test_017c_synthetic_exact_human_approval_is_schema_valid(self):
        observation = build_external_pr_observation()
        receipt = build_external_verification_receipt(
            self.records["manifest"], observation
        )
        approval = build_human_approval(observation, receipt, self.records["readme"])
        self.assertEqual(
            validate_draft_2020_12_subset(approval, self.schema),
            [],
        )


class M15FinalCompletionGitEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = load_json(RECORD_PATHS["inventory"])
        cls.continuity = load_json(RECORD_PATHS["continuity"])
        cls.external = load_json(RECORD_PATHS["external"])

    def test_018_source_main_base_is_an_immutable_commit_object(self):
        self.assertEqual(git_text("cat-file", "-t", SOURCE_MAIN_BASE_SHA), "commit")

    def test_019_source_main_base_tree_matches_the_exact_binding(self):
        self.assertEqual(
            git_text("rev-parse", f"{SOURCE_MAIN_BASE_SHA}^{{tree}}"),
            SOURCE_MAIN_BASE_TREE_SHA,
        )

    def test_020_source_main_base_is_an_ancestor_of_head(self):
        completed = subprocess.run(
            [GIT, "merge-base", "--is-ancestor", SOURCE_MAIN_BASE_SHA, "HEAD"],
            cwd=ROOT,
            check=False,
        )
        self.assertEqual(completed.returncode, 0)

    def test_021_ancestor_check_remains_valid_when_head_is_ahead(self):
        self.assertNotEqual(git_text("rev-parse", "HEAD"), SOURCE_MAIN_BASE_SHA)
        self.assertGreater(
            int(git_text("rev-list", "--count", f"{SOURCE_MAIN_BASE_SHA}..HEAD")),
            0,
        )
        self.assertEqual(
            git_text("merge-base", SOURCE_MAIN_BASE_SHA, "HEAD"),
            SOURCE_MAIN_BASE_SHA,
        )

    def test_022_no_mutable_main_ref_is_part_of_source_base_validation(self):
        source = Path(__file__).read_text(encoding="utf-8")
        self.assertNotIn("origin" + "/main", source)

    def test_023_e3_candidate_and_merge_are_commit_objects(self):
        self.assertEqual(git_text("cat-file", "-t", E3_CANDIDATE_SHA), "commit")
        self.assertEqual(git_text("cat-file", "-t", E3_MERGE_SHA), "commit")

    def test_024_e3_candidate_and_merge_trees_match_exactly(self):
        self.assertEqual(
            git_text("rev-parse", f"{E3_CANDIDATE_SHA}^{{tree}}"), E3_TREE_SHA
        )
        self.assertEqual(
            git_text("rev-parse", f"{E3_MERGE_SHA}^{{tree}}"), E3_TREE_SHA
        )

    def test_025_e3_merge_parents_match_git_order(self):
        self.assertEqual(
            git_text("show", "-s", "--format=%P", E3_MERGE_SHA).split(),
            [E3_BASE_SHA, E3_CANDIDATE_SHA],
        )

    def test_026_e3_candidate_to_merge_diff_is_empty(self):
        self.assertEqual(
            git_text("diff", "--name-status", E3_CANDIDATE_SHA, E3_MERGE_SHA),
            "",
        )
        self.assertEqual(self.continuity["candidate_to_merge_changed_path_count"], 0)
        self.assertEqual(
            self.continuity["additional_merge_result_difference_count"], 0
        )

    def test_027_e3_candidate_is_a_merge_ancestor(self):
        completed = subprocess.run(
            [GIT, "merge-base", "--is-ancestor", E3_CANDIDATE_SHA, E3_MERGE_SHA],
            cwd=ROOT,
            check=False,
        )
        self.assertEqual(completed.returncode, 0)

    def test_028_e3_continuity_record_is_exact_tree_match(self):
        self.assertEqual(self.continuity["source_main_base_sha"], E3_BASE_SHA)
        self.assertEqual(self.continuity["candidate_sha"], E3_CANDIDATE_SHA)
        self.assertEqual(self.continuity["candidate_tree_sha"], E3_TREE_SHA)
        self.assertEqual(self.continuity["merge_sha"], E3_MERGE_SHA)
        self.assertEqual(self.continuity["merge_tree_sha"], E3_TREE_SHA)
        self.assertEqual(
            self.continuity["merge_parents"], [E3_BASE_SHA, E3_CANDIDATE_SHA]
        )
        self.assertIs(self.continuity["source_main_base_is_merge_parent"], True)
        self.assertIs(self.continuity["candidate_is_merge_parent"], True)
        self.assertEqual(self.continuity["relation"], "exact_tree_match")

    def test_029_active_and_superseded_e3_evidence_are_distinct(self):
        self.assertEqual(
            self.external["active_observation_comment_id"],
            E3_ACTIVE_OBSERVATION_COMMENT_ID,
        )
        self.assertEqual(
            self.external["active_receipt_comment_id"],
            E3_ACTIVE_RECEIPT_COMMENT_ID,
        )
        self.assertEqual(
            self.external["active_receipt_canonical_sha256"],
            E3_ACTIVE_RECEIPT_SHA256,
        )
        self.assertEqual(
            self.external["superseded_observation_comment_id"],
            E3_SUPERSEDED_OBSERVATION_COMMENT_ID,
        )
        self.assertEqual(
            self.external["superseded_receipt_comment_id"],
            E3_SUPERSEDED_RECEIPT_COMMENT_ID,
        )
        self.assertEqual(
            self.external["superseded_observation_classification"],
            "superseded-historical-evidence",
        )
        self.assertEqual(
            self.external["superseded_receipt_classification"],
            "superseded-historical-evidence",
        )
        self.assertIs(self.external["active_observation_is_superseded"], False)
        self.assertIs(self.external["active_receipt_is_superseded"], False)

    def test_030_inventory_has_exact_209_phase_addressed_rows(self):
        artifacts = self.inventory["artifacts"]
        self.assertEqual(len(artifacts), 209)
        self.assertEqual(
            dict(Counter(item["track_id"] for item in artifacts)),
            TRACK_COUNTS,
        )

    def test_031_e3_inventory_preserves_five_separate_evidence_roles(self):
        roles = Counter(
            item["evidence_role"]
            for item in self.inventory["artifacts"]
            if item["track_id"] == "track-e3"
        )
        self.assertEqual(sum(roles.values()), 53)
        self.assertEqual(len(roles), 5)
        self.assertEqual(
            set(roles),
            {
                "e3-core-completion-readiness-artifact",
                "e3-synthetic-scenario",
                "e3-maintained-evidence-record",
                "e3-readme-next-phase-transition",
                "e3-authorized-historical-compatibility-repair",
            },
        )

    def test_032_every_inventory_row_matches_its_immutable_git_blob(self):
        summaries = {
            item["track_id"]: item for item in self.inventory["track_summaries"]
        }
        for artifact in self.inventory["artifacts"]:
            summary = summaries[artifact["track_id"]]
            with self.subTest(track=artifact["track_id"], path=artifact["repository_path"]):
                entry = git_text(
                    "ls-tree", summary["merge_sha"], "--", artifact["repository_path"]
                ).split()
                self.assertGreaterEqual(len(entry), 3)
                self.assertEqual(entry[0], artifact["git_file_mode"])
                self.assertEqual(entry[1], "blob")
                self.assertEqual(entry[2], artifact["git_blob_sha"])
                blob = git_bytes("cat-file", "blob", artifact["git_blob_sha"])
                self.assertEqual(
                    canonical_sha256(blob), artifact["canonical_text_sha256"]
                )

    def test_033_inventory_rows_match_the_immutable_runtime_catalog_exactly(self):
        observed = tuple(
            tuple(artifact[field] for field in ARTIFACT_BINDING_FIELDS)
            for artifact in self.inventory["artifacts"]
        )
        self.assertEqual(observed, EXPECTED_ARTIFACT_BINDINGS)

    def test_034_inventory_binding_digest_is_canonical(self):
        payload = copy.deepcopy(self.inventory)
        expected = payload.pop("inventory_binding_sha256")
        self.assertEqual(canonical_json_sha256(payload), expected)


class M15FinalCompletionReadmeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.observation = load_json(RECORD_PATHS["readme"])
        cls.base = git_bytes("show", f"{SOURCE_MAIN_BASE_SHA}:README.md")
        cls.candidate = git_bytes("show", f"{E4_MERGE_SHA}:README.md")
        cls.base_sections = level_two_sections(cls.base)
        cls.candidate_sections = level_two_sections(cls.candidate)

    def test_035_whole_readme_digests_match_the_observation(self):
        self.assertEqual(
            canonical_sha256(self.base),
            self.observation["base_readme_sha256"],
        )
        self.assertEqual(
            canonical_sha256(self.candidate),
            self.observation["candidate_readme_sha256"],
        )

    def test_036_only_permitted_level_two_sections_changed(self):
        self.assertEqual(set(self.base_sections), set(self.candidate_sections))
        changed = {
            name
            for name in self.base_sections
            if self.base_sections[name] != self.candidate_sections[name]
        }
        self.assertEqual(changed, {"Releases", "Current Status", "Next Phase"})

    def test_037_releases_adds_exactly_one_repository_state_entry(self):
        base_lines = self.base_sections["Releases"].splitlines()
        candidate_lines = self.candidate_sections["Releases"].splitlines()
        additions = [line for line in candidate_lines if line not in base_lines]
        self.assertEqual(
            [line for line in additions if line.startswith("- v0.14.0")],
            [EXPECTED_RELEASE_ENTRY],
        )
        self.assertIn(
            "v0.14.0 declares M15 complete and prepares the repository for the v0.14.0 release state.",
            additions,
        )
        self.assertNotIn("v0.14.0 is published", self.candidate_sections["Releases"])

    def test_038_current_baseline_includes_the_m15_pattern(self):
        releases = self.candidate_sections["Releases"]
        self.assertIn(
            "the M15 Learning Sovereignty and Evidence-Bound Capability Memory pattern",
            releases,
        )

    def test_039_current_status_declares_m1_through_m15_complete(self):
        status = self.candidate_sections["Current Status"]
        self.assertIn(
            "M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11, M12, M13, M14, and M15 are complete.",
            status,
        )
        self.assertIn("M15 completed:", status)

    def test_040_current_status_binds_all_m15_tracks_and_actual_e4_pr(self):
        status = self.candidate_sections["Current Status"]
        for reference in (
            "#231",
            "#232 / PR #233",
            "#234 / PR #237",
            "#238 / PR #239",
            "#240 / PR #241",
            "#242 / PR #243",
            "#248 / PR #249",
            "#250 / PR #251",
            "#252 / PR #253",
        ):
            with self.subTest(reference=reference):
                self.assertIn(reference, status)

    def test_041_next_phase_is_exact_post_merge_publication_path(self):
        self.assertEqual(
            self.candidate_sections["Next Phase"],
            EXPECTED_NEXT_PHASE,
        )

    def test_042_next_phase_does_not_claim_tag_or_release_already_exists(self):
        next_phase = self.candidate_sections["Next Phase"]
        self.assertIn("does not claim that the tag or GitHub Release already exists", next_phase)
        self.assertNotIn("tag v0.14.0 exists", next_phase)
        self.assertNotIn("GitHub Release v0.14.0 is published", next_phase)

    def test_043_next_phase_preserves_all_sovereignty_boundaries(self):
        next_phase = self.candidate_sections["Next Phase"]
        self.assertIn("Decision Proof sealing remains AAOS-owned", next_phase)
        self.assertIn("Learning Proof sealing remains AAOS-owned", next_phase)
        self.assertIn("AAOS remains the decision sovereignty layer", next_phase)

    def test_044_readme_section_digests_match_the_observation(self):
        key_by_section = {
            "Releases": "releases",
            "Current Status": "current_status",
            "Next Phase": "next_phase",
        }
        for title, key in key_by_section.items():
            with self.subTest(section=title):
                self.assertEqual(
                    canonical_sha256(self.base_sections[title].encode("utf-8")),
                    self.observation[f"base_{key}_section_sha256"],
                )
                self.assertEqual(
                    canonical_sha256(self.candidate_sections[title].encode("utf-8")),
                    self.observation[f"candidate_{key}_section_sha256"],
                )
        self.assertEqual(
            canonical_sha256(current_baseline_section(self.base).encode("utf-8")),
            self.observation["base_current_baseline_section_sha256"],
        )
        self.assertEqual(
            canonical_sha256(current_baseline_section(self.candidate).encode("utf-8")),
            self.observation["candidate_current_baseline_section_sha256"],
        )
        self.assertEqual(
            self.observation["candidate_completion_state_sha256"],
            self.observation["candidate_current_status_section_sha256"],
        )


class M15FinalCompletionRuntimeTests(unittest.TestCase):
    def test_045_runtime_signature_is_closed_to_exactly_eleven_mappings(self):
        self.assertEqual(
            list(inspect.signature(evaluate_final_completion).parameters),
            [
                "final_completion_manifest",
                "track_evidence_inventory",
                "e3_continuity_record",
                "e3_external_evidence",
                "acceptance_coverage_matrix",
                "transition_register",
                "readme_transition_observation",
                "release_preparation_record",
                "pull_request_observation",
                "external_verification_receipt",
                "human_approval_observation",
            ],
        )

    def test_046_exact_synthetic_human_approval_produces_ready_evidence(self):
        result = evaluate_package(load_package())
        self.assertEqual(result["outcome"], READY)
        self.assertEqual(result["blocking_findings"], [])
        self.assertEqual(result["readiness_findings"], [])
        self.assertIs(result["human_approval_present"], True)

    def test_047_missing_human_approval_is_not_ready(self):
        result = evaluate_package(load_package(include_approval=False))
        self.assertEqual(result["outcome"], NOT_READY)
        self.assertIn("missing-human-approval", result["readiness_findings"])
        self.assertIs(result["human_approval_present"], False)

    def test_048_blocking_finding_precedes_missing_approval(self):
        package = load_package(include_approval=False)
        package["continuity"]["merge_sha"] = "1" * 40
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertTrue(result["blocking_findings"])
        self.assertIn("missing-human-approval", result["readiness_findings"])

    def test_049_result_is_explicitly_caller_data_only_and_non_mutating(self):
        result = evaluate_package(load_package())
        expected = {
            "caller_data_only": True,
            "file_io_performed": False,
            "git_inspection_performed": False,
            "github_access_performed": False,
            "network_access_performed": False,
            "subprocess_executed": False,
            "repository_digests_calculated": False,
            "receipt_digests_calculated": False,
            "verification_commands_executed": False,
            "external_state_mutated": False,
            "merge_executed": False,
            "m15_state": "active-and-incomplete",
            "tracker_231_state": "open",
            "issue_252_state": "open",
            "tag_state": "not-created",
            "github_release_state": "not-published",
            "decision_proof_sealed": False,
            "learning_proof_sealed": False,
        }
        for key, value in expected.items():
            with self.subTest(key=key):
                self.assertEqual(result[key], value)

    def test_050_runtime_does_not_mutate_any_caller_mapping(self):
        package = load_package()
        before = copy.deepcopy(package)
        evaluate_package(package)
        self.assertEqual(package, before)

    def test_051_runtime_has_no_prohibited_imports(self):
        tree = ast.parse(EVALUATOR_PATH.read_text(encoding="utf-8"))
        prohibited = {
            "pathlib",
            "os",
            "io",
            "json",
            "hashlib",
            "subprocess",
            "socket",
            "urllib",
            "requests",
            "github",
            "importlib",
        }
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertFalse(imported.intersection(prohibited))

    def test_052_runtime_has_no_prohibited_calls(self):
        tree = ast.parse(EVALUATOR_PATH.read_text(encoding="utf-8"))
        prohibited = {
            "open",
            "eval",
            "exec",
            "compile",
            "__import__",
            "system",
            "popen",
            "run",
            "call",
            "check_call",
            "check_output",
            "urlopen",
        }
        called = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name):
                called.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                called.add(node.func.attr)
        self.assertFalse(called.intersection(prohibited))

    def test_053_runtime_has_no_mutation_or_authority_verbs_in_api(self):
        names = {node.name for node in ast.walk(ast.parse(EVALUATOR_PATH.read_text(encoding="utf-8"))) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        for fragment in (
            "write",
            "delete",
            "checkout",
            "commit",
            "merge_pull",
            "close_issue",
            "create_tag",
            "publish_release",
        ):
            with self.subTest(fragment=fragment):
                self.assertFalse(any(fragment in name for name in names))

    def test_054_inventory_path_and_digest_substitution_is_blocked(self):
        package = load_package()
        package["inventory"]["artifacts"][0]["repository_path"] = (
            "docs/synthetic-well-formed-substitution.md"
        )
        package["inventory"]["artifacts"][0]["canonical_text_sha256"] = "1" * 64
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn("track-a-e3-evidence-substitution", result["blocking_findings"])

    def test_055_acceptance_criterion_text_substitution_is_blocked(self):
        package = load_package()
        package["acceptance"]["criteria"][0]["criterion_text"] = (
            "Synthetic substituted criterion text."
        )
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn("substituted-acceptance-evidence", result["blocking_findings"])

    def test_056_arbitrary_acceptance_reference_is_blocked(self):
        package = load_package()
        package["acceptance"]["criteria"][0]["evidence_references"] = [
            "urn:aaos:synthetic:arbitrary-reference"
        ]
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn("substituted-acceptance-evidence", result["blocking_findings"])

    def test_057_missing_acceptance_criterion_is_blocked_and_not_covered(self):
        package = load_package()
        package["acceptance"]["criteria"].pop()
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIs(result["all_criteria_covered"], False)

    def test_058_partial_criterion_is_not_covered(self):
        package = load_package()
        package["acceptance"]["criteria"][0]["coverage_state"] = "partial"
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIs(result["all_criteria_covered"], False)

    def test_059_hidden_blocker_is_blocked(self):
        package = load_package()
        package["transition"]["blocking_conditions"].pop()
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn("hidden-completion-blocker", result["blocking_findings"])

    def test_060_superseded_e3_observation_cannot_be_active(self):
        package = load_package()
        package["external"]["active_observation_comment_id"] = (
            E3_SUPERSEDED_OBSERVATION_COMMENT_ID
        )
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn("superseded-e3-observation-used", result["blocking_findings"])

    def test_061_superseded_e3_receipt_cannot_be_active(self):
        package = load_package()
        package["external"]["active_receipt_comment_id"] = E3_SUPERSEDED_RECEIPT_COMMENT_ID
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn("superseded-e3-receipt-used", result["blocking_findings"])

    def test_062_human_approval_for_another_candidate_is_blocked(self):
        package = load_package()
        package["approval"]["candidate_head_sha"] = "1" * 40
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn("human-approval-candidate-mismatch", result["blocking_findings"])

    def test_063_human_approval_for_another_receipt_is_blocked(self):
        package = load_package()
        package["approval"]["verification_receipt_canonical_sha256"] = "1" * 64
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn("human-approval-receipt-mismatch", result["blocking_findings"])

    def test_064_nonhuman_approver_is_blocked(self):
        package = load_package()
        package["approval"]["approver_type"] = "automation"
        package["approval"]["authored_by_human"] = False
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)

    def test_065_candidate_head_cannot_be_the_final_tag_target(self):
        package = load_package()
        package["release"]["tag_target_rule"] = "candidate-head"
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)

    def test_066_verification_below_minimum_is_blocked(self):
        package = load_package()
        command = receipt_command(package, "e3-targeted")
        command["tests_observed"] -= 1
        command["passes"] -= 1
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn("insufficient-verification-coverage", result["blocking_findings"])

    def test_067_verification_failure_is_blocked(self):
        package = load_package()
        command = receipt_command(package)
        command["passes"] -= 1
        command["failures"] = 1
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)

    def test_068_verification_error_is_blocked(self):
        package = load_package()
        command = receipt_command(package)
        command["passes"] -= 1
        command["errors"] = 1
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)

    def test_069_verification_skip_is_blocked(self):
        package = load_package()
        command = receipt_command(package)
        command["passes"] -= 1
        command["skips"] = 1
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)

    def test_070_verification_nonzero_exit_is_blocked(self):
        package = load_package()
        receipt_command(package)["exit_code"] = 1
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)

    def test_071_observation_and_receipt_for_pr_254_are_blocked(self):
        package = load_package()
        package["observation"]["pull_request_number"] = 254
        package["receipt"]["pull_request_number"] = 254
        package["approval"]["pull_request_number"] = 254
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)


class M15FinalCompletionCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load_records()
        cls.schema = load_json(SCHEMA_PATH)

    def test_072_all_sixteen_acceptance_criteria_match_exact_catalog(self):
        rows = self.records["acceptance"]["criteria"]
        observed = tuple(
            tuple(row[field] if field not in {"evidence_references", "artifact_references", "test_references"} else tuple(row[field]) for field in ACCEPTANCE_BINDING_FIELDS)
            for row in rows
        )
        self.assertEqual(observed, EXPECTED_ACCEPTANCE_CRITERIA)
        self.assertEqual(len(observed), 16)

    def test_073_every_acceptance_criterion_is_covered_with_evidence(self):
        for row in self.records["acceptance"]["criteria"]:
            with self.subTest(criterion=row["criterion_id"]):
                self.assertEqual(row["coverage_state"], "covered")
                self.assertTrue(row["evidence_references"])
                self.assertTrue(row["artifact_references"])
                self.assertTrue(row["test_references"])
                self.assertEqual(row["authority_boundary"], AUTHORITY_BOUNDARY)

    def test_074_manifest_binds_exact_eighteen_command_registry(self):
        observed = tuple(
            (
                row["command_id"],
                tuple(row["declared_logical_argv"]),
                row["execution_scope"],
                row["minimum_tests_observed"],
            )
            for row in self.records["manifest"]["verification_commands"]
        )
        self.assertEqual(observed, EXPECTED_VERIFICATION_COMMANDS)
        self.assertEqual(len(observed), 18)
        self.assertEqual(tuple(row[0] for row in observed), COMMAND_IDS)

    def test_075_all_required_blockers_are_explicit(self):
        self.assertEqual(
            tuple(row["condition_id"] for row in self.records["transition"]["blocking_conditions"]),
            REQUIRED_BLOCKERS,
        )

    def test_076_all_readiness_findings_are_explicit(self):
        self.assertEqual(
            tuple(row["finding_id"] for row in self.records["transition"]["readiness_requirements"]),
            REQUIRED_READINESS_FINDINGS,
        )

    def test_077_inherited_minima_are_never_lowered(self):
        minima = {row[0]: row[3] for row in EXPECTED_VERIFICATION_COMMANDS}
        lower_bounds = {
            "e3-targeted": 167,
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
            "full-maintained-suite": 2092,
        }
        for command_id, minimum in lower_bounds.items():
            with self.subTest(command=command_id):
                self.assertGreaterEqual(minima[command_id], minimum)

    def test_078_e4_targeted_minimum_is_real_and_nonzero(self):
        minima = {row[0]: row[3] for row in EXPECTED_VERIFICATION_COMMANDS}
        self.assertEqual(minima["e4-targeted"], 183)
        self.assertEqual(minima["full-maintained-suite"], 2275)

    def test_079_manifest_and_receipt_arbitrary_command_substitution_is_blocked(self):
        package = load_package()
        manifest_row = package["manifest"]["verification_commands"][0]
        receipt_row = receipt_command(package)
        arbitrary = ["python", "-m", "unittest", "tests.synthetic_arbitrary", "-v"]
        manifest_row["declared_logical_argv"] = arbitrary
        receipt_row["declared_logical_argv"] = arbitrary
        receipt_row["actual_argv"] = [ACTUAL_PYTHON_LAUNCHER, *arbitrary[1:]]
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn("verification-command-registry-mismatch", result["blocking_findings"])

    def test_080_unittest_selector_substitution_is_blocked(self):
        package = load_package()
        command = package["manifest"]["verification_commands"][1]
        command["declared_logical_argv"][5] = "tests.synthetic_substitution"
        receipt = receipt_command(package, command["command_id"])
        receipt["declared_logical_argv"] = list(command["declared_logical_argv"])
        receipt["actual_argv"] = [
            ACTUAL_PYTHON_LAUNCHER,
            *command["declared_logical_argv"][1:],
        ]
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)

    def test_081_two_verification_scopes_exchanged_is_blocked(self):
        package = load_package()
        left = package["manifest"]["verification_commands"][0]
        right = package["manifest"]["verification_commands"][1]
        left["execution_scope"], right["execution_scope"] = (
            right["execution_scope"], left["execution_scope"]
        )
        receipt_command(package, left["command_id"])["execution_scope"] = left[
            "execution_scope"
        ]
        receipt_command(package, right["command_id"])["execution_scope"] = right[
            "execution_scope"
        ]
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)

    def test_082_full_suite_id_bound_to_non_discovery_command_is_blocked(self):
        package = load_package()
        command = package["manifest"]["verification_commands"][-1]
        command["declared_logical_argv"] = [
            "python",
            "-X",
            "faulthandler",
            "-m",
            "unittest",
            "tests.test_m15_final_completion_evaluator",
            "-v",
        ]
        receipt = receipt_command(package, "full-maintained-suite")
        receipt["declared_logical_argv"] = list(command["declared_logical_argv"])
        receipt["actual_argv"] = [
            ACTUAL_PYTHON_LAUNCHER,
            *command["declared_logical_argv"][1:],
        ]
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)

    def test_083_exact_five_authorized_compatibility_repairs_are_bound(self):
        rows = self.records["manifest"][
            "authorized_historical_compatibility_repairs"
        ]
        observed = tuple(
            tuple(row[field] for field in COMPATIBILITY_REPAIR_BINDING_FIELDS)
            for row in rows
        )
        self.assertEqual(observed, EXPECTED_AUTHORIZED_COMPATIBILITY_REPAIRS)
        self.assertEqual(len(rows), 5)
        self.assertTrue(
            all(row["human_authorized_bounded_exception"] for row in rows)
        )
        self.assertTrue(
            all(
                not row["counted_in_prior_track_artifact_inventory"]
                for row in rows
            )
        )

    def test_084_compatibility_repair_digests_are_phase_separated(self):
        rows = self.records["manifest"][
            "authorized_historical_compatibility_repairs"
        ]
        for row in rows:
            with self.subTest(path=row["path"]):
                historical = f"{row['historical_source_commit_sha']}:{row['path']}"
                self.assertEqual(
                    git_text("rev-parse", historical),
                    row["historical_git_blob_sha"],
                )
                self.assertEqual(
                    canonical_sha256(git_bytes("cat-file", "blob", historical)),
                    row["historical_canonical_sha256"],
                )
                if row["prior_compatibility_commit_sha"] is None:
                    self.assertIsNone(row["prior_compatibility_git_blob_sha"])
                    self.assertIsNone(row["prior_compatibility_canonical_sha256"])
                    self.assertIsNone(row["prior_compatibility_evidence_role"])
                else:
                    prior = f"{row['prior_compatibility_commit_sha']}:{row['path']}"
                    self.assertEqual(
                        git_text("rev-parse", prior),
                        row["prior_compatibility_git_blob_sha"],
                    )
                    self.assertEqual(
                        canonical_sha256(git_bytes("cat-file", "blob", prior)),
                        row["prior_compatibility_canonical_sha256"],
                    )
                e4_candidate = f"{E4_MERGE_SHA}:{row['path']}"
                self.assertEqual(
                    git_text("rev-parse", e4_candidate),
                    row["e4_candidate_git_blob_sha"],
                )
                self.assertEqual(
                    canonical_sha256(git_bytes("cat-file", "blob", e4_candidate)),
                    row["e4_candidate_canonical_sha256"],
                )
                self.assertNotEqual(
                    row["historical_canonical_sha256"],
                    row["e4_candidate_canonical_sha256"],
                )

    def test_085_sixth_compatibility_path_is_schema_invalid_and_blocked(self):
        package = load_package()
        package["manifest"]["authorized_historical_compatibility_repairs"].append(
            {
                **copy.deepcopy(
                    package["manifest"][
                        "authorized_historical_compatibility_repairs"
                    ][0]
                ),
                "path": "tests/unapproved_historical_cleanup.py",
            }
        )
        self.assertTrue(
            validate_draft_2020_12_subset(package["manifest"], self.schema)
        )
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn("unapproved-compatibility-repair", result["blocking_findings"])

    def test_086_compatibility_registry_mutation_is_blocked_without_digest_work(self):
        package = load_package()
        package["manifest"]["authorized_historical_compatibility_repairs"][0][
            "e4_candidate_canonical_sha256"
        ] = "0" * 64
        result = evaluate_package(package)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertIn("unapproved-compatibility-repair", result["blocking_findings"])
        self.assertFalse(result["repository_digests_calculated"])


def _make_criterion_catalog_test(index):
    def test(self):
        row = load_json(RECORD_PATHS["acceptance"])["criteria"][index]
        observed = tuple(
            tuple(row[field])
            if field in {"evidence_references", "artifact_references", "test_references"}
            else row[field]
            for field in ACCEPTANCE_BINDING_FIELDS
        )
        self.assertEqual(observed, EXPECTED_ACCEPTANCE_CRITERIA[index])
        self.assertEqual(row["coverage_state"], "covered")

    return test


for _criterion_index in range(16):
    setattr(
        M15FinalCompletionCoverageTests,
        f"test_criterion_{_criterion_index + 1:02d}_matches_exact_catalog",
        _make_criterion_catalog_test(_criterion_index),
    )


def _make_command_catalog_test(index):
    def test(self):
        row = load_json(RECORD_PATHS["manifest"])["verification_commands"][index]
        observed = (
            row["command_id"],
            tuple(row["declared_logical_argv"]),
            row["execution_scope"],
            row["minimum_tests_observed"],
        )
        self.assertEqual(observed, EXPECTED_VERIFICATION_COMMANDS[index])

    return test


for _command_index in range(18):
    setattr(
        M15FinalCompletionCoverageTests,
        f"test_command_{_command_index + 1:02d}_matches_exact_catalog",
        _make_command_catalog_test(_command_index),
    )


def _make_scenario_test(path):
    def test(self):
        scenario = load_json(path)
        first_package = load_package()
        apply_scenario_mutation(first_package, scenario)
        first = evaluate_package(first_package)
        second_package = load_package()
        apply_scenario_mutation(second_package, scenario)
        second = evaluate_package(second_package)
        self.assertEqual(first, second)
        self.assertEqual(first["outcome"], scenario["expected_outcome"])
        expected_finding = scenario["expected_finding"]
        if expected_finding != "none":
            findings = first["blocking_findings"] + first["readiness_findings"]
            self.assertIn(expected_finding, findings)

    return test


class M15FinalCompletionScenarioTests(unittest.TestCase):
    pass


for _scenario_path in SCENARIO_PATHS:
    _scenario = load_json(_scenario_path)
    setattr(
        M15FinalCompletionScenarioTests,
        "test_" + _scenario["scenario_id"].replace("-", "_"),
        _make_scenario_test(_scenario_path),
    )
