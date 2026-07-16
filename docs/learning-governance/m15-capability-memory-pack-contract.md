# M15 Evidence-Bound Capability Memory Pack Contract

## Status and scope

This document defines the bounded M15 Track B Capability Memory Pack contract. The supported schema version is `m15-capability-memory-pack/v1`.

This package is contract-first, deterministic, offline, read-only, and simulation-only. It evaluates caller-supplied manifest and binding declarations as inert evidence. It does not retrieve or import an external repository, hash fixture objects, register tools, install packages, connect to a runtime, execute a capability, use credentials, or mutate an external state.

M15 remains active work and is not complete. `v0.14.0` remains a future release path and is not published. Tracker #231 remains Open.

## Core separation

Knowledge retrieval is not specification verification. Specification verification is not tool registration. Runtime compatibility is not execution authorization.

A structurally valid evidence record is not necessarily a verified pack. The evaluator reports evidence-record validity independently from verified-pack eligibility. Stale, incompatible, quarantined, superseded, and revoked records can remain coherent lifecycle evidence while being ineligible for runtime review. A verified pack is eligible only when every required structural, manifest, digest, graph, version, runtime, license, lifecycle, sensitive-material, linkage, and authority check passes.

`retrieval_eligible` permits only inert evidence inspection. `runtime_eligible` means eligibility for independent policy review only. Neither field authorizes installation, registration, deployment, execution, production use, risk acceptance, or proof sealing.

The exact required boundary statement is:

> This Capability Memory Pack is evidence only; runtime eligibility means eligibility for independent policy review, not installation, registration, deployment, execution, risk acceptance, Learning Proof sealing, or Decision Proof sealing. Capability Pack sealing is undefined and out of scope for M15 Track B. A capability pack must not claim sealed status or sealing authority.

## Closed vocabulary

The following values are closed enumerations for `m15-capability-memory-pack/v1`:

| Field | Values |
| --- | --- |
| `lifecycle_state` | `unverified`, `verified`, `stale`, `incompatible`, `quarantined`, `superseded`, `revoked` |
| `compatibility_mode` | `exact` |
| `compatibility_result` | `compatible`, `incompatible`, `unknown` |
| `redistribution_status` | `allowed`, `restricted`, `prohibited`, `unknown` |
| `license_review_status` | `reviewed`, `review-required`, `revoked` |
| `evidence_disposition` | `verified-read-only`, `stale-evidence`, `quarantined-evidence`, `incompatible-evidence`, `revoked-evidence`, `unverified-evidence` |
| artifact `role` | `structured-spec`, `workflow-graph`, `examples`, `error-taxonomy`, `graph-snapshot`, `verification-report` |

`superseded` maps to `stale-evidence`; supersession makes the pack non-current without inventing a disposition outside the closed v1 vocabulary.

Every digest is a raw lowercase SHA-256 string matching `^[0-9a-f]{64}$`. A `sha256:` prefix, uppercase hexadecimal, truncation, or whitespace is invalid.

## Record structure

Every Capability Memory Pack contains these evidence groups:

- `manifest_references` binds the pack-level source, license, and derived manifest digests.
- `source_manifest` records an inert source reference, active or revoked source status, immutable commit-or-content digest, and upstream API version.
- `license_manifest` records the license identifier, redistribution status, review status, review evidence, and optional revocation evidence.
- `derived_spec_manifest` binds the source and license manifests, source API version, derivation evidence, and all six derived artifact digests.
- `artifact_inventory` contains exactly one item for every required role. Every item has a synthetic or repository-relative inert path, raw digest, media type, and `executable: false`.
- `graph_binding` binds the graph snapshot, structured specification, workflow graph, source manifest, and immutable source. It also records graph-alteration and integrity evidence state.
- `runtime_compatibility` records only exact expected-versus-observed runtime evidence. It defines no range or fallback inference.
- `lifecycle_evidence` records stale, version-drift, quarantine, contamination, supersession, and archival evidence state.
- `revocation` records active or revoked pack status and optional revocation evidence.
- optional Learning Proof and Decision Proof references record linkage only.
- `authority_claims` contains the fixed-false AAOS authority boundary and recursively inspected extensions.
- `extensions` accepts inert auxiliary evidence but remains subject to sensitive-material and authority inspection.
- declared retrieval eligibility, runtime-review eligibility, and evidence disposition must agree with the lifecycle.

