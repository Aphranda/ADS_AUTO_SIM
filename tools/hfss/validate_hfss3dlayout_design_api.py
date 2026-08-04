#!/usr/bin/env python3
"""Validate an HFSS 3D Layout design and collect AEDT messages through APIs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable


def _json_default(value: Any) -> str:
    return str(value)


def _safe(label: str, call: Callable[[], Any]) -> dict[str, Any]:
    try:
        value = call()
        if isinstance(value, (list, tuple)):
            value = [str(item) for item in value]
        return {"ok": True, "value": value}
    except Exception as exc:  # pragma: no cover - depends on AEDT COM/gRPC.
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "call": label}


def _module_methods(module: Any, needle: str | None = None) -> list[str]:
    methods = [name for name in dir(module) if not name.startswith("_")]
    if needle:
        methods = [name for name in methods if needle.lower() in name.lower()]
    return methods


def validate(args: argparse.Namespace) -> dict[str, Any]:
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
        payload: dict[str, Any] = {"project": str(args.project), "design": args.design}
        editor = app.odesign.SetActiveEditor("SchematicEditor")
        payload["ports"] = _safe("GetAllPorts", lambda: editor.GetAllPorts())
        payload["nets"] = _safe("GetAllNets", lambda: editor.GetAllNets())
        payload["validate_design"] = _safe("ValidateDesign", lambda: app.odesign.ValidateDesign())
        payload["validate_simple"] = _safe("validate_simple", lambda: app.validate_simple())
        payload["validate_full_design"] = _safe("validate_full_design", lambda: app.validate_full_design())
        payload["messages"] = _safe(
            "GetMessages",
            lambda: app.odesktop.GetMessages(app.project_name, app.design_name, 0),
        )
        payload["port_list"] = _safe("port_list", lambda: list(getattr(app, "port_list", [])))
        payload["excitations"] = _safe("excitations", lambda: list(getattr(app, "excitations", [])))
        payload["odesign_port_methods"] = [name for name in dir(app.odesign) if "Port" in name or "Source" in name]
        for module_name in ("Excitations", "BoundarySetup"):
            module = _safe(f"GetModule({module_name})", lambda module_name=module_name: app.odesign.GetModule(module_name))
            payload[f"{module_name}_module"] = module
            if module["ok"]:
                payload[f"{module_name}_methods"] = _module_methods(module["value"])
                payload[f"{module_name}_port_methods"] = _module_methods(module["value"], "port")
        payload["status"] = "validated"
        return payload
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an HFSS 3D Layout design through AEDT APIs.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
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
    payload = validate(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
