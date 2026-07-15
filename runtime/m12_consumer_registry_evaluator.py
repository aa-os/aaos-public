"""Deterministic checks for M12 consumer registry evidence."""

from __future__ import annotations

from typing import Any


REQUIRED_REGISTRY_FIELDS = {
    "registry_id": "missing_registry_id",
    "registry_name": "missing_registry_name",
    "registry_scope": "missing_registry_scope",
    "registry_status": "missing_registry_status",
    "m12_completion_status": "missing_m12_completion_status",
    "related_issue": "missing_related_issue_168",
    "tracker_issue_closure_state": "missing_tracker_issue_168_open_state",
    "tracker_issue_linkage": "missing_tracker_issue_168_reference",
    "introduced_after_release": "missing_introduced_after_release_v0_10_0",
    "target_future_release": "missing_target_future_release_v0_11_0",
    "release_status_path": "missing_release_status_path",
    "consumer_entries": "missing_consumer_entries",
    "negative_consumer_registry_fixtures": "missing_negative_consumer_registry_fixtures",
    "sealed_nonsealed_consumption_semantics": "missing_sealed_nonsealed_consumption_semantics",
    "registry_inclusion_boundary": "missing_registry_inclusion_boundary",
    "ci_pass_boundary": "missing_ci_pass_boundary",
    "release_proof_boundary": "missing_release_proof_boundary",
    "fail_closed_boundary": "missing_fail_closed_boundary",
    "decision_proof_sealing_boundary_statement": "missing_decision_proof_sealing_boundary_statement",
    "aaos_retained_authority_statement": "missing_aaos_retained_authority_statement",
    "governance_boundary_statement": "missing_governance_boundary_statement",
    "sovereignty_statement": "missing_sovereignty_statement",
    "allowed_evaluator_outputs": "missing_allowed_evaluator_outputs",
    "forbidden_evaluator_outputs": "missing_forbidden_evaluator_outputs",
}

REQUIRED_CONSUMER_ENTRY_FIELDS = {
    "entry_id": "missing_consumer_entry_id",
    "entry_type": "missing_consumer_entry_type",
    "allowed_behavior": "missing_consumer_allowed_behavior",
    "consumer_identity": "missing_consumer_identity",
    "consumer_role": "missing_consumer_role",
    "consumed_artifact_types": "missing_consumed_artifact_types",
    "allowed_consumption_actions": "missing_allowed_consumption_actions",
    "forbidden_authority_actions": "missing_forbidden_authority_actions",
    "sealed_artifact_consumption_semantics": "missing_sealed_artifact_consumption_semantics",
    "non_sealed_artifact_consumption_semantics": "missing_non_sealed_artifact_consumption_semantics",
    "replay_compatibility": "missing_replay_compatibility",
    "evaluator_compatibility": "missing_evaluator_compatibility",
    "release_proof_linkage": "missing_release_proof_linkage",
    "registry_entry_provenance": "missing_registry_entry_provenance",
    "aaos_retained_authority_statement": "missing_entry_aaos_retained_authority_statement",
    "governance_boundary_statement": "missing_entry_governance_boundary_statement",
}

REQUIRED_NEGATIVE_FIXTURE_FIELDS = {
    "fixture_id": "missing_negative_fixture_id",
    "fixture_type": "missing_negative_fixture_type",
    "allowed_behavior": "missing_negative_fixture_allowed_behavior",
    "negative_fixture_boundary": "missing_negative_fixture_boundary",
    "attempted_forbidden_actions": "missing_attempted_forbidden_actions",
    "attempted_forbidden_outputs": "missing_attempted_forbidden_outputs",
    "expected_evaluator_outputs": "missing_expected_evaluator_outputs",
}

REQUIRED_CONSUMED_ARTIFACT_TYPES = {
    "unsealed_evidence",
    "replay_ready_packets",
    "evidence_complete_packets",
    "evaluator_findings",
    "sealing_eligible_evidence",
    "aaos_sealed_decision_proof_artifacts",
    "sealing_rejected_artifacts",
    "sealing_deferred_artifacts",
    "sealing_blocked_artifacts",
}

REQUIRED_ALLOWED_CONSUMPTION_ACTIONS = {
    "read_aaos_artifacts",
    "reference_aaos_artifacts",
    "replay_replay_ready_packets",
    "inspect_evaluator_findings",
    "report_review_required",
    "report_escalation_required",
    "surface_fail_closed_recommended",
    "preserve_evidence_linkage",
    "preserve_release_proof_linkage",
    "preserve_sealed_nonsealed_semantics",
}

