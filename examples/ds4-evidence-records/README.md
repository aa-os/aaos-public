# DS4 Runtime Evidence Records

This directory contains example DS4 runtime evidence records demonstrating the schema and governance structure for ds4 local runtime evidence admission.

## Overview

DS4 is a local runtime inference engine. Its evidence records bind runtime execution to source version, model identity, runtime configuration, and inference output. These records enable reproducible audit and verification without treating ds4 as a governance authority.

## Evidence Records

### 1. ds4-runtime-admission-record-001.json

**Schema:** `schemas/ds4-runtime-admission-record.schema.json`

The admission record is the governance decision artifact. It:
- Binds the inference execution to source version, model variant, and runtime environment
- Contains explicit admission decision with human reviewer binding
- References all required supporting evidence records
- Includes governance decision and constraints
- Defines fail-closed conditions

**Key Fields:**
- `source_binding`: Links to ds4 source code version
- `model_binding`: Identifies model, variant, and weights
- `runtime_binding`: Specifies execution environment and hardware
- `evidence_binding`: Hashes of input and output
- `governance_decision`: Admission status, reason codes, constraints

### 2. ds4-model-identity-record-001.json

**Schema:** `schemas/ds4-model-identity-record.schema.json`

Records the complete model metadata and provenance. It:
- Identifies the base model and quantization variant
- References model weights with content hash
- Documents training date, data cutoff, and fine-tuning
- Includes architecture specifications (parameters, context window, vocab size)

**Key Fields:**
- `model_identity`: Base model identifier (e.g., deepseek-v4-flash)
- `model_variant`: Quantization scheme (e.g., int4-quantized)
- `weights_reference`: Source and hash of model weights
- `quantization`: Quantization method and parameters
- `architecture`: Model specifications and capacity

### 3. ds4-runtime-configuration-snapshot-001.json

**Schema:** `schemas/ds4-runtime-configuration-snapshot.schema.json`

Complete snapshot of runtime environment and inference configuration. It:
- Records OS, hardware, and accelerator configuration
- Documents inference parameters (temperature, top_p, tokens, etc.)
- Includes server configuration (API version, port, TLS, etc.)
- Provides configuration hash for reproducibility

**Key Fields:**
- `runtime_environment`: OS and architecture
- `hardware_configuration`: CPU, memory, accelerator specs
- `inference_configuration`: Model serving parameters
- `server_configuration`: API and listening settings
- `configuration_hash`: SHA256 of complete configuration

### 4. ds4-prompt-response-trace-001.json

**Schema:** `schemas/ds4-prompt-response-trace.schema.json`

The inference execution trace recording input, output, and metrics. It:
- Captures complete prompt and response text
- Records execution timestamps and duration metrics
- Includes parameter bindings to model and runtime
- Documents tokens-per-second and memory usage

**Key Fields:**
- `trace_id`: Unique identifier for this inference execution
- `prompt`: Input text and hash
- `response`: Output text, hash, and finish reason
- `inference_parameters`: Temperature, top_p, top_k, max_tokens
- `execution_metrics`: Latency, throughput, memory consumption
- `binding`: References to model, runtime, and configuration

### 5. ds4-replay-packet-001.json

**Schema:** `schemas/ds4-replay-packet.schema.json`

Complete reproducibility packet enabling audit verification. It:
- Specifies exact versions and hashes needed for reproduction
- Includes step-by-step replay instructions (bash, Python, Docker, etc.)
- Documents reproducibility status (deterministic or stochastic)
- Contains attestation of successful verification

**Key Fields:**
- `reproducibility_requirements`: Exact versions, hashes, OS/hardware needs
- `prompt_input`: Input text and hash for replay
- `inference_config`: Inference parameters including seed
- `expected_output`: Expected response hash for verification
- `replay_instructions`: Step-by-step commands to reproduce
- `attestation`: Verification status and who verified it

## Usage Patterns

### Complete Evidence Set

A single inference execution should have all five records:

```text
ds4-runtime-admission-record-001.json
├── requires_for_verification
│   ├── ds4-model-identity-record-001.json
│   ├── ds4-runtime-configuration-snapshot-001.json
│   ├── ds4-prompt-response-trace-001.json
│   └── ds4-replay-packet-001.json
```

The admission record references all supporting records and includes the governance decision.

### Verification Flow

1. **Load admission record** - Get governance decision and constraints
2. **Verify replay packet** - Reproduce inference execution
3. **Compare hashes** - Input/output hashes must match trace record
4. **Validate bindings** - Confirm model, runtime, configuration match
5. **Check constraints** - Ensure use case respects admission constraints

## Governance Assertions

DS4 runtime evidence is admitted as **L3/L4 local runtime evidence only**.

DS4 is **NOT**:
- Governance authority
- Policy authority
- Identity authority
- Decision approval authority
- Verification authority
- Audit closure
- Risk acceptance
- Production execution authority

## Fail-Closed Conditions

Admission must fail closed if:
- Output is treated as governance decision
- Required records are missing or incomplete
- Bindings between runtime, model, and configuration are absent
- Replay evidence is missing, incomplete, or non-reproducible
- Admission decision is absent or not reviewable
- Metadata not tied to specific version and runtime environment

## Binding Fields (Required)

Each record must bind evidence to governance-relevant attributes:
- Source version (exact commit or tag)
- Model identity and variant
- Runtime environment and configuration
- Execution timestamp
- Input/output hashes
- Human reviewer
- Admission decision

## Related Documentation

- [DS4 Governance Admission Contract](../contracts/ds4-governance-admission-contract.md)
- [DS4 Local Runtime Governance Adapter](../contracts/ds4-local-runtime-governance-adapter.md)
- [DS4 Runtime Boundary Contract](../contracts/ds4-runtime-boundary-contract.md)
- [Radar Node Schema](../schemas/radar-node.schema.json)

## Examples vs. Production

These example records demonstrate the governance structure and binding requirements. Production evidence records should:
- Use actual content hashes (SHA256)
- Include complete execution traces
- Maintain proper chain of custody
- Be reviewable and auditable
- Support replay/verification procedures
- Be bound to human decision makers
