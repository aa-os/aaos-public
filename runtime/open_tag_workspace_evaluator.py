"""Deterministic checks for open-tag human-agent workspace evidence."""

from __future__ import annotations

from typing import Any


FORBIDDEN_OPEN_TAG_OUTPUTS = {
    "business_intent_changed",
    "risk_appetite_changed",
    "approval_doctrine_changed",
    "identity_trust_changed",
    "policy_authority_changed",
    "decision_route_changed",
    "escalation_semantics_changed",
    "fail_closed_policy_changed",
    "rollback_decision",
    "final_risk_classification",
    "decision_proof_sealed",
    "audit_closed",
    "final_governance_judgment",
}

FORBIDDEN_CLAIM_VIOLATIONS = {
    "policy_authority_changed": "open_tag_claims_policy_authority",
    "decision_route_changed": "open_tag_claims_decision_router_authority",
    "rollback_decision": "open_tag_claims_rollback_authority",
    "decision_proof_sealed": "open_tag_claims_decision_proof_sealing_authority",
    "final_risk_classification": "open_tag_claims_final_risk_classification",
    "audit_closed": "open_tag_claims_audit_closure_authority",
    "final_governance_judgment": "open_tag_claims_final_governance_authority",
}

SAFE_NEGATIVE_CONTEXT_KEYS = {
    "allowed_open_tag_outputs",
    "forbidden_open_tag_outputs",
    "not_authority_statement",
    "sovereignty_statement",
}

REQUIRED_DECISION_FIELDS = {
    "decision_id": "missing_decision_id",
    "intent": "missing_intent",
    "actor": "missing_actor",
    "authority_source": "missing_authority_source",
    "risk_class": "missing_risk_class",
    "allowed_tools": "missing_allowed_tools",
    "approval_required": "missing_approval_required",
    "rollback_plan": "missing_rollback_plan",
    "evidence_required": "missing_evidence_required",
    "completion_criteria": "missing_completion_criteria",
    "execution_trace": "missing_execution_trace",
    "replay_target": "missing_replay_target",
}

HIGH_RISK_CLASSES = {"high", "critical"}
TASK_EXECUTION_EVENTS = {"task_execution_started", "task_execution_completed"}
GOVERNANCE_SENSITIVE_EVENTS = {"governance_sensitive_workspace_event"}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _is_enabled(value: Any) -> bool:
    return value is True or str(value).lower() in {"true", "allowed", "enabled", "yes"}


def _non_empty(value: Any) -> bool:
    return bool(value) and not (isinstance(value, list) and len(value) == 0)


