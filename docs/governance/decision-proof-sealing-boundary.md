# AAOS Decision Proof Sealing Boundary

Decision Proof sealing is the AAOS-owned act of finalizing a Decision Proof after evidence has been captured, replayed, checked, reviewed, and found eligible.

M10 separates evidence readiness from sealing authority. Adapters, runtime replay packets, release proof automation, governance CI checks, deterministic evaluators, registries, public integration packs, external tools, and external consumers may produce or consume evidence. They must not seal Decision Proof or claim final governance authority.

## Boundary Layers

Decision Proof sealing separates:

- captured evidence
- replayable evidence
- evaluator findings
- release proof evidence
- governance CI findings
- human review state
- sealing eligibility
- final sealing authority

Evidence may be captured by adapters, replayed by runtime replay packets, checked by deterministic evaluators, prepared by release proof automation, and reviewed by humans or advisors.

Final Decision Proof sealing remains AAOS-owned.

## Allowed Sealing States

- `unsealed`
- `replay_ready`
- `evidence_complete`
- `human_review_required`
- `advisor_review_required`
- `sealing_eligible`
- `sealed_by_aaos`
- `sealing_rejected_by_aaos`
- `sealing_deferred`
- `sealing_blocked`

## Forbidden Sealing States

- `sealed_by_adapter`
- `sealed_by_ci`
- `sealed_by_evaluator`
- `sealed_by_runtime_replay`
- `sealed_by_release_automation`
- `sealed_by_registry`
- `sealed_by_external_system`
- `audit_closed_by_adapter`
- `final_governance_judgment_by_external_system`

## Required Distinctions

AAOS must distinguish between:

- evidence readiness
- sealing eligibility
- actual sealing
- audit closure
- final governance judgment

Evidence readiness means the necessary artifacts exist and can be checked.

Sealing eligibility means AAOS may consider sealing after policy, authority, review, and traceability gates are satisfied.

Actual sealing means AAOS has performed the Decision Proof sealing act.

Audit closure and final governance judgment remain separate AAOS-owned governance outcomes.

## Boundary

Decision Proof sealing remains AAOS-owned.

Adapters, external tools, runtime replay packets, release proof automation, governance CI checks, deterministic evaluators, registries, public integration packs, and external consumers may produce or consume evidence.

They must not become governance authority, policy authority, identity authority, approval authority, release authority, decision router, rollback authority, fail-closed authority, final risk classification authority, Decision Proof sealing authority, audit closure authority, or final governance authority.

AAOS retains purpose and business intent, risk appetite, approval doctrine, identity trust chain, policy authority, decision router logic, escalation semantics, fail-closed policy, rollback policy, final risk classification, Decision Proof sealing logic, audit final judgment, and final governance authority.
