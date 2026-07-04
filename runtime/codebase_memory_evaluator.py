"""Deterministic checks for codebase-memory-mcp reconstruction evidence."""

from __future__ import annotations

from typing import Any


FORBIDDEN_ADAPTER_OUTPUTS = {
    "code_change_approved",
    "code_change_blocked_by_adapter",
    "final_risk_classification",
    "approval_doctrine_changed",
    "decision_route_changed",
    "rollback_decision",
    "fail_closed_policy_changed",
    "escalation_semantics_changed",
    "identity_trust_changed",
    "decision_proof_sealed",
    "audit_closed",
    "final_governance_judgment",
}

FORBIDDEN_CLAIM_VIOLATIONS = {
    "code_change_approved": "adapter_claims_approval_authority",
    "code_change_blocked_by_adapter": "adapter_claims_block_authority",
    "final_risk_classification": "adapter_claims_final_risk_classification",
    "rollback_decision": "adapter_claims_rollback_authority",
    "decision_proof_sealed": "decision_proof_sealing_claimed_by_adapter",
}

SAFE_NEGATIVE_CONTEXT_KEYS = {
    "allowed_adapter_outputs",
    "forbidden_adapter_outputs",
    "not_authority_statement",
    "sovereignty_statement",
}

ROUTE_FILE_ROLES = {"route", "api"}
ROUTE_PATH_MARKERS = ("/api/", "/routes/", "route", "handler")
HIGH_BLAST_RADIUS = {"high", "critical"}
SENSITIVE_SURFACE_KEYS = {
    "auth_surface_touched": "auth_surface_touched",
    "payment_surface_touched": "payment_surface_touched",
    "security_surface_touched": "security_surface_touched",
    "data_pipeline_surface_touched": "data_pipeline_surface_touched",
    "governance_sensitive_surface_touched": "governance_sensitive_surface_touched",
}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _is_enabled(value: Any) -> bool:
    return value is True or str(value).lower() in {"true", "allowed", "enabled", "yes"}


def _non_empty(value: Any) -> bool:
    return bool(value) and not (isinstance(value, list) and len(value) == 0)


def _extract_graph(record: dict[str, Any]) -> dict[str, Any]:
    if isinstance(record.get("codebase_graph_evidence"), dict):
        return record["codebase_graph_evidence"]
    if {"repository_id", "commit_sha", "graph_hash"}.issubset(record):
        return record
    return {}


def _extract_patch(record: dict[str, Any]) -> dict[str, Any]:
    if isinstance(record.get("patch_impact_evidence"), dict):
        return record["patch_impact_evidence"]
    if "change_id" in record:
        return record
    return {}


def detect_forbidden_authority_claims(value: Any, parent_key: str | None = None) -> set[str]:
    """Detect adapter outputs that would cross AAOS authority boundaries."""

    if parent_key in SAFE_NEGATIVE_CONTEXT_KEYS:
        return set()

    claims: set[str] = set()

    if isinstance(value, dict):
        for key, nested in value.items():
            normalized_key = str(key).lower()
            if normalized_key in FORBIDDEN_ADAPTER_OUTPUTS and _is_enabled(nested):
                claims.add(normalized_key)
            claims.update(detect_forbidden_authority_claims(nested, normalized_key))

    elif isinstance(value, list):
        for nested in value:
            claims.update(detect_forbidden_authority_claims(nested, parent_key))

    elif isinstance(value, str) and parent_key in {
        "adapter_output",
        "adapter_outputs",
        "authority_claim",
        "authority_claims",
        "output_claim",
        "output_claims",
    }:
        normalized_value = value.lower()
        if normalized_value in FORBIDDEN_ADAPTER_OUTPUTS:
            claims.add(normalized_value)

    return claims


def graph_evidence_missing(graph: dict[str, Any]) -> bool:
    return not (
        graph.get("repository_id")
        and graph.get("commit_sha")
        and graph.get("graph_hash")
        and graph.get("replay_trace_ref")
    )


def graph_evidence_is_stale(graph: dict[str, Any]) -> bool:
    freshness = _as_dict(graph.get("evidence_freshness"))
    if freshness.get("status") == "stale":
        return True
    age = freshness.get("evidence_age_days")
    max_age = freshness.get("max_age_days")
    return isinstance(age, int) and isinstance(max_age, int) and age > max_age


def route_or_api_files_changed(patch: dict[str, Any]) -> bool:
    for changed_file in _as_list(patch.get("changed_files")):
        if not isinstance(changed_file, dict):
            continue
        path = str(changed_file.get("path", "")).lower()
        role = str(changed_file.get("file_role", "")).lower()
        if role in ROUTE_FILE_ROLES or any(marker in path for marker in ROUTE_PATH_MARKERS):
            return True
    return False