REQUIRED_FORBIDDEN_AUTHORITY_ACTIONS = {
    "seal_decision_proof",
    "approve_releases",
    "accept_risk",
    "execute_rollback",
    "execute_fail_closed",
    "close_audits",
    "grant_waivers",
    "change_approval_doctrine",
    "change_identity_trust",
    "change_policy_authority",
    "change_decision_routing",
    "make_final_governance_judgments",
}

REQUIRED_EVALUATOR_OUTPUTS = {
    "consumer_registry_valid",
    "consumer_registry_invalid",
    "required_registry_fields_present",
    "required_registry_fields_missing",
    "compliant_consumer_entry_present",
    "compliant_consumer_entry_missing",
    "negative_consumer_fixture_present",
    "negative_consumer_fixture_missing",
    "authority_boundary_preserved",
    "authority_boundary_violation",
    "sealed_nonsealed_semantics_preserved",
    "release_status_future_only",
    "review_required",
    "escalation_required",
    "fail_closed_recommended",
}

FORBIDDEN_EVALUATOR_OUTPUTS = {
    "decision_proof_sealed",
    "sealed_by_external_consumer",
    "release_approved",
    "risk_accepted",
    "rollback_executed",
    "fail_closed_executed",
    "audit_closed",
    "final_governance_judgment",
    "v0_11_0_released",
    "m12_complete",
    "closes_168",
}

FORBIDDEN_AUTHORITY_PHRASES = {
    "external consumer seals decision proof",
    "consumer registry seals decision proof",
    "registry seals decision proof",
    "external consumer approves release",
    "consumer registry approves release",
    "registry approves release",
    "external consumer accepts risk",
    "consumer registry accepts risk",
    "registry accepts risk",
    "external consumer executes rollback",
    "consumer registry executes rollback",
    "registry executes rollback",
    "external consumer executes fail-closed",
    "consumer registry executes fail-closed",
    "registry executes fail-closed",
    "external consumer closes audit",
    "consumer registry closes audit",
    "registry closes audit",
    "external consumer makes final governance judgment",
    "consumer registry makes final governance judgment",
    "registry makes final governance judgment",
    "registry inclusion is approval",
    "ci pass is approval",
    "release proof linkage is release approval",
    "fail_closed_recommended is fail_closed_executed",
    "sealing_eligible is sealed",
    "v0.11.0 is released",
    "m12 is complete",
}

SAFE_NEGATIVE_CONTEXT_KEYS = {
    "forbidden_evaluator_outputs",
    "forbidden_authority_actions",
    "attempted_forbidden_actions",
    "attempted_forbidden_outputs",
    "expected_evaluator_outputs",
    "negative_fixture_boundary",
    "not_authority_statement",
    "governance_boundary_statement",
    "aaos_retained_authority_statement",
    "decision_proof_sealing_boundary_statement",
}

TRACKER_168_CLOSURE_PHRASES = {
    "closes #168",
    "close #168",
    "closed #168",
    "fixes #168",
    "fixed #168",
    "resolves #168",
    "resolved #168",
}

BOUNDARY_CLAIM_FINDINGS = {
    "registry inclusion is approval": "registry_inclusion_approval_claim_detected",
    "ci pass is approval": "ci_pass_approval_claim_detected",
    "release proof linkage is release approval": "release_proof_release_approval_claim_detected",
    "fail_closed_recommended is fail_closed_executed": "fail_closed_execution_claim_detected",
    "sealing_eligible is sealed": "sealing_eligibility_sealed_claim_detected",
}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_set(value: Any) -> set[str]:
    return {str(item).strip() for item in _as_list(value) if str(item).strip()}


def _has_value(record: dict[str, Any], field: str) -> bool:
    value = record.get(field)
    if isinstance(value, bool):
        return True
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return value is not None


def _text(value: Any) -> str:
    return str(value).strip().lower()


def _iter_claim_text(value: Any, parent_key: str | None = None) -> list[str]:
    if isinstance(value, dict):
        text: list[str] = []
        for key, item in value.items():
            text.extend(_iter_claim_text(item, str(key)))
        return text

    if isinstance(value, list):
        text = []
        for item in value:
            text.extend(_iter_claim_text(item, parent_key))
        return text

    if parent_key in SAFE_NEGATIVE_CONTEXT_KEYS:
        return []

    return [_text(value)]


