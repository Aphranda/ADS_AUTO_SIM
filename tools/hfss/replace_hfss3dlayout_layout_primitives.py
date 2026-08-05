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
from simads.hfss.ports import (
    apply_aedt_edge_gap_port_template,
    default_port_reference_name,
    infer_port_edge,
)
from simads.hfss.session import Hfss3dLayoutSessionConfig, open_hfss3dlayout_session

apply_grpc_startup_compat()


def _json_default(value: Any) -> str:
    return str(value)


def _load_layout(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"layout must be a JSON object: {path}")
    return data


def _shape_name(shape: dict[str, Any]) -> str:
    return str(shape.get("name", ""))


def _selected_shapes(layout: dict[str, Any], scope: str) -> list[dict[str, Any]]:
    shapes = [shape for shape in layout.get("shapes", []) if isinstance(shape, dict)]
    if scope == "single-p1-pcb-full":
        return shapes
    raise ValueError(f"unsupported replacement scope: {scope}")


def _delete_names_for_shape(shape: dict[str, Any]) -> list[str]:
    name = _shape_name(shape)
    if not name:
        return []
    if shape.get("kind") == "via":
        return [f"{name}_pad", name]
    return [name]


def _delete_names(shapes: list[dict[str, Any]]) -> list[str]:
    output: list[str] = []
    for shape in shapes:
        for name in _delete_names_for_shape(shape):
            if name and name not in output:
                output.append(name)
    return output


def _full_rebuild_delete_names(layout: dict[str, Any], geometry: GeometryBuildOptions) -> list[str]:
    names = [geometry.ground_plane_name]
    for name in _delete_names(_selected_shapes(layout, "single-p1-pcb-full")):
        if name not in names:
            names.append(name)
    # Optional source-layout primitives can disappear between connector
    # candidates. Keep them in the full rebuild delete set so a later candidate
    # cannot inherit copper from an earlier tuning run.
    for name in (
        "input_series_hi_z",
        "output_series_hi_z",
        "p1_l2_cutout_rect_extend_right",
        "p2_l2_cutout_rect_extend_left",
        "p1_l3_cutout_rect_extend_right",
        "p2_l3_cutout_rect_extend_left",
    ):
        if name not in names:
            names.append(name)
    # Full rebuilds must remove source primitives that may be absent from a new
    # candidate, for example when an iteration disables connector launch vias.
    for prefix in ("ground_via_p1_top", "ground_via_p1_bottom", "ground_via_p2_top", "ground_via_p2_bottom"):
        for idx in range(1, 17):
            for name in (f"{prefix}_{idx}_pad", f"{prefix}_{idx}"):
                if name not in names:
                    names.append(name)
    return names


def _matches_aedt_generated_name(actual: str, base: str) -> bool:
    if actual == base:
        return True
    if not actual.startswith(base):
        return False
    suffix = actual[len(base) :]
    if not suffix:
        return True
    # AEDT appends opaque suffixes such as ``input_feed5TJCER`` when a name
    # collides. Do not let a bare numeric continuation like top_10 match top_1.
    return any(ch.isalpha() for ch in suffix)


def _resolve_existing_delete_names(existing: set[str], requested: list[str]) -> list[str]:
    output: list[str] = []
    for base in requested:
        for actual in sorted(existing):
            if _matches_aedt_generated_name(actual, base) and actual not in output:
                output.append(actual)
    return output


def _existing_layout_objects(modeler: Any, editor: Any) -> set[str]:
    names: set[str] = set()
    for attr in ("polygon_names", "via_names", "line_names", "polygon_voids_names", "line_voids_names"):
        try:
            value = getattr(modeler, attr)
            items = value() if callable(value) else value
            names.update(str(item) for item in items or [])
        except Exception:
            continue
    for net in ("IN", "GND", "SIG", "OUT"):
        try:
            names.update(str(item) for item in modeler.objects_by_net(net))
        except Exception:
            continue
    for layer in ("ETCH_TOP", "ETCH_INNER1", "ETCH_INNER2", "ETCH_BOTTOM"):
        try:
            names.update(str(item) for item in modeler.objects_by_layer(layer))
        except Exception:
            continue
    groups = ("Solids", "Sheets", "Lines", "Unclassified", "Non Model", "Planes", "Points")
    for group in groups:
        try:
            names.update(str(item) for item in editor.GetObjectsInGroup(group))
        except Exception:
            continue
    return names


def _schematic_ports(app: Any) -> list[str]:
    try:
        editor = app.odesign.SetActiveEditor("SchematicEditor")
        return [str(item) for item in editor.GetAllPorts()]
    except Exception:
        return []


