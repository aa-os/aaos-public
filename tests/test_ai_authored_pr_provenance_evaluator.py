import copy
import json
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.ai_authored_pr_provenance_evaluator import (  # noqa: E402
    FORBIDDEN_EVALUATOR_OUTPUTS,
    REQUIRED_WORKFLOW_OUTPUTS,
    evaluate_ai_authored_pr_provenance_fixture,
    evaluate_workflow_text,
    is_trusted_workflow_comment,
)


FIXTURE_PATH = (
    ROOT
    / "examples"
    / "public-integration-pack-pilot"
    / "m14-ai-authored-pr-provenance-fixtures.json"
)
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "m14-ai-pr-provenance.yml"


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class AIAuthoredPRProvenanceEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.fixture_set = load_json(FIXTURE_PATH)
        self.workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")

    def evaluate(self, fixture_set=None, workflow_text=None):
        return evaluate_ai_authored_pr_provenance_fixture(
            self.fixture_set if fixture_set is None else fixture_set,
            self.workflow_text if workflow_text is None else workflow_text,
        )

    def case_result(self, result, case_type):
        return next(
            case
            for case in result["case_results"]
            if case["case_type"] == case_type
        )

    def fixture_case(self, fixture_set, case_type):
        return next(
            case
            for case in fixture_set["fixture_cases"]
            if case["case_type"] == case_type
        )

    def assert_forbidden_output_rejected(self, output):
        self.assertIn(output, FORBIDDEN_EVALUATOR_OUTPUTS)
        fixture_set = copy.deepcopy(self.fixture_set)
        fixture_set["simulated_evaluator_output"] = output

        result = self.evaluate(fixture_set)

        self.assertTrue(result["ai_pr_provenance_invalid"])
        self.assertFalse(result["ai_pr_provenance_valid"])
        self.assertIn(
            f"forbidden_output_claim_detected:{output}",
            result["ai_pr_provenance_findings"],
        )

    def test_valid_m14_fixture_state(self):
        result = self.evaluate()

        self.assertTrue(result["ai_pr_provenance_valid"])
        self.assertFalse(result["ai_pr_provenance_invalid"])
        self.assertEqual(result["ai_pr_provenance_findings"], [])
        self.assertTrue(result["workflow_security_valid"])

    def test_exact_m14_and_issue_linkage_state(self):
        self.assertEqual(self.fixture_set["fixture_status"], "m14_active_work_not_complete")
        self.assertEqual(self.fixture_set["related_issue"], "#180")
        self.assertEqual(self.fixture_set["tracker_issue"], "#201")
        self.assertEqual(self.fixture_set["tracker_issue_linkage"], "Refs #201")
        self.assertEqual(self.fixture_set["related_voice_runtime_pr"], "#202")
        self.assertEqual(self.fixture_set["related_public_output_gate_pr"], "#204")
        self.assertEqual(self.fixture_set["related_moda_mapping_pr"], "#205")
        self.assertFalse(self.fixture_set["future_release_tag_path"]["released"])

    def test_workflow_uses_pull_request_target(self):
        self.assertRegex(self.workflow_text, r"(?m)^  pull_request_target:\s*$")
        self.assertNotRegex(self.workflow_text, r"(?m)^  pull_request:\s*$")
        self.assertNotIn("pull_request_target_event_missing", evaluate_workflow_text(self.workflow_text))

    def test_workflow_has_exact_required_event_types(self):
        event_block = re.search(
            r"(?ms)^  pull_request_target:\s*\n(?P<body>.*?)(?=^permissions:)",
            self.workflow_text,
        ).group("body")
        event_types = set(re.findall(r"(?m)^\s{6}-\s+([a-z_]+)\s*$", event_block))
        self.assertEqual(
            event_types,
            {
                "opened",
                "edited",
                "synchronize",
                "reopened",
                "labeled",
                "unlabeled",
                "ready_for_review",
            },
        )

    def test_workflow_does_not_contain_actions_checkout(self):
        self.assertNotIn("actions/checkout", self.workflow_text.casefold())

    def test_workflow_does_not_contain_any_uses_step(self):
        self.assertNotRegex(self.workflow_text, r"(?m)^\s*uses\s*:")

    def test_workflow_does_not_checkout_or_execute_pr_code(self):
        forbidden_patterns = (
            r"\bgit\s+checkout\b",
            r"\bgit\s+switch\b",
            r"\bgit\s+clone\b",
            r"\bsubprocess\b",
            r"\bos\.system\s*\(",
            r"\beval\s*\(",
            r"\bexec\s*\(",
            r"/(zipball|tarball)\b",
            r"\b(download_url|contents_url)\b",
        )
        for pattern in forbidden_patterns:
            self.assertNotRegex(self.workflow_text, pattern)
        self.assertFalse(self.fixture_set["workflow_executes_pr_code"])
        self.assertFalse(self.fixture_set["pull_request_head_checked_out"])

    def test_workflow_permissions_are_limited_correctly(self):
        self.assertRegex(
            self.workflow_text,
            r"(?ms)^permissions:\s*\n  contents: read\n  issues: write\n  pull-requests: write\n",
        )
        modified = self.workflow_text.replace(
            "  pull-requests: write\n", "  pull-requests: write\n  actions: write\n", 1
        )
        self.assertIn("workflow_permissions_invalid", evaluate_workflow_text(modified))

    def test_workflow_uses_standard_library_inline_python_and_event_path(self):
        self.assertIn("python - <<'PY'", self.workflow_text)
        self.assertIn("GITHUB_EVENT_PATH", self.workflow_text)
        self.assertIn("urllib.request", self.workflow_text)
        self.assertNotRegex(self.workflow_text, r"(?m)^\s*(pip|python\s+-m\s+pip)\s+install\b")

    def test_workflow_does_not_use_third_party_runtime_action(self):
        self.assertFalse(self.fixture_set["third_party_runtime_action_used"])
        self.assertNotIn("Pradumnasaraf/agent-pr-police", self.workflow_text)
        self.assertNotRegex(self.workflow_text, r"(?m)^\s*uses\s*:")

    def test_workflow_token_is_not_logged(self):
        self.assertFalse(self.fixture_set["workflow_security_model"]["token_logged"])
        self.assertNotRegex(
            self.workflow_text,
            r"print\s*\([^\n]*(GITHUB_TOKEN|\btoken\b)",
        )

    def test_mutation_failures_are_warning_only_and_non_blocking(self):
        self.assertIn("::warning::", self.workflow_text)
        self.assertIn("sys.exit(0)", self.workflow_text)
        self.assertFalse(
            self.fixture_set["workflow_security_model"]["mutation_failures_blocking"]
        )
        self.assertFalse(self.fixture_set["merge_gate_created"])

    def test_codex_body_marker_detection(self):
        result = self.evaluate()
        case = self.case_result(
            result, "codex_pr_detected_from_structured_pr_body_marker"
        )

        self.assertTrue(case["case_valid"])
        self.assertTrue(case["detected"])
        self.assertEqual(case["agent"], "codex")
        self.assertIn("structured_marker:agent_authored_true", case["detection_signals"])
        self.assertIn("pr_marker:codex", case["detection_signals"])

    def test_claude_code_commit_marker_detection(self):
        case = self.case_result(
            self.evaluate(),
            "claude_code_detected_from_commit_or_coauthored_by_marker",
        )

        self.assertTrue(case["detected"])
        self.assertEqual(case["agent"], "claude_code")
        self.assertIn("commit_marker:claude_code", case["detection_signals"])
        self.assertIn("coauthor:claude_code", case["detection_signals"])

    def test_cursor_branch_prefix_detection(self):
        case = self.case_result(
            self.evaluate(), "cursor_detected_from_branch_prefix"
        )

        self.assertTrue(case["detected"])
        self.assertEqual(case["agent"], "cursor")
        self.assertIn("branch_prefix:cursor/", case["detection_signals"])

    def test_copilot_author_or_branch_detection(self):
        case = self.case_result(
            self.evaluate(), "copilot_detected_from_author_or_branch_signal"
        )

        self.assertTrue(case["detected"])
        self.assertEqual(case["agent"], "github_copilot")
        self.assertFalse(case["author_requested_as_reviewer"])

    def test_manual_pr_by_ai_label_detection(self):
        case = self.case_result(self.evaluate(), "manually_labeled_pr_by_ai")

        self.assertTrue(case["detected"])
        self.assertEqual(case["agent"], "unknown")
        self.assertIn("label:pr-by-ai", case["detection_signals"])
        self.assertTrue(case["unrelated_labels_preserved"])

    def test_all_required_agents_and_prefixes_are_present(self):
        self.assertEqual(
            set(self.fixture_set["recognized_agents"]),
            {
                "codex",
                "claude_code",
                "github_copilot",
                "cursor",
                "devin",
                "google_jules",
                "aider",
                "openhands",
                "sweep",
            },
        )
        self.assertEqual(
            set(self.fixture_set["recognized_branch_prefixes"]),
            {
                "codex/",
                "claude/",
                "copilot/",
                "cursor/",
                "devin/",
                "jules/",
                "aider/",
                "openhands/",
                "sweep/",
            },
        )

    def test_non_agent_pr_remains_unmodified(self):
        case = self.case_result(
            self.evaluate(), "ordinary_human_pr_with_no_ai_signal"
        )

        self.assertFalse(case["detected"])
        self.assertFalse(case["add_pr_by_ai"])
        self.assertFalse(case["add_human_review_required"])
        self.assertEqual(case["comment_action"], "none")
        self.assertEqual(case["reviewer_request_status"], "not_required")
        self.assertFalse(case["pr_modified"])

    def test_detected_ai_pr_gets_pr_by_ai(self):
        case = self.case_result(
            self.evaluate(), "codex_pr_detected_from_structured_pr_body_marker"
        )

        self.assertTrue(case["detected"])
        self.assertTrue(case["add_pr_by_ai"])
        self.assertTrue(case["unrelated_labels_preserved"])

    def test_sensitive_ai_pr_gets_human_review_required(self):
        case = self.case_result(
            self.evaluate(), "ai_authored_pr_changing_governance_sensitive_files"
        )

        self.assertTrue(case["sensitive_change"])
        self.assertTrue(case["add_human_review_required"])
        self.assertTrue(case["review_routing_required"])
        self.assertEqual(case["reviewer_request_status"], "reviewer_request_succeeded")

    def test_non_sensitive_ai_pr_does_not_get_sensitive_routing(self):
        case = self.case_result(
            self.evaluate(),
            "ai_authored_pr_changing_only_non_sensitive_documentation",
        )

        self.assertTrue(case["detected"])
        self.assertFalse(case["sensitive_change"])
        self.assertFalse(case["add_human_review_required"])
        self.assertFalse(case["review_routing_required"])
        self.assertEqual(case["reviewer_request_status"], "not_required")

    def test_sticky_marker_appears_exactly_once_in_workflow(self):
        marker = "<!-- aaos:m14-ai-pr-provenance -->"
        self.assertEqual(self.workflow_text.count(marker), 1)
        self.assertEqual(self.fixture_set["sticky_comment_marker"], marker)

    def test_workflow_checks_github_actions_comment_ownership(self):
        self.assertIn("def is_trusted_workflow_comment(comment):", self.workflow_text)
        self.assertIn("performed_via_github_app", self.workflow_text)
        self.assertIn('app.get("slug") == "github-actions"', self.workflow_text)
        self.assertIn(
            'user.get("login") == "github-actions[bot]"', self.workflow_text
        )
        self.assertIn('user.get("type") == "Bot"', self.workflow_text)
        self.assertTrue(
            is_trusted_workflow_comment(
                {"performed_via_github_app": {"slug": "github-actions"}}
            )
        )
        self.assertTrue(
            is_trusted_workflow_comment(
                {"user": {"login": "github-actions[bot]", "type": "Bot"}}
            )
        )

    def test_untrusted_pr_author_marker_comment_is_ignored(self):
        case = self.case_result(
            self.evaluate(),
            "untrusted_marker_comment_does_not_suppress_workflow_comment",
        )

        self.assertTrue(case["case_valid"])
        self.assertEqual(case["trusted_marker_comment_count"], 0)
        self.assertEqual(case["untrusted_marker_comment_count"], 1)
        self.assertTrue(case["untrusted_marker_comments_ignored"])
        self.assertIn(
            "untrusted_provenance_marker_comment_ignored", self.workflow_text
        )

    def test_untrusted_marker_does_not_suppress_authentic_comment_creation(self):
        case = self.case_result(
            self.evaluate(),
            "untrusted_marker_comment_does_not_suppress_workflow_comment",
        )

        self.assertEqual(case["comment_action"], "create")
        self.assertIsNone(case["selected_comment_id"])
        self.assertEqual(case["resulting_sticky_comment_count"], 1)

    def test_untrusted_marker_comment_is_never_selected_for_patch(self):
        case = self.case_result(
            self.evaluate(),
            "untrusted_marker_comment_does_not_suppress_workflow_comment",
        )

        self.assertEqual(case["patched_comment_ids"], [])
        self.assertFalse(case["untrusted_comments_patched"])
        self.assertNotIn("existing[0]", self.workflow_text)
        self.assertRegex(
            self.workflow_text,
            r"(?s)canonical_comment\s*=\s*trusted_with_id\[0\].*?comment_id\s*=\s*canonical_comment\[\"id\"\].*?\"PATCH\"",
        )

    def test_trusted_workflow_owned_marker_comment_is_updated(self):
        case = self.case_result(
            self.evaluate(), "trusted_workflow_marker_comment_is_updated"
        )

        self.assertTrue(case["case_valid"])
        self.assertEqual(case["trusted_marker_comment_count"], 1)
        self.assertEqual(case["untrusted_marker_comment_count"], 0)
        self.assertEqual(case["comment_action"], "update")
        self.assertEqual(case["selected_comment_id"], 9022)
        self.assertEqual(case["patched_comment_ids"], [9022])

    def test_marker_text_alone_is_insufficient_to_establish_ownership(self):
        marker = self.fixture_set["sticky_comment_marker"]
        untrusted_comment = {
            "id": 9100,
            "body": marker,
            "user": {"login": "pull-request-author", "type": "User"},
        }

        self.assertFalse(is_trusted_workflow_comment(untrusted_comment))
        self.assertFalse(
            self.fixture_set["sticky_comment_ownership"][
                "marker_text_alone_establishes_ownership"
            ]
        )

    def test_missing_comment_ownership_data_remains_non_blocking(self):
        fixture_set = copy.deepcopy(self.fixture_set)
        fixture_case = self.fixture_case(
            fixture_set,
            "untrusted_marker_comment_does_not_suppress_workflow_comment",
        )
        fixture_case["existing_marker_comments"] = [
            {
                "id": 9101,
                "body": fixture_set["sticky_comment_marker"],
            }
        ]

        result = self.evaluate(fixture_set)
        case = self.case_result(
            result,
            "untrusted_marker_comment_does_not_suppress_workflow_comment",
        )

        self.assertTrue(result["ai_pr_provenance_valid"])
        self.assertTrue(case["ownership_data_missing"])
        self.assertEqual(case["comment_action"], "create")
        self.assertEqual(case["patched_comment_ids"], [])
        self.assertTrue(case["non_blocking"])

    def test_concurrency_serializes_sticky_comment_updates(self):
        self.assertIn(
            "group: m14-ai-pr-provenance-${{ github.event.pull_request.number }}",
            self.workflow_text,
        )
        self.assertIn("cancel-in-progress: false", self.workflow_text)

    def test_rerun_updates_sticky_comment_without_duplicate(self):
        case = self.case_result(
            self.evaluate(),
            "repeated_workflow_run_updates_sticky_comment_without_duplication",
        )

        self.assertEqual(case["comment_action"], "update")
        self.assertEqual(case["resulting_sticky_comment_count"], 1)
        self.assertIn('"PATCH"', self.workflow_text)
        self.assertIn("issues/comments/", self.workflow_text)

    def test_absent_reviewer_configuration_is_non_blocking(self):
        case = self.case_result(
            self.evaluate(), "missing_reviewer_configuration_remains_non_blocking"
        )

        self.assertTrue(case["review_routing_required"])
        self.assertEqual(
            case["reviewer_request_status"], "reviewer_routing_not_configured"
        )
        self.assertTrue(case["non_blocking"])

    def test_reviewer_api_failure_is_non_blocking(self):
        case = self.case_result(
            self.evaluate(), "reviewer_api_failure_remains_non_blocking"
        )

        self.assertTrue(case["review_routing_required"])
        self.assertEqual(case["reviewer_request_status"], "reviewer_request_warning")
        self.assertTrue(case["non_blocking"])

    def test_required_outputs_are_exposed(self):
        self.assertEqual(set(self.fixture_set["workflow_outputs"]), REQUIRED_WORKFLOW_OUTPUTS)
        for output_name in REQUIRED_WORKFLOW_OUTPUTS:
            self.assertRegex(
                self.workflow_text,
                rf"(?m)^\s{{6}}{re.escape(output_name)}:\s*\$\{{\{{",
            )

    def test_required_governance_boundaries_are_in_sticky_comment_template(self):
        for statement in self.fixture_set["required_boundary_statements"]:
            self.assertIn(statement, self.workflow_text)

    def test_provenance_label_as_approval_fails(self):
        self.assert_forbidden_output_rejected("provenance_approved")

    def test_human_review_required_as_completed_review_fails(self):
        self.assert_forbidden_output_rejected("review_approved")

    def test_reviewer_routing_as_approval_fails(self):
        self.assert_forbidden_output_rejected("reviewer_routing_is_approval")

    def test_workflow_success_as_merge_approval_fails(self):
        self.assert_forbidden_output_rejected("merge_approved")

    def test_detection_as_identity_proof_fails(self):
        self.assert_forbidden_output_rejected("identity_proven")

    def test_evaluator_attempting_decision_proof_sealing_fails(self):
        self.assert_forbidden_output_rejected("decision_proof_sealed")

    def test_evaluator_attempting_authority_transfer_fails(self):
        self.assert_forbidden_output_rejected("authority_transferred")

    def test_evaluator_attempting_m14_completion_fails(self):
        self.assert_forbidden_output_rejected("m14_complete")

    def test_evaluator_attempting_v0_13_0_release_fails(self):
        self.assert_forbidden_output_rejected("v0_13_0_released")

    def test_evaluator_attempting_to_close_201_fails(self):
        self.assert_forbidden_output_rejected("closes_201")

    def test_negative_fixture_attempts_are_rejected_not_accepted(self):
        result = self.evaluate()
        negative_results = [
            case for case in result["case_results"] if "attempted_output" in case
        ]

        self.assertEqual(len(negative_results), 9)
        self.assertTrue(all(case["case_valid"] for case in negative_results))
        self.assertTrue(all(case["attempt_rejected"] for case in negative_results))


if __name__ == "__main__":
    unittest.main()
