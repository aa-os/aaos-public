# v0.14.0 post-release governance review and M15 retrospective

Status: maintained Issue #254 evidence for human review

Repository: aa-os/aaos-public

Release: v0.14.0

Completion PR: #253

Authoritative merge: 01870f4b844c1cda2f157e7be7bdb66317fdc738

Observation time: 2026-07-20T12:21:22.682Z, with mutable GitHub API
response receipts refreshed and hashed at 2026-07-20T13:20:20.660Z.

## Outcome

The reviewed tag and published GitHub Release are correctly bound to the M15
completion merge. The clean-clone reproduction passed the full 2,275-test
tagged baseline. No release-blocking defect or corrective patch-release
candidate was observed.

One documentation-drift finding is corrected by this Draft PR. The remaining
findings are non-blocking governance, evaluator, operational-hardening,
future-milestone, or accepted-risk items.

Recommendation: M16 planning may begin only after this review receives a
separate explicit human authorization. Issue #254 completion does not itself
authorize M16 planning, and neither this report nor Issue #254 authorizes M16
implementation.

This report is evidence only. It does not approve a release, accept risk, move
or delete a tag, edit a GitHub Release, close an issue, grant runtime authority,
or transfer Decision Proof or Learning Proof sealing authority.

## Evidence planes

The review keeps four evidence planes distinct:

| Plane | Bound state | Limitation |
| --- | --- | --- |
| Immutable tagged source | v0.14.0 commit 01870f4b844c1cda2f157e7be7bdb66317fdc738 and tree 6bc77ea15c1b55b3b99a0705da40a4568849b47b | A point-in-time Git observation cannot prove the ref was never moved before observation. |
| Maintained main | refs/heads/main at the same merge at observation time | Main can advance after this report. |
| Live GitHub | Release 356696715, PR #253, Issues #231, #252, and #254 | GitHub state is mutable; raw response and body digests are observation receipts, not authority. |
| Clean clone | Detached v0.14.0 checkout with a clean tree before and after verification | Reproduction proves source availability and maintained-test behavior, not governance approval. |

## Tag and release binding

The remote tag reference and refs/heads/main both resolved to
01870f4b844c1cda2f157e7be7bdb66317fdc738.

The tag is lightweight: git cat-file -t v0.14.0 returned commit. Peeling
v0.14.0^{commit} returned the required merge, and v0.14.0^{tree} returned
6bc77ea15c1b55b3b99a0705da40a4568849b47b.

The published release observation was:

| Field | Observed value |
| --- | --- |
| Release URL | https://github.com/aa-os/aaos-public/releases/tag/v0.14.0 |
| Release ID | 356696715 |
| Tag | v0.14.0 |
| Target commitish | main |
| Title | v0.14.0 — M15 Learning Sovereignty and Evidence-Bound Capability Memory |
| Author | aa-os |
| Created | 2026-07-20T11:57:48Z |
| Published | 2026-07-20T12:08:53Z |
| Updated | 2026-07-20T12:08:53Z |
| Draft | false |
| Prerelease | false |
| Latest | true; the releases/latest endpoint returned Release 356696715 |
| GitHub API immutable field | false |

The release notes identify the M15 release, PR #253, the merge, the tag, and the
2,275-test baseline. They preserve Learning Sovereignty, Decision Proof
sovereignty, and non-authorizing evidence boundaries. No claim of release,
risk-acceptance, runtime, invocation, or sealing authority was observed.

Release-note evidence:

| Field | Value |
| --- | --- |
| UTF-8 byte count | 3,433 |
| Digest mode | UTF-8 API body without normalization |
| SHA-256 | 665bceb884b3e4915d618efd585374b2105bd20dfda97374944162fb00b5dab5 |
| Raw release API response bytes | 5,357 |
| Raw release API response SHA-256 | f139e8d7c15965d600c4ee39cf35cfb3d84df575e1841057618eeaf08020484c |

There were zero uploaded release assets. GitHub-generated source archives are
not treated as uploaded assets, so no asset content digest was required.

## Repository consistency

PR #253 is merged at the required merge commit. Issue #252 and parent tracker
#231 are closed as completed. Issue #254 remains open for this human review.

The tagged README already records the v0.14.0/M15 release entry and states that
M1 through M15 are complete. Its Next Phase section retained pre-publication
wording saying that the tag and GitHub Release were not claimed to exist. That
is classified as documentation drift.

This Draft PR corrects the maintained README. The review-candidate README:

- states that v0.14.0 is published as the Latest stable release;
- binds the tag to 01870f4b844c1cda2f157e7be7bdb66317fdc738;
- keeps Issue #254 evidence-only;
- states that Issue #254 does not automatically authorize M16 planning;
- states that M16 implementation remains out of scope;
- preserves Decision Proof, Learning Proof, and AAOS sovereignty boundaries.

The candidate README is bound by Git blob
c72ed99f6de5415a0295b0832e8e22a9698b567e and canonical-text SHA-256
24e56be918627ff86f2383ec6473bc5d6789dcfeb903debf034c98576438add9.
The stale-statement scan returned no match.

