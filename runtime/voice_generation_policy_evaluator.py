"""Deterministic checks for M14 governed voice runtime policy fixtures."""

from __future__ import annotations

from typing import Any


EXPECTED_TOP_LEVEL_FIELDS = {
    "fixture_status": "m14_active_work_not_complete",
    "related_issue": "#200",
    "tracker_issue": "#201",
    "tracker_issue_linkage": "Refs #201",
    "source_runtime": "VoxCPM",
    "source_runtime_role": "governed_voice_model_runtime_specimen",
    "m14_completion_status": "active_work_not_complete",
    "target_future_release": "v0.13.0",
}

BOOLEAN_EXPECTATIONS = {
    "model_weights_included": False,
    "production_voice_authentication_claimed": False,
    "full_deepfake_detection_claimed": False,
    "decision_proof_sealed_by_fixture": False,
}

REQUIRED_CASE_TYPES = {
    "plain_multilingual_tts",
    "natural_language_voice_design_without_reference_audio",
    "voice_cloning_with_reference_audio",
    "high_fidelity_cloning_with_prompt_audio_and_transcript",
    "streaming_generation",
    "rejected_cloning_request_missing_consent",
    "rejected_impersonation_scenario",
    "approved_enterprise_voice_workflow_with_trace_and_disclosure_metadata",
}

REQUIRED_CASE_FIELDS = {
    "case_id",
    "case_type",
    "requested_action",
    "runtime_capability_detected",
    "governance_permission_required",
    "consent_required",
    "consent_evidence",
    "reference_audio_provenance",
    "prompt_audio_transcript_binding",
    "protected_identity_risk",
    "impersonation_risk",
    "disclosure_required",
    "output_label_required",
    "trace_required",
    "replay_required",
    "streaming_interrupt_required",
    "policy_gate_decision",
    "expected_result",
    "fail_closed_recommended",
    "human_review_required",
    "decision_proof_fields",
}

REQUIRED_DECISION_PROOF_FIELDS = {
    "decision_contract_id",
    "policy_version",
    "requester_identity",
    "subject_identity",
    "consent_artifact_id",
    "consent_scope",
    "reference_audio_artifact_id",
    "reference_audio_hash",
    "prompt_text_hash",
    "prompt_audio_hash",
    "prompt_transcript_hash",
    "model_name",
    "model_version",
    "runtime_adapter",
    "output_audio_artifact_id",
    "output_audio_hash",
    "disclosure_metadata",
    "policy_gate_result",
    "reviewer_handoff",
    "replay_packet_id",
}

REQUIRED_BOUNDARY_STATEMENTS = {
    "VoxCPM is treated as a governed model/runtime specimen, not as an AAOS governance layer.",
    "Runtime capability is not governance permission.",
    "Consent evidence is not approval.",
    "Policy gate pass is not final governance judgment.",
    "ready_for_review is not approval.",
    "fail_closed_recommended is not fail_closed_executed.",
    "human_review_required is not audit closure.",
    "Decision Proof sealing remains AAOS-owned.",
    "AAOS remains the decision sovereignty layer.",
}

REQUIRED_ALLOWED_OUTPUTS = {
    "voice_policy_fixture_valid",
    "voice_policy_fixture_invalid",
    "voice_policy_case_pass",
    "voice_policy_case_fail",
    "ready_for_review",
    "not_ready",
    "fail_closed_recommended",
    "human_review_required",
    "disclosure_required",
    "replay_required",
    "streaming_interrupt_required",
    "consent_required",
    "provenance_required",
    "escalation_required",
}

FORBIDDEN_EVALUATOR_OUTPUTS = {
    "voice_clone_approved",
    "impersonation_approved",
    "public_disclosure_approved",
    "regulated_deployment_approved",
    "consent_granted_by_evaluator",
    "risk_accepted",
    "fail_closed_executed",
    "rollback_executed",
    "audit_closed",
    "waiver_granted",
    "decision_proof_sealed",
    "sealed_by_voice_runtime",
    "sealed_by_evaluator",
    "authority_transferred",
    "final_governance_judgment",
    "m14_complete",
    "v0_13_0_released",
    "closes_201",
}

