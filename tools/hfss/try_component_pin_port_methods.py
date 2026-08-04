#!/usr/bin/env python3
"""Probe less-common HFSS 3D Layout component-pin port creation APIs."""

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


def _delete_schematic_iport(app: Any, port_name: str) -> dict[str, Any]:
    editor = app.odesign.SetActiveEditor("SchematicEditor")
    before = _schematic_ports(app)
    targets = [port for port in before if port.startswith(f"IPort@{port_name};")]
    result = None
    if targets:
        result = editor.Delete(["NAME:Selections", "Selections:=", targets])
    return {"targets": targets, "result": _json_default(result), "before": before, "after": _schematic_ports(app)}


def _port_info(layout: Any, port: str) -> dict[str, Any]:
    return {
        "port_info": _safe(f"GetPortInfo({port})", lambda: layout.GetPortInfo(port)),
        "net_connections": _safe(f"GetNetConnections({port})", lambda: layout.GetNetConnections(port)),
    }


def _is_good(info: dict[str, Any], component_id: str, pin: str) -> bool:
    port_info = info.get("port_info", {})
    net_connections = info.get("net_connections", {})
    values = port_info.get("value") if port_info.get("ok") else []
    conns = net_connections.get("value") if net_connections.get("ok") else []
    return any("Type=EdgePort" in item for item in values) and any(
        f"ComponentPin {component_id} {pin} " in item for item in conns
    )


def _calls(layout: Any, args: argparse.Namespace) -> list[tuple[str, Callable[[], Any]]]:
    comp = args.component
    port = args.port
    pin = args.pin
    return [
        (
            "AddPortsToNet_target_net",
            lambda: layout.AddPortsToNet(["NAME:Nets", args.net]),
        ),
        (
            "AddPortsToNet_pin_net",
            lambda: layout.AddPortsToNet(["NAME:Nets", pin]),
        ),
        (
            "AddPortsToAllNets",
            lambda: layout.AddPortsToAllNets(),
        ),
        (
            "CreatePortsOnComponentsByNet_target_net",
            lambda: layout.CreatePortsOnComponentsByNet(["NAME:Components", comp], ["NAME:Nets", args.net], "Port", "0", "0", "0"),
        ),
        (
            "CreatePortsOnComponentsByNet_empty_nets",
            lambda: layout.CreatePortsOnComponentsByNet(["NAME:Components", comp], [], "Port", "0", "0", "0"),
        ),
        (
            "CreateCircuitPortsOnComponents_components_only",
            lambda: layout.CreateCircuitPortsOnComponents(["NAME:Components", comp], "Port", "0", "0", "0"),
        ),
        (
            "CreateCircuitPortsOnComponents_with_empty_nets",
            lambda: layout.CreateCircuitPortsOnComponents(["NAME:Components", comp], ["NAME:Nets"], "Port", "0", "0", "0"),
        ),
        (
            "CreatePinGroupPortsOnComponents_components_only",
            lambda: layout.CreatePinGroupPortsOnComponents(["NAME:Components", comp], "Port", "0", "0", "0"),
        ),
        (
            "CreatePinGroupPortsOnComponents_with_empty_nets",
            lambda: layout.CreatePinGroupPortsOnComponents(["NAME:Components", comp], ["NAME:Nets"], "Port", "0", "0", "0"),
        ),
        (
            "CreatePinGroupsAndPorts_component",
            lambda: layout.CreatePinGroupsAndPorts(["NAME:Components", comp], "Port", "0", "0", "0"),
        ),
        (
            "CreatePinGroupsAndPorts_component_empty_nets",
            lambda: layout.CreatePinGroupsAndPorts(["NAME:Components", comp], ["NAME:Nets"], "Port", "0", "0", "0"),
        ),
        (
            "CreatePortInstancePorts_port",
            lambda: layout.CreatePortInstancePorts(["NAME:elements", port], "Port", "0", "0", "0"),
        ),
        (
            "ConnectPortInstancesToPins_port_component_pin",
            lambda: layout.ConnectPortInstancesToPins(["NAME:PortInstances", port], ["NAME:Pins", f"{comp}:{pin}"]),
        ),
        (
            "ConnectPortInstancesToPins_component_pin_port",
            lambda: layout.ConnectPortInstancesToPins(["NAME:Pins", f"{comp}:{pin}"], ["NAME:PortInstances", port]),
        ),
    ]


def probe(args: argparse.Namespace) -> dict[str, Any]:
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
            "component_id": args.component_id,
            "pin": args.pin,
            "port": args.port,
            "execute": args.execute,
            "before_ports": list(app.port_list),
            "before_schematic_ports": _schematic_ports(app),
            "before_port_info": {port: _port_info(layout, port) for port in app.port_list},
            "component_info": _safe("GetComponentInfo", lambda: layout.GetComponentInfo(args.component)),
            "component_pins": _safe("GetComponentPins", lambda: layout.GetComponentPins(args.component)),
            "component_pin_info": _safe("GetComponentPinInfo", lambda: layout.GetComponentPinInfo(args.component, args.pin)),
        }
        if not args.execute:
            payload["status"] = "dry_run"
            return payload

        payload["delete"] = _delete_schematic_iport(app, args.port)
        payload["after_delete_ports"] = list(app.port_list)
        attempts = []
        for label, call in _calls(layout, args):
            before_ports = list(app.port_list)
            before_schematic = _schematic_ports(app)
            item: dict[str, Any] = {"label": label, "before_ports": before_ports, "before_schematic_ports": before_schematic}
            item["result"] = _safe(label, call)
            after_ports = list(app.port_list)
            item["after_ports"] = after_ports
            item["after_schematic_ports"] = _schematic_ports(app)
            item["new_ports"] = [port for port in after_ports if port not in before_ports]
            item["new_schematic_ports"] = [port for port in item["after_schematic_ports"] if port not in before_schematic]
            item["after_port_info"] = {port: _port_info(layout, port) for port in after_ports}
            item["good_ports"] = [
                port for port, info in item["after_port_info"].items() if _is_good(info, args.component_id, args.pin)
            ]
            attempts.append(item)
            if item["good_ports"]:
                payload["attempts"] = attempts
                payload["status"] = "created_good_candidate_not_saved"
                return payload
        payload["attempts"] = attempts
        payload["status"] = "no_good_candidate_not_saved"
        return payload
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Try component pin port creation methods without saving.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--component", required=True)
    parser.add_argument("--component-id", required=True)
    parser.add_argument("--pin", default="Pin_T1")
    parser.add_argument("--port", required=True)
    parser.add_argument("--net", default=None)
    parser.add_argument("--execute", action="store_true")
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
    if args.net is None:
        args.net = args.port
    payload = probe(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if payload.get("status") in {"dry_run", "created_good_candidate_not_saved"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
