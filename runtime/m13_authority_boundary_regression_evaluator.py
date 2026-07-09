"""Deterministic checks for M13 authority-boundary regression fixtures."""

from __future__ import annotations

from typing import Any


REQUIRED_FIXTURE_SET_FIELDS = {
    "fixture_set_id": "missing_fixture_set_id",
    "fixture_set_name": "missing_fixture_set_name",
    "fixture_set_scope": "missing_fixture_set_scope",
    "artifact_status": "missing_artifact_status",
    "m13_completion_status": "missing_m13_completion_status",
    "related_issue": "missing_related_issue_176",
    "tracker_issue_closure_state": "missing_tracker_issue_176_open_state",
    "tracker_issue_linkage": "missing_tracker_issue_176_reference",
    "runtime_approval_gate_evidence_pr": "missing_runtime_approval_gate_evidence_pr_177",
    "registry_drift_detection_pr": "missing_registry_drift_detection_pr_178",
    "closed_runtime_approval_follow_up": "missing_closed_runtime_approval_follow_up_171",
    "closed_runtime_approval_follow_up_state": "missing_closed_runtime_approval_follow_up_state",
    "introduced_after_release": "missing_introduced_after_release_v0_11_0",
    "target_future_release": "missing_target_future_release_v0_12_0",
    "future_release_tag_path": "missing_future_release_tag_path",
    "release_status_path": "missing_release_status_path",
    "m12_reference_artifacts": "missing_m12_reference_artifacts",
    "m13_reference_artifacts": "missing_m13_reference_artifacts",
    "authority_boundary_scope_statement": "missing_authority_boundary_scope_statement",
    "authority_domains": "missing_authority_domains",
    "positive_authority_boundary_fixtures": "missing_positive_authority_boundary_fixtures",
    "negative_regression_fixtures": "missing_negative_regression_fixtures",
    "semantic_boundaries": "missing_semantic_boundaries",
    "allowed_evaluator_outputs": "missing_allowed_evaluator_outputs",
    "forbidden_evaluator_outputs": "missing_forbidden_evaluator_outputs",
    "authority_boundary": "missing_authority_boundary",
    "governance_boundary_statement": "missing_governance_boundary_statement",
    "decision_proof_sealing_boundary_statement": "missing_decision_proof_sealing_boundary_statement",
    "aaos_retained_authority_statement": "missing_aaos_retained_authority_statement",
    "sovereignty_statement": "missing_sovereignty_statement",
}

REQUIRED_M12_REFS = {
    "consumer_registry_pattern",
    "integration_ci_check_specimen",
    "cross_consumer_traceability_examples",
    "multi_consumer_sealed_nonsealed_semantics",
    "release_proof_linkage",
}

REQUIRED_M13_REFS = {
    "runtime_enforced_approval_gate_evidence",
    "registry_drift_detection_specimen",
    "runtime_approval_gate_evaluator",
    "registry_drift_evaluator",
}

REQUIRED_AUTHORITY_DOMAINS = {
    "external_consumer_registry",
    "registry_drift_detection",
    "runtime_enforced_approval_evidence",
    "integration_ci_checks",
    "cross_consumer_traceability",
    "multi_consumer_sealed_nonsealed_semantics",
    "release_proof_linkage",
    "deterministic_evaluators",
    "runtime_replay_evidence",
    "governance_ci_findings",
    "onboarding_documents",
    "readme_status_entries",
    "external_evidence_consumers",
}

REQUIRED_POSITIVE_FIXTURES = {
    "registry_drift_detection_preserves_authority",
    "runtime_enforced_approval_evidence_preserves_authority",
    "release_proof_linkage_preserves_authority",
}

