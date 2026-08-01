#!/usr/bin/env python3
"""Generate a third refinement plan around r2e_l595."""

from __future__ import annotations

import argparse
import csv
import json
from copy import deepcopy
from pathlib import Path


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
    "S7_mm",
    "S8_mm",
    "via_diameter_mm",
    "metal_layer",
    "via_layer",
    "notes",
]


def fmt(value: float) -> str:
    return f"{value:.4f}".rstrip("0").rstrip(".")


def load_params(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["parameters"]


def row_from_params(params: dict[str, object], name: str, notes: str) -> dict[str, str]:
    gaps = [float(value) for value in params["gaps_mm"]]
    return {
        "name": name,
        "L_mm": fmt(float(params["resonator_l_mm"])),
        "tap_mm": fmt(float(params["tap_from_bottom_mm"])),
        "Egap_mm": fmt(float(params["end_gap_mm"])),
        "S1_mm": fmt(gaps[0]),
        "S2_mm": fmt(gaps[1]),
        "S3_mm": fmt(gaps[2]),
        "S4_mm": fmt(gaps[3]),
        "S5_mm": fmt(gaps[4]),
        "S6_mm": fmt(gaps[5]),
        "S7_mm": fmt(gaps[6]),
        "S8_mm": fmt(gaps[7]),
        "via_diameter_mm": fmt(float(params["via_diameter_mm"])),
        "metal_layer": str(params["metal_layer"]),
        "via_layer": str(params["via_layer"]),
        "notes": notes,
    }


def with_updates(seed: dict[str, object], name: str, notes: str, **updates: object) -> dict[str, str]:
    params = deepcopy(seed)
    params["name"] = name
    params.update(updates)
    return row_from_params(params, name, notes)


def gap_variant(seed: dict[str, object], deltas: list[float]) -> list[float]:
    gaps = [float(value) for value in seed["gaps_mm"]]
    min_feature = float(seed["min_fab_feature_mm"])
    return [round(max(gap + delta, min_feature), 4) for gap, delta in zip(gaps, deltas, strict=True)]


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Generate a third ADS optimization plan around r2e_l595.")
    parser.add_argument(
        "--seed",
        type=Path,
        default=root / "SIM" / "ADS" / "opt_round2b" / "r2e_l595_params.json",
    )
    parser.add_argument("--out", type=Path, default=root / "SIM" / "ADS" / "filter_opt_round3.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seed = load_params(args.seed)

    rows = [
        with_updates(seed, "r3_base", "repeat r2e_l595 under round3 naming for baseline"),
        with_updates(seed, "r3_l592", "slightly shorter length to push 5 GHz rejection below -45 dB", resonator_l_mm=5.92),
        with_updates(seed, "r3_l597", "small length recovery toward lower passband edge", resonator_l_mm=5.97),
        with_updates(seed, "r3_t182", "tap moved down to test passband insertion and match", tap_from_bottom_mm=1.82),
        with_updates(seed, "r3_t187", "fine tap sweep below current best", tap_from_bottom_mm=1.87),
        with_updates(seed, "r3_t192", "fine tap sweep above current best", tap_from_bottom_mm=1.92),
        with_updates(
            seed,
            "r3_e540",
            "larger end gap to check stopband recovery at 5 GHz",
            end_gap_mm=0.54,
        ),
        with_updates(
            seed,
            "r3_e515",
            "smaller end gap to recover 6/8 GHz edge insertion",
            end_gap_mm=0.515,
        ),
        with_updates(
            seed,
            "r3_s1p",
            "increase S1/S8 for more 5 GHz rejection with minimal central impact",
            gaps_mm=gap_variant(seed, [0.015, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.015]),
        ),
        with_updates(
            seed,
            "r3_s1m",
            "decrease S1/S8 to recover edge insertion and compare rejection cost",
            gaps_mm=gap_variant(seed, [-0.015, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.015]),
        ),
        with_updates(
            seed,
            "r3_l597s1p",
            "combine slight length recovery with stronger outer stopband gap",
            resonator_l_mm=5.97,
            gaps_mm=gap_variant(seed, [0.015, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.015]),
        ),
    ]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} candidates: {args.out}")
    for row in rows:
        print(
            f"  {row['name']}: L={row['L_mm']} tap={row['tap_mm']} "
            f"Egap={row['Egap_mm']} S1/S8={row['S1_mm']}/{row['S8_mm']}"
        )


if __name__ == "__main__":
    main()
