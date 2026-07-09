"""Deterministic checks for M13 release proof linkage evidence."""

from __future__ import annotations

from typing import Any


REQUIRED_SPECIMEN_FIELDS = {
    "artifact_id": "missing_artifact_id",
    "artifact_name": "missing_artifact_name",
    "artifact_scope": "missing_artifact_scope",
    "artifact_status": "missing_artifact_status",
    "m13_completion_status": "missing_m13_completion_status",
    "related_issue": "missing_related_issue_176",
    "tracker_issue_closure_state": "missing_tracker_issue_176_open_state",
    "tracker_issue_linkage": "missing_tracker_issue_176_reference",
    "runtime_approval_gate_evidence_pr": "missing_runtime_approval_gate_evidence_pr_177",
    "registry_drift_detection_pr": "missing_registry_drift_detection_pr_178",
    "authority_boundary_regression_fixtures_pr": "missing_authority_boundary_regression_fixtures_pr_194",
    "operational_readiness_checklist_pr": "missing_operational_readiness_checklist_pr_195",
    "external_consumer_onboarding_documentation_pr": "missing_external_consumer_onboarding_documentation_pr_196",
    "introduced_after_release": "missing_introduced_after_release_v0_11_0",
    "target_future_release": "missing_target_future_release_v0_12_0",
    "prior_released_baseline": "missing_prior_released_baseline_v0_11_0",
    "future_release_tag_path": "missing_future_release_tag_path",
    "release_status": "missing_release_status",
    "release_status_path": "missing_release_status_path",
    "release_approval": "missing_release_approval_boundary",
    "release_created": "missing_release_created_boundary",
    "release_tag_created": "missing_release_tag_created_boundary",
    "release_notes_finalized": "missing_release_notes_finalized_boundary",
    "m13_complete": "missing_m13_complete_boundary",
    "decision_proof_sealed": "missing_decision_proof_sealed_boundary",
    "release_readiness_status": "missing_release_readiness_status",
    "release_ready_for_review": "missing_release_ready_for_review_boundary",
    "release_proof_complete": "missing_release_proof_complete_boundary",
    "released": "missing_released_boundary",
    "release_linkage_refs": "missing_release_linkage_refs",
    "artifact_links": "missing_artifact_links",
    "deterministic_evaluator_references": "missing_deterministic_evaluator_references",
    "test_references": "missing_test_references",
    "required_boundary_statements": "missing_required_boundary_statements",
    "semantic_boundaries": "missing_semantic_boundaries",
    "allowed_evaluator_outputs": "missing_allowed_evaluator_outputs",
    "forbidden_evaluator_outputs": "missing_forbidden_evaluator_outputs",
    "authority_boundary": "missing_authority_boundary",
    "governance_boundary_statement": "missing_governance_boundary_statement",
    "decision_proof_sealing_boundary_statement": "missing_decision_proof_sealing_boundary_statement",
    "aaos_retained_authority_statement": "missing_aaos_retained_authority_statement",
    "sovereignty_statement": "missing_sovereignty_statement",
}

EXPECTED_PR_REFS = {
    "runtime_approval_gate_evidence_pr": "#177",
    "registry_drift_detection_pr": "#178",
    "authority_boundary_regression_fixtures_pr": "#194",
    "operational_readiness_checklist_pr": "#195",
    "external_consumer_onboarding_documentation_pr": "#196",
}

REQUIRED_LINKAGE_REFS = {
    "m13_tracker_issue": "#176",
    "runtime_enforced_approval_evidence_pr": "#177",
    "registry_drift_detection_pr": "#178",
    "authority_boundary_regression_fixtures_pr": "#194",
    "operational_readiness_checklist_pr": "#195",
    "external_consumer_onboarding_documentation_pr": "#196",
    "prior_released_baseline": "v0.11.0",
    "future_target_release": "v0.12.0",
}

REQUIRED_ARTIFACT_LINKS = {
    "runtime_enforced_approval_evidence",
    "registry_drift_detection",
    "authority_boundary_regression_fixtures",
    "operational_readiness_checklist",
    "external_consumer_onboarding_fixtures",
    "external_consumer_onboarding_documentation",
}

REQUIRED_BOUNDARY_STATEMENTS = {
    "release proof linkage is evidence linkage only.",
    "release proof linkage is not release approval.",
    "future release target is not released.",
    "v0.12.0 is not released.",
    "m13 is active work and not complete.",
    "readme status path is future-only and not completion.",
    "release notes draft path is not release publication.",
    "release_ready_for_review is not release_approved.",
    "release_proof_complete is not released.",
    "evidence_complete is not sealed.",
    "replay_ready is not sealed.",
    "decision proof sealing remains aaos-owned.",
    "aaos remains the decision sovereignty layer.",
    "this specimen must not close #176.",
}

