#!/usr/bin/env python3
"""Validate HFSS tool script classification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = Path(__file__).with_name("script_classes.json")
ALLOWED_CLASSES = {"production", "diagnostic", "probe", "maintenance", "legacy_text_unsafe"}
PROBE_PREFIXES = ("probe_", "try_", "scan_")


def _script_key(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def load_registry(path: Path = REGISTRY) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_registry(registry: dict[str, Any], *, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    scripts_dir = repo_root / "tools" / "hfss"
    actual = sorted(_script_key(path) for path in scripts_dir.glob("*.py"))
    declared = registry.get("scripts", {})
    errors: list[str] = []
    warnings: list[str] = []

    if registry.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    missing = sorted(set(actual) - set(declared))
    stale = sorted(set(declared) - set(actual))
    if missing:
        errors.append(f"unclassified scripts: {missing}")
    if stale:
        errors.append(f"stale classified scripts: {stale}")

    for script, meta in sorted(declared.items()):
        cls = meta.get("class")
        if cls not in ALLOWED_CLASSES:
            errors.append(f"{script}: invalid class {cls!r}")
        if not meta.get("runtime"):
            errors.append(f"{script}: missing runtime")
        if "production_allowed" not in meta:
            errors.append(f"{script}: missing production_allowed")
        name = Path(script).name
        if name.startswith(PROBE_PREFIXES) and cls != "probe":
            errors.append(f"{script}: probe/try/scan script must be class=probe")
        if cls == "probe" and bool(meta.get("production_allowed")):
            errors.append(f"{script}: probe scripts cannot be production_allowed")
        if cls == "legacy_text_unsafe" and bool(meta.get("production_allowed")):
            errors.append(f"{script}: legacy_text_unsafe cannot be production_allowed")
        if cls == "production" and name.startswith(PROBE_PREFIXES):
            errors.append(f"{script}: production script cannot use probe prefix")
        if cls == "maintenance" and bool(meta.get("production_allowed")):
            warnings.append(f"{script}: maintenance script is production_allowed")

    return {
        "status": "ok" if not errors else "failed",
        "script_count": len(actual),
        "classified_count": len(declared),
        "missing": missing,
        "stale": stale,
        "errors": errors,
        "warnings": warnings,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate tools/hfss script classification.")
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = validate_registry(load_registry(args.registry))
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
