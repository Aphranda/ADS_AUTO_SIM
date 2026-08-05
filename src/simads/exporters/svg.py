"""SVG exporter for quick layout review images."""

from __future__ import annotations

from html import escape
from pathlib import Path as FsPath

from simads.geometry import Boundary, Layout, Path, Polygon, Rect, Shape, Via, bounds, fmt


DEFAULT_LAYER_COLORS = {
    "cond": "#2563eb",
    "pcvia1": "#f97316",
    "EM_BOUNDARY": "#64748b",
    "reference_ground_cutout": "#ef4444",
    "reference_ground_plane": "#22c55e",
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


def _shape_svg_at(
    shape: Shape,
    *,
    scale: float,
    min_x: float,
    max_y: float,
    y_offset: float,
    layer_colors: dict[str, str] | None,
    fill_override: str | None = None,
    stroke_override: str | None = None,
    opacity: float | None = None,
    fill: bool = True,
) -> str:
    color = fill_override or _color(getattr(shape, "layer", ""), layer_colors)
    stroke = stroke_override or color
    alpha = 0.82 if opacity is None else opacity

    def sx(x: float) -> float:
        return (x - min_x) * scale

    def sy(y: float) -> float:
        return y_offset + (max_y - y) * scale

    if isinstance(shape, Rect):
        fill_attr = color if fill else "none"
        stroke_attr = stroke if (stroke_override is not None or not fill) else "none"
        return (
            f'<rect x="{fmt(sx(shape.x))}" y="{fmt(sy(shape.y + shape.h))}" '
            f'width="{fmt(shape.w * scale)}" height="{fmt(shape.h * scale)}" '
            f'fill="{fill_attr}" stroke="{stroke_attr}" stroke-width="1" opacity="{fmt(alpha)}"><title>{escape(shape.name)}</title></rect>'
        )
    if isinstance(shape, Boundary):
        if fill_override is not None:
            return (
                f'<rect x="{fmt(sx(shape.x))}" y="{fmt(sy(shape.y + shape.h))}" '
                f'width="{fmt(shape.w * scale)}" height="{fmt(shape.h * scale)}" '
                f'fill="{color}" stroke="{stroke}" stroke-width="1" opacity="{fmt(alpha)}"><title>{escape(shape.name)}</title></rect>'
            )
        return (
            f'<rect x="{fmt(sx(shape.x))}" y="{fmt(sy(shape.y + shape.h))}" '
            f'width="{fmt(shape.w * scale)}" height="{fmt(shape.h * scale)}" '
            f'fill="none" stroke="{color}" stroke-width="1"><title>{escape(shape.name)}</title></rect>'
        )
    if isinstance(shape, Polygon):
        fill_attr = color if fill else "none"
        stroke_attr = stroke if (stroke_override is not None or not fill) else "none"
        points = " ".join(f"{fmt(sx(x))},{fmt(sy(y))}" for x, y in shape.points)
        return f'<polygon points="{points}" fill="{fill_attr}" stroke="{stroke_attr}" stroke-width="1" opacity="{fmt(alpha)}"><title>{escape(shape.name)}</title></polygon>'
    if isinstance(shape, Via):
        parts: list[str] = []
        if shape.pad_diameter:
            parts.append(
                f'<circle cx="{fmt(sx(shape.x))}" cy="{fmt(sy(shape.y))}" r="{fmt(shape.pad_diameter / 2.0 * scale)}" '
                f'fill="{color}" opacity="{fmt(alpha * 0.55)}"><title>{escape(shape.name)} pad</title></circle>'
            )
        parts.append(
            f'<circle cx="{fmt(sx(shape.x))}" cy="{fmt(sy(shape.y))}" r="{fmt(shape.radius * scale)}" '
            f'fill="{color}" opacity="{fmt(alpha)}"><title>{escape(shape.name)}</title></circle>'
        )
        return "\n  ".join(parts)
    if isinstance(shape, Path):
        points = " ".join(f"{fmt(sx(x))},{fmt(sy(y))}" for x, y in shape.points)
        return (
            f'<polyline points="{points}" fill="none" stroke="{color}" '
            f'stroke-width="{fmt(shape.width * scale)}" stroke-linecap="round" stroke-linejoin="round">'
            f"<title>{escape(shape.name)}</title></polyline>"
        )
    return _shape_svg(shape, scale=scale, min_x=min_x, max_y=max_y, layer_colors=layer_colors)


def _is_connector_layer_review(layout: Layout) -> bool:
    metadata = layout.metadata or {}
    return metadata.get("generator") == "simads.hfss.connector" and bool(metadata.get("reference_ground_layer"))


def _write_connector_layer_review_svg(
    path: FsPath,
    layout: Layout,
    *,
    title: str | None,
    layer_colors: dict[str, str] | None,
    padding: float,
    width_px: int,
) -> None:
    min_x, min_y, max_x, max_y = bounds(layout.shapes)
    width = max_x - min_x + 2.0 * padding
    panel_h = max_y - min_y + 2.0 * padding
    scale = width_px / width if width > 0 else 1.0
    panel_h_px = panel_h * scale
    gap_px = 56.0
    title_h_px = 36.0
    l3_shapes = [shape for shape in layout.shapes if getattr(shape, "kind", "") == "reference_ground_plane"]
    panel_count = 3 if l3_shapes else 2
    height_px = title_h_px + panel_count * panel_h_px + (panel_count - 1) * gap_px
    view_min_x = min_x - padding
    view_max_y = max_y + padding
    boundary = next((shape for shape in layout.shapes if isinstance(shape, Boundary)), None)
    l1_shapes = [
        shape
        for shape in layout.shapes
        if isinstance(shape, (Boundary, Via)) or getattr(shape, "layer", "") in {"cond", str(layout.metadata.get("signal_layer", ""))}
    ]
    l2_cutouts = [shape for shape in layout.shapes if getattr(shape, "kind", "") == "reference_ground_cutout"]
    l2_y = title_h_px + panel_h_px + gap_px
    l1_body = "\n  ".join(
        _shape_svg_at(shape, scale=scale, min_x=view_min_x, max_y=view_max_y, y_offset=title_h_px, layer_colors=layer_colors)
        for shape in l1_shapes
    )
    l2_parts: list[str] = []
    if boundary is not None:
        l2_parts.append(
            _shape_svg_at(
                boundary,
                scale=scale,
                min_x=view_min_x,
                max_y=view_max_y,
                y_offset=l2_y,
                layer_colors=layer_colors,
                fill_override="#16a34a",
                opacity=0.22,
            )
        )
    for shape in layout.shapes:
        if isinstance(shape, Via):
            l2_parts.append(
                _shape_svg_at(
                    shape,
                    scale=scale,
                    min_x=view_min_x,
                    max_y=view_max_y,
                    y_offset=l2_y,
                    layer_colors=layer_colors,
                    fill_override="#f97316",
                    opacity=0.8,
                )
            )
    for shape in l2_cutouts:
        l2_parts.append(
            _shape_svg_at(
                shape,
                scale=scale,
                min_x=view_min_x,
                max_y=view_max_y,
                y_offset=l2_y,
                layer_colors=layer_colors,
                fill_override="#ffffff",
                opacity=1.0,
            )
        )
        l2_parts.append(
            _shape_svg_at(
                shape,
                scale=scale,
                min_x=view_min_x,
                max_y=view_max_y,
                y_offset=l2_y,
                layer_colors=layer_colors,
                fill_override="#ffffff",
                stroke_override="#dc2626",
                opacity=1.0,
                fill=False,
            )
        )
    l2_body = "\n  ".join(l2_parts)
    l3_y = l2_y + panel_h_px + gap_px
    l3_parts: list[str] = []
    for shape in l3_shapes:
        l3_parts.append(
            _shape_svg_at(
                shape,
                scale=scale,
                min_x=view_min_x,
                max_y=view_max_y,
                y_offset=l3_y,
                layer_colors=layer_colors,
                fill_override="#16a34a",
                opacity=0.26,
            )
        )
    for shape in layout.shapes:
        if isinstance(shape, Via):
            l3_parts.append(
                _shape_svg_at(
                    shape,
                    scale=scale,
                    min_x=view_min_x,
                    max_y=view_max_y,
                    y_offset=l3_y,
                    layer_colors=layer_colors,
                    fill_override="#f97316",
                    opacity=0.75,
                )
            )
    l3_body = "\n  ".join(l3_parts)
    heading = escape(title or layout.layout_id)
    signal_layer = escape(str(layout.metadata.get("signal_layer") or "L1"))
    reference_layer = escape(str(layout.metadata.get("reference_ground_layer") or "L2"))
    l3_layer = escape(str(layout.metadata.get("l3_ground_layer") or "ETCH_INNER2"))
    l3_panel = (
        f'  <text x="16" y="{fmt(l3_y + 16)}" font-family="Arial, sans-serif" font-size="14" fill="#111827">L3 {l3_layer}</text>\n'
        f"  {l3_body}\n"
        if l3_shapes
        else ""
    )
    text = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width_px}" height="{fmt(height_px)}" viewBox="0 0 {width_px} {fmt(height_px)}">
  <rect x="0" y="0" width="{width_px}" height="{fmt(height_px)}" fill="#ffffff"/>
  <text x="16" y="24" font-family="Arial, sans-serif" font-size="16" fill="#111827">{heading}</text>
  <text x="16" y="{fmt(title_h_px + 16)}" font-family="Arial, sans-serif" font-size="14" fill="#111827">L1 {signal_layer}</text>
  {l1_body}
  <text x="16" y="{fmt(l2_y + 16)}" font-family="Arial, sans-serif" font-size="14" fill="#111827">L2 {reference_layer}</text>
  {l2_body}
{l3_panel.rstrip()}
</svg>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_svg(
    path: FsPath,
    layout: Layout,
    *,
    title: str | None = None,
    layer_colors: dict[str, str] | None = None,
    padding: float = 1.0,
    width_px: int = 1200,
) -> None:
    if _is_connector_layer_review(layout):
        _write_connector_layer_review_svg(
            path,
            layout,
            title=title,
            layer_colors=layer_colors,
            padding=padding,
            width_px=width_px,
        )
        return
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

