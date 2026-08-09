#!/usr/bin/env python3
"""Create a small HFSS 3D Layout project through AEDT APIs for smoke tests."""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from argparse import Namespace
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from simads.hfss.aedt_startup import OperationLifecycle, apply_grpc_startup_compat, prepare_aedt_project_lock
from simads.hfss.artifact_names import event_log_path_for_json
from simads.hfss.build import build_hfss_layout_project
from simads.hfss.session import Hfss3dLayoutSessionConfig, open_hfss3dlayout_session

apply_grpc_startup_compat()

AEDT_VERSION = "2026.1"
DEFAULT_RUN_ROOT = REPO_ROOT / ".simads" / "aedt_smoke"


def _json_default(value: Any) -> str:
    return str(value)


def _default_output() -> Path:
    stamp = time.strftime("%Y%m%d_%H%M%S")
    return DEFAULT_RUN_ROOT / f"hfss3dlayout_api_smoke_{stamp}.json"


def _smoke_layout() -> dict[str, Any]:
    return {
        "metadata": {
            "layout_id": "hfss3dlayout_api_smoke",
            "er": 4.6,
            "loss_tangent": 0.02,
            "dielectric_height_mm": 0.21,
            "copper_thickness_mm": 0.035,
        },
        "ports": [],
        "shapes": [
            {
                "kind": "boundary",
                "layer": "EM_BOUNDARY",
                "name": "smoke_boundary",
                "x": -2.0,
                "y": -1.0,
                "w": 4.0,
                "h": 2.0,
            },
            {
                "kind": "rect",
                "layer": "cond",
                "name": "smoke_signal_trace",
                "x": -1.0,
                "y": -0.05,
                "w": 2.0,
                "h": 0.1,
                "metadata": {"net": "SMOKE"},
            },
        ],
    }


def _build_args(args: argparse.Namespace) -> Namespace:
    return Namespace(
        er=None,
        loss_tangent=None,
        substrate_height_mm=None,
        copper_thickness_mm=None,
        gnd_boundary_mode="em-boundary",
        signal_layer="TOP",
        reference_ground_layer="GND",
        via_top_layer="TOP",
        via_bottom_layer="GND",
        ground_plane_name="hfss_ground_plane",
        configure_extents=True,
        diel_extent_type="BboxExtent",
        diel_horizontal_padding="0.005",
        diel_honor_primitives=True,
        include_3d_subdesigns=False,
        airbox_extent_type="BboxExtent",
        truncate_airbox_at_ground=False,
        airbox_horizontal_padding="0.15",
        airbox_vertical_positive_padding="2",
        airbox_vertical_negative_padding="2",
        airbox_vertical_sync=True,
        open_region_type="Radiation",
        use_radiation_boundary=True,
        pml_visible=False,
        open_region_frequency_ghz=5.0,
        radiation_factor=0.0,
        skip_ports=True,
        setup=args.setup,
        sweep=args.sweep,
        mesh_size_factor=2.0,
        enable_design_intersection_check=False,
        adaptive_frequency_ghz=args.adaptive_frequency_ghz,
        start_ghz=args.start_ghz,
        stop_ghz=args.stop_ghz,
        points=args.points,
        sweep_type="Interpolating",
        interpolation_tol_percent=0.5,
        interpolation_max_solutions=80,
        build_only=True,
        design=args.design,
    )


def _object_names(items: Any) -> list[str]:
    names: list[str] = []
    for item in items or []:
        names.append(getattr(item, "name", str(item)))
    return names


def _safe_messages(app: Any) -> list[str]:
    try:
        project_name = str(getattr(app, "project_name", "") or "")
        design_name = str(getattr(app, "design_name", "") or "")
        desktop = getattr(app, "odesktop", None)
        if desktop is not None:
            output: list[str] = []
            output.extend(str(message) for message in desktop.GetMessages("", "", 0))
            if project_name:
                output.extend(str(message) for message in desktop.GetMessages(project_name, "", 0))
            if project_name and design_name:
                output.extend(str(message) for message in desktop.GetMessages(project_name, design_name, 0))
            return list(dict.fromkeys(output))
    except Exception as exc:
        return [f"failed to read AEDT messages: {type(exc).__name__}: {exc}"]
    return []


