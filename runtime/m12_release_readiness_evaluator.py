"""Deterministic checks for M12 release proof linkage and readiness."""

from __future__ import annotations

from typing import Any


REQUIRED_RELEASE_FIELDS = {
    "artifact_id": "missing_release_artifact_id",
    "artifact_name": "missing_release_artifact_name",
    "artifact_scope": "missing_release_artifact_scope",
    "artifact_status": "missing_release_artifact_status",
    "m12_completion_status": "missing_release_m12_completion_status",
    "related_issue": "missing_release_related_issue_168",
    "tracker_issue_closure_state": "missing_release_tracker_issue_168_open_state",
    "tracker_issue_linkage": "missing_release_tracker_issue_168_reference",
    "consumer_registry_pr": "missing_release_consumer_registry_pr_169",
    "integration_ci_check_specimen_pr": "missing_release_integration_ci_check_specimen_pr_170",
    "cross_consumer_traceability_pr": "missing_release_cross_consumer_traceability_pr_172",
    "multi_consumer_semantics_pr": "missing_release_multi_consumer_semantics_pr_173",
    "consumer_registry_pattern_artifact": "missing_release_consumer_registry_pattern_artifact",
    "integration_ci_check_specimen_artifact": "missing_release_integration_ci_check_specimen_artifact",
    "cross_consumer_traceability_examples_artifact": "missing_release_cross_consumer_traceability_examples_artifact",
    "multi_consumer_semantics_artifact": "missing_release_multi_consumer_semantics_artifact",
    "deterministic_evaluator_references": "missing_release_deterministic_evaluator_references",
    "test_references": "missing_release_test_references",
    "target_future_release": "missing_release_target_future_release_v0_11_0",
    "future_release_tag_path": "missing_release_future_release_tag_path",
    "release_status_path": "missing_release_status_path",
    "readme_release_status_path": "missing_release_readme_status_path",
    "release_proof_linkage": "missing_release_proof_linkage",
    "release_readiness_boundary_statement": "missing_release_readiness_boundary_statement",
    "tracker_boundary_statement": "missing_release_tracker_boundary_statement",
    "m12_status_statement": "missing_release_m12_status_statement",
    "readme_status_statement": "missing_release_readme_status_statement",
    "authority_boundary": "missing_release_authority_boundary",
    "semantic_boundaries": "missing_release_semantic_boundaries",
    "decision_proof_sealing_boundary_statement": "missing_release_decision_proof_sealing_boundary_statement",
    "aaos_retained_authority_statement": "missing_release_aaos_retained_authority_statement",
    "sovereignty_statement": "missing_release_sovereignty_statement",
}

REQUIRED_CHECKLIST_FIELDS = {
    "checklist_id": "missing_checklist_id",
    "checklist_name": "missing_checklist_name",
    "checklist_scope": "missing_checklist_scope",
    "checklist_status": "missing_checklist_status",
    "m12_completion_status": "missing_checklist_m12_completion_status",
    "related_issue": "missing_checklist_related_issue_168",
    "tracker_issue_closure_state": "missing_checklist_tracker_issue_168_open_state",
    "tracker_issue_linkage": "missing_checklist_tracker_issue_168_reference",
    "consumer_registry_pr": "missing_checklist_consumer_registry_pr_169",
    "integration_ci_check_specimen_pr": "missing_checklist_integration_ci_check_specimen_pr_170",
    "cross_consumer_traceability_pr": "missing_checklist_cross_consumer_traceability_pr_172",
    "multi_consumer_semantics_pr": "missing_checklist_multi_consumer_semantics_pr_173",
    "release_proof_linkage_artifact": "missing_checklist_release_proof_linkage_artifact",
    "consumer_registry_pattern_artifact": "missing_checklist_consumer_registry_pattern_artifact",
    "integration_ci_check_specimen_artifact": "missing_checklist_integration_ci_check_specimen_artifact",
    "cross_consumer_traceability_examples_artifact": "missing_checklist_cross_consumer_traceability_examples_artifact",
    "multi_consumer_semantics_artifact": "missing_checklist_multi_consumer_semantics_artifact",
    "target_future_release": "missing_checklist_target_future_release_v0_11_0",
    "future_release_tag_path": "missing_checklist_future_release_tag_path",
    "release_status_path": "missing_checklist_release_status_path",
    "readme_release_status_path": "missing_checklist_readme_release_status_path",
    "expected_m12_output_checklist": "missing_expected_m12_output_checklist",
    "deterministic_test_references": "missing_deterministic_test_references",
    "readiness_summary": "missing_readiness_summary",
    "authority_boundary": "missing_checklist_authority_boundary",
    "semantic_boundaries": "missing_checklist_semantic_boundaries",
    "decision_proof_sealing_boundary_statement": "missing_checklist_decision_proof_sealing_boundary_statement",
    "aaos_retained_authority_statement": "missing_checklist_aaos_retained_authority_statement",
    "sovereignty_statement": "missing_checklist_sovereignty_statement",
}

