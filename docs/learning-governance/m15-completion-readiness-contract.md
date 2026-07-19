# M15 Track E3 Completion-Readiness Contract

## Status and purpose

This contract defines the deterministic M15 Track E3 completion-readiness
package and the future-only v0.14.0 README path. It binds maintained Track
A–E2 evidence for final human review. It does not approve M15 completion.

Tracker #231 remains open. M15 remains active and incomplete. Track E4 and a
separate final human completion review remain required.

v0.14.0 remains unpublished; no tag or GitHub Release is created or authorized.

Decision Proof sealing remains AAOS-owned.

Learning Proof sealing remains AAOS-owned.

AAOS remains the decision sovereignty layer.

## Source and historical bindings

The E3 source-main base is commit
`f6d074fca2fedecbf654697719179440bc0680d3` with tree
`f13913426545b77616128223cd195487a415ffde`.

The maintained prior-track inventory is derived from the first-parent material
diff of each merged implementation pull request:

| Track | Issue | PR | Candidate | Merge | Material paths |
| --- | ---: | ---: | --- | --- | ---: |
| A | #232 | #233 | `603a26890ceee940b0a3c9009e06d994f9f2f342` | `6e0fa4e8fdf4a672581cd897d52743d0462f0d4b` | 7 |
| B | #234 | #237 | `270a5bbb536c6bf0726e95455d4bb61ac86d693e` | `8e475518f2da6232ae9a6264d8e9c9f1e5fc514a` | 13 |
| C | #238 | #239 | `5f98f6c86e6b61d50b1c8183aca0736a3419c533` | `2d8bab3a84675543c34231a9e04521379febdac1` | 18 |
| D | #240 | #241 | `3bec19e42693b757b9abbb077146ca9860d48c1e` | `e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f` | 29 |
| E1 | #242 | #243 | `55629976db7f7b8dc9e2153eaf67f054bd9ee708` | `27c92e290cf6ad60bada49b63fe1888511930980` | 39 |
| E2 | #248 | #249 | `efc31e7d24c26d2cea2cb536a4cae257aababb5f` | `f6d074fca2fedecbf654697719179440bc0680d3` | 50 |

The total is 156 maintained material paths: 67 for Tracks A–D, 39 for E1,
and 50 for E2. Every inventory entry binds its source issue, implementation
PR, candidate, merge, path, artifact type, Git blob, file mode, canonical text
SHA-256, covering test, lifecycle state, evidence reference, and authority
boundary. A runtime result cannot create or repair these observations.

## Exact E2 continuity

The E2 continuity record binds exactly:

- source-main base: `27c92e290cf6ad60bada49b63fe1888511930980`;
- candidate commit: `efc31e7d24c26d2cea2cb536a4cae257aababb5f`;
- candidate tree: `f13913426545b77616128223cd195487a415ffde`;
- merge commit: `f6d074fca2fedecbf654697719179440bc0680d3`;
- merge tree: `f13913426545b77616128223cd195487a415ffde`;
- merge parents, in Git order:
  `27c92e290cf6ad60bada49b63fe1888511930980`, then
  `efc31e7d24c26d2cea2cb536a4cae257aababb5f`;
- candidate-to-merge changed paths: zero;
- additional merge-result differences: zero;
- relation: `exact_tree_match`.

Read-only, test-only Git inspection proves both object types are commits, both
recorded trees match the actual Git objects, both recorded parents match Git
order, the base and candidate are parents, and the candidate-to-merge file diff
is empty. The runtime evaluator does not inspect Git.

The active external E2 observation is PR #249 comment #5015690597. The active
verification receipt is PR #249 comment #5015694989 with canonical SHA-256
`511226a39144791ec47043203878bd22d14ec546e71702c267b66cc47da6af2f`.
PR #249 comment #5015466792 is classified only as
`superseded-historical-evidence`; it is never accepted as the active receipt.

## Authorized Phase-Aware Compatibility Repair

Purpose: phase-aware historical README regression repair.

Authorization basis: human-approved bounded scope exception for Issue #250.

The exception authorizes only these existing paths and purposes:

