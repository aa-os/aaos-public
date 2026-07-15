"""Deterministic, data-only M14 operational-readiness evaluation.

The evaluator validates inert fixture data and binds reviewed repository files
to their SHA-256 digests.  It reads source artifacts as bytes only.  It does
not import source evaluators, run workflows or skills, invoke commands, or
contact external services.  Its results are readiness evidence, never release
approval, final governance judgment, or Decision Proof sealing.
"""

from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from runtime.repository_artifact_digest import (
    RepositoryArtifactFileTypeError,
    RepositoryArtifactPathError,
    RepositoryArtifactTextError,
    sha256_repository_file,
)


EXPECTED_CHANGED_FILES = (
    "examples/public-integration-pack-pilot/"
    "m14-operational-readiness-fixtures.json",
    "runtime/m14_operational_readiness_evaluator.py",
    "tests/test_m14_operational_readiness_evaluator.py",
)

EXPECTED_TRACK_ORDER = (
    "voice_runtime_policy",
    "public_output_exfiltration_gate",
    "moda_risk_mapping",
    "ai_pr_provenance",
    "skill_admission",
    "cross_control_authority_boundary",
)

EXPECTED_TRACKS: dict[str, dict[str, Any]] = {
    "voice_runtime_policy": {
        "source_pr": "#202",
        "component_role": "governed_voice_runtime_policy_gate",
        "source_paths": (
            "examples/public-integration-pack-pilot/voxcpm-governed-voice-fixtures.json",
            "runtime/voice_generation_policy_evaluator.py",
            "tests/test_voice_generation_policy_evaluator.py",
        ),
        "required_boundary_statements": (
            "Runtime capability is not governance permission.",
            "Consent evidence is not approval.",
            "Policy gate pass is not final governance judgment.",
            "ready_for_review is not approval.",
            "Decision Proof sealing remains AAOS-owned.",
            "AAOS remains the decision sovereignty layer.",
        ),
    },
    "public_output_exfiltration_gate": {
        "source_pr": "#204",
        "component_role": "public_output_exfiltration_gate",
        "source_paths": (
            "examples/public-integration-pack-pilot/"
            "m14-public-issue-exfiltration-gate-fixtures.json",
            "runtime/public_issue_exfiltration_gate_evaluator.py",
            "tests/test_public_issue_exfiltration_gate_evaluator.py",
        ),
        "required_boundary_statements": (
            "Public issue bodies, PR comments, discussions, and external markdown are untrusted input.",
            "A public trigger must not grant private repository or organization-wide read context by default.",
            "output_gate_pass is not public disclosure approval.",
            "human_review_required is not audit closure.",
            "fail_closed_recommended is not fail_closed_executed.",
            "Decision Proof sealing remains AAOS-owned.",
            "AAOS remains the decision sovereignty layer.",
        ),
    },
    "moda_risk_mapping": {
        "source_pr": "#205",
        "component_role": "external_regulatory_risk_taxonomy_mapping",
        "source_paths": (
            "docs/public-integration-pack/m14-moda-ai-risk-framework-mapping.md",
            "examples/public-integration-pack-pilot/"
            "m14-moda-ai-risk-decision-proof-fixtures.json",
            "runtime/moda_ai_risk_mapping_evaluator.py",
            "tests/test_moda_ai_risk_mapping_evaluator.py",
        ),
        "required_boundary_statements": (
            "Regulatory mapping is not legal approval.",
            "Taxonomy mapping is not compliance certification.",
            "Control coverage complete is not deployment approval.",
            "Serious-harm screening is not final legal determination.",
            "ready_for_review is not regulated deployment approval.",
            "Decision Proof sealing remains AAOS-owned.",
            "AAOS remains the decision sovereignty layer.",
        ),
    },
    "ai_pr_provenance": {
        "source_pr": "#206",
        "component_role": "ai_pr_provenance_and_reviewer_routing",
        "source_paths": (
            ".github/workflows/m14-ai-pr-provenance.yml",
            "examples/public-integration-pack-pilot/"
            "m14-ai-authored-pr-provenance-fixtures.json",
            "runtime/ai_authored_pr_provenance_evaluator.py",
            "tests/test_ai_authored_pr_provenance_evaluator.py",
        ),
        "required_boundary_statements": (
            "AI-authored detection is provenance evidence, not identity proof.",
            "pr-by-ai is not approval.",
            "human-review-required is not completed review.",
            "Reviewer routing is not review approval.",
            "Workflow success is not merge approval.",
            "Decision Proof sealing remains AAOS-owned.",
            "AAOS remains the decision sovereignty layer.",
        ),
    },
    "skill_admission": {
        "source_pr": "#208",
        "component_role": "external_skill_capability_admission_gate",
        "source_paths": (
            "docs/capability-supply-chain/nvidia-skills-admission.md",
            "examples/public-integration-pack-pilot/m14-skill-admission-fixtures.json",
            "runtime/skill_admission_evaluator.py",
            "tests/test_skill_admission_evaluator.py",
        ),
        "required_boundary_statements": (
            "External skill capability is not governance permission.",
            "Skill installation is not execution authorization.",
            "Artifact signature is not governance approval.",
            "Scan passed is not risk accepted.",
            "admission_ready_for_review is not final admission approval.",
            "Decision Proof sealing remains AAOS-owned.",
            "AAOS remains the decision sovereignty layer.",
        ),
    },
    "cross_control_authority_boundary": {
        "source_pr": "#210",
        "component_role": "cross_control_authority_boundary_regression",
        "source_paths": (
            "examples/public-integration-pack-pilot/"
            "m14-cross-control-authority-boundary-regression-fixtures.json",
            "runtime/m14_cross_control_authority_boundary_evaluator.py",
            "tests/test_m14_cross_control_authority_boundary_evaluator.py",
        ),
        "required_boundary_statements": (
            "Multiple non-authoritative outputs do not aggregate into governance authority.",
            "Five passed gates are not final approval.",
            "Evidence accumulation does not create authority by aggregation.",
            "Source evaluators remain bounded evidence evaluators.",
            "Explicit negative governance evidence is not an affirmative authority claim.",
            "Decision Proof sealing remains AAOS-owned.",
            "AAOS remains the decision sovereignty layer.",
        ),
    },
}


def _artifact(
    track_id: str, source_pr: str, artifact_type: str
) -> dict[str, str]:
    return {
        "track_id": track_id,
        "source_pr": source_pr,
        "artifact_type": artifact_type,
    }


EXPECTED_ARTIFACTS: dict[str, dict[str, str]] = {
    "examples/public-integration-pack-pilot/voxcpm-governed-voice-fixtures.json": _artifact(
        "voice_runtime_policy", "#202", "fixture"
    ),
    "runtime/voice_generation_policy_evaluator.py": _artifact(
        "voice_runtime_policy", "#202", "runtime_evaluator"
    ),
    "tests/test_voice_generation_policy_evaluator.py": _artifact(
        "voice_runtime_policy", "#202", "deterministic_test"
    ),
    "examples/public-integration-pack-pilot/m14-public-issue-exfiltration-gate-fixtures.json": _artifact(
        "public_output_exfiltration_gate", "#204", "fixture"
    ),
    "runtime/public_issue_exfiltration_gate_evaluator.py": _artifact(
        "public_output_exfiltration_gate", "#204", "runtime_evaluator"
    ),
    "tests/test_public_issue_exfiltration_gate_evaluator.py": _artifact(
        "public_output_exfiltration_gate", "#204", "deterministic_test"
    ),
    "docs/public-integration-pack/m14-moda-ai-risk-framework-mapping.md": _artifact(
        "moda_risk_mapping", "#205", "mapping_document"
    ),
    "examples/public-integration-pack-pilot/m14-moda-ai-risk-decision-proof-fixtures.json": _artifact(
        "moda_risk_mapping", "#205", "fixture"
    ),
    "runtime/moda_ai_risk_mapping_evaluator.py": _artifact(
        "moda_risk_mapping", "#205", "runtime_evaluator"
    ),
    "tests/test_moda_ai_risk_mapping_evaluator.py": _artifact(
        "moda_risk_mapping", "#205", "deterministic_test"
    ),
    ".github/workflows/m14-ai-pr-provenance.yml": _artifact(
        "ai_pr_provenance", "#206", "workflow_definition"
    ),
    "examples/public-integration-pack-pilot/m14-ai-authored-pr-provenance-fixtures.json": _artifact(
        "ai_pr_provenance", "#206", "fixture"
    ),
    "runtime/ai_authored_pr_provenance_evaluator.py": _artifact(
        "ai_pr_provenance", "#206", "runtime_evaluator"
    ),
    "tests/test_ai_authored_pr_provenance_evaluator.py": _artifact(
        "ai_pr_provenance", "#206", "deterministic_test"
    ),
    "docs/capability-supply-chain/nvidia-skills-admission.md": _artifact(
        "skill_admission", "#208", "admission_document"
    ),
    "examples/public-integration-pack-pilot/m14-skill-admission-fixtures.json": _artifact(
        "skill_admission", "#208", "fixture"
    ),
    "runtime/skill_admission_evaluator.py": _artifact(
        "skill_admission", "#208", "runtime_evaluator"
    ),
    "tests/test_skill_admission_evaluator.py": _artifact(
        "skill_admission", "#208", "deterministic_test"
    ),
    "examples/public-integration-pack-pilot/m14-cross-control-authority-boundary-regression-fixtures.json": _artifact(
        "cross_control_authority_boundary", "#210", "fixture"
    ),
    "runtime/m14_cross_control_authority_boundary_evaluator.py": _artifact(
        "cross_control_authority_boundary", "#210", "runtime_evaluator"
    ),
    "tests/test_m14_cross_control_authority_boundary_evaluator.py": _artifact(
        "cross_control_authority_boundary", "#210", "deterministic_test"
    ),
}

