"""Deterministic historical M14 completion-readiness evaluation.

Repository files and fixture content are treated as inert evidence.  This module
does not import or execute other M14 evaluators or tests, run manifest commands
or workflows, query GitHub, approve a release, complete M14, or seal Decision
Proof.  It validates the immutable pre-final-transition README snapshot and
leaves current README validation to the M14 final-completion evaluator.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from runtime.repository_artifact_digest import (
    RepositoryArtifactFileTypeError,
    RepositoryArtifactPathError,
    RepositoryArtifactTextError,
    canonicalize_utf8_repository_text,
    sha256_repository_file,
)


EXPECTED_CHANGED_FILES = (
    "README.md",
    (
        "examples/public-integration-pack-pilot/"
        "m14-completion-readiness-future-readme-path.json"
    ),
    "runtime/m14_completion_readiness_evaluator.py",
    "tests/test_m14_completion_readiness_evaluator.py",
)

# PR #214 validated README.md while that file still represented the
# pre-final M14 transition.  The maintained evaluator binds that historical
# evidence to an immutable repository snapshot so the current README can move
# forward under the final-completion evaluator without rewriting history.
HISTORICAL_README_SNAPSHOT_PATH = (
    "examples/public-integration-pack-pilot/"
    "m14-completion-readiness-readme-snapshot.md"
)
HISTORICAL_README_SNAPSHOT_SOURCE_COMMIT = (
    "a7b5cbc2026468dde3d937e9366a780894570548"
)
EXPECTED_HISTORICAL_README_SNAPSHOT_SHA256 = (
    "a72061d2614b107e9780d31070ccae4ad683596c4873c6d1dac6a77fdf01d269"
)
HISTORICAL_EVIDENCE_PHASE = "pre_final_m14_transition"
CURRENT_README_VALIDATION_OWNER = "m14_final_completion_evaluator"

EXPECTED_README_PREFIX_SHA256 = (
    "07f45b06b56e8e52eb517a1f37bac47714ddc870d40707940962683405e72f63"
)
EXPECTED_RELEASES_SECTION_SHA256 = (
    "f0e4d1f6b2a3074b229f14ace4ea10340f6488d334ea7095192f586d0751cd4a"
)
EXPECTED_CURRENT_STATUS_SECTION_SHA256 = (
    "722891472b3db3de80f18393211230a63e6f939ea240050ed29a92431d80ec19"
)

EXPECTED_NEXT_PHASE_BLOCK = """## Next Phase

- M14 — High-Risk Runtime Policy Gates and Public-Output Safety
  - M14 remains active work; final completion has not been declared.
  - Tracker: #201 remains Open.
  - Prior released baseline: v0.12.0.
  - Future target release path: v0.13.0 remains future-only and is not listed in released versions.
  - Future README status path: v0.13.0 / M14 remains future-only until final completion review and authorized publication.
  - Current M14 evidence links:
    - #202 Governed Voice Runtime Policy Fixtures.
    - #204 Public Issue Exfiltration Gate.
    - #205 MODA AI Risk Framework Mapping.
    - #206 AI-Authored PR Provenance and Reviewer Routing.
    - #208 External Skill Admission Gate.
    - #210 Cross-Control Authority-Boundary Regression Fixtures.
    - #212 Operational Readiness Checklist.
    - #213 Release Proof Linkage Specimen.
  - Completion readiness is not completion.
  - README future status path is not release publication.
  - README future status path is not M14 completion.
  - Release proof linkage is not release approval.
  - completion_ready_for_review is not m14_complete.
  - ready_for_final_m14_completion_review is not final completion review completed.
  - readme_future_path_present is not released.
  - evidence_complete is not Decision Proof sealing.
  - replay_ready is not Decision Proof sealing.
  - Decision Proof sealing remains AAOS-owned.
  - AAOS remains the decision sovereignty layer.
