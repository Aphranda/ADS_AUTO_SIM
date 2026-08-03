#!/usr/bin/env python3
"""Generate a first-pass ADS-importable layout for the 9th order filter.

The geometry is based on the Marki interdigital Chebyshev dimensions captured
for RO4350B 0.020 inch substrate. Units are millimeters.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
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

from simads.config import StackupConfig, load_stackup_config, name_with_stackup_token, stackup_name_token
from simads.exporters.json import write_layout_json
from simads.geometry import Boundary, LayerMap, Layout, Polygon, Port, Rect as LayoutRect, Via


@dataclass(frozen=True)
class FilterParams:
    name: str = "interdigital_9o_ro4350b_508um"
    order: int = 9
    substrate: str = "RO4350B"
    er: float = 3.48
    dielectric_height_mm: float = 0.508
    copper_thickness_mm: float = 0.035
    stackup_id: str | None = None
    stackup_token: str | None = None
    stackup_config: str | None = None
    signal_layer: str | None = None
    reference_ground_layer: str | None = None
    via_top_layer: str | None = None
    via_bottom_layer: str | None = None
    ground_layers: tuple[str, ...] = ()
    layout_ground_layers: tuple[str, ...] = ()
    signal_to_reference_height_mm: float | None = None
    total_thickness_mm: float | None = None
    lower_cutoff_ghz: float = 6.0
    upper_cutoff_ghz: float = 8.0
    passband_ripple_db: float = 0.10
    z0_ohm: float = 50.0
    w0_mm: float = 1.113
    resonator_w_mm: float = 1.113
    resonator_l_mm: float = 6.337
    tap_from_bottom_mm: float = 2.143
    end_gap_mm: float = 0.527
    gaps_mm: tuple[float, ...] = (
        0.2891,
        0.4442,
        0.4774,
        0.4871,
        0.4871,
        0.4774,
        0.4442,
        0.2891,
    )
    feed_len_mm: float = 3.0
    feed_taper_len_mm: float = 0.0
    feed_tip_w_mm: float = 0.18
    feed_overlap_mm: float = 0.06
    boundary_margin_mm: float = 1.5
    min_fab_feature_mm: float = 0.1524
    metal_layer: str = "cond"
    via_layer: str = "pcvia1"
    ground_layer: str = "GND"
    layer_map_version: str = "profile-default-v1"
    include_ground_plane: bool = False
    ground_boundary_mode: str = "port-edges"
    ground_plane_name: str = "gnd_plane"
    via_diameter_mm: float = 0.50
    via_pad_mm: float = 0.50
    via_half_outside: bool = False
    via_pad_outside: bool = False


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


def stackup_layer_thickness(stackup: StackupConfig, layer_name: str) -> float:
    for layer in stackup.layers_bottom_to_top:
        if layer.name == layer_name:
            return layer.thickness_mm
    raise ValueError(f"stackup layer not found: {layer_name}")


def stackup_ads_drill_layer(stackup: StackupConfig, default: str) -> str:
    raw_ads = (stackup.raw or {}).get("ads", {})
    if isinstance(raw_ads, dict) and raw_ads.get("drill_layer"):
        return str(raw_ads["drill_layer"])
    return default


def params_with_stackup_config(
    params: FilterParams,
    stackup: StackupConfig,
    *,
    config_path: Path | None = None,
    rename: bool = True,
) -> FilterParams:
    primary = stackup.primary_dielectric
    stackup_token = stackup_name_token(stackup)
    return replace(
        params,
        name=name_with_stackup_token(params.name, stackup) if rename else params.name,
        substrate=stackup.stackup_id,
        er=float(primary.er if primary and primary.er is not None else params.er),
        dielectric_height_mm=stackup.signal_to_reference_height_mm,
        copper_thickness_mm=stackup_layer_thickness(stackup, stackup.geometry.signal_layer),
        stackup_id=stackup.stackup_id,
        stackup_token=stackup_token,
        stackup_config=str(config_path) if config_path is not None else None,
        signal_layer=stackup.geometry.signal_layer,
        reference_ground_layer=stackup.geometry.reference_ground_layer,
        ground_layers=stackup.geometry.ground_layers,
        metal_layer=stackup.geometry.signal_layer,
        via_layer=stackup_ads_drill_layer(stackup, params.via_layer),
        ground_layer=stackup.geometry.reference_ground_layer,
        layer_map_version="simads-em-template-v1",
        via_top_layer=stackup.geometry.via_top_layer,
        via_bottom_layer=stackup.geometry.via_bottom_layer,
        ground_plane_name=stackup.geometry.ground_plane_name,
        signal_to_reference_height_mm=stackup.signal_to_reference_height_mm,
        total_thickness_mm=stackup.total_thickness_mm,
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


def shape_min_feature(shape: Rect | Quad) -> float:
    if isinstance(shape, Rect):
        return min(shape.w, shape.h)
    points = shape.points
    edges = [
        math.hypot(xb - xa, yb - ya)
        for (xa, ya), (xb, yb) in zip(points, points[1:] + points[:1], strict=False)
    ]
    return min(edges)


def field_width(params: FilterParams) -> float:
    return params.order * params.resonator_w_mm + sum(params.gaps_mm)


def overall_height(params: FilterParams) -> float:
    return params.resonator_l_mm + params.end_gap_mm


def feed_extension_len(params: FilterParams) -> float:
    return params.feed_len_mm + max(0.0, params.feed_taper_len_mm) - (
        max(0.0, params.feed_overlap_mm) if params.feed_taper_len_mm > 0.0 else 0.0
    )


def port_locations(params: FilterParams) -> tuple[tuple[float, float], tuple[float, float]]:
    feed_total_len = feed_extension_len(params)
    return (-feed_total_len, params.tap_from_bottom_mm), (field_width(params) + feed_total_len, params.tap_from_bottom_mm)


def boundary_rect(params: FilterParams) -> Rect:
    p1, p2 = port_locations(params)
    return Rect(
        name="em_boundary",
        layer="EM_BOUNDARY",
        x=p1[0] - params.boundary_margin_mm,
        y=-params.boundary_margin_mm,
        w=p2[0] - p1[0] + 2.0 * params.boundary_margin_mm,
        h=overall_height(params) + 2.0 * params.boundary_margin_mm,
    )


def ground_plane_rect(params: FilterParams) -> Rect:
    return ground_plane_rect_for_layer(params, params.ground_layer, params.ground_plane_name)


def effective_ground_layers(params: FilterParams) -> tuple[str, ...]:
    return params.ground_layers or (params.ground_layer,)


def layout_ground_layers(params: FilterParams) -> tuple[str, ...]:
    return params.layout_ground_layers or (params.ground_layer,)


def ground_plane_name_for_layer(params: FilterParams, layer: str) -> str:
    if layer == params.ground_layer:
        return params.ground_plane_name
    return f"{params.ground_plane_name}_{layer}"


def ground_plane_rect_for_layer(params: FilterParams, layer: str, name: str | None = None) -> Rect:
    boundary = boundary_rect(params)
    if params.ground_boundary_mode == "em-boundary":
        x = boundary.x
        w = boundary.w
    elif params.ground_boundary_mode == "port-edges":
        p1, p2 = port_locations(params)
        x = min(p1[0], p2[0])
        w = abs(p2[0] - p1[0])
    else:
        raise ValueError("ground_boundary_mode must be 'port-edges' or 'em-boundary'")
    return Rect(
        name=name or ground_plane_name_for_layer(params, layer),
        layer=layer,
        x=x,
        y=boundary.y,
        w=w,
        h=boundary.h,
    )


def ground_plane_rects(params: FilterParams) -> list[Rect]:
    return [
        ground_plane_rect_for_layer(params, layer, ground_plane_name_for_layer(params, layer))
        for layer in layout_ground_layers(params)
    ]


def build_rects(params: FilterParams) -> list[Rect | Quad]:
    if len(params.gaps_mm) != params.order - 1:
        raise ValueError("gap count must be order - 1")

    overall_h = overall_height(params)
    x_positions: list[float] = []
    x = 0.0
    for idx in range(params.order):
        x_positions.append(x)
        if idx < len(params.gaps_mm):
            x += params.resonator_w_mm + params.gaps_mm[idx]

    field_w = field_width(params)
    rects: list[Rect | Quad] = []
    if params.include_ground_plane:
        rects.extend(ground_plane_rects(params))

    for idx, x0 in enumerate(x_positions, start=1):
        anchored_bottom = idx % 2 == 1
        y0 = 0.0 if anchored_bottom else params.end_gap_mm
        rects.append(
            Rect(
                name=f"resonator_{idx}",
                layer=params.metal_layer,
                x=x0,
                y=y0,
                w=params.resonator_w_mm,
                h=params.resonator_l_mm,
            )
        )
        via_cx = x0 + params.resonator_w_mm / 2.0
        pad_size = max(params.via_pad_mm, params.via_diameter_mm)
        if params.via_pad_outside:
            via_cy = y0 - pad_size / 2.0 if anchored_bottom else y0 + params.resonator_l_mm + pad_size / 2.0
        elif params.via_half_outside:
            via_cy = y0 if anchored_bottom else y0 + params.resonator_l_mm
        else:
            via_cy = (
                y0 + params.via_diameter_mm / 2.0
                if anchored_bottom
                else y0 + params.resonator_l_mm - params.via_diameter_mm / 2.0
            )
        if params.via_pad_mm > 0.0:
            rects.append(
                Rect(
                    name=f"via_pad_{idx}",
                    layer=params.metal_layer,
                    x=via_cx - pad_size / 2.0,
                    y=via_cy - pad_size / 2.0,
                    w=pad_size,
                    h=pad_size,
                )
            )
        via_x = via_cx - params.via_diameter_mm / 2.0
        via_y = via_cy - params.via_diameter_mm / 2.0
        rects.append(
            Rect(
                name=f"ground_via_{idx}",
                layer=params.via_layer,
                x=via_x,
                y=via_y,
                w=params.via_diameter_mm,
                h=params.via_diameter_mm,
            )
        )

    feed_y = params.tap_from_bottom_mm - params.w0_mm / 2.0
    taper_len = max(0.0, params.feed_taper_len_mm)
    taper_tip_w = min(max(params.feed_tip_w_mm, params.min_fab_feature_mm), params.w0_mm)
    overlap = max(0.0, params.feed_overlap_mm) if taper_len > 0.0 else 0.0
    left_tip_x = overlap
    left_feed_x1 = left_tip_x - taper_len
    input_x0 = left_feed_x1 - params.feed_len_mm
    right_tip_x = field_w - overlap
    right_feed_x0 = right_tip_x + taper_len
    feed_tip_y0 = params.tap_from_bottom_mm - taper_tip_w / 2.0
    feed_tip_y1 = params.tap_from_bottom_mm + taper_tip_w / 2.0

    rects.append(
        Rect(
            name="input_feed",
            layer=params.metal_layer,
            x=input_x0,
            y=feed_y,
            w=params.feed_len_mm,
            h=params.w0_mm,
        )
    )
    if taper_len > 0.0:
        rects.extend(
            [
                Quad(
                    name="input_feed_taper",
                    layer=params.metal_layer,
                    points=[
                        (left_feed_x1, feed_y),
                        (left_feed_x1, feed_y + params.w0_mm),
                        (left_tip_x, feed_tip_y1),
                        (left_tip_x, feed_tip_y0),
                    ],
                ),
                Quad(
                    name="output_feed_taper",
                    layer=params.metal_layer,
                    points=[
                        (right_tip_x, feed_tip_y0),
                        (right_tip_x, feed_tip_y1),
                        (right_feed_x0, feed_y + params.w0_mm),
                        (right_feed_x0, feed_y),
                    ],
                ),
            ]
        )
    rects.extend(
        [
            Rect(
                name="output_feed",
                layer=params.metal_layer,
                x=right_feed_x0,
                y=feed_y,
                w=params.feed_len_mm,
                h=params.w0_mm,
            ),
            boundary_rect(params),
        ]
    )
    return rects


def build_layout(params: FilterParams, rects: list[Rect | Quad] | None = None) -> Layout:
    rects = rects or build_rects(params)
    p1, p2 = port_locations(params)
    ground_layer_names = set(layout_ground_layers(params))

    shapes: list[LayoutRect | Polygon | Via | Boundary] = []
    for shape in rects:
        if isinstance(shape, Quad):
            shapes.append(Polygon(name=shape.name, layer=shape.layer, points=shape.points))
            continue
        if shape.layer == "EM_BOUNDARY":
            shapes.append(Boundary(name=shape.name, x=shape.x, y=shape.y, w=shape.w, h=shape.h, layer=shape.layer))
            continue
        if shape.name.startswith("via_pad_"):
            continue
        if shape.name.startswith("ground_via_"):
            shapes.append(
                Via(
                    name=shape.name,
                    layer=shape.layer,
                    x=shape.x + shape.w / 2.0,
                    y=shape.y + shape.h / 2.0,
                    diameter=shape.w,
                    pad_diameter=max(params.via_pad_mm, params.via_diameter_mm) if params.via_pad_mm > 0.0 else None,
                    pad_layer=params.metal_layer if params.via_pad_mm > 0.0 else None,
                    metadata={"source": "generate_interdigital_filter_layout"},
                )
            )
            continue
        metadata = {}
        if params.include_ground_plane and shape.layer in ground_layer_names:
            metadata = {
                "role": "reference_ground",
                "ground_boundary_mode": params.ground_boundary_mode,
                "source": "generate_interdigital_filter_layout",
            }
        shapes.append(
            LayoutRect(name=shape.name, layer=shape.layer, x=shape.x, y=shape.y, w=shape.w, h=shape.h, metadata=metadata)
        )

    ports = [
        Port(
            name="P1",
            number=1,
            x=p1[0],
            y=p1[1],
            width=params.w0_mm,
            layer=params.metal_layer,
            reference=params.ground_plane_name if params.include_ground_plane else "ground",
        ),
        Port(
            name="P2",
            number=2,
            x=p2[0],
            y=p2[1],
            width=params.w0_mm,
            layer=params.metal_layer,
            reference=params.ground_plane_name if params.include_ground_plane else "ground",
        ),
    ]
    metadata = {
        "generator": "tools/generate_interdigital_filter_layout.py",
        "layer_map_version": params.layer_map_version,
        "topology": "interdigital_bpf",
        "order": params.order,
        "substrate": params.substrate,
        "er": params.er,
        "dielectric_height_mm": params.dielectric_height_mm,
        "copper_thickness_mm": params.copper_thickness_mm,
        "include_ground_plane": params.include_ground_plane,
        "ground_layer": params.ground_layer,
        "ground_layers": list(effective_ground_layers(params)),
        "layout_ground_layers": list(layout_ground_layers(params)),
        "ground_boundary_mode": params.ground_boundary_mode,
        "ground_plane_name": params.ground_plane_name,
    }
    if params.stackup_id:
        metadata.update(
            {
                "stackup_id": params.stackup_id,
                "stackup_token": params.stackup_token,
                "stackup_config": params.stackup_config,
                "signal_layer": params.signal_layer,
                "reference_ground_layer": params.reference_ground_layer,
                "ground_layers": list(effective_ground_layers(params)),
                "layout_ground_layers": list(layout_ground_layers(params)),
                "via_top_layer": params.via_top_layer,
                "via_bottom_layer": params.via_bottom_layer,
                "signal_to_reference_height_mm": params.signal_to_reference_height_mm,
                "total_thickness_mm": params.total_thickness_mm,
            }
        )

    return Layout(
        layout_id=params.name,
        units="mm",
        layers=list(
            {
                params.metal_layer: LayerMap(name=params.metal_layer, dxf_layer=params.metal_layer),
                params.via_layer: LayerMap(name=params.via_layer, dxf_layer=params.via_layer),
                **{layer: LayerMap(name=layer, dxf_layer=layer) for layer in effective_ground_layers(params)},
                "EM_BOUNDARY": LayerMap(name="EM_BOUNDARY", dxf_layer="EM_BOUNDARY"),
            }.values()
        ),
        shapes=shapes,
        ports=ports,
        metadata=metadata,
    )


def rect_bounds(rects: list[Rect | Quad]) -> tuple[float, float, float, float]:
    points = [point for rect in rects for point in shape_points(rect)]
    min_x = min(point[0] for point in points)
    min_y = min(point[1] for point in points)
    max_x = max(point[0] for point in points)
    max_y = max(point[1] for point in points)
    return min_x, min_y, max_x, max_y


def write_dxf(path: Path, rects: list[Rect | Quad], coord_scale: float = 1.0, insunits: int = 4) -> None:
    """Write DXF rectangles.

    coord_scale converts internal millimeter coordinates to the DXF coordinate
    values. Use coord_scale=39.3700787402 and insunits=0 for ADS imports that
    treat DXF coordinates as mils.
    """
    lines: list[str] = [
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
        if rect.name.startswith("via_pad_") or rect.name.startswith("ground_via_"):
            cx = (rect.x + rect.w / 2.0) * coord_scale
            cy = (rect.y + rect.h / 2.0) * coord_scale
            radius = rect.w / 2.0 * coord_scale
            lines.extend(
                [
                    "0",
                    "CIRCLE",
                    "8",
                    rect.layer,
                    "10",
                    fmt(cx),
                    "20",
                    fmt(cy),
                    "30",
                    "0",
                    "40",
                    fmt(radius),
                ]
            )
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
        for (xa, ya), (xb, yb) in zip(points, points[1:]):
            lines.extend(
                [
                    "0",
                    "LINE",
                    "8",
                    rect.layer,
                    "10",
                    fmt(xa),
                    "20",
                    fmt(ya),
                    "30",
                    "0",
                    "11",
                    fmt(xb),
                    "21",
                    fmt(yb),
                    "31",
                    "0",
                ]
            )
    lines.extend(["0", "ENDSEC", "0", "EOF"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_svg(path: Path, rects: list[Rect | Quad], params: FilterParams) -> None:
    min_x, min_y, max_x, max_y = rect_bounds(rects)
    pad = 0.6
    panel_w = 4.8
    view_min_x = min_x - pad - panel_w
    view_min_y = min_y - pad
    view_w = max_x - min_x + 2.0 * pad + panel_w
    view_h = max_y - min_y + 2.0 * pad

    def sx(x: float) -> float:
        return x

    def sy(y: float) -> float:
        return view_min_y + view_h - (y - view_min_y)

    svg_rects: list[str] = []
    labels: list[str] = []
    for rect in rects:
        if isinstance(rect, Quad):
            points = " ".join(f"{fmt(sx(x))},{fmt(sy(y))}" for x, y in rect.points)
            svg_rects.append(
                '<polygon points="{points}" fill="#b88727" '
                'stroke="#33210a" stroke-width="0.025"/>'.format(points=points)
            )
            continue

        if rect.layer == "EM_BOUNDARY":
            svg_rects.append(
                '<rect x="{x}" y="{y}" width="{w}" height="{h}" '
                'fill="none" stroke="#177245" stroke-width="0.035" '
                'stroke-dasharray="0.16 0.12"/>'.format(
                    x=fmt(sx(rect.x)),
                    y=fmt(sy(rect.y + rect.h)),
                    w=fmt(rect.w),
                    h=fmt(rect.h),
                )
            )
            continue

        if rect.layer in effective_ground_layers(params) and rect.name.startswith(params.ground_plane_name):
            svg_rects.append(
                '<rect x="{x}" y="{y}" width="{w}" height="{h}" '
                'fill="#91b7d9" fill-opacity="0.24" stroke="#2b5f8a" stroke-width="0.03"/>'.format(
                    x=fmt(sx(rect.x)),
                    y=fmt(sy(rect.y + rect.h)),
                    w=fmt(rect.w),
                    h=fmt(rect.h),
                )
            )
            continue

        if rect.name.startswith("via_pad_"):
            svg_rects.append(
                '<circle cx="{cx}" cy="{cy}" r="{r}" '
                'fill="#b88727" stroke="#33210a" stroke-width="0.025"/>'.format(
                    cx=fmt(rect.x + rect.w / 2.0),
                    cy=fmt(sy(rect.y + rect.h / 2.0)),
                    r=fmt(rect.w / 2.0),
                )
            )
            continue

        if rect.layer == params.via_layer:
            svg_rects.append(
                '<circle cx="{cx}" cy="{cy}" r="{r}" '
                'fill="#2c7fb8" stroke="#083d70" stroke-width="0.025"/>'.format(
                    cx=fmt(rect.x + rect.w / 2.0),
                    cy=fmt(sy(rect.y + rect.h / 2.0)),
                    r=fmt(rect.w / 2.0),
                )
            )
            continue

        svg_rects.append(
            '<rect x="{x}" y="{y}" width="{w}" height="{h}" '
            'fill="#b88727" stroke="#33210a" stroke-width="0.025"/>'.format(
                x=fmt(sx(rect.x)),
                y=fmt(sy(rect.y + rect.h)),
                w=fmt(rect.w),
                h=fmt(rect.h),
            )
        )
        if rect.name.startswith("resonator_"):
            labels.append(
                '<text x="{x}" y="{y}" font-size="0.28" text-anchor="middle" '
                'fill="#111">{label}</text>'.format(
                    x=fmt(rect.x + rect.w / 2.0),
                    y=fmt(sy(rect.y + rect.h / 2.0)),
                    label=escape(rect.name.split("_")[-1]),
                )
            )

    title = (
        f"{params.name}: {params.order}th order interdigital BPF, "
        f"{params.substrate} h={params.dielectric_height_mm} mm"
    )
    field_w = field_width(params)
    overall_h = overall_height(params)
    feed_len = feed_extension_len(params)
    boundary = boundary_rect(params)
    gap_text = ",".join(fmt(gap) for gap in params.gaps_mm)
    panel_lines = [
        "Layout mm",
        f"field {fmt(field_w)} x {fmt(overall_h)}",
        f"boundary {fmt(boundary.w)} x {fmt(boundary.h)}",
        f"L {fmt(params.resonator_l_mm)}",
        f"W {fmt(params.resonator_w_mm)}",
        f"W0 {fmt(params.w0_mm)}",
        f"tap {fmt(params.tap_from_bottom_mm)}",
        f"feed {fmt(feed_len)}",
        f"via {fmt(params.via_diameter_mm)}",
        f"pad {fmt(params.via_pad_mm)}",
        f"gaps {gap_text}",
    ]
    panel_x = min_x - pad - panel_w + 0.25
    panel_y = view_min_y + 0.5
    panel_text = [
        '<text x="{x}" y="{y}" font-size="{size}" fill="{fill}">{line}</text>'.format(
            x=fmt(panel_x),
            y=fmt(panel_y + index * 0.34),
            size="0.3" if index == 0 else "0.24",
            fill="#222" if index == 0 else "#444",
            line=escape(line),
        )
        for index, line in enumerate(panel_lines)
    ]
    content = "\n  ".join(svg_rects + labels + panel_text)
    text = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="520" viewBox="{fmt(view_min_x)} {fmt(view_min_y)} {fmt(view_w)} {fmt(view_h)}">
  <title>{escape(title)}</title>
  <rect x="{fmt(view_min_x)}" y="{fmt(view_min_y)}" width="{fmt(view_w)}" height="{fmt(view_h)}" fill="#f8f6ef"/>
  <rect x="{fmt(view_min_x + 0.12)}" y="{fmt(view_min_y + 0.12)}" width="{fmt(panel_w - 0.35)}" height="{fmt(view_h - 0.24)}" fill="#ffffff" fill-opacity="0.58" stroke="#d0ccc1" stroke-width="0.025"/>
  {content}
</svg>
"""
    path.write_text(text, encoding="utf-8")


