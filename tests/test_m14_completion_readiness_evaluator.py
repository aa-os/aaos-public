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

from runtime.m14_completion_readiness_evaluator import (  # noqa: E402
    EXPECTED_BUNDLE,
    EXPECTED_CHANGED_FILES,
    EXPECTED_NEXT_PHASE_BLOCK,
    REQUIRED_ALLOWED_OUTPUTS,
    REQUIRED_BOUNDARY_STATEMENTS,
    REQUIRED_FORBIDDEN_OUTPUTS,
    evaluate_file,
    evaluate_m14_completion_readiness,
    load_fixture,
    validate_m14_completion_readiness,
)


FIXTURE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m14-completion-readiness-future-readme-path.json"
)
README_PATH = ROOT / "README.md"
EVALUATOR_PATH = ROOT / "runtime" / "m14_completion_readiness_evaluator.py"
RELEASE_PROOF_FIXTURE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m14-release-proof-linkage-specimen.json"
)

SOURCE_MODULES = {
    "runtime.voice_generation_policy_evaluator",
    "runtime.public_issue_exfiltration_gate_evaluator",
    "runtime.moda_ai_risk_mapping_evaluator",
    "runtime.ai_authored_pr_provenance_evaluator",
    "runtime.skill_admission_evaluator",
    "runtime.m14_cross_control_authority_boundary_evaluator",
    "runtime.m14_operational_readiness_evaluator",
    "runtime.m14_release_proof_linkage_evaluator",
    "tests.test_m14_release_proof_linkage_evaluator",
}

EXPECTED_RESULT_FIELDS = {
    "valid",
    "readme_present",
    "readme_prefix_integrity_valid",
    "readme_next_phase_valid",
    "released_versions_section_preserved",
    "current_status_section_preserved",
    "release_proof_bundle_present",
    "release_proof_bundle_integrity_valid",
    "release_proof_state_valid",
    "completion_evidence_coverage_complete",
    "authority_boundaries_preserved",
    "verification_manifest_complete",
    "external_state_confirmation_required",
    "outstanding_completion_items_valid",
    "completion_ready_for_review",
    "ready_for_final_m14_completion_review",
    "final_m14_completion_review_completed",
    "release_approved",
    "released",
    "m14_complete",
    "findings",
    "outputs",
}

REQUIRED_CASE_IDS = (
    "case_01_valid_completion_readiness_baseline",
    "case_02_readme_missing_blocks_readiness",
    "case_03_next_phase_heading_missing_blocks_readiness",
    "case_04_duplicate_next_phase_heading_blocks_readiness",
    "case_05_readme_immutable_prefix_digest_mismatch_blocks_readiness",
    "case_06_releases_section_modification_blocks_readiness",
    "case_07_current_status_section_modification_blocks_readiness",
    "case_08_v0_13_0_added_to_releases_blocks_readiness",
    "case_09_m14_declared_complete_in_current_status_blocks_readiness",
    "case_10_m14_completed_heading_in_current_status_blocks_readiness",
    "case_11_v0_13_0_described_as_released_blocks_readiness",
    "case_12_active_work_statement_missing_blocks_readiness",
    "case_13_tracker_open_statement_missing_blocks_readiness",
    "case_14_prior_baseline_statement_missing_blocks_readiness",
    "case_15_future_only_release_statement_missing_blocks_readiness",
    "case_16_pr_202_evidence_link_missing_blocks_readiness",
    "case_17_pr_204_evidence_link_missing_blocks_readiness",
    "case_18_pr_205_evidence_link_missing_blocks_readiness",
    "case_19_pr_206_evidence_link_missing_blocks_readiness",
    "case_20_pr_208_evidence_link_missing_blocks_readiness",
    "case_21_pr_210_evidence_link_missing_blocks_readiness",
    "case_22_pr_212_evidence_link_missing_blocks_readiness",
    "case_23_pr_213_evidence_link_missing_blocks_readiness",
    "case_24_release_proof_bundle_file_missing_blocks_readiness",
    "case_25_release_proof_bundle_digest_mismatch_blocks_readiness",
    "case_26_release_proof_bundle_path_substitution_blocks_readiness",
    "case_27_release_proof_fixture_incorrectly_declares_release_approval",
    "case_28_release_proof_fixture_incorrectly_declares_released",
    "case_29_release_proof_fixture_incorrectly_declares_m14_complete",
    "case_30_release_proof_fixture_incorrectly_changes_tracker_state",
    "case_31_release_proof_fixture_incorrectly_claims_decision_proof_sealing",
    "case_32_external_github_state_incorrectly_marked_machine_verified",
    "case_33_verification_command_manifest_incorrectly_treated_as_execution_evidence",
    "case_34_final_completion_review_incorrectly_marked_completed",
    "case_35_release_tag_creation_claim_blocks_readiness",
    "case_36_github_release_creation_claim_blocks_readiness",
    "case_37_release_note_publication_claim_blocks_readiness",
    "case_38_release_approval_claim_blocks_readiness",
    "case_39_risk_acceptance_claim_blocks_readiness",
    "case_40_fail_closed_execution_claim_blocks_readiness",
    "case_41_rollback_execution_claim_blocks_readiness",
    "case_42_audit_closure_claim_blocks_readiness",
    "case_43_authority_transfer_claim_blocks_readiness",
    "case_44_final_governance_judgment_claim_blocks_readiness",
    "case_45_decision_proof_sealing_claim_blocks_readiness",
    "case_46_outstanding_item_sequence_violation_blocks_readiness",
    "case_47_explicit_negative_governance_evidence_remains_valid",
    "case_48_arbitrary_not_prefix_disguise_is_rejected",
    "case_49_unknown_non_empty_value_under_forbidden_key_is_affirmative",
    "case_50_structured_affirmative_authority_state_is_rejected",
    "case_51_structured_negative_state_with_neutral_metadata_remains_valid",
    "case_52_negative_outer_state_does_not_hide_nested_affirmative_claim",
    "case_53_exact_forbidden_output_token_used_as_value_is_rejected",
    "case_54_valid_baseline_remains_m14_active_work",
    "case_55_valid_baseline_is_ready_for_final_completion_review",
    "case_56_valid_baseline_does_not_approve_release",
    "case_57_valid_baseline_does_not_release_v0_13_0",
    "case_58_valid_baseline_does_not_complete_m14",
)

