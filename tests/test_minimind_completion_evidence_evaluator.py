"""Repository-truth regressions for the MiniMind issue #235 repair."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]

from runtime.minimind_completion_evidence_evaluator import (  # noqa: E402
    CONSOLIDATED_SKELETON_PATH,
    EXPECTED_DECLARED_ARTIFACTS,
    MATRIX_PATH,
    RADAR_NODE_PATH,
    REQUIRED_AUTHORITY_BOUNDARIES,
    evaluate_minimind_completion_evidence,
)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class MiniMindCompletionEvidenceEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = load_json(MATRIX_PATH)
        cls.radar_text = RADAR_NODE_PATH.read_text(encoding="utf-8")

    def evaluate_matrix(self, payload: dict) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "matrix.json"
            path.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            return evaluate_minimind_completion_evidence(matrix_path=path)

    def evaluate_radar(self, text: str) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "minimind.yaml"
            path.write_text(text, encoding="utf-8")
            return evaluate_minimind_completion_evidence(radar_path=path)

    def requirement(self, requirement_id: str) -> dict:
        return next(
            row
            for row in self.matrix["requirements"]
            if row["requirement_id"] == requirement_id
        )

    def test_01_canonical_completion_evidence_passes(self):
        result = evaluate_minimind_completion_evidence()

        self.assertEqual(result["decision"], "pass")
        self.assertTrue(result["completion_evidence_valid"])
        self.assertTrue(result["radar_node_valid"])
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["requirements_evaluated"], 42)
        self.assertEqual(result["declared_issue_9_artifacts_evaluated"], 28)
        self.assertEqual(
            result["status_counts"],
            {
                "deferred": 26,
                "implemented": 1,
                "implemented_as_skeleton": 15,
            },
        )
        self.assertFalse(result["full_issue_9_implementation_claimed"])
        self.assertFalse(result["minimind_executed"])
        self.assertFalse(result["m15_scope_modified"])
        self.assertFalse(result["release_published"])

    def test_02_every_declared_issue_9_artifact_is_inventoried_once(self):
        issue_9_rows = [
            row
            for row in self.matrix["requirements"]
            if row["source_issue"] == "#9" and row["declared_path"] is not None
        ]
        paths = [row["declared_path"] for row in issue_9_rows]

        self.assertEqual(len(paths), len(set(paths)))
        self.assertEqual(set(paths), set(EXPECTED_DECLARED_ARTIFACTS))
        for row in issue_9_rows:
            with self.subTest(requirement_id=row["requirement_id"]):
                expected_type = EXPECTED_DECLARED_ARTIFACTS[row["declared_path"]]
                self.assertEqual(row["artifact_type"], expected_type)

    def test_03_contract_family_is_skeleton_not_full_implementation(self):
        contract_rows = [
            row
            for row in self.matrix["requirements"]
            if row["artifact_type"] == "contract"
        ]

        self.assertEqual(len(contract_rows), 5)
        self.assertTrue((ROOT / CONSOLIDATED_SKELETON_PATH).is_file())
        for row in contract_rows:
            with self.subTest(requirement_id=row["requirement_id"]):
                self.assertEqual(
                    row["implementation_status"], "implemented_as_skeleton"
                )
                self.assertEqual(row["path_disposition"], "renamed_and_consolidated")
                self.assertEqual(row["maintained_path"], CONSOLIDATED_SKELETON_PATH)
                self.assertFalse(row["runtime_implementation_claimed"])
                self.assertFalse(row["full_runtime_implementation"])
                self.assertFalse((ROOT / row["declared_path"]).exists())

    def test_04_unimplemented_schemas_runtimes_examples_and_tests_are_deferred(self):
        deferred_types = {"schema", "runtime_evaluator", "example", "test"}
        rows = [
            row
            for row in self.matrix["requirements"]
            if row["artifact_type"] in deferred_types
        ]

        self.assertEqual(len(rows), 23)
        for row in rows:
            with self.subTest(requirement_id=row["requirement_id"]):
                self.assertEqual(row["implementation_status"], "deferred")
                self.assertTrue(row["deferred_reason"])
                self.assertIsNone(row["maintained_path"])
                self.assertFalse((ROOT / row["declared_path"]).exists())

    def test_05_radar_node_is_minimind_specific_and_preserves_authority_boundary(self):
        folded = self.radar_text.casefold()

        self.assertIn(
            'source_url: "https://github.com/jingyaogong/minimind"',
            self.radar_text,
        )
        self.assertIn('source_name: "MiniMind"', self.radar_text)
        self.assertIn('source_type: "model-runtime"', self.radar_text)
        self.assertNotIn("this directory contains tests", folded)
        self.assertNotIn("tests should verify", folded)
        for statement in REQUIRED_AUTHORITY_BOUNDARIES:
            with self.subTest(statement=statement):
                self.assertIn(statement, folded)

    def test_06_unrelated_placeholder_substitution_fails_closed(self):
        old_placeholder = """description: |
  This directory contains tests for governance contracts, schemas, and runtime evaluators.
  Tests should verify that external sources remain evidence candidates and do not become governance authorities.
