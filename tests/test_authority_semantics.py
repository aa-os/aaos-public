import ast
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import runtime.authority_semantics as authority_semantics  # noqa: E402
from runtime.authority_semantics import (  # noqa: E402
    EXPLICIT_NEGATIVE_AUTHORITY_STRINGS,
    authority_value_is_affirmative,
    is_explicit_negative_authority_value,
    scan_forbidden_authority_claims,
)


FORBIDDEN_KEYS = frozenset({"approval"})


class AuthoritySemanticsTests(unittest.TestCase):
    def test_every_exact_negative_scalar_is_non_authoritative(self):
        for value in sorted(EXPLICIT_NEGATIVE_AUTHORITY_STRINGS):
            with self.subTest(value=value):
                self.assertTrue(is_explicit_negative_authority_value(value))
                self.assertFalse(
                    authority_value_is_affirmative(value, FORBIDDEN_KEYS)
                )

        for value in (None, False):
            with self.subTest(value=value):
                self.assertTrue(is_explicit_negative_authority_value(value))
                self.assertFalse(
                    authority_value_is_affirmative(value, FORBIDDEN_KEYS)
                )

    def test_arbitrary_not_prefix_values_remain_affirmative(self):
        for value in (
            "not_authorized_by_policy",
            "not_final_but_granted",
            "not_only_claimed_but_sealed",
        ):
            with self.subTest(value=value):
                self.assertFalse(is_explicit_negative_authority_value(value))
                self.assertTrue(
                    authority_value_is_affirmative(value, FORBIDDEN_KEYS)
                )

    def test_unknown_nonempty_scalar_under_forbidden_key_fails(self):
        self.assertEqual(
            scan_forbidden_authority_claims(
                {"approval": "unknown_non_empty_value"},
                forbidden_keys=FORBIDDEN_KEYS,
            ),
            ["affirmative_forbidden_claim:approval"],
        )

    def test_empty_mappings_and_lists_are_non_authoritative(self):
        for value in ({}, []):
            with self.subTest(value=value):
                self.assertFalse(
                    authority_value_is_affirmative(value, FORBIDDEN_KEYS)
                )
                self.assertEqual(
                    scan_forbidden_authority_claims(
                        {"approval": value},
                        forbidden_keys=FORBIDDEN_KEYS,
                    ),
                    [],
                )

    def test_numeric_zero_is_negative_and_nonzero_is_affirmative(self):
        for value in (0, 0.0):
            with self.subTest(value=value):
                self.assertTrue(is_explicit_negative_authority_value(value))
                self.assertFalse(
                    authority_value_is_affirmative(value, FORBIDDEN_KEYS)
                )

        for value in (1, -1, 0.5):
            with self.subTest(value=value):
                self.assertFalse(is_explicit_negative_authority_value(value))
                self.assertTrue(
                    authority_value_is_affirmative(value, FORBIDDEN_KEYS)
                )

    def test_structured_negative_state_allows_neutral_metadata(self):
        value = {
            "status": "not_approved",
            "metadata": {
                "source": "human-review-record",
                "evidence_id": "evidence-001",
            },
        }

        self.assertFalse(authority_value_is_affirmative(value, FORBIDDEN_KEYS))
        self.assertEqual(
            scan_forbidden_authority_claims(
                {"approval": value},
                forbidden_keys=FORBIDDEN_KEYS,
            ),
            [],
        )

    def test_negative_outer_status_cannot_hide_nested_affirmative_authority(self):
        value = {
            "approval": {
                "status": "not_approved",
                "details": {"authority": "granted"},
            }
        }

        self.assertEqual(
            scan_forbidden_authority_claims(
                value,
                forbidden_keys=FORBIDDEN_KEYS,
            ),
            [
                "affirmative_forbidden_claim:approval",
                "affirmative_forbidden_claim:approval.details.authority",
            ],
        )

    def test_nested_list_and_mapping_claims_are_inspected(self):
        value = {
            "records": [
                {
                    "wrapper": {
                        "approval": [
                            "not_approved",
                            {"authority": "granted"},
                        ]
                    }
                }
            ]
        }

        self.assertEqual(
            scan_forbidden_authority_claims(
                value,
                forbidden_keys=FORBIDDEN_KEYS,
            ),
            [
                "affirmative_forbidden_claim:records.0.wrapper.approval",
                (
                    "affirmative_forbidden_claim:"
                    "records.0.wrapper.approval.1.authority"
                ),
            ],
        )

    def test_forbidden_output_token_is_detected(self):
        self.assertEqual(
            scan_forbidden_authority_claims(
                {"result": "release_approved"},
                forbidden_keys=FORBIDDEN_KEYS,
                forbidden_tokens=("release_approved",),
            ),
            ["forbidden_output_token_used_as_value:result"],
        )

    def test_skip_key_excludes_the_complete_subtree(self):
        value = {
            "must_not": {"approval": "granted"},
            "active_claim": {"approval": "granted"},
        }

        self.assertEqual(
            scan_forbidden_authority_claims(
                value,
                forbidden_keys=FORBIDDEN_KEYS,
                skip_keys=("must_not",),
            ),
            ["affirmative_forbidden_claim:active_claim.approval"],
        )

    def test_finding_paths_are_deterministic_and_deduplicated(self):
        arguments = {
            "forbidden_keys": FORBIDDEN_KEYS,
            "forbidden_tokens": (
                "release_approved",
                "release-approved",
                "release_approved",
            ),
            "path": ("root",),
        }

        first = scan_forbidden_authority_claims("release_approved", **arguments)
        second = scan_forbidden_authority_claims("release_approved", **arguments)

        self.assertEqual(first, ["forbidden_output_token_used_as_value:root"])
        self.assertEqual(second, first)

    def test_module_has_no_network_subprocess_dynamic_import_or_execution_path(self):
        module_path = Path(authority_semantics.__file__).resolve()
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        imported_roots = set()
        forbidden_calls = {
            "__import__",
            "compile",
            "eval",
            "exec",
            "open",
            "popen",
            "run",
            "system",
            "urlopen",
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", 1)[0])
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    self.assertNotIn(node.func.id, forbidden_calls)
                elif isinstance(node.func, ast.Attribute):
                    self.assertNotIn(node.func.attr, forbidden_calls)

        self.assertLessEqual(
            imported_roots,
            {"__future__", "collections", "re", "typing"},
        )
        self.assertTrue(
            imported_roots.isdisjoint(
                {"http", "importlib", "os", "requests", "socket", "subprocess", "urllib"}
            )
        )


if __name__ == "__main__":
    unittest.main()
