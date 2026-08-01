#!/usr/bin/env python3
"""Generate a theory-guided FR4 7th-order interdigital refinement plan.

Round6 keeps the 50-ohm line fixed and uses the current hard-pass baseline as
the primary seed. The round3 ``tw020`` result is retained only as a control:
it improved the 8 GHz edge and S11 trend, but missed the 5 GHz stopband target
by about 0.03 dB. This round therefore nudges the baseline in smaller steps and
only tests a few compensated ``tw020`` combinations.
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


def symmetric_outer_gap(seed: FilterParams, value: float) -> tuple[float, ...]:
    gaps = list(seed.gaps_mm)
    gaps[0] = max(seed.min_fab_feature_mm, value)
    gaps[-1] = max(seed.min_fab_feature_mm, value)
    return tuple(gaps)


def symmetric_inner_gap(seed: FilterParams, value: float) -> tuple[float, ...]:
    gaps = list(seed.gaps_mm)
    gaps[1] = value
    gaps[-2] = value
    return tuple(gaps)


def build_round6(base_seed: FilterParams, tw020_seed: FilterParams) -> list[tuple[FilterParams, dict[str, str]]]:
    rows: list[tuple[FilterParams, dict[str, str]]] = []

    base = replace(base_seed, name="i7_fr4_r6_base")
    tw020 = replace(tw020_seed, name="i7_fr4_r6_tw020")

    rows.append((base, row_from_params(base, "repeat current best hard-pass baseline")))
    rows.append(make_variant(base_seed, "i7_fr4_r6_base_l5545", "baseline plus slight L shortening; preserve 5 GHz margin and test 8 GHz edge", resonator_l_mm=5.545))
    rows.append(make_variant(base_seed, "i7_fr4_r6_base_l5540", "baseline plus moderate L shortening; watch 6 GHz entry", resonator_l_mm=5.540))
    rows.append(make_variant(base_seed, "i7_fr4_r6_base_l5535", "baseline plus stronger L shortening; stop if 6 GHz degrades", resonator_l_mm=5.535))

    rows.append(make_variant(base_seed, "i7_fr4_r6_base_tw0185", "baseline with very small tip widening for Qe trim", feed_tip_w_mm=0.185))
    rows.append(make_variant(base_seed, "i7_fr4_r6_base_tw0190", "baseline with small tip widening for Qe trim", feed_tip_w_mm=0.190))
    rows.append(make_variant(base_seed, "i7_fr4_r6_base_tw0195", "baseline with intermediate tip before tw020 limit", feed_tip_w_mm=0.195))
    rows.append((tw020, row_from_params(tw020, "tw020 control: better 8 GHz/S11 trend but 5 GHz is marginal")))

    rows.append(make_variant(base_seed, "i7_fr4_r6_base_e472", "baseline plus lower end gap to compare high-edge support", end_gap_mm=0.4723))
    rows.append(make_variant(base_seed, "i7_fr4_r6_base_e492", "baseline plus higher end gap to test stopband/match compensation", end_gap_mm=0.4923))
    rows.append(
        make_variant(
            base_seed,
            "i7_fr4_r6_base_l5545_tw0190",
            "baseline mild L shortening plus small tip widening",
            resonator_l_mm=5.545,
            feed_tip_w_mm=0.190,
        )
    )
    rows.append(
        make_variant(
            base_seed,
            "i7_fr4_r6_base_l5545_tw0195",
            "baseline mild L shortening plus intermediate tip widening",
            resonator_l_mm=5.545,
            feed_tip_w_mm=0.195,
        )
    )

    rows.append(make_variant(tw020_seed, "i7_fr4_r6_tw020_l5545", "tw020 plus slight L shortening for 5 GHz recovery", resonator_l_mm=5.545))
    rows.append(make_variant(tw020_seed, "i7_fr4_r6_tw020_l5540", "tw020 plus moderate L shortening for 5 GHz recovery", resonator_l_mm=5.540))
    rows.append(make_variant(tw020_seed, "i7_fr4_r6_tw020_e492", "tw020 plus higher end gap to recover 5 GHz stopband margin", end_gap_mm=0.4923))
    rows.append(
        make_variant(
            tw020_seed,
            "i7_fr4_r6_tw020_l5545_e492",
            "combine mild L shortening and higher end gap for stopband compensation",
            resonator_l_mm=5.545,
            end_gap_mm=0.4923,
        )
    )
    rows.append(
        make_variant(
            tw020_seed,
            "i7_fr4_r6_tw020_l5545_s2p",
            "mild L shortening plus slightly weaker second-pair coupling",
            resonator_l_mm=5.545,
            gaps_mm=symmetric_inner_gap(tw020_seed, 0.1800),
        )
    )

    return rows


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Generate a theory-guided FR4 7th-order interdigital candidate set.")
    parser.add_argument(
        "--base-seed",
        type=Path,
        default=root / "SIM" / "ADS" / "interdigital_7o_fr4_210um_round3" / "i7_fr4_r3_base_params.json",
    )
    parser.add_argument(
        "--tw020-seed",
        type=Path,
        default=root / "SIM" / "ADS" / "interdigital_7o_fr4_210um_round3" / "i7_fr4_r3_t195_tw020_params.json",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=root / "SIM" / "ADS" / "interdigital_7o_fr4_210um_round6",
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=root / "SIM" / "ADS" / "filter_opt_i7_fr4_round6.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_seed = load_seed(args.base_seed)
    tw020_seed = load_seed(args.tw020_seed)
    rows = build_round6(base_seed, tw020_seed)

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
