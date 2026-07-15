"""Regression tests for the reader-facing M14 post-release state."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT_PATHS = {
    "MODA mapping": ROOT
    / "docs"
    / "public-integration-pack"
    / "m14-moda-ai-risk-framework-mapping.md",
    "NVIDIA skill admission": ROOT
    / "docs"
    / "capability-supply-chain"
    / "nvidia-skills-admission.md",
}
OBSOLETE_PHRASES = (
    "Status: M14 active work, not complete.",
    "Target future release path: v0.13.0, not released.",
    "M14 active-work and future v0.13.0 status",
    "This document is M14 active work",
    "v0.13.0 is a target future release path and is not released.",
)
HISTORICAL_REFERENCES = {
    "MODA mapping": ("PR #205", "source issue #181", "M14 tracker #201"),
    "NVIDIA skill admission": ("PR #208", "source issue #192", "M14 tracker #201"),
}
GOVERNANCE_STATEMENTS = (
    "Decision Proof sealing remains AAOS-owned.",
    "AAOS remains the decision sovereignty layer.",
)


class M14PostReleaseDocumentationStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents = {
            name: path.read_text(encoding="utf-8")
            for name, path in DOCUMENT_PATHS.items()
        }

    def test_obsolete_active_and_unreleased_phrases_are_absent(self):
        for document_name, document_text in self.documents.items():
            for phrase in OBSOLETE_PHRASES:
                with self.subTest(document=document_name, phrase=phrase):
                    self.assertNotIn(phrase, document_text)

    def test_documents_record_current_m14_and_release_state(self):
        for document_name, document_text in self.documents.items():
            with self.subTest(document=document_name, state="M14"):
                self.assertIn("M14 completed", document_text)
            with self.subTest(document=document_name, state="release"):
                self.assertIn("published v0.13.0", document_text)

    def test_documents_record_historical_implementation_references(self):
        for document_name, phrases in HISTORICAL_REFERENCES.items():
            for phrase in phrases:
                with self.subTest(document=document_name, phrase=phrase):
                    self.assertIn(phrase, self.documents[document_name])

    def test_documents_preserve_aaos_governance_boundaries(self):
        for document_name, document_text in self.documents.items():
            for statement in GOVERNANCE_STATEMENTS:
                with self.subTest(document=document_name, statement=statement):
                    self.assertIn(statement, document_text)


if __name__ == "__main__":
    unittest.main()