The immutable tag-tree release-reference inventory found 95 v0.14.0 matching
lines across 33 paths. Its canonical transcript SHA-256 is
b1f86e01cd397544777df95ef34c84e51eed893099771595560b768b1bd265ef.
A separate M15/version mismatch scan returned no matches. Historical
pre-publication contracts, fixtures, schemas, evaluator cases, and negative
tests remain historical phase evidence and were not rewritten as current
release state.

## Publication and approval evidence

The machine-readable record preserves API response digests for the release,
Latest endpoint, tag ref, assets, PR #253, Issues #231/#252/#254, and the three
external PR evidence comments. It also records exact comment URLs, actor,
created and updated timestamps, body byte counts, body digests, API-envelope
byte counts, and API-envelope digests.

The external sequence is strictly ordered:

1. PR observation comment 5021546499 at 2026-07-20T11:06:53Z.
2. Verification receipt comment 5021686076 at 2026-07-20T11:24:04Z.
3. Human approval comment 5021955084 at 2026-07-20T11:57:17Z.
4. Merge at 2026-07-20T11:57:48Z.
5. Release publication at 2026-07-20T12:08:53Z.

The approval body binds the candidate, verification receipt, and approved
action. Its embedded JSON still contains timestamp and approver placeholders;
the GitHub envelope provides the observed actor and time. This is a
governance-contract gap, not a release blocker. Future approval records should
standardize the binding between body, actor, time, update state, candidate,
tree, receipt, and action without replacing GitHub envelope evidence.

## Reproducibility

A fresh remote clone was created with local object reuse disabled. It checked
out v0.14.0 in detached-HEAD state. The detached HEAD, tag commit, tag tree,
non-shallow state, and clean worktree were verified independently.

The exact git clone --no-local command for the final reproduction clone
returned exit 0 directly; later inspections are not used as a substitute for
that command receipt.

The tagged tree has 501 ordinary Git blobs. It requires no submodule, Git LFS
object, sparse-checkout state, repository-local interpreter, or unrecorded
worktree content. It is independently inspectable from normal Git objects.

The exact maintained-test argv was:

python -X faulthandler -m unittest discover -s tests -t . -p test_*.py -q

Environment:

- PYTHONDONTWRITEBYTECODE=1
- AAOS_TEST_GIT_EXE=C:/Program Files/Git/cmd/git.exe
- CPython 3.14.6 outside the clean clone
- Git 2.55.0.windows.3

Exact stderr transcript:

    ----------------------------------------------------------------------
    Ran 2275 tests in 140.079s

    OK

The transcript contains CRLF line endings, is 106 UTF-8 bytes, and has SHA-256
2acc1d73a38d6362a8f84c490dcbb0cac240cf98e26037277f9d025b921175fd.
Stdout was empty. The worktree was empty under git status
--porcelain=v1 --untracked-files=all both before and after the run.

The machine-readable record contains all 36 normalized argv receipts, expected
exit codes, result kinds, derived summaries where applicable, and raw stdout or
stderr digests. The record itself is pinned by canonical JSON SHA-256
d5a38d89a159e66a4a2170c4194b1730947b3608e77d52b1b8308ff37b9815dd.

## Rollback and correction semantics

The publication policy for v0.14.0 is immutable:

- do not move the published tag;
- do not delete or recreate the published tag;
- rollback must not repoint v0.14.0;
- corrective work requires successor commits;
- use an explicit patch release when a release-level correction is appropriate;
- preserve the original release, PR, issue, receipt, and review evidence so the
  historical decision remains discoverable.

The current tag target is verified. Technical protected-tag or ruleset
enforcement was not evidenced, the tag is lightweight, and the release API
reports immutable=false. Therefore technical enforcement is an operational
hardening item. The inability of point-in-time observations to prove that a ref
was never previously moved is an accepted residual risk. Neither item changes
the rule that v0.14.0 must remain untouched.

## M15 governance retrospective

### Decision Proof

Decision Proof remains the governed decision record and remains distinct from
Learning Proof and capability admission. A future composition contract should
require evidence from the M13 approval gate across admission-to-use transitions
without turning that evidence into learning, invocation, or execution
authority.

### Learning Proof and Learning Sovereignty

The M15 contract preserves the distinction between readiness evidence,
authorization evidence, and AAOS-owned sovereignty. The evaluator accepts the
unknown local offset -00:00 and has no caller-supplied evaluation time for
current expiry. A successor change should add deterministic, bound temporal
semantics without consulting ambient time.

### Evidence-Bound Capability Memory

Capability Memory maintains evidence, lifecycle, dependency, rollback,
deletion, and portability separation. It does not grant runtime invocation or
execution authority. Before operational pack consumption, a future contract
should verify referenced bytes and define a canonical digest over the complete
pack rather than only compare declared internal digest strings.

### Human approval boundaries

The external evidence sequence binds observation, receipt, approval, merge, and
publication. The E4 evaluator validates timestamp shape and bindings but not
event chronology. A successor evaluator should validate monotonic event
ordering and bind an envelope-derived approval record.

