"""Deterministic checks for M13 external consumer onboarding evidence."""

from __future__ import annotations

from typing import Any

from runtime.authority_semantics import scan_forbidden_authority_claims


REQUIRED_FIXTURE_FIELDS = {
    "fixture_id": "missing_fixture_id",
    "fixture_name": "missing_fixture_name",
    "fixture_scope": "missing_fixture_scope",
    "documentation_path": "missing_documentation_path",
    "artifact_status": "missing_artifact_status",
    "m13_completion_status": "missing_m13_completion_status",
    "related_issue": "missing_related_issue_176",
    "tracker_issue_closure_state": "missing_tracker_issue_176_open_state",
    "tracker_issue_linkage": "missing_tracker_issue_176_reference",
    "runtime_approval_gate_evidence_pr": "missing_runtime_approval_gate_evidence_pr_177",
    "registry_drift_detection_pr": "missing_registry_drift_detection_pr_178",
    "authority_boundary_regression_fixtures_pr": "missing_authority_boundary_regression_fixtures_pr_194",
    "operational_readiness_checklist_pr": "missing_operational_readiness_checklist_pr_195",
    "target_future_release": "missing_target_future_release_v0_12_0",
    "future_release_tag_path": "missing_future_release_tag_path",
    "release_status_path": "missing_release_status_path",
    "onboarding_status": "missing_onboarding_status",
    "external_consumer_role": "missing_external_consumer_role",
    "documentation_sections": "missing_documentation_sections",
    "onboarding_checklist": "missing_onboarding_checklist",
    "required_evidence_fields": "missing_required_evidence_fields",
    "prohibited_claims": "missing_prohibited_claims",
    "required_boundary_statements": "missing_required_boundary_statements",
    "semantic_boundaries": "missing_semantic_boundaries",
    "fail_closed_and_escalation_handling": "missing_fail_closed_and_escalation_handling",
    "reviewer_handoff": "missing_reviewer_handoff",
    "allowed_evaluator_outputs": "missing_allowed_evaluator_outputs",
    "forbidden_evaluator_outputs": "missing_forbidden_evaluator_outputs",
    "authority_boundary": "missing_authority_boundary",
    "governance_boundary_statement": "missing_governance_boundary_statement",
    "decision_proof_sealing_boundary_statement": "missing_decision_proof_sealing_boundary_statement",
    "aaos_retained_authority_statement": "missing_aaos_retained_authority_statement",
    "sovereignty_statement": "missing_sovereignty_statement",
}

REQUIRED_DOCUMENTATION_SECTIONS = {
    "external_consumer_role",
    "registry_inclusion_boundary",
    "evidence_consumption_boundary",
    "runtime_approval_evidence_boundary",
    "registry_drift_review_boundary",
    "authority_boundary_regression_boundary",
    "operational_readiness_review_boundary",
    "onboarding_checklist",
    "required_evidence_fields",
    "prohibited_claims",
    "fail_closed_and_escalation_handling",
    "reviewer_handoff",
    "future_only_v0_12_0_release_path",
    "m13_active_work_status",
    "aaos_owned_decision_proof_sealing",
    "aaos_final_governance_authority",
}

REQUIRED_ONBOARDING_CHECKS = {
    "identify_external_consumer",
    "record_consumer_role_and_artifact_scope",
    "record_allowed_and_forbidden_actions",
    "link_runtime_approval_evidence",
    "link_registry_drift_review",
    "link_authority_boundary_regression_fixtures",
    "link_operational_readiness_checklist",
    "confirm_future_only_release_path",
    "prepare_reviewer_handoff",
}

REQUIRED_EVIDENCE_FIELDS = {
    "consumer_id",
    "consumer_name",
    "consumer_role",
    "registry_entry_id",
    "consumed_artifact_types",
    "allowed_consumption_actions",
    "forbidden_authority_actions",
    "evidence_artifact_refs",
    "artifact_status",
    "sealed_status",
    "runtime_approval_evidence_ref",
    "registry_drift_review_ref",
    "authority_boundary_regression_ref",
    "operational_readiness_ref",
    "release_proof_linkage_ref",
    "reviewer_handoff",
    "aaos_retained_authority_statement",
}

