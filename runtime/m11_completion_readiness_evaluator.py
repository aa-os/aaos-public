"""Deterministic checks for M11 completion readiness evidence."""

from __future__ import annotations

from typing import Any

from runtime.public_integration_pack_evaluator import detect_forbidden_authority_claims


REQUIRED_CHECKLIST_FIELDS = {
    "checklist_id": "missing_checklist_id",
    "readiness_state": "missing_completion_readiness_state",
    "readiness_scope": "missing_readiness_scope",
    "m11_completion_status": "missing_m11_completion_status",
    "m11_tracker_issue": "missing_m11_tracker_issue_120",
    "tracker_issue_closure_state": "missing_tracker_issue_120_open_state",
    "tracker_issue_linkage": "missing_tracker_issue_120_reference",
    "related_prs": "missing_related_prs",
    "artifact_references": "missing_artifact_references",
    "expected_m11_output_coverage": "missing_expected_m11_output_coverage",
    "authority_boundary_checklist": "missing_authority_boundary_checklist",
    "release_status_path": "missing_release_status_path",
    "readiness_outputs": "missing_readiness_outputs",
    "not_authority_statement": "missing_not_authority_statement",
    "decision_proof_sealing_boundary_statement": "missing_decision_proof_sealing_boundary_statement",
    "sovereignty_statement": "missing_sovereignty_statement",
}

REQUIRED_RELATED_PRS = {
    "#121": "missing_first_m11_pilot_pr_121",
    "#131": "missing_m11_readme_wip_sync_pr_131",
    "#134": "missing_m11_release_proof_registry_traceability_pr_134",
    "#135": "missing_m11_external_consumer_matrix_pr_135",
}

REQUIRED_ARTIFACT_REFERENCES = {
    "public_integration_pack_pilot_package": "missing_public_integration_pack_pilot_package",
    "external_evidence_consumer_specimen": "missing_external_evidence_consumer_specimen",
    "sealed_vs_non_sealed_artifact_consumption_matrix": "missing_consumption_matrix_reference",
    "external_consumer_fixtures": "missing_external_consumer_fixtures_reference",
    "fail_closed_consumption_examples": "missing_fail_closed_examples_reference",
    "m11_pilot_release_proof_linkage": "missing_m11_pilot_release_proof_linkage_reference",
    "registry_facing_traceability": "missing_registry_facing_traceability_reference",
    "deterministic_public_integration_pack_evaluator": "missing_public_integration_pack_evaluator_reference",
    "evaluator_tests": "missing_evaluator_tests_reference",
    "readme_current_work_status": "missing_readme_current_work_status_reference",
    "future_v0_10_0_completion_release_path": "missing_future_v0_10_0_completion_release_path",
}

EXPECTED_M11_OUTPUT_COVERAGE_KEYS = {
    "concrete_public_integration_pack_pilot_package",
    "external_evidence_consumer_specimen",
    "sealed_vs_non_sealed_artifact_consumption_semantics",
    "integration_facing_examples",
    "release_proof_linkage_for_pilot_package",
    "deterministic_checks_if_appropriate",
    "readme_release_status_update_path_for_v0_10_0",
    "clear_preservation_of_aaos_final_governance_authority",
}

REQUIRED_ALLOWED_EVIDENCE_ACTIONS = {
    "produce_evidence",
    "consume_evidence",
    "reference_evidence",
    "replay_evidence",
    "inspect_evidence",
    "report_evidence",
    "link_evidence",
}

REQUIRED_FORBIDDEN_AUTHORITY_ACTIONS = {
    "seal decision proof",
    "approve releases",
    "accept risk",
    "execute rollback",
    "execute fail-closed",
    "close audits",
    "grant waivers",
    "change approval doctrine",
    "change identity trust",
    "change policy authority",
    "change decision routing",
    "make final governance judgments",
    "convert sealing eligibility into final sealing",
    "convert non-sealed artifacts into sealed artifacts",
}

REQUIRED_READINESS_OUTPUTS = {
    "m11_completion_readiness_valid",
    "m11_completion_readiness_invalid",
    "expected_output_coverage_complete",
    "expected_output_coverage_incomplete",
    "authority_boundary_preserved",
    "authority_boundary_violation",
    "release_status_path_present",
    "release_status_path_missing",
    "review_required",
    "escalation_required",
    "fail_closed_recommended",
}

FORBIDDEN_READINESS_OUTPUTS = {
    "m11_complete",
    "v0_10_0_released",
    "release_approved",
    "risk_accepted",
    "decision_proof_sealed",
    "sealed_by_external_consumer",
    "sealed_by_integration_pack",
    "sealed_by_registry",
    "rollback_executed",
    "fail_closed_executed",
    "audit_closed",
    "final_governance_judgment",
    "closes_120",
}

