"""Deterministic, data-only M14 release-proof-linkage evaluation.

This evaluator treats repository files and fixture content as inert evidence. It
recomputes SHA-256 digests, validates traceability, and reports review readiness.
It never imports source evaluators, runs declared commands or workflows, queries
GitHub, authorizes a release, or seals Decision Proof.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.repository_artifact_digest import (
    RepositoryArtifactFileTypeError,
    RepositoryArtifactPathError,
    RepositoryArtifactTextError,
    canonicalize_utf8_repository_text,
    sha256_repository_file,
)


EXPECTED_CHANGED_FILES = (
    "examples/public-integration-pack-pilot/m14-release-proof-linkage-specimen.json",
    "runtime/m14_release_proof_linkage_evaluator.py",
    "tests/test_m14_release_proof_linkage_evaluator.py",
)

EXPECTED_BUNDLE = (
    {
        "source_pr": "#212",
        "relative_path": (
            "examples/public-integration-pack-pilot/"
            "m14-operational-readiness-fixtures.json"
        ),
        "artifact_type": "fixture",
        "required": True,
        "sha256": "249d97afe928c6087f84f2b7bb061cbcf75f4a258341c18262bc5525b57317ae",
        "digest_algorithm": "sha256",
        "observed_on_branch": "main",
        "evidence_role": "operational_readiness_fixture_data",
        "executable_by_release_proof_evaluator": False,
    },
    {
        "source_pr": "#212",
        "relative_path": "runtime/m14_operational_readiness_evaluator.py",
        "artifact_type": "runtime_evaluator",
        "required": True,
        "sha256": "8a7a2b996cc2d7022c7456e044724e503d350d516f867caf3138f60615def1ff",
        "digest_algorithm": "sha256",
        "observed_on_branch": "main",
        "evidence_role": "operational_readiness_evaluator_source",
        "executable_by_release_proof_evaluator": False,
    },
    {
        "source_pr": "#212",
        "relative_path": "tests/test_m14_operational_readiness_evaluator.py",
        "artifact_type": "deterministic_test",
        "required": True,
        "sha256": "5b32b25bc225914283a3ee4a3dac6569d495e03c0726494120580c41cfc159b7",
        "digest_algorithm": "sha256",
        "observed_on_branch": "main",
        "evidence_role": "operational_readiness_test_source",
        "executable_by_release_proof_evaluator": False,
    },
)

# The fixture continues to record the three digests reviewed in PR #212.  The
# operational evaluator and its tests legitimately changed after that review,
# so their current canonical digests are maintained separately.  This is a
# deterministic phase-aware lookup, not an "old OR new" acceptance rule.
MAINTAINED_OPERATIONAL_READINESS_BUNDLE_SHA256_OVERRIDES = {
    "runtime/m14_operational_readiness_evaluator.py": (
        "d3c6e22ff3ab7a885378ba6732a1cf91879f801e39226b720e3fb847ac8bbffb"
    ),
    "tests/test_m14_operational_readiness_evaluator.py": (
        "00d8dbad46190020f50661f08c413d383d327be55c93c5d2313b8204eb131d5b"
    ),
}
MAINTAINED_OPERATIONAL_READINESS_BUNDLE_SHA256 = {
    entry["relative_path"]: MAINTAINED_OPERATIONAL_READINESS_BUNDLE_SHA256_OVERRIDES.get(
        entry["relative_path"], entry["sha256"]
    )
    for entry in EXPECTED_BUNDLE
}

EXPECTED_TRACKS: dict[str, dict[str, Any]] = {
    "voice_runtime_policy": {
        "source_pr": "#202",
        "component_role": "governed_voice_runtime_policy_gate",
        "source_paths": (
            "examples/public-integration-pack-pilot/voxcpm-governed-voice-fixtures.json",
            "runtime/voice_generation_policy_evaluator.py",
            "tests/test_voice_generation_policy_evaluator.py",
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
    },
}
EXPECTED_TRACK_ORDER = tuple(EXPECTED_TRACKS)

# These are the immutable source-artifact digests recorded by the historical
# operational-readiness fixture.  They are intentionally hardcoded here so a
# fixture mutation cannot silently redefine its own expected historical value.
HISTORICAL_SOURCE_ARTIFACT_SHA256 = {
    "examples/public-integration-pack-pilot/voxcpm-governed-voice-fixtures.json": (
        "f2d30aca2abca68e0d69080098c473ff2ef7f45a5afae0eb2734dd48ae294921"
    ),
    "runtime/voice_generation_policy_evaluator.py": (
        "6c6a10fc88b1abd6f35ae3993b27784fbe69d028d192e19275677296e21df84f"
    ),
    "tests/test_voice_generation_policy_evaluator.py": (
        "0d2e3921ed4e7060615bfbc2ae0c192616b20990834e5be5a3663c78b19a0d4e"
    ),
    "examples/public-integration-pack-pilot/m14-public-issue-exfiltration-gate-fixtures.json": (
        "ac682908ba081cfc58726046efcb928c51e64eb2037f03354fda80afeb0846a9"
    ),
    "runtime/public_issue_exfiltration_gate_evaluator.py": (
        "f3453af5c1829a28c791b665640e24940ececdc211e364360635bfe39573e81d"
    ),
    "tests/test_public_issue_exfiltration_gate_evaluator.py": (
        "e3ab2be88dfeb8ec85a9cd12936f33b54476e46c22eeebe650648a8678d962bc"
    ),
    "docs/public-integration-pack/m14-moda-ai-risk-framework-mapping.md": (
        "d28987ceeb419d36f43e32f9fba6fa82c7233ce3355117ebac5f9c45cfae97a3"
    ),
    "examples/public-integration-pack-pilot/m14-moda-ai-risk-decision-proof-fixtures.json": (
        "dc157dd2029912ffe7d2ed48485c6b6e603237a9aa2cca72bb8d12ba285ff2ba"
    ),
    "runtime/moda_ai_risk_mapping_evaluator.py": (
        "11a71ee8a7a7120d798e5cbb262a9e98bb9b1e74ca2471db486d6bdd0d091f28"
    ),
    "tests/test_moda_ai_risk_mapping_evaluator.py": (
        "96a52094a65a2cd9303a01aa62b2e53c5240fdc789ee005c243a44a627fc3564"
    ),
    ".github/workflows/m14-ai-pr-provenance.yml": (
        "af8ba9426f1bda5c2b9a09fad7a2b03ef2c4d04a178e4f414519bf837ff19bf1"
    ),
    "examples/public-integration-pack-pilot/m14-ai-authored-pr-provenance-fixtures.json": (
        "e72636d1871f2c1232c811aec41ca9724be1505916d4804a05be75e600f3808a"
    ),
    "runtime/ai_authored_pr_provenance_evaluator.py": (
        "465a0aba8beb49a6d6ad55e0bfce65ab74f5368164c758841ab202c50432ef35"
    ),
    "tests/test_ai_authored_pr_provenance_evaluator.py": (
        "e648d2606d38f05063d72be0fa270a0191a28dca24a5fc07e80414faa4fc1f8f"
    ),
    "docs/capability-supply-chain/nvidia-skills-admission.md": (
        "f49b51dd960df118a002c7e3fef685bf39f4006f8372373c0cb1fa7b635f8f49"
    ),
    "examples/public-integration-pack-pilot/m14-skill-admission-fixtures.json": (
        "4fc229be3883a2681f8ebfc3f2eb828514cd3a2d6729c5841bab5a7efe609509"
    ),
    "runtime/skill_admission_evaluator.py": (
        "bb81697df1be79b96a6af373ce63314a01ac73392b3cdb97981abaddbe6a4400"
    ),
    "tests/test_skill_admission_evaluator.py": (
        "7cfd8b7f801a9a9da0546ae64499b234cbd1882fbba64b7a169b01b866ec6abd"
    ),
    "examples/public-integration-pack-pilot/m14-cross-control-authority-boundary-regression-fixtures.json": (
        "f44b6d3298922608096c10f248955fa4c25e8d4a3452d6d7c585f9237129809d"
    ),
    "runtime/m14_cross_control_authority_boundary_evaluator.py": (
        "51a413dc5303d64d49e958ffde970925ffc5aebead3435f8cf714e6112e1b48c"
    ),
    "tests/test_m14_cross_control_authority_boundary_evaluator.py": (
        "5a4a5e764655382e2b19aa5a4e8a5a6a2b5082ade733e7125d88dfd2ba6cfc52"
    ),
}

# Legitimate post-review source changes are explicit here and never rewrite
# HISTORICAL_SOURCE_ARTIFACT_SHA256.
MAINTAINED_SOURCE_ARTIFACT_SHA256_OVERRIDES: dict[str, str] = {
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
MAINTAINED_SOURCE_ARTIFACT_SHA256 = {
    relative_path: MAINTAINED_SOURCE_ARTIFACT_SHA256_OVERRIDES.get(
        relative_path, historical_digest
    )
    for relative_path, historical_digest in HISTORICAL_SOURCE_ARTIFACT_SHA256.items()
}

EXPECTED_TOP_LEVEL = {
    "artifact_id": "m14-release-proof-linkage-specimen",
    "artifact_name": "M14 Release Proof Linkage Specimen",
    "artifact_scope": (
        "high_risk_runtime_policy_and_public_output_safety_future_release_traceability"
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
    "prior_released_baseline": "v0.12.0",
    "introduced_after_release": "v0.12.0",
    "target_future_release": "v0.13.0",
    "release_proof_linkage_state": "evidence_linkage_complete_for_review",
}

REQUIRED_FALSE_TOP_LEVEL = (
    "tracker_state_changed_by_fixture",
    "ready_for_m14_completion_review",
    "readme_status_updated",
    "release_file_created",
    "release_tag_created",
    "github_release_created",
    "release_notes_finalized",
    "release_notes_published",
    "release_approved",
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
}

REQUIRED_BOUNDARY_STATEMENTS = (
    "Release proof linkage is evidence linkage only.",
    "Release proof linkage is not release approval.",
    "Operational readiness is not release authorization.",
    "Artifact presence is not evidence sufficiency.",
    "Artifact digest matching is not governance approval.",
    "A merged source PR reference is not release approval.",
    "A verification-command manifest is not proof that commands ran.",
    (
        "External GitHub state is reviewer-confirmed evidence, "
        "not machine-verified by this evaluator."
    ),
    "release_proof_complete is not released.",
    "release_ready_for_review is not release_approved.",
    "ready_for_future_readme_status_path is not README authorization.",
    "Future release target is not released.",
    "v0.13.0 is not released.",
    "M14 remains active work and not complete.",
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
    "m14_release_proof_linkage_valid",
    "m14_release_proof_linkage_invalid",
    "release_linkage_coverage_complete",
    "release_linkage_coverage_incomplete",
    "operational_readiness_bundle_valid",
    "operational_readiness_bundle_invalid",
    "source_artifact_integrity_valid",
    "source_artifact_integrity_invalid",
    "authority_boundaries_preserved",
    "authority_boundary_violation",
    "external_state_confirmation_required",
    "release_proof_complete",
    "release_ready_for_review",
    "ready_for_future_readme_status_path",
    "review_required",
    "escalation_required",
    "fail_closed_recommended",
    "not_ready",
}

REQUIRED_FORBIDDEN_OUTPUTS = {
    "release_approved",
    "release_created",
    "release_tag_created",
    "release_notes_finalized",
    "release_notes_published",
    "v0_13_0_released",
    "release_published",
    "readme_update_approved",
    "m14_completion_approved",
    "tracker_201_final_state_applied",
    "risk_accepted",
    "fail_closed_executed",
    "rollback_executed",
    "audit_closed",
    "waiver_granted",
    "decision_proof_verified",
    "decision_proof_sealed",
    "sealed_by_release_proof",
    "sealed_by_evaluator",
    "authority_transferred",
    "final_governance_judgment",
    "m14_complete",
}

EXPECTED_COMMANDS = (
    (
        "git_diff_check",
        "git diff --check",
    ),
    (
        "validate_release_proof_fixture_json",
        "python -m json.tool examples/public-integration-pack-pilot/"
        "m14-release-proof-linkage-specimen.json",
    ),
    (
        "compile_release_proof_evaluator",
        "python -m py_compile runtime/m14_release_proof_linkage_evaluator.py",
    ),
    (
        "compile_release_proof_tests",
        "python -m py_compile tests/test_m14_release_proof_linkage_evaluator.py",
    ),
    (
        "run_merged_m14_targeted_tests",
        "python -X faulthandler -m unittest "
        "tests.test_voice_generation_policy_evaluator "
        "tests.test_public_issue_exfiltration_gate_evaluator "
        "tests.test_moda_ai_risk_mapping_evaluator "
        "tests.test_ai_authored_pr_provenance_evaluator "
        "tests.test_skill_admission_evaluator "
        "tests.test_m14_cross_control_authority_boundary_evaluator -v",
    ),
    (
        "run_operational_readiness_tests",
        "python -X faulthandler -m unittest "
        "tests.test_m14_operational_readiness_evaluator -v",
    ),
    (
        "run_release_proof_linkage_tests",
        "python -X faulthandler -m unittest "
        "tests.test_m14_release_proof_linkage_evaluator -v",
    ),
    (
        "confirm_changed_file_scope",
        "git diff --name-only",
    ),
)

EXPECTED_OUTSTANDING_ORDER = (
    "future_readme_status_path",
    "final_m14_completion_review",
    "tracker_issue_201_final_state_transition",
    "publish_v0_13_0_release",
)

AUTHORITY_STATE_FIELDS = {
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
}

EXPLICIT_NEGATIVE_STRINGS = {
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
}

FORBIDDEN_AUTHORITY_KEYS = REQUIRED_FORBIDDEN_OUTPUTS | {
    "tag_created",
    "github_release_created",
    "release_file_created",
    "readme_status_updated",
    "ready_for_m14_completion_review",
    "risk_accepted_by_fixture",
    "fail_closed_executed_by_fixture",
    "rollback_executed_by_fixture",
    "audit_closed_by_fixture",
    "authority_transferred_by_fixture",
    "final_governance_judgment_made_by_fixture",
    "decision_proof_sealed_by_fixture",
    "tracker_state_changed_by_fixture",
    "release_authority_granted",
    "grants_current_release_authority",
}

CLAIM_SCAN_SKIP_KEYS = {
    "forbidden_evaluator_outputs",
}

REQUIRED_AUTHORITY_MAY = {
    "link_artifacts",
    "validate_paths",
    "recompute_sha256_digests",
    "inspect_inert_evidence",
    "report_coverage",
    "preserve_traceability",
    "route_findings_for_review",
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
    "publish_v0_13_0",
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


def _token(value: Any) -> str:
    text = str(value).strip().lower()
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_")


def _repository_root(repository_root: str | Path | None) -> Path:
    if repository_root is None:
        return Path(__file__).resolve().parents[1]
    # Keep a supplied root lexical here.  The shared digest utility requires
    # an absolute root and performs the authoritative strict resolution, so a
    # relative root is never interpreted through the process working directory.
    return Path(repository_root)


def _canonical_text_digest(
    root: Path,
    relative_path: str,
    findings: list[str],
    *,
    finding_prefix: str,
) -> tuple[str | None, str]:
    try:
        return sha256_repository_file(root, relative_path, mode="text"), "ok"
    except FileNotFoundError:
        _add(findings, f"{finding_prefix}_file_missing:{relative_path}")
        status = "missing"
    except UnicodeDecodeError:
        _add(findings, f"{finding_prefix}_malformed_utf8:{relative_path}")
        status = "malformed_utf8"
    except RepositoryArtifactTextError:
        _add(findings, f"{finding_prefix}_lone_carriage_return:{relative_path}")
        status = "lone_carriage_return"
    except (RepositoryArtifactPathError, RepositoryArtifactFileTypeError):
        _add(findings, f"{finding_prefix}_path_invalid:{relative_path}")
        status = "path_invalid"
    except OSError:
        _add(findings, f"{finding_prefix}_unreadable:{relative_path}")
        status = "unreadable"
    return None, status


def load_fixture(path: str | Path) -> dict[str, Any]:
    """Load one UTF-8 JSON fixture as inert data."""

    with Path(path).open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("release-proof fixture must contain a JSON object")
    return payload


def _validate_top_level(
    payload: Mapping[str, Any], findings: list[str]
) -> tuple[bool, bool]:
    valid = True
    for field, expected in EXPECTED_TOP_LEVEL.items():
        if payload.get(field) != expected:
            _add(findings, f"top_level_value_invalid:{field}")
            valid = False

    for field in REQUIRED_FALSE_TOP_LEVEL:
        if payload.get(field) is not False:
            _add(findings, f"top_level_false_boundary_invalid:{field}")
            valid = False

    for field in (
        "release_proof_complete",
        "release_ready_for_review",
        "ready_for_future_readme_status_path",
    ):
        if payload.get(field) is not True:
            _add(findings, f"top_level_review_state_invalid:{field}")
            valid = False

    if tuple(payload.get("changed_file_scope", ())) != EXPECTED_CHANGED_FILES:
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
    expected_future = {
        "target_tag": "v0.13.0",
        "state": "future_tag_path_only",
        "released": False,
        "tag_created": False,
        "github_release_created": False,
        "release_notes_finalized": False,
        "release_notes_published": False,
        "boundary": "Future release target is not released.",
    }
    if future != expected_future:
        _add(findings, "future_release_tag_path_invalid")
        valid = False

    status = _as_mapping(payload.get("release_status_path"))
    expected_status = {
        "state": "future_release_target_not_released",
        "prior_released_baseline": "v0.12.0",
        "target_future_release": "v0.13.0",
        "release_proof_complete": True,
        "release_ready_for_review": True,
        "release_approved": False,
        "released": False,
        "readme_status_updated": False,
        "m14_complete": False,
    }
    if status != expected_status:
        _add(findings, "release_status_path_invalid")
        valid = False

    refs_valid = _as_mapping(payload.get("release_linkage_refs")) == EXPECTED_LINKAGE_REFS
    if not refs_valid:
        _add(findings, "release_linkage_refs_invalid")
        valid = False

    required_containers = {
        "operational_readiness_bundle": list,
        "source_track_linkage": list,
        "source_artifact_verification": dict,
        "release_evidence_packet": dict,
        "external_state_review_inputs": dict,
        "verification_command_manifest": list,
        "outstanding_completion_items": list,
        "release_proof_cases": list,
        "required_boundary_statements": list,
        "semantic_boundaries": dict,
        "allowed_evaluator_outputs": list,
        "forbidden_evaluator_outputs": list,
        "forbidden_claim_inspection_policy": dict,
        "authority_boundary": dict,
    }
    for field, expected_type in required_containers.items():
        if not isinstance(payload.get(field), expected_type):
            _add(findings, f"container_type_invalid:{field}")
            valid = False
    return valid, refs_valid


def _validate_operational_readiness_bundle(
    payload: Mapping[str, Any], root: Path, findings: list[str]
) -> tuple[bool, bool, bool, bool, dict[str, Any] | None]:
    entries = payload.get("operational_readiness_bundle")
    present = isinstance(entries, list) and len(entries) == len(EXPECTED_BUNDLE)
    integrity_valid = present
    historical_digest_valid = present
    maintained_digest_valid = present

    if not isinstance(entries, list):
        entries = []
        _add(findings, "operational_readiness_bundle_invalid")
    elif len(entries) != len(EXPECTED_BUNDLE):
        _add(findings, "operational_readiness_bundle_coverage_invalid")

    digest_statuses: dict[str, str] = {}
    for index, expected in enumerate(EXPECTED_BUNDLE):
        raw = entries[index] if index < len(entries) else None
        if not isinstance(raw, Mapping):
            _add(findings, f"operational_readiness_bundle_entry_missing:{index}")
            present = False
            integrity_valid = False
            historical_digest_valid = False
            continue

        for field, expected_value in expected.items():
            if raw.get(field) != expected_value:
                _add(
                    findings,
                    f"operational_readiness_bundle_field_invalid:{index}:{field}",
                )
                integrity_valid = False
                if field == "relative_path":
                    present = False
                if field == "sha256":
                    historical_digest_valid = False
                    _add(
                        findings,
                        "operational_readiness_bundle_historical_digest_mismatch:"
                        f"{expected['relative_path']}",
                    )

        relative_path = expected["relative_path"]
        observed_digest, digest_status = _canonical_text_digest(
            root,
            relative_path,
            findings,
            finding_prefix="operational_readiness_bundle",
        )
        digest_statuses[relative_path] = digest_status
        if observed_digest is None:
            if digest_status in {"missing", "path_invalid"}:
                present = False
            integrity_valid = False
            maintained_digest_valid = False
        elif (
            observed_digest
            != MAINTAINED_OPERATIONAL_READINESS_BUNDLE_SHA256[relative_path]
        ):
            _add(
                findings,
                "operational_readiness_bundle_maintained_digest_mismatch:"
                f"{relative_path}",
            )
            integrity_valid = False
            maintained_digest_valid = False

    readiness_relative_path = EXPECTED_BUNDLE[0]["relative_path"]
    readiness_payload: dict[str, Any] | None = None
    if digest_statuses.get(readiness_relative_path) == "ok":
        try:
            readiness_path = root.joinpath(*readiness_relative_path.split("/")).resolve(
                strict=True
            )
            canonical = canonicalize_utf8_repository_text(readiness_path.read_bytes())
            loaded = json.loads(canonical.decode("utf-8", errors="strict"))
            if isinstance(loaded, dict):
                readiness_payload = loaded
            else:
                _add(findings, "operational_readiness_fixture_not_object")
                integrity_valid = False
        except (OSError, UnicodeError, RepositoryArtifactTextError, json.JSONDecodeError):
            _add(findings, "operational_readiness_fixture_unreadable")
            integrity_valid = False
    return (
        present,
        integrity_valid,
        historical_digest_valid,
        maintained_digest_valid,
        readiness_payload,
    )


def _readiness_dimensions(readiness: Mapping[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    dimensions = readiness.get("readiness_dimensions")
    if isinstance(dimensions, list):
        for item in dimensions:
            if isinstance(item, Mapping):
                dimension_id = item.get("dimension_id")
                status = item.get("status")
                if isinstance(dimension_id, str) and isinstance(status, str):
                    result[dimension_id] = status
    return result


def _validate_readiness_state(
    readiness: Mapping[str, Any] | None, findings: list[str]
) -> bool:
    if not isinstance(readiness, Mapping):
        _add(findings, "operational_readiness_fixture_missing")
        return False

    valid = True
    expected = {
        "fixture_status": "m14_active_work_not_complete",
        "tracker_issue": "#201",
        "tracker_issue_linkage": "Refs #201",
        "m14_completion_status": "active_work_not_complete",
        "target_future_release": "v0.13.0",
    }
    for field, value in expected.items():
        if readiness.get(field) != value:
            _add(findings, f"readiness_state_invalid:{field}")
            valid = False

    future = _as_mapping(readiness.get("future_release_tag_path"))
    if future.get("target_tag") != "v0.13.0" or future.get("released") is not False:
        _add(findings, "readiness_future_release_state_invalid")
        valid = False

    external = _as_mapping(readiness.get("external_state_review_inputs"))
    if (
        external.get("tracker_issue") != "#201"
        or external.get("tracker_expected_state") != "open"
        or external.get("verified_by_deterministic_evaluator") is not False
        or external.get("reviewer_confirmation_required") is not True
    ):
        _add(findings, "readiness_external_state_invalid")
        valid = False

    dimensions = _readiness_dimensions(readiness)
    expected_dimensions = {
        "release_proof_linkage_status": "pending_next_stage",
        "readme_future_status_path": "pending_next_stage",
        "tracker_completion_status": "pending_next_stage",
    }
    for dimension_id, status in expected_dimensions.items():
        if dimensions.get(dimension_id) != status:
            _add(findings, f"readiness_pending_stage_invalid:{dimension_id}")
            valid = False

    outstanding = readiness.get("outstanding_completion_items")
    required_pending = (
        ("release_proof_linkage", 1),
        ("future_readme_status_path", 2),
        ("final_m14_completion_review", 3),
    )
    if not isinstance(outstanding, list):
        _add(findings, "readiness_outstanding_items_invalid")
        valid = False
    else:
        by_id = {
            item.get("item_id"): item for item in outstanding if isinstance(item, Mapping)
        }
        for item_id, order in required_pending:
            item = _as_mapping(by_id.get(item_id))
            if item.get("status") != "pending" or item.get("sequence_order") != order:
                _add(findings, f"readiness_outstanding_item_invalid:{item_id}")
                valid = False

    baseline = _as_mapping(readiness.get("expected_baseline_result"))
    for field, expected_value in {
        "ready_for_release_proof_linkage": True,
        "ready_for_m14_completion_review": False,
        "m14_complete": False,
    }.items():
        if baseline.get(field) is not expected_value:
            _add(findings, f"readiness_expected_result_invalid:{field}")
            valid = False

    if readiness.get("verification_manifest_execution_claimed") is not False:
        _add(findings, "readiness_verification_execution_claimed")
        valid = False
    commands = readiness.get("verification_command_manifest")
    if not isinstance(commands, list) or any(
        not isinstance(command, Mapping)
        or command.get("executed_by_readiness_evaluator") is not False
        for command in commands
    ):
        _add(findings, "readiness_command_manifest_execution_claimed")
        valid = False
    return valid


def _validate_source_track_linkage(
    payload: Mapping[str, Any],
    readiness: Mapping[str, Any] | None,
    findings: list[str],
) -> bool:
    release_tracks = payload.get("source_track_linkage")
    readiness_tracks = (
        readiness.get("source_track_manifest") if isinstance(readiness, Mapping) else None
    )
    if not isinstance(release_tracks, list) or not isinstance(readiness_tracks, list):
        _add(findings, "source_track_linkage_invalid")
        return False

    valid = True
    if len(release_tracks) != 6:
        _add(findings, "source_track_linkage_count_invalid")
        valid = False
    if len(readiness_tracks) != 6:
        _add(findings, "readiness_source_track_count_invalid")
        valid = False

    for index, track_id in enumerate(EXPECTED_TRACK_ORDER):
        expected = EXPECTED_TRACKS[track_id]
        release_track = release_tracks[index] if index < len(release_tracks) else {}
        readiness_track = readiness_tracks[index] if index < len(readiness_tracks) else {}
        if not isinstance(release_track, Mapping):
            release_track = {}
        if not isinstance(readiness_track, Mapping):
            readiness_track = {}

        expected_paths = expected["source_paths"]
        implementation_paths = expected_paths[:-1]
        deterministic_test_path = expected_paths[-1]
        expected_linkage_path = (
            "examples/public-integration-pack-pilot/"
            "m14-operational-readiness-fixtures.json#/source_track_manifest/"
            f"{index}"
        )

        readiness_expectations = {
            "track_id": track_id,
            "source_pr": expected["source_pr"],
            "component_role": expected["component_role"],
            "source_paths": list(expected_paths),
            "retained_authority_owner": "AAOS",
            "decision_proof_sealing_owner": "AAOS",
        }
        for field, expected_value in readiness_expectations.items():
            if readiness_track.get(field) != expected_value:
                _add(findings, f"readiness_source_track_mismatch:{track_id}:{field}")
                valid = False

        release_expectations = {
            "track_id": track_id,
            "source_pr": expected["source_pr"],
            "component_role": expected["component_role"],
            "readiness_linkage_path": expected_linkage_path,
            "implementation_artifact_paths": list(implementation_paths),
            "deterministic_test_path": deterministic_test_path,
            "retained_authority_owner": "AAOS",
            "decision_proof_sealing_owner": "AAOS",
            "release_authority_granted": False,
        }
        for field, expected_value in release_expectations.items():
            if release_track.get(field) != expected_value:
                _add(findings, f"source_track_linkage_mismatch:{track_id}:{field}")
                valid = False
        role = release_track.get("release_evidence_role")
        if not isinstance(role, str) or not role:
            _add(findings, f"source_track_release_evidence_role_missing:{track_id}")
            valid = False

    all_source_prs = [
        track.get("source_pr")
        for track in release_tracks
        if isinstance(track, Mapping)
    ]
    if "#209" in all_source_prs:
        _add(findings, "adjacent_pr_209_in_source_track_manifest")
        valid = False
    return valid


def _validate_source_artifacts(
    readiness: Mapping[str, Any] | None,
    root: Path,
    findings: list[str],
) -> tuple[bool, bool, bool]:
    if not isinstance(readiness, Mapping):
        _add(findings, "source_artifact_manifest_unavailable")
        return False, False, False
    manifest = readiness.get("source_artifact_manifest")
    if not isinstance(manifest, list):
        _add(findings, "source_artifact_manifest_invalid")
        return False, False, False

    expected_paths: dict[str, tuple[str, str]] = {}
    for track_id, track in EXPECTED_TRACKS.items():
        for path in track["source_paths"]:
            expected_paths[path] = (track_id, track["source_pr"])

    valid = True
    historical_digest_valid = True
    maintained_digest_valid = True
    if set(HISTORICAL_SOURCE_ARTIFACT_SHA256) != set(expected_paths):
        _add(findings, "historical_source_artifact_digest_catalog_invalid")
        valid = False
        historical_digest_valid = False
    if set(MAINTAINED_SOURCE_ARTIFACT_SHA256) != set(expected_paths):
        _add(findings, "maintained_source_artifact_digest_catalog_invalid")
        valid = False
        maintained_digest_valid = False
    if len(manifest) != len(expected_paths):
        _add(findings, "source_artifact_manifest_count_invalid")
        valid = False
        historical_digest_valid = False

    by_path: dict[str, Mapping[str, Any]] = {}
    for entry in manifest:
        if not isinstance(entry, Mapping):
            _add(findings, "source_artifact_manifest_entry_invalid")
            valid = False
            continue
        relative_path = entry.get("relative_path")
        if not isinstance(relative_path, str) or relative_path in by_path:
            _add(findings, "source_artifact_manifest_path_duplicate_or_invalid")
            valid = False
            continue
        by_path[relative_path] = entry

    if set(by_path) != set(expected_paths):
        _add(findings, "source_artifact_manifest_path_set_invalid")
        valid = False
        historical_digest_valid = False

    for relative_path, (track_id, source_pr) in expected_paths.items():
        entry = _as_mapping(by_path.get(relative_path))
        if not entry:
            _add(findings, f"source_artifact_missing_from_manifest:{relative_path}")
            valid = False
            historical_digest_valid = False
        else:
            expectations = {
                "track_id": track_id,
                "source_pr": source_pr,
                "relative_path": relative_path,
                "required": True,
                "digest_algorithm": "sha256",
                "observed_on_branch": "main",
                "executable_by_readiness_evaluator": False,
            }
            for field, expected_value in expectations.items():
                if entry.get(field) != expected_value:
                    _add(
                        findings,
                        f"source_artifact_binding_invalid:{relative_path}:{field}",
                    )
                    valid = False

            if not isinstance(entry.get("artifact_type"), str) or not entry.get(
                "artifact_type"
            ):
                _add(findings, f"source_artifact_type_missing:{relative_path}")
                valid = False
            if not isinstance(entry.get("evidence_role"), str) or not entry.get(
                "evidence_role"
            ):
                _add(findings, f"source_artifact_evidence_role_missing:{relative_path}")
                valid = False

            recorded_digest = entry.get("sha256")
            if not isinstance(recorded_digest, str) or not re.fullmatch(
                r"[0-9a-f]{64}", recorded_digest
            ):
                _add(findings, f"source_artifact_digest_invalid:{relative_path}")
                valid = False
                historical_digest_valid = False
            elif recorded_digest != HISTORICAL_SOURCE_ARTIFACT_SHA256[relative_path]:
                _add(
                    findings,
                    f"source_artifact_historical_digest_mismatch:{relative_path}",
                )
                valid = False
                historical_digest_valid = False

        observed_digest, _ = _canonical_text_digest(
            root,
            relative_path,
            findings,
            finding_prefix="source_artifact",
        )
        if observed_digest is None:
            valid = False
            maintained_digest_valid = False
        elif observed_digest != MAINTAINED_SOURCE_ARTIFACT_SHA256[relative_path]:
            _add(
                findings,
                f"source_artifact_maintained_digest_mismatch:{relative_path}",
            )
            valid = False
            maintained_digest_valid = False
    return valid, historical_digest_valid, maintained_digest_valid


def _validate_source_artifact_policy(
    payload: Mapping[str, Any], findings: list[str]
) -> bool:
    policy = _as_mapping(payload.get("source_artifact_verification"))
    expected_scalars = {
        "operational_readiness_fixture_path": EXPECTED_BUNDLE[0]["relative_path"],
        "source_track_manifest_reference": "#/source_track_manifest",
        "source_artifact_manifest_reference": "#/source_artifact_manifest",
        "load_mode": "data_only",
        "required_source_track_count": 6,
        "required_source_artifact_count": 21,
        "import_operational_readiness_evaluator": False,
        "execute_operational_readiness_tests": False,
        "execute_source_evaluators": False,
        "execute_workflows": False,
        "execute_skills": False,
        "execute_models": False,
        "perform_network_access": False,
        "execute_shell_commands_from_fixture": False,
    }
    valid = True
    for field, expected in expected_scalars.items():
        if policy.get(field) != expected:
            _add(findings, f"source_artifact_policy_invalid:{field}")
            valid = False

    required_checks = {
        "exact_six_source_tracks",
        "all_required_source_artifact_paths_exist",
        "all_embedded_source_artifact_sha256_digests_match",
        "all_source_artifacts_non_executable_by_readiness_evaluator",
        "all_tracks_retain_AAOS_authority",
        "all_tracks_retain_AAOS_decision_proof_sealing",
        "tracker_expected_state_open",
        "v0_13_0_unreleased",
        "release_proof_linkage_pending_next_stage",
        "readme_status_path_pending",
        "final_m14_completion_review_pending",
    }
    if _string_set(policy.get("required_checks")) != required_checks:
        _add(findings, "source_artifact_policy_checks_invalid")
        valid = False
    return valid


def _validate_release_evidence_packet(
    payload: Mapping[str, Any], findings: list[str]
) -> bool:
    packet = _as_mapping(payload.get("release_evidence_packet"))
    expected_scalars = {
        "milestone": "M14",
        "future_release": "v0.13.0",
        "prior_release_baseline": "v0.12.0",
        "tracker_reference": "#201",
        "operational_readiness_pr": "#212",
        "source_artifact_manifest_reference": (
            "examples/public-integration-pack-pilot/"
            "m14-operational-readiness-fixtures.json#/source_artifact_manifest"
        ),
        "source_artifact_integrity_status": "valid",
        "authority_boundary_status": "preserved",
        "external_state_confirmation_requirement": "reviewer_required",
        "release_proof_linkage_status": "complete_for_review",
        "release_ready_for_review": True,
        "release_approved": False,
        "released": False,
        "decision_proof_sealed": False,
        "governance_role": "traceability_packet_only_not_release_approval",
    }
    valid = True
    for field, expected in expected_scalars.items():
        if packet.get(field) != expected:
            _add(findings, f"release_evidence_packet_invalid:{field}")
            valid = False

    if packet.get("source_pr_references") != [
        "#202",
        "#204",
        "#205",
        "#206",
        "#208",
        "#210",
    ]:
        _add(findings, "release_evidence_source_pr_references_invalid")
        valid = False

    expected_digests = [
        {"relative_path": entry["relative_path"], "sha256": entry["sha256"]}
        for entry in EXPECTED_BUNDLE
    ]
    if packet.get("operational_readiness_bundle_digests") != expected_digests:
        _add(findings, "release_evidence_bundle_digests_invalid")
        valid = False

    expected_tests = [
        spec["source_paths"][-1] for spec in EXPECTED_TRACKS.values()
    ] + [
        "tests/test_m14_operational_readiness_evaluator.py",
        "tests/test_m14_release_proof_linkage_evaluator.py",
    ]
    if packet.get("deterministic_test_manifest") != expected_tests:
        _add(findings, "release_evidence_test_manifest_invalid")
        valid = False
    if packet.get("outstanding_completion_sequence") != list(
        EXPECTED_OUTSTANDING_ORDER
    ):
        _add(findings, "release_evidence_outstanding_sequence_invalid")
        valid = False
    return valid


def _validate_external_state(
    payload: Mapping[str, Any], findings: list[str]
) -> bool:
    external = _as_mapping(payload.get("external_state_review_inputs"))
    expected = {
        "tracker_issue": "#201",
        "tracker_expected_state": "open",
        "source_prs": ["#202", "#204", "#205", "#206", "#208", "#210", "#212"],
        "source_pr_expected_state": "merged",
        "verification_mode": "reviewer_confirmed_external_state",
        "verified_by_deterministic_evaluator": False,
        "reviewer_confirmation_required": True,
    }
    if external != expected:
        _add(findings, "external_state_review_inputs_invalid")
        return False
    return True


def _validate_command_manifest(
    payload: Mapping[str, Any], findings: list[str]
) -> bool:
    commands = payload.get("verification_command_manifest")
    if not isinstance(commands, list):
        _add(findings, "verification_command_manifest_invalid")
        return False

    valid = True
    if len(commands) != len(EXPECTED_COMMANDS):
        _add(findings, "verification_command_manifest_count_invalid")
        valid = False

    for index, (command_id, command_text) in enumerate(EXPECTED_COMMANDS):
        entry = commands[index] if index < len(commands) else {}
        if not isinstance(entry, Mapping):
            entry = {}
        if entry.get("command_id") != command_id:
            _add(findings, f"verification_command_id_invalid:{index}")
            valid = False
        if entry.get("command") != command_text:
            _add(findings, f"verification_command_text_invalid:{command_id}")
            valid = False
        if not isinstance(entry.get("verification_scope"), str) or not entry.get(
            "verification_scope"
        ):
            _add(findings, f"verification_command_scope_missing:{command_id}")
            valid = False
        if entry.get("expected_exit_code") != 0:
            _add(findings, f"verification_command_exit_code_invalid:{command_id}")
            valid = False
        if not isinstance(entry.get("expected_result"), str) or not entry.get(
            "expected_result"
        ):
            _add(findings, f"verification_command_result_missing:{command_id}")
            valid = False
        if not isinstance(
            entry.get("evidence_recording_requirement"), str
        ) or not entry.get("evidence_recording_requirement"):
            _add(findings, f"verification_command_evidence_missing:{command_id}")
            valid = False
        if entry.get("executed_by_release_proof_evaluator") is not False:
            _add(findings, f"verification_command_execution_claimed:{command_id}")
            valid = False
        if command_id.startswith("run_"):
            expected_result = str(entry.get("expected_result", "")).lower()
            if "ran <number> tests" not in expected_result or "ok" not in expected_result:
                _add(findings, f"verification_command_test_output_invalid:{command_id}")
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
    if len(items) != len(EXPECTED_OUTSTANDING_ORDER):
        _add(findings, "outstanding_completion_items_count_invalid")
        valid = False

    for index, item_id in enumerate(EXPECTED_OUTSTANDING_ORDER, start=1):
        item = items[index - 1] if index <= len(items) else {}
        if not isinstance(item, Mapping):
            item = {}
        expected_prerequisite = (
            "m14_release_proof_linkage_valid"
            if index == 1
            else EXPECTED_OUTSTANDING_ORDER[index - 2]
        )
        expectations = {
            "item_id": item_id,
            "status": "pending",
            "sequence_order": index,
            "prerequisite": expected_prerequisite,
            "not_performed_by_this_pr": True,
        }
        for field, expected in expectations.items():
            if item.get(field) != expected:
                _add(findings, f"outstanding_item_invalid:{item_id}:{field}")
                valid = False
        if not isinstance(item.get("authorized_actor"), str) or not item.get(
            "authorized_actor"
        ):
            _add(findings, f"outstanding_item_actor_missing:{item_id}")
            valid = False
        evidence = item.get("completion_evidence_required")
        if not isinstance(evidence, list) or not evidence or not all(
            isinstance(value, str) and value for value in evidence
        ):
            _add(findings, f"outstanding_item_evidence_invalid:{item_id}")
            valid = False
    return valid


def _validate_cases(payload: Mapping[str, Any], findings: list[str]) -> bool:
    cases = payload.get("release_proof_cases")
    if not isinstance(cases, list):
        _add(findings, "release_proof_cases_invalid")
        return False
    valid = True
    if len(cases) < 42:
        _add(findings, "release_proof_case_coverage_incomplete")
        valid = False
    case_ids: list[str] = []
    for item in cases:
        if not isinstance(item, Mapping):
            _add(findings, "release_proof_case_entry_invalid")
            valid = False
            continue
        case_id = item.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            _add(findings, "release_proof_case_id_missing")
            valid = False
            continue
        case_ids.append(case_id)
        if not isinstance(item.get("description"), str) or not item.get("description"):
            _add(findings, f"release_proof_case_description_missing:{case_id}")
            valid = False
        if item.get("expected_result") not in {"valid", "invalid"}:
            _add(findings, f"release_proof_case_expected_result_invalid:{case_id}")
            valid = False
    if len(case_ids) != len(set(case_ids)):
        _add(findings, "release_proof_case_id_duplicate")
        valid = False
    for number in range(1, 43):
        prefix = f"case_{number:02d}_"
        if sum(case_id.startswith(prefix) for case_id in case_ids) != 1:
            _add(findings, f"release_proof_case_missing:{number:02d}")
            valid = False
    return valid


def _validate_catalogs_and_authority(
    payload: Mapping[str, Any], findings: list[str]
) -> tuple[bool, bool]:
    valid = True
    if tuple(payload.get("required_boundary_statements", ())) != (
        REQUIRED_BOUNDARY_STATEMENTS
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
    for field, expected in policy_expectations.items():
        if policy.get(field) is not expected:
            _add(findings, f"forbidden_claim_policy_invalid:{field}")
            valid = False

    negative_vocabulary = policy.get("explicit_negative_normalized_vocabulary")
    if not isinstance(negative_vocabulary, list):
        _add(findings, "explicit_negative_vocabulary_invalid")
        valid = False
    else:
        required_negative_values = {
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
        }
        if (
            False not in negative_vocabulary
            or 0 not in negative_vocabulary
            or None not in negative_vocabulary
            or "" not in negative_vocabulary
            or not required_negative_values <= _string_set(negative_vocabulary)
        ):
            _add(findings, "explicit_negative_vocabulary_invalid")
            valid = False

    if policy.get("authority_state_fields") != [
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
    ]:
        _add(findings, "authority_state_fields_invalid")
        valid = False

    authority = _as_mapping(payload.get("authority_boundary"))
    authority_valid = True
    if (
        authority.get("retained_authority_owner") != "AAOS"
        or authority.get("decision_proof_sealing_owner") != "AAOS"
        or authority.get("decision_proof_sealing_statement")
        != "Decision Proof sealing remains AAOS-owned."
        or authority.get("sovereignty_statement")
        != "AAOS remains the decision sovereignty layer."
        or not REQUIRED_AUTHORITY_MAY <= _string_set(authority.get("may"))
        or not REQUIRED_AUTHORITY_MUST_NOT <= _string_set(authority.get("must_not"))
    ):
        _add(findings, "authority_boundary_invalid")
        authority_valid = False
        valid = False
    return valid, authority_valid


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
                if _authority_value_is_affirmative(nested):
                    _add(
                        findings,
                        "affirmative_forbidden_claim:" + ".".join(current_path),
                    )
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


def _build_outputs(
    *,
    valid: bool,
    coverage: bool,
    bundle_integrity: bool,
    artifact_integrity: bool,
    authority_preserved: bool,
) -> list[str]:
    outputs = [
        (
            "m14_release_proof_linkage_valid"
            if valid
            else "m14_release_proof_linkage_invalid"
        ),
        (
            "release_linkage_coverage_complete"
            if coverage
            else "release_linkage_coverage_incomplete"
        ),
        (
            "operational_readiness_bundle_valid"
            if bundle_integrity
            else "operational_readiness_bundle_invalid"
        ),
        (
            "source_artifact_integrity_valid"
            if artifact_integrity
            else "source_artifact_integrity_invalid"
        ),
        (
            "authority_boundaries_preserved"
            if authority_preserved
            else "authority_boundary_violation"
        ),
        "external_state_confirmation_required",
    ]
    if valid:
        outputs.extend(
            (
                "release_proof_complete",
                "release_ready_for_review",
                "ready_for_future_readme_status_path",
                "review_required",
            )
        )
    else:
        outputs.extend(("not_ready", "escalation_required"))
        if not authority_preserved:
            outputs.append("fail_closed_recommended")
    return outputs


def evaluate_m14_release_proof_linkage(
    payload: dict[str, Any], repository_root: str | Path | None = None
) -> dict[str, Any]:
    """Validate M14 release-proof linkage without executing referenced artifacts."""

    findings: list[str] = []
    if not isinstance(payload, dict):
        payload = {}
        _add(findings, "release_proof_payload_invalid")
    root = _repository_root(repository_root)

    top_valid, refs_valid = _validate_top_level(payload, findings)
    (
        bundle_present,
        bundle_integrity,
        bundle_historical_digest_valid,
        bundle_maintained_digest_valid,
        readiness,
    ) = (
        _validate_operational_readiness_bundle(payload, root, findings)
    )
    readiness_valid = _validate_readiness_state(readiness, findings)
    source_track_valid = _validate_source_track_linkage(payload, readiness, findings)
    (
        source_artifact_integrity,
        source_artifact_historical_digest_valid,
        source_artifact_maintained_digest_valid,
    ) = _validate_source_artifacts(readiness, root, findings)
    source_policy_valid = _validate_source_artifact_policy(payload, findings)
    evidence_packet_valid = _validate_release_evidence_packet(payload, findings)
    external_valid = _validate_external_state(payload, findings)
    command_manifest_valid = _validate_command_manifest(payload, findings)
    outstanding_valid = _validate_outstanding_items(payload, findings)
    cases_valid = _validate_cases(payload, findings)
    catalogs_valid, authority_catalog_valid = _validate_catalogs_and_authority(
        payload, findings
    )
    claim_findings: list[str] = []
    _scan_forbidden_claims(payload, claim_findings)
    for finding in claim_findings:
        _add(findings, finding)
    no_forbidden_claims = not claim_findings

    coverage = bool(refs_valid and readiness_valid and source_track_valid)
    authority_preserved = bool(
        authority_catalog_valid
        and catalogs_valid
        and external_valid
        and no_forbidden_claims
        and all(payload.get(field) is False for field in REQUIRED_FALSE_TOP_LEVEL)
        and all(
            _as_mapping(track).get("retained_authority_owner") == "AAOS"
            and _as_mapping(track).get("decision_proof_sealing_owner") == "AAOS"
            and _as_mapping(track).get("release_authority_granted") is False
            for track in payload.get("source_track_linkage", ())
        )
    )

    valid = bool(
        top_valid
        and refs_valid
        and bundle_present
        and bundle_integrity
        and readiness_valid
        and source_track_valid
        and source_artifact_integrity
        and source_policy_valid
        and evidence_packet_valid
        and external_valid
        and command_manifest_valid
        and outstanding_valid
        and cases_valid
        and catalogs_valid
        and authority_preserved
        and no_forbidden_claims
        and not findings
    )

    outputs = _build_outputs(
        valid=valid,
        coverage=coverage,
        bundle_integrity=bundle_integrity,
        artifact_integrity=source_artifact_integrity,
        authority_preserved=authority_preserved,
    )
    return {
        "valid": valid,
        "release_linkage_coverage_complete": coverage,
        "operational_readiness_bundle_present": bundle_present,
        "operational_readiness_bundle_integrity_valid": bundle_integrity,
        "operational_readiness_bundle_historical_digest_valid": (
            bundle_historical_digest_valid
        ),
        "operational_readiness_bundle_maintained_digest_valid": (
            bundle_maintained_digest_valid
        ),
        "source_track_linkage_valid": source_track_valid,
        "source_artifact_integrity_valid": source_artifact_integrity,
        "source_artifact_historical_digest_valid": (
            source_artifact_historical_digest_valid
        ),
        "source_artifact_maintained_digest_valid": (
            source_artifact_maintained_digest_valid
        ),
        "authority_boundaries_preserved": authority_preserved,
        "verification_manifest_complete": command_manifest_valid,
        "external_state_confirmation_required": True,
        "outstanding_completion_items_valid": outstanding_valid,
        "release_proof_complete": valid,
        "release_ready_for_review": valid,
        "ready_for_future_readme_status_path": valid,
        "ready_for_m14_completion_review": False,
        "release_approved": False,
        "released": False,
        "m14_complete": False,
        "findings": sorted(findings),
        "outputs": outputs,
    }


def validate_m14_release_proof_linkage(
    payload: dict[str, Any], repository_root: str | Path | None = None
) -> dict[str, Any]:
    """Return the complete deterministic release-proof-linkage result."""

    return evaluate_m14_release_proof_linkage(payload, repository_root)


def evaluate_file(
    path: str | Path, repository_root: str | Path | None = None
) -> dict[str, Any]:
    """Load and evaluate one release-proof fixture as inert JSON data."""

    return evaluate_m14_release_proof_linkage(
        load_fixture(path),
        repository_root,
    )
