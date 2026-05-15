# ds4 Local Runtime Governance Adapter Skeleton

This skeleton defines the AAOS governance adapter for the ds4 local runtime.

## Source Metadata

- source_url: https://github.com/antirez/ds4
- source_name: ds4 / DwarfStar 4
- source_type: local-runtime

## Claimed Capability

- Describe the runtime's inference capability, local execution model, and compatibility surface.

## AAOS Layer Mapping

- L3: local runtime candidate
- L4: runtime execution substrate
- L4.5: evidence adapter

## Evidence Produced

- runtime_configuration_snapshot
- model_identity_record
- quantization_profile_record
- prompt_response_trace
- endpoint_compatibility_manifest

## Decision Boundary

This source may provide local inference and runtime evidence, but it must not define governance policy, approval authority, production execution permission, risk acceptance, or audit closure.

## Not Authority Statement

This source is an evidence candidate, not a governance authority.

## Risk If Misclassified

- Local inference could be incorrectly treated as sovereignty proof, safety proof, compliance proof, or production execution authority.

## Required Records

- required_admission_record: ds4_runtime_admission_record.json
- required_replay_or_audit_evidence: ds4_replay_packet.json

## Proposed Adapter Issue

- AAOS × ds4 DeepSeek V4 Flash Local Runtime Governance Adapter Pack

## Status

- candidate
