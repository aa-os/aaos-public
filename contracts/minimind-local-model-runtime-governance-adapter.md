# AAOS × MiniMind Local Model Runtime Governance Adapter

## Summary

This adapter admits MiniMind as a white-box local model runtime specimen, teaching/runtime experiment substrate, controlled inference target, and verification subject.

MiniMind output is model runtime output.

MiniMind output is not governance authority, policy authority, identity authority, decision authority, verification authority, audit authority, safety proof, or AAOS L0/L1/L2 replacement.

## Purpose

The purpose is to prove:

- AAOS governance value does not depend on one model.
- A model may be replaced.
- The governance contract must remain stable.

## Non-Goals

This adapter does not:

- implement MiniMind itself
- train MiniMind
- approve MiniMind outputs
- treat MiniMind as verification authority
- treat local inference as sovereignty proof
- define AAOS L0/L1/L2 policy
- approve production agent deployment
- create release approval
- close audit findings

## Status

M2 adapter skeleton.

## Source

https://github.com/jingyaogong/minimind

## AAOS Layer Mapping

MiniMind maps to:

- L3 Local Model Runtime
- L4 Tool / Data Execution Candidate
- L4.5 Runtime Evidence Adapter Candidate
- L6 Verification / Audit Subject

MiniMind must not map to:

- L0 Governance / Business Intent
- L1 Policy / Identity Authority
- L2 Control / Decision Authority

## Governance Boundary

Model runtime output is not governance authority.

Model runtime output is not policy.

Model runtime output is not identity.

Model runtime output is not decision approval.

Model runtime output is not audit closure.

Model runtime output is not verification authority.

Verification target is not verification authority.

## Core Invariants

1. Model runtime is not governance authority.
2. Local inference is not sovereignty proof.
3. White-box access is not audit closure.
4. Training pipeline visibility is not safety proof.
5. Model response is not decision approval.
6. Tool-use behavior is not workflow governance.
7. Agentic RL sample is not production agent authority.
8. Small-model controllability is not policy compliance.
9. Verification target is not verification authority.
10. MiniMind is an L3 runtime specimen, not an AAOS L0/L1/L2 authority.

## Required Evidence Records

The adapter should retain:

- minimind_admission_record.json
- minimind_model_identity_record.json
- minimind_runtime_configuration_snapshot.json
- minimind_training_pipeline_reference.json
- minimind_inference_trace_record.json
- minimind_tool_use_experiment_record.json
- minimind_prompt_response_trace.json
- minimind_runtime_failure_record.json
- minimind_drift_detection_input.json
- minimind_verification_replay_packet.json

## Required Binding Fields

Each MiniMind evidence record should bind runtime output to:

- source version
- model identity
- model variant
- weights reference
- training pipeline reference
- runtime environment
- runtime configuration
- serving mode
- tool policy reference
- prompt template reference
- execution timestamp
- input hash
- output hash
- trace ID
- human reviewer
- admission decision
- reason codes

## Decision Outcomes

MiniMind adapter evaluators should support:

- admit_with_constraints
- review_required
- reject
- fail_closed
- allow_with_recorded_exception

## Fail-Closed Conditions

The adapter should fail closed when:

- MiniMind output is treated as governance decision.
- MiniMind is treated as verification authority.
- Local inference is treated as safety proof.
- Tool-use experiment is treated as production tool permission.
- Training pipeline visibility is treated as audit closure.
- Model response is used to authorize external action.
- Runtime trace is missing model identity, config, prompt, timestamp, or hash binding.
- Verification replay packet is incomplete or non-reproducible.
- MiniMind is used to define L0/L1/L2 policy or approval boundaries.
- Model-swappability cannot be demonstrated under the same governance contract.

## Verification Harness Role

MiniMind may be used to test:

- drift detection
- tool misuse checks
- fail-closed simulation
- policy violation precheck
- decision replay
- restore-path replay readiness
- runtime failure taxonomy calibration
- model-swappability under fixed governance contracts

MiniMind must remain the object being tested.

It must not own the test criteria, authority thresholds, fail-closed policy, risk calibration, or audit closure.

## Model-Swappability Requirement

The adapter should support a model-swappability test:

```text
MiniMind baseline runtime
→ same governance contract
→ larger model backend
→ compare behavior under identical decision boundary
```
