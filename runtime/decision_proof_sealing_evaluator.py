"""Deterministic checks for AAOS Decision Proof sealing boundary evidence."""

from __future__ import annotations

from typing import Any


ALLOWED_SEALING_STATES = {
    "unsealed",
    "replay_ready",
    "evidence_complete",
    "human_review_required",
    "advisor_review_required",
    "sealing_eligible",
    "sealed_by_aaos",
    "sealing_rejected_by_aaos",
    "sealing_deferred",
    "sealing_blocked",
}

FORBIDDEN_SEALING_STATES = {
    "sealed_by_adapter",
    "sealed_by_ci",
    "sealed_by_evaluator",
    "sealed_by_runtime_replay",
    "sealed_by_release_automation",
    "sealed_by_registry",
    "sealed_by_external_system",
    "audit_closed_by_adapter",
    "final_governance_judgment_by_external_system",
}

FORBIDDEN_EVALUATOR_OUTPUTS = {
    "decision_proof_sealed",
    "sealed_by_evaluator",
    "sealed_by_ci",
    "sealed_by_adapter",
    "sealed_by_runtime_replay",
    "sealed_by_release_automation",
    "sealed_by_registry",
    "sealed_by_external_system",
    "release_approved",
    "risk_accepted",
    "waiver_granted",
    "approval_doctrine_changed",
    "identity_trust_changed",
    "policy_authority_changed",
    "decision_route_changed",
    "rollback_decision",
    "rollback_executed",
    "fail_closed_executed",
    "audit_closed",
    "final_governance_judgment",
}

REQUIRED_SEALING_FIELDS = {
    "sealing_boundary_statement": "missing_sealing_boundary_statement",
    "sealing_status": "missing_sealing_status",
    "evidence_readiness_state": "missing_evidence_readiness_state",
    "sealing_eligibility_state": "missing_sealing_eligibility_state",
    "final_sealing_authority_owner": "missing_final_sealing_authority_owner",
    "aaos_retained_authority_statement": "missing_aaos_retained_authority_statement",
}

REQUIRED_INTEGRATION_FIELDS = {
    "identity_boundary": "missing_external_integration_identity_boundary",
    "authority_boundary": "missing_external_integration_authority_boundary",
    "evidence_schema_compatibility": "missing_evidence_schema_compatibility",
    "replay_compatibility": "missing_replay_compatibility",
    "rollback_traceability": "missing_rollback_traceability",
    "escalation_semantics": "missing_escalation_semantics",
    "fail_closed_behavior": "missing_fail_closed_behavior",
    "decision_proof_sealing_boundary_preservation": "missing_decision_proof_sealing_boundary_preservation",
    "release_proof_linkage": "missing_release_proof_linkage",
}

REQUIRED_TRACEABILITY_FIELDS = {
    "adapter_contract",
    "adapter_evidence_schema",
    "adapter_example",
    "evaluator_output",
    "runtime_replay_packet",
    "release_proof_automation_packet",
    "readme_release_status",
    "tracker_issue",
    "closing_pr",
    "release_tag",
    "release_title",
    "release_body",
    "sealing_status",
    "aaos_retained_authority_statement",
}

SAFE_NEGATIVE_CONTEXT_KEYS = {
    "allowed_outputs",
    "allowed_evaluator_outputs",
    "allowed_integration_outputs",
    "forbidden_outputs",
    "forbidden_evaluator_outputs",
    "forbidden_integration_outputs",
    "forbidden_sealing_states",
    "not_authority_statement",
    "sovereignty_statement",
    "aaos_retained_authority_statement",
    "not_delegated_to",
}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _has_value(record: dict[str, Any], field: str) -> bool:
    if field not in record:
        return False

    value = record[field]
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)

    return value is not None


def _is_enabled(value: Any) -> bool:
    return value is True or str(value).lower() in {
        "true",
        "allowed",
        "enabled",
        "yes",
        "claimed",
        "approved",
        "sealed",
        "closed",
        "executed",
    }


def detect_forbidden_sealing_claims(value: Any, parent_key: str | None = None) -> set[str]:
    """Detect sealing or final-authority claims outside AAOS-owned boundaries."""

    if parent_key in SAFE_NEGATIVE_CONTEXT_KEYS:
        return set()

    claims: set[str] = set()

    if isinstance(value, dict):
        for key, nested in value.items():
            normalized_key = str(key).lower()
            if normalized_key in FORBIDDEN_SEALING_STATES and _is_enabled(nested):
                claims.add(normalized_key)
            if normalized_key in FORBIDDEN_EVALUATOR_OUTPUTS and _is_enabled(nested):
                claims.add(normalized_key)
            claims.update(detect_forbidden_sealing_claims(nested, normalized_key))

    elif isinstance(value, list):
        for nested in value:
            if isinstance(nested, str):
                normalized = nested.lower()
                if normalized in FORBIDDEN_SEALING_STATES:
                    claims.add(normalized)
                if normalized in FORBIDDEN_EVALUATOR_OUTPUTS:
                    claims.add(normalized)
            else:
                claims.update(detect_forbidden_sealing_claims(nested, parent_key))

    elif isinstance(value, str):
        normalized = value.lower()
        if normalized in FORBIDDEN_SEALING_STATES:
            claims.add(normalized)
        if normalized in FORBIDDEN_EVALUATOR_OUTPUTS:
            claims.add(normalized)

    return claims


