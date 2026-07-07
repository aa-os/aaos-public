"""Deterministic checks for M12 integration CI check specimens."""

from __future__ import annotations

from typing import Any


REQUIRED_SPECIMEN_FIELDS = {
    "specimen_id": "missing_specimen_id",
    "specimen_name": "missing_specimen_name",
    "specimen_scope": "missing_specimen_scope",
    "specimen_status": "missing_specimen_status",
    "m12_completion_status": "missing_m12_completion_status",
    "related_issue": "missing_related_issue_168",
    "tracker_issue_closure_state": "missing_tracker_issue_168_open_state",
    "tracker_issue_linkage": "missing_tracker_issue_168_reference",
    "first_m12_consumer_registry_pr": "missing_first_m12_consumer_registry_pr_169",
    "consumer_registry_pattern_artifact": "missing_consumer_registry_pattern_artifact",
    "consumer_registry_evaluator": "missing_consumer_registry_evaluator",
    "integration_ci_evaluator": "missing_integration_ci_evaluator",
    "target_future_release": "missing_target_future_release_v0_11_0",
    "release_status_path": "missing_release_status_path",
    "integration_ci_scope_statement": "missing_integration_ci_scope_statement",
    "integration_ci_check_catalog": "missing_integration_ci_check_catalog",
    "allowed_integration_ci_actions": "missing_allowed_integration_ci_actions",
    "forbidden_integration_ci_actions": "missing_forbidden_integration_ci_actions",
    "positive_ci_check_examples": "missing_positive_ci_check_examples",
    "negative_ci_check_examples": "missing_negative_ci_check_examples",
    "integration_ci_boundary_statement": "missing_integration_ci_boundary_statement",
    "registry_inclusion_boundary": "missing_registry_inclusion_boundary",
    "ci_pass_boundary": "missing_ci_pass_boundary",
    "release_proof_boundary": "missing_release_proof_boundary",
    "fail_closed_boundary": "missing_fail_closed_boundary",
    "sealing_eligibility_boundary": "missing_sealing_eligibility_boundary",
    "external_consumption_boundary": "missing_external_consumption_boundary",
    "decision_proof_sealing_boundary_statement": "missing_decision_proof_sealing_boundary_statement",
    "sovereignty_statement": "missing_sovereignty_statement",
    "allowed_evaluator_outputs": "missing_allowed_evaluator_outputs",
    "forbidden_evaluator_outputs": "missing_forbidden_evaluator_outputs",
}

REQUIRED_CHECK_CATALOG_KEYS = {
    "consumer_registry_required_fields",
    "compliant_consumer_registry_entries",
    "negative_consumer_registry_fixtures",
    "allowed_consumption_actions",
    "forbidden_authority_actions",
    "sealed_nonsealed_artifact_consumption_semantics",
    "registry_inclusion_boundary",
    "ci_pass_boundary",
    "release_proof_boundary",
    "fail_closed_boundary",
    "sealing_eligibility_boundary",
    "external_consumption_boundary",
    "decision_proof_sealing_boundary",
    "sovereignty_boundary",
}

REQUIRED_ALLOWED_CI_ACTIONS = {
    "check_registry_required_fields",
    "check_compliant_consumer_entries",
    "check_negative_consumer_fixtures",
    "check_allowed_consumption_actions",
    "check_forbidden_authority_actions",
    "check_sealed_nonsealed_semantics",
    "check_release_status_future_only",
    "surface_findings",
    "recommend_review_required",
    "recommend_escalation_required",
    "recommend_fail_closed_recommended",
}

REQUIRED_FORBIDDEN_CI_ACTIONS = {
    "approve_releases",
    "reject_releases_as_final_authority",
    "accept_risk",
    "execute_rollback",
    "execute_fail_closed",
    "seal_decision_proof",
    "close_audits",
    "grant_waivers",
    "make_final_governance_judgments",
}

REQUIRED_POSITIVE_OUTPUTS = {
    "integration_ci_check_passed",
    "consumer_registry_fields_valid",
    "compliant_consumer_entry_detected",
    "negative_fixture_detected",
    "authority_boundary_preserved",
    "sealed_nonsealed_semantics_preserved",
    "release_status_future_only",
    "review_not_required",
}