def make_ads_vars(params: FilterParams, field_w: float, overall_h: float) -> str:
    lines = [
        "# ADS variables for the interdigital/combline BPF layout",
        "# Units: mm, GHz, ohm",
        f"er={fmt(params.er)}",
        f"h={fmt(params.dielectric_height_mm)}",
        f"cu_t={fmt(params.copper_thickness_mm)}",
        f"f_low={fmt(params.lower_cutoff_ghz)}",
        f"f_high={fmt(params.upper_cutoff_ghz)}",
        f"ripple_db={fmt(params.passband_ripple_db)}",
        f"z0={fmt(params.z0_ohm)}",
        f"W0={fmt(params.w0_mm)}",
        f"feed_taper_len={fmt(params.feed_taper_len_mm)}",
        f"feed_tip_w={fmt(params.feed_tip_w_mm)}",
        f"feed_overlap={fmt(params.feed_overlap_mm)}",
        f"W={fmt(params.resonator_w_mm)}",
        f"L={fmt(params.resonator_l_mm)}",
        f"tap={fmt(params.tap_from_bottom_mm)}",
        f"Egap={fmt(params.end_gap_mm)}",
        f"filter_field_w={fmt(field_w)}",
        f"filter_field_h={fmt(overall_h)}",
    ]
    for idx, gap in enumerate(params.gaps_mm, start=1):
        lines.append(f"S{idx}={fmt(gap)}")
    return "\n".join(lines) + "\n"


