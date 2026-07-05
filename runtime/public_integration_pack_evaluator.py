"""Deterministic checks for M11 public integration pack pilot evidence."""

from __future__ import annotations

from typing import Any


REQUIRED_PACK_FIELDS = {
    "integration_boundary_contract": "missing_integration_boundary_contract",
    "evidence_schema_reference": "missing_evidence_schema_reference",
    "replay_packet_example": "missing_replay_packet_example",
    "release_proof_linkage": "missing_release_proof_linkage",
    "sealing_boundary_statement": "missing_sealing_boundary_statement",
    "adapter_registry_entry_reference": "missing_adapter_registry_entry_reference",
    "evaluator_check_reference": "missing_evaluator_check_reference",
    "readme_integration_status_language": "missing_readme_integration_status_language",
    "governance_boundary_language": "missing_governance_boundary_language",
    "not_authority_statement": "missing_not_authority_statement",
    "aaos_retained_authority_statement": "missing_aaos_retained_authority_statement",
}

REQUIRED_CONSUMER_FIELDS = {
    "sealed_artifacts": "missing_sealed_artifact_semantics",
    "non_sealed_artifacts": "missing_non_sealed_artifact_semantics",
    "replayable_evidence": "missing_replayable_evidence",
    "evaluator_findings": "missing_evaluator_findings",
    "release_proof_evidence": "missing_release_proof_evidence",
    "governance_ci_findings": "missing_governance_ci_findings",
    "human_review_state": "missing_human_review_state",
    "sealing_eligibility": "missing_sealing_eligibility",
    "final_aaos_owned_sealing_authority": "missing_final_aaos_owned_sealing_authority",
    "artifact_consumption_semantics": "missing_artifact_consumption_semantics",
    "not_authority_statement": "missing_not_authority_statement",
    "aaos_retained_authority_statement": "missing_aaos_retained_authority_statement",
}

REQUIRED_TRACEABILITY_FIELDS = {
    "traceability_id": "missing_traceability_id",
    "m11_tracker_issue": "missing_m11_tracker_issue_120",
    "tracker_issue_closure_state": "missing_tracker_issue_120_open_state",
    "tracker_issue_linkage": "missing_tracker_issue_120_reference",
    "first_m11_pilot_pr": "missing_first_m11_pilot_pr_121",
    "m11_readme_wip_sync_pr": "missing_m11_readme_wip_sync_pr_131",
    "public_integration_pack_pilot_package": "missing_public_integration_pack_pilot_package",
    "external_evidence_consumer_specimen": "missing_external_evidence_consumer_specimen",
    "deterministic_public_integration_pack_evaluator": "missing_deterministic_public_integration_pack_evaluator",
    "evaluator_tests": "missing_evaluator_tests",
    "readme_current_work_status": "missing_readme_current_work_status",
    "release_proof_linkage": "missing_release_proof_linkage",
    "registry_facing_traceability": "missing_registry_traceability",
    "aaos_retained_authority_statement": "missing_aaos_retained_authority_statement",
    "decision_proof_sealing_boundary_preservation": "missing_decision_proof_sealing_boundary_preservation",
    "v0_10_0_future_completion_release_reservation": "missing_v0_10_0_future_completion_release_reservation",
    "not_authority_statement": "missing_not_authority_statement",
    "sovereignty_statement": "missing_sovereignty_statement",
}

REQUIRED_REGISTRY_TRACEABILITY_FIELDS = {
    "registry_traceability_id": "missing_registry_traceability_id",
    "pilot_identity": "missing_public_integration_pack_pilot_identity",
    "evidence_interface_role": "missing_evidence_interface_role",
    "external_evidence_consumer_role": "missing_external_evidence_consumer_role",
    "release_proof_linkage": "missing_release_proof_linkage",
    "replay_evaluator_linkage": "missing_replay_evaluator_linkage",
    "artifact_consumption_semantics_linkage": "missing_artifact_consumption_semantics_linkage",
    "governance_boundary_statement": "missing_governance_boundary_statement",
    "aaos_owned_final_authority_statement": "missing_aaos_owned_final_authority_statement",
    "registry_not_authority_statement": "missing_registry_not_authority_statement",
}

