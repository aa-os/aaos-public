"""Deterministic validation for the M14 final-completion transition.

The evaluator treats repository files as inert evidence.  It reads JSON and
README text, preserves the recorded PR #214 digests as historical evidence,
recomputes canonical repository-text SHA-256 digests for maintained files, and
reports whether the recorded transition is internally consistent.  It never
imports or executes another evaluator or test, runs commands or workflows,
queries GitHub, publishes a release, changes tracker state, or exercises
governance authority.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence


EXPECTED_CHANGED_FILES = (
    "README.md",
    (
        "examples/public-integration-pack-pilot/"
        "m14-final-completion-release-state.json"
    ),
    "runtime/m14_final_completion_evaluator.py",
    "tests/test_m14_final_completion_evaluator.py",
)

EXPECTED_SOURCE_PRS = (
    "#202",
    "#204",
    "#205",
    "#206",
    "#208",
    "#210",
    "#212",
    "#213",
    "#214",
)

EXPECTED_BUNDLE = (
    {
        "source_pr": "#214",
        "relative_path": (
            "examples/public-integration-pack-pilot/"
            "m14-completion-readiness-future-readme-path.json"
        ),
        "artifact_type": "fixture",
        "required": True,
        "sha256": "e65e4558bc25504ebea24dd8479ac5c40e1ecc588cd3262e729fe77b193d2673",
        "digest_algorithm": "sha256",
        "observed_on_branch": "main",
        "evidence_role": "completion_readiness_fixture_data",
        "executable_by_final_completion_evaluator": False,
    },
    {
        "source_pr": "#214",
        "relative_path": "runtime/m14_completion_readiness_evaluator.py",
        "artifact_type": "runtime_evaluator",
        "required": True,
        "sha256": "c3e1a9b36b94750f4ec6fe00c2fda7def4c033eb2a7100100fc31a4378deb956",
        "digest_algorithm": "sha256",
        "observed_on_branch": "main",
        "evidence_role": "completion_readiness_evaluator_source",
        "executable_by_final_completion_evaluator": False,
    },
    {
        "source_pr": "#214",
        "relative_path": "tests/test_m14_completion_readiness_evaluator.py",
        "artifact_type": "deterministic_test",
        "required": True,
        "sha256": "7aec68924201a6facb5d9248c065346e774b49cf6377161d8c2c0931df30c7ed",
        "digest_algorithm": "sha256",
        "observed_on_branch": "main",
        "evidence_role": "completion_readiness_test_source",
        "executable_by_final_completion_evaluator": False,
    },
)

EXPECTED_MAINTAINED_BUNDLE_SHA256 = {
    (
        "examples/public-integration-pack-pilot/"
        "m14-completion-readiness-future-readme-path.json"
    ): "e65e4558bc25504ebea24dd8479ac5c40e1ecc588cd3262e729fe77b193d2673",
    "runtime/m14_completion_readiness_evaluator.py": (
        "c3e1a9b36b94750f4ec6fe00c2fda7def4c033eb2a7100100fc31a4378deb956"
    ),
    "tests/test_m14_completion_readiness_evaluator.py": (
        "9333843bdd89df5b5a4f6cc1889eba7d2a9ca48e636b8bdebda80ab9bad8f9b9"
    ),
}

EXPECTED_TOP_LEVEL = {
    "artifact_id": "m14-final-completion-release-state",
    "artifact_name": "M14 Final Completion Release State",
    "artifact_scope": (
        "high_risk_runtime_policy_and_public_output_safety_final_completion_"
        "release_state_preparation"
    ),
    "artifact_status": "final_completion_release_state_prepared",
    "milestone": "M14",
    "m14_completion_status": "complete",
    "related_issue": "#201",
    "tracker_issue_closure_state": "closes_on_merge",
    "tracker_issue_linkage": "Closes #201",
    "voice_runtime_policy_pr": "#202",
    "public_output_exfiltration_gate_pr": "#204",
    "moda_risk_mapping_pr": "#205",
    "ai_pr_provenance_pr": "#206",
    "skill_admission_pr": "#208",
    "cross_control_authority_boundary_pr": "#210",
    "operational_readiness_pr": "#212",
    "release_proof_linkage_pr": "#213",
    "completion_readiness_future_readme_path_pr": "#214",
    "introduced_after_release": "v0.12.0",
    "prior_released_baseline": "v0.12.0",
    "target_release": "v0.13.0",
    "release_status": "repository_release_state_prepared",
}

EXPECTED_TRUE_TOP_LEVEL = (
    "final_m14_completion_review_completed",
    "final_completion_recorded_by_authorized_merge",
    "completion_readiness_consumed",
    "github_release_to_be_created_after_merge",
    "m14_complete",
    "issue_201_closes_on_merge",
    "repository_release_state_prepared",
)

EXPECTED_FALSE_TOP_LEVEL = (
    "github_release_created_by_pr",
    "release_tag_created_by_pr",
    "release_notes_published_by_pr",
    "decision_proof_sealed_by_this_artifact",
    "evaluator_grants_release_authority",
    "evaluator_made_final_governance_judgment",
    "risk_accepted_by_artifact",
    "rollback_executed_by_artifact",
    "fail_closed_executed_by_artifact",
    "audit_closed_by_artifact",
    "authority_transferred_by_artifact",
    "network_access_performed_by_evaluator",
    "workflows_executed_by_evaluator",
)

REQUIRED_CONTAINERS = (
    "release_state_boundary",
    "completion_readiness_bundle",
    "completion_readiness_state_validation",
    "artifact_links",
    "release_linkage_refs",
    "readme_release_state_updates",
    "m14_outputs",
    "deterministic_evaluator_references",
    "test_references",
    "final_completion_evidence_packet",
    "manual_release_publication_steps",
    "required_boundary_statements",
    "semantic_boundaries",
    "allowed_evaluator_outputs",
    "forbidden_evaluator_outputs",
    "authority_boundary",
    "expected_baseline_result",
)

EXPECTED_PRE_TRANSITION = {
    "fixture_status": "m14_active_work_not_complete",
    "tracker_issue": "#201",
    "tracker_expected_state": "open",
    "target_future_release": "v0.13.0",
    "release_proof_complete": True,
    "completion_ready_for_review": True,
    "ready_for_final_m14_completion_review": True,
    "final_m14_completion_review_completed": False,
    "readme_future_path_present": True,
    "release_approved": False,
    "released": False,
    "m14_complete": False,
    "release_tag_created": False,
    "github_release_created": False,
    "decision_proof_sealed_by_fixture": False,
}

EXPECTED_RELEASE_STATE_BOUNDARY = {
    "repository_release_state_prepared": True,
    "github_release_publication": "manual_after_merge_only",
    "github_release_created_by_pr": False,
    "release_tag_created_by_pr": False,
    "release_notes_published_by_pr": False,
    "release_state_preparation_is_publication": False,
    "final_completion_is_github_release_publication": False,
}

EXPECTED_MANUAL_RELEASE_STEPS = (
    "verify final PR merged into main",
    "verify tracker #201 is closed as completed",
    "verify README lists v0.13.0 and M14 complete",
    "create GitHub Release v0.13.0 manually",
    "use the merge commit on main as the release target",
    "publish release notes describing M14 outputs",
    "verify v0.13.0 appears as Latest",
)

REQUIRED_BOUNDARY_STATEMENTS = (
    "Final completion records M14 completion but does not create a GitHub Release.",
    "GitHub Release v0.13.0 must be created only after this PR is merged.",
    "Release-state preparation is not GitHub Release publication.",
    "M14 completion does not transfer governance authority.",
    "README release entry is repository release-state preparation.",
    "The human-reviewed merge is the authorized final-completion transition.",
    "The deterministic evaluator validates evidence but does not grant release authority.",
    "The evaluator does not make the final governance judgment.",
    "Completion does not accept risk.",
    "Completion does not execute rollback.",
    "Completion does not execute fail-closed.",
    "Completion does not close audits independently.",
    "Completion does not grant waivers.",
    "M14 runtime and public-output artifacts do not seal Decision Proof.",
    "Decision Proof sealing remains AAOS-owned.",
    "AAOS remains the decision sovereignty layer.",
    "Final governance authority remains AAOS-owned.",
)

REQUIRED_ALLOWED_OUTPUTS = {
    "m14_final_completion_valid",
    "m14_final_completion_invalid",
    "m14_completion_declared",
    "final_m14_completion_review_recorded",
    "issue_201_closes_on_merge",
    "repository_release_state_prepared",
    "github_release_pending_manual_publication",
    "review_required",
    "escalation_required",
}

REQUIRED_FORBIDDEN_OUTPUTS = {
    "github_release_created",
    "release_published_by_evaluator",
    "release_tag_created_by_evaluator",
    "tracker_closed_by_evaluator",
    "decision_proof_sealed_by_evaluator",
    "sealed_by_runtime_gate",
    "sealed_by_public_output_gate",
    "authority_transferred",
    "risk_accepted_by_evaluator",
    "rollback_executed_by_evaluator",
    "fail_closed_executed_by_evaluator",
    "audit_closed_by_evaluator",
    "waiver_granted_by_evaluator",
    "final_governance_judgment_by_evaluator",
    "release_authority_granted_by_evaluator",
}

REQUIRED_M14_OUTPUTS = {
    "High-Risk Runtime Policy Gates and Public-Output Safety",
    "Governed Voice Runtime Policy Fixtures",
    "Public Issue Exfiltration Gate",
    "MODA AI Risk Framework Mapping",
    "AI-Authored PR Provenance and Reviewer Routing",
    "External Skill Admission Gate",
    "Cross-Control Authority-Boundary Regression Fixtures",
    "M14 Operational Readiness Checklist",
    "M14 Release Proof Linkage Specimen",
    "M14 Completion Readiness and README release-state path",
    "deterministic M14 evaluator coverage",
}

README_RELEASE_ENTRY = (
    "- v0.13.0 — M14 High-Risk Runtime Policy Gates and Public-Output Safety"
)
README_BASELINE_PATTERN = (
    "the M14 High-Risk Runtime Policy Gates and Public-Output Safety pattern"
)
README_ADDS_STATEMENT = (
    "v0.13.0 adds the M14 High-Risk Runtime Policy Gates and Public-Output Safety "
    "pattern."
)
README_DECLARES_STATEMENT = (
    "v0.13.0 declares M14 complete and prepares the repository for the v0.13.0 "
    "release state."
)
README_STATUS = (
    "M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11, M12, M13, and M14 "
    "are complete."
)
README_NEXT_PHASE_STATEMENT = (
    "Future milestone planning will be tracked separately after v0.13.0 release "
    "publication."
)
README_COMPLETED_REFS = {
    "#201 M14 tracker issue",
    "#202 Governed Voice Runtime Policy Fixtures",
    "#204 Public Issue Exfiltration Gate",
    "#205 MODA AI Risk Framework Mapping",
    "#206 AI-Authored PR Provenance and Reviewer Routing",
    "#208 External Skill Admission Gate",
    "#210 Cross-Control Authority-Boundary Regression Fixtures",
    "#212 Operational Readiness Checklist",
    "#213 Release Proof Linkage Specimen",
    "#214 Completion Readiness and Future README Path",
    "this final completion PR",
}
README_OBSOLETE_NEXT_PHASE_TEXT = (
    "M14 remains active work",
    "final completion has not been declared",
    "v0.13.0 remains future-only",
    "Tracker: #201 remains Open",
    (
        "ready_for_final_m14_completion_review is not final completion review "
        "completed"
    ),
)

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
    "not_closed",
    "not_complete",
    "not_completed",
    "not_created",
    "not_executed",
    "not_final",
    "not_granted",
    "not_made_by_evaluator",
    "not_published",
    "not_released",
    "not_sealed",
    "not_sealed_by_m14_artifacts_or_evaluator",
    "not_transferred",
    "not_verified",
    "not_closed_independently",
    "not_github_release_publication",
    "manual_after_merge_only",
    "pending_manual_publication_after_merge",
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
    "completion_status",
}

NEUTRAL_METADATA_FIELDS = {
    "description",
    "note",
    "rationale",
    "evidence_role",
    "source",
    "source_pr",
    "relative_path",
    "actor",
    "performed_after_merge",
    "performed_by_this_pr",
    "performed_by_evaluator",
}

FORBIDDEN_AUTHORITY_KEYS = REQUIRED_FORBIDDEN_OUTPUTS | {
    "repository_release_state_prepared",
    "release_approved",
    "release_created",
    "release_tag_created",
    "github_release_created",
    "release_notes_published",
    "released",
    "decision_proof_sealed",
    "decision_proof_sealed_by_fixture",
    "risk_accepted",
    "rollback_executed",
    "fail_closed_executed",
    "audit_closed",
    "waiver_granted",
    "final_governance_judgment",
    "m14_complete",
    "final_m14_completion_review_completed",
    "final_completion_recorded_by_authorized_merge",
    "issue_201_closes_on_merge",
    "evaluator_grants_release_authority",
    "evaluator_made_final_governance_judgment",
    "github_release_created_by_pr",
    "release_tag_created_by_pr",
    "release_notes_published_by_pr",
    "decision_proof_sealed_by_this_artifact",
    "risk_accepted_by_artifact",
    "rollback_executed_by_artifact",
    "fail_closed_executed_by_artifact",
    "audit_closed_by_artifact",
    "waiver_granted_by_artifact",
    "authority_transferred_by_artifact",
    "network_access_performed_by_evaluator",
    "workflows_executed_by_evaluator",
    "source_evaluators_executed_by_evaluator",
    "source_tests_executed_by_evaluator",
    "verification_commands_executed_by_evaluator",
    "tracker_closed_directly_by_evaluator",
    "release_created_by_evaluator",
    "tag_created_by_evaluator",
    "release_authority",
    "risk_acceptance",
    "rollback_execution",
    "fail_closed_execution",
    "audit_closure",
    "waiver_state",
    "authority_transfer",
    "decision_proof_sealing",
}

CLAIM_SCAN_SKIP_PATHS = {
    ("forbidden_evaluator_outputs",),
    ("expected_baseline_result",),
    ("authority_boundary", "must_not"),
}

EVALUATOR_ACTORS = {
    "evaluator",
    "deterministic_evaluator",
    "runtime_evaluator",
    "final_completion_evaluator",
}

FORBIDDEN_ACTION_TOKENS = (
    "grant_release_authority",
    "release_authority_granted",
    "create_or_publish_github_release",
    "create_github_release",
    "github_release_created",
    "publish_github_release",
    "github_release_published",
    "create_release",
    "release_created",
    "publish_release",
    "release_published",
    "create_release_tag",
    "release_tag_created",
    "close_tracker_directly",
    "close_tracker",
    "tracker_closed",
    "accept_risk",
    "risk_accepted",
    "execute_rollback",
    "rollback_executed",
    "execute_fail_closed",
    "fail_closed_executed",
    "close_audit",
    "audit_closed",
    "grant_waiver",
    "waiver_granted",
    "transfer_authority",
    "authority_transferred",
    "make_final_governance_judgment",
    "final_governance_judgment_made",
    "seal_decision_proof",
    "decision_proof_sealed",
)

FORBIDDEN_ACTION_NOUN_TOKENS = {
    "release_authority",
    "release_creation",
    "release_publication",
    "github_release_creation",
    "github_release_publication",
    "release_tag_creation",
    "tracker_closure",
    "risk_acceptance",
    "rollback",
    "rollback_execution",
    "fail_closed",
    "fail_closed_execution",
    "audit_closure",
    "waiver_grant",
    "authority_transfer",
    "final_governance_judgment",
    "decision_proof_sealing",
}

AFFIRMATIVE_AUTHORITY_PROSE = (
    "evaluator_grants_release_authority",
    "evaluator_grant_release_authority",
    "release_authority_granted_by_evaluator",
    "evaluator_creates_github_release",
    "evaluator_create_github_release",
    "evaluator_publishes_github_release",
    "evaluator_publish_github_release",
    "release_published_by_evaluator",
    "evaluator_creates_release_tag",
    "evaluator_create_release_tag",
    "release_tag_created_by_evaluator",
    "evaluator_closes_tracker",
    "evaluator_close_tracker",
    "tracker_closed_by_evaluator",
    "evaluator_accepts_risk",
    "evaluator_accept_risk",
    "risk_accepted_by_evaluator",
    "evaluator_executes_rollback",
    "evaluator_execute_rollback",
    "rollback_executed_by_evaluator",
    "evaluator_executes_fail_closed",
    "evaluator_execute_fail_closed",
    "fail_closed_executed_by_evaluator",
    "evaluator_closes_audit",
    "evaluator_close_audit",
    "audit_closed_by_evaluator",
    "evaluator_grants_waiver",
    "evaluator_grant_waiver",
    "waiver_granted_by_evaluator",
    "evaluator_transfers_authority",
    "evaluator_transfer_authority",
    "authority_transferred_by_evaluator",
    "evaluator_makes_final_governance_judgment",
    "evaluator_make_final_governance_judgment",
    "final_governance_judgment_by_evaluator",
    "evaluator_seals_decision_proof",
    "evaluator_seal_decision_proof",
    "decision_proof_sealed_by_evaluator",
)

AUTHORIZED_RECORD_PATHS = {
    ("m14_complete",): True,
    ("final_m14_completion_review_completed",): True,
    ("final_completion_recorded_by_authorized_merge",): True,
    ("issue_201_closes_on_merge",): True,
    ("repository_release_state_prepared",): True,
    ("release_state_boundary", "repository_release_state_prepared"): True,
}


def _add(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, (list, tuple)):
        return value
    return ()


def _string_set(value: Any) -> set[str]:
    return {
        item.strip()
        for item in _as_sequence(value)
        if isinstance(item, str) and item.strip()
    }


def _is_string_sequence(value: Any) -> bool:
    return isinstance(value, (list, tuple)) and all(
        isinstance(item, str) and bool(item.strip()) for item in value
    )


def _token(value: Any) -> str:
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", str(value).strip())
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


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


def _sha256_repository_text(path: Path) -> str:
    """Hash Git text bytes, canonicalizing only checkout CRLF to repository LF."""

    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_fixture(path: str | Path) -> dict[str, Any]:
    """Load one UTF-8 final-completion fixture as inert JSON data."""

    with Path(path).open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("M14 final-completion fixture must contain a JSON object")
    return payload


def _section(text: str, heading: str, end_heading: str | None = None) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    if end_heading is None:
        return text[start:]
    end = text.find(end_heading, start + len(heading))
    return text[start:] if end < 0 else text[start:end]


def _has_container(payload: Mapping[str, Any], key: str) -> bool:
    value = payload.get(key)
    return isinstance(value, (Mapping, list, tuple)) and bool(value)


def _validate_top_level(
    payload: Mapping[str, Any], findings: list[str], missing: list[str]
) -> tuple[bool, bool]:
    valid = True
    authority_valid = True
    for field, expected in EXPECTED_TOP_LEVEL.items():
        if payload.get(field) != expected:
            _add(findings, f"top_level_invalid:{field}")
            _add(missing, field)
            valid = False
    for field in EXPECTED_TRUE_TOP_LEVEL:
        if payload.get(field) is not True:
            _add(findings, f"top_level_true_required:{field}")
            _add(missing, field)
            valid = False
    for field in EXPECTED_FALSE_TOP_LEVEL:
        if payload.get(field) is not False:
            _add(findings, f"top_level_false_required:{field}")
            _add(missing, field)
            valid = False
            if payload.get(field) not in (False, None, 0, ""):
                authority_valid = False
    if tuple(payload.get("changed_file_scope", ())) != EXPECTED_CHANGED_FILES:
        _add(findings, "changed_file_scope_invalid")
        _add(missing, "exact_four_changed_file_scope")
        valid = False
    for key in REQUIRED_CONTAINERS:
        if not _has_container(payload, key):
            _add(findings, f"required_container_missing:{key}")
            _add(missing, key)
            valid = False
    return valid, authority_valid


def _validate_release_boundary(
    payload: Mapping[str, Any], findings: list[str], missing: list[str]
) -> tuple[bool, bool]:
    boundary = _as_mapping(payload.get("release_state_boundary"))
    valid = True
    authority_valid = True
    for field, expected in EXPECTED_RELEASE_STATE_BOUNDARY.items():
        if boundary.get(field) != expected:
            _add(findings, f"release_state_boundary_invalid:{field}")
            _add(missing, f"release_state_boundary.{field}")
            valid = False
            if expected is False and boundary.get(field) not in (False, None, 0, ""):
                authority_valid = False
    return valid, authority_valid


def _validate_bundle(
    payload: Mapping[str, Any], root: Path, findings: list[str], missing: list[str]
) -> tuple[bool, bool, Mapping[str, Any] | None]:
    entries = _as_sequence(payload.get("completion_readiness_bundle"))
    present = True
    integrity = True
    readiness_fixture: Mapping[str, Any] | None = None
    if len(entries) != len(EXPECTED_BUNDLE):
        _add(findings, "completion_readiness_bundle_count_invalid")
        _add(missing, "exact_three_completion_readiness_bundle_entries")
        integrity = False

    expected_by_path = {item["relative_path"]: item for item in EXPECTED_BUNDLE}
    actual_by_path: dict[str, Mapping[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, Mapping):
            _add(findings, "completion_readiness_bundle_entry_invalid")
            integrity = False
            continue
        path_value = entry.get("relative_path")
        if isinstance(path_value, str):
            if path_value in actual_by_path:
                _add(findings, f"completion_readiness_bundle_path_duplicate:{path_value}")
                integrity = False
            actual_by_path[path_value] = entry
        else:
            _add(findings, "completion_readiness_bundle_path_invalid")
            integrity = False

    if set(actual_by_path) != set(expected_by_path):
        _add(findings, "completion_readiness_bundle_paths_invalid")
        _add(missing, "exact_completion_readiness_bundle_paths")
        integrity = False

    for relative_path, expected in expected_by_path.items():
        entry = actual_by_path.get(relative_path)
        if entry is None:
            present = False
            continue
        for field, expected_value in expected.items():
            if entry.get(field) != expected_value:
                _add(findings, f"completion_readiness_bundle_metadata_invalid:{relative_path}:{field}")
                integrity = False
        path = _safe_repository_path(root, relative_path)
        if path is None or not path.is_file():
            _add(findings, f"completion_readiness_bundle_file_missing:{relative_path}")
            _add(missing, relative_path)
            present = False
            integrity = False
            continue
        observed = _sha256_repository_text(path)
        if observed != EXPECTED_MAINTAINED_BUNDLE_SHA256[relative_path]:
            _add(findings, f"completion_readiness_bundle_digest_mismatch:{relative_path}")
            integrity = False
        if expected["artifact_type"] == "fixture":
            try:
                loaded = load_fixture(path)
            except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
                _add(findings, "completion_readiness_fixture_invalid_json")
                integrity = False
            else:
                readiness_fixture = loaded
    return present, integrity, readiness_fixture


def _validate_pre_transition(
    payload: Mapping[str, Any],
    readiness_fixture: Mapping[str, Any] | None,
    findings: list[str],
    missing: list[str],
) -> bool:
    validation = _as_mapping(payload.get("completion_readiness_state_validation"))
    source_path = EXPECTED_BUNDLE[0]["relative_path"]
    valid = True
    if validation.get("source_fixture_path") != source_path:
        _add(findings, "completion_readiness_state_source_path_invalid")
        valid = False
    if validation.get("loaded_as_inert_json_only") is not True:
        _add(findings, "completion_readiness_fixture_not_marked_inert")
        valid = False
    if validation.get("pre_transition_role") not in {
        "pre_transition_readiness_evidence",
        "pre_transition_state_validation",
        "readiness_pre_transition_evidence",
        "validated_ready_for_final_review_not_complete_or_released",
    }:
        _add(findings, "completion_readiness_pre_transition_role_invalid")
        valid = False

    expected_values = _as_mapping(validation.get("expected_values"))
    for field, expected in EXPECTED_PRE_TRANSITION.items():
        if expected_values.get(field) != expected:
            _add(findings, f"completion_readiness_expected_state_invalid:{field}")
            valid = False

    required_authority = _as_mapping(validation.get("required_authority"))
    for field in ("retained_authority_owner", "decision_proof_sealing_owner"):
        if required_authority.get(field) != "AAOS":
            _add(findings, f"completion_readiness_required_authority_invalid:{field}")
            valid = False

    if readiness_fixture is None:
        _add(findings, "completion_readiness_pre_transition_fixture_unavailable")
        _add(missing, source_path)
        return False
    for field, expected in EXPECTED_PRE_TRANSITION.items():
        if readiness_fixture.get(field) != expected:
            _add(findings, f"completion_readiness_pre_transition_state_invalid:{field}")
            valid = False
    source_authority = _as_mapping(readiness_fixture.get("authority_boundary"))
    if source_authority.get("retained_authority_owner") != "AAOS":
        _add(findings, "completion_readiness_source_authority_owner_invalid")
        valid = False
    if source_authority.get("decision_proof_sealing_owner") != "AAOS":
        _add(findings, "completion_readiness_source_sealing_owner_invalid")
        valid = False
    return valid


def _validate_linkage_and_packet(
    payload: Mapping[str, Any], findings: list[str], missing: list[str]
) -> bool:
    valid = True
    refs = _as_mapping(payload.get("release_linkage_refs"))
    ref_values = {value for value in refs.values() if isinstance(value, str)}
    expected_refs = set(EXPECTED_SOURCE_PRS) | {"#201", "Closes #201"}
    if not set(EXPECTED_SOURCE_PRS) <= ref_values or "#201" not in ref_values:
        _add(findings, "release_linkage_refs_incomplete")
        _add(missing, "nine_m14_source_pr_references")
        valid = False
    if "#209" in ref_values:
        _add(findings, "pr_209_present_in_release_linkage_refs")
        valid = False
    unexpected_pr_refs = {
        value
        for value in ref_values
        if re.fullmatch(r"#[0-9]+", value) and value not in expected_refs
    }
    if unexpected_pr_refs:
        _add(findings, "unexpected_pr_present_in_release_linkage_refs")
        valid = False

    packet = _as_mapping(payload.get("final_completion_evidence_packet"))
    packet_expected = {
        "milestone": "M14",
        "tracker_issue": "#201",
        "tracker_linkage": "Closes #201",
        "prior_release_baseline": "v0.12.0",
        "target_release": "v0.13.0",
        "completion_readiness_pr": "#214",
        "final_completion_review_status": "completed",
        "tracker_transition_status": "closes_on_merge",
        "repository_release_state": "prepared",
        "github_release_status": "pending_manual_publication_after_merge",
        "release_tag_status": "not_created_by_pr",
        "m14_completion_status": "complete",
        "decision_proof_sealed": False,
        "authority_owner": "AAOS",
        "decision_proof_sealing_owner": "AAOS",
        "evidence_role": "final_completion_traceability_not_evaluator_authority",
    }
    for field, expected in packet_expected.items():
        if packet.get(field) != expected:
            _add(findings, f"final_completion_evidence_packet_invalid:{field}")
            valid = False
    if tuple(packet.get("source_pr_references", ())) != EXPECTED_SOURCE_PRS:
        _add(findings, "final_completion_source_pr_references_invalid")
        _add(missing, "exact_nine_source_pr_references")
        valid = False
    if "#209" in _string_set(packet.get("source_pr_references")):
        _add(findings, "pr_209_present_in_final_completion_evidence_chain")
        valid = False

    digest_entries = _as_sequence(packet.get("completion_readiness_bundle_digests"))
    digest_map: dict[str, str] = {}
    for entry in digest_entries:
        if isinstance(entry, Mapping):
            relative_path = entry.get("relative_path")
            digest = entry.get("sha256")
            if isinstance(relative_path, str) and isinstance(digest, str):
                digest_map[relative_path] = digest
    expected_digest_map = {
        entry["relative_path"]: entry["sha256"] for entry in EXPECTED_BUNDLE
    }
    if digest_map != expected_digest_map or len(digest_entries) != len(EXPECTED_BUNDLE):
        _add(findings, "final_completion_bundle_digest_packet_invalid")
        valid = False
    return valid


def _validate_manual_steps(payload: Mapping[str, Any], findings: list[str]) -> bool:
    steps = _as_sequence(payload.get("manual_release_publication_steps"))
    if len(steps) != len(EXPECTED_MANUAL_RELEASE_STEPS):
        _add(findings, "manual_release_publication_step_count_invalid")
        return False
    valid = True
    for index, (item, expected_step) in enumerate(
        zip(steps, EXPECTED_MANUAL_RELEASE_STEPS), start=1
    ):
        if not isinstance(item, Mapping):
            _add(findings, f"manual_release_step_invalid:{index}")
            valid = False
            continue
        step_text = item.get("step", item.get("action", item.get("description")))
        if step_text != expected_step:
            _add(findings, f"manual_release_step_order_invalid:{index}")
            valid = False
        for key, expected in {
            "performed_after_merge": True,
            "performed_by_this_pr": False,
            "performed_by_evaluator": False,
        }.items():
            if item.get(key) is not expected:
                _add(findings, f"manual_release_step_boundary_invalid:{index}:{key}")
                valid = False
        for order_key in ("sequence", "sequence_order", "step_order", "order"):
            if order_key in item and item.get(order_key) != index:
                _add(findings, f"manual_release_step_sequence_invalid:{index}")
                valid = False
    return valid


def _validate_catalogs_and_authority(
    payload: Mapping[str, Any], findings: list[str]
) -> bool:
    valid = True
    boundary_values = payload.get("required_boundary_statements")
    boundary_sequence = _as_sequence(boundary_values)
    boundaries = _string_set(boundary_values)
    if not _is_string_sequence(boundary_values):
        _add(findings, "required_boundary_statements_structure_invalid")
        valid = False
    if (
        boundaries != set(REQUIRED_BOUNDARY_STATEMENTS)
        or len(boundary_sequence) != len(REQUIRED_BOUNDARY_STATEMENTS)
    ):
        _add(findings, "required_boundary_statements_incomplete")
        valid = False
    semantic = _as_mapping(payload.get("semantic_boundaries"))
    expected_semantic = {
        "authorized_transition": "human_reviewed_merge",
        "evaluator_role": "deterministic_evidence_validation_only",
        "release_publication": "manual_after_merge_only",
        "release_state_preparation": "not_github_release_publication",
        "risk_acceptance": "not_accepted",
        "rollback_execution": "not_executed",
        "fail_closed_execution": "not_executed",
        "audit_closure": "not_closed_independently",
        "waiver_state": "not_granted",
        "authority_transfer": "not_transferred",
        "final_governance_judgment": "not_made_by_evaluator",
        "decision_proof_sealing": "not_sealed_by_m14_artifacts_or_evaluator",
    }
    for field, expected in expected_semantic.items():
        if semantic.get(field) != expected:
            _add(findings, f"semantic_boundary_invalid:{field}")
            valid = False

    allowed_values = payload.get("allowed_evaluator_outputs")
    forbidden_values = payload.get("forbidden_evaluator_outputs")
    allowed_sequence = _as_sequence(allowed_values)
    forbidden_sequence = _as_sequence(forbidden_values)
    allowed = _string_set(allowed_values)
    forbidden = _string_set(forbidden_values)
    if not _is_string_sequence(allowed_values):
        _add(findings, "allowed_evaluator_outputs_structure_invalid")
        valid = False
    if not _is_string_sequence(forbidden_values):
        _add(findings, "forbidden_evaluator_outputs_structure_invalid")
        valid = False
    if allowed != REQUIRED_ALLOWED_OUTPUTS or len(allowed_sequence) != len(
        REQUIRED_ALLOWED_OUTPUTS
    ):
        _add(findings, "allowed_evaluator_outputs_incomplete")
        valid = False
    if forbidden != REQUIRED_FORBIDDEN_OUTPUTS or len(forbidden_sequence) != len(
        REQUIRED_FORBIDDEN_OUTPUTS
    ):
        _add(findings, "forbidden_evaluator_outputs_incomplete")
        valid = False
    if allowed & forbidden:
        _add(findings, "evaluator_output_catalog_overlap")
        valid = False

    authority = _as_mapping(payload.get("authority_boundary"))
    expected_authority = {
        "retained_authority_owner": "AAOS",
        "decision_proof_sealing_owner": "AAOS",
        "decision_proof_sealing_statement": (
            "Decision Proof sealing remains AAOS-owned."
        ),
        "sovereignty_statement": "AAOS remains the decision sovereignty layer.",
    }
    for field, expected in expected_authority.items():
        if authority.get(field) != expected:
            _add(findings, f"authority_boundary_invalid:{field}")
            valid = False
    if not _is_string_sequence(authority.get("may")):
        _add(findings, "authority_boundary_may_missing")
        valid = False
    if not _is_string_sequence(authority.get("must_not")):
        _add(findings, "authority_boundary_must_not_missing")
        valid = False
    return valid


def _validate_supporting_content(payload: Mapping[str, Any], findings: list[str]) -> bool:
    valid = True
    if not REQUIRED_M14_OUTPUTS <= _string_set(payload.get("m14_outputs")):
        _add(findings, "m14_output_coverage_incomplete")
        valid = False
    for key in (
        "artifact_links",
        "readme_release_state_updates",
        "deterministic_evaluator_references",
        "test_references",
    ):
        if not _has_container(payload, key):
            _add(findings, f"supporting_content_missing:{key}")
            valid = False

    evidence_chain_values: list[str] = []
    for key in ("artifact_links", "release_linkage_refs"):
        value = payload.get(key)
        evidence_chain_values.append(json.dumps(value, sort_keys=True))
    if "#209" in " ".join(evidence_chain_values):
        _add(findings, "pr_209_present_in_m14_evidence_chain")
        valid = False
    return valid


def _validate_readme(root: Path, findings: list[str], missing: list[str]) -> bool:
    path = root / "README.md"
    if not path.is_file():
        _add(findings, "readme_missing")
        _add(missing, "README.md")
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        _add(findings, "readme_unreadable")
        _add(missing, "README.md")
        return False

    normalized = text.replace("\r\n", "\n")
    valid = True
    releases = _section(text, "## Releases", "## Current Status")
    release_lines = [line.strip() for line in releases.splitlines() if line.startswith("- v")]
    if release_lines.count(README_RELEASE_ENTRY) != 1:
        _add(findings, "readme_v0_13_0_release_entry_invalid")
        valid = False
    if not any(line.startswith("- v0.12.0 ") for line in release_lines):
        _add(findings, "readme_v0_12_0_prior_baseline_missing")
        valid = False
    versions: list[tuple[int, int, int]] = []
    for line in release_lines:
        match = re.match(r"^- v(\d+)\.(\d+)\.(\d+)\s+", line)
        if match:
            versions.append(tuple(int(part) for part in match.groups()))
    if (
        not release_lines
        or release_lines[-1] != README_RELEASE_ENTRY
        or not versions
        or max(versions) != (0, 13, 0)
    ):
        _add(findings, "readme_latest_release_not_v0_13_0")
        valid = False

    baseline = _section(text, "Current baseline:", "## Current Status")
    baseline_body = baseline[len("Current baseline:") :].lstrip("\r\n")
    baseline_paragraph = re.split(r"\r?\n\r?\n", baseline_body, maxsplit=1)[0]
    for value, finding in (
        (README_BASELINE_PATTERN, "readme_m14_baseline_pattern_missing"),
        (README_ADDS_STATEMENT, "readme_v0_13_0_adds_statement_missing"),
        (README_DECLARES_STATEMENT, "readme_v0_13_0_declares_statement_missing"),
    ):
        target = baseline_paragraph if value == README_BASELINE_PATTERN else baseline
        if value not in target:
            _add(findings, finding)
            valid = False

    current = _section(text, "## Current Status", "## M5 Additions")
    if README_STATUS not in current:
        _add(findings, "readme_m1_through_m14_completion_status_missing")
        valid = False
    completed = _section(current, "M14 completed:", "AAOS Public now has:")
    if not completed:
        _add(findings, "readme_m14_completed_section_missing")
        valid = False
    else:
        completed_lines = {line.strip() for line in completed.splitlines()}
        for reference in README_COMPLETED_REFS:
            if "- " + reference not in completed_lines:
                _add(findings, f"readme_m14_completed_reference_missing:{reference}")
                valid = False
        if normalized.count("- this final completion PR\n") != 2:
            _add(findings, "readme_historical_final_completion_reference_changed")
            valid = False
    now_has = _section(current, "AAOS Public now has:", None)
    for output in REQUIRED_M14_OUTPUTS:
        if output not in now_has:
            _add(findings, f"readme_m14_output_missing:{output}")
            valid = False

    next_phase_count = len(re.findall(r"(?m)^## Next Phase\s*$", normalized))
    expected_next = "## Next Phase\n\n" + README_NEXT_PHASE_STATEMENT
    next_phase = _section(normalized, "## Next Phase", None).strip()
    if next_phase_count != 1 or next_phase != expected_next:
        _add(findings, "readme_next_phase_not_exact_post_release_statement")
        valid = False
    for obsolete in README_OBSOLETE_NEXT_PHASE_TEXT:
        if obsolete in next_phase:
            _add(findings, "readme_next_phase_obsolete_m14_wording_present")
            valid = False

    for boundary in (
        "Decision Proof sealing remains AAOS-owned.",
        "AAOS remains the decision sovereignty layer.",
    ):
        if not re.search(r"(?m)^" + re.escape(boundary) + r"\r?$", text):
            _add(findings, f"readme_governance_boundary_missing:{boundary}")
            valid = False
    if not valid:
        _add(missing, "README.md final v0.13.0 release state")
    return valid


def _is_explicit_negative(value: Any) -> bool:
    if value is None or value is False:
        return True
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value == 0
    if isinstance(value, str):
        token = _token(value)
        return any(isinstance(item, str) and token == _token(item) for item in EXPLICIT_NEGATIVE_VOCABULARY)
    return False


def _text_has_affirmative_authority_claim(value: str) -> bool:
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", value)
    for sentence in re.split(r"[.!?]", text.lower()):
        evaluator_context = False
        for segment in re.split(
            r";|\b(?:and|or|but|yet|however|although|while)\b", sentence
        ):
            token = _token(segment)
            words = set(part for part in token.split("_") if part)
            if "evaluator" in words:
                evaluator_context = True
            if not evaluator_context:
                continue
            if words & {"not", "never", "cannot", "without", "neither"}:
                continue
            if any(pattern in token for pattern in AFFIRMATIVE_AUTHORITY_PROSE):
                return True
            if _words_have_forbidden_action(words):
                return True
    return False


def _words_have_forbidden_action(words: set[str]) -> bool:
    def has_stem(stem: str) -> bool:
        return any(word.startswith(stem) for word in words)

    grant_or_authorize = has_stem("grant") or has_stem("authoriz")
    execute_or_perform = has_stem("execut") or has_stem("perform")
    if "release" in words and "authority" in words and grant_or_authorize:
        return True
    if "release" in words and (
        has_stem("creat") or has_stem("publi") or has_stem("authoriz")
    ):
        return True
    if "tag" in words and has_stem("creat"):
        return True
    if ("tracker" in words or "issue" in words) and has_stem("clos"):
        return True
    if "risk" in words and has_stem("accept"):
        return True
    if "rollback" in words and execute_or_perform:
        return True
    if {"fail", "closed"} <= words and execute_or_perform:
        return True
    if "audit" in words and has_stem("clos"):
        return True
    if "waiver" in words and grant_or_authorize:
        return True
    if "authority" in words and has_stem("transfer"):
        return True
    if {"final", "governance", "judgment"} <= words and (
        has_stem("mak") or has_stem("decid") or "made" in words
    ):
        return True
    return {"decision", "proof"} <= words and has_stem("seal")


def _action_has_forbidden_semantics(value: str) -> bool:
    token = _token(value)
    words = set(part for part in token.split("_") if part)
    return (
        token in FORBIDDEN_ACTION_NOUN_TOKENS
        or any(pattern in token for pattern in FORBIDDEN_ACTION_TOKENS)
        or _words_have_forbidden_action(words)
    )


def _is_evaluator_actor(value: Any) -> bool:
    actor = _token(value)
    return actor in EVALUATOR_ACTORS or (
        "evaluator" in actor.split("_") and "not" not in actor.split("_")
    )


def _mapping_has_split_authority_claim(
    value: Mapping[str, Any], evaluator_context: bool = False
) -> bool:
    actor_fields = {
        "actor",
        "actor_role",
        "subject",
        "performed_by",
        "executed_by",
        "created_by",
        "granted_by",
        "decided_by",
        "authority_actor",
    }
    actors = [
        nested
        for raw_key, nested in value.items()
        if _token(raw_key) in actor_fields
    ]
    if not evaluator_context and not any(
        _is_evaluator_actor(actor) for actor in actors
    ):
        return False
    action_fields = {
        "action",
        "activity",
        "operation",
        "claim",
        "authority_action",
        "transition_action",
    }
    action = "_".join(
        _token(nested)
        for raw_key, nested in value.items()
        if _token(raw_key) in action_fields and nested is not None
    )
    if not action or not _action_has_forbidden_semantics(action):
        return False
    states = [
        nested
        for raw_key, nested in value.items()
        if _token(raw_key) in AUTHORITY_STATE_FIELDS
    ]
    return not states or any(_authority_value_is_affirmative(state) for state in states)


def _find_structured_authority_signals(value: Any) -> tuple[bool, bool]:
    if isinstance(value, Mapping):
        saw_signal = False
        affirmative = False
        for raw_key, nested in value.items():
            key = _token(raw_key)
            if key in FORBIDDEN_AUTHORITY_KEYS or key in AUTHORITY_STATE_FIELDS:
                saw_signal = True
                if _authority_value_is_affirmative(nested):
                    affirmative = True
            elif key in NEUTRAL_METADATA_FIELDS:
                if isinstance(nested, (Mapping, list, tuple)):
                    child_signal, child_affirmative = (
                        _find_structured_authority_signals(nested)
                    )
                    saw_signal = saw_signal or child_signal
                    affirmative = affirmative or child_affirmative
                elif isinstance(nested, str) and _text_has_affirmative_authority_claim(
                    nested
                ):
                    saw_signal = True
                    affirmative = True
            elif isinstance(nested, (Mapping, list, tuple)):
                child_signal, child_affirmative = _find_structured_authority_signals(
                    nested
                )
                saw_signal = saw_signal or child_signal
                affirmative = affirmative or child_affirmative or (
                    not child_signal and bool(nested)
                )
            else:
                saw_signal = True
                if not _is_explicit_negative(nested):
                    affirmative = True
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
            elif not _is_explicit_negative(nested):
                return True
        return False
    if _is_explicit_negative(value):
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    return bool(value)


def _scan_forbidden_claims(
    value: Any,
    findings: list[str],
    path: tuple[str, ...] = (),
    evaluator_context: bool = False,
) -> None:
    if isinstance(value, Mapping):
        actor_fields = {
            "actor",
            "actor_role",
            "subject",
            "performed_by",
            "executed_by",
            "created_by",
            "granted_by",
            "decided_by",
            "authority_actor",
        }
        local_evaluator_context = evaluator_context or any(
            _token(raw_key) in actor_fields and _is_evaluator_actor(nested)
            for raw_key, nested in value.items()
        )
        if _mapping_has_split_authority_claim(value, local_evaluator_context):
            _add(findings, "split_affirmative_evaluator_authority_claim:" + ".".join(path))
        for raw_key, nested in value.items():
            key = str(raw_key)
            key_token = _token(key)
            current = path + (key,)
            if current in CLAIM_SCAN_SKIP_PATHS:
                continue
            if current in AUTHORIZED_RECORD_PATHS and nested is AUTHORIZED_RECORD_PATHS[current]:
                continue
            if key_token in FORBIDDEN_AUTHORITY_KEYS or (
                _text_has_affirmative_authority_claim(key)
            ) or (
                local_evaluator_context and _action_has_forbidden_semantics(key)
            ):
                if _authority_value_is_affirmative(nested):
                    _add(findings, "affirmative_forbidden_claim:" + ".".join(current))
                if isinstance(nested, (Mapping, list, tuple)):
                    _scan_forbidden_claims(
                        nested, findings, current, local_evaluator_context
                    )
                continue
            if isinstance(nested, (Mapping, list, tuple)):
                child_evaluator_context = local_evaluator_context or (
                    key_token == "evaluator"
                    or key_token.endswith("_evaluator")
                    or key_token.startswith("evaluator_")
                )
                _scan_forbidden_claims(
                    nested, findings, current, child_evaluator_context
                )
            elif isinstance(nested, str):
                if _token(nested) in REQUIRED_FORBIDDEN_OUTPUTS:
                    _add(
                        findings,
                        "forbidden_output_token_used_as_value:" + ".".join(current),
                    )
                elif _text_has_affirmative_authority_claim(nested):
                    _add(
                        findings,
                        "affirmative_evaluator_authority_prose:" + ".".join(current),
                    )
    elif isinstance(value, (list, tuple)):
        for index, nested in enumerate(value):
            _scan_forbidden_claims(
                nested,
                findings,
                path + (str(index),),
                evaluator_context,
            )
    elif isinstance(value, str):
        if _token(value) in REQUIRED_FORBIDDEN_OUTPUTS:
            _add(findings, "forbidden_output_token_used_as_value:" + ".".join(path))
        elif _text_has_affirmative_authority_claim(value):
            _add(findings, "affirmative_evaluator_authority_prose:" + ".".join(path))


def _valid_outputs() -> list[str]:
    return [
        "m14_final_completion_valid",
        "m14_completion_declared",
        "final_m14_completion_review_recorded",
        "issue_201_closes_on_merge",
        "repository_release_state_prepared",
        "github_release_pending_manual_publication",
    ]


def _invalid_outputs(escalation: bool) -> list[str]:
    outputs = ["m14_final_completion_invalid", "review_required"]
    if escalation:
        outputs.append("escalation_required")
    return outputs


def _baseline_matches(
    declared: Mapping[str, Any], candidate: Mapping[str, Any]
) -> bool:
    if not declared:
        return False
    for field, expected in declared.items():
        if field not in candidate:
            return False
        actual = candidate[field]
        if field == "outputs":
            if list(_as_sequence(expected)) != list(_as_sequence(actual)):
                return False
        elif expected != actual:
            return False
    return True


def evaluate_m14_final_completion(
    payload: dict[str, Any], repository_root: str | Path | None = None
) -> dict[str, Any]:
    """Validate the reviewed M14 transition without exercising release authority."""

    findings: list[str] = []
    missing: list[str] = []
    if not isinstance(payload, dict):
        payload = {}
        _add(findings, "final_completion_payload_invalid")
        _add(missing, "artifact")
    root = _repository_root(repository_root)

    top_valid, top_authority_valid = _validate_top_level(payload, findings, missing)
    release_valid, release_authority_valid = _validate_release_boundary(
        payload, findings, missing
    )
    bundle_present, bundle_integrity, readiness_fixture = _validate_bundle(
        payload, root, findings, missing
    )
    readiness_state_valid = _validate_pre_transition(
        payload, readiness_fixture, findings, missing
    )
    linkage_valid = _validate_linkage_and_packet(payload, findings, missing)
    manual_steps_valid = _validate_manual_steps(payload, findings)
    catalogs_valid = _validate_catalogs_and_authority(payload, findings)
    supporting_valid = _validate_supporting_content(payload, findings)
    readme_valid = _validate_readme(root, findings, missing)

    authority_findings: list[str] = []
    _scan_forbidden_claims(payload, authority_findings)
    for finding in authority_findings:
        _add(findings, finding)
    authority_valid = bool(
        top_authority_valid
        and release_authority_valid
        and catalogs_valid
        and not authority_findings
    )

    core_valid = bool(
        top_valid
        and release_valid
        and bundle_present
        and bundle_integrity
        and readiness_state_valid
        and linkage_valid
        and manual_steps_valid
        and catalogs_valid
        and supporting_valid
        and readme_valid
        and authority_valid
        and not findings
        and not missing
    )

    candidate = {
        "valid": core_valid,
        "m14_final_completion_valid": core_valid,
        "m14_final_completion_invalid": not core_valid,
        "m14_completion_declared": core_valid,
        "final_m14_completion_review_recorded": core_valid,
        "issue_201_closes_on_merge": core_valid,
        "repository_release_state_prepared": core_valid,
        "github_release_pending_manual_publication": core_valid,
        "completion_readiness_bundle_present": bundle_present,
        "completion_readiness_bundle_integrity_valid": bundle_integrity,
        "completion_readiness_state_valid": readiness_state_valid,
        "readme_release_state_valid": readme_valid,
        "manual_release_steps_valid": manual_steps_valid,
        "authority_boundaries_preserved": authority_valid,
        "final_completion_findings": sorted(findings),
        "findings": sorted(findings),
        "missing_evidence": sorted(missing),
        "outputs": _valid_outputs() if core_valid else _invalid_outputs(not authority_valid),
        "review_required": not core_valid,
        "escalation_required": not authority_valid,
    }
    if core_valid and not _baseline_matches(
        _as_mapping(payload.get("expected_baseline_result")), candidate
    ):
        _add(findings, "expected_baseline_result_invalid")
        core_valid = False

    outputs = _valid_outputs() if core_valid else _invalid_outputs(not authority_valid)
    return {
        "valid": core_valid,
        "m14_final_completion_valid": core_valid,
        "m14_final_completion_invalid": not core_valid,
        "m14_completion_declared": core_valid,
        "final_m14_completion_review_recorded": core_valid,
        "issue_201_closes_on_merge": core_valid,
        "repository_release_state_prepared": core_valid,
        "github_release_pending_manual_publication": core_valid,
        "completion_readiness_bundle_present": bundle_present,
        "completion_readiness_bundle_integrity_valid": bundle_integrity,
        "completion_readiness_state_valid": readiness_state_valid,
        "readme_release_state_valid": readme_valid,
        "manual_release_steps_valid": manual_steps_valid,
        "authority_boundaries_preserved": authority_valid,
        "final_completion_findings": sorted(findings),
        "findings": sorted(findings),
        "missing_evidence": sorted(missing),
        "outputs": outputs,
        "review_required": not core_valid,
        "escalation_required": not authority_valid,
    }


def validate_m14_final_completion(
    payload: dict[str, Any], repository_root: str | Path | None = None
) -> dict[str, Any]:
    """Return the complete deterministic final-completion result."""

    return evaluate_m14_final_completion(payload, repository_root)


def evaluate_file(
    path: str | Path, repository_root: str | Path | None = None
) -> dict[str, Any]:
    """Load and evaluate a final-completion artifact as inert JSON."""

    return evaluate_m14_final_completion(load_fixture(path), repository_root)