TRACKER_120_CLOSURE_PHRASES = {
    "closes #120",
    "close #120",
    "closed #120",
    "fixes #120",
    "fixed #120",
    "resolves #120",
    "resolved #120",
}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_set(value: Any) -> set[str]:
    return {str(item).strip() for item in _as_list(value) if str(item).strip()}


def _as_lower_set(value: Any) -> set[str]:
    return {_text(item) for item in _as_list(value) if str(item).strip()}


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


def _iter_text(value: Any) -> list[str]:
    if isinstance(value, dict):
        text: list[str] = []
        for item in value.values():
            text.extend(_iter_text(item))
        return text
    if isinstance(value, list):
        text = []
        for item in value:
            text.extend(_iter_text(item))
        return text
    return [_text(value)]


def _iter_refs(value: Any) -> set[str]:
    if isinstance(value, dict):
        refs: set[str] = set()
        for item in value.values():
            refs.update(_iter_refs(item))
        return refs
    if isinstance(value, list):
        refs = set()
        for item in value:
            refs.update(_iter_refs(item))
        return refs
    return {str(value).strip()}


def evaluate_m11_completion_readiness_checklist(record: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    authority_boundary_violation = False

    for field, finding in REQUIRED_CHECKLIST_FIELDS.items():
        if not _has_value(record, field):
            findings.append(finding)
            missing_evidence.append(field)

    if record.get("readiness_state") != "completion_readiness_candidate":
        findings.append("missing_completion_readiness_candidate_state")
        missing_evidence.append("readiness_state")

    if _has_m11_completion_claim(record):
        findings.append("m11_completion_claim_detected")
        authority_boundary_violation = True

    if record.get("m11_tracker_issue") != "#120":
        findings.append("missing_m11_tracker_issue_120")
        missing_evidence.append("m11_tracker_issue")

    tracker_state = _text(record.get("tracker_issue_closure_state"))
    if "open" not in tracker_state or tracker_state == "closed":
        findings.append("tracker_issue_120_not_marked_open")
        missing_evidence.append("tracker_issue_closure_state")
    if _has_tracker_120_closure_claim(record):
        findings.append("tracker_issue_120_closure_claim_detected")
        authority_boundary_violation = True

    related_refs = _iter_refs(record.get("related_prs"))
    for pr_ref, finding in REQUIRED_RELATED_PRS.items():
        if pr_ref not in related_refs:
            findings.append(finding)
            missing_evidence.append("related_prs")

    artifact_references = _as_dict(record.get("artifact_references"))
    for field, finding in REQUIRED_ARTIFACT_REFERENCES.items():
        if not _has_value(artifact_references, field):
            findings.append(finding)
            missing_evidence.append(f"artifact_references.{field}")

    coverage = _as_dict(record.get("expected_m11_output_coverage"))
    coverage_findings: list[str] = []
    missing_coverage_keys = EXPECTED_M11_OUTPUT_COVERAGE_KEYS - set(coverage)
    for key in sorted(missing_coverage_keys):
        coverage_findings.append(f"missing_expected_output_{key}")
        missing_evidence.append(f"expected_m11_output_coverage.{key}")

    for key in sorted(EXPECTED_M11_OUTPUT_COVERAGE_KEYS & set(coverage)):
        entry = _as_dict(coverage.get(key))
        if entry.get("represented") is not True:
            coverage_findings.append(f"expected_output_{key}_not_represented")
            missing_evidence.append(f"expected_m11_output_coverage.{key}.represented")
        if not _as_list(entry.get("evidence_refs")):
            coverage_findings.append(f"expected_output_{key}_missing_evidence_refs")
            missing_evidence.append(f"expected_m11_output_coverage.{key}.evidence_refs")

    findings.extend(coverage_findings)
    expected_output_coverage_complete = not coverage_findings

    authority = _as_dict(record.get("authority_boundary_checklist"))
    allowed_actions = _as_lower_set(authority.get("allowed_evidence_actions"))
    forbidden_actions = _as_lower_set(authority.get("forbidden_authority_actions"))
    if not REQUIRED_ALLOWED_EVIDENCE_ACTIONS <= allowed_actions:
        findings.append("missing_allowed_evidence_actions")
        missing_evidence.append("authority_boundary_checklist.allowed_evidence_actions")
    if not REQUIRED_FORBIDDEN_AUTHORITY_ACTIONS <= forbidden_actions:
        findings.append("missing_forbidden_authority_actions")
        missing_evidence.append("authority_boundary_checklist.forbidden_authority_actions")

    leaked_actions = REQUIRED_FORBIDDEN_AUTHORITY_ACTIONS & allowed_actions
    if leaked_actions:
        findings.append("forbidden_authority_actions_allowed")
        authority_boundary_violation = True

    boundary_language = " ".join(
        [
            str(authority.get("decision_proof_sealing_boundary", "")),
            str(authority.get("aaos_sovereignty_statement", "")),
            str(authority.get("fail_closed_recommendation_boundary", "")),
            str(authority.get("sealing_eligibility_boundary", "")),
            str(authority.get("release_proof_boundary", "")),
            str(authority.get("external_final_authority_boundary", "")),
            str(record.get("not_authority_statement", "")),
            str(record.get("decision_proof_sealing_boundary_statement", "")),
            str(record.get("sovereignty_statement", "")),
        ]
    ).lower()
    for required_phrase in [
        "decision proof sealing remains aaos-owned",
        "aaos remains the decision sovereignty layer",
        "fail_closed_recommended does not imply fail_closed_executed",
        "sealing_eligible does not imply sealed",
        "release proof linkage does not imply release approval",
        "no external system is treated as final governance authority",
    ]:
        if required_phrase not in boundary_language:
            findings.append("missing_authority_boundary_statement")
            missing_evidence.append("authority_boundary_checklist")
            break

    release_status_path = _as_dict(record.get("release_status_path"))
    release_status_language = " ".join(_iter_text(release_status_path))
    release_status_path_present = (
        release_status_path.get("present") is True
        and "future" in release_status_language
        and "reserved" in release_status_language
        and "not be treated as released" in release_status_language
    )
    if not release_status_path_present:
        findings.append("release_status_path_missing")
        missing_evidence.append("release_status_path")
    if "release proof linkage does not imply release approval" not in (
        boundary_language + " " + release_status_language
    ):
        findings.append("release_proof_linkage_implies_release_approval_boundary_missing")
        missing_evidence.append("release_status_path.release_proof_linkage_boundary")

    readiness_outputs = _as_set(record.get("readiness_outputs"))
    missing_outputs = REQUIRED_READINESS_OUTPUTS - readiness_outputs
    if missing_outputs:
        findings.append("missing_allowed_readiness_outputs")
        missing_evidence.append("readiness_outputs")
    if FORBIDDEN_READINESS_OUTPUTS & readiness_outputs:
        findings.append("forbidden_readiness_output_detected")
        authority_boundary_violation = True

    if _has_v0_10_0_release_claim(record):
        findings.append("v0_10_0_release_claim_detected")
        authority_boundary_violation = True

    if detect_forbidden_authority_claims(record):
        findings.append("authority_transfer_claim_detected")
        authority_boundary_violation = True

    return _readiness_result(
        findings=findings,
        missing_evidence=missing_evidence,
        authority_boundary_violation=authority_boundary_violation,
        expected_output_coverage_complete=expected_output_coverage_complete,
        release_status_path_present=release_status_path_present,
    )


def _has_v0_10_0_release_claim(record: dict[str, Any]) -> bool:
    for item in _iter_text(record):
        if item == "v0_10_0_released" or "v0.10.0 is released" in item:
            return True
    return False


def _has_m11_completion_claim(record: dict[str, Any]) -> bool:
    for item in _iter_text(record):
        if item == "m11_complete" or "m11 is complete" in item:
            return True
    return False


def _has_tracker_120_closure_claim(record: dict[str, Any]) -> bool:
    for item in _iter_text(record):
        if any(phrase in item for phrase in TRACKER_120_CLOSURE_PHRASES):
            return True
    return False


def _readiness_result(
    findings: list[str],
    missing_evidence: list[str],
    authority_boundary_violation: bool,
    expected_output_coverage_complete: bool,
    release_status_path_present: bool,
) -> dict[str, Any]:
    unique_findings = sorted(set(findings))
    unique_missing = sorted(set(missing_evidence))
    failed = bool(unique_findings or unique_missing or authority_boundary_violation)

    return {
        "m11_completion_readiness_valid": not failed,
        "m11_completion_readiness_invalid": failed,
        "expected_output_coverage_complete": expected_output_coverage_complete,
        "expected_output_coverage_incomplete": not expected_output_coverage_complete,
        "authority_boundary_preserved": not authority_boundary_violation,
        "authority_boundary_violation": authority_boundary_violation,
        "release_status_path_present": release_status_path_present,
        "release_status_path_missing": not release_status_path_present,
        "readiness_findings": unique_findings,
        "missing_evidence": unique_missing,
        "review_required": failed,
        "escalation_required": authority_boundary_violation,
        "fail_closed_recommended": authority_boundary_violation,
    }