# These are the digests recorded by the original PR #212 fixture.  They are
# historical evidence and must not be rewritten when a maintained file changes.
EXPECTED_HISTORICAL_ARTIFACT_SHA256 = {
    "examples/public-integration-pack-pilot/voxcpm-governed-voice-fixtures.json": "f2d30aca2abca68e0d69080098c473ff2ef7f45a5afae0eb2734dd48ae294921",
    "runtime/voice_generation_policy_evaluator.py": "6c6a10fc88b1abd6f35ae3993b27784fbe69d028d192e19275677296e21df84f",
    "tests/test_voice_generation_policy_evaluator.py": "0d2e3921ed4e7060615bfbc2ae0c192616b20990834e5be5a3663c78b19a0d4e",
    "examples/public-integration-pack-pilot/m14-public-issue-exfiltration-gate-fixtures.json": "ac682908ba081cfc58726046efcb928c51e64eb2037f03354fda80afeb0846a9",
    "runtime/public_issue_exfiltration_gate_evaluator.py": "f3453af5c1829a28c791b665640e24940ececdc211e364360635bfe39573e81d",
    "tests/test_public_issue_exfiltration_gate_evaluator.py": "e3ab2be88dfeb8ec85a9cd12936f33b54476e46c22eeebe650648a8678d962bc",
    "docs/public-integration-pack/m14-moda-ai-risk-framework-mapping.md": "d28987ceeb419d36f43e32f9fba6fa82c7233ce3355117ebac5f9c45cfae97a3",
    "examples/public-integration-pack-pilot/m14-moda-ai-risk-decision-proof-fixtures.json": "dc157dd2029912ffe7d2ed48485c6b6e603237a9aa2cca72bb8d12ba285ff2ba",
    "runtime/moda_ai_risk_mapping_evaluator.py": "11a71ee8a7a7120d798e5cbb262a9e98bb9b1e74ca2471db486d6bdd0d091f28",
    "tests/test_moda_ai_risk_mapping_evaluator.py": "96a52094a65a2cd9303a01aa62b2e53c5240fdc789ee005c243a44a627fc3564",
    ".github/workflows/m14-ai-pr-provenance.yml": "af8ba9426f1bda5c2b9a09fad7a2b03ef2c4d04a178e4f414519bf837ff19bf1",
    "examples/public-integration-pack-pilot/m14-ai-authored-pr-provenance-fixtures.json": "e72636d1871f2c1232c811aec41ca9724be1505916d4804a05be75e600f3808a",
    "runtime/ai_authored_pr_provenance_evaluator.py": "465a0aba8beb49a6d6ad55e0bfce65ab74f5368164c758841ab202c50432ef35",
    "tests/test_ai_authored_pr_provenance_evaluator.py": "e648d2606d38f05063d72be0fa270a0191a28dca24a5fc07e80414faa4fc1f8f",
    "docs/capability-supply-chain/nvidia-skills-admission.md": "f49b51dd960df118a002c7e3fef685bf39f4006f8372373c0cb1fa7b635f8f49",
    "examples/public-integration-pack-pilot/m14-skill-admission-fixtures.json": "4fc229be3883a2681f8ebfc3f2eb828514cd3a2d6729c5841bab5a7efe609509",
    "runtime/skill_admission_evaluator.py": "bb81697df1be79b96a6af373ce63314a01ac73392b3cdb97981abaddbe6a4400",
    "tests/test_skill_admission_evaluator.py": "7cfd8b7f801a9a9da0546ae64499b234cbd1882fbba64b7a169b01b866ec6abd",
    "examples/public-integration-pack-pilot/m14-cross-control-authority-boundary-regression-fixtures.json": "f44b6d3298922608096c10f248955fa4c25e8d4a3452d6d7c585f9237129809d",
    "runtime/m14_cross_control_authority_boundary_evaluator.py": "51a413dc5303d64d49e958ffde970925ffc5aebead3435f8cf714e6112e1b48c",
    "tests/test_m14_cross_control_authority_boundary_evaluator.py": "5a4a5e764655382e2b19aa5a4e8a5a6a2b5082ade733e7125d88dfd2ba6cfc52",
}

# Current repository integrity is independently maintained.  Later legitimate
# source changes belong here; they never overwrite the historical map above.
EXPECTED_MAINTAINED_ARTIFACT_SHA256_OVERRIDES = {
    "docs/public-integration-pack/m14-moda-ai-risk-framework-mapping.md": (
        "75ae56e8fecc423cda353ef118ca8859ddd06f5e95e31e2f72659ecfca1a54f2"
    ),
    "docs/capability-supply-chain/nvidia-skills-admission.md": (
        "ad9129242540d241d82b8fcd35f7ecb1da1c4559937ec20b3c424ae88faa316d"
    ),
    "tests/test_skill_admission_evaluator.py": (
        "45ba9f2f8369bf0c127993c480e5091a1a2ee8f7ca2a0be2f579b3de38011b83"
    ),
}
EXPECTED_MAINTAINED_ARTIFACT_SHA256 = {
    relative_path: EXPECTED_MAINTAINED_ARTIFACT_SHA256_OVERRIDES.get(
        relative_path, historical_digest
    )
    for relative_path, historical_digest in EXPECTED_HISTORICAL_ARTIFACT_SHA256.items()
}

EXPECTED_TOP_LEVEL_VALUES = {
    "fixture_status": "m14_active_work_not_complete",
    "tracker_issue": "#201",
    "tracker_issue_linkage": "Refs #201",
    "related_voice_runtime_pr": "#202",
    "related_public_output_gate_pr": "#204",
    "related_moda_mapping_pr": "#205",
    "related_ai_pr_provenance_pr": "#206",
    "related_skill_admission_pr": "#208",
    "related_cross_control_regression_pr": "#210",
    "readiness_scope": "m14_operational_readiness_before_release_proof",
    "m14_completion_status": "active_work_not_complete",
    "target_future_release": "v0.13.0",
}

REQUIRED_FALSE_TOP_LEVEL_FIELDS = (
    "readme_status_updated",
    "release_file_created",
    "release_tag_created",
    "github_release_created",
    "tracker_closed_by_fixture",
    "final_completion_declared_by_fixture",
    "final_release_approved_by_fixture",
    "risk_accepted_by_fixture",
    "fail_closed_executed_by_fixture",
    "rollback_executed_by_fixture",
    "audit_closed_by_fixture",
    "authority_transferred_by_fixture",
    "final_governance_judgment_made_by_fixture",
    "decision_proof_sealed_by_fixture",
)

REQUIRED_CONTAINER_TYPES = {
    "source_track_manifest": list,
    "source_artifact_manifest": list,
    "artifact_integrity_policy": dict,
    "readiness_dimensions": list,
    "operational_checklist": list,
    "external_state_review_inputs": dict,
    "verification_command_manifest": list,
    "outstanding_completion_items": list,
    "readiness_cases": list,
    "required_boundary_statements": list,
    "allowed_evaluator_outputs": list,
    "forbidden_evaluator_outputs": list,
    "forbidden_claim_inspection_policy": dict,
}

ARTIFACT_INTEGRITY_POLICY_KEYS = {
    "exact_relative_path_binding_required",
    "sha256_binding_required",
    "track_to_pr_binding_required",
    "artifact_type_binding_required",
    "mutable_branch_name_not_sole_identity",
    "repository_url_not_sole_identity",
    "artifact_name_not_sole_identity",
    "digest_drift_blocks_readiness",
    "missing_source_artifact_blocks_readiness",
    "unexpected_source_track_substitution_blocks_readiness",
}

EXPECTED_DIMENSION_STATUSES = {
    "source_track_coverage": "ready",
    "source_artifact_presence": "ready",
    "source_artifact_integrity": "ready",
    "runtime_capability_permission_boundary": "ready",
    "consent_and_identity_boundary": "ready",
    "public_output_safety_boundary": "ready",
    "regulatory_mapping_boundary": "ready",
    "skill_supply_chain_boundary": "ready",
    "cross_control_authority_boundary": "ready",
    "human_review_escalation_coverage": "ready",
    "fail_closed_recommendation_coverage": "ready",
    "rollback_recommendation_coverage": "ready",
    "trace_evidence_coverage": "ready",
    "replay_evidence_coverage": "ready",
    "deterministic_evaluator_coverage": "ready",
    "operational_verification_manifest": "ready",
    "release_proof_linkage_status": "pending_next_stage",
    "readme_future_status_path": "pending_next_stage",
    "tracker_completion_status": "pending_next_stage",
    "decision_sovereignty_retention": "ready",
}

