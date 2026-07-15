"""Deterministic checks for M13 runtime approval gate evidence."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from runtime.authority_semantics import scan_forbidden_authority_claims


REQUIRED_ARTIFACT_FIELDS = {
    "artifact_id": "missing_artifact_id",
    "artifact_name": "missing_artifact_name",
    "artifact_scope": "missing_artifact_scope",
    "artifact_status": "missing_artifact_status",
    "related_issue": "missing_related_issue_176",
    "runtime_approval_gate_issue": "missing_runtime_approval_gate_issue_171",
    "introduced_after_release": "missing_introduced_after_release_v0_11_0",
    "target_future_release": "missing_target_future_release_v0_12_0",
    "m11_status_boundary": "missing_m11_status_boundary",
    "m12_status_boundary": "missing_m12_status_boundary",
    "approval_gate_modes": "missing_approval_gate_modes",
    "required_enforced_gate_trace_fields": "missing_required_enforced_gate_trace_fields",
    "verification_rules": "missing_verification_rules",
    "regression_fixtures": "missing_regression_fixtures",
    "allowed_evaluator_outputs": "missing_allowed_evaluator_outputs",
    "forbidden_evaluator_outputs": "missing_forbidden_evaluator_outputs",
    "authority_boundary": "missing_authority_boundary",
    "governance_boundary_statement": "missing_governance_boundary_statement",
    "decision_proof_sealing_boundary_statement": "missing_decision_proof_sealing_boundary_statement",
    "aaos_retained_authority_statement": "missing_aaos_retained_authority_statement",
    "sovereignty_statement": "missing_sovereignty_statement",
}

REQUIRED_GATE_MODES = {"observed", "advisory", "enforced"}

REQUIRED_ENFORCED_TRACE_FIELDS = {
    "blocked_tool_call_id",
    "gate_event_id",
    "gate_mode",
    "gate_state",
    "approval_event_id",
    "approval_actor",
    "approval_timestamp",
    "tool_call_requested_at",
    "tool_call_released_at",
    "tool_call_executed_at",
}

REQUIRED_VERIFICATION_RULES = {
    "enforced_gate_event_before_execution",
    "approval_before_release_and_execution",
    "approval_bound_to_blocked_tool_call",
    "advisory_does_not_satisfy_enforced_approval",
    "post_facto_approval_fails_enforced_verification",
    "missing_ordering_or_binding_evidence_fails_closed",
}

REQUIRED_REGRESSION_FIXTURES = {
    "post_facto_advisory_approval",
    "approval_state_only_trace",
    "valid_halt_approval_release_execution_trace",
    "observed_only_trace",
}

REQUIRED_AUTHORITY_MAY = {
    "produce_evidence",
    "consume_evidence",
    "reference_evidence",
    "inspect_evidence",
    "replay_evidence",
    "report_findings",
    "check_evidence",
    "link_evidence",
    "prove_gate_observation",
    "prove_gate_advice",
    "prove_gate_enforcement",
    "surface_review_required",
    "surface_escalation_required",
    "surface_fail_closed_recommended",
}

REQUIRED_AUTHORITY_MUST_NOT = {
    "approve_execution",
    "accept_risk",
    "seal_decision_proof",
    "execute_rollback",
    "execute_fail_closed",
    "close_audits",
    "grant_waivers",
    "change_approval_doctrine",
    "change_identity_trust",
    "change_policy_authority",
    "change_decision_routing",
    "make_final_governance_judgments",
}

REQUIRED_ALLOWED_OUTPUTS = {
    "runtime_approval_gate_evidence_valid",
    "runtime_approval_gate_evidence_invalid",
    "approval_gate_modes_present",
    "required_enforced_gate_trace_fields_present",
    "regression_fixture_coverage_complete",
    "enforced_gate_trace_valid",
    "enforced_gate_trace_invalid",
    "observed_trace_valid",
    "advisory_trace_valid",
    "authority_boundary_preserved",
    "authority_boundary_violation",
    "review_required",
    "escalation_required",
    "fail_closed_recommended",
}

FORBIDDEN_EVALUATOR_OUTPUTS = {
    "execution_approved",
    "release_approved",
    "risk_accepted",
    "decision_proof_sealed",
    "rollback_executed",
    "fail_closed_executed",
    "audit_closed",
    "final_governance_judgment",
}

SAFE_CONTEXT_KEYS = {
    "allowed_evaluator_outputs",
    "forbidden_evaluator_outputs",
    "authority_boundary",
    "must_not",
    "expected_evaluator_outputs",
    "negative_fixture_boundary",
}

FORBIDDEN_AUTHORITY_KEYS = FORBIDDEN_EVALUATOR_OUTPUTS | {
    "evaluator_outputs",
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



def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None



def _before_or_equal(left: Any, right: Any) -> bool:
    left_time = _parse_timestamp(left)
    right_time = _parse_timestamp(right)
    return left_time is not None and right_time is not None and left_time <= right_time



def _after(left: Any, right: Any) -> bool:
    left_time = _parse_timestamp(left)
    right_time = _parse_timestamp(right)
    return left_time is not None and right_time is not None and left_time > right_time



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



def detect_runtime_approval_gate_forbidden_claims(
    value: Any, parent_key: str | None = None
) -> set[str]:
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
    return claims



def evaluate_approval_gate_trace(trace: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    mode = _text(trace.get("gate_mode"))
    authority_boundary_violation = False
    fail_closed = False

    if mode not in REQUIRED_GATE_MODES:
        findings.append("approval_gate_mode_invalid")
        missing_evidence.append("gate_mode")
        fail_closed = True

    if _has_enforced_claim(trace) and mode != "enforced":
        findings.append(f"{mode or 'missing'}_trace_claimed_as_enforced")
        authority_boundary_violation = True
        fail_closed = True

    if mode == "observed":
        if _text(trace.get("gate_state")) != "observed":
            findings.append("observed_trace_state_invalid")
            missing_evidence.append("gate_state")

    if mode == "advisory":
        if _text(trace.get("gate_state")) != "advisory_only":
            findings.append("advisory_trace_state_invalid")
            missing_evidence.append("gate_state")
        if _post_facto_approval(trace):
            findings.append("post_facto_approval_detected")
            fail_closed = True

    if mode == "enforced":
        for field in REQUIRED_ENFORCED_TRACE_FIELDS:
            if not _has_value(trace, field):
                findings.append(f"missing_enforced_trace_{field}")
                missing_evidence.append(field)
                fail_closed = True

        if _text(trace.get("gate_state")) not in {"blocked", "halted"}:
            findings.append("enforced_gate_missing_block_state")
            fail_closed = True

        if not _gate_event_bound_to_tool_call(trace):
            findings.append("gate_event_binding_missing")
            missing_evidence.append("gate_event")
            fail_closed = True

        if not _approval_bound_to_tool_call(trace):
            findings.append("approval_binding_missing")
            missing_evidence.append("approval_binding")
            fail_closed = True

        if not _gate_event_before_execution(trace):
            findings.append("gate_event_ordering_invalid")
            missing_evidence.append("gate_event.occurred_at")
            fail_closed = True

        if not _approval_before_release_and_execution(trace):
            findings.append("approval_ordering_invalid")
            missing_evidence.append("approval_timestamp")
            fail_closed = True

    forbidden_claims = detect_runtime_approval_gate_forbidden_claims(trace)
    if forbidden_claims:
        findings.append("authority_transfer_claim_detected")
        authority_boundary_violation = True
        fail_closed = True

    failed = bool(findings or missing_evidence or authority_boundary_violation)
    return {
        "approval_gate_trace_valid": not failed,
        "approval_gate_trace_invalid": failed,
        "enforced_gate_trace_valid": mode == "enforced" and not failed,
        "enforced_gate_trace_invalid": mode != "enforced" or failed,
        "observed_trace_valid": mode == "observed" and not failed,
        "advisory_trace_valid": mode == "advisory" and not failed,
        "enforcement_satisfied": mode == "enforced" and not failed,
        "authority_boundary_preserved": not authority_boundary_violation,
        "authority_boundary_violation": authority_boundary_violation,
        "trace_findings": sorted(set(findings)),
        "missing_evidence": sorted(set(missing_evidence)),
        "review_required": failed,
        "escalation_required": authority_boundary_violation,
        "fail_closed_recommended": fail_closed,
    }



def evaluate_runtime_approval_gate_evidence(artifact: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    authority_boundary_violation = False

    def add_missing(finding: str, evidence: str) -> None:
        findings.append(finding)
        missing_evidence.append(evidence)

    for field, finding in REQUIRED_ARTIFACT_FIELDS.items():
        if not _has_value(artifact, field):
            add_missing(finding, field)

    if artifact.get("related_issue") != "#176":
        add_missing("missing_related_issue_176", "related_issue")
    if artifact.get("runtime_approval_gate_issue") != "#171":
        add_missing("missing_runtime_approval_gate_issue_171", "runtime_approval_gate_issue")
    if artifact.get("introduced_after_release") != "v0.11.0":
        add_missing("missing_introduced_after_release_v0_11_0", "introduced_after_release")
    if artifact.get("target_future_release") != "v0.12.0":
        add_missing("missing_target_future_release_v0_12_0", "target_future_release")

    if _completed_milestone_reopen_claim(artifact):
        findings.append("completed_milestone_reopen_claim_detected")
        authority_boundary_violation = True

    gate_modes = {
        _text(mode.get("mode"))
        for mode in _as_list(artifact.get("approval_gate_modes"))
        if isinstance(mode, dict)
    }
    approval_gate_modes_present = REQUIRED_GATE_MODES <= gate_modes
    if not approval_gate_modes_present:
        add_missing("approval_gate_modes_missing", "approval_gate_modes")

    required_trace_fields_present = REQUIRED_ENFORCED_TRACE_FIELDS <= _as_set(
        artifact.get("required_enforced_gate_trace_fields")
    )
    if not required_trace_fields_present:
        add_missing(
            "required_enforced_gate_trace_fields_missing",
            "required_enforced_gate_trace_fields",
        )

    rule_ids = {
        _text(rule.get("rule_id"))
        for rule in _as_list(artifact.get("verification_rules"))
        if isinstance(rule, dict)
    }
    if not REQUIRED_VERIFICATION_RULES <= rule_ids:
        add_missing("verification_rules_missing", "verification_rules")

    fixtures = {
        fixture.get("fixture_id"): fixture
        for fixture in _as_list(artifact.get("regression_fixtures"))
        if isinstance(fixture, dict)
    }
    regression_fixture_coverage_complete = REQUIRED_REGRESSION_FIXTURES <= set(fixtures)
    if not regression_fixture_coverage_complete:
        add_missing("regression_fixture_coverage_incomplete", "regression_fixtures")

    _evaluate_fixture_expectations(fixtures, findings, missing_evidence)

    if not _authority_boundary_complete(artifact):
        add_missing("authority_boundary_statement_incomplete", "authority_boundary")

    if not _required_boundary_language_present(artifact):
        add_missing("missing_aaos_authority_boundary_statement", "governance_boundary_statement")

    allowed_outputs = _as_set(artifact.get("allowed_evaluator_outputs"))
    if not REQUIRED_ALLOWED_OUTPUTS <= allowed_outputs:
        add_missing("allowed_evaluator_outputs_missing", "allowed_evaluator_outputs")

    forbidden_outputs = _as_set(artifact.get("forbidden_evaluator_outputs"))
    if not FORBIDDEN_EVALUATOR_OUTPUTS <= forbidden_outputs:
        add_missing("forbidden_evaluator_outputs_missing", "forbidden_evaluator_outputs")

    forbidden_claims = detect_runtime_approval_gate_forbidden_claims(artifact)
    if forbidden_claims:
        findings.append("authority_transfer_claim_detected")
        authority_boundary_violation = True

    failed = bool(findings or missing_evidence or authority_boundary_violation)
    return {
        "runtime_approval_gate_evidence_valid": not failed,
        "runtime_approval_gate_evidence_invalid": failed,
        "approval_gate_modes_present": approval_gate_modes_present,
        "required_enforced_gate_trace_fields_present": required_trace_fields_present,
        "regression_fixture_coverage_complete": regression_fixture_coverage_complete,
        "authority_boundary_preserved": not authority_boundary_violation,
        "authority_boundary_violation": authority_boundary_violation,
        "runtime_approval_gate_findings": sorted(set(findings)),
        "missing_evidence": sorted(set(missing_evidence)),
        "review_required": failed,
        "escalation_required": authority_boundary_violation,
        "fail_closed_recommended": authority_boundary_violation,
    }



def _evaluate_fixture_expectations(
    fixtures: dict[str, dict[str, Any]],
    findings: list[str],
    missing_evidence: list[str],
) -> None:
    valid_fixture = _as_dict(fixtures.get("valid_halt_approval_release_execution_trace"))
    valid_result = evaluate_approval_gate_trace(_as_dict(valid_fixture.get("trace")))
    if not valid_result["enforced_gate_trace_valid"]:
        findings.append("valid_enforced_trace_failed")
        missing_evidence.append("valid_halt_approval_release_execution_trace")

    observed_fixture = _as_dict(fixtures.get("observed_only_trace"))
    observed_result = evaluate_approval_gate_trace(_as_dict(observed_fixture.get("trace")))
    if not observed_result["observed_trace_valid"] or observed_result["enforcement_satisfied"]:
        findings.append("observed_only_trace_boundary_failed")
        missing_evidence.append("observed_only_trace")

    for fixture_id in ["post_facto_advisory_approval", "approval_state_only_trace"]:
        fixture = _as_dict(fixtures.get(fixture_id))
        if fixture.get("negative_fixture") is not True:
            findings.append(f"{fixture_id}_not_marked_negative")
            missing_evidence.append(fixture_id)
        trace_result = evaluate_approval_gate_trace(_as_dict(fixture.get("trace")))
        if trace_result["approval_gate_trace_valid"]:
            findings.append(f"{fixture_id}_unexpectedly_passed")
            missing_evidence.append(fixture_id)



def _gate_event_bound_to_tool_call(trace: dict[str, Any]) -> bool:
    gate_event = _as_dict(trace.get("gate_event"))
    if not all(
        [
            _has_value(trace, "gate_event_id"),
            _has_value(trace, "blocked_tool_call_id"),
            _has_value(gate_event, "event_id"),
            _has_value(gate_event, "blocked_tool_call_id"),
        ]
    ):
        return False
    return (
        gate_event.get("event_id") == trace.get("gate_event_id")
        and gate_event.get("blocked_tool_call_id") == trace.get("blocked_tool_call_id")
    )



def _approval_bound_to_tool_call(trace: dict[str, Any]) -> bool:
    binding = _as_dict(trace.get("approval_binding"))
    if not all(
        [
            _has_value(trace, "approval_event_id"),
            _has_value(trace, "blocked_tool_call_id"),
            _has_value(binding, "approval_event_id"),
            _has_value(binding, "blocked_tool_call_id"),
        ]
    ):
        return False
    return (
        binding.get("approval_event_id") == trace.get("approval_event_id")
        and binding.get("blocked_tool_call_id") == trace.get("blocked_tool_call_id")
    )



def _gate_event_before_execution(trace: dict[str, Any]) -> bool:
    gate_event = _as_dict(trace.get("gate_event"))
    return (
        _before_or_equal(trace.get("tool_call_requested_at"), gate_event.get("occurred_at"))
        and _before_or_equal(gate_event.get("occurred_at"), trace.get("tool_call_released_at"))
        and _before_or_equal(gate_event.get("occurred_at"), trace.get("tool_call_executed_at"))
    )



def _approval_before_release_and_execution(trace: dict[str, Any]) -> bool:
    return (
        _before_or_equal(trace.get("tool_call_requested_at"), trace.get("approval_timestamp"))
        and _before_or_equal(trace.get("approval_timestamp"), trace.get("tool_call_released_at"))
        and _before_or_equal(trace.get("tool_call_released_at"), trace.get("tool_call_executed_at"))
    )



def _post_facto_approval(trace: dict[str, Any]) -> bool:
    return _after(trace.get("approval_timestamp"), trace.get("tool_call_executed_at"))



def _has_enforced_claim(trace: dict[str, Any]) -> bool:
    return trace.get("satisfies_enforced_approval") is True or trace.get("enforcement_claimed") is True



def _authority_boundary_complete(artifact: dict[str, Any]) -> bool:
    boundary = _as_dict(artifact.get("authority_boundary"))
    return (
        REQUIRED_AUTHORITY_MAY <= _as_set(boundary.get("may"))
        and REQUIRED_AUTHORITY_MUST_NOT <= _as_set(boundary.get("must_not"))
    )



def _required_boundary_language_present(artifact: dict[str, Any]) -> bool:
    boundary_language = " ".join(
        [
            str(artifact.get("governance_boundary_statement", "")),
            str(artifact.get("decision_proof_sealing_boundary_statement", "")),
            str(artifact.get("aaos_retained_authority_statement", "")),
            str(artifact.get("sovereignty_statement", "")),
        ]
    ).lower()
    return all(
        phrase in boundary_language
        for phrase in [
            "runtime approval evidence may prove whether a gate observed, advised, or enforced approval",
            "must not itself approve execution",
            "decision proof sealing remains aaos-owned",
            "aaos retains",
            "aaos remains the decision sovereignty layer",
        ]
    )



def _completed_milestone_reopen_claim(artifact: dict[str, Any]) -> bool:
    status_text = " ".join(
        [
            str(artifact.get("m11_status_boundary", "")),
            str(artifact.get("m12_status_boundary", "")),
        ]
    ).lower()
    if "reopen" in status_text and "not reopened" not in status_text:
        return True
    return any("m11 reopened" in text or "m12 reopened" in text for text in _iter_claim_text(artifact))
