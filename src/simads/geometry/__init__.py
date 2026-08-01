"""Common geometry objects for ADS layout automation.

The module is intentionally small and dependency-free. Device-specific layout
generators can build these objects first, then hand them to exporters or ADS
import helpers.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import math
from typing import Any, Iterable, Literal

from .validation import LayoutCheck, load_layout_json, point_on_layer, validate_layout_contract, validate_pixel_qr_bpf_layout


Point = tuple[float, float]
ShapeKind = Literal["rect", "polygon", "path", "via", "port", "boundary"]


@dataclass(frozen=True)
class LayerMap:
    name: str
    purpose: str = "drawing"
    ads_layer: str | None = None
    dxf_layer: str | None = None
    gds_layer: int | None = None
    gds_datatype: int = 0


@dataclass(frozen=True)
class Rect:
    name: str
    layer: str
    x: float
    y: float
    w: float
    h: float
    kind: ShapeKind = "rect"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def points(self) -> list[Point]:
        return [
            (self.x, self.y),
            (self.x + self.w, self.y),
            (self.x + self.w, self.y + self.h),
            (self.x, self.y + self.h),
        ]


@dataclass(frozen=True)
class Polygon:
    name: str
    layer: str
    points: list[Point]
    kind: ShapeKind = "polygon"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Path:
    name: str
    layer: str
    points: list[Point]
    width: float
    kind: ShapeKind = "path"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Via:
    name: str
    layer: str
    x: float
    y: float
    diameter: float
    pad_diameter: float | None = None
    pad_layer: str | None = None
    kind: ShapeKind = "via"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def radius(self) -> float:
        return self.diameter / 2.0


@dataclass(frozen=True)
class Port:
    name: str
    number: int
    x: float
    y: float
    width: float
    layer: str
    orientation_deg: float = 0.0
    reference: str | None = None
    kind: ShapeKind = "port"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Boundary:
    name: str
    x: float
    y: float
    w: float
    h: float
    layer: str = "EM_BOUNDARY"
    kind: ShapeKind = "boundary"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def points(self) -> list[Point]:
        return [
            (self.x, self.y),
            (self.x + self.w, self.y),
            (self.x + self.w, self.y + self.h),
            (self.x, self.y + self.h),
        ]


Shape = Rect | Polygon | Path | Via | Port | Boundary


@dataclass(frozen=True)
class Layout:
    layout_id: str
    units: str = "mm"
    layers: list[LayerMap] = field(default_factory=list)
    shapes: list[Shape] = field(default_factory=list)
    ports: list[Port] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def with_shapes(self, shapes: Iterable[Shape]) -> "Layout":
        return Layout(
            layout_id=self.layout_id,
            units=self.units,
            layers=self.layers,
            shapes=list(shapes),
            ports=self.ports,
            metadata=self.metadata,
        )


def fmt(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def shape_layer(shape: Shape) -> str:
    return getattr(shape, "layer", "")


def shape_points(shape: Shape) -> list[Point]:
    if isinstance(shape, (Rect, Polygon, Path, Boundary)):
        return list(shape.points)
    if isinstance(shape, Via):
        r = shape.radius
        return [
            (shape.x - r, shape.y - r),
            (shape.x + r, shape.y - r),
            (shape.x + r, shape.y + r),
            (shape.x - r, shape.y + r),
        ]
    if isinstance(shape, Port):
        half = shape.width / 2.0
        return [
            (shape.x - half, shape.y - half),
            (shape.x + half, shape.y - half),
            (shape.x + half, shape.y + half),
            (shape.x - half, shape.y + half),
        ]
    raise TypeError(f"unsupported shape type: {type(shape)!r}")


def bounds(shapes: Iterable[Shape]) -> tuple[float, float, float, float]:
    points = [point for shape in shapes for point in shape_points(shape)]
    if not points:
        raise ValueError("cannot compute bounds for an empty shape list")
    min_x = min(point[0] for point in points)
    min_y = min(point[1] for point in points)
    max_x = max(point[0] for point in points)
    max_y = max(point[1] for point in points)
    return min_x, min_y, max_x, max_y


def min_feature(shape: Shape) -> float:
    if isinstance(shape, Rect):
        return min(abs(shape.w), abs(shape.h))
    if isinstance(shape, Boundary):
        return min(abs(shape.w), abs(shape.h))
    if isinstance(shape, Path):
        return abs(shape.width)
    if isinstance(shape, Via):
        return abs(shape.diameter)
    if isinstance(shape, Port):
        return abs(shape.width)
    points = shape_points(shape)
    edges = [
        math.hypot(xb - xa, yb - ya)
        for (xa, ya), (xb, yb) in zip(points, points[1:] + points[:1], strict=False)
    ]
    return min(edges)


def to_dict(value: Any) -> Any:
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, list):
        return [to_dict(item) for item in value]
    if hasattr(value, "__dataclass_fields__"):
        return {key: to_dict(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): to_dict(item) for key, item in value.items()}
    return value


__all__ = [
    "Boundary",
    "LayerMap",
    "Layout",
    "LayoutCheck",
    "Path",
    "Point",
    "Polygon",
    "Port",
    "Rect",
    "Shape",
    "ShapeKind",
    "Via",
    "bounds",
    "fmt",
    "load_layout_json",
    "min_feature",
    "point_on_layer",
    "shape_layer",
    "shape_points",
    "to_dict",
    "validate_layout_contract",
    "validate_pixel_qr_bpf_layout",
]

