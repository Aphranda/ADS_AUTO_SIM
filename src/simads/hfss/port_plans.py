"""Production port plans for HFSS 3D Layout connector workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Callable

METERS_PER_MIL = 25.4e-6


def _json_default(value: Any) -> str:
    return str(value)


def safe_aedt_call(label: str, call: Callable[[], Any]) -> dict[str, Any]:
    try:
        value = call()
        if isinstance(value, (list, tuple)):
            value = [str(item) for item in value]
        return {"ok": True, "value": value}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "call": label}


def parse_key_values(values: Any) -> dict[str, str]:
    output: dict[str, str] = {}
    if not isinstance(values, (list, tuple)):
        return output
    for item in values:
        text = str(item)
        if "=" in text:
            key, value = text.split("=", 1)
            output[key] = value
    return output


def float_value(values: dict[str, str], key: str, default: float = 0.0) -> float:
    try:
        return float(values.get(key, default))
    except (TypeError, ValueError):
        return default


def meter_to_mil(value: float) -> float:
    return value / METERS_PER_MIL


def format_mil(value: float) -> str:
    return f"{value:.6f}mil"


def schematic_ports(app: Any) -> list[str]:
    try:
        editor = app.odesign.SetActiveEditor("SchematicEditor")
        return [str(item) for item in editor.GetAllPorts()]
    except Exception:
        return []


def schematic_port_info(editor: Any, port: str) -> dict[str, Any]:
    raw = safe_aedt_call(f"SchematicEditor.GetPortInfo({port})", lambda: editor.GetPortInfo(port))
    values = parse_key_values(raw.get("value") if raw.get("ok") else [])
    x = float_value(values, "X")
    y = float_value(values, "Y")
    return {
        "port": port,
        "raw": raw,
        "x": x,
        "y": y,
        "x_mil": meter_to_mil(x),
        "y_mil": meter_to_mil(y),
        "angle": float_value(values, "Angle"),
        "wire_id": values.get("WireId"),
    }


def schematic_component_pin_info(editor: Any, component_selection: str, pin: str) -> dict[str, Any]:
    raw = safe_aedt_call(
        f"SchematicEditor.GetComponentPinInfo({component_selection}, {pin})",
        lambda: editor.GetComponentPinInfo(component_selection, pin),
    )
    values = parse_key_values(raw.get("value") if raw.get("ok") else [])
    x = float_value(values, "X")
    y = float_value(values, "Y")
    return {
        "component_selection": component_selection,
        "pin": pin,
        "raw": raw,
        "x": x,
        "y": y,
        "x_mil": meter_to_mil(x),
        "y_mil": meter_to_mil(y),
        "angle": float_value(values, "Angle"),
        "wire_id": values.get("WireId"),
    }


def layout_port_info(layout_editor: Any, port: str) -> dict[str, Any]:
    return {
        "port_info": safe_aedt_call(f"GetPortInfo({port})", lambda: layout_editor.GetPortInfo(port)),
        "net_connections": safe_aedt_call(f"GetNetConnections({port})", lambda: layout_editor.GetNetConnections(port)),
    }


def _port_values(info: dict[str, Any], key: str) -> list[Any]:
    item = info.get(key, {})
    return list(item.get("value") or []) if item.get("ok") else []


def is_connector_pin_edge_port(info: dict[str, Any], component_id: str, pin: str) -> bool:
    pvalues = _port_values(info, "port_info")
    cvalues = _port_values(info, "net_connections")
    return any("Type=EdgePort" in str(item) for item in pvalues) and any(
        f"ComponentPin {component_id} {pin} " in str(item) for item in cvalues
    )


def has_connection_points(info: dict[str, Any]) -> bool:
    for item in _port_values(info, "port_info"):
        text = str(item).replace(" ", "").upper()
        if text.startswith("CONNECTIONPOINTS="):
            return text != "CONNECTIONPOINTS=NONE"
    return False


def has_interface_connection(info: dict[str, Any]) -> bool:
    return any("InterfacePort " in str(item) for item in _port_values(info, "net_connections"))


def is_valid_connector_pin_port(info: dict[str, Any], component_id: str, pin: str) -> bool:
    return (
        is_connector_pin_edge_port(info, component_id, pin)
        and has_connection_points(info)
        and not has_interface_connection(info)
    )


def connection_points_value(info: dict[str, Any]) -> str | None:
    for item in _port_values(info, "port_info"):
        text = str(item)
        if text.replace(" ", "").upper().startswith("CONNECTIONPOINTS="):
            return text.split("=", 1)[1] if "=" in text else text
    return None


def _layout_ports(app: Any, layout: Any) -> list[str]:
    ports = [str(item) for item in getattr(app, "port_list", []) or []]
    if ports:
        return ports
    raw = safe_aedt_call("Layout.GetAllPorts", lambda: layout.GetAllPorts())
    return [str(item) for item in raw.get("value", [])] if raw.get("ok") else []


def _layout_port_summary(port: str, info: dict[str, Any]) -> dict[str, Any]:
    values = parse_key_values(_port_values(info, "port_info"))
    return {
        "port": port,
        "name": values.get("Name", port),
        "type": values.get("Type"),
        "connection_points": connection_points_value(info),
        "has_connection_points": has_connection_points(info),
        "net_connections": [str(item) for item in _port_values(info, "net_connections")],
        "has_interface_connection": has_interface_connection(info),
        "raw": info,
    }


def _desktop_boundary_warnings(app: Any) -> dict[str, Any]:
    desktop = getattr(app, "odesktop", None)
    if desktop is None:
        return {"raw": {"ok": False, "error": "app has no odesktop"}, "warnings": []}
    raw = safe_aedt_call("Desktop.GetMessages", lambda: desktop.GetMessages("", "", 1))
    values = [str(item) for item in raw.get("value", [])] if raw.get("ok") else []
    warnings = [item for item in values if "boundary" in item.lower() or "port" in item.lower()]
    return {"raw": raw, "warnings": warnings}


def connector_port_acceptance_report(app: Any, plans: tuple[ConnectorPinPortPlan, ...] = ()) -> dict[str, Any]:
    layout = app.odesign.SetActiveEditor("Layout")
    schematic = app.odesign.SetActiveEditor("SchematicEditor")
    layout_ports = _layout_ports(app, layout)
    layout_infos = {port: layout_port_info(layout, port) for port in layout_ports}
    layout_summaries = [_layout_port_summary(port, info) for port, info in layout_infos.items()]
    schematic_iports = [schematic_port_info(schematic, port) for port in schematic_ports(app)]

    component_pin_only_rejected = []
    interface_connection_rejected = []
    for plan in plans:
        for port, info in layout_infos.items():
            if is_connector_pin_edge_port(info, plan.component_id, plan.pin) and not has_connection_points(info):
                component_pin_only_rejected.append(
                    {
                        "port": port,
                        "component_id": plan.component_id,
                        "pin": plan.pin,
                        "connection_points": connection_points_value(info),
                        "net_connections": [str(item) for item in _port_values(info, "net_connections")],
                    }
                )
            if is_connector_pin_edge_port(info, plan.component_id, plan.pin) and has_interface_connection(info):
                interface_connection_rejected.append(
                    {
                        "port": port,
                        "component_id": plan.component_id,
                        "pin": plan.pin,
                        "net_connections": [str(item) for item in _port_values(info, "net_connections")],
                    }
                )

    expected = []
    for plan in plans:
        layout_info = layout_infos.get(plan.port)
        matching_iports = [
            item for item in schematic_iports if item["port"] == f"IPort@{plan.port}" or item["port"].startswith(f"IPort@{plan.port};")
        ]
        wire_ids = sorted({str(item["wire_id"]) for item in matching_iports if item.get("wire_id")})
        expected.append(
            {
                "component": plan.component,
                "component_def": plan.component_def,
                "component_id": plan.component_id,
                "raw_component": plan.raw_component,
                "pin": plan.pin,
                "port": plan.port,
                "layout_port_present": layout_info is not None,
                "layout_port_valid": bool(layout_info and is_valid_connector_pin_port(layout_info, plan.component_id, plan.pin)),
                "connection_points": connection_points_value(layout_info) if layout_info else None,
                "schematic_iports": matching_iports,
                "schematic_iport_count": len(matching_iports),
                "wire_ids": wire_ids,
                "schematic_connected": bool(wire_ids),
            }
        )

    boundary_messages = _desktop_boundary_warnings(app)
    return {
        "status": "ok" if all(item["layout_port_valid"] and item["schematic_connected"] for item in expected) else "needs_review",
        "port_count": {"layout": len(layout_summaries), "schematic_iports": len(schematic_iports), "expected": len(expected)},
        "layout_ports": layout_summaries,
        "schematic_iports": schematic_iports,
        "expected": expected,
        "component_pin_only_rejected": component_pin_only_rejected,
        "interface_connection_rejected": interface_connection_rejected,
        "boundary_warnings": boundary_messages["warnings"],
        "boundary_warning_raw": boundary_messages["raw"],
    }


def delete_schematic_iport(app: Any, port: str, *, delete_wires: bool = True) -> dict[str, Any]:
    editor = app.odesign.SetActiveEditor("SchematicEditor")
    before = schematic_ports(app)
    targets = [item for item in before if item == f"IPort@{port}" or item.startswith(f"IPort@{port};")]
    infos = [schematic_port_info(editor, item) for item in targets]
    wire_targets = sorted({str(info["wire_id"]) for info in infos if info.get("wire_id")}) if delete_wires else []
    port_delete_result = None
    wire_delete_result = None
    if targets:
        port_delete_result = editor.Delete(["NAME:Selections", "Selections:=", targets])
    if wire_targets:
        wire_delete_result = editor.Delete(["NAME:Selections", "Selections:=", wire_targets])
    return {
        "targets": targets,
        "target_info": infos,
        "wire_targets": wire_targets,
        "port_delete_result": _json_default(port_delete_result),
        "wire_delete_result": _json_default(wire_delete_result),
        "before": before,
        "after": schematic_ports(app),
    }


def _distance_mil(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.hypot(x1 - x2, y1 - y2)


def schematic_endpoint_obstacles(editor: Any) -> list[dict[str, Any]]:
    obstacles: list[dict[str, Any]] = []
    ports = safe_aedt_call("SchematicEditor.GetAllPorts", lambda: editor.GetAllPorts())
    for port in ports.get("value", []) if ports.get("ok") else []:
        info = schematic_port_info(editor, str(port))
        if info["raw"].get("ok"):
            obstacles.append({"kind": "port", "name": str(port), "x_mil": info["x_mil"], "y_mil": info["y_mil"]})

    components = safe_aedt_call("SchematicEditor.GetAllComponents", lambda: editor.GetAllComponents())
    for component in components.get("value", []) if components.get("ok") else []:
        pins = safe_aedt_call(f"SchematicEditor.GetComponentPins({component})", lambda component=component: editor.GetComponentPins(component))
        for pin in pins.get("value", []) if pins.get("ok") else []:
            info = schematic_component_pin_info(editor, str(component), str(pin))
            if info["raw"].get("ok"):
                obstacles.append(
                    {
                        "kind": "component_pin",
                        "component": str(component),
                        "pin": str(pin),
                        "name": f"{component}:{pin}",
                        "x_mil": info["x_mil"],
                        "y_mil": info["y_mil"],
                    }
                )
    return obstacles


def nearest_obstacle(x_mil: float, y_mil: float, obstacles: list[dict[str, Any]], *, ignore: set[str]) -> dict[str, Any] | None:
    nearest: dict[str, Any] | None = None
    for obstacle in obstacles:
        if obstacle.get("name") in ignore:
            continue
        distance = _distance_mil(x_mil, y_mil, float(obstacle["x_mil"]), float(obstacle["y_mil"]))
        candidate = {**obstacle, "distance_mil": distance}
        if nearest is None or distance < float(nearest["distance_mil"]):
            nearest = candidate
    return nearest


@dataclass(frozen=True)
class ConnectorPinPortPlan:
    component: str
    component_def: str
    component_id: str
    raw_component: str
    port: str
    pin: str = "Pin_T1"
    page: int = 1
    elements: tuple[str, ...] = ()
    methods: tuple[str, ...] = ("CreatePortsOnComponents",)
    delete_iport: bool = True
    connect_schematic: bool = True
    move_schematic_iport: bool = True
    delete_old_schematic_wires: bool = True
    schematic_safe_x_mil: float | None = None
    schematic_safe_y_mil: float | None = None
    schematic_safe_min_clearance_mil: float = 250.0
    schematic_safe_grid_start_x_mil: float = -4000.0
    schematic_safe_grid_start_y_mil: float = -4000.0
    schematic_safe_grid_step_mil: float = 1000.0
    schematic_safe_grid_count: int = 9
    metadata: dict[str, Any] = field(default_factory=dict)

    def element_candidates(self) -> list[str]:
        values = list(self.elements)
        values.extend(
            [
                self.component_id,
                f"0:{self.component_id}",
                f"1:{self.component_id}",
                f"{self.component_id}:0",
                f"{self.component_id}:1",
                f"{self.component_id}:{self.pin}",
                f"0:{self.component_id}:{self.pin}",
                f"1:{self.component_id}:{self.pin}",
                self.component,
                f"{self.component}:{self.pin}",
                self.component_def,
                f"{self.component_def}:{self.pin}",
                self.raw_component,
                self.port,
                f"{self.port}:{self.pin}",
            ]
        )
        return [item for item in dict.fromkeys(values) if item]

    def schematic_location_candidates(self) -> list[tuple[float, float, str]]:
        if self.schematic_safe_x_mil is not None and self.schematic_safe_y_mil is not None:
            return [(self.schematic_safe_x_mil, self.schematic_safe_y_mil, "explicit")]
        candidates: list[tuple[float, float, str]] = []
        for row in range(self.schematic_safe_grid_count):
            for col in range(self.schematic_safe_grid_count):
                x_mil = self.schematic_safe_grid_start_x_mil + col * self.schematic_safe_grid_step_mil
                y_mil = self.schematic_safe_grid_start_y_mil + row * self.schematic_safe_grid_step_mil
                candidates.append((x_mil, y_mil, "grid"))
        return candidates


def select_safe_schematic_location(editor: Any, plan: ConnectorPinPortPlan, iport: str) -> dict[str, Any]:
    obstacles = schematic_endpoint_obstacles(editor)
    ignore = {iport}
    evaluated = []
    for x_mil, y_mil, source in plan.schematic_location_candidates():
        nearest = nearest_obstacle(x_mil, y_mil, obstacles, ignore=ignore)
        clearance = float("inf") if nearest is None else float(nearest["distance_mil"])
        item = {"x_mil": x_mil, "y_mil": y_mil, "source": source, "clearance_mil": clearance, "nearest": nearest}
        evaluated.append(item)
        if clearance >= plan.schematic_safe_min_clearance_mil:
            return {"ok": True, "selected": item, "obstacle_count": len(obstacles), "evaluated": evaluated[:20]}
    best = max(evaluated, key=lambda item: item["clearance_mil"]) if evaluated else None
    return {"ok": False, "best": best, "obstacle_count": len(obstacles), "evaluated": evaluated[:20]}


def move_schematic_iport(editor: Any, iport: str, x_mil: float, y_mil: float) -> dict[str, Any]:
    before = schematic_port_info(editor, iport)
    change = safe_aedt_call(
        "SchematicEditor.ChangeProperty Component Location",
        lambda: editor.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:BaseElementTab",
                    ["NAME:PropServers", iport],
                    [
                        "NAME:ChangedProps",
                        ["NAME:Component Location", "X:=", format_mil(x_mil), "Y:=", format_mil(y_mil)],
                    ],
                ],
            ]
        ),
    )
    after = schematic_port_info(editor, iport)
    return {"before": before, "target_x_mil": x_mil, "target_y_mil": y_mil, "change": change, "after": after}


def delete_schematic_wires(editor: Any, wires: list[str]) -> dict[str, Any]:
    targets = [wire for wire in dict.fromkeys(wires) if wire]
    if not targets:
        return {"targets": [], "result": None}
    result = safe_aedt_call("SchematicEditor.Delete stale wires", lambda: editor.Delete(["NAME:Selections", "Selections:=", targets]))
    return {"targets": targets, "result": result}


def connect_schematic_iport_to_component_pin(app: Any, plan: ConnectorPinPortPlan, iport: str) -> dict[str, Any]:
    editor = app.odesign.SetActiveEditor("SchematicEditor")
    port_info = schematic_port_info(editor, iport)
    pin_info = schematic_component_pin_info(editor, plan.raw_component, plan.pin)
    if not port_info["raw"].get("ok") or not pin_info["raw"].get("ok"):
        return {
            "status": "missing_endpoint",
            "iport": iport,
            "component": plan.raw_component,
            "pin": plan.pin,
            "port_info": port_info,
            "pin_info": pin_info,
        }
    stale_wires = [port_info.get("wire_id"), pin_info.get("wire_id")] if plan.delete_old_schematic_wires else []
    delete_wires = delete_schematic_wires(editor, [str(wire) for wire in stale_wires if wire])

    move_result = None
    safe_location = None
    if plan.move_schematic_iport:
        safe_location = select_safe_schematic_location(editor, plan, iport)
        if not safe_location.get("ok"):
            return {
                "status": "no_safe_schematic_location",
                "iport": iport,
                "component": plan.raw_component,
                "pin": plan.pin,
                "initial_port_info": port_info,
                "initial_pin_info": pin_info,
                "delete_wires": delete_wires,
                "safe_location": safe_location,
            }
        selected = safe_location["selected"]
        move_result = move_schematic_iport(editor, iport, float(selected["x_mil"]), float(selected["y_mil"]))
        if not move_result["change"].get("ok"):
            return {
                "status": "move_iport_failed",
                "iport": iport,
                "component": plan.raw_component,
                "pin": plan.pin,
                "initial_port_info": port_info,
                "initial_pin_info": pin_info,
                "delete_wires": delete_wires,
                "safe_location": safe_location,
                "move": move_result,
            }

    port_info = schematic_port_info(editor, iport)
    pin_info = schematic_component_pin_info(editor, plan.raw_component, plan.pin)
    obstacles = schematic_endpoint_obstacles(editor)
    nearest = nearest_obstacle(port_info["x_mil"], port_info["y_mil"], obstacles, ignore={iport})
    clearance = float("inf") if nearest is None else float(nearest["distance_mil"])
    if clearance < plan.schematic_safe_min_clearance_mil:
        return {
            "status": "unsafe_iport_overlap_risk",
            "iport": iport,
            "component": plan.raw_component,
            "pin": plan.pin,
            "port_info": port_info,
            "pin_info": pin_info,
            "delete_wires": delete_wires,
            "safe_location": safe_location,
            "move": move_result,
            "nearest": nearest,
            "clearance_mil": clearance,
        }
    points = [str((port_info["x"], port_info["y"])), str((pin_info["x"], pin_info["y"]))]
    result = safe_aedt_call(
        "SchematicEditor.CreateWire",
        lambda: editor.CreateWire(["NAME:WireData", "Name:=", plan.port, "Points:=", points], ["NAME:Attributes", "Page:=", plan.page]),
    )
    port_after = schematic_port_info(editor, iport)
    pin_after = schematic_component_pin_info(editor, plan.raw_component, plan.pin)
    same_wire = bool(port_after.get("wire_id")) and port_after.get("wire_id") == pin_after.get("wire_id")
    return {
        "status": "connected" if result.get("ok") and same_wire else "connect_failed",
        "iport": iport,
        "component": plan.raw_component,
        "pin": plan.pin,
        "delete_wires": delete_wires,
        "safe_location": safe_location,
        "move": move_result,
        "nearest_after_move": nearest,
        "clearance_mil": clearance,
        "port_info": port_info,
        "pin_info": pin_info,
        "port_after": port_after,
        "pin_after": pin_after,
        "same_wire_after_connect": same_wire,
        "points": points,
        "result": result,
    }


def _save_project(app: Any, project: str | None) -> bool:
    if project:
        return bool(app.save_project(str(project), overwrite=True))
    try:
        return bool(app.save_project(overwrite=True))
    except TypeError:
        return bool(app.save_project())


def execute_connector_pin_port_plan(
    app: Any,
    plan: ConnectorPinPortPlan,
    *,
    execute: bool = False,
    save: bool = False,
    save_project_path: str | None = None,
) -> dict[str, Any]:
    layout = app.odesign.SetActiveEditor("Layout")
    payload: dict[str, Any] = {
        "component": plan.component,
        "component_def": plan.component_def,
        "component_id": plan.component_id,
        "raw_component": plan.raw_component,
        "pin": plan.pin,
        "port": plan.port,
        "execute": execute,
        "save": save,
        "before_ports": list(getattr(app, "port_list", []) or []),
        "before_schematic_ports": schematic_ports(app),
        "before_port_info": {port: layout_port_info(layout, port) for port in getattr(app, "port_list", []) or []},
        "component_pin_info": safe_aedt_call("GetComponentPinInfo", lambda: layout.GetComponentPinInfo(plan.component, plan.pin)),
        "elements": plan.element_candidates(),
        "methods": list(plan.methods),
        "metadata": dict(plan.metadata),
    }
    if not execute:
        payload["status"] = "dry_run"
        payload["acceptance_report"] = connector_port_acceptance_report(app, (plan,))
        return payload

    if plan.delete_iport:
        payload["delete"] = delete_schematic_iport(app, plan.port, delete_wires=plan.delete_old_schematic_wires)

    attempts = []
    for element in payload["elements"]:
        for method in plan.methods:
            before_ports = list(getattr(app, "port_list", []) or [])
            before_schematic = schematic_ports(app)
            call_args = ["NAME:elements", element]
            item: dict[str, Any] = {
                "method": method,
                "element": element,
                "call_args": call_args,
                "before_ports": before_ports,
                "before_schematic_ports": before_schematic,
            }
            if method == "CreatePortInstancePorts":
                item["result"] = safe_aedt_call(method, lambda call_args=call_args: layout.CreatePortInstancePorts(call_args))
            elif method == "CreatePortsOnComponents":
                item["result"] = safe_aedt_call(method, lambda call_args=call_args: layout.CreatePortsOnComponents(call_args))
            else:
                item["result"] = {"ok": False, "error": f"unsupported method {method}"}
            after_ports = list(getattr(app, "port_list", []) or [])
            item["after_ports"] = after_ports
            item["after_schematic_ports"] = schematic_ports(app)
            item["new_ports"] = [port for port in after_ports if port not in before_ports]
            item["new_schematic_ports"] = [port for port in item["after_schematic_ports"] if port not in before_schematic]
            item["after_port_info"] = {port: layout_port_info(layout, port) for port in after_ports}
            item["good_ports"] = [
                port
                for port, info in item["after_port_info"].items()
                if is_valid_connector_pin_port(info, plan.component_id, plan.pin)
            ]
            item["component_pin_only_ports"] = [
                port
                for port, info in item["after_port_info"].items()
                if is_connector_pin_edge_port(info, plan.component_id, plan.pin) and not has_connection_points(info)
            ]
            attempts.append(item)
            if item["good_ports"]:
                payload["attempts"] = attempts
                if plan.connect_schematic:
                    iports = [port for port in item["after_schematic_ports"] if port == f"IPort@{plan.port}" or port.startswith(f"IPort@{plan.port};")]
                    iport = iports[0] if iports else f"IPort@{plan.port}"
                    payload["schematic_connect"] = connect_schematic_iport_to_component_pin(app, plan, iport)
                    if payload["schematic_connect"].get("status") != "connected":
                        payload["status"] = "created_good_candidate_schematic_connect_failed_not_saved"
                        payload["acceptance_report"] = connector_port_acceptance_report(app, (plan,))
                        return payload
                if save:
                    payload["saved"] = _save_project(app, save_project_path)
                payload["status"] = "created_good_candidate"
                payload["acceptance_report"] = connector_port_acceptance_report(app, (plan,))
                return payload
    payload["attempts"] = attempts
    payload["status"] = "no_good_candidate_not_saved"
    payload["acceptance_report"] = connector_port_acceptance_report(app, (plan,))
    return payload


__all__ = [
    "ConnectorPinPortPlan",
    "connector_port_acceptance_report",
    "connect_schematic_iport_to_component_pin",
    "connection_points_value",
    "delete_schematic_iport",
    "execute_connector_pin_port_plan",
    "has_connection_points",
    "has_interface_connection",
    "is_connector_pin_edge_port",
    "is_valid_connector_pin_port",
    "layout_port_info",
    "parse_key_values",
    "safe_aedt_call",
    "schematic_ports",
]
