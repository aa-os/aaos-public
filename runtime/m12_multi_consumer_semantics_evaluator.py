"""Deterministic checks for M12 multi-consumer artifact semantics."""

from __future__ import annotations

from typing import Any


REQUIRED_ARTIFACT_FIELDS = {
    "artifact_id": "missing_artifact_id",
    "artifact_name": "missing_artifact_name",
    "artifact_scope": "missing_artifact_scope",
    "artifact_status": "missing_artifact_status",
    "m12_completion_status": "missing_m12_completion_status",
    "related_issue": "missing_related_issue_168",
    "tracker_issue_closure_state": "missing_tracker_issue_168_open_state",
    "tracker_issue_linkage": "missing_tracker_issue_168_reference",
    "m12_consumer_registry_pr": "missing_m12_consumer_registry_pr_169",
    "m12_integration_ci_check_specimen_pr": "missing_m12_integration_ci_check_specimen_pr_170",
    "m12_cross_consumer_traceability_pr": "missing_m12_cross_consumer_traceability_pr_172",
    "consumer_registry_pattern_artifact": "missing_consumer_registry_pattern_artifact",
    "integration_ci_check_specimen_ref": "missing_integration_ci_check_specimen_ref",
    "cross_consumer_traceability_examples_ref": "missing_cross_consumer_traceability_examples_ref",
    "multi_consumer_semantics_evaluator": "missing_multi_consumer_semantics_evaluator",
    "target_future_release": "missing_target_future_release_v0_11_0",
    "future_release_tag_path": "missing_future_release_tag_path",
    "release_status_path": "missing_release_status_path",
    "readme_release_status_path": "missing_readme_release_status_path",
    "semantics_scope_statement": "missing_semantics_scope_statement",
    "required_semantics": "missing_required_semantics",
    "artifact_status_semantics": "missing_artifact_status_semantics",
    "multi_consumer_matrix": "missing_multi_consumer_matrix",
    "negative_semantics_fixtures": "missing_negative_semantics_fixtures",
    "aaos_retained_authority_statement": "missing_aaos_retained_authority_statement",
    "governance_boundary_statement": "missing_governance_boundary_statement",
    "allowed_evaluator_outputs": "missing_allowed_evaluator_outputs",
    "forbidden_evaluator_outputs": "missing_forbidden_evaluator_outputs",
}

REQUIRED_SEMANTIC_KEYS = {
    "aaos_sealed_artifact_consumption",
    "aaos_sealed_artifact_reseal_boundary",
    "non_sealed_status_consumption",
    "non_sealed_conversion_boundary",
    "sealing_eligibility_boundary",
    "evidence_complete_boundary",
    "replay_ready_boundary",
    "evaluator_findings_boundary",
    "governance_ci_findings_boundary",
    "release_proof_boundary",
    "registry_inclusion_boundary",
    "ci_pass_boundary",
    "traceability_linkage_boundary",
    "external_consumption_boundary",
    "fail_closed_boundary",
    "decision_proof_sealing_boundary_statement",
    "sovereignty_statement",
}

REQUIRED_ARTIFACT_STATUSES = {
    "aaos_sealed_decision_proof_artifacts",
    "unsealed_evidence",
    "replay_ready_packets",
    "evidence_complete_packets",
    "evaluator_findings",
    "governance_ci_findings",
    "release_proof_evidence",
    "sealing_eligible_evidence",
    "sealing_rejected_artifacts",
    "sealing_deferred_artifacts",
    "sealing_blocked_artifacts",
}

REQUIRED_CONSUMER_TYPES = {
    "evidence_dashboard_consumer",
    "audit_export_consumer",
    "registry_observer_consumer",
}

REQUIRED_CONSUMER_FIELDS = {
    "consumer_type": "missing_consumer_type",
    "consumer_role": "missing_consumer_role",
    "consumer_registry_entry_ref": "missing_consumer_registry_entry_ref",
    "allowed_artifact_statuses": "missing_allowed_artifact_statuses",
    "allowed_consumption_actions": "missing_allowed_consumption_actions",
    "forbidden_authority_actions": "missing_forbidden_authority_actions",
    "sealed_artifact_handling": "missing_sealed_artifact_handling",
    "non_sealed_artifact_handling": "missing_non_sealed_artifact_handling",
    "sealing_eligibility_handling": "missing_sealing_eligibility_handling",
    "escalation_behavior": "missing_escalation_behavior",
    "fail_closed_recommendation_behavior": "missing_fail_closed_recommendation_behavior",
    "aaos_retained_authority_statement": "missing_consumer_aaos_retained_authority_statement",
}

