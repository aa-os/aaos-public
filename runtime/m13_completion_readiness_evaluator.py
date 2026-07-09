"""Deterministic checks for M13 completion readiness and future README path."""

from __future__ import annotations

from typing import Any


REQUIRED_ARTIFACT_FIELDS = {
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
    "release_proof_linkage_specimen_pr": "missing_release_proof_linkage_specimen_pr_197",
    "introduced_after_release": "missing_introduced_after_release_v0_11_0",
    "target_future_release": "missing_target_future_release_v0_12_0",
    "prior_released_baseline": "missing_prior_released_baseline_v0_11_0",
    "future_release_tag_path": "missing_future_release_tag_path",
    "readme_future_status_path": "missing_readme_future_status_path",
    "readme_status_path": "missing_readme_status_path",
    "release_status": "missing_release_status",
    "release_approval": "missing_release_approval_boundary",
    "release_created": "missing_release_created_boundary",
    "release_tag_created": "missing_release_tag_created_boundary",
    "release_notes_published": "missing_release_notes_published_boundary",
    "m13_complete": "missing_m13_complete_boundary",
    "issue_176_closed": "missing_issue_176_closed_boundary",
    "decision_proof_sealed": "missing_decision_proof_sealed_boundary",
    "completion_readiness_status": "missing_completion_readiness_status",
    "completion_ready_for_review": "missing_completion_ready_for_review_boundary",
    "readme_future_path_present": "missing_readme_future_path_present_boundary",
    "release_ready_for_review": "missing_release_ready_for_review_boundary",
    "evidence_complete": "missing_evidence_complete_boundary",
    "replay_ready": "missing_replay_ready_boundary",
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
    "release_proof_linkage_specimen_pr": "#197",
}

REQUIRED_LINKAGE_REFS = {
    "m13_tracker_issue": "#176",
    "runtime_enforced_approval_evidence_pr": "#177",
    "registry_drift_detection_pr": "#178",
    "authority_boundary_regression_fixtures_pr": "#194",
    "operational_readiness_checklist_pr": "#195",
    "external_consumer_onboarding_documentation_pr": "#196",
    "release_proof_linkage_specimen_pr": "#197",
    "prior_released_baseline": "v0.11.0",
    "future_target_release": "v0.12.0",
    "readme_future_status_path": "README.md#next-phase",
}

REQUIRED_ARTIFACT_LINKS = {
    "runtime_enforced_approval_evidence",
    "registry_drift_detection",
    "authority_boundary_regression_fixtures",
    "operational_readiness_checklist",
    "external_consumer_onboarding_documentation",
    "external_consumer_onboarding_fixtures",
    "release_proof_linkage_specimen",
    "readme_future_status_path",
}

REQUIRED_BOUNDARY_STATEMENTS = {
    "completion readiness is not completion.",
    "readme future status path is not release publication.",
    "readme future status path is not m13 completion.",
    "v0.12.0 future target is not released.",
    "m13 remains active work until final completion pr.",
    "#176 remains open until final completion pr.",
    "release proof linkage is not release approval.",
    "release_ready_for_review is not release_approved.",
    "completion_ready_for_review is not m13_complete.",
    "readme_future_path_present is not released.",
    "evidence_complete is not sealed.",
    "replay_ready is not sealed.",
    "decision proof sealing remains aaos-owned.",
    "aaos remains the decision sovereignty layer.",
}

REQUIRED_ALLOWED_OUTPUTS = {
    "completion_readiness_valid",
    "completion_readiness_invalid",
    "completion_readiness_coverage_complete",
    "completion_readiness_coverage_incomplete",
    "completion_ready_for_review",
    "completion_not_ready",
    "readme_future_path_present",
    "review_required",
    "escalation_required",
    "fail_closed_recommended",
}

FORBIDDEN_EVALUATOR_OUTPUTS = {
    "m13_complete",
    "closes_176",
    "issue_176_closed",
    "v0_12_0_released",
    "release_approved",
    "release_created",
    "release_tag_created",
    "release_notes_published",
    "decision_proof_sealed",
    "sealed_by_completion_readiness",
    "risk_accepted",
    "audit_closed",
    "waiver_granted",
    "final_governance_judgment",
    "authority_transferred",
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
    "prepare_future_readme_status_path",
}