EXPECTED_PR_REFS = {
    "consumer_registry_pr": "#169",
    "integration_ci_check_specimen_pr": "#170",
    "cross_consumer_traceability_pr": "#172",
    "multi_consumer_semantics_pr": "#173",
}

EXPECTED_M12_OUTPUT_ITEM_IDS = {
    "public_integration_pack_consumer_registry_pattern",
    "compliant_external_consumer_registry_entry",
    "negative_consumer_registry_fixture",
    "integration_facing_ci_checks",
    "cross_consumer_traceability_examples",
    "multi_consumer_sealed_nonsealed_semantics",
    "m12_registry_release_proof_linkage",
    "deterministic_checks",
    "readme_release_status_update_path",
    "aaos_final_governance_authority_preserved",
}

REQUIRED_EVALUATOR_REFS = {
    "runtime/m12_consumer_registry_evaluator.py",
    "runtime/m12_integration_ci_check_evaluator.py",
    "runtime/m12_cross_consumer_traceability_evaluator.py",
    "runtime/m12_multi_consumer_semantics_evaluator.py",
    "runtime/m12_release_readiness_evaluator.py",
}

REQUIRED_AUTHORITY_MAY = {
    "produce_evidence",
    "consume_evidence",
    "reference_evidence",
    "replay_evidence",
    "inspect_evidence",
    "report_findings",
    "check_evidence",
    "link_evidence",
    "surface_review_required",
    "surface_escalation_required",
    "surface_fail_closed_recommended",
}

