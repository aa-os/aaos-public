# AAOS-RFC-0000 — Specification Process, Normative Language, and Status Model

## Document metadata — Informative

```text
RFC ID: AAOS-RFC-0000
Title: Specification Process, Normative Language, and Status Model
RFC Class: process
Candidate Package ID: AAOS-RFC-0000-CANDIDATE-PACKAGE-001
Candidate Version: 0.1.0-candidate.1
rfc_review_state = under_review
rfc_status = not_assigned
proposed_status = candidate
Semantic Manifest Canonicalization: RFC 8785 JCS
Mandatory Digest Baseline: SHA-256
Semantic Manifest SHA-256: 522296812eb8b5e88a5353643a27500447459a6cf747d20b347993aa7b0ae7bc
Source Issues: #277, #279
Downstream Dependency: #278
```

`proposed_status = candidate` is a target for a later human disposition. It is
not the current RFC lifecycle status. The current lifecycle value remains
`rfc_status = not_assigned`.

## 1. Abstract — Informative

AAOS-RFC-0000 defines the governance process for AAOS RFCs. It specifies RFC
identity, normative language, requirement identifiers, RFC classes, review
states, lifecycle statuses, review roles, change classification, versioning,
emergency restrictions, semantic precedence, institutional applicability,
traceability, migration, and exact candidate disposition.

This RFC governs how AAOS specifications become normative. It does not define
the architecture, objects, states, evidence, interfaces, or conformance
semantics owned by downstream Semantic Core RFCs.

## 2. Scope — Normative

**Clause ID: `AAOS-RFC-0000-S02-C01`**
**Requirements: `AAOS-REQ-0000-012`, `AAOS-REQ-0000-030`,
`AAOS-REQ-0000-031`**

This RFC applies to every AAOS Process, Standards Track, Profile,
Informational, and Experimental RFC and to every downstream artifact that
implements, represents, evaluates, or claims conformance to an AAOS RFC.

**Clause ID: `AAOS-RFC-0000-S02-C02`**
**Requirement: `AAOS-REQ-0000-033`**

An accepted or stable RFC does not authorize implementation, release,
deployment, certification, risk acceptance, waiver, audit closure, rollback,
restore, cutover, or proof sealing.

**Clause ID: `AAOS-RFC-0000-S02-C03`**
**Requirement: `AAOS-REQ-0000-034`**

Unknown mandatory RFC semantics MUST produce `fail_closed`, `not_evaluable`,
or an explicit human disposition according to the applicable profile. They
MUST NOT be ignored, guessed, downgraded, or mapped to permissive behavior.

## 3. Normative language — Normative

**Clause ID: `AAOS-RFC-0000-S03-C01`**
**Requirement: `AAOS-REQ-0000-004`**

AAOS RFCs MUST use the uppercase terms `MUST`, `MUST NOT`, `SHOULD`,
`SHOULD NOT`, and `MAY` according to RFC 2119 as clarified by RFC 8174. New
AAOS normative text SHOULD NOT use `SHALL` or `SHALL NOT`.

**Clause ID: `AAOS-RFC-0000-S03-C02`**
**Requirements: `AAOS-REQ-0000-003`, `AAOS-REQ-0000-004`**

Normative force applies only in explicitly normative sections or requirement
records. Examples, diagrams, notes, rationale, summaries, and historical
descriptions are informative unless a requirement explicitly incorporates
them.

**Clause ID: `AAOS-RFC-0000-S03-C03`**
**Requirement: `AAOS-REQ-0000-005`**

A deviation from a `SHOULD` or `SHOULD NOT` obligation MUST identify the
affected requirement IDs, justification, risk, compensating behavior,
evidence, scope, and validity interval. Such a record is not itself a waiver,
risk acceptance, or expansion of Authority.

## 4. RFC identity — Normative

**Clause ID: `AAOS-RFC-0000-S04-C01`**
**Requirement: `AAOS-REQ-0000-001`**

Every AAOS RFC MUST have one stable RFC identifier. The RFC identifier is
distinct from the RFC version, repository path, issue, pull request, commit,
tree, rendered document digest, semantic-manifest digest, and release
identifier.

