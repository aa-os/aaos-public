# M15 Core Learning Proof Contract

## Status and scope

This document defines the first bounded M15 Track A Learning Proof contract. The supported schema version is `m15-learning-proof/v1`.

This package is contract-first, deterministic, offline, and simulation-only. It records and evaluates inert evidence. It does not implement persistent memory, training, skill activation, tool registration, production execution, live quarantine, live revocation, live rollback, live deletion, proof sealing, or an external state transition.

M15 remains active work and is not complete. `v0.14.0` remains a future release path and is not published. Tracker #231 remains Open.

## Core separation

Learning readiness is not learning authorization. Authorization evidence is not execution authority. Retrieval is not verification, verification is not authorization, and authorization evidence is not execution.

A Decision Proof must not automatically become organizational memory. A Decision Proof reference is optional linkage evidence; it is not an authority basis by itself and cannot authorize memory, skill creation, training, retention, or execution. Learning Proof and Decision Proof remain independently addressable but linkable, and Learning Proof does not replace Decision Proof.

An explicit `authorization_outcome` and a governed `authority_basis_reference` are required. The authority-basis reference must begin with `urn:aaos:m15:authority-basis:` and have a non-empty suffix. Authorization must not be inferred from identity labels, reviewer names, source ownership, verification success, schema validity, Decision Proof presence, a trusted-looking marker, or lifecycle state alone. `source_self_asserted_trust_marker` is inert source data and never authority evidence.

## Required vocabulary

The following values are closed enumerations for `m15-learning-proof/v1`:

| Field | Values |
| --- | --- |
| `source_type` | `prompt`, `trace`, `correction`, `evaluation`, `decision`, `tool-output`, `specification`, `generated-artifact` |
| `source_owner` | `organization`, `employee`, `customer`, `provider`, `shared`, `unknown` |
| `sensitivity` | `public`, `internal`, `confidential`, `restricted` |
| `processing_boundary`, `retention_boundary` | `local`, `organization`, `tenant`, `approved-provider`, `external`, `public` |
| `requested_purpose`, non-null `authorized_purpose` | `ephemeral-inference`, `evaluation`, `memory`, `skill`, `training`, `audit` |
| `authorization_outcome` | `deny`, `allow-ephemeral`, `allow-evaluation-only`, `allow-memory`, `allow-skill`, `allow-training`, `quarantine`, `require-review` |
| `lifecycle_state` | `proposed`, `verified`, `quarantined`, `active`, `stale`, `incompatible`, `superseded`, `revoked`, `deletion-pending`, `deleted` |

Issue #232 does not define a binding transformation-type enumeration. Therefore, `transformation_type` is a required non-empty string rather than a closed enum. Values such as `none`, `normalization`, `summarization`, `rule`, `memory`, `skill`, and `adapter` come from the illustrative source design in #217 and are not promoted to binding M15 vocabulary by this contract.

The Learning Sovereignty Boundary governs these operation names from tracker #231: `capture`, `processing`, `retention`, `transformation`, `evaluation`, `memory creation`, `skill creation`, `training`, `distillation`, `export`, `sharing`, `revocation`, and `deletion`. Listing an operation is not authorization to perform it.

## Flat record

Every Learning Proof is a single JSON object with exactly the following required top-level fields:

| Field | Contract |
| --- | --- |
| `schema_version` | Exactly `m15-learning-proof/v1`. |
| `learning_proof_id` | Non-empty identifier. |
| `source_type` | Closed source-type enum. |
| `source_reference` | Non-empty inert source reference. The evaluator does not dereference it. |
| `source_owner` | Closed ownership enum. |
| `source_integrity_hash` | Raw lowercase SHA-256 digest: exactly 64 hexadecimal characters. |
| `source_self_asserted_trust_marker` | Non-empty string or `null`; never authority evidence. |
| `sensitivity` | Closed sensitivity enum. |
| `requested_purpose` | Closed purpose enum. |
| `authorized_purpose` | Closed purpose enum or `null`. |
| `authorization_outcome` | Closed outcome enum. |
| `authority_basis_reference` | Governed reference with prefix `urn:aaos:m15:authority-basis:` and a non-empty suffix, distinct in meaning from Decision Proof linkage. |
| `policy_version` | Non-empty policy-version reference. |
| `processing_boundary` | Closed sovereignty-boundary enum. |
| `retention_boundary` | Closed sovereignty-boundary enum. |
| `boundary_evidence_reference` | Governed reference with prefix `urn:aaos:m15:boundary-evidence:` or `null`; mandatory when either boundary is `external` or `public`. |
| `transformation_type` | Non-empty string; not a closed enum in this version. |
| `transformation_input_references` | Non-empty array of unique, non-empty references. |
| `transformation_output_reference` | Non-empty reference. |
| `lifecycle_state` | Closed lifecycle enum. |
| `effective_timestamp` | RFC 3339 date-time string. |
| `expiration_timestamp` | RFC 3339 date-time string or `null`. |
| `superseded_by_reference` | Non-empty reference or `null`. |
| `rollback_target` | Non-empty reference or `null`. |
| `deletion_evidence_reference` | Non-empty reference or `null`. |
| `related_decision_proof_reference` | Non-empty reference or `null`; linkage only. |
| `contamination_detected` | Boolean contamination state. |
| `contamination_evidence_references` | Array of unique, non-empty references; non-empty when contamination is detected. |
| `authority_claims` | Required fixed-false claim set plus evaluator-inspected extensions. |
| `evaluator_findings` | Array of unique tokens from the closed v1 evidence-finding vocabulary. Input findings do not replace evaluator recomputation. |
| `non_authoritative_boundary_statement` | Exact evidence-only statement fixed by the schema. |