def write_tuning_table(path: Path, params: FilterParams) -> None:
    rows = [
        {
            "parameter": "L",
            "nominal_mm": params.resonator_l_mm,
            "sweep_min_mm": params.resonator_l_mm - 0.30,
            "sweep_max_mm": params.resonator_l_mm + 0.30,
            "step_mm": 0.05,
            "ads_variable": "L",
            "main_effect": "Center frequency; longer shifts passband lower.",
            "priority": "high",
        },
        {
            "parameter": "tap",
            "nominal_mm": params.tap_from_bottom_mm,
            "sweep_min_mm": params.tap_from_bottom_mm - 0.30,
            "sweep_max_mm": params.tap_from_bottom_mm + 0.30,
            "step_mm": 0.05,
            "ads_variable": "tap",
            "main_effect": "Input/output match and insertion loss.",
            "priority": "high",
        },
        {
            "parameter": "S1/S8",
            "nominal_mm": params.gaps_mm[0],
            "sweep_min_mm": max(params.min_fab_feature_mm, params.gaps_mm[0] - 0.08),
            "sweep_max_mm": params.gaps_mm[0] + 0.08,
            "step_mm": 0.01,
            "ads_variable": "S1,S8",
            "main_effect": "External-edge coupling, lower skirt, 5 GHz rejection, return loss.",
            "priority": "high",
        },
        {
            "parameter": "S2/S7",
            "nominal_mm": params.gaps_mm[1],
            "sweep_min_mm": params.gaps_mm[1] - 0.08,
            "sweep_max_mm": params.gaps_mm[1] + 0.08,
            "step_mm": 0.01,
            "ads_variable": "S2,S7",
            "main_effect": "Near-edge coupling and passband ripple.",
            "priority": "medium",
        },
        {
            "parameter": "S3/S6",
            "nominal_mm": params.gaps_mm[2],
            "sweep_min_mm": params.gaps_mm[2] - 0.08,
            "sweep_max_mm": params.gaps_mm[2] + 0.08,
            "step_mm": 0.01,
            "ads_variable": "S3,S6",
            "main_effect": "Mid-band coupling, ripple flatness, skirt slope.",
            "priority": "medium",
        },
        {
            "parameter": "S4/S5",
            "nominal_mm": params.gaps_mm[3],
            "sweep_min_mm": params.gaps_mm[3] - 0.08,
            "sweep_max_mm": params.gaps_mm[3] + 0.08,
            "step_mm": 0.01,
            "ads_variable": "S4,S5",
            "main_effect": "Center coupling and passband bandwidth.",
            "priority": "medium",
        },
        {
            "parameter": "W",
            "nominal_mm": params.resonator_w_mm,
            "sweep_min_mm": params.resonator_w_mm - 0.08,
            "sweep_max_mm": params.resonator_w_mm + 0.08,
            "step_mm": 0.02,
            "ads_variable": "W",
            "main_effect": "Resonator impedance and EM loading; keep tied to W0 initially.",
            "priority": "low",
        },
        {
            "parameter": "W0",
            "nominal_mm": params.w0_mm,
            "sweep_min_mm": params.w0_mm - 0.08,
            "sweep_max_mm": params.w0_mm + 0.08,
            "step_mm": 0.02,
            "ads_variable": "W0",
            "main_effect": "50 ohm launch width; usually fixed by stackup calculator.",
            "priority": "low",
        },
        {
            "parameter": "Egap",
            "nominal_mm": params.end_gap_mm,
            "sweep_min_mm": max(params.min_fab_feature_mm, params.end_gap_mm - 0.15),
            "sweep_max_mm": params.end_gap_mm + 0.15,
            "step_mm": 0.025,
            "ads_variable": "Egap",
            "main_effect": "Open-end capacitance and end-effect frequency shift.",
            "priority": "low",
        },
    ]
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            clean_row = {
                key: fmt(value) if isinstance(value, float) else value
                for key, value in row.items()
            }
            writer.writerow(clean_row)


