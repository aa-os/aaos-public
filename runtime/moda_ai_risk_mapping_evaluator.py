"""Deterministic checks for the M14 MODA AI risk taxonomy mapping fixtures."""

from __future__ import annotations

import re
from typing import Any


EXPECTED_TOP_LEVEL_FIELDS = {
    "fixture_status": "m14_active_work_not_complete",
    "related_issue": "#181",
    "tracker_issue": "#201",
    "tracker_issue_linkage": "Refs #201",
    "related_voice_runtime_pr": "#202",
    "related_public_output_gate_pr": "#204",
    "source_framework": "Taiwan MODA AI Risk Classification Framework",
    "source_framework_version": "v1.0",
    "source_framework_role": "external_regulatory_risk_taxonomy_reference",
    "m14_completion_status": "active_work_not_complete",
    "target_future_release": "v0.13.0",
}

BOOLEAN_EXPECTATIONS = {
    "source_framework_is_aaos_governance_authority": False,
    "legal_approval_claimed": False,
    "regulatory_certification_claimed": False,
    "full_compliance_claimed": False,
    "legal_advice_provided": False,
    "decision_proof_sealed_by_fixture": False,
    "final_risk_classification_made_by_fixture": False,
}

REQUIRED_CODES_BY_TYPE = {
    "A": {f"A{index}" for index in range(1, 9)},
    "B": {f"B{index}" for index in range(1, 7)},
    "C": {f"C{index}" for index in range(1, 7)},
}

REQUIRED_TAXONOMY_CODES = set().union(*REQUIRED_CODES_BY_TYPE.values())

SOURCE_TYPE_LABELS_ZH_TW = {
    "A": "AI 系統本身之技術設計缺陷",
    "B": "部署後操作及人機互動問題",
    "C": "社會結構與環境衝擊",
}

SOURCE_LABELS_ZH_TW = {
    "A1": "AI 系統的安全漏洞與攻擊",
    "A2": "缺乏透明性或可解釋性",
    "A3": "AI 行為偏離人類意圖與社會價值",
    "A4": "AI 具有危險的能力",
    "A5": "影響隱私與違反個人資料保護法規",
    "A6": "侵害智慧財產權疑慮",
    "A7": "不公平的歧視或偏見",
    "A8": "錯誤或誤導訊息",
    "B1": "過度依賴與不安全使用",
    "B2": "喪失人類自主性",
    "B3": "生成違法內容",
    "B4": "詐欺與深偽技術濫用",
    "B5": "用於網路攻擊",
    "B6": "AI 自主代理之授權外行為",
    "C1": "企業及國家間競爭秩序失衡",
    "C2": "權力集中與利益分配不公平",
    "C3": "不平等加劇、就業品質下降",
    "C4": "人類在經濟與文化上之創作價值受損",
    "C5": "環境傷害",
    "C6": "認知作戰與資訊主權",
}

AAOS_CONTROL_CATEGORIES = {
    "A1": "system_security_and_adversarial_resilience",
    "A2": "transparency_explainability_and_traceability",
    "A3": "intent_alignment_and_value_boundary",
    "A4": "dangerous_capability_and_containment",
    "A5": "privacy_and_personal_data_governance",
    "A6": "intellectual_property_provenance",
    "A7": "fairness_bias_and_non_discrimination",
    "A8": "information_integrity_and_misleading_output",
    "B1": "human_reliance_and_safe_use",
    "B2": "human_autonomy_and_override",
    "B3": "illegal_content_prevention_and_escalation",
    "B4": "identity_provenance_and_deepfake_misuse",
    "B5": "cyber_misuse_and_tool_boundary",
    "B6": "agent_authorization_and_action_boundary",
    "C1": "competitive_pressure_and_safe_deployment",
    "C2": "power_concentration_and_distributional_impact",
    "C3": "inequality_employment_quality_and_appeal",
    "C4": "human_creation_value_and_cultural_diversity",
    "C5": "environmental_impact_and_resource_use",
    "C6": "cognitive_security_and_information_sovereignty",
}

B6_SOURCE_LABEL = "AI autonomous agent unauthorized behavior"
B6_CONTROL_CATEGORY = "agent_authorization_and_action_boundary"
B6_REQUIRED_DECISION_PROOF_FIELDS = {
    "permission_scope",
    "authorization_decision",
    "action_target",
    "output_channel",
    "execution_trace_id",
}
B6_REQUIRED_BOOLEAN_REQUIREMENTS = {
    "permission_scope_required",
    "authorization_decision_required",
    "action_target_binding_required",
    "output_channel_binding_required",
    "execution_trace_required",
}

