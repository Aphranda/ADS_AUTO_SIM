#!/usr/bin/env python3
"""Build an HFSS 3D Layout JSON model from an ADS MCFIL DXF export.

The ADS MCFIL DXF observed for TX_BAND1 is a clean LWPOLYLINE-only export:
closed rectangular copper polygons on layer ``cond`` with DXF units set to
microns.  This tool converts that source into the SIMADS HFSS layout JSON
contract and emits a parameter file that can be edited for R1 sweeps.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
import math
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from simads.exporters.svg import write_svg
from simads.geometry import Boundary, LayerMap, Layout, Port, Rect, to_dict


DEFAULT_DXF = Path(
    r"D:\Work\ADS\TX_Band\mfg\TX_Band_lib_DA_CLFilter1_TX_BAND1\dxf\DA_CLFilter1_TX_BAND1.dxf"
)
DEFAULT_OUT_DIR = REPO_ROOT / "projects" / "RFSOC_RF" / "layouts" / "tx_band1_mcfil"
DEFAULT_LAYOUT_ID = "tx_band1_mcfil_r0"


DXF_INSUNITS_TO_MM = {
    0: ("Unitless", 1.0),
    1: ("Inches", 25.4),
    2: ("Feet", 304.8),
    4: ("Millimeters", 1.0),
    5: ("Centimeters", 10.0),
    6: ("Meters", 1000.0),
    8: ("Microinches", 25.4e-6),
    9: ("Mils", 0.0254),
    10: ("Yards", 914.4),
    12: ("Nanometers", 1e-6),
    13: ("Microns", 1e-3),
    14: ("Decimeters", 100.0),
}


@dataclass(frozen=True)
class DxfPolyline:
    index: int
    layer: str
    closed: bool
    raw_points: list[tuple[float, float]]
    points_mm: list[tuple[float, float]]
    bulges: list[float]
    constant_width: float | None


def _json_default(value: Any) -> str:
    return str(value)


def _round(value: float, digits: int = 6) -> float:
    return round(float(value), digits)


def _dxf_pairs(path: Path) -> list[tuple[int, str]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if len(lines) % 2:
        raise ValueError(f"DXF group-code stream has an odd line count: {path}")
    pairs: list[tuple[int, str]] = []
    for i in range(0, len(lines), 2):
        code_text = lines[i].strip()
        value = lines[i + 1].strip()
        try:
            code = int(code_text)
        except ValueError as exc:
            raise ValueError(f"invalid DXF group code {code_text!r} at line {i + 1}") from exc
        pairs.append((code, value))
    return pairs


def _sections(pairs: list[tuple[int, str]]) -> dict[str, list[tuple[int, str]]]:
    output: dict[str, list[tuple[int, str]]] = {}
    active: str | None = None
    expect_section_name = False
    for code, value in pairs:
        if code == 0 and value == "SECTION":
            expect_section_name = True
            active = None
            continue
        if expect_section_name and code == 2:
            active = value
            output.setdefault(active, [])
            expect_section_name = False
            continue
        if code == 0 and value == "ENDSEC":
            active = None
            continue
        if active is not None:
            output[active].append((code, value))
    return output


def _header_vars(header_pairs: list[tuple[int, str]]) -> dict[str, list[tuple[int, str]]]:
    variables: dict[str, list[tuple[int, str]]] = {}
    current: str | None = None
    for code, value in header_pairs:
        if code == 9:
            current = value
            variables.setdefault(current, [])
        elif current is not None:
            variables[current].append((code, value))
    return variables


def _first_int(values: list[tuple[int, str]], code: int) -> int | None:
    for item_code, item_value in values:
        if item_code == code:
            return int(item_value)
    return None


def _header_point(values: list[tuple[int, str]]) -> list[float] | None:
    coords: dict[int, float] = {}
    for code, value in values:
        if code in {10, 20, 30}:
            coords[code] = float(value)
    if 10 not in coords or 20 not in coords:
        return None
    return [coords[10], coords[20], coords.get(30, 0.0)]


def _unit_scale_mm(header: dict[str, list[tuple[int, str]]], override: float | None) -> tuple[int | None, str, float]:
    if override is not None:
        return None, "override", float(override)
    insunits = _first_int(header.get("$INSUNITS", []), 70)
    if insunits is None:
        return None, "missing $INSUNITS, assumed millimeters", 1.0
    name, scale = DXF_INSUNITS_TO_MM.get(insunits, (f"unsupported code {insunits}, assumed millimeters", 1.0))
    return insunits, name, scale


def _parse_lwpolylines(entity_pairs: list[tuple[int, str]], unit_scale_mm: float) -> list[DxfPolyline]:
    polylines: list[DxfPolyline] = []
    current_type: str | None = None
    current: list[tuple[int, str]] = []

    def flush() -> None:
        nonlocal current_type, current
        if current_type != "LWPOLYLINE":
            current_type = None
            current = []
            return
        layer = ""
        flags = 0
        raw_points: list[tuple[float, float]] = []
        bulges: list[float] = []
        constant_width: float | None = None
        pending_x: float | None = None
        for code, value in current:
            if code == 8:
                layer = value
            elif code == 70:
                flags = int(value)
            elif code == 43:
                constant_width = float(value) * unit_scale_mm
            elif code == 10:
                pending_x = float(value)
            elif code == 20 and pending_x is not None:
                raw_points.append((pending_x, float(value)))
                pending_x = None
            elif code == 42:
                bulges.append(float(value))
        polylines.append(
            DxfPolyline(
                index=len(polylines) + 1,
                layer=layer or "0",
                closed=bool(flags & 1),
                raw_points=raw_points,
                points_mm=[(x * unit_scale_mm, y * unit_scale_mm) for x, y in raw_points],
                bulges=bulges,
                constant_width=constant_width,
            )
        )
        current_type = None
        current = []

    for code, value in entity_pairs:
        if code == 0:
            flush()
            current_type = value
            current = []
            continue
        current.append((code, value))
    flush()
    return polylines


def _bbox(points: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return min(xs), min(ys), max(xs), max(ys)


def _area(points: list[tuple[float, float]]) -> float:
    total = 0.0
    for (xa, ya), (xb, yb) in zip(points, points[1:] + points[:1], strict=False):
        total += xa * yb - xb * ya
    return 0.5 * total


def _is_axis_aligned_rect(polyline: DxfPolyline, tol: float = 1e-9) -> bool:
    if not polyline.closed or len(polyline.points_mm) != 4:
        return False
    xs = {round(point[0], 9) for point in polyline.points_mm}
    ys = {round(point[1], 9) for point in polyline.points_mm}
    if len(xs) != 2 or len(ys) != 2:
        return False
    x0, y0, x1, y1 = _bbox(polyline.points_mm)
    expected = {(round(x0, 9), round(y0, 9)), (round(x0, 9), round(y1, 9)), (round(x1, 9), round(y0, 9)), (round(x1, 9), round(y1, 9))}
    actual = {(round(x, 9), round(y, 9)) for x, y in polyline.points_mm}
    return len(expected.symmetric_difference(actual)) <= tol


def _polyline_record(polyline: DxfPolyline) -> dict[str, Any]:
    x0, y0, x1, y1 = _bbox(polyline.points_mm)
    return {
        "index": polyline.index,
        "type": "LWPOLYLINE",
        "layer": polyline.layer,
        "closed": polyline.closed,
        "vertex_count": len(polyline.points_mm),
        "bbox_mm": [_round(x0), _round(y0), _round(x1), _round(y1)],
        "width_mm": _round(x1 - x0),
        "height_mm": _round(y1 - y0),
        "area_mm2": _round(abs(_area(polyline.points_mm))),
        "axis_aligned_rect": _is_axis_aligned_rect(polyline),
        "constant_width_mm": _round(polyline.constant_width) if polyline.constant_width is not None else None,
        "has_bulge": any(abs(item) > 1e-12 for item in polyline.bulges),
    }


def _group_sections(rects: list[dict[str, Any]], tol: float = 1e-6) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for rect in sorted(rects, key=lambda item: (-item["x1"], item["y0"])):
        match = None
        for group in groups:
            if abs(group["x0"] - rect["x0"]) <= tol and abs(group["x1"] - rect["x1"]) <= tol:
                match = group
                break
        if match is None:
            match = {"x0": rect["x0"], "x1": rect["x1"], "rects": []}
            groups.append(match)
        match["rects"].append(rect)

    sections: list[dict[str, Any]] = []
    for index, group in enumerate(sorted(groups, key=lambda item: -item["x1"]), start=1):
        members = sorted(group["rects"], key=lambda item: item["y0"])
        y_gaps = [
            _round(next_rect["y0"] - prev_rect["y1"])
            for prev_rect, next_rect in zip(members, members[1:], strict=False)
        ]
        x0 = min(item["x0"] for item in members)
        x1 = max(item["x1"] for item in members)
        y0 = min(item["y0"] for item in members)
        y1 = max(item["y1"] for item in members)
        sections.append(
            {
                "section": index,
                "x0_mm": _round(x0),
                "x1_mm": _round(x1),
                "length_mm": _round(x1 - x0),
                "bbox_mm": [_round(x0), _round(y0), _round(x1), _round(y1)],
                "strip_count": len(members),
                "coupling_gaps_mm": y_gaps,
                "strips": [
                    {
                        "source_entity": item["source_entity"],
                        "strip": strip_index,
                        "x0_mm": _round(item["x0"]),
                        "y0_mm": _round(item["y0"]),
                        "x1_mm": _round(item["x1"]),
                        "y1_mm": _round(item["y1"]),
                        "width_mm": _round(item["y1"] - item["y0"]),
                        "center_y_mm": _round((item["y0"] + item["y1"]) / 2.0),
                    }
                    for strip_index, item in enumerate(members, start=1)
                ],
            }
        )
    return sections


def _rects_from_polylines(polylines: list[DxfPolyline], metal_layer: str) -> list[dict[str, Any]]:
    rects: list[dict[str, Any]] = []
    for polyline in polylines:
        if not _is_axis_aligned_rect(polyline):
            continue
        x0, y0, x1, y1 = _bbox(polyline.points_mm)
        rects.append(
            {
                "source_entity": polyline.index,
                "layer": metal_layer,
                "x0": x0,
                "y0": y0,
                "x1": x1,
                "y1": y1,
            }
        )
    return rects


def _as_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    return float(value)


def _rects_from_params(params: dict[str, Any], metal_layer: str) -> list[dict[str, Any]]:
    global_params = params.get("global_parameters", {})
    if not isinstance(global_params, dict):
        global_params = {}
    global_x = _as_float(global_params.get("x_offset_mm"))
    global_y = _as_float(global_params.get("y_offset_mm"))
    rects: list[dict[str, Any]] = []
    sections = params.get("coupled_sections", [])
    if not isinstance(sections, list):
        raise ValueError("params JSON must contain a coupled_sections list")
    for section in sections:
        if not isinstance(section, dict):
            continue
        tuning = section.get("tuning", {})
        if not isinstance(tuning, dict):
            tuning = {}
        length_delta = _as_float(tuning.get("length_delta_mm"))
        width_delta = _as_float(tuning.get("width_delta_mm"))
        gap_delta = _as_float(tuning.get("gap_delta_mm"))
        section_x_delta = _as_float(tuning.get("x_delta_mm"))
        section_y_delta = _as_float(tuning.get("y_delta_mm"))
        strips = section.get("strips", [])
        if not isinstance(strips, list):
            continue
        clean_strips = [strip for strip in strips if isinstance(strip, dict)]
        sorted_strips = sorted(clean_strips, key=lambda item: _as_float(item.get("center_y_mm"), _as_float(item.get("y0_mm"))))
        separation_offsets: dict[int, float] = {}
        if len(sorted_strips) == 2 and abs(gap_delta) > 0.0:
            separation_offsets[id(sorted_strips[0])] = -gap_delta / 2.0
            separation_offsets[id(sorted_strips[1])] = gap_delta / 2.0
        for strip in sorted_strips:
            x0 = _as_float(strip.get("x0_mm"))
            x1 = _as_float(strip.get("x1_mm"))
            y0 = _as_float(strip.get("y0_mm"))
            y1 = _as_float(strip.get("y1_mm"))
            center_x = (x0 + x1) / 2.0 + global_x + section_x_delta
            center_y = _as_float(strip.get("center_y_mm"), (y0 + y1) / 2.0)
            center_y += global_y + section_y_delta + separation_offsets.get(id(strip), 0.0)
            length = max(0.001, (x1 - x0) + length_delta)
            width = max(0.001, (y1 - y0) + width_delta)
            rects.append(
                {
                    "source_entity": int(strip.get("source_entity") or 0),
                    "layer": metal_layer,
                    "x0": center_x - length / 2.0,
                    "y0": center_y - width / 2.0,
                    "x1": center_x + length / 2.0,
                    "y1": center_y + width / 2.0,
                }
            )
    return rects


def _layout_from_rects(
    *,
    layout_id: str,
    rects: list[dict[str, Any]],
    source_dxf: Path,
    boundary_margin_mm: float,
    metal_layer: str,
    boundary_layer: str,
    signal_layer: str,
    reference_ground_layer: str,
    include_ports: bool,
    p1_source_entity: int | None = None,
    p2_source_entity: int | None = None,
) -> Layout:
    if not rects:
        raise ValueError("no axis-aligned closed rectangular LWPOLYLINE entities were found")
    all_points = [(rect["x0"], rect["y0"]) for rect in rects] + [(rect["x1"], rect["y1"]) for rect in rects]
    x0, y0, x1, y1 = _bbox(all_points)
    boundary = Boundary(
        name="em_boundary",
        x=x0 - boundary_margin_mm,
        y=y0 - boundary_margin_mm,
        w=(x1 - x0) + 2.0 * boundary_margin_mm,
        h=(y1 - y0) + 2.0 * boundary_margin_mm,
        layer=boundary_layer,
        metadata={"role": "hfss_airbox_review_boundary", "source": str(source_dxf)},
    )
    sorted_rects = sorted(rects, key=lambda item: (-item["x1"], item["y0"]))
    # ADS MCFIL TX_BAND1 ports are on the outer coupled-line pair:
    # P1 = right-side lower strip, P2 = left-side upper strip.
    right_rect = max(rects, key=lambda item: (item["x1"], -item["y0"]))
    left_rect = min(rects, key=lambda item: (item["x0"], -item["y1"]))
    p1_entity = p1_source_entity or int(right_rect["source_entity"])
    p2_entity = p2_source_entity or int(left_rect["source_entity"])
    shapes: list[Any] = [boundary]
    for item_index, rect in enumerate(sorted_rects, start=1):
        source_entity = int(rect["source_entity"])
        name = f"mcfil_s{item_index:02d}_strip"
        role = "mcfil_coupled_strip"
        net = "RF"
        if include_ports and source_entity == p1_entity:
            name = "input_feed"
            role = "mcfil_candidate_input_feed"
            net = "RF"
            right_rect = rect
        elif include_ports and source_entity == p2_entity:
            name = "output_feed"
            role = "mcfil_candidate_output_feed"
            net = "RF"
            left_rect = rect
        shapes.append(
            Rect(
                name=name,
                layer=metal_layer,
                x=rect["x0"],
                y=rect["y0"],
                w=rect["x1"] - rect["x0"],
                h=rect["y1"] - rect["y0"],
                metadata={
                    "role": role,
                    "net": net,
                    "source_dxf_entity": source_entity,
                    "source_layer": "cond",
                    "hfss_signal_layer": signal_layer,
                    "port_candidate_needs_review": role.startswith("mcfil_candidate_"),
                },
            )
        )

    ports: list[Port] = []
    if include_ports:
        ports = [
            Port(
                name="P1",
                number=1,
                x=right_rect["x1"],
                y=(right_rect["y0"] + right_rect["y1"]) / 2.0,
                width=right_rect["y1"] - right_rect["y0"],
                layer=metal_layer,
                orientation_deg=0.0,
                reference=reference_ground_layer,
                metadata={"role": "candidate_port", "edge": "right", "source_dxf_entity": p1_entity, "needs_review": True},
            ),
            Port(
                name="P2",
                number=2,
                x=left_rect["x0"],
                y=(left_rect["y0"] + left_rect["y1"]) / 2.0,
                width=left_rect["y1"] - left_rect["y0"],
                layer=metal_layer,
                orientation_deg=180.0,
                reference=reference_ground_layer,
                metadata={"role": "candidate_port", "edge": "left", "source_dxf_entity": p2_entity, "needs_review": True},
            ),
        ]
    return Layout(
        layout_id=layout_id,
        units="mm",
        layers=[
            LayerMap(name=metal_layer, purpose="drawing", dxf_layer="cond"),
            LayerMap(name=boundary_layer, purpose="drawing", dxf_layer=boundary_layer),
        ],
        shapes=shapes,
        ports=ports,
        metadata={
            "source": "ADS MCFIL DXF",
            "source_dxf": str(source_dxf),
            "topology": "mcfil_coupled_line_bpf",
            "candidate_id": layout_id,
            "signal_layer": signal_layer,
            "reference_ground_layer": reference_ground_layer,
            "ground_plane_name": "hfss_ground_plane",
            "suppress_default_reference_ground_plane": False,
            "port_status": "candidate only; confirm MCFIL input/output edges before recreating HFSS ports",
        },
    )


def _params_from_sections(
    *,
    layout_id: str,
    source_dxf: Path,
    unit_code: int | None,
    unit_name: str,
    unit_scale_mm: float,
    sections: list[dict[str, Any]],
    bbox_mm: tuple[float, float, float, float],
    boundary_margin_mm: float,
    p1_source_entity: int | None = None,
    p2_source_entity: int | None = None,
) -> dict[str, Any]:
    x0, y0, x1, y1 = bbox_mm
    return {
        "schema_version": "0.1.0",
        "layout_id": layout_id,
        "source_dxf": str(source_dxf),
        "source_kind": "ADS MCFIL",
        "units": "mm",
        "dxf_units": {"insunits": unit_code, "name": unit_name, "scale_to_mm": unit_scale_mm},
        "frequency_plan": {
            "branch": "TX-F1 / TX_BAND1",
            "passband_GHz": [17.700, 19.325],
            "lo_stopband_GHz": [14.400, 15.025],
            "image_stopband_GHz": [10.1, 13.6],
            "targets": {
                "insertion_loss_max_dB": 2.5,
                "return_loss_min_dB": 15.0,
                "stopband_rejection_min_dB": 40.0,
                "group_delay_ripple_max_ns": 0.25,
            },
        },
        "global_parameters": {
            "x_offset_mm": 0.0,
            "y_offset_mm": 0.0,
            "boundary_margin_mm": boundary_margin_mm,
            "metal_thickness_mm": None,
            "substrate_stackup": "TBD; default HFSS profile currently points at config/stackups/JLC04161H_7628_1P6MM.json",
        },
        "source_bbox_mm": [_round(x0), _round(y0), _round(x1), _round(y1)],
        "source_size_mm": {"x": _round(x1 - x0), "y": _round(y1 - y0)},
        "coupled_sections": [
            {
                **section,
                "tuning": {
                    "length_delta_mm": 0.0,
                    "width_delta_mm": 0.0,
                    "gap_delta_mm": 0.0,
                    "x_delta_mm": 0.0,
                    "y_delta_mm": 0.0,
                },
            }
            for section in sections
        ],
        "editable_tuning_model": {
            "description": "R1 can rebuild each strip from x/y/length/width values below. Keep the R0 DXF layout as the reference geometry.",
            "supported_by_this_tool": "Edit coupled_sections[].tuning or global_parameters, then rerun this tool with --params-in.",
            "recommended_first_sweep": [
                "global y_offset_mm / connector feed alignment",
                "per-section coupling_gaps_mm",
                "per-section length_mm",
                "outer section strip widths",
            ],
        },
        "ports": {
            "status": "candidate only",
            "p1_source_entity": p1_source_entity,
            "p2_source_entity": p2_source_entity,
            "review_note": "MCFIL has open-coupled-line ends; confirm which physical open edges are P1/P2 before using --recreate-pcb-ports in HFSS.",
        },
    }


def build_from_dxf(args: argparse.Namespace) -> dict[str, Any]:
    dxf = args.dxf.resolve()
    pairs = _dxf_pairs(dxf)
    sections_raw = _sections(pairs)
    header = _header_vars(sections_raw.get("HEADER", []))
    unit_code, unit_name, unit_scale_mm = _unit_scale_mm(header, args.unit_scale_mm)
    polylines = _parse_lwpolylines(sections_raw.get("ENTITIES", []), unit_scale_mm)
    rects = _rects_from_polylines(polylines, args.metal_layer)
    all_points = [point for polyline in polylines for point in polyline.points_mm]
    if not all_points:
        raise ValueError(f"no LWPOLYLINE points found in {dxf}")
    bbox_mm = _bbox(all_points)
    sections = _group_sections(rects)
    auto_p1 = int(max(rects, key=lambda item: (item["x1"], -item["y0"]))["source_entity"]) if rects else None
    auto_p2 = int(min(rects, key=lambda item: (item["x0"], item["y0"]))["source_entity"]) if rects else None
    p1_source_entity = args.p1_source_entity or auto_p1
    p2_source_entity = args.p2_source_entity or auto_p2
    layout = _layout_from_rects(
        layout_id=args.layout_id,
        rects=rects,
        source_dxf=dxf,
        boundary_margin_mm=args.boundary_margin_mm,
        metal_layer=args.metal_layer,
        boundary_layer=args.boundary_layer,
        signal_layer=args.signal_layer,
        reference_ground_layer=args.reference_ground_layer,
        include_ports=not args.no_candidate_ports,
        p1_source_entity=p1_source_entity,
        p2_source_entity=p2_source_entity,
    )
    params = _params_from_sections(
        layout_id=args.layout_id,
        source_dxf=dxf,
        unit_code=unit_code,
        unit_name=unit_name,
        unit_scale_mm=unit_scale_mm,
        sections=sections,
        bbox_mm=bbox_mm,
        boundary_margin_mm=args.boundary_margin_mm,
        p1_source_entity=p1_source_entity,
        p2_source_entity=p2_source_entity,
    )
    header_summary = {
        "ACADVER": header.get("$ACADVER", []),
        "INSUNITS": unit_code,
        "INSUNITS_name": unit_name,
        "unit_scale_mm": unit_scale_mm,
        "EXTMIN_raw": _header_point(header.get("$EXTMIN", [])),
        "EXTMAX_raw": _header_point(header.get("$EXTMAX", [])),
    }
    summary = {
        "source_dxf": str(dxf),
        "layout_id": args.layout_id,
        "header": header_summary,
        "entity_counts": dict(Counter(["LWPOLYLINE" for _ in polylines])),
        "layer_counts": dict(Counter(polyline.layer for polyline in polylines)),
        "polyline_count": len(polylines),
        "axis_aligned_rect_count": len(rects),
        "unsupported_polyline_count": len(polylines) - len(rects),
        "bbox_mm": [_round(item) for item in bbox_mm],
        "size_mm": {"x": _round(bbox_mm[2] - bbox_mm[0]), "y": _round(bbox_mm[3] - bbox_mm[1])},
        "polylines": [_polyline_record(polyline) for polyline in polylines],
        "coupled_sections": sections,
        "candidate_ports": {"p1_source_entity": p1_source_entity, "p2_source_entity": p2_source_entity},
        "warnings": [
            "Ports are candidate metadata only until MCFIL P1/P2 edges are confirmed.",
            "No vias or backside ground features were present in this DXF; HFSS reference ground is created from the EM boundary by existing tooling.",
        ],
    }
    return {"layout": layout, "params": params, "summary": summary}


def build_from_params(args: argparse.Namespace) -> dict[str, Any]:
    params_path = args.params_in.resolve()
    params = json.loads(params_path.read_text(encoding="utf-8-sig"))
    if not isinstance(params, dict):
        raise ValueError(f"params JSON must contain an object: {params_path}")
    layout_id = args.layout_id or str(params.get("layout_id") or DEFAULT_LAYOUT_ID)
    global_params = params.get("global_parameters", {})
    if not isinstance(global_params, dict):
        global_params = {}
    boundary_margin_mm = _as_float(global_params.get("boundary_margin_mm"), args.boundary_margin_mm)
    source_dxf = Path(str(params.get("source_dxf") or args.dxf))
    rects = _rects_from_params(params, args.metal_layer)
    ports_params = params.get("ports", {})
    if not isinstance(ports_params, dict):
        ports_params = {}
    p1_source_entity = args.p1_source_entity or ports_params.get("p1_source_entity")
    p2_source_entity = args.p2_source_entity or ports_params.get("p2_source_entity")
    layout = _layout_from_rects(
        layout_id=layout_id,
        rects=rects,
        source_dxf=source_dxf,
        boundary_margin_mm=boundary_margin_mm,
        metal_layer=args.metal_layer,
        boundary_layer=args.boundary_layer,
        signal_layer=args.signal_layer,
        reference_ground_layer=args.reference_ground_layer,
        include_ports=not args.no_candidate_ports,
        p1_source_entity=int(p1_source_entity) if p1_source_entity else None,
        p2_source_entity=int(p2_source_entity) if p2_source_entity else None,
    )
    all_points = [(rect["x0"], rect["y0"]) for rect in rects] + [(rect["x1"], rect["y1"]) for rect in rects]
    bbox_mm = _bbox(all_points)
    sections = _group_sections(rects)
    summary = {
        "source_params": str(params_path),
        "source_dxf": str(source_dxf),
        "layout_id": layout_id,
        "build_mode": "params",
        "axis_aligned_rect_count": len(rects),
        "bbox_mm": [_round(item) for item in bbox_mm],
        "size_mm": {"x": _round(bbox_mm[2] - bbox_mm[0]), "y": _round(bbox_mm[3] - bbox_mm[1])},
        "coupled_sections": sections,
        "warnings": [
            "This layout was regenerated from editable parameters, not directly from the source DXF.",
            "Ports are candidate metadata only until MCFIL P1/P2 edges are confirmed.",
        ],
    }
    params = dict(params)
    params["layout_id"] = layout_id
    params["last_build_mode"] = "params"
    params["last_build_source_params"] = str(params_path)
    return {"layout": layout, "params": params, "summary": summary}


def write_outputs(payload: dict[str, Any], args: argparse.Namespace) -> dict[str, Path]:
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    layout_path = out_dir / f"{args.layout_id}_layout.json"
    params_path = out_dir / f"{args.layout_id}_params.json"
    summary_path = out_dir / f"{args.layout_id}_dxf_summary.json"
    svg_path = out_dir / f"{args.layout_id}_review.svg"

    layout: Layout = payload["layout"]
    layout_path.write_text(json.dumps(to_dict(layout), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    params_path.write_text(json.dumps(payload["params"], ensure_ascii=False, indent=2, default=_json_default) + "\n", encoding="utf-8")
    summary_path.write_text(json.dumps(payload["summary"], ensure_ascii=False, indent=2, default=_json_default) + "\n", encoding="utf-8")
    write_svg(svg_path, layout, title=f"{args.layout_id} ADS MCFIL DXF review", padding=args.svg_padding_mm)
    return {"layout": layout_path, "params": params_path, "summary": summary_path, "svg": svg_path}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert ADS MCFIL DXF rectangles to HFSS 3D Layout JSON plus parameter inventory.")
    parser.add_argument("--dxf", type=Path, default=DEFAULT_DXF)
    parser.add_argument("--params-in", type=Path, default=None, help="Regenerate layout from an editable *_params.json file instead of re-reading DXF.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--layout-id", default=DEFAULT_LAYOUT_ID)
    parser.add_argument("--unit-scale-mm", type=float, default=None, help="Override DXF coordinate to millimeter scale.")
    parser.add_argument("--boundary-margin-mm", type=float, default=0.6)
    parser.add_argument("--svg-padding-mm", type=float, default=0.4)
    parser.add_argument("--metal-layer", default="cond")
    parser.add_argument("--boundary-layer", default="EM_BOUNDARY")
    parser.add_argument("--signal-layer", default="ETCH_TOP")
    parser.add_argument("--reference-ground-layer", default="ETCH_INNER1")
    parser.add_argument("--no-candidate-ports", action="store_true")
    parser.add_argument("--p1-source-entity", type=int, default=None, help="DXF entity index to name as input_feed.")
    parser.add_argument("--p2-source-entity", type=int, default=None, help="DXF entity index to name as output_feed.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_from_params(args) if args.params_in is not None else build_from_dxf(args)
    outputs = write_outputs(payload, args)
    summary = payload["summary"]
    report = {
        "status": "ok",
        "outputs": {key: str(path) for key, path in outputs.items()},
        "summary": {
            "build_mode": summary.get("build_mode", "dxf"),
            "polyline_count": summary.get("polyline_count"),
            "axis_aligned_rect_count": summary["axis_aligned_rect_count"],
            "bbox_mm": summary["bbox_mm"],
            "size_mm": summary["size_mm"],
            "coupled_section_count": len(summary["coupled_sections"]),
        },
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
