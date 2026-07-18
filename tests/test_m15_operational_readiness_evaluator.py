import ast
import copy
import hashlib
import inspect
import json
import re
import tempfile
import unittest
from collections import Counter
from pathlib import Path

import runtime.m15_operational_readiness_evaluator as evaluator_module
from runtime.m15_operational_readiness_evaluator import (
    BLOCKED,
    MAINTAINED_MAIN_SHA,
    NON_AUTHORITATIVE_BOUNDARY_STATEMENT,
    NOT_READY,
    OUTCOMES,
    READY_FOR_COMPLETION_REVIEW,
    SYNTHETIC_SCENARIO_BOUNDARY_STATEMENT,
    evaluate_operational_readiness,
    evaluate_synthetic_scenario,
)
from runtime.repository_artifact_digest import (
    RepositoryArtifactTextError,
    canonicalize_utf8_repository_text,
    sha256_repository_file,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "examples" / "public-integration-pack-pilot"
MANIFEST_PATH = FIXTURE_ROOT / "m15-operational-readiness-manifest.json"
MATRIX_PATH = FIXTURE_ROOT / "m15-cross-control-matrix.json"
SCHEMA_PATH = ROOT / "schemas" / "m15-operational-readiness.schema.json"
CONTRACT_PATH = ROOT / "docs" / "learning-governance" / "m15-operational-readiness-contract.md"
EVALUATOR_PATH = ROOT / "runtime" / "m15_operational_readiness_evaluator.py"
SCENARIO_PATHS = sorted(
    FIXTURE_ROOT.glob("m15-operational-readiness-[0-9][0-9]-*.json")
)

ARTIFACT_AUTHORITY_BOUNDARY = (
    "Artifact observation is evidence only; it grants no completion, "
    "tracker-closure, README, tag, release, execution, or governance authority."
)
DEPENDENCY_AUTHORITY_BOUNDARY = (
    "Maintained-control dependency observation is evidence only; it does not "
    "grant control admission, completion, release, execution, or governance authority."
)
OBSERVATION_AUTHORITY_BOUNDARY = (
    "Observation evidence records bounded repository state only; it is not completion "
    "approval, tracker #231 closure, README authorization, tag authorization, release "
    "authorization, execution authority, or governance authority."
)


def _digest_path_lines(text):
    return {
        path: digest
        for digest, path in (
            line.strip().split(" ", 1) for line in text.strip().splitlines()
        )
    }


# This literal is deliberately independent of the evaluator and manifest. A change to
# either maintained binding must be consciously reflected here, so code + data co-drift
# cannot silently establish a new source of truth.
PINNED_MATERIAL_DIGESTS = _digest_path_lines(
    """
10152aea4911711c09edbb21bb78696244f9e71fe8447d9737a907eb8a3bb9df docs/learning-governance/m15-capability-memory-pack-contract.md
b28de6f87b675e96db229a71dd0b34d54e5e065fd0f9205cb56b3018fddacae3 docs/learning-governance/m15-core-learning-proof-contract.md
23f29596100bd85fb52bc46210548a9404c21bf10d532d692d7fc43b84d64fdf docs/learning-governance/m15-cross-control-regression-contract.md
d6c421be2fede2480f8bc2f3c8b0221e1862273184915b2ed317e69357c60f47 docs/learning-governance/m15-lineage-rollback-portability-contract.md
23f2502a23422d14215860d4dda5a154254365224909d4ac9a2c8a0eb8b3ed22 examples/public-integration-pack-pilot/m15-capability-pack-altered-derived-specification.json
1193ba3eeb7c1462816a7b1fbf1a6d9ae16ac11a22b5c315715378d95565a564 examples/public-integration-pack-pilot/m15-capability-pack-altered-graph.json
6e74d48b6f974a66f1187c7cefbaf45a8721c252a7c31bc84f250c828dde06e4 examples/public-integration-pack-pilot/m15-capability-pack-executable-authority-claim.json
2d585df48eb9899f80f3558767341c7d492bce14ee155552fad9f9571d6e31cf examples/public-integration-pack-pilot/m15-capability-pack-incompatible-runtime.json
2b6a9e3a8eae10299cd069bd938643c170669ce2eabce9f0200d2a981849a5de examples/public-integration-pack-pilot/m15-capability-pack-missing-license-usage-boundary-evidence.json
797a42b9c816acccd31759cb7b40a066ab70bcaa19683dc0ddbe66421fc538a3 examples/public-integration-pack-pilot/m15-capability-pack-revoked.json
60041c22641c33104f2d990829a873dbc68b865fc31396b030ec60411f270e3a examples/public-integration-pack-pilot/m15-capability-pack-source-digest-mismatch.json
92ee515bd75303c77531ce2efb9dc445368e1cebe5e61cea1e3f4f073375cbca examples/public-integration-pack-pilot/m15-capability-pack-stale-specification.json
66a601ed0f289e785f37e629a4fdc839186c22a93dabc6cec6387b0f188b97d8 examples/public-integration-pack-pilot/m15-capability-pack-valid-verified.json
96a657018d7a8be20faf90523957a4ccec0537f5b853f180c818710c17de975f examples/public-integration-pack-pilot/m15-cross-control-01.json
cdc696021de2603bb99114d253210eb7ce005527b74d22dbc9dc5dcf178c88db examples/public-integration-pack-pilot/m15-cross-control-02.json
aa91eb15b431723c4d99550cd38ea3e1a63a064f7b641f58960e295c942525c7 examples/public-integration-pack-pilot/m15-cross-control-03.json
6d96c04a17dda4928caf8cf332252a17599b3e146a210affefaa1ee6eae6374d examples/public-integration-pack-pilot/m15-cross-control-04.json
bcd86d84b9a2d24615764f4d4f5046c7e19d0f6bc0eddf28790f51c1d54896fb examples/public-integration-pack-pilot/m15-cross-control-05.json
6c70e7efa7000e76574815ddb593635c6bd48641ba36c12aa3d662de194b524b examples/public-integration-pack-pilot/m15-cross-control-06.json
3a4e8ae6456c76d0fab6111055ab4cc8f6b179a403e87ea6af13e535391d2752 examples/public-integration-pack-pilot/m15-cross-control-07.json
201f4b3eb1d7c87329f3e40b0602f8556a0b3fddc8501999b1f2e61ba194adfc examples/public-integration-pack-pilot/m15-cross-control-08.json
8e7c85f22fe9ef0e66dbf29d88ddf35507ce3daf730eb5c467f3585b038cb9f8 examples/public-integration-pack-pilot/m15-cross-control-09.json
b9ff7b587f1ebffa9a4994802e356915ea0c4c91bb83402493ed37747c202e98 examples/public-integration-pack-pilot/m15-cross-control-10.json
3a98010d7cea9ff288f47646721c189bb9019e3285959c6fae3018c8a6b783b3 examples/public-integration-pack-pilot/m15-cross-control-11.json
16b109d3938a7befb0e6947cef5e52e5bf922ba6389ffeb920a696f3f4049c49 examples/public-integration-pack-pilot/m15-cross-control-12.json
391a15a1641c4c8e172ea9128a1bbe5c55c60d672b8ec4f3c10ac712f7216841 examples/public-integration-pack-pilot/m15-cross-control-13.json
bc0c3ac7a5f04e0a25684652d4e966b3e704514ac98454f98037ae1e52dc8693 examples/public-integration-pack-pilot/m15-cross-control-14.json
48e2ac1afb874f9b95a7f812df7bcb30ed3f06cc978be3b6118353cf0dd11806 examples/public-integration-pack-pilot/m15-cross-control-15.json
0def119664507d11c91927a966055156b2be3c8e7a635d68b17ea8e23ad28497 examples/public-integration-pack-pilot/m15-cross-control-16.json
f3b8bbcb6157738873aa1f6db18ce7bfbfdfa40d4e0ca75a5b7232d96d038b9a examples/public-integration-pack-pilot/m15-cross-control-17.json
62ffa63f03979736e98f74da38bf5830e01cdaf8e77b5502f2ed85af0de1f629 examples/public-integration-pack-pilot/m15-cross-control-18.json
a4621c85ee076e2bdc8af6811f4a12f1eb166c2c9f89d6a9bfe65a69f0beae4b examples/public-integration-pack-pilot/m15-cross-control-19.json
af2568e0286541a8e44b0be3580914c3cd558490e19acf0d8406f505aaf947b6 examples/public-integration-pack-pilot/m15-cross-control-20.json
3f9806c2700c359f7241d26c348dd18b6595ecd1ad115af9e583a609694d8ab4 examples/public-integration-pack-pilot/m15-cross-control-21.json
5dae89de53a3698dde0fc598e63b1e34d7a2b9ceff66f041475d022afcfe4060 examples/public-integration-pack-pilot/m15-cross-control-22.json
6402079bda56eb8a086613ef1e3541d42f0fbe5f546570e19b964b4ab729bcfa examples/public-integration-pack-pilot/m15-cross-control-23.json
1da9dc250c9e3676257e93f4736133f5ec17d438e0c667f675ab1caf8d415c7c examples/public-integration-pack-pilot/m15-cross-control-24.json
9d05d2a5331b02d673b2ee2c01e05e0aa098e981d10b9b072a8b92af226b0ca0 examples/public-integration-pack-pilot/m15-cross-control-matrix.json
56209ec5b821dab72f23e02b9472de8323353d706e60ec431e147c2208316db0 examples/public-integration-pack-pilot/m15-learning-proof-approved-evaluation-only.json
8d1d1d46bfca7d4110978e17e7139041305b068979ee62cea939291138e91971 examples/public-integration-pack-pilot/m15-learning-proof-contaminated-quarantine.json
bf4c915b14fd968e5f50dc8b10b70edc9a56db54a13120891b9a7fedf9203ba8 examples/public-integration-pack-pilot/m15-learning-proof-rejected-untrusted-correction.json
25f6ec6fcb7ec0e47ed125ffb2e328bddeba30f50a81a4ac1ecf4afb37b4812d examples/public-integration-pack-pilot/m15-lineage-rollback-portability-decision-proof-deletion-execution-authority.json
b710d26212866fa40bcb4335385194449113758a102a59c0ddac2cc36332fc4b examples/public-integration-pack-pilot/m15-lineage-rollback-portability-deletion-pending-unresolved-copies.json
528b31423f15fd08c3b633ab2d079ed3ec5fdc5424cf3886755673931d439b6b examples/public-integration-pack-pilot/m15-lineage-rollback-portability-false-physical-provider-erasure-claim.json
437d5afb63e3b7cbac8bc791d198a38712acf755221a3af664412b94c238cdcc examples/public-integration-pack-pilot/m15-lineage-rollback-portability-learning-proof-rollback-authority.json
fd3c8a08e02916523848a5ce8b0f544a741f65549ebd5e2e60fba70991fd1acb examples/public-integration-pack-pilot/m15-lineage-rollback-portability-missing-downstream-dependency-declaration.json
14c4baacce910250ac45d540abebd29581e023875a22e1a88f2d3b2dcd946e25 examples/public-integration-pack-pilot/m15-lineage-rollback-portability-model-removal-drill-provider-specific-blocker.json
4d39580e90388765d8dcea32f3d6c9001463ddae5a3047a5e388e1721ec5a221 examples/public-integration-pack-pilot/m15-lineage-rollback-portability-model-removal-drill-success.json
d42011b3a5ba913bc5c3170c09273ec3170a8d3be613a33b178e19299a3a1dc2 examples/public-integration-pack-pilot/m15-lineage-rollback-portability-qualified-deleted-no-physical-erasure.json
82e419a91dfe334355dde8f263645e011782a83c91484fb2b0b79c803ecdd3c8 examples/public-integration-pack-pilot/m15-lineage-rollback-portability-replacement-model-use-incorrectly-authorized.json
1bdbd1bc3f61e1a83973da8dd466468844377831d8436d7c8f787a259a15fe3b examples/public-integration-pack-pilot/m15-lineage-rollback-portability-revoked-capability-pack-unresolved-downstream-use.json
b6f48aed01b78b7489bc364e8537ce0916fa1b7defed49a9cd15b9ea322e8579 examples/public-integration-pack-pilot/m15-lineage-rollback-portability-rollback-blocked-incompatible-dependent.json
0ad2376f0359f75b0afd38432ce4c921e2466f2b60732c98a1bb24b3a7db788f examples/public-integration-pack-pilot/m15-lineage-rollback-portability-rollback-ready-complete-dependency-evidence.json
8cc561a8bdc9c38641ea2522c466b910ce29590872f7645ec2207eeb58559dc7 examples/public-integration-pack-pilot/m15-lineage-rollback-portability-superseded-learning-artifact-known-dependents.json
a3c4e3c1c99341d07ff04612514d2abc25852acefd643b45852e98287de572fd examples/public-integration-pack-pilot/m15-lineage-rollback-portability-valid-complete-dependency-graph.json
5e45bbe0f311c3bfcc4d10ed7dc2b1eacbb8d64e4d8d2c922e74d558e66181e2 runtime/m15_capability_memory_pack_evaluator.py
4a412bbd215ed3974d842bc09ee0011b4148f849d5d8e91611a324ef83fc6af6 runtime/m15_cross_control_regression_evaluator.py
1f0d1eda01e3df92fba069ffd75eff34232c7bfe39f0b252b80cae2d1a2f00c8 runtime/m15_learning_proof_evaluator.py
4337f04d0619f4e153088fe080fac7d1a2d976e3e04f6a124169e3d96c73f6a4 runtime/m15_lineage_rollback_portability_evaluator.py
051436c094413715849ddffd8b54beebb7239f8f288fd2849c333b412e374351 schemas/m15-capability-memory-pack.schema.json
d52ef7010f596e28592c738b536f0d3131e60c5886ed538f1a57a067c675d651 schemas/m15-cross-control-regression.schema.json
c03bd734f287fae23deb7f8d3eaf2ccb501774caeccbe85d6520c57b7fdc1a44 schemas/m15-learning-proof.schema.json
8702925c5a2c62efb77fc44cb68328f5be04b963afa27f366f99bef2ee071949 schemas/m15-lineage-rollback-portability.schema.json
806eb6fe660465a5ac72f553cb336cbe3822170218040f7f036e60d4680a28db tests/test_m15_capability_memory_pack_evaluator.py
472b75a13498fbc257bbca9cf6eabba688e07cb236f36e3778587b0025415c78 tests/test_m15_cross_control_regression_evaluator.py
d382b1239bb623f3d165b24bda830a285f1aeaee93e53b9dc9abb8ada7b6b6c4 tests/test_m15_learning_proof_evaluator.py
5268f73a441898467e9b8f9471cfc4b9bd4fa27b7b67444fbf852d697d90f4c9 tests/test_m15_lineage_rollback_portability_evaluator.py
"""
)

PINNED_DEPENDENCY_DIGESTS = _digest_path_lines(
    """
f3453af5c1829a28c791b665640e24940ececdc211e364360635bfe39573e81d runtime/public_issue_exfiltration_gate_evaluator.py
e3ab2be88dfeb8ec85a9cd12936f33b54476e46c22eeebe650648a8678d962bc tests/test_public_issue_exfiltration_gate_evaluator.py
ac682908ba081cfc58726046efcb928c51e64eb2037f03354fda80afeb0846a9 examples/public-integration-pack-pilot/m14-public-issue-exfiltration-gate-fixtures.json
465a0aba8beb49a6d6ad55e0bfce65ab74f5368164c758841ab202c50432ef35 runtime/ai_authored_pr_provenance_evaluator.py
e648d2606d38f05063d72be0fa270a0191a28dca24a5fc07e80414faa4fc1f8f tests/test_ai_authored_pr_provenance_evaluator.py
e72636d1871f2c1232c811aec41ca9724be1505916d4804a05be75e600f3808a examples/public-integration-pack-pilot/m14-ai-authored-pr-provenance-fixtures.json
af8ba9426f1bda5c2b9a09fad7a2b03ef2c4d04a178e4f414519bf837ff19bf1 .github/workflows/m14-ai-pr-provenance.yml
bb81697df1be79b96a6af373ce63314a01ac73392b3cdb97981abaddbe6a4400 runtime/skill_admission_evaluator.py
45ba9f2f8369bf0c127993c480e5091a1a2ee8f7ca2a0be2f579b3de38011b83 tests/test_skill_admission_evaluator.py
4fc229be3883a2681f8ebfc3f2eb828514cd3a2d6729c5841bab5a7efe609509 examples/public-integration-pack-pilot/m14-skill-admission-fixtures.json
3271905c87a0b6914bbb48d7b77b1a6bb51741a2acdd36fbfeb973dc287c9884 runtime/external_evidence_admission_evaluator.py
3d077cc6699217f2076fa98e098761af145ffd60210be2e0c40a66b8cfe98aa7 tests/test_external_evidence_admission_evaluator.py
adc866d069143c688657d8938f18e76d9448d9223fa4ba2e3e857f62af462ebd schemas/external-evidence-admission.schema.json
3c02b06822ba5d11e1863c640ff8f34d474994d4e412e88aed39b17b7aeb32c1 examples/external-evidence-admission/twinkle-hub-fixtures.json
51a413dc5303d64d49e958ffde970925ffc5aebead3435f8cf714e6112e1b48c runtime/m14_cross_control_authority_boundary_evaluator.py
5a4a5e764655382e2b19aa5a4e8a5a6a2b5082ade733e7125d88dfd2ba6cfc52 tests/test_m14_cross_control_authority_boundary_evaluator.py
f44b6d3298922608096c10f248955fa4c25e8d4a3452d6d7c585f9237129809d examples/public-integration-pack-pilot/m14-cross-control-authority-boundary-regression-fixtures.json
"""
)

PINNED_DEPENDENCY_METADATA = {
    "m14-public-output-exfiltration": {
        "dependency_id": "m15-e1-maintained-control-01",
        "source_pr": "#204",
        "version": "public-output-gate-m14-draft-001",
        "dependent_tracks": ["track-a", "track-b", "cross-track"],
        "adapter": "SourceControlCompositionTests.test_track_a_blocked_by_existing_public_output_control",
        "boundary_digest": "7ab0aa8103f85d528992b8fe6e4b915aad8c54647fdae316b325ce62fc8d8739",
    },
    "m14-ai-provenance": {
        "dependency_id": "m15-e1-maintained-control-02",
        "source_pr": "#206",
        "version": "unversioned-contract/source-pr-206/path-bound-maintained-main",
        "dependent_tracks": ["track-a"],
        "adapter": "SourceControlCompositionTests.test_provenance_success_cannot_complete_human_review",
        "boundary_digest": "d9083d913cffa19146479a1160a641aab68709b4919d82b2a9f84c543d9f8214",
    },
    "m14-skill-admission": {
        "dependency_id": "m15-e1-maintained-control-03",
        "source_pr": "#208",
        "version": "aaos-skill-admission-policy-m14-synthetic-v1",
        "dependent_tracks": ["track-a", "track-b"],
        "adapter": "SourceControlCompositionTests.test_track_b_cannot_bypass_rejected_skill_admission",
        "boundary_digest": "2d9b353f9a4ce7ca528ab3514f16e282eeb6de88409c8bff444df366aee93387",
    },
    "external-evidence-admission": {
        "dependency_id": "m15-e1-maintained-control-04",
        "source_pr": "#209",
        "version": "aaos-external-evidence-admission-v1",
        "dependent_tracks": ["track-b"],
        "adapter": "SourceControlCompositionTests.test_external_evidence_states_cannot_bypass_gate",
        "boundary_digest": "374210f01fa81768284e8845b38db7b43c7e5f4b438c5041eba622bf603ad328",
    },
    "m14-cross-control-authority": {
        "dependency_id": "m15-e1-maintained-control-05",
        "source_pr": "#210",
        "version": "unversioned-contract/source-pr-210/path-bound-maintained-main",
        "dependent_tracks": ["track-a", "track-b", "track-c", "cross-track"],
        "adapter": "SourceControlCompositionTests.test_tracks_a_b_c_cannot_aggregate_authority",
        "boundary_digest": "d17e4c673564e2c848638d281882360fe5c03865e0a006bd824ec8d59ac39ddb",
    },
}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_manifest():
    return load_json(MANIFEST_PATH)


def scenario(number):
    matches = [
        path
        for path in SCENARIO_PATHS
        if path.name.startswith(f"m15-operational-readiness-{number:02d}-")
    ]
    if len(matches) != 1:
        raise AssertionError((number, matches))
    return load_json(matches[0])


def build_repository_observation(manifest=None, repository_root=ROOT):
    """Test-only adapter: inspect maintained files and supply inert caller data."""

    manifest = load_manifest() if manifest is None else manifest
    artifact_observations = []
    for entry in manifest["artifact_integrity_inventory"]["artifacts"]:
        relative_path = entry["relative_path"]
        observed = sha256_repository_file(repository_root, relative_path, mode="text")
        status = (
            "present"
            if observed == entry["maintained_canonical_sha256"]
            else "digest_mismatch"
        )
        artifact_observations.append(
            {
                "artifact_id": entry["artifact_id"],
                "relative_path": relative_path,
                "status": status,
                "observed_canonical_sha256": observed,
                "evidence_reference": f"test-observation:{entry['artifact_id']}",
                "authority_boundary": ARTIFACT_AUTHORITY_BOUNDARY,
                "notes": "Test-only canonical-text repository observation.",
                "deferred_reason": None,
            }
        )

    dependency_observations = []
    dependencies = manifest["maintained_control_dependency_inventory"]["dependencies"]
    for dependency in dependencies:
        for path_digest in dependency["path_digests"]:
            relative_path = path_digest["relative_path"]
            observed = sha256_repository_file(repository_root, relative_path, mode="text")
            status = (
                "present"
                if observed == path_digest["maintained_canonical_sha256"]
                else "digest_mismatch"
            )
            dependency_observations.append(
                {
                    "dependency_id": dependency["dependency_id"],
                    "source_control_id": dependency["source_control_id"],
                    "relative_path": relative_path,
                    "status": status,
                    "observed_canonical_sha256": observed,
                    "evidence_reference": (
                        f"test-observation:{dependency['dependency_id']}:{relative_path}"
                    ),
                    "authority_boundary": DEPENDENCY_AUTHORITY_BOUNDARY,
                    "notes": "Test-only maintained-control dependency observation.",
                }
            )

    return {
        "schema_version": "m15-operational-readiness-observation/v1",
        "document_type": "maintained-operational-readiness-observation",
        "record_id": "urn:aaos:m15:operational-readiness:e1:maintained-main:observation",
        "issue": "#242",
        "track": "E1",
        "maintained_repository": "aa-os/aaos-public",
        "maintained_branch": "main",
        "maintained_main_commit_sha": MAINTAINED_MAIN_SHA,
        "artifact_observation_count": len(artifact_observations),
        "dependency_observation_count": len(dependency_observations),
        "artifact_observations": artifact_observations,
        "dependency_observations": dependency_observations,
        "generated_by_evaluator": False,
        "non_authoritative_boundary_statement": OBSERVATION_AUTHORITY_BOUNDARY,
    }


def _json_equal(left, right):
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left == right
    return left == right


def _resolve_local_json_pointer(document, reference):
    if not reference.startswith("#/"):
        raise AssertionError(f"unsupported schema reference: {reference}")
    value = document
    for raw_token in reference[2:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        value = value[token]
    return value


def validate_draft_2020_12_subset(instance, schema, *, root_schema=None, path="$"):
    """Validate the dependency-free Draft 2020-12 subset used by E1."""

    root_schema = schema if root_schema is None else root_schema
    if schema is True:
        return []
    if schema is False:
        return [f"{path}: rejected by false schema"]
    if "$ref" in schema:
        return validate_draft_2020_12_subset(
            instance,
            _resolve_local_json_pointer(root_schema, schema["$ref"]),
            root_schema=root_schema,
            path=path,
        )

    errors = []
    if "oneOf" in schema:
        branch_errors = [
            validate_draft_2020_12_subset(
                instance, branch, root_schema=root_schema, path=path
            )
            for branch in schema["oneOf"]
        ]
        if sum(not branch for branch in branch_errors) != 1:
            errors.append(f"{path}: oneOf must match exactly one schema")

    if "const" in schema and not _json_equal(instance, schema["const"]):
        errors.append(f"{path}: const mismatch")
    if "enum" in schema and not any(
        _json_equal(instance, item) for item in schema["enum"]
    ):
        errors.append(f"{path}: value is not in enum")

    type_matches = {
        "object": isinstance(instance, dict),
        "array": isinstance(instance, list),
        "string": isinstance(instance, str),
        "integer": isinstance(instance, int) and not isinstance(instance, bool),
        "boolean": isinstance(instance, bool),
        "null": instance is None,
    }
    expected_type = schema.get("type")
    if expected_type is not None:
        expected_types = (
            expected_type if isinstance(expected_type, list) else [expected_type]
        )
        if not any(type_matches[item] for item in expected_types):
            errors.append(f"{path}: expected {expected_type}")
            return errors

    if isinstance(instance, dict):
        properties = schema.get("properties", {})
        for name in schema.get("required", []):
            if name not in instance:
                errors.append(f"{path}: missing required property {name}")
        for name, value in instance.items():
            if name in properties:
                errors.extend(
                    validate_draft_2020_12_subset(
                        value,
                        properties[name],
                        root_schema=root_schema,
                        path=f"{path}.{name}",
                    )
                )
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: additional property {name}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: fewer than minItems")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: more than maxItems")
        if schema.get("uniqueItems") is True:
            for index, item in enumerate(instance):
                if any(_json_equal(item, prior) for prior in instance[:index]):
                    errors.append(f"{path}: duplicate array item at {index}")
        prefix_items = schema.get("prefixItems", [])
        for index, item_schema in enumerate(prefix_items[: len(instance)]):
            errors.extend(
                validate_draft_2020_12_subset(
                    instance[index],
                    item_schema,
                    root_schema=root_schema,
                    path=f"{path}[{index}]",
                )
            )
        items_schema = schema.get("items", True)
        if items_schema is False and len(instance) > len(prefix_items):
            errors.append(f"{path}: items after prefixItems are forbidden")
        elif isinstance(items_schema, dict):
            for index in range(len(prefix_items), len(instance)):
                errors.extend(
                    validate_draft_2020_12_subset(
                        instance[index],
                        items_schema,
                        root_schema=root_schema,
                        path=f"{path}[{index}]",
                    )
                )

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: shorter than minLength")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{path}: longer than maxLength")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append(f"{path}: pattern mismatch")
    if (
        isinstance(instance, int)
        and not isinstance(instance, bool)
        and "minimum" in schema
        and instance < schema["minimum"]
    ):
        errors.append(f"{path}: below minimum")
    return errors


