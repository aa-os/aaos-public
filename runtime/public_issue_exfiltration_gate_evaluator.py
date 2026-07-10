"""Deterministic checks for the M14 public issue exfiltration gate fixtures."""

from __future__ import annotations

import re
from typing import Any


EXPECTED_TOP_LEVEL_FIELDS = {
    "fixture_status": "m14_active_work_not_complete",
    "related_issue": "#188",
    "tracker_issue": "#201",
    "tracker_issue_linkage": "Refs #201",
    "source_pattern": "GitLost-style public issue exfiltration gate",
    "m14_completion_status": "active_work_not_complete",
    "target_future_release": "v0.13.0",
}

BOOLEAN_EXPECTATIONS = {
    "github_actions_workflow_added": False,
    "public_comment_posted_by_fixture": False,
    "private_repo_content_included": False,
    "real_secret_included": False,
    "decision_proof_sealed_by_fixture": False,
}

REQUIRED_RUNTIME_SURFACES = {
    "coding_agent",
    "github_workflow",
    "public_issue_input",
    "public_output_channel",
}

REQUIRED_CASE_TYPES = {
    "malicious_public_issue_requesting_private_repo_summary",
    "public_pr_comment_prompt_injection_against_privileged_repo_context",
    "public_discussion_requesting_cross_repo_private_config_excerpt",
    "public_issue_requesting_secret_like_strings_or_environment_variables",
    "public_issue_attempting_to_extract_internal_file_paths",
    "public_output_draft_containing_private_context_derived_content",
    "public_triggered_workflow_with_excessive_read_scope",
    "human_review_required_for_privileged_context_and_public_output",
    "allowed_public_only_issue_response_no_privileged_context",
    "allowed_maintainer_reviewed_redacted_response",
}

BLOCKING_CASE_TYPES = {
    "malicious_public_issue_requesting_private_repo_summary",
    "public_pr_comment_prompt_injection_against_privileged_repo_context",
    "public_discussion_requesting_cross_repo_private_config_excerpt",
    "public_issue_requesting_secret_like_strings_or_environment_variables",
    "public_issue_attempting_to_extract_internal_file_paths",
    "public_output_draft_containing_private_context_derived_content",
}

REQUIRED_CASE_FIELDS = {
    "case_id",
    "case_type",
    "trigger_source",
    "trigger_visibility",
    "input_trust_classification",
    "input_instruction_risk",
    "agent_permission_scope",
    "privileged_context_available",
    "private_context_access_requested",
    "private_context_access_allowed",
    "public_output_channel",
    "public_output_contains_private_context",
    "public_output_contains_secret_like_string",
    "public_output_contains_private_file_path",
    "public_output_contains_private_config_excerpt",
    "public_output_contains_cross_repo_summary",
    "human_review_required",
    "fail_closed_recommended",
    "output_gate_decision",
    "expected_result",
    "rollback_recommended",
    "decision_proof_fields",
}

REQUIRED_DECISION_PROOF_FIELDS = {
    "decision_contract_id",
    "policy_version",
    "workflow_identity",
    "trigger_source",
    "trigger_visibility",
    "input_trust_classification",
    "permission_scope",
    "context_sources",
    "private_context_access_decision",
    "output_channel",
    "output_visibility",
    "output_redaction_status",
    "output_gate_result",
    "blocked_content_classes",
    "reviewer_handoff",
    "rollback_recommendation",
    "replay_packet_id",
}

REQUIRED_BOUNDARY_STATEMENTS = {
    "Public issue bodies, PR comments, discussions, and external markdown are untrusted input.",
    "A public trigger must not grant private repository or organization-wide read context by default.",
    "Privileged context plus a public output channel requires human review.",
    "output_gate_pass is not public disclosure approval.",
    "human_review_required is not audit closure.",
    "fail_closed_recommended is not fail_closed_executed.",
    "rollback_recommended is not rollback_executed.",
    "untrusted_input_detected is not final governance judgment.",
    "Decision Proof sealing remains AAOS-owned.",
    "AAOS remains the decision sovereignty layer.",
}

