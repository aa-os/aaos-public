import copy
import hashlib
import json
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.m15_post_release_governance_review_evaluator import (  # noqa: E402
    CANONICAL_RECORD_SHA256,
    CLASSIFICATIONS,
    EXPECTED_FINDING_IDS,
    M16_MAY_BEGIN_AFTER_AUTHORIZATION,
    M16_REMAIN_BLOCKED,
    MERGE_COMMIT_SHA,
    RETROSPECTIVE_AREAS,
    evaluate_post_release_governance_review,
)


SCHEMA_PATH = ROOT / "schemas" / "m15-post-release-governance-review.schema.json"
RECORD_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m15-post-release-governance-review-record.json"
)


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def canonical_sha256(value):
    payload = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def resolve_pointer(root, pointer):
    value = root
    for token in pointer.removeprefix("#/").split("/"):
        value = value[token.replace("~1", "/").replace("~0", "~")]
    return value


def validate_schema(schema, instance, root=None, path="$"):
    root = schema if root is None else root
    if "$ref" in schema:
        validate_schema(resolve_pointer(root, schema["$ref"]), instance, root, path)
        return
    if "oneOf" in schema:
        matches = 0
        for option in schema["oneOf"]:
            try:
                validate_schema(option, instance, root, path)
            except AssertionError:
                continue
            matches += 1
        assert matches == 1, f"{path} matches {matches} oneOf branches"
        return
    if "const" in schema:
        expected = schema["const"]
        assert type(instance) is type(expected) and instance == expected, (
            f"{path} must equal {expected!r}"
        )
    if "enum" in schema:
        assert any(
            type(instance) is type(option) and instance == option
            for option in schema["enum"]
        ), f"{path} is outside enum"

    schema_type = schema.get("type")
    if schema_type == "object":
        assert isinstance(instance, dict), f"{path} must be object"
        for required in schema.get("required", []):
            assert required in instance, f"{path}.{required} is required"
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = set(instance) - set(properties)
            assert not extra, f"{path} has unexpected keys {sorted(extra)}"
        for key, child in properties.items():
            if key in instance:
                validate_schema(child, instance[key], root, f"{path}.{key}")
    elif schema_type == "array":
        assert isinstance(instance, list), f"{path} must be array"
        assert len(instance) >= schema.get("minItems", 0), f"{path} is too short"
        if "maxItems" in schema:
            assert len(instance) <= schema["maxItems"], f"{path} is too long"
        if schema.get("uniqueItems"):
            encoded = [
                json.dumps(item, ensure_ascii=False, sort_keys=True)
                for item in instance
            ]
            assert len(encoded) == len(set(encoded)), f"{path} is not unique"
        for index, item in enumerate(instance):
            if "items" in schema:
                validate_schema(schema["items"], item, root, f"{path}[{index}]")
    elif schema_type == "string":
        assert isinstance(instance, str), f"{path} must be string"
        assert len(instance) >= schema.get("minLength", 0), f"{path} is too short"
        if "pattern" in schema:
            assert re.search(schema["pattern"], instance), f"{path} pattern mismatch"
    elif schema_type == "integer":
        assert isinstance(instance, int) and not isinstance(instance, bool)
        assert instance >= schema.get("minimum", instance)
    elif schema_type == "boolean":
        assert isinstance(instance, bool), f"{path} must be boolean"
    elif schema_type == "null":
        assert instance is None, f"{path} must be null"