EXPECTED_TOP_LEVEL = {
    "artifact_id": "m14-completion-readiness-future-readme-path",
    "artifact_name": "M14 Completion Readiness and Future v0.13.0 README Status Path",
    "artifact_scope": (
        "high_risk_runtime_policy_and_public_output_safety_"
        "completion_readiness_future_readme_path"
    ),
    "milestone": "M14",
    "artifact_status": "active_work_in_progress_not_released",
    "fixture_status": "m14_active_work_not_complete",
    "m14_completion_status": "active_work_not_complete",
    "tracker_issue": "#201",
    "tracker_issue_linkage": "Refs #201",
    "tracker_expected_state": "open",
    "prior_released_baseline": "v0.12.0",
    "introduced_after_release": "v0.12.0",
    "target_future_release": "v0.13.0",
    "release_proof_complete": True,
    "completion_ready_for_review": True,
    "ready_for_final_m14_completion_review": True,
    "final_m14_completion_review_completed": False,
    "readme_future_path_present": True,
    "readme_next_phase_changed_by_fixture": True,
    "released_versions_section_changed_by_fixture": False,
    "current_status_section_changed_by_fixture": False,
    "bootstrap_status_section_changed_by_fixture": False,
    "release_ready_for_review": True,
    "release_approved": False,
    "release_file_created": False,
    "release_tag_created": False,
    "github_release_created": False,
    "release_notes_finalized": False,
    "release_notes_published": False,
    "released": False,
    "m14_complete": False,
    "risk_accepted_by_fixture": False,
    "fail_closed_executed_by_fixture": False,
    "rollback_executed_by_fixture": False,
    "audit_closed_by_fixture": False,
    "authority_transferred_by_fixture": False,
    "final_governance_judgment_made_by_fixture": False,
    "decision_proof_sealed_by_fixture": False,
    "network_access_performed_by_fixture": False,
    "source_evaluators_executed_by_fixture": False,
    "workflows_executed_by_fixture": False,
    "verification_manifest_execution_claimed": False,
}