"""

        result = self.evaluate_radar(old_placeholder)

        self.assertEqual(result["decision"], "fail_closed")
        self.assertFalse(result["radar_node_valid"])
        self.assertIn(
            "minimind_radar_placeholder_content:this_directory_contains_tests",
            result["findings"],
        )
        self.assertIn(
            "minimind_radar_placeholder_content:tests_should_verify",
            result["findings"],
        )

    def test_07_declared_implemented_artifact_must_exist(self):
        payload = copy.deepcopy(self.matrix)
        row = next(
            item
            for item in payload["requirements"]
            if item["requirement_id"] == "MM-REPAIR-RADAR-001"
        )
        row["maintained_path"] = "examples/radar-nodes/not-present.yaml"

        result = self.evaluate_matrix(payload)

        self.assertIn(
            "declared_implemented_artifact_missing:MM-REPAIR-RADAR-001",
            result["findings"],
        )

    def test_08_implemented_artifact_requires_evidence_reference(self):
        payload = copy.deepcopy(self.matrix)
        row = next(
            item
            for item in payload["requirements"]
            if item["requirement_id"] == "MM-REPAIR-RADAR-001"
        )
        row["evidence_reference"] = None

        result = self.evaluate_matrix(payload)

        self.assertIn(
            "completed_artifact_missing_evidence:MM-REPAIR-RADAR-001",
            result["findings"],
        )

    def test_09_deferred_artifact_requires_explicit_reason(self):
        payload = copy.deepcopy(self.matrix)
        row = next(
            item
            for item in payload["requirements"]
            if item["requirement_id"] == "MM-SCHEMA-001"
        )
        row["deferred_reason"] = ""

        result = self.evaluate_matrix(payload)

        self.assertIn(
            "deferred_reason_missing:MM-SCHEMA-001",
            result["findings"],
        )

    def test_10_skeleton_cannot_claim_full_runtime_implementation(self):
        payload = copy.deepcopy(self.matrix)
        row = next(
            item
            for item in payload["requirements"]
            if item["requirement_id"] == "MM-CONTRACT-001"
        )
        row["full_runtime_implementation"] = True

        result = self.evaluate_matrix(payload)

        self.assertIn(
            "skeleton_represented_as_full_runtime:MM-CONTRACT-001",
            result["findings"],
        )

    def test_11_authority_and_proof_sealing_claims_fail_closed(self):
        cases = {
            "governance": (
                'not_authority_statement: "Runtime specimen, not governance authority; verification subject, not verification authority; model output, not decision approval; local inference, not sovereignty proof."',
                'not_authority_statement: "MiniMind is a governance authority."',
                "minimind_governance_authority_claimed",
            ),
            "verification": (
                'not_authority_statement: "Runtime specimen, not governance authority; verification subject, not verification authority; model output, not decision approval; local inference, not sovereignty proof."',
                'not_authority_statement: "MiniMind is a verification authority."',
                "minimind_verification_authority_claimed",
            ),
            "decision-proof": (
                'risk_if_misclassified: "A local, inspectable model could be mistaken for safety proof, production permission, verification authority, decision approval, or evidence that AAOS sovereignty controls are unnecessary."',
                'risk_if_misclassified: "MiniMind seals Decision Proof."',
                "decision_proof_sealed_by_minimind",
            ),
            "learning-proof": (
                'risk_if_misclassified: "A local, inspectable model could be mistaken for safety proof, production permission, verification authority, decision approval, or evidence that AAOS sovereignty controls are unnecessary."',
                'risk_if_misclassified: "Learning Proof is sealed by MiniMind."',
                "learning_proof_sealed_by_minimind",
            ),
        }

        for case, (old, new, expected_finding) in cases.items():
            with self.subTest(case=case):
                result = self.evaluate_radar(self.radar_text.replace(old, new))
                self.assertEqual(result["decision"], "fail_closed")
                self.assertIn(expected_finding, result["findings"])

    def test_12_m15_and_release_boundary_cannot_be_rewritten(self):
        payload = copy.deepcopy(self.matrix)
        payload["scope_boundary"]["m15_status_observed"] = "completed"
        payload["scope_boundary"]["m15_scope_modified"] = True
        payload["scope_boundary"]["release_published"] = True

        result = self.evaluate_matrix(payload)

        self.assertIn("m15_or_release_scope_boundary_invalid", result["findings"])

    def test_13_matrix_cannot_claim_full_issue_9_implementation(self):
        payload = copy.deepcopy(self.matrix)
        payload["full_issue_9_implementation_claimed"] = True

        result = self.evaluate_matrix(payload)

        self.assertIn("full_issue_9_implementation_claimed", result["findings"])

    def test_14_static_repair_contains_no_minimind_or_network_runtime(self):
        evaluator_text = (
            ROOT / "runtime" / "minimind_completion_evidence_evaluator.py"
        ).read_text(encoding="utf-8")
        lowered = evaluator_text.casefold()

        for forbidden_import in (
            "import requests",
            "import socket",
            "import subprocess",
            "import torch",
            "import transformers",
            "import urllib",
            "from minimind",
            "import minimind",
        ):
            with self.subTest(forbidden_import=forbidden_import):
                self.assertNotIn(forbidden_import, lowered)
        self.assertEqual(
            self.matrix["execution_boundary"],
            {
                "minimind_executed": False,
                "model_loaded": False,
                "inference_run": False,
                "training_or_fine_tuning_run": False,
                "live_tools_added": False,
                "credentials_added": False,
                "network_calls_added": False,
                "production_execution_added": False,
            },
        )


if __name__ == "__main__":
    unittest.main()