REQUIRED_BOUNDARY_STATEMENTS = {
    "external consumer onboarding documentation does not grant authority.",
    "registry inclusion is not approval.",
    "evidence consumption is not approval.",
    "runtime approval evidence is not execution approval.",
    "registry drift detection is not approval.",
    "operational readiness is not approval.",
    "release proof linkage is not release approval.",
    "ready_for_review is not approval.",
    "evidence_complete is not sealed.",
    "replay_ready is not sealed.",
    "onboarding_complete is not approved.",
    "onboarding documentation must not close audits.",
    "onboarding documentation must not grant waivers.",
    "onboarding documentation must not make final governance judgments.",
    "decision proof sealing remains aaos-owned.",
    "aaos remains the decision sovereignty layer.",
}

REQUIRED_ALLOWED_OUTPUTS = {
    "onboarding_documentation_valid",
    "onboarding_documentation_invalid",
    "onboarding_boundary_preserved",
    "onboarding_boundary_violation",
    "onboarding_ready_for_review",
    "onboarding_not_ready",
    "review_required",
    "escalation_required",
    "fail_closed_recommended",
}

FORBIDDEN_EVALUATOR_OUTPUTS = {
    "consumer_approved",
    "registry_entry_approved",
    "onboarding_approved",
    "execution_approved_by_documentation",
    "release_approved",
    "risk_accepted",
    "decision_proof_sealed",
    "sealed_by_documentation",
    "audit_closed",
    "waiver_granted",
    "final_governance_judgment",
    "authority_transferred",
    "v0_12_0_released",
    "m13_complete",
    "closes_176",
}

REQUIRED_AUTHORITY_MAY = {
    "describe_required_evidence",
    "describe_onboarding_steps",
    "surface_review_required",
    "surface_escalation_required",
    "surface_fail_closed_recommended",
    "reference_registry_entries",
    "reference_runtime_approval_evidence",
    "reference_registry_drift_review",
    "reference_authority_boundary_regression",
    "reference_operational_readiness",
    "link_release_proof_evidence",
    "hand_off_to_reviewer",
}

REQUIRED_AUTHORITY_MUST_NOT = {
    "approve_consumers",
    "approve_registry_entries",
    "approve_execution",
    "approve_releases",
    "accept_risk",
    "execute_rollback",
    "execute_fail_closed",
    "seal_decision_proof",
    "close_audits",
    "grant_waivers",
    "transfer_authority",
    "make_final_governance_judgments",
}

BOUNDARY_CLAIM_FINDINGS = {
    "external consumer onboarding documentation grants authority": "onboarding_documentation_authority_grant_claim_detected",
    "onboarding documentation grants authority": "onboarding_documentation_authority_grant_claim_detected",
    "registry inclusion is approval": "registry_inclusion_approval_claim_detected",
    "evidence consumption is approval": "evidence_consumption_approval_claim_detected",
    "runtime approval evidence is execution approval": "runtime_approval_execution_approval_claim_detected",
    "registry drift detection is approval": "registry_drift_approval_claim_detected",
    "operational readiness is approval": "operational_readiness_approval_claim_detected",
    "release proof linkage is release approval": "release_proof_release_approval_claim_detected",
    "ready_for_review is approval": "ready_for_review_approval_claim_detected",
    "evidence_complete is sealed": "evidence_complete_sealed_claim_detected",
    "replay_ready is sealed": "replay_ready_sealed_claim_detected",
    "onboarding_complete is approved": "onboarding_complete_approved_claim_detected",
    "onboarding documentation closes audits": "onboarding_documentation_audit_closure_claim_detected",
    "onboarding documentation grants waivers": "onboarding_documentation_waiver_grant_claim_detected",
    "onboarding documentation makes final governance judgments": "onboarding_documentation_final_judgment_claim_detected",
}

TRACKER_176_CLOSURE_PHRASES = {
    "closes #176",
    "close #176",
    "closed #176",
    "fixes #176",
    "fixed #176",
    "resolves #176",
    "resolved #176",
}

SAFE_CONTEXT_KEYS = {
    "allowed_evaluator_outputs",
    "forbidden_evaluator_outputs",
    "prohibited_claims",
    "authority_boundary",
    "must_not",
}