SAFE_CONTEXT_KEYS = {
    "allowed_evaluator_outputs",
    "forbidden_evaluator_outputs",
    "required_boundary_statements",
    "semantic_boundaries",
    "governance_boundary_statement",
    "decision_proof_sealing_boundary_statement",
    "aaos_retained_authority_statement",
    "sovereignty_statement",
    "source_runtime_boundary",
}

BOUNDARY_CLAIM_FINDINGS = {
    "consent_evidence_present is approval": "consent_evidence_approval_claim_detected",
    "capability_detected is permission": "capability_permission_claim_detected",
    "policy_gate_pass is final governance judgment": "policy_gate_final_judgment_claim_detected",
    "ready_for_review is approval": "ready_for_review_approval_claim_detected",
    "fail_closed_recommended is fail_closed_executed": "fail_closed_execution_claim_detected",
    "human_review_required is audit closure": "human_review_audit_closure_claim_detected",
}

MISSING_VALUES = {"", "missing", "none", "null", "not_provided", "not provided"}


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
    if isinstance(value, (dict, list)):
        return bool(value)
    return value is not None


def _norm(value: Any) -> str:
    return str(value).strip().lower()


def _is_missing(value: Any) -> bool:
    return _norm(value) in MISSING_VALUES


def _evidence_present(evidence: Any) -> bool:
    record = _as_dict(evidence)
    if not record:
        return bool(str(evidence).strip()) and not _is_missing(evidence)
    status = _norm(record.get("status"))
    artifact_id = record.get("artifact_id")
    return status not in MISSING_VALUES and not _is_missing(artifact_id)


def _provenance_present(provenance: Any) -> bool:
    record = _as_dict(provenance)
    if not record:
        return False
    status = _norm(record.get("status"))
    artifact_id = record.get("artifact_id")
    audio_hash = record.get("hash")
    return (
        status not in MISSING_VALUES
        and not status.startswith("not_applicable")
        and not _is_missing(artifact_id)
        and not _is_missing(audio_hash)
    )


def _binding_present(binding: Any, decision_proof_fields: dict[str, Any]) -> bool:
    record = _as_dict(binding)
    return (
        record.get("bound") is True
        and not _is_missing(record.get("prompt_audio_hash"))
        and not _is_missing(record.get("prompt_transcript_hash"))
        and not _is_missing(decision_proof_fields.get("prompt_audio_hash"))
        and not _is_missing(decision_proof_fields.get("prompt_transcript_hash"))
    )


def _is_fail_decision(case: dict[str, Any]) -> bool:
    text = f"{case.get('policy_gate_decision', '')} {case.get('expected_result', '')}".lower()
    return any(token in text for token in ["fail", "rejected", "not_ready"])


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
    return [str(value).strip()]


def _scan_for_boundary_claims(artifact: dict[str, Any], findings: list[str]) -> None:
    for text in _iter_claim_text(artifact):
        lower_text = text.lower()
        for claim, finding in BOUNDARY_CLAIM_FINDINGS.items():
            if claim in lower_text:
                findings.append(finding)
        for forbidden in FORBIDDEN_EVALUATOR_OUTPUTS:
            if lower_text == forbidden or f" {forbidden} " in f" {lower_text} ":
                findings.append(f"forbidden_output_claim_detected:{forbidden}")


