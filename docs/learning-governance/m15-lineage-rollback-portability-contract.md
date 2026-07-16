# M15 Lineage, Rollback Readiness, and Portability Contract

## Status and scope

This document defines the bounded M15 Track C lineage, rollback-readiness, deletion-evidence, and model-removal portability contract from issue #238. The supported schema version is `m15-lineage-rollback-portability/v1`.

This package is contract-first, deterministic, offline, read-only, additive, backward-compatible, and simulation-only. It evaluates caller-supplied declarations as inert evidence. It does not discover live systems, dereference an evidence reference, hash external content, access a provider, invoke a model, authorize or execute a rollback, delete data, disconnect a provider, migrate data, or transition external state.

Track C extends the lifecycle evidence available to M15 without rewriting or weakening Track A or Track B. The Track A contract from issue #232 and PR #233 remains `m15-learning-proof/v1`. The Track B contract from issue #234 and PR #237 remains `m15-capability-memory-pack/v1`. Issue #217 remains the Learning Sovereignty source issue; references to it and to Track A or Track B are provenance and linkage evidence only.

M15 remains active work and is not complete. `v0.14.0` remains a future release path and is not published. Tracker #231 remains Open.

## Governing separations

A missing dependency must not be inferred as absent. A declared dependency graph is a bounded evidence snapshot, not a live inventory. Dependency-graph completeness is a qualified claim that requires independent completeness evidence; it is not established by an empty unresolved list or by successful schema validation.

Supersession and revocation record lifecycle lineage. They do not prove that downstream memories, rules, skills, evaluations, adapters, copies, capability packs, or other derived artifacts were removed, updated, disabled, or made safe.

Rollback readiness is not rollback authorization. Rollback authorization is not rollback execution. A readiness result can support human review, but the evaluator cannot authorize, initiate, or complete a rollback.

Deletion request is not deletion authorization. Deletion authorization is not physical deletion. Deletion evidence is not proof of provider-side erasure. A qualified `deleted` evidence state records the bounded scope and evidence supplied by the caller; it does not silently expand into a universal erasure claim.

Portability evidence is not provider disconnection. Provider disconnection is not replacement-model authorization. Replacement-model authorization is not production execution. The model-removal record is a simulation-only drill and cannot be used to operate either an original or replacement model.

Track C evidence is not lifecycle authorization. Track C evaluation is not lifecycle execution. Learning Proof, Decision Proof, and Capability Memory Pack references are independently addressable linkage evidence; none becomes an authority basis by being present, valid, verified, current, or mutually linked.

The exact required boundary statement is:

> This Track C record is evidence only; it authorizes and executes no lifecycle action, rollback, deletion, provider disconnection, replacement-model use, installation, deployment, production workflow, risk acceptance, audit closure, waiver, authority transfer, Learning Proof sealing, or Decision Proof sealing.

## Record groups and common syntax

Every Track C record is a JSON object validated against the deterministic `m15-lineage-rollback-portability/v1` schema. The schema groups the record into dependency-graph evidence, supersession or revocation lineage, rollback-readiness evidence, deletion evidence, a model-removal portability drill, cross-track linkage, authority claims, and the fixed non-authoritative boundary statement. Fields that are not applicable remain explicitly represented as the schema defines; omission does not create a favorable inference.

Identifiers, versions, references, and reason codes must be non-empty and must match their schema-defined machine-token or URN syntax. Every digest is a raw lowercase SHA-256 value matching `^[0-9a-f]{64}$`. A `sha256:` prefix, uppercase hexadecimal, truncation, whitespace, or a digest in place of an identifier or version is invalid. Arrays that represent bindings, dependents, blockers, copies, derived artifacts, evidence, or reason codes are deterministic, unique collections.

Unknown top-level and ordinary nested fields fail schema validation. Open authority-bearing or extension surfaces, when provided by the schema, are recursively inspected and do not provide an authority-extension mechanism. An identifier, digest, version, snapshot reference, or evidence reference remains inert unless the record incorrectly reuses it as authority. Graph identity, completeness-evidence, and snapshot references cannot be relabeled as lifecycle requests, authorization, execution evidence, deletion evidence, revocation evidence, or provider-operation evidence.

The evaluator checks declared relationships only. It does not read referenced artifacts or independently prove that a digest binds bytes, that an evidence reference exists, that a dependency list matches a live environment, or that a stated action occurred.

## Dependency-graph evidence

The dependency-graph group records all of the following:

