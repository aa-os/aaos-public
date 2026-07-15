"""Deterministic, data-only evaluator for the M15 Learning Proof contract.

The evaluator validates caller-supplied evidence.  It performs no source
retrieval, file mutation, network access, subprocess execution, persistence,
training, rollback, deletion, or sealing.  A valid result is evidence that the
record is internally coherent; it is not learning or execution authority.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from runtime.authority_semantics import authority_token, scan_forbidden_authority_claims


SCHEMA_VERSION = "m15-learning-proof/v1"

SOURCE_TYPES = frozenset(
    {
        "prompt",
        "trace",
        "correction",
        "evaluation",
        "decision",
        "tool-output",
        "specification",
        "generated-artifact",
    }
)
SOURCE_OWNERS = frozenset(
    {"organization", "employee", "customer", "provider", "shared", "unknown"}
)
SENSITIVITY_CLASSES = frozenset(
    {"public", "internal", "confidential", "restricted"}
)
SOVEREIGNTY_BOUNDARIES = frozenset(
    {"local", "organization", "tenant", "approved-provider", "external", "public"}
)
ALLOWED_PURPOSES = frozenset(
    {"ephemeral-inference", "evaluation", "memory", "skill", "training", "audit"}
)
AUTHORIZATION_OUTCOMES = frozenset(
    {
        "deny",
        "allow-ephemeral",
        "allow-evaluation-only",
        "allow-memory",
        "allow-skill",
        "allow-training",
        "quarantine",
        "require-review",
    }
)
LIFECYCLE_STATES = frozenset(
    {
        "proposed",
        "verified",
        "quarantined",
        "active",
        "stale",
        "incompatible",
        "superseded",
        "revoked",
        "deletion-pending",
        "deleted",
    }
)

NON_AUTHORITATIVE_BOUNDARY_STATEMENT = (
    "This Learning Proof is evidence only; it grants no persistence, training, "
    "skill, tool, execution, rollback, deletion, sealing, or governance authority."
)

REQUIRED_FIELDS = (
    "schema_version",
    "learning_proof_id",
    "source_type",
    "source_reference",
    "source_owner",
    "source_integrity_hash",
    "source_self_asserted_trust_marker",
    "sensitivity",
    "requested_purpose",
    "authorized_purpose",
    "authorization_outcome",
    "authority_basis_reference",
    "policy_version",
    "processing_boundary",
    "retention_boundary",
    "boundary_evidence_reference",
    "transformation_type",
    "transformation_input_references",
    "transformation_output_reference",
    "lifecycle_state",
    "effective_timestamp",
    "expiration_timestamp",
    "superseded_by_reference",
    "rollback_target",
    "deletion_evidence_reference",
    "related_decision_proof_reference",
    "contamination_detected",
    "contamination_evidence_references",
    "authority_claims",
    "evaluator_findings",
    "non_authoritative_boundary_statement",
)
ALLOWED_FIELDS = frozenset(REQUIRED_FIELDS)

FIXED_FALSE_AUTHORITY_CLAIMS = (
    "release_approved",
    "deployment_approved",
    "execution_authorized",
    "risk_accepted",
    "rollback_executed",
    "deletion_executed",
    "audit_closed",
    "waiver_granted",
    "authority_transferred",
    "learning_proof_sealed",
    "decision_proof_sealed",
)

DECLARED_EVALUATOR_FINDINGS = frozenset(
    {
        "evaluation_only_authorization_recorded",
        "decision_proof_linkage_is_non_authoritative",
        "self_asserted_trust_marker_ignored",
        "rejection_evidence_recorded",
        "source_contamination_detected",
        "revoked_or_poisoned_source_dependency_detected",
        "learning_artifact_quarantined",
        "persistence_and_execution_not_authorized",
        "synthetic_identity_label_present",
        "synthetic_reviewer_label_present",
        "verification_success_observed",
        "schema_validity_observed",
    }
)

FORBIDDEN_AUTHORITY_KEYS = (
    "release_approved",
    "release_approval",
    "release_approval_claim",
    "release_authorization",
    "deployment_approved",
    "deployment_approval",
    "deployment_approval_claim",
    "execution_authorized",
    "execution_authorization",
    "execution_authorization_claim",
    "production_execution_allowed",
    "risk_accepted",
    "risk_acceptance",
    "risk_acceptance_claim",
    "rollback_executed",
    "rollback_execution",
    "rollback_execution_claim",
    "deletion_executed",
    "deletion_execution",
    "audit_closed",
    "audit_closure",
    "audit_closure_claim",
    "waiver_granted",
    "waiver_claim",
    "authority_transferred",
    "authority_transfer",
    "authority_transfer_claim",
    "learning_proof_sealed",
    "learning_proof_sealing",
    "decision_proof_sealed",
    "decision_proof_sealing",
    "decision_proof_to_memory",
    "memory_created_from_decision_proof",
    "persistent_retention_authorized",
    "memory_authorized",
    "memory_creation_authorized",
    "skill_authorized",
    "skill_creation_authorized",
    "training_authorized",
    "tool_registration_approved",
    "final_governance_judgment",
)

FORBIDDEN_AUTHORITY_TOKENS = (
    "release_approved",
    "deployment_approved",
    "execution_authorized",
    "risk_accepted",
    "rollback_executed",
    "deletion_executed",
    "audit_closed",
    "waiver_granted",
    "authority_transferred",
    "learning_proof_sealed",
    "decision_proof_sealed",
    "decision_proof_to_memory",
    "persistent_retention_authorized",
    "memory_authorized",
    "skill_authorized",
    "training_authorized",
)

OUTCOME_PURPOSE = {
    "deny": None,
    "allow-ephemeral": "ephemeral-inference",
    "allow-evaluation-only": "evaluation",
    "allow-memory": "memory",
    "allow-skill": "skill",
    "allow-training": "training",
    "quarantine": None,
    "require-review": None,
}

PERSISTENT_PURPOSES = frozenset({"memory", "skill", "training"})
NON_PERSISTENT_LIFECYCLE_STATES = frozenset(
    {"quarantined", "superseded", "revoked", "deletion-pending", "deleted"}
)
EXTERNAL_BOUNDARIES = frozenset({"external", "public"})

SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
TRANSFORMATION_TYPE_PATTERN = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
AUTHORITY_BASIS_PATTERN = re.compile(
    r"^urn:aaos:m15:authority-basis:[A-Za-z0-9][A-Za-z0-9._:/-]*$"
)
BOUNDARY_EVIDENCE_PATTERN = re.compile(
    r"^urn:aaos:m15:boundary-evidence:[A-Za-z0-9][A-Za-z0-9._:/-]*$"
)
RFC3339_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)

PROSE_AUTHORITY_PATTERNS = tuple(
    re.compile(pattern)
    for pattern in (
        r"release.*(?:approved|authorized|approval_?(?:granted|confirmed|accepted)|authorization_?(?:granted|approved|confirmed|accepted))",
        r"deployment.*(?:approved|authorized|approval_?(?:granted|confirmed)|authorization_?(?:granted|approved|confirmed|accepted))",
        r"execution.*(?:authorized|approved|allowed|permission_?granted|authorization_?(?:granted|approved|confirmed|accepted))",
        r"risk.*(?:accepted|acceptance_?(?:granted|approved|confirmed))",
        r"rollback.*(?:executed|performed|completed)",
        r"deletion.*(?:executed|performed|completed)",
        r"audit.*(?:closed|closure_?(?:granted|approved|confirmed|completed))",
        r"waiver.*(?:granted|approved|accepted|issued)",
        r"authority.*(?:transferred|transfer_?(?:granted|approved|completed|accepted))",
        r"learning_?proof.*(?:sealed|sealing_?(?:completed|confirmed|granted|approved))",
        r"decision_?proof.*(?:sealed|sealing_?(?:completed|confirmed|granted|approved))",
        r"persistent_retention.*(?:authorized|approved|allowed)",
        r"(?:memory|skill|training).*(?:authorized|approved|allowed)",
        r"decision_proof.*(?:became|converted|created).*memory",
    )
)

NEGATIVE_PROSE_PHRASES = (
    "not_authorized",
    "not_approved",
    "not_allowed",
    "not_granted",
    "not_accepted",
    "not_executed",
    "not_performed",
    "not_completed",
    "not_closed",
    "not_issued",
    "not_sealed",
    "not_transferred",
    "non_authoritative",
    "unauthorized",
    "unapproved",
    "unissued",
    "denied",
    "rejected",
    "prohibited",
    "forbidden",
)


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_enum_value(value: Any, allowed: frozenset[str]) -> bool:
    return isinstance(value, str) and value in allowed


def _optional_reference_valid(value: Any) -> bool:
    return value is None or _is_nonempty_string(value)


def _string_list_valid(value: Any, *, min_items: int = 0) -> bool:
    return (
        isinstance(value, list)
        and len(value) >= min_items
        and all(_is_nonempty_string(item) for item in value)
        and len(value) == len(set(value))
    )


def _parse_timestamp(value: Any) -> datetime | None:
    if not _is_nonempty_string(value) or not RFC3339_PATTERN.fullmatch(value):
        return None
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed


def _dedupe_sorted(findings: list[str]) -> list[str]:
    return sorted(set(findings))


def _scan_prose_authority_claims(
    value: Any,
    *,
    path: tuple[str, ...],
) -> list[str]:
    findings: list[str] = []

    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            findings.extend(
                _scan_prose_authority_claims(
                    child,
                    path=path + (str(raw_key),),
                )
            )
        return findings
    if isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(
                _scan_prose_authority_claims(
                    child,
                    path=path + (str(index),),
                )
            )
        return findings
    if not isinstance(value, str):
        return findings

    token = authority_token(value)
    for phrase in NEGATIVE_PROSE_PHRASES:
        token = token.replace(phrase, "negative")
    if any(pattern.search(token) for pattern in PROSE_AUTHORITY_PATTERNS):
        findings.append("affirmative_forbidden_prose_claim:" + ".".join(path))
    return findings


def _structure_findings(artifact: Mapping[str, Any]) -> list[str]:
    findings: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in artifact:
            findings.append(f"required_field_missing:{field}")
    for raw_field in artifact:
        field = str(raw_field)
        if field not in ALLOWED_FIELDS:
            findings.append(f"unknown_top_level_field:{field}")

    if artifact.get("schema_version") != SCHEMA_VERSION:
        findings.append("schema_version_missing_or_unsupported")

    required_strings = (
        "learning_proof_id",
        "source_reference",
        "authority_basis_reference",
        "policy_version",
        "transformation_type",
        "transformation_output_reference",
        "effective_timestamp",
        "non_authoritative_boundary_statement",
    )
    for field in required_strings:
        if not _is_nonempty_string(artifact.get(field)):
            findings.append(f"field_must_be_nonempty_string:{field}")

    transformation_type = artifact.get("transformation_type")
    if not (
        isinstance(transformation_type, str)
        and TRANSFORMATION_TYPE_PATTERN.fullmatch(transformation_type)
    ):
        findings.append("transformation_type_invalid")

    authority_basis = artifact.get("authority_basis_reference")
    if _is_nonempty_string(authority_basis) and not AUTHORITY_BASIS_PATTERN.fullmatch(
        authority_basis
    ):
        findings.append("authority_basis_reference_kind_invalid")

    if not _is_enum_value(artifact.get("source_type"), SOURCE_TYPES):
        findings.append("source_type_unknown")
    if not _is_enum_value(artifact.get("source_owner"), SOURCE_OWNERS):
        findings.append("source_owner_unknown")
    if not _is_enum_value(artifact.get("sensitivity"), SENSITIVITY_CLASSES):
        findings.append("sensitivity_unknown")
    if not _is_enum_value(artifact.get("requested_purpose"), ALLOWED_PURPOSES):
        findings.append("requested_purpose_unknown")

    authorized_purpose = artifact.get("authorized_purpose")
    if authorized_purpose is not None and not _is_enum_value(
        authorized_purpose, ALLOWED_PURPOSES
    ):
        findings.append("authorized_purpose_unknown")
    if not _is_enum_value(
        artifact.get("authorization_outcome"), AUTHORIZATION_OUTCOMES
    ):
        findings.append("authorization_outcome_unknown")
    if not _is_enum_value(
        artifact.get("processing_boundary"), SOVEREIGNTY_BOUNDARIES
    ):
        findings.append("processing_boundary_unknown")
    if not _is_enum_value(
        artifact.get("retention_boundary"), SOVEREIGNTY_BOUNDARIES
    ):
        findings.append("retention_boundary_unknown")
    if not _is_enum_value(artifact.get("lifecycle_state"), LIFECYCLE_STATES):
        findings.append("lifecycle_state_unknown")

    source_hash = artifact.get("source_integrity_hash")
    if not _is_nonempty_string(source_hash):
        findings.append("source_integrity_hash_missing")
    elif not SHA256_PATTERN.fullmatch(source_hash):
        findings.append("source_integrity_hash_malformed")

    optional_references = (
        "source_self_asserted_trust_marker",
        "boundary_evidence_reference",
        "expiration_timestamp",
        "superseded_by_reference",
        "rollback_target",
        "deletion_evidence_reference",
        "related_decision_proof_reference",
    )
    for field in optional_references:
        if not _optional_reference_valid(artifact.get(field)):
            findings.append(f"optional_reference_invalid:{field}")

    boundary_evidence = artifact.get("boundary_evidence_reference")
    if boundary_evidence is not None and (
        not _is_nonempty_string(boundary_evidence)
        or not BOUNDARY_EVIDENCE_PATTERN.fullmatch(boundary_evidence)
    ):
        findings.append("boundary_evidence_reference_invalid")

    if not _string_list_valid(
        artifact.get("transformation_input_references"), min_items=1
    ):
        findings.append("transformation_input_references_invalid")
    if not _string_list_valid(artifact.get("contamination_evidence_references")):
        findings.append("contamination_evidence_references_invalid")
    if not _string_list_valid(artifact.get("evaluator_findings")):
        findings.append("evaluator_findings_invalid")
    else:
        for item in artifact.get("evaluator_findings", []):
            if item not in DECLARED_EVALUATOR_FINDINGS:
                findings.append("evaluator_finding_unknown:" + item)

    if not isinstance(artifact.get("contamination_detected"), bool):
        findings.append("contamination_detected_must_be_boolean")

    authority_claims = artifact.get("authority_claims")
    if not isinstance(authority_claims, Mapping):
        findings.append("authority_claims_must_be_object")
    else:
        for field in FIXED_FALSE_AUTHORITY_CLAIMS:
            if field not in authority_claims:
                findings.append(f"authority_claim_missing:{field}")
            elif authority_claims.get(field) is not False:
                findings.append(f"authority_claim_must_be_false:{field}")

    if _parse_timestamp(artifact.get("effective_timestamp")) is None:
        findings.append("effective_timestamp_invalid")
    expiration = artifact.get("expiration_timestamp")
    if expiration is not None and _parse_timestamp(expiration) is None:
        findings.append("expiration_timestamp_invalid")
    if artifact.get("non_authoritative_boundary_statement") != (
        NON_AUTHORITATIVE_BOUNDARY_STATEMENT
    ):
        findings.append("non_authoritative_boundary_statement_invalid")

    outcome = artifact.get("authorization_outcome")
    requested = artifact.get("requested_purpose")
    authorized = artifact.get("authorized_purpose")
    state = artifact.get("lifecycle_state")
    if _is_enum_value(outcome, AUTHORIZATION_OUTCOMES):
        expected = OUTCOME_PURPOSE[outcome]
        if authorized != expected:
            findings.append("schema_outcome_authorized_purpose_conflict")
        if expected is not None and requested != expected:
            findings.append("schema_outcome_requested_purpose_conflict")
    if outcome == "deny" and state == "active":
        findings.append("schema_denied_artifact_active")
    if outcome == "quarantine":
        if state != "quarantined":
            findings.append("schema_quarantine_lifecycle_conflict")
        if artifact.get("contamination_detected") is not True:
            findings.append("schema_quarantine_contamination_missing")
        contamination_evidence = artifact.get("contamination_evidence_references")
        if not isinstance(contamination_evidence, list) or not contamination_evidence:
            findings.append("schema_quarantine_evidence_missing")
    if artifact.get("contamination_detected") is True:
        contamination_evidence = artifact.get("contamination_evidence_references")
        if not isinstance(contamination_evidence, list) or not contamination_evidence:
            findings.append("schema_contamination_evidence_missing")
        if outcome != "quarantine" or state != "quarantined":
            findings.append("schema_contamination_requires_quarantine")
        if authorized is not None:
            findings.append("schema_contamination_authorized_purpose_conflict")
    if (
        _is_enum_value(artifact.get("processing_boundary"), EXTERNAL_BOUNDARIES)
        or _is_enum_value(
            artifact.get("retention_boundary"), EXTERNAL_BOUNDARIES
        )
    ) and not _is_nonempty_string(artifact.get("boundary_evidence_reference")):
        findings.append("schema_external_or_public_boundary_evidence_missing")
    if _is_enum_value(state, NON_PERSISTENT_LIFECYCLE_STATES) and _is_enum_value(
        authorized, PERSISTENT_PURPOSES
    ):
        findings.append("schema_inactive_lifecycle_persistence_conflict")
    if state == "deleted" and not _is_nonempty_string(
        artifact.get("deletion_evidence_reference")
    ):
        findings.append("schema_deletion_evidence_missing")

    return _dedupe_sorted(findings)


def _classification_findings(artifact: Mapping[str, Any]) -> list[str]:
    findings: list[str] = []
    if not _is_enum_value(artifact.get("source_type"), SOURCE_TYPES):
        findings.append("source_type_unknown")
    if not _is_enum_value(artifact.get("source_owner"), SOURCE_OWNERS):
        findings.append("source_owner_unknown")
    if not _is_enum_value(artifact.get("sensitivity"), SENSITIVITY_CLASSES):
        findings.append("sensitivity_unknown")
    if not _is_enum_value(artifact.get("requested_purpose"), ALLOWED_PURPOSES):
        findings.append("requested_purpose_unknown")
    return findings


def _boundary_findings(artifact: Mapping[str, Any]) -> list[str]:
    findings: list[str] = []
    processing = artifact.get("processing_boundary")
    retention = artifact.get("retention_boundary")
    evidence = artifact.get("boundary_evidence_reference")

    if not _is_enum_value(processing, SOVEREIGNTY_BOUNDARIES):
        findings.append("processing_boundary_unknown")
    if not _is_enum_value(retention, SOVEREIGNTY_BOUNDARIES):
        findings.append("retention_boundary_unknown")
    if evidence is not None and (
        not _is_nonempty_string(evidence)
        or not BOUNDARY_EVIDENCE_PATTERN.fullmatch(evidence)
    ):
        findings.append("boundary_evidence_reference_invalid")
    if (
        _is_enum_value(processing, EXTERNAL_BOUNDARIES)
        or _is_enum_value(retention, EXTERNAL_BOUNDARIES)
    ):
        if not _is_nonempty_string(evidence):
            findings.append("external_or_public_boundary_evidence_missing")
        elif not BOUNDARY_EVIDENCE_PATTERN.fullmatch(evidence):
            findings.append("external_or_public_boundary_evidence_invalid")
        for inert_field in (
            "source_reference",
            "source_self_asserted_trust_marker",
            "related_decision_proof_reference",
            "authority_basis_reference",
        ):
            inert_value = artifact.get(inert_field)
            if inert_value is not None and evidence == inert_value:
                findings.append(
                    "boundary_evidence_reuses_non_boundary_field:" + inert_field
                )
    return findings


def _authorization_evidence_findings(
    artifact: Mapping[str, Any],
) -> list[str]:
    findings: list[str] = []
    outcome = artifact.get("authorization_outcome")
    basis = artifact.get("authority_basis_reference")

    if not _is_enum_value(outcome, AUTHORIZATION_OUTCOMES):
        findings.append("authorization_outcome_unknown")
    if not _is_nonempty_string(basis):
        findings.append("authority_basis_reference_missing")
    elif _is_enum_value(outcome, AUTHORIZATION_OUTCOMES):
        if not AUTHORITY_BASIS_PATTERN.fullmatch(basis):
            findings.append("authority_basis_reference_kind_invalid")
        for inert_field in (
            "learning_proof_id",
            "source_reference",
            "source_self_asserted_trust_marker",
            "policy_version",
            "related_decision_proof_reference",
        ):
            inert_value = artifact.get(inert_field)
            if inert_value is not None and basis == inert_value:
                findings.append(
                    "authority_basis_reuses_non_authoritative_field:"
                    + inert_field
                )
        self_asserted_marker = artifact.get("source_self_asserted_trust_marker")
        basis_suffix = basis.split("urn:aaos:m15:authority-basis:", 1)[-1]
        basis_token = authority_token(basis_suffix)
        if _is_nonempty_string(self_asserted_marker):
            marker_token = authority_token(self_asserted_marker)
            if marker_token and marker_token in basis_token:
                findings.append(
                    "authority_basis_derived_from_self_asserted_trust_marker"
                )
        for inert_field in (
            "learning_proof_id",
            "source_reference",
            "related_decision_proof_reference",
        ):
            inert_value = artifact.get(inert_field)
            if not _is_nonempty_string(inert_value):
                continue
            inert_identifier = authority_token(inert_value.rsplit(":", 1)[-1])
            if inert_identifier and inert_identifier in basis_token:
                findings.append(
                    "authority_basis_derived_from_non_authoritative_field:"
                    + inert_field
                )
    if not _is_nonempty_string(artifact.get("policy_version")):
        findings.append("policy_version_missing")
    return findings


def _purpose_separation_findings(
    artifact: Mapping[str, Any],
) -> list[str]:
    findings: list[str] = []
    requested = artifact.get("requested_purpose")
    authorized = artifact.get("authorized_purpose")
    outcome = artifact.get("authorization_outcome")

    if not _is_enum_value(requested, ALLOWED_PURPOSES):
        findings.append("requested_purpose_unknown")
    if authorized is not None and not _is_enum_value(authorized, ALLOWED_PURPOSES):
        findings.append("authorized_purpose_unknown")
    if not _is_enum_value(outcome, AUTHORIZATION_OUTCOMES):
        findings.append("authorization_outcome_unknown")
        return findings

    expected = OUTCOME_PURPOSE[outcome]
    if authorized != expected:
        findings.append("authorization_outcome_and_purpose_conflict")
    if authorized is not None and requested != authorized:
        findings.append("requested_and_authorized_purpose_conflict")
    if outcome == "allow-evaluation-only" and _is_enum_value(
        authorized, PERSISTENT_PURPOSES
    ):
        findings.append("evaluation_only_persistence_conflict")
    return findings


def _lifecycle_findings(artifact: Mapping[str, Any]) -> list[str]:
    findings: list[str] = []
    state = artifact.get("lifecycle_state")
    outcome = artifact.get("authorization_outcome")
    authorized = artifact.get("authorized_purpose")

    if not _is_enum_value(state, LIFECYCLE_STATES):
        findings.append("lifecycle_state_unknown")
        return findings

    if outcome == "quarantine" and state != "quarantined":
        findings.append("quarantine_outcome_lifecycle_conflict")
    if (outcome == "deny" or outcome == "quarantine") and state == "active":
        findings.append("denied_or_quarantined_artifact_active")
    if _is_enum_value(state, NON_PERSISTENT_LIFECYCLE_STATES) and _is_enum_value(
        authorized, PERSISTENT_PURPOSES
    ):
        findings.append("inactive_lifecycle_authorizes_new_persistence")
    if state == "deleted" and not _is_nonempty_string(
        artifact.get("deletion_evidence_reference")
    ):
        findings.append("deletion_evidence_reference_missing")

    effective = _parse_timestamp(artifact.get("effective_timestamp"))
    expiration_value = artifact.get("expiration_timestamp")
    expiration = (
        _parse_timestamp(expiration_value) if expiration_value is not None else None
    )
    if effective is None:
        findings.append("effective_timestamp_invalid")
    if expiration_value is not None and expiration is None:
        findings.append("expiration_timestamp_invalid")
    if effective is not None and expiration is not None and expiration < effective:
        findings.append("expiration_precedes_effective_timestamp")
    return findings


def _contamination_findings(artifact: Mapping[str, Any]) -> list[str]:
    findings: list[str] = []
    detected = artifact.get("contamination_detected")
    evidence = artifact.get("contamination_evidence_references")
    outcome = artifact.get("authorization_outcome")
    state = artifact.get("lifecycle_state")
    declared_findings = artifact.get("evaluator_findings")

    if not isinstance(detected, bool):
        findings.append("contamination_detected_must_be_boolean")
        return findings
    if not _string_list_valid(evidence):
        findings.append("contamination_evidence_references_invalid")
        return findings
    if detected and not evidence:
        findings.append("contamination_evidence_missing")
    if not detected and evidence:
        findings.append("contamination_evidence_without_detection")
    if detected:
        if outcome != "quarantine" or state != "quarantined":
            findings.append("contamination_requires_quarantine")
        if artifact.get("authorized_purpose") is not None:
            findings.append("contamination_authorizes_learning_purpose")
    if outcome == "quarantine" or state == "quarantined":
        if outcome != "quarantine" or state != "quarantined":
            findings.append("quarantine_state_and_outcome_conflict")
        if not detected:
            findings.append("quarantine_without_contamination_detection")
        if not (
            _string_list_valid(declared_findings)
            and any("contamination" in item.casefold() for item in declared_findings)
        ):
            findings.append("quarantine_contamination_finding_missing")
    return findings


def _authority_boundary_findings(artifact: Mapping[str, Any]) -> list[str]:
    findings: list[str] = []
    authority_claims = artifact.get("authority_claims")

    transformation_type = artifact.get("transformation_type")
    findings.extend(
        scan_forbidden_authority_claims(
            transformation_type,
            forbidden_keys=FORBIDDEN_AUTHORITY_KEYS,
            forbidden_tokens=FORBIDDEN_AUTHORITY_TOKENS,
            path=("transformation_type",),
        )
    )
    findings.extend(
        _scan_prose_authority_claims(
            transformation_type,
            path=("transformation_type",),
        )
    )

    if isinstance(authority_claims, Mapping):
        dynamic_keys = tuple(
            dict.fromkeys(
                FORBIDDEN_AUTHORITY_KEYS
                + tuple(str(key) for key in authority_claims.keys())
            )
        )
        findings.extend(
            scan_forbidden_authority_claims(
                authority_claims,
                forbidden_keys=dynamic_keys,
                forbidden_tokens=FORBIDDEN_AUTHORITY_TOKENS,
                path=("authority_claims",),
            )
        )
    else:
        findings.append("authority_claims_must_be_object")

    unknown_payload = {
        str(key): value for key, value in artifact.items() if str(key) not in ALLOWED_FIELDS
    }
    if unknown_payload:
        findings.extend(
            scan_forbidden_authority_claims(
                unknown_payload,
                forbidden_keys=FORBIDDEN_AUTHORITY_KEYS,
                forbidden_tokens=FORBIDDEN_AUTHORITY_TOKENS,
            )
        )
        findings.extend(
            _scan_prose_authority_claims(unknown_payload, path=())
        )

    declared_findings = artifact.get("evaluator_findings")
    if isinstance(declared_findings, list):
        findings.extend(
            scan_forbidden_authority_claims(
                declared_findings,
                forbidden_keys=FORBIDDEN_AUTHORITY_KEYS,
                forbidden_tokens=FORBIDDEN_AUTHORITY_TOKENS,
                path=("evaluator_findings",),
            )
        )
        findings.extend(
            _scan_prose_authority_claims(
                declared_findings,
                path=("evaluator_findings",),
            )
        )
        for index, item in enumerate(declared_findings):
            if not isinstance(item, str) or item not in DECLARED_EVALUATOR_FINDINGS:
                findings.append(f"unrecognized_evaluator_finding:{index}")

    if artifact.get("non_authoritative_boundary_statement") != (
        NON_AUTHORITATIVE_BOUNDARY_STATEMENT
    ):
        findings.append("non_authoritative_boundary_statement_invalid")
    return _dedupe_sorted(findings)


def _decision_proof_linkage_findings(
    artifact: Mapping[str, Any],
) -> list[str]:
    findings: list[str] = []
    reference = artifact.get("related_decision_proof_reference")
    basis = artifact.get("authority_basis_reference")

    if reference is not None:
        if not _is_nonempty_string(reference):
            findings.append("related_decision_proof_reference_invalid")
        if reference == basis:
            findings.append("decision_proof_used_as_learning_authority_basis")
    if _is_nonempty_string(basis) and basis.startswith("urn:aaos:decision-proof:"):
        findings.append("decision_proof_used_as_learning_authority_basis")
    return findings


def _evidence_disposition(outcome: Any) -> str:
    if not isinstance(outcome, str):
        return "invalid-evidence"
    return {
        "deny": "denied-evidence",
        "allow-ephemeral": "ephemeral-evidence",
        "allow-evaluation-only": "evaluation-only-evidence",
        "allow-memory": "memory-authorization-evidence",
        "allow-skill": "skill-authorization-evidence",
        "allow-training": "training-authorization-evidence",
        "quarantine": "quarantine-evidence",
        "require-review": "review-required-evidence",
    }.get(outcome, "invalid-evidence")


def evaluate_learning_proof(
    artifact: Mapping[str, object],
) -> dict[str, object]:
    """Evaluate one inert Learning Proof record without external side effects."""

    if not isinstance(artifact, Mapping):
        return {
            "valid": False,
            "schema_valid": False,
            "source_integrity_present": False,
            "source_integrity_format_valid": False,
            "classification_valid": False,
            "boundary_valid": False,
            "authorization_evidence_valid": False,
            "purpose_separation_valid": False,
            "lifecycle_valid": False,
            "contamination_state_valid": False,
            "authority_boundary_valid": False,
            "decision_proof_linkage_valid": False,
            "authorization_outcome": None,
            "authorized_purpose": None,
            "evidence_disposition": "invalid-evidence",
            "findings": ["artifact_must_be_object"],
        }

    artifact_dict: Mapping[str, Any] = artifact
    findings = _structure_findings(artifact_dict)
    schema_valid = not findings

    source_reference_present = _is_nonempty_string(
        artifact_dict.get("source_reference")
    )
    source_hash = artifact_dict.get("source_integrity_hash")
    source_hash_present = _is_nonempty_string(source_hash)
    source_integrity_present = source_reference_present and source_hash_present
    source_integrity_format_valid = bool(
        source_integrity_present and SHA256_PATTERN.fullmatch(source_hash)
    )
    if not source_reference_present:
        findings.append("source_reference_missing")
    if not source_hash_present:
        findings.append("source_integrity_hash_missing")
    elif not SHA256_PATTERN.fullmatch(source_hash):
        findings.append("source_integrity_hash_malformed")

    classification_findings = _classification_findings(artifact_dict)
    boundary_findings = _boundary_findings(artifact_dict)
    authorization_findings = _authorization_evidence_findings(artifact_dict)
    purpose_findings = _purpose_separation_findings(artifact_dict)
    lifecycle_findings = _lifecycle_findings(artifact_dict)
    contamination_findings = _contamination_findings(artifact_dict)
    authority_findings = _authority_boundary_findings(artifact_dict)
    decision_proof_findings = _decision_proof_linkage_findings(artifact_dict)

    findings.extend(classification_findings)
    findings.extend(boundary_findings)
    findings.extend(authorization_findings)
    findings.extend(purpose_findings)
    findings.extend(lifecycle_findings)
    findings.extend(contamination_findings)
    findings.extend(authority_findings)
    findings.extend(decision_proof_findings)

    outcome = artifact_dict.get("authorization_outcome")
    if outcome == "deny":
        findings.append("authorization_denied")
    if outcome == "quarantine":
        findings.append("contamination_quarantine_recorded")
    if _is_nonempty_string(artifact_dict.get("source_self_asserted_trust_marker")):
        findings.append("self_asserted_trust_marker_ignored")
    if artifact_dict.get("related_decision_proof_reference") is not None:
        findings.append("decision_proof_reference_is_linkage_only")

    result_dimensions = (
        schema_valid,
        source_integrity_present,
        source_integrity_format_valid,
        not classification_findings,
        not boundary_findings,
        not authorization_findings,
        not purpose_findings,
        not lifecycle_findings,
        not contamination_findings,
        not authority_findings,
        not decision_proof_findings,
    )

    return {
        "valid": all(result_dimensions),
        "schema_valid": schema_valid,
        "source_integrity_present": source_integrity_present,
        "source_integrity_format_valid": source_integrity_format_valid,
        "classification_valid": not classification_findings,
        "boundary_valid": not boundary_findings,
        "authorization_evidence_valid": not authorization_findings,
        "purpose_separation_valid": not purpose_findings,
        "lifecycle_valid": not lifecycle_findings,
        "contamination_state_valid": not contamination_findings,
        "authority_boundary_valid": not authority_findings,
        "decision_proof_linkage_valid": not decision_proof_findings,
        "authorization_outcome": (
            outcome if isinstance(outcome, str) else None
        ),
        "authorized_purpose": artifact_dict.get("authorized_purpose"),
        "evidence_disposition": _evidence_disposition(outcome),
        "findings": _dedupe_sorted(findings),
    }


__all__ = [
    "ALLOWED_PURPOSES",
    "AUTHORIZATION_OUTCOMES",
    "LIFECYCLE_STATES",
    "NON_AUTHORITATIVE_BOUNDARY_STATEMENT",
    "SCHEMA_VERSION",
    "SENSITIVITY_CLASSES",
    "SOURCE_OWNERS",
    "SOURCE_TYPES",
    "SOVEREIGNTY_BOUNDARIES",
    "evaluate_learning_proof",
]
