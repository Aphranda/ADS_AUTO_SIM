#!/usr/bin/env python3
"""Generate an SVG and JSON parameter record from an ADS DA_IDFilter1 model.

For the six-order component, W[1] and W[8] are the input/output coupled
lines, W[2]..W[7] are the six resonators, and S[1]..S[7] are the adjacent
gaps. The preview keeps those coupled lines separate from the resonators.
"""

from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path


MIL_TO_MM = 0.0254


DEFAULT_WIDTHS_MIL = (19.211, 21.518, 20.090, 20.363, 20.392, 20.452, 24.141, 19.310)
DEFAULT_GAPS_MIL = (3.335, 15.738, 17.814, 18.145, 17.839, 15.870, 3.353)


def _values(raw: str, expected: int, name: str) -> tuple[float, ...]:
    values = tuple(float(item.strip()) for item in raw.split(",") if item.strip())
    if len(values) != expected:
        raise ValueError(f"{name} must contain {expected} comma-separated values")
    return values


def _mm(mil: float) -> float:
    return mil * MIL_TO_MM


def _fmt(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def generate(args: argparse.Namespace) -> dict[str, str]:
    widths_mil = _values(args.widths_mil, 8, "--widths-mil")
    gaps_mil = _values(args.gaps_mil, 7, "--gaps-mil")
    widths = tuple(_mm(value) for value in widths_mil)
    gaps = tuple(_mm(value) for value in gaps_mil)
    length = _mm(args.length_mil)
    x_positions: list[float] = []
    cursor = 0.0
    for index, width in enumerate(widths):
        x_positions.append(cursor)
        cursor += width
        if index < len(gaps):
            cursor += gaps[index]
    field_width = cursor
    tap_len = args.tap_len_mm
    taper_len = min(max(args.taper_len_mm, 0.0), tap_len)
    straight_len = tap_len - taper_len
    tap_tip_w = min(max(args.tap_tip_w_mm, 0.0), min(widths[0], widths[-1]))
    tap_y = length / 2.0 if args.tap_y_mm is None else min(max(args.tap_y_mm, 0.0), length)
    pad_d = max(args.via_pad_mm, args.via_diameter_mm)
    margin = args.margin_mm
    view_min_x = -margin - tap_len - 0.6
    view_min_y = -margin - 0.55
    view_w = field_width + 2 * margin + 2 * tap_len + 1.2
    view_h = length + 2 * margin + 1.1
    shapes: list[dict[str, object]] = []
    svg_items: list[str] = []
    for index, (x, width) in enumerate(zip(x_positions, widths, strict=True), start=1):
        is_input_feed = index == 1
        is_output_feed = index == 8
        is_resonator = not (is_input_feed or is_output_feed)
        fill = "#4d79a8" if is_input_feed or is_output_feed else "#b88727"
        net = "P1" if is_input_feed else "P2" if is_output_feed else f"N_{index - 1}"
        shapes.append({
            "name": "input_coupled_section" if is_input_feed else "output_coupled_section" if is_output_feed else f"resonator_{index - 1}",
            "layer": "cond",
            "x_mm": x,
            "y_mm": 0.0,
            "w_mm": width,
            "h_mm": length,
            "net": net,
            "metadata": {
                "ads_width_mil": widths_mil[index - 1],
                "role": "input_coupled_line" if is_input_feed else "output_coupled_line" if is_output_feed else "resonator",
            },
        })
        svg_items.append(
            f'<rect x="{_fmt(x)}" y="0" width="{_fmt(width)}" height="{_fmt(length)}" '
            f'fill="{fill}" stroke="#33210a" stroke-width="0.012"/>'
        )
        # Every one of the eight physical sections has one grounded end.
        # W1/W8 are the external coupled sections, but they still receive
        # the alternating short-to-ground via shown in the ADS model.
        grounded_at_top = index % 2 == 0
        via_y = length if grounded_at_top else 0.0
        shapes.append({
            "name": f"ground_via_{index}",
            "layer": "pcvia1",
            "x_mm": x + width / 2,
            "y_mm": via_y,
            "diameter_mm": args.via_diameter_mm,
            "pad_diameter_mm": args.via_pad_mm,
            "net": "GND",
            "metadata": {"grounded_end": "top" if grounded_at_top else "bottom"},
        })
        svg_items.append(
            f'<circle cx="{_fmt(x + width / 2)}" cy="{_fmt(via_y)}" r="{_fmt(args.via_pad_mm / 2)}" '
            'fill="#b88727" stroke="#33210a" stroke-width="0.012"/>'
        )
        svg_items.append(
            f'<circle cx="{_fmt(x + width / 2)}" cy="{_fmt(via_y)}" r="{_fmt(args.via_diameter_mm / 2)}" '
            'fill="#2c7fb8" stroke="#083d70" stroke-width="0.012"/>'
        )
    input_tap = {
        "name": "input_feed",
        "layer": "cond",
        "x_mm": -tap_len,
        "y_mm": tap_y - widths[0] / 2,
        "w_mm": straight_len,
        "h_mm": widths[0],
        "net": "P1",
    }
    input_taper = {
        "name": "input_feed_taper",
        "layer": "cond",
        "points": [
            [-taper_len, tap_y - widths[0] / 2],
            [-taper_len, tap_y + widths[0] / 2],
            [0.0, tap_y + tap_tip_w / 2],
            [0.0, tap_y - tap_tip_w / 2],
        ],
        "net": "P1",
    }
    output_tap = {
        "name": "output_feed",
        "layer": "cond",
        "x_mm": field_width + taper_len,
        "y_mm": tap_y - widths[-1] / 2,
        "w_mm": straight_len,
        "h_mm": widths[-1],
        "net": "P2",
    }
    output_taper = {
        "name": "output_feed_taper",
        "layer": "cond",
        "points": [
            [field_width, tap_y - tap_tip_w / 2],
            [field_width, tap_y + tap_tip_w / 2],
            [field_width + taper_len, tap_y + widths[-1] / 2],
            [field_width + taper_len, tap_y - widths[-1] / 2],
        ],
        "net": "P2",
    }
    shapes.extend([input_tap, input_taper, output_taper, output_tap])
    svg_items.extend(
        [
            f'<rect x="{_fmt(input_tap["x_mm"])}" y="{_fmt(input_tap["y_mm"])}" width="{_fmt(input_tap["w_mm"])}" height="{_fmt(input_tap["h_mm"])}" fill="#4d79a8" stroke="#33210a" stroke-width="0.012"/>',
            f'<polygon points="{" ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in input_taper["points"])}" fill="#4d79a8" stroke="#33210a" stroke-width="0.012"/>',
            f'<polygon points="{" ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in output_taper["points"])}" fill="#4d79a8" stroke="#33210a" stroke-width="0.012"/>',
            f'<rect x="{_fmt(output_tap["x_mm"])}" y="{_fmt(output_tap["y_mm"])}" width="{_fmt(output_tap["w_mm"])}" height="{_fmt(output_tap["h_mm"])}" fill="#4d79a8" stroke="#33210a" stroke-width="0.012"/>',
        ]
    )
    port1 = {"name": "P1", "x_mm": -tap_len, "y_mm": tap_y, "reference": "GND"}
    port2 = {"name": "P2", "x_mm": field_width + tap_len, "y_mm": tap_y, "reference": "GND"}
    shapes.append({"name": "P1", "layer": "port", **port1})
    shapes.append({"name": "P2", "layer": "port", **port2})
    svg_items.extend(
        [
            f'<line x1="{_fmt(port1["x_mm"])}" y1="{_fmt(port1["y_mm"] - 0.18)}" x2="{_fmt(port1["x_mm"])}" y2="{_fmt(port1["y_mm"] + 0.18)}" stroke="#177245" stroke-width="0.025"/>',
            f'<line x1="{_fmt(port2["x_mm"])}" y1="{_fmt(port2["y_mm"] - 0.18)}" x2="{_fmt(port2["x_mm"])}" y2="{_fmt(port2["y_mm"] + 0.18)}" stroke="#177245" stroke-width="0.025"/>',
            f'<text x="{_fmt(port1["x_mm"] - 0.05)}" y="{_fmt(port1["y_mm"] + 0.38)}" font-size="0.18" fill="#177245">P1</text>',
            f'<text x="{_fmt(port2["x_mm"] + 0.08)}" y="{_fmt(port2["y_mm"] + 0.38)}" font-size="0.18" fill="#177245">P2</text>',
        ]
    )
    panel_lines = [
        f"DA_IDFilter1 N=6: 8 sections, 8 alternating GND vias, 7 gaps",
        f"Length = {_fmt(length)} mm ({_fmt(args.length_mil)} mil)",
        f"W1..W8 = {', '.join(_fmt(value) for value in widths)} mm",
        f"S1..S7 = {', '.join(_fmt(value) for value in gaps)} mm",
        f"tap y = {_fmt(tap_y)} mm from bottom; tap = {_fmt(tap_len)} mm ({_fmt(straight_len)} mm straight + {_fmt(taper_len)} mm taper), tip = {_fmt(tap_tip_w)} mm",
        f"via = {_fmt(args.via_diameter_mm)} mm, pad = {_fmt(args.via_pad_mm)} mm",
        "Tap/taper geometry is added for routing preview; it is not part of the ADS parameter table",
    ]
    panel_x = view_min_x + 0.25
    panel_y = view_min_y + 0.35
    for line_index, line in enumerate(panel_lines):
        svg_items.append(
            f'<text x="{_fmt(panel_x)}" y="{_fmt(panel_y + line_index * 0.28)}" '
            f'font-size="{0.22 if line_index == 0 else 0.16}" fill="#333">{escape(line)}</text>'
        )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="600" '
        f'viewBox="{_fmt(view_min_x)} {_fmt(view_min_y)} {_fmt(view_w)} {_fmt(view_h)}">\n'
        f'  <title>ADS interdigital parameterized core, Length={_fmt(length)} mm</title>\n'
        f'  <rect x="{_fmt(view_min_x)}" y="{_fmt(view_min_y)}" width="{_fmt(view_w)}" height="{_fmt(view_h)}" fill="#f8f6ef"/>\n'
        + "\n  ".join(svg_items)
        + "\n</svg>\n"
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    base = args.out_dir / args.name
    svg_path = base.with_suffix(".svg")
    params_path = base.with_name(base.name + "_params.json")
    layout_path = base.with_name(base.name + "_layout.json")
    svg_path.write_text(svg, encoding="utf-8")
    params_path.write_text(
        json.dumps(
            {
                "source": "ADS screenshot supplied by user",
                "units_source": "mil",
                "order": 6,
                "component": "DA_IDFilter1",
                "response_type": "Chebyshev",
                "coupling_type": "Coupled Line Transformer Input",
                "f_stop_low_ghz": 16.5,
                "f_pass_low_ghz": 18.7,
                "f_pass_high_ghz": 20.325,
                "f_stop_high_ghz": 23.5,
                "passband_ripple_db": 0.5,
                "stopband_attenuation_db": 40.0,
                "z0_ohm": 50.0,
                "ya": 1.0,
                "delta_mil": 0.0,
                "substrate": args.substrate,
                "er": args.er,
                "dielectric_height_mm": args.h_mm,
                "dielectric_loss_tangent": args.tan_d,
                "copper_thickness_mm": args.copper_um / 1000.0,
                "length_mil": args.length_mil,
                "length_mm": length,
                "widths_mil": widths_mil,
                "widths_mm": widths,
                "gaps_mil": gaps_mil,
                "gaps_mm": gaps,
                "via_diameter_mm": args.via_diameter_mm,
                "via_pad_mm": args.via_pad_mm,
                "tap_len_mm": tap_len,
                "tap_y_mm": tap_y,
                "taper_len_mm": taper_len,
                "tap_tip_w_mm": tap_tip_w,
                "notes": [
                    "W1/W8 are the external coupled sections; all eight sections have one alternating grounded end.",
                    "S6=15.870 mil was transcribed from the visible ADS parameter screenshot.",
                    "The component screenshot does not expose a separate via diameter; the preview uses the project values 0.2/0.4 mm.",
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    hfss_shapes: list[dict[str, object]] = []
    for shape in shapes:
        layer = str(shape.get("layer", "cond"))
        name = str(shape.get("name", "shape"))
        metadata = dict(shape.get("metadata") if isinstance(shape.get("metadata"), dict) else {})
        if shape.get("net"):
            metadata["net"] = str(shape["net"])
        if "points" in shape:
            hfss_shapes.append({"name": name, "layer": layer, "points": shape["points"], "kind": "polygon", "metadata": metadata})
        elif "diameter_mm" in shape:
            hfss_shapes.append({
                "name": name,
                "layer": "pcvia1",
                "x": float(shape["x_mm"]),
                "y": float(shape["y_mm"]),
                "diameter": float(shape["diameter_mm"]),
                "pad_diameter": float(shape["pad_diameter_mm"]),
                "pad_layer": "cond",
                "kind": "via",
                "metadata": metadata,
            })
        elif layer != "port":
            hfss_shapes.append({
                "name": name,
                "layer": layer,
                "x": float(shape["x_mm"]),
                "y": float(shape["y_mm"]),
                "w": float(shape["w_mm"]),
                "h": float(shape["h_mm"]),
                "kind": "rect",
                "metadata": metadata,
            })
    boundary = {
        "name": "em_boundary",
        "layer": "EM_BOUNDARY",
        "x": -tap_len - margin,
        "y": -margin,
        "w": field_width + 2 * tap_len + 2 * margin,
        "h": length + 2 * margin,
        "kind": "boundary",
        "metadata": {"role": "reference_ground", "net": "GND"},
    }
    hfss_shapes.append(boundary)
    hfss_ports = [
        {"name": "P1", "number": 1, "x": port1["x_mm"], "y": port1["y_mm"], "width": widths[0], "layer": "cond", "orientation_deg": 0.0, "reference": "gnd_plane", "kind": "port"},
        {"name": "P2", "number": 2, "x": port2["x_mm"], "y": port2["y_mm"], "width": widths[-1], "layer": "cond", "orientation_deg": 180.0, "reference": "gnd_plane", "kind": "port"},
    ]
    layout_path.write_text(
        json.dumps(
            {
                "layout_id": args.name,
                "units": "mm",
                "layers": [
                    {"name": "cond", "purpose": "drawing"},
                    {"name": "pcvia1", "purpose": "drawing"},
                    {"name": "GND", "purpose": "drawing"},
                    {"name": "EM_BOUNDARY", "purpose": "drawing"},
                ],
                "shapes": hfss_shapes,
                "ports": hfss_ports,
                "metadata": {
                    "topology": "ads_da_idfilter1_sixth_order",
                    "source": "ADS screenshot",
                    "order": 6,
                    "substrate": args.substrate,
                    "er": args.er,
                    "dielectric_height_mm": args.h_mm,
                    "copper_thickness_mm": args.copper_um / 1000.0,
                    "ground_boundary_mode": "em-boundary",
                    "ground_plane_name": "hfss_ground_plane",
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {"svg": str(svg_path), "params": str(params_path), "layout": str(layout_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--name", default="TX_band1_RO4350_ads8_parameterized")
    parser.add_argument("--length-mil", type=float, default=85.471)
    parser.add_argument("--widths-mil", default=",".join(str(value) for value in DEFAULT_WIDTHS_MIL))
    parser.add_argument("--gaps-mil", default=",".join(str(value) for value in DEFAULT_GAPS_MIL))
    parser.add_argument("--substrate", default="Subst1 / RO4350B")
    parser.add_argument("--er", type=float, default=3.66)
    parser.add_argument("--h-mm", type=float, default=9.8 * MIL_TO_MM)
    parser.add_argument("--tan-d", type=float, default=0.0031)
    parser.add_argument("--copper-um", type=float, default=1.4 * MIL_TO_MM * 1000.0)
    parser.add_argument("--via-diameter-mm", type=float, default=0.2)
    parser.add_argument("--via-pad-mm", type=float, default=0.4)
    parser.add_argument("--margin-mm", type=float, default=0.8)
    parser.add_argument("--tap-len-mm", type=float, default=1.0)
    parser.add_argument("--tap-y-mm", type=float, default=None)
    parser.add_argument("--taper-len-mm", type=float, default=0.6)
    parser.add_argument("--tap-tip-w-mm", type=float, default=0.2)
    args = parser.parse_args()
    print(json.dumps(generate(args), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
