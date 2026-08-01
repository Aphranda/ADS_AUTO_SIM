#!/usr/bin/env python3
"""Generate a paper-topology mixed-coupled SIR BPF layout for ADS."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from html import escape
import argparse
import csv
import json
import math
from pathlib import Path
import sys

_SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.exporters.json import write_layout_json
from simads.geometry import Boundary, LayerMap, Layout, Port, Rect as LayoutRect, Via


@dataclass(frozen=True)
class PaperSirParams:
    name: str = "paper_sir_ro4350_r0_base"
    substrate: str = "substrate1"
    er: float = 3.66
    dielectric_height_mm: float = 0.51
    copper_thickness_mm: float = 0.035
    lower_cutoff_ghz: float = 6.0
    upper_cutoff_ghz: float = 8.0
    f0_ghz: float = 6.8
    fbw_pct: float = 22.8
    order: int = 4
    feed_w_mm: float = 1.1252
    feed_len_mm: float = 3.20
    feed_gap_t1_mm: float = 0.28
    sir_span_l2_mm: float = 7.45
    sir_arm_l1_mm: float = 3.80
    sir_z1_w_mm: float = 0.206
    sir_z2_w_mm: float = 0.510
    sir_z3_w_mm: float = 0.267
    sir_center_stub_l3_mm: float = 0.00
    sir_bottom_arm_mm: float = 2.15
    via_diameter_mm: float = 0.30
    via_pad_size_mm: float = 0.42
    via_edge_clearance_mm: float = 0.06
    via_offset_d1_mm: float = 0.12
    upper_z1_w_mm: float = 0.206
    upper_z2_w_mm: float = 0.510
    upper_fold_h_mm: float = 1.35
    upper_margin_x_mm: float = 0.28
    upper_center_gap_d2_mm: float = 1.20
    upper_center_ground_via: int = 1
    main_gap_s_mm: float = 0.24
    side_gap_s2_mm: float = 0.24
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


def fmt(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def parse_float(row: dict[str, str], key: str, default: float) -> float:
    value = row.get(key, "").strip()
    return default if not value else float(value)


def parse_int(row: dict[str, str], key: str, default: int) -> int:
    value = row.get(key, "").strip()
    return default if not value else int(value)


def row_to_params(row: dict[str, str]) -> PaperSirParams:
    defaults = PaperSirParams()
    return PaperSirParams(
        name=row["name"].strip(),
        substrate=row.get("substrate", defaults.substrate).strip() or defaults.substrate,
        er=parse_float(row, "er", defaults.er),
        dielectric_height_mm=parse_float(row, "h_mm", defaults.dielectric_height_mm),
        copper_thickness_mm=parse_float(row, "copper_mm", defaults.copper_thickness_mm),
        lower_cutoff_ghz=parse_float(row, "lower_cutoff_ghz", defaults.lower_cutoff_ghz),
        upper_cutoff_ghz=parse_float(row, "upper_cutoff_ghz", defaults.upper_cutoff_ghz),
        f0_ghz=parse_float(row, "f0_ghz", defaults.f0_ghz),
        fbw_pct=parse_float(row, "fbw_pct", defaults.fbw_pct),
        order=parse_int(row, "order", defaults.order),
        feed_w_mm=parse_float(row, "feed_w_mm", defaults.feed_w_mm),
        feed_len_mm=parse_float(row, "feed_len_mm", defaults.feed_len_mm),
        feed_gap_t1_mm=parse_float(row, "feed_gap_t1_mm", defaults.feed_gap_t1_mm),
        sir_span_l2_mm=parse_float(row, "sir_span_l2_mm", defaults.sir_span_l2_mm),
        sir_arm_l1_mm=parse_float(row, "sir_arm_l1_mm", defaults.sir_arm_l1_mm),
        sir_z1_w_mm=parse_float(row, "sir_z1_w_mm", defaults.sir_z1_w_mm),
        sir_z2_w_mm=parse_float(row, "sir_z2_w_mm", defaults.sir_z2_w_mm),
        sir_z3_w_mm=parse_float(row, "sir_z3_w_mm", defaults.sir_z3_w_mm),
        sir_center_stub_l3_mm=parse_float(row, "sir_center_stub_l3_mm", defaults.sir_center_stub_l3_mm),
        sir_bottom_arm_mm=parse_float(row, "sir_bottom_arm_mm", defaults.sir_bottom_arm_mm),
        via_diameter_mm=parse_float(row, "via_diameter_mm", defaults.via_diameter_mm),
        via_pad_size_mm=parse_float(row, "via_pad_size_mm", defaults.via_pad_size_mm),
        via_edge_clearance_mm=parse_float(row, "via_edge_clearance_mm", defaults.via_edge_clearance_mm),
        via_offset_d1_mm=parse_float(row, "via_offset_d1_mm", defaults.via_offset_d1_mm),
        upper_z1_w_mm=parse_float(row, "upper_z1_w_mm", defaults.upper_z1_w_mm),
        upper_z2_w_mm=parse_float(row, "upper_z2_w_mm", defaults.upper_z2_w_mm),
        upper_fold_h_mm=parse_float(row, "upper_fold_h_mm", defaults.upper_fold_h_mm),
        upper_margin_x_mm=parse_float(row, "upper_margin_x_mm", defaults.upper_margin_x_mm),
        upper_center_gap_d2_mm=parse_float(row, "upper_center_gap_d2_mm", defaults.upper_center_gap_d2_mm),
        upper_center_ground_via=parse_int(row, "upper_center_ground_via", defaults.upper_center_ground_via),
        main_gap_s_mm=parse_float(row, "main_gap_s_mm", defaults.main_gap_s_mm),
        side_gap_s2_mm=parse_float(row, "side_gap_s2_mm", defaults.side_gap_s2_mm),
        boundary_margin_mm=parse_float(row, "boundary_margin_mm", defaults.boundary_margin_mm),
        min_fab_feature_mm=parse_float(row, "min_fab_feature_mm", defaults.min_fab_feature_mm),
        metal_layer=row.get("metal_layer", defaults.metal_layer).strip() or defaults.metal_layer,
        via_layer=row.get("via_layer", defaults.via_layer).strip() or defaults.via_layer,
    )


def rect_points(rect: Rect) -> list[tuple[float, float]]:
    return [(rect.x, rect.y), (rect.x + rect.w, rect.y), (rect.x + rect.w, rect.y + rect.h), (rect.x, rect.y + rect.h)]


def rect_bounds(rects: list[Rect]) -> tuple[float, float, float, float]:
    points = [point for rect in rects for point in rect_points(rect)]
    return (
        min(point[0] for point in points),
        min(point[1] for point in points),
        max(point[0] for point in points),
        max(point[1] for point in points),
    )


def add_boundary(rects: list[Rect], params: PaperSirParams) -> None:
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


def build_rects(params: PaperSirParams) -> tuple[list[Rect], dict[str, tuple[float, float]]]:
    if params.order != 4:
        raise ValueError("The paper topology baseline is parameterized as a 4th-order mixed-coupled SIR.")
    if params.sir_span_l2_mm <= 2.0 * params.sir_z1_w_mm:
        raise ValueError("sir_span_l2_mm is too small.")

    rects: list[Rect] = []
    metal = params.metal_layer
    via = params.via_layer
    span = params.sir_span_l2_mm
    center_x = span / 2.0

    upper_span = span - 2.0 * params.upper_margin_x_mm
    upper_x0 = params.upper_margin_x_mm
    upper_x1 = span - params.upper_margin_x_mm
    top_arm_len = (upper_span - params.upper_center_gap_d2_mm) / 2.0
    if top_arm_len <= params.upper_z2_w_mm:
        raise ValueError("upper_center_gap_d2_mm leaves too little folded top-arm length.")

    sir_top_y = 0.0
    sir_bottom_y = -(params.sir_arm_l1_mm - params.sir_z1_w_mm)
    upper_bottom_y = params.sir_z2_w_mm + params.main_gap_s_mm
    upper_top_y = upper_bottom_y + params.upper_fold_h_mm - params.upper_z1_w_mm
    rects.extend(
        [
            Rect("paper_upper_sir_left_top_arm", metal, upper_x0, upper_top_y, top_arm_len, params.upper_z1_w_mm),
            Rect("paper_upper_sir_right_top_arm", metal, upper_x1 - top_arm_len, upper_top_y, top_arm_len, params.upper_z1_w_mm),
            Rect("paper_upper_sir_left_z2_step", metal, upper_x0, upper_bottom_y, params.upper_z2_w_mm, params.upper_fold_h_mm),
            Rect("paper_upper_sir_right_z2_step", metal, upper_x1 - params.upper_z2_w_mm, upper_bottom_y, params.upper_z2_w_mm, params.upper_fold_h_mm),
            Rect("paper_upper_sir_lower_coupling_line", metal, upper_x0, upper_bottom_y, upper_span, params.upper_z1_w_mm),
        ]
    )

    if params.upper_center_ground_via:
        if params.upper_center_gap_d2_mm < params.via_pad_size_mm:
            raise ValueError("upper_center_gap_d2_mm is too small for the upper center via pad.")
        center_pad_y = upper_bottom_y + params.upper_z1_w_mm / 2.0 - params.via_pad_size_mm / 2.0
        rects.extend(
            [
                Rect(
                    "paper_upper_sir_center_via_pad",
                    metal,
                    center_x - params.via_pad_size_mm / 2.0,
                    center_pad_y,
                    params.via_pad_size_mm,
                    params.via_pad_size_mm,
                ),
                Rect(
                    "ground_via_upper_center",
                    via,
                    center_x - params.via_diameter_mm / 2.0,
                    upper_bottom_y + params.upper_z1_w_mm / 2.0 - params.via_diameter_mm / 2.0,
                    params.via_diameter_mm,
                    params.via_diameter_mm,
                ),
            ]
        )

    top_gap = params.side_gap_s2_mm
    if top_gap < params.min_fab_feature_mm:
        raise ValueError("side_gap_s2_mm is below the fabrication minimum.")
    left_top_w = center_x - top_gap / 2.0
    right_top_x = center_x + top_gap / 2.0
    right_top_w = span - right_top_x
    rects.extend(
        [
            Rect("paper_sir_top_z2_line_left", metal, 0.0, sir_top_y, left_top_w, params.sir_z2_w_mm),
            Rect("paper_sir_top_z2_line_right", metal, right_top_x, sir_top_y, right_top_w, params.sir_z2_w_mm),
            Rect("paper_sir_left_z1_arm", metal, 0.0, sir_bottom_y, params.sir_z1_w_mm, params.sir_arm_l1_mm),
            Rect("paper_sir_right_z1_arm", metal, span - params.sir_z1_w_mm, sir_bottom_y, params.sir_z1_w_mm, params.sir_arm_l1_mm),
            Rect("paper_sir_left_bottom_loading", metal, 0.0, sir_bottom_y, params.sir_bottom_arm_mm, params.sir_z1_w_mm),
            Rect("paper_sir_right_bottom_loading", metal, span - params.sir_bottom_arm_mm, sir_bottom_y, params.sir_bottom_arm_mm, params.sir_z1_w_mm),
        ]
    )

    if params.sir_center_stub_l3_mm > 0.0:
        rects.append(
            Rect(
                "paper_sir_center_z3_stub",
                metal,
                center_x - params.sir_z3_w_mm / 2.0,
                sir_top_y - params.sir_center_stub_l3_mm,
                params.sir_z3_w_mm,
                params.sir_center_stub_l3_mm,
            )
        )

    via_r = params.via_diameter_mm / 2.0
    via_pad = params.via_pad_size_mm
    via_pad_y = sir_bottom_y + params.sir_z1_w_mm - via_pad
    via_cy = via_pad_y + via_pad / 2.0
    via_comp = via_r + params.via_edge_clearance_mm + params.via_offset_d1_mm
    left_via_cx = params.sir_bottom_arm_mm - via_comp
    right_via_cx = span - params.sir_bottom_arm_mm + via_comp
    rects.extend(
        [
            Rect("paper_sir_left_via_pad", metal, left_via_cx - via_pad / 2.0, via_pad_y, via_pad, via_pad),
            Rect("paper_sir_right_via_pad", metal, right_via_cx - via_pad / 2.0, via_pad_y, via_pad, via_pad),
            Rect("ground_via_left", via, left_via_cx - via_r, via_cy - via_r, params.via_diameter_mm, params.via_diameter_mm),
            Rect("ground_via_right", via, right_via_cx - via_r, via_cy - via_r, params.via_diameter_mm, params.via_diameter_mm),
        ]
    )

    feed_center_y = via_cy
    feed_y = feed_center_y - params.feed_w_mm / 2.0
    left_feed_x = -params.feed_gap_t1_mm - params.feed_len_mm
    right_feed_x = span + params.feed_gap_t1_mm
    rects.extend(
        [
            Rect("input_feed_50ohm_gap_coupled", metal, left_feed_x, feed_y, params.feed_len_mm, params.feed_w_mm),
            Rect("output_feed_50ohm_gap_coupled", metal, right_feed_x, feed_y, params.feed_len_mm, params.feed_w_mm),
        ]
    )

    add_boundary(rects, params)
    ports = {
        "P1": (left_feed_x, feed_center_y),
        "P2": (right_feed_x + params.feed_len_mm, feed_center_y),
    }
    return rects, ports


def build_layout(
    params: PaperSirParams,
    rects: list[Rect] | None = None,
    ports: dict[str, tuple[float, float]] | None = None,
) -> Layout:
    if rects is None or ports is None:
        rects, ports = build_rects(params)

    shapes: list[LayoutRect | Via | Boundary] = []
    for rect in rects:
        if rect.layer == "EM_BOUNDARY":
            shapes.append(Boundary(name=rect.name, x=rect.x, y=rect.y, w=rect.w, h=rect.h, layer=rect.layer))
            continue
        if rect.name.startswith("ground_via_"):
            shapes.append(
                Via(
                    name=rect.name,
                    layer=rect.layer,
                    x=rect.x + rect.w / 2.0,
                    y=rect.y + rect.h / 2.0,
                    diameter=rect.w,
                    metadata={"source": "generate_paper_mixed_sir_bpf_layout"},
                )
            )
            continue
        shapes.append(LayoutRect(name=rect.name, layer=rect.layer, x=rect.x, y=rect.y, w=rect.w, h=rect.h))

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
            "generator": "tools/generate_paper_mixed_sir_bpf_layout.py",
            "layer_map_version": "profile-default-v1",
            "topology": "paper_mixed_coupled_sir_bpf",
            "order": params.order,
            "substrate": params.substrate,
            "er": params.er,
            "dielectric_height_mm": params.dielectric_height_mm,
            "copper_thickness_mm": params.copper_thickness_mm,
        },
    )


def write_dxf(path: Path, rects: list[Rect], coord_scale: float = 1.0, insunits: int = 4) -> None:
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
        x0, y0 = rect.x * coord_scale, rect.y * coord_scale
        x1, y1 = (rect.x + rect.w) * coord_scale, (rect.y + rect.h) * coord_scale
        if rect.name.startswith("ground_via_"):
            cx = (rect.x + rect.w / 2.0) * coord_scale
            cy = (rect.y + rect.h / 2.0) * coord_scale
            radius = rect.w / 2.0 * coord_scale
            lines.extend(["0", "CIRCLE", "8", rect.layer, "10", fmt(cx), "20", fmt(cy), "30", "0", "40", fmt(radius)])
        elif rect.layer != "EM_BOUNDARY":
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
        else:
            points = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
            for (xa, ya), (xb, yb) in zip(points, points[1:], strict=False):
                lines.extend(["0", "LINE", "8", rect.layer, "10", fmt(xa), "20", fmt(ya), "30", "0", "11", fmt(xb), "21", fmt(yb), "31", "0"])
    lines.extend(["0", "ENDSEC", "0", "EOF"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_svg(path: Path, rects: list[Rect], params: PaperSirParams, ports: dict[str, tuple[float, float]]) -> None:
    min_x, min_y, max_x, max_y = rect_bounds(rects)
    width = max_x - min_x
    height = max_y - min_y
    view_min_y = -max_y
    scale = 48
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(width * scale)}" height="{fmt(height * scale)}" viewBox="{fmt(min_x)} {fmt(view_min_y)} {fmt(width)} {fmt(height)}">',
        f'<rect x="{fmt(min_x)}" y="{fmt(view_min_y)}" width="{fmt(width)}" height="{fmt(height)}" fill="#fff"/>',
    ]
    for rect in rects:
        y = -(rect.y + rect.h)
        if rect.layer == "EM_BOUNDARY":
            parts.append(f'<rect x="{fmt(rect.x)}" y="{fmt(y)}" width="{fmt(rect.w)}" height="{fmt(rect.h)}" fill="none" stroke="#888" stroke-dasharray="0.18 0.12" stroke-width="0.035"/>')
        elif rect.name.startswith("ground_via_"):
            parts.append(f'<circle cx="{fmt(rect.x + rect.w / 2.0)}" cy="{fmt(-(rect.y + rect.h / 2.0))}" r="{fmt(rect.w / 2.0)}" fill="#111"/>')
        elif rect.name.startswith("paper_upper_"):
            parts.append(f'<rect x="{fmt(rect.x)}" y="{fmt(y)}" width="{fmt(rect.w)}" height="{fmt(rect.h)}" fill="#e67817" stroke="#603300" stroke-width="0.025"/>')
        elif rect.name.startswith("paper_sir_"):
            parts.append(f'<rect x="{fmt(rect.x)}" y="{fmt(y)}" width="{fmt(rect.w)}" height="{fmt(rect.h)}" fill="#b64a87" stroke="#4a1836" stroke-width="0.025"/>')
        else:
            parts.append(f'<rect x="{fmt(rect.x)}" y="{fmt(y)}" width="{fmt(rect.w)}" height="{fmt(rect.h)}" fill="#9aa0d4" stroke="#36396f" stroke-width="0.025"/>')
    for name, (x, y) in ports.items():
        parts.append(f'<circle cx="{fmt(x)}" cy="{fmt(-y)}" r="0.13" fill="#1769ff"/>')
        parts.append(f'<text x="{fmt(x + 0.15)}" y="{fmt(-y - 0.15)}" font-size="0.32">{escape(name)}</text>')
    parts.append(f'<text x="{fmt(min_x + 0.2)}" y="{fmt(view_min_y + 0.45)}" font-size="0.35" fill="#333">{escape(params.name)} paper mixed-coupled SIR BPF</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def shape_min_feature(rect: Rect) -> float:
    return min(rect.w, rect.h)


def make_drc(params: PaperSirParams, rects: list[Rect]) -> str:
    metal_rects = [rect for rect in rects if rect.layer == params.metal_layer]
    core_rects = [rect for rect in metal_rects if rect.name.startswith(("paper_sir_", "paper_upper_"))]
    min_width = min(shape_min_feature(rect) for rect in metal_rects)
    min_gap = min(params.feed_gap_t1_mm, params.main_gap_s_mm, params.side_gap_s2_mm)
    via_pad_covers_drill = params.via_pad_size_mm >= params.via_diameter_mm + 2.0 * params.via_edge_clearance_mm
    metal_min_x, metal_min_y, metal_max_x, metal_max_y = rect_bounds(metal_rects)
    core_min_x, core_min_y, core_max_x, core_max_y = rect_bounds(core_rects)
    return "\n".join(
        [
            f"Design: {params.name}",
            f"Substrate: {params.substrate}, er={fmt(params.er)}, h={fmt(params.dielectric_height_mm)} mm, copper={fmt(params.copper_thickness_mm)} mm",
            f"Band target: {fmt(params.lower_cutoff_ghz)}-{fmt(params.upper_cutoff_ghz)} GHz, f0={fmt(params.f0_ghz)} GHz, fbw={fmt(params.fbw_pct)}%, order={params.order}",
            "",
            "Fabrication check",
            f"  Rule minimum: {fmt(params.min_fab_feature_mm)} mm (6 mil)",
            f"  Minimum metal width: {fmt(min_width)} mm -> {'PASS' if min_width >= params.min_fab_feature_mm else 'FAIL'}",
            f"  Minimum coupling/feed gap: {fmt(min_gap)} mm -> {'PASS' if min_gap >= params.min_fab_feature_mm else 'FAIL'}",
            f"  Via drawing diameter: {fmt(params.via_diameter_mm)} mm -> {'PASS' if params.via_diameter_mm >= params.min_fab_feature_mm else 'FAIL'}",
            f"  Via pad size: {fmt(params.via_pad_size_mm)} mm -> {'PASS' if via_pad_covers_drill else 'FAIL'}",
            "",
            "Geometry summary",
            f"  Core resonator bounding box: {fmt(core_max_x - core_min_x)} mm x {fmt(core_max_y - core_min_y)} mm",
            f"  Total metal bounding box with feeds: {fmt(metal_max_x - metal_min_x)} mm x {fmt(metal_max_y - metal_min_y)} mm",
            f"  Gap-coupled feed t1: {fmt(params.feed_gap_t1_mm)} mm",
            f"  Dual-mode SIR span L2: {fmt(params.sir_span_l2_mm)} mm",
            f"  Dual-mode SIR arm L1: {fmt(params.sir_arm_l1_mm)} mm",
            f"  SIR widths Z1/Z2/Z3 approx: {fmt(params.sir_z1_w_mm)} / {fmt(params.sir_z2_w_mm)} / {fmt(params.sir_z3_w_mm)} mm",
            f"  Optional center Z3 stub length: {fmt(params.sir_center_stub_l3_mm)} mm",
            f"  Main upper/lower coupling gap S: {fmt(params.main_gap_s_mm)} mm",
            f"  Upper folded SIR top center gap d2: {fmt(params.upper_center_gap_d2_mm)} mm",
            f"  Lower via inward compensation d1: {fmt(params.via_offset_d1_mm)} mm",
            "",
            "Important assumptions",
            "  This branch follows the paper topology more closely than the earlier simplified folded SIR generator.",
            "  Feed lines are gap-coupled to the lower resonator; there is no direct taper overlap.",
            "  The lower purple dual-mode SIR top line is continuous; S2 is not implemented as a center cut in the purple line.",
            "  The upper orange folded SIR has no default shorting via; it is treated as a coupled resonant line.",
            "  Z1/Z2/Z3 widths are first-order Hammerstad-style approximations and must be calibrated in ADS LineCalc/FEM.",
        ]
    ) + "\n"


def write_outputs(params: PaperSirParams, out_dir: Path) -> dict[str, str]:
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
    core_rects = [rect for rect in metal_rects if rect.name.startswith(("paper_sir_", "paper_upper_"))]
    min_x, min_y, max_x, max_y = rect_bounds(metal_rects)
    core_min_x, core_min_y, core_max_x, core_max_y = rect_bounds(core_rects)
    minimum_gap = min(params.feed_gap_t1_mm, params.main_gap_s_mm, params.side_gap_s2_mm)
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
                "rectangles": [asdict(rect) for rect in rects],
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
    parser = argparse.ArgumentParser(description="Generate paper-topology mixed-coupled SIR BPF layout files.")
    parser.add_argument("--plan", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parents[1] / "ADS" / "paper_mixed_sir_bpf_ro4350_round0")
    parser.add_argument("--name", default=PaperSirParams.name)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.plan is not None:
        with args.plan.open(newline="", encoding="utf-8-sig") as fp:
            rows = list(csv.DictReader(fp))
        print(f"Generating {len(rows)} paper mixed-coupled SIR BPF candidates into {args.out_dir}")
        for row in rows:
            params = row_to_params(row)
            outputs = write_outputs(params, args.out_dir)
            print(f"  {params.name}: {outputs['dxf_mm_coords']}")
        return

    outputs = write_outputs(PaperSirParams(name=args.name), args.out_dir)
    print("Generated paper mixed-coupled SIR BPF layout support files:")
    for kind, path in outputs.items():
        print(f"  {kind}: {path}")


if __name__ == "__main__":
    main()
