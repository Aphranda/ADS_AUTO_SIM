#!/usr/bin/env python3
"""Try official HFSS 3D Layout Port > Create element syntax."""

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


def _delete_iport(app: Any, port: str) -> dict[str, Any]:
    editor = app.odesign.SetActiveEditor("SchematicEditor")
    before = _schematic_ports(app)
    targets = [item for item in before if item.startswith(f"IPort@{port};")]
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
    pinfo = info.get("port_info", {})
    nconn = info.get("net_connections", {})
    pvalues = pinfo.get("value") if pinfo.get("ok") else []
    cvalues = nconn.get("value") if nconn.get("ok") else []
    return any("Type=EdgePort" in item for item in pvalues) and any(
        f"ComponentPin {component_id} {pin} " in item for item in cvalues
    )


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
            payload["delete"] = _delete_iport(app, args.port)
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
                    if _is_good(info, args.component_id, args.pin) and not _has_interface(info)
                ]
                attempts.append(item)
                if item["good_ports"]:
                    payload["attempts"] = attempts
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
    parser.add_argument("--element", action="append", default=[])
    parser.add_argument("--method", action="append", choices=["CreatePortInstancePorts", "CreatePortsOnComponents"], default=[])
    parser.add_argument("--delete-iport", action="store_true")
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
    payload = run(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if payload.get("status") in {"dry_run", "created_good_candidate"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