def make_drc(params: FilterParams, field_w: float, overall_h: float) -> str:
    min_gap = min(params.gaps_mm)
    taper_width = params.feed_tip_w_mm if params.feed_taper_len_mm > 0.0 else params.w0_mm
    min_width = min(params.w0_mm, params.resonator_w_mm, taper_width)
    min_via = params.via_diameter_mm
    via_pad = max(params.via_pad_mm, params.via_diameter_mm)
    if params.via_pad_outside:
        open_end_pad_clearance = params.end_gap_mm - via_pad
    elif params.via_half_outside:
        open_end_pad_clearance = params.end_gap_mm - via_pad / 2.0
    else:
        open_end_pad_clearance = params.end_gap_mm - via_pad
    fab = params.min_fab_feature_mm
    pass_gap = min_gap >= fab
    pass_width = min_width >= fab
    pass_via = min_via >= fab
    pass_open_end_pad = open_end_pad_clearance >= fab
    feed_total_len = params.feed_len_mm + max(0.0, params.feed_taper_len_mm) - (
        max(0.0, params.feed_overlap_mm) if params.feed_taper_len_mm > 0.0 else 0.0
    )
    mode_notes = []
    if params.include_ground_plane:
        mode_notes.append(
            "  Reference ground copper rectangles are included on "
            f"{', '.join(effective_ground_layers(params))} using {params.ground_boundary_mode} extents."
        )
    else:
        mode_notes.append("  No explicit reference ground copper rectangle is included in the generated DXF.")
    if params.via_pad_mm > 0.0:
        mode_notes.append("  Circular top-metal via pads are drawn concentrically with the via holes.")
    if params.via_pad_outside:
        mode_notes.append("  via_pad_outside=True means each via pad sits outside the resonator end, tangent to the shorted edge.")
    if params.via_half_outside:
        mode_notes.append("  via_half_outside=True means each via/pad center sits on the resonator end edge.")
    if not mode_notes:
        mode_notes.append("  No separate top-metal via pad is drawn; the resonator metal itself carries the via landing.")
    if params.feed_taper_len_mm > 0.0:
        mode_notes.append("  Input/output feeds use mirrored tapered transitions into the edge resonators.")
    else:
        mode_notes.append("  Input/output feeds use direct rectangular taps into the edge resonators.")

    lines = [
        f"Design: {params.name}",
        f"Substrate: {params.substrate}, er={fmt(params.er)}, h={fmt(params.dielectric_height_mm)} mm, copper={fmt(params.copper_thickness_mm)} mm",
        f"Band: {fmt(params.lower_cutoff_ghz)}-{fmt(params.upper_cutoff_ghz)} GHz, order={params.order}, ripple={fmt(params.passband_ripple_db)} dB",
        "",
        "Fabrication check",
        f"  Rule minimum: {fmt(fab)} mm ({fmt(fab * 39.37007874015748)} mil)",
        f"  Minimum resonator/feed width: {fmt(min_width)} mm -> {'PASS' if pass_width else 'FAIL'}",
        f"  Minimum adjacent coupling gap: {fmt(min_gap)} mm -> {'PASS' if pass_gap else 'FAIL'}",
        f"  Ground via drawing diameter: {fmt(min_via)} mm -> {'PASS' if pass_via else 'FAIL'}",
        f"  Via top pad size: {fmt(params.via_pad_mm)} mm ({'enabled' if params.via_pad_mm > 0.0 else 'not drawn'})",
        f"  Open-end to opposite via-pad clearance: {fmt(open_end_pad_clearance)} mm -> {'PASS' if pass_open_end_pad else 'FAIL'}",
        "",
        "Geometry summary",
        f"  Resonator field width: {fmt(field_w)} mm",
        f"  Resonator/end-gap height: {fmt(overall_h)} mm",
        f"  50-ohm straight feedline length each side: {fmt(params.feed_len_mm)} mm",
        f"  Feed taper length each side: {fmt(params.feed_taper_len_mm)} mm",
        f"  Feed taper tip width: {fmt(params.feed_tip_w_mm)} mm",
        f"  Feed taper overlap into edge resonator: {fmt(params.feed_overlap_mm)} mm",
        f"  Feed metal extension each side: {fmt(feed_total_len)} mm",
        f"  EM boundary margin: {fmt(params.boundary_margin_mm)} mm",
        f"  Top metal layer: {params.metal_layer}",
        f"  Ground via layer: {params.via_layer}",
        f"  Reference ground layer: {params.ground_layer}",
        f"  Ground net layers: {', '.join(effective_ground_layers(params))}",
        f"  Explicit GND plane: {'enabled' if params.include_ground_plane else 'disabled'}",
        "",
        "Important assumptions",
        "  This is a first-pass interdigital/combline metal pattern for ADS/Momentum import.",
        "  Resonators alternate bottom/top grounding orientation by vertical offset.",
        "  One ground via is placed at the shorted end of each resonator.",
        *mode_notes,
        "  Input/output feeds touch the edge resonators at the configured tap height.",
        "  Exact port launch, via/ground treatment, solder-mask opening, and panel clearance still need ADS EM validation.",
    ]
    return "\n".join(lines) + "\n"