def _extract_activities(record: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(record.get("activity_evidence"), list):
        return [activity for activity in record["activity_evidence"] if isinstance(activity, dict)]
    if isinstance(record.get("activity_evidence"), dict):
        return [record["activity_evidence"]]
    if "workspace_id" in record:
        return [record]
    return []


def _extract_decision_contract(record: dict[str, Any]) -> dict[str, Any]:
    if isinstance(record.get("decision_contract_injection"), dict):
        return record["decision_contract_injection"]
    if "workspace_binding" in record and "decision_id" in record:
        return record
    return {}


def detect_forbidden_authority_claims(value: Any, parent_key: str | None = None) -> set[str]:
    """Detect open-tag outputs that would cross AAOS authority boundaries."""

    if parent_key in SAFE_NEGATIVE_CONTEXT_KEYS:
        return set()

    claims: set[str] = set()

    if isinstance(value, dict):
        for key, nested in value.items():
            normalized_key = str(key).lower()
            if normalized_key in FORBIDDEN_OPEN_TAG_OUTPUTS and _is_enabled(nested):
                claims.add(normalized_key)
            claims.update(detect_forbidden_authority_claims(nested, normalized_key))

    elif isinstance(value, list):
        for nested in value:
            claims.update(detect_forbidden_authority_claims(nested, parent_key))

    elif isinstance(value, str) and parent_key in {
        "open_tag_output",
        "open_tag_outputs",
        "authority_claim",
        "authority_claims",
        "output_claim",
        "output_claims",
    }:
        normalized_value = value.lower()
        if normalized_value in FORBIDDEN_OPEN_TAG_OUTPUTS:
            claims.add(normalized_value)

    return claims


def decision_contract_field_violations(contract: dict[str, Any]) -> list[str]:
    violations: list[str] = []

    for field, violation in REQUIRED_DECISION_FIELDS.items():
        if field == "approval_required":
            if not isinstance(contract.get(field), bool):
                violations.append(violation)
        elif field in {"allowed_tools", "evidence_required", "completion_criteria"}:
            if not _non_empty(contract.get(field)):
                violations.append(violation)
        elif field == "rollback_plan":
            rollback = _as_dict(contract.get("rollback_plan"))
            if not (rollback and rollback.get("plan_ref") and rollback.get("owner") == "AAOS"):
                violations.append(violation)
        elif field == "execution_trace":
            trace = _as_dict(contract.get("execution_trace"))
            if not (trace.get("required") is True and trace.get("trace_ref")):
                violations.append(violation)
        elif field == "replay_target":
            target = _as_dict(contract.get("replay_target"))
            if not (target.get("required") is True and target.get("target_ref")):
                violations.append(violation)
        elif not contract.get(field):
            violations.append(violation)

    return violations


def actor_agent_daemon_separated(activity: dict[str, Any]) -> bool:
    actor = activity.get("actor")
    agent_id = activity.get("agent_id")
    daemon_id = activity.get("daemon_id")
    values = [actor, agent_id, daemon_id]
    return all(isinstance(value, str) and value for value in values) and len(set(values)) == 3


def approval_state_missing(activity: dict[str, Any]) -> bool:
    return activity.get("approval_required") is True and activity.get("approval_state") in {
        None,
        "",
        "missing",
    }


def rollback_plan_missing(activity: dict[str, Any], contract: dict[str, Any]) -> bool:
    if not activity.get("rollback_plan_ref"):
        return True
    rollback = _as_dict(contract.get("rollback_plan"))
    if rollback:
        return not (rollback.get("required") is True and rollback.get("plan_ref"))
    return False


def execution_trace_missing(activity: dict[str, Any], contract: dict[str, Any]) -> bool:
    trace = _as_dict(contract.get("execution_trace"))
    return not (activity.get("execution_trace_ref") or trace.get("trace_ref"))


def replay_target_missing(activity: dict[str, Any], contract: dict[str, Any]) -> bool:
    target = _as_dict(contract.get("replay_target"))
    return not (activity.get("replay_target_ref") or target.get("target_ref"))


def advisor_invocation_present(activity: dict[str, Any], contract: dict[str, Any]) -> bool:
    advisor = _as_dict(activity.get("advisor_invocation")) or _as_dict(
        contract.get("advisor_invocation")
    )
    return (
        advisor.get("required") is True
        and advisor.get("contract_ref") == "advisor_invocation_boundary"
        and advisor.get("decision_owner") == "AAOS"
        and _non_empty(advisor.get("trigger_types"))
    )


def advisor_review_should_be_required(record: dict[str, Any]) -> bool:
    contract = _extract_decision_contract(record)
    activities = _extract_activities(record)
    forbidden_claims = detect_forbidden_authority_claims(record)

    for activity in activities:
        if str(activity.get("risk_class", "")).lower() in HIGH_RISK_CLASSES:
            return True
        if approval_state_missing(activity):
            return True
        if rollback_plan_missing(activity, contract):
            return True
        if execution_trace_missing(activity, contract):
            return True
        if replay_target_missing(activity, contract):
            return True
        if activity.get("event_type") == "runtime_adapter_event" and not activity.get("task_id"):
            return True
        if activity.get("event_type") in TASK_EXECUTION_EVENTS and not contract:
            return True
        if activity.get("event_type") in GOVERNANCE_SENSITIVE_EVENTS:
            return True

    return bool(forbidden_claims)


def evaluate_open_tag_workspace(record: dict[str, Any]) -> dict[str, Any]:
    """Evaluate governed open-tag workspace evidence.

    The evaluator returns boundary violations and review recommendations. It
    does not approve, block, route, roll back, fail closed, seal Decision
    Proof, close audits, or make final governance judgments.
    """

    activities = _extract_activities(record)
    contract = _extract_decision_contract(record)
    violations: list[str] = []
    recommendations: set[str] = set()

    if not contract:
        violations.extend(decision_contract_field_violations({}))
    else:
        violations.extend(decision_contract_field_violations(contract))

    for activity in activities:
        if not activity.get("decision_id"):
            violations.append("missing_decision_id")
        if not activity.get("intent"):
            violations.append("missing_intent")
        if not activity.get("actor"):
            violations.append("missing_actor")
        if not activity.get("authority_source"):
            violations.append("missing_authority_source")
        if not activity.get("risk_class"):
            violations.append("missing_risk_class")
        if not _non_empty(activity.get("allowed_tools")):
            violations.append("missing_allowed_tools")
        if not isinstance(activity.get("approval_required"), bool):
            violations.append("missing_approval_required")
        if not activity.get("rollback_plan_ref"):
            violations.append("missing_rollback_plan")
        if not _non_empty(activity.get("evidence_required")):
            violations.append("missing_evidence_required")
        if not _non_empty(activity.get("completion_criteria")):
            violations.append("missing_completion_criteria")
        if execution_trace_missing(activity, contract):
            violations.append("missing_execution_trace")
            recommendations.add("execution_trace_required")
        if replay_target_missing(activity, contract):
            violations.append("missing_replay_target")
            recommendations.add("replay_target_required")
        if not actor_agent_daemon_separated(activity):
            violations.append("missing_actor_agent_daemon_separation")
            recommendations.add("actor_agent_daemon_separation_required")
        if activity.get("event_type") == "runtime_adapter_event" and not activity.get("task_id"):
            violations.append("runtime_adapter_event_without_task_binding")
        if activity.get("event_type") in TASK_EXECUTION_EVENTS and not contract:
            violations.append("task_execution_without_decision_contract")
        if approval_state_missing(activity):
            violations.append("approval_required_but_missing_approval_state")
            recommendations.add("approval_mapping_required")
        if rollback_plan_missing(activity, contract):
            violations.append("rollback_required_but_missing_rollback_plan")
            recommendations.add("rollback_mapping_required")

        has_advisor = advisor_invocation_present(activity, contract)
        if str(activity.get("risk_class", "")).lower() in HIGH_RISK_CLASSES:
            recommendations.add("advisor_review_required")
            if not has_advisor:
                violations.append("high_risk_task_without_advisor_invocation")
        if activity.get("event_type") in GOVERNANCE_SENSITIVE_EVENTS:
            recommendations.add("advisor_review_required")
            if not has_advisor:
                violations.append("governance_sensitive_workspace_event_without_advisor_invocation")

    forbidden_claims = detect_forbidden_authority_claims(record)
    if forbidden_claims:
        violations.append("forbidden_open_tag_authority_claim")
        recommendations.update({"advisor_review_required", "fail_closed_required"})
        for claim in sorted(forbidden_claims):
            mapped = FORBIDDEN_CLAIM_VIOLATIONS.get(claim)
            if mapped:
                violations.append(mapped)
            if claim == "decision_proof_sealed":
                violations.append("decision_proof_sealing_claimed_by_open_tag")

    if advisor_review_should_be_required(record):
        recommendations.add("advisor_review_required")

    if violations:
        recommendations.add("fail_closed_required")

    return {
        "status": "review_required" if violations else "pass",
        "violations": sorted(set(violations)),
        "recommendations": sorted(recommendations),
    }
