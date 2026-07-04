"""Deterministic checks for M11 public integration pack pilot evidence."""

from __future__ import annotations

from typing import Any


REQUIRED_PACK_FIELDS = {
    "integration_boundary_contract": "missing_integration_boundary_contract",
    "evidence_schema_reference": "missing_evidence_schema_reference",
    "replay_packet_example": "missing_replay_packet_example",
    "release_proof_linkage": "missing_release_proof_linkage",
    "sealing_boundary_statement": "missing_sealing_boundary_statement",
    "adapter_registry_entry_reference": "missing_adapter_registry_entry_reference",
    "evaluator_check_reference": "missing_evaluator_check_reference",
    "readme_integration_status_language": "missing_readme_integration_status_language",
    "governance_boundary_language": "missing_governance_boundary_language",
    "not_authority_statement": "missing_not_authority_statement",
    "aaos_retained_authority_statement": "missing_aaos_retained_authority_statement",
}

REQUIRED_CONSUMER_FIELDS = {
    "sealed_artifacts": "missing_sealed_artifact_semantics",
    "non_sealed_artifacts": "missing_non_sealed_artifact_semantics",
    "replayable_evidence": "missing_replayable_evidence",
    "evaluator_findings": "missing_evaluator_findings",
    "release_proof_evidence": "missing_release_proof_evidence",
    "governance_ci_findings": "missing_governance_ci_findings",
    "human_review_state": "missing_human_review_state",
    "sealing_eligibility": "missing_sealing_eligibility",
    "final_aaos_owned_sealing_authority": "missing_final_aaos_owned_sealing_authority",
    "artifact_consumption_semantics": "missing_artifact_consumption_semantics",
    "not_authority_statement": "missing_not_authority_statement",
    "aaos_retained_authority_statement": "missing_aaos_retained_authority_statement",
}

REQUIRED_CONSUMPTION_STATUSES = {
    "unsealed_evidence",
    "replay_ready_packets",
    "evidence_complete_packets",
    "evaluator_findings",
    "sealing_eligible_evidence",
    "aaos_sealed_decision_proof_artifacts",
    "sealing_rejected_artifacts",
    "sealing_deferred_artifacts",
    "sealing_blocked_artifacts",
}

FORBIDDEN_AUTHORITY_OUTPUTS = {
    "decision_proof_sealed",
    "sealed_by_integration_pack",
    "sealed_by_external_consumer",
    "release_approved",
    "risk_accepted",
    "rollback_executed",
    "audit_closed",
    "final_governance_judgment",
}

FORBIDDEN_AUTHORITY_PHRASES = {
    "integration pack seals decision proof",
    "external consumer seals decision proof",
    "integration pack approves release",
    "external consumer approves release",
    "integration pack accepts risk",
    "external consumer accepts risk",
    "integration pack executes rollback",
    "external consumer executes rollback",
    "integration pack closes audit",
    "external consumer closes audit",
    "integration pack makes final governance judgment",
    "external consumer makes final governance judgment",
}

SAFE_NEGATIVE_CONTEXT_KEYS = {
    "forbidden_pack_outputs",
    "forbidden_consumer_outputs",
    "forbidden_outputs",
    "forbidden_authority_outputs",
    "forbidden_authority_phrases",
    "not_authority_statement",
    "governance_boundary_language",
    "authority_boundary",
    "authority_boundary_statement",
    "aaos_retained_authority_statement",
    "sealing_boundary_statement",
}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


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


def detect_forbidden_authority_claims(
    value: Any, parent_key: str | None = None
) -> set[str]:
    claims: set[str] = set()

    if isinstance(value, dict):
        for key, item in value.items():
            claims.update(detect_forbidden_authority_claims(item, str(key)))
        return claims

    if isinstance(value, list):
        for item in value:
            claims.update(detect_forbidden_authority_claims(item, parent_key))
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


