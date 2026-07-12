"""Deterministic, data-only M14 authority-boundary regression evaluator.

This module composes inert fixture records and caller-supplied source text.  It
does not import or execute the five source evaluators, execute workflows or
skills, invoke a shell, or perform network access.  Its outputs are explicitly
non-authoritative routing and review evidence; they are never approvals.
"""

from __future__ import annotations

import copy
import re
from typing import Any, Mapping, Sequence


COMPONENT_ORDER = (
    "voice_runtime_policy",
    "public_output_exfiltration_gate",
    "moda_risk_mapping",
    "ai_pr_provenance",
    "skill_admission",
)

INTENDED_CHANGED_FILES = (
    "examples/public-integration-pack-pilot/"
    "m14-cross-control-authority-boundary-regression-fixtures.json",
    "runtime/m14_cross_control_authority_boundary_evaluator.py",
    "tests/test_m14_cross_control_authority_boundary_evaluator.py",
)

EXPECTED_COMPONENTS: dict[str, dict[str, Any]] = {
    "voice_runtime_policy": {
        "source_pr": "#202",
        "component_role": "governed_voice_runtime_policy_gate",
        "source_paths": (
            "examples/public-integration-pack-pilot/voxcpm-governed-voice-fixtures.json",
            "runtime/voice_generation_policy_evaluator.py",
            "tests/test_voice_generation_policy_evaluator.py",
        ),
        "source_boundary_requirements": (
            "Runtime capability is not governance permission.",
            "Consent evidence is not approval.",
            "Policy gate pass is not final governance judgment.",
            "ready_for_review is not approval.",
            "Decision Proof sealing remains AAOS-owned.",
            "AAOS remains the decision sovereignty layer.",
        ),
    },
    "public_output_exfiltration_gate": {
        "source_pr": "#204",
        "component_role": "public_output_exfiltration_gate",
        "source_paths": (
            "examples/public-integration-pack-pilot/"
            "m14-public-issue-exfiltration-gate-fixtures.json",
            "runtime/public_issue_exfiltration_gate_evaluator.py",
            "tests/test_public_issue_exfiltration_gate_evaluator.py",
        ),
        "source_boundary_requirements": (
            "Public issue bodies, PR comments, discussions, and external markdown are untrusted input.",
            "A public trigger must not grant private repository or organization-wide read context by default.",
            "output_gate_pass is not public disclosure approval.",
            "human_review_required is not audit closure.",
            "fail_closed_recommended is not fail_closed_executed.",
            "Decision Proof sealing remains AAOS-owned.",
            "AAOS remains the decision sovereignty layer.",
        ),
    },
    "moda_risk_mapping": {
        "source_pr": "#205",
        "component_role": "external_regulatory_risk_taxonomy_mapping",
        "source_paths": (
            "docs/public-integration-pack/m14-moda-ai-risk-framework-mapping.md",
            "examples/public-integration-pack-pilot/"
            "m14-moda-ai-risk-decision-proof-fixtures.json",
            "runtime/moda_ai_risk_mapping_evaluator.py",
            "tests/test_moda_ai_risk_mapping_evaluator.py",
        ),
        "source_boundary_requirements": (
            "Regulatory mapping is not legal approval.",
            "Taxonomy mapping is not compliance certification.",
            "Control coverage complete is not deployment approval.",
            "Serious-harm screening is not final legal determination.",
            "ready_for_review is not regulated deployment approval.",
            "Decision Proof sealing remains AAOS-owned.",
            "AAOS remains the decision sovereignty layer.",
        ),
    },
    "ai_pr_provenance": {
        "source_pr": "#206",
        "component_role": "ai_pr_provenance_and_reviewer_routing",
        "source_paths": (
            ".github/workflows/m14-ai-pr-provenance.yml",
            "examples/public-integration-pack-pilot/"
            "m14-ai-authored-pr-provenance-fixtures.json",
            "runtime/ai_authored_pr_provenance_evaluator.py",
            "tests/test_ai_authored_pr_provenance_evaluator.py",
        ),
        "source_boundary_requirements": (
            "AI-authored detection is provenance evidence, not identity proof.",
            "pr-by-ai is not approval.",
            "human-review-required is not completed review.",
            "Reviewer routing is not review approval.",
            "Workflow success is not merge approval.",
            "Decision Proof sealing remains AAOS-owned.",
            "AAOS remains the decision sovereignty layer.",
        ),
    },
    "skill_admission": {
        "source_pr": "#208",
        "component_role": "external_skill_capability_admission_gate",
        "source_paths": (
            "docs/capability-supply-chain/nvidia-skills-admission.md",
            "examples/public-integration-pack-pilot/m14-skill-admission-fixtures.json",
            "runtime/skill_admission_evaluator.py",
            "tests/test_skill_admission_evaluator.py",
        ),
        "source_boundary_requirements": (
            "External skill capability is not governance permission.",
            "Skill installation is not execution authorization.",
            "Artifact signature is not governance approval.",
            "Scan passed is not risk accepted.",
            "admission_ready_for_review is not final admission approval.",
            "Decision Proof sealing remains AAOS-owned.",
            "AAOS remains the decision sovereignty layer.",
        ),
    },
}

EXPECTED_TOP_LEVEL_FIELDS = {
    "fixture_status": "m14_active_work_not_complete",
    "tracker_issue": "#201",
    "tracker_issue_linkage": "Refs #201",
    "related_voice_runtime_pr": "#202",
    "related_public_output_gate_pr": "#204",
    "related_moda_mapping_pr": "#205",
    "related_ai_pr_provenance_pr": "#206",
    "related_skill_admission_pr": "#208",
    "authority_boundary_scope": "cross_control_composition_regression",
    "m14_completion_status": "active_work_not_complete",
    "target_future_release": "v0.13.0",
}

FALSE_AUTHORITY_AND_EXECUTION_FIELDS = (
    "external_execution_performed",
    "workflow_execution_performed",
    "public_comment_posted",
    "risk_accepted_by_fixture",
    "final_action_approved_by_fixture",
    "fail_closed_executed_by_fixture",
    "rollback_executed_by_fixture",
    "audit_closed_by_fixture",
    "authority_transferred_by_fixture",
    "final_governance_judgment_made_by_fixture",
    "decision_proof_sealed_by_fixture",
)

