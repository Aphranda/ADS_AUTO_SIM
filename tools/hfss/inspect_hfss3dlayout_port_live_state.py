#!/usr/bin/env python3
"""Read targeted HFSS 3D Layout port state through AEDT APIs without saving.

This is a narrow live probe for cases where the saved AEDT/AEDB text proves a
problem exists but cannot expose exact layout-editor connection details. It does
not execute repair calls and does not save the project.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Callable

_SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.hfss.aedt_startup import (
    aedt_automation_lock,
    apply_grpc_startup_compat,
    apply_pyaedt_settings,
    start_aedt_reaper,
    startup_snapshot,
)

apply_grpc_startup_compat()


def _json_default(value: Any) -> str:
    return str(value)


def _safe(label: str, call: Callable[[], Any]) -> dict[str, Any]:
    try:
        value = call()
        if isinstance(value, (list, tuple)):
            value = [str(item) for item in value]
        return {"ok": True, "value": value}
    except Exception as exc:  # pragma: no cover - depends on AEDT gRPC.
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "call": label}


def _properties(editor: Any, tab: str, server: str) -> dict[str, Any]:
    props = _safe(f"GetProperties({tab}, {server})", lambda: editor.GetProperties(tab, server))
    values: dict[str, Any] = {}
    if props.get("ok"):
        for prop in props.get("value", []):
            values[str(prop)] = _safe(
                f"GetPropertyValue({tab}, {server}, {prop})",
                lambda prop=prop: editor.GetPropertyValue(tab, server, prop),
            )
    return {"properties": props, "values": values}


def _schematic_port_state(schematic: Any, port: str) -> dict[str, Any]:
    return {
        "GetPortInfo": _safe(f"SchematicEditor.GetPortInfo({port})", lambda: schematic.GetPortInfo(port)),
    }


def _layout_port_state(layout: Any, port: str) -> dict[str, Any]:
    return {
        "GetPortInfo": _safe(f"Layout.GetPortInfo({port})", lambda: layout.GetPortInfo(port)),
        "GetNetConnections": _safe(f"Layout.GetNetConnections({port})", lambda: layout.GetNetConnections(port)),
        "BaseElementTab": _properties(layout, "BaseElementTab", port),
        "EM Design": _properties(layout, "EM Design", f"Excitations:{port}"),
    }


def _component_state(layout: Any, component: str) -> dict[str, Any]:
    return {
        "GetComponentInfo": _safe(f"Layout.GetComponentInfo({component})", lambda: layout.GetComponentInfo(component)),
        "GetComponentPins": _safe(f"Layout.GetComponentPins({component})", lambda: layout.GetComponentPins(component)),
        "BaseElementTab": _properties(layout, "BaseElementTab", component),
        "ComponentTab": _properties(layout, "ComponentTab", component),
    }


def _net_state(layout: Any, net: str) -> dict[str, Any]:
    calls: dict[str, Any] = {}
    for method in ("GetNetConnections", "GetNetObjects", "GetObjectsByNet", "GetNetInfo"):
        func = getattr(layout, method, None)
        if callable(func):
            calls[method] = _safe(f"Layout.{method}({net})", lambda func=func: func(net))
    return calls


def _validate_port_mapping(payload: dict[str, Any]) -> list[str]:
    findings = []
    for port, state in payload.get("layout_ports", {}).items():
        info = state.get("GetPortInfo", {})
        conns = state.get("GetNetConnections", {})
        info_values = [str(item) for item in info.get("value", [])] if info.get("ok") else []
        conn_values = [str(item) for item in conns.get("value", [])] if conns.get("ok") else []
        if any("Type=EdgePort" in item for item in info_values) and not conn_values:
            findings.append(f"{port}: edge port has no reported net connections")
        if any("ConnectionPoints=None" in item.replace(" ", "") for item in info_values):
            findings.append(f"{port}: port reports ConnectionPoints=None")
        if not info.get("ok"):
            findings.append(f"{port}: GetPortInfo failed: {info.get('error')}")
    port_list = payload.get("app_port_list", {})
    excitations = payload.get("app_excitations", {})
    if port_list.get("ok") and port_list.get("value") == []:
        findings.append("app.port_list is empty")
    if excitations.get("ok") and excitations.get("value") == []:
        findings.append("app.excitations is empty")
    return findings


def inspect(args: argparse.Namespace) -> dict[str, Any]:
    from ansys.aedt.core import Hfss3dLayout, settings

    apply_pyaedt_settings(settings)
    with aedt_automation_lock("inspect_hfss3dlayout_port_live_state") as lock_info:
        app = Hfss3dLayout(
            project=str(args.project),
            design=args.design,
            version=args.version,
            non_graphical=args.non_graphical,
            new_desktop=args.new_desktop,
            close_on_exit=False,
            remove_lock=args.remove_lock,
        )
        reaper = start_aedt_reaper(
            app,
            label="inspect_hfss3dlayout_port_live_state",
            execute=not args.keep_attached,
            script_started=bool(args.new_desktop and args.non_graphical),
        )
        try:
            layout = app.odesign.SetActiveEditor("Layout")
            schematic = app.odesign.SetActiveEditor("SchematicEditor")
            payload: dict[str, Any] = {
                "project": str(args.project),
                "design": args.design,
                "backend": "pyaedt_live_readonly",
                "non_graphical": args.non_graphical,
                "new_desktop": args.new_desktop,
                "save": False,
                "aedt_startup": startup_snapshot(settings),
                "aedt_lock": lock_info,
                "aedt_reaper": reaper,
                "app_port_list": _safe("app.port_list", lambda: list(getattr(app, "port_list", []))),
                "app_excitations": _safe("app.excitations", lambda: list(getattr(app, "excitations", []))),
                "schematic_ports": _safe("SchematicEditor.GetAllPorts", lambda: schematic.GetAllPorts()),
                "layout_ports": {port: _layout_port_state(layout, port) for port in args.port},
                "schematic_port_details": {port: _schematic_port_state(schematic, port) for port in args.port},
                "components": {component: _component_state(layout, component) for component in args.component},
                "nets": {net: _net_state(layout, net) for net in args.net},
                "validate_design": _safe("ValidateDesign", lambda: app.odesign.ValidateDesign()) if args.validate else None,
            }
            payload["findings"] = _validate_port_mapping(payload)
            payload["status"] = "inspected"
            return payload
        finally:
            if not args.keep_attached:
                app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def _print_summary(payload: dict[str, Any]) -> None:
    print(f"project={payload.get('project')}")
    print(f"design={payload.get('design')} status={payload.get('status')}")
    print(f"app_port_list={payload.get('app_port_list')}")
    print(f"app_excitations={payload.get('app_excitations')}")
    for port, state in payload.get("layout_ports", {}).items():
        print(f"\n[{port}]")
        print(f"  info={state.get('GetPortInfo')}")
        print(f"  net_connections={state.get('GetNetConnections')}")
    for finding in payload.get("findings", []):
        print(f"finding: {finding}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect targeted HFSS 3D Layout live port state.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--port", action="append", default=[])
    parser.add_argument("--component", action="append", default=[])
    parser.add_argument("--net", action="append", default=[])
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--version", default="2026.1")
    parser.add_argument("--non-graphical", action="store_true", default=True)
    parser.add_argument("--graphical", action="store_false", dest="non_graphical")
    parser.add_argument("--new-desktop", action="store_true", default=True)
    parser.add_argument("--attach-existing", action="store_false", dest="new_desktop")
    parser.add_argument("--remove-lock", action="store_true")
    parser.add_argument("--keep-attached", action="store_true")
    parser.add_argument("--close-projects", action="store_true")
    parser.add_argument("--close-desktop", action="store_true")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = inspect(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    if args.summary:
        _print_summary(payload)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
