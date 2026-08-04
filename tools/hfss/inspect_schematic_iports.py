#!/usr/bin/env python3
"""Inspect HFSS 3D Layout schematic interface ports through AEDT API."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _json_default(value: Any) -> str:
    return str(value)


def _safe(call) -> Any:
    try:
        return call()
    except Exception as exc:
        return {"error": repr(exc)}


def inspect_iports(args: argparse.Namespace) -> dict[str, Any]:
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
        ports = [str(item) for item in _safe(editor.GetAllPorts) or []]
        components = [str(item) for item in _safe(editor.GetAllComponents) or []]
        tabs = [
            "BaseElementTab",
            "EM Design",
            "ComponentTab",
            "PassedParameterTab",
            "PropDisplayMap",
        ]
        port_details = []
        for port in ports:
            detail: dict[str, Any] = {"port": port, "properties": {}}
            for tab in tabs:
                props = _safe(lambda tab=tab, port=port: list(editor.GetProperties(tab, port)))
                detail["properties"][tab] = props
                if isinstance(props, list):
                    values = {}
                    for prop in props:
                        values[str(prop)] = _safe(lambda tab=tab, port=port, prop=prop: editor.GetPropertyValue(tab, port, prop))
                    detail.setdefault("values", {})[tab] = values
            port_details.append(detail)
        return {
            "project": str(args.project),
            "design": args.design,
            "ports": ports,
            "components": components,
            "port_details": port_details,
            "status": "inspected",
        }
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect schematic IPorts in an HFSS 3D Layout design.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
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
    payload = inspect_iports(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
