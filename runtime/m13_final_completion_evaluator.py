"""Deterministic checks for M13 final completion release state."""

from __future__ import annotations

from typing import Any


EXPECTED_FIELDS = {
    "artifact_status": "final_completion_release_state_prepared",
    "milestone": "M13",
    "m13_completion_status": "complete",
    "related_issue": "#176",
    "tracker_issue_closure_state": "closes_on_merge",
    "tracker_issue_linkage": "Closes #176",
    "runtime_approval_gate_evidence_pr": "#177",
    "registry_drift_detection_pr": "#178",
    "authority_boundary_regression_fixtures_pr": "#194",
    "operational_readiness_checklist_pr": "#195",
    "external_consumer_onboarding_documentation_pr": "#196",
    "release_proof_linkage_specimen_pr": "#197",
    "completion_readiness_future_readme_path_pr": "#198",
    "introduced_after_release": "v0.11.0",
    "target_release": "v0.12.0",
    "release_status": "repository_release_state_prepared",
}

BOOLEAN_EXPECTATIONS = {
    "github_release_created_by_pr": False,
    "github_release_to_be_created_after_merge": True,
    "release_tag_created_by_pr": False,
    "m13_complete": True,
    "issue_176_closes_on_merge": True,
    "decision_proof_sealed_by_this_artifact": False,
}

EXPECTED_LINK_REFS = {
    "m13_tracker_issue": "#176",
    "runtime_enforced_approval_evidence_pr": "#177",
    "registry_drift_detection_pr": "#178",
    "authority_boundary_regression_fixtures_pr": "#194",
    "operational_readiness_checklist_pr": "#195",
    "external_consumer_onboarding_documentation_pr": "#196",
    "release_proof_linkage_specimen_pr": "#197",
    "completion_readiness_future_readme_path_pr": "#198",
    "prior_released_baseline": "v0.11.0",
    "target_release": "v0.12.0",
    "readme_release_state": "README.md",
    "tracker_issue_linkage": "Closes #176",
}

REQUIRED_M13_OUTPUTS = {
    "External Consumer Registry Hardening",
    "Runtime-Enforced Approval Evidence pattern",
    "Registry Drift Detection Specimen",
    "Authority-Boundary Regression Fixture Set",
    "Operational Readiness Checklist",
    "External Consumer Onboarding Documentation",
    "Release Proof Linkage Specimen",
    "Completion Readiness and README release-state path",
    "deterministic M13 evaluator coverage",
}

REQUIRED_BOUNDARY_STATEMENTS = {
    "Final completion records M13 completion but does not create a GitHub Release.",
    "GitHub Release v0.12.0 must be created only after this PR is merged.",
    "Release-state preparation is not GitHub Release publication.",
    "M13 completion does not transfer governance authority.",
    "README release entry is repository release-state preparation.",
    "Decision Proof sealing remains AAOS-owned.",
    "AAOS remains the decision sovereignty layer.",
    "External consumer registry artifacts do not seal Decision Proof.",
    "Evaluators do not make final governance judgments.",
    "Final governance authority remains AAOS-owned.",
}

ALLOWED_EVALUATOR_OUTPUTS = {
    "m13_final_completion_valid",
    "m13_final_completion_invalid",
    "m13_completion_declared",
    "issue_176_closes_on_merge",
    "repository_release_state_prepared",
    "github_release_pending_manual_publication",
    "review_required",
    "escalation_required",
}

FORBIDDEN_EVALUATOR_OUTPUTS = {
    "github_release_created",
    "release_tag_created_by_evaluator",
    "decision_proof_sealed_by_evaluator",
    "sealed_by_external_consumer",
    "authority_transferred",
    "risk_accepted_by_evaluator",
    "audit_closed_by_evaluator",
    "waiver_granted_by_evaluator",
    "final_governance_judgment_by_evaluator",
}

SAFE_CONTEXT_KEYS = {
    "allowed_evaluator_outputs",
    "forbidden_evaluator_outputs",
    "authority_boundary",
    "must_not",
    "required_boundary_statements",
    "semantic_boundaries",
}