REQUIRED_NEGATIVE_SCENARIOS = {
    "missing_required_registry_fields",
    "consumer_attempts_to_seal_decision_proof",
    "registry_inclusion_as_approval",
    "ci_pass_as_approval",
    "release_proof_linkage_as_release_approval",
    "fail_closed_recommended_as_fail_closed_executed",
    "sealing_eligible_as_sealed",
    "v0_11_0_treated_as_released",
    "m12_treated_as_complete",
    "closes_168_language",
}

REQUIRED_EVALUATOR_OUTPUTS = {
    "integration_ci_specimen_valid",
    "integration_ci_specimen_invalid",
    "integration_ci_check_passed",
    "integration_ci_check_failed",
    "consumer_registry_fields_valid",
    "consumer_registry_fields_invalid",
    "authority_boundary_preserved",
    "authority_boundary_violation",
    "sealed_nonsealed_semantics_preserved",
    "release_status_future_only",
    "review_required",
    "escalation_required",
    "fail_closed_recommended",
}

FORBIDDEN_AUTHORITY_OUTPUTS = {
    "release_approved",
    "release_rejected_as_final_authority",
    "risk_accepted",
    "decision_proof_sealed",
    "sealed_by_ci",
    "sealed_by_registry",
    "sealed_by_external_consumer",
    "rollback_executed",
    "fail_closed_executed",
    "audit_closed",
    "waiver_granted",
    "final_governance_judgment",
    "v0_11_0_released",
    "m12_complete",
    "closes_168",
}

FORBIDDEN_AUTHORITY_PHRASES = {
    "integration ci approves release",
    "integration ci rejects release as final authority",
    "integration ci accepts risk",
    "integration ci executes rollback",
    "integration ci executes fail-closed",
    "integration ci seals decision proof",
    "integration ci closes audit",
    "integration ci grants waiver",
    "integration ci makes final governance judgment",
    "registry inclusion is approval",
    "ci pass is approval",
    "release proof linkage is release approval",
    "fail_closed_recommended is fail_closed_executed",
    "sealing_eligible is sealed",
    "v0.11.0 is released",
    "m12 is complete",
}

