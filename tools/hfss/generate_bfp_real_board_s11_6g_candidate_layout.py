#!/usr/bin/env python3
"""Generate the first BFP real-board 6 GHz S11 tuning layout candidate.

The candidate keeps the extracted TOP copper and vias unchanged, then replaces
the INNER1/INNER2 solid reference planes with materialized ground-plane parts
around local launch relief windows.  The reference_ground_cutout shapes are kept
in the JSON for review, but HFSS drawing uses the already-split ground parts.
"""

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

DEFAULT_BASELINE = (
    REPO_ROOT
    / "projects"
    / "bfp_real_board_hfss"
    / "layouts"
    / "baseline"
    / "bfp_real_board_extracted_baseline_layout.json"
)
DEFAULT_OUT = (
    REPO_ROOT
    / "projects"
    / "bfp_real_board_hfss"
    / "layouts"
    / "candidates"
    / "s11_6g_tune_r1"
    / "bfp_real_board_s11_6g_tune_r1_layout.json"
)


def _load_layout(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"layout JSON must be an object: {path}")
    return data


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _shape_to_object(shape: dict[str, Any]) -> Rect | Polygon | Via | Boundary | None:
    kind = str(shape.get("kind") or "")
    metadata = dict(shape.get("metadata") if isinstance(shape.get("metadata"), dict) else {})
    if kind == "boundary":
        return Boundary(
            name=str(shape.get("name") or "boundary"),
            x=float(shape["x"]),
            y=float(shape["y"]),
            w=float(shape["w"]),
            h=float(shape["h"]),
            layer=str(shape.get("layer") or "EM_BOUNDARY"),
            metadata=metadata,
        )
    if kind == "via":
        return Via(
            name=str(shape.get("name") or "via"),
            layer=str(shape.get("layer") or "pcvia1"),
            x=float(shape["x"]),
            y=float(shape["y"]),
            diameter=float(shape["diameter"]),
            pad_diameter=float(shape["pad_diameter"]) if shape.get("pad_diameter") not in (None, "") else None,
            pad_layer=str(shape.get("pad_layer")) if shape.get("pad_layer") else None,
            metadata=metadata,
        )
    if all(key in shape for key in ("x", "y", "w", "h")):
        return Rect(
            name=str(shape.get("name") or kind or "rect"),
            layer=str(shape.get("layer") or "cond"),
            x=float(shape["x"]),
            y=float(shape["y"]),
            w=float(shape["w"]),
            h=float(shape["h"]),
            kind=kind if kind else "rect",
            metadata=metadata,
        )
    if isinstance(shape.get("points"), list):
        return Polygon(
            name=str(shape.get("name") or kind or "polygon"),
            layer=str(shape.get("layer") or "cond"),
            points=[(float(point[0]), float(point[1])) for point in shape["points"]],
            kind=kind if kind else "polygon",
            metadata=metadata,
        )
    return None


def _layout_to_object(data: dict[str, Any]) -> Layout:
    layers = [
        LayerMap(
            name=str(layer.get("name")),
            purpose=str(layer.get("purpose") or "drawing"),
            dxf_layer=str(layer.get("dxf_layer")) if layer.get("dxf_layer") else None,
        )
        for layer in data.get("layers", [])
        if isinstance(layer, dict) and layer.get("name")
    ]
    shapes = [
        shape_obj
        for shape in data.get("shapes", [])
        if isinstance(shape, dict)
        for shape_obj in [_shape_to_object(shape)]
        if shape_obj is not None
    ]
    return Layout(
        layout_id=str(data.get("layout_id") or "bfp_real_board_s11_6g_tune_r1"),
        units=str(data.get("units") or "mm"),
        layers=layers,
        shapes=shapes,
        metadata=dict(data.get("metadata") if isinstance(data.get("metadata"), dict) else {}),
    )


def _unique_breaks(values: list[float], *, tol: float = 1e-9) -> list[float]:
    output: list[float] = []
    for value in sorted(values):
        if not output or abs(value - output[-1]) > tol:
            output.append(value)
    return output


def _merge_intervals(intervals: list[tuple[float, float]]) -> list[tuple[float, float]]:
    merged: list[tuple[float, float]] = []
    for x0, x1 in sorted(intervals):
        if not merged or x0 > merged[-1][1] + 1e-9:
            merged.append((x0, x1))
            continue
        merged[-1] = (merged[-1][0], max(merged[-1][1], x1))
    return merged


def _clip_rect(
    rect: tuple[float, float, float, float],
    base: tuple[float, float, float, float],
    *,
    min_feature_mm: float,
) -> tuple[float, float, float, float] | None:
    x0, y0, x1, y1 = rect
    bx0, by0, bx1, by1 = base
    clipped = max(x0, bx0), max(y0, by0), min(x1, bx1), min(y1, by1)
    cx0, cy0, cx1, cy1 = clipped
    if cx1 - cx0 < min_feature_mm or cy1 - cy0 < min_feature_mm:
        return None
    return clipped


