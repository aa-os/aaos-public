"""Deterministic, data-only M14 external skill admission evaluator.

This module classifies synthetic fixture data.  It never installs, imports, or
executes a skill and has no network, shell, subprocess, or file-I/O path.
"""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any


REQUIRED_SKILL_ADMISSION_CONTRACT_FIELDS = {
    "skill_id", "skill_name", "source_repo", "source_owner", "source_commit",
    "source_artifact_digest", "version", "license", "description", "intended_use",
    "prohibited_use", "activation_triggers", "supported_agents", "supported_runtimes",
    "required_tools", "required_permissions", "network_access",
    "allowed_network_domains", "blocked_network_domains", "file_access",
    "allowed_file_scopes", "blocked_file_scopes", "shell_access",
    "allowed_command_classes", "blocked_command_classes", "mcp_access",
    "required_mcp_servers", "environment_variables", "secret_access",
    "data_classification", "risk_level", "known_risks", "mitigations", "owner_contact",
    "skill_card", "scan_report", "scan_tool", "scan_timestamp", "signature",
    "signature_identity", "signature_verification_method", "benchmark_report",
    "evaluation_artifacts", "runtime_isolation_requirements", "output_contract",
    "trace_requirements", "replay_requirements", "rollback_requirements",
    "fail_closed_rules", "reassessment_interval", "last_reassessment",
    "expiration_date", "admission_policy_version",
}

REQUIRED_REGISTRY_FIELDS = {
    "registry_entry_id", "skill_id", "artifact_identity", "candidate_admission_state",
    "permission_envelope", "evidence_status", "runtime_constraints",
    "human_review_route", "reassessment_status", "trace_policy", "replay_policy",
    "governance_owner",
}

REQUIRED_CANDIDATE_STATES = {
    "candidate_allowed", "candidate_restricted", "candidate_blocked", "needs_approval",
    "needs_sandbox", "needs_human_review", "needs_replay_log",
    "needs_signature_verification", "needs_scan", "needs_evaluation",
    "stale_reassessment_required",
}

REQUIRED_IMMUTABLE_BINDINGS = {
    "source_commit", "source_artifact_digest", "version",
    "reviewed_permission_declaration", "reviewed_permission_scope",
    "reviewed_evidence_set",
    "admission_policy_version",
}

REQUIRED_PERMISSION_AXES = {"shell", "network", "file", "mcp", "secret"}

ACCESS_ENUMS = {
    "network": {"none", "restricted_outbound"},
    "file": {"none", "read_only", "restricted_read_write"},
    "shell": {"none", "restricted_command_classes"},
    "mcp": {"none", "restricted_mcp"},
    "secret": {"none", "named_secret_classes"},
}

REQUIRED_PERMISSION_SCOPE_FIELDS = {
    "required_tools", "network_domains", "file_scopes", "command_classes",
    "mcp_server_identities", "environment_variable_names", "secret_classes",
    "data_classifications", "activation_triggers",
}

PERMISSION_SCOPE_MIRRORS = {
    "required_tools": "required_tools",
    "network_domains": "allowed_network_domains",
    "file_scopes": "allowed_file_scopes",
    "command_classes": "allowed_command_classes",
    "mcp_server_identities": "required_mcp_servers",
    "environment_variable_names": "environment_variables",
    "activation_triggers": "activation_triggers",
}

PERMISSION_SCOPE_BLOCK_MIRRORS = {
    "network_domains": "blocked_network_domains",
    "file_scopes": "blocked_file_scopes",
    "command_classes": "blocked_command_classes",
}

REQUIRED_FAIL_CLOSED_RULES = {
    "unknown_skill_source", "missing_source_owner", "missing_source_commit",
    "missing_artifact_digest", "missing_version", "missing_license",
    "missing_skill_owner", "incomplete_permission_declaration", "permission_escalation",
    "undeclared_shell_access", "undeclared_network_access", "undeclared_file_access",
    "undeclared_mcp_access", "undeclared_secret_access", "undefined_output_contract",
    "missing_trace_requirements", "replay_evidence_unavailable",
    "insufficient_runtime_isolation", "required_signature_missing",
    "signature_verification_evidence_missing", "required_scan_missing",
    "high_risk_evaluation_evidence_missing", "artifact_digest_drift",
    "skill_expired_or_stale", "reassessment_overdue",
    "mutable_reference_without_binding", "malformed_optional_evidence",
    "contradictory_evidence_requirements", "permission_scope_unbounded",
    "blocked_scope_collision", "reviewed_permission_scope_binding_mismatch",
}

REQUIRED_FAIL_CLOSED_OUTCOMES = {
    rule: (
        "admission_not_ready"
        if rule in {
            "unknown_skill_source", "missing_source_owner", "missing_source_commit",
            "missing_artifact_digest", "missing_version", "missing_license",
            "missing_skill_owner", "undefined_output_contract", "required_signature_missing",
            "signature_verification_evidence_missing", "required_scan_missing",
            "malformed_optional_evidence", "contradictory_evidence_requirements",
        }
        else "stale_reassessment_required"
        if rule in {"skill_expired_or_stale", "reassessment_overdue"}
        else "candidate_blocked"
    )
    for rule in REQUIRED_FAIL_CLOSED_RULES
}

REQUIRED_FAIL_CLOSED_CONDITIONS = {
    "unknown_skill_source": "skill source is unknown",
    "missing_source_owner": "source owner is missing",
    "missing_source_commit": "source commit is missing",
    "missing_artifact_digest": "artifact digest is missing",
    "missing_version": "version is missing", "missing_license": "license is missing",
    "missing_skill_owner": "skill owner is missing",
    "incomplete_permission_declaration": "permission declaration is incomplete",
    "permission_escalation": "an observed coarse permission or detailed scope exceeds its reviewed declaration",
    "undeclared_shell_access": "shell access is undeclared",
    "undeclared_network_access": "network access is undeclared",
    "undeclared_file_access": "file access is undeclared",
    "undeclared_mcp_access": "MCP access is undeclared",
    "undeclared_secret_access": "secret access is undeclared",
    "undefined_output_contract": "output contract is undefined",
    "missing_trace_requirements": "trace requirements are missing",
    "replay_evidence_unavailable": "replay evidence cannot be produced",
    "insufficient_runtime_isolation": "runtime isolation is insufficient",
    "required_signature_missing": "signature is required but missing",
    "signature_verification_evidence_missing": "signature verification evidence is required but missing",
    "required_scan_missing": "scan evidence is required but its report, tool, timestamp, or artifact binding is missing",
    "high_risk_evaluation_evidence_missing": "high-risk or critical use lacks either benchmark evidence or evaluation evidence",
    "artifact_digest_drift": "artifact digest no longer matches the reviewed artifact",
    "skill_expired_or_stale": "skill is expired or stale",
    "reassessment_overdue": "reassessment is overdue",
    "mutable_reference_without_binding": "source uses only a mutable branch or tag without immutable binding",
    "malformed_optional_evidence": "optional signature or scan evidence is partial or malformed",
    "contradictory_evidence_requirements": "evidence requirement flags contradict supplied or not-required evidence state",
    "permission_scope_unbounded": "an allowed or observed permission scope contains a wildcard or unbounded value",
    "blocked_scope_collision": "a requested or observed permission scope collides with a blocked scope",
    "reviewed_permission_scope_binding_mismatch": "the declared detailed permission scope differs from its immutable reviewed binding",
}

REQUIRED_DEFAULT_POSTURE = {
    "Unverified skill = not executable", "Undeclared permission = blocked",
    "Permission escalation = blocked", "Missing trace = blocked",
    "Missing replay = blocked", "High-risk domain without evaluation evidence = blocked",
    "Artifact identity drift = blocked", "Expired admission evidence = blocked",
}

REQUIRED_BOUNDARY_STATEMENTS = {
    "External skill capability is not governance permission.",
    "Skill metadata is not verified behavior.",
    "Skill installation is not execution authorization.",
    "Artifact signature is not governance approval.",
    "Signature verification is not risk acceptance.",
    "Scan passed is not risk accepted.",
    "Benchmark passed is not deployment approval.",
    "Evaluation evidence is not final approval.",
    "candidate_allowed is not execution approval.",
    "needs_approval is not approval granted.",
    "admission_ready_for_review is not final admission approval.",
    "fail_closed_recommended is not fail_closed_executed.",
    "rollback_recommended is not rollback_executed.",
    "human_review_required is not completed review.",
    "evidence_complete is not Decision Proof sealing.",
    "replay_ready is not Decision Proof sealing.",
    "Registry classification is not final governance judgment.",
    "NVIDIA skills remain external capability artifacts.",
    "AAOS remains vendor-independent.",
    "Decision Proof sealing remains AAOS-owned.",
    "AAOS remains the decision sovereignty layer.",
}

