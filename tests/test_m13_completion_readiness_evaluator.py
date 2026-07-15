import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.m13_completion_readiness_evaluator import (  # noqa: E402
    EXPECTED_HISTORICAL_README_SNAPSHOT_SHA256,
    HISTORICAL_README_SNAPSHOT_EVIDENCE_ROLE,
    HISTORICAL_README_SNAPSHOT_PATH,
    HISTORICAL_README_SNAPSHOT_PHASE,
    HISTORICAL_README_SNAPSHOT_SOURCE_BLOB,
    HISTORICAL_README_SNAPSHOT_SOURCE_COMMIT,
    evaluate_m13_completion_readiness,
    load_historical_readme_snapshot,
)
from runtime.authority_semantics import (  # noqa: E402
    EXPLICIT_NEGATIVE_AUTHORITY_STRINGS,
    STRUCTURED_AUTHORITY_FIELDS,
)
from runtime.repository_artifact_digest import (  # noqa: E402
    canonicalize_utf8_repository_text,
)


ARTIFACT_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m13-completion-readiness-future-readme-path.json"
)
README_PATH = ROOT / "README.md"
SNAPSHOT_PATH = ROOT / HISTORICAL_README_SNAPSHOT_PATH


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_text(path):
    with path.open(encoding="utf-8") as handle:
        return handle.read()