def make_dimension_check(params: FilterParams, field_w: float, overall_h: float) -> str:
    feed_total_len = params.feed_len_mm + max(0.0, params.feed_taper_len_mm) - (
        max(0.0, params.feed_overlap_mm) if params.feed_taper_len_mm > 0.0 else 0.0
    )
    metal_w = field_w + 2.0 * feed_total_len
    boundary_w = metal_w + 2.0 * params.boundary_margin_mm
    boundary_h = overall_h + 2.0 * params.boundary_margin_mm
    mil_per_mm = 39.37007874015748
    lines = [
        f"Design: {params.name}",
        "",
        "Expected dimensions after ADS import",
        f"  Resonator field: {fmt(field_w)} mm x {fmt(overall_h)} mm",
        f"  Metal including input/output feeds: {fmt(metal_w)} mm x {fmt(overall_h)} mm",
        f"  EM boundary outline: {fmt(boundary_w)} mm x {fmt(boundary_h)} mm",
        "",
        "Same values in mil",
        f"  Resonator field: {fmt(field_w * mil_per_mm)} mil x {fmt(overall_h * mil_per_mm)} mil",
        f"  Metal including input/output feeds: {fmt(metal_w * mil_per_mm)} mil x {fmt(overall_h * mil_per_mm)} mil",
        f"  EM boundary outline: {fmt(boundary_w * mil_per_mm)} mil x {fmt(boundary_h * mil_per_mm)} mil",
        "",
        "Import guidance",
        "  If ADS asks for DXF input units, choose millimeter for *_mm_coords.dxf.",
        "  If ADS treats DXF coordinates as mil/unitless, import *_ads_mil_coords.dxf.",
        "  A 25.4x error means inch/mm mismatch.",
        "  A 39.37x error means mil/mm mismatch.",
        "  A 1000x error means um/mm mismatch.",
    ]
    return "\n".join(lines) + "\n"


