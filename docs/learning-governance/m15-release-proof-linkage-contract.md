# M15 Track E2 Release-Proof Linkage Contract

Status: deterministic, offline, evidence-only Track E2 contract for issue #248.

Parent tracker: #231 remains Open. M15 remains active and incomplete. Track E3 and Track E4 are not implemented by this contract. The future release candidate is identified as `urn:aaos:m15:release-candidate:v0.14.0:unapproved` with state `identified-not-authorized`; v0.14.0 remains unpublished.

## Purpose and authority boundary

Track E2 answers one bounded question: was the exact Track E1 pull-request candidate covered by the external E1 verification receipt preserved in the E1 merge-result commit?

The package can return `release_proof_linked` only when the supplied historical identities, complete candidate changed-path manifest, corresponding merge-result path manifest, candidate-to-merge continuity record, E1 external-receipt linkage, E2 blocker register, future prerequisite register, and external E2 execution receipt are mutually consistent. This outcome means only that the E1 candidate-to-merge evidence chain is complete and verified.

Release-proof linkage is evidence only. It is not:

- M15 completion approval;
- tracker #231 closure;
- README completion authorization;
- release-candidate approval;
- tag authorization or creation;
- GitHub Release authorization, creation, publication, or Latest status;
- Decision Proof sealing;
- Learning Proof sealing;
- deployment authorization, risk acceptance, audit closure, or waiver.

Decision Proof sealing and Learning Proof sealing remain AAOS-owned. AAOS remains the decision sovereignty layer. Neither provenance, operational readiness, a merge commit, nor successful verification is human approval or release authority.

## Scope

The maintained E2 implementation is additive:

- this contract;
- `schemas/m15-release-proof-linkage.schema.json`;
- the E2 manifest and five maintained evidence records under `examples/public-integration-pack-pilot/`;
- at least 30 standalone synthetic E2 fixtures in that directory;
- `runtime/m15_release_proof_linkage_evaluator.py`;
- `tests/test_m15_release_proof_linkage_evaluator.py`.

The implementation does not modify or supersede the E1 contract, schema, manifest, scenarios, evaluator, or tests. It does not implement Track E3 or Track E4. It does not change README milestone or release state and does not create a tag or GitHub Release.

## Fixed historical bindings

The records bind historical Git objects, not current branch names or mutable prose:

| Binding | Exact value |
| --- | --- |
| Track A-D source baseline commit | `e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f` |
| Source baseline tree | `a0277b8cb697c9e311118f7de67f7f6bf3534fcb` |
| E1 candidate commit | `55629976db7f7b8dc9e2153eaf67f054bd9ee708` |
| E1 candidate tree | `f4552f630e2dab5b9d34240efa8825f187b4abf1` |
| E1 merge-result commit | `27c92e290cf6ad60bada49b63fe1888511930980` |
| E1 merge-result tree | `f4552f630e2dab5b9d34240efa8825f187b4abf1` |
| E1 merge parents, in Git order | source baseline, then E1 candidate |
| E1 pull request | #243 |
| E1 external receipt comment | #5015070053 |
| E1 receipt schema | `m15-operational-readiness-verification-receipt/v1` |
| E1 receipt command count | 13 |
| Canonical E1 receipt JSON SHA-256 | `86e33a67a532b11502b376f196a755b62a72a487e5f754cc2ac3752082acbb5b` |

The actual E2 starting maintained-main commit is the E1 merge-result commit above. It is recorded as the source main/base for E2, rather than inferred later from a potentially advanced `main` reference. An E2 pull-request candidate head is deliberately absent from committed evidence because committing that value would change the candidate that it purported to identify.

## Independent Git observation and derivation

Test-only observation helpers may read local Git objects without mutation. They independently inspect the source baseline commit and tree, E1 candidate commit and tree, E1 merge commit and tree, merge parent order, tree entries, and history-derived diff. They do not trust PR prose, branch names, commit messages, merge state, or workflow state as continuity evidence.

The candidate change set is derived from the source baseline to E1 candidate Git history with rename and copy detection enabled. The observed complete set contains 39 paths. All 39 historical changes are additions with file mode `100644`; the zero counts for modification, rename, and deletion are recorded rather than omitted. The runtime comparison semantics nevertheless cover additions, modifications, renames, and deletions so those change types fail closed when represented inconsistently.