REQUIRED_CAPTURE_FIELDS = {
    "skill identity", "source identity", "immutable artifact identity", "declared owner",
    "intended use", "prohibited use", "runtime", "supported agent",
    "requested permissions", "shell scope", "network scope", "file scope", "MCP scope",
    "secret scope", "data classification", "risk classification", "output contract",
    "activation trigger",
}
REQUIRED_VERIFY_FIELDS = {
    "source binding", "digest binding", "version binding", "owner presence",
    "license presence", "permission completeness", "least-privilege check",
    "permission mismatch check", "signature requirement", "signature evidence",
    "scan requirement", "scan evidence", "benchmark requirement", "evaluation evidence",
    "runtime isolation", "sandbox requirement", "human-review requirement",
    "trace availability", "replay availability", "output-contract validity", "staleness",
    "expiration", "reassessment requirement", "fail-closed decision",
}
REQUIRED_ACCUMULATE_FIELDS = {
    "admission evaluation trace", "evidence artifact references", "denied-condition trace",
    "permission-diff record", "reviewer handoff", "registry decision record",
    "runtime constraint record", "execution trace policy", "replay packet requirements",
    "drift record", "reassessment history", "incident linkage",
    "governance authority retention",
}

ALLOWED_EVALUATOR_OUTPUTS = {
    "skill_admission_fixture_valid", "skill_admission_fixture_invalid",
    "admission_ready_for_review", "admission_not_ready", "candidate_allowed",
    "candidate_restricted", "candidate_blocked", "needs_approval", "needs_sandbox",
    "needs_human_review", "needs_replay_log", "needs_signature_verification",
    "needs_scan", "needs_evaluation", "stale_reassessment_required",
    "permission_mismatch_detected", "artifact_drift_detected", "fail_closed_recommended",
    "rollback_recommended", "escalation_required",
}

FORBIDDEN_EVALUATOR_OUTPUTS = {
    "skill_execution_approved", "skill_executed", "installation_approved",
    "activation_approved", "deployment_approved", "capability_permission_granted",
    "signature_is_governance_approval", "scan_is_risk_acceptance",
    "benchmark_is_deployment_approval", "final_admission_approved", "risk_accepted",
    "fail_closed_executed", "rollback_executed", "audit_closed", "waiver_granted",
    "decision_proof_verified", "decision_proof_sealed", "sealed_by_skill",
    "sealed_by_registry", "sealed_by_evaluator", "authority_transferred",
    "final_governance_judgment", "m14_complete", "v0_13_0_released", "closes_201",
}

EXPECTED_CASE_TYPES = {
    "case_01_complete_synthetic_low_risk_jetson_diagnostic": "complete_synthetic_low_risk_jetson_diagnostic_skill_ready_for_admission_review",
    "case_02_unknown_source_repository_blocked": "unknown_source_repository_is_blocked",
    "case_03_missing_source_owner_blocked": "missing_source_owner_is_blocked",
    "case_04_missing_source_commit_blocked": "missing_source_commit_is_blocked",
    "case_05_missing_artifact_digest_blocked": "missing_artifact_digest_is_blocked",
    "case_06_mutable_tag_without_immutable_binding_blocked": "mutable_tag_without_immutable_binding_is_blocked",
    "case_07_missing_version_blocked": "missing_version_is_blocked",
    "case_08_missing_license_blocked": "missing_license_is_blocked",
    "case_09_missing_skill_owner_blocked": "missing_skill_owner_is_blocked",
    "case_10_required_signature_missing_blocked": "required_signature_missing_is_blocked",
    "case_11_signature_without_verification_evidence_blocked": "signature_present_but_verification_evidence_missing_is_blocked",
    "case_12_required_scan_report_missing_blocked": "required_scan_report_missing_is_blocked",
    "case_13_undeclared_shell_access_blocked": "undeclared_shell_access_is_blocked",
    "case_14_undeclared_network_access_blocked": "undeclared_network_access_is_blocked",
    "case_15_undeclared_file_access_blocked": "undeclared_file_access_is_blocked",
    "case_16_undeclared_mcp_access_blocked": "undeclared_mcp_access_is_blocked",
    "case_17_undeclared_secret_access_blocked": "undeclared_secret_access_is_blocked",
    "case_18_declared_permissions_differ_from_observed_requirements": "declared_permissions_differ_from_observed_requirements",
    "case_19_unsupported_runtime_isolation_blocked": "unsupported_runtime_isolation_is_blocked",
    "case_20_undefined_output_contract_blocked": "undefined_output_contract_is_blocked",
    "case_21_missing_trace_requirements_blocked": "missing_trace_requirements_is_blocked",
    "case_22_missing_replay_capability_blocked": "missing_replay_capability_is_blocked",
    "case_23_stale_skill_requires_reassessment": "stale_skill_requires_reassessment",
    "case_24_expired_admission_evidence_blocked": "expired_admission_evidence_is_blocked",
    "case_25_artifact_digest_drift_blocked": "artifact_digest_drift_is_blocked",
    "case_26_high_risk_medical_without_evaluation_blocked": "high_risk_medical_skill_without_evaluation_evidence_is_blocked",
    "case_27_high_risk_physical_action_without_sandbox_and_review_blocked": "high_risk_physical_action_skill_without_sandbox_and_human_review_is_blocked",
    "case_28_signed_skill_with_excessive_permissions_blocked": "signed_skill_with_excessive_permissions_remains_blocked",
    "case_29_scanned_skill_with_undeclared_network_access_blocked": "scanned_skill_with_undeclared_network_access_remains_blocked",
    "case_30_admission_ready_treated_as_execution_approval_rejected": "admission_ready_state_incorrectly_treated_as_execution_approval",
    "case_31_signature_verification_treated_as_governance_approval_rejected": "signature_verification_incorrectly_treated_as_governance_approval",
    "case_32_scan_passed_treated_as_risk_acceptance_rejected": "scan_passed_incorrectly_treated_as_risk_acceptance",
    "case_33_benchmark_passed_treated_as_deployment_approval_rejected": "benchmark_passed_incorrectly_treated_as_deployment_approval",
    "case_34_evaluator_attempts_skill_execution_rejected": "evaluator_attempts_to_execute_the_skill",
    "case_35_evaluator_attempts_risk_acceptance_rejected": "evaluator_attempts_to_accept_risk",
    "case_36_evaluator_attempts_decision_proof_sealing_rejected": "evaluator_attempts_to_seal_decision_proof",
    "case_37_evaluator_attempts_authority_transfer_rejected": "evaluator_attempts_to_transfer_authority",
    "case_38_evaluator_attempts_close_tracker_201_rejected": "evaluator_attempts_to_close_201",
    "case_39_evaluator_attempts_m14_completion_rejected": "evaluator_attempts_to_declare_m14_complete",
    "case_40_evaluator_attempts_v0_13_0_release_rejected": "evaluator_attempts_to_declare_v0_13_0_released",
}

EXPECTED_INTENDED_FILES = {
    "docs/capability-supply-chain/nvidia-skills-admission.md",
    "examples/public-integration-pack-pilot/m14-skill-admission-fixtures.json",
    "runtime/skill_admission_evaluator.py",
    "tests/test_skill_admission_evaluator.py",
}

EXPECTED_JETSON_SKILL_ID = "synthetic-jetson-read-only-diagnostic-skill"

EVIDENCE_REQUIREMENT_FIELDS = {
    "signature_required", "signature_verification_evidence_required",
    "scan_required", "benchmark_required", "evaluation_required",
}

NOT_REQUIRED_EVIDENCE = "not_required_by_policy"

REGISTRY_FORBIDDEN_TRUE_FIELDS = {
    "final_approval", "execution_approved", "deployment_approved",
    "permission_granted", "risk_accepted", "audit_closed", "waiver_granted",
    "decision_proof_verified", "decision_proof_sealed", "authority_transferred",
    "final_governance_judgment", "skill_execution_by_evaluator",
}


def _present(value: Any) -> bool:
    return value is not None and value != "" and value != [] and value != {}


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _interval_days(value: Any) -> int | None:
    if isinstance(value, str) and value.startswith("P") and value.endswith("D"):
        try:
            return int(value[1:-1])
        except ValueError:
            return None
    return None


def _string_list(value: Any, *, nonempty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (not nonempty or bool(value))
        and all(isinstance(item, str) and bool(item.strip()) for item in value)
    )


def _safe_string_set(value: Any) -> set[str]:
    """Return a set only for a well-formed string list."""

    return set(value) if _string_list(value) else set()


def _evidence_absent(value: Any) -> bool:
    return value is None or value == NOT_REQUIRED_EVIDENCE