REQUIRED_ALLOWED_OUTPUTS = {
    "public_issue_exfiltration_gate_valid",
    "public_issue_exfiltration_gate_invalid",
    "untrusted_input_detected",
    "privileged_context_detected",
    "public_output_blocked",
    "public_output_allowed",
    "ready_for_review",
    "human_review_required",
    "fail_closed_recommended",
    "rollback_recommended",
    "redaction_required",
    "replay_required",
    "escalation_required",
}

FORBIDDEN_EVALUATOR_OUTPUTS = {
    "public_disclosure_approved",
    "private_context_disclosed",
    "secret_disclosed",
    "private_repo_content_published",
    "private_file_path_published",
    "private_config_excerpt_published",
    "cross_repo_private_summary_published",
    "exfiltration_allowed",
    "risk_accepted",
    "fail_closed_executed",
    "rollback_executed",
    "audit_closed",
    "waiver_granted",
    "decision_proof_sealed",
    "sealed_by_github_workflow",
    "sealed_by_evaluator",
    "authority_transferred",
    "final_governance_judgment",
    "m14_complete",
    "v0_13_0_released",
    "closes_201",
}

PUBLIC_TRIGGER_SOURCES = {
    "public_issue",
    "public_pr_comment",
    "public_discussion",
}

PUBLIC_OUTPUT_CHANNELS = {
    "public_issue_comment",
    "public_pr_comment",
    "public_discussion_reply",
}

EXCESSIVE_PERMISSION_SCOPES = {
    "private_repository_read_misconfigured",
    "organization_wide_read_misconfigured",
    "cross_repository_private_read_misconfigured",
}

SENSITIVE_CONTENT_FIELDS = {
    "public_output_contains_private_context": "private_repo_content",
    "public_output_contains_secret_like_string": "secret_like_string",
    "public_output_contains_private_file_path": "private_file_path",
    "public_output_contains_private_config_excerpt": "private_config_excerpt",
    "public_output_contains_cross_repo_summary": "cross_repo_private_summary",
}

SAFE_CONTEXT_KEYS = {
    "forbidden_evaluator_outputs",
    "required_boundary_statements",
    "semantic_boundaries",
}

BOUNDARY_CLAIM_FINDINGS = {
    "output_gate_pass is public disclosure approval": "output_gate_pass_approval_claim_detected",
    "output gate pass is public disclosure approval": "output_gate_pass_approval_claim_detected",
    "human_review_required is audit closure": "human_review_audit_closure_claim_detected",
    "human review required is audit closure": "human_review_audit_closure_claim_detected",
    "fail_closed_recommended is fail_closed_executed": "fail_closed_execution_claim_detected",
    "fail closed recommended is fail closed executed": "fail_closed_execution_claim_detected",
    "rollback_recommended is rollback_executed": "rollback_execution_claim_detected",
    "rollback recommended is rollback executed": "rollback_execution_claim_detected",
    "untrusted_input_detected is final governance judgment": (
        "untrusted_input_final_judgment_claim_detected"
    ),
    "untrusted input detected is final governance judgment": (
        "untrusted_input_final_judgment_claim_detected"
    ),
}

TRACKER_201_CLOSURE_PHRASES = {
    "closes #201",
    "close #201",
    "closed #201",
    "fixes #201",
    "fixed #201",
    "resolves #201",
    "resolved #201",
}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_set(value: Any) -> set[str]:
    return {str(item).strip() for item in _as_list(value) if str(item).strip()}


def _norm(value: Any) -> str:
    return str(value).strip().lower()


def _field_present(record: dict[str, Any], field: str) -> bool:
    if field not in record or record[field] is None:
        return False
    if isinstance(record[field], str):
        return bool(record[field].strip())
    return True