REQUIRED_NEGATIVE_FIXTURES = {
    "registry_inclusion_as_approval",
    "no_drift_detected_as_approval",
    "registry_drift_detector_approves_consumer",
    "registry_drift_detector_approves_release",
    "registry_drift_detector_accepts_risk",
    "registry_drift_detector_executes_fail_closed",
    "runtime_approval_evidence_approves_execution",
    "runtime_approval_evidence_accepts_risk",
    "runtime_approval_evidence_seals_decision_proof",
    "runtime_approval_evidence_closes_audit",
    "integration_ci_pass_as_approval",
    "traceability_linkage_as_approval",
    "release_proof_linkage_as_release_approval",
    "fail_closed_recommended_as_fail_closed_executed",
    "sealing_eligible_as_sealed",
    "evidence_complete_as_sealed",
    "replay_ready_as_sealed",
    "evaluator_findings_as_sealing",
    "governance_ci_findings_as_sealing",
    "non_sealed_artifact_converted_into_sealed_artifact",
    "aaos_sealed_artifact_resealed",
    "onboarding_documentation_grants_authority",
    "readme_status_entry_grants_authority",
    "external_consumer_final_governance_authority",
    "final_governance_judgment_output",
    "audit_closed_output",
    "v0_12_0_treated_as_released",
    "m13_treated_as_complete",
    "closes_176_language",
}

REQUIRED_ALLOWED_EVALUATOR_OUTPUTS = {
    "authority_boundary_regression_fixtures_valid",
    "authority_boundary_regression_fixtures_invalid",
    "authority_domain_coverage_complete",
    "authority_domain_coverage_incomplete",
    "authority_boundary_preserved",
    "authority_boundary_violation",
    "release_status_future_only",
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
    "sealed_by_traceability",
    "sealed_by_documentation",
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
    "detect_authority_boundary_violations",
    "report_findings",
    "surface_review_required",
    "surface_escalation_required",
    "surface_fail_closed_recommended",
    "reference_evidence",
    "inspect_evidence",
    "replay_evidence",
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
    "re_seal_aaos_sealed_artifacts",
    "convert_non_sealed_artifacts_into_sealed_artifacts",
    "close_audits",
    "grant_waivers",
    "transfer_authority",
    "make_final_governance_judgments",
}

