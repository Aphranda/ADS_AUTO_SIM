#!/usr/bin/env python3
"""Generate FR4 L3 folded-SIR bandpass filter layout candidates for ADS."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from html import escape
import argparse
import csv
import json
import math
from pathlib import Path
import sys

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.exporters.json import write_layout_json
from simads.geometry import Boundary, LayerMap, Layout, Polygon, Port, Rect as LayoutRect, Via


@dataclass(frozen=True)
class FoldedSirParams:
    name: str = "folded_sir_l3_base"
    substrate: str = "FR4_L3_REF"
    er: float = 4.6
    dielectric_height_mm: float = 1.2906
    copper_thickness_mm: float = 0.035
    lower_cutoff_ghz: float = 6.0
    upper_cutoff_ghz: float = 8.0
    f0_ghz: float = 7.0
    order: int = 4
    z0_ohm: float = 50.0
    feed_w_mm: float = 2.35421
    feed_len_mm: float = 3.2
    feed_gap_t1_mm: float = 1.00
    feed_tip_w_mm: float = 0.18
    feed_overlap_mm: float = 0.08
    lower_w1_mm: float = 0.24
    lower_arm_l1_mm: float = 5.30
    lower_span_l2_mm: float = 7.60
    lower_top_bridge_w_mm: float = 0.76
    lower_bottom_l2_mm: float = 2.15
    via_diameter_mm: float = 0.30
    via_pad_size_mm: float = 0.42
    via_edge_clearance_mm: float = 0.06
    via_offset_d1_mm: float = 0.00
    upper_w1_mm: float = 0.30
    upper_w2_mm: float = 0.70
    upper_fold_h_mm: float = 1.85
    upper_left_l3_mm: float = 2.70
    upper_right_l4_mm: float = 4.35
    upper_margin_x_mm: float = 0.20
    main_gap_s1_mm: float = 0.24
    side_gap_s2_mm: float = 0.24
    fold_offset_d2_mm: float = 0.65
    boundary_margin_mm: float = 3.00
    min_fab_feature_mm: float = 0.1524
    metal_layer: str = "cond"
    via_layer: str = "pcvia1"


@dataclass(frozen=True)
class Rect:
    name: str
    layer: str
    x: float
    y: float
    w: float
    h: float


@dataclass(frozen=True)
class Quad:
    name: str
    layer: str
    points: list[tuple[float, float]]


def fmt(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def parse_float(row: dict[str, str], key: str, default: float) -> float:
    value = row.get(key, "").strip()
    return default if not value else float(value)


def parse_int(row: dict[str, str], key: str, default: int) -> int:
    value = row.get(key, "").strip()
    return default if not value else int(value)


def row_to_params(row: dict[str, str]) -> FoldedSirParams:
    defaults = FoldedSirParams()
    return FoldedSirParams(
        name=row["name"].strip(),
        substrate=row.get("substrate", defaults.substrate).strip() or defaults.substrate,
        er=parse_float(row, "er", defaults.er),
        dielectric_height_mm=parse_float(row, "h_mm", defaults.dielectric_height_mm),
        copper_thickness_mm=parse_float(row, "copper_mm", defaults.copper_thickness_mm),
        lower_cutoff_ghz=parse_float(row, "lower_cutoff_ghz", defaults.lower_cutoff_ghz),
        upper_cutoff_ghz=parse_float(row, "upper_cutoff_ghz", defaults.upper_cutoff_ghz),
        f0_ghz=parse_float(row, "f0_ghz", defaults.f0_ghz),
        order=parse_int(row, "order", defaults.order),
        feed_w_mm=parse_float(row, "feed_w_mm", defaults.feed_w_mm),
        feed_len_mm=parse_float(row, "feed_len_mm", defaults.feed_len_mm),
        feed_gap_t1_mm=parse_float(row, "feed_gap_t1_mm", defaults.feed_gap_t1_mm),
        feed_tip_w_mm=parse_float(row, "feed_tip_w_mm", defaults.feed_tip_w_mm),
        feed_overlap_mm=parse_float(row, "feed_overlap_mm", defaults.feed_overlap_mm),
        lower_w1_mm=parse_float(row, "lower_w1_mm", defaults.lower_w1_mm),
        lower_arm_l1_mm=parse_float(row, "lower_arm_l1_mm", defaults.lower_arm_l1_mm),
        lower_span_l2_mm=parse_float(row, "lower_span_l2_mm", defaults.lower_span_l2_mm),
        lower_top_bridge_w_mm=parse_float(row, "lower_top_bridge_w_mm", defaults.lower_top_bridge_w_mm),
        lower_bottom_l2_mm=parse_float(row, "lower_bottom_l2_mm", defaults.lower_bottom_l2_mm),
        via_diameter_mm=parse_float(row, "via_diameter_mm", defaults.via_diameter_mm),
        via_pad_size_mm=parse_float(row, "via_pad_size_mm", defaults.via_pad_size_mm),
        via_edge_clearance_mm=parse_float(row, "via_edge_clearance_mm", defaults.via_edge_clearance_mm),
        via_offset_d1_mm=parse_float(row, "via_offset_d1_mm", defaults.via_offset_d1_mm),
        upper_w1_mm=parse_float(row, "upper_w1_mm", defaults.upper_w1_mm),
        upper_w2_mm=parse_float(row, "upper_w2_mm", defaults.upper_w2_mm),
        upper_fold_h_mm=parse_float(row, "upper_fold_h_mm", defaults.upper_fold_h_mm),
        upper_left_l3_mm=parse_float(row, "upper_left_l3_mm", defaults.upper_left_l3_mm),
        upper_right_l4_mm=parse_float(row, "upper_right_l4_mm", defaults.upper_right_l4_mm),
        upper_margin_x_mm=parse_float(row, "upper_margin_x_mm", defaults.upper_margin_x_mm),
        main_gap_s1_mm=parse_float(row, "main_gap_s1_mm", defaults.main_gap_s1_mm),
        side_gap_s2_mm=parse_float(row, "side_gap_s2_mm", defaults.side_gap_s2_mm),
        fold_offset_d2_mm=parse_float(row, "fold_offset_d2_mm", defaults.fold_offset_d2_mm),
        boundary_margin_mm=parse_float(row, "boundary_margin_mm", defaults.boundary_margin_mm),
        min_fab_feature_mm=parse_float(row, "min_fab_feature_mm", defaults.min_fab_feature_mm),
        metal_layer=row.get("metal_layer", defaults.metal_layer).strip() or defaults.metal_layer,
        via_layer=row.get("via_layer", defaults.via_layer).strip() or defaults.via_layer,
    )


def shape_points(shape: Rect | Quad) -> list[tuple[float, float]]:
    if isinstance(shape, Quad):
        return shape.points
    return [
        (shape.x, shape.y),
        (shape.x + shape.w, shape.y),
        (shape.x + shape.w, shape.y + shape.h),
        (shape.x, shape.y + shape.h),
    ]


def rect_bounds(rects: list[Rect | Quad]) -> tuple[float, float, float, float]:
    points = [point for rect in rects for point in shape_points(rect)]
    min_x = min(point[0] for point in points)
    min_y = min(point[1] for point in points)
    max_x = max(point[0] for point in points)
    max_y = max(point[1] for point in points)
    return min_x, min_y, max_x, max_y


def shape_min_feature(shape: Rect | Quad) -> float:
    if isinstance(shape, Rect):
        return min(shape.w, shape.h)
    points = shape.points
    edges = [
        math.hypot(xb - xa, yb - ya)
        for (xa, ya), (xb, yb) in zip(points, points[1:] + points[:1], strict=False)
    ]
    return min(edges)


def add_boundary(rects: list[Rect | Quad], params: FoldedSirParams) -> None:
    metal_rects = [rect for rect in rects if rect.layer != "EM_BOUNDARY"]
    min_x, min_y, max_x, max_y = rect_bounds(metal_rects)
    rects.append(
        Rect(
            "em_boundary",
            "EM_BOUNDARY",
            min_x - params.boundary_margin_mm,
            min_y - params.boundary_margin_mm,
            max_x - min_x + 2.0 * params.boundary_margin_mm,
            max_y - min_y + 2.0 * params.boundary_margin_mm,
        )
    )


def orange_fold_geometry(params: FoldedSirParams) -> tuple[float, float, float, float]:
    center_x = params.lower_span_l2_mm / 2.0
    max_half_span = params.lower_span_l2_mm / 2.0 - params.upper_margin_x_mm
    half_span = min(params.upper_right_l4_mm, max_half_span)
    if half_span <= params.upper_w2_mm:
        raise ValueError("orange folded line half span is too small for the step width")
    top_arm_len = min(params.upper_left_l3_mm, half_span - params.fold_offset_d2_mm)
    if top_arm_len <= params.upper_w2_mm:
        raise ValueError("orange folded line top arm is too short")
    return center_x - half_span, center_x + half_span, center_x, top_arm_len


def via_pad_y_for_bottom_edge_aligned_trace(trace_y: float) -> float:
    """Align the square via-pad lower edge to the trace lower edge."""
    return trace_y


def orange_via_pad_to_purple_gap(params: FoldedSirParams) -> float:
    return params.main_gap_s1_mm


def build_rects(params: FoldedSirParams) -> tuple[list[Rect | Quad], dict[str, tuple[float, float]]]:
    if params.order != 4:
        raise ValueError("This folded-SIR branch is currently parameterized as a 4th-order topology.")

    rects: list[Rect | Quad] = []
    lower_left_x = 0.0
    lower_right_x = params.lower_span_l2_mm - params.lower_w1_mm
    lower_top_y = params.lower_arm_l1_mm - params.lower_top_bridge_w_mm
    lower_mid_gap = params.side_gap_s2_mm
    lower_top_segment_w = (params.lower_span_l2_mm - lower_mid_gap) / 2.0
    lower_right_top_x = lower_top_segment_w + lower_mid_gap
    lower_bottom_y = 0.0
    lower_bottom_w = params.lower_w1_mm
    lower_right_bottom_x = params.lower_span_l2_mm - params.lower_bottom_l2_mm

    rects.extend(
        [
            Rect("purple_u_left_vertical_arm", params.metal_layer, lower_left_x, 0.0, params.lower_w1_mm, params.lower_arm_l1_mm),
            Rect("purple_u_right_vertical_arm", params.metal_layer, lower_right_x, 0.0, params.lower_w1_mm, params.lower_arm_l1_mm),
            Rect("purple_u_left_top_arm", params.metal_layer, 0.0, lower_top_y, lower_top_segment_w, params.lower_top_bridge_w_mm),
            Rect("purple_u_right_top_arm", params.metal_layer, lower_right_top_x, lower_top_y, lower_top_segment_w, params.lower_top_bridge_w_mm),
            Rect("purple_u_left_bottom_arm", params.metal_layer, 0.0, lower_bottom_y, params.lower_bottom_l2_mm, lower_bottom_w),
            Rect("purple_u_right_bottom_arm", params.metal_layer, lower_right_bottom_x, lower_bottom_y, params.lower_bottom_l2_mm, lower_bottom_w),
        ]
    )

    via_r = params.via_diameter_mm / 2.0
    via_end_compensation = via_r + params.via_edge_clearance_mm + params.via_offset_d1_mm
    left_via_cx = lower_left_x + params.lower_bottom_l2_mm - via_end_compensation
    right_via_cx = lower_right_bottom_x + via_end_compensation
    via_pad = params.via_pad_size_mm
    lower_via_pad_y = via_pad_y_for_bottom_edge_aligned_trace(lower_bottom_y)
    via_cy = lower_via_pad_y + via_pad / 2.0
    rects.extend(
        [
            Rect("purple_u_left_via_pad", params.metal_layer, left_via_cx - via_pad / 2.0, lower_via_pad_y, via_pad, via_pad),
            Rect("purple_u_right_via_pad", params.metal_layer, right_via_cx - via_pad / 2.0, lower_via_pad_y, via_pad, via_pad),
            Rect("ground_via_left", params.via_layer, left_via_cx - via_r, via_cy - via_r, params.via_diameter_mm, params.via_diameter_mm),
            Rect("ground_via_right", params.via_layer, right_via_cx - via_r, via_cy - via_r, params.via_diameter_mm, params.via_diameter_mm),
        ]
    )

    feed_center_y = lower_bottom_y + lower_bottom_w / 2.0
    feed_y = feed_center_y - params.feed_w_mm / 2.0
    feed_taper_len = params.feed_gap_t1_mm
    feed_tip_y0 = feed_center_y - params.feed_tip_w_mm / 2.0
    feed_tip_y1 = feed_center_y + params.feed_tip_w_mm / 2.0
    left_tip_x = lower_left_x + params.feed_overlap_mm
    right_tip_x = params.lower_span_l2_mm - params.feed_overlap_mm
    left_feed_x1 = left_tip_x - feed_taper_len
    input_x0 = left_feed_x1 - params.feed_len_mm
    right_feed_x0 = right_tip_x + feed_taper_len
    rects.extend(
        [
            Rect("input_feed_50ohm", params.metal_layer, input_x0, feed_y, params.feed_len_mm, params.feed_w_mm),
            Quad(
                "input_feed_taper_to_purple_u",
                params.metal_layer,
                [
                    (left_feed_x1, feed_y),
                    (left_feed_x1, feed_y + params.feed_w_mm),
                    (left_tip_x, feed_tip_y1),
                    (left_tip_x, feed_tip_y0),
                ],
            ),
            Quad(
                "output_feed_taper_to_purple_u",
                params.metal_layer,
                [
                    (right_tip_x, feed_tip_y0),
                    (right_tip_x, feed_tip_y1),
                    (right_feed_x0, feed_y + params.feed_w_mm),
                    (right_feed_x0, feed_y),
                ],
            ),
            Rect("output_feed_50ohm", params.metal_layer, right_feed_x0, feed_y, params.feed_len_mm, params.feed_w_mm),
        ]
    )

    upper_y0 = params.lower_arm_l1_mm + params.main_gap_s1_mm
    upper_top_y = upper_y0 + params.upper_fold_h_mm
    upper_x0, upper_x1, center_x, top_arm_len = orange_fold_geometry(params)

    rects.extend(
        [
            Rect("orange_folded_line_lower_arm", params.metal_layer, upper_x0, upper_y0, upper_x1 - upper_x0, params.upper_w1_mm),
            Rect("orange_folded_line_left_step", params.metal_layer, upper_x0, upper_y0, params.upper_w2_mm, params.upper_fold_h_mm),
            Rect("orange_folded_line_left_top_arm", params.metal_layer, upper_x0, upper_top_y - params.upper_w1_mm, top_arm_len, params.upper_w1_mm),
            Rect("orange_folded_line_right_top_arm", params.metal_layer, upper_x1 - top_arm_len, upper_top_y - params.upper_w1_mm, top_arm_len, params.upper_w1_mm),
            Rect("orange_folded_line_right_step", params.metal_layer, upper_x1 - params.upper_w2_mm, upper_y0, params.upper_w2_mm, params.upper_fold_h_mm),
        ]
    )

    upper_via_cx = center_x
    upper_via_pad_y = via_pad_y_for_bottom_edge_aligned_trace(upper_y0)
    upper_via_cy = upper_via_pad_y + via_pad / 2.0
    rects.append(
        Rect(
            "orange_folded_line_via_pad",
            params.metal_layer,
            upper_via_cx - via_pad / 2.0,
            upper_via_pad_y,
            via_pad,
            via_pad,
        )
    )
    rects.append(
        Rect(
            "ground_via_upper_sir",
            params.via_layer,
            upper_via_cx - via_r,
            upper_via_cy - via_r,
            params.via_diameter_mm,
            params.via_diameter_mm,
        )
    )

    add_boundary(rects, params)
    ports = {
        "P1": (input_x0, feed_y + params.feed_w_mm / 2.0),
        "P2": (right_feed_x0 + params.feed_len_mm, feed_y + params.feed_w_mm / 2.0),
    }
    return rects, ports


def build_layout(
    params: FoldedSirParams,
    rects: list[Rect | Quad] | None = None,
    ports: dict[str, tuple[float, float]] | None = None,
) -> Layout:
    if rects is None or ports is None:
        rects, ports = build_rects(params)

    shapes: list[LayoutRect | Polygon | Via | Boundary] = []
    for shape in rects:
        if isinstance(shape, Quad):
            shapes.append(Polygon(name=shape.name, layer=shape.layer, points=shape.points))
            continue
        if shape.layer == "EM_BOUNDARY":
            shapes.append(Boundary(name=shape.name, x=shape.x, y=shape.y, w=shape.w, h=shape.h, layer=shape.layer))
            continue
        if shape.name.startswith("ground_via_"):
            shapes.append(
                Via(
                    name=shape.name,
                    layer=shape.layer,
                    x=shape.x + shape.w / 2.0,
                    y=shape.y + shape.h / 2.0,
                    diameter=shape.w,
                    metadata={"source": "generate_folded_sir_bpf_layout"},
                )
            )
            continue
        shapes.append(LayoutRect(name=shape.name, layer=shape.layer, x=shape.x, y=shape.y, w=shape.w, h=shape.h))

    layout_ports = [
        Port(name=name, number=idx, x=x, y=y, width=params.feed_w_mm, layer=params.metal_layer)
        for idx, (name, (x, y)) in enumerate(sorted(ports.items()), start=1)
    ]
    return Layout(
        layout_id=params.name,
        units="mm",
        layers=[
            LayerMap(name=params.metal_layer, dxf_layer=params.metal_layer),
            LayerMap(name=params.via_layer, dxf_layer=params.via_layer),
            LayerMap(name="EM_BOUNDARY", dxf_layer="EM_BOUNDARY"),
        ],
        shapes=shapes,
        ports=layout_ports,
        metadata={
            "generator": "tools/generate_folded_sir_bpf_layout.py",
            "topology": "folded_sir_bpf",
            "order": params.order,
            "substrate": params.substrate,
            "er": params.er,
            "dielectric_height_mm": params.dielectric_height_mm,
            "copper_thickness_mm": params.copper_thickness_mm,
            "reference_plane": "L3",
        },
    )


def write_dxf(path: Path, rects: list[Rect | Quad], coord_scale: float = 1.0, insunits: int = 4) -> None:
    lines = [
        "0",
        "SECTION",
        "2",
        "HEADER",
        "9",
        "$INSUNITS",
        "70",
        str(insunits),
        "0",
        "ENDSEC",
        "0",
        "SECTION",
        "2",
        "ENTITIES",
    ]
    for rect in rects:
        if isinstance(rect, Quad):
            points = [(x * coord_scale, y * coord_scale) for x, y in rect.points]
            lines.extend(
                [
                    "0",
                    "SOLID",
                    "8",
                    rect.layer,
                    "10",
                    fmt(points[0][0]),
                    "20",
                    fmt(points[0][1]),
                    "30",
                    "0",
                    "11",
                    fmt(points[1][0]),
                    "21",
                    fmt(points[1][1]),
                    "31",
                    "0",
                    "12",
                    fmt(points[2][0]),
                    "22",
                    fmt(points[2][1]),
                    "32",
                    "0",
                    "13",
                    fmt(points[3][0]),
                    "23",
                    fmt(points[3][1]),
                    "33",
                    "0",
                ]
            )
            continue

        x0, y0 = rect.x * coord_scale, rect.y * coord_scale
        x1, y1 = (rect.x + rect.w) * coord_scale, (rect.y + rect.h) * coord_scale
        if rect.name.startswith("ground_via_"):
            cx = (rect.x + rect.w / 2.0) * coord_scale
            cy = (rect.y + rect.h / 2.0) * coord_scale
            radius = rect.w / 2.0 * coord_scale
            lines.extend(["0", "CIRCLE", "8", rect.layer, "10", fmt(cx), "20", fmt(cy), "30", "0", "40", fmt(radius)])
            continue
        if rect.layer != "EM_BOUNDARY":
            lines.extend(
                [
                    "0",
                    "SOLID",
                    "8",
                    rect.layer,
                    "10",
                    fmt(x0),
                    "20",
                    fmt(y0),
                    "30",
                    "0",
                    "11",
                    fmt(x1),
                    "21",
                    fmt(y0),
                    "31",
                    "0",
                    "12",
                    fmt(x0),
                    "22",
                    fmt(y1),
                    "32",
                    "0",
                    "13",
                    fmt(x1),
                    "23",
                    fmt(y1),
                    "33",
                    "0",
                ]
            )
            continue
        points = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
        for (xa, ya), (xb, yb) in zip(points, points[1:], strict=False):
            lines.extend(["0", "LINE", "8", rect.layer, "10", fmt(xa), "20", fmt(ya), "30", "0", "11", fmt(xb), "21", fmt(yb), "31", "0"])
    lines.extend(["0", "ENDSEC", "0", "EOF"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_svg(path: Path, rects: list[Rect | Quad], params: FoldedSirParams, ports: dict[str, tuple[float, float]]) -> None:
    min_x, min_y, max_x, max_y = rect_bounds(rects)
    width = max_x - min_x
    height = max_y - min_y
    scale = 42
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(width * scale)}" height="{fmt(height * scale)}" viewBox="{fmt(min_x)} {fmt(min_y)} {fmt(width)} {fmt(height)}">',
        f'<rect x="{fmt(min_x)}" y="{fmt(min_y)}" width="{fmt(width)}" height="{fmt(height)}" fill="#fff"/>',
    ]
    for rect in rects:
        if isinstance(rect, Quad):
            points = " ".join(f"{fmt(x)},{fmt(y)}" for x, y in rect.points)
            parts.append(f'<polygon points="{points}" fill="#9aa0d4" stroke="#36396f" stroke-width="0.025"/>')
        elif rect.layer == "EM_BOUNDARY":
            parts.append(f'<rect x="{fmt(rect.x)}" y="{fmt(rect.y)}" width="{fmt(rect.w)}" height="{fmt(rect.h)}" fill="none" stroke="#888" stroke-dasharray="0.18 0.12" stroke-width="0.035"/>')
        elif rect.name.startswith("ground_via_"):
            parts.append(f'<circle cx="{fmt(rect.x + rect.w / 2.0)}" cy="{fmt(rect.y + rect.h / 2.0)}" r="{fmt(rect.w / 2.0)}" fill="#111"/>')
        elif rect.name.startswith("orange_folded_line_"):
            parts.append(f'<rect x="{fmt(rect.x)}" y="{fmt(rect.y)}" width="{fmt(rect.w)}" height="{fmt(rect.h)}" fill="#e67817" stroke="#603300" stroke-width="0.025"/>')
        elif rect.name.startswith("purple_u_"):
            parts.append(f'<rect x="{fmt(rect.x)}" y="{fmt(rect.y)}" width="{fmt(rect.w)}" height="{fmt(rect.h)}" fill="#b64a87" stroke="#4a1836" stroke-width="0.025"/>')
        else:
            parts.append(f'<rect x="{fmt(rect.x)}" y="{fmt(rect.y)}" width="{fmt(rect.w)}" height="{fmt(rect.h)}" fill="#9aa0d4" stroke="#36396f" stroke-width="0.025"/>')
    for name, (x, y) in ports.items():
        parts.append(f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="0.13" fill="#1769ff"/>')
        parts.append(f'<text x="{fmt(x + 0.15)}" y="{fmt(y - 0.15)}" font-size="0.32">{escape(name)}</text>')
    parts.append(f'<text x="{fmt(min_x + 0.2)}" y="{fmt(min_y + 0.45)}" font-size="0.35" fill="#333">{escape(params.name)} folded SIR BPF, FR4 L3</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def make_drc(params: FoldedSirParams, rects: list[Rect | Quad]) -> str:
    metal_rects = [rect for rect in rects if rect.layer == params.metal_layer]
    core_rects = [
        rect
        for rect in metal_rects
        if rect.name.startswith("purple_u_") or rect.name.startswith("orange_folded_line_")
    ]
    min_width = min(shape_min_feature(rect) for rect in metal_rects)
    orange_pad_to_purple_gap = orange_via_pad_to_purple_gap(params)
    min_gap = min(params.main_gap_s1_mm, params.side_gap_s2_mm, orange_pad_to_purple_gap)
    via_pad_covers_drill = params.via_pad_size_mm >= params.via_diameter_mm + 2.0 * params.via_edge_clearance_mm
    via_r = params.via_diameter_mm / 2.0
    via_end_clearance = params.via_edge_clearance_mm + params.via_offset_d1_mm
    lower_via_inside_bottom = via_end_clearance >= params.via_edge_clearance_mm
    lower_via_away_from_corner = (
        params.lower_bottom_l2_mm - params.via_edge_clearance_mm - params.via_offset_d1_mm - params.via_diameter_mm
        >= params.lower_w1_mm / 2.0
    )
    upper_x0, upper_x1, center_x, top_arm_len = orange_fold_geometry(params)
    metal_min_x, metal_min_y, metal_max_x, metal_max_y = rect_bounds(metal_rects)
    core_min_x, core_min_y, core_max_x, core_max_y = rect_bounds(core_rects)
    return "\n".join(
        [
            f"Design: {params.name}",
            f"Substrate: {params.substrate}, er={fmt(params.er)}, h={fmt(params.dielectric_height_mm)} mm, copper={fmt(params.copper_thickness_mm)} mm",
            f"Band target: {fmt(params.lower_cutoff_ghz)}-{fmt(params.upper_cutoff_ghz)} GHz, f0={fmt(params.f0_ghz)} GHz, order={params.order}",
            "",
            "Fabrication check",
            f"  Rule minimum: {fmt(params.min_fab_feature_mm)} mm (6 mil)",
            f"  Minimum metal width: {fmt(min_width)} mm -> {'PASS' if min_width >= params.min_fab_feature_mm else 'FAIL'}",
            f"  Minimum coupling/feed gap: {fmt(min_gap)} mm -> {'PASS' if min_gap >= params.min_fab_feature_mm else 'FAIL'}",
            f"  Via drawing diameter: {fmt(params.via_diameter_mm)} mm -> {'PASS' if params.via_diameter_mm >= params.min_fab_feature_mm else 'FAIL'}",
            f"  Via pad size: {fmt(params.via_pad_size_mm)} mm -> {'PASS' if via_pad_covers_drill else 'FAIL'}",
            f"  Purple U via end clearance: {fmt(via_end_clearance)} mm -> {'PASS' if lower_via_inside_bottom else 'FAIL'}",
            f"  Purple U via clear of vertical corner: {fmt(params.lower_bottom_l2_mm)} mm -> {'PASS' if lower_via_away_from_corner else 'FAIL'}",
            f"  Orange via pad to purple coupling arm gap: {fmt(orange_pad_to_purple_gap)} mm -> {'PASS' if orange_pad_to_purple_gap >= params.min_fab_feature_mm else 'FAIL'}",
            "",
            "Geometry summary",
            f"  Core resonator bounding box: {fmt(core_max_x - core_min_x)} mm x {fmt(core_max_y - core_min_y)} mm",
            f"  Total metal bounding box with feeds: {fmt(metal_max_x - metal_min_x)} mm x {fmt(metal_max_y - metal_min_y)} mm",
            f"  Purple U resonator span L2: {fmt(params.lower_span_l2_mm)} mm",
            f"  Purple U resonator branch width W1: {fmt(params.lower_w1_mm)} mm",
            f"  Purple U resonator coupling width W2: {fmt(params.lower_top_bridge_w_mm)} mm",
            f"  Purple U resonator arm L1: {fmt(params.lower_arm_l1_mm)} mm",
            f"  Purple U bottom arm length: {fmt(params.lower_bottom_l2_mm)} mm",
            f"  Direct 50-ohm feed taper length t1: {fmt(params.feed_gap_t1_mm)} mm",
            f"  Direct 50-ohm feed taper tip width: {fmt(params.feed_tip_w_mm)} mm",
            f"  Direct 50-ohm feed overlap into Purple U: {fmt(params.feed_overlap_mm)} mm",
            f"  Main gap S1: {fmt(params.main_gap_s1_mm)} mm",
            f"  Purple U center split gap S2: {fmt(params.side_gap_s2_mm)} mm",
            f"  Via square pad size: {fmt(params.via_pad_size_mm)} mm",
            f"  Purple U via edge clearance: {fmt(params.via_edge_clearance_mm)} mm",
            f"  Purple U via extra inward compensation d1: {fmt(params.via_offset_d1_mm)} mm",
            f"  Orange folded-line center x: {fmt(center_x)} mm",
            f"  Orange folded-line narrow width W1: {fmt(params.upper_w1_mm)} mm",
            f"  Orange folded-line step width W2: {fmt(params.upper_w2_mm)} mm",
            f"  Orange folded-line span: {fmt(upper_x1 - upper_x0)} mm",
            f"  Orange folded-line top arm length each side: {fmt(top_arm_len)} mm",
            f"  Orange folded-line top center clearance from d2: {fmt(params.fold_offset_d2_mm)} mm each side",
            "",
            "Important assumptions",
            "  L1 signal references L3 ground through L2 keepout.",
            "  Purple metal is modeled as two mirrored via-loaded U-shaped resonators with a center split gap.",
            "  Purple U vias are placed on independent square pads near the inner open ends of the bottom branches.",
            "  Square via pads are lower-edge aligned to the narrow trace edge; the drills are centered inside the pads.",
            "  Orange metal is modeled as a left/right symmetric folded line / folded SIR loading path.",
            "  The orange shorting via is centered on an independent square pad on the folded-line lower segment.",
            "  The 50-ohm feed lines are moved outward and directly connected through narrow taper tips with only local overlap.",
            "  Via diameter is allowed to exceed narrow branch width because each via has an independent square copper pad.",
            "  It is an EM baseline candidate; dimensions must be calibrated by ADS FEM rather than copied from the Rogers 4003C article.",
        ]
    ) + "\n"


def write_outputs(params: FoldedSirParams, out_dir: Path) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rects, ports = build_rects(params)
    base = out_dir / params.name
    dxf_path = base.with_suffix(".dxf")
    dxf_mm_path = base.with_name(base.name + "_mm_coords.dxf")
    dxf_mil_path = base.with_name(base.name + "_ads_mil_coords.dxf")
    svg_path = base.with_suffix(".svg")
    json_path = base.with_name(base.name + "_params.json")
    layout_json_path = base.with_name(base.name + "_layout.json")
    drc_path = base.with_name(base.name + "_drc.txt")

    write_dxf(dxf_path, rects)
    write_dxf(dxf_mm_path, rects)
    write_dxf(dxf_mil_path, rects, coord_scale=39.37007874015748, insunits=0)
    write_svg(svg_path, rects, params, ports)
    metal_rects = [rect for rect in rects if rect.layer == params.metal_layer]
    core_rects = [
        rect
        for rect in metal_rects
        if rect.name.startswith("purple_u_") or rect.name.startswith("orange_folded_line_")
    ]
    min_x, min_y, max_x, max_y = rect_bounds(metal_rects)
    core_min_x, core_min_y, core_max_x, core_max_y = rect_bounds(core_rects)
    minimum_gap = min(params.main_gap_s1_mm, params.side_gap_s2_mm, orange_via_pad_to_purple_gap(params))
    json_path.write_text(
        json.dumps(
            {
                "parameters": {**asdict(params), "tap_from_bottom_mm": ports["P1"][1]},
                "derived": {
                    "metal_width_mm": max_x - min_x,
                    "metal_height_mm": max_y - min_y,
                    "core_width_mm": core_max_x - core_min_x,
                    "core_height_mm": core_max_y - core_min_y,
                    "minimum_width_mm": min(shape_min_feature(rect) for rect in metal_rects),
                    "minimum_gap_mm": minimum_gap,
                },
                "ports": {name: [x, y] for name, (x, y) in ports.items()},
                    "shapes": [asdict(rect) for rect in rects],
                    "rectangles": [asdict(rect) for rect in rects if isinstance(rect, Rect)],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_layout_json(layout_json_path, build_layout(params, rects, ports))
    drc_path.write_text(make_drc(params, rects), encoding="utf-8")

    return {
        "dxf": str(dxf_path),
        "dxf_mm_coords": str(dxf_mm_path),
        "dxf_ads_mil_coords": str(dxf_mil_path),
        "svg": str(svg_path),
        "params": str(json_path),
        "layout_json": str(layout_json_path),
        "drc": str(drc_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate folded SIR BPF layout files.")
    parser.add_argument("--plan", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parents[1] / "ADS" / "folded_sir_bpf_l3_round0")
    parser.add_argument("--name", default=FoldedSirParams.name)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.plan is not None:
        with args.plan.open(newline="", encoding="utf-8-sig") as fp:
            rows = list(csv.DictReader(fp))
        print(f"Generating {len(rows)} folded SIR BPF candidates into {args.out_dir}")
        for row in rows:
            params = row_to_params(row)
            outputs = write_outputs(params, args.out_dir)
            print(f"  {params.name}: {outputs['dxf_mm_coords']}")
        return

    outputs = write_outputs(FoldedSirParams(name=args.name), args.out_dir)
    print("Generated folded SIR BPF layout support files:")
    for kind, path in outputs.items():
        print(f"  {kind}: {path}")


if __name__ == "__main__":
    main()
