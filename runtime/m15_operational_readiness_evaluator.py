"""Deterministic, offline evaluator for the M15 Track E1 readiness record.

The evaluator reads inert repository text and compares it with the reviewed
maintained-main inventory.  It does not invoke source evaluators, execute the
verification command manifest, inspect Git or GitHub, mutate files, or grant
completion or release authority.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from runtime.repository_artifact_digest import (
    RepositoryArtifactFileTypeError,
    RepositoryArtifactPathError,
    RepositoryArtifactTextError,
    sha256_repository_file,
)


MANIFEST_SCHEMA_VERSION = "m15-operational-readiness/v1"
SCENARIO_SCHEMA_VERSION = "m15-operational-readiness-scenario/v1"
RESULT_SCHEMA_VERSION = "m15-operational-readiness-result/v1"
MAINTAINED_MAIN_SHA = "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f"
MANIFEST_PATH = (
    "examples/public-integration-pack-pilot/"
    "m15-operational-readiness-manifest.json"
)
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

READY_FOR_COMPLETION_REVIEW = "ready_for_completion_review"
NOT_READY = "not_ready"
BLOCKED = "blocked"
OUTCOMES = (
    READY_FOR_COMPLETION_REVIEW,
    NOT_READY,
    BLOCKED,
)

NON_AUTHORITATIVE_BOUNDARY_STATEMENT = (
    "ready_for_completion_review is evidence for a later human completion "
    "review only; it is not M15 completion approval, tracker #231 closure, "
    "README completion or release authorization, tag authorization, release "
    "authorization, or GitHub Release publication authorization."
)
SYNTHETIC_SCENARIO_BOUNDARY_STATEMENT = (
    "This standalone scenario is synthetic, inert, offline, and "
    "non-authoritative. " + NON_AUTHORITATIVE_BOUNDARY_STATEMENT
)

_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")

EXPECTED_SCENARIO_TITLES = {
    "m15-e1-01": "Valid maintained-main operational-readiness evidence",
    "m15-e1-02": "Maintained-main commit binding mismatch",
    "m15-e1-03": "Merged source-track binding mismatch",
    "m15-e1-04": "Incomplete Track A-D artifact inventory",
    "m15-e1-05": "Maintained artifact integrity failure",
    "m15-e1-06": "Operational-readiness internal consistency failure",
    "m15-e1-07": "Track D cross-control matrix is not bound",
    "m15-e1-08": "Deterministic test coverage is incomplete",
    "m15-e1-09": "Verification-command manifest is incomplete",
    "m15-e1-10": "Verification manifest claims command execution",
    "m15-e1-11": "Operational readiness claims completion approval",
    "m15-e1-12": "Operational readiness claims tracker closure",
    "m15-e1-13": "Operational readiness claims M15 completion",
    "m15-e1-14": "Operational readiness claims README authorization",
    "m15-e1-15": "Operational readiness claims tag authority or creation",
    "m15-e1-16": "Operational readiness claims release authority or publication",
    "m15-e1-17": "Known repository-local completion blocker remains unresolved",
    "m15-e1-18": "Unsupported operational-readiness scenario schema version",
}


def _paths(prefix: str, names: Sequence[str]) -> list[str]:
    return [f"{prefix}{name}" for name in names]


_TRACK_FIXTURES: dict[str, list[str]] = {
    "track-a": _paths(
        "examples/public-integration-pack-pilot/",
        [
            "m15-learning-proof-approved-evaluation-only.json",
            "m15-learning-proof-contaminated-quarantine.json",
            "m15-learning-proof-rejected-untrusted-correction.json",
        ],
    ),
    "track-b": _paths(
        "examples/public-integration-pack-pilot/",
        [
            "m15-capability-pack-altered-derived-specification.json",
            "m15-capability-pack-altered-graph.json",
            "m15-capability-pack-executable-authority-claim.json",
            "m15-capability-pack-incompatible-runtime.json",
            "m15-capability-pack-missing-license-usage-boundary-evidence.json",
            "m15-capability-pack-revoked.json",
            "m15-capability-pack-source-digest-mismatch.json",
            "m15-capability-pack-stale-specification.json",
            "m15-capability-pack-valid-verified.json",
        ],
    ),
    "track-c": _paths(
        "examples/public-integration-pack-pilot/",
        [
            "m15-lineage-rollback-portability-decision-proof-deletion-execution-authority.json",
            "m15-lineage-rollback-portability-deletion-pending-unresolved-copies.json",
            "m15-lineage-rollback-portability-false-physical-provider-erasure-claim.json",
            "m15-lineage-rollback-portability-learning-proof-rollback-authority.json",
            "m15-lineage-rollback-portability-missing-downstream-dependency-declaration.json",
            "m15-lineage-rollback-portability-model-removal-drill-provider-specific-blocker.json",
            "m15-lineage-rollback-portability-model-removal-drill-success.json",
            "m15-lineage-rollback-portability-qualified-deleted-no-physical-erasure.json",
            "m15-lineage-rollback-portability-replacement-model-use-incorrectly-authorized.json",
            "m15-lineage-rollback-portability-revoked-capability-pack-unresolved-downstream-use.json",
            "m15-lineage-rollback-portability-rollback-blocked-incompatible-dependent.json",
            "m15-lineage-rollback-portability-rollback-ready-complete-dependency-evidence.json",
            "m15-lineage-rollback-portability-superseded-learning-artifact-known-dependents.json",
            "m15-lineage-rollback-portability-valid-complete-dependency-graph.json",
        ],
    ),
    "track-d": _paths(
        "examples/public-integration-pack-pilot/",
        [f"m15-cross-control-{number:02d}.json" for number in range(1, 25)],
    ),
}

_TRACK_METADATA = {
    "track-a": {
        "source_issue": "#232",
        "implementation_pr": "#233",
        "head_sha": "603a26890ceee940b0a3c9009e06d994f9f2f342",
        "merge_sha": "6e0fa4e8fdf4a672581cd897d52743d0462f0d4b",
        "schema_version": "m15-learning-proof/v1",
        "test_module": "tests.test_m15_learning_proof_evaluator",
        "contract": "docs/learning-governance/m15-core-learning-proof-contract.md",
        "schema": "schemas/m15-learning-proof.schema.json",
        "evaluator": "runtime/m15_learning_proof_evaluator.py",
        "test": "tests/test_m15_learning_proof_evaluator.py",
    },
    "track-b": {
        "source_issue": "#234",
        "implementation_pr": "#237",
        "head_sha": "270a5bbb536c6bf0726e95455d4bb61ac86d693e",
        "merge_sha": "8e475518f2da6232ae9a6264d8e9c9f1e5fc514a",
        "schema_version": "m15-capability-memory-pack/v1",
        "test_module": "tests.test_m15_capability_memory_pack_evaluator",
        "contract": "docs/learning-governance/m15-capability-memory-pack-contract.md",
        "schema": "schemas/m15-capability-memory-pack.schema.json",
        "evaluator": "runtime/m15_capability_memory_pack_evaluator.py",
        "test": "tests/test_m15_capability_memory_pack_evaluator.py",
    },
    "track-c": {
        "source_issue": "#238",
        "implementation_pr": "#239",
        "head_sha": "5f98f6c86e6b61d50b1c8183aca0736a3419c533",
        "merge_sha": "2d8bab3a84675543c34231a9e04521379febdac1",
        "schema_version": "m15-lineage-rollback-portability/v1",
        "test_module": "tests.test_m15_lineage_rollback_portability_evaluator",
        "contract": "docs/learning-governance/m15-lineage-rollback-portability-contract.md",
        "schema": "schemas/m15-lineage-rollback-portability.schema.json",
        "evaluator": "runtime/m15_lineage_rollback_portability_evaluator.py",
        "test": "tests/test_m15_lineage_rollback_portability_evaluator.py",
    },
    "track-d": {
        "source_issue": "#240",
        "implementation_pr": "#241",
        "head_sha": "3bec19e42693b757b9abbb077146ca9860d48c1e",
        "merge_sha": MAINTAINED_MAIN_SHA,
        "schema_version": "m15-cross-control-regression/v1",
        "test_module": "tests.test_m15_cross_control_regression_evaluator",
        "contract": "docs/learning-governance/m15-cross-control-regression-contract.md",
        "schema": "schemas/m15-cross-control-regression.schema.json",
        "evaluator": "runtime/m15_cross_control_regression_evaluator.py",
        "test": "tests/test_m15_cross_control_regression_evaluator.py",
        "matrix": "examples/public-integration-pack-pilot/m15-cross-control-matrix.json",
    },
}


def _required_artifacts() -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for track_id, metadata in _TRACK_METADATA.items():
        common = {
            "track_id": track_id,
            "source_issue": metadata["source_issue"],
            "implementation_pr": metadata["implementation_pr"],
            "test_module": metadata["test_module"],
        }
        for role in ("contract", "schema", "evaluator", "test"):
            result[metadata[role]] = {**common, "artifact_type": role}
        for fixture_path in _TRACK_FIXTURES[track_id]:
            result[fixture_path] = {**common, "artifact_type": "fixture"}
        matrix_path = metadata.get("matrix")
        if matrix_path:
            result[matrix_path] = {
                **common,
                "artifact_type": "cross-control-matrix",
            }
    return result


REQUIRED_ARTIFACTS = _required_artifacts()
EXPECTED_MAINTAINED_ARTIFACT_DIGESTS = {
    "docs/learning-governance/m15-capability-memory-pack-contract.md": "10152aea4911711c09edbb21bb78696244f9e71fe8447d9737a907eb8a3bb9df",
    "docs/learning-governance/m15-core-learning-proof-contract.md": "b28de6f87b675e96db229a71dd0b34d54e5e065fd0f9205cb56b3018fddacae3",
    "docs/learning-governance/m15-cross-control-regression-contract.md": "23f29596100bd85fb52bc46210548a9404c21bf10d532d692d7fc43b84d64fdf",
    "docs/learning-governance/m15-lineage-rollback-portability-contract.md": "d6c421be2fede2480f8bc2f3c8b0221e1862273184915b2ed317e69357c60f47",
    "examples/public-integration-pack-pilot/m15-capability-pack-altered-derived-specification.json": "23f2502a23422d14215860d4dda5a154254365224909d4ac9a2c8a0eb8b3ed22",
    "examples/public-integration-pack-pilot/m15-capability-pack-altered-graph.json": "1193ba3eeb7c1462816a7b1fbf1a6d9ae16ac11a22b5c315715378d95565a564",
    "examples/public-integration-pack-pilot/m15-capability-pack-executable-authority-claim.json": "6e74d48b6f974a66f1187c7cefbaf45a8721c252a7c31bc84f250c828dde06e4",
    "examples/public-integration-pack-pilot/m15-capability-pack-incompatible-runtime.json": "2d585df48eb9899f80f3558767341c7d492bce14ee155552fad9f9571d6e31cf",
    "examples/public-integration-pack-pilot/m15-capability-pack-missing-license-usage-boundary-evidence.json": "2b6a9e3a8eae10299cd069bd938643c170669ce2eabce9f0200d2a981849a5de",
    "examples/public-integration-pack-pilot/m15-capability-pack-revoked.json": "797a42b9c816acccd31759cb7b40a066ab70bcaa19683dc0ddbe66421fc538a3",
    "examples/public-integration-pack-pilot/m15-capability-pack-source-digest-mismatch.json": "60041c22641c33104f2d990829a873dbc68b865fc31396b030ec60411f270e3a",
    "examples/public-integration-pack-pilot/m15-capability-pack-stale-specification.json": "92ee515bd75303c77531ce2efb9dc445368e1cebe5e61cea1e3f4f073375cbca",
    "examples/public-integration-pack-pilot/m15-capability-pack-valid-verified.json": "66a601ed0f289e785f37e629a4fdc839186c22a93dabc6cec6387b0f188b97d8",
    "examples/public-integration-pack-pilot/m15-cross-control-01.json": "96a657018d7a8be20faf90523957a4ccec0537f5b853f180c818710c17de975f",
    "examples/public-integration-pack-pilot/m15-cross-control-02.json": "cdc696021de2603bb99114d253210eb7ce005527b74d22dbc9dc5dcf178c88db",
    "examples/public-integration-pack-pilot/m15-cross-control-03.json": "aa91eb15b431723c4d99550cd38ea3e1a63a064f7b641f58960e295c942525c7",
    "examples/public-integration-pack-pilot/m15-cross-control-04.json": "6d96c04a17dda4928caf8cf332252a17599b3e146a210affefaa1ee6eae6374d",
    "examples/public-integration-pack-pilot/m15-cross-control-05.json": "bcd86d84b9a2d24615764f4d4f5046c7e19d0f6bc0eddf28790f51c1d54896fb",
    "examples/public-integration-pack-pilot/m15-cross-control-06.json": "6c70e7efa7000e76574815ddb593635c6bd48641ba36c12aa3d662de194b524b",
    "examples/public-integration-pack-pilot/m15-cross-control-07.json": "3a4e8ae6456c76d0fab6111055ab4cc8f6b179a403e87ea6af13e535391d2752",
    "examples/public-integration-pack-pilot/m15-cross-control-08.json": "201f4b3eb1d7c87329f3e40b0602f8556a0b3fddc8501999b1f2e61ba194adfc",
    "examples/public-integration-pack-pilot/m15-cross-control-09.json": "8e7c85f22fe9ef0e66dbf29d88ddf35507ce3daf730eb5c467f3585b038cb9f8",
    "examples/public-integration-pack-pilot/m15-cross-control-10.json": "b9ff7b587f1ebffa9a4994802e356915ea0c4c91bb83402493ed37747c202e98",
    "examples/public-integration-pack-pilot/m15-cross-control-11.json": "3a98010d7cea9ff288f47646721c189bb9019e3285959c6fae3018c8a6b783b3",
    "examples/public-integration-pack-pilot/m15-cross-control-12.json": "16b109d3938a7befb0e6947cef5e52e5bf922ba6389ffeb920a696f3f4049c49",
    "examples/public-integration-pack-pilot/m15-cross-control-13.json": "391a15a1641c4c8e172ea9128a1bbe5c55c60d672b8ec4f3c10ac712f7216841",
    "examples/public-integration-pack-pilot/m15-cross-control-14.json": "bc0c3ac7a5f04e0a25684652d4e966b3e704514ac98454f98037ae1e52dc8693",
    "examples/public-integration-pack-pilot/m15-cross-control-15.json": "48e2ac1afb874f9b95a7f812df7bcb30ed3f06cc978be3b6118353cf0dd11806",
    "examples/public-integration-pack-pilot/m15-cross-control-16.json": "0def119664507d11c91927a966055156b2be3c8e7a635d68b17ea8e23ad28497",
    "examples/public-integration-pack-pilot/m15-cross-control-17.json": "f3b8bbcb6157738873aa1f6db18ce7bfbfdfa40d4e0ca75a5b7232d96d038b9a",
    "examples/public-integration-pack-pilot/m15-cross-control-18.json": "62ffa63f03979736e98f74da38bf5830e01cdaf8e77b5502f2ed85af0de1f629",
    "examples/public-integration-pack-pilot/m15-cross-control-19.json": "a4621c85ee076e2bdc8af6811f4a12f1eb166c2c9f89d6a9bfe65a69f0beae4b",
    "examples/public-integration-pack-pilot/m15-cross-control-20.json": "af2568e0286541a8e44b0be3580914c3cd558490e19acf0d8406f505aaf947b6",
    "examples/public-integration-pack-pilot/m15-cross-control-21.json": "3f9806c2700c359f7241d26c348dd18b6595ecd1ad115af9e583a609694d8ab4",
    "examples/public-integration-pack-pilot/m15-cross-control-22.json": "5dae89de53a3698dde0fc598e63b1e34d7a2b9ceff66f041475d022afcfe4060",
    "examples/public-integration-pack-pilot/m15-cross-control-23.json": "6402079bda56eb8a086613ef1e3541d42f0fbe5f546570e19b964b4ab729bcfa",
    "examples/public-integration-pack-pilot/m15-cross-control-24.json": "1da9dc250c9e3676257e93f4736133f5ec17d438e0c667f675ab1caf8d415c7c",
    "examples/public-integration-pack-pilot/m15-cross-control-matrix.json": "9d05d2a5331b02d673b2ee2c01e05e0aa098e981d10b9b072a8b92af226b0ca0",
    "examples/public-integration-pack-pilot/m15-learning-proof-approved-evaluation-only.json": "56209ec5b821dab72f23e02b9472de8323353d706e60ec431e147c2208316db0",
    "examples/public-integration-pack-pilot/m15-learning-proof-contaminated-quarantine.json": "8d1d1d46bfca7d4110978e17e7139041305b068979ee62cea939291138e91971",
    "examples/public-integration-pack-pilot/m15-learning-proof-rejected-untrusted-correction.json": "bf4c915b14fd968e5f50dc8b10b70edc9a56db54a13120891b9a7fedf9203ba8",
    "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-decision-proof-deletion-execution-authority.json": "25f6ec6fcb7ec0e47ed125ffb2e328bddeba30f50a81a4ac1ecf4afb37b4812d",
    "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-deletion-pending-unresolved-copies.json": "b710d26212866fa40bcb4335385194449113758a102a59c0ddac2cc36332fc4b",
    "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-false-physical-provider-erasure-claim.json": "528b31423f15fd08c3b633ab2d079ed3ec5fdc5424cf3886755673931d439b6b",
    "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-learning-proof-rollback-authority.json": "437d5afb63e3b7cbac8bc791d198a38712acf755221a3af664412b94c238cdcc",
    "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-missing-downstream-dependency-declaration.json": "fd3c8a08e02916523848a5ce8b0f544a741f65549ebd5e2e60fba70991fd1acb",
    "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-model-removal-drill-provider-specific-blocker.json": "14c4baacce910250ac45d540abebd29581e023875a22e1a88f2d3b2dcd946e25",
    "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-model-removal-drill-success.json": "4d39580e90388765d8dcea32f3d6c9001463ddae5a3047a5e388e1721ec5a221",
    "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-qualified-deleted-no-physical-erasure.json": "d42011b3a5ba913bc5c3170c09273ec3170a8d3be613a33b178e19299a3a1dc2",
    "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-replacement-model-use-incorrectly-authorized.json": "82e419a91dfe334355dde8f263645e011782a83c91484fb2b0b79c803ecdd3c8",
    "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-revoked-capability-pack-unresolved-downstream-use.json": "1bdbd1bc3f61e1a83973da8dd466468844377831d8436d7c8f787a259a15fe3b",
    "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-rollback-blocked-incompatible-dependent.json": "b6f48aed01b78b7489bc364e8537ce0916fa1b7defed49a9cd15b9ea322e8579",
    "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-rollback-ready-complete-dependency-evidence.json": "0ad2376f0359f75b0afd38432ce4c921e2466f2b60732c98a1bb24b3a7db788f",
    "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-superseded-learning-artifact-known-dependents.json": "8cc561a8bdc9c38641ea2522c466b910ce29590872f7645ec2207eeb58559dc7",
    "examples/public-integration-pack-pilot/m15-lineage-rollback-portability-valid-complete-dependency-graph.json": "a3c4e3c1c99341d07ff04612514d2abc25852acefd643b45852e98287de572fd",
    "runtime/m15_capability_memory_pack_evaluator.py": "5e45bbe0f311c3bfcc4d10ed7dc2b1eacbb8d64e4d8d2c922e74d558e66181e2",
    "runtime/m15_cross_control_regression_evaluator.py": "4a412bbd215ed3974d842bc09ee0011b4148f849d5d8e91611a324ef83fc6af6",
    "runtime/m15_learning_proof_evaluator.py": "1f0d1eda01e3df92fba069ffd75eff34232c7bfe39f0b252b80cae2d1a2f00c8",
    "runtime/m15_lineage_rollback_portability_evaluator.py": "4337f04d0619f4e153088fe080fac7d1a2d976e3e04f6a124169e3d96c73f6a4",
    "schemas/m15-capability-memory-pack.schema.json": "051436c094413715849ddffd8b54beebb7239f8f288fd2849c333b412e374351",
    "schemas/m15-cross-control-regression.schema.json": "d52ef7010f596e28592c738b536f0d3131e60c5886ed538f1a57a067c675d651",
    "schemas/m15-learning-proof.schema.json": "c03bd734f287fae23deb7f8d3eaf2ccb501774caeccbe85d6520c57b7fdc1a44",
    "schemas/m15-lineage-rollback-portability.schema.json": "8702925c5a2c62efb77fc44cb68328f5be04b963afa27f366f99bef2ee071949",
    "tests/test_m15_capability_memory_pack_evaluator.py": "806eb6fe660465a5ac72f553cb336cbe3822170218040f7f036e60d4680a28db",
    "tests/test_m15_cross_control_regression_evaluator.py": "472b75a13498fbc257bbca9cf6eabba688e07cb236f36e3778587b0025415c78",
    "tests/test_m15_learning_proof_evaluator.py": "d382b1239bb623f3d165b24bda830a285f1aeaee93e53b9dc9abb8ada7b6b6c4",
    "tests/test_m15_lineage_rollback_portability_evaluator.py": "5268f73a441898467e9b8f9471cfc4b9bd4fa27b7b67444fbf852d697d90f4c9",
}
EXPECTED_TRACK_COUNTS = {"track-a": 7, "track-b": 13, "track-c": 18, "track-d": 29}
EXPECTED_TYPE_COUNTS = {
    "contract": 4,
    "schema": 4,
    "fixture": 50,
    "cross-control-matrix": 1,
    "evaluator": 4,
    "test": 4,
}

_BASE_UNITTEST = ["python", "-X", "faulthandler", "-m", "unittest"]


def _unittest_command(*selectors: str) -> list[str]:
    return [*_BASE_UNITTEST, *selectors, "-v"]


EXPECTED_VERIFICATION_COMMANDS: dict[str, dict[str, Any]] = {
    "run_m15_e1_targeted_tests": {
        "argv": _unittest_command("tests.test_m15_operational_readiness_evaluator"),
        "test_scope": "M15 Track E1 targeted tests",
    },
    "run_m15_track_a_tests": {
        "argv": _unittest_command("tests.test_m15_learning_proof_evaluator"),
        "test_scope": "M15 Track A tests",
    },
    "run_m15_track_b_tests": {
        "argv": _unittest_command("tests.test_m15_capability_memory_pack_evaluator"),
        "test_scope": "M15 Track B tests",
    },
    "run_m15_track_c_tests": {
        "argv": _unittest_command("tests.test_m15_lineage_rollback_portability_evaluator"),
        "test_scope": "M15 Track C tests",
    },
    "run_m15_track_d_tests": {
        "argv": _unittest_command("tests.test_m15_cross_control_regression_evaluator"),
        "test_scope": "M15 Track D tests",
    },
    "run_m14_public_output_tests": {
        "argv": _unittest_command("tests.test_public_issue_exfiltration_gate_evaluator"),
        "test_scope": "M14 public-output tests",
    },
    "run_m14_provenance_tests": {
        "argv": _unittest_command("tests.test_ai_authored_pr_provenance_evaluator"),
        "test_scope": "M14 provenance tests",
    },
    "run_m14_skill_admission_tests": {
        "argv": _unittest_command("tests.test_skill_admission_evaluator"),
        "test_scope": "M14 skill-admission tests",
    },
    "run_external_evidence_admission_tests": {
        "argv": _unittest_command("tests.test_external_evidence_admission_evaluator"),
        "test_scope": "external-evidence-admission tests",
    },
    "run_m14_cross_control_authority_tests": {
        "argv": _unittest_command("tests.test_m14_cross_control_authority_boundary_evaluator"),
        "test_scope": "M14 cross-control authority tests",
    },
    "run_decision_proof_ownership_tests": {
        "argv": _unittest_command(
            "tests.test_m15_learning_proof_evaluator.M15LearningProofEvaluatorTests.test_22_decision_proof_cannot_automatically_become_memory",
            "tests.test_m15_learning_proof_evaluator.M15LearningProofEvaluatorTests.test_23_decision_proof_reference_is_linkage_only_not_memory_authority",
            "tests.test_m15_capability_memory_pack_evaluator.M15CapabilityMemoryPackEvaluatorTests.test_38_learning_proof_linkage_cannot_be_used_as_authority",
            "tests.test_m15_capability_memory_pack_evaluator.M15CapabilityMemoryPackEvaluatorTests.test_39_decision_proof_linkage_cannot_grant_execution_authority",
            "tests.test_m15_lineage_rollback_portability_evaluator.M15TrackCCrossTrackLinkageTests",
            "tests.test_m15_cross_control_regression_evaluator.DecisionProofOwnershipTests"
        ),
        "test_scope": "Decision Proof ownership tests",
    },
    "run_release_state_and_m15_status_tests": {
        "argv": _unittest_command(
            "tests.test_m15_lineage_rollback_portability_evaluator.M15TrackCReleaseStateTests",
            "tests.test_m15_cross_control_regression_evaluator.TrackDContractTests.test_matrix_preserves_release_state",
            "tests.test_m15_cross_control_regression_evaluator.ReleaseM15StatusTests"
        ),
        "test_scope": "release-state and M15-status tests",
    },
    "run_full_maintained_repository_suite": {
        "argv": [
            *_BASE_UNITTEST,
            "discover",
            "-s",
            "tests",
            "-v",
        ],
        "test_scope": "full maintained repository suite",
    },
}

_MANIFEST_FIELDS = frozenset(
    {
        "schema_version",
        "document_type",
        "record_id",
        "issue",
        "track",
        "maintained_repository",
        "maintained_branch",
        "maintained_main_commit_sha",
        "parent_tracker",
        "source_track_bindings",
        "artifact_integrity_inventory",
        "verification_command_manifest",
        "known_repository_local_completion_blockers",
        "governance_boundary",
        "allowed_outcomes",
        "declared_outcome",
        "non_authoritative_boundary_statement",
    }
)
_TRACK_BINDING_FIELDS = frozenset(
    {
        "track_id",
        "source_issue",
        "implementation_pr",
        "head_sha",
        "merge_sha",
        "schema_version",
        "artifact_count",
        "implementation_state",
    }
)
_INVENTORY_FIELDS = frozenset(
    {
        "digest_algorithm",
        "digest_mode",
        "canonicalization",
        "historical_digest_evidence_policy",
        "artifact_count",
        "track_artifact_counts",
        "artifact_type_counts",
        "artifacts",
    }
)
_ARTIFACT_FIELDS = frozenset(
    {
        "track_id",
        "source_issue",
        "implementation_pr",
        "relative_path",
        "artifact_type",
        "required",
        "digest_algorithm",
        "digest_mode",
        "maintained_canonical_sha256",
        "test_module",
        "executable_by_evaluator",
    }
)
_VERIFICATION_FIELDS = frozenset(
    {
        "command_count",
        "environment",
        "execution_policy",
        "executed_by_evaluator",
        "execution_results_recorded",
        "verification_results_are_completion_approval",
        "commands",
    }
)
_COMMAND_FIELDS = frozenset(
    {
        "command_id",
        "argv",
        "test_scope",
        "required",
        "expected_exit_code",
        "executed_by_evaluator",
    }
)
_GOVERNANCE_FIELDS = frozenset(
    {
        "tracker_231_state",
        "m15_state",
        "v0_14_0_state",
        "completion_approved",
        "tracker_closure_authorized",
        "readme_completion_authorized",
        "readme_release_authorized",
        "tag_created",
        "tag_creation_authorized",
        "release_authorized",
        "github_release_created",
        "github_release_publication_authorized",
        "authority_transferred",
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
        "evidence_state",
        "notes",
    }
)
_SCENARIO_STATE_FIELDS = frozenset(
    {
        "manifest_shape_valid",
        "maintained_main_binding_valid",
        "source_track_bindings_valid",
        "artifact_inventory_complete",
        "artifact_integrity_valid",
        "internal_consistency_valid",
        "cross_control_matrix_bound",
        "test_coverage_complete",
        "verification_command_manifest_complete",
        "verification_execution_claimed",
        "authority_boundary_valid",
        "completion_approval_claimed",
        "tracker_closure_claimed",
        "m15_completion_claimed",
        "readme_authorization_claimed",
        "tag_authorization_or_creation_claimed",
        "release_authorization_or_publication_claimed",
        "known_repository_local_completion_blockers",
    }
)


def _mapping_has_exact_fields(value: Any, fields: frozenset[str]) -> bool:
    return isinstance(value, Mapping) and frozenset(value.keys()) == fields


def _is_bool(value: Any) -> bool:
    return type(value) is bool


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(_DIGEST_RE.fullmatch(value))


def _result(
    blocking_findings: set[str],
    readiness_findings: set[str],
    *,
    evaluated_artifact_count: int = 0,
    evaluated_verification_command_count: int = 0,
) -> dict[str, Any]:
    blocking = sorted(blocking_findings)
    readiness = sorted(readiness_findings)
    outcome = (
        BLOCKED
        if blocking
        else NOT_READY
        if readiness
        else READY_FOR_COMPLETION_REVIEW
    )
    findings = sorted(set(blocking) | set(readiness))
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "outcome": outcome,
        "ready_for_completion_review": outcome == READY_FOR_COMPLETION_REVIEW,
        "findings": findings,
        "blocking_findings": blocking,
        "readiness_findings": readiness,
        "evaluated_artifact_count": evaluated_artifact_count,
        "evaluated_verification_command_count": evaluated_verification_command_count,
        "non_authoritative_boundary_statement": NON_AUTHORITATIVE_BOUNDARY_STATEMENT,
    }


def _validate_track_bindings(value: Any, blocking: set[str]) -> None:
    if not isinstance(value, list) or len(value) != len(_TRACK_METADATA):
        blocking.add("source_track_bindings_shape_invalid")
        return
    observed_tracks: set[str] = set()
    for index, binding in enumerate(value):
        if not _mapping_has_exact_fields(binding, _TRACK_BINDING_FIELDS):
            blocking.add(f"source_track_binding_shape_invalid:{index}")
            continue
        track_id = binding.get("track_id")
        if track_id not in _TRACK_METADATA or track_id in observed_tracks:
            blocking.add(f"source_track_binding_identity_invalid:{index}")
            continue
        observed_tracks.add(track_id)
        expected = _TRACK_METADATA[track_id]
        expected_values = {
            "track_id": track_id,
            "source_issue": expected["source_issue"],
            "implementation_pr": expected["implementation_pr"],
            "head_sha": expected["head_sha"],
            "merge_sha": expected["merge_sha"],
            "schema_version": expected["schema_version"],
            "artifact_count": EXPECTED_TRACK_COUNTS[track_id],
            "implementation_state": "merged-into-maintained-main",
        }
        if dict(binding) != expected_values:
            blocking.add(f"source_track_binding_mismatch:{track_id}")
    for track_id in sorted(set(_TRACK_METADATA) - observed_tracks):
        blocking.add(f"source_track_binding_missing:{track_id}")


def _artifact_read_finding(path: str, error: BaseException) -> str:
    if isinstance(error, FileNotFoundError):
        return f"artifact_missing:{path}"
    if isinstance(error, RepositoryArtifactPathError):
        return f"artifact_path_unsafe:{path}"
    if isinstance(error, RepositoryArtifactFileTypeError):
        return f"artifact_not_regular:{path}"
    if isinstance(error, RepositoryArtifactTextError):
        return f"artifact_lone_carriage_return:{path}"
    if isinstance(error, UnicodeDecodeError):
        return f"artifact_malformed_utf8:{path}"
    return f"artifact_unreadable:{path}"


def _validate_inventory(
    value: Any,
    repository_root: Path,
    blocking: set[str],
    readiness: set[str],
) -> int:
    if not _mapping_has_exact_fields(value, _INVENTORY_FIELDS):
        blocking.add("artifact_inventory_shape_invalid")
        return 0
    if value.get("digest_algorithm") != "sha256":
        blocking.add("artifact_inventory_digest_algorithm_invalid")
    if value.get("digest_mode") != "canonical-text":
        blocking.add("artifact_inventory_digest_mode_invalid")
    if value.get("canonicalization") != "strict-utf8-crlf-to-lf-only":
        blocking.add("artifact_inventory_canonicalization_invalid")
    if value.get("historical_digest_evidence_policy") != "preserved-separate-and-unmodified":
        blocking.add("historical_digest_evidence_policy_invalid")
    if value.get("artifact_count") != len(REQUIRED_ARTIFACTS):
        blocking.add("artifact_inventory_count_invalid")
    if value.get("track_artifact_counts") != EXPECTED_TRACK_COUNTS:
        blocking.add("artifact_inventory_track_counts_invalid")
    if value.get("artifact_type_counts") != EXPECTED_TYPE_COUNTS:
        blocking.add("artifact_inventory_type_counts_invalid")

    artifacts = value.get("artifacts")
    if not isinstance(artifacts, list):
        blocking.add("artifact_inventory_entries_invalid")
        return 0

    observed: dict[str, Mapping[str, Any]] = {}
    duplicates: set[str] = set()
    for index, entry in enumerate(artifacts):
        if not _mapping_has_exact_fields(entry, _ARTIFACT_FIELDS):
            blocking.add(f"artifact_entry_shape_invalid:{index}")
            continue
        relative_path = entry.get("relative_path")
        if not isinstance(relative_path, str) or relative_path not in REQUIRED_ARTIFACTS:
            blocking.add(f"artifact_entry_identity_invalid:{index}")
            continue
        if relative_path in observed:
            duplicates.add(relative_path)
            continue
        observed[relative_path] = entry

    for relative_path in sorted(duplicates):
        blocking.add(f"duplicate_artifact:{relative_path}")
    for relative_path in sorted(set(REQUIRED_ARTIFACTS) - set(observed)):
        blocking.add(f"artifact_entry_missing:{relative_path}")
    if len(artifacts) != len(REQUIRED_ARTIFACTS):
        blocking.add("artifact_inventory_coverage_mismatch")

    for relative_path in sorted(observed):
        entry = observed[relative_path]
        expected = REQUIRED_ARTIFACTS[relative_path]
        for field in (
            "track_id",
            "source_issue",
            "implementation_pr",
            "artifact_type",
        ):
            if entry.get(field) != expected[field]:
                blocking.add(f"artifact_{field}_binding_mismatch:{relative_path}")
        if entry.get("required") is not True:
            blocking.add(f"artifact_required_binding_invalid:{relative_path}")
        if entry.get("digest_algorithm") != "sha256":
            blocking.add(f"artifact_digest_algorithm_invalid:{relative_path}")
        if entry.get("digest_mode") != "canonical-text":
            blocking.add(f"artifact_digest_mode_invalid:{relative_path}")
        if entry.get("executable_by_evaluator") is not False:
            blocking.add(f"artifact_execution_boundary_invalid:{relative_path}")
        if entry.get("test_module") != expected["test_module"]:
            readiness.add(f"test_coverage_incomplete:{expected['track_id']}")
        declared_digest = entry.get("maintained_canonical_sha256")
        if not _is_sha256(declared_digest):
            blocking.add(f"artifact_digest_shape_invalid:{relative_path}")
            continue
        expected_digest = EXPECTED_MAINTAINED_ARTIFACT_DIGESTS[relative_path]
        if declared_digest != expected_digest:
            blocking.add(f"artifact_declared_digest_mismatch:{relative_path}")
        try:
            observed_digest = sha256_repository_file(
                repository_root,
                relative_path,
                mode="text",
            )
        except (
            FileNotFoundError,
            RepositoryArtifactPathError,
            RepositoryArtifactFileTypeError,
            RepositoryArtifactTextError,
            UnicodeDecodeError,
            OSError,
        ) as error:
            blocking.add(_artifact_read_finding(relative_path, error))
            continue
        if observed_digest != expected_digest:
            blocking.add(f"artifact_maintained_digest_mismatch:{relative_path}")

    matrix_path = _TRACK_METADATA["track-d"]["matrix"]
    if matrix_path not in observed:
        blocking.add("track_d_cross_control_matrix_not_bound")
    return len(observed)


def _validate_verification_manifest(
    value: Any,
    blocking: set[str],
    readiness: set[str],
) -> int:
    if not _mapping_has_exact_fields(value, _VERIFICATION_FIELDS):
        blocking.add("verification_command_manifest_shape_invalid")
        return 0
    if value.get("command_count") != len(EXPECTED_VERIFICATION_COMMANDS):
        readiness.add("verification_command_count_incomplete")
    if value.get("environment") != {"PYTHONDONTWRITEBYTECODE": "1"}:
        blocking.add("verification_environment_invalid")
    if value.get("execution_policy") != "declarative-only-not-executed-by-evaluator":
        blocking.add("verification_execution_policy_invalid")
    if value.get("executed_by_evaluator") is not False:
        blocking.add("verification_execution_claimed")
    if value.get("execution_results_recorded") is not False:
        blocking.add("verification_result_recording_claim_invalid")
    if value.get("verification_results_are_completion_approval") is not False:
        blocking.add("verification_promoted_to_completion_approval")

    commands = value.get("commands")
    if not isinstance(commands, list):
        blocking.add("verification_commands_invalid")
        return 0
    observed: dict[str, Mapping[str, Any]] = {}
    for index, command in enumerate(commands):
        if not _mapping_has_exact_fields(command, _COMMAND_FIELDS):
            blocking.add(f"verification_command_shape_invalid:{index}")
            continue
        command_id = command.get("command_id")
        if not isinstance(command_id, str) or command_id not in EXPECTED_VERIFICATION_COMMANDS:
            blocking.add(f"verification_command_identity_invalid:{index}")
            continue
        if command_id in observed:
            blocking.add(f"verification_command_duplicate:{command_id}")
            continue
        observed[command_id] = command

    for command_id in sorted(set(EXPECTED_VERIFICATION_COMMANDS) - set(observed)):
        readiness.add(f"verification_command_missing:{command_id}")
    if len(commands) != len(EXPECTED_VERIFICATION_COMMANDS):
        readiness.add("verification_command_coverage_incomplete")

    for command_id in sorted(observed):
        command = observed[command_id]
        expected = EXPECTED_VERIFICATION_COMMANDS[command_id]
        if command.get("argv") != expected["argv"]:
            readiness.add(f"verification_command_invalid:{command_id}")
        if command.get("test_scope") != expected["test_scope"]:
            readiness.add(f"verification_command_scope_invalid:{command_id}")
        if command.get("required") is not True:
            readiness.add(f"verification_command_not_required:{command_id}")
        if command.get("expected_exit_code") != 0:
            readiness.add(f"verification_expected_exit_code_invalid:{command_id}")
        if command.get("executed_by_evaluator") is not False:
            blocking.add(f"verification_execution_claimed:{command_id}")
    return len(observed)


def _validate_governance(value: Any, blocking: set[str]) -> None:
    if not _mapping_has_exact_fields(value, _GOVERNANCE_FIELDS):
        blocking.add("governance_boundary_shape_invalid")
        return
    expected_states = {
        "tracker_231_state": "open",
        "m15_state": "active-and-incomplete",
        "v0_14_0_state": "unpublished",
    }
    for field, expected in expected_states.items():
        if value.get(field) != expected:
            blocking.add(f"release_boundary_violation:{field}")
    for field in sorted(_GOVERNANCE_FIELDS - set(expected_states)):
        if value.get(field) is not False:
            blocking.add(f"authority_boundary_violation:{field}")


def evaluate_operational_readiness(
    manifest: Mapping[str, Any],
    *,
    repository_root: str | Path = REPOSITORY_ROOT,
) -> dict[str, Any]:
    """Evaluate one maintained E1 manifest without executing its contents."""

    blocking: set[str] = set()
    readiness: set[str] = set()
    if not _mapping_has_exact_fields(manifest, _MANIFEST_FIELDS):
        blocking.add("manifest_shape_invalid")
        return _result(blocking, readiness)

    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        blocking.add("schema_version_mismatch")
    if manifest.get("document_type") != "maintained-operational-readiness-manifest":
        blocking.add("document_type_mismatch")
    if manifest.get("record_id") != "urn:aaos:m15:operational-readiness:e1:maintained-main":
        blocking.add("record_id_mismatch")
    if manifest.get("issue") != "#242" or manifest.get("track") != "E1":
        blocking.add("e1_scope_binding_mismatch")
    if manifest.get("maintained_repository") != "aa-os/aaos-public":
        blocking.add("maintained_repository_binding_mismatch")
    if manifest.get("maintained_branch") != "main":
        blocking.add("maintained_branch_binding_mismatch")
    if manifest.get("maintained_main_commit_sha") != MAINTAINED_MAIN_SHA:
        blocking.add("maintained_main_sha_mismatch")
    if manifest.get("parent_tracker") != "#231":
        blocking.add("parent_tracker_binding_mismatch")
    if manifest.get("allowed_outcomes") != list(OUTCOMES):
        blocking.add("allowed_outcomes_invalid")
    if manifest.get("declared_outcome") not in OUTCOMES:
        blocking.add("declared_outcome_invalid")
    if manifest.get("non_authoritative_boundary_statement") != NON_AUTHORITATIVE_BOUNDARY_STATEMENT:
        blocking.add("non_authoritative_boundary_statement_invalid")

    blockers = manifest.get("known_repository_local_completion_blockers")
    if not isinstance(blockers, list):
        blocking.add("completion_blocker_list_invalid")
    elif blockers:
        for index, blocker in enumerate(blockers):
            if isinstance(blocker, str) and blocker:
                blocking.add(f"unresolved_completion_blocker:{index}")
            else:
                blocking.add(f"completion_blocker_invalid:{index}")

    _validate_track_bindings(manifest.get("source_track_bindings"), blocking)
    _validate_governance(manifest.get("governance_boundary"), blocking)

    root = Path(repository_root)
    if not root.is_absolute():
        blocking.add("repository_root_not_absolute")
        return _result(blocking, readiness)
    try:
        root = root.resolve(strict=True)
    except OSError:
        blocking.add("repository_root_unavailable")
        return _result(blocking, readiness)
    if not root.is_dir():
        blocking.add("repository_root_not_directory")
        return _result(blocking, readiness)

    artifact_count = _validate_inventory(
        manifest.get("artifact_integrity_inventory"),
        root,
        blocking,
        readiness,
    )
    command_count = _validate_verification_manifest(
        manifest.get("verification_command_manifest"),
        blocking,
        readiness,
    )
    result = _result(
        blocking,
        readiness,
        evaluated_artifact_count=artifact_count,
        evaluated_verification_command_count=command_count,
    )
    if (
        result["outcome"] == READY_FOR_COMPLETION_REVIEW
        and manifest.get("declared_outcome") != READY_FOR_COMPLETION_REVIEW
    ):
        readiness.add("declared_outcome_not_ready_for_review")
        result = _result(
            blocking,
            readiness,
            evaluated_artifact_count=artifact_count,
            evaluated_verification_command_count=command_count,
        )
    return result


def evaluate_synthetic_scenario(document: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate a complete inert synthetic E1 scenario record."""

    blocking: set[str] = set()
    readiness: set[str] = set()
    if not _mapping_has_exact_fields(document, _SCENARIO_FIELDS):
        blocking.add("scenario_shape_invalid")
        return _result(blocking, readiness)
    if document.get("schema_version") != SCENARIO_SCHEMA_VERSION:
        blocking.add("schema_version_mismatch")
    if document.get("document_type") != "synthetic-scenario":
        blocking.add("scenario_document_type_invalid")
    if document.get("synthetic") is not True:
        blocking.add("scenario_synthetic_boundary_invalid")
    if document.get("expected_outcome") not in OUTCOMES:
        blocking.add("scenario_expected_outcome_invalid")
    scenario_id = document.get("scenario_id")
    if not isinstance(scenario_id, str) or scenario_id not in EXPECTED_SCENARIO_TITLES:
        blocking.add("scenario_id_invalid")
    if not isinstance(document.get("title"), str) or document.get("title") != EXPECTED_SCENARIO_TITLES.get(scenario_id):
        blocking.add("scenario_title_invalid")
    if not isinstance(document.get("notes"), str) or not document.get("notes"):
        blocking.add("scenario_notes_invalid")
    elif document.get("notes") != SYNTHETIC_SCENARIO_BOUNDARY_STATEMENT:
        blocking.add("scenario_notes_boundary_invalid")

    state = document.get("evidence_state")
    if not _mapping_has_exact_fields(state, _SCENARIO_STATE_FIELDS):
        blocking.add("scenario_evidence_state_shape_invalid")
        return _result(blocking, readiness)
    boolean_fields = _SCENARIO_STATE_FIELDS - {"known_repository_local_completion_blockers"}
    for field in sorted(boolean_fields):
        if not _is_bool(state.get(field)):
            blocking.add(f"scenario_boolean_invalid:{field}")

    for field in (
        "manifest_shape_valid",
        "maintained_main_binding_valid",
        "source_track_bindings_valid",
        "artifact_inventory_complete",
        "artifact_integrity_valid",
        "internal_consistency_valid",
        "cross_control_matrix_bound",
        "authority_boundary_valid",
    ):
        if state.get(field) is False:
            blocking.add(f"scenario_blocking_check_failed:{field}")
    for field in (
        "test_coverage_complete",
        "verification_command_manifest_complete",
    ):
        if state.get(field) is False:
            readiness.add(f"scenario_readiness_check_failed:{field}")
    if state.get("verification_execution_claimed") is True:
        blocking.add("verification_execution_claimed")
    for field in (
        "completion_approval_claimed",
        "tracker_closure_claimed",
        "m15_completion_claimed",
        "readme_authorization_claimed",
        "tag_authorization_or_creation_claimed",
        "release_authorization_or_publication_claimed",
    ):
        if state.get(field) is True:
            blocking.add(f"authority_boundary_violation:{field}")

    blockers = state.get("known_repository_local_completion_blockers")
    if not isinstance(blockers, list):
        blocking.add("completion_blocker_list_invalid")
    elif blockers:
        for index, blocker in enumerate(blockers):
            if isinstance(blocker, str) and blocker:
                blocking.add(f"unresolved_completion_blocker:{index}")
            else:
                blocking.add(f"completion_blocker_invalid:{index}")
    return _result(blocking, readiness)