BOUNDARY_CLAIM_FINDINGS = {
    "registry inclusion is approval": "registry_inclusion_approval_claim_detected",
    "ci pass is approval": "ci_pass_approval_claim_detected",
    "release proof linkage is release approval": "release_proof_release_approval_claim_detected",
    "fail_closed_recommended is fail_closed_executed": "fail_closed_execution_claim_detected",
    "sealing_eligible is sealed": "sealing_eligibility_sealed_claim_detected",
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
    "forbidden_integration_ci_actions",
    "attempted_forbidden_output",
    "attempted_forbidden_outputs",
    "invalid_claim",
    "expected_ci_outputs",
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

    if parent_key in SAFE_NEGATIVE_CONTEXT_KEYS:
        return []

    return [_text(value)]


def _boundary_language(record: dict[str, Any]) -> str:
    return " ".join(
        [
            str(record.get("integration_ci_scope_statement", "")),
            str(record.get("integration_ci_boundary_statement", "")),
            str(record.get("registry_inclusion_boundary", "")),
            str(record.get("ci_pass_boundary", "")),
            str(record.get("release_proof_boundary", "")),
            str(record.get("fail_closed_boundary", "")),
            str(record.get("sealing_eligibility_boundary", "")),
            str(record.get("external_consumption_boundary", "")),
            str(record.get("decision_proof_sealing_boundary_statement", "")),
            str(record.get("sovereignty_statement", "")),
        ]
    ).lower()


def detect_integration_ci_forbidden_claims(
    value: Any, parent_key: str | None = None
) -> set[str]:
    claims: set[str] = set()

    if isinstance(value, dict):
        for key, item in value.items():
            claims.update(detect_integration_ci_forbidden_claims(item, str(key)))
        return claims

    if isinstance(value, list):
        for item in value:
            claims.update(detect_integration_ci_forbidden_claims(item, parent_key))
        return claims

    if parent_key in SAFE_NEGATIVE_CONTEXT_KEYS:
        return claims

    normalized = _text(value)
    if normalized in FORBIDDEN_AUTHORITY_OUTPUTS:
        claims.add(normalized)

    for phrase in FORBIDDEN_AUTHORITY_PHRASES:
        if phrase in normalized:
            claims.add(phrase)

    return claims


def evaluate_m12_integration_ci_check_specimen(record: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    authority_boundary_violation = False

    for field, finding in REQUIRED_SPECIMEN_FIELDS.items():
        if not _has_value(record, field):
            findings.append(finding)
            missing_evidence.append(field)

    if record.get("related_issue") != "#168":
        findings.append("missing_related_issue_168")
        missing_evidence.append("related_issue")
    if record.get("first_m12_consumer_registry_pr") != "#169":
        findings.append("missing_first_m12_consumer_registry_pr_169")
        missing_evidence.append("first_m12_consumer_registry_pr")

    tracker_state = _text(record.get("tracker_issue_closure_state"))
    if "open" not in tracker_state or tracker_state == "closed":
        findings.append("tracker_issue_168_not_marked_open")
        missing_evidence.append("tracker_issue_closure_state")
    if _has_tracker_168_closure_claim(record):
        findings.append("tracker_issue_168_closure_claim_detected")
        authority_boundary_violation = True

    release_status_future_only = _release_status_future_only(record)
    if not release_status_future_only:
        findings.append("v0_11_0_future_release_state_missing")
        missing_evidence.append("release_status_path")
    if _has_v0_11_0_release_claim(record):
        findings.append("v0_11_0_release_claim_detected")
        authority_boundary_violation = True
    if _has_m12_completion_claim(record):
        findings.append("m12_completion_claim_detected")
        authority_boundary_violation = True

    catalog = _as_dict(record.get("integration_ci_check_catalog"))
    if not REQUIRED_CHECK_CATALOG_KEYS <= set(catalog):
        findings.append("integration_ci_check_catalog_incomplete")
        missing_evidence.append("integration_ci_check_catalog")

    allowed_actions = _as_set(record.get("allowed_integration_ci_actions"))
    forbidden_actions = _as_set(record.get("forbidden_integration_ci_actions"))
    if not REQUIRED_ALLOWED_CI_ACTIONS <= allowed_actions:
        findings.append("allowed_integration_ci_actions_missing")
        missing_evidence.append("allowed_integration_ci_actions")
    if not REQUIRED_FORBIDDEN_CI_ACTIONS <= forbidden_actions:
        findings.append("forbidden_integration_ci_actions_missing")
        missing_evidence.append("forbidden_integration_ci_actions")
    if REQUIRED_FORBIDDEN_CI_ACTIONS & allowed_actions:
        findings.append("forbidden_integration_ci_action_allowed")
        authority_boundary_violation = True

    positive_examples = _positive_examples(record)
    negative_examples = _negative_examples(record)
    if not positive_examples:
        findings.append("positive_ci_check_example_missing")
        missing_evidence.append("positive_ci_check_examples")
    if not negative_examples:
        findings.append("negative_ci_check_examples_missing")
        missing_evidence.append("negative_ci_check_examples")

    for example in positive_examples:
        outputs = _as_set(example.get("ci_outputs"))
        if not REQUIRED_POSITIVE_OUTPUTS <= outputs:
            findings.append("positive_ci_outputs_missing")
            missing_evidence.append("positive_ci_check_examples.ci_outputs")
        if FORBIDDEN_AUTHORITY_OUTPUTS & outputs:
            findings.append("positive_ci_output_forbidden_authority_output_detected")
            authority_boundary_violation = True
        if detect_integration_ci_forbidden_claims(example):
            findings.append("positive_ci_output_authority_claim_detected")
            authority_boundary_violation = True

    negative_scenarios = {
        _text(example.get("scenario")) for example in negative_examples
    }
    if not REQUIRED_NEGATIVE_SCENARIOS <= negative_scenarios:
        findings.append("negative_ci_check_examples_incomplete")
        missing_evidence.append("negative_ci_check_examples")
    for example in negative_examples:
        if example.get("example_type") != "negative" or example.get("allowed_behavior") is not False:
            findings.append("negative_ci_example_not_marked_negative")
            missing_evidence.append("negative_ci_check_examples.allowed_behavior")
        if not _has_value(example, "negative_fixture_boundary"):
            findings.append("negative_ci_example_missing_boundary")
            missing_evidence.append("negative_ci_check_examples.negative_fixture_boundary")

    boundary_language = _boundary_language(record)
    sealed_nonsealed_semantics_preserved = _sealed_nonsealed_semantics_preserved(
        boundary_language
    )
    if not sealed_nonsealed_semantics_preserved:
        findings.append("sealed_nonsealed_semantics_missing")
        missing_evidence.append("sealed_nonsealed_boundary")

    for phrase, finding in BOUNDARY_CLAIM_FINDINGS.items():
        if phrase in boundary_language:
            findings.append(finding)
            authority_boundary_violation = True

    for required_phrase in [
        "deterministic evidence checks",
        "may surface findings",
        "review_required",
        "escalation_required",
        "fail_closed_recommended",
        "must not approve releases",
        "must not approve releases, reject releases as final authority",
        "execute fail-closed",
        "decision proof sealing remains aaos-owned",
        "aaos remains the decision sovereignty layer",
    ]:
        if required_phrase not in boundary_language:
            findings.append("missing_integration_ci_authority_boundary_statement")
            missing_evidence.append("integration_ci_boundary_statement")
            break

    allowed_outputs = _as_set(record.get("allowed_evaluator_outputs"))
    if not REQUIRED_EVALUATOR_OUTPUTS <= allowed_outputs:
        findings.append("missing_allowed_evaluator_outputs")
        missing_evidence.append("allowed_evaluator_outputs")
    if FORBIDDEN_AUTHORITY_OUTPUTS & allowed_outputs:
        findings.append("forbidden_evaluator_output_allowed")
        authority_boundary_violation = True

    claims = detect_integration_ci_forbidden_claims(record)
    if claims:
        findings.append("authority_transfer_claim_detected")
        authority_boundary_violation = True

    return _integration_ci_result(
        findings=findings,
        missing_evidence=missing_evidence,
        authority_boundary_violation=authority_boundary_violation,
        consumer_registry_fields_valid=not any(
            finding in findings for finding in REQUIRED_SPECIMEN_FIELDS.values()
        ),
        sealed_nonsealed_semantics_preserved=sealed_nonsealed_semantics_preserved,
        release_status_future_only=release_status_future_only,
    )


def _positive_examples(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        example
        for example in _as_list(record.get("positive_ci_check_examples"))
        if isinstance(example, dict)
        and example.get("example_type") == "positive"
        and example.get("allowed_behavior") is True
    ]


def _negative_examples(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        example
        for example in _as_list(record.get("negative_ci_check_examples"))
        if isinstance(example, dict)
    ]


def _release_status_future_only(record: dict[str, Any]) -> bool:
    release_status = _as_dict(record.get("release_status_path"))
    release_text = " ".join(_iter_claim_text(release_status))
    return (
        record.get("target_future_release") == "v0.11.0"
        and release_status.get("state") == "future_target_release_only"
        and "future target release" in release_text
        and "not be treated as released" in release_text
        and not _has_v0_11_0_release_claim(record)
    )


def _sealed_nonsealed_semantics_preserved(boundary_language: str) -> bool:
    return all(
        phrase in boundary_language
        for phrase in [
            "registry inclusion is not approval",
            "ci pass is not approval",
            "release proof linkage is not release approval",
            "fail_closed_recommended is not fail_closed_executed",
            "sealing_eligible is not sealed",
            "external consumption is not authority transfer",
            "decision proof sealing remains aaos-owned",
        ]
    )


def _has_v0_11_0_release_claim(record: dict[str, Any]) -> bool:
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


def _integration_ci_result(
    findings: list[str],
    missing_evidence: list[str],
    authority_boundary_violation: bool,
    consumer_registry_fields_valid: bool,
    sealed_nonsealed_semantics_preserved: bool,
    release_status_future_only: bool,
) -> dict[str, Any]:
    unique_findings = sorted(set(findings))
    unique_missing = sorted(set(missing_evidence))
    failed = bool(unique_findings or unique_missing or authority_boundary_violation)

    return {
        "integration_ci_specimen_valid": not failed,
        "integration_ci_specimen_invalid": failed,
        "integration_ci_check_passed": not failed,
        "integration_ci_check_failed": failed,
        "consumer_registry_fields_valid": consumer_registry_fields_valid,
        "consumer_registry_fields_invalid": not consumer_registry_fields_valid,
        "authority_boundary_preserved": not authority_boundary_violation,
        "authority_boundary_violation": authority_boundary_violation,
        "sealed_nonsealed_semantics_preserved": sealed_nonsealed_semantics_preserved,
        "release_status_future_only": release_status_future_only,
        "integration_ci_findings": unique_findings,
        "missing_evidence": unique_missing,
        "review_required": failed,
        "escalation_required": authority_boundary_violation,
        "fail_closed_recommended": authority_boundary_violation,
    }
