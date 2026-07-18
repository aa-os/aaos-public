"""Deterministic, inert M15 Track D cross-control regression evaluator."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any


SCHEMA_VERSION = "m15-cross-control-regression/v1"
MAX_NESTING_DEPTH = 64
MAX_CONTAINERS = 10000

SENSITIVE_KEYS = re.compile(
    r"(?:password|passwd|secret|credential|api[_-]?key|access[_-]?token|"
    r"refresh[_-]?token|cookie|private[_-]?key|client[_-]?secret)",
    re.IGNORECASE,
)
SENSITIVE_VALUES = (
    ("secret-shaped", re.compile(r"\b(?:sk|ghp|github_pat)-[A-Za-z0-9_-]{8,}\b")),
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("authorization-header", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{8,}", re.IGNORECASE)),
    ("credential-assignment", re.compile(r"\b(?:password|secret|token|api[_-]?key)\s*[:=]\s*\S+", re.IGNORECASE)),
)

RULES = (
    ("provenance-is-identity-proof", (r"provenance.{0,40}identity proof", r"bot.{0,40}identity proof")),
    ("workflow-is-human-approval", (r"workflow success.{0,40}(?:human|review|merge) approv", r"reviewer routing.{0,40}completed review", r"schema validation.{0,40}(?:merge|approv)")),
    ("self-review-approval", (r"self.{0,20}(?:review|approv)", r"remove.{0,30}human.review.required")),
    ("learning-proof-training-authority", (r"learning proof.{0,60}(?:approved training|training data approved|retention approved|memory persistence approved)" ,)),
    ("learning-proof-skill-admission", (r"learning proof.{0,60}(?:admitted skill|skill creation approved|skill admission)" ,)),
    ("capability-pack-admission", (r"capability (?:memory )?pack.{0,70}(?:installed|admitted|registered|executable|runtime authoriz)",)),
    ("runtime-compatibility-is-authorization", (r"runtime compatibility.{0,40}runtime authoriz",)),
    ("generated-specification-is-tool", (r"generated specification.{0,40}executable tool",)),
    ("revoked-cache-remains-executable", (r"revoked.{0,80}cached dependenc.{0,50}executable",)),
    ("stale-evidence-treated-current", (r"stale.{0,50}(?:treated as )?current", r"superseded.{0,50}(?:treated as )?current")),
    ("incomplete-extraction-admitted", (r"incomplete extraction.{0,50}admitted", r"extraction status.{0,30}(?:absent|missing).{0,40}admitted")),
    ("digest-change-bypasses-readmission", (r"(?:source|dependency) digest.{0,60}(?:bypass|without) re[ -]admission",)),
    ("rollback-authority-claim", (r"rollback readiness.{0,50}rollback authoriz", r"rollback (?:authorized|executed)")),
    ("deletion-authority-claim", (r"deletion evidence.{0,60}(?:physical erasure|provider.side deletion|deletion authoriz|deletion execution)", r"physical erasure (?:proved|confirmed)")),
    ("portability-authority-claim", (r"portability evidence.{0,60}(?:provider migration|replacement.model authoriz|production execution)",)),
    ("decision-proof-fabricated", (r"fabricated decision proof",)),
    ("decision-proof-digest-reuse", (r"learning proof digest.{0,50}decision proof digest",)),
    ("decision-proof-linkage-escalation", (r"decision proof linkage.{0,50}(?:verified|verification|execution authority|sealed|sealing)",)),
    ("decision-proof-verification-is-sealing", (r"decision proof verification.{0,40}(?:sealed|sealing)",)),
    ("decision-proof-reference-is-execution", (r"decision proof reference.{0,60}(?:rollback|deletion) execution",)),
    ("authority-escalation", (r"(?:governance|policy|identity|runtime|execution) authority (?:granted|approved|transferred)", r"risk acceptance (?:granted|approved|complete)", r"(?:deployment|installation|package admission|tool registration) approval (?:granted|complete)", r"audit closure (?:granted|complete)", r"waiver approval (?:granted|complete)", r"(?:learning proof|decision proof) sealing (?:granted|complete)")),
    ("m15-completion-bypass", (r"#231 (?:is )?closed", r"m15 (?:is )?complete", r"completion review (?:is )?approved", r"release readiness (?:is )?final")),
    ("release-publication-bypass", (r"v0\.14\.0 publication (?:is )?authorized", r"release tag (?:has been )?created", r"github release (?:has been )?(?:created|approved)")),
    ("public-output-authorization-bypass", (r"public evidence.{0,60}public.output authoriz", r"public evidence.{0,60}(?:expose|disclose) sensitive")),
)

GOVERNED_KEY_PATTERNS = (
    "governance-authority", "policy-authority", "identity-authority",
    "risk-accept", "deployment-approv", "installation-approv",
    "package-admission", "tool-registration", "runtime-author",
    "rollback-author", "rollback-execut", "deletion-author",
    "deletion-execut", "provider-migration", "replacement-model-author",
    "audit-clos", "waiver-approv", "authority-transfer",
    "learning-proof-seal", "decision-proof-seal", "m15-complet",
    "release-approv",
)

STRUCTURED_SENSITIVE_KEYS = (
    (re.compile(r"confidential.*prompt|prompt.*confidential", re.IGNORECASE), "confidential-prompt", "public_output_contains_private_context", "private_repo_content"),
    (re.compile(r"hidden.*reason|reasoning.*trace|private.*trace", re.IGNORECASE), "hidden-reasoning-trace", "public_output_contains_private_context", "private_repo_content"),
    (re.compile(r"personal.*identifier|personally.*identifiable|customer.*identifier", re.IGNORECASE), "personal-identifier", "public_output_contains_private_context", "private_repo_content"),
    (re.compile(r"patient.*identifier|medical.*identifier|health.*identifier", re.IGNORECASE), "medical-identifier", "public_output_contains_private_context", "private_repo_content"),
    (re.compile(r"financial.*identifier|brokerage.*identifier|account.*number", re.IGNORECASE), "financial-identifier", "public_output_contains_private_context", "private_repo_content"),
    (re.compile(r"private.*evaluation|confidential.*evaluation", re.IGNORECASE), "private-evaluation", "public_output_contains_private_context", "private_repo_content"),
    (re.compile(r"provider.*managed.*memory|provider.*memory", re.IGNORECASE), "provider-managed-memory", "public_output_contains_private_context", "private_repo_content"),
    (re.compile(r"production.*account|production.*tenant", re.IGNORECASE), "production-account", "public_output_contains_private_context", "private_repo_content"),
    (re.compile(r"internal.*path|private.*file.*path", re.IGNORECASE), "internal-path", "public_output_contains_private_file_path", "private_file_path"),
    (re.compile(r"private.*config|confidential.*config", re.IGNORECASE), "private-configuration", "public_output_contains_private_config_excerpt", "private_config_excerpt"),
    (re.compile(r"cross.*repo.*private.*summary|private.*cross.*repo.*summary", re.IGNORECASE), "cross-repository-private-summary", "public_output_contains_cross_repo_summary", "cross_repo_private_summary"),
)

STRUCTURED_SENSITIVE_CONTENT = (
    (re.compile(r"confidential\s+prompt", re.IGNORECASE), "confidential-prompt", "public_output_contains_private_context", "private_repo_content"),
    (re.compile(r"hidden\s+(?:reasoning|trace)|reasoning\s+trace", re.IGNORECASE), "hidden-reasoning-trace", "public_output_contains_private_context", "private_repo_content"),
    (re.compile(r"personal\s+identifier|personally\s+identifiable", re.IGNORECASE), "personal-identifier", "public_output_contains_private_context", "private_repo_content"),
    (re.compile(r"patient\s+identifier|medical\s+identifier", re.IGNORECASE), "medical-identifier", "public_output_contains_private_context", "private_repo_content"),
    (re.compile(r"financial\s+identifier|brokerage\s+identifier", re.IGNORECASE), "financial-identifier", "public_output_contains_private_context", "private_repo_content"),
    (re.compile(r"private\s+evaluation", re.IGNORECASE), "private-evaluation", "public_output_contains_private_context", "private_repo_content"),
    (re.compile(r"provider[- ]managed\s+memory", re.IGNORECASE), "provider-managed-memory", "public_output_contains_private_context", "private_repo_content"),
    (re.compile(r"production\s+account", re.IGNORECASE), "production-account", "public_output_contains_private_context", "private_repo_content"),
    (re.compile(r"internal\s+(?:file\s+)?path", re.IGNORECASE), "internal-path", "public_output_contains_private_file_path", "private_file_path"),
    (re.compile(r"private\s+configuration", re.IGNORECASE), "private-configuration", "public_output_contains_private_config_excerpt", "private_config_excerpt"),
    (re.compile(r"cross[- ]repository\s+private\s+summary", re.IGNORECASE), "cross-repository-private-summary", "public_output_contains_cross_repo_summary", "cross_repo_private_summary"),
)

SOURCE_CONTROL_REQUIRED_FIELDS = {
    "m14-public-output-exfiltration": {
        "public_issue_exfiltration_gate_valid", "public_output_blocked",
        "public_output_allowed", "redaction_required", "human_review_required",
    },
    "m14-ai-provenance": {
        "ai_pr_provenance_valid", "workflow_security_valid",
        "human_review_required", "reviewer_routing_required",
    },
    "m14-skill-admission": {
        "ready_for_review", "candidate_admission_state", "outputs", "reasons",
    },
    "external-evidence-admission": {
        "external_evidence_admission_valid", "admission_result",
        "decision_path_eligible", "fail_closed",
    },
    "m14-cross-control-authority": {
        "valid", "effective_control_result", "authority_violation_detected",
        "outputs",
    },
}


class _MalformedGraph(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _path_text(path: tuple[str, ...]) -> str:
    safe_path = (
        "<redacted-key>"
        if any(pattern.search(segment) for _category, pattern in SENSITIVE_VALUES)
        else segment
        for segment in path
    )
    return ".".join(safe_path) if path else "$"


def _mapping_items(value: Mapping[Any, Any]) -> list[tuple[Any, Any]]:
    try:
        raw_items = list(value.items())
    except Exception as exc:
        raise _MalformedGraph("hostile-mapping") from exc
    items: list[tuple[Any, Any]] = []
    for raw_item in raw_items:
        try:
            key, child = raw_item
        except Exception as exc:
            raise _MalformedGraph("hostile-mapping") from exc
        items.append((key, child))
    return items


def _validate_inert_graph(root: Any) -> None:
    for _kind, _path, _text in _walk_inert(root):
        pass


def _walk_inert(root: Any):
    """Yield scalar/key text without recursion or dereferencing external state."""
    stack = [(root, (), 0, frozenset())]
    seen: set[int] = set()
    containers = 0
    while stack:
        value, path, depth, ancestors = stack.pop()
        if isinstance(value, (Mapping, list, tuple)):
            identity = id(value)
            if identity in ancestors:
                raise _MalformedGraph("cyclic-container")
            if identity in seen:
                raise _MalformedGraph("shared-container")
            if depth > MAX_NESTING_DEPTH:
                raise _MalformedGraph("nesting-limit")
            seen.add(identity)
            containers += 1
            if containers > MAX_CONTAINERS:
                raise _MalformedGraph("container-limit")
            child_ancestors = ancestors | {identity}
        else:
            child_ancestors = ancestors
        if isinstance(value, Mapping):
            items = _mapping_items(value)
            for key, child in reversed(items):
                key_text = key if isinstance(key, str) else f"<{type(key).__name__}>"
                yield "key", path + (key_text,), key_text
                stack.append((child, path + (key_text,), depth + 1, child_ancestors))
        elif isinstance(value, (list, tuple)):
            try:
                for index in range(len(value) - 1, -1, -1):
                    stack.append((value[index], path + (str(index),), depth + 1, child_ancestors))
            except Exception as exc:
                raise _MalformedGraph("hostile-mapping") from exc
        elif isinstance(value, (str, int, float, bool)) or value is None:
            yield "value", path, str(value)
        else:
            yield "value", path, f"<{type(value).__name__}>"


def _inspect_record(
    record: Mapping[str, Any], *, inspect_sensitive: bool = True, inspect_boundaries: bool = True
) -> dict[str, Any]:
    findings: set[str] = set()
    sensitive = False
    source_fields = {
        "public_output_contains_private_context": False,
        "public_output_contains_secret_like_string": False,
        "public_output_contains_private_file_path": False,
        "public_output_contains_private_config_excerpt": False,
        "public_output_contains_cross_repo_summary": False,
    }
    blocked_classes: set[str] = set()
    try:
        for kind, path, text in _walk_inert(record):
            location = _path_text(path)
            if inspect_sensitive and kind == "key" and SENSITIVE_KEYS.search(text):
                findings.add(f"sensitive:{location}:credential-or-secret-key")
                source_fields["public_output_contains_secret_like_string"] = True
                blocked_classes.add("secret_like_string")
                sensitive = True
            if inspect_sensitive and kind == "key":
                for category, pattern in SENSITIVE_VALUES:
                    if pattern.search(text):
                        findings.add(f"sensitive:{location}:{category}")
                        source_fields["public_output_contains_secret_like_string"] = True
                        blocked_classes.add("secret_like_string")
                        sensitive = True
                for pattern, category, source_field, blocked_class in STRUCTURED_SENSITIVE_KEYS:
                    if pattern.search(text):
                        findings.add(f"sensitive:{location}:{category}")
                        source_fields[source_field] = True
                        blocked_classes.add(blocked_class)
                        sensitive = True
            if inspect_sensitive and kind == "value":
                for pattern, category, source_field, blocked_class in STRUCTURED_SENSITIVE_CONTENT:
                    if pattern.search(text):
                        findings.add(f"sensitive:{location}:{category}")
                        source_fields[source_field] = True
                        blocked_classes.add(blocked_class)
                        sensitive = True
                for category, pattern in SENSITIVE_VALUES:
                    if pattern.search(text):
                        findings.add(f"sensitive:{location}:{category}")
                        source_fields["public_output_contains_secret_like_string"] = True
                        blocked_classes.add("secret_like_string")
                        sensitive = True
            if inspect_boundaries and kind == "value":
                normalized = re.sub(r"[_-]+", " ", text.lower())
                for code, patterns in RULES:
                    if any(re.search(pattern, normalized, re.IGNORECASE) for pattern in patterns):
                        findings.add(f"boundary:{location}:{code}")
                if text.lower() in {"true", "approved", "authorized", "executed", "sealed", "granted", "complete", "closed", "installed", "registered", "executable"}:
                    key_context = " ".join(path).lower().replace("_", "-")
                    if any(term in key_context for term in GOVERNED_KEY_PATTERNS):
                        findings.add(f"boundary:{location}:affirmative-governed-state")
    except _MalformedGraph as exc:
        findings.add(f"malformed:{exc.code}")
    return {
        "findings": sorted(findings),
        "sensitive": sensitive,
        "m14_public_output_fields": source_fields,
        "blocked_content_classes": sorted(blocked_classes),
    }


def adapt_sensitive_record_to_public_output_gate(record: Mapping[str, Any]) -> dict[str, Any]:
    """Map Track D categories to the five structured M14 public-output classes."""
    if not isinstance(record, Mapping):
        return {
            "m14_public_output_fields": {},
            "blocked_content_classes": [],
            "findings": ["malformed:record-not-mapping"],
        }
    inspected = _inspect_record(record)
    return {
        "m14_public_output_fields": inspected["m14_public_output_fields"],
        "blocked_content_classes": inspected["blocked_content_classes"],
        "findings": inspected["findings"],
    }


def evaluate_cross_control_scenario(document: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate an inert scenario mapping without mutating it or echoing secrets."""
    findings: set[str] = set()
    if not isinstance(document, Mapping):
        return {"valid": False, "outcome": "reject", "findings": ["malformed:root-not-mapping"]}
    try:
        _validate_inert_graph(document)
        document_fields = dict(_mapping_items(document))
    except (Exception, _MalformedGraph) as exc:
        code = exc.code if isinstance(exc, _MalformedGraph) else "hostile-mapping"
        return {"valid": False, "outcome": "reject", "findings": [f"malformed:{code}"]}
    if document_fields.get("schema_version") != SCHEMA_VERSION:
        findings.add("malformed:schema-version")
    if document_fields.get("synthetic") is not True:
        findings.add("synthetic-classification-required")
    record = document_fields.get("record")
    if not isinstance(record, Mapping):
        findings.add("malformed:record-not-mapping")
        record = {}
    sensitive_inspection = _inspect_record(
        document_fields, inspect_sensitive=True, inspect_boundaries=False
    )
    boundary_inspection = _inspect_record(
        record, inspect_sensitive=False, inspect_boundaries=True
    )
    findings.update(sensitive_inspection["findings"])
    findings.update(boundary_inspection["findings"])
    ordered = sorted(findings)
    malformed = any(finding.startswith("malformed:") for finding in ordered)
    outcome = "reject" if malformed else ("quarantine" if sensitive_inspection["sensitive"] else ("reject" if ordered else "pass"))
    return {"valid": not ordered, "outcome": outcome, "findings": ordered}


