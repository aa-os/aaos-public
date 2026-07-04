# AAOS Cross-Adapter Regression Pack

The M8 cross-adapter regression pack checks that AAOS adapters, specimens, workspaces, and verification inputs preserve the AAOS governance boundary across releases.

The pack is evidence-producing only. It may detect inconsistencies, missing evidence, or authority-boundary violations. It must not approve, block, classify, roll back, seal Decision Proof, close audits, or make final governance judgments.

## Required Systems

The initial cross-adapter regression pack covers systems completed through M7:

- Cloudflare security-audit-skill
- Advisor Invocation Contract
- AITBM L6 Scoring Adapter
- Heretic Adversarial Specimen
- SkillOpt Governed Skill Evolution Layer
- codebase-memory-mcp Codebase Memory & Reconstruction Adapter
- open-tag Human-Agent Workspace Adapter

## Sovereignty Regression

The core regression verifies that external systems do not claim:

- `final_governance_authority`
- `approval_doctrine`
- `identity_trust_chain`
- `policy_authority`
- `decision_router_authority`
- `rollback_authority`
- `fail_closed_authority`
- `final_risk_classification`
- `decision_proof_sealing_authority`
- `audit_closure_authority`

If a system attempts to claim one of these authorities, AAOS should record an authority-boundary violation, require review, and recommend fail-closed handling when appropriate.

## Registry Pattern

The initial adapter registry is stored at:

- `registries/adapter-registry.yaml`

The registry is descriptive and auditable. It lists known AAOS systems, their layer mapping, allowed outputs, forbidden outputs, evidence schema paths, contract paths, examples, evaluators, tests, related issues, related PRs, release introduction, authority boundary statement, and AAOS retained authority statement.

The registry must not become:

- governance authority
- policy authority
- decision router
- rollback authority
- fail-closed authority
- Decision Proof sealing authority
- audit closure authority
- final governance authority

## Regression Evidence

Cross-adapter regression evidence is captured by:

- `schemas/cross-adapter-regression-evidence.schema.json`
- `examples/cross-adapter-regression/sovereignty-regression-pack.json`

The example regression pack verifies that every M1-M7 system is present and that all forbidden sovereignty claims remain absent.

## Governance Boundary

External tools remain governed signals, specimens, workspaces, or evidence sources. AAOS governs the decision.

AAOS retains purpose and business intent, risk appetite, approval doctrine, identity trust chain, policy authority, decision router logic, escalation semantics, fail-closed policy, rollback policy, final risk classification, Decision Proof sealing logic, audit final judgment, and final governance authority.