def run(args: argparse.Namespace) -> dict[str, Any]:
    started = time.monotonic()
    project = args.project.resolve()
    output = args.output.resolve()
    event_log = event_log_path_for_json(output)
    lifecycle = OperationLifecycle("create_hfss3dlayout_smoke_project", output=event_log)
    project.parent.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    app = None
    session_metadata: dict[str, Any] = {}
    final_status = "failed"
    payload: dict[str, Any] = {
        "status": "starting",
        "project": str(project),
        "design": args.design,
        "version": args.version,
        "non_graphical": args.non_graphical,
        "new_desktop": True,
        "output": str(output),
        "event_log": str(event_log),
    }
    try:
        with lifecycle.timed("prepare_smoke_output_lock"):
            payload["smoke_output_lock"] = prepare_aedt_project_lock(
                project,
                force_remove=args.force_remove_project_lock,
            )
        session_config = Hfss3dLayoutSessionConfig(
            label="create_hfss3dlayout_smoke_project",
            project=project if args.reuse_project and project.exists() else None,
            design=args.design,
            version=args.version,
            non_graphical=args.non_graphical,
            new_desktop=True,
            close_on_exit=False,
            keep_open=args.keep_open,
            close_projects=True,
            close_desktop=True,
            wait_ready=True,
            ready_timeout_s=args.ready_timeout_s,
            ready_settle_s=args.ready_settle_s,
            force_remove_project_lock=args.force_remove_project_lock,
        )
        with open_hfss3dlayout_session(session_config, lifecycle) as session:
            app = session.app
            session_metadata = session.metadata()
            payload.update(session_metadata)
            with lifecycle.timed("build_minimal_project"):
                result = build_hfss_layout_project(
                    app,
                    _smoke_layout(),
                    _build_args(args),
                    project_path=project,
                    stackup_config=None,
                ).to_dict()
            with lifecycle.timed("read_back_project_state"):
                payload.update(
                    {
                        "status": "ok",
                        "stage": "completed",
                        "build": result,
                        "project_exists": project.exists(),
                        "project_name": getattr(app, "project_name", None),
                        "design_name": getattr(app, "design_name", None),
                        "design_type": getattr(app, "design_type", None),
                        "setup_names": list(getattr(app, "setup_names", []) or []),
                        "ports": _object_names(getattr(app, "ports", [])),
                        "port_list": list(getattr(app, "port_list", []) or []),
                        "messages": _safe_messages(app),
                    }
                )
        final_status = "ok"
        return payload
    except BaseException as exc:
        payload.update(
            {
                "status": "failed",
                "stage": payload.get("stage", "unknown"),
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "messages": _safe_messages(app),
            }
        )
        payload.update({key: value for key, value in session_metadata.items() if value is not None})
        return payload
    finally:
        payload["elapsed_s"] = round(time.monotonic() - started, 3)
        payload["lifecycle"] = lifecycle.finish(status=final_status)
        text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
        output.write_text(text + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a minimal HFSS 3D Layout smoke-test project via AEDT API.")
    parser.add_argument("--project", type=Path, default=DEFAULT_RUN_ROOT / "hfss3dlayout_api_smoke.aedt")
    parser.add_argument("--design", default="HFSS3DLayout_API_SMOKE")
    parser.add_argument("--version", default=AEDT_VERSION)
    parser.add_argument("--setup", default="Setup_4to10G")
    parser.add_argument("--sweep", default="Sweep_4to10G_21pt")
    parser.add_argument("--start-ghz", type=float, default=4.0)
    parser.add_argument("--stop-ghz", type=float, default=10.0)
    parser.add_argument("--points", type=int, default=21)
    parser.add_argument("--adaptive-frequency-ghz", type=float, default=7.0)
    parser.add_argument("--ready-timeout-s", type=float, default=120.0)
    parser.add_argument("--ready-settle-s", type=float, default=2.0)
    parser.add_argument("--non-graphical", action="store_true", default=True)
    parser.add_argument("--graphical", action="store_false", dest="non_graphical")
    parser.add_argument("--keep-open", action="store_true")
    parser.add_argument("--reuse-project", action="store_true", help="Open the existing smoke project instead of creating a fresh project.")
    parser.add_argument("--force-remove-project-lock", action="store_true")
    parser.add_argument("--output", type=Path, default=_default_output())
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = run(args)
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default))
    return 0 if payload.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