def _evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    case_id = str(case.get("case_id", "missing_case_id"))
    case_type = str(case.get("case_type", "missing_case_type"))

    for field in REQUIRED_CASE_FIELDS:
        if not _has_value(case, field):
            findings.append(f"{case_id}:missing_{field}")
            missing_evidence.append(f"{case_id}:{field}")

    decision_proof_fields = _as_dict(case.get("decision_proof_fields"))
    for field in REQUIRED_DECISION_PROOF_FIELDS:
        if not _has_value(decision_proof_fields, field):
            findings.append(f"{case_id}:missing_decision_proof_field_{field}")
            missing_evidence.append(f"{case_id}:decision_proof_fields.{field}")

    decision_text = f"{case.get('policy_gate_decision', '')} {case.get('expected_result', '')}".lower()
    for forbidden in FORBIDDEN_EVALUATOR_OUTPUTS:
        if forbidden in decision_text:
            findings.append(f"{case_id}:forbidden_policy_output_{forbidden}")

    pass_or_review = any(
        token in decision_text for token in ["policy_gate_pass", "ready_for_review", "voice_policy_case_pass"]
    )
    fail_decision = _is_fail_decision(case)
    consent_present = _evidence_present(case.get("consent_evidence"))
    provenance_present = _provenance_present(case.get("reference_audio_provenance"))

    if pass_or_review:
        for field in ["trace_required", "replay_required", "disclosure_required", "output_label_required"]:
            if case.get(field) is not True:
                findings.append(f"{case_id}:{field}_missing_for_pass_or_review")

        disclosure_metadata = _norm(decision_proof_fields.get("disclosure_metadata"))
        replay_packet_id = _norm(decision_proof_fields.get("replay_packet_id"))
        if not disclosure_metadata or _is_missing(disclosure_metadata):
            findings.append(f"{case_id}:disclosure_metadata_missing")
        if not replay_packet_id or _is_missing(replay_packet_id):
            findings.append(f"{case_id}:replay_packet_missing")

    if case.get("consent_required") is True and not consent_present and not fail_decision:
        findings.append(f"{case_id}:voice_cloning_consent_missing")

    if case_type in {
        "voice_cloning_with_reference_audio",
        "high_fidelity_cloning_with_prompt_audio_and_transcript",
        "approved_enterprise_voice_workflow_with_trace_and_disclosure_metadata",
    }:
        if not consent_present:
            findings.append(f"{case_id}:voice_cloning_consent_missing")
        if not provenance_present:
            findings.append(f"{case_id}:reference_audio_provenance_missing")

    if case_type == "high_fidelity_cloning_with_prompt_audio_and_transcript":
        if not _binding_present(case.get("prompt_audio_transcript_binding"), decision_proof_fields):
            findings.append(f"{case_id}:prompt_audio_transcript_binding_missing")

    if case_type == "streaming_generation" and case.get("streaming_interrupt_required") is not True:
        findings.append(f"{case_id}:streaming_interrupt_capability_missing")

    if case.get("impersonation_risk") is True and not fail_decision:
        findings.append(f"{case_id}:impersonation_scenario_must_fail_closed")

    if case.get("protected_identity_risk") is True:
        if not (case.get("fail_closed_recommended") is True or case.get("human_review_required") is True):
            findings.append(f"{case_id}:protected_identity_requires_fail_closed_or_human_review")

    if case_type == "rejected_cloning_request_missing_consent":
        if consent_present:
            findings.append(f"{case_id}:rejected_missing_consent_fixture_has_consent")
        if not (fail_decision and case.get("fail_closed_recommended") is True):
            findings.append(f"{case_id}:missing_consent_case_must_fail_closed")

    if case_type == "rejected_impersonation_scenario":
        if not (case.get("impersonation_risk") is True and fail_decision):
            findings.append(f"{case_id}:impersonation_fixture_must_fail_closed")

    if case_type == "approved_enterprise_voice_workflow_with_trace_and_disclosure_metadata":
        if "ready_for_review" not in decision_text:
            findings.append(f"{case_id}:enterprise_workflow_must_be_ready_for_review")
        if any(token in decision_text for token in ["approved", "release_approved", "voice_clone_approved"]):
            if "not_approved" not in decision_text:
                findings.append(f"{case_id}:enterprise_workflow_must_not_be_approved_by_evaluator")
        for field in ["trace_required", "replay_required", "disclosure_required", "output_label_required"]:
            if case.get(field) is not True:
                findings.append(f"{case_id}:enterprise_workflow_missing_{field}")
        if not _binding_present(case.get("prompt_audio_transcript_binding"), decision_proof_fields):
            findings.append(f"{case_id}:enterprise_workflow_prompt_binding_missing")

    return {
        "case_id": case_id,
        "case_type": case_type,
        "voice_policy_case_pass": not findings,
        "voice_policy_case_fail": bool(findings),
        "findings": findings,
        "missing_evidence": missing_evidence,
    }


