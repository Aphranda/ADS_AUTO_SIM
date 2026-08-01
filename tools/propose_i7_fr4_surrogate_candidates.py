#!/usr/bin/env python3
"""Propose FR4 7th-order interdigital candidates with a trust-region surrogate.

This is intentionally dependency-light: only numpy is required. The model is a
bootstrap ensemble of ridge regressors over standardized layout parameters. It
is not a replacement for ADS/FEM; it is a decision layer that ranks a large
virtual candidate pool before spending FEM time.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
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

from simads import optimizer as opt
from simads.config import load_project

from generate_interdigital_filter_layout import FilterParams, write_outputs


PARAM_COLUMNS = [
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
]

METRIC_COLUMNS = [
    "s21_5g_db",
    "s21_6g_db",
    "s21_8g_db",
    "passband_min_s21_db",
    "passband_ripple_db",
    "worst_s11_6_8_db",
    "worst_s22_6_8_db",
]

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

TARGETS = {
    "s21_5g_db": -25.0,
    "s21_6g_db": -5.0,
    "s21_8g_db": -5.0,
    "passband_min_s21_db": -5.0,
    "passband_ripple_db": 4.0,
    "worst_s11_6_8_db": -6.0,
    "worst_s22_6_8_db": -6.0,
}

BOUNDS = {
    "L_mm": (5.535, 5.565),
    "tap_mm": (1.935, 1.965),
    "Egap_mm": (0.4723, 0.4923),
    "S1_mm": (0.1126, 0.1226),
    "S2_mm": (0.1700, 0.1820),
    "S3_mm": (0.1800, 0.1920),
    "S4_mm": (0.1800, 0.1920),
    "S5_mm": (0.1700, 0.1820),
    "S6_mm": (0.1126, 0.1226),
    "W0_mm": (0.3560, 0.3740),
    "feed_len_mm": (2.85, 3.25),
    "feed_taper_len_mm": (0.52, 0.66),
    "feed_tip_w_mm": (0.176, 0.202),
    "feed_overlap_mm": (0.052, 0.068),
    "via_diameter_mm": (0.254, 0.254),
}


def repo_root() -> Path:
    return _SIM_ROOT


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fp:
        return list(csv.DictReader(fp))


def parse_float(value: str | float | int | None) -> float:
    if value is None:
        return float("nan")
    text = str(value).strip()
    return float(text) if text else float("nan")


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


def row_to_vector(row: dict[str, str]) -> np.ndarray:
    return np.array([parse_float(row[key]) for key in PARAM_COLUMNS], dtype=float)


def geometry_key(values: np.ndarray) -> str:
    return "|".join(f"{value:.5f}" for value in values)


def aggregate_unique(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["geometry_key"], []).append(row)
    output: list[dict[str, str]] = []
    for members in grouped.values():
        best = max(members, key=lambda item: parse_float(item["objective_score"]))
        averaged = dict(best)
        for key in METRIC_COLUMNS + ["objective_score"]:
            values = [parse_float(member[key]) for member in members]
            averaged[key] = f"{float(np.mean(values)):.6g}"
        output.append(averaged)
    return output


def expand_features(x: np.ndarray) -> np.ndarray:
    return np.concatenate([np.ones((x.shape[0], 1)), x], axis=1)


def fit_ridge(x: np.ndarray, y: np.ndarray, ridge: float) -> tuple[np.ndarray, float, float]:
    y_mean = float(np.mean(y))
    y_std = float(np.std(y)) or 1.0
    yy = (y - y_mean) / y_std
    phi = expand_features(x)
    gram = phi.T @ phi
    reg = ridge * np.eye(gram.shape[0])
    reg[0, 0] = 0.0
    coef = np.linalg.pinv(gram + reg) @ phi.T @ yy
    return coef, y_mean, y_std


def predict_ridge(x: np.ndarray, model: tuple[np.ndarray, float, float]) -> np.ndarray:
    coef, y_mean, y_std = model
    return expand_features(x) @ coef * y_std + y_mean


def objective_from_metrics(metrics: np.ndarray) -> np.ndarray:
    s21_5 = metrics[:, 0]
    s21_6 = metrics[:, 1]
    s21_8 = metrics[:, 2]
    pass_min = metrics[:, 3]
    ripple = metrics[:, 4]
    s11 = metrics[:, 5]
    s22 = metrics[:, 6]
    margins = np.column_stack(
        [
            TARGETS["s21_5g_db"] - s21_5,
            s21_6 - TARGETS["s21_6g_db"],
            s21_8 - TARGETS["s21_8g_db"],
            pass_min - TARGETS["passband_min_s21_db"],
            TARGETS["passband_ripple_db"] - ripple,
        ]
    )
    hard_violation = np.sum(np.maximum(0.0, -margins) ** 2, axis=1)
    s11_gap = np.maximum(0.0, s11 - TARGETS["worst_s11_6_8_db"])
    s22_gap = np.maximum(0.0, s22 - TARGETS["worst_s22_6_8_db"])
    worst_return = np.maximum(s11, s22)
    stop_margin = TARGETS["s21_5g_db"] - s21_5
    edge_margin = np.minimum(s21_6 - TARGETS["s21_6g_db"], s21_8 - TARGETS["s21_8g_db"])
    return (
        20.0
        - 18.0 * hard_violation
        - 10.0 * (s11_gap * s11_gap + s22_gap * s22_gap)
        + 1.15 * (-worst_return)
        - 0.65 * ripple
        + 0.25 * np.minimum(stop_margin, 4.0)
        + 0.35 * np.minimum(edge_margin, 4.0)
    )


def standardize(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = np.mean(x, axis=0)
    std = np.std(x, axis=0)
    std[std < 1e-6] = 1.0
    return (x - mean) / std, mean, std


def latin_hypercube(rng: np.random.Generator, count: int, dims: int) -> np.ndarray:
    result = np.empty((count, dims), dtype=float)
    base = (np.arange(count, dtype=float) + rng.random(count)) / count
    for dim in range(dims):
        result[:, dim] = rng.permutation(base)
    return result


def symmetric_pool(rng: np.random.Generator, count: int, center: np.ndarray) -> np.ndarray:
    latent_names = [
        "L_mm",
        "tap_mm",
        "Egap_mm",
        "S1_mm",
        "S2_mm",
        "S3_mm",
        "W0_mm",
        "feed_len_mm",
        "feed_taper_len_mm",
        "feed_tip_w_mm",
        "feed_overlap_mm",
    ]
    latent_bounds = np.array([BOUNDS[name] for name in latent_names], dtype=float)
    uniform = latent_bounds[:, 0] + latin_hypercube(rng, count // 2, len(latent_names)) * (
        latent_bounds[:, 1] - latent_bounds[:, 0]
    )
    center_latent = np.array(
        [
            center[PARAM_COLUMNS.index("L_mm")],
            center[PARAM_COLUMNS.index("tap_mm")],
            center[PARAM_COLUMNS.index("Egap_mm")],
            center[PARAM_COLUMNS.index("S1_mm")],
            center[PARAM_COLUMNS.index("S2_mm")],
            center[PARAM_COLUMNS.index("S3_mm")],
            center[PARAM_COLUMNS.index("W0_mm")],
            center[PARAM_COLUMNS.index("feed_len_mm")],
            center[PARAM_COLUMNS.index("feed_taper_len_mm")],
            center[PARAM_COLUMNS.index("feed_tip_w_mm")],
            center[PARAM_COLUMNS.index("feed_overlap_mm")],
        ],
        dtype=float,
    )
    sigma = (latent_bounds[:, 1] - latent_bounds[:, 0]) / 5.0
    local = rng.normal(center_latent, sigma, size=(count - len(uniform), len(latent_names)))
    local = np.clip(local, latent_bounds[:, 0], latent_bounds[:, 1])
    latent = np.vstack([uniform, local])
    pool = np.empty((len(latent), len(PARAM_COLUMNS)), dtype=float)
    pool[:, PARAM_COLUMNS.index("L_mm")] = latent[:, 0]
    pool[:, PARAM_COLUMNS.index("tap_mm")] = latent[:, 1]
    pool[:, PARAM_COLUMNS.index("Egap_mm")] = latent[:, 2]
    pool[:, PARAM_COLUMNS.index("S1_mm")] = latent[:, 3]
    pool[:, PARAM_COLUMNS.index("S6_mm")] = latent[:, 3]
    pool[:, PARAM_COLUMNS.index("S2_mm")] = latent[:, 4]
    pool[:, PARAM_COLUMNS.index("S5_mm")] = latent[:, 4]
    pool[:, PARAM_COLUMNS.index("S3_mm")] = latent[:, 5]
    pool[:, PARAM_COLUMNS.index("S4_mm")] = latent[:, 5]
    pool[:, PARAM_COLUMNS.index("W0_mm")] = latent[:, 6]
    pool[:, PARAM_COLUMNS.index("feed_len_mm")] = latent[:, 7]
    pool[:, PARAM_COLUMNS.index("feed_taper_len_mm")] = latent[:, 8]
    pool[:, PARAM_COLUMNS.index("feed_tip_w_mm")] = latent[:, 9]
    pool[:, PARAM_COLUMNS.index("feed_overlap_mm")] = latent[:, 10]
    pool[:, PARAM_COLUMNS.index("via_diameter_mm")] = BOUNDS["via_diameter_mm"][0]
    return pool


def train_ensemble(
    x_train: np.ndarray,
    y_train: np.ndarray,
    rng: np.random.Generator,
    size: int,
    ridge: float,
) -> list[list[tuple[np.ndarray, float, float]]]:
    models: list[list[tuple[np.ndarray, float, float]]] = []
    for _ in range(size):
        indices = rng.integers(0, len(x_train), size=len(x_train))
        xb = x_train[indices]
        yb = y_train[indices]
        models.append([fit_ridge(xb, yb[:, col], ridge) for col in range(y_train.shape[1])])
    return models


def predict_ensemble(pool: np.ndarray, models: list[list[tuple[np.ndarray, float, float]]]) -> np.ndarray:
    predictions = []
    for model_set in models:
        cols = [predict_ridge(pool, model) for model in model_set]
        predictions.append(np.column_stack(cols))
    return np.stack(predictions, axis=0)


def select_candidates(
    rows: list[dict[str, str]],
    count: int,
    pool_count: int,
    seed: int,
    exploration: float,
) -> tuple[list[dict[str, float]], dict[str, str]]:
    try:
        return opt.select_surrogate_candidates(
            rows=rows,
            count=count,
            pool_count=pool_count,
            seed=seed,
            exploration=exploration,
            param_columns=PARAM_COLUMNS,
            metric_columns=METRIC_COLUMNS,
            targets=TARGETS,
            bounds=BOUNDS,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


def params_from_candidate(seed: FilterParams, name: str, item: dict[str, float]) -> FilterParams:
    return replace(
        seed,
        name=name,
        resonator_l_mm=item["L_mm"],
        tap_from_bottom_mm=item["tap_mm"],
        end_gap_mm=item["Egap_mm"],
        gaps_mm=(item["S1_mm"], item["S2_mm"], item["S3_mm"], item["S4_mm"], item["S5_mm"], item["S6_mm"]),
        w0_mm=item["W0_mm"],
        resonator_w_mm=item["W0_mm"],
        feed_len_mm=item["feed_len_mm"],
        feed_taper_len_mm=item["feed_taper_len_mm"],
        feed_tip_w_mm=item["feed_tip_w_mm"],
        feed_overlap_mm=item["feed_overlap_mm"],
        via_diameter_mm=item["via_diameter_mm"],
    )


def row_from_params(params: FilterParams, item: dict[str, float], note: str) -> dict[str, str]:
    gaps = list(params.gaps_mm)
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
        "notes": note,
    }


def write_prediction_report(rows: list[dict[str, str]], selected: list[dict[str, float]], path: Path) -> None:
    fieldnames = [
        "candidate",
        "pred_objective_score",
        "pred_objective_std",
        "expected_improvement",
        "probability_improve",
        "pred_s21_5g_db",
        "pred_s21_6g_db",
        "pred_s21_8g_db",
        "pred_passband_min_s21_db",
        "pred_passband_ripple_db",
        "pred_worst_s11_6_8_db",
        "pred_worst_s22_6_8_db",
        "nearest_train_distance",
    ] + PARAM_COLUMNS
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        for plan_row, item in zip(rows, selected, strict=True):
            writer.writerow(
                {
                    "candidate": plan_row["name"],
                    **{key: f"{item[key]:.6g}" for key in fieldnames if key in item},
                }
            )


def round_short_name(round_name: str) -> str:
    lower = round_name.lower()
    if lower.startswith("round") and lower[5:].isdigit():
        return f"r{lower[5:]}"
    return lower.replace("-", "_")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Propose ADS candidates by surrogate trust-region search.")
    parser.add_argument("--project-id", default="bfp_6_8g_i7_fr4")
    parser.add_argument("--sweep-id", default=None)
    parser.add_argument("--dataset", type=Path, default=None)
    parser.add_argument("--seed-params", type=Path, default=None)
    parser.add_argument("--round-name", default=None)
    parser.add_argument("--count", type=int, default=None)
    parser.add_argument("--pool-count", type=int, default=None)
    parser.add_argument("--random-seed", type=int, default=None)
    parser.add_argument("--exploration", type=float, default=None)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--plan", type=Path, default=None)
    parser.add_argument("--prediction-report", type=Path, default=None)
    return parser.parse_args()


def apply_project_defaults(args: argparse.Namespace) -> None:
    root = repo_root()
    try:
        project = load_project(args.project_id, root=root)
    except FileNotFoundError:
        project = None
    sweep = project.get_sweep(args.sweep_id) if project else None
    optimizer = sweep.optimizer if sweep else {}
    fallback_project = root / "projects" / args.project_id

    args._project_config = project
    args._sweep_config = sweep
    args.dataset = args.dataset or Path(str(optimizer.get("dataset", fallback_project / "results" / "interdigital_7o_fr4_training_dataset.csv")))
    args.seed_params = args.seed_params or Path(
        str(
            optimizer.get(
                "seed_params",
                fallback_project / "layouts" / "interdigital_7o_fr4_210um_round3" / "i7_fr4_r3_base_params.json",
            )
        )
    )
    args.round_name = args.round_name or str(optimizer.get("round_name", "round7"))
    args.count = args.count if args.count is not None else int(optimizer.get("count", 8))
    args.pool_count = args.pool_count if args.pool_count is not None else int(optimizer.get("pool_count", 50000))
    args.random_seed = args.random_seed if args.random_seed is not None else int(optimizer.get("random_seed", 731))
    args.exploration = args.exploration if args.exploration is not None else float(optimizer.get("exploration", 0.0))
    args.out_dir = args.out_dir or (sweep.layouts_dir if sweep else None) or fallback_project / "layouts" / "interdigital_7o_fr4_210um_round7"
    args.plan = args.plan or (sweep.plan if sweep else None) or fallback_project / "plans" / "filter_opt_i7_fr4_round7.csv"
    args.prediction_report = args.prediction_report or Path(
        str(optimizer.get("prediction_report", fallback_project / "results" / "interdigital_7o_fr4_round7_predictions.csv"))
    )


def main() -> None:
    args = parse_args()
    apply_project_defaults(args)
    rows = read_csv(args.dataset)
    selected, best = select_candidates(rows, args.count, args.pool_count, args.random_seed, args.exploration)
    seed = load_seed(args.seed_params)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    plan_rows: list[dict[str, str]] = []
    print(f"Training best: {best['candidate']} objective={best['objective_score']}")
    print(f"Writing {len(selected)} proposed candidates into {args.out_dir}")
    round_prefix = round_short_name(args.round_name)
    for idx, item in enumerate(selected, start=1):
        name = f"i7_fr4_{round_prefix}_bo{idx:02d}"
        note = (
            "surrogate trust-region proposal; "
            f"EI {item['expected_improvement']:.2f}, P+ {item['probability_improve']:.2f}; "
            f"pred obj {item['pred_objective_score']:.2f}+/-{item['pred_objective_std']:.2f}; "
            f"pred S11/S22 {item['pred_worst_s11_6_8_db']:.2f}/{item['pred_worst_s22_6_8_db']:.2f} dB"
        )
        params = params_from_candidate(seed, name, item)
        outputs = write_outputs(params, args.out_dir)
        row = row_from_params(params, item, note)
        plan_rows.append(row)
        print(f"  {name}: {outputs['dxf_mm_coords']}")
    args.plan.parent.mkdir(parents=True, exist_ok=True)
    with args.plan.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(plan_rows)
    write_prediction_report(plan_rows, selected, args.prediction_report)
    print(f"Wrote plan: {args.plan}")
    print(f"Wrote prediction report: {args.prediction_report}")


if __name__ == "__main__":
    main()





