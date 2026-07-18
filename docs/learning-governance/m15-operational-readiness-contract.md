# M15 Track E1 Operational Readiness Contract

## Status and scope

This contract implements only M15 Track E1 from issue #242. It supports three strict document kinds: maintained manifest `m15-operational-readiness/v1`, independently supplied repository observation evidence `m15-operational-readiness-observation/v1`, and standalone synthetic scenario `m15-operational-readiness-scenario/v1`.

E1 is deterministic, offline, read-only, contract-first, simulation-only, additive, and backward-compatible. It inventories, integrity-binds, observes, validates, and reports the maintained Track A-D implementation state. It does not implement Track E2, E3, or E4.

Tracker #231 remains Open. M15 remains active and incomplete. `v0.14.0` remains unpublished. E1 does not modify README completion or release declarations, create or authorize a tag, publish or authorize `v0.14.0`, create or authorize a GitHub Release, close or authorize closure of #231, or approve M15 completion.

## Governing separation

```text
artifact present
!= artifact valid

artifact valid
!= operational readiness

operational readiness
!= completion approval

completion readiness
!= M15 completion

test suite passing
!= release authorization

release preparation
!= tag creation

release proof linkage
!= GitHub Release publication
```

The exact E1 boundary statement is:

> ready_for_completion_review is evidence for a later human completion review only; it is not M15 completion approval, tracker #231 closure, README completion or release authorization, tag authorization, release authorization, or GitHub Release publication authorization.

## Maintained-main and merged-track bindings

The reviewed maintained branch is `main` at commit `e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f`. That commit is the merge commit for PR #241 and includes the earlier Track A–C merge commits.

| Track | Source issue | Implementation PR | PR head SHA | Merge SHA | Schema version | Material artifacts |
| --- | --- | --- | --- | --- | --- | ---: |
| A | #232 | #233 | `603a26890ceee940b0a3c9009e06d994f9f2f342` | `6e0fa4e8fdf4a672581cd897d52743d0462f0d4b` | `m15-learning-proof/v1` | 7 |
| B | #234 | #237 | `270a5bbb536c6bf0726e95455d4bb61ac86d693e` | `8e475518f2da6232ae9a6264d8e9c9f1e5fc514a` | `m15-capability-memory-pack/v1` | 13 |
| C | #238 | #239 | `5f98f6c86e6b61d50b1c8183aca0736a3419c533` | `2d8bab3a84675543c34231a9e04521379febdac1` | `m15-lineage-rollback-portability/v1` | 18 |
| D | #240 | #241 | `3bec19e42693b757b9abbb077146ca9860d48c1e` | `e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f` | `m15-cross-control-regression/v1` | 29 |

These are reviewed static repository bindings. The E1 evaluator does not contact GitHub, inspect a Git checkout, infer live PR state, or claim that a static binding proves current external state.

## Material artifact inventory

The machine-readable `artifact_integrity_inventory` contains exactly the 67 material paths introduced by the first-parent diffs of merged PRs #233, #237, #239, and #241:

- 4 contracts;
- 4 schemas;
- 50 standalone scenario fixtures;
- 1 Track D cross-control matrix;
- 4 evaluators; and
- 4 focused test modules.

The per-track totals are Track A 7, Track B 13, Track C 18, and Track D 29. Every entry binds the exact artifact identifier, track, source issue, implementation PR, artifact type, repository-relative path, maintained canonical digest, covering test module, lifecycle status, evidence reference, authority boundary, notes, and nullable deferred reason. Every entry also states that the E1 evaluator must not execute it.

The closed artifact-status vocabulary is `present`, `missing`, `digest_mismatch`, `unverified`, `superseded`, `deferred`, and `not_applicable`. All 67 artifacts are required. The maintained record declares each as `present`, but the evaluator does not trust that declaration: it compares every artifact identifier and path with the reviewed inventory and every observed digest with the reviewed canonical digest.

- A required `missing`, `digest_mismatch`, or `not_applicable` status is blocking.
- A required `unverified` status is not ready.
- A required `superseded` or `deferred` status is not ready pending an explicit maintained re-baseline.
- `deferred` without a non-empty deferred reason is blocked because the lifecycle evidence is internally incomplete.
- An observed missing file, unsafe path, or digest mismatch remains blocking regardless of the declared status.
- `present` requires the exact observed canonical digest and a null deferred reason.

Artifact lifecycle state is evidence only. It does not authorize completion, tracker closure, README changes, execution, tag creation, or release publication.

The Track D matrix remains material evidence in its own right. Its five independently maintained control bindings and fifteen control rows are not flattened into a new E1 authority surface. Track D pass, reject, or quarantine results must not be translated into completion authority.

## Maintained-control dependency inventory

