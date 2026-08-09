#!/usr/bin/env python3
"""Render AEDT API-extracted HFSS 3D Layout geometry as SVG.

The input is the JSON produced by extract_hfss3dlayout_parameterized_layout.py.
This tool is offline by design: it does not start AEDT and does not read AEDT
project databases directly.
"""

from __future__ import annotations

import argparse
import json
import math
from html import escape
from pathlib import Path
import re
from typing import Any

import sys

_SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.common import read_json_object


DEFAULT_LAYERS = ("TOP", "L2_GND", "L3_SIG", "BOTTOM")
LAYER_ALIASES = {
    "TOP": "L1 TOP",
    "L2_GND": "L2 GND",
    "L3_SIG": "L3 SIG",
    "BOTTOM": "L4 BOTTOM",
}
LAYER_ORDER = {layer: index for index, layer in enumerate(DEFAULT_LAYERS)}
DEFAULT_LAYER_COLORS = {
    "TOP": "#d94f2b",
    "L2_GND": "#4b8f68",
    "L3_SIG": "#3b72b9",
    "BOTTOM": "#8a62c7",
}
SIGNAL_COLOR = "#f97316"
OTHER_SIGNAL_COLOR = "#2563eb"
GND_COLOR = "#5f7f69"
VOID_FILL = "#ffffff"
VOID_STROKE = "#dc2626"
PIN_COLOR = "#111827"
GRID_COLOR = "#d7dce2"
TEXT_COLOR = "#27313d"
BG_COLOR = "#fbfbf8"


def _fmt(value: float, digits: int = 3) -> str:
    text = f"{value:.{digits}f}".rstrip("0").rstrip(".")
    return text if text else "0"


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    return None


def _clean_points(points: Any) -> list[tuple[float, float]]:
    clean: list[tuple[float, float]] = []
    if not isinstance(points, list):
        return clean
    for point in points:
        if not isinstance(point, list) or len(point) < 2:
            continue
        x = _as_float(point[0])
        y = _as_float(point[1])
        if x is not None and y is not None:
            clean.append((x, y))
    return clean


def _clean_bbox(bbox: Any) -> tuple[float, float, float, float] | None:
    if not isinstance(bbox, list) or len(bbox) < 4:
        return None
    values = [_as_float(item) for item in bbox[:4]]
    if any(item is None for item in values):
        return None
    x0, y0, x1, y1 = [float(item) for item in values if item is not None]
    if x1 < x0:
        x0, x1 = x1, x0
    if y1 < y0:
        y0, y1 = y1, y0
    return x0, y0, x1, y1


