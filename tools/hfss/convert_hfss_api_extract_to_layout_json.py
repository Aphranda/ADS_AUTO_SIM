#!/usr/bin/env python3
"""Convert an AEDT API layout extract into editable SIM layout JSON.

The input is produced by tools/hfss/extract_hfss3dlayout_parameterized_layout.py.
This converter is offline; it does not read or write AEDT project files.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

_SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.common import json_default, read_json_object


def _clean_points(value: Any) -> list[list[float]]:
    points: list[list[float]] = []
    if not isinstance(value, list):
        return points
    for point in value:
        if not isinstance(point, list) or len(point) < 2:
            continue
        try:
            points.append([float(point[0]), float(point[1])])
        except (TypeError, ValueError):
            continue
    return points


def _bbox(value: Any) -> list[float] | None:
    if not isinstance(value, list) or len(value) < 4:
        return None
    try:
        x0, y0, x1, y1 = [float(item) for item in value[:4]]
    except (TypeError, ValueError):
        return None
    if x1 < x0:
        x0, x1 = x1, x0
    if y1 < y0:
        y0, y1 = y1, y0
    return [x0, y0, x1, y1]


def _bbox_from_points(points: list[list[float]]) -> list[float] | None:
    if not points:
        return None
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return [min(xs), min(ys), max(xs), max(ys)]


def _merge_bboxes(values: list[list[float] | None]) -> list[float] | None:
    boxes = [value for value in values if value is not None]
    if not boxes:
        return None
    return [
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    ]


def _bbox_size(box: list[float] | None) -> dict[str, float] | None:
    if box is None:
        return None
    return {"w_mm": box[2] - box[0], "h_mm": box[3] - box[1]}


def _center(box: list[float]) -> tuple[float, float]:
    return (box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0


def _classify_top_poly(box: list[float]) -> str:
    cx, cy = _center(box)
    w = box[2] - box[0]
    h = box[3] - box[1]
    in_core_x = 91.4 <= cx <= 95.5
    in_core_y = 86.8 <= cy <= 93.6
    thin_horizontal_feed = h <= 0.6 and w >= 2.0 and 88.6 <= cy <= 89.6
    if in_core_x and in_core_y:
        return "signal_filter_core"
    if thin_horizontal_feed:
        return "signal_feed"
    return "ground_copper"


def _parse_mm_from_property(text: Any, *, fallback: float) -> float:
    if text is None:
        return fallback
    raw = str(text).strip().lower()
    if not raw:
        return fallback
    try:
        if raw.endswith("mil"):
            return float(raw[:-3].strip()) * 0.0254
        if raw.endswith("mm"):
            return float(raw[:-2].strip())
        return float(raw)
    except ValueError:
        return fallback


def convert(payload: dict[str, Any], *, layout_id: str, via_pad_diameter_mm: float) -> dict[str, Any]:
    objects = [item for item in payload.get("objects", []) if isinstance(item, dict)]
    top_polys: list[dict[str, Any]] = []
    reference_planes: list[dict[str, Any]] = []
    outline_box: list[float] | None = None
    via_by_name: dict[str, dict[str, Any]] = {}

    for obj in objects:
        layer = str(obj.get("layer") or "")
        obj_type = str(obj.get("type") or "").lower()
        points = _clean_points(obj.get("points_mm"))
        box = _bbox(obj.get("bbox_mm")) or _bbox_from_points(points)
        name = str(obj.get("name") or f"{obj_type}_{len(top_polys)}")

        if layer == "TOP" and obj_type == "poly" and points and box is not None:
            role = _classify_top_poly(box)
            net = "RF" if role.startswith("signal_") else "GND"
            top_polys.append(
                {
                    "name": name,
                    "layer": "cond",
                    "points": points,
                    "kind": "polygon",
                    "metadata": {
                        "source_layer": layer,
                        "source_name": name,
                        "role": role,
                        "net": net,
                    },
                }
            )
        elif layer in {"INNER1", "INNER2", "BOTTOM"} and obj_type == "poly" and points and box is not None:
            if (box[2] - box[0]) >= 20.0 and (box[3] - box[1]) >= 10.0:
                reference_planes.append(
                    {
                        "name": f"{name}_{layer.lower()}",
                        "layer": "reference_ground_plane",
                        "points": points,
                        "kind": "reference_ground_plane",
                        "metadata": {
                            "source_layer": layer,
                            "source_name": name,
                            "target_layer": layer,
                            "net": "GND",
                            "role": "solid_reference_ground",
                        },
                    }
                )
        elif layer == "Outline" and obj_type in {"poly", "circle"} and box is not None:
            outline_box = _merge_bboxes([outline_box, box])
        elif obj_type == "via":
            loc = obj.get("location_mm") or obj.get("center_mm")
            if not isinstance(loc, list) or len(loc) < 2:
                continue
            try:
                x = float(loc[0])
                y = float(loc[1])
            except (TypeError, ValueError):
                continue
            props = obj.get("properties") if isinstance(obj.get("properties"), dict) else {}
            hole = _parse_mm_from_property(props.get("HoleDiameter"), fallback=0.3048)
            via_by_name.setdefault(
                name,
                {
                    "name": name,
                    "x": x,
                    "y": y,
                    "diameter": hole,
                    "pad_diameter": max(via_pad_diameter_mm, hole),
                    "layer": "pcvia1",
                    "kind": "via",
                    "metadata": {
                        "source_name": name,
                        "source_layer": layer,
                        "net": "GND",
                        "role": "ground_via",
                    },
                },
            )

    top_box = _merge_bboxes([_bbox_from_points(shape.get("points", [])) for shape in top_polys])
    board_box = outline_box or top_box
    shapes: list[dict[str, Any]] = []
    if board_box is not None:
        shapes.append(
            {
                "name": "em_boundary",
                "x": board_box[0],
                "y": board_box[1],
                "w": board_box[2] - board_box[0],
                "h": board_box[3] - board_box[1],
                "layer": "EM_BOUNDARY",
                "kind": "boundary",
                "metadata": {"source": "outline_bbox"},
            }
        )
    shapes.extend(top_polys)
    shapes.extend(reference_planes)
    shapes.extend(sorted(via_by_name.values(), key=lambda item: item["name"]))

    return {
        "layout_id": layout_id,
        "units": "mm",
        "layers": [
            {"name": "cond", "purpose": "drawing", "dxf_layer": "cond"},
            {"name": "pcvia1", "purpose": "drawing", "dxf_layer": "pcvia1"},
            {"name": "EM_BOUNDARY", "purpose": "drawing", "dxf_layer": "EM_BOUNDARY"},
            {
                "name": "reference_ground_plane",
                "purpose": "drawing",
                "dxf_layer": "reference_ground_plane",
            },
        ],
        "shapes": shapes,
        "metadata": {
            "source_project": payload.get("project"),
            "source_design": payload.get("design"),
            "source_model_units": payload.get("model_units"),
            "api_contract": payload.get("api_contract"),
            "board_bbox_mm": board_box,
            "board_size_mm": _bbox_size(board_box),
            "top_copper_bbox_mm": top_box,
            "top_copper_size_mm": _bbox_size(top_box),
            "editable_regions": {
                "left_launch_bbox_mm": [78.7, 80.4, 91.8, 96.2],
                "filter_core_bbox_mm": [91.6, 87.1, 95.3, 93.4],
                "right_launch_bbox_mm": [95.1, 80.4, 108.3, 96.2],
            },
            "classification_note": "TOP net names from AEDT API were all GND, so RF/feed roles are classified by geometry.",
            "shape_counts": {
                "top_polygons": len(top_polys),
                "reference_planes": len(reference_planes),
                "unique_vias": len(via_by_name),
            },
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert AEDT API extract JSON to editable SIM layout JSON.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--layout-id", default="bfp_real_board_extracted_baseline")
    parser.add_argument("--via-pad-diameter-mm", type=float, default=0.55)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = read_json_object(args.input)
    layout = convert(payload, layout_id=args.layout_id, via_pad_diameter_mm=args.via_pad_diameter_mm)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(layout, ensure_ascii=False, indent=2, default=json_default) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