REQUIRED_CHECKLIST_FIELDS = {
    "capture": {
        "application_scenario",
        "stakeholders",
        "model_tool_stack",
        "permission_scope",
        "data_sources",
        "deployment_context",
        "output_channel",
        "source_taxonomy_provenance",
    },
    "verify": {
        "taxonomy_risk_codes",
        "inherent_risk_screening",
        "serious_harm_screening",
        "existing_control_coverage",
        "b6_authorization_boundary",
        "human_review_requirement",
        "appealability_requirement",
    },
    "accumulate": {
        "trace_logs",
        "review_evidence",
        "rollback_records",
        "incident_examples",
        "periodic_reassessment_record",
        "framework_version_history",
        "replay_packet_id",
    },
}

REQUIRED_SECTORS = {
    "healthcare",
    "finance",
    "education",
    "labor",
    "government_service",
}

REQUIRED_REASSESSMENT_FIELDS = {
    "reassessment_required",
    "reassessment_cadence",
    "last_assessment_recorded_at",
    "next_assessment_due",
    "reassessment_triggers",
    "source_framework_version_at_assessment",
    "changed_risk_codes",
    "reviewer_handoff",
    "replay_packet_id",
}

REQUIRED_REASSESSMENT_TRIGGERS = {
    "source_framework_revision",
    "model_or_tool_change",
    "permission_change",
    "new_data_source",
    "incident_or_near_miss",
    "serious_harm_signal",
    "output_channel_change",
    "material_deployment_context_change",
}

REQUIRED_BOUNDARY_STATEMENTS = {
    "The MODA framework is treated as an external regulatory-risk taxonomy reference, not an AAOS governance authority.",
    "Regulatory mapping is not legal approval.",
    "Taxonomy mapping is not compliance certification.",
    "Risk-code coverage is not regulatory clearance.",
    "Control coverage complete is not deployment approval.",
    "Serious-harm screening is not final legal determination.",
    "inherent_risk_screened is not risk accepted.",
    "ready_for_review is not regulated deployment approval.",
    "human_review_required is not audit closure.",
    "fail_closed_recommended is not fail_closed_executed.",
    "rollback_recommended is not rollback_executed.",
    "Decision Proof sealing remains AAOS-owned.",
    "AAOS remains the decision sovereignty layer.",
}

REQUIRED_ALLOWED_OUTPUTS = {
    "moda_ai_risk_mapping_valid",
    "moda_ai_risk_mapping_invalid",
    "taxonomy_coverage_complete",
    "taxonomy_coverage_incomplete",
    "decision_proof_checklist_complete",
    "decision_proof_checklist_incomplete",
    "b6_first_class_control_present",
    "sector_coverage_complete",
    "sector_coverage_incomplete",
    "serious_harm_screening_required",
    "human_review_required",
    "public_output_gate_required",
    "periodic_reassessment_required",
    "ready_for_review",
    "fail_closed_recommended",
    "rollback_recommended",
    "replay_required",
    "escalation_required",
}

FORBIDDEN_EVALUATOR_OUTPUTS = {
    "legal_approval_granted",
    "regulatory_compliance_certified",
    "full_compliance_certified",
    "regulated_deployment_approved",
    "diagnosis_approved",
    "treatment_approved",
    "trade_approved",
    "payment_approved",
    "credit_decision_approved",
    "hiring_decision_approved",
    "termination_approved",
    "government_eligibility_approved",
    "public_disclosure_approved",
    "risk_accepted",
    "serious_harm_cleared",
    "final_risk_classification",
    "fail_closed_executed",
    "rollback_executed",
    "audit_closed",
    "waiver_granted",
    "decision_proof_sealed",
    "sealed_by_regulatory_mapping",
    "sealed_by_evaluator",
    "authority_transferred",
    "final_governance_judgment",
    "m14_complete",
    "v0_13_0_released",
    "closes_201",
}

SAFE_CONTEXT_KEYS = {
    "forbidden_evaluator_outputs",
    "required_boundary_statements",
    "semantic_boundaries",
    "boundary_statement",
    "provenance_policy",
}

