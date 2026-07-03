"""Deterministic evaluator for high-risk Heretic specimen registry records."""

from __future__ import annotations

from typing import Any


REQUIRED_RISK_TAGS = {
    "high_risk": "missing_high_risk_tag",
    "decensored": "missing_decensored_tag",
}

ACCESS_VIOLATIONS = {
    "network_access": "network_access_allowed",
    "write_access": "write_access_allowed",
    "credential_access": "credential_access_allowed",
    "production_tool_access": "production_tool_access_allowed",
}

CONTAINMENT_FLAGS = {
    "network_access": "no_network_access",
    "write_access": "no_write_access",
    "credential_access": "no_credential_access",
    "production_tool_access": "no_production_tools",
}

SAFE_NEGATIVE_CONTEXT_KEYS = {
    "blocked_capabilities",
    "forbidden_specimen_use",
    "not_authority_statement",
    "sovereignty_statement",
}

DECISION_AUTHORITY_KEYS = {
    "decision_router",
    "decision_router_authority",
    "workflow_routing",
}

POLICY_AUTHORITY_KEYS = {
    "policy_layer_modification",
    "policy_modification_capability",
    "governance_policy_rewrite",
}


def _risk_tags(record: dict[str, Any]) -> set[str]:
    tags = record.get("risk_tags", [])
    if not isinstance(tags, list):
        return set()
    return {str(tag) for tag in tags}


def _allowed_environment(record: dict[str, Any]) -> dict[str, Any]:
    environment = record.get("allowed_environment", {})
    if not isinstance(environment, dict):
        return {}
    return environment


def _containment_controls(record: dict[str, Any]) -> dict[str, Any]:
    controls = record.get("containment_controls", {})
    if not isinstance(controls, dict):
        return {}
    return controls


def _is_enabled(value: Any) -> bool:
    return value is True or str(value).lower() in {"true", "allowed", "enabled", "yes"}


def _contains_production_environment_claim(environment: dict[str, Any]) -> bool:
    environment_type = str(environment.get("environment_type", "")).lower()
    return "production" in environment_type or environment_type != "isolated_local_sandbox"


def _rollback_rule_missing(record: dict[str, Any]) -> bool:
    rollback_rule = record.get("rollback_rule", {})
    if not isinstance(rollback_rule, dict):
        return True
    return not (
        rollback_rule.get("required") is True
        and rollback_rule.get("rule_ref")
        and rollback_rule.get("trigger")
    )


def _advisor_invocation_missing(record: dict[str, Any]) -> bool:
    advisor_invocation = record.get("advisor_invocation", {})
    if not isinstance(advisor_invocation, dict):
        return True
    trigger_types = advisor_invocation.get("trigger_types", [])
    return not (
        advisor_invocation.get("required") is True
        and advisor_invocation.get("contract_ref") == "advisor_invocation_boundary"
        and isinstance(trigger_types, list)
        and "high_risk_adversarial_specimen" in trigger_types
    )


def detect_forbidden_authority_claims(value: Any, parent_key: str | None = None) -> set[str]:
    """Detect affirmative decision or policy authority claims."""

    if parent_key in SAFE_NEGATIVE_CONTEXT_KEYS:
        return set()

    violations: set[str] = set()

    if isinstance(value, dict):
        for key, nested in value.items():
            normalized_key = str(key).lower()

            if normalized_key in DECISION_AUTHORITY_KEYS and _is_enabled(nested):
                violations.add("decision_router_authority_claimed")

            if normalized_key in POLICY_AUTHORITY_KEYS and _is_enabled(nested):
                violations.add("policy_modification_capability_claimed")

            violations.update(detect_forbidden_authority_claims(nested, normalized_key))

    elif isinstance(value, list):
        for item in value:
            violations.update(detect_forbidden_authority_claims(item, parent_key))

    elif isinstance(value, str) and parent_key in {
        "authority_claim",
        "authority_claims",
        "allowed_capability",
        "allowed_capabilities",
    }:
        normalized_value = value.lower()
        if normalized_value in DECISION_AUTHORITY_KEYS:
            violations.add("decision_router_authority_claimed")
        if normalized_value in POLICY_AUTHORITY_KEYS:
            violations.add("policy_modification_capability_claimed")

    return violations


def evaluate_heretic_specimen(record: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a high-risk Heretic specimen registry record.

    The evaluator returns boundary violations and review recommendations.
    It does not make AAOS admission, release, rollback, or risk-acceptance decisions.
    """

    violations: list[str] = []
    recommendations: set[str] = {"advisor_review_required", "block_production_tools"}

    tags = _risk_tags(record)
    for required_tag, violation in REQUIRED_RISK_TAGS.items():
        if required_tag not in tags:
            violations.append(violation)

    environment = _allowed_environment(record)
    controls = _containment_controls(record)

    if _contains_production_environment_claim(environment):
        violations.append("production_environment_claim")

    for access_key, violation in ACCESS_VIOLATIONS.items():
        control_key = CONTAINMENT_FLAGS[access_key]
        if _is_enabled(environment.get(access_key)) or controls.get(control_key) is not True:
            violations.append(violation)

    authority_violations = detect_forbidden_authority_claims(record)
    violations.extend(sorted(authority_violations))

    if record.get("trace_logging_required") is not True or controls.get("full_trace_logging") is not True:
        violations.append("missing_trace_logging")

    if record.get("replay_required") is not True or controls.get("replay_ready_evidence") is not True:
        violations.append("missing_replay_requirement")
        recommendations.add("replay_required")

    if record.get("fail_closed_required") is not True or controls.get("fail_closed_enforced") is not True:
        violations.append("missing_fail_closed_requirement")
        recommendations.add("fail_closed_required")

    if _rollback_rule_missing(record):
        violations.append("missing_rollback_rule")
        recommendations.add("fail_closed_required")

    if _advisor_invocation_missing(record):
        violations.append("missing_advisor_invocation")

    if any(
        violation in violations
        for violation in {
            "production_environment_claim",
            "network_access_allowed",
            "write_access_allowed",
            "credential_access_allowed",
            "production_tool_access_allowed",
        }
    ):
        recommendations.add("containment_required")

    if violations:
        recommendations.add("fail_closed_required")

    return {
        "status": "review_required" if violations else "pass",
        "violations": sorted(set(violations)),
        "recommendations": sorted(recommendations),
    }
