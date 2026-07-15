"""Shared fail-closed helpers for non-authoritative evaluator claims.

The helpers in this module classify only active authority claims selected by a
caller.  Historical declarations, expected-output lists, and other inert
evidence remain the caller's responsibility to exclude explicitly.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any


STRUCTURED_AUTHORITY_FIELDS = frozenset(
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
    }
)

COMMON_FORBIDDEN_AUTHORITY_KEYS = frozenset(
    {
        "authorization",
        "approval",
        "authority",
        "sealing",
        "risk",
        "rollback",
        "fail_closed",
        "audit",
        "waiver",
    }
)

EXPLICIT_NEGATIVE_AUTHORITY_STRINGS = frozenset(
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
    }
)


def authority_token(value: Any) -> str:
    """Return a stable token for authority keys and scalar string values."""

    return re.sub(r"[^a-z0-9]+", "_", str(value).strip().casefold()).strip("_")


def is_explicit_negative_authority_value(value: Any) -> bool:
    """Recognize only the intentionally supported negative authority values."""

    if value is None or value is False:
        return True
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value == 0
    if isinstance(value, str):
        return authority_token(value) in EXPLICIT_NEGATIVE_AUTHORITY_STRINGS
    return False


def _scalar_is_affirmative(value: Any) -> bool:
    if is_explicit_negative_authority_value(value):
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    return bool(value)


def _find_structured_authority_signals(
    value: Any,
    forbidden_keys: frozenset[str],
) -> tuple[bool, bool]:
    if isinstance(value, Mapping):
        saw_signal = False
        affirmative = False
        for raw_key, nested in value.items():
            key = authority_token(raw_key)
            if key in forbidden_keys or key in STRUCTURED_AUTHORITY_FIELDS:
                saw_signal = True
                if authority_value_is_affirmative(nested, forbidden_keys):
                    affirmative = True
            elif isinstance(nested, (Mapping, list, tuple)):
                child_signal, child_affirmative = _find_structured_authority_signals(
                    nested,
                    forbidden_keys,
                )
                saw_signal = saw_signal or child_signal
                affirmative = affirmative or child_affirmative
        return saw_signal, affirmative

    if isinstance(value, (list, tuple)):
        saw_signal = False
        affirmative = False
        for nested in value:
            child_signal, child_affirmative = _find_structured_authority_signals(
                nested,
                forbidden_keys,
            )
            saw_signal = saw_signal or child_signal
            affirmative = affirmative or child_affirmative
        return saw_signal, affirmative

    return False, False


def authority_value_is_affirmative(
    value: Any,
    forbidden_keys: frozenset[str],
) -> bool:
    """Classify a value attached to a forbidden authority key.

    Unknown non-empty values are affirmative.  A structured negative outer
    value remains negative only when every authority-bearing nested signal is
    also explicitly negative.
    """

    if isinstance(value, Mapping):
        saw_signal, affirmative = _find_structured_authority_signals(
            value,
            forbidden_keys,
        )
        if affirmative:
            return True
        if saw_signal:
            return False
        return bool(value)

    if isinstance(value, (list, tuple)):
        if not value:
            return False
        for nested in value:
            if isinstance(nested, (Mapping, list, tuple)):
                saw_signal, affirmative = _find_structured_authority_signals(
                    nested,
                    forbidden_keys,
                )
                if affirmative:
                    return True
                if not saw_signal and bool(nested):
                    return True
            elif _scalar_is_affirmative(nested):
                return True
        return False

    return _scalar_is_affirmative(value)


def scan_forbidden_authority_claims(
    value: Any,
    *,
    forbidden_keys: Sequence[str],
    forbidden_tokens: Sequence[str] = (),
    skip_keys: Sequence[str] = (),
    path: tuple[str, ...] = (),
) -> list[str]:
    """Return deterministic paths containing affirmative authority claims."""

    normalized_forbidden_keys = frozenset(
        COMMON_FORBIDDEN_AUTHORITY_KEYS
        | {authority_token(item) for item in forbidden_keys}
    )
    normalized_forbidden_tokens = frozenset(
        authority_token(item) for item in forbidden_tokens
    )
    normalized_skip_keys = frozenset(authority_token(item) for item in skip_keys)
    findings: list[str] = []

    def scan(nested_value: Any, current_path: tuple[str, ...]) -> None:
        if isinstance(nested_value, Mapping):
            for raw_key, child in nested_value.items():
                key = str(raw_key)
                key_token = authority_token(key)
                if key_token in normalized_skip_keys:
                    continue
                child_path = current_path + (key,)
                if key_token in normalized_forbidden_keys:
                    if authority_value_is_affirmative(
                        child,
                        normalized_forbidden_keys,
                    ):
                        findings.append(
                            "affirmative_forbidden_claim:" + ".".join(child_path)
                        )
                    if isinstance(child, (Mapping, list, tuple)):
                        scan(child, child_path)
                    continue
                if isinstance(child, (Mapping, list, tuple)):
                    scan(child, child_path)
                elif (
                    isinstance(child, str)
                    and authority_token(child) in normalized_forbidden_tokens
                ):
                    findings.append(
                        "forbidden_output_token_used_as_value:"
                        + ".".join(child_path)
                    )
            return

        if isinstance(nested_value, (list, tuple)):
            for index, child in enumerate(nested_value):
                scan(child, current_path + (str(index),))
            return

        if (
            isinstance(nested_value, str)
            and authority_token(nested_value) in normalized_forbidden_tokens
        ):
            findings.append(
                "forbidden_output_token_used_as_value:" + ".".join(current_path)
            )

    scan(value, path)
    return list(dict.fromkeys(findings))
