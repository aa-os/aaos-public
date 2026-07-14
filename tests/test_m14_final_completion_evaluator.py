import ast
import hashlib
import json
import shutil
import tempfile
import unittest
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from unittest import mock

from runtime.m14_final_completion_evaluator import (
    evaluate_file,
    evaluate_m14_final_completion,
    load_fixture,
    validate_m14_final_completion,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m14-final-completion-release-state.json"
)
READINESS_FIXTURE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m14-completion-readiness-future-readme-path.json"
)
README_PATH = ROOT / "README.md"
EVALUATOR_PATH = ROOT / "runtime" / "m14_final_completion_evaluator.py"

EXPECTED_CHANGED_FILES = [
    "README.md",
    "examples/public-integration-pack-pilot/m14-final-completion-release-state.json",
    "runtime/m14_final_completion_evaluator.py",
    "tests/test_m14_final_completion_evaluator.py",
]
EXPECTED_SOURCE_PRS = [
    "#202",
    "#204",
    "#205",
    "#206",
    "#208",
    "#210",
    "#212",
    "#213",
    "#214",
]
EXPECTED_BUNDLE = [
    {
        "source_pr": "#214",
        "relative_path": "examples/public-integration-pack-pilot/m14-completion-readiness-future-readme-path.json",
        "artifact_type": "fixture",
        "required": True,
        "sha256": "e65e4558bc25504ebea24dd8479ac5c40e1ecc588cd3262e729fe77b193d2673",
        "digest_algorithm": "sha256",
        "observed_on_branch": "main",
        "evidence_role": "completion_readiness_fixture_data",
        "executable_by_final_completion_evaluator": False,
    },
    {
        "source_pr": "#214",
        "relative_path": "runtime/m14_completion_readiness_evaluator.py",
        "artifact_type": "runtime_evaluator",
        "required": True,
        "sha256": "c3e1a9b36b94750f4ec6fe00c2fda7def4c033eb2a7100100fc31a4378deb956",
        "digest_algorithm": "sha256",
        "observed_on_branch": "main",
        "evidence_role": "completion_readiness_evaluator_source",
        "executable_by_final_completion_evaluator": False,
    },
    {
        "source_pr": "#214",
        "relative_path": "tests/test_m14_completion_readiness_evaluator.py",
        "artifact_type": "deterministic_test",
        "required": True,
        "sha256": "7aec68924201a6facb5d9248c065346e774b49cf6377161d8c2c0931df30c7ed",
        "digest_algorithm": "sha256",
        "observed_on_branch": "main",
        "evidence_role": "completion_readiness_test_source",
        "executable_by_final_completion_evaluator": False,
    },
]
EXPECTED_MAINTAINED_BUNDLE_SHA256 = {
    (
        "examples/public-integration-pack-pilot/"
        "m14-completion-readiness-future-readme-path.json"
    ): "e65e4558bc25504ebea24dd8479ac5c40e1ecc588cd3262e729fe77b193d2673",
    "runtime/m14_completion_readiness_evaluator.py": (
        "c3e1a9b36b94750f4ec6fe00c2fda7def4c033eb2a7100100fc31a4378deb956"
    ),
    "tests/test_m14_completion_readiness_evaluator.py": (
        "9333843bdd89df5b5a4f6cc1889eba7d2a9ca48e636b8bdebda80ab9bad8f9b9"
    ),
}
EXPECTED_MANUAL_STEPS = [
    "verify final PR merged into main",
    "verify tracker #201 is closed as completed",
    "verify README lists v0.13.0 and M14 complete",
    "create GitHub Release v0.13.0 manually",
    "use the merge commit on main as the release target",
    "publish release notes describing M14 outputs",
    "verify v0.13.0 appears as Latest",
]
EXPECTED_M14_OUTPUTS = [
    "High-Risk Runtime Policy Gates and Public-Output Safety",
    "Governed Voice Runtime Policy Fixtures",
    "Public Issue Exfiltration Gate",
    "MODA AI Risk Framework Mapping",
    "AI-Authored PR Provenance and Reviewer Routing",
    "External Skill Admission Gate",
    "Cross-Control Authority-Boundary Regression Fixtures",
    "M14 Operational Readiness Checklist",
    "M14 Release Proof Linkage Specimen",
    "M14 Completion Readiness and README release-state path",
    "deterministic M14 evaluator coverage",
]
EXPECTED_M14_COMPLETED_REFS = [
    "#201 M14 tracker issue",
    "#202 Governed Voice Runtime Policy Fixtures",
    "#204 Public Issue Exfiltration Gate",
    "#205 MODA AI Risk Framework Mapping",
    "#206 AI-Authored PR Provenance and Reviewer Routing",
    "#208 External Skill Admission Gate",
    "#210 Cross-Control Authority-Boundary Regression Fixtures",
    "#212 Operational Readiness Checklist",
    "#213 Release Proof Linkage Specimen",
    "#214 Completion Readiness and Future README Path",
    "this final completion PR",
]
EXPECTED_ALLOWED_OUTPUTS = {
    "m14_final_completion_valid",
    "m14_final_completion_invalid",
    "m14_completion_declared",
    "final_m14_completion_review_recorded",
    "issue_201_closes_on_merge",
    "repository_release_state_prepared",
    "github_release_pending_manual_publication",
    "review_required",
    "escalation_required",
}
EXPECTED_FORBIDDEN_OUTPUTS = {
    "github_release_created",
    "release_published_by_evaluator",
    "release_tag_created_by_evaluator",
    "tracker_closed_by_evaluator",
    "decision_proof_sealed_by_evaluator",
    "sealed_by_runtime_gate",
    "sealed_by_public_output_gate",
    "authority_transferred",
    "risk_accepted_by_evaluator",
    "rollback_executed_by_evaluator",
    "fail_closed_executed_by_evaluator",
    "audit_closed_by_evaluator",
    "waiver_granted_by_evaluator",
    "final_governance_judgment_by_evaluator",
    "release_authority_granted_by_evaluator",
}
EXPECTED_PRE_TRANSITION = {
    "fixture_status": "m14_active_work_not_complete",
    "tracker_issue": "#201",
    "tracker_expected_state": "open",
    "target_future_release": "v0.13.0",
    "release_proof_complete": True,
    "completion_ready_for_review": True,
    "ready_for_final_m14_completion_review": True,
    "final_m14_completion_review_completed": False,
    "readme_future_path_present": True,
    "release_approved": False,
    "released": False,
    "m14_complete": False,
    "release_tag_created": False,
    "github_release_created": False,
    "decision_proof_sealed_by_fixture": False,
}