- `graph_id` and `graph_version`;
- `graph_integrity_digest`;
- a complete declared artifact inventory containing each artifact's identifier, type, version, and digest;
- declared `upstream_dependencies` and `downstream_dependents`;
- each dependency's purpose and criticality;
- processing and retention boundaries;
- whether a dependency is provider-specific;
- rollback and deletion sensitivity;
- the graph completeness declaration;
- the completeness-evidence reference;
- the unresolved-dependency list; and
- the graph-snapshot reference.

Every dependency endpoint supplies an artifact identifier, version, and digest and must resolve to exactly one declared graph node, where the artifact type is declared. An upstream binding and the corresponding downstream declaration must agree in both directions. An endpoint mismatch, conflicting version or digest, duplicate edge, self-contradictory purpose, or omitted reverse binding fails closed. The evaluator does not repair or infer a missing edge.

In v1, dependency purpose and criticality are declared on each artifact graph node and qualify that node's dependency posture across its listed bindings. They describe why the declared artifact participates in those dependencies and how consequential that dependency posture is within the snapshot; they do not create or infer an omitted edge. Processing boundary, retention boundary, provider-specific dependency, rollback sensitivity, and deletion sensitivity remain evidence classifications. They do not authorize processing, retention, provider use, rollback, or deletion.

A graph may declare itself complete only when a non-empty completeness-evidence reference is present, the unresolved-dependency list is empty, all declared upstream and downstream bindings are internally consistent, and the graph snapshot is identified. A complete declaration without that evidence fails closed. An incomplete graph remains valid bounded evidence only when incompleteness and every known unresolved dependency are explicit. An empty list in an unqualified or incomplete snapshot never proves that no additional dependency exists.

## Supersession and revocation lineage

Each lineage entry records:

- the affected artifact identifier, current version, and digest, with type obtained from its exact graph binding;
- whether the event is supersession or revocation;
- a superseding or replacement reference where required;
- the revocation or supersession reason;
- the effective timestamp;
- known downstream dependents;
- unresolved dependents;
- archival-evidence state; and
- the evidence digests that qualify the entry.

The affected artifact must bind deterministically to the dependency graph. Every known downstream dependent must be declared consistently in the graph snapshot, and every unresolved dependent must remain visible. A caller must not omit an unresolved dependent to obtain a favorable outcome.

Supersession requires a non-empty superseding or replacement reference. Revocation requires a non-empty reason and qualifying revocation evidence. Affected-artifact, replacement-artifact, archival-evidence, and revocation-evidence references are distinct roles; an artifact identifier cannot be relabeled as its own lifecycle evidence, and archival and revocation evidence references must differ. Malformed evidence digests, contradictory graph bindings, missing effective timestamps, and omitted dependents fail closed.

Archival evidence can remain available after an artifact is superseded or revoked. Retention of archival evidence does not reactivate the artifact and does not prove downstream removal. Conversely, absence of archival evidence does not prove deletion.

## Rollback-readiness evidence

The rollback group records:

- `rollback_request_id`;
- the current artifact identifier, version, and digest, bound to its declared graph type;
- the target artifact identifier, version, and digest;
- the dependency-graph snapshot reference;
- affected dependents;
- incompatible dependents;
- unresolved dependents;
- compatibility assessment;
- whether human review is required;
- an authorization reference, if separately supplied;
- an execution-evidence reference, if historical execution is claimed;
- readiness state;
- execution state;
- completion claim; and
- deterministic reason codes.

Current and target artifact bindings must be distinct, complete, of the same declared artifact type, and consistent with the referenced graph snapshot. The affected-dependent set must cover all declared downstream dependents relevant to the rollback. Incompatible and unresolved dependents remain explicit subsets of the affected set; they cannot be hidden by a favorable compatibility statement.

The evaluator may assess rollback readiness only. A rollback can be assessed as ready only when dependency evidence is complete and qualified, current and target bindings are consistent, the compatibility assessment is favorable, and both incompatible and unresolved dependent lists are empty. Otherwise readiness is blocked and the deterministic reason codes identify every known blocker. A readiness result never supplies an authorization reference.

An authorization reference is inert evidence of a separately governed input. Its presence is not authorization, and its absence cannot be filled by Learning Proof, Decision Proof, Capability Memory Pack, identity, policy, reviewer, or schema-validity evidence. Request, artifact, authorization, and execution-evidence identifiers are distinct roles and must not reuse one another or a cross-track linkage reference. Human review remains required wherever the schema or compatibility evidence says it is required.

Execution state and completion claim record caller-supplied historical evidence only. A rollback-execution or completion claim without a qualifying execution-evidence reference fails closed. Even with such a reference, the evaluator reports bounded evidence and does not verify, authorize, or execute rollback.

