#!/usr/bin/env python3
"""Render an MCFIL *_dxf_summary.json file as layout JSON and SVG."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from simads.exporters.svg import write_svg
from simads.geometry import Boundary, LayerMap, Layout, Port, Rect, to_dict


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON must contain an object: {path}")
    return data


def rects_from_summary(summary: dict[str, Any], metal_layer: str) -> list[dict[str, Any]]:
    rects: list[dict[str, Any]] = []
    for section in summary.get("coupled_sections", []):
        if not isinstance(section, dict):
            continue
        for strip in section.get("strips", []):
            if not isinstance(strip, dict):
                continue
            rects.append(
                {
                    "source_entity": int(strip["source_entity"]),
                    "x0": float(strip["x0_mm"]),
                    "y0": float(strip["y0_mm"]),
                    "x1": float(strip["x1_mm"]),
                    "y1": float(strip["y1_mm"]),
                    "layer": metal_layer,
                }
            )
    return rects


def build_layout(summary: dict[str, Any], *, metal_layer: str, boundary_layer: str) -> Layout:
    layout_id = str(summary["layout_id"])
    x0, y0, x1, y1 = [float(value) for value in summary["bbox_mm"]]
    margin = 0.6
    boundary = Boundary(
        name="em_boundary",
        x=x0 - margin,
        y=y0 - margin,
        w=(x1 - x0) + 2.0 * margin,
        h=(y1 - y0) + 2.0 * margin,
        layer=boundary_layer,
        metadata={"role": "hfss_airbox_review_boundary", "source": str(summary.get("source_params") or summary.get("source_dxf") or "")},
    )

    rects = rects_from_summary(summary, metal_layer)
    if not rects:
        raise ValueError("summary has no coupled-section strips to render")
    p1_entity = 2
    p2_entity = 9
    right_rect = next((rect for rect in rects if rect["source_entity"] == p1_entity), max(rects, key=lambda rect: rect["x1"]))
    left_rect = next((rect for rect in rects if rect["source_entity"] == p2_entity), min(rects, key=lambda rect: rect["x0"]))

    shapes: list[Any] = [boundary]
    for index, rect in enumerate(sorted(rects, key=lambda item: (-item["x1"], item["y0"])), start=1):
        source_entity = rect["source_entity"]
        name = f"mcfil_s{index:02d}_strip"
        role = "mcfil_coupled_strip"
        if source_entity == p1_entity:
            name = "input_feed"
            role = "mcfil_candidate_input_feed"
        elif source_entity == p2_entity:
            name = "output_feed"
            role = "mcfil_candidate_output_feed"
        shapes.append(
            Rect(
                name=name,
                layer=metal_layer,
                x=rect["x0"],
                y=rect["y0"],
                w=rect["x1"] - rect["x0"],
                h=rect["y1"] - rect["y0"],
                metadata={"role": role, "source_dxf_entity": source_entity, "net": "RF"},
            )
        )

    ports = [
        Port(
            name="P1",
            number=1,
            x=right_rect["x1"],
            y=(right_rect["y0"] + right_rect["y1"]) / 2.0,
            width=right_rect["y1"] - right_rect["y0"],
            layer=metal_layer,
            orientation_deg=0.0,
            reference="ETCH_INNER1",
            metadata={"role": "candidate_port", "edge": "right", "source_dxf_entity": p1_entity},
        ),
        Port(
            name="P2",
            number=2,
            x=left_rect["x0"],
            y=(left_rect["y0"] + left_rect["y1"]) / 2.0,
            width=left_rect["y1"] - left_rect["y0"],
            layer=metal_layer,
            orientation_deg=180.0,
            reference="ETCH_INNER1",
            metadata={"role": "candidate_port", "edge": "left", "source_dxf_entity": p2_entity},
        ),
    ]
    return Layout(
        layout_id=layout_id,
        units="mm",
        layers=[
            LayerMap(name=metal_layer, purpose="drawing", dxf_layer="cond"),
            LayerMap(name=boundary_layer, purpose="drawing", dxf_layer=boundary_layer),
        ],
        shapes=shapes,
        ports=ports,
        metadata={
            "source": "MCFIL parameterized dxf_summary",
            "topology": "mcfil_coupled_line_bpf",
            "candidate_id": layout_id,
            "signal_layer": "ETCH_TOP",
            "reference_ground_layer": "ETCH_INNER1",
        },
    )


def add_footprint_dimensions(svg_path: Path, summary: dict[str, Any]) -> None:
    text = svg_path.read_text(encoding="utf-8")
    metal_rects = []
    for match in re.finditer(r'<rect x="([^"]+)" y="([^"]+)" width="([^"]+)" height="([^"]+)" fill="#2563eb"', text):
        x = float(match.group(1))
        y = float(match.group(2))
        w = float(match.group(3))
        h = float(match.group(4))
        metal_rects.append((x, y, x + w, y + h))
    if not metal_rects:
        return

    viewbox_match = re.search(r'viewBox="0 0 ([^"]+) ([^"]+)"', text)
    if not viewbox_match:
        return
    view_w = float(viewbox_match.group(1))
    view_h = float(viewbox_match.group(2))
    min_x = min(item[0] for item in metal_rects)
    min_y = min(item[1] for item in metal_rects)
    max_x = max(item[2] for item in metal_rects)
    max_y = max(item[3] for item in metal_rects)

    size = summary.get("size_mm", {})
    length_mm = float(size.get("x", summary["bbox_mm"][2] - summary["bbox_mm"][0]))
    width_mm = float(size.get("y", summary["bbox_mm"][3] - summary["bbox_mm"][1]))

    dim_y = min(view_h - 54.0, max_y + 42.0)
    dim_x = min(view_w - 54.0, max_x + 46.0)
    label_y = min(view_h - 18.0, dim_y + 25.0)
    mid_x = (min_x + max_x) / 2.0
    mid_y = (min_y + max_y) / 2.0

    defs = """  <defs>
    <marker id="dimArrow" markerWidth="9" markerHeight="9" refX="4.5" refY="4.5" orient="auto-start-reverse">
      <path d="M0,0 L9,4.5 L0,9 Z" fill="#0f172a"/>
    </marker>
  </defs>
