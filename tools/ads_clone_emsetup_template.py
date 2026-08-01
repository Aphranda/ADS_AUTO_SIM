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
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from ads_profiles import profile_names, resolve_library, resolve_substrate_library, resolve_workspace
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


def set_pin_snapshot(root: ET.Element, pin_name: str, x_mm: float, y_mm: float) -> None:
    for pin in root.findall(".//Pin"):
        name = pin.findtext("pinName")
        if name != pin_name:
            continue
        item = pin.find(".//PinShapeDef/points/stdItem")
        if item is not None:
            item.text = f"{x_mm / 1000.0:.9g}:{y_mm / 1000.0:.9g}"


def load_port_locations(params_path: Path) -> tuple[tuple[float, float], tuple[float, float]]:
    return load_p1_p2_locations(params_path)


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
    substrate_lib_name = substrate_library or library
    substrate_search_dirs = [workspace / substrate_lib_name]
    if substrate_lib_name != library:
        substrate_search_dirs.append(workspace / library)
    substrate_search_dirs.append(workspace / "Substrates")
    substrate_name = substrate_name_from_params(params_path) or first_substrate_name(substrate_search_dirs, root)

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

    if params_path is not None:
        log(f"Patching pin snapshots from params: {params_path}")
        p1, p2 = load_port_locations(params_path)
        set_pin_snapshot(root, "P1", *p1)
        set_pin_snapshot(root, "P2", *p2)

    tree.write(xml_path, encoding="utf-8", xml_declaration=False)
    log(f"EM setup XML saved: {xml_path}")
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
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--force", action="store_true", help="Allow protected operations such as writing the template cell.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    log("ads_clone_emsetup_template.py started")
    workspace = resolve_workspace(args.profile, args.workspace)
    library = resolve_library(args.profile, args.library)
    substrate_library = resolve_substrate_library(args.profile, None)
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
    )
    print(f"Cloned EM setup: {xml_path}", flush=True)


if __name__ == "__main__":
    main()
