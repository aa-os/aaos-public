"""Deterministic checks for SkillOpt governed skill artifacts."""

from __future__ import annotations

from typing import Any


FORBIDDEN_SKILLOPT_OUTPUTS = {
    "deployment_approved",
    "deployment_rejected_by_skillopt",
    "risk_accepted",
    "waiver_granted",
    "approval_doctrine_changed",
    "identity_trust_changed",
    "rollback_executed",
    "decision_route_changed",
    "governance_policy_rewritten",
    "audit_closed",
    "final_governance_judgment",
}

FORBIDDEN_CLAIM_VIOLATIONS = {
    "deployment_approved": "deployment_approved_by_skillopt",
    "deployment_rejected_by_skillopt": "deployment_rejected_by_skillopt",
    "risk_accepted": "risk_accepted_by_skillopt",
    "identity_trust_changed": "identity_trust_changed_by_skillopt",
    "governance_policy_rewritten": "governance_policy_rewritten_by_skillopt",
    "audit_closed": "audit_closed_by_skillopt",
    "final_governance_judgment": "final_governance_judgment_claimed_by_skillopt",
}

SAFE_NEGATIVE_CONTEXT_KEYS = {
    "forbidden_skillopt_outputs",
    "not_authority_statement",
    "sovereignty_statement",
}

GOVERNANCE_REVIEW_TRIGGERS = {
    "authority_boundary_change",
    "tool_use_expansion",
    "data_access_expansion",
    "autonomy_increase",
    "safety_behavior_change",
    "validation_improved_policy_risk_increased",
    "rollback_or_replay_missing",
    "deployment_gate_failure_or_incomplete",
    "skillopt_authority_claim",
}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _is_enabled(value: Any) -> bool:
    return value is True or str(value).lower() in {"true", "allowed", "enabled", "yes"}


def _non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0


def detect_forbidden_authority_claims(value: Any, parent_key: str | None = None) -> set[str]:
    """Detect SkillOpt outputs that would cross AAOS authority boundaries."""

    if parent_key in SAFE_NEGATIVE_CONTEXT_KEYS:
        return set()

    claims: set[str] = set()

    if isinstance(value, dict):
        for key, nested in value.items():
            normalized_key = str(key).lower()
            if normalized_key in FORBIDDEN_SKILLOPT_OUTPUTS and _is_enabled(nested):
                claims.add(normalized_key)
            claims.update(detect_forbidden_authority_claims(nested, normalized_key))

    elif isinstance(value, list):
        for nested in value:
            claims.update(detect_forbidden_authority_claims(nested, parent_key))

    elif isinstance(value, str) and parent_key in {
        "authority_claim",
        "authority_claims",
        "skillopt_output",
        "skillopt_outputs",
        "output_claims",
    }:
        normalized_value = value.lower()
        if normalized_value in FORBIDDEN_SKILLOPT_OUTPUTS:
            claims.add(normalized_value)

    return claims


def rollback_plan_missing(record: dict[str, Any]) -> bool:
    rollback_plan = _as_dict(record.get("rollback_plan"))
    return not (
        rollback_plan.get("ready") is True
        and rollback_plan.get("plan_ref")
        and rollback_plan.get("owner") == "AAOS"
        and rollback_plan.get("trigger")
    )


def replay_traces_missing(record: dict[str, Any]) -> bool:
    return not _non_empty_list(record.get("replay_trace_refs"))


def validation_evidence_missing(record: dict[str, Any]) -> bool:
    validation_results = _as_list(record.get("validation_results"))
    evidence_hashes = _as_list(record.get("evidence_hashes"))
    has_result_evidence = any(
        isinstance(result, dict) and result.get("evidence_ref")
        for result in validation_results
    )
    return not (has_result_evidence and _non_empty_list(evidence_hashes))


def rejected_edit_history_missing(record: dict[str, Any]) -> bool:
    return not _non_empty_list(record.get("rejected_edits"))


def deployment_gate_missing(record: dict[str, Any]) -> bool:
    gate = _as_dict(record.get("deployment_gate"))
    checks = _as_dict(gate.get("checks"))
    return not (gate.get("status") and gate.get("approval_owner") == "AAOS" and checks)


def deployment_gate_fails_or_incomplete(record: dict[str, Any]) -> bool:
    gate = _as_dict(record.get("deployment_gate"))
    return gate.get("status") in {"fail", "incomplete"}


