#!/usr/bin/env python3
"""Recreate one connector component-pin port through production HFSS APIs."""

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
from simads.hfss.port_plans import ConnectorPinPortPlan, execute_connector_pin_port_plan
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
        target = source.with_name(f"{source.stem}.before_connector_pin_port_plan_{stamp}{source.suffix}")
        if source.is_dir():
            shutil.copytree(source, target, ignore=ignore_runtime)
        else:
            shutil.copy2(source, target)
        copied.append(str(target))
    return copied


def build_port_plan(args: argparse.Namespace) -> ConnectorPinPortPlan:
    if (args.schematic_safe_x_mil is None) ^ (args.schematic_safe_y_mil is None):
        raise ValueError("--schematic-safe-x-mil and --schematic-safe-y-mil must be provided together")
    return ConnectorPinPortPlan(
        component=args.component,
        component_def=args.component_def,
        component_id=args.component_id,
        raw_component=args.raw_component,
        pin=args.pin,
        port=args.port,
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
        metadata={"source": "tools/hfss/recreate_connector_component_pin_port.py"},
    )


def recreate_connector_component_pin_port(args: argparse.Namespace) -> dict[str, Any]:
    lifecycle = OperationLifecycle(
        "recreate_connector_component_pin_port",
        output=event_log_path_for_json(args.output) if getattr(args, "output", None) else None,
    )
    plan = build_port_plan(args)
    payload: dict[str, Any] = {
        "project": str(args.project),
        "design": args.design,
        "plan": {
            "component": plan.component,
            "component_def": plan.component_def,
            "component_id": plan.component_id,
            "raw_component": plan.raw_component,
            "pin": plan.pin,
            "port": plan.port,
            "elements": plan.element_candidates(),
            "methods": list(plan.methods),
        },
        "execute": args.execute,
        "save": args.save,
    }
    final_lifecycle_status = "failed"
    try:
        if args.backup and args.execute:
            with lifecycle.timed("backup_project"):
                payload["backups"] = _backup_project(args.project)
        session_config = Hfss3dLayoutSessionConfig(
            label="recreate_connector_component_pin_port",
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
            with lifecycle.timed("execute_connector_pin_port_plan"):
                payload["result"] = execute_connector_pin_port_plan(
                    session.app,
                    plan,
                    execute=args.execute,
                    save=args.save,
                    save_project_path=str(args.project),
                )
        payload["status"] = payload["result"].get("status", "unknown")
        final_lifecycle_status = "ok" if payload["status"] in {"dry_run", "created_good_candidate"} else "failed"
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
    parser = argparse.ArgumentParser(
        description=(
            "Delete a bad connector schematic IPort, create the layout connector port from the "
            "connector component pin, move the IPort to a safe schematic location, and wire it "
            "back to the connector pin."
        )
    )
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--component", required=True, help="Layout connector component name.")
    parser.add_argument("--component-def", required=True, help="Connector component definition name.")
    parser.add_argument("--component-id", required=True, help="AEDT component instance id used as CreatePortsOnComponents element.")
    parser.add_argument("--raw-component", required=True, help="Raw schematic selection, for example CompInst@SMA_...;80;8.")
    parser.add_argument("--pin", default="Pin_T1")
    parser.add_argument("--port", required=True, help="Expected generated AEDT port name, for example S2_1_Pin_T1.")
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--element", action="append", default=[], help="Extra CreatePortsOnComponents element candidate. Repeatable.")
    parser.add_argument("--method", action="append", choices=["CreatePortsOnComponents", "CreatePortInstancePorts"], default=["CreatePortsOnComponents"])
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
    payload = recreate_connector_component_pin_port(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if payload.get("status") in {"dry_run", "created_good_candidate"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
