#!/usr/bin/env python3
"""Generate a second refinement plan around the best round1 candidates."""

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


def clone_variant(seed: dict[str, object], name: str, notes: str, *, l_mm: float | None = None, tap_mm: float | None = None) -> dict[str, str]:
    params = deepcopy(seed)
    params["name"] = name
    if l_mm is not None:
        params["resonator_l_mm"] = l_mm
    if tap_mm is not None:
        params["tap_from_bottom_mm"] = tap_mm
    return row_from_params(params, str(params["name"]), notes)


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Generate a second ADS optimization plan around the best round1 candidates.")
    parser.add_argument(
        "--seed-all",
        type=Path,
        default=root
        / "SIM"
        / "ADS"
        / "opt_round1"
        / "interdigital_9o_ro4350b_508um_v4_more_coupling_r1_all_gaps_minus_params.json",
    )
    parser.add_argument(
        "--seed-edge",
        type=Path,
        default=root
        / "SIM"
        / "ADS"
        / "opt_round1"
        / "interdigital_9o_ro4350b_508um_v4_more_coupling_r1_tap190_edge_plus_params.json",
    )
    parser.add_argument("--out", type=Path, default=root / "SIM" / "ADS" / "filter_opt_round2.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seed_all = load_params(args.seed_all)
    seed_edge = load_params(args.seed_edge)

    rows = [
        clone_variant(seed_all, "r2a_l595", "seed=all_gaps_minus; shorten resonator to raise passband and 5 GHz rejection", l_mm=5.95),
        clone_variant(seed_all, "r2a_l600", "seed=all_gaps_minus; near-nominal length check around best passband case", l_mm=6.00),
        clone_variant(seed_all, "r2a_l605", "seed=all_gaps_minus; lengthen slightly to see if 6 GHz edge recovers", l_mm=6.05),
        clone_variant(seed_all, "r2a_t200", "seed=all_gaps_minus; slightly lower tap on the best passband case", tap_mm=2.00),
        clone_variant(seed_all, "r2a_t200_l600", "seed=all_gaps_minus; combined tap and length refinement", l_mm=6.00, tap_mm=2.00),
        clone_variant(seed_edge, "r2e_l595", "seed=tap190_edge_plus; shorten and preserve edge suppression", l_mm=5.95),
        clone_variant(seed_edge, "r2e_l600", "seed=tap190_edge_plus; near-nominal length", l_mm=6.00),
        clone_variant(seed_edge, "r2e_l605", "seed=tap190_edge_plus; slightly longer length", l_mm=6.05),
        clone_variant(seed_edge, "r2e_t185", "seed=tap190_edge_plus; lower tap a bit to recover passband insertion", tap_mm=1.85),
        clone_variant(seed_edge, "r2e_t195", "seed=tap190_edge_plus; small tap increase for match check", tap_mm=1.95),
    ]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} candidates: {args.out}")
    for row in rows:
        print(f"  {row['name']}: L={row['L_mm']} tap={row['tap_mm']} notes={row['notes']}")


if __name__ == "__main__":
    main()
