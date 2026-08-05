#!/usr/bin/env python3
"""Generate HFSS smoke layouts for a 50R microstrip plus connector launch."""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path
import sys

_SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.hfss.connector import (
    BASELINE_FIXTURE_TYPE,
    FIXTURE_TYPE,
    SINGLE_CONNECTOR_FIXTURE_TYPE,
    ConnectorLaunchParams,
    load_params,
    load_stackup_params,
    params_with_total_len,
    write_fixture_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate microstrip+connector launch layout JSON/SVG.")
    parser.add_argument("--params", type=Path, default=None, help="Optional connector params JSON.")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--name", default=None)
    parser.add_argument("--fixture-type", choices=[FIXTURE_TYPE, SINGLE_CONNECTOR_FIXTURE_TYPE, BASELINE_FIXTURE_TYPE], default=FIXTURE_TYPE)
    parser.add_argument("--stackup-config", type=Path, default=Path("config/stackups/JLC04161H_7628_1P6MM.json"))
    parser.add_argument("--line-w-mm", type=float, default=None)
    parser.add_argument("--line-l-mm", type=float, default=None)
    parser.add_argument("--total-l-mm", type=float, default=None, help="Set exact P1-to-P2 fixture length; mutually exclusive with --line-l-mm.")
    parser.add_argument("--cpw-ground-gap-mm", type=float, default=None)
    parser.add_argument("--line-via-pitch-mm", type=float, default=None)
    parser.add_argument("--pin-pad-w-mm", type=float, default=None)
    parser.add_argument("--pin-pad-l-mm", type=float, default=None)
    parser.add_argument("--taper-l-mm", type=float, default=None)
    parser.add_argument("--taper-w-start-mm", type=float, default=None)
    parser.add_argument("--taper-w-end-mm", type=float, default=None)
    parser.add_argument("--gnd-clearance-mm", type=float, default=None)
    parser.add_argument("--fence-offset-mm", type=float, default=None)
    parser.add_argument("--via-count", type=int, default=None)
    parser.add_argument("--l2-cutout-enabled", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--l2-cutout-shape", default=None)
    parser.add_argument("--l2-cutout-w-mm", type=float, default=None)
    parser.add_argument("--l2-cutout-l-mm", type=float, default=None)
    parser.add_argument("--l2-cutout-offset-x-mm", type=float, default=None)
    parser.add_argument("--l2-cutout-taper-l-mm", type=float, default=None)
    parser.add_argument("--l2-cutout-corner-r-mm", type=float, default=None)
    parser.add_argument("--l2-cutout-keep-gnd-via-clearance-mm", type=float, default=None)
    parser.add_argument("--series-hi-z-enabled", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--series-hi-z-w-mm", type=float, default=None)
    parser.add_argument("--series-hi-z-l-mm", type=float, default=None)
    parser.add_argument("--series-hi-z-offset-x-mm", type=float, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.line_l_mm is not None and args.total_l_mm is not None:
        raise SystemExit("--line-l-mm and --total-l-mm are mutually exclusive")
    params = load_params(args.params) if args.params is not None else ConnectorLaunchParams()
    updates = {
        key: value
        for key, value in {
            "name": args.name,
            "line_w_mm": args.line_w_mm,
            "cpw_ground_gap_mm": args.cpw_ground_gap_mm,
            "line_via_pitch_mm": args.line_via_pitch_mm,
            "pin_pad_w_mm": args.pin_pad_w_mm,
            "pin_pad_l_mm": args.pin_pad_l_mm,
            "taper_l_mm": args.taper_l_mm,
            "taper_w_start_mm": args.taper_w_start_mm,
            "taper_w_end_mm": args.taper_w_end_mm,
            "gnd_clearance_mm": args.gnd_clearance_mm,
            "fence_offset_mm": args.fence_offset_mm,
            "via_count": args.via_count,
            "l2_cutout_enabled": args.l2_cutout_enabled,
            "l2_cutout_shape": args.l2_cutout_shape,
            "l2_cutout_w_mm": args.l2_cutout_w_mm,
            "l2_cutout_l_mm": args.l2_cutout_l_mm,
            "l2_cutout_offset_x_mm": args.l2_cutout_offset_x_mm,
            "l2_cutout_taper_l_mm": args.l2_cutout_taper_l_mm,
            "l2_cutout_corner_r_mm": args.l2_cutout_corner_r_mm,
            "l2_cutout_keep_gnd_via_clearance_mm": args.l2_cutout_keep_gnd_via_clearance_mm,
            "series_hi_z_enabled": args.series_hi_z_enabled,
            "series_hi_z_w_mm": args.series_hi_z_w_mm,
            "series_hi_z_l_mm": args.series_hi_z_l_mm,
            "series_hi_z_offset_x_mm": args.series_hi_z_offset_x_mm,
        }.items()
        if value is not None
    }
    if updates:
        params = replace(params, **updates)
    if args.line_l_mm is not None:
        params = replace(params, line_l_mm=args.line_l_mm)
    if args.total_l_mm is not None:
        params = params_with_total_len(params, args.total_l_mm)
    params = load_stackup_params(params, args.stackup_config)
    outputs = write_fixture_outputs(params, args.out_dir, fixture_type=args.fixture_type)
    for key, path in outputs.items():
        print(f"{key}: {path}")


if __name__ == "__main__":
    main()