BOUNDARY_CLAIM_FINDINGS = {
    "moda framework is an aaos governance authority": "external_taxonomy_authority_claim_detected",
    "regulatory mapping is legal approval": "legal_approval_claim_detected",
    "taxonomy mapping is compliance certification": "compliance_certification_claim_detected",
    "risk-code coverage is regulatory clearance": "regulatory_clearance_claim_detected",
    "control coverage complete is deployment approval": "deployment_approval_claim_detected",
    "serious-harm screening is final legal determination": "serious_harm_final_determination_claim_detected",
    "inherent_risk_screened is risk accepted": "risk_acceptance_claim_detected",
    "ready_for_review is regulated deployment approval": "ready_for_review_deployment_approval_claim_detected",
    "human_review_required is audit closure": "human_review_audit_closure_claim_detected",
    "fail_closed_recommended is fail_closed_executed": "fail_closed_execution_claim_detected",
    "rollback_recommended is rollback_executed": "rollback_execution_claim_detected",
}

TRACKER_201_CLOSURE_PHRASES = {
    "closes #201",
    "close #201",
    "closed #201",
    "fixes #201",
    "fixed #201",
    "resolves #201",
    "resolved #201",
}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_set(value: Any) -> set[str]:
    return {str(item).strip() for item in _as_list(value) if str(item).strip()}


def _norm(value: Any) -> str:
    return str(value).strip().lower()


def _field_present(record: dict[str, Any], field: str) -> bool:
    if field not in record or record[field] is None:
        return False
    if isinstance(record[field], str):
        return bool(record[field].strip())
    return True


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _scan_for_forbidden_claims(
    value: Any,
    findings: list[str],
    parent_key: str | None = None,
) -> None:
    if parent_key in SAFE_CONTEXT_KEYS:
        return

    if isinstance(value, dict):
        for key, item in value.items():
            _scan_for_forbidden_claims(item, findings, str(key))
        return

    if isinstance(value, list):
        for item in value:
            _scan_for_forbidden_claims(item, findings, parent_key)
        return

    if not isinstance(value, str):
        return

    normalized = _norm(value)
    for claim, finding in BOUNDARY_CLAIM_FINDINGS.items():
        if claim in normalized:
            findings.append(finding)

    for forbidden in FORBIDDEN_EVALUATOR_OUTPUTS:
        pattern = rf"(?<![a-z0-9_]){re.escape(forbidden)}(?![a-z0-9_])"
        if re.search(pattern, normalized):
            findings.append(f"forbidden_output_claim_detected:{forbidden}")

    if any(phrase in normalized for phrase in TRACKER_201_CLOSURE_PHRASES):
        findings.append("tracker_issue_201_closure_claim_detected")
    if "m14 is complete" in normalized or "m14 complete" in normalized:
        findings.append("m14_completion_claim_detected")
    if "v0.13.0 is released" in normalized or "v0.13.0 released" in normalized:
        findings.append("v0_13_0_release_claim_detected")


def _checklist_field_sets(
    artifact: dict[str, Any],
    findings: list[str],
    missing_evidence: list[str],
) -> tuple[dict[str, set[str]], bool]:
    checklist = _as_dict(artifact.get("decision_proof_checklist"))
    field_sets: dict[str, set[str]] = {}
    complete = True

    for phase, required_fields in REQUIRED_CHECKLIST_FIELDS.items():
        items = [_as_dict(item) for item in _as_list(checklist.get(phase))]
        fields = {str(item.get("field", "")) for item in items if item.get("field")}
        field_sets[phase] = fields

        if len(fields) != len(items):
            findings.append(f"duplicate_or_missing_{phase}_checklist_field")
            complete = False

        for field in sorted(required_fields - fields):
            findings.append(f"missing_{phase}_checklist_field:{field}")
            missing_evidence.append(f"decision_proof_checklist.{phase}.{field}")
            complete = False

        for item in items:
            field = str(item.get("field", "missing_field"))
            if item.get("required") is not True:
                findings.append(f"{phase}_checklist_field_not_required:{field}")
                complete = False
            if not _field_present(item, "purpose"):
                findings.append(f"{phase}_checklist_purpose_missing:{field}")
                complete = False

    return field_sets, complete


