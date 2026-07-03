# Heretic Adversarial Specimen

Heretic is documented as a high-risk adversarial model-modification specimen for AAOS verification work.

It is not a trusted runtime, adapter, governance component, decision router, or production tool.

## Purpose

Heretic exists only to test whether AAOS can detect, contain, replay, and fail closed unsafe model behavior after safety-alignment degradation.

Supported test categories:

- alignment drift detection
- refusal degradation detection
- unsafe model provenance detection
- tool misuse precheck
- fail-closed simulation
- red-team scenario execution
- decision replay under compromised model behavior

## Layer Position

Allowed AAOS positions:

- L6 Verification Layer
- L3 Untrusted Local Model Runtime Specimen

Forbidden AAOS positions:

- L2 Control Plane
- L1 Policy & Identity Plane
- L0 Governance / Business Intent

## Containment Boundary

Heretic may only run as a contained specimen in an isolated local sandbox.

Required controls:

- no network access
- no write access
- no credential access
- no production tools
- no autonomous action execution
- no scheduler control
- read-only fixtures
- full trace logging
- replay-ready evidence
- fail-closed enforcement

Production tool access is blocked by default.

## Forbidden Use

Heretic must not be used for:

- production runtime execution
- autonomous action execution
- scheduler control
- workflow routing
- decision router authority
- approval-chain bypass
- policy-layer modification
- credential access
- network access
- production tool access

## Required Evidence

Every registry record must include:

- specimen identifier and type
- source model reference
- modification class
- high-risk and decensored risk tags
- allowed environment
- blocked capabilities
- containment controls
- provenance status
- trace logging requirement
- replay requirement
- fail-closed requirement
- advisor invocation
- test scenarios
- observed behavior
- comparison baseline
- rollback rule
- not-authority statement
- AAOS sovereignty statement

## Advisor Invocation

The Advisor Invocation Contract applies as a strategic governance review hook.

Advisor review is required when:

- the specimen is high-risk
- the specimen is decensored or alignment-removed
- provenance is unknown or unsafe
- containment controls are incomplete
- production tool access is requested
- network access is requested
- replay evidence is missing
- fail-closed behavior is missing
- policy or decision authority boundaries are ambiguous

Advisor review may recommend escalation, review, deferral, containment, or fail-closed handling. It does not own final release authority, risk appetite, approval doctrine, identity trust, decision routing, escalation semantics, audit closure, governance policy rewrite, or AAOS final decisions.

## Fail-Closed Rules

AAOS must fail closed when any of these conditions appear:

- containment boundary violation
- unsafe, unknown, or missing provenance
- missing trace logging
- missing replay-ready evidence
- missing fail-closed requirement
- missing rollback rule
- missing advisor invocation for a high-risk specimen
- network, write, credential, or production tool access allowed
- decision router or policy modification authority claimed

## Evaluator

`runtime/heretic_specimen_evaluator.py` performs deterministic checks for required high-risk and decensored tags, production environment claims, forbidden access, authority-boundary claims, trace logging, replay, fail-closed handling, rollback, and advisor invocation.

The evaluator emits review and containment recommendations only. It does not make final AAOS decisions.

## Example

`examples/heretic-adversarial-specimen/high-risk-decensored-model.json` provides a contained high-risk specimen registry record.

AAOS retains governance authority, policy authority, identity trust, decision routing, approval doctrine, fail-closed policy, rollback semantics, escalation semantics, risk appetite, and final decision authority.
