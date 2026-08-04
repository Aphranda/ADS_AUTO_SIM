#!/usr/bin/env python3
"""Add an existing schematic component definition to an AEDT design.

This is intended for HFSS 3D Layout project designs whose top-level schematic
contains layout/cosim component instances, such as an imported SMA connector
component linked into a CPWG fixture design.
"""

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
        dst = src.with_name(f"{src.stem}.before_schematic_component_{stamp}{src.suffix}")
        if src.is_dir():
            shutil.copytree(src, dst, ignore=ignore_runtime_locks)
        else:
            shutil.copy2(src, dst)
        copied.append(str(dst))
    return copied


def _component_instances(editor: Any) -> list[str]:
    try:
        return [str(item) for item in editor.GetAllComponents()]
    except Exception:
        return []


def _instance_components(instances: list[str]) -> list[str]:
    output = []
    for item in instances:
        if item.startswith("CompInst@"):
            body = item.removeprefix("CompInst@")
            component = body.split(";", 1)[0]
            output.append(component)
    return output


def add_component(args: argparse.Namespace) -> dict[str, Any]:
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
        editor = app.odesign.SetActiveEditor("SchematicEditor")
        before = _component_instances(editor)
        before_components = _instance_components(before)
        payload: dict[str, Any] = {
            "project": str(args.project),
            "design": args.design,
            "component": args.component,
            "before": before,
            "already_present": args.component in before_components,
            "execute": args.execute,
            "save": args.save,
            "location_m": [args.x, args.y],
            "angle_rad": args.angle_rad,
            "flip": args.flip,
        }
        if args.component in before_components and not args.allow_duplicate:
            payload["status"] = "skipped_existing_component"
            return payload
        if not args.execute:
            payload["status"] = "dry_run"
            return payload
        if args.backup:
            payload["backups"] = _backup_project(args.project)

        component_props = ["NAME:ComponentProps", "Name:=", args.component]
        attributes = [
            "NAME:Attributes",
            "Page:=",
            args.page,
            "X:=",
            args.x,
            "Y:=",
            args.y,
            "Angle:=",
            args.angle_rad,
            "Flip:=",
            args.flip,
        ]
        created = editor.CreateComponent(component_props, attributes)
        payload["created"] = str(created)
        payload["after"] = _component_instances(editor)
        if args.instance_name:
            try:
                inst = editor.GetCompInstanceFromInstanceName(args.instance_name)
                payload["instance_lookup_before_rename"] = str(inst)
            except Exception as exc:
                payload["instance_lookup_before_rename_error"] = repr(exc)
            # AEDT auto-assigns an instance name like S62. Renaming is not
            # required for simulation, so this script records rather than
            # force-edits it unless a future API path is needed.
            payload["requested_instance_name"] = args.instance_name
        if args.save:
            payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
        payload["status"] = "created"
        return payload
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add an existing schematic component instance to an AEDT design.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--component", required=True, help="Existing component definition name, for example SMA_KE_Unite_solder3.")
    parser.add_argument("--x", type=float, default=-0.00762, help="Schematic X location in meters.")
    parser.add_argument("--y", type=float, default=-0.04572, help="Schematic Y location in meters.")
    parser.add_argument("--angle-rad", type=float, default=0.0)
    parser.add_argument("--page", default=1)
    parser.add_argument("--flip", action="store_true")
    parser.add_argument("--instance-name", default=None)
    parser.add_argument("--allow-duplicate", action="store_true")
    parser.add_argument("--execute", action="store_true", help="Actually add the component. Without this, only dry-run.")
    parser.add_argument("--save", action="store_true", help="Save the AEDT project after creation.")
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
    payload = add_component(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