## Deletion-pending and qualified deleted evidence

Track C uses the lifecycle values `deletion-pending` and `deleted`. This is additive qualification of lifecycle evidence; it does not alter the same values already present in the Track A vocabulary.

The deletion group records:

- `deletion_request_id`;
- target identifier, version, and digest, bound to its declared graph type;
- deletion scope;
- known copies;
- derived artifacts;
- downstream dependents;
- unresolved dependencies;
- retention boundary;
- authorization reference;
- local deletion evidence;
- independently qualified local, external, or provider evidence;
- residual-risk statement;
- evidence qualification;
- completion status; and
- deterministic reason codes.

`deletion-pending` preserves the request and current blockers without implying authorization or deletion. A `request-only` qualification cannot carry local or independent deletion evidence, and `pending-unresolved` requires an explicit unresolved copy, dependent, or dependency. It is required when known copies, downstream dependents, derived artifacts, or unresolved dependencies prevent a qualified completion statement.

A `deleted` evidence state requires an explicit bounded scope, a matching target binding, qualified evidence for every declared scope, no unresolved copies or dependents, an explicit residual-risk statement, and a completion status consistent with the evidence qualification. Local scope requires qualified local evidence; an external or provider scope requires the corresponding independently verified evidence. The state means only that the stated evidence supports the stated scope. It does not automatically prove physical erasure, provider-side deletion, backup deletion, cache deletion, training-data removal, model-weight unlearning, deletion from every derived artifact, or deletion from every external system.

External or provider evidence must identify the specific independently evidenced claim and scope. A physical-erasure, provider-deletion, backup-deletion, cache-deletion, training-data-removal, or model-unlearning claim fails closed unless the required independent evidence and corresponding qualification are present. A generic deletion receipt, authorization reference, local evidence record, lifecycle label, empty unresolved list, or successful evaluator result cannot be reused as that independent evidence.

Known copies, derived artifacts, and other downstream dependents are disjoint evidence categories whose union must match the target's declared graph dependents. A known copy must resolve to a graph artifact of type `copy`, and a copy cannot be relabeled as another dependent category. Request, target, authorization, local-evidence, and independent-evidence references remain distinct roles; independent evidence references and digests must also be unique. These artifacts remain explicit even when they fall outside the qualified deletion scope. Residual risk must describe what remains unproven or outside scope and cannot assert that no risk remains. The evaluator never converts `deleted` into an unqualified universal-erasure finding, and this v1 contract cannot qualify an `all_external_systems_deleted_claimed` assertion because it has no live or independently complete inventory of every external system.

## Simulation-only model-removal portability drill

The portability group is an inert simulation record. It evaluates whether:

- Learning Proof remains readable;
- Decision Proof references remain interpretable;
- Capability Memory Packs remain readable;
- private evaluations remain usable;
- organizational memory remains interpretable;
- export manifests remain available;
- provider-specific dependencies are identified;
- replacement-model requirements are explicit;
- degraded-mode operation is represented;
- deletion and revocation evidence remain available;
- unsupported dependencies are quarantined; and
- portability blockers remain visible.

Each assessment is explicit and evidence-bound. A favorable readability or availability assessment requires the corresponding declared graph artifact type: `learning-proof`, `decision-proof`, `capability-memory-pack`, `private-evaluation`, `organizational-memory`, `export-manifest`, or `lifecycle-evidence`. The dependency graph must identify every provider-specific dependency relevant to the drill. Replacement-model requirements are compatibility requirements only, not a model selection, approval, invocation, or migration instruction. Degraded mode and quarantine are simulated evidence states; the evaluator does not activate them.

A successful portability result requires all required evidence to remain available or interpretable as declared, every provider-specific dependency to be identified, replacement requirements and degraded mode to be explicit, every unsupported dependency to be quarantined, and no unresolved portability blocker. An omitted provider-specific dependency, a provider-specific blocker, or an unsupported dependency that remains unresolved or unquarantined blocks portability. A portability result also fails closed when replacement-model use is represented as authorized.

The drill must not disconnect a real provider; invoke an original or replacement model; migrate live data; access provider accounts; use credentials; modify provider settings; export confidential information; or execute production workflows. A successful simulation is evidence about the declared snapshot only.

## Deterministic cross-track linkage

Cross-track linkage binds Track C evidence to separately addressable records without importing or invoking another track's evaluator. Each linkage supplies an exact schema version, record identifier in `reference`, separately declared `track_c_evidence_record_digest`, track-specific source or manifest digest where defined, usage classification, and the matching dependency-graph artifact binding.