def load_json(path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class M14CompletionReadinessEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = EVALUATOR_PATH.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def setUp(self):
        self.fixture = load_json(FIXTURE_PATH)

    def evaluate(self, fixture=None, repository_root=None):
        return evaluate_m14_completion_readiness(
            self.fixture if fixture is None else fixture,
            repository_root=ROOT if repository_root is None else repository_root,
        )

    def assert_valid(self, result):
        self.assertTrue(result["valid"], result["findings"])
        self.assertEqual(result["findings"], [])
        self.assertTrue(result["readme_present"])
        self.assertTrue(result["readme_prefix_integrity_valid"])
        self.assertTrue(result["readme_next_phase_valid"])
        self.assertTrue(result["released_versions_section_preserved"])
        self.assertTrue(result["current_status_section_preserved"])
        self.assertTrue(result["release_proof_bundle_present"])
        self.assertTrue(result["release_proof_bundle_integrity_valid"])
        self.assertTrue(result["release_proof_state_valid"])
        self.assertTrue(result["completion_evidence_coverage_complete"])
        self.assertTrue(result["authority_boundaries_preserved"])
        self.assertTrue(result["verification_manifest_complete"])
        self.assertTrue(result["external_state_confirmation_required"])
        self.assertTrue(result["outstanding_completion_items_valid"])
        self.assertTrue(result["completion_ready_for_review"])
        self.assertTrue(result["ready_for_final_m14_completion_review"])
        self.assertFalse(result["final_m14_completion_review_completed"])
        self.assertFalse(result["release_approved"])
        self.assertFalse(result["released"])
        self.assertFalse(result["m14_complete"])
        self.assertEqual(set(result), EXPECTED_RESULT_FIELDS)
        self.assertTrue(set(result["outputs"]) <= set(REQUIRED_ALLOWED_OUTPUTS))
        self.assertTrue(set(result["outputs"]).isdisjoint(REQUIRED_FORBIDDEN_OUTPUTS))

    def assert_invalid(self, result, finding_fragment=None):
        self.assertFalse(result["valid"])
        self.assertFalse(result["completion_ready_for_review"])
        self.assertFalse(result["ready_for_final_m14_completion_review"])
        self.assertFalse(result["final_m14_completion_review_completed"])
        self.assertFalse(result["release_approved"])
        self.assertFalse(result["released"])
        self.assertFalse(result["m14_complete"])
        self.assertTrue(result["findings"])
        self.assertIn("m14_completion_readiness_invalid", result["outputs"])
        if finding_fragment is not None:
            self.assertTrue(
                any(finding_fragment in finding for finding in result["findings"]),
                result["findings"],
            )

    def temporary_repository(self, *, include_readme=True, skip_bundle_path=None):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        if include_readme:
            shutil.copyfile(README_PATH, root / "README.md")
        for entry in EXPECTED_BUNDLE:
            relative_path = entry["relative_path"]
            if relative_path == skip_bundle_path:
                continue
            source = ROOT / relative_path
            target = root / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        return temporary, root

    def evaluate_readme_mutation(self, old, new):
        temporary, root = self.temporary_repository()
        self.addCleanup(temporary.cleanup)
        readme_path = root / "README.md"
        text = readme_path.read_bytes().decode("utf-8")
        self.assertEqual(text.count(old), 1, old)
        readme_path.write_bytes(text.replace(old, new, 1).encode("utf-8"))
        return self.evaluate(repository_root=root)

    def evaluate_release_proof_mutation(self, mutator):
        temporary, root = self.temporary_repository()
        self.addCleanup(temporary.cleanup)
        path = root / EXPECTED_BUNDLE[0]["relative_path"]
        payload = load_json(path)
        mutator(payload)
        path.write_bytes(
            (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        )
        return self.evaluate(repository_root=root)

    # Required completion-readiness cases 1-58.

    def test_01_valid_completion_readiness_baseline(self):
        self.assert_valid(self.evaluate())

    def test_02_readme_missing_blocks_readiness(self):
        temporary, root = self.temporary_repository(include_readme=False)
        self.addCleanup(temporary.cleanup)
        result = self.evaluate(repository_root=root)
        self.assert_invalid(result, "readme")
        self.assertFalse(result["readme_present"])

    def test_03_next_phase_heading_missing_blocks_readiness(self):
        result = self.evaluate_readme_mutation("## Next Phase", "## Future Phase")
        self.assert_invalid(result, "next_phase")
        self.assertFalse(result["readme_next_phase_valid"])

    def test_04_duplicate_next_phase_heading_blocks_readiness(self):
        result = self.evaluate_readme_mutation(
            EXPECTED_NEXT_PHASE_BLOCK,
            EXPECTED_NEXT_PHASE_BLOCK + "\n## Next Phase\n",
        )
        self.assert_invalid(result, "next_phase")
        self.assertFalse(result["readme_next_phase_valid"])

    def test_05_readme_immutable_prefix_digest_mismatch_blocks_readiness(self):
        result = self.evaluate_readme_mutation("# AAOS", "# ABOS")
        self.assert_invalid(result, "prefix")
        self.assertFalse(result["readme_prefix_integrity_valid"])

    def test_06_releases_section_modification_blocks_readiness(self):
        result = self.evaluate_readme_mutation(
            "\n## Current Status",
            "\nRelease section mutation sentinel.\n\n## Current Status",
        )
        self.assert_invalid(result, "releases")
        self.assertFalse(result["released_versions_section_preserved"])

    def test_07_current_status_section_modification_blocks_readiness(self):
        result = self.evaluate_readme_mutation(
            "## Current Status\n\n",
            "## Current Status\n\nCurrent status mutation sentinel.\n\n",
        )
        self.assert_invalid(result, "current_status")
        self.assertFalse(result["current_status_section_preserved"])

    def test_08_v0_13_0_added_to_releases_blocks_readiness(self):
        result = self.evaluate_readme_mutation(
            "\n## Current Status",
            "\n- v0.13.0 — M14\n\n## Current Status",
        )
        self.assert_invalid(result, "releases")
        self.assertFalse(result["released_versions_section_preserved"])

    def test_09_m14_declared_complete_in_current_status_blocks_readiness(self):
        result = self.evaluate_readme_mutation(
            "## Current Status\n\n",
            "## Current Status\n\nM14 is complete.\n\n",
        )
        self.assert_invalid(result, "current_status")
        self.assertFalse(result["current_status_section_preserved"])

    def test_10_m14_completed_heading_in_current_status_blocks_readiness(self):
        result = self.evaluate_readme_mutation(
            "## Current Status\n\n",
            "## Current Status\n\nM14 completed:\n\n",
        )
        self.assert_invalid(result, "current_status")
        self.assertFalse(result["current_status_section_preserved"])

    def test_11_v0_13_0_described_as_released_blocks_readiness(self):
        result = self.evaluate_readme_mutation(
            "## Current Status\n\n",
            "## Current Status\n\nv0.13.0 is released.\n\n",
        )
        self.assert_invalid(result, "current_status")
        self.assertFalse(result["current_status_section_preserved"])

    def test_12_active_work_statement_missing_blocks_readiness(self):
        result = self.evaluate_readme_mutation(
            "  - M14 remains active work; final completion has not been declared.\n",
            "",
        )
        self.assert_invalid(result, "next_phase")

    def test_13_tracker_open_statement_missing_blocks_readiness(self):
        result = self.evaluate_readme_mutation("  - Tracker: #201 remains Open.\n", "")
        self.assert_invalid(result, "next_phase")

    def test_14_prior_baseline_statement_missing_blocks_readiness(self):
        result = self.evaluate_readme_mutation(
            "  - Prior released baseline: v0.12.0.\n", ""
        )
        self.assert_invalid(result, "next_phase")

    def test_15_future_only_release_statement_missing_blocks_readiness(self):
        result = self.evaluate_readme_mutation(
            "  - Future target release path: v0.13.0 remains future-only and is not listed in released versions.\n",
            "",
        )
        self.assert_invalid(result, "next_phase")

    def _assert_missing_evidence_link_blocks(self, line):
        result = self.evaluate_readme_mutation(line + "\n", "")
        self.assert_invalid(result, "next_phase")

    def test_16_202_evidence_link_missing_blocks_readiness(self):
        self._assert_missing_evidence_link_blocks(
            "    - #202 Governed Voice Runtime Policy Fixtures."
        )

    def test_17_204_evidence_link_missing_blocks_readiness(self):
        self._assert_missing_evidence_link_blocks(
            "    - #204 Public Issue Exfiltration Gate."
        )

    def test_18_205_evidence_link_missing_blocks_readiness(self):
        self._assert_missing_evidence_link_blocks(
            "    - #205 MODA AI Risk Framework Mapping."
        )

    def test_19_206_evidence_link_missing_blocks_readiness(self):
        self._assert_missing_evidence_link_blocks(
            "    - #206 AI-Authored PR Provenance and Reviewer Routing."
        )

    def test_20_208_evidence_link_missing_blocks_readiness(self):
        self._assert_missing_evidence_link_blocks(
            "    - #208 External Skill Admission Gate."
        )

    def test_21_210_evidence_link_missing_blocks_readiness(self):
        self._assert_missing_evidence_link_blocks(
            "    - #210 Cross-Control Authority-Boundary Regression Fixtures."
        )

    def test_22_212_evidence_link_missing_blocks_readiness(self):
        self._assert_missing_evidence_link_blocks(
            "    - #212 Operational Readiness Checklist."
        )

    def test_23_213_evidence_link_missing_blocks_readiness(self):
        self._assert_missing_evidence_link_blocks(
            "    - #213 Release Proof Linkage Specimen."
        )

    def test_24_release_proof_bundle_file_missing_blocks_readiness(self):
        missing = EXPECTED_BUNDLE[0]["relative_path"]
        temporary, root = self.temporary_repository(skip_bundle_path=missing)
        self.addCleanup(temporary.cleanup)
        result = self.evaluate(repository_root=root)
        self.assert_invalid(result, "bundle")
        self.assertFalse(result["release_proof_bundle_present"])

    def test_25_release_proof_bundle_digest_mismatch_blocks_readiness(self):
        temporary, root = self.temporary_repository()
        self.addCleanup(temporary.cleanup)
        path = root / EXPECTED_BUNDLE[1]["relative_path"]
        path.write_bytes(path.read_bytes() + b"\n")
        result = self.evaluate(repository_root=root)
        self.assert_invalid(result, "digest")
        self.assertFalse(result["release_proof_bundle_integrity_valid"])

    def test_26_release_proof_bundle_path_substitution_blocks_readiness(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["release_proof_bundle"][1]["relative_path"] = (
            "runtime/m14_operational_readiness_evaluator.py"
        )
        result = self.evaluate(fixture)
        self.assert_invalid(result, "bundle")
        self.assertFalse(result["release_proof_bundle_integrity_valid"])

    def test_27_release_proof_fixture_incorrectly_declares_release_approval(self):
        result = self.evaluate_release_proof_mutation(
            lambda payload: payload.__setitem__("release_approved", True)
        )
        self.assert_invalid(result, "release_proof")
        self.assertFalse(result["release_proof_state_valid"])

    def test_28_release_proof_fixture_incorrectly_declares_released(self):
        result = self.evaluate_release_proof_mutation(
            lambda payload: payload.__setitem__("released", True)
        )
        self.assert_invalid(result, "release_proof")
        self.assertFalse(result["release_proof_state_valid"])

    def test_29_release_proof_fixture_incorrectly_declares_m14_complete(self):
        result = self.evaluate_release_proof_mutation(
            lambda payload: payload.__setitem__("m14_complete", True)
        )
        self.assert_invalid(result, "release_proof")
        self.assertFalse(result["release_proof_state_valid"])

    def test_30_release_proof_fixture_incorrectly_changes_tracker_state(self):
        result = self.evaluate_release_proof_mutation(
            lambda payload: payload.__setitem__("tracker_expected_state", "closed")
        )
        self.assert_invalid(result, "release_proof")
        self.assertFalse(result["release_proof_state_valid"])

    def test_31_release_proof_fixture_incorrectly_claims_decision_proof_sealing(self):
        result = self.evaluate_release_proof_mutation(
            lambda payload: payload.__setitem__(
                "decision_proof_sealed_by_fixture", True
            )
        )
        self.assert_invalid(result, "release_proof")
        self.assertFalse(result["release_proof_state_valid"])

    def test_32_external_github_state_incorrectly_marked_machine_verified(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["external_state_review_inputs"][
            "verified_by_deterministic_evaluator"
        ] = True
        self.assert_invalid(self.evaluate(fixture), "external_state")

    def test_33_verification_manifest_incorrectly_treated_as_execution_evidence(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["verification_manifest_execution_claimed"] = True
        self.assert_invalid(self.evaluate(fixture), "verification")

    def test_34_final_completion_review_incorrectly_marked_completed(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["final_m14_completion_review_completed"] = True
        self.assert_invalid(self.evaluate(fixture), "final_m14_completion_review_completed")

    def _assert_top_level_claim_blocks(self, field):
        fixture = copy.deepcopy(self.fixture)
        fixture[field] = True
        self.assert_invalid(self.evaluate(fixture), field)

    def test_35_release_tag_creation_claim_blocks_readiness(self):
        self._assert_top_level_claim_blocks("release_tag_created")

    def test_36_github_release_creation_claim_blocks_readiness(self):
        self._assert_top_level_claim_blocks("github_release_created")

    def test_37_release_note_publication_claim_blocks_readiness(self):
        self._assert_top_level_claim_blocks("release_notes_published")

    def test_38_release_approval_claim_blocks_readiness(self):
        self._assert_top_level_claim_blocks("release_approved")

    def test_39_risk_acceptance_claim_blocks_readiness(self):
        self._assert_top_level_claim_blocks("risk_accepted_by_fixture")

    def test_40_fail_closed_execution_claim_blocks_readiness(self):
        self._assert_top_level_claim_blocks("fail_closed_executed_by_fixture")

    def test_41_rollback_execution_claim_blocks_readiness(self):
        self._assert_top_level_claim_blocks("rollback_executed_by_fixture")

    def test_42_audit_closure_claim_blocks_readiness(self):
        self._assert_top_level_claim_blocks("audit_closed_by_fixture")

    def test_43_authority_transfer_claim_blocks_readiness(self):
        self._assert_top_level_claim_blocks("authority_transferred_by_fixture")

    def test_44_final_governance_judgment_claim_blocks_readiness(self):
        self._assert_top_level_claim_blocks(
            "final_governance_judgment_made_by_fixture"
        )

    def test_45_decision_proof_sealing_claim_blocks_readiness(self):
        self._assert_top_level_claim_blocks("decision_proof_sealed_by_fixture")

    def test_46_outstanding_item_sequence_violation_blocks_readiness(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["outstanding_completion_items"][1]["prerequisite"] = (
            "m14_completion_readiness_valid"
        )
        result = self.evaluate(fixture)
        self.assert_invalid(result, "outstanding")
        self.assertFalse(result["outstanding_completion_items_valid"])

    def test_47_explicit_negative_governance_evidence_remains_valid(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["active_governance_evidence"] = {
            "release_approved": False,
            "risk_accepted": 0,
            "decision_proof_sealed": None,
            "authority_transferred": "not_transferred",
            "audit_closed": "not_closed",
            "m14_complete": "active_work_not_complete",
            "final_m14_completion_review_completed": "not_completed",
        }
        self.assert_valid(self.evaluate(fixture))

    def test_48_arbitrary_not_prefix_disguise_is_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["active_governance_evidence"] = {
            "release_approved": "noteworthy_custom_state"
        }
        self.assert_invalid(self.evaluate(fixture), "release_approved")

    def test_49_unknown_non_empty_value_under_forbidden_key_is_affirmative(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["active_governance_evidence"] = {
            "release_approved": "awaiting_council"
        }
        self.assert_invalid(self.evaluate(fixture), "release_approved")

    def test_50_structured_affirmative_authority_state_is_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["active_governance_evidence"] = {
            "release_approved": {"status": "approved"}
        }
        self.assert_invalid(self.evaluate(fixture), "release_approved")

    def test_51_structured_negative_state_with_neutral_metadata_remains_valid(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["active_governance_evidence"] = {
            "release_approved": {
                "status": "not_approved",
                "reason": "reviewer_confirmation_pending",
                "evidence_id": "neutral-metadata",
                "trace_available": True,
                "attempts": 1,
            }
        }
        self.assert_valid(self.evaluate(fixture))

    def test_52_negative_outer_state_does_not_hide_nested_affirmative_claim(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["active_governance_evidence"] = {
            "release_approved": {
                "status": "not_approved",
                "nested": {"decision": "approved"},
            }
        }
        self.assert_invalid(self.evaluate(fixture), "release_approved")

    def test_53_exact_forbidden_output_token_used_as_value_is_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["active_governance_evidence"] = {
            "neutral_output": "release_approved"
        }
        self.assert_invalid(
            self.evaluate(fixture), "forbidden_output_token_used_as_value"
        )

    def test_54_valid_baseline_remains_m14_active_work(self):
        result = self.evaluate()
        self.assert_valid(result)
        self.assertEqual(self.fixture["m14_completion_status"], "active_work_not_complete")
        self.assertFalse(result["m14_complete"])

    def test_55_valid_baseline_is_ready_for_final_completion_review(self):
        result = self.evaluate()
        self.assert_valid(result)
        self.assertTrue(result["ready_for_final_m14_completion_review"])
        self.assertFalse(result["final_m14_completion_review_completed"])

    def test_56_valid_baseline_does_not_approve_release(self):
        result = self.evaluate()
        self.assert_valid(result)
        self.assertFalse(result["release_approved"])

    def test_57_valid_baseline_does_not_release_v0_13_0(self):
        result = self.evaluate()
        self.assert_valid(result)
        self.assertFalse(result["released"])

    def test_58_valid_baseline_does_not_complete_m14(self):
        result = self.evaluate()
        self.assert_valid(result)
        self.assertFalse(result["m14_complete"])

    # Fixture, API, integrity, and deterministic-execution contracts.

    def test_59_required_top_level_contract_is_exact(self):
        for field, expected in EXPECTED_TOP_LEVEL.items():
            with self.subTest(field=field):
                self.assertEqual(self.fixture[field], expected)
        self.assertEqual(tuple(self.fixture["changed_file_scope"]), EXPECTED_CHANGED_FILES)
        self.assertNotIn("#209", json.dumps(self.fixture, sort_keys=True))

    def test_60_prior_and_future_release_boundaries_are_exact(self):
        self.assertEqual(
            self.fixture["prior_release_baseline"],
            {
                "release_tag": "v0.12.0",
                "status": "prior_released_baseline",
                "governance_role": "historical_release_baseline_only",
                "grants_current_release_authority": False,
            },
        )
        self.assertEqual(
            self.fixture["future_release_tag_path"],
            {
                "target_tag": "v0.13.0",
                "state": "future_tag_path_only",
                "released": False,
                "tag_created": False,
                "github_release_created": False,
                "release_notes_finalized": False,
                "release_notes_published": False,
                "boundary": "Future release target is not released.",
            },
        )

    def test_61_readme_integrity_guard_matches_exact_main_prefix_bytes(self):
        guard = self.fixture["readme_integrity_guard"]
        self.assertEqual(guard["readme_path"], "README.md")
        self.assertEqual(guard["mutable_section_heading"], "## Next Phase")
        self.assertEqual(guard["mutable_section_occurrence_count"], 1)
        self.assertTrue(guard["immutable_prefix_ends_before_heading"])
        self.assertEqual(guard["allowed_modified_sections"], ["Next Phase"])
        self.assertEqual(
            guard["forbidden_modified_sections"],
            [
                "Bootstrap Status",
                "Releases",
                "Current Status",
                "M5 Additions",
                "M6 Additions",
                "M7 Additions",
                "M8 Additions",
                "M9 Additions",
                "M10 Additions",
                "M11 Additions",
                "M12 Additions",
                "M13 Additions",
            ],
        )
        readme = README_PATH.read_bytes()
        heading = b"## Next Phase"
        self.assertEqual(readme.count(heading), 1)
        prefix = readme[: readme.index(heading)]
        self.assertEqual(hashlib.sha256(prefix).hexdigest(), guard["immutable_prefix_sha256"])
        self.assertEqual(
            guard["immutable_prefix_sha256"],
            "07f45b06b56e8e52eb517a1f37bac47714ddc870d40707940962683405e72f63",
        )

    def test_62_complete_expected_next_phase_block_is_exact_and_terminal(self):
        expected = self.fixture["readme_expected_next_phase"]
        self.assertEqual(expected["heading"], "## Next Phase")
        self.assertEqual(expected["complete_expected_block"], EXPECTED_NEXT_PHASE_BLOCK)
        readme = README_PATH.read_bytes()
        offset = readme.index(b"## Next Phase")
        self.assertEqual(readme[offset:], EXPECTED_NEXT_PHASE_BLOCK.encode("utf-8"))
        self.assertTrue(readme.endswith(b"\n"))
        self.assertFalse(readme.endswith(b"\r\n"))

    def test_63_readme_release_and_current_status_sections_remain_prior_state(self):
        text = README_PATH.read_text(encoding="utf-8")
        releases = text.split("## Releases", 1)[1].split("## Current Status", 1)[0]
        current = text.split("## Current Status", 1)[1].split("\n## ", 1)[0]
        release_lines = [line for line in releases.splitlines() if line.startswith("- v")]
        self.assertTrue(release_lines[-1].startswith("- v0.12.0 "))
        self.assertNotIn("- v0.13.0", releases)
        self.assertIn(
            "M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11, M12, and M13 are complete.",
            current,
        )
        self.assertNotIn("M14 completed:", current)
        self.assertNotIn("M14 is complete", current)
        self.assertNotIn("v0.13.0 is released", current)

    def test_64_release_proof_bundle_has_exact_paths_and_main_digests(self):
        self.assertEqual(self.fixture["release_proof_bundle"], list(EXPECTED_BUNDLE))
        self.assertEqual(len(EXPECTED_BUNDLE), 3)
        for entry in EXPECTED_BUNDLE:
            with self.subTest(path=entry["relative_path"]):
                path = ROOT / entry["relative_path"]
                self.assertTrue(path.is_file())
                self.assertEqual(sha256(path), entry["sha256"])
                self.assertEqual(entry["source_pr"], "#213")
                self.assertTrue(entry["required"])
                self.assertEqual(entry["digest_algorithm"], "sha256")
                self.assertEqual(entry["observed_on_branch"], "main")
                self.assertFalse(
                    entry["executable_by_completion_readiness_evaluator"]
                )

    def test_65_release_proof_fixture_is_loaded_only_as_inert_json(self):
        imported = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        self.assertTrue(SOURCE_MODULES.isdisjoint(imported))

        real_import = builtins.__import__

        def guarded_import(name, *args, **kwargs):
            if name in SOURCE_MODULES:
                raise AssertionError(f"source module import attempted: {name}")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=guarded_import):
            self.assert_valid(self.evaluate())

    def test_66_evaluator_imports_no_network_or_execution_modules(self):
        forbidden_roots = {
            "socket",
            "urllib",
            "http",
            "requests",
            "ftplib",
            "github",
            "ghapi",
            "subprocess",
            "runpy",
            "importlib",
        }
        imported_roots = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".")[0])
        self.assertTrue(forbidden_roots.isdisjoint(imported_roots))

    def test_67_evaluator_performs_no_network_command_or_dynamic_execution(self):
        blocked = AssertionError("external or executable operation attempted")
        before = set(sys.modules)
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
        self.assertTrue(SOURCE_MODULES.isdisjoint(set(sys.modules) - before))

    def test_68_release_proof_state_validation_contract_is_exact(self):
        proof = load_json(RELEASE_PROOF_FIXTURE_PATH)
        expected = {
            "fixture_status": "m14_active_work_not_complete",
            "tracker_issue": "#201",
            "tracker_expected_state": "open",
            "target_future_release": "v0.13.0",
            "release_proof_complete": True,
            "release_ready_for_review": True,
            "ready_for_future_readme_status_path": True,
            "ready_for_m14_completion_review": False,
            "release_approved": False,
            "released": False,
            "m14_complete": False,
            "release_tag_created": False,
            "github_release_created": False,
            "decision_proof_sealed_by_fixture": False,
        }
        for field, value in expected.items():
            with self.subTest(field=field):
                self.assertEqual(proof[field], value)
        self.assertEqual(proof["authority_boundary"]["retained_authority_owner"], "AAOS")
        self.assertEqual(
            proof["authority_boundary"]["decision_proof_sealing_statement"],
            "Decision Proof sealing remains AAOS-owned.",
        )

    def test_69_completion_evidence_packet_covers_all_required_source_prs(self):
        packet = self.fixture["completion_evidence_packet"]
        self.assertEqual(
            packet["source_pr_references"],
            ["#202", "#204", "#205", "#206", "#208", "#210", "#212", "#213"],
        )
        self.assertNotIn("#209", packet["source_pr_references"])
        self.assertEqual(packet["release_proof_pr"], "#213")
        self.assertEqual(packet["readme_path"], "README.md")
        self.assertEqual(packet["readme_section"], "Next Phase")
        self.assertEqual(packet["readme_prefix_integrity_status"], "valid")
        self.assertEqual(packet["readme_future_path_status"], "present_future_only")
        self.assertEqual(packet["released_versions_section_status"], "unchanged")
        self.assertEqual(packet["current_status_section_status"], "unchanged")
        self.assertEqual(packet["release_proof_status"], "complete_for_review")
        self.assertEqual(packet["completion_readiness_status"], "ready_for_final_review")
        self.assertFalse(packet["final_completion_review_completed"])
        self.assertFalse(packet["release_approved"])
        self.assertFalse(packet["released"])
        self.assertFalse(packet["m14_complete"])
        self.assertFalse(packet["decision_proof_sealed"])

    def test_70_external_state_is_explicitly_reviewer_confirmed_only(self):
        external = self.fixture["external_state_review_inputs"]
        self.assertEqual(external["tracker_issue"], "#201")
        self.assertEqual(external["tracker_expected_state"], "open")
        self.assertEqual(
            external["source_prs"],
            ["#202", "#204", "#205", "#206", "#208", "#210", "#212", "#213"],
        )
        self.assertNotIn("#209", external["source_prs"])
        self.assertEqual(external["source_pr_expected_state"], "merged")
        self.assertEqual(
            external["verification_mode"], "reviewer_confirmed_external_state"
        )
        self.assertFalse(external["verified_by_deterministic_evaluator"])
        self.assertTrue(external["reviewer_confirmation_required"])

    def test_71_outstanding_items_are_exactly_pending_and_ordered(self):
        items = self.fixture["outstanding_completion_items"]
        self.assertEqual(
            [item["item_id"] for item in items],
            [
                "final_m14_completion_review",
                "tracker_issue_201_final_state_transition",
                "publish_v0_13_0_release",
            ],
        )
        self.assertEqual(
            [item["prerequisite"] for item in items],
            [
                "m14_completion_readiness_valid",
                "final_m14_completion_review",
                "tracker_issue_201_final_state_transition",
            ],
        )
        for order, item in enumerate(items, start=1):
            self.assertEqual(item["status"], "pending")
            self.assertEqual(item["sequence_order"], order)
            self.assertTrue(item["authorized_actor"])
            self.assertTrue(item["completion_evidence_required"])
            self.assertTrue(item["not_performed_by_this_pr"])

    def test_72_verification_manifest_is_complete_and_non_executing(self):
        commands = self.fixture["verification_command_manifest"]
        required_ids = {
            "git_diff_check",
            "validate_completion_readiness_fixture_json",
            "compile_completion_readiness_evaluator",
            "compile_completion_readiness_tests",
            "run_all_merged_m14_targeted_tests",
            "run_release_proof_linkage_tests",
            "run_completion_readiness_tests",
            "confirm_changed_file_scope",
        }
        self.assertTrue(required_ids <= {entry["command_id"] for entry in commands})
        for entry in commands:
            self.assertTrue(entry["command"])
            self.assertTrue(entry["verification_scope"])
            self.assertEqual(entry["expected_exit_code"], 0)
            self.assertTrue(entry["expected_result"])
            self.assertTrue(entry["evidence_recording_requirement"])
            self.assertFalse(entry["executed_by_completion_readiness_evaluator"])

    def test_73_required_boundary_and_output_catalogs_are_exact_and_disjoint(self):
        self.assertEqual(
            tuple(self.fixture["required_boundary_statements"]),
            tuple(REQUIRED_BOUNDARY_STATEMENTS),
        )
        self.assertEqual(
            set(self.fixture["semantic_boundaries"].values()),
            set(REQUIRED_BOUNDARY_STATEMENTS),
        )
        allowed = set(self.fixture["allowed_evaluator_outputs"])
        forbidden = set(self.fixture["forbidden_evaluator_outputs"])
        self.assertEqual(allowed, set(REQUIRED_ALLOWED_OUTPUTS))
        self.assertEqual(forbidden, set(REQUIRED_FORBIDDEN_OUTPUTS))
        self.assertTrue(allowed.isdisjoint(forbidden))

    def test_74_forbidden_claim_inspection_policy_includes_completion_status(self):
        policy = self.fixture["forbidden_claim_inspection_policy"]
        self.assertTrue(
            policy["explicit_negative_evidence_requires_exact_normalized_match"]
        )
        self.assertFalse(policy["arbitrary_not_prefix_is_negative"])
        self.assertTrue(
            policy["unknown_non_empty_value_under_forbidden_key_is_affirmative"]
        )
        self.assertTrue(
            policy["negative_outer_state_does_not_suppress_nested_affirmative_claim"]
        )
        self.assertTrue(policy["neutral_metadata_is_not_authority_state"])
        self.assertEqual(
            policy["authority_state_fields"],
            [
                "status",
                "state",
                "result",
                "outcome",
                "decision",
                "approval_status",
                "execution_status",
                "release_status",
                "sealing_status",
                "authority_status",
                "completion_status",
            ],
        )

    def test_75_authority_boundary_retains_aaos_ownership(self):
        authority = self.fixture["authority_boundary"]
        self.assertEqual(authority["retained_authority_owner"], "AAOS")
        self.assertEqual(authority["decision_proof_sealing_owner"], "AAOS")
        self.assertEqual(
            authority["decision_proof_sealing_statement"],
            "Decision Proof sealing remains AAOS-owned.",
        )
        self.assertEqual(
            authority["sovereignty_statement"],
            "AAOS remains the decision sovereignty layer.",
        )

    def test_76_completion_readiness_cases_have_all_58_named_scenarios(self):
        cases = self.fixture["completion_readiness_cases"]
        ids = [case["case_id"] for case in cases]
        self.assertGreaterEqual(len(cases), 58)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(set(REQUIRED_CASE_IDS) <= set(ids))
        for case_id in REQUIRED_CASE_IDS:
            case = next(item for item in cases if item["case_id"] == case_id)
            self.assertTrue(case["description"])
            self.assertIn(case["expected_result"], {"valid", "invalid"})

    def test_77_expected_baseline_result_matches_public_result(self):
        result = self.evaluate()
        baseline = self.fixture["expected_baseline_result"]
        self.assertEqual(set(baseline), EXPECTED_RESULT_FIELDS)
        for field, expected in baseline.items():
            with self.subTest(field=field):
                self.assertEqual(result[field], expected)

    def test_78_all_public_evaluator_apis_return_the_valid_baseline(self):
        loaded = load_fixture(FIXTURE_PATH)
        results = (
            evaluate_m14_completion_readiness(loaded),
            validate_m14_completion_readiness(loaded),
            evaluate_file(FIXTURE_PATH),
        )
        for result in results:
            with self.subTest(api=result):
                self.assert_valid(result)

    def test_79_affirmative_claim_cannot_hide_in_cases_policy_or_manifest(self):
        locations = (
            ("case", lambda fixture: fixture["completion_readiness_cases"][0]),
            ("policy", lambda fixture: fixture["forbidden_claim_inspection_policy"]),
            ("manifest", lambda fixture: fixture["verification_command_manifest"][0]),
        )
        for label, select in locations:
            fixture = copy.deepcopy(self.fixture)
            select(fixture)["release_approved"] = True
            with self.subTest(location=label):
                self.assert_invalid(self.evaluate(fixture), "release_approved")

    def test_80_completion_status_is_recursively_inspected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["active_governance_evidence"] = {
            "release_approved": {
                "status": "not_approved",
                "nested": {"completion_status": "completed"},
            }
        }
        self.assert_invalid(self.evaluate(fixture), "release_approved")

    def test_81_nested_forbidden_token_cannot_hide_under_negative_outer_state(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["active_governance_evidence"] = {
            "release_approved": {
                "status": "not_approved",
                "nested": {"neutral_output": "release_approved"},
            }
        }
        self.assert_invalid(self.evaluate(fixture), "forbidden_output_token")

    def test_82_authority_may_cannot_add_release_approval(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["authority_boundary"]["may"].append("approve_release")
        self.assert_invalid(self.evaluate(fixture), "authority_boundary")

    def test_83_pending_outstanding_item_rejects_completed_state(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["outstanding_completion_items"][0]["completed"] = True
        self.assert_invalid(self.evaluate(fixture), "outstanding_item_unexpected_fields")

    def test_84_standalone_specialized_authority_states_are_recursively_inspected(self):
        for field, value in (
            ("authority_status", "transferred"),
            ("sealing_status", "sealed"),
            ("approval_status", "approved"),
            ("completion_status", "completed"),
        ):
            fixture = copy.deepcopy(self.fixture)
            fixture["active_governance_evidence"] = {field: value}
            with self.subTest(field=field):
                self.assert_invalid(self.evaluate(fixture), field)

    def test_85_required_case_ids_cannot_be_substituted(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["completion_readiness_cases"][0]["case_id"] = "case_01_unrelated"
        self.assert_invalid(self.evaluate(fixture), "completion_readiness_case_missing")

    def test_86_known_forbidden_authority_key_policy_cannot_be_emptied(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["forbidden_claim_inspection_policy"][
            "known_forbidden_authority_keys"
        ] = []
        self.assert_invalid(self.evaluate(fixture), "known_forbidden_authority_keys")

    def test_87_arbitrary_negative_vocabulary_cannot_be_added(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["forbidden_claim_inspection_policy"][
            "explicit_negative_normalized_vocabulary"
        ].append("noteworthy_custom_state")
        self.assert_invalid(self.evaluate(fixture), "explicit_negative_vocabulary")

    def test_88_neutral_metadata_policy_must_match_runtime_semantics(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["forbidden_claim_inspection_policy"]["neutral_metadata_fields"] = []
        self.assert_invalid(self.evaluate(fixture), "neutral_metadata_fields")

    def test_89_required_case_outcome_cannot_be_flipped(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["completion_readiness_cases"][0]["expected_result"] = "invalid"
        self.assert_invalid(self.evaluate(fixture), "expected_result_mismatch")

    def test_90_verification_manifest_rejects_contradictory_extra_state(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["verification_command_manifest"][0]["executed"] = True
        self.assert_invalid(self.evaluate(fixture), "verification_command_unexpected_fields")

    def test_91_malformed_required_sequences_fail_closed(self):
        mutations = (
            ("changed_file_scope", lambda fixture: fixture.__setitem__("changed_file_scope", None)),
            (
                "readme_required_statements",
                lambda fixture: fixture["readme_expected_next_phase"].__setitem__(
                    "required_statements", None
                ),
            ),
            (
                "source_pr_references",
                lambda fixture: fixture["completion_evidence_packet"].__setitem__(
                    "source_pr_references", None
                ),
            ),
            (
                "required_boundary_statements",
                lambda fixture: fixture.__setitem__("required_boundary_statements", None),
            ),
        )
        for label, mutate in mutations:
            fixture = copy.deepcopy(self.fixture)
            mutate(fixture)
            with self.subTest(label=label):
                self.assert_invalid(self.evaluate(fixture))


if __name__ == "__main__":
    unittest.main()