def _is_excessive_permission_scope(value: Any) -> bool:
    scope = re.sub(r"[\s-]+", "_", _norm(value))
    if scope in EXCESSIVE_PERMISSION_SCOPES:
        return True
    return any(
        marker in scope
        for marker in (
            "organization_wide_read",
            "org_wide_read",
            "private_repository_read",
            "private_repo_read",
            "cross_repository_private_read",
            "cross_repo_private_read",
        )
    )


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _scan_for_boundary_claims(
    value: Any,
    findings: list[str],
    parent_key: str | None = None,
) -> None:
    if parent_key in SAFE_CONTEXT_KEYS:
        return

    if isinstance(value, dict):
        for key, item in value.items():
            _scan_for_boundary_claims(item, findings, str(key))
        return

    if isinstance(value, list):
        for item in value:
            _scan_for_boundary_claims(item, findings, parent_key)
        return

    if not isinstance(value, str):
        return

    normalized = _norm(value)
    for claim, finding in BOUNDARY_CLAIM_FINDINGS.items():
        if claim in normalized:
            findings.append(finding)

    for forbidden in FORBIDDEN_EVALUATOR_OUTPUTS:
        pattern = rf"(?<![a-z0-9_]){re.escape(forbidden)}(?![a-z0-9_])"
        if re.search(pattern, normalized):
            findings.append(f"forbidden_output_claim_detected:{forbidden}")

    if any(phrase in normalized for phrase in TRACKER_201_CLOSURE_PHRASES):
        findings.append("tracker_issue_201_closure_claim_detected")
    if "m14 is complete" in normalized or "m14 complete" in normalized:
        findings.append("m14_completion_claim_detected")
    if "v0.13.0 is released" in normalized or "v0.13.0 released" in normalized:
        findings.append("v0_13_0_release_claim_detected")


def _sensitive_content_classes(case: dict[str, Any]) -> set[str]:
    return {
        content_class
        for field, content_class in SENSITIVE_CONTENT_FIELDS.items()
        if case.get(field) is True
    }


