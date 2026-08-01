"""Machine checks for structured layout JSON files."""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LayoutCheck:
    name: str
    ok: bool
    message: str


def load_layout_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"layout JSON must be an object: {path}")
    return data


def _layer_names(layout: dict[str, Any]) -> set[str]:
    layers = layout.get("layers")
    if not isinstance(layers, list):
        return set()
    return {str(layer.get("name")) for layer in layers if isinstance(layer, dict) and layer.get("name")}


def _shapes(layout: dict[str, Any]) -> list[dict[str, Any]]:
    shapes = layout.get("shapes")
    return [shape for shape in shapes if isinstance(shape, dict)] if isinstance(shapes, list) else []


def _ports(layout: dict[str, Any]) -> list[dict[str, Any]]:
    ports = layout.get("ports")
    return [port for port in ports if isinstance(port, dict)] if isinstance(ports, list) else []


def _rect_contains_point(shape: dict[str, Any], x: float, y: float, margin: float = 1e-9) -> bool:
    sx = float(shape["x"])
    sy = float(shape["y"])
    sw = float(shape["w"])
    sh = float(shape["h"])
    min_x, max_x = sorted((sx, sx + sw))
    min_y, max_y = sorted((sy, sy + sh))
    return min_x - margin <= x <= max_x + margin and min_y - margin <= y <= max_y + margin


def _polygon_contains_point(points: list[list[float]], x: float, y: float, margin: float = 1e-9) -> bool:
    inside = False
    count = len(points)
    if count < 3:
        return False
    for idx in range(count):
        x1, y1 = float(points[idx][0]), float(points[idx][1])
        x2, y2 = float(points[(idx + 1) % count][0]), float(points[(idx + 1) % count][1])
        if _distance_point_to_segment(x, y, x1, y1, x2, y2) <= margin:
            return True
        crosses = (y1 > y) != (y2 > y)
        if crosses:
            x_at_y = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x <= x_at_y:
                inside = not inside
    return inside


def _distance_point_to_segment(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def _path_contains_point(shape: dict[str, Any], x: float, y: float, margin: float = 1e-9) -> bool:
    points = shape.get("points")
    if not isinstance(points, list) or len(points) < 2:
        return False
    half_width = float(shape.get("width", 0.0)) / 2.0
    for start, end in zip(points, points[1:], strict=False):
        if _distance_point_to_segment(x, y, float(start[0]), float(start[1]), float(end[0]), float(end[1])) <= half_width + margin:
            return True
    return False


def point_on_layer(layout: dict[str, Any], x: float, y: float, layer: str) -> bool:
    for shape in _shapes(layout):
        if shape.get("layer") != layer:
            continue
        kind = shape.get("kind")
        if kind == "rect" and all(key in shape for key in ("x", "y", "w", "h")):
            if _rect_contains_point(shape, x, y):
                return True
        if kind == "polygon" and isinstance(shape.get("points"), list):
            if _polygon_contains_point(shape["points"], x, y):
                return True
        if kind == "path":
            if _path_contains_point(shape, x, y):
                return True
    return False


def _shape_metadata(shape: dict[str, Any]) -> dict[str, Any]:
    metadata = shape.get("metadata")
    return metadata if isinstance(metadata, dict) else {}


def _shape_role(shape: dict[str, Any]) -> str:
    return str(_shape_metadata(shape).get("role", ""))


def _rect_bounds(shape: dict[str, Any]) -> tuple[float, float, float, float] | None:
    if shape.get("kind") != "rect" or not all(key in shape for key in ("x", "y", "w", "h")):
        return None
    try:
        x = float(shape["x"])
        y = float(shape["y"])
        w = float(shape["w"])
        h = float(shape["h"])
    except (TypeError, ValueError):
        return None
    x1, x2 = sorted((x, x + w))
    y1, y2 = sorted((y, y + h))
    return x1, y1, x2, y2


def _rect_gap(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    dx = max(bx1 - ax2, ax1 - bx2, 0.0)
    dy = max(by1 - ay2, ay1 - by2, 0.0)
    return math.hypot(dx, dy)


def _rects_touch_or_overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float], margin: float = 1e-9) -> bool:
    return _rect_gap(a, b) <= margin


def _connected_components(rects: list[tuple[float, float, float, float]]) -> list[list[int]]:
    remaining = set(range(len(rects)))
    components: list[list[int]] = []
    while remaining:
        seed = remaining.pop()
        component = [seed]
        stack = [seed]
        while stack:
            current = stack.pop()
            touching = [idx for idx in remaining if _rects_touch_or_overlap(rects[current], rects[idx])]
            for idx in touching:
                remaining.remove(idx)
                stack.append(idx)
                component.append(idx)
        components.append(component)
    return components