### Runtime authority boundaries

The reviewed M15 evaluators remain deterministic, caller-data-only,
non-mutating, and non-authorizing. The Issue #254 evaluator additionally pins
the exact release-specific record with an in-memory canonical digest. It does
not fetch evidence or verify external artifact bytes.

### Release governance

Repository completion, human approval, merge, tag publication, release
publication, and post-release review remain separate transitions. The release
is reproducible and correctly bound. The maintained README drift is corrected
here. Technical tag protection and reusable cross-release evidence packaging
remain prospective work.

## Classified findings

Every finding has exactly one permitted classification.

| ID | Classification | Finding | Disposition |
| --- | --- | --- | --- |
| m15-prg-001 | documentation drift | Tagged README retained pre-publication wording. | Corrected in this Draft PR; historical E4 bytes remain unchanged. |
| m15-prg-002 | operational hardening | No protected-tag/ruleset receipt or technical release immutability was evidenced. | Add prospective protection and audit receipts; never change v0.14.0. |
| m15-prg-003 | accepted residual risk | Point-in-time evidence cannot prove the ref was never previously moved. | Bounded risk for human review; retain prospective audit evidence. |
| m15-prg-004 | governance-contract gap | Published approval JSON retains actor/time placeholders despite exact GitHub envelope evidence. | Standardize an envelope-bound approval record in a successor contract. |
| m15-prg-005 | evaluator or test gap | E4 validates timestamp form but not strict event chronology. | Add immutable ordering evidence and negative tests. |
| m15-prg-006 | evaluator or test gap | Learning Proof admits -00:00 and lacks supplied as-of expiry evaluation. | Add strict known-offset and deterministic expiry semantics. |
| m15-prg-007 | governance-contract gap | Approval-gate evidence is not mandatory across the complete admission-to-use transition. | Add a non-authorizing future composition contract. |
| m15-prg-008 | future milestone candidate | Generic release schemas do not retain this complete evidence package. | Consider a reusable versioned post-release evidence contract. |
| m15-prg-009 | no action required | Tag and peeled commit equal the required merge, not the PR head. | Preserve the binding. |
| m15-prg-010 | no action required | Release is published, non-draft, non-prerelease, Latest, M15-correct, and non-authorizing. | Preserve the observation receipts. |
| m15-prg-011 | no action required | PR #253 is merged; #252 and #231 are closed; #254 is open. | Keep #254 open for human review. |
| m15-prg-012 | no action required | Detached clean-clone reproduction passed 2,275 tests without hidden local state. | Retain the exact receipts. |
| m15-prg-013 | no action required | Learning and capability evidence remain non-authorizing. | Preserve the boundary. |
| m15-prg-014 | no action required | Maintained evaluators remain inert and caller-data-only. | Preserve the boundary. |
| m15-prg-015 | no action required | Correction semantics preserve v0.14.0 and require successor work. | Apply the policy to any correction. |
| m15-prg-016 | future milestone candidate | Pack evaluation does not hash referenced bytes or expose a canonical whole-pack digest. | Add external byte receipts and a canonical pack digest before operational consumption. |

Classification totals:

| Classification | Count |
| --- | ---: |
| release-blocking defect | 0 |
| corrective patch-release candidate | 0 |
| documentation drift | 1 |
| governance-contract gap | 2 |
| evaluator or test gap | 2 |
| operational hardening | 1 |
| future milestone candidate | 2 |
| accepted residual risk | 1 |
| no action required | 7 |

## Candidate verification

The immutable tag baseline is recorded above. The Draft candidate passed:

- Issue #254 schema/evaluator hostile-input module: Ran 14 tests in 0.043s — OK.
- Full maintained candidate suite, including all historical phase-compatibility
  coverage: Ran 2289 tests in 136.308s — OK.
- JSON parsing for the schema and record: exit 0.
- Python compilation for the new evaluator and test module: exit 0.
- git diff --check: exit 0.

The full candidate command was:

python -X faulthandler -m unittest discover -s tests -t . -p test_*.py -q

It ran with PYTHONDONTWRITEBYTECODE=1 and AAOS_TEST_GIT_EXE bound to the
resolved Git executable. The 14-test increase over the immutable 2,275-test
tag baseline is the new post-release governance review suite.

## Maintained deliverables and exact changed paths

This review intentionally changes exactly these nine repository paths:

1. README.md
2. docs/governance/m15-post-release-governance-review.md
3. examples/public-integration-pack-pilot/m15-post-release-governance-review-record.json
4. runtime/m15_post_release_governance_review_evaluator.py
5. schemas/m15-post-release-governance-review.schema.json
6. tests/test_m14_final_completion_evaluator.py
7. tests/test_m15_final_completion_evaluator.py
8. tests/test_m15_lineage_rollback_portability_evaluator.py
9. tests/test_m15_post_release_governance_review_evaluator.py

No release or tag was edited. No issue was closed. No PR was merged. No M16
implementation was performed.