FORBIDDEN_AUTHORITY_KEYS = FORBIDDEN_EVALUATOR_OUTPUTS | {
    "authority_granting",
    "approved",
    "approval_granted",
    "execute_fail_closed",
    "execute_rollback",
    "released",
    "documentation_output",
    "evaluator_output",
}

EXPECTED_DOCUMENTATION_PATH = "docs/public-integration-pack/m13-external-consumer-onboarding.md"



def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}



def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []



def _as_set(value: Any) -> set[str]:
    return {str(item).strip() for item in _as_list(value) if str(item).strip()}



def _text(value: Any) -> str:
    return str(value).strip().lower()



def _has_value(record: dict[str, Any], field: str) -> bool:
    value = record.get(field)
    if isinstance(value, bool):
        return True
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return value is not None



def _iter_claim_text(value: Any, parent_key: str | None = None) -> list[str]:
    if parent_key in SAFE_CONTEXT_KEYS:
        return []

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

    return [_text(value)]



def detect_onboarding_forbidden_claims(value: Any, parent_key: str | None = None) -> set[str]:
    claims = set(
        scan_forbidden_authority_claims(
            value,
            forbidden_keys=FORBIDDEN_AUTHORITY_KEYS,
            forbidden_tokens=FORBIDDEN_EVALUATOR_OUTPUTS,
            skip_keys=SAFE_CONTEXT_KEYS,
        )
    )
    for normalized in _iter_claim_text(value, parent_key):
        if normalized in FORBIDDEN_EVALUATOR_OUTPUTS:
            claims.add(normalized)
        for phrase in BOUNDARY_CLAIM_FINDINGS:
            if phrase in normalized:
                claims.add(phrase)
    return claims



