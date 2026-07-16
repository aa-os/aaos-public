"""Deterministic M15 Track C lineage, rollback, deletion, and portability evaluator.

The evaluator consumes caller-supplied inert mappings only.  It performs no
network access, file access, subprocess execution, dynamic import, model call,
provider operation, rollback, deletion, or external state transition.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from runtime.authority_semantics import (
    authority_token,
    authority_value_is_affirmative,
    scan_forbidden_authority_claims,
)


SCHEMA_VERSION = "m15-lineage-rollback-portability/v1"
LEARNING_PROOF_SCHEMA_VERSION = "m15-learning-proof/v1"
CAPABILITY_PACK_SCHEMA_VERSION = "m15-capability-memory-pack/v1"
NON_AUTHORITATIVE_BOUNDARY_STATEMENT = (
    "This Track C record is evidence only; it authorizes and executes no "
    "lifecycle action, rollback, deletion, provider disconnection, "
    "replacement-model use, installation, deployment, production workflow, "
    "risk acceptance, audit closure, waiver, authority transfer, Learning "
    "Proof sealing, or Decision Proof sealing."
)

RECORD_KINDS = (
    "dependency-graph",
    "supersession",
    "revocation",
    "rollback-readiness",
    "deletion-pending",
    "deleted",
    "model-removal-portability",
)
ARTIFACT_TYPES = (
    "learning-proof",
    "decision-proof",
    "capability-memory-pack",
    "organizational-memory",
    "rule",
    "skill",
    "private-evaluation",
    "adapter",
    "copy",
    "derived-artifact",
    "export-manifest",
    "lifecycle-evidence",
    "other",
)
BOUNDARIES = (
    "local",
    "organization",
    "tenant",
    "approved-provider",
    "external",
    "public",
)
DEPENDENCY_PURPOSES = (
    "standalone-evidence",
    "learning-lineage",
    "capability-use",
    "evaluation-input",
    "memory-derivation",
    "decision-trace",
    "export-portability",
)
DEPENDENCY_CRITICALITIES = ("low", "medium", "high", "critical")
SENSITIVITIES = ("none", "low", "medium", "high", "blocking")
READINESS_STATES = (
    "ready-for-human-review",
    "blocked",
    "insufficient-evidence",
)
EXECUTION_STATES = (
    "not-executed",
    "execution-evidence-present",
    "execution-claimed",
)
PORTABILITY_STATES = ("portable-in-simulation", "blocked", "degraded")
MAX_NESTING_DEPTH = 128
ROLLBACK_REASON_CODES = frozenset(
    {
        "dependency-evidence-complete",
        "dependency-evidence-incomplete",
        "compatibility-confirmed",
        "incompatible-dependent",
        "unresolved-dependent",
        "human-review-required",
        "authorization-not-recorded",
        "execution-not-attempted",
        "execution-evidence-present",
        "execution-evidence-missing",
    }
)
DELETION_REASON_CODES = frozenset(
    {
        "deletion-request-recorded",
        "unresolved-copy",
        "unresolved-dependent",
        "local-deletion-evidence-present",
        "qualified-deleted-evidence",
        "physical-erasure-not-proven",
        "provider-deletion-not-proven",
        "residual-risk-remains",
        "independent-evidence-missing",
    }
)
PORTABILITY_REASON_CODES = frozenset(
    {
        "simulation-only",
        "evidence-readable",
        "degraded-mode-represented",
        "provider-specific-dependency",
        "portability-blocker-visible",
        "unsupported-dependency-quarantined",
        "replacement-model-not-authorized",
        "production-execution-not-attempted",
    }
)

FIXED_FALSE_AUTHORITY_CLAIMS = (
    "release_approved",
    "governance_authority_granted",
    "policy_authority_granted",
    "identity_authority_granted",
    "risk_accepted",
    "deployment_approved",
    "rollback_authorized",
    "rollback_executed",
    "deletion_authorized",
    "deletion_executed",
    "production_execution_allowed",
    "audit_closed",
    "waiver_granted",
    "authority_transferred",
    "capability_pack_installed",
    "capability_pack_executable",
    "learning_proof_sealed",
    "decision_proof_sealed",
)
FORBIDDEN_AUTHORITY_KEYS = (
    *FIXED_FALSE_AUTHORITY_CLAIMS,
    "release_approval",
    "governance_approval",
    "policy_approval",
    "identity_approval",
    "risk_acceptance",
    "deployment_approval",
    "rollback_authorization",
    "rollback_execution",
    "deletion_authorization",
    "deletion_execution",
    "physical_erasure_authority",
    "provider_deletion_authority",
    "replacement_model_authorization",
    "provider_disconnection_authority",
    "production_execution",
    "audit_closure",
    "waiver",
    "authority_transfer",
    "learning_proof_sealing",
    "decision_proof_sealing",
    "installation_authority",
    "execution_authority",
)
FORBIDDEN_AUTHORITY_TOKENS = (
    "release-approved",
    "governance-approved",
    "policy-approved",
    "identity-approved",
    "risk-accepted",
    "deployment-approved",
    "rollback-authorized",
    "rollback-executed",
    "deletion-authorized",
    "deletion-executed",
    "provider-disconnected",
    "replacement-model-authorized",
    "production-executed",
    "audit-closed",
    "waiver-granted",
    "authority-transferred",
    "learning-proof-sealed",
    "decision-proof-sealed",
    "capability-pack-installed",
    "capability-pack-executable",
)

TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "track_c_record_id",
        "record_kind",
        "effective_timestamp",
        "dependency_graph",
        "lineage_evidence",
        "rollback_evidence",
        "deletion_evidence",
        "portability_drill",
        "cross_track_linkage",
        "authority_claims",
        "extensions",
        "non_authoritative_boundary_statement",
    }
)
GRAPH_FIELDS = frozenset(
    {
        "graph_id",
        "graph_version",
        "graph_integrity_digest",
        "artifacts",
        "completeness_declared",
        "completeness_evidence_reference",
        "unresolved_dependencies",
        "graph_snapshot_reference",
    }
)
ARTIFACT_FIELDS = frozenset(
    {
        "artifact_id",
        "artifact_type",
        "artifact_version",
        "artifact_digest",
        "digest_role",
        "upstream_dependencies",
        "downstream_dependents",
        "dependency_purpose",
        "dependency_criticality",
        "processing_boundary",
        "retention_boundary",
        "provider_specific_dependency",
        "rollback_sensitivity",
        "deletion_sensitivity",
    }
)
ARTIFACT_REFERENCE_FIELDS = frozenset(
    {"artifact_id", "artifact_version", "artifact_digest"}
)

IDENTIFIER_PATTERN = re.compile(r"^urn:aaos:[A-Za-z0-9][A-Za-z0-9:._/-]*$")
DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")
VERSION_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/+:-]{0,127}$")
MACHINE_TOKEN_PATTERN = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
TIMESTAMP_PATTERN = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})$"
)

SENSITIVE_KEY_PATTERNS = (
    ("password", re.compile(r"(?:^|_)password(?:_|$)", re.IGNORECASE)),
    ("access_token", re.compile(r"(?:^|_)access[_-]?token(?:_|$)", re.IGNORECASE)),
    ("api_key", re.compile(r"(?:^|_)api[_-]?key(?:_|$)", re.IGNORECASE)),
    ("private_key", re.compile(r"(?:^|_)private[_-]?key(?:_|$)", re.IGNORECASE)),
    ("certificate", re.compile(r"(?:^|_)certificate(?:_|$)", re.IGNORECASE)),
    ("production_credential", re.compile(r"production[_-]?credential", re.IGNORECASE)),
    ("personal_identifier", re.compile(r"personal[_-]?identifier", re.IGNORECASE)),
)
SENSITIVE_VALUE_PATTERNS = (
    ("api_key", re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b")),
    ("access_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{8,}\b")),
    ("access_key", re.compile(r"\bAKIA[A-Z0-9]{12,}\b")),
    ("bearer_token", re.compile(r"Bearer\s+\S+", re.IGNORECASE)),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("certificate", re.compile(r"-----BEGIN CERTIFICATE-----")),
    ("personal_identifier", re.compile(r"\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b")),
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
)


def _redact_finding(value: str) -> str:
    redacted = value
    for _category, pattern in SENSITIVE_VALUE_PATTERNS:
        redacted = pattern.sub("<redacted>", redacted)
    path_components = re.split(r"[:.\[\]]", redacted)
    if not redacted.startswith("sensitive_material_detected:") and any(
        pattern.search(component)
        for component in path_components
        for _category, pattern in SENSITIVE_KEY_PATTERNS
    ):
        label = redacted.split(":", 1)[0]
        return f"{label}:<redacted-path>"
    return redacted


def _sorted_findings(*groups: list[str]) -> list[str]:
    return sorted({_redact_finding(item) for group in groups for item in group})


def _safe_path_component(value: Any) -> str:
    rendered = str(value)
    if any(
        pattern.search(rendered)
        for _category, pattern in (*SENSITIVE_KEY_PATTERNS, *SENSITIVE_VALUE_PATTERNS)
    ):
        return "<redacted-key>"
    return rendered


def _stable_key_component(value: Any) -> tuple[str, Any]:
    if value is None or isinstance(value, (str, int, float, bool)):
        return (type(value).__name__, value)
    return ("invalid", type(value).__name__)


def _duplicates_present(items: list[Any]) -> bool:
    for index, item in enumerate(items):
        for previous in items[:index]:
            try:
                if item == previous:
                    return True
            except Exception:
                return True
    return False


def _container_safety_findings(value: Any) -> list[str]:
    stack: list[tuple[Any, int]] = [(value, 0)]
    seen_container_ids: set[int] = set()
    while stack:
        current, depth = stack.pop()
        if not isinstance(current, (Mapping, list)):
            continue
        if depth > MAX_NESTING_DEPTH:
            return ["maximum_nesting_depth_exceeded"]
        current_id = id(current)
        if current_id in seen_container_ids:
            return ["cyclic_or_shared_container_not_supported"]
        seen_container_ids.add(current_id)
        children = current.values() if isinstance(current, Mapping) else current
        for child in children:
            if isinstance(child, (Mapping, list)):
                stack.append((child, depth + 1))
    return []


def _field_path(path: str, field: str) -> str:
    return f"{path}.{field}" if path else field


def _object_shape(
    value: Any,
    *,
    path: str,
    fields: frozenset[str],
    required: frozenset[str] | None = None,
    allow_additional: bool = False,
) -> list[str]:
    if not isinstance(value, Mapping):
        return [f"object_required:{path}"]
    findings: list[str] = []
    for field in sorted((required or fields) - set(value)):
        findings.append(f"required_field_missing:{_field_path(path, field)}")
    if not allow_additional:
        for field in sorted(set(value) - fields, key=str):
            findings.append(
                f"unexpected_field:{_field_path(path, _safe_path_component(field))}"
            )
    return findings


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and 12 <= len(value) <= 256
        and bool(IDENTIFIER_PATTERN.fullmatch(value))
    )


def _valid_reference(value: Any) -> bool:
    return (
        isinstance(value, str)
        and 12 <= len(value) <= 512
        and bool(IDENTIFIER_PATTERN.fullmatch(value))
    )


def _valid_digest(value: Any) -> bool:
    return isinstance(value, str) and bool(DIGEST_PATTERN.fullmatch(value))


def _valid_version(value: Any) -> bool:
    return isinstance(value, str) and bool(VERSION_PATTERN.fullmatch(value))


def _valid_machine_token(value: Any) -> bool:
    return isinstance(value, str) and bool(MACHINE_TOKEN_PATTERN.fullmatch(value))


def _valid_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not TIMESTAMP_PATTERN.fullmatch(value):
        return False
    if value.endswith("-00:00"):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _scalar_finding(valid: bool, label: str, path: str) -> list[str]:
    return [] if valid else [f"{label}:{path}"]


def _artifact_reference_findings(value: Any, path: str) -> list[str]:
    findings = _object_shape(
        value,
        path=path,
        fields=ARTIFACT_REFERENCE_FIELDS,
    )
    if not isinstance(value, Mapping):
        return findings
    findings.extend(_scalar_finding(_valid_identifier(value.get("artifact_id")), "invalid_identifier", f"{path}.artifact_id"))
    findings.extend(_scalar_finding(_valid_version(value.get("artifact_version")), "invalid_version", f"{path}.artifact_version"))
    findings.extend(_scalar_finding(_valid_digest(value.get("artifact_digest")), "invalid_digest", f"{path}.artifact_digest"))
    return findings


def _reference_list_findings(value: Any, path: str) -> list[str]:
    if not isinstance(value, list):
        return [f"array_required:{path}"]
    findings: list[str] = []
    seen: set[tuple[Any, Any, Any]] = set()
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        findings.extend(_artifact_reference_findings(item, item_path))
        if isinstance(item, Mapping):
            key = tuple(
                _stable_key_component(item.get(field))
                for field in ("artifact_id", "artifact_version", "artifact_digest")
            )
            if key in seen:
                findings.append(f"duplicate_artifact_reference:{item_path}")
            seen.add(key)
    return findings


def _graph_structure_findings(graph: Any) -> list[str]:
    findings = _object_shape(graph, path="dependency_graph", fields=GRAPH_FIELDS)
    if not isinstance(graph, Mapping):
        return findings
    findings.extend(_scalar_finding(_valid_identifier(graph.get("graph_id")), "invalid_identifier", "dependency_graph.graph_id"))
    findings.extend(_scalar_finding(_valid_version(graph.get("graph_version")), "invalid_version", "dependency_graph.graph_version"))
    findings.extend(_scalar_finding(_valid_digest(graph.get("graph_integrity_digest")), "invalid_digest", "dependency_graph.graph_integrity_digest"))
    findings.extend(_scalar_finding(isinstance(graph.get("completeness_declared"), bool), "boolean_required", "dependency_graph.completeness_declared"))
    completeness_ref = graph.get("completeness_evidence_reference")
    findings.extend(_scalar_finding(completeness_ref is None or _valid_reference(completeness_ref), "invalid_reference", "dependency_graph.completeness_evidence_reference"))
    findings.extend(_scalar_finding(_valid_reference(graph.get("graph_snapshot_reference")), "invalid_reference", "dependency_graph.graph_snapshot_reference"))

    artifacts = graph.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        findings.append("nonempty_array_required:dependency_graph.artifacts")
    else:
        seen_ids: set[tuple[str, Any]] = set()
        for index, artifact in enumerate(artifacts):
            path = f"dependency_graph.artifacts[{index}]"
            findings.extend(_object_shape(artifact, path=path, fields=ARTIFACT_FIELDS))
            if not isinstance(artifact, Mapping):
                continue
            artifact_id = artifact.get("artifact_id")
            findings.extend(_scalar_finding(_valid_identifier(artifact_id), "invalid_identifier", f"{path}.artifact_id"))
            stable_artifact_id = _stable_key_component(artifact_id)
            if stable_artifact_id in seen_ids:
                findings.append(f"duplicate_artifact_id:{path}.artifact_id")
            seen_ids.add(stable_artifact_id)
            findings.extend(_scalar_finding(artifact.get("artifact_type") in ARTIFACT_TYPES, "unknown_artifact_type", f"{path}.artifact_type"))
            findings.extend(_scalar_finding(_valid_version(artifact.get("artifact_version")), "invalid_version", f"{path}.artifact_version"))
            findings.extend(_scalar_finding(_valid_digest(artifact.get("artifact_digest")), "invalid_digest", f"{path}.artifact_digest"))
            findings.extend(_scalar_finding(artifact.get("digest_role") in ("track-c-evidence-record", "artifact-content", "export-manifest"), "unknown_digest_role", f"{path}.digest_role"))
            findings.extend(_reference_list_findings(artifact.get("upstream_dependencies"), f"{path}.upstream_dependencies"))
            findings.extend(_reference_list_findings(artifact.get("downstream_dependents"), f"{path}.downstream_dependents"))
            findings.extend(_scalar_finding(artifact.get("dependency_purpose") in DEPENDENCY_PURPOSES, "unknown_dependency_purpose", f"{path}.dependency_purpose"))
            findings.extend(_scalar_finding(artifact.get("dependency_criticality") in DEPENDENCY_CRITICALITIES, "unknown_dependency_criticality", f"{path}.dependency_criticality"))
            findings.extend(_scalar_finding(artifact.get("processing_boundary") in BOUNDARIES, "unknown_processing_boundary", f"{path}.processing_boundary"))
            findings.extend(_scalar_finding(artifact.get("retention_boundary") in BOUNDARIES, "unknown_retention_boundary", f"{path}.retention_boundary"))
            findings.extend(_scalar_finding(isinstance(artifact.get("provider_specific_dependency"), bool), "boolean_required", f"{path}.provider_specific_dependency"))
            findings.extend(_scalar_finding(artifact.get("rollback_sensitivity") in SENSITIVITIES, "unknown_rollback_sensitivity", f"{path}.rollback_sensitivity"))
            findings.extend(_scalar_finding(artifact.get("deletion_sensitivity") in SENSITIVITIES, "unknown_deletion_sensitivity", f"{path}.deletion_sensitivity"))

    unresolved = graph.get("unresolved_dependencies")
    unresolved_fields = frozenset({"source_artifact_id", "related_artifact_id", "direction", "reason_code"})
    if not isinstance(unresolved, list):
        findings.append("array_required:dependency_graph.unresolved_dependencies")
    else:
        seen_unresolved: set[tuple[Any, Any, Any, Any]] = set()
        for index, item in enumerate(unresolved):
            path = f"dependency_graph.unresolved_dependencies[{index}]"
            findings.extend(_object_shape(item, path=path, fields=unresolved_fields))
            if not isinstance(item, Mapping):
                continue
            findings.extend(_scalar_finding(_valid_identifier(item.get("source_artifact_id")), "invalid_identifier", f"{path}.source_artifact_id"))
            findings.extend(_scalar_finding(_valid_identifier(item.get("related_artifact_id")), "invalid_identifier", f"{path}.related_artifact_id"))
            findings.extend(_scalar_finding(item.get("direction") in ("upstream", "downstream"), "unknown_dependency_direction", f"{path}.direction"))
            findings.extend(_scalar_finding(_valid_machine_token(item.get("reason_code")), "invalid_reason_code", f"{path}.reason_code"))
            key = tuple(
                _stable_key_component(item.get(field))
                for field in (
                    "source_artifact_id",
                    "related_artifact_id",
                    "direction",
                    "reason_code",
                )
            )
            if key in seen_unresolved:
                findings.append(f"duplicate_unresolved_dependency:{path}")
            seen_unresolved.add(key)
    return findings


def _binding_key(value: Mapping[str, Any]) -> tuple[Any, Any, Any]:
    return (
        _stable_key_component(value.get("artifact_id")),
        _stable_key_component(value.get("artifact_version")),
        _stable_key_component(value.get("artifact_digest")),
    )


def _graph_semantic_findings(graph: Mapping[str, Any]) -> list[str]:
    artifacts = graph.get("artifacts")
    if not isinstance(artifacts, list):
        return ["dependency_graph_artifacts_unavailable"]
    artifact_by_id = {
        artifact.get("artifact_id"): artifact
        for artifact in artifacts
        if isinstance(artifact, Mapping) and _valid_identifier(artifact.get("artifact_id"))
    }
    unresolved = graph.get("unresolved_dependencies")
    unresolved_pairs = {
        (
            item.get("source_artifact_id"),
            item.get("related_artifact_id"),
            item.get("direction"),
        )
        for item in unresolved or []
        if isinstance(item, Mapping)
    }
    findings: list[str] = []

    for source_index, source in enumerate(artifacts):
        if not isinstance(source, Mapping):
            continue
        source_id = source.get("artifact_id")
        source_ref = _binding_key(source)
        if source.get("dependency_purpose") == "standalone-evidence" and (
            source.get("upstream_dependencies")
            or source.get("downstream_dependents")
        ):
            findings.append(
                "standalone_evidence_artifact_has_declared_dependency:"
                f"dependency_graph.artifacts[{source_index}]"
            )
        for direction, reciprocal in (
            ("upstream", "downstream_dependents"),
            ("downstream", "upstream_dependencies"),
        ):
            list_field = "upstream_dependencies" if direction == "upstream" else "downstream_dependents"
            bindings = source.get(list_field)
            if not isinstance(bindings, list):
                continue
            for binding_index, binding in enumerate(bindings):
                if not isinstance(binding, Mapping):
                    continue
                path = f"dependency_graph.artifacts[{source_index}].{list_field}[{binding_index}]"
                target_id = binding.get("artifact_id")
                target = artifact_by_id.get(target_id)
                if target is None:
                    findings.append(f"unresolved_graph_binding:{path}")
                    if (source_id, target_id, direction) not in unresolved_pairs:
                        findings.append(f"unresolved_dependency_declaration_missing:{path}")
                    continue
                if _binding_key(target) != _binding_key(binding):
                    findings.append(f"inconsistent_dependency_version_or_digest:{path}")
                reverse_values = target.get(reciprocal)
                reverse_keys = {
                    _binding_key(item)
                    for item in reverse_values or []
                    if isinstance(item, Mapping)
                }
                if source_ref not in reverse_keys:
                    findings.append(f"inconsistent_{direction}_binding:{path}")
                    if (source_id, target_id, direction) not in unresolved_pairs:
                        findings.append(f"unresolved_dependency_declaration_missing:{path}")

    for index, item in enumerate(unresolved or []):
        if not isinstance(item, Mapping):
            continue
        if item.get("source_artifact_id") not in artifact_by_id:
            findings.append(
                "unresolved_dependency_source_not_in_graph:"
                f"dependency_graph.unresolved_dependencies[{index}].source_artifact_id"
            )

    completeness = graph.get("completeness_declared")
    completeness_ref = graph.get("completeness_evidence_reference")
    if completeness is True:
        if not _valid_reference(completeness_ref):
            findings.append("false_dependency_graph_completeness:evidence_missing")
        if unresolved:
            findings.append("false_dependency_graph_completeness:unresolved_dependencies_present")
    elif completeness is False and not unresolved:
        findings.append("incomplete_graph_requires_unresolved_dependency")
    return findings


def _artifact_map(graph: Mapping[str, Any]) -> dict[Any, Mapping[str, Any]]:
    return {
        item.get("artifact_id"): item
        for item in graph.get("artifacts", [])
        if isinstance(item, Mapping) and _valid_identifier(item.get("artifact_id"))
    }


def _reference_matches_artifact(reference: Any, artifact: Mapping[str, Any] | None) -> bool:
    return (
        isinstance(reference, Mapping)
        and artifact is not None
        and _binding_key(reference) == _binding_key(artifact)
    )


def _lineage_structure_findings(value: Any) -> list[str]:
    fields = frozenset(
        {
            "action",
            "affected_artifact",
            "current_version",
            "replacement_reference",
            "reason",
            "effective_timestamp",
            "known_downstream_dependents",
            "unresolved_dependents",
            "archival_evidence_state",
            "archival_evidence_reference",
            "revocation_evidence_reference",
            "evidence_digests",
            "downstream_removal_claimed",
        }
    )
    findings = _object_shape(value, path="lineage_evidence", fields=fields)
    if not isinstance(value, Mapping):
        return findings
    findings.extend(_scalar_finding(value.get("action") in ("supersession", "revocation"), "unknown_lineage_action", "lineage_evidence.action"))
    findings.extend(_artifact_reference_findings(value.get("affected_artifact"), "lineage_evidence.affected_artifact"))
    findings.extend(_scalar_finding(_valid_version(value.get("current_version")), "invalid_version", "lineage_evidence.current_version"))
    replacement = value.get("replacement_reference")
    if replacement is not None:
        findings.extend(_artifact_reference_findings(replacement, "lineage_evidence.replacement_reference"))
    findings.extend(_scalar_finding(_valid_machine_token(value.get("reason")), "invalid_reason", "lineage_evidence.reason"))
    findings.extend(_scalar_finding(_valid_timestamp(value.get("effective_timestamp")), "invalid_timestamp", "lineage_evidence.effective_timestamp"))
    findings.extend(_reference_list_findings(value.get("known_downstream_dependents"), "lineage_evidence.known_downstream_dependents"))
    findings.extend(_reference_list_findings(value.get("unresolved_dependents"), "lineage_evidence.unresolved_dependents"))
    findings.extend(_scalar_finding(value.get("archival_evidence_state") in ("retained", "pending", "not-retained", "unknown"), "unknown_archival_evidence_state", "lineage_evidence.archival_evidence_state"))
    for field in ("archival_evidence_reference", "revocation_evidence_reference"):
        field_value = value.get(field)
        findings.extend(_scalar_finding(field_value is None or _valid_reference(field_value), "invalid_reference", f"lineage_evidence.{field}"))
    digests = value.get("evidence_digests")
    if not isinstance(digests, list) or not digests:
        findings.append("nonempty_array_required:lineage_evidence.evidence_digests")
    else:
        if _duplicates_present(digests):
            findings.append("duplicate_digest:lineage_evidence.evidence_digests")
        for index, digest in enumerate(digests):
            findings.extend(_scalar_finding(_valid_digest(digest), "invalid_digest", f"lineage_evidence.evidence_digests[{index}]"))
    findings.extend(_scalar_finding(isinstance(value.get("downstream_removal_claimed"), bool), "boolean_required", "lineage_evidence.downstream_removal_claimed"))
    return findings


def _lineage_semantic_findings(
    value: Mapping[str, Any],
    *,
    record_kind: Any,
    graph: Mapping[str, Any],
    effective_timestamp: Any,
) -> list[str]:
    findings: list[str] = []
    action = value.get("action")
    if action != record_kind:
        findings.append("lineage_action_record_kind_mismatch")
    affected = value.get("affected_artifact")
    artifact = _artifact_map(graph).get(affected.get("artifact_id") if isinstance(affected, Mapping) else None)
    if not _reference_matches_artifact(affected, artifact):
        findings.append("lineage_affected_artifact_graph_binding_mismatch")
    if isinstance(affected, Mapping) and value.get("current_version") != affected.get("artifact_version"):
        findings.append("lineage_current_version_mismatch")
    if value.get("effective_timestamp") != effective_timestamp:
        findings.append("lineage_effective_timestamp_mismatch")

    expected_downstream = {
        _binding_key(item)
        for item in (artifact or {}).get("downstream_dependents", [])
        if isinstance(item, Mapping)
    }
    declared_downstream = {
        _binding_key(item)
        for item in value.get("known_downstream_dependents", [])
        if isinstance(item, Mapping)
    }
    if expected_downstream != declared_downstream:
        findings.append("known_downstream_dependents_do_not_match_graph")

    affected_id = affected.get("artifact_id") if isinstance(affected, Mapping) else None
    expected_unresolved_ids = {
        item.get("related_artifact_id")
        for item in graph.get("unresolved_dependencies", [])
        if isinstance(item, Mapping)
        and item.get("source_artifact_id") == affected_id
        and item.get("direction") == "downstream"
    }
    declared_unresolved_ids = {
        item.get("artifact_id")
        for item in value.get("unresolved_dependents", [])
        if isinstance(item, Mapping)
    }
    if expected_unresolved_ids != declared_unresolved_ids:
        findings.append("unresolved_lineage_dependents_do_not_match_graph")

    if action == "supersession" and value.get("replacement_reference") is None:
        findings.append("supersession_replacement_reference_missing")
    if (
        action == "supersession"
        and isinstance(value.get("replacement_reference"), Mapping)
        and isinstance(affected, Mapping)
        and _binding_key(value["replacement_reference"]) == _binding_key(affected)
    ):
        findings.append("supersession_replacement_matches_affected_artifact")
    if action == "revocation":
        if not _valid_reference(value.get("revocation_evidence_reference")):
            findings.append("revocation_evidence_reference_missing")
        if not _valid_machine_token(value.get("reason")):
            findings.append("revocation_reason_missing")
    replacement = value.get("replacement_reference")
    artifact_role_identifiers = {
        item.get("artifact_id")
        for item in (affected, replacement)
        if isinstance(item, Mapping)
    }
    archival_reference = value.get("archival_evidence_reference")
    revocation_reference = value.get("revocation_evidence_reference")
    for field, reference in (
        ("archival_evidence_reference", archival_reference),
        ("revocation_evidence_reference", revocation_reference),
    ):
        if reference is not None and reference in artifact_role_identifiers:
            findings.append(f"lineage_evidence_reference_role_conflation:{field}")
    if (
        archival_reference is not None
        and archival_reference == revocation_reference
    ):
        findings.append("lineage_archival_and_revocation_evidence_must_differ")
    if value.get("archival_evidence_state") == "retained" and not _valid_reference(value.get("archival_evidence_reference")):
        findings.append("retained_archival_evidence_reference_missing")
    if value.get("downstream_removal_claimed") is not False:
        findings.append("lineage_cannot_claim_downstream_removal")
    return findings


def _rollback_structure_findings(value: Any) -> list[str]:
    fields = frozenset(
        {
            "rollback_request_id",
            "current_artifact",
            "target_artifact",
            "dependency_graph_snapshot_reference",
            "affected_dependents",
            "incompatible_dependents",
            "unresolved_dependents",
            "compatibility_assessment",
            "required_human_review",
            "authorization_reference",
            "execution_evidence_reference",
            "readiness_state",
            "execution_state",
            "completion_claim",
            "reason_codes",
        }
    )
    findings = _object_shape(value, path="rollback_evidence", fields=fields)
    if not isinstance(value, Mapping):
        return findings
    findings.extend(_scalar_finding(_valid_identifier(value.get("rollback_request_id")), "invalid_identifier", "rollback_evidence.rollback_request_id"))
    findings.extend(_artifact_reference_findings(value.get("current_artifact"), "rollback_evidence.current_artifact"))
    findings.extend(_artifact_reference_findings(value.get("target_artifact"), "rollback_evidence.target_artifact"))
    findings.extend(_scalar_finding(_valid_reference(value.get("dependency_graph_snapshot_reference")), "invalid_reference", "rollback_evidence.dependency_graph_snapshot_reference"))
    for field in ("affected_dependents", "incompatible_dependents", "unresolved_dependents"):
        findings.extend(_reference_list_findings(value.get(field), f"rollback_evidence.{field}"))
    findings.extend(_scalar_finding(value.get("compatibility_assessment") in ("compatible", "incompatible", "unknown"), "unknown_compatibility_assessment", "rollback_evidence.compatibility_assessment"))
    findings.extend(_scalar_finding(isinstance(value.get("required_human_review"), bool), "boolean_required", "rollback_evidence.required_human_review"))
    for field in ("authorization_reference", "execution_evidence_reference"):
        field_value = value.get(field)
        findings.extend(_scalar_finding(field_value is None or _valid_reference(field_value), "invalid_reference", f"rollback_evidence.{field}"))
    findings.extend(_scalar_finding(value.get("readiness_state") in READINESS_STATES, "unknown_readiness_state", "rollback_evidence.readiness_state"))
    findings.extend(_scalar_finding(value.get("execution_state") in EXECUTION_STATES, "unknown_execution_state", "rollback_evidence.execution_state"))
    findings.extend(_scalar_finding(isinstance(value.get("completion_claim"), bool), "boolean_required", "rollback_evidence.completion_claim"))
    reason_codes = value.get("reason_codes")
    if not isinstance(reason_codes, list) or not reason_codes:
        findings.append("nonempty_array_required:rollback_evidence.reason_codes")
    elif (
        _duplicates_present(reason_codes)
        or not all(
            isinstance(item, str) and item in ROLLBACK_REASON_CODES
            for item in reason_codes
        )
    ):
        findings.append("invalid_reason_codes:rollback_evidence.reason_codes")
    return findings


def _rollback_semantic_findings(
    value: Mapping[str, Any],
    *,
    graph: Mapping[str, Any],
    graph_complete: bool,
) -> list[str]:
    findings: list[str] = []
    current = value.get("current_artifact")
    current_artifact = _artifact_map(graph).get(current.get("artifact_id") if isinstance(current, Mapping) else None)
    if not _reference_matches_artifact(current, current_artifact):
        findings.append("rollback_current_artifact_graph_binding_mismatch")
    target = value.get("target_artifact")
    target_artifact = _artifact_map(graph).get(
        target.get("artifact_id") if isinstance(target, Mapping) else None
    )
    if not _reference_matches_artifact(target, target_artifact):
        findings.append("rollback_target_artifact_graph_binding_mismatch")
    if (
        isinstance(current_artifact, Mapping)
        and isinstance(target_artifact, Mapping)
        and current_artifact.get("artifact_type")
        != target_artifact.get("artifact_type")
    ):
        findings.append("rollback_current_target_artifact_type_mismatch")
    if (
        isinstance(current, Mapping)
        and isinstance(target, Mapping)
        and _binding_key(current) == _binding_key(target)
    ):
        findings.append("rollback_target_matches_current_artifact")
    rollback_request_id = value.get("rollback_request_id")
    authorization_reference = value.get("authorization_reference")
    execution_evidence_reference = value.get("execution_evidence_reference")
    artifact_role_identifiers = {
        item.get("artifact_id")
        for item in (current, target)
        if isinstance(item, Mapping)
    }
    for field, reference in (
        ("authorization_reference", authorization_reference),
        ("execution_evidence_reference", execution_evidence_reference),
    ):
        if reference == rollback_request_id or reference in artifact_role_identifiers:
            findings.append(f"rollback_reference_role_conflation:{field}")
    if (
        authorization_reference is not None
        and authorization_reference == execution_evidence_reference
    ):
        findings.append("rollback_authorization_and_execution_evidence_must_differ")
    if value.get("dependency_graph_snapshot_reference") != graph.get("graph_snapshot_reference"):
        findings.append("rollback_graph_snapshot_reference_mismatch")
    expected_known_affected = {
        _binding_key(item)
        for item in (current_artifact or {}).get("downstream_dependents", [])
        if isinstance(item, Mapping)
    }
    declared_affected = {
        _binding_key(item)
        for item in value.get("affected_dependents", [])
        if isinstance(item, Mapping)
    }
    incompatible = {
        _binding_key(item)
        for item in value.get("incompatible_dependents", [])
        if isinstance(item, Mapping)
    }
    unresolved = {
        _binding_key(item)
        for item in value.get("unresolved_dependents", [])
        if isinstance(item, Mapping)
    }
    current_id = current.get("artifact_id") if isinstance(current, Mapping) else None
    expected_unresolved_ids = {
        item.get("related_artifact_id")
        for item in graph.get("unresolved_dependencies", [])
        if isinstance(item, Mapping)
        and item.get("source_artifact_id") == current_id
        and item.get("direction") == "downstream"
    }
    declared_unresolved_ids = {
        item.get("artifact_id")
        for item in value.get("unresolved_dependents", [])
        if isinstance(item, Mapping)
    }
    if expected_unresolved_ids != declared_unresolved_ids:
        findings.append("rollback_unresolved_dependents_do_not_match_graph")
    if expected_known_affected | unresolved != declared_affected:
        findings.append("rollback_affected_dependents_do_not_match_graph")
    if not incompatible.issubset(declared_affected):
        findings.append("rollback_incompatible_dependent_not_affected")
    if not unresolved.issubset(declared_affected):
        findings.append("rollback_unresolved_dependent_not_affected")
    if value.get("required_human_review") is not True:
        findings.append("rollback_requires_human_review")

    readiness = value.get("readiness_state")
    assessment = value.get("compatibility_assessment")
    if incompatible and assessment != "incompatible":
        findings.append("rollback_incompatible_dependents_conflict_with_assessment")
    if not incompatible and assessment == "incompatible":
        findings.append("rollback_incompatible_assessment_without_dependent")
    blockers = bool(incompatible or unresolved or not graph_complete or assessment != "compatible")
    if readiness == "ready-for-human-review":
        if incompatible:
            findings.append("rollback_readiness_with_incompatible_dependents")
        if unresolved:
            findings.append("rollback_readiness_with_unresolved_dependents")
        if not graph_complete:
            findings.append("rollback_readiness_without_complete_dependency_evidence")
        if assessment != "compatible":
            findings.append("rollback_readiness_without_compatible_assessment")
    elif readiness == "blocked" and not blockers:
        findings.append("rollback_blocked_without_blocker")
    elif readiness == "insufficient-evidence" and graph_complete and not unresolved and assessment != "unknown":
        findings.append("rollback_insufficient_evidence_without_gap")

    execution_state = value.get("execution_state")
    execution_ref = value.get("execution_evidence_reference")
    completion = value.get("completion_claim")
    if execution_state == "not-executed":
        if execution_ref is not None:
            findings.append("rollback_not_executed_with_execution_evidence")
        if completion is not False:
            findings.append("rollback_completion_claim_without_execution")
    elif execution_state == "execution-claimed" and not _valid_reference(execution_ref):
        findings.append("rollback_execution_claim_without_execution_evidence")
    elif execution_state == "execution-evidence-present" and not _valid_reference(execution_ref):
        findings.append("rollback_execution_evidence_reference_missing")
    if completion is True:
        if execution_state != "execution-evidence-present" or not _valid_reference(execution_ref):
            findings.append("rollback_completion_claim_without_execution_evidence")
        if not _valid_reference(value.get("authorization_reference")):
            findings.append("rollback_completion_claim_without_authorization_reference")
        if incompatible or unresolved:
            findings.append("rollback_completion_claim_with_blocked_dependents")

    reason_codes = set(value.get("reason_codes", []))
    required_reason_codes = {
        "dependency-evidence-complete"
        if graph_complete
        else "dependency-evidence-incomplete",
    }
    if assessment == "compatible":
        required_reason_codes.add("compatibility-confirmed")
    if incompatible:
        required_reason_codes.add("incompatible-dependent")
    if unresolved:
        required_reason_codes.add("unresolved-dependent")
    if value.get("required_human_review") is True:
        required_reason_codes.add("human-review-required")
    if value.get("authorization_reference") is None:
        required_reason_codes.add("authorization-not-recorded")
    required_reason_codes.add(
        {
            "not-executed": "execution-not-attempted",
            "execution-evidence-present": "execution-evidence-present",
            "execution-claimed": (
                "execution-evidence-present"
                if _valid_reference(execution_ref)
                else "execution-evidence-missing"
            ),
        }.get(execution_state, "execution-evidence-missing")
    )
    for reason_code in sorted(required_reason_codes - reason_codes):
        findings.append(f"rollback_required_reason_code_missing:{reason_code}")
    for reason_code in sorted(reason_codes - required_reason_codes):
        findings.append(f"rollback_reason_code_not_applicable:{reason_code}")
    return findings


def _dependent_evidence_findings(value: Any, path: str) -> list[str]:
    fields = frozenset({"artifact_id", "artifact_version", "artifact_digest", "evidence_state"})
    findings = _object_shape(value, path=path, fields=fields)
    if not isinstance(value, Mapping):
        return findings
    findings.extend(_scalar_finding(_valid_identifier(value.get("artifact_id")), "invalid_identifier", f"{path}.artifact_id"))
    findings.extend(_scalar_finding(_valid_version(value.get("artifact_version")), "invalid_version", f"{path}.artifact_version"))
    findings.extend(_scalar_finding(_valid_digest(value.get("artifact_digest")), "invalid_digest", f"{path}.artifact_digest"))
    findings.extend(_scalar_finding(value.get("evidence_state") in ("known", "retained", "deletion-pending", "qualified-deleted", "unknown"), "unknown_evidence_state", f"{path}.evidence_state"))
    return findings


def _deletion_structure_findings(value: Any) -> list[str]:
    fields = frozenset(
        {
            "deletion_request_id",
            "target_artifact",
            "deletion_scope",
            "known_copies",
            "derived_artifacts",
            "downstream_dependents",
            "unresolved_dependencies",
            "retention_boundary",
            "authorization_reference",
            "local_deletion_evidence_reference",
            "independent_deletion_evidence",
            "residual_risk_statement",
            "evidence_qualification",
            "completion_status",
            "reason_codes",
            "physical_erasure_claimed",
            "provider_deletion_claimed",
            "backup_deletion_claimed",
            "cache_deletion_claimed",
            "training_data_removal_claimed",
            "model_unlearning_claimed",
            "all_derived_artifacts_deleted_claimed",
            "all_external_systems_deleted_claimed",
        }
    )
    findings = _object_shape(value, path="deletion_evidence", fields=fields)
    if not isinstance(value, Mapping):
        return findings
    findings.extend(_scalar_finding(_valid_identifier(value.get("deletion_request_id")), "invalid_identifier", "deletion_evidence.deletion_request_id"))
    findings.extend(_artifact_reference_findings(value.get("target_artifact"), "deletion_evidence.target_artifact"))
    scope = value.get("deletion_scope")
    valid_scopes = {"local-record", "known-copy", "derived-artifact", "provider-copy", "backup", "cache", "training-data", "model-weights", "external-system"}
    if not isinstance(scope, list) or not scope:
        findings.append("nonempty_array_required:deletion_evidence.deletion_scope")
    elif (
        _duplicates_present(scope)
        or not all(isinstance(item, str) and item in valid_scopes for item in scope)
    ):
        findings.append("invalid_deletion_scope")
    for field in ("known_copies", "derived_artifacts", "downstream_dependents"):
        items = value.get(field)
        if not isinstance(items, list):
            findings.append(f"array_required:deletion_evidence.{field}")
            continue
        if _duplicates_present(items):
            findings.append(f"duplicate_dependent_evidence:deletion_evidence.{field}")
        for index, item in enumerate(items):
            findings.extend(_dependent_evidence_findings(item, f"deletion_evidence.{field}[{index}]"))
    findings.extend(_reference_list_findings(value.get("unresolved_dependencies"), "deletion_evidence.unresolved_dependencies"))
    findings.extend(_scalar_finding(value.get("retention_boundary") in BOUNDARIES, "unknown_retention_boundary", "deletion_evidence.retention_boundary"))
    for field in ("authorization_reference", "local_deletion_evidence_reference"):
        field_value = value.get(field)
        findings.extend(_scalar_finding(field_value is None or _valid_reference(field_value), "invalid_reference", f"deletion_evidence.{field}"))
    independent_fields = frozenset({"evidence_type", "evidence_reference", "evidence_digest", "qualification"})
    independent = value.get("independent_deletion_evidence")
    valid_evidence_types = ("local-deletion", "physical-erasure", "provider-deletion", "backup-deletion", "cache-deletion", "training-data-removal", "model-unlearning", "derived-artifact-deletion", "external-system-deletion")
    if not isinstance(independent, list):
        findings.append("array_required:deletion_evidence.independent_deletion_evidence")
    else:
        if _duplicates_present(independent):
            findings.append("duplicate_independent_deletion_evidence")
        for index, item in enumerate(independent):
            path = f"deletion_evidence.independent_deletion_evidence[{index}]"
            findings.extend(_object_shape(item, path=path, fields=independent_fields))
            if not isinstance(item, Mapping):
                continue
            findings.extend(_scalar_finding(item.get("evidence_type") in valid_evidence_types, "unknown_deletion_evidence_type", f"{path}.evidence_type"))
            findings.extend(_scalar_finding(_valid_reference(item.get("evidence_reference")), "invalid_reference", f"{path}.evidence_reference"))
            findings.extend(_scalar_finding(_valid_digest(item.get("evidence_digest")), "invalid_digest", f"{path}.evidence_digest"))
            findings.extend(_scalar_finding(item.get("qualification") in ("locally-observed", "provider-attested", "independently-verified"), "unknown_evidence_qualification", f"{path}.qualification"))
    findings.extend(_scalar_finding(isinstance(value.get("residual_risk_statement"), str) and 1 <= len(value.get("residual_risk_statement")) <= 512, "bounded_nonempty_string_required", "deletion_evidence.residual_risk_statement"))
    findings.extend(_scalar_finding(value.get("evidence_qualification") in ("request-only", "pending-unresolved", "qualified-local-deletion", "qualified-external-deletion"), "unknown_evidence_qualification", "deletion_evidence.evidence_qualification"))
    findings.extend(_scalar_finding(value.get("completion_status") in ("pending", "incomplete", "qualified-deleted", "claimed-complete"), "unknown_deletion_completion_status", "deletion_evidence.completion_status"))
    reason_codes = value.get("reason_codes")
    if not isinstance(reason_codes, list) or not reason_codes:
        findings.append("nonempty_array_required:deletion_evidence.reason_codes")
    elif (
        _duplicates_present(reason_codes)
        or not all(
            isinstance(item, str) and item in DELETION_REASON_CODES
            for item in reason_codes
        )
    ):
        findings.append("invalid_reason_codes:deletion_evidence.reason_codes")
    for field in sorted(fields):
        if field.endswith("_claimed"):
            findings.extend(_scalar_finding(isinstance(value.get(field), bool), "boolean_required", f"deletion_evidence.{field}"))
    return findings


def _deletion_semantic_findings(
    value: Mapping[str, Any],
    *,
    record_kind: Any,
    graph: Mapping[str, Any],
    graph_complete: bool,
) -> list[str]:
    findings: list[str] = []
    target = value.get("target_artifact")
    artifact = _artifact_map(graph).get(target.get("artifact_id") if isinstance(target, Mapping) else None)
    if not _reference_matches_artifact(target, artifact):
        findings.append("deletion_target_graph_binding_mismatch")
    if artifact is not None and value.get("retention_boundary") != artifact.get(
        "retention_boundary"
    ):
        findings.append("deletion_retention_boundary_graph_mismatch")

    graph_dependents = {
        _binding_key(item)
        for item in (artifact or {}).get("downstream_dependents", [])
        if isinstance(item, Mapping)
    }
    derived_dependents = {
        _binding_key(item)
        for item in value.get("derived_artifacts", [])
        if isinstance(item, Mapping)
    }
    other_dependents = {
        _binding_key(item)
        for item in value.get("downstream_dependents", [])
        if isinstance(item, Mapping)
    }
    known_copy_dependents = {
        _binding_key(item)
        for item in value.get("known_copies", [])
        if isinstance(item, Mapping)
    }
    if (
        derived_dependents & other_dependents
        or known_copy_dependents & derived_dependents
        or known_copy_dependents & other_dependents
    ):
        findings.append("deletion_dependent_declared_in_multiple_categories")
    if graph_dependents != (
        derived_dependents | other_dependents | known_copy_dependents
    ):
        findings.append("deletion_dependents_do_not_match_graph")
    graph_artifacts_by_binding = {
        _binding_key(item): item
        for item in graph.get("artifacts", [])
        if isinstance(item, Mapping)
    }
    if any(
        graph_artifacts_by_binding.get(binding, {}).get("artifact_type") != "copy"
        for binding in known_copy_dependents
    ):
        findings.append("deletion_known_copy_artifact_type_mismatch")
    if any(
        graph_artifacts_by_binding.get(binding, {}).get("artifact_type")
        == "copy"
        for binding in derived_dependents | other_dependents
    ):
        findings.append("deletion_copy_artifact_declared_outside_known_copies")

    target_id = target.get("artifact_id") if isinstance(target, Mapping) else None
    graph_unresolved_ids = {
        item.get("related_artifact_id")
        for item in graph.get("unresolved_dependencies", [])
        if isinstance(item, Mapping)
        and item.get("source_artifact_id") == target_id
        and item.get("direction") == "downstream"
    }
    unresolved = value.get("unresolved_dependencies") or []
    declared_unresolved_ids = {
        item.get("artifact_id")
        for item in unresolved
        if isinstance(item, Mapping)
    }
    if not graph_unresolved_ids.issubset(declared_unresolved_ids):
        findings.append("deletion_graph_unresolved_dependents_omitted")
    unresolved_states = {
        "unknown",
        "deletion-pending",
    }
    copy_unresolved = any(
        isinstance(item, Mapping) and item.get("evidence_state") in unresolved_states
        for item in value.get("known_copies", [])
    )
    dependent_unresolved = any(
        isinstance(item, Mapping) and item.get("evidence_state") in unresolved_states
        for field in ("derived_artifacts", "downstream_dependents")
        for item in value.get(field, [])
    )
    known_unresolved = copy_unresolved or dependent_unresolved
    completion = value.get("completion_status")
    qualification = value.get("evidence_qualification")
    scope = set(value.get("deletion_scope", []))
    if record_kind == "deletion-pending":
        if completion not in {"pending", "incomplete"}:
            findings.append("deletion_pending_record_claims_completion")
        if qualification not in {"request-only", "pending-unresolved"}:
            findings.append("deletion_pending_record_has_completed_qualification")
        if qualification == "request-only" and (
            value.get("local_deletion_evidence_reference") is not None
            or value.get("independent_deletion_evidence")
        ):
            findings.append("request_only_deletion_cannot_include_deletion_evidence")
        if qualification == "request-only" and (
            unresolved or known_unresolved or graph_unresolved_ids
        ):
            findings.append("request_only_deletion_cannot_hide_unresolved_evidence")
        if qualification == "pending-unresolved" and not (
            unresolved or known_unresolved or graph_unresolved_ids
        ):
            findings.append("pending_unresolved_qualification_without_unresolved_evidence")
    elif record_kind == "deleted":
        if completion not in {"qualified-deleted", "claimed-complete"}:
            findings.append("deleted_record_missing_completion_evidence_state")
        if completion == "qualified-deleted":
            if not graph_complete:
                findings.append("deletion_completion_without_complete_dependency_evidence")
            if unresolved or known_unresolved or graph_unresolved_ids:
                findings.append("deletion_completion_claim_with_unresolved_copies_or_dependents")
            if qualification not in {"qualified-local-deletion", "qualified-external-deletion"}:
                findings.append("qualified_deleted_evidence_missing_qualification")
        if completion == "claimed-complete":
            findings.append("unqualified_deletion_completion_claim")

    independent = value.get("independent_deletion_evidence") or []
    independently_verified_types = {
        item.get("evidence_type")
        for item in independent
        if isinstance(item, Mapping) and item.get("qualification") == "independently-verified"
    }
    local_evidence_present = any(
        isinstance(item, Mapping)
        and item.get("evidence_type") == "local-deletion"
        and item.get("qualification") in {"locally-observed", "independently-verified"}
        for item in independent
    )
    deletion_request_id = value.get("deletion_request_id")
    authorization_reference = value.get("authorization_reference")
    local_evidence_reference = value.get("local_deletion_evidence_reference")
    target_id = target.get("artifact_id") if isinstance(target, Mapping) else None
    reserved_role_references = {deletion_request_id, target_id}
    for field, reference in (
        ("authorization_reference", authorization_reference),
        ("local_deletion_evidence_reference", local_evidence_reference),
    ):
        if reference is not None and reference in reserved_role_references:
            findings.append(f"deletion_reference_role_conflation:{field}")
    if (
        authorization_reference is not None
        and authorization_reference == local_evidence_reference
    ):
        findings.append("deletion_authorization_and_local_evidence_must_differ")
    independent_references = [
        item.get("evidence_reference")
        for item in independent
        if isinstance(item, Mapping)
    ]
    independent_digests = [
        item.get("evidence_digest")
        for item in independent
        if isinstance(item, Mapping)
    ]
    if _duplicates_present(independent_references):
        findings.append("independent_deletion_evidence_reference_reused")
    if _duplicates_present(independent_digests):
        findings.append("independent_deletion_evidence_digest_reused")
    prohibited_independent_references = {
        deletion_request_id,
        target_id,
        authorization_reference,
        local_evidence_reference,
    }
    if any(
        reference in prohibited_independent_references
        for reference in independent_references
    ):
        findings.append("independent_deletion_evidence_role_conflation")
    scoped_copy_blocked = False
    scoped_dependent_blocked = False
    missing_independent_evidence = False
    if completion == "qualified-deleted":
        if "local-record" in scope:
            if not _valid_reference(value.get("local_deletion_evidence_reference")):
                findings.append("qualified_deleted_local_evidence_reference_missing")
            if not local_evidence_present:
                findings.append("qualified_deleted_local_independent_evidence_missing")
        if "known-copy" in scope:
            known_copies = value.get("known_copies", [])
            if not known_copies or any(
                not isinstance(item, Mapping)
                or item.get("evidence_state") != "qualified-deleted"
                for item in known_copies
            ):
                scoped_copy_blocked = True
                findings.append("deletion_completion_claim_with_unresolved_copies_or_dependents")
        if "derived-artifact" in scope:
            derived_artifacts = value.get("derived_artifacts", [])
            if not derived_artifacts or any(
                not isinstance(item, Mapping)
                or item.get("evidence_state") != "qualified-deleted"
                for item in derived_artifacts
            ):
                scoped_dependent_blocked = True
                findings.append("scoped_derived_artifact_deletion_not_qualified")

        external_scope_evidence = {
            "provider-copy": "provider-deletion",
            "backup": "backup-deletion",
            "cache": "cache-deletion",
            "training-data": "training-data-removal",
            "model-weights": "model-unlearning",
            "external-system": "external-system-deletion",
        }
        for scoped_boundary, evidence_type in external_scope_evidence.items():
            if scoped_boundary in scope and evidence_type not in independently_verified_types:
                missing_independent_evidence = True
                findings.append(
                    "qualified_external_scope_evidence_missing:"
                    f"{scoped_boundary}"
                )
        if qualification == "qualified-local-deletion" and "local-record" not in scope:
            findings.append("qualified_local_deletion_scope_missing")
        if scope & set(external_scope_evidence) and qualification != "qualified-external-deletion":
            findings.append("external_deletion_scope_requires_external_qualification")
        if qualification == "qualified-external-deletion" and not (
            scope & set(external_scope_evidence)
        ):
            findings.append("qualified_external_deletion_scope_missing")
    claim_requirements = {
        "physical_erasure_claimed": "physical-erasure",
        "provider_deletion_claimed": "provider-deletion",
        "backup_deletion_claimed": "backup-deletion",
        "cache_deletion_claimed": "cache-deletion",
        "training_data_removal_claimed": "training-data-removal",
        "model_unlearning_claimed": "model-unlearning",
        "all_derived_artifacts_deleted_claimed": "derived-artifact-deletion",
        "all_external_systems_deleted_claimed": "external-system-deletion",
    }
    for field, evidence_type in claim_requirements.items():
        if value.get(field) is True and evidence_type not in independently_verified_types:
            missing_independent_evidence = True
            findings.append(f"qualified_independent_evidence_missing:{field}")
    claim_scope_requirements = {
        "provider_deletion_claimed": "provider-copy",
        "backup_deletion_claimed": "backup",
        "cache_deletion_claimed": "cache",
        "training_data_removal_claimed": "training-data",
        "model_unlearning_claimed": "model-weights",
        "all_derived_artifacts_deleted_claimed": "derived-artifact",
        "all_external_systems_deleted_claimed": "external-system",
    }
    for field, required_scope in claim_scope_requirements.items():
        if value.get(field) is True and required_scope not in scope:
            findings.append(f"deletion_claim_scope_missing:{field}:{required_scope}")
    if value.get("all_derived_artifacts_deleted_claimed") is True and any(
        isinstance(item, Mapping) and item.get("evidence_state") != "qualified-deleted"
        for item in value.get("derived_artifacts", [])
    ):
        findings.append("all_derived_artifacts_deleted_claim_conflicts_with_evidence")
    if value.get("all_external_systems_deleted_claimed") is True:
        findings.append("universal_external_system_deletion_claim_not_supported")
    residual_risk_token = authority_token(value.get("residual_risk_statement", ""))
    residual_risk_denials = (
        r"(?:^|_)no_(?:remaining_)?residual_risks?(?:_|$)",
        r"(?:^|_)no_risks?_remain(?:_|$)",
        r"(?:^|_)residual_risks?(?:_is|_are|_was|_were)?_(?:zero|nil|gone)(?:_|$)",
        r"(?:^|_)zero_residual_risks?(?:_|$)",
        r"(?:^|_)(?:all_)?(?:residual_)?risks?(?:(?:_has|_have)_been|_is|_are|_was|_were)?_(?:eliminated|fully_mitigated|gone)(?:_|$)",
        r"(?:^|_)residual_risks?_none(?:_|$)",
    )
    if residual_risk_token == "none" or any(
        re.search(pattern, residual_risk_token)
        for pattern in residual_risk_denials
    ):
        findings.append("residual_risk_statement_denies_required_qualification")

    reason_codes = set(value.get("reason_codes", []))
    required_reason_codes = {"residual-risk-remains"}
    if completion in ("pending", "incomplete"):
        required_reason_codes.add("deletion-request-recorded")
    if copy_unresolved or scoped_copy_blocked:
        required_reason_codes.add("unresolved-copy")
    if dependent_unresolved or graph_unresolved_ids or scoped_dependent_blocked:
        required_reason_codes.add("unresolved-dependent")
    if unresolved and not (copy_unresolved or dependent_unresolved):
        required_reason_codes.add("unresolved-dependent")
    if (
        _valid_reference(value.get("local_deletion_evidence_reference"))
        and local_evidence_present
    ):
        required_reason_codes.add("local-deletion-evidence-present")
    if completion == "qualified-deleted":
        required_reason_codes.add("qualified-deleted-evidence")
    if value.get("physical_erasure_claimed") is False:
        required_reason_codes.add("physical-erasure-not-proven")
    if value.get("provider_deletion_claimed") is False:
        required_reason_codes.add("provider-deletion-not-proven")
    if missing_independent_evidence:
        required_reason_codes.add("independent-evidence-missing")
    for reason_code in sorted(required_reason_codes - reason_codes):
        findings.append(f"deletion_required_reason_code_missing:{reason_code}")
    for reason_code in sorted(reason_codes - required_reason_codes):
        findings.append(f"deletion_reason_code_not_applicable:{reason_code}")
    return findings


def _provider_dependency_findings(value: Any, path: str) -> list[str]:
    fields = frozenset({"artifact", "provider_reference", "replacement_requirement", "status"})
    findings = _object_shape(value, path=path, fields=fields)
    if not isinstance(value, Mapping):
        return findings
    findings.extend(_artifact_reference_findings(value.get("artifact"), f"{path}.artifact"))
    findings.extend(_scalar_finding(_valid_reference(value.get("provider_reference")), "invalid_reference", f"{path}.provider_reference"))
    findings.extend(_scalar_finding(isinstance(value.get("replacement_requirement"), str) and 1 <= len(value.get("replacement_requirement")) <= 256, "bounded_nonempty_string_required", f"{path}.replacement_requirement"))
    findings.extend(_scalar_finding(value.get("status") in ("supported", "blocking", "quarantined"), "unknown_provider_dependency_status", f"{path}.status"))
    return findings


def _portability_structure_findings(value: Any) -> list[str]:
    fields = frozenset(
        {
            "drill_id",
            "simulation_only",
            "original_model_reference",
            "replacement_model_requirements",
            "learning_proof_readable",
            "decision_proof_references_interpretable",
            "capability_packs_readable",
            "private_evaluations_usable",
            "organizational_memory_interpretable",
            "export_manifests_available",
            "provider_specific_dependencies_identified",
            "provider_specific_dependencies",
            "degraded_mode_represented",
            "deletion_and_revocation_evidence_available",
            "unsupported_dependencies_quarantined",
            "portability_blockers_visible",
            "portability_blockers",
            "portability_state",
            "replacement_model_authorized",
            "provider_disconnected",
            "original_model_invoked",
            "replacement_model_invoked",
            "live_data_migrated",
            "provider_account_accessed",
            "credentials_used",
            "provider_settings_modified",
            "confidential_information_exported",
            "production_workflow_executed",
            "reason_codes",
        }
    )
    findings = _object_shape(value, path="portability_drill", fields=fields)
    if not isinstance(value, Mapping):
        return findings
    findings.extend(_scalar_finding(_valid_identifier(value.get("drill_id")), "invalid_identifier", "portability_drill.drill_id"))
    findings.extend(_scalar_finding(isinstance(value.get("simulation_only"), bool), "boolean_required", "portability_drill.simulation_only"))
    findings.extend(_scalar_finding(_valid_reference(value.get("original_model_reference")), "invalid_reference", "portability_drill.original_model_reference"))
    requirements = value.get("replacement_model_requirements")
    if (
        not isinstance(requirements, list)
        or not requirements
        or _duplicates_present(requirements)
        or not all(
            isinstance(item, str) and 1 <= len(item) <= 256
            for item in requirements
        )
    ):
        findings.append("nonempty_string_array_required:portability_drill.replacement_model_requirements")
    bool_fields = fields - {
        "drill_id",
        "original_model_reference",
        "replacement_model_requirements",
        "provider_specific_dependencies",
        "portability_blockers",
        "portability_state",
        "reason_codes",
    }
    for field in sorted(bool_fields):
        findings.extend(_scalar_finding(isinstance(value.get(field), bool), "boolean_required", f"portability_drill.{field}"))
    dependencies = value.get("provider_specific_dependencies")
    if not isinstance(dependencies, list):
        findings.append("array_required:portability_drill.provider_specific_dependencies")
    else:
        if _duplicates_present(dependencies):
            findings.append("duplicate_provider_specific_dependency")
        for index, item in enumerate(dependencies):
            findings.extend(_provider_dependency_findings(item, f"portability_drill.provider_specific_dependencies[{index}]"))
    blockers = value.get("portability_blockers")
    if (
        not isinstance(blockers, list)
        or _duplicates_present(blockers)
        or not all(_valid_machine_token(item) for item in blockers)
    ):
        findings.append("invalid_portability_blockers")
    findings.extend(_scalar_finding(value.get("portability_state") in PORTABILITY_STATES, "unknown_portability_state", "portability_drill.portability_state"))
    reasons = value.get("reason_codes")
    if (
        not isinstance(reasons, list)
        or not reasons
        or _duplicates_present(reasons)
        or not all(
            isinstance(item, str) and item in PORTABILITY_REASON_CODES
            for item in reasons
        )
    ):
        findings.append("invalid_reason_codes:portability_drill.reason_codes")
    return findings


def _portability_semantic_findings(
    value: Mapping[str, Any],
    *,
    graph: Mapping[str, Any],
    graph_complete: bool,
) -> list[str]:
    findings: list[str] = []
    if value.get("simulation_only") is not True:
        findings.append("portability_drill_must_be_simulation_only")
    forbidden_actions = (
        "replacement_model_authorized",
        "provider_disconnected",
        "original_model_invoked",
        "replacement_model_invoked",
        "live_data_migrated",
        "provider_account_accessed",
        "credentials_used",
        "provider_settings_modified",
        "confidential_information_exported",
        "production_workflow_executed",
    )
    for field in forbidden_actions:
        if value.get(field) is not False:
            findings.append(f"simulation_action_or_authority_forbidden:{field}")

    artifact_map = _artifact_map(graph)
    declared_provider_ids: set[Any] = set()
    blocking_dependencies = False
    quarantined_dependencies = False
    for index, dependency in enumerate(value.get("provider_specific_dependencies", [])):
        if not isinstance(dependency, Mapping):
            continue
        artifact_ref = dependency.get("artifact")
        artifact_id = artifact_ref.get("artifact_id") if isinstance(artifact_ref, Mapping) else None
        declared_provider_ids.add(artifact_id)
        artifact = artifact_map.get(artifact_id)
        if not _reference_matches_artifact(artifact_ref, artifact):
            findings.append(f"provider_dependency_graph_binding_mismatch:{index}")
        elif artifact.get("provider_specific_dependency") is not True:
            findings.append(f"provider_dependency_not_marked_in_graph:{index}")
        if dependency.get("status") == "blocking":
            blocking_dependencies = True
        if dependency.get("status") == "quarantined":
            quarantined_dependencies = True
    graph_provider_ids = {
        item.get("artifact_id")
        for item in artifact_map.values()
        if item.get("provider_specific_dependency") is True
    }
    if graph_provider_ids != declared_provider_ids:
        findings.append("provider_specific_dependencies_not_fully_identified")
    if value.get("provider_specific_dependencies_identified") is not True:
        findings.append("provider_specific_dependency_identification_not_complete")

    graph_artifact_types = {
        item.get("artifact_type")
        for item in artifact_map.values()
        if isinstance(item.get("artifact_type"), str)
    }
    required_type_by_assessment = {
        "learning_proof_readable": "learning-proof",
        "decision_proof_references_interpretable": "decision-proof",
        "capability_packs_readable": "capability-memory-pack",
        "private_evaluations_usable": "private-evaluation",
        "organizational_memory_interpretable": "organizational-memory",
        "export_manifests_available": "export-manifest",
        "deletion_and_revocation_evidence_available": "lifecycle-evidence",
    }
    for field, artifact_type in required_type_by_assessment.items():
        if value.get(field) is True and artifact_type not in graph_artifact_types:
            findings.append(
                f"portability_assessment_graph_evidence_missing:{field}:{artifact_type}"
            )

    blockers = value.get("portability_blockers") or []
    state = value.get("portability_state")
    readable_fields = (
        "learning_proof_readable",
        "decision_proof_references_interpretable",
        "capability_packs_readable",
        "private_evaluations_usable",
        "organizational_memory_interpretable",
        "export_manifests_available",
        "degraded_mode_represented",
        "deletion_and_revocation_evidence_available",
        "unsupported_dependencies_quarantined",
        "portability_blockers_visible",
    )
    if blocking_dependencies:
        if not blockers:
            findings.append("provider_specific_blocker_not_declared")
        if value.get("portability_blockers_visible") is not True:
            findings.append("portability_blockers_not_visible")
    if blockers and value.get("portability_blockers_visible") is not True:
        findings.append("portability_blockers_not_visible")
    if quarantined_dependencies and value.get("unsupported_dependencies_quarantined") is not True:
        findings.append("quarantined_dependency_state_not_represented")
    if state == "portable-in-simulation":
        if not graph_complete:
            findings.append("portability_claimed_without_complete_dependency_evidence")
        if blocking_dependencies or blockers:
            findings.append("portability_claimed_with_provider_specific_blocker")
        for field in readable_fields:
            if value.get(field) is not True:
                findings.append(f"portable_simulation_requirement_not_met:{field}")
    elif state == "blocked":
        if not blockers and not blocking_dependencies:
            findings.append("blocked_portability_without_visible_blocker")
        if value.get("portability_blockers_visible") is not True:
            findings.append("portability_blockers_not_visible")
    elif state == "degraded":
        if value.get("degraded_mode_represented") is not True:
            findings.append("degraded_portability_without_degraded_mode_evidence")
        if blocking_dependencies and value.get("unsupported_dependencies_quarantined") is not True:
            findings.append("degraded_portability_without_quarantine")

    reason_codes = set(value.get("reason_codes", []))
    required_reason_codes = {"simulation-only"}
    if all(value.get(field) is True for field in readable_fields[:6]) and value.get(
        "deletion_and_revocation_evidence_available"
    ) is True:
        required_reason_codes.add("evidence-readable")
    if value.get("degraded_mode_represented") is True:
        required_reason_codes.add("degraded-mode-represented")
    if graph_provider_ids:
        required_reason_codes.add("provider-specific-dependency")
    if blockers and value.get("portability_blockers_visible") is True:
        required_reason_codes.add("portability-blocker-visible")
    if value.get("unsupported_dependencies_quarantined") is True:
        required_reason_codes.add("unsupported-dependency-quarantined")
    if value.get("replacement_model_authorized") is False:
        required_reason_codes.add("replacement-model-not-authorized")
    if value.get("production_workflow_executed") is False:
        required_reason_codes.add("production-execution-not-attempted")
    for reason_code in sorted(required_reason_codes - reason_codes):
        findings.append(f"portability_required_reason_code_missing:{reason_code}")
    for reason_code in sorted(reason_codes - required_reason_codes):
        findings.append(f"portability_reason_code_not_applicable:{reason_code}")
    return findings


def _cross_track_structure_findings(value: Any) -> list[str]:
    fields = frozenset({"learning_proof", "capability_memory_pack", "decision_proof", "linkage_purpose"})
    findings = _object_shape(value, path="cross_track_linkage", fields=fields)
    if not isinstance(value, Mapping):
        return findings
    definitions = {
        "learning_proof": (
            frozenset({"reference", "schema_version", "track_c_evidence_record_digest", "source_integrity_hash", "usage"}),
            ("linkage-only", "rollback-authority", "deletion-authority", "installation-authority", "execution-authority"),
        ),
        "capability_memory_pack": (
            frozenset({"reference", "schema_version", "track_c_evidence_record_digest", "derived_spec_manifest_digest", "usage"}),
            ("non-executable-evidence", "installation-authority", "executable-authority"),
        ),
        "decision_proof": (
            frozenset({"reference", "schema_version", "track_c_evidence_record_digest", "usage"}),
            ("linkage-only", "deletion-execution-authority", "execution-authority"),
        ),
    }
    for name, (nested_fields, usages) in definitions.items():
        nested = value.get(name)
        path = f"cross_track_linkage.{name}"
        findings.extend(_object_shape(nested, path=path, fields=nested_fields))
        if not isinstance(nested, Mapping):
            continue
        findings.extend(_scalar_finding(_valid_reference(nested.get("reference")), "invalid_reference", f"{path}.reference"))
        findings.extend(_scalar_finding(_valid_version(nested.get("schema_version")), "invalid_version", f"{path}.schema_version"))
        findings.extend(_scalar_finding(_valid_digest(nested.get("track_c_evidence_record_digest")), "invalid_digest", f"{path}.track_c_evidence_record_digest"))
        findings.extend(_scalar_finding(nested.get("usage") in usages, "unknown_linkage_usage", f"{path}.usage"))
        if name == "learning_proof":
            findings.extend(_scalar_finding(nested.get("schema_version") == LEARNING_PROOF_SCHEMA_VERSION, "unsupported_schema_version", f"{path}.schema_version"))
            findings.extend(_scalar_finding(_valid_digest(nested.get("source_integrity_hash")), "invalid_digest", f"{path}.source_integrity_hash"))
        elif name == "capability_memory_pack":
            findings.extend(_scalar_finding(nested.get("schema_version") == CAPABILITY_PACK_SCHEMA_VERSION, "unsupported_schema_version", f"{path}.schema_version"))
            findings.extend(_scalar_finding(_valid_digest(nested.get("derived_spec_manifest_digest")), "invalid_digest", f"{path}.derived_spec_manifest_digest"))
    findings.extend(_scalar_finding(value.get("linkage_purpose") == "evidence-only", "invalid_linkage_purpose", "cross_track_linkage.linkage_purpose"))
    return findings


def _cross_track_semantic_findings(
    value: Mapping[str, Any],
    *,
    graph: Mapping[str, Any],
) -> tuple[list[str], list[str], list[str], list[str]]:
    general: list[str] = []
    learning: list[str] = []
    capability: list[str] = []
    decision: list[str] = []
    artifact_types = {
        "learning_proof": "learning-proof",
        "capability_memory_pack": "capability-memory-pack",
        "decision_proof": "decision-proof",
    }
    for name, artifact_type in artifact_types.items():
        linkage = value.get(name)
        if not isinstance(linkage, Mapping):
            general.append(f"cross_track_linkage_object_missing:{name}")
            continue
        matches = [
            artifact
            for artifact in graph.get("artifacts", [])
            if isinstance(artifact, Mapping)
            and artifact.get("artifact_type") == artifact_type
            and artifact.get("artifact_id") == linkage.get("reference")
        ]
        target_findings = learning if name == "learning_proof" else capability if name == "capability_memory_pack" else decision
        if len(matches) != 1:
            target_findings.append(f"{name}_graph_identifier_binding_missing")
            continue
        artifact = matches[0]
        if artifact.get("artifact_version") != linkage.get("schema_version"):
            target_findings.append(f"{name}_graph_version_binding_mismatch")
        if artifact.get("artifact_digest") != linkage.get("track_c_evidence_record_digest"):
            target_findings.append(f"{name}_graph_digest_binding_mismatch")
        if artifact.get("digest_role") != "track-c-evidence-record":
            target_findings.append(f"{name}_graph_digest_role_mismatch")

    learning_linkage = value.get("learning_proof")
    if isinstance(learning_linkage, Mapping):
        if learning_linkage.get("schema_version") != LEARNING_PROOF_SCHEMA_VERSION:
            learning.append("learning_proof_schema_version_mismatch")
        if learning_linkage.get("source_integrity_hash") == learning_linkage.get(
            "track_c_evidence_record_digest"
        ):
            learning.append("learning_proof_digest_role_conflation")
        if learning_linkage.get("usage") != "linkage-only":
            learning.append("learning_proof_linkage_treated_as_authority")
    capability_linkage = value.get("capability_memory_pack")
    if isinstance(capability_linkage, Mapping):
        if capability_linkage.get("schema_version") != CAPABILITY_PACK_SCHEMA_VERSION:
            capability.append("capability_memory_pack_schema_version_mismatch")
        if capability_linkage.get(
            "derived_spec_manifest_digest"
        ) == capability_linkage.get("track_c_evidence_record_digest"):
            capability.append("capability_memory_pack_digest_role_conflation")
        if capability_linkage.get("usage") != "non-executable-evidence":
            capability.append("capability_memory_pack_treated_as_installation_or_execution_authority")
    decision_linkage = value.get("decision_proof")
    if isinstance(decision_linkage, Mapping) and decision_linkage.get("usage") != "linkage-only":
        decision.append("decision_proof_linkage_treated_as_deletion_or_execution_authority")
    return general, learning, capability, decision


def _cross_track_lifecycle_reference_reuse_findings(
    artifact: Mapping[str, Any],
) -> dict[str, list[str]]:
    findings = {
        "dependency_graph": [],
        "lineage_evidence": [],
        "rollback_evidence": [],
        "deletion_evidence": [],
        "portability_drill": [],
    }
    linkage = artifact.get("cross_track_linkage")
    if not isinstance(linkage, Mapping):
        return findings
    cross_track_references = {
        item.get("reference")
        for item in linkage.values()
        if isinstance(item, Mapping) and _valid_reference(item.get("reference"))
    }
    if not cross_track_references:
        return findings

    def check(section: str, path: str, value: Any) -> None:
        if isinstance(value, str) and value in cross_track_references:
            findings[section].append(
                f"cross_track_reference_reused_as_lifecycle_evidence:{path}"
            )

    graph = artifact.get("dependency_graph")
    if isinstance(graph, Mapping):
        check(
            "dependency_graph",
            "dependency_graph.completeness_evidence_reference",
            graph.get("completeness_evidence_reference"),
        )
        check(
            "dependency_graph",
            "dependency_graph.graph_snapshot_reference",
            graph.get("graph_snapshot_reference"),
        )
    lineage = artifact.get("lineage_evidence")
    if isinstance(lineage, Mapping):
        for field in (
            "archival_evidence_reference",
            "revocation_evidence_reference",
        ):
            check("lineage_evidence", f"lineage_evidence.{field}", lineage.get(field))
    rollback = artifact.get("rollback_evidence")
    if isinstance(rollback, Mapping):
        for field in ("authorization_reference", "execution_evidence_reference"):
            check("rollback_evidence", f"rollback_evidence.{field}", rollback.get(field))
    deletion = artifact.get("deletion_evidence")
    if isinstance(deletion, Mapping):
        for field in ("authorization_reference", "local_deletion_evidence_reference"):
            check("deletion_evidence", f"deletion_evidence.{field}", deletion.get(field))
        independent = deletion.get("independent_deletion_evidence")
        if isinstance(independent, list):
            for index, item in enumerate(independent):
                if isinstance(item, Mapping):
                    check(
                        "deletion_evidence",
                        "deletion_evidence.independent_deletion_evidence"
                        f"[{index}].evidence_reference",
                        item.get("evidence_reference"),
                    )
    portability = artifact.get("portability_drill")
    if isinstance(portability, Mapping):
        check(
            "portability_drill",
            "portability_drill.original_model_reference",
            portability.get("original_model_reference"),
        )
        dependencies = portability.get("provider_specific_dependencies")
        if isinstance(dependencies, list):
            for index, item in enumerate(dependencies):
                if isinstance(item, Mapping):
                    check(
                        "portability_drill",
                        "portability_drill.provider_specific_dependencies"
                        f"[{index}].provider_reference",
                        item.get("provider_reference"),
                    )
    return findings


def _graph_lifecycle_reference_reuse_findings(
    artifact: Mapping[str, Any],
) -> dict[str, list[str]]:
    findings = {
        "lineage_evidence": [],
        "rollback_evidence": [],
        "deletion_evidence": [],
        "portability_drill": [],
    }
    graph = artifact.get("dependency_graph")
    if not isinstance(graph, Mapping):
        return findings
    graph_role_references = {
        value
        for value in (
            graph.get("graph_id"),
            graph.get("completeness_evidence_reference"),
            graph.get("graph_snapshot_reference"),
        )
        if isinstance(value, str) and _valid_reference(value)
    }
    if not graph_role_references:
        return findings

    def check(section: str, path: str, value: Any) -> None:
        if isinstance(value, str) and value in graph_role_references:
            findings[section].append(
                f"graph_reference_reused_as_lifecycle_evidence:{path}"
            )

    lineage = artifact.get("lineage_evidence")
    if isinstance(lineage, Mapping):
        check("lineage_evidence", "lineage_evidence.archival_evidence_reference", lineage.get("archival_evidence_reference"))
        check("lineage_evidence", "lineage_evidence.revocation_evidence_reference", lineage.get("revocation_evidence_reference"))

    rollback = artifact.get("rollback_evidence")
    if isinstance(rollback, Mapping):
        check("rollback_evidence", "rollback_evidence.rollback_request_id", rollback.get("rollback_request_id"))
        check("rollback_evidence", "rollback_evidence.authorization_reference", rollback.get("authorization_reference"))
        check("rollback_evidence", "rollback_evidence.execution_evidence_reference", rollback.get("execution_evidence_reference"))

    deletion = artifact.get("deletion_evidence")
    if isinstance(deletion, Mapping):
        check("deletion_evidence", "deletion_evidence.deletion_request_id", deletion.get("deletion_request_id"))
        check("deletion_evidence", "deletion_evidence.authorization_reference", deletion.get("authorization_reference"))
        check("deletion_evidence", "deletion_evidence.local_deletion_evidence_reference", deletion.get("local_deletion_evidence_reference"))
        for index, item in enumerate(deletion.get("independent_deletion_evidence", [])):
            if isinstance(item, Mapping):
                check(
                    "deletion_evidence",
                    f"deletion_evidence.independent_deletion_evidence[{index}].evidence_reference",
                    item.get("evidence_reference"),
                )

    portability = artifact.get("portability_drill")
    if isinstance(portability, Mapping):
        check("portability_drill", "portability_drill.original_model_reference", portability.get("original_model_reference"))
        for index, item in enumerate(portability.get("provider_specific_dependencies", [])):
            if isinstance(item, Mapping):
                check(
                    "portability_drill",
                    f"portability_drill.provider_specific_dependencies[{index}].provider_reference",
                    item.get("provider_reference"),
                )
    return findings


def _authority_subject_present(value: str) -> bool:
    compact = authority_token(value).replace("_", "")
    subjects = (
        "release",
        "governance",
        "policy",
        "identity",
        "risk",
        "deployment",
        "rollback",
        "deletion",
        "physical_erasure",
        "provider_deletion",
        "provider_erasure",
        "backup",
        "cache",
        "training_data",
        "model_unlearning",
        "provider",
        "replacement_model",
        "installation",
        "execution",
        "production",
        "audit",
        "waiver",
        "authority",
        "learning_proof",
        "decision_proof",
        "capability_pack",
        "downstream",
        "milestone",
        "m15",
        "tracker",
        "issue",
        "v0_14_0",
        "v0140",
        "tool",
        "skill",
        "capability",
        "model",
        "training",
        "fine_tuning",
        "credential",
        "network",
        "subprocess",
        "live_data",
        "confidential_information",
        "live_memory",
    )
    return any(subject.replace("_", "") in compact for subject in subjects)


def _authority_action_present(value: str) -> bool:
    token = authority_token(value)
    compact = token.replace("_", "")
    actions = (
        "approved",
        "approval",
        "authorized",
        "authorization",
        "accepted",
        "acceptance",
        "executed",
        "complete",
        "completed",
        "closed",
        "closure",
        "granted",
        "transferred",
        "transfer",
        "sealed",
        "sealing",
        "installed",
        "installation",
        "executable",
        "disconnected",
        "invoked",
        "migrated",
        "accessed",
        "modified",
        "exported",
        "allowed",
        "issued",
        "deleted",
        "erased",
        "unlearned",
        "removed",
        "proven",
        "activated",
        "registered",
        "confirmed",
        "attested",
        "permitted",
        "enabled",
        "deployed",
        "waived",
        "resolved",
        "passed",
        "finalized",
        "ratified",
        "adopted",
        "enacted",
        "destroyed",
        "purged",
        "scrubbed",
        "effective",
        "succeeded",
        "done",
        "achieved",
        "certified",
        "greenlit",
        "go",
        "performed",
        "satisfied",
        "finished",
        "delegated",
        "operational",
        "live",
        "published",
        "publication",
        "released",
        "started",
        "used",
        "called",
    )
    pieces = set(token.split("_"))
    if pieces.intersection(actions):
        return True
    return any(
        len(action) > 4
        and action in compact
        and f"un{action}" not in compact
        and f"in{action}" not in compact
        and f"not{action}" not in compact
        for action in actions
    )


def _authority_text_claim(value: str) -> bool:
    token = authority_token(value)
    token = re.sub(
        r"(?:physical_erasure|provider_(?:deletion|erasure))"
        r"(?:_is|_are|_remain|_remains)?_"
        r"(?:not_(?:independently_)?(?:verified|proven)|unverified)",
        "_",
        token,
    )
    token = re.sub(
        r"(?:does_not|cannot)_(?:establish|prove|show|qualify)_"
        r"(?:physical_erasure|provider_(?:deletion|erasure))",
        "_",
        token,
    )
    negative_phrases = (
        "not_authorized",
        "not_approved",
        "not_executed",
        "not_sealed",
        "not_disconnected",
        "not_proven",
        "evidence_only",
        "review_required",
        "authorization_not_recorded",
        "execution_not_attempted",
        "not_claimed",
        "no_authority",
        "without_authority",
        "authority_not_granted",
        "not_removed",
        "not_deleted",
        "not_erased",
        "not_unlearned",
        "not_verified",
        "not_independently_verified",
        "not_independently_proven",
        "remains_unverified",
        "remain_unverified",
        "is_unverified",
        "are_unverified",
        "not_invoked",
        "must_not_be_invoked",
        "must_not_invoke",
    )
    for phrase in negative_phrases:
        token = token.replace(phrase, "")
    token = re.sub(
        r"(?:^|_)no_(?:physical_erasure|provider_(?:deletion|erasure))"
        r"(?:_or_(?:physical_erasure|provider_(?:deletion|erasure)))*"
        r"_(?:is|are)_(?:independently_)?(?:verified|proven)(?:_|$)",
        "_",
        token,
    )
    compact = token.replace("_", "")
    pieces = set(token.split("_"))
    sensitive_qualified_claim = (
        ("identity" in compact and "valid" in pieces)
        or ("policy" in compact and "active" in pieces)
        or ("capability" in compact and "active" in pieces)
        or (
            "verified" in pieces
            and any(
                subject in compact
                for subject in (
                    "physicalerasure",
                    "providerdeletion",
                    "providererasure",
                    "backupdeletion",
                    "cachedeletion",
                    "trainingdataremoval",
                    "modelunlearning",
                )
            )
        )
    )
    return sensitive_qualified_claim or (
        _authority_subject_present(token) and _authority_action_present(token)
    ) or any(authority_token(item) == token for item in FORBIDDEN_AUTHORITY_TOKENS)


def _authority_value_explicitly_negative(value: Any) -> bool:
    if value is None or value is False or (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and value == 0
    ):
        return True
    if not isinstance(value, str):
        return False
    token = authority_token(value)
    return token in {
        "",
        "false",
        "denied",
        "rejected",
        "prohibited",
        "forbidden",
        "evidence_only",
        "review_required",
        "unresolved",
        "unverified",
        "incomplete",
        "open",
        "unpublished",
        "not_created",
        "unauthorized",
    } or any(
        phrase in token
        for phrase in (
            "not_authorized",
            "not_approved",
            "not_executed",
            "not_sealed",
            "not_disconnected",
            "not_proven",
            "not_claimed",
            "not_removed",
            "not_deleted",
            "not_erased",
            "not_unlearned",
            "not_verified",
            "not_independently_verified",
            "not_independently_proven",
            "remains_unverified",
            "remain_unverified",
            "is_unverified",
            "are_unverified",
            "not_invoked",
            "must_not_be_invoked",
            "must_not_invoke",
            "not_complete",
            "remains_open",
            "not_published",
            "does_not_establish_provider_erasure",
            "does_not_establish_provider_deletion",
            "does_not_prove_provider_erasure",
            "does_not_prove_provider_deletion",
            "authorization_not_recorded",
            "execution_not_attempted",
            "no_authority",
            "without_authority",
            "authority_not_granted",
        )
    )


def _scan_open_authority_text(
    value: Any,
    path: tuple[str, ...],
    *,
    subject_context: bool = False,
) -> list[str]:
    findings: list[str] = []
    normalized_forbidden_keys = frozenset(
        authority_token(item) for item in FORBIDDEN_AUTHORITY_KEYS
    )
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            safe_key = _safe_path_component(key)
            child_path = path + (safe_key,)
            key_is_claim = _authority_text_claim(key)
            key_has_subject = _authority_subject_present(key)
            if key_is_claim and authority_value_is_affirmative(
                child,
                normalized_forbidden_keys,
            ):
                findings.append("forbidden_authority_text:" + ".".join(child_path))
            if (
                subject_context
                and authority_token(key)
                in {
                    "status",
                    "state",
                    "result",
                    "outcome",
                    "decision",
                    "authorization",
                    "approval",
                    "authority",
                    "sealing",
                }
                and (
                    not _authority_value_explicitly_negative(child)
                    or (isinstance(child, str) and _authority_text_claim(child))
                )
                and authority_value_is_affirmative(
                    child,
                    normalized_forbidden_keys,
                )
            ):
                findings.append("forbidden_authority_text:" + ".".join(child_path))
            findings.extend(
                _scan_open_authority_text(
                    child,
                    child_path,
                    subject_context=subject_context or key_has_subject,
                )
            )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(
                _scan_open_authority_text(
                    child,
                    path + (str(index),),
                    subject_context=subject_context,
                )
            )
    elif isinstance(value, str):
        if _authority_text_claim(value) or (
            subject_context
            and not _authority_value_explicitly_negative(value)
            and _authority_action_present(value)
        ):
            findings.append("forbidden_authority_text:" + ".".join(path))
    elif subject_context and authority_value_is_affirmative(
        value,
        normalized_forbidden_keys,
    ):
        findings.append("forbidden_authority_text:" + ".".join(path))
    return findings


def _active_authority_text_findings(artifact: Mapping[str, Any]) -> list[str]:
    findings: list[str] = []
    candidates: tuple[tuple[tuple[str, ...], Any], ...] = (
        (("lineage_evidence", "reason"), (artifact.get("lineage_evidence") or {}).get("reason") if isinstance(artifact.get("lineage_evidence"), Mapping) else None),
        (("rollback_evidence", "reason_codes"), (artifact.get("rollback_evidence") or {}).get("reason_codes") if isinstance(artifact.get("rollback_evidence"), Mapping) else None),
        (("deletion_evidence", "residual_risk_statement"), (artifact.get("deletion_evidence") or {}).get("residual_risk_statement") if isinstance(artifact.get("deletion_evidence"), Mapping) else None),
        (("deletion_evidence", "reason_codes"), (artifact.get("deletion_evidence") or {}).get("reason_codes") if isinstance(artifact.get("deletion_evidence"), Mapping) else None),
        (("portability_drill", "replacement_model_requirements"), (artifact.get("portability_drill") or {}).get("replacement_model_requirements") if isinstance(artifact.get("portability_drill"), Mapping) else None),
        (("portability_drill", "portability_blockers"), (artifact.get("portability_drill") or {}).get("portability_blockers") if isinstance(artifact.get("portability_drill"), Mapping) else None),
        (("portability_drill", "reason_codes"), (artifact.get("portability_drill") or {}).get("reason_codes") if isinstance(artifact.get("portability_drill"), Mapping) else None),
    )
    for path, value in candidates:
        if value is not None:
            findings.extend(_scan_open_authority_text(value, path))
    portability = artifact.get("portability_drill")
    if isinstance(portability, Mapping):
        dependencies = portability.get("provider_specific_dependencies")
        if not isinstance(dependencies, list):
            dependencies = []
        for index, dependency in enumerate(
            dependencies
        ):
            if isinstance(dependency, Mapping):
                findings.extend(
                    _scan_open_authority_text(
                        dependency.get("replacement_requirement"),
                        (
                            "portability_drill",
                            "provider_specific_dependencies",
                            str(index),
                            "replacement_requirement",
                        ),
                    )
                )
    graph = artifact.get("dependency_graph")
    if isinstance(graph, Mapping):
        unresolved_dependencies = graph.get("unresolved_dependencies")
        if not isinstance(unresolved_dependencies, list):
            unresolved_dependencies = []
        for index, unresolved in enumerate(unresolved_dependencies):
            if isinstance(unresolved, Mapping):
                findings.extend(
                    _scan_open_authority_text(
                        unresolved.get("reason_code"),
                        (
                            "dependency_graph",
                            "unresolved_dependencies",
                            str(index),
                            "reason_code",
                        ),
                    )
                )
    return findings


def _authority_findings(artifact: Mapping[str, Any]) -> list[str]:
    findings: list[str] = []
    claims = artifact.get("authority_claims")
    if not isinstance(claims, Mapping):
        return ["authority_claims_must_be_object"]
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
        findings.extend(
            scan_forbidden_authority_claims(
                extensions,
                forbidden_keys=FORBIDDEN_AUTHORITY_KEYS,
                forbidden_tokens=FORBIDDEN_AUTHORITY_TOKENS,
                path=("extensions",),
            )
        )
        findings.extend(_scan_open_authority_text(extensions, ("extensions",)))
    findings.extend(_active_authority_text_findings(artifact))
    return _sorted_findings(findings)


def _sensitive_material_findings(value: Any, path: tuple[str, ...] = ()) -> list[str]:
    findings: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            safe_key = _safe_path_component(key)
            child_path = path + (safe_key,)
            rendered = ".".join(child_path)
            if safe_key == "<redacted-key>":
                findings.append(f"sensitive_material_detected:key:{rendered}")
            if key != "credentials_used":
                for category, pattern in SENSITIVE_KEY_PATTERNS:
                    if pattern.search(key):
                        findings.append(f"sensitive_material_detected:{category}:{rendered}")
            findings.extend(_sensitive_material_findings(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_sensitive_material_findings(child, path + (str(index),)))
    elif isinstance(value, str):
        rendered = ".".join(path) or "$"
        for category, pattern in SENSITIVE_VALUE_PATTERNS:
            if pattern.search(value):
                findings.append(f"sensitive_material_detected:{category}:{rendered}")
    return _sorted_findings(findings)


def _top_level_structure_findings(artifact: Mapping[str, Any]) -> list[str]:
    findings = _object_shape(artifact, path="", fields=TOP_LEVEL_FIELDS)
    findings.extend(_scalar_finding(artifact.get("schema_version") == SCHEMA_VERSION, "unsupported_schema_version", "schema_version"))
    findings.extend(_scalar_finding(_valid_identifier(artifact.get("track_c_record_id")), "invalid_identifier", "track_c_record_id"))
    findings.extend(_scalar_finding(artifact.get("record_kind") in RECORD_KINDS, "unknown_record_kind", "record_kind"))
    findings.extend(_scalar_finding(_valid_timestamp(artifact.get("effective_timestamp")), "invalid_timestamp", "effective_timestamp"))
    findings.extend(_scalar_finding(artifact.get("non_authoritative_boundary_statement") == NON_AUTHORITATIVE_BOUNDARY_STATEMENT, "boundary_statement_mismatch", "non_authoritative_boundary_statement"))
    if not isinstance(artifact.get("extensions"), Mapping):
        findings.append("object_required:extensions")
    claims = artifact.get("authority_claims")
    if not isinstance(claims, Mapping):
        findings.append("object_required:authority_claims")
    else:
        for field in FIXED_FALSE_AUTHORITY_CLAIMS:
            if field not in claims:
                findings.append(f"required_field_missing:authority_claims.{field}")
            elif claims.get(field) is not False:
                findings.append(f"authority_claim_must_be_false:{field}")

    record_kind = artifact.get("record_kind")
    expected_sections = {
        "supersession": "lineage_evidence",
        "revocation": "lineage_evidence",
        "rollback-readiness": "rollback_evidence",
        "deletion-pending": "deletion_evidence",
        "deleted": "deletion_evidence",
        "model-removal-portability": "portability_drill",
    }
    expected_section = (
        expected_sections.get(record_kind) if isinstance(record_kind, str) else None
    )
    for section in ("lineage_evidence", "rollback_evidence", "deletion_evidence", "portability_drill"):
        if section == expected_section:
            if not isinstance(artifact.get(section), Mapping):
                findings.append(f"required_evidence_section_missing:{section}")
        elif artifact.get(section) is not None:
            findings.append(f"unexpected_evidence_section:{section}")
    return findings


def _invalid_result(findings: list[str]) -> dict[str, object]:
    return {
        "valid": False,
        "schema_valid": False,
        "record_identity_valid": False,
        "dependency_graph_valid": False,
        "dependency_graph_complete": False,
        "lineage_valid": False,
        "rollback_evidence_valid": False,
        "rollback_ready": False,
        "rollback_readiness": "not-assessed",
        "deletion_evidence_valid": False,
        "deletion_complete_qualified": False,
        "deletion_status": "not-assessed",
        "portability_evidence_valid": False,
        "portable_in_simulation": False,
        "portability_state": "not-assessed",
        "cross_track_linkage_valid": False,
        "learning_proof_linkage_valid": False,
        "capability_memory_pack_linkage_valid": False,
        "decision_proof_linkage_valid": False,
        "sensitive_material_absent": False,
        "authority_boundary_valid": False,
        "evidence_disposition": "invalid-evidence",
        "findings": _sorted_findings(findings),
    }


def evaluate_lineage_rollback_portability(
    artifact: Mapping[str, object],
) -> dict[str, object]:
    """Evaluate caller-supplied Track C evidence without executing lifecycle work."""

    if not isinstance(artifact, Mapping):
        return _invalid_result(["artifact_must_be_mapping"])

    artifact_dict = dict(artifact)
    container_safety_findings = _container_safety_findings(artifact_dict)
    if container_safety_findings:
        return _invalid_result(container_safety_findings)
    lifecycle_reference_reuse = _cross_track_lifecycle_reference_reuse_findings(
        artifact_dict
    )
    graph_reference_reuse = _graph_lifecycle_reference_reuse_findings(
        artifact_dict
    )
    top_findings = _top_level_structure_findings(artifact_dict)
    graph = artifact_dict.get("dependency_graph")
    graph_structure_findings = _graph_structure_findings(graph)
    graph_dict = graph if isinstance(graph, Mapping) else {}
    graph_semantic_findings = (
        _graph_semantic_findings(graph_dict) if not graph_structure_findings else []
    )
    graph_semantic_findings.extend(lifecycle_reference_reuse["dependency_graph"])

    lineage = artifact_dict.get("lineage_evidence")
    lineage_structure_findings = (
        _lineage_structure_findings(lineage) if lineage is not None else []
    )
    lineage_semantic_findings = (
        _lineage_semantic_findings(
            lineage,
            record_kind=artifact_dict.get("record_kind"),
            graph=graph_dict,
            effective_timestamp=artifact_dict.get("effective_timestamp"),
        )
        if isinstance(lineage, Mapping)
        and not lineage_structure_findings
        and not graph_structure_findings
        else []
    )
    lineage_semantic_findings.extend(lifecycle_reference_reuse["lineage_evidence"])
    lineage_semantic_findings.extend(graph_reference_reuse["lineage_evidence"])

    rollback = artifact_dict.get("rollback_evidence")
    rollback_structure_findings = (
        _rollback_structure_findings(rollback) if rollback is not None else []
    )

    completeness_claimed = graph_dict.get("completeness_declared") is True
    graph_complete = (
        completeness_claimed
        and _valid_reference(graph_dict.get("completeness_evidence_reference"))
        and graph_dict.get("unresolved_dependencies") == []
        and not graph_structure_findings
        and not graph_semantic_findings
    )
    rollback_semantic_findings = (
        _rollback_semantic_findings(
            rollback,
            graph=graph_dict,
            graph_complete=graph_complete,
        )
        if isinstance(rollback, Mapping)
        and not rollback_structure_findings
        and not graph_structure_findings
        else []
    )
    rollback_semantic_findings.extend(lifecycle_reference_reuse["rollback_evidence"])
    rollback_semantic_findings.extend(graph_reference_reuse["rollback_evidence"])

    deletion = artifact_dict.get("deletion_evidence")
    deletion_structure_findings = (
        _deletion_structure_findings(deletion) if deletion is not None else []
    )
    deletion_semantic_findings = (
        _deletion_semantic_findings(
            deletion,
            record_kind=artifact_dict.get("record_kind"),
            graph=graph_dict,
            graph_complete=graph_complete,
        )
        if isinstance(deletion, Mapping)
        and not deletion_structure_findings
        and not graph_structure_findings
        else []
    )
    deletion_semantic_findings.extend(lifecycle_reference_reuse["deletion_evidence"])
    deletion_semantic_findings.extend(graph_reference_reuse["deletion_evidence"])

    portability = artifact_dict.get("portability_drill")
    portability_structure_findings = (
        _portability_structure_findings(portability)
        if portability is not None
        else []
    )
    portability_semantic_findings = (
        _portability_semantic_findings(
            portability,
            graph=graph_dict,
            graph_complete=graph_complete,
        )
        if isinstance(portability, Mapping)
        and not portability_structure_findings
        and not graph_structure_findings
        else []
    )
    portability_semantic_findings.extend(lifecycle_reference_reuse["portability_drill"])
    portability_semantic_findings.extend(graph_reference_reuse["portability_drill"])

    linkage = artifact_dict.get("cross_track_linkage")
    linkage_structure_findings = _cross_track_structure_findings(linkage)
    if (
        isinstance(linkage, Mapping)
        and not linkage_structure_findings
        and not graph_structure_findings
    ):
        (
            linkage_general_findings,
            learning_linkage_findings,
            capability_linkage_findings,
            decision_linkage_findings,
        ) = _cross_track_semantic_findings(linkage, graph=graph_dict)
    else:
        linkage_general_findings = []
        learning_linkage_findings = []
        capability_linkage_findings = []
        decision_linkage_findings = []

    authority_findings = _sorted_findings(
        _authority_findings(artifact_dict),
        *lifecycle_reference_reuse.values(),
        *graph_reference_reuse.values(),
    )
    sensitive_findings = _sensitive_material_findings(artifact_dict)

    schema_valid = not _sorted_findings(
        top_findings,
        graph_structure_findings,
        lineage_structure_findings,
        rollback_structure_findings,
        deletion_structure_findings,
        portability_structure_findings,
        linkage_structure_findings,
    )
    record_identity_valid = not any(
        item.startswith(("unsupported_schema_version:", "invalid_identifier:track_c_record_id", "unknown_record_kind:", "invalid_timestamp:effective_timestamp"))
        for item in top_findings
    )
    dependency_graph_valid = not graph_structure_findings and not graph_semantic_findings
    lineage_valid = (
        lineage is None
        if artifact_dict.get("record_kind") not in ("supersession", "revocation")
        else isinstance(lineage, Mapping)
        and not lineage_structure_findings
        and not lineage_semantic_findings
    )
    rollback_evidence_valid = (
        rollback is None
        if artifact_dict.get("record_kind") != "rollback-readiness"
        else isinstance(rollback, Mapping)
        and not rollback_structure_findings
        and not rollback_semantic_findings
    )
    deletion_evidence_valid = (
        deletion is None
        if artifact_dict.get("record_kind") not in ("deletion-pending", "deleted")
        else isinstance(deletion, Mapping)
        and not deletion_structure_findings
        and not deletion_semantic_findings
    )
    portability_evidence_valid = (
        portability is None
        if artifact_dict.get("record_kind") != "model-removal-portability"
        else isinstance(portability, Mapping)
        and not portability_structure_findings
        and not portability_semantic_findings
    )
    learning_proof_linkage_valid = not linkage_structure_findings and not learning_linkage_findings
    capability_memory_pack_linkage_valid = not linkage_structure_findings and not capability_linkage_findings
    decision_proof_linkage_valid = not linkage_structure_findings and not decision_linkage_findings
    cross_track_linkage_valid = all(
        (
            not linkage_structure_findings,
            not linkage_general_findings,
            learning_proof_linkage_valid,
            capability_memory_pack_linkage_valid,
            decision_proof_linkage_valid,
        )
    )
    sensitive_material_absent = not sensitive_findings
    authority_boundary_valid = not authority_findings and all(
        (
            not learning_linkage_findings,
            not capability_linkage_findings,
            not decision_linkage_findings,
            not any(
                item.startswith("simulation_action_or_authority_forbidden:")
                for item in portability_semantic_findings
            ),
        )
    )

    record_kind = artifact_dict.get("record_kind")
    rollback_readiness = (
        rollback.get("readiness_state")
        if record_kind == "rollback-readiness"
        and isinstance(rollback, Mapping)
        and rollback_evidence_valid
        else "not-assessed"
    )
    rollback_ready = rollback_readiness == "ready-for-human-review"
    deletion_status = (
        deletion.get("completion_status")
        if record_kind in ("deletion-pending", "deleted")
        and isinstance(deletion, Mapping)
        and deletion_evidence_valid
        else "not-assessed"
    )
    deletion_complete_qualified = deletion_status == "qualified-deleted"
    portability_state = (
        portability.get("portability_state")
        if record_kind == "model-removal-portability"
        and isinstance(portability, Mapping)
        and portability_evidence_valid
        else "not-assessed"
    )
    portable_in_simulation = portability_state == "portable-in-simulation"

    valid = all(
        (
            schema_valid,
            record_identity_valid,
            dependency_graph_valid,
            lineage_valid,
            rollback_evidence_valid,
            deletion_evidence_valid,
            portability_evidence_valid,
            cross_track_linkage_valid,
            sensitive_material_absent,
            authority_boundary_valid,
        )
    )

    if not valid:
        evidence_disposition = "invalid-evidence"
    elif record_kind == "dependency-graph":
        evidence_disposition = (
            "complete-dependency-evidence"
            if graph_complete
            else "incomplete-dependency-evidence"
        )
    elif record_kind in ("supersession", "revocation"):
        evidence_disposition = "lineage-evidence"
    elif record_kind == "rollback-readiness":
        evidence_disposition = "rollback-readiness-evidence"
    elif record_kind == "deletion-pending":
        evidence_disposition = "deletion-pending-evidence"
    elif record_kind == "deleted":
        evidence_disposition = "qualified-deleted-evidence"
    elif portability_state == "portable-in-simulation":
        evidence_disposition = "portability-evidence"
    else:
        evidence_disposition = "blocked-portability-evidence"

    informational_findings: list[str] = []
    if dependency_graph_valid and not graph_complete:
        informational_findings.append("dependency_graph_incomplete")
    if isinstance(lineage, Mapping) and lineage.get("unresolved_dependents"):
        informational_findings.append("unresolved_lineage_dependents_present")
    if rollback_evidence_valid and isinstance(rollback, Mapping):
        if rollback.get("incompatible_dependents"):
            informational_findings.append("rollback_incompatible_dependents_present")
        if rollback.get("unresolved_dependents"):
            informational_findings.append("rollback_unresolved_dependents_present")
    if deletion_evidence_valid and isinstance(deletion, Mapping) and (
        deletion.get("unresolved_dependencies")
        or any(
            isinstance(item, Mapping)
            and item.get("evidence_state") in ("unknown", "deletion-pending")
            for item in deletion.get("known_copies", [])
        )
    ):
        informational_findings.append("deletion_unresolved_dependencies_present")
    if portability_evidence_valid and portability_state == "blocked":
        informational_findings.append("portability_blockers_present")

    findings = _sorted_findings(
        top_findings,
        graph_structure_findings,
        graph_semantic_findings,
        lineage_structure_findings,
        lineage_semantic_findings,
        rollback_structure_findings,
        rollback_semantic_findings,
        deletion_structure_findings,
        deletion_semantic_findings,
        portability_structure_findings,
        portability_semantic_findings,
        linkage_structure_findings,
        linkage_general_findings,
        learning_linkage_findings,
        capability_linkage_findings,
        decision_linkage_findings,
        authority_findings,
        sensitive_findings,
        informational_findings,
    )
    return {
        "valid": valid,
        "schema_valid": schema_valid,
        "record_identity_valid": record_identity_valid,
        "dependency_graph_valid": dependency_graph_valid,
        "dependency_graph_complete": graph_complete,
        "lineage_valid": lineage_valid,
        "rollback_evidence_valid": rollback_evidence_valid,
        "rollback_ready": rollback_ready,
        "rollback_readiness": rollback_readiness,
        "deletion_evidence_valid": deletion_evidence_valid,
        "deletion_complete_qualified": deletion_complete_qualified,
        "deletion_status": deletion_status,
        "portability_evidence_valid": portability_evidence_valid,
        "portable_in_simulation": portable_in_simulation,
        "portability_state": portability_state,
        "cross_track_linkage_valid": cross_track_linkage_valid,
        "learning_proof_linkage_valid": learning_proof_linkage_valid,
        "capability_memory_pack_linkage_valid": capability_memory_pack_linkage_valid,
        "decision_proof_linkage_valid": decision_proof_linkage_valid,
        "sensitive_material_absent": sensitive_material_absent,
        "authority_boundary_valid": authority_boundary_valid,
        "evidence_disposition": evidence_disposition,
        "findings": findings,
    }


__all__ = [
    "ARTIFACT_TYPES",
    "BOUNDARIES",
    "CAPABILITY_PACK_SCHEMA_VERSION",
    "FIXED_FALSE_AUTHORITY_CLAIMS",
    "LEARNING_PROOF_SCHEMA_VERSION",
    "NON_AUTHORITATIVE_BOUNDARY_STATEMENT",
    "RECORD_KINDS",
    "SCHEMA_VERSION",
    "evaluate_lineage_rollback_portability",
]
