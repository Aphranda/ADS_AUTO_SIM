#!/usr/bin/env python3
"""Delete schematic component instances from an HFSS 3D Layout design.

Use this for connector swaps after the replacement component and its ports have
been added. The script operates only through AEDT's SchematicEditor API and is
dry-run by default.
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
        dst = src.with_name(f"{src.stem}.before_delete_schematic_component_{stamp}{src.suffix}")
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


def _parse_component_instance(item: str) -> dict[str, str] | None:
    if not item.startswith("CompInst@"):
        return None
    body = item.removeprefix("CompInst@")
    parts = body.split(";")
    if len(parts) < 2:
        return None
    return {
        "raw": item,
        "component": parts[0],
        "id": parts[1],
        "suffix": parts[2] if len(parts) > 2 else "",
    }


def _instances_by_component(editor: Any) -> dict[str, list[dict[str, str]]]:
    output: dict[str, list[dict[str, str]]] = {}
    for item in _component_instances(editor):
        parsed = _parse_component_instance(item)
        if parsed:
            output.setdefault(parsed["component"], []).append(parsed)
    return output


def delete_components(args: argparse.Namespace) -> dict[str, Any]:
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
        by_component = _instances_by_component(editor)
        selected: list[dict[str, Any]] = []
        for component in args.component:
            matches = by_component.get(component, [])
            for instance in matches:
                selected.append({**instance, "selection": instance["raw"]})

        payload: dict[str, Any] = {
            "project": str(args.project),
            "design": args.design,
            "components": args.component,
            "before": before,
            "selected": selected,
            "execute": args.execute,
            "save": args.save,
        }
        if not selected:
            payload["status"] = "nothing_selected"
            return payload
        if not args.execute:
            payload["status"] = "dry_run"
            return payload
        if args.backup:
            payload["backups"] = _backup_project(args.project)

        selections = [item["selection"] for item in selected]
        result = editor.Delete(["NAME:Selections", "Selections:=", selections])
        payload["delete_result"] = _json_default(result)
        payload["after"] = _component_instances(editor)
        if args.save:
            payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
        payload["status"] = "deleted"
        return payload
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Delete schematic component instances from a 3D Layout design.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--component", action="append", required=True)
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
    payload = delete_components(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
