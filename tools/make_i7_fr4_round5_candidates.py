#!/usr/bin/env python3
"""Generate a feed-impedance refinement plan for the FR4 interdigital filter."""

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
    "W0_mm",
    "feed_len_mm",
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
        "W0_mm": fmt(params.w0_mm),
        "feed_len_mm": fmt(params.feed_len_mm),
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


def build_round5(seed: FilterParams) -> list[tuple[FilterParams, dict[str, str]]]:
    base = seed
    rows: list[tuple[FilterParams, dict[str, str]]] = []

    rows.append(make_variant(base, "i7_fr4_r5_base", "repeat current baseline with home stackup"))
    rows.append(make_variant(base, "i7_fr4_r5_w0335", "narrower feedline; higher feed impedance trial", w0_mm=0.335))
    rows.append(make_variant(base, "i7_fr4_r5_w0345", "slightly narrower feedline", w0_mm=0.345))
    rows.append(make_variant(base, "i7_fr4_r5_w0385", "slightly wider feedline", w0_mm=0.385))
    rows.append(make_variant(base, "i7_fr4_r5_w0405", "wider feedline; lower feed impedance trial", w0_mm=0.405))
    rows.append(make_variant(base, "i7_fr4_r5_len250", "shorter straight feed section", feed_len_mm=2.50))
    rows.append(make_variant(base, "i7_fr4_r5_len350", "slightly longer straight feed section", feed_len_mm=3.50))
    rows.append(make_variant(base, "i7_fr4_r5_len400", "longer straight feed section for impedance-transform test", feed_len_mm=4.00))
    rows.append(
        make_variant(
            base,
            "i7_fr4_r5_w0345_len350",
            "narrow feedline with slightly longer straight section",
            w0_mm=0.345,
            feed_len_mm=3.50,
        )
    )
    rows.append(
        make_variant(
            base,
            "i7_fr4_r5_w0385_len350",
            "wide feedline with slightly longer straight section",
            w0_mm=0.385,
            feed_len_mm=3.50,
        )
    )
    rows.append(
        make_variant(
            base,
            "i7_fr4_r5_w0345_len400",
            "narrow feedline with longer straight section",
            w0_mm=0.345,
            feed_len_mm=4.00,
        )
    )
    rows.append(
        make_variant(
            base,
            "i7_fr4_r5_w0385_len400",
            "wide feedline with longer straight section",
            w0_mm=0.385,
            feed_len_mm=4.00,
        )
    )
    return rows


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Generate a feed-impedance FR4 7th-order candidate set.")
    parser.add_argument(
        "--seed",
        type=Path,
        default=root / "SIM" / "ADS" / "interdigital_7o_fr4_210um_round3" / "i7_fr4_r3_base_params.json",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=root / "SIM" / "ADS" / "interdigital_7o_fr4_210um_round5",
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=root / "SIM" / "ADS" / "filter_opt_i7_fr4_round5.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seed = load_seed(args.seed)
    rows = build_round5(seed)

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
