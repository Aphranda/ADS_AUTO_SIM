#!/usr/bin/env python3
"""Generate QR-like pixelated microstrip BPF layout seeds for ADS import."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import argparse
import csv
import hashlib
import json
from pathlib import Path
import random
import sys

_SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.exporters.dxf import write_dxf
from simads.exporters.json import write_layout_json
from simads.exporters.svg import write_svg
from simads.geometry import Boundary, LayerMap, Layout, Port, Rect, fmt


@dataclass(frozen=True)
class PixelQrBpfParams:
    name: str = "pixel_qr_bpf_fr4_210um_8x8_seed0"
    substrate: str = "FR4"
    er: float = 4.6
    dielectric_height_mm: float = 0.210
    copper_thickness_mm: float = 0.035
    lower_cutoff_ghz: float = 6.0
    upper_cutoff_ghz: float = 8.0
    z0_ohm: float = 50.0
    matrix_n: int = 8
    pixel_mm: float = 0.50
    cell_pitch_mm: float = 0.0
    pixel_overfill_ratio: float = 0.0
    gap_mm: float = 0.12
    feed_w_mm: float = 0.36
    feed_len_mm: float = 2.0
    coupling_overlap_mm: float = 0.40
    boundary_margin_mm: float = 1.50
    min_fab_gap_mm: float = 0.1016
    min_fab_feature_mm: float = 0.1016
    fill_probability: float = 0.50
    seed: int = 0
    pattern: str = "qr_seed"
    custom_mask_rows: tuple[str, ...] = ()
    mirror_x: bool = True
    force_edge_coupling: bool = True
    connect_adjacent_pixels: bool = True
    metal_layer: str = "cond"
    via_layer: str = "pcvia1"
    boundary_layer: str = "EM_BOUNDARY"


def parse_bool(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "y"}:
        return True
    if lowered in {"0", "false", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"invalid bool value: {value!r}")


def csv_value(row: dict[str, str], key: str, default: object) -> str:
    value = row.get(key, "").strip()
    return value if value else str(default)


def parse_mask_rows(value: str) -> tuple[str, ...]:
    text = value.strip()
    if not text:
        return ()
    rows = tuple(part.strip() for part in text.replace("/", ";").split(";") if part.strip())
    if not rows:
        return ()
    width = len(rows[0])
    if any(len(row) != width or set(row) - {"0", "1"} for row in rows):
        raise ValueError("custom_mask_rows must be semicolon-separated equal-width 0/1 rows")
    return rows


def row_to_params(row: dict[str, str]) -> PixelQrBpfParams:
    defaults = PixelQrBpfParams()
    return PixelQrBpfParams(
        name=csv_value(row, "name", defaults.name),
        substrate=csv_value(row, "substrate", defaults.substrate),
        er=float(csv_value(row, "er", defaults.er)),
        dielectric_height_mm=float(csv_value(row, "h_mm", defaults.dielectric_height_mm)),
        copper_thickness_mm=float(csv_value(row, "copper_mm", defaults.copper_thickness_mm)),
        matrix_n=int(csv_value(row, "matrix_n", defaults.matrix_n)),
        pixel_mm=float(csv_value(row, "pixel_mm", defaults.pixel_mm)),
        cell_pitch_mm=float(csv_value(row, "cell_pitch_mm", defaults.cell_pitch_mm)),
        pixel_overfill_ratio=float(csv_value(row, "pixel_overfill_ratio", defaults.pixel_overfill_ratio)),
        gap_mm=float(csv_value(row, "gap_mm", defaults.gap_mm)),
        feed_w_mm=float(csv_value(row, "feed_w_mm", defaults.feed_w_mm)),
        feed_len_mm=float(csv_value(row, "feed_len_mm", defaults.feed_len_mm)),
        coupling_overlap_mm=float(csv_value(row, "coupling_overlap_mm", defaults.coupling_overlap_mm)),
        boundary_margin_mm=float(csv_value(row, "boundary_margin_mm", defaults.boundary_margin_mm)),
        min_fab_gap_mm=float(csv_value(row, "min_fab_gap_mm", defaults.min_fab_gap_mm)),
        min_fab_feature_mm=float(csv_value(row, "min_fab_feature_mm", defaults.min_fab_feature_mm)),
        fill_probability=float(csv_value(row, "fill_probability", defaults.fill_probability)),
        seed=int(csv_value(row, "seed", defaults.seed)),
        pattern=csv_value(row, "pattern", defaults.pattern),
        custom_mask_rows=parse_mask_rows(csv_value(row, "custom_mask_rows", "")),
        mirror_x=parse_bool(csv_value(row, "mirror_x", defaults.mirror_x)),
        force_edge_coupling=parse_bool(csv_value(row, "force_edge_coupling", defaults.force_edge_coupling)),
        connect_adjacent_pixels=parse_bool(csv_value(row, "connect_adjacent_pixels", defaults.connect_adjacent_pixels)),
        metal_layer=csv_value(row, "metal_layer", defaults.metal_layer),
        via_layer=csv_value(row, "via_layer", defaults.via_layer),
        boundary_layer=csv_value(row, "boundary_layer", defaults.boundary_layer),
    )


def matrix_size(params: PixelQrBpfParams) -> float:
    pitch = pixel_pitch(params)
    if params.connect_adjacent_pixels or params.cell_pitch_mm > 0:
        return params.matrix_n * pitch
    return params.matrix_n * params.pixel_mm + (params.matrix_n - 1) * params.gap_mm


def pixel_pitch(params: PixelQrBpfParams) -> float:
    if params.cell_pitch_mm > 0:
        return params.cell_pitch_mm
    if params.connect_adjacent_pixels:
        return params.pixel_mm
    return params.pixel_mm + params.gap_mm


def metal_pixel_mm(params: PixelQrBpfParams) -> float:
    return params.pixel_mm * (1.0 + params.pixel_overfill_ratio)


def make_mask(params: PixelQrBpfParams) -> list[list[int]]:
    n = params.matrix_n
    if params.pattern == "custom":
        rows = params.custom_mask_rows
        if len(rows) != n or any(len(row) != n for row in rows):
            raise ValueError("custom_mask_rows must be matrix_n x matrix_n for pattern=custom")
        return [[int(value) for value in row] for row in rows]

    rng = random.Random(params.seed)
    half_cols = (n + 1) // 2 if params.mirror_x else n
    mask = [[0 for _ in range(n)] for _ in range(n)]
    for row in range(n):
        for col in range(half_cols):
            value = 0
            if params.pattern == "checker":
                value = 1 if (row + col) % 2 == 0 else 0
            elif params.pattern == "diag":
                value = 1 if abs(row - col) <= 1 or abs(row + col - (n - 1)) <= 1 else 0
            elif params.pattern == "edge_coupled":
                value = 1 if row in {n // 2 - 1, n // 2} or col in {0, half_cols - 1} else 0
            elif params.pattern == "symmetric_random":
                value = 1 if rng.random() < params.fill_probability else 0
            elif params.pattern == "qr_seed":
                finder = row < 3 and col < 3
                timing = row == n // 2 or col == half_cols - 1
                random_fill = rng.random() < params.fill_probability
                value = 1 if finder or timing or random_fill else 0
            else:
                raise ValueError(f"unsupported pattern: {params.pattern}")
            mask[row][col] = value
            if params.mirror_x:
                mask[row][n - 1 - col] = value

    if params.force_edge_coupling:
        mid_rows = {max(0, n // 2 - 1), min(n - 1, n // 2)}
        for row in mid_rows:
            mask[row][0] = 1
            mask[row][n - 1] = 1
        for col in range(n):
            if abs(col - n // 2) <= 1:
                mask[n // 2][col] = 1
    return mask


def mask_hash(mask: list[list[int]]) -> str:
    text = "\n".join("".join(str(value) for value in row) for row in mask)
    return hashlib.sha256(text.encode("ascii")).hexdigest()[:16]


def mask_rows(mask: list[list[int]]) -> list[str]:
    return ["".join(str(value) for value in row) for row in mask]


def build_layout(params: PixelQrBpfParams) -> Layout:
    n = params.matrix_n
    if n < 4:
        raise ValueError("matrix_n must be >= 4")
    metal_w = metal_pixel_mm(params)
    if params.pixel_mm <= 0 or metal_w <= 0:
        raise ValueError("pixel_mm and metal pixel size must be positive")
    if metal_w < params.min_fab_feature_mm:
        raise ValueError("pixel_mm is smaller than min_fab_feature_mm")
    if not params.connect_adjacent_pixels and params.gap_mm < params.min_fab_gap_mm:
        raise ValueError("gap_mm is smaller than min_fab_gap_mm")
    if params.feed_w_mm < params.min_fab_feature_mm:
        raise ValueError("feed_w_mm is smaller than min_fab_feature_mm")
    if params.coupling_overlap_mm <= 0:
        raise ValueError("coupling_overlap_mm must be positive")

    mask = make_mask(params)
    size = matrix_size(params)
    x0 = 0.0
    y0 = -size / 2.0
    feed_y = -params.feed_w_mm / 2.0
    left_feed_x = -params.feed_len_mm
    effective_coupling_overlap_mm = max(params.coupling_overlap_mm, metal_w) if params.connect_adjacent_pixels else params.coupling_overlap_mm
    right_feed_x = size - effective_coupling_overlap_mm
    shapes: list[Rect | Boundary] = [
        Rect(
            name="feed_left",
            layer=params.metal_layer,
            x=left_feed_x,
            y=feed_y,
            w=params.feed_len_mm + effective_coupling_overlap_mm,
            h=params.feed_w_mm,
            metadata={"role": "port_feed", "port": "P1"},
        ),
        Rect(
            name="feed_right",
            layer=params.metal_layer,
            x=right_feed_x,
            y=feed_y,
            w=params.feed_len_mm + effective_coupling_overlap_mm,
            h=params.feed_w_mm,
            metadata={"role": "port_feed", "port": "P2"},
        ),
    ]

    pitch = pixel_pitch(params)
    metal_w = metal_pixel_mm(params)
    metal_center_offset = (metal_w - pitch) / 2.0 if params.cell_pitch_mm > 0 else 0.0
    for row in range(n):
        for col in range(n):
            if not mask[row][col]:
                continue
            x = x0 + col * pitch - metal_center_offset
            y = y0 + (n - 1 - row) * pitch - metal_center_offset
            shapes.append(
                Rect(
                    name=f"pix_r{row:02d}_c{col:02d}",
                    layer=params.metal_layer,
                    x=x,
                    y=y,
                    w=metal_w,
                    h=metal_w,
                    metadata={"role": "binary_pixel", "row": row, "col": col},
                )
            )

    min_x = left_feed_x
    max_x = size + params.feed_len_mm
    min_y = y0
    max_y = y0 + size
    boundary = Boundary(
        name="em_boundary",
        layer=params.boundary_layer,
        x=min_x - params.boundary_margin_mm,
        y=min_y - params.boundary_margin_mm,
        w=max_x - min_x + 2.0 * params.boundary_margin_mm,
        h=max_y - min_y + 2.0 * params.boundary_margin_mm,
    )
    shapes.append(boundary)

    ports = [
        Port(
            name="P1",
            number=1,
            x=left_feed_x,
            y=0.0,
            width=params.feed_w_mm,
            layer=params.metal_layer,
            orientation_deg=180.0,
            reference="ground",
        ),
        Port(
            name="P2",
            number=2,
            x=max_x,
            y=0.0,
            width=params.feed_w_mm,
            layer=params.metal_layer,
            orientation_deg=0.0,
            reference="ground",
        ),
    ]
    return Layout(
        layout_id=params.name,
        units="mm",
        layers=[
            LayerMap(name=params.metal_layer, dxf_layer=params.metal_layer),
            LayerMap(name=params.via_layer, dxf_layer=params.via_layer),
            LayerMap(name=params.boundary_layer, dxf_layer=params.boundary_layer),
        ],
        shapes=shapes,
        ports=ports,
        metadata={
            "generator": "tools/layout/generate_pixel_qr_bpf_layout.py",
            "layer_map_version": "profile-default-v1",
            "topology": "pixel_qr_bpf",
            "pixel_connectivity": "adjacent_ones_edge_touching" if params.connect_adjacent_pixels else "isolated_pixels",
            "mask_rows": mask_rows(mask),
            "mask_hash": mask_hash(mask),
            "substrate": params.substrate,
            "er": params.er,
            "dielectric_height_mm": params.dielectric_height_mm,
            "copper_thickness_mm": params.copper_thickness_mm,
            "effective_coupling_overlap_mm": effective_coupling_overlap_mm,
            "cell_pitch_mm": pitch,
            "metal_pixel_mm": metal_w,
            "pixel_overfill_ratio": params.pixel_overfill_ratio,
            "source_map": {
                "P1": "feed_left",
                "P2": "feed_right",
                "pixels": "pix_rXX_cXX",
            },
        },
    )


def make_params_json(params: PixelQrBpfParams, layout: Layout) -> dict[str, object]:
    size = matrix_size(params)
    metal_shapes = [shape for shape in layout.shapes if isinstance(shape, Rect) and shape.layer == params.metal_layer]
    fill_count = sum(1 for shape in metal_shapes if shape.name.startswith("pix_"))
    rows = [str(row) for row in layout.metadata["mask_rows"]]
    edge_touch_count = 0
    for row_idx, row in enumerate(rows):
        for col_idx, value in enumerate(row):
            if value != "1":
                continue
            if col_idx + 1 < len(row) and row[col_idx + 1] == "1":
                edge_touch_count += 1
            if row_idx + 1 < len(rows) and rows[row_idx + 1][col_idx] == "1":
                edge_touch_count += 1
    total_pixels = params.matrix_n * params.matrix_n
    min_x = -params.feed_len_mm
    max_x = size + params.feed_len_mm
    return {
        "parameters": asdict(params),
        "derived": {
            "region_w_mm": size,
            "region_h_mm": size,
            "cell_pitch_mm": layout.metadata.get("cell_pitch_mm", pixel_pitch(params)),
            "metal_pixel_mm": layout.metadata.get("metal_pixel_mm", metal_pixel_mm(params)),
            "total_length_mm": max_x - min_x,
            "pixel_fill_count": fill_count,
            "edge_touch_connection_count": edge_touch_count,
            "additional_connection_shape_count": 0,
            "pixel_total_count": total_pixels,
            "pixel_fill_ratio": fill_count / total_pixels,
            "mask_hash": layout.metadata["mask_hash"],
            "effective_coupling_overlap_mm": layout.metadata.get("effective_coupling_overlap_mm", params.coupling_overlap_mm),
        },
        "ports": {port.name: [port.x, port.y] for port in layout.ports},
        "port_details": [
            {
                "name": port.name,
                "number": port.number,
                "x_mm": port.x,
                "y_mm": port.y,
                "width_mm": port.width,
                "layer": port.layer,
                "orientation_deg": port.orientation_deg,
                "reference": port.reference,
            }
            for port in layout.ports
        ],
        "mask_rows": layout.metadata["mask_rows"],
    }


def make_drc(params: PixelQrBpfParams, layout: Layout) -> str:
    data = make_params_json(params, layout)
    derived = data["derived"]
    metal_w = metal_pixel_mm(params)
    pass_feature = metal_w >= params.min_fab_feature_mm and params.feed_w_mm >= params.min_fab_feature_mm
    pass_gap = True if params.connect_adjacent_pixels or params.cell_pitch_mm > 0 else params.gap_mm >= params.min_fab_gap_mm
    return "\n".join(
        [
            f"Design: {params.name}",
            f"Substrate: {params.substrate}, er={fmt(params.er)}, h={fmt(params.dielectric_height_mm)} mm, copper={fmt(params.copper_thickness_mm)} mm",
            f"Band: {fmt(params.lower_cutoff_ghz)}-{fmt(params.upper_cutoff_ghz)} GHz",
            "",
            "Fabrication check",
            f"  Rule minimum feature: {fmt(params.min_fab_feature_mm)} mm",
            f"  Rule minimum gap: {fmt(params.min_fab_gap_mm)} mm",
            f"  Cell pitch: {fmt(pixel_pitch(params))} mm",
            f"  Metal pixel width: {fmt(metal_w)} mm -> {'PASS' if metal_w >= params.min_fab_feature_mm else 'FAIL'}",
            f"  Pixel overfill ratio: {fmt(params.pixel_overfill_ratio)}",
            f"  Pixel gap: {'0 mm edge-touching grid' if params.connect_adjacent_pixels else fmt(params.gap_mm) + ' mm'} -> {'PASS' if pass_gap else 'FAIL'}",
            f"  Feed width: {fmt(params.feed_w_mm)} mm -> {'PASS' if params.feed_w_mm >= params.min_fab_feature_mm else 'FAIL'}",
            f"  Adjacent black pixels edge-touching: {params.connect_adjacent_pixels}",
            f"  Additional connection shapes: 0",
            f"  Overall feature/gap gate: {'PASS' if pass_feature and pass_gap else 'FAIL'}",
            "",
            "Geometry summary",
            f"  Matrix: {params.matrix_n} x {params.matrix_n}",
            f"  Pixel region: {fmt(derived['region_w_mm'])} mm x {fmt(derived['region_h_mm'])} mm",
            f"  Total length: {fmt(derived['total_length_mm'])} mm",
            f"  Filled pixels: {derived['pixel_fill_count']} / {derived['pixel_total_count']} ({fmt(derived['pixel_fill_ratio'])})",
            f"  Edge-touching adjacent pairs: {derived['edge_touch_connection_count']}",
            f"  Mask hash: {derived['mask_hash']}",
            "",
            "Import guidance",
            "  Import *_mm_coords.dxf as millimeter.",
            "  Place P1/P2 from params JSON if ADS import script does not consume layout JSON ports.",
        ]
    ) + "\n"


def write_outputs(params: PixelQrBpfParams, out_dir: Path) -> dict[str, str]:
    layout = build_layout(params)
    out_dir.mkdir(parents=True, exist_ok=True)
    base = out_dir / params.name
    dxf_path = base.with_suffix(".dxf")
    dxf_mm_path = base.with_name(base.name + "_mm_coords.dxf")
    dxf_mil_path = base.with_name(base.name + "_ads_mil_coords.dxf")
    svg_path = base.with_suffix(".svg")
    params_path = base.with_name(base.name + "_params.json")
    layout_path = base.with_name(base.name + "_layout.json")
    drc_path = base.with_name(base.name + "_drc.txt")

    write_dxf(dxf_path, layout)
    write_dxf(dxf_mm_path, layout)
    write_dxf(dxf_mil_path, layout, coord_scale=39.37007874015748, insunits=0)
    write_svg(svg_path, layout, title=f"{params.name} pixel QR BPF")
    write_layout_json(layout_path, layout)
    params_path.write_text(json.dumps(make_params_json(params, layout), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    drc_path.write_text(make_drc(params, layout), encoding="utf-8")
    return {
        "dxf": str(dxf_path),
        "dxf_mm_coords": str(dxf_mm_path),
        "dxf_ads_mil_coords": str(dxf_mil_path),
        "svg": str(svg_path),
        "params": str(params_path),
        "layout_json": str(layout_path),
        "drc": str(drc_path),
    }


def add_common_args(parser: argparse.ArgumentParser) -> None:
    defaults = PixelQrBpfParams()
    parser.add_argument("--name", default=defaults.name)
    parser.add_argument("--matrix-n", type=int, default=defaults.matrix_n)
    parser.add_argument("--pixel-mm", type=float, default=defaults.pixel_mm)
    parser.add_argument("--cell-pitch-mm", type=float, default=defaults.cell_pitch_mm)
    parser.add_argument("--pixel-overfill-ratio", type=float, default=defaults.pixel_overfill_ratio)
    parser.add_argument("--gap-mm", type=float, default=defaults.gap_mm)
    parser.add_argument("--feed-w-mm", type=float, default=defaults.feed_w_mm)
    parser.add_argument("--feed-len-mm", type=float, default=defaults.feed_len_mm)
    parser.add_argument("--coupling-overlap-mm", type=float, default=defaults.coupling_overlap_mm)
    parser.add_argument("--fill-probability", type=float, default=defaults.fill_probability)
    parser.add_argument("--seed", type=int, default=defaults.seed)
    parser.add_argument("--pattern", default=defaults.pattern, choices=["qr_seed", "checker", "diag", "edge_coupled", "symmetric_random", "custom"])
    parser.add_argument("--custom-mask-rows", default="")
    parser.add_argument("--mirror-x", type=parse_bool, default=defaults.mirror_x)
    parser.add_argument("--force-edge-coupling", type=parse_bool, default=defaults.force_edge_coupling)
    parser.add_argument("--connect-adjacent-pixels", type=parse_bool, default=defaults.connect_adjacent_pixels)
    parser.add_argument("--metal-layer", default=defaults.metal_layer)
    parser.add_argument("--via-layer", default=defaults.via_layer)
    parser.add_argument("--boundary-layer", default=defaults.boundary_layer)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate QR-like pixelated FR4 BPF layout seeds for ADS import.")
    parser.add_argument("--plan", type=Path, default=None)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("projects") / "pixel_qr_bpf_fr4_210um" / "layouts" / "pixel_qr_bpf_fr4_210um_r0",
    )
    add_common_args(parser)
    return parser.parse_args()


def params_from_args(args: argparse.Namespace) -> PixelQrBpfParams:
    return PixelQrBpfParams(
        name=args.name,
        matrix_n=args.matrix_n,
        pixel_mm=args.pixel_mm,
        cell_pitch_mm=args.cell_pitch_mm,
        pixel_overfill_ratio=args.pixel_overfill_ratio,
        gap_mm=args.gap_mm,
        feed_w_mm=args.feed_w_mm,
        feed_len_mm=args.feed_len_mm,
        coupling_overlap_mm=args.coupling_overlap_mm,
        fill_probability=args.fill_probability,
        seed=args.seed,
        pattern=args.pattern,
        custom_mask_rows=parse_mask_rows(args.custom_mask_rows),
        mirror_x=args.mirror_x,
        force_edge_coupling=args.force_edge_coupling,
        connect_adjacent_pixels=args.connect_adjacent_pixels,
        metal_layer=args.metal_layer,
        via_layer=args.via_layer,
        boundary_layer=args.boundary_layer,
    )


def main() -> None:
    args = parse_args()
    if args.plan is not None:
        with args.plan.open(newline="", encoding="utf-8") as fp:
            rows = list(csv.DictReader(fp))
        print(f"Generating {len(rows)} pixel QR BPF candidates into {args.out_dir}")
        for row in rows:
            params = row_to_params(row)
            outputs = write_outputs(params, args.out_dir)
            print(f"  {params.name}: {outputs['dxf_mm_coords']}")
        return

    params = params_from_args(args)
    outputs = write_outputs(params, args.out_dir)
    print("Generated ADS layout support files:")
    for kind, path in outputs.items():
        print(f"  {kind}: {path}")


if __name__ == "__main__":
    main()
