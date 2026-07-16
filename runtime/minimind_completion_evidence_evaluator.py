"""Evaluate static MiniMind completion evidence without running MiniMind.

This evaluator reconciles issue #9 declarations with repository artifacts. It
performs no model loading, inference, training, network access, tool execution,
or governance decision execution.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "examples" / "minimind" / "completion-evidence-matrix.json"
RADAR_NODE_PATH = ROOT / "examples" / "radar-nodes" / "minimind.yaml"

ALLOWED_IMPLEMENTATION_STATUSES = {
    "implemented",
    "implemented_as_skeleton",
    "renamed",
    "superseded",
    "placeholder",
    "missing",
    "deferred",
    "not_applicable",
}

MATERIALIZED_STATUSES = {
    "implemented",
    "implemented_as_skeleton",
    "renamed",
    "superseded",
}

ALLOWED_PATH_DISPOSITIONS = {
    "not_applicable",
    "renamed_and_consolidated",
    "declared_path_not_present",
    "maintained_at_declared_path",
}

EXPECTED_DECLARED_ARTIFACTS = {
    "contracts/minimind_admission_contract.yaml": "contract",
    "contracts/minimind_runtime_boundary.yaml": "contract",
    "contracts/minimind_tool_use_boundary.yaml": "contract",
    "contracts/minimind_verification_subject_boundary.yaml": "contract",
    "contracts/minimind_model_swappability_boundary.yaml": "contract",
    "schemas/minimind_admission_record.schema.json": "schema",
    "schemas/minimind_model_identity_record.schema.json": "schema",
    "schemas/minimind_runtime_configuration_snapshot.schema.json": "schema",
    "schemas/minimind_training_pipeline_reference.schema.json": "schema",
    "schemas/minimind_inference_trace_record.schema.json": "schema",
    "schemas/minimind_tool_use_experiment_record.schema.json": "schema",
    "schemas/minimind_runtime_failure_record.schema.json": "schema",
    "schemas/minimind_verification_replay_packet.schema.json": "schema",
    "runtime/evaluate_minimind_admission.py": "runtime_evaluator",
    "runtime/evaluate_minimind_runtime_boundary.py": "runtime_evaluator",
    "runtime/evaluate_minimind_tool_use_boundary.py": "runtime_evaluator",
    "runtime/evaluate_minimind_verification_subject.py": "runtime_evaluator",
    "runtime/evaluate_model_swappability.py": "runtime_evaluator",
    "examples/minimind/candidate_admission_record.json": "example",
    "examples/minimind/runtime_admit_with_constraints.json": "example",
    "examples/minimind/tool_use_review_required.json": "example",
    "examples/minimind/verification_authority_fail_closed.json": "example",
    "examples/minimind/model_swappability_baseline.json": "example",
    "tests/test_minimind_admission.py": "test",
    "tests/test_minimind_runtime_boundary.py": "test",
    "tests/test_minimind_tool_use_boundary.py": "test",
    "tests/test_minimind_verification_subject.py": "test",
    "tests/test_model_swappability.py": "test",
}

REQUIRED_SEMANTIC_REQUIREMENT_IDS = {
    "MM-SEM-001",
    "MM-SEM-002",
    "MM-SEM-003",
    "MM-SEM-004",
    "MM-SEM-005",
    "MM-SEM-006",
    "MM-SEM-007",
    "MM-SEM-008",
    "MM-SEM-009",
    "MM-SEM-010",
    "MM-SEM-011",
    "MM-SEM-012",
    "MM-SEM-013",
}

REPAIR_RADAR_REQUIREMENT_ID = "MM-REPAIR-RADAR-001"
CONSOLIDATED_SKELETON_PATH = (
    "contracts/minimind-local-model-runtime-governance-adapter.md"
)

REQUIRED_ROW_FIELDS = {
    "requirement_id",
    "source_issue",
    "requirement",
    "declared_path",
    "maintained_path",
    "artifact_type",
    "implementation_status",
    "path_disposition",
    "evidence_reference",
    "test_reference",
    "deferred_reason",
    "authority_boundary",
    "runtime_implementation_claimed",
    "notes",
}

REQUIRED_RADAR_FIELDS = {
    "source_url",
    "source_name",
    "source_type",
    "claimed_capability",
    "aaos_layer_mapping",
    "evidence_produced",
    "decision_boundary",
    "not_authority_statement",
    "risk_if_misclassified",
    "required_admission_record",
    "required_replay_or_audit_evidence",
    "status",
}

REQUIRED_AUTHORITY_BOUNDARIES = (
    "runtime specimen, not governance authority",
    "verification subject, not verification authority",
    "model output, not decision approval",
    "local inference, not sovereignty proof",
)

EXPECTED_RADAR_EVIDENCE = [
    "model_identity",
    "runtime_configuration",
    "training_pipeline_reference",
    "inference_trace",
    "prompt_response_trace",
    "tool_use_experiment",
    "runtime_failure",
    "drift_detection_input",
    "verification_harness_input",
    "model_swappability_baseline",
    "replay_packet",
]

PLACEHOLDER_SNIPPETS = {
    "this directory contains tests": "this_directory_contains_tests",
    "tests should verify": "tests_should_verify",
    "tests for governance contracts, schemas, and runtime evaluators": (
        "generic_test_directory_description"
    ),
}

PROHIBITED_AUTHORITY_PATTERNS = {
    "minimind_governance_authority_claimed": re.compile(
        r"\bminimind\s+is\s+(?:an?\s+)?governance authority\b", re.IGNORECASE
    ),
    "minimind_verification_authority_claimed": re.compile(
        r"\bminimind\s+is\s+(?:an?\s+)?verification authority\b", re.IGNORECASE
    ),
    "minimind_decision_approval_claimed": re.compile(
        r"\bminimind(?: model)? output\s+is\s+decision approval\b", re.IGNORECASE
    ),
    "local_inference_sovereignty_claimed": re.compile(
        r"\blocal inference\s+is\s+sovereignty proof\b", re.IGNORECASE
    ),
    "decision_proof_sealed_by_minimind": re.compile(
        r"(?:\bminimind\s+seals\s+decision proof\b|"
        r"\bdecision proof\s+is\s+sealed by\s+minimind\b)",
        re.IGNORECASE,
    ),
    "learning_proof_sealed_by_minimind": re.compile(
        r"(?:\bminimind\s+seals\s+learning proof\b|"
        r"\blearning proof\s+is\s+sealed by\s+minimind\b)",
        re.IGNORECASE,
    ),
}


def _add(findings: list[str], finding: str) -> None:
    if finding not in findings:
        findings.append(finding)


def _code(value: Any) -> str:
    return re.sub(r"[^A-Za-z0-9_.:-]+", "_", str(value))[:120]


def _safe_repository_path(root: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value or "\\" in value:
        return None
    pure_path = PurePosixPath(value)
    if pure_path.is_absolute() or ".." in pure_path.parts:
        return None
    candidate = (root / pure_path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def _read_json(path: Path, findings: list[str]) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
    except FileNotFoundError:
        _add(findings, "completion_matrix_missing")
        return {}
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        _add(findings, "completion_matrix_invalid_json")
        return {}
    if not isinstance(payload, dict):
        _add(findings, "completion_matrix_not_object")
        return {}
    return payload


def _decode_yaml_scalar(value: str) -> Any:
    if not value:
        return None
    if value.startswith('"'):
        return json.loads(value)
    if value == "true":
        return True
    if value == "false":
        return False
    if value == "null":
        return None
    return value


def _parse_radar_node(text: str, findings: list[str]) -> dict[str, Any]:
    """Parse the scalar/list YAML subset used by Governance Radar examples."""

    node: dict[str, Any] = {}
    active_list: str | None = None
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line.startswith("  - ") and active_list:
            try:
                item = _decode_yaml_scalar(raw_line[4:].strip())
            except (json.JSONDecodeError, TypeError):
                _add(findings, f"radar_invalid_list_scalar:{line_number}")
                continue
            node[active_list].append(item)
            continue
        if raw_line.startswith((" ", "\t")):
            _add(findings, f"radar_unsupported_indentation:{line_number}")
            continue
        match = re.fullmatch(r"([A-Za-z0-9_]+):(?:\s*(.*))?", raw_line)
        if not match:
            _add(findings, f"radar_invalid_line:{line_number}")
            active_list = None
            continue
        key, raw_value = match.groups()
        if key in node:
            _add(findings, f"radar_duplicate_field:{key}")
            active_list = None
            continue
        if not raw_value:
            node[key] = []
            active_list = key
            continue
        try:
            node[key] = _decode_yaml_scalar(raw_value)
        except (json.JSONDecodeError, TypeError):
            _add(findings, f"radar_invalid_scalar:{line_number}")
        active_list = None
    return node


def _validate_matrix_metadata(
    matrix: dict[str, Any], findings: list[str]
) -> None:
    if matrix.get("matrix_id") != "minimind-issue-9-completion-evidence-v1":
        _add(findings, "completion_matrix_id_invalid")
    if matrix.get("source_issue") != "#9":
        _add(findings, "completion_matrix_source_issue_invalid")
    if matrix.get("repair_issue") != "#235":
        _add(findings, "completion_matrix_repair_issue_invalid")
    if matrix.get("full_issue_9_implementation_claimed") is not False:
        _add(findings, "full_issue_9_implementation_claimed")

    status_definitions = matrix.get("implementation_status_definitions")
    if not isinstance(status_definitions, dict) or set(status_definitions) != (
        ALLOWED_IMPLEMENTATION_STATUSES
    ):
        _add(findings, "implementation_status_definitions_invalid")

    authority_boundary = matrix.get("authority_boundary")
    if not isinstance(authority_boundary, dict):
        _add(findings, "authority_boundary_invalid")
    else:
        if authority_boundary.get("boundary_id") != "minimind_subject_only_v1":
            _add(findings, "authority_boundary_id_invalid")
        statements = authority_boundary.get("statements")
        normalized = {
            str(statement).strip().casefold()
            for statement in statements
        } if isinstance(statements, list) else set()
        if normalized != set(REQUIRED_AUTHORITY_BOUNDARIES):
            _add(findings, "authority_boundary_statements_invalid")

    execution_boundary = matrix.get("execution_boundary")
    expected_execution_boundary = {
        "minimind_executed": False,
        "model_loaded": False,
        "inference_run": False,
        "training_or_fine_tuning_run": False,
        "live_tools_added": False,
        "credentials_added": False,
        "network_calls_added": False,
        "production_execution_added": False,
    }
    if execution_boundary != expected_execution_boundary:
        _add(findings, "execution_boundary_invalid")

    scope_boundary = matrix.get("scope_boundary")
    expected_scope_boundary = {
        "m15_issue": "#231",
        "m15_status_observed": "open",
        "m15_scope_modified": False,
        "m15_completion_status_modified": False,
        "v0_14_release_path_modified": False,
        "readme_release_status_modified": False,
        "release_published": False,
    }
    if scope_boundary != expected_scope_boundary:
        _add(findings, "m15_or_release_scope_boundary_invalid")


def _validate_row(
    row: Any,
    *,
    root: Path,
    index: int,
    findings: list[str],
) -> tuple[str | None, str | None]:
    if not isinstance(row, dict):
        _add(findings, f"requirement_row_not_object:{index}")
        return None, None

    requirement_id = row.get("requirement_id")
    row_code = _code(requirement_id or index)
    missing_fields = REQUIRED_ROW_FIELDS - set(row)
    for field in sorted(missing_fields):
        _add(findings, f"requirement_row_missing_field:{row_code}:{field}")

    if not isinstance(requirement_id, str) or not requirement_id:
        _add(findings, f"requirement_id_invalid:{index}")
        requirement_id = None
    if row.get("source_issue") not in {"#9", "#235"}:
        _add(findings, f"source_issue_invalid:{row_code}")
    if not isinstance(row.get("requirement"), str) or not row.get("requirement"):
        _add(findings, f"requirement_description_invalid:{row_code}")

    status = row.get("implementation_status")
    if status not in ALLOWED_IMPLEMENTATION_STATUSES:
        _add(findings, f"implementation_status_invalid:{row_code}")
        status = None

    path_disposition = row.get("path_disposition")
    if path_disposition not in ALLOWED_PATH_DISPOSITIONS:
        _add(findings, f"path_disposition_invalid:{row_code}")

    if row.get("authority_boundary") != "minimind_subject_only_v1":
        _add(findings, f"authority_boundary_reference_invalid:{row_code}")
    if row.get("runtime_implementation_claimed") is not False:
        _add(findings, f"runtime_implementation_claimed:{row_code}")

    maintained_path = row.get("maintained_path")
    if status in MATERIALIZED_STATUSES:
        resolved = _safe_repository_path(root, maintained_path)
        if resolved is None:
            _add(findings, f"maintained_path_invalid:{row_code}")
        elif not resolved.is_file():
            _add(findings, f"declared_implemented_artifact_missing:{row_code}")
        evidence_reference = row.get("evidence_reference")
        if not isinstance(evidence_reference, str) or not evidence_reference:
            _add(findings, f"completed_artifact_missing_evidence:{row_code}")

    if status == "implemented_as_skeleton":
        if "skeleton" not in str(row.get("notes", "")).casefold():
            _add(findings, f"skeleton_not_explicit:{row_code}")
        if row.get("full_runtime_implementation") is True:
            _add(findings, f"skeleton_represented_as_full_runtime:{row_code}")

    if status == "deferred":
        reason = row.get("deferred_reason")
        if not isinstance(reason, str) or not reason.strip():
            _add(findings, f"deferred_reason_missing:{row_code}")
        if maintained_path is not None:
            _add(findings, f"deferred_artifact_has_maintained_path:{row_code}")

    if status in {"missing", "not_applicable"} and maintained_path is not None:
        _add(findings, f"nonmaterialized_status_has_maintained_path:{row_code}")

    test_reference = row.get("test_reference")
    if test_reference is not None:
        resolved_test = _safe_repository_path(root, test_reference)
        if resolved_test is None or not resolved_test.is_file():
            _add(findings, f"test_reference_missing:{row_code}")

    declared_path = row.get("declared_path")
    if declared_path is not None and _safe_repository_path(root, declared_path) is None:
        _add(findings, f"declared_path_invalid:{row_code}")
        declared_path = None

    return requirement_id, declared_path


def _validate_requirement_inventory(
    matrix: dict[str, Any], *, root: Path, findings: list[str]
) -> tuple[int, Counter[str]]:
    requirements = matrix.get("requirements")
    if not isinstance(requirements, list):
        _add(findings, "requirements_inventory_invalid")
        return 0, Counter()

    requirement_ids: list[str] = []
    declared_paths: list[str] = []
    status_counts: Counter[str] = Counter()
    rows_by_declared_path: dict[str, dict[str, Any]] = {}

    for index, row in enumerate(requirements):
        requirement_id, declared_path = _validate_row(
            row, root=root, index=index, findings=findings
        )
        if requirement_id is not None:
            requirement_ids.append(requirement_id)
        if declared_path is not None:
            declared_paths.append(declared_path)
            if declared_path in rows_by_declared_path:
                _add(findings, f"declared_path_duplicate:{declared_path}")
            elif isinstance(row, dict):
                rows_by_declared_path[declared_path] = row
        if isinstance(row, dict) and row.get("implementation_status") in (
            ALLOWED_IMPLEMENTATION_STATUSES
        ):
            status_counts[str(row["implementation_status"])] += 1

    for duplicate_id in sorted(
        requirement_id
        for requirement_id, count in Counter(requirement_ids).items()
        if count > 1
    ):
        _add(findings, f"requirement_id_duplicate:{duplicate_id}")

    observed_issue_9_paths = {
        path
        for path, row in rows_by_declared_path.items()
        if row.get("source_issue") == "#9"
    }
    expected_issue_9_paths = set(EXPECTED_DECLARED_ARTIFACTS)
    for path in sorted(expected_issue_9_paths - observed_issue_9_paths):
        _add(findings, f"declared_requirement_not_inventoried:{path}")
    for path in sorted(observed_issue_9_paths - expected_issue_9_paths):
        _add(findings, f"unexpected_issue_9_declared_path:{path}")

    for path, artifact_type in EXPECTED_DECLARED_ARTIFACTS.items():
        row = rows_by_declared_path.get(path)
        if not row:
            continue
        row_code = _code(row.get("requirement_id", path))
        if row.get("artifact_type") != artifact_type:
            _add(findings, f"artifact_type_mismatch:{row_code}")
        if artifact_type == "contract":
            if row.get("implementation_status") != "implemented_as_skeleton":
                _add(findings, f"contract_not_classified_as_skeleton:{row_code}")
            if row.get("maintained_path") != CONSOLIDATED_SKELETON_PATH:
                _add(findings, f"contract_skeleton_path_invalid:{row_code}")
            if row.get("path_disposition") != "renamed_and_consolidated":
                _add(findings, f"contract_path_disposition_invalid:{row_code}")
        else:
            if row.get("implementation_status") != "deferred":
                _add(findings, f"unimplemented_issue_9_artifact_not_deferred:{row_code}")
            if row.get("path_disposition") != "declared_path_not_present":
                _add(findings, f"deferred_path_disposition_invalid:{row_code}")

    semantic_ids = {
        row.get("requirement_id")
        for row in requirements
        if isinstance(row, dict) and row.get("artifact_type") == "semantic_requirement"
    }
    for requirement_id in sorted(REQUIRED_SEMANTIC_REQUIREMENT_IDS - semantic_ids):
        _add(findings, f"semantic_requirement_not_inventoried:{requirement_id}")

    repair_row = next(
        (
            row
            for row in requirements
            if isinstance(row, dict)
            and row.get("requirement_id") == REPAIR_RADAR_REQUIREMENT_ID
        ),
        None,
    )
    if not repair_row:
        _add(findings, "minimind_radar_repair_not_inventoried")
    else:
        if repair_row.get("source_issue") != "#235":
            _add(findings, "minimind_radar_repair_source_issue_invalid")
        if repair_row.get("declared_path") != "examples/radar-nodes/minimind.yaml":
            _add(findings, "minimind_radar_repair_declared_path_invalid")
        if repair_row.get("implementation_status") != "implemented":
            _add(findings, "minimind_radar_repair_not_implemented")

    expected_summary = dict(sorted(status_counts.items()))
    if matrix.get("inventory_summary") != {
        "total_requirements": len(requirements),
        "declared_issue_9_artifacts": len(EXPECTED_DECLARED_ARTIFACTS),
        "status_counts": expected_summary,
        "full_issue_9_implementation_complete": False,
    }:
        _add(findings, "inventory_summary_mismatch")

    return len(requirements), status_counts


def _validate_radar_node(
    radar_path: Path, findings: list[str]
) -> dict[str, Any]:
    try:
        radar_text = radar_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        _add(findings, "minimind_radar_node_missing")
        return {}
    except (OSError, UnicodeDecodeError):
        _add(findings, "minimind_radar_node_unreadable")
        return {}

    folded = radar_text.casefold()
    for snippet, code in PLACEHOLDER_SNIPPETS.items():
        if snippet in folded:
            _add(findings, f"minimind_radar_placeholder_content:{code}")

    node = _parse_radar_node(radar_text, findings)
    for field in sorted(REQUIRED_RADAR_FIELDS - set(node)):
        _add(findings, f"minimind_radar_missing_field:{field}")

    scalar_fields = REQUIRED_RADAR_FIELDS - {
        "aaos_layer_mapping",
        "evidence_produced",
    }
    for field in sorted(scalar_fields & set(node)):
        if not isinstance(node[field], str) or not node[field].strip():
            _add(findings, f"minimind_radar_field_invalid:{field}")

    if node.get("source_url") != "https://github.com/jingyaogong/minimind":
        _add(findings, "minimind_radar_source_url_invalid")
    if node.get("source_name") != "MiniMind":
        _add(findings, "minimind_radar_source_name_invalid")
    if node.get("source_type") not in {"model-runtime", "local-runtime"}:
        _add(findings, "minimind_radar_source_type_invalid")
    if node.get("aaos_layer_mapping") != ["L3", "L4", "L4.5", "L6"]:
        _add(findings, "minimind_radar_layer_mapping_invalid")
    if node.get("evidence_produced") != EXPECTED_RADAR_EVIDENCE:
        _add(findings, "minimind_radar_evidence_produced_invalid")
    if node.get("required_admission_record") != "minimind_admission_record.json":
        _add(findings, "minimind_radar_admission_record_invalid")
    if node.get("required_replay_or_audit_evidence") != (
        "minimind_verification_replay_packet.json"
    ):
        _add(findings, "minimind_radar_replay_evidence_invalid")
    if node.get("status") != "candidate":
        _add(findings, "minimind_radar_status_invalid")

    not_authority = str(node.get("not_authority_statement", "")).casefold()
    for statement in REQUIRED_AUTHORITY_BOUNDARIES:
        if statement not in not_authority:
            _add(findings, f"minimind_radar_authority_boundary_missing:{_code(statement)}")

    for code, pattern in PROHIBITED_AUTHORITY_PATTERNS.items():
        if pattern.search(radar_text):
            _add(findings, code)

    return node


def evaluate_minimind_completion_evidence(
    *,
    matrix_path: Path | str = MATRIX_PATH,
    radar_path: Path | str = RADAR_NODE_PATH,
    repository_root: Path | str = ROOT,
) -> dict[str, Any]:
    """Return deterministic repository-truth findings for the MiniMind repair."""

    root = Path(repository_root).resolve()
    findings: list[str] = []
    matrix = _read_json(Path(matrix_path), findings)
    _validate_matrix_metadata(matrix, findings)
    requirement_count, status_counts = _validate_requirement_inventory(
        matrix, root=root, findings=findings
    )
    radar_node = _validate_radar_node(Path(radar_path), findings)

    serialized_matrix = json.dumps(matrix, sort_keys=True, ensure_ascii=False)
    for code, pattern in PROHIBITED_AUTHORITY_PATTERNS.items():
        if pattern.search(serialized_matrix):
            _add(findings, code)

    findings.sort()
    execution_boundary = matrix.get("execution_boundary")
    if not isinstance(execution_boundary, dict):
        execution_boundary = {}
    scope_boundary = matrix.get("scope_boundary")
    if not isinstance(scope_boundary, dict):
        scope_boundary = {}
    return {
        "decision": "pass" if not findings else "fail_closed",
        "completion_evidence_valid": not findings,
        "findings": findings,
        "requirements_evaluated": requirement_count,
        "declared_issue_9_artifacts_evaluated": len(EXPECTED_DECLARED_ARTIFACTS),
        "status_counts": dict(sorted(status_counts.items())),
        "radar_node_valid": bool(radar_node)
        and not any(
            finding.startswith(("minimind_radar_", "radar_"))
            for finding in findings
        ),
        "full_issue_9_implementation_claimed": matrix.get(
            "full_issue_9_implementation_claimed"
        ),
        "minimind_executed": execution_boundary.get("minimind_executed"),
        "m15_scope_modified": scope_boundary.get("m15_scope_modified"),
        "release_published": scope_boundary.get("release_published"),
    }