def evaluate_m13_external_consumer_onboarding(
    fixture: dict[str, Any], documentation_text: str | None = None
) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    boundary_violation = False
    not_ready = False

    def add_missing(finding: str, evidence: str) -> None:
        findings.append(finding)
        missing_evidence.append(evidence)

    if not fixture:
        add_missing("onboarding_fixture_missing", "fixture")

    for field, finding in REQUIRED_FIXTURE_FIELDS.items():
        if not _has_value(fixture, field):
            add_missing(finding, field)

    if fixture.get("documentation_path") != EXPECTED_DOCUMENTATION_PATH:
        add_missing("unexpected_documentation_path", "documentation_path")
    if fixture.get("artifact_status") != "active_work_in_progress_not_released":
        add_missing("artifact_status_not_active_work_in_progress", "artifact_status")
    if fixture.get("m13_completion_status") != "active_work_not_complete":
        add_missing("m13_completion_status_not_active_work", "m13_completion_status")
    if fixture.get("related_issue") != "#176":
        add_missing("missing_related_issue_176", "related_issue")
    if fixture.get("runtime_approval_gate_evidence_pr") != "#177":
        add_missing("missing_runtime_approval_gate_evidence_pr_177", "runtime_approval_gate_evidence_pr")
    if fixture.get("registry_drift_detection_pr") != "#178":
        add_missing("missing_registry_drift_detection_pr_178", "registry_drift_detection_pr")
    if fixture.get("authority_boundary_regression_fixtures_pr") != "#194":
        add_missing("missing_authority_boundary_regression_fixtures_pr_194", "authority_boundary_regression_fixtures_pr")
    if fixture.get("operational_readiness_checklist_pr") != "#195":
        add_missing("missing_operational_readiness_checklist_pr_195", "operational_readiness_checklist_pr")

    tracker_state = _text(fixture.get("tracker_issue_closure_state"))
    if "open" not in tracker_state or tracker_state == "closed":
        findings.append("tracker_issue_176_not_marked_open")
        missing_evidence.append("tracker_issue_closure_state")
        boundary_violation = True
    if _has_tracker_176_closure_claim(fixture):
        findings.append("tracker_issue_176_closure_claim_detected")
        boundary_violation = True

    if fixture.get("tracker_issue_linkage") != "Refs #176":
        add_missing("tracker_issue_linkage_not_refs_only", "tracker_issue_linkage")

    release_status_future_only = _release_status_future_only(fixture)
    if not release_status_future_only:
        add_missing("release_status_future_only_missing", "release_status_path")
    if _has_v0_12_0_release_claim(fixture):
        findings.append("v0_12_0_release_claim_detected")
        boundary_violation = True
    if _has_m13_completion_claim(fixture):
        findings.append("m13_completion_claim_detected")
        boundary_violation = True

    if fixture.get("onboarding_status") != "ready_for_review_not_approved":
        add_missing("onboarding_status_not_ready_for_review_not_approved", "onboarding_status")
        not_ready = True

    role = _as_dict(fixture.get("external_consumer_role"))
    if role.get("authority_granting") is True:
        findings.append("onboarding_documentation_authority_grant_claim_detected")
        boundary_violation = True

    if not REQUIRED_DOCUMENTATION_SECTIONS <= _as_set(fixture.get("documentation_sections")):
        add_missing("documentation_section_coverage_incomplete", "documentation_sections")
        not_ready = True

    checklist_ids = {
        str(item.get("check_id"))
        for item in _as_list(fixture.get("onboarding_checklist"))
        if isinstance(item, dict)
    }
    if not REQUIRED_ONBOARDING_CHECKS <= checklist_ids:
        add_missing("onboarding_checklist_coverage_incomplete", "onboarding_checklist")
        not_ready = True
    for item in _as_list(fixture.get("onboarding_checklist")):
        if not isinstance(item, dict):
            continue
        if item.get("approved") is True:
            findings.append("onboarding_checklist_approval_claim_detected")
            boundary_violation = True
        if item.get("ready_for_review") is not True:
            add_missing("onboarding_check_not_ready_for_review", str(item.get("check_id")))
            not_ready = True

    if not REQUIRED_EVIDENCE_FIELDS <= _as_set(fixture.get("required_evidence_fields")):
        add_missing("required_evidence_fields_incomplete", "required_evidence_fields")
        not_ready = True

    fixture_boundary_statements = {
        statement.lower() for statement in _as_set(fixture.get("required_boundary_statements"))
    }
    if not REQUIRED_BOUNDARY_STATEMENTS <= fixture_boundary_statements:
        add_missing("required_boundary_statements_incomplete", "required_boundary_statements")
        not_ready = True

    if documentation_text is not None:
        normalized_doc = documentation_text.lower()
        missing_doc_statements = [
            statement
            for statement in REQUIRED_BOUNDARY_STATEMENTS
            if statement not in normalized_doc
        ]
        if missing_doc_statements:
            add_missing("documentation_required_boundary_statement_missing", "documentation_text")
            not_ready = True

    if not REQUIRED_ALLOWED_OUTPUTS <= _as_set(fixture.get("allowed_evaluator_outputs")):
        add_missing("allowed_evaluator_outputs_missing", "allowed_evaluator_outputs")
    if not FORBIDDEN_EVALUATOR_OUTPUTS <= _as_set(fixture.get("forbidden_evaluator_outputs")):
        add_missing("forbidden_evaluator_outputs_missing", "forbidden_evaluator_outputs")

    if not _authority_boundary_complete(fixture):
        add_missing("authority_boundary_statement_incomplete", "authority_boundary")

    if not _required_boundary_language_present(_boundary_language(fixture)):
        add_missing("missing_aaos_authority_boundary_statement", "aaos_retained_authority_statement")

    for claim_text in _iter_claim_text(fixture):
        for phrase, finding in BOUNDARY_CLAIM_FINDINGS.items():
            if phrase in claim_text:
                findings.append(finding)
                boundary_violation = True

    forbidden_claims = detect_onboarding_forbidden_claims(fixture)
    if forbidden_claims:
        findings.append("authority_transfer_claim_detected")
        boundary_violation = True

    handoff = _as_dict(fixture.get("reviewer_handoff"))
    if handoff.get("approval_granted") is True:
        findings.append("reviewer_handoff_approval_claim_detected")
        boundary_violation = True
    if handoff.get("required") is not True:
        add_missing("reviewer_handoff_missing", "reviewer_handoff")
        not_ready = True

    handling = _as_dict(fixture.get("fail_closed_and_escalation_handling"))
    if handling.get("execute_fail_closed") is True:
        findings.append("fail_closed_execution_claim_detected")
        boundary_violation = True
    if handling.get("execute_rollback") is True:
        findings.append("rollback_execution_claim_detected")
        boundary_violation = True

    return _onboarding_result(
        findings=findings,
        missing_evidence=missing_evidence,
        boundary_violation=boundary_violation,
        release_status_future_only=release_status_future_only,
        not_ready=not_ready,
    )



