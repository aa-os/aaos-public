# M15 Track E4 final-completion contract

## Status and purpose

This contract implements the source contract in Issue #252 for the final,
human-reviewed M15 repository completion transition and v0.14.0 release-state
preparation.

Track E4 remains a proposed transition until the exact frozen pull-request
candidate has all required external evidence, an explicit commit-external
human approval record, and an approved merge commit.

The evaluator, schema, fixtures, tests, observations, receipts, approval
templates, README candidate state, and release-preparation records are
non-authoritative evidence. They do not approve or execute completion,
tracker closure, tag creation, or GitHub Release publication.

Source and parent bindings:

- repository: `aa-os/aaos-public`
- E4 source issue: `#252`
- parent M15 tracker: `#231`
- E3 source issue / implementation PR: `#250` / `#251`
- E4 source-main base: `52ec76c17cd21ec519dfec45ced4ad720b82d80e`
- E4 source-main base tree: `97b239cbd175aac01b05a1fba2394b72c47a5360`

Before the approved E4 merge, Issue #252 and tracker #231 remain Open, M15
remains active and incomplete, v0.14.0 remains unpublished, and neither a
v0.14.0 tag nor GitHub Release is created or authorized.

## Governing transition states

### Pre-merge evidence state

The E4 pull request is only a proposed repository transition. Draft, Ready,
mergeable, approved-review, evaluator-success, and test-success states are
not repository completion or release publication.

### Human-reviewed repository transition

Only an explicitly authorized human may approve the exact frozen E4
candidate. The approved candidate must be merged with a merge commit. That
merge may establish the repository M15 completion state and close #252 and
#231 through the reviewed pull-request linkage.

The runtime evaluator cannot create, approve, or merge the transition.

### Manual v0.14.0 publication

After the E4 merge, a human-controlled operation may create tag `v0.14.0` at
the exact E4 merge commit and create the corresponding GitHub Release. The
tag target is never the candidate head. Publication remains separate from
repository completion and requires a post-release review.

No evaluator, fixture, receipt, observation, or committed record may create
or publish the tag or GitHub Release.

## Exact E3 continuity binding

Track E4 binds the merged E3 result exactly:

- E3 source-main base: `f6d074fca2fedecbf654697719179440bc0680d3`
- E3 candidate: `907d2361233c7b0405a41271d7b02fa6c1a0c62d`
- E3 candidate tree: `97b239cbd175aac01b05a1fba2394b72c47a5360`
- E3 merge: `52ec76c17cd21ec519dfec45ced4ad720b82d80e`
- E3 merge tree: `97b239cbd175aac01b05a1fba2394b72c47a5360`
- E3 merge parents, in Git order:
  1. `f6d074fca2fedecbf654697719179440bc0680d3`
  2. `907d2361233c7b0405a41271d7b02fa6c1a0c62d`
- relation: `exact_tree_match`
- active PR observation: PR #251 comment #5017872695
- active verification receipt: PR #251 comment #5017894934
- active receipt canonical SHA-256:
  `660ffddc0644bbb6e11689ceaf77b5c47b4061241a04cba233f2607287e30cb4`
- superseded observation: PR #251 comment #5016298363
- superseded receipt: PR #251 comment #5016356607

Superseded E3 evidence is historical only and cannot satisfy an active E3
evidence binding.

## Required maintained package

The completed E4 package must contain:

1. This governance contract.
2. A strict Draft 2020-12 schema.
3. A machine-readable final-completion manifest.
4. Exact E3 continuity and external-evidence records.
5. An immutable Track A-E3 evidence inventory.
6. Exact coverage for all 16 #231 acceptance criteria.
7. Completion-blocker and transition-prerequisite registers.
8. A README final-transition observation.
9. Release-target, release-notes, and publication-checklist records.
10. Pull-request observation, verification-receipt, and human-approval
    contracts.
11. A deterministic caller-data-only runtime evaluator.
12. Standalone synthetic positive and adversarial fixtures.
13. Focused tests and the full maintained regression suite.

Historical evidence is bound to its immutable historical Git snapshot. E4
must not rebaseline E1, E2, or E3 digests to current candidate content or
pin a mutable branch ref to an earlier source base.

### Exact phase-addressed inventory

The immutable caller-supplied inventory contains exactly 209 rows. The first
156 rows preserve the Track A-E2 bindings established by E3, with counts of
7, 13, 18, 29, 39, and 50 respectively. The 53 E3 rows are derived from the
actual PR #251 Git objects and remain separately classified as:

- 4 core completion-readiness artifacts;
- 37 standalone synthetic scenarios;
- 7 maintained evidence records;
- 1 README Next Phase transition;
- 4 authorized historical compatibility repairs.

Every row binds the track, source issue, implementation PR, candidate and
merge commits, repository path, artifact type, Git blob SHA, file mode,
canonical SHA-256, covering test, lifecycle state, evidence reference,
historical authority boundary, and phase-aware evidence role. Aggregate
counts or an inventory digest cannot substitute for exact row comparison.
The four E3 compatibility-repair rows remain E3-authorized historical repair
evidence; they are not reclassified as original Track A-E2 artifacts.

### Authorized Phase-Aware Compatibility Repair

Issue #252 authorizes exactly five current E4 compatibility-repair paths:

1. `runtime/m14_final_completion_evaluator.py` —
   `phase-aware-later-milestone-readme-validation`;
