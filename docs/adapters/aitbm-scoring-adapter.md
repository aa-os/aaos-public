# AITBM L6 Scoring Adapter

This adapter treats AITBM as an AAOS L6 AI Trust Benchmarking / Maturity Scoring Adapter.

AITBM provides external AI security maturity scoring, risk scoring, evidence freshness checks, confidence signals, containment maturity signals, reassessment triggers, and verification gate input.

## AAOS Layer Position

AITBM maps to:

- L6 Verification & Audit
- L5 Decision Proof / Evidence

It must not map to:

- L0 Governance / Business Intent
- L1 Policy & Identity Plane
- L2 Control Plane
- model runtime
- identity authority
- rollback engine

## Governance Boundary

AITBM is an external scoring and verification signal adapter.

It may produce:

- risk_score
- maturity_score
- evidence_freshness_signal
- evidence_confidence_signal
- containment_maturity_signal
- deployment_context_multiplier
- reassessment_required
- verification_gate_input
- recommendation_to_review
- recommendation_to_restrict
- recommendation_to_retest
- recommendation_to_fail_closed
- advisor_review_required

It must not produce:

- allow_final_decision
- restrict_final_decision
- risk_accepted
- waiver_granted
- approval_doctrine_changed
- identity_trust_changed
- rollback_executed
- governance_policy_rewritten
- final_release_authority_claimed

## AAOS Retained Authority

AITBM output is evidence, not authority.

AAOS retains:

- risk appetite
- decision thresholds
- approval doctrine
- fail-closed rules
- rollback semantics
- escalation policy
- identity trust chain
- final decision authority

## Evidence Fields

AITBM evidence records should include:

- score_snapshot
- assessment_date
- evidence_age_days
- evidence_confidence
- deployment_context
- assessor_assumptions
- required_reassessment_date
- decision_gate_result
- maturity_score
- risk_score
- containment_maturity
- autonomy_level
- tool_access_level
- data_sensitivity
- reassessment_trigger

## Review And Reassessment

The adapter should recommend review, reassessment, restriction, human approval, or fail-closed handling when:

- evidence is stale
- confidence is low
- risk score is high or critical
- maturity score is below threshold
- containment maturity is weak
- tool access level is high
- data sensitivity is high
- reassessment date is missing or expired
- adapter output appears to cross an authority boundary

These are recommendations and gate inputs. AAOS decides final admission, restriction, risk acceptance, rollback, release, and fail-closed outcomes.

## Advisor Invocation

AITBM should trigger advisor review under the Advisor Invocation Contract when:

- evidence is stale
- confidence is low
- risk score is high or critical
- maturity score is below threshold
- containment maturity is weak
- tool access level is high
- data sensitivity is high
- reassessment date is missing or expired
- adapter output appears to cross an authority boundary

Advisor review is a governance review hook. It may recommend escalation, review, deferral, containment, reassessment, or fail-closed handling.

Advisor review does not own final release authority, risk appetite, approval doctrine, identity trust, decision routing, escalation semantics, audit closure, rollback semantics, or governance policy rewrite.

## Deterministic Evaluator

`runtime/aitbm_scoring_evaluator.py` performs policy-neutral checks for:

- forbidden authority claims
- stale evidence
- low evidence confidence
- high or critical risk score
- maturity below threshold
- weak containment maturity
- high tool access
- high data sensitivity
- missing or expired reassessment date
- missing advisor invocation when required
- adapter final decision claims

The evaluator returns findings and recommendations only. It does not decide AAOS outcomes.

## Example

See `examples/aitbm-scoring/high-risk-stale-evidence.json`.

The example shows stale, low-confidence, high-risk scoring evidence below the maturity threshold. It recommends review, reassessment, restriction, human approval, fail-closed handling, and advisor review, but AAOS retains final authority.

## Status

- candidate
