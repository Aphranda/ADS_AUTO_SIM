from __future__ import annotations

from pathlib import Path

import pytest

from simads.common import json_default, read_json_object, write_json


def test_write_and_read_json_object_uses_utf8(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "payload.json"
    write_json(path, {"name": "测试", "path": Path("demo")})

    assert read_json_object(path) == {"name": "测试", "path": "demo"}


def test_read_json_object_rejects_non_object(tmp_path: Path) -> None:
    path = tmp_path / "array.json"
    path.write_text("[1, 2, 3]\n", encoding="utf-8")

    with pytest.raises(ValueError, match="JSON root must be an object"):
        read_json_object(path)


def test_json_default_stringifies_unknown_values() -> None:
    assert json_default(Path("a/b")) in {"a\\b", "a/b"}
