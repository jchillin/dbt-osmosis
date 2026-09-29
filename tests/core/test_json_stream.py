import json

import pytest

from dbt_osmosis.core.json_stream import validate_json_file

_VALID_DOCUMENTS = [
    "{}",
    "[]",
    '"just a string"',
    "123",
    "-0.5e-3",
    "true",
    "null",
    '{"a": 1}',
    '{"a": {"b": [1, 2.5e3, -0, true, false, null]}, "c": "x\\u00e9\\"y\\\\"}',
    ' \n {"a" : { "b" : 1 } ,\t"c" : [ ] , "d" : { } }\r\n ',
    '[{"a": [1, {"b": null}]}, "s", []]',
    '{"a": {"b": {"c": {"d": [1, {"e": "deep"}]}}}}',
    '{"é": "ü", "emoji": "\\ud83d\\ude00"}',
    '{"a": 12345678901234567890, "b": 1.0000001}',
    '{"a": 1.5e-3, "b": -0.25, "c": 10E+2, "d": 0}',
    "[1.5e3, -2, 0.0]",
    '{"dup": 1, "dup": 2}',
]

_INVALID_DOCUMENTS = [
    "",
    "   ",
    "{",
    '{"a"',
    '{"a":',
    '{"a": 1',
    '{"a": 1,}',
    '{"a": 1} x',
    '{"a": 1}{}',
    "[1, 2",
    "[1,]",
    "[,1]",
    '{"a": tru}',
    '{"a": nul',
    '{"a": "unterminated}',
    "{1: 2}",
    '{"a" 1}',
    '{"a": 1 "b": 2}',
    '{"a": {"b": 1}',
    '{"a": [1, 2}',
    '{"a": "\\x"}',
    '{"a": -}',
    '{"a": 01}',
    '{"a": 1.5e}',
    '{"a": 1.}',
    "[1.5e3, -]",
    "1.5e",
    '{"a": {"b": {"c": [1, 2}}}',
    "\ufeff{}",
]

_CHUNK_SIZES = [1, 2, 3, 5, 8, 1024 * 1024]


def _write(tmp_path, text: str):
    path = tmp_path / "doc.json"
    path.write_text(text, encoding="utf-8")
    return path


@pytest.mark.parametrize("text", _VALID_DOCUMENTS)
def test_accepts_what_json_loads_accepts(tmp_path, text):
    """Every document json.loads accepts validates at any chunk size."""
    json.loads(text)
    path = _write(tmp_path, text)
    for chunk_chars in _CHUNK_SIZES:
        validate_json_file(path, chunk_chars=chunk_chars)


@pytest.mark.parametrize("text", _INVALID_DOCUMENTS)
def test_rejects_what_json_loads_rejects(tmp_path, text):
    """Every document json.loads rejects raises ValueError at any chunk size."""
    with pytest.raises(ValueError):
        json.loads(text)
    path = _write(tmp_path, text)
    for chunk_chars in _CHUNK_SIZES:
        with pytest.raises(ValueError):
            validate_json_file(path, chunk_chars=chunk_chars)


def test_rejects_invalid_utf8(tmp_path):
    """Bytes that aren't UTF-8 raise ValueError."""
    path = tmp_path / "doc.json"
    path.write_bytes(b'{"a": "\xff"}')
    with pytest.raises(ValueError):
        validate_json_file(path)


def test_missing_file_raises_oserror(tmp_path):
    """A missing file raises OSError rather than reporting invalid JSON."""
    with pytest.raises(OSError):
        validate_json_file(tmp_path / "missing.json")
