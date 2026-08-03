#!/usr/bin/env python3
"""Synchronize stackup-derived ADS technology files into a workspace library."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

_SIM_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _SIM_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from ads_profiles import profile_names, resolve_ads_python, resolve_library, resolve_workspace
from simads.ads.stackup_sync import sync_ads_stackup_files
from simads.config import load_stackup_config
from simads.stackups.ads import ads_stackup_layer_map


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync ADS substrate/material/tech files from a stackup JSON config.")
    parser.add_argument("--profile", default="home_simads_em_parallel", choices=profile_names())
    parser.add_argument("--workspace", type=Path, default=None)
    parser.add_argument("--library", default=None)
    parser.add_argument("--stackup-config", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="Write files. Without this flag only reports changes.")
    parser.add_argument("--force", action="store_true", help="Allow modifying an existing ADS substrate file.")
    parser.add_argument("--no-backup", action="store_true", help="Do not create .bak files before modifying files.")
    parser.add_argument(
        "--sync-tech-layers",
        action="store_true",
        help="Also invoke ADS Python to create/verify real physical technology layers.",
    )
    parser.add_argument("--ads-python", type=Path, default=None, help="ADS Python executable override.")
    parser.add_argument(
        "--verify-tech-layer-ids",
        action="store_true",
        help="Verify ADS LayerId lookup for each stackup layer after tech sync.",
    )
    return parser.parse_args()


def _run_ads_tech_layer_sync(args: argparse.Namespace, *, workspace: Path, library: str) -> dict[str, object]:
    ads_python = resolve_ads_python(args.profile, args.ads_python)
    script = _SIM_ROOT / "tools" / "ads" / "ads_sync_stackup_tech_layers.py"
    cmd = [
        str(ads_python),
        str(script),
        "--workspace",
        str(workspace),
        "--library",
        library,
        "--stackup-config",
        str(args.stackup_config),
    ]
    if args.apply:
        cmd.append("--apply")
    if args.verify_tech_layer_ids:
        cmd.append("--verify-layer-ids")
    completed = subprocess.run(
        cmd,
        cwd=_SIM_ROOT,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "ADS tech layer sync failed\n"
            f"command: {' '.join(cmd)}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    return json.loads(completed.stdout)


def main() -> None:
    args = parse_args()
    workspace = resolve_workspace(args.profile, args.workspace)
    library = resolve_library(args.profile, args.library)
    library_dir = workspace / library
    if not library_dir.exists():
        raise FileNotFoundError(f"ADS library directory not found: {library_dir}")
    stackup = load_stackup_config(args.stackup_config)
    layer_map = ads_stackup_layer_map(stackup)
    result = sync_ads_stackup_files(
        library_dir,
        stackup,
        apply=args.apply,
        force=args.force,
        backup=not args.no_backup,
    )
    tech_layer_sync = None
    if args.sync_tech_layers:
        tech_layer_sync = _run_ads_tech_layer_sync(args, workspace=workspace, library=library)
    print(
        json.dumps(
            {
                "profile": args.profile,
                "workspace": str(workspace),
                "library": library,
                "library_dir": str(library_dir),
                "stackup_id": stackup.stackup_id,
                "ads_substrate": f"{library}:{layer_map.substrate_name}",
                "apply": args.apply,
                "changed": result.changed,
                "files": {
                    "substrate": str(result.substrate_path),
                    "materials": str(result.materials_path),
                    "library_tech": str(result.library_tech_path),
                    "display_tech": str(result.display_tech_path),
                },
                "layers": {
                    "conductors": layer_map.conductor_layer_ids,
                    "drill_layer": layer_map.drill_layer,
                    "drill_layer_id": layer_map.drill_layer_id,
                    "drill_process_role": layer_map.drill_process_role,
                    "drill_layer_binding": layer_map.drill_layer_binding,
                    "drill_substrate_top_layer": layer_map.drill_substrate_top_layer,
                    "drill_substrate_bottom_layer": layer_map.drill_substrate_bottom_layer,
                    "boundary_layer": layer_map.boundary_layer,
                    "boundary_layer_id": layer_map.boundary_layer_id,
                },
                "tech_layer_sync": tech_layer_sync,
            },
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
