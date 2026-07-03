# AAOS Skill Governance Lab

SkillOpt is an AAOS governed skill evolution layer.

It produces versioned, testable, replayable, and auditable skill artifacts. It does not approve deployment, accept risk, rewrite policy, change identity trust, execute rollback, route decisions, or close audits.

## Layer Position

SkillOpt belongs in:

- L4.5 Skill Optimization Layer

SkillOpt outputs feed:

- L6 Verification / Audit Layer
- L5 Memory & Reconstruction Graph
- L4 Tool / Data Execution Substrate
- L3 Model Runtime

SkillOpt must not own:

- L0 Governance / Business Intent
- L1 Policy & Identity Plane
- L2 Control Plane
- final deployment authority
- decision router authority

## Allowed Outputs

SkillOpt may produce:

- best skill artifacts
- skill snapshots
- accepted edits
- rejected edits
- validation scores
- validation results
- rollout traces
- history logs
- runtime state
- optimization recommendations
- replay datasets
- regression signals

## Forbidden Outputs

SkillOpt must not produce or claim:

- deployment approval
- deployment rejection by SkillOpt
- risk acceptance
- waiver grants
- approval doctrine changes
- identity trust changes
- rollback execution
- decision route changes
- governance policy rewrites
- audit closure
- final governance judgment

## Governed Artifact Requirements

Every governed skill artifact must include lineage, accepted edits, rejected edits, validation scores, validation results, regression checks, tool-use impact, data-access impact, authority impact, autonomy impact, safety impact, policy precheck, deployment gate status, rollback plan, replay trace references, evidence hashes, advisor invocation, AAOS decision state, and sovereignty statements.

Rollback readiness, replay-ready traces, validation evidence, rejected edit history, and deployment-gate status are required before AAOS can consider deployment approval.

## Deployment Gate

The deployment gate records policy-bound checks for:

- policy violation
- tool misuse risk
- unsafe instruction
- overbroad autonomy
- missing fallback
- rollback readiness
- trace completeness
- replay readiness
- authority boundary change
- data access expansion
- missing AAOS deployment approval

Passing validation does not deploy a skill. AAOS owns deployment approval.

## Advisor Invocation

The Advisor Invocation Contract applies as a governance review hook.

Advisor review is required when:

- a skill changes authority boundaries
- a skill expands tool use
- a skill expands data access
- a skill increases autonomy
- a skill affects safety behavior
- validation improves but policy risk increases
- rollback plans are missing
- replay traces are missing
- deployment gates fail or are incomplete
- SkillOpt output appears to claim AAOS authority

Advisor review may recommend review, challenge, deferral, restriction, retesting, rollback readiness, or fail-closed handling. It does not own deployment approval, risk thresholds, identity trust, decision routing, rollback policy, audit final judgment, or final governance authority.

## Deterministic Evaluator

`runtime/skillopt_governance_evaluator.py` checks for forbidden authority claims, missing rollback plans, missing replay traces, missing validation evidence, missing rejected edit history, missing deployment gates, and missing advisor invocation for governance-sensitive changes.

The evaluator emits review and readiness recommendations only. It does not make AAOS deployment, rollback, risk acceptance, audit closure, or final governance decisions.

## AAOS Sovereignty

AAOS governs how optimized skills are accepted, rejected, deployed, rolled back, replayed, challenged, and finally judged.
