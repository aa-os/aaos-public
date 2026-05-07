# AAOS Architecture L0–L6

本文件說明 AAOS Public 版本中的 L0–L6 架構。

AAOS 的核心定位是：

> Governance-first operating layer for AI agents.

也就是說，AAOS 不是單純的 AI agent 框架，也不是模型執行器，而是一套讓 AI agent 的行為可以被約束、驗證、追溯、稽核與治理的操作層。

## Layer Overview

AAOS 採用七層架構：

```text
L0  Governance / Business Intent
L1  Policy & Identity Plane
L2  Control Plane
L3  Local Model Runtime
L4  Tool / Data Execution
L5  Memory & Reconstruction Graph
L6  Verification & Audit
````

## L0 Governance / Business Intent

L0 定義系統為什麼存在，以及它應該承擔什麼責任。

這一層回答的不是技術問題，而是治理問題：

* 系統目的
* 責任邊界
* 風險承擔
* 升級原則
* 人類覆核條件
* 不可自動化的決策範圍

AAOS 的基本原則是：

> AI action is not valid because a model produced it.
> It is valid only when it passes identity, policy, evidence, verification, and audit gates.

## L1 Policy & Identity Plane

L1 定義誰可以做什麼。

這一層處理：

* agent identity
* human identity
* RBAC / ABAC
* approval chain
* policy binding
* permission scope
* human-in-the-loop control

在 AAOS 中，模型不能自己決定自己的權限。

任何 agent action 都必須先被綁定到明確身份、政策與授權邊界。

## L2 Control Plane

L2 是 AAOS 的主控層。

這一層負責：

* workflow routing
* scheduler
* orchestrator
* action arbitration
* task admission
* decision routing
* escalation handling

L2 不等於模型推理。

模型可以提出建議，但是否能進入下一步，由 control plane 根據 policy、identity、risk、evidence 與 verification state 判斷。

## L3 Local Model Runtime

L3 是模型執行層。

這一層可以包含：

* local model
* cloud model
* small model
* large model
* fallback model
* canary runtime
* OpenAI-compatible endpoint
* model adapter

在 AAOS 中，模型是 runtime，不是 governance authority。

模型可以被替換、比較、測試、隔離與降級。

## L4 Tool / Data Execution

L4 是工具與資料執行層。

這一層處理：

* tool calling
* sandbox execution
* file access
* API connector
* database connector
* RAG pipeline
* context routing
* data permission boundary

AAOS 特別重視 destructive action 的治理。

例如：

* delete
* overwrite
* deploy
* send
* approve
* revoke
* execute
* transfer
* expose data

這些動作不能只因為模型要求就執行，必須通過 policy、approval、evidence 與 audit gate。

## L5 Memory & Reconstruction Graph

L5 是記憶、狀態與重建層。

這一層處理：

* state snapshot
* decision lineage
* dependency graph
* restore map
* timeline ledger
* manifest index
* evidence registry
* reconstruction record

AAOS 不把記憶只視為聊天紀錄。

更精確地說，AAOS 把記憶視為：

> 可追溯、可重播、可重建的系統狀態。

如果一個 AI 決策事後無法重建，就不應該被視為完整治理過的決策。

## L6 Verification & Audit

L6 是驗證與稽核層。

這一層處理：

* audit gate
* replay
* simulation
* drift detection
* risk threshold
* verification harness
* evidence sufficiency check
* governance verdict
* audit report

AAOS 不把測試視為最後補救，而是把 verification 放進 runtime governance flow。

也就是說，系統在執行之前、執行期間、執行之後，都要留下可檢查的治理證據。

## Runtime Flow

AAOS 的基本 runtime flow 可以表示為：

```text
user intent
  ↓
task intake
  ↓
identity binding
  ↓
policy check
  ↓
control plane routing
  ↓
model runtime
  ↓
tool / data execution
  ↓
decision envelope
  ↓
governance verdict
  ↓
audit evidence
  ↓
replay / reconstruction readiness
```

## Core Design Principle

AAOS 的核心設計原則是：

```text
Model output is not authority.
Tool execution is not approval.
Workflow completion is not audit closure.
Human acceptance is not governance evidence.
A decision is valid only if it is governable, verifiable, traceable, and reconstructable.
```

## Public Version Scope

本公開架構文件只說明 AAOS 的高階分層與治理邏輯。

本 repo 可以公開：

* architecture overview
* governance boundary
* public schema
* example decision contract
* example governance verdict
* plugin interface
* audit evidence format
* test harness pattern

本 repo 不公開：

* production decision router
* risk threshold
* approval doctrine
* identity trust chain
* restore map
* dependency graph
* private registry
* fail-closed calibration
* commercial governance engine

## Summary

AAOS L0–L6 架構的目的，是把 AI agent 從「會執行任務的工具」，升級成「受治理、可驗證、可追溯、可稽核的決策工作流」。

AAOS Public 提供公共語言與接入邊界。

AAOS Core 保留決策主權與生產治理內核。

````

最後下面 **Commit changes**。

Commit message 填：

```text
Add L0-L6 architecture document
````