def _evaluate_taxonomy_mappings(
    artifact: dict[str, Any],
    checklist_fields: dict[str, set[str]],
) -> tuple[list[str], list[str], bool, bool]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    mappings = [_as_dict(item) for item in _as_list(artifact.get("taxonomy_mappings"))]
    codes = [str(item.get("risk_code", "")) for item in mappings]
    code_set = set(codes)

    for code in sorted(REQUIRED_TAXONOMY_CODES - code_set):
        findings.append(f"missing_taxonomy_code:{code}")
        missing_evidence.append(f"taxonomy_mappings.{code}")
    for code in sorted(code_set - REQUIRED_TAXONOMY_CODES):
        findings.append(f"unexpected_taxonomy_code:{code}")
    if len(codes) != len(code_set):
        findings.append("duplicate_taxonomy_code")

    source_types = [_as_dict(item) for item in _as_list(artifact.get("taxonomy_source_types"))]
    source_type_by_prefix = {str(item.get("prefix", "")): item for item in source_types}
    for prefix, required_codes in REQUIRED_CODES_BY_TYPE.items():
        source_type = source_type_by_prefix.get(prefix, {})
        if source_type.get("source_type_label_zh_tw") != SOURCE_TYPE_LABELS_ZH_TW[prefix]:
            findings.append(f"invalid_source_type_label:{prefix}")
        if _as_set(source_type.get("required_codes")) != required_codes:
            findings.append(f"invalid_source_type_code_coverage:{prefix}")

    b6_mapping_valid = False
    for mapping in mappings:
        code = str(mapping.get("risk_code", ""))
        if code not in REQUIRED_TAXONOMY_CODES:
            continue

        if mapping.get("source_risk_type") != code[0]:
            findings.append(f"{code}:source_risk_type_mismatch")
        if mapping.get("source_label_zh_tw") != SOURCE_LABELS_ZH_TW[code]:
            findings.append(f"{code}:source_label_zh_tw_mismatch")
        if not _field_present(mapping, "source_label"):
            findings.append(f"{code}:source_label_missing")
            missing_evidence.append(f"taxonomy_mappings.{code}.source_label")
        if not _field_present(mapping, "source_provenance_ref"):
            findings.append(f"{code}:source_provenance_ref_missing")
            missing_evidence.append(f"taxonomy_mappings.{code}.source_provenance_ref")
        if mapping.get("aaos_control_category") != AAOS_CONTROL_CATEGORIES[code]:
            findings.append(f"{code}:aaos_control_category_mismatch")
        if mapping.get("periodic_reassessment_required") is not True:
            findings.append(f"{code}:periodic_reassessment_not_required")

        control_refs = _as_dict(mapping.get("decision_proof_control_refs"))
        for phase in REQUIRED_CHECKLIST_FIELDS:
            refs = _as_set(control_refs.get(phase))
            if not refs:
                findings.append(f"{code}:missing_{phase}_decision_proof_control_refs")
                continue
            invalid_refs = refs - checklist_fields.get(phase, set())
            for ref in sorted(invalid_refs):
                findings.append(f"{code}:unknown_{phase}_control_ref:{ref}")

        if code == "B6":
            b6_mapping_valid = (
                mapping.get("source_label") == B6_SOURCE_LABEL
                and mapping.get("aaos_control_category") == B6_CONTROL_CATEGORY
                and mapping.get("source_label_zh_tw") == SOURCE_LABELS_ZH_TW["B6"]
            )
            if mapping.get("source_label") != B6_SOURCE_LABEL:
                findings.append("b6_exact_source_label_mismatch")
            if mapping.get("aaos_control_category") != B6_CONTROL_CATEGORY:
                findings.append("b6_control_category_mismatch")

    taxonomy_complete = code_set == REQUIRED_TAXONOMY_CODES and len(codes) == len(code_set)
    return findings, missing_evidence, taxonomy_complete, b6_mapping_valid


