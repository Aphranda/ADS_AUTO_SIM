"""PCB stackup configuration loader."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class StackupMaterialConfig:
    name: str
    kind: str
    hfss_material: str | None = None
    er: float | None = None
    loss_tangent: float | None = None
    display_name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "hfss_material": self.hfss_material,
            "er": self.er,
            "loss_tangent": self.loss_tangent,
            "display_name": self.display_name,
        }


@dataclass(frozen=True)
class StackupLayerConfig:
    name: str
    kind: str
    material: str
    thickness_mm: float
    role: str | None = None
    thickness_mil: float | None = None
    ads_layer_id: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "material": self.material,
            "thickness_mm": self.thickness_mm,
            "role": self.role,
            "thickness_mil": self.thickness_mil,
            "ads_layer_id": self.ads_layer_id,
        }


@dataclass(frozen=True)
class StackupGeometryConfig:
    signal_layer: str
    reference_ground_layer: str
    via_top_layer: str
    via_bottom_layer: str
    ground_plane_name: str = "hfss_ground_plane"

    def to_dict(self) -> dict[str, str]:
        return {
            "signal_layer": self.signal_layer,
            "reference_ground_layer": self.reference_ground_layer,
            "via_top_layer": self.via_top_layer,
            "via_bottom_layer": self.via_bottom_layer,
            "ground_plane_name": self.ground_plane_name,
        }


@dataclass(frozen=True)
class StackupConfig:
    stackup_id: str
    name: str
    materials: dict[str, StackupMaterialConfig]
    layers_bottom_to_top: list[StackupLayerConfig]
    geometry: StackupGeometryConfig
    source: str | None = None
    notes: str | None = None
    vendor: str | None = None
    board_code: str | None = None
    finished_thickness_mm: float | None = None
    raw: dict[str, Any] | None = None

    @property
    def total_thickness_mm(self) -> float:
        return sum(layer.thickness_mm for layer in self.layers_bottom_to_top)

    @property
    def primary_dielectric(self) -> StackupMaterialConfig | None:
        for layer in reversed(self.layers_bottom_to_top):
            if layer.kind == "dielectric":
                return self.materials.get(layer.material)
        return None

    @property
    def signal_to_reference_height_mm(self) -> float:
        layers = self.layers_bottom_to_top
        ref_idx = next(i for i, layer in enumerate(layers) if layer.name == self.geometry.reference_ground_layer)
        sig_idx = next(i for i, layer in enumerate(layers) if layer.name == self.geometry.signal_layer)
        if ref_idx >= sig_idx:
            raise ValueError("reference_ground_layer must be below signal_layer")
        return sum(layer.thickness_mm for layer in layers[ref_idx + 1 : sig_idx])

    def to_dict(self) -> dict[str, Any]:
        return {
            "stackup_id": self.stackup_id,
            "name": self.name,
            "vendor": self.vendor,
            "board_code": self.board_code,
            "finished_thickness_mm": self.finished_thickness_mm,
            "total_thickness_mm": self.total_thickness_mm,
            "signal_to_reference_height_mm": self.signal_to_reference_height_mm,
            "source": self.source,
            "notes": self.notes,
            "materials": {name: material.to_dict() for name, material in self.materials.items()},
            "layers_bottom_to_top": [layer.to_dict() for layer in self.layers_bottom_to_top],
            "geometry": self.geometry.to_dict(),
        }


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_stackups_dir() -> Path:
    return repo_root() / "config" / "stackups"


def default_stackup_config_path(stackup_id: str) -> Path:
    return default_stackups_dir() / f"{stackup_id}.json"


def _optional_float(value: object) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def stackup_from_mapping(data: dict[str, Any]) -> StackupConfig:
    materials_raw = data.get("materials")
    layers_raw = data.get("layers_bottom_to_top")
    geometry_raw = data.get("geometry")
    if not isinstance(materials_raw, dict):
        raise ValueError("stackup config must contain a materials object")
    if not isinstance(layers_raw, list) or not layers_raw:
        raise ValueError("stackup config must contain non-empty layers_bottom_to_top")
    if not isinstance(geometry_raw, dict):
        raise ValueError("stackup config must contain a geometry object")

    materials = {
        str(name): StackupMaterialConfig(
            name=str(name),
            kind=str(material.get("kind", "")),
            hfss_material=str(material["hfss_material"]) if material.get("hfss_material") else None,
            er=_optional_float(material.get("er")),
            loss_tangent=_optional_float(material.get("loss_tangent")),
            display_name=str(material["display_name"]) if material.get("display_name") else None,
        )
        for name, material in materials_raw.items()
        if isinstance(material, dict)
    }
    layers = [
        StackupLayerConfig(
            name=str(layer["name"]),
            kind=str(layer["kind"]),
            material=str(layer["material"]),
            thickness_mm=float(layer["thickness_mm"]),
            role=str(layer["role"]) if layer.get("role") else None,
            thickness_mil=_optional_float(layer.get("thickness_mil")),
            ads_layer_id=int(layer["ads_layer_id"]) if layer.get("ads_layer_id") is not None else None,
        )
        for layer in layers_raw
    ]
    known_layers = {layer.name for layer in layers}
    for required in ("signal_layer", "reference_ground_layer", "via_top_layer", "via_bottom_layer"):
        if str(geometry_raw[required]) not in known_layers:
            raise ValueError(f"geometry.{required} references unknown stackup layer: {geometry_raw[required]}")
    missing_materials = sorted({layer.material for layer in layers if layer.material not in materials})
    if missing_materials:
        raise ValueError(f"stackup layers reference unknown materials: {missing_materials}")

    geometry = StackupGeometryConfig(
        signal_layer=str(geometry_raw["signal_layer"]),
        reference_ground_layer=str(geometry_raw["reference_ground_layer"]),
        via_top_layer=str(geometry_raw["via_top_layer"]),
        via_bottom_layer=str(geometry_raw["via_bottom_layer"]),
        ground_plane_name=str(geometry_raw.get("ground_plane_name", "hfss_ground_plane")),
    )
    config = StackupConfig(
        stackup_id=str(data["stackup_id"]),
        name=str(data.get("name", data["stackup_id"])),
        vendor=str(data["vendor"]) if data.get("vendor") else None,
        board_code=str(data["board_code"]) if data.get("board_code") else None,
        finished_thickness_mm=_optional_float(data.get("finished_thickness_mm")),
        source=str(data["source"]) if data.get("source") else None,
        notes=str(data["notes"]) if data.get("notes") else None,
        materials=materials,
        layers_bottom_to_top=layers,
        geometry=geometry,
        raw=data,
    )
    _ = config.signal_to_reference_height_mm
    return config


def load_stackup_config(path: Path) -> StackupConfig:
    return stackup_from_mapping(json.loads(path.read_text(encoding="utf-8-sig")))


__all__ = [
    "StackupConfig",
    "StackupGeometryConfig",
    "StackupLayerConfig",
    "StackupMaterialConfig",
    "default_stackup_config_path",
    "default_stackups_dir",
    "load_stackup_config",
    "stackup_from_mapping",
]
