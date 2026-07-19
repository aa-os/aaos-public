"""Deterministic, caller-data-only evaluator for M15 Track E2.

The evaluator consumes inert mappings supplied by its caller.  It does not read
files, inspect Git or GitHub, calculate repository digests, execute commands,
create source-control objects, or mutate caller data or external state.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any


MANIFEST_SCHEMA_VERSION = "m15-release-proof-linkage/v1"
CANDIDATE_PATH_MANIFEST_SCHEMA_VERSION = (
    "m15-release-proof-linkage-candidate-path-manifest/v1"
)
MERGE_PATH_MANIFEST_SCHEMA_VERSION = (
    "m15-release-proof-linkage-merge-path-manifest/v1"
)
CONTINUITY_RECORD_SCHEMA_VERSION = (
    "m15-release-proof-linkage-continuity-record/v1"
)
E1_RECEIPT_LINKAGE_SCHEMA_VERSION = (
    "m15-release-proof-linkage-e1-receipt-linkage/v1"
)
RELEASE_BOUNDARY_REGISTER_SCHEMA_VERSION = (
    "m15-release-proof-linkage-boundary-register/v1"
)
VERIFICATION_RECEIPT_SCHEMA_VERSION = (
    "m15-release-proof-linkage-verification-receipt/v1"
)
SCENARIO_SCHEMA_VERSION = "m15-release-proof-linkage-scenario/v1"
RESULT_SCHEMA_VERSION = "m15-release-proof-linkage-result/v1"

SOURCE_BASELINE_SHA = "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f"
SOURCE_BASELINE_TREE_SHA = "a0277b8cb697c9e311118f7de67f7f6bf3534fcb"
E1_CANDIDATE_SHA = "55629976db7f7b8dc9e2153eaf67f054bd9ee708"
E1_CANDIDATE_TREE_SHA = "f4552f630e2dab5b9d34240efa8825f187b4abf1"
E1_MERGE_SHA = "27c92e290cf6ad60bada49b63fe1888511930980"
E1_MERGE_TREE_SHA = E1_CANDIDATE_TREE_SHA
STARTING_MAIN_SHA = E1_MERGE_SHA
STARTING_MAIN_TREE_SHA = E1_MERGE_TREE_SHA
E1_EXTERNAL_RECEIPT_SHA256 = (
    "86e33a67a532b11502b376f196a755b62a72a487e5f754cc2ac3752082acbb5b"
)
E1_EXTERNAL_RECEIPT_SCHEMA_VERSION = (
    "m15-operational-readiness-verification-receipt/v1"
)
E1_PR_NUMBER = 243
E1_RECEIPT_COMMENT_ID = 5015070053
E1_RECEIPT_COMMAND_COUNT = 13
E2_ISSUE_NUMBER = 248

RELEASE_PROOF_LINKED = "release_proof_linked"
NOT_READY = "not_ready"
BLOCKED = "blocked"
OUTCOMES = (RELEASE_PROOF_LINKED, NOT_READY, BLOCKED)

EXACT_TREE_MATCH = "exact_tree_match"
CANDIDATE_CHANGE_SET_PRESERVED = "candidate_change_set_preserved"
DRIFT_DETECTED = "drift_detected"
UNVERIFIED = "unverified"
CONTINUITY_RELATIONS = (
    EXACT_TREE_MATCH,
    CANDIDATE_CHANGE_SET_PRESERVED,
    DRIFT_DETECTED,
    UNVERIFIED,
)

FUTURE_RELEASE_CANDIDATE_IDENTIFIER = (
    "urn:aaos:m15:release-candidate:v0.14.0:unapproved"
)
FUTURE_RELEASE_CANDIDATE_STATE = "identified-not-authorized"

NON_AUTHORITATIVE_BOUNDARY_STATEMENT = (
    "release_proof_linked means only that the exact E1 candidate-to-merge "
    "evidence chain is complete and verified; it is not M15 completion "
    "approval, tracker #231 closure, README completion authorization, "
    "release-candidate approval, tag authorization, GitHub Release "
    "authorization, Decision Proof sealing, or Learning Proof sealing."
)
PATH_EVIDENCE_BOUNDARY_STATEMENT = (
    "Candidate and merge path evidence is inert continuity evidence only; it "
    "grants no completion, release, execution, sealing, or governance authority."
)
E1_RECEIPT_BOUNDARY_STATEMENT = (
    "The E1 external receipt linkage is inert caller-supplied evidence only; "
    "it is not merge approval, M15 completion approval, tracker #231 closure, "
    "README authorization, tag authorization, release authorization, or "
    "GitHub Release publication authorization."
)
VERIFICATION_RECEIPT_BOUNDARY_STATEMENT = (
    "The external E2 verification receipt is inert caller-supplied execution "
    "evidence only; it is not M15 completion approval, tracker #231 closure, "
    "README completion authorization, release-candidate approval, tag "
    "authorization, GitHub Release authorization, Decision Proof sealing, "
    "or Learning Proof sealing."
)
SCENARIO_BOUNDARY_STATEMENT = (
    "This standalone scenario is synthetic, inert, offline, and "
    "non-authoritative. " + NON_AUTHORITATIVE_BOUNDARY_STATEMENT
)

_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_OBJECT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_RFC3339_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
)
_PYTHON_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


_EXPECTED_PATH_ROWS = """\
docs/learning-governance/m15-operational-readiness-contract.md|d454686815611ec8e28778298b408f2b8df7defc|47d8e744d9e9be51f95f0e66eb6a511b748077ce4f5b9f49bf6a62093fb16d96|governance-contract
examples/public-integration-pack-pilot/m15-operational-readiness-01-valid-maintained-main.json|27a4dbe92808abd3122ff89843779e9c7d183719|9aad611db5379353f34815e2826bf471694193b393abbbdd71a9a153c2e9fc16|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-02-maintained-main-binding-mismatch.json|324bbf57af27c1bd813354134383cc25da5b9ef9|85ba22b02d08d6e55029c626f483337ad8febff884e01ed1325f067478d7c1da|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-03-source-track-binding-mismatch.json|828ad36732db7aea16ebdeff1bd6c20e5202dfac|44616ae315d9d00140ce2b1c4faabd32479053b7560d95b6a2ba2b37adac7c9b|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-04-incomplete-artifact-inventory.json|1937fa7f8039728c33ec36dee83616ada7c2f625|8c4e8a70f6fc52bf32d1c07cf5c788bf6787165bde00532d94bc7ba1f4fb5110|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-05-artifact-integrity-failure.json|19d67542103b5ead8b9c28ee355815148d017505|fd1055a4d0d1699187deb2c041c358e260d2622f514caca966e9e85c1c3dabe7|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-06-internal-consistency-failure.json|aa60a7229dee9ef0aaee06817159e12a83fd46c5|73dc57c22802c81fff132badd7e86b84c2b2d1c9caddf60ea467b12a6e803c2a|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-07-cross-control-matrix-unbound.json|3050c571c067d11b42addaa6b4660191c3273754|143957f60cf1da7ab08f108331861e198b95fa8425d092d6d3f11b7a90d10b78|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-08-incomplete-test-coverage.json|edff791f05136f67762c7e8b9f6d3ae578e133a3|7f170117fb4f2805bb9ae4678599df8166ce80ef1e1ca8a4e696e9fd24d4f778|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-09-incomplete-verification-command-manifest.json|22c6891b91aec4b4ce1bc8e1e7a86916bfbbdfec|ce72f6edcfd49b14253d2118b802cbc282ce0ac638955a57b63a22ed44243705|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-10-verification-execution-claimed.json|11f1290eb8e75acaf1cd84a2811bbb5704e6950e|c5ee061a8e0517741d6cbf527778eb8e8adf1f2dfc111916741aa9c9779c01ca|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-11-completion-approval-claim.json|38e22ca9a82fff8649f8a582ee894368d04e4887|73567d971012393ddc119eb83062642cc2959516be50771cdc6cd76085030b5c|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-12-tracker-closure-claim.json|b7f72df2cf26f920f7edfc56935dffade31d0161|0244643637e551b3277604906da3048241130575b26f8d704d97057def73fb2e|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-13-m15-completion-claim.json|f911604ac5998f243494ba502a3f08536044d728|31e7d71239db392ff0809959cba7adee5b8c5a9d984087b28733a4b4d9269184|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-14-readme-authorization-claim.json|d185c556afa544f758d4148121d187dbe40a7aa1|75294b248efefe6b8295ae351ecfb28b3171612905a34efd4c9251c9deba025d|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-15-tag-authorization-or-creation-claim.json|47a92fc9915fefa002078df350381e34907b4257|a5d17e8c2d67aefbb100054d50edc177ae6a31685963ed475ebb9fac0c717f5f|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-16-release-authorization-or-publication-claim.json|55ab272a6fbf68f404d7e642a066a98abfbb0159|98781331e52175fd74e8d480e4fb960c0bf77a98a1feaf920a3a8644eba818b6|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-17-known-repository-local-completion-blocker.json|6964c11c9433531ba811b8e83668808a06308c90|042b14f1428a811ca8f4f3fd5005572e961de2d68b160ba9744df125c3ad0629|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-18-malformed-schema-version.json|d618aa09533764089db31135b8274dbe1771c97d|f82ad6bb84e979d930654e91320f19e27cdf248e2a77fb2d8cbd036e23f3f3f7|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-19-failed-targeted-test.json|e25bb9a8e0ba76aca1c490c7f2b401c7d43a73d0|335785bbbf6eed8c045053a22edd01944a5d72d24513e35ed7e67af892674e35|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-20-test-error.json|a8a2c1a6e516272b4f639d20648103a69d8ec44e|002e8d6d7843d78de5d1c6b0e0574cd85ab17f4fb053a2c73c0170118fd80699|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-21-unexpected-skip.json|120948d02c55cbd102b1ffe0ab76cb7ef313e9cb|f269d73f9ebf83d3e79a9776e014acdbec2bbb7e007ccfbd4833664d03545602|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-22-missing-verification-result.json|52883a2e9a0b22a5b766bfb3393e69758abc24e4|0cb48dfa8df43c23415c2f11058590e4be15609f3d37bc8fbcbfab48a21ef9e7|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-23-observed-test-count-mismatch.json|bce3df2510ef477c718c8975846d8b6ede5e87e6|9e7fb4c833078e8fe2ff7e4826f0a91f8010e281d0c794a1e9bec5f8c326115d|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-24-verification-result-missing-main-sha.json|414557f5cccdf7d413b29a4798d25bd4a37e290f|e659fedc52e439927bb7eb80a14c8de24bc099a7db681296357625e2b58f6045|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-25-required-artifact-unverified.json|6f5a687b37b0519926312d5d75ca6a8cf6f375e9|9b841c41ebebcae2dba8da5cdae8e46b4f71c17abdae2341a49169c3bd80a52f|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-26-deferred-artifact-without-reason.json|ef300568c8f84413ca7ac7c9aeff34d9c422949c|51aa84a12fc0bde3b08aca7f6cfa7aecf8136690a41fcfd6a195e9c1734bc1bf|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-27-track-d-external-control-dependency-drift.json|c3300fb87029848b0efaa41bcefc5980eb34c931|1b2bda2f12c7ed62c1c3f96e9806a5985e2f43c010a544bc5e73c3c1e25aa8c0|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-28-candidate-head-receipt-binding-mismatch.json|28a31e146a173bf278837219fe7651ae02140d76|06f42ddcc8c571863fa1fdfe67736332bbd3d80ffe1ef4a65058a08394fa3089|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-29-baseline-candidate-sha-conflation.json|3f0bdaaa11c1026258855bd54c822d39e888b2dd|2d6365a1f2dca4c5e98fe77bf987f095b7fbe6f3b1ee8df8e913d2bea087674b|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-30-missing-external-execution-receipt.json|06ec329938386a85750279e2ec4a7ac1db496b71|f821dfcd998d081628a6c74149ae095ec8be499ca3d7e0bdf656100081aff649|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-31-undeclared-python-launcher-substitution.json|d4e48eb8b19a3e4ff8e72aefe99445559665be69|bbf96ef0105597e9046ba5cce4628f9a10d490b34aed71b16d499eeb19ac0d67|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-32-missing-python-interpreter-version.json|d46089d1c24dba38b84c5a6daa01dfd57027d9b1|f79a9f71a7894049ee4d7d86d74d7f8906e51d9bf3ae6a8e1db6a23e25ebbda2|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-33-missing-transcript-digest.json|337b373240c9d93b3737d31846d4edf3bc0fbeff|b5ea416c201582de191c6c41f4addd426fb7c63a8fad7fd7ba6a5d6e22e7ba1e|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-34-command-result-binding-mismatch.json|0176d4a1355092df6f4635d5d349803eb7a26022|ea3610e1f46116730c85aa3eb85839a115740009838a22714ad58b742465d524|standalone-synthetic-fixture
examples/public-integration-pack-pilot/m15-operational-readiness-manifest.json|99ebb1bb51875c3f5c5e1bd959868097d67ec94f|9e8021398e643330779fcbb0f04a15bbbbf88d238ec0d29eb7d41697158e2eb5|operational-readiness-manifest
runtime/m15_operational_readiness_evaluator.py|432dc6124a4bc233f4b5e2ece6bd6879b257d730|13021d344cc47c34f2bf3c54ba0a88c54468c10408c67c18c86eaab3e674c627|offline-evaluator
schemas/m15-operational-readiness.schema.json|92368bfd000ea7b2a41139594fa8f4a4a8471198|bacbf3ed130356c12b6407623e9fded74e4ac0d85af0415c328ffcdff280d53a|strict-schema
tests/test_m15_operational_readiness_evaluator.py|f3b58fdfb117230b3ba06d1d2af609d6eed922b2|87e1bcc65cee94617bc8656cd02864b400c08bbe611e651e4d7ed9cc48544c60|focused-tests
"""


def _expected_paths() -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for index, row in enumerate(_EXPECTED_PATH_ROWS.splitlines(), start=1):
        path, blob_sha, digest, role = row.split("|")
        rows[path] = {
            "path_id": f"m15-e2-e1-path-{index:02d}",
            "candidate_blob_sha": blob_sha,
            "candidate_canonical_sha256": digest,
            "artifact_role": role,
        }
    return rows


EXPECTED_PATHS = _expected_paths()
EXPECTED_CHANGE_TYPE_COUNTS = {
    "addition": 39,
    "modification": 0,
    "rename": 0,
    "deletion": 0,
}


_BASE_UNITTEST = ["python", "-X", "faulthandler", "-m", "unittest"]


def _unittest_command(*selectors: str) -> list[str]:
    return [*_BASE_UNITTEST, *selectors, "-v"]


EXPECTED_VERIFICATION_COMMANDS: dict[str, dict[str, Any]] = {
    "run_m15_e2_targeted_tests": {
        "argv": _unittest_command("tests.test_m15_release_proof_linkage_evaluator"),
        "test_scope": "M15 Track E2 targeted tests",
        "execution_scope": "e2-candidate-validation",
    },
    "run_m15_e1_targeted_tests": {
        "argv": _unittest_command("tests.test_m15_operational_readiness_evaluator"),
        "test_scope": "M15 Track E1 targeted tests",
        "execution_scope": "inherited-regression",
    },
    "run_m15_track_a_tests": {
        "argv": _unittest_command("tests.test_m15_learning_proof_evaluator"),
        "test_scope": "M15 Track A tests",
        "execution_scope": "inherited-regression",
    },
    "run_m15_track_b_tests": {
        "argv": _unittest_command("tests.test_m15_capability_memory_pack_evaluator"),
        "test_scope": "M15 Track B tests",
        "execution_scope": "inherited-regression",
    },
    "run_m15_track_c_tests": {
        "argv": _unittest_command("tests.test_m15_lineage_rollback_portability_evaluator"),
        "test_scope": "M15 Track C tests",
        "execution_scope": "inherited-regression",
    },
    "run_m15_track_d_tests": {
        "argv": _unittest_command("tests.test_m15_cross_control_regression_evaluator"),
        "test_scope": "M15 Track D tests",
        "execution_scope": "inherited-regression",
    },
    "run_m14_public_output_tests": {
        "argv": _unittest_command("tests.test_public_issue_exfiltration_gate_evaluator"),
        "test_scope": "M14 public-output tests",
        "execution_scope": "inherited-regression",
    },
    "run_m14_provenance_tests": {
        "argv": _unittest_command("tests.test_ai_authored_pr_provenance_evaluator"),
        "test_scope": "M14 provenance tests",
        "execution_scope": "inherited-regression",
    },
    "run_m14_skill_admission_tests": {
        "argv": _unittest_command("tests.test_skill_admission_evaluator"),
        "test_scope": "M14 skill-admission tests",
        "execution_scope": "inherited-regression",
    },
    "run_external_evidence_admission_tests": {
        "argv": _unittest_command("tests.test_external_evidence_admission_evaluator"),
        "test_scope": "external-evidence-admission tests",
        "execution_scope": "inherited-regression",
    },
    "run_m14_cross_control_authority_tests": {
        "argv": _unittest_command(
            "tests.test_m14_cross_control_authority_boundary_evaluator"
        ),
        "test_scope": "M14 cross-control authority tests",
        "execution_scope": "inherited-regression",
    },
    "run_decision_proof_ownership_tests": {
        "argv": _unittest_command(
            "tests.test_m15_learning_proof_evaluator.M15LearningProofEvaluatorTests.test_22_decision_proof_cannot_automatically_become_memory",
            "tests.test_m15_learning_proof_evaluator.M15LearningProofEvaluatorTests.test_23_decision_proof_reference_is_linkage_only_not_memory_authority",
            "tests.test_m15_capability_memory_pack_evaluator.M15CapabilityMemoryPackEvaluatorTests.test_38_learning_proof_linkage_cannot_be_used_as_authority",
            "tests.test_m15_capability_memory_pack_evaluator.M15CapabilityMemoryPackEvaluatorTests.test_39_decision_proof_linkage_cannot_grant_execution_authority",
            "tests.test_m15_lineage_rollback_portability_evaluator.M15TrackCCrossTrackLinkageTests",
            "tests.test_m15_cross_control_regression_evaluator.DecisionProofOwnershipTests",
        ),
        "test_scope": "Decision Proof ownership tests",
        "execution_scope": "inherited-regression",
    },
    "run_release_state_and_m15_status_tests": {
        "argv": _unittest_command(
            "tests.test_m15_lineage_rollback_portability_evaluator.M15TrackCReleaseStateTests",
            "tests.test_m15_cross_control_regression_evaluator.TrackDContractTests.test_matrix_preserves_release_state",
            "tests.test_m15_cross_control_regression_evaluator.ReleaseM15StatusTests",
        ),
        "test_scope": "release-state and M15-status tests",
        "execution_scope": "inherited-regression",
    },
    "run_full_maintained_repository_suite": {
        "argv": [*_BASE_UNITTEST, "discover", "-s", "tests", "-v"],
        "test_scope": "full maintained repository suite",
        "execution_scope": "candidate-full-suite-integration",
    },
}


REQUIRED_LINKAGE_BLOCKERS = (
    "missing-continuity-evidence",
    "candidate-merge-mismatch",
    "missing-receipt-binding",
    "incomplete-path-coverage",
    "unexplained-digest-or-mode-drift",
)
REQUIRED_FUTURE_PREREQUISITES = (
    "track-e3-not-completed",
    "track-e4-not-completed",
    "final-m15-completion-not-approved",
    "tracker-231-open",
    "readme-completion-not-authorized",
    "v0.14.0-tag-not-authorized",
    "github-release-not-authorized",
)


EXPECTED_SCENARIO_TITLES = {
    "m15-e2-01": "Exact E1 candidate and merge tree match",
    "m15-e2-02": "Candidate changes preserved with explained base advancement",
    "m15-e2-03": "E1 candidate head mismatch",
    "m15-e2-04": "E1 candidate tree mismatch",
    "m15-e2-05": "E1 merge commit mismatch",
    "m15-e2-06": "E1 merge tree is missing",
    "m15-e2-07": "Required candidate path is missing after merge",
    "m15-e2-08": "Candidate and merge blob mismatch",
    "m15-e2-09": "Candidate and merge canonical digest mismatch",
    "m15-e2-10": "Candidate and merge file mode mismatch",
    "m15-e2-11": "Unexpected path substitution",
    "m15-e2-12": "Incomplete candidate changed-path manifest",
    "m15-e2-13": "Incomplete merge-result path manifest",
    "m15-e2-14": "Missing E1 external receipt linkage",
    "m15-e2-15": "E1 external receipt digest mismatch",
    "m15-e2-16": "E1 receipt bound to another candidate",
    "m15-e2-17": "E1 receipt bound to another baseline",
    "m15-e2-18": "E1 receipt treated as merge approval",
    "m15-e2-19": "Provenance success treated as human approval",
    "m15-e2-20": "Operational readiness treated as completion approval",
    "m15-e2-21": "Merge commit treated as a published release",
    "m15-e2-22": "Future v0.14.0 candidate represented as tagged",
    "m15-e2-23": "GitHub Release represented as published",
    "m15-e2-24": "Tracker 231 represented as closed",
    "m15-e2-25": "M15 represented as complete",
    "m15-e2-26": "README completion represented as authorized",
    "m15-e2-27": "Required E2 linkage blocker omitted",
    "m15-e2-28": "Unverified continuity treated as linked",
    "m15-e2-29": "Future release-candidate identifier is missing",
    "m15-e2-30": "Release proof claims Decision Proof or Learning Proof sealing",
    "m15-e2-31": "Unverified continuity remains not ready",
    "m15-e2-32": "Candidate modification is preserved",
    "m15-e2-33": "Candidate rename is preserved",
    "m15-e2-34": "Candidate deletion is preserved",
    "m15-e2-35": "External E2 verification receipt is missing",
    "m15-e2-36": "External E2 verification receipt is inconsistent",
}


_MANIFEST_FIELDS = frozenset(
    {
        "schema_version",
        "document_type",
        "record_id",
        "issue",
        "track",
        "repository",
        "branch",
        "source_main_base_sha",
        "source_main_base_tree_sha",
        "execution_subject_type",
        "execution_candidate_reference",
        "execution_candidate_head_sha",
        "parent_tracker",
        "historical_bindings",
        "record_references",
        "expected_candidate_changed_path_count",
        "verification_command_manifest",
        "external_verification_receipt_required",
        "external_verification_receipt_schema_version",
        "allowed_continuity_relations",
        "declared_continuity_relation",
        "allowed_outcomes",
        "declared_outcome",
        "future_release_candidate",
        "non_authoritative_boundary_statement",
    }
)
_HISTORICAL_BINDING_FIELDS = frozenset(
    {
        "source_baseline_commit_sha",
        "source_baseline_tree_sha",
        "e1_candidate_commit_sha",
        "e1_candidate_tree_sha",
        "e1_merge_commit_sha",
        "e1_merge_tree_sha",
        "e1_merge_parent_shas",
        "e1_pull_request_number",
        "e1_receipt_comment_id",
        "e1_receipt_canonical_sha256",
    }
)
_RECORD_REFERENCE_FIELDS = frozenset(
    {
        "candidate_changed_path_manifest",
        "merge_result_path_manifest",
        "candidate_to_merge_continuity_record",
        "e1_external_receipt_linkage_record",
        "release_boundary_register",
    }
)
_COMMAND_MANIFEST_FIELDS = frozenset(
    {
        "command_count",
        "environment",
        "execution_policy",
        "commands_executed_by_evaluator",
        "commands",
    }
)
_COMMAND_FIELDS = frozenset(
    {
        "command_id",
        "argv",
        "test_scope",
        "execution_scope",
        "required",
        "expected_exit_code",
        "executed_by_evaluator",
    }
)
_CANDIDATE_MANIFEST_FIELDS = frozenset(
    {
        "schema_version",
        "document_type",
        "record_id",
        "issue",
        "source_baseline_commit_sha",
        "candidate_commit_sha",
        "candidate_tree_sha",
        "derivation",
        "changed_path_count",
        "change_type_counts",
        "paths",
        "generated_by_evaluator",
        "non_authoritative_boundary_statement",
    }
)
_CANDIDATE_PATH_FIELDS = frozenset(
    {
        "path_id",
        "path",
        "previous_path",
        "change_type",
        "baseline_blob_sha",
        "candidate_blob_sha",
        "candidate_canonical_sha256",
        "candidate_file_mode",
        "artifact_role",
        "required_status",
        "evidence_reference",
    }
)
_MERGE_MANIFEST_FIELDS = frozenset(
    {
        "schema_version",
        "document_type",
        "record_id",
        "issue",
        "candidate_commit_sha",
        "merge_commit_sha",
        "merge_tree_sha",
        "candidate_changed_path_count",
        "observed_path_count",
        "paths",
        "generated_by_evaluator",
        "non_authoritative_boundary_statement",
    }
)
_MERGE_PATH_FIELDS = frozenset(
    {
        "path_id",
        "path",
        "source_change_type",
        "merge_blob_sha",
        "merge_canonical_sha256",
        "merge_file_mode",
        "presence_state",
        "continuity_status",
        "continuity_evidence_reference",
    }
)
_CONTINUITY_FIELDS = frozenset(
    {
        "schema_version",
        "document_type",
        "record_id",
        "issue",
        "source_baseline_commit_sha",
        "source_baseline_tree_sha",
        "candidate_commit_sha",
        "candidate_tree_sha",
        "merge_commit_sha",
        "merge_tree_sha",
        "merge_parent_shas",
        "merge_parent_count",
        "candidate_is_merge_parent",
        "source_baseline_is_merge_parent",
        "merge_parent_inclusion_verified",
        "base_advancement",
        "complete_path_coverage",
        "preserved_path_count",
        "missing_paths",
        "blob_mismatches",
        "digest_mismatches",
        "file_mode_mismatches",
        "unexpected_substitutions",
        "additional_merge_difference_count",
        "additional_merge_difference_explanations",
        "allowed_relations",
        "continuity_relation",
        "evidence_reference",
        "generated_by_evaluator",
        "non_authoritative_boundary_statement",
    }
)
_BASE_ADVANCEMENT_FIELDS = frozenset(
    {
        "present",
        "advanced_base_sha",
        "source_baseline_is_ancestor",
        "explanation",
        "evidence_reference",
    }
)
_E1_RECEIPT_FIELDS = frozenset(
    {
        "schema_version",
        "document_type",
        "record_id",
        "issue",
        "source_pull_request_number",
        "source_comment_id",
        "receipt_schema_version",
        "source_baseline_commit_sha",
        "candidate_commit_sha",
        "command_count",
        "canonical_receipt_json_sha256",
        "receipt_present",
        "linkage_state",
        "external_to_e1_candidate",
        "caller_supplied_inert_evidence",
        "fetched_by_evaluator",
        "treated_as_merge_approval",
        "non_authoritative_boundary_statement",
    }
)
_BOUNDARY_REGISTER_FIELDS = frozenset(
    {
        "schema_version",
        "document_type",
        "record_id",
        "issue",
        "parent_tracker",
        "e2_linkage_blocker_count",
        "e2_linkage_blockers",
        "future_release_prerequisite_count",
        "future_release_prerequisites",
        "future_release_candidate",
        "governance_boundary",
        "non_authoritative_boundary_statement",
    }
)
_REGISTER_ENTRY_FIELDS = frozenset(
    {"blocker_id", "state", "evidence_reference", "notes"}
)
_PREREQUISITE_ENTRY_FIELDS = frozenset(
    {"prerequisite_id", "state", "evidence_reference", "notes"}
)
_RELEASE_CANDIDATE_FIELDS = frozenset({"identifier", "state"})
_GOVERNANCE_FIELDS = frozenset(
    {
        "tracker_231_state",
        "m15_state",
        "track_e3_implemented",
        "track_e4_implemented",
        "readme_completion_authorized",
        "v0_14_0_tag_state",
        "github_release_state",
        "github_release_latest",
        "completion_approved",
        "release_candidate_approved",
        "tag_authorized",
        "github_release_authorized",
        "decision_proof_sealed",
        "learning_proof_sealed",
        "deployment_authorized",
        "risk_accepted",
        "audit_closed",
        "waiver_granted",
        "authority_transferred",
    }
)
_VERIFICATION_RECEIPT_FIELDS = frozenset(
    {
        "schema_version",
        "document_type",
        "repository",
        "issue_number",
        "pull_request_number",
        "source_main_base_sha",
        "execution_subject_type",
        "execution_candidate_reference",
        "execution_candidate_head_sha",
        "command_receipt_count",
        "commands",
        "external_to_candidate_commit",
        "executed_by_evaluator",
        "non_authoritative_boundary_statement",
    }
)
_VERIFICATION_COMMAND_RECEIPT_FIELDS = frozenset(
    {
        "command_id",
        "declared_logical_argv",
        "actual_argv",
        "execution_scope",
        "execution_candidate_head_sha",
        "executable_binding",
        "tests_observed",
        "passes",
        "failures",
        "errors",
        "skips",
        "exit_code",
        "execution_timestamp",
        "transcript_sha256",
        "evidence_reference",
        "executed_by_evaluator",
        "verification_results_are_release_authority",
    }
)
_EXECUTABLE_BINDING_FIELDS = frozenset(
    {
        "declared_launcher",
        "actual_launcher",
        "launcher_substitution_detected",
        "launcher_substitution_declared",
        "python_implementation",
        "python_version",
    }
)
_SCENARIO_FIELDS = frozenset(
    {
        "schema_version",
        "document_type",
        "scenario_id",
        "title",
        "synthetic",
        "expected_outcome",
        "expected_relation",
        "evidence_state",
        "notes",
    }
)
_SCENARIO_STATE_FIELDS = frozenset(
    {
        "historical_bindings_present",
        "candidate_head_binding_valid",
        "candidate_tree_binding_valid",
        "merge_commit_binding_valid",
        "merge_tree_present",
        "merge_parent_binding_valid",
        "candidate_manifest_complete",
        "merge_manifest_complete",
        "required_candidate_paths_present_after_merge",
        "blob_continuity_valid",
        "canonical_digest_continuity_valid",
        "file_mode_continuity_valid",
        "unexpected_path_substitution_absent",
        "e1_receipt_present",
        "e1_receipt_digest_valid",
        "e1_receipt_candidate_binding_valid",
        "e1_receipt_baseline_binding_valid",
        "e1_receipt_treated_as_merge_approval",
        "provenance_treated_as_human_approval",
        "operational_readiness_treated_as_completion_approval",
        "merge_commit_treated_as_published_release",
        "release_candidate_identifier_present",
        "release_candidate_state",
        "github_release_state",
        "tracker_231_state",
        "m15_state",
        "readme_completion_authorized",
        "linkage_blocker_register_complete",
        "unresolved_linkage_blocker_count",
        "continuity_verified",
        "unverified_continuity_treated_as_linked",
        "decision_proof_sealing_claimed",
        "learning_proof_sealing_claimed",
        "candidate_and_merge_trees_equal",
        "candidate_change_set_preserved",
        "additional_merge_differences_explained",
        "future_release_prerequisites_visible",
        "external_e2_verification_receipt_present",
        "external_e2_verification_receipt_consistent",
        "change_type",
    }
)


def _mapping_has_exact_fields(value: Any, fields: frozenset[str]) -> bool:
    return isinstance(value, Mapping) and frozenset(value.keys()) == fields


def _is_bool(value: Any) -> bool:
    return type(value) is bool


def _is_nonnegative_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _is_object_sha(value: Any) -> bool:
    return isinstance(value, str) and bool(_OBJECT_SHA_RE.fullmatch(value))


def _is_digest(value: Any) -> bool:
    return isinstance(value, str) and bool(_DIGEST_RE.fullmatch(value))


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _safe_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(_is_nonempty_string(item) for item in value)


def evaluate_path_continuity(
    candidate_entry: Mapping[str, Any],
    merge_entry: Mapping[str, Any],
) -> dict[str, Any]:
    """Compare one caller-supplied candidate path with one merge-result path."""

    findings: set[str] = set()
    if not _mapping_has_exact_fields(candidate_entry, _CANDIDATE_PATH_FIELDS):
        findings.add("candidate_path_shape_invalid")
    if not _mapping_has_exact_fields(merge_entry, _MERGE_PATH_FIELDS):
        findings.add("merge_path_shape_invalid")
    if findings:
        return {"continuity_status": "unverified", "findings": sorted(findings)}

    change_type = candidate_entry.get("change_type")
    if change_type not in {"addition", "modification", "rename", "deletion"}:
        findings.add("candidate_change_type_invalid")
    if merge_entry.get("source_change_type") != change_type:
        findings.add("change_type_binding_mismatch")
    if candidate_entry.get("path_id") != merge_entry.get("path_id"):
        findings.add("path_id_mismatch")
    if candidate_entry.get("path") != merge_entry.get("path"):
        findings.add("path_substitution")

    previous_path = candidate_entry.get("previous_path")
    baseline_blob = candidate_entry.get("baseline_blob_sha")
    candidate_blob = candidate_entry.get("candidate_blob_sha")
    candidate_digest = candidate_entry.get("candidate_canonical_sha256")
    candidate_mode = candidate_entry.get("candidate_file_mode")
    merge_blob = merge_entry.get("merge_blob_sha")
    merge_digest = merge_entry.get("merge_canonical_sha256")
    merge_mode = merge_entry.get("merge_file_mode")
    presence = merge_entry.get("presence_state")

    if change_type == "addition":
        if previous_path is not None or baseline_blob is not None:
            findings.add("addition_baseline_semantics_invalid")
    elif change_type == "modification":
        if previous_path is not None or not _is_object_sha(baseline_blob):
            findings.add("modification_baseline_semantics_invalid")
    elif change_type == "rename":
        if not _is_nonempty_string(previous_path) or not _is_object_sha(baseline_blob):
            findings.add("rename_baseline_semantics_invalid")
        elif previous_path == candidate_entry.get("path"):
            findings.add("rename_path_semantics_invalid")
    elif change_type == "deletion":
        if previous_path is not None or not _is_object_sha(baseline_blob):
            findings.add("deletion_baseline_semantics_invalid")

    if change_type == "deletion":
        if any(value is not None for value in (candidate_blob, candidate_digest, candidate_mode)):
            findings.add("deletion_candidate_presence_invalid")
        if presence != "absent":
            findings.add("deleted_path_present_after_merge")
        if any(value is not None for value in (merge_blob, merge_digest, merge_mode)):
            findings.add("deleted_path_merge_identity_invalid")
    else:
        if presence != "present":
            findings.add("required_path_missing_after_merge")
        if not _is_object_sha(candidate_blob) or not _is_object_sha(merge_blob):
            findings.add("blob_shape_invalid")
        elif candidate_blob != merge_blob:
            findings.add("blob_mismatch")
        if not _is_digest(candidate_digest) or not _is_digest(merge_digest):
            findings.add("canonical_digest_shape_invalid")
        elif candidate_digest != merge_digest:
            findings.add("canonical_digest_mismatch")
        if candidate_mode not in {"100644", "100755", "120000", "160000"}:
            findings.add("candidate_file_mode_invalid")
        if merge_mode not in {"100644", "100755", "120000", "160000"}:
            findings.add("merge_file_mode_invalid")
        elif candidate_mode != merge_mode:
            findings.add("file_mode_mismatch")

    status = "preserved" if not findings else "drifted"
    return {"continuity_status": status, "findings": sorted(findings)}


def _result(
    blocking_findings: set[str],
    readiness_findings: set[str],
    linkage_blockers: set[str],
    *,
    continuity_relation: str = UNVERIFIED,
    candidate_path_count: int = 0,
    merge_path_count: int = 0,
    preserved_path_count: int = 0,
    external_verification_receipt_validated: bool = False,
) -> dict[str, Any]:
    blocking = sorted(blocking_findings)
    readiness = sorted(readiness_findings)
    outcome = BLOCKED if blocking else NOT_READY if readiness else RELEASE_PROOF_LINKED
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "outcome": outcome,
        "release_proof_linked": outcome == RELEASE_PROOF_LINKED,
        "continuity_relation": continuity_relation,
        "findings": sorted(set(blocking) | set(readiness)),
        "blocking_findings": blocking,
        "readiness_findings": readiness,
        "e2_linkage_blockers": sorted(linkage_blockers),
        "future_release_prerequisites": list(REQUIRED_FUTURE_PREREQUISITES),
        "candidate_changed_path_count": candidate_path_count,
        "merge_result_path_count": merge_path_count,
        "preserved_path_count": preserved_path_count,
        "external_verification_receipt_validated": (
            external_verification_receipt_validated
        ),
        "future_release_candidate": {
            "identifier": FUTURE_RELEASE_CANDIDATE_IDENTIFIER,
            "state": FUTURE_RELEASE_CANDIDATE_STATE,
        },
        "tracker_231_state": "open",
        "m15_state": "active-and-incomplete",
        "v0_14_0_state": "unpublished",
        "track_e3_implemented": False,
        "track_e4_implemented": False,
        "caller_data_only": True,
        "file_io_performed": False,
        "git_inspection_performed": False,
        "github_access_performed": False,
        "repository_digests_calculated": False,
        "verification_commands_executed": False,
        "external_state_mutated": False,
        "non_authoritative_boundary_statement": NON_AUTHORITATIVE_BOUNDARY_STATEMENT,
    }


def _validate_manifest(
    value: Any,
    blocking: set[str],
    readiness: set[str],
) -> None:
    if not _mapping_has_exact_fields(value, _MANIFEST_FIELDS):
        blocking.add("manifest_shape_invalid")
        return
    expected_scalars = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "document_type": "release-proof-linkage-manifest",
        "record_id": "urn:aaos:m15:release-proof-linkage:e2",
        "issue": "#248",
        "track": "E2",
        "repository": "aa-os/aaos-public",
        "branch": "feature/m15-release-proof-linkage",
        "source_main_base_sha": STARTING_MAIN_SHA,
        "source_main_base_tree_sha": STARTING_MAIN_TREE_SHA,
        "execution_subject_type": "pull-request-candidate-checkout",
        "execution_candidate_reference": "branch:feature/m15-release-proof-linkage",
        "parent_tracker": "#231",
        "expected_candidate_changed_path_count": len(EXPECTED_PATHS),
        "external_verification_receipt_required": True,
        "external_verification_receipt_schema_version": (
            VERIFICATION_RECEIPT_SCHEMA_VERSION
        ),
        "non_authoritative_boundary_statement": NON_AUTHORITATIVE_BOUNDARY_STATEMENT,
    }
    for field, expected in expected_scalars.items():
        if value.get(field) != expected:
            blocking.add(f"manifest_binding_mismatch:{field}")
    if value.get("execution_candidate_head_sha") is not None:
        blocking.add("manifest_candidate_head_self_reference")
    if value.get("allowed_continuity_relations") != list(CONTINUITY_RELATIONS):
        blocking.add("manifest_relation_vocabulary_invalid")
    if value.get("declared_continuity_relation") not in CONTINUITY_RELATIONS:
        blocking.add("manifest_declared_relation_invalid")
    if value.get("allowed_outcomes") != list(OUTCOMES):
        blocking.add("manifest_outcome_vocabulary_invalid")
    if value.get("declared_outcome") not in OUTCOMES:
        blocking.add("manifest_declared_outcome_invalid")

    historical = value.get("historical_bindings")
    if not _mapping_has_exact_fields(historical, _HISTORICAL_BINDING_FIELDS):
        blocking.add("historical_bindings_shape_invalid")
    else:
        expected_historical = {
            "source_baseline_commit_sha": SOURCE_BASELINE_SHA,
            "source_baseline_tree_sha": SOURCE_BASELINE_TREE_SHA,
            "e1_candidate_commit_sha": E1_CANDIDATE_SHA,
            "e1_candidate_tree_sha": E1_CANDIDATE_TREE_SHA,
            "e1_merge_commit_sha": E1_MERGE_SHA,
            "e1_merge_tree_sha": E1_MERGE_TREE_SHA,
            "e1_merge_parent_shas": [SOURCE_BASELINE_SHA, E1_CANDIDATE_SHA],
            "e1_pull_request_number": E1_PR_NUMBER,
            "e1_receipt_comment_id": E1_RECEIPT_COMMENT_ID,
            "e1_receipt_canonical_sha256": E1_EXTERNAL_RECEIPT_SHA256,
        }
        if dict(historical) != expected_historical:
            blocking.add("historical_bindings_mismatch")

    references = value.get("record_references")
    expected_references = {
        "candidate_changed_path_manifest": "examples/public-integration-pack-pilot/m15-release-proof-linkage-candidate-changed-paths.json",
        "merge_result_path_manifest": "examples/public-integration-pack-pilot/m15-release-proof-linkage-merge-result-paths.json",
        "candidate_to_merge_continuity_record": "examples/public-integration-pack-pilot/m15-release-proof-linkage-candidate-to-merge-continuity.json",
        "e1_external_receipt_linkage_record": "examples/public-integration-pack-pilot/m15-release-proof-linkage-e1-external-receipt.json",
        "release_boundary_register": "examples/public-integration-pack-pilot/m15-release-proof-linkage-release-boundaries.json",
    }
    if not _mapping_has_exact_fields(references, _RECORD_REFERENCE_FIELDS):
        blocking.add("record_references_shape_invalid")
    elif dict(references) != expected_references:
        blocking.add("record_references_mismatch")

    candidate = value.get("future_release_candidate")
    if not _mapping_has_exact_fields(candidate, _RELEASE_CANDIDATE_FIELDS):
        blocking.add("future_release_candidate_shape_invalid")
    elif dict(candidate) != {
        "identifier": FUTURE_RELEASE_CANDIDATE_IDENTIFIER,
        "state": FUTURE_RELEASE_CANDIDATE_STATE,
    }:
        blocking.add("future_release_candidate_binding_invalid")

    command_manifest = value.get("verification_command_manifest")
    if not _mapping_has_exact_fields(command_manifest, _COMMAND_MANIFEST_FIELDS):
        blocking.add("verification_command_manifest_shape_invalid")
        return
    if command_manifest.get("command_count") != len(EXPECTED_VERIFICATION_COMMANDS):
        readiness.add("verification_command_count_incomplete")
    if command_manifest.get("environment") != {"PYTHONDONTWRITEBYTECODE": "1"}:
        blocking.add("verification_environment_invalid")
    if command_manifest.get("execution_policy") != "declarative-external-execution-only":
        blocking.add("verification_execution_policy_invalid")
    if command_manifest.get("commands_executed_by_evaluator") is not False:
        blocking.add("verification_execution_claimed")
    commands = command_manifest.get("commands")
    if not isinstance(commands, list):
        blocking.add("verification_commands_invalid")
        return
    observed: dict[str, Mapping[str, Any]] = {}
    for index, command in enumerate(commands):
        if not _mapping_has_exact_fields(command, _COMMAND_FIELDS):
            blocking.add(f"verification_command_shape_invalid:{index}")
            continue
        command_id = command.get("command_id")
        if command_id not in EXPECTED_VERIFICATION_COMMANDS or command_id in observed:
            blocking.add(f"verification_command_identity_invalid:{index}")
            continue
        observed[command_id] = command
    for command_id in sorted(set(EXPECTED_VERIFICATION_COMMANDS) - set(observed)):
        readiness.add(f"verification_command_missing:{command_id}")
    if len(commands) != len(EXPECTED_VERIFICATION_COMMANDS):
        readiness.add("verification_command_coverage_incomplete")
    for command_id, command in observed.items():
        expected = EXPECTED_VERIFICATION_COMMANDS[command_id]
        for field in ("argv", "test_scope", "execution_scope"):
            if command.get(field) != expected[field]:
                readiness.add(f"verification_command_binding_invalid:{command_id}:{field}")
        if command.get("required") is not True or command.get("expected_exit_code") != 0:
            readiness.add(f"verification_command_requirement_invalid:{command_id}")
        if command.get("executed_by_evaluator") is not False:
            blocking.add(f"verification_command_execution_claim:{command_id}")


def _validate_candidate_manifest(
    value: Any,
    blocking: set[str],
    linkage_blockers: set[str],
) -> tuple[dict[str, Mapping[str, Any]], int]:
    if not _mapping_has_exact_fields(value, _CANDIDATE_MANIFEST_FIELDS):
        blocking.add("candidate_manifest_shape_invalid")
        linkage_blockers.add("incomplete-path-coverage")
        return {}, 0
    expected = {
        "schema_version": CANDIDATE_PATH_MANIFEST_SCHEMA_VERSION,
        "document_type": "candidate-changed-path-manifest",
        "record_id": "urn:aaos:m15:release-proof-linkage:e2:e1-candidate-paths",
        "issue": "#248",
        "source_baseline_commit_sha": SOURCE_BASELINE_SHA,
        "candidate_commit_sha": E1_CANDIDATE_SHA,
        "candidate_tree_sha": E1_CANDIDATE_TREE_SHA,
        "derivation": "git-diff-tree:source-baseline..candidate:rename-and-copy-detection",
        "changed_path_count": len(EXPECTED_PATHS),
        "change_type_counts": EXPECTED_CHANGE_TYPE_COUNTS,
        "generated_by_evaluator": False,
        "non_authoritative_boundary_statement": PATH_EVIDENCE_BOUNDARY_STATEMENT,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            blocking.add(f"candidate_manifest_binding_mismatch:{field}")
            linkage_blockers.add("candidate-merge-mismatch")
    paths = value.get("paths")
    if not isinstance(paths, list):
        blocking.add("candidate_paths_invalid")
        linkage_blockers.add("incomplete-path-coverage")
        return {}, 0
    observed: dict[str, Mapping[str, Any]] = {}
    for index, entry in enumerate(paths):
        if not _mapping_has_exact_fields(entry, _CANDIDATE_PATH_FIELDS):
            blocking.add(f"candidate_path_shape_invalid:{index}")
            continue
        path = entry.get("path")
        if path not in EXPECTED_PATHS or path in observed:
            blocking.add(f"candidate_path_identity_invalid:{index}")
            continue
        observed[path] = entry
    if set(observed) != set(EXPECTED_PATHS) or len(paths) != len(EXPECTED_PATHS):
        blocking.add("candidate_path_coverage_incomplete")
        linkage_blockers.add("incomplete-path-coverage")
    if [entry.get("path") for entry in paths if isinstance(entry, Mapping)] != sorted(
        EXPECTED_PATHS
    ):
        blocking.add("candidate_path_order_invalid")
    for path, entry in observed.items():
        expected_path = EXPECTED_PATHS[path]
        exact = {
            "path_id": expected_path["path_id"],
            "path": path,
            "previous_path": None,
            "change_type": "addition",
            "baseline_blob_sha": None,
            "candidate_blob_sha": expected_path["candidate_blob_sha"],
            "candidate_canonical_sha256": expected_path[
                "candidate_canonical_sha256"
            ],
            "candidate_file_mode": "100644",
            "artifact_role": expected_path["artifact_role"],
            "required_status": "required",
            "evidence_reference": f"urn:aaos:m15:e2:e1-candidate-path:{expected_path['path_id']}",
        }
        if dict(entry) != exact:
            blocking.add(f"candidate_path_binding_mismatch:{path}")
            linkage_blockers.add("candidate-merge-mismatch")
    return observed, len(observed)


def _validate_merge_manifest(
    value: Any,
    blocking: set[str],
    linkage_blockers: set[str],
) -> tuple[dict[str, Mapping[str, Any]], int]:
    if not _mapping_has_exact_fields(value, _MERGE_MANIFEST_FIELDS):
        blocking.add("merge_manifest_shape_invalid")
        linkage_blockers.add("incomplete-path-coverage")
        return {}, 0
    expected = {
        "schema_version": MERGE_PATH_MANIFEST_SCHEMA_VERSION,
        "document_type": "merge-result-path-manifest",
        "record_id": "urn:aaos:m15:release-proof-linkage:e2:e1-merge-paths",
        "issue": "#248",
        "candidate_commit_sha": E1_CANDIDATE_SHA,
        "merge_commit_sha": E1_MERGE_SHA,
        "merge_tree_sha": E1_MERGE_TREE_SHA,
        "candidate_changed_path_count": len(EXPECTED_PATHS),
        "observed_path_count": len(EXPECTED_PATHS),
        "generated_by_evaluator": False,
        "non_authoritative_boundary_statement": PATH_EVIDENCE_BOUNDARY_STATEMENT,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            blocking.add(f"merge_manifest_binding_mismatch:{field}")
            linkage_blockers.add("candidate-merge-mismatch")
    paths = value.get("paths")
    if not isinstance(paths, list):
        blocking.add("merge_paths_invalid")
        linkage_blockers.add("incomplete-path-coverage")
        return {}, 0
    observed: dict[str, Mapping[str, Any]] = {}
    for index, entry in enumerate(paths):
        if not _mapping_has_exact_fields(entry, _MERGE_PATH_FIELDS):
            blocking.add(f"merge_path_shape_invalid:{index}")
            continue
        path = entry.get("path")
        if path not in EXPECTED_PATHS or path in observed:
            blocking.add(f"merge_path_identity_invalid:{index}")
            continue
        observed[path] = entry
    if set(observed) != set(EXPECTED_PATHS) or len(paths) != len(EXPECTED_PATHS):
        blocking.add("merge_path_coverage_incomplete")
        linkage_blockers.add("incomplete-path-coverage")
    if [entry.get("path") for entry in paths if isinstance(entry, Mapping)] != sorted(
        EXPECTED_PATHS
    ):
        blocking.add("merge_path_order_invalid")
    for path, entry in observed.items():
        expected_path = EXPECTED_PATHS[path]
        exact = {
            "path_id": expected_path["path_id"],
            "path": path,
            "source_change_type": "addition",
            "merge_blob_sha": expected_path["candidate_blob_sha"],
            "merge_canonical_sha256": expected_path["candidate_canonical_sha256"],
            "merge_file_mode": "100644",
            "presence_state": "present",
            "continuity_status": "preserved",
            "continuity_evidence_reference": (
                f"urn:aaos:m15:e2:e1-merge-path:{expected_path['path_id']}"
            ),
        }
        if dict(entry) != exact:
            blocking.add(f"merge_path_binding_mismatch:{path}")
            linkage_blockers.add("candidate-merge-mismatch")
    return observed, len(observed)


def _validate_continuity_record(
    value: Any,
    blocking: set[str],
    linkage_blockers: set[str],
) -> str:
    if not _mapping_has_exact_fields(value, _CONTINUITY_FIELDS):
        blocking.add("continuity_record_shape_invalid")
        linkage_blockers.add("missing-continuity-evidence")
        return UNVERIFIED
    expected_scalars = {
        "schema_version": CONTINUITY_RECORD_SCHEMA_VERSION,
        "document_type": "candidate-to-merge-continuity-record",
        "record_id": "urn:aaos:m15:release-proof-linkage:e2:e1-continuity",
        "issue": "#248",
        "source_baseline_commit_sha": SOURCE_BASELINE_SHA,
        "source_baseline_tree_sha": SOURCE_BASELINE_TREE_SHA,
        "candidate_commit_sha": E1_CANDIDATE_SHA,
        "candidate_tree_sha": E1_CANDIDATE_TREE_SHA,
        "merge_commit_sha": E1_MERGE_SHA,
        "merge_tree_sha": E1_MERGE_TREE_SHA,
        "merge_parent_shas": [SOURCE_BASELINE_SHA, E1_CANDIDATE_SHA],
        "merge_parent_count": 2,
        "candidate_is_merge_parent": True,
        "source_baseline_is_merge_parent": True,
        "merge_parent_inclusion_verified": True,
        "complete_path_coverage": True,
        "preserved_path_count": len(EXPECTED_PATHS),
        "missing_paths": [],
        "blob_mismatches": [],
        "digest_mismatches": [],
        "file_mode_mismatches": [],
        "unexpected_substitutions": [],
        "additional_merge_difference_count": 0,
        "additional_merge_difference_explanations": [],
        "allowed_relations": list(CONTINUITY_RELATIONS),
        "continuity_relation": EXACT_TREE_MATCH,
        "evidence_reference": "git-object-observation:e1-candidate-to-merge",
        "generated_by_evaluator": False,
        "non_authoritative_boundary_statement": PATH_EVIDENCE_BOUNDARY_STATEMENT,
    }
    for field, expected in expected_scalars.items():
        if value.get(field) != expected:
            blocking.add(f"continuity_record_binding_mismatch:{field}")
            linkage_blockers.add("candidate-merge-mismatch")
    advancement = value.get("base_advancement")
    expected_advancement = {
        "present": False,
        "advanced_base_sha": None,
        "source_baseline_is_ancestor": True,
        "explanation": None,
        "evidence_reference": None,
    }
    if not _mapping_has_exact_fields(advancement, _BASE_ADVANCEMENT_FIELDS):
        blocking.add("base_advancement_shape_invalid")
    elif dict(advancement) != expected_advancement:
        blocking.add("base_advancement_binding_mismatch")
        linkage_blockers.add("candidate-merge-mismatch")
    return value.get("continuity_relation") if value.get(
        "continuity_relation"
    ) in CONTINUITY_RELATIONS else UNVERIFIED


def _validate_e1_receipt_linkage(
    value: Any,
    blocking: set[str],
    linkage_blockers: set[str],
) -> None:
    if not _mapping_has_exact_fields(value, _E1_RECEIPT_FIELDS):
        blocking.add("e1_receipt_linkage_shape_invalid")
        linkage_blockers.add("missing-receipt-binding")
        return
    expected = {
        "schema_version": E1_RECEIPT_LINKAGE_SCHEMA_VERSION,
        "document_type": "e1-external-receipt-linkage-record",
        "record_id": "urn:aaos:m15:release-proof-linkage:e2:e1-receipt",
        "issue": "#248",
        "source_pull_request_number": E1_PR_NUMBER,
        "source_comment_id": E1_RECEIPT_COMMENT_ID,
        "receipt_schema_version": E1_EXTERNAL_RECEIPT_SCHEMA_VERSION,
        "source_baseline_commit_sha": SOURCE_BASELINE_SHA,
        "candidate_commit_sha": E1_CANDIDATE_SHA,
        "command_count": E1_RECEIPT_COMMAND_COUNT,
        "canonical_receipt_json_sha256": E1_EXTERNAL_RECEIPT_SHA256,
        "receipt_present": True,
        "linkage_state": "bound",
        "external_to_e1_candidate": True,
        "caller_supplied_inert_evidence": True,
        "fetched_by_evaluator": False,
        "treated_as_merge_approval": False,
        "non_authoritative_boundary_statement": E1_RECEIPT_BOUNDARY_STATEMENT,
    }
    if dict(value) != expected:
        blocking.add("e1_receipt_linkage_mismatch")
        linkage_blockers.add("missing-receipt-binding")


def _validate_boundary_register(
    value: Any,
    blocking: set[str],
    linkage_blockers: set[str],
) -> list[str]:
    if not _mapping_has_exact_fields(value, _BOUNDARY_REGISTER_FIELDS):
        blocking.add("release_boundary_register_shape_invalid")
        linkage_blockers.add("missing-continuity-evidence")
        return list(REQUIRED_FUTURE_PREREQUISITES)
    expected_scalars = {
        "schema_version": RELEASE_BOUNDARY_REGISTER_SCHEMA_VERSION,
        "document_type": "release-blocker-and-prerequisite-register",
        "record_id": "urn:aaos:m15:release-proof-linkage:e2:release-boundaries",
        "issue": "#248",
        "parent_tracker": "#231",
        "e2_linkage_blocker_count": len(REQUIRED_LINKAGE_BLOCKERS),
        "future_release_prerequisite_count": len(REQUIRED_FUTURE_PREREQUISITES),
        "non_authoritative_boundary_statement": NON_AUTHORITATIVE_BOUNDARY_STATEMENT,
    }
    for field, expected in expected_scalars.items():
        if value.get(field) != expected:
            blocking.add(f"release_boundary_register_binding_mismatch:{field}")

    blocker_rows = value.get("e2_linkage_blockers")
    observed_blockers: dict[str, Mapping[str, Any]] = {}
    if not isinstance(blocker_rows, list):
        blocking.add("e2_linkage_blocker_register_invalid")
    else:
        for index, row in enumerate(blocker_rows):
            if not _mapping_has_exact_fields(row, _REGISTER_ENTRY_FIELDS):
                blocking.add(f"e2_linkage_blocker_shape_invalid:{index}")
                continue
            blocker_id = row.get("blocker_id")
            if blocker_id not in REQUIRED_LINKAGE_BLOCKERS or blocker_id in observed_blockers:
                blocking.add(f"e2_linkage_blocker_identity_invalid:{index}")
                continue
            observed_blockers[blocker_id] = row
        if set(observed_blockers) != set(REQUIRED_LINKAGE_BLOCKERS):
            blocking.add("e2_linkage_blocker_register_incomplete")
            linkage_blockers.add("missing-continuity-evidence")
        for blocker_id, row in observed_blockers.items():
            if row.get("state") != "resolved":
                blocking.add(f"e2_linkage_blocker_unresolved:{blocker_id}")
                linkage_blockers.add(blocker_id)
            if not _is_nonempty_string(row.get("evidence_reference")) or not _is_nonempty_string(
                row.get("notes")
            ):
                blocking.add(f"e2_linkage_blocker_evidence_invalid:{blocker_id}")

    prerequisite_rows = value.get("future_release_prerequisites")
    observed_prerequisites: dict[str, Mapping[str, Any]] = {}
    if not isinstance(prerequisite_rows, list):
        blocking.add("future_release_prerequisite_register_invalid")
    else:
        for index, row in enumerate(prerequisite_rows):
            if not _mapping_has_exact_fields(row, _PREREQUISITE_ENTRY_FIELDS):
                blocking.add(f"future_release_prerequisite_shape_invalid:{index}")
                continue
            prerequisite_id = row.get("prerequisite_id")
            if prerequisite_id not in REQUIRED_FUTURE_PREREQUISITES or prerequisite_id in observed_prerequisites:
                blocking.add(f"future_release_prerequisite_identity_invalid:{index}")
                continue
            observed_prerequisites[prerequisite_id] = row
        if set(observed_prerequisites) != set(REQUIRED_FUTURE_PREREQUISITES):
            blocking.add("future_release_prerequisite_register_incomplete")
        for prerequisite_id, row in observed_prerequisites.items():
            if row.get("state") != "open":
                blocking.add(f"future_release_prerequisite_state_invalid:{prerequisite_id}")
            if not _is_nonempty_string(row.get("evidence_reference")) or not _is_nonempty_string(
                row.get("notes")
            ):
                blocking.add(f"future_release_prerequisite_evidence_invalid:{prerequisite_id}")

    candidate = value.get("future_release_candidate")
    if not _mapping_has_exact_fields(candidate, _RELEASE_CANDIDATE_FIELDS) or dict(
        candidate
    ) != {
        "identifier": FUTURE_RELEASE_CANDIDATE_IDENTIFIER,
        "state": FUTURE_RELEASE_CANDIDATE_STATE,
    }:
        blocking.add("future_release_candidate_binding_invalid")

    governance = value.get("governance_boundary")
    if not _mapping_has_exact_fields(governance, _GOVERNANCE_FIELDS):
        blocking.add("governance_boundary_shape_invalid")
    else:
        expected_states = {
            "tracker_231_state": "open",
            "m15_state": "active-and-incomplete",
            "v0_14_0_tag_state": "not-authorized",
            "github_release_state": "not-created",
        }
        for field, expected in expected_states.items():
            if governance.get(field) != expected:
                blocking.add(f"governance_boundary_violation:{field}")
        for field in sorted(_GOVERNANCE_FIELDS - set(expected_states)):
            if governance.get(field) is not False:
                blocking.add(f"governance_authority_claim:{field}")
    return list(REQUIRED_FUTURE_PREREQUISITES)


def _validate_external_verification_receipt(
    value: Any,
    blocking: set[str],
    readiness: set[str],
) -> bool:
    if value is None:
        readiness.add("external_e2_verification_receipt_missing")
        return False
    receipt_blocking_before = set(blocking)
    if not _mapping_has_exact_fields(value, _VERIFICATION_RECEIPT_FIELDS):
        blocking.add("external_e2_verification_receipt_shape_invalid")
        return False
    expected_scalars = {
        "schema_version": VERIFICATION_RECEIPT_SCHEMA_VERSION,
        "document_type": "external-verification-execution-receipt",
        "repository": "aa-os/aaos-public",
        "issue_number": E2_ISSUE_NUMBER,
        "source_main_base_sha": STARTING_MAIN_SHA,
        "execution_subject_type": "pull-request-candidate-checkout",
        "external_to_candidate_commit": True,
        "executed_by_evaluator": False,
        "non_authoritative_boundary_statement": VERIFICATION_RECEIPT_BOUNDARY_STATEMENT,
    }
    for field, expected in expected_scalars.items():
        if value.get(field) != expected:
            blocking.add(f"external_e2_verification_receipt_mismatch:{field}")
    if not _is_nonnegative_integer(value.get("pull_request_number")) or value.get(
        "pull_request_number"
    ) < 1:
        blocking.add("external_e2_verification_receipt_pr_invalid")
    candidate_head = value.get("execution_candidate_head_sha")
    if not _is_object_sha(candidate_head) or candidate_head == STARTING_MAIN_SHA:
        blocking.add("external_e2_verification_receipt_candidate_invalid")
    expected_reference = (
        f"pull-request:#{value.get('pull_request_number')}"
        if _is_nonnegative_integer(value.get("pull_request_number"))
        else None
    )
    if value.get("execution_candidate_reference") != expected_reference:
        blocking.add("external_e2_verification_receipt_candidate_reference_invalid")
    if value.get("command_receipt_count") != len(EXPECTED_VERIFICATION_COMMANDS):
        blocking.add("external_e2_verification_receipt_command_count_invalid")
    commands = value.get("commands")
    if not isinstance(commands, list):
        blocking.add("external_e2_verification_receipt_commands_invalid")
        return False
    observed: dict[str, Mapping[str, Any]] = {}
    for index, command in enumerate(commands):
        if not _mapping_has_exact_fields(command, _VERIFICATION_COMMAND_RECEIPT_FIELDS):
            blocking.add(f"external_e2_verification_command_shape_invalid:{index}")
            continue
        command_id = command.get("command_id")
        if command_id not in EXPECTED_VERIFICATION_COMMANDS or command_id in observed:
            blocking.add(f"external_e2_verification_command_identity_invalid:{index}")
            continue
        observed[command_id] = command
    if set(observed) != set(EXPECTED_VERIFICATION_COMMANDS) or len(commands) != len(
        EXPECTED_VERIFICATION_COMMANDS
    ):
        blocking.add("external_e2_verification_command_coverage_incomplete")
    for command_id, command in observed.items():
        expected = EXPECTED_VERIFICATION_COMMANDS[command_id]
        if command.get("declared_logical_argv") != expected["argv"]:
            blocking.add(f"external_e2_verification_argv_mismatch:{command_id}")
        if command.get("execution_scope") != expected["execution_scope"]:
            blocking.add(f"external_e2_verification_scope_mismatch:{command_id}")
        if command.get("execution_candidate_head_sha") != candidate_head:
            blocking.add(f"external_e2_verification_candidate_mismatch:{command_id}")
        actual_argv = command.get("actual_argv")
        declared_argv = command.get("declared_logical_argv")
        if not isinstance(actual_argv, list) or not actual_argv or not all(
            _is_nonempty_string(item) for item in actual_argv
        ):
            blocking.add(f"external_e2_verification_actual_argv_invalid:{command_id}")
        elif isinstance(declared_argv, list) and actual_argv[1:] != declared_argv[1:]:
            blocking.add(f"external_e2_verification_actual_argv_mismatch:{command_id}")
        binding = command.get("executable_binding")
        if not _mapping_has_exact_fields(binding, _EXECUTABLE_BINDING_FIELDS):
            blocking.add(f"external_e2_verification_executable_binding_invalid:{command_id}")
        else:
            declared_launcher = binding.get("declared_launcher")
            actual_launcher = binding.get("actual_launcher")
            launchers_differ = declared_launcher != actual_launcher
            if declared_launcher != "python" or not _is_nonempty_string(actual_launcher):
                blocking.add(f"external_e2_verification_launcher_invalid:{command_id}")
            if not isinstance(declared_argv, list) or not declared_argv or declared_argv[0] != declared_launcher:
                blocking.add(f"external_e2_verification_declared_launcher_mismatch:{command_id}")
            if not isinstance(actual_argv, list) or not actual_argv or actual_argv[0] != actual_launcher:
                blocking.add(f"external_e2_verification_actual_launcher_mismatch:{command_id}")
            if binding.get("launcher_substitution_detected") is not launchers_differ:
                blocking.add(f"external_e2_verification_substitution_detection_invalid:{command_id}")
            if launchers_differ and binding.get("launcher_substitution_declared") is not True:
                blocking.add(f"external_e2_verification_substitution_undeclared:{command_id}")
            if binding.get("python_implementation") != "CPython":
                blocking.add(f"external_e2_verification_python_implementation_invalid:{command_id}")
            if not isinstance(binding.get("python_version"), str) or not _PYTHON_VERSION_RE.fullmatch(
                binding.get("python_version")
            ):
                blocking.add(f"external_e2_verification_python_version_invalid:{command_id}")
        for field in ("tests_observed", "passes", "failures", "errors", "skips"):
            if not _is_nonnegative_integer(command.get(field)):
                blocking.add(f"external_e2_verification_count_invalid:{command_id}:{field}")
        counts = [
            command.get(field)
            for field in ("passes", "failures", "errors", "skips")
        ]
        if all(_is_nonnegative_integer(item) for item in counts) and sum(counts) != command.get(
            "tests_observed"
        ):
            blocking.add(f"external_e2_verification_count_arithmetic_invalid:{command_id}")
        if command.get("failures"):
            blocking.add(f"external_e2_verification_failures_present:{command_id}")
        if command.get("errors"):
            blocking.add(f"external_e2_verification_errors_present:{command_id}")
        if command.get("skips"):
            readiness.add(f"external_e2_verification_skips_present:{command_id}")
        if command.get("exit_code") != 0:
            blocking.add(f"external_e2_verification_nonzero_exit:{command_id}")
        if not isinstance(command.get("execution_timestamp"), str) or not _RFC3339_RE.fullmatch(
            command.get("execution_timestamp")
        ):
            blocking.add(f"external_e2_verification_timestamp_invalid:{command_id}")
        if not _is_digest(command.get("transcript_sha256")):
            blocking.add(f"external_e2_verification_transcript_invalid:{command_id}")
        if not _is_nonempty_string(command.get("evidence_reference")):
            blocking.add(f"external_e2_verification_evidence_reference_invalid:{command_id}")
        if command.get("executed_by_evaluator") is not False:
            blocking.add(f"external_e2_verification_execution_claim:{command_id}")
        if command.get("verification_results_are_release_authority") is not False:
            blocking.add(f"external_e2_verification_release_authority_claim:{command_id}")
    return set(blocking) == receipt_blocking_before and len(observed) == len(
        EXPECTED_VERIFICATION_COMMANDS
    )


def evaluate_release_proof_linkage(
    manifest: Mapping[str, Any],
    candidate_path_manifest: Mapping[str, Any],
    merge_path_manifest: Mapping[str, Any],
    continuity_record: Mapping[str, Any],
    e1_receipt_linkage: Mapping[str, Any],
    release_boundary_register: Mapping[str, Any],
    external_verification_receipt: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Evaluate the complete caller-supplied E2 evidence package."""

    blocking: set[str] = set()
    readiness: set[str] = set()
    linkage_blockers: set[str] = set()
    _validate_manifest(manifest, blocking, readiness)
    candidate_paths, candidate_count = _validate_candidate_manifest(
        candidate_path_manifest, blocking, linkage_blockers
    )
    merge_paths, merge_count = _validate_merge_manifest(
        merge_path_manifest, blocking, linkage_blockers
    )
    relation = _validate_continuity_record(
        continuity_record, blocking, linkage_blockers
    )
    _validate_e1_receipt_linkage(e1_receipt_linkage, blocking, linkage_blockers)
    _validate_boundary_register(
        release_boundary_register, blocking, linkage_blockers
    )

    preserved = 0
    for path in sorted(set(candidate_paths) & set(merge_paths)):
        continuity = evaluate_path_continuity(candidate_paths[path], merge_paths[path])
        if continuity["continuity_status"] == "preserved":
            preserved += 1
        else:
            linkage_blockers.add("unexplained-digest-or-mode-drift")
            for finding in continuity["findings"]:
                blocking.add(f"path_continuity:{path}:{finding}")
    if set(candidate_paths) != set(merge_paths):
        blocking.add("candidate_merge_path_coverage_mismatch")
        linkage_blockers.add("incomplete-path-coverage")
    if relation == EXACT_TREE_MATCH:
        if E1_CANDIDATE_TREE_SHA != E1_MERGE_TREE_SHA or preserved != len(
            EXPECTED_PATHS
        ):
            blocking.add("exact_tree_match_not_supported_by_path_evidence")
            linkage_blockers.add("candidate-merge-mismatch")
    elif relation == CANDIDATE_CHANGE_SET_PRESERVED:
        if preserved != len(EXPECTED_PATHS):
            blocking.add("candidate_change_set_not_fully_preserved")
            linkage_blockers.add("candidate-merge-mismatch")
    elif relation == DRIFT_DETECTED:
        blocking.add("continuity_drift_detected")
        linkage_blockers.add("candidate-merge-mismatch")
    elif relation == UNVERIFIED:
        readiness.add("continuity_unverified")
        linkage_blockers.add("missing-continuity-evidence")

    receipt_validated = _validate_external_verification_receipt(
        external_verification_receipt, blocking, readiness
    )
    if not blocking and not readiness:
        if manifest.get("declared_continuity_relation") != relation:
            blocking.add("manifest_continuity_relation_mismatch")
            linkage_blockers.add("candidate-merge-mismatch")
        if manifest.get("declared_outcome") != RELEASE_PROOF_LINKED:
            readiness.add("manifest_does_not_declare_release_proof_linked")
    return _result(
        blocking,
        readiness,
        linkage_blockers,
        continuity_relation=relation,
        candidate_path_count=candidate_count,
        merge_path_count=merge_count,
        preserved_path_count=preserved,
        external_verification_receipt_validated=receipt_validated,
    )