A Track A link uses `m15-learning-proof/v1` and binds to a Learning Proof identifier. The linked record digest is a distinct Track C declaration; Track A's `source_integrity_hash` binds the Learning Proof source and must not be reinterpreted as the digest of a serialized Learning Proof record. A Learning Proof reference is linkage evidence only and must not be treated as rollback, deletion, installation, registration, activation, persistence, training, tool, or execution authority.

A Track B link uses `m15-capability-memory-pack/v1` and binds to a Capability Memory Pack identifier. Track B does not expose a whole-pack digest or top-level pack version. Track C therefore records a separately named record digest and exact schema-version binding rather than relabeling a source, license, derived-manifest, immutable-source, artifact, or graph digest. Capability Memory Pack evidence remains non-executable and must not be treated as installed, registered, activated, deployed, or executable authority.

A Decision Proof reference remains inert linkage evidence. It does not authorize deletion or execution. Decision Proof sealing remains AAOS-owned.

Identifier, type, version, digest, or graph-binding disagreement fails closed. Cross-track linkage references cannot be reused as graph-completeness, graph-snapshot, archival, revocation, rollback-authorization, rollback-execution, deletion-authorization, deletion-execution, independent-deletion, or provider-operation evidence. A matching reference establishes caller-declared internal consistency only; it does not prove content authenticity, lifecycle authorization, or external availability. Track A and Track B remain independently valid under their existing contracts, and Track C does not add required fields to either one.

## Authority boundary

The fixed `authority_claims` fields are all required to be exactly `false`: `release_approved`, `governance_authority_granted`, `policy_authority_granted`, `identity_authority_granted`, `risk_accepted`, `deployment_approved`, `rollback_authorized`, `rollback_executed`, `deletion_authorized`, `deletion_executed`, `production_execution_allowed`, `audit_closed`, `waiver_granted`, `authority_transferred`, `capability_pack_installed`, `capability_pack_executable`, `learning_proof_sealed`, and `decision_proof_sealed`.

The deletion-claim and portability-drill groups separately represent physical erasure, provider deletion, backup deletion, cache deletion, training-data removal, model unlearning, provider disconnection, provider access, model invocation, replacement-model authorization, confidential export, and production workflow execution. Those fields remain subject to their own fixed-false, independent-evidence, qualification, and simulation-only rules; moving a claim outside `authority_claims` does not bypass the boundary.

Additional authority-bearing fields, completion assertions, open machine-token surfaces, and extension structures are inspected recursively with fail-closed semantics. Unknown non-empty values under an authority-bearing key are affirmative. A false or negative outer value cannot hide a nested affirmative claim. Governance, policy, identity, risk-acceptance, deployment, rollback, deletion, audit-closure, waiver, authority-transfer, Decision Proof sealing, or Learning Proof sealing claims fail the boundary.

Evidence-state fields may record bounded historical evidence only where this contract expressly defines their qualifications. They must not be reused as present authority, and authority fields must not be relabeled as evidence fields. Inert identifiers, versions, digests, snapshot references, evidence references, reason histories, and lifecycle labels are not treated as current authority merely because they contain historical words; their values and uses remain subject to their own binding rules.

Learning Proof references are linkage evidence only. Decision Proof references are linkage evidence only. Capability Memory Pack references remain non-executable evidence. Capability Pack sealing remains undefined and out of scope for Track B. Learning Proof sealing remains AAOS-owned. Decision Proof sealing remains AAOS-owned. AAOS remains the decision sovereignty layer.

## Fail-closed evaluation rules

The evaluator returns an unfavorable result and deterministic reason codes for every applicable failure, including:

- a missing or malformed identifier, version, reference, timestamp, reason code, or digest;
- an inconsistent artifact, upstream, downstream, snapshot, or cross-track binding;
- a false dependency-graph completeness claim or omitted completeness evidence;
- a missing downstream dependency declaration or an unresolved dependent omitted from the declared unresolved set;
- supersession without a replacement reference;
- revocation without a reason or qualifying evidence;
- rollback readiness claimed while a dependent is unresolved or incompatible;
- rollback execution or completion claimed without qualifying execution evidence;
- deletion completion claimed while a known copy, derived artifact, dependent, or dependency remains unresolved within scope;
- physical erasure, provider deletion, backup deletion, cache deletion, training-data removal, or model unlearning claimed without independent qualified evidence;
- portability claimed while a provider-specific or unsupported blocker remains unresolved or unquarantined;
- original- or replacement-model use represented as authorized;
- Learning Proof treated as rollback, deletion, installation, registration, activation, persistence, training, tool, or execution authority;
- Decision Proof treated as deletion or execution authority;
- Capability Memory Pack treated as installed, registered, activated, deployed, or executable authority; or
- any forbidden governance, policy, identity, risk-acceptance, deployment, rollback, deletion, audit-closure, waiver, authority-transfer, Learning Proof sealing, or Decision Proof sealing claim.

