# AAOS Release Governance Hardening

M8 adds a release governance consistency layer for AAOS Public after M1-M7 completion.

The hardening layer produces auditable evidence about release readiness. It does not approve releases, reject releases, accept risk, close audits, seal Decision Proof, or make final governance judgments.

## Scope

Release governance consistency checks cover:

- README version status
- milestone completion wording
- issue tracker closure
- PR merge status
- release tag presence
- release title consistency
- release body consistency
- next-phase declaration
- related issue linkage
- governance boundary preservation

AAOS should be able to ask:

- Does README say the same milestone is complete?
- Is the tracker issue closed?
- Is the closing PR merged?
- Does the release tag exist?
- Does the release title match README?
- Does the release body preserve the governance boundary?
- Does the next phase point to the correct milestone?

## Evidence Model

Release consistency evidence is captured by:

- `schemas/release-governance-consistency.schema.json`
- `examples/release-governance/v0.6.0-consistency-check.json`

The evidence record is intended to be replayable. It should identify the release version, milestone, tracker issue, closing PRs, release tag, title/body checks, next phase, related issue linkage, and governance boundary preservation.

## Evaluator Behavior

The deterministic evaluator may detect:

- missing README version
- milestone completion mismatch
- tracker issue not closed
- closing PR not merged
- missing release tag
- release title mismatch
- release body missing governance boundary
- next-phase mismatch
- related issue linkage gaps
- forbidden authority claims

Evaluator outputs are evidence only. Allowed outputs include:

- `release_consistency_passed`
- `release_consistency_failed`
- `regression_findings`
- `missing_evidence`
- `authority_boundary_violation`
- `review_required`
- `escalation_required`
- `fail_closed_recommended`

## Forbidden Authority

Release governance checks, CI checks, registries, regression packs, and deterministic evaluators must not emit:

- `release_approved`
- `release_rejected_by_evaluator`
- `risk_accepted`
- `waiver_granted`
- `approval_doctrine_changed`
- `identity_trust_changed`
- `policy_authority_changed`
- `decision_route_changed`
- `rollback_decision`
- `fail_closed_executed`
- `decision_proof_sealed`
- `audit_closed`
- `final_governance_judgment`

## Governance Boundary

M8 hardens the AAOS governance surface. It must not turn adapters, registries, release checklists, CI checks, or regression packs into final authorities.

External systems remain governed evidence sources, specimens, workspaces, or verification inputs.

AAOS retains purpose and business intent, risk appetite, approval doctrine, identity trust chain, policy authority, decision router logic, escalation semantics, fail-closed policy, rollback policy, final risk classification, Decision Proof sealing logic, audit final judgment, and final governance authority.
