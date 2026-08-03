#!/usr/bin/env python3
"""Create/verify ADS physical technology layers for a stackup config.

Run this with ADS Python. The host-side ``tools/ads_sync_stackup.py`` can invoke
it after syncing substrate/material XML files.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC_ROOT = _REPO_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.config import load_stackup_config
from simads.stackups.ads import ads_stackup_layer_map, ads_tech_layer_specs


def ensure_hpeesof_dir() -> None:
    if os.environ.get("HPEESOF_DIR"):
        return
    executable = Path(sys.executable).resolve()
    ads_root = executable.parents[2]
    os.environ["HPEESOF_DIR"] = str(ads_root)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync ADS technology physical layers from stackup JSON.")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--library", required=True)
    parser.add_argument("--stackup-config", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="Create missing layers. Without this flag only checks.")
    parser.add_argument("--verify-layer-ids", action="store_true", help="Verify layer/purpose lookup with LayerId.")
    return parser.parse_args()


def _layer_status(tech: Any, *, name: str, number: int) -> dict[str, Any]:
    by_name = tech.find_layer(name)
    by_number = tech.find_layer(number)
    actual_process_role = None if by_name is None else str(getattr(by_name.process_role, "name", by_name.process_role))
    actual_layer_binding = None if by_name is None else by_name.layer_binding
    return {
        "name": name,
        "number": number,
        "name_exists": by_name is not None,
        "number_exists": by_number is not None,
        "actual_number": None if by_name is None else by_name.number,
        "actual_name": None if by_number is None else by_number.name,
        "actual_process_role": actual_process_role,
        "actual_layer_binding": actual_layer_binding,
    }


def _validate_no_conflict(status: dict[str, Any]) -> None:
    if status["name_exists"] and status["actual_number"] != status["number"]:
        raise RuntimeError(
            f'ADS layer "{status["name"]}" exists with number {status["actual_number"]}, '
            f'expected {status["number"]}'
        )
    if status["number_exists"] and status["actual_name"] != status["name"]:
        raise RuntimeError(
            f'ADS layer number {status["number"]} exists as "{status["actual_name"]}", '
            f'expected "{status["name"]}"'
        )


def _verify_layer_id(library: Any, layer_name: str, purpose_name: str) -> dict[str, Any]:
    import keysight.ads.de as de

    try:
        layer_id = de.db.LayerId.create_layer_id_from_library(library, layer_name, purpose_name)
        return {
            "layer": layer_id.layer,
            "purpose": layer_id.purpose,
            "ok": True,
            "error": None,
        }
    except Exception as exc:  # ADS raises RuntimeError for unresolved layer/purpose.
        return {
            "layer": None,
            "purpose": None,
            "ok": False,
            "error": str(exc),
        }


def _process_role_enum(de: Any, role_name: str) -> Any:
    normalized = role_name.strip().upper()
    if not normalized:
        normalized = "CONDUCTOR"
    return getattr(de.tech.ProcessRole, normalized)


def _apply_layer_properties(de: Any, layer: Any, *, process_role: str, layer_binding: str) -> bool:
    changed = False
    desired_role = _process_role_enum(de, process_role)
    if layer.process_role != desired_role:
        layer.process_role = desired_role
        changed = True
    if layer.layer_binding != layer_binding:
        layer.layer_binding = layer_binding
        changed = True
    return changed


def _desired_master_substrate(library: str, substrate_name: str) -> str:
    return f"{library}:{substrate_name}"


def main() -> None:
    ensure_hpeesof_dir()
    import keysight.ads.de as de

    args = parse_args()
    stackup = load_stackup_config(args.stackup_config)
    layer_map = ads_stackup_layer_map(stackup)
    specs = ads_tech_layer_specs(stackup)

    workspace = de.open_workspace(str(args.workspace))
    created: list[dict[str, Any]] = []
    statuses: list[dict[str, Any]] = []
    try:
        library = de.Library.get(args.library)
        tech = library.tech
        if tech is None:
            raise RuntimeError(f'ADS library "{args.library}" has no technology database')

        changed = False
        desired_master_substrate = _desired_master_substrate(args.library, layer_map.substrate_name)
        initial_master_substrate = tech.master_substrate_name
        if args.apply and tech.master_substrate_name != desired_master_substrate:
            tech.master_substrate_name = desired_master_substrate
            changed = True
        actual_master_substrate = tech.master_substrate_name

        for spec in specs:
            status = _layer_status(tech, name=spec.name, number=spec.number)
            _validate_no_conflict(status)
            layer = tech.find_layer(spec.name)
            if not status["name_exists"]:
                if args.apply:
                    layer = tech.create_physical_layer(spec.name, spec.number)
                    changed = True
                    changed = (
                        _apply_layer_properties(de, layer, process_role=spec.process_role, layer_binding=spec.layer_binding)
                        or changed
                    )
                    created.append(
                        {
                            "name": layer.name,
                            "number": layer.number,
                            "process_role": spec.process_role,
                            "layer_binding": spec.layer_binding,
                        }
                    )
                    status = _layer_status(tech, name=spec.name, number=spec.number)
                else:
                    status["missing"] = True
            elif args.apply and layer is not None:
                changed = (
                    _apply_layer_properties(de, layer, process_role=spec.process_role, layer_binding=spec.layer_binding)
                    or changed
                )
                status = _layer_status(tech, name=spec.name, number=spec.number)
            statuses.append(
                {
                    **status,
                    "purpose": spec.purpose,
                    "role": spec.role,
                    "desired_process_role": spec.process_role,
                    "desired_layer_binding": spec.layer_binding,
                    "definition_ok": (
                        status["actual_process_role"] == spec.process_role
                        and status["actual_layer_binding"] == spec.layer_binding
                    ),
                }
            )

        if changed:
            tech.save()

        if args.verify_layer_ids:
            for status in statuses:
                status["layer_id"] = _verify_layer_id(library, status["name"], status["purpose"])
    finally:
        try:
            workspace.close()
        except RuntimeError:
            pass

    print(
        json.dumps(
            {
                "workspace": str(args.workspace),
                "library": args.library,
                "stackup_id": stackup.stackup_id,
                "apply": args.apply,
                "created": created,
                "changed": changed,
                "master_substrate": {
                    "initial": initial_master_substrate,
                    "desired": desired_master_substrate,
                    "actual": actual_master_substrate,
                    "ok": actual_master_substrate == desired_master_substrate,
                },
                "layers": statuses,
                "desired": [asdict(spec) for spec in specs],
            },
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
