"""Small JSON I/O helpers shared by CLI wrappers and package modules."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def json_default(value: Any) -> str:
    """Return a stable JSON fallback for API wrapper objects and Paths."""

    return str(value)


def read_json_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def write_json(path: Path, payload: Any, *, ensure_ascii: bool = False) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=ensure_ascii, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    return path


__all__ = ["json_default", "read_json_object", "write_json"]
