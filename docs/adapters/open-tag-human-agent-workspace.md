# open-tag Human-Agent Workspace Adapter

open-tag is documented as an AAOS Human-Agent Workspace Adapter and Human-Agent Control Surface specimen.

It provides governed collaboration context for channels, threads, tasks, DMs, persistent workspaces, agent lifecycle events, runtime adapter events, activity logs, execution traces, and replayable workspace history.

open-tag is not a model runtime, governance core, policy authority, identity authority, verification authority, memory/reconstruction authority, decision router, rollback authority, fail-closed authority, Decision Proof sealing authority, audit closure authority, or final governance authority.

## Layer Position

Candidate:

- L2 Control Plane

Secondary:

- L4 Tool / Data Execution Substrate

Specimen:

- Human-agent workspace adapter
- Multi-runtime agent coordination surface
- Responsibility workflow specimen

Must not replace:

- L0 Governance / Business Intent
- L1 Policy & Identity Plane
- L5 Memory & Reconstruction Graph
- L6 Verification Layer

## Allowed Context

open-tag may provide:

- channel context
- thread context
- DM context
- task context
- task board state
- workspace state
- human message logs
- agent message logs
- daemon event logs
- runtime adapter events
- agent lifecycle events
- start, stop, sleep, and resume events
- activity logs
- execution traces
- approval request context
- rollback request context
- collaboration replay context
- responsibility workflow context

## Forbidden Authority

open-tag must not claim:

- business intent changes
- risk appetite changes
- approval doctrine changes
- identity trust changes
- policy authority changes
- decision route changes
- escalation semantics changes
- fail-closed policy changes
- rollback decisions
- final risk classification
- Decision Proof sealing
- audit closure
- final governance judgment

## Required Evidence

Human-agent activity evidence must bind workspace, channel, thread, task, decision, actor, agent, daemon, event type, task state, intent, risk class, allowed tools, approval state, rollback plan, required evidence, completion criteria, execution trace, replay target, and activity hashes.

Decision Contract injection must bind decision intent, actor, authority source, risk class, tools, approval, rollback, evidence, completion criteria, execution trace, replay target, workspace, channel, thread, task, runtime adapter, approval, rollback, and Decision Proof traceability.

## Workspace Gate

AAOS should review or fail closed when workspace evidence reports:

- missing Decision Contract fields
- missing execution trace
- missing replay target
- missing actor, agent, or daemon separation
- runtime adapter event without task binding
- task execution without Decision Contract
- required approval without approval state
- required rollback without rollback plan
- high-risk task without advisor invocation
- governance-sensitive workspace event without advisor invocation
- open-tag authority claims
- Decision Proof sealing claimed by open-tag

## Advisor Invocation

The Advisor Invocation Contract applies as a strategic governance review hook.

Advisor review is required when:

- risk class is high or critical
- approval is required but approval state is missing
- rollback plan is missing or incomplete
- execution trace is missing
- replay target is missing
- runtime adapter event is not bound to a task
- task execution occurs without Decision Contract fields
- governance-sensitive workspace event occurs
- open-tag output appears to claim AAOS authority
- policy authority is attempted by open-tag
- decision router authority is attempted by open-tag
- rollback authority is attempted by open-tag
- Decision Proof sealing is attempted by open-tag

Advisor review may recommend review, escalation, approval mapping review, rollback mapping review, replay, or fail-closed handling. It does not own policy, identity, decision routing, rollback, fail-closed policy, Decision Proof sealing, audit closure, or final governance authority.

## Evaluator

`runtime/open_tag_workspace_evaluator.py` checks for missing Decision Contract fields, missing replay targets, missing execution traces, missing approval state, missing rollback plans, missing actor / agent / daemon separation, unbound runtime adapter events, task execution without a Decision Contract, missing advisor invocation, forbidden authority claims, and Decision Proof sealing claims.

The evaluator emits evidence and review findings only. It does not approve, block, classify, route, roll back, fail closed, seal Decision Proof, close audits, or make final governance judgments.

## AAOS Sovereignty

AAOS retains purpose and business intent, risk appetite, approval doctrine, identity trust chain, policy authority, decision router logic, escalation semantics, fail-closed policy, rollback policy, final risk classification, Decision Proof sealing logic, audit final judgment, and final governance authority.