def evaluate_synthetic_scenario(document: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate one complete inert standalone E2 synthetic scenario."""

    blocking: set[str] = set()
    readiness: set[str] = set()
    linkage_blockers: set[str] = set()
    if not _mapping_has_exact_fields(document, _SCENARIO_FIELDS):
        blocking.add("scenario_shape_invalid")
        return _result(blocking, readiness, linkage_blockers)
    if document.get("schema_version") != SCENARIO_SCHEMA_VERSION:
        blocking.add("scenario_schema_version_invalid")
    if document.get("document_type") != "synthetic-scenario":
        blocking.add("scenario_document_type_invalid")
    if document.get("synthetic") is not True:
        blocking.add("scenario_synthetic_boundary_invalid")
    scenario_id = document.get("scenario_id")
    if scenario_id not in EXPECTED_SCENARIO_TITLES:
        blocking.add("scenario_id_invalid")
    if document.get("title") != EXPECTED_SCENARIO_TITLES.get(scenario_id):
        blocking.add("scenario_title_invalid")
    if document.get("expected_outcome") not in OUTCOMES:
        blocking.add("scenario_expected_outcome_invalid")
    if document.get("expected_relation") not in CONTINUITY_RELATIONS:
        blocking.add("scenario_expected_relation_invalid")
    if document.get("notes") != SCENARIO_BOUNDARY_STATEMENT:
        blocking.add("scenario_boundary_invalid")
    state = document.get("evidence_state")
    if not _mapping_has_exact_fields(state, _SCENARIO_STATE_FIELDS):
        blocking.add("scenario_evidence_state_shape_invalid")
        return _result(blocking, readiness, linkage_blockers)

    boolean_fields = _SCENARIO_STATE_FIELDS - {
        "unresolved_linkage_blocker_count",
        "release_candidate_state",
        "github_release_state",
        "tracker_231_state",
        "m15_state",
        "change_type",
    }
    for field in sorted(boolean_fields):
        if not _is_bool(state.get(field)):
            blocking.add(f"scenario_boolean_invalid:{field}")
    if not _is_nonnegative_integer(state.get("unresolved_linkage_blocker_count")):
        blocking.add("scenario_unresolved_linkage_blocker_count_invalid")

    required_checks = {
        "historical_bindings_present": "missing-continuity-evidence",
        "candidate_head_binding_valid": "candidate-merge-mismatch",
        "candidate_tree_binding_valid": "candidate-merge-mismatch",
        "merge_commit_binding_valid": "candidate-merge-mismatch",
        "merge_tree_present": "missing-continuity-evidence",
        "merge_parent_binding_valid": "candidate-merge-mismatch",
        "candidate_manifest_complete": "incomplete-path-coverage",
        "merge_manifest_complete": "incomplete-path-coverage",
        "required_candidate_paths_present_after_merge": "incomplete-path-coverage",
        "blob_continuity_valid": "unexplained-digest-or-mode-drift",
        "canonical_digest_continuity_valid": "unexplained-digest-or-mode-drift",
        "file_mode_continuity_valid": "unexplained-digest-or-mode-drift",
        "unexpected_path_substitution_absent": "candidate-merge-mismatch",
        "e1_receipt_present": "missing-receipt-binding",
        "e1_receipt_digest_valid": "missing-receipt-binding",
        "e1_receipt_candidate_binding_valid": "missing-receipt-binding",
        "e1_receipt_baseline_binding_valid": "missing-receipt-binding",
        "linkage_blocker_register_complete": "missing-continuity-evidence",
        "future_release_prerequisites_visible": "missing-continuity-evidence",
    }
    for field, blocker_id in required_checks.items():
        if state.get(field) is False:
            blocking.add(f"scenario_required_check_failed:{field}")
            linkage_blockers.add(blocker_id)
    if _is_nonnegative_integer(state.get("unresolved_linkage_blocker_count")) and state.get(
        "unresolved_linkage_blocker_count"
    ):
        blocking.add("scenario_unresolved_linkage_blocker_present")
        linkage_blockers.add("missing-continuity-evidence")

    for field in (
        "e1_receipt_treated_as_merge_approval",
        "provenance_treated_as_human_approval",
        "operational_readiness_treated_as_completion_approval",
        "merge_commit_treated_as_published_release",
        "readme_completion_authorized",
        "unverified_continuity_treated_as_linked",
        "decision_proof_sealing_claimed",
        "learning_proof_sealing_claimed",
    ):
        if state.get(field) is True:
            blocking.add(f"scenario_authority_boundary_violation:{field}")
    if state.get("release_candidate_identifier_present") is not True:
        blocking.add("scenario_future_release_candidate_identifier_missing")
    if state.get("release_candidate_state") != FUTURE_RELEASE_CANDIDATE_STATE:
        blocking.add("scenario_future_release_candidate_state_invalid")
    if state.get("github_release_state") != "not-created":
        blocking.add("scenario_github_release_state_invalid")
    if state.get("tracker_231_state") != "open":
        blocking.add("scenario_tracker_231_state_invalid")
    if state.get("m15_state") != "active-and-incomplete":
        blocking.add("scenario_m15_state_invalid")
    if state.get("external_e2_verification_receipt_present") is False:
        readiness.add("scenario_external_e2_verification_receipt_missing")
    if state.get("external_e2_verification_receipt_consistent") is False:
        blocking.add("scenario_external_e2_verification_receipt_inconsistent")
    if state.get("change_type") not in {
        "addition",
        "modification",
        "rename",
        "deletion",
        "mixed",
    }:
        blocking.add("scenario_change_type_invalid")

    relation = UNVERIFIED
    if state.get("continuity_verified") is not True:
        if state.get("unverified_continuity_treated_as_linked") is not True:
            readiness.add("scenario_continuity_unverified")
    elif state.get("candidate_and_merge_trees_equal") is True:
        relation = EXACT_TREE_MATCH
    elif (
        state.get("candidate_change_set_preserved") is True
        and state.get("additional_merge_differences_explained") is True
    ):
        relation = CANDIDATE_CHANGE_SET_PRESERVED
    else:
        relation = DRIFT_DETECTED
        blocking.add("scenario_continuity_drift_detected")
        linkage_blockers.add("candidate-merge-mismatch")
    return _result(
        blocking,
        readiness,
        linkage_blockers,
        continuity_relation=relation,
    )


__all__ = [
    "BLOCKED",
    "CANDIDATE_CHANGE_SET_PRESERVED",
    "CANDIDATE_PATH_MANIFEST_SCHEMA_VERSION",
    "CONTINUITY_RECORD_SCHEMA_VERSION",
    "CONTINUITY_RELATIONS",
    "DRIFT_DETECTED",
    "E1_CANDIDATE_SHA",
    "E1_CANDIDATE_TREE_SHA",
    "E1_EXTERNAL_RECEIPT_SHA256",
    "E1_MERGE_SHA",
    "E1_MERGE_TREE_SHA",
    "E1_RECEIPT_LINKAGE_SCHEMA_VERSION",
    "EXACT_TREE_MATCH",
    "EXPECTED_PATHS",
    "EXPECTED_SCENARIO_TITLES",
    "EXPECTED_VERIFICATION_COMMANDS",
    "FUTURE_RELEASE_CANDIDATE_IDENTIFIER",
    "FUTURE_RELEASE_CANDIDATE_STATE",
    "MANIFEST_SCHEMA_VERSION",
    "MERGE_PATH_MANIFEST_SCHEMA_VERSION",
    "NON_AUTHORITATIVE_BOUNDARY_STATEMENT",
    "NOT_READY",
    "OUTCOMES",
    "PATH_EVIDENCE_BOUNDARY_STATEMENT",
    "RELEASE_BOUNDARY_REGISTER_SCHEMA_VERSION",
    "RELEASE_PROOF_LINKED",
    "REQUIRED_FUTURE_PREREQUISITES",
    "REQUIRED_LINKAGE_BLOCKERS",
    "RESULT_SCHEMA_VERSION",
    "SCENARIO_BOUNDARY_STATEMENT",
    "SCENARIO_SCHEMA_VERSION",
    "SOURCE_BASELINE_SHA",
    "SOURCE_BASELINE_TREE_SHA",
    "STARTING_MAIN_SHA",
    "STARTING_MAIN_TREE_SHA",
    "UNVERIFIED",
    "VERIFICATION_RECEIPT_BOUNDARY_STATEMENT",
    "VERIFICATION_RECEIPT_SCHEMA_VERSION",
    "evaluate_path_continuity",
    "evaluate_release_proof_linkage",
    "evaluate_synthetic_scenario",
]
