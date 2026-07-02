"""Deterministic checks for Cloudflare security audit evidence.

This evaluator is intentionally small and policy-neutral. It verifies whether
an adapter output stays inside the AAOS L6 verification boundary; it does not
decide release approval, risk acceptance, waiver approval, or governance policy.
"""

FORBIDDEN_ADAPTER_OUTPUTS = {
    "release_approved",
    "release_rejected_by_adapter",
    "risk_accepted",
    "waiver_granted",
    "approval_doctrine_changed",
    "identity_trust_changed",
    "aaos_policy_rewritten",
    "audit_closed_by_adapter",
}

HIGH_SEVERITIES = {"high", "critical"}


def finding_ids_with_high_or_critical_severity(record):
    """Return finding IDs that require release-gate and human-review signals."""
    finding_ids = []
    for finding in record.get("security_findings", []):
        if finding.get("severity") in HIGH_SEVERITIES:
            finding_ids.append(finding.get("finding_id"))
    return [finding_id for finding_id in finding_ids if finding_id]


def has_replay_evidence(record):
    """Check replay evidence without interpreting governance thresholds."""
    replay_packet = record.get("replay_packet") or {}
    return (
        replay_packet.get("replay_ready") is True
        and bool(replay_packet.get("trace_id"))
        and bool(replay_packet.get("input_refs"))
        and bool(replay_packet.get("evidence_hashes"))
        and bool(replay_packet.get("replay_instructions_ref"))
    )


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


def evaluate_cloudflare_security_audit(record):
    """Return deterministic L6 verification findings for one evidence record."""
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
        recommendations.append("fail_closed_recommended")

    high_or_critical_findings = finding_ids_with_high_or_critical_severity(record)
    if high_or_critical_findings:
        release_gate = record.get("release_gate") or {}
        handoff = record.get("human_review_handoff") or {}
        if release_gate.get("gate_triggered") is not True:
            violations.append(
                {
                    "code": "release_gate_required",
                    "finding_ids": high_or_critical_findings,
                }
            )
        if release_gate.get("adapter_recommendation") not in {
            "block_or_escalate",
            "fail_closed_recommended",
            "human_review_required",
        }:
            violations.append(
                {
                    "code": "release_gate_recommendation_required",
                    "finding_ids": high_or_critical_findings,
                }
            )
        if handoff.get("required") is not True:
            violations.append(
                {
                    "code": "human_review_required",
                    "finding_ids": high_or_critical_findings,
                }
            )
        recommendations.extend(["release_gate_triggered", "human_review_required"])

    if not has_replay_evidence(record):
        violations.append({"code": "missing_replay_evidence"})
        recommendations.append("fail_closed_recommended")

    if record.get("release_gate", {}).get("final_release_decision") != "not_decided_by_adapter":
        violations.append({"code": "adapter_final_release_decision_claim"})
        recommendations.append("fail_closed_recommended")

    unique_recommendations = list(dict.fromkeys(recommendations))
    status = "pass" if not violations else "review_required"

    return {
        "status": status,
        "violations": violations,
        "recommendations": unique_recommendations,
    }
