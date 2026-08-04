#!/usr/bin/env python3
"""Probe HFSS 3D Layout editor component/net/port APIs without saving."""

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


def _methods(obj: Any, *tokens: str) -> list[str]:
    names = [name for name in dir(obj) if not name.startswith("_")]
    if tokens:
        lowered = [token.lower() for token in tokens]
        names = [name for name in names if any(token in name.lower() for token in lowered)]
    return names


def _properties(editor: Any, tab: str, server: str) -> dict[str, Any]:
    props = _safe(f"GetProperties({tab}, {server})", lambda: editor.GetProperties(tab, server))
    if not props["ok"]:
        return {"properties": props}
    values = {}
    for prop in props["value"]:
        values[prop] = _safe(
            f"GetPropertyValue({tab}, {server}, {prop})",
            lambda prop=prop: editor.GetPropertyValue(tab, server, prop),
        )
    return {"properties": props, "values": values}


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
        payload: dict[str, Any] = {"project": str(args.project), "design": args.design}
        layout = app.odesign.SetActiveEditor("Layout")
        schematic = app.odesign.SetActiveEditor("SchematicEditor")
        payload["app_port_list"] = _safe("port_list", lambda: list(app.port_list))
        payload["app_excitations"] = _safe("excitations", lambda: list(getattr(app, "excitations", [])))
        payload["layout_methods"] = _methods(layout, "component", "port", "net", "object", "excitation")
        payload["schematic_ports"] = _safe("SchematicEditor.GetAllPorts", lambda: schematic.GetAllPorts())
        payload["schematic_components"] = _safe("SchematicEditor.GetAllComponents", lambda: schematic.GetAllComponents())
        payload["layout_calls"] = {}
        call_specs: list[tuple[str, Callable[[], Any]]] = [
            ("GetAllPorts", lambda: layout.GetAllPorts()),
            ("GetAllNets", lambda: layout.GetAllNets()),
            ("GetAllObjects", lambda: layout.GetAllObjects()),
            ("GetAllElements", lambda: layout.GetAllElements()),
            ("GetComponents", lambda: layout.GetComponents()),
            ("GetComponentNames", lambda: layout.GetComponentNames()),
            ("GetComponentPins", lambda: layout.GetComponentPins()),
            ("GetExcitations", lambda: layout.GetExcitations()),
            ("GetNetNames", lambda: layout.GetNetNames()),
            ("GetSelections", lambda: layout.GetSelections()),
        ]
        for label, call in call_specs:
            payload["layout_calls"][label] = _safe(label, call)
        try_names: list[str] = []
        for key in ("GetComponents", "GetComponentNames", "GetAllObjects", "GetAllElements"):
            value = payload["layout_calls"].get(key, {})
            if value.get("ok"):
                try_names.extend([str(item) for item in value["value"]])
        try_names.extend(args.server)
        try_names = list(dict.fromkeys([name for name in try_names if name]))
        payload["layout_properties"] = {}
        for server in try_names[: args.max_servers]:
            payload["layout_properties"][server] = {}
            for tab in ("BaseElementTab", "EM Design", "Geometry3DAttributeTab", "PassedParameterTab"):
                payload["layout_properties"][server][tab] = _properties(layout, tab, server)
        payload["boundary_props"] = {}
        for port in app.port_list:
            payload["boundary_props"][port] = _properties(layout, "EM Design", f"Excitations:{port}")
        payload["candidate_calls"] = {}
        for name in args.server:
            payload["candidate_calls"][name] = {
                "GetComponentInfo": _safe(f"GetComponentInfo({name})", lambda name=name: layout.GetComponentInfo(name)),
                "GetComponentPins": _safe(f"GetComponentPins({name})", lambda name=name: layout.GetComponentPins(name)),
                "GetPortInfo": _safe(f"GetPortInfo({name})", lambda name=name: layout.GetPortInfo(name)),
                "GetPortInstances": _safe(f"GetPortInstances({name})", lambda name=name: layout.GetPortInstances(name)),
                "GetNetConnections": _safe(f"GetNetConnections({name})", lambda name=name: layout.GetNetConnections(name)),
            }
        payload["status"] = "probed"
        return payload
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe HFSS 3D Layout port/component APIs.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--server", action="append", default=[])
    parser.add_argument("--max-servers", type=int, default=80)
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
    payload = probe(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