For each candidate-changed path the maintained manifest records:

- exact repository-relative path and stable path identifier;
- previous path where applicable;
- closed change type;
- baseline blob SHA where applicable;
- candidate blob SHA;
- candidate canonical SHA-256;
- candidate file mode;
- artifact role;
- required status;
- evidence reference.

For each corresponding merge-result path the maintained manifest records:

- the same path identifier and exact path;
- source change type;
- merge blob SHA;
- merge canonical SHA-256;
- merge file mode;
- presence state;
- continuity status;
- continuity evidence reference.

Canonical text SHA-256 is calculated outside the runtime evaluator by strictly decoding UTF-8, converting checkout CRLF sequences to Git-style LF, rejecting any remaining lone carriage return, encoding UTF-8, and applying SHA-256. No other content transformation is permitted. Git blob identity and canonical-content identity are separate checks.

Complete coverage requires an entry for every derived candidate path and exactly one corresponding merge entry. Additions, modifications, and renames require the expected path to be present after merge with matching blob, canonical digest, and mode. Deletions require the path and all post-merge identities to be absent. Previous-path and baseline-blob semantics must match the declared change type. Any differently named path is substitution, not continuity.

## Candidate-to-merge relation

The only allowed relation values are:

- `exact_tree_match`;
- `candidate_change_set_preserved`;
- `drift_detected`;
- `unverified`.

`exact_tree_match` is used only when the candidate tree SHA and merge-result tree SHA are identical and the complete changed-path evidence supports preservation.

`candidate_change_set_preserved` is used only when every candidate change is preserved and every additional merge-result difference is independently explained and evidence-bound. An explanation must bind the advanced base, show the source baseline ancestry, and reference inert observation evidence. A PR number, branch, merge state, commit message, or successful workflow cannot supply that explanation.

`drift_detected` applies when observed continuity fails, including missing paths, blob mismatch, canonical digest mismatch, file-mode mismatch, or substitution. `unverified` applies when the necessary evidence is absent or incomplete. Neither relation may be silently promoted to linkage.

For the fixed E1 history, the independently observed E1 candidate and merge trees are both `f4552f630e2dab5b9d34240efa8825f187b4abf1`. All 39 candidate paths are preserved and no additional merge difference exists. The maintained relation is therefore `exact_tree_match`.

## E1 external-receipt linkage

The E1 receipt linkage record binds exactly:

- PR #243;
- comment #5015070053;
- receipt schema `m15-operational-readiness-verification-receipt/v1`;
- source baseline `e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f`;
- E1 candidate `55629976db7f7b8dc9e2153eaf67f054bd9ee708`;
- 13 verification commands;
- canonical receipt JSON SHA-256 `86e33a67a532b11502b376f196a755b62a72a487e5f754cc2ac3752082acbb5b`;
- an explicit non-authoritative boundary.

The runtime receives this record as inert caller data. It does not fetch the PR, comment, or GitHub and does not calculate the receipt digest. Receipt presence cannot be inferred from a URL, comment identifier, PR merge, workflow result, or caller assertion with a different digest. The receipt is not merge approval.

## E2 linkage blockers and future release prerequisites

The two structures are deliberately separate.

The complete E2 linkage-blocker register is:

- `missing-continuity-evidence`;
- `candidate-merge-mismatch`;
- `missing-receipt-binding`;
- `incomplete-path-coverage`;
- `unexplained-digest-or-mode-drift`.

Every blocker must remain visible. The maintained evidence marks each `resolved` only because a non-empty evidence reference and explanation bind the observed continuity result. An omitted or unresolved E2 blocker blocks linkage.

The complete future-release-prerequisite register is:

- `track-e3-not-completed`;
- `track-e4-not-completed`;
- `final-m15-completion-not-approved`;
- `tracker-231-open`;
- `readme-completion-not-authorized`;
- `v0.14.0-tag-not-authorized`;
- `github-release-not-authorized`.

Every future prerequisite remains `open` and visible. These facts intentionally do not become E2 continuity failures. This separation allows E2 to truthfully produce `release_proof_linked` while M15 remains incomplete and no release is authorized.