`maintained_control_dependency_inventory` records five Track D source controls separately from the 67 Track A-D material artifacts. Its seventeen dependency paths are not added to the material-artifact count or type totals.

The five records bind the maintained controls from PRs #204, #206, #208, #209, and #210. Each record carries the exact source-control identifier, source PR, source schema or contract version, `path-binding:maintained-main` integrity reference, dependent Track A-D or cross-track bindings derived from the Track D control rows, per-path canonical-text SHA-256 objects, required boundary statements, covering test references, evidence reference, and non-authoritative status. The two source controls without native version fields retain the exact `unversioned-contract/.../path-bound-maintained-main` labels; E1 must not invent versions for them.

The evaluator compares the dependency inventory with an independently reviewed five-control baseline and with the Track D matrix. Missing, extra, substituted, or drifted control identifiers, source PRs, dependent Tracks, path sets, digests, versions, boundary statements, or covering tests are blocking. A dependency binding is evidence that an independently maintained control remains bound; it is not control admission, execution authority, completion approval, or release authority.

## Canonical SHA-256 convention

E1 reuses `runtime.repository_artifact_digest.sha256_repository_file` with `mode="text"` for every inventoried file. Repository text is decoded strictly as UTF-8. Only checkout CRLF is converted to Git-style LF. A lone carriage return is rejected. Terminal-newline presence, spaces, tabs, a UTF-8 BOM, Unicode normalization form, and all other bytes remain significant.

Paths must use exact POSIX repository-relative spelling. Empty, dot, dot-dot, backslash, drive, alternate-stream, trailing-dot, trailing-space, case-aliased, symlink, junction, escaping, missing, and non-regular-file paths fail closed.

The E1 inventory is new maintained-main repository-file evidence. It does not overwrite, substitute for, reinterpret, normalize, or claim authority from any historical digest evidence or any Track A-D record-internal digest field.

## Repository observation evidence

The strict `m15-operational-readiness-observation/v1` document is a third document kind, separate from both the maintained manifest and synthetic scenarios. It binds the same maintained repository, branch, and exact maintained-main SHA as the manifest. It contains exactly 67 artifact observations and exactly 17 maintained-control dependency-path observations.

Each artifact observation binds the reviewed artifact identifier and path, one closed lifecycle status, an observed canonical digest or null where no digest could be established, an inert evidence reference, the fixed authority boundary, notes, and a nullable deferred reason. Each dependency observation binds its maintained-control identifier, source-control identifier, path, status, observed canonical digest or null, evidence reference, boundary, and notes. Identifiers and paths must match the maintained manifest exactly; an observation cannot substitute a differently named artifact or control path.

Observation evidence is supplied to the evaluator and is not generated by it. The evaluator does not execute a source evaluator or verification command to create favorable observations. Observation evidence records bounded repository state only; it is not completion approval, tracker #231 closure, README authorization, tag authorization, release authorization, execution authority, or governance authority.

## Verification-command manifest

The machine-readable `verification_command_manifest` contains one required declarative command for each of these thirteen groups:

1. E1 targeted tests;
2. Track A tests;
3. Track B tests;
4. Track C tests;
5. Track D tests;
6. M14 public-output tests;
7. M14 provenance tests;
8. M14 skill-admission tests;
9. external-evidence-admission tests;
10. M14 cross-control authority tests;
11. Decision Proof ownership tests;
12. release-state and M15-status tests; and
13. the full maintained repository suite.

The command manifest sets `PYTHONDONTWRITEBYTECODE=1`, requires exit code zero, and records commands as argv arrays. Its truth fields are exact: `execution_results_recorded: true`, `commands_executed_by_evaluator: false`, `results_supplied_as_external_verification_evidence: true`, and `verification_results_are_completion_approval: false`. Each command also retains `executed_by_evaluator: false`.

`verification_result_manifest` supplies exactly one externally produced result record for each of the thirteen command identifiers. Each record binds a unique verification identifier, the command identifier, the external evidence source, exact maintained-main SHA, reviewed expected test count, observed test count, passes, failures, errors, skips, `exit_code`, `result`, evidence reference, `executed_by_evaluator: false`, and `verification_results_are_completion_approval: false`. The only result values are `pass` and `fail`.

The evaluator checks result records against independently reviewed command identifiers and exact expected counts. `passes + failures + errors + skips` must equal the observed test count. Expected and observed counts must match. `pass` is coherent only with exit code zero and zero failures and errors; `fail` is required otherwise. A failure, error, nonzero exit code, count mismatch, arithmetic inconsistency, command or verification-identifier substitution, evidence-binding inconsistency, or missing or mismatched maintained-main SHA is blocking. A structurally assessable result array missing a required command result is not ready; a missing or malformed result manifest is blocked. Any unexpected skip is not ready. Result evidence remains external: the E1 evaluator records and validates it but never executes its command.