def _rects_intersect(a: tuple[float, float, float, float], b: tuple[float, float, float, float], margin: float = 1e-9) -> bool:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return ax1 <= bx2 + margin and bx1 <= ax2 + margin and ay1 <= by2 + margin and by1 <= ay2 + margin


def validate_pixel_qr_bpf_layout(
    layout: dict[str, Any],
    *,
    metal_layer: str = "cond",
    min_spacing_mm: float | None = 0.1016,
    max_island_components: int | None = None,
) -> list[LayoutCheck]:
    checks: list[LayoutCheck] = []

    def add(name: str, ok: bool, message: str) -> None:
        checks.append(LayoutCheck(name, ok, message))

    metadata = layout.get("metadata") if isinstance(layout.get("metadata"), dict) else {}
    topology = metadata.get("topology")
    add("pixel_qr.topology", topology == "pixel_qr_bpf", "layout metadata topology must be pixel_qr_bpf")

    rows_raw = metadata.get("mask_rows")
    rows = [str(row) for row in rows_raw] if isinstance(rows_raw, list) else []
    mask_ok = bool(rows) and all(len(row) == len(rows) and set(row) <= {"0", "1"} for row in rows)
    add("pixel_qr.mask_rows", mask_ok, "mask_rows must be a non-empty square 0/1 matrix")

    source_map = metadata.get("source_map") if isinstance(metadata.get("source_map"), dict) else {}
    add("pixel_qr.source_map", "pixels" in source_map and "P1" in source_map and "P2" in source_map, "source_map must trace pixels, P1 and P2")

    shapes = _shapes(layout)
    metal_rect_items = [(shape, bounds) for shape in shapes if shape.get("layer") == metal_layer for bounds in [_rect_bounds(shape)] if bounds]
    pixel_items = [(shape, bounds) for shape, bounds in metal_rect_items if _shape_role(shape) == "binary_pixel"]
    feed_left = next((bounds for shape, bounds in metal_rect_items if shape.get("name") == "feed_left"), None)
    feed_right = next((bounds for shape, bounds in metal_rect_items if shape.get("name") == "feed_right"), None)

    add("pixel_qr.feed_left", feed_left is not None, "feed_left metal rectangle must exist")
    add("pixel_qr.feed_right", feed_right is not None, "feed_right metal rectangle must exist")
    add("pixel_qr.pixel_count", bool(pixel_items), "layout must contain binary pixel metal rectangles")

    if mask_ok:
        expected = {(row_idx, col_idx) for row_idx, row in enumerate(rows) for col_idx, value in enumerate(row) if value == "1"}
        actual: set[tuple[int, int]] = set()
        for shape, _bounds in pixel_items:
            shape_metadata = _shape_metadata(shape)
            try:
                actual.add((int(shape_metadata["row"]), int(shape_metadata["col"])))
            except (KeyError, TypeError, ValueError):
                pass
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        add(
            "pixel_qr.mask_pixels",
            not missing and not extra,
            f"pixel rectangles must match mask_rows; missing={len(missing)}, extra={len(extra)}",
        )

        left_edge = [bounds for shape, bounds in pixel_items if _shape_metadata(shape).get("col") == 0]
        right_edge = [bounds for shape, bounds in pixel_items if _shape_metadata(shape).get("col") == len(rows) - 1]
        left_coupled = feed_left is not None and any(_rects_intersect(feed_left, bounds) for bounds in left_edge)
        right_coupled = feed_right is not None and any(_rects_intersect(feed_right, bounds) for bounds in right_edge)
        add("pixel_qr.feed_left_coupled", bool(left_coupled), "feed_left must overlap or touch at least one left-edge pixel")
        add("pixel_qr.feed_right_coupled", bool(right_coupled), "feed_right must overlap or touch at least one right-edge pixel")

    rect_bounds = [bounds for _shape, bounds in metal_rect_items]
    if min_spacing_mm is not None and rect_bounds:
        min_gap: float | None = None
        min_pair: tuple[int, int] | None = None
        for idx, first in enumerate(rect_bounds):
            for jdx in range(idx + 1, len(rect_bounds)):
                second = rect_bounds[jdx]
                if _rects_touch_or_overlap(first, second):
                    continue
                gap = _rect_gap(first, second)
                if min_gap is None or gap < min_gap:
                    min_gap = gap
                    min_pair = (idx, jdx)
        spacing_ok = min_gap is None or min_gap + 1e-9 >= min_spacing_mm
        pair_text = "" if min_pair is None else f", pair={min_pair[0]}-{min_pair[1]}"
        actual_text = "none" if min_gap is None else f"{min_gap:.6g} mm"
        add("pixel_qr.min_metal_spacing", spacing_ok, f"minimum separated metal spacing must be >= {min_spacing_mm:.6g} mm; actual={actual_text}{pair_text}")

    if rect_bounds:
        components = _connected_components(rect_bounds)
        isolated = sum(1 for component in components if len(component) == 1)
        ok = max_island_components is None or isolated <= max_island_components
        limit_text = "unlimited" if max_island_components is None else str(max_island_components)
        add("pixel_qr.island_components", ok, f"metal connected components={len(components)}, isolated={isolated}, isolated_limit={limit_text}")

    return checks