def _delete_schematic_ports_by_name(app: Any, port_names: list[str]) -> dict[str, Any]:
    if not port_names:
        return {"requested": [], "selected": [], "deleted": False}
    requested = {str(name) for name in port_names}
    editor = app.odesign.SetActiveEditor("SchematicEditor")
    before = [str(item) for item in editor.GetAllPorts()]
    selected = []
    for port in before:
        for name in requested:
            if port == f"IPort@{name}" or port.startswith(f"IPort@{name};"):
                selected.append(port)
    if not selected:
        return {"requested": sorted(requested), "before": before, "selected": [], "deleted": False}
    result = editor.Delete(["NAME:Selections", "Selections:=", selected])
    after = [str(item) for item in editor.GetAllPorts()]
    return {
        "requested": sorted(requested),
        "before": before,
        "selected": selected,
        "delete_result": _json_default(result),
        "after": after,
        "deleted": True,
    }


def _delete_layout_objects(editor: Any, names: list[str]) -> dict[str, Any]:
    deleted: list[str] = []
    errors: list[dict[str, str]] = []
    for name in names:
        try:
            editor.Delete(["NAME:Selections", "Selections:=", name])
            deleted.append(name)
        except Exception as exc:
            errors.append({"name": name, "error": f"{type(exc).__name__}: {exc}"})
    return {"requested": names, "deleted": deleted, "errors": errors, "ok": not errors}


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
    layout = _load_layout(args.layout)
    geometry = GeometryBuildOptions(
        gnd_boundary_mode=args.gnd_boundary_mode,
        signal_layer=args.signal_layer,
        reference_ground_layer=args.reference_ground_layer,
        via_top_layer=args.via_top_layer,
        via_bottom_layer=args.via_bottom_layer,
        ground_plane_name=args.ground_plane_name,
    )
    selected_shapes = _selected_shapes(layout, args.scope)
    requested_delete = _full_rebuild_delete_names(layout, geometry)
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
            "allowed_geometry_boolean_scope": "inside_create_geometry_only_for_declared_layout_json_shapes",
        },
        "selected_shape_names": [_shape_name(shape) for shape in selected_shapes],
        "requested_delete_names": requested_delete,
        "notes": [
            "Schematic connector instances and connector pin IPorts are never selected by this tool.",
            "If --recreate-pcb-output-port is used, only the output_feed/P2 PCB edge port is created; no P1 PCB port is created.",
            "Layout iteration uses full delete/rebuild; this single operation covers candidate updates.",
            "Do not patch individual boolean cutouts, direct voids, or partial deltas between candidates.",
            "Reference-ground cutouts are geometry semantics in layout JSON and are applied only while drawing the new source layout.",
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
                payload["before_ports"] = _schematic_ports(app)
            if args.recreate_pcb_output_port:
                with lifecycle.timed("delete_existing_pcb_output_port"):
                    payload["pcb_output_port_delete"] = _delete_schematic_ports_by_name(app, list(args.delete_pcb_port_name))
            with lifecycle.timed("inspect_existing_layout_objects"):
                layout_editor = app.odesign.SetActiveEditor("Layout")
                existing = _existing_layout_objects(app.modeler, layout_editor)
            payload["existing_candidate_count"] = len(existing)
            delete_existing = _resolve_existing_delete_names(existing, requested_delete)
            payload["delete_existing_names"] = delete_existing
            if delete_existing:
                with lifecycle.timed("delete_source_layout_objects", object_count=len(delete_existing)):
                    payload["delete_result"] = _delete_layout_objects(layout_editor, delete_existing)
                if not payload["delete_result"]["ok"]:
                    payload["status"] = "delete_failed_no_create_no_save"
                    final_lifecycle_status = "failed"
                    return payload
            with lifecycle.timed("draw_new_layout_from_json", shape_count=len(selected_shapes)):
                created = create_geometry(app, layout, geometry)
            payload["created_names"] = created
            if args.recreate_pcb_output_port:
                with lifecycle.timed("recreate_pcb_output_port"):
                    app.odesign.SetActiveEditor("Layout")
                    payload["pcb_output_port_create"] = _create_pcb_output_port(app, layout, args)
            with lifecycle.timed("read_after_ports"):
                payload["after_ports"] = _schematic_ports(app)
            if args.save:
                with lifecycle.timed("save_aedt_project"):
                    payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
            payload["status"] = "replaced"
            final_lifecycle_status = "ok"
            return payload
    finally:
        if "lifecycle" not in payload:
            payload["lifecycle"] = lifecycle.finish(status=final_lifecycle_status)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Delete and redraw the HFSS 3D Layout PCB source layout without touching connector objects.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--layout", type=Path, required=True)
    parser.add_argument(
        "--scope",
        choices=["single-p1-pcb-full"],
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
    parser.add_argument("--ready-timeout-s", type=float, default=120.0)
    parser.add_argument("--ready-settle-s", type=float, default=3.0)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


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