**Clause ID: `AAOS-RFC-0000-S04-C02`**
**Requirement: `AAOS-REQ-0000-002`**

Every material review disposition and lifecycle transition MUST bind an exact
RFC version and canonical semantic-manifest digest. When materialized in a
repository, the disposition MUST also bind repository, commit, and tree
identity.

**Clause ID: `AAOS-RFC-0000-S04-C03`**
**Requirements: `AAOS-REQ-0000-002`, `AAOS-REQ-0000-020`**

A mutable issue, branch, title, or file path is insufficient as the sole
identity of an RFC candidate.

## 5. Requirement governance — Normative

**Clause ID: `AAOS-RFC-0000-S05-C01`**
**Requirement: `AAOS-REQ-0000-006`**

Every normative obligation MUST have exactly one primary identifier in the
form `AAOS-REQ-<RFC>-<NUMBER>`.

**Clause ID: `AAOS-RFC-0000-S05-C02`**
**Requirement: `AAOS-REQ-0000-007`**

Specialized interface, conformance, schema, test, fixture, evidence,
transition, and record identifiers MAY map to a primary AAOS requirement, but
MUST NOT compete with it as the normative identity of the same obligation.

**Clause ID: `AAOS-RFC-0000-S05-C03`**
**Requirement: `AAOS-REQ-0000-008`**

A requirement identifier MUST NOT be reused for unrelated or materially
incompatible semantics. Editorial clarification MAY preserve the ID only when
normative meaning is unchanged. Breaking replacement requires an explicit
successor requirement or major RFC revision.

**Clause ID: `AAOS-RFC-0000-S05-C04`**
**Requirement: `AAOS-REQ-0000-009`**

Deprecated, superseded, withdrawn, and rejected requirement records MUST
remain historically resolvable, including their text, version, status, and
successor references.

**Clause ID: `AAOS-RFC-0000-S05-C05`**
**Requirement: `AAOS-REQ-0000-010`**

Every requirement MUST declare one or more of the verification classes
`machine_testable`, `evidence_reviewable`, `human_disposition_only`, and
`private_l0_dependent`. It MUST also declare required evidence, negative
behavior, unknown behavior, restrictive consequence, and public claim
boundary.

## 6. RFC namespaces — Normative

**Clause ID: `AAOS-RFC-0000-S06-C01`**
**Requirement: `AAOS-REQ-0000-011`**

The namespaces `rfc_class`, `rfc_review_state`, `rfc_status`, archival
designation, implementation state, conformance outcome, and deployment state
MUST remain independent and MUST NOT be collapsed.

### 6.1 RFC classes — Normative

**Clause ID: `AAOS-RFC-0000-S06-C02`**
**Requirement: `AAOS-REQ-0000-012`**

The initial RFC classes are `process`, `standards_track`, `profile`,
`informational`, and `experimental`. An RFC class MUST NOT imply lifecycle
status, implementation maturity, deployment suitability, or conformance.

### 6.2 Review states — Normative

**Clause ID: `AAOS-RFC-0000-S06-C03`**
**Requirement: `AAOS-REQ-0000-013`**

The initial review states are `not_started`, `under_review`,
`changes_requested`, `ready_for_disposition`,
`blocked_pending_private_l0_input`, and
`blocked_by_contract_contradiction`. A review state MUST NOT create normative
force.

### 6.3 Lifecycle statuses — Normative

**Clause ID: `AAOS-RFC-0000-S06-C04`**
**Requirement: `AAOS-REQ-0000-014`**

The initial lifecycle statuses are `draft`, `candidate`, `provisional`,
`accepted`, `stable`, `deprecated`, `superseded`, `withdrawn`, and
`rejected`. Each status MUST define its predecessors, successors, transition
authority, required evidence, and migration consequences.

**Clause ID: `AAOS-RFC-0000-S06-C05`**
**Requirement: `AAOS-REQ-0000-016`**

`historical` MUST be a derived archival designation, not a competing RFC class
or lifecycle status.

## 7. Lifecycle transitions — Normative

