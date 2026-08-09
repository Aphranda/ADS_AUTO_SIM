#!/usr/bin/env python3
"""Generate a BFP_5O Marki-style 5th-order L3-reference trial layout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from simads.exporters.svg import write_svg
from simads.geometry import Boundary, LayerMap, Layout, Polygon, Rect, Via


DEFAULT_OUT = (
    REPO_ROOT
    / "projects"
    / "bfp_real_board_hfss"
    / "layouts"
    / "candidates"
    / "bfp_5o_marki_l3_ref_r1"
    / "bfp_5o_marki_l3_ref_r1_layout.json"
)

DEFAULT_L2_CUTOUT_MARGIN_Y_MM = 0.45


def _rect_shape(name: str, layer: str, x0: float, y0: float, x1: float, y1: float, *, kind: str, metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "layer": layer,
        "x": x0,
        "y": y0,
        "w": x1 - x0,
        "h": y1 - y0,
        "kind": kind,
        "metadata": metadata,
    }


def _poly_shape(name: str, points: list[tuple[float, float]], *, metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "layer": "cond",
        "points": [[x, y] for x, y in points],
        "kind": "polygon",
        "metadata": metadata,
    }


def _ground_plane_parts(
    *,
    board: tuple[float, float, float, float],
    cutout: tuple[float, float, float, float],
    target_layer: str,
    name_prefix: str,
) -> list[dict[str, Any]]:
    bx0, by0, bx1, by1 = board
    cx0, cy0, cx1, cy1 = cutout
    metadata = {
        "role": "solid_reference_ground",
        "target_layer": target_layer,
        "candidate_source": "bfp_5o_marki_l3_ref_r1",
        "cutout_materialized": True,
    }
    pieces = [
        (bx0, by0, bx1, cy0),
        (bx0, cy1, bx1, by1),
        (bx0, cy0, cx0, cy1),
        (cx1, cy0, bx1, cy1),
    ]
    output: list[dict[str, Any]] = []
    for index, (x0, y0, x1, y1) in enumerate(pieces, start=1):
        if x1 - x0 <= 0.05 or y1 - y0 <= 0.05:
            continue
        output.append(
            _rect_shape(
                f"{name_prefix}_part_{index}",
                "reference_ground_plane",
                x0,
                y0,
                x1,
                y1,
                kind="reference_ground_plane",
                metadata=metadata,
            )
        )
    return output


def _layout_object(data: dict[str, Any]) -> Layout:
    shapes = []
    for shape in data["shapes"]:
        metadata = dict(shape.get("metadata") if isinstance(shape.get("metadata"), dict) else {})
        kind = shape.get("kind")
        if kind == "boundary":
            shapes.append(Boundary(name=shape["name"], x=shape["x"], y=shape["y"], w=shape["w"], h=shape["h"], layer=shape["layer"], metadata=metadata))
        elif kind == "polygon":
            shapes.append(Polygon(name=shape["name"], layer=shape["layer"], points=[(float(x), float(y)) for x, y in shape["points"]], metadata=metadata))
        elif kind == "via":
            shapes.append(
                Via(
                    name=shape["name"],
                    layer=shape["layer"],
                    x=shape["x"],
                    y=shape["y"],
                    diameter=shape["diameter"],
                    pad_diameter=shape.get("pad_diameter"),
                    pad_layer=shape.get("pad_layer"),
                    metadata=metadata,
                )
            )
        else:
            shapes.append(Rect(name=shape["name"], layer=shape["layer"], x=shape["x"], y=shape["y"], w=shape["w"], h=shape["h"], kind=kind, metadata=metadata))
    return Layout(
        layout_id=data["layout_id"],
        units=data["units"],
        layers=[LayerMap(name=item["name"], purpose=item.get("purpose", "drawing"), dxf_layer=item.get("dxf_layer")) for item in data["layers"]],
        shapes=shapes,
        metadata=data.get("metadata", {}),
    )


def build_layout(*, l2_cutout_mode: str = "window", l2_cutout_margin_y_mm: float = DEFAULT_L2_CUTOUT_MARGIN_Y_MM) -> tuple[dict[str, Any], dict[str, Any]]:
    board = (78.72857, 80.42656, 108.21543, 99.91344)
    center_x = (78.75085096988678 + 108.20024101209641) / 2.0
    feed_y = ((89.00413999999999 + 89.33434) / 2.0 + (88.99906 + 89.33808893800736) / 2.0) / 2.0

    w0 = 2.384
    resonator_w = 2.384
    resonator_l = 5.376
    tap_from_bottom = 1.969
    end_gap = 0.4935
    gaps = [0.7501, 1.108, 1.108, 0.7501]
    existing_feed_w = 0.3346
    field_w = 5 * resonator_w + sum(gaps)
    field_x0 = center_x - field_w / 2.0
    field_y0 = feed_y - tap_from_bottom
    field_y1 = field_y0 + resonator_l + end_gap
    left_feed_x0 = 78.75085096988678
    right_feed_x1 = 108.20024101209641
    taper_len = field_x0 - left_feed_x0
    right_taper_len = right_feed_x1 - (field_x0 + field_w)

    signal_meta = {
        "role": "signal_filter_core",
        "net": "RF",
        "candidate_source": "bfp_5o_marki_l3_ref_r1",
        "reference": "L3",
    }
    shapes: list[dict[str, Any]] = [
        {
            "name": "em_boundary",
            "x": board[0],
            "y": board[1],
            "w": board[2] - board[0],
            "h": board[3] - board[1],
            "layer": "EM_BOUNDARY",
            "kind": "boundary",
            "metadata": {"source": "BFP_5O_board_bbox"},
        }
    ]

    left_core_x = field_x0
    right_core_x = field_x0 + field_w
    feed_y0 = feed_y - existing_feed_w / 2.0
    feed_y1 = feed_y + existing_feed_w / 2.0
    wide_y0 = feed_y - w0 / 2.0
    wide_y1 = feed_y + w0 / 2.0
    shapes.extend(
        [
            _rect_shape("marki_5o_input_feed_tip", "cond", left_feed_x0, feed_y0, left_feed_x0 + 0.3, feed_y1, kind="rect", metadata=signal_meta),
            _poly_shape(
                "marki_5o_input_taper",
                [(left_feed_x0 + 0.3, feed_y0), (left_core_x, wide_y0), (left_core_x, wide_y1), (left_feed_x0 + 0.3, feed_y1)],
                metadata=signal_meta,
            ),
            _rect_shape("marki_5o_output_feed_tip", "cond", right_feed_x1 - 0.3, feed_y0, right_feed_x1, feed_y1, kind="rect", metadata=signal_meta),
            _poly_shape(
                "marki_5o_output_taper",
                [(right_core_x, wide_y0), (right_feed_x1 - 0.3, feed_y0), (right_feed_x1 - 0.3, feed_y1), (right_core_x, wide_y1)],
                metadata=signal_meta,
            ),
        ]
    )

    x = field_x0
    via_shapes: list[dict[str, Any]] = []
    for index in range(1, 6):
        bottom_anchored = index % 2 == 1
        y0 = field_y0 if bottom_anchored else field_y0 + end_gap
        shapes.append(
            _rect_shape(
                f"marki_5o_resonator_{index}",
                "cond",
                x,
                y0,
                x + resonator_w,
                y0 + resonator_l,
                kind="rect",
                metadata=signal_meta,
            )
        )
        via_cx = x + resonator_w / 2.0
        via_cy = y0 + 0.254 / 2.0 if bottom_anchored else y0 + resonator_l - 0.254 / 2.0
        via_shapes.append(
            {
                "name": f"marki_5o_ground_via_{index}",
                "x": via_cx,
                "y": via_cy,
                "diameter": 0.254,
                "pad_diameter": 0.55,
                "pad_layer": "cond",
                "layer": "pcvia1",
                "kind": "via",
                "metadata": {"role": "filter_short_via", "net": "GND", "candidate_source": "bfp_5o_marki_l3_ref_r1"},
            }
        )
        if index <= len(gaps):
            x += resonator_w + gaps[index - 1]
    shapes.extend(via_shapes)

    if l2_cutout_mode not in {"window", "solid"}:
        raise ValueError(f"unsupported l2_cutout_mode: {l2_cutout_mode}")
    l2_cutout = (board[0], field_y0 - l2_cutout_margin_y_mm, board[2], field_y1 + l2_cutout_margin_y_mm)
    if l2_cutout_mode == "window":
        shapes.extend(_ground_plane_parts(board=board, cutout=l2_cutout, target_layer="INNER1", name_prefix="marki_5o_inner1_l3_ref_ground"))

    metadata = {
        "candidate_id": "bfp_5o_marki_l3_ref_r1",
        "source_design": "BFP_5O",
        "optimization_goal": "test Marki 5th-order 6-8 GHz interdigital dimensions with L2 cutout and L3 reference",
        "suppress_default_reference_ground_plane": True,
        "board_bbox_mm": list(board),
        "reference_strategy": {
            "signal_layer": "TOP",
            "cutout_layer": "INNER1",
            "reference_layer": "INNER2",
            "l2_cutout_mode": l2_cutout_mode,
            "l2_cutout_margin_y_mm": l2_cutout_margin_y_mm,
            "core_copper_assumption": "Only INNER1 copper is opened under the wide 5th-order body; dielectric/core remains present and INNER2 stays a continuous ground reference.",
        },
        "delete_extra_names": [
            "poly__0",
            "poly__17",
            "poly__22",
            "poly__23",
            "poly__13",
            "poly__14",
            "poly__20",
            "poly__21",
            "poly__11",
            "poly__12",
            "poly__15",
            "poly__16",
            "poly__9",
            "poly__10",
            "poly__18",
            "poly__19",
            "poly__1",
            "poly__2",
            "poly__3",
            "poly__4",
            "poly__24",
        ],
        "delete_via_bbox_mm": [field_x0 - 0.8, field_y0 - 0.6, field_x0 + field_w + 0.8, field_y1 + 0.6],
        "marki_dimensions_mm": {
            "order": 5,
            "w0": w0,
            "resonator_w": resonator_w,
            "resonator_l": resonator_l,
            "tap_from_bottom": tap_from_bottom,
            "end_gap": end_gap,
            "gaps": gaps,
            "field_w": field_w,
            "field_x0": field_x0,
            "field_y0": field_y0,
            "field_y1": field_y1,
            "left_taper_len": taper_len,
            "right_taper_len": right_taper_len,
            "l2_cutout": l2_cutout,
        },
    }
    return {
        "layout_id": "bfp_5o_marki_l3_ref_r1",
        "units": "mm",
        "layers": [
            {"name": "cond", "purpose": "drawing", "dxf_layer": "cond"},
            {"name": "pcvia1", "purpose": "drawing", "dxf_layer": "pcvia1"},
            {"name": "EM_BOUNDARY", "purpose": "drawing", "dxf_layer": "EM_BOUNDARY"},
            {"name": "reference_ground_plane", "purpose": "drawing", "dxf_layer": "reference_ground_plane"},
        ],
        "shapes": shapes,
        "metadata": metadata,
    }, metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate BFP_5O Marki L3-reference trial layout JSON.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary-out", type=Path, default=None)
    parser.add_argument("--svg-out", type=Path, default=None)
    parser.add_argument("--l2-cutout-mode", choices=["window", "solid"], default="window")
    parser.add_argument("--l2-cutout-margin-y-mm", type=float, default=DEFAULT_L2_CUTOUT_MARGIN_Y_MM)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    layout, summary = build_layout(l2_cutout_mode=args.l2_cutout_mode, l2_cutout_margin_y_mm=args.l2_cutout_margin_y_mm)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(layout, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_out = args.summary_out or args.out.with_name(args.out.stem.removesuffix("_layout") + "_summary.json")
    summary_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    svg_out = args.svg_out or args.out.with_suffix(".svg")
    write_svg(svg_out, _layout_object(layout), title="BFP_5O Marki L3 reference r1")
    print(json.dumps({"layout": str(args.out), "summary": str(summary_out), "svg": str(svg_out), **summary}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
