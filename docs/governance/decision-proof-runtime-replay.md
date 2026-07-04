# AAOS Decision Proof Runtime Replay

Decision Proof runtime replay reconstructs what happened around an AAOS-governed decision.

Replay packets bind the decision context, adapter events, runtime events, evaluator findings, rollback surface, replay target, and replay result into auditable evidence. They do not approve, block, classify, roll back, seal Decision Proof, close audits, or make final governance judgments.

## Purpose

The runtime replay packet lets AAOS ask:

- What decision was being executed?
- Who or what acted?
- Which authority source allowed the work to proceed?
- Which tools were allowed?
- Was approval required and present?
- Which adapters or runtime components produced events?
- Which evidence was captured?
- What did deterministic evaluators report?
- What rollback or escalation surface existed?
- Can the decision be replayed?
- Was Decision Proof sealing preserved as an AAOS-owned boundary?

## Packet Contents

The Decision Proof Runtime Replay Packet schema requires:

- `decision_id`
- `intent`
- `actor`
- `authority_source`
- `risk_class`
- `allowed_tools`
- `approval_required`
- `approval_state`
- `adapter_events`
- `runtime_events`
- `execution_trace`
- `evidence_refs`
- `evaluator_outputs`
- `regression_findings`
- `rollback_plan`
- `rollback_surface`
- `replay_target`
- `replay_steps`
- `replay_result`
- `sealing_status`
- `not_authority_statement`
- `sovereignty_statement`

## Replay Sources

M9 replay packets may reference evidence produced by:

- Cloudflare security-audit-skill
- Advisor Invocation Contract
- AITBM L6 Scoring Adapter
- Heretic Adversarial Specimen
- SkillOpt Governed Skill Evolution Layer
- codebase-memory-mcp Codebase Memory & Reconstruction Adapter
- open-tag Human-Agent Workspace Adapter
- M8 Release Governance Evaluator
- M8 Adapter Registry

## Boundary

Runtime replay reconstructs what happened.

It may produce evidence for review, escalation, replay, rollback-surface inspection, fail-closed recommendation, or release proof automation.

It must not become governance authority, policy authority, identity authority, approval authority, release authority, decision router, rollback authority, fail-closed authority, final risk classification authority, Decision Proof sealing authority, audit closure authority, or final governance authority.

AAOS retains purpose and business intent, risk appetite, approval doctrine, identity trust chain, policy authority, decision router logic, escalation semantics, fail-closed policy, rollback policy, final risk classification, Decision Proof sealing logic, audit final judgment, and final governance authority.
