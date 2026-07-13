import ast
import builtins
import copy
import hashlib
import importlib
import json
import os
import runpy
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.m14_release_proof_linkage_evaluator import (  # noqa: E402
    EXPECTED_BUNDLE,
    EXPECTED_CHANGED_FILES,
    EXPECTED_OUTSTANDING_ORDER,
    EXPECTED_TRACKS,
    REQUIRED_ALLOWED_OUTPUTS,
    REQUIRED_BOUNDARY_STATEMENTS,
    REQUIRED_FORBIDDEN_OUTPUTS,
    evaluate_file,
    evaluate_m14_release_proof_linkage,
    load_fixture,
    validate_m14_release_proof_linkage,
)


SPECIMEN_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m14-release-proof-linkage-specimen.json"
)
READINESS_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m14-operational-readiness-fixtures.json"
)
EVALUATOR_PATH = ROOT / "runtime" / "m14_release_proof_linkage_evaluator.py"

SOURCE_EVALUATOR_MODULES = {
    "runtime.voice_generation_policy_evaluator",
    "runtime.public_issue_exfiltration_gate_evaluator",
    "runtime.moda_ai_risk_mapping_evaluator",
    "runtime.ai_authored_pr_provenance_evaluator",
    "runtime.skill_admission_evaluator",
    "runtime.m14_cross_control_authority_boundary_evaluator",
    "runtime.m14_operational_readiness_evaluator",
}

EXPECTED_RESULT_FIELDS = {
    "valid",
    "release_linkage_coverage_complete",
    "operational_readiness_bundle_present",
    "operational_readiness_bundle_integrity_valid",
    "source_track_linkage_valid",
    "source_artifact_integrity_valid",
    "authority_boundaries_preserved",
    "verification_manifest_complete",
    "external_state_confirmation_required",
    "outstanding_completion_items_valid",
    "release_proof_complete",
    "release_ready_for_review",
    "ready_for_future_readme_status_path",
    "ready_for_m14_completion_review",
    "release_approved",
    "released",
    "m14_complete",
    "findings",
    "outputs",
}


