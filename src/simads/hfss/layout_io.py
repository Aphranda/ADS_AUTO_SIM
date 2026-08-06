"""HFSS-facing helpers for SIM layout JSON metadata."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from simads.config import name_with_stackup_token


def load_layout(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"layout JSON must contain an object: {path}")
    return data


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


__all__ = ["collect_layout_summary", "configured_layout_id", "load_layout"]
