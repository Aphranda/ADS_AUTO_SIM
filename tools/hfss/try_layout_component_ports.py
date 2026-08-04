#!/usr/bin/env python3
"""Try creating HFSS 3D Layout component ports through Layout APIs."""

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


def _schematic_ports(app: Any) -> list[str]:
    try:
        editor = app.odesign.SetActiveEditor("SchematicEditor")
        return [str(item) for item in editor.GetAllPorts()]
    except Exception:
        return []


def _boundary_props(app: Any, port: str) -> dict[str, Any]:
    try:
        layout = app.odesign.SetActiveEditor("Layout")
        props = [str(item) for item in layout.GetProperties("EM Design", f"Excitations:{port}")]
    except Exception as exc:
        return {"error": repr(exc)}
    values = {}
    for prop in props:
        values[prop] = _safe(
            f"GetPropertyValue(EM Design, Excitations:{port}, {prop})",
            lambda prop=prop: layout.GetPropertyValue("EM Design", f"Excitations:{port}", prop),
        )
    return {"properties": props, "values": values}


def _delete_schematic_iport(app: Any, name: str) -> dict[str, Any]:
    editor = app.odesign.SetActiveEditor("SchematicEditor")
    before = _schematic_ports(app)
    targets = [port for port in before if port.startswith(f"IPort@{name};")]
    if not targets:
        return {"target": name, "before": before, "targets": [], "deleted": False}
    result = editor.Delete(["NAME:Selections", "Selections:=", targets])
    return {"target": name, "before": before, "targets": targets, "result": _json_default(result), "after": _schematic_ports(app)}


def _try_call(app: Any, method: str, component: str, net: str) -> dict[str, Any]:
    layout = app.odesign.SetActiveEditor("Layout")
    before_port_list = list(app.port_list)
    before_schematic = _schematic_ports(app)
    item: dict[str, Any] = {
        "method": method,
        "component": component,
        "net": net,
        "before_port_list": before_port_list,
        "before_schematic_ports": before_schematic,
    }
    if method == "pyaedt_create_ports_on_component_by_nets":
        result = _safe(
            f"create_ports_on_component_by_nets({component}, {net})",
            lambda: app.create_ports_on_component_by_nets(component=component, nets=net),
        )
    elif method == "layout_create_ports_on_components_by_net":
        result = _safe(
            f"CreatePortsOnComponentsByNet({component}, {net})",
            lambda: layout.CreatePortsOnComponentsByNet(["NAME:Components", component], ["NAME:Nets", net], "Port", "0", "0", "0"),
        )
    elif method == "layout_create_ports_on_components":
        result = _safe(
            f"CreatePortsOnComponents({component})",
            lambda: layout.CreatePortsOnComponents(["NAME:Components", component], "Port", "0", "0", "0"),
        )
    elif method == "layout_create_port_instance_ports":
        result = _safe(
            f"CreatePortInstancePorts({component})",
            lambda: layout.CreatePortInstancePorts(["NAME:Components", component], "Port", "0", "0", "0"),
        )
    elif method == "layout_create_interface_port_component":
        result = _safe(
            f"CreateInterfacePortComponent({component})",
            lambda: layout.CreateInterfacePortComponent(["NAME:elements", component]),
        )
    else:
        result = {"ok": False, "error": f"unknown method {method}"}
    after_port_list = list(app.port_list)
    after_schematic = _schematic_ports(app)
    item["result"] = result
    item["after_port_list"] = after_port_list
    item["after_schematic_ports"] = after_schematic
    item["new_port_list"] = [port for port in after_port_list if port not in before_port_list]
    item["new_schematic_ports"] = [port for port in after_schematic if port not in before_schematic]
    for port in item["new_port_list"]:
        item.setdefault("new_boundary_props", {})[port] = _boundary_props(app, port)
    return item


def try_ports(args: argparse.Namespace) -> dict[str, Any]:
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
        payload: dict[str, Any] = {
            "project": str(args.project),
            "design": args.design,
            "execute": args.execute,
            "save": args.save,
            "before_port_list": list(app.port_list),
            "before_schematic_ports": _schematic_ports(app),
            "before_boundary_props": {port: _boundary_props(app, port) for port in app.port_list},
        }
        if not args.execute:
            payload["status"] = "dry_run"
            return payload

        payload["delete"] = [_delete_schematic_iport(app, name) for name in args.delete_port]
        payload["after_delete_port_list"] = list(app.port_list)
        payload["after_delete_schematic_ports"] = _schematic_ports(app)
        attempts = []
        for method in args.method:
            for component in args.component:
                for net in args.net:
                    attempt = _try_call(app, method, component, net)
                    attempts.append(attempt)
                    if attempt["new_port_list"] or attempt["new_schematic_ports"]:
                        payload["attempts"] = attempts
                        payload["after_boundary_props"] = {port: _boundary_props(app, port) for port in app.port_list}
                        if args.save:
                            payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
                        payload["status"] = "created_candidate"
                        return payload
        payload["attempts"] = attempts
        payload["after_boundary_props"] = {port: _boundary_props(app, port) for port in app.port_list}
        payload["status"] = "no_candidate_created"
        return payload
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Try Layout API component port creation.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--delete-port", action="append", default=[])
    parser.add_argument("--component", action="append", required=True)
    parser.add_argument("--net", action="append", required=True)
    parser.add_argument(
        "--method",
        action="append",
        choices=[
            "pyaedt_create_ports_on_component_by_nets",
            "layout_create_ports_on_components_by_net",
            "layout_create_ports_on_components",
            "layout_create_port_instance_ports",
            "layout_create_interface_port_component",
        ],
        default=[],
    )
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
    if not args.method:
        args.method = [
            "pyaedt_create_ports_on_component_by_nets",
            "layout_create_ports_on_components_by_net",
            "layout_create_ports_on_components",
            "layout_create_port_instance_ports",
            "layout_create_interface_port_component",
        ]
    payload = try_ports(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if payload.get("status") in {"dry_run", "created_candidate"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
