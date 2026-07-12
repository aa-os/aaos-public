import ast
import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.m14_cross_control_authority_boundary_evaluator import (  # noqa: E402
    detect_authority_violations,
    evaluate_cross_control_case,
    evaluate_m14_cross_control_authority_boundary,
)


FIXTURE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m14-cross-control-authority-boundary-regression-fixtures.json"
)
EVALUATOR_PATH = (
    ROOT / "runtime" / "m14_cross_control_authority_boundary_evaluator.py"
)
TEST_PATH = Path(__file__).resolve()

INTENDED_FILES = {
    "examples/public-integration-pack-pilot/"
    "m14-cross-control-authority-boundary-regression-fixtures.json",
    "runtime/m14_cross_control_authority_boundary_evaluator.py",
    "tests/test_m14_cross_control_authority_boundary_evaluator.py",
}

COMPONENTS = {
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
            "docs/public-integration-pack/"
            "m14-moda-ai-risk-framework-mapping.md",
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
}

MATRIX_FIELDS = {
    "component_id",
    "source_pr",
    "component_role",
    "source_paths",
    "input_evidence_classes",
    "permitted_operations",
    "advisory_outputs",
    "prohibited_operations",
    "prohibited_authority_claims",
    "escalation_route",
    "retained_authority_owner",
    "decision_proof_sealing_owner",
}

PERMITTED_OPERATIONS = {
    "capture",
    "inspect",
    "classify",
    "validate structure",
    "detect risk",
    "detect policy mismatch",
    "block output",
    "recommend fail-closed",
    "recommend rollback",
    "request human review",
    "request reviewer routing",
    "preserve trace",
    "preserve replay metadata",
    "report readiness for review",
}

COMPOSITION_RULES = {
    "no_authority_by_aggregation",
    "capability_is_not_permission",
    "consent_evidence_is_not_approval",
    "provenance_is_not_identity_proof",
    "regulatory_mapping_is_not_legal_approval",
    "taxonomy_coverage_is_not_compliance_certification",
    "signature_is_not_governance_approval",
    "scan_is_not_risk_acceptance",
    "benchmark_is_not_deployment_approval",
    "policy_gate_pass_is_scope_limited",
    "ready_for_review_is_not_approval",
    "reviewer_routing_is_not_review_approval",
    "workflow_success_is_not_merge_approval",
    "public_output_gate_pass_is_not_disclosure_approval",
    "fail_closed_recommended_is_not_fail_closed_executed",
    "rollback_recommended_is_not_rollback_executed",
    "human_review_required_is_not_audit_closure",
    "replay_ready_is_not_decision_proof_sealing",
    "evidence_complete_is_not_decision_proof_sealing",
    "most_restrictive_applicable_control_is_preserved",
    "authority_cannot_be_transferred_by_field_renaming",
    "forbidden_claims_remain_forbidden_when_nested",
    "forbidden_claims_remain_forbidden_when_multiple_components_agree",
    "decision_proof_sealing_remains_aaos_owned",
    "aaos_remains_decision_sovereignty_layer",
}

BOUNDARY_STATEMENTS = {
    "Multiple non-authoritative outputs do not aggregate into governance authority.",
    "Five passed gates are not final approval.",
    "Evidence accumulation does not create authority by aggregation.",
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
}

ALLOWED_OUTPUTS = {
    "m14_authority_boundary_fixture_valid",
    "m14_authority_boundary_fixture_invalid",
    "cross_control_boundary_valid",
    "cross_control_boundary_invalid",
    "component_boundary_valid",
    "component_boundary_invalid",
    "composition_not_authoritative",
    "most_restrictive_control_preserved",
    "human_review_required",
    "fail_closed_recommended",
    "rollback_recommended",
    "source_boundary_drift_detected",
    "authority_violation_detected",
    "ready_for_m14_readiness_review",
    "not_ready",
    "escalation_required",
}

FORBIDDEN_OUTPUTS = {
    "voice_clone_approved",
    "impersonation_approved",
    "public_disclosure_approved",
    "regulated_deployment_approved",
    "legal_approval_granted",
    "compliance_certified",
    "risk_accepted",
    "identity_proven",
    "review_approved",
    "merge_approved",
    "installation_approved",
    "skill_execution_approved",
    "deployment_approved",
    "final_action_approved",
    "fail_closed_executed",
    "rollback_executed",
    "audit_closed",
    "waiver_granted",
    "decision_proof_verified",
    "decision_proof_sealed",
    "sealed_by_voice_runtime",
    "sealed_by_output_gate",
    "sealed_by_regulatory_mapping",
    "sealed_by_provenance_workflow",
    "sealed_by_skill_registry",
    "sealed_by_evaluator",
    "authority_transferred",
    "final_governance_judgment",
    "m14_complete",
    "v0_13_0_released",
    "closes_201",
}

