#!/usr/bin/env python3
"""Generate a first-pass high/low impedance SIR bandpass layout for ADS."""

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
from simads.geometry import Boundary, LayerMap, Layout, Port, Rect as LayoutRect


@dataclass(frozen=True)
class HiloSirParams:
    name: str = "hilo_sir_l3_base"
    substrate: str = "FR4_L3_REF"
    er: float = 4.6
    dielectric_height_mm: float = 1.2906
    copper_thickness_mm: float = 0.035
    lower_cutoff_ghz: float = 6.0
    upper_cutoff_ghz: float = 8.0
    order: int = 5
    z0_ohm: float = 50.0
    z_high_ohm: float = 75.0
    z_low_ohm: float = 42.0
    feed_w_mm: float = 2.35
    high_w_mm: float = 0.86
    low_w_mm: float = 3.00
    arm_l_mm: float = 4.25
    bridge_l_mm: float = 2.45
    inner_gap_mm: float = 0.75
    coupling_gap_mm: float = 0.30
    coupling_gaps_mm: str = ""
    feed_gap_mm: float = 0.25
    feed_overlap_mm: float = 3.35
    feed_len_mm: float = 3.00
    boundary_margin_mm: float = 3.00
    min_fab_feature_mm: float = 0.1524
    metal_layer: str = "cond"


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


def row_to_params(row: dict[str, str]) -> HiloSirParams:
    defaults = HiloSirParams()
    return HiloSirParams(
        name=row["name"].strip(),
        substrate=row.get("substrate", defaults.substrate).strip() or defaults.substrate,
        er=parse_float(row, "er", defaults.er),
        dielectric_height_mm=parse_float(row, "h_mm", defaults.dielectric_height_mm),
        copper_thickness_mm=parse_float(row, "copper_mm", defaults.copper_thickness_mm),
        order=parse_int(row, "order", defaults.order),
        feed_w_mm=parse_float(row, "feed_w_mm", defaults.feed_w_mm),
        high_w_mm=parse_float(row, "high_w_mm", defaults.high_w_mm),
        low_w_mm=parse_float(row, "low_w_mm", defaults.low_w_mm),
        arm_l_mm=parse_float(row, "arm_l_mm", defaults.arm_l_mm),
        bridge_l_mm=parse_float(row, "bridge_l_mm", defaults.bridge_l_mm),
        inner_gap_mm=parse_float(row, "inner_gap_mm", defaults.inner_gap_mm),
        coupling_gap_mm=parse_float(row, "coupling_gap_mm", defaults.coupling_gap_mm),
        coupling_gaps_mm=row.get("coupling_gaps_mm", defaults.coupling_gaps_mm).strip(),
        feed_gap_mm=parse_float(row, "feed_gap_mm", defaults.feed_gap_mm),
        feed_overlap_mm=parse_float(row, "feed_overlap_mm", defaults.feed_overlap_mm),
        feed_len_mm=parse_float(row, "feed_len_mm", defaults.feed_len_mm),
        boundary_margin_mm=parse_float(row, "boundary_margin_mm", defaults.boundary_margin_mm),
        min_fab_feature_mm=parse_float(row, "min_fab_feature_mm", defaults.min_fab_feature_mm),
        metal_layer=row.get("metal_layer", defaults.metal_layer).strip() or defaults.metal_layer,
    )


def resonator_pitch(params: HiloSirParams) -> float:
    return 2.0 * params.high_w_mm + params.inner_gap_mm + params.coupling_gap_mm


def coupling_gaps(params: HiloSirParams) -> list[float]:
    if not params.coupling_gaps_mm.strip():
        return [params.coupling_gap_mm] * (params.order - 1)

    tokens = (
        params.coupling_gaps_mm.replace(";", ",")
        .replace("|", ",")
        .replace(" ", ",")
        .split(",")
    )
    gaps = [float(token) for token in tokens if token.strip()]
    expected = params.order - 1
    if len(gaps) != expected:
        raise ValueError(f"coupling_gaps_mm must contain {expected} gaps for order={params.order}, got {len(gaps)}")
    return gaps


def resonator_width(params: HiloSirParams) -> float:
    return 2.0 * params.high_w_mm + params.inner_gap_mm


def field_width(params: HiloSirParams) -> float:
    return params.order * resonator_width(params) + sum(coupling_gaps(params))


