#!/usr/bin/env python3
"""Recreate an HFSS 3D Layout component-pin edge port through AEDT APIs."""

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


def _project_sidecars(project: Path) -> list[Path]:
    paths = [project]
    for suffix in (".aedb", ".aedtresults"):
        path = project.with_suffix(suffix)
        if path.exists():
            paths.append(path)
    return paths


def _backup_project(project: Path) -> list[str]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    copied: list[str] = []
    ignore_runtime = shutil.ignore_patterns("*.semaphore", "*.lock", "*.tmp")
    for source in _project_sidecars(project):
        target = source.with_name(f"{source.stem}.before_recreate_edge_port_{stamp}{source.suffix}")
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


def _delete_schematic_iport(app: Any, port_name: str) -> dict[str, Any]:
    editor = app.odesign.SetActiveEditor("SchematicEditor")
    before = _schematic_ports(app)
    targets = [port for port in before if port.startswith(f"IPort@{port_name};")]
    result = None
    if targets:
        result = editor.Delete(["NAME:Selections", "Selections:=", targets])
    return {
        "port_name": port_name,
        "targets": targets,
        "result": _json_default(result),
        "before": before,
        "after": _schematic_ports(app),
    }


def _port_info(layout: Any, port: str) -> dict[str, Any]:
    return {
        "port_info": _safe(f"GetPortInfo({port})", lambda: layout.GetPortInfo(port)),
        "net_connections": _safe(f"GetNetConnections({port})", lambda: layout.GetNetConnections(port)),
    }


def _is_component_edge_port(info: dict[str, Any], *, component_id: str, pin: str) -> bool:
    port_info = info.get("port_info", {})
    net_connections = info.get("net_connections", {})
    info_values = port_info.get("value") if port_info.get("ok") else []
    conn_values = net_connections.get("value") if net_connections.get("ok") else []
    return any("Type=EdgePort" in item for item in info_values) and any(
        f"ComponentPin {component_id} {pin} " in item for item in conn_values
    )


def _has_interface_port_connection(info: dict[str, Any]) -> bool:
    net_connections = info.get("net_connections", {})
    conn_values = net_connections.get("value") if net_connections.get("ok") else []
    return any("InterfacePort " in item for item in conn_values)


def _rename_port(layout: Any, old_name: str, new_name: str) -> dict[str, Any]:
    if old_name == new_name:
        return {"old_name": old_name, "new_name": new_name, "skipped": True}
    result = _safe(
        f"ChangeProperty rename {old_name} to {new_name}",
        lambda: layout.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:BaseElementTab",
                    ["NAME:PropServers", old_name],
                    ["NAME:ChangedProps", ["NAME:Name", "Value:=", new_name]],
                ],
            ]
        ),
    )
    return {"old_name": old_name, "new_name": new_name, "result": result}


def recreate(args: argparse.Namespace) -> dict[str, Any]:
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
            "component_info": _safe("GetComponentInfo", lambda: layout.GetComponentInfo(args.component)),
            "component_pins": _safe("GetComponentPins", lambda: layout.GetComponentPins(args.component)),
        }
        if not args.execute:
            payload["status"] = "dry_run"
            return payload

        if args.backup:
            payload["backups"] = _backup_project(args.project)

        payload["delete"] = _delete_schematic_iport(app, args.port)
        payload["after_delete_ports"] = list(app.port_list)
        payload["after_delete_schematic_ports"] = _schematic_ports(app)
        payload["after_delete_port_info"] = {port: _port_info(layout, port) for port in app.port_list}

        before_create = list(app.port_list)
        payload["create_result"] = _safe(
            f"CreatePortsOnComponentsByNet({args.component}, empty nets)",
            lambda: layout.CreatePortsOnComponentsByNet(["NAME:Components", args.component], [], "Port", "0", "0", "0"),
        )
        after_create = list(app.port_list)
        new_ports = [port for port in after_create if port not in before_create]
        payload["after_create_ports"] = after_create
        payload["new_ports"] = new_ports
        payload["after_create_port_info"] = {port: _port_info(layout, port) for port in after_create}

        good_ports = [
            port
            for port, info in payload["after_create_port_info"].items()
            if _is_component_edge_port(info, component_id=args.component_id, pin=args.pin)
            and not _has_interface_port_connection(info)
        ]
        payload["good_ports"] = good_ports
        if not good_ports:
            payload["status"] = "no_good_component_edge_port_not_saved"
            return payload

        chosen = good_ports[0]
        if args.keep_generated_name:
            payload["chosen_port"] = chosen
        else:
            payload["rename"] = _rename_port(layout, chosen, args.port)
            payload["chosen_port"] = args.port

        final_ports = list(app.port_list)
        payload["final_ports"] = final_ports
        payload["final_port_info"] = {port: _port_info(layout, port) for port in final_ports}
        chosen_info = payload["final_port_info"].get(payload["chosen_port"], {})
        if not _is_component_edge_port(chosen_info, component_id=args.component_id, pin=args.pin):
            payload["status"] = "final_port_not_component_edge_not_saved"
            return payload
        if _has_interface_port_connection(chosen_info):
            payload["status"] = "final_port_still_has_interface_connection_not_saved"
            return payload

        if args.save:
            payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
        payload["status"] = "recreated_component_edge_port"
        return payload
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recreate a component-pin edge port through AEDT APIs.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--component", required=True, help="Layout component name, for example S2.")
    parser.add_argument("--component-id", required=True, help="Schematic/layout component ID, for example 80.")
    parser.add_argument("--pin", default="Pin_T1")
    parser.add_argument("--port", required=True, help="Existing bad port name to delete/recreate.")
    parser.add_argument("--keep-generated-name", action="store_true")
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
    payload = recreate(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if payload.get("status") in {"dry_run", "recreated_component_edge_port"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