RESULT_SEMANTIC_FIELDS = {
    "component_results",
    "effective_control_result",
    "human_review_required",
    "fail_closed_recommended",
    "rollback_recommended",
    "authority_violation_detected",
    "source_boundary_drift_detected",
    "ready_for_m14_readiness_review",
    "outputs",
    "findings",
}

SOURCE_MODULES = {
    "runtime.voice_generation_policy_evaluator",
    "runtime.public_issue_exfiltration_gate_evaluator",
    "runtime.moda_ai_risk_mapping_evaluator",
    "runtime.ai_authored_pr_provenance_evaluator",
    "runtime.skill_admission_evaluator",
}


def load_fixture():
    with FIXTURE_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def manifest_index(fixture):
    return {
        entry["component_id"]: entry
        for entry in fixture["source_artifact_manifest"]
    }


def matrix_index(fixture):
    return {
        entry["component_id"]: entry
        for entry in fixture["component_authority_matrix"]
    }


def load_source_artifacts(fixture):
    artifacts = {}
    for entry in fixture["source_artifact_manifest"]:
        for relative_path in entry["source_paths"]:
            artifacts[relative_path] = (ROOT / relative_path).read_text(encoding="utf-8")
    return artifacts


def result_findings(result):
    return set(result.get("findings", []))


def component_result_index(result):
    component_results = result["component_results"]
    if isinstance(component_results, dict):
        return component_results
    return {entry["component_id"]: entry for entry in component_results}


def preserved_component_ids(result):
    for key in (
        "preserved_component_ids",
        "effective_result_component_ids",
        "effective_control_component_ids",
    ):
        if isinstance(result.get(key), list):
            return set(result[key])
    effective = result.get("effective_control_result")
    if isinstance(effective, dict):
        for key in ("preserved_component_ids", "component_ids", "source_components"):
            if isinstance(effective.get(key), list):
                return set(effective[key])
    return set()


class M14CrossControlAuthorityBoundaryEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = load_fixture()
        cls.source_artifacts = load_source_artifacts(cls.fixture)
        cls.evaluator_text = EVALUATOR_PATH.read_text(encoding="utf-8")

    def fixture_case(self, number):
        prefix = f"case_{number:02d}_"
        matches = [
            case
            for case in self.fixture["cross_control_cases"]
            if case["case_id"].startswith(prefix)
        ]
        self.assertEqual(len(matches), 1, prefix)
        return matches[0]

    def evaluate_fixture(self, fixture=None, source_artifacts=None):
        return evaluate_m14_cross_control_authority_boundary(
            copy.deepcopy(self.fixture if fixture is None else fixture),
            copy.deepcopy(
                self.source_artifacts
                if source_artifacts is None
                else source_artifacts
            ),
        )

    def evaluate_case(self, number):
        case = self.fixture_case(number)
        return evaluate_cross_control_case(
            copy.deepcopy(self.fixture),
            case["case_id"],
            copy.deepcopy(self.source_artifacts),
        )

    def assert_result_vocabulary(self, result):
        outputs = set(result["outputs"])
        self.assertLessEqual(outputs, ALLOWED_OUTPUTS)
        self.assertFalse(outputs & FORBIDDEN_OUTPUTS)

    def assert_case_matches_expected(self, number):
        case = self.fixture_case(number)
        result = self.evaluate_case(number)
        expected = case["expected"]
        self.assertLessEqual(RESULT_SEMANTIC_FIELDS, set(result))
        for key, value in expected.items():
            if key == "required_outputs":
                self.assertLessEqual(set(value), set(result["outputs"]))
            elif key == "required_findings":
                self.assertLessEqual(set(value), result_findings(result))
            else:
                self.assertIn(key, result)
                self.assertEqual(result[key], value, f"{case['case_id']}:{key}")
        self.assert_result_vocabulary(result)
        return result

    def assert_authority_case(self, number):
        result = self.assert_case_matches_expected(number)
        self.assertTrue(result["authority_violation_detected"])
        self.assertIn("authority_violation_detected", result["outputs"])
        self.assertFalse(result["ready_for_m14_readiness_review"])
        return result

    def assert_source_drift_for(self, component_id):
        entry = manifest_index(self.fixture)[component_id]
        requirement = entry["source_boundary_requirements"][0]
        artifacts = copy.deepcopy(self.source_artifacts)
        for relative_path in entry["source_paths"]:
            artifacts[relative_path] = artifacts[relative_path].replace(
                requirement, "source boundary intentionally removed"
            )
        result = self.evaluate_fixture(source_artifacts=artifacts)
        self.assertTrue(result["source_boundary_drift_detected"])
        self.assertIn("source_boundary_drift_detected", result["outputs"])
        self.assertFalse(result["ready_for_m14_readiness_review"])
        return result

    def test_01_valid_top_level_m14_active_work_state(self):
        self.assertEqual(self.fixture["fixture_status"], "m14_active_work_not_complete")
        self.assertEqual(self.fixture["tracker_issue"], "#201")
        self.assertEqual(self.fixture["tracker_issue_linkage"], "Refs #201")
        self.assertEqual(
            self.fixture["authority_boundary_scope"],
            "cross_control_composition_regression",
        )
        self.assertEqual(
            self.fixture["m14_completion_status"], "active_work_not_complete"
        )

    def test_02_exact_three_changed_file_scope(self):
        self.assertEqual(set(self.fixture["intended_files"]), INTENDED_FILES)

    def test_03_all_five_components_represented(self):
        self.assertEqual(set(manifest_index(self.fixture)), set(COMPONENTS))
        self.assertEqual(set(matrix_index(self.fixture)), set(COMPONENTS))

    def test_04_all_source_pr_references_correct(self):
        expected_top = {
            "related_voice_runtime_pr": "#202",
            "related_public_output_gate_pr": "#204",
            "related_moda_mapping_pr": "#205",
            "related_ai_pr_provenance_pr": "#206",
            "related_skill_admission_pr": "#208",
        }
        for field, value in expected_top.items():
            self.assertEqual(self.fixture[field], value)
        for component_id, expected in COMPONENTS.items():
            self.assertEqual(
                manifest_index(self.fixture)[component_id]["source_pr"],
                expected["source_pr"],
            )

    def test_05_source_artifact_manifest_complete(self):
        entries = manifest_index(self.fixture)
        for component_id, expected in COMPONENTS.items():
            entry = entries[component_id]
            self.assertEqual(entry["component_role"], expected["component_role"])
            self.assertEqual(set(entry["source_paths"]), expected["source_paths"])
            self.assertTrue(entry["source_boundary_requirements"])

    def test_06_component_authority_matrices_complete(self):
        for entry in self.fixture["component_authority_matrix"]:
            self.assertLessEqual(MATRIX_FIELDS, set(entry))
            for field in MATRIX_FIELDS - {
                "retained_authority_owner",
                "decision_proof_sealing_owner",
            }:
                self.assertTrue(entry[field], f"{entry['component_id']}:{field}")

    def test_07_retained_authority_owner_is_aaos_for_every_component(self):
        for entry in self.fixture["component_authority_matrix"]:
            self.assertEqual(entry["retained_authority_owner"], "AAOS")

    def test_08_sealing_owner_is_aaos_for_every_component(self):
        for entry in self.fixture["component_authority_matrix"]:
            self.assertEqual(entry["decision_proof_sealing_owner"], "AAOS")

    def test_09_all_composition_rules_present(self):
        self.assertEqual(set(self.fixture["composition_rules"]), COMPOSITION_RULES)

    def test_10_valid_baseline_is_ready_for_m14_readiness_review(self):
        result = self.evaluate_fixture()
        self.assertTrue(result["ready_for_m14_readiness_review"])
        self.assertFalse(result["authority_violation_detected"])
        self.assertFalse(result["source_boundary_drift_detected"])
        self.assertIn("ready_for_m14_readiness_review", result["outputs"])
        self.assert_result_vocabulary(result)

    def test_11_baseline_does_not_declare_m14_complete(self):
        self.assertEqual(
            self.fixture["m14_completion_status"], "active_work_not_complete"
        )
        self.assertNotIn("m14_complete", self.evaluate_fixture()["outputs"])

    def test_12_baseline_does_not_release_v0_13_0(self):
        self.assertEqual(self.fixture["target_future_release"], "v0.13.0")
        self.assertFalse(self.fixture["future_release_tag_path"]["released"])
        self.assertNotIn("v0_13_0_released", self.evaluate_fixture()["outputs"])

    def test_13_baseline_does_not_close_tracker_201(self):
        self.assertEqual(self.fixture["tracker_issue_linkage"], "Refs #201")
        self.assertNotIn("closes_201", self.evaluate_fixture()["outputs"])

    def test_14_five_pass_results_do_not_create_final_approval(self):
        result = self.assert_case_matches_expected(11)
        self.assertIn("final_governance_judgment", " ".join(result["findings"]))
        self.assertNotIn("final_action_approved", result["outputs"])

    def test_15_five_pass_results_do_not_create_decision_proof_sealing(self):
        result = self.assert_case_matches_expected(12)
        self.assertTrue(result["authority_violation_detected"])
        self.assertNotIn("decision_proof_sealed", result["outputs"])

    def test_16_consent_plus_voice_gate_pass_does_not_approve_cloning(self):
        result = self.assert_authority_case(2)
        self.assertNotIn("voice_clone_approved", result["outputs"])

    def test_17_output_gate_pass_does_not_approve_disclosure(self):
        result = self.assert_authority_case(4)
        self.assertNotIn("public_disclosure_approved", result["outputs"])

    def test_18_moda_mapping_does_not_grant_legal_approval(self):
        result = self.assert_authority_case(5)
        self.assertNotIn("legal_approval_granted", result["outputs"])

    def test_19_provenance_detection_does_not_prove_identity(self):
        result = self.assert_authority_case(7)
        self.assertNotIn("identity_proven", result["outputs"])

    def test_20_reviewer_routing_does_not_approve_review(self):
        result = self.assert_authority_case(7)
        self.assertNotIn("review_approved", result["outputs"])

    def test_21_workflow_success_does_not_approve_merge(self):
        result = self.assert_authority_case(8)
        self.assertNotIn("merge_approved", result["outputs"])

    def test_22_skill_admission_does_not_approve_installation(self):
        result = self.assert_authority_case(10)
        self.assertNotIn("installation_approved", result["outputs"])

    def test_23_signature_plus_scan_does_not_accept_risk(self):
        result = self.assert_authority_case(9)
        self.assertNotIn("risk_accepted", result["outputs"])

    def test_24_benchmark_does_not_approve_deployment(self):
        result = self.assert_authority_case(9)
        self.assertNotIn("deployment_approved", result["outputs"])

    def test_25_fail_closed_recommendation_does_not_execute_fail_closed(self):
        result = self.assert_authority_case(13)
        self.assertTrue(result["fail_closed_recommended"])
        self.assertNotIn("fail_closed_executed", result["outputs"])

    def test_26_rollback_recommendation_does_not_execute_rollback(self):
        result = self.assert_authority_case(14)
        self.assertTrue(result["rollback_recommended"])
        self.assertNotIn("rollback_executed", result["outputs"])

    def test_27_human_review_requirement_does_not_close_audit(self):
        result = self.assert_authority_case(15)
        self.assertTrue(result["human_review_required"])
        self.assertNotIn("audit_closed", result["outputs"])

    def test_28_evidence_complete_does_not_seal_decision_proof(self):
        result = self.assert_authority_case(16)
        self.assertNotIn("decision_proof_sealed", result["outputs"])

    def test_29_replay_ready_does_not_seal_decision_proof(self):
        result = self.assert_authority_case(16)
        self.assertNotIn("decision_proof_verified", result["outputs"])

    def test_30_nested_forbidden_claim_is_detected(self):
        result = self.assert_authority_case(17)
        self.assertTrue(result_findings(result))

    def test_31_renamed_authority_transfer_claim_is_detected(self):
        result = self.assert_authority_case(18)
        self.assertTrue(
            any("authority" in finding for finding in result["findings"])
        )
        self.assertTrue(
            any("renamed_approval" in finding for finding in result["findings"])
        )

    def test_32_permissive_result_cannot_override_blocking_result(self):
        result = self.assert_case_matches_expected(19)
        self.assertEqual(result["effective_control_result"], "blocked")
        self.assertIn("most_restrictive_control_preserved", result["outputs"])

    def test_33_most_restrictive_result_is_preserved(self):
        result = self.assert_case_matches_expected(20)
        self.assertEqual(result["effective_control_result"], "blocked")
        self.assertTrue(preserved_component_ids(result))

    def test_34_missing_component_fails(self):
        result = self.assert_case_matches_expected(21)
        self.assertFalse(result["ready_for_m14_readiness_review"])
        self.assertIn("not_ready", result["outputs"])

    def test_35_missing_source_path_fails(self):
        result = self.assert_case_matches_expected(22)
        self.assertFalse(result["ready_for_m14_readiness_review"])
        self.assertTrue(result["source_boundary_drift_detected"])

    def test_36_missing_boundary_statement_causes_source_boundary_drift(self):
        result = self.assert_source_drift_for("voice_runtime_policy")
        self.assertTrue(
            any("voice_runtime_policy" in finding for finding in result["findings"])
        )

    def test_37_component_claiming_undeclared_authority_fails(self):
        result = self.assert_case_matches_expected(23)
        self.assertTrue(result["authority_violation_detected"])

    def test_38_component_claiming_local_sealing_ownership_fails(self):
        result = self.assert_case_matches_expected(24)
        self.assertTrue(result["authority_violation_detected"])

    def test_39_evaluator_attempting_authority_transfer_fails(self):
        self.assert_authority_case(17)

    def test_40_evaluator_attempting_final_governance_judgment_fails(self):
        self.assert_authority_case(11)

    def test_41_evaluator_attempting_decision_proof_sealing_fails(self):
        self.assert_authority_case(12)

    def test_42_evaluator_attempting_m14_completion_fails(self):
        self.assert_authority_case(26)

    def test_43_evaluator_attempting_v0_13_0_release_fails(self):
        self.assert_authority_case(27)

    def test_44_evaluator_attempting_to_close_tracker_201_fails(self):
        self.assert_authority_case(25)

    def test_45_valid_case_is_ready_but_not_complete(self):
        result = self.assert_case_matches_expected(28)
        self.assertTrue(result["ready_for_m14_readiness_review"])
        self.assertNotIn("m14_complete", result["outputs"])

    def test_46_fixture_has_exactly_28_unique_cases(self):
        cases = self.fixture["cross_control_cases"]
        case_ids = [case["case_id"] for case in cases]
        self.assertEqual(len(cases), 28)
        self.assertEqual(len(case_ids), len(set(case_ids)))
        self.assertEqual(
            {case_id.split("_", 2)[1] for case_id in case_ids},
            {f"{number:02d}" for number in range(1, 29)},
        )

    def test_47_every_case_matches_its_expected_core(self):
        for number in range(1, 29):
            with self.subTest(number=number):
                self.assert_case_matches_expected(number)

    def test_48_allowed_output_vocabulary_is_exact(self):
        self.assertEqual(set(self.fixture["allowed_evaluator_outputs"]), ALLOWED_OUTPUTS)

    def test_49_forbidden_output_vocabulary_is_exact(self):
        self.assertEqual(
            set(self.fixture["forbidden_evaluator_outputs"]), FORBIDDEN_OUTPUTS
        )

    def test_50_baseline_outputs_are_allowed_and_non_authoritative(self):
        result = self.evaluate_fixture()
        self.assert_result_vocabulary(result)
        self.assertIn("composition_not_authoritative", result["outputs"])

    def test_51_all_case_outputs_are_allowed_and_disjoint_from_forbidden(self):
        for number in range(1, 29):
            with self.subTest(number=number):
                self.assert_result_vocabulary(self.evaluate_case(number))

    def test_52_required_boundary_statements_are_exact(self):
        self.assertEqual(
            set(self.fixture["required_boundary_statements"]), BOUNDARY_STATEMENTS
        )

    def test_54_every_manifest_source_path_is_loaded_as_text(self):
        expected_paths = set().union(
            *(entry["source_paths"] for entry in self.fixture["source_artifact_manifest"])
        )
        self.assertEqual(set(self.source_artifacts), expected_paths)
        self.assertTrue(all(isinstance(value, str) for value in self.source_artifacts.values()))

    def test_55_provenance_workflow_is_read_as_inert_text_data(self):
        workflow_path = ".github/workflows/m14-ai-pr-provenance.yml"
        self.assertIn(workflow_path, self.source_artifacts)
        self.assertIsInstance(self.source_artifacts[workflow_path], str)
        self.assertTrue(self.source_artifacts[workflow_path].strip())

    def test_56_test_module_imports_no_existing_source_evaluator(self):
        tree = ast.parse(TEST_PATH.read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        self.assertFalse(imported & SOURCE_MODULES)

    def test_57_new_evaluator_imports_standard_library_only(self):
        tree = ast.parse(self.evaluator_text)
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        self.assertLessEqual(imports, sys.stdlib_module_names)

    def test_58_new_evaluator_has_no_network_shell_or_dynamic_execution_path(self):
        tree = ast.parse(self.evaluator_text)
        forbidden_imports = {
            "asyncio",
            "ftplib",
            "http",
            "requests",
            "socket",
            "subprocess",
            "urllib",
        }
        imported = set()
        call_names = set()

        def dotted_name(node):
            parts = []
            while isinstance(node, ast.Attribute):
                parts.append(node.attr)
                node = node.value
            if isinstance(node, ast.Name):
                parts.append(node.id)
            return ".".join(reversed(parts))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call):
                call_names.add(dotted_name(node.func))

        self.assertFalse(imported & forbidden_imports)
        self.assertFalse(
            call_names
            & {
                "eval",
                "exec",
                "compile",
                "__import__",
                "open",
                "Path.open",
                "Path.read_text",
                "os.popen",
                "os.system",
                "subprocess.call",
                "subprocess.check_call",
                "subprocess.check_output",
                "subprocess.Popen",
                "subprocess.run",
            }
        )

    def test_59_source_boundary_requirements_are_canonical_across_each_group(self):
        for entry in self.fixture["source_artifact_manifest"]:
            combined = "\n".join(
                self.source_artifacts[path] for path in entry["source_paths"]
            )
            for requirement in entry["source_boundary_requirements"]:
                with self.subTest(
                    component_id=entry["component_id"], requirement=requirement
                ):
                    self.assertIn(requirement, combined)

    def test_60_missing_source_artifact_mapping_detects_drift(self):
        artifacts = copy.deepcopy(self.source_artifacts)
        missing_path = next(iter(COMPONENTS["skill_admission"]["source_paths"]))
        artifacts.pop(missing_path)
        result = self.evaluate_fixture(source_artifacts=artifacts)
        self.assertTrue(result["source_boundary_drift_detected"])
        self.assertFalse(result["ready_for_m14_readiness_review"])

    def test_61_voice_source_boundary_drift_is_detected(self):
        self.assert_source_drift_for("voice_runtime_policy")

    def test_62_public_output_source_boundary_drift_is_detected(self):
        self.assert_source_drift_for("public_output_exfiltration_gate")

    def test_63_moda_source_boundary_drift_is_detected(self):
        self.assert_source_drift_for("moda_risk_mapping")

    def test_64_provenance_source_boundary_drift_is_detected(self):
        self.assert_source_drift_for("ai_pr_provenance")

    def test_65_skill_admission_source_boundary_drift_is_detected(self):
        self.assert_source_drift_for("skill_admission")

    def test_66_forbidden_claim_inside_nested_list_is_detected(self):
        findings = detect_authority_violations(
            {"nested_evidence": [{"claims": ["decision_proof_sealed"]}]}
        )
        self.assertTrue(any("decision_proof_sealed" in item for item in findings))

    def test_67_forbidden_claim_inside_arbitrary_nested_dictionary_is_detected(self):
        findings = detect_authority_violations(
            {"arbitrary": {"deeper": {"outcome": "public_disclosure_approved"}}}
        )
        self.assertTrue(
            any("public_disclosure_approved" in item for item in findings)
        )

    def test_68_forbidden_claim_inside_recommendation_field_is_detected(self):
        findings = detect_authority_violations(
            {"recommendation": {"next_state": "fail_closed_executed"}}
        )
        self.assertTrue(any("fail_closed_executed" in item for item in findings))

    def test_69_forbidden_claim_inside_reviewer_state_is_detected(self):
        findings = detect_authority_violations(
            {"reviewer_state": [{"result": "review_approved"}]}
        )
        self.assertTrue(any("review_approved" in item for item in findings))

    def test_70_forbidden_claim_inside_registry_state_is_detected(self):
        findings = detect_authority_violations(
            {"registry_state": {"decision": "installation_approved"}}
        )
        self.assertTrue(any("installation_approved" in item for item in findings))

    def test_71_component_results_represent_all_five_components(self):
        results = component_result_index(self.evaluate_fixture())
        self.assertEqual(set(results), set(COMPONENTS))

    def test_72_effective_block_result_identifies_preserved_components(self):
        result = self.evaluate_case(20)
        self.assertEqual(result["effective_control_result"], "blocked")
        self.assertTrue(preserved_component_ids(result))
        self.assertLessEqual(preserved_component_ids(result), set(COMPONENTS))

    def test_73_human_review_requirement_is_sticky(self):
        result = self.evaluate_case(15)
        self.assertTrue(result["human_review_required"])
        self.assertIn("human_review_required", result["outputs"])

    def test_74_fail_closed_recommendation_is_sticky_but_not_execution(self):
        result = self.evaluate_case(13)
        self.assertTrue(result["fail_closed_recommended"])
        self.assertIn("fail_closed_recommended", result["outputs"])
        self.assertNotIn("fail_closed_executed", result["outputs"])

    def test_75_rollback_recommendation_is_sticky_but_not_execution(self):
        result = self.evaluate_case(14)
        self.assertTrue(result["rollback_recommended"])
        self.assertIn("rollback_recommended", result["outputs"])
        self.assertNotIn("rollback_executed", result["outputs"])

    def test_76_readiness_requires_all_five_complete_source_groups(self):
        artifacts = copy.deepcopy(self.source_artifacts)
        for path in COMPONENTS["voice_runtime_policy"]["source_paths"]:
            artifacts.pop(path)
        result = self.evaluate_fixture(source_artifacts=artifacts)
        self.assertFalse(result["ready_for_m14_readiness_review"])

    def test_77_component_operations_are_scope_bounded(self):
        for entry in self.fixture["component_authority_matrix"]:
            self.assertLessEqual(set(entry["permitted_operations"]), PERMITTED_OPERATIONS)

    def test_78_component_permitted_and_prohibited_operations_are_disjoint(self):
        for entry in self.fixture["component_authority_matrix"]:
            self.assertFalse(
                set(entry["permitted_operations"])
                & set(entry["prohibited_operations"])
            )

    def test_79_matrix_source_paths_match_manifest_source_paths(self):
        manifest = manifest_index(self.fixture)
        matrix = matrix_index(self.fixture)
        for component_id in COMPONENTS:
            self.assertEqual(
                set(matrix[component_id]["source_paths"]),
                set(manifest[component_id]["source_paths"]),
            )

    def test_80_matrix_roles_match_manifest_roles(self):
        manifest = manifest_index(self.fixture)
        matrix = matrix_index(self.fixture)
        for component_id in COMPONENTS:
            self.assertEqual(
                matrix[component_id]["component_role"],
                manifest[component_id]["component_role"],
            )

    def test_81_baseline_performs_no_external_or_authoritative_action(self):
        false_fields = {
            "external_execution_performed",
            "workflow_execution_performed",
            "public_comment_posted",
            "risk_accepted_by_fixture",
            "final_action_approved_by_fixture",
            "fail_closed_executed_by_fixture",
            "rollback_executed_by_fixture",
            "audit_closed_by_fixture",
            "authority_transferred_by_fixture",
            "final_governance_judgment_made_by_fixture",
            "decision_proof_sealed_by_fixture",
        }
        for field in false_fields:
            self.assertIs(self.fixture[field], False, field)

    def test_82_new_evaluator_imports_no_existing_source_evaluator(self):
        tree = ast.parse(self.evaluator_text)
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        self.assertFalse(imported & SOURCE_MODULES)

    def test_83_new_evaluator_is_described_as_data_only_and_non_authoritative(self):
        module = ast.parse(self.evaluator_text)
        docstring = ast.get_docstring(module) or ""
        self.assertIn("data-only", docstring)
        self.assertIn("non-authoritative", docstring)

    def test_84_baseline_evaluation_is_deterministic(self):
        first = self.evaluate_fixture()
        second = self.evaluate_fixture()
        self.assertEqual(first, second)

    def test_85_case_evaluation_is_deterministic(self):
        first = self.evaluate_case(20)
        second = self.evaluate_case(20)
        self.assertEqual(first, second)

    def test_86_source_artifacts_are_not_mutated_by_evaluation(self):
        artifacts = copy.deepcopy(self.source_artifacts)
        before = copy.deepcopy(artifacts)
        self.evaluate_fixture(source_artifacts=artifacts)
        self.assertEqual(artifacts, before)

    def test_87_top_level_forbidden_claim_is_detected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["decision_proof_sealed"] = True
        result = evaluate_m14_cross_control_authority_boundary(
            fixture, self.source_artifacts
        )
        self.assertFalse(result["valid"])
        self.assertTrue(result["authority_violation_detected"])
        self.assertFalse(result["ready_for_m14_readiness_review"])

    def test_88_nested_top_level_forbidden_claim_is_detected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["reviewer_state"] = {
            "nested": [{"registry_state": {"result": "merge_approved"}}]
        }
        result = evaluate_m14_cross_control_authority_boundary(
            fixture, self.source_artifacts
        )
        self.assertFalse(result["valid"])
        self.assertTrue(result["authority_violation_detected"])

    def test_89_renamed_approval_container_is_detected(self):
        findings = detect_authority_violations(
            {"renamed_approval_field": {"state": "approved"}}
        )
        self.assertTrue(any("renamed_approval" in item for item in findings))

    def test_90_renamed_release_status_is_detected(self):
        findings = detect_authority_violations(
            {"public_release_status": "approved"}
        )
        self.assertTrue(any("renamed_approval" in item for item in findings))

    def test_91_decision_proof_sealed_false_does_not_trigger(self):
        self.assertEqual(
            detect_authority_violations({"decision_proof_sealed": False}), []
        )

    def test_92_risk_accepted_denied_does_not_trigger(self):
        self.assertEqual(
            detect_authority_violations({"risk_accepted": "denied"}), []
        )

    def test_93_merge_approved_not_approved_does_not_trigger(self):
        self.assertEqual(
            detect_authority_violations({"merge_approved": "not_approved"}),
            [],
        )

    def test_94_fail_closed_executed_false_does_not_trigger(self):
        self.assertEqual(
            detect_authority_violations({"fail_closed_executed": False}), []
        )

    def test_95_authority_transferred_not_transferred_does_not_trigger(self):
        self.assertEqual(
            detect_authority_violations(
                {"authority_transferred": "not_transferred"}
            ),
            [],
        )

    def test_96_nested_explicit_negative_authority_fields_do_not_trigger(self):
        payload = {
            "decision_proof_sealed": {
                "status": "not_sealed",
                "evidence": [
                    {"risk_accepted": "denied"},
                    {"merge_approved": "not_approved"},
                    {"fail_closed_executed": False},
                    {"authority_transferred": "not_transferred"},
                    {"waiver_granted": None},
                    {"deployment_approved": 0},
                    {"review_approved": ""},
                    {"installation_approved": "no"},
                    {"audit_closed": "rejected"},
                    {"final_action_approved": "not_authorized"},
                    {"skill_execution_approved": "not_allowed"},
                    {"rollback_executed": "not_executed"},
                    {"m14_complete": "not_complete"},
                    {"v0_13_0_released": "not_released"},
                    {"closes_201": "blocked"},
                    {"sealed_by_evaluator": "aaos"},
                ],
            }
        }
        self.assertEqual(detect_authority_violations(payload), [])

    def test_97_negative_outer_field_does_not_hide_nested_affirmative_claim(self):
        payload = {
            "decision_proof_sealed": {
                "status": "not_sealed",
                "nested": {"authority_transferred": True},
            }
        }
        findings = detect_authority_violations(payload)
        self.assertNotIn(
            "forbidden_authority_key:$.decision_proof_sealed:decision_proof_sealed",
            findings,
        )
        self.assertTrue(
            any("authority_transferred" in finding for finding in findings)
        )

    def test_98_affirmative_boolean_and_numeric_forbidden_claims_still_trigger(self):
        for value in (True, 1, -1):
            with self.subTest(value=value):
                findings = detect_authority_violations(
                    {"decision_proof_sealed": value}
                )
                self.assertTrue(
                    any("forbidden_authority_key" in finding for finding in findings)
                )

    def test_99_affirmative_string_forbidden_claims_still_trigger(self):
        affirmative_states = {
            "accepted",
            "allowed",
            "approved",
            "authorized",
            "closed",
            "complete",
            "completed",
            "executed",
            "final",
            "granted",
            "released",
            "sealed",
            "transferred",
        }
        for state in affirmative_states:
            with self.subTest(state=state):
                findings = detect_authority_violations({"risk_accepted": state})
                self.assertTrue(
                    any("forbidden_authority_key" in finding for finding in findings)
                )

    def test_100_exact_forbidden_output_tokens_used_as_values_still_trigger(self):
        for token in FORBIDDEN_OUTPUTS:
            with self.subTest(token=token):
                findings = detect_authority_violations({"result": token})
                self.assertTrue(
                    any("forbidden_authority_value" in finding for finding in findings)
                )

    def test_101_renamed_approval_and_authority_transfer_claims_still_trigger(self):
        payloads = (
            {"public_release_status": "approved"},
            {"retained_authority_owner": "cross_control_evaluator"},
            {"delegated_final_authority": True},
            {"approval_context": {"state": "approved"}},
        )
        for payload in payloads:
            with self.subTest(payload=payload):
                self.assertTrue(detect_authority_violations(payload))
        self.assertEqual(
            detect_authority_violations(
                {"non_authoritative_observation": {"state": "approved"}}
            ),
            [],
        )

    def test_102_active_component_explicit_negative_governance_evidence_is_valid(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["baseline_component_results"][0]["evidence"][
            "explicit_negative_governance_evidence"
        ] = {
            "decision_proof_sealed": False,
            "risk_accepted": "denied",
            "merge_approved": "not_approved",
            "fail_closed_executed": False,
            "authority_transferred": "not_transferred",
        }
        result = self.evaluate_fixture(fixture=fixture)
        self.assertTrue(result["valid"])
        self.assertFalse(result["authority_violation_detected"])
        self.assertTrue(result["ready_for_m14_readiness_review"])

    def test_103_baseline_remains_ready_for_m14_readiness_review(self):
        result = self.evaluate_fixture()
        self.assertTrue(result["valid"])
        self.assertTrue(result["ready_for_m14_readiness_review"])

    def test_104_baseline_remains_m14_active_work_not_complete(self):
        result = self.evaluate_fixture()
        self.assertEqual(
            self.fixture["m14_completion_status"], "active_work_not_complete"
        )
        self.assertNotIn("m14_complete", result["outputs"])
        self.assertTrue(result["ready_for_m14_readiness_review"])

    def test_105_neutral_metadata_inside_negative_container_does_not_trigger(self):
        payload = {
            "decision_proof_sealed": {
                "status": "not_sealed",
                "attempts": 1,
                "trace_available": True,
            }
        }
        self.assertEqual(detect_authority_violations(payload), [])

    def test_106_generic_complete_status_is_not_approval(self):
        payloads = (
            {"risk_assessment": {"status": "complete"}},
            {"release_notes": {"status": "complete"}},
        )
        for payload in payloads:
            with self.subTest(payload=payload):
                self.assertEqual(detect_authority_violations(payload), [])

    def test_107_named_affirmative_forbidden_key_values_still_trigger(self):
        payloads = (
            {"decision_proof_sealed": "by_registry"},
            {"authority_transferred": "cross_control_evaluator"},
        )
        for payload in payloads:
            with self.subTest(payload=payload):
                findings = detect_authority_violations(payload)
                self.assertTrue(
                    any("forbidden_authority_key" in finding for finding in findings)
                )

    def test_108_arbitrary_not_prefix_cannot_hide_affirmative_claim(self):
        findings = detect_authority_violations(
            {"decision_proof_sealed": "not_only_claimed_but_sealed"}
        )
        self.assertTrue(
            any("forbidden_authority_key" in finding for finding in findings)
        )


if __name__ == "__main__":
    unittest.main()