def build_rects(params: HiloSirParams) -> tuple[list[Rect], dict[str, tuple[float, float]]]:
    if params.order < 3:
        raise ValueError("order must be at least 3")

    rects: list[Rect] = []
    res_w = resonator_width(params)
    gaps = coupling_gaps(params)
    bridge_y = 0.0
    arm_y = params.low_w_mm
    top_y = arm_y + params.arm_l_mm

    x_positions = [0.0]
    for gap in gaps:
        x_positions.append(x_positions[-1] + res_w + gap)

    for idx in range(params.order):
        x0 = x_positions[idx]
        left_x = x0
        right_x = x0 + params.high_w_mm + params.inner_gap_mm
        bridge_center_x = x0 + res_w / 2.0
        bridge_x = bridge_center_x - params.bridge_l_mm / 2.0
        rects.extend(
            [
                Rect(f"res{idx + 1}_left_high_z_arm", params.metal_layer, left_x, arm_y, params.high_w_mm, params.arm_l_mm),
                Rect(f"res{idx + 1}_right_high_z_arm", params.metal_layer, right_x, arm_y, params.high_w_mm, params.arm_l_mm),
                Rect(f"res{idx + 1}_low_z_bridge", params.metal_layer, bridge_x, bridge_y, params.bridge_l_mm, params.low_w_mm),
            ]
        )

    feed_y = top_y - params.feed_overlap_mm
    input_x0 = -params.feed_len_mm - params.feed_gap_mm
    input_x1 = -params.feed_gap_mm
    output_x0 = field_width(params) + params.feed_gap_mm
    output_x1 = output_x0 + params.feed_len_mm
    rects.extend(
        [
            Rect("input_coupled_feed", params.metal_layer, input_x0, feed_y, params.feed_len_mm, params.feed_w_mm),
            Rect("output_coupled_feed", params.metal_layer, output_x0, feed_y, params.feed_len_mm, params.feed_w_mm),
        ]
    )

    min_x, min_y, max_x, max_y = rect_bounds(rects)
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
    ports = {
        "P1": (input_x0, feed_y + params.feed_w_mm / 2.0),
        "P2": (output_x1, feed_y + params.feed_w_mm / 2.0),
    }
    return rects, ports


