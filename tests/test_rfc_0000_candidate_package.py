import hashlib
import importlib.util
import json
import math
import re
import struct
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RFC_DOCUMENT_PATH = ROOT / "docs" / "rfc" / "AAOS-RFC-0000.md"
CANONICALIZER_PATH = (
    ROOT / "tools" / "rfc" / "canonicalize_rfc_candidate.py"
)

JSON_PATHS = {
    "C0": ROOT / "spec" / "rfc" / "AAOS-RFC-0000.package.json",
    "C2": ROOT / "spec" / "rfc" / "AAOS-RFC-0000.manifest.json",
    "C3": ROOT / "spec" / "rfc" / "AAOS-RFC-0000.requirements.json",
    "C4": ROOT / "spec" / "rfc" / "AAOS-RFC-0000.transitions.json",
    "C5": ROOT / "spec" / "rfc" / "AAOS-RFC-0000.review-evidence.json",
    "C6": ROOT / "spec" / "rfc" / "AAOS-RFC-0000.change-versioning.json",
    "C7": ROOT / "spec" / "rfc" / "AAOS-RFC-0000.ecn.json",
    "C8": (
        ROOT
        / "spec"
        / "rfc"
        / "AAOS-RFC-0000.public-private-boundary.json"
    ),
    "C9": ROOT / "spec" / "rfc" / "AAOS-RFC-0000.traceability.json",
    "C10": (
        ROOT / "spec" / "rfc" / "AAOS-RFC-0000.disposition-template.json"
    ),
    "component_manifest": (
        ROOT / "spec" / "rfc" / "AAOS-RFC-0000.component-manifest.json"
    ),
}

COMPONENT_DIGEST_SUBJECTS = {
    "semantic_manifest_sha256": (JSON_PATHS["C2"], "RFC8785_JCS"),
    "requirement_registry_sha256": (JSON_PATHS["C3"], "RFC8785_JCS"),
    "human_readable_document_sha256": (RFC_DOCUMENT_PATH, "raw_bytes"),
    "component_manifest_sha256": (
        JSON_PATHS["component_manifest"],
        "RFC8785_JCS",
    ),
    "transition_registry_sha256": (JSON_PATHS["C4"], "RFC8785_JCS"),
    "review_evidence_registry_sha256": (
        JSON_PATHS["C5"],
        "RFC8785_JCS",
    ),
    "change_versioning_registry_sha256": (
        JSON_PATHS["C6"],
        "RFC8785_JCS",
    ),
    "ecn_contract_sha256": (JSON_PATHS["C7"], "RFC8785_JCS"),
    "public_private_boundary_sha256": (
        JSON_PATHS["C8"],
        "RFC8785_JCS",
    ),
    "traceability_manifest_sha256": (
        JSON_PATHS["C9"],
        "RFC8785_JCS",
    ),
    "disposition_template_sha256": (JSON_PATHS["C10"], "RFC8785_JCS"),
}

REQUIRED_REQUIREMENT_FIELDS = {
    "requirement_id",
    "requirement_version",
    "title",
    "normative_statement",
    "requirement_group",
    "applicable_rfc_classes",
    "applicable_roles",
    "applicable_package_components",
    "verification_classes",
    "required_inputs",
    "required_evidence",
    "positive_case",
    "negative_case",
    "adversarial_case",
    "unknown_case",
    "not_evaluable_behavior",
    "failure_or_restrictive_consequence",
    "public_claim_boundary",
    "private_l0_dependency",
    "source_review_refs",
    "normative_clause_refs",
    "predecessor_requirement_refs",
    "successor_requirement_refs",
    "specialized_identifier_mappings",
    "change_class",
    "status_within_candidate",
}

RFC_CLASSES = {
    "process",
    "standards_track",
    "profile",
    "informational",
    "experimental",
}

SOURCE_COMMENT_IDS = {
    5047457643,
    5047507591,
    5054243927,
    5054339690,
    5054380735,
    5054665217,
    5054777271,
    5054796507,
}

