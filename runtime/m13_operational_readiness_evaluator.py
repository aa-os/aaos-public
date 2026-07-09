"""Deterministic checks for M13 operational readiness evidence."""

from __future__ import annotations

from typing import Any


REQUIRED_CHECKLIST_FIELDS = {
    "checklist_id": "missing_checklist_id",
    "checklist_name": "missing_checklist_name",
    "checklist_scope": "missing_checklist_scope",
    "artifact_status": "missing_artifact_status",
    "m13_completion_status": "missing_m13_completion_status",
    "related_issue": "missing_related_issue_176",
    "tracker_issue_closure_state": "missing_tracker_issue_176_open_state",
    "tracker_issue_linkage": "missing_tracker_issue_176_reference",
    "runtime_approval_gate_evidence_pr": "missing_runtime_approval_gate_evidence_pr_177",
    "registry_drift_detection_pr": "missing_registry_drift_detection_pr_178",
    "authority_boundary_regression_fixtures_pr": "missing_authority_boundary_regression_fixtures_pr_194",
    "introduced_after_release": "missing_introduced_after_release_v0_11_0",
    "target_future_release": "missing_target_future_release_v0_12_0",
    "future_release_tag_path": "missing_future_release_tag_path",
    "release_status_path": "missing_release_status_path",
    "m13_reference_artifacts": "missing_m13_reference_artifacts",
    "readiness_outcome": "missing_readiness_outcome",
    "readiness_domains": "missing_readiness_domains",
    "semantic_boundaries": "missing_semantic_boundaries",
    "allowed_evaluator_outputs": "missing_allowed_evaluator_outputs",
    "forbidden_evaluator_outputs": "missing_forbidden_evaluator_outputs",
    "authority_boundary": "missing_authority_boundary",
    "governance_boundary_statement": "missing_governance_boundary_statement",
    "decision_proof_sealing_boundary_statement": "missing_decision_proof_sealing_boundary_statement",
    "aaos_retained_authority_statement": "missing_aaos_retained_authority_statement",
    "sovereignty_statement": "missing_sovereignty_statement",
}

REQUIRED_M13_REFS = {
    "runtime_enforced_approval_gate_evidence",
    "registry_drift_detection_specimen",
    "authority_boundary_regression_fixtures",
    "runtime_approval_gate_evaluator",
    "registry_drift_evaluator",
    "authority_boundary_regression_evaluator",
}

REQUIRED_READINESS_DOMAINS = {
    "m13_tracker_issue_176_remains_open",
    "runtime_enforced_approval_evidence_from_177_present",
    "registry_drift_detection_from_178_present",
    "authority_boundary_regression_fixtures_from_194_present",
    "external_consumer_registry_entry_stable",
    "registry_drift_checks_available",
    "runtime_approval_evidence_enforced_or_explicitly_not_ready",
    "onboarding_documentation_required_not_authority_granting",
    "release_proof_linkage_future_only_for_v0_12_0",
    "v0_12_0_not_released",
    "m13_not_complete",
    "decision_proof_sealing_remains_aaos_owned",
    "aaos_remains_decision_sovereignty_layer",
}

REQUIRED_ALLOWED_OUTPUTS = {
    "operational_readiness_checklist_valid",
    "operational_readiness_checklist_invalid",
    "readiness_domain_coverage_complete",
    "readiness_domain_coverage_incomplete",
    "ready_for_review",
    "not_ready",
    "review_required",
    "escalation_required",
    "fail_closed_recommended",
}

FORBIDDEN_EVALUATOR_OUTPUTS = {
    "consumer_approved",
    "registry_entry_approved",
    "release_approved",
    "execution_approved_by_evaluator",
    "risk_accepted",
    "decision_proof_sealed",
    "sealed_by_registry",
    "sealed_by_consumer",
    "sealed_by_ci",
    "sealed_by_evaluator",
    "rollback_executed",
    "fail_closed_executed",
    "audit_closed",
    "waiver_granted",
    "final_governance_judgment",
    "authority_transferred",
    "v0_12_0_released",
    "m13_complete",
    "closes_176",
}

