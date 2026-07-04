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

Current baseline:

AAOS Public now includes the Governance Radar foundation, first adapter skeletons, contract/schema hardening, Cloudflare L6 security verification, deterministic evaluator tests, CI gate coverage, the M5 governed adapter/specimen/evaluator pattern, and the M6 software Decision Proof reconstruction workflow.

v0.5.0 adds the first AAOS software Decision Proof reconstruction workflow and introduces a governed Codebase Memory & Reconstruction Adapter pattern. External tools continue to be admitted as governed evidence sources, not authorities.

## Current Status

M1, M2, M3, M4, M5, and M6 are complete.

M5 completed:

- #28 Advisor Invocation Contract
- #29 AITBM L6 Scoring Adapter
- #30 Heretic Adversarial Specimen
- #33 SkillOpt Governed Skill Evolution Layer

M6 completed:

- #62 M6: Decision Proof Reconstruction Layer and Codebase Memory Adapter
- #32 codebase-memory-mcp Codebase Memory & Reconstruction Adapter

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

## Next Phase

- M7 — Human-Agent Control Surface
  - #31 open-tag Human-Agent Workspace Adapter