REQUIRED_CONSUMPTION_MATRIX_FIELDS = {
    "matrix_id": "missing_consumption_matrix_id",
    "m11_tracker_issue": "missing_m11_tracker_issue_120",
    "tracker_issue_closure_state": "missing_tracker_issue_120_open_state",
    "tracker_issue_linkage": "missing_tracker_issue_120_reference",
    "v0_10_0_release_state": "missing_v0_10_0_release_state",
    "artifact_consumption_matrix": "missing_artifact_consumption_matrix",
    "sealed_artifact_consumption_statement": "missing_sealed_artifact_consumption_statement",
    "non_sealed_artifact_consumption_statement": "missing_non_sealed_artifact_consumption_statement",
    "sealing_eligibility_statement": "missing_sealing_eligibility_statement",
    "fail_closed_recommendation_boundary": "missing_fail_closed_recommendation_boundary",
    "external_consumption_authority_statement": "missing_external_consumption_authority_statement",
    "decision_proof_sealing_boundary_statement": "missing_decision_proof_sealing_boundary_statement",
    "not_authority_statement": "missing_not_authority_statement",
}

REQUIRED_CONSUMER_FIXTURE_FIELDS = {
    "fixture_set_id": "missing_fixture_set_id",
    "m11_tracker_issue": "missing_m11_tracker_issue_120",
    "tracker_issue_closure_state": "missing_tracker_issue_120_open_state",
    "tracker_issue_linkage": "missing_tracker_issue_120_reference",
    "v0_10_0_release_state": "missing_v0_10_0_release_state",
    "compliant_fixtures": "missing_compliant_fixtures",
    "non_compliant_negative_fixtures": "missing_non_compliant_negative_fixtures",
    "not_authority_statement": "missing_not_authority_statement",
    "decision_proof_sealing_boundary_statement": "missing_decision_proof_sealing_boundary_statement",
}

REQUIRED_FAIL_CLOSED_EXAMPLE_FIELDS = {
    "example_set_id": "missing_fail_closed_example_set_id",
    "m11_tracker_issue": "missing_m11_tracker_issue_120",
    "tracker_issue_closure_state": "missing_tracker_issue_120_open_state",
    "tracker_issue_linkage": "missing_tracker_issue_120_reference",
    "v0_10_0_release_state": "missing_v0_10_0_release_state",
    "allowed_consumer_actions": "missing_allowed_consumer_actions",
    "forbidden_consumer_actions": "missing_forbidden_consumer_actions",
    "examples": "missing_fail_closed_examples",
    "not_authority_statement": "missing_not_authority_statement",
    "decision_proof_sealing_boundary_statement": "missing_decision_proof_sealing_boundary_statement",
}

REQUIRED_MATRIX_ALLOWED_ACTIONS = {
    "read",
    "reference",
    "inspect",
    "report",
    "preserve_linkage",
}

REQUIRED_MATRIX_SURFACE_ACTIONS = {
    "replay",
    "surface_review_requirement",
    "surface_escalation_requirement",
    "surface_fail_closed_recommendation",
}

REQUIRED_FAIL_CLOSED_ALLOWED_ACTIONS = {
    "surface_fail_closed_recommended",
    "preserve_evidence_link",
    "preserve_sealing_boundary",
    "escalate_to_aaos_review",
}

REQUIRED_FORBIDDEN_CONSUMER_ACTIONS = {
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
    "convert_non_sealed_artifacts_into_sealed_artifacts",
    "convert_sealing_eligibility_into_final_sealing",
}

EXPECTED_COMPLIANT_FIXTURE_IDS = {
    "compliant_replay_ready_reader",
    "compliant_aaos_sealed_reader",
    "compliant_review_required_surface",
    "compliant_fail_closed_recommendation_surface",
}

EXPECTED_NON_COMPLIANT_FIXTURE_IDS = {
    "negative_attempt_external_sealing",
    "negative_attempt_release_approval",
    "negative_attempt_v0_10_0_released",
    "negative_attempt_audit_close",
}

