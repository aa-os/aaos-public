"""Deterministic caller-data-only evaluator for M15 Track E3.

The evaluator consumes nine inert mappings.  It performs no file, Git, GitHub,
network, process, command, digest, or external-state operation.
"""

from collections.abc import Mapping, Sequence
from typing import Any


MANIFEST_SCHEMA_VERSION = "m15-completion-readiness/v1"
TRACK_EVIDENCE_SCHEMA_VERSION = "m15-completion-readiness-track-evidence/v1"
E2_CONTINUITY_SCHEMA_VERSION = "m15-completion-readiness-e2-continuity/v1"
E2_EXTERNAL_EVIDENCE_SCHEMA_VERSION = (
    "m15-completion-readiness-e2-external-evidence/v1"
)
ACCEPTANCE_MATRIX_SCHEMA_VERSION = (
    "m15-completion-readiness-acceptance-matrix/v1"
)
BOUNDARY_REGISTER_SCHEMA_VERSION = (
    "m15-completion-readiness-boundary-register/v1"
)
README_OBSERVATION_SCHEMA_VERSION = (
    "m15-completion-readiness-readme-observation/v1"
)
PR_OBSERVATION_SCHEMA_VERSION = "m15-completion-readiness-pr-observation/v1"
VERIFICATION_RECEIPT_SCHEMA_VERSION = (
    "m15-completion-readiness-verification-receipt/v1"
)
SCENARIO_SCHEMA_VERSION = "m15-completion-readiness-scenario/v1"
RESULT_SCHEMA_VERSION = "m15-completion-readiness-result/v1"

READY = "ready_for_final_m15_completion_review"
NOT_READY = "not_ready"
BLOCKED = "blocked"
OUTCOMES = (READY, NOT_READY, BLOCKED)

REPOSITORY = "aa-os/aaos-public"
SOURCE_ISSUE = 250
PARENT_TRACKER = 231
E3_PULL_REQUEST_NUMBER = 251
E3_PR_OBSERVATION_EVIDENCE_REFERENCE = (
    "github:aa-os/aaos-public:pull/251:commit-external-observation"
)
SOURCE_MAIN_BASE_SHA = "f6d074fca2fedecbf654697719179440bc0680d3"
SOURCE_MAIN_BASE_TREE_SHA = "f13913426545b77616128223cd195487a415ffde"

E2_SOURCE_MAIN_BASE_SHA = "27c92e290cf6ad60bada49b63fe1888511930980"
E2_CANDIDATE_SHA = "efc31e7d24c26d2cea2cb536a4cae257aababb5f"
E2_CANDIDATE_TREE_SHA = "f13913426545b77616128223cd195487a415ffde"
E2_MERGE_SHA = "f6d074fca2fedecbf654697719179440bc0680d3"
E2_MERGE_TREE_SHA = "f13913426545b77616128223cd195487a415ffde"
E2_MERGE_PARENTS = (E2_SOURCE_MAIN_BASE_SHA, E2_CANDIDATE_SHA)
E2_RELATION = "exact_tree_match"
E2_OBSERVATION_COMMENT_ID = 5015690597
E2_ACTIVE_RECEIPT_COMMENT_ID = 5015694989
E2_ACTIVE_RECEIPT_SHA256 = (
    "511226a39144791ec47043203878bd22d14ec546e71702c267b66cc47da6af2f"
)
E2_SUPERSEDED_RECEIPT_COMMENT_ID = 5015466792
E2_SUPERSEDED_CLASSIFICATION = "superseded-historical-evidence"

PRIOR_MATERIAL_ARTIFACT_COUNT = 156
TRACK_COUNTS = {
    "track-a": 7,
    "track-b": 13,
    "track-c": 18,
    "track-d": 29,
    "track-e1": 39,
    "track-e2": 50,
}
TRACK_BINDINGS = {
    "track-a": (
        232,
        233,
        "603a26890ceee940b0a3c9009e06d994f9f2f342",
        "6e0fa4e8fdf4a672581cd897d52743d0462f0d4b",
    ),
    "track-b": (
        234,
        237,
        "270a5bbb536c6bf0726e95455d4bb61ac86d693e",
        "8e475518f2da6232ae9a6264d8e9c9f1e5fc514a",
    ),
    "track-c": (
        238,
        239,
        "5f98f6c86e6b61d50b1c8183aca0736a3419c533",
        "2d8bab3a84675543c34231a9e04521379febdac1",
    ),
    "track-d": (
        240,
        241,
        "3bec19e42693b757b9abbb077146ca9860d48c1e",
        "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f",
    ),
    "track-e1": (
        242,
        243,
        "55629976db7f7b8dc9e2153eaf67f054bd9ee708",
        "27c92e290cf6ad60bada49b63fe1888511930980",
    ),
    "track-e2": (
        248,
        249,
        E2_CANDIDATE_SHA,
        E2_MERGE_SHA,
    ),
}
TRACK_SUMMARY_BINDINGS = {
    "track-a": {
        "source_issue": 232,
        "implementation_pr": 233,
        "base_sha": "b99b62761de9a6fdfceafd3c0d60698ba94c8f40",
        "candidate_sha": "603a26890ceee940b0a3c9009e06d994f9f2f342",
        "candidate_tree_sha": "fa7c5603810a05e0ec093ae7b06363ec56019e53",
        "merge_sha": "6e0fa4e8fdf4a672581cd897d52743d0462f0d4b",
        "merge_tree_sha": "fa7c5603810a05e0ec093ae7b06363ec56019e53",
        "material_path_count": 7,
    },
    "track-b": {
        "source_issue": 234,
        "implementation_pr": 237,
        "base_sha": "3c98a1e2b34f394097054f91102d3346d6aa9810",
        "candidate_sha": "270a5bbb536c6bf0726e95455d4bb61ac86d693e",
        "candidate_tree_sha": "ff32997c992c6d288fadd598c64634aba58aed28",
        "merge_sha": "8e475518f2da6232ae9a6264d8e9c9f1e5fc514a",
        "merge_tree_sha": "7fec07ff0b346f76c885303d98fec4c5b8372149",
        "material_path_count": 13,
    },
    "track-c": {
        "source_issue": 238,
        "implementation_pr": 239,
        "base_sha": "8e475518f2da6232ae9a6264d8e9c9f1e5fc514a",
        "candidate_sha": "5f98f6c86e6b61d50b1c8183aca0736a3419c533",
        "candidate_tree_sha": "253d64dd203741a213e34afaa501218a362c88e7",
        "merge_sha": "2d8bab3a84675543c34231a9e04521379febdac1",
        "merge_tree_sha": "253d64dd203741a213e34afaa501218a362c88e7",
        "material_path_count": 18,
    },
    "track-d": {
        "source_issue": 240,
        "implementation_pr": 241,
        "base_sha": "2d8bab3a84675543c34231a9e04521379febdac1",
        "candidate_sha": "3bec19e42693b757b9abbb077146ca9860d48c1e",
        "candidate_tree_sha": "a0277b8cb697c9e311118f7de67f7f6bf3534fcb",
        "merge_sha": "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f",
        "merge_tree_sha": "a0277b8cb697c9e311118f7de67f7f6bf3534fcb",
        "material_path_count": 29,
    },
    "track-e1": {
        "source_issue": 242,
        "implementation_pr": 243,
        "base_sha": "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f",
        "candidate_sha": "55629976db7f7b8dc9e2153eaf67f054bd9ee708",
        "candidate_tree_sha": "f4552f630e2dab5b9d34240efa8825f187b4abf1",
        "merge_sha": "27c92e290cf6ad60bada49b63fe1888511930980",
        "merge_tree_sha": "f4552f630e2dab5b9d34240efa8825f187b4abf1",
        "material_path_count": 39,
    },
    "track-e2": {
        "source_issue": 248,
        "implementation_pr": 249,
        "base_sha": E2_SOURCE_MAIN_BASE_SHA,
        "candidate_sha": E2_CANDIDATE_SHA,
        "candidate_tree_sha": E2_CANDIDATE_TREE_SHA,
        "merge_sha": E2_MERGE_SHA,
        "merge_tree_sha": E2_MERGE_TREE_SHA,
        "material_path_count": 50,
    },
}
AUTHORIZED_HISTORICAL_COMPATIBILITY_REPAIRS = (
    {
        "path": "runtime/m14_final_completion_evaluator.py",
        "purpose": "phase-aware-next-phase-validation",
        "counted_in_prior_material_artifact_inventory": False,
    },
    {
        "path": "tests/test_m14_final_completion_evaluator.py",
        "purpose": "explicit-historical-mutation-fixtures",
        "counted_in_prior_material_artifact_inventory": False,
    },
    {
        "path": "tests/test_m15_lineage_rollback_portability_evaluator.py",
        "purpose": "section-aware-future-version-assertions",
        "counted_in_prior_material_artifact_inventory": False,
    },
    {
        "path": "tests/test_m15_operational_readiness_evaluator.py",
        "purpose": "historical-source-baseline-artifact-observation",
        "counted_in_prior_material_artifact_inventory": False,
    },
)
E1_SOURCE_BASELINE_SHA = "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f"
TRACK_C_HISTORICAL_TEST_PATH = (
    "tests/test_m15_lineage_rollback_portability_evaluator.py"
)
TRACK_C_HISTORICAL_CANONICAL_SHA256 = (
    "5268f73a441898467e9b8f9471cfc4b9bd4fa27b7b67444fbf852d697d90f4c9"
)
TRACK_C_E3_COMPATIBILITY_CANONICAL_SHA256 = (
    "0dee39fe81189fd558f136732579995245828bc6b14c9791b67c9bb6e8a39f5c"
)
HISTORICAL_E1_ARTIFACT_BINDING = {
    "path": TRACK_C_HISTORICAL_TEST_PATH,
    "source_baseline_commit_sha": E1_SOURCE_BASELINE_SHA,
    "historical_canonical_sha256": TRACK_C_HISTORICAL_CANONICAL_SHA256,
    "evidence_role": "immutable-e1-source-baseline-evidence",
}
E3_AUTHORIZED_COMPATIBILITY_REPAIR = {
    "path": TRACK_C_HISTORICAL_TEST_PATH,
    "current_candidate_canonical_sha256": (
        TRACK_C_E3_COMPATIBILITY_CANONICAL_SHA256
    ),
    "purpose": "section-aware-future-version-assertions",
    "authority": "human-approved-bounded-e3-compatibility-repair",
}
COMPATIBILITY_REPAIR_PURPOSE = "phase-aware historical README regression repair"
COMPATIBILITY_REPAIR_AUTHORIZATION_BASIS = (
    "human-approved bounded scope exception for Issue #250"
)
COMPATIBILITY_REPAIR_NOT_AUTHORIZED = (
    "release-state modification",
    "M14 reopening",
    "authority-doctrine change",
    "test deletion",
    "unconditional skip",
    "arbitrary historical evaluator cleanup",
    "external adapter scope",
)
AUTHORIZED_PHASE_AWARE_COMPATIBILITY_REPAIR = {
    "purpose": COMPATIBILITY_REPAIR_PURPOSE,
    "authorization_basis": COMPATIBILITY_REPAIR_AUTHORIZATION_BASIS,
    "not_authorized": list(COMPATIBILITY_REPAIR_NOT_AUTHORIZED),
}
INVENTORY_BINDING_SHA256 = (
    "e3d92da9c09192153383ce447f8b1beaeda5001c468fd9d79b8babcd435aff26"
)

CRITERION_IDS = tuple(f"m15-ac-{number:02d}" for number in range(1, 17))
REQUIRED_BLOCKERS = (
    "missing-track-a-evidence",
    "missing-track-b-evidence",
    "missing-track-c-evidence",
    "missing-track-d-evidence",
    "missing-track-e1-evidence",
    "missing-track-e2-evidence",
    "e2-candidate-merge-mismatch",
    "missing-e2-pr-observation",
    "missing-active-e2-receipt",
    "superseded-e2-receipt-used",
    "e2-receipt-digest-mismatch",
    "incomplete-acceptance-criteria-coverage",
    "hidden-completion-blocker",
    "invalid-future-readme-path",
    "incomplete-verification-coverage",
    "authority-boundary-violation",
)
REQUIRED_FUTURE_PREREQUISITES = (
    "track-e4-not-completed",
    "final-m15-completion-not-approved",
    "tracker-231-open",
    "readme-final-completion-not-authorized",
    "v0.14.0-tag-not-authorized",
    "github-release-not-authorized",
    "post-merge-final-review-not-completed",
)

BLOCKER_RESOLUTION_EXPLANATION = (
    "Resolved by the maintained inert evidence package; this does not resolve "
    "or authorize any future prerequisite."
)
FUTURE_PREREQUISITE_EXPLANATION = (
    "Remains open after E3 and cannot be interpreted as completed or authorized "
    "by a readiness outcome."
)
EXPECTED_BLOCKER_REGISTRY = tuple(
    (
        blocker_id,
        "resolved",
        (f"urn:aaos:m15:e3:blocker-evidence:{blocker_id}",),
        BLOCKER_RESOLUTION_EXPLANATION,
    )
    for blocker_id in REQUIRED_BLOCKERS
)
EXPECTED_FUTURE_PREREQUISITE_REGISTRY = tuple(
    (
        prerequisite_id,
        "open",
        (f"urn:aaos:m15:e3:future-prerequisite:{prerequisite_id}",),
        FUTURE_PREREQUISITE_EXPLANATION,
    )
    for prerequisite_id in REQUIRED_FUTURE_PREREQUISITES
)

# Bound to the discoverable focused E3 suite and prior maintained baseline.
E3_TARGETED_MINIMUM = 167
FULL_SUITE_MINIMUM = 2092
# Immutable registry for every maintained verification command.
EXPECTED_VERIFICATION_COMMANDS = (
    ("e3-targeted", ("python", "-X", "faulthandler", "-m", "unittest", "tests.test_m15_completion_readiness_evaluator", "-v"), "e3-candidate-validation", 167),
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
    ("full-maintained-suite", ("python", "-X", "faulthandler", "-m", "unittest", "discover", "-s", "tests", "-v"), "candidate-full-suite-integration", 2092),
    ("m14-final-completion", ("python", "-X", "faulthandler", "-m", "unittest", "tests.test_m14_final_completion_evaluator", "-v"), "authorized-compatibility-regression", 110),
    ("m14-completion-readiness", ("python", "-X", "faulthandler", "-m", "unittest", "tests.test_m14_completion_readiness_evaluator", "-v"), "authorized-compatibility-regression", 112),
)
COMMAND_IDS = tuple(item[0] for item in EXPECTED_VERIFICATION_COMMANDS)
COMMAND_MINIMA = {item[0]: item[3] for item in EXPECTED_VERIFICATION_COMMANDS}

BASE_README_SHA256 = (
    "bc4ba48a8ad986d8865d48623c83ad70c4a8fdfcee27ae17da456115fc413d43"
)
CANDIDATE_README_SHA256 = (
    "c4612bfd5346e69cfa51dd772bba43902368fcb06590686b6a05519e4d9b31de"
)
RELEASES_SECTION_SHA256 = (
    "47f8eaa077b16c8bf7138a22c4bb9256ee2161dc1c478009705d85ac75472453"
)
CURRENT_STATUS_SECTION_SHA256 = (
    "407818064b89453349d6e094f54ad852450dc8a33c2a82c4f4e55cf31bb5208d"
)
BASE_NEXT_PHASE_SHA256 = (
    "fe4fb31b62caedec587133fe8a00c84a59f65c0f2d640da550fbbdbf4045f529"
)
CANDIDATE_NEXT_PHASE_SHA256 = (
    "06ef31f0016717c8388bbdfbc2a04132cc060ee11566e2d6d45cfadaf99af8b4"
)

