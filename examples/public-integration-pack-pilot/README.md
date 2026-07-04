# M11 Public Integration Pack Pilot

Status: M11 pilot package. M11 is active work in progress; this is not v0.10.0 release completion language.

The public integration pack pilot is an evidence-interface package for external systems that provide evidence to AAOS or consume AAOS artifacts. It makes the M10 Public Integration Pack Pattern concrete without transferring Decision Proof sealing or final governance authority.

## Included References

- Integration boundary contract: `pilot-package.json#integration_boundary_contract`
- Evidence schema references: `schemas/external-integration-readiness.schema.json`, `schemas/decision-proof-sealing-status.schema.json`, `schemas/decision-proof-runtime-replay-packet.schema.json`, and `schemas/release-proof-automation.schema.json`
- Replay packet example: `examples/decision-proof-runtime-replay/release-governance-replay.json`
- Release proof linkage: `examples/release-proof-automation/v0.8.0-release-proof.json`
- Sealing boundary statement: `pilot-package.json#sealing_boundary_statement`
- Adapter registry entry reference: `registries/adapter-registry.yaml#public-integration-pack-pilot`
- Evaluator check reference: `runtime/public_integration_pack_evaluator.py`
- README integration status language: M11 is active work in progress and must not be treated as released.
- Governance boundary language: public integration packs shape, reference, replay, check, and link evidence but do not govern AAOS decisions.

## Governance Boundary

The public integration pack is an evidence-interface package.

It may define how evidence is shaped, referenced, replayed, checked, and linked to release proof.

It must not become governance authority, approval authority, release authority, rollback authority, Decision Proof sealing authority, audit closure authority, or final governance authority.

Decision Proof sealing remains AAOS-owned.

## Integration-Facing Flow

1. An external tool provides evidence using the pack boundary contract.
2. AAOS receives the evidence as governed input.
3. Deterministic checks evaluate evidence readiness and authority-boundary preservation.
4. Runtime replay supports inspection without approving the underlying decision.
5. Release proof linkage preserves traceability to release evidence.
6. Sealing eligibility is represented as evidence state only.
7. AAOS retains final Decision Proof sealing authority.
8. External consumers may consume artifacts without becoming authorities.

## Artifact Consumption Semantics

External consumers may read, reference, replay, inspect, or report on artifacts according to their status.

External consumers must not convert artifact status into final governance judgment.

See `external-evidence-consumer-specimen.json` for sealed and non-sealed artifact consumption semantics.