def _evidence_present(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value != NOT_REQUIRED_EVIDENCE


def _evidence_value_well_formed(value: Any) -> bool:
    return _evidence_absent(value) or _evidence_present(value)


def _evidence_reference_list(value: Any, *, nonempty: bool = False) -> bool:
    return (
        _string_list(value, nonempty=nonempty)
        and all(_evidence_present(reference) for reference in value)
    )


def _unbounded_scope_token(value: str) -> bool:
    normalized = value.strip().casefold()
    return (
        "*" in value
        or normalized in {"all", "any", "unbounded", "unrestricted"}
        or normalized.startswith("all_")
        or normalized.endswith("_all")
        or normalized.endswith("://all")
    )


def _valid_environment_name(value: str) -> bool:
    return (
        bool(value)
        and value == value.upper()
        and value[0] != "_"
        and not value[0].isdigit()
        and all(character.isalnum() or character == "_" for character in value)
        and "=" not in value
    )


def _valid_secret_class(value: str) -> bool:
    normalized = value.casefold()
    return (
        bool(value)
        and "=" not in value
        and not any(character.isspace() for character in value)
        and not normalized.startswith(("sk-", "ghp_", "bearer"))
        and "secret_value" not in normalized
        and "-----begin" not in normalized
    )


def _blocked_scope_match(value: str, blocked: set[str]) -> bool:
    """Match exact deny identifiers; wildcard deny patterns never grant access."""

    for pattern in blocked:
        if pattern == "*" or value == pattern:
            return True
        if pattern.endswith("*") and value.startswith(pattern[:-1]):
            return True
    return False


def _access_relation(axis: str, declared: Any, observed: Any) -> str:
    """Return equal, escalation, overdeclaration, or invalid for coarse enums."""

    allowed = ACCESS_ENUMS[axis]
    if declared not in allowed or observed not in allowed:
        return "invalid"
    if declared == observed:
        return "equal"
    if observed == "none":
        return "overdeclaration"
    if declared == "none":
        return "escalation"
    if axis == "file":
        if declared == "restricted_read_write" and observed == "read_only":
            return "overdeclaration"
        if declared == "read_only" and observed == "restricted_read_write":
            return "escalation"
    return "escalation"


def _detailed_permission_scope_reasons(item: dict[str, Any]) -> list[str]:
    """Compare observed scope to the immutable declared scope without execution."""

    reasons: list[str] = []
    scope = item.get("permission_scope")
    if not isinstance(scope, dict) or set(scope) != {"declared", "observed"}:
        return ["detailed_permission_scope_invalid"]
    declared = scope.get("declared")
    observed = scope.get("observed")
    if (
        not isinstance(declared, dict)
        or not isinstance(observed, dict)
        or set(declared) != REQUIRED_PERMISSION_SCOPE_FIELDS
        or set(observed) != REQUIRED_PERMISSION_SCOPE_FIELDS
    ):
        return ["detailed_permission_scope_invalid"]

    escalation = False
    overdeclaration = False
    for field in sorted(REQUIRED_PERMISSION_SCOPE_FIELDS):
        declaration = declared.get(field)
        observed_values = observed.get(field)
        if (
            not isinstance(declaration, dict)
            or set(declaration) != {"allowed", "blocked"}
            or not _string_list(declaration.get("allowed"))
            or not _string_list(declaration.get("blocked"))
            or not _string_list(observed_values)
        ):
            reasons.append(f"permission_scope_invalid:{field}")
            continue
        allowed_list = declaration["allowed"]
        blocked_list = declaration["blocked"]
        if (
            len(allowed_list) != len(set(allowed_list))
            or len(blocked_list) != len(set(blocked_list))
            or len(observed_values) != len(set(observed_values))
        ):
            reasons.append(f"permission_scope_duplicate:{field}")
            continue

        if any(_unbounded_scope_token(value) for value in allowed_list + observed_values):
            reasons.append(f"unbounded_permission_scope:{field}")
            escalation = True

        if field == "environment_variable_names" and any(
            not _valid_environment_name(value)
            for value in allowed_list + blocked_list + observed_values
        ):
            reasons.append("environment_variable_name_invalid")
        if field == "secret_classes" and any(
            not _valid_secret_class(value)
            for value in allowed_list + blocked_list + observed_values
        ):
            reasons.append("secret_class_metadata_invalid")

        allowed = set(allowed_list)
        blocked = set(blocked_list)
        observed_set = set(observed_values)
        if any(_blocked_scope_match(value, blocked) for value in observed_set):
            reasons.append(f"blocked_permission_scope:{field}")
            escalation = True
        if observed_set - allowed:
            reasons.append(f"permission_scope_escalation:{field}")
            escalation = True
        if allowed - observed_set:
            overdeclaration = True

    for field, top_level in PERMISSION_SCOPE_MIRRORS.items():
        declaration = declared.get(field)
        if isinstance(declaration, dict) and item.get(top_level) != declaration.get("allowed"):
            reasons.append(f"permission_scope_mirror_mismatch:{field}")
    for field, top_level in PERMISSION_SCOPE_BLOCK_MIRRORS.items():
        declaration = declared.get(field)
        if isinstance(declaration, dict) and item.get(top_level) != declaration.get("blocked"):
            reasons.append(f"permission_scope_block_mirror_mismatch:{field}")

    classifications = declared.get("data_classifications")
    if isinstance(classifications, dict) and classifications.get("allowed") != [
        item.get("data_classification")
    ]:
        reasons.append("permission_scope_mirror_mismatch:data_classifications")

    secret_classes = declared.get("secret_classes")
    secret_allowed = (
        secret_classes.get("allowed") if isinstance(secret_classes, dict) else None
    )
    if item.get("secret_access") == "none" and secret_allowed != []:
        reasons.append("secret_scope_contradiction")
    if item.get("secret_access") == "named_secret_classes" and not secret_allowed:
        reasons.append("secret_scope_incomplete")

    if escalation:
        reasons.append("permission_escalation")
    elif overdeclaration:
        reasons.append("permission_overdeclaration")
    return _dedupe(reasons)


def _contains_forbidden_true_claim(value: Any) -> bool:
    """Reject affirmative governance/execution claims in registry records."""

    if isinstance(value, dict):
        for key, item in value.items():
            if (
                str(key) in REGISTRY_FORBIDDEN_TRUE_FIELDS
                or str(key) in FORBIDDEN_EVALUATOR_OUTPUTS
            ) and item is True:
                return True
            if _contains_forbidden_true_claim(item):
                return True
    elif isinstance(value, list):
        return any(_contains_forbidden_true_claim(item) for item in value)
    return False


def _contract_semantic_reasons(item: dict[str, Any], existing: list[str]) -> list[str]:
    """Return additional type, scope, and synthetic-boundary failures."""

    reasons: list[str] = []
    specific_fields = {
        "source_repo": "unknown_skill_source", "source_owner": "missing_source_owner",
        "source_commit": "missing_source_commit", "source_artifact_digest": "missing_artifact_digest",
        "version": "missing_version", "license": "missing_license",
        "owner_contact": "missing_skill_owner", "output_contract": "undefined_output_contract",
        "trace_requirements": "missing_trace_requirements",
        "replay_requirements": "replay_evidence_unavailable",
        "shell_access": "undeclared_shell_access", "network_access": "undeclared_network_access",
        "file_access": "undeclared_file_access", "mcp_access": "undeclared_mcp_access",
        "secret_access": "undeclared_secret_access",
    }
    nullable = {"benchmark_report"}
    string_fields = {
        "skill_id", "skill_name", "source_repo", "source_owner", "source_commit",
        "source_artifact_digest", "version", "license", "description", "network_access",
        "file_access", "shell_access", "mcp_access", "secret_access", "data_classification",
        "risk_level", "owner_contact", "reassessment_interval", "last_reassessment",
        "expiration_date", "admission_policy_version",
    }
    list_fields = {
        "intended_use", "prohibited_use", "activation_triggers", "supported_agents",
        "supported_runtimes", "required_tools", "allowed_network_domains",
        "blocked_network_domains", "allowed_file_scopes", "blocked_file_scopes",
        "allowed_command_classes", "blocked_command_classes", "required_mcp_servers",
        "environment_variables", "known_risks", "mitigations", "evaluation_artifacts",
        "fail_closed_rules",
    }
    nonempty_lists = {
        "intended_use", "prohibited_use", "activation_triggers", "supported_agents",
        "supported_runtimes", "required_tools", "known_risks", "mitigations",
        "fail_closed_rules",
    }
    dict_fields = {
        "required_permissions", "skill_card", "runtime_isolation_requirements",
        "output_contract", "trace_requirements", "replay_requirements",
        "rollback_requirements",
    }
    for field in sorted(REQUIRED_SKILL_ADMISSION_CONTRACT_FIELDS):
        value = item.get(field)
        if field in nullable and value is None:
            continue
        valid = True
        if field in string_fields:
            valid = isinstance(value, str) and bool(value.strip())
        elif field in list_fields:
            valid = _string_list(value, nonempty=field in nonempty_lists)
        elif field in dict_fields:
            valid = isinstance(value, dict) and bool(value)
        elif field in {"scan_report", "signature", "benchmark_report"}:
            valid = value is None or (isinstance(value, str) and bool(value.strip()))
        if not valid and specific_fields.get(field) not in existing:
            reasons.append(f"required_contract_field_invalid:{field}")

    declared = item.get("required_permissions")
    observed = item.get("observed_required_permissions")
    access_fields = {
        "shell": "shell_access", "network": "network_access", "file": "file_access",
        "mcp": "mcp_access", "secret": "secret_access",
    }
    if isinstance(declared, dict):
        for axis, field in access_fields.items():
            declared_value = declared.get(axis)
            access_value = item.get(field)
            if declared_value is not None and not isinstance(declared_value, str):
                reasons.append(f"permission_declaration_type_invalid:{axis}")
            if access_value is not None and not isinstance(access_value, str):
                reasons.append(f"permission_access_type_invalid:{axis}")
            if isinstance(declared_value, str) and isinstance(access_value, str) and declared_value != access_value:
                reasons.append(f"permission_access_field_mismatch:{axis}")
            if isinstance(declared_value, str) and declared_value not in ACCESS_ENUMS[axis]:
                reasons.append(f"permission_access_enum_invalid:{axis}")
            if isinstance(access_value, str) and access_value not in ACCESS_ENUMS[axis]:
                reasons.append(f"permission_access_enum_invalid:{axis}")
    if not isinstance(observed, dict) or set(observed) != REQUIRED_PERMISSION_AXES or any(
        not isinstance(observed.get(axis), str) or not observed.get(axis)
        for axis in REQUIRED_PERMISSION_AXES
    ):
        reasons.append("observed_permission_axes_invalid")
    elif any(observed.get(axis) not in ACCESS_ENUMS[axis] for axis in REQUIRED_PERMISSION_AXES):
        reasons.append("observed_permission_axes_invalid")

    scope_fields = {
        "allowed_network_domains": item.get("allowed_network_domains"),
        "blocked_network_domains": item.get("blocked_network_domains"),
        "allowed_file_scopes": item.get("allowed_file_scopes"),
        "blocked_file_scopes": item.get("blocked_file_scopes"),
        "allowed_command_classes": item.get("allowed_command_classes"),
        "blocked_command_classes": item.get("blocked_command_classes"),
        "required_mcp_servers": item.get("required_mcp_servers"),
        "environment_variables": item.get("environment_variables"),
    }
    for field, value in scope_fields.items():
        if not _string_list(value):
            reasons.append(f"permission_scope_invalid:{field}")
    allowed_scope_fields = (
        "allowed_network_domains", "allowed_file_scopes", "allowed_command_classes",
        "required_mcp_servers", "environment_variables",
    )
    wildcard_allowed = any(
        "*" in value
        for field in allowed_scope_fields
        for value in (item.get(field) if isinstance(item.get(field), list) else [])
        if isinstance(value, str)
    )
    if wildcard_allowed:
        reasons.append("excessive_permissions")
        if "excessive_permissions" not in existing:
            reasons.append("permission_scope_excessive")
    for allowed_field, blocked_field in (
        ("allowed_network_domains", "blocked_network_domains"),
        ("allowed_file_scopes", "blocked_file_scopes"),
        ("allowed_command_classes", "blocked_command_classes"),
    ):
        allowed_values = item.get(allowed_field)
        blocked_values = item.get(blocked_field)
        if (
            _string_list(allowed_values)
            and _string_list(blocked_values)
            and _safe_string_set(allowed_values) & _safe_string_set(blocked_values)
            and "excessive_permissions" not in existing + reasons
        ):
            reasons.append(f"permission_scope_allow_block_collision:{allowed_field}")
    if item.get("network_access") == "none" and (
        item.get("allowed_network_domains") != []
    ):
        reasons.append("network_scope_contradiction")
    if isinstance(item.get("network_access"), str) and item.get("network_access") != "none" and (
        not _string_list(item.get("allowed_network_domains"), nonempty=True)
        or not _string_list(item.get("blocked_network_domains"), nonempty=True)
    ):
        reasons.append("network_scope_incomplete")
    if item.get("file_access") == "none" and item.get("allowed_file_scopes") != []:
        reasons.append("file_scope_contradiction")
    if item.get("file_access") != "none" and (
        not item.get("allowed_file_scopes") or not item.get("blocked_file_scopes")
    ):
        reasons.append("file_scope_incomplete")
    if item.get("shell_access") == "none" and (
        item.get("allowed_command_classes") != []
    ):
        reasons.append("shell_scope_contradiction")
    if isinstance(item.get("shell_access"), str) and item.get("shell_access") != "none" and (
        not _string_list(item.get("allowed_command_classes"), nonempty=True)
        or not _string_list(item.get("blocked_command_classes"), nonempty=True)
    ):
        reasons.append("shell_scope_incomplete")
    if item.get("mcp_access") == "none" and item.get("required_mcp_servers") != []:
        reasons.append("mcp_scope_contradiction")
    if isinstance(item.get("mcp_access"), str) and item.get("mcp_access") != "none" and not _string_list(
        item.get("required_mcp_servers"), nonempty=True
    ):
        reasons.append("mcp_scope_incomplete")
    if str(item.get("risk_level") or "").strip().casefold() == "low":
        low_maximum = {
            "shell": "none", "network": "none",
            "file": "read_only", "mcp": "none", "secret": "none",
        }
        low_risk_envelope_exceeded = not isinstance(declared, dict) or any(
            _access_relation(axis, maximum, declared.get(axis))
                in {"escalation", "invalid"}
            for axis, maximum in low_maximum.items()
        )
        if low_risk_envelope_exceeded and not any(
            reason.startswith(("undeclared_", "permission_", "excessive_", "reviewed_permission_"))
            for reason in existing + reasons
        ):
            reasons.extend(["low_risk_permission_envelope_exceeded", "excessive_permissions"])

    reasons.extend(_detailed_permission_scope_reasons(item))

    output = item.get("output_contract")
    if isinstance(output, dict) and (
        not isinstance(output.get("schema_id"), str)
        or not output.get("schema_id")
        or output.get("schema_validation_required") is not True
        or output.get("side_effects_allowed") is not False
        or output.get("execution_or_approval_claims_allowed") is not False
    ):
        reasons.append("output_contract_semantics_invalid")
    trace = item.get("trace_requirements")
    if isinstance(trace, dict) and "missing_trace_requirements" not in existing and (
        trace.get("required") is not True
        or trace.get("available") is not True
        or not _string_list(trace.get("fields"), nonempty=True)
    ):
        reasons.append("trace_requirements_invalid")
    replay = item.get("replay_requirements")
    if isinstance(replay, dict) and "replay_evidence_unavailable" not in existing and (
        replay.get("required") is not True
        or replay.get("capable") is not True
        or replay.get("evidence_can_be_produced") is not True
        or not isinstance(replay.get("packet_format"), str)
        or not replay.get("packet_format")
        or replay.get("skill_execution_in_replay") is not False
    ):
        reasons.append("replay_requirements_invalid")
    rollback = item.get("rollback_requirements")
    if isinstance(rollback, dict) and (
        rollback.get("required") is not True
        or rollback.get("runtime_mutation_performed") is not False
        or rollback.get("rollback_is_recommendation_only") is not True
        or not _present(rollback.get("action"))
    ):
        reasons.append("rollback_requirements_invalid")
    contract_rules = item.get("fail_closed_rules")
    required_contract_rules = {
        "unknown_skill_source", "missing_source_owner", "missing_source_commit",
        "missing_artifact_digest", "missing_version", "missing_license",
        "missing_skill_owner", "incomplete_permission_declaration", "permission_escalation",
        "missing_output_contract", "missing_trace", "missing_replay",
        "insufficient_runtime_isolation", "missing_required_evidence",
        "artifact_identity_drift", "stale_or_expired_evidence",
    }
    if isinstance(contract_rules, list) and not required_contract_rules <= _safe_string_set(contract_rules):
        reasons.append("contract_fail_closed_rules_invalid")
    if item.get("skill_id") == "synthetic-jetson-read-only-diagnostic-skill":
        specimen = item.get("synthetic_specimen")
        true_flags = {
            "synthetic", "read_only_diagnostic_intent", "restricted_permission_envelope",
            "device_mutation_prohibited", "firmware_modification_prohibited",
            "package_installation_prohibited", "credential_access_prohibited",
            "arbitrary_shell_execution_prohibited", "output_schema_validation_required",
            "trace_evidence_required", "replay_evidence_required",
            "immutable_artifact_identity_required",
        }
        false_flags = {
            "contains_real_nvidia_code", "contains_real_device_data", "skill_executed",
            "shell_command_executed", "device_accessed", "network_accessed",
        }
        if not isinstance(specimen, dict) or any(specimen.get(key) is not True for key in true_flags) or any(
            specimen.get(key) is not False for key in false_flags
        ) or (isinstance(specimen, dict) and specimen.get("maximum_outcome") != "admission_ready_for_review"):
            reasons.append("synthetic_specimen_boundary_invalid")
        prohibited = _safe_string_set(item.get("prohibited_use"))
        if not {
            "device mutation", "firmware modification", "package installation",
            "credential access", "arbitrary shell execution", "network access",
            "execution authorization",
        } <= prohibited:
            reasons.append("jetson_prohibited_use_incomplete")
        expected_permissions = {
            "shell": "none", "network": "none",
            "file": "read_only", "mcp": "none", "secret": "none",
        }
        permission_related = any(
            reason.startswith(("undeclared_", "permission_", "excessive_", "reviewed_permission_"))
            for reason in existing + reasons
        )
        if declared != expected_permissions and not permission_related:
            reasons.append("jetson_restricted_permission_envelope_invalid")
        isolation = item.get("runtime_isolation_requirements")
        isolation_flags = {
            "supported", "sandbox_required", "network_disabled", "shell_disabled",
            "filesystem_read_only", "device_access_disabled_during_evaluation",
            "process_spawn_disabled", "secrets_unavailable",
        }
        if isinstance(isolation, dict) and any(isolation.get(key) is not True for key in isolation_flags) and not any(
            reason in existing for reason in ("insufficient_runtime_isolation", "high_risk_sandbox_missing")
        ):
            reasons.extend(["runtime_isolation_controls_invalid", "synthetic_specimen_boundary_invalid"])
        replay = item.get("replay_requirements")
        if isinstance(replay, dict) and replay.get("skill_execution_in_replay") is not False and "replay_evidence_unavailable" not in existing:
            reasons.extend(["replay_execution_boundary_invalid", "synthetic_specimen_boundary_invalid"])
        skill_card = item.get("skill_card")
        if not isinstance(skill_card, dict) or (
            skill_card.get("status") != "synthetic_reference_only"
            or skill_card.get("contains_skill_code") is not False
            or skill_card.get("behavior_verified_by_metadata") is not False
            or skill_card.get("admission_ready_is_final_approval") is not False
        ):
            reasons.append("synthetic_specimen_boundary_invalid")
        if isinstance(output, dict) and (
            output.get("side_effects_allowed") is not False
            or output.get("execution_or_approval_claims_allowed") is not False
        ) and "undefined_output_contract" not in existing:
            reasons.append("synthetic_specimen_boundary_invalid")
    return _dedupe(reasons)


def _apply_overrides(source: dict[str, Any], overrides: Any) -> dict[str, Any]:
    result = deepcopy(source)
    if not isinstance(overrides, dict):
        return result
    for path, value in overrides.items():
        parts = str(path).split(".")
        target = result
        for part in parts[:-1]:
            child = target.get(part)
            if not isinstance(child, dict):
                child = {}
                target[part] = child
            target = child
        target[parts[-1]] = deepcopy(value)
    return result


def evaluate_skill_admission(
    contract: Any, evaluation_overrides: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Classify one supplied contract without performing external activity."""

    item = contract if isinstance(contract, dict) else {}
    options = evaluation_overrides if isinstance(evaluation_overrides, dict) else {}
    simulated = options.get("simulated_evaluator_output")
    if simulated in FORBIDDEN_EVALUATOR_OUTPUTS:
        return {
            "ready_for_review": False,
            "candidate_admission_state": "candidate_blocked",
            "outputs": ["admission_not_ready", "candidate_blocked", "escalation_required"],
            "reasons": [f"forbidden_output_claim:{simulated}"],
        }

    reasons: list[str] = []
    if not _present(item.get("source_repo")) or str(item.get("source_repo")).casefold() in {
        "unknown", "unverified", "none"
    } or item.get("source_reference_type") == "unknown":
        reasons.append("unknown_skill_source")
    if not _present(item.get("source_owner")):
        reasons.append("missing_source_owner")
    if not _present(item.get("source_commit")):
        reasons.append("missing_source_commit")
    if not _present(item.get("source_artifact_digest")):
        reasons.append("missing_artifact_digest")

    binding = item.get("immutable_review_binding")
    reference_type = str(item.get("artifact_reference_type") or "")
    source_commit = str(item.get("source_commit") or "")
    mutable = reference_type in {"mutable_tag_only", "mutable_branch_only"} or (
        source_commit.startswith("refs/tags/") or source_commit.startswith("refs/heads/")
    )
    if mutable:
        reasons.append("mutable_reference_without_binding")
    if not _present(item.get("version")):
        reasons.append("missing_version")
    if not _present(item.get("license")):
        reasons.append("missing_license")
    if not _present(item.get("skill_owner")) or not _present(item.get("owner_contact")):
        reasons.append("missing_skill_owner")

    evidence = item.get("evidence_requirements")
    evidence = evidence if isinstance(evidence, dict) else {}
    if (
        set(evidence) != EVIDENCE_REQUIREMENT_FIELDS
        or any(
            not isinstance(evidence.get(field), bool)
            for field in EVIDENCE_REQUIREMENT_FIELDS
        )
    ):
        reasons.append("evidence_requirement_policy_invalid")

    signature_required = evidence.get("signature_required") is True
    verification_required = (
        evidence.get("signature_verification_evidence_required") is True
    )
    scan_required = evidence.get("scan_required") is True
    signature = item.get("signature")
    signature_identity = item.get("signature_identity")
    signature_method = item.get("signature_verification_method")
    signature_verification = item.get("signature_verification_evidence")
    signature_present = _evidence_present(signature)
    verification_present = _evidence_present(signature_verification)

    if signature_required and not signature_present:
        reasons.append("required_signature_missing")
    if verification_required:
        if not signature_present and not signature_required:
            reasons.append("contradictory_evidence_requirements")
            reasons.append("required_signature_missing")
        if not verification_present:
            reasons.append("signature_verification_evidence_missing")

    signature_companions = (
        signature_identity, signature_method, signature_verification,
    )
    if signature_present:
        signature_metadata_complete = (
            _evidence_present(signature_identity)
            and _evidence_present(signature_method)
        )
        if not signature_metadata_complete:
            reasons.append(
                "optional_signature_evidence_malformed"
                if not signature_required and not verification_required
                else "signature_evidence_malformed"
            )
        if not _evidence_value_well_formed(signature_verification):
            reasons.append(
                "optional_signature_evidence_malformed"
                if not verification_required
                else "signature_evidence_malformed"
            )
    elif not signature_required and not verification_required:
        if not all(
            _evidence_absent(value)
            for value in (signature, *signature_companions)
        ):
            reasons.append("optional_signature_evidence_malformed")

    scan_report = item.get("scan_report")
    scan_tool = item.get("scan_tool")
    scan_timestamp = item.get("scan_timestamp")
    scan_binding = item.get("scan_artifact_binding")
    scan_parts_present = (
        _evidence_present(scan_report),
        _evidence_present(scan_tool),
        _evidence_present(scan_timestamp),
        isinstance(scan_binding, dict) and bool(scan_binding),
    )
    scan_bundle_absent = all(
        _evidence_absent(value)
        for value in (scan_report, scan_tool, scan_timestamp, scan_binding)
    )
    scan_binding_valid = isinstance(scan_binding, dict) and scan_binding == {
        "source_commit": item.get("source_commit"),
        "source_artifact_digest": item.get("source_artifact_digest"),
        "version": item.get("version"),
    }
    scan_timestamp_valid = (
        _parse_time(scan_timestamp) is not None
        if _evidence_present(scan_timestamp)
        else False
    )
    complete_scan = all(scan_parts_present) and scan_binding_valid and scan_timestamp_valid
    if scan_required and not complete_scan:
        reasons.append("required_scan_missing")
    elif not scan_required and not scan_bundle_absent and not complete_scan:
        reasons.append("optional_scan_evidence_malformed")

    declared = item.get("required_permissions")
    declared = declared if isinstance(declared, dict) else {}
    observed = item.get("observed_required_permissions")
    observed = observed if isinstance(observed, dict) else {}
    access_fields = {
        "shell": "shell_access", "network": "network_access", "file": "file_access",
        "mcp": "mcp_access", "secret": "secret_access",
    }
    missing_axes: list[str] = []
    escalated = False
    overdeclared = False
    for axis, field in access_fields.items():
        if not _present(item.get(field)) or not _present(declared.get(axis)):
            reasons.append(f"undeclared_{axis}_access")
            missing_axes.append(axis)
        actual = observed.get(axis)
        requested = declared.get(axis)
        relation = _access_relation(axis, requested, actual)
        if relation == "escalation":
            escalated = True
        elif relation == "overdeclaration":
            overdeclared = True
        elif (
            relation == "invalid"
            and _present(requested)
            and isinstance(actual, str)
            and actual != "none"
        ):
            escalated = True
        if (
            not _present(requested)
            and isinstance(actual, str)
            and actual not in {"none", "read_only"}
        ):
            escalated = True
    if escalated:
        reasons.append("permission_escalation")
    if overdeclared:
        reasons.append("permission_overdeclaration")
    if not escalated and not overdeclared and (
        missing_axes or item.get("permission_declaration_complete") is not True
    ):
        reasons.append("incomplete_permission_declaration")

    excessive_values = {"unrestricted", "arbitrary_shell", "*", "read_write", "write"}
    if any(isinstance(value, str) and value in excessive_values for value in declared.values()):
        reasons.append("excessive_permissions")
    if isinstance(binding, dict):
        if not missing_axes:
            reviewed = binding.get("reviewed_permission_declaration")
            if not isinstance(reviewed, dict) or not reviewed or not REQUIRED_PERMISSION_AXES <= set(reviewed):
                reasons.append("reviewed_permission_binding_invalid")
            elif reviewed != declared:
                reasons.append("reviewed_permission_binding_mismatch")
            permission_scope = item.get("permission_scope")
            declared_scope = (
                permission_scope.get("declared")
                if isinstance(permission_scope, dict)
                else None
            )
            reviewed_scope = binding.get("reviewed_permission_scope")
            if not isinstance(reviewed_scope, dict) or not reviewed_scope:
                reasons.append("reviewed_permission_scope_binding_invalid")
            elif reviewed_scope != declared_scope:
                reasons.append("reviewed_permission_scope_binding_mismatch")
        identity_pairs = (
            ("source_commit", "source_commit"),
            ("source_artifact_digest", "source_artifact_digest"),
            ("version", "version"),
            ("admission_policy_version", "admission_policy_version"),
        )
        if all(_present(item.get(left)) for left, _ in identity_pairs) and any(
            binding.get(right) != item.get(left) for left, right in identity_pairs
        ):
            reasons.append("immutable_review_binding_mismatch")
        if not REQUIRED_IMMUTABLE_BINDINGS <= set(binding):
            reasons.append("immutable_review_binding_incomplete")
        reviewed_evidence = binding.get("reviewed_evidence_set")
        if (
            not _string_list(reviewed_evidence, nonempty=True)
            or len(reviewed_evidence) != len(set(reviewed_evidence))
        ):
            reasons.append("reviewed_evidence_binding_invalid")
        elif not (
            any(
                reason in reasons
                for reason in (
                    "required_signature_missing", "signature_verification_evidence_missing",
                    "required_scan_missing", "high_risk_evaluation_evidence_missing",
                )
            )
            or (
                str(item.get("risk_level") or "").strip().casefold()
                    in {"high", "critical"}
                and (
                    not _evidence_present(item.get("benchmark_report"))
                    or not _evidence_reference_list(
                        item.get("evaluation_artifacts"), nonempty=True
                    )
                )
            )
        ):
            evaluation_artifacts = item.get("evaluation_artifacts")
            safe_evaluations = (
                evaluation_artifacts
                if _evidence_reference_list(evaluation_artifacts)
                else []
            )
            current_evidence = {
                value for value in (
                    item.get("signature"), item.get("scan_report"),
                    item.get("signature_verification_evidence"),
                    item.get("benchmark_report"), *safe_evaluations,
                )
                if _evidence_present(value)
            }
            if set(reviewed_evidence) != current_evidence:
                reasons.append("reviewed_evidence_binding_mismatch")
    elif not mutable and all(
        _present(item.get(field))
        for field in ("source_commit", "source_artifact_digest", "version")
    ):
        reasons.append("immutable_review_binding_missing")

    isolation = item.get("runtime_isolation_requirements")
    isolation = isolation if isinstance(isolation, dict) else {}
    if item.get("runtime_isolation_sufficient") is not True or isolation.get("supported") is not True:
        reasons.append("insufficient_runtime_isolation")
    output_contract = item.get("output_contract")
    if not isinstance(output_contract, dict) or not _present(output_contract.get("schema_id")):
        reasons.append("undefined_output_contract")
    trace = item.get("trace_requirements")
    if not isinstance(trace, dict) or trace.get("required") is not True or trace.get("available") is not True:
        reasons.append("missing_trace_requirements")
    replay = item.get("replay_requirements")
    if (
        not isinstance(replay, dict)
        or replay.get("required") is not True
        or replay.get("capable") is not True
        or replay.get("evidence_can_be_produced") is not True
    ):
        reasons.append("replay_evidence_unavailable")

    if (
        _present(item.get("source_artifact_digest"))
        and _present(item.get("observed_artifact_digest"))
        and item.get("source_artifact_digest") != item.get("observed_artifact_digest")
    ):
        reasons.append("artifact_digest_drift")

    evaluation_time = _parse_time(options.get("evaluation_time", "2026-02-01T00:00:00Z"))
    expiration = _parse_time(item.get("expiration_date"))
    last = _parse_time(item.get("last_reassessment"))
    interval = _interval_days(item.get("reassessment_interval"))
    if evaluation_time is None:
        reasons.append("invalid_evaluation_time")
    if expiration is None:
        reasons.append("invalid_expiration_date")
    if last is None:
        reasons.append("invalid_last_reassessment")
    if interval is None or interval <= 0:
        reasons.append("invalid_reassessment_interval")
    expired = bool(evaluation_time and expiration and evaluation_time >= expiration)
    overdue = bool(evaluation_time and last and interval is not None and evaluation_time > last + timedelta(days=interval))
    if expired:
        reasons.append("skill_expired_or_stale")
    elif overdue:
        reasons.append("reassessment_overdue")

    high_risk = str(item.get("risk_level") or "").strip().casefold() in {
        "high", "critical",
    }
    if high_risk:
        benchmark_missing = not _evidence_present(item.get("benchmark_report"))
        evaluations_missing = not _evidence_reference_list(
            item.get("evaluation_artifacts"), nonempty=True
        )
        if (
            evidence.get("benchmark_required") is not True
            or evidence.get("evaluation_required") is not True
        ):
            reasons.append("evidence_requirement_policy_invalid")
        if benchmark_missing or evaluations_missing:
            reasons.append("high_risk_evaluation_evidence_missing")
        if item.get("sandbox_required") is not True or isolation.get("sandbox_required") is not True:
            reasons.append("high_risk_sandbox_missing")
        if item.get("human_review_required") is not True or not _present(item.get("human_review_route")):
            reasons.append("high_risk_human_review_missing")

    reasons.extend(_contract_semantic_reasons(item, reasons))

    reasons = _dedupe(reasons)
    if not reasons:
        return {
            "ready_for_review": True,
            "candidate_admission_state": "candidate_restricted",
            "outputs": [
                "admission_ready_for_review", "candidate_restricted", "needs_approval",
                "needs_human_review", "needs_replay_log",
            ],
            "reasons": [],
        }

    if reasons == ["reassessment_overdue"]:
        return {
            "ready_for_review": False,
            "candidate_admission_state": "stale_reassessment_required",
            "outputs": [
                "admission_not_ready", "stale_reassessment_required",
                "needs_human_review", "fail_closed_recommended",
            ],
            "reasons": reasons,
        }

    outputs = ["admission_not_ready", "candidate_blocked"]
    if any(reason in reasons for reason in ("required_signature_missing", "signature_verification_evidence_missing")):
        outputs.append("needs_signature_verification")
    if "required_scan_missing" in reasons:
        outputs.append("needs_scan")
    if any(reason in reasons for reason in (
        "permission_escalation", "permission_overdeclaration", "excessive_permissions",
        "reviewed_permission_binding_mismatch",
        "reviewed_permission_scope_binding_mismatch",
        "reviewed_permission_scope_binding_invalid",
    )):
        outputs.append("permission_mismatch_detected")
    if any(reason in reasons for reason in ("insufficient_runtime_isolation", "high_risk_sandbox_missing")):
        outputs.append("needs_sandbox")
    if "replay_evidence_unavailable" in reasons:
        outputs.append("needs_replay_log")
    if "skill_expired_or_stale" in reasons:
        outputs.append("stale_reassessment_required")
    if "artifact_digest_drift" in reasons:
        outputs.extend(["artifact_drift_detected", "rollback_recommended"])
    if "high_risk_evaluation_evidence_missing" in reasons:
        outputs.extend(["needs_evaluation", "needs_human_review"])
    if "high_risk_human_review_missing" in reasons:
        outputs.append("needs_human_review")
    if "high_risk_sandbox_missing" in reasons and "high_risk_human_review_missing" in reasons:
        outputs.append("escalation_required")
    outputs.append("fail_closed_recommended")
    return {
        "ready_for_review": False,
        "candidate_admission_state": "candidate_blocked",
        "outputs": _dedupe(outputs),
        "reasons": reasons,
    }


def evaluate_fixture_case(fixture: Any, case_id: str) -> dict[str, Any]:
    """Evaluate one named fixture case against the fixture's baseline contract."""

    data = fixture if isinstance(fixture, dict) else {}
    cases = data.get("fixture_cases") if isinstance(data.get("fixture_cases"), list) else []
    case = next((entry for entry in cases if isinstance(entry, dict) and entry.get("case_id") == case_id), None)
    if case is None:
        return {
            "case_id": case_id,
            "ready_for_review": False,
            "candidate_admission_state": "candidate_blocked",
            "outputs": ["admission_not_ready", "candidate_blocked", "fail_closed_recommended"],
            "reasons": ["fixture_case_not_found"],
        }
    contract = _apply_overrides(
        data.get("skill_admission_contract") if isinstance(data.get("skill_admission_contract"), dict) else {},
        case.get("contract_overrides"),
    )
    options = deepcopy(case.get("evaluation_overrides")) if isinstance(case.get("evaluation_overrides"), dict) else {}
    options.setdefault("evaluation_time", data.get("evaluation_time"))
    result = evaluate_skill_admission(contract, options)
    return {"case_id": case_id, "case_type": case.get("case_type"), **result}


def _fixture_findings(fixture: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    expected_top = {
        "fixture_status": "m14_active_work_not_complete", "related_issue": "#192",
        "tracker_issue": "#201", "tracker_issue_linkage": "Refs #201",
        "related_voice_runtime_pr": "#202", "related_public_output_gate_pr": "#204",
        "related_moda_mapping_pr": "#205", "related_ai_pr_provenance_pr": "#206",
        "source_reference": "NVIDIA/skills",
        "source_reference_role": "external_capability_supply_chain_reference_specimen",
        "m14_completion_status": "active_work_not_complete",
        "target_future_release": "v0.13.0",
    }
    for field, expected in expected_top.items():
        if fixture.get(field) != expected:
            findings.append(f"top_level_state_invalid:{field}")
    false_fields = {
        "vendor_dependency_created", "external_skill_downloaded", "external_skill_installed",
        "external_skill_executed", "network_access_performed_by_fixture",
        "shell_command_executed_by_fixture", "final_admission_approval_made_by_fixture",
        "execution_authorization_made_by_fixture", "risk_accepted_by_fixture",
        "decision_proof_sealed_by_fixture",
    }
    for field in sorted(false_fields):
        if fixture.get(field) is not False:
            findings.append(f"external_or_authority_boundary_invalid:{field}")
    if fixture.get("fixture_evidence_is_synthetic") is not True:
        findings.append("fixture_evidence_not_synthetic")
    release = fixture.get("future_release_tag_path")
    if not isinstance(release, dict) or release.get("released") is not False:
        findings.append("future_release_state_invalid")
    intended = fixture.get("intended_files")
    if not isinstance(intended, list) or len(intended) != 4 or _safe_string_set(intended) != EXPECTED_INTENDED_FILES:
        findings.append("intended_files_not_exactly_four")

    boundary = fixture.get("evaluation_boundary")
    if not isinstance(boundary, dict) or boundary.get("fixture_data_only") is not True:
        findings.append("evaluation_not_fixture_data_only")
    elif any(value is not False for key, value in boundary.items() if key != "fixture_data_only"):
        findings.append("external_execution_boundary_invalid")
    claims = fixture.get("source_reference_claims")
    if not isinstance(claims, dict) or any(value is not False for value in claims.values()):
        findings.append("unsupported_source_reference_claim")
    positioning = fixture.get("supply_chain_positioning")
    expected_positioning = {
        "external_artifact_role": "NVIDIA skills are external agent capability artifacts.",
        "aaos_role": "AAOS is the capability admission, permission, evidence, replay, escalation, and decision-governance control plane.",
        "dependency_status": "reference_specimen_only_not_an_aaos_dependency",
        "vendor_governance": "AAOS governance remains model-agnostic and vendor-agnostic.",
    }
    if positioning != expected_positioning:
        findings.append("supply_chain_positioning_invalid")

    contract = fixture.get("skill_admission_contract")
    if not isinstance(contract, dict):
        findings.append("skill_admission_contract_missing")
        contract = {}
    for field in sorted(REQUIRED_SKILL_ADMISSION_CONTRACT_FIELDS - set(contract)):
        findings.append(f"skill_admission_contract_field_missing:{field}")
    baseline = evaluate_skill_admission(contract, {"evaluation_time": fixture.get("evaluation_time")})
    if not baseline.get("ready_for_review"):
        findings.extend(f"baseline_contract:{reason}" for reason in baseline.get("reasons", []))

    schema = fixture.get("capability_registry_schema")
    if not isinstance(schema, dict):
        findings.append("capability_registry_schema_missing")
        schema = {}
    if not REQUIRED_REGISTRY_FIELDS <= _safe_string_set(schema.get("required_fields")):
        findings.append("capability_registry_required_fields_incomplete")
    if not REQUIRED_CANDIDATE_STATES <= _safe_string_set(schema.get("candidate_states")):
        findings.append("capability_registry_candidate_states_incomplete")
    semantics = schema.get("state_semantics")
    if not isinstance(semantics, dict) or any(
        semantics.get(state) not in {"registry_classification_only", "routing_state_only"}
        for state in REQUIRED_CANDIDATE_STATES
    ):
        findings.append("candidate_state_semantics_authoritative")
    non_authoritative = _safe_string_set(schema.get("non_authoritative_for"))
    if not {"final_execution_approval", "risk_acceptance", "deployment_authorization", "audit_closure", "decision_proof_sealing"} <= non_authoritative:
        findings.append("registry_non_authority_boundary_incomplete")
    entry = fixture.get("capability_registry_entry")
    if not isinstance(entry, dict) or not REQUIRED_REGISTRY_FIELDS <= set(entry):
        findings.append("capability_registry_entry_incomplete")
    elif (
        entry.get("governance_owner") != "AAOS"
        or not isinstance(entry.get("candidate_admission_state"), str)
        or entry.get("candidate_admission_state") not in REQUIRED_CANDIDATE_STATES
    ):
        findings.append("capability_registry_entry_governance_invalid")
    else:
        if entry.get("skill_id") != contract.get("skill_id"):
            findings.append("registry_skill_identity_mismatch")
        if _contains_forbidden_true_claim(entry):
            findings.append("registry_forbidden_governance_claim")
        evidence_status = entry.get("evidence_status")
        runtime_constraints = entry.get("runtime_constraints")
        if not isinstance(evidence_status, dict) or evidence_status.get("final_approval") is not False:
            findings.append("registry_final_approval_boundary_invalid")
        if not isinstance(runtime_constraints, dict) or runtime_constraints.get("skill_execution_by_evaluator") is not False:
            findings.append("registry_execution_boundary_invalid")
        if entry.get("permission_envelope") != contract.get("required_permissions"):
            findings.append("registry_permission_envelope_mismatch")
        artifact_identity = entry.get("artifact_identity")
        contract_binding = contract.get("immutable_review_binding")
        artifact_identity_invalid = (
            not isinstance(artifact_identity, dict)
            or not REQUIRED_IMMUTABLE_BINDINGS <= set(artifact_identity)
            or any(
                artifact_identity.get(field) != contract.get(field)
                for field in (
                    "source_commit", "source_artifact_digest", "version",
                    "admission_policy_version",
                )
            )
            or not isinstance(contract_binding, dict)
            or artifact_identity.get("reviewed_permission_declaration")
                != contract_binding.get("reviewed_permission_declaration")
            or artifact_identity.get("reviewed_permission_scope")
                != contract_binding.get("reviewed_permission_scope")
            or not _string_list(
                artifact_identity.get("reviewed_evidence_set"), nonempty=True
            )
            or _safe_string_set(artifact_identity.get("reviewed_evidence_set"))
                != _safe_string_set(contract_binding.get("reviewed_evidence_set"))
        )
        if artifact_identity_invalid:
            findings.append("registry_artifact_identity_mismatch")

    immutable_rule = fixture.get("immutable_review_rule")
    if not isinstance(immutable_rule, dict) or not REQUIRED_IMMUTABLE_BINDINGS <= _safe_string_set(immutable_rule.get("required_bindings")):
        findings.append("immutable_review_rule_incomplete")
    permission = fixture.get("permission_policy")
    if not isinstance(permission, dict) or not REQUIRED_PERMISSION_AXES <= _safe_string_set(permission.get("required_declaration_axes")):
        findings.append("permission_policy_incomplete")
    else:
        expected_low_envelope = {
            "shell": "none", "network": "none", "file": "read_only",
            "mcp": "none", "secret": "none",
        }
        if permission.get("low_risk_maximum_envelope") != expected_low_envelope:
            findings.append("low_risk_maximum_envelope_invalid")
        expected_access_enums = {
            axis: sorted(values) for axis, values in ACCESS_ENUMS.items()
        }
        actual_access_enums = permission.get("access_enums")
        if not isinstance(actual_access_enums, dict) or {
            axis: sorted(values) if _string_list(values) else values
            for axis, values in actual_access_enums.items()
        } != expected_access_enums:
            findings.append("permission_policy_access_enums_invalid")
        if (
            _safe_string_set(permission.get("permission_scope_dimensions"))
                != REQUIRED_PERMISSION_SCOPE_FIELDS
            or permission.get("declared_scope_dimension_shape")
                != {
                    "allowed": "unique_bounded_string_list",
                    "blocked": "unique_bounded_string_list",
                }
            or permission.get("observed_scope_dimension_shape")
                != "unique_bounded_string_list"
            or permission.get("observed_must_be_subset_of_reviewed_declared_allowed")
                is not True
            or permission.get("blocked_scope_precedence")
                != "blocked_overrides_allowed"
            or permission.get("narrower_observed_scope_is_permission_escalation")
                is not False
            or permission.get("permission_overdeclaration_may_be_reported")
                is not True
            or permission.get("wildcard_or_unbounded_allowed_or_observed_scope_outcome")
                != "candidate_blocked"
            or permission.get("environment_variable_names_imply_secret_access")
                is not False
            or permission.get("secret_access_uses_named_secret_classes")
                is not True
            or permission.get("raw_secret_values_allowed_in_fixture_metadata")
                is not False
        ):
            findings.append("permission_policy_scope_semantics_invalid")
        if (
            permission.get("undeclared_permission_outcome") != "candidate_blocked"
            or permission.get("permission_escalation_outcome") != "candidate_blocked"
            or permission.get("capability_availability_is_permission") is not False
            or permission.get("installation_is_execution_authorization") is not False
        ):
            findings.append("permission_policy_semantics_invalid")
    rules = fixture.get("fail_closed_rules")
    rule_ids = {
        rule.get("rule_id") for rule in rules
        if isinstance(rule, dict) and isinstance(rule.get("rule_id"), str)
    } if isinstance(rules, list) else set()
    if rule_ids != REQUIRED_FAIL_CLOSED_RULES or not isinstance(rules, list) or len(rules) != len(REQUIRED_FAIL_CLOSED_RULES):
        findings.append("fail_closed_rules_incomplete")
    elif any(
        rule.get("outcome") != REQUIRED_FAIL_CLOSED_OUTCOMES.get(rule.get("rule_id"))
        or rule.get("condition") != REQUIRED_FAIL_CLOSED_CONDITIONS.get(rule.get("rule_id"))
        for rule in rules
    ):
        findings.append("fail_closed_rule_semantics_invalid")
    default_posture = fixture.get("default_posture")
    if not isinstance(default_posture, list) or len(default_posture) != len(REQUIRED_DEFAULT_POSTURE) or _safe_string_set(default_posture) != REQUIRED_DEFAULT_POSTURE:
        findings.append("default_posture_invalid")
    if not REQUIRED_BOUNDARY_STATEMENTS <= _safe_string_set(fixture.get("required_boundary_statements")):
        findings.append("required_boundary_statements_incomplete")
    cva = fixture.get("capture_verify_accumulate")
    cva = cva if isinstance(cva, dict) else {}
    if not REQUIRED_CAPTURE_FIELDS <= _safe_string_set(cva.get("capture")):
        findings.append("capture_fields_incomplete")
    if not REQUIRED_VERIFY_FIELDS <= _safe_string_set(cva.get("verify")):
        findings.append("verify_fields_incomplete")
    if not REQUIRED_ACCUMULATE_FIELDS <= _safe_string_set(cva.get("accumulate")):
        findings.append("accumulate_fields_incomplete")

    high_policy = fixture.get("high_risk_policy")
    required_high_controls = {
        "benchmark_evidence", "evaluation_evidence", "supported_runtime_isolation",
        "sandbox", "human_review", "trace", "replay",
    }
    if (
        not isinstance(high_policy, dict)
        or _safe_string_set(high_policy.get("risk_levels")) != {"high", "critical"}
        or _safe_string_set(high_policy.get("required_controls")) != required_high_controls
        or high_policy.get("benchmark_and_evaluation_are_both_required") is not True
        or high_policy.get("requirement_flags_cannot_disable_controls") is not True
        or high_policy.get("medical_skill_without_evaluation_outcome") != "candidate_blocked"
        or high_policy.get("physical_action_without_sandbox_or_review_outcome") != "candidate_blocked"
        or high_policy.get("risk_acceptance_by_evaluator") is not False
    ):
        findings.append("high_risk_policy_invalid")

    specimen = fixture.get("low_risk_jetson_diagnostic_specimen")
    required_true = {
        "synthetic", "device_mutation_prohibited", "firmware_modification_prohibited",
        "package_installation_prohibited", "credential_access_prohibited",
        "arbitrary_shell_execution_prohibited", "output_schema_validation_required",
        "trace_evidence_required", "replay_evidence_required",
        "immutable_artifact_identity_required",
    }
    required_false = {
        "contains_real_nvidia_code", "contains_real_device_data", "skill_execution_performed",
        "shell_command_execution_performed", "device_access_performed",
        "network_access_performed", "execution_approval",
    }
    if not isinstance(specimen, dict) or any(specimen.get(field) is not True for field in required_true) or any(specimen.get(field) is not False for field in required_false) or specimen.get("intent") != "read_only_diagnostic" or specimen.get("permission_envelope") != "restricted" or specimen.get("maximum_outcome") != "admission_ready_for_review":
        findings.append("synthetic_jetson_specimen_boundary_invalid")

    contract_specimen = contract.get("synthetic_specimen")
    expected_permissions = {
        "shell": "none", "network": "none",
        "file": "read_only", "mcp": "none", "secret": "none",
    }
    specimen_flag_pairs = {
        "synthetic": "synthetic",
        "contains_real_nvidia_code": "contains_real_nvidia_code",
        "contains_real_device_data": "contains_real_device_data",
        "skill_execution_performed": "skill_executed",
        "shell_command_execution_performed": "shell_command_executed",
        "device_access_performed": "device_accessed",
        "network_access_performed": "network_accessed",
        "device_mutation_prohibited": "device_mutation_prohibited",
        "firmware_modification_prohibited": "firmware_modification_prohibited",
        "package_installation_prohibited": "package_installation_prohibited",
        "credential_access_prohibited": "credential_access_prohibited",
        "arbitrary_shell_execution_prohibited": "arbitrary_shell_execution_prohibited",
        "output_schema_validation_required": "output_schema_validation_required",
        "trace_evidence_required": "trace_evidence_required",
        "replay_evidence_required": "replay_evidence_required",
        "immutable_artifact_identity_required": "immutable_artifact_identity_required",
        "maximum_outcome": "maximum_outcome",
    }
    isolation = contract.get("runtime_isolation_requirements")
    output_contract = contract.get("output_contract")
    trace = contract.get("trace_requirements")
    replay = contract.get("replay_requirements")
    required_isolation_flags = {
        "supported", "sandbox_required", "network_disabled", "shell_disabled",
        "filesystem_read_only", "device_access_disabled_during_evaluation",
        "process_spawn_disabled", "secrets_unavailable",
    }
    jetson_cross_binding_invalid = (
        not isinstance(specimen, dict)
        or specimen.get("specimen_id") != "synthetic-jetson-read-only-diagnostic-001"
        or contract.get("skill_id") != EXPECTED_JETSON_SKILL_ID
        or not isinstance(entry, dict)
        or entry.get("skill_id") != EXPECTED_JETSON_SKILL_ID
        or not isinstance(contract_specimen, dict)
        or any(
            specimen.get(outer) != contract_specimen.get(inner)
            for outer, inner in specimen_flag_pairs.items()
        )
        or contract_specimen.get("read_only_diagnostic_intent") is not True
        or contract_specimen.get("restricted_permission_envelope") is not True
        or contract.get("required_permissions") != expected_permissions
        or not isinstance(isolation, dict)
        or any(isolation.get(field) is not True for field in required_isolation_flags)
        or not isinstance(output_contract, dict)
        or output_contract.get("schema_validation_required") is not True
        or output_contract.get("side_effects_allowed") is not False
        or output_contract.get("execution_or_approval_claims_allowed") is not False
        or not isinstance(trace, dict)
        or trace.get("required") is not True
        or trace.get("available") is not True
        or not isinstance(replay, dict)
        or replay.get("required") is not True
        or replay.get("capable") is not True
        or replay.get("evidence_can_be_produced") is not True
        or replay.get("skill_execution_in_replay") is not False
    )
    if jetson_cross_binding_invalid:
        findings.append("synthetic_jetson_contract_binding_invalid")

    if _safe_string_set(fixture.get("allowed_evaluator_outputs")) != ALLOWED_EVALUATOR_OUTPUTS:
        findings.append("allowed_evaluator_outputs_invalid")
    if _safe_string_set(fixture.get("forbidden_evaluator_outputs")) != FORBIDDEN_EVALUATOR_OUTPUTS:
        findings.append("forbidden_evaluator_outputs_invalid")
    cases = fixture.get("fixture_cases") if isinstance(fixture.get("fixture_cases"), list) else []
    actual_case_types = {
        case.get("case_id"): case.get("case_type")
        for case in cases
        if (
            isinstance(case, dict)
            and isinstance(case.get("case_id"), str)
            and isinstance(case.get("case_type"), str)
        )
    }
    if len(cases) != 40 or actual_case_types != EXPECTED_CASE_TYPES:
        findings.append("fixture_cases_not_exactly_40")
    return _dedupe(findings)


def evaluate_skill_admission_fixture(fixture: Any) -> dict[str, Any]:
    """Validate the complete M14 fixture and all declared expected case outcomes."""

    data = fixture if isinstance(fixture, dict) else {}
    reasons = _fixture_findings(data)
    cases = data.get("fixture_cases") if isinstance(data.get("fixture_cases"), list) else []
    case_results: list[dict[str, Any]] = []
    for case in cases:
        if not isinstance(case, dict):
            continue
        result = evaluate_fixture_case(data, str(case.get("case_id") or ""))
        case_results.append(result)
        expected = case.get("expected")
        actual = {key: result.get(key) for key in ("ready_for_review", "candidate_admission_state", "outputs", "reasons")}
        if not isinstance(expected, dict) or actual != expected:
            reasons.append(f"fixture_case_expected_outcome_mismatch:{case.get('case_id')}")
    reasons = _dedupe(reasons)
    valid = not reasons
    return {
        "valid": valid,
        "fixture_valid": valid,
        "ready_for_review": valid,
        "candidate_admission_state": "candidate_restricted" if valid else "candidate_blocked",
        "outputs": ["skill_admission_fixture_valid"] if valid else ["skill_admission_fixture_invalid"],
        "reasons": reasons,
        "case_results": case_results,
    }


evaluate_fixture = evaluate_skill_admission_fixture


__all__ = [
    "ALLOWED_EVALUATOR_OUTPUTS", "FORBIDDEN_EVALUATOR_OUTPUTS",
    "REQUIRED_ACCUMULATE_FIELDS", "REQUIRED_BOUNDARY_STATEMENTS",
    "REQUIRED_CANDIDATE_STATES", "REQUIRED_CAPTURE_FIELDS",
    "REQUIRED_FAIL_CLOSED_RULES", "REQUIRED_IMMUTABLE_BINDINGS",
    "REQUIRED_PERMISSION_AXES", "REQUIRED_REGISTRY_FIELDS",
    "REQUIRED_SKILL_ADMISSION_CONTRACT_FIELDS", "REQUIRED_VERIFY_FIELDS",
    "evaluate_fixture", "evaluate_fixture_case", "evaluate_skill_admission",
    "evaluate_skill_admission_fixture",
]
