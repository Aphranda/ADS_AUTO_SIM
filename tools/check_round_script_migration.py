"""Validate the round script migration index.

This script is intentionally side-effect free. It checks that the migration
index remains complete enough to protect old round scripts while new work moves
to project sweep/optimizer configuration.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


VALID_STATUSES = {
    "active_configured",
    "legacy_candidate_generator",
    "legacy_reference",
}

REQUIRED_SCRIPT_FIELDS = {
    "script",
    "status",
    "migration_action",
}

ROUND_SCRIPT_RE = re.compile(r"^(make_.*round.*|make_next_filter_candidates)\.py$")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_index_path() -> Path:
    return repo_root() / "config" / "round_script_migration.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("top-level JSON value must be an object")
    return data


def validate_script_entry(entry: Any, index: int, root: Path) -> list[str]:
    errors: list[str] = []
    prefix = f"scripts[{index}]"

    if not isinstance(entry, dict):
        return [f"{prefix}: entry must be an object"]

    missing = sorted(REQUIRED_SCRIPT_FIELDS - set(entry))
    if missing:
        errors.append(f"{prefix}: missing required fields: {', '.join(missing)}")

    script = entry.get("script")
    if not isinstance(script, str) or not script.strip():
        errors.append(f"{prefix}.script: must be a non-empty string")
    else:
        script_path = root / script
        if not script_path.is_file():
            errors.append(f"{prefix}.script: file does not exist: {script}")

    status = entry.get("status")
    if status not in VALID_STATUSES:
        errors.append(
            f"{prefix}.status: invalid value {status!r}; "
            f"expected one of {', '.join(sorted(VALID_STATUSES))}"
        )

    migration_action = entry.get("migration_action")
    if not isinstance(migration_action, str) or not migration_action.strip():
        errors.append(f"{prefix}.migration_action: must be a non-empty string")

    return errors


def discover_round_scripts(root: Path) -> set[str]:
    tools_dir = root / "tools"
    if not tools_dir.is_dir():
        return set()
    return {
        f"tools/{path.name}"
        for path in tools_dir.glob("*.py")
        if ROUND_SCRIPT_RE.match(path.name)
    }


def validate_index(index_path: Path) -> tuple[list[str], list[str]]:
    root = repo_root()
    data = load_json(index_path)
    errors: list[str] = []
    warnings: list[str] = []

    scripts = data.get("scripts")
    if not isinstance(scripts, list):
        errors.append("scripts: must be a list")
        return errors, warnings

    seen: set[str] = set()
    indexed_round_scripts: set[str] = set()

    for index, entry in enumerate(scripts):
        errors.extend(validate_script_entry(entry, index, root))
        if not isinstance(entry, dict):
            continue

        script = entry.get("script")
        if not isinstance(script, str):
            continue

        normalized_script = script.replace("\\", "/")
        if normalized_script in seen:
            errors.append(f"scripts[{index}].script: duplicate entry: {script}")
        seen.add(normalized_script)

        name = Path(normalized_script).name
        if ROUND_SCRIPT_RE.match(name):
            indexed_round_scripts.add(normalized_script)

    discovered = discover_round_scripts(root)
    missing_from_index = sorted(discovered - indexed_round_scripts)
    if missing_from_index:
        warnings.append(
            "round-like scripts not indexed: " + ", ".join(missing_from_index)
        )

    return errors, warnings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate config/round_script_migration.json."
    )
    parser.add_argument(
        "--index",
        type=Path,
        default=default_index_path(),
        help="Path to the round script migration index.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    index_path = args.index.resolve()

    try:
        errors, warnings = validate_index(index_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: failed to read migration index: {exc}", file=sys.stderr)
        return 1

    for warning in warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors or (args.strict and warnings):
        return 1

    status = "ok"
    if warnings:
        status = "ok_with_warnings"
    print(f"round script migration index: {status}")
    print(f"index: {index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
