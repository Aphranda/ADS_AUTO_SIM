#!/usr/bin/env python3
"""Generate a fine-refinement 7th-order FR4 interdigital candidate set.

Round2 showed that the current best point is still the baseline
``i7_fr4_r2_base`` geometry. This round keeps the same FR4 stackup and
focuses on small feed-transition adjustments around that point, especially
for S11/S22 recovery without disturbing the 5 GHz stopband.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import replace
from pathlib import Path

from generate_interdigital_filter_layout import FilterParams, write_outputs


FIELDNAMES = [
    "name",
    "L_mm",
    "tap_mm",
    "Egap_mm",
    "S1_mm",
    "S2_mm",
    "S3_mm",
    "S4_mm",
    "S5_mm",
    "S6_mm",
    "feed_taper_len_mm",
    "feed_tip_w_mm",
    "feed_overlap_mm",
    "via_diameter_mm",
    "metal_layer",
    "via_layer",
    "notes",
]


def fmt(value: float) -> str:
    return f"{value:.4f}".rstrip("0").rstrip(".")


def load_seed(path: Path) -> FilterParams:
    data = json.loads(path.read_text(encoding="utf-8"))
    params = data["parameters"]
    return FilterParams(
        name=str(params["name"]),
        order=int(params["order"]),
        substrate=str(params["substrate"]),
        er=float(params["er"]),
        dielectric_height_mm=float(params["dielectric_height_mm"]),
        copper_thickness_mm=float(params["copper_thickness_mm"]),
        lower_cutoff_ghz=float(params["lower_cutoff_ghz"]),
        upper_cutoff_ghz=float(params["upper_cutoff_ghz"]),
        passband_ripple_db=float(params["passband_ripple_db"]),
        z0_ohm=float(params["z0_ohm"]),
        w0_mm=float(params["w0_mm"]),
        resonator_w_mm=float(params["resonator_w_mm"]),
        resonator_l_mm=float(params["resonator_l_mm"]),
        tap_from_bottom_mm=float(params["tap_from_bottom_mm"]),
        end_gap_mm=float(params["end_gap_mm"]),
        gaps_mm=tuple(float(value) for value in params["gaps_mm"]),
        feed_len_mm=float(params["feed_len_mm"]),
        feed_taper_len_mm=float(params["feed_taper_len_mm"]),
        feed_tip_w_mm=float(params["feed_tip_w_mm"]),
        feed_overlap_mm=float(params["feed_overlap_mm"]),
        boundary_margin_mm=float(params["boundary_margin_mm"]),
        min_fab_feature_mm=float(params["min_fab_feature_mm"]),
        metal_layer=str(params["metal_layer"]),
        via_layer=str(params["via_layer"]),
        via_diameter_mm=float(params["via_diameter_mm"]),
        via_pad_mm=float(params["via_pad_mm"]),
        via_half_outside=bool(params["via_half_outside"]),
        via_pad_outside=bool(params["via_pad_outside"]),
    )


def row_from_params(params: FilterParams, notes: str) -> dict[str, str]:
    gaps = list(params.gaps_mm)
    if len(gaps) != 6:
        raise ValueError("expected 6 gaps for the 7th-order layout")
    return {
        "name": params.name,
        "L_mm": fmt(params.resonator_l_mm),
        "tap_mm": fmt(params.tap_from_bottom_mm),
        "Egap_mm": fmt(params.end_gap_mm),
        "S1_mm": fmt(gaps[0]),
        "S2_mm": fmt(gaps[1]),
        "S3_mm": fmt(gaps[2]),
        "S4_mm": fmt(gaps[3]),
        "S5_mm": fmt(gaps[4]),
        "S6_mm": fmt(gaps[5]),
        "feed_taper_len_mm": fmt(params.feed_taper_len_mm),
        "feed_tip_w_mm": fmt(params.feed_tip_w_mm),
        "feed_overlap_mm": fmt(params.feed_overlap_mm),
        "via_diameter_mm": fmt(params.via_diameter_mm),
        "metal_layer": params.metal_layer,
        "via_layer": params.via_layer,
        "notes": notes,
    }


def make_variant(seed: FilterParams, name: str, notes: str, **updates: object) -> tuple[FilterParams, dict[str, str]]:
    params = replace(seed, name=name, **updates)
    return params, row_from_params(params, notes)


def build_round3(seed: FilterParams) -> list[tuple[FilterParams, dict[str, str]]]:
    base = seed
    rows: list[tuple[FilterParams, dict[str, str]]] = []

    rows.append(make_variant(base, "i7_fr4_r3_base", "repeat round2 best point as the baseline"))
    rows.append(
        make_variant(
            base,
            "i7_fr4_r3_t194",
            "slightly lower tap to see whether input match improves",
            tap_from_bottom_mm=1.94,
        )
    )
    rows.append(
        make_variant(
            base,
            "i7_fr4_r3_t196",
            "slightly higher tap to check the opposite match direction",
            tap_from_bottom_mm=1.96,
        )
    )
    rows.append(
        make_variant(
            base,
            "i7_fr4_r3_t195_tl045",
            "shorter taper at the current tap to tighten the feed transition",
            feed_taper_len_mm=0.45,
        )
    )
    rows.append(
        make_variant(
            base,
            "i7_fr4_r3_t195_tl075",
            "longer taper at the current tap to smooth the feed transition",
            feed_taper_len_mm=0.75,
        )
    )
    rows.append(
        make_variant(
            base,
            "i7_fr4_r3_t195_tw016",
            "narrower taper tip to test stronger local coupling",
            feed_tip_w_mm=0.16,
        )
    )
    rows.append(
        make_variant(
            base,
            "i7_fr4_r3_t195_tw020",
            "slightly wider taper tip to compare match recovery",
            feed_tip_w_mm=0.20,
        )
    )
    rows.append(
        make_variant(
            base,
            "i7_fr4_r3_t195_tw022",
            "wider taper tip to test weaker local coupling",
            feed_tip_w_mm=0.22,
        )
    )
    rows.append(
        make_variant(
            base,
            "i7_fr4_r3_t195_ov004",
            "smaller taper overlap to reduce feed loading",
            feed_overlap_mm=0.04,
        )
    )
    rows.append(
        make_variant(
            base,
            "i7_fr4_r3_t195_ov008",
            "larger taper overlap to increase feed loading",
            feed_overlap_mm=0.08,
        )
    )
    rows.append(
        make_variant(
            base,
            "i7_fr4_r3_t194_tl045",
            "combined lower tap and shorter taper for a tighter input launch",
            tap_from_bottom_mm=1.94,
            feed_taper_len_mm=0.45,
        )
    )
    rows.append(
        make_variant(
            base,
            "i7_fr4_r3_t196_tl075",
            "combined higher tap and longer taper for a looser input launch",
            tap_from_bottom_mm=1.96,
            feed_taper_len_mm=0.75,
        )
    )
    return rows


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Generate the next FR4 7th-order interdigital candidate set.")
    parser.add_argument(
        "--seed",
        type=Path,
        default=root / "SIM" / "ADS" / "interdigital_7o_fr4_210um_round2" / "i7_fr4_r2_base_params.json",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=root / "SIM" / "ADS" / "interdigital_7o_fr4_210um_round3",
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=root / "SIM" / "ADS" / "filter_opt_i7_fr4_round3.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seed = load_seed(args.seed)
    rows = build_round3(seed)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    plan_rows: list[dict[str, str]] = []
    print(f"Generating {len(rows)} candidates into {args.out_dir}")
    for params, row in rows:
        outputs = write_outputs(params, args.out_dir)
        plan_rows.append(row)
        print(f"  {params.name}: {outputs['dxf_mm_coords']}")

    args.plan.parent.mkdir(parents=True, exist_ok=True)
    with args.plan.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(plan_rows)

    print(f"Wrote plan: {args.plan}")


if __name__ == "__main__":
    main()
