# DS4 Governance Admission Contract

This contract defines the admission rules for ds4 as an AAOS local runtime evidence source.

## Summary

DS4 may be admitted as an evidence-producing local runtime candidate when its outputs are bound to reproducible runtime, model identity, and admission metadata.

## Source Metadata

- source_url: https://github.com/antirez/ds4
- source_name: ds4 / DwarfStar 4
- source_type: local-runtime

## Purpose

The admission contract ensures ds4 is treated as a runtime evidence subject rather than a governance authority.
It defines what evidence is required for admission, what bindings are mandatory, and what conditions must fail closed.

## Admission Criteria

DS4 may be admitted when the following are present and verifiable:

- runtime admission record bound to ds4 source, version, and environment
- model identity and variant metadata
- runtime configuration snapshot
- inference prompt/response trace
- replay or audit evidence capable of reproducing the runtime event
- explicit admission decision, reason codes, and human reviewer binding

## Required Evidence Records

Minimum records required for admission:

- ds4_runtime_admission_record.json
- ds4_model_identity_record.json
- ds4_runtime_configuration_snapshot.json
- ds4_prompt_response_trace.json
- ds4_replay_packet.json

## Required Binding Fields

Each admission record must bind the evidence to:

- source version
- model identity
- model variant
- runtime environment
- runtime configuration
- execution timestamp
- input hash
- output hash
- trace ID
- admission decision
- human reviewer
- reason codes

## Governance Assertion

DS4 runtime evidence is admitted as local runtime evidence.
Admission does not make ds4 a governance authority.
Admission does not approve production execution or accept risk on behalf of AAOS.

## Fail-Closed Conditions

The admission contract must fail closed if:

- ds4 output is treated as governance decision or approval authority
- required admission records are missing or incomplete
- bindings between runtime evidence and source/model/configuration are absent
- replay evidence is missing, incomplete, or irreproducible
- admission decision is absent, ambiguous, or not reviewable
- ds4 metadata is not tied to a specific version and runtime environment

## Decision Outcomes

Admission evaluators should support:

- admit_with_constraints
- review_required
- reject
- fail_closed
- allow_with_recorded_exception

## Non-Goals

This contract does not:

- implement ds4 itself
- define AAOS policy or business intent
- waive governance requirements
- treat ds4 runtime output as audit closure
- approve external action without higher-layer authority

## Status

- candidate
