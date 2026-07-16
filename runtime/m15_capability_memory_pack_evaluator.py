"""Deterministic evaluator for the M15 Capability Memory Pack contract.

The evaluator checks only caller-supplied declarations and equality bindings.
It does not fetch or hash artifacts, import external repositories, execute a
capability, mutate files, or invoke either Learning Proof or Decision Proof
logic.  A valid result describes an internally coherent evidence record; it
does not grant installation, registration, deployment, or execution authority.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Mapping
from typing import Any

from runtime.authority_semantics import (
    authority_token,
    authority_value_is_affirmative,
    scan_forbidden_authority_claims,
)


SCHEMA_VERSION = "m15-capability-memory-pack/v1"

LIFECYCLE_STATES = frozenset(
    {
        "unverified",
        "verified",
        "stale",
        "incompatible",
        "quarantined",
        "superseded",
        "revoked",
    }
)
COMPATIBILITY_MODES = frozenset({"exact"})
COMPATIBILITY_RESULTS = frozenset({"compatible", "incompatible", "unknown"})
REDISTRIBUTION_STATUSES = frozenset(
    {"allowed", "restricted", "prohibited", "unknown"}
)
LICENSE_REVIEW_STATUSES = frozenset({"reviewed", "review-required", "revoked"})
EVIDENCE_DISPOSITIONS = frozenset(
    {
        "verified-read-only",
        "stale-evidence",
        "quarantined-evidence",
        "incompatible-evidence",
        "revoked-evidence",
        "unverified-evidence",
    }
)
ARTIFACT_ROLES = (
    "structured-spec",
    "workflow-graph",
    "examples",
    "error-taxonomy",
    "graph-snapshot",
    "verification-report",
)
ARTIFACT_ROLE_SET = frozenset(ARTIFACT_ROLES)

NON_AUTHORITATIVE_BOUNDARY_STATEMENT = (
    "This Capability Memory Pack is evidence only; runtime eligibility means "
    "eligibility for independent policy review, not installation, registration, "
    "deployment, execution, risk acceptance, Learning Proof sealing, or Decision "
    "Proof sealing. Capability Pack sealing is undefined and out of scope for M15 "
    "Track B. A capability pack must not claim sealed status or sealing authority."
)

REQUIRED_TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "capability_pack_id",
        "manifest_references",
        "source_manifest",
        "license_manifest",
        "derived_spec_manifest",
        "artifact_inventory",
        "graph_binding",
        "runtime_compatibility",
        "lifecycle_state",
        "lifecycle_evidence",
        "revocation",
        "authority_claims",
        "extensions",
        "retrieval_eligible",
        "runtime_eligible",
        "evidence_disposition",
        "non_authoritative_boundary_statement",
    }
)
OPTIONAL_TOP_LEVEL_FIELDS = frozenset(
    {"related_learning_proof_reference", "related_decision_proof_reference"}
)
ALLOWED_TOP_LEVEL_FIELDS = REQUIRED_TOP_LEVEL_FIELDS | OPTIONAL_TOP_LEVEL_FIELDS

MANIFEST_REFERENCE_FIELDS = frozenset(
    {
        "source_manifest_digest",
        "license_manifest_digest",
        "derived_spec_manifest_digest",
    }
)
SOURCE_MANIFEST_FIELDS = frozenset(
    {
        "manifest_digest",
        "source_reference",
        "source_status",
        "immutable_commit_or_content_digest",
        "upstream_api_version",
    }
)
LICENSE_MANIFEST_FIELDS = frozenset(
    {
        "manifest_digest",
        "license_identifier",
        "redistribution_status",
        "license_review_status",
        "review_evidence_reference",
        "revocation_evidence_reference",
    }
)
DERIVED_MANIFEST_FIELDS = frozenset(
    {
        "manifest_digest",
        "source_manifest_digest",
        "license_manifest_digest",
        "source_api_version",
        "derivation_evidence_reference",
        "artifact_digests",
    }
)
ARTIFACT_FIELDS = frozenset(
    {"role", "path", "digest", "media_type", "executable"}
)
GRAPH_BINDING_FIELDS = frozenset(
    {
        "graph_snapshot_digest",
        "structured_spec_digest",
        "workflow_graph_digest",
        "source_manifest_digest",
        "immutable_source_binding",
        "graph_altered",
        "integrity_evidence_reference",
    }
)
RUNTIME_COMPATIBILITY_FIELDS = frozenset(
    {
        "compatibility_mode",
        "expected_runtime_name",
        "expected_runtime_version",
        "observed_runtime_name",
        "observed_runtime_version",
        "compatibility_result",
        "compatibility_evidence_reference",
    }
)
LIFECYCLE_EVIDENCE_FIELDS = frozenset(
    {
        "stale_reason",
        "version_drift_detected",
        "quarantine_reason",
        "contamination_detected",
        "superseded_by_reference",
        "archival_evidence_retained",
    }
)
REVOCATION_FIELDS = frozenset(
    {"pack_status", "revocation_evidence_reference"}
)

FIXED_FALSE_AUTHORITY_CLAIMS = (
    "installation_approved",
    "tool_registration_approved",
    "deployment_approved",
    "execution_authorized",
    "production_execution_allowed",
    "risk_accepted",
    "rollback_executed",
    "audit_closed",
    "waiver_granted",
    "authority_transferred",
    "capability_pack_sealed",
    "learning_proof_sealed",
    "decision_proof_sealed",
)

FORBIDDEN_AUTHORITY_KEYS = (
    *FIXED_FALSE_AUTHORITY_CLAIMS,
    "installation_approval",
    "installation_authorization",
    "tool_registration_approval",
    "tool_registration_authorization",
    "deployment_approval",
    "deployment_authorization",
    "execution_approval",
    "execution_authorization",
    "production_execution_authorization",
    "risk_acceptance",
    "rollback_execution",
    "audit_closure",
    "waiver",
    "authority_transfer",
    "capability_pack_sealing",
    "learning_proof_sealing",
    "decision_proof_sealing",
    "learning_proof_authorizes_installation",
    "learning_proof_grants_authority",
    "decision_proof_authorizes_execution",
    "decision_proof_grants_execution_authority",
)
FORBIDDEN_AUTHORITY_TOKENS = (
    *FIXED_FALSE_AUTHORITY_CLAIMS,
    "installation_authorized",
    "tool_registration_authorized",
    "deployment_authorized",
    "execution_approved",
    "risk_acceptance_granted",
    "authority_transfer_granted",
)
NORMALIZED_FORBIDDEN_AUTHORITY_KEYS = frozenset(
    authority_token(item) for item in FORBIDDEN_AUTHORITY_KEYS
)

SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
MEDIA_TYPE_PATTERN = re.compile(
    r"^[a-z0-9][a-z0-9.+-]*/[a-z0-9][a-z0-9.+-]*$"
)
SYNTHETIC_SECRET_REFERENCE_PATTERN = re.compile(
    r"^urn:aaos:synthetic-secret-reference:[A-Za-z0-9][A-Za-z0-9._:/-]*$"
)
SYNTHETIC_SECRET_REFERENCE_PREFIX = "urn:aaos:synthetic-secret-reference:"
APPARENT_SECRET_VALUE_SHAPES = (
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{8,}\b", re.I),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{8,}\b", re.I),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{8,}\b", re.I),
    re.compile(r"\bAKIA[A-Z0-9]{12,}\b"),
    re.compile(r"\bBearer\s+\S+", re.I),
    re.compile(r"-----BEGIN [A-Z ]*(?:PRIVATE KEY|CERTIFICATE)-----", re.I),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
)
SECRET_TOKEN_PATTERNS = (
    (
        "access_token",
        re.compile(
            r"(?:access[\s_-]*token|\bBearer\s+\S+|"
            r"\bgh[pousr]_[A-Za-z0-9]{8,}\b|"
            r"\bgithub_pat_[A-Za-z0-9_]{8,}\b|"
            r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b)",
            re.I,
        ),
    ),
    (
        "api_key",
        re.compile(
            r"(?:api[\s_-]*key|\bsk-(?:proj-)?[A-Za-z0-9_-]{8,}\b|"
            r"\bs[\s._-]+k[\s._-]+(?:proj[\s._-]+)?[A-Za-z0-9_-]{8,}\b|"
            r"\bAIza[0-9A-Za-z_-]{20,}\b|"
            r"\bAKIA[A-Z0-9]{12,}\b)",
            re.I,
        ),
    ),
    ("password", re.compile(r"(?:password|passwd)", re.I)),
    ("private_key", re.compile(r"(?:private[\s_-]*key|-----BEGIN [A-Z ]*PRIVATE KEY-----)", re.I)),
    (
        "certificate_material",
        re.compile(
            r"(?:certificate|cert(?:ificate)?[\s_-]*material|"
            r"-----BEGIN CERTIFICATE-----)",
            re.I,
        ),
    ),
    ("production_credential", re.compile(r"prod(?:uction)?[\s_-]*credential", re.I)),
    ("brokerage_account_number", re.compile(r"broker(?:age)?[\s_-]*account[\s_-]*(?:number|identifier|id)", re.I)),
    (
        "personal_identifier",
        re.compile(
            r"(?:personal[\s_-]*(?:identifier|id)|\bssn\b|"
            r"\b\d{3}-\d{2}-\d{4}\b|"
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})",
            re.I,
        ),
    ),
)

AUTHORITY_MACHINE_TOKEN_PATTERNS = tuple(
    re.compile(pattern)
    for pattern in (
        r"(?:^|_)(?:installation|tool_registration|deployment)_"
        r"(?:approval|approved|authorization|authorized)(?:_|$)",
        r"(?:^|_)(?:execution|production_execution)_"
        r"(?:approval|approved|authorization|authorized|allowed)(?:_|$)",
        r"(?:^|_)risk_(?:acceptance|accepted)(?:_|$)",
        r"(?:^|_)rollback_(?:execution|executed)(?:_|$)",
        r"(?:^|_)audit_(?:closure|closed)(?:_|$)",
        r"(?:^|_)waiver_(?:granted|approved|issued)(?:_|$)",
        r"(?:^|_)authority_(?:transfer|transferred)(?:_|$)",
        r"(?:^|_)(?:capability_pack|learning_proof|decision_proof)_"
        r"(?:sealed|sealing)(?:_|$)",
    )
)
AUTHORITY_COMPACT_TOKEN_PATTERNS = tuple(
    re.compile(pattern)
    for pattern in (
        r"(?:installation|toolregistration|deployment)"
        r"(?:approval|approved|authorization|authorized)",
        r"(?:execution|productionexecution)"
        r"(?:approval|approved|authorization|authorized|allowed)",
        r"risk(?:acceptance|accepted)",
        r"rollback(?:execution|executed)",
        r"audit(?:closure|closed)",
        r"waiver(?:granted|approved|issued)",
        r"authority(?:transfer|transferred)",
        r"(?:capabilitypack|learningproof|decisionproof)(?:sealed|sealing)",
    )
)
AUTHORITY_TOKEN_MARKERS = frozenset(
    {
        "approve",
        "approves",
        "approval",
        "approved",
        "allows",
        "authorize",
        "authorizes",
        "authorization",
        "authorized",
        "authority",
        "grant",
        "granted",
        "grants",
        "permit",
        "permits",
        "permitted",
        "permission",
        "permissions",
        "sealing",
        "sealed",
        "enables",
    }
)
AUTHORITY_COMPACT_ACTIONS = (
    "approval",
    "approved",
    "allows",
    "authorization",
    "authorized",
    "authorizes",
    "authority",
    "grant",
    "granted",
    "grants",
    "permit",
    "permits",
    "permitted",
    "sealing",
    "sealed",
    "enables",
)
AUTHORITY_SUBJECT_ACTIONS = AUTHORITY_COMPACT_ACTIONS + (
    "permission",
    "allowed",
    "enabled",
    "complete",
    "completed",
    "registered",
    "installed",
    "deployed",
    "executed",
    "accepted",
    "closed",
    "transferred",
)
AUTHORITY_STATUS_SUBJECTS = frozenset(
    {
        "installation",
        "tool_registration",
        "tool",
        "tools",
        "capability",
        "deployment",
        "execution",
        "production_execution",
        "production_use",
        "risk",
        "rollback",
        "audit",
        "waiver",
        "authority",
        "capability_pack",
        "learning_proof",
        "decision_proof",
    }
)
PROOF_COMPACT_AUTHORITY_PATTERNS = tuple(
    re.compile(pattern)
    for pattern in (
        r"(?:learningproof|decisionproof)(?:grants?|authorizes?|approves?|permits?|allows?|enables?)"
        r"(?:installation|toolregistration|deployment|execution|riskacceptance|authority|sealing)",
        r"(?:learningproof|decisionproof)"
        r"(?:installation|toolregistration|deployment|execution|riskacceptance|authority)"
        r"(?:approved|authorized|granted|allowed|permitted|sealed)",
    )
)
NEGATIVE_AUTHORITY_PHRASES = (
    "not_approved",
    "not_authorized",
    "not_allowed",
    "not_granted",
    "not_accepted",
    "not_executed",
    "not_closed",
    "not_issued",
    "not_sealed",
    "not_transferred",
    "non_authoritative",
    "unauthorized",
    "unapproved",
    "denied",
    "rejected",
    "prohibited",
    "forbidden",
)
NEGATIVE_AUTHORITY_COMPACT_PHRASES = tuple(
    phrase.replace("_", "") for phrase in NEGATIVE_AUTHORITY_PHRASES
)


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _optional_reference_valid(value: Any) -> bool:
    return value is None or _is_nonempty_string(value)


def _dedupe_sorted(findings: list[str]) -> list[str]:
    return sorted(set(findings))


def _object_shape_findings(
    value: Any,
    *,
    path: str,
    required: frozenset[str],
    allowed: frozenset[str] | None = None,
) -> list[str]:
    if not isinstance(value, Mapping):
        return [f"object_required:{path}"]
    findings = [
        f"required_field_missing:{path}.{field}"
        for field in sorted(required)
        if field not in value
    ]
    if allowed is not None:
        findings.extend(
            f"unexpected_field:{path}.{key}"
            for key in sorted(str(item) for item in value)
            if key not in allowed
        )
    return findings


def _digest_finding(value: Any, path: str) -> list[str]:
    if not isinstance(value, str) or SHA256_PATTERN.fullmatch(value) is None:
        return [f"digest_malformed:{path}"]
    return []


def _string_finding(value: Any, path: str) -> list[str]:
    return [] if _is_nonempty_string(value) else [f"nonempty_string_required:{path}"]


def _enum_finding(value: Any, path: str, allowed: frozenset[str]) -> list[str]:
    return [] if isinstance(value, str) and value in allowed else [f"enum_invalid:{path}"]


def _manifest_reference_structure_findings(value: Any) -> list[str]:
    findings = _object_shape_findings(
        value,
        path="manifest_references",
        required=MANIFEST_REFERENCE_FIELDS,
        allowed=MANIFEST_REFERENCE_FIELDS,
    )
    if isinstance(value, Mapping):
        for field in sorted(MANIFEST_REFERENCE_FIELDS):
            findings.extend(_digest_finding(value.get(field), f"manifest_references.{field}"))
    return findings


def _source_manifest_findings(value: Any) -> list[str]:
    findings = _object_shape_findings(
        value,
        path="source_manifest",
        required=SOURCE_MANIFEST_FIELDS,
        allowed=SOURCE_MANIFEST_FIELDS,
    )
    if not isinstance(value, Mapping):
        return findings
    findings.extend(_digest_finding(value.get("manifest_digest"), "source_manifest.manifest_digest"))
    findings.extend(
        _digest_finding(
            value.get("immutable_commit_or_content_digest"),
            "source_manifest.immutable_commit_or_content_digest",
        )
    )
    findings.extend(_string_finding(value.get("source_reference"), "source_manifest.source_reference"))
    findings.extend(_string_finding(value.get("upstream_api_version"), "source_manifest.upstream_api_version"))
    findings.extend(_enum_finding(value.get("source_status"), "source_manifest.source_status", frozenset({"active", "revoked"})))
    return findings


def _license_manifest_findings(value: Any) -> list[str]:
    findings = _object_shape_findings(
        value,
        path="license_manifest",
        required=LICENSE_MANIFEST_FIELDS,
        allowed=LICENSE_MANIFEST_FIELDS,
    )
    if not isinstance(value, Mapping):
        return findings
    findings.extend(_digest_finding(value.get("manifest_digest"), "license_manifest.manifest_digest"))
    findings.extend(_string_finding(value.get("license_identifier"), "license_manifest.license_identifier"))
    findings.extend(_enum_finding(value.get("redistribution_status"), "license_manifest.redistribution_status", REDISTRIBUTION_STATUSES))
    findings.extend(_enum_finding(value.get("license_review_status"), "license_manifest.license_review_status", LICENSE_REVIEW_STATUSES))
    for field in ("review_evidence_reference", "revocation_evidence_reference"):
        if not _optional_reference_valid(value.get(field)):
            findings.append(f"optional_reference_invalid:license_manifest.{field}")
    if value.get("license_review_status") == "reviewed" and not _is_nonempty_string(value.get("review_evidence_reference")):
        findings.append("license_review_evidence_reference_missing")
    if value.get("license_review_status") == "revoked" and not _is_nonempty_string(value.get("revocation_evidence_reference")):
        findings.append("license_revocation_evidence_reference_missing")
    return findings


def _derived_manifest_structure_findings(value: Any) -> list[str]:
    findings = _object_shape_findings(
        value,
        path="derived_spec_manifest",
        required=DERIVED_MANIFEST_FIELDS,
        allowed=DERIVED_MANIFEST_FIELDS,
    )
    if not isinstance(value, Mapping):
        return findings
    for field in ("manifest_digest", "source_manifest_digest", "license_manifest_digest"):
        findings.extend(_digest_finding(value.get(field), f"derived_spec_manifest.{field}"))
    findings.extend(_string_finding(value.get("source_api_version"), "derived_spec_manifest.source_api_version"))
    findings.extend(_string_finding(value.get("derivation_evidence_reference"), "derived_spec_manifest.derivation_evidence_reference"))
    artifact_digests = value.get("artifact_digests")
    findings.extend(
        _object_shape_findings(
            artifact_digests,
            path="derived_spec_manifest.artifact_digests",
            required=ARTIFACT_ROLE_SET,
            allowed=ARTIFACT_ROLE_SET,
        )
    )
    if isinstance(artifact_digests, Mapping):
        for role in ARTIFACT_ROLES:
            findings.extend(_digest_finding(artifact_digests.get(role), f"derived_spec_manifest.artifact_digests.{role}"))
    return findings


def _artifact_inventory_findings(value: Any) -> tuple[list[str], dict[str, Any]]:
    findings: list[str] = []
    by_role: dict[str, Any] = {}
    if not isinstance(value, list):
        return ["artifact_inventory_must_be_array", *[f"artifact_role_missing:{role}" for role in ARTIFACT_ROLES]], by_role

    roles: list[str] = []
    for index, item in enumerate(value):
        path = f"artifact_inventory.{index}"
        findings.extend(_object_shape_findings(item, path=path, required=ARTIFACT_FIELDS, allowed=ARTIFACT_FIELDS))
        if not isinstance(item, Mapping):
            continue
        role = item.get("role")
        role_label = role if isinstance(role, str) and role else str(index)
        if not isinstance(role, str) or role not in ARTIFACT_ROLE_SET:
            findings.append(f"artifact_role_unsupported:{role_label}")
        else:
            roles.append(role)
            if role not in by_role:
                by_role[role] = item.get("digest")
        findings.extend(_string_finding(item.get("path"), f"{path}.path"))
        findings.extend(_string_finding(item.get("media_type"), f"{path}.media_type"))
        if (
            isinstance(item.get("media_type"), str)
            and MEDIA_TYPE_PATTERN.fullmatch(item["media_type"]) is None
        ):
            findings.append(f"media_type_invalid:{path}.media_type")
        findings.extend(_digest_finding(item.get("digest"), f"{path}.digest"))
        if item.get("executable") is not False:
            findings.append(f"executable_artifact_forbidden:{role_label}")

    role_counts = Counter(roles)
    for role in ARTIFACT_ROLES:
        if role_counts[role] == 0:
            findings.append(f"artifact_role_missing:{role}")
        elif role_counts[role] > 1:
            findings.append(f"duplicate_artifact_role:{role}")
    if len(value) != len(ARTIFACT_ROLES):
        findings.append("artifact_inventory_role_count_invalid")
    return findings, by_role


def _graph_structure_findings(value: Any) -> list[str]:
    findings = _object_shape_findings(
        value,
        path="graph_binding",
        required=GRAPH_BINDING_FIELDS,
        allowed=GRAPH_BINDING_FIELDS,
    )
    if not isinstance(value, Mapping):
        return findings
    for field in (
        "graph_snapshot_digest",
        "structured_spec_digest",
        "workflow_graph_digest",
        "source_manifest_digest",
        "immutable_source_binding",
    ):
        findings.extend(_digest_finding(value.get(field), f"graph_binding.{field}"))
    if not isinstance(value.get("graph_altered"), bool):
        findings.append("boolean_required:graph_binding.graph_altered")
    if not _optional_reference_valid(value.get("integrity_evidence_reference")):
        findings.append("optional_reference_invalid:graph_binding.integrity_evidence_reference")
    if value.get("graph_altered") is True and not _is_nonempty_string(
        value.get("integrity_evidence_reference")
    ):
        findings.append("graph_alteration_integrity_evidence_missing")
    return findings


def _runtime_structure_findings(value: Any) -> list[str]:
    findings = _object_shape_findings(
        value,
        path="runtime_compatibility",
        required=RUNTIME_COMPATIBILITY_FIELDS,
        allowed=RUNTIME_COMPATIBILITY_FIELDS,
    )
    if not isinstance(value, Mapping):
        return findings
    findings.extend(_enum_finding(value.get("compatibility_mode"), "runtime_compatibility.compatibility_mode", COMPATIBILITY_MODES))
    findings.extend(_enum_finding(value.get("compatibility_result"), "runtime_compatibility.compatibility_result", COMPATIBILITY_RESULTS))
    for field in (
        "expected_runtime_name",
        "expected_runtime_version",
        "observed_runtime_name",
        "observed_runtime_version",
    ):
        findings.extend(_string_finding(value.get(field), f"runtime_compatibility.{field}"))
    if not _optional_reference_valid(value.get("compatibility_evidence_reference")):
        findings.append("optional_reference_invalid:runtime_compatibility.compatibility_evidence_reference")
    if value.get("compatibility_result") in {"compatible", "incompatible"} and not _is_nonempty_string(
        value.get("compatibility_evidence_reference")
    ):
        findings.append("compatibility_evidence_reference_missing")
    return findings


def _lifecycle_structure_findings(value: Any) -> list[str]:
    findings = _object_shape_findings(
        value,
        path="lifecycle_evidence",
        required=LIFECYCLE_EVIDENCE_FIELDS,
        allowed=LIFECYCLE_EVIDENCE_FIELDS,
    )
    if not isinstance(value, Mapping):
        return findings
    for field in ("stale_reason", "quarantine_reason", "superseded_by_reference"):
        if not _optional_reference_valid(value.get(field)):
            findings.append(f"optional_reference_invalid:lifecycle_evidence.{field}")
    for field in ("version_drift_detected", "contamination_detected", "archival_evidence_retained"):
        if not isinstance(value.get(field), bool):
            findings.append(f"boolean_required:lifecycle_evidence.{field}")
    return findings


def _revocation_structure_findings(value: Any) -> list[str]:
    findings = _object_shape_findings(
        value,
        path="revocation",
        required=REVOCATION_FIELDS,
        allowed=REVOCATION_FIELDS,
    )
    if not isinstance(value, Mapping):
        return findings
    findings.extend(_enum_finding(value.get("pack_status"), "revocation.pack_status", frozenset({"active", "revoked"})))
    if not _optional_reference_valid(value.get("revocation_evidence_reference")):
        findings.append("optional_reference_invalid:revocation.revocation_evidence_reference")
    return findings


def _top_structure_findings(artifact: Mapping[str, Any]) -> list[str]:
    findings: list[str] = []
    if artifact.get("schema_version") != SCHEMA_VERSION:
        findings.append("schema_version_missing_or_unsupported")
    if not _is_nonempty_string(artifact.get("capability_pack_id")):
        findings.append("capability_pack_id_missing")
    findings.extend(
        f"required_field_missing:{field}"
        for field in sorted(REQUIRED_TOP_LEVEL_FIELDS)
        if field not in artifact
    )
    findings.extend(
        f"unexpected_field:{key}"
        for key in sorted(str(item) for item in artifact)
        if key not in ALLOWED_TOP_LEVEL_FIELDS
    )
    findings.extend(_enum_finding(artifact.get("lifecycle_state"), "lifecycle_state", LIFECYCLE_STATES))
    findings.extend(_enum_finding(artifact.get("evidence_disposition"), "evidence_disposition", EVIDENCE_DISPOSITIONS))
    for field in ("retrieval_eligible", "runtime_eligible"):
        if not isinstance(artifact.get(field), bool):
            findings.append(f"boolean_required:{field}")
    if not isinstance(artifact.get("extensions"), Mapping):
        findings.append("object_required:extensions")
    for field in OPTIONAL_TOP_LEVEL_FIELDS:
        if field in artifact and not _optional_reference_valid(artifact.get(field)):
            findings.append(f"optional_reference_invalid:{field}")
    authority_claims = artifact.get("authority_claims")
    if not isinstance(authority_claims, Mapping):
        findings.append("object_required:authority_claims")
    else:
        for field in FIXED_FALSE_AUTHORITY_CLAIMS:
            if field not in authority_claims:
                findings.append(f"authority_claim_missing:{field}")
            elif authority_claims.get(field) is not False:
                findings.append(f"authority_claim_must_be_false:{field}")
    if (
        artifact.get("non_authoritative_boundary_statement")
        != NON_AUTHORITATIVE_BOUNDARY_STATEMENT
    ):
        findings.append("non_authoritative_boundary_statement_invalid")
    return findings


def _schema_conditional_findings(artifact: Mapping[str, Any]) -> list[str]:
    state = artifact.get("lifecycle_state")
    source = artifact.get("source_manifest")
    license_manifest = artifact.get("license_manifest")
    graph = artifact.get("graph_binding")
    runtime = artifact.get("runtime_compatibility")
    evidence = artifact.get("lifecycle_evidence")
    revocation = artifact.get("revocation")
    if not all(
        isinstance(item, Mapping)
        for item in (
            source,
            license_manifest,
            graph,
            runtime,
            evidence,
            revocation,
        )
    ):
        return []
    assert isinstance(source, Mapping)
    assert isinstance(license_manifest, Mapping)
    assert isinstance(graph, Mapping)
    assert isinstance(runtime, Mapping)
    assert isinstance(evidence, Mapping)
    assert isinstance(revocation, Mapping)

    findings: list[str] = []

    def require(condition: bool, label: str) -> None:
        if not condition:
            findings.append("schema_condition_failed:" + label)

    if state == "unverified":
        require(artifact.get("retrieval_eligible") is False, "unverified_retrieval")
        require(artifact.get("runtime_eligible") is False, "unverified_runtime")
        require(
            artifact.get("evidence_disposition") == "unverified-evidence",
            "unverified_disposition",
        )
    elif state == "verified":
        require(source.get("source_status") == "active", "verified_source_active")
        require(
            license_manifest.get("redistribution_status") == "allowed",
            "verified_redistribution_allowed",
        )
        require(
            license_manifest.get("license_review_status") == "reviewed",
            "verified_license_reviewed",
        )
        require(
            _is_nonempty_string(
                license_manifest.get("review_evidence_reference")
            ),
            "verified_license_review_evidence",
        )
        require(graph.get("graph_altered") is False, "verified_graph_unaltered")
        require(
            runtime.get("compatibility_result") == "compatible",
            "verified_runtime_compatible",
        )
        require(
            _is_nonempty_string(runtime.get("compatibility_evidence_reference")),
            "verified_runtime_evidence",
        )
        require(evidence.get("stale_reason") is None, "verified_no_stale_reason")
        require(
            evidence.get("version_drift_detected") is False,
            "verified_no_version_drift",
        )
        require(
            evidence.get("quarantine_reason") is None,
            "verified_no_quarantine_reason",
        )
        require(
            evidence.get("contamination_detected") is False,
            "verified_no_contamination",
        )
        require(
            evidence.get("superseded_by_reference") is None,
            "verified_not_superseded",
        )
        require(revocation.get("pack_status") == "active", "verified_pack_active")
        require(artifact.get("retrieval_eligible") is True, "verified_retrieval")
        require(artifact.get("runtime_eligible") is True, "verified_runtime")
        require(
            artifact.get("evidence_disposition") == "verified-read-only",
            "verified_disposition",
        )
    elif state == "stale":
        require(_is_nonempty_string(evidence.get("stale_reason")), "stale_reason")
        require(evidence.get("version_drift_detected") is True, "stale_version_drift")
        require(artifact.get("runtime_eligible") is False, "stale_runtime")
        require(
            artifact.get("evidence_disposition") == "stale-evidence",
            "stale_disposition",
        )
    elif state == "incompatible":
        require(artifact.get("runtime_eligible") is False, "incompatible_runtime")
        require(
            artifact.get("evidence_disposition") == "incompatible-evidence",
            "incompatible_disposition",
        )
    elif state == "quarantined":
        require(
            _is_nonempty_string(evidence.get("quarantine_reason")),
            "quarantine_reason",
        )
        require(artifact.get("retrieval_eligible") is False, "quarantine_retrieval")
        require(artifact.get("runtime_eligible") is False, "quarantine_runtime")
        require(
            artifact.get("evidence_disposition") == "quarantined-evidence",
            "quarantine_disposition",
        )
    elif state == "superseded":
        require(
            _is_nonempty_string(evidence.get("superseded_by_reference")),
            "superseded_successor",
        )
        require(artifact.get("runtime_eligible") is False, "superseded_runtime")
        require(
            artifact.get("evidence_disposition") == "stale-evidence",
            "superseded_disposition",
        )
    elif state == "revoked":
        require(
            _is_nonempty_string(revocation.get("revocation_evidence_reference")),
            "revoked_evidence",
        )
        require(artifact.get("retrieval_eligible") is False, "revoked_retrieval")
        require(artifact.get("runtime_eligible") is False, "revoked_runtime")
        require(
            artifact.get("evidence_disposition") == "revoked-evidence",
            "revoked_disposition",
        )
        require(
            source.get("source_status") == "revoked"
            or license_manifest.get("license_review_status") == "revoked"
            or revocation.get("pack_status") == "revoked",
            "revoked_status",
        )
    return findings


def _binding_findings(artifact: Mapping[str, Any], inventory: Mapping[str, Any]) -> list[str]:
    findings: list[str] = []
    refs = artifact.get("manifest_references")
    source = artifact.get("source_manifest")
    license_manifest = artifact.get("license_manifest")
    derived = artifact.get("derived_spec_manifest")
    prerequisites = (
        ("manifest_references", refs),
        ("source_manifest", source),
        ("license_manifest", license_manifest),
        ("derived_spec_manifest", derived),
    )
    for label, prerequisite in prerequisites:
        if not isinstance(prerequisite, Mapping):
            findings.append(f"artifact_digest_binding_unavailable:{label}")
    if all(isinstance(item, Mapping) for item in (refs, source, license_manifest, derived)):
        assert isinstance(refs, Mapping)
        assert isinstance(source, Mapping)
        assert isinstance(license_manifest, Mapping)
        assert isinstance(derived, Mapping)
        digest_endpoints = (
            ("manifest_references.source_manifest_digest", refs.get("source_manifest_digest")),
            ("manifest_references.license_manifest_digest", refs.get("license_manifest_digest")),
            ("manifest_references.derived_spec_manifest_digest", refs.get("derived_spec_manifest_digest")),
            ("source_manifest.manifest_digest", source.get("manifest_digest")),
            ("license_manifest.manifest_digest", license_manifest.get("manifest_digest")),
            ("derived_spec_manifest.manifest_digest", derived.get("manifest_digest")),
            ("derived_spec_manifest.source_manifest_digest", derived.get("source_manifest_digest")),
            ("derived_spec_manifest.license_manifest_digest", derived.get("license_manifest_digest")),
        )
        for path, endpoint in digest_endpoints:
            if not isinstance(endpoint, str) or SHA256_PATTERN.fullmatch(endpoint) is None:
                findings.append(f"artifact_digest_binding_endpoint_invalid:{path}")
        if refs.get("source_manifest_digest") != source.get("manifest_digest"):
            findings.append("pack_source_manifest_digest_mismatch")
        if refs.get("license_manifest_digest") != license_manifest.get("manifest_digest"):
            findings.append("pack_license_manifest_digest_mismatch")
        if refs.get("derived_spec_manifest_digest") != derived.get("manifest_digest"):
            findings.append("pack_derived_spec_manifest_digest_mismatch")
        if derived.get("source_manifest_digest") != source.get("manifest_digest"):
            findings.append("derived_source_manifest_digest_mismatch")
        if derived.get("license_manifest_digest") != license_manifest.get("manifest_digest"):
            findings.append("derived_license_manifest_digest_mismatch")
        declared = derived.get("artifact_digests")
        if isinstance(declared, Mapping):
            for role in ARTIFACT_ROLES:
                declared_digest = declared.get(role)
                if (
                    not isinstance(declared_digest, str)
                    or SHA256_PATTERN.fullmatch(declared_digest) is None
                ):
                    findings.append(
                        f"artifact_digest_binding_endpoint_invalid:"
                        f"derived_spec_manifest.artifact_digests.{role}"
                    )
                if role not in inventory:
                    findings.append(
                        f"derived_artifact_inventory_role_missing:{role}"
                    )
                else:
                    inventory_digest = inventory.get(role)
                    if (
                        not isinstance(inventory_digest, str)
                        or SHA256_PATTERN.fullmatch(inventory_digest) is None
                    ):
                        findings.append(
                            f"artifact_digest_binding_endpoint_invalid:"
                            f"artifact_inventory.{role}.digest"
                        )
                if role in inventory and declared_digest != inventory.get(role):
                    findings.append(f"derived_artifact_digest_mismatch:{role}")
        else:
            findings.append("derived_artifact_digest_map_unavailable")
    return findings


def _graph_binding_findings(artifact: Mapping[str, Any], inventory: Mapping[str, Any]) -> list[str]:
    findings: list[str] = []
    graph = artifact.get("graph_binding")
    source = artifact.get("source_manifest")
    if not isinstance(graph, Mapping):
        findings.append("graph_binding_unavailable:graph_binding")
    if not isinstance(source, Mapping):
        findings.append("graph_binding_unavailable:source_manifest")
    if findings:
        return findings
    if graph.get("source_manifest_digest") != source.get("manifest_digest"):
        findings.append("graph_source_manifest_digest_mismatch")
    if graph.get("immutable_source_binding") != source.get("immutable_commit_or_content_digest"):
        findings.append("graph_immutable_source_binding_mismatch")
    comparisons = (
        ("graph_snapshot_digest", "graph-snapshot", "graph_snapshot_digest_mismatch"),
        ("structured_spec_digest", "structured-spec", "graph_structured_spec_digest_mismatch"),
        ("workflow_graph_digest", "workflow-graph", "graph_workflow_graph_digest_mismatch"),
    )
    for graph_field, role, finding in comparisons:
        if role not in inventory:
            findings.append(f"graph_artifact_inventory_role_missing:{role}")
        elif graph.get(graph_field) != inventory.get(role):
            findings.append(finding)
    if graph.get("graph_altered") is True:
        findings.append("graph_alteration_declared")
    return findings


def _runtime_compatibility_findings(value: Any) -> list[str]:
    if not isinstance(value, Mapping):
        return []
    findings: list[str] = []
    if value.get("expected_runtime_name") != value.get("observed_runtime_name"):
        findings.append("runtime_name_mismatch")
    if value.get("expected_runtime_version") != value.get("observed_runtime_version"):
        findings.append("runtime_version_mismatch")
    if value.get("compatibility_result") != "compatible":
        findings.append("compatibility_result_not_compatible")
    if not _is_nonempty_string(value.get("compatibility_evidence_reference")):
        findings.append("compatibility_evidence_reference_missing")
    return findings


def _revocation_state_findings(artifact: Mapping[str, Any]) -> list[str]:
    source = artifact.get("source_manifest")
    license_manifest = artifact.get("license_manifest")
    revocation = artifact.get("revocation")
    if not all(isinstance(item, Mapping) for item in (source, license_manifest, revocation)):
        return []
    assert isinstance(source, Mapping)
    assert isinstance(license_manifest, Mapping)
    assert isinstance(revocation, Mapping)
    state = artifact.get("lifecycle_state")
    revoked_marker = any(
        (
            source.get("source_status") == "revoked",
            license_manifest.get("license_review_status") == "revoked",
            revocation.get("pack_status") == "revoked",
        )
    )
    findings: list[str] = []
    if state == "revoked":
        if not revoked_marker:
            findings.append("revoked_status_marker_missing")
        if not _is_nonempty_string(revocation.get("revocation_evidence_reference")):
            findings.append("revocation_evidence_reference_missing")
    elif revoked_marker:
        findings.append("revoked_status_requires_revoked_lifecycle")
    return findings


def _lifecycle_findings(
    artifact: Mapping[str, Any],
    *,
    binding_findings: list[str],
    graph_findings: list[str],
    runtime_findings: list[str],
    strict_verified_inputs_valid: bool,
) -> list[str]:
    state = artifact.get("lifecycle_state")
    evidence = artifact.get("lifecycle_evidence")
    source = artifact.get("source_manifest")
    license_manifest = artifact.get("license_manifest")
    runtime = artifact.get("runtime_compatibility")
    graph = artifact.get("graph_binding")
    if not all(
        isinstance(item, Mapping)
        for item in (evidence, source, license_manifest, runtime, graph)
    ):
        return []
    assert isinstance(evidence, Mapping)
    assert isinstance(source, Mapping)
    assert isinstance(license_manifest, Mapping)
    assert isinstance(runtime, Mapping)
    assert isinstance(graph, Mapping)
    derived = artifact.get("derived_spec_manifest")
    api_drift = isinstance(derived, Mapping) and source.get("upstream_api_version") != derived.get("source_api_version")
    runtime_mismatch = bool(
        runtime.get("expected_runtime_name") != runtime.get("observed_runtime_name")
        or runtime.get("expected_runtime_version") != runtime.get("observed_runtime_version")
        or runtime.get("compatibility_result") == "incompatible"
    )
    integrity_problem = bool(
        binding_findings
        or graph_findings
        or graph.get("graph_altered") is True
        or evidence.get("contamination_detected") is True
        or _is_nonempty_string(graph.get("integrity_evidence_reference"))
    )
    disposition_for_state = {
        "verified": "verified-read-only",
        "stale": "stale-evidence",
        "incompatible": "incompatible-evidence",
        "quarantined": "quarantined-evidence",
        "revoked": "revoked-evidence",
        "unverified": "unverified-evidence",
        "superseded": "stale-evidence",
    }
    findings: list[str] = []
    expected_disposition = disposition_for_state.get(state)
    if expected_disposition is not None and artifact.get("evidence_disposition") != expected_disposition:
        findings.append("lifecycle_evidence_disposition_mismatch")

    if api_drift:
        findings.append("source_api_version_drift")
    if (
        evidence.get("contamination_detected") is True
        and state not in {"quarantined", "revoked"}
    ):
        findings.append("contamination_requires_quarantine")
    if (
        _is_nonempty_string(graph.get("integrity_evidence_reference"))
        and state not in {"quarantined", "revoked"}
    ):
        findings.append("integrity_evidence_requires_quarantine")
    if state == "verified":
        if not strict_verified_inputs_valid:
            findings.append("verified_lifecycle_requirements_not_met")
        if api_drift:
            findings.append("verified_state_api_version_drift")
        if runtime_findings:
            findings.append("verified_state_runtime_compatibility_invalid")
        if license_manifest.get("license_review_status") != "reviewed":
            findings.append("verified_license_review_missing")
        if not _is_nonempty_string(
            license_manifest.get("review_evidence_reference")
        ):
            findings.append("verified_license_review_evidence_missing")
        if evidence.get("version_drift_detected") is not False:
            findings.append("verified_version_drift_claim")
        if evidence.get("contamination_detected") is not False:
            findings.append("verified_contamination_claim")
        if evidence.get("stale_reason") is not None:
            findings.append("verified_stale_reason_claim")
        if evidence.get("quarantine_reason") is not None:
            findings.append("verified_quarantine_reason_claim")
        if evidence.get("superseded_by_reference") is not None:
            findings.append("verified_supersession_claim")
        if artifact.get("retrieval_eligible") is not True:
            findings.append("verified_retrieval_eligibility_missing")
        if artifact.get("runtime_eligible") is not True:
            findings.append("verified_runtime_eligibility_missing")
    elif state == "stale":
        if not _is_nonempty_string(evidence.get("stale_reason")):
            findings.append("stale_reason_missing")
        if evidence.get("version_drift_detected") is not True or not api_drift:
            findings.append("stale_version_drift_missing")
        if artifact.get("runtime_eligible") is not False:
            findings.append("stale_runtime_eligibility_claim")
    elif state == "incompatible":
        if not runtime_mismatch:
            findings.append("incompatible_runtime_mismatch_missing")
        if runtime.get("compatibility_result") not in {"incompatible", "unknown"}:
            findings.append("incompatible_compatibility_result_invalid")
        if not _is_nonempty_string(runtime.get("compatibility_evidence_reference")):
            findings.append("compatibility_evidence_reference_missing")
        if artifact.get("runtime_eligible") is not False:
            findings.append("incompatible_runtime_eligibility_claim")
    elif state == "quarantined":
        if not integrity_problem:
            findings.append("quarantine_integrity_trigger_missing")
        if not _is_nonempty_string(evidence.get("quarantine_reason")):
            findings.append("quarantine_reason_missing")
        if artifact.get("retrieval_eligible") is not False:
            findings.append("quarantined_retrieval_eligibility_claim")
        if artifact.get("runtime_eligible") is not False:
            findings.append("quarantined_runtime_eligibility_claim")
    elif state == "revoked":
        if artifact.get("retrieval_eligible") is not False:
            findings.append("revoked_retrieval_eligibility_claim")
        if artifact.get("runtime_eligible") is not False:
            findings.append("revoked_runtime_eligibility_claim")
    elif state == "superseded":
        if not _is_nonempty_string(evidence.get("superseded_by_reference")):
            findings.append("superseded_by_reference_missing")
        if artifact.get("runtime_eligible") is not False:
            findings.append("superseded_runtime_eligibility_claim")
    elif state == "unverified":
        if artifact.get("retrieval_eligible") is not False:
            findings.append("unverified_retrieval_eligibility_claim")
        if artifact.get("runtime_eligible") is not False:
            findings.append("unverified_runtime_eligibility_claim")
    return findings


INERT_REFERENCE_PATTERN = re.compile(
    r"^(?:urn:[^\s]+|https?://[^\s]+|[A-Za-z0-9._-]+(?:/[A-Za-z0-9._/-]+)+)$"
)


def _authority_normalized_token(value: Any) -> str:
    camel_split = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", str(value).strip())
    return authority_token(camel_split)


def _extension_value_is_inert(token: str, value: Any) -> bool:
    compact = token.replace("_", "")
    if (
        token.endswith(("_digest", "_hash"))
        or compact.endswith(("digest", "hash"))
        or token in {"digest", "hash"}
    ):
        return isinstance(value, str) and SHA256_PATTERN.fullmatch(value) is not None
    if token.endswith("_references") or compact.endswith("references"):
        return bool(value) and isinstance(value, (list, tuple)) and all(
            isinstance(item, str) and INERT_REFERENCE_PATTERN.fullmatch(item)
            for item in value
        )
    if token.endswith("_reference") or compact.endswith("reference"):
        return isinstance(value, str) and INERT_REFERENCE_PATTERN.fullmatch(value) is not None
    if token.endswith(("_id", "_identifier")) or token in {"id", "identifier"}:
        return bool(
            isinstance(value, str)
            and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]*", value)
            and any(character.isdigit() or character in ":/.-" for character in value)
            and not _authority_machine_token_claim(value)
        )
    if token == "path":
        return isinstance(value, str) and bool(value) and any(
            character in value for character in "/\\."
        )
    if token in {"uri", "url"}:
        return isinstance(value, str) and bool(
            re.match(r"^(?:urn:|https?://)", value)
        )
    if token == "media_type":
        return isinstance(value, str) and MEDIA_TYPE_PATTERN.fullmatch(value) is not None
    if token == "version":
        return isinstance(value, str) and bool(re.search(r"\d", value))
    return False


def _prune_inert_fields(value: Any) -> Any:
    if isinstance(value, Mapping):
        pruned: dict[str, Any] = {}
        for raw_key, child in value.items():
            key = str(raw_key)
            token = _authority_normalized_token(key)
            if _extension_value_is_inert(token, child):
                continue
            pruned[key] = _prune_inert_fields(child)
        return pruned
    if isinstance(value, list):
        return [_prune_inert_fields(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_prune_inert_fields(item) for item in value)
    return value


def _authority_machine_token_claim(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    token = _authority_normalized_token(value)
    for phrase in NEGATIVE_AUTHORITY_PHRASES:
        token = token.replace(phrase, "negative")
    compact = token.replace("_", "")
    for phrase in NEGATIVE_AUTHORITY_COMPACT_PHRASES:
        compact = compact.replace(phrase, "negative")
    if AUTHORITY_TOKEN_MARKERS.intersection(token.split("_")):
        return True
    token_parts = frozenset(token.split("_"))
    if token_parts.intersection(
        {
            "install",
            "installation",
            "register",
            "registration",
            "deploy",
            "deployment",
            "execute",
            "execution",
            "run",
            "production",
        }
    ) and token_parts.intersection(
        {
            "can",
            "may",
            "allow",
            "allowed",
            "enable",
            "enabled",
            "permission",
            "permissions",
            "permit",
            "permits",
            "permitted",
        }
    ):
        return True
    if {"use", "production"}.issubset(token_parts):
        return True
    if token_parts.intersection({"action", "actions"}) and token_parts.intersection(
        {
            "allow",
            "allowed",
            "authorize",
            "authorized",
            "permit",
            "permitted",
            "permission",
            "permissions",
        }
    ):
        return True
    if any(
        subject.replace("_", "") + suffix in compact
        or token.startswith(subject + "_") and token.endswith("_" + suffix)
        for subject in AUTHORITY_STATUS_SUBJECTS
        if subject not in {"learning_proof", "decision_proof"}
        for suffix in ("status", "decision", "claim")
    ):
        return True
    if any(pattern.search(compact) for pattern in PROOF_COMPACT_AUTHORITY_PATTERNS):
        return True
    if any(
        subject.replace("_", "") + action in compact
        for subject in AUTHORITY_STATUS_SUBJECTS
        if subject not in {"learning_proof", "decision_proof"}
        for action in AUTHORITY_SUBJECT_ACTIONS
    ):
        return True
    if any(
        compact == action + suffix
        for action in AUTHORITY_COMPACT_ACTIONS
        for suffix in ("status", "decision", "claim")
    ):
        return True
    return any(
        pattern.search(token) for pattern in AUTHORITY_MACHINE_TOKEN_PATTERNS
    ) or any(
        pattern.search(compact) for pattern in AUTHORITY_COMPACT_TOKEN_PATTERNS
    )


def _scan_open_authority_claims(
    value: Any,
    *,
    path: tuple[str, ...],
) -> list[str]:
    findings: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            token = _authority_normalized_token(key)
            child_path = path + (key,)
            inert = _extension_value_is_inert(token, child)
            key_is_authority_bearing = _authority_machine_token_claim(key)
            if (
                key_is_authority_bearing
                and not inert
                and authority_value_is_affirmative(
                    child,
                    NORMALIZED_FORBIDDEN_AUTHORITY_KEYS,
                )
            ):
                findings.append(
                    "affirmative_forbidden_claim:" + ".".join(child_path)
                )
            if inert:
                continue
            if isinstance(child, (Mapping, list, tuple)):
                findings.extend(
                    _scan_open_authority_claims(child, path=child_path)
                )
            elif not inert and _authority_machine_token_claim(child):
                findings.append(
                    "forbidden_open_machine_token:" + ".".join(child_path)
                )
        return findings
    if isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            findings.extend(
                _scan_open_authority_claims(
                    child,
                    path=path + (str(index),),
                )
            )
        return findings
    if _authority_machine_token_claim(value):
        findings.append("forbidden_open_machine_token:" + ".".join(path))
    return findings


def _linkage_authority_findings(
    value: Any,
    *,
    proof_token: str,
    path: tuple[str, ...] = (),
    proof_context: bool = False,
) -> list[str]:
    findings: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            token = _authority_normalized_token(key)
            child_path = path + (key,)
            if _extension_value_is_inert(token, child):
                continue
            token_compact = token.replace("_", "")
            proof_matches = proof_context or proof_token in token or proof_token.replace(
                "_", ""
            ) in token_compact
            proof_authority_tokens = frozenset(
                {
                    "accept",
                    "accepted",
                    "approval",
                    "approve",
                    "approved",
                    "authority",
                    "authorization",
                    "authorize",
                    "authorized",
                    "deploy",
                    "deployment",
                    "execute",
                    "execution",
                    "grant",
                    "granted",
                    "grants",
                    "install",
                    "installation",
                    "register",
                    "registration",
                    "risk",
                    "seal",
                    "sealed",
                    "sealing",
                }
            )
            proof_authority_key = _authority_machine_token_claim(key) or bool(
                proof_authority_tokens.intersection(token.split("_"))
            )
            if proof_matches and proof_authority_key:
                if authority_value_is_affirmative(child, NORMALIZED_FORBIDDEN_AUTHORITY_KEYS):
                    findings.append(f"{proof_token}_linkage_treated_as_authority:{'.'.join(child_path)}")
            if isinstance(child, (Mapping, list, tuple)):
                findings.extend(
                    _linkage_authority_findings(
                        child,
                        proof_token=proof_token,
                        path=child_path,
                        proof_context=proof_matches,
                    )
                )
            elif isinstance(child, str):
                child_token = _authority_normalized_token(child)
                child_compact = child_token.replace("_", "")
                child_names_proof = proof_token in child_token or proof_token.replace(
                    "_", ""
                ) in child_compact
                if child_names_proof and _authority_machine_token_claim(child):
                    findings.append(
                        f"{proof_token}_linkage_treated_as_authority:"
                        + ".".join(child_path)
                    )
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            findings.extend(
                _linkage_authority_findings(
                    child,
                    proof_token=proof_token,
                    path=path + (str(index),),
                    proof_context=proof_context,
                )
            )
    return findings


def _contains_reference(value: Any, reference: str) -> bool:
    if isinstance(value, Mapping):
        return any(_contains_reference(child, reference) for child in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_reference(child, reference) for child in value)
    return value == reference


def _reference_used_as_authority_findings(
    value: Any,
    *,
    reference: Any,
    proof_token: str,
    path: tuple[str, ...],
) -> list[str]:
    if not _is_nonempty_string(reference):
        return []
    assert isinstance(reference, str)
    findings: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            child_path = path + (key,)
            if (
                _authority_machine_token_claim(key)
                and authority_value_is_affirmative(
                    child,
                    NORMALIZED_FORBIDDEN_AUTHORITY_KEYS,
                )
                and _contains_reference(child, reference)
            ):
                findings.append(
                    f"{proof_token}_linkage_treated_as_authority:"
                    + ".".join(child_path)
                )
            if isinstance(child, (Mapping, list, tuple)):
                findings.extend(
                    _reference_used_as_authority_findings(
                        child,
                        reference=reference,
                        proof_token=proof_token,
                        path=child_path,
                    )
                )
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            findings.extend(
                _reference_used_as_authority_findings(
                    child,
                    reference=reference,
                    proof_token=proof_token,
                    path=path + (str(index),),
                )
            )
    return findings


def _authority_findings(artifact: Mapping[str, Any]) -> tuple[list[str], list[str], list[str]]:
    findings: list[str] = []
    claims = artifact.get("authority_claims")
    if not isinstance(claims, Mapping):
        findings.append("authority_claims_must_be_object")
    else:
        for field in FIXED_FALSE_AUTHORITY_CLAIMS:
            if field not in claims:
                findings.append(f"authority_claim_missing:{field}")
            elif claims.get(field) is not False:
                findings.append(f"authority_claim_must_be_false:{field}")
        dynamic_keys = tuple(dict.fromkeys((*FORBIDDEN_AUTHORITY_KEYS, *(str(key) for key in claims))))
        findings.extend(
            scan_forbidden_authority_claims(
                claims,
                forbidden_keys=dynamic_keys,
                forbidden_tokens=FORBIDDEN_AUTHORITY_TOKENS,
                path=("authority_claims",),
            )
        )

    extensions = artifact.get("extensions")
    if isinstance(extensions, Mapping):
        pruned_extensions = _prune_inert_fields(extensions)
        findings.extend(
            scan_forbidden_authority_claims(
                pruned_extensions,
                forbidden_keys=FORBIDDEN_AUTHORITY_KEYS,
                forbidden_tokens=FORBIDDEN_AUTHORITY_TOKENS,
                path=("extensions",),
            )
        )
        findings.extend(
            _scan_open_authority_claims(
                extensions,
                path=("extensions",),
            )
        )
    lifecycle_evidence = artifact.get("lifecycle_evidence")
    if isinstance(lifecycle_evidence, Mapping):
        open_lifecycle_fields = {
            field: lifecycle_evidence.get(field)
            for field in ("stale_reason", "quarantine_reason")
            if lifecycle_evidence.get(field) is not None
        }
        findings.extend(
            _scan_open_authority_claims(
                open_lifecycle_fields,
                path=("lifecycle_evidence",),
            )
        )
    learning_findings = _linkage_authority_findings(extensions, proof_token="learning_proof", path=("extensions",))
    decision_findings = _linkage_authority_findings(extensions, proof_token="decision_proof", path=("extensions",))
    learning_findings.extend(
        _reference_used_as_authority_findings(
            extensions,
            reference=artifact.get("related_learning_proof_reference"),
            proof_token="learning_proof",
            path=("extensions",),
        )
    )
    decision_findings.extend(
        _reference_used_as_authority_findings(
            extensions,
            reference=artifact.get("related_decision_proof_reference"),
            proof_token="decision_proof",
            path=("extensions",),
        )
    )
    if isinstance(claims, Mapping) and claims.get("learning_proof_sealed") is not False:
        learning_findings.append("learning_proof_linkage_treated_as_authority:authority_claims.learning_proof_sealed")
    if isinstance(claims, Mapping) and claims.get("decision_proof_sealed") is not False:
        decision_findings.append("decision_proof_linkage_treated_as_authority:authority_claims.decision_proof_sealed")
    findings.extend(learning_findings)
    findings.extend(decision_findings)
    if artifact.get("non_authoritative_boundary_statement") != NON_AUTHORITATIVE_BOUNDARY_STATEMENT:
        findings.append("non_authoritative_boundary_statement_invalid")
    return _dedupe_sorted(findings), _dedupe_sorted(learning_findings), _dedupe_sorted(decision_findings)


def _sensitive_scan_text(value: str) -> str:
    separated = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", value)
    separated = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", separated)
    separated = re.sub(r"[^A-Za-z0-9]+", " ", separated)
    compact = re.sub(r"[^A-Za-z0-9]+", "", separated)
    return value + "\n" + separated + "\n" + compact


def _sensitive_material_findings(value: Any, path: tuple[str, ...] = ()) -> list[str]:
    findings: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            child_path = path + (key,)
            rendered_path = ".".join(child_path)
            key_compact = re.sub(r"[^a-z0-9]+", "", key.casefold())
            if key_compact.endswith("secretreferencealias") and (
                not isinstance(child, str)
                or SYNTHETIC_SECRET_REFERENCE_PATTERN.fullmatch(child) is None
            ):
                findings.append(
                    "sensitive_material_detected:"
                    f"synthetic_secret_reference_malformed:{rendered_path}"
                )
            for category, pattern in SECRET_TOKEN_PATTERNS:
                if pattern.search(_sensitive_scan_text(key)):
                    findings.append(f"sensitive_material_detected:{category}:{rendered_path}")
            findings.extend(_sensitive_material_findings(child, child_path))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            findings.extend(_sensitive_material_findings(child, path + (str(index),)))
    elif isinstance(value, str):
        rendered_path = ".".join(path) or "artifact"
        if value.casefold().startswith(SYNTHETIC_SECRET_REFERENCE_PREFIX):
            if SYNTHETIC_SECRET_REFERENCE_PATTERN.fullmatch(value) is None:
                findings.append(
                    "sensitive_material_detected:"
                    f"synthetic_secret_reference_malformed:{rendered_path}"
                )
                return findings
        for category, pattern in SECRET_TOKEN_PATTERNS:
            if pattern.search(_sensitive_scan_text(value)):
                findings.append(f"sensitive_material_detected:{category}:{rendered_path}")
    return _dedupe_sorted(findings)


def evaluate_capability_memory_pack(
    artifact: Mapping[str, object],
) -> dict[str, object]:
    """Evaluate one inert Capability Memory Pack evidence record."""

    if not isinstance(artifact, Mapping):
        return {
            "valid": False,
            "schema_valid": False,
            "pack_identity_valid": False,
            "source_manifest_valid": False,
            "license_manifest_valid": False,
            "derived_manifest_valid": False,
            "artifact_inventory_valid": False,
            "artifact_digest_bindings_valid": False,
            "graph_binding_valid": False,
            "runtime_compatibility_valid": False,
            "lifecycle_valid": False,
            "revocation_state_valid": False,
            "sensitive_material_absent": False,
            "learning_proof_linkage_valid": False,
            "decision_proof_linkage_valid": False,
            "authority_boundary_valid": False,
            "retrieval_eligible": False,
            "runtime_eligible": False,
            "verified_pack_eligible": False,
            "evidence_disposition": None,
            "findings": ["artifact_must_be_object"],
        }

    artifact_dict: Mapping[str, Any] = artifact
    top_findings = _top_structure_findings(artifact_dict)
    manifest_ref_findings = _manifest_reference_structure_findings(artifact_dict.get("manifest_references"))
    source_findings = _source_manifest_findings(artifact_dict.get("source_manifest"))
    license_findings = _license_manifest_findings(artifact_dict.get("license_manifest"))
    derived_findings = _derived_manifest_structure_findings(artifact_dict.get("derived_spec_manifest"))
    inventory_findings, inventory = _artifact_inventory_findings(artifact_dict.get("artifact_inventory"))
    graph_structure_findings = _graph_structure_findings(artifact_dict.get("graph_binding"))
    runtime_structure_findings = _runtime_structure_findings(artifact_dict.get("runtime_compatibility"))
    lifecycle_structure_findings = _lifecycle_structure_findings(artifact_dict.get("lifecycle_evidence"))
    revocation_structure_findings = _revocation_structure_findings(artifact_dict.get("revocation"))
    schema_conditional_findings = _schema_conditional_findings(artifact_dict)

    binding_findings = _binding_findings(artifact_dict, inventory)
    graph_findings = _graph_binding_findings(artifact_dict, inventory)
    runtime_findings = _runtime_compatibility_findings(artifact_dict.get("runtime_compatibility"))
    revocation_findings = _revocation_state_findings(artifact_dict)
    authority_findings, learning_authority_findings, decision_authority_findings = _authority_findings(artifact_dict)
    sensitive_findings = _sensitive_material_findings(artifact_dict)

    schema_findings = [
        *top_findings,
        *manifest_ref_findings,
        *source_findings,
        *license_findings,
        *derived_findings,
        *inventory_findings,
        *graph_structure_findings,
        *runtime_structure_findings,
        *lifecycle_structure_findings,
        *revocation_structure_findings,
        *schema_conditional_findings,
    ]
    schema_valid = not schema_findings
    pack_identity_valid = _is_nonempty_string(artifact_dict.get("capability_pack_id"))
    source_manifest_valid = not source_findings
    license_manifest_valid = not license_findings
    derived_manifest_valid = not derived_findings
    artifact_inventory_valid = not inventory_findings
    artifact_digest_bindings_valid = not binding_findings
    graph_binding_valid = not graph_structure_findings and not graph_findings
    runtime_compatibility_valid = not runtime_structure_findings and not runtime_findings
    revocation_state_valid = not revocation_structure_findings and not revocation_findings
    sensitive_material_absent = not sensitive_findings

    learning_reference_findings: list[str] = []
    if (
        artifact_dict.get("related_learning_proof_reference") is not None
        and not _is_nonempty_string(
            artifact_dict.get("related_learning_proof_reference")
        )
    ):
        learning_reference_findings.append("related_learning_proof_reference_invalid")
    decision_reference_findings: list[str] = []
    if (
        artifact_dict.get("related_decision_proof_reference") is not None
        and not _is_nonempty_string(
            artifact_dict.get("related_decision_proof_reference")
        )
    ):
        decision_reference_findings.append("related_decision_proof_reference_invalid")
    learning_proof_linkage_valid = not learning_reference_findings and not learning_authority_findings
    decision_proof_linkage_valid = not decision_reference_findings and not decision_authority_findings
    authority_boundary_valid = not authority_findings

    strict_verified_inputs_valid = all(
        (
            schema_valid,
            pack_identity_valid,
            source_manifest_valid,
            license_manifest_valid,
            derived_manifest_valid,
            artifact_inventory_valid,
            artifact_digest_bindings_valid,
            graph_binding_valid,
            runtime_compatibility_valid,
            revocation_state_valid,
            sensitive_material_absent,
            learning_proof_linkage_valid,
            decision_proof_linkage_valid,
            authority_boundary_valid,
        )
    )
    lifecycle_findings = _lifecycle_findings(
        artifact_dict,
        binding_findings=binding_findings,
        graph_findings=graph_findings,
        runtime_findings=runtime_findings,
        strict_verified_inputs_valid=strict_verified_inputs_valid,
    )
    lifecycle_error_findings = list(lifecycle_findings)
    if state := artifact_dict.get("lifecycle_state"):
        if state != "verified":
            lifecycle_error_findings = [
                finding
                for finding in lifecycle_error_findings
                if finding != "source_api_version_drift"
            ]
    lifecycle_valid = (
        not lifecycle_structure_findings and not lifecycle_error_findings
    )

    state = artifact_dict.get("lifecycle_state")
    base_record_valid = all(
        (
            schema_valid,
            pack_identity_valid,
            source_manifest_valid,
            license_manifest_valid,
            derived_manifest_valid,
            artifact_inventory_valid,
            revocation_state_valid,
            sensitive_material_absent,
            learning_proof_linkage_valid,
            decision_proof_linkage_valid,
            authority_boundary_valid,
            lifecycle_valid,
            not graph_structure_findings,
            not runtime_structure_findings,
        )
    )
    if state == "verified":
        valid = base_record_valid and artifact_digest_bindings_valid and graph_binding_valid and runtime_compatibility_valid
    elif state == "stale":
        valid = base_record_valid and artifact_digest_bindings_valid and graph_binding_valid and runtime_compatibility_valid
    elif state == "incompatible":
        valid = base_record_valid and artifact_digest_bindings_valid and graph_binding_valid
    elif state == "quarantined":
        valid = base_record_valid
    elif state in {"revoked", "superseded"}:
        valid = base_record_valid and artifact_digest_bindings_valid and graph_binding_valid
    else:
        valid = base_record_valid and artifact_digest_bindings_valid and graph_binding_valid

    source = artifact_dict.get("source_manifest")
    license_manifest = artifact_dict.get("license_manifest")
    revocation = artifact_dict.get("revocation")
    verified_license_eligible = bool(
        isinstance(license_manifest, Mapping)
        and license_manifest.get("redistribution_status") == "allowed"
        and license_manifest.get("license_review_status") == "reviewed"
        and _is_nonempty_string(license_manifest.get("review_evidence_reference"))
    )
    active_statuses = bool(
        isinstance(source, Mapping)
        and source.get("source_status") == "active"
        and isinstance(revocation, Mapping)
        and revocation.get("pack_status") == "active"
    )
    verified_pack_eligible = bool(
        valid
        and state == "verified"
        and verified_license_eligible
        and active_statuses
        and artifact_dict.get("retrieval_eligible") is True
        and artifact_dict.get("runtime_eligible") is True
    )

    findings = _dedupe_sorted(
        [
            *schema_findings,
            *binding_findings,
            *graph_findings,
            *runtime_findings,
            *revocation_findings,
            *authority_findings,
            *sensitive_findings,
            *learning_reference_findings,
            *decision_reference_findings,
            *lifecycle_findings,
        ]
    )
    effective_retrieval_eligible = bool(
        valid and artifact_dict.get("retrieval_eligible") is True
    )
    effective_runtime_eligible = bool(
        valid and artifact_dict.get("runtime_eligible") is True
    )
    return {
        "valid": valid,
        "schema_valid": schema_valid,
        "pack_identity_valid": pack_identity_valid,
        "source_manifest_valid": source_manifest_valid,
        "license_manifest_valid": license_manifest_valid,
        "derived_manifest_valid": derived_manifest_valid,
        "artifact_inventory_valid": artifact_inventory_valid,
        "artifact_digest_bindings_valid": artifact_digest_bindings_valid,
        "graph_binding_valid": graph_binding_valid,
        "runtime_compatibility_valid": runtime_compatibility_valid,
        "lifecycle_valid": lifecycle_valid,
        "revocation_state_valid": revocation_state_valid,
        "sensitive_material_absent": sensitive_material_absent,
        "learning_proof_linkage_valid": learning_proof_linkage_valid,
        "decision_proof_linkage_valid": decision_proof_linkage_valid,
        "authority_boundary_valid": authority_boundary_valid,
        "retrieval_eligible": effective_retrieval_eligible,
        "runtime_eligible": effective_runtime_eligible,
        "verified_pack_eligible": verified_pack_eligible,
        "evidence_disposition": artifact_dict.get("evidence_disposition"),
        "findings": findings,
    }


__all__ = [
    "ARTIFACT_ROLES",
    "COMPATIBILITY_MODES",
    "COMPATIBILITY_RESULTS",
    "EVIDENCE_DISPOSITIONS",
    "FIXED_FALSE_AUTHORITY_CLAIMS",
    "LICENSE_REVIEW_STATUSES",
    "LIFECYCLE_STATES",
    "NON_AUTHORITATIVE_BOUNDARY_STATEMENT",
    "REDISTRIBUTION_STATUSES",
    "SCHEMA_VERSION",
    "evaluate_capability_memory_pack",
]
