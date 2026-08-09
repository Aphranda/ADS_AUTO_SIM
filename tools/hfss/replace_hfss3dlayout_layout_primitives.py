#!/usr/bin/env python3
"""Replace HFSS 3D Layout PCB primitives without touching connector objects.

This tool is for connector launch tuning after the SMA component has already
been fixed in AEDT. The production flow always deletes the existing source PCB
layout, draws the new layout from JSON, and recreates only the PCB remote edge
port. Candidate iteration must not call incremental or candidate-specific
boolean operations against the existing AEDT layout.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

_SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.hfss.aedt_startup import (
    OperationLifecycle,
    apply_grpc_startup_compat,
)
from simads.hfss.layout import GeometryBuildOptions, create_geometry
from simads.hfss.layout_cleanup import (
    delete_layout_objects,
    full_rebuild_delete_names,
    existing_layout_objects,
    resolve_existing_delete_names_and_prefixes,
    selected_shapes as select_layout_shapes,
    shape_name,
    sibling_layout_root,
    TEMPORARY_CLIP_FRAME_PREFIXES,
)
from simads.hfss.layout_io import load_layout
from simads.hfss.ports import (
    apply_aedt_edge_gap_port_template,
    default_port_reference_name,
    delete_schematic_iports_by_name,
    infer_port_edge,
    schematic_iport_names,
)
from simads.hfss.session import Hfss3dLayoutSessionConfig, open_hfss3dlayout_session

apply_grpc_startup_compat()


def _json_default(value: Any) -> str:
    return str(value)


def _pcb_port_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        signal_layer=args.signal_layer,
        reference_ground_layer=args.reference_ground_layer,
        ground_plane_name=args.ground_plane_name,
        port_reference_name=args.port_reference_name,
        port_horizontal_extent_factor=args.port_horizontal_extent_factor,
        port_vertical_extent_factor=args.port_vertical_extent_factor,
        port_radial_extent_factor=args.port_radial_extent_factor,
        port_pec_launch_width=args.port_pec_launch_width,
    )


def _create_pcb_output_port(app: Any, layout: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    p2_edge, p2_side = infer_port_edge(layout, "output_feed", 2)
    created = app.create_edge_port("output_feed", p2_edge, is_circuit_port=False)
    port_name = getattr(created, "name", str(created)) if created else ""
    return {
        "logical_port": "P2",
        "primitive": "output_feed",
        "edge": p2_edge,
        "side": p2_side,
        "created_port_name": port_name,
        "template": apply_aedt_edge_gap_port_template(app, port_name, _pcb_port_args(args)) if port_name else {},
    }


def replace_layout_primitives(args: argparse.Namespace) -> dict[str, Any]:
    lifecycle = OperationLifecycle(
        "replace_hfss3dlayout_layout_primitives",
        output=args.output.with_suffix(".events.jsonl") if getattr(args, "output", None) else None,
    )
    layout = load_layout(args.layout)
    geometry = GeometryBuildOptions(
        gnd_boundary_mode=args.gnd_boundary_mode,
        signal_layer=args.signal_layer,
        reference_ground_layer=args.reference_ground_layer,
        via_top_layer=args.via_top_layer,
        via_bottom_layer=args.via_bottom_layer,
        ground_plane_name=args.ground_plane_name,
    )
    layout_shapes = select_layout_shapes(layout, args.scope)
    include_sibling_layouts = getattr(args, "include_sibling_layouts", True)
    stop_after_delete = getattr(args, "stop_after_delete", False)
    sibling_root = sibling_layout_root(args.layout) if include_sibling_layouts else None
    stale_layout_roots = [sibling_root] if sibling_root is not None else []
    requested_delete = full_rebuild_delete_names(
        layout,
        ground_plane_name=geometry.ground_plane_name,
        scope=args.scope,
        stale_layout_roots=stale_layout_roots,
    )
    for name in getattr(args, "delete_extra_name", []):
        if name and name not in requested_delete:
            requested_delete.append(name)
    delete_prefixes = list(TEMPORARY_CLIP_FRAME_PREFIXES)
    for prefix in getattr(args, "delete_extra_prefix", []):
        if prefix and prefix not in delete_prefixes:
            delete_prefixes.append(prefix)
    payload: dict[str, Any] = {
        "project": str(args.project),
        "design": args.design,
        "layout": str(args.layout),
        "scope": args.scope,
        "workflow": "delete_source_layout_draw_new_layout_recreate_pcb_output_port",
        "layout_update_policy": {
            "mode": "full_source_layout_rebuild",
            "candidate_level_boolean_ops": False,
            "candidate_level_incremental_ops": False,
            "allowed_geometry_boolean_scope": "none",
            "reference_ground_cutout_handling": "delete_stale_objects_only_do_not_create_or_subtract",
        },
        "selected_shape_names": [shape_name(shape) for shape in layout_shapes],
        "requested_delete_names": requested_delete,
        "delete_name_prefixes": delete_prefixes,
        "stale_layout_roots": [str(path) for path in stale_layout_roots],
        "notes": [
            "Schematic connector instances and connector pin IPorts are never selected by this tool.",
            "If --recreate-pcb-output-port is used, only the output_feed/P2 PCB edge port is created; no P1 PCB port is created.",
            "Layout iteration uses full delete/rebuild; this single operation covers candidate updates.",
            "Do not patch individual boolean cutouts, direct voids, or partial deltas between candidates.",
            "Reference-ground cutout records are allowed only as stale-object delete names or review metadata; new HFSS geometry must express voids as real generated ground-plane shapes.",
            "Sibling candidate layout JSON files are included in the delete-name registry so old candidates cannot overlap the next rebuild.",
            "Temporary board clip/cut frames are part of source-layout lifecycle cleanup when their names match the configured names or prefixes.",
        ],
        "pcb_output_port": {"recreate": bool(args.recreate_pcb_output_port), "delete_port_names": list(args.delete_pcb_port_name), "primitive": "output_feed", "logical_port": "P2"},
        "execute": args.execute,
        "save": args.save,
    }
    if not args.execute:
        payload["status"] = "dry_run"
        payload["lifecycle"] = lifecycle.finish(status="dry_run")
        return payload

    final_lifecycle_status = "failed"
    try:
        session_config = Hfss3dLayoutSessionConfig(
            label="replace_hfss3dlayout_layout_primitives",
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
            app = session.app
            payload.update(session.metadata())
            with lifecycle.timed("read_before_ports"):
                payload["before_ports"] = schematic_iport_names(app)
            if args.recreate_pcb_output_port:
                with lifecycle.timed("delete_existing_pcb_output_port"):
                    payload["pcb_output_port_delete"] = delete_schematic_iports_by_name(app, list(args.delete_pcb_port_name))
            with lifecycle.timed("inspect_existing_layout_objects"):
                layout_editor = app.odesign.SetActiveEditor("Layout")
                existing = existing_layout_objects(app.modeler, layout_editor)
            payload["existing_candidate_count"] = len(existing)
            payload["existing_before_names"] = sorted(existing)
            delete_existing = resolve_existing_delete_names_and_prefixes(existing, requested_delete, delete_prefixes)
            payload["delete_existing_names"] = delete_existing
            if delete_existing:
                with lifecycle.timed("delete_source_layout_objects", object_count=len(delete_existing)):
                    payload["delete_result"] = delete_layout_objects(layout_editor, delete_existing)
                if not payload["delete_result"]["ok"]:
                    payload["status"] = "delete_failed_no_create_no_save"
                    final_lifecycle_status = "failed"
                    return payload
            with lifecycle.timed("inspect_layout_objects_after_delete"):
                existing_after_delete = existing_layout_objects(app.modeler, layout_editor)
            payload["existing_after_delete_names"] = sorted(existing_after_delete)
            payload["source_like_names_after_delete"] = resolve_existing_delete_names_and_prefixes(
                existing_after_delete,
                requested_delete,
                delete_prefixes,
            )
            if stop_after_delete:
                if args.save:
                    with lifecycle.timed("save_aedt_project_after_delete_only"):
                        payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
                payload["status"] = "deleted_stopped_before_create"
                final_lifecycle_status = "ok"
                return payload
            with lifecycle.timed("draw_new_layout_from_json", shape_count=len(layout_shapes)):
                created = create_geometry(app, layout, geometry)
            payload["created_names"] = created
            if args.recreate_pcb_output_port:
                with lifecycle.timed("recreate_pcb_output_port"):
                    app.odesign.SetActiveEditor("Layout")
                    payload["pcb_output_port_create"] = _create_pcb_output_port(app, layout, args)
            with lifecycle.timed("read_after_ports"):
                payload["after_ports"] = schematic_iport_names(app)
            if args.save:
                with lifecycle.timed("save_aedt_project"):
                    payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
            payload["status"] = "replaced"
            final_lifecycle_status = "ok"
            return payload
    finally:
        if "lifecycle" not in payload:
            payload["lifecycle"] = lifecycle.finish(status=final_lifecycle_status)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Delete and redraw the HFSS 3D Layout PCB source layout without touching connector objects.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--layout", type=Path, required=True)
    parser.add_argument(
        "--scope",
        choices=["single-p1-pcb-full", "bfp-real-board-full"],
        default="single-p1-pcb-full",
    )
    parser.add_argument("--signal-layer", default="ETCH_TOP")
    parser.add_argument("--reference-ground-layer", default="ETCH_INNER1")
    parser.add_argument("--via-top-layer", default="ETCH_TOP")
    parser.add_argument("--via-bottom-layer", default="ETCH_BOTTOM")
    parser.add_argument("--ground-plane-name", default="hfss_ground_plane")
    parser.add_argument("--gnd-boundary-mode", default="port-edges")
    parser.add_argument("--recreate-pcb-output-port", action="store_true", help="Create only the non-connector PCB output edge port on output_feed/P2.")
    parser.add_argument(
        "--delete-pcb-port-name",
        action="append",
        default=[],
        help="Existing schematic IPort name to delete before recreating the PCB output port. Repeat if the old PCB port name is ambiguous.",
    )
    parser.add_argument("--port-reference-name", default=default_port_reference_name("ETCH_INNER1", "hfss_ground_plane"))
    parser.add_argument("--port-pec-launch-width", default="0.04mm")
    parser.add_argument("--port-horizontal-extent-factor", type=float, default=5.0)
    parser.add_argument("--port-vertical-extent-factor", type=float, default=3.0)
    parser.add_argument("--port-radial-extent-factor", type=float, default=0.0)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--stop-after-delete", action="store_true", help="Delete existing source layout and stop before drawing the new layout.")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--include-sibling-layouts", action=argparse.BooleanOptionalAction, default=True, help="Also delete source names found in sibling candidate layout JSON files.")
    parser.add_argument("--delete-extra-name", action="append", default=[], help="Additional exact/base layout object name to delete during rebuild, for example a leftover clip frame.")
    parser.add_argument("--delete-extra-prefix", action="append", default=[], help="Additional layout object name prefix to delete during rebuild, for example clip_frame_.")
    parser.add_argument("--version", default="2026.1")
    parser.add_argument("--non-graphical", action="store_true", default=True)
    parser.add_argument("--graphical", action="store_false", dest="non_graphical")
    parser.add_argument("--new-desktop", action="store_true", default=True)
    parser.add_argument("--attach-existing", action="store_false", dest="new_desktop")
    parser.add_argument("--remove-lock", action="store_true")
    parser.add_argument("--keep-attached", action="store_true")
    parser.add_argument("--close-projects", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--close-desktop", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--ready-timeout-s", type=float, default=120.0)
    parser.add_argument("--ready-settle-s", type=float, default=3.0)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    payload = replace_layout_primitives(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
