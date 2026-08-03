#!/usr/bin/env python3
"""Generate round9 interdigital candidates with small asymmetric gap deltas."""

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

from simads.nn.interdigital_features import PARAM_COLUMNS

from layout.generate_interdigital_filter_layout import FilterParams, write_outputs


FIELDNAMES = ["name", *PARAM_COLUMNS, "metal_layer", "via_layer", "notes"]
MIN_GAP_MM = 0.1016


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


def center_row(seed: FilterParams) -> dict[str, float]:
    s1, s2, s3, s4, s5, s6 = seed.gaps_mm
    return {
        "L_mm": seed.resonator_l_mm,
        "tap_mm": seed.tap_from_bottom_mm,
        "Egap_mm": seed.end_gap_mm,
        "S1_mm": s1,
        "S2_mm": s2,
        "S3_mm": s3,
        "S4_mm": s4,
        "S5_mm": s5,
        "S6_mm": s6,
        "W0_mm": seed.w0_mm,
        "feed_len_mm": seed.feed_len_mm,
        "feed_taper_len_mm": seed.feed_taper_len_mm,
        "feed_tip_w_mm": seed.feed_tip_w_mm,
        "feed_overlap_mm": seed.feed_overlap_mm,
        "via_diameter_mm": seed.via_diameter_mm,
    }


def row_from_latent(seed: FilterParams, item: np.ndarray) -> dict[str, float]:
    base = center_row(seed)
    keys = ["L_mm", "tap_mm", "Egap_mm", "S1_mean", "S2_mean", "S3_mean", "W0_mm", "feed_taper_len_mm", "feed_tip_w_mm", "feed_overlap_mm"]
    values = dict(zip(keys, item[: len(keys)], strict=True))
    d16, d25, d34 = item[len(keys) :]
    s1_mean = float(values["S1_mean"])
    s2_mean = float(values["S2_mean"])
    s3_mean = float(values["S3_mean"])
    row = dict(base)
    for key in ("L_mm", "tap_mm", "Egap_mm", "W0_mm", "feed_taper_len_mm", "feed_tip_w_mm", "feed_overlap_mm"):
        row[key] = float(values[key])
    row["S1_mm"] = max(MIN_GAP_MM, s1_mean + 0.5 * float(d16))
    row["S6_mm"] = max(MIN_GAP_MM, s1_mean - 0.5 * float(d16))
    row["S2_mm"] = max(MIN_GAP_MM, s2_mean + 0.5 * float(d25))
    row["S5_mm"] = max(MIN_GAP_MM, s2_mean - 0.5 * float(d25))
    row["S3_mm"] = max(MIN_GAP_MM, s3_mean + 0.5 * float(d34))
    row["S4_mm"] = max(MIN_GAP_MM, s3_mean - 0.5 * float(d34))
    row["feed_len_mm"] = seed.feed_len_mm
    row["via_diameter_mm"] = seed.via_diameter_mm
    return {key: row[key] for key in PARAM_COLUMNS}


def bounds_from_seed(seed: FilterParams) -> tuple[np.ndarray, np.ndarray]:
    s1, s2, s3, s4, s5, s6 = seed.gaps_mm
    center = np.asarray(
        [
            seed.resonator_l_mm,
            seed.tap_from_bottom_mm,
            seed.end_gap_mm,
            0.5 * (s1 + s6),
            0.5 * (s2 + s5),
            0.5 * (s3 + s4),
            seed.w0_mm,
            seed.feed_taper_len_mm,
            seed.feed_tip_w_mm,
            seed.feed_overlap_mm,
            0.0,
            0.0,
            0.0,
        ],
        dtype=float,
    )
    span = np.asarray([0.010, 0.014, 0.014, 0.006, 0.007, 0.006, 0.010, 0.090, 0.035, 0.007, 0.010, 0.010, 0.008], dtype=float)
    lower = center - span
    upper = center + span
    lower[3:6] = np.maximum(lower[3:6], MIN_GAP_MM + 0.004)
    lower[8] = max(lower[8], 0.17)
    upper[8] = min(upper[8], 0.22)
    lower[9] = max(lower[9], 0.050)
    upper[9] = min(upper[9], 0.072)
    return lower, upper


def sample_pool(seed: FilterParams, rng: np.random.Generator, count: int, span_scale: float) -> list[dict[str, float]]:
    lower, upper = bounds_from_seed(seed)
    if span_scale <= 0.0:
        raise ValueError("--span-scale must be > 0")
    if span_scale != 1.0:
        center = 0.5 * (lower + upper)
        half_span = 0.5 * (upper - lower) * span_scale
        lower = center - half_span
        upper = center + half_span
        lower[3:6] = np.maximum(lower[3:6], MIN_GAP_MM + 0.004)
        lower[8] = max(lower[8], 0.17)
        upper[8] = min(upper[8], 0.22)
        lower[9] = max(lower[9], 0.050)
        upper[9] = min(upper[9], 0.072)
    uniform_count = max(count // 2, 1)
    uniform = lower + latin_hypercube(rng, uniform_count, len(lower)) * (upper - lower)
    center = 0.5 * (lower + upper)
    sigma = (upper - lower) / 5.0
    local = rng.normal(center, sigma, size=(count - uniform_count, len(lower)))
    local = np.clip(local, lower, upper)
    values = np.vstack([uniform, local])
    rows = [center_row(seed)]
    rows.extend(row_from_latent(seed, item) for item in values)
    return rows[:count]


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
    parser = argparse.ArgumentParser(description="Generate round9 refined-NN candidates with asymmetric gap deltas.")
    parser.add_argument(
        "--seed-params",
        type=Path,
        default=root
        / "projects"
        / "bfp_6_8g_i7_fr4"
        / "layouts"
        / "interdigital_7o_fr4_210um_round8_refined_nn_pool"
        / "i7_fr4_r8_nn0447_params.json",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=root / "projects" / "bfp_6_8g_i7_fr4" / "layouts" / "interdigital_7o_fr4_210um_round9_asym_gap_nn_pool",
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=root / "projects" / "bfp_6_8g_i7_fr4" / "plans" / "filter_opt_i7_fr4_round9_asym_gap_nn_pool.csv",
    )
    parser.add_argument("--count", type=int, default=768)
    parser.add_argument("--seed", type=int, default=909)
    parser.add_argument("--name-prefix", default="i7_fr4_r9_asym")
    parser.add_argument("--notes", default="round9 asym-gap refined-NN pool around ADS-best i7_fr4_r8_nn0447")
    parser.add_argument("--span-scale", type=float, default=1.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seed_params = read_seed(args.seed_params)
    rng = np.random.default_rng(args.seed)
    rows = sample_pool(seed_params, rng, args.count, args.span_scale)
    plan_rows: list[dict[str, str]] = []
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for idx, row in enumerate(rows, start=1):
        name = f"{args.name_prefix}{idx:04d}"
        params = params_from_row(seed_params, name, row)
        write_outputs(params, args.out_dir)
        plan_rows.append(
            {
                "name": name,
                **{key: fmt(row[key]) for key in PARAM_COLUMNS},
                "metal_layer": seed_params.metal_layer,
                "via_layer": seed_params.via_layer,
                "notes": args.notes,
            }
        )
    write_plan(args.plan, plan_rows)
    print(f"Wrote {len(plan_rows)} candidate layouts: {args.out_dir}")
    print(f"Wrote plan: {args.plan}")


if __name__ == "__main__":
    main()
