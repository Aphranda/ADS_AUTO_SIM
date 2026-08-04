#!/usr/bin/env python3
"""Recreate a detached schematic IPort for an existing component-pin edge port."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import shutil
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


def _sidecars(project: Path) -> list[Path]:
    paths = [project]
    for suffix in (".aedb", ".aedtresults"):
        candidate = project.with_suffix(suffix)
        if candidate.exists():
            paths.append(candidate)
    return paths


def _backup(project: Path) -> list[str]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    copied: list[str] = []
    ignore_runtime = shutil.ignore_patterns("*.semaphore", "*.lock", "*.tmp")
    for src in _sidecars(project):
        dst = src.with_name(f"{src.stem}.before_detached_iport_{stamp}{src.suffix}")
        if src.is_dir():
            shutil.copytree(src, dst, ignore=ignore_runtime)
        else:
            shutil.copy2(src, dst)
        copied.append(str(dst))
    return copied


def _schematic_ports(app: Any) -> list[str]:
    try:
        editor = app.odesign.SetActiveEditor("SchematicEditor")
        return [str(item) for item in editor.GetAllPorts()]
    except Exception:
        return []


def _delete_iport(app: Any, name: str) -> dict[str, Any]:
    editor = app.odesign.SetActiveEditor("SchematicEditor")
    before = _schematic_ports(app)
    targets = [port for port in before if port.startswith(f"IPort@{name};")]
    result = None
    if targets:
        result = editor.Delete(["NAME:Selections", "Selections:=", targets])
    return {"targets": targets, "result": _json_default(result), "before": before, "after": _schematic_ports(app)}


def _create_iport(app: Any, *, name: str, x: float, y: float, angle: float, page: int) -> dict[str, Any]:
    editor = app.odesign.SetActiveEditor("SchematicEditor")
    before = _schematic_ports(app)
    result = editor.CreateIPort(
        ["NAME:IPortProps", "Name:=", name],
        ["NAME:Attributes", "Page:=", page, "X:=", x, "Y:=", y, "Angle:=", angle, "Flip:=", False],
    )
    after = _schematic_ports(app)
    return {
        "name": name,
        "x": x,
        "y": y,
        "angle": angle,
        "page": page,
        "result": _json_default(result),
        "before": before,
        "after": after,
        "new_ports": [port for port in after if port not in before],
    }


def _port_info(layout: Any, port: str) -> dict[str, Any]:
    return {
        "port_info": _safe(f"GetPortInfo({port})", lambda: layout.GetPortInfo(port)),
        "net_connections": _safe(f"GetNetConnections({port})", lambda: layout.GetNetConnections(port)),
    }


def _is_good(info: dict[str, Any], *, component_id: str, pin: str) -> bool:
    port_info = info.get("port_info", {})
    net_connections = info.get("net_connections", {})
    values = port_info.get("value") if port_info.get("ok") else []
    conns = net_connections.get("value") if net_connections.get("ok") else []
    return any("Type=EdgePort" in item for item in values) and any(
        f"ComponentPin {component_id} {pin} " in item for item in conns
    )


def _has_bad_interface_connection(info: dict[str, Any]) -> bool:
    net_connections = info.get("net_connections", {})
    conns = net_connections.get("value") if net_connections.get("ok") else []
    return any("InterfacePort " in item for item in conns)


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
            "pin": args.pin,
            "port": args.port,
            "execute": args.execute,
            "save": args.save,
            "before_ports": list(app.port_list),
            "before_schematic_ports": _schematic_ports(app),
            "before_port_info": {port: _port_info(layout, port) for port in app.port_list},
            "component_pin_info": _safe("GetComponentPinInfo", lambda: layout.GetComponentPinInfo(args.component, args.pin)),
        }
        if not args.execute:
            payload["status"] = "dry_run"
            return payload

        if args.backup:
            payload["backups"] = _backup(args.project)
        payload["delete"] = _delete_iport(app, args.port)
        payload["after_delete_ports"] = list(app.port_list)
        payload["after_delete_port_info"] = {port: _port_info(layout, port) for port in app.port_list}
        payload["create"] = _create_iport(app, name=args.port, x=args.x, y=args.y, angle=args.angle, page=args.page)
        payload["after_create_ports"] = list(app.port_list)
        payload["after_create_schematic_ports"] = _schematic_ports(app)
        payload["after_create_port_info"] = {port: _port_info(layout, port) for port in app.port_list}
        target_info = payload["after_create_port_info"].get(args.port, {})
        payload["target_good_component_edge"] = _is_good(target_info, component_id=args.component_id, pin=args.pin)
        payload["target_has_interface_connection"] = _has_bad_interface_connection(target_info)
        if not payload["target_good_component_edge"] or payload["target_has_interface_connection"]:
            payload["status"] = "detached_iport_not_good_not_saved"
            return payload
        if args.save:
            payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
        payload["status"] = "recreated_detached_iport_component_edge"
        return payload
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recreate a detached schematic IPort and verify component-pin edge binding.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--component", required=True)
    parser.add_argument("--component-id", required=True)
    parser.add_argument("--pin", default="Pin_T1")
    parser.add_argument("--port", required=True)
    parser.add_argument("--x", type=float, required=True)
    parser.add_argument("--y", type=float, required=True)
    parser.add_argument("--angle", type=float, default=0.0)
    parser.add_argument("--page", type=int, default=1)
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
    payload = run(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if payload.get("status") in {"dry_run", "recreated_detached_iport_component_edge"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