Unknown top-level fields and unknown nested fields outside `authority_claims` and `extensions` fail schema validation.

## Declared digest relationships

The evaluator validates declared equality among fields. It does not hash a fixture object, fetch a source, read an artifact path, or independently prove that any declared digest binds bytes.

The required declared relationships are:

- `manifest_references.source_manifest_digest` equals `source_manifest.manifest_digest`.
- `manifest_references.license_manifest_digest` equals `license_manifest.manifest_digest`.
- `manifest_references.derived_spec_manifest_digest` equals `derived_spec_manifest.manifest_digest`.
- `derived_spec_manifest.source_manifest_digest` equals `source_manifest.manifest_digest`.
- `derived_spec_manifest.license_manifest_digest` equals `license_manifest.manifest_digest`.
- each entry in `derived_spec_manifest.artifact_digests` equals the digest of the inventory entry with the corresponding role.
- `graph_binding.graph_snapshot_digest` equals the `graph-snapshot` inventory digest.
- `graph_binding.structured_spec_digest` equals the `structured-spec` inventory digest.
- `graph_binding.workflow_graph_digest` equals the `workflow-graph` inventory digest.
- `graph_binding.source_manifest_digest` equals `source_manifest.manifest_digest`.
- `graph_binding.immutable_source_binding` equals `source_manifest.immutable_commit_or_content_digest`.

Passing these checks establishes internal consistency evidence only. Declared equality is not independent cryptographic verification, provenance approval, tool admission, or execution authority.

## Version and runtime relationships

A verified pack requires `source_manifest.upstream_api_version` to equal `derived_spec_manifest.source_api_version`.

Exact runtime compatibility requires all of the following:

- `compatibility_mode` is exactly `exact`.
- `expected_runtime_name` equals `observed_runtime_name`.
- `expected_runtime_version` equals `observed_runtime_version`.
- `compatibility_result` is `compatible`.
- `compatibility_evidence_reference` is present and non-empty.

The evaluator performs no semantic-version range inference, compatibility fallback, runtime probing, dependency installation, or runtime execution.

## Lifecycle consistency

### `unverified`

An unverified record uses `unverified-evidence`, is not retrieval or runtime eligible, and does not claim verified-pack eligibility.

### `verified`

A verified record requires every structural, manifest, digest, graph, version, exact-runtime, license, lifecycle, sensitive-material, linkage, and authority check to pass. The source and pack are active, the license is reviewed, graph alteration and contamination are false, and both declared eligibility fields are true. Its disposition is `verified-read-only`.

Runtime eligibility remains eligibility for independent policy review only and is never execution authorization.

### `stale`

A stale record requires a non-empty `stale_reason`, `version_drift_detected: true`, and an upstream-versus-derived API-version difference. It uses `stale-evidence`, may remain retrievable for inert inspection, and must have `runtime_eligible: false`.

The record can be valid stale evidence while being ineligible as a verified pack.

### `incompatible`

An incompatible record requires an expected-versus-observed runtime name or version mismatch, or `compatibility_result: incompatible`. It uses `incompatible-evidence` and must have `runtime_eligible: false`. No fallback is inferred.

### `quarantined`

A quarantined record requires evidence of graph alteration, a digest or source-binding mismatch, contamination, or another integrity failure. A non-empty quarantine reason is required, and graph alteration requires an integrity-evidence reference. It uses `quarantined-evidence` and must have both eligibility fields false.

### `superseded`