BOUNDARY_CLAIM_FINDINGS = {
    "registry inclusion is approval": "registry_inclusion_approval_claim_detected",
    "no_drift_detected is approval": "no_drift_approval_claim_detected",
    "registry drift detector approves a consumer": "registry_drift_consumer_approval_claim_detected",
    "registry drift detector approves a release": "registry_drift_release_approval_claim_detected",
    "registry drift detector accepts risk": "registry_drift_risk_acceptance_claim_detected",
    "registry drift detector executes fail-closed": "registry_drift_fail_closed_execution_claim_detected",
    "runtime approval evidence approves execution": "runtime_approval_execution_approval_claim_detected",
    "runtime approval evidence accepts risk": "runtime_approval_risk_acceptance_claim_detected",
    "runtime approval evidence seals decision proof": "runtime_approval_decision_proof_sealing_claim_detected",
    "runtime approval evidence closes audit": "runtime_approval_audit_closure_claim_detected",
    "ci pass is approval": "ci_pass_approval_claim_detected",
    "traceability linkage is approval": "traceability_linkage_approval_claim_detected",
    "release proof linkage is release approval": "release_proof_release_approval_claim_detected",
    "fail_closed_recommended is fail_closed_executed": "fail_closed_execution_claim_detected",
    "sealing_eligible is sealed": "sealing_eligibility_sealed_claim_detected",
    "evidence_complete is sealed": "evidence_complete_sealed_claim_detected",
    "replay_ready is sealed": "replay_ready_sealed_claim_detected",
    "evaluator findings are sealing": "evaluator_findings_sealing_claim_detected",
    "governance ci findings are sealing": "governance_ci_findings_sealing_claim_detected",
    "non-sealed artifact is converted into sealed artifact": "nonsealed_to_sealed_conversion_claim_detected",
    "aaos-sealed artifact is re-sealed": "aaos_sealed_reseal_claim_detected",
    "onboarding documentation grants authority": "onboarding_documentation_authority_grant_claim_detected",
    "readme status entry grants authority": "readme_status_authority_grant_claim_detected",
    "external consumer becomes final governance authority": "external_consumer_final_authority_claim_detected",
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
    "forbidden_outputs",
    "forbidden_evaluator_outputs",
    "authority_boundary",
    "must_not",
    "positive_authority_boundary_fixtures",
    "negative_regression_fixtures",
    "negative_fixture_boundary",
    "attempted_forbidden_output",
    "attempted_forbidden_outputs",
    "invalid_claim",
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
        return value
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



def detect_authority_boundary_forbidden_claims(
    value: Any, parent_key: str | None = None
) -> set[str]:
    claims: set[str] = set()

    if parent_key in SAFE_CONTEXT_KEYS:
        return claims

    if isinstance(value, dict):
        for key, item in value.items():
            claims.update(detect_authority_boundary_forbidden_claims(item, str(key)))
        return claims

    if isinstance(value, list):
        for item in value:
            claims.update(detect_authority_boundary_forbidden_claims(item, parent_key))
        return claims

    normalized = _text(value)
    if normalized in FORBIDDEN_EVALUATOR_OUTPUTS:
        claims.add(normalized)
    for phrase in BOUNDARY_CLAIM_FINDINGS:
        if phrase in normalized:
            claims.add(phrase)
    return claims



def evaluate_authority_boundary_regression_fixtures(
    fixture_set: dict[str, Any]
) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    authority_boundary_violation = False

    def add_missing(finding: str, evidence: str) -> None:
        findings.append(finding)
        missing_evidence.append(evidence)

    if not fixture_set:
        add_missing("authority_boundary_regression_fixture_set_missing", "fixture_set")

    for field, finding in REQUIRED_FIXTURE_SET_FIELDS.items():
        if not _has_value(fixture_set, field):
            add_missing(finding, field)

    if fixture_set.get("related_issue") != "#176":
        add_missing("missing_related_issue_176", "related_issue")
    if fixture_set.get("runtime_approval_gate_evidence_pr") != "#177":
        add_missing("missing_runtime_approval_gate_evidence_pr_177", "runtime_approval_gate_evidence_pr")
    if fixture_set.get("registry_drift_detection_pr") != "#178":
        add_missing("missing_registry_drift_detection_pr_178", "registry_drift_detection_pr")
    if fixture_set.get("closed_runtime_approval_follow_up") != "#171":
        add_missing("missing_closed_runtime_approval_follow_up_171", "closed_runtime_approval_follow_up")
    if fixture_set.get("closed_runtime_approval_follow_up_state") != "closed_by_177":
        add_missing("missing_closed_runtime_approval_follow_up_state", "closed_runtime_approval_follow_up_state")

    tracker_state = _text(fixture_set.get("tracker_issue_closure_state"))
    if "open" not in tracker_state or tracker_state == "closed":
        add_missing("tracker_issue_176_not_marked_open", "tracker_issue_closure_state")
    if _has_tracker_176_closure_claim(fixture_set):
        findings.append("tracker_issue_176_closure_claim_detected")
        authority_boundary_violation = True

    release_status_future_only = _release_status_future_only(fixture_set)
    if not release_status_future_only:
        add_missing("release_status_future_only_missing", "release_status_path")
    if _has_v0_12_0_release_claim(fixture_set):
        findings.append("v0_12_0_release_claim_detected")
        authority_boundary_violation = True
    if _has_m13_completion_claim(fixture_set):
        findings.append("m13_completion_claim_detected")
        authority_boundary_violation = True

    if not REQUIRED_M12_REFS <= set(_as_dict(fixture_set.get("m12_reference_artifacts"))):
        add_missing("m12_reference_artifacts_missing", "m12_reference_artifacts")
    if not REQUIRED_M13_REFS <= set(_as_dict(fixture_set.get("m13_reference_artifacts"))):
        add_missing("m13_reference_artifacts_missing", "m13_reference_artifacts")

    authority_domain_coverage_complete = REQUIRED_AUTHORITY_DOMAINS <= _as_set(
        fixture_set.get("authority_domains")
    )
    if not authority_domain_coverage_complete:
        add_missing("authority_domain_coverage_incomplete", "authority_domains")

    if not _positive_fixture_present(fixture_set, "registry_drift_detection_preserves_authority"):
        add_missing("registry_drift_positive_fixture_missing", "positive_authority_boundary_fixtures")
    if not _positive_fixture_present(fixture_set, "runtime_enforced_approval_evidence_preserves_authority"):
        add_missing("runtime_approval_positive_fixture_missing", "positive_authority_boundary_fixtures")
    if not _positive_fixture_present(fixture_set, "release_proof_linkage_preserves_authority"):
        add_missing("release_proof_linkage_positive_fixture_missing", "positive_authority_boundary_fixtures")

    if not _negative_fixture_coverage_complete(fixture_set):
        add_missing("negative_regression_fixture_coverage_incomplete", "negative_regression_fixtures")
    _evaluate_negative_fixture_marking(fixture_set, findings, missing_evidence)

    if not REQUIRED_ALLOWED_EVALUATOR_OUTPUTS <= _as_set(fixture_set.get("allowed_evaluator_outputs")):
        add_missing("allowed_evaluator_outputs_missing", "allowed_evaluator_outputs")
    if not FORBIDDEN_EVALUATOR_OUTPUTS <= _as_set(fixture_set.get("forbidden_evaluator_outputs")):
        add_missing("forbidden_evaluator_outputs_missing", "forbidden_evaluator_outputs")

    if not _authority_boundary_complete(fixture_set):
        add_missing("authority_boundary_statement_incomplete", "authority_boundary")

    boundary_language = _boundary_language(fixture_set)
    if not _required_boundary_language_present(boundary_language):
        add_missing("missing_aaos_authority_boundary_statement", "aaos_retained_authority_statement")
    for phrase, finding in BOUNDARY_CLAIM_FINDINGS.items():
        if phrase in boundary_language:
            findings.append(finding)
            authority_boundary_violation = True

    forbidden_claims = detect_authority_boundary_forbidden_claims(fixture_set)
    if forbidden_claims:
        findings.append("authority_transfer_claim_detected")
        authority_boundary_violation = True

    return _authority_boundary_result(
        findings=findings,
        missing_evidence=missing_evidence,
        authority_boundary_violation=authority_boundary_violation,
        authority_domain_coverage_complete=authority_domain_coverage_complete,
        release_status_future_only=release_status_future_only,
    )



def _positive_fixture_present(fixture_set: dict[str, Any], fixture_id: str) -> bool:
    for fixture in _as_list(fixture_set.get("positive_authority_boundary_fixtures")):
        if not isinstance(fixture, dict) or fixture.get("fixture_id") != fixture_id:
            continue
        allowed = _as_set(fixture.get("allowed_outputs"))
        forbidden = _as_set(fixture.get("forbidden_outputs"))
        return (
            fixture.get("authority_action_executed") is False
            and fixture.get("authority_boundary_preserved") is True
            and "authority_boundary_preserved" in allowed
            and not (allowed & FORBIDDEN_EVALUATOR_OUTPUTS)
            and bool(forbidden & FORBIDDEN_EVALUATOR_OUTPUTS)
        )
    return False



def _negative_fixture_coverage_complete(fixture_set: dict[str, Any]) -> bool:
    fixture_ids = {
        str(item.get("fixture_id"))
        for item in _as_list(fixture_set.get("negative_regression_fixtures"))
        if isinstance(item, dict)
    }
    return REQUIRED_NEGATIVE_FIXTURES <= fixture_ids



def _evaluate_negative_fixture_marking(
    fixture_set: dict[str, Any],
    findings: list[str],
    missing_evidence: list[str],
) -> None:
    for fixture in _as_list(fixture_set.get("negative_regression_fixtures")):
        if not isinstance(fixture, dict):
            continue
        fixture_id = str(fixture.get("fixture_id", "unknown_negative_fixture"))
        if fixture.get("negative_fixture") is not True or fixture.get("allowed_behavior") is not False:
            findings.append(f"negative_fixture_unmarked_{fixture_id}")
            missing_evidence.append(f"negative_regression_fixtures.{fixture_id}")
        if not _has_value(fixture, "negative_fixture_boundary"):
            findings.append(f"negative_fixture_boundary_missing_{fixture_id}")
            missing_evidence.append(f"negative_regression_fixtures.{fixture_id}.negative_fixture_boundary")



def _release_status_future_only(fixture_set: dict[str, Any]) -> bool:
    release_status = _as_dict(fixture_set.get("release_status_path"))
    future_tag = _as_dict(fixture_set.get("future_release_tag_path"))
    return (
        fixture_set.get("target_future_release") == "v0.12.0"
        and release_status.get("state") == "future_target_release_only"
        and future_tag.get("target_tag") == "v0.12.0"
        and future_tag.get("state") == "future_tag_path_only"
        and future_tag.get("released") is False
        and not _has_v0_12_0_release_claim(fixture_set)
    )



def _authority_boundary_complete(fixture_set: dict[str, Any]) -> bool:
    boundary = _as_dict(fixture_set.get("authority_boundary"))
    return (
        REQUIRED_AUTHORITY_MAY <= _as_set(boundary.get("may"))
        and REQUIRED_AUTHORITY_MUST_NOT <= _as_set(boundary.get("must_not"))
    )



def _boundary_language(fixture_set: dict[str, Any]) -> str:
    segments = [
        str(fixture_set.get("authority_boundary_scope_statement", "")),
        str(fixture_set.get("governance_boundary_statement", "")),
        str(fixture_set.get("decision_proof_sealing_boundary_statement", "")),
        str(fixture_set.get("aaos_retained_authority_statement", "")),
        str(fixture_set.get("sovereignty_statement", "")),
    ]
    segments.extend(str(value) for value in _as_dict(fixture_set.get("semantic_boundaries")).values())
    return " ".join(segments).lower()



def _required_boundary_language_present(boundary_language: str) -> bool:
    return all(
        phrase in boundary_language
        for phrase in [
            "authority-boundary regression fixtures are evidence checks only",
            "must not approve consumers",
            "registry inclusion is not approval",
            "no_drift_detected is not approval",
            "ci pass is not approval",
            "traceability linkage is not approval",
            "release proof linkage is not release approval",
            "runtime approval evidence is not execution approval",
            "fail_closed_recommended is not fail_closed_executed",
            "sealing_eligible is not sealed",
            "evidence_complete is not sealed",
            "replay_ready is not sealed",
            "evaluator findings are not sealing",
            "governance ci findings are not sealing",
            "non-sealed artifacts are not converted into sealed artifacts",
            "aaos-sealed artifacts are not re-sealed",
            "onboarding documentation does not grant authority",
            "readme status entries do not grant authority",
            "external consumers do not become final governance authorities",
            "decision proof sealing remains aaos-owned",
            "aaos retains",
            "aaos remains the decision sovereignty layer",
        ]
    )



def _has_tracker_176_closure_claim(fixture_set: dict[str, Any]) -> bool:
    for item in _iter_claim_text(fixture_set):
        if item == "closes_176" or any(phrase in item for phrase in TRACKER_176_CLOSURE_PHRASES):
            return True
    return False



def _has_v0_12_0_release_claim(fixture_set: dict[str, Any]) -> bool:
    if _as_dict(fixture_set.get("future_release_tag_path")).get("released") is True:
        return True
    for item in _iter_claim_text(fixture_set):
        if item == "v0_12_0_released" or "v0.12.0 is released" in item:
            return True
    return False



def _has_m13_completion_claim(fixture_set: dict[str, Any]) -> bool:
    for item in _iter_claim_text(fixture_set):
        if item == "m13_complete":
            return True
        if "m13 is complete" in item and "not complete" not in item:
            return True
    return False



def _authority_boundary_result(
    findings: list[str],
    missing_evidence: list[str],
    authority_boundary_violation: bool,
    authority_domain_coverage_complete: bool,
    release_status_future_only: bool,
) -> dict[str, Any]:
    unique_findings = sorted(set(findings))
    unique_missing = sorted(set(missing_evidence))
    failed = bool(unique_findings or unique_missing or authority_boundary_violation)

    return {
        "authority_boundary_regression_fixtures_valid": not failed,
        "authority_boundary_regression_fixtures_invalid": failed,
        "authority_domain_coverage_complete": authority_domain_coverage_complete,
        "authority_domain_coverage_incomplete": not authority_domain_coverage_complete,
        "authority_boundary_preserved": not authority_boundary_violation,
        "authority_boundary_violation": authority_boundary_violation,
        "release_status_future_only": release_status_future_only,
        "authority_boundary_findings": unique_findings,
        "missing_evidence": unique_missing,
        "review_required": failed,
        "escalation_required": authority_boundary_violation,
        "fail_closed_recommended": authority_boundary_violation,
    }