AUTHORITY_BOUNDARY = (
    "Completion readiness is evidence for final human review only; it is not "
    "M15 completion, tracker #231 closure, README final-state authorization, "
    "release approval, tag authorization, GitHub Release authorization, "
    "Decision Proof sealing, Learning Proof sealing, deployment authorization, "
    "risk acceptance, rollback execution, deletion execution, fail-closed "
    "execution, audit closure, waiver, authority transfer, or final governance "
    "judgment."
)
RUNTIME_BOUNDARY = (
    "The Track E3 runtime evaluator accepts caller-supplied inert mappings only "
    "and performs no file, Git, GitHub, network, subprocess, command, digest, "
    "or external-state operation."
)

ARTIFACT_BINDING_FIELDS = (
    "track_id",
    "source_issue",
    "implementation_pr",
    "candidate_sha",
    "merge_sha",
    "repository_path",
    "artifact_type",
    "git_blob_sha",
    "git_file_mode",
    "canonical_text_sha256",
    "covering_test",
    "lifecycle_state",
    "evidence_reference",
    "authority_boundary",
)
EXPECTED_ARTIFACT_BINDINGS = (
    ("track-a", 232, 233, "603a26890ceee940b0a3c9009e06d994f9f2f342", "6e0fa4e8fdf4a672581cd897d52743d0462f0d4b", "docs/learning-governance/m15-core-learning-proof-contract.md", "governance-contract", "47cd884ba77c616d2660bb3e6693b51ea6b35509", "100644", "b28de6f87b675e96db229a71dd0b34d54e5e065fd0f9205cb56b3018fddacae3", "tests/test_m15_learning_proof_evaluator.py", "maintained", "git-object:6e0fa4e8fdf4a672581cd897d52743d0462f0d4b:docs/learning-governance/m15-core-learning-proof-contract.md", AUTHORITY_BOUNDARY),
    ("track-a", 232, 233, "603a26890ceee940b0a3c9009e06d994f9f2f342", "6e0fa4e8fdf4a672581cd897d52743d0462f0d4b", "examples/public-integration-pack-pilot/m15-learning-proof-approved-evaluation-only.json", "synthetic-fixture", "737559accedb9dc44326236f65d5142f43b3c95a", "100644", "56209ec5b821dab72f23e02b9472de8323353d706e60ec431e147c2208316db0", "tests/test_m15_learning_proof_evaluator.py", "maintained", "git-object:6e0fa4e8fdf4a672581cd897d52743d0462f0d4b:examples/public-integration-pack-pilot/m15-learning-proof-approved-evaluation-only.json", AUTHORITY_BOUNDARY),
    ("track-a", 232, 233, "603a26890ceee940b0a3c9009e06d994f9f2f342", "6e0fa4e8fdf4a672581cd897d52743d0462f0d4b", "examples/public-integration-pack-pilot/m15-learning-proof-contaminated-quarantine.json", "synthetic-fixture", "6826200cab0a40c33f6bde642f5553f9a11e58ca", "100644", "8d1d1d46bfca7d4110978e17e7139041305b068979ee62cea939291138e91971", "tests/test_m15_learning_proof_evaluator.py", "maintained", "git-object:6e0fa4e8fdf4a672581cd897d52743d0462f0d4b:examples/public-integration-pack-pilot/m15-learning-proof-contaminated-quarantine.json", AUTHORITY_BOUNDARY),
    ("track-a", 232, 233, "603a26890ceee940b0a3c9009e06d994f9f2f342", "6e0fa4e8fdf4a672581cd897d52743d0462f0d4b", "examples/public-integration-pack-pilot/m15-learning-proof-rejected-untrusted-correction.json", "synthetic-fixture", "d765bf30d4a89e46c717bed179f7a5f85a70dc03", "100644", "bf4c915b14fd968e5f50dc8b10b70edc9a56db54a13120891b9a7fedf9203ba8", "tests/test_m15_learning_proof_evaluator.py", "maintained", "git-object:6e0fa4e8fdf4a672581cd897d52743d0462f0d4b:examples/public-integration-pack-pilot/m15-learning-proof-rejected-untrusted-correction.json", AUTHORITY_BOUNDARY),
    ("track-a", 232, 233, "603a26890ceee940b0a3c9009e06d994f9f2f342", "6e0fa4e8fdf4a672581cd897d52743d0462f0d4b", "runtime/m15_learning_proof_evaluator.py", "runtime-evaluator", "fc499debd33c5c1e6eade831d84d54137e670be3", "100644", "1f0d1eda01e3df92fba069ffd75eff34232c7bfe39f0b252b80cae2d1a2f00c8", "tests/test_m15_learning_proof_evaluator.py", "maintained", "git-object:6e0fa4e8fdf4a672581cd897d52743d0462f0d4b:runtime/m15_learning_proof_evaluator.py", AUTHORITY_BOUNDARY),
    ("track-a", 232, 233, "603a26890ceee940b0a3c9009e06d994f9f2f342", "6e0fa4e8fdf4a672581cd897d52743d0462f0d4b", "schemas/m15-learning-proof.schema.json", "json-schema", "efe1113dcdb1ea193531a55fd182c58bcfd94f5f", "100644", "c03bd734f287fae23deb7f8d3eaf2ccb501774caeccbe85d6520c57b7fdc1a44", "tests/test_m15_learning_proof_evaluator.py", "maintained", "git-object:6e0fa4e8fdf4a672581cd897d52743d0462f0d4b:schemas/m15-learning-proof.schema.json", AUTHORITY_BOUNDARY),
    ("track-a", 232, 233, "603a26890ceee940b0a3c9009e06d994f9f2f342", "6e0fa4e8fdf4a672581cd897d52743d0462f0d4b", "tests/test_m15_learning_proof_evaluator.py", "evaluator-tests", "103e103ea629ea8a58c998db9deb2e9f674192e7", "100644", "d382b1239bb623f3d165b24bda830a285f1aeaee93e53b9dc9abb8ada7b6b6c4", "tests/test_m15_learning_proof_evaluator.py", "maintained", "git-object:6e0fa4e8fdf4a672581cd897d52743d0462f0d4b:tests/test_m15_learning_proof_evaluator.py", AUTHORITY_BOUNDARY),
    ("track-b", 234, 237, "270a5bbb536c6bf0726e95455d4bb61ac86d693e", "8e475518f2da6232ae9a6264d8e9c9f1e5fc514a", "docs/learning-governance/m15-capability-memory-pack-contract.md", "governance-contract", "1dc2344f50532111f32355dfffafa56c3ec214e4", "100644", "10152aea4911711c09edbb21bb78696244f9e71fe8447d9737a907eb8a3bb9df", "tests/test_m15_capability_memory_pack_evaluator.py", "maintained", "git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:docs/learning-governance/m15-capability-memory-pack-contract.md", AUTHORITY_BOUNDARY),
    ("track-b", 234, 237, "270a5bbb536c6bf0726e95455d4bb61ac86d693e", "8e475518f2da6232ae9a6264d8e9c9f1e5fc514a", "examples/public-integration-pack-pilot/m15-capability-pack-altered-derived-specification.json", "synthetic-fixture", "7438af0d6f9c1735bf9046fd1bba570480b3e56c", "100644", "23f2502a23422d14215860d4dda5a154254365224909d4ac9a2c8a0eb8b3ed22", "tests/test_m15_capability_memory_pack_evaluator.py", "maintained", "git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:examples/public-integration-pack-pilot/m15-capability-pack-altered-derived-specification.json", AUTHORITY_BOUNDARY),
    ("track-b", 234, 237, "270a5bbb536c6bf0726e95455d4bb61ac86d693e", "8e475518f2da6232ae9a6264d8e9c9f1e5fc514a", "examples/public-integration-pack-pilot/m15-capability-pack-altered-graph.json", "synthetic-fixture", "b55b18a11d6472f3f71373cad8c68869ee995d31", "100644", "1193ba3eeb7c1462816a7b1fbf1a6d9ae16ac11a22b5c315715378d95565a564", "tests/test_m15_capability_memory_pack_evaluator.py", "maintained", "git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:examples/public-integration-pack-pilot/m15-capability-pack-altered-graph.json", AUTHORITY_BOUNDARY),
    ("track-b", 234, 237, "270a5bbb536c6bf0726e95455d4bb61ac86d693e", "8e475518f2da6232ae9a6264d8e9c9f1e5fc514a", "examples/public-integration-pack-pilot/m15-capability-pack-executable-authority-claim.json", "synthetic-fixture", "2a72b605385111b9c37b7315306bdc6d1779533f", "100644", "6e74d48b6f974a66f1187c7cefbaf45a8721c252a7c31bc84f250c828dde06e4", "tests/test_m15_capability_memory_pack_evaluator.py", "maintained", "git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:examples/public-integration-pack-pilot/m15-capability-pack-executable-authority-claim.json", AUTHORITY_BOUNDARY),
    ("track-b", 234, 237, "270a5bbb536c6bf0726e95455d4bb61ac86d693e", "8e475518f2da6232ae9a6264d8e9c9f1e5fc514a", "examples/public-integration-pack-pilot/m15-capability-pack-incompatible-runtime.json", "synthetic-fixture", "b5ae6ba9e24916377aa1f443c3c28f03bc5fd763", "100644", "2d585df48eb9899f80f3558767341c7d492bce14ee155552fad9f9571d6e31cf", "tests/test_m15_capability_memory_pack_evaluator.py", "maintained", "git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:examples/public-integration-pack-pilot/m15-capability-pack-incompatible-runtime.json", AUTHORITY_BOUNDARY),
    ("track-b", 234, 237, "270a5bbb536c6bf0726e95455d4bb61ac86d693e", "8e475518f2da6232ae9a6264d8e9c9f1e5fc514a", "examples/public-integration-pack-pilot/m15-capability-pack-missing-license-usage-boundary-evidence.json", "boundary-record", "8c04ab66553a46d099aec1a9b8b11262c31db7b2", "100644", "2b6a9e3a8eae10299cd069bd938643c170669ce2eabce9f0200d2a981849a5de", "tests/test_m15_capability_memory_pack_evaluator.py", "maintained", "git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:examples/public-integration-pack-pilot/m15-capability-pack-missing-license-usage-boundary-evidence.json", AUTHORITY_BOUNDARY),
    ("track-b", 234, 237, "270a5bbb536c6bf0726e95455d4bb61ac86d693e", "8e475518f2da6232ae9a6264d8e9c9f1e5fc514a", "examples/public-integration-pack-pilot/m15-capability-pack-revoked.json", "synthetic-fixture", "a98c301c0f3f9c1b3e9c4dc33b7903a179aa02bc", "100644", "797a42b9c816acccd31759cb7b40a066ab70bcaa19683dc0ddbe66421fc538a3", "tests/test_m15_capability_memory_pack_evaluator.py", "maintained", "git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:examples/public-integration-pack-pilot/m15-capability-pack-revoked.json", AUTHORITY_BOUNDARY),
    ("track-b", 234, 237, "270a5bbb536c6bf0726e95455d4bb61ac86d693e", "8e475518f2da6232ae9a6264d8e9c9f1e5fc514a", "examples/public-integration-pack-pilot/m15-capability-pack-source-digest-mismatch.json", "synthetic-fixture", "8a2992906863cee649614684aff0f9ebebcb96c9", "100644", "60041c22641c33104f2d990829a873dbc68b865fc31396b030ec60411f270e3a", "tests/test_m15_capability_memory_pack_evaluator.py", "maintained", "git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:examples/public-integration-pack-pilot/m15-capability-pack-source-digest-mismatch.json", AUTHORITY_BOUNDARY),
    ("track-b", 234, 237, "270a5bbb536c6bf0726e95455d4bb61ac86d693e", "8e475518f2da6232ae9a6264d8e9c9f1e5fc514a", "examples/public-integration-pack-pilot/m15-capability-pack-stale-specification.json", "synthetic-fixture", "04ebfccd4519e2e79ca15fe403dfae522948ed19", "100644", "92ee515bd75303c77531ce2efb9dc445368e1cebe5e61cea1e3f4f073375cbca", "tests/test_m15_capability_memory_pack_evaluator.py", "maintained", "git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:examples/public-integration-pack-pilot/m15-capability-pack-stale-specification.json", AUTHORITY_BOUNDARY),
    ("track-b", 234, 237, "270a5bbb536c6bf0726e95455d4bb61ac86d693e", "8e475518f2da6232ae9a6264d8e9c9f1e5fc514a", "examples/public-integration-pack-pilot/m15-capability-pack-valid-verified.json", "synthetic-fixture", "c54cb7ec3c842deed422c5945265f8fc7f430b0c", "100644", "66a601ed0f289e785f37e629a4fdc839186c22a93dabc6cec6387b0f188b97d8", "tests/test_m15_capability_memory_pack_evaluator.py", "maintained", "git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:examples/public-integration-pack-pilot/m15-capability-pack-valid-verified.json", AUTHORITY_BOUNDARY),
    ("track-b", 234, 237, "270a5bbb536c6bf0726e95455d4bb61ac86d693e", "8e475518f2da6232ae9a6264d8e9c9f1e5fc514a", "runtime/m15_capability_memory_pack_evaluator.py", "runtime-evaluator", "d1429fbb930dfaa8a4f75c09cd6771ba2dc7190c", "100644", "5e45bbe0f311c3bfcc4d10ed7dc2b1eacbb8d64e4d8d2c922e74d558e66181e2", "tests/test_m15_capability_memory_pack_evaluator.py", "maintained", "git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:runtime/m15_capability_memory_pack_evaluator.py", AUTHORITY_BOUNDARY),
    ("track-b", 234, 237, "270a5bbb536c6bf0726e95455d4bb61ac86d693e", "8e475518f2da6232ae9a6264d8e9c9f1e5fc514a", "schemas/m15-capability-memory-pack.schema.json", "json-schema", "de3ba2fbe6e02c5390846258addeed70fac4da48", "100644", "051436c094413715849ddffd8b54beebb7239f8f288fd2849c333b412e374351", "tests/test_m15_capability_memory_pack_evaluator.py", "maintained", "git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:schemas/m15-capability-memory-pack.schema.json", AUTHORITY_BOUNDARY),
    ("track-b", 234, 237, "270a5bbb536c6bf0726e95455d4bb61ac86d693e", "8e475518f2da6232ae9a6264d8e9c9f1e5fc514a", "tests/test_m15_capability_memory_pack_evaluator.py", "evaluator-tests", "8bb014ef58d6ba5e95bf401561844604bb11b66c", "100644", "806eb6fe660465a5ac72f553cb336cbe3822170218040f7f036e60d4680a28db", "tests/test_m15_capability_memory_pack_evaluator.py", "maintained", "git-object:8e475518f2da6232ae9a6264d8e9c9f1e5fc514a:tests/test_m15_capability_memory_pack_evaluator.py", AUTHORITY_BOUNDARY),
    ("track-c", 238, 239, "5f98f6c86e6b61d50b1c8183aca0736a3419c533", "2d8bab3a84675543c34231a9e04521379febdac1", "docs/learning-governance/m15-lineage-rollback-portability-contract.md", "governance-contract", "2da0edca2e8b1e2fe50ed5f4798a9674b226c011", "100644", "d6c421be2fede2480f8bc2f3c8b0221e1862273184915b2ed317e69357c60f47", "tests/test_m15_lineage_rollback_portability_evaluator.py", "maintained", "git-object:2d8bab3a84675543c34231a9e04521379febdac1:docs/learning-governance/m15-lineage-rollback-portability-contract.md", AUTHORITY_BOUNDARY),
    ("track-c", 238, 239, "5f98f6c86e6b61d50b1c8183aca0736a3419c533", "2d8bab3a84675543c34231a9e04521379febdac1", "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-decision-proof-deletion-execution-authority.json", "synthetic-fixture", "60f7a47fd93ebf380d99af51ec8b14260297fc12", "100644", "25f6ec6fcb7ec0e47ed125ffb2e328bddeba30f50a81a4ac1ecf4afb37b4812d", "tests/test_m15_lineage_rollback_portability_evaluator.py", "maintained", "git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-decision-proof-deletion-execution-authority.json", AUTHORITY_BOUNDARY),
    ("track-c", 238, 239, "5f98f6c86e6b61d50b1c8183aca0736a3419c533", "2d8bab3a84675543c34231a9e04521379febdac1", "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-deletion-pending-unresolved-copies.json", "synthetic-fixture", "504dae9bf980a55dd0d961159845d0efdf877bbf", "100644", "b710d26212866fa40bcb4335385194449113758a102a59c0ddac2cc36332fc4b", "tests/test_m15_lineage_rollback_portability_evaluator.py", "maintained", "git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-deletion-pending-unresolved-copies.json", AUTHORITY_BOUNDARY),
    ("track-c", 238, 239, "5f98f6c86e6b61d50b1c8183aca0736a3419c533", "2d8bab3a84675543c34231a9e04521379febdac1", "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-false-physical-provider-erasure-claim.json", "synthetic-fixture", "9b762e08a0e569d9eba83f6352290570f264f3e6", "100644", "528b31423f15fd08c3b633ab2d079ed3ec5fdc5424cf3886755673931d439b6b", "tests/test_m15_lineage_rollback_portability_evaluator.py", "maintained", "git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-false-physical-provider-erasure-claim.json", AUTHORITY_BOUNDARY),
    ("track-c", 238, 239, "5f98f6c86e6b61d50b1c8183aca0736a3419c533", "2d8bab3a84675543c34231a9e04521379febdac1", "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-learning-proof-rollback-authority.json", "synthetic-fixture", "e10a906ad5c745640c800e83d945a491ca649c9c", "100644", "437d5afb63e3b7cbac8bc791d198a38712acf755221a3af664412b94c238cdcc", "tests/test_m15_lineage_rollback_portability_evaluator.py", "maintained", "git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-learning-proof-rollback-authority.json", AUTHORITY_BOUNDARY),
    ("track-c", 238, 239, "5f98f6c86e6b61d50b1c8183aca0736a3419c533", "2d8bab3a84675543c34231a9e04521379febdac1", "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-missing-downstream-dependency-declaration.json", "synthetic-fixture", "7d8f00af4565ef60df7ebdcf84c249aad88485ac", "100644", "fd3c8a08e02916523848a5ce8b0f544a741f65549ebd5e2e60fba70991fd1acb", "tests/test_m15_lineage_rollback_portability_evaluator.py", "maintained", "git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-missing-downstream-dependency-declaration.json", AUTHORITY_BOUNDARY),
    ("track-c", 238, 239, "5f98f6c86e6b61d50b1c8183aca0736a3419c533", "2d8bab3a84675543c34231a9e04521379febdac1", "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-model-removal-drill-provider-specific-blocker.json", "synthetic-fixture", "0492da9a45db3289358dab1246feaa78d4f62d82", "100644", "14c4baacce910250ac45d540abebd29581e023875a22e1a88f2d3b2dcd946e25", "tests/test_m15_lineage_rollback_portability_evaluator.py", "maintained", "git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-model-removal-drill-provider-specific-blocker.json", AUTHORITY_BOUNDARY),
    ("track-c", 238, 239, "5f98f6c86e6b61d50b1c8183aca0736a3419c533", "2d8bab3a84675543c34231a9e04521379febdac1", "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-model-removal-drill-success.json", "synthetic-fixture", "ce1ce3e8ba7b04c5305ad0611bfde2b65e15a520", "100644", "4d39580e90388765d8dcea32f3d6c9001463ddae5a3047a5e388e1721ec5a221", "tests/test_m15_lineage_rollback_portability_evaluator.py", "maintained", "git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-model-removal-drill-success.json", AUTHORITY_BOUNDARY),
    ("track-c", 238, 239, "5f98f6c86e6b61d50b1c8183aca0736a3419c533", "2d8bab3a84675543c34231a9e04521379febdac1", "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-qualified-deleted-no-physical-erasure.json", "synthetic-fixture", "db1972c88a7d32017dbce86baa02d90d295d7150", "100644", "d42011b3a5ba913bc5c3170c09273ec3170a8d3be613a33b178e19299a3a1dc2", "tests/test_m15_lineage_rollback_portability_evaluator.py", "maintained", "git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-qualified-deleted-no-physical-erasure.json", AUTHORITY_BOUNDARY),
    ("track-c", 238, 239, "5f98f6c86e6b61d50b1c8183aca0736a3419c533", "2d8bab3a84675543c34231a9e04521379febdac1", "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-replacement-model-use-incorrectly-authorized.json", "synthetic-fixture", "22e37814f85078f163fe56e822617c63b66aa2ac", "100644", "82e419a91dfe334355dde8f263645e011782a83c91484fb2b0b79c803ecdd3c8", "tests/test_m15_lineage_rollback_portability_evaluator.py", "maintained", "git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-replacement-model-use-incorrectly-authorized.json", AUTHORITY_BOUNDARY),
    ("track-c", 238, 239, "5f98f6c86e6b61d50b1c8183aca0736a3419c533", "2d8bab3a84675543c34231a9e04521379febdac1", "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-revoked-capability-pack-unresolved-downstream-use.json", "synthetic-fixture", "5dda3afde2969adbf42a3eaa5048fb24c8574a44", "100644", "1bdbd1bc3f61e1a83973da8dd466468844377831d8436d7c8f787a259a15fe3b", "tests/test_m15_lineage_rollback_portability_evaluator.py", "maintained", "git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-revoked-capability-pack-unresolved-downstream-use.json", AUTHORITY_BOUNDARY),
    ("track-c", 238, 239, "5f98f6c86e6b61d50b1c8183aca0736a3419c533", "2d8bab3a84675543c34231a9e04521379febdac1", "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-rollback-blocked-incompatible-dependent.json", "synthetic-fixture", "2411da98fff3398534794cd9ed09d8b2830bb2de", "100644", "b6f48aed01b78b7489bc364e8537ce0916fa1b7defed49a9cd15b9ea322e8579", "tests/test_m15_lineage_rollback_portability_evaluator.py", "maintained", "git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-rollback-blocked-incompatible-dependent.json", AUTHORITY_BOUNDARY),
    ("track-c", 238, 239, "5f98f6c86e6b61d50b1c8183aca0736a3419c533", "2d8bab3a84675543c34231a9e04521379febdac1", "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-rollback-ready-complete-dependency-evidence.json", "synthetic-fixture", "fd7fc0f20f4ab17468c1d45ed12176b4fd5aa4c6", "100644", "0ad2376f0359f75b0afd38432ce4c921e2466f2b60732c98a1bb24b3a7db788f", "tests/test_m15_lineage_rollback_portability_evaluator.py", "maintained", "git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-rollback-ready-complete-dependency-evidence.json", AUTHORITY_BOUNDARY),
    ("track-c", 238, 239, "5f98f6c86e6b61d50b1c8183aca0736a3419c533", "2d8bab3a84675543c34231a9e04521379febdac1", "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-superseded-learning-artifact-known-dependents.json", "synthetic-fixture", "93ebe358dd4ce64c66103a3b4f3eeee046515877", "100644", "8cc561a8bdc9c38641ea2522c466b910ce29590872f7645ec2207eeb58559dc7", "tests/test_m15_lineage_rollback_portability_evaluator.py", "maintained", "git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-superseded-learning-artifact-known-dependents.json", AUTHORITY_BOUNDARY),
    ("track-c", 238, 239, "5f98f6c86e6b61d50b1c8183aca0736a3419c533", "2d8bab3a84675543c34231a9e04521379febdac1", "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-valid-complete-dependency-graph.json", "synthetic-fixture", "2f8918feecb6a625b57bec6a2ac80b49ce97152b", "100644", "a3c4e3c1c99341d07ff04612514d2abc25852acefd643b45852e98287de572fd", "tests/test_m15_lineage_rollback_portability_evaluator.py", "maintained", "git-object:2d8bab3a84675543c34231a9e04521379febdac1:examples/public-integration-pack-pilot/m15-lineage-rollback-portability-valid-complete-dependency-graph.json", AUTHORITY_BOUNDARY),
    ("track-c", 238, 239, "5f98f6c86e6b61d50b1c8183aca0736a3419c533", "2d8bab3a84675543c34231a9e04521379febdac1", "runtime/m15_lineage_rollback_portability_evaluator.py", "runtime-evaluator", "27071fdf92b2561e9432e4a83022ea4ad506d4d5", "100644", "4337f04d0619f4e153088fe080fac7d1a2d976e3e04f6a124169e3d96c73f6a4", "tests/test_m15_lineage_rollback_portability_evaluator.py", "maintained", "git-object:2d8bab3a84675543c34231a9e04521379febdac1:runtime/m15_lineage_rollback_portability_evaluator.py", AUTHORITY_BOUNDARY),
    ("track-c", 238, 239, "5f98f6c86e6b61d50b1c8183aca0736a3419c533", "2d8bab3a84675543c34231a9e04521379febdac1", "schemas/m15-lineage-rollback-portability.schema.json", "json-schema", "4e41841552d7ee2a9905b1104449274bc58e0333", "100644", "8702925c5a2c62efb77fc44cb68328f5be04b963afa27f366f99bef2ee071949", "tests/test_m15_lineage_rollback_portability_evaluator.py", "maintained", "git-object:2d8bab3a84675543c34231a9e04521379febdac1:schemas/m15-lineage-rollback-portability.schema.json", AUTHORITY_BOUNDARY),
    ("track-c", 238, 239, "5f98f6c86e6b61d50b1c8183aca0736a3419c533", "2d8bab3a84675543c34231a9e04521379febdac1", "tests/test_m15_lineage_rollback_portability_evaluator.py", "evaluator-tests", "ef2e87f272e176579a23eb7d5448ed13627cebb4", "100644", "5268f73a441898467e9b8f9471cfc4b9bd4fa27b7b67444fbf852d697d90f4c9", "tests/test_m15_lineage_rollback_portability_evaluator.py", "maintained", "git-object:2d8bab3a84675543c34231a9e04521379febdac1:tests/test_m15_lineage_rollback_portability_evaluator.py", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "docs/learning-governance/m15-cross-control-regression-contract.md", "governance-contract", "007a61eeceea2893c0068140c07615a34b1f370b", "100644", "23f29596100bd85fb52bc46210548a9404c21bf10d532d692d7fc43b84d64fdf", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:docs/learning-governance/m15-cross-control-regression-contract.md", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-01.json", "synthetic-fixture", "0f8cb88ed41365e1b982a12a6787473eeebd456b", "100644", "96a657018d7a8be20faf90523957a4ccec0537f5b853f180c818710c17de975f", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-01.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-02.json", "synthetic-fixture", "40cf8566eec0e1f4f7a68967060022ade47f20cc", "100644", "cdc696021de2603bb99114d253210eb7ce005527b74d22dbc9dc5dcf178c88db", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-02.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-03.json", "synthetic-fixture", "39a708dda6d55479a1a629024b4b44eca0ee163d", "100644", "aa91eb15b431723c4d99550cd38ea3e1a63a064f7b641f58960e295c942525c7", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-03.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-04.json", "synthetic-fixture", "2eabab7e3037dd1a7745f0a33eaefb47ac1662f9", "100644", "6d96c04a17dda4928caf8cf332252a17599b3e146a210affefaa1ee6eae6374d", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-04.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-05.json", "synthetic-fixture", "eaccf8406e0f83035ea033ac358ef59988e0a1b0", "100644", "bcd86d84b9a2d24615764f4d4f5046c7e19d0f6bc0eddf28790f51c1d54896fb", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-05.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-06.json", "synthetic-fixture", "ac60ed83cde870d8dcbe31f13778e37c472bd8df", "100644", "6c70e7efa7000e76574815ddb593635c6bd48641ba36c12aa3d662de194b524b", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-06.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-07.json", "synthetic-fixture", "ee86c6d59f2ee1d4f0af29b535ef355181749a36", "100644", "3a4e8ae6456c76d0fab6111055ab4cc8f6b179a403e87ea6af13e535391d2752", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-07.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-08.json", "synthetic-fixture", "9e96a992bcf57a09f25c40fd4a2c1f6da2fbb702", "100644", "201f4b3eb1d7c87329f3e40b0602f8556a0b3fddc8501999b1f2e61ba194adfc", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-08.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-09.json", "synthetic-fixture", "c548cde76c7128c8d88515e844faaebcc444f796", "100644", "8e7c85f22fe9ef0e66dbf29d88ddf35507ce3daf730eb5c467f3585b038cb9f8", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-09.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-10.json", "synthetic-fixture", "2465fdeaa4b4ac84a6a5930b907b1f7d2e544463", "100644", "b9ff7b587f1ebffa9a4994802e356915ea0c4c91bb83402493ed37747c202e98", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-10.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-11.json", "synthetic-fixture", "4ef3930db08eaa6f2931d9989d09e928335e7bcf", "100644", "3a98010d7cea9ff288f47646721c189bb9019e3285959c6fae3018c8a6b783b3", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-11.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-12.json", "synthetic-fixture", "c54a3a95602a73f119f4cc5bafe1ceeb794c8341", "100644", "16b109d3938a7befb0e6947cef5e52e5bf922ba6389ffeb920a696f3f4049c49", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-12.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-13.json", "synthetic-fixture", "253ab8a1a0feb53a9b048d5fa477a6eb6e1bf07c", "100644", "391a15a1641c4c8e172ea9128a1bbe5c55c60d672b8ec4f3c10ac712f7216841", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-13.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-14.json", "synthetic-fixture", "f22bb5431b58e4e331d7c123964bbd9004fb9f0b", "100644", "bc0c3ac7a5f04e0a25684652d4e966b3e704514ac98454f98037ae1e52dc8693", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-14.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-15.json", "synthetic-fixture", "205e0ea49cde0379009fa3e2c62309c704a3071a", "100644", "48e2ac1afb874f9b95a7f812df7bcb30ed3f06cc978be3b6118353cf0dd11806", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-15.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-16.json", "synthetic-fixture", "90fb92621dfac34b3c2dd88a093e0b24d869fb1d", "100644", "0def119664507d11c91927a966055156b2be3c8e7a635d68b17ea8e23ad28497", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-16.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-17.json", "synthetic-fixture", "c4d42d6914bb869e61d69345c3eea27c19907184", "100644", "f3b8bbcb6157738873aa1f6db18ce7bfbfdfa40d4e0ca75a5b7232d96d038b9a", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-17.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-18.json", "synthetic-fixture", "5920fb287f3fb88cd593217ec530bbde219be8a7", "100644", "62ffa63f03979736e98f74da38bf5830e01cdaf8e77b5502f2ed85af0de1f629", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-18.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-19.json", "synthetic-fixture", "b514d4e984bd58432c09621daa00c8dd20112af0", "100644", "a4621c85ee076e2bdc8af6811f4a12f1eb166c2c9f89d6a9bfe65a69f0beae4b", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-19.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-20.json", "synthetic-fixture", "af412432f376d19e53d61eced21666ee0b22d775", "100644", "af2568e0286541a8e44b0be3580914c3cd558490e19acf0d8406f505aaf947b6", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-20.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-21.json", "synthetic-fixture", "ca5ad3888b14e62f94b86d4d6297706ba843669d", "100644", "3f9806c2700c359f7241d26c348dd18b6595ecd1ad115af9e583a609694d8ab4", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-21.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-22.json", "synthetic-fixture", "8c96d0a89a83eb69f6d2c873b6545ddf02191825", "100644", "5dae89de53a3698dde0fc598e63b1e34d7a2b9ceff66f041475d022afcfe4060", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-22.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-23.json", "synthetic-fixture", "a22582435303c8e59ad4277e9e7e6f21d5d03576", "100644", "6402079bda56eb8a086613ef1e3541d42f0fbe5f546570e19b964b4ab729bcfa", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-23.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-24.json", "synthetic-fixture", "9462de7e0c850c7bc994b70beb3150070139bede", "100644", "1da9dc250c9e3676257e93f4736133f5ec17d438e0c667f675ab1caf8d415c7c", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-24.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "examples/public-integration-pack-pilot/m15-cross-control-matrix.json", "synthetic-fixture", "1fd3ee94b7a3bcb62dc5937f1670eb80b6db0627", "100644", "9d05d2a5331b02d673b2ee2c01e05e0aa098e981d10b9b072a8b92af226b0ca0", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:examples/public-integration-pack-pilot/m15-cross-control-matrix.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "runtime/m15_cross_control_regression_evaluator.py", "runtime-evaluator", "4f083ce374709716e5cc412accb0e723e4ee559f", "100644", "4a412bbd215ed3974d842bc09ee0011b4148f849d5d8e91611a324ef83fc6af6", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:runtime/m15_cross_control_regression_evaluator.py", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "schemas/m15-cross-control-regression.schema.json", "json-schema", "82250c57f380099b04d7c2574101469e42e1929d", "100644", "d52ef7010f596e28592c738b536f0d3131e60c5886ed538f1a57a067c675d651", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:schemas/m15-cross-control-regression.schema.json", AUTHORITY_BOUNDARY),
    ("track-d", 240, 241, "3bec19e42693b757b9abbb077146ca9860d48c1e", "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f", "tests/test_m15_cross_control_regression_evaluator.py", "evaluator-tests", "ee1d7dd3ea493f70a38d0d42a127d77d41f814f8", "100644", "472b75a13498fbc257bbca9cf6eabba688e07cb236f36e3778587b0025415c78", "tests/test_m15_cross_control_regression_evaluator.py", "maintained", "git-object:e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f:tests/test_m15_cross_control_regression_evaluator.py", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "docs/learning-governance/m15-operational-readiness-contract.md", "governance-contract", "d454686815611ec8e28778298b408f2b8df7defc", "100644", "47d8e744d9e9be51f95f0e66eb6a511b748077ce4f5b9f49bf6a62093fb16d96", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:docs/learning-governance/m15-operational-readiness-contract.md", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-01-valid-maintained-main.json", "synthetic-fixture", "27a4dbe92808abd3122ff89843779e9c7d183719", "100644", "9aad611db5379353f34815e2826bf471694193b393abbbdd71a9a153c2e9fc16", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-01-valid-maintained-main.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-02-maintained-main-binding-mismatch.json", "synthetic-fixture", "324bbf57af27c1bd813354134383cc25da5b9ef9", "100644", "85ba22b02d08d6e55029c626f483337ad8febff884e01ed1325f067478d7c1da", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-02-maintained-main-binding-mismatch.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-03-source-track-binding-mismatch.json", "synthetic-fixture", "828ad36732db7aea16ebdeff1bd6c20e5202dfac", "100644", "44616ae315d9d00140ce2b1c4faabd32479053b7560d95b6a2ba2b37adac7c9b", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-03-source-track-binding-mismatch.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-04-incomplete-artifact-inventory.json", "synthetic-fixture", "1937fa7f8039728c33ec36dee83616ada7c2f625", "100644", "8c4e8a70f6fc52bf32d1c07cf5c788bf6787165bde00532d94bc7ba1f4fb5110", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-04-incomplete-artifact-inventory.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-05-artifact-integrity-failure.json", "synthetic-fixture", "19d67542103b5ead8b9c28ee355815148d017505", "100644", "fd1055a4d0d1699187deb2c041c358e260d2622f514caca966e9e85c1c3dabe7", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-05-artifact-integrity-failure.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-06-internal-consistency-failure.json", "synthetic-fixture", "aa60a7229dee9ef0aaee06817159e12a83fd46c5", "100644", "73dc57c22802c81fff132badd7e86b84c2b2d1c9caddf60ea467b12a6e803c2a", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-06-internal-consistency-failure.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-07-cross-control-matrix-unbound.json", "synthetic-fixture", "3050c571c067d11b42addaa6b4660191c3273754", "100644", "143957f60cf1da7ab08f108331861e198b95fa8425d092d6d3f11b7a90d10b78", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-07-cross-control-matrix-unbound.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-08-incomplete-test-coverage.json", "synthetic-fixture", "edff791f05136f67762c7e8b9f6d3ae578e133a3", "100644", "7f170117fb4f2805bb9ae4678599df8166ce80ef1e1ca8a4e696e9fd24d4f778", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-08-incomplete-test-coverage.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-09-incomplete-verification-command-manifest.json", "machine-readable-manifest", "22c6891b91aec4b4ce1bc8e1e7a86916bfbbdfec", "100644", "ce72f6edcfd49b14253d2118b802cbc282ce0ac638955a57b63a22ed44243705", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-09-incomplete-verification-command-manifest.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-10-verification-execution-claimed.json", "synthetic-fixture", "11f1290eb8e75acaf1cd84a2811bbb5704e6950e", "100644", "c5ee061a8e0517741d6cbf527778eb8e8adf1f2dfc111916741aa9c9779c01ca", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-10-verification-execution-claimed.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-11-completion-approval-claim.json", "synthetic-fixture", "38e22ca9a82fff8649f8a582ee894368d04e4887", "100644", "73567d971012393ddc119eb83062642cc2959516be50771cdc6cd76085030b5c", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-11-completion-approval-claim.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-12-tracker-closure-claim.json", "synthetic-fixture", "b7f72df2cf26f920f7edfc56935dffade31d0161", "100644", "0244643637e551b3277604906da3048241130575b26f8d704d97057def73fb2e", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-12-tracker-closure-claim.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-13-m15-completion-claim.json", "synthetic-fixture", "f911604ac5998f243494ba502a3f08536044d728", "100644", "31e7d71239db392ff0809959cba7adee5b8c5a9d984087b28733a4b4d9269184", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-13-m15-completion-claim.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-14-readme-authorization-claim.json", "synthetic-fixture", "d185c556afa544f758d4148121d187dbe40a7aa1", "100644", "75294b248efefe6b8295ae351ecfb28b3171612905a34efd4c9251c9deba025d", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-14-readme-authorization-claim.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-15-tag-authorization-or-creation-claim.json", "synthetic-fixture", "47a92fc9915fefa002078df350381e34907b4257", "100644", "a5d17e8c2d67aefbb100054d50edc177ae6a31685963ed475ebb9fac0c717f5f", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-15-tag-authorization-or-creation-claim.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-16-release-authorization-or-publication-claim.json", "synthetic-fixture", "55ab272a6fbf68f404d7e642a066a98abfbb0159", "100644", "98781331e52175fd74e8d480e4fb960c0bf77a98a1feaf920a3a8644eba818b6", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-16-release-authorization-or-publication-claim.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-17-known-repository-local-completion-blocker.json", "synthetic-fixture", "6964c11c9433531ba811b8e83668808a06308c90", "100644", "042b14f1428a811ca8f4f3fd5005572e961de2d68b160ba9744df125c3ad0629", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-17-known-repository-local-completion-blocker.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-18-malformed-schema-version.json", "synthetic-fixture", "d618aa09533764089db31135b8274dbe1771c97d", "100644", "f82ad6bb84e979d930654e91320f19e27cdf248e2a77fb2d8cbd036e23f3f3f7", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-18-malformed-schema-version.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-19-failed-targeted-test.json", "synthetic-fixture", "e25bb9a8e0ba76aca1c490c7f2b401c7d43a73d0", "100644", "335785bbbf6eed8c045053a22edd01944a5d72d24513e35ed7e67af892674e35", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-19-failed-targeted-test.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-20-test-error.json", "synthetic-fixture", "a8a2c1a6e516272b4f639d20648103a69d8ec44e", "100644", "002e8d6d7843d78de5d1c6b0e0574cd85ab17f4fb053a2c73c0170118fd80699", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-20-test-error.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-21-unexpected-skip.json", "synthetic-fixture", "120948d02c55cbd102b1ffe0ab76cb7ef313e9cb", "100644", "f269d73f9ebf83d3e79a9776e014acdbec2bbb7e007ccfbd4833664d03545602", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-21-unexpected-skip.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-22-missing-verification-result.json", "synthetic-fixture", "52883a2e9a0b22a5b766bfb3393e69758abc24e4", "100644", "0cb48dfa8df43c23415c2f11058590e4be15609f3d37bc8fbcbfab48a21ef9e7", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-22-missing-verification-result.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-23-observed-test-count-mismatch.json", "synthetic-fixture", "bce3df2510ef477c718c8975846d8b6ede5e87e6", "100644", "9e7fb4c833078e8fe2ff7e4826f0a91f8010e281d0c794a1e9bec5f8c326115d", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-23-observed-test-count-mismatch.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-24-verification-result-missing-main-sha.json", "synthetic-fixture", "414557f5cccdf7d413b29a4798d25bd4a37e290f", "100644", "e659fedc52e439927bb7eb80a14c8de24bc099a7db681296357625e2b58f6045", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-24-verification-result-missing-main-sha.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-25-required-artifact-unverified.json", "synthetic-fixture", "6f5a687b37b0519926312d5d75ca6a8cf6f375e9", "100644", "9b841c41ebebcae2dba8da5cdae8e46b4f71c17abdae2341a49169c3bd80a52f", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-25-required-artifact-unverified.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-26-deferred-artifact-without-reason.json", "synthetic-fixture", "ef300568c8f84413ca7ac7c9aeff34d9c422949c", "100644", "51aa84a12fc0bde3b08aca7f6cfa7aecf8136690a41fcfd6a195e9c1734bc1bf", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-26-deferred-artifact-without-reason.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-27-track-d-external-control-dependency-drift.json", "external-evidence-linkage", "c3300fb87029848b0efaa41bcefc5980eb34c931", "100644", "1b2bda2f12c7ed62c1c3f96e9806a5985e2f43c010a544bc5e73c3c1e25aa8c0", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-27-track-d-external-control-dependency-drift.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-28-candidate-head-receipt-binding-mismatch.json", "external-evidence-linkage", "28a31e146a173bf278837219fe7651ae02140d76", "100644", "06f42ddcc8c571863fa1fdfe67736332bbd3d80ffe1ef4a65058a08394fa3089", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-28-candidate-head-receipt-binding-mismatch.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-29-baseline-candidate-sha-conflation.json", "synthetic-fixture", "3f0bdaaa11c1026258855bd54c822d39e888b2dd", "100644", "2d6365a1f2dca4c5e98fe77bf987f095b7fbe6f3b1ee8df8e913d2bea087674b", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-29-baseline-candidate-sha-conflation.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-30-missing-external-execution-receipt.json", "external-evidence-linkage", "06ec329938386a85750279e2ec4a7ac1db496b71", "100644", "f821dfcd998d081628a6c74149ae095ec8be499ca3d7e0bdf656100081aff649", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-30-missing-external-execution-receipt.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-31-undeclared-python-launcher-substitution.json", "synthetic-fixture", "d4e48eb8b19a3e4ff8e72aefe99445559665be69", "100644", "bbf96ef0105597e9046ba5cce4628f9a10d490b34aed71b16d499eeb19ac0d67", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-31-undeclared-python-launcher-substitution.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-32-missing-python-interpreter-version.json", "synthetic-fixture", "d46089d1c24dba38b84c5a6daa01dfd57027d9b1", "100644", "f79a9f71a7894049ee4d7d86d74d7f8906e51d9bf3ae6a8e1db6a23e25ebbda2", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-32-missing-python-interpreter-version.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-33-missing-transcript-digest.json", "synthetic-fixture", "337b373240c9d93b3737d31846d4edf3bc0fbeff", "100644", "b5ea416c201582de191c6c41f4addd426fb7c63a8fad7fd7ba6a5d6e22e7ba1e", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-33-missing-transcript-digest.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-34-command-result-binding-mismatch.json", "synthetic-fixture", "0176d4a1355092df6f4635d5d349803eb7a26022", "100644", "ea3610e1f46116730c85aa3eb85839a115740009838a22714ad58b742465d524", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-34-command-result-binding-mismatch.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "examples/public-integration-pack-pilot/m15-operational-readiness-manifest.json", "machine-readable-manifest", "99ebb1bb51875c3f5c5e1bd959868097d67ec94f", "100644", "9e8021398e643330779fcbb0f04a15bbbbf88d238ec0d29eb7d41697158e2eb5", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:examples/public-integration-pack-pilot/m15-operational-readiness-manifest.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "runtime/m15_operational_readiness_evaluator.py", "runtime-evaluator", "432dc6124a4bc233f4b5e2ece6bd6879b257d730", "100644", "13021d344cc47c34f2bf3c54ba0a88c54468c10408c67c18c86eaab3e674c627", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:runtime/m15_operational_readiness_evaluator.py", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "schemas/m15-operational-readiness.schema.json", "json-schema", "92368bfd000ea7b2a41139594fa8f4a4a8471198", "100644", "bacbf3ed130356c12b6407623e9fded74e4ac0d85af0415c328ffcdff280d53a", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:schemas/m15-operational-readiness.schema.json", AUTHORITY_BOUNDARY),
    ("track-e1", 242, 243, "55629976db7f7b8dc9e2153eaf67f054bd9ee708", "27c92e290cf6ad60bada49b63fe1888511930980", "tests/test_m15_operational_readiness_evaluator.py", "evaluator-tests", "f3b58fdfb117230b3ba06d1d2af609d6eed922b2", "100644", "87e1bcc65cee94617bc8656cd02864b400c08bbe611e651e4d7ed9cc48544c60", "tests/test_m15_operational_readiness_evaluator.py", "maintained", "git-object:27c92e290cf6ad60bada49b63fe1888511930980:tests/test_m15_operational_readiness_evaluator.py", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "docs/learning-governance/m15-release-proof-linkage-contract.md", "governance-contract", "d9b0976c86d1d2f381997a4220a993c8307a0748", "100644", "359f3fa0bed44ec85c8225158ad8fb1b89d1779479e11e6a675cb1e52712204d", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:docs/learning-governance/m15-release-proof-linkage-contract.md", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-01-exact-e1-candidate-and-merge-tree-match.json", "synthetic-fixture", "dc1c1a897bb9b7d1f819c349d368b2a934d6b410", "100644", "375655a5bca0ce710d9aa2a1b8bfe57e84fc61b1ab41430c11e52dea118a64fe", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-01-exact-e1-candidate-and-merge-tree-match.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-02-candidate-changes-preserved-with-explained-base-advancement.json", "synthetic-fixture", "42708258f476bb9600488780bae208aec72eb318", "100644", "1500d23e5b068e4df7ae37d3e491a6993fa012e16e5709d99963d67270f75b1e", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-02-candidate-changes-preserved-with-explained-base-advancement.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-03-e1-candidate-head-mismatch.json", "synthetic-fixture", "ee058ba05e9c2443f9dc7c2e2db59f8d2d2a1a59", "100644", "cab01691c16af18c7bc6feec39060c7c185980c517921994e3f4102ac05c8086", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-03-e1-candidate-head-mismatch.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-04-e1-candidate-tree-mismatch.json", "synthetic-fixture", "1893d6f592698f77a41fcbb2e57a93b31f759227", "100644", "a83c2962fdd162281eeba60a4cb27b61b9e2b2d5f506b8ec4256fd400bddb684", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-04-e1-candidate-tree-mismatch.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-05-e1-merge-commit-mismatch.json", "synthetic-fixture", "2f70b6d21ec2d61a4a0a37a922557b0edddb928e", "100644", "3158dc6ad5a5fe6e348c82fd6282fc7017a5d49a255bd6944bcd1cb3f9e017ca", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-05-e1-merge-commit-mismatch.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-06-e1-merge-tree-is-missing.json", "synthetic-fixture", "67da4de93926f08e018cd1484d515aad2f6c9957", "100644", "aac925a629f72be59b7e15210f63a98a6c844d24dd9717b4cab8a8b2caf6c1cc", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-06-e1-merge-tree-is-missing.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-07-required-candidate-path-is-missing-after-merge.json", "synthetic-fixture", "7964c7c4b18d30f5a993d52ff4ce657a2a12be22", "100644", "0194a40ab8fc536986ab261eff99d896b8502c13461c59fa46cfb63b0da45c40", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-07-required-candidate-path-is-missing-after-merge.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-08-candidate-and-merge-blob-mismatch.json", "synthetic-fixture", "d1fdc075d6df8d6ed08c98532f9622e44f3813a1", "100644", "2ca437d3f610d3fc4d9db4844d56969bc004b3cf08c15e002d6a93814359f919", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-08-candidate-and-merge-blob-mismatch.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-09-candidate-and-merge-canonical-digest-mismatch.json", "synthetic-fixture", "f340b2490b527249467021c0aecd9f4f66e603a7", "100644", "b265cf3c6caf18c5e77038826eadce87376fa89c62dd6c61683bc2e21ba81b5d", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-09-candidate-and-merge-canonical-digest-mismatch.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-10-candidate-and-merge-file-mode-mismatch.json", "synthetic-fixture", "a2f301a681c23edda557aaf449d02267c6090324", "100644", "6bc635f86e3fdc6be9e0e8fecf707b67b480c97c0bed624cd7effdc6a9b23941", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-10-candidate-and-merge-file-mode-mismatch.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-11-unexpected-path-substitution.json", "synthetic-fixture", "57fc6fde3880cd8fc47844fac2c9e7f5874bfeb9", "100644", "6c2ff66061c65d908e310317b742378183913025fc387e321fbd8fe538059baa", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-11-unexpected-path-substitution.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-12-incomplete-candidate-changed-path-manifest.json", "machine-readable-manifest", "67b80b1053aa7a87136a4ec9ad33a3f4db190f75", "100644", "34deef712b8b73d9a6d6b2ec7311dab49013a72cec4f92871ae89b3d14260544", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-12-incomplete-candidate-changed-path-manifest.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-13-incomplete-merge-result-path-manifest.json", "machine-readable-manifest", "1c5f151884e3079d34713b50e4a843736800a689", "100644", "0e3b21229eac68024ce2ea55ffc4575154bf1512a1922c87c4812ec1dce39552", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-13-incomplete-merge-result-path-manifest.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-14-missing-e1-external-receipt-linkage.json", "external-evidence-linkage", "ff6d674da2835d2d19999f427426f67c9c358e06", "100644", "89c04421104c132fb48d40e631162ada88d362fc1f2a04553ff8754919583b0b", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-14-missing-e1-external-receipt-linkage.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-15-e1-external-receipt-digest-mismatch.json", "external-evidence-linkage", "ba577147590b4419dfa387e80312f1122323a74e", "100644", "1467682623a8f94e9dc0a0e38adc64b7efded8e5e48dfa3dd64a5882d53f8bde", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-15-e1-external-receipt-digest-mismatch.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-16-e1-receipt-bound-to-another-candidate.json", "external-evidence-linkage", "38fbfa43d98bf88d5f87a070be41675672cbd899", "100644", "673970528df18a85cc7b97330823aa7b15a7046acf3fddb07ae13f7491f05b76", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-16-e1-receipt-bound-to-another-candidate.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-17-e1-receipt-bound-to-another-baseline.json", "external-evidence-linkage", "77c9095f90b702047ba5484fcd2d89b3d5440270", "100644", "d2e208c3ba7ebc99daffd9ad78e8dd4e41825d7ab4eca4f1f5e4d079964edff8", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-17-e1-receipt-bound-to-another-baseline.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-18-e1-receipt-treated-as-merge-approval.json", "external-evidence-linkage", "9745a665bb6ab83b6b6584b3ff0bcebc0a4f27ed", "100644", "cdeb14bfc7875a3a59e45e7f1c824b126c4a83fc8e005686db4c5a25f592a7cc", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-18-e1-receipt-treated-as-merge-approval.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-19-provenance-success-treated-as-human-approval.json", "synthetic-fixture", "e55fc1bbff5d2bf02c5257d3ce6d475abc7f1ee7", "100644", "5921cc77739e474d5c7980241961a1eeda5eef39506be1f5a3536ad8d51365b6", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-19-provenance-success-treated-as-human-approval.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-20-operational-readiness-treated-as-completion-approval.json", "synthetic-fixture", "791388e58ec2f5663b4d3b33f3cbfed438a93e52", "100644", "d755560619130d00576b7e7e52d135582b0e8765fed86cf1cd72098b1b9e93c1", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-20-operational-readiness-treated-as-completion-approval.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-21-merge-commit-treated-as-a-published-release.json", "synthetic-fixture", "77927f730d31f05f831dd6e1910b485fd4761fe0", "100644", "6bbd5f4598c335ed827370ea87ceb43fdb2b6a51e57d6c387834266b1d469368", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-21-merge-commit-treated-as-a-published-release.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-22-future-v0-14-0-candidate-represented-as-tagged.json", "synthetic-fixture", "a8823829bea2d00c16e8a666a26f6598a1685e9f", "100644", "bc9904b0fa44a0cfd6bae6af50ab5039c9490c1cd57e70cf0ebb585c1332a7cb", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-22-future-v0-14-0-candidate-represented-as-tagged.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-23-github-release-represented-as-published.json", "synthetic-fixture", "5cb18d331f9b6e979e78c5a1c3ecdc9fed4aa735", "100644", "e899bc7e07c47f0f5060fb9b216a00955ffa6a1aabd8180c945bb83577d03618", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-23-github-release-represented-as-published.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-24-tracker-231-represented-as-closed.json", "synthetic-fixture", "6d08443cbb3f2b03349b820afe509ea48c95ee33", "100644", "ceca86e8473045d30ba9f391cf4c84e3f9867eb4544e910bae47e8035ca7ab65", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-24-tracker-231-represented-as-closed.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-25-m15-represented-as-complete.json", "synthetic-fixture", "e6702c95bd12c7dfeccf54b02406f32a9922397e", "100644", "1dc16a3330dae0edde7ef7d25f2082d2a6fa89276c9433fb3a746d7c0190e775", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-25-m15-represented-as-complete.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-26-readme-completion-represented-as-authorized.json", "synthetic-fixture", "530be5fded9e4debeaa846d19080544c32da51cb", "100644", "b3c19dae79f5bae0e2cfdae20d4caa9950c27907c020bc537ab38526184359c8", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-26-readme-completion-represented-as-authorized.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-27-required-e2-linkage-blocker-omitted.json", "synthetic-fixture", "47643903ece530922c1a6c4ff5a429fb8452e7e8", "100644", "3d72abff5f2c691a31cbbf3c2325ec7fb4abe5133ecfa746cb856db3fec8b6cc", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-27-required-e2-linkage-blocker-omitted.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-28-unverified-continuity-treated-as-linked.json", "continuity-record", "2159d0e70989facd129e00465c112b39c93bb994", "100644", "d4fe8b5f9cca77b0a090c32465bbb738655c1afa85c50afd51c473d62df4a99d", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-28-unverified-continuity-treated-as-linked.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-29-future-release-candidate-identifier-is-missing.json", "synthetic-fixture", "ee1b6644e99c11a1d30d14164a33eeb12eade599", "100644", "c1b68b2bd33d366d4135c68f56acacdf2195443b856c8f7d0f76d86e9b5202b2", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-29-future-release-candidate-identifier-is-missing.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-30-release-proof-claims-decision-proof-or-learning-proof-sealing.json", "synthetic-fixture", "05381dfcac7de4c313f2385206c118c471ddce50", "100644", "92df78cd1891422ae9f200645e52c15fbbba757535e6b8f8c330a8b4cc9c2532", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-30-release-proof-claims-decision-proof-or-learning-proof-sealing.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-31-unverified-continuity-remains-not-ready.json", "continuity-record", "17c34f65891b1ab9cf10228a73a19fd1e8729e98", "100644", "f99cdc09eb6ec7fd213d7a4105bb638d8527194c9eec61c3fa0d0e4d714cba5a", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-31-unverified-continuity-remains-not-ready.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-32-candidate-modification-is-preserved.json", "synthetic-fixture", "f93c787266cb7ba97dacb05258fe38d646770a70", "100644", "dbe0fe39ee9410952258539617ade363933510f0f62f0bc58d9000154a44278b", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-32-candidate-modification-is-preserved.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-33-candidate-rename-is-preserved.json", "synthetic-fixture", "a81da2c9fcb7363fd6f2a188eac7d3dd43f2c332", "100644", "8a3f7897159b5c25e54697a96402d88d1a8d6d576f1c95c196494b732db9d847", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-33-candidate-rename-is-preserved.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-34-candidate-deletion-is-preserved.json", "synthetic-fixture", "ea168af26605e97f632c6b3d6bb237a14159f008", "100644", "b0bc2ae32a1be21dad62bc0551bdbd899633ed3259a395e087bc65a51778c387", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-34-candidate-deletion-is-preserved.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-35-external-e2-verification-receipt-is-missing.json", "external-evidence-linkage", "c54c1a8e08c6e805702ea365c68e0722e1baa0a6", "100644", "ebf4ad3e977aaf05a7cfa3d21ad020981ed9b32b9cf339dcd06b20fc34d4c28e", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-35-external-e2-verification-receipt-is-missing.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-36-external-e2-verification-receipt-is-inconsistent.json", "external-evidence-linkage", "7e38142fc950b8ecd87c62a2eb3643b2dd13ba73", "100644", "d0c9dc4aa4e45a755cbc6e9d344efbe35426ba1626be5049bd6305fb4ed9c6b4", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-36-external-e2-verification-receipt-is-inconsistent.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-37-external-pr-observation-is-missing.json", "external-evidence-linkage", "f118dddff441f7b98b341d816bdc7dfc4b6710d0", "100644", "74078ded045369d2260a29fb77314de7854e9858a0553c1bb375103bda0ca9dc", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-37-external-pr-observation-is-missing.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-38-pr-observation-bound-to-another-pr.json", "synthetic-fixture", "723cb0d643e2de79d577d60f762aac12384301b9", "100644", "3d5ba2780a760ada32497f998b339719dede698ec5d5015e280159f5a9c9ad8a", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-38-pr-observation-bound-to-another-pr.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-39-observation-receipt-candidate-mismatch.json", "external-evidence-linkage", "8d9d92cc9993b5c535a405c2ba166126917b4b7e", "100644", "416fe6a82df368970edd30856ae524ec5f53dd9d893cb302ad8f6902a3f11106", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-39-observation-receipt-candidate-mismatch.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-40-verification-test-count-below-minimum.json", "synthetic-fixture", "664067710e4f77a54f556e4c16d6bc3e34da1b51", "100644", "10034dcdb976d62fd8063c7c3fc2af511f9188525b22d334204b607e4245fdaa", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-40-verification-test-count-below-minimum.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-candidate-changed-paths.json", "synthetic-fixture", "b476339bc96f9303cf6124619d760c01603043cd", "100644", "7def94051d634bad63ef8cbe27f0f068242312f6c20ca680e270a6cea4074378", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-candidate-changed-paths.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-candidate-to-merge-continuity.json", "continuity-record", "76a9a65ea82fcb03ddc425a3107cc5fd328ad5aa", "100644", "8e1fa60898f4efd4c726f44dc3e756ae00231670e568f0b8ed6435d37dec1916", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-candidate-to-merge-continuity.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-e1-external-receipt.json", "external-evidence-linkage", "e30b7d7408517f5fdc86050b4a182d2815230db9", "100644", "5884203aff41d4b173fa21121669eadc6727c21a17f8f33e6ad1d964459b5d3c", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-e1-external-receipt.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-manifest.json", "machine-readable-manifest", "8c482631bf8eea5cefc98769c71379baf74ecc5b", "100644", "6c9e020a6597f9e9e9fda0fff3cf4150b50c1155000ae598716453b99cf4e185", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-manifest.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-merge-result-paths.json", "synthetic-fixture", "83593b26e3fe5ec9bd26400b1646df79dfb8f692", "100644", "40f246f3f30d4ca924c9004f5c60c8fa3c3a0342c285e407246e86704d92a908", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-merge-result-paths.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "examples/public-integration-pack-pilot/m15-release-proof-linkage-release-boundaries.json", "boundary-record", "01a91f1ba05f4675bf197ce2828cbe84f6443a70", "100644", "33a0418bd509669644521980ce449dd4aa914094eb719a1b7637d3bc496ef833", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:examples/public-integration-pack-pilot/m15-release-proof-linkage-release-boundaries.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "runtime/m15_release_proof_linkage_evaluator.py", "runtime-evaluator", "6fdf56d2718be5d17b83da01bb47c76cd52b63d9", "100644", "1f62114d8b1ed16ec90173c0d8648e112350b46c45ed4df9a166d5d4441ed66e", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:runtime/m15_release_proof_linkage_evaluator.py", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "schemas/m15-release-proof-linkage.schema.json", "json-schema", "ded0187f339b990459386f509c9399181ca4de21", "100644", "6f7155564ec94397d096de1190087f568af4cdfa438ef75c13caffb47abd2031", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:schemas/m15-release-proof-linkage.schema.json", AUTHORITY_BOUNDARY),
    ("track-e2", 248, 249, "efc31e7d24c26d2cea2cb536a4cae257aababb5f", "f6d074fca2fedecbf654697719179440bc0680d3", "tests/test_m15_release_proof_linkage_evaluator.py", "evaluator-tests", "b24ceba23e0e6424f1663e6274170a08466a8edc", "100644", "afc489cbc215a008d78ec440444bf5009d6d0a652f57c2c2fa087ffcf1961c1e", "tests/test_m15_release_proof_linkage_evaluator.py", "maintained", "git-object:f6d074fca2fedecbf654697719179440bc0680d3:tests/test_m15_release_proof_linkage_evaluator.py", AUTHORITY_BOUNDARY),
)

ACCEPTANCE_BINDING_FIELDS = (
    "criterion_id",
    "criterion_text",
    "source_track",
    "evidence_references",
    "artifact_references",
    "test_references",
    "authority_boundary",
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

ARTIFACT_FIELDS = frozenset(
    {
        "track_id",
        "source_issue",
        "implementation_pr",
        "candidate_sha",
        "merge_sha",
        "repository_path",
        "artifact_type",
        "git_blob_sha",
        "git_file_mode",
        "canonical_text_sha256",
        "covering_test",
        "lifecycle_state",
        "evidence_reference",
        "authority_boundary",
    }
)
ARTIFACT_TYPES = {
    "governance-contract",
    "json-schema",
    "runtime-evaluator",
    "evaluator-tests",
    "machine-readable-manifest",
    "boundary-record",
    "continuity-record",
    "external-evidence-linkage",
    "synthetic-fixture",
}
AFFIRMATIVE_AUTHORITY_KEYS = {
    "m15_complete",
    "m15_completed",
    "tracker_231_closed",
    "track_e4_implemented",
    "track_e4_completed",
    "v0_14_0_released",
    "tag_authorized",
    "tag_created",
    "github_release_authorized",
    "github_release_created",
    "github_release_published",
    "completion_approved",
    "release_approved",
    "decision_proof_sealed",
    "learning_proof_sealed",
    "deployment_authorized",
    "risk_accepted",
    "rollback_executed",
    "deletion_executed",
    "fail_closed_executed",
    "audit_closed",
    "waiver_granted",
    "authority_transferred",
    "external_state_mutated",
}
AUTHORITY_STATE_KEYS = {
    "m15_state",
    "tracker_231_state",
    "v0_14_0_state",
    "tag_state",
    "github_release_state",
}
NEGATIVE_AUTHORITY_VALUES = {
    "",
    "false",
    "none",
    "open",
    "active-and-incomplete",
    "incomplete",
    "unpublished",
    "not-authorized",
    "not-created",
    "not-published",
    "not-implemented",
    "historical-only",
    E2_SUPERSEDED_CLASSIFICATION,
}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return ()


def _exact_fields(value: Any, expected: frozenset[str]) -> bool:
    return isinstance(value, Mapping) and frozenset(value) == expected


def _object_sha(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(character in "0123456789abcdef" for character in value)
    )


def _sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _utc_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    core = value[:-1]
    if "." in core:
        core, fraction = core.split(".", 1)
        if not fraction or not fraction.isdigit():
            return False
    if len(core) != 19 or core[4] != "-" or core[7] != "-":
        return False
    if core[10] != "T" or core[13] != ":" or core[16] != ":":
        return False
    digits = core[:4] + core[5:7] + core[8:10] + core[11:13] + core[14:16] + core[17:19]
    if not digits.isdigit():
        return False
    year = int(core[:4])
    month = int(core[5:7])
    day = int(core[8:10])
    hour = int(core[11:13])
    minute = int(core[14:16])
    second = int(core[17:19])
    if year < 1 or month < 1 or month > 12 or hour > 23 or minute > 59 or second > 59:
        return False
    month_days = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
    maximum_day = 29 if month == 2 and leap else month_days[month - 1]
    return 1 <= day <= maximum_day


def _affirmative(value: Any) -> bool:
    if value is True:
        return True
    if value is False or value is None:
        return False
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() not in NEGATIVE_AUTHORITY_VALUES
    if isinstance(value, Mapping):
        return any(_affirmative(item) for item in value.values())
    if _sequence(value):
        return any(_affirmative(item) for item in value)
    return bool(value)


def _authority_findings(value: Any, findings: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            token = str(key).strip().lower().replace("-", "_")
            if token in AFFIRMATIVE_AUTHORITY_KEYS and _affirmative(item):
                findings.append(f"authority-boundary-violation:{token}")
            if token in AUTHORITY_STATE_KEYS and _affirmative(item):
                findings.append(f"authority-state-violation:{token}")
            _authority_findings(item, findings)
    elif _sequence(value):
        for item in value:
            _authority_findings(item, findings)


def _prose_clauses(value: str) -> tuple[tuple[str, ...], ...]:
    """Tokenize prose without imports while preserving semantic clause edges."""

    clauses: list[tuple[str, ...]] = []
    tokens: list[str] = []
    token: list[str] = []

    def finish_token() -> None:
        if token:
            tokens.append("".join(token))
            token.clear()

    def finish_clause() -> None:
        finish_token()
        if tokens:
            clauses.append(tuple(tokens))
            tokens.clear()

    lowered = value.casefold()
    for index, character in enumerate(lowered):
        if character.isalnum():
            token.append(character)
            continue
        finish_token()
        decimal_point = (
            character == "."
            and index > 0
            and index + 1 < len(lowered)
            and lowered[index - 1].isdigit()
            and lowered[index + 1].isdigit()
        )
        if character in ".!?;\n\r" and not decimal_point:
            finish_clause()
    finish_clause()
    return tuple(clauses)


def _prose_action_is_negated(tokens: tuple[str, ...], index: int) -> bool:
    start = 0
    for boundary in ("but", "however", "yet"):
        positions = [
            position
            for position, token in enumerate(tokens[:index])
            if token == boundary
        ]
        if positions:
            start = max(start, positions[-1] + 1)
    prefix = tokens[start:index]
    if not prefix:
        return False
    if prefix[0] in {"no", "never", "cannot", "neither"}:
        return True
    return any(
        token in {"not", "never", "cannot", "without"}
        for token in prefix[-6:]
    )


def _prose_has_affirmative_authority_claim(value: Any) -> bool:
    """Detect narrow, explicit authority assertions in unrestricted prose."""

    if not isinstance(value, str):
        return False
    for tokens in _prose_clauses(value):
        token_set = frozenset(tokens)
        has_m15 = "m15" in token_set
        has_track_e4 = "track" in token_set and "e4" in token_set
        has_v0_14_0 = {"v0", "14", "0"}.issubset(token_set)
        has_github_release = "github" in token_set and "release" in token_set
        has_tag = "tag" in token_set
        has_decision_proof = "decision" in token_set and "proof" in token_set
        has_learning_proof = "learning" in token_set and "proof" in token_set
        has_tracker_231 = "tracker" in token_set and "231" in token_set
        has_completion_or_release = bool(
            {"completion", "release", "authority"}.intersection(token_set)
        )
        for index, action in enumerate(tokens):
            affirmative = (
                action in {"complete", "completed"}
                and (has_m15 or has_track_e4)
            ) or (
                action in {"approve", "approved", "approves", "authorize", "authorized", "authorizes"}
                and (
                    has_m15
                    or has_track_e4
                    or has_v0_14_0
                    or has_github_release
                    or has_tag
                    or has_completion_or_release
                )
            ) or (
                action in {"released", "published"}
                and (has_v0_14_0 or has_github_release)
            ) or (
                action in {"created", "exists"}
                and (has_tag or has_github_release)
            ) or (
                action in {"sealed", "seals"}
                and (has_decision_proof or has_learning_proof)
            ) or (action == "closed" and has_tracker_231)
            if affirmative and not _prose_action_is_negated(tokens, index):
                return True
    return False


def _validate_unrestricted_prose(
    value: Any,
    path: str,
    blocking: list[str],
) -> None:
    if not _nonempty_string(value):
        blocking.append(f"unrestricted-prose-invalid:{path}")
    elif _prose_has_affirmative_authority_claim(value):
        blocking.append(f"affirmative-authority-prose:{path}")


def _validate_manifest(value: Any, blocking: list[str]) -> None:
    fields = frozenset(
        {
            "schema_version",
            "document_kind",
            "repository",
            "source_issue",
            "parent_tracker",
            "source_main_base_sha",
            "source_main_base_tree_sha",
            "prior_material_artifact_count",
            "required_track_ids",
            "required_acceptance_criteria_count",
            "required_blockers",
            "required_future_prerequisites",
            "authorized_phase_aware_compatibility_repair",
            "authorized_historical_compatibility_repairs",
            "historical_e1_artifact_binding",
            "e3_authorized_compatibility_repair",
            "verification_commands",
            "completion_readiness_only",
            "runtime_caller_data_only",
            "final_candidate_commit_external",
            "final_receipt_commit_external",
            "m15_state",
            "tracker_231_state",
            "track_e4_implemented",
            "v0_14_0_state",
            "tag_state",
            "github_release_state",
            "decision_proof_sealed",
            "learning_proof_sealed",
            "authority_boundary",
            "runtime_boundary",
        }
    )
    if not _exact_fields(value, fields):
        blocking.append("manifest-shape-invalid")
        return
    manifest = _mapping(value)
    expected = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "document_kind": "completion-readiness-manifest",
        "repository": REPOSITORY,
        "source_issue": SOURCE_ISSUE,
        "parent_tracker": PARENT_TRACKER,
        "source_main_base_sha": SOURCE_MAIN_BASE_SHA,
        "source_main_base_tree_sha": SOURCE_MAIN_BASE_TREE_SHA,
        "prior_material_artifact_count": PRIOR_MATERIAL_ARTIFACT_COUNT,
        "required_track_ids": list(TRACK_COUNTS),
        "required_acceptance_criteria_count": len(CRITERION_IDS),
        "required_blockers": list(REQUIRED_BLOCKERS),
        "required_future_prerequisites": list(REQUIRED_FUTURE_PREREQUISITES),
        "authorized_phase_aware_compatibility_repair": dict(
            AUTHORIZED_PHASE_AWARE_COMPATIBILITY_REPAIR
        ),
        "authorized_historical_compatibility_repairs": [
            dict(item) for item in AUTHORIZED_HISTORICAL_COMPATIBILITY_REPAIRS
        ],
        "historical_e1_artifact_binding": dict(HISTORICAL_E1_ARTIFACT_BINDING),
        "e3_authorized_compatibility_repair": dict(
            E3_AUTHORIZED_COMPATIBILITY_REPAIR
        ),
        "completion_readiness_only": True,
        "runtime_caller_data_only": True,
        "final_candidate_commit_external": True,
        "final_receipt_commit_external": True,
        "m15_state": "active-and-incomplete",
        "tracker_231_state": "open",
        "track_e4_implemented": False,
        "v0_14_0_state": "unpublished",
        "tag_state": "not-authorized",
        "github_release_state": "not-created",
        "decision_proof_sealed": False,
        "learning_proof_sealed": False,
        "authority_boundary": AUTHORITY_BOUNDARY,
        "runtime_boundary": RUNTIME_BOUNDARY,
    }
    for key, expected_value in expected.items():
        if manifest.get(key) != expected_value:
            blocking.append(f"manifest-binding-invalid:{key}")
    commands = _sequence(manifest.get("verification_commands"))
    if len(commands) != len(COMMAND_IDS):
        blocking.append("manifest-verification-command-count-invalid")
        return
    seen: list[str] = []
    observed_registry: list[tuple[Any, ...]] = []
    command_fields = frozenset(
        {
            "command_id",
            "declared_logical_argv",
            "execution_scope",
            "minimum_tests_observed",
        }
    )
    for command in commands:
        if not _exact_fields(command, command_fields):
            blocking.append("manifest-verification-command-shape-invalid")
            continue
        item = _mapping(command)
        command_id = item.get("command_id")
        if command_id not in COMMAND_MINIMA:
            blocking.append("manifest-verification-command-id-invalid")
            continue
        seen.append(command_id)
        if item.get("minimum_tests_observed") != COMMAND_MINIMA[command_id]:
            blocking.append(f"verification-minimum-invalid:{command_id}")
        argv = _sequence(item.get("declared_logical_argv"))
        if not argv or argv[0] != "python" or not all(
            _nonempty_string(token) for token in argv
        ):
            blocking.append(f"verification-argv-invalid:{command_id}")
        if item.get("execution_scope") not in {
            "e3-candidate-validation",
            "inherited-regression",
            "candidate-full-suite-integration",
            "authorized-compatibility-regression",
        }:
            blocking.append(f"verification-scope-invalid:{command_id}")
        observed_registry.append(
            (
                command_id,
                tuple(argv),
                item.get("execution_scope"),
                item.get("minimum_tests_observed"),
            )
        )
    if tuple(seen) != COMMAND_IDS:
        blocking.append("manifest-verification-command-order-invalid")
    if tuple(observed_registry) != EXPECTED_VERIFICATION_COMMANDS:
        blocking.append("manifest-verification-command-registry-invalid")


def _validate_inventory(value: Any, blocking: list[str]) -> None:
    fields = frozenset(
        {
            "schema_version",
            "document_kind",
            "repository",
            "source_main_base_sha",
            "source_main_base_tree_sha",
            "prior_material_artifact_count",
            "track_summaries",
            "artifacts",
            "inventory_binding_sha256",
            "caller_supplied_inert_record",
            "authority_boundary",
        }
    )
    if not _exact_fields(value, fields):
        blocking.append("track-evidence-inventory-shape-invalid")
        return
    inventory = _mapping(value)
    expected = {
        "schema_version": TRACK_EVIDENCE_SCHEMA_VERSION,
        "document_kind": "track-evidence-inventory",
        "repository": REPOSITORY,
        "source_main_base_sha": SOURCE_MAIN_BASE_SHA,
        "source_main_base_tree_sha": SOURCE_MAIN_BASE_TREE_SHA,
        "prior_material_artifact_count": PRIOR_MATERIAL_ARTIFACT_COUNT,
        "inventory_binding_sha256": INVENTORY_BINDING_SHA256,
        "caller_supplied_inert_record": True,
        "authority_boundary": AUTHORITY_BOUNDARY,
    }
    for key, expected_value in expected.items():
        if inventory.get(key) != expected_value:
            blocking.append(f"track-evidence-binding-invalid:{key}")
    summaries = _sequence(inventory.get("track_summaries"))
    artifacts = _sequence(inventory.get("artifacts"))
    if len(summaries) != len(TRACK_COUNTS):
        blocking.append("track-summary-count-invalid")
    if len(artifacts) != PRIOR_MATERIAL_ARTIFACT_COUNT:
        blocking.append("prior-material-artifact-count-invalid")
    summary_fields = frozenset(
        {
            "track_id",
            "source_issue",
            "implementation_pr",
            "base_sha",
            "candidate_sha",
            "candidate_tree_sha",
            "merge_sha",
            "merge_tree_sha",
            "material_path_count",
        }
    )
    summary_ids: list[str] = []
    for summary in summaries:
        if not _exact_fields(summary, summary_fields):
            blocking.append("track-summary-shape-invalid")
            continue
        item = _mapping(summary)
        track_id = item.get("track_id")
        if track_id not in TRACK_SUMMARY_BINDINGS or track_id in summary_ids:
            blocking.append("track-summary-id-invalid-or-duplicate")
            continue
        summary_ids.append(track_id)
        expected_summary = {"track_id": track_id, **TRACK_SUMMARY_BINDINGS[track_id]}
        if dict(item) != expected_summary:
            blocking.append(f"track-summary-binding-invalid:{track_id}")
    if tuple(summary_ids) != tuple(TRACK_COUNTS):
        blocking.append("track-summary-order-or-coverage-invalid")
    counts = {track_id: 0 for track_id in TRACK_COUNTS}
    paths: set[str] = set()
    observed_artifact_bindings: list[tuple[Any, ...]] = []
    for artifact in artifacts:
        if not _exact_fields(artifact, ARTIFACT_FIELDS):
            blocking.append("artifact-shape-invalid")
            continue
        item = _mapping(artifact)
        observed_artifact_bindings.append(
            tuple(item.get(field) for field in ARTIFACT_BINDING_FIELDS)
        )
        track_id = item.get("track_id")
        if track_id not in TRACK_BINDINGS:
            blocking.append("artifact-track-binding-invalid")
            continue
        issue, pull_request, candidate_sha, merge_sha = TRACK_BINDINGS[track_id]
        checks = {
            "source_issue": issue,
            "implementation_pr": pull_request,
            "candidate_sha": candidate_sha,
            "merge_sha": merge_sha,
            "lifecycle_state": "maintained",
            "authority_boundary": AUTHORITY_BOUNDARY,
        }
        for key, expected_value in checks.items():
            if item.get(key) != expected_value:
                blocking.append(f"artifact-binding-invalid:{track_id}:{key}")
        path = item.get("repository_path")
        if not _nonempty_string(path) or path in paths:
            blocking.append("artifact-path-invalid-or-duplicate")
        else:
            paths.add(path)
        if item.get("artifact_type") not in ARTIFACT_TYPES:
            blocking.append("artifact-type-invalid")
        if not _object_sha(item.get("git_blob_sha")):
            blocking.append("artifact-blob-sha-invalid")
        if item.get("git_file_mode") not in {"100644", "100755"}:
            blocking.append("artifact-file-mode-invalid")
        if not _sha256(item.get("canonical_text_sha256")):
            blocking.append("artifact-canonical-digest-invalid")
        if not _nonempty_string(item.get("covering_test")):
            blocking.append("artifact-covering-test-missing")
        if not _nonempty_string(item.get("evidence_reference")):
            blocking.append("artifact-evidence-reference-missing")
        counts[track_id] += 1
    if counts != TRACK_COUNTS:
        blocking.append("track-material-counts-invalid")
    if tuple(observed_artifact_bindings) != EXPECTED_ARTIFACT_BINDINGS:
        blocking.append("artifact-inventory-exact-binding-invalid")


def _validate_e2_continuity(value: Any, blocking: list[str]) -> None:
    fields = frozenset(
        {
            "schema_version",
            "document_kind",
            "repository",
            "e2_source_issue",
            "e2_implementation_pr",
            "source_main_base_sha",
            "candidate_sha",
            "candidate_tree_sha",
            "merge_sha",
            "merge_tree_sha",
            "merge_parents",
            "candidate_is_merge_parent",
            "base_is_merge_parent",
            "candidate_to_merge_changed_path_count",
            "additional_merge_difference_count",
            "active_observation_comment_id",
            "active_receipt_comment_id",
            "active_receipt_canonical_sha256",
            "superseded_receipt_comment_id",
            "superseded_receipt_classification",
            "relation",
            "caller_supplied_inert_record",
            "authority_boundary",
        }
    )
    if not _exact_fields(value, fields):
        blocking.append("e2-continuity-shape-invalid")
        return
    record = _mapping(value)
    expected = {
        "schema_version": E2_CONTINUITY_SCHEMA_VERSION,
        "document_kind": "e2-continuity-record",
        "repository": REPOSITORY,
        "e2_source_issue": 248,
        "e2_implementation_pr": 249,
        "source_main_base_sha": E2_SOURCE_MAIN_BASE_SHA,
        "candidate_sha": E2_CANDIDATE_SHA,
        "candidate_tree_sha": E2_CANDIDATE_TREE_SHA,
        "merge_sha": E2_MERGE_SHA,
        "merge_tree_sha": E2_MERGE_TREE_SHA,
        "merge_parents": list(E2_MERGE_PARENTS),
        "candidate_is_merge_parent": True,
        "base_is_merge_parent": True,
        "candidate_to_merge_changed_path_count": 0,
        "additional_merge_difference_count": 0,
        "active_observation_comment_id": E2_OBSERVATION_COMMENT_ID,
        "active_receipt_comment_id": E2_ACTIVE_RECEIPT_COMMENT_ID,
        "active_receipt_canonical_sha256": E2_ACTIVE_RECEIPT_SHA256,
        "superseded_receipt_comment_id": E2_SUPERSEDED_RECEIPT_COMMENT_ID,
        "superseded_receipt_classification": E2_SUPERSEDED_CLASSIFICATION,
        "relation": E2_RELATION,
        "caller_supplied_inert_record": True,
        "authority_boundary": AUTHORITY_BOUNDARY,
    }
    for key, expected_value in expected.items():
        if record.get(key) != expected_value:
            blocking.append(f"e2-candidate-merge-mismatch:{key}")


def _validate_e2_external(value: Any, blocking: list[str]) -> None:
    fields = frozenset(
        {
            "schema_version",
            "document_kind",
            "repository",
            "source_main_base_sha",
            "candidate_sha",
            "active_observation_comment_id",
            "active_observation_reference",
            "active_receipt_comment_id",
            "active_receipt_reference",
            "active_receipt_canonical_sha256",
            "active_receipt_accepted",
            "superseded_receipt_comment_id",
            "superseded_receipt_reference",
            "superseded_receipt_classification",
            "superseded_receipt_accepted_as_active",
            "external_evidence_is_completion_authority",
            "external_evidence_is_release_authority",
            "caller_supplied_inert_record",
            "authority_boundary",
        }
    )
    if not _exact_fields(value, fields):
        blocking.append("e2-external-evidence-shape-invalid")
        return
    record = _mapping(value)
    expected = {
        "schema_version": E2_EXTERNAL_EVIDENCE_SCHEMA_VERSION,
        "document_kind": "e2-external-evidence-record",
        "repository": REPOSITORY,
        "source_main_base_sha": E2_SOURCE_MAIN_BASE_SHA,
        "candidate_sha": E2_CANDIDATE_SHA,
        "active_observation_comment_id": E2_OBSERVATION_COMMENT_ID,
        "active_observation_reference": (
            "https://github.com/aa-os/aaos-public/pull/249#issuecomment-5015690597"
        ),
        "active_receipt_comment_id": E2_ACTIVE_RECEIPT_COMMENT_ID,
        "active_receipt_reference": (
            "https://github.com/aa-os/aaos-public/pull/249#issuecomment-5015694989"
        ),
        "active_receipt_canonical_sha256": E2_ACTIVE_RECEIPT_SHA256,
        "active_receipt_accepted": True,
        "superseded_receipt_comment_id": E2_SUPERSEDED_RECEIPT_COMMENT_ID,
        "superseded_receipt_reference": (
            "https://github.com/aa-os/aaos-public/pull/249#issuecomment-5015466792"
        ),
        "superseded_receipt_classification": E2_SUPERSEDED_CLASSIFICATION,
        "superseded_receipt_accepted_as_active": False,
        "external_evidence_is_completion_authority": False,
        "external_evidence_is_release_authority": False,
        "caller_supplied_inert_record": True,
        "authority_boundary": AUTHORITY_BOUNDARY,
    }
    for key, expected_value in expected.items():
        if record.get(key) != expected_value:
            blocking.append(f"e2-external-evidence-binding-invalid:{key}")


def _validate_acceptance_matrix(
    value: Any,
    blocking: list[str],
    readiness: list[str],
) -> None:
    fields = frozenset(
        {
            "schema_version",
            "document_kind",
            "repository",
            "parent_tracker",
            "criterion_count",
            "criteria",
            "all_criteria_covered",
            "caller_supplied_inert_record",
            "authority_boundary",
        }
    )
    if not _exact_fields(value, fields):
        blocking.append("acceptance-matrix-shape-invalid")
        return
    matrix = _mapping(value)
    matrix_blocking: list[str] = []
    matrix_readiness: list[str] = []
    if matrix.get("schema_version") != ACCEPTANCE_MATRIX_SCHEMA_VERSION:
        matrix_blocking.append("acceptance-matrix-schema-version-invalid")
    if matrix.get("document_kind") != "m15-acceptance-coverage-matrix":
        matrix_blocking.append("acceptance-matrix-document-kind-invalid")
    if matrix.get("repository") != REPOSITORY or matrix.get(
        "parent_tracker"
    ) != PARENT_TRACKER:
        matrix_blocking.append("acceptance-matrix-repository-binding-invalid")
    criteria = _sequence(matrix.get("criteria"))
    if matrix.get("criterion_count") != len(CRITERION_IDS) or len(criteria) != len(
        CRITERION_IDS
    ):
        matrix_readiness.append("incomplete-acceptance-criteria-coverage")
    row_fields = frozenset(
        {
            "criterion_id",
            "criterion_text",
            "source_track",
            "evidence_references",
            "artifact_references",
            "test_references",
            "coverage_state",
            "notes",
            "authority_boundary",
        }
    )
    seen: list[str] = []
    for index, row in enumerate(criteria):
        if not _exact_fields(row, row_fields):
            matrix_blocking.append("acceptance-criterion-shape-invalid")
            continue
        item = _mapping(row)
        criterion_id = item.get("criterion_id")
        if criterion_id not in CRITERION_IDS or criterion_id in seen:
            matrix_blocking.append("acceptance-criterion-id-invalid-or-duplicate")
            continue
        seen.append(criterion_id)
        expected = EXPECTED_ACCEPTANCE_CRITERIA[CRITERION_IDS.index(criterion_id)]
        observed = tuple(
            tuple(item.get(field))
            if field in {
                "evidence_references",
                "artifact_references",
                "test_references",
            }
            and _sequence(item.get(field))
            else item.get(field)
            for field in ACCEPTANCE_BINDING_FIELDS
        )
        state = item.get("coverage_state")
        if state not in {"covered", "partial", "missing", "blocked"}:
            matrix_blocking.append(
                f"acceptance-coverage-state-invalid:{criterion_id}"
            )
        elif state == "blocked":
            matrix_blocking.append(f"acceptance-criterion-blocked:{criterion_id}")
        elif state != "covered":
            matrix_readiness.append(
                f"acceptance-criterion-not-covered:{criterion_id}"
            )
        for field_index, key in enumerate(
            (
            "evidence_references",
            "artifact_references",
            "test_references",
            ),
            start=3,
        ):
            references = _sequence(item.get(key))
            if not references or not all(_nonempty_string(ref) for ref in references):
                matrix_readiness.append(
                    f"acceptance-criterion-reference-missing:{criterion_id}"
                )
            elif tuple(references) != expected[field_index]:
                matrix_blocking.append(
                    f"acceptance-criterion-reference-binding-invalid:"
                    f"{criterion_id}:{key}"
                )
        if item.get("criterion_text") != expected[1]:
            matrix_blocking.append(
                f"acceptance-criterion-text-binding-invalid:{criterion_id}"
            )
        if item.get("source_track") != expected[2]:
            matrix_blocking.append(
                f"acceptance-source-track-binding-invalid:{criterion_id}"
            )
        if item.get("authority_boundary") != AUTHORITY_BOUNDARY:
            matrix_blocking.append(
                f"acceptance-authority-boundary-invalid:{criterion_id}"
            )
        if item.get("notes") != EXPECTED_ACCEPTANCE_NOTE:
            matrix_blocking.append(
                f"acceptance-criterion-notes-binding-invalid:{criterion_id}"
            )
        _validate_unrestricted_prose(
            item.get("notes"),
            f"acceptance.criteria.{criterion_id}.notes",
            matrix_blocking,
        )
        if not _nonempty_string(item.get("criterion_text")) or not _nonempty_string(
            item.get("notes")
        ):
            matrix_blocking.append(
                f"acceptance-criterion-text-invalid:{criterion_id}"
            )
        if index >= len(EXPECTED_ACCEPTANCE_CRITERIA) or observed != expected:
            if not matrix_readiness:
                matrix_blocking.append(
                    f"acceptance-criterion-exact-binding-invalid:{criterion_id}"
                )
    if tuple(seen) != CRITERION_IDS:
        matrix_readiness.append("acceptance-criterion-inventory-incomplete")
    if matrix.get("caller_supplied_inert_record") is not True:
        matrix_blocking.append("acceptance-matrix-not-inert")
    if matrix.get("authority_boundary") != AUTHORITY_BOUNDARY:
        matrix_blocking.append("acceptance-matrix-authority-boundary-invalid")
    expected_complete = not matrix_readiness and not matrix_blocking
    if matrix.get("all_criteria_covered") is not expected_complete:
        matrix_blocking.append("acceptance-completion-summary-inconsistent")
    blocking.extend(matrix_blocking)
    readiness.extend(matrix_readiness)


def _validate_boundary_register(value: Any, blocking: list[str]) -> None:
    fields = frozenset(
        {
            "schema_version",
            "document_kind",
            "repository",
            "blockers",
            "future_prerequisites",
            "caller_supplied_inert_record",
            "authority_boundary",
        }
    )
    if not _exact_fields(value, fields):
        blocking.append("boundary-register-shape-invalid")
        return
    register = _mapping(value)
    if register.get("schema_version") != BOUNDARY_REGISTER_SCHEMA_VERSION:
        blocking.append("boundary-register-schema-version-invalid")
    if register.get("document_kind") != "completion-boundary-register":
        blocking.append("boundary-register-document-kind-invalid")
    if register.get("repository") != REPOSITORY:
        blocking.append("boundary-register-repository-invalid")
    blocker_fields = frozenset(
        {"blocker_id", "state", "evidence_references", "explanation"}
    )
    blockers = _sequence(register.get("blockers"))
    blocker_ids: list[str] = []
    observed_blockers: list[tuple[Any, ...]] = []
    for blocker in blockers:
        if not _exact_fields(blocker, blocker_fields):
            blocking.append("completion-blocker-shape-invalid")
            continue
        item = _mapping(blocker)
        blocker_id = item.get("blocker_id")
        if blocker_id not in REQUIRED_BLOCKERS or blocker_id in blocker_ids:
            blocking.append("completion-blocker-id-invalid-or-duplicate")
            continue
        blocker_ids.append(blocker_id)
        references = _sequence(item.get("evidence_references"))
        observed_blockers.append(
            (
                blocker_id,
                item.get("state"),
                tuple(references),
                item.get("explanation"),
            )
        )
        if item.get("state") not in {"resolved", "open", "blocked"}:
            blocking.append(f"completion-blocker-state-invalid:{blocker_id}")
        elif item.get("state") != "resolved":
            blocking.append(f"completion-blocker-unresolved:{blocker_id}")
        if not references or not all(
            _nonempty_string(reference) for reference in references
        ) or not _nonempty_string(item.get("explanation")):
            blocking.append(f"completion-blocker-resolution-evidence-missing:{blocker_id}")
        else:
            for reference_index, reference in enumerate(references):
                _validate_unrestricted_prose(
                    reference,
                    f"boundary.blockers.{blocker_id}.evidence_references.{reference_index}",
                    blocking,
                )
        _validate_unrestricted_prose(
            item.get("explanation"),
            f"boundary.blockers.{blocker_id}.explanation",
            blocking,
        )
    if tuple(blocker_ids) != REQUIRED_BLOCKERS:
        blocking.append("completion-blocker-register-incomplete")
    if tuple(observed_blockers) != EXPECTED_BLOCKER_REGISTRY:
        blocking.append("completion-blocker-registry-binding-invalid")
    future_fields = frozenset(
        {"prerequisite_id", "state", "evidence_references", "explanation"}
    )
    prerequisites = _sequence(register.get("future_prerequisites"))
    future_ids: list[str] = []
    observed_prerequisites: list[tuple[Any, ...]] = []
    for prerequisite in prerequisites:
        if not _exact_fields(prerequisite, future_fields):
            blocking.append("future-prerequisite-shape-invalid")
            continue
        item = _mapping(prerequisite)
        prerequisite_id = item.get("prerequisite_id")
        if (
            prerequisite_id not in REQUIRED_FUTURE_PREREQUISITES
            or prerequisite_id in future_ids
        ):
            blocking.append("future-prerequisite-id-invalid-or-duplicate")
            continue
        future_ids.append(prerequisite_id)
        references = _sequence(item.get("evidence_references"))
        observed_prerequisites.append(
            (
                prerequisite_id,
                item.get("state"),
                tuple(references),
                item.get("explanation"),
            )
        )
        if item.get("state") != "open":
            blocking.append(f"future-prerequisite-not-open:{prerequisite_id}")
        if not references or not all(
            _nonempty_string(reference) for reference in references
        ) or not _nonempty_string(item.get("explanation")):
            blocking.append(f"future-prerequisite-evidence-missing:{prerequisite_id}")
        else:
            for reference_index, reference in enumerate(references):
                _validate_unrestricted_prose(
                    reference,
                    "boundary.future_prerequisites."
                    f"{prerequisite_id}.evidence_references.{reference_index}",
                    blocking,
                )
        _validate_unrestricted_prose(
            item.get("explanation"),
            f"boundary.future_prerequisites.{prerequisite_id}.explanation",
            blocking,
        )
    if tuple(future_ids) != REQUIRED_FUTURE_PREREQUISITES:
        blocking.append("future-prerequisite-register-incomplete")
    if tuple(observed_prerequisites) != EXPECTED_FUTURE_PREREQUISITE_REGISTRY:
        blocking.append("future-prerequisite-registry-binding-invalid")
    if register.get("caller_supplied_inert_record") is not True:
        blocking.append("boundary-register-not-inert")
    if register.get("authority_boundary") != AUTHORITY_BOUNDARY:
        blocking.append("boundary-register-authority-boundary-invalid")


def _validate_readme_observation(value: Any, blocking: list[str]) -> None:
    fields = frozenset(
        {
            "schema_version",
            "document_kind",
            "repository",
            "source_main_base_sha",
            "base_readme_canonical_sha256",
            "candidate_readme_canonical_sha256",
            "base_releases_section_sha256",
            "candidate_releases_section_sha256",
            "base_current_status_section_sha256",
            "candidate_current_status_section_sha256",
            "base_next_phase_section_sha256",
            "candidate_next_phase_section_sha256",
            "releases_unchanged",
            "current_status_unchanged",
            "next_phase_changed",
            "future_only_wording_valid",
            "m15_complete_claim",
            "v0_14_0_released_claim",
            "tag_claim",
            "github_release_claim",
            "track_e4_completion_claim",
            "caller_supplied_inert_record",
            "authority_boundary",
        }
    )
    if not _exact_fields(value, fields):
        blocking.append("readme-observation-shape-invalid")
        return
    observation = _mapping(value)
    expected = {
        "schema_version": README_OBSERVATION_SCHEMA_VERSION,
        "document_kind": "readme-future-path-observation",
        "repository": REPOSITORY,
        "source_main_base_sha": SOURCE_MAIN_BASE_SHA,
        "base_readme_canonical_sha256": BASE_README_SHA256,
        "candidate_readme_canonical_sha256": CANDIDATE_README_SHA256,
        "base_releases_section_sha256": RELEASES_SECTION_SHA256,
        "candidate_releases_section_sha256": RELEASES_SECTION_SHA256,
        "base_current_status_section_sha256": CURRENT_STATUS_SECTION_SHA256,
        "candidate_current_status_section_sha256": CURRENT_STATUS_SECTION_SHA256,
        "base_next_phase_section_sha256": BASE_NEXT_PHASE_SHA256,
        "candidate_next_phase_section_sha256": CANDIDATE_NEXT_PHASE_SHA256,
        "releases_unchanged": True,
        "current_status_unchanged": True,
        "next_phase_changed": True,
        "future_only_wording_valid": True,
        "m15_complete_claim": False,
        "v0_14_0_released_claim": False,
        "tag_claim": False,
        "github_release_claim": False,
        "track_e4_completion_claim": False,
        "caller_supplied_inert_record": True,
        "authority_boundary": AUTHORITY_BOUNDARY,
    }
    for key, expected_value in expected.items():
        if observation.get(key) != expected_value:
            blocking.append(f"invalid-future-readme-path:{key}")


def _validate_pr_observation(
    value: Any,
    blocking: list[str],
    readiness: list[str],
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or not value:
        readiness.append("missing-e3-pr-observation")
        return {}
    fields = frozenset(
        {
            "schema_version",
            "document_kind",
            "repository",
            "issue_number",
            "pull_request_number",
            "source_main_base_sha",
            "source_main_base_tree_sha",
            "candidate_head_sha",
            "candidate_tree_sha",
            "execution_subject_type",
            "observed_at",
            "observer",
            "evidence_reference",
            "external_to_candidate_commit",
            "fetched_by_evaluator",
            "non_authoritative_boundary_statement",
        }
    )
    if not _exact_fields(value, fields):
        blocking.append("pr-observation-shape-invalid")
        return {}
    observation = _mapping(value)
    expected = {
        "schema_version": PR_OBSERVATION_SCHEMA_VERSION,
        "document_kind": "pull-request-candidate-observation",
        "repository": REPOSITORY,
        "issue_number": SOURCE_ISSUE,
        "pull_request_number": E3_PULL_REQUEST_NUMBER,
        "source_main_base_sha": SOURCE_MAIN_BASE_SHA,
        "source_main_base_tree_sha": SOURCE_MAIN_BASE_TREE_SHA,
        "execution_subject_type": "pull-request-candidate-checkout",
        "evidence_reference": E3_PR_OBSERVATION_EVIDENCE_REFERENCE,
        "external_to_candidate_commit": True,
        "fetched_by_evaluator": False,
        "non_authoritative_boundary_statement": AUTHORITY_BOUNDARY,
    }
    for key, expected_value in expected.items():
        if observation.get(key) != expected_value:
            blocking.append(f"pr-observation-binding-invalid:{key}")
    candidate = observation.get("candidate_head_sha")
    if not _object_sha(candidate) or candidate == SOURCE_MAIN_BASE_SHA:
        blocking.append("pr-observation-candidate-head-invalid")
    if not _object_sha(observation.get("candidate_tree_sha")):
        blocking.append("pr-observation-candidate-tree-invalid")
    if not _utc_timestamp(observation.get("observed_at")):
        blocking.append("pr-observation-timestamp-invalid")
    if not _nonempty_string(observation.get("observer")) or not _nonempty_string(
        observation.get("evidence_reference")
    ):
        blocking.append("pr-observation-evidence-reference-invalid")
    _validate_unrestricted_prose(
        observation.get("observer"),
        "pull_request_observation.observer",
        blocking,
    )
    return observation


def _validate_receipt(
    value: Any,
    observation: Mapping[str, Any],
    blocking: list[str],
    readiness: list[str],
) -> None:
    if not isinstance(value, Mapping) or not value:
        readiness.append("missing-external-verification-receipt")
        return
    fields = frozenset(
        {
            "schema_version",
            "document_kind",
            "repository",
            "issue_number",
            "pull_request_number",
            "source_main_base_sha",
            "execution_candidate_head_sha",
            "observation_evidence_reference",
            "command_receipt_count",
            "commands",
            "external_to_candidate_commit",
            "executed_by_evaluator",
            "verification_results_are_completion_authority",
            "verification_results_are_release_authority",
            "non_authoritative_boundary_statement",
        }
    )
    if not _exact_fields(value, fields):
        blocking.append("verification-receipt-shape-invalid")
        return
    receipt = _mapping(value)
    expected = {
        "schema_version": VERIFICATION_RECEIPT_SCHEMA_VERSION,
        "document_kind": "external-verification-execution-receipt",
        "repository": REPOSITORY,
        "issue_number": SOURCE_ISSUE,
        "pull_request_number": E3_PULL_REQUEST_NUMBER,
        "source_main_base_sha": SOURCE_MAIN_BASE_SHA,
        "observation_evidence_reference": E3_PR_OBSERVATION_EVIDENCE_REFERENCE,
        "external_to_candidate_commit": True,
        "executed_by_evaluator": False,
        "verification_results_are_completion_authority": False,
        "verification_results_are_release_authority": False,
        "non_authoritative_boundary_statement": AUTHORITY_BOUNDARY,
    }
    for key, expected_value in expected.items():
        if receipt.get(key) != expected_value:
            blocking.append(f"verification-receipt-binding-invalid:{key}")
    if observation:
        if receipt.get("pull_request_number") != observation.get(
            "pull_request_number"
        ):
            blocking.append("pr-observation-receipt-pr-mismatch")
        if receipt.get("execution_candidate_head_sha") != observation.get(
            "candidate_head_sha"
        ):
            blocking.append("pr-observation-receipt-candidate-mismatch")
        if receipt.get("observation_evidence_reference") != observation.get(
            "evidence_reference"
        ):
            blocking.append("pr-observation-receipt-reference-mismatch")
    commands = _sequence(receipt.get("commands"))
    if receipt.get("command_receipt_count") != len(COMMAND_IDS) or len(commands) != len(
        COMMAND_IDS
    ):
        blocking.append("verification-command-coverage-incomplete")
    command_fields = frozenset(
        {
            "command_id",
            "declared_logical_argv",
            "actual_argv",
            "execution_scope",
            "execution_candidate_head_sha",
            "executable_binding",
            "tests_observed",
            "minimum_tests_observed",
            "passes",
            "failures",
            "errors",
            "skips",
            "exit_code",
            "execution_timestamp",
            "transcript_sha256",
            "evidence_reference",
            "executed_by_evaluator",
            "verification_results_are_completion_authority",
            "verification_results_are_release_authority",
        }
    )
    binding_fields = frozenset(
        {
            "declared_launcher",
            "actual_launcher",
            "launcher_substitution_detected",
            "launcher_substitution_declared",
            "python_implementation",
            "python_version",
        }
    )
    seen: list[str] = []
    observed_registry: list[tuple[Any, ...]] = []
    for command in commands:
        if not _exact_fields(command, command_fields):
            blocking.append("verification-command-receipt-shape-invalid")
            continue
        item = _mapping(command)
        command_id = item.get("command_id")
        if command_id not in COMMAND_MINIMA or command_id in seen:
            blocking.append("verification-command-id-invalid-or-duplicate")
            continue
        seen.append(command_id)
        expected_command = EXPECTED_VERIFICATION_COMMANDS[
            COMMAND_IDS.index(command_id)
        ]
        minimum = expected_command[3]
        if item.get("minimum_tests_observed") != minimum:
            blocking.append(f"verification-minimum-binding-invalid:{command_id}")
        counts = (
            item.get("tests_observed"),
            item.get("passes"),
            item.get("failures"),
            item.get("errors"),
            item.get("skips"),
            item.get("exit_code"),
        )
        if not all(isinstance(count, int) and count >= 0 for count in counts):
            blocking.append(f"verification-count-invalid:{command_id}")
            continue
        observed, passes, failures, errors, skips, exit_code = counts
        if passes + failures + errors + skips != observed:
            blocking.append(f"verification-count-arithmetic-invalid:{command_id}")
        if observed < minimum:
            blocking.append(f"verification-below-minimum:{command_id}")
        if failures:
            blocking.append(f"verification-failure:{command_id}")
        if errors:
            blocking.append(f"verification-error:{command_id}")
        if exit_code:
            blocking.append(f"verification-nonzero-exit:{command_id}")
        if skips:
            readiness.append(f"verification-unexpected-skip:{command_id}")
        declared = _sequence(item.get("declared_logical_argv"))
        actual = _sequence(item.get("actual_argv"))
        observed_command = (
            command_id,
            tuple(declared),
            item.get("execution_scope"),
            item.get("minimum_tests_observed"),
        )
        observed_registry.append(observed_command)
        if observed_command != expected_command:
            blocking.append(
                f"verification-command-registry-binding-invalid:{command_id}"
            )
        if (
            not declared
            or not actual
            or declared[0] != "python"
            or actual[0] != ".verification-python/python.exe"
            or tuple(actual[1:]) != expected_command[1][1:]
        ):
            blocking.append(f"verification-argv-binding-invalid:{command_id}")
        binding = item.get("executable_binding")
        if not _exact_fields(binding, binding_fields):
            blocking.append(f"verification-launcher-binding-shape-invalid:{command_id}")
        else:
            expected_binding = {
                "declared_launcher": "python",
                "actual_launcher": ".verification-python/python.exe",
                "launcher_substitution_detected": True,
                "launcher_substitution_declared": True,
                "python_implementation": "CPython",
                "python_version": "3.14.6",
            }
            if dict(_mapping(binding)) != expected_binding:
                blocking.append(f"verification-launcher-binding-invalid:{command_id}")
        if item.get("execution_candidate_head_sha") != receipt.get(
            "execution_candidate_head_sha"
        ):
            blocking.append(f"verification-candidate-binding-invalid:{command_id}")
        if not _utc_timestamp(item.get("execution_timestamp")):
            blocking.append(f"verification-timestamp-invalid:{command_id}")
        if not _sha256(item.get("transcript_sha256")) or not _nonempty_string(
            item.get("evidence_reference")
        ):
            blocking.append(f"verification-transcript-binding-invalid:{command_id}")
        _validate_unrestricted_prose(
            item.get("evidence_reference"),
            f"external_verification_receipt.commands.{command_id}.evidence_reference",
            blocking,
        )
        if (
            item.get("executed_by_evaluator") is not False
            or item.get("verification_results_are_completion_authority") is not False
            or item.get("verification_results_are_release_authority") is not False
        ):
            blocking.append(f"verification-authority-claim:{command_id}")
    if tuple(seen) != COMMAND_IDS:
        blocking.append("verification-command-order-invalid")
    if tuple(observed_registry) != EXPECTED_VERIFICATION_COMMANDS:
        blocking.append("verification-command-registry-invalid")


def _build_result(blocking: list[str], readiness: list[str]) -> dict[str, Any]:
    blocking_findings = sorted(set(blocking))
    readiness_findings = sorted(set(readiness))
    outcome = BLOCKED if blocking_findings else NOT_READY if readiness_findings else READY
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "outcome": outcome,
        "blocking_findings": blocking_findings,
        "readiness_findings": readiness_findings,
        "findings": sorted(set(blocking_findings + readiness_findings)),
        "caller_data_only": True,
        "file_io_performed": False,
        "git_inspection_performed": False,
        "github_access_performed": False,
        "network_access_performed": False,
        "repository_digests_calculated": False,
        "verification_commands_executed": False,
        "external_state_mutated": False,
        "m15_state": "active-and-incomplete",
        "tracker_231_state": "open",
        "track_e4_implemented": False,
        "v0_14_0_state": "unpublished",
        "tag_state": "not-authorized",
        "github_release_state": "not-created",
        "decision_proof_sealed": False,
        "learning_proof_sealed": False,
        "non_authoritative_boundary_statement": AUTHORITY_BOUNDARY,
    }


def evaluate_completion_readiness(
    manifest: Mapping[str, Any],
    track_evidence_inventory: Mapping[str, Any],
    e2_continuity_record: Mapping[str, Any],
    e2_external_evidence: Mapping[str, Any],
    acceptance_coverage_matrix: Mapping[str, Any],
    boundary_register: Mapping[str, Any],
    readme_observation: Mapping[str, Any],
    pull_request_observation: Mapping[str, Any],
    external_verification_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    """Evaluate nine inert caller mappings without external operations."""

    blocking: list[str] = []
    readiness: list[str] = []
    values = (
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
    for value in values:
        _authority_findings(value, blocking)
    _validate_manifest(manifest, blocking)
    _validate_inventory(track_evidence_inventory, blocking)
    _validate_e2_continuity(e2_continuity_record, blocking)
    _validate_e2_external(e2_external_evidence, blocking)
    _validate_acceptance_matrix(acceptance_coverage_matrix, blocking, readiness)
    _validate_boundary_register(boundary_register, blocking)
    _validate_readme_observation(readme_observation, blocking)
    observation = _validate_pr_observation(
        pull_request_observation,
        blocking,
        readiness,
    )
    _validate_receipt(
        external_verification_receipt,
        observation,
        blocking,
        readiness,
    )
    return _build_result(blocking, readiness)


__all__ = [
    "ACCEPTANCE_MATRIX_SCHEMA_VERSION",
    "ACCEPTANCE_BINDING_FIELDS",
    "ARTIFACT_BINDING_FIELDS",
    "AUTHORIZED_HISTORICAL_COMPATIBILITY_REPAIRS",
    "AUTHORIZED_PHASE_AWARE_COMPATIBILITY_REPAIR",
    "AUTHORITY_BOUNDARY",
    "BLOCKED",
    "BOUNDARY_REGISTER_SCHEMA_VERSION",
    "COMMAND_IDS",
    "COMMAND_MINIMA",
    "COMPATIBILITY_REPAIR_AUTHORIZATION_BASIS",
    "COMPATIBILITY_REPAIR_NOT_AUTHORIZED",
    "COMPATIBILITY_REPAIR_PURPOSE",
    "CRITERION_IDS",
    "E3_PR_OBSERVATION_EVIDENCE_REFERENCE",
    "E3_PULL_REQUEST_NUMBER",
    "E1_SOURCE_BASELINE_SHA",
    "E2_CONTINUITY_SCHEMA_VERSION",
    "E2_EXTERNAL_EVIDENCE_SCHEMA_VERSION",
    "E3_AUTHORIZED_COMPATIBILITY_REPAIR",
    "EXPECTED_ACCEPTANCE_NOTE",
    "EXPECTED_ACCEPTANCE_CRITERIA",
    "EXPECTED_ARTIFACT_BINDINGS",
    "EXPECTED_BLOCKER_REGISTRY",
    "EXPECTED_FUTURE_PREREQUISITE_REGISTRY",
    "EXPECTED_VERIFICATION_COMMANDS",
    "HISTORICAL_E1_ARTIFACT_BINDING",
    "MANIFEST_SCHEMA_VERSION",
    "NOT_READY",
    "OUTCOMES",
    "PR_OBSERVATION_SCHEMA_VERSION",
    "README_OBSERVATION_SCHEMA_VERSION",
    "READY",
    "REQUIRED_BLOCKERS",
    "REQUIRED_FUTURE_PREREQUISITES",
    "RUNTIME_BOUNDARY",
    "SCENARIO_SCHEMA_VERSION",
    "TRACK_EVIDENCE_SCHEMA_VERSION",
    "VERIFICATION_RECEIPT_SCHEMA_VERSION",
    "evaluate_completion_readiness",
]
