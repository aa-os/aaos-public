import ast
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.m14_operational_readiness_evaluator import (  # noqa: E402
    evaluate_file,
    evaluate_m14_operational_readiness,
    load_fixture,
    validate_m14_operational_readiness,
)


FIXTURE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m14-operational-readiness-fixtures.json"
)
EVALUATOR_PATH = ROOT / "runtime" / "m14_operational_readiness_evaluator.py"
TEST_PATH = Path(__file__).resolve()

EXPECTED_CHANGED_FILES = {
    "examples/public-integration-pack-pilot/"
    "m14-operational-readiness-fixtures.json",
    "runtime/m14_operational_readiness_evaluator.py",
    "tests/test_m14_operational_readiness_evaluator.py",
}

EXPECTED_TRACKS = {
    "voice_runtime_policy": {
        "source_pr": "#202",
        "component_role": "governed_voice_runtime_policy_gate",
        "source_paths": {
            "examples/public-integration-pack-pilot/"
            "voxcpm-governed-voice-fixtures.json",
            "runtime/voice_generation_policy_evaluator.py",
            "tests/test_voice_generation_policy_evaluator.py",
        },
    },
    "public_output_exfiltration_gate": {
        "source_pr": "#204",
        "component_role": "public_output_exfiltration_gate",
        "source_paths": {
            "examples/public-integration-pack-pilot/"
            "m14-public-issue-exfiltration-gate-fixtures.json",
            "runtime/public_issue_exfiltration_gate_evaluator.py",
            "tests/test_public_issue_exfiltration_gate_evaluator.py",
        },
    },
    "moda_risk_mapping": {
        "source_pr": "#205",
        "component_role": "external_regulatory_risk_taxonomy_mapping",
        "source_paths": {
            "docs/public-integration-pack/m14-moda-ai-risk-framework-mapping.md",
            "examples/public-integration-pack-pilot/"
            "m14-moda-ai-risk-decision-proof-fixtures.json",
            "runtime/moda_ai_risk_mapping_evaluator.py",
            "tests/test_moda_ai_risk_mapping_evaluator.py",
        },
    },
    "ai_pr_provenance": {
        "source_pr": "#206",
        "component_role": "ai_pr_provenance_and_reviewer_routing",
        "source_paths": {
            ".github/workflows/m14-ai-pr-provenance.yml",
            "examples/public-integration-pack-pilot/"
            "m14-ai-authored-pr-provenance-fixtures.json",
            "runtime/ai_authored_pr_provenance_evaluator.py",
            "tests/test_ai_authored_pr_provenance_evaluator.py",
        },
    },
    "skill_admission": {
        "source_pr": "#208",
        "component_role": "external_skill_capability_admission_gate",
        "source_paths": {
            "docs/capability-supply-chain/nvidia-skills-admission.md",
            "examples/public-integration-pack-pilot/"
            "m14-skill-admission-fixtures.json",
            "runtime/skill_admission_evaluator.py",
            "tests/test_skill_admission_evaluator.py",
        },
    },
    "cross_control_authority_boundary": {
        "source_pr": "#210",
        "component_role": "cross_control_authority_boundary_regression",
        "source_paths": {
            "examples/public-integration-pack-pilot/"
            "m14-cross-control-authority-boundary-regression-fixtures.json",
            "runtime/m14_cross_control_authority_boundary_evaluator.py",
            "tests/test_m14_cross_control_authority_boundary_evaluator.py",
        },
    },
}

