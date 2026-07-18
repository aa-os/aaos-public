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


def _path_text(path: tuple[str, ...]) -> str:
    return ".".join(path) if path else "$"


def _walk_inert(root: Any):
    """Yield scalar/key text without recursion or dereferencing external state."""
    stack = [(root, (), 0)]
    seen: set[int] = set()
    containers = 0
    while stack:
        value, path, depth = stack.pop()
        if isinstance(value, (Mapping, list, tuple)):
            identity = id(value)
            if identity in seen:
                continue
            seen.add(identity)
            containers += 1
            if containers > MAX_CONTAINERS:
                raise ValueError("container limit exceeded")
            if depth > MAX_NESTING_DEPTH:
                raise ValueError("nesting limit exceeded")
        if isinstance(value, Mapping):
            items = []
            try:
                items = list(value.items())
            except Exception as exc:
                raise ValueError("hostile mapping") from exc
            for key, child in reversed(items):
                key_text = key if isinstance(key, str) else f"<{type(key).__name__}>"
                yield "key", path + (key_text,), key_text
                stack.append((child, path + (key_text,), depth + 1))
        elif isinstance(value, (list, tuple)):
            for index in range(len(value) - 1, -1, -1):
                stack.append((value[index], path + (str(index),), depth + 1))
        elif isinstance(value, (str, int, float, bool)) or value is None:
            yield "value", path, str(value)
        else:
            yield "value", path, f"<{type(value).__name__}>"


def evaluate_cross_control_scenario(document: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate an inert scenario mapping without mutating it or echoing secrets."""
    findings: set[str] = set()
    if not isinstance(document, Mapping):
        return {"valid": False, "outcome": "reject", "findings": ["malformed:root-not-mapping"]}
    if document.get("schema_version") != SCHEMA_VERSION:
        findings.add("malformed:schema-version")
    if document.get("synthetic") is not True:
        findings.add("synthetic-classification-required")
    record = document.get("record")
    if not isinstance(record, Mapping):
        findings.add("malformed:record-not-mapping")
        record = {}
    sensitive = False
    try:
        for kind, path, text in _walk_inert(record):
            location = _path_text(path)
            if kind == "key" and SENSITIVE_KEYS.search(text):
                findings.add(f"sensitive:{location}:sensitive-key")
                sensitive = True
            if kind == "value":
                for category, pattern in SENSITIVE_VALUES:
                    if pattern.search(text):
                        findings.add(f"sensitive:{location}:{category}")
                        sensitive = True
                normalized = re.sub(r"[_-]+", " ", text.lower())
                for code, patterns in RULES:
                    if any(re.search(pattern, normalized, re.IGNORECASE) for pattern in patterns):
                        findings.add(f"boundary:{location}:{code}")
                if text.lower() in {"true", "approved", "authorized", "executed", "sealed", "granted", "complete", "closed", "installed", "registered", "executable"}:
                    key_context = " ".join(path).lower().replace("_", "-")
                    if any(term in key_context for term in GOVERNED_KEY_PATTERNS):
                        findings.add(f"boundary:{location}:affirmative-governed-state")
    except Exception:
        findings.add("malformed:hostile-or-over-complex-input")
    ordered = sorted(findings)
    outcome = "quarantine" if sensitive else ("reject" if ordered else "pass")
    return {"valid": not ordered, "outcome": outcome, "findings": ordered}
