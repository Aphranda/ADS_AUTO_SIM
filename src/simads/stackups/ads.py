"""Pure ADS mapping helpers for stackup configs."""

from __future__ import annotations

from dataclasses import dataclass
import xml.etree.ElementTree as ET

from simads.config.stackups import StackupConfig, StackupLayerConfig

ADS_PERFECT_CONDUCTOR = "PERFECT_CONDUCTOR"
ADS_AIR = "AIR"


@dataclass(frozen=True)
class AdsViaLayerMap:
    name: str
    layer_id: int
    process_role: str
    layer_binding: str
    substrate_top_layer: str
    substrate_bottom_layer: str


@dataclass(frozen=True)
class AdsStackupLayerMap:
    conductor_layer_ids: dict[str, int]
    drill_layer: str
    drill_layer_id: int
    drill_process_role: str
    drill_layer_binding: str
    drill_substrate_top_layer: str
    drill_substrate_bottom_layer: str
    boundary_layer: str
    boundary_layer_id: int
    substrate_name: str


@dataclass(frozen=True)
class AdsTechLayerSpec:
    name: str
    number: int
    purpose: str = "drawing"
    role: str = "auxiliary"
    process_role: str = "CONDUCTOR"
    layer_binding: str = ""


def _active_via_layer_map(ads: dict[str, object], stackup: StackupConfig) -> AdsViaLayerMap:
    drill_layer = str(ads.get("drill_layer") or "").strip()
    if not drill_layer:
        raise ValueError(f"stackup {stackup.stackup_id} has no ads.drill_layer")
    drill_layer_id = int(ads.get("drill_layer_id", 24))
    via_layers = ads.get("via_layers")
    selected: dict[str, object] = {}
    if isinstance(via_layers, list):
        for item in via_layers:
            if isinstance(item, dict) and str(item.get("name") or "").strip() == drill_layer:
                selected = item
                break
    layer_id = int(selected.get("layer_id", drill_layer_id))
    process_role = str(
        selected.get("process_role")
        or ads.get("drill_layer_process_role")
        or "CONDUCTOR_VIA"
    ).strip()
    layer_binding = str(selected.get("layer_binding") or ads.get("drill_layer_binding") or "").strip()
    if not layer_binding:
        layer_binding = f"{stackup.geometry.via_top_layer} {stackup.geometry.via_bottom_layer}"
    substrate_top_layer = str(
        selected.get("substrate_top_layer") or stackup.geometry.via_top_layer
    ).strip()
    substrate_bottom_layer = str(
        selected.get("substrate_bottom_layer") or stackup.geometry.via_bottom_layer
    ).strip()
    return AdsViaLayerMap(
        name=drill_layer,
        layer_id=layer_id,
        process_role=process_role,
        layer_binding=layer_binding,
        substrate_top_layer=substrate_top_layer,
        substrate_bottom_layer=substrate_bottom_layer,
    )


def ads_stackup_layer_map(stackup: StackupConfig) -> AdsStackupLayerMap:
    raw = stackup.raw or {}
    ads = raw.get("ads")
    if not isinstance(ads, dict):
        raise ValueError(f"stackup {stackup.stackup_id} has no ads mapping")
    imported_layers = ads.get("imported_layers")
    if not isinstance(imported_layers, dict):
        raise ValueError(f"stackup {stackup.stackup_id} has no ads.imported_layers mapping")
    via = _active_via_layer_map(ads, stackup)
    boundary_layer = str(ads.get("boundary_layer") or "EM_BOUNDARY").strip()
    boundary_layer_id = int(ads.get("boundary_layer_id", 1004))
    substrate_name = str(ads.get("expected_substrate_name") or stackup.stackup_id).strip()
    return AdsStackupLayerMap(
        conductor_layer_ids={str(name): int(value) for name, value in imported_layers.items()},
        drill_layer=via.name,
        drill_layer_id=via.layer_id,
        drill_process_role=via.process_role,
        drill_layer_binding=via.layer_binding,
        drill_substrate_top_layer=via.substrate_top_layer,
        drill_substrate_bottom_layer=via.substrate_bottom_layer,
        boundary_layer=boundary_layer,
        boundary_layer_id=boundary_layer_id,
        substrate_name=substrate_name,
    )


def ads_tech_layer_specs(stackup: StackupConfig) -> list[AdsTechLayerSpec]:
    layer_map = ads_stackup_layer_map(stackup)
    specs = [
        AdsTechLayerSpec(name=name, number=number, role="conductor", process_role="CONDUCTOR")
        for name, number in sorted(layer_map.conductor_layer_ids.items(), key=lambda item: item[1])
    ]
    specs.append(
        AdsTechLayerSpec(
            name=layer_map.drill_layer,
            number=layer_map.drill_layer_id,
            role="conductor_via",
            process_role=layer_map.drill_process_role,
            layer_binding=layer_map.drill_layer_binding,
        )
    )
    specs.append(
        AdsTechLayerSpec(
            name=layer_map.boundary_layer,
            number=layer_map.boundary_layer_id,
            role="boundary",
            process_role="BOUNDARY",
        )
    )
    return specs


