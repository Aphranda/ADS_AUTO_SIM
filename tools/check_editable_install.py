#!/usr/bin/env python3
"""Check whether the SIM ADS automation package is installed editably."""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata as metadata
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urlparse


PACKAGE_NAME = "sim-ads-automation"
IMPORT_NAME = "simads"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def path_from_file_url(url: str) -> Path | None:
    parsed = urlparse(url)
    if parsed.scheme != "file":
        return None
    path = unquote(parsed.path)
    if sys.platform.startswith("win") and path.startswith("/"):
        path = path[1:]
    return Path(path).resolve()


def import_status(module_name: str) -> tuple[bool, str]:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"
    return True, str(getattr(module, "__file__", "built-in"))


def distribution_status(root: Path) -> dict[str, str]:
    try:
        dist = metadata.distribution(PACKAGE_NAME)
    except metadata.PackageNotFoundError:
        return {
            "installed": "no",
            "version": "",
            "editable": "no",
            "location": "",
        }

    direct_url = dist.read_text("direct_url.json")
    editable = "unknown"
    location = ""
    if direct_url:
        data = json.loads(direct_url)
        editable = "yes" if data.get("dir_info", {}).get("editable") else "no"
        file_path = path_from_file_url(str(data.get("url", "")))
        location = str(file_path) if file_path else str(data.get("url", ""))
        if editable == "yes" and file_path and file_path != root:
            editable = f"yes, but points to {file_path}"
    return {
        "installed": "yes",
        "version": dist.version,
        "editable": editable,
        "location": location,
    }


def dependency_status(names: list[str]) -> list[tuple[str, bool, str]]:
    rows = []
    for name in names:
        ok, detail = import_status(name)
        rows.append((name, ok, detail))
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check editable install status for sim-ads-automation.")
    parser.add_argument("--require-editable", action="store_true", help="Exit nonzero unless package is installed editably.")
    parser.add_argument(
        "--deps",
        nargs="*",
        default=["numpy", "scipy", "sklearn", "pandas", "matplotlib"],
        help="Python modules to import-check.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = repo_root()
    print(f"Python: {sys.executable}")
    print(f"Project root: {root}")

    simads_ok, simads_detail = import_status(IMPORT_NAME)
    dist = distribution_status(root)
    print(f"{IMPORT_NAME} import: {'ok' if simads_ok else 'missing'} ({simads_detail})")
    print(f"{PACKAGE_NAME} installed: {dist['installed']}")
    print(f"{PACKAGE_NAME} version: {dist['version']}")
    print(f"{PACKAGE_NAME} editable: {dist['editable']}")
    print(f"{PACKAGE_NAME} location: {dist['location']}")

    print("Dependencies:")
    for name, ok, detail in dependency_status(args.deps):
        print(f"  {name}: {'ok' if ok else 'missing'} ({detail})")

    print("Suggested editable install command:")
    print(f'  "{sys.executable}" -m pip install -e "{root}"')

    if args.require_editable and not (simads_ok and dist["installed"] == "yes" and dist["editable"] == "yes"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
