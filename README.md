# AAOS Public

AAOS 是一套治理優先的 AI Agent 操作層。

本公開版本提供規格、範例、模式、插件介面與監管邊界說明，協助開發者理解如何建立可驗證、可稽核、可追溯、受政策約束的 AI Agent 工作流。

## 核心理念

AAOS 不把模型輸出視為最終權威。

AI action 是否有效，取決於它是否通過身份、政策、證據、驗證與稽核閘門。

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