A superseded record requires `superseded_by_reference`, uses `stale-evidence`, and must have `runtime_eligible: false`.

### `revoked`

A revoked record requires a non-empty revocation-evidence reference and a revoked source, license, or pack status. It uses `revoked-evidence` and must have both eligibility fields false. `archival_evidence_retained` may remain true solely to record archival evidence; it does not restore retrieval or runtime eligibility.

## Linkage boundary

`related_learning_proof_reference` and `related_decision_proof_reference` are optional inert linkage evidence. The evaluator does not import or invoke the Track A evaluator.

A Learning Proof reference does not authorize installation, registration, deployment, persistence, or execution. A Decision Proof reference does not grant execution authority. Neither reference is a substitute for manifest, compatibility, lifecycle, or AAOS authority evidence.

## Authority boundary

`authority_claims` requires all of these fields to be exactly `false`:

- `installation_approved`
- `tool_registration_approved`
- `deployment_approved`
- `execution_authorized`
- `production_execution_allowed`
- `risk_accepted`
- `rollback_executed`
- `audit_closed`
- `waiver_granted`
- `authority_transferred`
- `capability_pack_sealed`
- `learning_proof_sealed`
- `decision_proof_sealed`

Additional authority-claim fields and extension structures are recursively inspected with fail-closed authority semantics. Unknown non-empty values under authority-bearing keys are affirmative. A negative outer state cannot hide a nested affirmative claim.

Open machine-token fields are scanned for tokenized authority claims. Inert identifiers, manifest references, evidence references, versions, paths, and digest fields are not treated as current authority merely because an identifier contains authority-related historical text.

Capability Pack sealing is undefined and out of scope for M15 Track B. A capability pack must not claim sealed status or sealing authority. Learning Proof sealing remains AAOS-owned. Decision Proof sealing remains AAOS-owned. AAOS remains the decision sovereignty layer.

## Sensitive-value boundary

Key names and scalar values are recursively inspected for apparent passwords, access tokens, API keys, private keys, certificate material, production credentials, brokerage account numbers, and personal identifiers.

The only secret-shaped value permitted by this contract is an inert synthetic alias matching `^urn:aaos:synthetic-secret-reference:[A-Za-z0-9][A-Za-z0-9._:/-]*$`. The alias is evidence-only and cannot grant authority. It does not make a forbidden sensitive key name acceptable, and it must never contain actual secret material.

Findings identify only a deterministic category and field path; they do not echo a detected sensitive value.

## Public fixtures and execution safety

The nine public fixtures contain synthetic URNs, synthetic names, synthetic versions, and declared raw digests only. They contain no production account identifiers, credentials, personal data, external vendor content, network locations, or executable artifacts.

- `m15-capability-pack-valid-verified.json` demonstrates a fully consistent verified evidence pack.
- `m15-capability-pack-stale-specification.json` demonstrates explicit API-version drift and valid stale evidence.
- `m15-capability-pack-altered-graph.json` demonstrates quarantined graph and immutable-source binding mismatches.
- `m15-capability-pack-incompatible-runtime.json` demonstrates exact runtime-version incompatibility with no fallback.
- `m15-capability-pack-revoked.json` demonstrates revocation overriding otherwise consistent digest and runtime declarations.
- `m15-capability-pack-source-digest-mismatch.json` demonstrates a quarantined pack-level source-manifest digest mismatch.
- `m15-capability-pack-altered-derived-specification.json` demonstrates a quarantined altered derived structured-specification digest.
- `m15-capability-pack-missing-license-usage-boundary-evidence.json` demonstrates valid unverified evidence when license review and redistribution-boundary evidence are not available.
- `m15-capability-pack-executable-authority-claim.json` demonstrates fail-closed rejection when a capability pack is incorrectly treated as executable authority; every declared artifact remains non-executable.

The evaluator treats all fixture content as inert mappings. It performs no network access, subprocess execution, dynamic fixture import, file access, file mutation, external repository import, or external state transition.
