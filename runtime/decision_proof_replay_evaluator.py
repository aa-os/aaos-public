"""Deterministic checks for AAOS Decision Proof runtime replay evidence."""

from __future__ import annotations

from typing import Any


REQUIRED_REPLAY_FIELDS = {
    "decision_id": "missing_decision_id",
    "intent": "missing_intent",
    "actor": "missing_actor",
    "authority_source": "missing_authority_source",
    "risk_class": "missing_risk_class",
    "allowed_tools": "missing_allowed_tools",
    "approval_required": "missing_approval_required",
    "approval_state": "missing_approval_state",
    "adapter_events": "missing_adapter_events",
    "runtime_events": "missing_runtime_events",
    "execution_trace": "missing_execution_trace",
    "evidence_refs": "missing_evidence_refs",
    "evaluator_outputs": "missing_evaluator_outputs",
    "rollback_plan": "missing_rollback_plan",
    "rollback_surface": "missing_rollback_surface",
    "replay_target": "missing_replay_target",
    "replay_steps": "missing_replay_steps",
    "replay_result": "missing_replay_result",
    "sealing_status": "missing_sealing_status",
    "not_authority_statement": "missing_not_authority_statement",
    "sovereignty_statement": "missing_sovereignty_statement",
}

FORBIDDEN_AUTHORITY_CLAIMS = {
    "governance_authority",
    "policy_authority",
    "identity_authority",
    "approval_authority",
    "release_authority",
    "decision_router_authority",
    "rollback_authority",
    "fail_closed_authority",
    "final_risk_classification_authority",
    "decision_proof_sealing_authority",
    "audit_closure_authority",
    "final_governance_authority",
}

FORBIDDEN_EVALUATOR_OUTPUTS = {
    "release_approved",
    "release_rejected_by_evaluator",
    "risk_accepted",
    "waiver_granted",
    "approval_doctrine_changed",
    "identity_trust_changed",
    "policy_authority_changed",
    "decision_route_changed",
    "rollback_decision",
    "rollback_executed",
    "fail_closed_executed",
    "decision_proof_sealed",
    "audit_closed",
    "final_governance_judgment",
}

SAFE_NEGATIVE_CONTEXT_KEYS = {
    "aaos_retained_authority",
    "allowed_outputs",
    "allowed_tools",
    "allowed_evaluator_outputs",
    "forbidden_outputs",
    "forbidden_authority_claims",
    "forbidden_evaluator_outputs",
    "governance_boundary_preservation",
    "not_authority_statement",
    "sovereignty_statement",
}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


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


def _has_value(record: dict[str, Any], field: str) -> bool:
    if field not in record:
        return False

    value = record[field]
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)

    return value is not None


def detect_forbidden_authority_claims(value: Any, parent_key: str | None = None) -> set[str]:
    """Detect explicit claims to AAOS-retained runtime replay authority."""

    if parent_key in SAFE_NEGATIVE_CONTEXT_KEYS:
        return set()

    claims: set[str] = set()

    if isinstance(value, dict):
        for key, nested in value.items():
            normalized_key = str(key).lower()
            if normalized_key in FORBIDDEN_AUTHORITY_CLAIMS and _is_enabled(nested):
                claims.add(normalized_key)
            if normalized_key in FORBIDDEN_EVALUATOR_OUTPUTS and _is_enabled(nested):
                claims.add(normalized_key)
            claims.update(detect_forbidden_authority_claims(nested, normalized_key))

    elif isinstance(value, list):
        for nested in value:
            if isinstance(nested, str):
                normalized = nested.lower()
                if normalized in FORBIDDEN_AUTHORITY_CLAIMS:
                    claims.add(normalized)
                if normalized in FORBIDDEN_EVALUATOR_OUTPUTS:
                    claims.add(normalized)
            else:
                claims.update(detect_forbidden_authority_claims(nested, parent_key))

    elif isinstance(value, str):
        normalized = value.lower()
        if normalized in FORBIDDEN_AUTHORITY_CLAIMS:
            claims.add(normalized)
        if normalized in FORBIDDEN_EVALUATOR_OUTPUTS:
            claims.add(normalized)

    return claims


