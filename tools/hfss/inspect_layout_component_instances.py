#!/usr/bin/env python3
"""Inspect HFSS 3D Layout component instance placement through AEDT API."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _json_default(value: Any) -> str:
    return str(value)


def _component_ids(editor: Any, *, limit: int = 1000) -> dict[str, list[str]]:
    components: dict[str, list[str]] = {}
    for idx in range(1, limit):
        comp_id = str(idx)
        try:
            info = editor.GetComponentInfo(comp_id)
        except Exception:
            continue
        if not info:
            continue
        component_name = None
        for item in info:
            text = str(item)
            if text.startswith("ComponentName="):
                component_name = text.split("=", 1)[1]
                break
        if component_name:
            components.setdefault(component_name, []).append(comp_id)
    return components


def _read_component_properties(editor: Any, comp_id: str) -> dict[str, Any]:
    props: dict[str, Any] = {"id": comp_id}
    for tab in ("BaseElementTab", "ComponentTab"):
        tab_props: dict[str, Any] = {}
        for prop in (
            "Component Name",
            "Location",
            "Angle",
            "Rotation Angle",
            "3D Placement",
            "Local Origin",
            "Layer",
            "PlacementLayer",
        ):
            try:
                tab_props[prop] = editor.GetPropertyValue(tab, comp_id, prop)
            except Exception:
                pass
        if tab_props:
            props[tab] = tab_props
    try:
        props["component_info"] = [str(item) for item in editor.GetComponentInfo(comp_id)]
    except Exception as exc:
        props["component_info_error"] = repr(exc)
    return props


def inspect_components(args: argparse.Namespace) -> dict[str, Any]:
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
        editor = app.odesign.SetActiveEditor("Layout")
        by_name = _component_ids(editor)
        selected_ids: list[str] = []
        for comp_id in args.component_id:
            if comp_id not in selected_ids:
                selected_ids.append(comp_id)
        for name in args.component_name:
            for comp_id in by_name.get(name, []):
                if comp_id not in selected_ids:
                    selected_ids.append(comp_id)
        if not selected_ids and args.all:
            for ids in by_name.values():
                for comp_id in ids:
                    if comp_id not in selected_ids:
                        selected_ids.append(comp_id)
        return {
            "project": str(args.project),
            "design": args.design,
            "component_names": args.component_name,
            "component_ids": args.component_id,
            "all_components": by_name,
            "selected": [_read_component_properties(editor, comp_id) for comp_id in selected_ids],
            "status": "inspected",
        }
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect HFSS 3D Layout component instance placement.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--component-name", action="append", default=[])
    parser.add_argument("--component-id", action="append", default=[])
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--version", default="2026.1")
    parser.add_argument("--non-graphical", action="store_true", default=True)
    parser.add_argument("--graphical", action="store_false", dest="non_graphical")
    parser.add_argument("--new-desktop", action="store_true", default=True)
    parser.add_argument("--attach-existing", action="store_false", dest="new_desktop")
    parser.add_argument("--remove-lock", action="store_true")
    parser.add_argument("--keep-attached", action="store_true")
    parser.add_argument("--close-projects", action="store_true")
    parser.add_argument("--close-desktop", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = inspect_components(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
