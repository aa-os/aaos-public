# External Evidence Admission

AAOS treats Twinkle Hub MCP output as an external evidence candidate, not as a verification authority. A successful connection or retrieval is only one observation. It does not establish freshness, extraction integrity, admission, or Decision Proof sealing.

The deterministic admission model is defined by:

- [external evidence admission schema](../../schemas/external-evidence-admission.schema.json)
- [external evidence admission evaluator](../../runtime/external_evidence_admission_evaluator.py)
- [Twinkle Hub deterministic fixtures](../../examples/external-evidence-admission/twinkle-hub-fixtures.json)

The evaluator performs no network calls and requires no Hub credentials.

## State Model

Connection readiness, data freshness, extraction integrity, and the final admission result are independent fields.

| Dimension | States | Passing state |
| --- | --- | --- |
| `connection_status` | `ready`, `auth_failed`, `unreachable`, `misconfigured`, `unknown` | `ready` |
| `freshness_status` | `current`, `stale`, `unknown`, `not_applicable` | `current`, or `not_applicable` for an immutable paper, document, or endpoint observation |
| `extraction_status` | `complete`, `partial`, `empty`, `schema_mismatch`, `fallback_required` | `complete` |
| `admission_result` | `verified`, `degraded`, `rejected` | `verified` |

`freshness_status` is derived from the recorded source publication time, retrieval time, and an AAOS-owned fixed threshold. It is never calculated against the evaluator's wall clock. Mutable datasets cannot use `not_applicable`.

`extraction_status` is derived from whether extraction ran, the reported and verified item counts, required-field gaps, schema validity, and structured/raw source availability. A positive response envelope or reported count cannot override incomplete structured content.

## Supported Timestamp Profile

`retrieved_at` and a non-null `source_published_at` use a strict known-offset RFC 3339 subset shared by the schema and evaluator. The profile requires a timezone, limits hours to `00`–`23`, minutes and seconds to `00`–`59`, and permits one to six fractional-second digits. `T` and `Z` are accepted case-insensitively.

`Z` and `+00:00` are known UTC references. `+00:00` and other known numeric offsets such as `+08:00` or `-04:00` are canonicalized to the equivalent UTC `Z` instant without dropping supported fractional precision.

The RFC 3339 unknown-local-offset convention `-00:00` is not admissible Decision Proof evidence. The evaluator emits the bounded finding `unknown_local_offset_not_allowed`, replaces the untrusted timestamp with the existing safe invalid-input sentinel, and rejects the record. It never stores the supplied unknown-offset instant as the corresponding known UTC `Z` instant. A nullable invalid `source_published_at` is stored as `null`.

Leap seconds (`:60`) are not supported by this profile. Both schema and runtime restrict seconds to `00`–`59`; leap-second, timezone-naive, malformed, or over-precision timestamps fail closed rather than being normalized.

## Trusted Policy Binding

Freshness thresholds and admission policy are governance inputs, not external-source claims. The caller supplies an AAOS-owned trusted policy snapshot to the evaluator. The replay record preserves the same version, threshold, and stale/unknown/partial/fallback outcomes, and the gate rejects any candidate whose embedded snapshot differs.

The v1 policy permits stale evidence to be degraded or rejected according to the selected trusted profile. Unknown freshness is always rejected. An external candidate cannot make stale evidence current by increasing its own threshold, select a more permissive policy, or change the policy version.

This bounded gate also pins the Twinkle Hub source identity and endpoint, and permits only the deterministic fixture client/authentication descriptors represented by the schema. Arbitrary source names, endpoints, client types, authentication modes, or non-Hub evidence identifiers are canonicalized to non-secret sentinels and rejected.

## Fail-Closed Admission

The evaluator applies the most restrictive result across the independent dimensions:

| Condition | Admission | Governed decision path | Inspection storage | Decision Proof sealing eligibility |
| --- | --- | --- | --- | --- |
| ready connection, current or valid non-applicable freshness, complete extraction | `verified` | eligible when no model or governance failure is recorded | allowed | eligible for the separate AAOS-owned sealing step |
| stale evidence under the default policy | `degraded` | blocked | allowed with warning codes and a raw-source reference | blocked |
| stale evidence under a strict policy | `rejected` | blocked | replay metadata only | blocked |
| partial or fallback-required extraction with warnings and a raw/PDF reference | `degraded` | blocked | allowed for inspection | blocked |
| empty or schema-mismatched extraction | `rejected` | blocked | replay metadata only | blocked |
| authentication, reachability, configuration, unknown-source, or source-absence failure | `rejected` | blocked | replay metadata only | blocked |
| missing provenance, secret material, inconsistent classification, or a result more permissive than policy | `rejected` | blocked | sanitized replay metadata only | blocked |