class M13CompletionReadinessEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.artifact = load_json(ARTIFACT_PATH)
        self.readme_text = load_historical_readme_snapshot(ROOT)

    def evaluate(self, artifact=None, readme_text=None):
        return evaluate_m13_completion_readiness(
            self.artifact if artifact is None else artifact,
            self.readme_text if readme_text is None else readme_text,
        )

    def mutate_semantic_boundary(self, key, original, replacement):
        semantic_boundaries = self.artifact["semantic_boundaries"]
        self.assertEqual(list(semantic_boundaries).count(key), 1)
        self.assertEqual(semantic_boundaries[key], original)
        artifact = copy.deepcopy(self.artifact)
        artifact["semantic_boundaries"][key] = replacement
        self.assertNotEqual(artifact, self.artifact)
        self.assertNotEqual(artifact["semantic_boundaries"][key], original)
        return artifact

    def test_valid_completion_readiness_and_readme_future_path_ready_for_review(self):
        result = self.evaluate()

        self.assertTrue(result["completion_readiness_valid"])
        self.assertFalse(result["completion_readiness_invalid"])
        self.assertTrue(result["completion_readiness_coverage_complete"])
        self.assertTrue(result["completion_ready_for_review"])
        self.assertFalse(result["completion_not_ready"])
        self.assertTrue(result["readme_future_path_present"])
        self.assertTrue(result["release_status_future_only"])
        self.assertEqual(result["completion_readiness_findings"], [])
        self.assertEqual(result["missing_evidence"], [])

    def test_historical_readme_snapshot_identity_is_explicit_and_bound(self):
        self.assertEqual(
            HISTORICAL_README_SNAPSHOT_PATH,
            (
                "examples/public-integration-pack-pilot/"
                "m13-completion-readiness-readme-snapshot.md"
            ),
        )
        self.assertEqual(
            HISTORICAL_README_SNAPSHOT_SOURCE_COMMIT,
            "4e2485a0390a81aa31508777dce5cccc3f344b62",
        )
        self.assertEqual(
            HISTORICAL_README_SNAPSHOT_SOURCE_BLOB,
            "5d77feffb9dcdcaf527c69e154fae76351115da8",
        )
        self.assertEqual(
            HISTORICAL_README_SNAPSHOT_PHASE,
            "m13_completion_readiness_pre_final_transition",
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

    def test_current_readme_is_not_an_alternate_completion_readiness_source(self):
        current_readme = load_text(README_PATH)
        self.assertNotEqual(current_readme, self.readme_text)
        self.assertTrue(self.evaluate()["completion_readiness_valid"])

        current_result = self.evaluate(readme_text=current_readme)

        self.assertFalse(current_result["completion_readiness_valid"])
        self.assertIn(
            "readme_m13_completion_claim_detected",
            current_result["completion_readiness_findings"],
        )
        self.assertIn(
            "readme_v0_12_0_released_claim_detected",
            current_result["completion_readiness_findings"],
        )

    def test_missing_177_runtime_approval_evidence_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["runtime_approval_gate_evidence_pr"] = ""
        artifact["release_linkage_refs"]["runtime_enforced_approval_evidence_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertTrue(result["completion_readiness_coverage_incomplete"])
        self.assertIn("missing_runtime_approval_gate_evidence_pr", result["completion_readiness_findings"])

    def test_missing_178_registry_drift_detection_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["registry_drift_detection_pr"] = ""
        artifact["release_linkage_refs"]["registry_drift_detection_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertTrue(result["completion_readiness_coverage_incomplete"])
        self.assertIn("missing_registry_drift_detection_pr", result["completion_readiness_findings"])

    def test_missing_194_authority_boundary_regression_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["authority_boundary_regression_fixtures_pr"] = ""
        artifact["release_linkage_refs"]["authority_boundary_regression_fixtures_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertTrue(result["completion_readiness_coverage_incomplete"])
        self.assertIn(
            "missing_authority_boundary_regression_fixtures_pr",
            result["completion_readiness_findings"],
        )

    def test_missing_195_operational_readiness_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["operational_readiness_checklist_pr"] = ""
        artifact["release_linkage_refs"]["operational_readiness_checklist_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertTrue(result["completion_readiness_coverage_incomplete"])
        self.assertIn("missing_operational_readiness_checklist_pr", result["completion_readiness_findings"])

    def test_missing_196_onboarding_documentation_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["external_consumer_onboarding_documentation_pr"] = ""
        artifact["release_linkage_refs"]["external_consumer_onboarding_documentation_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertTrue(result["completion_readiness_coverage_incomplete"])
        self.assertIn(
            "missing_external_consumer_onboarding_documentation_pr",
            result["completion_readiness_findings"],
        )

    def test_missing_197_release_proof_linkage_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["release_proof_linkage_specimen_pr"] = ""
        artifact["release_linkage_refs"]["release_proof_linkage_specimen_pr"] = ""

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertTrue(result["completion_readiness_coverage_incomplete"])
        self.assertIn("missing_release_proof_linkage_specimen_pr", result["completion_readiness_findings"])

    def test_readme_future_path_missing_fails(self):
        target = (
            "Future README status path: v0.12.0 / M13 remains a future-only "
            "path until a final completion PR."
        )
        self.assertEqual(self.readme_text.count(target), 1)
        readme_text = self.readme_text.replace(
            target,
            "",
            1,
        )
        self.assertNotEqual(readme_text, self.readme_text)

        result = self.evaluate(readme_text=readme_text)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertFalse(result["readme_future_path_present"])
        self.assertIn("readme_future_status_path_missing", result["completion_readiness_findings"])

    def test_readme_declaring_m13_complete_fails(self):
        result = self.evaluate(readme_text=self.readme_text + "\nM13 complete\n")

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertIn("readme_m13_completion_claim_detected", result["completion_readiness_findings"])

    def test_readme_declaring_v012_released_fails(self):
        result = self.evaluate(readme_text=self.readme_text + "\nv0.12.0 released\n")

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertIn("readme_v0_12_0_released_claim_detected", result["completion_readiness_findings"])

    def test_readme_closes_176_language_fails(self):
        result = self.evaluate(readme_text=self.readme_text + "\nCloses #176\n")

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertIn(
            "readme_tracker_issue_176_closure_claim_detected",
            result["completion_readiness_findings"],
        )

    def test_completion_ready_for_review_as_m13_complete_fails(self):
        artifact = self.mutate_semantic_boundary(
            "completion_ready_for_review_boundary",
            "completion_ready_for_review is not m13_complete.",
            "completion_ready_for_review is m13_complete.",
        )

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertIn(
            "completion_ready_for_review_m13_complete_claim_detected",
            result["completion_readiness_findings"],
        )

    def test_readme_future_path_present_as_released_fails(self):
        artifact = self.mutate_semantic_boundary(
            "readme_future_path_boundary",
            "readme_future_path_present is not released.",
            "readme_future_path_present is released.",
        )

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertIn(
            "readme_future_path_released_claim_detected",
            result["completion_readiness_findings"],
        )

    def test_release_ready_for_review_as_release_approved_fails(self):
        artifact = self.mutate_semantic_boundary(
            "release_ready_for_review_boundary",
            "release_ready_for_review is not release_approved.",
            "release_ready_for_review is release_approved.",
        )

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertIn(
            "release_ready_for_review_approval_claim_detected",
            result["completion_readiness_findings"],
        )

    def test_evidence_complete_as_sealed_fails(self):
        artifact = self.mutate_semantic_boundary(
            "evidence_complete_boundary",
            "evidence_complete is not sealed.",
            "evidence_complete is sealed.",
        )

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertIn("evidence_complete_sealed_claim_detected", result["completion_readiness_findings"])

    def test_replay_ready_as_sealed_fails(self):
        artifact = self.mutate_semantic_boundary(
            "replay_ready_boundary",
            "replay_ready is not sealed.",
            "replay_ready is sealed.",
        )

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertIn("replay_ready_sealed_claim_detected", result["completion_readiness_findings"])

    def test_release_tag_marked_created_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["release_tag_created"] = True

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertFalse(result["release_status_future_only"])
        self.assertIn("release_tag_created_claim_detected", result["completion_readiness_findings"])

    def test_release_notes_marked_published_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["release_notes_published"] = True

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertFalse(result["release_status_future_only"])
        self.assertIn("release_notes_published_claim_detected", result["completion_readiness_findings"])

    def test_issue_176_closed_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["issue_176_closed"] = True

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertIn("issue_176_closed_claim_detected", result["completion_readiness_findings"])

    def test_exact_negative_authority_values_remain_non_authoritative(self):
        self.assertEqual(
            EXPLICIT_NEGATIVE_AUTHORITY_STRINGS,
            {
                "",
                "false",
                "denied",
                "rejected",
                "prohibited",
                "forbidden",
                "not_granted",
                "not_transferred",
                "not_approved",
                "not_sealed",
                "evidence_only",
                "review_required",
            },
        )
        for value in (
            False,
            "false",
            "denied",
            "rejected",
            "prohibited",
            "forbidden",
            "not_granted",
            "not_transferred",
            "not_approved",
            "not_sealed",
            "evidence_only",
            "review_required",
        ):
            with self.subTest(value=value):
                artifact = copy.deepcopy(self.artifact)
                artifact["approval"] = value
                result = self.evaluate(artifact)
                self.assertTrue(
                    result["completion_readiness_valid"],
                    result["completion_readiness_findings"],
                )

    def test_arbitrary_not_prefix_under_authority_key_is_affirmative(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["decision_proof_sealed"] = "not_only_claimed_but_sealed"

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn(
            "authority_transfer_claim_detected",
            result["completion_readiness_findings"],
        )

    def test_all_structured_authority_fields_are_inspected_recursively(self):
        self.assertEqual(
            STRUCTURED_AUTHORITY_FIELDS,
            {
                "status",
                "state",
                "result",
                "outcome",
                "decision",
                "authorization",
                "approval",
                "authority",
                "sealing",
                "risk",
                "rollback",
                "fail_closed",
                "audit",
                "waiver",
            },
        )
        for field in STRUCTURED_AUTHORITY_FIELDS:
            with self.subTest(field=field):
                artifact = copy.deepcopy(self.artifact)
                artifact["approval"] = {
                    "status": "not_approved",
                    field: "unknown_non_empty_value",
                }
                result = self.evaluate(artifact)
                self.assertTrue(result["completion_readiness_invalid"])
                self.assertIn(
                    "authority_transfer_claim_detected",
                    result["completion_readiness_findings"],
                )

    def test_negative_outer_authority_state_cannot_hide_nested_affirmative(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["decision_proof_sealed"] = {
            "status": "not_sealed",
            "nested": {
                "authority": {
                    "state": "not_transferred",
                    "waiver": "granted",
                }
            },
        }

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn(
            "authority_transfer_claim_detected",
            result["completion_readiness_findings"],
        )

    def test_evaluator_output_attempting_to_seal_decision_proof_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["evaluator_output"] = "decision_proof_sealed"

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn("authority_transfer_claim_detected", result["completion_readiness_findings"])

    def test_evaluator_output_attempting_final_governance_judgment_fails(self):
        artifact = copy.deepcopy(self.artifact)
        artifact["evaluator_output"] = "final_governance_judgment"

        result = self.evaluate(artifact)

        self.assertTrue(result["completion_readiness_invalid"])
        self.assertTrue(result["escalation_required"])
        self.assertIn("authority_transfer_claim_detected", result["completion_readiness_findings"])


if __name__ == "__main__":
    unittest.main()
