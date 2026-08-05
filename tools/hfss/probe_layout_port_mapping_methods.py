#!/usr/bin/env python3
"""Probe less-common layout port mapping methods without saving."""

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


def _props(editor: Any, port: str) -> dict[str, Any]:
    server = f"Excitations:{port}"
    props = _safe(f"GetProperties(EM Design, {server})", lambda: editor.GetProperties("EM Design", server))
    values: dict[str, Any] = {}
    if props["ok"]:
        for prop in props["value"]:
            values[prop] = _safe(
                f"GetPropertyValue(EM Design, {server}, {prop})",
                lambda prop=prop: editor.GetPropertyValue("EM Design", server, prop),
            )
    return {"properties": props, "values": values}


def _port_info(layout: Any, port: str) -> dict[str, Any]:
    return {
        "port_info": _safe(f"GetPortInfo({port})", lambda port=port: layout.GetPortInfo(port)),
        "net_connections": _safe(
            f"GetNetConnections({port})",
            lambda port=port: layout.GetNetConnections(port),
        ),
        "em_design": _props(layout, port),
    }


def _port_state(app: Any, layout: Any, extra_ports: list[str]) -> dict[str, Any]:
    port_list = _safe("port_list", lambda: list(app.port_list))
    ports = list(port_list.get("value", [])) if port_list.get("ok") else []
    ports.extend(extra_ports)
    ports = list(dict.fromkeys([str(port) for port in ports if port]))
    return {
        "app_port_list": port_list,
        "ports": {port: _port_info(layout, port) for port in ports},
    }


def _has_valid_hfss_port(info: dict[str, Any]) -> bool:
    values = info.get("em_design", {}).get("values", {})
    hfss = values.get("HFSS Type", {})
    if not hfss.get("ok"):
        return False
    return str(hfss.get("value")) not in {"", "**Invalid**", "Invalid"}


def _call_specs(layout: Any, args: argparse.Namespace) -> list[tuple[str, Callable[[], Any]]]:
    specs: list[tuple[str, Callable[[], Any]]] = []
    targets = list(dict.fromkeys(args.target))
    refdes = list(dict.fromkeys(args.refdes))
    ports = list(dict.fromkeys(args.port))
    pins = list(dict.fromkeys(args.pin))

    for item in refdes:
        specs.append((f"GetCompInstanceFromRefDes:{item}", lambda item=item: layout.GetCompInstanceFromRefDes(item)))

    specs.append(("PushExcitations:no_args", lambda: layout.PushExcitations()))
    for item in targets:
        specs.extend(
            [
                (f"ExpandWithPorts:string:{item}", lambda item=item: layout.ExpandWithPorts(item)),
                (f"ExpandWithPorts:elements:{item}", lambda item=item: layout.ExpandWithPorts(["NAME:elements", item])),
                (f"ExpandWithPorts:components:{item}", lambda item=item: layout.ExpandWithPorts(["NAME:Components", item])),
                (
                    f"CreateInterfacePortComponent:elements:{item}",
                    lambda item=item: layout.CreateInterfacePortComponent(["NAME:elements", item]),
                ),
                (f"PinConnectivity:string:{item}", lambda item=item: layout.PinConnectivity(item)),
                (
                    f"PinConnectivity:components:{item}",
                    lambda item=item: layout.PinConnectivity(["NAME:Components", item]),
                ),
                (
                    f"SelectPhysicallyConnected:elements:{item}",
                    lambda item=item: layout.SelectPhysicallyConnected(["NAME:elements", item]),
                ),
            ]
        )
    for port in ports:
        for pin in pins:
            specs.extend(
                [
                    (
                        f"ConnectPortInstancesToPins:{port}->{pin}",
                        lambda port=port, pin=pin: layout.ConnectPortInstancesToPins(
                            ["NAME:PortInstances", port],
                            ["NAME:Pins", pin],
                        ),
                    ),
                    (
                        f"ConnectPortInstancesToPins:{pin}->{port}",
                        lambda port=port, pin=pin: layout.ConnectPortInstancesToPins(
                            ["NAME:Pins", pin],
                            ["NAME:PortInstances", port],
                        ),
                    ),
                ]
            )
    return specs


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
            "before": _port_state(app, layout, args.port),
        }
        if not args.execute:
            payload["status"] = "dry_run"
            return payload

        attempts = []
        for label, call in _call_specs(layout, args):
            before = _port_state(app, layout, args.port)
            item: dict[str, Any] = {"label": label, "before": before}
            item["result"] = _safe(label, call)
            item["after"] = _port_state(app, layout, args.port)
            item["valid_ports"] = [
                port for port, info in item["after"]["ports"].items() if _has_valid_hfss_port(info)
            ]
            attempts.append(item)
            if args.stop_on_new_valid:
                requested_valid = [port for port in args.port if port in item["valid_ports"]]
                if requested_valid:
                    break
        payload["attempts"] = attempts
        payload["after"] = _port_state(app, layout, args.port)
        payload["validate_design"] = _safe("ValidateDesign", lambda: app.odesign.ValidateDesign())
        payload["post_validate"] = _port_state(app, layout, args.port)
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
    parser = argparse.ArgumentParser(description="Probe layout port mapping methods.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--target", action="append", default=[])
    parser.add_argument("--refdes", action="append", default=[])
    parser.add_argument("--port", action="append", default=[])
    parser.add_argument("--pin", action="append", default=[])
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--stop-on-new-valid", action="store_true")
    parser.add_argument("--summary", action="store_true", help="Print a compact summary while still writing full JSON to --output.")
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
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    if args.summary:
        attempts = payload.get("attempts", [])
        print(f"status={payload.get('status')} attempts={len(attempts)}")
        for item in attempts:
            result = item.get("result", {})
            print(f"{item.get('label')}: ok={result.get('ok')} value={result.get('value')} error={result.get('error')}")
        after = payload.get("after", {}).get("ports", {})
        hfss = {
            port: info.get("em_design", {}).get("values", {}).get("HFSS Type", {}).get("value")
            for port, info in after.items()
        }
        print(f"after_hfss={hfss}")
        print(f"validate={payload.get('validate_design')}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
