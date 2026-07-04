"""Deterministic checks for AAOS release governance and adapter regression evidence."""

from __future__ import annotations

from typing import Any


REQUIRED_ADAPTER_FIELDS = {
    "adapter_id",
    "adapter_name",
    "adapter_type",
    "aaos_layer_mapping",
    "allowed_outputs",
    "forbidden_outputs",
    "evidence_schema_path",
    "contract_path",
    "example_path",
    "evaluator_path",
    "test_path",
    "related_issue",
    "related_pr",
    "release_introduced",
    "authority_boundary_statement",
    "aaos_retained_authority_statement",
}

REQUIRED_SYSTEMS = {
    "cloudflare_security_audit_skill",
    "advisor_invocation_contract",
    "aitbm_l6_scoring_adapter",
    "heretic_adversarial_specimen",
    "skillopt_governed_skill_evolution",
    "codebase_memory_reconstruction_adapter",
    "open_tag_human_agent_workspace_adapter",
}

FORBIDDEN_AUTHORITY_CLAIMS = {
    "final_governance_authority",
    "approval_doctrine",
    "identity_trust_chain",
    "policy_authority",
    "decision_router_authority",
    "rollback_authority",
    "fail_closed_authority",
    "final_risk_classification",
    "decision_proof_sealing_authority",
    "audit_closure_authority",
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
    "fail_closed_executed",
    "decision_proof_sealed",
    "audit_closed",
    "final_governance_judgment",
}

SAFE_NEGATIVE_CONTEXT_KEYS = {
    "allowed_outputs",
    "allowed_evaluator_outputs",
    "forbidden_outputs",
    "forbidden_authority_claims",
    "forbidden_evaluator_outputs",
    "not_authority",
    "not_authority_statement",
    "registry_boundary",
    "sovereignty_checks",
    "sovereignty_statement",
    "authority_boundary_statement",
    "aaos_retained_authority_statement",
}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _is_enabled(value: Any) -> bool:
    return value is True or str(value).lower() in {"true", "allowed", "enabled", "yes", "claimed"}


def _non_empty(value: Any) -> bool:
    return bool(value) and not (isinstance(value, list) and len(value) == 0)


def detect_forbidden_authority_claims(value: Any, parent_key: str | None = None) -> set[str]:
    """Detect explicit claims to AAOS-retained authority."""

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
                if normalized in FORBIDDEN_EVALUATOR_OUTPUTS:
                    claims.add(normalized)
            else:
                claims.update(detect_forbidden_authority_claims(nested, parent_key))

    return claims


def adapter_registry_field_violations(adapter: dict[str, Any]) -> list[str]:
    missing = [
        field
        for field in sorted(REQUIRED_ADAPTER_FIELDS)
        if field not in adapter
    ]
    return [f"missing_adapter_registry_field:{field}" for field in missing]


def evaluate_adapter_registry(registry: dict[str, Any]) -> dict[str, Any]:
    adapters = [
        adapter
        for adapter in _as_list(registry.get("adapters"))
        if isinstance(adapter, dict)
    ]
    findings: list[str] = []
    missing_evidence: list[str] = []

    if not adapters:
        findings.append("adapter_registry_missing_required_fields")
        missing_evidence.append("adapters")

    for adapter in adapters:
        field_violations = adapter_registry_field_violations(adapter)
        if field_violations:
            findings.append("adapter_registry_missing_required_fields")
            missing_evidence.extend(field_violations)

        if not _non_empty(adapter.get("aaos_retained_authority_statement")):
            findings.append("adapter_missing_aaos_retained_authority_statement")

        forbidden_claims = detect_forbidden_authority_claims(adapter)
        if forbidden_claims:
            findings.append("adapter_claims_forbidden_authority")
            if "decision_proof_sealed" in forbidden_claims or "decision_proof_sealing_authority" in forbidden_claims:
                findings.append("decision_proof_sealing_claimed_outside_aaos")
            if "audit_closed" in forbidden_claims or "audit_closure_authority" in forbidden_claims:
                findings.append("audit_closure_claimed_outside_aaos")

    authority_boundary_violation = any(
        finding
        in {
            "adapter_claims_forbidden_authority",
            "decision_proof_sealing_claimed_outside_aaos",
            "audit_closure_claimed_outside_aaos",
        }
        for finding in findings
    )

    return _result(findings, missing_evidence, authority_boundary_violation)