README_RELEASE_ENTRY = (
    "- v0.12.0 — M13 External Consumer Registry Hardening and Operational Readiness"
)
README_STATUS = (
    "M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11, M12, and M13 are complete."
)
README_BASELINE_PHRASE = "the M13 External Consumer Registry Hardening and Operational Readiness pattern"
README_NEXT_PHASE = (
    "Future milestone planning will be tracked separately after v0.12.0 release publication."
)
README_ACTIVE_WORK_PHRASES = {
    "M13 remains active work",
    "final completion has not been declared",
    "Future README status path: v0.12.0 / M13 remains a future-only path",
}
README_COMPLETED_REFS = {
    "#176 M13 tracker issue",
    "#177 Runtime-Enforced Approval Gate Evidence for Decision Proof",
    "#178 Registry Drift Detection Specimen",
    "#194 Authority-Boundary Regression Fixtures",
    "#195 Operational Readiness Checklist",
    "#196 External Consumer Onboarding Documentation",
    "#197 Release Proof Linkage Specimen",
    "#198 Completion Readiness and Future README Path",
    "this final completion PR",
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
    if isinstance(value, (dict, list)):
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
    return [str(value).strip()]


def _section_between(text: str, start: str, end: str | None = None) -> str:
    start_index = text.find(start)
    if start_index == -1:
        return ""
    if end is None:
        return text[start_index:]
    end_index = text.find(end, start_index + len(start))
    if end_index == -1:
        return text[start_index:]
    return text[start_index:end_index]


def evaluate_m13_final_completion(
    artifact: dict[str, Any], readme_text: str | None = None
) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    boundary_violation = False

    def add_missing(finding: str, evidence: str) -> None:
        findings.append(finding)
        missing_evidence.append(evidence)

    if not artifact:
        add_missing("final_completion_artifact_missing", "artifact")

    for field in [
        "artifact_id",
        "artifact_name",
        "artifact_scope",
        "release_state_boundary",
        "artifact_links",
        "release_linkage_refs",
        "readme_release_state_updates",
        "m13_outputs",
        "deterministic_evaluator_references",
        "test_references",
        "required_boundary_statements",
        "semantic_boundaries",
        "allowed_evaluator_outputs",
        "forbidden_evaluator_outputs",
        "authority_boundary",
        "governance_boundary_statement",
        "release_boundary_statement",
        "decision_proof_sealing_boundary_statement",
        "aaos_retained_authority_statement",
        "sovereignty_statement",
    ]:
        if not _has_value(artifact, field):
            add_missing(f"missing_{field}", field)

    for field, expected in EXPECTED_FIELDS.items():
        if artifact.get(field) != expected:
            add_missing(f"missing_or_invalid_{field}", field)

    for field, expected in BOOLEAN_EXPECTATIONS.items():
        if artifact.get(field) is not expected:
            findings.append(f"invalid_{field}")
            if expected is False:
                boundary_violation = True

    release_state_boundary = _as_dict(artifact.get("release_state_boundary"))
    if release_state_boundary.get("repository_release_state_prepared") is not True:
        add_missing("repository_release_state_not_prepared", "release_state_boundary")
    if release_state_boundary.get("github_release_publication") != "manual_after_merge_only":
        add_missing("manual_github_release_publication_boundary_missing", "release_state_boundary")
    if release_state_boundary.get("release_state_preparation_is_publication") is not False:
        findings.append("release_state_preparation_publication_claim_detected")
        boundary_violation = True

    link_refs = _as_dict(artifact.get("release_linkage_refs"))
    for field, expected in EXPECTED_LINK_REFS.items():
        if link_refs.get(field) != expected:
            add_missing(f"missing_{field}", "release_linkage_refs")

    if not REQUIRED_M13_OUTPUTS <= _as_set(artifact.get("m13_outputs")):
        add_missing("m13_output_coverage_incomplete", "m13_outputs")

    if not REQUIRED_BOUNDARY_STATEMENTS <= _as_set(artifact.get("required_boundary_statements")):
        add_missing("required_boundary_statements_incomplete", "required_boundary_statements")
    if not ALLOWED_EVALUATOR_OUTPUTS <= _as_set(artifact.get("allowed_evaluator_outputs")):
        add_missing("allowed_evaluator_outputs_missing", "allowed_evaluator_outputs")
    if not FORBIDDEN_EVALUATOR_OUTPUTS <= _as_set(artifact.get("forbidden_evaluator_outputs")):
        add_missing("forbidden_evaluator_outputs_missing", "forbidden_evaluator_outputs")

    boundary_text = " ".join(
        str(artifact.get(field, ""))
        for field in [
            "governance_boundary_statement",
            "release_boundary_statement",
            "decision_proof_sealing_boundary_statement",
            "aaos_retained_authority_statement",
            "sovereignty_statement",
        ]
    ).lower()
    for phrase in [
        "m13 completion does not transfer governance authority",
        "does not create the github release",
        "does not create a release tag directly",
        "decision proof sealing remains aaos-owned",
        "aaos remains the decision sovereignty layer",
        "final governance authority",
    ]:
        if phrase not in boundary_text:
            add_missing("missing_final_completion_boundary_language", phrase)

    forbidden_claims = {
        text for text in _iter_claim_text(artifact) if text in FORBIDDEN_EVALUATOR_OUTPUTS
    }
    if forbidden_claims:
        findings.append("forbidden_evaluator_output_claim_detected")
        boundary_violation = True

    if artifact.get("github_release_created_by_pr") is True:
        findings.append("github_release_created_by_pr_claim_detected")
        boundary_violation = True
    if artifact.get("release_tag_created_by_pr") is True:
        findings.append("release_tag_created_by_pr_claim_detected")
        boundary_violation = True
    if artifact.get("decision_proof_sealed_by_this_artifact") is True:
        findings.append("decision_proof_sealed_by_artifact_claim_detected")
        boundary_violation = True

    readme_valid = True
    if readme_text is not None:
        readme_result = _evaluate_readme(readme_text)
        findings.extend(readme_result["findings"])
        missing_evidence.extend(readme_result["missing_evidence"])
        boundary_violation = boundary_violation or readme_result["boundary_violation"]
        readme_valid = readme_result["readme_valid"]

    completion_declared = (
        artifact.get("m13_complete") is True
        and artifact.get("m13_completion_status") == "complete"
        and readme_valid
    )
    issue_closes = (
        artifact.get("tracker_issue_linkage") == "Closes #176"
        and artifact.get("issue_176_closes_on_merge") is True
    )
    release_state_prepared = artifact.get("release_status") == "repository_release_state_prepared"
    release_pending_manual = (
        artifact.get("github_release_created_by_pr") is False
        and artifact.get("github_release_to_be_created_after_merge") is True
        and artifact.get("release_tag_created_by_pr") is False
    )

    failed = bool(findings or missing_evidence or boundary_violation)
    return {
        "m13_final_completion_valid": not failed,
        "m13_final_completion_invalid": failed,
        "m13_completion_declared": completion_declared and not failed,
        "issue_176_closes_on_merge": issue_closes and not failed,
        "repository_release_state_prepared": release_state_prepared and not failed,
        "github_release_pending_manual_publication": release_pending_manual and not failed,
        "final_completion_findings": sorted(set(findings)),
        "missing_evidence": sorted(set(missing_evidence)),
        "review_required": failed,
        "escalation_required": boundary_violation,
    }


def _evaluate_readme(readme_text: str) -> dict[str, Any]:
    findings: list[str] = []
    missing_evidence: list[str] = []
    boundary_violation = False

    if README_RELEASE_ENTRY not in readme_text:
        add = "readme_v0_12_0_release_entry_missing"
        findings.append(add)
        missing_evidence.append("README.md#releases")
    if README_BASELINE_PHRASE not in readme_text:
        findings.append("readme_m13_baseline_missing")
        missing_evidence.append("README.md#current-baseline")
    if README_STATUS not in readme_text:
        findings.append("readme_m13_completion_status_missing")
        missing_evidence.append("README.md#current-status")

    m13_section = _section_between(readme_text, "M13 completed:", "AAOS Public now has:")
    if not m13_section:
        findings.append("readme_m13_completed_section_missing")
        missing_evidence.append("README.md#m13-completed")
    else:
        for ref in README_COMPLETED_REFS:
            if ref not in m13_section:
                findings.append("readme_m13_completed_ref_missing")
                missing_evidence.append(ref)

    now_has_section = _section_between(readme_text, "AAOS Public now has:", "## M5 Additions")
    for output in REQUIRED_M13_OUTPUTS:
        if output not in now_has_section:
            findings.append("readme_m13_output_missing")
            missing_evidence.append(output)

    next_phase = _section_between(readme_text, "## Next Phase", None)
    if README_NEXT_PHASE not in next_phase:
        findings.append("readme_next_phase_final_planning_missing")
        missing_evidence.append("README.md#next-phase")
    if any(phrase in next_phase for phrase in README_ACTIVE_WORK_PHRASES):
        findings.append("readme_next_phase_m13_active_work_claim_detected")
        boundary_violation = True

    for phrase in [
        "Decision Proof sealing remains AAOS-owned.",
        "AAOS remains the decision sovereignty layer.",
    ]:
        if phrase not in readme_text:
            findings.append("readme_governance_boundary_statement_missing")
            missing_evidence.append(phrase)

    return {
        "readme_valid": not findings and not missing_evidence and not boundary_violation,
        "findings": findings,
        "missing_evidence": missing_evidence,
        "boundary_violation": boundary_violation,
    }
