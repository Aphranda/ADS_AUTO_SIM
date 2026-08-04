#!/usr/bin/env python3
"""Try shaping a layout port's EM properties to match a reference port."""

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
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "call": label}


def _props(editor: Any, port: str) -> dict[str, Any]:
    server = f"Excitations:{port}"
    props = _safe(f"GetProperties(EM Design, {server})", lambda: editor.GetProperties("EM Design", server))
    values = {}
    if props["ok"]:
        for prop in props["value"]:
            values[prop] = _safe(
                f"GetPropertyValue(EM Design, {server}, {prop})",
                lambda prop=prop: editor.GetPropertyValue("EM Design", server, prop),
            )
    return {"properties": props, "values": values}


def try_shape(args: argparse.Namespace) -> dict[str, Any]:
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
        editor = app.odesign.SetActiveEditor("Layout")
        payload: dict[str, Any] = {
            "project": str(args.project),
            "design": args.design,
            "target": args.target,
            "reference": args.reference,
            "before_target": _props(editor, args.target),
            "before_reference": _props(editor, args.reference),
            "execute": args.execute,
            "save": args.save,
        }
        if not args.execute:
            payload["status"] = "dry_run"
            return payload
        calls = []
        calls.append(
            _safe(
                "Layout.ChangeProperty delete Gap props",
                lambda: editor.ChangeProperty(
                    [
                        "NAME:AllTabs",
                        [
                            "NAME:EM Design",
                            ["NAME:PropServers", f"Excitations:{args.target}"],
                            ["NAME:DeletedProps", "Reference", "HFSS Type", "Orientation"],
                        ],
                    ]
                ),
            )
        )
        calls.append(
            _safe(
                "Layout.ChangeProperty add Override Impedance",
                lambda: editor.ChangeProperty(
                    [
                        "NAME:AllTabs",
                        [
                            "NAME:EM Design",
                            ["NAME:PropServers", f"Excitations:{args.target}"],
                            [
                                "NAME:NewProps",
                                [
                                    "NAME:Override Impedance",
                                    "PropType:=",
                                    "CheckboxProp",
                                    "OverridingDef:=",
                                    True,
                                    "Value:=",
                                    False,
                                ],
                            ],
                        ],
                    ]
                ),
            )
        )
        calls.append(
            _safe(
                "ChangePortProperty delete Gap props",
                lambda: app.odesign.ChangePortProperty(
                    args.target,
                    [f"NAME:{args.target}", "IIPortName:=", args.target],
                    [["NAME:Properties", [], ["NAME:DeletedProps", "Reference", "HFSS Type", "Orientation"]]],
                ),
            )
        )
        payload["calls"] = calls
        payload["after_target"] = _props(editor, args.target)
        if args.save:
            payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
        payload["status"] = "shaped"
        return payload
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Try shaping port properties.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--save", action="store_true")
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
    payload = try_shape(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if payload.get("status") in {"dry_run", "shaped"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
