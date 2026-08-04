#!/usr/bin/env python3
"""Try creating an edge port directly on a layout component pin."""

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
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "call": label}


def _schematic_ports(app: Any) -> list[str]:
    try:
        editor = app.odesign.SetActiveEditor("SchematicEditor")
        return [str(item) for item in editor.GetAllPorts()]
    except Exception:
        return []


def _delete_schematic_iport(app: Any, name: str) -> dict[str, Any]:
    editor = app.odesign.SetActiveEditor("SchematicEditor")
    before = _schematic_ports(app)
    targets = [port for port in before if port.startswith(f"IPort@{name};")]
    result = None
    if targets:
        result = editor.Delete(["NAME:Selections", "Selections:=", targets])
    return {"name": name, "targets": targets, "result": _json_default(result), "before": before, "after": _schematic_ports(app)}


def _port_info(layout: Any, port: str) -> dict[str, Any]:
    return {
        "port_info": _safe(f"GetPortInfo({port})", lambda: layout.GetPortInfo(port)),
        "net_connections": _safe(f"GetNetConnections({port})", lambda: layout.GetNetConnections(port)),
    }


def _edge_args(selector: dict[str, Any], *, external: bool) -> list[Any]:
    args = ["NAME:Contents", "edge:=", selector, "btype:=", 0]
    if external:
        args.extend(["external:=", True])
    return args


def try_edge(args: argparse.Namespace) -> dict[str, Any]:
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
            "component": args.component,
            "pin": args.pin,
            "delete_port": args.delete_port,
            "execute": args.execute,
            "save": args.save,
            "before_port_list": list(app.port_list),
            "before_schematic_ports": _schematic_ports(app),
            "before_port_info": {port: _port_info(layout, port) for port in app.port_list},
        }
        if not args.execute:
            payload["status"] = "dry_run"
            return payload
        payload["delete"] = _delete_schematic_iport(app, args.delete_port) if args.delete_port else None
        candidates: list[dict[str, Any]] = []
        et_values = ["cp", "pin", "componentpin", "component_pin", "p"]
        key_sets = [
            {"comp:=": args.component, "pin:=": args.pin},
            {"component:=": args.component, "pin:=": args.pin},
            {"refdes:=": args.component, "pin:=": args.pin},
            {"prim:=": args.component, "pin:=": args.pin},
            {"name:=": args.component, "pin:=": args.pin},
        ]
        for et in et_values:
            for key_set in key_sets:
                selector: list[Any] = ["et:=", et]
                for key, value in key_set.items():
                    selector.extend([key, value])
                candidates.append({"selector": selector})
        attempts = []
        for candidate in candidates:
            for external in (False, True):
                before_ports = list(app.port_list)
                before_schematic = _schematic_ports(app)
                call_args = _edge_args(candidate["selector"], external=external)
                item = {
                    "selector": candidate["selector"],
                    "external": external,
                    "call_args": call_args,
                    "before_ports": before_ports,
                    "before_schematic": before_schematic,
                }
                item["result"] = _safe("CreateEdgePort", lambda call_args=call_args: layout.CreateEdgePort(call_args))
                after_ports = list(app.port_list)
                after_schematic = _schematic_ports(app)
                item["after_ports"] = after_ports
                item["after_schematic"] = after_schematic
                item["new_ports"] = [port for port in after_ports if port not in before_ports]
                item["new_schematic_ports"] = [port for port in after_schematic if port not in before_schematic]
                if item["new_ports"]:
                    item["new_port_info"] = {port: _port_info(layout, port) for port in item["new_ports"]}
                attempts.append(item)
                if item["new_ports"] or item["new_schematic_ports"]:
                    payload["attempts"] = attempts
                    payload["after_port_info"] = {port: _port_info(layout, port) for port in app.port_list}
                    if args.save:
                        payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
                    payload["status"] = "created_candidate"
                    return payload
        payload["attempts"] = attempts
        payload["after_port_info"] = {port: _port_info(layout, port) for port in app.port_list}
        payload["status"] = "no_candidate_created"
        return payload
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Try creating an edge port on a component pin.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--component", required=True)
    parser.add_argument("--pin", required=True)
    parser.add_argument("--delete-port", default="")
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
    payload = try_edge(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if payload.get("status") in {"dry_run", "created_candidate"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
