# Cloudflare Security Audit L6 Verification Adapter

This adapter treats Cloudflare security-audit-skill as an AAOS L6 security verification layer.

It converts security audit workflow output into structured evidence, risk findings, release gate signals, human-review handoff records, and replay-ready audit packets.

## AAOS Layer Position

Cloudflare security-audit-skill maps to:

- L6 Verification & Audit

It must not map to:

- L0 Governance / Business Intent
- L1 Policy & Identity Plane
- L2 Control Plane

## Governance Boundary

Cloudflare security-audit-skill is a verification adapter only.

It may verify:

- security evidence
- audit traces
- risk findings
- release readiness signals
- escalation requirements
- replay readiness

It must not own:

- business intent
- risk appetite
- approval doctrine
- identity trust chain
- decision router logic
- escalation semantics
- final release authority
- production fail-closed policy

## Authority Boundary

Security audit output is evidence, not authority.

The adapter may say:

- a high-severity finding exists
- evidence is missing or non-replayable
- a release gate should be triggered
- human review is required
- fail-closed behavior is recommended

The adapter must not say:

- release is approved
- release is finally rejected by the adapter
- business risk is accepted
- a waiver is granted
- identity trust rules are changed
- AAOS policy is rewritten
- audit is closed

## Release Gate Behavior

Release gate behavior is recommendation or trigger only.

A release gate signal from this adapter means security verification found a condition that should enter AAOS governance review. It does not mean the adapter has final release authority.

When high or critical findings exist, the adapter should emit:

- release_gate_triggered
- human_review_required
- remediation_or_exception_required

AAOS governance and release authority decide the final release outcome, exception approval, escalation meaning, and fail-closed policy.

## Fail-Closed Conditions

The adapter should emit a fail-closed recommendation when:

- security audit evidence is missing or non-replayable
- high or critical findings lack remediation or recorded exception evidence
- evidence is not bound to repository, branch, commit, build, and artifact
- audit trace lacks timestamp, skill version, or input hashes
- adapter output is treated as final release approval
- waiver or risk acceptance is claimed without authority binding
- absence of scanner output is treated as a clean security state

The adapter reports these conditions. AAOS governance owns the final fail-closed rule and threshold.

## Human-Review Handoff

Human review is required when:

- high or critical findings are present
- a release gate is triggered
- fail-closed recommendation is emitted
- remediation or exception evidence is missing
- authority boundary confusion is detected

The handoff record should include:

- reviewer role
- handoff reason
- triggering findings
- release gate signal
- required authority
- replay packet reference

## Replay-Ready Audit Evidence

Evidence should be replay-ready before it is admitted into AAOS governance review.

Required replay properties include:

- audit trace ID
- skill version
- input references
- evidence hashes
- finding IDs
- verification timestamp
- release gate signal
- human-review handoff
- adapter decision boundary

## Risk-to-Governance Mapping

The adapter maps security risk into governance review inputs:

| Security signal | Governance mapping |
| --- | --- |
| high_or_critical_security_finding | human_review_required, release_gate_triggered, remediation_or_exception_required |
| missing_replay_evidence | evidence_sufficiency_failure, fail_closed_recommended |
| authority_boundary_confusion | governance_boundary_violation, escalation_required |
| stale_security_audit | verification_freshness_failure, revalidation_required |

These mappings are routing evidence for AAOS governance. They do not define business intent, risk appetite, escalation semantics, or final release decisions.

## Example

See `examples/cloudflare-security-audit/release-gate-triggered.json`.

The example shows a release gate triggered by a high-severity security finding. The release state is blocked pending AAOS governance review, but the adapter does not finally decide release approval, rejection, risk acceptance, exception approval, or fail-closed policy.

## Status

- candidate
