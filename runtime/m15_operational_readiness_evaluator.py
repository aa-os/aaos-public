"""Deterministic, caller-data-only evaluator for M15 Track E1 readiness.

The evaluator accepts inert manifest, repository-observation, and external
verification-receipt mappings.  It does not read files, inspect Git or GitHub,
invoke source controls, execute the verification command manifest, mutate
caller data, or grant completion or release authority.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any


MANIFEST_SCHEMA_VERSION = "m15-operational-readiness/v1"
SCENARIO_SCHEMA_VERSION = "m15-operational-readiness-scenario/v1"
RESULT_SCHEMA_VERSION = "m15-operational-readiness-result/v1"
OBSERVATION_SCHEMA_VERSION = "m15-operational-readiness-observation/v1"
VERIFICATION_RECEIPT_SCHEMA_VERSION = (
    "m15-operational-readiness-verification-receipt/v1"
)
SOURCE_BASELINE_SHA = "e4681dfbc9c7cc69372b0e44bc6d2f2da034d88f"
# Kept as a compatibility alias for the maintained Track A-D snapshot.
MAINTAINED_MAIN_SHA = SOURCE_BASELINE_SHA

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
VERIFICATION_RECEIPT_NON_AUTHORITATIVE_BOUNDARY_STATEMENT = (
    "The external verification receipt is inert, caller-supplied execution evidence only; "
    "it is not M15 completion approval, tracker #231 closure, README completion or release "
    "authorization, tag authorization, release authorization, or GitHub Release "
    "publication authorization."
)
SYNTHETIC_SCENARIO_BOUNDARY_STATEMENT = (
    "This standalone scenario is synthetic, inert, offline, and "
    "non-authoritative. " + NON_AUTHORITATIVE_BOUNDARY_STATEMENT
)

_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_RFC3339_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)

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
    "m15-e1-19": "E1 targeted verification reports a test failure",
    "m15-e1-20": "Verification reports a test error",
    "m15-e1-21": "Verification reports an unexpected skip",
    "m15-e1-22": "Required verification result is missing",
    "m15-e1-23": "Observed verification test count does not match the reviewed count",
    "m15-e1-24": "Verification result omits the maintained-main binding",
    "m15-e1-25": "Required material artifact remains unverified",
    "m15-e1-26": "Deferred material artifact has no reason",
    "m15-e1-27": "Track D external-control dependency binding has drifted",
    "m15-e1-28": "Candidate-head receipt binding mismatch",
    "m15-e1-29": "Source-baseline and candidate SHA conflation",
    "m15-e1-30": "Missing external execution receipt",
    "m15-e1-31": "Undeclared Python launcher substitution",
    "m15-e1-32": "Missing Python interpreter version",
    "m15-e1-33": "Missing verification transcript digest",
    "m15-e1-34": "Verification command/result binding mismatch",
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
    for track_id in _TRACK_METADATA:
        track_paths = sorted(
            path for path, metadata in result.items() if metadata["track_id"] == track_id
        )
        for index, path in enumerate(track_paths, start=1):
            result[path]["artifact_id"] = f"m15-e1-{track_id}-artifact-{index:02d}"
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

EXPECTED_VERIFICATION_RESULT_COUNTS = {
    "run_m15_e1_targeted_tests": 126,
    "run_m15_track_a_tests": 68,
    "run_m15_track_b_tests": 73,
    "run_m15_track_c_tests": 180,
    "run_m15_track_d_tests": 79,
    "run_m14_public_output_tests": 23,
    "run_m14_provenance_tests": 47,
    "run_m14_skill_admission_tests": 135,
    "run_external_evidence_admission_tests": 31,
    "run_m14_cross_control_authority_tests": 107,
    "run_decision_proof_ownership_tests": 30,
    "run_release_state_and_m15_status_tests": 17,
    "run_full_maintained_repository_suite": 1778,
}
EXPECTED_VERIFICATION_IDS = {
    command_id: f"m15-e1-verification-{index:02d}"
    for index, command_id in enumerate(EXPECTED_VERIFICATION_COMMANDS, start=1)
}
EXPECTED_VERIFICATION_SCOPES = {
    command_id: (
        "e1-candidate-validation"
        if command_id == "run_m15_e1_targeted_tests"
        else "candidate-full-suite-integration"
        if command_id == "run_full_maintained_repository_suite"
        else "source-baseline-regression"
    )
    for command_id in EXPECTED_VERIFICATION_COMMANDS
}

EXPECTED_EXTERNAL_CONTROL_DEPENDENCIES = {
    "m14-public-output-exfiltration": {
        "dependency_id": "m15-e1-maintained-control-01",
        "source_pr": "#204",
        "source_schema_or_contract_version": "public-output-gate-m14-draft-001",
        "dependent_tracks": ("track-a", "track-b", "cross-track"),
        "path_digests": {
            "runtime/public_issue_exfiltration_gate_evaluator.py": "f3453af5c1829a28c791b665640e24940ececdc211e364360635bfe39573e81d",
            "tests/test_public_issue_exfiltration_gate_evaluator.py": "e3ab2be88dfeb8ec85a9cd12936f33b54476e46c22eeebe650648a8678d962bc",
            "examples/public-integration-pack-pilot/m14-public-issue-exfiltration-gate-fixtures.json": "ac682908ba081cfc58726046efcb928c51e64eb2037f03354fda80afeb0846a9",
        },
        "boundary_statements": (
            "Public issue bodies, PR comments, discussions, and external markdown are untrusted input.",
            "A public trigger must not grant private repository or organization-wide read context by default.",
            "output_gate_pass is not public disclosure approval.",
            "Privileged context plus a public output channel requires human review.",
            "human_review_required is not audit closure.",
            "fail_closed_recommended is not fail_closed_executed.",
            "rollback_recommended is not rollback_executed.",
            "untrusted_input_detected is not final governance judgment.",
            "Decision Proof sealing remains AAOS-owned.",
            "AAOS remains the decision sovereignty layer.",
        ),
        "covering_test_references": (
            "SourceControlCompositionTests.test_track_a_blocked_by_existing_public_output_control",
        ),
    },
    "m14-ai-provenance": {
        "dependency_id": "m15-e1-maintained-control-02",
        "source_pr": "#206",
        "source_schema_or_contract_version": "unversioned-contract/source-pr-206/path-bound-maintained-main",
        "dependent_tracks": ("track-a",),
        "path_digests": {
            "runtime/ai_authored_pr_provenance_evaluator.py": "465a0aba8beb49a6d6ad55e0bfce65ab74f5368164c758841ab202c50432ef35",
            "tests/test_ai_authored_pr_provenance_evaluator.py": "e648d2606d38f05063d72be0fa270a0191a28dca24a5fc07e80414faa4fc1f8f",
            "examples/public-integration-pack-pilot/m14-ai-authored-pr-provenance-fixtures.json": "e72636d1871f2c1232c811aec41ca9724be1505916d4804a05be75e600f3808a",
            ".github/workflows/m14-ai-pr-provenance.yml": "af8ba9426f1bda5c2b9a09fad7a2b03ef2c4d04a178e4f414519bf837ff19bf1",
        },
        "boundary_statements": (
            "AI-authored detection is provenance evidence, not identity proof.",
            "pr-by-ai is not approval.",
            "human-review-required is not completed review.",
            "Reviewer routing is not review approval.",
            "Workflow success is not merge approval.",
            "This workflow is not a security scanner.",
            "This workflow is not a policy authority.",
            "This workflow is not a Decision Proof verification or sealing engine.",
            "Decision Proof sealing remains AAOS-owned.",
            "AAOS remains the decision sovereignty layer.",
        ),
        "covering_test_references": (
            "SourceControlCompositionTests.test_provenance_success_cannot_complete_human_review",
        ),
    },
    "m14-skill-admission": {
        "dependency_id": "m15-e1-maintained-control-03",
        "source_pr": "#208",
        "source_schema_or_contract_version": "aaos-skill-admission-policy-m14-synthetic-v1",
        "dependent_tracks": ("track-a", "track-b"),
        "path_digests": {
            "runtime/skill_admission_evaluator.py": "bb81697df1be79b96a6af373ce63314a01ac73392b3cdb97981abaddbe6a4400",
            "tests/test_skill_admission_evaluator.py": "45ba9f2f8369bf0c127993c480e5091a1a2ee8f7ca2a0be2f579b3de38011b83",
            "examples/public-integration-pack-pilot/m14-skill-admission-fixtures.json": "4fc229be3883a2681f8ebfc3f2eb828514cd3a2d6729c5841bab5a7efe609509",
        },
        "boundary_statements": (
            "External skill capability is not governance permission.",
            "Skill metadata is not verified behavior.",
            "Skill installation is not execution authorization.",
            "Artifact signature is not governance approval.",
            "Signature verification is not risk acceptance.",
            "Scan passed is not risk accepted.",
            "Benchmark passed is not deployment approval.",
            "Evaluation evidence is not final approval.",
            "candidate_allowed is not execution approval.",
            "needs_approval is not approval granted.",
            "admission_ready_for_review is not final admission approval.",
            "fail_closed_recommended is not fail_closed_executed.",
            "rollback_recommended is not rollback_executed.",
            "human_review_required is not completed review.",
            "evidence_complete is not Decision Proof sealing.",
            "replay_ready is not Decision Proof sealing.",
            "Registry classification is not final governance judgment.",
            "NVIDIA skills remain external capability artifacts.",
            "AAOS remains vendor-independent.",
            "Decision Proof sealing remains AAOS-owned.",
            "AAOS remains the decision sovereignty layer.",
        ),
        "covering_test_references": (
            "SourceControlCompositionTests.test_track_b_cannot_bypass_rejected_skill_admission",
        ),
    },
    "external-evidence-admission": {
        "dependency_id": "m15-e1-maintained-control-04",
        "source_pr": "#209",
        "source_schema_or_contract_version": "aaos-external-evidence-admission-v1",
        "dependent_tracks": ("track-b",),
        "path_digests": {
            "runtime/external_evidence_admission_evaluator.py": "3271905c87a0b6914bbb48d7b77b1a6bb51741a2acdd36fbfeb973dc287c9884",
            "tests/test_external_evidence_admission_evaluator.py": "3d077cc6699217f2076fa98e098761af145ffd60210be2e0c40a66b8cfe98aa7",
            "schemas/external-evidence-admission.schema.json": "adc866d069143c688657d8938f18e76d9448d9223fa4ba2e3e857f62af462ebd",
            "examples/external-evidence-admission/twinkle-hub-fixtures.json": "3c02b06822ba5d11e1863c640ff8f34d474994d4e412e88aed39b17b7aeb32c1",
        },
        "boundary_statements": (
            "Only verified evidence may enter the governed decision path.",
            "Degraded and rejected evidence remain decision-path ineligible.",
            "Decision Proof sealing eligibility is not Decision Proof sealing.",
        ),
        "covering_test_references": (
            "SourceControlCompositionTests.test_external_evidence_states_cannot_bypass_gate",
        ),
    },
    "m14-cross-control-authority": {
        "dependency_id": "m15-e1-maintained-control-05",
        "source_pr": "#210",
        "source_schema_or_contract_version": "unversioned-contract/source-pr-210/path-bound-maintained-main",
        "dependent_tracks": ("track-a", "track-b", "track-c", "cross-track"),
        "path_digests": {
            "runtime/m14_cross_control_authority_boundary_evaluator.py": "51a413dc5303d64d49e958ffde970925ffc5aebead3435f8cf714e6112e1b48c",
            "tests/test_m14_cross_control_authority_boundary_evaluator.py": "5a4a5e764655382e2b19aa5a4e8a5a6a2b5082ade733e7125d88dfd2ba6cfc52",
            "examples/public-integration-pack-pilot/m14-cross-control-authority-boundary-regression-fixtures.json": "f44b6d3298922608096c10f248955fa4c25e8d4a3452d6d7c585f9237129809d",
        },
        "boundary_statements": (
            "Multiple non-authoritative outputs do not aggregate into governance authority.",
            "Evidence accumulation does not create authority by aggregation.",
            "Five passed gates are not final approval.",
            "Capability is not permission.",
            "Consent evidence is not approval.",
            "Provenance is not identity proof.",
            "Regulatory mapping is not legal approval.",
            "Taxonomy coverage is not compliance certification.",
            "Artifact signature is not governance approval.",
            "Scan passed is not risk accepted.",
            "Benchmark passed is not deployment approval.",
            "ready_for_review is not approval.",
            "Reviewer routing is not review approval.",
            "Workflow success is not merge approval.",
            "output_gate_pass is not public disclosure approval.",
            "fail_closed_recommended is not fail_closed_executed.",
            "rollback_recommended is not rollback_executed.",
            "human_review_required is not audit closure.",
            "evidence_complete is not Decision Proof sealing.",
            "replay_ready is not Decision Proof sealing.",
            "Source evaluators remain bounded evidence evaluators.",
            "Explicit negative governance evidence is not an affirmative authority claim.",
            "Decision Proof sealing remains AAOS-owned.",
            "AAOS remains the decision sovereignty layer.",
        ),
        "covering_test_references": (
            "SourceControlCompositionTests.test_tracks_a_b_c_cannot_aggregate_authority",
        ),
    },
}

ARTIFACT_LIFECYCLE_STATUSES = frozenset(
    {"present", "missing", "digest_mismatch", "unverified", "superseded", "deferred", "not_applicable"}
)
ARTIFACT_BOUNDARY_STATEMENT = (
    "Artifact lifecycle and integrity status is evidence only; it grants no "
    "completion, tracker-closure, README, tag, release, execution, or governance authority."
)
ARTIFACT_OBSERVATION_BOUNDARY_STATEMENT = (
    "Artifact observation is evidence only; it grants no completion, tracker-closure, "
    "README, tag, release, execution, or governance authority."
)
DEPENDENCY_BOUNDARY_STATEMENT = (
    "Maintained-control dependency binding is evidence only; it does not grant control "
    "admission, completion, release, execution, or governance authority."
)
DEPENDENCY_OBSERVATION_BOUNDARY_STATEMENT = (
    "Maintained-control dependency observation is evidence only; it does not grant control "
    "admission, completion, release, execution, or governance authority."
)
OBSERVATION_BOUNDARY_STATEMENT = (
    "Observation evidence records bounded repository state only; it is not completion "
    "approval, tracker #231 closure, README authorization, tag authorization, release "
    "authorization, execution authority, or governance authority."
)

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
        "source_baseline_commit_sha",
        "execution_subject_type",
        "execution_candidate_reference",
        "execution_candidate_head_sha",
        "parent_tracker",
        "source_track_bindings",
        "artifact_integrity_inventory",
        "verification_command_manifest",
        "verification_result_manifest",
        "maintained_control_dependency_inventory",
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
        "artifact_id",
        "track_id",
        "source_issue",
        "implementation_pr",
        "relative_path",
        "artifact_type",
        "status",
        "required",
        "digest_algorithm",
        "digest_mode",
        "maintained_canonical_sha256",
        "test_module",
        "executable_by_evaluator",
        "evidence_reference",
        "authority_boundary",
        "notes",
        "deferred_reason",
    }
)
_VERIFICATION_FIELDS = frozenset(
    {
        "command_count",
        "environment",
        "execution_policy",
        "execution_results_recorded",
        "commands_executed_by_evaluator",
        "results_supplied_as_external_verification_evidence",
        "external_execution_receipt_required",
        "verification_results_are_completion_approval",
        "commands",
    }
)
_COMMAND_FIELDS = frozenset(
    {
        "command_id",
        "argv",
        "test_scope",
        "verification_scope",
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
_VERIFICATION_RESULT_MANIFEST_FIELDS = frozenset(
    {
        "result_count",
        "results_supplied_as_external_verification_evidence",
        "result_records_are_execution_receipts",
        "external_execution_receipt_required",
        "executed_by_evaluator",
        "verification_results_are_completion_approval",
        "results",
    }
)
_VERIFICATION_RESULT_FIELDS = frozenset(
    {
        "verification_id",
        "command_id",
        "evidence_source",
        "source_baseline_commit_sha",
        "execution_subject_type",
        "execution_candidate_reference",
        "execution_candidate_head_sha",
        "verification_scope",
        "expected_test_count",
        "observed_test_count",
        "passes",
        "failures",
        "errors",
        "skips",
        "exit_code",
        "result",
        "evidence_reference",
        "external_execution_receipt_required",
        "executed_by_evaluator",
        "verification_results_are_completion_approval",
    }
)
_DEPENDENCY_PATH_FIELDS = frozenset(
    {
        "relative_path",
        "digest_algorithm",
        "digest_mode",
        "maintained_canonical_sha256",
    }
)
_DEPENDENCY_FIELDS = frozenset(
    {
        "dependency_id",
        "source_control_id",
        "source_pr",
        "source_schema_or_contract_version",
        "dependent_tracks",
        "maintained_integrity_reference",
        "path_digests",
        "boundary_statements",
        "covering_test_references",
        "status",
        "evidence_reference",
        "authority_boundary",
        "notes",
    }
)
_DEPENDENCY_INVENTORY_FIELDS = frozenset(
    {
        "dependency_count",
        "dependency_artifact_count",
        "included_in_material_artifact_count",
        "maintained_main_commit_sha",
        "dependencies",
    }
)
_OBSERVATION_FIELDS = frozenset(
    {
        "schema_version",
        "document_type",
        "record_id",
        "issue",
        "track",
        "maintained_repository",
        "maintained_branch",
        "maintained_main_commit_sha",
        "source_baseline_commit_sha",
        "artifact_observation_count",
        "dependency_observation_count",
        "artifact_observations",
        "dependency_observations",
        "generated_by_evaluator",
        "non_authoritative_boundary_statement",
    }
)
_ARTIFACT_OBSERVATION_FIELDS = frozenset(
    {
        "artifact_id",
        "relative_path",
        "status",
        "observed_canonical_sha256",
        "evidence_reference",
        "authority_boundary",
        "notes",
        "deferred_reason",
    }
)
_DEPENDENCY_OBSERVATION_FIELDS = frozenset(
    {
        "dependency_id",
        "source_control_id",
        "relative_path",
        "status",
        "observed_canonical_sha256",
        "evidence_reference",
        "authority_boundary",
        "notes",
    }
)
_VERIFICATION_RECEIPT_FIELDS = frozenset(
    {
        "schema_version",
        "document_type",
        "repository",
        "pull_request_number",
        "source_baseline_commit_sha",
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
_VERIFICATION_RECEIPT_COMMAND_FIELDS = frozenset(
    {
        "verification_id",
        "command_id",
        "verification_scope",
        "source_baseline_commit_sha",
        "execution_candidate_reference",
        "execution_candidate_head_sha",
        "declared_logical_argv",
        "actual_argv",
        "executable_binding",
        "observed_test_count",
        "passes",
        "failures",
        "errors",
        "skips",
        "exit_code",
        "result",
        "execution_timestamp",
        "output_transcript_sha256",
        "evidence_reference",
        "executed_by_evaluator",
        "verification_results_are_completion_approval",
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
        "verification_result_manifest_complete",
        "verification_result_main_binding_valid",
        "verification_result_counts_valid",
        "verification_failures",
        "verification_errors",
        "verification_skips",
        "verification_execution_claimed",
        "required_artifact_status",
        "artifact_deferred_reason",
        "maintained_control_dependencies_valid",
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
_SCENARIO_RECEIPT_STATE_FIELDS = frozenset(
    {
        "candidate_head_matches_receipt",
        "baseline_candidate_sha_distinct",
        "external_execution_receipt_present",
        "launcher_substitution_declared",
        "interpreter_identity_present",
        "transcript_digest_present",
        "command_result_binding_matches",
    }
)


def _mapping_has_exact_fields(value: Any, fields: frozenset[str]) -> bool:
    return isinstance(value, Mapping) and frozenset(value.keys()) == fields


def _is_bool(value: Any) -> bool:
    return type(value) is bool


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(_DIGEST_RE.fullmatch(value))


def _is_commit_sha(value: Any) -> bool:
    return isinstance(value, str) and bool(_COMMIT_SHA_RE.fullmatch(value))


def _is_rfc3339(value: Any) -> bool:
    return isinstance(value, str) and bool(_RFC3339_RE.fullmatch(value))


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _is_nonnegative_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _apply_artifact_lifecycle(
    status: Any,
    deferred_reason: Any,
    identity: str,
    finding_prefix: str,
    blocking: set[str],
    readiness: set[str],
) -> None:
    if status not in ARTIFACT_LIFECYCLE_STATUSES:
        blocking.add(f"{finding_prefix}_status_invalid:{identity}")
        return
    if deferred_reason is not None and not _is_nonempty_string(deferred_reason):
        blocking.add(f"{finding_prefix}_deferred_reason_invalid:{identity}")
    if status == "present":
        if deferred_reason is not None:
            blocking.add(f"{finding_prefix}_present_has_deferred_reason:{identity}")
    elif status in {"missing", "digest_mismatch", "not_applicable"}:
        blocking.add(f"{finding_prefix}_status_blocking:{identity}:{status}")
    elif status == "deferred":
        if not _is_nonempty_string(deferred_reason):
            blocking.add(f"{finding_prefix}_deferred_reason_missing:{identity}")
        else:
            readiness.add(f"{finding_prefix}_status_not_ready:{identity}:deferred")
    else:
        readiness.add(f"{finding_prefix}_status_not_ready:{identity}:{status}")


def _result(
    blocking_findings: set[str],
    readiness_findings: set[str],
    *,
    evaluated_artifact_count: int = 0,
    evaluated_artifact_observation_count: int = 0,
    evaluated_source_track_binding_count: int = 0,
    evaluated_maintained_control_dependency_count: int = 0,
    evaluated_dependency_observation_count: int = 0,
    evaluated_verification_command_count: int = 0,
    evaluated_verification_result_count: int = 0,
    evaluated_verification_receipt_command_count: int = 0,
    external_verification_receipt_validated: bool = False,
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
        "evaluated_artifact_observation_count": evaluated_artifact_observation_count,
        "evaluated_source_track_binding_count": evaluated_source_track_binding_count,
        "evaluated_maintained_control_dependency_count": evaluated_maintained_control_dependency_count,
        "evaluated_dependency_observation_count": evaluated_dependency_observation_count,
        "evaluated_verification_command_count": evaluated_verification_command_count,
        "evaluated_verification_result_count": evaluated_verification_result_count,
        "evaluated_verification_receipt_command_count": evaluated_verification_receipt_command_count,
        "external_verification_receipt_validated": external_verification_receipt_validated,
        "caller_data_only": True,
        "file_io_performed": False,
        "external_controls_invoked": False,
        "verification_commands_executed": False,
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


def _validate_inventory(
    value: Any,
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
            "artifact_id",
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
        if not _is_nonempty_string(entry.get("evidence_reference")):
            blocking.add(f"artifact_evidence_reference_invalid:{relative_path}")
        if entry.get("authority_boundary") != ARTIFACT_BOUNDARY_STATEMENT:
            blocking.add(f"artifact_authority_boundary_invalid:{relative_path}")
        if not _is_nonempty_string(entry.get("notes")):
            blocking.add(f"artifact_notes_invalid:{relative_path}")
        _apply_artifact_lifecycle(
            entry.get("status"),
            entry.get("deferred_reason"),
            relative_path,
            "artifact_declared",
            blocking,
            readiness,
        )
        declared_digest = entry.get("maintained_canonical_sha256")
        if not _is_sha256(declared_digest):
            blocking.add(f"artifact_digest_shape_invalid:{relative_path}")
            continue
        expected_digest = EXPECTED_MAINTAINED_ARTIFACT_DIGESTS[relative_path]
        if declared_digest != expected_digest:
            blocking.add(f"artifact_declared_digest_mismatch:{relative_path}")

    matrix_path = _TRACK_METADATA["track-d"]["matrix"]
    if matrix_path not in observed:
        blocking.add("track_d_cross_control_matrix_not_bound")
    return len(observed)


def _validate_repository_observation(
    value: Any,
    blocking: set[str],
) -> Mapping[str, Any] | None:
    if not _mapping_has_exact_fields(value, _OBSERVATION_FIELDS):
        blocking.add("repository_observation_shape_invalid")
        return None
    if value.get("schema_version") != OBSERVATION_SCHEMA_VERSION:
        blocking.add("repository_observation_schema_version_mismatch")
    if value.get("document_type") != "maintained-operational-readiness-observation":
        blocking.add("repository_observation_document_type_invalid")
    if value.get("record_id") != "urn:aaos:m15:operational-readiness:e1:maintained-main:observation":
        blocking.add("repository_observation_record_id_invalid")
    if value.get("issue") != "#242" or value.get("track") != "E1":
        blocking.add("repository_observation_scope_binding_mismatch")
    if value.get("maintained_repository") != "aa-os/aaos-public":
        blocking.add("repository_observation_repository_mismatch")
    if value.get("maintained_branch") != "main":
        blocking.add("repository_observation_branch_mismatch")
    if value.get("maintained_main_commit_sha") != MAINTAINED_MAIN_SHA:
        blocking.add("repository_observation_main_sha_mismatch")
    if value.get("source_baseline_commit_sha") != SOURCE_BASELINE_SHA:
        blocking.add("repository_observation_source_baseline_sha_mismatch")
    if value.get("artifact_observation_count") != len(REQUIRED_ARTIFACTS):
        blocking.add("artifact_observation_count_invalid")
    dependency_path_count = sum(
        len(metadata["path_digests"])
        for metadata in EXPECTED_EXTERNAL_CONTROL_DEPENDENCIES.values()
    )
    if value.get("dependency_observation_count") != dependency_path_count:
        blocking.add("dependency_observation_count_invalid")
    if value.get("generated_by_evaluator") is not False:
        blocking.add("repository_observation_generation_claim_invalid")
    if value.get("non_authoritative_boundary_statement") != OBSERVATION_BOUNDARY_STATEMENT:
        blocking.add("repository_observation_boundary_invalid")
    return value


def _validate_artifact_observations(
    value: Any,
    blocking: set[str],
    readiness: set[str],
) -> int:
    if not isinstance(value, list):
        blocking.add("artifact_observations_invalid")
        return 0
    observations: dict[str, Mapping[str, Any]] = {}
    for index, observation in enumerate(value):
        if not _mapping_has_exact_fields(observation, _ARTIFACT_OBSERVATION_FIELDS):
            blocking.add(f"artifact_observation_shape_invalid:{index}")
            continue
        relative_path = observation.get("relative_path")
        if not isinstance(relative_path, str) or relative_path not in REQUIRED_ARTIFACTS:
            blocking.add(f"artifact_observation_identity_invalid:{index}")
            continue
        if relative_path in observations:
            blocking.add(f"artifact_observation_duplicate:{relative_path}")
            continue
        observations[relative_path] = observation

    for relative_path in sorted(set(REQUIRED_ARTIFACTS) - set(observations)):
        blocking.add(f"artifact_observation_missing:{relative_path}")
    if len(value) != len(REQUIRED_ARTIFACTS):
        blocking.add("artifact_observation_coverage_incomplete")

    for relative_path in sorted(observations):
        observation = observations[relative_path]
        expected = REQUIRED_ARTIFACTS[relative_path]
        if observation.get("artifact_id") != expected["artifact_id"]:
            blocking.add(f"artifact_observation_id_mismatch:{relative_path}")
        if not _is_nonempty_string(observation.get("evidence_reference")):
            blocking.add(f"artifact_observation_evidence_reference_invalid:{relative_path}")
        if observation.get("authority_boundary") != ARTIFACT_OBSERVATION_BOUNDARY_STATEMENT:
            blocking.add(f"artifact_observation_authority_boundary_invalid:{relative_path}")
        if not _is_nonempty_string(observation.get("notes")):
            blocking.add(f"artifact_observation_notes_invalid:{relative_path}")
        status = observation.get("status")
        _apply_artifact_lifecycle(
            status,
            observation.get("deferred_reason"),
            relative_path,
            "artifact_observation",
            blocking,
            readiness,
        )
        observed_digest = observation.get("observed_canonical_sha256")
        if status != "present":
            if observed_digest is not None and not _is_sha256(observed_digest):
                blocking.add(f"artifact_observed_digest_shape_invalid:{relative_path}")
            continue
        if not _is_sha256(observed_digest):
            blocking.add(f"artifact_observed_digest_shape_invalid:{relative_path}")
            continue
        expected_digest = EXPECTED_MAINTAINED_ARTIFACT_DIGESTS[relative_path]
        if observed_digest != expected_digest:
            blocking.add(f"artifact_observed_digest_mismatch:{relative_path}")
    return len(observations)


def _validate_maintained_control_dependency_inventory(
    value: Any,
    blocking: set[str],
) -> int:
    if not _mapping_has_exact_fields(value, _DEPENDENCY_INVENTORY_FIELDS):
        blocking.add("maintained_control_dependency_inventory_shape_invalid")
        return 0
    if value.get("dependency_count") != len(EXPECTED_EXTERNAL_CONTROL_DEPENDENCIES):
        blocking.add("maintained_control_dependency_count_invalid")
    expected_path_count = sum(
        len(metadata["path_digests"])
        for metadata in EXPECTED_EXTERNAL_CONTROL_DEPENDENCIES.values()
    )
    if value.get("dependency_artifact_count") != expected_path_count:
        blocking.add("maintained_control_dependency_artifact_count_invalid")
    if value.get("included_in_material_artifact_count") is not False:
        blocking.add("maintained_control_dependency_material_count_boundary_invalid")
    if value.get("maintained_main_commit_sha") != MAINTAINED_MAIN_SHA:
        blocking.add("maintained_control_dependency_main_sha_mismatch")

    dependencies = value.get("dependencies")
    if not isinstance(dependencies, list):
        blocking.add("maintained_control_dependencies_invalid")
        return 0
    observed: dict[str, Mapping[str, Any]] = {}
    for index, dependency in enumerate(dependencies):
        if not _mapping_has_exact_fields(dependency, _DEPENDENCY_FIELDS):
            blocking.add(f"maintained_control_dependency_shape_invalid:{index}")
            continue
        control_id = dependency.get("source_control_id")
        if control_id not in EXPECTED_EXTERNAL_CONTROL_DEPENDENCIES or control_id in observed:
            blocking.add(f"maintained_control_dependency_identity_invalid:{index}")
            continue
        observed[control_id] = dependency
    for control_id in sorted(set(EXPECTED_EXTERNAL_CONTROL_DEPENDENCIES) - set(observed)):
        blocking.add(f"maintained_control_dependency_missing:{control_id}")
    if len(dependencies) != len(EXPECTED_EXTERNAL_CONTROL_DEPENDENCIES):
        blocking.add("maintained_control_dependency_coverage_mismatch")

    for control_id in sorted(observed):
        dependency = observed[control_id]
        expected = EXPECTED_EXTERNAL_CONTROL_DEPENDENCIES[control_id]
        for field in (
            "dependency_id",
            "source_pr",
            "source_schema_or_contract_version",
        ):
            if dependency.get(field) != expected[field]:
                blocking.add(f"maintained_control_dependency_{field}_mismatch:{control_id}")
        if dependency.get("dependent_tracks") != list(expected["dependent_tracks"]):
            blocking.add(f"maintained_control_dependency_dependent_tracks_mismatch:{control_id}")
        if dependency.get("maintained_integrity_reference") != "path-binding:maintained-main":
            blocking.add(f"maintained_control_dependency_integrity_reference_invalid:{control_id}")
        if dependency.get("boundary_statements") != list(expected["boundary_statements"]):
            blocking.add(f"maintained_control_dependency_boundaries_mismatch:{control_id}")
        if dependency.get("covering_test_references") != list(expected["covering_test_references"]):
            blocking.add(f"maintained_control_dependency_tests_mismatch:{control_id}")
        if dependency.get("status") != "bound":
            blocking.add(f"maintained_control_dependency_status_invalid:{control_id}")
        if not _is_nonempty_string(dependency.get("evidence_reference")):
            blocking.add(f"maintained_control_dependency_evidence_reference_invalid:{control_id}")
        if dependency.get("authority_boundary") != DEPENDENCY_BOUNDARY_STATEMENT:
            blocking.add(f"maintained_control_dependency_authority_boundary_invalid:{control_id}")
        if not _is_nonempty_string(dependency.get("notes")):
            blocking.add(f"maintained_control_dependency_notes_invalid:{control_id}")

        path_digests = dependency.get("path_digests")
        if not isinstance(path_digests, list):
            blocking.add(f"maintained_control_dependency_paths_invalid:{control_id}")
            continue
        observed_paths: dict[str, Mapping[str, Any]] = {}
        for index, path_digest in enumerate(path_digests):
            if not _mapping_has_exact_fields(path_digest, _DEPENDENCY_PATH_FIELDS):
                blocking.add(f"maintained_control_dependency_path_shape_invalid:{control_id}:{index}")
                continue
            path = path_digest.get("relative_path")
            if not isinstance(path, str) or path not in expected["path_digests"] or path in observed_paths:
                blocking.add(f"maintained_control_dependency_path_identity_invalid:{control_id}:{index}")
                continue
            observed_paths[path] = path_digest
        if set(observed_paths) != set(expected["path_digests"]):
            blocking.add(f"maintained_control_dependency_path_coverage_mismatch:{control_id}")
        if len(path_digests) != len(expected["path_digests"]):
            blocking.add(f"maintained_control_dependency_path_count_mismatch:{control_id}")
        for path in sorted(observed_paths):
            path_digest = observed_paths[path]
            if path_digest.get("digest_algorithm") != "sha256":
                blocking.add(f"maintained_control_dependency_digest_algorithm_invalid:{control_id}:{path}")
            if path_digest.get("digest_mode") != "canonical-text":
                blocking.add(f"maintained_control_dependency_digest_mode_invalid:{control_id}:{path}")
            if path_digest.get("maintained_canonical_sha256") != expected["path_digests"][path]:
                blocking.add(f"maintained_control_dependency_digest_mismatch:{control_id}:{path}")
    return len(observed)


def _validate_dependency_observations(
    value: Any,
    blocking: set[str],
) -> int:
    if not isinstance(value, list):
        blocking.add("dependency_observations_invalid")
        return 0
    expected_rows: dict[tuple[str, str], tuple[str, str]] = {}
    for control_id, metadata in EXPECTED_EXTERNAL_CONTROL_DEPENDENCIES.items():
        for path, digest in metadata["path_digests"].items():
            expected_rows[(metadata["dependency_id"], path)] = (control_id, digest)
    observations: dict[tuple[str, str], Mapping[str, Any]] = {}
    for index, observation in enumerate(value):
        if not _mapping_has_exact_fields(observation, _DEPENDENCY_OBSERVATION_FIELDS):
            blocking.add(f"dependency_observation_shape_invalid:{index}")
            continue
        identity = (observation.get("dependency_id"), observation.get("relative_path"))
        if identity not in expected_rows or identity in observations:
            blocking.add(f"dependency_observation_identity_invalid:{index}")
            continue
        observations[identity] = observation
    if set(observations) != set(expected_rows):
        blocking.add("dependency_observation_coverage_mismatch")
    if len(value) != len(expected_rows):
        blocking.add("dependency_observation_count_mismatch")
    for identity in sorted(observations):
        observation = observations[identity]
        control_id, expected_digest = expected_rows[identity]
        dependency_id, path = identity
        if observation.get("source_control_id") != control_id:
            blocking.add(f"dependency_observation_control_mismatch:{dependency_id}:{path}")
        if observation.get("status") != "present":
            blocking.add(f"dependency_observation_status_invalid:{dependency_id}:{path}")
        observed_digest = observation.get("observed_canonical_sha256")
        if not _is_sha256(observed_digest):
            blocking.add(f"dependency_observation_digest_shape_invalid:{dependency_id}:{path}")
        elif observed_digest != expected_digest:
            blocking.add(f"dependency_observation_digest_mismatch:{dependency_id}:{path}")
        if not _is_nonempty_string(observation.get("evidence_reference")):
            blocking.add(f"dependency_observation_evidence_reference_invalid:{dependency_id}:{path}")
        if observation.get("authority_boundary") != DEPENDENCY_OBSERVATION_BOUNDARY_STATEMENT:
            blocking.add(f"dependency_observation_authority_boundary_invalid:{dependency_id}:{path}")
        if not _is_nonempty_string(observation.get("notes")):
            blocking.add(f"dependency_observation_notes_invalid:{dependency_id}:{path}")
    return len(observations)


def _validate_verification_results(
    value: Any,
    blocking: set[str],
    readiness: set[str],
) -> int:
    if not isinstance(value, list):
        blocking.add("verification_results_invalid")
        return 0
    results: dict[str, Mapping[str, Any]] = {}
    for index, result in enumerate(value):
        if not _mapping_has_exact_fields(result, _VERIFICATION_RESULT_FIELDS):
            blocking.add(f"verification_result_shape_invalid:{index}")
            continue
        command_id = result.get("command_id")
        if command_id not in EXPECTED_VERIFICATION_RESULT_COUNTS or command_id in results:
            blocking.add(f"verification_result_identity_invalid:{index}")
            continue
        results[command_id] = result
    for command_id in sorted(set(EXPECTED_VERIFICATION_RESULT_COUNTS) - set(results)):
        readiness.add(f"verification_result_missing:{command_id}")
    if len(value) != len(EXPECTED_VERIFICATION_RESULT_COUNTS):
        readiness.add("verification_result_coverage_incomplete")

    for command_id in sorted(results):
        result = results[command_id]
        if result.get("verification_id") != EXPECTED_VERIFICATION_IDS[command_id]:
            blocking.add(f"verification_result_id_mismatch:{command_id}")
        if result.get("evidence_source") != "external-verification-receipt-required":
            blocking.add(f"verification_result_evidence_source_invalid:{command_id}")
        if result.get("source_baseline_commit_sha") != SOURCE_BASELINE_SHA:
            blocking.add(f"verification_result_source_baseline_sha_mismatch:{command_id}")
        if result.get("execution_subject_type") != "pull-request-candidate-checkout":
            blocking.add(f"verification_result_execution_subject_invalid:{command_id}")
        if result.get("execution_candidate_reference") != "pull-request:#243":
            blocking.add(f"verification_result_candidate_reference_invalid:{command_id}")
        if result.get("execution_candidate_head_sha") is not None:
            blocking.add(f"verification_result_candidate_head_self_reference:{command_id}")
        if result.get("verification_scope") != EXPECTED_VERIFICATION_SCOPES[command_id]:
            blocking.add(f"verification_result_scope_mismatch:{command_id}")
        if result.get("external_execution_receipt_required") is not True:
            blocking.add(f"verification_result_external_receipt_boundary_invalid:{command_id}")
        if result.get("executed_by_evaluator") is not False:
            blocking.add(f"verification_result_execution_claim:{command_id}")
        if result.get("verification_results_are_completion_approval") is not False:
            blocking.add(f"verification_result_completion_approval_claim:{command_id}")
        if not _is_nonempty_string(result.get("evidence_reference")):
            blocking.add(f"verification_result_evidence_reference_invalid:{command_id}")
        for field in (
            "expected_test_count",
            "observed_test_count",
            "passes",
            "failures",
            "errors",
            "skips",
        ):
            if not _is_nonnegative_integer(result.get(field)):
                blocking.add(f"verification_result_count_invalid:{command_id}:{field}")
        if not isinstance(result.get("exit_code"), int) or isinstance(
            result.get("exit_code"), bool
        ):
            blocking.add(f"verification_result_exit_code_invalid:{command_id}")
        expected_count = EXPECTED_VERIFICATION_RESULT_COUNTS[command_id]
        if result.get("expected_test_count") != expected_count:
            blocking.add(f"verification_result_expected_count_mismatch:{command_id}")
        if result.get("observed_test_count") != expected_count:
            blocking.add(f"verification_result_observed_count_mismatch:{command_id}")
        counts = [result.get(field) for field in ("passes", "failures", "errors", "skips")]
        if all(_is_nonnegative_integer(count) for count in counts):
            if sum(counts) != result.get("observed_test_count"):
                blocking.add(f"verification_result_arithmetic_mismatch:{command_id}")
        failures = result.get("failures")
        errors = result.get("errors")
        skips = result.get("skips")
        exit_code = result.get("exit_code")
        if _is_nonnegative_integer(failures) and failures:
            blocking.add(f"verification_result_failures_present:{command_id}")
        if _is_nonnegative_integer(errors) and errors:
            blocking.add(f"verification_result_errors_present:{command_id}")
        if _is_nonnegative_integer(skips) and skips:
            readiness.add(f"verification_result_skips_present:{command_id}")
        if isinstance(exit_code, int) and not isinstance(exit_code, bool) and exit_code != 0:
            blocking.add(f"verification_result_nonzero_exit:{command_id}")
        coherent_pass = exit_code == 0 and failures == 0 and errors == 0
        expected_result = "pass" if coherent_pass else "fail"
        if result.get("result") not in {"pass", "fail"}:
            blocking.add(f"verification_result_value_invalid:{command_id}")
        elif result.get("result") != expected_result:
            blocking.add(f"verification_result_coherence_invalid:{command_id}")
    return len(results)


def _validate_verification_result_manifest(
    value: Any,
    blocking: set[str],
    readiness: set[str],
) -> int:
    if not _mapping_has_exact_fields(value, _VERIFICATION_RESULT_MANIFEST_FIELDS):
        blocking.add("verification_result_manifest_shape_invalid")
        return 0
    result_count = value.get("result_count")
    if not _is_nonnegative_integer(result_count):
        blocking.add("verification_result_count_invalid")
    elif result_count != len(EXPECTED_VERIFICATION_RESULT_COUNTS):
        readiness.add("verification_result_count_incomplete")
    if value.get("results_supplied_as_external_verification_evidence") is not True:
        blocking.add("verification_result_external_evidence_boundary_invalid")
    if value.get("result_records_are_execution_receipts") is not False:
        blocking.add("verification_result_receipt_claim_invalid")
    if value.get("external_execution_receipt_required") is not True:
        blocking.add("verification_result_external_receipt_requirement_invalid")
    if value.get("executed_by_evaluator") is not False:
        blocking.add("verification_result_manifest_execution_claim")
    if value.get("verification_results_are_completion_approval") is not False:
        blocking.add("verification_result_manifest_completion_approval_claim")
    return _validate_verification_results(value.get("results"), blocking, readiness)


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
    if value.get("execution_policy") != "declarative-commands-with-supplied-external-results":
        blocking.add("verification_execution_policy_invalid")
    if value.get("execution_results_recorded") is not True:
        blocking.add("verification_result_recording_invalid")
    if value.get("commands_executed_by_evaluator") is not False:
        blocking.add("verification_execution_claimed")
    if value.get("results_supplied_as_external_verification_evidence") is not True:
        blocking.add("verification_external_result_boundary_invalid")
    if value.get("external_execution_receipt_required") is not True:
        blocking.add("verification_external_receipt_requirement_invalid")
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
        if command.get("verification_scope") != EXPECTED_VERIFICATION_SCOPES[command_id]:
            blocking.add(f"verification_command_execution_scope_invalid:{command_id}")
        if command.get("required") is not True:
            readiness.add(f"verification_command_not_required:{command_id}")
        if command.get("expected_exit_code") != 0:
            readiness.add(f"verification_expected_exit_code_invalid:{command_id}")
        if command.get("executed_by_evaluator") is not False:
            blocking.add(f"verification_execution_claimed:{command_id}")
    return len(observed)


def _manifest_verification_records(
    manifest: Mapping[str, Any],
) -> tuple[dict[str, Mapping[str, Any]], dict[str, Mapping[str, Any]]]:
    command_records: dict[str, Mapping[str, Any]] = {}
    result_records: dict[str, Mapping[str, Any]] = {}
    command_manifest = manifest.get("verification_command_manifest")
    if isinstance(command_manifest, Mapping):
        commands = command_manifest.get("commands")
        if isinstance(commands, list):
            for command in commands:
                if isinstance(command, Mapping) and isinstance(command.get("command_id"), str):
                    command_records.setdefault(command["command_id"], command)
    result_manifest = manifest.get("verification_result_manifest")
    if isinstance(result_manifest, Mapping):
        results = result_manifest.get("results")
        if isinstance(results, list):
            for result in results:
                if isinstance(result, Mapping) and isinstance(result.get("command_id"), str):
                    result_records.setdefault(result["command_id"], result)
    return command_records, result_records


def _validate_receipt_executable_binding(
    value: Any,
    declared_argv: Any,
    actual_argv: Any,
    command_id: str,
    blocking: set[str],
) -> None:
    if not _mapping_has_exact_fields(value, _EXECUTABLE_BINDING_FIELDS):
        blocking.add(f"verification_receipt_executable_binding_shape_invalid:{command_id}")
        return
    declared_launcher = value.get("declared_launcher")
    actual_launcher = value.get("actual_launcher")
    if (
        not isinstance(declared_argv, list)
        or not declared_argv
        or declared_launcher != declared_argv[0]
    ):
        blocking.add(f"verification_receipt_declared_launcher_mismatch:{command_id}")
    if (
        not isinstance(actual_argv, list)
        or not actual_argv
        or actual_launcher != actual_argv[0]
    ):
        blocking.add(f"verification_receipt_actual_launcher_mismatch:{command_id}")
    if not _is_nonempty_string(declared_launcher):
        blocking.add(f"verification_receipt_declared_launcher_invalid:{command_id}")
    if not _is_nonempty_string(actual_launcher):
        blocking.add(f"verification_receipt_actual_launcher_invalid:{command_id}")

    substitution_detected = value.get("launcher_substitution_detected")
    substitution_declared = value.get("launcher_substitution_declared")
    if not _is_bool(substitution_detected):
        blocking.add(f"verification_receipt_substitution_detection_invalid:{command_id}")
    if not _is_bool(substitution_declared):
        blocking.add(f"verification_receipt_substitution_declaration_invalid:{command_id}")
    launchers_differ = (
        _is_nonempty_string(declared_launcher)
        and _is_nonempty_string(actual_launcher)
        and declared_launcher != actual_launcher
    )
    if _is_bool(substitution_detected) and substitution_detected != launchers_differ:
        blocking.add(f"verification_receipt_substitution_detection_mismatch:{command_id}")
    if launchers_differ and substitution_declared is not True:
        blocking.add(f"verification_receipt_undeclared_launcher_substitution:{command_id}")
    if not launchers_differ and substitution_declared is True:
        blocking.add(f"verification_receipt_false_launcher_substitution_declaration:{command_id}")

    if value.get("python_implementation") != "CPython":
        blocking.add(f"verification_receipt_python_implementation_invalid:{command_id}")
    python_version = value.get("python_version")
    if not isinstance(python_version, str) or re.fullmatch(r"\d+\.\d+\.\d+", python_version) is None:
        blocking.add(f"verification_receipt_python_version_invalid:{command_id}")


def _validate_external_verification_receipt(
    value: Any,
    manifest: Mapping[str, Any],
    blocking: set[str],
    readiness: set[str],
) -> tuple[int, bool]:
    if value is None:
        readiness.add("verification_receipt_missing")
        return 0, False
    receipt_blocking_before = set(blocking)
    if not _mapping_has_exact_fields(value, _VERIFICATION_RECEIPT_FIELDS):
        blocking.add("verification_receipt_shape_invalid")
        return 0, False
    if value.get("schema_version") != VERIFICATION_RECEIPT_SCHEMA_VERSION:
        blocking.add("verification_receipt_schema_version_mismatch")
    if value.get("document_type") != "external-verification-execution-receipt":
        blocking.add("verification_receipt_document_type_invalid")
    if value.get("repository") != "aa-os/aaos-public":
        blocking.add("verification_receipt_repository_mismatch")
    if value.get("pull_request_number") != 243:
        blocking.add("verification_receipt_pull_request_mismatch")
    if value.get("source_baseline_commit_sha") != SOURCE_BASELINE_SHA:
        blocking.add("verification_receipt_source_baseline_sha_mismatch")
    if value.get("source_baseline_commit_sha") != manifest.get("source_baseline_commit_sha"):
        blocking.add("verification_receipt_manifest_baseline_sha_mismatch")
    if value.get("execution_subject_type") != "pull-request-candidate-checkout":
        blocking.add("verification_receipt_execution_subject_invalid")
    if value.get("execution_candidate_reference") != "pull-request:#243":
        blocking.add("verification_receipt_candidate_reference_invalid")
    candidate_head_sha = value.get("execution_candidate_head_sha")
    if not _is_commit_sha(candidate_head_sha):
        blocking.add("verification_receipt_candidate_head_sha_invalid")
    elif candidate_head_sha == value.get("source_baseline_commit_sha"):
        blocking.add("verification_receipt_baseline_candidate_sha_conflated")
    if value.get("external_to_candidate_commit") is not True:
        blocking.add("verification_receipt_externality_invalid")
    if value.get("executed_by_evaluator") is not False:
        blocking.add("verification_receipt_execution_claim")
    if (
        value.get("non_authoritative_boundary_statement")
        != VERIFICATION_RECEIPT_NON_AUTHORITATIVE_BOUNDARY_STATEMENT
    ):
        blocking.add("verification_receipt_boundary_invalid")

    command_receipt_count = value.get("command_receipt_count")
    if not _is_nonnegative_integer(command_receipt_count):
        blocking.add("verification_receipt_command_count_invalid")
    elif command_receipt_count != len(EXPECTED_VERIFICATION_COMMANDS):
        blocking.add("verification_receipt_command_count_incomplete")
    commands = value.get("commands")
    if not isinstance(commands, list):
        blocking.add("verification_receipt_commands_invalid")
        return 0, False

    manifest_commands, manifest_results = _manifest_verification_records(manifest)
    observed: dict[str, Mapping[str, Any]] = {}
    for index, command in enumerate(commands):
        if not _mapping_has_exact_fields(command, _VERIFICATION_RECEIPT_COMMAND_FIELDS):
            blocking.add(f"verification_receipt_command_shape_invalid:{index}")
            continue
        command_id = command.get("command_id")
        if command_id not in EXPECTED_VERIFICATION_COMMANDS or command_id in observed:
            blocking.add(f"verification_receipt_command_identity_invalid:{index}")
            continue
        observed[command_id] = command

    for command_id in sorted(set(EXPECTED_VERIFICATION_COMMANDS) - set(observed)):
        blocking.add(f"verification_receipt_command_missing:{command_id}")
    if len(commands) != len(EXPECTED_VERIFICATION_COMMANDS):
        blocking.add("verification_receipt_command_coverage_incomplete")

    for command_id in sorted(observed):
        command = observed[command_id]
        expected_manifest_command = manifest_commands.get(command_id)
        expected_manifest_result = manifest_results.get(command_id)
        if command.get("verification_id") != EXPECTED_VERIFICATION_IDS[command_id]:
            blocking.add(f"verification_receipt_verification_id_mismatch:{command_id}")
        if command.get("verification_scope") != EXPECTED_VERIFICATION_SCOPES[command_id]:
            blocking.add(f"verification_receipt_scope_mismatch:{command_id}")
        if (
            isinstance(expected_manifest_command, Mapping)
            and command.get("verification_scope") != expected_manifest_command.get("verification_scope")
        ):
            blocking.add(f"verification_receipt_manifest_scope_mismatch:{command_id}")
        if command.get("source_baseline_commit_sha") != SOURCE_BASELINE_SHA:
            blocking.add(f"verification_receipt_command_baseline_sha_mismatch:{command_id}")
        if command.get("source_baseline_commit_sha") != value.get("source_baseline_commit_sha"):
            blocking.add(f"verification_receipt_command_receipt_baseline_mismatch:{command_id}")
        if command.get("execution_candidate_reference") != value.get("execution_candidate_reference"):
            blocking.add(f"verification_receipt_command_candidate_reference_mismatch:{command_id}")
        if command.get("execution_candidate_head_sha") != candidate_head_sha:
            blocking.add(f"verification_receipt_candidate_head_mismatch:{command_id}")
        if command.get("execution_candidate_head_sha") == command.get("source_baseline_commit_sha"):
            blocking.add(f"verification_receipt_command_baseline_candidate_sha_conflated:{command_id}")

        declared_argv = command.get("declared_logical_argv")
        expected_argv = (
            expected_manifest_command.get("argv")
            if isinstance(expected_manifest_command, Mapping)
            else EXPECTED_VERIFICATION_COMMANDS[command_id]["argv"]
        )
        if declared_argv != expected_argv:
            blocking.add(f"verification_receipt_declared_argv_mismatch:{command_id}")
        if (
            not isinstance(declared_argv, list)
            or not declared_argv
            or not all(_is_nonempty_string(argument) for argument in declared_argv)
        ):
            blocking.add(f"verification_receipt_declared_argv_invalid:{command_id}")
        actual_argv = command.get("actual_argv")
        if (
            not isinstance(actual_argv, list)
            or not actual_argv
            or not all(_is_nonempty_string(argument) for argument in actual_argv)
        ):
            blocking.add(f"verification_receipt_actual_argv_invalid:{command_id}")
        elif isinstance(declared_argv, list) and actual_argv[1:] != declared_argv[1:]:
            blocking.add(f"verification_receipt_actual_argv_binding_mismatch:{command_id}")
        _validate_receipt_executable_binding(
            command.get("executable_binding"),
            declared_argv,
            actual_argv,
            command_id,
            blocking,
        )

        for field in ("observed_test_count", "passes", "failures", "errors", "skips"):
            if not _is_nonnegative_integer(command.get(field)):
                blocking.add(f"verification_receipt_count_invalid:{command_id}:{field}")
        expected_count = EXPECTED_VERIFICATION_RESULT_COUNTS[command_id]
        if isinstance(expected_manifest_result, Mapping):
            manifest_expected_count = expected_manifest_result.get("expected_test_count")
            if manifest_expected_count != expected_count:
                blocking.add(f"verification_receipt_manifest_expected_count_mismatch:{command_id}")
            expected_count = manifest_expected_count
            for field in (
                "observed_test_count",
                "passes",
                "failures",
                "errors",
                "skips",
                "exit_code",
                "result",
            ):
                if command.get(field) != expected_manifest_result.get(field):
                    blocking.add(
                        "verification_receipt_manifest_result_binding_mismatch:"
                        f"{command_id}:{field}"
                    )
        if command.get("observed_test_count") != expected_count:
            blocking.add(f"verification_receipt_observed_count_mismatch:{command_id}")
        counts = [command.get(field) for field in ("passes", "failures", "errors", "skips")]
        if all(_is_nonnegative_integer(count) for count in counts):
            if sum(counts) != command.get("observed_test_count"):
                blocking.add(f"verification_receipt_count_arithmetic_mismatch:{command_id}")
        failures = command.get("failures")
        errors = command.get("errors")
        skips = command.get("skips")
        exit_code = command.get("exit_code")
        if _is_nonnegative_integer(failures) and failures:
            blocking.add(f"verification_receipt_failures_present:{command_id}")
        if _is_nonnegative_integer(errors) and errors:
            blocking.add(f"verification_receipt_errors_present:{command_id}")
        if _is_nonnegative_integer(skips) and skips:
            readiness.add(f"verification_receipt_skips_present:{command_id}")
        if not isinstance(exit_code, int) or isinstance(exit_code, bool):
            blocking.add(f"verification_receipt_exit_code_invalid:{command_id}")
        elif exit_code != 0:
            blocking.add(f"verification_receipt_nonzero_exit:{command_id}")
        coherent_pass = exit_code == 0 and failures == 0 and errors == 0
        expected_result = "pass" if coherent_pass else "fail"
        if command.get("result") not in {"pass", "fail"}:
            blocking.add(f"verification_receipt_result_invalid:{command_id}")
        elif command.get("result") != expected_result:
            blocking.add(f"verification_receipt_command_result_binding_mismatch:{command_id}")
        if not _is_rfc3339(command.get("execution_timestamp")):
            blocking.add(f"verification_receipt_execution_timestamp_invalid:{command_id}")
        if not _is_sha256(command.get("output_transcript_sha256")):
            blocking.add(f"verification_receipt_output_transcript_sha256_invalid:{command_id}")
        if not _is_nonempty_string(command.get("evidence_reference")):
            blocking.add(f"verification_receipt_evidence_reference_invalid:{command_id}")
        if command.get("executed_by_evaluator") is not False:
            blocking.add(f"verification_receipt_command_execution_claim:{command_id}")
        if command.get("verification_results_are_completion_approval") is not False:
            blocking.add(f"verification_receipt_completion_approval_claim:{command_id}")

    validated = (
        len(observed) == len(EXPECTED_VERIFICATION_COMMANDS)
        and set(blocking) == receipt_blocking_before
    )
    return len(observed), validated


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
    observation: Mapping[str, Any],
    verification_receipt: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Evaluate caller-supplied manifest, observation, and receipt evidence."""

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
    if manifest.get("source_baseline_commit_sha") != SOURCE_BASELINE_SHA:
        blocking.add("source_baseline_sha_mismatch")
    if manifest.get("execution_subject_type") != "pull-request-candidate-checkout":
        blocking.add("execution_subject_type_invalid")
    if manifest.get("execution_candidate_reference") != "pull-request:#243":
        blocking.add("execution_candidate_reference_invalid")
    if manifest.get("execution_candidate_head_sha") is not None:
        blocking.add("execution_candidate_head_self_reference")
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
    artifact_count = _validate_inventory(
        manifest.get("artifact_integrity_inventory"),
        blocking,
        readiness,
    )
    command_count = _validate_verification_manifest(
        manifest.get("verification_command_manifest"),
        blocking,
        readiness,
    )
    verification_result_count = _validate_verification_result_manifest(
        manifest.get("verification_result_manifest"),
        blocking,
        readiness,
    )
    verification_receipt_command_count, verification_receipt_validated = (
        _validate_external_verification_receipt(
            verification_receipt,
            manifest,
            blocking,
            readiness,
        )
    )
    dependency_count = _validate_maintained_control_dependency_inventory(
        manifest.get("maintained_control_dependency_inventory"),
        blocking,
    )

    artifact_observation_count = 0
    dependency_observation_count = 0
    validated_observation = _validate_repository_observation(observation, blocking)
    if validated_observation is not None:
        artifact_observation_count = _validate_artifact_observations(
            validated_observation.get("artifact_observations"),
            blocking,
            readiness,
        )
        dependency_observation_count = _validate_dependency_observations(
            validated_observation.get("dependency_observations"),
            blocking,
        )
    result = _result(
        blocking,
        readiness,
        evaluated_artifact_count=artifact_count,
        evaluated_artifact_observation_count=artifact_observation_count,
        evaluated_source_track_binding_count=len(_TRACK_METADATA),
        evaluated_maintained_control_dependency_count=dependency_count,
        evaluated_dependency_observation_count=dependency_observation_count,
        evaluated_verification_command_count=command_count,
        evaluated_verification_result_count=verification_result_count,
        evaluated_verification_receipt_command_count=verification_receipt_command_count,
        external_verification_receipt_validated=verification_receipt_validated,
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
            evaluated_artifact_observation_count=artifact_observation_count,
            evaluated_source_track_binding_count=len(_TRACK_METADATA),
            evaluated_maintained_control_dependency_count=dependency_count,
            evaluated_dependency_observation_count=dependency_observation_count,
            evaluated_verification_command_count=command_count,
            evaluated_verification_result_count=verification_result_count,
            evaluated_verification_receipt_command_count=verification_receipt_command_count,
            external_verification_receipt_validated=verification_receipt_validated,
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
    receipt_scenario = scenario_id in {
        "m15-e1-28",
        "m15-e1-29",
        "m15-e1-30",
        "m15-e1-31",
        "m15-e1-32",
        "m15-e1-33",
        "m15-e1-34",
    }
    expected_state_fields = (
        _SCENARIO_STATE_FIELDS | _SCENARIO_RECEIPT_STATE_FIELDS
        if receipt_scenario
        else _SCENARIO_STATE_FIELDS
    )
    if not _mapping_has_exact_fields(state, expected_state_fields):
        blocking.add("scenario_evidence_state_shape_invalid")
        return _result(blocking, readiness)
    non_boolean_fields = {
        "verification_failures",
        "verification_errors",
        "verification_skips",
        "required_artifact_status",
        "artifact_deferred_reason",
        "known_repository_local_completion_blockers",
    }
    boolean_fields = _SCENARIO_STATE_FIELDS - non_boolean_fields
    for field in sorted(boolean_fields):
        if not _is_bool(state.get(field)):
            blocking.add(f"scenario_boolean_invalid:{field}")
    if receipt_scenario:
        for field in sorted(_SCENARIO_RECEIPT_STATE_FIELDS):
            if not _is_bool(state.get(field)):
                blocking.add(f"scenario_boolean_invalid:{field}")
        if state.get("external_execution_receipt_present") is False:
            readiness.add("scenario_external_execution_receipt_missing")
        for field in (
            "candidate_head_matches_receipt",
            "baseline_candidate_sha_distinct",
            "launcher_substitution_declared",
            "interpreter_identity_present",
            "transcript_digest_present",
            "command_result_binding_matches",
        ):
            if state.get(field) is False:
                blocking.add(f"scenario_receipt_binding_check_failed:{field}")

    for field in (
        "manifest_shape_valid",
        "maintained_main_binding_valid",
        "source_track_bindings_valid",
        "artifact_inventory_complete",
        "artifact_integrity_valid",
        "internal_consistency_valid",
        "cross_control_matrix_bound",
        "verification_result_main_binding_valid",
        "verification_result_counts_valid",
        "maintained_control_dependencies_valid",
        "authority_boundary_valid",
    ):
        if state.get(field) is False:
            blocking.add(f"scenario_blocking_check_failed:{field}")
    for field in (
        "test_coverage_complete",
        "verification_command_manifest_complete",
        "verification_result_manifest_complete",
    ):
        if state.get(field) is False:
            readiness.add(f"scenario_readiness_check_failed:{field}")
    if state.get("verification_execution_claimed") is True:
        blocking.add("verification_execution_claimed")
    for field in ("verification_failures", "verification_errors", "verification_skips"):
        if not _is_nonnegative_integer(state.get(field)):
            blocking.add(f"scenario_count_invalid:{field}")
    if _is_nonnegative_integer(state.get("verification_failures")) and state.get("verification_failures"):
        blocking.add("scenario_verification_failures_present")
    if _is_nonnegative_integer(state.get("verification_errors")) and state.get("verification_errors"):
        blocking.add("scenario_verification_errors_present")
    if _is_nonnegative_integer(state.get("verification_skips")) and state.get("verification_skips"):
        readiness.add("scenario_verification_skips_present")
    _apply_artifact_lifecycle(
        state.get("required_artifact_status"),
        state.get("artifact_deferred_reason"),
        "required-artifact",
        "scenario_artifact",
        blocking,
        readiness,
    )
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


__all__ = [
    "ARTIFACT_LIFECYCLE_STATUSES",
    "BLOCKED",
    "EXPECTED_EXTERNAL_CONTROL_DEPENDENCIES",
    "EXPECTED_TRACK_COUNTS",
    "EXPECTED_TYPE_COUNTS",
    "EXPECTED_MAINTAINED_ARTIFACT_DIGESTS",
    "EXPECTED_SCENARIO_TITLES",
    "EXPECTED_VERIFICATION_COMMANDS",
    "EXPECTED_VERIFICATION_IDS",
    "EXPECTED_VERIFICATION_RESULT_COUNTS",
    "EXPECTED_VERIFICATION_SCOPES",
    "MAINTAINED_MAIN_SHA",
    "MANIFEST_SCHEMA_VERSION",
    "NON_AUTHORITATIVE_BOUNDARY_STATEMENT",
    "NOT_READY",
    "OBSERVATION_SCHEMA_VERSION",
    "OUTCOMES",
    "READY_FOR_COMPLETION_REVIEW",
    "REQUIRED_ARTIFACTS",
    "RESULT_SCHEMA_VERSION",
    "SCENARIO_SCHEMA_VERSION",
    "SOURCE_BASELINE_SHA",
    "SYNTHETIC_SCENARIO_BOUNDARY_STATEMENT",
    "VERIFICATION_RECEIPT_NON_AUTHORITATIVE_BOUNDARY_STATEMENT",
    "VERIFICATION_RECEIPT_SCHEMA_VERSION",
    "evaluate_operational_readiness",
    "evaluate_synthetic_scenario",
]