ALLOWED_READINESS_STATUSES = {
    "ready",
    "conditionally_ready",
    "pending_next_stage",
    "blocked",
    "invalid",
}

REQUIRED_EVIDENCE_CLASSES = {
    "human_review",
    "fail_closed_recommendation",
    "rollback_recommendation",
    "trace_evidence",
    "replay_evidence",
    "deterministic_test",
}

REQUIRED_BOUNDARY_STATEMENTS = {
    "Operational readiness is not milestone completion.",
    "Implementation coverage is not release approval.",
    "Artifact presence is not evidence sufficiency.",
    "Artifact digest match is not governance approval.",
    "Test manifest completeness is not test execution evidence.",
    "A passing readiness evaluator is not final governance judgment.",
    "External GitHub state is reviewer-confirmed evidence, not machine-verified by this evaluator.",
    "ready_for_release_proof_linkage is not M14 complete.",
    "release_proof_linkage_pending is not release approval.",
    "readme_status_path_pending is not README authorization.",
    "Human-review coverage is not completed review.",
    "fail_closed_recommended is not fail_closed_executed.",
    "rollback_recommended is not rollback_executed.",
    "evidence_complete is not Decision Proof sealing.",
    "replay_ready is not Decision Proof sealing.",
    "Explicit negative governance evidence is not an affirmative authority claim.",
    "Decision Proof sealing remains AAOS-owned.",
    "AAOS remains the decision sovereignty layer.",
}

REQUIRED_ALLOWED_OUTPUTS = {
    "m14_operational_readiness_valid",
    "m14_operational_readiness_invalid",
    "source_track_coverage_complete",
    "source_track_coverage_incomplete",
    "source_artifact_missing",
    "artifact_integrity_valid",
    "artifact_integrity_invalid",
    "authority_boundaries_preserved",
    "authority_boundary_violation",
    "human_review_coverage_present",
    "fail_closed_coverage_present",
    "rollback_coverage_present",
    "trace_coverage_present",
    "replay_coverage_present",
    "verification_manifest_complete",
    "verification_manifest_incomplete",
    "external_state_confirmation_required",
    "release_proof_linkage_pending",
    "readme_status_path_pending",
    "ready_for_release_proof_linkage",
    "not_ready",
    "escalation_required",
}

REQUIRED_FORBIDDEN_OUTPUTS = {
    "operational_readiness_is_completion",
    "implementation_is_release_approval",
    "artifact_digest_is_governance_approval",
    "tests_executed_by_manifest",
    "github_state_machine_verified",
    "release_proof_approved",
    "readme_update_approved",
    "m14_completion_approved",
    "tracker_201_closed",
    "v0_13_0_released",
    "release_published",
    "risk_accepted",
    "fail_closed_executed",
    "rollback_executed",
    "audit_closed",
    "waiver_granted",
    "decision_proof_verified",
    "decision_proof_sealed",
    "sealed_by_readiness_evaluator",
    "authority_transferred",
    "final_governance_judgment",
    "m14_complete",
    "closes_201",
}

REQUIRED_COMMAND_IDS = (
    "validate_readiness_fixture_json",
    "compile_m14_evaluators",
    "compile_m14_tests",
    "run_merged_m14_targeted_tests",
    "run_operational_readiness_tests",
    "git_diff_check",
    "confirm_changed_file_scope",
)

EVALUATOR_MODULE_PATHS = (
    "runtime/voice_generation_policy_evaluator.py",
    "runtime/public_issue_exfiltration_gate_evaluator.py",
    "runtime/moda_ai_risk_mapping_evaluator.py",
    "runtime/ai_authored_pr_provenance_evaluator.py",
    "runtime/skill_admission_evaluator.py",
    "runtime/m14_cross_control_authority_boundary_evaluator.py",
    "runtime/m14_operational_readiness_evaluator.py",
)

TEST_MODULE_PATHS = (
    "tests/test_voice_generation_policy_evaluator.py",
    "tests/test_public_issue_exfiltration_gate_evaluator.py",
    "tests/test_moda_ai_risk_mapping_evaluator.py",
    "tests/test_ai_authored_pr_provenance_evaluator.py",
    "tests/test_skill_admission_evaluator.py",
    "tests/test_m14_cross_control_authority_boundary_evaluator.py",
    "tests/test_m14_operational_readiness_evaluator.py",
)

TARGETED_TEST_MODULES = (
    "tests.test_voice_generation_policy_evaluator",
    "tests.test_public_issue_exfiltration_gate_evaluator",
    "tests.test_moda_ai_risk_mapping_evaluator",
    "tests.test_ai_authored_pr_provenance_evaluator",
    "tests.test_skill_admission_evaluator",
    "tests.test_m14_cross_control_authority_boundary_evaluator",
)

EXPECTED_OUTSTANDING_ITEM_ORDER = (
    "release_proof_linkage",
    "future_readme_status_path",
    "final_m14_completion_review",
    "close_tracker_issue_201",
    "publish_v0_13_0_release",
)

EXPECTED_EXTERNAL_STATE = {
    "tracker_issue": "#201",
    "tracker_expected_state": "open",
    "source_prs": ["#202", "#204", "#205", "#206", "#208", "#210"],
    "source_pr_expected_state": "merged",
    "source_issues": ["#200", "#188", "#181", "#180", "#192"],
    "source_issue_expected_state": "closed_completed",
    "verification_mode": "reviewer_confirmed_external_state",
    "verified_by_deterministic_evaluator": False,
    "reviewer_confirmation_required": True,
}

TRACK_REQUIRED_FIELDS = {
    "track_id",
    "source_pr",
    "component_role",
    "implementation_state",
    "source_paths",
    "expected_control_capabilities",
    "required_boundary_statements",
    "readiness_evidence_classes",
    "reviewer_confirmation_required",
    "retained_authority_owner",
    "decision_proof_sealing_owner",
}

ARTIFACT_REQUIRED_FIELDS = {
    "track_id",
    "source_pr",
    "relative_path",
    "artifact_type",
    "required",
    "sha256",
    "digest_algorithm",
    "observed_on_branch",
    "evidence_role",
    "executable_by_readiness_evaluator",
}

DIMENSION_REQUIRED_FIELDS = {
    "dimension_id",
    "status",
    "required_evidence",
    "observed_evidence",
    "blocking_conditions",
    "reviewer_confirmation_required",
    "authoritative_result",
}

CHECKLIST_REQUIRED_FIELDS = {
    "check_id",
    "description",
    "category",
    "required",
    "evidence_references",
    "expected_status",
    "blocking_if_failed",
    "governance_boundary",
}

COMMAND_REQUIRED_FIELDS = {
    "command_id",
    "command",
    "verification_scope",
    "expected_exit_code",
    "expected_result",
    "evidence_recording_requirement",
    "executed_by_readiness_evaluator",
}

OUTSTANDING_REQUIRED_FIELDS = {
    "item_id",
    "status",
    "sequence_order",
    "prerequisite",
    "authorized_actor",
    "completion_evidence_required",
    "not_performed_by_this_pr",
}

SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

CLAIM_SCAN_SKIP_KEYS = {
    "source_track_manifest",
    "source_artifact_manifest",
    "artifact_integrity_policy",
    "readiness_dimensions",
    "operational_checklist",
    "external_state_review_inputs",
    "verification_command_manifest",
    "outstanding_completion_items",
    "readiness_cases",
    "required_boundary_statements",
    "allowed_evaluator_outputs",
    "forbidden_evaluator_outputs",
    "forbidden_claim_inspection_policy",
    "changed_file_scope",
}

ACTIVE_CLAIM_ROOT_KEYS = {
    "active_governance_evidence",
    "active_readiness_payload",
    "active_payload",
    "simulated_outputs",
    "evaluator_output",
    "outputs",
}

AFFIRMATIVE_CLAIM_KEYS = REQUIRED_FORBIDDEN_OUTPUTS | {
    "decision_proof_sealed_by_fixture",
    "risk_accepted_by_fixture",
    "fail_closed_executed_by_fixture",
    "rollback_executed_by_fixture",
    "audit_closed_by_fixture",
    "authority_transferred_by_fixture",
    "final_governance_judgment_made_by_fixture",
    "tracker_closed_by_fixture",
    "final_completion_declared_by_fixture",
    "final_release_approved_by_fixture",
    "readme_status_updated",
    "release_file_created",
    "release_tag_created",
    "github_release_created",
    "release_proof_linkage_complete",
    "release_proof_linkage_completed_by_fixture",
    "tracker_closed",
    "released",
}