2. `tests/test_m14_final_completion_evaluator.py` —
   `explicit-historical-m14-final-mutation-validation`;
3. `tests/test_m14_completion_readiness_evaluator.py` —
   `immutable-m14-readiness-snapshot-validation`;
4. `tests/test_m15_completion_readiness_evaluator.py` —
   `immutable-e3-completion-readiness-snapshot-validation`;
5. `tests/test_m15_lineage_rollback_portability_evaluator.py` —
   `section-aware-e4-release-state-candidate-validation`.

Every row is a human-authorized bounded exception and is excluded from the
209-row Track A-E3 prior-material inventory. A sixth historical path is not
authorized and must block evaluation. This exception does not authorize a
release-state mutation outside the reviewed README transition, reopen M14,
change authority doctrine, delete or skip tests, perform arbitrary historical
cleanup, add external-adapter scope, approve the E4 merge, complete M15, close
#231 or #252, create a tag, or create or publish a GitHub Release.

The machine-readable register keeps three evidence roles separately
addressable: the immutable historical milestone state, any applicable prior
authorized compatibility state, and the current E4 compatibility candidate.
Each state binds its own commit or candidate role, Git blob identity, and
canonical-text SHA-256. A current E4 digest cannot overwrite or supersede a
historical pin. In particular, the Track C historical artifact, its E3 repair,
and its E4 repair are distinct evidence; the E3 completion-readiness artifact
and its E4 repair are also distinct evidence.

### Exact acceptance and verification registries

The acceptance matrix preserves exact criterion text and bindings for all 16
criteria in tracker #231. Non-empty arbitrary references are not coverage.
Partial, missing, blocked, omitted, or substituted coverage cannot produce a
ready outcome.

The final verification receipt binds exactly 18 maintained commands. Their
logical argv, execution scope, and minimum test counts must match the manifest
registry exactly. The E4 focused minimum is 183 and the candidate full-suite
minimum is 2275; inherited minima may only increase. Actual argv may differ
from logical argv only at argv[0], where the declared checkout-local
`.verification-python/python.exe` launcher is used. Every execution must have
zero failures, errors, skips, and exit code, and its observed test count must
meet the maintained minimum.

## README candidate boundary

The reviewed E4 candidate may update only the M15 final repository state:

- add the v0.14.0 repository release-state entry without claiming the tag or
  GitHub Release already exists;
- extend Current Baseline with the M15 Learning Sovereignty and
  Evidence-Bound Capability Memory pattern;
- update Current Status from M1-M14 complete to M1-M15 complete and add the
  exact M15 completion evidence chain;
- replace Next Phase with the separate manual publication path.

Unrelated README sections must remain unchanged. The README transition is
candidate state reviewed for a future merge, not a claim about maintained
main before that merge.

## Runtime contract

The E4 runtime accepts only eleven caller-supplied inert mappings:

1. final completion manifest;
2. Track A-E3 evidence inventory;
3. E3 continuity record;
4. E3 external-evidence record;
5. acceptance-coverage matrix;
6. transition register;
7. README transition observation;
8. release-preparation record;
9. pull-request observation;
10. external verification receipt;
11. human approval observation.

It may validate shapes, closed vocabularies, exact values, cross-bindings,
counts, and precedence, and it may return a newly allocated result mapping.

It must not read files, inspect Git, access GitHub or a network, execute a
subprocess or command, calculate repository or receipt digests, mutate caller
data, mutate files, create a branch or commit, merge a pull request, close an
Issue, close #231, create a tag, publish a GitHub Release, or mutate any
external state.

Allowed outcomes are exactly:

- `ready_for_human_m15_completion_transition`
- `not_ready`
- `blocked`

Contradictions, binding substitutions, malformed evidence, and authority
promotion are `blocked`. Missing required evidence or exact human approval is
`not_ready`. The ready outcome remains evidence only and is not approval,
completion, merge authorization, tracker closure, tag authorization, release
publication, risk acceptance, audit closure, waiver, authority transfer,
Decision Proof sealing, or Learning Proof sealing.

## Human approval boundary

The final human approval record must be authored outside the candidate commit
after final candidate freeze, active PR observation publication, completion of
all maintained verification groups, and active verification receipt
publication.

It must bind the exact repository, #252, actual E4 pull request, source-main
base, candidate head and tree, active observation, active receipt and receipt
digest, reviewed README and completion-state digests, intended merge method,
permitted issue closures, timestamp, approver identity, and authority scope.

Codex, CI, an evaluator, a bot, or a generated artifact cannot be the human
approver. Any candidate-head change after approval invalidates the observation,
receipt, and approval.

The approval may authorize only the exact candidate merge and repository M15
completion transition. It does not authorize the v0.14.0 tag or GitHub Release,
risk acceptance, audit closure, waiver, authority transfer, Decision Proof
sealing, or Learning Proof sealing.

## Authority and implementation boundary

Track E4 remains deterministic, contract-first, offline and caller-data-only
at runtime, synthetic-fixture based, non-production, and non-authoritative.

It must not use production credentials or private data, train or fine-tune a
model, implement persistent organizational memory, activate generated tools,
register executable capabilities, execute live deletion or rollback, connect
to production systems, add MiniMind, AURION, Clinical, Field, Device, PQC,
Advisor, or external-adapter implementation scope, or modify historical
milestone files without separate bounded human authorization.

Decision Proof sealing remains AAOS-owned.

Learning Proof sealing remains AAOS-owned.

AAOS remains the decision sovereignty layer.
