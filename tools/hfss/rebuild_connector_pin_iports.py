#!/usr/bin/env python3
"""Batch rebuild connector pin ports through the production HFSS port plan API."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import shutil
import sys
from typing import Any

_SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.hfss.aedt_startup import OperationLifecycle, apply_grpc_startup_compat
from simads.hfss.artifact_names import event_log_path_for_json
from simads.hfss.port_plans import (
    ConnectorPinPortPlan,
    connector_port_acceptance_report,
    execute_connector_pin_port_plan,
)
from simads.hfss.session import Hfss3dLayoutSessionConfig, open_hfss3dlayout_session

apply_grpc_startup_compat()


def _json_default(value: Any) -> str:
    return str(value)


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
        target = source.with_name(f"{source.stem}.before_rebuild_connector_pin_iports_{stamp}{source.suffix}")
        if source.is_dir():
            shutil.copytree(source, target, ignore=ignore_runtime)
        else:
            shutil.copy2(source, target)
        copied.append(str(target))
    return copied


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
    return {
        "raw": item,
        "component": parts[0],
        "id": parts[1],
        "suffix": parts[2] if len(parts) > 2 else "",
    }


def _instances_by_id(editor: Any) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for item in _component_instances(editor):
        parsed = _parse_component_instance(item)
        if parsed:
            output[parsed["id"]] = parsed
    return output


def _first_pin(editor: Any, selection: str) -> str | None:
    try:
        pins = [str(item) for item in editor.GetComponentPins(selection)]
    except Exception:
        return None
    return pins[0] if pins else None


def _value_at(values: list[str], index: int, *, default: str | None = None, repeat_single: bool = False) -> str | None:
    if not values:
        return default
    if len(values) == 1 and repeat_single:
        return values[0]
    if index < len(values):
        return values[index]
    return default


def _validate_repeated_arg_lengths(args: argparse.Namespace) -> list[str]:
    errors: list[str] = []
    count = len(args.component_id)
    aligned = {
        "--delete-port": args.delete_port,
        "--expected-port": args.expected_port,
        "--component": args.component,
        "--component-def": args.component_def,
        "--raw-component": args.raw_component,
    }
    for label, values in aligned.items():
        if values and len(values) not in {1, count}:
            errors.append(f"{label} count must be 1 or match --component-id count ({count}); got {len(values)}")
    if args.pin and len(args.pin) not in {1, count}:
        errors.append(f"--pin count must be 1 or match --component-id count ({count}); got {len(args.pin)}")
    return errors


def build_port_plans(args: argparse.Namespace, app: Any) -> tuple[list[ConnectorPinPortPlan], list[dict[str, Any]], list[str]]:
    errors = _validate_repeated_arg_lengths(args)
    if (args.schematic_safe_x_mil is None) ^ (args.schematic_safe_y_mil is None):
        errors.append("--schematic-safe-x-mil and --schematic-safe-y-mil must be provided together")
    if args.add_method != "add-pin":
        errors.append(
            f"--add-method {args.add_method} is a legacy diagnostic path; production rebuild uses ConnectorPinPortPlan"
        )

    editor = app.odesign.SetActiveEditor("SchematicEditor")
    by_id = _instances_by_id(editor)
    plans: list[ConnectorPinPortPlan] = []
    selected: list[dict[str, Any]] = []
    for index, component_id in enumerate(args.component_id):
        instance = by_id.get(str(component_id))
        raw_component = _value_at(args.raw_component, index)
        component = _value_at(args.component, index)
        component_def = _value_at(args.component_def, index, repeat_single=True)
        if instance:
            raw_component = raw_component or instance["raw"]
            component = component or instance["component"]
            component_def = component_def or instance["component"]

        port = _value_at(args.expected_port, index) or _value_at(args.delete_port, index)
        pin = _value_at(args.pin, index, default=None, repeat_single=True)
        if raw_component and not pin:
            pin = _first_pin(editor, raw_component)
        pin = pin or "Pin_T1"

        item: dict[str, Any] = {
            "index": index,
            "component_id": component_id,
            "raw_component": raw_component,
            "component": component,
            "component_def": component_def,
            "pin": pin,
            "port": port,
            "inferred_from_schematic": bool(instance),
        }
        missing = [
            name
            for name, value in {
                "raw_component": raw_component,
                "component": component,
                "component_def": component_def,
                "port": port,
            }.items()
            if not value
        ]
        if missing:
            item["status"] = "missing_metadata"
            item["missing"] = missing
            errors.append(f"component-id {component_id} missing {', '.join(missing)}")
            selected.append(item)
            continue

        plan = ConnectorPinPortPlan(
            component=str(component),
            component_def=str(component_def),
            component_id=str(component_id),
            raw_component=str(raw_component),
            pin=str(pin),
            port=str(port),
            page=args.page,
            elements=tuple(args.element),
            methods=tuple(args.method),
            delete_iport=args.delete_iport,
            connect_schematic=args.connect_schematic,
            move_schematic_iport=args.move_schematic_iport,
            delete_old_schematic_wires=args.delete_old_schematic_wires,
            schematic_safe_x_mil=args.schematic_safe_x_mil,
            schematic_safe_y_mil=args.schematic_safe_y_mil,
            schematic_safe_min_clearance_mil=args.schematic_safe_min_clearance_mil,
            schematic_safe_grid_start_x_mil=args.schematic_safe_grid_start_x_mil,
            schematic_safe_grid_start_y_mil=args.schematic_safe_grid_start_y_mil,
            schematic_safe_grid_step_mil=args.schematic_safe_grid_step_mil,
            schematic_safe_grid_count=args.schematic_safe_grid_count,
            metadata={"source": "tools/hfss/rebuild_connector_pin_iports.py", "batch_index": index},
        )
        item["status"] = "planned"
        item["elements"] = plan.element_candidates()
        item["methods"] = list(plan.methods)
        selected.append(item)
        plans.append(plan)
    return plans, selected, errors


def rebuild_iports(args: argparse.Namespace) -> dict[str, Any]:
    lifecycle = OperationLifecycle(
        "rebuild_connector_pin_iports",
        output=event_log_path_for_json(args.output) if getattr(args, "output", None) else None,
    )
    payload: dict[str, Any] = {
        "project": str(args.project),
        "design": args.design,
        "delete_ports": args.delete_port,
        "component_ids": args.component_id,
        "expected_ports": args.expected_port,
        "execute": args.execute,
        "save": args.save,
    }
    final_lifecycle_status = "failed"
    try:
        if args.backup and args.execute:
            with lifecycle.timed("backup_project"):
                payload["backups"] = _backup_project(args.project)
        session_config = Hfss3dLayoutSessionConfig(
            label="rebuild_connector_pin_iports",
            project=args.project,
            design=args.design,
            version=args.version,
            non_graphical=args.non_graphical,
            new_desktop=args.new_desktop,
            close_on_exit=False,
            keep_open=args.keep_attached,
            close_projects=args.close_projects,
            close_desktop=args.close_desktop,
            remove_lock=args.remove_lock,
            ready_timeout_s=args.ready_timeout_s,
            ready_settle_s=args.ready_settle_s,
        )
        with open_hfss3dlayout_session(session_config, lifecycle) as session:
            payload.update(session.metadata())
            with lifecycle.timed("build_connector_pin_port_plans"):
                plans, selected, errors = build_port_plans(args, session.app)
            payload["selected"] = selected
            if errors:
                payload["status"] = "invalid_plan"
                payload["errors"] = errors
                final_lifecycle_status = "failed"
                return payload
            results = []
            with lifecycle.timed("execute_connector_pin_port_plans"):
                for plan in plans:
                    result = execute_connector_pin_port_plan(
                        session.app,
                        plan,
                        execute=args.execute,
                        save=False,
                        save_project_path=str(args.project),
                    )
                    results.append(result)
                    if result.get("status") not in {"dry_run", "created_good_candidate"}:
                        payload["results"] = results
                        payload["status"] = "batch_failed_not_saved"
                        final_lifecycle_status = "failed"
                        return payload
            payload["results"] = results
            payload["acceptance_report"] = connector_port_acceptance_report(session.app, tuple(plans))
            if args.save and args.execute:
                with lifecycle.timed("save_project"):
                    payload["saved"] = bool(session.app.save_project(str(args.project), overwrite=True))
            payload["status"] = "dry_run" if not args.execute else "rebuilt"
            final_lifecycle_status = "ok"
            return payload
    except BaseException as exc:
        payload["status"] = "failed"
        payload["error_type"] = type(exc).__name__
        payload["error"] = str(exc)
        final_lifecycle_status = "failed"
        return payload
    finally:
        if "lifecycle" not in payload:
            payload["lifecycle"] = lifecycle.finish(status=final_lifecycle_status)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch rebuild connector pin ports through ConnectorPinPortPlan.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--delete-port", action="append", required=True)
    parser.add_argument("--component-id", action="append", required=True)
    parser.add_argument("--expected-port", action="append", default=[])
    parser.add_argument("--component", action="append", default=[], help="Layout connector component name. Repeatable.")
    parser.add_argument("--component-def", action="append", default=[], help="Connector component definition name. Repeatable.")
    parser.add_argument("--raw-component", action="append", default=[], help="Raw schematic CompInst selection. Repeatable.")
    parser.add_argument("--pin", action="append", default=[], help="Connector pin name. Repeatable; defaults to schematic first pin.")
    parser.add_argument("--element", action="append", default=[], help="Extra CreatePortsOnComponents element candidate. Repeatable.")
    parser.add_argument("--method", action="append", choices=["CreatePortsOnComponents", "CreatePortInstancePorts"], default=["CreatePortsOnComponents"])
    parser.add_argument(
        "--add-method",
        choices=["add-pin", "create-iport-existing", "create-iport-pin"],
        default="add-pin",
        help="Compatibility option. Production execution only supports add-pin/ConnectorPinPortPlan.",
    )
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--keep-existing-iport", action="store_false", dest="delete_iport")
    parser.set_defaults(delete_iport=True)
    parser.add_argument("--no-connect-schematic", action="store_false", dest="connect_schematic")
    parser.set_defaults(connect_schematic=True)
    parser.add_argument("--no-move-schematic-iport", action="store_false", dest="move_schematic_iport")
    parser.set_defaults(move_schematic_iport=True)
    parser.add_argument("--keep-old-schematic-wires", action="store_false", dest="delete_old_schematic_wires")
    parser.set_defaults(delete_old_schematic_wires=True)
    parser.add_argument("--schematic-safe-x-mil", type=float, default=None)
    parser.add_argument("--schematic-safe-y-mil", type=float, default=None)
    parser.add_argument("--schematic-safe-min-clearance-mil", type=float, default=250.0)
    parser.add_argument("--schematic-safe-grid-start-x-mil", type=float, default=-4000.0)
    parser.add_argument("--schematic-safe-grid-start-y-mil", type=float, default=-4000.0)
    parser.add_argument("--schematic-safe-grid-step-mil", type=float, default=1000.0)
    parser.add_argument("--schematic-safe-grid-count", type=int, default=9)
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
    parser.add_argument("--ready-timeout-s", type=float, default=120.0)
    parser.add_argument("--ready-settle-s", type=float, default=3.0)
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
