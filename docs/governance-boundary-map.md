# Governance Boundary Map

本文件定義 AAOS Public 版本的公開邊界。

AAOS 採取「部分開源」策略，不是單純開或不開，而是依照治理層級決定公開範圍。

## 核心原則

越靠近使用者接觸面，越適合公開。

越靠近決策主權、風險門檻、身份信任鏈與重建能力，越必須保留。

## L0 Governance / Business Intent

狀態：不公開核心。

原因：這一層定義系統目的、責任分配、風險承擔與升級原則，不是一般功能模組。

可公開：

- 理念說明
- 使用情境
- 治理原則
- 公共版定位

不公開：

- business intent
- risk appetite
- escalation doctrine
- liability strategy

## L1 Policy & Identity Plane

狀態：核心不公開，只公開介面。

原因：RBAC、ABAC、agent identity、approval chain 與 policy binding 決定誰有權做什麼。

可公開：

- 外部接入規格
- 身份介面
- 權限模板
- policy schema 範例

不公開：

- identity trust chain
- approval doctrine
- private policy registry
- production authorization logic

## L2 Control Plane

狀態：不公開決策引擎。

原因：scheduler、orchestrator、workflow runtime 與 action arbitration 是 AAOS 主控中樞。

可公開：

- workflow DSL
- job API
- plugin interface
- routing pattern 範例

不公開：

- decision router logic
- action arbitration logic
- production routing strategy
- fail-closed calibration

## L3 Local Model Runtime

狀態：可公開、可替換、可外接。

原因：模型是被治理與被驗證的 runtime，不是治理權威。

可公開：

- local runtime integration
- model adapter
- OpenAI-compatible endpoint pattern
- tool-use playground
- fallback runtime pattern

不公開：

- production model selection strategy
- private model evaluation ranking
- sensitive runtime optimization logic

## L4 Tool / Data Execution

狀態：可公開工具介面，不公開敏感執行細節。

原因：tool calling、sandbox、connector、context routing 會影響資料安全與實際操作風險。

可公開：

- tool contract
- connector interface
- sandbox policy example
- data access pattern

不公開：

- sensitive connector credentials
- production tool permission map
- destructive action execution rules
- private data routing details

## L5 Memory & Reconstruction Graph

狀態：只公開 schema 與查詢介面，不公開完整重建能力。

原因：state snapshot、dependency graph、restore map 與 decision lineage 是系統可追溯與可重建的核心。

可公開：

- metadata schema
- catalog API
- version format
- lineage record example

不公開：

- restore map
- full dependency graph
- private registry
- state reconstruction rule
- production lineage risk map

## L6 Verification & Audit

狀態：公開 audit 形式與 test harness，不公開完整風險門檻。

原因：verification、drift detection、replay、simulation 與 audit gate 是治理防線。

可公開：

- audit report example
- verification interface
- test harness
- status dashboard pattern
- evidence packet format

不公開：

- risk threshold
- drift sensitivity calibration
- internal audit scoring
- fail-closed trigger rule
- production verification policy

## Public Repository Scope

本 repo 可以公開：

- 架構說明
- Governance Boundary Map
- Decision Contract 範例
- Governance Verdict 範例
- Plugin SDK 介面
- Audit Evidence 格式
- RFC 文件
- 非敏感測試樣本

## Non-Public Scope

本 repo 不公開：

- decision router 核心邏輯
- risk threshold
- private registry
- approval doctrine
- identity trust chain
- restore map
- dependency graph
- production governance gate
- complete fail-closed rules

## Positioning

AAOS Public 的目的不是把 AAOS 全部開源。

AAOS Public 的目的，是建立一套可被理解、可被討論、可被接入、可被驗證的 AI Agent Governance 公共語言。

真正的決策主權層，仍然保留在 AAOS Core。