def _impact_requires_review(record: dict[str, Any]) -> set[str]:
    triggers: set[str] = set()

    authority_impact = _as_dict(record.get("authority_impact"))
    if (
        authority_impact.get("boundary_changed") is True
        or authority_impact.get("impact_level") in {"expanded", "ambiguous"}
    ):
        triggers.add("authority_boundary_change")

    tool_impact = _as_dict(record.get("tool_use_impact"))
    if tool_impact.get("expanded") is True or tool_impact.get("impact_level") in {
        "expanded",
        "high",
    }:
        triggers.add("tool_use_expansion")

    data_impact = _as_dict(record.get("data_access_impact"))
    if data_impact.get("expanded") is True or data_impact.get("impact_level") in {
        "expanded",
        "high",
    }:
        triggers.add("data_access_expansion")

    autonomy_impact = _as_dict(record.get("autonomy_impact"))
    if autonomy_impact.get("increased") is True or autonomy_impact.get("impact_level") in {
        "expanded",
        "high",
    }:
        triggers.add("autonomy_increase")

    safety_impact = _as_dict(record.get("safety_impact"))
    if (
        safety_impact.get("affects_safety_behavior") is True
        or safety_impact.get("risk_level") in {"high", "critical"}
    ):
        triggers.add("safety_behavior_change")

    validation_scores = _as_dict(record.get("validation_scores"))
    policy_precheck = _as_dict(record.get("policy_precheck"))
    if (
        validation_scores.get("validation_improved") is True
        and policy_precheck.get("policy_risk_increased") is True
    ):
        triggers.add("validation_improved_policy_risk_increased")

    return triggers


def advisor_review_triggers(record: dict[str, Any]) -> set[str]:
    triggers = _impact_requires_review(record)

    if rollback_plan_missing(record) or replay_traces_missing(record):
        triggers.add("rollback_or_replay_missing")

    if deployment_gate_fails_or_incomplete(record):
        triggers.add("deployment_gate_failure_or_incomplete")

    if detect_forbidden_authority_claims(record):
        triggers.add("skillopt_authority_claim")

    return triggers


def advisor_invocation_missing(record: dict[str, Any]) -> bool:
    triggers = advisor_review_triggers(record)
    if not triggers:
        return False

    advisor_invocation = _as_dict(record.get("advisor_invocation"))
    trigger_types = set(_as_list(advisor_invocation.get("trigger_types")))
    return not (
        advisor_invocation.get("required") is True
        and advisor_invocation.get("contract_ref") == "advisor_invocation_boundary"
        and advisor_invocation.get("decision_owner") == "AAOS"
        and bool(trigger_types & GOVERNANCE_REVIEW_TRIGGERS)
    )


def evaluate_skillopt_governance(record: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a SkillOpt governed skill artifact.

    The evaluator returns boundary violations and readiness recommendations.
    It does not make AAOS deployment, rollback, risk, audit, or governance decisions.
    """

    violations: list[str] = []
    recommendations: set[str] = set()

    forbidden_claims = detect_forbidden_authority_claims(record)
    if forbidden_claims:
        violations.append("forbidden_skillopt_authority_claim")
        for claim in sorted(forbidden_claims):
            mapped_violation = FORBIDDEN_CLAIM_VIOLATIONS.get(claim)
            if mapped_violation:
                violations.append(mapped_violation)
        recommendations.update({"advisor_review_required", "fail_closed_required"})

    if rollback_plan_missing(record):
        violations.append("missing_rollback_plan")
        recommendations.add("rollback_readiness_required")

    if replay_traces_missing(record):
        violations.append("missing_replay_traces")
        recommendations.add("replay_required")

    if validation_evidence_missing(record):
        violations.append("missing_validation_evidence")
        recommendations.add("validation_evidence_required")

    if rejected_edit_history_missing(record):
        violations.append("missing_rejected_edit_history")
        recommendations.add("rejected_edit_history_required")

    if deployment_gate_missing(record):
        violations.append("missing_deployment_gate")
        recommendations.add("deployment_gate_required")

    if advisor_invocation_missing(record):
        violations.append("missing_advisor_invocation")
        recommendations.add("advisor_review_required")

    if advisor_review_triggers(record):
        recommendations.add("advisor_review_required")

    if violations:
        recommendations.add("fail_closed_required")

    return {
        "status": "review_required" if violations else "pass",
        "violations": sorted(set(violations)),
        "recommendations": sorted(recommendations),
    }
