#!/usr/bin/env python3
"""Try patching existing padstack pin ports to HFSS Gap properties without saving."""

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


def _props(editor: Any, port: str) -> dict[str, Any]:
    server = f"Excitations:{port}"
    props = _safe(f"GetProperties(EM Design, {server})", lambda: editor.GetProperties("EM Design", server))
    values = {}
    if props["ok"]:
        for prop in props["value"]:
            values[prop] = _safe(
                f"GetPropertyValue(EM Design, {server}, {prop})",
                lambda prop=prop: editor.GetPropertyValue("EM Design", server, prop),
            )
    return {"properties": props, "values": values}


def _port_info(layout: Any, port: str) -> dict[str, Any]:
    return {
        "port_info": _safe(f"GetPortInfo({port})", lambda: layout.GetPortInfo(port)),
        "net_connections": _safe(f"GetNetConnections({port})", lambda: layout.GetNetConnections(port)),
    }


def _set_existing_property(editor: Any, port: str, name: str, value: Any) -> dict[str, Any]:
    server = f"Excitations:{port}"
    return _safe(
        f"SetPropertyValue({server}, {name})",
        lambda: editor.SetPropertyValue("EM Design", server, name, value),
    )


def _patch_port(editor: Any, port: str, args: argparse.Namespace) -> dict[str, Any]:
    updates: dict[str, Any] = {
        "HFSS Type": "Gap",
        "Reference": args.reference,
        "Impedance": "50ohm",
        "Renormalize": "true",
        "Renormalize Impedance": "50ohm",
        "DeembedParasiticPortInductance": "false",
    }
    if args.orientation:
        updates["Orientation"] = args.orientation
    return {name: _set_existing_property(editor, port, name, value) for name, value in updates.items()}


def run(args: argparse.Namespace) -> dict[str, Any]:
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
        layout = app.odesign.SetActiveEditor("Layout")
        payload: dict[str, Any] = {
            "project": str(args.project),
            "design": args.design,
            "ports": args.port,
            "reference": args.reference,
            "execute": args.execute,
            "save": args.save,
            "before_port_list": _safe("port_list", lambda: list(app.port_list)),
            "before_props": {port: _props(layout, port) for port in args.port},
            "before_port_info": {port: _port_info(layout, port) for port in args.port},
        }
        if not args.execute:
            payload["status"] = "dry_run"
            return payload
        payload["patch"] = {port: _patch_port(layout, port, args) for port in args.port}
        payload["after_props"] = {port: _props(layout, port) for port in args.port}
        payload["after_port_info"] = {port: _port_info(layout, port) for port in args.port}
        payload["after_port_list"] = _safe("port_list", lambda: list(app.port_list))
        payload["validate_design"] = _safe("ValidateDesign", lambda: app.odesign.ValidateDesign())
        payload["validate_simple"] = _safe("validate_simple", lambda: app.validate_simple())
        payload["post_validate_port_list"] = _safe("post_validate_port_list", lambda: list(app.port_list))
        payload["messages"] = _safe(
            "GetMessages",
            lambda: app.odesktop.GetMessages(app.project_name, app.design_name, 0),
        )
        if args.save:
            payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
        payload["status"] = "patched_not_saved" if not args.save else "patched_saved"
        return payload
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Try patching pin ports to HFSS Gap properties.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--port", action="append", required=True)
    parser.add_argument("--reference", default="ETCH_INNER1:GND:hfss_ground_plane")
    parser.add_argument("--orientation", default="Vertical")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--save", action="store_true")
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
    payload = run(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