CLAUSE_PATTERN = re.compile(
    r"\*\*Clause ID: `(AAOS-RFC-0000-S\d{2}-C\d{2})`\*\*"
)
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
EXPECTED_CANDIDATE_PACKAGE_SHA256 = (
    "d6b00b1a70b6b5e89da576090f74eb8ef37193cee0983c86c3bdaada7ff0c81b"
)


sys.dont_write_bytecode = True
_MODULE_SPEC = importlib.util.spec_from_file_location(
    "aaos_rfc_0000_canonicalizer",
    CANONICALIZER_PATH,
)
if _MODULE_SPEC is None or _MODULE_SPEC.loader is None:
    raise RuntimeError("unable to load RFC-0000 canonicalization module")
JCS = importlib.util.module_from_spec(_MODULE_SPEC)
_MODULE_SPEC.loader.exec_module(JCS)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def as_list(value):
    if isinstance(value, list):
        return value
    return [value]


def values_for_key(value, key):
    found = []
    if isinstance(value, dict):
        for current_key, current_value in value.items():
            if current_key == key:
                found.append(current_value)
            found.extend(values_for_key(current_value, key))
    elif isinstance(value, list):
        for item in value:
            found.extend(values_for_key(item, key))
    return found


def float_from_ieee754(hex_bits):
    return struct.unpack(">d", struct.pack(">Q", int(hex_bits, 16)))[0]


def canonical_file_sha256(path):
    return hashlib.sha256(JCS.canonicalize_json(path.read_bytes())).hexdigest()


def lf_normalized_sha256(path):
    content = path.read_bytes()
    if b"\r" in content.replace(b"\r\n", b""):
        raise AssertionError("lone carriage return in RFC document")
    return hashlib.sha256(content.replace(b"\r\n", b"\n")).hexdigest()


