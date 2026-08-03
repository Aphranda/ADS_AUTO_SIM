#!/usr/bin/env python3
"""Clone a known-good ADS EM Setup view to a new imported cell.

This is a pragmatic bridge for the filter optimization loop: keep the proven
FEM setup from the V3 cell, clone it to a new DXF-imported cell, and patch the
cell/dataset/frequency references.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

_TOOLS_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC_ROOT = _REPO_ROOT / "src"
for _path in (_TOOLS_ROOT, _SRC_ROOT):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from ads_profiles import profile_names, resolve_library, resolve_substrate, resolve_substrate_library, resolve_workspace
from simads.ads.layout import load_p1_p2_locations
from simads.ads.workspace import find_cell_dir
from simads.safety import AdsWriteContext, guard_directory_delete, validate_ads_cell_write

DEFAULT_TEMPLATE_CELL = "interdigital_9o_ro4350b_508um_v3_wide_mm_coords"
DEFAULT_SETUP_VIEW = "em%Setup"


def log(message: str) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    print(line, flush=True)
    log_path = os.environ.get("ADS_FLOW_LOG")
    if log_path:
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        with Path(log_path).open("a", encoding="utf-8") as fp:
            fp.write(line + "\n")


def replace_text(root: ET.Element, old: str, new: str) -> None:
    for elem in root.iter():
        if elem.text and old in elem.text:
            elem.text = elem.text.replace(old, new)
        if elem.tail and old in elem.tail:
            elem.tail = elem.tail.replace(old, new)


def set_first(root: ET.Element, tag: str, value: str) -> None:
    elem = root.find(f".//{tag}")
    if elem is not None:
        elem.text = value


def set_all(root: ET.Element, tag: str, value: str) -> None:
    for elem in root.findall(f".//{tag}"):
        elem.text = value


def first_substrate_name(search_dirs: list[Path], root: ET.Element) -> str:
    lib_subst = root.findtext(".//libSubstName")
    if lib_subst:
        subst_name = lib_subst.split(":", 1)[-1]
        return Path(subst_name).stem

    for search_dir in search_dirs:
        subst_files = sorted(search_dir.glob("*.subst"))
        if subst_files:
            return subst_files[0].stem

    return "tech"


def substrate_name_from_params(params_path: Path | None) -> str | None:
    if params_path is None:
        return None
    try:
        data = json.loads(params_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    params = data.get("parameters")
    if not isinstance(params, dict):
        return None
    substrate = str(params.get("substrate", "")).strip()
    return substrate or None


def split_substrate_ref(substrate: str | None) -> tuple[str | None, str | None]:
    if not substrate:
        return (None, None)
    if ":" in substrate:
        lib, name = substrate.split(":", 1)
        return (lib or None, Path(name).stem or name)
    return (None, Path(substrate).stem or substrate)


def load_ads_port_layer_context(params_path: Path | None) -> dict[str, object]:
    if params_path is None:
        return {}
    try:
        data = json.loads(params_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    params = data.get("parameters")
    if not isinstance(params, dict):
        return {}

    context: dict[str, object] = {}
    signal_layer = str(params.get("signal_layer") or params.get("metal_layer") or "").strip()
    reference_layer = str(params.get("reference_ground_layer") or params.get("ground_layer") or "").strip()
    if signal_layer:
        context["signal_layer"] = signal_layer
    if reference_layer:
        context["reference_ground_layer"] = reference_layer

    stackup_path_raw = params.get("stackup_config")
    if stackup_path_raw:
        stackup_path = Path(str(stackup_path_raw))
        if not stackup_path.is_absolute():
            stackup_path = _REPO_ROOT / stackup_path
        try:
            stackup = json.loads(stackup_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            stackup = {}
        geometry = stackup.get("geometry", {}) if isinstance(stackup, dict) else {}
        if isinstance(geometry, dict):
            context.setdefault("signal_layer", str(geometry.get("signal_layer") or "").strip())
            context.setdefault("reference_ground_layer", str(geometry.get("reference_ground_layer") or "").strip())
        for layer in stackup.get("layers_bottom_to_top", []) if isinstance(stackup, dict) else []:
            if not isinstance(layer, dict):
                continue
            name = str(layer.get("name") or "").strip()
            layer_id = layer.get("ads_layer_id")
            if layer_id is None:
                continue
            if name == context.get("signal_layer"):
                context["signal_layer_num"] = int(layer_id)
            if name == context.get("reference_ground_layer"):
                context["reference_ground_layer_num"] = int(layer_id)

    return {key: value for key, value in context.items() if value not in ("", None)}


def set_pin_snapshot(
    root: ET.Element,
    pin_name: str,
    x_mm: float,
    y_mm: float,
    *,
    layer_name: str | None = None,
    layer_num: int | None = None,
) -> None:
    for pin in root.findall(".//Pin"):
        name = pin.findtext("pinName")
        if name != pin_name:
            continue
        shape = pin.find(".//PinShapeDef")
        item = shape.find("./points/stdItem") if shape is not None else None
        if item is not None:
            item.text = f"{x_mm / 1000.0:.9g}:{y_mm / 1000.0:.9g}"
        if shape is not None and layer_name:
            layer_id_name = shape.find("./layerIdName")
            if layer_id_name is not None:
                layer_id_name.text = f"{layer_name}:drawing"
            if layer_num is not None:
                layer_num_elem = shape.find("./layerNum")
                if layer_num_elem is not None:
                    layer_num_elem.text = str(layer_num)


def set_port_gnd_layer(root: ET.Element, gnd_layer: str | None, gnd_layer_num: int | None = None) -> str | None:
    if not gnd_layer and gnd_layer_num is None:
        return None
    gnd_layer_token = str(gnd_layer_num) if gnd_layer_num is not None else str(gnd_layer)
    if not gnd_layer_token:
        return None
    for port in root.findall(".//PortView/Ports/Port"):
        elem = port.find("./gndLayer")
        if elem is None:
            elem = ET.SubElement(port, "gndLayer")
        elem.text = gnd_layer_token
    return gnd_layer_token


def ensure_child(parent: ET.Element, tag: str) -> ET.Element:
    child = parent.find(f"./{tag}")
    if child is None:
        child = ET.SubElement(parent, tag)
    return child


def set_single_std_item(parent: ET.Element, tag: str, value: str) -> None:
    container = ensure_child(parent, tag)
    for child in list(container):
        container.remove(child)
    item = ET.SubElement(container, "stdItem")
    item.text = value


def set_port_pin_bindings(root: ET.Element) -> None:
    for port in root.findall(".//PortView/Ports/Port"):
        port_name = (port.findtext("./portName") or "").strip()
        if not port_name:
            continue
        set_single_std_item(port, "PlusPinNames", port_name)
        set_single_std_item(port, "MinusPinNames", "::__GND__")


def load_port_locations(params_path: Path) -> tuple[tuple[float, float], tuple[float, float]]:
    return load_p1_p2_locations(params_path)


def patch_port_editor_reference_fields(
    root: ET.Element,
    params_path: Path | None,
    *,
    signal_layer: str | None,
    signal_layer_num: int | None,
    reference_ground_layer: str | None,
    reference_ground_layer_num: int | None,
) -> str | None:
    gnd_layer_token = set_port_gnd_layer(
        root,
        reference_ground_layer,
        reference_ground_layer_num,
    )
    set_port_pin_bindings(root)

    if params_path is not None:
        p1, p2 = load_port_locations(params_path)
        set_pin_snapshot(
            root,
            "P1",
            *p1,
            layer_name=signal_layer,
            layer_num=signal_layer_num,
        )
        set_pin_snapshot(
            root,
            "P2",
            *p2,
            layer_name=signal_layer,
            layer_num=signal_layer_num,
        )

    return gnd_layer_token


def _add_text(parent: ET.Element, tag: str, text: str) -> ET.Element:
    elem = ET.SubElement(parent, tag)
    elem.text = text
    return elem


def _add_gui_pin(
    pins: ET.Element,
    *,
    name: str,
    number: int,
    signal_layer: str | None,
    signal_layer_num: int | None,
) -> None:
    pin = ET.SubElement(pins, "Pin")
    _add_text(pin, "pinName", name)
    _add_text(pin, "netName", name)
    _add_text(pin, "pinNum", str(number))
    _add_text(pin, "toolInfo", "")
    _add_text(pin, "compInfo", "")
    shapes = ET.SubElement(pin, "shapes")
    shape = ET.SubElement(shapes, "PinShapeDef")
    _add_text(shape, "layerNum", str(signal_layer_num) if signal_layer_num is not None else "")
    _add_text(shape, "purposeNum", "-1")
    _add_text(shape, "layerIdName", f"{signal_layer}:drawing" if signal_layer else "")
    _add_text(shape, "shapeType", "point")
    points = ET.SubElement(shape, "points")
    _add_text(points, "stdItem", "0:0")
    _add_text(pin, "deltaGapInfo", "")


def _add_gui_port(ports: ET.Element, *, name: str, number: int, reference_ground_layer: str | None) -> None:
    port = ET.SubElement(ports, "Port")
    _add_text(port, "portNum", str(number))
    _add_text(port, "portName", name)
    _add_text(port, "refImpedance", "50:0")
    _add_text(port, "feedType", "Auto")
    _add_text(port, "refoffset", "0")
    _add_text(port, "termType", "2")
    _add_text(port, "gndLayer", reference_ground_layer or "")
    set_single_std_item(port, "PlusPinNames", name)
    set_single_std_item(port, "MinusPinNames", "::__GND__")


def build_ads_gui_port_state_root(
    library: str,
    target_cell: str,
    *,
    signal_layer: str | None,
    signal_layer_num: int | None,
    reference_ground_layer: str | None,
) -> ET.Element:
    root = ET.Element("EmSimSetup")
    port_main = ET.SubElement(root, "PortMain")
    mom_layout = ET.SubElement(port_main, "MomLayout")
    _add_text(mom_layout, "workspaceText", "undefined")
    _add_text(mom_layout, "libraryText", library)
    _add_text(mom_layout, "cellText", target_cell)
    _add_text(mom_layout, "viewText", "layout")

    dialog = ET.SubElement(port_main, "PortEditorDialog")
    _add_text(dialog, "autoSelect", "true")
    _add_text(dialog, "autoCenter", "true")
    _add_text(dialog, "autoZoom", "true")
    _add_text(dialog, "hideConnectedPins", "false")
    _add_text(dialog, "dataScope", "0")

    pin_view = ET.SubElement(dialog, "PinView")
    _add_text(pin_view, "isSnapshotForInfoOnly", "true")
    pins = ET.SubElement(pin_view, "Pins")
    _add_gui_pin(pins, name="P1", number=1, signal_layer=signal_layer, signal_layer_num=signal_layer_num)
    _add_gui_pin(pins, name="P2", number=2, signal_layer=signal_layer, signal_layer_num=signal_layer_num)

    port_view = ET.SubElement(dialog, "PortView")
    _add_text(port_view, "portCalibrationTypeOverride", "Default")
    _add_text(port_view, "isSnapshotForInfoOnly", "true")
    ports = ET.SubElement(port_view, "Ports")
    _add_gui_port(ports, name="P1", number=1, reference_ground_layer=reference_ground_layer)
    _add_gui_port(ports, name="P2", number=2, reference_ground_layer=reference_ground_layer)
    return root


def sync_ads_gui_port_state(
    workspace: Path,
    library: str,
    target_cell: str,
    params_path: Path | None,
    *,
    signal_layer: str | None,
    signal_layer_num: int | None,
    reference_ground_layer: str | None,
    create_if_missing: bool = True,
) -> Path | None:
    state_xml_path = workspace / "undefined" / "state" / library / target_cell / "layout" / "emSetup.xml"
    if state_xml_path.exists():
        tree = ET.parse(state_xml_path)
        root = tree.getroot()
    elif create_if_missing:
        root = build_ads_gui_port_state_root(
            library,
            target_cell,
            signal_layer=signal_layer,
            signal_layer_num=signal_layer_num,
            reference_ground_layer=reference_ground_layer,
        )
        tree = ET.ElementTree(root)
    else:
        return None

    set_all(root, "workspaceText", "undefined")
    set_all(root, "libraryText", library)
    set_all(root, "cellText", target_cell)
    set_all(root, "viewText", "layout")
    patch_port_editor_reference_fields(
        root,
        params_path,
        signal_layer=signal_layer,
        signal_layer_num=signal_layer_num,
        reference_ground_layer=reference_ground_layer,
        reference_ground_layer_num=None,
    )
    state_xml_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(state_xml_path, encoding="utf-8", xml_declaration=False)
    return state_xml_path


def patch_existing_ads_gui_port_state(
    workspace: Path,
    library: str,
    target_cell: str,
    params_path: Path | None,
    *,
    signal_layer: str | None,
    signal_layer_num: int | None,
    reference_ground_layer: str | None,
    reference_ground_layer_num: int | None,
) -> Path | None:
    return sync_ads_gui_port_state(
        workspace,
        library,
        target_cell,
        params_path,
        signal_layer=signal_layer,
        signal_layer_num=signal_layer_num,
        reference_ground_layer=reference_ground_layer,
        create_if_missing=False,
    )


def clone_emsetup(
    workspace: Path,
    library: str,
    substrate_library: str | None,
    template_cell: str,
    target_cell: str,
    setup_view: str,
    params_path: Path | None,
    start_ghz: float,
    stop_ghz: float,
    points_text: str,
    overwrite: bool,
    force: bool,
    profile_substrate: str | None = None,
    substrate_override: str | None = None,
    prefer_params_substrate: bool = False,
) -> Path:
    log(
        "Clone EM setup configured: "
        f"workspace={workspace}, library={library}, template_cell={template_cell}, "
        f"target_cell={target_cell}, setup_view={setup_view}, overwrite={overwrite}, force={force}"
    )
    validate_ads_cell_write(
        AdsWriteContext(
            profile_id="direct",
            workspace=workspace,
            library=library,
            template_cell=template_cell,
            target_cell=target_cell,
            force=force,
        ),
        operation="clone_emsetup",
    )
    lib_dir = workspace / library
    template_dir = find_cell_dir(lib_dir, template_cell)
    target_dir = find_cell_dir(lib_dir, target_cell)
    src_dir = template_dir / setup_view
    dst_dir = target_dir / setup_view
    log(f"Template EM setup dir: {src_dir}")
    log(f"Target EM setup dir: {dst_dir}")
    if not src_dir.exists():
        raise FileNotFoundError(f"template EM setup not found: {src_dir}")
    if not target_dir.exists():
        raise FileNotFoundError(f"target ADS cell directory not found: {target_dir}")
    if dst_dir.exists():
        if not overwrite:
            raise FileExistsError(f"target EM setup already exists: {dst_dir}")
        guard_directory_delete(dst_dir, required_parent=target_dir, operation="overwrite em setup")
        log(f"Removing existing target EM setup dir: {dst_dir}")
        shutil.rmtree(dst_dir)

    log("Copying EM setup directory")
    shutil.copytree(src_dir, dst_dir)

    xml_path = dst_dir / "emStateFile.xml"
    log(f"Patching EM setup XML: {xml_path}")
    tree = ET.parse(xml_path)
    root = tree.getroot()
    port_layer_context = load_ads_port_layer_context(params_path)
    signal_layer = str(port_layer_context.get("signal_layer", "")) or None
    signal_layer_num = port_layer_context.get("signal_layer_num")
    reference_ground_layer = str(port_layer_context.get("reference_ground_layer", "")) or None
    reference_ground_layer_num = port_layer_context.get("reference_ground_layer_num")
    params_substrate_name = substrate_name_from_params(params_path)
    override_substrate_lib, override_substrate_name = split_substrate_ref(substrate_override)
    profile_substrate_lib, profile_substrate_name = split_substrate_ref(profile_substrate)
    substrate_lib_name = override_substrate_lib or profile_substrate_lib or substrate_library or library
    substrate_search_dirs = [workspace / substrate_lib_name]
    if substrate_lib_name != library:
        substrate_search_dirs.append(workspace / library)
    substrate_search_dirs.append(workspace / "Substrates")
    if prefer_params_substrate:
        substrate_name = (
            override_substrate_name
            or params_substrate_name
            or profile_substrate_name
            or first_substrate_name(substrate_search_dirs, root)
        )
    else:
        substrate_name = (
            override_substrate_name
            or profile_substrate_name
            or params_substrate_name
            or first_substrate_name(substrate_search_dirs, root)
        )
    log(f"Using ADS substrate: {substrate_lib_name}:{substrate_name}")

    replace_text(root, template_cell, target_cell)
    replace_text(root, f"{template_cell}_emCosim", f"{target_cell}_emCosim")
    set_all(root, "workspaceText", str(workspace))
    set_all(root, "libraryText", library)
    set_all(root, "cellText", target_cell)
    set_all(root, "libSubstName", f"{substrate_lib_name}:{substrate_name}")
    set_first(root, "givenDatasetName", target_cell)
    set_first(root, "givenDdsName", target_cell)
    set_first(root, "dds_givenName", target_cell)
    set_first(root, "ds_givenName", target_cell)
    set_first(root, "topLibCellView", f"{library}:{target_cell}:layout")
    set_first(root, "intermediateLibraryName", library)
    set_first(root, "intermediateCellName", f"{target_cell}_emCosim")
    set_first(root, "startFreq", f"{start_ghz:g}")
    set_first(root, "stopFreq", f"{stop_ghz:g}")
    set_first(root, "ptsFreq", points_text)
    set_first(root, "MaxRefineFrequency", f"{stop_ghz:g} GHz")
    gnd_layer_token = patch_port_editor_reference_fields(
        root,
        params_path,
        signal_layer=signal_layer,
        signal_layer_num=int(signal_layer_num) if signal_layer_num is not None else None,
        reference_ground_layer=reference_ground_layer,
        reference_ground_layer_num=int(reference_ground_layer_num) if reference_ground_layer_num is not None else None,
    )
    if gnd_layer_token:
        log(f"Using explicit ADS port gndLayer: {gnd_layer_token} ({reference_ground_layer})")

    if params_path is not None:
        log(f"Patching pin snapshots from params: {params_path}")

    tree.write(xml_path, encoding="utf-8", xml_declaration=False)
    log(f"EM setup XML saved: {xml_path}")
    state_xml_path = None
    if reference_ground_layer:
        state_xml_path = sync_ads_gui_port_state(
            workspace,
            library,
            target_cell,
            params_path,
            signal_layer=signal_layer,
            signal_layer_num=int(signal_layer_num) if signal_layer_num is not None else None,
            reference_ground_layer=reference_ground_layer,
        )
    if state_xml_path is not None:
        log(f"Synced ADS GUI EM setup state: {state_xml_path}")
    return xml_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clone/patched ADS FEM EM Setup from a template cell.")
    parser.add_argument("--profile", default="company", choices=profile_names(), help="ADS path profile to use.")
    parser.add_argument("--workspace", type=Path, default=None, help="Override profile ADS workspace.")
    parser.add_argument("--library", default=None, help="Override profile ADS library.")
    parser.add_argument("--template-cell", default=DEFAULT_TEMPLATE_CELL)
    parser.add_argument("--target-cell", required=True)
    parser.add_argument("--setup-view", default=DEFAULT_SETUP_VIEW)
    parser.add_argument("--params", type=Path, default=None)
    parser.add_argument("--start-ghz", type=float, default=4.0)
    parser.add_argument("--stop-ghz", type=float, default=10.0)
    parser.add_argument("--points-text", default="50 (max)")
    parser.add_argument(
        "--substrate",
        default=None,
        help="Override substrate reference or name, for example LIB:JLC04161H_7628_1P6MM.",
    )
    parser.add_argument(
        "--prefer-params-substrate",
        action="store_true",
        help="Use params JSON substrate before the profile substrate when no explicit --substrate is given.",
    )
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--force", action="store_true", help="Allow protected operations such as writing the template cell.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    log("ads_clone_emsetup_template.py started")
    workspace = resolve_workspace(args.profile, args.workspace)
    library = resolve_library(args.profile, args.library)
    substrate_library = resolve_substrate_library(args.profile, None)
    profile_substrate = resolve_substrate(args.profile, None)
    xml_path = clone_emsetup(
        workspace=workspace,
        library=library,
        substrate_library=substrate_library,
        template_cell=args.template_cell,
        target_cell=args.target_cell,
        setup_view=args.setup_view,
        params_path=args.params,
        start_ghz=args.start_ghz,
        stop_ghz=args.stop_ghz,
        points_text=args.points_text,
        overwrite=args.overwrite,
        force=args.force,
        profile_substrate=profile_substrate,
        substrate_override=args.substrate,
        prefer_params_substrate=args.prefer_params_substrate,
    )
    print(f"Cloned EM setup: {xml_path}", flush=True)


if __name__ == "__main__":
    main()