REQUIRED_ALLOWED_CONSUMPTION_ACTIONS = {
    "read_artifacts",
    "reference_artifacts",
    "replay_replay_ready_packets",
    "inspect_evaluator_findings",
    "inspect_governance_ci_findings",
    "inspect_release_proof_evidence",
    "preserve_evidence_linkage",
    "preserve_release_proof_linkage",
    "surface_review_required",
    "surface_escalation_required",
    "surface_fail_closed_recommended",
}

REQUIRED_FORBIDDEN_AUTHORITY_ACTIONS = {
    "seal_decision_proof",
    "reseal_aaos_sealed_artifact",
    "convert_non_sealed_artifact_into_sealed_artifact",
    "convert_sealing_eligibility_into_final_sealing",
    "approve_releases",
    "accept_risk",
    "execute_rollback",
    "execute_fail_closed",
    "close_audits",
    "grant_waivers",
    "make_final_governance_judgments",
}

REQUIRED_NEGATIVE_SCENARIOS = {
    "consumer_reseals_aaos_sealed_artifact",
    "consumer_converts_non_sealed_artifact_into_sealed_artifact",
    "sealing_eligible_as_sealed",
    "evidence_complete_as_sealed",
    "replay_ready_as_sealed",
    "evaluator_findings_as_sealing",
    "governance_ci_findings_as_sealing",
    "release_proof_linkage_as_release_approval",
    "registry_inclusion_as_approval",
    "ci_pass_as_approval",
    "traceability_linkage_as_approval",
    "fail_closed_recommended_as_fail_closed_executed",
    "v0_11_0_treated_as_released",
    "m12_treated_as_complete",
    "closes_168_language",
    "final_governance_judgment_output",
    "audit_closed_output",
}

REQUIRED_NEGATIVE_FIXTURE_FIELDS = {
    "fixture_id": "missing_negative_fixture_id",
    "fixture_type": "missing_negative_fixture_type",
    "allowed_behavior": "missing_negative_fixture_allowed_behavior",
    "negative_fixture_boundary": "missing_negative_fixture_boundary",
    "scenario": "missing_negative_fixture_scenario",
    "expected_evaluator_outputs": "missing_expected_evaluator_outputs",
}

REQUIRED_EVALUATOR_OUTPUTS = {
    "multi_consumer_semantics_valid",
    "multi_consumer_semantics_invalid",
    "sealed_nonsealed_semantics_preserved",
    "sealed_nonsealed_semantics_violation",
    "consumer_matrix_complete",
    "consumer_matrix_incomplete",
    "authority_boundary_preserved",
    "authority_boundary_violation",
    "release_status_future_only",
    "review_required",
    "escalation_required",
    "fail_closed_recommended",
}

FORBIDDEN_EVALUATOR_OUTPUTS = {
    "decision_proof_sealed",
    "resealed_by_consumer",
    "sealed_by_consumer",
    "sealed_by_registry",
    "sealed_by_ci",
    "sealed_by_traceability",
    "release_approved",
    "risk_accepted",
    "rollback_executed",
    "fail_closed_executed",
    "audit_closed",
    "waiver_granted",
    "final_governance_judgment",
    "v0_11_0_released",
    "m12_complete",
    "closes_168",
}