REQUIRED_AUTHORITY_MAY = {
    "report_readiness_gaps",
    "surface_review_required",
    "surface_escalation_required",
    "surface_fail_closed_recommended",
    "reference_evidence",
    "inspect_evidence",
    "check_evidence",
    "link_evidence",
}

REQUIRED_AUTHORITY_MUST_NOT = {
    "approve_consumers",
    "approve_releases",
    "approve_execution",
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
    "onboarding documentation grants authority": "onboarding_documentation_authority_grant_claim_detected",
    "release proof linkage is release approval": "release_proof_release_approval_claim_detected",
    "ready_for_review is approval": "ready_for_review_approval_claim_detected",
    "not_ready is fail_closed_executed": "not_ready_fail_closed_execution_claim_detected",
    "review_required is audit closure": "review_required_audit_closure_claim_detected",
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
    "authority_boundary",
    "must_not",
}



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



def detect_operational_readiness_forbidden_claims(
    value: Any, parent_key: str | None = None
) -> set[str]:
    claims: set[str] = set()

    if parent_key in SAFE_CONTEXT_KEYS:
        return claims

    if isinstance(value, dict):
        for key, item in value.items():
            claims.update(detect_operational_readiness_forbidden_claims(item, str(key)))
        return claims

    if isinstance(value, list):
        for item in value:
            claims.update(detect_operational_readiness_forbidden_claims(item, parent_key))
        return claims

    normalized = _text(value)
    if normalized in FORBIDDEN_EVALUATOR_OUTPUTS:
        claims.add(normalized)
    for phrase in BOUNDARY_CLAIM_FINDINGS:
        if phrase in normalized:
            claims.add(phrase)
    return claims



