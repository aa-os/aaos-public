"""Deterministic checks for M12 cross-consumer traceability evidence."""

from __future__ import annotations

from typing import Any


REQUIRED_TRACEABILITY_FIELDS = {
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
    "public_integration_pack_ref": "missing_public_integration_pack_ref",
    "consumer_registry_pattern_artifact": "missing_consumer_registry_pattern_artifact",
    "integration_ci_check_specimen_ref": "missing_integration_ci_check_specimen_ref",
    "integration_ci_check_reference": "missing_integration_ci_check_reference",
    "cross_consumer_traceability_evaluator": "missing_cross_consumer_traceability_evaluator",
    "target_future_release": "missing_target_future_release_v0_11_0",
    "future_release_tag_path": "missing_future_release_tag_path",
    "release_status_path": "missing_release_status_path",
    "release_proof_linkage": "missing_release_proof_linkage",
    "readme_release_status_path": "missing_readme_release_status_path",
    "traceability_scope_statement": "missing_traceability_scope_statement",
    "evidence_linkage_only_statement": "missing_evidence_linkage_only_statement",
    "compliant_consumer_traceability_examples": "missing_compliant_consumer_traceability_examples",
    "negative_cross_consumer_traceability_fixtures": "missing_negative_cross_consumer_traceability_fixtures",
    "registry_inclusion_boundary": "missing_registry_inclusion_boundary",
    "ci_pass_boundary": "missing_ci_pass_boundary",
    "release_proof_boundary": "missing_release_proof_boundary",
    "fail_closed_boundary": "missing_fail_closed_boundary",
    "sealing_eligibility_boundary": "missing_sealing_eligibility_boundary",
    "nonsealed_conversion_boundary": "missing_nonsealed_conversion_boundary",
    "decision_proof_sealing_boundary_statement": "missing_decision_proof_sealing_boundary_statement",
    "aaos_retained_authority_statement": "missing_aaos_retained_authority_statement",
    "sovereignty_statement": "missing_sovereignty_statement",
    "allowed_evaluator_outputs": "missing_allowed_evaluator_outputs",
    "forbidden_evaluator_outputs": "missing_forbidden_evaluator_outputs",
}

REQUIRED_COMPLIANT_EXAMPLE_FIELDS = {
    "example_id": "missing_example_id",
    "example_type": "missing_example_type",
    "allowed_behavior": "missing_example_allowed_behavior",
    "consumer_identity": "missing_consumer_identity",
    "consumer_role": "missing_consumer_role",
    "consumer_registry_entry_ref": "missing_consumer_registry_entry_ref",
    "public_integration_pack_ref": "missing_example_public_integration_pack_ref",
    "consumed_artifact_statuses": "missing_consumed_artifact_statuses",
    "consumed_sealed_artifact": "missing_consumed_sealed_artifact",
    "consumed_non_sealed_artifact": "missing_consumed_non_sealed_artifact",
    "evidence_schema_reference": "missing_evidence_schema_reference",
    "replay_packet_reference": "missing_replay_packet_reference",
    "evaluator_output_reference": "missing_evaluator_output_reference",
    "integration_ci_check_reference": "missing_example_integration_ci_check_reference",
    "integration_ci_check_result": "missing_integration_ci_check_result",
    "release_proof_linkage": "missing_example_release_proof_linkage",
    "readme_release_status_path": "missing_example_readme_release_status_path",
    "allowed_traceability_actions": "missing_allowed_traceability_actions",
    "forbidden_authority_actions": "missing_forbidden_authority_actions",
    "traceability_outputs": "missing_traceability_outputs",
    "aaos_retained_authority_statement": "missing_example_aaos_retained_authority_statement",
    "governance_boundary_statement": "missing_example_governance_boundary_statement",
}