class RFC8785CanonicalizationTests(unittest.TestCase):
    def test_01_official_rfc_8785_sample(self):
        source = r"""{
          "numbers": [333333333.33333329, 1E30, 4.50,
                      2e-3, 0.000000000000000000000000001],
          "string": "\u20ac$\u000F\u000aA'\u0042\u0022\u005c\\\"\/",
          "literals": [null, true, false]
        }"""
        expected = (
            r"""{"literals":[null,true,false],"numbers":[333333333.3333333,"""
            r"""1e+30,4.5,0.002,1e-27],"string":"€$\u000f\nA'B\"\\\\\"/"}"""
        ).encode("utf-8")

        self.assertEqual(JCS.canonicalize_json(source), expected)

    def test_02_all_finite_rfc_8785_appendix_b_numbers(self):
        samples = [
            ("0000000000000000", "0"),
            ("8000000000000000", "0"),
            ("0000000000000001", "5e-324"),
            ("8000000000000001", "-5e-324"),
            ("7fefffffffffffff", "1.7976931348623157e+308"),
            ("ffefffffffffffff", "-1.7976931348623157e+308"),
            ("4340000000000000", "9007199254740992"),
            ("c340000000000000", "-9007199254740992"),
            ("4430000000000000", "295147905179352830000"),
            ("44b52d02c7e14af5", "9.999999999999997e+22"),
            ("44b52d02c7e14af6", "1e+23"),
            ("44b52d02c7e14af7", "1.0000000000000001e+23"),
            ("444b1ae4d6e2ef4e", "999999999999999700000"),
            ("444b1ae4d6e2ef4f", "999999999999999900000"),
            ("444b1ae4d6e2ef50", "1e+21"),
            ("3eb0c6f7a0b5ed8c", "9.999999999999997e-7"),
            ("3eb0c6f7a0b5ed8d", "0.000001"),
            ("41b3de4355555553", "333333333.3333332"),
            ("41b3de4355555554", "333333333.33333325"),
            ("41b3de4355555555", "333333333.3333333"),
            ("41b3de4355555556", "333333333.3333334"),
            ("41b3de4355555557", "333333333.33333343"),
            ("becbf647612f3696", "-0.0000033333333333333333"),
            ("43143ff3c1cb0959", "1424953923781206.2"),
        ]

        for hex_bits, expected in samples:
            with self.subTest(hex_bits=hex_bits):
                value = float_from_ieee754(hex_bits)
                self.assertEqual(JCS.canonicalize(value).decode("ascii"), expected)

    def test_03_utf16_property_order_matches_rfc_8785(self):
        source = r"""{
          "\u20ac": "Euro Sign",
          "\r": "Carriage Return",
          "\ufb33": "Hebrew Letter Dalet With Dagesh",
          "1": "One",
          "\ud83d\ude00": "Emoji: Grinning Face",
          "\u0080": "Control",
          "\u00f6": "Latin Small Letter O With Diaeresis"
        }"""
        canonical = JCS.canonicalize_json(source)
        ordered_values = list(json.loads(canonical.decode("utf-8")).values())

        self.assertEqual(
            ordered_values,
            [
                "Carriage Return",
                "One",
                "Control",
                "Latin Small Letter O With Diaeresis",
                "Euro Sign",
                "Emoji: Grinning Face",
                "Hebrew Letter Dalet With Dagesh",
            ],
        )

    def test_04_duplicate_property_names_are_rejected(self):
        samples = [
            b'{"duplicate":1,"duplicate":2}',
            b'{"outer":{"duplicate":1,"duplicate":2}}',
        ]
        for sample in samples:
            with self.subTest(sample=sample):
                with self.assertRaises(JCS.DuplicatePropertyError):
                    JCS.canonicalize_json(sample)

    def test_05_lone_surrogates_are_rejected(self):
        samples = [
            r'{"value":"\ud800"}',
            r'{"value":"\udead"}',
            r'{"\ud800":"property name"}',
        ]
        for sample in samples:
            with self.subTest(sample=sample):
                with self.assertRaises(JCS.CanonicalizationError):
                    JCS.canonicalize_json(sample)

    def test_06_nonfinite_numbers_are_rejected(self):
        for value in [math.nan, math.inf, -math.inf]:
            with self.subTest(programmatic=value):
                with self.assertRaises(JCS.CanonicalizationError):
                    JCS.canonicalize(value)

        for token in [b"NaN", b"Infinity", b"-Infinity", b"1e9999"]:
            with self.subTest(json_token=token):
                with self.assertRaises(JCS.CanonicalizationError):
                    JCS.canonicalize_json(token)

    def test_07_repeated_canonicalization_is_byte_identical(self):
        source = (
            '{"z":[{"b":2,"a":1}],"a":"€","numbers":'
            "[333333333.33333329,1E30,2e-3]}"
        )
        outputs = {JCS.canonicalize_json(source) for _ in range(20)}

        self.assertEqual(len(outputs), 1)
        canonical = outputs.pop()
        self.assertEqual(
            JCS.canonicalize_json(canonical),
            canonical,
        )