**Clause ID: `AAOS-RFC-0000-S07-C01`**
**Requirement: `AAOS-REQ-0000-015`**

No RFC lifecycle transition MAY be inferred from GitHub state, publication,
CI, evaluator output, runtime behavior, implementation availability,
conformance-test results, or elapsed time. Every material transition MUST use
an exact-candidate-bound human disposition.

**Clause ID: `AAOS-RFC-0000-S07-C02`**
**Requirements: `AAOS-REQ-0000-014`, `AAOS-REQ-0000-015`,
`AAOS-REQ-0000-036`**

The base transition path is `draft → candidate → provisional → accepted →
stable → deprecated → superseded`. A pre-acceptance candidate MAY be
rejected. An eligible RFC version MAY be withdrawn only from source states
enumerated by the C4 transition registry. Rejection and withdrawal MUST
preserve historical identity.

**Clause ID: `AAOS-RFC-0000-S07-C03`**
**Requirements: `AAOS-REQ-0000-014`, `AAOS-REQ-0000-015`**

Standards Track and Profile RFCs MUST pass through `provisional` before
`accepted`. Process RFCs MAY use `candidate → accepted` only when they do not
directly change runtime, Authority, evidence, object, state, interface, or
conformance semantics. Informational RFCs MAY use the bounded direct path
defined by the C4 transition registry.

**Clause ID: `AAOS-RFC-0000-S07-C04`**
**Requirements: `AAOS-REQ-0000-014`, `AAOS-REQ-0000-015`**

`stable` MUST NOT be inferred from elapsed time. Stability evidence MUST be
class-specific.

**Clause ID: `AAOS-RFC-0000-S07-C05`**
**Requirements: `AAOS-REQ-0000-014`, `AAOS-REQ-0000-036`,
`AAOS-REQ-0000-037`**

`superseded` MUST require an exact accepted or stable successor. A newer
draft, title, or version number is insufficient.

**Clause ID: `AAOS-RFC-0000-S07-C06`**
**Requirements: `AAOS-REQ-0000-014`, `AAOS-REQ-0000-037`**

Direct `stable → withdrawn` is reserved for critical unsafe semantics,
Authority widening or fail-open behavior, legal or institutional
impossibility of maintenance, or absence of a safe deprecation path.
Otherwise the normal path MUST be `stable → deprecated → superseded or
withdrawn`.

## 8. Review roles and dispositions — Normative

**Clause ID: `AAOS-RFC-0000-S08-C01`**
**Requirement: `AAOS-REQ-0000-017`**

RFC review MUST distinguish proposer, editor, semantic owner, governance
reviewer, and final disposer. Standards Track and Profile RFCs additionally
require a conformance reviewer. Security- or authority-sensitive RFCs
additionally require a security or authority-boundary reviewer.

**Clause ID: `AAOS-RFC-0000-S08-C02`**
**Requirement: `AAOS-REQ-0000-018`**

A proposer or editor MUST NOT assign `accepted` or `stable` status solely by
virtue of proposing or editing the RFC. Any permitted role combination MUST
be explicitly authorized, and reduced independence MUST be recorded.

**Clause ID: `AAOS-RFC-0000-S08-C03`**
**Requirement: `AAOS-REQ-0000-019`**

Every material disposition MUST bind the RFC ID and exact version, candidate
digest, requirement-manifest digest, review evidence, disposition and
constraints, unresolved inputs, final-disposer Authority reference, effective
time and clock context, and migration, supersession, rejection, or withdrawal
effects.

**Clause ID: `AAOS-RFC-0000-S08-C04`**
**Requirement: `AAOS-REQ-0000-020`**

Review of mutable planning text MAY assign only planning review state. It MUST
NOT assign `candidate`, `provisional`, `accepted`, or `stable` lifecycle
status before an immutable candidate exists.

## 9. Change classification and versioning — Normative

**Clause ID: `AAOS-RFC-0000-S09-C01`**
**Requirement: `AAOS-REQ-0000-021`**

Every RFC revision MUST declare both a semantic change class and a resulting
RFC version.

