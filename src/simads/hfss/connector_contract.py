"""Connector fixture metadata contracts for HFSS workflows."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from simads.hfss.connector import FIXTURE_TYPE as MICROSTRIP_CONNECTOR_FIXTURE_TYPE
from simads.hfss.connector import SINGLE_CONNECTOR_FIXTURE_TYPE
from simads.hfss.ports import BOTTOM_LAYER, port_reference_name

CONNECTOR_FIXTURE_TYPES = {MICROSTRIP_CONNECTOR_FIXTURE_TYPE, SINGLE_CONNECTOR_FIXTURE_TYPE}


def is_connector_fixture(layout: dict[str, Any]) -> bool:
    return layout.get("metadata", {}).get("fixture_type") in CONNECTOR_FIXTURE_TYPES


def connector_params_json(args: argparse.Namespace, metadata: dict[str, Any]) -> Path | None:
    explicit = getattr(args, "connector_params_json", None)
    if explicit is not None:
        return explicit
    metadata_path = metadata.get("connector_params_json")
    if metadata_path:
        return Path(str(metadata_path))
    layout_path = getattr(args, "layout", None)
    if layout_path is None:
        return None
    layout_path = Path(layout_path)
    name = layout_path.name
    if name.endswith("_layout.json"):
        inferred = layout_path.with_name(f"{name.removesuffix('_layout.json')}_params.json")
        if inferred.exists():
            return inferred
    return None


def connector_port_reference_name(args: argparse.Namespace, metadata: dict[str, Any]) -> str:
    explicit = getattr(args, "port_reference_name", None)
    if explicit:
        return str(explicit)
    layer = metadata.get("reference_ground_layer") or getattr(args, "reference_ground_layer", None)
    primitive = metadata.get("ground_plane_name") or getattr(args, "ground_plane_name", None)
    if layer or primitive:
        return f"GND:{layer or BOTTOM_LAYER}:{primitive or 'hfss_ground_plane'}"
    return port_reference_name(args)


def connector_fixture_metadata(args: argparse.Namespace, layout: dict[str, Any]) -> dict[str, Any]:
    metadata = layout.get("metadata", {})
    fixture_type = metadata.get("fixture_type")
    if fixture_type not in CONNECTOR_FIXTURE_TYPES:
        return {}
    params_json = connector_params_json(args, metadata)
    model_path = getattr(args, "connector_hfss_model_path", None) or metadata.get("connector_hfss_model_path")
    model_version = getattr(args, "connector_hfss_model_version", None) or metadata.get("connector_hfss_model_version")
    model_hash = getattr(args, "connector_hfss_model_hash", None) or metadata.get("connector_hfss_model_hash")
    port_mapping = getattr(args, "connector_port_mapping", None) or metadata.get("connector_port_mapping")
    stackup_config = getattr(args, "stackup_config", None) or metadata.get("stackup_config")
    port_deembed_mm = float(metadata.get("port_deembed_mm", 0.0) or 0.0)
    reference_plane_offset_mm = float(metadata.get("reference_plane_offset_mm", 0.0) or 0.0)
    return {
        "fixture_type": fixture_type,
        "connector_model_version": metadata.get("connector_model_version"),
        "connector_route": metadata.get("connector_route"),
        "connector_type": metadata.get("connector_type"),
        "microstrip_connector_layout_json": str(getattr(args, "layout", "")),
        "connector_params_json": str(params_json) if params_json is not None else None,
        "line_w_mm": metadata.get("line_w_mm"),
        "line_l_mm": metadata.get("line_l_mm"),
        "reference_plane_offset_mm": reference_plane_offset_mm,
        "port_deembed_mm": port_deembed_mm,
        "connector_region_bbox_mm": metadata.get("connector_region_bbox_mm"),
        "connector_port_contract": {
            "route": str(getattr(args, "route", "custom") or "custom"),
            "port_type": getattr(args, "port_type", None),
            "gnd_boundary_mode": getattr(args, "gnd_boundary_mode", None),
            "reference_ground_ports": bool(getattr(args, "reference_ground_ports", False)),
            "reference_name": connector_port_reference_name(args, metadata),
            "renormalize": True,
            "renormalize_impedance_ohm": 50.0,
            "reference_plane_offset_mm": reference_plane_offset_mm,
            "port_deembed_mm": port_deembed_mm,
            "deembed_enabled": port_deembed_mm > 0.0,
        },
        "stackup_config": str(stackup_config) if stackup_config is not None else None,
        "connector_hfss_model_path": str(model_path) if model_path is not None else None,
        "connector_hfss_model_version": model_version,
        "connector_hfss_model_hash": model_hash,
        "connector_port_mapping": port_mapping,
    }


__all__ = [
    "CONNECTOR_FIXTURE_TYPES",
    "connector_fixture_metadata",
    "connector_params_json",
    "connector_port_reference_name",
    "is_connector_fixture",
]