Unknown top-level fields fail schema validation. Unknown fields are allowed only inside `authority_claims`, where the evaluator inspects them recursively and fails closed on unknown non-empty authority-bearing claims.

The closed declared-finding vocabulary is `evaluation_only_authorization_recorded`, `decision_proof_linkage_is_non_authoritative`, `self_asserted_trust_marker_ignored`, `rejection_evidence_recorded`, `source_contamination_detected`, `revoked_or_poisoned_source_dependency_detected`, `learning_artifact_quarantined`, `persistence_and_execution_not_authorized`, `synthetic_identity_label_present`, `synthetic_reviewer_label_present`, `verification_success_observed`, and `schema_validity_observed`. The final four tokens record inert observations and never become authority evidence. Unknown input findings fail closed; result findings are recomputed independently by the evaluator.

`source_integrity_present` reports only that the source reference and declared digest are present. `source_integrity_format_valid` reports only the lowercase 64-hex SHA-256 syntax. This mapping-only evaluator does not read source content or prove that the declared digest binds that content.

## Outcome and purpose mapping

The deterministic mapping is:

| Outcome | Requested purpose | Authorized purpose |
| --- | --- | --- |
| `allow-ephemeral` | `ephemeral-inference` | `ephemeral-inference` |
| `allow-evaluation-only` | `evaluation` | `evaluation` |
| `allow-memory` | `memory` | `memory` |
| `allow-skill` | `skill` | `skill` |
| `allow-training` | `training` | `training` |
| `deny` | Any defined purpose | `null` |
| `quarantine` | Any defined purpose | `null` |
| `require-review` | Any defined purpose | `null` |

This version defines no `allow-audit` outcome. An `audit` request therefore remains denied, quarantined, or pending review with `authorized_purpose: null` until a separately governed contract revision supplies an explicit compatible authorization outcome.

An evaluation-only outcome forbids memory, skill, training, and persistent retention beyond the declared evaluation purpose. A coherent denial, quarantine, or review-pending record can be valid evidence while authorizing no persistence.

## Boundary, lifecycle, and contamination rules

Use of `external` or `public` as either processing or retention boundary requires a `boundary_evidence_reference` beginning with `urn:aaos:m15:boundary-evidence:` and containing a non-empty suffix. A source reference, trusted marker, Decision Proof reference, authority-basis reference, destination name, provider identity, source owner, or public-looking label is not boundary evidence.

A `deny` outcome must use a non-active lifecycle state and authorize no purpose. Detected contamination and a `quarantine` outcome both require `lifecycle_state: quarantined`, at least one contamination-evidence reference, and no authorized purpose. Contamination evidence cannot coexist with an allow outcome.

A lifecycle state of `superseded`, `revoked`, `deletion-pending`, or `deleted` cannot authorize new memory, skill, or training persistence. These states, as well as denied and quarantined evidence, must not be treated as active authorization.

`deletion-pending` records intent or workflow state, not physical deletion. A `deleted` claim requires an explicit `deletion_evidence_reference`. Even with a reference, this evaluator records evidence only and does not perform or independently prove physical deletion. A rollback target or finding likewise does not prove rollback execution.

## Authority boundary

`authority_claims` requires all of these booleans to be exactly `false`:

- `release_approved`
- `deployment_approved`
- `execution_authorized`
- `risk_accepted`
- `rollback_executed`
- `deletion_executed`
- `audit_closed`
- `waiver_granted`
- `authority_transferred`
- `learning_proof_sealed`
- `decision_proof_sealed`

Additional claim fields are retained for fail-closed evaluator inspection; they are not an extension mechanism for granting authority. A negative outer state cannot hide a nested affirmative claim.

The exact required statement is:

> This Learning Proof is evidence only; it grants no persistence, training, skill, tool, execution, rollback, deletion, sealing, or governance authority.

Learning Proof sealing remains AAOS-owned. Decision Proof sealing remains AAOS-owned. AAOS remains the decision sovereignty layer.

## Public fixtures and execution safety

The three public fixtures use synthetic URNs, synthetic contents, and raw SHA-256 digests. They contain no production account identifiers, credentials, personal data, confidential prompts, or executable content.

The evaluator treats fixture content as inert JSON data. It performs no network access, subprocess execution, dynamic fixture import, command execution, credential access, file mutation, or external state transition.

The approved fixture demonstrates evaluation-only authorization. The denied fixture demonstrates that a self-declared `trusted` marker does not become authority. The quarantine fixture demonstrates deterministic contamination evidence without authorizing memory, skill, training, execution, rollback, deletion, or sealing.
