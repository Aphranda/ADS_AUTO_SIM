#!/usr/bin/env python3
"""Generate HFSS smoke layouts for a 50R microstrip plus connector launch."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys

_SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.hfss.connector import (
    BASELINE_FIXTURE_TYPE,
    FIXTURE_TYPE,
    FIXTURE_TYPES,
    SINGLE_CONNECTOR_FIXTURE_TYPE,
    ConnectorLaunchParams,
    load_fixture_type,
    load_params,
    load_stackup_params,
    params_with_total_len,
    write_fixture_outputs,
)


def _deep_merge(left: dict, right: dict) -> dict:
    output = dict(left)
    for key, value in right.items():
        if isinstance(value, dict) and isinstance(output.get(key), dict):
            output[key] = _deep_merge(output[key], value)
        else:
            output[key] = value
    return output


def _candidate_config(args: argparse.Namespace) -> dict:
    if args.project_config is None and args.layout_candidate is None:
        return {}
    if args.project_config is None or args.layout_candidate is None:
        raise SystemExit("--project-config and --layout-candidate must be used together")
    data = json.loads(args.project_config.read_text(encoding="utf-8-sig"))
    layout_opt = data.get("layout_optimization", {}) if isinstance(data, dict) else {}
    defaults = layout_opt.get("defaults", {})
    candidates = layout_opt.get("candidates", {})
    if args.layout_candidate not in candidates:
        raise SystemExit(f"layout candidate not found in {args.project_config}: {args.layout_candidate}")
    return _deep_merge(defaults, candidates[args.layout_candidate])


def _configured_path(value: str | None) -> Path | None:
    return Path(value) if value else None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate microstrip+connector launch layout JSON/SVG.")
    parser.add_argument("--params", type=Path, default=None, help="Optional connector params JSON.")
    parser.add_argument("--project-config", type=Path, default=None, help="Project JSON containing layout_optimization candidates.")
    parser.add_argument("--layout-candidate", default=None, help="Candidate key under project_config.layout_optimization.candidates.")
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--name", default=None)
    parser.add_argument(
        "--fixture-type",
        choices=FIXTURE_TYPES,
        default=None,
        help="Fixture topology. Default: inherit from --params fixture_type, or dual connector fixture without --params.",
    )
    parser.add_argument("--stackup-config", type=Path, default=Path("config/stackups/JLC04161H_7628_1P6MM.json"))
    parser.add_argument("--line-w-mm", type=float, default=None)
    parser.add_argument("--line-l-mm", type=float, default=None)
    parser.add_argument("--total-l-mm", type=float, default=None, help="Set exact P1-to-P2 fixture length; mutually exclusive with --line-l-mm.")
    parser.add_argument("--cpw-ground-gap-mm", type=float, default=None)
    parser.add_argument("--launch-ground-gap-mm", type=float, default=None)
    parser.add_argument("--launch-cpw-ground-enabled", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--connector-ground-pad-enabled", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--connector-ground-pad-l-mm", type=float, default=None)
    parser.add_argument("--connector-ground-pad-y-inner-mm", type=float, default=None)
    parser.add_argument("--connector-ground-pad-y-outer-mm", type=float, default=None)
    parser.add_argument("--connector-ground-foot-via-enabled", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--connector-ground-foot-via-count", type=int, default=None)
    parser.add_argument("--connector-ground-foot-via-pitch-mm", type=float, default=None)
    parser.add_argument("--connector-ground-foot-via-x-offset-mm", type=float, default=None)
    parser.add_argument("--connector-ground-foot-via-y-mm", type=float, default=None)
    parser.add_argument("--connector-ground-foot-via-edge-clearance-mm", type=float, default=None)
    parser.add_argument("--launch-ground-via-enabled", action=argparse.BooleanOptionalAction, default=None)
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
    parser.add_argument("--l3-cutout-enabled", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--l3-cutout-shape", default=None)
    parser.add_argument("--l3-cutout-w-mm", type=float, default=None)
    parser.add_argument("--l3-cutout-l-mm", type=float, default=None)
    parser.add_argument("--l3-cutout-offset-x-mm", type=float, default=None)
    parser.add_argument("--l3-cutout-taper-l-mm", type=float, default=None)
    parser.add_argument("--l3-ground-enabled", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--l3-ground-layer", default=None)
    parser.add_argument("--l3-ground-margin-mm", type=float, default=None)
    parser.add_argument("--reference-ground-extend-left-mm", type=float, default=None)
    parser.add_argument("--reference-ground-extend-right-mm", type=float, default=None)
    parser.add_argument("--l3-ground-extend-left-mm", type=float, default=None)
    parser.add_argument("--l3-ground-extend-right-mm", type=float, default=None)
    parser.add_argument("--l4-ground-enabled", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--l4-ground-layer", default=None)
    parser.add_argument("--l4-ground-margin-mm", type=float, default=None)
    parser.add_argument("--l4-ground-extend-left-mm", type=float, default=None)
    parser.add_argument("--l4-ground-extend-right-mm", type=float, default=None)
    parser.add_argument("--series-hi-z-enabled", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--series-hi-z-w-mm", type=float, default=None)
    parser.add_argument("--series-hi-z-l-mm", type=float, default=None)
    parser.add_argument("--series-hi-z-offset-x-mm", type=float, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidate = _candidate_config(args)
    candidate_params = candidate.get("params", {})
    config_params = _configured_path(candidate.get("base_params")) or args.params
    config_out_dir = _configured_path(candidate.get("out_dir")) or args.out_dir
    config_stackup = _configured_path(candidate.get("stackup_config")) or args.stackup_config
    config_fixture_type = candidate.get("fixture_type")
    config_total_l = candidate.get("total_l_mm")
    config_line_l = candidate.get("line_l_mm")
    if args.line_l_mm is not None and args.total_l_mm is not None:
        raise SystemExit("--line-l-mm and --total-l-mm are mutually exclusive")
    if config_out_dir is None:
        raise SystemExit("--out-dir is required unless layout candidate config provides out_dir")
    if config_line_l is not None and config_total_l is not None:
        raise SystemExit("configured line_l_mm and total_l_mm are mutually exclusive")
    params = load_params(config_params) if config_params is not None else ConnectorLaunchParams()
    updates = {
        key: value
        for key, value in {
            "name": args.name if args.name is not None else candidate.get("name"),
            "line_w_mm": args.line_w_mm if args.line_w_mm is not None else candidate_params.get("line_w_mm"),
            "cpw_ground_gap_mm": args.cpw_ground_gap_mm if args.cpw_ground_gap_mm is not None else candidate_params.get("cpw_ground_gap_mm"),
            "launch_ground_gap_mm": args.launch_ground_gap_mm if args.launch_ground_gap_mm is not None else candidate_params.get("launch_ground_gap_mm"),
            "launch_cpw_ground_enabled": args.launch_cpw_ground_enabled
            if args.launch_cpw_ground_enabled is not None
            else candidate_params.get("launch_cpw_ground_enabled"),
            "connector_ground_pad_enabled": args.connector_ground_pad_enabled
            if args.connector_ground_pad_enabled is not None
            else candidate_params.get("connector_ground_pad_enabled"),
            "connector_ground_pad_l_mm": args.connector_ground_pad_l_mm if args.connector_ground_pad_l_mm is not None else candidate_params.get("connector_ground_pad_l_mm"),
            "connector_ground_pad_y_inner_mm": args.connector_ground_pad_y_inner_mm
            if args.connector_ground_pad_y_inner_mm is not None
            else candidate_params.get("connector_ground_pad_y_inner_mm"),
            "connector_ground_pad_y_outer_mm": args.connector_ground_pad_y_outer_mm
            if args.connector_ground_pad_y_outer_mm is not None
            else candidate_params.get("connector_ground_pad_y_outer_mm"),
            "connector_ground_foot_via_enabled": args.connector_ground_foot_via_enabled
            if args.connector_ground_foot_via_enabled is not None
            else candidate_params.get("connector_ground_foot_via_enabled"),
            "connector_ground_foot_via_count": args.connector_ground_foot_via_count
            if args.connector_ground_foot_via_count is not None
            else candidate_params.get("connector_ground_foot_via_count"),
            "connector_ground_foot_via_pitch_mm": args.connector_ground_foot_via_pitch_mm
            if args.connector_ground_foot_via_pitch_mm is not None
            else candidate_params.get("connector_ground_foot_via_pitch_mm"),
            "connector_ground_foot_via_x_offset_mm": args.connector_ground_foot_via_x_offset_mm
            if args.connector_ground_foot_via_x_offset_mm is not None
            else candidate_params.get("connector_ground_foot_via_x_offset_mm"),
            "connector_ground_foot_via_y_mm": args.connector_ground_foot_via_y_mm
            if args.connector_ground_foot_via_y_mm is not None
            else candidate_params.get("connector_ground_foot_via_y_mm"),
            "connector_ground_foot_via_edge_clearance_mm": args.connector_ground_foot_via_edge_clearance_mm
            if args.connector_ground_foot_via_edge_clearance_mm is not None
            else candidate_params.get("connector_ground_foot_via_edge_clearance_mm"),
            "launch_ground_via_enabled": args.launch_ground_via_enabled
            if args.launch_ground_via_enabled is not None
            else candidate_params.get("launch_ground_via_enabled"),
            "line_via_pitch_mm": args.line_via_pitch_mm if args.line_via_pitch_mm is not None else candidate_params.get("line_via_pitch_mm"),
            "pin_pad_w_mm": args.pin_pad_w_mm if args.pin_pad_w_mm is not None else candidate_params.get("pin_pad_w_mm"),
            "pin_pad_l_mm": args.pin_pad_l_mm if args.pin_pad_l_mm is not None else candidate_params.get("pin_pad_l_mm"),
            "taper_l_mm": args.taper_l_mm if args.taper_l_mm is not None else candidate_params.get("taper_l_mm"),
            "taper_w_start_mm": args.taper_w_start_mm if args.taper_w_start_mm is not None else candidate_params.get("taper_w_start_mm"),
            "taper_w_end_mm": args.taper_w_end_mm if args.taper_w_end_mm is not None else candidate_params.get("taper_w_end_mm"),
            "gnd_clearance_mm": args.gnd_clearance_mm if args.gnd_clearance_mm is not None else candidate_params.get("gnd_clearance_mm"),
            "fence_offset_mm": args.fence_offset_mm if args.fence_offset_mm is not None else candidate_params.get("fence_offset_mm"),
            "via_count": args.via_count if args.via_count is not None else candidate_params.get("via_count"),
            "l2_cutout_enabled": args.l2_cutout_enabled if args.l2_cutout_enabled is not None else candidate_params.get("l2_cutout_enabled"),
            "l2_cutout_shape": args.l2_cutout_shape if args.l2_cutout_shape is not None else candidate_params.get("l2_cutout_shape"),
            "l2_cutout_w_mm": args.l2_cutout_w_mm if args.l2_cutout_w_mm is not None else candidate_params.get("l2_cutout_w_mm"),
            "l2_cutout_l_mm": args.l2_cutout_l_mm if args.l2_cutout_l_mm is not None else candidate_params.get("l2_cutout_l_mm"),
            "l2_cutout_offset_x_mm": args.l2_cutout_offset_x_mm if args.l2_cutout_offset_x_mm is not None else candidate_params.get("l2_cutout_offset_x_mm"),
            "l2_cutout_taper_l_mm": args.l2_cutout_taper_l_mm if args.l2_cutout_taper_l_mm is not None else candidate_params.get("l2_cutout_taper_l_mm"),
            "l2_cutout_corner_r_mm": args.l2_cutout_corner_r_mm if args.l2_cutout_corner_r_mm is not None else candidate_params.get("l2_cutout_corner_r_mm"),
            "l2_cutout_keep_gnd_via_clearance_mm": args.l2_cutout_keep_gnd_via_clearance_mm
            if args.l2_cutout_keep_gnd_via_clearance_mm is not None
            else candidate_params.get("l2_cutout_keep_gnd_via_clearance_mm"),
            "l3_cutout_enabled": args.l3_cutout_enabled if args.l3_cutout_enabled is not None else candidate_params.get("l3_cutout_enabled"),
            "l3_cutout_shape": args.l3_cutout_shape if args.l3_cutout_shape is not None else candidate_params.get("l3_cutout_shape"),
            "l3_cutout_w_mm": args.l3_cutout_w_mm if args.l3_cutout_w_mm is not None else candidate_params.get("l3_cutout_w_mm"),
            "l3_cutout_l_mm": args.l3_cutout_l_mm if args.l3_cutout_l_mm is not None else candidate_params.get("l3_cutout_l_mm"),
            "l3_cutout_offset_x_mm": args.l3_cutout_offset_x_mm
            if args.l3_cutout_offset_x_mm is not None
            else candidate_params.get("l3_cutout_offset_x_mm"),
            "l3_cutout_taper_l_mm": args.l3_cutout_taper_l_mm if args.l3_cutout_taper_l_mm is not None else candidate_params.get("l3_cutout_taper_l_mm"),
            "l3_ground_enabled": args.l3_ground_enabled if args.l3_ground_enabled is not None else candidate_params.get("l3_ground_enabled"),
            "l3_ground_layer": args.l3_ground_layer if args.l3_ground_layer is not None else candidate_params.get("l3_ground_layer"),
            "l3_ground_margin_mm": args.l3_ground_margin_mm if args.l3_ground_margin_mm is not None else candidate_params.get("l3_ground_margin_mm"),
            "reference_ground_extend_left_mm": args.reference_ground_extend_left_mm
            if args.reference_ground_extend_left_mm is not None
            else candidate_params.get("reference_ground_extend_left_mm"),
            "reference_ground_extend_right_mm": args.reference_ground_extend_right_mm
            if args.reference_ground_extend_right_mm is not None
            else candidate_params.get("reference_ground_extend_right_mm"),
            "l3_ground_extend_left_mm": args.l3_ground_extend_left_mm
            if args.l3_ground_extend_left_mm is not None
            else candidate_params.get("l3_ground_extend_left_mm"),
            "l3_ground_extend_right_mm": args.l3_ground_extend_right_mm
            if args.l3_ground_extend_right_mm is not None
            else candidate_params.get("l3_ground_extend_right_mm"),
            "l4_ground_enabled": args.l4_ground_enabled if args.l4_ground_enabled is not None else candidate_params.get("l4_ground_enabled"),
            "l4_ground_layer": args.l4_ground_layer if args.l4_ground_layer is not None else candidate_params.get("l4_ground_layer"),
            "l4_ground_margin_mm": args.l4_ground_margin_mm if args.l4_ground_margin_mm is not None else candidate_params.get("l4_ground_margin_mm"),
            "l4_ground_extend_left_mm": args.l4_ground_extend_left_mm
            if args.l4_ground_extend_left_mm is not None
            else candidate_params.get("l4_ground_extend_left_mm"),
            "l4_ground_extend_right_mm": args.l4_ground_extend_right_mm
            if args.l4_ground_extend_right_mm is not None
            else candidate_params.get("l4_ground_extend_right_mm"),
            "series_hi_z_enabled": args.series_hi_z_enabled if args.series_hi_z_enabled is not None else candidate_params.get("series_hi_z_enabled"),
            "series_hi_z_w_mm": args.series_hi_z_w_mm if args.series_hi_z_w_mm is not None else candidate_params.get("series_hi_z_w_mm"),
            "series_hi_z_l_mm": args.series_hi_z_l_mm if args.series_hi_z_l_mm is not None else candidate_params.get("series_hi_z_l_mm"),
            "series_hi_z_offset_x_mm": args.series_hi_z_offset_x_mm
            if args.series_hi_z_offset_x_mm is not None
            else candidate_params.get("series_hi_z_offset_x_mm"),
        }.items()
        if value is not None
    }
    if updates:
        params = replace(params, **updates)
    line_l_mm = args.line_l_mm if args.line_l_mm is not None else config_line_l
    total_l_mm = args.total_l_mm if args.total_l_mm is not None else config_total_l
    if line_l_mm is not None:
        params = replace(params, line_l_mm=float(line_l_mm))
    if total_l_mm is not None:
        params = params_with_total_len(params, float(total_l_mm))
    params = load_stackup_params(params, config_stackup)
    fixture_type = args.fixture_type or config_fixture_type or load_fixture_type(config_params)
    outputs = write_fixture_outputs(params, config_out_dir, fixture_type=fixture_type)
    for key, path in outputs.items():
        print(f"{key}: {path}")


if __name__ == "__main__":
    main()
