"""HFSS-facing helpers for SIM layout JSON metadata."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from simads.config import name_with_stackup_token
from simads.geometry import Boundary, LayerMap, Layout, Polygon, Port, Rect, Via


def load_layout(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"layout JSON must contain an object: {path}")
    return data


def shape_to_geometry_object(shape: dict[str, Any]) -> Rect | Polygon | Via | Port | Boundary | None:
    kind = str(shape.get("kind") or "")
    metadata = dict(shape.get("metadata") if isinstance(shape.get("metadata"), dict) else {})
    if kind == "boundary":
        return Boundary(
            name=str(shape.get("name") or "boundary"),
            x=float(shape["x"]),
            y=float(shape["y"]),
            w=float(shape["w"]),
            h=float(shape["h"]),
            layer=str(shape.get("layer") or "EM_BOUNDARY"),
            metadata=metadata,
        )
    if kind == "via":
        return Via(
            name=str(shape.get("name") or "via"),
            layer=str(shape.get("layer") or "pcvia1"),
            x=float(shape["x"]),
            y=float(shape["y"]),
            diameter=float(shape["diameter"]),
            pad_diameter=float(shape["pad_diameter"]) if shape.get("pad_diameter") not in (None, "") else None,
            pad_layer=str(shape.get("pad_layer")) if shape.get("pad_layer") else None,
            metadata=metadata,
        )
    if kind == "port":
        return Port(
            name=str(shape.get("name") or "port"),
            number=int(shape.get("number") or 0),
            x=float(shape["x"]),
            y=float(shape["y"]),
            width=float(shape.get("width") or 0.0),
            layer=str(shape.get("layer") or "cond"),
            orientation_deg=float(shape.get("orientation_deg") or 0.0),
            reference=str(shape.get("reference")) if shape.get("reference") else None,
            metadata=metadata,
        )
    if all(key in shape for key in ("x", "y", "w", "h")):
        return Rect(
            name=str(shape.get("name") or kind or "rect"),
            layer=str(shape.get("layer") or "cond"),
            x=float(shape["x"]),
            y=float(shape["y"]),
            w=float(shape["w"]),
            h=float(shape["h"]),
            kind=kind if kind else "rect",
            metadata=metadata,
        )
    if isinstance(shape.get("points"), list):
        return Polygon(
            name=str(shape.get("name") or kind or "polygon"),
            layer=str(shape.get("layer") or "cond"),
            points=[(float(point[0]), float(point[1])) for point in shape["points"]],
            kind=kind if kind else "polygon",
            metadata=metadata,
        )
    return None


def layout_to_geometry(layout: dict[str, Any]) -> Layout:
    layers = [
        LayerMap(
            name=str(layer.get("name")),
            purpose=str(layer.get("purpose") or "drawing"),
            dxf_layer=str(layer.get("dxf_layer")) if layer.get("dxf_layer") else None,
        )
        for layer in layout.get("layers", [])
        if isinstance(layer, dict) and layer.get("name")
    ]
    shapes = [
        shape_obj
        for shape in layout.get("shapes", [])
        if isinstance(shape, dict)
        for shape_obj in [shape_to_geometry_object(shape)]
        if shape_obj is not None
    ]
    return Layout(
        layout_id=str(layout.get("layout_id") or "hfss_layout"),
        units=str(layout.get("units") or "mm"),
        layers=layers,
        shapes=shapes,
        metadata=dict(layout.get("metadata") if isinstance(layout.get("metadata"), dict) else {}),
    )


def configured_layout_id(layout: dict[str, Any]) -> str:
    layout_id = str(layout.get("layout_id") or "hfss_verdict")
    metadata = layout.get("metadata", {})
    if not isinstance(metadata, dict):
        return layout_id
    stackup_token = metadata.get("stackup_token") or metadata.get("stackup_id")
    if not stackup_token:
        return layout_id
    return name_with_stackup_token(layout_id, str(stackup_token))


def collect_layout_summary(layout: dict[str, Any]) -> dict[str, Any]:
    shapes = layout.get("shapes", [])
    ports = layout.get("ports", [])
    cond = [shape for shape in shapes if shape.get("layer") == "cond"]
    vias = [shape for shape in shapes if shape.get("kind") == "via"]
    boundary = next((shape for shape in shapes if shape.get("kind") == "boundary"), None)
    metadata = layout.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    return {
        "layout_id": layout.get("layout_id"),
        "configured_layout_id": configured_layout_id(layout),
        "units": layout.get("units"),
        "order": metadata.get("order"),
        "substrate": metadata.get("substrate"),
        "stackup_id": metadata.get("stackup_id"),
        "stackup_token": metadata.get("stackup_token"),
        "er": metadata.get("er"),
        "dielectric_height_mm": metadata.get("dielectric_height_mm"),
        "copper_thickness_mm": metadata.get("copper_thickness_mm"),
        "cond_shapes": len(cond),
        "vias": len(vias),
        "ports": len(ports),
        "boundary": boundary,
    }


__all__ = [
    "collect_layout_summary",
    "configured_layout_id",
    "layout_to_geometry",
    "load_layout",
    "shape_to_geometry_object",
]