def evaluate_m13_operational_readiness_checklist(
    checklist: dict[str, Any]
) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    authority_boundary_violation = False
    not_ready = False

    def add_missing(finding: str, evidence: str) -> None:
        findings.append(finding)
        missing_evidence.append(evidence)

    if not checklist:
        add_missing("operational_readiness_checklist_missing", "checklist")

    for field, finding in REQUIRED_CHECKLIST_FIELDS.items():
        if not _has_value(checklist, field):
            add_missing(finding, field)

    if checklist.get("related_issue") != "#176":
        add_missing("missing_related_issue_176", "related_issue")
    if checklist.get("runtime_approval_gate_evidence_pr") != "#177":
        add_missing("missing_runtime_approval_gate_evidence_pr_177", "runtime_approval_gate_evidence_pr")
    if checklist.get("registry_drift_detection_pr") != "#178":
        add_missing("missing_registry_drift_detection_pr_178", "registry_drift_detection_pr")
    if checklist.get("authority_boundary_regression_fixtures_pr") != "#194":
        add_missing("missing_authority_boundary_regression_fixtures_pr_194", "authority_boundary_regression_fixtures_pr")

    tracker_state = _text(checklist.get("tracker_issue_closure_state"))
    if "open" not in tracker_state or tracker_state == "closed":
        add_missing("tracker_issue_176_not_marked_open", "tracker_issue_closure_state")
        authority_boundary_violation = True
    if _has_tracker_176_closure_claim(checklist):
        findings.append("tracker_issue_176_closure_claim_detected")
        authority_boundary_violation = True

    release_status_future_only = _release_status_future_only(checklist)
    if not release_status_future_only:
        add_missing("release_status_future_only_missing", "release_status_path")
    if _has_v0_12_0_release_claim(checklist):
        findings.append("v0_12_0_release_claim_detected")
        authority_boundary_violation = True
    if _has_m13_completion_claim(checklist):
        findings.append("m13_completion_claim_detected")
        authority_boundary_violation = True

    if not REQUIRED_M13_REFS <= set(_as_dict(checklist.get("m13_reference_artifacts"))):
        add_missing("m13_reference_artifacts_missing", "m13_reference_artifacts")

    domains = _domain_map(checklist)
    readiness_domain_coverage_complete = REQUIRED_READINESS_DOMAINS <= set(domains)
    if not readiness_domain_coverage_complete:
        add_missing("readiness_domain_coverage_incomplete", "readiness_domains")
        not_ready = True

    for domain_id in REQUIRED_READINESS_DOMAINS:
        domain = domains.get(domain_id)
        if domain is None:
            continue
        if domain.get("represented") is not True or not _as_list(domain.get("evidence_refs")):
            add_missing(f"readiness_domain_missing_{domain_id}", f"readiness_domains.{domain_id}")
            not_ready = True
        if domain.get("authority_granting") is True:
            findings.append("readiness_domain_authority_grant_detected")
            authority_boundary_violation = True

    registry_drift = domains.get("registry_drift_detection_from_178_present")
    if not _domain_ready(registry_drift):
        add_missing("registry_drift_detection_evidence_missing", "registry_drift_detection_from_178_present")
        not_ready = True

    runtime_approval = domains.get("runtime_enforced_approval_evidence_from_177_present")
    if not _domain_ready(runtime_approval):
        add_missing("runtime_approval_evidence_missing", "runtime_enforced_approval_evidence_from_177_present")
        not_ready = True

    runtime_enforcement = domains.get("runtime_approval_evidence_enforced_or_explicitly_not_ready")
    if not _runtime_approval_enforced_or_not_ready(runtime_enforcement):
        add_missing(
            "runtime_approval_evidence_not_enforced_or_marked_not_ready",
            "runtime_approval_evidence_enforced_or_explicitly_not_ready",
        )
        not_ready = True
    if _as_dict(runtime_enforcement).get("explicit_not_ready") is True:
        not_ready = True

    onboarding = domains.get("onboarding_documentation_required_not_authority_granting")
    if _as_dict(onboarding).get("authority_granting") is True:
        findings.append("onboarding_documentation_authority_grant_claim_detected")
        authority_boundary_violation = True

    release_linkage = domains.get("release_proof_linkage_future_only_for_v0_12_0")
    if _as_dict(release_linkage).get("release_approval") is True:
        findings.append("release_proof_release_approval_claim_detected")
        authority_boundary_violation = True

    readiness_outcome = _as_dict(checklist.get("readiness_outcome"))
    if readiness_outcome.get("state") != "ready_for_review":
        not_ready = True
    for forbidden_state in ["approval", "release_approval", "decision_proof_sealing", "audit_closure", "tracker_closure"]:
        if readiness_outcome.get(forbidden_state) is True:
            findings.append(f"readiness_outcome_{forbidden_state}_claim_detected")
            authority_boundary_violation = True

    if not REQUIRED_ALLOWED_OUTPUTS <= _as_set(checklist.get("allowed_evaluator_outputs")):
        add_missing("allowed_evaluator_outputs_missing", "allowed_evaluator_outputs")
    if not FORBIDDEN_EVALUATOR_OUTPUTS <= _as_set(checklist.get("forbidden_evaluator_outputs")):
        add_missing("forbidden_evaluator_outputs_missing", "forbidden_evaluator_outputs")

    if not _authority_boundary_complete(checklist):
        add_missing("authority_boundary_statement_incomplete", "authority_boundary")

    boundary_language = _boundary_language(checklist)
    if not _required_boundary_language_present(boundary_language):
        add_missing("missing_aaos_authority_boundary_statement", "aaos_retained_authority_statement")
    for phrase, finding in BOUNDARY_CLAIM_FINDINGS.items():
        if phrase in boundary_language:
            findings.append(finding)
            authority_boundary_violation = True

    forbidden_claims = detect_operational_readiness_forbidden_claims(checklist)
    if forbidden_claims:
        findings.append("authority_transfer_claim_detected")
        authority_boundary_violation = True

    return _operational_readiness_result(
        findings=findings,
        missing_evidence=missing_evidence,
        authority_boundary_violation=authority_boundary_violation,
        readiness_domain_coverage_complete=readiness_domain_coverage_complete,
        release_status_future_only=release_status_future_only,
        not_ready=not_ready,
    )



def _domain_map(checklist: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(domain.get("domain_id")): domain
        for domain in _as_list(checklist.get("readiness_domains"))
        if isinstance(domain, dict)
    }



def _domain_ready(domain: dict[str, Any] | None) -> bool:
    if not isinstance(domain, dict):
        return False
    return (
        domain.get("represented") is True
        and domain.get("ready_for_review") is True
        and bool(_as_list(domain.get("evidence_refs")))
        and domain.get("authority_granting") is not True
    )