def _fmt_micron(mm: float) -> str:
    text = f"{mm * 1000.0:.6f}".rstrip("0").rstrip(".")
    return text or "0"


def _stack_layers_bottom_to_top(stackup: StackupConfig) -> list[StackupLayerConfig]:
    return list(stackup.layers_bottom_to_top)


def _conductor_layers_bottom_to_top(stackup: StackupConfig) -> list[StackupLayerConfig]:
    return [layer for layer in _stack_layers_bottom_to_top(stackup) if layer.kind == "conductor"]


def _dielectric_layers_bottom_to_top(stackup: StackupConfig) -> list[StackupLayerConfig]:
    return [layer for layer in _stack_layers_bottom_to_top(stackup) if layer.kind == "dielectric"]


def _interface_index_by_layer(stackup: StackupConfig) -> dict[str, int]:
    return {layer.name: index for index, layer in enumerate(_conductor_layers_bottom_to_top(stackup))}


def build_ads_substrate_tree(stackup: StackupConfig) -> ET.ElementTree:
    layer_map = ads_stackup_layer_map(stackup)
    root = ET.Element("SubstrateModel")
    stack = ET.SubElement(
        root,
        "stack",
        {
            "BAL_NUM": "0",
            "BAL_TYPE": "NONE",
            "PURPOSE_TREATMENT": "USE_ALL_EXCEPT_SPECIFIED",
            "SPECIFIED_PURPOSES": "",
        },
    )
    ET.SubElement(stack, "material", {"BAL_NUM": "0", "BAL_TYPE": "INHERIT", "materialname": ADS_AIR})

    conductors = _conductor_layers_bottom_to_top(stackup)
    dielectrics = _dielectric_layers_bottom_to_top(stackup)
    if len(dielectrics) != len(conductors) - 1:
        raise ValueError(
            f"stackup {stackup.stackup_id} must have one dielectric between adjacent conductors "
            f"(conductors={len(conductors)}, dielectrics={len(dielectrics)})"
        )

    for index, conductor in enumerate(conductors):
        layer_id = layer_map.conductor_layer_ids.get(conductor.name)
        if layer_id is None:
            raise ValueError(f"ADS layer id missing for conductor layer {conductor.name}")
        interface_attrs = {
            "BAL_NUM": "0",
            "BAL_TYPE": "INHERIT",
            "materialname": ADS_PERFECT_CONDUCTOR,
            "thick": _fmt_micron(conductor.thickness_mm),
            "thickunit": "micron",
        }
        ET.SubElement(stack, "interface", interface_attrs)
        if index < len(dielectrics):
            dielectric = dielectrics[index]
            ET.SubElement(
                stack,
                "material",
                {
                    "BAL_NUM": "0",
                    "BAL_TYPE": "INHERIT",
                    "materialname": dielectric.material,
                    "thick": _fmt_micron(dielectric.thickness_mm),
                    "thickunit": "micron",
                },
            )
    ET.SubElement(stack, "material", {"BAL_NUM": "0", "BAL_TYPE": "INHERIT", "materialname": ADS_AIR})

    layers = ET.SubElement(root, "layers")
    for index, conductor in enumerate(conductors):
        ET.SubElement(
            layers,
            "layer",
            {
                "angle": "90",
                "bottomrough": "",
                "expand": "0",
                "index": str(index),
                "layer": str(layer_map.conductor_layer_ids[conductor.name]),
                "materialname": ADS_PERFECT_CONDUCTOR,
                "negative": "0",
                "pinsOnly": "0",
                "precedence": "1" if conductor.name == stackup.geometry.signal_layer else "0",
                "processRole": "1",
                "sheet": "0",
                "subtype": "0",
                "thick": _fmt_micron(conductor.thickness_mm),
                "thickunit": "micron",
                "toprough": "",
            },
        )

    indexes = _interface_index_by_layer(stackup)
    via_index1 = indexes[layer_map.drill_substrate_bottom_layer]
    via_index2 = indexes[layer_map.drill_substrate_top_layer]
    if via_index1 > via_index2:
        via_index1, via_index2 = via_index2, via_index1
    vias = ET.SubElement(root, "vias")
    ET.SubElement(
        vias,
        "via",
        {
            "index1": str(via_index1),
            "index2": str(via_index2),
            "layer": str(layer_map.drill_layer_id),
            "materialname": ADS_PERFECT_CONDUCTOR,
            "platingdielectricmaterial": ADS_AIR,
            "platingenabled": "0",
            "platingthickness": "",
            "platingthicknessunit": "micron",
            "precedence": "0",
            "processRole": "4",
            "rough": "",
            "subtype": "0",
        },
    )
    ET.SubElement(root, "substrates")
    return ET.ElementTree(root)


