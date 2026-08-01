"""SVG exporter for quick layout review images."""

from __future__ import annotations

from html import escape
from pathlib import Path as FsPath

from simads.geometry import Boundary, Layout, Path, Polygon, Rect, Shape, Via, bounds, fmt


DEFAULT_LAYER_COLORS = {
    "cond": "#7c3aed",
    "pcvia1": "#f97316",
    "EM_BOUNDARY": "#64748b",
}


def _color(layer: str, layer_colors: dict[str, str] | None) -> str:
    return (layer_colors or {}).get(layer) or DEFAULT_LAYER_COLORS.get(layer, "#334155")


def _shape_svg(shape: Shape, *, scale: float, min_x: float, max_y: float, layer_colors: dict[str, str] | None) -> str:
    color = _color(getattr(shape, "layer", ""), layer_colors)

    def sx(x: float) -> float:
        return (x - min_x) * scale

    def sy(y: float) -> float:
        return (max_y - y) * scale

    if isinstance(shape, Rect):
        return (
            f'<rect x="{fmt(sx(shape.x))}" y="{fmt(sy(shape.y + shape.h))}" '
            f'width="{fmt(shape.w * scale)}" height="{fmt(shape.h * scale)}" '
            f'fill="{color}" opacity="0.82"><title>{escape(shape.name)}</title></rect>'
        )
    if isinstance(shape, Boundary):
        return (
            f'<rect x="{fmt(sx(shape.x))}" y="{fmt(sy(shape.y + shape.h))}" '
            f'width="{fmt(shape.w * scale)}" height="{fmt(shape.h * scale)}" '
            f'fill="none" stroke="{color}" stroke-width="1"><title>{escape(shape.name)}</title></rect>'
        )
    if isinstance(shape, Polygon):
        points = " ".join(f"{fmt(sx(x))},{fmt(sy(y))}" for x, y in shape.points)
        return f'<polygon points="{points}" fill="{color}" opacity="0.82"><title>{escape(shape.name)}</title></polygon>'
    if isinstance(shape, Path):
        points = " ".join(f"{fmt(sx(x))},{fmt(sy(y))}" for x, y in shape.points)
        return (
            f'<polyline points="{points}" fill="none" stroke="{color}" '
            f'stroke-width="{fmt(shape.width * scale)}" stroke-linecap="round" stroke-linejoin="round">'
            f"<title>{escape(shape.name)}</title></polyline>"
        )
    if isinstance(shape, Via):
        parts: list[str] = []
        if shape.pad_diameter:
            pad_color = _color(shape.pad_layer or shape.layer, layer_colors)
            parts.append(
                f'<circle cx="{fmt(sx(shape.x))}" cy="{fmt(sy(shape.y))}" r="{fmt(shape.pad_diameter / 2.0 * scale)}" '
                f'fill="{pad_color}" opacity="0.45"><title>{escape(shape.name)} pad</title></circle>'
            )
        parts.append(
            f'<circle cx="{fmt(sx(shape.x))}" cy="{fmt(sy(shape.y))}" r="{fmt(shape.radius * scale)}" '
            f'fill="{color}"><title>{escape(shape.name)}</title></circle>'
        )
        return "\n  ".join(parts)
    raise TypeError(f"unsupported SVG shape type: {type(shape)!r}")


def write_svg(
    path: FsPath,
    layout: Layout,
    *,
    title: str | None = None,
    layer_colors: dict[str, str] | None = None,
    padding: float = 1.0,
    width_px: int = 1200,
) -> None:
    min_x, min_y, max_x, max_y = bounds(layout.shapes)
    width = max_x - min_x + 2.0 * padding
    height = max_y - min_y + 2.0 * padding
    scale = width_px / width if width > 0 else 1.0
    height_px = height * scale
    view_min_x = min_x - padding
    view_max_y = max_y + padding
    body = "\n  ".join(
        _shape_svg(shape, scale=scale, min_x=view_min_x, max_y=view_max_y, layer_colors=layer_colors)
        for shape in layout.shapes
    )
    heading = escape(title or layout.layout_id)
    text = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width_px}" height="{fmt(height_px)}" viewBox="0 0 {width_px} {fmt(height_px)}">
  <rect x="0" y="0" width="{width_px}" height="{fmt(height_px)}" fill="#ffffff"/>
  {body}
  <text x="16" y="24" font-family="Arial, sans-serif" font-size="16" fill="#111827">{heading}</text>
</svg>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