def evaluate_public_integration_pack(record: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []

    for field, finding in REQUIRED_PACK_FIELDS.items():
        if not _has_value(record, field):
            findings.append(finding)
            missing_evidence.append(field)

    release_linkage = _as_dict(record.get("release_proof_linkage"))
    if release_linkage.get("present") is not True:
        findings.append("release_proof_linkage_missing")
        missing_evidence.append("release_proof_linkage")

    boundary_language = " ".join(
        [
            str(record.get("governance_boundary_language", "")),
            str(record.get("sealing_boundary_statement", "")),
            str(record.get("not_authority_statement", "")),
        ]
    ).lower()
    for required_phrase in [
        "decision proof sealing remains aaos-owned",
        "must not become governance authority",
        "final governance authority",
    ]:
        if required_phrase not in boundary_language:
            findings.append("missing_governance_boundary_language")
            missing_evidence.append("governance_boundary_language")
            break

    claims = detect_forbidden_authority_claims(record)
    return _result(
        mode="pack",
        findings=findings,
        missing_evidence=missing_evidence,
        authority_boundary_violation=bool(claims),
    )


def evaluate_external_evidence_consumer(record: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []

    for field, finding in REQUIRED_CONSUMER_FIELDS.items():
        if not _has_value(record, field):
            findings.append(finding)
            missing_evidence.append(field)

    final_authority = _as_dict(record.get("final_aaos_owned_sealing_authority"))
    if final_authority.get("owner") != "AAOS" or final_authority.get("delegated") is not False:
        findings.append("missing_final_aaos_owned_sealing_authority")
        missing_evidence.append("final_aaos_owned_sealing_authority")

    semantics_result = evaluate_artifact_consumption_semantics(record)
    findings.extend(semantics_result["integration_findings"])
    missing_evidence.extend(semantics_result["missing_evidence"])

    if not _as_list(record.get("release_proof_evidence")):
        findings.append("release_proof_linkage_missing")
        missing_evidence.append("release_proof_evidence")

    claims = detect_forbidden_authority_claims(record)
    return _result(
        mode="consumer",
        findings=findings,
        missing_evidence=missing_evidence,
        authority_boundary_violation=bool(claims),
    )


def evaluate_artifact_consumption_semantics(record: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    semantics = _as_dict(record.get("artifact_consumption_semantics"))

    for status in REQUIRED_CONSUMPTION_STATUSES:
        status_semantics = _as_dict(semantics.get(status))
        if not status_semantics:
            findings.append(f"missing_consumption_semantics_for_{status}")
            missing_evidence.append(f"artifact_consumption_semantics.{status}")
            continue
        if not _as_list(status_semantics.get("allowed_consumer_actions")):
            findings.append(f"missing_allowed_consumer_actions_for_{status}")
            missing_evidence.append(
                f"artifact_consumption_semantics.{status}.allowed_consumer_actions"
            )
        if not _has_value(status_semantics, "authority_boundary"):
            findings.append(f"missing_authority_boundary_for_{status}")
            missing_evidence.append(
                f"artifact_consumption_semantics.{status}.authority_boundary"
            )

    claims = detect_forbidden_authority_claims(record)
    return _result(
        mode="semantics",
        findings=findings,
        missing_evidence=missing_evidence,
        authority_boundary_violation=bool(claims),
    )


def _result(
    mode: str,
    findings: list[str],
    missing_evidence: list[str],
    authority_boundary_violation: bool,
) -> dict[str, Any]:
    unique_findings = sorted(set(findings))
    unique_missing = sorted(set(missing_evidence))
    failed = bool(unique_findings or unique_missing or authority_boundary_violation)

    return {
        "public_integration_pack_valid": not failed if mode == "pack" else not authority_boundary_violation,
        "public_integration_pack_invalid": failed if mode == "pack" else authority_boundary_violation,
        "external_consumer_valid": not failed if mode == "consumer" else not authority_boundary_violation,
        "external_consumer_invalid": failed if mode == "consumer" else authority_boundary_violation,
        "artifact_consumption_semantics_present": not failed if mode == "semantics" else not any("consumption_semantics" in finding for finding in unique_findings),
        "artifact_consumption_semantics_missing": failed if mode == "semantics" else any("consumption_semantics" in finding for finding in unique_findings),
        "release_proof_linkage_present": "release_proof_linkage_missing" not in unique_findings,
        "release_proof_linkage_missing": "release_proof_linkage_missing" in unique_findings,
        "authority_boundary_preserved": not authority_boundary_violation,
        "authority_boundary_violation": authority_boundary_violation,
        "integration_findings": unique_findings,
        "missing_evidence": unique_missing,
        "review_required": failed,
        "escalation_required": authority_boundary_violation,
        "fail_closed_recommended": authority_boundary_violation,
    }
