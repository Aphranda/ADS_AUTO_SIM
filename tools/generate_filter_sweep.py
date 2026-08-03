#!/usr/bin/env python3
"""Generate a batch of interdigital filter DXF candidates from a CSV plan."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

_SIM_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _SIM_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.config import load_stackup_config
from layout.generate_interdigital_filter_layout import FilterParams, params_with_stackup_config, write_outputs


def read_float(row: dict[str, str], key: str, default: float) -> float:
    value = row.get(key, "").strip()
    return default if value == "" else float(value)


def read_str(row: dict[str, str], key: str, default: str) -> str:
    value = row.get(key, "").strip()
    return value or default


def read_bool(row: dict[str, str], key: str, default: bool) -> bool:
    value = row.get(key, "").strip().lower()
    if value == "":
        return default
    if value in {"1", "true", "yes", "y", "on"}:
        return True
    if value in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError(f"{key} must be a boolean value, got {row.get(key)!r}")


def row_to_params(row: dict[str, str]) -> FilterParams:
    defaults = FilterParams()
    gap_keys = [key for key in row if key.startswith("S") and key.endswith("_mm")]
    gap_count = max((int(key[1:-3]) for key in gap_keys if key[1:-3].isdigit()), default=len(defaults.gaps_mm))
    gaps = tuple(read_float(row, f"S{idx}_mm", defaults.gaps_mm[idx - 1]) for idx in range(1, gap_count + 1))
    return FilterParams(
        name=row["name"].strip(),
        order=gap_count + 1,
        substrate=read_str(row, "substrate", defaults.substrate),
        er=read_float(row, "er", defaults.er),
        dielectric_height_mm=read_float(row, "dielectric_height_mm", defaults.dielectric_height_mm),
        copper_thickness_mm=read_float(row, "copper_thickness_mm", defaults.copper_thickness_mm),
        w0_mm=read_float(row, "W0_mm", defaults.w0_mm),
        resonator_w_mm=read_float(row, "resonator_w_mm", read_float(row, "W0_mm", defaults.resonator_w_mm)),
        resonator_l_mm=read_float(row, "L_mm", defaults.resonator_l_mm),
        tap_from_bottom_mm=read_float(row, "tap_mm", defaults.tap_from_bottom_mm),
        end_gap_mm=read_float(row, "Egap_mm", defaults.end_gap_mm),
        gaps_mm=gaps,
        feed_len_mm=read_float(row, "feed_len_mm", defaults.feed_len_mm),
        feed_taper_len_mm=read_float(row, "feed_taper_len_mm", defaults.feed_taper_len_mm),
        feed_tip_w_mm=read_float(row, "feed_tip_w_mm", defaults.feed_tip_w_mm),
        feed_overlap_mm=read_float(row, "feed_overlap_mm", defaults.feed_overlap_mm),
        min_fab_feature_mm=read_float(row, "min_fab_feature_mm", defaults.min_fab_feature_mm),
        via_diameter_mm=read_float(row, "via_diameter_mm", defaults.via_diameter_mm),
        via_pad_mm=read_float(row, "via_pad_mm", defaults.via_pad_mm),
        via_half_outside=read_bool(row, "via_half_outside", defaults.via_half_outside),
        via_pad_outside=read_bool(row, "via_pad_outside", defaults.via_pad_outside),
        metal_layer=row.get("metal_layer", defaults.metal_layer).strip() or defaults.metal_layer,
        via_layer=row.get("via_layer", defaults.via_layer).strip() or defaults.via_layer,
        ground_layer=row.get("ground_layer", defaults.ground_layer).strip() or defaults.ground_layer,
        include_ground_plane=read_bool(row, "include_ground_plane", defaults.include_ground_plane),
        ground_boundary_mode=row.get("ground_boundary_mode", defaults.ground_boundary_mode).strip()
        or defaults.ground_boundary_mode,
        ground_plane_name=row.get("ground_plane_name", defaults.ground_plane_name).strip()
        or defaults.ground_plane_name,
    )


def parse_args() -> argparse.Namespace:
    script_dir = Path(__file__).resolve().parent
    sim_dir = script_dir.parent
    parser = argparse.ArgumentParser(description="Generate filter layout candidates from a project plan CSV.")
    parser.add_argument("--plan", type=Path, default=sim_dir / "ADS" / "filter_sweep_plan.csv")
    parser.add_argument("--out-dir", type=Path, default=sim_dir / "ADS" / "sweep")
    parser.add_argument("--stackup-config", type=Path, default=None, help="PCB stackup JSON config used for naming and EM material parameters.")
    parser.add_argument(
        "--name-stackup-token",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Append/replace the configured stackup token in generated candidate names.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with args.plan.open(newline="", encoding="utf-8") as fp:
        rows = list(csv.DictReader(fp))
    stackup = load_stackup_config(args.stackup_config) if args.stackup_config is not None else None

    print(f"Generating {len(rows)} candidates into {args.out_dir}")
    for row in rows:
        params = row_to_params(row)
        if stackup is not None:
            params = params_with_stackup_config(
                params,
                stackup,
                config_path=args.stackup_config,
                rename=args.name_stackup_token,
            )
        outputs = write_outputs(params, args.out_dir)
        print(f"  {params.name}: {outputs['dxf_mm_coords']}")


if __name__ == "__main__":
    main()