**Clause ID: `AAOS-RFC-0000-S09-C02`**
**Requirement: `AAOS-REQ-0000-021`**

The initial semantic change classes are `editorial`, `clarifying`,
`additive_compatible`, `restrictive`, and `breaking`.

**Clause ID: `AAOS-RFC-0000-S09-C03`**
**Requirement: `AAOS-REQ-0000-022`**

AAOS RFC versions SHOULD use `MAJOR.MINOR.PATCH`. The default resulting
version increments are PATCH for editorial or non-conformance-impact
clarification, MINOR for additive compatible change, MAJOR by default for
restrictive change, and MAJOR or a successor RFC for breaking change.

**Clause ID: `AAOS-RFC-0000-S09-C04`**
**Requirement: `AAOS-REQ-0000-023`**

A change MUST NOT be classified as `clarifying` when it changes required
evidence, permitted Authority, object or state meaning, failure behavior,
interface obligations, conformance outcomes, or public claim boundaries.

**Clause ID: `AAOS-RFC-0000-S09-C05`**
**Requirements: `AAOS-REQ-0000-022`, `AAOS-REQ-0000-023`**

A restrictive revision MAY use MINOR only through an accepted Compatibility
Preservation Profile proving that canonical identity, Authority meaning,
conformance boundaries, downgrade safety, migration, and claim scoping remain
bounded. Otherwise it MUST use MAJOR.

## 10. Emergency Constraint Notices — Normative

**Clause ID: `AAOS-RFC-0000-S10-C01`**
**Requirement: `AAOS-REQ-0000-024`**

RFC-0000 defines the Emergency Constraint Notice, or ECN, as a temporary
restrictive instrument that MUST NOT silently rewrite an accepted RFC.

**Clause ID: `AAOS-RFC-0000-S10-C02`**
**Requirement: `AAOS-REQ-0000-024`**

An ECN MUST bind the affected RFC versions, profiles, and requirement IDs;
the identified threat or governance defect; the restrictive rule; issuing
Authority reference; effective time; maximum validity; affected claims and
admissions; evidence; withdrawal conditions; and required follow-up RFC
action.

**Clause ID: `AAOS-RFC-0000-S10-C03`**
**Requirements: `AAOS-REQ-0000-024`, `AAOS-REQ-0000-025`**

An ECN has a maximum initial validity of 30 calendar days, at most one renewal
of 30 additional calendar days, and an absolute RFC-process validity limit of
60 calendar days without a normal RFC revision.

**Clause ID: `AAOS-RFC-0000-S10-C04`**
**Requirement: `AAOS-REQ-0000-025`**

An ECN MAY restrict or suspend use. It MUST NOT expand Authority, waive
mandatory evidence, convert `not_evaluable` into a permissive result, or
become permanent without a normal RFC revision and disposition.

**Clause ID: `AAOS-RFC-0000-S10-C05`**
**Requirements: `AAOS-REQ-0000-025`, `AAOS-REQ-0000-034`**

Expiry of an ECN MUST NOT automatically authorize previously restricted
unsafe behavior. Continued restriction requires another valid governance
basis.

## 11. Public semantic precedence — Normative

**Clause ID: `AAOS-RFC-0000-S11-C01`**
**Requirement: `AAOS-REQ-0000-026`**

Public AAOS semantic precedence is accepted RFC, accepted RFC-owned
requirement registry, accepted ADR interpretation where delegated by the RFC,
implementation contract, schema/API/event representation, tests/fixtures/
validators, runtime behavior, informational documentation, and historical
milestone text, in that order. Lower-level artifacts MUST NOT redefine
accepted public Semantic Core semantics.

**Clause ID: `AAOS-RFC-0000-S11-C02`**
**Requirement: `AAOS-REQ-0000-032`**

Passing a schema validator, evaluator, fixture, test suite, or CI workflow
MUST NOT by itself establish live control enforcement, institutional
adoption, deployment authorization, certification, or risk acceptance.

## 12. Private institutional applicability — Normative

**Clause ID: `AAOS-RFC-0000-S12-C01`**
**Requirement: `AAOS-REQ-0000-027`**

