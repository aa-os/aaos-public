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

# Bound to the discoverable focused E3 suite and prior maintained baseline.
E3_TARGETED_MINIMUM = 151
FULL_SUITE_MINIMUM = 2076
COMMAND_MINIMA = {
    "e3-targeted": E3_TARGETED_MINIMUM,
    "e2-targeted": 140,
    "e1-targeted": 132,
    "track-a": 68,
    "track-b": 73,
    "track-c": 181,
    "track-d": 79,
    "m14-public-output": 23,
    "m14-provenance": 47,
    "m14-skill-admission": 135,
    "external-evidence-admission": 31,
    "m14-cross-control-authority": 107,
    "decision-proof-ownership": 30,
    "release-m15-status": 18,
    "full-maintained-suite": FULL_SUITE_MINIMUM,
    "m14-final-completion": 110,
    "m14-completion-readiness": 112,
}
COMMAND_IDS = tuple(COMMAND_MINIMA)

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
    if tuple(seen) != COMMAND_IDS:
        blocking.append("manifest-verification-command-order-invalid")


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
    for artifact in artifacts:
        if not _exact_fields(artifact, ARTIFACT_FIELDS):
            blocking.append("artifact-shape-invalid")
            continue
        item = _mapping(artifact)
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
    if matrix.get("schema_version") != ACCEPTANCE_MATRIX_SCHEMA_VERSION:
        blocking.append("acceptance-matrix-schema-version-invalid")
    if matrix.get("document_kind") != "m15-acceptance-coverage-matrix":
        blocking.append("acceptance-matrix-document-kind-invalid")
    if matrix.get("repository") != REPOSITORY or matrix.get(
        "parent_tracker"
    ) != PARENT_TRACKER:
        blocking.append("acceptance-matrix-repository-binding-invalid")
    criteria = _sequence(matrix.get("criteria"))
    if matrix.get("criterion_count") != len(CRITERION_IDS) or len(criteria) != len(
        CRITERION_IDS
    ):
        readiness.append("incomplete-acceptance-criteria-coverage")
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
    for row in criteria:
        if not _exact_fields(row, row_fields):
            blocking.append("acceptance-criterion-shape-invalid")
            continue
        item = _mapping(row)
        criterion_id = item.get("criterion_id")
        if criterion_id not in CRITERION_IDS or criterion_id in seen:
            blocking.append("acceptance-criterion-id-invalid-or-duplicate")
            continue
        seen.append(criterion_id)
        state = item.get("coverage_state")
        if state not in {"covered", "partial", "missing", "blocked"}:
            blocking.append(f"acceptance-coverage-state-invalid:{criterion_id}")
        elif state == "blocked":
            blocking.append(f"acceptance-criterion-blocked:{criterion_id}")
        elif state != "covered":
            readiness.append(f"acceptance-criterion-not-covered:{criterion_id}")
        for key in (
            "evidence_references",
            "artifact_references",
            "test_references",
        ):
            references = _sequence(item.get(key))
            if not references or not all(_nonempty_string(ref) for ref in references):
                readiness.append(f"acceptance-criterion-reference-missing:{criterion_id}")
        if item.get("source_track") not in {
            *TRACK_COUNTS,
            "cross-track",
            "track-e3",
        }:
            blocking.append(f"acceptance-source-track-invalid:{criterion_id}")
        if item.get("authority_boundary") != AUTHORITY_BOUNDARY:
            blocking.append(f"acceptance-authority-boundary-invalid:{criterion_id}")
        if not _nonempty_string(item.get("criterion_text")) or not _nonempty_string(
            item.get("notes")
        ):
            blocking.append(f"acceptance-criterion-text-invalid:{criterion_id}")
    if tuple(seen) != CRITERION_IDS:
        readiness.append("acceptance-criterion-inventory-incomplete")
    expected_complete = not readiness and not blocking
    if matrix.get("all_criteria_covered") is not expected_complete:
        blocking.append("acceptance-completion-summary-inconsistent")
    if matrix.get("caller_supplied_inert_record") is not True:
        blocking.append("acceptance-matrix-not-inert")
    if matrix.get("authority_boundary") != AUTHORITY_BOUNDARY:
        blocking.append("acceptance-matrix-authority-boundary-invalid")


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
        if item.get("state") not in {"resolved", "open", "blocked"}:
            blocking.append(f"completion-blocker-state-invalid:{blocker_id}")
        elif item.get("state") != "resolved":
            blocking.append(f"completion-blocker-unresolved:{blocker_id}")
        if not _sequence(item.get("evidence_references")) or not _nonempty_string(
            item.get("explanation")
        ):
            blocking.append(f"completion-blocker-resolution-evidence-missing:{blocker_id}")
    if tuple(blocker_ids) != REQUIRED_BLOCKERS:
        blocking.append("completion-blocker-register-incomplete")
    future_fields = frozenset(
        {"prerequisite_id", "state", "evidence_references", "explanation"}
    )
    prerequisites = _sequence(register.get("future_prerequisites"))
    future_ids: list[str] = []
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
        if item.get("state") != "open":
            blocking.append(f"future-prerequisite-not-open:{prerequisite_id}")
        if not _sequence(item.get("evidence_references")) or not _nonempty_string(
            item.get("explanation")
        ):
            blocking.append(f"future-prerequisite-evidence-missing:{prerequisite_id}")
    if tuple(future_ids) != REQUIRED_FUTURE_PREREQUISITES:
        blocking.append("future-prerequisite-register-incomplete")
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
        "source_main_base_sha": SOURCE_MAIN_BASE_SHA,
        "source_main_base_tree_sha": SOURCE_MAIN_BASE_TREE_SHA,
        "execution_subject_type": "pull-request-candidate-checkout",
        "external_to_candidate_commit": True,
        "fetched_by_evaluator": False,
        "non_authoritative_boundary_statement": AUTHORITY_BOUNDARY,
    }
    for key, expected_value in expected.items():
        if observation.get(key) != expected_value:
            blocking.append(f"pr-observation-binding-invalid:{key}")
    if not isinstance(observation.get("pull_request_number"), int) or observation.get(
        "pull_request_number"
    ) <= 0:
        blocking.append("pr-observation-pull-request-number-invalid")
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
        "source_main_base_sha": SOURCE_MAIN_BASE_SHA,
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
        minimum = COMMAND_MINIMA[command_id]
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
        if (
            not declared
            or not actual
            or declared[0] != "python"
            or actual[0] != ".verification-python/python.exe"
            or list(declared[1:]) != list(actual[1:])
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
        if (
            item.get("executed_by_evaluator") is not False
            or item.get("verification_results_are_completion_authority") is not False
            or item.get("verification_results_are_release_authority") is not False
        ):
            blocking.append(f"verification-authority-claim:{command_id}")
    if tuple(seen) != COMMAND_IDS:
        blocking.append("verification-command-order-invalid")


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
    "E1_SOURCE_BASELINE_SHA",
    "E2_CONTINUITY_SCHEMA_VERSION",
    "E2_EXTERNAL_EVIDENCE_SCHEMA_VERSION",
    "E3_AUTHORIZED_COMPATIBILITY_REPAIR",
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