def load_json(path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def canonical_sha256(path):
    data = Path(path).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


class M14FinalCompletionEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_json(FIXTURE_PATH)
        cls.readme = README_PATH.read_text(encoding="utf-8")
        cls.evaluator_source = EVALUATOR_PATH.read_text(encoding="utf-8")

    def setUp(self):
        self.fixture = deepcopy(self.baseline)

    def evaluate(self, payload=None, repository_root=ROOT):
        return evaluate_m14_final_completion(
            self.fixture if payload is None else payload,
            repository_root,
        )

    @contextmanager
    def temporary_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative_path in [
                "README.md",
                *(entry["relative_path"] for entry in EXPECTED_BUNDLE),
            ]:
                source = ROOT / relative_path
                target = root / relative_path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
            yield root

    def evaluate_readme_mutation(self, old, new):
        with self.temporary_repository() as root:
            path = root / "README.md"
            text = path.read_text(encoding="utf-8")
            self.assertIn(old, text)
            path.write_text(text.replace(old, new, 1), encoding="utf-8")
            return self.evaluate(repository_root=root)

    def evaluate_readiness_mutation(self, field, value):
        with self.temporary_repository() as root:
            path = root / EXPECTED_BUNDLE[0]["relative_path"]
            payload = load_json(path)
            payload[field] = value
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            return self.evaluate(repository_root=root)

    def assert_authority_claim_fails(self, key, value):
        payload = deepcopy(self.fixture)
        payload["artifact_links"]["nested_evaluator_claim"] = {key: value}
        result = self.evaluate(payload)
        self.assertFalse(result["m14_final_completion_valid"])
        self.assertTrue(result["m14_final_completion_invalid"])
        self.assertTrue(result["escalation_required"])

    def test_01_exact_four_changed_file_scope(self):
        self.assertEqual(self.fixture["changed_file_scope"], EXPECTED_CHANGED_FILES)

    def test_02_valid_final_top_level_state(self):
        result = self.evaluate()
        self.assertTrue(result["m14_final_completion_valid"])
        self.assertFalse(result["m14_final_completion_invalid"])

    def test_03_correct_tracker_closing_linkage(self):
        self.assertEqual(self.fixture["tracker_issue_linkage"], "Closes #201")
        self.fixture["tracker_issue_linkage"] = "Refs #201"
        self.assertFalse(self.evaluate()["m14_final_completion_valid"])

    def test_04_correct_nine_source_pr_references(self):
        packet = self.fixture["final_completion_evidence_packet"]
        self.assertEqual(packet["source_pr_references"], EXPECTED_SOURCE_PRS)
        for source_pr in EXPECTED_SOURCE_PRS:
            payload = deepcopy(self.fixture)
            payload["final_completion_evidence_packet"]["source_pr_references"].remove(
                source_pr
            )
            self.assertFalse(self.evaluate(payload)["m14_final_completion_valid"])

    def test_05_pr_209_absent_from_m14_evidence_chain(self):
        chain = {
            "top_level": {
                key: value
                for key, value in self.fixture.items()
                if key.endswith("_pr")
            },
            "linkage": self.fixture["release_linkage_refs"],
            "packet": self.fixture["final_completion_evidence_packet"],
        }
        self.assertNotIn("#209", json.dumps(chain, sort_keys=True))
        self.fixture["final_completion_evidence_packet"]["source_pr_references"].append(
            "#209"
        )
        self.assertFalse(self.evaluate()["m14_final_completion_valid"])

    def test_06_completion_readiness_bundle_has_exactly_three_files(self):
        self.assertEqual(len(self.fixture["completion_readiness_bundle"]), 3)
        self.assertEqual(self.fixture["completion_readiness_bundle"], EXPECTED_BUNDLE)

    def test_07_all_bundle_files_exist(self):
        for entry in EXPECTED_BUNDLE:
            self.assertTrue((ROOT / entry["relative_path"]).is_file())

    def test_08_all_bundle_sha256_digests_match(self):
        for entry in EXPECTED_BUNDLE:
            self.assertEqual(
                canonical_sha256(ROOT / entry["relative_path"]),
                EXPECTED_MAINTAINED_BUNDLE_SHA256[entry["relative_path"]],
            )
        self.assertEqual(
            self.fixture["completion_readiness_bundle"],
            EXPECTED_BUNDLE,
        )
        self.assertNotEqual(
            EXPECTED_MAINTAINED_BUNDLE_SHA256[
                "tests/test_m14_completion_readiness_evaluator.py"
            ],
            EXPECTED_BUNDLE[2]["sha256"],
        )
        self.assertTrue(self.evaluate()["completion_readiness_bundle_integrity_valid"])

    def test_09_missing_bundle_file_fails(self):
        with self.temporary_repository() as root:
            (root / EXPECTED_BUNDLE[1]["relative_path"]).unlink()
            result = self.evaluate(repository_root=root)
        self.assertFalse(result["m14_final_completion_valid"])
        self.assertFalse(result["completion_readiness_bundle_present"])

    def test_10_bundle_digest_mismatch_fails(self):
        with self.temporary_repository() as root:
            path = root / EXPECTED_BUNDLE[2]["relative_path"]
            path.write_bytes(path.read_bytes() + b"# digest mutation\n")
            result = self.evaluate(repository_root=root)
        self.assertFalse(result["m14_final_completion_valid"])
        self.assertFalse(result["completion_readiness_bundle_integrity_valid"])

    def test_11_bundle_path_substitution_fails(self):
        self.fixture["completion_readiness_bundle"][0]["relative_path"] = "README.md"
        result = self.evaluate()
        self.assertFalse(result["m14_final_completion_valid"])

    def test_12_pr_214_fixture_is_loaded_as_inert_json(self):
        tree = ast.parse(self.evaluator_source)
        imported = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertFalse(any("m14_completion_readiness" in name for name in imported))
        self.assertTrue(
            self.fixture["completion_readiness_state_validation"][
                "loaded_as_inert_json_only"
            ]
        )

    def test_13_pre_transition_readiness_state_is_valid(self):
        result = self.evaluate()
        self.assertTrue(result["completion_readiness_state_valid"])
        source = load_json(READINESS_FIXTURE_PATH)
        for key, value in EXPECTED_PRE_TRANSITION.items():
            self.assertEqual(source[key], value)

    def test_14_pre_transition_must_be_ready_for_final_review(self):
        result = self.evaluate_readiness_mutation(
            "ready_for_final_m14_completion_review", False
        )
        self.assertFalse(result["completion_readiness_state_valid"])

    def test_15_pre_transition_fixture_must_not_claim_m14_complete(self):
        result = self.evaluate_readiness_mutation("m14_complete", True)
        self.assertFalse(result["completion_readiness_state_valid"])

    def test_16_pre_transition_fixture_must_not_claim_v013_released(self):
        result = self.evaluate_readiness_mutation("released", True)
        self.assertFalse(result["completion_readiness_state_valid"])

    def test_17_final_artifact_declares_m14_complete(self):
        self.assertTrue(self.fixture["m14_complete"])
        self.assertEqual(self.fixture["m14_completion_status"], "complete")
        self.assertTrue(self.evaluate()["m14_completion_declared"])

    def test_18_final_review_is_recorded_completed(self):
        self.assertTrue(self.fixture["final_m14_completion_review_completed"])
        self.assertTrue(self.evaluate()["final_m14_completion_review_recorded"])

    def test_19_tracker_linkage_is_closes_on_merge(self):
        self.assertEqual(self.fixture["tracker_issue_closure_state"], "closes_on_merge")
        self.assertTrue(self.fixture["issue_201_closes_on_merge"])
        self.assertTrue(self.evaluate()["issue_201_closes_on_merge"])

    def test_20_repository_release_state_is_prepared(self):
        self.assertEqual(
            self.fixture["release_status"], "repository_release_state_prepared"
        )
        self.assertTrue(self.evaluate()["repository_release_state_prepared"])

    def test_21_github_release_is_not_created_by_pr(self):
        self.assertIs(self.fixture["github_release_created_by_pr"], False)
        self.fixture["github_release_created_by_pr"] = True
        self.assertFalse(self.evaluate()["m14_final_completion_valid"])

    def test_22_release_tag_is_not_created_by_pr(self):
        self.assertIs(self.fixture["release_tag_created_by_pr"], False)
        self.fixture["release_tag_created_by_pr"] = True
        self.assertFalse(self.evaluate()["m14_final_completion_valid"])

    def test_23_release_notes_are_not_published_by_pr(self):
        self.assertIs(self.fixture["release_notes_published_by_pr"], False)
        self.fixture["release_notes_published_by_pr"] = True
        self.assertFalse(self.evaluate()["m14_final_completion_valid"])

    def test_24_manual_publication_is_required_after_merge(self):
        self.assertTrue(self.fixture["github_release_to_be_created_after_merge"])
        self.assertEqual(
            self.fixture["release_state_boundary"]["github_release_publication"],
            "manual_after_merge_only",
        )
        self.assertTrue(self.evaluate()["github_release_pending_manual_publication"])

    def test_25_release_state_preparation_is_not_publication(self):
        boundary = self.fixture["release_state_boundary"]
        self.assertIs(boundary["release_state_preparation_is_publication"], False)
        self.assertIs(boundary["final_completion_is_github_release_publication"], False)

    def test_26_readme_v013_release_entry_exists(self):
        entry = "- v0.13.0 — M14 High-Risk Runtime Policy Gates and Public-Output Safety"
        self.assertIn(entry, self.readme)
        result = self.evaluate_readme_mutation(entry + "\n", "")
        self.assertFalse(result["readme_release_state_valid"])

    def test_27_readme_latest_release_is_v013(self):
        releases = self.readme.split("## Releases", 1)[1].split("Current baseline:", 1)[0]
        version_lines = [line for line in releases.splitlines() if line.startswith("- v")]
        self.assertTrue(version_lines[-1].startswith("- v0.13.0 —"))
        result = self.evaluate_readme_mutation(
            "- v0.13.0 — M14 High-Risk Runtime Policy Gates and Public-Output Safety\n",
            "- v0.13.0 — M14 High-Risk Runtime Policy Gates and Public-Output Safety\n"
            "- v0.14.0 — unauthorized future release\n",
        )
        self.assertFalse(result["readme_release_state_valid"])

    def test_28_readme_retains_v012(self):
        entry = "- v0.12.0 — M13 External Consumer Registry Hardening and Operational Readiness"
        self.assertIn(entry, self.readme)
        result = self.evaluate_readme_mutation(entry + "\n", "")
        self.assertFalse(result["readme_release_state_valid"])

    def test_29_readme_baseline_includes_m14(self):
        phrase = "the M14 High-Risk Runtime Policy Gates and Public-Output Safety pattern"
        self.assertIn(phrase, self.readme)
        result = self.evaluate_readme_mutation(phrase, "the M14 pattern")
        self.assertFalse(result["readme_release_state_valid"])

    def test_30_readme_declares_m1_through_m14_complete(self):
        sentence = (
            "M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11, M12, M13, "
            "and M14 are complete."
        )
        self.assertIn(sentence, self.readme)
        result = self.evaluate_readme_mutation(sentence, sentence.replace(", and M14", ""))
        self.assertFalse(result["readme_release_state_valid"])

    def test_31_m14_completed_section_is_complete(self):
        section = self.readme.split("M14 completed:", 1)[1].split(
            "AAOS Public now has:", 1
        )[0]
        for reference in EXPECTED_M14_COMPLETED_REFS:
            self.assertIn(reference, section)
            result = self.evaluate_readme_mutation("- " + reference + "\n", "")
            self.assertFalse(result["readme_release_state_valid"])

    def test_32_all_m14_output_bullets_exist(self):
        section = self.readme.split("AAOS Public now has:", 1)[1].split(
            "## M5 Additions", 1
        )[0]
        for output in EXPECTED_M14_OUTPUTS:
            self.assertIn("- " + output, section)
            result = self.evaluate_readme_mutation("- " + output + "\n", "")
            self.assertFalse(result["readme_release_state_valid"])

    def test_33_next_phase_post_release_statement_is_exact(self):
        expected = (
            "## Next Phase\n\n"
            "Future milestone planning will be tracked separately after v0.13.0 release publication.\n"
        )
        self.assertEqual(self.readme.split("## Next Phase", 1)[1].join(["## Next Phase", ""]), expected)
        result = self.evaluate_readme_mutation(
            "Future milestone planning will be tracked separately after v0.13.0 release publication.",
            "Future planning remains active.",
        )
        self.assertFalse(result["readme_release_state_valid"])

    def test_34_obsolete_active_work_wording_is_absent(self):
        next_phase = self.readme.split("## Next Phase", 1)[1]
        for phrase in [
            "M14 remains active work",
            "final completion has not been declared",
            "Tracker: #201 remains Open",
            "ready_for_final_m14_completion_review is not final completion review completed",
        ]:
            self.assertNotIn(phrase, next_phase)
        result = self.evaluate_readme_mutation(
            "Future milestone planning will be tracked separately after v0.13.0 release publication.",
            "Future milestone planning will be tracked separately after v0.13.0 release publication.\n"
            "M14 remains active work",
        )
        self.assertFalse(result["readme_release_state_valid"])

    def test_35_obsolete_future_only_wording_is_absent(self):
        next_phase = self.readme.split("## Next Phase", 1)[1]
        self.assertNotIn("v0.13.0 remains future-only", next_phase)
        result = self.evaluate_readme_mutation(
            "Future milestone planning will be tracked separately after v0.13.0 release publication.",
            "Future milestone planning will be tracked separately after v0.13.0 release publication.\n"
            "v0.13.0 remains future-only",
        )
        self.assertFalse(result["readme_release_state_valid"])

    def test_36_decision_proof_sealing_boundary_remains(self):
        phrase = "Decision Proof sealing remains AAOS-owned."
        self.assertIn(phrase, self.readme)
        result = self.evaluate_readme_mutation(phrase, "Decision Proof sealing moved.")
        self.assertFalse(result["readme_release_state_valid"])

    def test_37_aaos_sovereignty_boundary_remains(self):
        phrase = "AAOS remains the decision sovereignty layer."
        self.assertIn(phrase, self.readme)
        result = self.evaluate_readme_mutation(phrase, "AAOS is a signal layer.")
        self.assertFalse(result["readme_release_state_valid"])

    def test_38_evaluator_does_not_query_github(self):
        tree = ast.parse(self.evaluator_source)
        imported_roots = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            (node.module or "").split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertTrue(
            imported_roots.isdisjoint(
                {"requests", "urllib", "http", "socket", "github", "ghapi"}
            )
        )

    def test_39_evaluator_does_not_import_source_evaluators(self):
        tree = ast.parse(self.evaluator_source)
        imported = [
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        ] + [
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        ]
        self.assertFalse(any(name.startswith("runtime.") for name in imported))
        self.assertFalse(any(name.startswith("tests.") for name in imported))

    def test_40_evaluator_does_not_execute_workflows(self):
        tree = ast.parse(self.evaluator_source)
        imported_roots = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            (node.module or "").split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertTrue(imported_roots.isdisjoint({"subprocess", "runpy", "importlib"}))

    def test_41_evaluator_does_not_execute_verification_commands(self):
        with mock.patch("subprocess.run") as run, mock.patch("os.system") as system:
            result = self.evaluate()
        run.assert_not_called()
        system.assert_not_called()
        self.assertTrue(result["m14_final_completion_valid"])

    def test_42_evaluator_cannot_create_a_release(self):
        self.assert_authority_claim_fails("github_release_created", True)

    def test_43_evaluator_cannot_create_a_tag(self):
        self.assert_authority_claim_fails("release_tag_created_by_evaluator", True)

    def test_44_evaluator_cannot_directly_close_tracker(self):
        self.assert_authority_claim_fails("tracker_closed_by_evaluator", "closed")

    def test_45_evaluator_cannot_accept_risk(self):
        self.assert_authority_claim_fails("risk_accepted_by_evaluator", True)

    def test_46_evaluator_cannot_execute_rollback(self):
        self.assert_authority_claim_fails("rollback_executed_by_evaluator", True)

    def test_47_evaluator_cannot_execute_fail_closed(self):
        self.assert_authority_claim_fails("fail_closed_executed_by_evaluator", True)

    def test_48_evaluator_cannot_close_audit(self):
        self.assert_authority_claim_fails("audit_closed_by_evaluator", True)

    def test_49_evaluator_cannot_transfer_authority(self):
        self.assert_authority_claim_fails("authority_transferred", True)

    def test_50_evaluator_cannot_make_final_governance_judgment(self):
        self.assert_authority_claim_fails(
            "final_governance_judgment_by_evaluator", "made"
        )

    def test_51_evaluator_cannot_seal_decision_proof(self):
        self.assert_authority_claim_fails("decision_proof_sealed_by_evaluator", True)

    def test_52_explicit_negative_governance_evidence_remains_valid(self):
        self.fixture["artifact_links"]["explicit_negative_evidence"] = {
            "github_release_created": False,
            "release_tag_created_by_evaluator": "not_created",
            "tracker_closed_by_evaluator": "not_closed",
            "decision_proof_sealed_by_evaluator": "not_sealed",
            "release_authority_granted_by_evaluator": "not_granted",
        }
        self.assertTrue(self.evaluate()["m14_final_completion_valid"])

    def test_53_nested_affirmative_evaluator_authority_claim_fails(self):
        self.assert_authority_claim_fails(
            "release_authority_granted_by_evaluator",
            {"status": "granted", "decision": "authorized"},
        )

    def test_54_negative_outer_state_cannot_hide_nested_affirmative_claim(self):
        self.fixture["artifact_links"]["nested_claim"] = {
            "state": "not_authorized",
            "release_authority_granted_by_evaluator": False,
            "nested": {"release_authority_granted_by_evaluator": "granted"},
        }
        result = self.evaluate()
        self.assertFalse(result["m14_final_completion_valid"])
        self.assertTrue(result["escalation_required"])

    def test_55_manual_release_steps_are_ordered(self):
        steps = self.fixture["manual_release_publication_steps"]
        self.assertEqual([item["step_order"] for item in steps], list(range(1, 8)))
        self.assertEqual([item["step"] for item in steps], EXPECTED_MANUAL_STEPS)
        steps[0], steps[1] = steps[1], steps[0]
        self.assertFalse(self.evaluate()["manual_release_steps_valid"])

    def test_56_manual_release_steps_are_post_merge_only(self):
        for item in self.fixture["manual_release_publication_steps"]:
            self.assertIs(item["performed_after_merge"], True)
            self.assertIs(item["performed_by_this_pr"], False)
            self.assertIs(item["performed_by_evaluator"], False)
        self.fixture["manual_release_publication_steps"][0]["performed_by_evaluator"] = True
        self.assertFalse(self.evaluate()["manual_release_steps_valid"])

    def test_57_public_evaluator_apis_return_the_valid_final_baseline(self):
        loaded = load_fixture(FIXTURE_PATH)
        results = [
            evaluate_m14_final_completion(loaded, ROOT),
            validate_m14_final_completion(loaded, ROOT),
            evaluate_file(FIXTURE_PATH, ROOT),
        ]
        for result in results:
            self.assertTrue(result["m14_final_completion_valid"])
            self.assertFalse(result["review_required"])
            self.assertFalse(result["escalation_required"])

    def test_58_required_top_level_contract_is_exact(self):
        expected = {
            "artifact_id": "m14-final-completion-release-state",
            "artifact_name": "M14 Final Completion Release State",
            "artifact_scope": "high_risk_runtime_policy_and_public_output_safety_final_completion_release_state_preparation",
            "artifact_status": "final_completion_release_state_prepared",
            "milestone": "M14",
            "m14_completion_status": "complete",
            "related_issue": "#201",
            "prior_released_baseline": "v0.12.0",
            "target_release": "v0.13.0",
            "release_status": "repository_release_state_prepared",
        }
        for key, value in expected.items():
            self.assertEqual(self.fixture[key], value)

    def test_59_bundle_metadata_and_main_digests_are_exact(self):
        self.assertEqual(self.fixture["completion_readiness_bundle"], EXPECTED_BUNDLE)

    def test_60_pre_transition_validation_contract_is_exact(self):
        validation = self.fixture["completion_readiness_state_validation"]
        self.assertTrue(validation["loaded_as_inert_json_only"])
        self.assertEqual(validation["expected_values"], EXPECTED_PRE_TRANSITION)
        self.assertEqual(
            validation["required_authority"],
            {
                "retained_authority_owner": "AAOS",
                "decision_proof_sealing_owner": "AAOS",
            },
        )

    def test_61_manual_step_text_is_exact(self):
        self.assertEqual(
            [item["step"] for item in self.fixture["manual_release_publication_steps"]],
            EXPECTED_MANUAL_STEPS,
        )

    def test_62_required_boundary_statements_are_complete(self):
        required = set(self.fixture["required_boundary_statements"])
        for statement in [
            "The human-reviewed merge is the authorized final-completion transition.",
            "The deterministic evaluator validates evidence but does not grant release authority.",
            "The evaluator does not make the final governance judgment.",
            "Decision Proof sealing remains AAOS-owned.",
            "AAOS remains the decision sovereignty layer.",
            "Final governance authority remains AAOS-owned.",
        ]:
            self.assertIn(statement, required)

    def test_63_allowed_and_forbidden_output_catalogs_are_exact_and_disjoint(self):
        allowed = set(self.fixture["allowed_evaluator_outputs"])
        forbidden = set(self.fixture["forbidden_evaluator_outputs"])
        self.assertEqual(allowed, EXPECTED_ALLOWED_OUTPUTS)
        self.assertEqual(forbidden, EXPECTED_FORBIDDEN_OUTPUTS)
        self.assertTrue(allowed.isdisjoint(forbidden))

    def test_64_authority_boundary_retains_aaos_ownership(self):
        boundary = self.fixture["authority_boundary"]
        self.assertEqual(boundary["retained_authority_owner"], "AAOS")
        self.assertEqual(boundary["decision_proof_sealing_owner"], "AAOS")
        self.assertEqual(
            boundary["final_completion_transition_authorized_by"],
            "human_reviewed_merge",
        )
        self.assertNotIn("grant_release_authority", boundary["may"])
        self.assertIn("grant_release_authority", boundary["must_not"])

    def test_65_final_completion_evidence_packet_is_exactly_linked(self):
        packet = self.fixture["final_completion_evidence_packet"]
        self.assertEqual(packet["source_pr_references"], EXPECTED_SOURCE_PRS)
        self.assertEqual(packet["completion_readiness_pr"], "#214")
        self.assertEqual(
            packet["completion_readiness_bundle_digests"],
            [
                {"relative_path": entry["relative_path"], "sha256": entry["sha256"]}
                for entry in EXPECTED_BUNDLE
            ],
        )
        self.assertEqual(packet["authority_owner"], "AAOS")
        self.assertEqual(packet["decision_proof_sealing_owner"], "AAOS")

    def test_66_artifact_and_release_linkage_refs_are_complete(self):
        links = self.fixture["artifact_links"]
        for path in EXPECTED_CHANGED_FILES:
            if path == "README.md" or "final-completion" in path or "final_completion" in path:
                self.assertIn(path, links.values())
        refs = self.fixture["release_linkage_refs"]
        self.assertEqual(refs["m14_tracker_issue"], "#201")
        self.assertEqual(refs["tracker_issue_linkage"], "Closes #201")
        self.assertEqual(
            {value for key, value in refs.items() if key.endswith("_pr")},
            set(EXPECTED_SOURCE_PRS),
        )

    def test_67_evaluator_cannot_grant_a_waiver(self):
        self.assert_authority_claim_fails("waiver_granted_by_evaluator", True)

    def test_68_unknown_non_empty_forbidden_value_is_affirmative(self):
        self.assert_authority_claim_fails(
            "release_authority_granted_by_evaluator", "unexpected_state"
        )

    def test_69_structured_authority_status_is_recursively_inspected(self):
        self.assert_authority_claim_fails(
            "risk_accepted_by_evaluator",
            {"authority_status": "not_accepted", "nested": {"status": "accepted"}},
        )

    def test_70_authorized_final_root_facts_are_not_evaluator_authority(self):
        for key in [
            "final_m14_completion_review_completed",
            "final_completion_recorded_by_authorized_merge",
            "m14_complete",
            "issue_201_closes_on_merge",
            "repository_release_state_prepared",
        ]:
            self.assertIs(self.fixture[key], True)
        self.assertIs(
            self.fixture["release_state_boundary"]["repository_release_state_prepared"],
            True,
        )
        self.assertTrue(self.evaluate()["m14_final_completion_valid"])

    def test_71_authorized_final_fact_nested_elsewhere_is_invalid(self):
        self.fixture["artifact_links"]["nested_transition_claim"] = {
            "m14_complete": True
        }
        result = self.evaluate()
        self.assertFalse(result["m14_final_completion_valid"])
        self.assertTrue(result["escalation_required"])

    def test_72_expected_baseline_result_matches_public_result(self):
        result = self.evaluate()
        expected = self.fixture["expected_baseline_result"]
        for key, value in expected.items():
            self.assertEqual(result[key], value)

    def test_73_evaluator_uses_only_standard_library_imports(self):
        tree = ast.parse(self.evaluator_source)
        allowed = {"__future__", "hashlib", "json", "re", "pathlib", "typing"}
        imported = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            (node.module or "").split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertTrue(imported <= allowed)

    def test_74_evaluator_uses_no_dynamic_execution(self):
        tree = ast.parse(self.evaluator_source)
        forbidden_calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in {"eval", "exec", "compile", "__import__"}:
                    forbidden_calls.append(node.func.id)
        self.assertEqual(forbidden_calls, [])

    def test_75_release_state_boundary_contract_is_exact(self):
        self.assertEqual(
            self.fixture["release_state_boundary"],
            {
                "repository_release_state_prepared": True,
                "github_release_publication": "manual_after_merge_only",
                "github_release_created_by_pr": False,
                "release_tag_created_by_pr": False,
                "release_notes_published_by_pr": False,
                "release_state_preparation_is_publication": False,
                "final_completion_is_github_release_publication": False,
            },
        )

    def test_76_repository_release_state_fact_nested_elsewhere_is_invalid(self):
        self.fixture["artifact_links"]["nested_transition_claim"] = {
            "repository_release_state_prepared": True
        }
        result = self.evaluate()
        self.assertFalse(result["m14_final_completion_valid"])
        self.assertTrue(result["escalation_required"])

    def test_77_root_repository_release_state_must_be_true(self):
        self.fixture["repository_release_state_prepared"] = False
        result = self.evaluate()
        self.assertFalse(result["m14_final_completion_valid"])
        self.assertIn(
            "top_level_true_required:repository_release_state_prepared",
            result["findings"],
        )

    def test_78_nested_must_not_key_cannot_hide_affirmative_claim(self):
        self.fixture["artifact_links"]["claim"] = {
            "must_not": {"release_authority_granted_by_evaluator": True}
        }
        result = self.evaluate()
        self.assertFalse(result["m14_final_completion_valid"])
        self.assertTrue(result["escalation_required"])

    def test_79_negative_status_cannot_hide_unknown_affirmative_field(self):
        self.assert_authority_claim_fails(
            "risk_accepted_by_evaluator",
            {"authority_status": "not_accepted", "claim": "accepted"},
        )

    def test_80_camel_case_authority_claim_is_invalid(self):
        self.assert_authority_claim_fails("evaluatorGrantsReleaseAuthority", True)

    def test_81_split_actor_action_status_claim_is_invalid(self):
        self.fixture["artifact_links"]["claim"] = {
            "actor": "evaluator",
            "action": "grant_release_authority",
            "status": "completed",
        }
        result = self.evaluate()
        self.assertFalse(result["m14_final_completion_valid"])
        self.assertTrue(result["escalation_required"])

    def test_82_affirmative_authority_prose_is_invalid(self):
        self.fixture["artifact_links"]["claim"] = (
            "The evaluator grants release authority."
        )
        result = self.evaluate()
        self.assertFalse(result["m14_final_completion_valid"])
        self.assertTrue(result["escalation_required"])

    def test_83_explicit_negative_authority_prose_remains_valid(self):
        self.fixture["artifact_links"]["claim"] = (
            "The evaluator does not grant release authority."
        )
        result = self.evaluate()
        self.assertTrue(result["m14_final_completion_valid"])
        self.assertFalse(result["escalation_required"])

    def test_84_inert_catalogs_reject_structured_claim_injection(self):
        targets = [
            self.fixture["allowed_evaluator_outputs"],
            self.fixture["forbidden_evaluator_outputs"],
            self.fixture["required_boundary_statements"],
            self.fixture["authority_boundary"]["must_not"],
        ]
        for target in targets:
            with self.subTest(target=target[0]):
                payload = deepcopy(self.fixture)
                if target is self.fixture["allowed_evaluator_outputs"]:
                    candidate = payload["allowed_evaluator_outputs"]
                elif target is self.fixture["forbidden_evaluator_outputs"]:
                    candidate = payload["forbidden_evaluator_outputs"]
                elif target is self.fixture["required_boundary_statements"]:
                    candidate = payload["required_boundary_statements"]
                else:
                    candidate = payload["authority_boundary"]["must_not"]
                candidate.append({"risk_accepted_by_evaluator": True})
                result = self.evaluate(payload)
                self.assertFalse(result["m14_final_completion_valid"])
                self.assertTrue(result["escalation_required"])

    def test_85_split_authority_claim_aliases_are_invalid(self):
        claims = [
            {
                "actor": "evaluator",
                "action": "release_authority_granted",
                "status": "completed",
            },
            {
                "actor": "the_evaluator",
                "action": "grant_release_authority",
                "status": "completed",
            },
            {
                "performed_by": "evaluator",
                "action": "grant_release_authority",
                "status": "completed",
            },
        ]
        for claim in claims:
            with self.subTest(claim=claim):
                payload = deepcopy(self.fixture)
                payload["artifact_links"]["claim"] = claim
                result = self.evaluate(payload)
                self.assertFalse(result["m14_final_completion_valid"])
                self.assertTrue(result["escalation_required"])

    def test_86_passive_and_auxiliary_authority_prose_is_invalid(self):
        claims = [
            "Release authority is granted by the evaluator.",
            "The evaluator has granted release authority.",
        ]
        for claim in claims:
            with self.subTest(claim=claim):
                payload = deepcopy(self.fixture)
                payload["artifact_links"]["claim"] = claim
                result = self.evaluate(payload)
                self.assertFalse(result["m14_final_completion_valid"])
                self.assertTrue(result["escalation_required"])

    def test_87_allowed_and_boundary_catalog_string_injection_fails(self):
        for field in ["allowed_evaluator_outputs", "required_boundary_statements"]:
            with self.subTest(field=field):
                payload = deepcopy(self.fixture)
                payload[field].append("The evaluator grants release authority.")
                result = self.evaluate(payload)
                self.assertFalse(result["m14_final_completion_valid"])
                self.assertTrue(result["escalation_required"])

    def test_88_extended_camel_case_authority_keys_are_invalid(self):
        keys = [
            "m14EvaluatorGrantsReleaseAuthority",
            "evaluatorGrantsReleaseAuthorityClaim",
            "GitHubReleaseCreatedByEvaluator",
        ]
        for key in keys:
            with self.subTest(key=key):
                self.assert_authority_claim_fails(key, True)

    def test_89_split_field_and_action_aliases_are_invalid(self):
        claims = [
            {
                "subject": "evaluator",
                "action": "grant_release_authority",
                "status": "completed",
            },
            {
                "actor": "evaluator",
                "activity": "grant_release_authority",
                "status": "completed",
            },
            {
                "actor": "evaluator",
                "action": "granting authority for release",
                "status": "completed",
            },
        ]
        for claim in claims:
            with self.subTest(claim=claim):
                payload = deepcopy(self.fixture)
                payload["artifact_links"]["claim"] = claim
                result = self.evaluate(payload)
                self.assertFalse(result["m14_final_completion_valid"])
                self.assertTrue(result["escalation_required"])

    def test_90_negation_scope_and_authority_synonyms_are_inspected(self):
        claims = [
            "The evaluator does not query GitHub and grants release authority.",
            "The evaluator authorizes the release.",
            "The evaluator performs rollback.",
        ]
        for claim in claims:
            with self.subTest(claim=claim):
                payload = deepcopy(self.fixture)
                payload["artifact_links"]["claim"] = claim
                result = self.evaluate(payload)
                self.assertFalse(result["m14_final_completion_valid"])
                self.assertTrue(result["escalation_required"])

    def test_91_nested_evaluator_context_is_propagated(self):
        claims = [
            {
                "actor": "evaluator",
                "details": {
                    "action": "grant_release_authority",
                    "status": "completed",
                },
            },
            {
                "evaluator": {
                    "action": "publish_release",
                    "status": "completed",
                }
            },
            {"evaluator": {"release_published": True}},
        ]
        for claim in claims:
            with self.subTest(claim=claim):
                payload = deepcopy(self.fixture)
                payload["artifact_links"]["claim"] = claim
                result = self.evaluate(payload)
                self.assertFalse(result["m14_final_completion_valid"])
                self.assertTrue(result["escalation_required"])

    def test_92_actor_role_and_completed_noun_actions_are_invalid(self):
        actions = [
            "seal_decision_proof",
            "rollback",
            "fail_closed",
            "release_publication",
            "final_governance_judgment",
        ]
        for action in actions:
            with self.subTest(action=action):
                payload = deepcopy(self.fixture)
                payload["artifact_links"]["claim"] = {
                    "actor_role": "evaluator",
                    "action": action,
                    "status": "completed",
                }
                result = self.evaluate(payload)
                self.assertFalse(result["m14_final_completion_valid"])
                self.assertTrue(result["escalation_required"])

    def test_93_evaluator_context_crosses_clause_boundaries(self):
        claims = [
            "The evaluator validates evidence but grants release authority.",
            "The evaluator validates evidence; publishes the release.",
            "The evaluator does not seal Decision Proof yet publishes the release.",
        ]
        for claim in claims:
            with self.subTest(claim=claim):
                payload = deepcopy(self.fixture)
                payload["artifact_links"]["claim"] = claim
                result = self.evaluate(payload)
                self.assertFalse(result["m14_final_completion_valid"])
                self.assertTrue(result["escalation_required"])


if __name__ == "__main__":
    unittest.main()
