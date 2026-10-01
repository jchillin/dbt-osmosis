"""Bounded-memory reading and validation of large JSON files.

``json.load`` builds the whole document in memory, which for a 100MB+ dbt
manifest costs several times the file size. ``validate_json_file`` checks the
same thing while holding only one chunk of text and one inner value at a time.
``read_first_member`` decodes the leading member of an object, such as a
manifest's ``metadata``, and stops reading where that value ends.
"""

from __future__ import annotations

import json
import re
import typing as t
from pathlib import Path

__all__ = ["read_first_member", "validate_json_file"]

_DEFAULT_CHUNK_CHARS = 1024 * 1024
# Containers in the two outermost levels are walked piece by piece. Anything
# deeper, such as one node in a dbt manifest, is decoded whole by json.
_WALK_DEPTH = 2
_CONTAINER_CLOSERS = {"{": "}", "[": "]"}
_NON_WHITESPACE_RE = re.compile(r"[^ \t\n\r]")
_NUMBER_START_CHARS = frozenset("-0123456789")
_NUMBER_CHARS_RE = re.compile(r"[-+.eE0-9]*")
_DECODER = json.JSONDecoder()


@t.final
class _ChunkedJsonReader:
    """Read JSON text from a file in chunks, keeping only the unconsumed tail."""

    def __init__(self, file: t.TextIO, chunk_chars: int) -> None:
        self._file = file
        self._chunk_chars = chunk_chars
        self._buffer = ""
        self._pos = 0
        self._at_eof = False

    def _read_more(self, min_chars: int = 0) -> None:
        self._buffer = self._buffer[self._pos :]
        self._pos = 0
        chunk = self._file.read(max(min_chars, self._chunk_chars))
        if chunk:
            self._buffer += chunk
        else:
            self._at_eof = True

    def peek(self) -> str:
        """Skip whitespace and return the next character, or "" at the end of the file."""
        while True:
            token = _NON_WHITESPACE_RE.search(self._buffer, self._pos)
            if token is not None:
                self._pos = token.start()
                return token.group()
            self._pos = len(self._buffer)
            if self._at_eof:
                return ""
            self._read_more()

    def take(self, char: str) -> bool:
        """Consume ``char`` if it is the next character."""
        if self.peek() != char:
            return False
        self._pos += 1
        return True

    def expect(self, char: str) -> None:
        """Consume ``char`` as the next character, or raise ValueError."""
        if not self.take(char):
            raise ValueError(f"Expected {char!r} but found {self.peek() or 'end of file'!r}")

    def _read_past_number(self) -> None:
        # Unlike strings, containers, and literals, a cut-off number still
        # decodes, as its valid prefix, so read past its last character first.
        while not self._at_eof and _NUMBER_CHARS_RE.fullmatch(self._buffer, self._pos):
            self._read_more(len(self._buffer))

    def decode_value(self) -> object:
        """Decode the next complete JSON value, reading more text until it fits."""
        if self.peek() in _NUMBER_START_CHARS:
            self._read_past_number()
        while True:
            try:
                decoded = _DECODER.raw_decode(self._buffer, self._pos)
                break
            except json.JSONDecodeError:
                if self._at_eof:
                    raise
                self._read_more(len(self._buffer))
        value, self._pos = t.cast("tuple[object, int]", decoded)
        return value


def _skip_key(reader: _ChunkedJsonReader) -> None:
    if reader.peek() != '"':
        raise ValueError("Expected a string object key")
    _ = reader.decode_value()
    reader.expect(":")


def _skip_value(reader: _ChunkedJsonReader, depth: int) -> None:
    opener = reader.peek()
    if depth == 0 or opener not in _CONTAINER_CLOSERS:
        _ = reader.decode_value()
        return

    closer = _CONTAINER_CLOSERS[opener]
    reader.expect(opener)
    if reader.take(closer):
        return
    while True:
        if opener == "{":
            _skip_key(reader)
        _skip_value(reader, depth - 1)
        if reader.take(closer):
            return
        reader.expect(",")


def validate_json_file(path: Path | str, *, chunk_chars: int = _DEFAULT_CHUNK_CHARS) -> None:
    """Check that a file holds exactly one complete JSON value, without loading it whole.

    Accepts the same documents as ``json.load``. Memory stays around one chunk
    plus the largest value two levels down, such as one node in a dbt manifest.
    A file that is malformed partway through can grow that value, and the
    buffer, to the rest of the file before the error surfaces.

    Args:
        path: The file to check.
        chunk_chars: How many characters to read at a time.

    Raises:
        OSError: If the file can't be read.
        ValueError: If the file isn't UTF-8 or isn't one complete JSON value.
    """
    with open(path, encoding="utf-8") as f:
        reader = _ChunkedJsonReader(f, chunk_chars)
        _skip_value(reader, _WALK_DEPTH)
        if reader.peek():
            raise ValueError("Extra data after the JSON value")


def read_first_member(
    path: Path | str, key: str, *, chunk_chars: int = _DEFAULT_CHUNK_CHARS
) -> object:
    """Decode the value of ``key`` when it is the first member of the top-level object.

    Reading stops where that value ends, so the rest of the file is neither
    read nor checked. Memory stays around one chunk plus the value. A value
    that is malformed partway through can grow the buffer to the rest of the
    file before the error surfaces.

    Args:
        path: The file to read.
        key: The key the first member must have.
        chunk_chars: How many characters to read at a time.

    Returns:
        The decoded value, or None if the file doesn't hold an object whose first key is ``key``.

    Raises:
        OSError: If the file can't be read.
        ValueError: If the file isn't UTF-8, or the first member is cut off or invalid JSON.
    """
    with open(path, encoding="utf-8") as f:
        reader = _ChunkedJsonReader(f, chunk_chars)
        if not reader.take("{") or reader.peek() != '"':
            return None
        if reader.decode_value() != key:
            return None
        reader.expect(":")
        return reader.decode_value()
