# AAOS-RFC-0001 — Canonical Architecture and Governance Vocabulary

Status: Draft. Review state: `under_review`. This package does not assign Candidate status.

## Normative scope

AAOS retains L0–L6 as conceptual responsibility domains. Layer number does not establish Authority rank.

AAOS defines a non-numbered Governed Intent and Interaction Ingress Surface. Capture does not establish identity, mandate, Authority, approval, admission, or execution permission.

L2 is logically separated into L2-A Admission and Arbitration, L2-O Orchestration and Coordination, and L2-E Enforcement and Dispatch.

Models, runtimes, tools, schedulers, policy engines, evaluators, findings, receipts, GitHub metadata, and CI results are non-authoritative by existence alone.

Verification remains distinct from approval, authorization, risk acceptance, audit closure, and proof sealing.

Restore request, restore authorization, restore execution, restore verification, cutover authorization, and cutover execution remain distinct.

Unknown mandatory semantics fail closed, become `not_evaluable`, or require explicit human disposition.

## Admission outcome clarification

`allow` is an admission outcome value, not an independent authorization and not a canonical verb.

`human_review_required` is a routing/review outcome value, not an Authority grant and not a canonical verb.

`admit` is the canonical governance operation.

## L0 clarification

L0 provides governing institutional intent, doctrine, and Authority reference context. It is not a mandatory synchronous centralized runtime hop.

## Informative architecture

Ingress is governed by L0/L1 context, evaluated by L2-A, coordinated by L2-O, enforced by L2-E, executed through L3/L4, preserved by L5, and independently assessed by L6 before any separate consequential disposition.
