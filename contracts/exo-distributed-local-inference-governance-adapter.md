# AAOS × exo Distributed Local Inference Governance Adapter

## Summary

This adapter admits exo as a distributed local inference runtime, heterogeneous device cluster, model-sharding substrate, local AI serving endpoint, and runtime evidence source.

exo output is distributed runtime evidence.

exo output is not governance authority, policy authority, identity authority, cluster trust authority, production execution authority, safety proof, sovereignty proof, audit closure, or AAOS L0/L1/L2 replacement.

## Source

https://github.com/exo-explore/exo

## AAOS Layer Mapping

exo maps to:

- L3 Distributed Local Model Runtime
- L4 Runtime / Device / API Execution Substrate
- L4.5 Runtime Evidence Adapter Candidate
- L5 Cluster State / Reconstruction Candidate
- L6 Verification / Audit Subject

exo must not map to:

- L0 Governance / Business Intent
- L1 Policy / Identity Authority
- L2 Control / Decision Authority

## Governance Boundary

Distributed runtime evidence is not governance authority.

Cluster availability is not execution authorization.

Local inference is not sovereignty proof.

Device discovery is not identity trust.

Cluster membership is not trust membership.

Model sharding is not safety proof.

API compatibility is not governance compatibility.

Runtime acceleration is not production readiness.

## Core Invariants

1. Distributed inference is not governance authority.
2. Local cluster execution is not sovereignty proof.
3. Device discovery is not identity admission.
4. Cluster membership is not trust membership.
5. Model sharding is not safety assurance.
6. API compatibility is not policy compatibility.
7. Runtime availability is not production execution authority.
8. Performance gain is not governance clearance.
9. Cluster state is not reconstruction proof unless captured and replayable.
10. exo is an L3/L4 runtime substrate, not an AAOS L0/L1/L2 authority.

## Required Evidence Records

The adapter should retain:

- exo_admission_record.json
- exo_cluster_topology_snapshot.json
- exo_device_identity_record.json
- exo_runtime_configuration_snapshot.json
- exo_model_partition_record.json
- exo_model_identity_record.json
- exo_api_compatibility_manifest.json
- exo_inference_trace_record.json
- exo_scheduling_decision_record.json
- exo_runtime_failure_record.json
- exo_cluster_reconstruction_record.json
- exo_verification_replay_packet.json

## Required Binding Fields

Each exo evidence record should bind runtime output to:

- source version
- runtime version
- cluster ID
- device identities
- device owner
- device role
- device trust status
- device admission status
- network profile
- model identity
- weights reference
- model partition plan
- runtime configuration
- serving endpoint
- API compatibility surface
- input hash
- output hash
- trace ID
- timestamp
- human reviewer
- admission decision
- reason codes

## Evidence Categories

exo outputs should be classified as:

- cluster_topology
- device_identity
- device_admission_state
- runtime_configuration
- model_identity
- model_partition_plan
- api_compatibility_manifest
- inference_trace
- scheduling_decision
- runtime_failure
- cluster_reconstruction_input
- verification_replay_packet

## Decision Outcomes

exo adapter evaluators should support:

- admit_with_constraints
- review_required
- reject
- fail_closed
- allow_with_recorded_exception

## Fail-Closed Conditions

The adapter should fail closed when:

- exo output is treated as governance decision.
- Device discovery is treated as trusted identity.
- Cluster membership is not explicitly admitted.
- Runtime API compatibility is treated as governance compatibility.
- Model partitioning is treated as safety proof.
- Runtime availability is treated as production execution authority.
- Cluster topology is missing device, network, version, model, timestamp, or hash binding.
- Model partitions cannot be reconstructed.
- Inference traces cannot be replayed.
- Scheduling decisions are unbound to device state and model partition state.
- Untrusted devices are allowed into protected inference lanes.
- exo is used to define L0/L1/L2 policy or approval boundaries.

## Cluster Admission Governance

Every device in an exo cluster must have an explicit admission state:

```yaml
device_id:
device_fingerprint:
device_owner:
device_role:
hardware_profile:
network_zone:
trust_status:
admission_status:
approved_by:
approval_timestamp:
allowed_model_lanes:
allowed_tool_lanes:
revocation_status:
```

Cluster admission must be:

* device-bound
* owner-bound
* role-bound
* network-zone-bound
* model-lane-bound
* time-bound when needed
* revocable
* replayable

A discovered device is not an admitted device.

An admitted device is not automatically trusted for all model lanes.

Model Partition Governance

Every distributed model execution should retain:
model_id:
model_variant:
weights_reference:
partition_strategy:
partition_map:
	- device_id:
		partition_role:
		tensor_range:
		kv_cache_role:
		memory_allocation:
partition_hash:
runtime_config_hash:
reconstruction_requirements:
Model partitioning must be reconstructable before it can enter L5/L6 evidence routing.

API Compatibility Boundary

exo may expose or emulate common AI APIs.

API compatibility must not be treated as governance compatibility.

For each exposed API surface, retain:
api_surface:
compatibility_claim:
enabled:
network_exposure:
authentication_mode:
authorization_boundary:
request_trace_required:
response_trace_required:
If API endpoints are exposed beyond a local trusted boundary, the adapter should require review_required or fail_closed, depending on policy.

Verification Harness Role

exo may be used to test:

* distributed inference reproducibility
* cluster topology drift
* device admission drift
* runtime configuration drift
* model partition reconstruction
* API compatibility boundary
* scheduling decision replay
* runtime failure taxonomy
* model-swappability under distributed execution

exo must remain the object being tested.

It must not own the test criteria, authority thresholds, fail-closed policy, risk calibration, or audit closure.

Non-Goals

This adapter does not:

* implement exo itself
* approve exo outputs
* approve cluster membership by default
* treat discovered devices as trusted devices
* treat local inference as sovereignty proof
* treat distributed inference as safety proof
* treat API compatibility as governance compatibility
* define AAOS L0/L1/L2 policy
* approve production deployment
* create release approval
* close audit findings

Status

M2 adapter skeleton.