def _evaluate_b6_first_class_control(
    artifact: dict[str, Any],
) -> tuple[list[str], list[str], bool]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    controls = [
        _as_dict(item) for item in _as_list(artifact.get("first_class_control_categories"))
    ]
    b6_controls = [item for item in controls if item.get("risk_code") == "B6"]

    if len(b6_controls) != 1:
        findings.append("b6_first_class_control_missing_or_duplicate")
        missing_evidence.append("first_class_control_categories.B6")
        return findings, missing_evidence, False

    b6 = b6_controls[0]
    if b6.get("source_label") != B6_SOURCE_LABEL:
        findings.append("b6_first_class_exact_source_label_mismatch")
    if b6.get("source_label_zh_tw") != SOURCE_LABELS_ZH_TW["B6"]:
        findings.append("b6_first_class_source_label_zh_tw_mismatch")
    if b6.get("aaos_control_category") != B6_CONTROL_CATEGORY:
        findings.append("b6_first_class_control_category_mismatch")

    required_fields = _as_set(b6.get("required_decision_proof_fields"))
    for field in sorted(B6_REQUIRED_DECISION_PROOF_FIELDS - required_fields):
        findings.append(f"b6_required_decision_proof_field_missing:{field}")
        missing_evidence.append(f"first_class_control_categories.B6.{field}")

    requirements = _as_dict(b6.get("requirements"))
    for requirement in sorted(B6_REQUIRED_BOOLEAN_REQUIREMENTS):
        if requirements.get(requirement) is not True:
            findings.append(f"b6_requirement_missing:{requirement}")
            missing_evidence.append(f"first_class_control_categories.B6.{requirement}")

    valid = not findings
    return findings, missing_evidence, valid


def _evaluate_serious_harm_boundary(
    artifact: dict[str, Any],
) -> tuple[list[str], list[str], bool]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    boundary = _as_dict(artifact.get("serious_harm_screening_boundary"))

    expectations = {
        "screening_required": True,
        "screening_output": "serious_harm_screening_required",
        "inherent_risk_screening_status": "inherent_risk_screened",
        "final_legal_determination_made": False,
        "risk_acceptance_made": False,
        "human_review_required": True,
    }
    for field, expected in expectations.items():
        if boundary.get(field) != expected:
            findings.append(f"serious_harm_boundary_invalid:{field}")
            missing_evidence.append(f"serious_harm_screening_boundary.{field}")
    if not _field_present(boundary, "reviewer_handoff"):
        findings.append("serious_harm_reviewer_handoff_missing")
        missing_evidence.append("serious_harm_screening_boundary.reviewer_handoff")

    return findings, missing_evidence, not findings


def _evaluate_periodic_reassessment_policy(
    artifact: dict[str, Any],
) -> tuple[list[str], list[str], bool]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    policy = _as_dict(artifact.get("periodic_reassessment_policy"))

    if policy.get("reassessment_required") is not True:
        findings.append("periodic_reassessment_policy_not_required")
    required_fields = _as_set(policy.get("required_fields"))
    for field in sorted(REQUIRED_REASSESSMENT_FIELDS - required_fields):
        findings.append(f"periodic_reassessment_required_field_missing:{field}")
        missing_evidence.append(f"periodic_reassessment_policy.required_fields.{field}")
    triggers = _as_set(policy.get("minimum_triggers"))
    for trigger in sorted(REQUIRED_REASSESSMENT_TRIGGERS - triggers):
        findings.append(f"periodic_reassessment_trigger_missing:{trigger}")
        missing_evidence.append(f"periodic_reassessment_policy.minimum_triggers.{trigger}")

    return findings, missing_evidence, not findings