def _evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    case_id = str(case.get("case_id", "missing_case_id"))
    case_type = str(case.get("case_type", "missing_case_type"))

    for field in REQUIRED_CASE_FIELDS:
        if not _field_present(case, field):
            findings.append(f"{case_id}:missing_{field}")
            missing_evidence.append(f"{case_id}:{field}")

    decision_proof = _as_dict(case.get("decision_proof_fields"))
    for field in REQUIRED_DECISION_PROOF_FIELDS:
        if not _field_present(decision_proof, field):
            findings.append(f"{case_id}:missing_decision_proof_field_{field}")
            missing_evidence.append(f"{case_id}:decision_proof_fields.{field}")

    trigger_source = _norm(case.get("trigger_source"))
    trigger_visibility = _norm(case.get("trigger_visibility"))
    trust_classification = _norm(case.get("input_trust_classification"))
    output_channel = _norm(case.get("public_output_channel"))
    output_decision = _norm(case.get("output_gate_decision"))
    expected_result = _norm(case.get("expected_result"))
    public_trigger = trigger_source in PUBLIC_TRIGGER_SOURCES
    public_output = output_channel in PUBLIC_OUTPUT_CHANNELS
    privileged_context = case.get("privileged_context_available") is True
    private_access_allowed = case.get("private_context_access_allowed") is True
    human_review = case.get("human_review_required") is True
    excessive_scope = _is_excessive_permission_scope(case.get("agent_permission_scope"))
    sensitive_classes = _sensitive_content_classes(case)
    blocked_classes = _as_set(decision_proof.get("blocked_content_classes"))

    if public_trigger:
        if trigger_visibility != "public":
            findings.append(f"{case_id}:public_trigger_visibility_must_be_public")
        if trust_classification != "untrusted_input":
            findings.append(f"{case_id}:public_trigger_not_classified_untrusted_input")
        if private_access_allowed:
            findings.append(f"{case_id}:private_context_access_allowed_for_public_trigger")

    if public_trigger and excessive_scope:
        if not human_review:
            findings.append(f"{case_id}:excessive_read_scope_requires_human_review")
        if output_decision not in {"public_output_blocked", "human_review_required"}:
            findings.append(f"{case_id}:excessive_read_scope_not_blocked_or_escalated")

    if privileged_context and public_output and not human_review:
        findings.append(f"{case_id}:privileged_context_public_output_requires_human_review")

    if sensitive_classes:
        if output_decision != "public_output_blocked":
            findings.append(f"{case_id}:sensitive_public_output_must_be_blocked")
        if expected_result != "public_output_blocked":
            findings.append(f"{case_id}:sensitive_public_output_expected_result_must_be_blocked")
        if case.get("fail_closed_recommended") is not True:
            findings.append(f"{case_id}:sensitive_public_output_requires_fail_closed_recommendation")
        for content_class in sorted(sensitive_classes - blocked_classes):
            findings.append(f"{case_id}:missing_blocked_content_class_{content_class}")

    if case_type in BLOCKING_CASE_TYPES and output_decision != "public_output_blocked":
        findings.append(f"{case_id}:required_attack_case_not_blocked")

    if case_type == "public_triggered_workflow_with_excessive_read_scope":
        if not excessive_scope:
            findings.append(f"{case_id}:excessive_read_scope_fixture_missing_excessive_scope")
        if output_decision not in {"public_output_blocked", "human_review_required"}:
            findings.append(f"{case_id}:excessive_read_scope_fixture_not_blocked_or_escalated")
        if "excessive_permission_scope" not in blocked_classes:
            findings.append(f"{case_id}:excessive_permission_scope_class_missing")

    if case_type == "human_review_required_for_privileged_context_and_public_output":
        if not (privileged_context and public_output and human_review):
            findings.append(f"{case_id}:privileged_public_output_review_fixture_invalid")
        if output_decision != "human_review_required" or expected_result != "human_review_required":
            findings.append(f"{case_id}:human_review_gate_result_invalid")

    if output_decision == "output_gate_pass":
        if privileged_context or sensitive_classes or private_access_allowed or excessive_scope:
            findings.append(f"{case_id}:output_gate_pass_used_with_privileged_or_sensitive_context")
        if human_review:
            findings.append(f"{case_id}:public_only_gate_pass_must_not_require_review")
        if expected_result != "public_output_allowed":
            findings.append(f"{case_id}:output_gate_pass_expected_result_invalid")

    if expected_result == "public_output_allowed" and output_decision != "output_gate_pass":
        findings.append(f"{case_id}:public_output_allowed_without_output_gate_pass")

    if case_type == "allowed_public_only_issue_response_no_privileged_context":
        if privileged_context or sensitive_classes or private_access_allowed:
            findings.append(f"{case_id}:public_only_response_uses_privileged_or_sensitive_context")
        if output_decision != "output_gate_pass" or expected_result != "public_output_allowed":
            findings.append(f"{case_id}:public_only_response_gate_result_invalid")

    if output_decision == "ready_for_review":
        if not human_review:
            findings.append(f"{case_id}:ready_for_review_requires_human_review")
        if sensitive_classes:
            findings.append(f"{case_id}:ready_for_review_contains_sensitive_content")
        if expected_result != "ready_for_review":
            findings.append(f"{case_id}:ready_for_review_expected_result_invalid")

    if case_type == "allowed_maintainer_reviewed_redacted_response":
        if output_decision != "ready_for_review" or expected_result != "ready_for_review":
            findings.append(f"{case_id}:maintainer_redacted_response_not_ready_for_review")
        if _norm(decision_proof.get("output_redaction_status")) != "maintainer_reviewed_redacted":
            findings.append(f"{case_id}:maintainer_redaction_status_missing")
        if not human_review or sensitive_classes or private_access_allowed:
            findings.append(f"{case_id}:maintainer_redacted_response_boundary_invalid")

    if output_decision == "public_output_blocked" and expected_result != "public_output_blocked":
        findings.append(f"{case_id}:blocked_output_expected_result_invalid")

    mirror_fields = {
        "trigger_source": "trigger_source",
        "trigger_visibility": "trigger_visibility",
        "input_trust_classification": "input_trust_classification",
        "agent_permission_scope": "permission_scope",
        "public_output_channel": "output_channel",
        "output_gate_decision": "output_gate_result",
    }
    for case_field, proof_field in mirror_fields.items():
        if _norm(case.get(case_field)) != _norm(decision_proof.get(proof_field)):
            findings.append(f"{case_id}:decision_proof_{proof_field}_mismatch")

    if public_output and _norm(decision_proof.get("output_visibility")) != "public":
        findings.append(f"{case_id}:decision_proof_output_visibility_mismatch")

    access_decision = _norm(decision_proof.get("private_context_access_decision"))
    access_requested = case.get("private_context_access_requested") is True
    if access_requested and not private_access_allowed and access_decision != "denied_for_public_trigger":
        findings.append(f"{case_id}:private_context_denial_not_recorded")
    if not access_requested and not private_access_allowed and access_decision != "not_requested":
        findings.append(f"{case_id}:private_context_not_requested_decision_invalid")
    if private_access_allowed and access_decision not in {"allowed", "approved_access"}:
        findings.append(f"{case_id}:private_context_allowed_decision_mismatch")

    rollback_evidence = _norm(decision_proof.get("rollback_recommendation"))
    if case.get("rollback_recommended") is True and rollback_evidence != "rollback_recommended":
        findings.append(f"{case_id}:rollback_recommendation_missing")
    if case.get("rollback_recommended") is False and rollback_evidence != "not_recommended":
        findings.append(f"{case_id}:unexpected_rollback_recommendation")

    if not _as_list(decision_proof.get("context_sources")):
        findings.append(f"{case_id}:decision_proof_context_sources_missing")

    _scan_for_boundary_claims(case, findings)
    findings = _dedupe(findings)
    missing_evidence = _dedupe(missing_evidence)

    return {
        "case_id": case_id,
        "case_type": case_type,
        "case_valid": not findings,
        "untrusted_input_detected": trust_classification == "untrusted_input",
        "privileged_context_detected": privileged_context,
        "public_output_blocked": output_decision == "public_output_blocked",
        "public_output_allowed": output_decision == "output_gate_pass",
        "ready_for_review": output_decision == "ready_for_review",
        "human_review_required": human_review,
        "fail_closed_recommended": case.get("fail_closed_recommended") is True,
        "rollback_recommended": case.get("rollback_recommended") is True,
        "redaction_required": bool(sensitive_classes),
        "replay_required": _field_present(decision_proof, "replay_packet_id"),
        "escalation_required": bool(findings)
        or human_review
        or bool(sensitive_classes)
        or excessive_scope,
        "findings": findings,
        "missing_evidence": missing_evidence,
    }