"""

REQUIRED_NEXT_PHASE_STATEMENTS = (
    "M14 — High-Risk Runtime Policy Gates and Public-Output Safety",
    "M14 remains active work; final completion has not been declared.",
    "Tracker: #201 remains Open.",
    "Prior released baseline: v0.12.0.",
    (
        "Future target release path: v0.13.0 remains future-only and is not "
        "listed in released versions."
    ),
    (
        "Future README status path: v0.13.0 / M14 remains future-only until "
        "final completion review and authorized publication."
    ),
    "Current M14 evidence links:",
    "#202 Governed Voice Runtime Policy Fixtures.",
    "#204 Public Issue Exfiltration Gate.",
    "#205 MODA AI Risk Framework Mapping.",
    "#206 AI-Authored PR Provenance and Reviewer Routing.",
    "#208 External Skill Admission Gate.",
    "#210 Cross-Control Authority-Boundary Regression Fixtures.",
    "#212 Operational Readiness Checklist.",
    "#213 Release Proof Linkage Specimen.",
    "Completion readiness is not completion.",
    "README future status path is not release publication.",
    "README future status path is not M14 completion.",
    "Release proof linkage is not release approval.",
    "completion_ready_for_review is not m14_complete.",
    (
        "ready_for_final_m14_completion_review is not final completion review "
        "completed."
    ),
    "readme_future_path_present is not released.",
    "evidence_complete is not Decision Proof sealing.",
    "replay_ready is not Decision Proof sealing.",
    "Decision Proof sealing remains AAOS-owned.",
    "AAOS remains the decision sovereignty layer.",
)

EXPECTED_BUNDLE = (
    {
        "source_pr": "#213",
        "relative_path": (
            "examples/public-integration-pack-pilot/"
            "m14-release-proof-linkage-specimen.json"
        ),
        "artifact_type": "fixture",
        "required": True,
        "sha256": "8f45d7cdd108132e5032874a14bf9a6fc3cf585bdf28b718cd73d5d20b3793a6",
        "digest_algorithm": "sha256",
        "observed_on_branch": "main",
        "evidence_role": "release_proof_fixture_data",
        "executable_by_completion_readiness_evaluator": False,
    },
    {
        "source_pr": "#213",
        "relative_path": "runtime/m14_release_proof_linkage_evaluator.py",
        "artifact_type": "runtime_evaluator",
        "required": True,
        "sha256": "7cef0132a578c1f091aa3a713468149fc756f7a4e5eab41bee9fc6c40940860f",
        "digest_algorithm": "sha256",
        "observed_on_branch": "main",
        "evidence_role": "release_proof_evaluator_source",
        "executable_by_completion_readiness_evaluator": False,
    },
    {
        "source_pr": "#213",
        "relative_path": "tests/test_m14_release_proof_linkage_evaluator.py",
        "artifact_type": "deterministic_test",
        "required": True,
        "sha256": "278dcd0dd1183c6ad55c96503a8f93b71bf7b62aa155ac0fa1f2229615b5c3fb",
        "digest_algorithm": "sha256",
        "observed_on_branch": "main",
        "evidence_role": "release_proof_test_source",
        "executable_by_completion_readiness_evaluator": False,
    },
)

# The fixture records the immutable PR #213 manifest values in EXPECTED_BUNDLE.
# Only repository files that changed after that historical phase belong here.
# Current-file integrity is checked against this maintained overlay without
# rewriting or loosely accepting the historical fixture digest.
EXPECTED_MAINTAINED_BUNDLE_SHA256_OVERRIDES: dict[str, str] = {
    "runtime/m14_release_proof_linkage_evaluator.py": (
        "a572fd9470ac2a852f576d6487d926374a5bb5a4a632f79d0a365b7c1c167098"
    ),
    "tests/test_m14_release_proof_linkage_evaluator.py": (
        "b992c29ff29656353d6d8b4586becc8fee86c4b4957e58f73fc06c410336a03d"
    ),
}

EXPECTED_SOURCE_PRS = ("#202", "#204", "#205", "#206", "#208", "#210", "#212", "#213")

EXPECTED_TOP_LEVEL = {
    "artifact_id": "m14-completion-readiness-future-readme-path",
    "artifact_name": "M14 Completion Readiness and Future v0.13.0 README Status Path",
    "artifact_scope": (
        "high_risk_runtime_policy_and_public_output_safety_completion_readiness_"
        "future_readme_path"
    ),
    "milestone": "M14",
    "artifact_status": "active_work_in_progress_not_released",
    "fixture_status": "m14_active_work_not_complete",
    "m14_completion_status": "active_work_not_complete",
    "tracker_issue": "#201",
    "tracker_issue_linkage": "Refs #201",
    "tracker_expected_state": "open",
    "related_voice_runtime_pr": "#202",
    "related_public_output_gate_pr": "#204",
    "related_moda_mapping_pr": "#205",
    "related_ai_pr_provenance_pr": "#206",
    "related_skill_admission_pr": "#208",
    "related_cross_control_regression_pr": "#210",
    "related_operational_readiness_pr": "#212",
    "related_release_proof_pr": "#213",
    "prior_released_baseline": "v0.12.0",
    "introduced_after_release": "v0.12.0",
    "target_future_release": "v0.13.0",
}

REQUIRED_TRUE_TOP_LEVEL = (
    "release_proof_complete",
    "completion_ready_for_review",
    "ready_for_final_m14_completion_review",
    "readme_future_path_present",
    "readme_next_phase_changed_by_fixture",
    "release_ready_for_review",
)

REQUIRED_FALSE_TOP_LEVEL = (
    "tracker_state_changed_by_fixture",
    "final_m14_completion_review_completed",
    "released_versions_section_changed_by_fixture",
    "current_status_section_changed_by_fixture",
    "bootstrap_status_section_changed_by_fixture",
    "release_approved",
    "release_file_created",
    "release_tag_created",
    "github_release_created",
    "release_notes_finalized",
    "release_notes_published",
    "released",
    "m14_complete",
    "risk_accepted_by_fixture",
    "fail_closed_executed_by_fixture",
    "rollback_executed_by_fixture",
    "audit_closed_by_fixture",
    "authority_transferred_by_fixture",
    "final_governance_judgment_made_by_fixture",
    "decision_proof_sealed_by_fixture",
    "network_access_performed_by_fixture",
    "source_evaluators_executed_by_fixture",
    "workflows_executed_by_fixture",
    "verification_manifest_execution_claimed",
    "shell_commands_from_fixture_executed",
)

EXPECTED_LINKAGE_REFS = {
    "tracker_issue": "#201",
    "voice_runtime_policy_pr": "#202",
    "public_output_exfiltration_gate_pr": "#204",
    "moda_risk_mapping_pr": "#205",
    "ai_pr_provenance_pr": "#206",
    "skill_admission_pr": "#208",
    "cross_control_authority_boundary_pr": "#210",
    "operational_readiness_pr": "#212",
    "release_proof_pr": "#213",
}

REQUIRED_BOUNDARY_STATEMENTS = (
    "Completion readiness is not completion.",
    "README future status path is not release publication.",
    "README future status path is not M14 completion.",
    "Release proof linkage is not release approval.",
    "release_proof_complete is not released.",
    "completion_ready_for_review is not m14_complete.",
    (
        "ready_for_final_m14_completion_review is not final completion review "
        "completed."
    ),
    "readme_future_path_present is not released.",
    "A README entry is descriptive evidence, not governance authority.",
    "A merged PR reference is not release approval.",
    "Artifact digest matching is not governance approval.",
    "A verification-command manifest is not proof that commands ran.",
    (
        "External GitHub state is reviewer-confirmed evidence, not machine-"
        "verified by this evaluator."
    ),
    "Future release target is not released.",
    "v0.13.0 is not released.",
    "M14 remains active work and not complete.",
    "Tracker #201 remains Open.",
    "Human-review requirement is not completed review.",
    "fail_closed_recommended is not fail_closed_executed.",
    "rollback_recommended is not rollback_executed.",
    "evidence_complete is not Decision Proof sealing.",
    "replay_ready is not Decision Proof sealing.",
    "Explicit negative governance evidence is not an affirmative authority claim.",
    "Decision Proof sealing remains AAOS-owned.",
    "AAOS remains the decision sovereignty layer.",
)

REQUIRED_ALLOWED_OUTPUTS = {
    "m14_completion_readiness_valid",
    "m14_completion_readiness_invalid",
    "completion_evidence_coverage_complete",
    "completion_evidence_coverage_incomplete",
    "readme_prefix_integrity_valid",
    "readme_prefix_integrity_invalid",
    "readme_future_path_present",
    "readme_future_path_invalid",
    "released_versions_section_preserved",
    "current_status_section_preserved",
    "release_proof_bundle_valid",
    "release_proof_bundle_invalid",
    "completion_ready_for_review",
    "ready_for_final_m14_completion_review",
    "external_state_confirmation_required",
    "review_required",
    "escalation_required",
    "fail_closed_recommended",
    "not_ready",
}

REQUIRED_FORBIDDEN_OUTPUTS = {
    "final_m14_completion_review_completed",
    "m14_completion_approved",
    "m14_complete",
    "release_approved",
    "release_created",
    "release_tag_created",
    "github_release_created",
    "release_notes_finalized",
    "release_notes_published",
    "v0_13_0_released",
    "release_published",
    "tracker_201_final_state_applied",
    "risk_accepted",
    "fail_closed_executed",
    "rollback_executed",
    "audit_closed",
    "waiver_granted",
    "decision_proof_verified",
    "decision_proof_sealed",
    "sealed_by_completion_readiness",
    "sealed_by_readme",
    "authority_transferred",
    "final_governance_judgment",
}

EXPECTED_COMMANDS = (
    ("git_diff_check", "git diff --check"),
    (
        "validate_completion_readiness_fixture_json",
        "python -m json.tool examples/public-integration-pack-pilot/"
        "m14-completion-readiness-future-readme-path.json",
    ),
    (
        "compile_completion_readiness_evaluator",
        "python -m py_compile runtime/m14_completion_readiness_evaluator.py",
    ),
    (
        "compile_completion_readiness_tests",
        "python -m py_compile tests/test_m14_completion_readiness_evaluator.py",
    ),
    (
        "run_all_merged_m14_targeted_tests",
        "python -X faulthandler -m unittest "
        "tests.test_voice_generation_policy_evaluator "
        "tests.test_public_issue_exfiltration_gate_evaluator "
        "tests.test_moda_ai_risk_mapping_evaluator "
        "tests.test_ai_authored_pr_provenance_evaluator "
        "tests.test_skill_admission_evaluator "
        "tests.test_m14_cross_control_authority_boundary_evaluator "
        "tests.test_m14_operational_readiness_evaluator "
        "tests.test_m14_release_proof_linkage_evaluator -v",
    ),
    (
        "run_release_proof_linkage_tests",
        "python -X faulthandler -m unittest "
        "tests.test_m14_release_proof_linkage_evaluator -v",
    ),
    (
        "run_completion_readiness_tests",
        "python -X faulthandler -m unittest "
        "tests.test_m14_completion_readiness_evaluator -v",
    ),
    ("confirm_changed_file_scope", "git diff --name-only"),
)

EXPECTED_OUTSTANDING = (
    ("final_m14_completion_review", 1, "m14_completion_readiness_valid"),
    (
        "tracker_issue_201_final_state_transition",
        2,
        "final_m14_completion_review",
    ),
    (
        "publish_v0_13_0_release",
        3,
        "tracker_issue_201_final_state_transition",
    ),
)
EXPECTED_OUTSTANDING_ORDER = tuple(item[0] for item in EXPECTED_OUTSTANDING)

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
    (
        "case_33_verification_command_manifest_incorrectly_treated_as_"
        "execution_evidence"
    ),
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
VALID_COMPLETION_READINESS_CASE_NUMBERS = {1, 47, 51, 54, 55, 56, 57, 58}
REQUIRED_CASE_EXPECTED_RESULTS = {
    case_id: "valid" if number in VALID_COMPLETION_READINESS_CASE_NUMBERS else "invalid"
    for number, case_id in enumerate(REQUIRED_CASE_IDS, start=1)
}

AUTHORITY_STATE_FIELD_ORDER = (
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
)
AUTHORITY_STATE_FIELDS = set(AUTHORITY_STATE_FIELD_ORDER)

SPECIALIZED_AUTHORITY_STATE_FIELDS = {
    "approval_status",
    "execution_status",
    "release_status",
    "sealing_status",
    "authority_status",
    "completion_status",
}

EXPLICIT_NEGATIVE_VOCABULARY = (
    False,
    0,
    None,
    "",
    "no",
    "none",
    "denied",
    "rejected",
    "blocked",
    "pending",
    "open",
    "unreleased",
    "not_accepted",
    "not_allowed",
    "not_approved",
    "not_authorized",
    "not_certified",
    "not_closed",
    "not_complete",
    "not_completed",
    "not_executed",
    "not_final",
    "not_granted",
    "not_published",
    "not_released",
    "not_sealed",
    "not_transferred",
    "not_verified",
    "active_work_not_complete",
)
EXPLICIT_NEGATIVE_STRINGS = {
    value for value in EXPLICIT_NEGATIVE_VOCABULARY if isinstance(value, str)
}

EXPECTED_POLICY_KNOWN_FORBIDDEN_AUTHORITY_KEYS = (
    "final_m14_completion_review_completed",
    "release_approved",
    "release_created",
    "release_file_created",
    "release_tag_created",
    "github_release_created",
    "release_notes_finalized",
    "release_notes_published",
    "released",
    "m14_complete",
    "risk_accepted_by_fixture",
    "fail_closed_executed_by_fixture",
    "rollback_executed_by_fixture",
    "audit_closed_by_fixture",
    "authority_transferred_by_fixture",
    "final_governance_judgment_made_by_fixture",
    "decision_proof_sealed_by_fixture",
    "verification_manifest_execution_claimed",
)

EXPECTED_POLICY_NEUTRAL_METADATA_FIELDS = (
    "description",
    "note",
    "rationale",
    "evidence_role",
    "verification_scope",
    "expected_result",
    "evidence_recording_requirement",
    "boundary",
    "governance_role",
    "prerequisite",
    "authorized_actor",
    "completion_evidence_required",
)

FORBIDDEN_AUTHORITY_KEYS = REQUIRED_FORBIDDEN_OUTPUTS | {
    "released",
    "final_completion_review_completed",
    "tag_created",
    "release_file_created",
    "tracker_state_changed_by_fixture",
    "released_versions_section_changed_by_fixture",
    "current_status_section_changed_by_fixture",
    "bootstrap_status_section_changed_by_fixture",
    "risk_accepted_by_fixture",
    "fail_closed_executed_by_fixture",
    "rollback_executed_by_fixture",
    "audit_closed_by_fixture",
    "authority_transferred_by_fixture",
    "final_governance_judgment_made_by_fixture",
    "decision_proof_sealed_by_fixture",
    "network_access_performed_by_fixture",
    "source_evaluators_executed_by_fixture",
    "workflows_executed_by_fixture",
    "verification_manifest_execution_claimed",
    "shell_commands_from_fixture_executed",
    "executed_by_completion_readiness_evaluator",
    "verified_by_deterministic_evaluator",
    "release_authority_granted",
    "grants_current_release_authority",
}

CLAIM_SCAN_SKIP_KEYS = {
    "forbidden_evaluator_outputs",
    "known_forbidden_authority_keys",
}

REQUIRED_AUTHORITY_MAY = {
    "describe_evidence",
    "reference_evidence",
    "read_repository_files",
    "load_release_proof_fixture_as_inert_json",
    "validate_readme_integrity",
    "validate_readme_release_state",
    "validate_paths",
    "inspect_inert_evidence",
    "validate_repository_state",
    "recompute_sha256_digests",
    "report_completion_readiness",
    "report_coverage",
    "preserve_traceability",
    "route_findings_for_review",
    "require_external_state_confirmation",
    "validate_verification_command_manifest",
    "validate_outstanding_completion_sequence",
}

REQUIRED_AUTHORITY_MUST_NOT = {
    "approve_release",
    "accept_risk",
    "execute_rollback",
    "execute_fail_closed",
    "finalize_release_notes",
    "publish_release_notes",
    "grant_waivers",
    "transfer_authority",
    "make_final_governance_judgments",
    "seal_decision_proof",
    "declare_m14_complete",
    "complete_final_m14_completion_review",
    "publish_v0_13_0",
    "create_release_files",
    "create_release_tag",
    "create_github_release",
    "change_tracker_state",
    "query_github",
    "import_source_evaluators",
    "execute_source_evaluators",
    "execute_source_tests",
    "execute_workflows",
    "execute_skills",
    "execute_models",
    "execute_external_runtimes",
    "perform_network_access",
    "execute_fixture_commands",
    "execute_shell_commands_derived_from_fixture_content",
    "declare_v0_13_0_released",
}

EXPECTED_BASELINE_RESULT = {
    "valid": True,
    "readme_present": True,
    "readme_prefix_integrity_valid": True,
    "readme_next_phase_valid": True,
    "released_versions_section_preserved": True,
    "current_status_section_preserved": True,
    "release_proof_bundle_present": True,
    "release_proof_bundle_integrity_valid": True,
    "release_proof_state_valid": True,
    "completion_evidence_coverage_complete": True,
    "authority_boundaries_preserved": True,
    "verification_manifest_complete": True,
    "external_state_confirmation_required": True,
    "outstanding_completion_items_valid": True,
    "completion_ready_for_review": True,
    "ready_for_final_m14_completion_review": True,
    "final_m14_completion_review_completed": False,
    "release_approved": False,
    "released": False,
    "m14_complete": False,
    "findings": [],
    "outputs": [
        "m14_completion_readiness_valid",
        "completion_evidence_coverage_complete",
        "readme_prefix_integrity_valid",
        "readme_future_path_present",
        "released_versions_section_preserved",
        "current_status_section_preserved",
        "release_proof_bundle_valid",
        "completion_ready_for_review",
        "ready_for_final_m14_completion_review",
        "external_state_confirmation_required",
        "review_required",
    ],
}


def _add(findings: list[str], finding: str) -> None:
    if finding not in findings:
        findings.append(finding)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_set(value: Any) -> set[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return set()
    return {item for item in value if isinstance(item, str)}


def _typed_sequence_equal(value: Any, expected: Sequence[Any]) -> bool:
    if not isinstance(value, list) or len(value) != len(expected):
        return False
    return all(
        type(actual) is type(expected_value) and actual == expected_value
        for actual, expected_value in zip(value, expected)
    )


def _ordered_string_sequence_equal(value: Any, expected: Sequence[str]) -> bool:
    if not isinstance(value, Sequence) or isinstance(
        value, (str, bytes, bytearray)
    ):
        return False
    return len(value) == len(expected) and all(
        isinstance(actual, str) and actual == expected_value
        for actual, expected_value in zip(value, expected)
    )


def _token(value: Any) -> str:
    text = str(value).strip().lower()
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_")


def _repository_root(repository_root: str | Path | None) -> Path:
    if repository_root is None:
        return Path(__file__).resolve().parents[1]
    return Path(repository_root).resolve()


def _safe_repository_path(root: Path, relative_path: Any) -> Path | None:
    if not isinstance(relative_path, str) or not relative_path or "\\" in relative_path:
        return None
    pure = PurePosixPath(relative_path)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        return None
    candidate = (root / Path(*pure.parts)).resolve()
    if candidate != root and root not in candidate.parents:
        return None
    return candidate


def _sha256_repository_text_bytes(value: bytes) -> str:
    """Hash canonical UTF-8 repository text already loaded for section checks."""

    return hashlib.sha256(canonicalize_utf8_repository_text(value)).hexdigest()


def load_fixture(path: str | Path) -> dict[str, Any]:
    """Load one UTF-8 JSON fixture as inert data."""

    with Path(path).open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("completion-readiness fixture must contain a JSON object")
    return payload


def _heading_positions(data: bytes, heading: str) -> list[int]:
    pattern = re.compile(rb"^" + re.escape(heading.encode("utf-8")) + rb"\r?$", re.MULTILINE)
    return [match.start() for match in pattern.finditer(data)]


def _level_two_sections(data: bytes) -> dict[str, bytes]:
    pattern = re.compile(rb"^## [^\r\n]+\r?$", re.MULTILINE)
    matches = list(pattern.finditer(data))
    sections: dict[str, bytes] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(data)
        try:
            heading = match.group().rstrip(b"\r").decode("utf-8")
        except UnicodeDecodeError:
            continue
        if heading not in sections:
            sections[heading] = data[match.start() : end]
    return sections


def _validate_top_level(payload: Mapping[str, Any], findings: list[str]) -> bool:
    valid = True
    for field, expected in EXPECTED_TOP_LEVEL.items():
        if payload.get(field) != expected:
            _add(findings, f"top_level_value_invalid:{field}")
            valid = False

    for field in REQUIRED_TRUE_TOP_LEVEL:
        if payload.get(field) is not True:
            _add(findings, f"top_level_review_state_invalid:{field}")
            valid = False
    for field in REQUIRED_FALSE_TOP_LEVEL:
        if payload.get(field) is not False:
            _add(findings, f"top_level_false_boundary_invalid:{field}")
            valid = False

    if not _ordered_string_sequence_equal(
        payload.get("changed_file_scope"), EXPECTED_CHANGED_FILES
    ):
        _add(findings, "changed_file_scope_invalid")
        valid = False

    prior = _as_mapping(payload.get("prior_release_baseline"))
    if prior != {
        "release_tag": "v0.12.0",
        "status": "prior_released_baseline",
        "governance_role": "historical_release_baseline_only",
        "grants_current_release_authority": False,
    }:
        _add(findings, "prior_release_baseline_invalid")
        valid = False

    future = _as_mapping(payload.get("future_release_tag_path"))
    if future != {
        "target_tag": "v0.13.0",
        "state": "future_tag_path_only",
        "released": False,
        "tag_created": False,
        "github_release_created": False,
        "release_notes_finalized": False,
        "release_notes_published": False,
        "boundary": "Future release target is not released.",
    }:
        _add(findings, "future_release_tag_path_invalid")
        valid = False

    required_containers = {
        "readme_integrity_guard": dict,
        "readme_expected_next_phase": dict,
        "readme_release_state_guards": dict,
        "release_linkage_refs": dict,
        "release_proof_bundle": list,
        "release_proof_state_validation": dict,
        "completion_evidence_packet": dict,
        "external_state_review_inputs": dict,
        "verification_command_manifest": list,
        "outstanding_completion_items": list,
        "completion_readiness_cases": list,
        "required_boundary_statements": list,
        "semantic_boundaries": dict,
        "allowed_evaluator_outputs": list,
        "forbidden_evaluator_outputs": list,
        "forbidden_claim_inspection_policy": dict,
        "authority_boundary": dict,
        "expected_baseline_result": dict,
    }
    for field, expected_type in required_containers.items():
        if not isinstance(payload.get(field), expected_type):
            _add(findings, f"container_type_invalid:{field}")
            valid = False
    return valid


def _validate_readme_configuration(
    payload: Mapping[str, Any], findings: list[str]
) -> bool:
    valid = True
    guard = _as_mapping(payload.get("readme_integrity_guard"))
    expected_guard = {
        "readme_path": "README.md",
        "mutable_section_heading": "## Next Phase",
        "mutable_section_occurrence_count": 1,
        "immutable_prefix_sha256": EXPECTED_README_PREFIX_SHA256,
        "immutable_prefix_ends_before_heading": True,
        "allowed_modified_sections": ["Next Phase"],
        "forbidden_modified_sections": [
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
    }
    if guard != expected_guard:
        _add(findings, "readme_integrity_guard_invalid")
        valid = False

    expected = _as_mapping(payload.get("readme_expected_next_phase"))
    if expected.get("heading") != "## Next Phase":
        _add(findings, "readme_expected_heading_invalid")
        valid = False
    if expected.get("complete_expected_block") != EXPECTED_NEXT_PHASE_BLOCK:
        _add(findings, "readme_expected_block_invalid")
        valid = False
    if not _ordered_string_sequence_equal(
        expected.get("required_statements"), REQUIRED_NEXT_PHASE_STATEMENTS
    ):
        _add(findings, "readme_expected_statements_invalid")
        valid = False

    release_guards = _as_mapping(payload.get("readme_release_state_guards"))
    releases = _as_mapping(release_guards.get("releases_section"))
    if releases != {
        "start_heading": "## Releases",
        "end_heading": "## Current Status",
        "latest_released_version": "v0.12.0",
        "forbidden_released_version": "v0.13.0",
        "section_changed_by_fixture": False,
    }:
        _add(findings, "readme_releases_guard_invalid")
        valid = False

    current = _as_mapping(release_guards.get("current_status_section"))
    if current != {
        "start_heading": "## Current Status",
        "end_at_next_level_two_heading": True,
        "completed_milestones": [f"M{number}" for number in range(1, 14)],
        "forbidden_completion_milestone": "M14",
        "forbidden_heading": "M14 completed:",
        "forbidden_released_version": "v0.13.0",
        "section_changed_by_fixture": False,
    }:
        _add(findings, "readme_current_status_guard_invalid")
        valid = False

    next_phase = _as_mapping(release_guards.get("next_phase_section"))
    if next_phase != {
        "required_state": "active_work",
        "tracker_state": "open",
        "prior_released_baseline": "v0.12.0",
        "target_future_release": "v0.13.0",
        "target_release_state": "future_only",
        "required_evidence_prs": list(EXPECTED_SOURCE_PRS),
    }:
        _add(findings, "readme_next_phase_guard_invalid")
        valid = False
    return valid


def _validate_historical_readme_snapshot(
    payload: Mapping[str, Any], root: Path, findings: list[str]
) -> tuple[bool, bool, bool, bool, bool, bool]:
    configuration_valid = _validate_readme_configuration(payload, findings)
    path = _safe_repository_path(root, HISTORICAL_README_SNAPSHOT_PATH)
    present = path is not None and path.is_file()

    try:
        observed_digest = sha256_repository_file(
            root,
            HISTORICAL_README_SNAPSHOT_PATH,
            mode="text",
        )
    except RepositoryArtifactPathError:
        _add(findings, "historical_readme_snapshot_path_invalid")
        return False, False, False, False, False, False
    except FileNotFoundError:
        _add(findings, "historical_readme_snapshot_missing")
        return False, False, False, False, False, False
    except RepositoryArtifactFileTypeError:
        _add(findings, "historical_readme_snapshot_not_regular")
        return False, False, False, False, False, False
    except UnicodeDecodeError:
        _add(findings, "historical_readme_snapshot_malformed_utf8")
        return present, False, False, False, False, False
    except RepositoryArtifactTextError:
        _add(findings, "historical_readme_snapshot_lone_cr")
        return present, False, False, False, False, False
    except OSError:
        _add(findings, "historical_readme_snapshot_unreadable")
        return present, False, False, False, False, False

    snapshot_integrity_valid = (
        observed_digest == EXPECTED_HISTORICAL_README_SNAPSHOT_SHA256
    )
    if not snapshot_integrity_valid:
        _add(findings, "historical_readme_snapshot_digest_mismatch")

    try:
        assert path is not None
        data = canonicalize_utf8_repository_text(path.read_bytes())
    except UnicodeDecodeError:
        _add(findings, "historical_readme_snapshot_malformed_utf8")
        return present, False, False, False, False, False
    except RepositoryArtifactTextError:
        _add(findings, "historical_readme_snapshot_lone_cr")
        return present, False, False, False, False, False
    except OSError:
        _add(findings, "historical_readme_snapshot_unreadable")
        return present, False, False, False, False, False

    next_positions = _heading_positions(data, "## Next Phase")
    if not next_positions:
        _add(findings, "historical_readme_next_phase_heading_missing")
    elif len(next_positions) != 1:
        _add(findings, "historical_readme_next_phase_heading_duplicated")

    prefix_valid = configuration_valid and len(next_positions) == 1
    next_phase_valid = configuration_valid and len(next_positions) == 1
    if len(next_positions) == 1:
        heading_start = next_positions[0]
        prefix = data[:heading_start]
        if _sha256_repository_text_bytes(prefix) != EXPECTED_README_PREFIX_SHA256:
            _add(findings, "historical_readme_immutable_prefix_digest_mismatch")
            prefix_valid = False
        actual_block = data[heading_start:]
        if actual_block != EXPECTED_NEXT_PHASE_BLOCK.encode("utf-8"):
            _add(
                findings,
                "historical_readme_next_phase_block_mismatch_or_unexpected_"
                "trailing_content",
            )
            next_phase_valid = False
    else:
        prefix_valid = False
        next_phase_valid = False

    sections = _level_two_sections(data)
    releases_bytes = sections.get("## Releases")
    releases_preserved = releases_bytes is not None
    if releases_bytes is None:
        _add(findings, "historical_readme_releases_section_missing")
    else:
        if (
            _sha256_repository_text_bytes(releases_bytes)
            != EXPECTED_RELEASES_SECTION_SHA256
        ):
            _add(findings, "historical_readme_releases_section_modified")
            releases_preserved = False
        releases_text = releases_bytes.decode("utf-8")
        listed_versions = re.findall(
            r"(?m)^-\s+(v\d+\.\d+\.\d+)\b", releases_text
        )
        if not listed_versions or listed_versions[-1] != "v0.12.0":
            _add(findings, "historical_readme_latest_released_version_invalid")
            releases_preserved = False
        if "v0.13.0" in releases_text:
            _add(findings, "historical_readme_v0_13_0_release_entry_forbidden")
            releases_preserved = False

    current_bytes = sections.get("## Current Status")
    current_preserved = current_bytes is not None
    if current_bytes is None:
        _add(findings, "historical_readme_current_status_section_missing")
    else:
        if (
            _sha256_repository_text_bytes(current_bytes)
            != EXPECTED_CURRENT_STATUS_SECTION_SHA256
        ):
            _add(findings, "historical_readme_current_status_section_modified")
            current_preserved = False
        current_text = current_bytes.decode("utf-8")
        required_complete = (
            "M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11, M12, "
            "and M13 are complete."
        )
        if required_complete not in current_text:
            _add(
                findings,
                "historical_readme_m1_through_m13_completion_state_invalid",
            )
            current_preserved = False
        if re.search(r"(?im)^\s*M14\s+completed:\s*$", current_text):
            _add(findings, "historical_readme_m14_completed_heading_forbidden")
            current_preserved = False
        if re.search(r"(?i)\bM14\b[^\r\n]{0,100}\bcomplete(?:d)?\b", current_text):
            _add(
                findings,
                "historical_readme_m14_completion_declaration_forbidden",
            )
            current_preserved = False
        if "v0.13.0" in current_text:
            _add(
                findings,
                "historical_readme_v0_13_0_released_status_forbidden",
            )
            current_preserved = False

    if len(next_positions) == 1:
        next_text = data[next_positions[0] :].decode("utf-8")
        for statement in REQUIRED_NEXT_PHASE_STATEMENTS:
            if statement not in next_text:
                _add(
                    findings,
                    "historical_readme_next_phase_statement_missing:"
                    f"{_token(statement)}",
                )
                next_phase_valid = False
        for source_pr in EXPECTED_SOURCE_PRS:
            if source_pr not in next_text:
                _add(
                    findings,
                    f"historical_readme_evidence_link_missing:{source_pr}",
                )
                next_phase_valid = False

    return (
        present,
        snapshot_integrity_valid,
        prefix_valid,
        next_phase_valid,
        releases_preserved,
        current_preserved,
    )


def _validate_release_proof_bundle(
    payload: Mapping[str, Any], root: Path, findings: list[str]
) -> tuple[bool, bool, dict[str, Any] | None]:
    entries = payload.get("release_proof_bundle")
    present = isinstance(entries, list) and len(entries) == len(EXPECTED_BUNDLE)
    integrity_valid = present
    if not isinstance(entries, list):
        entries = []
        _add(findings, "release_proof_bundle_invalid")
    elif len(entries) != len(EXPECTED_BUNDLE):
        _add(findings, "release_proof_bundle_coverage_invalid")

    for index, expected in enumerate(EXPECTED_BUNDLE):
        raw = entries[index] if index < len(entries) else None
        if not isinstance(raw, Mapping):
            _add(findings, f"release_proof_bundle_entry_missing:{index}")
            present = False
            integrity_valid = False
            continue
        for field, expected_value in expected.items():
            if raw.get(field) != expected_value:
                _add(findings, f"release_proof_bundle_field_invalid:{index}:{field}")
                integrity_valid = False
                if field == "relative_path":
                    _add(findings, f"release_proof_bundle_path_substitution:{index}")
                    present = False
                elif field == "sha256":
                    _add(
                        findings,
                        "release_proof_bundle_historical_digest_mismatch:"
                        + expected["relative_path"],
                    )
                    _add(
                        findings,
                        "release_proof_bundle_digest_mismatch:"
                        + expected["relative_path"],
                    )

        relative_path = expected["relative_path"]
        maintained_digest = EXPECTED_MAINTAINED_BUNDLE_SHA256_OVERRIDES.get(
            relative_path, expected["sha256"]
        )
        try:
            observed_digest = sha256_repository_file(
                root,
                relative_path,
                mode="text",
            )
        except RepositoryArtifactPathError:
            _add(findings, f"release_proof_bundle_path_unsafe:{relative_path}")
            present = False
            integrity_valid = False
        except FileNotFoundError:
            _add(findings, f"release_proof_bundle_file_missing:{relative_path}")
            present = False
            integrity_valid = False
        except RepositoryArtifactFileTypeError:
            _add(findings, f"release_proof_bundle_file_not_regular:{relative_path}")
            present = False
            integrity_valid = False
        except UnicodeDecodeError:
            _add(findings, f"release_proof_bundle_malformed_utf8:{relative_path}")
            integrity_valid = False
        except RepositoryArtifactTextError:
            _add(findings, f"release_proof_bundle_lone_cr:{relative_path}")
            integrity_valid = False
        except OSError:
            _add(findings, f"release_proof_bundle_file_unreadable:{relative_path}")
            integrity_valid = False
        else:
            if observed_digest != maintained_digest:
                _add(
                    findings,
                    f"release_proof_bundle_maintained_digest_mismatch:{relative_path}",
                )
                _add(findings, f"release_proof_bundle_digest_mismatch:{relative_path}")
                integrity_valid = False

    release_fixture_path = _safe_repository_path(root, EXPECTED_BUNDLE[0]["relative_path"])
    release_fixture: dict[str, Any] | None = None
    if release_fixture_path is not None and release_fixture_path.is_file():
        try:
            loaded = json.loads(release_fixture_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                release_fixture = loaded
            else:
                _add(findings, "release_proof_fixture_not_object")
                integrity_valid = False
        except (OSError, UnicodeError, json.JSONDecodeError):
            _add(findings, "release_proof_fixture_unreadable")
            integrity_valid = False
    return present, integrity_valid, release_fixture


def _validate_release_proof_state(
    payload: Mapping[str, Any], release_fixture: Mapping[str, Any] | None, findings: list[str]
) -> bool:
    expected_values = {
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
    required_authority = {
        "retained_authority_owner": "AAOS",
        "decision_proof_sealing_owner": "AAOS",
        "decision_proof_sealing_statement": "Decision Proof sealing remains AAOS-owned.",
        "sovereignty_statement": "AAOS remains the decision sovereignty layer.",
    }
    declaration = _as_mapping(payload.get("release_proof_state_validation"))
    valid = True
    if declaration.get("source_fixture_path") != EXPECTED_BUNDLE[0]["relative_path"]:
        _add(findings, "release_proof_state_source_path_invalid")
        valid = False
    if declaration.get("loaded_as_inert_json_only") is not True:
        _add(findings, "release_proof_state_load_mode_invalid")
        valid = False
    if _as_mapping(declaration.get("expected_values")) != expected_values:
        _add(findings, "release_proof_state_expected_values_invalid")
        valid = False
    if _as_mapping(declaration.get("required_authority")) != required_authority:
        _add(findings, "release_proof_state_required_authority_invalid")
        valid = False
    if declaration.get("completeness_role") != "evidence_readiness_only":
        _add(findings, "release_proof_state_completeness_role_invalid")
        valid = False

    if not isinstance(release_fixture, Mapping):
        _add(findings, "release_proof_fixture_missing")
        return False
    for field, expected in expected_values.items():
        actual = release_fixture.get(field)
        mismatch = (
            actual is not expected if isinstance(expected, bool) else actual != expected
        )
        if mismatch:
            _add(findings, f"release_proof_state_invalid:{field}")
            valid = False

    authority = _as_mapping(release_fixture.get("authority_boundary"))
    for field, expected in required_authority.items():
        if authority.get(field) != expected:
            _add(findings, f"release_proof_authority_invalid:{field}")
            valid = False
    return valid


def _validate_linkage_and_evidence(
    payload: Mapping[str, Any], findings: list[str]
) -> tuple[bool, bool]:
    refs_valid = _as_mapping(payload.get("release_linkage_refs")) == EXPECTED_LINKAGE_REFS
    if not refs_valid:
        _add(findings, "release_linkage_refs_invalid")

    packet = _as_mapping(payload.get("completion_evidence_packet"))
    valid = True
    expected_scalar_values = {
        "milestone": "M14",
        "tracker_reference": "#201",
        "prior_release_baseline": "v0.12.0",
        "future_release": "v0.13.0",
        "release_proof_pr": "#213",
        "readme_path": "README.md",
        "readme_section": "Next Phase",
        "readme_prefix_integrity_status": "valid",
        "readme_future_path_status": "present_future_only",
        "released_versions_section_status": "unchanged",
        "current_status_section_status": "unchanged",
        "release_proof_status": "complete_for_review",
        "completion_readiness_status": "ready_for_final_review",
        "final_completion_review_completed": False,
        "release_approved": False,
        "released": False,
        "m14_complete": False,
        "decision_proof_sealed": False,
        "governance_role": "completion_traceability_only_not_final_completion",
    }
    for field, expected in expected_scalar_values.items():
        actual = packet.get(field)
        mismatch = (
            actual is not expected if isinstance(expected, bool) else actual != expected
        )
        if mismatch:
            _add(findings, f"completion_evidence_packet_invalid:{field}")
            valid = False
    if not _ordered_string_sequence_equal(
        packet.get("source_pr_references"), EXPECTED_SOURCE_PRS
    ):
        _add(findings, "completion_evidence_source_pr_references_invalid")
        valid = False
    expected_digests = [
        {"relative_path": entry["relative_path"], "sha256": entry["sha256"]}
        for entry in EXPECTED_BUNDLE
    ]
    if packet.get("release_proof_bundle_digests") != expected_digests:
        _add(findings, "completion_evidence_bundle_digests_invalid")
        valid = False
    return refs_valid, valid


def _validate_external_state(payload: Mapping[str, Any], findings: list[str]) -> bool:
    external = _as_mapping(payload.get("external_state_review_inputs"))
    expected = {
        "tracker_issue": "#201",
        "tracker_expected_state": "open",
        "source_prs": list(EXPECTED_SOURCE_PRS),
        "source_pr_expected_state": "merged",
        "verification_mode": "reviewer_confirmed_external_state",
        "verified_by_deterministic_evaluator": False,
        "reviewer_confirmation_required": True,
    }
    if external != expected:
        _add(findings, "external_state_review_inputs_invalid")
        return False
    return True


def _validate_command_manifest(payload: Mapping[str, Any], findings: list[str]) -> bool:
    entries = payload.get("verification_command_manifest")
    valid = True
    if not isinstance(entries, list):
        _add(findings, "verification_command_manifest_invalid")
        return False
    if len(entries) != len(EXPECTED_COMMANDS):
        _add(findings, "verification_command_manifest_count_invalid")
        valid = False
    for index, (command_id, command) in enumerate(EXPECTED_COMMANDS):
        entry = entries[index] if index < len(entries) else None
        if not isinstance(entry, Mapping):
            _add(findings, f"verification_command_missing:{command_id}")
            valid = False
            continue
        expected_keys = {
            "command_id",
            "command",
            "verification_scope",
            "expected_exit_code",
            "expected_result",
            "evidence_recording_requirement",
            "executed_by_completion_readiness_evaluator",
        }
        if set(entry) != expected_keys:
            _add(findings, f"verification_command_unexpected_fields:{command_id}")
            valid = False
        if entry.get("command_id") != command_id or entry.get("command") != command:
            _add(findings, f"verification_command_binding_invalid:{command_id}")
            valid = False
        for field in (
            "verification_scope",
            "expected_result",
            "evidence_recording_requirement",
        ):
            if not isinstance(entry.get(field), str) or not entry.get(field):
                _add(findings, f"verification_command_field_invalid:{command_id}:{field}")
                valid = False
        if entry.get("expected_exit_code") != 0:
            _add(findings, f"verification_command_exit_code_invalid:{command_id}")
            valid = False
        if entry.get("executed_by_completion_readiness_evaluator") is not False:
            _add(findings, f"verification_command_execution_claimed:{command_id}")
            valid = False
    if payload.get("verification_manifest_execution_claimed") is not False:
        _add(findings, "verification_manifest_execution_claimed")
        valid = False
    return valid


def _validate_outstanding_items(payload: Mapping[str, Any], findings: list[str]) -> bool:
    entries = payload.get("outstanding_completion_items")
    if not isinstance(entries, list):
        _add(findings, "outstanding_completion_items_invalid")
        return False
    valid = True
    if len(entries) != len(EXPECTED_OUTSTANDING):
        _add(findings, "outstanding_completion_item_count_invalid")
        valid = False
    for index, (item_id, order, prerequisite) in enumerate(EXPECTED_OUTSTANDING):
        item = entries[index] if index < len(entries) else None
        if not isinstance(item, Mapping):
            _add(findings, f"outstanding_item_missing:{item_id}")
            valid = False
            continue
        expected_keys = {
            "item_id",
            "status",
            "sequence_order",
            "prerequisite",
            "authorized_actor",
            "completion_evidence_required",
            "not_performed_by_this_pr",
        }
        if set(item) != expected_keys:
            _add(findings, f"outstanding_item_unexpected_fields:{item_id}")
            valid = False
        expected = {
            "item_id": item_id,
            "status": "pending",
            "sequence_order": order,
            "prerequisite": prerequisite,
            "not_performed_by_this_pr": True,
        }
        for field, expected_value in expected.items():
            if item.get(field) != expected_value:
                _add(findings, f"outstanding_item_invalid:{item_id}:{field}")
                valid = False
        if not isinstance(item.get("authorized_actor"), str) or not item.get(
            "authorized_actor"
        ):
            _add(findings, f"outstanding_item_invalid:{item_id}:authorized_actor")
            valid = False
        evidence = item.get("completion_evidence_required")
        evidence_valid = (
            isinstance(evidence, str)
            and bool(evidence)
            or isinstance(evidence, list)
            and bool(evidence)
            and all(isinstance(value, str) and bool(value) for value in evidence)
        )
        if not evidence_valid:
            _add(
                findings,
                f"outstanding_item_invalid:{item_id}:completion_evidence_required",
            )
            valid = False
    return valid


def _validate_cases(payload: Mapping[str, Any], findings: list[str]) -> bool:
    cases = payload.get("completion_readiness_cases")
    if not isinstance(cases, list):
        _add(findings, "completion_readiness_cases_invalid")
        return False
    valid = True
    if len(cases) < 58:
        _add(findings, "completion_readiness_case_coverage_incomplete")
        valid = False
    case_ids: list[str] = []
    for item in cases:
        if not isinstance(item, Mapping):
            _add(findings, "completion_readiness_case_entry_invalid")
            valid = False
            continue
        case_id = item.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            _add(findings, "completion_readiness_case_id_missing")
            valid = False
            continue
        case_ids.append(case_id)
        if not isinstance(item.get("description"), str) or not item.get("description"):
            _add(findings, f"completion_readiness_case_description_missing:{case_id}")
            valid = False
        if item.get("expected_result") not in {"valid", "invalid"}:
            _add(findings, f"completion_readiness_case_expected_result_invalid:{case_id}")
            valid = False
        elif (
            case_id in REQUIRED_CASE_EXPECTED_RESULTS
            and item.get("expected_result")
            != REQUIRED_CASE_EXPECTED_RESULTS[case_id]
        ):
            _add(
                findings,
                f"completion_readiness_case_expected_result_mismatch:{case_id}",
            )
            valid = False
    if len(case_ids) != len(set(case_ids)):
        _add(findings, "completion_readiness_case_id_duplicate")
        valid = False
    for required_case_id in REQUIRED_CASE_IDS:
        if case_ids.count(required_case_id) != 1:
            _add(findings, f"completion_readiness_case_missing:{required_case_id}")
            valid = False
    return valid


def _validate_catalogs_and_authority(
    payload: Mapping[str, Any], findings: list[str]
) -> tuple[bool, bool]:
    valid = True
    if not _ordered_string_sequence_equal(
        payload.get("required_boundary_statements"), REQUIRED_BOUNDARY_STATEMENTS
    ):
        _add(findings, "required_boundary_statements_invalid")
        valid = False

    semantic = _as_mapping(payload.get("semantic_boundaries"))
    if set(semantic.values()) != set(REQUIRED_BOUNDARY_STATEMENTS):
        _add(findings, "semantic_boundaries_invalid")
        valid = False

    allowed = _string_set(payload.get("allowed_evaluator_outputs"))
    forbidden = _string_set(payload.get("forbidden_evaluator_outputs"))
    if allowed != REQUIRED_ALLOWED_OUTPUTS:
        _add(findings, "allowed_evaluator_outputs_invalid")
        valid = False
    if forbidden != REQUIRED_FORBIDDEN_OUTPUTS:
        _add(findings, "forbidden_evaluator_outputs_invalid")
        valid = False
    if allowed & forbidden:
        _add(findings, "evaluator_output_catalog_overlap")
        valid = False

    policy = _as_mapping(payload.get("forbidden_claim_inspection_policy"))
    policy_expectations = {
        "explicit_negative_evidence_requires_exact_normalized_match": True,
        "arbitrary_not_prefix_is_negative": False,
        "unknown_non_empty_value_under_forbidden_key_is_affirmative": True,
        "negative_outer_state_does_not_suppress_nested_affirmative_claim": True,
        "neutral_metadata_is_not_authority_state": True,
    }
    expected_policy_keys = set(policy_expectations) | {
        "explicit_negative_normalized_vocabulary",
        "authority_state_fields",
        "known_forbidden_authority_keys",
        "neutral_metadata_fields",
    }
    if set(policy) != expected_policy_keys:
        _add(findings, "forbidden_claim_policy_catalogs_invalid")
        valid = False
    for field, expected in policy_expectations.items():
        if policy.get(field) is not expected:
            _add(findings, f"forbidden_claim_policy_invalid:{field}")
            valid = False

    negative_vocabulary = policy.get("explicit_negative_normalized_vocabulary")
    if not _typed_sequence_equal(
        negative_vocabulary, EXPLICIT_NEGATIVE_VOCABULARY
    ):
        _add(findings, "explicit_negative_vocabulary_invalid")
        valid = False

    if not _typed_sequence_equal(
        policy.get("authority_state_fields"), AUTHORITY_STATE_FIELD_ORDER
    ):
        _add(findings, "authority_state_fields_invalid")
        valid = False
    if not _typed_sequence_equal(
        policy.get("known_forbidden_authority_keys"),
        EXPECTED_POLICY_KNOWN_FORBIDDEN_AUTHORITY_KEYS,
    ):
        _add(findings, "known_forbidden_authority_keys_invalid")
        valid = False
    if not _typed_sequence_equal(
        policy.get("neutral_metadata_fields"),
        EXPECTED_POLICY_NEUTRAL_METADATA_FIELDS,
    ):
        _add(findings, "neutral_metadata_fields_invalid")
        valid = False

    authority = _as_mapping(payload.get("authority_boundary"))
    authority_valid = True
    expected_authority_keys = {
        "retained_authority_owner",
        "decision_proof_sealing_owner",
        "may",
        "must_not",
        "readme_entry_role",
        "release_proof_role",
        "decision_proof_sealing_statement",
        "sovereignty_statement",
    }
    if (
        set(authority) != expected_authority_keys
        or authority.get("retained_authority_owner") != "AAOS"
        or authority.get("decision_proof_sealing_owner") != "AAOS"
        or authority.get("decision_proof_sealing_statement")
        != "Decision Proof sealing remains AAOS-owned."
        or authority.get("sovereignty_statement")
        != "AAOS remains the decision sovereignty layer."
        or _string_set(authority.get("may")) != REQUIRED_AUTHORITY_MAY
        or _string_set(authority.get("must_not")) != REQUIRED_AUTHORITY_MUST_NOT
    ):
        _add(findings, "authority_boundary_invalid")
        authority_valid = False
        valid = False
    return valid, authority_valid


def _validate_expected_baseline(payload: Mapping[str, Any], findings: list[str]) -> bool:
    baseline = _as_mapping(payload.get("expected_baseline_result"))
    if baseline != EXPECTED_BASELINE_RESULT:
        _add(findings, "expected_baseline_result_invalid")
        return False
    return True


def _is_explicit_negative(value: Any) -> bool:
    if value is None or value is False:
        return True
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value == 0
    if isinstance(value, str):
        return _token(value) in EXPLICIT_NEGATIVE_STRINGS
    return False


def _scalar_is_affirmative(value: Any) -> bool:
    if _is_explicit_negative(value):
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    return bool(value)


def _find_structured_authority_signals(value: Any) -> tuple[bool, bool]:
    if isinstance(value, Mapping):
        saw_signal = False
        affirmative = False
        for key, nested in value.items():
            key_token = _token(key)
            if key_token in FORBIDDEN_AUTHORITY_KEYS or key_token in AUTHORITY_STATE_FIELDS:
                saw_signal = True
                if _authority_value_is_affirmative(nested):
                    affirmative = True
            elif isinstance(nested, (Mapping, list, tuple)):
                child_signal, child_affirmative = _find_structured_authority_signals(
                    nested
                )
                saw_signal = saw_signal or child_signal
                affirmative = affirmative or child_affirmative
        return saw_signal, affirmative
    if isinstance(value, (list, tuple)):
        saw_signal = False
        affirmative = False
        for nested in value:
            child_signal, child_affirmative = _find_structured_authority_signals(
                nested
            )
            saw_signal = saw_signal or child_signal
            affirmative = affirmative or child_affirmative
        return saw_signal, affirmative
    return False, False


def _authority_value_is_affirmative(value: Any) -> bool:
    if isinstance(value, Mapping):
        saw_signal, affirmative = _find_structured_authority_signals(value)
        if affirmative:
            return True
        if saw_signal:
            return False
        return bool(value)
    if isinstance(value, (list, tuple)):
        if not value:
            return False
        for nested in value:
            if isinstance(nested, (Mapping, list, tuple)):
                saw_signal, affirmative = _find_structured_authority_signals(nested)
                if affirmative:
                    return True
                if not saw_signal and bool(nested):
                    return True
            elif _scalar_is_affirmative(nested):
                return True
        return False
    return _scalar_is_affirmative(value)


def _scan_forbidden_claims(
    value: Any, findings: list[str], path: tuple[str, ...] = ()
) -> None:
    if isinstance(value, Mapping):
        for raw_key, nested in value.items():
            key = str(raw_key)
            key_token = _token(key)
            if key_token in CLAIM_SCAN_SKIP_KEYS:
                continue
            current_path = path + (key,)
            if key_token in FORBIDDEN_AUTHORITY_KEYS:
                affirmative = _authority_value_is_affirmative(nested)
                if affirmative:
                    _add(
                        findings,
                        "affirmative_forbidden_claim:" + ".".join(current_path),
                    )
                elif isinstance(nested, (Mapping, list, tuple)):
                    # An exact-negative outer state is not authority, but it must
                    # not hide a nested forbidden key or exact forbidden token.
                    # Recurse only when the outer claim did not already produce a
                    # finding so one structured claim is not reported twice.
                    _scan_forbidden_claims(nested, findings, current_path)
                continue
            if key_token in SPECIALIZED_AUTHORITY_STATE_FIELDS:
                affirmative = _authority_value_is_affirmative(nested)
                if affirmative:
                    _add(
                        findings,
                        "affirmative_forbidden_claim:" + ".".join(current_path),
                    )
                elif isinstance(nested, (Mapping, list, tuple)):
                    _scan_forbidden_claims(nested, findings, current_path)
                continue
            if isinstance(nested, (Mapping, list, tuple)):
                _scan_forbidden_claims(nested, findings, current_path)
            elif isinstance(nested, str) and _token(nested) in REQUIRED_FORBIDDEN_OUTPUTS:
                _add(
                    findings,
                    "forbidden_output_token_used_as_value:" + ".".join(current_path),
                )
    elif isinstance(value, (list, tuple)):
        for index, nested in enumerate(value):
            _scan_forbidden_claims(nested, findings, path + (str(index),))
    elif isinstance(value, str) and _token(value) in REQUIRED_FORBIDDEN_OUTPUTS:
        _add(findings, "forbidden_output_token_used_as_value:" + ".".join(path))


def _build_outputs(
    *,
    valid: bool,
    coverage: bool,
    prefix_integrity: bool,
    next_phase_valid: bool,
    releases_preserved: bool,
    current_preserved: bool,
    bundle_integrity: bool,
    authority_preserved: bool,
) -> list[str]:
    outputs = [
        "m14_completion_readiness_valid"
        if valid
        else "m14_completion_readiness_invalid",
        (
            "completion_evidence_coverage_complete"
            if coverage
            else "completion_evidence_coverage_incomplete"
        ),
        (
            "readme_prefix_integrity_valid"
            if prefix_integrity
            else "readme_prefix_integrity_invalid"
        ),
        (
            "readme_future_path_present"
            if next_phase_valid
            else "readme_future_path_invalid"
        ),
    ]
    if releases_preserved:
        outputs.append("released_versions_section_preserved")
    if current_preserved:
        outputs.append("current_status_section_preserved")
    outputs.append(
        "release_proof_bundle_valid"
        if bundle_integrity
        else "release_proof_bundle_invalid"
    )
    if valid:
        outputs.extend(
            (
                "completion_ready_for_review",
                "ready_for_final_m14_completion_review",
                "external_state_confirmation_required",
                "review_required",
            )
        )
    else:
        outputs.extend(
            (
                "external_state_confirmation_required",
                "not_ready",
                "escalation_required",
            )
        )
        if not authority_preserved:
            outputs.append("fail_closed_recommended")
    return outputs


def evaluate_m14_completion_readiness(
    payload: dict[str, Any], repository_root: str | Path | None = None
) -> dict[str, Any]:
    """Validate completion readiness without completing M14 or publishing v0.13.0."""

    findings: list[str] = []
    if not isinstance(payload, dict):
        payload = {}
        _add(findings, "completion_readiness_payload_invalid")
    root = _repository_root(repository_root)

    top_valid = _validate_top_level(payload, findings)
    (
        historical_snapshot_present,
        historical_snapshot_integrity,
        prefix_integrity,
        next_phase_valid,
        releases_preserved,
        current_preserved,
    ) = _validate_historical_readme_snapshot(payload, root, findings)
    historical_phase_state_valid = bool(
        prefix_integrity
        and next_phase_valid
        and releases_preserved
        and current_preserved
    )
    bundle_present, bundle_integrity, release_fixture = _validate_release_proof_bundle(
        payload, root, findings
    )
    release_state_valid = _validate_release_proof_state(
        payload, release_fixture, findings
    )
    refs_valid, evidence_packet_valid = _validate_linkage_and_evidence(payload, findings)
    external_valid = _validate_external_state(payload, findings)
    manifest_valid = _validate_command_manifest(payload, findings)
    outstanding_valid = _validate_outstanding_items(payload, findings)
    cases_valid = _validate_cases(payload, findings)
    catalogs_valid, authority_catalog_valid = _validate_catalogs_and_authority(
        payload, findings
    )
    baseline_valid = _validate_expected_baseline(payload, findings)

    claim_findings: list[str] = []
    _scan_forbidden_claims(payload, claim_findings)
    for finding in claim_findings:
        _add(findings, finding)
    no_forbidden_claims = not claim_findings

    authority_preserved = bool(
        authority_catalog_valid
        and catalogs_valid
        and external_valid
        and no_forbidden_claims
        and all(payload.get(field) is False for field in REQUIRED_FALSE_TOP_LEVEL)
    )
    coverage = bool(
        refs_valid
        and evidence_packet_valid
        and historical_snapshot_present
        and historical_snapshot_integrity
        and prefix_integrity
        and next_phase_valid
        and releases_preserved
        and current_preserved
        and bundle_present
        and bundle_integrity
        and release_state_valid
    )

    valid = bool(
        top_valid
        and historical_snapshot_present
        and historical_snapshot_integrity
        and prefix_integrity
        and next_phase_valid
        and releases_preserved
        and current_preserved
        and bundle_present
        and bundle_integrity
        and release_state_valid
        and refs_valid
        and evidence_packet_valid
        and external_valid
        and manifest_valid
        and outstanding_valid
        and cases_valid
        and catalogs_valid
        and baseline_valid
        and authority_preserved
        and no_forbidden_claims
        and not findings
    )

    outputs = _build_outputs(
        valid=valid,
        coverage=coverage,
        prefix_integrity=prefix_integrity,
        next_phase_valid=next_phase_valid,
        releases_preserved=releases_preserved,
        current_preserved=current_preserved,
        bundle_integrity=bundle_integrity,
        authority_preserved=authority_preserved,
    )
    return {
        "valid": valid,
        "historical_readme_snapshot_present": historical_snapshot_present,
        "historical_readme_snapshot_integrity_valid": historical_snapshot_integrity,
        "historical_readme_prefix_integrity_valid": prefix_integrity,
        "historical_readme_next_phase_state_valid": next_phase_valid,
        "historical_readme_releases_state_valid": releases_preserved,
        "historical_readme_current_status_state_valid": current_preserved,
        "historical_readme_phase_state_valid": historical_phase_state_valid,
        "historical_evidence_phase": HISTORICAL_EVIDENCE_PHASE,
        "current_readme_checked_by_completion_readiness_evaluator": False,
        "current_readme_validation_owner": CURRENT_README_VALIDATION_OWNER,
        # Compatibility aliases below refer only to the immutable historical
        # snapshot.  They do not describe or validate the current README.md.
        "readme_present": historical_snapshot_present,
        "readme_prefix_integrity_valid": prefix_integrity,
        "readme_next_phase_valid": next_phase_valid,
        "released_versions_section_preserved": releases_preserved,
        "current_status_section_preserved": current_preserved,
        "release_proof_bundle_present": bundle_present,
        "release_proof_bundle_integrity_valid": bundle_integrity,
        "release_proof_state_valid": release_state_valid,
        "completion_evidence_coverage_complete": coverage,
        "authority_boundaries_preserved": authority_preserved,
        "verification_manifest_complete": manifest_valid,
        "external_state_confirmation_required": True,
        "outstanding_completion_items_valid": outstanding_valid,
        "completion_ready_for_review": valid,
        "ready_for_final_m14_completion_review": valid,
        "final_m14_completion_review_completed": False,
        "release_approved": False,
        "released": False,
        "m14_complete": False,
        "findings": sorted(findings),
        "outputs": outputs,
    }


def validate_m14_completion_readiness(
    payload: dict[str, Any], repository_root: str | Path | None = None
) -> dict[str, Any]:
    """Return the complete deterministic completion-readiness result."""

    return evaluate_m14_completion_readiness(payload, repository_root)


def evaluate_file(
    path: str | Path, repository_root: str | Path | None = None
) -> dict[str, Any]:
    """Load and evaluate one completion-readiness fixture as inert JSON data."""

    return evaluate_m14_completion_readiness(load_fixture(path), repository_root)