REQUIRED_AUTHORITY_MUST_NOT = {
    "declare_m13_complete",
    "close_tracker_issue_176",
    "declare_v0_12_0_released",
    "approve_releases",
    "create_releases",
    "create_tags",
    "publish_release_notes",
    "accept_risk",
    "seal_decision_proof",
    "close_audits",
    "grant_waivers",
    "transfer_authority",
    "make_final_governance_judgments",
}

BOUNDARY_CLAIM_FINDINGS = {
    "completion readiness is completion": "completion_readiness_completion_claim_detected",
    "readme future status path is release publication": "readme_future_status_release_publication_claim_detected",
    "readme future status path is m13 completion": "readme_future_status_m13_completion_claim_detected",
    "release proof linkage is release approval": "release_proof_release_approval_claim_detected",
    "release_ready_for_review is release_approved": "release_ready_for_review_approval_claim_detected",
    "completion_ready_for_review is m13_complete": "completion_ready_for_review_m13_complete_claim_detected",
    "readme_future_path_present is released": "readme_future_path_released_claim_detected",
    "evidence_complete is sealed": "evidence_complete_sealed_claim_detected",
    "replay_ready is sealed": "replay_ready_sealed_claim_detected",
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

README_REQUIRED_PHRASES = {
    "M13 remains active work; final completion has not been declared.",
    "Tracker: #176 remains open.",
    "Future target release path: v0.12.0 has not been released and is not listed in released versions.",
    "Future README status path: v0.12.0 / M13 remains a future-only path until a final completion PR.",
}

SAFE_NEGATED_PHRASES = {
    "not m13_complete",
    "must not declare m13 complete",
    "not released",
    "not release publication",
    "not release approval",
    "not m13 completion",
    "not sealed",
    "not close #176",
    "#176 remains open",
    "close_tracker_issue_176",
    "declare_m13_complete",
    "declare_v0_12_0_released",
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



def _is_safe_negated(text: str) -> bool:
    return any(phrase in text for phrase in SAFE_NEGATED_PHRASES)



def detect_completion_readiness_forbidden_claims(
    value: Any, parent_key: str | None = None
) -> set[str]:
    claims: set[str] = set()

    if parent_key in SAFE_CONTEXT_KEYS:
        return claims

    if isinstance(value, dict):
        for key, item in value.items():
            claims.update(detect_completion_readiness_forbidden_claims(item, str(key)))
        return claims

    if isinstance(value, list):
        for item in value:
            claims.update(detect_completion_readiness_forbidden_claims(item, parent_key))
        return claims

    normalized = _text(value)
    if _is_safe_negated(normalized):
        return claims
    if normalized in FORBIDDEN_EVALUATOR_OUTPUTS:
        claims.add(normalized)
    for phrase in BOUNDARY_CLAIM_FINDINGS:
        if phrase in normalized:
            claims.add(phrase)
    return claims



def evaluate_m13_completion_readiness(
    artifact: dict[str, Any], readme_text: str | None = None
) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    boundary_violation = False
    not_ready = False

    def add_missing(finding: str, evidence: str) -> None:
        findings.append(finding)
        missing_evidence.append(evidence)

    if not artifact:
        add_missing("completion_readiness_artifact_missing", "artifact")

    for field, finding in REQUIRED_ARTIFACT_FIELDS.items():
        if not _has_value(artifact, field):
            add_missing(finding, field)

    if artifact.get("artifact_status") != "active_work_in_progress_not_released":
        add_missing("artifact_status_not_active_work_in_progress", "artifact_status")
    if artifact.get("m13_completion_status") != "active_work_not_complete":
        add_missing("m13_completion_status_not_active_work", "m13_completion_status")
    if artifact.get("related_issue") != "#176":
        add_missing("missing_related_issue_176", "related_issue")
    if artifact.get("introduced_after_release") != "v0.11.0":
        add_missing("missing_prior_released_baseline_v0_11_0", "introduced_after_release")
    if artifact.get("target_future_release") != "v0.12.0":
        add_missing("missing_target_future_release_v0_12_0", "target_future_release")

    for field, expected in EXPECTED_PR_REFS.items():
        if artifact.get(field) != expected:
            add_missing(f"missing_{field}", field)

    tracker_state = _text(artifact.get("tracker_issue_closure_state"))
    if "open" not in tracker_state or tracker_state == "closed":
        findings.append("tracker_issue_176_not_marked_open")
        missing_evidence.append("tracker_issue_closure_state")
        boundary_violation = True
    if artifact.get("tracker_issue_linkage") != "Refs #176":
        add_missing("tracker_issue_linkage_not_refs_only", "tracker_issue_linkage")
    if _has_tracker_176_closure_claim(artifact):
        findings.append("tracker_issue_176_closure_claim_detected")
        boundary_violation = True

    release_status_future_only = _release_status_future_only(artifact)
    if not release_status_future_only:
        add_missing("release_status_future_only_missing", "release_status")

    for field, finding in [
        ("release_approval", "release_approval_claim_detected"),
        ("release_created", "release_created_claim_detected"),
        ("release_tag_created", "release_tag_created_claim_detected"),
        ("release_notes_published", "release_notes_published_claim_detected"),
        ("m13_complete", "m13_completion_claim_detected"),
        ("issue_176_closed", "issue_176_closed_claim_detected"),
        ("decision_proof_sealed", "decision_proof_sealing_claim_detected"),
        ("released", "v0_12_0_release_claim_detected"),
    ]:
        if artifact.get(field) is True:
            findings.append(finding)
            boundary_violation = True

    if _has_v0_12_0_release_claim(artifact):
        findings.append("v0_12_0_release_claim_detected")
        boundary_violation = True
    if _has_m13_completion_claim(artifact):
        findings.append("m13_completion_claim_detected")
        boundary_violation = True

    coverage_complete = _completion_readiness_coverage_complete(artifact)
    if not coverage_complete:
        add_missing("completion_readiness_coverage_incomplete", "release_linkage_refs")
        not_ready = True

    if not REQUIRED_ARTIFACT_LINKS <= set(_as_dict(artifact.get("artifact_links"))):
        add_missing("artifact_link_coverage_incomplete", "artifact_links")
        not_ready = True

    boundary_statements = {
        statement.lower() for statement in _as_set(artifact.get("required_boundary_statements"))
    }
    if not REQUIRED_BOUNDARY_STATEMENTS <= boundary_statements:
        add_missing("required_boundary_statements_incomplete", "required_boundary_statements")
        not_ready = True

    if artifact.get("readme_future_status_path") != "present_future_only":
        add_missing("readme_future_status_path_missing", "readme_future_status_path")
        not_ready = True
    if artifact.get("readme_future_path_present") is not True:
        add_missing("readme_future_path_present_missing", "readme_future_path_present")
        not_ready = True

    if not REQUIRED_ALLOWED_OUTPUTS <= _as_set(artifact.get("allowed_evaluator_outputs")):
        add_missing("allowed_evaluator_outputs_missing", "allowed_evaluator_outputs")
    if not FORBIDDEN_EVALUATOR_OUTPUTS <= _as_set(artifact.get("forbidden_evaluator_outputs")):
        add_missing("forbidden_evaluator_outputs_missing", "forbidden_evaluator_outputs")
    if not _authority_boundary_complete(artifact):
        add_missing("authority_boundary_statement_incomplete", "authority_boundary")

    boundary_language = _boundary_language(artifact)
    if not _required_boundary_language_present(boundary_language):
        add_missing("missing_aaos_completion_readiness_boundary_statement", "aaos_retained_authority_statement")
    for phrase, finding in BOUNDARY_CLAIM_FINDINGS.items():
        if phrase in boundary_language and not _is_safe_negated(boundary_language):
            findings.append(finding)
            boundary_violation = True

    forbidden_claims = detect_completion_readiness_forbidden_claims(artifact)
    if forbidden_claims:
        findings.append("authority_transfer_claim_detected")
        boundary_violation = True

    readme_future_path_present = readme_text is None
    if readme_text is not None:
        readme_result = _evaluate_readme_future_path(readme_text)
        readme_future_path_present = readme_result["readme_future_path_present"]
        findings.extend(readme_result["findings"])
        missing_evidence.extend(readme_result["missing_evidence"])
        boundary_violation = boundary_violation or readme_result["boundary_violation"]
        not_ready = not_ready or not readme_future_path_present

    if artifact.get("completion_readiness_status") != "completion_ready_for_review_not_complete":
        add_missing(
            "completion_readiness_status_not_ready_for_review_not_complete",
            "completion_readiness_status",
        )
        not_ready = True
    if artifact.get("completion_ready_for_review") is not True:
        add_missing("completion_ready_for_review_missing", "completion_ready_for_review")
        not_ready = True

    return _completion_readiness_result(
        findings=findings,
        missing_evidence=missing_evidence,
        boundary_violation=boundary_violation,
        coverage_complete=coverage_complete,
        readme_future_path_present=readme_future_path_present,
        release_status_future_only=release_status_future_only,
        not_ready=not_ready,
    )



def _completion_readiness_coverage_complete(artifact: dict[str, Any]) -> bool:
    refs = _as_dict(artifact.get("release_linkage_refs"))
    return all(refs.get(field) == expected for field, expected in REQUIRED_LINKAGE_REFS.items())



def _release_status_future_only(artifact: dict[str, Any]) -> bool:
    future_tag = _as_dict(artifact.get("future_release_tag_path"))
    prior_baseline = _as_dict(artifact.get("prior_released_baseline"))
    return (
        artifact.get("introduced_after_release") == "v0.11.0"
        and prior_baseline.get("release_tag") == "v0.11.0"
        and prior_baseline.get("status") == "prior_released_baseline"
        and artifact.get("target_future_release") == "v0.12.0"
        and artifact.get("release_status") == "future_target_release_only"
        and future_tag.get("target_tag") == "v0.12.0"
        and future_tag.get("state") == "future_tag_path_only"
        and future_tag.get("released") is False
        and artifact.get("release_approval") is False
        and artifact.get("release_created") is False
        and artifact.get("release_tag_created") is False
        and artifact.get("release_notes_published") is False
        and artifact.get("m13_complete") is False
        and artifact.get("issue_176_closed") is False
        and artifact.get("decision_proof_sealed") is False
        and artifact.get("released") is False
        and not _has_v0_12_0_release_claim(artifact)
    )



def _authority_boundary_complete(artifact: dict[str, Any]) -> bool:
    boundary = _as_dict(artifact.get("authority_boundary"))
    return (
        REQUIRED_AUTHORITY_MAY <= _as_set(boundary.get("may"))
        and REQUIRED_AUTHORITY_MUST_NOT <= _as_set(boundary.get("must_not"))
    )



def _boundary_language(artifact: dict[str, Any]) -> str:
    segments = [
        str(artifact.get("governance_boundary_statement", "")),
        str(artifact.get("decision_proof_sealing_boundary_statement", "")),
        str(artifact.get("aaos_retained_authority_statement", "")),
        str(artifact.get("sovereignty_statement", "")),
    ]
    segments.extend(str(value) for value in _as_dict(artifact.get("semantic_boundaries")).values())
    return " ".join(segments).lower()



def _required_boundary_language_present(boundary_language: str) -> bool:
    return all(
        phrase in boundary_language
        for phrase in [
            "completion readiness is evidence review only",
            "must not declare m13 complete",
            "completion readiness is not completion",
            "readme future status path is not release publication",
            "readme future status path is not m13 completion",
            "v0.12.0 future target is not released",
            "m13 remains active work until final completion pr",
            "#176 remains open until final completion pr",
            "release proof linkage is not release approval",
            "completion_ready_for_review is not m13_complete",
            "readme_future_path_present is not released",
            "evidence_complete is not sealed",
            "replay_ready is not sealed",
            "decision proof sealing remains aaos-owned",
            "aaos retains",
            "aaos remains the decision sovereignty layer",
        ]
    )



def _evaluate_readme_future_path(readme_text: str) -> dict[str, Any]:
    lower = readme_text.lower()
    findings: list[str] = []
    missing_evidence: list[str] = []
    boundary_violation = False

    for phrase in README_REQUIRED_PHRASES:
        if phrase.lower() not in lower:
            missing_evidence.append("README.md#next-phase")

    if missing_evidence:
        findings.append("readme_future_status_path_missing")

    releases_section = _section_between(lower, "## releases", "current baseline:")
    current_status_section = _section_between(lower, "## current status", "aaos public now has:")

    if "\n- v0.12.0" in releases_section:
        findings.append("readme_v0_12_0_released_claim_detected")
        boundary_violation = True
    if "m13 completed:" in current_status_section or "m13 are complete" in current_status_section:
        findings.append("readme_m13_completion_claim_detected")
        boundary_violation = True
    if "m13 complete" in lower:
        findings.append("readme_m13_completion_claim_detected")
        boundary_violation = True
    if "v0.12.0 released" in lower:
        findings.append("readme_v0_12_0_released_claim_detected")
        boundary_violation = True
    if any(phrase in lower for phrase in TRACKER_176_CLOSURE_PHRASES):
        findings.append("readme_tracker_issue_176_closure_claim_detected")
        boundary_violation = True

    return {
        "readme_future_path_present": not missing_evidence,
        "findings": findings,
        "missing_evidence": missing_evidence,
        "boundary_violation": boundary_violation,
    }



def _section_between(text: str, start: str, end: str) -> str:
    start_index = text.find(start)
    if start_index == -1:
        return ""
    end_index = text.find(end, start_index)
    if end_index == -1:
        return text[start_index:]
    return text[start_index:end_index]



def _has_tracker_176_closure_claim(artifact: dict[str, Any]) -> bool:
    for item in _iter_claim_text(artifact):
        if item == "closes_176" or item == "issue_176_closed":
            return True
        if _is_safe_negated(item):
            continue
        if any(phrase in item for phrase in TRACKER_176_CLOSURE_PHRASES):
            return True
    return False



def _has_v0_12_0_release_claim(artifact: dict[str, Any]) -> bool:
    if _as_dict(artifact.get("future_release_tag_path")).get("released") is True:
        return True
    if artifact.get("released") is True:
        return True
    for item in _iter_claim_text(artifact):
        if _is_safe_negated(item):
            continue
        if item == "v0_12_0_released" or "v0.12.0 released" in item:
            return True
    return False



def _has_m13_completion_claim(artifact: dict[str, Any]) -> bool:
    if artifact.get("m13_complete") is True:
        return True
    for item in _iter_claim_text(artifact):
        if _is_safe_negated(item):
            continue
        if item == "m13_complete" or "m13 complete" in item:
            return True
    return False



def _completion_readiness_result(
    findings: list[str],
    missing_evidence: list[str],
    boundary_violation: bool,
    coverage_complete: bool,
    readme_future_path_present: bool,
    release_status_future_only: bool,
    not_ready: bool,
) -> dict[str, Any]:
    unique_findings = sorted(set(findings))
    unique_missing = sorted(set(missing_evidence))
    failed = bool(unique_findings or unique_missing or boundary_violation)
    ready_for_review = not failed and not not_ready

    return {
        "completion_readiness_valid": not failed,
        "completion_readiness_invalid": failed,
        "completion_readiness_coverage_complete": coverage_complete,
        "completion_readiness_coverage_incomplete": not coverage_complete,
        "completion_ready_for_review": ready_for_review,
        "completion_not_ready": not_ready or failed,
        "readme_future_path_present": readme_future_path_present,
        "release_status_future_only": release_status_future_only,
        "completion_readiness_findings": unique_findings,
        "missing_evidence": unique_missing,
        "review_required": failed or not_ready,
        "escalation_required": boundary_violation,
        "fail_closed_recommended": boundary_violation,
    }
