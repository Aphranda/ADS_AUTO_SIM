#!/usr/bin/env python3
"""Delete and recreate connector pin interface ports through AEDT APIs."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import shutil
from typing import Any


def _json_default(value: Any) -> str:
    return str(value)


def _project_sidecars(project: Path) -> list[Path]:
    paths = [project]
    for suffix in [".aedb", ".aedtresults"]:
        sidecar = project.with_suffix(suffix)
        if sidecar.exists():
            paths.append(sidecar)
    return paths


def _backup_project(project: Path) -> list[str]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    copied: list[str] = []
    ignore_runtime_locks = shutil.ignore_patterns("*.semaphore", "*.lock", "*.tmp")
    for src in _project_sidecars(project):
        dst = src.with_name(f"{src.stem}.before_rebuild_pin_iports_{stamp}{src.suffix}")
        if src.is_dir():
            shutil.copytree(src, dst, ignore=ignore_runtime_locks)
        else:
            shutil.copy2(src, dst)
        copied.append(str(dst))
    return copied


def _ports_from_editor(editor: Any) -> list[str]:
    try:
        return [str(item) for item in editor.GetAllPorts()]
    except Exception:
        return []


def _port_name(port: str) -> str:
    if not port.startswith("IPort@"):
        return port
    body = port.removeprefix("IPort@")
    return body.split(";", 1)[0]


def _parse_key_values(values: Any) -> dict[str, str]:
    output: dict[str, str] = {}
    if not isinstance(values, (list, tuple)):
        return output
    for item in values:
        text = str(item)
        if "=" in text:
            key, value = text.split("=", 1)
            output[key] = value
    return output


def _float_value(values: dict[str, str], key: str, default: float = 0.0) -> float:
    try:
        return float(values.get(key, default))
    except (TypeError, ValueError):
        return default


def _port_info(editor: Any, port: str) -> dict[str, Any]:
    try:
        raw = [str(item) for item in editor.GetPortInfo(port)]
    except Exception as exc:
        return {"port": port, "error": repr(exc)}
    values = _parse_key_values(raw)
    return {
        "port": port,
        "name": values.get("Name", _port_name(port)),
        "raw": raw,
        "x": _float_value(values, "X"),
        "y": _float_value(values, "Y"),
        "angle": _float_value(values, "Angle"),
        "wire_id": values.get("WireId"),
    }


def _component_pin_info(editor: Any, selection: str, pin: str) -> dict[str, Any]:
    try:
        raw = [str(item) for item in editor.GetComponentPinInfo(selection, pin)]
    except Exception as exc:
        return {"selection": selection, "pin": pin, "error": repr(exc)}
    values = _parse_key_values(raw)
    return {
        "selection": selection,
        "pin": pin,
        "raw": raw,
        "x": _float_value(values, "X"),
        "y": _float_value(values, "Y"),
        "angle": _float_value(values, "Angle"),
        "wire_id": values.get("WireId"),
    }


def _component_instances(editor: Any) -> list[str]:
    try:
        return [str(item) for item in editor.GetAllComponents()]
    except Exception:
        return []


def _parse_component_instance(item: str) -> dict[str, str] | None:
    if not item.startswith("CompInst@"):
        return None
    body = item.removeprefix("CompInst@")
    parts = body.split(";")
    if len(parts) < 2:
        return None
    return {"raw": item, "component": parts[0], "id": parts[1], "suffix": parts[2] if len(parts) > 2 else ""}


def _instances_by_id(editor: Any) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for item in _component_instances(editor):
        parsed = _parse_component_instance(item)
        if parsed:
            output[parsed["id"]] = parsed
    return output


def _selection_for(instance: dict[str, str], *, suffix: str) -> str:
    if suffix.lower() == "raw":
        return instance["raw"]
    return f"CompInst@{instance['component']};{instance['id']};{suffix}"


def _create_iport(editor: Any, *, name: str, x: float, y: float, angle: float, page: int) -> Any:
    return editor.CreateIPort(
        ["NAME:IPortProps", "Name:=", name],
        ["NAME:Attributes", "Page:=", page, "X:=", x, "Y:=", y, "Angle:=", angle, "Flip:=", False],
    )


def _first_pin(editor: Any, selection: str) -> str | None:
    try:
        pins = [str(item) for item in editor.GetComponentPins(selection)]
    except Exception:
        return None
    return pins[0] if pins else None


def rebuild_iports(args: argparse.Namespace) -> dict[str, Any]:
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
        before_ports = _ports_from_editor(editor)
        delete_targets = [port for port in before_ports if _port_name(port) in set(args.delete_port)]
        by_id = _instances_by_id(editor)
        selected: list[dict[str, Any]] = []
        for component_id in args.component_id:
            instance = by_id.get(str(component_id))
            if not instance:
                selected.append({"component_id": component_id, "status": "missing"})
                continue
            selected.append(
                {
                    "component": instance["component"],
                    "id": instance["id"],
                    "raw": instance["raw"],
                    "selection": _selection_for(instance, suffix=args.selection_suffix),
                    "status": "selected",
                }
            )

        payload: dict[str, Any] = {
            "project": str(args.project),
            "design": args.design,
            "delete_ports": args.delete_port,
            "before_ports": before_ports,
            "delete_targets": delete_targets,
            "before_port_info": [_port_info(editor, port) for port in delete_targets],
            "component_ids": args.component_id,
            "selection_suffix": args.selection_suffix,
            "selected": selected,
            "expected_ports": args.expected_port,
            "add_method": args.add_method,
            "execute": args.execute,
            "save": args.save,
        }
        if len(delete_targets) != len(args.delete_port):
            payload["status"] = "delete_ports_missing"
            return payload
        missing = [item for item in selected if item["status"] == "missing"]
        if missing:
            payload["status"] = "missing_components"
            return payload
        if not args.execute:
            payload["status"] = "dry_run"
            return payload

        for item in selected:
            pin = _first_pin(editor, item["selection"])
            item["pin"] = pin
            item["pin_info"] = _component_pin_info(editor, item["selection"], pin) if pin else None

        if args.backup:
            payload["backups"] = _backup_project(args.project)

        delete_result = editor.Delete(["NAME:Selections", "Selections:=", delete_targets])
        payload["delete_result"] = _json_default(delete_result)
        ports_after_delete = _ports_from_editor(editor)
        payload["ports_after_delete"] = ports_after_delete

        selections = [item["selection"] for item in selected]
        if args.add_method == "create-iport-existing":
            port_infos = payload["before_port_info"]
            if len(args.expected_port) != len(port_infos):
                payload["status"] = "expected_port_count_mismatch_not_saved"
                return payload
            create_results = []
            for name, info in zip(args.expected_port, port_infos, strict=True):
                result = _create_iport(editor, name=name, x=info["x"], y=info["y"], angle=info["angle"], page=args.page)
                create_results.append({"name": name, "source": info, "result": _json_default(result)})
            payload["create_iport_results"] = create_results
        elif args.add_method == "create-iport-pin":
            if len(args.expected_port) != len(selected):
                payload["status"] = "expected_port_count_mismatch_not_saved"
                return payload
            create_results = []
            for name, item in zip(args.expected_port, selected, strict=True):
                info = item.get("pin_info") or {}
                if "error" in info or item.get("pin") is None:
                    payload["status"] = "pin_info_missing_not_saved"
                    return payload
                angle = args.create_angle if args.create_angle is not None else float(info["angle"])
                result = _create_iport(editor, name=name, x=float(info["x"]), y=float(info["y"]), angle=angle, page=args.page)
                create_results.append({"name": name, "source": info, "result": _json_default(result)})
            payload["create_iport_results"] = create_results
        elif args.per_component:
            add_results = []
            for selection in selections:
                result = editor.AddPinIPorts(["Name:Selections", "Selections:=", [selection]])
                add_results.append({"selection": selection, "result": _json_default(result), "ports": _ports_from_editor(editor)})
            payload["add_pin_iports_results"] = add_results
        else:
            add_result = editor.AddPinIPorts(["Name:Selections", "Selections:=", selections])
            payload["add_pin_iports_result"] = _json_default(add_result)
        after_ports = _ports_from_editor(editor)
        payload["after_ports"] = after_ports
        payload["new_ports"] = [port for port in after_ports if port not in ports_after_delete]
        payload["after_port_info"] = [_port_info(editor, port) for port in after_ports]
        payload["after_pin_info"] = [
            _component_pin_info(editor, item["selection"], item["pin"])
            for item in selected
            if item.get("pin")
        ]

        after_names = {_port_name(port) for port in after_ports}
        expected = set(args.expected_port)
        if expected and not expected.issubset(after_names):
            payload["status"] = "expected_ports_missing_not_saved"
            payload["missing_expected_ports"] = sorted(expected - after_names)
            return payload

        if args.save:
            payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
        payload["status"] = "rebuilt"
        return payload
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Delete and recreate connector pin interface ports.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--delete-port", action="append", required=True)
    parser.add_argument("--component-id", action="append", required=True)
    parser.add_argument("--expected-port", action="append", default=[])
    parser.add_argument(
        "--add-method",
        choices=["add-pin", "create-iport-existing", "create-iport-pin"],
        default="add-pin",
    )
    parser.add_argument("--selection-suffix", default="raw", help="Use 'raw' for the component selection returned by AEDT.")
    parser.add_argument("--per-component", action="store_true", help="Call AddPinIPorts once for each component selection.")
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--create-angle", type=float, default=None)
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
    payload = rebuild_iports(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if payload.get("status") in {"dry_run", "rebuilt"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