def evaluate_repository_operational_readiness(
    repository_root: str | Path = REPOSITORY_ROOT,
) -> dict[str, Any]:
    """Load and evaluate the maintained manifest from an explicit repository root."""

    root = Path(repository_root)
    if not root.is_absolute():
        return _result({"repository_root_not_absolute"}, set())
    try:
        manifest_text = (root / Path(MANIFEST_PATH)).read_text(encoding="utf-8")
        manifest = json.loads(manifest_text)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return _result({"manifest_unreadable"}, set())
    if not isinstance(manifest, Mapping):
        return _result({"manifest_shape_invalid"}, set())
    return evaluate_operational_readiness(manifest, repository_root=root)


__all__ = [
    "BLOCKED",
    "EXPECTED_TRACK_COUNTS",
    "EXPECTED_TYPE_COUNTS",
    "EXPECTED_MAINTAINED_ARTIFACT_DIGESTS",
    "EXPECTED_SCENARIO_TITLES",
    "EXPECTED_VERIFICATION_COMMANDS",
    "MAINTAINED_MAIN_SHA",
    "MANIFEST_PATH",
    "MANIFEST_SCHEMA_VERSION",
    "NON_AUTHORITATIVE_BOUNDARY_STATEMENT",
    "NOT_READY",
    "OUTCOMES",
    "READY_FOR_COMPLETION_REVIEW",
    "REPOSITORY_ROOT",
    "REQUIRED_ARTIFACTS",
    "RESULT_SCHEMA_VERSION",
    "SCENARIO_SCHEMA_VERSION",
    "SYNTHETIC_SCENARIO_BOUNDARY_STATEMENT",
    "evaluate_operational_readiness",
    "evaluate_repository_operational_readiness",
    "evaluate_synthetic_scenario",
]
