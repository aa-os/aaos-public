import ast
import hashlib
import inspect
import os
import runpy
import socket
import subprocess
import tempfile
import unittest
import urllib.request
from copy import deepcopy
from pathlib import Path
from unittest import mock

import runtime.repository_artifact_digest as digest_module
from runtime.repository_artifact_digest import (
    RepositoryArtifactFileTypeError,
    RepositoryArtifactPathError,
    RepositoryArtifactTextError,
    canonicalize_utf8_repository_text,
    sha256_repository_file,
)


HISTORICAL_PATH = "artifacts/phase-evaluator.py"
HISTORICAL_RECORDED_SHA256 = (
    "1836ba9826fdaed7e7aba81f8b3edc73f167c8d7b1f40ce011671d5bc23c0179"
)
MAINTAINED_CANONICAL_SHA256 = (
    "4038d6296bb0b2d4f46a2467edea3960d474a5027379f018dbd4cf8fb4cc37d2"
)
MAINTAINED_TEXT_LF = b"maintained\n"

EXPECTED_HISTORICAL_ENTRY = {
    "relative_path": HISTORICAL_PATH,
    "sha256": HISTORICAL_RECORDED_SHA256,
}


def consume_maintained_artifact(repository_root, historical_entry):
    """Minimal phase-aware consumer used to test digest integration boundaries."""

    findings = []
    historical_path_valid = historical_entry.get("relative_path") == HISTORICAL_PATH
    if not historical_path_valid:
        findings.append("historical_manifest_path_substitution")

    historical_digest_valid = (
        historical_entry.get("sha256") == HISTORICAL_RECORDED_SHA256
    )
    if not historical_digest_valid:
        findings.append("historical_manifest_digest_mismatch")

    maintained_digest_valid = False
    try:
        observed = sha256_repository_file(
            repository_root,
            HISTORICAL_PATH,
            mode="text",
        )
    except UnicodeDecodeError:
        findings.append("maintained_artifact_malformed_utf8")
    except RepositoryArtifactTextError:
        findings.append("maintained_artifact_lone_cr")
    except RepositoryArtifactPathError:
        findings.append("maintained_artifact_path_unsafe")
    except FileNotFoundError:
        findings.append("maintained_artifact_missing")
    except RepositoryArtifactFileTypeError:
        findings.append("maintained_artifact_not_regular")
    except OSError:
        findings.append("maintained_artifact_unreadable")
    else:
        maintained_digest_valid = observed == MAINTAINED_CANONICAL_SHA256
        if not maintained_digest_valid:
            findings.append("maintained_artifact_digest_mismatch")

    integrity_valid = (
        historical_path_valid
        and historical_digest_valid
        and maintained_digest_valid
    )
    return {
        "integrity_valid": integrity_valid,
        "historical_digest_valid": historical_digest_valid,
        "maintained_digest_valid": maintained_digest_valid,
        "findings": findings,
        # Digest validation is evidence only and grants no governance state.
        "release_approved": False,
        "risk_accepted": False,
        "public_disclosure_approved": False,
        "audit_closed": False,
        "authority_transferred": False,
        "final_governance_judgment": False,
        "decision_proof_sealed": False,
    }