def _runtime_approval_enforced_or_not_ready(domain: dict[str, Any] | None) -> bool:
    if not isinstance(domain, dict):
        return False
    if not _as_list(domain.get("evidence_refs")) or domain.get("represented") is not True:
        return False
    return domain.get("runtime_approval_state") == "enforced" or domain.get("explicit_not_ready") is True



def _release_status_future_only(checklist: dict[str, Any]) -> bool:
    release_status = _as_dict(checklist.get("release_status_path"))
    future_tag = _as_dict(checklist.get("future_release_tag_path"))
    return (
        checklist.get("target_future_release") == "v0.12.0"
        and release_status.get("state") == "future_target_release_only"
        and release_status.get("release_approval") is False
        and future_tag.get("target_tag") == "v0.12.0"
        and future_tag.get("state") == "future_tag_path_only"
        and future_tag.get("released") is False
        and not _has_v0_12_0_release_claim(checklist)
    )



def _authority_boundary_complete(checklist: dict[str, Any]) -> bool:
    boundary = _as_dict(checklist.get("authority_boundary"))
    return (
        REQUIRED_AUTHORITY_MAY <= _as_set(boundary.get("may"))
        and REQUIRED_AUTHORITY_MUST_NOT <= _as_set(boundary.get("must_not"))
    )



def _boundary_language(checklist: dict[str, Any]) -> str:
    segments = [
        str(checklist.get("governance_boundary_statement", "")),
        str(checklist.get("decision_proof_sealing_boundary_statement", "")),
        str(checklist.get("aaos_retained_authority_statement", "")),
        str(checklist.get("sovereignty_statement", "")),
    ]
    segments.extend(str(value) for value in _as_dict(checklist.get("semantic_boundaries")).values())
    return " ".join(segments).lower()



def _required_boundary_language_present(boundary_language: str) -> bool:
    return all(
        phrase in boundary_language
        for phrase in [
            "operational readiness checks are evidence checks only",
            "must not approve consumers",
            "ready_for_review is not approval",
            "not_ready is not fail_closed_executed",
            "review_required is not audit closure",
            "release proof linkage is not release approval",
            "onboarding documentation does not grant authority",
            "decision proof sealing remains aaos-owned",
            "aaos retains",
            "aaos remains the decision sovereignty layer",
        ]
    )



def _has_tracker_176_closure_claim(checklist: dict[str, Any]) -> bool:
    for item in _iter_claim_text(checklist):
        if item == "closes_176" or any(phrase in item for phrase in TRACKER_176_CLOSURE_PHRASES):
            return True
    return False



def _has_v0_12_0_release_claim(checklist: dict[str, Any]) -> bool:
    if _as_dict(checklist.get("future_release_tag_path")).get("released") is True:
        return True
    for item in _iter_claim_text(checklist):
        if item == "v0_12_0_released" or "v0.12.0 is released" in item:
            return True
    return False



def _has_m13_completion_claim(checklist: dict[str, Any]) -> bool:
    for item in _iter_claim_text(checklist):
        if item == "m13_complete":
            return True
        if "m13 is complete" in item and "not complete" not in item:
            return True
    return False



def _operational_readiness_result(
    findings: list[str],
    missing_evidence: list[str],
    authority_boundary_violation: bool,
    readiness_domain_coverage_complete: bool,
    release_status_future_only: bool,
    not_ready: bool,
) -> dict[str, Any]:
    unique_findings = sorted(set(findings))
    unique_missing = sorted(set(missing_evidence))
    failed = bool(unique_findings or unique_missing or authority_boundary_violation)
    ready_for_review = not failed and not not_ready

    return {
        "operational_readiness_checklist_valid": not failed,
        "operational_readiness_checklist_invalid": failed,
        "readiness_domain_coverage_complete": readiness_domain_coverage_complete,
        "readiness_domain_coverage_incomplete": not readiness_domain_coverage_complete,
        "ready_for_review": ready_for_review,
        "not_ready": not_ready or failed,
        "release_status_future_only": release_status_future_only,
        "operational_readiness_findings": unique_findings,
        "missing_evidence": unique_missing,
        "review_required": failed or not_ready,
        "escalation_required": authority_boundary_violation,
        "fail_closed_recommended": authority_boundary_violation,
    }
