#!/usr/bin/env python3
"""Generate round8 refined-NN trust-region interdigital candidates."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import replace
from pathlib import Path
import sys

import numpy as np

_SIM_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _SIM_ROOT / "src"
_TOOLS_ROOT = _SIM_ROOT / "tools"
for _path in (_SRC_ROOT, _TOOLS_ROOT):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from simads.nn.interdigital_features import LEGACY_CENTER, PARAM_COLUMNS, TRUST_BOUNDS

from layout.generate_interdigital_filter_layout import FilterParams, write_outputs


FIELDNAMES = [
    "name",
    *PARAM_COLUMNS,
    "metal_layer",
    "via_layer",
    "notes",
]


def repo_root() -> Path:
    return _SIM_ROOT


def fmt(value: float) -> str:
    return f"{value:.5f}".rstrip("0").rstrip(".")


def read_seed(path: Path) -> FilterParams:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    p = data["parameters"]
    return FilterParams(
        name=str(p["name"]),
        order=int(p["order"]),
        substrate=str(p["substrate"]),
        er=float(p["er"]),
        dielectric_height_mm=float(p["dielectric_height_mm"]),
        copper_thickness_mm=float(p["copper_thickness_mm"]),
        lower_cutoff_ghz=float(p["lower_cutoff_ghz"]),
        upper_cutoff_ghz=float(p["upper_cutoff_ghz"]),
        passband_ripple_db=float(p["passband_ripple_db"]),
        z0_ohm=float(p["z0_ohm"]),
        w0_mm=float(p["w0_mm"]),
        resonator_w_mm=float(p["resonator_w_mm"]),
        resonator_l_mm=float(p["resonator_l_mm"]),
        tap_from_bottom_mm=float(p["tap_from_bottom_mm"]),
        end_gap_mm=float(p["end_gap_mm"]),
        gaps_mm=tuple(float(value) for value in p["gaps_mm"]),
        feed_len_mm=float(p["feed_len_mm"]),
        feed_taper_len_mm=float(p["feed_taper_len_mm"]),
        feed_tip_w_mm=float(p["feed_tip_w_mm"]),
        feed_overlap_mm=float(p["feed_overlap_mm"]),
        boundary_margin_mm=float(p["boundary_margin_mm"]),
        min_fab_feature_mm=float(p["min_fab_feature_mm"]),
        metal_layer=str(p["metal_layer"]),
        via_layer=str(p["via_layer"]),
        via_diameter_mm=float(p["via_diameter_mm"]),
        via_pad_mm=float(p["via_pad_mm"]),
        via_half_outside=bool(p["via_half_outside"]),
        via_pad_outside=bool(p["via_pad_outside"]),
    )


def latin_hypercube(rng: np.random.Generator, count: int, dims: int) -> np.ndarray:
    result = np.empty((count, dims), dtype=float)
    base = (np.arange(count, dtype=float) + rng.random(count)) / count
    for dim in range(dims):
        result[:, dim] = rng.permutation(base)
    return result


def sample_pool(rng: np.random.Generator, count: int) -> list[dict[str, float]]:
    latent = [
        "L_mm",
        "tap_mm",
        "Egap_mm",
        "S1_mm",
        "S2_mm",
        "S3_mm",
        "W0_mm",
        "feed_taper_len_mm",
        "feed_tip_w_mm",
        "feed_overlap_mm",
    ]
    bounds = np.asarray([TRUST_BOUNDS[name] for name in latent], dtype=float)
    uniform_count = max(count // 2, 1)
    uniform = bounds[:, 0] + latin_hypercube(rng, uniform_count, len(latent)) * (bounds[:, 1] - bounds[:, 0])
    center = np.asarray([LEGACY_CENTER[name] for name in latent], dtype=float)
    sigma = (bounds[:, 1] - bounds[:, 0]) / 5.0
    local = rng.normal(center, sigma, size=(count - uniform_count, len(latent)))
    local = np.clip(local, bounds[:, 0], bounds[:, 1])
    values = np.vstack([uniform, local])
    rows: list[dict[str, float]] = []
    for item in values:
        row = dict(LEGACY_CENTER)
        for key, value in zip(latent, item, strict=True):
            row[key] = float(value)
        row["S6_mm"] = row["S1_mm"]
        row["S5_mm"] = row["S2_mm"]
        row["S4_mm"] = row["S3_mm"]
        row["feed_len_mm"] = LEGACY_CENTER["feed_len_mm"]
        row["via_diameter_mm"] = LEGACY_CENTER["via_diameter_mm"]
        rows.append({key: row[key] for key in PARAM_COLUMNS})
    return rows


def params_from_row(seed: FilterParams, name: str, row: dict[str, float]) -> FilterParams:
    return replace(
        seed,
        name=name,
        resonator_l_mm=row["L_mm"],
        tap_from_bottom_mm=row["tap_mm"],
        end_gap_mm=row["Egap_mm"],
        gaps_mm=(row["S1_mm"], row["S2_mm"], row["S3_mm"], row["S4_mm"], row["S5_mm"], row["S6_mm"]),
        w0_mm=row["W0_mm"],
        resonator_w_mm=row["W0_mm"],
        feed_len_mm=row["feed_len_mm"],
        feed_taper_len_mm=row["feed_taper_len_mm"],
        feed_tip_w_mm=row["feed_tip_w_mm"],
        feed_overlap_mm=row["feed_overlap_mm"],
        via_diameter_mm=row["via_diameter_mm"],
    )


def write_plan(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Generate round8 refined-NN interdigital trust-region candidates.")
    parser.add_argument("--seed-params", type=Path, default=root / "projects" / "bfp_6_8g_i7_fr4" / "layouts" / "interdigital_7o_fr4_210um_round3" / "i7_fr4_r3_base_params.json")
    parser.add_argument("--out-dir", type=Path, default=root / "projects" / "bfp_6_8g_i7_fr4" / "layouts" / "interdigital_7o_fr4_210um_round8_refined_nn_pool")
    parser.add_argument("--plan", type=Path, default=root / "projects" / "bfp_6_8g_i7_fr4" / "plans" / "filter_opt_i7_fr4_round8_refined_nn_pool.csv")
    parser.add_argument("--count", type=int, default=512)
    parser.add_argument("--seed", type=int, default=808)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seed_params = read_seed(args.seed_params)
    rng = np.random.default_rng(args.seed)
    rows = sample_pool(rng, args.count)
    plan_rows: list[dict[str, str]] = []
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for idx, row in enumerate(rows, start=1):
        name = f"i7_fr4_r8_nn{idx:04d}"
        params = params_from_row(seed_params, name, row)
        write_outputs(params, args.out_dir)
        plan_rows.append(
            {
                "name": name,
                **{key: fmt(row[key]) for key in PARAM_COLUMNS},
                "metal_layer": seed_params.metal_layer,
                "via_layer": seed_params.via_layer,
                "notes": "round8 refined-NN symmetric trust-region pool around i7_fr4_r1_l555_taper",
            }
        )
    write_plan(args.plan, plan_rows)
    print(f"Wrote {len(plan_rows)} candidate layouts: {args.out_dir}")
    print(f"Wrote plan: {args.plan}")


if __name__ == "__main__":
    main()