Private L0 doctrine MAY determine whether, where, under whose Authority, and
with which restrictions an institution adopts a public RFC or profile. It
MUST NOT silently rewrite the public RFC's canonical semantics.

**Clause ID: `AAOS-RFC-0000-S12-C02`**
**Requirement: `AAOS-REQ-0000-028`**

A material contradiction between public RFC semantics and required private
doctrine MUST produce a bounded profile restriction, non-adoption,
`blocked_pending_private_l0_input`, or
`blocked_by_contract_contradiction`. It MUST NOT use last-write-wins,
newest-document-wins, or silent override.

**Clause ID: `AAOS-RFC-0000-S12-C03`**
**Requirement: `AAOS-REQ-0000-029`**

Acceptance of a public RFC MUST NOT be represented as disclosure,
implementation evidence, or independent verification of private sovereign
controls.

**Clause ID: `AAOS-RFC-0000-S12-C04`**
**Requirements: `AAOS-REQ-0000-027`, `AAOS-REQ-0000-028`,
`AAOS-REQ-0000-029`**

A public Private Dependency Review Receipt MAY state a bounded review result,
restrictions, validity, revocation, abstract Authority reference, and
evidence-location reference. It MUST NOT disclose restricted private doctrine
or imply verification beyond the stated scope.

## 13. Artifact boundaries and traceability — Normative

**Clause ID: `AAOS-RFC-0000-S13-C01`**
**Requirement: `AAOS-REQ-0000-030`**

Issue, ADR, RFC, requirement registry, schema, interface contract, test,
fixture, validator, runtime control, conformance claim, deployment admission,
and institutional decision MUST remain distinct artifact types.

**Clause ID: `AAOS-RFC-0000-S13-C02`**
**Requirement: `AAOS-REQ-0000-031`**

Every schema, interface contract, event contract, validator, test, fixture,
runtime control, and conformance claim that implements or evaluates an RFC
obligation MUST trace to stable RFC and primary requirement IDs.

**Clause ID: `AAOS-RFC-0000-S13-C03`**
**Requirements: `AAOS-REQ-0000-031`, `AAOS-REQ-0000-032`**

Traceability establishes derivation and a declared relationship. It does not
by itself prove semantic correctness or conformance.

**Clause ID: `AAOS-RFC-0000-S13-C04`**
**Requirement: `AAOS-REQ-0000-035`**

A new Semantic Core RFC or primary issue MUST be justified by an unowned
irreducible concept, canonical contradiction, necessary breaking change,
authority-boundary or fail-closed defect, or independently reviewable profile
after base stabilization. External novelty alone MUST NOT create a normative
RFC.

## 14. History, migration, and claim effects — Normative

**Clause ID: `AAOS-RFC-0000-S14-C01`**
**Requirement: `AAOS-REQ-0000-036`**

Accepted RFC versions, requirements, dispositions, and conformance claims
MUST remain historically preserved after deprecation, supersession,
withdrawal, or rejection.

**Clause ID: `AAOS-RFC-0000-S14-C02`**
**Requirement: `AAOS-REQ-0000-037`**

Deprecation, supersession, restrictive revision, breaking revision, ECN
issuance, and requirement withdrawal MUST declare their effects on
implementations, profiles, schemas, tests, deployment admissions, conformance
claims, and public claim language.

**Clause ID: `AAOS-RFC-0000-S14-C03`**
**Requirement: `AAOS-REQ-0000-038`**

A conformance claim against one RFC version MUST NOT be represented as
conformance to a successor RFC unless the successor requirement set has been
evaluated against the exact implementation and environment.

**Clause ID: `AAOS-RFC-0000-S14-C04`**
**Requirement: `AAOS-REQ-0000-039`**

A migration window MAY preserve a historical claim only within its original
RFC version, evaluated subject, environment, restrictions, and validity
interval. It MUST NOT imply successor-version conformance.

## 15. Candidate serialization and disposition subject — Normative

**Clause ID: `AAOS-RFC-0000-S15-C01`**
**Requirements: `AAOS-REQ-0000-002`, `AAOS-REQ-0000-019`,
`AAOS-REQ-0000-020`, `AAOS-REQ-0000-031`**

