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


def _target_ground_layer_name(shape: Shape, reference_layer: str) -> str:
    metadata = getattr(shape, "metadata", None)
    if isinstance(metadata, dict):
        target = metadata.get("target_layer")
        if target and target != "reference_ground_layer":
            return str(target)
    return reference_layer


def _reference_ground_review_rect(layout: Layout, boundary: Boundary | None, reference_layer: str) -> Rect | Boundary | None:
    if boundary is None:
        return None
    ports = list(layout.ports or [])
    if len(ports) >= 2:
        left = min(float(port.x) for port in ports)
        right = max(float(port.x) for port in ports)
        if right > left:
            params = layout.metadata.get("parameters", {}) if isinstance(layout.metadata, dict) else {}
            if not isinstance(params, dict):
                params = {}
            extend_left = max(
                0.0,
                float(layout.metadata.get("reference_ground_extend_left_mm") or params.get("reference_ground_extend_left_mm") or 0.0),
            )
            extend_right = max(
                0.0,
                float(layout.metadata.get("reference_ground_extend_right_mm") or params.get("reference_ground_extend_right_mm") or 0.0),
            )
            source_left = float(boundary.x)
            source_right = float(boundary.x + boundary.w)
            left = max(source_left, left - extend_left)
            right = min(source_right, right + extend_right)
            return Rect(
                name=str(layout.metadata.get("ground_plane_name") or "hfss_ground_plane"),
                layer=reference_layer,
                x=left,
                y=boundary.y,
                w=right - left,
                h=boundary.h,
                metadata={"role": "reference_ground_plane_review", "target_layer": reference_layer, "net": "GND"},
            )
    return boundary


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
    reference_layer_name = str(layout.metadata.get("reference_ground_layer") or "L2")
    l3_layer_name = str(layout.metadata.get("l3_ground_layer") or "ETCH_INNER2")
    l4_layer_name = str(layout.metadata.get("l4_ground_layer") or "ETCH_BOTTOM")
    ground_plane_shapes = [shape for shape in layout.shapes if getattr(shape, "kind", "") == "reference_ground_plane"]
    extra_ground_layers: list[str] = []
    for preferred in (l3_layer_name, l4_layer_name):
        if preferred and any(_target_ground_layer_name(shape, reference_layer_name) == preferred for shape in ground_plane_shapes):
            extra_ground_layers.append(preferred)
    for shape in ground_plane_shapes:
        layer_name = _target_ground_layer_name(shape, reference_layer_name)
        if layer_name not in extra_ground_layers:
            extra_ground_layers.append(layer_name)
    panel_count = 2 + len(extra_ground_layers)
    height_px = title_h_px + panel_count * panel_h_px + (panel_count - 1) * gap_px
    view_min_x = min_x - padding
    view_max_y = max_y + padding
    boundary = next((shape for shape in layout.shapes if isinstance(shape, Boundary)), None)
    l2_ground = _reference_ground_review_rect(layout, boundary, reference_layer_name)
    l1_shapes = [
        shape
        for shape in layout.shapes
        if isinstance(shape, (Boundary, Via)) or getattr(shape, "layer", "") in {"cond", str(layout.metadata.get("signal_layer", ""))}
    ]
    cutouts_by_layer: dict[str, list[Shape]] = {}
    for shape in layout.shapes:
        if getattr(shape, "kind", "") == "reference_ground_cutout":
            cutouts_by_layer.setdefault(_target_ground_layer_name(shape, reference_layer_name), []).append(shape)
    l2_y = title_h_px + panel_h_px + gap_px
    l1_body = "\n  ".join(
        _shape_svg_at(shape, scale=scale, min_x=view_min_x, max_y=view_max_y, y_offset=title_h_px, layer_colors=layer_colors)
        for shape in l1_shapes
    )
    l2_parts: list[str] = []
    if l2_ground is not None:
        l2_parts.append(
            _shape_svg_at(
                l2_ground,
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
    for shape in cutouts_by_layer.get(reference_layer_name, []):
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
    heading = escape(title or layout.layout_id)
    signal_layer = escape(str(layout.metadata.get("signal_layer") or "L1"))
    reference_layer = escape(reference_layer_name)
    extra_panels: list[str] = []
    for idx, layer_name in enumerate(extra_ground_layers):
        panel_y = l2_y + (idx + 1) * (panel_h_px + gap_px)
        parts: list[str] = []
        for shape in ground_plane_shapes:
            if _target_ground_layer_name(shape, reference_layer_name) != layer_name:
                continue
            parts.append(
                _shape_svg_at(
                    shape,
                    scale=scale,
                    min_x=view_min_x,
                    max_y=view_max_y,
                    y_offset=panel_y,
                    layer_colors=layer_colors,
                    fill_override="#16a34a",
                    opacity=0.26,
                )
            )
        for shape in layout.shapes:
            if isinstance(shape, Via):
                parts.append(
                    _shape_svg_at(
                        shape,
                        scale=scale,
                        min_x=view_min_x,
                        max_y=view_max_y,
                        y_offset=panel_y,
                        layer_colors=layer_colors,
                        fill_override="#f97316",
                        opacity=0.75,
                    )
                )
        for shape in cutouts_by_layer.get(layer_name, []):
            parts.append(
                _shape_svg_at(
                    shape,
                    scale=scale,
                    min_x=view_min_x,
                    max_y=view_max_y,
                    y_offset=panel_y,
                    layer_colors=layer_colors,
                    fill_override="#ffffff",
                    opacity=1.0,
                )
            )
            parts.append(
                _shape_svg_at(
                    shape,
                    scale=scale,
                    min_x=view_min_x,
                    max_y=view_max_y,
                    y_offset=panel_y,
                    layer_colors=layer_colors,
                    fill_override="#ffffff",
                    stroke_override="#dc2626",
                    opacity=1.0,
                    fill=False,
                )
            )
        logical_name = "L3" if layer_name == l3_layer_name else "L4" if layer_name == l4_layer_name else f"GND{idx + 3}"
        body = "\n  ".join(parts)
        extra_panels.append(
            f'  <text x="16" y="{fmt(panel_y + 16)}" font-family="Arial, sans-serif" font-size="14" fill="#111827">{escape(logical_name)} {escape(layer_name)}</text>\n'
            f"  {body}"
        )
    extra_panel_text = "\n".join(extra_panels)
    text = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width_px}" height="{fmt(height_px)}" viewBox="0 0 {width_px} {fmt(height_px)}">
  <rect x="0" y="0" width="{width_px}" height="{fmt(height_px)}" fill="#ffffff"/>
  <text x="16" y="24" font-family="Arial, sans-serif" font-size="16" fill="#111827">{heading}</text>
  <text x="16" y="{fmt(title_h_px + 16)}" font-family="Arial, sans-serif" font-size="14" fill="#111827">L1 {signal_layer}</text>
  {l1_body}
  <text x="16" y="{fmt(l2_y + 16)}" font-family="Arial, sans-serif" font-size="14" fill="#111827">L2 {reference_layer}</text>
  {l2_body}
{extra_panel_text}
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

