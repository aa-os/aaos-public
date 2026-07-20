"""Caller-data-only evaluator for the v0.14.0 post-release review.

The evaluator validates one inert mapping supplied by its caller. It does not
read repository files, inspect Git or GitHub, calculate or verify external
artifact digests, run commands, or mutate external state. It does calculate an
in-memory canonical SHA-256 over the supplied mapping to pin the
release-specific record. That digest calculation does not verify external
bytes and does not create governance authority. A complete result is evidence
for human review only; it does not authorize M16 planning or implementation.
"""

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any


SCHEMA_VERSION = "m15-post-release-governance-review/v1"
RESULT_SCHEMA_VERSION = "m15-post-release-governance-review-result/v1"

REPOSITORY = "aa-os/aaos-public"
ISSUE_NUMBER = 254
COMPLETION_PULL_REQUEST = 253
COMPLETION_CANDIDATE_HEAD_SHA = "b18c77f7745842aa849b53487be96c4eb5e531ca"
MERGE_COMMIT_SHA = "01870f4b844c1cda2f157e7be7bdb66317fdc738"
MERGE_TREE_SHA = "6bc77ea15c1b55b3b99a0705da40a4568849b47b"
RELEASE_TAG = "v0.14.0"
RELEASE_ID = 356696715
RELEASE_URL = "https://github.com/aa-os/aaos-public/releases/tag/v0.14.0"
RELEASE_TITLE = (
    "v0.14.0 — M15 Learning Sovereignty and Evidence-Bound Capability Memory"
)
RELEASE_AUTHOR = "aa-os"
RELEASE_CREATED_AT = "2026-07-20T11:57:48Z"
RELEASE_PUBLISHED_AT = "2026-07-20T12:08:53Z"
RELEASE_UPDATED_AT = "2026-07-20T12:08:53Z"
OBSERVED_AT = "2026-07-20T12:21:22.682Z"
RELEASE_NOTES_UTF8_BYTES = 3433
RELEASE_NOTES_SHA256 = (
    "665bceb884b3e4915d618efd585374b2105bd20dfda97374944162fb00b5dab5"
)
CANONICAL_RECORD_SHA256 = (
    "d5a38d89a159e66a4a2170c4194b1730947b3608e77d52b1b8308ff37b9815dd"
)

OBSERVATION_COMMENT_ID = 5021546499
OBSERVATION_COMMENT_AT = "2026-07-20T11:06:53Z"
VERIFICATION_COMMENT_ID = 5021686076
VERIFICATION_COMMENT_AT = "2026-07-20T11:24:04Z"
VERIFICATION_PAYLOAD_SHA256 = (
    "ec2995e2abf9acfa567a67ba7506ece683036f7c5afad87b9a0fb1bcc1b80a3d"
)
HUMAN_APPROVAL_COMMENT_ID = 5021955084
HUMAN_APPROVAL_COMMENT_AT = "2026-07-20T11:57:17Z"

CLASSIFICATIONS = (
    "release-blocking defect",
    "corrective patch-release candidate",
    "documentation drift",
    "governance-contract gap",
    "evaluator or test gap",
    "operational hardening",
    "future milestone candidate",
    "accepted residual risk",
    "no action required",
)
RETROSPECTIVE_AREAS = (
    "decision-proof",
    "learning-proof-and-learning-sovereignty",
    "evidence-bound-capability-memory",
    "human-approval-boundaries",
    "runtime-authority-boundaries",
    "release-governance",
)
EXPECTED_FINDING_IDS = tuple(f"m15-prg-{index:03d}" for index in range(1, 17))
REQUIRED_VERIFICATION_RUN_IDS = (
    "clean-clone-create",
    "tag-checkout-detached",
    "detached-head-symbolic-ref",
    "detached-head-commit",
    "github-release-by-tag",
    "github-latest-release",
    "github-tag-ref",
    "github-release-assets",
    "github-completion-pull-request",
    "github-issue-252",
    "github-issue-231",
    "github-issue-254",
    "github-observation-comment",
    "github-verification-comment",
    "github-approval-comment",
    "release-notes-sha256",
    "remote-main-and-tag-refs",
    "candidate-readme-git-blob",
    "candidate-readme-stale-scan",
    "tagged-release-reference-inventory",
    "tagged-m15-release-identity-mismatch-scan",
    "tag-object-type",
    "tag-commit-resolution",
    "tag-tree-resolution",
    "tagged-tree-inventory",
    "tagged-tree-object-inventory",
    "tagged-gitmodules-absence",
    "tagged-lfs-pointer-absence",
    "main-contains-completion-merge",
    "tagged-full-maintained-suite",
    "clean-clone-status-before",
    "clean-clone-status-after",
    "clean-clone-shallow-state",
    "clean-clone-promisor-state",
    "clean-clone-partial-clone-state",
    "clean-clone-sparse-state",
)

M16_MAY_BEGIN_AFTER_AUTHORIZATION = (
    "recommend-m16-planning-may-begin-after-separate-human-authorization"
)
M16_REMAIN_BLOCKED = "recommend-m16-planning-remain-blocked"

AUTHORITY_BOUNDARY = (
    "This post-release record and its evaluator are evidence only. They do not "
    "move, delete, or recreate v0.14.0; edit or republish the GitHub Release; "
    "close Issue #254; authorize M16 planning or implementation; seal Decision "
    "Proof or Learning Proof; grant capability invocation or execution "
    "authority; accept risk; execute rollback; close an audit; grant a waiver; "
    "or transfer governance authority."
)
RUNTIME_BOUNDARY = (
    "The evaluator accepts one inert caller-supplied mapping and performs no "
    "file, Git, GitHub, network, subprocess, command, clone, test, tag, release, "
    "issue, or external-state operation. It calculates only an in-memory "
    "canonical SHA-256 over the supplied mapping to pin this release-specific "
    "record; it does not verify external artifact bytes."
)

TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "document_kind",
        "record_id",
        "repository",
        "issue_number",
        "observed_at",
        "release_under_review",
        "evidence_planes",
        "tag_release_binding",
        "publication_evidence_inventory",
        "repository_consistency",
        "completion_approval_evidence",
        "verification_runs",
        "reproducibility",
        "rollback_and_correction",
        "retrospective",
        "findings",
        "classification_counts",
        "m16_planning_recommendation",
        "authority_boundary",
        "runtime_boundary",
    }
)