def write_outputs(params: FilterParams, out_dir: Path) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rects = build_rects(params)
    field_w = field_width(params)
    overall_h = overall_height(params)
    p1, p2 = port_locations(params)
    gnd_planes = ground_plane_rects(params) if params.include_ground_plane else []

    base = out_dir / params.name
    dxf_path = base.with_suffix(".dxf")
    dxf_mm_path = base.with_name(base.name + "_mm_coords.dxf")
    dxf_mil_path = base.with_name(base.name + "_ads_mil_coords.dxf")
    svg_path = base.with_suffix(".svg")
    json_path = base.with_name(base.name + "_params.json")
    layout_json_path = base.with_name(base.name + "_layout.json")
    drc_path = base.with_name(base.name + "_drc.txt")
    ads_vars_path = base.with_name(base.name + "_ads_vars.txt")
    tuning_table_path = base.with_name(base.name + "_tuning_table.csv")
    dimension_check_path = base.with_name(base.name + "_dimension_check.txt")

    write_dxf(dxf_path, rects)
    write_dxf(dxf_mm_path, rects)
    write_dxf(dxf_mil_path, rects, coord_scale=39.37007874015748, insunits=0)
    write_svg(svg_path, rects, params)
    json_path.write_text(
        json.dumps(
            {
                "parameters": asdict(params),
                "derived": {
                    "field_width_mm": field_w,
                    "overall_height_mm": overall_h,
                    "feed_extension_len_mm": feed_extension_len(params),
                    "ground_plane": asdict(gnd_planes[0]) if gnd_planes else None,
                    "ground_planes": [asdict(gnd) for gnd in gnd_planes],
                    "ground_layers": list(effective_ground_layers(params)),
                    "layout_ground_layers": list(layout_ground_layers(params)),
                    "minimum_gap_mm": min(params.gaps_mm),
                    "minimum_width_mm": min(
                        params.w0_mm,
                        params.resonator_w_mm,
                        params.feed_tip_w_mm if params.feed_taper_len_mm > 0.0 else params.w0_mm,
                    ),
                },
                "ports": {
                    "P1": [p1[0], p1[1]],
                    "P2": [p2[0], p2[1]],
                },
                "rectangles": [asdict(r) for r in rects],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_layout_json(layout_json_path, build_layout(params, rects))
    drc_path.write_text(make_drc(params, field_w, overall_h), encoding="utf-8")
    ads_vars_path.write_text(make_ads_vars(params, field_w, overall_h), encoding="utf-8")
    write_tuning_table(tuning_table_path, params)
    dimension_check_path.write_text(make_dimension_check(params, field_w, overall_h), encoding="utf-8")

    return {
        "dxf": str(dxf_path),
        "dxf_mm_coords": str(dxf_mm_path),
        "dxf_ads_mil_coords": str(dxf_mil_path),
        "svg": str(svg_path),
        "params": str(json_path),
        "layout_json": str(layout_json_path),
        "drc": str(drc_path),
        "ads_vars": str(ads_vars_path),
        "tuning_table": str(tuning_table_path),
        "dimension_check": str(dimension_check_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate RO4350B 9th-order interdigital BPF layout files for ADS import."
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "projects" / "bfp_6_8g_i7_fr4" / "layouts" / "reference_interdigital_9o_ro4350b_508um",
        help="Output directory. Default: SIM/projects/bfp_6_8g_i7_fr4/layouts/reference_interdigital_9o_ro4350b_508um",
    )
    parser.add_argument("--copper-um", type=float, default=35.0, help="Copper thickness in um.")
    parser.add_argument("--order", type=int, default=FilterParams.order, help="Filter order.")
    parser.add_argument("--substrate", default=FilterParams.substrate, help="Substrate name stored in params JSON.")
    parser.add_argument("--stackup-config", type=Path, default=None, help="PCB stackup JSON config used for naming and EM material parameters.")
    parser.add_argument(
        "--name-stackup-token",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Append/replace the configured stackup token in generated file and layout ids.",
    )
    parser.add_argument("--er", type=float, default=FilterParams.er, help="Relative dielectric constant.")
    parser.add_argument("--h-mm", type=float, default=0.508, help="Dielectric height in mm.")
    parser.add_argument("--name", default=FilterParams.name, help="Output design base name.")
    parser.add_argument("--w0-mm", type=float, default=FilterParams.w0_mm, help="Input/output feed width in mm.")
    parser.add_argument("--resonator-w-mm", type=float, default=FilterParams.resonator_w_mm, help="Resonator strip width in mm.")
    parser.add_argument("--l-mm", type=float, default=FilterParams.resonator_l_mm, help="Resonator length in mm.")
    parser.add_argument("--tap-mm", type=float, default=FilterParams.tap_from_bottom_mm, help="Tap position from bottom in mm.")
    parser.add_argument("--egap-mm", type=float, default=FilterParams.end_gap_mm, help="Open-end gap in mm.")
    parser.add_argument(
        "--gaps-mm",
        default=",".join(fmt(value) for value in FilterParams.gaps_mm),
        help="Comma-separated adjacent gaps S1..S8 in mm.",
    )
    parser.add_argument("--metal-layer", default="cond", help="ADS layout layer for top metal.")
    parser.add_argument("--via-layer", default="pcvia1", help="ADS layout layer for ground vias.")
    parser.add_argument(
        "--ground-layer",
        default=FilterParams.ground_layer,
        help="ADS layout layer for an explicit reference ground plane when --include-ground-plane is set.",
    )
    parser.add_argument(
        "--include-ground-plane",
        action=argparse.BooleanOptionalAction,
        default=FilterParams.include_ground_plane,
        help="Draw an explicit rectangular reference ground plane into DXF/layout JSON.",
    )
    parser.add_argument(
        "--ground-boundary-mode",
        choices=("port-edges", "em-boundary"),
        default=FilterParams.ground_boundary_mode,
        help="Ground plane extents. port-edges aligns left/right edges to P1/P2; em-boundary uses full EM boundary.",
    )
    parser.add_argument(
        "--ground-plane-name",
        default=FilterParams.ground_plane_name,
        help="Shape name for the explicit reference ground plane.",
    )
    parser.add_argument("--via-diameter-mm", type=float, default=0.50, help="Round via drawing diameter in mm.")
    parser.add_argument("--via-pad-mm", type=float, default=FilterParams.via_pad_mm, help="Local top-metal pad size around each via in mm.")
    parser.add_argument(
        "--via-half-outside",
        action="store_true",
        help="Place via centers on resonator end edges so half of each via/pad protrudes outward.",
    )
    parser.add_argument(
        "--via-pad-outside",
        action="store_true",
        help="Place each via pad outside the resonator end, tangent to the shorted edge.",
    )
    parser.add_argument("--feed-len-mm", type=float, default=FilterParams.feed_len_mm, help="Feedline length at each side in mm.")
    parser.add_argument(
        "--feed-taper-len-mm",
        type=float,
        default=FilterParams.feed_taper_len_mm,
        help="Taper length from 50-ohm line into each edge resonator in mm. Use 0 for rectangular direct taps.",
    )
    parser.add_argument(
        "--feed-tip-w-mm",
        type=float,
        default=FilterParams.feed_tip_w_mm,
        help="Narrow end width of the feed taper in mm.",
    )
    parser.add_argument(
        "--feed-overlap-mm",
        type=float,
        default=FilterParams.feed_overlap_mm,
        help="How far the taper tip overlaps into the edge resonator in mm.",
    )
    parser.add_argument(
        "--min-feature-mm",
        type=float,
        default=0.1524,
        help="Minimum manufacturable line/space in mm. Default is 6 mil.",
    )
    return parser.parse_args()


def parse_gaps(value: str) -> tuple[float, ...]:
    gaps = tuple(float(item.strip()) for item in value.split(",") if item.strip())
    return gaps


def main() -> None:
    args = parse_args()
    gaps = parse_gaps(args.gaps_mm)
    if len(gaps) != args.order - 1:
        raise ValueError(f"--gaps-mm must contain {args.order - 1} values for order={args.order}")
    params = FilterParams(
        name=args.name,
        order=args.order,
        substrate=args.substrate,
        er=args.er,
        dielectric_height_mm=args.h_mm,
        copper_thickness_mm=args.copper_um / 1000.0,
        w0_mm=args.w0_mm,
        resonator_w_mm=args.resonator_w_mm,
        resonator_l_mm=args.l_mm,
        tap_from_bottom_mm=args.tap_mm,
        end_gap_mm=args.egap_mm,
        gaps_mm=gaps,
        feed_len_mm=args.feed_len_mm,
        feed_taper_len_mm=args.feed_taper_len_mm,
        feed_tip_w_mm=args.feed_tip_w_mm,
        feed_overlap_mm=args.feed_overlap_mm,
        min_fab_feature_mm=args.min_feature_mm,
        metal_layer=args.metal_layer,
        via_layer=args.via_layer,
        ground_layer=args.ground_layer,
        include_ground_plane=args.include_ground_plane,
        ground_boundary_mode=args.ground_boundary_mode,
        ground_plane_name=args.ground_plane_name,
        via_diameter_mm=args.via_diameter_mm,
        via_pad_mm=args.via_pad_mm,
        via_half_outside=args.via_half_outside,
        via_pad_outside=args.via_pad_outside,
    )
    if args.stackup_config is not None:
        stackup = load_stackup_config(args.stackup_config)
        params = params_with_stackup_config(
            params,
            stackup,
            config_path=args.stackup_config,
            rename=args.name_stackup_token,
        )
    outputs = write_outputs(params, args.out_dir)
    print("Generated ADS layout support files:")
    for kind, path in outputs.items():
        print(f"  {kind}: {path}")


if __name__ == "__main__":
    main()