class M15PostReleaseGovernanceReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_json(SCHEMA_PATH)
        cls.record = load_json(RECORD_PATH)

    def assert_mutation_fails_closed(self, mutation):
        candidate = copy.deepcopy(self.record)
        mutation(candidate)
        result = evaluate_post_release_governance_review(candidate)
        self.assertEqual(result["outcome"], "record_invalid")
        self.assertFalse(result["canonical_record_matches"])
        self.assertIn(
            "canonical-record-sha256-mismatch",
            result["validation_findings"],
        )
        self.assertEqual(
            result["m16_planning_recommendation"],
            M16_REMAIN_BLOCKED,
        )
        self.assertFalse(result["m16_authorized"])
        return result

    def test_01_record_matches_strict_schema(self):
        validate_schema(self.schema, self.record)

    def test_02_canonical_record_is_complete_for_human_review(self):
        self.assertEqual(canonical_sha256(self.record), CANONICAL_RECORD_SHA256)
        result = evaluate_post_release_governance_review(self.record)
        self.assertEqual(result["outcome"], "record_complete_for_human_review")
        self.assertEqual(result["validation_findings"], [])
        self.assertTrue(result["canonical_record_matches"])
        self.assertEqual(
            result["m16_planning_recommendation"],
            M16_MAY_BEGIN_AFTER_AUTHORIZATION,
        )
        self.assertFalse(result["m16_authorized"])

    def test_03_release_and_repository_bindings_are_exact(self):
        binding = self.record["tag_release_binding"]
        publication = self.record["publication_evidence_inventory"]
        consistency = self.record["repository_consistency"]
        self.assertEqual(binding["tag_ref_target_sha"], MERGE_COMMIT_SHA)
        self.assertEqual(binding["peeled_commit_sha"], MERGE_COMMIT_SHA)
        self.assertFalse(binding["historical_non_movement_proven"])
        self.assertEqual(publication["tag_name"], "v0.14.0")
        self.assertFalse(publication["draft"])
        self.assertFalse(publication["prerelease"])
        self.assertTrue(publication["latest"])
        self.assertEqual(publication["assets"]["uploaded_asset_count"], 0)
        self.assertTrue(consistency["main_contains_completion_merge"])
        issue_states = {
            issue["number"]: issue["state"] for issue in consistency["issues"]
        }
        self.assertEqual(issue_states, {252: "closed", 231: "closed", 254: "open"})

    def test_04_tagged_and_candidate_readme_states_are_distinct(self):
        consistency = self.record["repository_consistency"]
        tagged = consistency["tagged_readme_observation"]
        candidate = consistency["review_candidate_readme_observation"]
        self.assertTrue(tagged["stale_prepublication_statement_present"])
        self.assertFalse(candidate["stale_prepublication_statement_present"])
        self.assertTrue(candidate["published_latest_statement_present"])
        self.assertTrue(
            candidate["m16_separate_human_authorization_boundary_present"]
        )
        normalized = " ".join((ROOT / "README.md").read_text(encoding="utf-8").split())
        self.assertIn(
            "v0.14.0 is published as the Latest stable GitHub Release",
            normalized,
        )
        self.assertIn(
            "completion of #254 does not automatically authorize M16 planning",
            normalized,
        )

    def test_05_all_exact_command_receipts_are_present(self):
        runs = self.record["verification_runs"]
        self.assertEqual(len(runs), 36)
        by_id = {run["command_id"]: run for run in runs}
        self.assertEqual(len(by_id), 36)
        self.assertEqual(
            by_id["tag-commit-resolution"]["logical_argv"],
            ["git", "rev-parse", "v0.14.0^{commit}"],
        )
        self.assertEqual(
            by_id["tag-commit-resolution"]["result"],
            MERGE_COMMIT_SHA,
        )
        self.assertEqual(by_id["detached-head-symbolic-ref"]["exit_code"], 1)
        self.assertEqual(
            by_id["tagged-full-maintained-suite"]["raw_stderr_sha256"],
            "2acc1d73a38d6362a8f84c490dcbb0cac240cf98e26037277f9d025b921175fd",
        )
        self.assertEqual(
            by_id["tagged-tree-object-inventory"]["result"],
            "501 entries; 501 blobs; 0 gitlinks; 0 symlinks",
        )
        self.assertTrue(all(run["passed"] for run in runs))

    def test_06_reproducibility_and_rollback_boundaries_are_explicit(self):
        reproduction = self.record["reproducibility"]
        rollback = self.record["rollback_and_correction"]
        self.assertTrue(reproduction["detached_head_confirmed"])
        self.assertTrue(reproduction["working_tree_clean_before_and_after"])
        self.assertEqual(reproduction["tagged_tree_blob_count"], 501)
        self.assertEqual(reproduction["tagged_tree_gitlink_count"], 0)
        self.assertFalse(reproduction["gitmodules_present"])
        self.assertFalse(reproduction["git_lfs_pointers_present"])
        self.assertFalse(reproduction["promisor_remote_configured"])
        self.assertFalse(reproduction["partial_clone_extension_configured"])
        self.assertFalse(reproduction["sparse_checkout_configured"])
        self.assertFalse(reproduction["unrecorded_repository_state_required"])
        self.assertFalse(rollback["tag_move_allowed"])
        self.assertFalse(rollback["tag_delete_allowed"])
        self.assertFalse(rollback["tag_recreate_allowed"])
        self.assertTrue(rollback["corrective_work_requires_successor_commit"])
        self.assertTrue(
            rollback["patch_release_required_when_release_level_correction_is_appropriate"]
        )

    def test_07_classifications_and_retrospective_coverage_are_complete(self):
        findings = self.record["findings"]
        self.assertEqual(
            {finding["finding_id"] for finding in findings},
            set(EXPECTED_FINDING_IDS),
        )
        counts = {classification: 0 for classification in CLASSIFICATIONS}
        for finding in findings:
            self.assertIn(finding["classification"], CLASSIFICATIONS)
            counts[finding["classification"]] += 1
        self.assertEqual(counts, self.record["classification_counts"])
        retrospective = self.record["retrospective"]
        self.assertEqual(
            {entry["area"] for entry in retrospective},
            set(RETROSPECTIVE_AREAS),
        )
        referenced = {
            finding_id
            for entry in retrospective
            for finding_id in entry["finding_ids"]
        }
        self.assertEqual(referenced, set(EXPECTED_FINDING_IDS))

    def test_08_schema_and_evaluator_reject_extra_authority_key(self):
        candidate = copy.deepcopy(self.record)
        candidate["m16_authorized"] = True
        with self.assertRaises(AssertionError):
            validate_schema(self.schema, candidate)
        result = evaluate_post_release_governance_review(candidate)
        self.assertIn("top-level-key-set-mismatch", result["validation_findings"])
        self.assertEqual(result["m16_planning_recommendation"], M16_REMAIN_BLOCKED)

    def test_09_invalid_tag_target_blocks_planning_recommendation(self):
        result = self.assert_mutation_fails_closed(
            lambda value: value["tag_release_binding"].__setitem__(
                "tag_ref_target_sha", "f" * 40
            )
        )
        self.assertIn("tag-target-mismatch", result["validation_findings"])

    def test_10_command_argv_and_result_mutations_fail_closed(self):
        command_index = 22
        mutations = (
            lambda value: value["verification_runs"][command_index].__setitem__(
                "logical_argv", ["echo", "not-git"]
            ),
            lambda value: value["verification_runs"][command_index].__setitem__(
                "result", "f" * 40
            ),
        )
        for index, mutation in enumerate(mutations):
            with self.subTest(index=index):
                self.assert_mutation_fails_closed(mutation)

    def test_11_mutable_github_receipts_are_pinned(self):
        mutations = (
            lambda value: value["publication_evidence_inventory"].__setitem__(
                "latest", False
            ),
            lambda value: value["publication_evidence_inventory"][
                "raw_release_api_response"
            ].__setitem__("sha256", "f" * 64),
            lambda value: value["completion_approval_evidence"][
                "human_approval_comment"
            ].__setitem__("body_sha256", "f" * 64),
        )
        for index, mutation in enumerate(mutations):
            with self.subTest(index=index):
                self.assert_mutation_fails_closed(mutation)

    def test_12_candidate_state_and_rollback_overclaims_fail_closed(self):
        mutations = (
            lambda value: value["repository_consistency"][
                "review_candidate_readme_observation"
            ].__setitem__("stale_prepublication_statement_present", True),
            lambda value: value["rollback_and_correction"].__setitem__(
                "tag_move_allowed", True
            ),
            lambda value: value["m16_planning_recommendation"].__setitem__(
                "m16_implementation_authorized", True
            ),
        )
        for index, mutation in enumerate(mutations):
            with self.subTest(index=index):
                self.assert_mutation_fails_closed(mutation)

    def test_13_authority_prose_and_reclassification_fail_closed(self):
        def mutate_prose(value):
            value["findings"][0]["summary"] = (
                "M16 implementation is authorized by this record."
            )

        def mutate_classification(value):
            value["findings"][0]["classification"] = "no action required"
            value["classification_counts"]["documentation drift"] = 0
            value["classification_counts"]["no action required"] = 8

        for mutation in (mutate_prose, mutate_classification):
            with self.subTest(mutation=mutation.__name__):
                self.assert_mutation_fails_closed(mutation)

    def test_14_evaluator_runtime_is_transparent_and_non_mutating(self):
        result = evaluate_post_release_governance_review(self.record)
        for key in (
            "file_io_performed",
            "git_inspection_performed",
            "github_access_performed",
            "network_access_performed",
            "subprocess_executed",
            "commands_executed",
            "external_artifact_digests_verified",
            "external_state_mutated",
            "tag_or_release_mutated",
            "issue_state_mutated",
            "m16_authorized",
        ):
            self.assertFalse(result[key], key)
        self.assertTrue(result["caller_data_only"])
        self.assertTrue(result["digests_calculated"])


if __name__ == "__main__":
    unittest.main()