def rollback_surface_missing(patch: dict[str, Any]) -> bool:
    rollback_surface = _as_dict(patch.get("rollback_surface"))
    return not (
        rollback_surface.get("complete") is True
        and rollback_surface.get("rollback_ready") is True
        and _non_empty(rollback_surface.get("candidate_refs"))
        and rollback_surface.get("owner") == "AAOS"
    )


def replay_trace_missing(graph: dict[str, Any], patch: dict[str, Any]) -> bool:
    return not (
        graph.get("replay_trace_ref")
        and patch.get("replay_ready") is True
        and _non_empty(patch.get("trace_refs"))
    )


def high_blast_radius(patch: dict[str, Any]) -> bool:
    rating = str(_as_dict(patch.get("blast_radius")).get("rating", "")).lower()
    return rating in HIGH_BLAST_RADIUS


def sensitive_surface_touched(patch: dict[str, Any]) -> bool:
    return any(patch.get(key) is True for key in SENSITIVE_SURFACE_KEYS)


def advisor_invocation_present(patch: dict[str, Any]) -> bool:
    advisor = _as_dict(patch.get("advisor_invocation"))
    trigger_types = _as_list(advisor.get("trigger_types"))
    return (
        advisor.get("required") is True
        and advisor.get("contract_ref") == "advisor_invocation_boundary"
        and advisor.get("decision_owner") == "AAOS"
        and len(trigger_types) > 0
    )


def advisor_review_should_be_required(record: dict[str, Any]) -> bool:
    graph = _extract_graph(record)
    patch = _extract_patch(record)
    return any(
        [
            high_blast_radius(patch),
            sensitive_surface_touched(patch),
            rollback_surface_missing(patch),
            replay_trace_missing(graph, patch),
            graph_evidence_is_stale(graph),
            bool(detect_forbidden_authority_claims(record)),
        ]
    )


def evaluate_codebase_memory(record: dict[str, Any]) -> dict[str, Any]:
    """Evaluate governed codebase graph and patch impact evidence.

    The evaluator returns evidence gaps and review recommendations. It does
    not approve, block, classify, roll back, fail closed, seal Decision Proof,
    close audits, or make final governance judgments.
    """

    graph = _extract_graph(record)
    patch = _extract_patch(record)
    violations: list[str] = []
    recommendations: set[str] = set()

    if graph_evidence_missing(graph):
        violations.append("missing_graph_evidence")
        recommendations.add("graph_evidence_required")

    if graph_evidence_is_stale(graph):
        violations.append("stale_evidence")
        recommendations.add("advisor_review_required")

    if not graph.get("dependency_graph_ref"):
        violations.append("missing_dependency_graph")

    if not graph.get("call_graph_ref"):
        violations.append("missing_call_graph")

    if route_or_api_files_changed(patch) and not graph.get("route_map_ref"):
        violations.append("missing_route_map")

    if not _non_empty(patch.get("affected_symbols")):
        violations.append("missing_affected_symbol_mapping")
        recommendations.add("affected_symbol_mapping_required")

    if not _non_empty(patch.get("affected_tests")):
        violations.append("missing_affected_test_mapping")
        recommendations.add("affected_test_mapping_required")

    if rollback_surface_missing(patch):
        violations.append("missing_rollback_surface")
        recommendations.add("rollback_surface_required")

    if replay_trace_missing(graph, patch):
        violations.append("missing_replay_trace")
        recommendations.add("replay_required")

    has_advisor = advisor_invocation_present(patch)
    if high_blast_radius(patch):
        recommendations.add("advisor_review_required")
        if not has_advisor:
            violations.append("high_blast_radius_without_advisor_invocation")

    if patch.get("governance_sensitive_surface_touched") is True:
        recommendations.add("advisor_review_required")
        if not has_advisor:
            violations.append("governance_sensitive_surface_touched_without_advisor_invocation")

    if sensitive_surface_touched(patch):
        recommendations.add("advisor_review_required")
        if not has_advisor:
            violations.append("sensitive_surface_touched_without_advisor_invocation")

    forbidden_claims = detect_forbidden_authority_claims(record)
    if forbidden_claims:
        violations.append("forbidden_adapter_authority_claim")
        recommendations.update({"advisor_review_required", "fail_closed_required"})
        for claim in sorted(forbidden_claims):
            mapped = FORBIDDEN_CLAIM_VIOLATIONS.get(claim)
            if mapped:
                violations.append(mapped)

    if advisor_review_should_be_required(record) and not has_advisor:
        violations.append("missing_advisor_invocation")
        recommendations.add("advisor_review_required")

    if violations:
        recommendations.add("fail_closed_required")

    return {
        "status": "review_required" if violations else "pass",
        "violations": sorted(set(violations)),
        "recommendations": sorted(recommendations),
    }
