import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.decision_proof_replay_evaluator import (  # noqa: E402
    detect_forbidden_authority_claims,
    evaluate_release_proof,
    evaluate_replay_packet,
)


REPLAY_SCHEMA_PATH = (
    ROOT / "schemas" / "decision-proof-runtime-replay-packet.schema.json"
)
RELEASE_PROOF_SCHEMA_PATH = ROOT / "schemas" / "release-proof-automation.schema.json"
RELEASE_REPLAY_EXAMPLE_PATH = (
    ROOT
    / "examples"
    / "decision-proof-runtime-replay"
    / "release-governance-replay.json"
)
CROSS_ADAPTER_REPLAY_EXAMPLE_PATH = (
    ROOT
    / "examples"
    / "decision-proof-runtime-replay"
    / "cross-adapter-regression-replay.json"
)
RELEASE_PROOF_EXAMPLE_PATH = (
    ROOT / "examples" / "release-proof-automation" / "v0.7.0-release-proof.json"
)


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_subset(schema, instance, path="$"):
    schema_type = schema.get("type")

    if schema_type == "object":
        assert isinstance(instance, dict), f"{path} must be object"
        for required in schema.get("required", []):
            assert required in instance, f"{path}.{required} is required"
        allowed_properties = set(schema.get("properties", {}))
        if schema.get("additionalProperties") is False:
            extra = set(instance) - allowed_properties
            assert not extra, f"{path} has unexpected keys: {sorted(extra)}"
        for key, property_schema in schema.get("properties", {}).items():
            if key in instance:
                validate_subset(property_schema, instance[key], f"{path}.{key}")

    elif schema_type == "array":
        assert isinstance(instance, list), f"{path} must be array"
        if "minItems" in schema:
            assert len(instance) >= schema["minItems"], f"{path} must have enough items"
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(instance):
                validate_subset(item_schema, item, f"{path}[{index}]")

    elif schema_type == "string":
        assert isinstance(instance, str), f"{path} must be string"
        if "const" in schema:
            assert instance == schema["const"], f"{path} must equal {schema['const']}"
        if "enum" in schema:
            assert instance in schema["enum"], f"{path} must be one of {schema['enum']}"

    elif schema_type == "boolean":
        assert isinstance(instance, bool), f"{path} must be boolean"


class DecisionProofReplayEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.replay_schema = load_json(REPLAY_SCHEMA_PATH)
        self.release_proof_schema = load_json(RELEASE_PROOF_SCHEMA_PATH)
        self.release_replay_example = load_json(RELEASE_REPLAY_EXAMPLE_PATH)
        self.cross_adapter_replay_example = load_json(CROSS_ADAPTER_REPLAY_EXAMPLE_PATH)
        self.release_proof_example = load_json(RELEASE_PROOF_EXAMPLE_PATH)

    def test_examples_match_schemas(self):
        validate_subset(self.replay_schema, self.release_replay_example)
        validate_subset(self.replay_schema, self.cross_adapter_replay_example)
        validate_subset(self.release_proof_schema, self.release_proof_example)

    def test_replay_examples_pass(self):
        for example in [self.release_replay_example, self.cross_adapter_replay_example]:
            result = evaluate_replay_packet(example)

            self.assertTrue(result["replay_packet_valid"])
            self.assertFalse(result["replay_packet_invalid"])
            self.assertEqual(result["replay_findings"], [])
            self.assertEqual(result["missing_evidence"], [])

    def test_replay_packet_detects_missing_required_evidence(self):
        packet = copy.deepcopy(self.release_replay_example)
        for field in [
            "decision_id",
            "intent",
            "actor",
            "authority_source",
            "risk_class",
            "allowed_tools",
            "approval_required",
            "approval_state",
            "adapter_events",
            "runtime_events",
            "execution_trace",
            "evidence_refs",
            "rollback_plan",
            "rollback_surface",
            "replay_target",
            "replay_steps",
            "replay_result",
            "not_authority_statement",
            "sovereignty_statement",
        ]:
            packet.pop(field)

        result = evaluate_replay_packet(packet)

        self.assertTrue(result["replay_packet_invalid"])
        self.assertIn("missing_decision_id", result["replay_findings"])
        self.assertIn("missing_intent", result["replay_findings"])
        self.assertIn("missing_actor", result["replay_findings"])
        self.assertIn("missing_authority_source", result["replay_findings"])
        self.assertIn("missing_risk_class", result["replay_findings"])
        self.assertIn("missing_allowed_tools", result["replay_findings"])
        self.assertIn("missing_approval_required", result["replay_findings"])
        self.assertIn("missing_approval_state", result["replay_findings"])
        self.assertIn("missing_adapter_events", result["replay_findings"])
        self.assertIn("missing_runtime_events", result["replay_findings"])
        self.assertIn("missing_execution_trace", result["replay_findings"])
        self.assertIn("missing_evidence_refs", result["replay_findings"])
        self.assertIn("missing_rollback_plan", result["replay_findings"])
        self.assertIn("missing_rollback_surface", result["replay_findings"])
        self.assertIn("missing_replay_target", result["replay_findings"])
        self.assertIn("missing_replay_steps", result["replay_findings"])
        self.assertIn("missing_replay_result", result["replay_findings"])
        self.assertIn("missing_not_authority_statement", result["replay_findings"])
        self.assertIn("missing_sovereignty_statement", result["replay_findings"])

    def test_approval_required_requires_approval_state(self):
        packet = copy.deepcopy(self.release_replay_example)
        packet["approval_required"] = True
        packet["approval_state"] = "missing"

        result = evaluate_replay_packet(packet)

        self.assertTrue(result["replay_packet_invalid"])
        self.assertIn(
            "missing_approval_state_when_approval_is_required",
            result["replay_findings"],
        )

    def test_forbidden_authority_outputs_are_detected(self):
        packet = copy.deepcopy(self.release_replay_example)
        packet["runtime_output"] = {
            "decision_proof_sealed": True,
            "audit_closed": True,
            "release_approved": True,
            "rollback_executed": True,
            "final_governance_judgment": True,
        }

        claims = detect_forbidden_authority_claims(packet)
        result = evaluate_replay_packet(packet)

        self.assertIn("decision_proof_sealed", claims)
        self.assertIn("audit_closed", claims)
        self.assertIn("release_approved", claims)
        self.assertIn("rollback_executed", claims)
        self.assertIn("final_governance_judgment", claims)
        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn(
            "decision_proof_sealing_claimed_outside_aaos",
            result["replay_findings"],
        )
        self.assertIn("audit_closure_claimed_outside_aaos", result["replay_findings"])
        self.assertIn("release_authority_claimed_outside_aaos", result["replay_findings"])
        self.assertIn("rollback_authority_claimed_outside_aaos", result["replay_findings"])
        self.assertIn(
            "final_governance_authority_claimed_outside_aaos",
            result["replay_findings"],
        )
        self.assertTrue(result["fail_closed_recommended"])

    def test_release_proof_example_passes(self):
        result = evaluate_release_proof(self.release_proof_example)

        self.assertTrue(result["release_proof_consistency_passed"])
        self.assertFalse(result["release_proof_consistency_failed"])
        self.assertEqual(result["replay_findings"], [])
        self.assertEqual(result["missing_evidence"], [])

    def test_release_proof_detects_missing_evidence_and_boundary(self):
        proof = copy.deepcopy(self.release_proof_example)
        proof["readme_version_status"]["present"] = False
        proof["closing_prs"][0]["merged"] = False
        proof["release_tag"]["present"] = False
        proof["release_title_consistency"]["matches"] = False
        proof["release_body_consistency"]["governance_boundary_preserved"] = False
        proof["next_phase_declaration"]["matches_expected"] = False
        proof["decision_proof_replay_packet"]["present"] = False
        proof["governance_boundary_preservation"]["preserved"] = False
        proof["automation_checks"]["governance_boundary_preservation"] = False

        result = evaluate_release_proof(proof)

        self.assertTrue(result["release_proof_consistency_failed"])
        self.assertIn("missing_readme_version", result["replay_findings"])
        self.assertIn("release_proof_consistency_failed", result["replay_findings"])
        self.assertIn("release_title_mismatch", result["replay_findings"])
        self.assertIn("next_phase_mismatch", result["replay_findings"])
        self.assertIn("missing_release_proof_evidence", result["replay_findings"])
        self.assertIn("missing_governance_boundary_preservation", result["replay_findings"])

    def test_forbidden_evaluator_output_list_is_detected(self):
        packet = copy.deepcopy(self.release_replay_example)
        packet["unsafe_outputs"] = [
            "release_approved",
            "decision_proof_sealed",
            "audit_closed",
        ]

        result = evaluate_replay_packet(packet)

        self.assertTrue(result["authority_boundary_violation"])
        self.assertIn("release_authority_claimed_outside_aaos", result["replay_findings"])
        self.assertIn(
            "decision_proof_sealing_claimed_outside_aaos",
            result["replay_findings"],
        )
        self.assertIn("audit_closure_claimed_outside_aaos", result["replay_findings"])


if __name__ == "__main__":
    unittest.main()
