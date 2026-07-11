"""Deterministic, fail-closed admission for external Decision Proof evidence."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any


CONNECTION_STATUSES = {
    "ready",
    "auth_failed",
    "unreachable",
    "misconfigured",
    "unknown",
}

FRESHNESS_STATUSES = {
    "current",
    "stale",
    "unknown",
    "not_applicable",
}

EXTRACTION_STATUSES = {
    "complete",
    "partial",
    "empty",
    "schema_mismatch",
    "fallback_required",
}

ADMISSION_RESULTS = {"verified", "degraded", "rejected"}

EVIDENCE_KINDS = {"dataset", "paper", "document", "endpoint"}

SUPPORTED_POLICY_VERSION = "aaos-external-evidence-admission-v1"

TWINKLE_HUB_SOURCE_ID = "ai-twinkle-hub"
TWINKLE_HUB_SOURCE_NAME = "ai-twinkle/Hub"
TWINKLE_HUB_ENDPOINT_REFERENCE = "https://api.twinkleai.tw/mcp/"
ALLOWED_CLIENT_TYPES = {
    "aaos-deterministic-fixture",
    "mcp-remote-fixture",
}
ALLOWED_AUTHENTICATION_MODES = {
    "fixture_no_live_auth",
    "oauth_metadata_flow_observed",
}

SANITIZED_ERROR_CATEGORIES = {
    "none",
    "source_not_found",
    "oauth_token_exchange_failed",
    "authentication_rejected",
    "source_unreachable",
    "source_misconfigured",
    "freshness_check_failed",
    "extraction_integrity_failed",
    "schema_validation_failed",
    "model_interpretation_failed",
    "governance_policy_failed",
    "unknown_external_source_error",
}

WARNING_CODES = {
    "structured_questions_partial",
    "structured_questions_empty",
    "missing_multiple_choice_options",
    "missing_answer",
    "raw_pdf_fallback_required",
    "source_batch_stale",
    "authoritative_source_refresh_required",
    "oauth_failure_before_retrieval",
    "source_not_found",
    "admission_record_rejected_by_gate",
}

SOURCE_FAILURE_CATEGORIES = {
    "none",
    "source_absence",
    "authentication_failure",
    "connection_failure",
    "configuration_failure",
    "freshness_failure",
    "unknown_source_failure",
}

EXTRACTION_FAILURE_CATEGORIES = {
    "none",
    "partial_extraction",
    "empty_extraction",
    "schema_mismatch",
    "fallback_required",
}

MODEL_FAILURE_CATEGORIES = {
    "none",
    "model_interpretation_failure",
    "model_output_validation_failure",
}

GOVERNANCE_FAILURE_CATEGORIES = {
    "none",
    "governance_policy_failure",
    "sealing_boundary_violation",
}

POLICY_RESULTS_BY_FIELD = {
    "stale_freshness_result": {"degraded", "rejected"},
    "unknown_freshness_result": {"rejected"},
    "partial_extraction_result": {"degraded", "rejected"},
    "fallback_required_result": {"degraded", "rejected"},
}

REQUIRED_FIELDS = (
    "evidence_id",
    "source_identity",
    "evidence_kind",
    "dataset_or_paper_identifier",
    "retrieved_at",
    "source_published_at",
    "source_batch_or_version",
    "authoritative_source_reference",
    "retrieval_succeeded",
    "connection_status",
    "freshness_required",
    "freshness_threshold_seconds",
    "freshness_status",
    "extraction_attempted",
    "extraction_status",
    "extraction_metrics",
    "admission_result",
    "policy_version",
    "admission_policy",
    "sanitized_error_category",
    "explicit_warnings",
    "raw_or_pdf_fallback_reference",
    "replay_failure_classification",
    "decision_path_eligible",
    "decision_proof_sealing_eligible",
    "storage_disposition",
)

SOURCE_IDENTITY_FIELDS = (
    "source_id",
    "source_name",
    "source_type",
    "endpoint_reference",
    "client_type",
    "authentication_mode",
)

EXTRACTION_METRIC_FIELDS = (
    "item_count_reported",
    "item_count_verified",
    "missing_fields",
    "schema_valid",
    "structured_evidence_available",
    "raw_source_available",
)

ADMISSION_POLICY_FIELDS = (
    "stale_freshness_result",
    "unknown_freshness_result",
    "partial_extraction_result",
    "fallback_required_result",
)

REPLAY_CLASSIFICATION_FIELDS = (
    "source_failure",
    "extraction_failure",
    "model_failure",
    "governance_failure",
)

ALLOWED_TOP_LEVEL_FIELDS = REQUIRED_FIELDS

FORBIDDEN_SECRET_KEYS = {
    "access_token",
    "authorization",
    "authorization_code",
    "authorization_header",
    "authorization_headers",
    "auth_code",
    "client_secret",
    "cookie",
    "cookies",
    "oauth_token",
    "proxy_authorization",
    "raw_auth_header",
    "raw_auth_headers",
    "raw_authorization_header",
    "raw_authorization_headers",
    "set_cookie",
}

SECRET_VALUE_PATTERNS = (
    re.compile(
        r"(?i)\b(?:authorization|proxy-authorization|cookie|set-cookie)\s*:"
        r"\s*[^\r\n]+"
    ),
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+"),
    re.compile(r"(?i)\b(?:basic|digest)\s+[A-Za-z0-9._~+/=,:-]{8,}"),
    re.compile(
        r"(?i)\b(?:access_token|authorization_code|auth_code|client_secret|"
        r"oauth_token|cookie|set_cookie)\s*=\s*[^&\s]+"
    ),
    re.compile(
        r"(?i)[?#&](?:access_token|authorization_code|code|client_secret|"
        r"oauth_token|token|secret)=[^&#\s]+"
    ),
    re.compile(
        r"""(?ix)
        ["']?(?:access_token|authorization_code|auth_code|client_secret|
        oauth_token|cookie|cookies|authorization|raw_authorization_headers?)
        ["']?\s*:\s*(?:"[^"]*"|'[^']*'|[^,}\s]+)
        """
    ),
    re.compile(
        r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"
    ),
    re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bya29\.[A-Za-z0-9._-]{10,}\b"),
    re.compile(r"\bGOCSPX-[A-Za-z0-9_-]{10,}\b"),
    re.compile(r"\b4/[A-Za-z0-9_-]{10,}\b"),
    re.compile(r"(?i)\bsessionid[A-Za-z0-9._-]{8,}\b"),
    re.compile(r"(?i)\bhttps?://[^/\s:@]+:[^/\s@]+@"),
)

FIELD_PATH_PATTERN = re.compile(r"^[A-Za-z0-9_.\[\]-]+$")
SAFE_LABEL_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+-]{0,255}$")
EVIDENCE_ID_PATTERN = re.compile(r"^hub-[A-Za-z0-9._:-]{1,251}$")
SAFE_REFERENCE_PATTERN = re.compile(
    r"^(?:[A-Za-z][A-Za-z0-9+.-]*:[^\s?#{}\"'@]+|"
    r"not_available:[A-Za-z0-9._:-]+)$"
)
RFC3339_TIMESTAMP_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2})[Tt]"
    r"((?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d)"
    r"(\.\d{1,6})?"
    r"([Zz]|\+(?:[01]\d|2[0-3]):[0-5]\d|"
    r"-(?:(?:0[1-9]|1\d|2[0-3]):[0-5]\d|00:(?:0[1-9]|[1-5]\d)))"
    r"(?![\s\S])"
)

RESERVED_SANITIZATION_SENTINELS = {
    "[REDACTED_SENSITIVE_VALUE]",
    "hub-invalid-evidence-id",
    "redacted-source",
    "urn:aaos:redacted:unsafe-endpoint-reference",
    "redacted-client",
    "redacted-authentication-mode",
    "redacted-dataset-or-paper",
    "redacted-source-batch",
    "urn:aaos:redacted:unsafe-authoritative-reference",
    "not_available:unsafe_reference_removed",
    "invalid-policy-version",
}

RESULT_SEVERITY = {"verified": 0, "degraded": 1, "rejected": 2}

STORAGE_DISPOSITIONS = {
    "verified": "verified_evidence",
    "degraded": "inspection_only",
    "rejected": "replay_metadata_only",
}


def _normalize_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")


def _sanitize_value(value: Any) -> tuple[Any, bool]:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        changed = False
        for key, nested in value.items():
            normalized_key = _normalize_key(key)
            if normalized_key in FORBIDDEN_SECRET_KEYS:
                changed = True
                continue
            safe_value, nested_changed = _sanitize_value(nested)
            sanitized[str(key)] = safe_value
            changed = changed or nested_changed
        return sanitized, changed

    if isinstance(value, (list, tuple)):
        sanitized_items = []
        changed = isinstance(value, tuple)
        for nested in value:
            safe_value, nested_changed = _sanitize_value(nested)
            sanitized_items.append(safe_value)
            changed = changed or nested_changed
        return sanitized_items, changed

    if isinstance(value, str):
        sanitized = value
        for pattern in SECRET_VALUE_PATTERNS:
            sanitized = pattern.sub("[REDACTED_SENSITIVE_VALUE]", sanitized)
        return sanitized, sanitized != value

    if value is None or isinstance(value, (bool, int, float)):
        return value, False

    return None, True


def _filter_mapping(
    value: Any, allowed_fields: tuple[str, ...]
) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {key: value[key] for key in allowed_fields if key in value}


def _safe_label(value: Any, fallback: str) -> str:
    if not isinstance(value, str) or not SAFE_LABEL_PATTERN.fullmatch(value):
        return fallback
    normalized = value.casefold()
    if any(
        marker in normalized
        for marker in (
            "access_token",
            "authorization_code",
            "client_secret",
            "credential",
            "raw_authorization",
            "sessionid",
            "ya29.",
            "gocspx-",
        )
    ) or normalized.startswith("4/"):
        return fallback
    return value


def _safe_reference(value: Any, fallback: str) -> str:
    if not isinstance(value, str) or not SAFE_REFERENCE_PATTERN.fullmatch(value):
        return fallback
    normalized = value.casefold()
    if any(
        marker in normalized
        for marker in (
            "access_token",
            "authorization_code",
            "client_secret",
            "credential",
            "raw_authorization",
        )
    ):
        return fallback
    return value


def _safe_field_path(value: Any) -> str | None:
    if not isinstance(value, str) or not FIELD_PATH_PATTERN.fullmatch(value):
        return None
    normalized = value.casefold()
    if any(
        marker in normalized
        for marker in (
            "access_token",
            "authorization_code",
            "client_secret",
            "credential",
            "raw_authorization",
        )
    ):
        return None
    return value


def _safe_enum(value: Any, allowed: set[str], fallback: str) -> str:
    return value if isinstance(value, str) and value in allowed else fallback


def _safe_nonnegative_int(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return 0
    return value


def _canonical_timestamp(value: Any, *, nullable: bool) -> str | None:
    parsed = _parse_timestamp(value)
    if parsed is None:
        return None if nullable else "1970-01-01T00:00:00Z"
    match = RFC3339_TIMESTAMP_PATTERN.fullmatch(value)
    assert match is not None
    fraction = match.group(3) or ""
    return parsed.strftime("%Y-%m-%dT%H:%M:%S") + fraction + "Z"


def _sanitize_external_evidence_record(candidate: Any) -> dict[str, Any]:

    sanitized, _ = _sanitize_value(candidate)
    if not isinstance(sanitized, dict):
        sanitized = {}

    filtered = _filter_mapping(sanitized, ALLOWED_TOP_LEVEL_FIELDS)
    source = _filter_mapping(
        filtered.get("source_identity"), SOURCE_IDENTITY_FIELDS
    )
    metrics = _filter_mapping(
        filtered.get("extraction_metrics"), EXTRACTION_METRIC_FIELDS
    )
    policy = _filter_mapping(
        filtered.get("admission_policy"), ADMISSION_POLICY_FIELDS
    )
    replay = _filter_mapping(
        filtered.get("replay_failure_classification"),
        REPLAY_CLASSIFICATION_FIELDS,
    )

    warnings = filtered.get("explicit_warnings")
    if not isinstance(warnings, list):
        warnings = []
    safe_warnings = [
        warning
        for warning in warnings
        if isinstance(warning, str) and warning in WARNING_CODES
    ]

    missing_fields = metrics.get("missing_fields")
    if not isinstance(missing_fields, list):
        missing_fields = []
    safe_missing_fields = []
    for field in missing_fields:
        safe_field = _safe_field_path(field)
        if safe_field is not None:
            safe_missing_fields.append(safe_field)

    safe_policy = {
        field: _safe_enum(
            policy.get(field),
            POLICY_RESULTS_BY_FIELD[field],
            "rejected",
        )
        for field in ADMISSION_POLICY_FIELDS
    }

    return {
        "evidence_id": (
            filtered["evidence_id"]
            if isinstance(filtered.get("evidence_id"), str)
            and EVIDENCE_ID_PATTERN.fullmatch(filtered["evidence_id"])
            else "hub-invalid-evidence-id"
        ),
        "source_identity": {
            "source_id": (
                TWINKLE_HUB_SOURCE_ID
                if source.get("source_id") == TWINKLE_HUB_SOURCE_ID
                else "redacted-source"
            ),
            "source_name": (
                TWINKLE_HUB_SOURCE_NAME
                if source.get("source_name") == TWINKLE_HUB_SOURCE_NAME
                else "redacted-source"
            ),
            "source_type": (
                "mcp" if source.get("source_type") == "mcp" else "mcp"
            ),
            "endpoint_reference": (
                TWINKLE_HUB_ENDPOINT_REFERENCE
                if source.get("endpoint_reference")
                == TWINKLE_HUB_ENDPOINT_REFERENCE
                else "urn:aaos:redacted:unsafe-endpoint-reference"
            ),
            "client_type": _safe_enum(
                source.get("client_type"),
                ALLOWED_CLIENT_TYPES,
                "redacted-client",
            ),
            "authentication_mode": _safe_enum(
                source.get("authentication_mode"),
                ALLOWED_AUTHENTICATION_MODES,
                "redacted-authentication-mode",
            ),
        },
        "evidence_kind": _safe_enum(
            filtered.get("evidence_kind"), EVIDENCE_KINDS, "endpoint"
        ),
        "dataset_or_paper_identifier": _safe_label(
            filtered.get("dataset_or_paper_identifier"),
            "redacted-dataset-or-paper",
        ),
        "retrieved_at": _canonical_timestamp(
            filtered.get("retrieved_at"), nullable=False
        ),
        "source_published_at": _canonical_timestamp(
            filtered.get("source_published_at"), nullable=True
        ),
        "source_batch_or_version": _safe_label(
            filtered.get("source_batch_or_version"),
            "redacted-source-batch",
        ),
        "authoritative_source_reference": _safe_reference(
            filtered.get("authoritative_source_reference"),
            "urn:aaos:redacted:unsafe-authoritative-reference",
        ),
        "retrieval_succeeded": filtered.get("retrieval_succeeded") is True,
        "connection_status": _safe_enum(
            filtered.get("connection_status"),
            CONNECTION_STATUSES,
            "unknown",
        ),
        "freshness_required": filtered.get("freshness_required") is True,
        "freshness_threshold_seconds": _safe_nonnegative_int(
            filtered.get("freshness_threshold_seconds")
        ),
        "freshness_status": _safe_enum(
            filtered.get("freshness_status"),
            FRESHNESS_STATUSES,
            "unknown",
        ),
        "extraction_attempted": filtered.get("extraction_attempted") is True,
        "extraction_status": _safe_enum(
            filtered.get("extraction_status"),
            EXTRACTION_STATUSES,
            "schema_mismatch",
        ),
        "extraction_metrics": {
            "item_count_reported": _safe_nonnegative_int(
                metrics.get("item_count_reported")
            ),
            "item_count_verified": _safe_nonnegative_int(
                metrics.get("item_count_verified")
            ),
            "missing_fields": safe_missing_fields,
            "schema_valid": metrics.get("schema_valid") is True,
            "structured_evidence_available": (
                metrics.get("structured_evidence_available") is True
            ),
            "raw_source_available": metrics.get("raw_source_available") is True,
        },
        "admission_result": _safe_enum(
            filtered.get("admission_result"), ADMISSION_RESULTS, "rejected"
        ),
        "policy_version": (
            SUPPORTED_POLICY_VERSION
            if filtered.get("policy_version") == SUPPORTED_POLICY_VERSION
            else "invalid-policy-version"
        ),
        "admission_policy": safe_policy,
        "sanitized_error_category": _safe_enum(
            filtered.get("sanitized_error_category"),
            SANITIZED_ERROR_CATEGORIES,
            "unknown_external_source_error",
        ),
        "explicit_warnings": safe_warnings,
        "raw_or_pdf_fallback_reference": _safe_reference(
            filtered.get("raw_or_pdf_fallback_reference"),
            "not_available:unsafe_reference_removed",
        ),
        "replay_failure_classification": {
            "source_failure": _safe_enum(
                replay.get("source_failure"),
                SOURCE_FAILURE_CATEGORIES,
                "unknown_source_failure",
            ),
            "extraction_failure": _safe_enum(
                replay.get("extraction_failure"),
                EXTRACTION_FAILURE_CATEGORIES,
                "schema_mismatch",
            ),
            "model_failure": _safe_enum(
                replay.get("model_failure"),
                MODEL_FAILURE_CATEGORIES,
                "model_output_validation_failure",
            ),
            "governance_failure": _safe_enum(
                replay.get("governance_failure"),
                GOVERNANCE_FAILURE_CATEGORIES,
                "governance_policy_failure",
            ),
        },
        "decision_path_eligible": filtered.get("decision_path_eligible") is True,
        "decision_proof_sealing_eligible": (
            filtered.get("decision_proof_sealing_eligible") is True
        ),
        "storage_disposition": _safe_enum(
            filtered.get("storage_disposition"),
            set(STORAGE_DISPOSITIONS.values()),
            "replay_metadata_only",
        ),
    }


def sanitize_external_evidence_record(candidate: Any) -> dict[str, Any]:
    """Return the only representation that may be stored or serialized."""

    try:
        return _sanitize_external_evidence_record(candidate)
    except Exception:
        return _sanitize_external_evidence_record({})


def _strictly_equivalent_after_benign_canonicalization(
    candidate: Any,
    sanitized: Any,
    *,
    path: tuple[str, ...] = (),
) -> bool:
    if path in {("retrieved_at",), ("source_published_at",)}:
        if candidate is None or sanitized is None:
            return candidate is None and sanitized is None
        if _parse_timestamp(candidate) is None:
            return False
        canonical = _canonical_timestamp(
            candidate,
            nullable=path == ("source_published_at",),
        )
        return type(sanitized) is str and canonical == sanitized

    if type(candidate) is not type(sanitized):
        return False
    if type(candidate) is dict:
        if set(candidate) != set(sanitized):
            return False
        return all(
            _strictly_equivalent_after_benign_canonicalization(
                candidate[key],
                sanitized[key],
                path=path + (key,),
            )
            for key in candidate
        )
    if type(candidate) is list:
        if len(candidate) != len(sanitized):
            return False
        return all(
            _strictly_equivalent_after_benign_canonicalization(
                candidate_item,
                sanitized_item,
                path=path + (str(index),),
            )
            for index, (candidate_item, sanitized_item) in enumerate(
                zip(candidate, sanitized)
            )
        )
    return candidate == sanitized


def _contains_reserved_sanitization_sentinel(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            _contains_reserved_sanitization_sentinel(nested)
            for nested in value.values()
        )
    if isinstance(value, list):
        return any(_contains_reserved_sanitization_sentinel(item) for item in value)
    return isinstance(value, str) and value in RESERVED_SANITIZATION_SENTINELS


def _source_identity_is_supported(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and value.get("source_id") == TWINKLE_HUB_SOURCE_ID
        and value.get("source_name") == TWINKLE_HUB_SOURCE_NAME
        and value.get("source_type") == "mcp"
        and value.get("endpoint_reference") == TWINKLE_HUB_ENDPOINT_REFERENCE
        and value.get("client_type") in ALLOWED_CLIENT_TYPES
        and value.get("authentication_mode") in ALLOWED_AUTHENTICATION_MODES
    )


def _record_uses_unknown_local_offset(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    return any(
        isinstance(value.get(field), str)
        and value[field].endswith("-00:00")
        for field in ("retrieved_at", "source_published_at")
    )


def _record_shape_changed(candidate: Any, sanitized: dict[str, Any]) -> bool:
    generic_sanitized, secret_changed = _sanitize_value(candidate)
    if secret_changed:
        return True
    if not isinstance(generic_sanitized, dict):
        return True

    if set(generic_sanitized) - set(ALLOWED_TOP_LEVEL_FIELDS):
        return True
    if _contains_reserved_sanitization_sentinel(generic_sanitized):
        return True
    if not _source_identity_is_supported(generic_sanitized.get("source_identity")):
        return True

    nested_shapes = {
        "source_identity": SOURCE_IDENTITY_FIELDS,
        "extraction_metrics": EXTRACTION_METRIC_FIELDS,
        "admission_policy": ADMISSION_POLICY_FIELDS,
        "replay_failure_classification": REPLAY_CLASSIFICATION_FIELDS,
    }
    for field, allowed_fields in nested_shapes.items():
        value = generic_sanitized.get(field)
        if not isinstance(value, dict):
            continue
        if set(value) - set(allowed_fields):
            return True

    return not _strictly_equivalent_after_benign_canonicalization(
        generic_sanitized,
        sanitized,
    )


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    match = RFC3339_TIMESTAMP_PATTERN.fullmatch(value)
    if match is None:
        return None
    zone = match.group(4)
    normalized_zone = "+00:00" if zone in {"Z", "z"} else zone
    normalized = (
        f"{match.group(1)}T{match.group(2)}"
        f"{match.group(3) or ''}{normalized_zone}"
    )
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _normalize_trusted_policy(
    value: Any,
) -> tuple[dict[str, Any], list[str]]:
    fallback = {
        "policy_version": SUPPORTED_POLICY_VERSION,
        "freshness_threshold_seconds": 0,
        "admission_policy": {
            field: "rejected" for field in ADMISSION_POLICY_FIELDS
        },
    }
    if not isinstance(value, dict):
        return fallback, ["missing_trusted_admission_policy"]

    findings: list[str] = []
    version = value.get("policy_version")
    if version != SUPPORTED_POLICY_VERSION:
        findings.append("unsupported_trusted_policy_version")
        version = SUPPORTED_POLICY_VERSION

    threshold = value.get("freshness_threshold_seconds")
    if (
        isinstance(threshold, bool)
        or not isinstance(threshold, int)
        or threshold < 0
    ):
        findings.append("invalid_trusted_freshness_threshold")
        threshold = 0

    supplied_policy = value.get("admission_policy")
    if not isinstance(supplied_policy, dict):
        findings.append("invalid_trusted_admission_policy")
        supplied_policy = {}

    normalized_policy: dict[str, str] = {}
    for field in ADMISSION_POLICY_FIELDS:
        result = supplied_policy.get(field)
        if result not in POLICY_RESULTS_BY_FIELD[field]:
            findings.append(f"invalid_trusted_admission_policy:{field}")
            result = "rejected"
        normalized_policy[field] = result

    return {
        "policy_version": version,
        "freshness_threshold_seconds": threshold,
        "admission_policy": normalized_policy,
    }, findings


def derive_freshness_status(
    record: dict[str, Any],
    freshness_threshold_seconds: int | None = None,
) -> tuple[str, list[str]]:
    """Derive freshness from fixed record timestamps, never from wall-clock time."""

    findings: list[str] = []
    if record.get("freshness_required") is not True:
        if record.get("evidence_kind") == "dataset":
            findings.append("mutable_dataset_freshness_not_applicable")
            return "unknown", findings
        return "not_applicable", findings

    retrieved_at = _parse_timestamp(record.get("retrieved_at"))
    published_at = _parse_timestamp(record.get("source_published_at"))
    threshold = freshness_threshold_seconds

    if retrieved_at is None:
        findings.append("invalid_retrieved_at")
    if published_at is None:
        findings.append("invalid_source_published_at")
    if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold < 0:
        findings.append("invalid_freshness_threshold")

    if findings:
        return "unknown", findings

    assert retrieved_at is not None
    assert published_at is not None
    assert isinstance(threshold, int)

    age_seconds = (retrieved_at - published_at).total_seconds()
    if age_seconds < 0:
        findings.append("source_published_after_retrieval")
        return "unknown", findings
    if age_seconds > threshold:
        return "stale", findings
    return "current", findings


def derive_extraction_status(record: dict[str, Any]) -> tuple[str, list[str]]:
    """Derive extraction integrity from deterministic count and schema metrics."""

    findings: list[str] = []
    if record.get("extraction_attempted") is not True:
        return "fallback_required", findings

    metrics = record.get("extraction_metrics")
    if not isinstance(metrics, dict):
        return "schema_mismatch", ["missing_extraction_metrics"]

    reported = metrics.get("item_count_reported")
    verified = metrics.get("item_count_verified")
    missing_fields = metrics.get("missing_fields")

    for name, value in (("reported", reported), ("verified", verified)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            findings.append(f"invalid_{name}_item_count")

    if not isinstance(missing_fields, list):
        findings.append("invalid_missing_fields")
        missing_fields = []

    if metrics.get("schema_valid") is not True:
        return "schema_mismatch", findings
    if findings:
        return "schema_mismatch", findings
    if verified == 0:
        return "empty", findings
    if reported != verified or missing_fields:
        return "partial", findings
    if metrics.get("structured_evidence_available") is not True:
        return "fallback_required", findings
    return "complete", findings


def _derive_source_failure(
    connection_status: str,
    freshness_status: str,
    sanitized_error_category: str,
) -> str:
    if sanitized_error_category == "source_not_found":
        return "source_absence"
    if connection_status == "auth_failed":
        return "authentication_failure"
    if connection_status == "unreachable":
        return "connection_failure"
    if connection_status == "misconfigured":
        return "configuration_failure"
    if connection_status == "unknown":
        return "unknown_source_failure"
    if freshness_status in {"stale", "unknown"}:
        return "freshness_failure"
    return "none"


def _derive_extraction_failure(
    extraction_attempted: bool,
    extraction_status: str,
    source_failure: str,
    retrieval_succeeded: bool,
) -> str:
    if not extraction_attempted:
        if source_failure != "none" or not retrieval_succeeded:
            return "none"
        return "fallback_required"
    return {
        "complete": "none",
        "partial": "partial_extraction",
        "empty": "empty_extraction",
        "schema_mismatch": "schema_mismatch",
        "fallback_required": "fallback_required",
    }.get(extraction_status, "schema_mismatch")


def _most_restrictive(*results: str) -> str:
    return max(results, key=lambda result: RESULT_SEVERITY.get(result, 2))


def _policy_result(
    trusted_policy: dict[str, Any],
    connection_status: str,
    freshness_status: str,
    extraction_status: str,
    sanitized_error_category: str,
) -> str:
    policy_values = trusted_policy["admission_policy"]

    if connection_status != "ready" or sanitized_error_category == "source_not_found":
        connection_result = "rejected"
    else:
        connection_result = "verified"

    freshness_result = {
        "current": "verified",
        "not_applicable": "verified",
        "stale": policy_values["stale_freshness_result"],
        "unknown": policy_values["unknown_freshness_result"],
    }.get(freshness_status, "rejected")

    extraction_result = {
        "complete": "verified",
        "partial": policy_values["partial_extraction_result"],
        "fallback_required": policy_values["fallback_required_result"],
        "empty": "rejected",
        "schema_mismatch": "rejected",
    }.get(extraction_status, "rejected")

    return _most_restrictive(
        connection_result,
        freshness_result,
        extraction_result,
    )


def _validate_degraded_storage(
    record: dict[str, Any],
    freshness_status: str,
    extraction_status: str,
) -> list[str]:
    findings: list[str] = []
    metrics = record.get("extraction_metrics")
    raw_source_available = (
        isinstance(metrics, dict) and metrics.get("raw_source_available") is True
    )
    raw_reference = record.get("raw_or_pdf_fallback_reference")
    usable_reference = (
        isinstance(raw_reference, str)
        and bool(raw_reference.strip())
        and not raw_reference.startswith("not_available:")
    )
    warnings = record.get("explicit_warnings")
    warning_codes = set(warnings) if isinstance(warnings, list) else set()

    if not warning_codes:
        findings.append("degraded_evidence_missing_explicit_warning")
    if not raw_source_available or not usable_reference:
        findings.append("degraded_evidence_missing_raw_source_reference")

    required_warning_by_state = {
        ("freshness", "stale"): "source_batch_stale",
        ("extraction", "partial"): "structured_questions_partial",
        ("extraction", "fallback_required"): "raw_pdf_fallback_required",
    }
    for (dimension, status), warning in required_warning_by_state.items():
        actual_status = (
            freshness_status if dimension == "freshness" else extraction_status
        )
        if actual_status == status and warning not in warning_codes:
            findings.append(f"degraded_evidence_missing_reason_warning:{warning}")

    return findings


def _validate_error_category(
    connection_status: str,
    error_category: str,
    source_failure: str,
    extraction_failure: str,
    model_failure: str,
    governance_failure: str,
) -> list[str]:
    if error_category not in SANITIZED_ERROR_CATEGORIES:
        return ["invalid_sanitized_error_category"]

    required_by_connection = {
        "auth_failed": {
            "oauth_token_exchange_failed",
            "authentication_rejected",
        },
        "unreachable": {"source_unreachable"},
        "misconfigured": {"source_misconfigured"},
        "unknown": {"unknown_external_source_error"},
    }
    expected = required_by_connection.get(connection_status)
    if expected is None:
        expected = set()
        if source_failure == "source_absence":
            expected.add("source_not_found")
        elif source_failure == "freshness_failure":
            expected.add("freshness_check_failed")

        if extraction_failure in {
            "partial_extraction",
            "empty_extraction",
            "fallback_required",
        }:
            expected.add("extraction_integrity_failed")
        elif extraction_failure == "schema_mismatch":
            expected.add("schema_validation_failed")

        if model_failure != "none":
            expected.add("model_interpretation_failed")
        if governance_failure != "none":
            expected.add("governance_policy_failed")
        if not expected:
            expected.add("none")

    if error_category not in expected:
        return ["error_failure_classification_mismatch"]
    return []


def _validate_required_metadata(record: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    for field in sorted(REQUIRED_FIELDS):
        if field not in record:
            findings.append(f"missing_replay_metadata:{field}")

    source_identity = record.get("source_identity")
    if not isinstance(source_identity, dict):
        findings.append("missing_replay_metadata:source_identity")
    else:
        for field in sorted(SOURCE_IDENTITY_FIELDS):
            value = source_identity.get(field)
            if not isinstance(value, str) or not value.strip():
                findings.append(f"missing_replay_metadata:source_identity.{field}")

    for field in (
        "evidence_id",
        "dataset_or_paper_identifier",
        "source_batch_or_version",
        "authoritative_source_reference",
        "policy_version",
    ):
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            findings.append(f"missing_replay_metadata:{field}")

    if _parse_timestamp(record.get("retrieved_at")) is None:
        findings.append("invalid_retrieved_at")

    return findings


def evaluate_external_evidence_admission(
    candidate: Any,
    *,
    trusted_policy: Any = None,
) -> dict[str, Any]:
    """Evaluate and serialize evidence under an AAOS-owned policy snapshot."""

    findings: list[str] = []
    input_sanitization_failed = False
    unknown_local_offset = False
    try:
        unknown_local_offset = _record_uses_unknown_local_offset(candidate)
        _, secret_material_removed = _sanitize_value(candidate)
        record = sanitize_external_evidence_record(candidate)
        shape_changed = _record_shape_changed(candidate, record)
    except Exception:
        secret_material_removed = True
        shape_changed = True
        input_sanitization_failed = True
        record = sanitize_external_evidence_record({})

    try:
        normalized_policy, policy_findings = _normalize_trusted_policy(
            trusted_policy
        )
    except Exception:
        normalized_policy, _ = _normalize_trusted_policy(None)
        policy_findings = ["trusted_policy_processing_failed"]

    findings.extend(policy_findings)
    if not isinstance(candidate, dict):
        findings.append("admission_record_must_be_object")
    if input_sanitization_failed:
        findings.append("unsafe_input_rejected")
    if unknown_local_offset:
        findings.append("unknown_local_offset_not_allowed")
    if secret_material_removed:
        findings.append("secret_material_removed")
    if shape_changed and not secret_material_removed:
        findings.append("unexpected_or_unsafe_field_removed")

    findings.extend(_validate_required_metadata(record))

    expected_policy_snapshot = normalized_policy["admission_policy"]
    if (
        record.get("policy_version") != normalized_policy["policy_version"]
        or record.get("freshness_threshold_seconds")
        != normalized_policy["freshness_threshold_seconds"]
        or record.get("admission_policy") != expected_policy_snapshot
    ):
        findings.append("policy_snapshot_mismatch")

    connection_status = record["connection_status"]
    claimed_freshness = record["freshness_status"]
    claimed_extraction = record["extraction_status"]
    retrieval_succeeded = record["retrieval_succeeded"]

    if (connection_status == "ready") != retrieval_succeeded:
        findings.append("connection_retrieval_status_mismatch")

    derived_freshness, freshness_findings = derive_freshness_status(
        record,
        normalized_policy["freshness_threshold_seconds"],
    )
    findings.extend(freshness_findings)
    if claimed_freshness != derived_freshness:
        findings.append("freshness_status_mismatch")

    derived_extraction, extraction_findings = derive_extraction_status(record)
    findings.extend(extraction_findings)
    if claimed_extraction != derived_extraction:
        findings.append("extraction_status_mismatch")

    error_category = record["sanitized_error_category"]
    expected_source_failure = _derive_source_failure(
        connection_status,
        derived_freshness,
        error_category,
    )
    expected_extraction_failure = _derive_extraction_failure(
        record["extraction_attempted"],
        derived_extraction,
        expected_source_failure,
        retrieval_succeeded,
    )

    replay = record["replay_failure_classification"]
    claimed_source_failure = replay["source_failure"]
    claimed_extraction_failure = replay["extraction_failure"]
    model_failure = replay["model_failure"]
    governance_failure = replay["governance_failure"]

    if claimed_source_failure != expected_source_failure:
        findings.append("source_failure_classification_mismatch")
    if claimed_extraction_failure != expected_extraction_failure:
        findings.append("extraction_failure_classification_mismatch")

    findings.extend(
        _validate_error_category(
            connection_status,
            error_category,
            expected_source_failure,
            expected_extraction_failure,
            model_failure,
            governance_failure,
        )
    )

    policy_result = _policy_result(
        normalized_policy,
        connection_status,
        derived_freshness,
        derived_extraction,
        error_category,
    )
    claimed_result = record["admission_result"]
    if RESULT_SEVERITY[claimed_result] < RESULT_SEVERITY[policy_result]:
        findings.append("admission_result_more_permissive_than_policy")
        effective_result = "rejected"
    else:
        effective_result = claimed_result

    if effective_result == "degraded":
        findings.extend(
            _validate_degraded_storage(
                record,
                derived_freshness,
                derived_extraction,
            )
        )
        if (
            derived_freshness != "stale"
            and derived_extraction not in {"partial", "fallback_required"}
        ):
            findings.append("degraded_evidence_missing_dimension_reason")

    downstream_failure = model_failure != "none" or governance_failure != "none"
    expected_path_eligible = (
        effective_result == "verified" and not downstream_failure
    )
    expected_sealing_eligible = expected_path_eligible
    expected_storage = STORAGE_DISPOSITIONS[effective_result]

    if record["decision_path_eligible"] is not expected_path_eligible:
        findings.append("decision_path_eligibility_mismatch")
    if (
        record["decision_proof_sealing_eligible"]
        is not expected_sealing_eligible
    ):
        findings.append("decision_proof_sealing_eligibility_mismatch")
    if record["storage_disposition"] != expected_storage:
        findings.append("storage_disposition_mismatch")

    unique_findings = sorted(set(findings))
    admission_record_valid = not unique_findings
    effective_governance_failure = governance_failure
    if not admission_record_valid and effective_governance_failure == "none":
        effective_governance_failure = "governance_policy_failure"
    if not admission_record_valid:
        effective_result = "rejected"
        expected_path_eligible = False
        expected_sealing_eligible = False
        expected_storage = STORAGE_DISPOSITIONS["rejected"]

    safe_warnings = list(record["explicit_warnings"])
    if (
        not admission_record_valid
        and "admission_record_rejected_by_gate" not in safe_warnings
    ):
        safe_warnings.append("admission_record_rejected_by_gate")

    safe_replay = {
        "source_failure": expected_source_failure,
        "extraction_failure": expected_extraction_failure,
        "model_failure": model_failure,
        "governance_failure": effective_governance_failure,
    }

    storage_record = dict(record)
    storage_record["connection_status"] = connection_status
    storage_record["freshness_threshold_seconds"] = normalized_policy[
        "freshness_threshold_seconds"
    ]
    storage_record["freshness_status"] = derived_freshness
    storage_record["extraction_status"] = derived_extraction
    storage_record["admission_result"] = effective_result
    storage_record["policy_version"] = normalized_policy["policy_version"]
    storage_record["admission_policy"] = dict(expected_policy_snapshot)
    storage_record["explicit_warnings"] = safe_warnings
    storage_record["replay_failure_classification"] = safe_replay
    storage_record["decision_path_eligible"] = expected_path_eligible
    storage_record["decision_proof_sealing_eligible"] = (
        expected_sealing_eligible
    )
    storage_record["storage_disposition"] = expected_storage

    return {
        "external_evidence_admission_valid": admission_record_valid,
        "external_evidence_admission_invalid": not admission_record_valid,
        "connection_assessment": {
            "status": connection_status,
            "passed": connection_status == "ready" and retrieval_succeeded,
        },
        "freshness_assessment": {
            "status": derived_freshness,
            "passed": derived_freshness in {"current", "not_applicable"},
        },
        "extraction_assessment": {
            "status": derived_extraction,
            "passed": derived_extraction == "complete",
            "fallback_required": derived_extraction != "complete",
        },
        "admission_result": effective_result,
        "decision_path_eligible": expected_path_eligible,
        "decision_proof_sealing_eligible": expected_sealing_eligible,
        "degraded_storage_allowed": (
            admission_record_valid and effective_result == "degraded"
        ),
        "rejected_from_governed_decision_path": (
            effective_result == "rejected"
        ),
        "fail_closed": (
            effective_result != "verified" or not expected_path_eligible
        ),
        "storage_disposition": expected_storage,
        "explicit_warnings": safe_warnings,
        "replay_failure_classification": safe_replay,
        "admission_findings": unique_findings,
        "storage_record": storage_record,
    }


__all__ = [
    "ADMISSION_RESULTS",
    "CONNECTION_STATUSES",
    "EXTRACTION_STATUSES",
    "FRESHNESS_STATUSES",
    "RFC3339_TIMESTAMP_PATTERN",
    "SANITIZED_ERROR_CATEGORIES",
    "WARNING_CODES",
    "derive_extraction_status",
    "derive_freshness_status",
    "evaluate_external_evidence_admission",
    "sanitize_external_evidence_record",
]