def _boundary_digest(statements):
    payload = json.dumps(
        statements, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class M15OperationalReadinessContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_json(SCHEMA_PATH)
        cls.manifest = load_manifest()
        cls.observation = build_repository_observation(cls.manifest)

    def test_01_schema_has_three_strict_document_kinds(self):
        self.assertEqual(
            self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema"
        )
        self.assertEqual(len(self.schema["oneOf"]), 3)
        for name in ("maintainedManifest", "observationEvidence", "syntheticScenario"):
            self.assertFalse(self.schema["$defs"][name]["additionalProperties"])

    def test_02_schema_distinguishes_commit_and_digest_shapes(self):
        self.assertEqual(self.schema["$defs"]["gitCommitSha"]["pattern"], "^[0-9a-f]{40}$")
        self.assertEqual(self.schema["$defs"]["sha256"]["pattern"], "^[0-9a-f]{64}$")

    def test_03_manifest_binds_issue_track_repository_and_main(self):
        self.assertEqual(self.manifest["issue"], "#242")
        self.assertEqual(self.manifest["track"], "E1")
        self.assertEqual(self.manifest["maintained_repository"], "aa-os/aaos-public")
        self.assertEqual(self.manifest["maintained_branch"], "main")
        self.assertEqual(self.manifest["maintained_main_commit_sha"], MAINTAINED_MAIN_SHA)

    def test_04_manifest_binds_exact_track_pr_heads_and_merges(self):
        expected = {
            "track-a": ("#232", "#233", "603a26890ceee940b0a3c9009e06d994f9f2f342", "6e0fa4e8fdf4a672581cd897d52743d0462f0d4b"),
            "track-b": ("#234", "#237", "270a5bbb536c6bf0726e95455d4bb61ac86d693e", "8e475518f2da6232ae9a6264d8e9c9f1e5fc514a"),
            "track-c": ("#238", "#239", "5f98f6c86e6b61d50b1c8183aca0736a3419c533", "2d8bab3a84675543c34231a9e04521379febdac1"),
            "track-d": ("#240", "#241", "3bec19e42693b757b9abbb077146ca9860d48c1e", MAINTAINED_MAIN_SHA),
        }
        observed = {
            item["track_id"]: (
                item["source_issue"],
                item["implementation_pr"],
                item["head_sha"],
                item["merge_sha"],
            )
            for item in self.manifest["source_track_bindings"]
        }
        self.assertEqual(observed, expected)

    def test_05_material_inventory_has_exact_counts_and_unique_ids(self):
        inventory = self.manifest["artifact_integrity_inventory"]
        artifacts = inventory["artifacts"]
        self.assertEqual(inventory["artifact_count"], 67)
        self.assertEqual(inventory["track_artifact_counts"], evaluator_module.EXPECTED_TRACK_COUNTS)
        self.assertEqual(inventory["artifact_type_counts"], evaluator_module.EXPECTED_TYPE_COUNTS)
        self.assertEqual(Counter(item["track_id"] for item in artifacts), inventory["track_artifact_counts"])
        self.assertEqual(Counter(item["artifact_type"] for item in artifacts), inventory["artifact_type_counts"])
        self.assertEqual(len({item["artifact_id"] for item in artifacts}), 67)

    def test_06_material_paths_and_digests_match_independent_pins(self):
        declared = {
            item["relative_path"]: item["maintained_canonical_sha256"]
            for item in self.manifest["artifact_integrity_inventory"]["artifacts"]
        }
        self.assertEqual(declared, PINNED_MATERIAL_DIGESTS)
        self.assertEqual(evaluator_module.EXPECTED_MAINTAINED_ARTIFACT_DIGESTS, PINNED_MATERIAL_DIGESTS)

    def test_07_all_67_material_pins_match_actual_canonical_text(self):
        for relative_path, expected in PINNED_MATERIAL_DIGESTS.items():
            with self.subTest(path=relative_path):
                self.assertEqual(
                    sha256_repository_file(ROOT, relative_path, mode="text"), expected
                )

    def test_08_material_lifecycle_contract_is_complete_and_non_authoritative(self):
        for entry in self.manifest["artifact_integrity_inventory"]["artifacts"]:
            with self.subTest(path=entry["relative_path"]):
                self.assertEqual(entry["status"], "present")
                self.assertTrue(entry["required"])
                self.assertIsNone(entry["deferred_reason"])
                self.assertTrue(entry["evidence_reference"])
                self.assertIn("grants no completion", entry["authority_boundary"])
                self.assertTrue(entry["notes"])
                self.assertFalse(entry["executable_by_evaluator"])

    def test_09_material_inventory_excludes_e1_readme_and_historical_evidence(self):
        paths = set(PINNED_MATERIAL_DIGESTS)
        self.assertNotIn("README.md", paths)
        self.assertFalse(any("operational-readiness" in path for path in paths))
        self.assertFalse(any("historical" in path for path in paths))

    def test_10_dependency_inventory_is_separate_5_control_17_path_evidence(self):
        inventory = self.manifest["maintained_control_dependency_inventory"]
        self.assertEqual(inventory["dependency_count"], 5)
        self.assertEqual(inventory["dependency_artifact_count"], 17)
        self.assertFalse(inventory["included_in_material_artifact_count"])
        self.assertEqual(inventory["maintained_main_commit_sha"], MAINTAINED_MAIN_SHA)
        self.assertEqual(len(inventory["dependencies"]), 5)
        self.assertEqual(
            sum(len(item["path_digests"]) for item in inventory["dependencies"]), 17
        )
        self.assertTrue(set(PINNED_DEPENDENCY_DIGESTS).isdisjoint(PINNED_MATERIAL_DIGESTS))

    def test_11_dependency_metadata_tracks_boundaries_and_tests_are_exact(self):
        matrix_document = load_json(MATRIX_PATH)
        matrix = {
            item["source_control_id"]: item
            for item in matrix_document["source_control_bindings"]
        }
        matrix_tracks = {}
        for item in matrix_document["controls"]:
            tracks = matrix_tracks.setdefault(item["source_control_id"], [])
            if item["source_track"] not in tracks:
                tracks.append(item["source_track"])
        declared = {
            item["source_control_id"]: item
            for item in self.manifest["maintained_control_dependency_inventory"]["dependencies"]
        }
        self.assertEqual(set(declared), set(PINNED_DEPENDENCY_METADATA))
        for control_id, pin in PINNED_DEPENDENCY_METADATA.items():
            row = declared[control_id]
            source = matrix[control_id]
            with self.subTest(control=control_id):
                self.assertEqual(row["dependency_id"], pin["dependency_id"])
                self.assertEqual(row["source_pr"], pin["source_pr"])
                self.assertEqual(row["source_schema_or_contract_version"], pin["version"])
                self.assertEqual(row["dependent_tracks"], pin["dependent_tracks"])
                self.assertEqual(row["dependent_tracks"], matrix_tracks[control_id])
                self.assertEqual(row["status"], "bound")
                self.assertEqual(row["maintained_integrity_reference"], "path-binding:maintained-main")
                self.assertEqual(row["boundary_statements"], source["required_boundary_statements"])
                self.assertEqual(_boundary_digest(row["boundary_statements"]), pin["boundary_digest"])
                self.assertEqual(row["covering_test_references"], [pin["adapter"]])
                self.assertEqual(source["adapter_test_reference"], pin["adapter"])
                self.assertIn("does not grant", row["authority_boundary"])

    def test_12_dependency_paths_and_digests_match_independent_pins_and_source_matrix(self):
        matrix_paths = {
            item["source_control_id"]: item["source_artifact_paths"]
            for item in load_json(MATRIX_PATH)["source_control_bindings"]
        }
        declared = {}
        for dependency in self.manifest["maintained_control_dependency_inventory"]["dependencies"]:
            paths = []
            for item in dependency["path_digests"]:
                paths.append(item["relative_path"])
                declared[item["relative_path"]] = item["maintained_canonical_sha256"]
                self.assertEqual(item["digest_algorithm"], "sha256")
                self.assertEqual(item["digest_mode"], "canonical-text")
            self.assertEqual(paths, matrix_paths[dependency["source_control_id"]])
        self.assertEqual(declared, PINNED_DEPENDENCY_DIGESTS)

    def test_13_all_17_dependency_pins_match_actual_canonical_text(self):
        for relative_path, expected in PINNED_DEPENDENCY_DIGESTS.items():
            with self.subTest(path=relative_path):
                self.assertEqual(
                    sha256_repository_file(ROOT, relative_path, mode="text"), expected
                )

    def test_14_verification_command_manifest_separates_commands_from_results(self):
        value = self.manifest["verification_command_manifest"]
        self.assertEqual(value["command_count"], 13)
        self.assertTrue(value["execution_results_recorded"])
        self.assertFalse(value["commands_executed_by_evaluator"])
        self.assertTrue(value["results_supplied_as_external_verification_evidence"])
        self.assertFalse(value["verification_results_are_completion_approval"])
        self.assertTrue(all(not item["executed_by_evaluator"] for item in value["commands"]))
        self.assertEqual(
            {item["command_id"] for item in value["commands"]},
            set(evaluator_module.EXPECTED_VERIFICATION_COMMANDS),
        )

    def test_15_verification_commands_have_exact_argv_scope_and_exit_contract(self):
        commands = {
            item["command_id"]: item
            for item in self.manifest["verification_command_manifest"]["commands"]
        }
        for command_id, expected in evaluator_module.EXPECTED_VERIFICATION_COMMANDS.items():
            with self.subTest(command=command_id):
                self.assertEqual(commands[command_id]["argv"], expected["argv"])
                self.assertEqual(commands[command_id]["test_scope"], expected["test_scope"])
                self.assertEqual(commands[command_id]["expected_exit_code"], 0)

    def test_16_verification_results_bind_all_13_commands_and_exact_counts(self):
        result_manifest = self.manifest["verification_result_manifest"]
        results = result_manifest["results"]
        self.assertEqual(result_manifest["result_count"], 13)
        self.assertTrue(result_manifest["results_supplied_as_external_verification_evidence"])
        self.assertFalse(result_manifest["executed_by_evaluator"])
        self.assertFalse(result_manifest["verification_results_are_completion_approval"])
        self.assertEqual(len({item["verification_id"] for item in results}), 13)
        self.assertEqual(
            {item["command_id"] for item in results},
            set(evaluator_module.EXPECTED_VERIFICATION_COMMANDS),
        )
        for item in results:
            with self.subTest(command=item["command_id"]):
                expected = evaluator_module.EXPECTED_VERIFICATION_RESULT_COUNTS[item["command_id"]]
                self.assertEqual(item["maintained_main_commit_sha"], MAINTAINED_MAIN_SHA)
                self.assertEqual(
                    item["evidence_source"],
                    "externally-supplied-maintained-repository-test-execution",
                )
                self.assertEqual(item["expected_test_count"], expected)
                self.assertEqual(item["observed_test_count"], expected)
                self.assertEqual(item["passes"], expected)
                self.assertEqual((item["failures"], item["errors"], item["skips"]), (0, 0, 0))
                self.assertEqual(item["exit_code"], 0)
                self.assertEqual(item["result"], "pass")
                self.assertTrue(item["evidence_reference"])
                self.assertFalse(item["executed_by_evaluator"])
                self.assertFalse(item["verification_results_are_completion_approval"])

    def test_17_governance_boundary_keeps_tracker_m15_and_release_open(self):
        boundary = self.manifest["governance_boundary"]
        self.assertEqual(boundary["tracker_231_state"], "open")
        self.assertEqual(boundary["m15_state"], "active-and-incomplete")
        self.assertEqual(boundary["v0_14_0_state"], "unpublished")
        for field, value in boundary.items():
            if field not in {"tracker_231_state", "m15_state", "v0_14_0_state"}:
                self.assertIs(value, False, field)

    def test_18_outcome_vocabulary_and_non_authoritative_boundary_are_exact(self):
        self.assertEqual(self.manifest["allowed_outcomes"], list(OUTCOMES))
        self.assertEqual(self.manifest["declared_outcome"], READY_FOR_COMPLETION_REVIEW)
        self.assertEqual(
            self.manifest["non_authoritative_boundary_statement"],
            NON_AUTHORITATIVE_BOUNDARY_STATEMENT,
        )

    def test_19_contract_preserves_scope_and_authority_boundaries(self):
        text = CONTRACT_PATH.read_text(encoding="utf-8")
        self.assertIn(NON_AUTHORITATIVE_BOUNDARY_STATEMENT, text)
        self.assertIn(SYNTHETIC_SCENARIO_BOUNDARY_STATEMENT, text)
        self.assertIn("does not implement Track E2, E3, or E4", text)
        self.assertIn("M15 remains active and incomplete", text)
        self.assertIn("`v0.14.0` remains unpublished", text)

    def test_20_exactly_27_standalone_scenarios_are_present(self):
        self.assertEqual(len(SCENARIO_PATHS), 27)
        documents = [load_json(path) for path in SCENARIO_PATHS]
        self.assertEqual(
            [document["scenario_id"] for document in documents],
            [f"m15-e1-{number:02d}" for number in range(1, 28)],
        )
        self.assertEqual(
            {document["scenario_id"]: document["title"] for document in documents},
            evaluator_module.EXPECTED_SCENARIO_TITLES,
        )
        self.assertEqual(
            {document["notes"] for document in documents},
            {SYNTHETIC_SCENARIO_BOUNDARY_STATEMENT},
        )

    def test_21_manifest_observation_and_valid_scenarios_validate_against_schema(self):
        self.assertEqual(validate_draft_2020_12_subset(self.manifest, self.schema), [])
        self.assertEqual(validate_draft_2020_12_subset(self.observation, self.schema), [])
        for number in (*range(1, 18), *range(19, 28)):
            with self.subTest(number=number):
                self.assertEqual(
                    validate_draft_2020_12_subset(scenario(number), self.schema), []
                )

    def test_22_scenario_18_is_deliberately_schema_invalid(self):
        self.assertTrue(validate_draft_2020_12_subset(scenario(18), self.schema))

    def test_23_schema_subset_enforces_type_lists_null_and_max_length(self):
        self.assertEqual(validate_draft_2020_12_subset(None, {"type": ["string", "null"]}), [])
        self.assertEqual(validate_draft_2020_12_subset("ok", {"type": ["string", "null"]}), [])
        self.assertTrue(validate_draft_2020_12_subset(1, {"type": ["string", "null"]}))
        self.assertTrue(validate_draft_2020_12_subset("too-long", {"type": "string", "maxLength": 3}))

    def test_24_schema_prefix_items_and_unique_items_are_enforced(self):
        extra = copy.deepcopy(self.manifest)
        extra["allowed_outcomes"].append("unexpected")
        reordered = copy.deepcopy(self.manifest)
        reordered["allowed_outcomes"][0:2] = reversed(reordered["allowed_outcomes"][0:2])
        duplicate = copy.deepcopy(self.manifest)
        duplicate["known_repository_local_completion_blockers"] = ["same", "same"]
        self.assertTrue(validate_draft_2020_12_subset(extra, self.schema))
        self.assertTrue(validate_draft_2020_12_subset(reordered, self.schema))
        self.assertTrue(validate_draft_2020_12_subset(duplicate, self.schema))


class M15OperationalReadinessMaintainedEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_manifest()
        self.observation = build_repository_observation(self.manifest)

    def evaluate(self, manifest=None, observation=None):
        return evaluate_operational_readiness(
            self.manifest if manifest is None else manifest,
            self.observation if observation is None else observation,
        )

    def assert_blocked(self, result, prefix=None):
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertFalse(result["ready_for_completion_review"])
        if prefix:
            self.assertTrue(
                any(item.startswith(prefix) for item in result["blocking_findings"]),
                result,
            )

    def assert_not_ready(self, result, prefix=None):
        self.assertEqual(result["outcome"], NOT_READY)
        self.assertFalse(result["ready_for_completion_review"])
        if prefix:
            self.assertTrue(
                any(item.startswith(prefix) for item in result["readiness_findings"]),
                result,
            )

    def test_01_clean_caller_supplied_evidence_is_ready_for_completion_review(self):
        result = self.evaluate()
        self.assertEqual(result["outcome"], READY_FOR_COMPLETION_REVIEW)
        self.assertTrue(result["ready_for_completion_review"])
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["evaluated_artifact_count"], 67)
        self.assertEqual(result["evaluated_artifact_observation_count"], 67)
        self.assertEqual(result["evaluated_maintained_control_dependency_count"], 5)
        self.assertEqual(result["evaluated_dependency_observation_count"], 17)
        self.assertEqual(result["evaluated_verification_command_count"], 13)
        self.assertEqual(result["evaluated_verification_result_count"], 13)

    def test_02_evaluation_does_not_mutate_caller_data(self):
        manifest = copy.deepcopy(self.manifest)
        observation = copy.deepcopy(self.observation)
        before = (copy.deepcopy(manifest), copy.deepcopy(observation))
        self.evaluate(manifest, observation)
        self.assertEqual((manifest, observation), before)

    def test_03_evaluation_is_deterministic_and_findings_are_sorted_unique(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["maintained_main_commit_sha"] = "0" * 40
        manifest["governance_boundary"]["tag_created"] = True
        first = self.evaluate(manifest)
        second = self.evaluate(manifest)
        self.assertEqual(first, second)
        self.assertEqual(first["findings"], sorted(set(first["findings"])))

    def test_04_manifest_main_binding_mismatch_blocks(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["maintained_main_commit_sha"] = "0" * 40
        self.assert_blocked(self.evaluate(manifest), "maintained_main_sha_mismatch")

    def test_05_observation_main_binding_mismatch_blocks(self):
        observation = copy.deepcopy(self.observation)
        observation["maintained_main_commit_sha"] = "0" * 40
        self.assert_blocked(
            self.evaluate(observation=observation),
            "repository_observation_main_sha_mismatch",
        )

    def test_06_source_track_binding_substitutions_block(self):
        for field, value in (
            ("implementation_pr", "#999"),
            ("head_sha", "0" * 40),
            ("merge_sha", "0" * 40),
        ):
            manifest = copy.deepcopy(self.manifest)
            manifest["source_track_bindings"][0][field] = value
            with self.subTest(field=field):
                self.assert_blocked(self.evaluate(manifest), "source_track_binding_mismatch:track-a")

    def test_07_missing_or_duplicate_material_declarations_block(self):
        missing = copy.deepcopy(self.manifest)
        missing["artifact_integrity_inventory"]["artifacts"].pop()
        duplicate = copy.deepcopy(self.manifest)
        duplicate["artifact_integrity_inventory"]["artifacts"][-1] = copy.deepcopy(
            duplicate["artifact_integrity_inventory"]["artifacts"][0]
        )
        self.assert_blocked(self.evaluate(missing), "artifact_entry_missing:")
        self.assert_blocked(self.evaluate(duplicate), "duplicate_artifact:")

    def test_08_declared_material_digest_drift_blocks(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["artifact_integrity_inventory"]["artifacts"][0]["maintained_canonical_sha256"] = "0" * 64
        self.assert_blocked(self.evaluate(manifest), "artifact_declared_digest_mismatch:")

    def test_09_declared_and_observed_material_codrift_still_blocks(self):
        manifest = copy.deepcopy(self.manifest)
        observation = copy.deepcopy(self.observation)
        path = manifest["artifact_integrity_inventory"]["artifacts"][0]["relative_path"]
        manifest["artifact_integrity_inventory"]["artifacts"][0]["maintained_canonical_sha256"] = "0" * 64
        observed = next(item for item in observation["artifact_observations"] if item["relative_path"] == path)
        observed["observed_canonical_sha256"] = "0" * 64
        self.assert_blocked(self.evaluate(manifest, observation), "artifact_declared_digest_mismatch:")

    def test_10_missing_or_duplicate_material_observations_block(self):
        missing = copy.deepcopy(self.observation)
        missing["artifact_observations"].pop()
        duplicate = copy.deepcopy(self.observation)
        duplicate["artifact_observations"][-1] = copy.deepcopy(duplicate["artifact_observations"][0])
        self.assert_blocked(self.evaluate(observation=missing), "artifact_observation_missing:")
        self.assert_blocked(self.evaluate(observation=duplicate), "artifact_observation_duplicate:")

    def test_11_required_material_missing_digest_mismatch_or_not_applicable_blocks(self):
        for status in ("missing", "digest_mismatch", "not_applicable"):
            observation = copy.deepcopy(self.observation)
            item = observation["artifact_observations"][0]
            item["status"] = status
            if status != "digest_mismatch":
                item["observed_canonical_sha256"] = None
            with self.subTest(status=status):
                self.assert_blocked(self.evaluate(observation=observation))

    def test_12_required_material_unverified_is_not_ready(self):
        observation = copy.deepcopy(self.observation)
        item = observation["artifact_observations"][0]
        item["status"] = "unverified"
        item["observed_canonical_sha256"] = None
        self.assert_not_ready(
            self.evaluate(observation=observation),
            "artifact_observation_status_not_ready:",
        )

    def test_13_deferred_material_with_reason_is_not_ready(self):
        observation = copy.deepcopy(self.observation)
        item = observation["artifact_observations"][0]
        item["status"] = "deferred"
        item["observed_canonical_sha256"] = None
        item["deferred_reason"] = "Synthetic maintenance deferral."
        self.assert_not_ready(
            self.evaluate(observation=observation),
            "artifact_observation_status_not_ready:",
        )

    def test_14_deferred_material_without_reason_fails_closed(self):
        observation = copy.deepcopy(self.observation)
        item = observation["artifact_observations"][0]
        item["status"] = "deferred"
        item["observed_canonical_sha256"] = None
        item["deferred_reason"] = None
        self.assert_blocked(
            self.evaluate(observation=observation),
            "artifact_observation_deferred_reason_missing:",
        )

    def test_15_superseded_required_material_is_not_ready(self):
        observation = copy.deepcopy(self.observation)
        item = observation["artifact_observations"][0]
        item["status"] = "superseded"
        item["observed_canonical_sha256"] = None
        self.assert_not_ready(
            self.evaluate(observation=observation),
            "artifact_observation_status_not_ready:",
        )

    def test_15b_declared_material_lifecycle_states_follow_the_same_fail_closed_rules(self):
        cases = {
            "missing": BLOCKED,
            "digest_mismatch": BLOCKED,
            "not_applicable": BLOCKED,
            "unverified": NOT_READY,
            "superseded": NOT_READY,
            "deferred": NOT_READY,
        }
        for status, outcome in cases.items():
            manifest = copy.deepcopy(self.manifest)
            item = manifest["artifact_integrity_inventory"]["artifacts"][0]
            item["status"] = status
            item["deferred_reason"] = (
                "Synthetic maintained deferral evidence."
                if status == "deferred"
                else None
            )
            with self.subTest(status=status):
                self.assertEqual(self.evaluate(manifest)["outcome"], outcome)

        no_reason = copy.deepcopy(self.manifest)
        no_reason_item = no_reason["artifact_integrity_inventory"]["artifacts"][0]
        no_reason_item["status"] = "deferred"
        no_reason_item["deferred_reason"] = None
        self.assert_blocked(
            self.evaluate(no_reason), "artifact_declared_deferred_reason_missing:"
        )

    def test_16_changed_test_module_is_not_ready(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["artifact_integrity_inventory"]["artifacts"][0]["test_module"] = "tests.test_m15_cross_control_regression_evaluator"
        self.assert_not_ready(self.evaluate(manifest), "test_coverage_incomplete:")

    def test_17_missing_or_changed_verification_command_is_not_ready(self):
        missing = copy.deepcopy(self.manifest)
        missing["verification_command_manifest"]["commands"].pop()
        changed = copy.deepcopy(self.manifest)
        changed["verification_command_manifest"]["commands"][0]["argv"].append("unexpected")
        self.assert_not_ready(self.evaluate(missing), "verification_command_missing:")
        self.assert_not_ready(self.evaluate(changed), "verification_command_invalid:")

    def test_18_verification_command_execution_claim_blocks(self):
        for mutate in (
            lambda value: value["verification_command_manifest"].__setitem__("commands_executed_by_evaluator", True),
            lambda value: value["verification_command_manifest"]["commands"][0].__setitem__("executed_by_evaluator", True),
        ):
            manifest = copy.deepcopy(self.manifest)
            mutate(manifest)
            with self.subTest(manifest=manifest["verification_command_manifest"]):
                self.assert_blocked(self.evaluate(manifest))

    def test_19_missing_verification_result_is_not_ready(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["verification_result_manifest"]["results"].pop()
        self.assert_not_ready(self.evaluate(manifest), "verification_result_missing:")

    def test_20_verification_result_main_binding_missing_or_mismatch_blocks(self):
        for replacement in (None, "0" * 40):
            manifest = copy.deepcopy(self.manifest)
            result = manifest["verification_result_manifest"]["results"][0]
            if replacement is None:
                result.pop("maintained_main_commit_sha")
            else:
                result["maintained_main_commit_sha"] = replacement
            with self.subTest(replacement=replacement):
                self.assert_blocked(self.evaluate(manifest))

    def test_21_verification_result_count_inconsistencies_block(self):
        fields = ("expected_test_count", "observed_test_count", "passes")
        for field in fields:
            manifest = copy.deepcopy(self.manifest)
            manifest["verification_result_manifest"]["results"][0][field] += 1
            with self.subTest(field=field):
                self.assert_blocked(self.evaluate(manifest))

    def test_22_verification_failure_blocks(self):
        manifest = copy.deepcopy(self.manifest)
        result = manifest["verification_result_manifest"]["results"][0]
        result["passes"] -= 1
        result["failures"] = 1
        result["exit_code"] = 1
        result["result"] = "fail"
        self.assert_blocked(
            self.evaluate(manifest), "verification_result_failures_present:"
        )

    def test_23_verification_error_blocks(self):
        manifest = copy.deepcopy(self.manifest)
        result = manifest["verification_result_manifest"]["results"][0]
        result["passes"] -= 1
        result["errors"] = 1
        result["exit_code"] = 1
        result["result"] = "fail"
        self.assert_blocked(
            self.evaluate(manifest), "verification_result_errors_present:"
        )

    def test_24_unexpected_verification_skip_is_not_ready(self):
        manifest = copy.deepcopy(self.manifest)
        result = manifest["verification_result_manifest"]["results"][0]
        result["passes"] -= 1
        result["skips"] = 1
        self.assert_not_ready(self.evaluate(manifest), "verification_result_skips_present:")

    def test_25_verification_exit_result_or_arithmetic_inconsistency_blocks(self):
        cases = (("exit_code", 1), ("result", "fail"), ("failures", 1))
        for field, value in cases:
            manifest = copy.deepcopy(self.manifest)
            manifest["verification_result_manifest"]["results"][0][field] = value
            with self.subTest(field=field):
                self.assert_blocked(self.evaluate(manifest))

    def test_26_result_execution_or_completion_approval_claim_blocks(self):
        for field in ("executed_by_evaluator", "verification_results_are_completion_approval"):
            manifest = copy.deepcopy(self.manifest)
            manifest["verification_result_manifest"]["results"][0][field] = True
            with self.subTest(field=field):
                self.assert_blocked(self.evaluate(manifest))

    def test_27_missing_or_duplicate_dependency_declaration_blocks(self):
        missing = copy.deepcopy(self.manifest)
        missing["maintained_control_dependency_inventory"]["dependencies"].pop()
        duplicate = copy.deepcopy(self.manifest)
        duplicate["maintained_control_dependency_inventory"]["dependencies"][-1] = copy.deepcopy(
            duplicate["maintained_control_dependency_inventory"]["dependencies"][0]
        )
        self.assert_blocked(self.evaluate(missing))
        self.assert_blocked(self.evaluate(duplicate))

    def test_28_dependency_declared_digest_drift_blocks(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["maintained_control_dependency_inventory"]["dependencies"][0]["path_digests"][0]["maintained_canonical_sha256"] = "0" * 64
        self.assert_blocked(
            self.evaluate(manifest),
            "maintained_control_dependency_digest_mismatch:",
        )

    def test_29_dependency_declared_and_observed_codrift_still_blocks(self):
        manifest = copy.deepcopy(self.manifest)
        observation = copy.deepcopy(self.observation)
        path_item = manifest["maintained_control_dependency_inventory"]["dependencies"][0]["path_digests"][0]
        path_item["maintained_canonical_sha256"] = "0" * 64
        observed = next(item for item in observation["dependency_observations"] if item["relative_path"] == path_item["relative_path"])
        observed["observed_canonical_sha256"] = "0" * 64
        self.assert_blocked(
            self.evaluate(manifest, observation),
            "maintained_control_dependency_digest_mismatch:",
        )

    def test_30_missing_or_drifted_dependency_observation_blocks(self):
        missing = copy.deepcopy(self.observation)
        missing["dependency_observations"].pop()
        drifted = copy.deepcopy(self.observation)
        drifted["dependency_observations"][0]["status"] = "digest_mismatch"
        drifted["dependency_observations"][0]["observed_canonical_sha256"] = "0" * 64
        self.assert_blocked(self.evaluate(observation=missing))
        self.assert_blocked(self.evaluate(observation=drifted))

    def test_31_dependency_metadata_or_dependent_track_drift_blocks(self):
        for field, value in (
            ("source_pr", "#999"),
            ("source_schema_or_contract_version", "drifted"),
            ("dependent_tracks", ["track-c"]),
            ("status", "missing"),
        ):
            manifest = copy.deepcopy(self.manifest)
            manifest["maintained_control_dependency_inventory"]["dependencies"][0][field] = value
            with self.subTest(field=field):
                self.assert_blocked(self.evaluate(manifest))

    def test_32_malformed_or_missing_observation_blocks(self):
        extra = copy.deepcopy(self.observation)
        extra["unexpected"] = True
        missing = copy.deepcopy(self.observation)
        missing.pop("artifact_observations")
        self.assert_blocked(
            self.evaluate(observation=extra), "repository_observation_shape_invalid"
        )
        self.assert_blocked(
            self.evaluate(observation=missing), "repository_observation_shape_invalid"
        )
        self.assert_blocked(evaluate_operational_readiness(self.manifest, None))

    def test_33_every_governance_escalation_blocks(self):
        state_fields = {
            "tracker_231_state": "closed",
            "m15_state": "complete",
            "v0_14_0_state": "published",
        }
        for field in self.manifest["governance_boundary"]:
            manifest = copy.deepcopy(self.manifest)
            manifest["governance_boundary"][field] = state_fields.get(field, True)
            with self.subTest(field=field):
                self.assert_blocked(self.evaluate(manifest))

    def test_34_known_repository_local_blocker_blocks(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["known_repository_local_completion_blockers"] = ["synthetic-local-blocker"]
        self.assert_blocked(self.evaluate(manifest), "unresolved_completion_blocker:")

    def test_35_declared_not_ready_cannot_be_promoted(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["declared_outcome"] = NOT_READY
        self.assert_not_ready(self.evaluate(manifest), "declared_outcome_not_ready_for_review")

    def test_36_historical_digest_policy_drift_blocks(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["artifact_integrity_inventory"]["historical_digest_evidence_policy"] = "reinterpreted"
        self.assert_blocked(self.evaluate(manifest), "historical_digest_evidence_policy_invalid")


class M15OperationalReadinessScenarioTests(unittest.TestCase):
    EXPECTED = {
        1: READY_FOR_COMPLETION_REVIEW,
        2: BLOCKED,
        3: BLOCKED,
        4: BLOCKED,
        5: BLOCKED,
        6: BLOCKED,
        7: BLOCKED,
        8: NOT_READY,
        9: NOT_READY,
        10: BLOCKED,
        11: BLOCKED,
        12: BLOCKED,
        13: BLOCKED,
        14: BLOCKED,
        15: BLOCKED,
        16: BLOCKED,
        17: BLOCKED,
        18: BLOCKED,
        19: BLOCKED,
        20: BLOCKED,
        21: NOT_READY,
        22: NOT_READY,
        23: BLOCKED,
        24: BLOCKED,
        25: NOT_READY,
        26: BLOCKED,
        27: BLOCKED,
    }

    def assert_scenario(self, number):
        document = scenario(number)
        before = copy.deepcopy(document)
        first = evaluate_synthetic_scenario(document)
        second = evaluate_synthetic_scenario(document)
        expected = self.EXPECTED[number]
        self.assertEqual(first, second)
        self.assertEqual(document, before)
        self.assertEqual(document["expected_outcome"], expected)
        self.assertEqual(first["outcome"], expected)
        self.assertIn(first["outcome"], OUTCOMES)

    def test_01_valid_maintained_main(self): self.assert_scenario(1)
    def test_02_main_binding_mismatch(self): self.assert_scenario(2)
    def test_03_source_track_binding_mismatch(self): self.assert_scenario(3)
    def test_04_incomplete_artifact_inventory(self): self.assert_scenario(4)
    def test_05_artifact_integrity_failure(self): self.assert_scenario(5)
    def test_06_internal_consistency_failure(self): self.assert_scenario(6)
    def test_07_cross_control_matrix_unbound(self): self.assert_scenario(7)
    def test_08_incomplete_test_coverage(self): self.assert_scenario(8)
    def test_09_incomplete_command_manifest(self): self.assert_scenario(9)
    def test_10_command_execution_claim(self): self.assert_scenario(10)
    def test_11_completion_approval_claim(self): self.assert_scenario(11)
    def test_12_tracker_closure_claim(self): self.assert_scenario(12)
    def test_13_m15_completion_claim(self): self.assert_scenario(13)
    def test_14_readme_authorization_claim(self): self.assert_scenario(14)
    def test_15_tag_authority_claim(self): self.assert_scenario(15)
    def test_16_release_authority_claim(self): self.assert_scenario(16)
    def test_17_known_local_blocker(self): self.assert_scenario(17)
    def test_18_malformed_schema_version(self): self.assert_scenario(18)
    def test_19_failed_targeted_test(self): self.assert_scenario(19)
    def test_20_verification_error(self): self.assert_scenario(20)
    def test_21_unexpected_skip(self): self.assert_scenario(21)
    def test_22_missing_result(self): self.assert_scenario(22)
    def test_23_observed_count_mismatch(self): self.assert_scenario(23)
    def test_24_missing_result_main_binding(self): self.assert_scenario(24)
    def test_25_required_artifact_unverified(self): self.assert_scenario(25)
    def test_26_deferred_without_reason(self): self.assert_scenario(26)
    def test_27_track_d_dependency_drift(self): self.assert_scenario(27)

    def test_28_expected_outcome_is_not_trusted_for_classification(self):
        document = scenario(1)
        document["expected_outcome"] = BLOCKED
        self.assertEqual(
            evaluate_synthetic_scenario(document)["outcome"],
            READY_FOR_COMPLETION_REVIEW,
        )

    def test_29_blocked_takes_precedence_over_not_ready(self):
        document = scenario(1)
        document["evidence_state"]["test_coverage_complete"] = False
        document["evidence_state"]["completion_approval_claimed"] = True
        result = evaluate_synthetic_scenario(document)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertTrue(result["readiness_findings"])
        self.assertTrue(result["blocking_findings"])

    def test_30_non_boolean_or_unknown_state_fails_closed_without_echoing_values(self):
        non_boolean = scenario(1)
        non_boolean["evidence_state"]["manifest_shape_valid"] = 1
        unknown = scenario(1)
        unknown["hostile-secret-field"] = "do-not-echo"
        self.assertEqual(evaluate_synthetic_scenario(non_boolean)["outcome"], BLOCKED)
        result = evaluate_synthetic_scenario(unknown)
        self.assertEqual(result["outcome"], BLOCKED)
        self.assertNotIn("do-not-echo", json.dumps(result))

    def test_31_scenario_text_is_closed_and_non_authoritative(self):
        for field, value in (
            ("notes", "Synthetic inert evidence only."),
            ("title", "M15 complete and v0.14.0 published"),
        ):
            document = scenario(1)
            document[field] = value
            with self.subTest(field=field):
                self.assertEqual(evaluate_synthetic_scenario(document)["outcome"], BLOCKED)


class M15OperationalReadinessSafetyTests(unittest.TestCase):
    def test_01_canonical_text_hash_normalizes_only_crlf(self):
        self.assertEqual(
            canonicalize_utf8_repository_text(b"alpha\r\nbeta\r\n"),
            b"alpha\nbeta\n",
        )
        self.assertEqual(
            hashlib.sha256(canonicalize_utf8_repository_text(b"alpha\r\nbeta\r\n")).hexdigest(),
            hashlib.sha256(b"alpha\nbeta\n").hexdigest(),
        )

    def test_02_canonical_text_rejects_lone_carriage_return(self):
        with self.assertRaises(RepositoryArtifactTextError):
            canonicalize_utf8_repository_text(b"alpha\rbeta")

    def test_03_canonical_text_preserves_newline_spaces_and_bom(self):
        self.assertNotEqual(
            canonicalize_utf8_repository_text(b"alpha"),
            canonicalize_utf8_repository_text(b"alpha\n"),
        )
        self.assertEqual(canonicalize_utf8_repository_text(b"alpha  \n"), b"alpha  \n")
        self.assertEqual(
            canonicalize_utf8_repository_text(b"\xef\xbb\xbfalpha\n"),
            b"\xef\xbb\xbfalpha\n",
        )

    def test_04_repository_hash_is_checkout_line_ending_independent(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "crlf.txt").write_bytes(b"alpha\r\nbeta\r\n")
            (root / "lf.txt").write_bytes(b"alpha\nbeta\n")
            self.assertEqual(
                sha256_repository_file(root, "crlf.txt", mode="text"),
                sha256_repository_file(root, "lf.txt", mode="text"),
            )

    def test_05_evaluator_is_caller_data_only_by_signature_and_exports(self):
        signature = inspect.signature(evaluate_operational_readiness)
        self.assertEqual(list(signature.parameters), ["manifest", "observation"])
        self.assertNotIn("evaluate_repository_operational_readiness", evaluator_module.__dict__)
        self.assertNotIn("load_manifest", evaluator_module.__dict__)
        self.assertNotIn("REPOSITORY_ROOT", evaluator_module.__dict__)

    def test_06_evaluator_imports_no_filesystem_hash_execution_or_network_modules(self):
        tree = ast.parse(EVALUATOR_PATH.read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        banned = {
            "hashlib",
            "json",
            "os",
            "pathlib",
            "subprocess",
            "socket",
            "requests",
            "urllib",
            "http",
            "runpy",
            "importlib",
            "runtime.repository_artifact_digest",
        }
        self.assertFalse(imported & banned, imported & banned)

    def test_07_evaluator_has_no_file_hash_command_git_or_network_calls(self):
        tree = ast.parse(EVALUATOR_PATH.read_text(encoding="utf-8"))
        banned_names = {
            "open",
            "Path",
            "sha256_repository_file",
            "canonicalize_utf8_repository_text",
            "load_manifest",
            "evaluate_repository_operational_readiness",
            "system",
            "popen",
            "run",
            "call",
            "check_call",
            "check_output",
            "urlopen",
        }
        banned_attributes = {
            "read_text",
            "read_bytes",
            "write_text",
            "write_bytes",
            "open",
            "glob",
            "rglob",
            "iterdir",
            "exists",
            "is_file",
            "is_dir",
            "stat",
            "resolve",
            "unlink",
            "rename",
            "replace",
            "mkdir",
            "rmdir",
            "system",
            "popen",
            "run",
            "call",
            "check_call",
            "check_output",
            "urlopen",
            "request",
        }
        names = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        attributes = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        self.assertFalse(names & banned_names, names & banned_names)
        self.assertFalse(attributes & banned_attributes, attributes & banned_attributes)
        identifiers = {
            node.id.lower() for node in ast.walk(tree) if isinstance(node, ast.Name)
        }
        self.assertFalse({"git", "github", "gh"} & identifiers)

    def test_08_evaluator_does_not_import_track_a_through_d_evaluators(self):
        source = EVALUATOR_PATH.read_text(encoding="utf-8")
        for module_name in (
            "m15_learning_proof_evaluator",
            "m15_capability_memory_pack_evaluator",
            "m15_lineage_rollback_portability_evaluator",
            "m15_cross_control_regression_evaluator",
        ):
            self.assertNotIn(f"import {module_name}", source)

    def test_09_result_has_one_closed_outcome_and_no_status_alias(self):
        result = evaluate_operational_readiness(load_manifest(), build_repository_observation())
        self.assertEqual([key for key in result if key == "outcome"], ["outcome"])
        self.assertIn(result["outcome"], OUTCOMES)
        self.assertNotIn("status", result)

    def test_10_all_fixture_findings_are_sorted_and_deduplicated(self):
        for path in SCENARIO_PATHS:
            with self.subTest(path=path.name):
                result = evaluate_synthetic_scenario(load_json(path))
                self.assertEqual(result["findings"], sorted(set(result["findings"])))

    def test_11_ready_for_review_never_grants_completion_or_release_authority(self):
        result = evaluate_operational_readiness(load_manifest(), build_repository_observation())
        self.assertEqual(result["outcome"], READY_FOR_COMPLETION_REVIEW)
        self.assertEqual(
            result["non_authoritative_boundary_statement"],
            NON_AUTHORITATIVE_BOUNDARY_STATEMENT,
        )
        self.assertIn("not M15 completion approval", result["non_authoritative_boundary_statement"])


if __name__ == "__main__":
    unittest.main()
