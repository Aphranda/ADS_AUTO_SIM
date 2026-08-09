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


def _git_ls_files(args: list[str], patterns: list[str]) -> list[str]:
    command = ["git", "ls-files", "-z", *args, "--", *patterns]
    raw = subprocess.check_output(command, cwd=REPO_ROOT, stderr=subprocess.DEVNULL)
    return [item.decode("utf-8", errors="surrogateescape") for item in raw.split(b"\0") if item]


def _json_files_by_git_status(scope: str) -> list[tuple[str, str]]:
    patterns = ["*.json", "*.jsonl"]
    tracked = [(rel, "tracked") for rel in _git_ls_files([], patterns)]
    if scope == "tracked":
        return tracked

    seen = {rel for rel, _status in tracked}
    rows = tracked.copy()
    for rel in _git_ls_files(["-o", "--exclude-standard"], patterns):
        if rel not in seen:
            rows.append((rel, "untracked"))
            seen.add(rel)
    for rel in _git_ls_files(["-o", "-i", "--exclude-standard"], patterns):
        if rel not in seen:
            rows.append((rel, "ignored"))
            seen.add(rel)
    return sorted(rows)


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


def audit_json_artifacts(*, scope: str = "tracked", include_ok: bool = False) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    for rel, git_status in _json_files_by_git_status(scope):
        artifact_class = json_artifact_class(rel)
        parse = _parse_status(rel)
        counts[artifact_class] += 1
        counts[f"git_{git_status}"] += 1
        counts[f"parse_{parse['parse']}"] += 1
        row = {"path": rel, "git_status": git_status, "class": artifact_class, **parse}
        if (
            include_ok
            or git_status != "ignored"
            and (artifact_class.startswith("local_runtime") or artifact_class == "legacy_or_unclear_json")
            or parse["parse"] == "error"
        ):
            rows.append(row)
    return {"scope": scope, "counts": dict(sorted(counts.items())), "items": rows}


def audit_tracked_json(*, include_ok: bool = False) -> dict[str, Any]:
    """Backward-compatible entry point for tracked-only audits."""

    return audit_json_artifacts(scope="tracked", include_ok=include_ok)


def _print_markdown(payload: dict[str, Any]) -> None:
    print("# JSON Artifact Audit")
    print()
    print(f"Scope: `{payload['scope']}`")
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
        print(f"- `{item['git_status']}` `{item['class']}` `{item['path']}`{detail}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit tracked JSON artifacts against SIM naming rules.")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--scope", choices=["tracked", "all"], default="tracked")
    parser.add_argument("--include-ok", action="store_true", help="Include every tracked JSON/JSONL item, not only items needing review.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = audit_json_artifacts(scope=args.scope, include_ok=args.include_ok)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_markdown(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