REQUIRED_NEGATIVE_FIXTURE_FIELDS = {
    "fixture_id": "missing_negative_fixture_id",
    "fixture_type": "missing_negative_fixture_type",
    "allowed_behavior": "missing_negative_fixture_allowed_behavior",
    "negative_fixture_boundary": "missing_negative_fixture_boundary",
    "scenario": "missing_negative_fixture_scenario",
    "expected_evaluator_outputs": "missing_expected_evaluator_outputs",
}

REQUIRED_ALLOWED_TRACEABILITY_ACTIONS = {
    "read_artifacts",
    "reference_artifacts",
    "replay_replay_ready_packets",
    "inspect_evaluator_findings",
    "preserve_evidence_linkage",
    "preserve_release_proof_linkage",
    "surface_review_required",
    "surface_escalation_required",
    "surface_fail_closed_recommended",
}

REQUIRED_FORBIDDEN_AUTHORITY_ACTIONS = {
    "seal_decision_proof",
    "approve_releases",
    "accept_risk",
    "execute_rollback",
    "execute_fail_closed",
    "close_audits",
    "grant_waivers",
    "make_final_governance_judgments",
    "convert_sealing_eligibility_into_final_sealing",
    "convert_non_sealed_artifacts_into_sealed_artifacts",
}

REQUIRED_NONSEALED_STATUSES = {
    "unsealed_evidence",
    "replay_ready_packets",
    "evidence_complete_packets",
    "evaluator_findings",
    "sealing_eligible_evidence",
    "sealing_rejected_artifacts",
    "sealing_deferred_artifacts",
    "sealing_blocked_artifacts",
}

REQUIRED_NEGATIVE_SCENARIOS = {
    "registry_inclusion_as_approval",
    "ci_pass_as_approval",
    "release_proof_linkage_as_release_approval",
    "fail_closed_recommended_as_fail_closed_executed",
    "sealing_eligible_as_sealed",
    "v0_11_0_treated_as_released",
    "m12_treated_as_complete",
    "closes_168_language",
    "final_governance_judgment_output",
    "audit_closed_output",
}

REQUIRED_EVALUATOR_OUTPUTS = {
    "cross_consumer_traceability_valid",
    "cross_consumer_traceability_invalid",
    "compliant_consumer_traceability_present",
    "compliant_consumer_traceability_missing",
    "traceability_linkage_complete",
    "traceability_linkage_incomplete",
    "authority_boundary_preserved",
    "authority_boundary_violation",
    "sealed_nonsealed_semantics_preserved",
    "release_status_future_only",
    "review_required",
    "escalation_required",
    "fail_closed_recommended",
}

FORBIDDEN_EVALUATOR_OUTPUTS = {
    "release_approved",
    "risk_accepted",
    "decision_proof_sealed",
    "sealed_by_consumer",
    "sealed_by_registry",
    "sealed_by_ci",
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
    "cross-consumer traceability approves release",
    "cross-consumer traceability accepts risk",
    "cross-consumer traceability executes rollback",
    "cross-consumer traceability executes fail-closed",
    "cross-consumer traceability seals decision proof",
    "cross-consumer traceability closes audit",
    "cross-consumer traceability grants waiver",
    "cross-consumer traceability makes final governance judgment",
    "external consumer approves release",
    "external consumer accepts risk",
    "external consumer executes rollback",
    "external consumer executes fail-closed",
    "external consumer seals decision proof",
    "external consumer closes audit",
    "external consumer grants waiver",
    "external consumer makes final governance judgment",
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
            str(record.get("traceability_scope_statement", "")),
            str(record.get("evidence_linkage_only_statement", "")),
            str(record.get("registry_inclusion_boundary", "")),
            str(record.get("ci_pass_boundary", "")),
            str(record.get("release_proof_boundary", "")),
            str(record.get("fail_closed_boundary", "")),
            str(record.get("sealing_eligibility_boundary", "")),
            str(record.get("nonsealed_conversion_boundary", "")),
            str(record.get("decision_proof_sealing_boundary_statement", "")),
            str(record.get("aaos_retained_authority_statement", "")),
            str(record.get("sovereignty_statement", "")),
        ]
    ).lower()



