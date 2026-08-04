#!/usr/bin/env python3
"""Probe 3D Layout schematic component pins and interface ports through AEDT APIs."""

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


def _component_instances(editor: Any) -> list[str]:
    result = _safe("GetAllComponents", lambda: editor.GetAllComponents())
    return result["value"] if result["ok"] else []


def _parse_component_instance(item: str) -> dict[str, str] | None:
    if not item.startswith("CompInst@"):
        return None
    body = item.removeprefix("CompInst@")
    parts = body.split(";")
    if len(parts) < 2:
        return None
    return {"raw": item, "component": parts[0], "id": parts[1], "suffix": parts[2] if len(parts) > 2 else ""}


def _selection_variants(instance: dict[str, str], suffixes: list[str]) -> list[str]:
    variants = [instance["raw"]]
    for suffix in suffixes:
        value = f"CompInst@{instance['component']};{instance['id']};{suffix}"
        if value not in variants:
            variants.append(value)
    return variants


def _port_names(ports: list[str]) -> list[str]:
    names = []
    for port in ports:
        if port.startswith("IPort@"):
            names.append(port.removeprefix("IPort@").split(";", 1)[0])
        names.append(port)
    return list(dict.fromkeys(names))


def _probe_port(editor: Any, port: str) -> dict[str, Any]:
    item: dict[str, Any] = {"port": port}
    item["port_info"] = _safe(f"GetPortInfo({port})", lambda: editor.GetPortInfo(port))
    for tab in ("BaseElementTab", "SchematicElementTab", "PassedParameterTab"):
        props = _safe(f"GetProperties({tab}, {port})", lambda tab=tab: editor.GetProperties(tab, port))
        item[f"{tab}_properties"] = props
        if props["ok"]:
            values = {}
            for prop in props["value"]:
                values[prop] = _safe(
                    f"GetPropertyValue({tab}, {port}, {prop})",
                    lambda tab=tab, prop=prop: editor.GetPropertyValue(tab, port, prop),
                )
            item[f"{tab}_values"] = values
    return item


def _probe_component(editor: Any, instance: dict[str, str], suffixes: list[str]) -> dict[str, Any]:
    item: dict[str, Any] = dict(instance)
    item["selection_variants"] = {}
    for selection in _selection_variants(instance, suffixes):
        variant: dict[str, Any] = {}
        pins_result = _safe(f"GetComponentPins({selection})", lambda selection=selection: editor.GetComponentPins(selection))
        variant["pins"] = pins_result
        pins = pins_result["value"] if pins_result["ok"] else []
        pin_details = {}
        for pin in pins:
            pin_details[pin] = {
                "info": _safe(
                    f"GetComponentPinInfo({selection}, {pin})",
                    lambda selection=selection, pin=pin: editor.GetComponentPinInfo(selection, pin),
                ),
                "location_true": _safe(
                    f"GetComponentPinLocation({selection}, {pin}, True)",
                    lambda selection=selection, pin=pin: editor.GetComponentPinLocation(selection, pin, True),
                ),
                "location_false": _safe(
                    f"GetComponentPinLocation({selection}, {pin}, False)",
                    lambda selection=selection, pin=pin: editor.GetComponentPinLocation(selection, pin, False),
                ),
            }
        variant["pin_details"] = pin_details
        item["selection_variants"][selection] = variant
    return item


def probe(args: argparse.Namespace) -> dict[str, Any]:
    from ansys.aedt.core import Hfss3dLayout

    app = Hfss3dLayout(
        project=str(args.project),
        design=args.design[0] if args.design else None,
        version=args.version,
        non_graphical=args.non_graphical,
        new_desktop=args.new_desktop,
        close_on_exit=False,
        remove_lock=args.remove_lock,
    )
    try:
        output: dict[str, Any] = {"project": str(args.project), "designs": []}
        for design in args.design:
            design_item: dict[str, Any] = {"design": design}
            app.set_active_design(design)
            editor = app.odesign.SetActiveEditor("SchematicEditor")
            components = _component_instances(editor)
            design_item["components"] = components
            ports_result = _safe("GetAllPorts", lambda: editor.GetAllPorts())
            ports = ports_result["value"] if ports_result["ok"] else []
            design_item["ports"] = ports_result
            nets_result = _safe("GetAllNets", lambda: editor.GetAllNets())
            design_item["nets"] = nets_result
            net_values = nets_result["value"] if nets_result["ok"] else []
            design_item["net_connections"] = {
                net: _safe(f"GetNetConnections({net})", lambda net=net: editor.GetNetConnections(net)) for net in net_values
            }
            design_item["port_details"] = [_probe_port(editor, port) for port in _port_names(ports)]

            parsed = [_parse_component_instance(component) for component in components]
            parsed = [item for item in parsed if item]
            requested_ids = set(args.component_id)
            if requested_ids:
                parsed = [item for item in parsed if item["id"] in requested_ids]
            design_item["component_details"] = [_probe_component(editor, item, args.selection_suffix) for item in parsed]
            output["designs"].append(design_item)
        output["status"] = "probed"
        return output
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe schematic pins and interface ports through AEDT APIs.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", action="append", required=True)
    parser.add_argument("--component-id", action="append", default=[])
    parser.add_argument("--selection-suffix", action="append", default=["395"])
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