- `runtime/m14_final_completion_evaluator.py` —
  `phase-aware-next-phase-validation`;
- `tests/test_m14_final_completion_evaluator.py` —
  `explicit-historical-mutation-fixtures`;
- `tests/test_m15_lineage_rollback_portability_evaluator.py` —
  `section-aware-future-version-assertions`;
- `tests/test_m15_operational_readiness_evaluator.py` —
  `historical-source-baseline-artifact-observation`.

It does not authorize:

- release-state modification;
- M14 reopening;
- authority-doctrine change;
- test deletion;
- unconditional skip;
- arbitrary historical evaluator cleanup;
- external adapter scope.

These repair paths are E3-authorized compatibility changes, not additional
Track A–E2 material artifacts, and do not increment or replace the 156-item
prior-material inventory. The historical Track C inventory entry for
`tests/test_m15_lineage_rollback_portability_evaluator.py` remains bound to its
original Track C merge blob and digest; the current compatibility change is a
separate E3 scope record.

The E1 historical binding for
`tests/test_m15_lineage_rollback_portability_evaluator.py` is the immutable
source-baseline commit `e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f` and
canonical SHA-256
`5268f73a441898467e9b8f9471cfc4b9bd4fa27b7b67444fbf852d697d90f4c9`.
The authorized current E3 repair of that path has canonical SHA-256
`0dee39fe81189fd558f136732579995245828bc6b14c9791b67c9bb6e8a39f5c`
and purpose `section-aware-future-version-assertions`.

The E1 historical digest is not superseded, and the E3 current digest does
not replace it. They represent different observation times and evidence
roles. The E3 repair is not the original Track C implementation artifact, and
E1 source-snapshot validation is not current-main validation. All four repair
scope records remain separate from the 156-item prior-material inventory.

## Maintained documents

The strict Draft 2020-12 schema recognizes ten closed document kinds:

1. completion-readiness manifest;
2. Track A–E2 evidence inventory;
3. E2 continuity record;
4. E2 external-evidence record;
5. M15 acceptance-coverage matrix;
6. blocker and future-prerequisite register;
7. README future-path observation;
8. commit-external pull-request observation;
9. commit-external verification receipt;
10. standalone synthetic scenario.

Every object has a complete required-field set and rejects additional
properties. Git object identifiers are lower-case 40-hex values, SHA-256
digests are lower-case 64-hex values, timestamps are RFC 3339 UTC, and states
use closed vocabularies. Negative outer state never makes a nested affirmative
completion, release, sealing, execution, or authority claim admissible.

## Acceptance-criteria coverage

The maintained matrix has one ordered row for each of tracker #231's 16
acceptance criteria. Each row contains a source-track binding, an evidence
reference, an artifact or contract reference, a test reference, a coverage
state, notes, and the exact non-authoritative boundary.

`covered`, `partial`, `missing`, and `blocked` are the only coverage states.
Only `covered` with every required reference can contribute to readiness.
Partial, missing, blocked, omitted, duplicated, or reference-free criteria do
not produce `ready_for_final_m15_completion_review`. Evaluator success alone is
not acceptance-criterion coverage.

## Completion blockers and future prerequisites

The blocker register contains exactly these required blocker identifiers:

- `missing-track-a-evidence`;
- `missing-track-b-evidence`;
- `missing-track-c-evidence`;
- `missing-track-d-evidence`;
- `missing-track-e1-evidence`;
- `missing-track-e2-evidence`;
- `e2-candidate-merge-mismatch`;
- `missing-e2-pr-observation`;
- `missing-active-e2-receipt`;
- `superseded-e2-receipt-used`;
- `e2-receipt-digest-mismatch`;
- `incomplete-acceptance-criteria-coverage`;
- `hidden-completion-blocker`;
- `invalid-future-readme-path`;
- `incomplete-verification-coverage`;
- `authority-boundary-violation`.

A resolved blocker requires a non-empty evidence reference and explanation.
Open or blocked entries remain blocking. A blocker cannot be omitted or be
resolved merely because a future prerequisite has not yet occurred.

The following future prerequisites remain explicitly open during E3:

- `track-e4-not-completed`;
- `final-m15-completion-not-approved`;
- `tracker-231-open`;
- `readme-final-completion-not-authorized`;
- `v0.14.0-tag-not-authorized`;
- `github-release-not-authorized`;
- `post-merge-final-review-not-completed`.

These open prerequisites do not prevent an evidence-only readiness result.
They do prevent that result from being treated as completion, tracker closure,
release publication, tag authorization, or GitHub Release authorization.

## README boundary

Track E3 changes only the future-facing `## Next Phase` section. The Releases,
Bootstrap Status, Current Status, historical M1–M14 completion statements, and
v0.13.0 latest-release statement remain unchanged.

The caller-supplied README observation binds canonical SHA-256 values for the
base and candidate README plus the Releases, Current Status, and Next Phase
sections. It requires Releases and Current Status to be identical and Next
Phase to change to the bounded future wording. It rejects claims that M15 is
complete, E4 is complete, v0.14.0 is released, a tag is authorized, or a GitHub
Release exists. Digest calculation and README inspection are test-only; the
runtime accepts only the resulting inert mapping.

## Runtime contract

The runtime API accepts exactly nine caller-supplied inert mappings:

```python
evaluate_completion_readiness(
    manifest,
    track_evidence_inventory,
    e2_continuity_record,
    e2_external_evidence,
    acceptance_coverage_matrix,
    boundary_register,
    readme_observation,
    pull_request_observation,
    external_verification_receipt,
)
```

It performs mapping and sequence shape checks, primitive comparisons, closed
vocabulary validation, deterministic aggregation, and creation of a new result
mapping. It does not mutate callers.

It does not read files or repository state, inspect Git or GitHub, use a
network, execute a subprocess or command, calculate a repository or receipt
digest, import fixture content dynamically, or mutate external state.

The only outcomes are:

1. `blocked` when any blocking contradiction exists;
2. `not_ready` when there is no blocker but readiness evidence is incomplete;
3. `ready_for_final_m15_completion_review` otherwise.

The result always reports that it is caller-data-only and that no file, Git,
GitHub, network, digest, verification-command, or external-state action was
performed. It also reports M15 as active and incomplete, tracker #231 as open,
Track E4 as not implemented, v0.14.0 as unpublished, tag state as
not-authorized, GitHub Release state as not-created, and both proof-sealing
states as false.

## External observation and verification receipt

The final E3 pull-request candidate observation and verification receipt are
commit-external PR comments. They bind the repository, issue #250, actual PR,
source-main base, frozen candidate head, candidate tree, timestamps, evidence
references, and the exact non-authoritative boundary.

The receipt contains all 17 maintained verification commands, including
explicit M14 final-completion and M14 completion-readiness regression groups.
Each command
binds declared and actual argv, scope, candidate head, launcher substitution,
Python implementation and version, observed/minimum counts, pass/failure/error/
skip arithmetic, exit code, execution timestamp, transcript SHA-256, and an
external evidence reference. Acceptable execution requires zero failures,
errors, skips, and exit code, with observed tests at or above the maintained
minimum. Command presence and exit code zero are not proof of sufficient
execution.

The evaluator validates supplied observation and receipt mappings; it does not
fetch, execute, or publish them. Verification is neither completion authority
nor release authority.

## Synthetic and implementation boundary

Public scenarios are standalone, synthetic, inert, offline, deterministic, and
contain no secret, credential, personal data, private prompt, production
identifier, executable payload, argv, command, or script payload.

Track E3 is additive except for the bounded README Next Phase change. It does
not implement persistence, training, fine-tuning, generated-tool activation,
capability registration, live deletion, live rollback, or production system
connections. It adds no MiniMind, AURION, Clinical, Field, Device, PQC,
Advisor, or external-adapter implementation.

Completion readiness may inspect, compare, validate, preserve, and report
evidence. It cannot approve M15 completion, close #231, authorize final README
state, authorize or publish v0.14.0, create or authorize a tag or GitHub
Release, approve deployment, accept risk, execute rollback/deletion/fail-closed,
grant a waiver, close an audit, transfer authority, seal Decision Proof, seal
Learning Proof, or make a final governance judgment.