class RFC0000CandidatePackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents = {
            component: load_json(path)
            for component, path in JSON_PATHS.items()
        }
        cls.markdown = RFC_DOCUMENT_PATH.read_text(encoding="utf-8")

    def test_08_all_expected_json_artifacts_parse_as_i_json(self):
        expected_names = {path.name for path in JSON_PATHS.values()}
        observed_names = {
            path.name for path in (ROOT / "spec" / "rfc").glob("*.json")
        }
        self.assertEqual(observed_names, expected_names)

        for component, path in JSON_PATHS.items():
            with self.subTest(component=component):
                raw = path.read_bytes()
                parsed = JCS.loads_i_json(raw)
                canonical = JCS.canonicalize(parsed)
                self.assertIsInstance(canonical, bytes)
                self.assertEqual(JCS.canonicalize_json(canonical), canonical)

    def test_09_requirement_registry_is_exact_and_complete(self):
        registry = self.documents["C3"]
        records = registry["requirements"]
        expected_ids = [
            "AAOS-REQ-0000-{:03d}".format(number)
            for number in range(1, 40)
        ]
        actual_ids = [record["requirement_id"] for record in records]

        self.assertEqual(registry["requirement_count"], 39)
        self.assertEqual(len(records), 39)
        self.assertEqual(registry["ordered_requirement_ids"], expected_ids)
        self.assertEqual(actual_ids, expected_ids)
        self.assertEqual(len(set(actual_ids)), 39)
        for record in records:
            with self.subTest(requirement_id=record["requirement_id"]):
                self.assertTrue(REQUIRED_REQUIREMENT_FIELDS <= set(record))
                self.assertTrue(record["normative_clause_refs"])

        artifact_text = self.markdown + "\n" + "\n".join(
            path.read_text(encoding="utf-8") for path in JSON_PATHS.values()
        )
        self.assertNotIn("AAOS-REQ-0000-040", artifact_text)

    def test_10_c1_clauses_have_complete_bidirectional_mapping(self):
        clause_ids = CLAUSE_PATTERN.findall(self.markdown)
        clause_id_set = set(clause_ids)
        requirements = self.documents["C3"]["requirements"]
        requirement_map = {
            record["requirement_id"]: record["normative_clause_refs"]
            for record in requirements
        }

        self.assertEqual(len(clause_ids), 57)
        self.assertEqual(len(clause_id_set), 57)
        self.assertEqual(
            set().union(*(set(refs) for refs in requirement_map.values())),
            clause_id_set,
        )
        for requirement_id, refs in requirement_map.items():
            with self.subTest(requirement_id=requirement_id):
                self.assertTrue(refs)
                self.assertTrue(set(refs) <= clause_id_set)

        trace_edges = self.documents["C9"]["requirement_to_clause_edges"]
        trace_map = {
            edge["source_artifact_id"]: edge["target_artifact_id"]
            for edge in trace_edges
        }
        self.assertEqual(trace_map, requirement_map)
        self.assertEqual(
            self.documents["C2"]["normative_assertion_order"],
            clause_ids,
        )

    def test_11_c2_requirement_order_statements_and_refs_equal_c3(self):
        manifest = self.documents["C2"]
        registry = self.documents["C3"]
        manifest_records = manifest["ordered_primary_requirement_records"]
        registry_records = registry["requirements"]

        self.assertEqual(len(manifest_records), 39)
        self.assertEqual(
            manifest["manifest_metadata"]["requirement_count"],
            registry["requirement_count"],
        )
        self.assertEqual(
            [record["requirement_id"] for record in manifest_records],
            registry["ordered_requirement_ids"],
        )
        for manifest_record, registry_record in zip(
            manifest_records,
            registry_records,
        ):
            with self.subTest(
                requirement_id=registry_record["requirement_id"]
            ):
                for field in [
                    "requirement_id",
                    "requirement_version",
                    "title",
                    "normative_statement",
                    "requirement_group",
                    "verification_classes",
                    "normative_clause_refs",
                    "status_within_candidate",
                ]:
                    self.assertEqual(
                        manifest_record[field],
                        registry_record[field],
                    )

        self.assertEqual(
            manifest["primary_normative_disposition_subject"],
            "semantic_manifest",
        )
        self.assertEqual(
            manifest["requirement_registry_ref"]["component_id"],
            "AAOS-RFC-0000-C3",
        )

    def test_12_c4_transition_ids_and_terminal_source_sets_are_exact(self):
        registry = self.documents["C4"]
        rules = registry["transition_rules"]
        transition_ids = [rule["transition_rule_id"] for rule in rules]

        self.assertEqual(len(transition_ids), len(set(transition_ids)))
        self.assertIsNone(
            re.search(
                r"\beligible\b",
                JSON_PATHS["C4"].read_text(encoding="utf-8"),
                flags=re.IGNORECASE,
            )
        )
        self.assertEqual(
            {
                rule["from_status"]
                for rule in rules
                if rule["to_status"] == "rejected"
            },
            {"draft", "candidate", "provisional"},
        )
        self.assertEqual(
            {
                rule["from_status"]
                for rule in rules
                if rule["to_status"] == "withdrawn"
            },
            {
                "draft",
                "candidate",
                "provisional",
                "accepted",
                "stable",
                "deprecated",
            },
        )

        stable_withdrawal = [
            rule
            for rule in rules
            if rule["from_status"] == "stable"
            and rule["to_status"] == "withdrawn"
        ]
        self.assertEqual(len(stable_withdrawal), 1)
        self.assertEqual(
            stable_withdrawal[0]["rule_effect"],
            "permitted_only_for_critical_conditions",
        )

    def test_13_c4_direct_transition_restrictions_are_explicit(self):
        rules = self.documents["C4"]["transition_rules"]
        direct_acceptance = [
            rule
            for rule in rules
            if rule["from_status"] == "candidate"
            and rule["to_status"] == "accepted"
        ]
        effect_by_class = {}
        for rule in direct_acceptance:
            for rfc_class in rule["applicable_rfc_classes"]:
                effect_by_class[rfc_class] = rule["rule_effect"]

        self.assertTrue(effect_by_class["process"].startswith("permitted"))
        self.assertTrue(
            effect_by_class["informational"].startswith("permitted")
        )
        self.assertEqual(effect_by_class["standards_track"], "prohibited")
        self.assertEqual(effect_by_class["profile"], "prohibited")
        self.assertEqual(effect_by_class["experimental"], "prohibited")

        experimental_stable = [
            rule
            for rule in rules
            if rule["from_status"] == "accepted"
            and rule["to_status"] == "stable"
            and "experimental" in rule["applicable_rfc_classes"]
        ]
        self.assertEqual(len(experimental_stable), 1)
        self.assertEqual(experimental_stable[0]["rule_effect"], "prohibited")

    def test_14_c5_has_five_class_branches_for_core_transitions(self):
        c4_rules = self.documents["C4"]["transition_rules"]
        c5_rules = self.documents["C5"]["review_evidence_rules"]
        transition_pairs = [
            ("candidate", "provisional"),
            ("provisional", "accepted"),
            ("accepted", "stable"),
        ]

        collected = {}
        for from_status, to_status in transition_pairs:
            transition_ids = {
                rule["transition_rule_id"]
                for rule in c4_rules
                if rule["from_status"] == from_status
                and rule["to_status"] == to_status
            }
            branches = []
            for evidence_rule in c5_rules:
                refs = set(as_list(evidence_rule["transition_rule_ref"]))
                if refs & transition_ids:
                    branches.extend(
                        evidence_rule.get(
                            "class_specific_evidence_branches",
                            [],
                        )
                    )
            by_class = {branch["rfc_class"]: branch for branch in branches}
            self.assertEqual(set(by_class), RFC_CLASSES)
            for branch in by_class.values():
                self.assertTrue(branch["minimum_evidence"])
            collected[(from_status, to_status)] = by_class

        stable = collected[("accepted", "stable")]
        self.assertEqual(
            stable["process"]["minimum_evidence"],
            [
                "at least one completed downstream RFC cycle using the process",
                "no unresolved critical governance contradiction",
                (
                    "review records demonstrate that status, requirement, "
                    "and change-control rules were usable"
                ),
                "exact human disposition",
            ],
        )
        self.assertEqual(
            stable["standards_track"]["minimum_evidence"],
            [
                (
                    "at least two independent implementations or one "
                    "implementation plus one independent offline "
                    "validator/specimen"
                ),
                (
                    "applicable conformance requirements exercised through "
                    "positive, negative, adversarial, and indeterminate cases"
                ),
                (
                    "no unresolved critical authority-boundary or "
                    "fail-open defect"
                ),
                "version and migration behavior demonstrated",
                "exact human disposition",
            ],
        )
        self.assertEqual(
            stable["profile"]["minimum_evidence"],
            [
                "one conformant base implementation",
                "one profile-specific implementation or specimen",
                (
                    "proof that profile rules strengthen or restrict without "
                    "weakening the Base Profile"
                ),
                "profile-specific conformance evidence",
                "exact human disposition",
            ],
        )
        self.assertIn(
            "normally_unnecessary",
            stable["informational"]["transition_mode"],
        )
        self.assertEqual(
            stable["experimental"]["transition_mode"],
            "prohibited",
        )

    def test_15_c6_separates_semantic_class_from_version_increment(self):
        registry = self.documents["C6"]
        records = registry["change_class_records"]
        by_class = {
            record["semantic_change_class"]: record for record in records
        }

        self.assertEqual(
            set(by_class),
            {
                "editorial",
                "clarifying",
                "additive_compatible",
                "restrictive",
                "breaking",
            },
        )
        self.assertTrue(
            registry["classification_policy"][
                "semantic_change_class_and_resulting_version_increment_are_separate_required_fields"
            ]
        )
        for record in records:
            self.assertIn("semantic_change_class", record)
            self.assertIn("resulting_version_increment", record)
            self.assertIn("normative_definition", record)

        self.assertEqual(
            set(by_class["clarifying"]["forbidden_semantic_effects"]),
            {
                "required evidence",
                "Authority",
                "object meaning",
                "state meaning",
                "failure behavior",
                "interface obligation",
                "conformance outcome",
                "public claim boundary",
            },
        )
        self.assertEqual(
            by_class["restrictive"]["resulting_version_increment"]["default"],
            "MAJOR",
        )
        preservation = registry[
            "compatibility_preservation_profile_exception"
        ]
        self.assertEqual(
            preservation["conditional_resulting_version_increment"],
            "MINOR",
        )
        self.assertEqual(len(preservation["must_prove_all"]), 7)

    def test_16_c7_preserves_restrictive_30_30_60_contract(self):
        contract = self.documents["C7"]

        self.assertEqual(contract["maximum_initial_validity_days"], 30)
        self.assertEqual(contract["maximum_single_renewal_days"], 30)
        self.assertEqual(contract["absolute_process_validity_days"], 60)
        self.assertEqual(contract["maximum_renewal_count"], 1)
        self.assertFalse(contract["renewal_policy"]["second_renewal_permitted"])
        self.assertFalse(
            contract["expiry_policy"]["automatic_permission_after_expiry"]
        )
        prohibited = set(contract["prohibited_effects"])
        self.assertTrue(
            {
                "expand Authority",
                "waive mandatory evidence",
                "convert unknown into allow",
                "convert not_evaluable into allow",
                "silently mutate accepted RFC text",
                "become permanent through repeated renewal",
            }
            <= prohibited
        )

    def test_17_c8_receipt_has_exact_mandatory_claim_boundary(self):
        boundary = self.documents["C8"]
        receipt = boundary["private_dependency_review_receipt_contract"]

        self.assertEqual(
            receipt["claim_boundary"],
            [
                "receipt proves only the declared bounded review result",
                "receipt does not prove full private implementation",
            ],
        )
        self.assertTrue(receipt["claim_boundary_field_mandatory"])
        self.assertIn("claim_boundary", receipt["required_fields"])
        self.assertEqual(
            set(receipt["allowed_review_results"]),
            {
                "satisfied",
                "satisfied_with_restrictions",
                "blocked_pending_private_input",
                "contradiction_found",
                "not_evaluable",
            },
        )
        self.assertIn(
            "public semantic precedence != private institutional applicability",
            boundary["boundary_invariants"],
        )

    def test_18_c9_binds_exact_eight_source_comment_ids(self):
        traceability = self.documents["C9"]
        reviews = traceability["immutable_source_reviews"]
        actual_ids = [review["comment_id"] for review in reviews]

        self.assertEqual(len(actual_ids), 8)
        self.assertEqual(set(actual_ids), SOURCE_COMMENT_IDS)
        self.assertEqual(len(set(actual_ids)), 8)
        for review in reviews:
            self.assertIn(
                "issuecomment-{}".format(review["comment_id"]),
                review["url"],
            )
            self.assertFalse(review["mutable_title_is_identity"])

    def test_19_c10_uses_external_exact_git_binding_and_phase_6_is_unstarted(self):
        disposition = self.documents["C10"]
        repository = disposition["repository_identity_contract"]
        record = disposition["unexecuted_disposition_record"]

        self.assertEqual(disposition["phase_6_state"], "not_started")
        self.assertEqual(
            repository["repository_identity_state"],
            "materialized_exact_identity_bound_in_commit_external_receipt",
        )
        self.assertEqual(repository["repository"], "aa-os/aaos-public")
        self.assertEqual(
            repository["branch"],
            "agent/rfc-0000-candidate-package",
        )
        self.assertEqual(
            repository["base_commit_sha"],
            "9259c2eebffb98352a2f79783d6c345177a5fc77",
        )
        for field in ["final_commit_sha", "final_tree_sha"]:
            self.assertTrue(repository[field]["required"])
            self.assertEqual(
                repository[field]["value_location"],
                "phase_5_external_verification_receipt",
            )
        self.assertIsNone(record["disposition"])
        self.assertEqual(record["resulting_rfc_status"], "not_assigned")
        self.assertEqual(
            record["execution_state"],
            "not_executed_phase_6_not_started",
        )

    def test_20_no_artifact_assigns_candidate_as_rfc_status(self):
        observed_statuses = []
        for document in self.documents.values():
            observed_statuses.extend(values_for_key(document, "rfc_status"))

        self.assertTrue(observed_statuses)
        self.assertEqual(set(observed_statuses), {"not_assigned"})
        self.assertIsNone(
            re.search(
                r"\brfc_status\s*=\s*candidate\b",
                self.markdown,
                flags=re.IGNORECASE,
            )
        )
        for path in JSON_PATHS.values():
            self.assertIsNone(
                re.search(
                    r'"rfc_status"\s*:\s*"candidate"',
                    path.read_text(encoding="utf-8"),
                    flags=re.IGNORECASE,
                )
            )

    def test_21_c0_digest_values_recompute_when_recorded(self):
        package = self.documents["C0"]
        component_digests = package["component_digests"]
        self.assertEqual(
            set(component_digests),
            set(COMPONENT_DIGEST_SUBJECTS),
        )

        recorded = {
            name: value
            for name, value in component_digests.items()
            if isinstance(value, str) and SHA256_PATTERN.fullmatch(value)
        }
        self.assertEqual(set(recorded), set(COMPONENT_DIGEST_SUBJECTS))
        for name, expected in recorded.items():
            path, digest_mode = COMPONENT_DIGEST_SUBJECTS[name]
            with self.subTest(component_digest=name):
                if digest_mode == "raw_bytes":
                    actual = lf_normalized_sha256(path)
                else:
                    actual = canonical_file_sha256(path)
                self.assertEqual(actual, expected)

        digest_contract = package["candidate_package_digest_contract"]
        self.assertFalse(digest_contract["descriptor_contains_its_own_digest"])
        self.assertEqual(
            digest_contract["candidate_package_sha256_value_location"],
            "phase_5_external_verification_receipt",
        )
        computed = hashlib.sha256(JCS.canonicalize(package)).hexdigest()
        self.assertEqual(computed, EXPECTED_CANDIDATE_PACKAGE_SHA256)


if __name__ == "__main__":
    unittest.main()
