"""HFSS 3D Layout stackup, material, and extent helpers."""

from __future__ import annotations

import argparse
from typing import Any

from simads.config.stackups import StackupConfig
from simads.hfss.ports import BOTTOM_LAYER, TOP_LAYER

DIELECTRIC_LAYER = "FR4_CORE"
FR4_MATERIAL = "SIMADS_FR4_ER4P6_TD02"


def mm(value: float) -> str:
    return f"{value:.9g}mm"


def ensure_material(app: Any, er: float, loss_tangent: float) -> None:
    material = app.materials.add_material(
        FR4_MATERIAL,
        properties={
            "permittivity": er,
            "dielectric_loss_tangent": loss_tangent,
            "conductivity": 0,
        },
    )
    if material:
        material.permittivity = er
        material.dielectric_loss_tangent = loss_tangent
        material.conductivity = 0
        material.update()


def ensure_stackup_materials(app: Any, stackup: StackupConfig) -> None:
    for material in stackup.materials.values():
        if material.kind != "dielectric":
            continue
        if material.er is None:
            raise ValueError(f"dielectric material {material.name} requires er")
        loss_tangent = float(material.loss_tangent if material.loss_tangent is not None else 0.0)
        created = app.materials.add_material(
            material.name,
            properties={
                "permittivity": float(material.er),
                "dielectric_loss_tangent": loss_tangent,
                "conductivity": 0,
            },
        )
        if created:
            created.permittivity = float(material.er)
            created.dielectric_loss_tangent = loss_tangent
            created.conductivity = 0
            created.update()


def _hfss_material_name(stackup: StackupConfig, material_name: str) -> str:
    material = stackup.materials[material_name]
    return material.hfss_material or material.name


def _hfss_layer_type(kind: str) -> str:
    if kind == "conductor":
        return "signal"
    if kind == "dielectric":
        return "dielectric"
    raise ValueError(f"unsupported stackup layer kind: {kind}")


def clear_layers(app: Any) -> None:
    layers = app.modeler.layers
    for layer in list(layers.all_layers):
        try:
            layers.remove_layer(layer)
        except Exception:
            pass


def reset_stackup(app: Any, core_h_mm: float, cu_t_mm: float) -> None:
    layers = app.modeler.layers
    clear_layers(app)
    layers.add_layer(BOTTOM_LAYER, layer_type="signal", thickness=mm(cu_t_mm), elevation=mm(0), material="copper")
    layers.add_layer(
        DIELECTRIC_LAYER,
        layer_type="dielectric",
        thickness=mm(core_h_mm),
        elevation=mm(cu_t_mm),
        material=FR4_MATERIAL,
    )
    layers.add_layer(
        TOP_LAYER,
        layer_type="signal",
        thickness=mm(cu_t_mm),
        elevation=mm(cu_t_mm + core_h_mm),
        material="copper",
    )


def reset_stackup_from_config(app: Any, stackup: StackupConfig) -> None:
    layers = app.modeler.layers
    clear_layers(app)
    elevation_mm = 0.0
    for layer in stackup.layers_bottom_to_top:
        layers.add_layer(
            layer.name,
            layer_type=_hfss_layer_type(layer.kind),
            thickness=mm(layer.thickness_mm),
            elevation=mm(elevation_mm),
            material=_hfss_material_name(stackup, layer.material),
        )
        elevation_mm += layer.thickness_mm


def configure_hfss_extents(app: Any, args: argparse.Namespace) -> bool:
    if not args.configure_extents:
        return False
    app.odesign.EditHfssExtents(
        [
            "NAME:HfssExportInfo",
            "DielExtentType:=",
            args.diel_extent_type,
            "DielExt:=",
            ["Ext:=", str(args.diel_horizontal_padding), "Dim:=", False],
            "HonorUserDiel:=",
            args.diel_honor_primitives,
            "Include3D:=",
            args.include_3d_subdesigns,
            "ExtentType:=",
            args.airbox_extent_type,
            "TruncAtGnd:=",
            args.truncate_airbox_at_ground,
            "AirHorExt:=",
            ["Ext:=", str(args.airbox_horizontal_padding), "Dim:=", False],
            "AirPosZExt:=",
            ["Ext:=", str(args.airbox_vertical_positive_padding), "Dim:=", False],
            "AirNegZExt:=",
            ["Ext:=", str(args.airbox_vertical_negative_padding), "Dim:=", False],
            "SyncZExt:=",
            args.airbox_vertical_sync,
            "OpenRegionType:=",
            args.open_region_type,
            "UseRadBound:=",
            args.use_radiation_boundary,
            "PMLVisible:=",
            args.pml_visible,
            "OperFreq:=",
            f"{args.open_region_frequency_ghz}GHz",
            "RadLvl:=",
            args.radiation_factor,
            "UseStackupForZExtFact:=",
            True,
        ]
    )
    return True


__all__ = [
    "DIELECTRIC_LAYER",
    "FR4_MATERIAL",
    "configure_hfss_extents",
    "ensure_stackup_materials",
    "ensure_material",
    "mm",
    "reset_stackup",
    "reset_stackup_from_config",
]
