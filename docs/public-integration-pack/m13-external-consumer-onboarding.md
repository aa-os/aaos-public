# M13 External Consumer Onboarding Documentation

Status: active work in progress, not released.
Tracker: Refs #176.
Target future release path: v0.12.0, not released.

This document explains how an external consumer may connect to AAOS evidence artifacts without becoming a governance authority. It is guidance and evidence structure only.

## External Consumer Role

An external consumer may read, reference, replay, inspect, report on, and preserve linkage to AAOS evidence artifacts according to artifact status and registry policy. A consumer may surface review requirements, escalation requirements, or fail-closed recommendations for AAOS review.

An external consumer must not approve consumers, approve registry entries, approve execution, accept risk, approve releases, execute rollback, execute fail-closed, seal Decision Proof, close audits, grant waivers, transfer authority, or make final governance judgments.

## Registry Inclusion Boundary

Registry inclusion identifies a consumer entry and its evidence-facing role. It records consumer identity, consumed artifact types, allowed consumption actions, prohibited authority claims, provenance, and reviewer handoff expectations.

External consumer onboarding documentation does not grant authority.

Registry inclusion is not approval.

## Evidence Consumption Boundary

External consumers may consume AAOS artifacts only according to the artifact status and the registry entry. Sealed artifacts may be consumed as AAOS-sealed artifacts. Non-sealed artifacts may be consumed only as non-sealed evidence.

Evidence consumption is not approval.

evidence_complete is not sealed.

replay_ready is not sealed.

## Runtime Approval Evidence Boundary

Runtime approval evidence may show whether a runtime gate observed, advised, or enforced approval evidence before a gated action was released. It is evidence for AAOS review.

Runtime approval evidence is not execution approval.

## Registry Drift Review Boundary

Registry drift detection may compare a current consumer entry with a baseline entry and report identity, role, artifact scope, action, compatibility, provenance, release proof, or authority-boundary drift.

Registry drift detection is not approval.

## Authority-Boundary Regression Boundary

Authority-boundary regression fixtures may detect authority escalation patterns across registry entries, drift detection, runtime approval evidence, integration CI checks, traceability artifacts, onboarding documents, README status entries, or external evidence consumers.

Authority-boundary findings may require review, escalation, or fail-closed recommendation handling, but they do not execute authority actions.

## Operational Readiness Review Boundary

Operational readiness review may report whether M13 hardening artifacts are ready for human review. It does not approve consumers, approve execution, accept risk, seal Decision Proof, close audits, complete M13, or release v0.12.0.

Operational readiness is not approval.

ready_for_review is not approval.

## Onboarding Checklist

1. Identify the external consumer and registry entry.
2. Record consumer role and consumed artifact types.
3. Record allowed evidence consumption actions.
4. Record prohibited authority claims.
5. Link runtime approval evidence from #177 when relevant.
6. Link registry drift detection from #178.
7. Link authority-boundary regression fixtures from #194.
8. Link operational readiness checklist evidence from #195.
9. Confirm release proof linkage is future-only for v0.12.0.
10. Prepare reviewer handoff for AAOS review.

onboarding_complete is not approved.

## Required Evidence Fields

External consumer onboarding records should include:

- consumer_id
- consumer_name
- consumer_role
- registry_entry_id
- consumed_artifact_types
- allowed_consumption_actions
- forbidden_authority_actions
- evidence_artifact_refs
- artifact_status
- sealed_status
- runtime_approval_evidence_ref
- registry_drift_review_ref
- authority_boundary_regression_ref
- operational_readiness_ref
- release_proof_linkage_ref
- reviewer_handoff
- aaos_retained_authority_statement

## Prohibited Claims

External consumer onboarding documentation must not claim or imply:

- consumer_approved
- registry_entry_approved
- onboarding_approved
- execution_approved_by_documentation
- release_approved
- risk_accepted
- decision_proof_sealed
- sealed_by_documentation
- audit_closed
- waiver_granted
- final_governance_judgment
- authority_transferred
- v0_12_0_released
- m13_complete
- closes_176

## Fail-Closed And Escalation Handling

Onboarding documentation may surface review_required, escalation_required, or fail_closed_recommended when evidence is incomplete, inconsistent, drifted, or authority-boundary unsafe.

not_ready is not fail_closed_executed.

fail_closed_recommended is not fail_closed_executed.

## Reviewer Handoff

Reviewer handoff should provide links to the consumer registry entry, evidence artifacts, runtime approval evidence, registry drift review, authority-boundary regression fixtures, operational readiness checklist, and future-only release proof linkage. The reviewer remains responsible for AAOS governance review.

## Future-Only v0.12.0 Release Path

v0.12.0 is a future target release and must not be treated as released. Release proof linkage is evidence linkage only.

Release proof linkage is not release approval.

## M13 Active-Work Status

M13 is active work and is not complete. This onboarding documentation must not declare M13 complete and must not close #176.

## AAOS-Owned Decision Proof Sealing

Decision Proof sealing remains AAOS-owned.

## AAOS Final Governance Authority

AAOS retains purpose and business intent, risk appetite, approval doctrine, identity trust chain, policy authority, decision router logic, escalation semantics, fail-closed policy, rollback policy, final risk classification, Decision Proof sealing logic, audit final judgment, release authority, and final governance authority.

AAOS remains the decision sovereignty layer.

onboarding documentation must not close audits.

onboarding documentation must not grant waivers.

onboarding documentation must not make final governance judgments.