def _boundary_language(record: dict[str, Any]) -> str:
    semantics = _as_dict(record.get("sealed_nonsealed_consumption_semantics"))
    return " ".join(
        [
            str(semantics.get("sealed_artifacts", "")),
            str(semantics.get("non_sealed_artifacts", "")),
            str(semantics.get("sealing_eligibility_boundary", "")),
            str(semantics.get("external_consumption_boundary", "")),
            str(semantics.get("non_sealed_conversion_boundary", "")),
            str(record.get("registry_inclusion_boundary", "")),
            str(record.get("ci_pass_boundary", "")),
            str(record.get("release_proof_boundary", "")),
            str(record.get("fail_closed_boundary", "")),
            str(record.get("decision_proof_sealing_boundary_statement", "")),
            str(record.get("aaos_retained_authority_statement", "")),
            str(record.get("governance_boundary_statement", "")),
            str(record.get("sovereignty_statement", "")),
        ]
    ).lower()


def detect_m12_forbidden_authority_claims(
    value: Any, parent_key: str | None = None
) -> set[str]:
    claims: set[str] = set()

    if isinstance(value, dict):
        for key, item in value.items():
            claims.update(detect_m12_forbidden_authority_claims(item, str(key)))
        return claims

    if isinstance(value, list):
        for item in value:
            claims.update(detect_m12_forbidden_authority_claims(item, parent_key))
        return claims

    if parent_key in SAFE_NEGATIVE_CONTEXT_KEYS:
        return claims

    normalized = _text(value)
    if normalized in FORBIDDEN_EVALUATOR_OUTPUTS:
        claims.add(normalized)

    for phrase in FORBIDDEN_AUTHORITY_PHRASES:
        if phrase in normalized:
            claims.add(phrase)

    return claims


