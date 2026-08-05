"""HFSS 3D Layout port and GND-reference helpers."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

TOP_LAYER = "TOP"
BOTTOM_LAYER = "GND"
GROUND_PLANE = "hfss_ground_plane"
RECT_EDGE_BY_SIDE = {"top": 0, "left": 1, "bottom": 2, "right": 3}


def signal_layer(args: argparse.Namespace) -> str:
    return str(getattr(args, "signal_layer", None) or TOP_LAYER)


def reference_ground_layer(args: argparse.Namespace) -> str:
    return str(getattr(args, "reference_ground_layer", None) or BOTTOM_LAYER)


def via_top_layer(args: argparse.Namespace) -> str:
    return str(getattr(args, "via_top_layer", None) or signal_layer(args))


def via_bottom_layer(args: argparse.Namespace) -> str:
    return str(getattr(args, "via_bottom_layer", None) or reference_ground_layer(args))


def ground_plane_name(args: argparse.Namespace | None = None) -> str:
    if args is None:
        return GROUND_PLANE
    return str(getattr(args, "ground_plane_name", None) or GROUND_PLANE)


def original_boundary(layout: dict[str, Any]) -> dict[str, Any]:
    boundary = next((s for s in layout.get("shapes", []) if s.get("kind") == "boundary"), None)
    if not boundary:
        raise ValueError("Layout boundary is required")
    return boundary


def resolve_gnd_boundary(layout: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    boundary = dict(original_boundary(layout))
    if args.gnd_boundary_mode == "em-boundary":
        return boundary
    p1 = find_port(layout, 1)
    p2 = find_port(layout, 2)
    left = min(float(p1["x"]), float(p2["x"]))
    right = max(float(p1["x"]), float(p2["x"]))
    if left >= right:
        raise ValueError(f"Invalid port-edge GND boundary: left={left:g}, right={right:g}")
    boundary["x"] = left
    boundary["w"] = right - left
    boundary.setdefault("metadata", {})
    boundary["metadata"] = dict(boundary["metadata"])
    boundary["metadata"]["gnd_boundary_mode"] = args.gnd_boundary_mode
    boundary["metadata"]["source_boundary"] = "em_boundary"
    return boundary


def find_shape(layout: dict[str, Any], name: str) -> dict[str, Any]:
    for shape in layout.get("shapes", []):
        if shape.get("name") == name:
            return shape
    raise ValueError(f"Layout shape not found: {name}")


def find_port(layout: dict[str, Any], number: int) -> dict[str, Any]:
    for port in layout.get("ports", []):
        if int(port.get("number", -1)) == number:
            return port
    raise ValueError(f"Layout port P{number} not found")


def shape_bounds(shape: dict[str, Any]) -> tuple[float, float, float, float]:
    if shape.get("kind") in {"rect", "boundary"}:
        x0 = float(shape["x"])
        y0 = float(shape["y"])
        return x0, y0, x0 + float(shape["w"]), y0 + float(shape["h"])
    points = shape.get("points")
    if points:
        xs = [float(point[0]) for point in points]
        ys = [float(point[1]) for point in points]
        return min(xs), min(ys), max(xs), max(ys)
    raise ValueError(f"Cannot infer bounds for shape: {shape.get('name')}")


def nearest_rect_side(bounds: tuple[float, float, float, float], x: float, y: float) -> str:
    x0, y0, x1, y1 = bounds
    distances = {
        "left": abs(x - x0),
        "bottom": abs(y - y0),
        "right": abs(x - x1),
        "top": abs(y - y1),
    }
    return min(distances, key=distances.get)


def infer_port_edge(layout: dict[str, Any], primitive: str, port_number: int) -> tuple[int, str]:
    port = find_port(layout, port_number)
    shape = find_shape(layout, primitive)
    side = nearest_rect_side(shape_bounds(shape), float(port["x"]), float(port["y"]))
    return RECT_EDGE_BY_SIDE[side], side


def infer_reference_edge(layout: dict[str, Any], port_number: int) -> tuple[int, str]:
    port = find_port(layout, port_number)
    boundary = next((s for s in layout.get("shapes", []) if s.get("kind") == "boundary"), None)
    if not boundary:
        return 0, "left"
    side = nearest_rect_side(shape_bounds(boundary), float(port["x"]), float(port["y"]))
    return RECT_EDGE_BY_SIDE[side], side


def infer_pin_ports(layout: dict[str, Any]) -> dict[str, Any]:
    input_feed = find_shape(layout, "input_feed")
    output_feed = find_shape(layout, "output_feed")
    p1 = {
        "name": "Port1",
        "x": float(input_feed["x"]),
        "y": float(input_feed["y"]),
        "rotation": 0.0,
        "anchor": "input_feed lower-left outside endpoint",
    }
    p2 = {
        "name": "Port2",
        "x": float(output_feed["x"]) + float(output_feed["w"]),
        "y": float(output_feed["y"]),
        "rotation": 180.0,
        "anchor": "output_feed lower-right outside endpoint",
    }
    return {"p1": p1, "p2": p2}


def default_port_reference_name(layer: str = BOTTOM_LAYER, primitive: str = GROUND_PLANE) -> str:
    return f"GND:{layer}:{primitive}"


def port_reference_name(args: argparse.Namespace) -> str:
    return args.port_reference_name or default_port_reference_name(reference_ground_layer(args), ground_plane_name(args))


def set_excitation_property(app: Any, port_name: str, name: str, value: Any) -> bool:
    try:
        properties = set(app.modeler.oeditor.GetProperties("EM Design", f"Excitations:{port_name}"))
    except Exception:
        properties = set()
    if properties and name not in properties:
        return False
    try:
        app.modeler.oeditor.SetPropertyValue("EM Design", f"Excitations:{port_name}", name, value)
        return True
    except Exception:
        try:
            return bool(
                app.modeler.change_property(
                    assignment=f"Excitations:{port_name}",
                    name=name,
                    value=value,
                    aedt_tab="EM Design",
                )
            )
        except Exception:
            return False


def hfss_gap_port_template(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "hfss_type": "Gap",
        "orientation": "Vertical",
        "layer_alignment": "Upper",
        "horizontal_extent_factor": float(args.port_horizontal_extent_factor),
        "vertical_extent_factor": float(args.port_vertical_extent_factor),
        "radial_extent_factor": float(args.port_radial_extent_factor),
        "pec_launch_width": args.port_pec_launch_width,
        "reference_name": port_reference_name(args),
    }


def pin_gap_port_template(args: argparse.Namespace) -> dict[str, Any]:
    return hfss_gap_port_template(args)


def apply_pin_gap_port_template(app: Any, port: Any, args: argparse.Namespace) -> dict[str, bool]:
    return {key: False for key in pin_gap_port_template(args)}


def normalize_created_port_name(app: Any, created_port: Any, desired_name: str) -> str:
    port_name = getattr(created_port, "name", str(created_port))
    if port_name == desired_name:
        return desired_name
    if not port_name or port_name == "False":
        return desired_name
    set_excitation_property(app, port_name, "Port", desired_name)
    return desired_name


def apply_gap_edge_port_template(app: Any, port_name: str, args: argparse.Namespace) -> dict[str, bool]:
    return {"created_as_edge_port": bool(port_name), "edb_property_patch_after_save": True}


def apply_aedt_edge_gap_port_template(app: Any, port_name: str, args: argparse.Namespace) -> dict[str, bool]:
    template = hfss_gap_port_template(args)
    updates = {
        "HFSS Type": template["hfss_type"],
        "Orientation": template["orientation"],
        "Layer Alignment": template["layer_alignment"],
        "Horizontal Extent Factor": str(template["horizontal_extent_factor"]),
        "Vertical Extent Factor": str(template["vertical_extent_factor"]),
        "Radial Extent Factor": str(template["radial_extent_factor"]),
        "PEC Launch Width": template["pec_launch_width"],
        "Renormalize": True,
        "Renormalize Impedance": "50ohm",
        "DeembedParasiticPortInductance": False,
    }
    return {name: set_excitation_property(app, port_name, name, value) for name, value in updates.items()}


def apply_port_post_processing(port: Any, edb: Any, *, renormalize: bool = True, deembed: bool = True) -> dict[str, Any]:
    pp = port.core.port_post_processing_prop
    pp.do_renormalize = renormalize
    pp.do_deembed = deembed
    pp.renormalization_impedance = edb.value(50.0)
    pp.voltage_magnitude = edb.value(1.0)
    port.core.port_post_processing_prop = pp
    return read_port_post_processing(port)


def read_port_post_processing(port: Any) -> dict[str, Any]:
    pp = port.core.port_post_processing_prop
    return {
        "do_renormalize": bool(getattr(pp, "do_renormalize", False)),
        "do_deembed": bool(getattr(pp, "do_deembed", False)),
        "renormalization_impedance": edb_float(getattr(pp, "renormalization_impedance", 0.0)),
        "voltage_magnitude": edb_float(getattr(pp, "voltage_magnitude", 0.0)),
    }


def meters(value_mm: float) -> float:
    return value_mm * 1e-3


def edb_float(value: Any) -> float:
    raw = getattr(value, "value", value)
    return float(raw)


def edb_primitive_bbox(primitive: Any) -> tuple[float, float, float, float]:
    bbox_attr = getattr(primitive, "bbox")
    bbox = bbox_attr() if callable(bbox_attr) else bbox_attr
    return edb_float(bbox[0]), edb_float(bbox[1]), edb_float(bbox[2]), edb_float(bbox[3])


def edb_net_name(primitive: Any) -> str:
    return str(getattr(primitive, "net_name", None) or getattr(getattr(primitive, "net", None), "name", "") or "")


def edb_layer_name(primitive: Any) -> str:
    return str(getattr(primitive, "layer_name", "") or getattr(getattr(primitive, "layer", None), "name", "") or "")


def bbox_match_error(actual: tuple[float, float, float, float], expected: tuple[float, float, float, float]) -> float:
    return sum(abs(a - b) for a, b in zip(actual, expected))


def find_edb_primitive_by_shape(edb: Any, shape: dict[str, Any], layer: str, net: str, *, tol_m: float = 2e-6) -> Any:
    x0, y0, x1, y1 = shape_bounds(shape)
    expected = (meters(x0), meters(y0), meters(x1), meters(y1))
    matches: list[tuple[float, Any, tuple[float, float, float, float]]] = []
    for primitive in edb.modeler.primitives:
        if edb_layer_name(primitive) != layer or edb_net_name(primitive) != net:
            continue
        try:
            bbox = edb_primitive_bbox(primitive)
        except Exception:
            continue
        error = bbox_match_error(bbox, expected)
        matches.append((error, primitive, bbox))
    if not matches:
        raise ValueError(f"No EDB primitive found for layer={layer}, net={net}, shape={shape.get('name')}")
    matches.sort(key=lambda item: item[0])
    if matches[0][0] > tol_m:
        raise ValueError(
            f"Best EDB primitive bbox mismatch for {shape.get('name')}: error={matches[0][0]:.6g}m, "
            f"expected={expected}, actual={matches[0][2]}"
        )
    return matches[0][1]


def edge_midpoint_from_side(shape: dict[str, Any], side: str) -> list[float]:
    x0, y0, x1, y1 = shape_bounds(shape)
    if side == "left":
        return [meters(x0), meters((y0 + y1) / 2.0)]
    if side == "right":
        return [meters(x1), meters((y0 + y1) / 2.0)]
    if side == "bottom":
        return [meters((x0 + x1) / 2.0), meters(y0)]
    if side == "top":
        return [meters((x0 + x1) / 2.0), meters(y1)]
    raise ValueError(f"Unsupported edge side: {side}")


def reference_point_on_gnd_boundary(boundary: dict[str, Any], signal_point_m: list[float], ref_side: str) -> list[float]:
    x0, y0, x1, y1 = shape_bounds(boundary)
    sx, sy = signal_point_m
    if ref_side == "left":
        return [meters(x0), sy]
    if ref_side == "right":
        return [meters(x1), sy]
    if ref_side == "bottom":
        return [sx, meters(y0)]
    if ref_side == "top":
        return [sx, meters(y1)]
    raise ValueError(f"Unsupported reference side: {ref_side}")


def create_gap_edge_ports_in_edb(edb_path: Path, layout: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    from ansys.aedt.core import Edb

    template = hfss_gap_port_template(args)
    edges = resolve_port_edges(layout, args.p1_edge, args.p2_edge, args.p1_ref_edge, args.p2_ref_edge)
    input_feed = find_shape(layout, "input_feed")
    output_feed = find_shape(layout, "output_feed")
    boundary = resolve_gnd_boundary(layout, args)

    status: dict[str, Any] = {"edb": str(edb_path), "ports": {}, "port_edges": edges}
    edb = Edb(str(edb_path), version=args.version, isreadonly=False)
    try:
        signal_ref = [
            ("Port1", input_feed, "IN", edges["p1_side"], edges["p1_ref_side"]),
            ("Port2", output_feed, "OUT", edges["p2_side"], edges["p2_ref_side"]),
        ]
        gnd_primitive = find_edb_primitive_by_shape(edb, boundary, reference_ground_layer(args), "GND")
        for port_name, signal_shape, signal_net, signal_side, ref_side in signal_ref:
            if port_name in edb.ports:
                edb.ports[port_name].delete()
            signal_primitive = find_edb_primitive_by_shape(edb, signal_shape, signal_layer(args), signal_net)
            terminal_point = edge_midpoint_from_side(signal_shape, signal_side)
            reference_point = reference_point_on_gnd_boundary(boundary, terminal_point, ref_side)
            created = edb.excitation_manager.create_edge_port_on_polygon(
                polygon=signal_primitive,
                reference_polygon=gnd_primitive,
                terminal_point=terminal_point,
                reference_point=reference_point,
                port_name=port_name,
                port_impedance=50.0,
                force_circuit_port=False,
            )
            port = edb.ports.get(port_name)
            if not port:
                status["ports"][port_name] = {"created": bool(created), "patched": False, "reason": "missing_after_create"}
                continue
            props = port._hfss_port_property
            props.hfss_type = template["hfss_type"]
            props.orientation = template["orientation"]
            props.layer_alignment = template["layer_alignment"]
            props.horizontal_extent_factor = template["horizontal_extent_factor"]
            props.vertical_extent_factor = template["vertical_extent_factor"]
            props.radial_extent_factor = template["radial_extent_factor"]
            props.pec_launch_width = template["pec_launch_width"]
            props.reference_name = template["reference_name"]
            port._hfss_port_property = props
            port.is_circuit_port = False
            post_processing = apply_port_post_processing(port, edb)
            status["ports"][port_name] = {
                "created": bool(created),
                "patched": True,
                "type": type(port).__name__,
                "terminal_type": str(getattr(port, "terminal_type", "")),
                "boundary_type": str(getattr(port, "boundary_type", "")),
                "is_circuit_port": bool(getattr(port, "is_circuit_port", False)),
                "terminal_point_m": terminal_point,
                "reference_point_m": reference_point,
                "reference_mode": "same_axis_projection_to_gnd_boundary",
                "post_processing": post_processing,
                "hfss": props.to_hfss_string(),
            }
        status["saved"] = bool(edb.save())
    finally:
        edb.close()
    return status


def patch_gap_ports_in_edb(edb_path: Path, args: argparse.Namespace) -> dict[str, Any]:
    from ansys.aedt.core import Edb

    template = hfss_gap_port_template(args)
    status: dict[str, Any] = {"edb": str(edb_path), "ports": {}}
    edb = Edb(str(edb_path), version=args.version, isreadonly=False)
    try:
        for port_name in ("Port1", "Port2"):
            port = edb.ports.get(port_name)
            if not port:
                status["ports"][port_name] = {"patched": False, "reason": "missing"}
                continue
            props = port._hfss_port_property
            before = {
                "type": type(port).__name__,
                "terminal_type": str(getattr(port, "terminal_type", "")),
                "boundary_type": str(getattr(port, "boundary_type", "")),
                "is_circuit_port": bool(getattr(port, "is_circuit_port", False)),
                "pec_launch_width": props.pec_launch_width,
                "reference_name": props.reference_name,
            }
            port.is_circuit_port = False
            props.hfss_type = template["hfss_type"]
            props.orientation = template["orientation"]
            props.layer_alignment = template["layer_alignment"]
            props.horizontal_extent_factor = template["horizontal_extent_factor"]
            props.vertical_extent_factor = template["vertical_extent_factor"]
            props.radial_extent_factor = template["radial_extent_factor"]
            props.pec_launch_width = template["pec_launch_width"]
            props.reference_name = template["reference_name"]
            port._hfss_port_property = props
            post_processing = apply_port_post_processing(port, edb)
            status["ports"][port_name] = {
                "patched": True,
                "before": before,
                "after": {
                    "type": type(port).__name__,
                    "terminal_type": str(getattr(port, "terminal_type", "")),
                    "boundary_type": str(getattr(port, "boundary_type", "")),
                    "is_circuit_port": bool(getattr(port, "is_circuit_port", False)),
                    "pec_launch_width": props.pec_launch_width,
                    "reference_name": props.reference_name,
                    "post_processing": post_processing,
                },
            }
        status["saved"] = bool(edb.save())
    finally:
        edb.close()
    return status


def patch_pin_gap_ports_in_edb(edb_path: Path, args: argparse.Namespace) -> dict[str, Any]:
    return patch_gap_ports_in_edb(edb_path, args)


def project_edb_path(project: Path) -> Path:
    return project.with_suffix(".aedb")


def net_for_shape(name: str | None) -> str:
    if not name:
        return "SIG"
    if name.startswith("input_"):
        return "IN"
    if name.startswith("output_"):
        return "OUT"
    if name.startswith("resonator_") or name.startswith("ground_via_"):
        return "GND"
    return "SIG"


def resolve_port_edges(
    layout: dict[str, Any],
    p1_edge: int | None,
    p2_edge: int | None,
    p1_ref_edge: int | None,
    p2_ref_edge: int | None,
) -> dict[str, Any]:
    inferred_p1_edge, p1_side = infer_port_edge(layout, "input_feed", 1)
    inferred_p2_edge, p2_side = infer_port_edge(layout, "output_feed", 2)
    inferred_p1_ref_edge, p1_ref_side = infer_reference_edge(layout, 1)
    inferred_p2_ref_edge, p2_ref_side = infer_reference_edge(layout, 2)
    return {
        "p1_edge": inferred_p1_edge if p1_edge is None else p1_edge,
        "p2_edge": inferred_p2_edge if p2_edge is None else p2_edge,
        "p1_ref_edge": inferred_p1_ref_edge if p1_ref_edge is None else p1_ref_edge,
        "p2_ref_edge": inferred_p2_ref_edge if p2_ref_edge is None else p2_ref_edge,
        "p1_side": p1_side,
        "p2_side": p2_side,
        "p1_ref_side": p1_ref_side,
        "p2_ref_side": p2_ref_side,
    }


def create_ports(app: Any, layout: dict[str, Any], args: argparse.Namespace) -> tuple[list[str], dict[str, Any]]:
    created: list[str] = []
    edges = resolve_port_edges(layout, args.p1_edge, args.p2_edge, args.p1_ref_edge, args.p2_ref_edge)
    skip_port_numbers = {int(item) for item in getattr(args, "skip_port_number", [])}
    create_p1 = 1 not in skip_port_numbers
    create_p2 = 2 not in skip_port_numbers
    if args.port_type == "edge-gap":
        p1 = None
        p2 = None
        edges["edge_gap_template"] = {
            "p1": {"created_after_save_by_pyedb": True},
            "p2": {"created_after_save_by_pyedb": True},
            "reference_name": port_reference_name(args),
            "pec_launch_width": args.port_pec_launch_width,
            "reference_primitive": ground_plane_name(args),
        }
    elif args.port_type == "pin-gap":
        pin_ports = infer_pin_ports(layout)
        p1 = (
            app.create_pin_port(
                name=pin_ports["p1"]["name"],
                x=pin_ports["p1"]["x"],
                y=pin_ports["p1"]["y"],
                rotation=pin_ports["p1"]["rotation"],
                top_layer=signal_layer(args),
                bottom_layer=reference_ground_layer(args),
            )
            if create_p1
            else None
        )
        p2 = (
            app.create_pin_port(
                name=pin_ports["p2"]["name"],
                x=pin_ports["p2"]["x"],
                y=pin_ports["p2"]["y"],
                rotation=pin_ports["p2"]["rotation"],
                top_layer=signal_layer(args),
                bottom_layer=reference_ground_layer(args),
            )
            if create_p2
            else None
        )
        edges["pin_ports"] = pin_ports
        edges["pin_gap_template"] = {
            "p1": apply_pin_gap_port_template(app, p1, args) if p1 else {},
            "p2": apply_pin_gap_port_template(app, p2, args) if p2 else {},
            "reference_name": port_reference_name(args),
            "pec_launch_width": args.port_pec_launch_width,
        }
    elif args.port_type == "aedt-edge":
        p1 = app.create_edge_port("input_feed", edges["p1_edge"], is_circuit_port=False) if create_p1 else None
        p2 = app.create_edge_port("output_feed", edges["p2_edge"], is_circuit_port=False) if create_p2 else None
        edge_ports = {
            "reference_primitive": None,
            "reference_name": port_reference_name(args),
            "is_circuit_port": False,
            "p1": {},
            "p2": {},
        }
        if p1:
            edge_ports["p1"] = apply_aedt_edge_gap_port_template(app, getattr(p1, "name", str(p1)), args)
        if p2:
            edge_ports["p2"] = apply_aedt_edge_gap_port_template(app, getattr(p2, "name", str(p2)), args)
        edges["aedt_edge_template"] = edge_ports
    elif args.port_type == "wave":
        p1 = app.create_wave_port("input_feed", edges["p1_edge"]) if create_p1 else None
        p2 = app.create_wave_port("output_feed", edges["p2_edge"]) if create_p2 else None
    else:
        reference = ground_plane_name(args) if args.reference_ground_ports else None
        p1 = (
            app.create_edge_port(
                "input_feed",
                edges["p1_edge"],
                is_circuit_port=True,
                reference_primitive=reference,
                reference_edge_number=edges["p1_ref_edge"],
            )
            if create_p1
            else None
        )
        p2 = (
            app.create_edge_port(
                "output_feed",
                edges["p2_edge"],
                is_circuit_port=True,
                reference_primitive=reference,
                reference_edge_number=edges["p2_ref_edge"],
            )
            if create_p2
            else None
        )
    edges["created_port_numbers"] = [number for number, enabled in ((1, create_p1), (2, create_p2)) if enabled]
    edges["skipped_port_numbers"] = sorted(skip_port_numbers)
    for port in (p1, p2):
        if port:
            created.append(getattr(port, "name", str(port)))
    return created, edges


__all__ = [
    "BOTTOM_LAYER",
    "GROUND_PLANE",
    "TOP_LAYER",
    "create_gap_edge_ports_in_edb",
    "create_ports",
    "default_port_reference_name",
    "edge_midpoint_from_side",
    "find_port",
    "find_shape",
    "ground_plane_name",
    "net_for_shape",
    "patch_gap_ports_in_edb",
    "patch_pin_gap_ports_in_edb",
    "port_reference_name",
    "project_edb_path",
    "reference_ground_layer",
    "reference_point_on_gnd_boundary",
    "resolve_gnd_boundary",
    "resolve_port_edges",
    "shape_bounds",
    "signal_layer",
    "via_bottom_layer",
    "via_top_layer",
]
