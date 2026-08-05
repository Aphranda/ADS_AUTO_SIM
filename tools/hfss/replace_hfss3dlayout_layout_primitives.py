#!/usr/bin/env python3
"""Replace selected HFSS 3D Layout PCB primitives without touching ports.

This tool is intentionally narrower than the normal build workflow. It is for
connector launch tuning after the SMA component and ports have already been
fixed in AEDT. The default scope updates only local P1 launch PCB objects and
preserves schematic components, IPorts, the 50R through section, and the P2
edge-port carrier object.
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

from simads.hfss.aedt_startup import apply_grpc_startup_compat, apply_pyaedt_settings, startup_snapshot
from simads.hfss.layout import GeometryBuildOptions, _create_cutout_tool, _shape_net, _subtract_from_ground
from simads.hfss.ports import (
    apply_aedt_edge_gap_port_template,
    default_port_reference_name,
    infer_port_edge,
)

apply_grpc_startup_compat()


P1_LOCAL_LAUNCH_NAMES = {
    "p1_launch_top_ground",
    "p1_launch_bottom_ground",
    "input_feed",
    "input_neck",
    "input_series_hi_z",
    "input_taper",
}

P1_CONNECTED_LAUNCH_NAMES = {
    *P1_LOCAL_LAUNCH_NAMES,
    "center_line_top_ground",
    "center_line_bottom_ground",
    "through_line",
}

PRESERVED_NAMES = {
    "em_boundary",
    "hfss_ground_plane",
    "center_line_top_ground",
    "center_line_bottom_ground",
    "through_line",
    "output_feed",
}


def _json_default(value: Any) -> str:
    return str(value)


def _load_layout(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"layout must be a JSON object: {path}")
    return data


def _shape_name(shape: dict[str, Any]) -> str:
    return str(shape.get("name", ""))


def _is_p1_local_launch_shape(shape: dict[str, Any]) -> bool:
    name = _shape_name(shape)
    if name in P1_LOCAL_LAUNCH_NAMES:
        return True
    if name.startswith("ground_via_p1_"):
        return True
    if shape.get("kind") == "reference_ground_cutout":
        metadata = shape.get("metadata", {})
        return isinstance(metadata, dict) and metadata.get("side") == "P1"
    return False


def _is_p1_connected_launch_shape(shape: dict[str, Any]) -> bool:
    name = _shape_name(shape)
    if _is_p1_local_launch_shape(shape) or name in P1_CONNECTED_LAUNCH_NAMES:
        return True
    return name.startswith("gcpw_line_via_")


def _selected_shapes(layout: dict[str, Any], scope: str) -> list[dict[str, Any]]:
    shapes = [shape for shape in layout.get("shapes", []) if isinstance(shape, dict)]
    if scope == "single-p1-launch-local":
        return [shape for shape in shapes if _is_p1_local_launch_shape(shape)]
    if scope == "single-p1-launch-connected":
        return [shape for shape in shapes if _is_p1_connected_launch_shape(shape)]
    if scope == "all-pcb-except-p2-port-carrier":
        return [shape for shape in shapes if _shape_name(shape) not in PRESERVED_NAMES]
    raise ValueError(f"unsupported replacement scope: {scope}")


def _delete_names_for_shape(shape: dict[str, Any]) -> list[str]:
    name = _shape_name(shape)
    if not name:
        return []
    if shape.get("kind") == "via":
        return [f"{name}_pad", name]
    if shape.get("kind") == "reference_ground_cutout":
        return []
    return [name]


def _delete_names(shapes: list[dict[str, Any]]) -> list[str]:
    output: list[str] = []
    for shape in shapes:
        for name in _delete_names_for_shape(shape):
            if name and name not in output:
                output.append(name)
    return output


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
    for layer in ("ETCH_TOP", "ETCH_INNER1"):
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


def _create_shape(app: Any, shape: dict[str, Any], geometry: GeometryBuildOptions) -> Any | None:
    kind = shape.get("kind")
    layer = shape.get("layer")
    name = _shape_name(shape)
    signal_layers = {"cond", geometry.signal_layer}
    if kind == "rect" and layer in signal_layers:
        return app.modeler.create_rectangle(
            geometry.signal_layer,
            [shape["x"], shape["y"]],
            [shape["w"], shape["h"]],
            name=name,
            net=_shape_net(shape, name),
        )
    if kind == "polygon" and layer in signal_layers:
        return app.modeler.create_polygon(
            geometry.signal_layer,
            [[float(x), float(y)] for x, y in shape["points"]],
            units="mm",
            name=name,
            net=_shape_net(shape, name),
        )
    if kind == "via":
        pad_d = float(shape.get("pad_diameter") or shape.get("diameter"))
        via_d = float(shape.get("diameter") or pad_d)
        pad = app.modeler.create_circle(
            geometry.signal_layer,
            float(shape["x"]),
            float(shape["y"]),
            pad_d / 2.0,
            name=f"{name}_pad",
            net="GND",
        )
        via = app.modeler.create_via(
            x=float(shape["x"]),
            y=float(shape["y"]),
            hole_diam=via_d,
            top_layer=geometry.via_top_layer,
            bot_layer=geometry.via_bottom_layer,
            name=name,
            net="GND",
        )
        return [item for item in (pad, via) if item]
    if kind == "reference_ground_cutout":
        return _create_cutout_tool(app, shape, geometry)
    return None


def replace_layout_primitives(args: argparse.Namespace) -> dict[str, Any]:
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
    requested_delete = _delete_names(selected_shapes)
    payload: dict[str, Any] = {
        "project": str(args.project),
        "design": args.design,
        "layout": str(args.layout),
        "scope": args.scope,
        "preserved_names": sorted(PRESERVED_NAMES),
        "selected_shape_names": [_shape_name(shape) for shape in selected_shapes],
        "requested_delete_names": requested_delete,
        "notes": [
            "Schematic connector instances and IPorts are never selected by this tool.",
            "If --recreate-pcb-output-port is used, only the output_feed/P2 PCB edge port is created; no P1 PCB port is created.",
            "Reference-ground cutouts are subtractive; an existing L2 cutout cannot be cleanly shrunk without rebuilding the ground plane.",
        ],
        "pcb_output_port": {
            "recreate": bool(args.recreate_pcb_output_port),
            "delete_port_names": list(args.delete_pcb_port_name),
            "primitive": "output_feed",
            "logical_port": "P2",
        },
        "execute": args.execute,
        "save": args.save,
    }
    if not args.execute:
        payload["status"] = "dry_run"
        return payload

    from ansys.aedt.core import Hfss3dLayout, settings

    apply_pyaedt_settings(settings)
    payload["aedt_startup"] = startup_snapshot(settings)

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
        payload["before_ports"] = _schematic_ports(app)
        layout_editor = app.odesign.SetActiveEditor("Layout")
        existing = _existing_layout_objects(app.modeler, layout_editor)
        payload["existing_candidate_count"] = len(existing)
        delete_existing = _resolve_existing_delete_names(existing, requested_delete)
        payload["delete_existing_names"] = delete_existing
        if delete_existing:
            payload["delete_result"] = _delete_layout_objects(layout_editor, delete_existing)
            if not payload["delete_result"]["ok"]:
                payload["status"] = "delete_failed_no_create_no_save"
                return payload
        created: list[str] = []
        cutout_tools: list[Any] = []
        for shape in selected_shapes:
            obj = _create_shape(app, shape, geometry)
            if shape.get("kind") == "reference_ground_cutout":
                if obj:
                    cutout_tools.append(obj)
                continue
            if isinstance(obj, list):
                created.extend(str(getattr(item, "name", item)) for item in obj)
            elif obj:
                created.append(str(getattr(obj, "name", obj)))
        if cutout_tools:
            _subtract_from_ground(app, geometry.ground_plane_name, cutout_tools)
            created.extend(str(getattr(item, "name", item)) for item in cutout_tools)
        payload["created_names"] = created
        if args.recreate_pcb_output_port:
            payload["pcb_output_port_delete"] = _delete_schematic_ports_by_name(app, list(args.delete_pcb_port_name))
            app.odesign.SetActiveEditor("Layout")
            payload["pcb_output_port_create"] = _create_pcb_output_port(app, layout, args)
        payload["after_ports"] = _schematic_ports(app)
        if args.save:
            payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
        payload["status"] = "replaced"
        return payload
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replace selected HFSS 3D Layout PCB primitives without touching ports.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--layout", type=Path, required=True)
    parser.add_argument(
        "--scope",
        choices=["single-p1-launch-local", "single-p1-launch-connected", "all-pcb-except-p2-port-carrier"],
        default="single-p1-launch-local",
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
