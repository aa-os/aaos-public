# AAOS Governance CI Expansion

Governance CI expands deterministic checks over schemas, examples, replay packets, release proof evidence, adapter registry entries, and authority-boundary preservation.

This first M9 PR documents the CI expansion pattern and adds deterministic evaluator coverage. It does not add a workflow file yet. A workflow can be added after the checks are stable across release proof and runtime replay examples.

## Candidate Checks

Governance CI should evaluate:

- schema validity
- example validity
- evaluator forbidden-output detection
- adapter registry required fields
- release proof consistency
- replay packet completeness
- forbidden authority claim detection
- Decision Proof sealing boundary preservation

## Evidence Sources

Governance CI may read:

- `schemas/decision-proof-runtime-replay-packet.schema.json`
- `schemas/release-proof-automation.schema.json`
- `examples/decision-proof-runtime-replay/*.json`
- `examples/release-proof-automation/*.json`
- `registries/adapter-registry.yaml`
- deterministic evaluator test results

## Allowed Outputs

Governance CI checks may produce:

- `replay_packet_valid`
- `replay_packet_invalid`
- `replay_findings`
- `missing_evidence`
- `authority_boundary_violation`
- `release_proof_consistency_passed`
- `release_proof_consistency_failed`
- `review_required`
- `escalation_required`
- `fail_closed_recommended`

## Forbidden Outputs

Governance CI checks must not produce:

- `release_approved`
- `release_rejected_by_evaluator`
- `risk_accepted`
- `waiver_granted`
- `approval_doctrine_changed`
- `identity_trust_changed`
- `policy_authority_changed`
- `decision_route_changed`
- `rollback_decision`
- `rollback_executed`
- `fail_closed_executed`
- `decision_proof_sealed`
- `audit_closed`
- `final_governance_judgment`

## Boundary

Governance CI checks evidence consistency.

CI may detect missing evidence, incomplete replay packets, stale registry entries, forbidden authority claims, or Decision Proof sealing boundary violations.

CI must not approve, block, classify, roll back, publish releases, seal Decision Proof, close audits, or make final governance judgments.

AAOS retains purpose and business intent, risk appetite, approval doctrine, identity trust chain, policy authority, decision router logic, escalation semantics, fail-closed policy, rollback policy, final risk classification, Decision Proof sealing logic, audit final judgment, and final governance authority.
