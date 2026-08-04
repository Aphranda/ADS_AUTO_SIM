#!/usr/bin/env python3
"""Try official HFSS 3D Layout Port > Create element syntax."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import math
from pathlib import Path
import shutil
from typing import Any, Callable

METERS_PER_MIL = 25.4e-6


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


def _project_sidecars(project: Path) -> list[Path]:
    paths = [project]
    for suffix in (".aedb", ".aedtresults"):
        sidecar = project.with_suffix(suffix)
        if sidecar.exists():
            paths.append(sidecar)
    return paths


def _backup_project(project: Path) -> list[str]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    copied: list[str] = []
    ignore_runtime = shutil.ignore_patterns("*.semaphore", "*.lock", "*.tmp")
    for source in _project_sidecars(project):
        target = source.with_name(f"{source.stem}.before_official_port_create_{stamp}{source.suffix}")
        if source.is_dir():
            shutil.copytree(source, target, ignore=ignore_runtime)
        else:
            shutil.copy2(source, target)
        copied.append(str(target))
    return copied


def _schematic_ports(app: Any) -> list[str]:
    try:
        editor = app.odesign.SetActiveEditor("SchematicEditor")
        return [str(item) for item in editor.GetAllPorts()]
    except Exception:
        return []


def _meter_to_mil(value: float) -> float:
    return value / METERS_PER_MIL


def _format_mil(value: float) -> str:
    return f"{value:.6f}mil"


def _distance_mil(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.hypot(x1 - x2, y1 - y2)


def _delete_iport(app: Any, port: str, *, delete_wires: bool) -> dict[str, Any]:
    editor = app.odesign.SetActiveEditor("SchematicEditor")
    before = _schematic_ports(app)
    targets = [item for item in before if item.startswith(f"IPort@{port};")]
    infos = [_schematic_port_info(editor, item) for item in targets]
    wire_targets = sorted({info["wire_id"] for info in infos if info.get("wire_id")}) if delete_wires else []
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
        "after": _schematic_ports(app),
    }


def _parse_key_values(values: Any) -> dict[str, str]:
    output: dict[str, str] = {}
    if not isinstance(values, (list, tuple)):
        return output
    for item in values:
        text = str(item)
        if "=" in text:
            key, value = text.split("=", 1)
            output[key] = value
    return output


def _float_value(values: dict[str, str], key: str, default: float = 0.0) -> float:
    try:
        return float(values.get(key, default))
    except (TypeError, ValueError):
        return default


def _schematic_port_info(editor: Any, port: str) -> dict[str, Any]:
    raw = _safe(f"SchematicEditor.GetPortInfo({port})", lambda: editor.GetPortInfo(port))
    values = _parse_key_values(raw.get("value") if raw.get("ok") else [])
    return {
        "port": port,
        "raw": raw,
        "x": _float_value(values, "X"),
        "y": _float_value(values, "Y"),
        "x_mil": _meter_to_mil(_float_value(values, "X")),
        "y_mil": _meter_to_mil(_float_value(values, "Y")),
        "angle": _float_value(values, "Angle"),
        "wire_id": values.get("WireId"),
    }


def _schematic_component_pin_info(editor: Any, component_selection: str, pin: str) -> dict[str, Any]:
    raw = _safe(
        f"SchematicEditor.GetComponentPinInfo({component_selection}, {pin})",
        lambda: editor.GetComponentPinInfo(component_selection, pin),
    )
    values = _parse_key_values(raw.get("value") if raw.get("ok") else [])
    return {
        "component_selection": component_selection,
        "pin": pin,
        "raw": raw,
        "x": _float_value(values, "X"),
        "y": _float_value(values, "Y"),
        "x_mil": _meter_to_mil(_float_value(values, "X")),
        "y_mil": _meter_to_mil(_float_value(values, "Y")),
        "angle": _float_value(values, "Angle"),
        "wire_id": values.get("WireId"),
    }


def _schematic_endpoint_obstacles(editor: Any) -> list[dict[str, Any]]:
    obstacles: list[dict[str, Any]] = []
    ports = _safe("SchematicEditor.GetAllPorts", lambda: editor.GetAllPorts())
    for port in ports.get("value", []) if ports.get("ok") else []:
        info = _schematic_port_info(editor, str(port))
        if info["raw"].get("ok"):
            obstacles.append({"kind": "port", "name": str(port), "x_mil": info["x_mil"], "y_mil": info["y_mil"]})

    components = _safe("SchematicEditor.GetAllComponents", lambda: editor.GetAllComponents())
    for component in components.get("value", []) if components.get("ok") else []:
        pins = _safe(f"SchematicEditor.GetComponentPins({component})", lambda component=component: editor.GetComponentPins(component))
        for pin in pins.get("value", []) if pins.get("ok") else []:
            info = _schematic_component_pin_info(editor, str(component), str(pin))
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


def _nearest_obstacle(x_mil: float, y_mil: float, obstacles: list[dict[str, Any]], *, ignore: set[str]) -> dict[str, Any] | None:
    nearest: dict[str, Any] | None = None
    for obstacle in obstacles:
        if obstacle.get("name") in ignore:
            continue
        distance = _distance_mil(x_mil, y_mil, float(obstacle["x_mil"]), float(obstacle["y_mil"]))
        candidate = {**obstacle, "distance_mil": distance}
        if nearest is None or distance < float(nearest["distance_mil"]):
            nearest = candidate
    return nearest


def _schematic_location_candidates(args: argparse.Namespace) -> list[tuple[float, float, str]]:
    if args.schematic_safe_x_mil is not None and args.schematic_safe_y_mil is not None:
        return [(args.schematic_safe_x_mil, args.schematic_safe_y_mil, "explicit")]
    candidates: list[tuple[float, float, str]] = []
    for row in range(args.schematic_safe_grid_count):
        for col in range(args.schematic_safe_grid_count):
            x_mil = args.schematic_safe_grid_start_x_mil + col * args.schematic_safe_grid_step_mil
            y_mil = args.schematic_safe_grid_start_y_mil + row * args.schematic_safe_grid_step_mil
            candidates.append((x_mil, y_mil, "grid"))
    return candidates


def _select_safe_schematic_location(editor: Any, args: argparse.Namespace, iport: str) -> dict[str, Any]:
    obstacles = _schematic_endpoint_obstacles(editor)
    ignore = {iport}
    evaluated = []
    for x_mil, y_mil, source in _schematic_location_candidates(args):
        nearest = _nearest_obstacle(x_mil, y_mil, obstacles, ignore=ignore)
        clearance = float("inf") if nearest is None else float(nearest["distance_mil"])
        item = {"x_mil": x_mil, "y_mil": y_mil, "source": source, "clearance_mil": clearance, "nearest": nearest}
        evaluated.append(item)
        if clearance >= args.schematic_safe_min_clearance_mil:
            return {"ok": True, "selected": item, "obstacle_count": len(obstacles), "evaluated": evaluated[:20]}
    best = max(evaluated, key=lambda item: item["clearance_mil"]) if evaluated else None
    return {"ok": False, "best": best, "obstacle_count": len(obstacles), "evaluated": evaluated[:20]}


def _move_schematic_iport(editor: Any, iport: str, x_mil: float, y_mil: float) -> dict[str, Any]:
    before = _schematic_port_info(editor, iport)
    change = _safe(
        "SchematicEditor.ChangeProperty Component Location",
        lambda: editor.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:BaseElementTab",
                    ["NAME:PropServers", iport],
                    [
                        "NAME:ChangedProps",
                        ["NAME:Component Location", "X:=", _format_mil(x_mil), "Y:=", _format_mil(y_mil)],
                    ],
                ],
            ]
        ),
    )
    after = _schematic_port_info(editor, iport)
    return {"before": before, "target_x_mil": x_mil, "target_y_mil": y_mil, "change": change, "after": after}


def _delete_schematic_wires(editor: Any, wires: list[str]) -> dict[str, Any]:
    targets = [wire for wire in dict.fromkeys(wires) if wire]
    if not targets:
        return {"targets": [], "result": None}
    result = _safe("SchematicEditor.Delete stale wires", lambda: editor.Delete(["NAME:Selections", "Selections:=", targets]))
    return {"targets": targets, "result": result}


def _connect_schematic_iport_to_component_pin(app: Any, args: argparse.Namespace, iport: str) -> dict[str, Any]:
    editor = app.odesign.SetActiveEditor("SchematicEditor")
    port_info = _schematic_port_info(editor, iport)
    pin_info = _schematic_component_pin_info(editor, args.raw_component, args.pin)
    if not port_info["raw"].get("ok") or not pin_info["raw"].get("ok"):
        return {
            "status": "missing_endpoint",
            "iport": iport,
            "component": args.raw_component,
            "pin": args.pin,
            "port_info": port_info,
            "pin_info": pin_info,
        }
    stale_wires = [port_info.get("wire_id"), pin_info.get("wire_id")] if args.delete_old_schematic_wires else []
    delete_wires = _delete_schematic_wires(editor, [str(wire) for wire in stale_wires if wire])

    move_result = None
    safe_location = None
    if args.move_schematic_iport:
        safe_location = _select_safe_schematic_location(editor, args, iport)
        if not safe_location.get("ok"):
            return {
                "status": "no_safe_schematic_location",
                "iport": iport,
                "component": args.raw_component,
                "pin": args.pin,
                "initial_port_info": port_info,
                "initial_pin_info": pin_info,
                "delete_wires": delete_wires,
                "safe_location": safe_location,
            }
        selected = safe_location["selected"]
        move_result = _move_schematic_iport(editor, iport, float(selected["x_mil"]), float(selected["y_mil"]))
        if not move_result["change"].get("ok"):
            return {
                "status": "move_iport_failed",
                "iport": iport,
                "component": args.raw_component,
                "pin": args.pin,
                "initial_port_info": port_info,
                "initial_pin_info": pin_info,
                "delete_wires": delete_wires,
                "safe_location": safe_location,
                "move": move_result,
            }

    port_info = _schematic_port_info(editor, iport)
    pin_info = _schematic_component_pin_info(editor, args.raw_component, args.pin)
    obstacles = _schematic_endpoint_obstacles(editor)
    nearest = _nearest_obstacle(port_info["x_mil"], port_info["y_mil"], obstacles, ignore={iport})
    clearance = float("inf") if nearest is None else float(nearest["distance_mil"])
    if clearance < args.schematic_safe_min_clearance_mil:
        return {
            "status": "unsafe_iport_overlap_risk",
            "iport": iport,
            "component": args.raw_component,
            "pin": args.pin,
            "port_info": port_info,
            "pin_info": pin_info,
            "delete_wires": delete_wires,
            "safe_location": safe_location,
            "move": move_result,
            "nearest": nearest,
            "clearance_mil": clearance,
        }
    points = [
        str((port_info["x"], port_info["y"])),
        str((pin_info["x"], pin_info["y"])),
    ]
    result = _safe(
        "SchematicEditor.CreateWire",
        lambda: editor.CreateWire(
            ["NAME:WireData", "Name:=", args.port, "Points:=", points],
            ["NAME:Attributes", "Page:=", args.page],
        ),
    )
    port_after = _schematic_port_info(editor, iport)
    pin_after = _schematic_component_pin_info(editor, args.raw_component, args.pin)
    same_wire = bool(port_after.get("wire_id")) and port_after.get("wire_id") == pin_after.get("wire_id")
    return {
        "status": "connected" if result.get("ok") and same_wire else "connect_failed",
        "iport": iport,
        "component": args.raw_component,
        "pin": args.pin,
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


def _port_info(layout: Any, port: str) -> dict[str, Any]:
    return {
        "port_info": _safe(f"GetPortInfo({port})", lambda: layout.GetPortInfo(port)),
        "net_connections": _safe(f"GetNetConnections({port})", lambda: layout.GetNetConnections(port)),
    }


def _is_good(info: dict[str, Any], component_id: str, pin: str) -> bool:
    pinfo = info.get("port_info", {})
    nconn = info.get("net_connections", {})
    pvalues = pinfo.get("value") if pinfo.get("ok") else []
    cvalues = nconn.get("value") if nconn.get("ok") else []
    return any("Type=EdgePort" in item for item in pvalues) and any(
        f"ComponentPin {component_id} {pin} " in item for item in cvalues
    )


def _has_connection_points(info: dict[str, Any]) -> bool:
    pinfo = info.get("port_info", {})
    pvalues = pinfo.get("value") if pinfo.get("ok") else []
    for item in pvalues:
        text = str(item).replace(" ", "").upper()
        if text.startswith("CONNECTIONPOINTS="):
            return text != "CONNECTIONPOINTS=NONE"
    return False


def _has_interface(info: dict[str, Any]) -> bool:
    nconn = info.get("net_connections", {})
    cvalues = nconn.get("value") if nconn.get("ok") else []
    return any("InterfacePort " in item for item in cvalues)


def _element_candidates(args: argparse.Namespace) -> list[str]:
    values = list(args.element)
    ids = [args.component_id, args.schematic_component_id, args.schematic_symbol_id, args.page_net_id]
    for ident in [item for item in ids if item]:
        values.extend(
            [
                ident,
                f"0:{ident}",
                f"1:{ident}",
                f"{ident}:0",
                f"{ident}:1",
                f"{ident}:{args.pin}",
                f"0:{ident}:{args.pin}",
                f"1:{ident}:{args.pin}",
            ]
        )
    values.extend(
        [
            args.component,
            f"{args.component}:{args.pin}",
            args.component_def,
            f"{args.component_def}:{args.pin}",
            args.raw_component,
            args.port,
            f"{args.port}:{args.pin}",
        ]
    )
    return [item for item in dict.fromkeys(values) if item]


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
            "component": args.component,
            "component_id": args.component_id,
            "schematic_component_id": args.schematic_component_id,
            "pin": args.pin,
            "port": args.port,
            "execute": args.execute,
            "before_ports": list(app.port_list),
            "before_schematic_ports": _schematic_ports(app),
            "before_port_info": {port: _port_info(layout, port) for port in app.port_list},
            "component_pin_info": _safe("GetComponentPinInfo", lambda: layout.GetComponentPinInfo(args.component, args.pin)),
            "elements": _element_candidates(args),
        }
        if not args.execute:
            payload["status"] = "dry_run"
            return payload

        if args.backup:
            payload["backups"] = _backup_project(args.project)
        if args.delete_iport:
            payload["delete"] = _delete_iport(app, args.port, delete_wires=args.delete_old_schematic_wires)
        attempts = []
        for element in payload["elements"]:
            for method in args.method:
                before_ports = list(app.port_list)
                before_schematic = _schematic_ports(app)
                call_args = ["NAME:elements", element]
                item: dict[str, Any] = {
                    "method": method,
                    "element": element,
                    "call_args": call_args,
                    "before_ports": before_ports,
                    "before_schematic_ports": before_schematic,
                }
                if method == "CreatePortInstancePorts":
                    item["result"] = _safe(method, lambda call_args=call_args: layout.CreatePortInstancePorts(call_args))
                elif method == "CreatePortsOnComponents":
                    item["result"] = _safe(method, lambda call_args=call_args: layout.CreatePortsOnComponents(call_args))
                else:
                    item["result"] = {"ok": False, "error": f"unsupported method {method}"}
                after_ports = list(app.port_list)
                item["after_ports"] = after_ports
                item["after_schematic_ports"] = _schematic_ports(app)
                item["new_ports"] = [port for port in after_ports if port not in before_ports]
                item["new_schematic_ports"] = [port for port in item["after_schematic_ports"] if port not in before_schematic]
                item["after_port_info"] = {port: _port_info(layout, port) for port in after_ports}
                item["good_ports"] = [
                    port
                    for port, info in item["after_port_info"].items()
                    if _is_good(info, args.component_id, args.pin) and _has_connection_points(info) and not _has_interface(info)
                ]
                item["component_pin_only_ports"] = [
                    port
                    for port, info in item["after_port_info"].items()
                    if _is_good(info, args.component_id, args.pin) and not _has_connection_points(info)
                ]
                attempts.append(item)
                if item["good_ports"]:
                    payload["attempts"] = attempts
                    if args.connect_schematic:
                        iports = [port for port in item["after_schematic_ports"] if port.startswith(f"IPort@{args.port};")]
                        iport = iports[0] if iports else f"IPort@{args.port}"
                        payload["schematic_connect"] = _connect_schematic_iport_to_component_pin(app, args, iport)
                        if payload["schematic_connect"].get("status") != "connected":
                            payload["status"] = "created_good_candidate_schematic_connect_failed_not_saved"
                            return payload
                    if args.save:
                        payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
                    payload["status"] = "created_good_candidate"
                    return payload
        payload["attempts"] = attempts
        payload["status"] = "no_good_candidate_not_saved"
        return payload
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Try official Port > Create element syntax.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--component", required=True)
    parser.add_argument("--component-def", required=True)
    parser.add_argument("--component-id", required=True)
    parser.add_argument("--schematic-component-id", default="")
    parser.add_argument("--schematic-symbol-id", default="")
    parser.add_argument("--page-net-id", default="")
    parser.add_argument("--raw-component", default="")
    parser.add_argument("--pin", default="Pin_T1")
    parser.add_argument("--port", required=True)
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--element", action="append", default=[])
    parser.add_argument("--method", action="append", choices=["CreatePortInstancePorts", "CreatePortsOnComponents"], default=[])
    parser.add_argument("--delete-iport", action="store_true")
    parser.add_argument("--connect-schematic", action="store_true")
    parser.add_argument("--move-schematic-iport", action="store_true", default=True)
    parser.add_argument("--no-move-schematic-iport", action="store_false", dest="move_schematic_iport")
    parser.add_argument("--keep-old-schematic-wires", action="store_false", dest="delete_old_schematic_wires")
    parser.set_defaults(delete_old_schematic_wires=True)
    parser.add_argument("--schematic-safe-x-mil", type=float, default=None)
    parser.add_argument("--schematic-safe-y-mil", type=float, default=None)
    parser.add_argument("--schematic-safe-min-clearance-mil", type=float, default=250.0)
    parser.add_argument("--schematic-safe-grid-start-x-mil", type=float, default=-4000.0)
    parser.add_argument("--schematic-safe-grid-start-y-mil", type=float, default=-4000.0)
    parser.add_argument("--schematic-safe-grid-step-mil", type=float, default=1000.0)
    parser.add_argument("--schematic-safe-grid-count", type=int, default=9)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--backup", action="store_true")
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
        args.method = ["CreatePortInstancePorts", "CreatePortsOnComponents"]
    if args.connect_schematic and not args.raw_component:
        raise SystemExit("--connect-schematic requires --raw-component")
    if (args.schematic_safe_x_mil is None) ^ (args.schematic_safe_y_mil is None):
        raise SystemExit("--schematic-safe-x-mil and --schematic-safe-y-mil must be provided together")
    payload = run(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if payload.get("status") in {"dry_run", "created_good_candidate"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
