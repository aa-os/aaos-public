"""Deterministic caller-data-only evaluator for M15 Track E4.

The evaluator consumes exactly eleven inert caller mappings.  It performs no
file, Git, GitHub, network, process, command, digest, or external-state
operation.  Its ready outcome is evidence for a human-reviewed merge only; it
is neither human approval nor release-publication authority.
"""

from collections.abc import Mapping, Sequence
from typing import Any


MANIFEST_SCHEMA_VERSION = "m15-final-completion/v1"
TRACK_EVIDENCE_SCHEMA_VERSION = "m15-final-completion-track-evidence/v1"
E3_CONTINUITY_SCHEMA_VERSION = "m15-final-completion-e3-continuity/v1"
E3_EXTERNAL_EVIDENCE_SCHEMA_VERSION = (
    "m15-final-completion-e3-external-evidence/v1"
)
ACCEPTANCE_MATRIX_SCHEMA_VERSION = "m15-final-completion-acceptance-matrix/v1"
TRANSITION_REGISTER_SCHEMA_VERSION = "m15-final-completion-transition-register/v1"
README_TRANSITION_SCHEMA_VERSION = "m15-final-completion-readme-transition/v1"
RELEASE_PREPARATION_SCHEMA_VERSION = "m15-final-completion-release-preparation/v1"
PR_OBSERVATION_SCHEMA_VERSION = "m15-final-completion-pr-observation/v1"
VERIFICATION_RECEIPT_SCHEMA_VERSION = "m15-final-completion-verification-receipt/v1"
HUMAN_APPROVAL_SCHEMA_VERSION = "m15-final-completion-human-approval/v1"
SCENARIO_SCHEMA_VERSION = "m15-final-completion-scenario/v1"
RESULT_SCHEMA_VERSION = "m15-final-completion-result/v1"

READY = "ready_for_human_m15_completion_transition"
NOT_READY = "not_ready"
BLOCKED = "blocked"
OUTCOMES = (READY, NOT_READY, BLOCKED)

REPOSITORY = "aa-os/aaos-public"
SOURCE_ISSUE = 252
PARENT_TRACKER = 231
E4_PULL_REQUEST_NUMBER = 253
E4_PR_OBSERVATION_EVIDENCE_REFERENCE = (
    "github:aa-os/aaos-public:pull/253:commit-external-observation"
)
E4_VERIFICATION_RECEIPT_EVIDENCE_REFERENCE = (
    "github:aa-os/aaos-public:pull/253:external-verification-receipt"
)
SOURCE_MAIN_BASE_SHA = "52ec76c17cd21ec519dfec45ced4ad720b82d80e"
SOURCE_MAIN_BASE_TREE_SHA = "97b239cbd175aac01b05a1fba2394b72c47a5360"

E3_SOURCE_ISSUE = 250
E3_PULL_REQUEST_NUMBER = 251
E3_SOURCE_MAIN_BASE_SHA = "f6d074fca2fedecbf654697719179440bc0680d3"
E3_SOURCE_MAIN_BASE_TREE_SHA = "f13913426545b77616128223cd195487a415ffde"
E3_CANDIDATE_SHA = "907d2361233c7b0405a41271d7b02fa6c1a0c62d"
E3_CANDIDATE_TREE_SHA = "97b239cbd175aac01b05a1fba2394b72c47a5360"
E3_MERGE_SHA = SOURCE_MAIN_BASE_SHA
E3_MERGE_TREE_SHA = SOURCE_MAIN_BASE_TREE_SHA
E3_MERGE_PARENTS = (E3_SOURCE_MAIN_BASE_SHA, E3_CANDIDATE_SHA)
E3_RELATION = "exact_tree_match"
E3_ACTIVE_OBSERVATION_COMMENT_ID = 5017872695
E3_ACTIVE_RECEIPT_COMMENT_ID = 5017894934
E3_ACTIVE_RECEIPT_SHA256 = (
    "660ffddc0644bbb6e11689ceaf77b5c47b4061241a04cba233f2607287e30cb4"
)
E3_SUPERSEDED_OBSERVATION_COMMENT_ID = 5016298363
E3_SUPERSEDED_RECEIPT_COMMENT_ID = 5016356607
SUPERSEDED_CLASSIFICATION = "superseded-historical-evidence"

PRIOR_MATERIAL_ARTIFACT_COUNT = 209
TRACK_COUNTS = {
    "track-a": 7,
    "track-b": 13,
    "track-c": 18,
    "track-d": 29,
    "track-e1": 39,
    "track-e2": 50,
    "track-e3": 53,
}
REQUIRED_TRACK_IDS = tuple(TRACK_COUNTS)

AUTHORITY_BOUNDARY = (
    "Track E4 evidence is non-authoritative. Only an explicitly approved "
    "human-reviewed merge of the exact frozen candidate may perform the M15 "
    "repository completion transition. Tag and GitHub Release publication "
    "remain separate human-controlled post-merge actions. Decision Proof "
    "sealing and Learning Proof sealing remain AAOS-owned; no evaluator may "
    "accept risk, close an audit, grant a waiver, or transfer authority."
)
HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY = (
    "Completion readiness is evidence for final human review only; it is not "
    "M15 completion, tracker #231 closure, README final-state authorization, "
    "release approval, tag authorization, GitHub Release authorization, "
    "Decision Proof sealing, Learning Proof sealing, deployment authorization, "
    "risk acceptance, rollback execution, deletion execution, fail-closed "
    "execution, audit closure, waiver, authority transfer, or final governance "
    "judgment."
)
RUNTIME_BOUNDARY = (
    "The Track E4 runtime evaluator accepts caller-supplied inert mappings "
    "only and performs no file, Git, GitHub, network, subprocess, command, "
    "digest, merge, issue-closure, tag, release, or external-state operation."
)
HUMAN_APPROVAL_AUTHORITY_SCOPE = (
    "Approve merging only the exact reviewed E4 candidate and the linked "
    "repository M15 completion transition, including closure of #252 and #231; "
    "this does not authorize tag creation, GitHub Release publication, risk "
    "acceptance, audit closure, waiver, Decision Proof sealing, Learning Proof "
    "sealing, or authority transfer."
)
NON_AUTHORITATIVE_RELEASE_BOUNDARY = (
    "Human approval of the E4 repository transition does not authorize or "
    "perform v0.14.0 tag creation or GitHub Release publication."
)
PR_OBSERVATION_BOUNDARY = (
    "This commit-external observation records the frozen E4 candidate only; "
    "it is not human approval, merge authority, completion authority, tag "
    "authority, or GitHub Release authority."
)
VERIFICATION_BOUNDARY = (
    "Verification results are non-authoritative evidence only and do not "
    "approve M15 completion, a merge, tag creation, or GitHub Release publication."
)

REQUIRED_BLOCKERS = (
    "malformed-e3-continuity-evidence",
    "e3-candidate-merge-identity-mismatch",
    "e3-merge-tree-mismatch",
    "e3-merge-parent-mismatch",
    "e3-artifact-drift",
    "superseded-e3-observation-used",
    "superseded-e3-receipt-used",
    "active-e3-receipt-digest-mismatch",
    "track-a-e3-evidence-substitution",
    "omitted-acceptance-criterion",
    "substituted-acceptance-evidence",
    "hidden-completion-blocker",
    "readme-final-transition-drift",
    "premature-tracker-closure-claim",
    "premature-issue-closure-claim",
    "premature-m15-complete-claim",
    "premature-tag-created-claim",
    "premature-github-release-published-claim",
    "candidate-head-as-final-tag-target",
    "verification-observation-candidate-mismatch",
    "human-approval-candidate-mismatch",
    "human-approval-receipt-mismatch",
    "evaluator-output-as-human-approval",
    "historical-evidence-rebaseline",
    "mutable-main-source-base-pinning",
    "unapproved-compatibility-repair",
    "insufficient-verification-coverage",
    "completion-publication-conflation",
    "proof-sealing-claim",
    "authority-transfer-claim",
    "runtime-boundary-violation",
)
REQUIRED_READINESS_FINDINGS = (
    "missing-final-pr-observation",
    "missing-final-verification-receipt",
    "incomplete-test-execution",
    "missing-readme-transition-observation",
    "missing-release-target-preparation",
    "missing-release-notes",
    "missing-publication-checklist",
    "missing-human-approval",
    "missing-approval-timestamp",
    "missing-approval-receipt-binding",
    "missing-approval-candidate-binding",
)

EXPECTED_VERIFICATION_COMMANDS = (
    ("e4-targeted", ("python", "-X", "faulthandler", "-m", "unittest", "tests.test_m15_final_completion_evaluator", "-v"), "e4-candidate-validation", 183),
    ("e3-targeted", ("python", "-X", "faulthandler", "-m", "unittest", "tests.test_m15_completion_readiness_evaluator", "-v"), "inherited-regression", 167),
    ("e2-targeted", ("python", "-X", "faulthandler", "-m", "unittest", "tests.test_m15_release_proof_linkage_evaluator", "-v"), "inherited-regression", 140),
    ("e1-targeted", ("python", "-X", "faulthandler", "-m", "unittest", "tests.test_m15_operational_readiness_evaluator", "-v"), "inherited-regression", 132),
    ("track-a", ("python", "-X", "faulthandler", "-m", "unittest", "tests.test_m15_learning_proof_evaluator", "-v"), "inherited-regression", 68),
    ("track-b", ("python", "-X", "faulthandler", "-m", "unittest", "tests.test_m15_capability_memory_pack_evaluator", "-v"), "inherited-regression", 73),
    ("track-c", ("python", "-X", "faulthandler", "-m", "unittest", "tests.test_m15_lineage_rollback_portability_evaluator", "-v"), "inherited-regression", 181),
    ("track-d", ("python", "-X", "faulthandler", "-m", "unittest", "tests.test_m15_cross_control_regression_evaluator", "-v"), "inherited-regression", 79),
    ("m14-public-output", ("python", "-X", "faulthandler", "-m", "unittest", "tests.test_public_issue_exfiltration_gate_evaluator", "-v"), "inherited-regression", 23),
    ("m14-provenance", ("python", "-X", "faulthandler", "-m", "unittest", "tests.test_ai_authored_pr_provenance_evaluator", "-v"), "inherited-regression", 47),
    ("m14-skill-admission", ("python", "-X", "faulthandler", "-m", "unittest", "tests.test_skill_admission_evaluator", "-v"), "inherited-regression", 135),
    ("external-evidence-admission", ("python", "-X", "faulthandler", "-m", "unittest", "tests.test_external_evidence_admission_evaluator", "-v"), "inherited-regression", 31),
    ("m14-cross-control-authority", ("python", "-X", "faulthandler", "-m", "unittest", "tests.test_m14_cross_control_authority_boundary_evaluator", "-v"), "inherited-regression", 107),
    ("decision-proof-ownership", ("python", "-X", "faulthandler", "-m", "unittest", "tests.test_m15_learning_proof_evaluator.M15LearningProofEvaluatorTests.test_22_decision_proof_cannot_automatically_become_memory", "tests.test_m15_learning_proof_evaluator.M15LearningProofEvaluatorTests.test_23_decision_proof_reference_is_linkage_only_not_memory_authority", "tests.test_m15_capability_memory_pack_evaluator.M15CapabilityMemoryPackEvaluatorTests.test_38_learning_proof_linkage_cannot_be_used_as_authority", "tests.test_m15_capability_memory_pack_evaluator.M15CapabilityMemoryPackEvaluatorTests.test_39_decision_proof_linkage_cannot_grant_execution_authority", "tests.test_m15_lineage_rollback_portability_evaluator.M15TrackCCrossTrackLinkageTests", "tests.test_m15_cross_control_regression_evaluator.DecisionProofOwnershipTests", "-v"), "inherited-regression", 30),
    ("release-m15-status", ("python", "-X", "faulthandler", "-m", "unittest", "tests.test_m15_lineage_rollback_portability_evaluator.M15TrackCReleaseStateTests", "tests.test_m15_cross_control_regression_evaluator.TrackDContractTests.test_matrix_preserves_release_state", "tests.test_m15_cross_control_regression_evaluator.ReleaseM15StatusTests", "-v"), "inherited-regression", 18),
    ("m14-final-completion", ("python", "-X", "faulthandler", "-m", "unittest", "tests.test_m14_final_completion_evaluator", "-v"), "authorized-compatibility-regression", 110),
    ("m14-completion-readiness", ("python", "-X", "faulthandler", "-m", "unittest", "tests.test_m14_completion_readiness_evaluator", "-v"), "authorized-compatibility-regression", 112),
    ("full-maintained-suite", ("python", "-X", "faulthandler", "-m", "unittest", "discover", "-s", "tests", "-v"), "candidate-full-suite-integration", 2275),
)
COMMAND_IDS = tuple(row[0] for row in EXPECTED_VERIFICATION_COMMANDS)
COMMAND_MINIMA = {row[0]: row[3] for row in EXPECTED_VERIFICATION_COMMANDS}

COMPATIBILITY_REPAIR_BINDING_FIELDS = (
    "path",
    "purpose",
    "counted_in_prior_track_artifact_inventory",
    "human_authorized_bounded_exception",
    "historical_source_commit_sha",
    "historical_git_blob_sha",
    "historical_canonical_sha256",
    "historical_evidence_role",
    "prior_compatibility_commit_sha",
    "prior_compatibility_git_blob_sha",
    "prior_compatibility_canonical_sha256",
    "prior_compatibility_evidence_role",
    "e4_candidate_git_blob_sha",
    "e4_candidate_canonical_sha256",
    "e4_evidence_role",
    "authority_basis",
)
EXPECTED_AUTHORIZED_COMPATIBILITY_REPAIRS = (
    (
        "runtime/m14_final_completion_evaluator.py",
        "phase-aware-later-milestone-readme-validation",
        False,
        True,
        "06d1a3f64eaebf2ccb1667ebe4b3c85351bfd186",
        "d7a166c00bec4c5ca250c5ea9bf61a1576cc4fe6",
        "0fac7efcaed7a747520e2cc32072223ee5630e90fb11b256b5980a644ace35f6",
        "m14-final-historical-artifact",
        "b1e51b0f750e3a2c8d64c5bf8a89bbca4d460fba",
        "341807d4a2d433c51701e5b5094e03f4eb12b25b",
        "e5a9925c35196d13dd32444786a86fcd975192bc4f379aa0333ec3d8e30acc99",
        "e3-authorized-phase-aware-compatibility-repair",
        "d4b63b53606d9e179135a5ad94abbe9826e1b532",
        "0e4d9398971778256b746e2cca97d1e83ee203c33cb6f2faca8bbbe1200b7f27",
        "e4-authorized-phase-aware-compatibility-repair",
        "human-approved-bounded-scope-exception-for-issue-252",
    ),
    (
        "tests/test_m14_final_completion_evaluator.py",
        "explicit-historical-m14-final-mutation-validation",
        False,
        True,
        "06d1a3f64eaebf2ccb1667ebe4b3c85351bfd186",
        "c6459aac3f04a0633618035d3a53bf0b18b65e3a",
        "70ea270bdd4c742439f8e916f435fd1a6e9526c8b9c75507c099d6171f980175",
        "m14-final-historical-test-artifact",
        "b1e51b0f750e3a2c8d64c5bf8a89bbca4d460fba",
        "d2c48597d3ac76aee6ee910ea530faea0010af9d",
        "b002cdc5d0bd40baa74fc977293a9c1706ea21f6de7df02f46099dea4d708551",
        "e3-authorized-phase-aware-compatibility-repair",
        "7b3eee18a0e05f6a1ee2312668c9ab4d6f0e73dc",
        "d70883730d37812705cf1dcd1d2c4dcc20a9080d25c3ae2413858b8afdd79756",
        "e4-authorized-phase-aware-compatibility-repair",
        "human-approved-bounded-scope-exception-for-issue-252",
    ),
    (
        "tests/test_m14_completion_readiness_evaluator.py",
        "immutable-m14-readiness-snapshot-validation",
        False,
        True,
        "a7b5cbc2026468dde3d937e9366a780894570548",
        "367361f28659e7d304b20fdcfa0922a3ac5b1d52",
        "7aec68924201a6facb5d9248c065346e774b49cf6377161d8c2c0931df30c7ed",
        "m14-readiness-historical-test-artifact",
        "c97dfe7ddf3e04ac7a46726414a3523ed14e966b",
        "f806df39fb82649978a0674c09cc92f83d0983f5",
        "6faf721f987379bc5220e022017f9a3a3c91555a58264de6c0a36ff8a8241b1b",
        "m14-post-release-authorized-compatibility-repair",
        "c95b44408e0b8b5a5e69d468ae402e7262fad52e",
        "19211655db6a9f8853a81b93d4b45211aeeb9c1b4a41eba82e33e26bbe86c050",
        "e4-authorized-phase-aware-compatibility-repair",
        "human-approved-bounded-scope-exception-for-issue-252",
    ),
    (
        "tests/test_m15_completion_readiness_evaluator.py",
        "immutable-e3-completion-readiness-snapshot-validation",
        False,
        True,
        "52ec76c17cd21ec519dfec45ced4ad720b82d80e",
        "0f36dd1e5378466ce051df38f1cb463e860175fe",
        "f0ff78e0fabe8bcaa856e2c3258e30e6dc372964eed19063e71491e4444d4363",
        "e3-completion-readiness-historical-test-artifact",
        None,
        None,
        None,
        None,
        "2a8402f47ab8dd233f71a1e47ae494acdd7912d1",
        "6eda49b40e60e4b5ca6eb35ceb6d245377c32de6e4a07b08f843c66a6edcb14a",
        "e4-authorized-phase-aware-compatibility-repair",
        "human-approved-bounded-scope-exception-for-issue-252",
    ),
    (
        "tests/test_m15_lineage_rollback_portability_evaluator.py",
        "section-aware-e4-release-state-candidate-validation",
        False,
        True,
        "2d8bab3a84675543c34231a9e04521379febdac1",
        "ef2e87f272e176579a23eb7d5448ed13627cebb4",
        "5268f73a441898467e9b8f9471cfc4b9bd4fa27b7b67444fbf852d697d90f4c9",
        "track-c-historical-test-artifact",
        "b1e51b0f750e3a2c8d64c5bf8a89bbca4d460fba",
        "0309453f29e093ea942a6965b32bd8dad7f69d55",
        "0dee39fe81189fd558f136732579995245828bc6b14c9791b67c9bb6e8a39f5c",
        "e3-authorized-phase-aware-compatibility-repair",
        "437348e8a9bfd8340aa95b14601b1d021a1af94c",
        "9e3b455cc91c1b3fc114abd3b0de4682c7bbeaa93cae3511dc21e3bafd291e68",
        "e4-authorized-phase-aware-compatibility-repair",
        "human-approved-bounded-scope-exception-for-issue-252",
    ),
)