class TemporaryRepositoryTestCase(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.repository_root = Path(self.temporary_directory.name).resolve()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def write_bytes(self, relative_path, data):
        path = self.repository_root.joinpath(*relative_path.split("/"))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path


class RepositoryTextCanonicalizationTests(TemporaryRepositoryTestCase):
    def test_01_lf_text_produces_expected_digest(self):
        self.write_bytes("artifact.txt", b"hello\n")
        self.assertEqual(
            sha256_repository_file(
                self.repository_root,
                "artifact.txt",
                mode="text",
            ),
            "5891b5b522d5df086d0ff0b110fbd9d21bb4fc7163af34d08286a2e846f6be03",
        )

    def test_02_equivalent_crlf_text_produces_same_canonical_digest(self):
        self.write_bytes("lf.txt", b"alpha\nbeta\n")
        self.write_bytes("crlf.txt", b"alpha\r\nbeta\r\n")
        self.assertEqual(
            sha256_repository_file(self.repository_root, "lf.txt", mode="text"),
            sha256_repository_file(
                self.repository_root,
                "crlf.txt",
                mode="text",
            ),
        )

    def test_03_repeated_canonicalization_is_idempotent(self):
        first = canonicalize_utf8_repository_text(b"alpha\r\nbeta\n")
        self.assertEqual(canonicalize_utf8_repository_text(first), first)

    def test_04_lf_only_input_remains_byte_equivalent(self):
        raw = b"alpha\nbeta\n"
        self.assertEqual(canonicalize_utf8_repository_text(raw), raw)

    def test_05_terminal_newline_is_preserved(self):
        self.assertEqual(
            canonicalize_utf8_repository_text(b"alpha\r\n"),
            b"alpha\n",
        )

    def test_06_absence_of_terminal_newline_is_preserved(self):
        self.assertEqual(
            canonicalize_utf8_repository_text(b"alpha"),
            b"alpha",
        )

    def test_07_spaces_and_tabs_are_preserved(self):
        raw = b" \talpha  \r\n\tbeta \t"
        self.assertEqual(
            canonicalize_utf8_repository_text(raw),
            b" \talpha  \n\tbeta \t",
        )

    def test_08_unicode_content_is_preserved_without_normalization(self):
        composed = "caf\u00e9\n".encode("utf-8")
        decomposed = "cafe\u0301\n".encode("utf-8")
        self.assertEqual(canonicalize_utf8_repository_text(composed), composed)
        self.assertEqual(canonicalize_utf8_repository_text(decomposed), decomposed)
        self.assertNotEqual(composed, decomposed)

    def test_09_utf8_bom_is_not_silently_removed(self):
        raw = b"\xef\xbb\xbfhello\r\n"
        canonical = canonicalize_utf8_repository_text(raw)
        self.assertEqual(canonical, b"\xef\xbb\xbfhello\n")
        self.assertNotEqual(
            hashlib.sha256(canonical).hexdigest(),
            hashlib.sha256(b"hello\n").hexdigest(),
        )


class RepositoryFileDigestTests(TemporaryRepositoryTestCase):
    def test_10_binary_mode_hashes_exact_bytes(self):
        raw = b"\x00\xff\r\n\x80"
        self.write_bytes("artifact.bin", raw)
        self.assertEqual(
            sha256_repository_file(
                self.repository_root,
                "artifact.bin",
                mode="binary",
            ),
            hashlib.sha256(raw).hexdigest(),
        )

    def test_11_binary_crlf_and_lf_sequences_produce_different_hashes(self):
        self.write_bytes("lf.bin", b"alpha\nbeta\n")
        self.write_bytes("crlf.bin", b"alpha\r\nbeta\r\n")
        self.assertNotEqual(
            sha256_repository_file(self.repository_root, "lf.bin", mode="binary"),
            sha256_repository_file(
                self.repository_root,
                "crlf.bin",
                mode="binary",
            ),
        )

    def test_12_lone_cr_fails_deterministically_in_text_mode(self):
        self.write_bytes("artifact.txt", b"alpha\rbeta\n")
        with self.assertRaisesRegex(
            RepositoryArtifactTextError,
            "lone carriage return",
        ):
            sha256_repository_file(
                self.repository_root,
                "artifact.txt",
                mode="text",
            )

    def test_13_malformed_utf8_fails_deterministically_in_text_mode(self):
        self.write_bytes("artifact.txt", b"alpha\xffbeta\n")
        with self.assertRaises(UnicodeDecodeError):
            sha256_repository_file(
                self.repository_root,
                "artifact.txt",
                mode="text",
            )

    def test_14_missing_file_fails(self):
        with self.assertRaises(FileNotFoundError):
            sha256_repository_file(
                self.repository_root,
                "missing.txt",
                mode="text",
            )

    def test_15_absolute_path_fails(self):
        path = self.write_bytes("artifact.txt", b"alpha\n")
        with self.assertRaises(RepositoryArtifactPathError):
            sha256_repository_file(
                self.repository_root,
                path.as_posix(),
                mode="text",
            )

    def test_16_parent_traversal_fails(self):
        with self.assertRaises(RepositoryArtifactPathError):
            sha256_repository_file(
                self.repository_root,
                "../artifact.txt",
                mode="text",
            )

    def test_17_backslash_substitution_fails(self):
        self.write_bytes("nested/artifact.txt", b"alpha\n")
        with self.assertRaises(RepositoryArtifactPathError):
            sha256_repository_file(
                self.repository_root,
                "nested\\artifact.txt",
                mode="text",
            )

    def test_18_path_substitution_fails_in_consuming_evaluator(self):
        self.write_bytes(HISTORICAL_PATH, MAINTAINED_TEXT_LF)
        self.write_bytes("artifacts/substitute.py", MAINTAINED_TEXT_LF)
        entry = deepcopy(EXPECTED_HISTORICAL_ENTRY)
        entry["relative_path"] = "artifacts/substitute.py"
        result = consume_maintained_artifact(self.repository_root, entry)
        self.assertFalse(result["integrity_valid"])
        self.assertIn("historical_manifest_path_substitution", result["findings"])
        self.assertTrue(result["maintained_digest_valid"])

    def test_19_non_regular_file_fails(self):
        (self.repository_root / "directory").mkdir()
        with self.assertRaises(RepositoryArtifactFileTypeError):
            sha256_repository_file(
                self.repository_root,
                "directory",
                mode="binary",
            )

    def test_link_like_path_substitution_fails_without_privileged_symlink(self):
        path = self.write_bytes("artifact.txt", b"alpha\n")
        real_check = digest_module._path_is_link_like

        def simulated_link(candidate):
            return candidate == path or real_check(candidate)

        with mock.patch.object(
            digest_module,
            "_path_is_link_like",
            side_effect=simulated_link,
        ):
            with self.assertRaises(RepositoryArtifactPathError):
                sha256_repository_file(
                    self.repository_root,
                    "artifact.txt",
                    mode="text",
                )

    def test_explicit_mode_is_required_and_invalid_modes_fail(self):
        self.write_bytes("artifact.txt", b"alpha\n")
        with self.assertRaises(TypeError):
            sha256_repository_file(self.repository_root, "artifact.txt")
        with self.assertRaises(ValueError):
            sha256_repository_file(
                self.repository_root,
                "artifact.txt",
                mode="auto",
            )

    def test_empty_and_normalized_substitute_paths_fail(self):
        for relative_path in ("", " ", "./artifact.txt", "nested//artifact.txt"):
            with self.subTest(relative_path=relative_path):
                with self.assertRaises(RepositoryArtifactPathError):
                    sha256_repository_file(
                        self.repository_root,
                        relative_path,
                        mode="text",
                    )

    def test_windows_drive_and_stream_substitution_fails_on_every_platform(self):
        for relative_path in ("C:/artifact.txt", "artifact.txt:stream"):
            with self.subTest(relative_path=relative_path):
                with self.assertRaises(RepositoryArtifactPathError):
                    sha256_repository_file(
                        self.repository_root,
                        relative_path,
                        mode="binary",
                    )

    def test_case_alias_is_never_accepted_as_the_exact_path(self):
        self.write_bytes("artifact.txt", b"alpha\n")
        alias = "ARTIFACT.TXT"
        expected_error = (
            RepositoryArtifactPathError
            if (self.repository_root / alias).exists()
            else FileNotFoundError
        )
        with self.assertRaises(expected_error):
            sha256_repository_file(
                self.repository_root,
                alias,
                mode="text",
            )

    def test_trailing_dot_and_space_aliases_fail_on_every_platform(self):
        self.write_bytes("artifact.txt", b"alpha\n")
        for alias in ("artifact.txt.", "artifact.txt "):
            with self.subTest(alias=alias):
                with self.assertRaises(RepositoryArtifactPathError):
                    sha256_repository_file(
                        self.repository_root,
                        alias,
                        mode="text",
                    )

    def test_relative_repository_root_is_rejected(self):
        with self.assertRaises(RepositoryArtifactPathError):
            sha256_repository_file(
                Path("relative-repository-root"),
                "artifact.txt",
                mode="text",
            )


class RepositoryDigestConsumerBoundaryTests(TemporaryRepositoryTestCase):
    def setUp(self):
        super().setUp()
        self.write_bytes(HISTORICAL_PATH, MAINTAINED_TEXT_LF)

    def test_20_digest_mismatch_is_reported_by_consuming_evaluator(self):
        self.write_bytes(HISTORICAL_PATH, b"maintained but drifted\n")
        result = consume_maintained_artifact(
            self.repository_root,
            deepcopy(EXPECTED_HISTORICAL_ENTRY),
        )
        self.assertFalse(result["integrity_valid"])
        self.assertIn("maintained_artifact_digest_mismatch", result["findings"])
        self.assertTrue(result["historical_digest_valid"])

    def test_21_historical_digest_remains_unchanged(self):
        self.assertEqual(
            EXPECTED_HISTORICAL_ENTRY["sha256"],
            "1836ba9826fdaed7e7aba81f8b3edc73f167c8d7b1f40ce011671d5bc23c0179",
        )
        mutated = deepcopy(EXPECTED_HISTORICAL_ENTRY)
        mutated["sha256"] = "0" * 64
        result = consume_maintained_artifact(self.repository_root, mutated)
        self.assertFalse(result["historical_digest_valid"])
        self.assertTrue(result["maintained_digest_valid"])
        self.assertIn("historical_manifest_digest_mismatch", result["findings"])

    def test_22_maintained_digest_is_independently_recomputed(self):
        self.write_bytes(HISTORICAL_PATH, b"maintained\r\n")
        result = consume_maintained_artifact(
            self.repository_root,
            deepcopy(EXPECTED_HISTORICAL_ENTRY),
        )
        self.assertNotEqual(
            HISTORICAL_RECORDED_SHA256,
            MAINTAINED_CANONICAL_SHA256,
        )
        self.assertTrue(result["historical_digest_valid"])
        self.assertTrue(result["maintained_digest_valid"])
        self.assertTrue(result["integrity_valid"])

    def test_23_utility_performs_no_network_access(self):
        source_tree = ast.parse(inspect.getsource(digest_module))
        imported_roots = {
            alias.name.split(".", 1)[0]
            for node in ast.walk(source_tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            (node.module or "").split(".", 1)[0]
            for node in ast.walk(source_tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertTrue(
            imported_roots.isdisjoint(
                {"http", "socket", "urllib", "requests"}
            )
        )
        with mock.patch.object(
            socket,
            "create_connection",
            side_effect=AssertionError("network access attempted"),
        ), mock.patch.object(
            urllib.request,
            "urlopen",
            side_effect=AssertionError("network access attempted"),
        ):
            digest = sha256_repository_file(
                self.repository_root,
                HISTORICAL_PATH,
                mode="text",
            )
        self.assertEqual(digest, MAINTAINED_CANONICAL_SHA256)

    def test_24_utility_executes_no_artifact(self):
        executable_path = "artifacts/never-execute.py"
        self.write_bytes(
            executable_path,
            b"raise AssertionError('artifact was executed')\n",
        )
        with mock.patch.object(
            runpy,
            "run_path",
            side_effect=AssertionError("runpy execution attempted"),
        ), mock.patch.object(
            subprocess,
            "run",
            side_effect=AssertionError("subprocess execution attempted"),
        ), mock.patch.object(
            os,
            "system",
            side_effect=AssertionError("shell execution attempted"),
        ):
            digest = sha256_repository_file(
                self.repository_root,
                executable_path,
                mode="text",
            )
        self.assertEqual(
            digest,
            hashlib.sha256(
                b"raise AssertionError('artifact was executed')\n"
            ).hexdigest(),
        )

    def test_25_utility_grants_no_governance_authority(self):
        result = consume_maintained_artifact(
            self.repository_root,
            deepcopy(EXPECTED_HISTORICAL_ENTRY),
        )
        self.assertTrue(result["integrity_valid"])
        for field in (
            "release_approved",
            "risk_accepted",
            "public_disclosure_approved",
            "audit_closed",
            "authority_transferred",
            "final_governance_judgment",
            "decision_proof_sealed",
        ):
            with self.subTest(field=field):
                self.assertFalse(result[field])


if __name__ == "__main__":
    unittest.main()
