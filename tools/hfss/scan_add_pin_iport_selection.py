#!/usr/bin/env python3
"""Scan schematic AddPinIPorts selection suffixes without saving."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _json_default(value: Any) -> str:
    return str(value)


def _ports(editor: Any) -> list[str]:
    try:
        return [str(item) for item in editor.GetAllPorts()]
    except Exception:
        return []


def _pin_info(editor: Any, selection: str, pin: str) -> list[str] | str:
    try:
        return [str(item) for item in editor.GetComponentPinInfo(selection, pin)]
    except Exception as exc:
        return repr(exc)


def scan(args: argparse.Namespace) -> dict[str, Any]:
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
        editor = app.odesign.SetActiveEditor("SchematicEditor")
        before = _ports(editor)
        delete_targets = [port for port in before if port.startswith(f"IPort@{args.delete_port};")]
        payload: dict[str, Any] = {
            "project": str(args.project),
            "design": args.design,
            "component": args.component,
            "component_id": args.component_id,
            "delete_port": args.delete_port,
            "before_ports": before,
            "delete_targets": delete_targets,
            "execute": args.execute,
            "save": args.save,
        }
        if not args.execute:
            payload["status"] = "dry_run"
            return payload
        if delete_targets:
            payload["delete_result"] = _json_default(editor.Delete(["NAME:Selections", "Selections:=", delete_targets]))
        payload["after_delete_ports"] = _ports(editor)

        attempts = []
        base_raw = f"CompInst@{args.component};{args.component_id};{args.raw_suffix}"
        suffixes = list(args.suffix)
        if args.suffix_start is not None and args.suffix_end is not None:
            suffixes.extend(str(item) for item in range(args.suffix_start, args.suffix_end + 1))
        suffixes = list(dict.fromkeys(suffixes))
        for suffix in suffixes:
            selection = f"CompInst@{args.component};{args.component_id};{suffix}"
            item: dict[str, Any] = {"suffix": suffix, "selection": selection}
            try:
                item["pins"] = [str(pin) for pin in editor.GetComponentPins(selection)]
            except Exception as exc:
                item["pins_error"] = repr(exc)
            before_attempt = _ports(editor)
            try:
                result = editor.AddPinIPorts(["Name:Selections", "Selections:=", [selection]])
                item["result"] = _json_default(result)
            except Exception as exc:
                item["error"] = repr(exc)
            after_attempt = _ports(editor)
            item["after_ports"] = after_attempt
            item["new_ports"] = [port for port in after_attempt if port not in before_attempt]
            item["raw_pin_info"] = _pin_info(editor, base_raw, args.pin)
            attempts.append(item)
            if item["new_ports"]:
                payload["attempts"] = attempts
                payload["status"] = "created_candidate"
                if args.save:
                    payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
                return payload
        payload["attempts"] = attempts
        payload["status"] = "no_candidate_created"
        return payload
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan AddPinIPorts selection suffixes.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--component", required=True)
    parser.add_argument("--component-id", required=True)
    parser.add_argument("--raw-suffix", required=True)
    parser.add_argument("--pin", default="Pin_T1")
    parser.add_argument("--delete-port", required=True)
    parser.add_argument("--suffix", action="append", default=[])
    parser.add_argument("--suffix-start", type=int, default=None)
    parser.add_argument("--suffix-end", type=int, default=None)
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
    payload = scan(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if payload.get("status") in {"dry_run", "created_candidate"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