The normative semantic manifest MUST be serialized using RFC 8785 JSON
Canonicalization Scheme and initially digested with SHA-256.

**Clause ID: `AAOS-RFC-0000-S15-C02`**
**Requirements: `AAOS-REQ-0000-001`, `AAOS-REQ-0000-002`,
`AAOS-REQ-0000-019`**

The semantic-manifest digest, requirement-registry digest, human-readable
Markdown byte digest, rendered-output digest, component-manifest digest,
candidate-package digest, Git blob SHA, Git commit SHA, and Git tree SHA are
distinct identities.

**Clause ID: `AAOS-RFC-0000-S15-C03`**
**Requirements: `AAOS-REQ-0000-002`, `AAOS-REQ-0000-003`,
`AAOS-REQ-0000-019`, `AAOS-REQ-0000-031`**

The semantic manifest is the primary disposition subject for normative
meaning. The human-readable RFC MUST remain traceably consistent with it.

## 16. Security and governance considerations — Normative

**Clause ID: `AAOS-RFC-0000-S16-C01`**
**Requirements: `AAOS-REQ-0000-008`, `AAOS-REQ-0000-011`,
`AAOS-REQ-0000-015`, `AAOS-REQ-0000-018`, `AAOS-REQ-0000-023`,
`AAOS-REQ-0000-025`, `AAOS-REQ-0000-026`, `AAOS-REQ-0000-029`,
`AAOS-REQ-0000-032`, `AAOS-REQ-0000-034`, `AAOS-REQ-0000-036`**

AAOS RFC governance MUST prevent shadow normative sources, silent Authority
promotion, ambiguous status transitions, requirement-ID reuse, semantic
downgrade through compatibility modes, tests or runtime behavior redefining
the specification, public claims overstating private assurance, emergency
restrictions becoming permanent without review, history rewriting, and
unknown mandatory semantics becoming permissive.

## 17. Non-goals — Informative

This RFC does not:

- define AAOS architecture layers or governance verbs;
- define canonical governance objects or relations;
- define state namespaces or transition semantics outside the RFC process;
- define Decision Proof or evidence sufficiency;
- define runtime interfaces or conformance profiles;
- assign private institutional roles, trusted roots, risk thresholds, or
  emergency procedures;
- authorize implementation, deployment, certification, risk acceptance,
  restore, cutover, or sealing.

Those concerns are owned by downstream RFCs or private institutional doctrine.

## 18. Normative traceability index — Informative

The index below summarizes mappings already attached to individual normative
clauses. It creates no additional obligation.

| Section | Clause IDs | Primary requirement mappings |
|---|---|---|
| Scope | S02-C01–C03 | 012, 030–034 |
| Normative language | S03-C01–C03 | 003–005 |
| RFC identity | S04-C01–C03 | 001–002, 020 |
| Requirement governance | S05-C01–C05 | 006–010 |
| RFC namespaces | S06-C01–C05 | 011–016 |
| Lifecycle transitions | S07-C01–C06 | 014–015, 036–037 |
| Review roles | S08-C01–C04 | 017–020 |
| Change and versioning | S09-C01–C05 | 021–023 |
| ECN | S10-C01–C05 | 024–025, 034 |
| Public precedence | S11-C01–C02 | 026, 032 |
| Private applicability | S12-C01–C04 | 027–029 |
| Artifact boundaries | S13-C01–C04 | 030–032, 035 |
| History and migration | S14-C01–C04 | 036–039 |
| Candidate binding | S15-C01–C03 | 001–003, 019–020, 031 |
| Security and governance | S16-C01 | 008, 011, 015, 018, 023, 025–026, 029, 032, 034, 036 |

All 39 primary requirements are represented. Clause IDs are stable
traceability identifiers; they are not new primary requirement IDs.

## 19. Change history — Informative

```text
0.1.0-candidate.1
- Materialized the Phase 3 human-readable draft.
- Added stable clause IDs required by R0-CORR-02.
- Preserved rfc_status = not_assigned.
- Bound the Phase 5 semantic-manifest digest.
```
