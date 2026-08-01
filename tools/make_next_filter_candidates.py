#!/usr/bin/env python3
"""Create the next heuristic ADS filter optimization plan."""

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


def clamp_gap(value: float, min_feature: float) -> float:
    return max(min_feature, value)


def load_params(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["parameters"]


def make_row(params: dict[str, object], name: str, notes: str) -> dict[str, str]:
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


def variant(base: dict[str, object], suffix: str, notes: str, **updates: object) -> dict[str, str]:
    params = deepcopy(base)
    name_base = str(base["name"]).removesuffix("_mm_coords")
    params["name"] = f"{name_base}_{suffix}"
    for key, value in updates.items():
        params[key] = value
    return make_row(params, str(params["name"]), notes)


def symmetric_gap_update(base: dict[str, object], deltas: list[float]) -> list[float]:
    gaps = [float(value) for value in base["gaps_mm"]]
    min_feature = float(base["min_fab_feature_mm"])
    return [round(clamp_gap(gap + delta, min_feature), 4) for gap, delta in zip(gaps, deltas, strict=True)]


def build_round1(base: dict[str, object]) -> list[dict[str, str]]:
    tap0 = float(base["tap_from_bottom_mm"])
    rows = [
        make_row(base, f"{base['name']}_r1_base_repeat", "repeat current V4 through the batch loop"),
    ]

    for tap in (1.70, 1.90, 2.30, 2.55):
        rows.append(
            variant(
                base,
                f"r1_tap{int(round(tap * 100)):03d}",
                "tap sweep for 6-8 GHz return loss and edge insertion",
                tap_from_bottom_mm=tap,
            )
        )

    rows.append(
        variant(
            base,
            "r1_end_gap_small",
            "smaller end gap to test edge coupling without changing minimum line space below process limit",
            end_gap_mm=0.47,
        )
    )
    rows.append(
        variant(
            base,
            "r1_edge_gaps_plus",
            "larger S1/S8 and S2/S7 to test 5 GHz rejection recovery",
            gaps_mm=symmetric_gap_update(base, [0.035, 0.020, 0.0, 0.0, 0.0, 0.0, 0.020, 0.035]),
        )
    )
    rows.append(
        variant(
            base,
            "r1_all_gaps_minus",
            "slightly stronger overall coupling to recover 6/8 GHz insertion",
            gaps_mm=symmetric_gap_update(base, [-0.020, -0.020, -0.015, -0.015, -0.015, -0.015, -0.020, -0.020]),
        )
    )
    rows.append(
        variant(
            base,
            "r1_tap190_edge_plus",
            "combine lower tap with more 5 GHz rejection from larger edge gaps",
            tap_from_bottom_mm=1.90,
            gaps_mm=symmetric_gap_update(base, [0.030, 0.015, 0.0, 0.0, 0.0, 0.0, 0.015, 0.030]),
        )
    )
    rows.append(
        variant(
            base,
            "r1_tap230_all_minus",
            "combine upper tap with stronger coupling to improve passband edges",
            tap_from_bottom_mm=2.30,
            gaps_mm=symmetric_gap_update(base, [-0.015, -0.015, -0.010, -0.010, -0.010, -0.010, -0.015, -0.015]),
        )
    )

    if abs(tap0 - 2.143) > 1e-6:
        rows.append(variant(base, "r1_original_tap", "restore original V4 tap as a control", tap_from_bottom_mm=2.143))

    return rows


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Build the next small ADS/FEM optimization plan.")
    parser.add_argument(
        "--base-params",
        type=Path,
        default=root / "SIM" / "ADS" / "sweep" / "interdigital_9o_ro4350b_508um_v4_more_coupling_params.json",
    )
    parser.add_argument("--out", type=Path, default=root / "SIM" / "ADS" / "filter_opt_round1.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base = load_params(args.base_params)
    rows = build_round1(base)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} candidates: {args.out}")
    for row in rows:
        print(f"  {row['name']}: tap={row['tap_mm']} S1/S8={row['S1_mm']}/{row['S8_mm']} notes={row['notes']}")


if __name__ == "__main__":
    main()
