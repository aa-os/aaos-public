"""Deterministic SHA-256 hashing for repository-controlled artifacts.

Repository text is decoded strictly as UTF-8 and canonicalized only from
checkout CRLF line endings to Git-style LF line endings.  Binary artifacts are
hashed byte-for-byte.  Callers must choose the mode explicitly.

This module only reads regular files beneath a supplied repository root.  It
does not locate repositories from the process working directory, access the
network, import artifacts, or execute artifact content.
"""

from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath
from typing import Literal


DigestMode = Literal["text", "binary"]


class RepositoryArtifactPathError(ValueError):
    """Raised when a repository artifact path is not safely repository-relative."""


class RepositoryArtifactTextError(ValueError):
    """Raised when UTF-8 repository text has unsupported line endings."""


class RepositoryArtifactFileTypeError(OSError):
    """Raised when an artifact path does not resolve to a regular file."""


def _path_is_link_like(path: Path) -> bool:
    """Return whether a lexical path component can substitute another target."""

    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction and is_junction())


def canonicalize_utf8_repository_text(raw: bytes) -> bytes:
    """Return the canonical bytes for repository-controlled UTF-8 text.

    Strict UTF-8 decoding rejects malformed input.  CRLF is converted to LF,
    and any remaining carriage return is rejected.  No other transformation
    is performed.
    """

    if not isinstance(raw, bytes):
        raise TypeError("repository text must be bytes")

    text = raw.decode("utf-8", errors="strict")
    canonical_text = text.replace("\r\n", "\n")
    if "\r" in canonical_text:
        raise RepositoryArtifactTextError(
            "repository text contains a lone carriage return"
        )
    return canonical_text.encode("utf-8")


def _resolve_repository_file(
    repository_root: str | Path,
    relative_path: str,
) -> Path:
    if not isinstance(relative_path, str):
        raise TypeError("repository artifact path must be a string")
    if not relative_path or not relative_path.strip():
        raise RepositoryArtifactPathError("repository artifact path must not be empty")
    if "\x00" in relative_path:
        raise RepositoryArtifactPathError(
            "repository artifact path must not contain NUL"
        )
    if "\\" in relative_path:
        raise RepositoryArtifactPathError(
            "repository artifact path must use POSIX separators"
        )
    if ":" in relative_path:
        raise RepositoryArtifactPathError(
            "repository artifact path must not contain drive or stream syntax"
        )

    # Inspect lexical segments before PurePosixPath can collapse dot or empty
    # segments.  Exact path binding must not accept a normalized substitute.
    segments = relative_path.split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        raise RepositoryArtifactPathError(
            "repository artifact path contains an unsafe segment"
        )
    if any(segment.endswith((" ", ".")) for segment in segments):
        raise RepositoryArtifactPathError(
            "repository artifact path contains a platform-aliased segment"
        )

    pure_path = PurePosixPath(relative_path)
    if pure_path.is_absolute():
        raise RepositoryArtifactPathError(
            "repository artifact path must be repository-relative"
        )

    root = Path(repository_root)
    if not root.is_absolute():
        raise RepositoryArtifactPathError("repository root must be absolute")
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise RepositoryArtifactFileTypeError(
            "repository root does not resolve to a directory"
        )

    unresolved_candidate = root
    for segment in segments:
        parent = unresolved_candidate
        unresolved_candidate = parent / segment
        try:
            exact_names = {entry.name for entry in parent.iterdir()}
        except OSError as error:
            raise RepositoryArtifactPathError(
                "repository artifact parent is not a readable directory"
            ) from error
        if segment not in exact_names:
            # A case-insensitive or Unicode-normalizing filesystem may still
            # resolve this spelling.  That is an alias, not the exact bound
            # repository-relative path.
            try:
                unresolved_candidate.lstat()
            except FileNotFoundError as error:
                raise FileNotFoundError(
                    f"repository artifact does not exist: {relative_path}"
                ) from error
            raise RepositoryArtifactPathError(
                "repository artifact path spelling does not match exactly"
            )
        try:
            unresolved_candidate.lstat()
        except FileNotFoundError as error:
            raise FileNotFoundError(
                f"repository artifact does not exist: {relative_path}"
            ) from error
        if _path_is_link_like(unresolved_candidate):
            raise RepositoryArtifactPathError(
                "repository artifact path must not traverse a link or junction"
            )

    try:
        candidate = unresolved_candidate.resolve(strict=True)
    except FileNotFoundError as error:
        raise FileNotFoundError(
            f"repository artifact does not exist: {relative_path}"
        ) from error

    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise RepositoryArtifactPathError(
            "repository artifact path resolves outside the repository root"
        ) from error

    if not candidate.is_file():
        raise RepositoryArtifactFileTypeError(
            f"repository artifact is not a regular file: {relative_path}"
        )
    return candidate


def sha256_repository_file(
    repository_root: str | Path,
    relative_path: str,
    *,
    mode: DigestMode,
) -> str:
    """Return a SHA-256 digest for one safely bound repository artifact.

    ``mode`` is deliberately keyword-only and has no default.  Text mode uses
    :func:`canonicalize_utf8_repository_text`; binary mode hashes exact bytes.
    """

    if mode not in {"text", "binary"}:
        raise ValueError("mode must be exactly 'text' or 'binary'")

    path = _resolve_repository_file(repository_root, relative_path)
    raw = path.read_bytes()
    digest_input = (
        canonicalize_utf8_repository_text(raw) if mode == "text" else raw
    )
    return hashlib.sha256(digest_input).hexdigest()


__all__ = [
    "DigestMode",
    "RepositoryArtifactFileTypeError",
    "RepositoryArtifactPathError",
    "RepositoryArtifactTextError",
    "canonicalize_utf8_repository_text",
    "sha256_repository_file",
]
