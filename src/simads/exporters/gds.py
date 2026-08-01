"""Optional GDS exporter.

GDS export requires `gdstk`. The dependency is optional because most current
ADS flows use DXF, and ADS Python environments should not import extra binary
packages unless explicitly configured.
"""

from __future__ import annotations

from pathlib import Path as FsPath

from simads.geometry import Boundary, Layout, Polygon, Rect, Shape, Via


class ExportDependencyError(RuntimeError):
    """Raised when an optional export backend is unavailable."""


def _layer_map(layout: Layout) -> dict[str, tuple[int, int]]:
    result: dict[str, tuple[int, int]] = {}
    for idx, layer in enumerate(layout.layers, start=1):
        result[layer.name] = (layer.gds_layer or idx, layer.gds_datatype)
    return result


def _shape_polygons(shape: Shape) -> list[tuple[str, list[tuple[float, float]]]]:
    if isinstance(shape, Rect):
        return [(shape.layer, shape.points)]
    if isinstance(shape, Polygon):
        return [(shape.layer, shape.points)]
    if isinstance(shape, Boundary):
        return []
    if isinstance(shape, Via):
        pad_layer = shape.pad_layer or shape.layer
        pad_d = shape.pad_diameter or shape.diameter
        r = pad_d / 2.0
        return [
            (
                pad_layer,
                [
                    (shape.x - r, shape.y - r),
                    (shape.x + r, shape.y - r),
                    (shape.x + r, shape.y + r),
                    (shape.x - r, shape.y + r),
                ],
            )
        ]
    return []


def write_gds(path: FsPath, layout: Layout) -> None:
    try:
        import gdstk  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ExportDependencyError("GDS export requires optional dependency 'gdstk'.") from exc

    lib = gdstk.Library(unit=1e-3 if layout.units == "mm" else 1e-6, precision=1e-9)
    cell = lib.new_cell(layout.layout_id)
    layers = _layer_map(layout)
    for shape in layout.shapes:
        for layer_name, points in _shape_polygons(shape):
            layer, datatype = layers.get(layer_name, (1, 0))
            cell.add(gdstk.Polygon(points, layer=layer, datatype=datatype))
    path.parent.mkdir(parents=True, exist_ok=True)
    lib.write_gds(str(path))

