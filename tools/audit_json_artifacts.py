#!/usr/bin/env python3
"""Audit tracked JSON/JSONL artifacts against SIM naming rules."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from simads.hfss.artifact_names import json_artifact_class


def _git_ls_files(patterns: list[str]) -> list[str]:
    command = ["git", "ls-files", "-z", *patterns]
    raw = subprocess.check_output(command, cwd=REPO_ROOT)
    return [item.decode("utf-8", errors="surrogateescape") for item in raw.split(b"\0") if item]


def _parse_status(rel: str) -> dict[str, Any]:
    path = REPO_ROOT / rel
    if path.suffix.lower() != ".json":
        return {"parse": "not_json"}
    try:
        with path.open("r", encoding="utf-8-sig") as fp:
            json.load(fp)
    except Exception as exc:
        return {"parse": "error", "error_type": type(exc).__name__, "error": str(exc)}
    return {"parse": "ok"}


def audit_tracked_json(*, include_ok: bool = False) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    for rel in _git_ls_files(["*.json", "*.jsonl"]):
        artifact_class = json_artifact_class(rel)
        parse = _parse_status(rel)
        counts[artifact_class] += 1
        counts[f"parse_{parse['parse']}"] += 1
        row = {"path": rel, "class": artifact_class, **parse}
        if include_ok or artifact_class.startswith("local_runtime") or artifact_class == "legacy_or_unclear_json" or parse["parse"] == "error":
            rows.append(row)
    return {"counts": dict(sorted(counts.items())), "items": rows}


def _print_markdown(payload: dict[str, Any]) -> None:
    print("# JSON Artifact Audit")
    print()
    print("## Counts")
    print()
    for key, value in payload["counts"].items():
        print(f"- `{key}`: {value}")
    print()
    print("## Items")
    print()
    for item in payload["items"]:
        detail = ""
        if item.get("parse") == "error":
            detail = f" ({item.get('error_type')}: {item.get('error')})"
        print(f"- `{item['class']}` `{item['path']}`{detail}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit tracked JSON artifacts against SIM naming rules.")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--include-ok", action="store_true", help="Include every tracked JSON/JSONL item, not only items needing review.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = audit_tracked_json(include_ok=args.include_ok)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_markdown(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
