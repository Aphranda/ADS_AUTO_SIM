#!/usr/bin/env python3
"""Try HFSS 3D Layout port-instance APIs using Layout element identifiers."""

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


def _is_good_component_edge_port(info: dict[str, Any], component_id: str, pin: str) -> bool:
    port_info = info.get("port_info", {})
    net_connections = info.get("net_connections", {})
    values = port_info.get("value") if port_info.get("ok") else []
    conns = net_connections.get("value") if net_connections.get("ok") else []
    return any("Type=EdgePort" in item for item in values) and any(
        f"ComponentPin {component_id} {pin} " in item for item in conns
    )


def _candidate_elements(args: argparse.Namespace) -> list[str]:
    values = []
    for item in args.element:
        values.append(item)
    for ident in [args.component_id, args.schematic_port_id, args.wire_id]:
        if ident:
            values.extend([ident, f"0:{ident}", f"{ident}:0", f"{ident}:{args.pin}", f"0:{ident}:{args.pin}"])
    values.extend(
        [
            args.component,
            args.component_def,
            args.raw_component,
            args.port,
            f"{args.component}:{args.pin}",
            f"{args.component_def}:{args.pin}",
            f"{args.raw_component}:{args.pin}",
            f"Comp{args.component_id}" if args.component_id else "",
            f"Pin@{args.port};{args.component_id}" if args.component_id else "",
        ]
    )
    return [item for item in dict.fromkeys(values) if item]


def try_elements(args: argparse.Namespace) -> dict[str, Any]:
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
            "execute": args.execute,
            "save": args.save,
            "component": args.component,
            "component_id": args.component_id,
            "pin": args.pin,
            "before_ports": list(app.port_list),
            "before_schematic_ports": _schematic_ports(app),
            "before_port_info": {port: _port_info(layout, port) for port in app.port_list},
            "component_info": _safe("GetComponentInfo", lambda: layout.GetComponentInfo(args.component)),
            "component_pins": _safe("GetComponentPins", lambda: layout.GetComponentPins(args.component)),
            "component_pin_info": _safe(
                "GetComponentPinInfo",
                lambda: layout.GetComponentPinInfo(args.component, args.pin),
            ),
            "elements": _candidate_elements(args),
        }
        payload["element_probe"] = {}
        for element in payload["elements"]:
            payload["element_probe"][element] = {
                "GetPortInstances": _safe(f"GetPortInstances({element})", lambda element=element: layout.GetPortInstances(element)),
                "GetPortInfo": _safe(f"GetPortInfo({element})", lambda element=element: layout.GetPortInfo(element)),
                "GetNetConnections": _safe(
                    f"GetNetConnections({element})", lambda element=element: layout.GetNetConnections(element)
                ),
            }
        if not args.execute:
            payload["status"] = "dry_run"
            return payload

        payload["delete"] = _delete_schematic_iport(app, args.port)
        payload["after_delete_ports"] = list(app.port_list)
        attempts = []
        for element in payload["elements"]:
            for call_shape in ("elements_only", "elements_with_kind"):
                before = list(app.port_list)
                before_schematic = _schematic_ports(app)
                call_args = ["NAME:elements", element]
                item = {
                    "element": element,
                    "call_shape": call_shape,
                    "before_ports": before,
                    "before_schematic_ports": before_schematic,
                }
                if call_shape == "elements_only":
                    item["result"] = _safe(
                        f"CreatePortInstancePorts({element})",
                        lambda call_args=call_args: layout.CreatePortInstancePorts(call_args),
                    )
                else:
                    item["result"] = _safe(
                        f"CreatePortInstancePorts({element}, Port, 0, 0, 0)",
                        lambda call_args=call_args: layout.CreatePortInstancePorts(call_args, "Port", "0", "0", "0"),
                    )
                after = list(app.port_list)
                item["after_ports"] = after
                item["after_schematic_ports"] = _schematic_ports(app)
                item["new_ports"] = [port for port in after if port not in before]
                item["new_schematic_ports"] = [port for port in item["after_schematic_ports"] if port not in before_schematic]
                item["new_port_info"] = {port: _port_info(layout, port) for port in item["new_ports"]}
                attempts.append(item)
                for port, info in item["new_port_info"].items():
                    if _is_good_component_edge_port(info, args.component_id, args.pin):
                        if port != args.port:
                            layout.ChangeProperty(
                                [
                                    "NAME:AllTabs",
                                    [
                                        "NAME:BaseElementTab",
                                        ["NAME:PropServers", port],
                                        ["NAME:ChangedProps", ["NAME:Name", "Value:=", args.port]],
                                    ],
                                ]
                            )
                        payload["attempts"] = attempts
                        payload["after_port_info"] = {port: _port_info(layout, port) for port in app.port_list}
                        if args.save:
                            payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
                        payload["status"] = "created_good_candidate"
                        return payload
                if item["new_ports"] or item["new_schematic_ports"]:
                    payload["attempts"] = attempts
                    payload["after_port_info"] = {port: _port_info(layout, port) for port in app.port_list}
                    payload["status"] = "created_bad_or_unverified_candidate"
                    return payload
        payload["attempts"] = attempts
        payload["after_port_info"] = {port: _port_info(layout, port) for port in app.port_list}
        payload["status"] = "no_candidate_created"
        return payload
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Try CreatePortInstancePorts with Layout element IDs.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--component", default="S2")
    parser.add_argument("--component-def", default="SMA_KE_Unite_Small_Solder9")
    parser.add_argument("--raw-component", default="CompInst@SMA_KE_Unite_Small_Solder9;80;8")
    parser.add_argument("--component-id", default="80")
    parser.add_argument("--schematic-port-id", default="30")
    parser.add_argument("--wire-id", default="35")
    parser.add_argument("--pin", default="Pin_T1")
    parser.add_argument("--port", default="S2_1_Pin_T1")
    parser.add_argument("--element", action="append", default=[])
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
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = try_elements(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if payload.get("status") in {"dry_run", "created_good_candidate"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