def detect_cross_consumer_forbidden_claims(
    value: Any, parent_key: str | None = None
) -> set[str]:
    claims: set[str] = set()

    if isinstance(value, dict):
        for key, item in value.items():
            claims.update(detect_cross_consumer_forbidden_claims(item, str(key)))
        return claims

    if isinstance(value, list):
        for item in value:
            claims.update(detect_cross_consumer_forbidden_claims(item, parent_key))
        return claims

    if parent_key in SAFE_NEGATIVE_CONTEXT_KEYS:
        return claims

    normalized = _text(value)
    if normalized in FORBIDDEN_EVALUATOR_OUTPUTS:
        claims.add(normalized)

    for phrase in FORBIDDEN_AUTHORITY_PHRASES:
        if phrase in normalized:
            claims.add(phrase)

    return claims



def evaluate_m12_cross_consumer_traceability(record: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    authority_boundary_violation = False
    traceability_linkage_complete = True

    def add_missing(finding: str, evidence: str) -> None:
        nonlocal traceability_linkage_complete
        findings.append(finding)
        missing_evidence.append(evidence)
        traceability_linkage_complete = False

    for field, finding in REQUIRED_TRACEABILITY_FIELDS.items():
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

    top_release_linkage = _as_dict(record.get("release_proof_linkage"))
    if not _release_proof_linkage_present(top_release_linkage):
        add_missing("release_proof_linkage_missing", "release_proof_linkage")

    if "pilot-package.json" not in str(record.get("public_integration_pack_ref", "")):
        add_missing("public_integration_pack_linkage_missing", "public_integration_pack_ref")
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

    compliant_examples = _compliant_examples(record)
    if len(compliant_examples) < 2:
        add_missing(
            "compliant_consumer_traceability_missing",
            "compliant_consumer_traceability_examples",
        )

    for example in compliant_examples:
        example_linkage_complete, example_authority_violation = _evaluate_example(
            example, findings, missing_evidence
        )
        traceability_linkage_complete = (
            traceability_linkage_complete and example_linkage_complete
        )
        authority_boundary_violation = (
            authority_boundary_violation or example_authority_violation
        )

    negative_fixtures = _negative_fixtures(record)
    if not negative_fixtures:
        add_missing(
            "negative_cross_consumer_traceability_fixtures_missing",
            "negative_cross_consumer_traceability_fixtures",
        )
    _evaluate_negative_fixtures(negative_fixtures, findings, missing_evidence)

    boundary_language = _boundary_language(record)
    sealed_nonsealed_semantics_preserved = _sealed_nonsealed_semantics_preserved(
        boundary_language
    )
    if not sealed_nonsealed_semantics_preserved:
        add_missing("sealed_nonsealed_semantics_missing", "sealed_nonsealed_boundary")

    for phrase, finding in BOUNDARY_CLAIM_FINDINGS.items():
        if phrase in boundary_language:
            findings.append(finding)
            authority_boundary_violation = True

    for required_phrase in [
        "evidence linkage only",
        "must not approve releases",
        "must not approve releases, accept risk",
        "execute fail-closed",
        "convert sealing eligibility into final sealing",
        "convert non-sealed artifacts into sealed artifacts",
        "registry inclusion is not approval",
        "ci pass is not approval",
        "release proof linkage is not release approval",
        "fail_closed_recommended is not fail_closed_executed",
        "sealing_eligible is not sealed",
        "non-sealed artifacts must not be converted into sealed artifacts",
        "decision proof sealing remains aaos-owned",
        "aaos retains",
        "aaos remains the decision sovereignty layer",
    ]:
        if required_phrase not in boundary_language:
            add_missing(
                "missing_aaos_authority_boundary_statement",
                "aaos_retained_authority_statement",
            )
            break

    allowed_outputs = _as_set(record.get("allowed_evaluator_outputs"))
    if not REQUIRED_EVALUATOR_OUTPUTS <= allowed_outputs:
        add_missing("missing_allowed_evaluator_outputs", "allowed_evaluator_outputs")
    if FORBIDDEN_EVALUATOR_OUTPUTS & allowed_outputs:
        findings.append("forbidden_evaluator_output_allowed")
        authority_boundary_violation = True

    claims = detect_cross_consumer_forbidden_claims(record)
    if claims:
        findings.append("authority_transfer_claim_detected")
        authority_boundary_violation = True

    return _traceability_result(
        findings=findings,
        missing_evidence=missing_evidence,
        authority_boundary_violation=authority_boundary_violation,
        compliant_consumer_traceability_present=len(compliant_examples) >= 2,
        traceability_linkage_complete=traceability_linkage_complete,
        sealed_nonsealed_semantics_preserved=sealed_nonsealed_semantics_preserved,
        release_status_future_only=release_status_future_only,
    )



def _compliant_examples(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        example
        for example in _as_list(record.get("compliant_consumer_traceability_examples"))
        if isinstance(example, dict)
        and example.get("example_type") == "compliant"
        and example.get("allowed_behavior") is True
    ]



def _negative_fixtures(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        fixture
        for fixture in _as_list(record.get("negative_cross_consumer_traceability_fixtures"))
        if isinstance(fixture, dict)
    ]



def _evaluate_example(
    example: dict[str, Any],
    findings: list[str],
    missing_evidence: list[str],
) -> tuple[bool, bool]:
    linkage_complete = True
    authority_violation = False

    def add_missing(finding: str, evidence: str) -> None:
        nonlocal linkage_complete
        findings.append(finding)
        missing_evidence.append(evidence)
        linkage_complete = False

    for field, finding in REQUIRED_COMPLIANT_EXAMPLE_FIELDS.items():
        if not _has_value(example, field):
            add_missing(finding, f"compliant_consumer_traceability_examples.{field}")

    if "m12-consumer-registry-pattern.json" not in str(
        example.get("consumer_registry_entry_ref", "")
    ):
        add_missing(
            "consumer_registry_entry_linkage_missing",
            "compliant_consumer_traceability_examples.consumer_registry_entry_ref",
        )
    if "pilot-package.json" not in str(example.get("public_integration_pack_ref", "")):
        add_missing(
            "example_public_integration_pack_linkage_missing",
            "compliant_consumer_traceability_examples.public_integration_pack_ref",
        )

    statuses = _as_set(example.get("consumed_artifact_statuses"))
    if "aaos_sealed_decision_proof_artifacts" not in statuses:
        add_missing(
            "sealed_artifact_status_missing",
            "compliant_consumer_traceability_examples.consumed_artifact_statuses",
        )
    if not (REQUIRED_NONSEALED_STATUSES & statuses):
        add_missing(
            "nonsealed_artifact_status_missing",
            "compliant_consumer_traceability_examples.consumed_artifact_statuses",
        )

    for ref_field in [
        "evidence_schema_reference",
        "replay_packet_reference",
        "evaluator_output_reference",
        "integration_ci_check_reference",
        "readme_release_status_path",
    ]:
        if not _has_value(example, ref_field):
            add_missing(
                f"missing_{ref_field}",
                f"compliant_consumer_traceability_examples.{ref_field}",
            )

    if not _release_proof_linkage_present(_as_dict(example.get("release_proof_linkage"))):
        add_missing(
            "example_release_proof_linkage_missing",
            "compliant_consumer_traceability_examples.release_proof_linkage",
        )

    allowed_actions = _as_set(example.get("allowed_traceability_actions"))
    forbidden_actions = _as_set(example.get("forbidden_authority_actions"))
    if not REQUIRED_ALLOWED_TRACEABILITY_ACTIONS <= allowed_actions:
        add_missing(
            "allowed_traceability_actions_missing",
            "compliant_consumer_traceability_examples.allowed_traceability_actions",
        )
    if not REQUIRED_FORBIDDEN_AUTHORITY_ACTIONS <= forbidden_actions:
        add_missing(
            "forbidden_authority_actions_missing",
            "compliant_consumer_traceability_examples.forbidden_authority_actions",
        )
    if REQUIRED_FORBIDDEN_AUTHORITY_ACTIONS & allowed_actions:
        findings.append("forbidden_authority_action_allowed")
        authority_violation = True

    outputs = _as_set(example.get("traceability_outputs"))
    if FORBIDDEN_EVALUATOR_OUTPUTS & outputs:
        findings.append("traceability_output_forbidden_authority_output_detected")
        authority_violation = True

    if detect_cross_consumer_forbidden_claims(example):
        findings.append("compliant_traceability_example_authority_claim_detected")
        authority_violation = True

    return linkage_complete, authority_violation



def _evaluate_negative_fixtures(
    fixtures: list[dict[str, Any]],
    findings: list[str],
    missing_evidence: list[str],
) -> None:
    scenarios = {_text(fixture.get("scenario")) for fixture in fixtures}
    if not REQUIRED_NEGATIVE_SCENARIOS <= scenarios:
        findings.append("negative_cross_consumer_traceability_fixtures_incomplete")
        missing_evidence.append("negative_cross_consumer_traceability_fixtures")

    for fixture in fixtures:
        for field, finding in REQUIRED_NEGATIVE_FIXTURE_FIELDS.items():
            if not _has_value(fixture, field):
                findings.append(finding)
                missing_evidence.append(
                    f"negative_cross_consumer_traceability_fixtures.{field}"
                )
        if fixture.get("fixture_type") != "negative" or fixture.get("allowed_behavior") is not False:
            findings.append("negative_fixture_not_marked_negative")
            missing_evidence.append(
                "negative_cross_consumer_traceability_fixtures.allowed_behavior"
            )



def _release_proof_linkage_present(linkage: dict[str, Any]) -> bool:
    return (
        linkage.get("present") is True
        and linkage.get("evidence_linkage_only") is True
        and linkage.get("release_approval") is False
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



def _sealed_nonsealed_semantics_preserved(boundary_language: str) -> bool:
    return all(
        phrase in boundary_language
        for phrase in [
            "registry inclusion is not approval",
            "ci pass is not approval",
            "release proof linkage is not release approval",
            "fail_closed_recommended is not fail_closed_executed",
            "sealing_eligible is not sealed",
            "non-sealed artifacts must not be converted into sealed artifacts",
            "decision proof sealing remains aaos-owned",
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



def _traceability_result(
    findings: list[str],
    missing_evidence: list[str],
    authority_boundary_violation: bool,
    compliant_consumer_traceability_present: bool,
    traceability_linkage_complete: bool,
    sealed_nonsealed_semantics_preserved: bool,
    release_status_future_only: bool,
) -> dict[str, Any]:
    unique_findings = sorted(set(findings))
    unique_missing = sorted(set(missing_evidence))
    failed = bool(unique_findings or unique_missing or authority_boundary_violation)

    return {
        "cross_consumer_traceability_valid": not failed,
        "cross_consumer_traceability_invalid": failed,
        "compliant_consumer_traceability_present": compliant_consumer_traceability_present,
        "compliant_consumer_traceability_missing": not compliant_consumer_traceability_present,
        "traceability_linkage_complete": traceability_linkage_complete,
        "traceability_linkage_incomplete": not traceability_linkage_complete,
        "authority_boundary_preserved": not authority_boundary_violation,
        "authority_boundary_violation": authority_boundary_violation,
        "sealed_nonsealed_semantics_preserved": sealed_nonsealed_semantics_preserved,
        "release_status_future_only": release_status_future_only,
        "traceability_findings": unique_findings,
        "missing_evidence": unique_missing,
        "review_required": failed,
        "escalation_required": authority_boundary_violation,
        "fail_closed_recommended": authority_boundary_violation,
    }
