import ast
import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.skill_admission_evaluator import (  # noqa: E402
    evaluate_fixture_case,
    evaluate_skill_admission,
    evaluate_skill_admission_fixture,
)


FIXTURE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m14-skill-admission-fixtures.json"
)
EVALUATOR_PATH = ROOT / "runtime" / "skill_admission_evaluator.py"
DOCUMENT_PATH = (
    ROOT / "docs" / "capability-supply-chain" / "nvidia-skills-admission.md"
)

INTENDED_FILES = {
    "docs/capability-supply-chain/nvidia-skills-admission.md",
    "examples/public-integration-pack-pilot/m14-skill-admission-fixtures.json",
    "runtime/skill_admission_evaluator.py",
    "tests/test_skill_admission_evaluator.py",
}

REQUIRED_CONTRACT_FIELDS = {
    "skill_id",
    "skill_name",
    "source_repo",
    "source_owner",
    "source_commit",
    "source_artifact_digest",
    "version",
    "license",
    "description",
    "intended_use",
    "prohibited_use",
    "activation_triggers",
    "supported_agents",
    "supported_runtimes",
    "required_tools",
    "required_permissions",
    "network_access",
    "allowed_network_domains",
    "blocked_network_domains",
    "file_access",
    "allowed_file_scopes",
    "blocked_file_scopes",
    "shell_access",
    "allowed_command_classes",
    "blocked_command_classes",
    "mcp_access",
    "required_mcp_servers",
    "environment_variables",
    "secret_access",
    "data_classification",
    "risk_level",
    "known_risks",
    "mitigations",
    "owner_contact",
    "skill_card",
    "scan_report",
    "scan_tool",
    "scan_timestamp",
    "signature",
    "signature_identity",
    "signature_verification_method",
    "benchmark_report",
    "evaluation_artifacts",
    "runtime_isolation_requirements",
    "output_contract",
    "trace_requirements",
    "replay_requirements",
    "rollback_requirements",
    "fail_closed_rules",
    "reassessment_interval",
    "last_reassessment",
    "expiration_date",
    "admission_policy_version",
}

REQUIRED_REGISTRY_FIELDS = {
    "registry_entry_id",
    "skill_id",
    "artifact_identity",
    "candidate_admission_state",
    "permission_envelope",
    "evidence_status",
    "runtime_constraints",
    "human_review_route",
    "reassessment_status",
    "trace_policy",
    "replay_policy",
    "governance_owner",
}

REQUIRED_REGISTRY_STATES = {
    "candidate_allowed",
    "candidate_restricted",
    "candidate_blocked",
    "needs_approval",
    "needs_sandbox",
    "needs_human_review",
    "needs_replay_log",
    "needs_signature_verification",
    "needs_scan",
    "needs_evaluation",
    "stale_reassessment_required",
}

REQUIRED_FAIL_CLOSED_RULES = {
    "unknown_skill_source",
    "missing_source_owner",
    "missing_source_commit",
    "missing_artifact_digest",
    "missing_version",
    "missing_license",
    "missing_skill_owner",
    "incomplete_permission_declaration",
    "permission_escalation",
    "undeclared_shell_access",
    "undeclared_network_access",
    "undeclared_file_access",
    "undeclared_mcp_access",
    "undeclared_secret_access",
    "undefined_output_contract",
    "missing_trace_requirements",
    "replay_evidence_unavailable",
    "insufficient_runtime_isolation",
    "required_signature_missing",
    "signature_verification_evidence_missing",
    "required_scan_missing",
    "high_risk_evaluation_evidence_missing",
    "artifact_digest_drift",
    "skill_expired_or_stale",
    "reassessment_overdue",
    "mutable_reference_without_binding",
}

REQUIRED_BOUNDARY_STATEMENTS = {
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
}


def load_fixture():
    with FIXTURE_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


class SkillAdmissionEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = load_fixture()
        cls.evaluator_text = EVALUATOR_PATH.read_text(encoding="utf-8")
        cls.document_text = DOCUMENT_PATH.read_text(encoding="utf-8")

    def fixture_case(self, case_id):
        return next(
            case for case in self.fixture["fixture_cases"] if case["case_id"] == case_id
        )

    def assert_case_matches_fixture(self, case_id):
        result = evaluate_fixture_case(copy.deepcopy(self.fixture), case_id)
        expected = self.fixture_case(case_id)["expected"]

        self.assertEqual(result["ready_for_review"], expected["ready_for_review"])
        self.assertEqual(
            result["candidate_admission_state"],
            expected["candidate_admission_state"],
        )
        self.assertEqual(set(result["outputs"]), set(expected["outputs"]))
        self.assertEqual(set(result["reasons"]), set(expected["reasons"]))
        self.assertLessEqual(
            set(result["outputs"]), set(self.fixture["allowed_evaluator_outputs"])
        )
        self.assertFalse(
            set(result["outputs"]) & set(self.fixture["forbidden_evaluator_outputs"])
        )
        return result

    def contract_with(self, changes):
        contract = copy.deepcopy(self.fixture["skill_admission_contract"])
        for path, value in changes.items():
            target = contract
            parts = path.split(".")
            for part in parts[:-1]:
                target = target[part]
            target[parts[-1]] = copy.deepcopy(value)
        return contract

    def assert_contract_rejected(self, changes, evaluation_overrides=None):
        result = evaluate_skill_admission(
            self.contract_with(changes), evaluation_overrides
        )
        self.assertFalse(result["ready_for_review"])
        self.assertEqual(result["candidate_admission_state"], "candidate_blocked")
        self.assertIn("admission_not_ready", result["outputs"])
        self.assertIn("fail_closed_recommended", result["outputs"])
        self.assertTrue(result["reasons"])
        self.assertFalse(
            set(result["outputs"]) & set(self.fixture["forbidden_evaluator_outputs"])
        )
        return result

    def assert_fixture_rejected(self, fixture):
        result = evaluate_skill_admission_fixture(fixture)
        self.assertFalse(result["valid"])
        self.assertFalse(result["ready_for_review"])
        self.assertEqual(result["candidate_admission_state"], "candidate_blocked")
        self.assertEqual(result["outputs"], ["skill_admission_fixture_invalid"])
        self.assertTrue(result["reasons"])
        return result

    def test_01_valid_top_level_m14_state(self):
        result = evaluate_skill_admission_fixture(copy.deepcopy(self.fixture))

        self.assertTrue(result["valid"])
        self.assertEqual(result["reasons"], [])
        self.assertIn("skill_admission_fixture_valid", result["outputs"])
        self.assertEqual(self.fixture["fixture_status"], "m14_active_work_not_complete")
        self.assertEqual(self.fixture["related_issue"], "#192")
        self.assertEqual(self.fixture["tracker_issue"], "#201")
        self.assertEqual(self.fixture["tracker_issue_linkage"], "Refs #201")
        self.assertEqual(self.fixture["related_voice_runtime_pr"], "#202")
        self.assertEqual(self.fixture["related_public_output_gate_pr"], "#204")
        self.assertEqual(self.fixture["related_moda_mapping_pr"], "#205")
        self.assertEqual(self.fixture["related_ai_pr_provenance_pr"], "#206")
        self.assertEqual(self.fixture["m14_completion_status"], "active_work_not_complete")
        self.assertEqual(self.fixture["target_future_release"], "v0.13.0")
        self.assertFalse(self.fixture["future_release_tag_path"]["released"])

    def test_02_exactly_four_intended_files(self):
        self.assertEqual(set(self.fixture["intended_files"]), INTENDED_FILES)
        self.assertEqual(len(self.fixture["intended_files"]), 4)
        self.assertEqual(len(set(self.fixture["intended_files"])), 4)
        for relative_path in INTENDED_FILES:
            self.assertTrue((ROOT / relative_path).is_file(), relative_path)

    def test_03_complete_skill_admission_contract(self):
        contract = self.fixture["skill_admission_contract"]
        self.assertLessEqual(REQUIRED_CONTRACT_FIELDS, set(contract))
        self.assertEqual(
            set(contract["required_permissions"]),
            {"shell", "network", "file", "mcp", "secret"},
        )
        result = evaluate_skill_admission(copy.deepcopy(contract))
        self.assertTrue(result["ready_for_review"])
        self.assertEqual(result["candidate_admission_state"], "candidate_restricted")

    def test_04_complete_capability_registry_schema(self):
        schema = self.fixture["capability_registry_schema"]
        entry = self.fixture["capability_registry_entry"]
        self.assertEqual(set(schema["required_fields"]), REQUIRED_REGISTRY_FIELDS)
        self.assertEqual(set(schema["candidate_states"]), REQUIRED_REGISTRY_STATES)
        self.assertLessEqual(REQUIRED_REGISTRY_FIELDS, set(entry))
        self.assertEqual(entry["governance_owner"], "AAOS")

    def test_05_valid_synthetic_jetson_diagnostic_specimen(self):
        specimen = self.fixture["low_risk_jetson_diagnostic_specimen"]
        self.assertTrue(specimen["synthetic"])
        self.assertFalse(specimen["contains_real_nvidia_code"])
        self.assertFalse(specimen["contains_real_device_data"])
        self.assertFalse(specimen["skill_execution_performed"])
        self.assertFalse(specimen["shell_command_execution_performed"])
        self.assertFalse(specimen["device_access_performed"])
        self.assertFalse(specimen["network_access_performed"])
        self.assertEqual(specimen["intent"], "read_only_diagnostic")
        self.assertEqual(specimen["permission_envelope"], "restricted")
        for field in (
            "device_mutation_prohibited",
            "firmware_modification_prohibited",
            "package_installation_prohibited",
            "credential_access_prohibited",
            "arbitrary_shell_execution_prohibited",
            "output_schema_validation_required",
            "trace_evidence_required",
            "replay_evidence_required",
            "immutable_artifact_identity_required",
        ):
            self.assertTrue(specimen[field], field)
        self.assertEqual(specimen["maximum_outcome"], "admission_ready_for_review")
        self.assertFalse(specimen["execution_approval"])

    def test_06_fixture_performs_no_external_execution(self):
        for field in (
            "external_skill_downloaded",
            "external_skill_installed",
            "external_skill_executed",
            "network_access_performed_by_fixture",
            "shell_command_executed_by_fixture",
            "vendor_dependency_created",
        ):
            self.assertFalse(self.fixture[field], field)
        boundary = self.fixture["evaluation_boundary"]
        self.assertTrue(boundary["fixture_data_only"])
        for field, value in boundary.items():
            if field != "fixture_data_only":
                self.assertFalse(value, field)

    def test_07_missing_source_repository_fails(self):
        result = self.assert_case_matches_fixture(
            "case_02_unknown_source_repository_blocked"
        )
        self.assertIn("unknown_skill_source", result["reasons"])

    def test_08_missing_source_owner_fails(self):
        result = self.assert_case_matches_fixture(
            "case_03_missing_source_owner_blocked"
        )
        self.assertIn("missing_source_owner", result["reasons"])

    def test_09_missing_source_commit_fails(self):
        result = self.assert_case_matches_fixture(
            "case_04_missing_source_commit_blocked"
        )
        self.assertIn("missing_source_commit", result["reasons"])

    def test_10_missing_digest_fails(self):
        result = self.assert_case_matches_fixture(
            "case_05_missing_artifact_digest_blocked"
        )
        self.assertIn("missing_artifact_digest", result["reasons"])

    def test_11_mutable_tag_without_immutable_binding_fails(self):
        result = self.assert_case_matches_fixture(
            "case_06_mutable_tag_without_immutable_binding_blocked"
        )
        self.assertIn("mutable_reference_without_binding", result["reasons"])

    def test_12_missing_version_fails(self):
        result = self.assert_case_matches_fixture("case_07_missing_version_blocked")
        self.assertIn("missing_version", result["reasons"])

    def test_13_missing_license_fails(self):
        result = self.assert_case_matches_fixture("case_08_missing_license_blocked")
        self.assertIn("missing_license", result["reasons"])

    def test_14_missing_skill_owner_fails(self):
        result = self.assert_case_matches_fixture(
            "case_09_missing_skill_owner_blocked"
        )
        self.assertIn("missing_skill_owner", result["reasons"])

    def test_15_required_signature_missing_fails(self):
        result = self.assert_case_matches_fixture(
            "case_10_required_signature_missing_blocked"
        )
        self.assertIn("required_signature_missing", result["reasons"])
        self.assertIn("needs_signature_verification", result["outputs"])

    def test_16_signature_without_verification_evidence_fails(self):
        result = self.assert_case_matches_fixture(
            "case_11_signature_without_verification_evidence_blocked"
        )
        self.assertIn(
            "signature_verification_evidence_missing", result["reasons"]
        )

    def test_17_required_scan_missing_fails(self):
        result = self.assert_case_matches_fixture(
            "case_12_required_scan_report_missing_blocked"
        )
        self.assertIn("required_scan_missing", result["reasons"])
        self.assertIn("needs_scan", result["outputs"])

    def test_18_undeclared_shell_access_fails(self):
        result = self.assert_case_matches_fixture(
            "case_13_undeclared_shell_access_blocked"
        )
        self.assertIn("undeclared_shell_access", result["reasons"])

    def test_19_undeclared_network_access_fails(self):
        result = self.assert_case_matches_fixture(
            "case_14_undeclared_network_access_blocked"
        )
        self.assertIn("undeclared_network_access", result["reasons"])

    def test_20_undeclared_file_access_fails(self):
        result = self.assert_case_matches_fixture(
            "case_15_undeclared_file_access_blocked"
        )
        self.assertIn("undeclared_file_access", result["reasons"])

    def test_21_undeclared_mcp_access_fails(self):
        result = self.assert_case_matches_fixture(
            "case_16_undeclared_mcp_access_blocked"
        )
        self.assertIn("undeclared_mcp_access", result["reasons"])

    def test_22_undeclared_secret_access_fails(self):
        result = self.assert_case_matches_fixture(
            "case_17_undeclared_secret_access_blocked"
        )
        self.assertIn("undeclared_secret_access", result["reasons"])

    def test_23_permission_mismatch_fails(self):
        result = self.assert_case_matches_fixture(
            "case_18_declared_permissions_differ_from_observed_requirements"
        )
        self.assertIn("permission_escalation", result["reasons"])
        self.assertIn("permission_mismatch_detected", result["outputs"])

    def test_24_insufficient_runtime_isolation_fails(self):
        result = self.assert_case_matches_fixture(
            "case_19_unsupported_runtime_isolation_blocked"
        )
        self.assertIn("insufficient_runtime_isolation", result["reasons"])
        self.assertIn("needs_sandbox", result["outputs"])

    def test_25_missing_output_contract_fails(self):
        result = self.assert_case_matches_fixture(
            "case_20_undefined_output_contract_blocked"
        )
        self.assertIn("undefined_output_contract", result["reasons"])

    def test_26_missing_trace_fails(self):
        result = self.assert_case_matches_fixture(
            "case_21_missing_trace_requirements_blocked"
        )
        self.assertIn("missing_trace_requirements", result["reasons"])

    def test_27_missing_replay_fails(self):
        result = self.assert_case_matches_fixture(
            "case_22_missing_replay_capability_blocked"
        )
        self.assertIn("replay_evidence_unavailable", result["reasons"])
        self.assertIn("needs_replay_log", result["outputs"])

    def test_28_stale_skill_requires_reassessment(self):
        result = self.assert_case_matches_fixture(
            "case_23_stale_skill_requires_reassessment"
        )
        self.assertIn("reassessment_overdue", result["reasons"])
        self.assertEqual(
            result["candidate_admission_state"], "stale_reassessment_required"
        )

    def test_29_expired_evidence_fails(self):
        result = self.assert_case_matches_fixture(
            "case_24_expired_admission_evidence_blocked"
        )
        self.assertIn("skill_expired_or_stale", result["reasons"])

    def test_30_artifact_digest_drift_fails(self):
        result = self.assert_case_matches_fixture(
            "case_25_artifact_digest_drift_blocked"
        )
        self.assertIn("artifact_digest_drift", result["reasons"])
        self.assertIn("artifact_drift_detected", result["outputs"])
        self.assertIn("rollback_recommended", result["outputs"])

    def test_31_high_risk_medical_skill_without_evaluations_fails(self):
        result = self.assert_case_matches_fixture(
            "case_26_high_risk_medical_without_evaluation_blocked"
        )
        self.assertIn("high_risk_evaluation_evidence_missing", result["reasons"])
        self.assertIn("needs_evaluation", result["outputs"])
        self.assertIn("needs_human_review", result["outputs"])

    def test_32_physical_action_skill_without_sandbox_and_review_fails(self):
        result = self.assert_case_matches_fixture(
            "case_27_high_risk_physical_action_without_sandbox_and_review_blocked"
        )
        self.assertIn("high_risk_sandbox_missing", result["reasons"])
        self.assertIn("high_risk_human_review_missing", result["reasons"])
        self.assertIn("needs_sandbox", result["outputs"])
        self.assertIn("needs_human_review", result["outputs"])

    def test_33_signature_incorrectly_treated_as_approval_fails(self):
        result = self.assert_case_matches_fixture(
            "case_31_signature_verification_treated_as_governance_approval_rejected"
        )
        self.assertIn(
            "forbidden_output_claim:signature_is_governance_approval",
            result["reasons"],
        )

    def test_34_scan_incorrectly_treated_as_risk_acceptance_fails(self):
        result = self.assert_case_matches_fixture(
            "case_32_scan_passed_treated_as_risk_acceptance_rejected"
        )
        self.assertIn(
            "forbidden_output_claim:scan_is_risk_acceptance", result["reasons"]
        )

    def test_35_benchmark_incorrectly_treated_as_deployment_approval_fails(self):
        result = self.assert_case_matches_fixture(
            "case_33_benchmark_passed_treated_as_deployment_approval_rejected"
        )
        self.assertIn(
            "forbidden_output_claim:benchmark_is_deployment_approval",
            result["reasons"],
        )

    def test_36_candidate_admission_treated_as_execution_approval_fails(self):
        result = self.assert_case_matches_fixture(
            "case_30_admission_ready_treated_as_execution_approval_rejected"
        )
        self.assertIn(
            "forbidden_output_claim:skill_execution_approved", result["reasons"]
        )

    def test_37_evaluator_attempting_execution_fails(self):
        result = self.assert_case_matches_fixture(
            "case_34_evaluator_attempts_skill_execution_rejected"
        )
        self.assertIn("forbidden_output_claim:skill_executed", result["reasons"])

    def test_38_evaluator_attempting_risk_acceptance_fails(self):
        result = self.assert_case_matches_fixture(
            "case_35_evaluator_attempts_risk_acceptance_rejected"
        )
        self.assertIn("forbidden_output_claim:risk_accepted", result["reasons"])

    def test_39_evaluator_attempting_decision_proof_sealing_fails(self):
        result = self.assert_case_matches_fixture(
            "case_36_evaluator_attempts_decision_proof_sealing_rejected"
        )
        self.assertIn(
            "forbidden_output_claim:decision_proof_sealed", result["reasons"]
        )

    def test_40_evaluator_attempting_authority_transfer_fails(self):
        result = self.assert_case_matches_fixture(
            "case_37_evaluator_attempts_authority_transfer_rejected"
        )
        self.assertIn(
            "forbidden_output_claim:authority_transferred", result["reasons"]
        )

    def test_41_evaluator_attempting_m14_completion_fails(self):
        result = self.assert_case_matches_fixture(
            "case_39_evaluator_attempts_m14_completion_rejected"
        )
        self.assertIn("forbidden_output_claim:m14_complete", result["reasons"])

    def test_42_evaluator_attempting_v0_13_0_release_fails(self):
        result = self.assert_case_matches_fixture(
            "case_40_evaluator_attempts_v0_13_0_release_rejected"
        )
        self.assertIn(
            "forbidden_output_claim:v0_13_0_released", result["reasons"]
        )

    def test_43_evaluator_attempting_to_close_tracker_201_fails(self):
        result = self.assert_case_matches_fixture(
            "case_38_evaluator_attempts_close_tracker_201_rejected"
        )
        self.assertIn("forbidden_output_claim:closes_201", result["reasons"])

    def test_44_complete_low_risk_case_is_ready_for_review_only(self):
        result = self.assert_case_matches_fixture(
            "case_01_complete_synthetic_low_risk_jetson_diagnostic"
        )
        self.assertTrue(result["ready_for_review"])
        self.assertIn("admission_ready_for_review", result["outputs"])
        self.assertNotIn("final_admission_approved", result["outputs"])
        self.assertNotIn("skill_execution_approved", result["outputs"])

    def test_45_signed_skill_with_excessive_permissions_remains_blocked(self):
        result = self.assert_case_matches_fixture(
            "case_28_signed_skill_with_excessive_permissions_blocked"
        )
        self.assertIn("excessive_permissions", result["reasons"])
        self.assertIn("reviewed_permission_binding_mismatch", result["reasons"])

    def test_46_scanned_skill_with_undeclared_network_remains_blocked(self):
        result = self.assert_case_matches_fixture(
            "case_29_scanned_skill_with_undeclared_network_access_blocked"
        )
        self.assertIn("undeclared_network_access", result["reasons"])
        self.assertIn("permission_escalation", result["reasons"])

    def test_47_all_fixture_cases_are_unique_and_evaluated(self):
        case_ids = [case["case_id"] for case in self.fixture["fixture_cases"]]
        self.assertEqual(len(case_ids), 40)
        self.assertEqual(len(case_ids), len(set(case_ids)))
        fixture_result = evaluate_skill_admission_fixture(copy.deepcopy(self.fixture))
        self.assertEqual(len(fixture_result["case_results"]), 40)
        self.assertEqual(
            {result["case_id"] for result in fixture_result["case_results"]},
            set(case_ids),
        )

    def test_48_immutable_review_binding_is_exact_and_complete(self):
        contract = self.fixture["skill_admission_contract"]
        binding = contract["immutable_review_binding"]
        self.assertEqual(binding["source_commit"], contract["source_commit"])
        self.assertEqual(
            binding["source_artifact_digest"], contract["source_artifact_digest"]
        )
        self.assertEqual(binding["version"], contract["version"])
        self.assertEqual(
            binding["reviewed_permission_declaration"],
            contract["required_permissions"],
        )
        self.assertEqual(
            binding["admission_policy_version"], contract["admission_policy_version"]
        )
        self.assertIn("reviewed_evidence_set", binding)

    def test_49_fail_closed_rule_catalog_is_complete(self):
        actual = {rule["rule_id"] for rule in self.fixture["fail_closed_rules"]}
        self.assertLessEqual(REQUIRED_FAIL_CLOSED_RULES, actual)
        for rule in self.fixture["fail_closed_rules"]:
            self.assertIn(
                rule["outcome"],
                {"admission_not_ready", "candidate_blocked", "stale_reassessment_required"},
            )

    def test_50_candidate_registry_states_are_routing_only(self):
        schema = self.fixture["capability_registry_schema"]
        self.assertEqual(set(schema["state_semantics"]), REQUIRED_REGISTRY_STATES)
        for state, semantics in schema["state_semantics"].items():
            self.assertIn(semantics, {"registry_classification_only", "routing_state_only"}, state)
        self.assertLessEqual(
            {
                "final_execution_approval",
                "risk_acceptance",
                "deployment_authorization",
                "audit_closure",
                "decision_proof_sealing",
            },
            set(schema["non_authoritative_for"]),
        )

    def test_51_required_boundary_statements_are_preserved(self):
        self.assertLessEqual(
            REQUIRED_BOUNDARY_STATEMENTS,
            set(self.fixture["required_boundary_statements"]),
        )
        normalized_document = self.document_text.replace("`", "")
        for statement in REQUIRED_BOUNDARY_STATEMENTS - {
            "AAOS remains vendor-independent."
        }:
            self.assertIn(statement, normalized_document)
        self.assertIn(
            "AAOS remains model-agnostic and vendor-independent.",
            normalized_document,
        )

    def test_52_allowed_and_forbidden_outputs_are_disjoint(self):
        allowed = set(self.fixture["allowed_evaluator_outputs"])
        forbidden = set(self.fixture["forbidden_evaluator_outputs"])
        self.assertFalse(allowed & forbidden)
        self.assertLessEqual(REQUIRED_REGISTRY_STATES, allowed)
        self.assertLessEqual(
            {
                "skill_admission_fixture_valid",
                "skill_admission_fixture_invalid",
                "admission_ready_for_review",
                "admission_not_ready",
                "permission_mismatch_detected",
                "artifact_drift_detected",
                "fail_closed_recommended",
                "rollback_recommended",
                "escalation_required",
            },
            allowed,
        )
        self.assertLessEqual(
            {
                "skill_execution_approved",
                "final_admission_approved",
                "risk_accepted",
                "decision_proof_sealed",
                "authority_transferred",
                "m14_complete",
                "v0_13_0_released",
                "closes_201",
            },
            forbidden,
        )

    def test_53_capture_verify_accumulate_mapping_is_complete(self):
        mapping = self.fixture["capture_verify_accumulate"]
        self.assertLessEqual(
            {
                "skill identity",
                "source identity",
                "immutable artifact identity",
                "declared owner",
                "intended use",
                "prohibited use",
                "runtime",
                "supported agent",
                "requested permissions",
                "shell scope",
                "network scope",
                "file scope",
                "MCP scope",
                "secret scope",
                "data classification",
                "risk classification",
                "output contract",
                "activation trigger",
            },
            set(mapping["capture"]),
        )
        self.assertLessEqual(
            {
                "source binding",
                "digest binding",
                "version binding",
                "owner presence",
                "license presence",
                "permission completeness",
                "least-privilege check",
                "permission mismatch check",
                "signature requirement",
                "signature evidence",
                "scan requirement",
                "scan evidence",
                "benchmark requirement",
                "evaluation evidence",
                "runtime isolation",
                "sandbox requirement",
                "human-review requirement",
                "trace availability",
                "replay availability",
                "output-contract validity",
                "staleness",
                "expiration",
                "reassessment requirement",
                "fail-closed decision",
            },
            set(mapping["verify"]),
        )
        self.assertLessEqual(
            {
                "admission evaluation trace",
                "evidence artifact references",
                "denied-condition trace",
                "permission-diff record",
                "reviewer handoff",
                "registry decision record",
                "runtime constraint record",
                "execution trace policy",
                "replay packet requirements",
                "drift record",
                "reassessment history",
                "incident linkage",
                "governance authority retention",
            },
            set(mapping["accumulate"]),
        )

    def test_54_evaluator_imports_standard_library_only(self):
        tree = ast.parse(self.evaluator_text)
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        self.assertLessEqual(imports, sys.stdlib_module_names)

    def test_55_evaluator_has_no_network_shell_or_dynamic_execution_calls(self):
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
                "os.popen",
                "os.spawnl",
                "os.spawnle",
                "os.spawnlp",
                "os.spawnlpe",
                "os.spawnv",
                "os.spawnve",
                "os.spawnvp",
                "os.spawnvpe",
                "os.system",
                "subprocess.call",
                "subprocess.check_call",
                "subprocess.check_output",
                "subprocess.Popen",
                "subprocess.run",
            }
        )

    def test_56_document_contains_all_required_sections(self):
        for section in (
            "## 1. Purpose and scope",
            "## 2. External capability-supply-chain threat model",
            "## 3. NVIDIA/skills reference positioning",
            "## 4. AAOS layer mapping",
            "## 5. Skill Admission Contract",
            "## 6. Capability registry model",
            "## 7. Artifact identity and immutable review binding",
            "## 8. Permission declaration and least-privilege rules",
            "## 9. Scan, signature, benchmark, and evaluation evidence",
            "## 10. Runtime compatibility and isolation requirements",
            "## 11. Execution trace and replay requirements",
            "## 12. Output contract requirements",
            "## 13. Drift, staleness, and periodic reassessment",
            "## 14. Fail-closed admission rules",
            "## 15. Low-risk Jetson diagnostic specimen",
            "## 16. High-risk domain restrictions",
            "## 17. Capture / Verify / Accumulate mapping",
            "## 18. Governance boundary",
            "## 19. M14 active-work and future v0.13.0 status",
        ):
            self.assertIn(section, self.document_text)

    def test_57_nvidia_is_reference_specimen_not_dependency_or_approval(self):
        self.assertEqual(self.fixture["source_reference"], "NVIDIA/skills")
        self.assertEqual(
            self.fixture["source_reference_role"],
            "external_capability_supply_chain_reference_specimen",
        )
        self.assertFalse(self.fixture["vendor_dependency_created"])
        for claim, made in self.fixture["source_reference_claims"].items():
            self.assertFalse(made, claim)
        positioning = self.fixture["supply_chain_positioning"]
        self.assertIn("external agent capability artifacts", positioning["external_artifact_role"])
        self.assertEqual(
            positioning["dependency_status"],
            "reference_specimen_only_not_an_aaos_dependency",
        )

    def test_58_decision_sovereignty_and_sealing_remain_aaos_owned(self):
        self.assertFalse(self.fixture["decision_proof_sealed_by_fixture"])
        self.assertFalse(self.fixture["final_admission_approval_made_by_fixture"])
        self.assertFalse(self.fixture["execution_authorization_made_by_fixture"])
        self.assertFalse(self.fixture["risk_accepted_by_fixture"])
        self.assertIn(
            "Decision Proof sealing remains AAOS-owned.",
            self.fixture["required_boundary_statements"],
        )

    def test_59_high_risk_false_requirement_flags_cannot_bypass_evidence(self):
        result = self.assert_contract_rejected(
            {
                "risk_level": "high",
                "intended_use": ["synthetic_high_risk_medical_specimen"],
                "benchmark_report": None,
                "evaluation_artifacts": [],
                "evidence_requirements.benchmark_required": False,
                "evidence_requirements.evaluation_required": False,
            }
        )
        self.assertIn("high_risk_evaluation_evidence_missing", result["reasons"])
        self.assertIn("needs_evaluation", result["outputs"])
        self.assertIn("needs_human_review", result["outputs"])

    def test_60_mutable_branch_source_commit_rejected_even_with_binding(self):
        mutable_ref = "refs/heads/synthetic-main"
        result = self.assert_contract_rejected(
            {
                "source_commit": mutable_ref,
                "artifact_reference_type": "immutable_commit_and_digest",
                "immutable_review_binding.source_commit": mutable_ref,
            }
        )
        self.assertIn("mutable_reference_without_binding", result["reasons"])

    def test_61_mutable_tag_source_commit_rejected_even_with_binding(self):
        mutable_ref = "refs/tags/synthetic-latest"
        result = self.assert_contract_rejected(
            {
                "source_commit": mutable_ref,
                "artifact_reference_type": "immutable_commit_and_digest",
                "immutable_review_binding.source_commit": mutable_ref,
            }
        )
        self.assertIn("mutable_reference_without_binding", result["reasons"])

    def test_62_empty_reviewed_permission_binding_fails(self):
        result = self.assert_contract_rejected(
            {"immutable_review_binding.reviewed_permission_declaration": {}}
        )
        self.assertIn("reviewed_permission_binding_invalid", result["reasons"])

    def test_63_malformed_reviewed_permission_binding_fails(self):
        result = self.assert_contract_rejected(
            {
                "immutable_review_binding.reviewed_permission_declaration":
                    "not-a-permission-declaration"
            }
        )
        self.assertIn("reviewed_permission_binding_invalid", result["reasons"])

    def test_64_empty_reviewed_evidence_binding_fails(self):
        result = self.assert_contract_rejected(
            {"immutable_review_binding.reviewed_evidence_set": []}
        )
        self.assertIn("reviewed_evidence_binding_invalid", result["reasons"])

    def test_65_malformed_reviewed_evidence_binding_fails(self):
        result = self.assert_contract_rejected(
            {"immutable_review_binding.reviewed_evidence_set": "not-an-evidence-set"}
        )
        self.assertIn("reviewed_evidence_binding_invalid", result["reasons"])

    def test_66_empty_admission_policy_binding_fails(self):
        result = self.assert_contract_rejected(
            {
                "admission_policy_version": "",
                "immutable_review_binding.admission_policy_version": "",
            }
        )
        self.assertTrue(
            {
                "immutable_review_binding_incomplete",
                "required_contract_field_invalid:admission_policy_version",
            }
            & set(result["reasons"])
        )

    def test_67_wildcard_network_scope_fails_closed(self):
        result = self.assert_contract_rejected(
            {"allowed_network_domains": ["*"]}
        )
        self.assertIn("network_scope_contradiction", result["reasons"])

    def test_68_wildcard_host_file_scope_fails_closed(self):
        result = self.assert_contract_rejected(
            {"allowed_file_scopes": ["host://*"]}
        )
        self.assertIn("excessive_permissions", result["reasons"])

    def test_69_arbitrary_command_scope_fails_closed(self):
        result = self.assert_contract_rejected(
            {"allowed_command_classes": ["arbitrary_shell"]}
        )
        self.assertIn("shell_scope_contradiction", result["reasons"])

    def test_70_low_risk_candidate_cannot_exceed_maximum_permission_envelope(self):
        result = self.assert_contract_rejected(
            {
                "required_permissions.network": "outbound_https",
                "network_access": "outbound_https",
                "allowed_network_domains": ["synthetic.example.invalid"],
                "observed_required_permissions.network": "outbound_https",
                "immutable_review_binding.reviewed_permission_declaration.network":
                    "outbound_https",
            }
        )
        self.assertIn("low_risk_permission_envelope_exceeded", result["reasons"])

    def test_71_jetson_network_activity_contradiction_fails(self):
        result = self.assert_contract_rejected(
            {"synthetic_specimen.network_accessed": True}
        )
        self.assertIn("synthetic_specimen_boundary_invalid", result["reasons"])

    def test_72_jetson_shell_activity_contradiction_fails(self):
        result = self.assert_contract_rejected(
            {"synthetic_specimen.shell_command_executed": True}
        )
        self.assertIn("synthetic_specimen_boundary_invalid", result["reasons"])

    def test_73_jetson_runtime_isolation_contradiction_fails(self):
        result = self.assert_contract_rejected(
            {"runtime_isolation_requirements.network_disabled": False}
        )
        self.assertIn("runtime_isolation_controls_invalid", result["reasons"])

    def test_74_jetson_output_side_effect_contradiction_fails(self):
        result = self.assert_contract_rejected(
            {"output_contract.side_effects_allowed": True}
        )
        self.assertIn("output_contract_semantics_invalid", result["reasons"])

    def test_75_jetson_execution_claim_contradiction_fails(self):
        result = self.assert_contract_rejected(
            {
                "synthetic_specimen.skill_executed": True,
                "output_contract.execution_or_approval_claims_allowed": True,
            }
        )
        self.assertIn("synthetic_specimen_boundary_invalid", result["reasons"])

    def test_76_jetson_replay_execution_contradiction_fails(self):
        result = self.assert_contract_rejected(
            {"replay_requirements.skill_execution_in_replay": True}
        )
        self.assertIn("replay_execution_boundary_invalid", result["reasons"])

    def test_77_empty_required_contract_identity_and_description_fields_fail(self):
        for field in (
            "skill_id",
            "skill_name",
            "description",
            "data_classification",
            "risk_level",
            "scan_tool",
            "scan_timestamp",
            "signature_identity",
            "signature_verification_method",
            "admission_policy_version",
        ):
            with self.subTest(field=field):
                result = self.assert_contract_rejected({field: ""})
                self.assertIn(
                    f"required_contract_field_invalid:{field}", result["reasons"]
                )

    def test_78_malformed_required_contract_collection_and_object_fields_fail(self):
        malformed = {
            "intended_use": "not-a-list",
            "prohibited_use": "not-a-list",
            "activation_triggers": "not-a-list",
            "supported_agents": "not-a-list",
            "supported_runtimes": "not-a-list",
            "required_tools": "not-a-list",
            "known_risks": "not-a-list",
            "mitigations": "not-a-list",
            "evaluation_artifacts": "not-a-list",
            "runtime_isolation_requirements": "not-an-object",
            "output_contract": "not-an-object",
            "trace_requirements": "not-an-object",
            "replay_requirements": "not-an-object",
            "rollback_requirements": "not-an-object",
            "fail_closed_rules": "not-a-list",
            "skill_card": "not-an-object",
        }
        specific_reasons = {
            "output_contract": "undefined_output_contract",
            "trace_requirements": "missing_trace_requirements",
            "replay_requirements": "replay_evidence_unavailable",
        }
        for field, value in malformed.items():
            with self.subTest(field=field):
                result = self.assert_contract_rejected({field: value})
                self.assertIn(
                    specific_reasons.get(
                        field, f"required_contract_field_invalid:{field}"
                    ),
                    result["reasons"],
                )

    def test_79_missing_required_contract_fields_fail(self):
        for field in ("skill_id", "skill_name", "description", "intended_use"):
            with self.subTest(field=field):
                contract = copy.deepcopy(self.fixture["skill_admission_contract"])
                contract.pop(field)
                result = evaluate_skill_admission(contract)
                self.assertFalse(result["ready_for_review"])
                self.assertIn(
                    f"required_contract_field_invalid:{field}", result["reasons"]
                )

    def test_80_fail_closed_rule_outcome_contradiction_invalidates_fixture(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["fail_closed_rules"][0]["outcome"] = "candidate_allowed"
        result = self.assert_fixture_rejected(fixture)
        self.assertIn("fail_closed_rule_semantics_invalid", result["reasons"])

    def test_81_default_posture_contradiction_invalidates_fixture(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["default_posture"][1] = "Undeclared permission = allowed"
        result = self.assert_fixture_rejected(fixture)
        self.assertIn("default_posture_invalid", result["reasons"])

    def test_82_permission_policy_contradictions_invalidate_fixture(self):
        mutations = {
            "capability_availability_is_permission": True,
            "installation_is_execution_authorization": True,
            "undeclared_permission_outcome": "candidate_allowed",
            "permission_escalation_outcome": "candidate_allowed",
        }
        for field, value in mutations.items():
            with self.subTest(field=field):
                fixture = copy.deepcopy(self.fixture)
                fixture["permission_policy"][field] = value
                result = self.assert_fixture_rejected(fixture)
                self.assertIn("permission_policy_semantics_invalid", result["reasons"])

    def test_83_invalid_contract_timestamps_fail_closed(self):
        expected_reasons = {
            "scan_timestamp": "invalid_scan_timestamp",
            "last_reassessment": "invalid_last_reassessment",
            "expiration_date": "invalid_expiration_date",
        }
        for field in (
            "scan_timestamp",
            "last_reassessment",
            "expiration_date",
        ):
            with self.subTest(field=field):
                result = self.assert_contract_rejected({field: "not-a-timestamp"})
                self.assertIn(expected_reasons[field], result["reasons"])

    def test_84_missing_contract_timestamps_fail_closed(self):
        expected_reasons = {
            "scan_timestamp": "invalid_scan_timestamp",
            "last_reassessment": "invalid_last_reassessment",
            "expiration_date": "invalid_expiration_date",
        }
        for field in (
            "scan_timestamp",
            "last_reassessment",
            "expiration_date",
        ):
            with self.subTest(field=field):
                result = self.assert_contract_rejected({field: None})
                self.assertIn(expected_reasons[field], result["reasons"])

    def test_85_invalid_or_missing_reassessment_interval_fails_closed(self):
        for interval in (None, "", "soon", "P0D", "P-1D"):
            with self.subTest(interval=interval):
                result = self.assert_contract_rejected(
                    {"reassessment_interval": interval}
                )
                self.assertIn("invalid_reassessment_interval", result["reasons"])

    def test_86_invalid_or_missing_evaluation_time_fails_closed(self):
        for evaluation_time in (None, "", "not-a-timestamp"):
            with self.subTest(evaluation_time=evaluation_time):
                result = self.assert_contract_rejected(
                    {}, {"evaluation_time": evaluation_time}
                )
                self.assertIn("invalid_evaluation_time", result["reasons"])

    def test_87_altered_case_id_semantics_invalidate_fixture(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["fixture_cases"][0]["case_id"] = (
            "case_01_complete_synthetic_low_risk_jetson_diagnostic_tampered"
        )
        result = self.assert_fixture_rejected(fixture)
        self.assertIn("fixture_cases_not_exactly_40", result["reasons"])

    def test_88_altered_case_type_semantics_invalidate_fixture(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["fixture_cases"][0]["case_type"] = "execution_approval_granted"
        result = self.assert_fixture_rejected(fixture)
        self.assertIn("fixture_cases_not_exactly_40", result["reasons"])

    def test_89_registry_final_approval_contradiction_invalidates_fixture(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["capability_registry_entry"]["evidence_status"][
            "final_approval"
        ] = True
        result = self.assert_fixture_rejected(fixture)
        self.assertIn("registry_final_approval_boundary_invalid", result["reasons"])

    def test_90_registry_skill_execution_contradiction_invalidates_fixture(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["capability_registry_entry"]["runtime_constraints"][
            "skill_execution_by_evaluator"
        ] = True
        result = self.assert_fixture_rejected(fixture)
        self.assertIn("registry_execution_boundary_invalid", result["reasons"])

    def test_91_registry_governance_owner_contradiction_invalidates_fixture(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["capability_registry_entry"]["governance_owner"] = "external-skill"
        result = self.assert_fixture_rejected(fixture)
        self.assertIn("capability_registry_entry_governance_invalid", result["reasons"])

    def test_92_supply_chain_dependency_contradiction_invalidates_fixture(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["supply_chain_positioning"]["dependency_status"] = (
            "nvidia_skills_is_an_aaos_dependency"
        )
        result = self.assert_fixture_rejected(fixture)
        self.assertIn("supply_chain_positioning_invalid", result["reasons"])

    def test_93_supply_chain_authority_contradictions_invalidate_fixture(self):
        mutations = {
            "external_artifact_role": "NVIDIA skills are governance authority.",
            "aaos_role": "AAOS delegates admission decisions to the skill.",
            "vendor_governance": "AAOS governance is vendor-controlled.",
        }
        for field, value in mutations.items():
            with self.subTest(field=field):
                fixture = copy.deepcopy(self.fixture)
                fixture["supply_chain_positioning"][field] = value
                result = self.assert_fixture_rejected(fixture)
                self.assertIn("supply_chain_positioning_invalid", result["reasons"])

    def test_94_malformed_permission_scope_types_fail_closed(self):
        for field in (
            "allowed_network_domains",
            "blocked_network_domains",
            "allowed_file_scopes",
            "blocked_file_scopes",
            "allowed_command_classes",
            "blocked_command_classes",
            "required_mcp_servers",
            "environment_variables",
        ):
            with self.subTest(field=field):
                result = self.assert_contract_rejected({field: "not-a-scope-list"})
                self.assertIn(
                    f"permission_scope_invalid:{field}", result["reasons"]
                )

    def test_95_mismatched_admission_policy_binding_fails(self):
        result = self.assert_contract_rejected(
            {
                "immutable_review_binding.admission_policy_version":
                    "synthetic-different-policy-version"
            }
        )
        self.assertIn("immutable_review_binding_mismatch", result["reasons"])
        self.assertIn(
            "AAOS remains the decision sovereignty layer.",
            self.fixture["required_boundary_statements"],
        )

    def test_96_high_risk_case_evidence_is_immutably_bound(self):
        case = self.fixture_case(
            "case_27_high_risk_physical_action_without_sandbox_and_review_blocked"
        )
        reviewed = case["contract_overrides"][
            "immutable_review_binding.reviewed_evidence_set"
        ]
        self.assertEqual(
            set(reviewed),
            {
                "synthetic-signature-placeholder-not-cryptographic",
                "synthetic-scan-evidence-fixture-not-a-real-scan-result",
                "synthetic-signature-verification-evidence",
                "synthetic-high-risk-benchmark-evidence-not-a-real-result",
                "synthetic-high-risk-evaluation-evidence-not-a-real-result",
            },
        )
        result = self.assert_case_matches_fixture(case["case_id"])
        self.assertNotIn("reviewed_evidence_binding_mismatch", result["reasons"])

    def test_97_permission_overdeclaration_fails_least_privilege(self):
        result = self.assert_contract_rejected(
            {
                "required_permissions.network": "restricted_outbound",
                "network_access": "restricted_outbound",
                "observed_required_permissions.network": "none",
                "allowed_network_domains": ["synthetic.example.invalid"],
            }
        )
        self.assertIn("permission_overdeclaration", result["reasons"])
        self.assertIn("permission_mismatch_detected", result["outputs"])

    def test_98_registry_skill_identity_must_match_contract(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["capability_registry_entry"]["skill_id"] = "synthetic-other-skill"
        result = self.assert_fixture_rejected(fixture)
        self.assertIn("registry_skill_identity_mismatch", result["reasons"])

    def test_99_registry_risk_acceptance_claim_is_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["capability_registry_entry"]["evidence_status"][
            "risk_accepted"
        ] = True
        result = self.assert_fixture_rejected(fixture)
        self.assertIn("registry_forbidden_governance_claim", result["reasons"])

    def test_100_registry_decision_proof_sealing_claim_is_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["capability_registry_entry"]["evidence_status"][
            "decision_proof_sealed"
        ] = True
        result = self.assert_fixture_rejected(fixture)
        self.assertIn("registry_forbidden_governance_claim", result["reasons"])

    def test_101_jetson_specimen_identity_is_bound_to_contract(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["skill_admission_contract"]["skill_id"] = "synthetic-other-skill"
        result = self.assert_fixture_rejected(fixture)
        self.assertIn("synthetic_jetson_contract_binding_invalid", result["reasons"])

    def test_102_scalar_evaluation_artifacts_fail_closed_without_exception(self):
        result = self.assert_contract_rejected({"evaluation_artifacts": 1})
        self.assertIn(
            "required_contract_field_invalid:evaluation_artifacts",
            result["reasons"],
        )

    def test_103_unhashable_scope_item_fails_closed_without_exception(self):
        result = self.assert_contract_rejected(
            {"allowed_network_domains": [{"domain": "synthetic.example.invalid"}]}
        )
        self.assertIn(
            "permission_scope_invalid:allowed_network_domains", result["reasons"]
        )

    def test_104_signature_and_scan_requirements_cannot_be_disabled(self):
        result = self.assert_contract_rejected(
            {
                "evidence_requirements.signature_required": False,
                "evidence_requirements.signature_verification_evidence_required": False,
                "evidence_requirements.scan_required": False,
                "signature": None,
                "signature_verification_evidence": None,
                "scan_report": None,
            }
        )
        self.assertIn("evidence_requirement_policy_invalid", result["reasons"])
        self.assertIn("required_signature_missing", result["reasons"])
        self.assertIn("signature_verification_evidence_missing", result["reasons"])
        self.assertIn("required_scan_missing", result["reasons"])

    def test_105_reviewed_evidence_binding_must_be_exact(self):
        binding = copy.deepcopy(
            self.fixture["skill_admission_contract"]["immutable_review_binding"]
        )
        binding["reviewed_evidence_set"].append("synthetic-stale-evidence-reference")
        result = self.assert_contract_rejected({"immutable_review_binding": binding})
        self.assertIn("reviewed_evidence_binding_mismatch", result["reasons"])

    def test_106_registry_artifact_identity_binds_permissions_and_evidence(self):
        contract = self.fixture["skill_admission_contract"]
        binding = contract["immutable_review_binding"]
        identity = self.fixture["capability_registry_entry"]["artifact_identity"]
        self.assertEqual(
            identity["reviewed_permission_declaration"],
            binding["reviewed_permission_declaration"],
        )
        self.assertEqual(
            set(identity["reviewed_evidence_set"]),
            set(binding["reviewed_evidence_set"]),
        )
        fixture = copy.deepcopy(self.fixture)
        fixture["capability_registry_entry"]["artifact_identity"].pop(
            "reviewed_evidence_set"
        )
        result = self.assert_fixture_rejected(fixture)
        self.assertIn("registry_artifact_identity_mismatch", result["reasons"])

    def test_107_signature_change_invalidates_reviewed_evidence_binding(self):
        result = self.assert_contract_rejected(
            {"signature": "synthetic-changed-signature-not-cryptographic"}
        )
        self.assertIn("reviewed_evidence_binding_mismatch", result["reasons"])


if __name__ == "__main__":
    unittest.main()
