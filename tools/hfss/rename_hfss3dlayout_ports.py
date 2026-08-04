#!/usr/bin/env python3
"""Rename HFSS 3D Layout ports through the AEDT API."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import shutil
from typing import Any


def _json_default(value: Any) -> str:
    return str(value)


def _project_sidecars(project: Path) -> list[Path]:
    paths = [project]
    for suffix in [".aedb", ".aedtresults"]:
        sidecar = project.with_suffix(suffix)
        if sidecar.exists():
            paths.append(sidecar)
    return paths


def _backup_project(project: Path) -> list[str]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    copied: list[str] = []
    ignore_runtime_locks = shutil.ignore_patterns("*.semaphore", "*.lock", "*.tmp")
    for src in _project_sidecars(project):
        dst = src.with_name(f"{src.stem}.before_rename_ports_{stamp}{src.suffix}")
        if src.is_dir():
            shutil.copytree(src, dst, ignore=ignore_runtime_locks)
        else:
            shutil.copy2(src, dst)
        copied.append(str(dst))
    return copied


def _parse_mapping(values: list[str]) -> list[tuple[str, str]]:
    pairs = []
    for value in values:
        if "=" not in value:
            raise ValueError(f"port mapping must be OLD=NEW, got {value!r}")
        old, new = value.split("=", 1)
        old = old.strip()
        new = new.strip()
        if not old or not new:
            raise ValueError(f"port mapping must be OLD=NEW, got {value!r}")
        pairs.append((old, new))
    return pairs


def rename_ports(args: argparse.Namespace) -> dict[str, Any]:
    mappings = _parse_mapping(args.rename)
    from ansys.aedt.core import Hfss3dLayout

    app = Hfss3dLayout(
        project=str(args.project),
        design=args.design,
        version=args.version,
        non_graphical=args.non_graphical,
        new_desktop=args.new_desktop,
        close_on_exit=False,
        remove_lock=args.remove_lock,
    )
    try:
        before = [str(name) for name in getattr(app, "port_list", []) or getattr(app, "ports", [])]
        if not before:
            try:
                before = [str(item) for item in app.odesign.GetModule("BoundarySetup").GetExcitations()]
            except Exception:
                before = []
        existing = set(before)
        payload: dict[str, Any] = {
            "project": str(args.project),
            "design": args.design,
            "mappings": [{"old": old, "new": new} for old, new in mappings],
            "before_ports": before,
            "execute": args.execute,
            "save": args.save,
        }
        checks = []
        for old, new in mappings:
            checks.append({"old": old, "new": new, "old_exists": old in existing, "new_exists": new in existing})
        payload["checks"] = checks
        missing = [item for item in checks if not item["old_exists"]]
        conflicts = [item for item in checks if item["new_exists"] and item["old"] != item["new"]]
        if missing:
            payload["status"] = "missing_ports"
            return payload
        if conflicts and not args.allow_existing_target:
            payload["status"] = "target_exists"
            return payload
        if not args.execute:
            payload["status"] = "dry_run"
            return payload
        if args.backup:
            payload["backups"] = _backup_project(args.project)

        renamed = []
        for old, new in mappings:
            result = app.odesign.RenamePort(old, new)
            renamed.append({"old": old, "new": new, "result": _json_default(result)})
        payload["renamed"] = renamed
        after = [str(name) for name in getattr(app, "port_list", []) or getattr(app, "ports", [])]
        if not after:
            try:
                after = [str(item) for item in app.odesign.GetModule("BoundarySetup").GetExcitations()]
            except Exception:
                after = []
        payload["after_ports"] = after
        if args.save:
            payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
        payload["status"] = "renamed"
        return payload
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rename HFSS 3D Layout ports.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--rename", action="append", required=True, help="Port rename mapping OLD=NEW. Repeat as needed.")
    parser.add_argument("--allow-existing-target", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--backup", action="store_true")
    parser.add_argument("--version", default="2026.1")
    parser.add_argument("--non-graphical", action="store_true")
    parser.add_argument("--new-desktop", action="store_true")
    parser.add_argument("--remove-lock", action="store_true")
    parser.add_argument("--keep-attached", action="store_true")
    parser.add_argument("--close-projects", action="store_true")
    parser.add_argument("--close-desktop", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = rename_ports(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