## Outcome semantics

The only E2 outcomes are:

- `release_proof_linked`: every required continuity and E1 receipt binding is complete, consistent, preserved, and externally verified for the exact E2 candidate;
- `not_ready`: no blocking contradiction is present, but required verification or continuity evidence is not yet complete;
- `blocked`: malformed, absent, inconsistent, drifted, substituted, or authority-promoting evidence is present.

Future release prerequisites remaining open do not prevent the evidence-only `release_proof_linked` outcome. They do prevent the outcome from being interpreted as completion or release readiness.

The evaluator fails closed for missing or inconsistent historical identity, missing candidate or merge tree, incomplete path coverage, missing required merge paths, unexplained blob/digest/mode drift, receipt mismatch, identity conflation, omitted linkage blockers, and any completion, tracker closure, README, tag, release, Latest, sealing, waiver, risk, audit, deployment, or transferred-authority claim.

## Caller-data-only runtime boundary

`runtime/m15_release_proof_linkage_evaluator.py` accepts only caller-supplied inert mappings. It may compare strings, booleans, integers, lists, and mappings and return a newly allocated result mapping.

The runtime evaluator must not:

- import `pathlib` or read repository files;
- inspect Git or invoke Git commands;
- access GitHub or any network;
- import or use subprocess or shell execution;
- calculate repository or receipt digests;
- create branches, commits, tags, or releases;
- mutate files, caller mappings, Git, GitHub, or external state.

The result explicitly reports these operations as not performed. Test-only helpers may observe local Git history and calculate inert metadata, tree and parent SHAs, path changes, blob SHAs, canonical SHA-256 values, and modes. Those helpers must not mutate Git or GitHub.

## Standalone synthetic scenarios

The package supplies 36 standalone synthetic JSON files. Each contains a complete synthetic evidence state, expected outcome, expected relation, and non-authoritative boundary. The first 30 cover every scenario required by #248: exact match, explained base advancement, all specified identity/path/digest/mode/receipt failures, authority-promotion failures, omitted blocker, unverified linkage, missing future identifier, and forbidden Decision Proof or Learning Proof sealing.

The additional scenarios prove fail-closed `unverified` handling; preserved modification, rename, and deletion semantics; and the absent or inconsistent external E2 receipt gates. The files contain synthetic data only and no credentials, personal data, private prompts, production identifiers, or executable content.

## External E2 verification-receipt contract

The final E2 pull-request candidate requires an external machine-readable receipt in the E2 PR conversation. It is external precisely because committing the exact candidate head would alter that head.

The receipt binds:

- repository `aa-os/aaos-public`;
- issue #248 and the actual E2 pull-request number;
- source main/base `27c92e290cf6ad60bada49b63fe1888511930980`;
- the exact final E2 candidate head;
- all 14 required command identifiers;
- declared logical argv and actual argv;
- execution scope and the candidate head for every command;
- declared and actual Python launchers, declared substitution state, implementation, and version;
- exact tests, passes, failures, errors, skips, and exit code;
- UTC execution timestamp;
- SHA-256 of each complete combined transcript;
- an external evidence reference and non-authoritative boundary.

Every command must have zero failures, zero errors, zero skips, and exit code zero. Count arithmetic must reconcile. The actual argv may replace only the declared `python` launcher, and any replacement must be explicit. The runtime consumes this receipt as caller data and never executes the declared commands.

If a commit is pushed after the receipt is produced, the receipt no longer binds the current candidate. All 14 commands must be rerun and the PR receipt replaced with one bound to the new head.

## Required verification groups

The manifest declares, without executing, these external validation groups:

1. E2 targeted tests;
2. E1 targeted tests;
3. Track A tests;
4. Track B tests;
5. Track C tests;
6. Track D tests;
7. M14 public-output tests;
8. M14 provenance tests;
9. M14 skill-admission tests;
10. external-evidence-admission tests;
11. M14 cross-control authority tests;
12. Decision Proof ownership tests;
13. release-state and M15-status tests;
14. the full maintained repository suite.

Execution records are external observations and do not alter repository state or grant completion, release, sealing, or governance authority.
