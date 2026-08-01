#!/usr/bin/env python3
"""Generate ADS-importable DXF layouts for FR4 shorted-stub BPF candidates."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from html import escape
import argparse
import csv
import json
from pathlib import Path
import sys

_SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.exporters.json import write_layout_json
from simads.geometry import Boundary, LayerMap, Layout, Rect as LayoutRect, Via


@dataclass(frozen=True)
class StubBpfParams:
    name: str = "fr4_ssb_step_r_base"
    substrate: str = "FR4"
    er: float = 4.6
    dielectric_height_mm: float = 0.210
    copper_thickness_mm: float = 0.035
    lower_cutoff_ghz: float = 6.0
    upper_cutoff_ghz: float = 8.0
    z0_ohm: float = 50.0
    main_segment_count: int = 5
    section_l_mm: float = 5.167
    stub_l_mm: float = 5.167
    main_w_mm: float = 0.0904
    top_stub_w_mm: tuple[float, ...] = (0.425, 0.423, 0.423, 0.425)
    bottom_stub_w_mm: tuple[float, ...] = (0.249, 0.251, 0.243, 0.243, 0.245, 0.249)
    feed_len_mm: float = 1.5
    boundary_margin_mm: float = 1.2
    via_diameter_mm: float = 0.20
    via_edge_clearance_mm: float = 0.06
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


def parse_float_list(value: str) -> tuple[float, ...]:
    return tuple(float(item.strip()) for item in value.split(",") if item.strip())


def csv_value(row: dict[str, str], key: str, default: str) -> str:
    value = row.get(key, "").strip()
    return value if value else default


def row_to_params(row: dict[str, str]) -> StubBpfParams:
    defaults = StubBpfParams()
    return StubBpfParams(
        name=row["name"].strip(),
        substrate=csv_value(row, "substrate", defaults.substrate),
        er=float(csv_value(row, "er", str(defaults.er))),
        dielectric_height_mm=float(csv_value(row, "h_mm", str(defaults.dielectric_height_mm))),
        copper_thickness_mm=float(csv_value(row, "copper_mm", str(defaults.copper_thickness_mm))),
        main_segment_count=int(csv_value(row, "main_segment_count", str(defaults.main_segment_count))),
        section_l_mm=float(csv_value(row, "section_l_mm", str(defaults.section_l_mm))),
        stub_l_mm=float(csv_value(row, "stub_l_mm", str(defaults.stub_l_mm))),
        main_w_mm=float(csv_value(row, "main_w_mm", str(defaults.main_w_mm))),
        top_stub_w_mm=parse_float_list(csv_value(row, "top_stub_w_mm", ",".join(fmt(v) for v in defaults.top_stub_w_mm))),
        bottom_stub_w_mm=parse_float_list(
            csv_value(row, "bottom_stub_w_mm", ",".join(fmt(v) for v in defaults.bottom_stub_w_mm))
        ),
        feed_len_mm=float(csv_value(row, "feed_len_mm", str(defaults.feed_len_mm))),
        boundary_margin_mm=float(csv_value(row, "boundary_margin_mm", str(defaults.boundary_margin_mm))),
        via_diameter_mm=float(csv_value(row, "via_diameter_mm", str(defaults.via_diameter_mm))),
        via_edge_clearance_mm=float(csv_value(row, "via_edge_clearance_mm", str(defaults.via_edge_clearance_mm))),
        min_fab_feature_mm=float(csv_value(row, "min_fab_feature_mm", str(defaults.min_fab_feature_mm))),
        metal_layer=csv_value(row, "metal_layer", defaults.metal_layer),
        via_layer=csv_value(row, "via_layer", defaults.via_layer),
    )


def build_rects(params: StubBpfParams) -> list[Rect]:
    expected_top = max(0, params.main_segment_count - 1)
    expected_bottom = params.main_segment_count + 1
    if len(params.top_stub_w_mm) != expected_top:
        raise ValueError(f"top_stub_w_mm must contain {expected_top} values")
    if len(params.bottom_stub_w_mm) != expected_bottom:
        raise ValueError(f"bottom_stub_w_mm must contain {expected_bottom} values")

    field_w = params.main_segment_count * params.section_l_mm
    main_center_y = params.stub_l_mm + params.via_diameter_mm / 2.0 + params.via_edge_clearance_mm
    main_y = main_center_y - params.main_w_mm / 2.0
    rects: list[Rect] = [
        Rect(
            name="main_line",
            layer=params.metal_layer,
            x=-params.feed_len_mm,
            y=main_y,
            w=field_w + 2.0 * params.feed_len_mm,
            h=params.main_w_mm,
        )
    ]

    bottom_nodes = [idx * params.section_l_mm for idx in range(params.main_segment_count + 1)]
    top_nodes = [idx * params.section_l_mm for idx in range(1, params.main_segment_count)]

    for idx, (x_center, stub_w) in enumerate(zip(bottom_nodes, params.bottom_stub_w_mm, strict=True), start=1):
        rects.append(
            Rect(
                name=f"bottom_stub_{idx}",
                layer=params.metal_layer,
                x=x_center - stub_w / 2.0,
                y=main_y - params.stub_l_mm,
                w=stub_w,
                h=params.stub_l_mm + params.main_w_mm,
            )
        )
        rects.append(
            Rect(
                name=f"ground_via_bottom_{idx}",
                layer=params.via_layer,
                x=x_center - params.via_diameter_mm / 2.0,
                y=main_y - params.stub_l_mm,
                w=params.via_diameter_mm,
                h=params.via_diameter_mm,
            )
        )

    for idx, (x_center, stub_w) in enumerate(zip(top_nodes, params.top_stub_w_mm, strict=True), start=1):
        rects.append(
            Rect(
                name=f"top_stub_{idx}",
                layer=params.metal_layer,
                x=x_center - stub_w / 2.0,
                y=main_y,
                w=stub_w,
                h=params.stub_l_mm + params.main_w_mm,
            )
        )
        rects.append(
            Rect(
                name=f"ground_via_top_{idx}",
                layer=params.via_layer,
                x=x_center - params.via_diameter_mm / 2.0,
                y=main_y + params.main_w_mm + params.stub_l_mm - params.via_diameter_mm,
                w=params.via_diameter_mm,
                h=params.via_diameter_mm,
            )
        )

    min_x = -params.feed_len_mm
    max_x = field_w + params.feed_len_mm
    min_y = main_y - params.stub_l_mm
    max_y = main_y + params.main_w_mm + params.stub_l_mm
    rects.append(
        Rect(
            name="em_boundary",
            layer="EM_BOUNDARY",
            x=min_x - params.boundary_margin_mm,
            y=min_y - params.boundary_margin_mm,
            w=max_x - min_x + 2.0 * params.boundary_margin_mm,
            h=max_y - min_y + 2.0 * params.boundary_margin_mm,
        )
    )
    return rects


def build_layout(params: StubBpfParams, rects: list[Rect] | None = None) -> Layout:
    rects = rects or build_rects(params)
    shapes: list[LayoutRect | Via | Boundary] = []
    for rect in rects:
        if rect.layer == "EM_BOUNDARY":
            shapes.append(Boundary(name=rect.name, x=rect.x, y=rect.y, w=rect.w, h=rect.h, layer=rect.layer))
        elif rect.name.startswith("ground_via_"):
            shapes.append(
                Via(
                    name=rect.name,
                    layer=rect.layer,
                    x=rect.x + rect.w / 2.0,
                    y=rect.y + rect.h / 2.0,
                    diameter=rect.w,
                    metadata={"source": "generate_stub_bpf_layout"},
                )
            )
        else:
            shapes.append(LayoutRect(name=rect.name, layer=rect.layer, x=rect.x, y=rect.y, w=rect.w, h=rect.h))

    return Layout(
        layout_id=params.name,
        units="mm",
        layers=[
            LayerMap(name=params.metal_layer, dxf_layer=params.metal_layer),
            LayerMap(name=params.via_layer, dxf_layer=params.via_layer),
            LayerMap(name="EM_BOUNDARY", dxf_layer="EM_BOUNDARY"),
        ],
        shapes=shapes,
        metadata={
            "generator": "tools/generate_stub_bpf_layout.py",
            "topology": "shorted_stub_bpf",
            "substrate": params.substrate,
            "er": params.er,
            "dielectric_height_mm": params.dielectric_height_mm,
            "copper_thickness_mm": params.copper_thickness_mm,
        },
    )


def rect_bounds(rects: list[Rect]) -> tuple[float, float, float, float]:
    min_x = min(rect.x for rect in rects)
    min_y = min(rect.y for rect in rects)
    max_x = max(rect.x + rect.w for rect in rects)
    max_y = max(rect.y + rect.h for rect in rects)
    return min_x, min_y, max_x, max_y


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
                    fmt(rect.w / 2.0 * coord_scale),
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
        for (xa, ya), (xb, yb) in zip(points, points[1:], strict=False):
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


def write_svg(path: Path, rects: list[Rect], params: StubBpfParams) -> None:
    min_x, min_y, max_x, max_y = rect_bounds(rects)
    width = max_x - min_x
    height = max_y - min_y
    scale = 32
    svg_w = width * scale
    svg_h = height * scale
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(svg_w)}" height="{fmt(svg_h)}" '
        f'viewBox="{fmt(min_x)} {fmt(min_y)} {fmt(width)} {fmt(height)}">',
        '<rect x="{0}" y="{1}" width="{2}" height="{3}" fill="#fff" />'.format(
            fmt(min_x), fmt(min_y), fmt(width), fmt(height)
        ),
    ]
    for rect in rects:
        if rect.layer == "EM_BOUNDARY":
            parts.append(
                f'<rect x="{fmt(rect.x)}" y="{fmt(rect.y)}" width="{fmt(rect.w)}" height="{fmt(rect.h)}" '
                'fill="none" stroke="#777" stroke-width="0.03" stroke-dasharray="0.2 0.15" />'
            )
        elif rect.name.startswith("ground_via_"):
            cx = rect.x + rect.w / 2.0
            cy = rect.y + rect.h / 2.0
            parts.append(
                f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(rect.w / 2.0)}" '
                'fill="#c99700" stroke="#4d3300" stroke-width="0.025" />'
            )
        else:
            parts.append(
                f'<rect x="{fmt(rect.x)}" y="{fmt(rect.y)}" width="{fmt(rect.w)}" height="{fmt(rect.h)}" '
                'fill="#f5c542" stroke="#6f5200" stroke-width="0.025" />'
            )
    parts.append(
        f'<text x="{fmt(min_x + 0.2)}" y="{fmt(min_y + 0.35)}" font-size="0.32" fill="#333">'
        f'{escape(params.name)} FR4 shorted-stub BPF</text>'
    )
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def make_drc(params: StubBpfParams, rects: list[Rect]) -> str:
    metal_widths = [min(rect.w, rect.h) for rect in rects if rect.layer == params.metal_layer]
    min_x, min_y, max_x, max_y = rect_bounds([rect for rect in rects if rect.layer != "EM_BOUNDARY"])
    min_stub_width = min(min(params.top_stub_w_mm), min(params.bottom_stub_w_mm))
    pass_feature = min(min(metal_widths), params.via_diameter_mm) >= params.min_fab_feature_mm
    pass_via_fit = params.via_diameter_mm <= min_stub_width
    return "\n".join(
        [
            f"Design: {params.name}",
            f"Substrate: {params.substrate}, er={fmt(params.er)}, h={fmt(params.dielectric_height_mm)} mm, copper={fmt(params.copper_thickness_mm)} mm",
            f"Band: {fmt(params.lower_cutoff_ghz)}-{fmt(params.upper_cutoff_ghz)} GHz",
            "",
            "Fabrication check",
            f"  Rule minimum: {fmt(params.min_fab_feature_mm)} mm (6 mil)",
            f"  Minimum top metal width: {fmt(min(metal_widths))} mm -> {'PASS' if pass_feature else 'FAIL'}",
            f"  Via drawing diameter: {fmt(params.via_diameter_mm)} mm -> {'PASS' if params.via_diameter_mm >= params.min_fab_feature_mm else 'FAIL'}",
            f"  Via diameter <= minimum stub width: {fmt(min_stub_width)} mm -> {'PASS' if pass_via_fit else 'FAIL'}",
            "",
            "Geometry summary",
            f"  Main path section count: {params.main_segment_count}",
            f"  Electrical straight path length: {fmt(params.main_segment_count * params.section_l_mm)} mm",
            f"  Metal bounding box: {fmt(max_x - min_x)} mm x {fmt(max_y - min_y)} mm",
            f"  Top shorted stubs: {len(params.top_stub_w_mm)}",
            f"  Bottom shorted stubs: {len(params.bottom_stub_w_mm)}",
            f"  Top metal layer: {params.metal_layer}",
            f"  Ground via layer: {params.via_layer}",
        ]
    ) + "\n"


def make_dimension_check(params: StubBpfParams, rects: list[Rect]) -> str:
    min_x, min_y, max_x, max_y = rect_bounds(rects)
    mil_per_mm = 39.37007874015748
    return "\n".join(
        [
            f"Design: {params.name}",
            "",
            "Expected dimensions after ADS import",
            f"  EM boundary outline: {fmt(max_x - min_x)} mm x {fmt(max_y - min_y)} mm",
            f"  EM boundary outline: {fmt((max_x - min_x) * mil_per_mm)} mil x {fmt((max_y - min_y) * mil_per_mm)} mil",
            "",
            "Import guidance",
            "  Choose millimeter when importing *_mm_coords.dxf.",
            "  A low-pass EM response usually means shorted stubs are not connected to ground vias.",
        ]
    ) + "\n"


def write_outputs(params: StubBpfParams, out_dir: Path) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rects = build_rects(params)
    field_w = params.main_segment_count * params.section_l_mm
    main_center_y = params.stub_l_mm + params.via_diameter_mm / 2.0 + params.via_edge_clearance_mm
    metal_rects = [rect for rect in rects if rect.layer != "EM_BOUNDARY"]
    min_x, min_y, max_x, max_y = rect_bounds(metal_rects)

    base = out_dir / params.name
    dxf_path = base.with_suffix(".dxf")
    dxf_mm_path = base.with_name(base.name + "_mm_coords.dxf")
    dxf_mil_path = base.with_name(base.name + "_ads_mil_coords.dxf")
    svg_path = base.with_suffix(".svg")
    json_path = base.with_name(base.name + "_params.json")
    layout_json_path = base.with_name(base.name + "_layout.json")
    drc_path = base.with_name(base.name + "_drc.txt")
    dimension_check_path = base.with_name(base.name + "_dimension_check.txt")

    write_dxf(dxf_path, rects)
    write_dxf(dxf_mm_path, rects)
    write_dxf(dxf_mil_path, rects, coord_scale=39.37007874015748, insunits=0)
    write_svg(svg_path, rects, params)
    json_path.write_text(
        json.dumps(
            {
                "parameters": {
                    **asdict(params),
                    "feed_len_mm": params.feed_len_mm,
                    "tap_from_bottom_mm": main_center_y,
                },
                "derived": {
                    "field_width_mm": field_w,
                    "metal_width_mm": max_x - min_x,
                    "metal_height_mm": max_y - min_y,
                    "main_center_y_mm": main_center_y,
                    "minimum_width_mm": min(params.main_w_mm, min(params.top_stub_w_mm), min(params.bottom_stub_w_mm)),
                },
                "rectangles": [asdict(rect) for rect in rects],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_layout_json(layout_json_path, build_layout(params, rects))
    drc_path.write_text(make_drc(params, rects), encoding="utf-8")
    dimension_check_path.write_text(make_dimension_check(params, rects), encoding="utf-8")

    return {
        "dxf": str(dxf_path),
        "dxf_mm_coords": str(dxf_mm_path),
        "dxf_ads_mil_coords": str(dxf_mil_path),
        "svg": str(svg_path),
        "params": str(json_path),
        "layout_json": str(layout_json_path),
        "drc": str(drc_path),
        "dimension_check": str(dimension_check_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate FR4 shorted-stub BPF layout files for ADS import.")
    parser.add_argument("--plan", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parents[1] / "ADS" / "fr4_stub_bpf")
    parser.add_argument("--name", default=StubBpfParams.name)
    parser.add_argument("--main-segment-count", type=int, default=StubBpfParams.main_segment_count)
    parser.add_argument("--section-l-mm", type=float, default=StubBpfParams.section_l_mm)
    parser.add_argument("--stub-l-mm", type=float, default=StubBpfParams.stub_l_mm)
    parser.add_argument("--main-w-mm", type=float, default=StubBpfParams.main_w_mm)
    parser.add_argument("--top-stub-w-mm", default=",".join(fmt(value) for value in StubBpfParams.top_stub_w_mm))
    parser.add_argument("--bottom-stub-w-mm", default=",".join(fmt(value) for value in StubBpfParams.bottom_stub_w_mm))
    parser.add_argument("--feed-len-mm", type=float, default=StubBpfParams.feed_len_mm)
    parser.add_argument("--via-diameter-mm", type=float, default=StubBpfParams.via_diameter_mm)
    parser.add_argument("--metal-layer", default=StubBpfParams.metal_layer)
    parser.add_argument("--via-layer", default=StubBpfParams.via_layer)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.plan is not None:
        with args.plan.open(newline="", encoding="utf-8") as fp:
            rows = list(csv.DictReader(fp))
        print(f"Generating {len(rows)} FR4 shorted-stub candidates into {args.out_dir}")
        for row in rows:
            params = row_to_params(row)
            outputs = write_outputs(params, args.out_dir)
            print(f"  {params.name}: {outputs['dxf_mm_coords']}")
        return

    params = StubBpfParams(
        name=args.name,
        main_segment_count=args.main_segment_count,
        section_l_mm=args.section_l_mm,
        stub_l_mm=args.stub_l_mm,
        main_w_mm=args.main_w_mm,
        top_stub_w_mm=parse_float_list(args.top_stub_w_mm),
        bottom_stub_w_mm=parse_float_list(args.bottom_stub_w_mm),
        feed_len_mm=args.feed_len_mm,
        via_diameter_mm=args.via_diameter_mm,
        metal_layer=args.metal_layer,
        via_layer=args.via_layer,
    )
    outputs = write_outputs(params, args.out_dir)
    print("Generated ADS layout support files:")
    for kind, path in outputs.items():
        print(f"  {kind}: {path}")


if __name__ == "__main__":
    main()
