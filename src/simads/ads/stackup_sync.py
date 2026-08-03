"""Synchronize stackup-derived ADS files into a library directory."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

from simads.config import StackupConfig
from simads.safety import validate_substrate_patch
from simads.stackups.ads import (
    ads_stackup_layer_map,
    ads_substrate_text,
    ensure_dielectric_materials,
    ensure_display_layers,
    ensure_lpp_layers,
    xml_text,
)


@dataclass(frozen=True)
class AdsStackupSyncResult:
    substrate_path: Path
    materials_path: Path
    library_tech_path: Path
    display_tech_path: Path
    changed: dict[str, bool]


def _read_xml_or_default(path: Path, root_name: str) -> ET.Element:
    if path.exists():
        return ET.parse(path).getroot()
    return ET.Element(root_name)


def _write_if_changed(path: Path, text: str, *, backup: bool) -> bool:
    current = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else None
    if current == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    if backup and path.exists():
        backup_path = path.with_suffix(path.suffix + ".bak")
        if not backup_path.exists():
            shutil.copy2(path, backup_path)
    path.write_text(text, encoding="utf-8")
    return True


def _materials_text(path: Path, stackup: StackupConfig) -> tuple[str, bool]:
    root = _read_xml_or_default(path, "Materials")
    if root.find("Conductors") is None:
        root.insert(0, ET.Element("Conductors"))
    if root.find("Semiconductors") is None:
        ET.SubElement(root, "Semiconductors")
    if root.find("Superconductors") is None:
        ET.SubElement(root, "Superconductors")
    if root.find("roughness") is None:
        ET.SubElement(root, "roughness")
    changed = ensure_dielectric_materials(root, stackup)
    return xml_text(root, "<!DOCTYPE Materials>"), changed


def _library_tech_text(path: Path, stackup: StackupConfig) -> tuple[str, bool]:
    root = _read_xml_or_default(path, "Lpp_List")
    changed = ensure_lpp_layers(root, stackup)
    return xml_text(root, "<!DOCTYPE Technology>"), changed


def _display_text(path: Path, stackup: StackupConfig) -> tuple[str, bool]:
    root = _read_xml_or_default(path, "Display")
    changed = ensure_display_layers(root, stackup)
    return xml_text(root, "<!DOCTYPE Display>"), changed


def sync_ads_stackup_files(
    library_dir: Path,
    stackup: StackupConfig,
    *,
    apply: bool,
    force: bool,
    backup: bool = True,
) -> AdsStackupSyncResult:
    layer_map = ads_stackup_layer_map(stackup)
    substrate_path = library_dir / f"{layer_map.substrate_name}.subst"
    materials_path = library_dir / "materials.matdb"
    library_tech_path = library_dir / "library.tech"
    display_tech_path = library_dir / "display.tech"

    substrate_text = ads_substrate_text(stackup)
    materials_text, materials_changed = _materials_text(materials_path, stackup)
    library_tech_text, library_tech_changed = _library_tech_text(library_tech_path, stackup)
    display_text, display_changed = _display_text(display_tech_path, stackup)

    current_substrate = substrate_path.read_text(encoding="utf-8", errors="ignore") if substrate_path.exists() else None
    substrate_changed = current_substrate != substrate_text
    validate_substrate_patch(substrate_path, force=force, will_modify=substrate_path.exists() and substrate_changed)

    changed = {
        "substrate": substrate_changed,
        "materials": materials_changed,
        "library_tech": library_tech_changed,
        "display_tech": display_changed,
    }
    if apply:
        _write_if_changed(substrate_path, substrate_text, backup=backup)
        _write_if_changed(materials_path, materials_text, backup=backup)
        _write_if_changed(library_tech_path, library_tech_text, backup=backup)
        _write_if_changed(display_tech_path, display_text, backup=backup)
    return AdsStackupSyncResult(
        substrate_path=substrate_path,
        materials_path=materials_path,
        library_tech_path=library_tech_path,
        display_tech_path=display_tech_path,
        changed=changed,
    )


__all__ = ["AdsStackupSyncResult", "sync_ads_stackup_files"]