BOUNDARY_CLAIM_FINDINGS = {
    "consumer re-seals aaos-sealed artifact": "consumer_reseals_aaos_sealed_artifact_detected",
    "consumer converts non-sealed artifact into sealed artifact": "consumer_converts_nonsealed_to_sealed_detected",
    "sealing_eligible is sealed": "sealing_eligibility_sealed_claim_detected",
    "evidence_complete is sealed": "evidence_complete_sealed_claim_detected",
    "replay_ready is sealed": "replay_ready_sealed_claim_detected",
    "evaluator findings are sealing": "evaluator_findings_sealing_claim_detected",
    "governance ci findings are sealing": "governance_ci_findings_sealing_claim_detected",
    "release proof linkage is release approval": "release_proof_release_approval_claim_detected",
    "registry inclusion is approval": "registry_inclusion_approval_claim_detected",
    "ci pass is approval": "ci_pass_approval_claim_detected",
    "traceability linkage is approval": "traceability_linkage_approval_claim_detected",
    "fail_closed_recommended is fail_closed_executed": "fail_closed_execution_claim_detected",
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

SAFE_NEGATIVE_CONTEXT_KEYS = {
    "forbidden_evaluator_outputs",
    "forbidden_authority_actions",
    "attempted_forbidden_action",
    "attempted_forbidden_actions",
    "attempted_forbidden_output",
    "attempted_forbidden_outputs",
    "invalid_claim",
    "expected_evaluator_outputs",
    "negative_fixture_boundary",
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
        return True
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

    if parent_key in SAFE_NEGATIVE_CONTEXT_KEYS:
        return []

    return [_text(value)]



def _boundary_language(record: dict[str, Any]) -> str:
    required_semantics = _as_dict(record.get("required_semantics"))
    return " ".join(
        [
            str(record.get("semantics_scope_statement", "")),
            " ".join(str(value) for value in required_semantics.values()),
            str(record.get("aaos_retained_authority_statement", "")),
            str(record.get("governance_boundary_statement", "")),
        ]
    ).lower()



def detect_multi_consumer_forbidden_claims(
    value: Any, parent_key: str | None = None
) -> set[str]:
    claims: set[str] = set()

    if isinstance(value, dict):
        for key, item in value.items():
            claims.update(detect_multi_consumer_forbidden_claims(item, str(key)))
        return claims

    if isinstance(value, list):
        for item in value:
            claims.update(detect_multi_consumer_forbidden_claims(item, parent_key))
        return claims

    if parent_key in SAFE_NEGATIVE_CONTEXT_KEYS:
        return claims

    normalized = _text(value)
    if normalized in FORBIDDEN_EVALUATOR_OUTPUTS:
        claims.add(normalized)

    for phrase in BOUNDARY_CLAIM_FINDINGS:
        if phrase in normalized:
            claims.add(phrase)

    return claims



def evaluate_m12_multi_consumer_semantics(record: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    authority_boundary_violation = False
    semantic_boundary_violation = False
    consumer_matrix_complete = True

    def add_missing(finding: str, evidence: str) -> None:
        nonlocal consumer_matrix_complete
        findings.append(finding)
        missing_evidence.append(evidence)
        consumer_matrix_complete = False

    for field, finding in REQUIRED_ARTIFACT_FIELDS.items():
        if not _has_value(record, field):
            add_missing(finding, field)

    if record.get("related_issue") != "#168":
        add_missing("missing_related_issue_168", "related_issue")
    if record.get("m12_consumer_registry_pr") != "#169":
        add_missing("missing_m12_consumer_registry_pr_169", "m12_consumer_registry_pr")
    if record.get("m12_integration_ci_check_specimen_pr") != "#170":
        add_missing(
            "missing_m12_integration_ci_check_specimen_pr_170",
            "m12_integration_ci_check_specimen_pr",
        )
    if record.get("m12_cross_consumer_traceability_pr") != "#172":
        add_missing(
            "missing_m12_cross_consumer_traceability_pr_172",
            "m12_cross_consumer_traceability_pr",
        )

    tracker_state = _text(record.get("tracker_issue_closure_state"))
    if "open" not in tracker_state or tracker_state == "closed":
        add_missing("tracker_issue_168_not_marked_open", "tracker_issue_closure_state")
    if _has_tracker_168_closure_claim(record):
        findings.append("tracker_issue_168_closure_claim_detected")
        authority_boundary_violation = True

    release_status_future_only = _release_status_future_only(record)
    if not release_status_future_only:
        add_missing("v0_11_0_future_release_state_missing", "release_status_path")
    if _has_v0_11_0_release_claim(record):
        findings.append("v0_11_0_release_claim_detected")
        authority_boundary_violation = True
    if _has_m12_completion_claim(record):
        findings.append("m12_completion_claim_detected")
        authority_boundary_violation = True

    if "m12-consumer-registry-pattern.json" not in str(
        record.get("consumer_registry_pattern_artifact", "")
    ):
        add_missing(
            "consumer_registry_pattern_linkage_missing",
            "consumer_registry_pattern_artifact",
        )
    if "m12-integration-ci-check-specimen.json" not in str(
        record.get("integration_ci_check_specimen_ref", "")
    ):
        add_missing(
            "integration_ci_check_specimen_linkage_missing",
            "integration_ci_check_specimen_ref",
        )
    if "m12-cross-consumer-traceability-examples.json" not in str(
        record.get("cross_consumer_traceability_examples_ref", "")
    ):
        add_missing(
            "cross_consumer_traceability_examples_linkage_missing",
            "cross_consumer_traceability_examples_ref",
        )

    required_semantics = _as_dict(record.get("required_semantics"))
    if not REQUIRED_SEMANTIC_KEYS <= set(required_semantics):
        add_missing("required_semantics_incomplete", "required_semantics")

    status_semantics = _as_dict(record.get("artifact_status_semantics"))
    if not REQUIRED_ARTIFACT_STATUSES <= set(status_semantics):
        add_missing("artifact_status_semantics_incomplete", "artifact_status_semantics")
    _evaluate_artifact_status_semantics(status_semantics, findings, missing_evidence)

    matrix = _as_list(record.get("multi_consumer_matrix"))
    matrix_complete, matrix_authority_violation = _evaluate_consumer_matrix(
        matrix, findings, missing_evidence
    )
    consumer_matrix_complete = consumer_matrix_complete and matrix_complete
    authority_boundary_violation = authority_boundary_violation or matrix_authority_violation

    _evaluate_negative_fixtures(
        _as_list(record.get("negative_semantics_fixtures")),
        findings,
        missing_evidence,
    )

    boundary_language = _boundary_language(record)
    sealed_nonsealed_semantics_preserved = _sealed_nonsealed_semantics_preserved(
        boundary_language
    )
    if not sealed_nonsealed_semantics_preserved:
        findings.append("sealed_nonsealed_semantics_missing")
        missing_evidence.append("required_semantics")
        semantic_boundary_violation = True

    for phrase, finding in BOUNDARY_CLAIM_FINDINGS.items():
        if phrase in boundary_language:
            findings.append(finding)
            semantic_boundary_violation = True
            authority_boundary_violation = True

    for required_phrase in [
        "evidence consumption rules only",
        "must not seal decision proof",
        "re-seal aaos-sealed artifacts",
        "convert non-sealed artifacts into sealed artifacts",
        "convert sealing eligibility into final sealing",
        "approve releases",
        "execute fail-closed",
        "decision proof sealing remains aaos-owned",
        "aaos retains",
        "aaos remains the decision sovereignty layer",
    ]:
        if required_phrase not in boundary_language:
            findings.append("missing_aaos_authority_boundary_statement")
            missing_evidence.append("aaos_retained_authority_statement")
            break

    allowed_outputs = _as_set(record.get("allowed_evaluator_outputs"))
    if not REQUIRED_EVALUATOR_OUTPUTS <= allowed_outputs:
        findings.append("missing_allowed_evaluator_outputs")
        missing_evidence.append("allowed_evaluator_outputs")
    if FORBIDDEN_EVALUATOR_OUTPUTS & allowed_outputs:
        findings.append("forbidden_evaluator_output_allowed")
        authority_boundary_violation = True

    claims = detect_multi_consumer_forbidden_claims(record)
    if claims:
        findings.append("authority_transfer_claim_detected")
        authority_boundary_violation = True
        if any(claim in BOUNDARY_CLAIM_FINDINGS for claim in claims):
            semantic_boundary_violation = True

    return _semantics_result(
        findings=findings,
        missing_evidence=missing_evidence,
        semantic_boundary_violation=semantic_boundary_violation,
        authority_boundary_violation=authority_boundary_violation,
        consumer_matrix_complete=consumer_matrix_complete,
        release_status_future_only=release_status_future_only,
    )



def _evaluate_artifact_status_semantics(
    status_semantics: dict[str, Any],
    findings: list[str],
    missing_evidence: list[str],
) -> None:
    for status in REQUIRED_ARTIFACT_STATUSES:
        entry = _as_dict(status_semantics.get(status))
        if not _has_value(entry, "artifact_status") or not _has_value(
            entry, "consumer_handling"
        ):
            findings.append("artifact_status_handling_missing")
            missing_evidence.append(f"artifact_status_semantics.{status}")

    sealed_entry = _as_dict(status_semantics.get("aaos_sealed_decision_proof_artifacts"))
    if sealed_entry.get("sealed") is not True or sealed_entry.get("consumer_may_reseal") is not False:
        findings.append("sealed_artifact_handling_missing")
        missing_evidence.append(
            "artifact_status_semantics.aaos_sealed_decision_proof_artifacts"
        )

    for status in REQUIRED_ARTIFACT_STATUSES - {"aaos_sealed_decision_proof_artifacts"}:
        entry = _as_dict(status_semantics.get(status))
        if entry.get("sealed") is not False:
            findings.append("non_sealed_artifact_handling_missing")
            missing_evidence.append(f"artifact_status_semantics.{status}")



def _evaluate_consumer_matrix(
    matrix: list[Any],
    findings: list[str],
    missing_evidence: list[str],
) -> tuple[bool, bool]:
    complete = True
    authority_violation = False
    typed_entries = [entry for entry in matrix if isinstance(entry, dict)]
    consumer_types = {_text(entry.get("consumer_type")) for entry in typed_entries}

    if len(typed_entries) < 3 or not REQUIRED_CONSUMER_TYPES <= consumer_types:
        findings.append("consumer_matrix_incomplete")
        missing_evidence.append("multi_consumer_matrix")
        complete = False

    for entry in typed_entries:
        entry_complete, entry_authority_violation = _evaluate_consumer_entry(
            entry, findings, missing_evidence
        )
        complete = complete and entry_complete
        authority_violation = authority_violation or entry_authority_violation

    return complete, authority_violation



def _evaluate_consumer_entry(
    entry: dict[str, Any],
    findings: list[str],
    missing_evidence: list[str],
) -> tuple[bool, bool]:
    complete = True
    authority_violation = False

    def add_missing(finding: str, evidence: str) -> None:
        nonlocal complete
        findings.append(finding)
        missing_evidence.append(evidence)
        complete = False

    for field, finding in REQUIRED_CONSUMER_FIELDS.items():
        if not _has_value(entry, field):
            add_missing(finding, f"multi_consumer_matrix.{field}")

    statuses = _as_set(entry.get("allowed_artifact_statuses"))
    if "aaos_sealed_decision_proof_artifacts" not in statuses:
        add_missing("sealed_artifact_status_missing", "multi_consumer_matrix.allowed_artifact_statuses")
    if not (REQUIRED_ARTIFACT_STATUSES - {"aaos_sealed_decision_proof_artifacts"}) & statuses:
        add_missing("nonsealed_artifact_status_missing", "multi_consumer_matrix.allowed_artifact_statuses")

    allowed_actions = _as_set(entry.get("allowed_consumption_actions"))
    forbidden_actions = _as_set(entry.get("forbidden_authority_actions"))
    if not REQUIRED_ALLOWED_CONSUMPTION_ACTIONS <= allowed_actions:
        add_missing("allowed_consumption_actions_missing", "multi_consumer_matrix.allowed_consumption_actions")
    if not REQUIRED_FORBIDDEN_AUTHORITY_ACTIONS <= forbidden_actions:
        add_missing("forbidden_authority_actions_missing", "multi_consumer_matrix.forbidden_authority_actions")
    if REQUIRED_FORBIDDEN_AUTHORITY_ACTIONS & allowed_actions:
        findings.append("forbidden_authority_action_allowed")
        authority_violation = True

    sealed_handling = _text(entry.get("sealed_artifact_handling"))
    if (
        "aaos-sealed artifacts" not in sealed_handling
        or "must not be re-sealed by consumers" not in sealed_handling
    ):
        add_missing("sealed_artifact_handling_missing", "multi_consumer_matrix.sealed_artifact_handling")

    nonsealed_handling = _text(entry.get("non_sealed_artifact_handling"))
    if (
        "non-sealed artifacts" not in nonsealed_handling
        or "must not be converted into sealed artifacts" not in nonsealed_handling
    ):
        add_missing("non_sealed_artifact_handling_missing", "multi_consumer_matrix.non_sealed_artifact_handling")

    eligibility_handling = _text(entry.get("sealing_eligibility_handling"))
    if "sealing_eligible is not sealed" not in eligibility_handling:
        add_missing("sealing_eligibility_handling_missing", "multi_consumer_matrix.sealing_eligibility_handling")

    if "must not execute fail-closed" not in _text(entry.get("fail_closed_recommendation_behavior")):
        add_missing(
            "fail_closed_recommendation_boundary_missing",
            "multi_consumer_matrix.fail_closed_recommendation_behavior",
        )

    outputs = _as_set(entry.get("semantics_outputs"))
    if FORBIDDEN_EVALUATOR_OUTPUTS & outputs:
        findings.append("semantics_output_forbidden_authority_output_detected")
        authority_violation = True

    if detect_multi_consumer_forbidden_claims(entry):
        findings.append("consumer_semantics_authority_claim_detected")
        authority_violation = True

    return complete, authority_violation



def _evaluate_negative_fixtures(
    fixtures: list[Any],
    findings: list[str],
    missing_evidence: list[str],
) -> None:
    typed_fixtures = [fixture for fixture in fixtures if isinstance(fixture, dict)]
    scenarios = {_text(fixture.get("scenario")) for fixture in typed_fixtures}
    if not REQUIRED_NEGATIVE_SCENARIOS <= scenarios:
        findings.append("negative_semantics_fixtures_incomplete")
        missing_evidence.append("negative_semantics_fixtures")

    for fixture in typed_fixtures:
        for field, finding in REQUIRED_NEGATIVE_FIXTURE_FIELDS.items():
            if not _has_value(fixture, field):
                findings.append(finding)
                missing_evidence.append(f"negative_semantics_fixtures.{field}")
        if fixture.get("fixture_type") != "negative" or fixture.get("allowed_behavior") is not False:
            findings.append("negative_fixture_not_marked_negative")
            missing_evidence.append("negative_semantics_fixtures.allowed_behavior")



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



def _sealed_nonsealed_semantics_preserved(boundary_language: str) -> bool:
    return all(
        phrase in boundary_language
        for phrase in [
            "aaos-sealed artifacts may be consumed as aaos-sealed artifacts",
            "aaos-sealed artifacts must not be re-sealed by consumers",
            "non-sealed artifacts may be consumed only according to their status",
            "non-sealed artifacts must not be converted into sealed artifacts",
            "sealing_eligible is not sealed",
            "evidence_complete is not sealed",
            "replay_ready is not sealed",
            "evaluator_findings are not sealing",
            "governance ci findings are not sealing",
            "release proof linkage is not release approval",
            "registry inclusion is not approval",
            "ci pass is not approval",
            "traceability linkage is not approval",
            "external consumption is not authority transfer",
            "fail_closed_recommended is not fail_closed_executed",
            "decision proof sealing remains aaos-owned",
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



def _semantics_result(
    findings: list[str],
    missing_evidence: list[str],
    semantic_boundary_violation: bool,
    authority_boundary_violation: bool,
    consumer_matrix_complete: bool,
    release_status_future_only: bool,
) -> dict[str, Any]:
    unique_findings = sorted(set(findings))
    unique_missing = sorted(set(missing_evidence))
    sealed_nonsealed_semantics_preserved = not semantic_boundary_violation
    failed = bool(unique_findings or unique_missing or authority_boundary_violation)

    return {
        "multi_consumer_semantics_valid": not failed,
        "multi_consumer_semantics_invalid": failed,
        "sealed_nonsealed_semantics_preserved": sealed_nonsealed_semantics_preserved,
        "sealed_nonsealed_semantics_violation": not sealed_nonsealed_semantics_preserved,
        "consumer_matrix_complete": consumer_matrix_complete,
        "consumer_matrix_incomplete": not consumer_matrix_complete,
        "authority_boundary_preserved": not authority_boundary_violation,
        "authority_boundary_violation": authority_boundary_violation,
        "release_status_future_only": release_status_future_only,
        "semantics_findings": unique_findings,
        "missing_evidence": unique_missing,
        "review_required": failed,
        "escalation_required": authority_boundary_violation,
        "fail_closed_recommended": authority_boundary_violation,
    }