MATRIX_REQUIRED_FIELDS = {
    "component_id",
    "source_pr",
    "component_role",
    "source_paths",
    "input_evidence_classes",
    "permitted_operations",
    "advisory_outputs",
    "prohibited_operations",
    "prohibited_authority_claims",
    "escalation_route",
    "retained_authority_owner",
    "decision_proof_sealing_owner",
}

ALLOWED_COMPONENT_OPERATIONS = {
    "capture",
    "inspect",
    "classify",
    "validate_structure",
    "detect_risk",
    "detect_policy_mismatch",
    "block_output",
    "recommend_fail_closed",
    "recommend_rollback",
    "request_human_review",
    "request_reviewer_routing",
    "preserve_trace",
    "preserve_replay_metadata",
    "report_readiness_for_review",
}

REQUIRED_COMPOSITION_RULES = {
    "no_authority_by_aggregation",
    "capability_is_not_permission",
    "consent_evidence_is_not_approval",
    "provenance_is_not_identity_proof",
    "regulatory_mapping_is_not_legal_approval",
    "taxonomy_coverage_is_not_compliance_certification",
    "signature_is_not_governance_approval",
    "scan_is_not_risk_acceptance",
    "benchmark_is_not_deployment_approval",
    "policy_gate_pass_is_scope_limited",
    "ready_for_review_is_not_approval",
    "reviewer_routing_is_not_review_approval",
    "workflow_success_is_not_merge_approval",
    "public_output_gate_pass_is_not_disclosure_approval",
    "fail_closed_recommended_is_not_fail_closed_executed",
    "rollback_recommended_is_not_rollback_executed",
    "human_review_required_is_not_audit_closure",
    "replay_ready_is_not_decision_proof_sealing",
    "evidence_complete_is_not_decision_proof_sealing",
    "most_restrictive_applicable_control_is_preserved",
    "authority_cannot_be_transferred_by_field_renaming",
    "forbidden_claims_remain_forbidden_when_nested",
    "forbidden_claims_remain_forbidden_when_multiple_components_agree",
    "decision_proof_sealing_remains_aaos_owned",
    "aaos_remains_decision_sovereignty_layer",
}

REQUIRED_BOUNDARY_STATEMENTS = {
    "Multiple non-authoritative outputs do not aggregate into governance authority.",
    "Five passed gates are not final approval.",
    "Evidence accumulation does not create authority by aggregation.",
    "Capability is not permission.",
    "Consent evidence is not approval.",
    "Provenance is not identity proof.",
    "Regulatory mapping is not legal approval.",
    "Taxonomy coverage is not compliance certification.",
    "Artifact signature is not governance approval.",
    "Scan passed is not risk accepted.",
    "Benchmark passed is not deployment approval.",
    "ready_for_review is not approval.",
    "Reviewer routing is not review approval.",
    "Workflow success is not merge approval.",
    "output_gate_pass is not public disclosure approval.",
    "fail_closed_recommended is not fail_closed_executed.",
    "rollback_recommended is not rollback_executed.",
    "human_review_required is not audit closure.",
    "evidence_complete is not Decision Proof sealing.",
    "replay_ready is not Decision Proof sealing.",
    "Source evaluators remain bounded evidence evaluators.",
    "Decision Proof sealing remains AAOS-owned.",
    "AAOS remains the decision sovereignty layer.",
}

ALLOWED_EVALUATOR_OUTPUTS = {
    "m14_authority_boundary_fixture_valid",
    "m14_authority_boundary_fixture_invalid",
    "cross_control_boundary_valid",
    "cross_control_boundary_invalid",
    "component_boundary_valid",
    "component_boundary_invalid",
    "composition_not_authoritative",
    "most_restrictive_control_preserved",
    "human_review_required",
    "fail_closed_recommended",
    "rollback_recommended",
    "source_boundary_drift_detected",
    "authority_violation_detected",
    "ready_for_m14_readiness_review",
    "not_ready",
    "escalation_required",
}

FORBIDDEN_EVALUATOR_OUTPUTS = {
    "voice_clone_approved",
    "impersonation_approved",
    "public_disclosure_approved",
    "regulated_deployment_approved",
    "legal_approval_granted",
    "compliance_certified",
    "risk_accepted",
    "identity_proven",
    "review_approved",
    "merge_approved",
    "installation_approved",
    "skill_execution_approved",
    "deployment_approved",
    "final_action_approved",
    "fail_closed_executed",
    "rollback_executed",
    "audit_closed",
    "waiver_granted",
    "decision_proof_verified",
    "decision_proof_sealed",
    "sealed_by_voice_runtime",
    "sealed_by_output_gate",
    "sealed_by_regulatory_mapping",
    "sealed_by_provenance_workflow",
    "sealed_by_skill_registry",
    "sealed_by_evaluator",
    "authority_transferred",
    "final_governance_judgment",
    "m14_complete",
    "v0_13_0_released",
    "closes_201",
}

RESULT_LATTICE = {
    "passed_scope_limited": 0,
    "ready_for_review": 1,
    "restricted": 2,
    "human_review_required": 3,
    "escalation_required": 4,
    "blocked": 5,
}
RESULT_BY_RANK = {rank: result for result, rank in RESULT_LATTICE.items()}

REQUIRED_CASE_PREFIXES = tuple(f"case_{index:02d}_" for index in range(1, 29))

INERT_TOP_LEVEL_DECLARATION_FIELDS = frozenset(
    {
        "allowed_evaluator_outputs",
        "baseline_component_results",
        "component_authority_matrix",
        "composition_rules",
        "cross_control_cases",
        "forbidden_evaluator_outputs",
        "intended_files",
        "required_boundary_statements",
        "result_precedence",
        "source_artifact_manifest",
    }
)


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _dedupe(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _normalized_operation(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).strip().casefold()).strip("_")


def _normalized_path(value: Any) -> str:
    return str(value).strip().replace("\\", "/")