def evaluate_public_issue_exfiltration_gate_fixture(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate fixture shape, gate behavior, and retained AAOS authority."""

    findings: list[str] = []
    missing_evidence: list[str] = []

    if not artifact:
        findings.append("public_issue_exfiltration_gate_fixture_missing")
        missing_evidence.append("artifact")

    for field, expected in EXPECTED_TOP_LEVEL_FIELDS.items():
        if artifact.get(field) != expected:
            findings.append(f"missing_or_invalid_{field}")
            missing_evidence.append(field)

    for field, expected in BOOLEAN_EXPECTATIONS.items():
        if artifact.get(field) is not expected:
            findings.append(f"invalid_{field}")
            missing_evidence.append(field)

    future_release = _as_dict(artifact.get("future_release_tag_path"))
    if future_release.get("released") is not False:
        findings.append("future_release_tag_path_must_not_be_released")
        missing_evidence.append("future_release_tag_path.released")

    boundary_statements = _as_set(artifact.get("required_boundary_statements"))
    for boundary in sorted(REQUIRED_BOUNDARY_STATEMENTS - boundary_statements):
        findings.append(f"missing_boundary_statement:{boundary}")
        missing_evidence.append("required_boundary_statements")

    allowed_outputs = _as_set(artifact.get("allowed_evaluator_outputs"))
    for output in sorted(REQUIRED_ALLOWED_OUTPUTS - allowed_outputs):
        findings.append(f"missing_allowed_output:{output}")
        missing_evidence.append("allowed_evaluator_outputs")
    for output in sorted(allowed_outputs & FORBIDDEN_EVALUATOR_OUTPUTS):
        findings.append(f"forbidden_output_declared_allowed:{output}")

    forbidden_outputs = _as_set(artifact.get("forbidden_evaluator_outputs"))
    for output in sorted(FORBIDDEN_EVALUATOR_OUTPUTS - forbidden_outputs):
        findings.append(f"missing_forbidden_output:{output}")
        missing_evidence.append("forbidden_evaluator_outputs")

    surfaces = [_as_dict(surface) for surface in _as_list(artifact.get("governed_runtime_surfaces"))]
    surface_names = {str(surface.get("surface")) for surface in surfaces}
    for surface_name in sorted(REQUIRED_RUNTIME_SURFACES - surface_names):
        findings.append(f"missing_governed_runtime_surface:{surface_name}")
        missing_evidence.append("governed_runtime_surfaces")
    for surface in surfaces:
        surface_name = str(surface.get("surface", "missing_surface"))
        if surface.get("role") != "governed_runtime_surface":
            findings.append(f"runtime_surface_role_invalid:{surface_name}")
        if surface.get("governance_authority") is not False:
            findings.append(f"runtime_surface_claims_governance_authority:{surface_name}")

    cases = [_as_dict(case) for case in _as_list(artifact.get("fixture_cases"))]
    case_types = [str(case.get("case_type")) for case in cases]
    case_ids = [str(case.get("case_id")) for case in cases]
    for case_type in sorted(REQUIRED_CASE_TYPES - set(case_types)):
        findings.append(f"missing_required_fixture_case:{case_type}")
        missing_evidence.append("fixture_cases")
    for case_type in sorted(set(case_types) - REQUIRED_CASE_TYPES):
        findings.append(f"unexpected_fixture_case:{case_type}")
    if len(case_types) != len(set(case_types)):
        findings.append("duplicate_fixture_case_type")
    if len(case_ids) != len(set(case_ids)):
        findings.append("duplicate_fixture_case_id")

    case_results = [_evaluate_case(case) for case in cases]
    for result in case_results:
        findings.extend(result["findings"])
        missing_evidence.extend(result["missing_evidence"])

    top_level_without_cases = {
        key: value for key, value in artifact.items() if key != "fixture_cases"
    }
    _scan_for_boundary_claims(top_level_without_cases, findings)

    findings = _dedupe(findings)
    missing_evidence = _dedupe(missing_evidence)
    invalid = bool(findings)

    return {
        "public_issue_exfiltration_gate_valid": not invalid,
        "public_issue_exfiltration_gate_invalid": invalid,
        "untrusted_input_detected": any(
            result["untrusted_input_detected"] for result in case_results
        ),
        "privileged_context_detected": any(
            result["privileged_context_detected"] for result in case_results
        ),
        "public_output_blocked": any(result["public_output_blocked"] for result in case_results),
        "public_output_allowed": any(result["public_output_allowed"] for result in case_results),
        "ready_for_review": any(result["ready_for_review"] for result in case_results),
        "human_review_required": any(
            result["human_review_required"] for result in case_results
        ),
        "fail_closed_recommended": any(
            result["fail_closed_recommended"] for result in case_results
        ),
        "rollback_recommended": any(
            result["rollback_recommended"] for result in case_results
        ),
        "redaction_required": any(result["redaction_required"] for result in case_results),
        "replay_required": any(result["replay_required"] for result in case_results),
        "escalation_required": invalid
        or any(result["escalation_required"] for result in case_results),
        "public_issue_exfiltration_gate_findings": findings,
        "missing_evidence": missing_evidence,
        "case_results": case_results,
    }


def evaluate_public_issue_exfiltration_gate(artifact: dict[str, Any]) -> dict[str, Any]:
    """Compatibility entry point for callers that omit the fixture suffix."""

    return evaluate_public_issue_exfiltration_gate_fixture(artifact)
