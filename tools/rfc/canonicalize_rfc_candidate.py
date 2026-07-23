#!/usr/bin/env python3
"""Canonicalize JSON using RFC 8785 (JCS) and optionally hash the result.

This module is deliberately limited to the Python standard library.  JSON text
is parsed as I-JSON: duplicate object names, non-finite binary64 numbers, and
lone Unicode surrogates are rejected.  Number parsing uses IEEE 754 binary64
semantics, and serialization implements the ECMAScript shortest-round-trip
rules required by RFC 8785.

Examples:

    python tools/rfc/canonicalize_rfc_candidate.py input.json
    python tools/rfc/canonicalize_rfc_candidate.py input.json -o canonical.json
    python tools/rfc/canonicalize_rfc_candidate.py input.json --sha256
    python tools/rfc/canonicalize_rfc_candidate.py input.json \
        -o canonical.json --sha256
"""

import argparse
import hashlib
import json
import math
import struct
import sys
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union


class CanonicalizationError(ValueError):
    """Raised when input cannot be represented as RFC 8785 canonical JSON."""


class DuplicatePropertyError(CanonicalizationError):
    """Raised when parsed JSON contains duplicate object property names."""


_MAX_FINITE_BINARY64_BITS = 0x7FEFFFFFFFFFFFFF
_CONTROL_ESCAPES = {
    0x08: "\\b",
    0x09: "\\t",
    0x0A: "\\n",
    0x0C: "\\f",
    0x0D: "\\r",
}


def _validate_unicode(value: str) -> None:
    """Reject lone UTF-16 surrogate code points as required by RFC 8785."""

    for character in value:
        code_point = ord(character)
        if 0xD800 <= code_point <= 0xDFFF:
            raise CanonicalizationError(
                "JSON strings must not contain lone Unicode surrogates"
            )


def _quote_string(value: str) -> str:
    """Apply the ECMAScript JSON string escaping used by RFC 8785."""

    _validate_unicode(value)
    output = ['"']
    for character in value:
        code_point = ord(character)
        if character == '"':
            output.append('\\"')
        elif character == "\\":
            output.append("\\\\")
        elif code_point <= 0x1F:
            output.append(
                _CONTROL_ESCAPES.get(code_point, "\\u{:04x}".format(code_point))
            )
        else:
            output.append(character)
    output.append('"')
    return "".join(output)


def _utf16_sort_key(value: str) -> bytes:
    """Return the unsigned UTF-16 code-unit sequence used for JCS sorting."""

    _validate_unicode(value)
    return value.encode("utf-16-be")


def _float_from_bits(bits: int) -> float:
    return struct.unpack(">d", struct.pack(">Q", bits))[0]


def _fraction_from_float(value: float) -> Fraction:
    numerator, denominator = value.as_integer_ratio()
    return Fraction(numerator, denominator)


def _rounding_interval(value: float) -> Tuple[Fraction, Fraction, bool]:
    """Return binary64's decimal-input interval and endpoint inclusivity.

    IEEE 754 round-to-nearest, ties-to-even maps every decimal value inside
    this interval back to ``value``.  Both midpoint endpoints select ``value``
    exactly when its significand is even.
    """

    bits = struct.unpack(">Q", struct.pack(">d", value))[0]
    exact = _fraction_from_float(value)

    previous = _fraction_from_float(_float_from_bits(bits - 1))
    lower = (exact + previous) / 2

    if bits == _MAX_FINITE_BINARY64_BITS:
        # The overflow boundary is half of one final-binade ULP above the
        # maximum finite value.  That ULP equals the preceding spacing.
        upper = exact + (exact - previous) / 2
    else:
        following = _fraction_from_float(_float_from_bits(bits + 1))
        upper = (exact + following) / 2

    return lower, upper, (bits & 1) == 0


def _ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def _decimal_scale(power: int) -> Fraction:
    if power >= 0:
        return Fraction(10**power, 1)
    return Fraction(1, 10 ** (-power))


def _coefficient_bounds(
    lower: Fraction,
    upper: Fraction,
    scale: Fraction,
    endpoints_inclusive: bool,
) -> Tuple[int, int]:
    scaled_lower = lower / scale
    scaled_upper = upper / scale

    minimum = _ceil_fraction(scaled_lower)
    if not endpoints_inclusive and Fraction(minimum, 1) == scaled_lower:
        minimum += 1

    maximum = scaled_upper.numerator // scaled_upper.denominator
    if not endpoints_inclusive and Fraction(maximum, 1) == scaled_upper:
        maximum -= 1

    return minimum, maximum