EXPECTED_ARTIFACTS = {
    "examples/public-integration-pack-pilot/voxcpm-governed-voice-fixtures.json":
        ("voice_runtime_policy", "#202", "fixture"),
    "runtime/voice_generation_policy_evaluator.py":
        ("voice_runtime_policy", "#202", "runtime_evaluator"),
    "tests/test_voice_generation_policy_evaluator.py":
        ("voice_runtime_policy", "#202", "deterministic_test"),
    "examples/public-integration-pack-pilot/"
    "m14-public-issue-exfiltration-gate-fixtures.json":
        ("public_output_exfiltration_gate", "#204", "fixture"),
    "runtime/public_issue_exfiltration_gate_evaluator.py":
        ("public_output_exfiltration_gate", "#204", "runtime_evaluator"),
    "tests/test_public_issue_exfiltration_gate_evaluator.py":
        ("public_output_exfiltration_gate", "#204", "deterministic_test"),
    "docs/public-integration-pack/m14-moda-ai-risk-framework-mapping.md":
        ("moda_risk_mapping", "#205", "mapping_document"),
    "examples/public-integration-pack-pilot/"
    "m14-moda-ai-risk-decision-proof-fixtures.json":
        ("moda_risk_mapping", "#205", "fixture"),
    "runtime/moda_ai_risk_mapping_evaluator.py":
        ("moda_risk_mapping", "#205", "runtime_evaluator"),
    "tests/test_moda_ai_risk_mapping_evaluator.py":
        ("moda_risk_mapping", "#205", "deterministic_test"),
    ".github/workflows/m14-ai-pr-provenance.yml":
        ("ai_pr_provenance", "#206", "workflow_definition"),
    "examples/public-integration-pack-pilot/"
    "m14-ai-authored-pr-provenance-fixtures.json":
        ("ai_pr_provenance", "#206", "fixture"),
    "runtime/ai_authored_pr_provenance_evaluator.py":
        ("ai_pr_provenance", "#206", "runtime_evaluator"),
    "tests/test_ai_authored_pr_provenance_evaluator.py":
        ("ai_pr_provenance", "#206", "deterministic_test"),
    "docs/capability-supply-chain/nvidia-skills-admission.md":
        ("skill_admission", "#208", "admission_document"),
    "examples/public-integration-pack-pilot/m14-skill-admission-fixtures.json":
        ("skill_admission", "#208", "fixture"),
    "runtime/skill_admission_evaluator.py":
        ("skill_admission", "#208", "runtime_evaluator"),
    "tests/test_skill_admission_evaluator.py":
        ("skill_admission", "#208", "deterministic_test"),
    "examples/public-integration-pack-pilot/"
    "m14-cross-control-authority-boundary-regression-fixtures.json":
        ("cross_control_authority_boundary", "#210", "fixture"),
    "runtime/m14_cross_control_authority_boundary_evaluator.py":
        ("cross_control_authority_boundary", "#210", "runtime_evaluator"),
    "tests/test_m14_cross_control_authority_boundary_evaluator.py":
        ("cross_control_authority_boundary", "#210", "deterministic_test"),
}

EXPECTED_DIMENSION_STATES = {
    "source_track_coverage": "ready",
    "source_artifact_presence": "ready",
    "source_artifact_integrity": "ready",
    "runtime_capability_permission_boundary": "ready",
    "consent_and_identity_boundary": "ready",
    "public_output_safety_boundary": "ready",
    "regulatory_mapping_boundary": "ready",
    "skill_supply_chain_boundary": "ready",
    "cross_control_authority_boundary": "ready",
    "human_review_escalation_coverage": "ready",
    "fail_closed_recommendation_coverage": "ready",
    "rollback_recommendation_coverage": "ready",
    "trace_evidence_coverage": "ready",
    "replay_evidence_coverage": "ready",
    "deterministic_evaluator_coverage": "ready",
    "operational_verification_manifest": "ready",
    "release_proof_linkage_status": "pending_next_stage",
    "readme_future_status_path": "pending_next_stage",
    "tracker_completion_status": "pending_next_stage",
    "decision_sovereignty_retention": "ready",
}

EXPECTED_COMMAND_IDS = {
    "validate_readiness_fixture_json",
    "compile_m14_evaluators",
    "compile_m14_tests",
    "run_merged_m14_targeted_tests",
    "run_operational_readiness_tests",
    "git_diff_check",
    "confirm_changed_file_scope",
}

EXPECTED_OUTSTANDING_ITEMS = [
    "release_proof_linkage",
    "future_readme_status_path",
    "final_m14_completion_review",
    "close_tracker_issue_201",
    "publish_v0_13_0_release",
]

REQUIRED_BOUNDARY_STATEMENTS = {
    "Operational readiness is not milestone completion.",
    "Implementation coverage is not release approval.",
    "Artifact presence is not evidence sufficiency.",
    "Artifact digest match is not governance approval.",
    "Test manifest completeness is not test execution evidence.",
    "A passing readiness evaluator is not final governance judgment.",
    "External GitHub state is reviewer-confirmed evidence, not machine-verified by this evaluator.",
    "ready_for_release_proof_linkage is not M14 complete.",
    "release_proof_linkage_pending is not release approval.",
    "readme_status_path_pending is not README authorization.",
    "Human-review coverage is not completed review.",
    "fail_closed_recommended is not fail_closed_executed.",
    "rollback_recommended is not rollback_executed.",
    "evidence_complete is not Decision Proof sealing.",
    "replay_ready is not Decision Proof sealing.",
    "Explicit negative governance evidence is not an affirmative authority claim.",
    "Decision Proof sealing remains AAOS-owned.",
    "AAOS remains the decision sovereignty layer.",
}

REQUIRED_RESULT_FIELDS = {
    "valid",
    "source_track_coverage_complete",
    "source_artifacts_present",
    "artifact_integrity_valid",
    "authority_boundaries_preserved",
    "human_review_coverage_present",
    "fail_closed_recommendation_coverage_present",
    "rollback_recommendation_coverage_present",
    "trace_coverage_present",
    "replay_coverage_present",
    "verification_manifest_complete",
    "external_state_confirmation_required",
    "outstanding_completion_items_valid",
    "ready_for_release_proof_linkage",
    "ready_for_m14_completion_review",
    "m14_complete",
    "findings",
    "outputs",
}