ARTIFACT_BINDING_FIELDS = (
    "track_id", "source_issue", "implementation_pr", "candidate_sha",
    "merge_sha", "repository_path", "artifact_type", "git_blob_sha",
    "git_file_mode", "canonical_text_sha256", "covering_test",
    "lifecycle_state", "evidence_reference", "authority_boundary",
    "evidence_role",
)

# Immutable 209-row table emitted from the maintained Git-derived inventory.
_EXPECTED_ARTIFACT_BINDINGS_EXACT: tuple[tuple[Any, ...], ...] = ()

_EXPECTED_ARTIFACT_BINDINGS_EXACT += (
    ('track-a', 232, 233, '603a26890ceee940b0a3c9009e06d994f9f2f342', '6e0fa4e8fdf4a672581cd897d52743d0462f0d4b', 'docs/learning-governance/m15-core-learning-proof-contract.md', 'governance-contract', '47cd884ba77c616d2660bb3e6693b51ea6b35509', '100644', 'b28de6f87b675e96db229a71dd0b34d54e5e065fd0f9205cb56b3018fddacae3', 'tests/test_m15_learning_proof_evaluator.py', 'maintained', 'git-object:6e0fa4e8fdf4a672581cd897d52743d0462f0d4b:docs/learning-governance/m15-core-learning-proof-contract.md', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-a', 232, 233, '603a26890ceee940b0a3c9009e06d994f9f2f342', '6e0fa4e8fdf4a672581cd897d52743d0462f0d4b', 'examples/public-integration-pack-pilot/m15-learning-proof-approved-evaluation-only.json', 'synthetic-fixture', '737559accedb9dc44326236f65d5142f43b3c95a', '100644', '56209ec5b821dab72f23e02b9472de8323353d706e60ec431e147c2208316db0', 'tests/test_m15_learning_proof_evaluator.py', 'maintained', 'git-object:6e0fa4e8fdf4a672581cd897d52743d0462f0d4b:examples/public-integration-pack-pilot/m15-learning-proof-approved-evaluation-only.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-a', 232, 233, '603a26890ceee940b0a3c9009e06d994f9f2f342', '6e0fa4e8fdf4a672581cd897d52743d0462f0d4b', 'examples/public-integration-pack-pilot/m15-learning-proof-contaminated-quarantine.json', 'synthetic-fixture', '6826200cab0a40c33f6bde642f5553f9a11e58ca', '100644', '8d1d1d46bfca7d4110978e17e7139041305b068979ee62cea939291138e91971', 'tests/test_m15_learning_proof_evaluator.py', 'maintained', 'git-object:6e0fa4e8fdf4a672581cd897d52743d0462f0d4b:examples/public-integration-pack-pilot/m15-learning-proof-contaminated-quarantine.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-a', 232, 233, '603a26890ceee940b0a3c9009e06d994f9f2f342', '6e0fa4e8fdf4a672581cd897d52743d0462f0d4b', 'examples/public-integration-pack-pilot/m15-learning-proof-rejected-untrusted-correction.json', 'synthetic-fixture', 'd765bf30d4a89e46c717bed179f7a5f85a70dc03', '100644', 'bf4c915b14fd968e5f50dc8b10b70edc9a56db54a13120891b9a7fedf9203ba8', 'tests/test_m15_learning_proof_evaluator.py', 'maintained', 'git-object:6e0fa4e8fdf4a672581cd897d52743d0462f0d4b:examples/public-integration-pack-pilot/m15-learning-proof-rejected-untrusted-correction.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-a', 232, 233, '603a26890ceee940b0a3c9009e06d994f9f2f342', '6e0fa4e8fdf4a672581cd897d52743d0462f0d4b', 'runtime/m15_learning_proof_evaluator.py', 'runtime-evaluator', 'fc499debd33c5c1e6eade831d84d54137e670be3', '100644', '1f0d1eda01e3df92fba069ffd75eff34232c7bfe39f0b252b80cae2d1a2f00c8', 'tests/test_m15_learning_proof_evaluator.py', 'maintained', 'git-object:6e0fa4e8fdf4a672581cd897d52743d0462f0d4b:runtime/m15_learning_proof_evaluator.py', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-a', 232, 233, '603a26890ceee940b0a3c9009e06d994f9f2f342', '6e0fa4e8fdf4a672581cd897d52743d0462f0d4b', 'schemas/m15-learning-proof.schema.json', 'json-schema', 'efe1113dcdb1ea193531a55fd182c58bcfd94f5f', '100644', 'c03bd734f287fae23deb7f8d3eaf2ccb501774caeccbe85d6520c57b7fdc1a44', 'tests/test_m15_learning_proof_evaluator.py', 'maintained', 'git-object:6e0fa4e8fdf4a672581cd897d52743d0462f0d4b:schemas/m15-learning-proof.schema.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-a', 232, 233, '603a26890ceee940b0a3c9009e06d994f9f2f342', '6e0fa4e8fdf4a672581cd897d52743d0462f0d4b', 'tests/test_m15_learning_proof_evaluator.py', 'evaluator-tests', '103e103ea629ea8a58c998db9deb2e9f674192e7', '100644', 'd382b1239bb623f3d165b24bda830a285f1aeaee93e53b9dc9abb8ada7b6b6c4', 'tests/test_m15_learning_proof_evaluator.py', 'maintained', 'git-object:6e0fa4e8fdf4a672581cd897d52743d0462f0d4b:tests/test_m15_learning_proof_evaluator.py', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-b', 234, 237, '270a5bbb536c6bf0726e95455d4bb61ac86d693e', '8e475518f2da6232ae9a6264d8e9c9f1e5fc514a', 'docs/learning-governance/m15-capability-memory-pack-contract.md', 'governance-contract', '1dc2344f50532111f32355dfffafa56c3ec214e4', '100644', '10152aea4911711c09edbb21bb78696244f9e71fe8447d9737a907eb8a3bb9df', 'tests/test_m15_capability_memory_pack_evaluator.py', 'maintained', 'git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:docs/learning-governance/m15-capability-memory-pack-contract.md', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-b', 234, 237, '270a5bbb536c6bf0726e95455d4bb61ac86d693e', '8e475518f2da6232ae9a6264d8e9c9f1e5fc514a', 'examples/public-integration-pack-pilot/m15-capability-pack-altered-derived-specification.json', 'synthetic-fixture', '7438af0d6f9c1735bf9046fd1bba570480b3e56c', '100644', '23f2502a23422d14215860d4dda5a154254365224909d4ac9a2c8a0eb8b3ed22', 'tests/test_m15_capability_memory_pack_evaluator.py', 'maintained', 'git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:examples/public-integration-pack-pilot/m15-capability-pack-altered-derived-specification.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-b', 234, 237, '270a5bbb536c6bf0726e95455d4bb61ac86d693e', '8e475518f2da6232ae9a6264d8e9c9f1e5fc514a', 'examples/public-integration-pack-pilot/m15-capability-pack-altered-graph.json', 'synthetic-fixture', 'b55b18a11d6472f3f71373cad8c68869ee995d31', '100644', '1193ba3eeb7c1462816a7b1fbf1a6d9ae16ac11a22b5c315715378d95565a564', 'tests/test_m15_capability_memory_pack_evaluator.py', 'maintained', 'git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:examples/public-integration-pack-pilot/m15-capability-pack-altered-graph.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
)

_EXPECTED_ARTIFACT_BINDINGS_EXACT += (
    ('track-b', 234, 237, '270a5bbb536c6bf0726e95455d4bb61ac86d693e', '8e475518f2da6232ae9a6264d8e9c9f1e5fc514a', 'examples/public-integration-pack-pilot/m15-capability-pack-executable-authority-claim.json', 'synthetic-fixture', '2a72b605385111b9c37b7315306bdc6d1779533f', '100644', '6e74d48b6f974a66f1187c7cefbaf45a8721c252a7c31bc84f250c828dde06e4', 'tests/test_m15_capability_memory_pack_evaluator.py', 'maintained', 'git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:examples/public-integration-pack-pilot/m15-capability-pack-executable-authority-claim.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-b', 234, 237, '270a5bbb536c6bf0726e95455d4bb61ac86d693e', '8e475518f2da6232ae9a6264d8e9c9f1e5fc514a', 'examples/public-integration-pack-pilot/m15-capability-pack-incompatible-runtime.json', 'synthetic-fixture', 'b5ae6ba9e24916377aa1f443c3c28f03bc5fd763', '100644', '2d585df48eb9899f80f3558767341c7d492bce14ee155552fad9f9571d6e31cf', 'tests/test_m15_capability_memory_pack_evaluator.py', 'maintained', 'git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:examples/public-integration-pack-pilot/m15-capability-pack-incompatible-runtime.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-b', 234, 237, '270a5bbb536c6bf0726e95455d4bb61ac86d693e', '8e475518f2da6232ae9a6264d8e9c9f1e5fc514a', 'examples/public-integration-pack-pilot/m15-capability-pack-missing-license-usage-boundary-evidence.json', 'boundary-record', '8c04ab66553a46d099aec1a9b8b11262c31db7b2', '100644', '2b6a9e3a8eae10299cd069bd938643c170669ce2eabce9f0200d2a981849a5de', 'tests/test_m15_capability_memory_pack_evaluator.py', 'maintained', 'git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:examples/public-integration-pack-pilot/m15-capability-pack-missing-license-usage-boundary-evidence.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-b', 234, 237, '270a5bbb536c6bf0726e95455d4bb61ac86d693e', '8e475518f2da6232ae9a6264d8e9c9f1e5fc514a', 'examples/public-integration-pack-pilot/m15-capability-pack-revoked.json', 'synthetic-fixture', 'a98c301c0f3f9c1b3e9c4dc33b7903a179aa02bc', '100644', '797a42b9c816acccd31759cb7b40a066ab70bcaa19683dc0ddbe66421fc538a3', 'tests/test_m15_capability_memory_pack_evaluator.py', 'maintained', 'git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:examples/public-integration-pack-pilot/m15-capability-pack-revoked.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-b', 234, 237, '270a5bbb536c6bf0726e95455d4bb61ac86d693e', '8e475518f2da6232ae9a6264d8e9c9f1e5fc514a', 'examples/public-integration-pack-pilot/m15-capability-pack-source-digest-mismatch.json', 'synthetic-fixture', '8a2992906863cee649614684aff0f9ebebcb96c9', '100644', '60041c22641c33104f2d990829a873dbc68b865fc31396b030ec60411f270e3a', 'tests/test_m15_capability_memory_pack_evaluator.py', 'maintained', 'git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:examples/public-integration-pack-pilot/m15-capability-pack-source-digest-mismatch.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-b', 234, 237, '270a5bbb536c6bf0726e95455d4bb61ac86d693e', '8e475518f2da6232ae9a6264d8e9c9f1e5fc514a', 'examples/public-integration-pack-pilot/m15-capability-pack-stale-specification.json', 'synthetic-fixture', '04ebfccd4519e2e79ca15fe403dfae522948ed19', '100644', '92ee515bd75303c77531ce2efb9dc445368e1cebe5e61cea1e3f4f073375cbca', 'tests/test_m15_capability_memory_pack_evaluator.py', 'maintained', 'git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:examples/public-integration-pack-pilot/m15-capability-pack-stale-specification.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-b', 234, 237, '270a5bbb536c6bf0726e95455d4bb61ac86d693e', '8e475518f2da6232ae9a6264d8e9c9f1e5fc514a', 'examples/public-integration-pack-pilot/m15-capability-pack-valid-verified.json', 'synthetic-fixture', 'c54cb7ec3c842deed422c5945265f8fc7f430b0c', '100644', '66a601ed0f289e785f37e629a4fdc839186c22a93dabc6cec6387b0f188b97d8', 'tests/test_m15_capability_memory_pack_evaluator.py', 'maintained', 'git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:examples/public-integration-pack-pilot/m15-capability-pack-valid-verified.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-b', 234, 237, '270a5bbb536c6bf0726e95455d4bb61ac86d693e', '8e475518f2da6232ae9a6264d8e9c9f1e5fc514a', 'runtime/m15_capability_memory_pack_evaluator.py', 'runtime-evaluator', 'd1429fbb930dfaa8a4f75c09cd6771ba2dc7190c', '100644', '5e45bbe0f311c3bfcc4d10ed7dc2b1eacbb8d64e4d8d2c922e74d558e66181e2', 'tests/test_m15_capability_memory_pack_evaluator.py', 'maintained', 'git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:runtime/m15_capability_memory_pack_evaluator.py', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-b', 234, 237, '270a5bbb536c6bf0726e95455d4bb61ac86d693e', '8e475518f2da6232ae9a6264d8e9c9f1e5fc514a', 'schemas/m15-capability-memory-pack.schema.json', 'json-schema', 'de3ba2fbe6e02c5390846258addeed70fac4da48', '100644', '051436c094413715849ddffd8b54beebb7239f8f288fd2849c333b412e374351', 'tests/test_m15_capability_memory_pack_evaluator.py', 'maintained', 'git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:schemas/m15-capability-memory-pack.schema.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-b', 234, 237, '270a5bbb536c6bf0726e95455d4bb61ac86d693e', '8e475518f2da6232ae9a6264d8e9c9f1e5fc514a', 'tests/test_m15_capability_memory_pack_evaluator.py', 'evaluator-tests', '8bb014ef58d6ba5e95bf401561844604bb11b66c', '100644', '806eb6fe660465a5ac72f553cb336cbe3822170218040f7f036e60d4680a28db', 'tests/test_m15_capability_memory_pack_evaluator.py', 'maintained', 'git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:tests/test_m15_capability_memory_pack_evaluator.py', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
)

_EXPECTED_ARTIFACT_BINDINGS_EXACT += (
    ('track-c', 238, 239, '5f98f6c86e6b61d50b1c8183aca0736a3419c533', '2d8bab3a84675543c34231a9e04521379febdac1', 'docs/learning-governance/m15-lineage-rollback-portability-contract.md', 'governance-contract', '2da0edca2e8b1e2fe50ed5f4798a9674b226c011', '100644', 'd6c421be2fede2480f8bc2f3c8b0221e1862273184915b2ed317e69357c60f47', 'tests/test_m15_lineage_rollback_portability_evaluator.py', 'maintained', 'git-object:2d8bab3a84675543c34231a9e04521379febdac1:docs/learning-governance/m15-lineage-rollback-portability-contract.md', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-c', 238, 239, '5f98f6c86e6b61d50b1c8183aca0736a3419c533', '2d8bab3a84675543c34231a9e04521379febdac1', 'examples/public-integration-pack-pilot/m15-lineage-rollback-portability-decision-proof-deletion-execution-authority.json', 'synthetic-fixture', '60f7a47fd93ebf380d99af51ec8b14260297fc12', '100644', '25f6ec6fcb7ec0e47ed125ffb2e328bddeba30f50a81a4ac1ecf4afb37b4812d', 'tests/test_m15_lineage_rollback_portability_evaluator.py', 'maintained', 'git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-decision-proof-deletion-execution-authority.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-c', 238, 239, '5f98f6c86e6b61d50b1c8183aca0736a3419c533', '2d8bab3a84675543c34231a9e04521379febdac1', 'examples/public-integration-pack-pilot/m15-lineage-rollback-portability-deletion-pending-unresolved-copies.json', 'synthetic-fixture', '504dae9bf980a55dd0d961159845d0efdf877bbf', '100644', 'b710d26212866fa40bcb4335385194449113758a102a59c0ddac2cc36332fc4b', 'tests/test_m15_lineage_rollback_portability_evaluator.py', 'maintained', 'git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-deletion-pending-unresolved-copies.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-c', 238, 239, '5f98f6c86e6b61d50b1c8183aca0736a3419c533', '2d8bab3a84675543c34231a9e04521379febdac1', 'examples/public-integration-pack-pilot/m15-lineage-rollback-portability-false-physical-provider-erasure-claim.json', 'synthetic-fixture', '9b762e08a0e569d9eba83f6352290570f264f3e6', '100644', '528b31423f15fd08c3b633ab2d079ed3ec5fdc5424cf3886755673931d439b6b', 'tests/test_m15_lineage_rollback_portability_evaluator.py', 'maintained', 'git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-false-physical-provider-erasure-claim.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-c', 238, 239, '5f98f6c86e6b61d50b1c8183aca0736a3419c533', '2d8bab3a84675543c34231a9e04521379febdac1', 'examples/public-integration-pack-pilot/m15-lineage-rollback-portability-learning-proof-rollback-authority.json', 'synthetic-fixture', 'e10a906ad5c745640c800e83d945a491ca649c9c', '100644', '437d5afb63e3b7cbac8bc791d198a38712acf755221a3af664412b94c238cdcc', 'tests/test_m15_lineage_rollback_portability_evaluator.py', 'maintained', 'git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-learning-proof-rollback-authority.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-c', 238, 239, '5f98f6c86e6b61d50b1c8183aca0736a3419c533', '2d8bab3a84675543c34231a9e04521379febdac1', 'examples/public-integration-pack-pilot/m15-lineage-rollback-portability-missing-downstream-dependency-declaration.json', 'synthetic-fixture', '7d8f00af4565ef60df7ebdcf84c249aad88485ac', '100644', 'fd3c8a08e02916523848a5ce8b0f544a741f65549ebd5e2e60fba70991fd1acb', 'tests/test_m15_lineage_rollback_portability_evaluator.py', 'maintained', 'git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-missing-downstream-dependency-declaration.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-c', 238, 239, '5f98f6c86e6b61d50b1c8183aca0736a3419c533', '2d8bab3a84675543c34231a9e04521379febdac1', 'examples/public-integration-pack-pilot/m15-lineage-rollback-portability-model-removal-drill-provider-specific-blocker.json', 'synthetic-fixture', '0492da9a45db3289358dab1246feaa78d4f62d82', '100644', '14c4baacce910250ac45d540abebd29581e023875a22e1a88f2d3b2dcd946e25', 'tests/test_m15_lineage_rollback_portability_evaluator.py', 'maintained', 'git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-model-removal-drill-provider-specific-blocker.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-c', 238, 239, '5f98f6c86e6b61d50b1c8183aca0736a3419c533', '2d8bab3a84675543c34231a9e04521379febdac1', 'examples/public-integration-pack-pilot/m15-lineage-rollback-portability-model-removal-drill-success.json', 'synthetic-fixture', 'ce1ce3e8ba7b04c5305ad0611bfde2b65e15a520', '100644', '4d39580e90388765d8dcea32f3d6c9001463ddae5a3047a5e388e1721ec5a221', 'tests/test_m15_lineage_rollback_portability_evaluator.py', 'maintained', 'git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-model-removal-drill-success.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-c', 238, 239, '5f98f6c86e6b61d50b1c8183aca0736a3419c533', '2d8bab3a84675543c34231a9e04521379febdac1', 'examples/public-integration-pack-pilot/m15-lineage-rollback-portability-qualified-deleted-no-physical-erasure.json', 'synthetic-fixture', 'db1972c88a7d32017dbce86baa02d90d295d7150', '100644', 'd42011b3a5ba913bc5c3170c09273ec3170a8d3be613a33b178e19299a3a1dc2', 'tests/test_m15_lineage_rollback_portability_evaluator.py', 'maintained', 'git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-qualified-deleted-no-physical-erasure.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-c', 238, 239, '5f98f6c86e6b61d50b1c8183aca0736a3419c533', '2d8bab3a84675543c34231a9e04521379febdac1', 'examples/public-integration-pack-pilot/m15-lineage-rollback-portability-replacement-model-use-incorrectly-authorized.json', 'synthetic-fixture', '22e37814f85078f163fe56e822617c63b66aa2ac', '100644', '82e419a91dfe334355dde8f263645e011782a83c91484fb2b0b79c803ecdd3c8', 'tests/test_m15_lineage_rollback_portability_evaluator.py', 'maintained', 'git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-replacement-model-use-incorrectly-authorized.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
)

_EXPECTED_ARTIFACT_BINDINGS_EXACT += (
    ('track-c', 238, 239, '5f98f6c86e6b61d50b1c8183aca0736a3419c533', '2d8bab3a84675543c34231a9e04521379febdac1', 'examples/public-integration-pack-pilot/m15-lineage-rollback-portability-revoked-capability-pack-unresolved-downstream-use.json', 'synthetic-fixture', '5dda3afde2969adbf42a3eaa5048fb24c8574a44', '100644', '1bdbd1bc3f61e1a83973da8dd466468844377831d8436d7c8f787a259a15fe3b', 'tests/test_m15_lineage_rollback_portability_evaluator.py', 'maintained', 'git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-revoked-capability-pack-unresolved-downstream-use.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-c', 238, 239, '5f98f6c86e6b61d50b1c8183aca0736a3419c533', '2d8bab3a84675543c34231a9e04521379febdac1', 'examples/public-integration-pack-pilot/m15-lineage-rollback-portability-rollback-blocked-incompatible-dependent.json', 'synthetic-fixture', '2411da98fff3398534794cd9ed09d8b2830bb2de', '100644', 'b6f48aed01b78b7489bc364e8537ce0916fa1b7defed49a9cd15b9ea322e8579', 'tests/test_m15_lineage_rollback_portability_evaluator.py', 'maintained', 'git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-rollback-blocked-incompatible-dependent.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-c', 238, 239, '5f98f6c86e6b61d50b1c8183aca0736a3419c533', '2d8bab3a84675543c34231a9e04521379febdac1', 'examples/public-integration-pack-pilot/m15-lineage-rollback-portability-rollback-ready-complete-dependency-evidence.json', 'synthetic-fixture', 'fd7fc0f20f4ab17468c1d45ed12176b4fd5aa4c6', '100644', '0ad2376f0359f75b0afd38432ce4c921e2466f2b60732c98a1bb24b3a7db788f', 'tests/test_m15_lineage_rollback_portability_evaluator.py', 'maintained', 'git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-rollback-ready-complete-dependency-evidence.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-c', 238, 239, '5f98f6c86e6b61d50b1c8183aca0736a3419c533', '2d8bab3a84675543c34231a9e04521379febdac1', 'examples/public-integration-pack-pilot/m15-lineage-rollback-portability-superseded-learning-artifact-known-dependents.json', 'synthetic-fixture', '93ebe358dd4ce64c66103a3b4f3eeee046515877', '100644', '8cc561a8bdc9c38641ea2522c466b910ce29590872f7645ec2207eeb58559dc7', 'tests/test_m15_lineage_rollback_portability_evaluator.py', 'maintained', 'git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-superseded-learning-artifact-known-dependents.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-c', 238, 239, '5f98f6c86e6b61d50b1c8183aca0736a3419c533', '2d8bab3a84675543c34231a9e04521379febdac1', 'examples/public-integration-pack-pilot/m15-lineage-rollback-portability-valid-complete-dependency-graph.json', 'synthetic-fixture', '2f8918feecb6a625b57bec6a2ac80b49ce97152b', '100644', 'a3c4e3c1c99341d07ff04612514d2abc25852acefd643b45852e98287de572fd', 'tests/test_m15_lineage_rollback_portability_evaluator.py', 'maintained', 'git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-valid-complete-dependency-graph.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-c', 238, 239, '5f98f6c86e6b61d50b1c8183aca0736a3419c533', '2d8bab3a84675543c34231a9e04521379febdac1', 'runtime/m15_lineage_rollback_portability_evaluator.py', 'runtime-evaluator', '27071fdf92b2561e9432e4a83022ea4ad506d4d5', '100644', '4337f04d0619f4e153088fe080fac7d1a2d976e3e04f6a124169e3d96c73f6a4', 'tests/test_m15_lineage_rollback_portability_evaluator.py', 'maintained', 'git-object:2d8bab3a84675543c34231a9e04521379febdac1:runtime/m15_lineage_rollback_portability_evaluator.py', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-c', 238, 239, '5f98f6c86e6b61d50b1c8183aca0736a3419c533', '2d8bab3a84675543c34231a9e04521379febdac1', 'schemas/m15-lineage-rollback-portability.schema.json', 'json-schema', '4e41841552d7ee2a9905b1104449274bc58e0333', '100644', '8702925c5a2c62efb77fc44cb68328f5be04b963afa27f366f99bef2ee071949', 'tests/test_m15_lineage_rollback_portability_evaluator.py', 'maintained', 'git-object:2d8bab3a84675543c34231a9e04521379febdac1:schemas/m15-lineage-rollback-portability.schema.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-c', 238, 239, '5f98f6c86e6b61d50b1c8183aca0736a3419c533', '2d8bab3a84675543c34231a9e04521379febdac1', 'tests/test_m15_lineage_rollback_portability_evaluator.py', 'evaluator-tests', 'ef2e87f272e176579a23eb7d5448ed13627cebb4', '100644', '5268f73a441898467e9b8f9471cfc4b9bd4fa27b7b67444fbf852d697d90f4c9', 'tests/test_m15_lineage_rollback_portability_evaluator.py', 'maintained', 'git-object:2d8bab3a84675543c34231a9e04521379febdac1:tests/test_m15_lineage_rollback_portability_evaluator.py', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'docs/learning-governance/m15-cross-control-regression-contract.md', 'governance-contract', '007a61eeceea2893c0068140c07615a34b1f370b', '100644', '23f29596100bd85fb52bc46210548a9404c21bf10d532d692d7fc43b84d64fdf', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:docs/learning-governance/m15-cross-control-regression-contract.md', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-01.json', 'synthetic-fixture', '0f8cb88ed41365e1b982a12a6787473eeebd456b', '100644', '96a657018d7a8be20faf90523957a4ccec0537f5b853f180c818710c17de975f', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-01.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
)

_EXPECTED_ARTIFACT_BINDINGS_EXACT += (
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-02.json', 'synthetic-fixture', '40cf8566eec0e1f4f7a68967060022ade47f20cc', '100644', 'cdc696021de2603bb99114d253210eb7ce005527b74d22dbc9dc5dcf178c88db', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-02.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-03.json', 'synthetic-fixture', '39a708dda6d55479a1a629024b4b44eca0ee163d', '100644', 'aa91eb15b431723c4d99550cd38ea3e1a63a064f7b641f58960e295c942525c7', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-03.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-04.json', 'synthetic-fixture', '2eabab7e3037dd1a7745f0a33eaefb47ac1662f9', '100644', '6d96c04a17dda4928caf8cf332252a17599b3e146a210affefaa1ee6eae6374d', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-04.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-05.json', 'synthetic-fixture', 'eaccf8406e0f83035ea033ac358ef59988e0a1b0', '100644', 'bcd86d84b9a2d24615764f4d4f5046c7e19d0f6bc0eddf28790f51c1d54896fb', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-05.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-06.json', 'synthetic-fixture', 'ac60ed83cde870d8dcbe31f13778e37c472bd8df', '100644', '6c70e7efa7000e76574815ddb593635c6bd48641ba36c12aa3d662de194b524b', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-06.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-07.json', 'synthetic-fixture', 'ee86c6d59f2ee1d4f0af29b535ef355181749a36', '100644', '3a4e8ae6456c76d0fab6111055ab4cc8f6b179a403e87ea6af13e535391d2752', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-07.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-08.json', 'synthetic-fixture', '9e96a992bcf57a09f25c40fd4a2c1f6da2fbb702', '100644', '201f4b3eb1d7c87329f3e40b0602f8556a0b3fddc8501999b1f2e61ba194adfc', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-08.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-09.json', 'synthetic-fixture', 'c548cde76c7128c8d88515e844faaebcc444f796', '100644', '8e7c85f22fe9ef0e66dbf29d88ddf35507ce3daf730eb5c467f3585b038cb9f8', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-09.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-10.json', 'synthetic-fixture', '2465fdeaa4b4ac84a6a5930b907b1f7d2e544463', '100644', 'b9ff7b587f1ebffa9a4994802e356915ea0c4c91bb83402493ed37747c202e98', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-10.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-11.json', 'synthetic-fixture', '4ef3930db08eaa6f2931d9989d09e928335e7bcf', '100644', '3a98010d7cea9ff288f47646721c189bb9019e3285959c6fae3018c8a6b783b3', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-11.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
)

_EXPECTED_ARTIFACT_BINDINGS_EXACT += (
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-12.json', 'synthetic-fixture', 'c54a3a95602a73f119f4cc5bafe1ceeb794c8341', '100644', '16b109d3938a7befb0e6947cef5e52e5bf922ba6389ffeb920a696f3f4049c49', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-12.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-13.json', 'synthetic-fixture', '253ab8a1a0feb53a9b048d5fa477a6eb6e1bf07c', '100644', '391a15a1641c4c8e172ea9128a1bbe5c55c60d672b8ec4f3c10ac712f7216841', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-13.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-14.json', 'synthetic-fixture', 'f22bb5431b58e4e331d7c123964bbd9004fb9f0b', '100644', 'bc0c3ac7a5f04e0a25684652d4e966b3e704514ac98454f98037ae1e52dc8693', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-14.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-15.json', 'synthetic-fixture', '205e0ea49cde0379009fa3e2c62309c704a3071a', '100644', '48e2ac1afb874f9b95a7f812df7bcb30ed3f06cc978be3b6118353cf0dd11806', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-15.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-16.json', 'synthetic-fixture', '90fb92621dfac34b3c2dd88a093e0b24d869fb1d', '100644', '0def119664507d11c91927a966055156b2be3c8e7a635d68b17ea8e23ad28497', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-16.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-17.json', 'synthetic-fixture', 'c4d42d6914bb869e61d69345c3eea27c19907184', '100644', 'f3b8bbcb6157738873aa1f6db18ce7bfbfdfa40d4e0ca75a5b7232d96d038b9a', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-17.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-18.json', 'synthetic-fixture', '5920fb287f3fb88cd593217ec530bbde219be8a7', '100644', '62ffa63f03979736e98f74da38bf5830e01cdaf8e77b5502f2ed85af0de1f629', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-18.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-19.json', 'synthetic-fixture', 'b514d4e984bd58432c09621daa00c8dd20112af0', '100644', 'a4621c85ee076e2bdc8af6811f4a12f1eb166c2c9f89d6a9bfe65a69f0beae4b', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-19.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-20.json', 'synthetic-fixture', 'af412432f376d19e53d61eced21666ee0b22d775', '100644', 'af2568e0286541a8e44b0be3580914c3cd558490e19acf0d8406f505aaf947b6', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-20.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-21.json', 'synthetic-fixture', 'ca5ad3888b14e62f94b86d4d6297706ba843669d', '100644', '3f9806c2700c359f7241d26c348dd18b6595ecd1ad115af9e583a609694d8ab4', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-21.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
)

_EXPECTED_ARTIFACT_BINDINGS_EXACT += (
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-22.json', 'synthetic-fixture', '8c96d0a89a83eb69f6d2c873b6545ddf02191825', '100644', '5dae89de53a3698dde0fc598e63b1e34d7a2b9ceff66f041475d022afcfe4060', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-22.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-23.json', 'synthetic-fixture', 'a22582435303c8e59ad4277e9e7e6f21d5d03576', '100644', '6402079bda56eb8a086613ef1e3541d42f0fbe5f546570e19b964b4ab729bcfa', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-23.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-24.json', 'synthetic-fixture', '9462de7e0c850c7bc994b70beb3150070139bede', '100644', '1da9dc250c9e3676257e93f4736133f5ec17d438e0c667f675ab1caf8d415c7c', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-24.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'examples/public-integration-pack-pilot/m15-cross-control-matrix.json', 'synthetic-fixture', '1fd3ee94b7a3bcb62dc5937f1670eb80b6db0627', '100644', '9d05d2a5331b02d673b2ee2c01e05e0aa098e981d10b9b072a8b92af226b0ca0', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-matrix.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'runtime/m15_cross_control_regression_evaluator.py', 'runtime-evaluator', '4f083ce374709716e5cc412accb0e723e4ee559f', '100644', '4a412bbd215ed3974d842bc09ee0011b4148f849d5d8e91611a324ef83fc6af6', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:runtime/m15_cross_control_regression_evaluator.py', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'schemas/m15-cross-control-regression.schema.json', 'json-schema', '82250c57f380099b04d7c2574101469e42e1929d', '100644', 'd52ef7010f596e28592c738b536f0d3131e60c5886ed538f1a57a067c675d651', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:schemas/m15-cross-control-regression.schema.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-d', 240, 241, '3bec19e42693b757b9abbb077146ca9860d48c1e', 'e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f', 'tests/test_m15_cross_control_regression_evaluator.py', 'evaluator-tests', 'ee1d7dd3ea493f70a38d0d42a127d77d41f814f8', '100644', '472b75a13498fbc257bbca9cf6eabba688e07cb236f36e3778587b0025415c78', 'tests/test_m15_cross_control_regression_evaluator.py', 'maintained', 'git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:tests/test_m15_cross_control_regression_evaluator.py', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'docs/learning-governance/m15-operational-readiness-contract.md', 'governance-contract', 'd454686815611ec8e28778298b408f2b8df7defc', '100644', '47d8e744d9e9be51f95f0e66eb6a511b748077ce4f5b9f49bf6a62093fb16d96', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:docs/learning-governance/m15-operational-readiness-contract.md', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-01-valid-maintained-main.json', 'synthetic-fixture', '27a4dbe92808abd3122ff89843779e9c7d183719', '100644', '9aad611db5379353f34815e2826bf471694193b393abbbdd71a9a153c2e9fc16', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-01-valid-maintained-main.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-02-maintained-main-binding-mismatch.json', 'synthetic-fixture', '324bbf57af27c1bd813354134383cc25da5b9ef9', '100644', '85ba22b02d08d6e55029c626f483337ad8febff884e01ed1325f067478d7c1da', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-02-maintained-main-binding-mismatch.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
)

_EXPECTED_ARTIFACT_BINDINGS_EXACT += (
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-03-source-track-binding-mismatch.json', 'synthetic-fixture', '828ad36732db7aea16ebdeff1bd6c20e5202dfac', '100644', '44616ae315d9d00140ce2b1c4faabd32479053b7560d95b6a2ba2b37adac7c9b', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-03-source-track-binding-mismatch.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-04-incomplete-artifact-inventory.json', 'synthetic-fixture', '1937fa7f8039728c33ec36dee83616ada7c2f625', '100644', '8c4e8a70f6fc52bf32d1c07cf5c788bf6787165bde00532d94bc7ba1f4fb5110', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-04-incomplete-artifact-inventory.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-05-artifact-integrity-failure.json', 'synthetic-fixture', '19d67542103b5ead8b9c28ee355815148d017505', '100644', 'fd1055a4d0d1699187deb2c041c358e260d2622f514caca966e9e85c1c3dabe7', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-05-artifact-integrity-failure.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-06-internal-consistency-failure.json', 'synthetic-fixture', 'aa60a7229dee9ef0aaee06817159e12a83fd46c5', '100644', '73dc57c22802c81fff132badd7e86b84c2b2d1c9caddf60ea467b12a6e803c2a', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-06-internal-consistency-failure.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-07-cross-control-matrix-unbound.json', 'synthetic-fixture', '3050c571c067d11b42addaa6b4660191c3273754', '100644', '143957f60cf1da7ab08f108331861e198b95fa8425d092d6d3f11b7a90d10b78', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-07-cross-control-matrix-unbound.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-08-incomplete-test-coverage.json', 'synthetic-fixture', 'edff791f05136f67762c7e8b9f6d3ae578e133a3', '100644', '7f170117fb4f2805bb9ae4678599df8166ce80ef1e1ca8a4e696e9fd24d4f778', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-08-incomplete-test-coverage.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-09-incomplete-verification-command-manifest.json', 'machine-readable-manifest', '22c6891b91aec4b4ce1bc8e1e7a86916bfbbdfec', '100644', 'ce72f6edcfd49b14253d2118b802cbc282ce0ac638955a57b63a22ed44243705', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-09-incomplete-verification-command-manifest.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-10-verification-execution-claimed.json', 'synthetic-fixture', '11f1290eb8e75acaf1cd84a2811bbb5704e6950e', '100644', 'c5ee061a8e0517741d6cbf527778eb8e8adf1f2dfc111916741aa9c9779c01ca', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-10-verification-execution-claimed.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-11-completion-approval-claim.json', 'synthetic-fixture', '38e22ca9a82fff8649f8a582ee894368d04e4887', '100644', '73567d971012393ddc119eb83062642cc2959516be50771cdc6cd76085030b5c', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-11-completion-approval-claim.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-12-tracker-closure-claim.json', 'synthetic-fixture', 'b7f72df2cf26f920f7edfc56935dffade31d0161', '100644', '0244643637e551b3277604906da3048241130575b26f8d704d97057def73fb2e', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-12-tracker-closure-claim.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
)

_EXPECTED_ARTIFACT_BINDINGS_EXACT += (
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-13-m15-completion-claim.json', 'synthetic-fixture', 'f911604ac5998f243494ba502a3f08536044d728', '100644', '31e7d71239db392ff0809959cba7adee5b8c5a9d984087b28733a4b4d9269184', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-13-m15-completion-claim.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-14-readme-authorization-claim.json', 'synthetic-fixture', 'd185c556afa544f758d4148121d187dbe40a7aa1', '100644', '75294b248efefe6b8295ae351ecfb28b3171612905a34efd4c9251c9deba025d', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-14-readme-authorization-claim.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-15-tag-authorization-or-creation-claim.json', 'synthetic-fixture', '47a92fc9915fefa002078df350381e34907b4257', '100644', 'a5d17e8c2d67aefbb100054d50edc177ae6a31685963ed475ebb9fac0c717f5f', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-15-tag-authorization-or-creation-claim.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-16-release-authorization-or-publication-claim.json', 'synthetic-fixture', '55ab272a6fbf68f404d7e642a066a98abfbb0159', '100644', '98781331e52175fd74e8d480e4fb960c0bf77a98a1feaf920a3a8644eba818b6', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-16-release-authorization-or-publication-claim.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-17-known-repository-local-completion-blocker.json', 'synthetic-fixture', '6964c11c9433531ba811b8e83668808a06308c90', '100644', '042b14f1428a811ca8f4f3fd5005572e961de2d68b160ba9744df125c3ad0629', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-17-known-repository-local-completion-blocker.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-18-malformed-schema-version.json', 'synthetic-fixture', 'd618aa09533764089db31135b8274dbe1771c97d', '100644', 'f82ad6bb84e979d930654e91320f19e27cdf248e2a77fb2d8cbd036e23f3f3f7', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-18-malformed-schema-version.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-19-failed-targeted-test.json', 'synthetic-fixture', 'e25bb9a8e0ba76aca1c490c7f2b401c7d43a73d0', '100644', '335785bbbf6eed8c045053a22edd01944a5d72d24513e35ed7e67af892674e35', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-19-failed-targeted-test.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-20-test-error.json', 'synthetic-fixture', 'a8a2c1a6e516272b4f639d20648103a69d8ec44e', '100644', '002e8d6d7843d78de5d1c6b0e0574cd85ab17f4fb053a2c73c0170118fd80699', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-20-test-error.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-21-unexpected-skip.json', 'synthetic-fixture', '120948d02c55cbd102b1ffe0ab76cb7ef313e9cb', '100644', 'f269d73f9ebf83d3e79a9776e014acdbec2bbb7e007ccfbd4833664d03545602', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-21-unexpected-skip.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-22-missing-verification-result.json', 'synthetic-fixture', '52883a2e9a0b22a5b766bfb3393e69758abc24e4', '100644', '0cb48dfa8df43c23415c2f11058590e4be15609f3d37bc8fbcbfab48a21ef9e7', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-22-missing-verification-result.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
)

_EXPECTED_ARTIFACT_BINDINGS_EXACT += (
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-23-observed-test-count-mismatch.json', 'synthetic-fixture', 'bce3df2510ef477c718c8975846d8b6ede5e87e6', '100644', '9e7fb4c833078e8fe2ff7e4826f0a91f8010e281d0c794a1e9bec5f8c326115d', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-23-observed-test-count-mismatch.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-24-verification-result-missing-main-sha.json', 'synthetic-fixture', '414557f5cccdf7d413b29a4798d25bd4a37e290f', '100644', 'e659fedc52e439927bb7eb80a14c8de24bc099a7db681296357625e2b58f6045', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-24-verification-result-missing-main-sha.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-25-required-artifact-unverified.json', 'synthetic-fixture', '6f5a687b37b0519926312d5d75ca6a8cf6f375e9', '100644', '9b841c41ebebcae2dba8da5cdae8e46b4f71c17abdae2341a49169c3bd80a52f', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-25-required-artifact-unverified.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-26-deferred-artifact-without-reason.json', 'synthetic-fixture', 'ef300568c8f84413ca7ac7c9aeff34d9c422949c', '100644', '51aa84a12fc0bde3b08aca7f6cfa7aecf8136690a41fcfd6a195e9c1734bc1bf', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-26-deferred-artifact-without-reason.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-27-track-d-external-control-dependency-drift.json', 'external-evidence-linkage', 'c3300fb87029848b0efaa41bcefc5980eb34c931', '100644', '1b2bda2f12c7ed62c1c3f96e9806a5985e2f43c010a544bc5e73c3c1e25aa8c0', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-27-track-d-external-control-dependency-drift.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-28-candidate-head-receipt-binding-mismatch.json', 'external-evidence-linkage', '28a31e146a173bf278837219fe7651ae02140d76', '100644', '06f42ddcc8c571863fa1fdfe67736332bbd3d80ffe1ef4a65058a08394fa3089', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-28-candidate-head-receipt-binding-mismatch.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-29-baseline-candidate-sha-conflation.json', 'synthetic-fixture', '3f0bdaaa11c1026258855bd54c822d39e888b2dd', '100644', '2d6365a1f2dca4c5e98fe77bf987f095b7fbe6f3b1ee8df8e913d2bea087674b', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-29-baseline-candidate-sha-conflation.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-30-missing-external-execution-receipt.json', 'external-evidence-linkage', '06ec329938386a85750279e2ec4a7ac1db496b71', '100644', 'f821dfcd998d081628a6c74149ae095ec8be499ca3d7e0bdf656100081aff649', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-30-missing-external-execution-receipt.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-31-undeclared-python-launcher-substitution.json', 'synthetic-fixture', 'd4e48eb8b19a3e4ff8e72aefe99445559665be69', '100644', 'bbf96ef0105597e9046ba5cce4628f9a10d490b34aed71b16d499eeb19ac0d67', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-31-undeclared-python-launcher-substitution.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-32-missing-python-interpreter-version.json', 'synthetic-fixture', 'd46089d1c24dba38b84c5a6daa01dfd57027d9b1', '100644', 'f79a9f71a7894049ee4d7d86d74d7f8906e51d9bf3ae6a8e1db6a23e25ebbda2', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-32-missing-python-interpreter-version.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
)

_EXPECTED_ARTIFACT_BINDINGS_EXACT += (
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-33-missing-transcript-digest.json', 'synthetic-fixture', '337b373240c9d93b3737d31846d4edf3bc0fbeff', '100644', 'b5ea416c201582de191c6c41f4addd426fb7c63a8fad7fd7ba6a5d6e22e7ba1e', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-33-missing-transcript-digest.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-34-command-result-binding-mismatch.json', 'synthetic-fixture', '0176d4a1355092df6f4635d5d349803eb7a26022', '100644', 'ea3610e1f46116730c85aa3eb85839a115740009838a22714ad58b742465d524', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-34-command-result-binding-mismatch.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'examples/public-integration-pack-pilot/m15-operational-readiness-manifest.json', 'machine-readable-manifest', '99ebb1bb51875c3f5c5e1bd959868097d67ec94f', '100644', '9e8021398e643330779fcbb0f04a15bbbbf88d238ec0d29eb7d41697158e2eb5', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-manifest.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'runtime/m15_operational_readiness_evaluator.py', 'runtime-evaluator', '432dc6124a4bc233f4b5e2ece6bd6879b257d730', '100644', '13021d344cc47c34f2bf3c54ba0a88c54468c10408c67c18c86eaab3e674c627', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:runtime/m15_operational_readiness_evaluator.py', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'schemas/m15-operational-readiness.schema.json', 'json-schema', '92368bfd000ea7b2a41139594fa8f4a4a8471198', '100644', 'bacbf3ed130356c12b6407623e9fded74e4ac0d85af0415c328ffcdff280d53a', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:schemas/m15-operational-readiness.schema.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e1', 242, 243, '55629976db7f7b8dc9e2153eaf67f054bd9ee708', '27c92e290cf6ad60bada49b63fe1888511930980', 'tests/test_m15_operational_readiness_evaluator.py', 'evaluator-tests', 'f3b58fdfb117230b3ba06d1d2af609d6eed922b2', '100644', '87e1bcc65cee94617bc8656cd02864b400c08bbe611e651e4d7ed9cc48544c60', 'tests/test_m15_operational_readiness_evaluator.py', 'maintained', 'git-object:27c92e290cf6ad60bada49b63fe1888511930980:tests/test_m15_operational_readiness_evaluator.py', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'docs/learning-governance/m15-release-proof-linkage-contract.md', 'governance-contract', 'd9b0976c86d1d2f381997a4220a993c8307a0748', '100644', '359f3fa0bed44ec85c8225158ad8fb1b89d1779479e11e6a675cb1e52712204d', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:docs/learning-governance/m15-release-proof-linkage-contract.md', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-01-exact-e1-candidate-and-merge-tree-match.json', 'synthetic-fixture', 'dc1c1a897bb9b7d1f819c349d368b2a934d6b410', '100644', '375655a5bca0ce710d9aa2a1b8bfe57e84fc61b1ab41430c11e52dea118a64fe', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-01-exact-e1-candidate-and-merge-tree-match.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-02-candidate-changes-preserved-with-explained-base-advancement.json', 'synthetic-fixture', '42708258f476bb9600488780bae208aec72eb318', '100644', '1500d23e5b068e4df7ae37d3e491a6993fa012e16e5709d99963d67270f75b1e', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-02-candidate-changes-preserved-with-explained-base-advancement.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-03-e1-candidate-head-mismatch.json', 'synthetic-fixture', 'ee058ba05e9c2443f9dc7c2e2db59f8d2d2a1a59', '100644', 'cab01691c16af18c7bc6feec39060c7c185980c517921994e3f4102ac05c8086', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-03-e1-candidate-head-mismatch.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
)

_EXPECTED_ARTIFACT_BINDINGS_EXACT += (
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-04-e1-candidate-tree-mismatch.json', 'synthetic-fixture', '1893d6f592698f77a41fcbb2e57a93b31f759227', '100644', 'a83c2962fdd162281eeba60a4cb27b61b9e2b2d5f506b8ec4256fd400bddb684', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-04-e1-candidate-tree-mismatch.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-05-e1-merge-commit-mismatch.json', 'synthetic-fixture', '2f70b6d21ec2d61a4a0a37a922557b0edddb928e', '100644', '3158dc6ad5a5fe6e348c82fd6282fc7017a5d49a255bd6944bcd1cb3f9e017ca', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-05-e1-merge-commit-mismatch.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-06-e1-merge-tree-is-missing.json', 'synthetic-fixture', '67da4de93926f08e018cd1484d515aad2f6c9957', '100644', 'aac925a629f72be59b7e15210f63a98a6c844d24dd9717b4cab8a8b2caf6c1cc', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-06-e1-merge-tree-is-missing.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-07-required-candidate-path-is-missing-after-merge.json', 'synthetic-fixture', '7964c7c4b18d30f5a993d52ff4ce657a2a12be22', '100644', '0194a40ab8fc536986ab261eff99d896b8502c13461c59fa46cfb63b0da45c40', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-07-required-candidate-path-is-missing-after-merge.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-08-candidate-and-merge-blob-mismatch.json', 'synthetic-fixture', 'd1fdc075d6df8d6ed08c98532f9622e44f3813a1', '100644', '2ca437d3f610d3fc4d9db4844d56969bc004b3cf08c15e002d6a93814359f919', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-08-candidate-and-merge-blob-mismatch.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-09-candidate-and-merge-canonical-digest-mismatch.json', 'synthetic-fixture', 'f340b2490b527249467021c0aecd9f4f66e603a7', '100644', 'b265cf3c6caf18c5e77038826eadce87376fa89c62dd6c61683bc2e21ba81b5d', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-09-candidate-and-merge-canonical-digest-mismatch.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-10-candidate-and-merge-file-mode-mismatch.json', 'synthetic-fixture', 'a2f301a681c23edda557aaf449d02267c6090324', '100644', '6bc635f86e3fdc6be9e0e8fecf707b67b480c97c0bed624cd7effdc6a9b23941', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-10-candidate-and-merge-file-mode-mismatch.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-11-unexpected-path-substitution.json', 'synthetic-fixture', '57fc6fde3880cd8fc47844fac2c9e7f5874bfeb9', '100644', '6c2ff66061c65d908e310317b742378183913025fc387e321fbd8fe538059baa', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-11-unexpected-path-substitution.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-12-incomplete-candidate-changed-path-manifest.json', 'machine-readable-manifest', '67b80b1053aa7a87136a4ec9ad33a3f4db190f75', '100644', '34deef712b8b73d9a6d6b2ec7311dab49013a72cec4f92871ae89b3d14260544', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-12-incomplete-candidate-changed-path-manifest.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-13-incomplete-merge-result-path-manifest.json', 'machine-readable-manifest', '1c5f151884e3079d34713b50e4a843736800a689', '100644', '0e3b21229eac68024ce2ea55ffc4575154bf1512a1922c87c4812ec1dce39552', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-13-incomplete-merge-result-path-manifest.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
)

_EXPECTED_ARTIFACT_BINDINGS_EXACT += (
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-14-missing-e1-external-receipt-linkage.json', 'external-evidence-linkage', 'ff6d674da2835d2d19999f427426f67c9c358e06', '100644', '89c04421104c132fb48d40e631162ada88d362fc1f2a04553ff8754919583b0b', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-14-missing-e1-external-receipt-linkage.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-15-e1-external-receipt-digest-mismatch.json', 'external-evidence-linkage', 'ba577147590b4419dfa387e80312f1122323a74e', '100644', '1467682623a8f94e9dc0a0e38adc64b7efded8e5e48dfa3dd64a5882d53f8bde', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-15-e1-external-receipt-digest-mismatch.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-16-e1-receipt-bound-to-another-candidate.json', 'external-evidence-linkage', '38fbfa43d98bf88d5f87a070be41675672cbd899', '100644', '673970528df18a85cc7b97330823aa7b15a7046acf3fddb07ae13f7491f05b76', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-16-e1-receipt-bound-to-another-candidate.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-17-e1-receipt-bound-to-another-baseline.json', 'external-evidence-linkage', '77c9095f90b702047ba5484fcd2d89b3d5440270', '100644', 'd2e208c3ba7ebc99daffd9ad78e8dd4e41825d7ab4eca4f1f5e4d079964edff8', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-17-e1-receipt-bound-to-another-baseline.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-18-e1-receipt-treated-as-merge-approval.json', 'external-evidence-linkage', '9745a665bb6ab83b6b6584b3ff0bcebc0a4f27ed', '100644', 'cdeb14bfc7875a3a59e45e7f1c824b126c4a83fc8e005686db4c5a25f592a7cc', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-18-e1-receipt-treated-as-merge-approval.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-19-provenance-success-treated-as-human-approval.json', 'synthetic-fixture', 'e55fc1bbff5d2bf02c5257d3ce6d475abc7f1ee7', '100644', '5921cc77739e474d5c7980241961a1eeda5eef39506be1f5a3536ad8d51365b6', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-19-provenance-success-treated-as-human-approval.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-20-operational-readiness-treated-as-completion-approval.json', 'synthetic-fixture', '791388e58ec2f5663b4d3b33f3cbfed438a93e52', '100644', 'd755560619130d00576b7e7e52d135582b0e8765fed86cf1cd72098b1b9e93c1', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-20-operational-readiness-treated-as-completion-approval.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-21-merge-commit-treated-as-a-published-release.json', 'synthetic-fixture', '77927f730d31f05f831dd6e1910b485fd4761fe0', '100644', '6bbd5f4598c335ed827370ea87ceb43fdb2b6a51e57d6c387834266b1d469368', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-21-merge-commit-treated-as-a-published-release.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-22-future-v0-14-0-candidate-represented-as-tagged.json', 'synthetic-fixture', 'a8823829bea2d00c16e8a666a26f6598a1685e9f', '100644', 'bc9904b0fa44a0cfd6bae6af50ab5039c9490c1cd57e70cf0ebb585c1332a7cb', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-22-future-v0-14-0-candidate-represented-as-tagged.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-23-github-release-represented-as-published.json', 'synthetic-fixture', '5cb18d331f9b6e979e78c5a1c3ecdc9fed4aa735', '100644', 'e899bc7e07c47f0f5060fb9b216a00955ffa6a1aabd8180c945bb83577d03618', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-23-github-release-represented-as-published.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
)

_EXPECTED_ARTIFACT_BINDINGS_EXACT += (
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-24-tracker-231-represented-as-closed.json', 'synthetic-fixture', '6d08443cbb3f2b03349b820afe509ea48c95ee33', '100644', 'ceca86e8473045d30ba9f391cf4c84e3f9867eb4544e910bae47e8035ca7ab65', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-24-tracker-231-represented-as-closed.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-25-m15-represented-as-complete.json', 'synthetic-fixture', 'e6702c95bd12c7dfeccf54b02406f32a9922397e', '100644', '1dc16a3330dae0edde7ef7d25f2082d2a6fa89276c9433fb3a746d7c0190e775', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-25-m15-represented-as-complete.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-26-readme-completion-represented-as-authorized.json', 'synthetic-fixture', '530be5fded9e4debeaa846d19080544c32da51cb', '100644', 'b3c19dae79f5bae0e2cfdae20d4caa9950c27907c020bc537ab38526184359c8', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-26-readme-completion-represented-as-authorized.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-27-required-e2-linkage-blocker-omitted.json', 'synthetic-fixture', '47643903ece530922c1a6c4ff5a429fb8452e7e8', '100644', '3d72abff5f2c691a31cbbf3c2325ec7fb4abe5133ecfa746cb856db3fec8b6cc', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-27-required-e2-linkage-blocker-omitted.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-28-unverified-continuity-treated-as-linked.json', 'continuity-record', '2159d0e70989facd129e00465c112b39c93bb994', '100644', 'd4fe8b5f9cca77b0a090c32465bbb738655c1afa85c50afd51c473d62df4a99d', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-28-unverified-continuity-treated-as-linked.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-29-future-release-candidate-identifier-is-missing.json', 'synthetic-fixture', 'ee1b6644e99c11a1d30d14164a33eeb12eade599', '100644', 'c1b68b2bd33d366d4135c68f56acacdf2195443b856c8f7d0f76d86e9b5202b2', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-29-future-release-candidate-identifier-is-missing.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-30-release-proof-claims-decision-proof-or-learning-proof-sealing.json', 'synthetic-fixture', '05381dfcac7de4c313f2385206c118c471ddce50', '100644', '92df78cd1891422ae9f200645e52c15fbbba757535e6b8f8c330a8b4cc9c2532', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-30-release-proof-claims-decision-proof-or-learning-proof-sealing.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-31-unverified-continuity-remains-not-ready.json', 'continuity-record', '17c34f65891b1ab9cf10228a73a19fd1e8729e98', '100644', 'f99cdc09eb6ec7fd213d7a4105bb638d8527194c9eec61c3fa0d0e4d714cba5a', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-31-unverified-continuity-remains-not-ready.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-32-candidate-modification-is-preserved.json', 'synthetic-fixture', 'f93c787266cb7ba97dacb05258fe38d646770a70', '100644', 'dbe0fe39ee9410952258539617ade363933510f0f62f0bc58d9000154a44278b', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-32-candidate-modification-is-preserved.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-33-candidate-rename-is-preserved.json', 'synthetic-fixture', 'a81da2c9fcb7363fd6f2a188eac7d3dd43f2c332', '100644', '8a3f7897159b5c25e54697a96402d88d1a8d6d576f1c95c196494b732db9d847', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-33-candidate-rename-is-preserved.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
)

_EXPECTED_ARTIFACT_BINDINGS_EXACT += (
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-34-candidate-deletion-is-preserved.json', 'synthetic-fixture', 'ea168af26605e97f632c6b3d6bb237a14159f008', '100644', 'b0bc2ae32a1be21dad62bc0551bdbd899633ed3259a395e087bc65a51778c387', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-34-candidate-deletion-is-preserved.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-35-external-e2-verification-receipt-is-missing.json', 'external-evidence-linkage', 'c54c1a8e08c6e805702ea365c68e0722e1baa0a6', '100644', 'ebf4ad3e977aaf05a7cfa3d21ad020981ed9b32b9cf339dcd06b20fc34d4c28e', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-35-external-e2-verification-receipt-is-missing.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-36-external-e2-verification-receipt-is-inconsistent.json', 'external-evidence-linkage', '7e38142fc950b8ecd87c62a2eb3643b2dd13ba73', '100644', 'd0c9dc4aa4e45a755cbc6e9d344efbe35426ba1626be5049bd6305fb4ed9c6b4', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-36-external-e2-verification-receipt-is-inconsistent.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-37-external-pr-observation-is-missing.json', 'external-evidence-linkage', 'f118dddff441f7b98b341d816bdc7dfc4b6710d0', '100644', '74078ded045369d2260a29fb77314de7854e9858a0553c1bb375103bda0ca9dc', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-37-external-pr-observation-is-missing.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-38-pr-observation-bound-to-another-pr.json', 'synthetic-fixture', '723cb0d643e2de79d577d60f762aac12384301b9', '100644', '3d5ba2780a760ada32497f998b339719dede698ec5d5015e280159f5a9c9ad8a', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-38-pr-observation-bound-to-another-pr.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-39-observation-receipt-candidate-mismatch.json', 'external-evidence-linkage', '8d9d92cc9993b5c535a405c2ba166126917b4b7e', '100644', '416fe6a82df368970edd30856ae524ec5f53dd9d893cb302ad8f6902a3f11106', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-39-observation-receipt-candidate-mismatch.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-40-verification-test-count-below-minimum.json', 'synthetic-fixture', '664067710e4f77a54f556e4c16d6bc3e34da1b51', '100644', '10034dcdb976d62fd8063c7c3fc2af511f9188525b22d334204b607e4245fdaa', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-40-verification-test-count-below-minimum.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-candidate-changed-paths.json', 'synthetic-fixture', 'b476339bc96f9303cf6124619d760c01603043cd', '100644', '7def94051d634bad63ef8cbe27f0f068242312f6c20ca680e270a6cea4074378', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-candidate-changed-paths.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-candidate-to-merge-continuity.json', 'continuity-record', '76a9a65ea82fcb03ddc425a3107cc5fd328ad5aa', '100644', '8e1fa60898f4efd4c726f44dc3e756ae00231670e568f0b8ed6435d37dec1916', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-candidate-to-merge-continuity.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-e1-external-receipt.json', 'external-evidence-linkage', 'e30b7d7408517f5fdc86050b4a182d2815230db9', '100644', '5884203aff41d4b173fa21121669eadc6727c21a17f8f33e6ad1d964459b5d3c', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-e1-external-receipt.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
)

_EXPECTED_ARTIFACT_BINDINGS_EXACT += (
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-manifest.json', 'machine-readable-manifest', '8c482631bf8eea5cefc98769c71379baf74ecc5b', '100644', '6c9e020a6597f9e9e9fda0fff3cf4150b50c1155000ae598716453b99cf4e185', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-manifest.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-merge-result-paths.json', 'synthetic-fixture', '83593b26e3fe5ec9bd26400b1646df79dfb8f692', '100644', '40f246f3f30d4ca924c9004f5c60c8fa3c3a0342c285e407246e86704d92a908', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-merge-result-paths.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'examples/public-integration-pack-pilot/m15-release-proof-linkage-release-boundaries.json', 'boundary-record', '01a91f1ba05f4675bf197ce2828cbe84f6443a70', '100644', '33a0418bd509669644521980ce449dd4aa914094eb719a1b7637d3bc496ef833', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-release-boundaries.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'runtime/m15_release_proof_linkage_evaluator.py', 'runtime-evaluator', '6fdf56d2718be5d17b83da01bb47c76cd52b63d9', '100644', '1f62114d8b1ed16ec90173c0d8648e112350b46c45ed4df9a166d5d4441ed66e', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:runtime/m15_release_proof_linkage_evaluator.py', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'schemas/m15-release-proof-linkage.schema.json', 'json-schema', 'ded0187f339b990459386f509c9399181ca4de21', '100644', '6f7155564ec94397d096de1190087f568af4cdfa438ef75c13caffb47abd2031', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:schemas/m15-release-proof-linkage.schema.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e2', 248, 249, 'efc31e7d24c26d2cea2cb536a4cae257aababb5f', 'f6d074fca2fedecbf654697719179440bc0680d3', 'tests/test_m15_release_proof_linkage_evaluator.py', 'evaluator-tests', 'b24ceba23e0e6424f1663e6274170a08466a8edc', '100644', 'afc489cbc215a008d78ec440444bf5009d6d0a652f57c2c2fa087ffcf1961c1e', 'tests/test_m15_release_proof_linkage_evaluator.py', 'maintained', 'git-object:f6d074fca2fedecbf654697719179440bc0680d3:tests/test_m15_release_proof_linkage_evaluator.py', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'historical-track-artifact'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'README.md', 'readme-future-transition', '15110b9dea1cc8049b95740006d7e495106f916a', '100644', 'c4612bfd5346e69cfa51dd772bba43902368fcb06590686b6a05519e4d9b31de', 'tests/test_m15_completion_readiness_evaluator.py', 'e3-completion-readiness-transition', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:README.md', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-readme-next-phase-transition'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'docs/learning-governance/m15-completion-readiness-contract.md', 'governance-contract', '9171c7c33bfa51da5144be3b3251d77c88c42fca', '100644', 'c2c9781b2efdbc31817a5aac9ce9a42039cfa26e62c846fb1ab6189f54af0036', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:docs/learning-governance/m15-completion-readiness-contract.md', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-core-completion-readiness-artifact'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-01-valid-completion-readiness-package.json', 'synthetic-fixture', '17f53622d42a21cb7ba8f743b76b6ec40872b1f0', '100644', '835336cf210c4b562883b08c3cdc1e2e495a6745fde052aeb8b0dc2c0d5e48d2', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-01-valid-completion-readiness-package.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-02-e2-merge-commit-mismatch.json', 'synthetic-fixture', '6f2b259cf1f8b514751d1d61442cfab9b372d3bf', '100644', '3f6903f06aa7d2d13a2a7668ffd25fdf66846d3b980510c3eb93f9d7a52bb4b4', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-02-e2-merge-commit-mismatch.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
)

_EXPECTED_ARTIFACT_BINDINGS_EXACT += (
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-03-e2-merge-tree-mismatch.json', 'synthetic-fixture', '4c184cce64050af82152ed61f25c040221691533', '100644', '713eee19d39b67bf67df89b7d8fa4089301a5aa0ba6865e3b10fc6dcf20f1974', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-03-e2-merge-tree-mismatch.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-04-e2-candidate-not-merge-parent.json', 'synthetic-fixture', '4f8bce02da79d7b9ab59c6f6eb1d419026b1a2e3', '100644', '1ee2acbffc1213769c857d1b0804dd2d45680bb5a6600a780f753282c53fe49d', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-04-e2-candidate-not-merge-parent.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-05-e2-path-drift.json', 'synthetic-fixture', '431e4145c795d9f04464a5ca261c952c2ceb8e1d', '100644', '565d603a1f3cbc078fe61638b210fbd8a399d991da3b36e8cb72831e326bfd46', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-05-e2-path-drift.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-06-e2-observation-missing.json', 'synthetic-fixture', 'f62ae5521597dd9033d79f510d73f99fa4687740', '100644', 'd1d33d25f664cded10ab0664f4105309fe348e4f61e04cb20f3990820987e517', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-06-e2-observation-missing.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-07-active-receipt-missing.json', 'synthetic-fixture', 'c8f9461e5c413c44c84a51d2f9d1d6ad96634795', '100644', '8a628fb059f393ad59b09cc92c8747e75f6db97bbe74e76e8d2fef54b2e9d490', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-07-active-receipt-missing.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-08-superseded-receipt-used.json', 'synthetic-fixture', 'd3f5c256229353a252935ffbe193554a4820723c', '100644', '399265295b204d8e87f635873cfb2bda602877f579594b247051dad98b643fa7', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-08-superseded-receipt-used.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-09-active-receipt-digest-mismatch.json', 'synthetic-fixture', '9619d4d8e0d3c2d32e2860b192315b7f3ba33af5', '100644', '6e5e4d8d84a78206da4f5a48a290d444a8a5b6d5909b207e90cbcf3456a46976', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-09-active-receipt-digest-mismatch.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-10-track-a-evidence-missing.json', 'synthetic-fixture', 'ff7d7c938bda35223703caaf1c04a0e8b0755af2', '100644', 'a1bfc2faae00da385a905b00da5582b318d0c7266c39d86323d7964716bcb7a6', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-10-track-a-evidence-missing.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-11-track-b-evidence-missing.json', 'synthetic-fixture', 'c33942649350fb43e7b01f303ee3265a3bcff903', '100644', '7253fb6c992087fc510da00575176d0ed4a96041b99c624f995ddba14c35e048', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-11-track-b-evidence-missing.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-12-track-c-evidence-missing.json', 'synthetic-fixture', 'ab1f752df1624599916a3201aa0f45154c491dba', '100644', 'e83ad26e08bcb9ac9f4455d04d6708c55d62efe726ea497dc471103e76467218', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-12-track-c-evidence-missing.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
)

_EXPECTED_ARTIFACT_BINDINGS_EXACT += (
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-13-track-d-evidence-missing.json', 'synthetic-fixture', 'b0ebbfbff5f7baf35f6d9aff4ab5d18be9f87a51', '100644', '1f446b1956956bc83fa5894c0d67f35fcca81e40156f4ee676e4fb77fe664cc9', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-13-track-d-evidence-missing.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-14-track-e1-evidence-missing.json', 'synthetic-fixture', '48e3b815129eb6ede0cac3be9d0d8cd5b4e53721', '100644', '8b02765759ed3478b79ca97d46c1c7333aa6a970e71836cc2e7bc44f2ffd45aa', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-14-track-e1-evidence-missing.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-15-track-e2-evidence-missing.json', 'synthetic-fixture', '7f16df95d16a8b870df262f7f872f2584aed7ec6', '100644', '0552371b05039b583307ed24330a2092d9b499c5868c55dae1fab42c500cb8a6', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-15-track-e2-evidence-missing.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-16-acceptance-criterion-omitted.json', 'synthetic-fixture', '8c368518c5cc6d315b8bfc2a7150dd7d0225e8a6', '100644', '1335751a7f6243b07752f7df8e3511e728c60f4ba997cde1127caa85c1a85e08', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-16-acceptance-criterion-omitted.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-17-criterion-has-no-evidence.json', 'synthetic-fixture', '5b9a75ec36e8e50f015df328eed2e79912a4fd57', '100644', '5339bda8b3f0b79ab4ef909e0e5129d07df023fdb118818734695695c14666e0', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-17-criterion-has-no-evidence.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-18-hidden-blocker.json', 'synthetic-fixture', 'a0c21899124ad89900584bbee2fece6543413557', '100644', 'd7bd0e3f1afb160b042ab5f24a459a463809ece964fbf9c16b7ca2a2fc1499fe', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-18-hidden-blocker.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-19-tracker-represented-closed.json', 'synthetic-fixture', '9d3edeedaa597261bf2c853e4566a823a9ab36ec', '100644', '0bb24893632538b1c6654a07600a328259831f602df9b401cf866899d95476b4', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-19-tracker-represented-closed.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-20-m15-represented-complete.json', 'synthetic-fixture', '30ba133c96da98da032dc9b64a8d870d7ae8f3f6', '100644', 'f51458a972cd14f3b169caf7f7769738176d42aa22d181727bc2b0cfdf0e5451', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-20-m15-represented-complete.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-21-readme-says-v0-14-0-released.json', 'synthetic-fixture', '54e3f145182290e4e3d643e883f9f2e7a22c9c20', '100644', '964bf110e215dbaa88a37d5004ca6ecd7f805531ea60d080645a7d3d75b77cb3', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-21-readme-says-v0-14-0-released.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-22-readme-changes-releases.json', 'synthetic-fixture', '84e5b46db3d1da6ffd0a6d2a70f0bfe80493d1e5', '100644', 'fd64f1bb959f1e81a2a8f5212d90a74de9a2f054d7cdd008403825e29543a5e6', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-22-readme-changes-releases.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
)

_EXPECTED_ARTIFACT_BINDINGS_EXACT += (
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-23-readme-changes-current-status.json', 'synthetic-fixture', 'a2ec1412b7b0e7a3fbe5b927c2fbdf5012dfd66c', '100644', '3fbaecc5b9ba1941beaab3fb06ff48cb7aecff6f4076eb49898571282fed3b40', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-23-readme-changes-current-status.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-24-tag-represented-authorized.json', 'synthetic-fixture', 'ad7db9476243caeb6d29a206f8873d196a0141df', '100644', '1e6d50242999eb1cc3cf1424247736a84f808c3e3b79dcb32d29995080c8c885', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-24-tag-represented-authorized.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-25-github-release-represented-published.json', 'synthetic-fixture', '5bfc754d91337967d0616ab4b740ca0b3a85f91d', '100644', 'fb80be7ed6346160f94ed3520a80196e5473fb949fad212999c604be239d96f2', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-25-github-release-represented-published.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-26-track-e4-represented-complete.json', 'synthetic-fixture', '64bab36a9c8c0692303aed3d9830f84f84c71b66', '100644', '657b19534ff0d798c034c4aad56d768282f45d39cb9591b21ad7854b030496ba', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-26-track-e4-represented-complete.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-27-readiness-treated-as-approval.json', 'synthetic-fixture', '488802cb7d63c140982e4e8defcfd90460c5938a', '100644', 'b4d5c8c7aa26e29e40e440c296316b655b24717b93c082cbd38cf4d290017f47', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-27-readiness-treated-as-approval.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-28-decision-proof-sealing-claim.json', 'synthetic-fixture', '3f9e2813004ca6b187f46adf724e445128bea9ad', '100644', '993c6073935ad2cf6acca8d0ddaa5b5d224f5c3658cb8688fb0ab9ef98b7ec08', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-28-decision-proof-sealing-claim.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-29-learning-proof-sealing-claim.json', 'synthetic-fixture', 'f811e35097b27fd4303ae308f60cbd7ad55864a6', '100644', '9fa930e84c4345528b3836b44e5f93837b5621d56d7c9b5b36d2dfb394ff505b', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-29-learning-proof-sealing-claim.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-30-verification-below-minimum.json', 'synthetic-fixture', '4a1ea1c45ff377ee702a6f97eff8071cca9afdeb', '100644', '7ce2348593b03af2f56c05a2cc4f4686e263caa434694942f300744b80ab7fd8', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-30-verification-below-minimum.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-31-verification-failure.json', 'synthetic-fixture', '089c234f3c9fa50915042ef85630513a5c1f61ee', '100644', '99f9edb001a004e7fb6f74077ae5a75a5d4d2897f08d4ab3d6411cfa33f9c7e1', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-31-verification-failure.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-32-verification-error.json', 'synthetic-fixture', '043f925f3db72a188d075c805755419d666a2f45', '100644', 'ad4bcdcef9ef35be767956d64e85bb689e8fb2379d958c3e6a6573d1b4e7ccdc', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-32-verification-error.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
)

_EXPECTED_ARTIFACT_BINDINGS_EXACT += (
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-33-unexpected-skip.json', 'synthetic-fixture', '52e89b5ac03aa9482fe8e3b339e88adafb24b6e0', '100644', '26bac075b1cbce1de82f2b986e2047a34f5544c5f2e5d65044bcd947bf2a8734', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-33-unexpected-skip.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-34-nonzero-exit.json', 'synthetic-fixture', '67f66f15389034440cd9bbdf47d3d5d654a8cd59', '100644', '2fed4bb63b2c796190141bae235d3a9cd7a61d535833876e64ea275da537611c', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-34-nonzero-exit.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-35-pr-observation-receipt-candidate-mismatch.json', 'synthetic-fixture', '235a612a34bd6742c82420819edf5d80d0ee83f9', '100644', '922e9cf0a7f8501e6b18ce8820c85706399a548d40b23e6d93e58010a378943a', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-35-pr-observation-receipt-candidate-mismatch.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-36-runtime-execution-claim.json', 'synthetic-fixture', 'f3d9ede0eed68c026abfc0caafd12e50d2185f63', '100644', 'f03bff731b5062eb23868e66ca8eed619f592e57dfd3f1f3bdc1bde36763211f', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-36-runtime-execution-claim.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-37-external-evidence-authority-claim.json', 'synthetic-fixture', 'd9deca348147c7403661f0dec950a039078a8965', '100644', 'ada7aec7fdeef5142ad305255397954a90db97f419d11dcf8dfcf160bd186750', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-37-external-evidence-authority-claim.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-synthetic-scenario'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-acceptance-coverage.json', 'acceptance-matrix', 'b73d016d556ac2b35848b1307b27105da0a2f800', '100644', '48663ea8831b4867c1a06a1c47f3c613f246c4a985d033a219e7399204980782', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-acceptance-coverage.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-maintained-evidence-record'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-boundaries.json', 'boundary-record', '1c96c1f7e0bc03c232146e8308953a680e0c3160', '100644', '509c03dc9a70e9aec1b839c2fe36388fcdf4a974699443867855bebb9172e6bf', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-boundaries.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-maintained-evidence-record'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-e2-continuity.json', 'continuity-record', 'e0367654daeefa6322902e2e4797a5eca6808b92', '100644', '54be409721ce846287a26744bde6ae322080ac820da0d5b9903fd793869e3be7', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-e2-continuity.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-maintained-evidence-record'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-e2-external-evidence.json', 'external-evidence-linkage', '625acae23a12d6aed9c56fb283163e8a1225c629', '100644', 'cf6abd2084943a43bdd2633c94afc4317797008e452adf375e14155f2f0b4903', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-e2-external-evidence.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-maintained-evidence-record'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-manifest.json', 'machine-readable-manifest', '265bbdc0f707cdd037d928c6d2c4d861c4027d87', '100644', 'b4990c7e75542a4e97dfcbf25f4fd1fdc6febfbba9c0cc6507aba90d9440f210', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-manifest.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-maintained-evidence-record'),
)

_EXPECTED_ARTIFACT_BINDINGS_EXACT += (
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-readme-observation.json', 'readme-observation', '097d9493b031ba755f29585f9940ef6e4058a8b9', '100644', '91f2bea7b55aa7b214594c2ce5f2260e233d4923ad0f78147894a80c1e782d6f', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-readme-observation.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-maintained-evidence-record'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'examples/public-integration-pack-pilot/m15-completion-readiness-track-evidence.json', 'track-evidence-inventory', 'b4322c3e73b498cce3a65dd3fb6c1563f3443a8a', '100644', '09c3790e09cad1281bb93499bf36967a2cb1f95fe63d0c0e755d04af7e60d6e4', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:examples/public-integration-pack-pilot/m15-completion-readiness-track-evidence.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-maintained-evidence-record'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'runtime/m14_final_completion_evaluator.py', 'authorized-compatibility-repair', '341807d4a2d433c51701e5b5094e03f4eb12b25b', '100644', 'e5a9925c35196d13dd32444786a86fcd975192bc4f379aa0333ec3d8e30acc99', 'tests/test_m15_completion_readiness_evaluator.py', 'e3-authorized-compatibility-repair', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:runtime/m14_final_completion_evaluator.py', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-authorized-historical-compatibility-repair'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'runtime/m15_completion_readiness_evaluator.py', 'runtime-evaluator', '04e4a45348509d19c15a46692e6d6568b1945795', '100644', '28ec7d4b99f4144d229af073677ff5b98d48813b166300f810ccdf809589f8d3', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:runtime/m15_completion_readiness_evaluator.py', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-core-completion-readiness-artifact'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'schemas/m15-completion-readiness.schema.json', 'json-schema', '61e6d4a66036048b9cea87cc1603c5e0365a3867', '100644', 'f33e158326596f182625ee78d8c39e0287caa558cfd4c3d38e7f33055088b52b', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:schemas/m15-completion-readiness.schema.json', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-core-completion-readiness-artifact'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'tests/test_m14_final_completion_evaluator.py', 'authorized-compatibility-repair', 'd2c48597d3ac76aee6ee910ea530faea0010af9d', '100644', 'b002cdc5d0bd40baa74fc977293a9c1706ea21f6de7df02f46099dea4d708551', 'tests/test_m15_completion_readiness_evaluator.py', 'e3-authorized-compatibility-repair', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:tests/test_m14_final_completion_evaluator.py', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-authorized-historical-compatibility-repair'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'tests/test_m15_completion_readiness_evaluator.py', 'evaluator-tests', '0f36dd1e5378466ce051df38f1cb463e860175fe', '100644', 'f0ff78e0fabe8bcaa856e2c3258e30e6dc372964eed19063e71491e4444d4363', 'tests/test_m15_completion_readiness_evaluator.py', 'maintained', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:tests/test_m15_completion_readiness_evaluator.py', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-core-completion-readiness-artifact'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'tests/test_m15_lineage_rollback_portability_evaluator.py', 'authorized-compatibility-repair', '0309453f29e093ea942a6965b32bd8dad7f69d55', '100644', '0dee39fe81189fd558f136732579995245828bc6b14c9791b67c9bb6e8a39f5c', 'tests/test_m15_completion_readiness_evaluator.py', 'e3-authorized-compatibility-repair', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:tests/test_m15_lineage_rollback_portability_evaluator.py', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-authorized-historical-compatibility-repair'),
    ('track-e3', 250, 251, '907d2361233c7b0405a41271d7b02fa6c1a0c62d', '52ec76c17cd21ec519dfec45ced4ad720b82d80e', 'tests/test_m15_operational_readiness_evaluator.py', 'authorized-compatibility-repair', '28a08a2e90271c2d6188f5d17650d3f7c40973ab', '100644', '8bbc82b05ed6b309b0d470da6063522193223476f84f8ce5830d34bf4f29c93c', 'tests/test_m15_completion_readiness_evaluator.py', 'e3-authorized-compatibility-repair', 'git-object:52ec76c17cd21ec519dfec45ced4ad720b82d80e:tests/test_m15_operational_readiness_evaluator.py', HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY, 'e3-authorized-historical-compatibility-repair'),
)

EXPECTED_ARTIFACT_BINDINGS = _EXPECTED_ARTIFACT_BINDINGS_EXACT

ACCEPTANCE_BINDING_FIELDS = (
    "criterion_id", "criterion_text", "source_track", "evidence_references",
    "artifact_references", "test_references", "authority_boundary",
)
EXPECTED_ACCEPTANCE_NOTE = (
    "Maintained evidence is linked; evaluator success alone is not coverage."
)
EXPECTED_ACCEPTANCE_CRITERIA = (
    ("m15-ac-01", "Learning Proof schema is deterministic and machine-readable.", "track-a", ("https://github.com/aa-os/aaos-public/issues/231#criterion-01",), ("schemas/m15-learning-proof.schema.json",), ("tests/test_m15_learning_proof_evaluator.py",), AUTHORITY_BOUNDARY),
    ("m15-ac-02", "Learning Sovereignty Boundary classes are defined.", "track-a", ("https://github.com/aa-os/aaos-public/issues/231#criterion-02",), ("docs/learning-governance/m15-core-learning-proof-contract.md",), ("tests/test_m15_learning_proof_evaluator.py",), AUTHORITY_BOUNDARY),
    ("m15-ac-03", "Learning authorization remains separate from decision execution.", "track-a", ("https://github.com/aa-os/aaos-public/issues/231#criterion-03",), ("runtime/m15_learning_proof_evaluator.py",), ("tests/test_m15_learning_proof_evaluator.py",), AUTHORITY_BOUNDARY),
    ("m15-ac-04", "Retention purposes are explicitly constrained.", "track-a", ("https://github.com/aa-os/aaos-public/issues/231#criterion-04",), ("schemas/m15-learning-proof.schema.json",), ("tests/test_m15_learning_proof_evaluator.py",), AUTHORITY_BOUNDARY),
    ("m15-ac-05", "Capability packs bind exact source and derived content.", "track-b", ("https://github.com/aa-os/aaos-public/issues/231#criterion-05",), ("schemas/m15-capability-memory-pack.schema.json",), ("tests/test_m15_capability_memory_pack_evaluator.py",), AUTHORITY_BOUNDARY),
    ("m15-ac-06", "Stale, incompatible, altered, contaminated, and revoked states fail deterministically.", "cross-track", ("https://github.com/aa-os/aaos-public/issues/231#criterion-06",), ("runtime/m15_capability_memory_pack_evaluator.py",), ("tests/test_m15_capability_memory_pack_evaluator.py",), AUTHORITY_BOUNDARY),
    ("m15-ac-07", "Lineage covers derived memory, rules, skills, evaluations, and adapters.", "track-c", ("https://github.com/aa-os/aaos-public/issues/231#criterion-07",), ("schemas/m15-lineage-rollback-portability.schema.json",), ("tests/test_m15_lineage_rollback_portability_evaluator.py",), AUTHORITY_BOUNDARY),
    ("m15-ac-08", "Rollback evidence identifies downstream dependencies.", "track-c", ("https://github.com/aa-os/aaos-public/issues/231#criterion-08",), ("runtime/m15_lineage_rollback_portability_evaluator.py",), ("tests/test_m15_lineage_rollback_portability_evaluator.py",), AUTHORITY_BOUNDARY),
    ("m15-ac-09", "Deletion evidence does not falsely claim physical deletion.", "track-c", ("https://github.com/aa-os/aaos-public/issues/231#criterion-09",), ("docs/learning-governance/m15-lineage-rollback-portability-contract.md",), ("tests/test_m15_lineage_rollback_portability_evaluator.py",), AUTHORITY_BOUNDARY),
    ("m15-ac-10", "Model-removal portability drill is simulation-only and reproducible.", "track-c", ("https://github.com/aa-os/aaos-public/issues/231#criterion-10",), ("examples/public-integration-pack-pilot/m15-lineage-rollback-portability-model-removal-drill-success.json",), ("tests/test_m15_lineage_rollback_portability_evaluator.py",), AUTHORITY_BOUNDARY),
    ("m15-ac-11", "Public fixtures use synthetic data only.", "cross-track", ("https://github.com/aa-os/aaos-public/issues/231#criterion-11",), ("examples/public-integration-pack-pilot/m15-cross-control-matrix.json",), ("tests/test_m15_cross_control_regression_evaluator.py",), AUTHORITY_BOUNDARY),
    ("m15-ac-12", "Maintained evaluators perform no network access or external execution.", "cross-track", ("https://github.com/aa-os/aaos-public/issues/231#criterion-12",), ("runtime/m15_cross_control_regression_evaluator.py",), ("tests/test_m15_cross_control_regression_evaluator.py",), AUTHORITY_BOUNDARY),
    ("m15-ac-13", "Authority and Decision Proof boundaries are regression-tested.", "track-d", ("https://github.com/aa-os/aaos-public/issues/231#criterion-13",), ("docs/learning-governance/m15-cross-control-regression-contract.md",), ("tests/test_m15_cross_control_regression_evaluator.py",), AUTHORITY_BOUNDARY),
    ("m15-ac-14", "M15 targeted tests pass.", "track-e3", ("https://github.com/aa-os/aaos-public/issues/231#criterion-14",), ("examples/public-integration-pack-pilot/m15-completion-readiness-manifest.json",), ("tests/test_m15_completion_readiness_evaluator.py",), AUTHORITY_BOUNDARY),
    ("m15-ac-15", "Full maintained repository suite remains clean.", "track-e3", ("https://github.com/aa-os/aaos-public/issues/231#criterion-15",), ("examples/public-integration-pack-pilot/m15-completion-readiness-manifest.json",), ("tests/test_m15_completion_readiness_evaluator.py",), AUTHORITY_BOUNDARY),
    ("m15-ac-16", "Final completion and release publication remain separately authorized.", "track-e3", ("https://github.com/aa-os/aaos-public/issues/231#criterion-16",), ("examples/public-integration-pack-pilot/m15-completion-readiness-boundaries.json",), ("tests/test_m15_completion_readiness_evaluator.py",), AUTHORITY_BOUNDARY),
)
CRITERION_IDS = tuple(row[0] for row in EXPECTED_ACCEPTANCE_CRITERIA)

EXPECTED_BLOCKER_REGISTRY = tuple(
    (
        blocker_id,
        "resolved",
        (f"urn:aaos:m15:e4:blocker-evidence:{blocker_id}",),
        "Resolved by specific inert evidence; resolution grants no transition or publication authority.",
    )
    for blocker_id in REQUIRED_BLOCKERS
)
EXPECTED_READINESS_REGISTRY = tuple(
    (
        finding_id,
        "required",
        (f"urn:aaos:m15:e4:readiness-requirement:{finding_id}",),
        "Must be supplied and cross-bound before readiness; the requirement grants no authority.",
    )
    for finding_id in REQUIRED_READINESS_FINDINGS
)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return ()


def _sha(value: Any, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(character in "0123456789abcdef" for character in value)
    )


def _timestamp(value: Any) -> bool:
    return isinstance(value, str) and value.endswith("Z") and "T" in value


def _add(target: list[str], finding: str) -> None:
    if finding not in target:
        target.append(finding)


def _exact_header(
    value: Mapping[str, Any],
    schema_version: str,
    document_kind: str,
) -> bool:
    return (
        value.get("schema_version") == schema_version
        and value.get("document_kind") == document_kind
        and value.get("repository") == REPOSITORY
    )


def _authority_findings(value: Any, blocking: list[str]) -> None:
    forbidden_true = {
        "tag_created", "tag_authorized", "github_release_created",
        "github_release_published", "github_release_authorized",
        "decision_proof_sealed", "learning_proof_sealed", "risk_accepted",
        "audit_closed", "waiver_granted", "authority_transferred",
        "evaluator_is_human_approval", "verification_is_human_approval",
        "external_state_mutated", "merge_executed", "file_io_performed",
        "git_inspection_performed", "github_access_performed",
        "network_access_performed", "subprocess_executed",
        "verification_commands_executed", "repository_digests_calculated",
        "receipt_digests_calculated",
    }
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in forbidden_true and child is True:
                if key in {
                    "file_io_performed", "git_inspection_performed",
                    "github_access_performed", "network_access_performed",
                    "subprocess_executed", "verification_commands_executed",
                    "repository_digests_calculated", "receipt_digests_calculated",
                    "external_state_mutated", "merge_executed",
                }:
                    _add(blocking, "runtime-boundary-violation")
                elif key in {"decision_proof_sealed", "learning_proof_sealed"}:
                    _add(blocking, "proof-sealing-claim")
                elif key in {"risk_accepted", "audit_closed", "waiver_granted", "authority_transferred"}:
                    _add(blocking, "authority-transfer-claim")
                elif key in {"evaluator_is_human_approval", "verification_is_human_approval"}:
                    _add(blocking, "evaluator-output-as-human-approval")
                elif key in {"tag_created", "tag_authorized"}:
                    _add(blocking, "premature-tag-created-claim")
                elif key in {"github_release_created", "github_release_published", "github_release_authorized"}:
                    _add(blocking, "premature-github-release-published-claim")
            _authority_findings(child, blocking)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for child in value:
            _authority_findings(child, blocking)


def _normalize_commands(value: Any) -> tuple[tuple[Any, ...], ...]:
    normalized = []
    for item in _sequence(value):
        row = _mapping(item)
        normalized.append(
            (
                row.get("command_id"),
                tuple(_sequence(row.get("declared_logical_argv"))),
                row.get("execution_scope"),
                row.get("minimum_tests_observed"),
            )
        )
    return tuple(normalized)


def _normalize_compatibility_repairs(value: Any) -> tuple[tuple[Any, ...], ...]:
    return tuple(
        tuple(_mapping(item).get(field) for field in COMPATIBILITY_REPAIR_BINDING_FIELDS)
        for item in _sequence(value)
    )


def _validate_manifest(value: Any, blocking: list[str]) -> None:
    manifest = _mapping(value)
    if not _exact_header(manifest, MANIFEST_SCHEMA_VERSION, "final-completion-manifest"):
        _add(blocking, "manifest-invalid")
        return
    expected = {
        "source_issue": SOURCE_ISSUE,
        "parent_tracker": PARENT_TRACKER,
        "implementation_pr": E4_PULL_REQUEST_NUMBER,
        "source_main_base_sha": SOURCE_MAIN_BASE_SHA,
        "source_main_base_tree_sha": SOURCE_MAIN_BASE_TREE_SHA,
        "prior_material_artifact_count": PRIOR_MATERIAL_ARTIFACT_COUNT,
        "required_acceptance_criteria_count": len(EXPECTED_ACCEPTANCE_CRITERIA),
        "m15_state_before_merge": "active-and-incomplete",
        "tracker_231_state_before_merge": "open",
        "issue_252_state_before_merge": "open",
        "tag_state_before_merge": "absent-not-created",
        "github_release_state_before_merge": "absent-not-published",
        "expected_merge_method": "merge-commit",
        "repository_completion_transition": "human-reviewed-e4-merge-only",
        "evaluator_readiness_is_human_approval": False,
        "runtime_caller_data_only": True,
        "final_candidate_commit_external": True,
        "final_receipt_commit_external": True,
        "human_approval_commit_external": True,
        "decision_proof_sealed": False,
        "learning_proof_sealed": False,
        "runtime_boundary": RUNTIME_BOUNDARY,
        "authority_boundary": AUTHORITY_BOUNDARY,
    }
    if any(manifest.get(key) != expected_value for key, expected_value in expected.items()):
        _add(blocking, "manifest-binding-mismatch")
    if manifest.get("tracker_231_state_before_merge") != "open":
        _add(blocking, "premature-tracker-closure-claim")
    if manifest.get("issue_252_state_before_merge") != "open":
        _add(blocking, "premature-issue-closure-claim")
    if manifest.get("m15_state_before_merge") != "active-and-incomplete":
        _add(blocking, "premature-m15-complete-claim")
    if manifest.get("tag_state_before_merge") != "absent-not-created":
        _add(blocking, "premature-tag-created-claim")
    if manifest.get("github_release_state_before_merge") != "absent-not-published":
        _add(blocking, "premature-github-release-published-claim")
    if manifest.get("evaluator_readiness_is_human_approval") is not False:
        _add(blocking, "evaluator-output-as-human-approval")
    if tuple(_sequence(manifest.get("required_track_ids"))) != REQUIRED_TRACK_IDS:
        _add(blocking, "manifest-track-registry-mismatch")
    if tuple(_sequence(manifest.get("required_blockers"))) != REQUIRED_BLOCKERS:
        _add(blocking, "manifest-blocker-registry-mismatch")
    if tuple(_sequence(manifest.get("required_readiness_findings"))) != REQUIRED_READINESS_FINDINGS:
        _add(blocking, "manifest-readiness-registry-mismatch")
    if _normalize_commands(manifest.get("verification_commands")) != EXPECTED_VERIFICATION_COMMANDS:
        _add(blocking, "verification-command-registry-mismatch")
    observed_repairs = _normalize_compatibility_repairs(
        manifest.get("authorized_historical_compatibility_repairs")
    )
    if observed_repairs != EXPECTED_AUTHORIZED_COMPATIBILITY_REPAIRS:
        _add(blocking, "unapproved-compatibility-repair")
        if len(observed_repairs) == len(EXPECTED_AUTHORIZED_COMPATIBILITY_REPAIRS):
            _add(blocking, "historical-evidence-rebaseline")
    if "source_main_base_ref" in manifest:
        _add(blocking, "mutable-main-source-base-pinning")


def _normalize_artifacts(value: Any) -> tuple[tuple[Any, ...], ...]:
    rows = []
    for item in _sequence(value):
        artifact = _mapping(item)
        rows.append(tuple(artifact.get(field) for field in ARTIFACT_BINDING_FIELDS))
    return tuple(rows)


def _validate_inventory(value: Any, blocking: list[str]) -> None:
    inventory = _mapping(value)
    if not _exact_header(inventory, TRACK_EVIDENCE_SCHEMA_VERSION, "track-evidence-inventory"):
        _add(blocking, "track-evidence-inventory-invalid")
        return
    if inventory.get("source_main_base_sha") != SOURCE_MAIN_BASE_SHA:
        _add(blocking, "track-evidence-source-base-mismatch")
    if inventory.get("source_main_base_tree_sha") != SOURCE_MAIN_BASE_TREE_SHA:
        _add(blocking, "track-evidence-source-base-mismatch")
    if inventory.get("artifact_count") != PRIOR_MATERIAL_ARTIFACT_COUNT:
        _add(blocking, "track-evidence-count-mismatch")
    if dict(_mapping(inventory.get("track_counts"))) != TRACK_COUNTS:
        _add(blocking, "track-evidence-count-mismatch")
    if _normalize_artifacts(inventory.get("artifacts")) != EXPECTED_ARTIFACT_BINDINGS:
        _add(blocking, "track-a-e3-evidence-substitution")
        observed = _sequence(inventory.get("artifacts"))
        if len(observed) > PRIOR_MATERIAL_ARTIFACT_COUNT:
            _add(blocking, "unapproved-compatibility-repair")
        elif len(observed) == PRIOR_MATERIAL_ARTIFACT_COUNT:
            _add(blocking, "historical-evidence-rebaseline")
    if inventory.get("historical_evidence_rebaselined") is not False:
        _add(blocking, "historical-evidence-rebaseline")
    if inventory.get("mutable_main_ref_pinned") is not False:
        _add(blocking, "mutable-main-source-base-pinning")


def _validate_e3_continuity(value: Any, blocking: list[str]) -> None:
    record = _mapping(value)
    if not _exact_header(record, E3_CONTINUITY_SCHEMA_VERSION, "e3-continuity-record"):
        _add(blocking, "malformed-e3-continuity-evidence")
        return
    expected = {
        "source_issue": E3_SOURCE_ISSUE,
        "implementation_pr": E3_PULL_REQUEST_NUMBER,
        "source_main_base_sha": E3_SOURCE_MAIN_BASE_SHA,
        "source_main_base_tree_sha": E3_SOURCE_MAIN_BASE_TREE_SHA,
        "candidate_sha": E3_CANDIDATE_SHA,
        "candidate_tree_sha": E3_CANDIDATE_TREE_SHA,
        "merge_sha": E3_MERGE_SHA,
        "merge_tree_sha": E3_MERGE_TREE_SHA,
        "candidate_is_merge_parent": True,
        "source_main_base_is_merge_parent": True,
        "candidate_is_merge_ancestor": True,
        "merge_is_current_main_ancestor": True,
        "candidate_to_merge_changed_path_count": 0,
        "additional_merge_result_difference_count": 0,
        "relation": E3_RELATION,
        "active_observation_comment_id": E3_ACTIVE_OBSERVATION_COMMENT_ID,
        "active_receipt_comment_id": E3_ACTIVE_RECEIPT_COMMENT_ID,
        "active_receipt_canonical_sha256": E3_ACTIVE_RECEIPT_SHA256,
        "superseded_observation_comment_id": E3_SUPERSEDED_OBSERVATION_COMMENT_ID,
        "superseded_receipt_comment_id": E3_SUPERSEDED_RECEIPT_COMMENT_ID,
        "authority_boundary": AUTHORITY_BOUNDARY,
    }
    if any(record.get(key) != expected_value for key, expected_value in expected.items()):
        _add(blocking, "e3-candidate-merge-identity-mismatch")
    if tuple(_sequence(record.get("merge_parents"))) != E3_MERGE_PARENTS:
        _add(blocking, "e3-merge-parent-mismatch")
    if (
        record.get("candidate_is_merge_parent") is not True
        or record.get("source_main_base_is_merge_parent") is not True
        or record.get("base_is_merge_parent") is False
    ):
        _add(blocking, "e3-merge-parent-mismatch")
    if record.get("candidate_tree_sha") != record.get("merge_tree_sha"):
        _add(blocking, "e3-merge-tree-mismatch")
    if record.get("candidate_to_merge_changed_path_count") != 0:
        _add(blocking, "e3-artifact-drift")


def _validate_e3_external(value: Any, blocking: list[str]) -> None:
    record = _mapping(value)
    if not _exact_header(record, E3_EXTERNAL_EVIDENCE_SCHEMA_VERSION, "e3-external-evidence"):
        _add(blocking, "malformed-e3-continuity-evidence")
        return
    expected = {
        "source_issue": E3_SOURCE_ISSUE,
        "implementation_pr": E3_PULL_REQUEST_NUMBER,
        "candidate_sha": E3_CANDIDATE_SHA,
        "active_observation_comment_id": E3_ACTIVE_OBSERVATION_COMMENT_ID,
        "active_observation_reference": (
            "https://github.com/aa-os/aaos-public/pull/251#issuecomment-5017872695"
        ),
        "active_receipt_comment_id": E3_ACTIVE_RECEIPT_COMMENT_ID,
        "active_receipt_reference": (
            "https://github.com/aa-os/aaos-public/pull/251#issuecomment-5017894934"
        ),
        "active_receipt_canonical_sha256": E3_ACTIVE_RECEIPT_SHA256,
        "superseded_observation_comment_id": E3_SUPERSEDED_OBSERVATION_COMMENT_ID,
        "superseded_receipt_comment_id": E3_SUPERSEDED_RECEIPT_COMMENT_ID,
        "superseded_observation_classification": SUPERSEDED_CLASSIFICATION,
        "superseded_receipt_classification": SUPERSEDED_CLASSIFICATION,
        "superseded_observation_accepted_as_active": False,
        "superseded_receipt_accepted_as_active": False,
        "external_evidence_is_completion_authority": False,
        "external_evidence_is_release_authority": False,
        "active_observation_is_superseded": False,
        "active_receipt_is_superseded": False,
        "authority_boundary": AUTHORITY_BOUNDARY,
    }
    if any(record.get(key) != expected_value for key, expected_value in expected.items()):
        _add(blocking, "malformed-e3-continuity-evidence")
    if record.get("active_observation_comment_id") == E3_SUPERSEDED_OBSERVATION_COMMENT_ID:
        _add(blocking, "superseded-e3-observation-used")
    if record.get("active_receipt_comment_id") == E3_SUPERSEDED_RECEIPT_COMMENT_ID:
        _add(blocking, "superseded-e3-receipt-used")
    if record.get("active_receipt_canonical_sha256") != E3_ACTIVE_RECEIPT_SHA256:
        _add(blocking, "active-e3-receipt-digest-mismatch")


def _validate_acceptance(value: Any, blocking: list[str]) -> bool:
    matrix = _mapping(value)
    local: list[str] = []
    if not _exact_header(matrix, ACCEPTANCE_MATRIX_SCHEMA_VERSION, "acceptance-coverage-matrix"):
        _add(local, "acceptance-matrix-invalid")
    criteria = _sequence(matrix.get("criteria"))
    if matrix.get("parent_tracker") != PARENT_TRACKER or matrix.get("criterion_count") != 16 or len(criteria) != 16:
        _add(local, "omitted-acceptance-criterion")
    for index, item in enumerate(criteria):
        row = _mapping(item)
        if index >= len(EXPECTED_ACCEPTANCE_CRITERIA):
            _add(local, "substituted-acceptance-evidence")
            continue
        observed = (
            row.get("criterion_id"), row.get("criterion_text"), row.get("source_track"),
            tuple(_sequence(row.get("evidence_references"))),
            tuple(_sequence(row.get("artifact_references"))),
            tuple(_sequence(row.get("test_references"))), row.get("authority_boundary"),
        )
        if observed != EXPECTED_ACCEPTANCE_CRITERIA[index]:
            _add(local, "substituted-acceptance-evidence")
        if row.get("coverage_state") != "covered" or row.get("notes") != EXPECTED_ACCEPTANCE_NOTE:
            _add(local, "incomplete-acceptance-criteria-coverage")
    for finding in local:
        _add(blocking, finding)
    return not local


def _normalize_register(value: Any, id_field: str) -> tuple[tuple[Any, ...], ...]:
    return tuple(
        (
            row.get(id_field), row.get("state"),
            tuple(_sequence(row.get("evidence_references"))), row.get("explanation"),
        )
        for row in (_mapping(item) for item in _sequence(value))
    )


def _validate_transition_register(value: Any, blocking: list[str]) -> None:
    register = _mapping(value)
    if not _exact_header(register, TRANSITION_REGISTER_SCHEMA_VERSION, "transition-register"):
        _add(blocking, "transition-register-invalid")
        return
    if _normalize_register(register.get("blocking_conditions"), "condition_id") != EXPECTED_BLOCKER_REGISTRY:
        _add(blocking, "hidden-completion-blocker")
    if _normalize_register(register.get("readiness_requirements"), "finding_id") != EXPECTED_READINESS_REGISTRY:
        _add(blocking, "readiness-register-mismatch")
    expected = {
        "tracker_231_state_before_merge": "open",
        "issue_252_state_before_merge": "open",
        "m15_state_before_merge": "active-and-incomplete",
        "tag_state_before_merge": "absent-not-created",
        "github_release_state_before_merge": "absent-not-published",
        "authority_boundary": AUTHORITY_BOUNDARY,
    }
    if any(register.get(key) != expected_value for key, expected_value in expected.items()):
        _add(blocking, "premature-completion-or-publication-claim")


def _validate_readme(value: Any, blocking: list[str], readiness: list[str]) -> Mapping[str, Any]:
    record = _mapping(value)
    if not record:
        _add(readiness, "missing-readme-transition-observation")
        return {}
    if not _exact_header(record, README_TRANSITION_SCHEMA_VERSION, "readme-transition-observation"):
        _add(blocking, "readme-final-transition-drift")
        return record
    digests = (
        "base_readme_sha256", "candidate_readme_sha256",
        "base_releases_section_sha256", "candidate_releases_section_sha256",
        "base_current_baseline_section_sha256", "candidate_current_baseline_section_sha256",
        "base_current_status_section_sha256", "candidate_current_status_section_sha256",
        "base_next_phase_section_sha256", "candidate_next_phase_section_sha256",
    )
    if any(not _sha(record.get(field), 64) for field in digests):
        _add(blocking, "readme-final-transition-drift")
    expected = {
        "source_main_base_sha": SOURCE_MAIN_BASE_SHA,
        "releases_changed": True,
        "current_baseline_changed": True,
        "current_status_changed": True,
        "next_phase_changed": True,
        "unrelated_sections_unchanged": True,
        "m15_repository_completion_claim": True,
        "v0_14_0_release_state_entry_present": True,
        "v0_14_0_tag_exists_claim": False,
        "github_release_published_claim": False,
        "tag_target_rule": "exact-e4-merge-commit-after-merge",
        "decision_proof_sealed": False,
        "learning_proof_sealed": False,
        "authority_boundary": AUTHORITY_BOUNDARY,
    }
    if any(record.get(key) != expected_value for key, expected_value in expected.items()):
        _add(blocking, "readme-final-transition-drift")
    if record.get("v0_14_0_tag_exists_claim") is not False:
        _add(blocking, "premature-tag-created-claim")
    if record.get("github_release_published_claim") is not False:
        _add(blocking, "premature-github-release-published-claim")
    return record


def _validate_release_preparation(value: Any, blocking: list[str], readiness: list[str]) -> Mapping[str, Any]:
    record = _mapping(value)
    if not record:
        _add(readiness, "missing-release-target-preparation")
        _add(readiness, "missing-release-notes")
        _add(readiness, "missing-publication-checklist")
        return {}
    if not _exact_header(record, RELEASE_PREPARATION_SCHEMA_VERSION, "release-preparation-record"):
        _add(blocking, "release-preparation-invalid")
        return record
    expected = {
        "source_issue": SOURCE_ISSUE,
        "parent_tracker": PARENT_TRACKER,
        "pull_request_number": E4_PULL_REQUEST_NUMBER,
        "release_version": "v0.14.0",
        "release_title": "M15 Learning Sovereignty and Evidence-Bound Capability Memory",
        "final_candidate_binding": "commit-external-active-pr-observation",
        "future_merge_commit": "post-merge-placeholder",
        "expected_merge_method": "merge-commit",
        "tag_target_rule": "exact-e4-merge-commit",
        "tag_state_before_merge": "absent-not-created",
        "github_release_state_before_merge": "absent-not-published",
        "publication_authority": "human-controlled-post-merge-action",
        "candidate_head_is_tag_target": False,
        "non_authoritative_boundary_statement": NON_AUTHORITATIVE_RELEASE_BOUNDARY,
    }
    if any(record.get(key) != expected_value for key, expected_value in expected.items()):
        _add(blocking, "release-preparation-binding-mismatch")
    if record.get("tag_state_before_merge") != "absent-not-created":
        _add(blocking, "premature-tag-created-claim")
    if record.get("github_release_state_before_merge") != "absent-not-published":
        _add(blocking, "premature-github-release-published-claim")
    if record.get("tag_target_rule") != "exact-e4-merge-commit":
        _add(blocking, "candidate-head-as-final-tag-target")
    if (
        record.get("repository_completion_is_release_publication") is not False
        or record.get("publication_is_governance_approval") is not False
    ):
        _add(blocking, "completion-publication-conflation")
    if not record.get("release_notes_reference"):
        _add(readiness, "missing-release-notes")
    if not record.get("publication_checklist_reference"):
        _add(readiness, "missing-publication-checklist")
    if not record.get("publication_checklist"):
        _add(readiness, "missing-publication-checklist")
    return record


def _validate_pr_observation(value: Any, blocking: list[str], readiness: list[str]) -> Mapping[str, Any]:
    record = _mapping(value)
    if not record:
        _add(readiness, "missing-final-pr-observation")
        return {}
    if not _exact_header(
        record,
        PR_OBSERVATION_SCHEMA_VERSION,
        "pull-request-candidate-observation",
    ):
        _add(blocking, "pr-observation-invalid")
        return record
    expected = {
        "issue_number": SOURCE_ISSUE,
        "parent_tracker": PARENT_TRACKER,
        "pull_request_number": E4_PULL_REQUEST_NUMBER,
        "source_main_base_sha": SOURCE_MAIN_BASE_SHA,
        "source_main_base_tree_sha": SOURCE_MAIN_BASE_TREE_SHA,
        "execution_subject_type": "pull-request-candidate-checkout",
        "external_to_candidate_commit": True,
        "fetched_by_evaluator": False,
        "non_authoritative_boundary_statement": PR_OBSERVATION_BOUNDARY,
    }
    if any(record.get(key) != expected_value for key, expected_value in expected.items()):
        _add(blocking, "pr-observation-binding-mismatch")
    if not _sha(record.get("candidate_head_sha"), 40) or record.get("candidate_head_sha") == SOURCE_MAIN_BASE_SHA:
        _add(blocking, "pr-observation-candidate-invalid")
    if not _sha(record.get("candidate_tree_sha"), 40):
        _add(blocking, "pr-observation-tree-invalid")
    reference = record.get("evidence_reference")
    if reference != E4_PR_OBSERVATION_EVIDENCE_REFERENCE:
        _add(blocking, "pr-observation-reference-mismatch")
    if not _timestamp(record.get("observed_at")) or not record.get("observer"):
        _add(blocking, "pr-observation-metadata-invalid")
    return record


def _validate_receipt(value: Any, observation: Mapping[str, Any], blocking: list[str], readiness: list[str]) -> Mapping[str, Any]:
    receipt = _mapping(value)
    if not receipt:
        _add(readiness, "missing-final-verification-receipt")
        _add(readiness, "incomplete-test-execution")
        return {}
    if not _exact_header(
        receipt,
        VERIFICATION_RECEIPT_SCHEMA_VERSION,
        "external-verification-execution-receipt",
    ):
        _add(blocking, "verification-receipt-invalid")
        return receipt
    expected = {
        "issue_number": SOURCE_ISSUE,
        "parent_tracker": PARENT_TRACKER,
        "pull_request_number": E4_PULL_REQUEST_NUMBER,
        "source_main_base_sha": SOURCE_MAIN_BASE_SHA,
        "external_to_candidate_commit": True,
        "executed_by_evaluator": False,
        "verification_results_are_completion_authority": False,
        "verification_results_are_release_authority": False,
        "non_authoritative_boundary_statement": VERIFICATION_BOUNDARY,
        "evidence_reference": E4_VERIFICATION_RECEIPT_EVIDENCE_REFERENCE,
    }
    if any(receipt.get(key) != expected_value for key, expected_value in expected.items()):
        _add(blocking, "verification-receipt-binding-mismatch")
    receipt_candidate_fields = (
        ("execution_candidate_head_sha", "candidate_head_sha"),
        ("execution_candidate_tree_sha", "candidate_tree_sha"),
    )
    for receipt_field, observation_field in receipt_candidate_fields:
        if receipt.get(receipt_field) != observation.get(observation_field):
            _add(blocking, "verification-observation-candidate-mismatch")
    if receipt.get("observation_evidence_reference") != observation.get("evidence_reference"):
        _add(blocking, "pr-observation-receipt-reference-mismatch")
    commands = _sequence(receipt.get("commands"))
    if receipt.get("command_receipt_count") != len(EXPECTED_VERIFICATION_COMMANDS):
        _add(blocking, "insufficient-verification-coverage")
    if len(commands) != len(EXPECTED_VERIFICATION_COMMANDS):
        _add(blocking, "insufficient-verification-coverage")
    for index, expected_command in enumerate(EXPECTED_VERIFICATION_COMMANDS):
        if index >= len(commands):
            break
        row = _mapping(commands[index])
        command_id, logical_argv, scope, minimum = expected_command
        if (
            row.get("command_id") != command_id
            or tuple(_sequence(row.get("declared_logical_argv"))) != logical_argv
            or row.get("execution_scope") != scope
            or row.get("minimum_tests_observed") != minimum
        ):
            _add(blocking, "verification-command-registry-mismatch")
        actual_argv = tuple(_sequence(row.get("actual_argv")))
        executable_binding = _mapping(row.get("executable_binding"))
        launcher = executable_binding.get("actual_launcher")
        if (
            len(actual_argv) != len(logical_argv)
            or not actual_argv
            or actual_argv[0] != launcher
            or actual_argv[1:] != logical_argv[1:]
            or not isinstance(launcher, str)
            or not launcher.replace("\\", "/").endswith(".verification-python/python.exe")
        ):
            _add(blocking, "verification-actual-argv-mismatch")
        counts = tuple(row.get(field) for field in ("tests_observed", "passes", "failures", "errors", "skips", "exit_code"))
        if any(not isinstance(item, int) or isinstance(item, bool) or item < 0 for item in counts):
            _add(blocking, "verification-counts-invalid")
            continue
        tests, passes, failures, errors, skips, exit_code = counts
        if tests < minimum:
            _add(blocking, "insufficient-verification-coverage")
        if passes + failures + errors + skips != tests:
            _add(blocking, "verification-counts-invalid")
        if failures or errors or skips or exit_code:
            _add(blocking, "verification-execution-not-clean")
            _add(blocking, "insufficient-verification-coverage")
        if row.get("execution_candidate_head_sha") != observation.get("candidate_head_sha"):
            _add(blocking, "verification-candidate-mismatch")
        if (
            row.get("executed_by_evaluator") is not False
            or row.get("verification_results_are_completion_authority") is not False
            or row.get("verification_results_are_release_authority") is not False
            or not _timestamp(row.get("execution_timestamp"))
            or not _sha(row.get("transcript_sha256"), 64)
            or not row.get("evidence_reference")
            or executable_binding.get("declared_launcher") != "python"
            or executable_binding.get("launcher_substitution_detected") is not True
            or executable_binding.get("launcher_substitution_declared") is not True
            or not executable_binding.get("python_implementation")
            or not executable_binding.get("python_version")
        ):
            _add(blocking, "verification-command-metadata-invalid")
    if not _sha(receipt.get("canonical_payload_sha256"), 64):
        _add(blocking, "verification-receipt-digest-invalid")
    return receipt


def _validate_human_approval(
    value: Any,
    observation: Mapping[str, Any],
    receipt: Mapping[str, Any],
    readme: Mapping[str, Any],
    blocking: list[str],
    readiness: list[str],
) -> Mapping[str, Any]:
    approval = _mapping(value)
    if not approval:
        _add(readiness, "missing-human-approval")
        _add(readiness, "missing-approval-timestamp")
        _add(readiness, "missing-approval-receipt-binding")
        _add(readiness, "missing-approval-candidate-binding")
        return {}
    if not _exact_header(
        approval,
        HUMAN_APPROVAL_SCHEMA_VERSION,
        "commit-external-human-approval-observation",
    ):
        _add(blocking, "human-approval-invalid")
        return approval
    expected = {
        "issue_number": SOURCE_ISSUE,
        "parent_tracker": PARENT_TRACKER,
        "pull_request_number": E4_PULL_REQUEST_NUMBER,
        "source_main_base_sha": SOURCE_MAIN_BASE_SHA,
        "pr_observation_reference": observation.get("evidence_reference"),
        "verification_receipt_reference": receipt.get("evidence_reference"),
        "reviewed_readme_transition_sha256": readme.get("candidate_readme_sha256"),
        "reviewed_completion_state_sha256": readme.get(
            "candidate_completion_state_sha256"
        ),
        "intended_merge_method": "merge-commit",
        "permitted_issue_closures": [SOURCE_ISSUE, PARENT_TRACKER],
        "explicit_authority_scope": HUMAN_APPROVAL_AUTHORITY_SCOPE,
        "approver_type": "human",
        "authored_by_human": True,
        "external_to_candidate_commit": True,
        "candidate_head_frozen": True,
        "approved": True,
        "tag_creation_authorized": False,
        "github_release_publication_authorized": False,
        "risk_acceptance_authorized": False,
        "audit_closure_authorized": False,
        "waiver_authorized": False,
        "authority_transfer_authorized": False,
        "decision_proof_sealing_authorized": False,
        "learning_proof_sealing_authorized": False,
        "non_authoritative_release_publication_boundary": NON_AUTHORITATIVE_RELEASE_BOUNDARY,
    }
    if any(approval.get(key) != expected_value for key, expected_value in expected.items()):
        _add(blocking, "human-approval-binding-mismatch")
    if approval.get("pull_request_number") != E4_PULL_REQUEST_NUMBER:
        _add(blocking, "human-approval-candidate-mismatch")
    if (
        approval.get("approver_type") != "human"
        or approval.get("authored_by_human") is not True
    ):
        _add(blocking, "evaluator-output-as-human-approval")
    authority_flags = (
        "tag_creation_authorized",
        "github_release_publication_authorized",
        "risk_acceptance_authorized",
        "audit_closure_authorized",
        "waiver_authorized",
        "authority_transfer_authorized",
        "decision_proof_sealing_authorized",
        "learning_proof_sealing_authorized",
    )
    if any(approval.get(field) is not False for field in authority_flags):
        _add(blocking, "authority-transfer-claim")
    for field in ("candidate_head_sha", "candidate_tree_sha"):
        if approval.get(field) != observation.get(field):
            _add(blocking, "human-approval-candidate-mismatch")
    if approval.get("verification_receipt_canonical_sha256") != receipt.get(
        "canonical_payload_sha256"
    ):
        _add(blocking, "human-approval-receipt-mismatch")
    if not _sha(approval.get("verification_receipt_canonical_sha256"), 64):
        _add(blocking, "human-approval-receipt-mismatch")
    if not _sha(approval.get("reviewed_completion_state_sha256"), 64):
        _add(blocking, "human-approval-completion-state-digest-invalid")
    if not _timestamp(approval.get("approval_timestamp")):
        _add(readiness, "missing-approval-timestamp")
    if not isinstance(approval.get("approver_identity"), str) or not approval.get("approver_identity").strip():
        _add(blocking, "human-approver-identity-invalid")
    return approval


def _build_result(blocking: list[str], readiness: list[str], all_criteria_covered: bool, approval_present: bool) -> dict[str, Any]:
    blocking_findings = sorted(set(blocking))
    readiness_findings = sorted(set(readiness))
    outcome = BLOCKED if blocking_findings else (NOT_READY if readiness_findings else READY)
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "outcome": outcome,
        "ready_for_human_m15_completion_transition": outcome == READY,
        "blocking_findings": blocking_findings,
        "readiness_findings": readiness_findings,
        "all_criteria_covered": all_criteria_covered,
        "human_approval_present": approval_present,
        "caller_data_only": True,
        "file_io_performed": False,
        "git_inspection_performed": False,
        "github_access_performed": False,
        "network_access_performed": False,
        "subprocess_executed": False,
        "repository_digests_calculated": False,
        "receipt_digests_calculated": False,
        "verification_commands_executed": False,
        "external_state_mutated": False,
        "merge_executed": False,
        "m15_state": "active-and-incomplete",
        "tracker_231_state": "open",
        "issue_252_state": "open",
        "v0_14_0_state": "repository-release-state-proposed-publication-pending",
        "tag_state": "not-created",
        "github_release_state": "not-published",
        "decision_proof_sealed": False,
        "learning_proof_sealed": False,
    }


def evaluate_final_completion(
    final_completion_manifest: Mapping[str, Any],
    track_evidence_inventory: Mapping[str, Any],
    e3_continuity_record: Mapping[str, Any],
    e3_external_evidence: Mapping[str, Any],
    acceptance_coverage_matrix: Mapping[str, Any],
    transition_register: Mapping[str, Any],
    readme_transition_observation: Mapping[str, Any],
    release_preparation_record: Mapping[str, Any],
    pull_request_observation: Mapping[str, Any],
    external_verification_receipt: Mapping[str, Any],
    human_approval_observation: Mapping[str, Any],
) -> dict[str, Any]:
    """Evaluate eleven inert mappings without performing external operations."""

    blocking: list[str] = []
    readiness: list[str] = []
    values = (
        final_completion_manifest, track_evidence_inventory,
        e3_continuity_record, e3_external_evidence,
        acceptance_coverage_matrix, transition_register,
        readme_transition_observation, release_preparation_record,
        pull_request_observation, external_verification_receipt,
        human_approval_observation,
    )
    for value in values:
        _authority_findings(value, blocking)
    _validate_manifest(final_completion_manifest, blocking)
    _validate_inventory(track_evidence_inventory, blocking)
    _validate_e3_continuity(e3_continuity_record, blocking)
    _validate_e3_external(e3_external_evidence, blocking)
    all_criteria_covered = _validate_acceptance(acceptance_coverage_matrix, blocking)
    _validate_transition_register(transition_register, blocking)
    readme = _validate_readme(readme_transition_observation, blocking, readiness)
    _validate_release_preparation(release_preparation_record, blocking, readiness)
    observation = _validate_pr_observation(pull_request_observation, blocking, readiness)
    receipt = _validate_receipt(external_verification_receipt, observation, blocking, readiness)
    approval = _validate_human_approval(
        human_approval_observation, observation, receipt, readme, blocking, readiness
    )
    return _build_result(blocking, readiness, all_criteria_covered, bool(approval))


evaluate_final_completion_readiness = evaluate_final_completion


__all__ = [
    "ACCEPTANCE_BINDING_FIELDS", "ACCEPTANCE_MATRIX_SCHEMA_VERSION",
    "ARTIFACT_BINDING_FIELDS", "AUTHORITY_BOUNDARY", "BLOCKED",
    "COMMAND_IDS", "COMMAND_MINIMA", "CRITERION_IDS",
    "E3_ACTIVE_OBSERVATION_COMMENT_ID", "E3_ACTIVE_RECEIPT_COMMENT_ID",
    "E3_ACTIVE_RECEIPT_SHA256", "E3_CANDIDATE_SHA", "E3_CANDIDATE_TREE_SHA",
    "E3_CONTINUITY_SCHEMA_VERSION", "E3_EXTERNAL_EVIDENCE_SCHEMA_VERSION",
    "E3_MERGE_PARENTS", "E3_MERGE_SHA", "E3_MERGE_TREE_SHA",
    "E3_RELATION", "E3_SUPERSEDED_OBSERVATION_COMMENT_ID",
    "E3_SUPERSEDED_RECEIPT_COMMENT_ID", "E4_PULL_REQUEST_NUMBER",
    "E4_PR_OBSERVATION_EVIDENCE_REFERENCE",
    "E4_VERIFICATION_RECEIPT_EVIDENCE_REFERENCE",
    "EXPECTED_ACCEPTANCE_CRITERIA", "EXPECTED_ARTIFACT_BINDINGS",
    "EXPECTED_BLOCKER_REGISTRY", "EXPECTED_READINESS_REGISTRY",
    "EXPECTED_VERIFICATION_COMMANDS", "HUMAN_APPROVAL_AUTHORITY_SCOPE",
    "HISTORICAL_ARTIFACT_AUTHORITY_BOUNDARY",
    "HUMAN_APPROVAL_SCHEMA_VERSION", "MANIFEST_SCHEMA_VERSION",
    "NON_AUTHORITATIVE_RELEASE_BOUNDARY", "NOT_READY", "OUTCOMES",
    "PRIOR_MATERIAL_ARTIFACT_COUNT", "PR_OBSERVATION_BOUNDARY",
    "PR_OBSERVATION_SCHEMA_VERSION", "READY", "README_TRANSITION_SCHEMA_VERSION",
    "RELEASE_PREPARATION_SCHEMA_VERSION", "REQUIRED_BLOCKERS",
    "REQUIRED_READINESS_FINDINGS", "RUNTIME_BOUNDARY", "SCENARIO_SCHEMA_VERSION",
    "SOURCE_MAIN_BASE_SHA", "SOURCE_MAIN_BASE_TREE_SHA", "TRACK_COUNTS",
    "TRACK_EVIDENCE_SCHEMA_VERSION", "TRANSITION_REGISTER_SCHEMA_VERSION",
    "VERIFICATION_BOUNDARY", "VERIFICATION_RECEIPT_SCHEMA_VERSION",
    "evaluate_final_completion", "evaluate_final_completion_readiness",
]