Multiple failures are reported together. Findings are stable machine-readable reason codes, sorted and deduplicated. Caller-declared findings never replace evaluator recomputation. Structural validity, dependency consistency, lineage consistency, rollback readiness, deletion qualification, portability readiness, cross-track linkage, and authority validity remain separately observable; one passing dimension cannot erase another dimension's failure.

## Standalone synthetic public fixtures

Every public fixture is a standalone file under `examples/public-integration-pack-pilot/`. In-memory mutations may supplement these cases but do not replace them.

- `m15-lineage-rollback-portability-valid-complete-dependency-graph.json` demonstrates a complete graph with qualified completeness evidence and consistent bidirectional bindings.
- `m15-lineage-rollback-portability-missing-downstream-dependency-declaration.json` demonstrates that a missing downstream declaration is not inferred as absence.
- `m15-lineage-rollback-portability-superseded-learning-artifact-known-dependents.json` demonstrates supersession with known dependents retained explicitly.
- `m15-lineage-rollback-portability-revoked-capability-pack-unresolved-downstream-use.json` demonstrates revocation with unresolved downstream use and no implied removal.
- `m15-lineage-rollback-portability-rollback-ready-complete-dependency-evidence.json` demonstrates readiness evidence with a qualified complete graph and no unresolved or incompatible dependent.
- `m15-lineage-rollback-portability-rollback-blocked-incompatible-dependent.json` demonstrates a rollback blocked by an incompatible dependent.
- `m15-lineage-rollback-portability-deletion-pending-unresolved-copies.json` demonstrates deletion-pending evidence with unresolved copies.
- `m15-lineage-rollback-portability-qualified-deleted-no-physical-erasure.json` demonstrates bounded qualified deleted evidence without a physical-erasure claim.
- `m15-lineage-rollback-portability-false-physical-provider-erasure-claim.json` demonstrates fail-closed physical-deletion and provider-erasure claims without independent qualification.
- `m15-lineage-rollback-portability-model-removal-drill-success.json` demonstrates a successful simulation-only model-removal drill.
- `m15-lineage-rollback-portability-model-removal-drill-provider-specific-blocker.json` demonstrates portability blocked by a provider-specific dependency.
- `m15-lineage-rollback-portability-replacement-model-use-incorrectly-authorized.json` demonstrates fail-closed treatment of replacement-model use as authorized.
- `m15-lineage-rollback-portability-learning-proof-rollback-authority.json` demonstrates that Learning Proof cannot become rollback authority.
- `m15-lineage-rollback-portability-decision-proof-deletion-execution-authority.json` demonstrates that Decision Proof cannot become deletion or execution authority.

All public fixtures contain synthetic URNs, names, versions, timestamps, paths, references, and raw digests only. They contain no production identifiers, personal data, confidential information, credentials, provider account data, external vendor content, or executable payloads.

## Evaluator safety

The evaluator accepts caller-supplied inert data only. It performs no network access, subprocess or shell execution, dynamic external import, model invocation, file discovery, fixture loading, file mutation, provider access, credential access, external state transition, or production workflow. It does not mutate the input object.

Detected secret-like content is reported by deterministic category and field path only; a finding must not echo the secret value. Results and findings are deterministic across repeated evaluation. Findings are sorted and deduplicated.

Schema validation and evaluator execution remain offline. The schema validates the record's declared shape. The evaluator independently recomputes semantic consistency and authority boundaries; schema validity alone is never a favorable lifecycle, readiness, deletion, portability, or authority result.

## Strict non-goals

This contract provides no network call, provider access, production credential use, model invocation, training, fine-tuning, live memory access, live rollback, live deletion, physical deletion, unqualified provider-erasure claim, tool installation, tool registration, generated-capability activation, production execution, deployment authorization, risk acceptance, audit closure, tag, GitHub Release, or `v0.14.0` publication.

It does not modify README release or milestone declarations, close tracker #231, or claim M15 completion. It does not seal a Learning Proof or Decision Proof and does not transfer any AAOS authority.