"""
    group = f"""  <g id="footprint-dimensions" font-family="Arial, 'Microsoft YaHei', sans-serif" fill="#0f172a" stroke="#0f172a">
    <rect x="{min_x:.3f}" y="{min_y:.3f}" width="{(max_x - min_x):.3f}" height="{(max_y - min_y):.3f}" fill="none" stroke="#0f172a" stroke-width="1.2" stroke-dasharray="7 5" opacity="0.62"/>
    <line x1="{min_x:.3f}" y1="{max_y:.3f}" x2="{min_x:.3f}" y2="{dim_y:.3f}" stroke-width="1.2"/>
    <line x1="{max_x:.3f}" y1="{max_y:.3f}" x2="{max_x:.3f}" y2="{dim_y:.3f}" stroke-width="1.2"/>
    <line x1="{min_x:.3f}" y1="{dim_y:.3f}" x2="{max_x:.3f}" y2="{dim_y:.3f}" stroke-width="1.8" marker-start="url(#dimArrow)" marker-end="url(#dimArrow)"/>
    <text x="{mid_x:.3f}" y="{label_y:.3f}" text-anchor="middle" font-size="20" font-weight="700">L = {length_mm:.3f} mm</text>
    <line x1="{max_x:.3f}" y1="{min_y:.3f}" x2="{dim_x:.3f}" y2="{min_y:.3f}" stroke-width="1.2"/>
    <line x1="{max_x:.3f}" y1="{max_y:.3f}" x2="{dim_x:.3f}" y2="{max_y:.3f}" stroke-width="1.2"/>
    <line x1="{dim_x:.3f}" y1="{min_y:.3f}" x2="{dim_x:.3f}" y2="{max_y:.3f}" stroke-width="1.8" marker-start="url(#dimArrow)" marker-end="url(#dimArrow)"/>
    <text x="{(dim_x + 31.0):.3f}" y="{mid_y:.3f}" text-anchor="middle" font-size="20" font-weight="700" transform="rotate(-90 {(dim_x + 31.0):.3f} {mid_y:.3f})">W = {width_mm:.3f} mm</text>
  </g>
"""
    text = text.replace("<svg ", "<svg ", 1)
    if "<defs>" not in text:
        text = text.replace(">\n", ">\n" + defs, 1)
    text = text.replace("</svg>", group + "</svg>")
    svg_path.write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render an MCFIL dxf summary as review SVG.")
    parser.add_argument("summary", type=Path)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--metal-layer", default="cond")
    parser.add_argument("--boundary-layer", default="EM_BOUNDARY")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary_path = args.summary.resolve()
    summary = load_json(summary_path)
    layout = build_layout(summary, metal_layer=args.metal_layer, boundary_layer=args.boundary_layer)
    out_dir = (args.out_dir or summary_path.parent).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    layout_path = out_dir / f"{layout.layout_id}_layout.json"
    svg_path = out_dir / f"{layout.layout_id}_review.svg"
    layout_path.write_text(json.dumps(to_dict(layout), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_svg(svg_path, layout, title=f"{layout.layout_id} parameterized layout", padding=0.4)
    add_footprint_dimensions(svg_path, summary)
    print(json.dumps({"layout_json": str(layout_path), "svg": str(svg_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