SOURCE_EVALUATOR_MODULES = {
    "runtime.voice_generation_policy_evaluator",
    "runtime.public_issue_exfiltration_gate_evaluator",
    "runtime.moda_ai_risk_mapping_evaluator",
    "runtime.ai_authored_pr_provenance_evaluator",
    "runtime.skill_admission_evaluator",
    "runtime.m14_cross_control_authority_boundary_evaluator",
}


def index_by(items, key):
    return {item[key]: item for item in items}


def dotted_name(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


class M14OperationalReadinessEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_fixture(FIXTURE_PATH)
        cls.evaluator_text = EVALUATOR_PATH.read_text(encoding="utf-8")
        cls.evaluator_tree = ast.parse(cls.evaluator_text)

    def setUp(self):
        self.fixture = copy.deepcopy(self.baseline)

    def evaluate(self, fixture=None):
        return evaluate_m14_operational_readiness(
            self.fixture if fixture is None else fixture,
            repository_root=ROOT,
        )

    def assert_invalid(self, fixture):
        result = self.evaluate(fixture)
        self.assertFalse(result["valid"])
        self.assertIn("m14_operational_readiness_invalid", result["outputs"])
        self.assertTrue(result["findings"])
        return result

    def track(self, fixture, track_id):
        return index_by(fixture["source_track_manifest"], "track_id")[track_id]

    def artifact(self, fixture, relative_path):
        return index_by(
            fixture["source_artifact_manifest"], "relative_path"
        )[relative_path]

    def dimension(self, fixture, dimension_id):
        return index_by(
            fixture["readiness_dimensions"], "dimension_id"
        )[dimension_id]

    def outstanding(self, fixture, item_id):
        return index_by(
            fixture["outstanding_completion_items"], "item_id"
        )[item_id]

    def test_01_valid_top_level_active_work_state(self):
        self.assertEqual(self.fixture["fixture_status"], "m14_active_work_not_complete")
        self.assertEqual(self.fixture["tracker_issue"], "#201")
        self.assertEqual(self.fixture["tracker_issue_linkage"], "Refs #201")
        self.assertEqual(
            self.fixture["readiness_scope"],
            "m14_operational_readiness_before_release_proof",
        )
        self.assertEqual(
            self.fixture["m14_completion_status"], "active_work_not_complete"
        )
        self.assertTrue(self.evaluate()["valid"])

    def test_02_exact_three_changed_file_scope(self):
        scope = self.fixture["changed_file_scope"]
        self.assertEqual(len(scope), 3)
        self.assertEqual(set(scope), EXPECTED_CHANGED_FILES)

    def test_03_exactly_six_source_tracks(self):
        tracks = self.fixture["source_track_manifest"]
        self.assertEqual(len(tracks), 6)
        self.assertEqual(set(index_by(tracks, "track_id")), set(EXPECTED_TRACKS))

    def test_04_correct_source_pr_linkage(self):
        top_level = {
            "related_voice_runtime_pr": "#202",
            "related_public_output_gate_pr": "#204",
            "related_moda_mapping_pr": "#205",
            "related_ai_pr_provenance_pr": "#206",
            "related_skill_admission_pr": "#208",
            "related_cross_control_regression_pr": "#210",
        }
        for field, expected in top_level.items():
            self.assertEqual(self.fixture[field], expected)
        for track_id, expected in EXPECTED_TRACKS.items():
            self.assertEqual(self.track(self.fixture, track_id)["source_pr"], expected["source_pr"])

    def test_05_complete_source_artifact_manifest(self):
        artifacts = self.fixture["source_artifact_manifest"]
        self.assertEqual(len(artifacts), 21)
        self.assertEqual(set(index_by(artifacts, "relative_path")), set(EXPECTED_ARTIFACTS))
        for path, (track_id, source_pr, artifact_type) in EXPECTED_ARTIFACTS.items():
            entry = self.artifact(self.fixture, path)
            self.assertEqual(entry["track_id"], track_id)
            self.assertEqual(entry["source_pr"], source_pr)
            self.assertEqual(entry["artifact_type"], artifact_type)

    def test_06_all_source_artifact_paths_exist(self):
        for relative_path in EXPECTED_ARTIFACTS:
            with self.subTest(relative_path=relative_path):
                self.assertTrue((ROOT / relative_path).is_file())

    def test_07_all_sha256_digests_match_exact_file_bytes(self):
        for relative_path in EXPECTED_ARTIFACTS:
            with self.subTest(relative_path=relative_path):
                expected = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
                entry = self.artifact(self.fixture, relative_path)
                self.assertEqual(entry["digest_algorithm"], "sha256")
                self.assertEqual(entry["sha256"], expected)

    def test_08_source_artifact_digest_mismatch_fails(self):
        entry = self.fixture["source_artifact_manifest"][0]
        entry["sha256"] = "0" * 64
        result = self.assert_invalid(self.fixture)
        self.assertFalse(result["artifact_integrity_valid"])

    def test_09_missing_source_artifact_fails(self):
        self.fixture["source_artifact_manifest"].pop()
        result = self.assert_invalid(self.fixture)
        self.assertFalse(result["source_artifacts_present"])
        self.assertFalse(result["artifact_integrity_valid"])

    def test_10_wrong_track_assignment_fails(self):
        entry = self.fixture["source_artifact_manifest"][0]
        entry["track_id"] = "skill_admission"
        result = self.assert_invalid(self.fixture)
        self.assertFalse(result["artifact_integrity_valid"])

    def test_11_every_authority_owner_is_aaos(self):
        for track in self.fixture["source_track_manifest"]:
            self.assertEqual(track["retained_authority_owner"], "AAOS")
        fixture = copy.deepcopy(self.fixture)
        fixture["source_track_manifest"][0]["retained_authority_owner"] = "local_evaluator"
        result = self.assert_invalid(fixture)
        self.assertFalse(result["authority_boundaries_preserved"])

    def test_12_every_decision_proof_sealing_owner_is_aaos(self):
        for track in self.fixture["source_track_manifest"]:
            self.assertEqual(track["decision_proof_sealing_owner"], "AAOS")
        fixture = copy.deepcopy(self.fixture)
        fixture["source_track_manifest"][0]["decision_proof_sealing_owner"] = "workflow"
        result = self.assert_invalid(fixture)
        self.assertFalse(result["authority_boundaries_preserved"])

    def test_13_all_readiness_dimensions_exist(self):
        dimensions = self.fixture["readiness_dimensions"]
        self.assertEqual(len(dimensions), 20)
        self.assertEqual(set(index_by(dimensions, "dimension_id")), set(EXPECTED_DIMENSION_STATES))

    def test_14_baseline_readiness_dimension_states_are_correct(self):
        dimensions = index_by(self.fixture["readiness_dimensions"], "dimension_id")
        for dimension_id, status in EXPECTED_DIMENSION_STATES.items():
            with self.subTest(dimension_id=dimension_id):
                self.assertEqual(dimensions[dimension_id]["status"], status)
                self.assertFalse(dimensions[dimension_id]["authoritative_result"])

    def test_15_all_required_operational_checklist_items_exist(self):
        checklist = self.fixture["operational_checklist"]
        self.assertGreaterEqual(len(checklist), 36)
        ids = [item["check_id"] for item in checklist]
        self.assertEqual(len(ids), len(set(ids)))
        for number in range(1, 37):
            prefix = f"check_{number:02d}_"
            self.assertEqual(sum(item.startswith(prefix) for item in ids), 1, prefix)
        descriptions = "\n".join(item["description"].casefold() for item in checklist)
        for phrase in (
            "all six source tracks",
            "every expected source artifact",
            "every source artifact digest",
            "capability from permission",
            "public input as untrusted",
            "regulatory reference only",
            "heuristic evidence",
            "cannot create authority",
            "no network access",
            "v0.13.0 remains unreleased",
            "#201 remains open",
            "decision proof sealing remains aaos-owned",
        ):
            self.assertIn(phrase, descriptions)

    def test_16_external_state_inputs_remain_reviewer_confirmed(self):
        state = self.fixture["external_state_review_inputs"]
        self.assertEqual(state["tracker_issue"], "#201")
        self.assertEqual(state["tracker_expected_state"], "open")
        self.assertEqual(state["source_prs"], ["#202", "#204", "#205", "#206", "#208", "#210"])
        self.assertEqual(state["source_pr_expected_state"], "merged")
        self.assertEqual(state["source_issues"], ["#200", "#188", "#181", "#180", "#192"])
        self.assertEqual(state["source_issue_expected_state"], "closed_completed")
        self.assertEqual(state["verification_mode"], "reviewer_confirmed_external_state")
        self.assertFalse(state["verified_by_deterministic_evaluator"])
        self.assertTrue(state["reviewer_confirmation_required"])

    def test_17_evaluator_does_not_perform_github_or_network_access(self):
        imported = set()
        calls = set()
        for node in ast.walk(self.evaluator_tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call):
                calls.add(dotted_name(node.func))
        self.assertFalse(imported & {"ftplib", "github", "ghapi", "http", "requests", "socket", "urllib"})
        self.assertFalse(any(name.startswith(("requests.", "socket.", "urllib.", "http.")) for name in calls))

    def test_18_evaluator_does_not_import_source_evaluators(self):
        imported = set()
        for node in ast.walk(self.evaluator_tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        self.assertFalse(imported & SOURCE_EVALUATOR_MODULES)

    def test_19_evaluator_does_not_execute_workflows_or_skills(self):
        imported = set()
        calls = set()
        for node in ast.walk(self.evaluator_tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call):
                calls.add(dotted_name(node.func))
        self.assertFalse(imported & {"importlib", "runpy", "subprocess"})
        self.assertFalse(
            calls
            & {
                "eval",
                "exec",
                "compile",
                "__import__",
                "os.popen",
                "os.system",
                "subprocess.call",
                "subprocess.check_call",
                "subprocess.check_output",
                "subprocess.Popen",
                "subprocess.run",
            }
        )

    def test_20_verification_command_manifest_is_complete(self):
        commands = index_by(self.fixture["verification_command_manifest"], "command_id")
        self.assertEqual(set(commands), EXPECTED_COMMAND_IDS)
        self.assertIn("python -m json.tool", commands["validate_readiness_fixture_json"]["command"])
        self.assertIn("python -m py_compile", commands["compile_m14_evaluators"]["command"])
        self.assertIn("python -m py_compile", commands["compile_m14_tests"]["command"])
        for module in (
            "tests.test_voice_generation_policy_evaluator",
            "tests.test_public_issue_exfiltration_gate_evaluator",
            "tests.test_moda_ai_risk_mapping_evaluator",
            "tests.test_ai_authored_pr_provenance_evaluator",
            "tests.test_skill_admission_evaluator",
            "tests.test_m14_cross_control_authority_boundary_evaluator",
        ):
            self.assertIn(module, commands["run_merged_m14_targeted_tests"]["command"])
        self.assertIn("tests.test_m14_operational_readiness_evaluator", commands["run_operational_readiness_tests"]["command"])
        self.assertEqual(commands["git_diff_check"]["command"], "git diff --check")
        self.assertEqual(commands["confirm_changed_file_scope"]["command"], "git diff --name-only")
        self.assertTrue(self.evaluate()["verification_manifest_complete"])

    def test_21_verification_manifest_is_not_test_execution_evidence(self):
        for command in self.fixture["verification_command_manifest"]:
            self.assertFalse(command["executed_by_readiness_evaluator"])
        result = self.evaluate()
        self.assertNotIn("tests_executed_by_manifest", result["outputs"])
        self.assertTrue(result["verification_manifest_complete"])

    def test_22_outstanding_items_are_exactly_the_five_required_items(self):
        items = self.fixture["outstanding_completion_items"]
        self.assertEqual([item["item_id"] for item in items], EXPECTED_OUTSTANDING_ITEMS)
        for item in items:
            self.assertEqual(item["status"], "pending")
            self.assertTrue(item["not_performed_by_this_pr"])

    def test_23_outstanding_completion_sequence_is_correct(self):
        items = self.fixture["outstanding_completion_items"]
        self.assertEqual([item["sequence_order"] for item in items], [1, 2, 3, 4, 5])
        for index, item in enumerate(items):
            self.assertTrue(item["prerequisite"])
            if index:
                self.assertIn(items[index - 1]["item_id"], item["prerequisite"])
        self.assertTrue(self.evaluate()["outstanding_completion_items_valid"])

    def test_24_release_proof_linkage_remains_pending(self):
        item = self.outstanding(self.fixture, "release_proof_linkage")
        self.assertEqual(item["status"], "pending")
        self.assertEqual(
            self.dimension(self.fixture, "release_proof_linkage_status")["status"],
            "pending_next_stage",
        )

    def test_25_readme_future_status_path_remains_pending(self):
        item = self.outstanding(self.fixture, "future_readme_status_path")
        self.assertEqual(item["status"], "pending")
        self.assertFalse(self.fixture["readme_status_updated"])
        self.assertEqual(
            self.dimension(self.fixture, "readme_future_status_path")["status"],
            "pending_next_stage",
        )

    def test_26_tracker_201_remains_open_in_fixture_state(self):
        self.assertFalse(self.fixture["tracker_closed_by_fixture"])
        self.assertEqual(
            self.fixture["external_state_review_inputs"]["tracker_expected_state"],
            "open",
        )

    def test_27_v0_13_0_remains_unreleased(self):
        self.assertEqual(self.fixture["target_future_release"], "v0.13.0")
        self.assertFalse(self.fixture["future_release_tag_path"]["released"])
        self.assertFalse(self.fixture["release_file_created"])
        self.assertFalse(self.fixture["release_tag_created"])
        self.assertFalse(self.fixture["github_release_created"])

    def test_28_baseline_is_ready_for_release_proof_linkage(self):
        result = self.evaluate()
        self.assertTrue(result["valid"])
        self.assertTrue(result["ready_for_release_proof_linkage"])
        self.assertIn("ready_for_release_proof_linkage", result["outputs"])

    def test_29_baseline_is_not_ready_for_m14_completion_review(self):
        result = self.evaluate()
        self.assertFalse(result["ready_for_m14_completion_review"])

    def test_30_baseline_m14_complete_is_false(self):
        result = self.evaluate()
        self.assertFalse(result["m14_complete"])
        self.assertNotIn("m14_complete", result["outputs"])

    def test_31_missing_authority_boundary_fails(self):
        self.fixture["required_boundary_statements"].remove(
            "Decision Proof sealing remains AAOS-owned."
        )
        result = self.assert_invalid(self.fixture)
        self.assertFalse(result["authority_boundaries_preserved"])

    def test_32_missing_human_review_evidence_fails(self):
        dimension = self.dimension(self.fixture, "human_review_escalation_coverage")
        dimension["status"] = "blocked"
        dimension["observed_evidence"] = []
        result = self.assert_invalid(self.fixture)
        self.assertFalse(result["human_review_coverage_present"])

    def test_33_missing_fail_closed_recommendation_coverage_fails(self):
        dimension = self.dimension(self.fixture, "fail_closed_recommendation_coverage")
        dimension["status"] = "blocked"
        dimension["observed_evidence"] = []
        result = self.assert_invalid(self.fixture)
        self.assertFalse(result["fail_closed_recommendation_coverage_present"])

    def test_34_missing_rollback_recommendation_coverage_fails(self):
        dimension = self.dimension(self.fixture, "rollback_recommendation_coverage")
        dimension["status"] = "blocked"
        dimension["observed_evidence"] = []
        result = self.assert_invalid(self.fixture)
        self.assertFalse(result["rollback_recommendation_coverage_present"])

    def test_35_missing_trace_coverage_fails(self):
        dimension = self.dimension(self.fixture, "trace_evidence_coverage")
        dimension["status"] = "blocked"
        dimension["observed_evidence"] = []
        result = self.assert_invalid(self.fixture)
        self.assertFalse(result["trace_coverage_present"])

    def test_36_missing_replay_coverage_fails(self):
        dimension = self.dimension(self.fixture, "replay_evidence_coverage")
        dimension["status"] = "blocked"
        dimension["observed_evidence"] = []
        result = self.assert_invalid(self.fixture)
        self.assertFalse(result["replay_coverage_present"])

    def test_37_source_track_substitution_fails(self):
        track = self.track(self.fixture, "voice_runtime_policy")
        track["source_paths"][0] = "README.md"
        result = self.assert_invalid(self.fixture)
        self.assertFalse(result["source_track_coverage_complete"])

    def test_38_incomplete_verification_manifest_fails(self):
        self.fixture["verification_command_manifest"] = [
            command
            for command in self.fixture["verification_command_manifest"]
            if command["command_id"] != "run_operational_readiness_tests"
        ]
        result = self.assert_invalid(self.fixture)
        self.assertFalse(result["verification_manifest_complete"])

    def test_39_external_state_marked_machine_verified_fails(self):
        self.fixture["external_state_review_inputs"][
            "verified_by_deterministic_evaluator"
        ] = True
        result = self.assert_invalid(self.fixture)
        self.assertTrue(result["external_state_confirmation_required"])

    def test_40_release_proof_incorrectly_marked_complete_fails(self):
        item = self.outstanding(self.fixture, "release_proof_linkage")
        item["status"] = "complete"
        item["not_performed_by_this_pr"] = False
        result = self.assert_invalid(self.fixture)
        self.assertFalse(result["outstanding_completion_items_valid"])

    def test_41_readme_incorrectly_marked_updated_fails(self):
        self.fixture["readme_status_updated"] = True
        self.assert_invalid(self.fixture)

    def test_42_tracker_incorrectly_marked_closed_fails(self):
        self.fixture["tracker_closed_by_fixture"] = True
        self.assert_invalid(self.fixture)

    def test_43_release_incorrectly_marked_published_fails(self):
        self.fixture["future_release_tag_path"]["released"] = True
        self.fixture["release_tag_created"] = True
        self.fixture["github_release_created"] = True
        self.assert_invalid(self.fixture)

    def test_44_outstanding_completion_sequence_violation_fails(self):
        item = self.outstanding(self.fixture, "future_readme_status_path")
        item["status"] = "complete"
        item["not_performed_by_this_pr"] = False
        result = self.assert_invalid(self.fixture)
        self.assertFalse(result["outstanding_completion_items_valid"])

    def test_45_affirmative_decision_proof_sealing_claim_fails(self):
        self.fixture["simulated_outputs"] = {"decision_proof_sealed": True}
        result = self.assert_invalid(self.fixture)
        self.assertFalse(result["authority_boundaries_preserved"])

    def test_46_affirmative_authority_transfer_claim_fails(self):
        self.fixture["simulated_outputs"] = {"authority_transferred": True}
        result = self.assert_invalid(self.fixture)
        self.assertFalse(result["authority_boundaries_preserved"])

    def test_47_affirmative_risk_acceptance_claim_fails(self):
        self.fixture["simulated_outputs"] = {"risk_accepted": True}
        result = self.assert_invalid(self.fixture)
        self.assertFalse(result["authority_boundaries_preserved"])

    def test_48_explicit_negative_governance_evidence_remains_valid(self):
        self.fixture["simulated_outputs"] = {
            "m14_complete": False,
            "release_tag_created": False,
            "github_release_created": False,
            "decision_proof_sealed": False,
            "risk_accepted": "denied",
            "authority_transferred": "not_transferred",
            "tracker_closed": False,
        }
        result = self.evaluate()
        self.assertTrue(result["valid"])
        self.assertTrue(result["authority_boundaries_preserved"])

    def test_49_negative_outer_container_does_not_hide_nested_affirmative_claim(self):
        self.fixture["simulated_outputs"] = {
            "decision_proof_sealed": False,
            "nested": {"authority_transferred": True},
        }
        result = self.assert_invalid(self.fixture)
        self.assertFalse(result["authority_boundaries_preserved"])

    def test_50_evaluator_attempting_m14_completion_fails(self):
        self.fixture["simulated_outputs"] = {"m14_complete": True}
        result = self.assert_invalid(self.fixture)
        self.assertFalse(result["m14_complete"])
        self.assertFalse(result["ready_for_m14_completion_review"])

    def test_51_readiness_cases_cover_all_required_scenarios(self):
        cases = self.fixture["readiness_cases"]
        case_ids = [case["case_id"] for case in cases]
        self.assertGreaterEqual(len(cases), 35)
        self.assertEqual(len(case_ids), len(set(case_ids)))
        for number in range(1, 36):
            prefix = f"case_{number:02d}_"
            self.assertEqual(sum(case_id.startswith(prefix) for case_id in case_ids), 1, prefix)

    def test_52_required_boundary_statements_are_exact(self):
        self.assertEqual(set(self.fixture["required_boundary_statements"]), REQUIRED_BOUNDARY_STATEMENTS)

    def test_53_allowed_and_forbidden_output_catalogs_are_complete_and_disjoint(self):
        allowed = set(self.fixture["allowed_evaluator_outputs"])
        forbidden = set(self.fixture["forbidden_evaluator_outputs"])
        self.assertFalse(allowed & forbidden)
        self.assertTrue(
            {
                "m14_operational_readiness_valid",
                "m14_operational_readiness_invalid",
                "external_state_confirmation_required",
                "release_proof_linkage_pending",
                "readme_status_path_pending",
                "ready_for_release_proof_linkage",
                "not_ready",
                "escalation_required",
            }
            <= allowed
        )
        self.assertTrue(
            {
                "tests_executed_by_manifest",
                "github_state_machine_verified",
                "release_proof_approved",
                "m14_completion_approved",
                "tracker_201_closed",
                "v0_13_0_released",
                "decision_proof_sealed",
                "authority_transferred",
                "final_governance_judgment",
                "m14_complete",
                "closes_201",
            }
            <= forbidden
        )

    def test_54_artifact_integrity_policy_is_fail_closed(self):
        policy = self.fixture["artifact_integrity_policy"]
        required_rules = {
            "exact_relative_path_binding_required",
            "sha256_binding_required",
            "track_to_pr_binding_required",
            "artifact_type_binding_required",
            "mutable_branch_name_not_sole_identity",
            "repository_url_not_sole_identity",
            "artifact_name_not_sole_identity",
            "digest_drift_blocks_readiness",
            "missing_source_artifact_blocks_readiness",
            "unexpected_source_track_substitution_blocks_readiness",
        }
        self.assertTrue(required_rules <= set(policy))
        self.assertTrue(all(policy[key] is True for key in required_rules))

    def test_55_source_artifacts_are_required_and_never_executable(self):
        for artifact in self.fixture["source_artifact_manifest"]:
            self.assertTrue(artifact["required"])
            self.assertEqual(artifact["observed_on_branch"], "main")
            self.assertFalse(artifact["executable_by_readiness_evaluator"])
            self.assertTrue(artifact["evidence_role"])

    def test_56_result_contains_required_fields_and_allowed_outputs_only(self):
        result = self.evaluate()
        self.assertTrue(REQUIRED_RESULT_FIELDS <= set(result))
        self.assertTrue(set(result["outputs"]) <= set(self.fixture["allowed_evaluator_outputs"]))
        self.assertFalse(set(result["outputs"]) & set(self.fixture["forbidden_evaluator_outputs"]))

    def test_57_public_evaluator_apis_return_valid_baseline(self):
        loaded = load_fixture(FIXTURE_PATH)
        self.assertEqual(loaded, self.baseline)
        validated = validate_m14_operational_readiness(
            copy.deepcopy(loaded), repository_root=ROOT
        )
        evaluated_file = evaluate_file(FIXTURE_PATH, repository_root=ROOT)
        self.assertTrue(validated["valid"])
        self.assertTrue(evaluated_file["valid"])

    def test_58_source_track_entries_have_complete_contract(self):
        fields = {
            "track_id",
            "source_pr",
            "component_role",
            "implementation_state",
            "source_paths",
            "expected_control_capabilities",
            "required_boundary_statements",
            "readiness_evidence_classes",
            "reviewer_confirmation_required",
            "retained_authority_owner",
            "decision_proof_sealing_owner",
        }
        evidence_classes = set()
        for track in self.fixture["source_track_manifest"]:
            self.assertTrue(fields <= set(track))
            self.assertEqual(track["implementation_state"], "merged_source_artifacts_present")
            self.assertTrue(track["reviewer_confirmation_required"])
            evidence_classes.update(track["readiness_evidence_classes"])
        self.assertTrue(
            {
                "human_review",
                "fail_closed_recommendation",
                "rollback_recommendation",
                "trace_evidence",
                "replay_evidence",
                "deterministic_test",
            }
            <= evidence_classes
        )

    def test_59_operational_checklist_entries_have_complete_contract(self):
        fields = {
            "check_id",
            "description",
            "category",
            "required",
            "evidence_references",
            "expected_status",
            "blocking_if_failed",
            "governance_boundary",
        }
        for item in self.fixture["operational_checklist"]:
            self.assertTrue(fields <= set(item))
            self.assertTrue(item["required"])
            self.assertTrue(item["evidence_references"])
            self.assertTrue(item["governance_boundary"])

    def test_60_readiness_dimension_entries_have_complete_contract(self):
        fields = {
            "dimension_id",
            "status",
            "required_evidence",
            "observed_evidence",
            "blocking_conditions",
            "reviewer_confirmation_required",
            "authoritative_result",
        }
        allowed_statuses = {
            "ready",
            "conditionally_ready",
            "pending_next_stage",
            "blocked",
            "invalid",
        }
        for dimension in self.fixture["readiness_dimensions"]:
            self.assertTrue(fields <= set(dimension))
            self.assertIn(dimension["status"], allowed_statuses)
            self.assertFalse(dimension["authoritative_result"])

    def test_61_verification_commands_have_complete_nonexecuting_contract(self):
        fields = {
            "command_id",
            "command",
            "verification_scope",
            "expected_exit_code",
            "expected_result",
            "evidence_recording_requirement",
            "executed_by_readiness_evaluator",
        }
        for command in self.fixture["verification_command_manifest"]:
            self.assertTrue(fields <= set(command))
            self.assertEqual(command["expected_exit_code"], 0)
            self.assertFalse(command["executed_by_readiness_evaluator"])

    def test_62_outstanding_items_have_complete_nonperforming_contract(self):
        fields = {
            "item_id",
            "status",
            "sequence_order",
            "prerequisite",
            "authorized_actor",
            "completion_evidence_required",
            "not_performed_by_this_pr",
        }
        for item in self.fixture["outstanding_completion_items"]:
            self.assertTrue(fields <= set(item))
            self.assertEqual(item["status"], "pending")
            self.assertTrue(item["authorized_actor"])
            self.assertTrue(item["completion_evidence_required"])
            self.assertTrue(item["not_performed_by_this_pr"])

    def test_63_missing_source_track_blocks_readiness(self):
        self.fixture["source_track_manifest"] = [
            track
            for track in self.fixture["source_track_manifest"]
            if track["track_id"] != "cross_control_authority_boundary"
        ]
        result = self.assert_invalid(self.fixture)
        self.assertFalse(result["source_track_coverage_complete"])

    def test_64_source_pr_linkage_mismatch_blocks_readiness(self):
        entry = self.fixture["source_artifact_manifest"][0]
        entry["source_pr"] = "#208"
        result = self.assert_invalid(self.fixture)
        self.assertFalse(result["artifact_integrity_valid"])

    def test_65_missing_deterministic_test_artifact_blocks_readiness(self):
        missing_path = "tests/test_m14_cross_control_authority_boundary_evaluator.py"
        self.fixture["source_artifact_manifest"] = [
            artifact
            for artifact in self.fixture["source_artifact_manifest"]
            if artifact["relative_path"] != missing_path
        ]
        result = self.assert_invalid(self.fixture)
        self.assertFalse(result["source_artifacts_present"])
        self.assertFalse(result["artifact_integrity_valid"])


if __name__ == "__main__":
    unittest.main()