POSITIVE_CLAIM_PHRASES = (
    "operational readiness is completion",
    "implementation is release approval",
    "artifact digest is governance approval",
    "tests executed by manifest",
    "github state machine verified",
    "release proof approved",
    "readme update approved",
    "m14 completion approved",
    "tracker 201 closed",
    "v0.13.0 released",
    "release published",
    "risk accepted",
    "fail closed executed",
    "rollback executed",
    "audit closed",
    "waiver granted",
    "decision proof verified",
    "decision proof sealed",
    "authority transferred",
    "final governance judgment",
    "m14 complete",
    "closes #201",
)

EXPLICIT_NEGATIVE_CLAIM_STATES = (
    "",
    "false",
    "0",
    "null",
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

NEGATIVE_CLAIM_VALUES = frozenset(EXPLICIT_NEGATIVE_CLAIM_STATES)

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
)

AUTHORITY_STATE_FIELDS = frozenset(AUTHORITY_STATE_FIELD_ORDER)

FORBIDDEN_CLAIM_POLICY_VALUES = {
    "recursively_inspect_active_readiness_payloads": True,
    "recursively_inspect_simulated_outputs": True,
    "explicit_negative_evidence_allowed": True,
    "field_name_alone_does_not_trigger_violation": True,
    "nested_affirmative_claims_detected": True,
    "dormant_case_payloads_excluded_until_activated": True,
    "explicit_negative_requires_exact_normalized_match": True,
    "generic_negative_prefix_acceptance": False,
    "unknown_non_empty_scalar_under_forbidden_key_is_affirmative": True,
    "structured_authority_state_fields_recursively_inspected": True,
    "neutral_metadata_is_not_authority_state": True,
    "negative_outer_state_cannot_hide_nested_affirmative_claim": True,
}


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_set(value: Any) -> set[str]:
    return {
        item.strip()
        for item in _as_list(value)
        if isinstance(item, str) and item.strip()
    }


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _token(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")


def _text(value: Any) -> str:
    return " ".join(str(value).strip().lower().replace("_", " ").split())


def _add(findings: list[str], finding: str) -> None:
    if finding not in findings:
        findings.append(finding)


def _is_explicit_negative(value: Any) -> bool:
    if value is False or value is None:
        return True
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value == 0
    if not isinstance(value, str):
        return False
    return _token(value) in NEGATIVE_CLAIM_VALUES


def _is_affirmative_claim_value(value: Any, known_claim_key: bool = False) -> bool:
    if _is_explicit_negative(value):
        return False
    if value is True:
        return True
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    if not isinstance(value, str):
        return False
    if known_claim_key:
        return bool(value.strip())
    normalized_token = _token(value)
    text = _text(value)
    if normalized_token in REQUIRED_FORBIDDEN_OUTPUTS:
        return True
    if any(phrase in text for phrase in POSITIVE_CLAIM_PHRASES):
        return True
    return False


def _scan_forbidden_claims(
    value: Any,
    findings: list[str],
    path: str = "payload",
    parent_key: str | None = None,
    active_context: bool = False,
    forbidden_container_context: bool = False,
    authority_state_context: bool = False,
) -> None:
    if not active_context and parent_key in CLAIM_SCAN_SKIP_KEYS:
        return
    if isinstance(value, Mapping):
        for raw_key, item in value.items():
            key = str(raw_key)
            token = _token(key)
            child_path = f"{path}.{key}"
            known_key = token in AFFIRMATIVE_CLAIM_KEYS
            state_field = token in AUTHORITY_STATE_FIELDS
            scalar_claim_context = bool(
                known_key
                or authority_state_context
                or (forbidden_container_context and state_field)
            )
            if not isinstance(item, (Mapping, list)):
                affirmative = _is_affirmative_claim_value(
                    item, scalar_claim_context
                )
                if affirmative and (
                    scalar_claim_context
                    or (
                    isinstance(item, str)
                    and (
                        _token(item) in REQUIRED_FORBIDDEN_OUTPUTS
                        or any(
                            phrase in _text(item)
                            for phrase in POSITIVE_CLAIM_PHRASES
                        )
                    )
                    )
                ):
                    _add(findings, f"affirmative_forbidden_claim:{child_path}")
            child_active_context = bool(
                active_context
                or (path == "payload" and token in ACTIVE_CLAIM_ROOT_KEYS)
            )
            child_forbidden_context = bool(
                forbidden_container_context or known_key
            )
            child_authority_state_context = bool(
                authority_state_context
                or (forbidden_container_context and state_field)
            )
            _scan_forbidden_claims(
                item,
                findings,
                child_path,
                token,
                child_active_context,
                child_forbidden_context,
                child_authority_state_context,
            )
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _scan_forbidden_claims(
                item,
                findings,
                f"{path}[{index}]",
                parent_key,
                active_context,
                forbidden_container_context,
                authority_state_context,
            )
        return
    if authority_state_context and _is_affirmative_claim_value(value, True):
        _add(findings, f"affirmative_forbidden_claim:{path}")
    elif isinstance(value, str) and _is_affirmative_claim_value(value):
        _add(findings, f"affirmative_forbidden_claim:{path}")


def _default_repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _repository_root(repository_root: str | Path | None) -> Path:
    root = _default_repository_root() if repository_root is None else Path(repository_root)
    return root.resolve()


def _safe_artifact_path(root: Path, relative_path: Any) -> Path | None:
    if not isinstance(relative_path, str) or not relative_path.strip():
        return None
    if "\\" in relative_path:
        return None
    pure_path = PurePosixPath(relative_path)
    if pure_path.is_absolute() or any(part in {"", ".", ".."} for part in pure_path.parts):
        return None
    candidate = root.joinpath(*pure_path.parts).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def load_fixture(path: str | Path) -> dict[str, Any]:
    """Load a JSON readiness fixture without interpreting or executing content."""

    parsed = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError("M14 operational readiness fixture must be a JSON object")
    return parsed


def _validate_top_level(payload: Mapping[str, Any], findings: list[str]) -> bool:
    valid = True
    for field, expected in EXPECTED_TOP_LEVEL_VALUES.items():
        if payload.get(field) != expected:
            _add(findings, f"top_level_state_invalid:{field}")
            valid = False

    for field in REQUIRED_FALSE_TOP_LEVEL_FIELDS:
        if payload.get(field) is not False:
            _add(findings, f"top_level_negative_boundary_invalid:{field}")
            valid = False

    future_release = payload.get("future_release_tag_path")
    if not isinstance(future_release, Mapping):
        _add(findings, "future_release_tag_path_invalid")
        valid = False
    else:
        if future_release.get("released") is not False:
            _add(findings, "future_release_incorrectly_marked_released")
            valid = False
        target_tag = future_release.get("target_tag")
        if target_tag is not None and target_tag != "v0.13.0":
            _add(findings, "future_release_target_tag_invalid")
            valid = False

    changed_files = payload.get("changed_file_scope")
    if not isinstance(changed_files, list) or tuple(changed_files) != EXPECTED_CHANGED_FILES:
        _add(findings, "changed_file_scope_invalid")
        valid = False

    for field, expected_type in REQUIRED_CONTAINER_TYPES.items():
        if not isinstance(payload.get(field), expected_type):
            _add(findings, f"required_container_invalid:{field}")
            valid = False
    return valid


def _validate_tracks(
    payload: Mapping[str, Any], findings: list[str]
) -> tuple[bool, bool, set[str]]:
    manifest = payload.get("source_track_manifest")
    if not isinstance(manifest, list):
        _add(findings, "source_track_manifest_invalid")
        return False, False, set()

    valid = True
    authority_valid = True
    evidence_classes: set[str] = set()
    entries: dict[str, Mapping[str, Any]] = {}
    seen_ids: list[str] = []

    for index, raw_entry in enumerate(manifest):
        if not isinstance(raw_entry, Mapping):
            _add(findings, f"source_track_entry_invalid:{index}")
            valid = False
            continue
        track_id = raw_entry.get("track_id")
        if not isinstance(track_id, str) or not track_id:
            _add(findings, f"source_track_id_missing:{index}")
            valid = False
            continue
        seen_ids.append(track_id)
        if track_id in entries:
            _add(findings, f"source_track_duplicate:{track_id}")
            valid = False
        entries[track_id] = raw_entry

    if tuple(seen_ids) != EXPECTED_TRACK_ORDER:
        _add(findings, "source_track_order_or_coverage_invalid")
        valid = False
    if set(entries) != set(EXPECTED_TRACKS) or len(manifest) != len(EXPECTED_TRACKS):
        _add(findings, "source_track_coverage_incomplete")
        valid = False

    for track_id, expected in EXPECTED_TRACKS.items():
        entry = entries.get(track_id)
        if entry is None:
            _add(findings, f"source_track_missing:{track_id}")
            continue

        missing_fields = TRACK_REQUIRED_FIELDS - set(entry)
        if missing_fields:
            for field in sorted(missing_fields):
                _add(findings, f"source_track_field_missing:{track_id}:{field}")
            valid = False

        if entry.get("source_pr") != expected["source_pr"]:
            _add(findings, f"source_pr_linkage_mismatch:{track_id}")
            valid = False
        if entry.get("component_role") != expected["component_role"]:
            _add(findings, f"component_role_mismatch:{track_id}")
            valid = False
        if entry.get("implementation_state") != "merged_source_artifacts_present":
            _add(findings, f"implementation_state_invalid:{track_id}")
            valid = False

        source_paths = entry.get("source_paths")
        if not isinstance(source_paths, list) or tuple(source_paths) != expected["source_paths"]:
            _add(findings, f"source_track_path_substitution:{track_id}")
            valid = False

        capabilities = entry.get("expected_control_capabilities")
        if not isinstance(capabilities, list) or not _string_set(capabilities):
            _add(findings, f"expected_control_capabilities_missing:{track_id}")
            valid = False

        boundaries = _string_set(entry.get("required_boundary_statements"))
        missing_boundaries = set(expected["required_boundary_statements"]) - boundaries
        if missing_boundaries:
            for statement in sorted(missing_boundaries):
                _add(
                    findings,
                    f"track_boundary_statement_missing:{track_id}:{_token(statement)}",
                )
            valid = False
            authority_valid = False

        track_evidence = _string_set(entry.get("readiness_evidence_classes"))
        if not track_evidence:
            _add(findings, f"readiness_evidence_classes_missing:{track_id}")
            valid = False
        evidence_classes.update(track_evidence)

        if entry.get("reviewer_confirmation_required") is not True:
            _add(findings, f"reviewer_confirmation_boundary_invalid:{track_id}")
            valid = False
        if entry.get("retained_authority_owner") != "AAOS":
            _add(findings, f"authority_owner_invalid:{track_id}")
            valid = False
            authority_valid = False
        if entry.get("decision_proof_sealing_owner") != "AAOS":
            _add(findings, f"decision_proof_sealing_owner_invalid:{track_id}")
            valid = False
            authority_valid = False

    missing_evidence_classes = REQUIRED_EVIDENCE_CLASSES - evidence_classes
    if missing_evidence_classes:
        for evidence_class in sorted(missing_evidence_classes):
            _add(findings, f"readiness_evidence_class_missing:{evidence_class}")
        valid = False

    return valid, authority_valid, evidence_classes


def _validate_artifact_policy(
    payload: Mapping[str, Any], findings: list[str]
) -> bool:
    policy = payload.get("artifact_integrity_policy")
    if not isinstance(policy, Mapping):
        _add(findings, "artifact_integrity_policy_invalid")
        return False
    valid = True
    for key in sorted(ARTIFACT_INTEGRITY_POLICY_KEYS):
        if policy.get(key) is not True:
            _add(findings, f"artifact_integrity_policy_rule_invalid:{key}")
            valid = False
    return valid


def _validate_artifacts(
    payload: Mapping[str, Any], root: Path, findings: list[str]
) -> tuple[bool, bool]:
    manifest = payload.get("source_artifact_manifest")
    if not isinstance(manifest, list):
        _add(findings, "source_artifact_manifest_invalid")
        return False, False

    presence_valid = True
    integrity_valid = _validate_artifact_policy(payload, findings)
    entries: dict[str, Mapping[str, Any]] = {}

    for index, raw_entry in enumerate(manifest):
        if not isinstance(raw_entry, Mapping):
            _add(findings, f"source_artifact_entry_invalid:{index}")
            presence_valid = False
            integrity_valid = False
            continue
        relative_path = raw_entry.get("relative_path")
        if not isinstance(relative_path, str) or not relative_path:
            _add(findings, f"source_artifact_path_missing:{index}")
            presence_valid = False
            integrity_valid = False
            continue
        if relative_path in entries:
            _add(findings, f"source_artifact_duplicate:{relative_path}")
            integrity_valid = False
        entries[relative_path] = raw_entry

    if len(manifest) != len(EXPECTED_ARTIFACTS) or set(entries) != set(EXPECTED_ARTIFACTS):
        _add(findings, "source_artifact_manifest_coverage_invalid")
        presence_valid = False
        integrity_valid = False

    for relative_path in sorted(set(entries) - set(EXPECTED_ARTIFACTS)):
        _add(findings, f"unexpected_source_artifact:{relative_path}")

    for relative_path, expected in EXPECTED_ARTIFACTS.items():
        entry = entries.get(relative_path)
        if entry is None:
            _add(findings, f"source_artifact_manifest_entry_missing:{relative_path}")
            presence_valid = False
            integrity_valid = False
            continue

        missing_fields = ARTIFACT_REQUIRED_FIELDS - set(entry)
        if missing_fields:
            for field in sorted(missing_fields):
                _add(findings, f"source_artifact_field_missing:{relative_path}:{field}")
            integrity_valid = False

        if entry.get("track_id") != expected["track_id"]:
            _add(findings, f"artifact_track_binding_mismatch:{relative_path}")
            integrity_valid = False
        if entry.get("source_pr") != expected["source_pr"]:
            _add(findings, f"artifact_source_pr_binding_mismatch:{relative_path}")
            integrity_valid = False
        if entry.get("artifact_type") != expected["artifact_type"]:
            _add(findings, f"artifact_type_binding_mismatch:{relative_path}")
            integrity_valid = False
        if entry.get("required") is not True:
            _add(findings, f"artifact_not_required:{relative_path}")
            integrity_valid = False
        if entry.get("digest_algorithm") != "sha256":
            _add(findings, f"artifact_digest_algorithm_invalid:{relative_path}")
            integrity_valid = False
        if entry.get("observed_on_branch") != "main":
            _add(findings, f"artifact_observed_branch_invalid:{relative_path}")
            integrity_valid = False
        if entry.get("executable_by_readiness_evaluator") is not False:
            _add(findings, f"artifact_execution_boundary_invalid:{relative_path}")
            integrity_valid = False
        if not _non_empty_string(entry.get("evidence_role")):
            _add(findings, f"artifact_evidence_role_missing:{relative_path}")
            integrity_valid = False

        declared_digest = entry.get("sha256")
        if not isinstance(declared_digest, str) or not SHA256_PATTERN.fullmatch(
            declared_digest
        ):
            _add(findings, f"artifact_digest_shape_invalid:{relative_path}")
            integrity_valid = False
        elif declared_digest != EXPECTED_HISTORICAL_ARTIFACT_SHA256[relative_path]:
            _add(findings, f"artifact_historical_digest_mismatch:{relative_path}")
            integrity_valid = False

        artifact_path = _safe_artifact_path(root, relative_path)
        if artifact_path is None:
            _add(findings, f"artifact_relative_path_unsafe:{relative_path}")
            presence_valid = False
            integrity_valid = False
            continue
        if not artifact_path.is_file():
            _add(findings, f"source_artifact_missing:{relative_path}")
            presence_valid = False
            integrity_valid = False
            continue
        try:
            observed_digest = sha256_repository_file(
                root, relative_path, mode="text"
            )
        except UnicodeDecodeError:
            _add(findings, f"source_artifact_malformed_utf8:{relative_path}")
            integrity_valid = False
            continue
        except RepositoryArtifactTextError:
            _add(findings, f"source_artifact_lone_carriage_return:{relative_path}")
            integrity_valid = False
            continue
        except RepositoryArtifactPathError:
            _add(findings, f"artifact_relative_path_unsafe:{relative_path}")
            presence_valid = False
            integrity_valid = False
            continue
        except (FileNotFoundError, RepositoryArtifactFileTypeError):
            _add(findings, f"source_artifact_missing:{relative_path}")
            presence_valid = False
            integrity_valid = False
            continue
        except OSError:
            _add(findings, f"source_artifact_unreadable:{relative_path}")
            presence_valid = False
            integrity_valid = False
            continue
        if observed_digest != EXPECTED_MAINTAINED_ARTIFACT_SHA256[relative_path]:
            _add(findings, f"artifact_maintained_digest_mismatch:{relative_path}")
            integrity_valid = False

    return presence_valid, integrity_valid and presence_valid


def _validate_dimensions(
    payload: Mapping[str, Any], findings: list[str]
) -> tuple[bool, dict[str, Mapping[str, Any]]]:
    dimensions = payload.get("readiness_dimensions")
    if not isinstance(dimensions, list):
        _add(findings, "readiness_dimensions_invalid")
        return False, {}

    valid = True
    entries: dict[str, Mapping[str, Any]] = {}
    seen_ids: list[str] = []
    for index, raw_entry in enumerate(dimensions):
        if not isinstance(raw_entry, Mapping):
            _add(findings, f"readiness_dimension_entry_invalid:{index}")
            valid = False
            continue
        dimension_id = raw_entry.get("dimension_id")
        if not isinstance(dimension_id, str) or not dimension_id:
            _add(findings, f"readiness_dimension_id_missing:{index}")
            valid = False
            continue
        seen_ids.append(dimension_id)
        if dimension_id in entries:
            _add(findings, f"readiness_dimension_duplicate:{dimension_id}")
            valid = False
        entries[dimension_id] = raw_entry

    if tuple(seen_ids) != tuple(EXPECTED_DIMENSION_STATUSES):
        _add(findings, "readiness_dimension_order_or_coverage_invalid")
        valid = False
    if (
        set(entries) != set(EXPECTED_DIMENSION_STATUSES)
        or len(dimensions) != len(EXPECTED_DIMENSION_STATUSES)
    ):
        _add(findings, "readiness_dimension_coverage_incomplete")
        valid = False

    for dimension_id, expected_status in EXPECTED_DIMENSION_STATUSES.items():
        entry = entries.get(dimension_id)
        if entry is None:
            _add(findings, f"readiness_dimension_missing:{dimension_id}")
            continue
        missing_fields = DIMENSION_REQUIRED_FIELDS - set(entry)
        if missing_fields:
            for field in sorted(missing_fields):
                _add(findings, f"readiness_dimension_field_missing:{dimension_id}:{field}")
            valid = False

        status = entry.get("status")
        if status not in ALLOWED_READINESS_STATUSES:
            _add(findings, f"readiness_dimension_status_invalid:{dimension_id}")
            valid = False
        if status != expected_status:
            _add(findings, f"readiness_dimension_baseline_mismatch:{dimension_id}")
            valid = False
        if not isinstance(entry.get("required_evidence"), list) or not _as_list(
            entry.get("required_evidence")
        ):
            _add(findings, f"readiness_dimension_required_evidence_missing:{dimension_id}")
            valid = False
        if not isinstance(entry.get("observed_evidence"), list) or not _as_list(
            entry.get("observed_evidence")
        ):
            _add(findings, f"readiness_dimension_observed_evidence_missing:{dimension_id}")
            valid = False
        if not isinstance(entry.get("blocking_conditions"), list):
            _add(findings, f"readiness_dimension_blocking_conditions_invalid:{dimension_id}")
            valid = False
        if not isinstance(entry.get("reviewer_confirmation_required"), bool):
            _add(findings, f"readiness_dimension_reviewer_flag_invalid:{dimension_id}")
            valid = False
        if entry.get("authoritative_result") is not False:
            _add(findings, f"readiness_dimension_authority_violation:{dimension_id}")
            valid = False

    return valid, entries


def _dimension_matches_baseline(
    entries: Mapping[str, Mapping[str, Any]], dimension_id: str
) -> bool:
    entry = entries.get(dimension_id)
    return bool(
        entry
        and entry.get("status") == EXPECTED_DIMENSION_STATUSES[dimension_id]
        and isinstance(entry.get("required_evidence"), list)
        and bool(entry.get("required_evidence"))
        and isinstance(entry.get("observed_evidence"), list)
        and bool(entry.get("observed_evidence"))
        and entry.get("authoritative_result") is False
    )


def _validate_checklist(payload: Mapping[str, Any], findings: list[str]) -> bool:
    checklist = payload.get("operational_checklist")
    if not isinstance(checklist, list):
        _add(findings, "operational_checklist_invalid")
        return False

    valid = True
    ids: list[str] = []
    for index, raw_entry in enumerate(checklist):
        if not isinstance(raw_entry, Mapping):
            _add(findings, f"operational_checklist_entry_invalid:{index}")
            valid = False
            continue
        check_id = raw_entry.get("check_id")
        if not isinstance(check_id, str) or not check_id:
            _add(findings, f"operational_checklist_id_missing:{index}")
            valid = False
            continue
        ids.append(check_id)
        missing_fields = CHECKLIST_REQUIRED_FIELDS - set(raw_entry)
        if missing_fields:
            for field in sorted(missing_fields):
                _add(findings, f"operational_checklist_field_missing:{check_id}:{field}")
            valid = False
        if not _non_empty_string(raw_entry.get("description")):
            _add(findings, f"operational_checklist_description_missing:{check_id}")
            valid = False
        if not _non_empty_string(raw_entry.get("category")):
            _add(findings, f"operational_checklist_category_missing:{check_id}")
            valid = False
        if raw_entry.get("required") is not True:
            _add(findings, f"operational_checklist_not_required:{check_id}")
            valid = False
        if not isinstance(raw_entry.get("evidence_references"), list) or not raw_entry.get(
            "evidence_references"
        ):
            _add(findings, f"operational_checklist_evidence_missing:{check_id}")
            valid = False
        if check_id.startswith("check_32_"):
            expected_check_status = "reviewer_confirmation_required"
        elif check_id.startswith(("check_33_", "check_34_")):
            expected_check_status = "pending_next_stage"
        else:
            expected_check_status = "satisfied"
        if raw_entry.get("expected_status") != expected_check_status:
            _add(findings, f"operational_checklist_expected_status_invalid:{check_id}")
            valid = False
        if raw_entry.get("blocking_if_failed") is not True:
            _add(findings, f"operational_checklist_blocking_rule_invalid:{check_id}")
            valid = False
        if not _non_empty_string(raw_entry.get("governance_boundary")):
            _add(findings, f"operational_checklist_boundary_missing:{check_id}")
            valid = False

    if len(ids) != len(set(ids)):
        _add(findings, "operational_checklist_duplicate_id")
        valid = False
    for number in range(1, 37):
        prefix = f"check_{number:02d}_"
        if sum(check_id.startswith(prefix) for check_id in ids) != 1:
            _add(findings, f"operational_checklist_item_missing:{number:02d}")
            valid = False
    if len(checklist) < 36:
        _add(findings, "operational_checklist_coverage_incomplete")
        valid = False
    return valid


def _validate_external_state(payload: Mapping[str, Any], findings: list[str]) -> bool:
    external = payload.get("external_state_review_inputs")
    if not isinstance(external, Mapping):
        _add(findings, "external_state_review_inputs_invalid")
        return False
    valid = True
    for field, expected in EXPECTED_EXTERNAL_STATE.items():
        if external.get(field) != expected:
            _add(findings, f"external_state_boundary_invalid:{field}")
            valid = False
    if external.get("verified_by_deterministic_evaluator") is not False:
        _add(findings, "external_state_incorrectly_machine_verified")
        valid = False
    if external.get("reviewer_confirmation_required") is not True:
        _add(findings, "external_state_reviewer_confirmation_not_required")
        valid = False
    return valid


def _normalized_command(value: Any) -> str:
    return " ".join(str(value).split()) if isinstance(value, str) else ""


def _command_contains(command: str, fragments: Sequence[str]) -> bool:
    return all(fragment in command for fragment in fragments)


def _validate_command_manifest(
    payload: Mapping[str, Any], findings: list[str]
) -> bool:
    manifest = payload.get("verification_command_manifest")
    if not isinstance(manifest, list):
        _add(findings, "verification_command_manifest_invalid")
        return False

    valid = True
    entries: dict[str, Mapping[str, Any]] = {}
    seen_ids: list[str] = []
    for index, raw_entry in enumerate(manifest):
        if not isinstance(raw_entry, Mapping):
            _add(findings, f"verification_command_entry_invalid:{index}")
            valid = False
            continue
        command_id = raw_entry.get("command_id")
        if not isinstance(command_id, str) or not command_id:
            _add(findings, f"verification_command_id_missing:{index}")
            valid = False
            continue
        seen_ids.append(command_id)
        if command_id in entries:
            _add(findings, f"verification_command_duplicate:{command_id}")
            valid = False
        entries[command_id] = raw_entry

    if tuple(seen_ids) != REQUIRED_COMMAND_IDS:
        _add(findings, "verification_command_order_or_coverage_invalid")
        valid = False
    if set(entries) != set(REQUIRED_COMMAND_IDS) or len(manifest) != len(
        REQUIRED_COMMAND_IDS
    ):
        _add(findings, "verification_command_manifest_incomplete")
        valid = False

    for command_id in REQUIRED_COMMAND_IDS:
        entry = entries.get(command_id)
        if entry is None:
            _add(findings, f"verification_command_missing:{command_id}")
            continue
        missing_fields = COMMAND_REQUIRED_FIELDS - set(entry)
        if missing_fields:
            for field in sorted(missing_fields):
                _add(findings, f"verification_command_field_missing:{command_id}:{field}")
            valid = False
        command = _normalized_command(entry.get("command"))
        if not command:
            _add(findings, f"verification_command_text_missing:{command_id}")
            valid = False
        if not _non_empty_string(entry.get("verification_scope")):
            _add(findings, f"verification_scope_missing:{command_id}")
            valid = False
        if entry.get("expected_exit_code") != 0:
            _add(findings, f"verification_exit_code_invalid:{command_id}")
            valid = False
        if not _non_empty_string(entry.get("expected_result")):
            _add(findings, f"verification_expected_result_missing:{command_id}")
            valid = False
        if not _non_empty_string(entry.get("evidence_recording_requirement")):
            _add(findings, f"verification_evidence_requirement_missing:{command_id}")
            valid = False
        if entry.get("executed_by_readiness_evaluator") is not False:
            _add(findings, f"verification_manifest_execution_claim:{command_id}")
            valid = False
        for key, value in entry.items():
            if "executed" in _token(key) and _is_affirmative_claim_value(
                value, known_claim_key=True
            ):
                _add(findings, f"verification_manifest_execution_claim:{command_id}")
                valid = False

    fixture_command = _normalized_command(
        _as_mapping(entries.get("validate_readiness_fixture_json")).get("command")
    )
    if not _command_contains(
        fixture_command,
        (
            "python -m json.tool",
            "examples/public-integration-pack-pilot/m14-operational-readiness-fixtures.json",
        ),
    ):
        _add(findings, "json_validation_command_incomplete")
        valid = False

    evaluator_compile = _normalized_command(
        _as_mapping(entries.get("compile_m14_evaluators")).get("command")
    )
    if not _command_contains(
        evaluator_compile, ("python -m py_compile", *EVALUATOR_MODULE_PATHS)
    ):
        _add(findings, "evaluator_compile_command_incomplete")
        valid = False

    test_compile = _normalized_command(
        _as_mapping(entries.get("compile_m14_tests")).get("command")
    )
    if not _command_contains(test_compile, ("python -m py_compile", *TEST_MODULE_PATHS)):
        _add(findings, "test_compile_command_incomplete")
        valid = False

    merged_tests = _normalized_command(
        _as_mapping(entries.get("run_merged_m14_targeted_tests")).get("command")
    )
    if not _command_contains(
        merged_tests,
        ("python -X faulthandler -m unittest", *TARGETED_TEST_MODULES, "-v"),
    ):
        _add(findings, "merged_targeted_test_command_incomplete")
        valid = False

    readiness_tests = _normalized_command(
        _as_mapping(entries.get("run_operational_readiness_tests")).get("command")
    )
    if not _command_contains(
        readiness_tests,
        (
            "python -X faulthandler -m unittest",
            "tests.test_m14_operational_readiness_evaluator",
            "-v",
        ),
    ):
        _add(findings, "readiness_test_command_incomplete")
        valid = False

    for command_id in (
        "run_merged_m14_targeted_tests",
        "run_operational_readiness_tests",
    ):
        expected_result = str(
            _as_mapping(entries.get(command_id)).get("expected_result", "")
        ).lower()
        if "ran" not in expected_result or "ok" not in expected_result:
            _add(findings, f"unittest_expected_output_incomplete:{command_id}")
            valid = False

    diff_check = _normalized_command(
        _as_mapping(entries.get("git_diff_check")).get("command")
    )
    if "git diff --check" not in diff_check:
        _add(findings, "git_diff_check_command_incomplete")
        valid = False

    scope_check = _normalized_command(
        _as_mapping(entries.get("confirm_changed_file_scope")).get("command")
    )
    if "git diff --name-only" not in scope_check:
        _add(findings, "changed_file_scope_command_incomplete")
        valid = False
    return valid


def _validate_outstanding_items(
    payload: Mapping[str, Any], findings: list[str]
) -> bool:
    items = payload.get("outstanding_completion_items")
    if not isinstance(items, list):
        _add(findings, "outstanding_completion_items_invalid")
        return False

    valid = True
    item_ids = [
        item.get("item_id") if isinstance(item, Mapping) else None for item in items
    ]
    if tuple(item_ids) != EXPECTED_OUTSTANDING_ITEM_ORDER or len(items) != len(
        EXPECTED_OUTSTANDING_ITEM_ORDER
    ):
        _add(findings, "outstanding_completion_item_order_or_coverage_invalid")
        valid = False

    for index, expected_id in enumerate(EXPECTED_OUTSTANDING_ITEM_ORDER, start=1):
        if index > len(items) or not isinstance(items[index - 1], Mapping):
            _add(findings, f"outstanding_completion_item_missing:{expected_id}")
            valid = False
            continue
        item = items[index - 1]
        missing_fields = OUTSTANDING_REQUIRED_FIELDS - set(item)
        if missing_fields:
            for field in sorted(missing_fields):
                _add(findings, f"outstanding_item_field_missing:{expected_id}:{field}")
            valid = False
        if item.get("item_id") != expected_id:
            _add(findings, f"outstanding_item_id_invalid:{index}")
            valid = False
        if item.get("status") != "pending":
            _add(findings, f"outstanding_item_incorrectly_completed:{expected_id}")
            valid = False
        if item.get("sequence_order") != index:
            _add(findings, f"outstanding_item_sequence_invalid:{expected_id}")
            valid = False
        prerequisite = item.get("prerequisite")
        if index == 1:
            if not (
                _non_empty_string(prerequisite)
                or (isinstance(prerequisite, list) and bool(prerequisite))
            ):
                _add(findings, f"outstanding_item_prerequisite_missing:{expected_id}")
                valid = False
        elif EXPECTED_OUTSTANDING_ITEM_ORDER[index - 2] not in str(prerequisite):
            _add(findings, f"outstanding_item_prerequisite_invalid:{expected_id}")
            valid = False
        if not _non_empty_string(item.get("authorized_actor")):
            _add(findings, f"outstanding_item_authorized_actor_missing:{expected_id}")
            valid = False
        evidence = item.get("completion_evidence_required")
        if not (
            _non_empty_string(evidence)
            or (isinstance(evidence, list) and bool(evidence))
        ):
            _add(findings, f"outstanding_item_evidence_missing:{expected_id}")
            valid = False
        if item.get("not_performed_by_this_pr") is not True:
            _add(findings, f"outstanding_item_performed_by_this_pr:{expected_id}")
            valid = False
    return valid


def _validate_boundary_catalogs(
    payload: Mapping[str, Any], findings: list[str]
) -> bool:
    valid = True
    boundaries = _string_set(payload.get("required_boundary_statements"))
    for statement in sorted(REQUIRED_BOUNDARY_STATEMENTS - boundaries):
        _add(findings, f"required_boundary_statement_missing:{_token(statement)}")
        valid = False

    allowed = _string_set(payload.get("allowed_evaluator_outputs"))
    missing_allowed = REQUIRED_ALLOWED_OUTPUTS - allowed
    if missing_allowed:
        for output in sorted(missing_allowed):
            _add(findings, f"allowed_evaluator_output_missing:{output}")
        valid = False

    forbidden = _string_set(payload.get("forbidden_evaluator_outputs"))
    missing_forbidden = REQUIRED_FORBIDDEN_OUTPUTS - forbidden
    if missing_forbidden:
        for output in sorted(missing_forbidden):
            _add(findings, f"forbidden_evaluator_output_missing:{output}")
        valid = False

    overlap = allowed & REQUIRED_FORBIDDEN_OUTPUTS
    if overlap:
        for output in sorted(overlap):
            _add(findings, f"forbidden_output_in_allowed_catalog:{output}")
        valid = False

    policy = payload.get("forbidden_claim_inspection_policy")
    if not isinstance(policy, Mapping):
        _add(findings, "forbidden_claim_inspection_policy_invalid")
        return False

    for field, expected in FORBIDDEN_CLAIM_POLICY_VALUES.items():
        if policy.get(field) is not expected:
            _add(findings, f"forbidden_claim_policy_value_invalid:{field}")
            valid = False

    explicit_negative_states = policy.get(
        "explicit_negative_normalized_vocabulary"
    )
    if not isinstance(explicit_negative_states, list) or tuple(
        explicit_negative_states
    ) != EXPLICIT_NEGATIVE_CLAIM_STATES:
        _add(findings, "explicit_negative_vocabulary_invalid")
        valid = False

    authority_state_fields = policy.get("authority_state_fields")
    if not isinstance(authority_state_fields, list) or tuple(
        authority_state_fields
    ) != AUTHORITY_STATE_FIELD_ORDER:
        _add(findings, "authority_state_field_vocabulary_invalid")
        valid = False
    return valid


def _validate_readiness_cases(
    payload: Mapping[str, Any], findings: list[str]
) -> bool:
    cases = payload.get("readiness_cases")
    if not isinstance(cases, list):
        _add(findings, "readiness_cases_invalid")
        return False
    valid = True
    case_ids: list[str] = []
    for index, raw_case in enumerate(cases):
        if not isinstance(raw_case, Mapping):
            _add(findings, f"readiness_case_entry_invalid:{index}")
            valid = False
            continue
        case_id = raw_case.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            _add(findings, f"readiness_case_id_missing:{index}")
            valid = False
            continue
        case_ids.append(case_id)
        if not _non_empty_string(raw_case.get("description")):
            _add(findings, f"readiness_case_description_missing:{case_id}")
            valid = False

    if len(case_ids) != len(set(case_ids)):
        _add(findings, "readiness_case_duplicate_id")
        valid = False
    for number in range(1, 36):
        prefix = f"case_{number:02d}_"
        if sum(case_id.startswith(prefix) for case_id in case_ids) != 1:
            _add(findings, f"readiness_case_missing:{number:02d}")
            valid = False
    if len(cases) < 35:
        _add(findings, "readiness_case_coverage_incomplete")
        valid = False
    return valid


def _top_level_authority_boundaries_valid(payload: Mapping[str, Any]) -> bool:
    future_release = payload.get("future_release_tag_path")
    return bool(
        payload.get("m14_completion_status") == "active_work_not_complete"
        and isinstance(future_release, Mapping)
        and future_release.get("released") is False
        and all(payload.get(field) is False for field in REQUIRED_FALSE_TOP_LEVEL_FIELDS)
    )


def _build_outputs(
    *,
    valid: bool,
    source_track_coverage_complete: bool,
    source_artifacts_present: bool,
    artifact_integrity_valid: bool,
    authority_boundaries_preserved: bool,
    human_review_coverage_present: bool,
    fail_closed_recommendation_coverage_present: bool,
    rollback_recommendation_coverage_present: bool,
    trace_coverage_present: bool,
    replay_coverage_present: bool,
    verification_manifest_complete: bool,
    ready_for_release_proof_linkage: bool,
) -> list[str]:
    outputs = [
        "m14_operational_readiness_valid"
        if valid
        else "m14_operational_readiness_invalid",
        "source_track_coverage_complete"
        if source_track_coverage_complete
        else "source_track_coverage_incomplete",
    ]
    if not source_artifacts_present:
        outputs.append("source_artifact_missing")
    outputs.append(
        "artifact_integrity_valid"
        if artifact_integrity_valid
        else "artifact_integrity_invalid"
    )
    outputs.append(
        "authority_boundaries_preserved"
        if authority_boundaries_preserved
        else "authority_boundary_violation"
    )
    if human_review_coverage_present:
        outputs.append("human_review_coverage_present")
    if fail_closed_recommendation_coverage_present:
        outputs.append("fail_closed_coverage_present")
    if rollback_recommendation_coverage_present:
        outputs.append("rollback_coverage_present")
    if trace_coverage_present:
        outputs.append("trace_coverage_present")
    if replay_coverage_present:
        outputs.append("replay_coverage_present")
    outputs.append(
        "verification_manifest_complete"
        if verification_manifest_complete
        else "verification_manifest_incomplete"
    )
    outputs.extend(
        (
            "external_state_confirmation_required",
            "release_proof_linkage_pending",
            "readme_status_path_pending",
        )
    )
    if ready_for_release_proof_linkage:
        outputs.append("ready_for_release_proof_linkage")
    else:
        outputs.extend(("not_ready", "escalation_required"))
    return outputs


def evaluate_m14_operational_readiness(
    payload: dict[str, Any], repository_root: str | Path | None = None
) -> dict[str, Any]:
    """Evaluate M14 operational readiness without performing declared commands."""

    findings: list[str] = []
    if not isinstance(payload, dict):
        payload = {}
        _add(findings, "readiness_payload_invalid")
    root = _repository_root(repository_root)

    top_level_valid = _validate_top_level(payload, findings)
    tracks_valid, track_authority_valid, evidence_classes = _validate_tracks(
        payload, findings
    )
    artifacts_present, artifacts_valid = _validate_artifacts(payload, root, findings)
    dimensions_valid, dimensions = _validate_dimensions(payload, findings)
    checklist_valid = _validate_checklist(payload, findings)
    external_valid = _validate_external_state(payload, findings)
    command_manifest_valid = _validate_command_manifest(payload, findings)
    outstanding_valid = _validate_outstanding_items(payload, findings)
    boundary_catalogs_valid = _validate_boundary_catalogs(payload, findings)
    cases_valid = _validate_readiness_cases(payload, findings)

    claim_findings: list[str] = []
    _scan_forbidden_claims(payload, claim_findings)
    for finding in claim_findings:
        _add(findings, finding)
    no_affirmative_forbidden_claims = not claim_findings

    source_track_coverage_complete = bool(
        tracks_valid
        and _dimension_matches_baseline(dimensions, "source_track_coverage")
    )
    source_artifacts_present = bool(
        artifacts_present
        and _dimension_matches_baseline(dimensions, "source_artifact_presence")
    )
    artifact_integrity_valid = bool(
        artifacts_valid
        and _dimension_matches_baseline(dimensions, "source_artifact_integrity")
    )

    human_review_coverage_present = bool(
        "human_review" in evidence_classes
        and _dimension_matches_baseline(
            dimensions, "human_review_escalation_coverage"
        )
    )
    fail_closed_recommendation_coverage_present = bool(
        "fail_closed_recommendation" in evidence_classes
        and _dimension_matches_baseline(
            dimensions, "fail_closed_recommendation_coverage"
        )
    )
    rollback_recommendation_coverage_present = bool(
        "rollback_recommendation" in evidence_classes
        and _dimension_matches_baseline(
            dimensions, "rollback_recommendation_coverage"
        )
    )
    trace_coverage_present = bool(
        "trace_evidence" in evidence_classes
        and _dimension_matches_baseline(dimensions, "trace_evidence_coverage")
    )
    replay_coverage_present = bool(
        "replay_evidence" in evidence_classes
        and _dimension_matches_baseline(dimensions, "replay_evidence_coverage")
    )
    deterministic_coverage_present = bool(
        "deterministic_test" in evidence_classes
        and _dimension_matches_baseline(
            dimensions, "deterministic_evaluator_coverage"
        )
    )
    verification_manifest_complete = bool(
        command_manifest_valid
        and _dimension_matches_baseline(
            dimensions, "operational_verification_manifest"
        )
    )

    authority_boundaries_preserved = bool(
        track_authority_valid
        and boundary_catalogs_valid
        and no_affirmative_forbidden_claims
        and _top_level_authority_boundaries_valid(payload)
        and external_valid
        and outstanding_valid
        and _dimension_matches_baseline(
            dimensions, "decision_sovereignty_retention"
        )
        and _dimension_matches_baseline(
            dimensions, "runtime_capability_permission_boundary"
        )
        and _dimension_matches_baseline(dimensions, "consent_and_identity_boundary")
        and _dimension_matches_baseline(dimensions, "public_output_safety_boundary")
        and _dimension_matches_baseline(dimensions, "regulatory_mapping_boundary")
        and _dimension_matches_baseline(dimensions, "skill_supply_chain_boundary")
        and _dimension_matches_baseline(
            dimensions, "cross_control_authority_boundary"
        )
    )

    operational_components_ready = all(
        (
            source_track_coverage_complete,
            source_artifacts_present,
            artifact_integrity_valid,
            authority_boundaries_preserved,
            human_review_coverage_present,
            fail_closed_recommendation_coverage_present,
            rollback_recommendation_coverage_present,
            trace_coverage_present,
            replay_coverage_present,
            deterministic_coverage_present,
            verification_manifest_complete,
            outstanding_valid,
        )
    )

    structural_valid = all(
        (
            top_level_valid,
            tracks_valid,
            artifacts_present,
            artifacts_valid,
            dimensions_valid,
            checklist_valid,
            external_valid,
            command_manifest_valid,
            outstanding_valid,
            boundary_catalogs_valid,
            cases_valid,
            no_affirmative_forbidden_claims,
        )
    )
    valid = bool(structural_valid and operational_components_ready and not findings)
    ready_for_release_proof_linkage = bool(valid and operational_components_ready)

    outputs = _build_outputs(
        valid=valid,
        source_track_coverage_complete=source_track_coverage_complete,
        source_artifacts_present=source_artifacts_present,
        artifact_integrity_valid=artifact_integrity_valid,
        authority_boundaries_preserved=authority_boundaries_preserved,
        human_review_coverage_present=human_review_coverage_present,
        fail_closed_recommendation_coverage_present=fail_closed_recommendation_coverage_present,
        rollback_recommendation_coverage_present=rollback_recommendation_coverage_present,
        trace_coverage_present=trace_coverage_present,
        replay_coverage_present=replay_coverage_present,
        verification_manifest_complete=verification_manifest_complete,
        ready_for_release_proof_linkage=ready_for_release_proof_linkage,
    )

    return {
        "valid": valid,
        "source_track_coverage_complete": source_track_coverage_complete,
        "source_artifacts_present": source_artifacts_present,
        "artifact_integrity_valid": artifact_integrity_valid,
        "authority_boundaries_preserved": authority_boundaries_preserved,
        "human_review_coverage_present": human_review_coverage_present,
        "fail_closed_recommendation_coverage_present": fail_closed_recommendation_coverage_present,
        "rollback_recommendation_coverage_present": rollback_recommendation_coverage_present,
        "trace_coverage_present": trace_coverage_present,
        "replay_coverage_present": replay_coverage_present,
        "verification_manifest_complete": verification_manifest_complete,
        "external_state_confirmation_required": True,
        "outstanding_completion_items_valid": outstanding_valid,
        "ready_for_release_proof_linkage": ready_for_release_proof_linkage,
        "ready_for_m14_completion_review": False,
        "m14_complete": False,
        "findings": sorted(findings),
        "outputs": outputs,
    }


def validate_m14_operational_readiness(
    payload: dict[str, Any], repository_root: str | Path | None = None
) -> dict[str, Any]:
    """Validate a readiness payload and return the complete evaluation result."""

    return evaluate_m14_operational_readiness(payload, repository_root)


def evaluate_file(
    path: str | Path, repository_root: str | Path | None = None
) -> dict[str, Any]:
    """Load and evaluate a readiness fixture from disk."""

    return evaluate_m14_operational_readiness(
        load_fixture(path),
        repository_root,
    )
