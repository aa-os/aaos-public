# AAOS Public

AAOS 是一套治理優先的 AI Agent 操作層。

本公開版本提供規格、範例、模式、插件介面與監管邊界說明，協助開發者理解如何建立可驗證、可稽核、可追溯、受政策約束的 AI Agent 工作流。

## 核心理念

AAOS 不把模型輸出視為最終權威。

AI action 是否有效，取決於它是否通過身份、政策、證據、驗證與稽核閘門。
## Documents

- [Governance Boundary Map](docs/governance-boundary-map.md)
- [Architecture L0–L6](docs/architecture-l0-l6.md)


## Public Scope

本 repo 預計公開：

- 架構說明
- Governance Boundary Map
- Decision Contract 範例
- Governance Verdict 範例
- Plugin SDK 介面設計
- Audit Evidence 格式
- RFC 文件

## Not Public

本 repo 不公開：

- decision router 核心邏輯
- risk threshold
- private registry
- approval doctrine
- restore map
- dependency graph
- production governance gate
  
## Bootstrap Status

AAOS Public bootstrap completed its first two milestones.

- M1 — Governance Radar Bootstrap Artifacts: complete
- M2 — First Governance Adapter Packs: complete

M1 established the public Governance Radar foundation:

- HUBEO Governance Radar documentation
- external signal admission documentation
- adapter intake taxonomy
- radar node schema
- adapter intake issue template
- sample radar nodes

M2 established the first governance adapter skeleton family:

- ds4 local runtime adapter
- ECC Tools agent workflow adapter
- Threatrix supply-chain evidence adapter
- MiniMind local model runtime adapter
- exo distributed local inference adapter

The repository now has the first public AAOS external signal admission path:

external source → governed signal → radar node → adapter issue → governance adapter skeleton

AAOS Public v0.1.0 is now released: Governance Radar Bootstrap is complete. External tools, runtimes, scanners, and agent frameworks now have a public admission path into AAOS as governed signals, not authorities.
## Releases

- v0.1.0 — Governance Radar Bootstrap
- v0.2.0 — Contract & Schema Hardening
- v0.3.0 — L6 Security Verification & Deterministic CI Gates
- v0.4.0 — M5 Evaluator Expansion, Adapter Regression Packs, and Governed Specimens
- v0.5.0 — M6 Decision Proof Reconstruction Layer and Codebase Memory Adapter
- v0.6.0 — M7 Human-Agent Control Surface and Workspace Adapter
- v0.7.0 — M8 Release Governance Hardening and Cross-Adapter Regression

Current baseline:

AAOS Public now includes the Governance Radar foundation, first adapter skeletons, contract/schema hardening, Cloudflare L6 security verification, deterministic evaluator tests, CI gate coverage, the M5 governed adapter/specimen/evaluator pattern, the M6 software Decision Proof reconstruction workflow, the M7 Human-Agent Control Surface pattern, and the M8 release governance hardening pattern.

v0.7.0 adds AAOS Release Governance Hardening.

v0.7.0 introduces the first Cross-Adapter Regression Pack.

v0.7.0 introduces an initial Adapter Registry pattern.

Release governance checks, regression packs, adapter registries, CI checks, and deterministic evaluators remain evidence-producing systems, not authorities.

## Current Status

M1, M2, M3, M4, M5, M6, M7, and M8 are complete.

M5 completed:

- #28 Advisor Invocation Contract
- #29 AITBM L6 Scoring Adapter
- #30 Heretic Adversarial Specimen
- #33 SkillOpt Governed Skill Evolution Layer

M6 completed:

- #62 M6: Decision Proof Reconstruction Layer and Codebase Memory Adapter
- #32 codebase-memory-mcp Codebase Memory & Reconstruction Adapter

M7 completed:

- #68 M7: Human-Agent Control Surface and Workspace Adapter
- #31 open-tag Human-Agent Workspace Adapter

M8 completed:

- #80 M8: Release Governance Hardening and Cross-Adapter Regression
- #86 Add M8 release governance and cross-adapter regression pack

AAOS Public now has:

- external signal admission documentation
- radar node schema
- adapter intake template
- sample radar nodes
- first adapter skeletons
- ds4 contract/schema hardening
- Threatrix contract/schema hardening
- Cloudflare security-audit-skill L6 security verification adapter
- deterministic evaluator tests
- GitHub Actions CI gate for Cloudflare security audit evidence
- Advisor Invocation Contract
- AITBM L6 Scoring Adapter
- Heretic Adversarial Specimen handling
- SkillOpt Governed Skill Evolution Layer
- Codebase Memory & Reconstruction Adapter
- codebase graph evidence schema
- patch impact / blast-radius evidence schema
- software Decision Proof reconstruction example
- open-tag Human-Agent Workspace Adapter
- human-agent activity evidence schema
- Decision Contract injection map
- workspace activity replay example
- responsibility workflow specimen
- AAOS Release Governance Hardening
- Cross-Adapter Regression Pack
- initial Adapter Registry pattern
- release governance consistency evidence
- deterministic release governance evaluator coverage