REQUIRED_CONSUMPTION_STATUSES = {
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

FORBIDDEN_AUTHORITY_OUTPUTS = {
    "decision_proof_sealed",
    "sealed_by_registry",
    "sealed_by_integration_pack",
    "sealed_by_external_consumer",
    "release_approved",
    "v0_10_0_released",
    "m11_complete",
    "fail_closed_executed",
    "closes_120",
    "risk_accepted",
    "rollback_executed",
    "audit_closed",
    "final_governance_judgment",
}

FORBIDDEN_AUTHORITY_PHRASES = {
    "integration pack seals decision proof",
    "external consumer seals decision proof",
    "registry seals decision proof",
    "integration pack approves release",
    "external consumer approves release",
    "registry approves release",
    "integration pack accepts risk",
    "external consumer accepts risk",
    "registry accepts risk",
    "integration pack executes rollback",
    "external consumer executes rollback",
    "registry executes rollback",
    "integration pack closes audit",
    "external consumer closes audit",
    "registry closes audit",
    "integration pack makes final governance judgment",
    "external consumer makes final governance judgment",
    "registry makes final governance judgment",
    "external consumer executes fail-closed",
    "external consumer treats v0.10.0 as released",
    "external consumer closes #120",
    "v0.10.0 is released",
    "m11 is complete",
}

SAFE_NEGATIVE_CONTEXT_KEYS = {
    "forbidden_pack_outputs",
    "forbidden_consumer_outputs",
    "forbidden_traceability_outputs",
    "forbidden_registry_traceability_outputs",
    "forbidden_matrix_outputs",
    "forbidden_fixture_outputs",
    "forbidden_fail_closed_outputs",
    "forbidden_consumer_actions",
    "forbidden_fail_closed_actions",
    "attempted_forbidden_action",
    "attempted_forbidden_output",
    "expected_evaluator_output",
    "expected_evaluator_outputs",
    "negative_fixture_boundary",
    "presentation_boundary",
    "forbidden_outputs",
    "forbidden_authority_outputs",
    "forbidden_authority_phrases",
    "not_authority_statement",
    "governance_boundary_language",
    "governance_boundary_statement",
    "registry_not_authority_statement",
    "authority_boundary",
    "authority_boundary_statement",
    "aaos_retained_authority_statement",
    "aaos_owned_final_authority_statement",
    "sealing_boundary_statement",
    "decision_proof_sealing_boundary_preservation",
}

TRACKER_120_CLOSURE_PHRASES = {
    "closes #120",
    "close #120",
    "closed #120",
    "fixes #120",
    "fixed #120",
    "resolves #120",
    "resolved #120",
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
        return value
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


def detect_forbidden_authority_claims(
    value: Any, parent_key: str | None = None
) -> set[str]:
    claims: set[str] = set()

    if isinstance(value, dict):
        for key, item in value.items():
            claims.update(detect_forbidden_authority_claims(item, str(key)))
        return claims

    if isinstance(value, list):
        for item in value:
            claims.update(detect_forbidden_authority_claims(item, parent_key))
        return claims

    if parent_key in SAFE_NEGATIVE_CONTEXT_KEYS:
        return claims

    normalized = _text(value)
    if normalized in FORBIDDEN_AUTHORITY_OUTPUTS:
        claims.add(normalized)

    for phrase in FORBIDDEN_AUTHORITY_PHRASES:
        if phrase in normalized:
            claims.add(phrase)

    return claims


def evaluate_public_integration_pack(record: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []

    for field, finding in REQUIRED_PACK_FIELDS.items():
        if not _has_value(record, field):
            findings.append(finding)
            missing_evidence.append(field)

    release_linkage = _as_dict(record.get("release_proof_linkage"))
    if release_linkage.get("present") is not True:
        findings.append("release_proof_linkage_missing")
        missing_evidence.append("release_proof_linkage")

    boundary_language = " ".join(
        [
            str(record.get("governance_boundary_language", "")),
            str(record.get("sealing_boundary_statement", "")),
            str(record.get("not_authority_statement", "")),
        ]
    ).lower()
    for required_phrase in [
        "decision proof sealing remains aaos-owned",
        "must not become governance authority",
        "final governance authority",
    ]:
        if required_phrase not in boundary_language:
            findings.append("missing_governance_boundary_language")
            missing_evidence.append("governance_boundary_language")
            break

    claims = detect_forbidden_authority_claims(record)
    return _result(
        mode="pack",
        findings=findings,
        missing_evidence=missing_evidence,
        authority_boundary_violation=bool(claims),
    )


def evaluate_external_evidence_consumer(record: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []

    for field, finding in REQUIRED_CONSUMER_FIELDS.items():
        if not _has_value(record, field):
            findings.append(finding)
            missing_evidence.append(field)

    final_authority = _as_dict(record.get("final_aaos_owned_sealing_authority"))
    if final_authority.get("owner") != "AAOS" or final_authority.get("delegated") is not False:
        findings.append("missing_final_aaos_owned_sealing_authority")
        missing_evidence.append("final_aaos_owned_sealing_authority")

    semantics_result = evaluate_artifact_consumption_semantics(record)
    findings.extend(semantics_result["integration_findings"])
    missing_evidence.extend(semantics_result["missing_evidence"])

    if not _as_list(record.get("release_proof_evidence")):
        findings.append("release_proof_linkage_missing")
        missing_evidence.append("release_proof_evidence")

    claims = detect_forbidden_authority_claims(record)
    return _result(
        mode="consumer",
        findings=findings,
        missing_evidence=missing_evidence,
        authority_boundary_violation=bool(claims),
    )


def evaluate_artifact_consumption_semantics(record: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    semantics = _as_dict(record.get("artifact_consumption_semantics"))

    for status in REQUIRED_CONSUMPTION_STATUSES:
        status_semantics = _as_dict(semantics.get(status))
        if not status_semantics:
            findings.append(f"missing_consumption_semantics_for_{status}")
            missing_evidence.append(f"artifact_consumption_semantics.{status}")
            continue
        if not _as_list(status_semantics.get("allowed_consumer_actions")):
            findings.append(f"missing_allowed_consumer_actions_for_{status}")
            missing_evidence.append(
                f"artifact_consumption_semantics.{status}.allowed_consumer_actions"
            )
        if not _has_value(status_semantics, "authority_boundary"):
            findings.append(f"missing_authority_boundary_for_{status}")
            missing_evidence.append(
                f"artifact_consumption_semantics.{status}.authority_boundary"
            )

    claims = detect_forbidden_authority_claims(record)
    return _result(
        mode="semantics",
        findings=findings,
        missing_evidence=missing_evidence,
        authority_boundary_violation=bool(claims),
    )


def evaluate_m11_pilot_traceability(record: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []

    for field, finding in REQUIRED_TRACEABILITY_FIELDS.items():
        if not _has_value(record, field):
            findings.append(finding)
            missing_evidence.append(field)

    if record.get("m11_tracker_issue") != "#120":
        findings.append("missing_m11_tracker_issue_120")
        missing_evidence.append("m11_tracker_issue")
    if record.get("first_m11_pilot_pr") != "#121":
        findings.append("missing_first_m11_pilot_pr_121")
        missing_evidence.append("first_m11_pilot_pr")
    if record.get("m11_readme_wip_sync_pr") != "#131":
        findings.append("missing_m11_readme_wip_sync_pr_131")
        missing_evidence.append("m11_readme_wip_sync_pr")

    tracker_state = _text(record.get("tracker_issue_closure_state"))
    if "open" not in tracker_state or tracker_state == "closed":
        findings.append("tracker_issue_120_not_marked_open")
        missing_evidence.append("tracker_issue_closure_state")
    if _has_tracker_120_closure_claim(record):
        findings.append("tracker_issue_120_closure_claim_detected")

    release_linkage = _as_dict(record.get("release_proof_linkage"))
    release_present = (
        bool(release_linkage)
        and release_linkage.get("present") is True
        and release_linkage.get("evidence_linkage_only") is True
    )
    if not release_present:
        findings.append("release_proof_linkage_missing")
        missing_evidence.append("release_proof_linkage")

    registry_present = _has_value(record, "registry_facing_traceability")
    if not registry_present:
        findings.append("registry_traceability_missing")
        missing_evidence.append("registry_facing_traceability")

    reservation = _text(record.get("v0_10_0_future_completion_release_reservation"))
    if "reserved" not in reservation or "not be treated as released" not in reservation:
        findings.append("v0_10_0_future_completion_release_reservation_missing")
        missing_evidence.append("v0_10_0_future_completion_release_reservation")

    boundary_language = " ".join(
        [
            str(record.get("decision_proof_sealing_boundary_preservation", "")),
            str(record.get("not_authority_statement", "")),
            str(record.get("aaos_retained_authority_statement", "")),
            str(record.get("sovereignty_statement", "")),
        ]
    ).lower()
    for required_phrase in [
        "decision proof sealing remains aaos-owned",
        "must not seal decision proof",
        "aaos remains the decision sovereignty layer",
    ]:
        if required_phrase not in boundary_language:
            findings.append("missing_authority_boundary_statement")
            missing_evidence.append("authority_boundary_statement")
            break

    claims = detect_forbidden_authority_claims(record)
    authority_boundary_violation = bool(claims)
    if "v0.10.0 is released" in reservation or reservation == "v0_10_0_released":
        findings.append("v0_10_0_release_claim_detected")
        authority_boundary_violation = True

    return _traceability_result(
        findings=findings,
        missing_evidence=missing_evidence,
        authority_boundary_violation=authority_boundary_violation,
        release_proof_linkage_present=release_present,
        registry_traceability_present=registry_present,
    )


def evaluate_registry_facing_traceability(record: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []

    for field, finding in REQUIRED_REGISTRY_TRACEABILITY_FIELDS.items():
        if not _has_value(record, field):
            findings.append(finding)
            missing_evidence.append(field)

    release_present = _has_value(record, "release_proof_linkage")
    registry_present = _has_value(record, "registry_traceability_id")

    boundary_language = " ".join(
        [
            str(record.get("governance_boundary_statement", "")),
            str(record.get("aaos_owned_final_authority_statement", "")),
            str(record.get("registry_not_authority_statement", "")),
        ]
    ).lower()
    for required_phrase in [
        "descriptive",
        "decision proof sealing remains aaos-owned",
        "aaos remains the decision sovereignty layer",
        "must not become governance authority",
    ]:
        if required_phrase not in boundary_language:
            findings.append("missing_registry_governance_boundary_statement")
            missing_evidence.append("governance_boundary_statement")
            break

    claims = detect_forbidden_authority_claims(record)
    return _traceability_result(
        findings=findings,
        missing_evidence=missing_evidence,
        authority_boundary_violation=bool(claims),
        release_proof_linkage_present=release_present,
        registry_traceability_present=registry_present,
    )



def evaluate_external_consumer_consumption_matrix(record: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []

    for field, finding in REQUIRED_CONSUMPTION_MATRIX_FIELDS.items():
        if not _has_value(record, field):
            findings.append(finding)
            missing_evidence.append(field)

    matrix = _as_dict(record.get("artifact_consumption_matrix"))
    covered_statuses = set(matrix)
    missing_statuses = REQUIRED_CONSUMPTION_STATUSES - covered_statuses
    for status in missing_statuses:
        findings.append(f"missing_artifact_status_{status}")
        missing_evidence.append(f"artifact_consumption_matrix.{status}")

    all_allowed_actions: set[str] = set()
    all_forbidden_actions: set[str] = set()
    authority_boundary_violation = False

    for status in REQUIRED_CONSUMPTION_STATUSES:
        entry = _as_dict(matrix.get(status))
        if not entry:
            continue
        allowed_actions = _as_set(entry.get("allowed_consumer_actions"))
        forbidden_actions = _as_set(entry.get("forbidden_consumer_actions"))
        all_allowed_actions.update(allowed_actions)
        all_forbidden_actions.update(forbidden_actions)

        missing_allowed = REQUIRED_MATRIX_ALLOWED_ACTIONS - allowed_actions
        if missing_allowed:
            findings.append(f"missing_allowed_consumption_actions_for_{status}")
            missing_evidence.append(
                f"artifact_consumption_matrix.{status}.allowed_consumer_actions"
            )

        missing_forbidden = REQUIRED_FORBIDDEN_CONSUMER_ACTIONS - forbidden_actions
        if missing_forbidden:
            findings.append(f"missing_forbidden_authority_actions_for_{status}")
            missing_evidence.append(
                f"artifact_consumption_matrix.{status}.forbidden_consumer_actions"
            )

        leaked_actions = REQUIRED_FORBIDDEN_CONSUMER_ACTIONS & allowed_actions
        if leaked_actions:
            findings.append(f"forbidden_authority_actions_allowed_for_{status}")
            authority_boundary_violation = True

        if status != "aaos_sealed_decision_proof_artifacts":
            if "convert_non_sealed_artifacts_into_sealed_artifacts" not in forbidden_actions:
                findings.append(f"missing_non_sealed_conversion_boundary_for_{status}")
                missing_evidence.append(
                    f"artifact_consumption_matrix.{status}.forbidden_consumer_actions"
                )
        if status == "sealing_eligible_evidence":
            if "convert_sealing_eligibility_into_final_sealing" not in forbidden_actions:
                findings.append("missing_sealing_eligibility_boundary")
                missing_evidence.append(
                    "artifact_consumption_matrix.sealing_eligible_evidence.forbidden_consumer_actions"
                )

    if not REQUIRED_MATRIX_SURFACE_ACTIONS <= all_allowed_actions:
        findings.append("allowed_consumption_actions_missing")
        missing_evidence.append("artifact_consumption_matrix.allowed_consumer_actions")

    if not REQUIRED_FORBIDDEN_CONSUMER_ACTIONS <= all_forbidden_actions:
        findings.append("forbidden_authority_actions_missing")
        missing_evidence.append("artifact_consumption_matrix.forbidden_consumer_actions")

    boundary_language = " ".join(
        [
            str(record.get("sealed_artifact_consumption_statement", "")),
            str(record.get("non_sealed_artifact_consumption_statement", "")),
            str(record.get("sealing_eligibility_statement", "")),
            str(record.get("fail_closed_recommendation_boundary", "")),
            str(record.get("external_consumption_authority_statement", "")),
            str(record.get("decision_proof_sealing_boundary_statement", "")),
            str(record.get("not_authority_statement", "")),
            str(record.get("sovereignty_statement", "")),
        ]
    ).lower()
    for required_phrase in [
        "sealed artifacts may be consumed as aaos-sealed artifacts",
        "non-sealed artifacts may be consumed only according to their status",
        "sealing eligibility is not sealing",
        "external consumption is not authority transfer",
        "decision proof sealing remains aaos-owned",
    ]:
        if required_phrase not in boundary_language:
            findings.append("missing_consumption_boundary_language")
            missing_evidence.append("consumption_boundary_language")
            break

    if record.get("m11_tracker_issue") != "#120":
        findings.append("missing_m11_tracker_issue_120")
        missing_evidence.append("m11_tracker_issue")
    tracker_state = _text(record.get("tracker_issue_closure_state"))
    if "open" not in tracker_state or tracker_state == "closed":
        findings.append("tracker_issue_120_not_marked_open")
        missing_evidence.append("tracker_issue_closure_state")
    if _has_tracker_120_closure_claim(record):
        findings.append("tracker_issue_120_closure_claim_detected")
        authority_boundary_violation = True
    if _has_v0_10_0_release_claim(record):
        findings.append("v0_10_0_release_claim_detected")
        authority_boundary_violation = True

    authority_boundary_violation = authority_boundary_violation or bool(
        detect_forbidden_authority_claims(record)
    )
    return _consumer_consumption_result(
        findings=findings,
        missing_evidence=missing_evidence,
        authority_boundary_violation=authority_boundary_violation,
        artifact_status_coverage_complete=not missing_statuses,
        allowed_consumption_actions_present=not any(
            "allowed_consumption_actions" in finding for finding in findings
        ),
        forbidden_authority_actions_present=not any(
            "forbidden_authority_actions" in finding for finding in findings
        ),
    )


def evaluate_external_consumer_fixtures(record: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    authority_boundary_violation = False

    for field, finding in REQUIRED_CONSUMER_FIXTURE_FIELDS.items():
        if not _has_value(record, field):
            findings.append(finding)
            missing_evidence.append(field)

    compliant_fixtures = _as_list(record.get("compliant_fixtures"))
    negative_fixtures = _as_list(record.get("non_compliant_negative_fixtures"))
    compliant_ids = {_text(fixture.get("fixture_id")) for fixture in compliant_fixtures if isinstance(fixture, dict)}
    negative_ids = {_text(fixture.get("fixture_id")) for fixture in negative_fixtures if isinstance(fixture, dict)}

    missing_compliant = EXPECTED_COMPLIANT_FIXTURE_IDS - compliant_ids
    missing_negative = EXPECTED_NON_COMPLIANT_FIXTURE_IDS - negative_ids
    if missing_compliant:
        findings.append("missing_compliant_consumer_fixtures")
        missing_evidence.append("compliant_fixtures")
    if missing_negative:
        findings.append("missing_negative_consumer_fixtures")
        missing_evidence.append("non_compliant_negative_fixtures")

    for fixture in compliant_fixtures:
        if not isinstance(fixture, dict):
            findings.append("invalid_compliant_fixture")
            continue
        if detect_forbidden_authority_claims(fixture):
            findings.append("compliant_fixture_claims_authority")
            authority_boundary_violation = True
        if fixture.get("final_governance_judgment") is True:
            findings.append("compliant_fixture_makes_final_governance_judgment")
            authority_boundary_violation = True
        for forbidden_flag in [
            "fail_closed_executed",
            "rollback_executed",
            "release_approved",
            "risk_accepted",
            "decision_proof_sealed",
            "audit_closed",
        ]:
            if fixture.get(forbidden_flag) is True:
                findings.append(f"compliant_fixture_sets_{forbidden_flag}")
                authority_boundary_violation = True

    for fixture in negative_fixtures:
        if not isinstance(fixture, dict):
            findings.append("invalid_negative_fixture")
            continue
        if fixture.get("fixture_type") != "negative" or fixture.get("allowed_behavior") is not False:
            findings.append("negative_fixture_not_marked_negative")
            missing_evidence.append("non_compliant_negative_fixtures.allowed_behavior")
        if not fixture.get("attempted_forbidden_action") and not fixture.get("attempted_forbidden_output"):
            findings.append("negative_fixture_missing_attempted_forbidden_behavior")
            missing_evidence.append("non_compliant_negative_fixtures.attempted_forbidden_behavior")

    if record.get("m11_tracker_issue") != "#120":
        findings.append("missing_m11_tracker_issue_120")
        missing_evidence.append("m11_tracker_issue")
    if _has_tracker_120_closure_claim(record):
        findings.append("tracker_issue_120_closure_claim_detected")
        authority_boundary_violation = True
    if _has_v0_10_0_release_claim(record):
        findings.append("v0_10_0_release_claim_detected")
        authority_boundary_violation = True

    authority_boundary_violation = authority_boundary_violation or bool(
        detect_forbidden_authority_claims(record)
    )
    return _consumer_consumption_result(
        findings=findings,
        missing_evidence=missing_evidence,
        authority_boundary_violation=authority_boundary_violation,
        artifact_status_coverage_complete=True,
        allowed_consumption_actions_present=bool(compliant_fixtures),
        forbidden_authority_actions_present=bool(negative_fixtures),
    )


def evaluate_fail_closed_consumption_examples(record: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    authority_boundary_violation = False

    for field, finding in REQUIRED_FAIL_CLOSED_EXAMPLE_FIELDS.items():
        if not _has_value(record, field):
            findings.append(finding)
            missing_evidence.append(field)

    allowed_actions = _as_set(record.get("allowed_consumer_actions"))
    forbidden_actions = _as_set(record.get("forbidden_consumer_actions"))
    if not REQUIRED_FAIL_CLOSED_ALLOWED_ACTIONS <= allowed_actions:
        findings.append("allowed_consumption_actions_missing")
        missing_evidence.append("allowed_consumer_actions")
    for required_forbidden in [
        "execute_fail_closed",
        "execute_rollback",
        "approve_releases",
        "accept_risk",
        "seal_decision_proof",
        "close_audits",
        "make_final_governance_judgments",
    ]:
        if required_forbidden not in forbidden_actions:
            findings.append("forbidden_authority_actions_missing")
            missing_evidence.append("forbidden_consumer_actions")
            break

    for example in _as_list(record.get("examples")):
        if not isinstance(example, dict):
            findings.append("invalid_fail_closed_example")
            continue
        if example.get("consumer_output") != "fail_closed_recommended":
            findings.append("fail_closed_example_missing_recommendation_output")
            missing_evidence.append("examples.consumer_output")
        for forbidden_flag in [
            "fail_closed_executed",
            "rollback_executed",
            "release_approved",
            "risk_accepted",
            "decision_proof_sealed",
            "audit_closed",
            "final_governance_judgment",
        ]:
            if example.get(forbidden_flag) is True:
                findings.append(f"{forbidden_flag}_detected")
                authority_boundary_violation = True
        for required_flag in ["preserves_evidence_link", "preserves_sealing_boundary"]:
            if example.get(required_flag) is not True:
                findings.append(f"missing_{required_flag}")
                missing_evidence.append(f"examples.{required_flag}")

    if _has_tracker_120_closure_claim(record):
        findings.append("tracker_issue_120_closure_claim_detected")
        authority_boundary_violation = True
    if _has_v0_10_0_release_claim(record):
        findings.append("v0_10_0_release_claim_detected")
        authority_boundary_violation = True

    authority_boundary_violation = authority_boundary_violation or bool(
        detect_forbidden_authority_claims(record)
    )
    return _consumer_consumption_result(
        findings=findings,
        missing_evidence=missing_evidence,
        authority_boundary_violation=authority_boundary_violation,
        artifact_status_coverage_complete=True,
        allowed_consumption_actions_present="allowed_consumption_actions_missing" not in findings,
        forbidden_authority_actions_present="forbidden_authority_actions_missing" not in findings,
    )


def _has_v0_10_0_release_claim(record: dict[str, Any]) -> bool:
    for item in _iter_claim_text(record):
        if item == "v0_10_0_released" or "v0.10.0 is released" in item:
            return True
    return False

def _has_tracker_120_closure_claim(record: dict[str, Any]) -> bool:
    for item in _iter_claim_text(record):
        if any(phrase in item for phrase in TRACKER_120_CLOSURE_PHRASES):
            return True
    return False



def _consumer_consumption_result(
    findings: list[str],
    missing_evidence: list[str],
    authority_boundary_violation: bool,
    artifact_status_coverage_complete: bool,
    allowed_consumption_actions_present: bool,
    forbidden_authority_actions_present: bool,
) -> dict[str, Any]:
    unique_findings = sorted(set(findings))
    unique_missing = sorted(set(missing_evidence))
    failed = bool(unique_findings or unique_missing or authority_boundary_violation)

    return {
        "consumer_consumption_matrix_valid": not failed,
        "consumer_consumption_matrix_invalid": failed,
        "artifact_status_coverage_complete": artifact_status_coverage_complete,
        "artifact_status_coverage_incomplete": not artifact_status_coverage_complete,
        "allowed_consumption_actions_present": allowed_consumption_actions_present,
        "forbidden_authority_actions_present": forbidden_authority_actions_present,
        "authority_boundary_preserved": not authority_boundary_violation,
        "authority_boundary_violation": authority_boundary_violation,
        "consumption_findings": unique_findings,
        "missing_evidence": unique_missing,
        "review_required": failed,
        "escalation_required": authority_boundary_violation,
        "fail_closed_recommended": authority_boundary_violation,
    }

def _result(
    mode: str,
    findings: list[str],
    missing_evidence: list[str],
    authority_boundary_violation: bool,
) -> dict[str, Any]:
    unique_findings = sorted(set(findings))
    unique_missing = sorted(set(missing_evidence))
    failed = bool(unique_findings or unique_missing or authority_boundary_violation)

    return {
        "public_integration_pack_valid": not failed if mode == "pack" else not authority_boundary_violation,
        "public_integration_pack_invalid": failed if mode == "pack" else authority_boundary_violation,
        "external_consumer_valid": not failed if mode == "consumer" else not authority_boundary_violation,
        "external_consumer_invalid": failed if mode == "consumer" else authority_boundary_violation,
        "artifact_consumption_semantics_present": not failed if mode == "semantics" else not any("consumption_semantics" in finding for finding in unique_findings),
        "artifact_consumption_semantics_missing": failed if mode == "semantics" else any("consumption_semantics" in finding for finding in unique_findings),
        "release_proof_linkage_present": "release_proof_linkage_missing" not in unique_findings,
        "release_proof_linkage_missing": "release_proof_linkage_missing" in unique_findings,
        "authority_boundary_preserved": not authority_boundary_violation,
        "authority_boundary_violation": authority_boundary_violation,
        "integration_findings": unique_findings,
        "missing_evidence": unique_missing,
        "review_required": failed,
        "escalation_required": authority_boundary_violation,
        "fail_closed_recommended": authority_boundary_violation,
    }


def _traceability_result(
    findings: list[str],
    missing_evidence: list[str],
    authority_boundary_violation: bool,
    release_proof_linkage_present: bool,
    registry_traceability_present: bool,
) -> dict[str, Any]:
    unique_findings = sorted(set(findings))
    unique_missing = sorted(set(missing_evidence))
    failed = bool(unique_findings or unique_missing or authority_boundary_violation)

    return {
        "m11_pilot_traceability_valid": not failed,
        "m11_pilot_traceability_invalid": failed,
        "release_proof_linkage_present": release_proof_linkage_present and "release_proof_linkage_missing" not in unique_findings,
        "release_proof_linkage_missing": not release_proof_linkage_present or "release_proof_linkage_missing" in unique_findings,
        "registry_traceability_present": registry_traceability_present and "registry_traceability_missing" not in unique_findings,
        "registry_traceability_missing": not registry_traceability_present or "registry_traceability_missing" in unique_findings,
        "authority_boundary_preserved": not authority_boundary_violation,
        "authority_boundary_violation": authority_boundary_violation,
        "traceability_findings": unique_findings,
        "missing_evidence": unique_missing,
        "review_required": failed,
        "escalation_required": authority_boundary_violation,
        "fail_closed_recommended": authority_boundary_violation,
    }