def validate_layout_contract(
    layout: dict[str, Any],
    *,
    units: str = "mm",
    metal_layer: str = "cond",
    via_layer: str = "pcvia1",
    boundary_layer: str = "EM_BOUNDARY",
    layer_map_version: str | None = None,
    port_names: tuple[str, ...] = ("P1", "P2"),
) -> list[LayoutCheck]:
    checks: list[LayoutCheck] = []

    def add(name: str, ok: bool, message: str) -> None:
        checks.append(LayoutCheck(name, ok, message))

    layers = _layer_names(layout)
    shapes = _shapes(layout)
    ports = _ports(layout)
    shape_layers = {str(shape.get("layer")) for shape in shapes if shape.get("layer")}
    port_layers = {str(port.get("layer")) for port in ports if port.get("layer")}
    all_used_layers = shape_layers | port_layers

    add("units", layout.get("units") == units, f"layout units must be {units}")
    add("layer.metal", metal_layer in layers, f"declared layers must include metal layer {metal_layer}")
    add("layer.via", via_layer in layers, f"declared layers must include via layer {via_layer}")
    add("layer.boundary", boundary_layer in layers, f"declared layers must include boundary layer {boundary_layer}")
    missing_layers = sorted(layer for layer in all_used_layers if layer not in layers)
    add("layer_exists", not missing_layers, f"all used layers must be declared; missing={','.join(missing_layers)}")
    metadata = layout.get("metadata") if isinstance(layout.get("metadata"), dict) else {}
    add("source_trace", bool(metadata.get("source_map") or metadata.get("generator")), "layout metadata must contain source_map or generator")
    if layer_map_version:
        source_map = metadata.get("source_map") if isinstance(metadata.get("source_map"), dict) else {}
        actual_layer_map_version = metadata.get("layer_map_version") or source_map.get("layer_map_version")
        add(
            "layer_map.version",
            actual_layer_map_version == layer_map_version,
            f"layout metadata layer_map_version must be {layer_map_version}",
        )

    names = tuple(str(port.get("name")) for port in ports if port.get("name"))
    add("ports.names", names == port_names, f"ports must be {','.join(port_names)} in order")
    for port in ports:
        name = str(port.get("name", ""))
        try:
            x = float(port["x"])
            y = float(port["y"])
        except (KeyError, TypeError, ValueError):
            add(f"port.{name or 'unknown'}.coords", False, "port must contain numeric x/y")
            continue
        add(f"port.{name}.layer", port.get("layer") == metal_layer, f"port {name} must be on {metal_layer}")
        add(f"port.{name}.on_metal", point_on_layer(layout, x, y, metal_layer), f"port {name} coordinate must lie on metal")

    vias = [shape for shape in shapes if shape.get("kind") == "via"]
    for via in vias:
        name = str(via.get("name", "via"))
        try:
            x = float(via["x"])
            y = float(via["y"])
            diameter = float(via["diameter"])
        except (KeyError, TypeError, ValueError):
            add(f"via.{name}.geometry", False, "via must contain numeric x/y/diameter")
            continue
        add(f"via.{name}.layer", via.get("layer") == via_layer, f"via {name} must be on {via_layer}")
        pad_diameter = via.get("pad_diameter")
        pad_layer = via.get("pad_layer")
        try:
            has_valid_pad = pad_diameter not in (None, "") and float(pad_diameter) >= diameter and pad_layer == metal_layer
        except (TypeError, ValueError):
            has_valid_pad = False
        center_on_metal = point_on_layer(layout, x, y, metal_layer)
        add(
            f"via.{name}.inside_pad",
            bool(has_valid_pad or center_on_metal),
            f"via {name} must have a metal pad or center inside metal",
        )

    return checks