def evaluate_m12_consumer_registry(record: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    authority_boundary_violation = False

    for field, finding in REQUIRED_REGISTRY_FIELDS.items():
        if not _has_value(record, field):
            findings.append(finding)
            missing_evidence.append(field)

    if record.get("related_issue") != "#168":
        findings.append("missing_related_issue_168")
        missing_evidence.append("related_issue")

    tracker_state = _text(record.get("tracker_issue_closure_state"))
    if "open" not in tracker_state or tracker_state == "closed":
        findings.append("tracker_issue_168_not_marked_open")
        missing_evidence.append("tracker_issue_closure_state")
    if _has_tracker_168_closure_claim(record):
        findings.append("tracker_issue_168_closure_claim_detected")
        authority_boundary_violation = True

    if record.get("introduced_after_release") != "v0.10.0":
        findings.append("missing_introduced_after_release_v0_10_0")
        missing_evidence.append("introduced_after_release")
    if record.get("target_future_release") != "v0.11.0":
        findings.append("missing_target_future_release_v0_11_0")
        missing_evidence.append("target_future_release")

    release_status_future_only = _release_status_future_only(record)
    if not release_status_future_only:
        findings.append("v0_11_0_future_release_state_missing")
        missing_evidence.append("release_status_path")
    if _has_v0_11_0_release_claim(record):
        findings.append("v0_11_0_release_claim_detected")
        authority_boundary_violation = True
    if _has_m12_completion_claim(record):
        findings.append("m12_completion_claim_detected")
        authority_boundary_violation = True

    compliant_entries = _compliant_entries(record)
    negative_fixtures = _negative_fixtures(record)
    if not compliant_entries:
        findings.append("compliant_consumer_entry_missing")
        missing_evidence.append("consumer_entries")
    if not negative_fixtures:
        findings.append("negative_consumer_fixture_missing")
        missing_evidence.append("negative_consumer_registry_fixtures")

    for entry in compliant_entries:
        _evaluate_compliant_entry(
            entry,
            findings=findings,
            missing_evidence=missing_evidence,
        )
        if _entry_claims_authority(entry):
            findings.append("compliant_consumer_entry_claims_authority")
            authority_boundary_violation = True

    for fixture in negative_fixtures:
        _evaluate_negative_fixture(
            fixture,
            findings=findings,
            missing_evidence=missing_evidence,
        )

    boundary_language = _boundary_language(record)
    sealed_nonsealed_semantics_preserved = _sealed_nonsealed_semantics_preserved(
        boundary_language
    )
    if not sealed_nonsealed_semantics_preserved:
        findings.append("sealed_nonsealed_semantics_missing")
        missing_evidence.append("sealed_nonsealed_consumption_semantics")

    for phrase, finding in BOUNDARY_CLAIM_FINDINGS.items():
        if phrase in boundary_language:
            findings.append(finding)
            authority_boundary_violation = True

    for required_phrase in [
        "decision proof sealing remains aaos-owned",
        "aaos remains the decision sovereignty layer",
        "aaos retains",
        "must not become governance authorities",
    ]:
        if required_phrase not in boundary_language:
            findings.append("missing_aaos_authority_boundary_statement")
            missing_evidence.append("aaos_retained_authority_statement")
            break

    allowed_outputs = _as_set(record.get("allowed_evaluator_outputs"))
    if not REQUIRED_EVALUATOR_OUTPUTS <= allowed_outputs:
        findings.append("missing_allowed_evaluator_outputs")
        missing_evidence.append("allowed_evaluator_outputs")
    if FORBIDDEN_EVALUATOR_OUTPUTS & allowed_outputs:
        findings.append("forbidden_evaluator_output_allowed")
        authority_boundary_violation = True

    claims = detect_m12_forbidden_authority_claims(record)
    if claims:
        findings.append("authority_transfer_claim_detected")
        authority_boundary_violation = True

    return _consumer_registry_result(
        findings=findings,
        missing_evidence=missing_evidence,
        authority_boundary_violation=authority_boundary_violation,
        required_registry_fields_present=not any(
            finding in findings for finding in REQUIRED_REGISTRY_FIELDS.values()
        ),
        compliant_consumer_entry_present=bool(compliant_entries),
        negative_consumer_fixture_present=bool(negative_fixtures),
        sealed_nonsealed_semantics_preserved=sealed_nonsealed_semantics_preserved,
        release_status_future_only=release_status_future_only,
    )


def _compliant_entries(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        entry
        for entry in _as_list(record.get("consumer_entries"))
        if isinstance(entry, dict)
        and entry.get("entry_type") == "compliant"
        and entry.get("allowed_behavior") is True
    ]


def _negative_fixtures(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        fixture
        for fixture in _as_list(record.get("negative_consumer_registry_fixtures"))
        if isinstance(fixture, dict)
    ]


def _evaluate_compliant_entry(
    entry: dict[str, Any],
    findings: list[str],
    missing_evidence: list[str],
) -> None:
    for field, finding in REQUIRED_CONSUMER_ENTRY_FIELDS.items():
        if not _has_value(entry, field):
            findings.append(finding)
            missing_evidence.append(f"consumer_entries.{field}")

    consumed_artifacts = _as_set(entry.get("consumed_artifact_types"))
    if not REQUIRED_CONSUMED_ARTIFACT_TYPES <= consumed_artifacts:
        findings.append("consumed_artifact_types_incomplete")
        missing_evidence.append("consumer_entries.consumed_artifact_types")

    allowed_actions = _as_set(entry.get("allowed_consumption_actions"))
    if not REQUIRED_ALLOWED_CONSUMPTION_ACTIONS <= allowed_actions:
        findings.append("allowed_consumption_actions_missing")
        missing_evidence.append("consumer_entries.allowed_consumption_actions")

    forbidden_actions = _as_set(entry.get("forbidden_authority_actions"))
    if not REQUIRED_FORBIDDEN_AUTHORITY_ACTIONS <= forbidden_actions:
        findings.append("forbidden_authority_actions_missing")
        missing_evidence.append("consumer_entries.forbidden_authority_actions")

    if REQUIRED_FORBIDDEN_AUTHORITY_ACTIONS & allowed_actions:
        findings.append("forbidden_authority_action_allowed")

    release_linkage = _as_dict(entry.get("release_proof_linkage"))
    if (
        release_linkage.get("present") is not True
        or release_linkage.get("evidence_linkage_only") is not True
        or release_linkage.get("release_approval") is not False
    ):
        findings.append("release_proof_linkage_missing")
        missing_evidence.append("consumer_entries.release_proof_linkage")

    for compatibility_field in ["replay_compatibility", "evaluator_compatibility"]:
        compatibility = _as_dict(entry.get(compatibility_field))
        if compatibility.get("compatible") is not True:
            findings.append(f"{compatibility_field}_missing")
            missing_evidence.append(f"consumer_entries.{compatibility_field}")


def _evaluate_negative_fixture(
    fixture: dict[str, Any],
    findings: list[str],
    missing_evidence: list[str],
) -> None:
    for field, finding in REQUIRED_NEGATIVE_FIXTURE_FIELDS.items():
        if not _has_value(fixture, field):
            findings.append(finding)
            missing_evidence.append(f"negative_consumer_registry_fixtures.{field}")

    if fixture.get("fixture_type") != "negative" or fixture.get("allowed_behavior") is not False:
        findings.append("negative_fixture_not_marked_negative")
        missing_evidence.append("negative_consumer_registry_fixtures.allowed_behavior")

    attempted_outputs = _as_set(fixture.get("attempted_forbidden_outputs"))
    attempted_actions = _as_set(fixture.get("attempted_forbidden_actions"))
    if not FORBIDDEN_EVALUATOR_OUTPUTS <= attempted_outputs:
        findings.append("negative_fixture_missing_forbidden_outputs")
        missing_evidence.append("negative_consumer_registry_fixtures.attempted_forbidden_outputs")
    if not {
        "seal_decision_proof",
        "approve_releases",
        "execute_rollback",
        "execute_fail_closed",
    } <= attempted_actions:
        findings.append("negative_fixture_missing_forbidden_actions")
        missing_evidence.append("negative_consumer_registry_fixtures.attempted_forbidden_actions")


def _entry_claims_authority(entry: dict[str, Any]) -> bool:
    if detect_m12_forbidden_authority_claims(entry):
        return True

    for forbidden_flag in [
        "decision_proof_sealed",
        "release_approved",
        "risk_accepted",
        "rollback_executed",
        "fail_closed_executed",
        "audit_closed",
        "final_governance_judgment",
    ]:
        if entry.get(forbidden_flag) is True:
            return True

    allowed_actions = _as_set(entry.get("allowed_consumption_actions"))
    return bool(REQUIRED_FORBIDDEN_AUTHORITY_ACTIONS & allowed_actions)


def _release_status_future_only(record: dict[str, Any]) -> bool:
    release_status = _as_dict(record.get("release_status_path"))
    release_text = " ".join(_iter_claim_text(release_status))
    return (
        record.get("target_future_release") == "v0.11.0"
        and release_status.get("state") == "future_target_release_only"
        and "future target release" in release_text
        and "not be treated as released" in release_text
        and not _has_v0_11_0_release_claim(record)
    )


def _sealed_nonsealed_semantics_preserved(boundary_language: str) -> bool:
    return all(
        phrase in boundary_language
        for phrase in [
            "aaos-sealed artifacts may be consumed as aaos-sealed artifacts",
            "non-sealed artifacts may be consumed only according to their status",
            "sealing_eligible is not sealed",
            "external consumption is not authority transfer",
            "non-sealed artifacts must not be converted into sealed artifacts",
            "registry inclusion is not approval",
            "ci pass is not approval",
            "release proof linkage is not release approval",
            "fail_closed_recommended is not fail_closed_executed",
            "decision proof sealing remains aaos-owned",
        ]
    )


def _has_v0_11_0_release_claim(record: dict[str, Any]) -> bool:
    for item in _iter_claim_text(record):
        if item == "v0_11_0_released" or "v0.11.0 is released" in item:
            return True
    return False


def _has_m12_completion_claim(record: dict[str, Any]) -> bool:
    for item in _iter_claim_text(record):
        if item == "m12_complete" or "m12 is complete" in item:
            return True
    return False


def _has_tracker_168_closure_claim(record: dict[str, Any]) -> bool:
    for item in _iter_claim_text(record):
        if item == "closes_168" or any(
            phrase in item for phrase in TRACKER_168_CLOSURE_PHRASES
        ):
            return True
    return False


def _consumer_registry_result(
    findings: list[str],
    missing_evidence: list[str],
    authority_boundary_violation: bool,
    required_registry_fields_present: bool,
    compliant_consumer_entry_present: bool,
    negative_consumer_fixture_present: bool,
    sealed_nonsealed_semantics_preserved: bool,
    release_status_future_only: bool,
) -> dict[str, Any]:
    unique_findings = sorted(set(findings))
    unique_missing = sorted(set(missing_evidence))
    failed = bool(unique_findings or unique_missing or authority_boundary_violation)

    return {
        "consumer_registry_valid": not failed,
        "consumer_registry_invalid": failed,
        "required_registry_fields_present": required_registry_fields_present,
        "required_registry_fields_missing": not required_registry_fields_present,
        "compliant_consumer_entry_present": compliant_consumer_entry_present,
        "compliant_consumer_entry_missing": not compliant_consumer_entry_present,
        "negative_consumer_fixture_present": negative_consumer_fixture_present,
        "negative_consumer_fixture_missing": not negative_consumer_fixture_present,
        "authority_boundary_preserved": not authority_boundary_violation,
        "authority_boundary_violation": authority_boundary_violation,
        "sealed_nonsealed_semantics_preserved": sealed_nonsealed_semantics_preserved,
        "release_status_future_only": release_status_future_only,
        "registry_findings": unique_findings,
        "missing_evidence": unique_missing,
        "review_required": failed,
        "escalation_required": authority_boundary_violation,
        "fail_closed_recommended": authority_boundary_violation,
    }