Exact counts, failures, errors, and skips remain verification evidence. Neither command presence nor a passing result is completion or release authorization.

## Deterministic outcomes

The evaluator emits exactly one of these outcome values:

- `ready_for_completion_review`;
- `not_ready`; or
- `blocked`.

Outcome precedence is deterministic:

1. any blocking finding produces `blocked`;
2. otherwise, any readiness finding produces `not_ready`;
3. otherwise, the result is `ready_for_completion_review`.

Blocking findings include an unassessable or malformed manifest or observation document; maintained-main or Track A-D binding drift; an incomplete, substituted, unsafe, unreadable, missing, non-regular, non-UTF-8, lone-CR, or digest-drifted required artifact; required `not_applicable` status; deferred status without a reason; a missing or drifted Track D matrix or maintained-control dependency; a verification failure, error, nonzero exit, count mismatch, arithmetic inconsistency, malformed result, or result-binding inconsistency; an execution claim; an authority or release-boundary violation; or a known repository-local completion blocker.

`not_ready` is reserved for a structurally assessable package whose deterministic test-coverage mapping, required command coverage, or required verification-result coverage is incomplete; whose otherwise coherent result evidence includes an unexpected skip; or whose required artifact remains `unverified`, `superseded`, or validly deferred. A self-declared expected outcome never controls evaluator classification.

Findings are sorted and deduplicated. Findings identify reviewed field or path names, not arbitrary hostile values. The evaluator does not mutate caller inputs.

## Standalone synthetic scenarios

The checked-in scenario records are complete, inert JSON documents covering:

- the valid maintained-main path;
- maintained-main and merged-track binding drift;
- missing inventory coverage, canonical digest failure, and internal substitution;
- missing Track D matrix binding;
- incomplete test and command coverage;
- a false command-execution claim;
- completion approval, tracker closure, M15 completion, README authorization, tag, and release/GitHub Release escalation attempts;
- a known repository-local blocker; and
- an unsupported scenario schema version;
- a failed E1 targeted test;
- a verification test error;
- an unexpected verification skip;
- a missing required verification result;
- an observed test-count mismatch;
- a verification result without the maintained-main SHA;
- a required unverified artifact;
- a deferred artifact without a reason; and
- Track D external-control dependency drift.

The failed-test, test-error, count-mismatch, missing-main-SHA, deferred-without-reason, and maintained-control-drift scenarios are `blocked`. The unexpected-skip, missing-result, and required-unverified-artifact scenarios are `not_ready`. Blocking findings always take precedence over readiness findings.

Fixtures contain no live credentials, personal data, production account identifiers, provider operations, executable content, or external state transitions. In-memory adversarial mutations may supplement these files but do not replace them.

Every supported scenario carries this exact closed boundary statement; alternate free text is invalid:

> This standalone scenario is synthetic, inert, offline, and non-authoritative. ready_for_completion_review is evidence for a later human completion review only; it is not M15 completion approval, tracker #231 closure, README completion or release authorization, tag authorization, release authorization, or GitHub Release publication authorization.

## Preserved Track A–D boundaries

E1 binds the following source boundaries without replacing or weakening them:

- Track A: `This Learning Proof is evidence only; it grants no persistence, training, skill, tool, execution, rollback, deletion, sealing, or governance authority.`
- Track B: `This Capability Memory Pack is evidence only; runtime eligibility means eligibility for independent policy review, not installation, registration, deployment, execution, risk acceptance, Learning Proof sealing, or Decision Proof sealing. Capability Pack sealing is undefined and out of scope for M15 Track B. A capability pack must not claim sealed status or sealing authority.`
- Track C: `This Track C record is evidence only; it authorizes and executes no lifecycle action, rollback, deletion, provider disconnection, replacement-model use, installation, deployment, production workflow, risk acceptance, audit closure, waiver, authority transfer, Learning Proof sealing, or Decision Proof sealing.`
- Track D: `Track D evidence grants no authority; Learning Proof and Decision Proof sealing remain AAOS-owned; AAOS remains the decision sovereignty layer.`

Learning readiness is not learning authorization. Authorization evidence is not execution authority. Capability Pack sealing remains undefined and out of scope for Track B. Rollback readiness is not rollback authorization or execution. Deletion evidence is not physical deletion or provider erasure. Portability evidence is not provider disconnection, replacement-model authorization, or production execution. Non-authoritative records do not aggregate into authority. Decision Proof linkage is not verification or sealing.

## Execution safety

The evaluator performs no network access, subprocess execution, shell execution, dynamic import, package installation, source-evaluator invocation, model invocation, provider access, MCP or skill registration, credential access, fixture import, file mutation, rollback, deletion, tag creation, release publication, GitHub mutation, or external state transition.

Operational readiness is evidence for a later human completion review. Human review remains required.
