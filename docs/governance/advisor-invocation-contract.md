# Advisor Invocation Contract

Advisor invocation is an AAOS strategic governance review hook.

It is used when adapter admission, release gating, high-risk evidence, or governance-sensitive changes need strategic review before AAOS proceeds.

Advisor review produces advisory evidence. It does not make final governance decisions.

## When Advisor Review Is Required

AAOS should invoke advisor review before proceeding when any of these triggers are present:

- new adapter admission
- adapter authority-boundary uncertainty
- release gate escalation
- high or critical risk signal
- high-risk adversarial specimen
- governance policy ambiguity
- fail-closed override request
- external scoring adapter with stale evidence
- human review required but missing
- CI gate failure on a governance-sensitive artifact

## Governance Boundary

Advisor review may recommend:

- escalation
- additional review
- deferral
- containment
- fail-closed handling
- replay or evidence repair

Advisor review must not become:

- final release authority
- risk acceptance authority
- approval doctrine authority
- identity authority
- decision router
- governance policy rewrite authority
- audit closure authority

## AAOS Decision Sovereignty

AAOS retains:

- risk appetite
- approval doctrine
- identity trust chain
- decision router logic
- escalation semantics
- fail-closed policy
- final release authority

An advisor recommendation can inform governance review, but AAOS decides whether to admit an adapter, trigger or clear a release gate, accept risk, grant an exception, close an audit, or fail closed.

## Required Review Packet

Advisor review records should include:

- task ID
- repository, branch, and commit binding
- trigger reason
- executor model
- advisor model
- transcript snapshot hash
- tool state hash
- advisor result hash
- advice summary
- executor acceptance status
- downstream actions
- verification status
- rollback or escalation requirement
- sovereignty statement
- reason codes

## Example

See `examples/advisor-invocation/high-risk-adapter-review.json`.

The example shows a high-risk adapter admission review. Advisor review recommends deferring admission, but AAOS retains final authority over admission, risk acceptance, escalation, fail-closed behavior, and release decisions.

## Status

- candidate
