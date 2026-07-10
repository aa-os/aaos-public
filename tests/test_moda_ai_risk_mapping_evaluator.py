import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.moda_ai_risk_mapping_evaluator import (  # noqa: E402
    B6_CONTROL_CATEGORY,
    B6_REQUIRED_DECISION_PROOF_FIELDS,
    B6_SOURCE_LABEL,
    FORBIDDEN_EVALUATOR_OUTPUTS,
    REQUIRED_CHECKLIST_FIELDS,
    REQUIRED_CODES_BY_TYPE,
    REQUIRED_REASSESSMENT_FIELDS,
    REQUIRED_SECTORS,
    evaluate_moda_ai_risk_mapping_fixture,
)


FIXTURE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m14-moda-ai-risk-decision-proof-fixtures.json"
)


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class ModaAIRiskMappingEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.fixture = load_json(FIXTURE_PATH)

    def evaluate(self, fixture=None):
        return evaluate_moda_ai_risk_mapping_fixture(
            self.fixture if fixture is None else fixture
        )

    def mapping_by_code(self, fixture, risk_code):
        return next(
            mapping
            for mapping in fixture["taxonomy_mappings"]
            if mapping["risk_code"] == risk_code
        )

    def scenario_by_sector(self, fixture, sector):
        return next(
            scenario
            for scenario in fixture["sector_scenarios"]
            if scenario["sector"] == sector
        )

    def b6_first_class_control(self, fixture):
        return next(
            control
            for control in fixture["first_class_control_categories"]
            if control["risk_code"] == "B6"
        )

    def assert_forbidden_output_rejected(self, output):
        fixture = copy.deepcopy(self.fixture)
        fixture["simulated_evaluator_output"] = output

        result = self.evaluate(fixture)

        self.assertTrue(result["moda_ai_risk_mapping_invalid"])
        self.assertIn(
            f"forbidden_output_claim_detected:{output}",
            result["moda_ai_risk_mapping_findings"],
        )

    def test_complete_a_b_c_taxonomy_coverage_passes(self):
        result = self.evaluate()
        mapped_codes = {
            mapping["risk_code"] for mapping in self.fixture["taxonomy_mappings"]
        }

        self.assertTrue(result["moda_ai_risk_mapping_valid"])
        self.assertTrue(result["taxonomy_coverage_complete"])
        self.assertFalse(result["taxonomy_coverage_incomplete"])
        self.assertEqual(
            mapped_codes,
            set().union(*REQUIRED_CODES_BY_TYPE.values()),
        )
        self.assertEqual(result["moda_ai_risk_mapping_findings"], [])

    def test_incomplete_a_taxonomy_coverage_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["taxonomy_mappings"] = [
            mapping for mapping in fixture["taxonomy_mappings"] if mapping["risk_code"] != "A8"
        ]

        result = self.evaluate(fixture)

        self.assertTrue(result["taxonomy_coverage_incomplete"])
        self.assertTrue(result["moda_ai_risk_mapping_invalid"])
        self.assertIn("missing_taxonomy_code:A8", result["moda_ai_risk_mapping_findings"])

    def test_incomplete_b_taxonomy_coverage_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["taxonomy_mappings"] = [
            mapping for mapping in fixture["taxonomy_mappings"] if mapping["risk_code"] != "B5"
        ]

        result = self.evaluate(fixture)

        self.assertTrue(result["taxonomy_coverage_incomplete"])
        self.assertIn("missing_taxonomy_code:B5", result["moda_ai_risk_mapping_findings"])

    def test_incomplete_c_taxonomy_coverage_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["taxonomy_mappings"] = [
            mapping for mapping in fixture["taxonomy_mappings"] if mapping["risk_code"] != "C6"
        ]

        result = self.evaluate(fixture)

        self.assertTrue(result["taxonomy_coverage_incomplete"])
        self.assertIn("missing_taxonomy_code:C6", result["moda_ai_risk_mapping_findings"])

    def test_b6_uses_exact_source_label(self):
        result = self.evaluate()
        mapping = self.mapping_by_code(self.fixture, "B6")

        self.assertTrue(result["moda_ai_risk_mapping_valid"])
        self.assertEqual(mapping["source_label"], B6_SOURCE_LABEL)
        self.assertEqual(B6_SOURCE_LABEL, "AI autonomous agent unauthorized behavior")

    def test_b6_source_label_drift_fails(self):
        fixture = copy.deepcopy(self.fixture)
        self.mapping_by_code(fixture, "B6")["source_label"] = (
            "AI autonomous agent behavior outside authorization"
        )

        result = self.evaluate(fixture)

        self.assertTrue(result["moda_ai_risk_mapping_invalid"])
        self.assertIn("b6_exact_source_label_mismatch", result["moda_ai_risk_mapping_findings"])

    def test_b6_first_class_control_is_present(self):
        result = self.evaluate()
        control = self.b6_first_class_control(self.fixture)

        self.assertTrue(result["b6_first_class_control_present"])
        self.assertEqual(control["risk_code"], "B6")
        self.assertEqual(control["source_label"], B6_SOURCE_LABEL)
        self.assertEqual(control["aaos_control_category"], B6_CONTROL_CATEGORY)

    def test_missing_b6_first_class_control_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["first_class_control_categories"] = []

        result = self.evaluate(fixture)

        self.assertFalse(result["b6_first_class_control_present"])
        self.assertIn(
            "b6_first_class_control_missing_or_duplicate",
            result["moda_ai_risk_mapping_findings"],
        )

    def test_capture_verify_accumulate_checklist_is_complete(self):
        result = self.evaluate()

        self.assertTrue(result["decision_proof_checklist_complete"])
        self.assertFalse(result["decision_proof_checklist_incomplete"])
        for phase, required_fields in REQUIRED_CHECKLIST_FIELDS.items():
            actual_fields = {
                item["field"] for item in self.fixture["decision_proof_checklist"][phase]
            }
            self.assertTrue(required_fields.issubset(actual_fields))

    def test_incomplete_capture_verify_or_accumulate_checklist_fails(self):
        for phase in ("capture", "verify", "accumulate"):
            with self.subTest(phase=phase):
                fixture = copy.deepcopy(self.fixture)
                removed = fixture["decision_proof_checklist"][phase].pop(0)["field"]

                result = self.evaluate(fixture)

                self.assertTrue(result["decision_proof_checklist_incomplete"])
                self.assertIn(
                    f"missing_{phase}_checklist_field:{removed}",
                    result["moda_ai_risk_mapping_findings"],
                )

    def test_all_five_sector_scenarios_are_present(self):
        result = self.evaluate()
        sectors = {scenario["sector"] for scenario in self.fixture["sector_scenarios"]}

        self.assertTrue(result["sector_coverage_complete"])
        self.assertFalse(result["sector_coverage_incomplete"])
        self.assertEqual(sectors, REQUIRED_SECTORS)

    def test_missing_sector_scenario_fails(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["sector_scenarios"] = [
            scenario
            for scenario in fixture["sector_scenarios"]
            if scenario["sector"] != "labor"
        ]

        result = self.evaluate(fixture)

        self.assertTrue(result["sector_coverage_incomplete"])
        self.assertIn(
            "missing_sector_scenario:labor",
            result["moda_ai_risk_mapping_findings"],
        )

    def test_b6_permission_authorization_target_output_and_trace_fields_are_required(self):
        control = self.b6_first_class_control(self.fixture)

        self.assertEqual(
            set(control["required_decision_proof_fields"]),
            B6_REQUIRED_DECISION_PROOF_FIELDS,
        )
        self.assertTrue(all(control["requirements"].values()))

    def test_missing_b6_permission_authorization_target_output_or_trace_field_fails(self):
        for field in sorted(B6_REQUIRED_DECISION_PROOF_FIELDS):
            with self.subTest(field=field):
                fixture = copy.deepcopy(self.fixture)
                control = self.b6_first_class_control(fixture)
                control["required_decision_proof_fields"].remove(field)

                result = self.evaluate(fixture)

                self.assertIn(
                    f"b6_required_decision_proof_field_missing:{field}",
                    result["moda_ai_risk_mapping_findings"],
                )

    def test_missing_b6_boolean_requirement_fails(self):
        fixture = copy.deepcopy(self.fixture)
        control = self.b6_first_class_control(fixture)
        control["requirements"]["authorization_decision_required"] = False

        result = self.evaluate(fixture)

        self.assertIn(
            "b6_requirement_missing:authorization_decision_required",
            result["moda_ai_risk_mapping_findings"],
        )

    def test_serious_harm_screening_boundary_requires_review_without_clearance(self):
        result = self.evaluate()
        boundary = self.fixture["serious_harm_screening_boundary"]

        self.assertTrue(result["serious_harm_screening_required"])
        self.assertTrue(boundary["screening_required"])
        self.assertTrue(boundary["human_review_required"])
        self.assertFalse(boundary["final_legal_determination_made"])
        self.assertFalse(boundary["risk_acceptance_made"])
        self.assertNotIn("serious_harm_cleared", result)

    def test_serious_harm_clearance_claim_fails(self):
        self.assert_forbidden_output_rejected("serious_harm_cleared")

    def test_healthcare_has_sensitive_scope_serious_harm_screening_and_human_review(self):
        scenario = self.scenario_by_sector(self.fixture, "healthcare")

        self.assertEqual(
            scenario["sensitive_data_scope"],
            "restricted_health_and_personal_data",
        )
        self.assertEqual(
            scenario["serious_harm_screening"],
            "required_not_cleared_by_mapping",
        )
        self.assertTrue(scenario["human_review_required"])

    def test_healthcare_without_human_review_fails(self):
        fixture = copy.deepcopy(self.fixture)
        self.scenario_by_sector(fixture, "healthcare")["human_review_required"] = False

        result = self.evaluate(fixture)

        self.assertIn(
            "healthcare:human_review_required_missing",
            result["moda_ai_risk_mapping_findings"],
        )

    def test_finance_separates_analysis_capability_from_transaction_authority(self):
        scenario = self.scenario_by_sector(self.fixture, "finance")

        self.assertEqual(scenario["analysis_capability"], "analysis_and_recommendation_only")
        self.assertEqual(
            scenario["transaction_authority"],
            "not_granted_by_analysis_capability_or_mapping",
        )
        self.assertTrue(scenario["transaction_execution_requires_separate_authorization"])

    def test_finance_without_separate_transaction_authorization_fails(self):
        fixture = copy.deepcopy(self.fixture)
        scenario = self.scenario_by_sector(fixture, "finance")
        scenario["transaction_execution_requires_separate_authorization"] = False

        result = self.evaluate(fixture)

        self.assertIn(
            "finance:separate_transaction_authorization_missing",
            result["moda_ai_risk_mapping_findings"],
        )

    def test_education_and_labor_preserve_human_review_and_appealability(self):
        for sector in ("education", "labor"):
            with self.subTest(sector=sector):
                scenario = self.scenario_by_sector(self.fixture, sector)
                self.assertTrue(scenario["human_review_required"])
                self.assertTrue(scenario["appealability_required"])

    def test_government_service_uses_public_output_gate_and_pr_204_pattern(self):
        result = self.evaluate()
        scenario = self.scenario_by_sector(self.fixture, "government_service")

        self.assertTrue(result["public_output_gate_required"])
        self.assertTrue(scenario["public_output_gate_required"])
        self.assertEqual(scenario["public_output_gate_result"], "ready_for_review")
        self.assertIn("#204", scenario["related_control_pattern"])

    def test_government_service_without_public_output_gate_fails(self):
        fixture = copy.deepcopy(self.fixture)
        scenario = self.scenario_by_sector(fixture, "government_service")
        scenario["public_output_gate_required"] = False

        result = self.evaluate(fixture)

        self.assertIn(
            "government_service:public_output_gate_missing",
            result["moda_ai_risk_mapping_findings"],
        )

    def test_periodic_reassessment_fields_are_present_for_every_sector(self):
        result = self.evaluate()

        self.assertTrue(result["periodic_reassessment_required"])
        for scenario in self.fixture["sector_scenarios"]:
            reassessment = scenario["periodic_reassessment"]
            self.assertTrue(REQUIRED_REASSESSMENT_FIELDS.issubset(reassessment))
            self.assertTrue(reassessment["reassessment_required"])
            self.assertTrue(reassessment["reassessment_triggers"])
            self.assertEqual(reassessment["source_framework_version_at_assessment"], "v1.0")

    def test_legal_approval_violation_fails(self):
        self.assert_forbidden_output_rejected("legal_approval_granted")

    def test_regulatory_certification_violation_fails(self):
        self.assert_forbidden_output_rejected("regulatory_compliance_certified")

    def test_full_compliance_certification_violation_fails(self):
        self.assert_forbidden_output_rejected("full_compliance_certified")

    def test_regulated_deployment_approval_violation_fails(self):
        self.assert_forbidden_output_rejected("regulated_deployment_approved")

    def test_risk_acceptance_violation_fails(self):
        self.assert_forbidden_output_rejected("risk_accepted")

    def test_decision_proof_sealing_violation_fails(self):
        for output in (
            "decision_proof_sealed",
            "sealed_by_regulatory_mapping",
            "sealed_by_evaluator",
        ):
            with self.subTest(output=output):
                self.assert_forbidden_output_rejected(output)

    def test_final_risk_classification_violation_fails(self):
        self.assert_forbidden_output_rejected("final_risk_classification")

    def test_authority_transfer_violation_fails(self):
        self.assert_forbidden_output_rejected("authority_transferred")

    def test_m14_completion_violation_fails(self):
        self.assert_forbidden_output_rejected("m14_complete")

    def test_v0130_release_violation_fails(self):
        self.assert_forbidden_output_rejected("v0_13_0_released")

    def test_tracker_201_closure_violation_fails(self):
        self.assert_forbidden_output_rejected("closes_201")

    def test_every_forbidden_evaluator_output_is_rejected(self):
        self.assertEqual(
            set(self.fixture["forbidden_evaluator_outputs"]),
            FORBIDDEN_EVALUATOR_OUTPUTS,
        )
        for output in sorted(FORBIDDEN_EVALUATOR_OUTPUTS):
            with self.subTest(output=output):
                self.assert_forbidden_output_rejected(output)


if __name__ == "__main__":
    unittest.main()
