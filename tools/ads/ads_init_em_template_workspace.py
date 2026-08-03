#!/usr/bin/env python3
"""Initialize a reusable ADS workspace for SIMADS RFPro/FEM automation."""

from __future__ import annotations

import argparse
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

from simads.ads.workspace import ads_encoded_cell_dir_name, find_cell_dir
from simads.safety import guard_directory_delete

DEFAULT_WORKSPACE = Path(r"D:\Work\ADS\SIMADS_EM_PAR\SIMADS_EM_PAR")
DEFAULT_LIBRARY = "SIMADS_EM_PAR_lib"
DEFAULT_TEMPLATE_CELL = "SIMADS_EM_TEMPLATE_2PORT_FEM"
DEFAULT_SOURCE_WORKSPACE = Path(r"D:\Work\ADS\BFP\BFP")
DEFAULT_SOURCE_LIBRARY = "BFP_lib"
DEFAULT_SOURCE_TEMPLATE_CELL = "BFP"
DEFAULT_SOURCE_SUBSTRATE = "substrate4"
DEFAULT_SUBSTRATE = "FR4_210UM"
DEFAULT_SETUP_VIEW = "em%Setup"
DEFAULT_OALIB_INCLUDES = (
    "INCLUDE $HPEESOF_DIR/oalibs/analog_rf.defs",
    "INCLUDE $HPEESOF_DIR/oalibs/dsp.defs",
)


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


def patch_template_emsetup(
    xml_path: Path,
    *,
    workspace: Path,
    library: str,
    template_cell: str,
    source_workspace: Path,
    source_library: str,
    source_cell: str,
    substrate_name: str,
) -> None:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    replace_text(root, str(source_workspace), str(workspace))
    replace_text(root, source_library, library)
    replace_text(root, source_cell, template_cell)
    replace_text(root, f"{source_cell}_emCosim", f"{template_cell}_emCosim")
    replace_text(root, f"{source_library}:{source_cell}:layout", f"{library}:{template_cell}:layout")

    set_all(root, "workspaceText", str(workspace))
    set_all(root, "libraryText", library)
    set_all(root, "cellText", template_cell)
    set_all(root, "libSubstName", f"{library}:{substrate_name}")
    set_first(root, "givenDatasetName", template_cell)
    set_first(root, "givenDdsName", template_cell)
    set_first(root, "dds_givenName", template_cell)
    set_first(root, "ds_givenName", template_cell)
    set_first(root, "topLibCellView", f"{library}:{template_cell}:layout")
    set_first(root, "intermediateLibraryName", library)
    set_first(root, "intermediateCellName", f"{template_cell}_emCosim")

    tree.write(xml_path, encoding="utf-8", xml_declaration=False)


def create_workspace_and_library(workspace_path: Path, library_name: str) -> None:
    import keysight.ads.de as de

    log(f"Creating ADS workspace: {workspace_path}")
    de.create_workspace(str(workspace_path))
    workspace = de.open_workspace(str(workspace_path))
    try:
        lib_path = workspace_path / library_name
        try:
            library = de.Library.get(library_name)
        except RuntimeError:
            library = None
        if library is None:
            log(f"Creating ADS library: {library_name} at {lib_path}")
            library = de.create_new_library(library_name, lib_path)
        library_names_attr = workspace.library_names
        library_names = library_names_attr() if callable(library_names_attr) else library_names_attr
        if library_name not in library_names:
            log(f"Adding ADS library to workspace: {library_name}")
            workspace.add_library(library_name, lib_path, mode=de.LibraryMode.SHARED)
        log("Creating standard ADS layout technology")
        library.create_layout_tech_std_ads("millimeter", 1000, copy_tech=True)
    finally:
        log(f"Closing ADS workspace: {workspace_path}")
        try:
            workspace.close()
        except RuntimeError:
            pass


