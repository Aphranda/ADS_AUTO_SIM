#!/usr/bin/env python3
"""Patch an ADS substrate XML file with a pcvia1 via layer definition."""

from __future__ import annotations

import argparse
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

_SIM_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _SIM_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.safety import validate_substrate_patch


def ensure_pcvia(root: ET.Element, via_layer: int, top_index: int, bottom_index: int) -> bool:
    vias = root.find("vias")
    if vias is None:
        vias = ET.SubElement(root, "vias")
        changed = True
    else:
        changed = False

    for via in vias.findall("via"):
        if via.get("layer") == str(via_layer):
            expected = {
                "processRole": "4",
                "materialname": "PERFECT_CONDUCTOR",
                "index1": str(top_index),
                "index2": str(bottom_index),
            }
            for key, value in expected.items():
                if via.get(key) != value:
                    via.set(key, value)
                    changed = True
            return changed

    ET.SubElement(
        vias,
        "via",
        {
            "rough": "",
            "platingthicknessunit": "micron",
            "platingthickness": "",
            "layer": str(via_layer),
            "processRole": "4",
            "platingdielectricmaterial": "AIR",
            "precedence": "0",
            "materialname": "PERFECT_CONDUCTOR",
            "index2": str(bottom_index),
            "subtype": "0",
            "index1": str(top_index),
            "platingenabled": "0",
        },
    )
    return True


def substrate_patch_needed(path: Path, via_layer: int, top_index: int, bottom_index: int) -> bool:
    tree = ET.parse(path)
    root = tree.getroot()
    return ensure_pcvia(root, via_layer, top_index, bottom_index)


def patch_substrate(
    path: Path,
    via_layer: int,
    top_index: int,
    bottom_index: int,
    backup: bool,
    *,
    force: bool,
) -> bool:
    tree = ET.parse(path)
    root = tree.getroot()
    changed = ensure_pcvia(root, via_layer, top_index, bottom_index)
    validate_substrate_patch(path, force=force, will_modify=changed)
    if not changed:
        return False

    if backup:
        backup_path = path.with_suffix(path.suffix + ".bak")
        if not backup_path.exists():
            shutil.copy2(path, backup_path)
    tree.write(path, encoding="utf-8", xml_declaration=False)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Add/update a pcvia1 via layer entry in ADS substrate XML.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--via-layer", type=int, default=24)
    parser.add_argument("--top-index", type=int, default=1)
    parser.add_argument("--bottom-index", type=int, default=0)
    parser.add_argument("--no-backup", action="store_true")
    parser.add_argument("--force", action="store_true", help="Allow modifying the ADS substrate file.")
    parser.add_argument("--check-only", action="store_true", help="Report whether a patch is needed without writing.")
    args = parser.parse_args()

    if args.check_only:
        needed = substrate_patch_needed(
            args.path,
            via_layer=args.via_layer,
            top_index=args.top_index,
            bottom_index=args.bottom_index,
        )
        print(f"{'patch needed' if needed else 'already ok'}: {args.path}")
        return

    changed = patch_substrate(
        args.path,
        via_layer=args.via_layer,
        top_index=args.top_index,
        bottom_index=args.bottom_index,
        backup=not args.no_backup,
        force=args.force,
    )
    print(f"{'patched' if changed else 'already ok'}: {args.path}")


if __name__ == "__main__":
    main()