Only `verified` evidence can be marked `decision_proof_sealing_eligible`. Eligibility is not sealing. The evaluator does not emit a sealed Decision Proof artifact and cannot transfer sealing authority.

Correctly classified `degraded` and `rejected` records remain valid replay records. Their admission state is not silently promoted. Rejected evidence cannot influence an irreversible or accountable governed decision.

## Replay-Safe Metadata

Every record preserves:

- source identity, source type, endpoint reference, client type, and authentication mode
- dataset or paper identifier
- fixed `retrieved_at`
- source batch or version
- authoritative source reference
- connection, freshness, extraction, and admission states
- sanitized error category
- opaque raw/PDF fallback reference
- AAOS-owned policy version, fixed freshness threshold, and stale/unknown/partial/fallback handling
- explicit warning codes
- reported and verified item counts plus missing-field paths
- source, extraction, model, and governance failure classification

Replay uses separate failure fields:

- `source_failure` distinguishes source absence, authentication, connection, configuration, freshness, and unknown-source failures.
- `extraction_failure` distinguishes partial, empty, schema-mismatched, and fallback-required structured extraction.
- `model_failure` records downstream model interpretation or output-validation failure.
- `governance_failure` records policy or sealing-boundary failure.

An OAuth failure before retrieval is a source authentication failure, not an extraction failure. A reachable source that returns empty structured content is an extraction failure, not source absence. Model and governance failures remain independently attributable even when the external evidence itself passed admission.

This classification complements [Decision Proof runtime replay](decision-proof-runtime-replay.md) and preserves the [Decision Proof sealing boundary](decision-proof-sealing-boundary.md).

## Raw-Source And PDF Fallback

Degraded evidence may retain an opaque raw-source or PDF reference for inspection and replay. AAOS stores the reference and deterministic warning codes, not the raw Hub response payload.

Fallback does not mutate a degraded or rejected structured record into verified evidence. PDF or raw-source processing creates a new evidence candidate with its own connection, freshness, extraction, and admission evaluation. A raw-source reference is not authoritative evidence by itself and does not bypass extraction checks.

Rejected authentication records may state that no fallback was available before retrieval. They retain sanitized failure metadata only and cannot enter the decision path.

## Secret Exclusion

Admission serialization uses an allowlist, bounded enums, safe identifier/reference formats, and canonical values before any record can be returned for storage. Malformed fields are replaced by non-secret sentinels and force rejection. AAOS never persists:

- OAuth access tokens
- authorization codes
- cookies or `Set-Cookie` values
- client secrets
- raw authorization or proxy-authorization headers

Raw exception text and raw Hub payloads are not part of the admission schema. Error reporting uses bounded categories such as `oauth_token_exchange_failed`, `source_unreachable`, `freshness_check_failed`, and `extraction_integrity_failed`. Secret or unexpected material makes the record fail closed; it is never echoed into findings, logs, snapshots, serialized evidence, or errors.

## Deterministic Twinkle Hub Evidence

The checked-in fixtures use fixed identifiers, timestamps, batches, thresholds, and opaque fallback references. Tests do not call the live Hub service.

- [ai-twinkle/Hub#6](https://github.com/ai-twinkle/Hub/issues/6) — partial mixed-question extraction and empty structured questions despite PDF availability
- [ai-twinkle/Hub#7](https://github.com/ai-twinkle/Hub/issues/7) — stale `pcc-tender` batch relative to the authoritative source
- [ai-twinkle/Hub#8](https://github.com/ai-twinkle/Hub/issues/8) — OAuth token exchange failure represented only by a sanitized category

## Boundary

External sources may provide evidence candidates and raw-source references. Deterministic evaluators may classify admission, surface findings, preserve replay metadata, recommend fail-closed handling, and establish sealing eligibility.

They must not seal Decision Proof, accept risk, execute rollback, execute fail-closed, close audits, grant waivers, change identity trust, change policy authority, change decision routing, or make final governance judgments.

Decision Proof sealing remains AAOS-owned.

AAOS remains the decision sovereignty layer.