def _nearest_coefficients(
    target: Fraction, minimum: int, maximum: int
) -> Iterable[int]:
    """Yield the interval edges and integers nearest to ``target``."""

    floor_target = target.numerator // target.denominator
    candidates = {
        minimum,
        maximum,
        floor_target - 1,
        floor_target,
        floor_target + 1,
        floor_target + 2,
    }
    for candidate in sorted(candidates):
        if minimum <= candidate <= maximum and candidate % 10:
            yield candidate


def _shortest_decimal(value: float) -> Tuple[str, int]:
    """Return ECMAScript's shortest coefficient digits and decimal position.

    The result is ``(digits, n)`` where the represented mathematical value is
    ``int(digits) * 10 ** (n - len(digits))``.  Candidate coefficients are
    selected exactly with :class:`fractions.Fraction`; ties choose an even
    coefficient, matching ECMA-262 Number::toString Note 2.
    """

    exact = _fraction_from_float(value)
    lower, upper, endpoints_inclusive = _rounding_interval(value)
    decimal_position = Decimal.from_float(value).adjusted() + 1

    # Every binary64 value has a round-tripping representation containing no
    # more than 17 significant decimal digits.
    for digit_count in range(1, 18):
        candidates: List[Tuple[Fraction, int, int]] = []
        minimum_digits = 1 if digit_count == 1 else 10 ** (digit_count - 1)
        maximum_digits = 10**digit_count - 1

        # A rounding interval can straddle a power of ten, so inspect the
        # neighboring decimal positions as well as the position of the value.
        for position in range(decimal_position - 1, decimal_position + 2):
            scale = _decimal_scale(position - digit_count)
            minimum, maximum = _coefficient_bounds(
                lower, upper, scale, endpoints_inclusive
            )
            minimum = max(minimum, minimum_digits)
            maximum = min(maximum, maximum_digits)
            if minimum > maximum:
                continue

            target = exact / scale
            for coefficient in _nearest_coefficients(target, minimum, maximum):
                represented = coefficient * scale
                candidates.append(
                    (abs(represented - exact), coefficient, position)
                )

        if candidates:
            # Note 2 selects the closest value, then the even coefficient.
            # Remaining fields only make equivalent edge cases deterministic.
            _, coefficient, position = min(
                candidates,
                key=lambda item: (
                    item[0],
                    item[1] & 1,
                    item[1],
                    item[2],
                ),
            )
            return str(coefficient), position

    raise CanonicalizationError(
        "failed to create a shortest IEEE 754 binary64 decimal representation"
    )


def _serialize_number(value: float) -> str:
    if not math.isfinite(value):
        raise CanonicalizationError("NaN and Infinity are not valid I-JSON numbers")
    if value == 0:
        return "0"

    sign = ""
    if value < 0:
        sign = "-"
        value = -value

    digits, position = _shortest_decimal(value)
    digit_count = len(digits)

    if digit_count <= position <= 21:
        rendered = digits + ("0" * (position - digit_count))
    elif 0 < position <= 21:
        rendered = digits[:position] + "." + digits[position:]
    elif -6 < position <= 0:
        rendered = "0." + ("0" * (-position)) + digits
    else:
        exponent = position - 1
        mantissa = digits
        if digit_count > 1:
            mantissa = digits[0] + "." + digits[1:]
        exponent_sign = "+" if exponent >= 0 else "-"
        rendered = "{}e{}{}".format(mantissa, exponent_sign, abs(exponent))

    return sign + rendered


def _serialize(value: Any, output: List[str], active_containers: set) -> None:
    if value is None:
        output.append("null")
    elif value is True:
        output.append("true")
    elif value is False:
        output.append("false")
    elif isinstance(value, str):
        output.append(_quote_string(value))
    elif isinstance(value, float):
        output.append(_serialize_number(value))
    elif isinstance(value, int):
        try:
            binary64 = float(value)
        except OverflowError as error:
            raise CanonicalizationError(
                "integer is outside the finite IEEE 754 binary64 range"
            ) from error
        if not math.isfinite(binary64) or int(binary64) != value:
            raise CanonicalizationError(
                "programmatic integer is not exactly representable as binary64"
            )
        output.append(_serialize_number(binary64))
    elif isinstance(value, list):
        identity = id(value)
        if identity in active_containers:
            raise CanonicalizationError("cyclic JSON arrays are not supported")
        active_containers.add(identity)
        try:
            output.append("[")
            for index, item in enumerate(value):
                if index:
                    output.append(",")
                _serialize(item, output, active_containers)
            output.append("]")
        finally:
            active_containers.remove(identity)
    elif isinstance(value, dict):
        identity = id(value)
        if identity in active_containers:
            raise CanonicalizationError("cyclic JSON objects are not supported")
        active_containers.add(identity)
        try:
            for key in value:
                if not isinstance(key, str):
                    raise CanonicalizationError(
                        "JSON object property names must be strings"
                    )
                _validate_unicode(key)

            output.append("{")
            for index, key in enumerate(sorted(value, key=_utf16_sort_key)):
                if index:
                    output.append(",")
                output.append(_quote_string(key))
                output.append(":")
                _serialize(value[key], output, active_containers)
            output.append("}")
        finally:
            active_containers.remove(identity)
    else:
        raise CanonicalizationError(
            "unsupported JSON value type: {}".format(type(value).__name__)
        )