def evaluate_sealing_status(record: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []

    for field, finding in REQUIRED_SEALING_FIELDS.items():
        if not _has_value(record, field):
            findings.append(finding)
            missing_evidence.append(field)

    sealing_status = str(record.get("sealing_status", "")).lower()
    if sealing_status and sealing_status not in ALLOWED_SEALING_STATES:
        findings.append("forbidden_sealing_state")

    if sealing_status in FORBIDDEN_SEALING_STATES:
        findings.append("decision_proof_sealed_outside_aaos")

    if str(record.get("final_sealing_authority_owner", "")).lower() not in {"", "aaos"}:
        findings.append("decision_proof_sealed_outside_aaos")

    claims = detect_forbidden_sealing_claims(record)
    authority_findings = _authority_findings(claims)
    findings.extend(authority_findings)

    return _result(
        findings,
        missing_evidence,
        bool(authority_findings or "decision_proof_sealed_outside_aaos" in findings),
        mode="sealing",
    )


def evaluate_external_integration_readiness(record: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []

    identity_boundary = _as_dict(record.get("identity_boundary"))
    authority_boundary = _as_dict(record.get("authority_boundary"))

    if identity_boundary.get("defined") is not True:
        findings.append("missing_external_integration_identity_boundary")
        missing_evidence.append("identity_boundary")

    if authority_boundary.get("defined") is not True:
        findings.append("missing_external_integration_authority_boundary")
        missing_evidence.append("authority_boundary")

    for field, finding in REQUIRED_INTEGRATION_FIELDS.items():
        if field in {"identity_boundary", "authority_boundary"}:
            continue
        if record.get(field) is not True:
            findings.append(finding)
            missing_evidence.append(field)

    claims = detect_forbidden_sealing_claims(record)
    authority_findings = _authority_findings(claims)
    findings.extend(authority_findings)

    return _result(findings, missing_evidence, bool(authority_findings), mode="integration")


def evaluate_adapter_release_traceability(record: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []

    for field in sorted(REQUIRED_TRACEABILITY_FIELDS):
        if not _has_value(record, field):
            findings.append("missing_adapter_to_release_proof_traceability")
            missing_evidence.append(field)

    if record.get("adapter_to_release_proof_traceability") is not True:
        findings.append("missing_adapter_to_release_proof_traceability")
        missing_evidence.append("adapter_to_release_proof_traceability")

    if record.get("release_proof_linkage") is not True:
        findings.append("missing_release_proof_linkage")
        missing_evidence.append("release_proof_linkage")

    if not _has_value(record, "aaos_retained_authority_statement"):
        findings.append("missing_aaos_retained_authority_statement")
        missing_evidence.append("aaos_retained_authority_statement")

    sealing_status = str(record.get("sealing_status", "")).lower()
    if sealing_status and sealing_status not in ALLOWED_SEALING_STATES:
        findings.append("forbidden_sealing_state")

    claims = detect_forbidden_sealing_claims(record)
    authority_findings = _authority_findings(claims)
    findings.extend(authority_findings)

    return _result(findings, missing_evidence, bool(authority_findings), mode="traceability")


def _authority_findings(claims: set[str]) -> list[str]:
    findings: list[str] = []

    if not claims:
        return findings

    findings.append("authority_boundary_violation")

    if claims & {
        "decision_proof_sealed",
        "sealed_by_adapter",
        "sealed_by_ci",
        "sealed_by_evaluator",
        "sealed_by_runtime_replay",
        "sealed_by_release_automation",
        "sealed_by_registry",
        "sealed_by_external_system",
    }:
        findings.append("decision_proof_sealed_outside_aaos")

    if claims & {"audit_closed", "audit_closed_by_adapter"}:
        findings.append("audit_closed_outside_aaos")

    if claims & {"final_governance_judgment", "final_governance_judgment_by_external_system"}:
        findings.append("final_governance_judgment_made_outside_aaos")

    return findings


def _result(
    findings: list[str],
    missing_evidence: list[str],
    authority_boundary_violation: bool,
    mode: str,
) -> dict[str, Any]:
    unique_findings = sorted(set(findings))
    unique_missing = sorted(set(missing_evidence))
    failed = bool(unique_findings or unique_missing)

    return {
        "sealing_boundary_valid": not failed if mode == "sealing" else not authority_boundary_violation,
        "sealing_boundary_invalid": failed if mode == "sealing" else authority_boundary_violation,
        "integration_readiness_passed": not failed if mode == "integration" else not authority_boundary_violation,
        "integration_readiness_failed": failed if mode == "integration" else authority_boundary_violation,
        "traceability_complete": not failed if mode == "traceability" else not authority_boundary_violation,
        "traceability_incomplete": failed if mode == "traceability" else authority_boundary_violation,
        "sealing_findings": unique_findings,
        "missing_evidence": unique_missing,
        "forbidden_sealing_state": "forbidden_sealing_state" in unique_findings,
        "authority_boundary_violation": authority_boundary_violation,
        "review_required": failed,
        "escalation_required": authority_boundary_violation,
        "fail_closed_recommended": authority_boundary_violation,
    }