def _evaluate_sector_scenarios(
    artifact: dict[str, Any],
) -> tuple[list[str], list[str], bool, list[dict[str, Any]]]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    scenarios = [_as_dict(item) for item in _as_list(artifact.get("sector_scenarios"))]
    sectors = [str(item.get("sector", "")) for item in scenarios]
    sector_set = set(sectors)

    for sector in sorted(REQUIRED_SECTORS - sector_set):
        findings.append(f"missing_sector_scenario:{sector}")
        missing_evidence.append(f"sector_scenarios.{sector}")
    for sector in sorted(sector_set - REQUIRED_SECTORS):
        findings.append(f"unexpected_sector_scenario:{sector}")
    if len(sectors) != len(sector_set):
        findings.append("duplicate_sector_scenario")

    scenario_results: list[dict[str, Any]] = []
    for scenario in scenarios:
        sector = str(scenario.get("sector", "missing_sector"))
        scenario_findings: list[str] = []

        for field in (
            "scenario_id",
            "scenario",
            "sensitive_data_scope",
            "serious_harm_screening",
            "decision_authority_boundary",
            "related_control_pattern",
            "decision_proof_status",
        ):
            if not _field_present(scenario, field):
                scenario_findings.append(f"{sector}:missing_{field}")

        mapped_codes = _as_set(scenario.get("mapped_risk_codes"))
        if not mapped_codes or not mapped_codes.issubset(REQUIRED_TAXONOMY_CODES):
            scenario_findings.append(f"{sector}:invalid_mapped_risk_codes")
        if "B6" not in mapped_codes:
            scenario_findings.append(f"{sector}:b6_mapping_missing")
        if scenario.get("serious_harm_screening") != "required_not_cleared_by_mapping":
            scenario_findings.append(f"{sector}:serious_harm_screening_boundary_invalid")

        reassessment = _as_dict(scenario.get("periodic_reassessment"))
        for field in REQUIRED_REASSESSMENT_FIELDS:
            if not _field_present(reassessment, field):
                scenario_findings.append(f"{sector}:missing_reassessment_field:{field}")
        if reassessment.get("reassessment_required") is not True:
            scenario_findings.append(f"{sector}:reassessment_not_required")
        if reassessment.get("source_framework_version_at_assessment") != "v1.0":
            scenario_findings.append(f"{sector}:reassessment_framework_version_mismatch")
        if not _as_list(reassessment.get("reassessment_triggers")):
            scenario_findings.append(f"{sector}:reassessment_triggers_missing")

        if sector == "healthcare":
            if scenario.get("sensitive_data_scope") != "restricted_health_and_personal_data":
                scenario_findings.append("healthcare:sensitive_data_scope_invalid")
            if scenario.get("human_review_required") is not True:
                scenario_findings.append("healthcare:human_review_required_missing")
            authority = _norm(scenario.get("decision_authority_boundary"))
            if "diagnosis" not in authority or "treatment" not in authority:
                scenario_findings.append("healthcare:diagnosis_treatment_boundary_missing")

        if sector == "finance":
            if scenario.get("analysis_capability") != "analysis_and_recommendation_only":
                scenario_findings.append("finance:analysis_capability_boundary_missing")
            if scenario.get("transaction_authority") != (
                "not_granted_by_analysis_capability_or_mapping"
            ):
                scenario_findings.append("finance:transaction_authority_boundary_missing")
            if scenario.get("transaction_execution_requires_separate_authorization") is not True:
                scenario_findings.append("finance:separate_transaction_authorization_missing")

        if sector in {"education", "labor"}:
            if scenario.get("human_review_required") is not True:
                scenario_findings.append(f"{sector}:human_review_required_missing")
            if scenario.get("appealability_required") is not True:
                scenario_findings.append(f"{sector}:appealability_required_missing")

        if sector == "government_service":
            if scenario.get("public_output_gate_required") is not True:
                scenario_findings.append("government_service:public_output_gate_missing")
            if "#204" not in str(scenario.get("related_control_pattern", "")):
                scenario_findings.append("government_service:pr_204_control_reference_missing")
            if scenario.get("public_output_gate_result") != "ready_for_review":
                scenario_findings.append("government_service:public_output_gate_result_invalid")
            if scenario.get("human_review_required") is not True:
                scenario_findings.append("government_service:human_review_required_missing")

        scenario_findings = _dedupe(scenario_findings)
        findings.extend(scenario_findings)
        scenario_results.append(
            {
                "sector": sector,
                "scenario_valid": not scenario_findings,
                "findings": scenario_findings,
            }
        )

    coverage_complete = sector_set == REQUIRED_SECTORS and len(sectors) == len(sector_set)
    return findings, missing_evidence, coverage_complete, scenario_results