REQUIRED_AUTHORITY_MUST_NOT = {
    "seal_decision_proof",
    "re_seal_aaos_sealed_artifacts",
    "convert_non_sealed_artifacts_into_sealed_artifacts",
    "convert_sealing_eligibility_into_final_sealing",
    "approve_releases",
    "accept_risk",
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

REQUIRED_EVALUATOR_OUTPUTS = {
    "m12_release_readiness_valid",
    "m12_release_readiness_invalid",
    "release_proof_linkage_present",
    "release_proof_linkage_missing",
    "completion_readiness_candidate",
    "expected_output_coverage_complete",
    "expected_output_coverage_incomplete",
    "authority_boundary_preserved",
    "authority_boundary_violation",
    "release_status_future_only",
    "review_required",
    "escalation_required",
    "fail_closed_recommended",
}

FORBIDDEN_EVALUATOR_OUTPUTS = {
    "m12_complete",
    "v0_11_0_released",
    "release_approved",
    "risk_accepted",
    "decision_proof_sealed",
    "sealed_by_consumer",
    "sealed_by_registry",
    "sealed_by_ci",
    "sealed_by_traceability",
    "rollback_executed",
    "fail_closed_executed",
    "audit_closed",
    "waiver_granted",
    "final_governance_judgment",
    "closes_168",
}

BOUNDARY_CLAIM_FINDINGS = {
    "registry inclusion is approval": "registry_inclusion_approval_claim_detected",
    "ci pass is approval": "ci_pass_approval_claim_detected",
    "traceability linkage is approval": "traceability_linkage_approval_claim_detected",
    "release proof linkage is release approval": "release_proof_release_approval_claim_detected",
    "fail_closed_recommended is fail_closed_executed": "fail_closed_execution_claim_detected",
    "sealing_eligible is sealed": "sealing_eligibility_sealed_claim_detected",
    "evidence_complete is sealed": "evidence_complete_sealed_claim_detected",
    "replay_ready is sealed": "replay_ready_sealed_claim_detected",
    "evaluator findings are sealing": "evaluator_findings_sealing_claim_detected",
    "governance ci findings are sealing": "governance_ci_findings_sealing_claim_detected",
}

TRACKER_168_CLOSURE_PHRASES = {
    "closes #168",
    "close #168",
    "closed #168",
    "fixes #168",
    "fixed #168",
    "resolves #168",
    "resolved #168",
}

SAFE_CONTEXT_KEYS = {
    "must_not",
    "forbidden_evaluator_outputs",
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



def _iter_claim_text(value: Any, parent_key: str | None = None) -> list[str]:
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

    if parent_key in SAFE_CONTEXT_KEYS:
        return []

    return [_text(value)]



def _boundary_language(*records: dict[str, Any]) -> str:
    segments: list[str] = []
    for record in records:
        segments.extend(
            [
                str(record.get("release_readiness_boundary_statement", "")),
                str(record.get("tracker_boundary_statement", "")),
                str(record.get("m12_status_statement", "")),
                str(record.get("readme_status_statement", "")),
                str(record.get("decision_proof_sealing_boundary_statement", "")),
                str(record.get("aaos_retained_authority_statement", "")),
                str(record.get("sovereignty_statement", "")),
                str(record.get("governance_boundary_statement", "")),
            ]
        )
        semantic_boundaries = _as_dict(record.get("semantic_boundaries"))
        segments.extend(str(value) for value in semantic_boundaries.values())
        release_linkage = _as_dict(record.get("release_proof_linkage"))
        segments.append(str(release_linkage.get("boundary_statement", "")))
    return " ".join(segments).lower()



def detect_m12_release_readiness_forbidden_claims(
    value: Any, parent_key: str | None = None
) -> set[str]:
    claims: set[str] = set()

    if isinstance(value, dict):
        for key, item in value.items():
            claims.update(detect_m12_release_readiness_forbidden_claims(item, str(key)))
        return claims

    if isinstance(value, list):
        for item in value:
            claims.update(detect_m12_release_readiness_forbidden_claims(item, parent_key))
        return claims

    if parent_key in SAFE_CONTEXT_KEYS:
        return claims

    normalized = _text(value)
    if normalized in FORBIDDEN_EVALUATOR_OUTPUTS:
        claims.add(normalized)

    for phrase in BOUNDARY_CLAIM_FINDINGS:
        if phrase in normalized:
            claims.add(phrase)

    return claims



def evaluate_m12_release_readiness(
    release_linkage: dict[str, Any],
    readiness_checklist: dict[str, Any],
) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    authority_boundary_violation = False

    def add_missing(finding: str, evidence: str) -> None:
        findings.append(finding)
        missing_evidence.append(evidence)

    if not release_linkage:
        add_missing("release_proof_linkage_artifact_missing", "release_linkage")
    if not readiness_checklist:
        add_missing("completion_readiness_checklist_missing", "readiness_checklist")

    _evaluate_required_fields(
        release_linkage,
        REQUIRED_RELEASE_FIELDS,
        findings,
        missing_evidence,
    )
    _evaluate_required_fields(
        readiness_checklist,
        REQUIRED_CHECKLIST_FIELDS,
        findings,
        missing_evidence,
    )

    for record_name, record in [
        ("release", release_linkage),
        ("checklist", readiness_checklist),
    ]:
        if record.get("related_issue") != "#168":
            add_missing(f"missing_{record_name}_related_issue_168", f"{record_name}.related_issue")
        for field, expected in EXPECTED_PR_REFS.items():
            if record.get(field) != expected:
                add_missing(
                    f"missing_{record_name}_{field}_{expected.removeprefix('#')}",
                    f"{record_name}.{field}",
                )
        tracker_state = _text(record.get("tracker_issue_closure_state"))
        if "open" not in tracker_state or tracker_state == "closed":
            add_missing(
                f"{record_name}_tracker_issue_168_not_marked_open",
                f"{record_name}.tracker_issue_closure_state",
            )

    if _has_tracker_168_closure_claim(release_linkage) or _has_tracker_168_closure_claim(readiness_checklist):
        findings.append("tracker_issue_168_closure_claim_detected")
        authority_boundary_violation = True

    release_status_future_only = _release_status_future_only(release_linkage) and _release_status_future_only(readiness_checklist)
    if not release_status_future_only:
        add_missing("release_status_future_only_missing", "release_status_path")
    if _has_v0_11_0_release_claim(release_linkage) or _has_v0_11_0_release_claim(readiness_checklist):
        findings.append("v0_11_0_release_claim_detected")
        authority_boundary_violation = True
    if _has_m12_completion_claim(release_linkage) or _has_m12_completion_claim(readiness_checklist):
        findings.append("m12_completion_claim_detected")
        authority_boundary_violation = True

    release_proof_linkage_present = _release_proof_linkage_present(release_linkage)
    if not release_proof_linkage_present:
        add_missing("release_proof_linkage_missing", "release_linkage.release_proof_linkage")

    if not _expected_output_coverage_complete(readiness_checklist):
        add_missing("expected_output_coverage_incomplete", "expected_m12_output_checklist")

    if not REQUIRED_EVALUATOR_REFS <= _as_set(release_linkage.get("deterministic_evaluator_references")):
        add_missing("deterministic_evaluator_references_missing", "deterministic_evaluator_references")

    if not _authority_boundary_complete(release_linkage) or not _authority_boundary_complete(readiness_checklist):
        add_missing("authority_boundary_statement_incomplete", "authority_boundary")

    boundary_language = _boundary_language(release_linkage, readiness_checklist)
    for phrase, finding in BOUNDARY_CLAIM_FINDINGS.items():
        if phrase in boundary_language:
            findings.append(finding)
            authority_boundary_violation = True

    if not _required_boundary_language_present(boundary_language):
        add_missing("missing_aaos_authority_boundary_statement", "aaos_retained_authority_statement")

    claims = detect_m12_release_readiness_forbidden_claims(release_linkage) | detect_m12_release_readiness_forbidden_claims(readiness_checklist)
    if claims:
        findings.append("authority_transfer_claim_detected")
        authority_boundary_violation = True

    return _release_readiness_result(
        findings=findings,
        missing_evidence=missing_evidence,
        authority_boundary_violation=authority_boundary_violation,
        release_proof_linkage_present=release_proof_linkage_present,
        expected_output_coverage_complete=_expected_output_coverage_complete(readiness_checklist),
        release_status_future_only=release_status_future_only,
    )



def _evaluate_required_fields(
    record: dict[str, Any],
    required_fields: dict[str, str],
    findings: list[str],
    missing_evidence: list[str],
) -> None:
    for field, finding in required_fields.items():
        if not _has_value(record, field):
            findings.append(finding)
            missing_evidence.append(field)



def _release_proof_linkage_present(record: dict[str, Any]) -> bool:
    linkage = _as_dict(record.get("release_proof_linkage"))
    return (
        linkage.get("present") is True
        and linkage.get("evidence_linkage_only") is True
        and linkage.get("release_approval") is False
        and bool(_as_list(linkage.get("release_proof_refs")))
    )



def _expected_output_coverage_complete(checklist: dict[str, Any]) -> bool:
    items = _as_list(checklist.get("expected_m12_output_checklist"))
    represented_ids = {
        _text(item.get("item_id"))
        for item in items
        if isinstance(item, dict)
        and item.get("represented") is True
        and bool(_as_list(item.get("evidence_refs")))
    }
    return EXPECTED_M12_OUTPUT_ITEM_IDS <= represented_ids



def _authority_boundary_complete(record: dict[str, Any]) -> bool:
    boundary = _as_dict(record.get("authority_boundary"))
    return (
        REQUIRED_AUTHORITY_MAY <= _as_set(boundary.get("may"))
        and REQUIRED_AUTHORITY_MUST_NOT <= _as_set(boundary.get("must_not"))
    )



def _release_status_future_only(record: dict[str, Any]) -> bool:
    release_status = _as_dict(record.get("release_status_path"))
    future_tag = _as_dict(record.get("future_release_tag_path"))
    release_text = " ".join(
        _iter_claim_text(release_status) + _iter_claim_text(future_tag)
    )
    return (
        record.get("target_future_release") == "v0.11.0"
        and release_status.get("state") == "future_target_release_only"
        and future_tag.get("target_tag") == "v0.11.0"
        and future_tag.get("state") == "future_tag_path_only"
        and future_tag.get("released") is False
        and "future target release" in release_text
        and "not be treated as released" in release_text
        and not _has_v0_11_0_release_claim(record)
    )



def _required_boundary_language_present(boundary_language: str) -> bool:
    return all(
        phrase in boundary_language
        for phrase in [
            "evidence linkage only",
            "not release approval",
            "registry inclusion is not approval",
            "ci pass is not approval",
            "traceability linkage is not approval",
            "release proof linkage is not release approval",
            "fail_closed_recommended is not fail_closed_executed",
            "sealing_eligible is not sealed",
            "evidence_complete is not sealed",
            "replay_ready is not sealed",
            "evaluator_findings are not sealing",
            "governance ci findings are not sealing",
            "decision proof sealing remains aaos-owned",
            "aaos retains",
            "aaos remains the decision sovereignty layer",
        ]
    )



def _has_v0_11_0_release_claim(record: dict[str, Any]) -> bool:
    if _as_dict(record.get("future_release_tag_path")).get("released") is True:
        return True
    for item in _iter_claim_text(record):
        if item == "v0_11_0_released" or "v0.11.0 is released" in item:
            return True
    return False



def _has_m12_completion_claim(record: dict[str, Any]) -> bool:
    for item in _iter_claim_text(record):
        if item == "m12_complete" or "m12 is complete" in item:
            return True
    return False



def _has_tracker_168_closure_claim(record: dict[str, Any]) -> bool:
    for item in _iter_claim_text(record):
        if item == "closes_168" or any(
            phrase in item for phrase in TRACKER_168_CLOSURE_PHRASES
        ):
            return True
    return False



def _release_readiness_result(
    findings: list[str],
    missing_evidence: list[str],
    authority_boundary_violation: bool,
    release_proof_linkage_present: bool,
    expected_output_coverage_complete: bool,
    release_status_future_only: bool,
) -> dict[str, Any]:
    unique_findings = sorted(set(findings))
    unique_missing = sorted(set(missing_evidence))
    failed = bool(unique_findings or unique_missing or authority_boundary_violation)

    return {
        "m12_release_readiness_valid": not failed,
        "m12_release_readiness_invalid": failed,
        "release_proof_linkage_present": release_proof_linkage_present,
        "release_proof_linkage_missing": not release_proof_linkage_present,
        "completion_readiness_candidate": not failed,
        "expected_output_coverage_complete": expected_output_coverage_complete,
        "expected_output_coverage_incomplete": not expected_output_coverage_complete,
        "authority_boundary_preserved": not authority_boundary_violation,
        "authority_boundary_violation": authority_boundary_violation,
        "release_status_future_only": release_status_future_only,
        "release_readiness_findings": unique_findings,
        "missing_evidence": unique_missing,
        "review_required": failed,
        "escalation_required": authority_boundary_violation,
        "fail_closed_recommended": authority_boundary_violation,
    }