REQUIRED_ALLOWED_OUTPUTS = {
    "release_proof_linkage_valid",
    "release_proof_linkage_invalid",
    "release_linkage_coverage_complete",
    "release_linkage_coverage_incomplete",
    "release_ready_for_review",
    "release_not_ready",
    "review_required",
    "escalation_required",
    "fail_closed_recommended",
}

FORBIDDEN_EVALUATOR_OUTPUTS = {
    "release_approved",
    "release_created",
    "release_tag_created",
    "release_notes_published",
    "v0_12_0_released",
    "m13_complete",
    "decision_proof_sealed",
    "sealed_by_release_proof",
    "risk_accepted",
    "audit_closed",
    "waiver_granted",
    "final_governance_judgment",
    "authority_transferred",
    "closes_176",
}

REQUIRED_AUTHORITY_MAY = {
    "link_artifacts",
    "report_coverage",
    "surface_review_required",
    "surface_escalation_required",
    "surface_fail_closed_recommended",
    "reference_evidence",
    "inspect_evidence",
    "check_evidence",
}

REQUIRED_AUTHORITY_MUST_NOT = {
    "approve_releases",
    "create_releases",
    "create_tags",
    "publish_release_notes",
    "accept_risk",
    "seal_decision_proof",
    "close_audits",
    "grant_waivers",
    "transfer_authority",
    "declare_m13_complete",
    "declare_v0_12_0_released",
    "make_final_governance_judgments",
    "close_tracker_issue_176",
}