def evaluate_moda_ai_risk_mapping_fixture(artifact: dict[str, Any]) -> dict[str, Any]:
    """Validate source provenance, control mapping, sector boundaries, and authority limits."""

    findings: list[str] = []
    missing_evidence: list[str] = []

    if not artifact:
        findings.append("moda_ai_risk_mapping_fixture_missing")
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

    provenance = _as_dict(artifact.get("source_provenance"))
    for field in (
        "issuing_authority",
        "publication_date",
        "notice_number",
        "official_notice_url",
        "official_pdf_url",
        "taxonomy_location",
        "provenance_policy",
    ):
        if not _field_present(provenance, field):
            findings.append(f"source_provenance_missing:{field}")
            missing_evidence.append(f"source_provenance.{field}")

    boundary_statements = _as_set(artifact.get("required_boundary_statements"))
    for boundary in sorted(REQUIRED_BOUNDARY_STATEMENTS - boundary_statements):
        findings.append(f"missing_boundary_statement:{boundary}")
        missing_evidence.append("required_boundary_statements")

    allowed_outputs = _as_set(artifact.get("allowed_evaluator_outputs"))
    for output in sorted(REQUIRED_ALLOWED_OUTPUTS - allowed_outputs):
        findings.append(f"missing_allowed_output:{output}")
        missing_evidence.append("allowed_evaluator_outputs")
    for output in sorted(allowed_outputs & FORBIDDEN_EVALUATOR_OUTPUTS):
        findings.append(f"forbidden_output_declared_allowed:{output}")

    forbidden_outputs = _as_set(artifact.get("forbidden_evaluator_outputs"))
    for output in sorted(FORBIDDEN_EVALUATOR_OUTPUTS - forbidden_outputs):
        findings.append(f"missing_forbidden_output:{output}")
        missing_evidence.append("forbidden_evaluator_outputs")

    checklist_fields, checklist_complete = _checklist_field_sets(
        artifact, findings, missing_evidence
    )

    mapping_findings, mapping_missing, taxonomy_complete, b6_mapping_valid = (
        _evaluate_taxonomy_mappings(artifact, checklist_fields)
    )
    findings.extend(mapping_findings)
    missing_evidence.extend(mapping_missing)

    b6_findings, b6_missing, b6_control_valid = _evaluate_b6_first_class_control(artifact)
    findings.extend(b6_findings)
    missing_evidence.extend(b6_missing)

    serious_findings, serious_missing, serious_boundary_valid = (
        _evaluate_serious_harm_boundary(artifact)
    )
    findings.extend(serious_findings)
    missing_evidence.extend(serious_missing)

    reassessment_findings, reassessment_missing, reassessment_policy_valid = (
        _evaluate_periodic_reassessment_policy(artifact)
    )
    findings.extend(reassessment_findings)
    missing_evidence.extend(reassessment_missing)

    sector_findings, sector_missing, sector_coverage_complete, scenario_results = (
        _evaluate_sector_scenarios(artifact)
    )
    findings.extend(sector_findings)
    missing_evidence.extend(sector_missing)

    _scan_for_forbidden_claims(artifact, findings)

    findings = _dedupe(findings)
    missing_evidence = _dedupe(missing_evidence)
    invalid = bool(findings)
    sectors = [_as_dict(item) for item in _as_list(artifact.get("sector_scenarios"))]

    return {
        "moda_ai_risk_mapping_valid": not invalid,
        "moda_ai_risk_mapping_invalid": invalid,
        "taxonomy_coverage_complete": taxonomy_complete,
        "taxonomy_coverage_incomplete": not taxonomy_complete,
        "decision_proof_checklist_complete": checklist_complete,
        "decision_proof_checklist_incomplete": not checklist_complete,
        "b6_first_class_control_present": b6_mapping_valid and b6_control_valid,
        "sector_coverage_complete": sector_coverage_complete,
        "sector_coverage_incomplete": not sector_coverage_complete,
        "serious_harm_screening_required": serious_boundary_valid,
        "human_review_required": any(
            scenario.get("human_review_required") is True for scenario in sectors
        ),
        "public_output_gate_required": any(
            scenario.get("public_output_gate_required") is True for scenario in sectors
        ),
        "periodic_reassessment_required": reassessment_policy_valid
        and all(
            _as_dict(scenario.get("periodic_reassessment")).get(
                "reassessment_required"
            )
            is True
            for scenario in sectors
        ),
        "ready_for_review": not invalid
        and all(scenario.get("decision_proof_status") == "ready_for_review" for scenario in sectors),
        "fail_closed_recommended": invalid,
        "rollback_recommended": invalid,
        "replay_required": all(
            _field_present(
                _as_dict(scenario.get("periodic_reassessment")), "replay_packet_id"
            )
            for scenario in sectors
        ),
        "escalation_required": invalid,
        "moda_ai_risk_mapping_findings": findings,
        "missing_evidence": missing_evidence,
        "scenario_results": scenario_results,
    }


def evaluate_moda_ai_risk_mapping(artifact: dict[str, Any]) -> dict[str, Any]:
    """Compatibility entry point for callers that omit the fixture suffix."""

    return evaluate_moda_ai_risk_mapping_fixture(artifact)