def _rect_shape(
    *,
    name: str,
    layer: str,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    kind: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
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


def _ground_plane_parts(
    *,
    base_name: str,
    base: tuple[float, float, float, float],
    cutouts: list[tuple[float, float, float, float]],
    target_layer: str,
    min_feature_mm: float,
) -> list[dict[str, Any]]:
    bx0, by0, bx1, by1 = base
    clipped = [
        clipped
        for cutout in cutouts
        for clipped in [_clip_rect(cutout, base, min_feature_mm=min_feature_mm)]
        if clipped is not None
    ]
    if not clipped:
        return [
            _rect_shape(
                name=base_name,
                layer="reference_ground_plane",
                x0=bx0,
                y0=by0,
                x1=bx1,
                y1=by1,
                kind="reference_ground_plane",
                metadata={"role": "solid_reference_ground", "target_layer": target_layer},
            )
        ]

    xs = _unique_breaks([bx0, bx1, *(value for x0, _, x1, _ in clipped for value in (x0, x1))])
    ys = _unique_breaks([by0, by1, *(value for _, y0, _, y1 in clipped for value in (y0, y1))])
    specs: list[tuple[float, float, float, float]] = []
    for y0, y1 in zip(ys, ys[1:], strict=False):
        if y1 - y0 < min_feature_mm:
            continue
        intervals: list[tuple[float, float]] = []
        cy = (y0 + y1) / 2.0
        for x0, x1 in zip(xs, xs[1:], strict=False):
            cx = (x0 + x1) / 2.0
            if any(vx0 < cx < vx1 and vy0 < cy < vy1 for vx0, vy0, vx1, vy1 in clipped):
                continue
            intervals.append((x0, x1))
        for x0, x1 in _merge_intervals(intervals):
            if x1 - x0 >= min_feature_mm:
                specs.append((x0, y0, x1, y1))

    output: list[dict[str, Any]] = []
    for index, (x0, y0, x1, y1) in enumerate(specs):
        name = base_name if index == 0 else f"{base_name}_part_{index}"
        output.append(
            _rect_shape(
                name=name,
                layer="reference_ground_plane",
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
                kind="reference_ground_plane",
                metadata={
                    "role": "solid_reference_ground",
                    "target_layer": target_layer,
                    "candidate_source": "s11_6g_tune_r1",
                    "cutout_materialized": True,
                },
            )
        )
    return output


def _feed_center_y(layout: dict[str, Any]) -> float:
    spans: list[tuple[float, float]] = []
    for shape in layout.get("shapes", []):
        if not isinstance(shape, dict):
            continue
        metadata = shape.get("metadata")
        if not isinstance(metadata, dict) or metadata.get("role") != "signal_feed":
            continue
        points = shape.get("points")
        if not isinstance(points, list) or not points:
            continue
        ys = [float(point[1]) for point in points]
        spans.append((min(ys), max(ys)))
    if not spans:
        metadata = layout.get("metadata") if isinstance(layout.get("metadata"), dict) else {}
        bbox = metadata.get("board_bbox_mm")
        if isinstance(bbox, list) and len(bbox) == 4:
            return (float(bbox[1]) + float(bbox[3])) / 2.0
        raise ValueError("cannot infer feed center y from signal_feed shapes or board bbox")
    return sum((y0 + y1) / 2.0 for y0, y1 in spans) / len(spans)


def _board_bbox(layout: dict[str, Any]) -> tuple[float, float, float, float]:
    metadata = layout.get("metadata") if isinstance(layout.get("metadata"), dict) else {}
    bbox = metadata.get("board_bbox_mm")
    if isinstance(bbox, list) and len(bbox) == 4:
        return float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
    boundary = next((shape for shape in layout.get("shapes", []) if isinstance(shape, dict) and shape.get("kind") == "boundary"), None)
    if boundary is None:
        raise ValueError("layout is missing metadata.board_bbox_mm and boundary shape")
    x0 = float(boundary["x"])
    y0 = float(boundary["y"])
    return x0, y0, x0 + float(boundary["w"]), y0 + float(boundary["h"])


def _reference_target_layer(shape: dict[str, Any]) -> str | None:
    metadata = shape.get("metadata")
    if not isinstance(metadata, dict):
        return None
    return str(metadata.get("target_layer") or metadata.get("source_layer") or "")


def _cutout_shapes(
    *,
    cutouts_by_side: dict[str, tuple[float, float, float, float]],
    target_layer: str,
    layer_token: str,
) -> list[dict[str, Any]]:
    shapes: list[dict[str, Any]] = []
    for side, (x0, y0, x1, y1) in cutouts_by_side.items():
        shapes.append(
            _rect_shape(
                name=f"{side.lower()}_{layer_token}_s11_6g_tune_r1_cutout_rect",
                layer="reference_ground_cutout",
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
                kind="reference_ground_cutout",
                metadata={
                    "role": "reference_ground_cutout",
                    "target_layer": target_layer,
                    "side": side,
                    "candidate_source": "s11_6g_tune_r1",
                },
            )
        )
    return shapes


def build_candidate_layout(
    layout: dict[str, Any],
    *,
    candidate_id: str,
    cutout_w_mm: float,
    cutout_l_mm: float,
    min_feature_mm: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    bx0, by0, bx1, by1 = _board_bbox(layout)
    feed_y = _feed_center_y(layout)
    half_w = cutout_w_mm / 2.0
    cutouts_by_side = {
        "P1": (bx0, feed_y - half_w, bx0 + cutout_l_mm, feed_y + half_w),
        "P2": (bx1 - cutout_l_mm, feed_y - half_w, bx1, feed_y + half_w),
    }
    cutout_rects = list(cutouts_by_side.values())
    replacement_layers = {"INNER1": "l2", "INNER2": "l3"}
    replacement: dict[str, list[dict[str, Any]]] = {}
    for target_layer, layer_token in replacement_layers.items():
        replacement[target_layer] = [
            *_cutout_shapes(cutouts_by_side=cutouts_by_side, target_layer=target_layer, layer_token=layer_token),
            *_ground_plane_parts(
                base_name=f"{candidate_id}_{target_layer.lower()}_ground_plane",
                base=(bx0, by0, bx1, by1),
                cutouts=cutout_rects,
                target_layer=target_layer,
                min_feature_mm=min_feature_mm,
            ),
        ]

    new_shapes: list[dict[str, Any]] = []
    replaced_layers: set[str] = set()
    removed_reference_planes: list[str] = []
    for shape in layout.get("shapes", []):
        if not isinstance(shape, dict):
            continue
        if shape.get("kind") == "reference_ground_plane":
            target_layer = _reference_target_layer(shape)
            if target_layer in replacement:
                removed_reference_planes.append(str(shape.get("name")))
                if target_layer not in replaced_layers:
                    new_shapes.extend(replacement[target_layer])
                    replaced_layers.add(target_layer)
                continue
        new_shapes.append(shape)
    for target_layer, shapes in replacement.items():
        if target_layer not in replaced_layers:
            new_shapes.extend(shapes)

    candidate = dict(layout)
    candidate["layout_id"] = "bfp_real_board_s11_6g_tune_r1"
    candidate["shapes"] = new_shapes
    metadata = dict(layout.get("metadata") if isinstance(layout.get("metadata"), dict) else {})
    metadata.update(
        {
            "candidate_id": candidate_id,
            "source_layout_id": layout.get("layout_id"),
            "optimization_goal": "improve 6 GHz S11/S22 by reducing launch capacitance on INNER1/INNER2",
            "generator": {
                "tool": "tools/hfss/generate_bfp_real_board_s11_6g_candidate_layout.py",
                "cutout_w_mm": cutout_w_mm,
                "cutout_l_mm": cutout_l_mm,
                "feed_center_y_mm": feed_y,
                "cutout_layers": sorted(replacement_layers),
                "ground_plane_policy": "replace INNER1/INNER2 solid planes with materialized split rectangles",
            },
            "launch_relief_cutouts_mm": {
                side: {"x0": x0, "y0": y0, "x1": x1, "y1": y1}
                for side, (x0, y0, x1, y1) in cutouts_by_side.items()
            },
        }
    )
    candidate["metadata"] = metadata
    summary = {
        "candidate_id": candidate_id,
        "source_layout": layout.get("layout_id"),
        "board_bbox_mm": [bx0, by0, bx1, by1],
        "feed_center_y_mm": feed_y,
        "cutout_w_mm": cutout_w_mm,
        "cutout_l_mm": cutout_l_mm,
        "cutouts_by_side_mm": metadata["launch_relief_cutouts_mm"],
        "removed_reference_planes": removed_reference_planes,
        "shape_count_before": len(layout.get("shapes", [])),
        "shape_count_after": len(new_shapes),
    }
    return candidate, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate BFP 6 GHz S11 tuning candidate layout JSON.")
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary-out", type=Path, default=None)
    parser.add_argument("--svg-out", type=Path, default=None)
    parser.add_argument("--no-svg", action="store_true")
    parser.add_argument("--candidate-id", default="s11_6g_tune_r1")
    parser.add_argument("--cutout-w-mm", type=float, default=2.0)
    parser.add_argument("--cutout-l-mm", type=float, default=6.0)
    parser.add_argument("--min-feature-mm", type=float, default=0.1524)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    layout = _load_layout(args.baseline)
    candidate, summary = build_candidate_layout(
        layout,
        candidate_id=args.candidate_id,
        cutout_w_mm=args.cutout_w_mm,
        cutout_l_mm=args.cutout_l_mm,
        min_feature_mm=args.min_feature_mm,
    )
    _write_json(args.out, candidate)
    summary_out = args.summary_out or args.out.with_name(args.out.stem.removesuffix("_layout") + "_summary.json")
    _write_json(summary_out, summary)
    svg_out = None
    if not args.no_svg:
        svg_out = args.svg_out or args.out.with_suffix(".svg")
        write_svg(svg_out, _layout_to_object(candidate), title="BFP s11_6g_tune_r1 layout")
    print(
        json.dumps(
            {"layout": str(args.out), "summary": str(summary_out), "svg": str(svg_out) if svg_out else None, **summary},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
