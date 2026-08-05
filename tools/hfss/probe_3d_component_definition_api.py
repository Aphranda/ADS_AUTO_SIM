#!/usr/bin/env python3
"""Probe HFSS 3D Layout 3D component definition update APIs without saving."""

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
    lowered = [token.lower() for token in tokens]
    return [name for name in names if any(token in name.lower() for token in lowered)]


def _properties(editor: Any, tab: str, server: str) -> dict[str, Any]:
    props = _safe(f"GetProperties({tab}, {server})", lambda: editor.GetProperties(tab, server))
    values: dict[str, Any] = {}
    if props["ok"]:
        for prop in props["value"]:
            values[prop] = _safe(
                f"GetPropertyValue({tab}, {server}, {prop})",
                lambda prop=prop: editor.GetPropertyValue(tab, server, prop),
            )
    return {"properties": props, "values": values}


def _port_state(app: Any, layout: Any, ports: list[str]) -> dict[str, Any]:
    state: dict[str, Any] = {
        "app_port_list": _safe("port_list", lambda: list(app.port_list)),
        "ports": {},
    }
    for port in ports:
        state["ports"][port] = {
            "info": _safe(f"GetPortInfo({port})", lambda port=port: layout.GetPortInfo(port)),
            "net_connections": _safe(
                f"GetNetConnections({port})",
                lambda port=port: layout.GetNetConnections(port),
            ),
            "em_design": _properties(layout, "EM Design", f"Excitations:{port}"),
        }
    return state


def _component_state(layout: Any, components: list[str]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for component in components:
        output[component] = {
            "component_info": _safe(
                f"GetComponentInfo({component})",
                lambda component=component: layout.GetComponentInfo(component),
            ),
            "component_pins": _safe(
                f"GetComponentPins({component})",
                lambda component=component: layout.GetComponentPins(component),
            ),
        }
        for tab in ("BaseElementTab", "PassedParameterTab", "EM Design"):
            output[component][tab] = _properties(layout, tab, component)
    return output


def _definition_call_args(args: argparse.Namespace) -> list[tuple[str, tuple[Any, ...]]]:
    definitions = list(dict.fromkeys(args.definition))
    components = list(dict.fromkeys(args.component))
    calls: list[tuple[str, tuple[Any, ...]]] = [
        ("no_args", ()),
    ]
    for definition in definitions:
        calls.extend(
            [
                (f"definition_string:{definition}", (definition,)),
                (f"definition_elements:{definition}", (["NAME:elements", definition],)),
                (f"definition_components:{definition}", (["NAME:Components", definition],)),
                (f"definition_defs:{definition}", (["NAME:Definitions", definition],)),
            ]
        )
    for component in components:
        calls.extend(
            [
                (f"component_string:{component}", (component,)),
                (f"component_elements:{component}", (["NAME:elements", component],)),
                (f"component_components:{component}", (["NAME:Components", component],)),
            ]
        )
    return calls


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
            "execute": args.execute,
            "save": args.save,
            "methods": _methods(layout, "3D", "component", "definition", "source", "port", "pin", "connect"),
            "before_ports": _port_state(app, layout, args.port),
            "components": _component_state(layout, args.component),
            "definitions": _component_state(layout, args.definition),
        }
        if not args.execute:
            payload["status"] = "dry_run"
            return payload

        attempts = []
        for label, call_args in _definition_call_args(args):
            item: dict[str, Any] = {"label": label, "call_args": [str(arg) for arg in call_args]}
            item["update_result"] = _safe(
                f"Update3DComponentDefinitions {label}",
                lambda call_args=call_args: layout.Update3DComponentDefinitions(*call_args),
            )
            item["post_update_ports"] = _port_state(app, layout, args.port)
            attempts.append(item)
            if args.stop_on_port_valid:
                port_values = item["post_update_ports"]["ports"]
                if all(
                    not any("HFSS Type=**Invalid**" in str(v) for v in p["em_design"]["values"].values())
                    for p in port_values.values()
                ):
                    break
        payload["attempts"] = attempts
        payload["after_ports"] = _port_state(app, layout, args.port)
        payload["validate_design"] = _safe("ValidateDesign", lambda: app.odesign.ValidateDesign())
        payload["post_validate_ports"] = _port_state(app, layout, args.port)
        payload["messages"] = _safe(
            "GetMessages",
            lambda: app.odesktop.GetMessages(app.project_name, app.design_name, 0),
        )
        if args.save:
            payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
        payload["status"] = "executed_not_saved" if not args.save else "executed_saved"
        return payload
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe 3D component definition update APIs.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--component", action="append", default=[])
    parser.add_argument("--definition", action="append", default=[])
    parser.add_argument("--port", action="append", default=[])
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--stop-on-port-valid", action="store_true")
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