BOUNDARY_CLAIM_FINDINGS = {
    "release proof linkage is release approval": "release_proof_release_approval_claim_detected",
    "release_ready_for_review is release_approved": "release_ready_for_review_approval_claim_detected",
    "release_proof_complete is released": "release_proof_complete_released_claim_detected",
    "evidence_complete is sealed": "evidence_complete_sealed_claim_detected",
    "replay_ready is sealed": "replay_ready_sealed_claim_detected",
    "release notes draft path is release publication": "release_notes_draft_publication_claim_detected",
    "readme status path is completion": "readme_status_completion_claim_detected",
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

SAFE_TRACKER_BOUNDARY_PHRASES = {
    "must not close #176",
    "not close #176",
    "must not close tracker issue 176",
    "close_tracker_issue_176",
}

SAFE_CONTEXT_KEYS = {
    "allowed_evaluator_outputs",
    "forbidden_evaluator_outputs",
    "authority_boundary",
    "must_not",
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
        return True
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



def detect_release_proof_forbidden_claims(value: Any, parent_key: str | None = None) -> set[str]:
    claims: set[str] = set()

    if parent_key in SAFE_CONTEXT_KEYS:
        return claims

    if isinstance(value, dict):
        for key, item in value.items():
            claims.update(detect_release_proof_forbidden_claims(item, str(key)))
        return claims

    if isinstance(value, list):
        for item in value:
            claims.update(detect_release_proof_forbidden_claims(item, parent_key))
        return claims

    normalized = _text(value)
    if normalized in FORBIDDEN_EVALUATOR_OUTPUTS:
        claims.add(normalized)
    for phrase in BOUNDARY_CLAIM_FINDINGS:
        if phrase in normalized:
            claims.add(phrase)
    return claims



def evaluate_m13_release_proof_linkage(specimen: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    boundary_violation = False
    not_ready = False

    def add_missing(finding: str, evidence: str) -> None:
        findings.append(finding)
        missing_evidence.append(evidence)

    if not specimen:
        add_missing("release_proof_linkage_specimen_missing", "specimen")

    for field, finding in REQUIRED_SPECIMEN_FIELDS.items():
        if not _has_value(specimen, field):
            add_missing(finding, field)

    if specimen.get("artifact_status") != "active_work_in_progress_not_released":
        add_missing("artifact_status_not_active_work_in_progress", "artifact_status")
    if specimen.get("m13_completion_status") != "active_work_not_complete":
        add_missing("m13_completion_status_not_active_work", "m13_completion_status")
    if specimen.get("related_issue") != "#176":
        add_missing("missing_related_issue_176", "related_issue")
    if specimen.get("introduced_after_release") != "v0.11.0":
        add_missing("missing_prior_released_baseline_v0_11_0", "introduced_after_release")
    if specimen.get("target_future_release") != "v0.12.0":
        add_missing("missing_target_future_release_v0_12_0", "target_future_release")

    for field, expected in EXPECTED_PR_REFS.items():
        if specimen.get(field) != expected:
            add_missing(f"missing_{field}", field)

    tracker_state = _text(specimen.get("tracker_issue_closure_state"))
    if "open" not in tracker_state or tracker_state == "closed":
        findings.append("tracker_issue_176_not_marked_open")
        missing_evidence.append("tracker_issue_closure_state")
        boundary_violation = True
    if specimen.get("tracker_issue_linkage") != "Refs #176":
        add_missing("tracker_issue_linkage_not_refs_only", "tracker_issue_linkage")
    if _has_tracker_176_closure_claim(specimen):
        findings.append("tracker_issue_176_closure_claim_detected")
        boundary_violation = True

    release_status_future_only = _release_status_future_only(specimen)
    if not release_status_future_only:
        add_missing("release_status_future_only_missing", "release_status_path")

    if specimen.get("release_approval") is True:
        findings.append("release_approval_claim_detected")
        boundary_violation = True
    if specimen.get("release_created") is True:
        findings.append("release_created_claim_detected")
        boundary_violation = True
    if specimen.get("release_tag_created") is True:
        findings.append("release_tag_created_claim_detected")
        boundary_violation = True
    if specimen.get("release_notes_finalized") is True:
        findings.append("release_notes_finalized_claim_detected")
        boundary_violation = True
    if specimen.get("release_notes_published") is True:
        findings.append("release_notes_published_claim_detected")
        boundary_violation = True
    if specimen.get("m13_complete") is True:
        findings.append("m13_completion_claim_detected")
        boundary_violation = True
    if specimen.get("decision_proof_sealed") is True:
        findings.append("decision_proof_sealing_claim_detected")
        boundary_violation = True
    if specimen.get("released") is True:
        findings.append("release_created_claim_detected")
        boundary_violation = True

    if _has_v0_12_0_release_claim(specimen):
        findings.append("v0_12_0_release_claim_detected")
        boundary_violation = True
    if _has_m13_completion_claim(specimen):
        findings.append("m13_completion_claim_detected")
        boundary_violation = True

    linkage_coverage_complete = _release_linkage_coverage_complete(specimen)
    if not linkage_coverage_complete:
        add_missing("release_linkage_coverage_incomplete", "release_linkage_refs")
        not_ready = True

    if not REQUIRED_ARTIFACT_LINKS <= set(_as_dict(specimen.get("artifact_links"))):
        add_missing("artifact_link_coverage_incomplete", "artifact_links")
        not_ready = True

    boundary_statements = {
        statement.lower() for statement in _as_set(specimen.get("required_boundary_statements"))
    }
    if not REQUIRED_BOUNDARY_STATEMENTS <= boundary_statements:
        add_missing("required_boundary_statements_incomplete", "required_boundary_statements")
        not_ready = True

    if not REQUIRED_ALLOWED_OUTPUTS <= _as_set(specimen.get("allowed_evaluator_outputs")):
        add_missing("allowed_evaluator_outputs_missing", "allowed_evaluator_outputs")
    if not FORBIDDEN_EVALUATOR_OUTPUTS <= _as_set(specimen.get("forbidden_evaluator_outputs")):
        add_missing("forbidden_evaluator_outputs_missing", "forbidden_evaluator_outputs")

    if not _authority_boundary_complete(specimen):
        add_missing("authority_boundary_statement_incomplete", "authority_boundary")

    boundary_language = _boundary_language(specimen)
    if not _required_boundary_language_present(boundary_language):
        add_missing("missing_aaos_release_proof_boundary_statement", "aaos_retained_authority_statement")
    for phrase, finding in BOUNDARY_CLAIM_FINDINGS.items():
        if phrase in boundary_language:
            findings.append(finding)
            boundary_violation = True

    forbidden_claims = detect_release_proof_forbidden_claims(specimen)
    if forbidden_claims:
        findings.append("authority_transfer_claim_detected")
        boundary_violation = True

    if specimen.get("release_readiness_status") != "release_ready_for_review_not_approved":
        add_missing("release_readiness_status_not_ready_for_review_not_approved", "release_readiness_status")
        not_ready = True
    if specimen.get("release_ready_for_review") is not True:
        add_missing("release_ready_for_review_missing", "release_ready_for_review")
        not_ready = True
    if specimen.get("release_proof_complete") is not True:
        add_missing("release_proof_complete_missing", "release_proof_complete")
        not_ready = True

    return _release_proof_result(
        findings=findings,
        missing_evidence=missing_evidence,
        boundary_violation=boundary_violation,
        release_linkage_coverage_complete=linkage_coverage_complete,
        release_status_future_only=release_status_future_only,
        not_ready=not_ready,
    )



def _release_linkage_coverage_complete(specimen: dict[str, Any]) -> bool:
    refs = _as_dict(specimen.get("release_linkage_refs"))
    return all(refs.get(field) == expected for field, expected in REQUIRED_LINKAGE_REFS.items())



def _release_status_future_only(specimen: dict[str, Any]) -> bool:
    release_status = _as_dict(specimen.get("release_status_path"))
    future_tag = _as_dict(specimen.get("future_release_tag_path"))
    prior_baseline = _as_dict(specimen.get("prior_released_baseline"))
    return (
        specimen.get("introduced_after_release") == "v0.11.0"
        and prior_baseline.get("release_tag") == "v0.11.0"
        and prior_baseline.get("status") == "prior_released_baseline"
        and specimen.get("target_future_release") == "v0.12.0"
        and specimen.get("release_status") == "future_target_release_only"
        and release_status.get("state") == "future_target_release_only"
        and release_status.get("release_approval") is False
        and release_status.get("release_created") is False
        and release_status.get("release_tag_created") is False
        and release_status.get("release_notes_finalized") is False
        and release_status.get("release_notes_published") is False
        and future_tag.get("target_tag") == "v0.12.0"
        and future_tag.get("state") == "future_tag_path_only"
        and future_tag.get("released") is False
        and specimen.get("release_approval") is False
        and specimen.get("release_created") is False
        and specimen.get("release_tag_created") is False
        and specimen.get("release_notes_finalized") is False
        and specimen.get("release_notes_published") is False
        and specimen.get("m13_complete") is False
        and specimen.get("decision_proof_sealed") is False
        and specimen.get("released") is False
        and not _has_v0_12_0_release_claim(specimen)
    )



def _authority_boundary_complete(specimen: dict[str, Any]) -> bool:
    boundary = _as_dict(specimen.get("authority_boundary"))
    return (
        REQUIRED_AUTHORITY_MAY <= _as_set(boundary.get("may"))
        and REQUIRED_AUTHORITY_MUST_NOT <= _as_set(boundary.get("must_not"))
    )



def _boundary_language(specimen: dict[str, Any]) -> str:
    segments = [
        str(specimen.get("governance_boundary_statement", "")),
        str(specimen.get("decision_proof_sealing_boundary_statement", "")),
        str(specimen.get("aaos_retained_authority_statement", "")),
        str(specimen.get("sovereignty_statement", "")),
    ]
    segments.extend(str(value) for value in _as_dict(specimen.get("semantic_boundaries")).values())
    return " ".join(segments).lower()



def _required_boundary_language_present(boundary_language: str) -> bool:
    return all(
        phrase in boundary_language
        for phrase in [
            "release proof linkage is evidence linkage only",
            "must not approve releases",
            "release proof linkage is not release approval",
            "future release target is not released",
            "v0.12.0 is not released",
            "m13 is active work and not complete",
            "readme status path is future-only and not completion",
            "release notes draft path is not release publication",
            "release_ready_for_review is not release_approved",
            "release_proof_complete is not released",
            "evidence_complete is not sealed",
            "replay_ready is not sealed",
            "decision proof sealing remains aaos-owned",
            "aaos retains",
            "aaos remains the decision sovereignty layer",
        ]
    )



def _has_tracker_176_closure_claim(specimen: dict[str, Any]) -> bool:
    for item in _iter_claim_text(specimen):
        if item == "closes_176":
            return True
        if any(safe_phrase in item for safe_phrase in SAFE_TRACKER_BOUNDARY_PHRASES):
            continue
        if any(phrase in item for phrase in TRACKER_176_CLOSURE_PHRASES):
            return True
    return False



def _has_v0_12_0_release_claim(specimen: dict[str, Any]) -> bool:
    if _as_dict(specimen.get("future_release_tag_path")).get("released") is True:
        return True
    if specimen.get("released") is True:
        return True
    for item in _iter_claim_text(specimen):
        if item == "v0_12_0_released" or "v0.12.0 is released" in item:
            return True
    return False



def _has_m13_completion_claim(specimen: dict[str, Any]) -> bool:
    if specimen.get("m13_complete") is True:
        return True
    for item in _iter_claim_text(specimen):
        if item == "m13_complete":
            return True
        if "m13 is complete" in item and "not complete" not in item:
            return True
    return False



def _release_proof_result(
    findings: list[str],
    missing_evidence: list[str],
    boundary_violation: bool,
    release_linkage_coverage_complete: bool,
    release_status_future_only: bool,
    not_ready: bool,
) -> dict[str, Any]:
    unique_findings = sorted(set(findings))
    unique_missing = sorted(set(missing_evidence))
    failed = bool(unique_findings or unique_missing or boundary_violation)
    ready_for_review = not failed and not not_ready

    return {
        "release_proof_linkage_valid": not failed,
        "release_proof_linkage_invalid": failed,
        "release_linkage_coverage_complete": release_linkage_coverage_complete,
        "release_linkage_coverage_incomplete": not release_linkage_coverage_complete,
        "release_ready_for_review": ready_for_review,
        "release_not_ready": not_ready or failed,
        "release_status_future_only": release_status_future_only,
        "release_proof_findings": unique_findings,
        "missing_evidence": unique_missing,
        "review_required": failed or not_ready,
        "escalation_required": boundary_violation,
        "fail_closed_recommended": boundary_violation,
    }
