# AAOS Codebase Decision Proof Kit

codebase-memory-mcp is an AAOS Codebase Memory & Reconstruction Adapter.

It reconstructs software context as governed evidence for codebase memory, dependency reconstruction, graph evidence, patch impact analysis, rollback surface mapping, software decision replay, and code-level Decision Proof.

It is not a coding agent, model runtime, governance authority, verification authority, decision router, rollback authority, identity authority, fail-closed authority, Decision Proof sealing authority, audit closure authority, or final governance authority.

## Layer Position

Primary layer:

- L5 Memory & Reconstruction Graph

Secondary layer:

- L4 Tool / Data Execution Substrate

Evidence feed only:

- L6 Verification Layer

Forbidden AAOS positions:

- L2 Control Plane
- L1 Policy & Identity Plane
- L0 Governance / Business Intent

## Allowed Evidence

codebase-memory-mcp may produce:

- repository indexes
- codebase snapshots
- dependency graphs
- call graphs
- route maps
- affected symbol maps
- affected test surfaces
- architecture summaries
- change impact evidence
- patch blast radius
- rollback surface candidates
- replay support evidence
- software decision context

## Forbidden Authority

codebase-memory-mcp must not produce or claim:

- code change approval
- code change blocking authority
- final risk classification
- approval doctrine changes
- decision route changes
- rollback decisions
- fail-closed policy changes
- escalation semantics changes
- identity trust changes
- Decision Proof sealing
- audit closure
- final governance judgment

## Required Evidence

Codebase graph evidence must include repository identity, commit SHA, index timestamp, indexed paths, language summary, symbol table reference, dependency graph reference, call graph reference, route map reference, test map reference, architecture summary reference, graph hash, source hashes, replay trace reference, freshness status, not-authority statement, and AAOS sovereignty statement.

Patch impact evidence must include changed files, changed symbols, affected symbols, affected routes, affected tests, dependency edges touched, call paths touched, sensitive surface flags, blast radius, rollback surface, replay readiness, trace references, policy precheck, advisor invocation, AAOS decision state, not-authority statement, and AAOS sovereignty statement.

## Policy-Bound Code Change Gate

AAOS should review or fail closed when codebase evidence reports:

- missing graph evidence
- stale codebase index
- missing affected symbol map
- missing affected test surface
- missing rollback surface
- missing replay trace
- auth surface touched
- payment surface touched
- security surface touched
- data pipeline surface touched
- governance-sensitive surface touched
- high blast radius
- adapter claims final risk classification
- adapter claims approval or block authority
- adapter claims rollback authority
- adapter claims Decision Proof sealing authority

## Advisor Invocation

The Advisor Invocation Contract applies as a strategic governance review hook.

Advisor review is required when:

- blast radius is high
- auth surface is touched
- payment surface is touched
- security surface is touched
- data pipeline surface is touched
- governance-sensitive surface is touched
- rollback surface is incomplete
- replay traces are missing
- graph evidence is stale
- adapter output appears to claim AAOS authority
- final risk classification is attempted by the adapter
- Decision Proof sealing is attempted by the adapter

Advisor review may recommend review, escalation, replay, rollback surface review, fail-closed handling, or Decision Proof challenge. It does not own final risk classification, code change approval, code change blocking, rollback authority, fail-closed policy, decision routing, identity trust, Decision Proof sealing, audit closure, or final governance authority.

## Deterministic Evaluator

`runtime/codebase_memory_evaluator.py` checks for missing graph evidence, stale evidence, missing dependency and call graphs, route map gaps for API changes, missing affected symbol and test mappings, missing rollback surface, missing replay traces, high blast radius without advisor invocation, governance-sensitive surface changes without advisor invocation, forbidden adapter authority claims, and Decision Proof sealing claims.

The evaluator emits evidence and review findings only. It does not approve, block, classify, roll back, fail closed, seal Decision Proof, close audits, or make final governance judgments.

## AAOS Sovereignty

codebase-memory-mcp reconstructs software context. AAOS decides whether a code change is allowed, blocked, escalated, replayed, rolled back, or sealed.