def _truthy_claim(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    if isinstance(value, str):
        return value.strip().casefold() not in {"", "false", "none", "not_granted", "aaos"}
    return bool(value)


def _walk(value: Any, path: str = "$"):
    yield path, None, value
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            yield child_path, str(key), child
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            yield from _walk(child, child_path)


def detect_authority_violations(value: Any) -> list[str]:
    """Return recursive authority findings for an active runtime payload.

    Declaration lists, expected values, boundary prose, and dormant fixture
    cases must not be passed to this function.  The public evaluators below
    apply it only to active component payloads, active claims, and simulated
    outputs.
    """

    findings: list[str] = []
    for path, key, child in _walk(value):
        normalized_key = _normalized_operation(key) if key is not None else ""
        normalized_path = _normalized_operation(path)
        normalized_value = (
            _normalized_operation(child) if isinstance(child, str) else ""
        )

        if normalized_key in FORBIDDEN_EVALUATOR_OUTPUTS:
            findings.append(f"forbidden_authority_key:{path}:{normalized_key}")
        if normalized_value in FORBIDDEN_EVALUATOR_OUTPUTS:
            findings.append(f"forbidden_authority_value:{path}:{normalized_value}")
        if isinstance(child, str):
            if (
                normalized_value.endswith("_approved")
                or normalized_value.endswith("_approval_granted")
                or normalized_value.endswith("_certified")
                or normalized_value.startswith("sealed_by_")
            ):
                findings.append(f"renamed_authority_value:{path}:{normalized_value}")
            if normalized_value in {
                "delegated_final_authority",
                "delegated_governance_authority",
                "transferred_authority",
                "local_final_authority",
            }:
                findings.append(f"renamed_authority_transfer_value:{path}")
            approval_context_tokens = {
                "activation",
                "approval",
                "authority",
                "decision",
                "deployment",
                "disclosure",
                "execution",
                "governance",
                "installation",
                "merge",
                "permission",
                "release",
                "review",
                "risk",
                "state",
                "status",
                "waiver",
            }
            if normalized_value in {"approved", "granted"} and (
                set(normalized_path.split("_")) & approval_context_tokens
            ):
                findings.append(
                    f"renamed_approval_value:{path}:{normalized_value}"
                )

        if key is not None and _truthy_claim(child):
            if (
                normalized_key.endswith("_approved")
                or normalized_key.endswith("_approval_granted")
                or normalized_key.endswith("_certified")
                or normalized_key.startswith("sealed_by_")
            ):
                findings.append(f"renamed_authority_claim:{path}:{normalized_key}")
            if normalized_key in {
                "delegated_final_authority",
                "delegated_governance_authority",
                "transferred_authority",
                "local_final_authority",
            }:
                findings.append(f"renamed_authority_transfer:{path}:{normalized_key}")
            if "final_authority" in normalized_key and normalized_key not in {
                "retained_final_authority_owner",
            }:
                findings.append(f"final_authority_claim:{path}:{normalized_key}")
            if normalized_key.endswith("authority_owner") and str(child).strip() != "AAOS":
                findings.append(f"local_authority_owner_claim:{path}")
            if normalized_key.endswith("sealing_owner") and str(child).strip() != "AAOS":
                findings.append(f"local_sealing_owner_claim:{path}")
            if "approval" in normalized_key and normalized_value in {
                "approved",
                "granted",
                "final",
                "true",
            }:
                findings.append(f"renamed_approval_claim:{path}:{normalized_key}")

    return _dedupe(findings)


def _manifest_entries(fixture: Mapping[str, Any]) -> tuple[list[dict[str, Any]], bool]:
    manifest = fixture.get("source_artifact_manifest")
    if isinstance(manifest, list):
        return [item if isinstance(item, dict) else {} for item in manifest], True
    if isinstance(manifest, dict):
        entries = []
        for component_id in COMPONENT_ORDER:
            item = manifest.get(component_id)
            if isinstance(item, dict):
                normalized = dict(item)
                normalized.setdefault("component_id", component_id)
                entries.append(normalized)
        return entries, False
    return [], False


def _matrix_entries(matrix: Any) -> tuple[list[dict[str, Any]], bool]:
    if isinstance(matrix, list):
        return [item if isinstance(item, dict) else {} for item in matrix], True
    if isinstance(matrix, dict):
        entries = []
        for component_id in COMPONENT_ORDER:
            item = matrix.get(component_id)
            if isinstance(item, dict):
                normalized = dict(item)
                normalized.setdefault("component_id", component_id)
                entries.append(normalized)
        return entries, False
    return [], False


def _validate_manifest(fixture: Mapping[str, Any]) -> list[str]:
    findings: list[str] = []
    entries, canonical_list = _manifest_entries(fixture)
    if not canonical_list:
        findings.append("source_artifact_manifest_must_be_list")
    ids = [str(entry.get("component_id", "")) for entry in entries]
    if ids != list(COMPONENT_ORDER):
        findings.append("source_artifact_manifest_components_or_order_invalid")
    if len(ids) != len(set(ids)):
        findings.append("source_artifact_manifest_duplicate_component")

    for component_id in COMPONENT_ORDER:
        expected = EXPECTED_COMPONENTS[component_id]
        matches = [entry for entry in entries if entry.get("component_id") == component_id]
        if len(matches) != 1:
            findings.append(f"source_artifact_manifest_component_missing:{component_id}")
            continue
        entry = matches[0]
        if entry.get("source_pr") != expected["source_pr"]:
            findings.append(f"source_pr_invalid:{component_id}")
        if entry.get("component_role") != expected["component_role"]:
            findings.append(f"component_role_invalid:{component_id}")
        paths = entry.get("source_paths")
        normalized_paths = (
            [_normalized_path(path) for path in paths] if isinstance(paths, list) else []
        )
        if normalized_paths != list(expected["source_paths"]):
            findings.append(f"source_paths_invalid:{component_id}")
        requirements = entry.get("source_boundary_requirements")
        normalized_requirements = requirements if isinstance(requirements, list) else []
        if (
            len(normalized_requirements) != len(set(normalized_requirements))
            or set(normalized_requirements)
            != set(expected["source_boundary_requirements"])
        ):
            findings.append(f"source_boundary_requirements_invalid:{component_id}")
    return findings


def _validate_matrix(matrix: Any) -> list[str]:
    findings: list[str] = []
    entries, canonical_list = _matrix_entries(matrix)
    if not canonical_list:
        findings.append("component_authority_matrix_must_be_list")
    ids = [str(entry.get("component_id", "")) for entry in entries]
    if ids != list(COMPONENT_ORDER):
        findings.append("component_authority_matrix_components_or_order_invalid")
    if len(ids) != len(set(ids)):
        findings.append("component_authority_matrix_duplicate_component")

    for component_id in COMPONENT_ORDER:
        matches = [entry for entry in entries if entry.get("component_id") == component_id]
        if len(matches) != 1:
            findings.append(f"component_authority_declaration_missing:{component_id}")
            continue
        entry = matches[0]
        expected = EXPECTED_COMPONENTS[component_id]
        for field in sorted(MATRIX_REQUIRED_FIELDS):
            if field not in entry:
                findings.append(f"component_authority_field_missing:{component_id}:{field}")
        if entry.get("source_pr") != expected["source_pr"]:
            findings.append(f"component_authority_source_pr_invalid:{component_id}")
        if entry.get("component_role") != expected["component_role"]:
            findings.append(f"component_authority_role_invalid:{component_id}")
        paths = entry.get("source_paths")
        normalized_paths = (
            [_normalized_path(path) for path in paths] if isinstance(paths, list) else []
        )
        if normalized_paths != list(expected["source_paths"]):
            findings.append(f"component_authority_source_paths_invalid:{component_id}")

        for field in (
            "input_evidence_classes",
            "permitted_operations",
            "advisory_outputs",
            "prohibited_operations",
            "prohibited_authority_claims",
        ):
            value = entry.get(field)
            if not isinstance(value, list) or not value:
                findings.append(f"component_authority_list_invalid:{component_id}:{field}")
            elif len(value) != len({str(item) for item in value}):
                findings.append(f"component_authority_list_duplicate:{component_id}:{field}")

        permitted = {
            _normalized_operation(operation)
            for operation in _as_list(entry.get("permitted_operations"))
        }
        invalid_permitted = sorted(permitted - ALLOWED_COMPONENT_OPERATIONS)
        for operation in invalid_permitted:
            findings.append(
                f"component_permitted_operation_exceeds_boundary:{component_id}:{operation}"
            )
        if entry.get("retained_authority_owner") != "AAOS":
            findings.append(f"retained_authority_owner_invalid:{component_id}")
        if entry.get("decision_proof_sealing_owner") != "AAOS":
            findings.append(f"decision_proof_sealing_owner_invalid:{component_id}")
        if not isinstance(entry.get("escalation_route"), str) or not str(
            entry.get("escalation_route")
        ).strip():
            findings.append(f"component_escalation_route_invalid:{component_id}")
    return findings


def _validate_fixture_structure(fixture: Mapping[str, Any]) -> list[str]:
    findings: list[str] = []
    if not isinstance(fixture, dict):
        return ["fixture_must_be_object"]

    for field, expected in EXPECTED_TOP_LEVEL_FIELDS.items():
        if fixture.get(field) != expected:
            findings.append(f"top_level_field_invalid:{field}")
    release_path = fixture.get("future_release_tag_path")
    if not isinstance(release_path, dict) or release_path.get("released") is not False:
        findings.append("future_release_tag_path_released_must_be_false")
    for field in FALSE_AUTHORITY_AND_EXECUTION_FIELDS:
        if fixture.get(field) is not False:
            findings.append(f"top_level_false_boundary_invalid:{field}")

    changed_files = fixture.get("intended_files")
    if not isinstance(changed_files, list) or changed_files != list(INTENDED_CHANGED_FILES):
        findings.append("intended_files_invalid")

    findings.extend(_validate_manifest(fixture))
    findings.extend(_validate_matrix(fixture.get("component_authority_matrix")))

    rules = fixture.get("composition_rules")
    if not isinstance(rules, list):
        findings.append("composition_rules_must_be_list")
        rule_ids: list[str] = []
    else:
        rule_ids = [str(rule) if isinstance(rule, str) else "" for rule in rules]
    if len(rule_ids) != len(set(rule_ids)) or set(rule_ids) != REQUIRED_COMPOSITION_RULES:
        findings.append("composition_rules_incomplete_or_duplicate")

    boundary_statements = fixture.get("required_boundary_statements")
    boundaries = set(boundary_statements) if isinstance(boundary_statements, list) else set()
    if not REQUIRED_BOUNDARY_STATEMENTS.issubset(boundaries):
        findings.append("required_boundary_statements_incomplete")

    allowed = fixture.get("allowed_evaluator_outputs")
    forbidden = fixture.get("forbidden_evaluator_outputs")
    allowed_set = set(allowed) if isinstance(allowed, list) else set()
    forbidden_set = set(forbidden) if isinstance(forbidden, list) else set()
    if allowed_set != ALLOWED_EVALUATOR_OUTPUTS or len(_as_list(allowed)) != len(allowed_set):
        findings.append("allowed_evaluator_outputs_invalid")
    if forbidden_set != FORBIDDEN_EVALUATOR_OUTPUTS or len(_as_list(forbidden)) != len(
        forbidden_set
    ):
        findings.append("forbidden_evaluator_outputs_invalid")
    if allowed_set & forbidden_set:
        findings.append("allowed_and_forbidden_outputs_overlap")

    cases = fixture.get("cross_control_cases")
    if not isinstance(cases, list):
        findings.append("cross_control_cases_must_be_list")
        case_ids: list[str] = []
    else:
        case_ids = [
            str(case.get("case_id", "")) if isinstance(case, dict) else ""
            for case in cases
        ]
    prefixes_complete = all(
        sum(case_id.startswith(prefix) for case_id in case_ids) == 1
        for prefix in REQUIRED_CASE_PREFIXES
    )
    if (
        len(case_ids) != 28
        or len(case_ids) != len(set(case_ids))
        or not prefixes_complete
    ):
        findings.append("cross_control_cases_incomplete_or_order_invalid")

    return _dedupe(findings)


def validate_source_boundaries(
    fixture: Mapping[str, Any], source_artifacts: Mapping[str, str] | None
) -> dict[str, Any]:
    """Validate source boundaries from caller-supplied inert UTF-8 text."""

    findings: list[str] = []
    component_status: dict[str, bool] = {}
    artifacts = source_artifacts if isinstance(source_artifacts, Mapping) else {}
    normalized_artifacts = {
        _normalized_path(path): text
        for path, text in artifacts.items()
        if isinstance(path, str)
    }
    entries, _ = _manifest_entries(fixture)
    entries_by_id = {
        str(entry.get("component_id")): entry
        for entry in entries
        if entry.get("component_id")
    }

    for component_id in COMPONENT_ORDER:
        expected = EXPECTED_COMPONENTS[component_id]
        entry = entries_by_id.get(component_id)
        component_findings: list[str] = []
        if not entry:
            component_findings.append(f"source_manifest_component_missing:{component_id}")
        else:
            paths = entry.get("source_paths")
            if not isinstance(paths, list):
                component_findings.append(f"source_paths_missing:{component_id}")
                paths = []
            normalized_paths = [_normalized_path(path) for path in paths]
            if normalized_paths != list(expected["source_paths"]):
                component_findings.append(f"source_path_set_drift:{component_id}")

            source_texts: list[str] = []
            for path in normalized_paths:
                if path not in normalized_artifacts:
                    component_findings.append(f"source_artifact_missing:{component_id}:{path}")
                    continue
                text = normalized_artifacts[path]
                if not isinstance(text, str):
                    component_findings.append(f"source_artifact_not_text:{component_id}:{path}")
                    continue
                source_texts.append(text)

            declared_requirements = entry.get("source_boundary_requirements")
            requirements = (
                declared_requirements if isinstance(declared_requirements, list) else []
            )
            if set(requirements) != set(expected["source_boundary_requirements"]):
                component_findings.append(
                    f"source_boundary_requirement_set_drift:{component_id}"
                )
            group_text = "\n".join(source_texts).casefold()
            for statement in requirements:
                if not isinstance(statement, str) or statement.casefold() not in group_text:
                    component_findings.append(
                        f"source_boundary_statement_missing:{component_id}:{statement}"
                    )

        component_status[component_id] = not component_findings
        findings.extend(component_findings)

    findings = _dedupe(findings)
    return {
        "source_boundary_drift_detected": bool(findings),
        "source_boundary_findings": findings,
        "component_source_boundaries": component_status,
    }


def _classify_output_token(token: Any) -> int | None:
    normalized = _normalized_operation(token)
    if not normalized:
        return None
    if normalized in RESULT_LATTICE:
        return RESULT_LATTICE[normalized]
    if normalized in {
        "candidate_blocked",
        "public_output_blocked",
        "output_blocked",
        "policy_gate_blocked",
        "admission_blocked",
        "skill_admission_fixture_invalid",
        "moda_ai_risk_mapping_invalid",
        "ai_pr_provenance_invalid",
        "voice_policy_fixture_invalid",
        "public_issue_exfiltration_gate_invalid",
    }:
        return RESULT_LATTICE["blocked"]
    if normalized.endswith("_blocked"):
        return RESULT_LATTICE["blocked"]
    if normalized in {
        "escalation_required",
        "needs_approval",
        "needs_sandbox",
        "needs_signature_verification",
        "needs_scan",
        "needs_evaluation",
        "stale_reassessment_required",
    }:
        return RESULT_LATTICE["escalation_required"]
    if normalized in {
        "human_review_required",
        "needs_human_review",
        "reviewer_routing_required",
        "serious_harm_screening_required",
    }:
        return RESULT_LATTICE["human_review_required"]
    if normalized in {
        "candidate_restricted",
        "admission_not_ready",
        "not_ready",
        "needs_replay_log",
    }:
        return RESULT_LATTICE["restricted"]
    if normalized in {
        "ready_for_review",
        "admission_ready_for_review",
    }:
        return RESULT_LATTICE["ready_for_review"]
    if normalized in {
        "passed",
        "pass",
        "output_gate_pass",
        "policy_gate_pass",
        "candidate_allowed",
        "evidence_complete",
        "replay_ready",
        "workflow_success",
        "taxonomy_coverage_complete",
        "component_boundary_valid",
    }:
        return RESULT_LATTICE["passed_scope_limited"]
    return None


def _derived_rank(value: Any) -> int:
    rank = RESULT_LATTICE["passed_scope_limited"]
    if isinstance(value, dict):
        for key, child in value.items():
            if child is True or (isinstance(child, str) and child.strip()):
                classified_key = _classify_output_token(key)
                if classified_key is not None:
                    rank = max(rank, classified_key)
            rank = max(rank, _derived_rank(child))
    elif isinstance(value, list):
        for child in value:
            rank = max(rank, _derived_rank(child))
    elif isinstance(value, str):
        classified = _classify_output_token(value)
        if classified is not None:
            rank = max(rank, classified)
    return rank


def evaluate_component_results(component_results: Any, matrix: Any) -> dict[str, Any]:
    """Compose component records while preserving the strongest applicable state."""

    findings: list[str] = []
    authority_findings: list[str] = []
    results = component_results if isinstance(component_results, list) else []
    if not isinstance(component_results, list):
        findings.append("component_results_must_be_list")

    entries, _ = _matrix_entries(matrix)
    matrix_by_id = {
        str(entry.get("component_id")): entry
        for entry in entries
        if entry.get("component_id")
    }
    result_ids = [
        str(result.get("component_id", "")) if isinstance(result, dict) else ""
        for result in results
    ]
    if result_ids != list(COMPONENT_ORDER):
        findings.append("component_results_components_or_order_invalid")
    if len(result_ids) != len(set(result_ids)):
        findings.append("component_results_duplicate_component")

    evaluated_results: list[dict[str, Any]] = []
    maximum_rank = RESULT_LATTICE["passed_scope_limited"]
    preserved_ids: list[str] = []
    sticky_human_review = False
    sticky_fail_closed = False
    sticky_rollback = False

    for component_id in COMPONENT_ORDER:
        matches = [
            result
            for result in results
            if isinstance(result, dict) and result.get("component_id") == component_id
        ]
        if len(matches) != 1:
            findings.append(f"component_result_missing:{component_id}")
            continue
        result = matches[0]
        required_fields = {
            "component_id",
            "control_result",
            "advisory_outputs",
            "claimed_operations",
            "human_review_required",
            "fail_closed_recommended",
            "rollback_recommended",
            "evidence",
        }
        for field in sorted(required_fields - set(result)):
            findings.append(f"component_result_field_missing:{component_id}:{field}")

        declared_result = result.get("control_result")
        if declared_result not in RESULT_LATTICE:
            findings.append(f"component_control_result_invalid:{component_id}")
            declared_rank = RESULT_LATTICE["blocked"]
        else:
            declared_rank = RESULT_LATTICE[str(declared_result)]

        advisory_outputs = result.get("advisory_outputs")
        if not isinstance(advisory_outputs, list):
            findings.append(f"component_advisory_outputs_invalid:{component_id}")
            advisory_outputs = []
        elif len(advisory_outputs) != len({str(output) for output in advisory_outputs}):
            findings.append(f"component_advisory_outputs_duplicate:{component_id}")
        claimed_operations = result.get("claimed_operations")
        if not isinstance(claimed_operations, list):
            findings.append(f"component_claimed_operations_invalid:{component_id}")
            claimed_operations = []

        matrix_entry = matrix_by_id.get(component_id)
        if matrix_entry is None:
            findings.append(f"component_authority_declaration_missing:{component_id}")
            permitted: set[str] = set()
            declared_advisory_outputs: set[str] = set()
        else:
            permitted = {
                _normalized_operation(operation)
                for operation in _as_list(matrix_entry.get("permitted_operations"))
            }
            declared_advisory_outputs = {
                str(output) for output in _as_list(matrix_entry.get("advisory_outputs"))
            }
        for output in advisory_outputs:
            if str(output) not in declared_advisory_outputs:
                finding = (
                    f"component_claims_undeclared_advisory_output:"
                    f"{component_id}:{output}"
                )
                findings.append(finding)
                authority_findings.append(finding)
        for operation in claimed_operations:
            normalized = _normalized_operation(operation)
            if normalized not in permitted:
                finding = f"component_claims_undeclared_operation:{component_id}:{normalized}"
                findings.append(finding)
                authority_findings.append(finding)

        for field in (
            "human_review_required",
            "fail_closed_recommended",
            "rollback_recommended",
        ):
            if result.get(field) not in {True, False}:
                findings.append(f"component_boolean_invalid:{component_id}:{field}")

        sticky_human_review = sticky_human_review or result.get("human_review_required") is True
        sticky_fail_closed = sticky_fail_closed or result.get("fail_closed_recommended") is True
        sticky_rollback = sticky_rollback or result.get("rollback_recommended") is True

        runtime_payload = {
            "control_result": result.get("control_result"),
            "advisory_outputs": result.get("advisory_outputs"),
            "claimed_operations": result.get("claimed_operations"),
            "human_review_required": result.get("human_review_required"),
            "fail_closed_recommended": result.get("fail_closed_recommended"),
            "rollback_recommended": result.get("rollback_recommended"),
            "evidence": result.get("evidence"),
        }
        component_authority_findings = [
            f"{component_id}:{finding}"
            for finding in detect_authority_violations(runtime_payload)
        ]
        authority_findings.extend(component_authority_findings)

        observed_rank = _derived_rank(runtime_payload)
        if result.get("human_review_required") is True:
            observed_rank = max(observed_rank, RESULT_LATTICE["human_review_required"])
        if observed_rank > declared_rank:
            finding = f"restrictive_control_override_attempt:{component_id}"
            findings.append(finding)
            authority_findings.append(finding)
        effective_rank = max(declared_rank, observed_rank)

        if effective_rank > maximum_rank:
            maximum_rank = effective_rank
            preserved_ids = [component_id]
        elif effective_rank == maximum_rank:
            preserved_ids.append(component_id)

        evaluated_results.append(
            {
                "component_id": component_id,
                "declared_control_result": declared_result,
                "derived_control_result": RESULT_BY_RANK[observed_rank],
                "effective_control_result": RESULT_BY_RANK[effective_rank],
                "human_review_required": result.get("human_review_required") is True,
                "fail_closed_recommended": result.get("fail_closed_recommended") is True,
                "rollback_recommended": result.get("rollback_recommended") is True,
                "authority_violation_detected": bool(component_authority_findings),
            }
        )

    missing_components = set(COMPONENT_ORDER) - set(result_ids)
    if missing_components:
        maximum_rank = RESULT_LATTICE["blocked"]
        preserved_ids = sorted(missing_components)

    findings = _dedupe(findings)
    authority_findings = _dedupe(authority_findings)
    return {
        "component_results": evaluated_results,
        "effective_control_result": RESULT_BY_RANK[maximum_rank],
        "human_review_required": sticky_human_review,
        "fail_closed_recommended": sticky_fail_closed,
        "rollback_recommended": sticky_rollback,
        "authority_violation_detected": bool(authority_findings),
        "authority_findings": authority_findings,
        "most_restrictive_control_preserved": True,
        "preserved_component_ids": preserved_ids,
        "findings": findings,
        "valid": not findings and not authority_findings,
    }


def _top_level_authority_findings(fixture: Mapping[str, Any]) -> list[str]:
    findings: list[str] = []
    for field in FALSE_AUTHORITY_AND_EXECUTION_FIELDS:
        if fixture.get(field) is not False:
            findings.append(f"top_level_authority_or_execution_claim:{field}")
    if fixture.get("m14_completion_status") != "active_work_not_complete":
        findings.append("m14_completion_authority_claim")
    release_path = fixture.get("future_release_tag_path")
    if not isinstance(release_path, dict) or release_path.get("released") is not False:
        findings.append("future_release_authority_claim")
    return findings


def _top_level_recursive_authority_findings(
    fixture: Mapping[str, Any],
) -> list[str]:
    """Scan active top-level payloads while excluding inert declarations.

    Forbidden-output vocabularies, dormant cases, expected case outcomes, and
    boundary prose are declarations rather than active claims.  Baseline
    component results are scanned separately by ``evaluate_component_results``.
    Every other top-level field, including previously unknown nested payloads,
    remains subject to the same recursive authority boundary.
    """

    active_payload = {
        key: value
        for key, value in fixture.items()
        if key not in INERT_TOP_LEVEL_DECLARATION_FIELDS
    }
    return detect_authority_violations(active_payload)


def _matrix_authority_findings(matrix: Any) -> list[str]:
    findings: list[str] = []
    entries, _ = _matrix_entries(matrix)
    for entry in entries:
        component_id = str(entry.get("component_id", "missing_component"))
        if entry.get("retained_authority_owner") != "AAOS":
            findings.append(f"retained_authority_owner_invalid:{component_id}")
        if entry.get("decision_proof_sealing_owner") != "AAOS":
            findings.append(f"decision_proof_sealing_owner_invalid:{component_id}")
        permitted = {
            _normalized_operation(operation)
            for operation in _as_list(entry.get("permitted_operations"))
        }
        for operation in sorted(permitted - ALLOWED_COMPONENT_OPERATIONS):
            findings.append(
                f"component_permitted_operation_exceeds_boundary:{component_id}:{operation}"
            )
    return _dedupe(findings)


def _base_outputs(
    valid: bool,
    component_valid: bool,
    ready: bool,
    composition: Mapping[str, Any],
    source_drift: bool,
    authority_violation: bool,
) -> list[str]:
    outputs = [
        "m14_authority_boundary_fixture_valid"
        if valid
        else "m14_authority_boundary_fixture_invalid",
        "cross_control_boundary_valid" if valid else "cross_control_boundary_invalid",
        "component_boundary_valid"
        if component_valid
        else "component_boundary_invalid",
        "composition_not_authoritative",
    ]
    if composition.get("most_restrictive_control_preserved") is True:
        outputs.append("most_restrictive_control_preserved")
    for sticky in (
        "human_review_required",
        "fail_closed_recommended",
        "rollback_recommended",
    ):
        if composition.get(sticky) is True:
            outputs.append(sticky)
    if source_drift:
        outputs.append("source_boundary_drift_detected")
    if authority_violation:
        outputs.append("authority_violation_detected")
    outputs.append("ready_for_m14_readiness_review" if ready else "not_ready")
    if (
        not valid
        or composition.get("effective_control_result")
        in {"escalation_required", "blocked"}
    ):
        outputs.append("escalation_required")
    return _dedupe(outputs)


def evaluate_m14_cross_control_authority_boundary(
    fixture: Mapping[str, Any], source_artifacts: Mapping[str, str] | None
) -> dict[str, Any]:
    """Evaluate a baseline cross-control fixture without executing source code."""

    if not isinstance(fixture, dict):
        structural_findings = ["fixture_must_be_object"]
        fixture_dict: dict[str, Any] = {}
    else:
        fixture_dict = fixture
        structural_findings = _validate_fixture_structure(fixture_dict)

    composition = evaluate_component_results(
        fixture_dict.get(
            "baseline_component_results", fixture_dict.get("component_results")
        ),
        fixture_dict.get("component_authority_matrix"),
    )
    source_status = validate_source_boundaries(fixture_dict, source_artifacts)
    top_authority_findings = _top_level_authority_findings(fixture_dict)
    recursive_top_authority_findings = _top_level_recursive_authority_findings(
        fixture_dict
    )
    matrix_authority_findings = _matrix_authority_findings(
        fixture_dict.get("component_authority_matrix")
    )
    authority_findings = _dedupe(
        list(composition.get("authority_findings", []))
        + top_authority_findings
        + recursive_top_authority_findings
        + matrix_authority_findings
    )
    authority_violation = bool(authority_findings)
    source_drift = source_status["source_boundary_drift_detected"]
    findings = _dedupe(
        structural_findings
        + list(composition.get("findings", []))
        + list(source_status.get("source_boundary_findings", []))
        + authority_findings
    )
    matrix_boundary_findings = _validate_matrix(
        fixture_dict.get("component_authority_matrix")
    )
    component_valid = (
        composition.get("valid") is True and not matrix_boundary_findings
    )
    valid = not findings and not authority_violation and not source_drift
    ready = (
        valid
        and composition.get("effective_control_result")
        not in {"escalation_required", "blocked"}
    )
    outputs = _base_outputs(
        valid,
        component_valid,
        ready,
        composition,
        source_drift,
        authority_violation,
    )
    return {
        "component_results": composition.get("component_results", []),
        "effective_control_result": composition.get(
            "effective_control_result", "blocked"
        ),
        "human_review_required": composition.get("human_review_required", False),
        "fail_closed_recommended": composition.get("fail_closed_recommended", False),
        "rollback_recommended": composition.get("rollback_recommended", False),
        "authority_violation_detected": authority_violation,
        "source_boundary_drift_detected": source_drift,
        "ready_for_m14_readiness_review": ready,
        "outputs": outputs,
        "findings": findings,
        "valid": valid,
        "preserved_component_ids": composition.get("preserved_component_ids", []),
        "source_boundary_results": source_status.get("component_source_boundaries", {}),
    }


def _apply_dotted_override(target: Any, dotted_path: str, value: Any) -> str | None:
    parts = [part for part in str(dotted_path).split(".") if part != ""]
    if not parts:
        return "fixture_override_path_empty"
    current = target
    for part in parts[:-1]:
        if isinstance(current, list):
            if not part.isdigit() or int(part) >= len(current):
                return f"fixture_override_path_invalid:{dotted_path}"
            current = current[int(part)]
        elif isinstance(current, dict):
            if part not in current:
                current[part] = {}
            current = current[part]
        else:
            return f"fixture_override_path_invalid:{dotted_path}"

    final = parts[-1]
    delete = isinstance(value, dict) and value == {"$delete": True}
    if isinstance(current, list):
        if not final.isdigit() or int(final) >= len(current):
            return f"fixture_override_path_invalid:{dotted_path}"
        index = int(final)
        if delete:
            del current[index]
        else:
            current[index] = copy.deepcopy(value)
    elif isinstance(current, dict):
        if delete:
            if final not in current:
                return f"fixture_override_delete_missing:{dotted_path}"
            del current[final]
        else:
            current[final] = copy.deepcopy(value)
    else:
        return f"fixture_override_path_invalid:{dotted_path}"
    return None


def evaluate_cross_control_case(
    fixture: Mapping[str, Any],
    case_id: str,
    source_artifacts: Mapping[str, str] | None,
) -> dict[str, Any]:
    """Evaluate one active case; dormant cases and expected data are not scanned."""

    if not isinstance(fixture, dict):
        return {
            "case_id": case_id,
            "valid": False,
            "authority_violation_detected": False,
            "source_boundary_drift_detected": True,
            "ready_for_m14_readiness_review": False,
            "effective_control_result": "blocked",
            "human_review_required": False,
            "fail_closed_recommended": False,
            "rollback_recommended": False,
            "component_results": [],
            "preserved_component_ids": [],
            "outputs": [
                "m14_authority_boundary_fixture_invalid",
                "cross_control_boundary_invalid",
                "component_boundary_invalid",
                "composition_not_authoritative",
                "source_boundary_drift_detected",
                "not_ready",
                "escalation_required",
            ],
            "findings": ["fixture_must_be_object"],
        }

    cases = fixture.get("cross_control_cases")
    selected = [
        case
        for case in _as_list(cases)
        if isinstance(case, dict) and case.get("case_id") == case_id
    ]
    if len(selected) != 1:
        result = evaluate_m14_cross_control_authority_boundary(fixture, source_artifacts)
        result.update(
            {
                "case_id": case_id,
                "valid": False,
                "ready_for_m14_readiness_review": False,
                "outputs": _dedupe(
                    [
                        output
                        for output in result["outputs"]
                        if output != "m14_authority_boundary_fixture_valid"
                        and output != "cross_control_boundary_valid"
                        and output != "ready_for_m14_readiness_review"
                    ]
                    + [
                        "m14_authority_boundary_fixture_invalid",
                        "cross_control_boundary_invalid",
                        "not_ready",
                        "escalation_required",
                    ]
                ),
                "findings": _dedupe(
                    list(result["findings"]) + [f"cross_control_case_missing:{case_id}"]
                ),
            }
        )
        return result

    case = selected[0]
    active_fixture = copy.deepcopy(fixture)
    override_findings: list[str] = []
    overrides = case.get("fixture_overrides", {})
    if not isinstance(overrides, dict):
        override_findings.append(f"fixture_overrides_invalid:{case_id}")
    else:
        for dotted_path, value in overrides.items():
            finding = _apply_dotted_override(active_fixture, str(dotted_path), value)
            if finding:
                override_findings.append(finding)

    if "component_results" in case:
        active_fixture["baseline_component_results"] = copy.deepcopy(
            case.get("component_results")
        )

    result = evaluate_m14_cross_control_authority_boundary(
        active_fixture, source_artifacts
    )
    active_claims = case.get("active_claims")
    simulated_output = case.get("simulated_evaluator_output")
    active_authority_findings: list[str] = []
    if active_claims not in (None, {}, []):
        active_authority_findings.extend(detect_authority_violations(active_claims))
    if simulated_output not in (None, ""):
        active_authority_findings.extend(detect_authority_violations(simulated_output))

    effective_override = case.get("effective_control_result_override")
    derived_result = str(result.get("effective_control_result", "blocked"))
    if effective_override not in (None, ""):
        if effective_override not in RESULT_LATTICE:
            active_authority_findings.append("effective_control_result_override_invalid")
        elif RESULT_LATTICE[str(effective_override)] < RESULT_LATTICE[derived_result]:
            active_authority_findings.append("restrictive_control_override_attempt")
        elif RESULT_LATTICE[str(effective_override)] > RESULT_LATTICE[derived_result]:
            result["effective_control_result"] = str(effective_override)

    active_authority_findings = _dedupe(active_authority_findings)
    all_findings = _dedupe(
        list(result.get("findings", []))
        + override_findings
        + active_authority_findings
    )
    authority_violation = (
        result.get("authority_violation_detected") is True
        or bool(active_authority_findings)
    )
    valid = result.get("valid") is True and not override_findings and not active_authority_findings
    ready = (
        valid
        and result.get("source_boundary_drift_detected") is False
        and result.get("effective_control_result")
        not in {"escalation_required", "blocked"}
    )
    component_valid = "component_boundary_invalid" not in result.get("outputs", [])
    composition_view = {
        "most_restrictive_control_preserved": True,
        "human_review_required": result.get("human_review_required", False),
        "fail_closed_recommended": result.get("fail_closed_recommended", False),
        "rollback_recommended": result.get("rollback_recommended", False),
        "effective_control_result": result.get("effective_control_result", "blocked"),
    }
    outputs = _base_outputs(
        valid,
        component_valid,
        ready,
        composition_view,
        result.get("source_boundary_drift_detected") is True,
        authority_violation,
    )
    result.update(
        {
            "case_id": case_id,
            "authority_violation_detected": authority_violation,
            "ready_for_m14_readiness_review": ready,
            "outputs": outputs,
            "findings": all_findings,
            "valid": valid,
        }
    )
    return result


def evaluate_m14_cross_control_authority_boundary_fixture(
    fixture: Mapping[str, Any], source_artifacts: Mapping[str, str] | None
) -> dict[str, Any]:
    """Compatibility alias for the primary fixture evaluator."""

    return evaluate_m14_cross_control_authority_boundary(fixture, source_artifacts)


__all__ = [
    "ALLOWED_COMPONENT_OPERATIONS",
    "ALLOWED_EVALUATOR_OUTPUTS",
    "COMPONENT_ORDER",
    "EXPECTED_COMPONENTS",
    "FORBIDDEN_EVALUATOR_OUTPUTS",
    "INTENDED_CHANGED_FILES",
    "REQUIRED_BOUNDARY_STATEMENTS",
    "REQUIRED_CASE_PREFIXES",
    "REQUIRED_COMPOSITION_RULES",
    "RESULT_LATTICE",
    "detect_authority_violations",
    "evaluate_component_results",
    "evaluate_cross_control_case",
    "evaluate_m14_cross_control_authority_boundary",
    "evaluate_m14_cross_control_authority_boundary_fixture",
    "validate_source_boundaries",
]