def build_layout(
    params: HiloSirParams,
    rects: list[Rect] | None = None,
    ports: dict[str, tuple[float, float]] | None = None,
) -> Layout:
    if rects is None or ports is None:
        rects, ports = build_rects(params)

    shapes: list[LayoutRect | Boundary] = []
    for rect in rects:
        if rect.layer == "EM_BOUNDARY":
            shapes.append(Boundary(name=rect.name, x=rect.x, y=rect.y, w=rect.w, h=rect.h, layer=rect.layer))
        else:
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
            LayerMap(name="EM_BOUNDARY", dxf_layer="EM_BOUNDARY"),
        ],
        shapes=shapes,
        ports=layout_ports,
        metadata={
            "generator": "tools/generate_hilo_sir_bpf_layout.py",
            "topology": "high_low_impedance_sir_bpf",
            "order": params.order,
            "substrate": params.substrate,
            "er": params.er,
            "dielectric_height_mm": params.dielectric_height_mm,
            "copper_thickness_mm": params.copper_thickness_mm,
            "reference_plane": "L3",
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


def write_svg(path: Path, rects: list[Rect], params: HiloSirParams, ports: dict[str, tuple[float, float]]) -> None:
    min_x, min_y, max_x, max_y = rect_bounds(rects)
    width = max_x - min_x
    height = max_y - min_y
    scale = 36
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(width * scale)}" height="{fmt(height * scale)}" '
        f'viewBox="{fmt(min_x)} {fmt(min_y)} {fmt(width)} {fmt(height)}">',
        f'<rect x="{fmt(min_x)}" y="{fmt(min_y)}" width="{fmt(width)}" height="{fmt(height)}" fill="#fff"/>',
    ]
    for rect in rects:
        if rect.layer == "EM_BOUNDARY":
            parts.append(
                f'<rect x="{fmt(rect.x)}" y="{fmt(rect.y)}" width="{fmt(rect.w)}" height="{fmt(rect.h)}" '
                'fill="none" stroke="#777" stroke-width="0.03" stroke-dasharray="0.25 0.18"/>'
            )
        else:
            color = "#f3c33c" if "high_z" in rect.name else "#e2a82e"
            if "feed" in rect.name:
                color = "#ffd86a"
            parts.append(
                f'<rect x="{fmt(rect.x)}" y="{fmt(rect.y)}" width="{fmt(rect.w)}" height="{fmt(rect.h)}" '
                f'fill="{color}" stroke="#604500" stroke-width="0.025"/>'
            )
    for name, (x, y) in ports.items():
        parts.append(f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="0.12" fill="#1769ff"/>')
        parts.append(f'<text x="{fmt(x + 0.12)}" y="{fmt(y - 0.12)}" font-size="0.32">{escape(name)}</text>')
    parts.append(
        f'<text x="{fmt(min_x + 0.2)}" y="{fmt(min_y + 0.45)}" font-size="0.35" fill="#333">'
        f'{escape(params.name)} high/low impedance SIR BPF</text>'
    )
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def make_drc(params: HiloSirParams, rects: list[Rect]) -> str:
    metal_rects = [rect for rect in rects if rect.layer == params.metal_layer]
    min_feature = min(min(rect.w, rect.h) for rect in metal_rects)
    _, _, metal_max_x, metal_max_y = rect_bounds(metal_rects)
    metal_min_x, metal_min_y, _, _ = rect_bounds(metal_rects)
    gaps = coupling_gaps(params)
    min_gap = min([params.feed_gap_mm, params.inner_gap_mm, *gaps])
    return "\n".join(
        [
            f"Design: {params.name}",
            f"Substrate: {params.substrate}, er={fmt(params.er)}, h={fmt(params.dielectric_height_mm)} mm, copper={fmt(params.copper_thickness_mm)} mm",
            f"Band target: {fmt(params.lower_cutoff_ghz)}-{fmt(params.upper_cutoff_ghz)} GHz, order={params.order}",
            "",
            "Fabrication check",
            f"  Rule minimum: {fmt(params.min_fab_feature_mm)} mm (6 mil)",
            f"  Minimum metal width: {fmt(min_feature)} mm -> {'PASS' if min_feature >= params.min_fab_feature_mm else 'FAIL'}",
            f"  Minimum designed gap: {fmt(min_gap)} mm -> {'PASS' if min_gap >= params.min_fab_feature_mm else 'FAIL'}",
            "",
            "Geometry summary",
            f"  Resonator count: {params.order}",
            f"  Resonator path length approx: {fmt(2.0 * params.arm_l_mm + params.bridge_l_mm)} mm",
            f"  Metal bounding box: {fmt(metal_max_x - metal_min_x)} mm x {fmt(metal_max_y - metal_min_y)} mm",
            f"  High-Z arm width: {fmt(params.high_w_mm)} mm",
            f"  Low-Z bridge width: {fmt(params.low_w_mm)} mm",
            f"  Coupling gaps: {', '.join(fmt(gap) for gap in gaps)} mm",
            f"  Feed gap: {fmt(params.feed_gap_mm)} mm",
            "",
            "Important assumptions",
            "  L1 signal references L3 ground through L2 keepout.",
            "  This first-pass layout uses capacitively coupled input/output feed lines.",
            "  It is intended as an EM baseline, not a closed-form final synthesis.",
        ]
    ) + "\n"


def write_outputs(params: HiloSirParams, out_dir: Path) -> dict[str, str]:
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
    json_path.write_text(
        json.dumps(
            {
                "parameters": {
                    **asdict(params),
                    "tap_from_bottom_mm": ports["P1"][1],
                },
                "derived": {
                    "field_width_mm": field_width(params),
                    "resonator_width_mm": resonator_width(params),
                    "resonator_pitch_mm": resonator_pitch(params),
                    "coupling_gaps_mm": coupling_gaps(params),
                    "resonator_path_length_mm": 2.0 * params.arm_l_mm + params.bridge_l_mm,
                    "minimum_width_mm": min(params.feed_w_mm, params.high_w_mm, params.low_w_mm),
                    "minimum_gap_mm": min([params.feed_gap_mm, params.inner_gap_mm, *coupling_gaps(params)]),
                },
                "ports": {name: [x, y] for name, (x, y) in ports.items()},
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
    parser = argparse.ArgumentParser(description="Generate high/low impedance SIR BPF layout files.")
    parser.add_argument("--plan", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parents[1] / "ADS" / "hilo_sir_bpf")
    parser.add_argument("--name", default=HiloSirParams.name)
    parser.add_argument("--arm-l-mm", type=float, default=HiloSirParams.arm_l_mm)
    parser.add_argument("--bridge-l-mm", type=float, default=HiloSirParams.bridge_l_mm)
    parser.add_argument("--coupling-gap-mm", type=float, default=HiloSirParams.coupling_gap_mm)
    parser.add_argument("--coupling-gaps-mm", default=HiloSirParams.coupling_gaps_mm)
    parser.add_argument("--feed-gap-mm", type=float, default=HiloSirParams.feed_gap_mm)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.plan is not None:
        with args.plan.open(newline="", encoding="utf-8") as fp:
            rows = list(csv.DictReader(fp))
        print(f"Generating {len(rows)} high/low impedance SIR BPF candidates into {args.out_dir}")
        for row in rows:
            params = row_to_params(row)
            outputs = write_outputs(params, args.out_dir)
            print(f"  {params.name}: {outputs['dxf_mm_coords']}")
        return

    params = HiloSirParams(
        name=args.name,
        arm_l_mm=args.arm_l_mm,
        bridge_l_mm=args.bridge_l_mm,
        coupling_gap_mm=args.coupling_gap_mm,
        coupling_gaps_mm=args.coupling_gaps_mm,
        feed_gap_mm=args.feed_gap_mm,
    )
    outputs = write_outputs(params, args.out_dir)
    print("Generated high/low impedance SIR BPF layout support files:")
    for kind, path in outputs.items():
        print(f"  {kind}: {path}")


if __name__ == "__main__":
    main()
