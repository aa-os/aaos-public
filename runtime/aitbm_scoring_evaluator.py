"""Deterministic checks for AITBM scoring evidence.

This evaluator is policy-neutral. It checks whether AITBM evidence stays inside
the AAOS L6 scoring adapter boundary; it does not decide admission, restriction,
risk acceptance, rollback, or final AAOS governance outcomes.
"""

from datetime import datetime, timezone


FORBIDDEN_ADAPTER_OUTPUTS = {
    "allow_final_decision",
    "restrict_final_decision",
    "risk_accepted",
    "waiver_granted",
    "approval_doctrine_changed",
    "identity_trust_changed",
    "rollback_executed",
    "governance_policy_rewritten",
    "final_release_authority_claimed",
}

HIGH_RISK_RATINGS = {"high", "critical"}
LOW_CONFIDENCE_VALUES = {"low"}
WEAK_CONTAINMENT_VALUES = {"weak"}
HIGH_TOOL_ACCESS_VALUES = {"high", "privileged"}
HIGH_DATA_SENSITIVITY_VALUES = {"high", "regulated"}


def parse_timestamp(value):
    """Parse a simple ISO-8601 timestamp without changing policy semantics."""
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def detect_forbidden_authority_claims(record):
    """Detect adapter outputs that would cross AAOS authority boundaries."""
    claims = set()

    def walk(value):
        if isinstance(value, dict):
            for key, nested in value.items():
                if key in FORBIDDEN_ADAPTER_OUTPUTS:
                    claims.add(key)
                walk(nested)
        elif isinstance(value, list):
            for nested in value:
                walk(nested)
        elif isinstance(value, str) and value in FORBIDDEN_ADAPTER_OUTPUTS:
            claims.add(value)

    walk(record)
    return sorted(claims)


def evidence_is_stale(record):
    """Check evidence age against the record's declared freshness window."""
    age = record.get("evidence_age_days")
    max_age = (record.get("score_snapshot") or {}).get("max_evidence_age_days")
    if not isinstance(age, int) or not isinstance(max_age, int):
        return False
    return age > max_age


def reassessment_missing_or_expired(record):
    """Check required reassessment date against the snapshot evaluation time."""
    reassessment_date = parse_timestamp(record.get("required_reassessment_date"))
    evaluation_time = parse_timestamp(
        (record.get("score_snapshot") or {}).get("evaluation_timestamp")
    )
    if reassessment_date is None:
        return True
    if evaluation_time is None:
        return False
    return reassessment_date < evaluation_time


def maturity_below_threshold(record):
    """Check maturity score against the record's declared threshold."""
    maturity = record.get("maturity_score") or {}
    value = maturity.get("value")
    threshold = maturity.get("threshold")
    if isinstance(value, (int, float)) and isinstance(threshold, (int, float)):
        return value < threshold
    return maturity.get("status") == "below_threshold"


def risk_is_high_or_critical(record):
    """Return whether the AITBM risk rating requires governance review."""
    rating = (record.get("risk_score") or {}).get("rating")
    return rating in HIGH_RISK_RATINGS


def advisor_review_should_be_required(record):
    """Return whether AITBM signals should invoke the advisor review hook."""
    return any(
        [
            evidence_is_stale(record),
            record.get("evidence_confidence") in LOW_CONFIDENCE_VALUES,
            risk_is_high_or_critical(record),
            maturity_below_threshold(record),
            record.get("containment_maturity") in WEAK_CONTAINMENT_VALUES,
            record.get("tool_access_level") in HIGH_TOOL_ACCESS_VALUES,
            record.get("data_sensitivity") in HIGH_DATA_SENSITIVITY_VALUES,
            reassessment_missing_or_expired(record),
            bool(detect_forbidden_authority_claims(record)),
        ]
    )


def evaluate_aitbm_scoring(record):
    """Return deterministic L6 scoring adapter findings for one evidence record."""
    violations = []
    recommendations = []

    forbidden_claims = detect_forbidden_authority_claims(record)
    if forbidden_claims:
        violations.append(
            {
                "code": "forbidden_authority_claim",
                "claims": forbidden_claims,
            }
        )
        recommendations.extend(
            ["recommendation_to_fail_closed", "advisor_review_required"]
        )

    if evidence_is_stale(record):
        violations.append({"code": "stale_evidence"})
        recommendations.extend(
            [
                "recommendation_to_review",
                "recommendation_to_retest",
                "advisor_review_required",
            ]
        )

    if record.get("evidence_confidence") in LOW_CONFIDENCE_VALUES:
        violations.append({"code": "low_evidence_confidence"})
        recommendations.extend(
            ["recommendation_to_review", "advisor_review_required"]
        )

    if risk_is_high_or_critical(record):
        violations.append(
            {
                "code": "high_or_critical_risk_score",
                "rating": record.get("risk_score", {}).get("rating"),
            }
        )
        recommendations.extend(
            [
                "recommendation_to_review",
                "recommendation_to_restrict",
                "human_approval_required",
                "advisor_review_required",
            ]
        )
        if evidence_is_stale(record) or record.get("risk_score", {}).get("rating") == "critical":
            recommendations.append("recommendation_to_fail_closed")

    if maturity_below_threshold(record):
        violations.append({"code": "maturity_below_threshold"})
        recommendations.extend(
            [
                "recommendation_to_review",
                "recommendation_to_retest",
                "recommendation_to_restrict",
                "advisor_review_required",
            ]
        )

    if record.get("containment_maturity") in WEAK_CONTAINMENT_VALUES:
        violations.append({"code": "weak_containment_maturity"})
        recommendations.extend(
            ["recommendation_to_review", "recommendation_to_restrict"]
        )

    if record.get("tool_access_level") in HIGH_TOOL_ACCESS_VALUES:
        violations.append({"code": "high_tool_access"})
        recommendations.extend(
            ["recommendation_to_restrict", "human_approval_required"]
        )

    if record.get("data_sensitivity") in HIGH_DATA_SENSITIVITY_VALUES:
        violations.append({"code": "high_data_sensitivity"})
        recommendations.extend(
            ["recommendation_to_restrict", "human_approval_required"]
        )

    if reassessment_missing_or_expired(record):
        violations.append({"code": "reassessment_missing_or_expired"})
        recommendations.extend(
            [
                "recommendation_to_review",
                "recommendation_to_retest",
                "advisor_review_required",
            ]
        )

    if advisor_review_should_be_required(record):
        advisor_invocation = record.get("advisor_invocation") or {}
        if advisor_invocation.get("required") is not True:
            violations.append({"code": "advisor_review_required"})
        recommendations.append("advisor_review_required")

    final_decision = (record.get("decision_gate_result") or {}).get("final_decision")
    if final_decision != "not_decided_by_adapter":
        violations.append({"code": "adapter_final_decision_claim"})
        recommendations.extend(
            ["recommendation_to_fail_closed", "advisor_review_required"]
        )

    unique_recommendations = list(dict.fromkeys(recommendations))
    status = "pass" if not violations else "review_required"

    return {
        "status": status,
        "violations": violations,
        "recommendations": unique_recommendations,
    }
