"""Deterministic checks for M13 registry drift detection evidence."""

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
    "closed_runtime_approval_follow_up": "missing_closed_runtime_approval_follow_up_171",
    "closed_runtime_approval_follow_up_state": "missing_closed_runtime_approval_follow_up_state",
    "introduced_after_release": "missing_introduced_after_release_v0_11_0",
    "target_future_release": "missing_target_future_release_v0_12_0",
    "future_release_tag_path": "missing_future_release_tag_path",
    "release_status_path": "missing_release_status_path",
    "m12_reference_artifacts": "missing_m12_reference_artifacts",
    "m13_reference_artifacts": "missing_m13_reference_artifacts",
    "drift_detection_scope_statement": "missing_drift_detection_scope_statement",
    "drift_types": "missing_drift_types",
    "allowed_drift_outcomes": "missing_allowed_drift_outcomes",
    "forbidden_drift_outcomes": "missing_forbidden_drift_outcomes",
    "positive_drift_examples": "missing_positive_drift_examples",
    "negative_drift_fixtures": "missing_negative_drift_fixtures",
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
    "runtime_approval_gate_evaluator",
}

REQUIRED_DRIFT_TYPES = {
    "consumer_identity_drift",
    "consumer_role_drift",
    "consumed_artifact_type_drift",
    "allowed_consumption_action_drift",
    "forbidden_authority_action_drift",
    "sealed_artifact_handling_drift",
    "non_sealed_artifact_handling_drift",
    "sealing_eligibility_semantics_drift",
    "replay_compatibility_drift",
    "evaluator_compatibility_drift",
    "integration_ci_compatibility_drift",
    "release_proof_linkage_drift",
    "registry_provenance_drift",
    "registry_version_drift",
    "authority_boundary_drift",
    "aaos_retained_authority_statement_drift",
}

REQUIRED_NEGATIVE_FIXTURES = {
    "registry_inclusion_as_approval",
    "no_drift_detected_as_release_approval",
    "fail_closed_recommended_as_fail_closed_executed",
    "sealing_eligible_as_sealed",
    "non_sealed_artifact_converted_into_sealed_artifact",
    "aaos_sealed_artifact_resealed_by_registry",
    "authority_transferred_to_external_consumer",
    "final_governance_judgment_output",
    "audit_closed_output",
    "v0_12_0_treated_as_released",
    "m13_treated_as_complete",
    "closes_176_language",
}

REQUIRED_ALLOWED_OUTCOMES = {
    "no_drift_detected",
    "registry_drift_detected",
    "consumer_identity_drift_detected",
    "consumer_role_drift_detected",
    "artifact_scope_drift_detected",
    "allowed_action_drift_detected",
    "forbidden_authority_action_drift_detected",
    "sealed_nonsealed_semantics_drift_detected",
    "replay_compatibility_drift_detected",
    "evaluator_compatibility_drift_detected",
    "integration_ci_compatibility_drift_detected",
    "release_proof_linkage_drift_detected",
    "registry_provenance_drift_detected",
    "authority_boundary_drift_detected",
    "review_required",
    "escalation_required",
    "fail_closed_recommended",
}

