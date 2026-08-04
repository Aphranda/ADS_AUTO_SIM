#!/usr/bin/env python3
"""Add schematic interface ports for HFSS 3D Layout connector component pins."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import shutil
from typing import Any


def _json_default(value: Any) -> str:
    return str(value)


def _load_json_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON must be an object: {path}")
    return data


def _connector_placement_config(args: argparse.Namespace) -> dict[str, Any]:
    if args.project_config is None:
        return {}
    project_config = _load_json_object(args.project_config)
    hfss = project_config.get("hfss", {})
    if not isinstance(hfss, dict):
        return {}
    placement = hfss.get("connector_placement", {})
    if not isinstance(placement, dict):
        return {}
    profiles = placement.get("profiles", {})
    if not isinstance(profiles, dict):
        profiles = {}
    profile_name = args.connector_placement_profile or placement.get("default_profile")
    if not profile_name:
        return {}
    profile = profiles.get(str(profile_name), {})
    if not isinstance(profile, dict):
        raise ValueError(f"missing connector placement profile {profile_name!r} in {args.project_config}")
    args.connector_placement_profile = str(profile_name)
    return profile


def _components_from_profile(args: argparse.Namespace) -> list[str]:
    profile = _connector_placement_config(args)
    if not profile:
        return []
    connector_model = str(profile.get("connector_model", "") or "")
    p1 = profile.get("p1_component_name") or (f"{connector_model}1" if connector_model else None)
    p2 = profile.get("p2_component_name") or (f"{connector_model}2" if connector_model else None)
    if args.placement == "single":
        return [str(p1 if args.single_side == "P1" else p2)] if (p1 if args.single_side == "P1" else p2) else []
    if args.placement == "dual":
        return [str(item) for item in (p1, p2) if item]
    return []


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
        dst = src.with_name(f"{src.stem}.before_pin_iports_{stamp}{src.suffix}")
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
    return {"raw": item, "component": parts[0], "id": parts[1], "suffix": parts[2] if len(parts) > 2 else ""}


def _instances_by_component(editor: Any) -> dict[str, list[dict[str, str]]]:
    output: dict[str, list[dict[str, str]]] = {}
    for item in _component_instances(editor):
        parsed = _parse_component_instance(item)
        if not parsed:
            continue
        output.setdefault(parsed["component"], []).append(parsed)
    return output


def _instances_by_id(editor: Any) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for item in _component_instances(editor):
        parsed = _parse_component_instance(item)
        if parsed:
            output[parsed["id"]] = parsed
    return output


def _ports_from_editor(editor: Any) -> list[str]:
    try:
        return [str(item) for item in editor.GetAllPorts()]
    except Exception:
        return []


def _selection_for(instance: dict[str, str], *, suffix: str) -> str:
    return f"CompInst@{instance['component']};{instance['id']};{suffix}"


def add_pin_iports(args: argparse.Namespace) -> dict[str, Any]:
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
        by_component = _instances_by_component(editor)
        by_id = _instances_by_id(editor)
        before_ports = _ports_from_editor(editor)
        components = list(args.component)
        for component in _components_from_profile(args):
            if component not in components:
                components.append(component)
        selected: list[dict[str, Any]] = []
        for component_id in args.component_id:
            instance = by_id.get(str(component_id))
            if not instance:
                selected.append({"component_id": component_id, "status": "missing"})
                continue
            selected.append(
                {
                    "component": instance["component"],
                    "id": instance["id"],
                    "raw": instance["raw"],
                    "selection": _selection_for(instance, suffix=args.selection_suffix),
                    "status": "selected",
                    "source": "component_id",
                }
            )
        for component in components:
            matches = by_component.get(component, [])
            if not matches:
                selected.append({"component": component, "status": "missing"})
                continue
            instance = matches[-1]
            selected.append(
                {
                    "component": component,
                    "id": instance["id"],
                    "raw": instance["raw"],
                    "selection": _selection_for(instance, suffix=args.selection_suffix),
                    "status": "selected",
                    "source": "component",
                }
            )

        payload: dict[str, Any] = {
            "project": str(args.project),
            "design": args.design,
            "project_config": str(args.project_config) if args.project_config else None,
            "connector_placement_profile": args.connector_placement_profile,
            "placement": args.placement,
            "single_side": args.single_side,
            "components": components,
            "component_ids": args.component_id,
            "selection_suffix": args.selection_suffix,
            "before_ports": before_ports,
            "selected": selected,
            "execute": args.execute,
            "save": args.save,
        }
        if not selected:
            payload["status"] = "no_components_requested"
            return payload
        missing = [item for item in selected if item["status"] == "missing"]
        if missing:
            payload["status"] = "missing_components"
            return payload
        if not args.execute:
            payload["status"] = "dry_run"
            return payload
        if args.backup:
            payload["backups"] = _backup_project(args.project)

        selections = [item["selection"] for item in selected]
        result = editor.AddPinIPorts(["Name:Selections", "Selections:=", selections])
        payload["add_pin_iports_result"] = _json_default(result)
        payload["after_ports"] = _ports_from_editor(editor)
        payload["new_ports"] = [port for port in payload["after_ports"] if port not in before_ports]
        if args.save:
            payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
        payload["status"] = "added"
        return payload
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add interface ports for connector component pins in a 3D Layout schematic.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--project-config", type=Path, default=None)
    parser.add_argument("--connector-placement-profile", default=None)
    parser.add_argument("--placement", choices=["single", "dual"], default=None)
    parser.add_argument("--single-side", choices=["P1", "P2"], default="P1")
    parser.add_argument("--component", action="append", default=[], help="Component definition name, repeat for multiple connectors.")
    parser.add_argument("--component-id", action="append", default=[], help="Explicit schematic component instance ID, repeat as needed.")
    parser.add_argument("--selection-suffix", default="395", help="AEDT component selection suffix used by AddPinIPorts.")
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
    payload = add_pin_iports(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
