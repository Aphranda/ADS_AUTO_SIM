#!/usr/bin/env python3
"""Probe connector pin terminals in an AEDB through PyEDB without saving."""

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
        elif isinstance(value, dict):
            value = {str(k): _json_default(v) for k, v in value.items()}
        return {"ok": True, "value": value}
    except Exception as exc:  # pragma: no cover - depends on installed EDB runtime.
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "call": label}


def _obj_info(obj: Any) -> dict[str, Any]:
    keys = [
        "name",
        "type",
        "terminal_type",
        "boundary_type",
        "is_reference_terminal",
        "is_circuit_port",
        "impedance",
        "hfss_type",
        "net_name",
        "edb_uid",
        "id",
        "position",
        "location",
    ]
    return {key: _safe(key, lambda key=key: getattr(obj, key)) for key in keys if hasattr(obj, key)}


def _pin_info(pin: Any) -> dict[str, Any]:
    return {
        "info": _obj_info(pin),
        "aedt_name": _safe("aedt_name", lambda: pin.aedt_name),
        "net": _safe("net.name", lambda: pin.net.name),
        "layer_range": _safe("get_layer_range", lambda: pin.get_layer_range()),
        "terminal": _safe("terminal", lambda: pin.terminal),
        "terminal_info": _safe("terminal_info", lambda: _obj_info(pin.terminal)),
    }


def probe(args: argparse.Namespace) -> dict[str, Any]:
    from pyedb import Edb

    edb = Edb(edbpath=str(args.edb), cellname=args.cell, isreadonly=True, version=args.version)
    try:
        payload: dict[str, Any] = {
            "edb": str(args.edb),
            "version": args.version,
            "active_cell": _safe("active_cell.name", lambda: edb.active_cell.name),
            "components_keys": _safe("components.instances.keys", lambda: list(edb.components.instances.keys())),
            "terminals": [],
            "component_details": {},
        }
        for term in edb.layout.terminals:
            payload["terminals"].append(_obj_info(term))
        for component in args.component:
            comp = edb.components.instances.get(component)
            if comp is None:
                payload["component_details"][component] = {
                    "status": "missing",
                    "available_components": payload["components_keys"],
                }
                continue
            payload["component_details"][component] = {
                "info": _obj_info(comp),
                "pins": _safe("pins.keys", lambda comp=comp: list(comp.pins.keys())),
                "pin_details": {},
            }
            for pin_name, pin in comp.pins.items():
                payload["component_details"][component]["pin_details"][pin_name] = _pin_info(pin)
        payload["status"] = "probed"
        return payload
    finally:
        edb.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe connector pin terminals with PyEDB.")
    parser.add_argument("--edb", type=Path, required=True)
    parser.add_argument("--cell", default=None)
    parser.add_argument("--component", action="append", default=[])
    parser.add_argument("--version", default="2026.1")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = probe(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
