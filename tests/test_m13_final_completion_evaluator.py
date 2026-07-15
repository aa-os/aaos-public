import copy
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import runtime.m13_final_completion_evaluator as final_completion_evaluator  # noqa: E402
from runtime.m13_final_completion_evaluator import (  # noqa: E402
    EXPECTED_HISTORICAL_README_SNAPSHOT_SHA256,
    HISTORICAL_README_SNAPSHOT_EVIDENCE_ROLE,
    HISTORICAL_README_SNAPSHOT_PATH,
    HISTORICAL_README_SNAPSHOT_PHASE,
    HISTORICAL_README_SNAPSHOT_SOURCE_BLOB,
    HISTORICAL_README_SNAPSHOT_SOURCE_COMMIT,
    README_RELEASE_ENTRY,
    README_STATUS,
    evaluate_m13_final_completion,
    load_historical_readme_snapshot,
)
from runtime.repository_artifact_digest import (  # noqa: E402
    canonicalize_utf8_repository_text,
)


ARTIFACT_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m13-final-completion-release-state.json"
)
README_PATH = ROOT / "README.md"
SNAPSHOT_PATH = ROOT / HISTORICAL_README_SNAPSHOT_PATH

FORBIDDEN_RESULT_KEYS = {
    "github_release_created",
    "release_tag_created_by_evaluator",
    "decision_proof_sealed_by_evaluator",
    "sealed_by_external_consumer",
    "authority_transferred",
    "risk_accepted_by_evaluator",
    "audit_closed_by_evaluator",
    "waiver_granted_by_evaluator",
    "final_governance_judgment_by_evaluator",
}


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_text(path):
    with path.open(encoding="utf-8") as handle:
        return handle.read()