def canonicalize(value: Any) -> bytes:
    """Return RFC 8785 canonical JSON as deterministic UTF-8 bytes."""

    output: List[str] = []
    try:
        _serialize(value, output, set())
    except RecursionError as error:
        raise CanonicalizationError("JSON nesting is too deep") from error
    return "".join(output).encode("utf-8")


def _reject_constant(token: str) -> None:
    raise CanonicalizationError(
        "{} is not a finite I-JSON number".format(token)
    )


def _object_from_pairs(pairs: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        _validate_unicode(key)
        if key in result:
            raise DuplicatePropertyError(
                "duplicate JSON object property: {!r}".format(key)
            )
        result[key] = value
    return result


def loads_i_json(document: Union[str, bytes, bytearray]) -> Any:
    """Parse JSON with the I-JSON constraints needed by RFC 8785.

    All JSON number tokens are converted to IEEE 754 binary64 values, matching
    ECMAScript JSON parsing before canonical serialization.
    """

    if isinstance(document, (bytes, bytearray)):
        try:
            text = bytes(document).decode("utf-8")
        except UnicodeDecodeError as error:
            raise CanonicalizationError("input is not valid UTF-8") from error
    elif isinstance(document, str):
        text = document
    else:
        raise TypeError("document must be str, bytes, or bytearray")

    try:
        value = json.loads(
            text,
            object_pairs_hook=_object_from_pairs,
            parse_float=float,
            parse_int=float,
            parse_constant=_reject_constant,
        )
    except CanonicalizationError:
        raise
    except (json.JSONDecodeError, ValueError, OverflowError) as error:
        raise CanonicalizationError("invalid JSON: {}".format(error)) from error

    # String values and number ranges are checked recursively by canonicalize.
    return value


def canonicalize_json(document: Union[str, bytes, bytearray]) -> bytes:
    """Parse JSON text and return RFC 8785 canonical UTF-8 bytes."""

    return canonicalize(loads_i_json(document))


def sha256_hex(canonical_bytes: bytes) -> str:
    """Return the lowercase SHA-256 digest of canonical bytes."""

    return hashlib.sha256(canonical_bytes).hexdigest()


def canonical_sha256(document: Union[str, bytes, bytearray]) -> str:
    """Parse, canonicalize, and SHA-256 hash a JSON document."""

    return sha256_hex(canonicalize_json(document))


def _read_input(path: str) -> bytes:
    if path == "-":
        return sys.stdin.buffer.read()
    return Path(path).read_bytes()


def _write_output(path: str, content: bytes) -> None:
    if path == "-":
        sys.stdout.buffer.write(content)
        return
    Path(path).write_bytes(content)


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Canonicalize an I-JSON document with RFC 8785 (JCS), or print "
            "the SHA-256 digest of its canonical bytes."
        )
    )
    parser.add_argument("input", help="input JSON path, or - for standard input")
    parser.add_argument(
        "-o",
        "--output",
        help=(
            "write canonical UTF-8 bytes to this path; - means standard output"
        ),
    )
    parser.add_argument(
        "--sha256",
        action="store_true",
        help="print the canonical bytes' lowercase SHA-256 digest",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_argument_parser()
    arguments = parser.parse_args(argv)

    if arguments.sha256 and arguments.output == "-":
        parser.error("--sha256 cannot be combined with --output -")

    try:
        canonical_bytes = canonicalize_json(_read_input(arguments.input))
        if arguments.output is not None:
            _write_output(arguments.output, canonical_bytes)
        elif not arguments.sha256:
            _write_output("-", canonical_bytes)

        if arguments.sha256:
            sys.stdout.write(sha256_hex(canonical_bytes) + "\n")
    except (CanonicalizationError, OSError) as error:
        parser.exit(1, "error: {}\n".format(error))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