def ensure_workspace_lib_defs(workspace_path: Path, library_name: str) -> None:
    """Register the reusable library in the workspace lib.defs.

    ADS can create the library on disk without adding a stable DEFINE/ASSIGN
    entry to lib.defs. RFPro automation then opens the workspace but cannot
    resolve the library by name, especially in fresh template workspaces.
    """

    lib_defs = workspace_path / "lib.defs"
    lines = lib_defs.read_text(encoding="utf-8").splitlines() if lib_defs.exists() else []

    def has_line(target: str) -> bool:
        return any(line.strip() == target for line in lines)

    changed = False
    for include in reversed(DEFAULT_OALIB_INCLUDES):
        if not has_line(include):
            lines.insert(0, include)
            changed = True

    define = f"DEFINE {library_name} {library_name}"
    assign = f"ASSIGN {library_name} libMode shared"
    softinclude_indices = [idx for idx, line in enumerate(lines) if line.strip().lower() == "softinclude lib.defs"]
    insert_at = softinclude_indices[0] if softinclude_indices else len(lines)

    for entry in (define, assign):
        if not has_line(entry):
            lines.insert(insert_at, entry)
            insert_at += 1
            changed = True

    if changed:
        log(f"Updating ADS workspace library registry: {lib_defs}")
        lib_defs.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def copy_template_setup(
    *,
    workspace: Path,
    library: str,
    template_cell: str,
    source_workspace: Path,
    source_library: str,
    source_cell: str,
    setup_view: str,
    substrate_name: str,
) -> None:
    lib_dir = workspace / library
    source_lib_dir = source_workspace / source_library
    source_cell_dir = find_cell_dir(source_lib_dir, source_cell)
    source_setup = source_cell_dir / setup_view
    if not source_setup.exists():
        raise FileNotFoundError(f"source EM setup not found: {source_setup}")

    template_dir = lib_dir / ads_encoded_cell_dir_name(template_cell)
    template_setup = template_dir / setup_view
    template_dir.mkdir(parents=True, exist_ok=True)
    if template_setup.exists():
        guard_directory_delete(template_setup, required_parent=template_dir, operation="replace template EM setup")
        shutil.rmtree(template_setup)
    log(f"Copying template EM setup: {source_setup} -> {template_setup}")
    shutil.copytree(source_setup, template_setup)

    xml_path = template_setup / "emStateFile.xml"
    log(f"Patching reusable template EM setup: {xml_path}")
    patch_template_emsetup(
        xml_path,
        workspace=workspace,
        library=library,
        template_cell=template_cell,
        source_workspace=source_workspace,
        source_library=source_library,
        source_cell=source_cell,
        substrate_name=substrate_name,
    )


def copy_substrate(
    *,
    workspace: Path,
    library: str,
    source_workspace: Path,
    source_library: str,
    source_substrate: str,
    substrate_name: str,
) -> None:
    source_name = Path(source_substrate).stem
    source_path = source_workspace / source_library / f"{source_name}.subst"
    if not source_path.exists():
        raise FileNotFoundError(f"source substrate not found: {source_path}")

    target_path = workspace / library / f"{substrate_name}.subst"
    log(f"Copying substrate stack: {source_path} -> {target_path}")
    shutil.copy2(source_path, target_path)

    source_materials = source_workspace / source_library / "materials.matdb"
    if source_materials.exists():
        target_materials = workspace / library / "materials.matdb"
        log(f"Copying substrate material database: {source_materials} -> {target_materials}")
        shutil.copy2(source_materials, target_materials)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a reusable ADS RFPro/FEM template workspace.")
    parser.add_argument("--workspace", type=Path, default=DEFAULT_WORKSPACE)
    parser.add_argument("--library", default=DEFAULT_LIBRARY)
    parser.add_argument("--template-cell", default=DEFAULT_TEMPLATE_CELL)
    parser.add_argument("--source-workspace", type=Path, default=DEFAULT_SOURCE_WORKSPACE)
    parser.add_argument("--source-library", default=DEFAULT_SOURCE_LIBRARY)
    parser.add_argument("--source-template-cell", default=DEFAULT_SOURCE_TEMPLATE_CELL)
    parser.add_argument("--source-substrate", default=DEFAULT_SOURCE_SUBSTRATE)
    parser.add_argument("--substrate-name", default=DEFAULT_SUBSTRATE)
    parser.add_argument("--setup-view", default=DEFAULT_SETUP_VIEW)
    parser.add_argument("--overwrite-empty", action="store_true", help="Allow replacing an existing empty workspace directory.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workspace = args.workspace.resolve()
    if workspace.exists():
        children = list(workspace.iterdir()) if workspace.is_dir() else []
        if not args.overwrite_empty or children:
            raise FileExistsError(f"workspace path already exists and is not an approved empty directory: {workspace}")
        workspace.rmdir()
    workspace.parent.mkdir(parents=True, exist_ok=True)

    create_workspace_and_library(workspace, args.library)
    ensure_workspace_lib_defs(workspace, args.library)
    copy_substrate(
        workspace=workspace,
        library=args.library,
        source_workspace=args.source_workspace,
        source_library=args.source_library,
        source_substrate=args.source_substrate,
        substrate_name=args.substrate_name,
    )
    copy_template_setup(
        workspace=workspace,
        library=args.library,
        template_cell=args.template_cell,
        source_workspace=args.source_workspace,
        source_library=args.source_library,
        source_cell=args.source_template_cell,
        setup_view=args.setup_view,
        substrate_name=args.substrate_name,
    )
    log("Reusable ADS EM template workspace initialized")
    print(
        {
            "workspace": str(workspace),
            "library": args.library,
            "template_cell": args.template_cell,
            "setup_view": args.setup_view,
            "substrate": f"{args.library}:{args.substrate_name}",
        },
        flush=True,
    )


if __name__ == "__main__":
    main()
