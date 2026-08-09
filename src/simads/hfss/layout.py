"""HFSS 3D Layout geometry builders."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from simads.hfss.ports import (
    BOTTOM_LAYER,
    GROUND_PLANE,
    TOP_LAYER,
    net_for_shape,
    resolve_gnd_boundary,
)


@dataclass(frozen=True)
class GeometryBuildOptions:
    gnd_boundary_mode: str = "em-boundary"
    signal_layer: str = TOP_LAYER
    reference_ground_layer: str = BOTTOM_LAYER
    via_top_layer: str = TOP_LAYER
    via_bottom_layer: str = BOTTOM_LAYER
    ground_plane_name: str = GROUND_PLANE

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "GeometryBuildOptions":
        signal = str(getattr(args, "signal_layer", None) or TOP_LAYER)
        reference = str(getattr(args, "reference_ground_layer", None) or BOTTOM_LAYER)
        return cls(
            gnd_boundary_mode=str(getattr(args, "gnd_boundary_mode", "em-boundary")),
            signal_layer=signal,
            reference_ground_layer=reference,
            via_top_layer=str(getattr(args, "via_top_layer", None) or signal),
            via_bottom_layer=str(getattr(args, "via_bottom_layer", None) or reference),
            ground_plane_name=str(getattr(args, "ground_plane_name", None) or GROUND_PLANE),
        )


def _geometry_options(options: GeometryBuildOptions | argparse.Namespace) -> GeometryBuildOptions:
    if isinstance(options, GeometryBuildOptions):
        return options
    return GeometryBuildOptions.from_args(options)


def _shape_net(shape: dict[str, Any], name: str | None) -> str:
    metadata = shape.get("metadata")
    if isinstance(metadata, dict) and metadata.get("net"):
        return str(metadata["net"])
    return net_for_shape(name)


def _target_ground_layer(shape: dict[str, Any], geometry: GeometryBuildOptions) -> str:
    metadata = shape.get("metadata")
    if isinstance(metadata, dict):
        target = metadata.get("target_layer")
        if target and target != "reference_ground_layer":
            return str(target)
    return geometry.reference_ground_layer


def _create_reference_ground_plane(app: Any, shape: dict[str, Any], geometry: GeometryBuildOptions) -> Any:
    layer = _target_ground_layer(shape, geometry)
    name = shape.get("name")
    if "points" in shape:
        return app.modeler.create_polygon(
            layer,
            [[float(x), float(y)] for x, y in shape["points"]],
            units="mm",
            name=name,
            net="GND",
        )
    return app.modeler.create_rectangle(
        layer,
        [shape["x"], shape["y"]],
        [shape["w"], shape["h"]],
        name=name,
        net="GND",
    )


def _has_explicit_reference_ground_plane(layout: dict[str, Any], geometry: GeometryBuildOptions) -> bool:
    for shape in layout.get("shapes", []):
        if not isinstance(shape, dict) or shape.get("kind") != "reference_ground_plane":
            continue
        if _target_ground_layer(shape, geometry) == geometry.reference_ground_layer:
            return True
    return False


def create_geometry(app: Any, layout: dict[str, Any], options: GeometryBuildOptions | argparse.Namespace) -> list[str]:
    geometry = _geometry_options(options)
    signal_layers = {"cond", geometry.signal_layer}
    names: list[str] = []
    metadata = layout.get("metadata", {})
    suppress_default_ground = bool(isinstance(metadata, dict) and metadata.get("suppress_default_reference_ground_plane"))
    boundary = None if suppress_default_ground else resolve_gnd_boundary(layout, geometry)
    gnd = None
    ground_by_layer: dict[str, Any] = {}
    if boundary and not _has_explicit_reference_ground_plane(layout, geometry):
        gnd = app.modeler.create_rectangle(
            geometry.reference_ground_layer,
            [boundary["x"], boundary["y"]],
            [boundary["w"], boundary["h"]],
            name=geometry.ground_plane_name,
            net="GND",
        )
        if gnd:
            names.append(gnd.name)
            ground_by_layer[geometry.reference_ground_layer] = gnd
    for shape in layout.get("shapes", []):
        kind = shape.get("kind")
        layer = shape.get("layer")
        if layer == "EM_BOUNDARY" or kind == "boundary":
            continue
        if kind == "reference_ground_cutout":
            # Cutouts must be materialized by the layout generator as actual
            # ground-plane geometry. HFSS replacement only reloads layout
            # primitives and never applies candidate-level boolean edits.
            continue
        if kind == "reference_ground_plane":
            obj = _create_reference_ground_plane(app, shape, geometry)
            if obj:
                names.append(obj.name)
                ground_by_layer[_target_ground_layer(shape, geometry)] = obj
            continue
        name = shape.get("name")
        if kind == "rect" and layer in signal_layers:
            obj = app.modeler.create_rectangle(
                geometry.signal_layer,
                [shape["x"], shape["y"]],
                [shape["w"], shape["h"]],
                name=name,
                net=_shape_net(shape, name),
            )
            if obj:
                names.append(obj.name)
        elif kind == "polygon" and layer in signal_layers:
            obj = app.modeler.create_polygon(
                geometry.signal_layer,
                [[float(x), float(y)] for x, y in shape["points"]],
                units="mm",
                name=name,
                net=_shape_net(shape, name),
            )
            if obj:
                names.append(obj.name)
        elif kind == "via":
            pad_d = float(shape.get("pad_diameter") or shape.get("diameter"))
            via_d = float(shape.get("diameter") or pad_d)
            pad = app.modeler.create_circle(
                geometry.signal_layer,
                float(shape["x"]),
                float(shape["y"]),
                pad_d / 2.0,
                name=f"{name}_pad",
                net="GND",
            )
            via = app.modeler.create_via(
                x=float(shape["x"]),
                y=float(shape["y"]),
                hole_diam=via_d,
                top_layer=geometry.via_top_layer,
                bot_layer=geometry.via_bottom_layer,
                name=name,
                net="GND",
            )
            if pad:
                names.append(pad.name)
            if via:
                names.append(via.name)
    return names


__all__ = ["GeometryBuildOptions", "create_geometry"]