def _record_claims_true(record: Mapping[str, Any], field_names: set[str]) -> bool:
    normalized_names = {name.replace("-", "_").lower() for name in field_names}
    for kind, path, text in _walk_inert(record):
        if kind != "value" or not path:
            continue
        key = path[-1].replace("-", "_").lower()
        if key in normalized_names and text.lower() in {"true", "approved", "complete", "completed", "authorized", "admitted"}:
            return True
    return False


def _record_claims_false(record: Mapping[str, Any], field_names: set[str]) -> bool:
    normalized_names = {name.replace("-", "_").lower() for name in field_names}
    for kind, path, text in _walk_inert(record):
        if kind != "value" or not path:
            continue
        key = path[-1].replace("-", "_").lower()
        if key in normalized_names and text.lower() in {"false", "removed", "waived", "not_required"}:
            return True
    return False


def evaluate_source_control_composition(
    document: Mapping[str, Any], source_control_outputs: Mapping[str, Any]
) -> dict[str, Any]:
    """Compose inert outputs produced by maintained, independently governed controls."""
    base = evaluate_cross_control_scenario(document)
    findings = set(base["findings"])
    source_results: list[dict[str, Any]] = []
    source_sensitive = base["outcome"] == "quarantine"
    if any(finding.startswith("malformed:") for finding in findings):
        return {**base, "source_control_results": source_results}
    if not isinstance(source_control_outputs, Mapping):
        findings.add("malformed:source-control-outputs-not-mapping")
        ordered = sorted(findings)
        return {
            "valid": False,
            "outcome": "reject",
            "findings": ordered,
            "source_control_results": source_results,
        }
    else:
        try:
            _validate_inert_graph(source_control_outputs)
            source_items = _mapping_items(source_control_outputs)
        except _MalformedGraph as exc:
            findings.add(f"malformed:source-control-{exc.code}")
            ordered = sorted(findings)
            return {
                "valid": False,
                "outcome": "reject",
                "findings": ordered,
                "source_control_results": source_results,
            }
    try:
        document_fields = dict(_mapping_items(document))
    except (Exception, _MalformedGraph) as exc:
        code = exc.code if isinstance(exc, _MalformedGraph) else "hostile-mapping"
        return {
            "valid": False,
            "outcome": "reject",
            "findings": [f"malformed:{code}"],
            "source_control_results": source_results,
        }
    record = document_fields.get("record")
    record = record if isinstance(record, Mapping) else {}
    source_by_id: dict[str, Any] = {}
    for control_id, output in source_items:
        if not isinstance(control_id, str):
            findings.add("malformed:source-control-id-not-string")
        elif control_id in source_by_id:
            findings.add("malformed:source-control-id-duplicate")
        else:
            source_by_id[control_id] = output
    control_ids = set(SOURCE_CONTROL_REQUIRED_FIELDS) | set(source_by_id)
    for control_id in sorted(control_ids):
        required = SOURCE_CONTROL_REQUIRED_FIELDS.get(control_id)
        control_findings: set[str] = set()
        if control_id not in source_by_id:
            control_findings.add("missing-output")
        elif required is None:
            control_findings.add("unknown-source-control")
        elif not isinstance(source_by_id[control_id], Mapping):
            control_findings.add("malformed-output")
        else:
            try:
                output = dict(_mapping_items(source_by_id[control_id]))
            except (Exception, _MalformedGraph):
                output = {}
                control_findings.add("malformed-output")
            missing = required - set(output)
            control_findings.update(f"missing-output:{field}" for field in missing)
            if not missing and control_id == "m14-public-output-exfiltration":
                if output.get("public_issue_exfiltration_gate_valid") is not True:
                    control_findings.add("source-gate-invalid")
                if output.get("public_output_blocked") is True:
                    control_findings.add("public-output-blocked")
                    source_sensitive = source_sensitive or output.get("redaction_required") is True
                elif output.get("public_output_allowed") is not True:
                    control_findings.add("public-output-decision-missing")
            elif not missing and control_id == "m14-ai-provenance":
                if output.get("ai_pr_provenance_valid") is not True or output.get("workflow_security_valid") is not True:
                    control_findings.add("source-gate-invalid")
                if output.get("human_review_required") is not True:
                    control_findings.add("human-review-boundary-weakened")
                if _record_claims_true(record, {"human_review_completed", "review_approved", "merge_approved"}):
                    control_findings.add("human-review-remains-required")
                if _record_claims_false(record, {"human_review_required", "reviewer_routing_required"}):
                    control_findings.add("human-review-required-cannot-be-removed")
            elif not missing and control_id == "m14-skill-admission":
                if output.get("candidate_admission_state") == "candidate_blocked" or output.get("ready_for_review") is not True:
                    control_findings.add("skill-admission-blocked")
                if _record_claims_true(record, {"skill_admitted", "package_admitted", "mcp_admitted", "executable_capability"}):
                    control_findings.add("admission-cannot-be-promoted")
            elif not missing and control_id == "external-evidence-admission":
                if (
                    output.get("external_evidence_admission_valid") is not True
                    or output.get("admission_result") != "verified"
                    or output.get("decision_path_eligible") is not True
                    or output.get("fail_closed") is True
                ):
                    control_findings.add("external-evidence-ineligible")
            elif not missing and control_id == "m14-cross-control-authority":
                if (
                    output.get("valid") is not True
                    or output.get("authority_violation_detected") is True
                    or output.get("effective_control_result") in {"blocked", "escalation_required"}
                ):
                    control_findings.add("authority-composition-blocked")
        for finding in control_findings:
            findings.add(f"source-control:{control_id}:{finding}")
        source_results.append(
            {
                "source_control_id": control_id,
                "accepted": not control_findings,
                "findings": sorted(control_findings),
            }
        )
    ordered = sorted(findings)
    outcome = "quarantine" if source_sensitive else ("reject" if ordered else "pass")
    return {
        "valid": not ordered,
        "outcome": outcome,
        "findings": ordered,
        "source_control_results": source_results,
    }