## M5 Additions

### Advisor Invocation Contract (#28)

Purpose: Defines when AAOS requires strategic governance review before adapter admission, release gating, fail-closed override, high-risk specimen handling, stale evidence handling, or authority-boundary escalation.

### AITBM L6 Scoring Adapter (#29)

Purpose: Adds AI trust benchmarking / maturity scoring as an external L6 scoring signal for risk score, maturity score, evidence freshness, confidence, reassessment, and admission-control input.

Boundary: AITBM is not governance authority, model runtime, identity authority, rollback engine, or final decision authority.

### Heretic Adversarial Specimen (#30)

Purpose: Adds high-risk adversarial model-modification specimen handling for alignment drift detection, refusal degradation detection, unsafe provenance detection, tool misuse precheck, fail-closed simulation, red-team scenarios, and replay under compromised model behavior.

Boundary: Heretic is not a trusted runtime, adapter, governance component, decision router, or production tool.

### SkillOpt Governed Skill Evolution Layer (#33)

Purpose: Adds governed skill artifact, validation evidence, rollback readiness, replay trace, and deployment-gate structure for self-improving or optimized skills.

Boundary: SkillOpt may produce optimized skill artifacts and validation evidence, but AAOS owns deployment approval, rollback policy, risk thresholds, identity trust, audit final judgment, and final governance authority.

## M6 Additions

### Codebase Memory & Reconstruction Adapter (#32)

Purpose: Adds codebase-memory-mcp as a governed evidence source for codebase memory, dependency reconstruction, graph evidence, patch impact analysis, rollback surface mapping, software decision replay, and code-level Decision Proof.

Layer mapping:

- Primary: L5 Memory & Reconstruction Graph
- Secondary: L4 Tool / Data Execution Substrate
- Evidence feed only: L6 Verification Layer

Boundary: codebase-memory-mcp reconstructs software context and may provide repository indexes, dependency graphs, call graphs, route maps, affected-symbol maps, affected-test surfaces, patch blast radius, rollback surface candidates, and replay-support evidence.

codebase-memory-mcp must not act as a coding agent, model runtime, governance authority, verification authority, decision router, rollback authority, identity authority, fail-closed authority, Decision Proof sealing authority, audit closure authority, or final governance authority.

### Software Decision Proof Reconstruction Workflow (#62)

Purpose: Defines the first AAOS workflow for reconstructing codebase context before, during, and after an agentic code change.

AAOS uses graph evidence to ask:

- What code path is affected?
- What functions, classes, routes, or tests depend on this change?
- Does the change touch auth, payment, security, data pipeline, or governance-sensitive code?
- What is the patch blast radius?
- Can the rollback surface be reconstructed?
- Can the decision be replayed?

### Patch Impact / Blast-Radius Evidence

Purpose: Adds governed patch impact evidence for changed files, changed symbols, affected symbols, affected routes, affected tests, dependency edges touched, call paths touched, sensitive surface flags, blast radius, rollback surface, replay readiness, policy precheck, advisor invocation, and AAOS decision state.

Boundary: Patch impact evidence may inform AAOS review, escalation, replay, rollback-surface review, or fail-closed handling, but it must not approve, block, classify, roll back, seal Decision Proof, or close audit by itself.

## M7 Additions

### open-tag Human-Agent Workspace Adapter (#31)

Purpose: Adds open-tag as a governed collaboration surface for channels, threads, DMs, tasks, task boards, agent workspaces, runtime adapter events, human-agent messages, activity logs, execution traces, workspace state, and replayable collaboration context.

Layer mapping:

- Candidate: L2 Control Plane
- Secondary: L4 Tool / Data Execution Substrate
- Specimen: Human-agent workspace adapter, multi-runtime agent coordination surface, responsibility workflow specimen

Boundary: open-tag may host the work, but AAOS governs the decision.

open-tag must not act as a model runtime, governance core, policy authority, identity authority, verification authority, memory/reconstruction authority, decision router, rollback authority, fail-closed authority, Decision Proof sealing authority, audit closure authority, or final governance authority.

### Human-Agent Activity Evidence