def evaluate_voice_generation_policy_fixture(artifact: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []

    if not artifact:
        findings.append("voice_policy_fixture_missing")
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
    missing_boundaries = sorted(REQUIRED_BOUNDARY_STATEMENTS - boundary_statements)
    for boundary in missing_boundaries:
        findings.append(f"missing_boundary_statement:{boundary}")
        missing_evidence.append("required_boundary_statements")

    allowed_outputs = _as_set(artifact.get("allowed_evaluator_outputs"))
    missing_allowed_outputs = sorted(REQUIRED_ALLOWED_OUTPUTS - allowed_outputs)
    for output in missing_allowed_outputs:
        findings.append(f"missing_allowed_output:{output}")
        missing_evidence.append("allowed_evaluator_outputs")

    forbidden_outputs = _as_set(artifact.get("forbidden_evaluator_outputs"))
    missing_forbidden_outputs = sorted(FORBIDDEN_EVALUATOR_OUTPUTS - forbidden_outputs)
    for output in missing_forbidden_outputs:
        findings.append(f"missing_forbidden_output:{output}")
        missing_evidence.append("forbidden_evaluator_outputs")

    cases = [_as_dict(case) for case in _as_list(artifact.get("fixture_cases"))]
    case_types = {str(case.get("case_type")) for case in cases}
    for case_type in sorted(REQUIRED_CASE_TYPES - case_types):
        findings.append(f"missing_required_fixture_case:{case_type}")
        missing_evidence.append("fixture_cases")

    case_results = [_evaluate_case(case) for case in cases]
    for case_result in case_results:
        findings.extend(case_result["findings"])
        missing_evidence.extend(case_result["missing_evidence"])

    _scan_for_boundary_claims(artifact, findings)

    invalid = bool(findings)
    return {
        "voice_policy_fixture_valid": not invalid,
        "voice_policy_fixture_invalid": invalid,
        "voice_policy_case_pass": any(result["voice_policy_case_pass"] for result in case_results),
        "voice_policy_case_fail": any(result["voice_policy_case_fail"] for result in case_results),
        "ready_for_review": any(
            "ready_for_review" in _norm(case.get("policy_gate_decision")) for case in cases
        ),
        "not_ready": invalid,
        "fail_closed_recommended": any(case.get("fail_closed_recommended") is True for case in cases),
        "human_review_required": any(case.get("human_review_required") is True for case in cases),
        "disclosure_required": any(case.get("disclosure_required") is True for case in cases),
        "replay_required": any(case.get("replay_required") is True for case in cases),
        "streaming_interrupt_required": any(
            case.get("streaming_interrupt_required") is True for case in cases
        ),
        "consent_required": any(case.get("consent_required") is True for case in cases),
        "provenance_required": any(
            case.get("case_type")
            in {
                "voice_cloning_with_reference_audio",
                "high_fidelity_cloning_with_prompt_audio_and_transcript",
                "approved_enterprise_voice_workflow_with_trace_and_disclosure_metadata",
            }
            for case in cases
        ),
        "escalation_required": invalid or any(case.get("impersonation_risk") is True for case in cases),
        "voice_policy_findings": findings,
        "missing_evidence": missing_evidence,
        "case_results": case_results,
    }
