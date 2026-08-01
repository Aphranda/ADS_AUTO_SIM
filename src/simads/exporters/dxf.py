"""Minimal DXF exporter for generated ADS layout geometry."""

from __future__ import annotations

from pathlib import Path as FsPath

from simads.geometry import Boundary, Layout, Path, Polygon, Rect, Shape, Via, fmt


def _append_solid(lines: list[str], layer: str, points: list[tuple[float, float]]) -> None:
    if len(points) != 4:
        raise ValueError("DXF SOLID export requires exactly four points")
    lines.extend(["0", "SOLID", "8", layer])
    for idx, (x, y) in enumerate(points):
        group = 10 + idx
        lines.extend([str(group), fmt(x), str(group + 10), fmt(y), str(group + 20), "0"])


def _append_polyline(lines: list[str], layer: str, points: list[tuple[float, float]], *, closed: bool = True) -> None:
    lines.extend(["0", "LWPOLYLINE", "8", layer, "90", str(len(points)), "70", "1" if closed else "0"])
    for x, y in points:
        lines.extend(["10", fmt(x), "20", fmt(y)])


def _append_circle(lines: list[str], layer: str, x: float, y: float, radius: float) -> None:
    lines.extend(["0", "CIRCLE", "8", layer, "10", fmt(x), "20", fmt(y), "30", "0", "40", fmt(radius)])


def _append_shape(lines: list[str], shape: Shape, coord_scale: float) -> None:
    def scaled(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
        return [(x * coord_scale, y * coord_scale) for x, y in points]

    if isinstance(shape, Rect):
        _append_solid(lines, shape.layer, scaled(shape.points))
        return
    if isinstance(shape, Polygon):
        if len(shape.points) == 4:
            _append_solid(lines, shape.layer, scaled(shape.points))
        else:
            _append_polyline(lines, shape.layer, scaled(shape.points), closed=True)
        return
    if isinstance(shape, Boundary):
        points = scaled(shape.points + [shape.points[0]])
        for start, end in zip(points, points[1:], strict=False):
            lines.extend(["0", "LINE", "8", shape.layer, "10", fmt(start[0]), "20", fmt(start[1]), "30", "0"])
            lines.extend(["11", fmt(end[0]), "21", fmt(end[1]), "31", "0"])
        return
    if isinstance(shape, Via):
        _append_circle(lines, shape.layer, shape.x * coord_scale, shape.y * coord_scale, shape.radius * coord_scale)
        if shape.pad_diameter and shape.pad_layer:
            _append_circle(
                lines,
                shape.pad_layer,
                shape.x * coord_scale,
                shape.y * coord_scale,
                shape.pad_diameter / 2.0 * coord_scale,
            )
        return
    if isinstance(shape, Path):
        _append_polyline(lines, shape.layer, scaled(shape.points), closed=False)
        return
    raise TypeError(f"unsupported DXF shape type: {type(shape)!r}")


def write_dxf(path: FsPath, layout: Layout, *, coord_scale: float = 1.0, insunits: int = 4) -> None:
    """Write a small ADS-importable DXF.

    `coord_scale` converts layout coordinates to DXF coordinate values. Use
    `coord_scale=39.3700787402` and `insunits=0` only for legacy mil-coordinate
    import paths.
    """
    lines: list[str] = [
        "0",
        "SECTION",
        "2",
        "HEADER",
        "9",
        "$INSUNITS",
        "70",
        str(insunits),
        "0",
        "ENDSEC",
        "0",
        "SECTION",
        "2",
        "ENTITIES",
    ]
    for shape in layout.shapes:
        _append_shape(lines, shape, coord_scale)
    lines.extend(["0", "ENDSEC", "0", "EOF", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")