def load_json(path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


class M14ReleaseProofLinkageEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = EVALUATOR_PATH.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.readiness = load_json(READINESS_PATH)

    def setUp(self):
        self.specimen = load_json(SPECIMEN_PATH)

    def evaluate(self, specimen=None, repository_root=None):
        return evaluate_m14_release_proof_linkage(
            self.specimen if specimen is None else specimen,
            repository_root=repository_root,
        )

    def assert_valid(self, result):
        self.assertTrue(result["valid"], result["findings"])
        self.assertEqual(result["findings"], [])
        self.assertTrue(result["release_proof_complete"])
        self.assertTrue(result["release_ready_for_review"])
        self.assertTrue(result["ready_for_future_readme_status_path"])
        self.assertFalse(result["ready_for_m14_completion_review"])
        self.assertFalse(result["release_approved"])
        self.assertFalse(result["released"])
        self.assertFalse(result["m14_complete"])
        self.assertEqual(set(result), EXPECTED_RESULT_FIELDS)

    def assert_invalid(self, result, finding_fragment=None):
        self.assertFalse(result["valid"])
        self.assertFalse(result["release_proof_complete"])
        self.assertFalse(result["release_ready_for_review"])
        self.assertFalse(result["ready_for_future_readme_status_path"])
        self.assertFalse(result["ready_for_m14_completion_review"])
        self.assertFalse(result["release_approved"])
        self.assertFalse(result["released"])
        self.assertFalse(result["m14_complete"])
        self.assertTrue(result["findings"])
        self.assertIn("m14_release_proof_linkage_invalid", result["outputs"])
        if finding_fragment is not None:
            self.assertTrue(
                any(finding_fragment in finding for finding in result["findings"]),
                result["findings"],
            )

    def temporary_evidence_repository(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        paths = {
            entry["relative_path"] for entry in self.specimen["operational_readiness_bundle"]
        }
        paths.update(
            entry["relative_path"]
            for entry in self.readiness["source_artifact_manifest"]
        )
        for relative_path in paths:
            source = ROOT / relative_path
            target = root / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        return temporary, root

    def mutate_readiness_file(self, root, mutator):
        path = (
            root
            / "examples"
            / "public-integration-pack-pilot"
            / "m14-operational-readiness-fixtures.json"
        )
        payload = load_json(path)
        mutator(payload)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def test_01_valid_top_level_active_work_state(self):
        self.assertEqual(
            self.specimen["artifact_status"],
            "active_work_in_progress_not_released",
        )
        self.assertEqual(
            self.specimen["fixture_status"], "m14_active_work_not_complete"
        )
        self.assertEqual(
            self.specimen["m14_completion_status"], "active_work_not_complete"
        )
        self.assert_valid(self.evaluate())

    def test_02_exact_three_changed_file_scope(self):
        self.assertEqual(
            tuple(self.specimen["changed_file_scope"]), EXPECTED_CHANGED_FILES
        )
        self.assertEqual(len(self.specimen["changed_file_scope"]), 3)

    def test_03_correct_prior_release_baseline(self):
        self.assertEqual(self.specimen["prior_released_baseline"], "v0.12.0")
        self.assertEqual(
            self.specimen["prior_release_baseline"],
            {
                "release_tag": "v0.12.0",
                "status": "prior_released_baseline",
                "governance_role": "historical_release_baseline_only",
                "grants_current_release_authority": False,
            },
        )

    def test_04_v013_remains_future_only(self):
        future = self.specimen["future_release_tag_path"]
        self.assertEqual(future["target_tag"], "v0.13.0")
        self.assertEqual(future["state"], "future_tag_path_only")
        for field in (
            "released",
            "tag_created",
            "github_release_created",
            "release_notes_finalized",
            "release_notes_published",
        ):
            self.assertFalse(future[field])

    def test_05_correct_source_pr_references(self):
        self.assertEqual(
            self.specimen["release_evidence_packet"]["source_pr_references"],
            ["#202", "#204", "#205", "#206", "#208", "#210"],
        )
        self.assertEqual(
            self.specimen["external_state_review_inputs"]["source_prs"],
            ["#202", "#204", "#205", "#206", "#208", "#210", "#212"],
        )

    def test_06_exactly_six_source_tracks(self):
        tracks = self.specimen["source_track_linkage"]
        self.assertEqual(len(tracks), 6)
        self.assertEqual(
            [track["track_id"] for track in tracks], list(EXPECTED_TRACKS)
        )

    def test_07_pr_209_is_not_in_source_track_manifest(self):
        tracks = self.specimen["source_track_linkage"]
        self.assertNotIn("#209", [track["source_pr"] for track in tracks])
        self.assertNotIn(
            "#209", self.specimen["release_evidence_packet"]["source_pr_references"]
        )
        self.assertNotIn(
            "#209", self.specimen["external_state_review_inputs"]["source_prs"]
        )
        self.assertNotIn("#209", self.specimen["release_linkage_refs"].values())

    def test_08_operational_readiness_bundle_has_exactly_three_files(self):
        bundle = self.specimen["operational_readiness_bundle"]
        self.assertEqual(len(bundle), 3)
        self.assertEqual(
            [entry["relative_path"] for entry in bundle],
            [entry["relative_path"] for entry in EXPECTED_BUNDLE],
        )

    def test_09_all_readiness_bundle_files_exist(self):
        for entry in self.specimen["operational_readiness_bundle"]:
            with self.subTest(path=entry["relative_path"]):
                self.assertTrue((ROOT / entry["relative_path"]).is_file())

    def test_10_readiness_bundle_sha256_digests_match(self):
        for entry in self.specimen["operational_readiness_bundle"]:
            with self.subTest(path=entry["relative_path"]):
                digest = hashlib.sha256(
                    (ROOT / entry["relative_path"]).read_bytes()
                ).hexdigest()
                self.assertEqual(digest, entry["sha256"])

    def test_11_readiness_bundle_digest_mismatch_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["operational_readiness_bundle"][0]["sha256"] = "0" * 64
        self.assert_invalid(
            self.evaluate(specimen),
            "operational_readiness_bundle_field_invalid",
        )

    def test_12_readiness_bundle_path_substitution_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["operational_readiness_bundle"][1]["relative_path"] = (
            "runtime/voice_generation_policy_evaluator.py"
        )
        self.assert_invalid(
            self.evaluate(specimen),
            "operational_readiness_bundle_field_invalid",
        )

    def test_13_readiness_fixture_is_loaded_as_data_only(self):
        imported = {
            node.module
            for node in ast.walk(self.tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        self.assertNotIn(
            "runtime.m14_operational_readiness_evaluator", imported
        )
        real_import = builtins.__import__

        def guarded_import(name, *args, **kwargs):
            if name in SOURCE_EVALUATOR_MODULES:
                raise AssertionError(f"source evaluator import attempted: {name}")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=guarded_import):
            self.assert_valid(self.evaluate())

    def test_14_source_evaluators_are_not_imported_or_executed(self):
        before = set(sys.modules)
        self.assert_valid(self.evaluate())
        newly_loaded = set(sys.modules) - before
        self.assertTrue(SOURCE_EVALUATOR_MODULES.isdisjoint(newly_loaded))
        imports = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
        self.assertTrue(SOURCE_EVALUATOR_MODULES.isdisjoint(imports))

    def test_15_workflows_skills_and_models_are_not_executed(self):
        policy = self.specimen["source_artifact_verification"]
        self.assertFalse(policy["execute_workflows"])
        self.assertFalse(policy["execute_skills"])
        self.assertFalse(policy["execute_models"])
        self.assertFalse(self.specimen["workflows_executed_by_fixture"])
        forbidden_imports = {"subprocess", "runpy", "importlib"}
        imports = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        self.assertTrue(forbidden_imports.isdisjoint(imports))

    def test_16_evaluator_performs_no_network_access(self):
        forbidden_imports = {
            "socket",
            "urllib",
            "http",
            "requests",
            "ftplib",
            "github",
            "ghapi",
        }
        imports = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        self.assertTrue(forbidden_imports.isdisjoint(imports))

        blocked = AssertionError("external operation attempted")
        with (
            patch.object(socket, "create_connection", side_effect=blocked),
            patch.object(urllib.request, "urlopen", side_effect=blocked),
            patch.object(subprocess, "run", side_effect=blocked),
            patch.object(subprocess, "Popen", side_effect=blocked),
            patch.object(os, "system", side_effect=blocked),
            patch.object(runpy, "run_path", side_effect=blocked),
            patch.object(runpy, "run_module", side_effect=blocked),
            patch.object(importlib, "import_module", side_effect=blocked),
        ):
            self.assert_valid(self.evaluate())

    def test_17_source_track_linkage_agrees_with_readiness_fixture(self):
        for index, release_track in enumerate(
            self.specimen["source_track_linkage"]
        ):
            readiness_track = self.readiness["source_track_manifest"][index]
            self.assertEqual(release_track["track_id"], readiness_track["track_id"])
            self.assertEqual(release_track["source_pr"], readiness_track["source_pr"])
            self.assertEqual(
                release_track["component_role"], readiness_track["component_role"]
            )
            combined_paths = release_track["implementation_artifact_paths"] + [
                release_track["deterministic_test_path"]
            ]
            self.assertEqual(combined_paths, readiness_track["source_paths"])

    def test_18_source_artifact_paths_exist(self):
        for entry in self.readiness["source_artifact_manifest"]:
            with self.subTest(path=entry["relative_path"]):
                self.assertTrue((ROOT / entry["relative_path"]).is_file())

    def test_19_source_artifact_digests_match(self):
        for entry in self.readiness["source_artifact_manifest"]:
            with self.subTest(path=entry["relative_path"]):
                digest = hashlib.sha256(
                    (ROOT / entry["relative_path"]).read_bytes()
                ).hexdigest()
                self.assertEqual(digest, entry["sha256"])

    def test_20_all_retained_authority_owners_are_aaos(self):
        for track in self.specimen["source_track_linkage"]:
            self.assertEqual(track["retained_authority_owner"], "AAOS")
        for track in self.readiness["source_track_manifest"]:
            self.assertEqual(track["retained_authority_owner"], "AAOS")

    def test_21_all_sealing_owners_are_aaos(self):
        for track in self.specimen["source_track_linkage"]:
            self.assertEqual(track["decision_proof_sealing_owner"], "AAOS")
        for track in self.readiness["source_track_manifest"]:
            self.assertEqual(track["decision_proof_sealing_owner"], "AAOS")

    def test_22_verification_command_manifest_is_complete(self):
        manifest = self.specimen["verification_command_manifest"]
        self.assertEqual(
            [entry["command_id"] for entry in manifest],
            [
                "git_diff_check",
                "validate_release_proof_fixture_json",
                "compile_release_proof_evaluator",
                "compile_release_proof_tests",
                "run_merged_m14_targeted_tests",
                "run_operational_readiness_tests",
                "run_release_proof_linkage_tests",
                "confirm_changed_file_scope",
            ],
        )
        for entry in manifest:
            self.assertEqual(entry["expected_exit_code"], 0)
            self.assertTrue(entry["verification_scope"])
            self.assertTrue(entry["expected_result"])
            self.assertTrue(entry["evidence_recording_requirement"])

    def test_23_command_manifest_is_not_execution_evidence(self):
        self.assertFalse(self.specimen["verification_manifest_execution_claimed"])
        for entry in self.specimen["verification_command_manifest"]:
            self.assertFalse(entry["executed_by_release_proof_evaluator"])
        specimen = copy.deepcopy(self.specimen)
        specimen["verification_command_manifest"][0][
            "executed_by_release_proof_evaluator"
        ] = True
        self.assert_invalid(
            self.evaluate(specimen), "verification_command_execution_claimed"
        )

    def test_24_external_github_state_is_reviewer_confirmed(self):
        external = self.specimen["external_state_review_inputs"]
        self.assertEqual(
            external["verification_mode"], "reviewer_confirmed_external_state"
        )
        self.assertFalse(external["verified_by_deterministic_evaluator"])
        self.assertTrue(external["reviewer_confirmation_required"])

    def test_25_release_proof_complete_is_true(self):
        self.assertTrue(self.evaluate()["release_proof_complete"])

    def test_26_release_ready_for_review_is_true(self):
        self.assertTrue(self.evaluate()["release_ready_for_review"])

    def test_27_ready_for_future_readme_status_path_is_true(self):
        self.assertTrue(self.evaluate()["ready_for_future_readme_status_path"])

    def test_28_ready_for_m14_completion_review_is_false(self):
        self.assertFalse(self.evaluate()["ready_for_m14_completion_review"])

    def test_29_release_approved_is_false(self):
        self.assertFalse(self.evaluate()["release_approved"])

    def test_30_released_is_false(self):
        self.assertFalse(self.evaluate()["released"])

    def test_31_m14_complete_is_false(self):
        self.assertFalse(self.evaluate()["m14_complete"])

    def test_32_readme_remains_unchanged_by_fixture_state(self):
        self.assertFalse(self.specimen["readme_status_updated"])
        self.assertFalse(
            self.specimen["release_status_path"]["readme_status_updated"]
        )

    def test_33_tracker_expected_state_remains_open(self):
        self.assertEqual(self.specimen["tracker_issue"], "#201")
        self.assertEqual(self.specimen["tracker_issue_linkage"], "Refs #201")
        self.assertEqual(self.specimen["tracker_expected_state"], "open")
        self.assertFalse(self.specimen["tracker_state_changed_by_fixture"])

    def test_34_outstanding_items_are_exactly_the_four_required(self):
        self.assertEqual(
            tuple(
                item["item_id"]
                for item in self.specimen["outstanding_completion_items"]
            ),
            EXPECTED_OUTSTANDING_ORDER,
        )

    def test_35_outstanding_sequence_is_correct(self):
        items = self.specimen["outstanding_completion_items"]
        for index, item in enumerate(items, start=1):
            self.assertEqual(item["status"], "pending")
            self.assertEqual(item["sequence_order"], index)
            self.assertTrue(item["not_performed_by_this_pr"])
            expected_prerequisite = (
                "m14_release_proof_linkage_valid"
                if index == 1
                else items[index - 2]["item_id"]
            )
            self.assertEqual(item["prerequisite"], expected_prerequisite)

    def test_36_release_approval_claim_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["release_approved"] = True
        self.assert_invalid(self.evaluate(specimen), "release_approved")

    def test_37_tag_creation_claim_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["release_tag_created"] = True
        self.assert_invalid(self.evaluate(specimen), "release_tag_created")

    def test_38_github_release_creation_claim_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["github_release_created"] = True
        self.assert_invalid(self.evaluate(specimen), "github_release_created")

    def test_39_release_note_publication_claim_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["release_notes_published"] = True
        self.assert_invalid(self.evaluate(specimen), "release_notes_published")

    def test_40_v013_release_claim_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["released"] = True
        specimen["future_release_tag_path"]["released"] = True
        self.assert_invalid(self.evaluate(specimen), "released")

    def test_41_m14_completion_claim_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["m14_complete"] = True
        self.assert_invalid(self.evaluate(specimen), "m14_complete")

    def test_42_risk_acceptance_claim_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["risk_accepted_by_fixture"] = True
        self.assert_invalid(self.evaluate(specimen), "risk_accepted_by_fixture")

    def test_43_fail_closed_execution_claim_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["fail_closed_executed_by_fixture"] = True
        self.assert_invalid(
            self.evaluate(specimen), "fail_closed_executed_by_fixture"
        )

    def test_44_rollback_execution_claim_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["rollback_executed_by_fixture"] = True
        self.assert_invalid(
            self.evaluate(specimen), "rollback_executed_by_fixture"
        )

    def test_45_audit_closure_claim_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["audit_closed_by_fixture"] = True
        self.assert_invalid(self.evaluate(specimen), "audit_closed_by_fixture")

    def test_46_authority_transfer_claim_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["authority_transferred_by_fixture"] = True
        self.assert_invalid(
            self.evaluate(specimen), "authority_transferred_by_fixture"
        )

    def test_47_final_governance_judgment_claim_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["final_governance_judgment_made_by_fixture"] = True
        self.assert_invalid(
            self.evaluate(specimen),
            "final_governance_judgment_made_by_fixture",
        )

    def test_48_decision_proof_sealing_claim_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["decision_proof_sealed_by_fixture"] = True
        self.assert_invalid(
            self.evaluate(specimen), "decision_proof_sealed_by_fixture"
        )

    def test_49_explicit_negative_governance_evidence_remains_valid(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["active_governance_evidence"] = {
            "release_approved": False,
            "risk_accepted": 0,
            "decision_proof_sealed": None,
            "authority_transferred": "not_transferred",
            "audit_closed": "not_closed",
            "m14_complete": "active_work_not_complete",
        }
        self.assert_valid(self.evaluate(specimen))

    def test_50_arbitrary_not_prefix_disguise_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["active_governance_evidence"] = {
            "release_approved": "noteworthy_custom_state"
        }
        self.assert_invalid(self.evaluate(specimen), "release_approved")

    def test_51_unknown_affirmative_value_under_forbidden_key_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["active_governance_evidence"] = {
            "release_approved": "awaiting_council"
        }
        self.assert_invalid(self.evaluate(specimen), "release_approved")

    def test_52_structured_affirmative_authority_state_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["active_governance_evidence"] = {
            "release_approved": {"status": "approved"}
        }
        self.assert_invalid(self.evaluate(specimen), "release_approved")

    def test_53_structured_negative_state_with_neutral_metadata_remains_valid(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["active_governance_evidence"] = {
            "release_approved": {
                "status": "not_approved",
                "reason": "reviewer_confirmation_pending",
                "evidence_id": "neutral-metadata",
                "trace_available": True,
                "attempts": 1,
            }
        }
        self.assert_valid(self.evaluate(specimen))

    def test_54_negative_outer_state_does_not_hide_nested_affirmative_claim(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["active_governance_evidence"] = {
            "release_approved": {
                "status": "not_approved",
                "nested": {"decision": "approved"},
            }
        }
        self.assert_invalid(self.evaluate(specimen), "release_approved")

    def test_55_exact_forbidden_token_used_as_value_fails(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["active_governance_evidence"] = {
            "neutral_output": "release_approved"
        }
        self.assert_invalid(
            self.evaluate(specimen), "forbidden_output_token_used_as_value"
        )

    def test_56_required_boundary_statements_are_complete(self):
        self.assertEqual(
            tuple(self.specimen["required_boundary_statements"]),
            REQUIRED_BOUNDARY_STATEMENTS,
        )
        self.assertEqual(
            set(self.specimen["semantic_boundaries"].values()),
            set(REQUIRED_BOUNDARY_STATEMENTS),
        )

    def test_57_allowed_and_forbidden_output_catalogs_are_complete_and_disjoint(self):
        allowed = set(self.specimen["allowed_evaluator_outputs"])
        forbidden = set(self.specimen["forbidden_evaluator_outputs"])
        self.assertEqual(allowed, REQUIRED_ALLOWED_OUTPUTS)
        self.assertEqual(forbidden, REQUIRED_FORBIDDEN_OUTPUTS)
        self.assertTrue(allowed.isdisjoint(forbidden))
        result = self.evaluate()
        self.assertTrue(set(result["outputs"]) <= allowed)
        self.assertTrue(set(result["outputs"]).isdisjoint(forbidden))

    def test_58_public_evaluator_apis_return_valid_baseline(self):
        loaded = load_fixture(SPECIMEN_PATH)
        results = (
            evaluate_m14_release_proof_linkage(loaded),
            validate_m14_release_proof_linkage(loaded),
            evaluate_file(SPECIMEN_PATH),
        )
        for result in results:
            with self.subTest(api=result):
                self.assert_valid(result)

    def test_59_release_proof_cases_have_exact_numbered_coverage(self):
        cases = self.specimen["release_proof_cases"]
        self.assertEqual(len(cases), 42)
        self.assertEqual(len({case["case_id"] for case in cases}), 42)
        for number, case in enumerate(cases, start=1):
            self.assertTrue(case["case_id"].startswith(f"case_{number:02d}_"))

    def test_60_missing_operational_readiness_fixture_blocks_linkage(self):
        temporary, root = self.temporary_evidence_repository()
        self.addCleanup(temporary.cleanup)
        (root / EXPECTED_BUNDLE[0]["relative_path"]).unlink()
        result = self.evaluate(repository_root=root)
        self.assert_invalid(result, "operational_readiness_bundle_file_missing")
        self.assertFalse(result["operational_readiness_bundle_present"])

    def test_61_missing_readiness_evaluator_source_blocks_linkage(self):
        temporary, root = self.temporary_evidence_repository()
        self.addCleanup(temporary.cleanup)
        (root / EXPECTED_BUNDLE[1]["relative_path"]).unlink()
        result = self.evaluate(repository_root=root)
        self.assert_invalid(result, "operational_readiness_bundle_file_missing")
        self.assertFalse(result["operational_readiness_bundle_present"])

    def test_62_missing_readiness_test_source_blocks_linkage(self):
        temporary, root = self.temporary_evidence_repository()
        self.addCleanup(temporary.cleanup)
        (root / EXPECTED_BUNDLE[2]["relative_path"]).unlink()
        result = self.evaluate(repository_root=root)
        self.assert_invalid(result, "operational_readiness_bundle_file_missing")
        self.assertFalse(result["operational_readiness_bundle_present"])

    def test_63_missing_source_track_blocks_linkage(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["source_track_linkage"].pop()
        self.assert_invalid(self.evaluate(specimen), "source_track_linkage_count_invalid")

    def test_64_unexpected_seventh_source_track_blocks_linkage(self):
        specimen = copy.deepcopy(self.specimen)
        extra = copy.deepcopy(specimen["source_track_linkage"][0])
        extra["track_id"] = "unexpected_track"
        extra["source_pr"] = "#999"
        specimen["source_track_linkage"].append(extra)
        self.assert_invalid(self.evaluate(specimen), "source_track_linkage_count_invalid")

    def test_65_source_pr_mismatch_blocks_linkage(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["source_track_linkage"][0]["source_pr"] = "#999"
        self.assert_invalid(self.evaluate(specimen), "source_track_linkage_mismatch")

    def test_66_source_artifact_missing_blocks_linkage(self):
        temporary, root = self.temporary_evidence_repository()
        self.addCleanup(temporary.cleanup)
        relative_path = self.readiness["source_artifact_manifest"][0]["relative_path"]
        (root / relative_path).unlink()
        result = self.evaluate(repository_root=root)
        self.assert_invalid(result, "source_artifact_file_missing")
        self.assertFalse(result["source_artifact_integrity_valid"])

    def test_67_source_artifact_digest_drift_blocks_linkage(self):
        temporary, root = self.temporary_evidence_repository()
        self.addCleanup(temporary.cleanup)
        relative_path = self.readiness["source_artifact_manifest"][0]["relative_path"]
        with (root / relative_path).open("ab") as handle:
            handle.write(b"drift")
        result = self.evaluate(repository_root=root)
        self.assert_invalid(result, "source_artifact_digest_mismatch")
        self.assertFalse(result["source_artifact_integrity_valid"])

    def test_68_non_aaos_retained_authority_owner_blocks_linkage(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["source_track_linkage"][0]["retained_authority_owner"] = (
            "ExternalSystem"
        )
        self.assert_invalid(self.evaluate(specimen), "retained_authority_owner")

    def test_69_non_aaos_sealing_owner_blocks_linkage(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["source_track_linkage"][0]["decision_proof_sealing_owner"] = (
            "ExternalSystem"
        )
        self.assert_invalid(self.evaluate(specimen), "decision_proof_sealing_owner")

    def test_70_readiness_fixture_declaring_m14_complete_blocks_linkage(self):
        temporary, root = self.temporary_evidence_repository()
        self.addCleanup(temporary.cleanup)

        def mutate(payload):
            payload["m14_completion_status"] = "complete"
            payload["expected_baseline_result"]["m14_complete"] = True

        self.mutate_readiness_file(root, mutate)
        self.assert_invalid(
            self.evaluate(repository_root=root), "readiness_state_invalid"
        )

    def test_71_readiness_fixture_marking_v013_released_blocks_linkage(self):
        temporary, root = self.temporary_evidence_repository()
        self.addCleanup(temporary.cleanup)

        def mutate(payload):
            payload["future_release_tag_path"]["released"] = True

        self.mutate_readiness_file(root, mutate)
        self.assert_invalid(
            self.evaluate(repository_root=root), "readiness_future_release_state_invalid"
        )

    def test_72_readiness_tracker_state_not_open_blocks_linkage(self):
        temporary, root = self.temporary_evidence_repository()
        self.addCleanup(temporary.cleanup)

        def mutate(payload):
            payload["external_state_review_inputs"]["tracker_expected_state"] = (
                "completed"
            )

        self.mutate_readiness_file(root, mutate)
        self.assert_invalid(
            self.evaluate(repository_root=root), "readiness_external_state_invalid"
        )

    def test_73_external_state_machine_verified_claim_blocks_linkage(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["external_state_review_inputs"][
            "verified_by_deterministic_evaluator"
        ] = True
        self.assert_invalid(self.evaluate(specimen), "external_state_review_inputs_invalid")

    def test_74_release_notes_finalized_claim_blocks_linkage(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["release_notes_finalized"] = True
        self.assert_invalid(self.evaluate(specimen), "release_notes_finalized")

    def test_75_outstanding_item_sequence_violation_blocks_linkage(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["outstanding_completion_items"][3]["status"] = "completed"
        self.assert_invalid(self.evaluate(specimen), "outstanding_item_invalid")

    def test_76_readiness_source_artifact_executable_claim_blocks_linkage(self):
        temporary, root = self.temporary_evidence_repository()
        self.addCleanup(temporary.cleanup)

        def mutate(payload):
            payload["source_artifact_manifest"][0][
                "executable_by_readiness_evaluator"
            ] = True

        self.mutate_readiness_file(root, mutate)
        self.assert_invalid(
            self.evaluate(repository_root=root), "source_artifact_binding_invalid"
        )

    def test_77_readiness_source_track_path_mismatch_blocks_linkage(self):
        temporary, root = self.temporary_evidence_repository()
        self.addCleanup(temporary.cleanup)

        def mutate(payload):
            payload["source_track_manifest"][0]["source_paths"][0] = (
                "examples/substituted.json"
            )

        self.mutate_readiness_file(root, mutate)
        self.assert_invalid(
            self.evaluate(repository_root=root), "readiness_source_track_mismatch"
        )

    def test_78_bundle_source_pr_mismatch_blocks_linkage(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["operational_readiness_bundle"][0]["source_pr"] = "#999"
        self.assert_invalid(
            self.evaluate(specimen), "operational_readiness_bundle_field_invalid"
        )

    def test_79_release_evidence_packet_is_traceability_only(self):
        packet = self.specimen["release_evidence_packet"]
        self.assertEqual(packet["release_proof_linkage_status"], "complete_for_review")
        self.assertEqual(
            packet["governance_role"],
            "traceability_packet_only_not_release_approval",
        )
        self.assertTrue(packet["release_ready_for_review"])
        self.assertFalse(packet["release_approved"])
        self.assertFalse(packet["released"])
        self.assertFalse(packet["decision_proof_sealed"])

    def test_80_source_artifact_verification_policy_is_data_only(self):
        policy = self.specimen["source_artifact_verification"]
        self.assertEqual(policy["load_mode"], "data_only")
        for field in (
            "import_operational_readiness_evaluator",
            "execute_operational_readiness_tests",
            "execute_source_evaluators",
            "execute_workflows",
            "execute_skills",
            "execute_models",
            "perform_network_access",
            "execute_shell_commands_from_fixture",
        ):
            self.assertFalse(policy[field])

    def test_81_valid_result_matches_declared_baseline(self):
        result = self.evaluate()
        baseline = self.specimen["expected_baseline_result"]
        for field, expected in baseline.items():
            with self.subTest(field=field):
                self.assertEqual(result[field], expected)
        self.assertEqual(result["findings"], [])
        self.assertTrue(
            set(result["outputs"])
            <= set(self.specimen["allowed_evaluator_outputs"])
        )

    def test_82_affirmative_claim_cannot_hide_in_release_proof_cases(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["release_proof_cases"][0]["release_approved"] = True
        self.assert_invalid(self.evaluate(specimen), "release_approved")

    def test_83_affirmative_claim_cannot_hide_in_detector_policy(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["forbidden_claim_inspection_policy"]["release_approved"] = True
        self.assert_invalid(self.evaluate(specimen), "release_approved")

    def test_84_affirmative_claim_cannot_hide_in_command_manifest(self):
        specimen = copy.deepcopy(self.specimen)
        specimen["verification_command_manifest"][0]["release_approved"] = True
        self.assert_invalid(self.evaluate(specimen), "release_approved")


if __name__ == "__main__":
    unittest.main()