def xml_text(root: ET.Element, doctype: str | None = None, declaration: bool = False) -> str:
    ET.indent(root, space="    ")
    text = ET.tostring(root, encoding="unicode")
    parts: list[str] = []
    if declaration:
        parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    if doctype:
        parts.append(doctype)
    parts.append(text)
    return "\n".join(parts) + "\n"


def ads_substrate_text(stackup: StackupConfig) -> str:
    return xml_text(build_ads_substrate_tree(stackup).getroot(), "<!DOCTYPE Substrate>")


def ensure_dielectric_materials(root: ET.Element, stackup: StackupConfig) -> bool:
    dielectrics = root.find("Dielectrics")
    if dielectrics is None:
        dielectrics = ET.SubElement(root, "Dielectrics")
        changed = True
    else:
        changed = False
    existing = {elem.get("name"): elem for elem in dielectrics.findall("Dielectric")}
    for material in stackup.materials.values():
        if material.kind != "dielectric":
            continue
        attrs = {
            "electron_path": "",
            "er_imag": "",
            "er_loss": "" if material.loss_tangent is None else f"{material.loss_tangent:g}",
            "er_real": "" if material.er is None else f"{material.er:g}",
            "heat_capacity": "",
            "highfreq": "1 THz",
            "loss_type": "1",
            "lowfreq": "1 KHz",
            "mur_imag": "",
            "mur_real": "1",
            "name": material.name,
            "thermal_conductivity": "",
            "thermal_conductivity_in_z": "",
            "valuefreq": "1 GHz",
        }
        elem = existing.get(material.name)
        if elem is None:
            ET.SubElement(dielectrics, "Dielectric", attrs)
            changed = True
            continue
        for key, value in attrs.items():
            if elem.get(key) != value:
                elem.set(key, value)
                changed = True
    return changed


def ensure_lpp_layers(root: ET.Element, stackup: StackupConfig) -> bool:
    desired = {
        stackup.geometry.signal_layer: ("18", "15624784", "109"),
        stackup.geometry.reference_ground_layer: ("18", "16776960", "109"),
        stackup.geometry.via_bottom_layer: ("6", "9364974", "180"),
        "ETCH_INNER2": ("18", "3050327", "109"),
    }
    layer_map = ads_stackup_layer_map(stackup)
    desired[layer_map.drill_layer] = ("71", "12713921", "255")
    desired[layer_map.boundary_layer] = ("13", "16759807", "255")

    existing = {elem.get("layer"): elem for elem in root.findall("LPP")}
    changed = False
    for layer, (fill, rgb, alpha) in desired.items():
        attrs = {
            "alpha": alpha,
            "fill": fill,
            "layer": layer,
            "line": "0",
            "mode": "1",
            "protect": "0",
            "purpose": "drawing",
            "rgb": rgb,
            "visible": "1",
        }
        elem = existing.get(layer)
        if elem is None:
            ET.SubElement(root, "LPP", attrs)
            changed = True
            continue
        for key, value in attrs.items():
            if elem.get(key) != value:
                elem.set(key, value)
                changed = True
    return changed


def ensure_display_layers(root: ET.Element, stackup: StackupConfig) -> bool:
    order = root.find("Lpp_Display_Order")
    if order is None:
        order = ET.SubElement(root, "Lpp_Display_Order", {"order": "0"})
        changed = True
    else:
        changed = False
    existing = {elem.get("name") for elem in order.findall("LPP")}
    layer_map = ads_stackup_layer_map(stackup)
    names = [
        f"{stackup.geometry.signal_layer}:drawing",
        f"{stackup.geometry.reference_ground_layer}:drawing",
        "ETCH_INNER2:drawing",
        f"{stackup.geometry.via_bottom_layer}:drawing",
        f"{layer_map.drill_layer}:drawing",
        f"{layer_map.boundary_layer}:drawing",
    ]
    for name in names:
        if name not in existing:
            ET.SubElement(order, "LPP", {"name": name})
            changed = True
    return changed


__all__ = [
    "ADS_AIR",
    "ADS_PERFECT_CONDUCTOR",
    "AdsStackupLayerMap",
    "AdsTechLayerSpec",
    "AdsViaLayerMap",
    "ads_stackup_layer_map",
    "ads_substrate_text",
    "ads_tech_layer_specs",
    "build_ads_substrate_tree",
    "ensure_dielectric_materials",
    "ensure_display_layers",
    "ensure_lpp_layers",
    "xml_text",
]