FORBIDDEN_DRIFT_OUTCOMES = {
    "registry_entry_approved",
    "consumer_approved",
    "release_approved",
    "risk_accepted",
    "decision_proof_sealed",
    "sealed_by_registry",
    "sealed_by_consumer",
    "sealed_by_ci",
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

REQUIRED_ALLOWED_EVALUATOR_OUTPUTS = {
    "registry_drift_specimen_valid",
    "registry_drift_specimen_invalid",
    "no_drift_detected",
    "registry_drift_detected",
    "drift_type_coverage_complete",
    "drift_type_coverage_incomplete",
    "authority_boundary_preserved",
    "authority_boundary_violation",
    "release_status_future_only",
    "review_required",
    "escalation_required",
    "fail_closed_recommended",
}

REQUIRED_AUTHORITY_MAY = {
    "detect_drift",
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
    "no_drift_detected is release approval": "no_drift_release_approval_claim_detected",
    "fail_closed_recommended is fail_closed_executed": "fail_closed_execution_claim_detected",
    "sealing_eligible is sealed": "sealing_eligibility_sealed_claim_detected",
    "converts non-sealed artifact into sealed artifact": "nonsealed_to_sealed_conversion_claim_detected",
    "converted non-sealed artifact into sealed artifact": "nonsealed_to_sealed_conversion_claim_detected",
    "re-seals aaos-sealed artifact": "aaos_sealed_reseal_claim_detected",
    "resealed aaos-sealed artifact": "aaos_sealed_reseal_claim_detected",
    "authority transferred to external consumer": "authority_transfer_to_external_consumer_claim_detected",
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
    "allowed_drift_outcomes",
    "forbidden_drift_outcomes",
    "allowed_evaluator_outputs",
    "forbidden_evaluator_outputs",
    "authority_boundary",
    "must_not",
    "negative_drift_fixtures",
    "negative_fixture_boundary",
    "attempted_forbidden_output",
    "attempted_forbidden_outputs",
    "expected_evaluator_outputs",
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



def detect_registry_drift_forbidden_claims(value: Any, parent_key: str | None = None) -> set[str]:
    claims: set[str] = set()

    if parent_key in SAFE_CONTEXT_KEYS:
        return claims

    if isinstance(value, dict):
        for key, item in value.items():
            claims.update(detect_registry_drift_forbidden_claims(item, str(key)))
        return claims

    if isinstance(value, list):
        for item in value:
            claims.update(detect_registry_drift_forbidden_claims(item, parent_key))
        return claims

    normalized = _text(value)
    if normalized in FORBIDDEN_DRIFT_OUTCOMES:
        claims.add(normalized)
    for phrase in BOUNDARY_CLAIM_FINDINGS:
        if phrase in normalized:
            claims.add(phrase)
    return claims



def evaluate_registry_drift_specimen(specimen: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    authority_boundary_violation = False

    def add_missing(finding: str, evidence: str) -> None:
        findings.append(finding)
        missing_evidence.append(evidence)

    if not specimen:
        add_missing("registry_drift_specimen_missing", "specimen")

    for field, finding in REQUIRED_SPECIMEN_FIELDS.items():
        if not _has_value(specimen, field):
            add_missing(finding, field)

    if specimen.get("related_issue") != "#176":
        add_missing("missing_related_issue_176", "related_issue")
    if specimen.get("runtime_approval_gate_evidence_pr") != "#177":
        add_missing("missing_runtime_approval_gate_evidence_pr_177", "runtime_approval_gate_evidence_pr")
    if specimen.get("closed_runtime_approval_follow_up") != "#171":
        add_missing("missing_closed_runtime_approval_follow_up_171", "closed_runtime_approval_follow_up")
    if specimen.get("closed_runtime_approval_follow_up_state") != "closed_by_177":
        add_missing("missing_closed_runtime_approval_follow_up_state", "closed_runtime_approval_follow_up_state")

    tracker_state = _text(specimen.get("tracker_issue_closure_state"))
    if "open" not in tracker_state or tracker_state == "closed":
        add_missing("tracker_issue_176_not_marked_open", "tracker_issue_closure_state")
    if _has_tracker_176_closure_claim(specimen):
        findings.append("tracker_issue_176_closure_claim_detected")
        authority_boundary_violation = True

    release_status_future_only = _release_status_future_only(specimen)
    if not release_status_future_only:
        add_missing("release_status_future_only_missing", "release_status_path")
    if _has_v0_12_0_release_claim(specimen):
        findings.append("v0_12_0_release_claim_detected")
        authority_boundary_violation = True
    if _has_m13_completion_claim(specimen):
        findings.append("m13_completion_claim_detected")
        authority_boundary_violation = True

    if not REQUIRED_M12_REFS <= set(_as_dict(specimen.get("m12_reference_artifacts"))):
        add_missing("m12_reference_artifacts_missing", "m12_reference_artifacts")
    if not REQUIRED_M13_REFS <= set(_as_dict(specimen.get("m13_reference_artifacts"))):
        add_missing("m13_reference_artifacts_missing", "m13_reference_artifacts")

    drift_type_coverage_complete = _drift_type_coverage_complete(specimen)
    if not drift_type_coverage_complete:
        add_missing("drift_type_coverage_incomplete", "drift_types")

    no_drift_example_present = _no_drift_example_present(specimen)
    if not no_drift_example_present:
        add_missing("no_drift_positive_example_missing", "positive_drift_examples")

    drift_detected_example_present = _drift_detected_example_present(specimen)
    if not drift_detected_example_present:
        add_missing("drift_detected_positive_example_missing", "positive_drift_examples")

    if not _negative_fixture_coverage_complete(specimen):
        add_missing("negative_fixture_coverage_incomplete", "negative_drift_fixtures")
    _evaluate_negative_fixture_marking(specimen, findings, missing_evidence)

    if not REQUIRED_ALLOWED_OUTCOMES <= _as_set(specimen.get("allowed_drift_outcomes")):
        add_missing("allowed_drift_outcomes_missing", "allowed_drift_outcomes")
    if not FORBIDDEN_DRIFT_OUTCOMES <= _as_set(specimen.get("forbidden_drift_outcomes")):
        add_missing("forbidden_drift_outcomes_missing", "forbidden_drift_outcomes")
    if not REQUIRED_ALLOWED_EVALUATOR_OUTPUTS <= _as_set(specimen.get("allowed_evaluator_outputs")):
        add_missing("allowed_evaluator_outputs_missing", "allowed_evaluator_outputs")
    if not FORBIDDEN_DRIFT_OUTCOMES <= _as_set(specimen.get("forbidden_evaluator_outputs")):
        add_missing("forbidden_evaluator_outputs_missing", "forbidden_evaluator_outputs")

    if not _authority_boundary_complete(specimen):
        add_missing("authority_boundary_statement_incomplete", "authority_boundary")

    boundary_language = _boundary_language(specimen)
    if not _required_boundary_language_present(boundary_language):
        add_missing("missing_aaos_authority_boundary_statement", "aaos_retained_authority_statement")
    for phrase, finding in BOUNDARY_CLAIM_FINDINGS.items():
        if phrase in boundary_language:
            findings.append(finding)
            authority_boundary_violation = True

    forbidden_claims = detect_registry_drift_forbidden_claims(specimen)
    if forbidden_claims:
        findings.append("authority_transfer_claim_detected")
        authority_boundary_violation = True

    return _registry_drift_result(
        findings=findings,
        missing_evidence=missing_evidence,
        authority_boundary_violation=authority_boundary_violation,
        drift_type_coverage_complete=drift_type_coverage_complete,
        no_drift_detected=no_drift_example_present,
        registry_drift_detected=drift_detected_example_present,
        release_status_future_only=release_status_future_only,
    )



def _drift_type_coverage_complete(specimen: dict[str, Any]) -> bool:
    drift_type_ids = {
        _text(item.get("drift_type_id"))
        for item in _as_list(specimen.get("drift_types"))
        if isinstance(item, dict)
    }
    return REQUIRED_DRIFT_TYPES <= drift_type_ids



def _no_drift_example_present(specimen: dict[str, Any]) -> bool:
    for example in _as_list(specimen.get("positive_drift_examples")):
        if not isinstance(example, dict):
            continue
        expected_outputs = _as_set(example.get("expected_outputs"))
        if (
            example.get("example_id") == "no_drift_detected_external_evidence_dashboard_consumer"
            and example.get("example_type") == "positive_no_drift"
            and example.get("drift_detected") is False
            and example.get("authority_action_executed") is False
            and example.get("baseline_state_hash") == example.get("current_state_hash")
            and {"no_drift_detected", "authority_boundary_preserved", "release_status_future_only"} <= expected_outputs
        ):
            return True
    return False



def _drift_detected_example_present(specimen: dict[str, Any]) -> bool:
    for example in _as_list(specimen.get("positive_drift_examples")):
        if not isinstance(example, dict):
            continue
        expected_outputs = _as_set(example.get("expected_outputs"))
        if (
            example.get("example_id") == "drift_detected_authority_preserved_audit_export_consumer"
            and example.get("example_type") == "positive_drift_detected_authority_preserved"
            and example.get("drift_detected") is True
            and bool(_as_list(example.get("detected_drift_types")))
            and example.get("authority_action_executed") is False
            and {
                "registry_drift_detected",
                "review_required",
                "escalation_required",
                "fail_closed_recommended",
                "authority_boundary_preserved",
            }
            <= expected_outputs
        ):
            return True
    return False



def _negative_fixture_coverage_complete(specimen: dict[str, Any]) -> bool:
    fixture_ids = {
        str(item.get("fixture_id"))
        for item in _as_list(specimen.get("negative_drift_fixtures"))
        if isinstance(item, dict)
    }
    return REQUIRED_NEGATIVE_FIXTURES <= fixture_ids



def _evaluate_negative_fixture_marking(
    specimen: dict[str, Any],
    findings: list[str],
    missing_evidence: list[str],
) -> None:
    for fixture in _as_list(specimen.get("negative_drift_fixtures")):
        if not isinstance(fixture, dict):
            continue
        fixture_id = str(fixture.get("fixture_id", "unknown_negative_fixture"))
        if fixture.get("negative_fixture") is not True or fixture.get("allowed_behavior") is not False:
            findings.append(f"negative_fixture_unmarked_{fixture_id}")
            missing_evidence.append(f"negative_drift_fixtures.{fixture_id}")
        if not _has_value(fixture, "negative_fixture_boundary"):
            findings.append(f"negative_fixture_boundary_missing_{fixture_id}")
            missing_evidence.append(f"negative_drift_fixtures.{fixture_id}.negative_fixture_boundary")



def _release_status_future_only(specimen: dict[str, Any]) -> bool:
    release_status = _as_dict(specimen.get("release_status_path"))
    future_tag = _as_dict(specimen.get("future_release_tag_path"))
    return (
        specimen.get("target_future_release") == "v0.12.0"
        and release_status.get("state") == "future_target_release_only"
        and future_tag.get("target_tag") == "v0.12.0"
        and future_tag.get("state") == "future_tag_path_only"
        and future_tag.get("released") is False
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
        str(specimen.get("drift_detection_scope_statement", "")),
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
            "registry drift detection is evidence checking only",
            "must not approve consumers",
            "registry inclusion is not approval",
            "no_drift_detected is not approval",
            "fail_closed_recommended is not fail_closed_executed",
            "sealing_eligible is not sealed",
            "not converted into sealed artifacts",
            "not re-sealed by consumers or registry checks",
            "decision proof sealing remains aaos-owned",
            "aaos retains",
            "aaos remains the decision sovereignty layer",
        ]
    )



def _has_tracker_176_closure_claim(specimen: dict[str, Any]) -> bool:
    for item in _iter_claim_text(specimen):
        if item == "closes_176" or any(phrase in item for phrase in TRACKER_176_CLOSURE_PHRASES):
            return True
    return False



def _has_v0_12_0_release_claim(specimen: dict[str, Any]) -> bool:
    if _as_dict(specimen.get("future_release_tag_path")).get("released") is True:
        return True
    for item in _iter_claim_text(specimen):
        if item == "v0_12_0_released" or "v0.12.0 is released" in item:
            return True
    return False



def _has_m13_completion_claim(specimen: dict[str, Any]) -> bool:
    for item in _iter_claim_text(specimen):
        if item == "m13_complete":
            return True
        if "m13 is complete" in item and "not complete" not in item:
            return True
    return False



def _registry_drift_result(
    findings: list[str],
    missing_evidence: list[str],
    authority_boundary_violation: bool,
    drift_type_coverage_complete: bool,
    no_drift_detected: bool,
    registry_drift_detected: bool,
    release_status_future_only: bool,
) -> dict[str, Any]:
    unique_findings = sorted(set(findings))
    unique_missing = sorted(set(missing_evidence))
    failed = bool(unique_findings or unique_missing or authority_boundary_violation)

    return {
        "registry_drift_specimen_valid": not failed,
        "registry_drift_specimen_invalid": failed,
        "no_drift_detected": no_drift_detected,
        "registry_drift_detected": registry_drift_detected,
        "drift_type_coverage_complete": drift_type_coverage_complete,
        "drift_type_coverage_incomplete": not drift_type_coverage_complete,
        "authority_boundary_preserved": not authority_boundary_violation,
        "authority_boundary_violation": authority_boundary_violation,
        "release_status_future_only": release_status_future_only,
        "registry_drift_findings": unique_findings,
        "missing_evidence": unique_missing,
        "review_required": failed,
        "escalation_required": authority_boundary_violation,
        "fail_closed_recommended": authority_boundary_violation,
    }