def _mapping(value: Any, findings: list[str], code: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        findings.append(code)
        return {}
    return value


def _sequence(value: Any, findings: list[str], code: str) -> Sequence[Any]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        findings.append(code)
        return ()
    return value


def _expect(
    value: Mapping[str, Any],
    key: str,
    expected: Any,
    findings: list[str],
    code: str,
) -> None:
    observed = value.get(key, object())
    if type(observed) is not type(expected) or observed != expected:
        findings.append(code)


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _hex_digest(value: Any, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(character in "0123456789abcdef" for character in value)
    )


def _canonical_record_sha256(value: Mapping[str, Any]) -> str | None:
    try:
        canonical = json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except (TypeError, ValueError):
        return None
    return hashlib.sha256(canonical).hexdigest()


def _validate_release_under_review(
    record: Mapping[str, Any], findings: list[str]
) -> None:
    release = _mapping(
        record.get("release_under_review"), findings, "release-under-review-malformed"
    )
    expected = (
        ("milestone", "M15", "milestone-mismatch"),
        ("completion_pull_request", COMPLETION_PULL_REQUEST, "completion-pr-mismatch"),
        (
            "completion_candidate_head_sha",
            COMPLETION_CANDIDATE_HEAD_SHA,
            "completion-candidate-mismatch",
        ),
        ("expected_merge_commit_sha", MERGE_COMMIT_SHA, "expected-merge-mismatch"),
        ("expected_merge_tree_sha", MERGE_TREE_SHA, "expected-tree-mismatch"),
        ("release_tag", RELEASE_TAG, "release-tag-mismatch"),
        ("release_title", RELEASE_TITLE, "release-title-mismatch"),
    )
    for key, value, code in expected:
        _expect(release, key, value, findings, code)


def _validate_evidence_planes(record: Mapping[str, Any], findings: list[str]) -> None:
    planes = _mapping(record.get("evidence_planes"), findings, "evidence-planes-malformed")
    tagged = _mapping(planes.get("tagged_release"), findings, "tagged-plane-malformed")
    _expect(tagged, "tag", RELEASE_TAG, findings, "tagged-plane-tag-mismatch")
    _expect(tagged, "commit_sha", MERGE_COMMIT_SHA, findings, "tagged-plane-commit-mismatch")
    _expect(tagged, "tree_sha", MERGE_TREE_SHA, findings, "tagged-plane-tree-mismatch")

    main = _mapping(planes.get("maintained_main"), findings, "main-plane-malformed")
    _expect(main, "ref", "refs/heads/main", findings, "main-plane-ref-mismatch")
    _expect(main, "commit_sha", MERGE_COMMIT_SHA, findings, "main-plane-commit-mismatch")
    _expect(main, "observed_at", OBSERVED_AT, findings, "main-plane-observation-mismatch")

    github = _mapping(planes.get("live_github"), findings, "github-plane-malformed")
    _expect(github, "release_id", RELEASE_ID, findings, "github-plane-release-mismatch")
    _expect(github, "observed_at", OBSERVED_AT, findings, "github-plane-observation-mismatch")
    _expect(github, "external_state_mutable", True, findings, "github-mutability-misrepresented")

    clone = _mapping(planes.get("clean_clone"), findings, "clone-plane-malformed")
    _expect(clone, "resolved_commit_sha", MERGE_COMMIT_SHA, findings, "clone-plane-commit-mismatch")
    _expect(clone, "working_tree_clean", True, findings, "clone-plane-dirty")


def _validate_tag_binding(record: Mapping[str, Any], findings: list[str]) -> None:
    binding = _mapping(record.get("tag_release_binding"), findings, "tag-binding-malformed")
    expected = (
        ("tag_name", RELEASE_TAG, "tag-name-mismatch"),
        ("tag_ref", "refs/tags/v0.14.0", "tag-ref-mismatch"),
        ("tag_object_type", "commit", "tag-object-type-mismatch"),
        ("annotated_tag_object_sha", None, "unexpected-annotated-tag-object"),
        ("tag_ref_target_sha", MERGE_COMMIT_SHA, "tag-target-mismatch"),
        ("peeled_commit_sha", MERGE_COMMIT_SHA, "peeled-commit-mismatch"),
        ("target_tree_sha", MERGE_TREE_SHA, "tag-tree-mismatch"),
        ("expected_merge_commit_sha", MERGE_COMMIT_SHA, "binding-expected-merge-mismatch"),
        ("completion_pr_head_sha", COMPLETION_CANDIDATE_HEAD_SHA, "binding-pr-head-mismatch"),
        ("target_equals_expected_merge_commit", True, "tag-target-not-expected-merge"),
        ("target_equals_completion_pr_head", False, "tag-target-confused-with-pr-head"),
        ("release_tag_name", RELEASE_TAG, "release-binding-tag-mismatch"),
        ("release_target_commitish", "main", "release-target-commitish-mismatch"),
        ("release_resolved_commit_sha", MERGE_COMMIT_SHA, "release-resolved-commit-mismatch"),
        ("tag_and_release_binding_match", True, "tag-release-binding-mismatch"),
        ("point_in_time_observation_only", True, "tag-observation-overclaimed"),
        ("historical_non_movement_proven", False, "historical-non-movement-overclaimed"),
    )
    for key, value, code in expected:
        _expect(binding, key, value, findings, code)
    if binding.get("tag_ref_target_sha") == COMPLETION_CANDIDATE_HEAD_SHA:
        findings.append("candidate-head-used-as-tag-target")


def _validate_publication(record: Mapping[str, Any], findings: list[str]) -> None:
    publication = _mapping(
        record.get("publication_evidence_inventory"),
        findings,
        "publication-evidence-malformed",
    )
    expected = (
        ("release_id", RELEASE_ID, "release-id-mismatch"),
        ("release_url", RELEASE_URL, "release-url-mismatch"),
        ("release_title", RELEASE_TITLE, "publication-title-mismatch"),
        ("tag_name", RELEASE_TAG, "publication-tag-mismatch"),
        ("target_commitish", "main", "publication-target-mismatch"),
        ("author_login", RELEASE_AUTHOR, "publication-author-mismatch"),
        ("created_at", RELEASE_CREATED_AT, "release-created-time-mismatch"),
        ("published_at", RELEASE_PUBLISHED_AT, "release-published-time-mismatch"),
        ("updated_at", RELEASE_UPDATED_AT, "release-updated-time-mismatch"),
        ("draft", False, "release-is-draft"),
        ("prerelease", False, "release-is-prerelease"),
        ("latest", True, "release-is-not-latest"),
        ("github_api_immutable", False, "github-immutability-observation-mismatch"),
        ("evidence_only", True, "publication-evidence-authority-overclaim"),
    )
    for key, value, code in expected:
        _expect(publication, key, value, findings, code)

    latest = _mapping(
        publication.get("latest_observation"), findings, "latest-observation-malformed"
    )
    _expect(latest, "observed_release_id", RELEASE_ID, findings, "latest-release-id-mismatch")
    _expect(latest, "matches_reviewed_release", True, findings, "latest-release-identity-mismatch")

    raw_api = _mapping(
        publication.get("raw_release_api_response"),
        findings,
        "raw-release-api-response-malformed",
    )
    _expect(raw_api, "captured_at", "2026-07-20T13:20:20.660Z", findings, "raw-release-api-capture-time-mismatch")
    _expect(raw_api, "utf8_byte_count", 5357, findings, "raw-release-api-size-mismatch")
    _expect(raw_api, "sha256", "f139e8d7c15965d600c4ee39cf35cfb3d84df575e1841057618eeaf08020484c", findings, "raw-release-api-digest-mismatch")

    notes = _mapping(publication.get("release_notes"), findings, "release-notes-malformed")
    _expect(notes, "digest_algorithm", "sha256", findings, "release-notes-algorithm-mismatch")
    _expect(notes, "digest_mode", "utf8-api-body-without-normalization", findings, "release-notes-digest-mode-mismatch")
    _expect(notes, "utf8_byte_count", RELEASE_NOTES_UTF8_BYTES, findings, "release-notes-size-mismatch")
    _expect(notes, "sha256", RELEASE_NOTES_SHA256, findings, "release-notes-digest-mismatch")
    _expect(notes, "identifies_m15_release", True, findings, "release-notes-m15-identity-missing")
    authority = _mapping(notes.get("authority_review"), findings, "release-authority-review-malformed")
    _expect(
        authority,
        "review_result",
        "no-authority-overreach-observed",
        findings,
        "release-authority-review-failed",
    )
    for key in (
        "claims_decision_proof_sealing",
        "claims_learning_proof_sealing",
        "claims_release_as_governance_approval",
        "claims_risk_acceptance",
        "claims_runtime_authority",
    ):
        _expect(authority, key, False, findings, f"release-notes-overclaim:{key}")

    assets = _mapping(publication.get("assets"), findings, "asset-inventory-malformed")
    uploaded = _sequence(assets.get("uploaded_assets"), findings, "uploaded-assets-malformed")
    count = assets.get("uploaded_asset_count")
    if type(count) is not int or count != len(uploaded):
        findings.append("asset-count-mismatch")
    for index, item in enumerate(uploaded):
        asset = _mapping(item, findings, f"asset-malformed:{index}")
        if not _hex_digest(asset.get("sha256"), 64):
            findings.append(f"asset-digest-malformed:{index}")
    _expect(
        assets,
        "asset_digests_required_when_assets_exist",
        True,
        findings,
        "asset-digest-policy-missing",
    )
    _expect(
        assets,
        "generated_source_archives_excluded",
        True,
        findings,
        "generated-source-archive-policy-mismatch",
    )
    expected_inventory = (
        "no-uploaded-release-assets" if len(uploaded) == 0 else "uploaded-release-assets-digested"
    )
    _expect(assets, "inventory_result", expected_inventory, findings, "asset-inventory-result-mismatch")


def _validate_repository_consistency(
    record: Mapping[str, Any], findings: list[str]
) -> None:
    consistency = _mapping(
        record.get("repository_consistency"), findings, "repository-consistency-malformed"
    )
    _expect(consistency, "main_ref_sha", MERGE_COMMIT_SHA, findings, "main-ref-mismatch")
    _expect(consistency, "main_contains_completion_merge", True, findings, "main-missing-completion-merge")
    pull_request = _mapping(
        consistency.get("completion_pull_request"), findings, "completion-pr-observation-malformed"
    )
    _expect(pull_request, "number", COMPLETION_PULL_REQUEST, findings, "completion-pr-number-mismatch")
    _expect(pull_request, "merged", True, findings, "completion-pr-not-merged")
    _expect(pull_request, "merge_commit_sha", MERGE_COMMIT_SHA, findings, "completion-pr-merge-mismatch")
    _expect(pull_request, "merged_at", RELEASE_CREATED_AT, findings, "completion-pr-time-mismatch")

    issues = _sequence(consistency.get("issues"), findings, "issue-observations-malformed")
    by_number: dict[int, Mapping[str, Any]] = {}
    for index, item in enumerate(issues):
        issue = _mapping(item, findings, f"issue-observation-malformed:{index}")
        number = issue.get("number")
        if type(number) is not int or number in by_number:
            findings.append(f"issue-observation-identity-invalid:{index}")
            continue
        by_number[number] = issue
    expected_issues = (
        (252, "closed", "completed", "2026-07-20T11:57:49Z"),
        (231, "closed", "completed", "2026-07-20T11:57:50Z"),
        (254, "open", None, None),
    )
    if set(by_number) != {231, 252, 254}:
        findings.append("required-issue-observations-mismatch")
    for number, state, reason, closed_at in expected_issues:
        issue = by_number.get(number, {})
        _expect(issue, "state", state, findings, f"issue-{number}-state-mismatch")
        _expect(issue, "state_reason", reason, findings, f"issue-{number}-reason-mismatch")
        _expect(issue, "closed_at", closed_at, findings, f"issue-{number}-closed-time-mismatch")

    readme = _mapping(
        consistency.get("tagged_readme_observation"),
        findings,
        "tagged-readme-observation-malformed",
    )
    _expect(readme, "observed_commit_sha", MERGE_COMMIT_SHA, findings, "readme-commit-mismatch")
    _expect(readme, "m1_through_m15_complete", True, findings, "readme-milestone-state-mismatch")
    _expect(readme, "v0_14_0_release_entry_present", True, findings, "readme-release-entry-missing")
    _expect(readme, "stale_prepublication_statement_present", True, findings, "readme-drift-observation-mismatch")
    _expect(readme, "finding_id", "m15-prg-001", findings, "readme-drift-finding-mismatch")

    candidate = _mapping(
        consistency.get("review_candidate_readme_observation"),
        findings,
        "candidate-readme-observation-malformed",
    )
    for key, expected, code in (
        ("source_role", "draft-review-candidate-worktree", "candidate-readme-source-mismatch"),
        ("path", "README.md", "candidate-readme-path-mismatch"),
        ("git_blob_sha", "c72ed99f6de5415a0295b0832e8e22a9698b567e", "candidate-readme-blob-mismatch"),
        ("canonical_text_sha256", "24e56be918627ff86f2383ec6473bc5d6789dcfeb903debf034c98576438add9", "candidate-readme-sha256-mismatch"),
        ("m1_through_m15_complete", True, "candidate-readme-milestone-state-mismatch"),
        ("v0_14_0_release_entry_present", True, "candidate-readme-release-entry-missing"),
        ("published_latest_statement_present", True, "candidate-readme-published-state-missing"),
        ("m16_separate_human_authorization_boundary_present", True, "candidate-readme-m16-boundary-missing"),
        ("stale_prepublication_statement_present", False, "candidate-readme-still-stale"),
    ):
        _expect(candidate, key, expected, findings, code)

    audit = _mapping(consistency.get("release_reference_audit"), findings, "release-reference-audit-malformed")
    _expect(audit, "correct_release_identifier", RELEASE_TAG, findings, "release-reference-mismatch")
    for key, expected, code in (
        ("tagged_tree_matching_line_count", 95, "release-reference-line-count-mismatch"),
        ("tagged_tree_matching_path_count", 33, "release-reference-path-count-mismatch"),
        ("tagged_tree_matching_transcript_sha256", "b1f86e01cd397544777df95ef34c84e51eed893099771595560b768b1bd265ef", "release-reference-transcript-mismatch"),
        ("mismatched_m15_version_association_count", 0, "release-reference-mismatch-count-nonzero"),
        ("mismatch_transcript_sha256", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "release-reference-mismatch-transcript-invalid"),
    ):
        _expect(audit, key, expected, findings, code)
    _expect(
        audit,
        "historical_prepublication_references_preserved",
        True,
        findings,
        "historical-prepublication-evidence-not-preserved",
    )
    conflicts = _sequence(
        audit.get("unclassified_conflicting_release_identifiers"),
        findings,
        "release-reference-conflicts-malformed",
    )
    if conflicts:
        findings.append("unclassified-release-reference-conflict")


def _validate_completion_approval(
    record: Mapping[str, Any], findings: list[str]
) -> None:
    approval = _mapping(
        record.get("completion_approval_evidence"),
        findings,
        "completion-approval-evidence-malformed",
    )
    _expect(approval, "pull_request_number", COMPLETION_PULL_REQUEST, findings, "approval-pr-mismatch")
    _expect(approval, "candidate_head_sha", COMPLETION_CANDIDATE_HEAD_SHA, findings, "approval-candidate-mismatch")
    _expect(approval, "github_envelope_ordering_valid", True, findings, "approval-envelope-order-invalid")
    _expect(approval, "evidence_only", True, findings, "approval-evidence-authority-overclaim")

    observation = _mapping(approval.get("observation_comment"), findings, "observation-comment-malformed")
    for key, value, code in (
        ("comment_id", OBSERVATION_COMMENT_ID, "observation-comment-id-mismatch"),
        ("author_login", RELEASE_AUTHOR, "observation-comment-author-mismatch"),
        ("created_at", OBSERVATION_COMMENT_AT, "observation-comment-time-mismatch"),
        ("updated_at", OBSERVATION_COMMENT_AT, "observation-comment-update-time-mismatch"),
        ("body_utf8_byte_count", 1230, "observation-comment-body-size-mismatch"),
        ("body_sha256", "a32abd57d3f3503bba5e17b81f385a0581c86581e81a83ccf891731120c5da6e", "observation-comment-body-digest-mismatch"),
        ("api_response_utf8_byte_count", 4554, "observation-comment-api-size-mismatch"),
        ("api_response_sha256", "99a3f0e473b56a9a815facfc16e5357d072d589db284d28ba2c7d4321b8d1340", "observation-comment-api-digest-mismatch"),
        ("binds_candidate", True, "observation-comment-candidate-unbound"),
    ):
        _expect(observation, key, value, findings, code)

    receipt = _mapping(
        approval.get("verification_receipt_comment"), findings, "verification-comment-malformed"
    )
    for key, value, code in (
        ("comment_id", VERIFICATION_COMMENT_ID, "verification-comment-id-mismatch"),
        ("author_login", RELEASE_AUTHOR, "verification-comment-author-mismatch"),
        ("created_at", VERIFICATION_COMMENT_AT, "verification-comment-time-mismatch"),
        ("updated_at", VERIFICATION_COMMENT_AT, "verification-comment-update-time-mismatch"),
        ("body_utf8_byte_count", 30769, "verification-comment-body-size-mismatch"),
        ("body_sha256", "c43fd9fcc214d56e2f30c205220f5e4e088d0aa1f029610c32e21fa77b12fd5a", "verification-comment-body-digest-mismatch"),
        ("api_response_utf8_byte_count", 36708, "verification-comment-api-size-mismatch"),
        ("api_response_sha256", "c3de9247f168969c7a3282b84fc8536b7150cd9641337232192af492b81cfea3", "verification-comment-api-digest-mismatch"),
        ("canonical_payload_sha256", VERIFICATION_PAYLOAD_SHA256, "verification-payload-digest-mismatch"),
        ("binds_candidate", True, "verification-comment-candidate-unbound"),
    ):
        _expect(receipt, key, value, findings, code)

    human = _mapping(approval.get("human_approval_comment"), findings, "human-approval-comment-malformed")
    for key, value, code in (
        ("comment_id", HUMAN_APPROVAL_COMMENT_ID, "human-approval-comment-id-mismatch"),
        ("author_login", RELEASE_AUTHOR, "human-approval-comment-author-mismatch"),
        ("created_at", HUMAN_APPROVAL_COMMENT_AT, "human-approval-comment-time-mismatch"),
        ("updated_at", HUMAN_APPROVAL_COMMENT_AT, "human-approval-comment-update-time-mismatch"),
        ("body_utf8_byte_count", 2818, "human-approval-comment-body-size-mismatch"),
        ("body_sha256", "9bbb49d001aa6e9c8bff5f54187a406d8b0489ece3d446eb44da313b6bafa650", "human-approval-comment-body-digest-mismatch"),
        ("api_response_utf8_byte_count", 4586, "human-approval-comment-api-size-mismatch"),
        ("api_response_sha256", "148b7ca01f51648389b13baa76ac99d867896fca3f2fa1cf99714d90d936fd08", "human-approval-comment-api-digest-mismatch"),
        ("binds_candidate", True, "human-approval-candidate-unbound"),
        ("binds_verification_receipt", True, "human-approval-receipt-unbound"),
        ("binds_approved_action", True, "human-approval-action-unbound"),
    ):
        _expect(human, key, value, findings, code)

    timestamps = _mapping(approval.get("event_timestamps"), findings, "approval-timestamps-malformed")
    expected_timestamps = (
        ("observation_at", OBSERVATION_COMMENT_AT),
        ("verification_at", VERIFICATION_COMMENT_AT),
        ("human_approval_at", HUMAN_APPROVAL_COMMENT_AT),
        ("merge_at", RELEASE_CREATED_AT),
        ("release_publication_at", RELEASE_PUBLISHED_AT),
    )
    timeline: list[str] = []
    for key, expected in expected_timestamps:
        _expect(timestamps, key, expected, findings, f"approval-timeline-mismatch:{key}")
        observed = timestamps.get(key)
        if isinstance(observed, str):
            timeline.append(observed)
    if len(timeline) != len(expected_timestamps) or timeline != sorted(timeline) or len(set(timeline)) != len(timeline):
        findings.append("approval-timeline-not-strictly-ordered")

    embedded = _mapping(
        approval.get("embedded_human_approval_json"),
        findings,
        "embedded-human-approval-json-malformed",
    )
    _expect(embedded, "approval_timestamp", "<RFC3339_UTC_TIMESTAMP>", findings, "approval-placeholder-time-mismatch")
    _expect(embedded, "approver_identity", "<AUTHORIZED_HUMAN_GITHUB_LOGIN>", findings, "approval-placeholder-identity-mismatch")
    _expect(embedded, "contains_placeholders", True, findings, "approval-placeholder-gap-concealed")
    _expect(
        embedded,
        "standardized_envelope_bound_record_present",
        False,
        findings,
        "approval-envelope-record-gap-concealed",
    )
    _expect(embedded, "finding_id", "m15-prg-004", findings, "approval-gap-finding-mismatch")


def _validate_verification_runs(record: Mapping[str, Any], findings: list[str]) -> None:
    runs = _sequence(record.get("verification_runs"), findings, "verification-runs-malformed")
    by_id: dict[str, Mapping[str, Any]] = {}
    for index, item in enumerate(runs):
        run = _mapping(item, findings, f"verification-run-malformed:{index}")
        command_id = run.get("command_id")
        if not _non_empty_string(command_id) or command_id in by_id:
            findings.append(f"verification-run-id-invalid:{index}")
            continue
        by_id[command_id] = run
        argv = _sequence(run.get("logical_argv"), findings, f"verification-argv-malformed:{command_id}")
        if len(argv) < 2 or any(not _non_empty_string(argument) for argument in argv):
            findings.append(f"verification-argv-invalid:{command_id}")
        expected_exit = (
            1
            if command_id
            in {
                "detached-head-symbolic-ref",
                "candidate-readme-stale-scan",
                "tagged-m15-release-identity-mismatch-scan",
                "tagged-lfs-pointer-absence",
                "clean-clone-promisor-state",
                "clean-clone-partial-clone-state",
                "clean-clone-sparse-state",
            }
            else 0
        )
        _expect(run, "exit_code", expected_exit, findings, f"verification-exit-mismatch:{command_id}")
        _expect(run, "passed", True, findings, f"verification-failed:{command_id}")
        if not _non_empty_string(run.get("result_kind")):
            findings.append(f"verification-result-kind-missing:{command_id}")
        if not _non_empty_string(run.get("result")):
            findings.append(f"verification-result-missing:{command_id}")
    if set(by_id) != set(REQUIRED_VERIFICATION_RUN_IDS):
        findings.append("required-verification-run-set-mismatch")
    expected_api_results = {
        "github-release-by-tag": "id=356696715; tag_name=v0.14.0; draft=false; prerelease=false; author=aa-os; created_at=2026-07-20T11:57:48Z; published_at=2026-07-20T12:08:53Z; updated_at=2026-07-20T12:08:53Z",
        "github-latest-release": "id=356696715; tag_name=v0.14.0; matches reviewed release=true",
        "github-tag-ref": "ref=refs/tags/v0.14.0; object.type=commit; object.sha=01870f4b844c1cda2f157e7be7bdb66317fdc738",
        "github-release-assets": "[]; uploaded_asset_count=0",
        "github-completion-pull-request": "number=253; merged=true; head.sha=b18c77f7745842aa849b53487be96c4eb5e531ca; merge_commit_sha=01870f4b844c1cda2f157e7be7bdb66317fdc738; merged_at=2026-07-20T11:57:48Z",
        "github-issue-252": "number=252; state=closed; state_reason=completed; closed_at=2026-07-20T11:57:49Z",
        "github-issue-231": "number=231; state=closed; state_reason=completed; closed_at=2026-07-20T11:57:50Z",
        "github-issue-254": "number=254; state=open; state_reason=null; closed_at=null",
        "release-notes-sha256": "{\"utf8_byte_count\":3433,\"sha256\":\"665bceb884b3e4915d618efd585374b2105bd20dfda97374944162fb00b5dab5\"}",
    }
    for command_id, expected_result in expected_api_results.items():
        _expect(
            by_id.get(command_id, {}),
            "result",
            expected_result,
            findings,
            f"verification-result-mismatch:{command_id}",
        )
    full = by_id.get("tagged-full-maintained-suite", {})
    _expect(
        full,
        "result",
        "----------------------------------------------------------------------\r\n"
        "Ran 2275 tests in 140.079s\r\n\r\nOK\r\n",
        findings,
        "tagged-full-suite-result-mismatch",
    )
    _expect(full, "actual_launcher_role", "external-cpython-outside-clean-clone", findings, "tagged-full-suite-launcher-role-mismatch")
    environment = _mapping(full.get("environment"), findings, "tagged-full-suite-environment-malformed")
    _expect(environment, "PYTHONDONTWRITEBYTECODE", "1", findings, "tagged-full-suite-bytecode-policy-mismatch")
    _expect(
        environment,
        "AAOS_TEST_GIT_EXE",
        "C:/Program Files/Git/cmd/git.exe",
        findings,
        "tagged-full-suite-git-toolchain-mismatch",
    )
    clone = by_id.get("clean-clone-create", {})
    _expect(
        clone,
        "result",
        "clone completed",
        findings,
        "clean-clone-create-result-mismatch",
    )
    checkout = by_id.get("tag-checkout-detached", {})
    _expect(
        checkout,
        "result",
        "HEAD is now at 01870f4 Merge pull request #253 from aa-os/agent/m15-track-e4-final-completion",
        findings,
        "tag-checkout-result-mismatch",
    )
    _expect(
        by_id.get("detached-head-commit", {}),
        "result",
        MERGE_COMMIT_SHA,
        findings,
        "detached-head-commit-mismatch",
    )
    inventory = by_id.get("tagged-tree-inventory", {})
    _expect(inventory, "result", "501 entries", findings, "tagged-tree-inventory-mismatch")
    _expect(
        by_id.get("tagged-tree-object-inventory", {}),
        "result",
        "501 entries; 501 blobs; 0 gitlinks; 0 symlinks",
        findings,
        "tagged-tree-object-inventory-mismatch",
    )
    _expect(
        by_id.get("tagged-gitmodules-absence", {}),
        "result",
        ".gitmodules absent",
        findings,
        "tagged-gitmodules-observation-mismatch",
    )
    _expect(
        by_id.get("tagged-lfs-pointer-absence", {}),
        "result",
        "no Git LFS pointer header matches",
        findings,
        "tagged-lfs-observation-mismatch",
    )
    for command_id in ("clean-clone-status-before", "clean-clone-status-after"):
        _expect(
            by_id.get(command_id, {}),
            "result",
            "0 paths",
            findings,
            f"{command_id}-not-empty",
        )
    shallow = by_id.get("clean-clone-shallow-state", {})
    _expect(shallow, "result", "false", findings, "clean-clone-shallow-state-mismatch")


def _validate_reproducibility(record: Mapping[str, Any], findings: list[str]) -> None:
    value = _mapping(record.get("reproducibility"), findings, "reproducibility-malformed")
    expected = (
        ("clone_url", "https://github.com/aa-os/aaos-public.git", "clone-url-mismatch"),
        ("clone_mode", "fresh-remote-clone-without-local-object-reuse", "clone-mode-mismatch"),
        ("tag_resolved_in_clean_clone", True, "clean-clone-tag-resolution-failed"),
        ("tag_checkout_command_id", "tag-checkout-detached", "tag-checkout-command-mismatch"),
        ("detached_head_confirmed", True, "detached-head-not-confirmed"),
        ("detached_head_symbolic_ref_command_id", "detached-head-symbolic-ref", "detached-head-symbolic-ref-command-mismatch"),
        ("detached_head_commit_command_id", "detached-head-commit", "detached-head-commit-command-mismatch"),
        ("resolved_commit_sha", MERGE_COMMIT_SHA, "clean-clone-commit-mismatch"),
        ("resolved_tree_sha", MERGE_TREE_SHA, "clean-clone-tree-mismatch"),
        ("tagged_tree_entry_count", 501, "tagged-tree-entry-count-mismatch"),
        ("tagged_tree_blob_count", 501, "tagged-tree-blob-count-mismatch"),
        ("tagged_tree_gitlink_count", 0, "tagged-tree-gitlink-count-mismatch"),
        ("tagged_tree_symlink_count", 0, "tagged-tree-symlink-count-mismatch"),
        ("gitmodules_present", False, "tagged-gitmodules-present"),
        ("git_lfs_pointers_present", False, "tagged-lfs-pointers-present"),
        ("tagged_source_tree_independently_inspectable", True, "tagged-tree-not-independently-inspectable"),
        ("shallow_repository", False, "clean-clone-is-shallow"),
        ("promisor_remote_configured", False, "clean-clone-promisor-remote-configured"),
        ("partial_clone_extension_configured", False, "clean-clone-partial-extension-configured"),
        ("sparse_checkout_configured", False, "clean-clone-sparse-checkout-configured"),
        ("maintained_verification_procedure_executed", True, "maintained-verification-not-executed"),
        ("maintained_verification_passed", True, "maintained-verification-failed"),
        ("verification_command_id", "tagged-full-maintained-suite", "reproducibility-command-mismatch"),
        ("working_tree_clean_before_and_after", True, "reproduction-working-tree-dirty"),
        ("clean_status_before_command_id", "clean-clone-status-before", "clean-status-before-command-mismatch"),
        ("clean_status_after_command_id", "clean-clone-status-after", "clean-status-after-command-mismatch"),
        ("repository_submodules_required", False, "unrecorded-submodule-dependency"),
        ("unrecorded_repository_state_required", False, "unrecorded-local-state-required"),
    )
    for key, expected_value, code in expected:
        _expect(value, key, expected_value, findings, code)
    source_inspection_ids = _sequence(
        value.get("source_inspection_command_ids"),
        findings,
        "source-inspection-command-ids-malformed",
    )
    if set(source_inspection_ids) != {
        "tagged-tree-object-inventory",
        "tagged-gitmodules-absence",
        "tagged-lfs-pointer-absence",
        "clean-clone-promisor-state",
        "clean-clone-partial-clone-state",
        "clean-clone-sparse-state",
    }:
        findings.append("source-inspection-command-id-set-mismatch")
    toolchain = _mapping(value.get("toolchain"), findings, "reproducibility-toolchain-malformed")
    for key, expected_value, code in (
        ("git_version", "2.55.0.windows.3", "git-version-mismatch"),
        ("python_implementation", "CPython", "python-implementation-mismatch"),
        ("python_version", "3.14.6", "python-version-mismatch"),
        ("python_launcher_role", "external-cpython-outside-clean-clone", "python-launcher-role-mismatch"),
        ("repository_local_interpreter_required", False, "repository-local-interpreter-required"),
    ):
        _expect(toolchain, key, expected_value, findings, code)


def _validate_rollback(record: Mapping[str, Any], findings: list[str]) -> None:
    value = _mapping(
        record.get("rollback_and_correction"), findings, "rollback-correction-malformed"
    )
    expected = (
        ("published_tag_immutable_by_policy", True, "published-tag-not-immutable-by-policy"),
        ("tag_move_allowed", False, "published-tag-move-allowed"),
        ("tag_delete_allowed", False, "published-tag-delete-allowed"),
        ("tag_recreate_allowed", False, "published-tag-recreation-allowed"),
        ("rollback_moves_published_tag", False, "rollback-moves-published-tag"),
        ("corrective_work_requires_successor_commit", True, "successor-commit-not-required"),
        (
            "patch_release_required_when_release_level_correction_is_appropriate",
            True,
            "patch-release-correction-policy-missing",
        ),
        (
            "historical_release_evidence_remains_discoverable",
            True,
            "historical-release-evidence-not-discoverable",
        ),
        ("release_edit_or_republication_performed", False, "release-mutation-performed"),
        ("rollback_execution_performed", False, "rollback-execution-performed"),
    )
    for key, expected_value, code in expected:
        _expect(value, key, expected_value, findings, code)
    if not _non_empty_string(value.get("supersession_and_withdrawal_semantics")):
        findings.append("supersession-semantics-missing")


def _validate_retrospective_and_findings(
    record: Mapping[str, Any], findings: list[str]
) -> tuple[list[str], dict[str, int]]:
    finding_records = _sequence(record.get("findings"), findings, "findings-malformed")
    by_id: dict[str, Mapping[str, Any]] = {}
    counts = {classification: 0 for classification in CLASSIFICATIONS}
    release_blockers: list[str] = []
    for index, item in enumerate(finding_records):
        finding = _mapping(item, findings, f"finding-malformed:{index}")
        finding_id = finding.get("finding_id")
        if not _non_empty_string(finding_id) or finding_id in by_id:
            findings.append(f"finding-id-invalid:{index}")
            continue
        by_id[finding_id] = finding
        area = finding.get("area")
        if area not in RETROSPECTIVE_AREAS:
            findings.append(f"finding-area-invalid:{finding_id}")
        classification = finding.get("classification")
        if not isinstance(classification, str) or classification not in CLASSIFICATIONS:
            findings.append(f"finding-classification-invalid:{finding_id}")
        else:
            counts[classification] += 1
            if classification == "release-blocking defect":
                release_blockers.append(finding_id)
        for key in ("title", "summary", "recommendation"):
            if not _non_empty_string(finding.get(key)):
                findings.append(f"finding-field-missing:{finding_id}:{key}")
        evidence = _sequence(
            finding.get("evidence_references"),
            findings,
            f"finding-evidence-malformed:{finding_id}",
        )
        if not evidence or any(not _non_empty_string(reference) for reference in evidence):
            findings.append(f"finding-evidence-missing:{finding_id}")
    if set(by_id) != set(EXPECTED_FINDING_IDS):
        findings.append("expected-finding-set-mismatch")

    retrospective = _sequence(
        record.get("retrospective"), findings, "retrospective-malformed"
    )
    seen_areas: set[str] = set()
    referenced_ids: set[str] = set()
    for index, item in enumerate(retrospective):
        entry = _mapping(item, findings, f"retrospective-entry-malformed:{index}")
        area = entry.get("area")
        if area not in RETROSPECTIVE_AREAS or area in seen_areas:
            findings.append(f"retrospective-area-invalid:{index}")
        elif isinstance(area, str):
            seen_areas.add(area)
        if entry.get("assessment") not in (
            "effective",
            "effective-with-follow-up",
            "release-blocking",
        ):
            findings.append(f"retrospective-assessment-invalid:{area}")
        if not _non_empty_string(entry.get("summary")):
            findings.append(f"retrospective-summary-missing:{area}")
        references = _sequence(
            entry.get("evidence_references"),
            findings,
            f"retrospective-evidence-malformed:{area}",
        )
        if not references or any(not _non_empty_string(reference) for reference in references):
            findings.append(f"retrospective-evidence-missing:{area}")
        entry_findings = _sequence(
            entry.get("finding_ids"), findings, f"retrospective-finding-ids-malformed:{area}"
        )
        if not entry_findings:
            findings.append(f"retrospective-finding-ids-missing:{area}")
        for finding_id in entry_findings:
            if finding_id not in by_id:
                findings.append(f"retrospective-finding-reference-invalid:{area}")
            elif by_id[finding_id].get("area") != area:
                findings.append(f"retrospective-finding-area-mismatch:{finding_id}")
            if isinstance(finding_id, str):
                referenced_ids.add(finding_id)
        area_has_release_blocker = any(
            by_id.get(finding_id, {}).get("classification")
            == "release-blocking defect"
            for finding_id in entry_findings
            if isinstance(finding_id, str)
        )
        if area_has_release_blocker != (entry.get("assessment") == "release-blocking"):
            findings.append(f"retrospective-release-blocking-assessment-mismatch:{area}")
    if seen_areas != set(RETROSPECTIVE_AREAS):
        findings.append("retrospective-area-set-mismatch")
    if referenced_ids != set(by_id):
        findings.append("retrospective-finding-coverage-mismatch")

    recorded_counts = _mapping(
        record.get("classification_counts"), findings, "classification-counts-malformed"
    )
    if set(recorded_counts) != set(CLASSIFICATIONS):
        findings.append("classification-count-key-set-mismatch")
    for classification, expected_count in counts.items():
        _expect(
            recorded_counts,
            classification,
            expected_count,
            findings,
            f"classification-count-mismatch:{classification}",
        )
    return sorted(release_blockers), counts


def _validate_m16_recommendation(
    record: Mapping[str, Any], release_blockers: list[str], findings: list[str]
) -> str | None:
    value = _mapping(
        record.get("m16_planning_recommendation"), findings, "m16-recommendation-malformed"
    )
    recommendation = value.get("recommendation")
    expected_recommendation = (
        M16_REMAIN_BLOCKED if release_blockers else M16_MAY_BEGIN_AFTER_AUTHORIZATION
    )
    _expect(value, "recommendation", expected_recommendation, findings, "m16-recommendation-inconsistent")
    blockers = _sequence(
        value.get("release_blocking_finding_ids"),
        findings,
        "m16-release-blocker-list-malformed",
    )
    if sorted(blockers) != release_blockers:
        findings.append("m16-release-blocker-list-mismatch")
    _expect(value, "human_authorization_required", True, findings, "m16-human-authorization-not-required")
    _expect(value, "authorized_by_this_record", False, findings, "m16-authorized-by-record")
    _expect(
        value,
        "issue_254_completion_automatically_authorizes_m16",
        False,
        findings,
        "issue-254-used-as-m16-authorization",
    )
    _expect(value, "m16_implementation_authorized", False, findings, "m16-implementation-authorized")
    if not _non_empty_string(value.get("rationale")):
        findings.append("m16-recommendation-rationale-missing")
    return recommendation if isinstance(recommendation, str) else None


def evaluate_post_release_governance_review(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a caller-supplied v0.14.0 post-release evidence record."""

    findings: list[str] = []
    value = _mapping(record, findings, "record-malformed")
    if set(value) != TOP_LEVEL_KEYS:
        findings.append("top-level-key-set-mismatch")
    canonical_record_sha256 = _canonical_record_sha256(value)
    if canonical_record_sha256 is None:
        findings.append("canonical-record-not-json-serializable")
    elif canonical_record_sha256 != CANONICAL_RECORD_SHA256:
        findings.append("canonical-record-sha256-mismatch")
    _expect(value, "schema_version", SCHEMA_VERSION, findings, "schema-version-mismatch")
    _expect(
        value,
        "document_kind",
        "m15-post-release-governance-review-record",
        findings,
        "document-kind-mismatch",
    )
    _expect(
        value,
        "record_id",
        "urn:aaos:m15:post-release-governance-review:v0.14.0:issue-254",
        findings,
        "record-id-mismatch",
    )
    _expect(value, "repository", REPOSITORY, findings, "repository-mismatch")
    _expect(value, "issue_number", ISSUE_NUMBER, findings, "issue-number-mismatch")
    _expect(value, "observed_at", OBSERVED_AT, findings, "observation-time-mismatch")

    _validate_release_under_review(value, findings)
    _validate_evidence_planes(value, findings)
    _validate_tag_binding(value, findings)
    _validate_publication(value, findings)
    _validate_repository_consistency(value, findings)
    _validate_completion_approval(value, findings)
    _validate_verification_runs(value, findings)
    _validate_reproducibility(value, findings)
    _validate_rollback(value, findings)
    release_blockers, classification_counts = _validate_retrospective_and_findings(
        value, findings
    )
    m16_recommendation = _validate_m16_recommendation(
        value, release_blockers, findings
    )
    _expect(value, "authority_boundary", AUTHORITY_BOUNDARY, findings, "authority-boundary-mismatch")
    _expect(value, "runtime_boundary", RUNTIME_BOUNDARY, findings, "runtime-boundary-mismatch")

    validation_findings = sorted(set(findings))
    complete = not validation_findings
    output_m16_recommendation = (
        m16_recommendation
        if complete
        else M16_REMAIN_BLOCKED
    )
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "outcome": (
            "record_complete_for_human_review" if complete else "record_invalid"
        ),
        "record_complete_for_human_review": complete,
        "validation_findings": validation_findings,
        "release_blocking_finding_ids": release_blockers,
        "classification_counts": classification_counts,
        "m16_planning_recommendation": output_m16_recommendation,
        "canonical_record_sha256": canonical_record_sha256,
        "canonical_record_matches": canonical_record_sha256 == CANONICAL_RECORD_SHA256,
        "caller_data_only": True,
        "file_io_performed": False,
        "git_inspection_performed": False,
        "github_access_performed": False,
        "network_access_performed": False,
        "subprocess_executed": False,
        "commands_executed": False,
        "digests_calculated": True,
        "external_artifact_digests_verified": False,
        "external_state_mutated": False,
        "tag_or_release_mutated": False,
        "issue_state_mutated": False,
        "m16_authorized": False,
        "authority_boundary": AUTHORITY_BOUNDARY,
        "runtime_boundary": RUNTIME_BOUNDARY,
    }


__all__ = [
    "AUTHORITY_BOUNDARY",
    "CANONICAL_RECORD_SHA256",
    "CLASSIFICATIONS",
    "EXPECTED_FINDING_IDS",
    "MERGE_COMMIT_SHA",
    "MERGE_TREE_SHA",
    "M16_MAY_BEGIN_AFTER_AUTHORIZATION",
    "M16_REMAIN_BLOCKED",
    "RELEASE_ID",
    "RELEASE_NOTES_SHA256",
    "RELEASE_TAG",
    "RESULT_SCHEMA_VERSION",
    "RETROSPECTIVE_AREAS",
    "RUNTIME_BOUNDARY",
    "SCHEMA_VERSION",
    "evaluate_post_release_governance_review",
]
