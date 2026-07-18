# M15 Track E1 Operational Readiness Contract

## Status and scope

This contract implements only M15 Track E1 from issue #242. The supported maintained-manifest schema version is `m15-operational-readiness/v1`, and the supported standalone synthetic-scenario version is `m15-operational-readiness-scenario/v1`.

E1 is deterministic, offline, read-only, contract-first, simulation-only, additive, and backward-compatible. It inventories, integrity-binds, validates, and reports the maintained Track A–D implementation state. It does not implement Track E2, E3, or E4.

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

The per-track totals are Track A 7, Track B 13, Track C 18, and Track D 29. Every entry binds the exact track, source issue, implementation PR, artifact type, repository-relative path, maintained canonical digest, and covering test module. Every entry also states that the E1 evaluator must not execute it.

The Track D matrix remains material evidence in its own right. Its five independently maintained control bindings and fifteen control rows are not flattened into a new E1 authority surface. Track D pass, reject, or quarantine results must not be translated into completion authority.

## Canonical SHA-256 convention

E1 reuses `runtime.repository_artifact_digest.sha256_repository_file` with `mode="text"` for every inventoried file. Repository text is decoded strictly as UTF-8. Only checkout CRLF is converted to Git-style LF. A lone carriage return is rejected. Terminal-newline presence, spaces, tabs, a UTF-8 BOM, Unicode normalization form, and all other bytes remain significant.

Paths must use exact POSIX repository-relative spelling. Empty, dot, dot-dot, backslash, drive, alternate-stream, trailing-dot, trailing-space, case-aliased, symlink, junction, escaping, missing, and non-regular-file paths fail closed.

The E1 inventory is new maintained-main repository-file evidence. It does not overwrite, substitute for, reinterpret, normalize, or claim authority from any historical digest evidence or any Track A–C record-internal digest field.

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

The manifest sets `PYTHONDONTWRITEBYTECODE=1`, requires exit code zero, and records commands as argv arrays. It explicitly states that the E1 evaluator does not execute commands and that the manifest does not record execution results. Exact run counts, failures, errors, and skips are external verification evidence reported with the PR; neither command presence nor a passing suite is completion or release authorization.

## Deterministic outcomes

The evaluator emits exactly one of these outcome values:

- `ready_for_completion_review`;
- `not_ready`; or
- `blocked`.

Outcome precedence is deterministic:

1. any blocking finding produces `blocked`;
2. otherwise, any readiness finding produces `not_ready`;
3. otherwise, the result is `ready_for_completion_review`.

Blocking findings include an unassessable or malformed manifest; maintained-main or Track A–D binding drift; an incomplete, substituted, unsafe, unreadable, missing, non-regular, non-UTF-8, lone-CR, or digest-drifted artifact; a missing or drifted Track D matrix; an execution claim; an authority or release-boundary violation; or a known repository-local completion blocker.

`not_ready` is reserved for a structurally assessable package whose deterministic test-coverage mapping or required verification-command coverage is incomplete. A self-declared expected outcome never controls evaluator classification.

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
- an unsupported scenario schema version.

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