class M13FinalCompletionEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.artifact = load_json(ARTIFACT_PATH)
        self.readme_text = load_historical_readme_snapshot(ROOT)

    def evaluate(self, artifact=None, readme_text=None, repository_root=None):
        return evaluate_m13_final_completion(
            self.artifact if artifact is None else artifact,
            readme_text=readme_text,
            repository_root=repository_root,
        )

    def write_default_snapshot(self, repository_root, raw):
        path = Path(repository_root) / HISTORICAL_README_SNAPSHOT_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return path

    def test_valid_final_m13_completion_state_prepares_v012_release_state(self):
        result = self.evaluate()

        self.assertTrue(result["m13_final_completion_valid"])
        self.assertFalse(result["m13_final_completion_invalid"])
        self.assertTrue(result["m13_completion_declared"])
        self.assertTrue(result["issue_176_closes_on_merge"])
        self.assertTrue(result["repository_release_state_prepared"])
        self.assertTrue(result["github_release_pending_manual_publication"])
        self.assertEqual(result["final_completion_findings"], [])
        self.assertEqual(result["missing_evidence"], [])
        for forbidden_key in FORBIDDEN_RESULT_KEYS:
            self.assertNotIn(forbidden_key, result)

    def test_historical_readme_snapshot_identity_is_explicit_and_bound(self):
        self.assertEqual(
            HISTORICAL_README_SNAPSHOT_PATH,
            (
                "examples/public-integration-pack-pilot/"
                "m13-final-completion-readme-snapshot.md"
            ),
        )
        self.assertEqual(
            HISTORICAL_README_SNAPSHOT_SOURCE_COMMIT,
            "d387e824f8c01c5afd6625982bb4f2d9fa1b829d",
        )
        self.assertEqual(
            HISTORICAL_README_SNAPSHOT_SOURCE_BLOB,
            "de1f4483fa0a2b1b41edc386583260ea7b409438",
        )
        self.assertEqual(
            HISTORICAL_README_SNAPSHOT_PHASE,
            "m13_final_completion_v0_12_release_state",
        )
        self.assertEqual(
            HISTORICAL_README_SNAPSHOT_EVIDENCE_ROLE,
            "post_release_auxiliary_historical_readme_evidence",
        )

        raw = SNAPSHOT_PATH.read_bytes()
        canonical = canonicalize_utf8_repository_text(raw)
        git_blob = hashlib.sha1(
            f"blob {len(canonical)}\0".encode("ascii") + canonical,
            usedforsecurity=False,
        ).hexdigest()
        canonical_digest = hashlib.sha256(canonical).hexdigest()
        self.assertEqual(git_blob, HISTORICAL_README_SNAPSHOT_SOURCE_BLOB)
        self.assertEqual(
            canonical_digest,
            EXPECTED_HISTORICAL_README_SNAPSHOT_SHA256,
        )

    def test_default_historical_snapshot_is_validated_independent_of_cwd(self):
        original_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as unrelated_cwd:
            try:
                os.chdir(unrelated_cwd)
                result = evaluate_m13_final_completion(self.artifact)
            finally:
                os.chdir(original_cwd)

        self.assertTrue(result["m13_final_completion_valid"])
        self.assertTrue(result["m13_completion_declared"])
        self.assertEqual(result["final_completion_findings"], [])

    def test_explicit_valid_historical_readme_text_still_passes(self):
        with tempfile.TemporaryDirectory() as empty_root:
            result = self.evaluate(
                readme_text=self.readme_text,
                repository_root=empty_root,
            )

        self.assertTrue(result["m13_final_completion_valid"])
        self.assertTrue(result["m13_completion_declared"])

    def test_missing_default_historical_snapshot_fails_closed(self):
        with tempfile.TemporaryDirectory() as empty_root:
            result = self.evaluate(repository_root=empty_root)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertFalse(result["m13_completion_declared"])
        self.assertIn(
            "historical_readme_snapshot_missing",
            result["final_completion_findings"],
        )

    def test_omitting_readme_text_cannot_bypass_snapshot_digest_mismatch(self):
        raw = SNAPSHOT_PATH.read_bytes()
        target = b"# AAOS Public"
        self.assertEqual(raw.count(target), 1)
        mutated = raw.replace(target, b"# AXOS Public", 1)
        self.assertNotEqual(mutated, raw)

        with tempfile.TemporaryDirectory() as repository_root:
            self.write_default_snapshot(repository_root, mutated)
            result = self.evaluate(repository_root=repository_root)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertFalse(result["m13_completion_declared"])
        self.assertIn(
            "historical_readme_snapshot_digest_mismatch",
            result["final_completion_findings"],
        )

    def test_malformed_utf8_default_historical_snapshot_fails_closed(self):
        with tempfile.TemporaryDirectory() as repository_root:
            self.write_default_snapshot(repository_root, b"\xffhistorical-readme")
            result = self.evaluate(repository_root=repository_root)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn(
            "historical_readme_snapshot_invalid_utf8",
            result["final_completion_findings"],
        )

    def test_lone_cr_default_historical_snapshot_fails_closed(self):
        with tempfile.TemporaryDirectory() as repository_root:
            self.write_default_snapshot(repository_root, b"historical\rreadme\n")
            result = self.evaluate(repository_root=repository_root)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn(
            "historical_readme_snapshot_lone_cr",
            result["final_completion_findings"],
        )

    def test_path_substituted_default_historical_snapshot_fails_closed(self):
        with patch.object(
            final_completion_evaluator,
            "HISTORICAL_README_SNAPSHOT_PATH",
            "../README.md",
        ):
            result = self.evaluate(repository_root=ROOT)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn(
            "historical_readme_snapshot_path_invalid",
            result["final_completion_findings"],
        )

    def test_current_readme_is_not_an_alternate_final_completion_source(self):
        current_readme = load_text(README_PATH)
        self.assertNotEqual(current_readme, self.readme_text)
        self.assertTrue(self.evaluate()["m13_final_completion_valid"])

        current_result = self.evaluate(readme_text=current_readme)

        self.assertFalse(current_result["m13_final_completion_valid"])
        self.assertIn(
            "readme_m13_completion_status_missing",
            current_result["final_completion_findings"],
        )
        self.assertIn(
            "readme_next_phase_final_planning_missing",
            current_result["final_completion_findings"],
        )

    def test_missing_177_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["runtime_approval_gate_evidence_pr"] = ""
        artifact["release_linkage_refs"]["runtime_enforced_approval_evidence_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn("missing_or_invalid_runtime_approval_gate_evidence_pr", result["final_completion_findings"])

    def test_missing_178_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["registry_drift_detection_pr"] = ""
        artifact["release_linkage_refs"]["registry_drift_detection_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn("missing_or_invalid_registry_drift_detection_pr", result["final_completion_findings"])

    def test_missing_194_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["authority_boundary_regression_fixtures_pr"] = ""
        artifact["release_linkage_refs"]["authority_boundary_regression_fixtures_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn(
            "missing_or_invalid_authority_boundary_regression_fixtures_pr",
            result["final_completion_findings"],
        )

    def test_missing_195_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["operational_readiness_checklist_pr"] = ""
        artifact["release_linkage_refs"]["operational_readiness_checklist_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn("missing_or_invalid_operational_readiness_checklist_pr", result["final_completion_findings"])

    def test_missing_196_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["external_consumer_onboarding_documentation_pr"] = ""
        artifact["release_linkage_refs"]["external_consumer_onboarding_documentation_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn(
            "missing_or_invalid_external_consumer_onboarding_documentation_pr",
            result["final_completion_findings"],
        )

    def test_missing_197_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["release_proof_linkage_specimen_pr"] = ""
        artifact["release_linkage_refs"]["release_proof_linkage_specimen_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn("missing_or_invalid_release_proof_linkage_specimen_pr", result["final_completion_findings"])

    def test_missing_198_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["completion_readiness_future_readme_path_pr"] = ""
        artifact["release_linkage_refs"]["completion_readiness_future_readme_path_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn(
            "missing_or_invalid_completion_readiness_future_readme_path_pr",
            result["final_completion_findings"],
        )

    def test_readme_missing_v012_release_entry_fails(self):
        self.assertEqual(self.readme_text.count(README_RELEASE_ENTRY), 1)
        readme_text = self.readme_text.replace(README_RELEASE_ENTRY, "", 1)
        self.assertNotEqual(readme_text, self.readme_text)

        result = self.evaluate(readme_text=readme_text)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn("readme_v0_12_0_release_entry_missing", result["final_completion_findings"])

    def test_readme_failing_to_declare_m13_complete_fails(self):
        replacement = (
            "M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11, and M12 are complete."
        )
        self.assertEqual(self.readme_text.count(README_STATUS), 1)
        readme_text = self.readme_text.replace(README_STATUS, replacement, 1)
        self.assertNotEqual(readme_text, self.readme_text)

        result = self.evaluate(readme_text=readme_text)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn("readme_m13_completion_status_missing", result["final_completion_findings"])

    def test_readme_leaving_m13_active_work_in_next_phase_fails(self):
        next_phase_heading = "## Next Phase"
        self.assertEqual(self.readme_text.count(next_phase_heading), 1)
        readme_text = self.readme_text.replace(
            next_phase_heading,
            (
                f"{next_phase_heading}\n\n"
                "M13 remains active work; final completion has not been declared."
            ),
            1,
        )
        self.assertNotEqual(readme_text, self.readme_text)

        result = self.evaluate(readme_text=readme_text)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn("readme_next_phase_m13_active_work_claim_detected", result["final_completion_findings"])

    def test_tracker_linkage_not_using_closes_176_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["tracker_issue_linkage"] = "Refs #176"
        artifact["release_linkage_refs"]["tracker_issue_linkage"] = "Refs #176"

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertIn("missing_or_invalid_tracker_issue_linkage", result["final_completion_findings"])

    def test_artifact_claiming_github_release_created_by_pr_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["github_release_created_by_pr"] = True

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn("github_release_created_by_pr_claim_detected", result["final_completion_findings"])

    def test_artifact_claiming_release_tag_created_by_pr_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["release_tag_created_by_pr"] = True

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn("release_tag_created_by_pr_claim_detected", result["final_completion_findings"])

    def test_evaluator_attempting_to_seal_decision_proof_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["evaluator_output"] = "decision_proof_sealed_by_evaluator"

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn("forbidden_evaluator_output_claim_detected", result["final_completion_findings"])

    def test_evaluator_attempting_to_transfer_authority_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["evaluator_output"] = "authority_transferred"

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn("forbidden_evaluator_output_claim_detected", result["final_completion_findings"])

    def test_evaluator_attempting_final_governance_judgment_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["evaluator_output"] = "final_governance_judgment_by_evaluator"

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn("forbidden_evaluator_output_claim_detected", result["final_completion_findings"])

    def test_negative_outer_output_cannot_hide_nested_authority_claim(self):
        artifact = copy.deepcopy(self.artifact)
        self.assertNotIn("evaluator_output", artifact)
        artifact["evaluator_output"] = {
            "status": "evidence_only",
            "decision": {
                "authority": "not_transferred",
                "waiver": "granted",
            },
        }
        self.assertNotEqual(artifact, self.artifact)

        result = self.evaluate(artifact)

        self.assertTrue(result["m13_final_completion_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn(
            "forbidden_evaluator_output_claim_detected",
            result["final_completion_findings"],
        )


if __name__ == "__main__":
    unittest.main()