def evaluate_release_governance(record: dict[str, Any]) -> dict[str, Any]:
    readme = _as_dict(record.get("readme_version_status"))
    milestone_wording = _as_dict(record.get("milestone_completion_wording"))
    tracker = _as_dict(record.get("issue_tracker_closure"))
    release_tag = _as_dict(record.get("release_tag"))
    title_consistency = _as_dict(record.get("release_title_consistency"))
    body_consistency = _as_dict(record.get("release_body_consistency"))
    next_phase = _as_dict(record.get("next_phase_declaration"))
    issue_linkage = _as_dict(record.get("related_issue_linkage"))
    boundary = _as_dict(record.get("governance_boundary_preservation"))

    findings: list[str] = []
    missing_evidence: list[str] = []

    if readme.get("present") is not True:
        findings.append("missing_readme_version")
        missing_evidence.append("readme_version_status")

    if milestone_wording.get("matches") is not True:
        findings.append("milestone_completion_mismatch")

    if tracker.get("closed") is not True:
        findings.append("tracker_issue_not_closed")

    closing_prs = _as_list(record.get("closing_prs"))
    if not closing_prs:
        findings.append("closing_pr_not_merged")
        missing_evidence.append("closing_prs")
    for pr in closing_prs:
        if not isinstance(pr, dict) or pr.get("merged") is not True:
            findings.append("closing_pr_not_merged")

    if release_tag.get("present") is not True:
        findings.append("missing_release_tag")
        missing_evidence.append("release_tag")

    if title_consistency.get("matches") is not True:
        findings.append("release_title_mismatch")

    if body_consistency.get("governance_boundary_preserved") is not True:
        findings.append("release_body_missing_governance_boundary")

    if next_phase.get("matches_expected") is not True:
        findings.append("next_phase_mismatch")

    if issue_linkage.get("present") is not True:
        findings.append("missing_related_issue_linkage")
        missing_evidence.append("related_issue_linkage")

    if boundary.get("preserved") is not True:
        findings.append("release_body_missing_governance_boundary")

    forbidden_claims = detect_forbidden_authority_claims(record)
    authority_boundary_violation = bool(forbidden_claims)
    if authority_boundary_violation:
        findings.append("authority_boundary_violation")
        if "decision_proof_sealed" in forbidden_claims or "decision_proof_sealing_authority" in forbidden_claims:
            findings.append("decision_proof_sealing_claimed_outside_aaos")
        if "audit_closed" in forbidden_claims or "audit_closure_authority" in forbidden_claims:
            findings.append("audit_closure_claimed_outside_aaos")

    return _result(findings, missing_evidence, authority_boundary_violation)


def evaluate_cross_adapter_regression(record: dict[str, Any]) -> dict[str, Any]:
    systems = [
        system
        for system in _as_list(record.get("included_systems"))
        if isinstance(system, dict)
    ]
    present_systems = {str(system.get("adapter_id")) for system in systems}
    sovereignty = _as_dict(record.get("sovereignty_checks"))

    findings: list[str] = []
    missing_evidence: list[str] = []

    missing_systems = sorted(REQUIRED_SYSTEMS - present_systems)
    if missing_systems:
        findings.append("cross_adapter_regression_missing_required_system")
        missing_evidence.extend(f"missing_system:{system}" for system in missing_systems)

    for system in systems:
        if system.get("authority_boundary_preserved") is not True:
            findings.append("adapter_claims_forbidden_authority")
        if _as_list(system.get("forbidden_authority_claims_detected")):
            findings.append("adapter_claims_forbidden_authority")
        if system.get("aaos_retained_authority_statement_present") is not True:
            findings.append("adapter_missing_aaos_retained_authority_statement")

    if sovereignty.get("all_forbidden_claims_absent") is not True:
        findings.append("adapter_claims_forbidden_authority")

    if sovereignty.get("decision_proof_sealing_claimed_outside_aaos") is True:
        findings.append("decision_proof_sealing_claimed_outside_aaos")

    if sovereignty.get("audit_closure_claimed_outside_aaos") is True:
        findings.append("audit_closure_claimed_outside_aaos")

    forbidden_claims = detect_forbidden_authority_claims(record)
    if forbidden_claims:
        findings.append("adapter_claims_forbidden_authority")

    authority_boundary_violation = any(
        finding
        in {
            "adapter_claims_forbidden_authority",
            "decision_proof_sealing_claimed_outside_aaos",
            "audit_closure_claimed_outside_aaos",
        }
        for finding in findings
    )

    return _result(findings, missing_evidence, authority_boundary_violation)


def _result(
    findings: list[str],
    missing_evidence: list[str],
    authority_boundary_violation: bool,
) -> dict[str, Any]:
    unique_findings = sorted(set(findings))
    unique_missing = sorted(set(missing_evidence))
    failed = bool(unique_findings or unique_missing)

    return {
        "release_consistency_passed": not failed,
        "release_consistency_failed": failed,
        "regression_findings": unique_findings,
        "missing_evidence": unique_missing,
        "authority_boundary_violation": authority_boundary_violation,
        "review_required": failed,
        "escalation_required": authority_boundary_violation,
        "fail_closed_recommended": authority_boundary_violation,
    }