def _release_status_future_only(fixture: dict[str, Any]) -> bool:
    release_status = _as_dict(fixture.get("release_status_path"))
    future_tag = _as_dict(fixture.get("future_release_tag_path"))
    return (
        fixture.get("target_future_release") == "v0.12.0"
        and release_status.get("state") == "future_target_release_only"
        and release_status.get("release_approval") is False
        and future_tag.get("target_tag") == "v0.12.0"
        and future_tag.get("state") == "future_tag_path_only"
        and future_tag.get("released") is False
        and not _has_v0_12_0_release_claim(fixture)
    )



def _authority_boundary_complete(fixture: dict[str, Any]) -> bool:
    boundary = _as_dict(fixture.get("authority_boundary"))
    return (
        REQUIRED_AUTHORITY_MAY <= _as_set(boundary.get("may"))
        and REQUIRED_AUTHORITY_MUST_NOT <= _as_set(boundary.get("must_not"))
    )



def _boundary_language(fixture: dict[str, Any]) -> str:
    segments = [
        str(fixture.get("governance_boundary_statement", "")),
        str(fixture.get("decision_proof_sealing_boundary_statement", "")),
        str(fixture.get("aaos_retained_authority_statement", "")),
        str(fixture.get("sovereignty_statement", "")),
    ]
    segments.extend(str(value) for value in _as_dict(fixture.get("semantic_boundaries")).values())
    return " ".join(segments).lower()



def _required_boundary_language_present(boundary_language: str) -> bool:
    return all(
        phrase in boundary_language
        for phrase in [
            "external consumer onboarding documentation is guidance and evidence structure only",
            "must not approve consumers",
            "registry inclusion is not approval",
            "evidence consumption is not approval",
            "runtime approval evidence is not execution approval",
            "operational readiness is not approval",
            "release proof linkage is not release approval",
            "onboarding_complete is not approved",
            "evidence_complete is not sealed",
            "replay_ready is not sealed",
            "decision proof sealing remains aaos-owned",
            "aaos retains",
            "aaos remains the decision sovereignty layer",
        ]
    )



def _has_tracker_176_closure_claim(fixture: dict[str, Any]) -> bool:
    for item in _iter_claim_text(fixture):
        if item == "closes_176" or any(phrase in item for phrase in TRACKER_176_CLOSURE_PHRASES):
            return True
    return False



def _has_v0_12_0_release_claim(fixture: dict[str, Any]) -> bool:
    if _as_dict(fixture.get("future_release_tag_path")).get("released") is True:
        return True
    for item in _iter_claim_text(fixture):
        if item == "v0_12_0_released" or "v0.12.0 is released" in item:
            return True
    return False



def _has_m13_completion_claim(fixture: dict[str, Any]) -> bool:
    for item in _iter_claim_text(fixture):
        if item == "m13_complete":
            return True
        if "m13 is complete" in item and "not complete" not in item:
            return True
    return False



def _onboarding_result(
    findings: list[str],
    missing_evidence: list[str],
    boundary_violation: bool,
    release_status_future_only: bool,
    not_ready: bool,
) -> dict[str, Any]:
    unique_findings = sorted(set(findings))
    unique_missing = sorted(set(missing_evidence))
    failed = bool(unique_findings or unique_missing or boundary_violation)
    ready_for_review = not failed and not not_ready

    return {
        "onboarding_documentation_valid": not failed,
        "onboarding_documentation_invalid": failed,
        "onboarding_boundary_preserved": not boundary_violation and not failed,
        "onboarding_boundary_violation": boundary_violation,
        "onboarding_ready_for_review": ready_for_review,
        "onboarding_not_ready": not_ready or failed,
        "release_status_future_only": release_status_future_only,
        "onboarding_findings": unique_findings,
        "missing_evidence": unique_missing,
        "review_required": failed or not_ready,
        "escalation_required": boundary_violation,
        "fail_closed_recommended": boundary_violation,
    }