_NUMBER_RE = re.compile(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")


def _parse_mil_location(value: Any) -> tuple[float, float] | None:
    if not isinstance(value, str):
        return None
    numbers = _NUMBER_RE.findall(value)
    if len(numbers) < 2:
        return None
    return float(numbers[0]) * 0.0254, float(numbers[1]) * 0.0254


def _component_info_value(component_info: Any, key: str) -> str | None:
    if not isinstance(component_info, list):
        return None
    prefix = f"{key}="
    for item in component_info:
        text = str(item)
        if text.startswith(prefix):
            return text.split("=", 1)[1]
    return None


def _component_info_bbox_mm(component_info: Any) -> tuple[float, float, float, float] | None:
    values = []
    for key in ("BBoxLLx", "BBoxLLy", "BBoxURx", "BBoxURy"):
        value = _component_info_value(component_info, key)
        if value is None:
            return None
        values.append(float(value) * 1000.0)
    x0, y0, x1, y1 = values
    if x1 < x0:
        x0, x1 = x1, x0
    if y1 < y0:
        y0, y1 = y1, y0
    return x0, y0, x1, y1


def _translated_bbox(local: tuple[float, float, float, float], origin: tuple[float, float]) -> list[float]:
    return [local[0] + origin[0], local[1] + origin[1], local[2] + origin[0], local[3] + origin[1]]


def _pin_location_mm(pin_info: Any) -> list[float] | None:
    if not isinstance(pin_info, list):
        return None
    values: dict[str, float] = {}
    for item in pin_info:
        text = str(item)
        if "=" not in text:
            continue
        key, value = text.split("=", 1)
        if key in {"X", "Y"}:
            values[key] = float(value) * 1000.0
    if "X" not in values or "Y" not in values:
        return None
    return [values["X"], values["Y"]]


def _bbox_from_points(points: list[tuple[float, float]]) -> tuple[float, float, float, float] | None:
    if not points:
        return None
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return min(xs), min(ys), max(xs), max(ys)


def _location(obj: dict[str, Any]) -> tuple[float, float] | None:
    value = obj.get("location_mm")
    if not isinstance(value, list) or len(value) < 2:
        return None
    x = _as_float(value[0])
    y = _as_float(value[1])
    if x is None or y is None:
        return None
    return x, y


def _object_bbox(obj: dict[str, Any]) -> tuple[float, float, float, float] | None:
    bbox = _clean_bbox(obj.get("bbox_mm"))
    location = _location(obj)
    if bbox is not None and not (
        bbox[0] == bbox[1] == bbox[2] == bbox[3] == 0.0
        and location is not None
        and location != (0.0, 0.0)
    ):
        return bbox
    points = _clean_points(obj.get("points_mm"))
    bbox = _bbox_from_points(points)
    if bbox is not None:
        return bbox
    if location is not None:
        x, y = location
        return x, y, x, y
    return None


def _merge_bboxes(bboxes: list[tuple[float, float, float, float]]) -> tuple[float, float, float, float] | None:
    if not bboxes:
        return None
    return (
        min(item[0] for item in bboxes),
        min(item[1] for item in bboxes),
        max(item[2] for item in bboxes),
        max(item[3] for item in bboxes),
    )


def _expand_bbox(bbox: tuple[float, float, float, float], margin: float) -> tuple[float, float, float, float]:
    return bbox[0] - margin, bbox[1] - margin, bbox[2] + margin, bbox[3] + margin


def _bbox_intersects(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    return a[0] <= b[2] and a[2] >= b[0] and a[1] <= b[3] and a[3] >= b[1]


def _signal_nets(payload: dict[str, Any], explicit: list[str] | None) -> list[str]:
    if explicit:
        return explicit
    nets = payload.get("signal_nets")
    if isinstance(nets, list) and nets:
        return [str(item) for item in nets]
    distilled = payload.get("distilled")
    if isinstance(distilled, dict):
        nets = distilled.get("signal_nets")
        if isinstance(nets, list) and nets:
            return [str(item) for item in nets]
    return []


def _layers(payload: dict[str, Any], explicit: list[str] | None) -> list[str]:
    if explicit:
        requested = explicit
    else:
        requested = []
        raw = payload.get("layers_requested")
        if isinstance(raw, list) and raw:
            requested = [str(item) for item in raw]
        else:
            requested = list(DEFAULT_LAYERS)
    return sorted(
        list(dict.fromkeys(requested)),
        key=lambda layer: (LAYER_ORDER.get(layer, 100), layer),
    )


def _component_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    editor_components = payload.get("components")
    if isinstance(editor_components, dict) and editor_components:
        records: list[dict[str, Any]] = []
        for name, component in editor_components.items():
            if not isinstance(component, dict):
                continue
            props_root = component.get("properties")
            props = {}
            if isinstance(props_root, dict):
                props = props_root.get("BaseElementTab") if isinstance(props_root.get("BaseElementTab"), dict) else {}
            origin = _parse_mil_location(props.get("Location"))
            layer = str(props.get("PlacementLayer") or "TOP")
            local_bbox = _component_info_bbox_mm(component.get("component_info"))
            component_name = _component_info_value(component.get("component_info"), "ComponentName")
            records.append(
                {
                    "name": str(name),
                    "type": "component",
                    "layer": layer,
                    "net": None,
                    "bbox_mm": _translated_bbox(local_bbox, origin) if local_bbox and origin else None,
                    "location_mm": list(origin) if origin else None,
                    "part": component_name,
                }
            )
            pin_info = component.get("pin_info")
            if isinstance(pin_info, dict):
                for pin_name, info in pin_info.items():
                    records.append(
                        {
                            "name": f"{name}.{pin_name}",
                            "type": "component_pin",
                            "layer": layer,
                            "net": _component_info_value(info, "NetName"),
                            "location_mm": _pin_location_mm(info),
                            "bbox_mm": None,
                            "part": component_name,
                        }
                    )
        return records

    raw = payload.get("modeler_components")
    if not isinstance(raw, dict):
        return []
    records: list[dict[str, Any]] = []
    for name, component in raw.items():
        if not isinstance(component, dict):
            continue
        layer = str(component.get("placement_layer") or "TOP")
        bbox = _clean_bbox(component.get("bbox_mm"))
        record = {
            "name": str(name),
            "type": "component",
            "layer": layer,
            "net": component.get("net_name"),
            "bbox_mm": list(bbox) if bbox else None,
            "location_mm": component.get("location_mm"),
            "part": component.get("part"),
        }
        records.append(record)
        pins = component.get("pins")
        if isinstance(pins, dict):
            for pin_name, pin in pins.items():
                if not isinstance(pin, dict):
                    continue
                pin_layer = str(pin.get("start_layer") or pin.get("placement_layer") or layer)
                records.append(
                    {
                        "name": f"{name}.{pin_name}",
                        "type": "component_pin",
                        "layer": pin_layer,
                        "net": pin.get("net"),
                        "location_mm": pin.get("location_mm"),
                        "bbox_mm": pin.get("bbox_mm"),
                        "part": component.get("part"),
                    }
                )
    return records


def _component_pin_names(payload: dict[str, Any]) -> set[str]:
    raw = payload.get("modeler_components")
    if not isinstance(raw, dict):
        return set()
    names: set[str] = set()
    for component in raw.values():
        if not isinstance(component, dict):
            continue
        pins = component.get("pins")
        if isinstance(pins, dict):
            names.update(str(name) for name in pins.keys())
    return names


def _crop_bbox(
    objects: list[dict[str, Any]],
    *,
    signal_nets: list[str],
    layers: list[str],
    explicit_crop: list[float] | None,
    focus_signal: bool,
    margin_mm: float,
) -> tuple[float, float, float, float]:
    if explicit_crop is not None:
        if len(explicit_crop) != 4:
            raise ValueError("--crop expects four numbers: xmin ymin xmax ymax")
        bbox = tuple(float(item) for item in explicit_crop)
        return _expand_bbox((bbox[0], bbox[1], bbox[2], bbox[3]), 0.0)

    layer_set = {layer.lower() for layer in layers}
    candidates = [
        obj
        for obj in objects
        if not layer_set or str(obj.get("layer") or "").lower() in layer_set
    ]
    if focus_signal and signal_nets:
        signal_set = {net.lower() for net in signal_nets}
        signal_boxes = [
            bbox
            for obj in candidates
            if str(obj.get("net") or "").lower() in signal_set
            for bbox in [_object_bbox(obj)]
            if bbox is not None
        ]
        merged = _merge_bboxes(signal_boxes)
        if merged is not None:
            return _expand_bbox(merged, margin_mm)

    merged = _merge_bboxes([bbox for obj in candidates for bbox in [_object_bbox(obj)] if bbox is not None])
    if merged is None:
        raise ValueError("no drawable geometry found in input JSON")
    return _expand_bbox(merged, margin_mm)


class View:
    def __init__(self, bbox: tuple[float, float, float, float], *, width_px: int, title_height_px: float = 32.0):
        self.min_x, self.min_y, self.max_x, self.max_y = bbox
        width_mm = max(self.max_x - self.min_x, 1e-6)
        height_mm = max(self.max_y - self.min_y, 1e-6)
        self.width_px = float(width_px)
        self.scale = self.width_px / width_mm
        self.height_px = height_mm * self.scale
        self.title_height_px = title_height_px

    def sx(self, x: float) -> float:
        return (x - self.min_x) * self.scale

    def sy(self, y: float, y_offset: float) -> float:
        return y_offset + self.title_height_px + (self.max_y - y) * self.scale


def _style_for_object(obj: dict[str, Any], signal_nets: set[str], layer: str) -> tuple[str, str, float]:
    net = str(obj.get("net") or "")
    typ = str(obj.get("type") or "").lower()
    if typ == "ground_plane":
        return "#8eae98", "#315542", 0.32
    if typ == "component":
        return "none", "#111827", 0.72
    if typ == "component_pin":
        return "#ffffff", "#111827", 0.92
    if bool(obj.get("is_void")):
        return VOID_FILL, VOID_STROKE, 0.78
    if net.lower() in signal_nets:
        return SIGNAL_COLOR, "#9a3412", 0.9
    if net.lower() == "gnd":
        return GND_COLOR, "#315542", 0.62
    if net and net != "None":
        return OTHER_SIGNAL_COLOR, "#1d4ed8", 0.6
    color = DEFAULT_LAYER_COLORS.get(layer, "#64748b")
    return color, color, 0.36


def _title(obj: dict[str, Any]) -> str:
    parts = [str(obj.get("name") or "unnamed")]
    for key in ("type", "layer", "net"):
        value = obj.get(key)
        if value not in (None, "", "None"):
            parts.append(f"{key}={value}")
    if obj.get("is_void"):
        parts.append("void")
    if obj.get("part"):
        parts.append(f"part={obj.get('part')}")
    bbox = _clean_bbox(obj.get("bbox_mm"))
    if bbox is not None:
        parts.append(
            f"bbox_mm=[{_fmt(bbox[0])},{_fmt(bbox[1])},{_fmt(bbox[2])},{_fmt(bbox[3])}]"
        )
    return " ".join(parts)


def _label_point(obj: dict[str, Any]) -> tuple[float, float] | None:
    loc = _location(obj)
    if loc is not None:
        return loc
    bbox = _object_bbox(obj)
    if bbox is None:
        return None
    return (bbox[0] + bbox[2]) / 2.0, (bbox[1] + bbox[3]) / 2.0


def _svg_polygon(points: list[tuple[float, float]], view: View, y_offset: float, *, fill: str, stroke: str, opacity: float, title: str) -> str:
    svg_points = " ".join(f"{_fmt(view.sx(x))},{_fmt(view.sy(y, y_offset))}" for x, y in points)
    return (
        f'<polygon points="{svg_points}" fill="{fill}" stroke="{stroke}" stroke-width="1" '
        f'opacity="{_fmt(opacity, 2)}"><title>{escape(title)}</title></polygon>'
    )


def _svg_bbox(bbox: tuple[float, float, float, float], view: View, y_offset: float, *, fill: str, stroke: str, opacity: float, title: str) -> str:
    x0, y0, x1, y1 = bbox
    return (
        f'<rect x="{_fmt(view.sx(x0))}" y="{_fmt(view.sy(y1, y_offset))}" '
        f'width="{_fmt((x1 - x0) * view.scale)}" height="{_fmt((y1 - y0) * view.scale)}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1" opacity="{_fmt(opacity, 2)}">'
        f"<title>{escape(title)}</title></rect>"
    )


def _svg_polyline(points: list[tuple[float, float]], view: View, y_offset: float, *, width_mm: float, stroke: str, opacity: float, title: str) -> str:
    svg_points = " ".join(f"{_fmt(view.sx(x))},{_fmt(view.sy(y, y_offset))}" for x, y in points)
    stroke_width = max(width_mm * view.scale, 1.0)
    return (
        f'<polyline points="{svg_points}" fill="none" stroke="{stroke}" stroke-width="{_fmt(stroke_width)}" '
        f'stroke-linecap="round" stroke-linejoin="round" opacity="{_fmt(opacity, 2)}">'
        f"<title>{escape(title)}</title></polyline>"
    )


def _svg_marker(obj: dict[str, Any], view: View, y_offset: float, *, fill: str, stroke: str, opacity: float, title: str) -> str:
    loc = _location(obj)
    if loc is None:
        bbox = _object_bbox(obj)
        if bbox is None:
            return ""
        loc = ((bbox[0] + bbox[2]) / 2.0, (bbox[1] + bbox[3]) / 2.0)
    x, y = loc
    cx = view.sx(x)
    cy = view.sy(y, y_offset)
    typ = str(obj.get("type") or "").lower()
    if typ == "via":
        r = 0.12 * view.scale
        return (
            f'<circle cx="{_fmt(cx)}" cy="{_fmt(cy)}" r="{_fmt(max(r, 2.0))}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1" opacity="{_fmt(opacity, 2)}">'
            f"<title>{escape(title)}</title></circle>"
        )
    if typ == "component_pin":
        r = 3.8
        return (
            f'<circle cx="{_fmt(cx)}" cy="{_fmt(cy)}" r="{_fmt(r)}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.3" opacity="{_fmt(opacity, 2)}">'
            f"<title>{escape(title)}</title></circle>"
        )
    size = 5.0
    return (
        f'<g opacity="{_fmt(opacity, 2)}"><line x1="{_fmt(cx - size)}" y1="{_fmt(cy)}" x2="{_fmt(cx + size)}" '
        f'y2="{_fmt(cy)}" stroke="{stroke}" stroke-width="1.4"/><line x1="{_fmt(cx)}" y1="{_fmt(cy - size)}" '
        f'x2="{_fmt(cx)}" y2="{_fmt(cy + size)}" stroke="{stroke}" stroke-width="1.4"/>'
        f'<title>{escape(title)}</title></g>'
    )


def _object_svg(obj: dict[str, Any], view: View, y_offset: float, signal_nets: set[str]) -> str:
    layer = str(obj.get("layer") or "")
    fill, stroke, opacity = _style_for_object(obj, signal_nets, layer)
    title = _title(obj)
    typ = str(obj.get("type") or "").lower()
    if typ == "component":
        bbox = _clean_bbox(obj.get("bbox_mm"))
        if bbox is not None and (bbox[2] > bbox[0] or bbox[3] > bbox[1]):
            return _svg_bbox(bbox, view, y_offset, fill="none", stroke=stroke, opacity=opacity, title=title)
    if typ == "ground_plane":
        bbox = _clean_bbox(obj.get("bbox_mm"))
        if bbox is not None:
            return _svg_bbox(bbox, view, y_offset, fill=fill, stroke=stroke, opacity=opacity, title=title)

    if typ == "line":
        center_line = _clean_points(obj.get("center_line_points_mm"))
        width = _as_float(obj.get("width_mm")) or 0.05
        if len(center_line) >= 2:
            return _svg_polyline(center_line, view, y_offset, width_mm=width, stroke=fill, opacity=opacity, title=title)

    points = _clean_points(obj.get("points_mm"))
    if len(points) >= 3:
        return _svg_polygon(points, view, y_offset, fill=fill, stroke=stroke, opacity=opacity, title=title)
    if len(points) >= 2:
        return _svg_polyline(points, view, y_offset, width_mm=0.05, stroke=fill, opacity=opacity, title=title)

    bbox = _clean_bbox(obj.get("bbox_mm"))
    if bbox is not None and (bbox[2] > bbox[0] or bbox[3] > bbox[1]):
        return _svg_bbox(bbox, view, y_offset, fill=fill, stroke=stroke, opacity=opacity, title=title)

    return _svg_marker(obj, view, y_offset, fill=fill or PIN_COLOR, stroke=stroke or PIN_COLOR, opacity=max(opacity, 0.85), title=title)


def _grid_svg(view: View, y_offset: float) -> str:
    width = view.width_px
    height = view.height_px
    if max(view.max_x - view.min_x, view.max_y - view.min_y) <= 16:
        step = 1.0
    else:
        step = 5.0
    first_x = math.ceil(view.min_x / step) * step
    first_y = math.ceil(view.min_y / step) * step
    parts: list[str] = [
        f'<rect x="0" y="{_fmt(y_offset + view.title_height_px)}" width="{_fmt(width)}" height="{_fmt(height)}" fill="{BG_COLOR}" stroke="#aeb6c1" stroke-width="1"/>'
    ]
    x = first_x
    while x <= view.max_x + 1e-9:
        sx = view.sx(x)
        parts.append(
            f'<line x1="{_fmt(sx)}" y1="{_fmt(y_offset + view.title_height_px)}" x2="{_fmt(sx)}" '
            f'y2="{_fmt(y_offset + view.title_height_px + height)}" stroke="{GRID_COLOR}" stroke-width="0.6"/>'
        )
        parts.append(
            f'<text x="{_fmt(sx + 2)}" y="{_fmt(y_offset + view.title_height_px + 12)}" font-size="10" fill="#6b7280">{escape(_fmt(x))}</text>'
        )
        x += step
    y = first_y
    while y <= view.max_y + 1e-9:
        sy = view.sy(y, y_offset)
        parts.append(
            f'<line x1="0" y1="{_fmt(sy)}" x2="{_fmt(width)}" y2="{_fmt(sy)}" stroke="{GRID_COLOR}" stroke-width="0.6"/>'
        )
        parts.append(
            f'<text x="4" y="{_fmt(sy - 3)}" font-size="10" fill="#6b7280">{escape(_fmt(y))}</text>'
        )
        y += step
    scale_len_mm = 1.0 if view.max_x - view.min_x <= 16 else 5.0
    x0 = width - (scale_len_mm * view.scale) - 18
    y0 = y_offset + view.title_height_px + height - 18
    parts.append(
        f'<line x1="{_fmt(x0)}" y1="{_fmt(y0)}" x2="{_fmt(x0 + scale_len_mm * view.scale)}" '
        f'y2="{_fmt(y0)}" stroke="#111827" stroke-width="2"/>'
    )
    parts.append(
        f'<text x="{_fmt(x0)}" y="{_fmt(y0 - 5)}" font-size="11" fill="#111827">{_fmt(scale_len_mm)} mm</text>'
    )
    return "\n".join(parts)


def _label_svg(objects: list[dict[str, Any]], view: View, y_offset: float, signal_nets: set[str]) -> str:
    labels: list[str] = []
    for obj in objects:
        name = str(obj.get("name") or "")
        net = str(obj.get("net") or "").lower()
        typ = str(obj.get("type") or "").lower()
        important = (
            net in signal_nets
            or bool(obj.get("is_void"))
            or (typ == "pin" and net in signal_nets)
            or typ in {"component", "component_pin"}
        )
        if not important:
            continue
        point = _label_point(obj)
        if point is None:
            continue
        x, y = point
        sx = view.sx(x)
        sy = view.sy(y, y_offset)
        text = name
        if obj.get("is_void"):
            text = f"{name} void"
        labels.append(
            f'<text x="{_fmt(sx + 5)}" y="{_fmt(sy - 4)}" font-size="10" fill="{TEXT_COLOR}" '
            f'paint-order="stroke" stroke="{BG_COLOR}" stroke-width="3" stroke-linejoin="round">{escape(text)}</text>'
        )
    return "\n".join(labels)


def _object_span_mm(obj: dict[str, Any]) -> float | None:
    bbox = _object_bbox(obj)
    if bbox is None:
        return None
    return max(bbox[2] - bbox[0], bbox[3] - bbox[1])


def _should_render_object(
    obj: dict[str, Any],
    signal_nets: set[str],
    *,
    signal_only: bool,
    max_object_span_mm: float | None,
    component_pin_names: set[str],
) -> bool:
    span = _object_span_mm(obj)
    if max_object_span_mm is not None and span is not None and span > max_object_span_mm:
        if str(obj.get("type") or "").lower() in {"component", "ground_plane"}:
            return True
        return False
    if str(obj.get("type") or "").lower() == "pin" and str(obj.get("name") or "") in component_pin_names:
        return False
    if not signal_only:
        return True
    if bool(obj.get("is_void")):
        return True
    net = str(obj.get("net") or "").lower()
    return net in signal_nets or net == "gnd"


def _panel_svg(
    title: str,
    objects: list[dict[str, Any]],
    view: View,
    y_offset: float,
    *,
    panel_id: str,
    crop: tuple[float, float, float, float],
    signal_nets: set[str],
    signal_only: bool,
    max_object_span_mm: float | None,
    component_pin_names: set[str],
) -> str:
    visible = [
        obj
        for obj in objects
        for bbox in [_object_bbox(obj)]
        if bbox is not None
        and _bbox_intersects(bbox, crop)
        and _should_render_object(
            obj,
            signal_nets,
            signal_only=signal_only,
            max_object_span_mm=max_object_span_mm,
            component_pin_names=component_pin_names,
        )
    ]
    visible.sort(
        key=lambda obj: (
            -1 if str(obj.get("type") or "").lower() == "ground_plane" else (
                0 if str(obj.get("type") or "").lower() not in {"via", "pin", "component_pin"} else 1
            ),
            2 if bool(obj.get("is_void")) else 0,
            str(obj.get("name") or ""),
        )
    )
    parts = [
        f'<g class="panel"><text x="0" y="{_fmt(y_offset + 22)}" font-size="18" font-family="Arial, sans-serif" '
        f'font-weight="700" fill="{TEXT_COLOR}">{escape(title)}</text>',
        _grid_svg(view, y_offset),
        f'<clipPath id="{escape(panel_id)}"><rect x="0" y="{_fmt(y_offset + view.title_height_px)}" '
        f'width="{_fmt(view.width_px)}" height="{_fmt(view.height_px)}"/></clipPath>',
        f'<g clip-path="url(#{escape(panel_id)})">',
    ]
    parts.extend(_object_svg(obj, view, y_offset, signal_nets) for obj in visible)
    parts.append(_label_svg(visible, view, y_offset, signal_nets))
    parts.append("</g>")
    parts.append("</g>")
    return "\n".join(part for part in parts if part)


def _legend_svg(payload: dict[str, Any], view: View, *, x: float, y: float, signal_nets: list[str], crop: tuple[float, float, float, float]) -> str:
    distilled = payload.get("distilled") if isinstance(payload.get("distilled"), dict) else {}
    lines = [
        "API layout SVG",
        f"Design: {payload.get('design', '')}",
        f"Model units: {payload.get('model_units', '')} -> mm",
        "Stack: L1 TOP -> L2 GND -> L3 SIG -> L4 BOTTOM",
        f"Signal nets: {', '.join(signal_nets) if signal_nets else 'none'}",
        f"Crop: [{_fmt(crop[0])}, {_fmt(crop[1])}] to [{_fmt(crop[2])}, {_fmt(crop[3])}] mm",
    ]
    if isinstance(distilled, dict):
        signal_size = distilled.get("signal_bbox_size_mm")
        if isinstance(signal_size, dict):
            lines.append(
                f"Signal bbox: {_fmt(float(signal_size.get('w_mm', 0)))} x {_fmt(float(signal_size.get('h_mm', 0)))} mm"
            )
        if "void_object_count" in distilled:
            lines.append(f"Void objects: {distilled.get('void_object_count')}")
        if "gnd_via_count" in distilled:
            lines.append(f"GND vias: {distilled.get('gnd_via_count')}")
    preview_layers = payload.get("_solid_gnd_layers")
    if isinstance(preview_layers, list) and preview_layers:
        lines.append(f"Preview solid GND: {', '.join(str(item) for item in preview_layers)}")

    swatches = [
        ("Signal", SIGNAL_COLOR),
        ("GND", GND_COLOR),
        ("Void/cutout", VOID_STROKE),
        ("Other signal", OTHER_SIGNAL_COLOR),
        ("Component/pin", PIN_COLOR),
    ]
    parts = [
        f'<g class="legend" font-family="Arial, sans-serif" fill="{TEXT_COLOR}">',
        f'<rect x="{_fmt(x)}" y="{_fmt(y)}" width="260" height="{_fmt(88 + len(lines) * 17)}" '
        f'fill="#ffffff" stroke="#c7cdd5" stroke-width="1"/>',
    ]
    yy = y + 24
    for line in lines:
        weight = "700" if line == "API layout SVG" else "400"
        parts.append(
            f'<text x="{_fmt(x + 12)}" y="{_fmt(yy)}" font-size="12" font-weight="{weight}">{escape(line)}</text>'
        )
        yy += 17
    yy += 8
    for name, color in swatches:
        parts.append(f'<rect x="{_fmt(x + 12)}" y="{_fmt(yy - 10)}" width="12" height="12" fill="{color}"/>')
        parts.append(f'<text x="{_fmt(x + 32)}" y="{_fmt(yy)}" font-size="12">{escape(name)}</text>')
        yy += 18
    parts.append("</g>")
    return "\n".join(parts)


def render_svg(
    payload: dict[str, Any],
    *,
    layers: list[str] | None = None,
    signal_nets: list[str] | None = None,
    focus_signal: bool = True,
    margin_mm: float = 3.0,
    crop: list[float] | None = None,
    width_px: int = 900,
    signal_only: bool = False,
    max_object_span_mm: float | None = 15.0,
    solid_gnd_layers: list[str] | None = None,
) -> str:
    objects = [obj for obj in payload.get("objects", []) if isinstance(obj, dict)]
    objects.extend(_component_records(payload))
    component_pin_names = _component_pin_names(payload)
    selected_layers = _layers(payload, layers)
    selected_signal_nets = _signal_nets(payload, signal_nets)
    signal_set = {net.lower() for net in selected_signal_nets}
    crop_bbox = _crop_bbox(
        objects,
        signal_nets=selected_signal_nets,
        layers=selected_layers,
        explicit_crop=crop,
        focus_signal=focus_signal,
        margin_mm=margin_mm,
    )
    solid_layers = {str(layer).lower() for layer in (solid_gnd_layers or [])}
    if solid_layers:
        filtered_objects: list[dict[str, Any]] = []
        for obj in objects:
            layer = str(obj.get("layer") or "").lower()
            if layer not in solid_layers:
                filtered_objects.append(obj)
                continue
            net = str(obj.get("net") or "").lower()
            typ = str(obj.get("type") or "").lower()
            if net == "gnd" or typ in {"via", "component", "component_pin"}:
                filtered_objects.append(obj)
        objects = filtered_objects
        for layer in solid_layers:
            selected_layer = next(
                (name for name in selected_layers if name.lower() == layer),
                layer,
            )
            objects.append(
                {
                    "name": f"solid_gnd_{selected_layer}",
                    "type": "ground_plane",
                    "layer": selected_layer,
                    "net": "GND",
                    "bbox_mm": list(crop_bbox),
                    "role": "preview_solid_ground_override",
                }
            )
        payload["_solid_gnd_layers"] = [
            next((name for name in selected_layers if name.lower() == layer), layer)
            for layer in sorted(solid_layers, key=lambda item: (LAYER_ORDER.get(item.upper(), 100), item))
        ]
    view = View(crop_bbox, width_px=width_px)
    panel_gap = 28.0
    panel_step = view.title_height_px + view.height_px + panel_gap
    panel_titles = selected_layers + ["Overlay"]
    total_height = panel_step * len(panel_titles) - panel_gap + 18
    total_width = width_px + 288

    by_layer = {
        layer: [obj for obj in objects if str(obj.get("layer") or "").lower() == layer.lower()]
        for layer in selected_layers
    }
    overlay_objects = [obj for layer in selected_layers for obj in by_layer.get(layer, [])]
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{_fmt(total_width)}" height="{_fmt(total_height)}" '
        f'viewBox="0 0 {_fmt(total_width)} {_fmt(total_height)}">',
        "<defs>",
        '<style>text { font-family: Arial, sans-serif; } .panel text { pointer-events: none; }</style>',
        "</defs>",
    ]
    for index, layer in enumerate(selected_layers):
        parts.append(
            _panel_svg(
                f"{LAYER_ALIASES.get(layer, layer)} layer",
                by_layer.get(layer, []),
                view,
                panel_step * index,
                panel_id=f"clip-{index}-{layer}",
                crop=crop_bbox,
                signal_nets=signal_set,
                signal_only=signal_only,
                max_object_span_mm=max_object_span_mm,
                component_pin_names=component_pin_names,
            )
        )
    overlay_index = len(selected_layers)
    parts.append(
        _panel_svg(
            "Overlay - selected HFSS 3D Layout geometry",
            overlay_objects,
            view,
            panel_step * overlay_index,
            panel_id="clip-overlay",
            crop=crop_bbox,
            signal_nets=signal_set,
            signal_only=signal_only,
            max_object_span_mm=max_object_span_mm,
            component_pin_names=component_pin_names,
        )
    )
    parts.append(
        _legend_svg(
            payload,
            view,
            x=width_px + 18,
            y=36,
            signal_nets=selected_signal_nets,
            crop=crop_bbox,
        )
    )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def render_file(args: argparse.Namespace) -> Path:
    payload = read_json_object(args.input)
    svg = render_svg(
        payload,
        layers=args.layers,
        signal_nets=args.signal_nets,
        focus_signal=not args.full_extent,
        margin_mm=args.margin_mm,
        crop=args.crop,
        width_px=args.width_px,
        signal_only=args.signal_only,
        max_object_span_mm=args.max_object_span_mm,
        solid_gnd_layers=args.solid_gnd_layers,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8")
    return args.output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render API-extracted HFSS 3D Layout geometry to SVG.")
    parser.add_argument("--input", type=Path, required=True, help="Full layout JSON from the AEDT API extractor.")
    parser.add_argument("--output", type=Path, required=True, help="Output SVG path.")
    parser.add_argument("--layers", nargs="+", default=None, help="Layer names to render. Defaults to extracted/requested layers.")
    parser.add_argument("--signal-nets", nargs="+", default=None, help="Signal nets to highlight. Defaults to JSON signal_nets.")
    parser.add_argument("--full-extent", action="store_true", help="Render full extracted extent instead of signal-focused crop.")
    parser.add_argument("--signal-only", action="store_true", help="Draw only highlighted signal nets, GND, and void/cutout objects.")
    parser.add_argument(
        "--solid-gnd-layers",
        nargs="+",
        default=None,
        help="Preview a continuous GND plane on these layers, removing their non-GND geometry from the SVG only.",
    )
    parser.add_argument(
        "--max-object-span-mm",
        type=float,
        default=15.0,
        help="Skip objects whose bbox width or height exceeds this value. Use 0 or negative to disable.",
    )
    parser.add_argument("--margin-mm", type=float, default=3.0, help="Margin around the signal-focused crop.")
    parser.add_argument("--crop", nargs=4, type=float, default=None, metavar=("XMIN", "YMIN", "XMAX", "YMAX"))
    parser.add_argument("--width-px", type=int, default=900)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.max_object_span_mm is not None and args.max_object_span_mm <= 0:
        args.max_object_span_mm = None
    output = render_file(args)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