Purpose: Adds governed evidence for workspace, channel, thread, task, decision, actor, agent, daemon, event type, task state, intent, risk class, allowed tools, approval state, rollback plan, required evidence, completion criteria, execution trace, replay target, and activity hashes.

Boundary: Human-agent activity evidence may support review, escalation, replay, approval mapping review, rollback mapping review, or fail-closed handling, but it must not approve, block, classify, route, roll back, seal Decision Proof, close audit, or make final governance judgments by itself.

### Decision Contract Injection Map

Purpose: Defines how AAOS Decision Contract fields can be injected into open-tag tasks, threads, channels, runtime adapter events, and activity logs.

Required Decision Contract fields include:

- decision_id
- intent
- actor
- authority_source
- risk_class
- allowed_tools
- approval_required
- rollback_plan
- evidence_required
- completion_criteria
- execution_trace
- replay_target

### Workspace Activity Replay and Responsibility Workflow Specimen

Purpose: Adds replay-ready collaboration context and responsibility workflow examples for human-agent task execution.

AAOS uses this to ask:

- Who initiated the task?
- Which agent or runtime adapter acted?
- What authority source allowed the action?
- Was approval required?
- Was approval present?
- Was rollback defined?
- Is execution trace available?
- Can the workspace activity be replayed?
- Can Decision Proof be generated without giving the workspace final authority?

## M8 Additions

### Release Governance Hardening (#80)

Purpose: Adds a release governance consistency layer for README version status, milestone completion wording, issue tracker closure, PR merge status, release tag presence, release title consistency, release body consistency, next-phase declaration, related issue linkage, and governance boundary preservation.

AAOS uses this to ask:

- Does README say the same milestone is complete?
- Is the tracker issue closed?
- Is the closing PR merged?
- Does the release tag exist?
- Does the release title match README?
- Does the release body preserve the governance boundary?
- Does the next phase point to the correct milestone?

Boundary: Release governance checks may detect inconsistencies and produce auditable evidence, but they must not approve releases, reject releases, accept risk, close audits, seal Decision Proof, or make final governance judgments.

### Cross-Adapter Regression Pack

Purpose: Adds a cross-adapter sovereignty regression pack covering AAOS systems completed through M7:

- Cloudflare security-audit-skill
- Advisor Invocation Contract
- AITBM L6 Scoring Adapter
- Heretic Adversarial Specimen
- SkillOpt Governed Skill Evolution Layer
- codebase-memory-mcp Codebase Memory & Reconstruction Adapter
- open-tag Human-Agent Workspace Adapter

The regression pack verifies that external systems do not claim:

- final governance authority
- approval doctrine
- identity trust chain
- policy authority
- decision router authority
- rollback authority
- fail-closed authority
- final risk classification
- Decision Proof sealing authority
- audit closure authority

Boundary: Cross-adapter regression packs may detect missing evidence, inconsistencies, or authority-boundary violations, but they must not approve, block, classify, roll back, seal Decision Proof, close audits, or make final governance judgments.

### Initial Adapter Registry Pattern

Purpose: Adds a descriptive and auditable adapter registry pattern for known AAOS systems.

Registry fields include:

- adapter_id
- adapter_name
- adapter_type
- AAOS layer mapping
- allowed outputs
- forbidden outputs
- evidence schema path
- contract path
- example path
- evaluator path if present
- test path if present
- related issue
- related PR
- release introduced
- authority boundary statement
- AAOS retained authority statement

Boundary: The adapter registry is descriptive and auditable.

It must not become a governance authority, policy authority, decision router, rollback authority, fail-closed authority, Decision Proof sealing authority, audit closure authority, or final governance authority.

### Deterministic Release Governance Evaluator

Purpose: Adds deterministic checks for release governance consistency, adapter registry completeness, cross-adapter regression coverage, missing evidence, and forbidden authority claims.

Allowed evaluator outputs include:

- release_consistency_passed
- release_consistency_failed
- regression_findings
- missing_evidence
- authority_boundary_violation
- review_required
- escalation_required
- fail_closed_recommended

Forbidden evaluator outputs include:

- release_approved
- release_rejected_by_evaluator
- risk_accepted
- waiver_granted
- approval_doctrine_changed
- identity_trust_changed
- policy_authority_changed
- decision_route_changed
- rollback_decision
- fail_closed_executed
- decision_proof_sealed
- audit_closed
- final_governance_judgment

## Next Phase

- M9 — Decision Proof Runtime Replay and Governance CI Expansion
  - Expand runtime replay examples across adapters.
  - Add governance CI coverage where appropriate.
  - Strengthen release proof automation.
  - Prepare stronger Decision Proof replay packets for future external integrations.