def evaluate_replay_packet(packet: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []

    for field, finding in REQUIRED_REPLAY_FIELDS.items():
        if not _has_value(packet, field):
            findings.append(finding)
            missing_evidence.append(field)

    if packet.get("approval_required") is True and not _has_value(packet, "approval_state"):
        findings.append("missing_approval_state_when_approval_is_required")
        missing_evidence.append("approval_state")

    if packet.get("approval_required") is True and str(packet.get("approval_state", "")).lower() in {
        "missing",
        "none",
        "not_present",
    }:
        findings.append("missing_approval_state_when_approval_is_required")
        missing_evidence.append("approval_state")

    if not _as_dict(packet.get("execution_trace")).get("replay_ready", False):
        findings.append("missing_execution_trace")
        missing_evidence.append("execution_trace")

    if not _as_dict(packet.get("rollback_surface")).get("complete", False):
        findings.append("missing_rollback_surface")
        missing_evidence.append("rollback_surface")

    if not _as_dict(packet.get("replay_result")).get("replay_completed", False):
        findings.append("missing_replay_result")
        missing_evidence.append("replay_result")

    forbidden_claims = detect_forbidden_authority_claims(packet)
    authority_findings = _authority_findings(forbidden_claims)
    findings.extend(authority_findings)

    return _result(findings, missing_evidence, bool(authority_findings))


def evaluate_release_proof(proof: dict[str, Any]) -> dict[str, Any]:
    readme = _as_dict(proof.get("readme_version_status"))
    release_tag = _as_dict(proof.get("release_tag"))
    title_consistency = _as_dict(proof.get("release_title_consistency"))
    body_consistency = _as_dict(proof.get("release_body_consistency"))
    next_phase = _as_dict(proof.get("next_phase_declaration"))
    replay_packet = _as_dict(proof.get("decision_proof_replay_packet"))
    boundary = _as_dict(proof.get("governance_boundary_preservation"))
    automation_checks = _as_dict(proof.get("automation_checks"))

    findings: list[str] = []
    missing_evidence: list[str] = []

    if readme.get("present") is not True:
        findings.append("missing_readme_version")
        missing_evidence.append("readme_version_status")

    if not proof.get("tracker_issue"):
        findings.append("missing_release_proof_evidence")
        missing_evidence.append("tracker_issue")

    closing_prs = _as_list(proof.get("closing_prs"))
    if not closing_prs:
        findings.append("missing_release_proof_evidence")
        missing_evidence.append("closing_prs")
    for pr in closing_prs:
        if not isinstance(pr, dict) or pr.get("merged") is not True:
            findings.append("release_proof_consistency_failed")
            missing_evidence.append("closing_prs")

    if release_tag.get("present") is not True:
        findings.append("missing_release_proof_evidence")
        missing_evidence.append("release_tag")

    if title_consistency.get("matches") is not True:
        findings.append("release_title_mismatch")

    if body_consistency.get("governance_boundary_preserved") is not True:
        findings.append("missing_governance_boundary_preservation")
        missing_evidence.append("release_body_consistency")

    if next_phase.get("matches_expected") is not True:
        findings.append("next_phase_mismatch")

    if replay_packet.get("present") is not True or replay_packet.get("replay_ready") is not True:
        findings.append("missing_release_proof_evidence")
        missing_evidence.append("decision_proof_replay_packet")

    if boundary.get("preserved") is not True:
        findings.append("missing_governance_boundary_preservation")
        missing_evidence.append("governance_boundary_preservation")

    for check_name, check_value in automation_checks.items():
        if check_value is not True:
            findings.append("release_proof_consistency_failed")
            missing_evidence.append(f"automation_check:{check_name}")

    forbidden_claims = detect_forbidden_authority_claims(proof)
    authority_findings = _authority_findings(forbidden_claims)
    findings.extend(authority_findings)

    return _result(findings, missing_evidence, bool(authority_findings))


def _authority_findings(forbidden_claims: set[str]) -> list[str]:
    findings: list[str] = []

    if not forbidden_claims:
        return findings

    findings.append("authority_boundary_violation")

    if forbidden_claims & {"decision_proof_sealed", "decision_proof_sealing_authority"}:
        findings.append("decision_proof_sealing_claimed_outside_aaos")

    if forbidden_claims & {"audit_closed", "audit_closure_authority"}:
        findings.append("audit_closure_claimed_outside_aaos")

    if forbidden_claims & {"release_approved", "release_rejected_by_evaluator", "release_authority"}:
        findings.append("release_authority_claimed_outside_aaos")

    if forbidden_claims & {"rollback_decision", "rollback_executed", "rollback_authority"}:
        findings.append("rollback_authority_claimed_outside_aaos")

    if forbidden_claims & {"final_governance_judgment", "final_governance_authority"}:
        findings.append("final_governance_authority_claimed_outside_aaos")

    return findings


def _result(
    findings: list[str],
    missing_evidence: list[str],
    authority_boundary_violation: bool,
) -> dict[str, Any]:
    unique_findings = sorted(set(findings))
    unique_missing = sorted(set(missing_evidence))
    failed = bool(unique_findings or unique_missing)

    return {
        "replay_packet_valid": not failed,
        "replay_packet_invalid": failed,
        "replay_findings": unique_findings,
        "missing_evidence": unique_missing,
        "authority_boundary_violation": authority_boundary_violation,
        "release_proof_consistency_passed": not failed,
        "release_proof_consistency_failed": failed,
        "review_required": failed,
        "escalation_required": authority_boundary_violation,
        "fail_closed_recommended": authority_boundary_violation,
    }
