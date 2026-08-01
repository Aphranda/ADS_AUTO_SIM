"""Dependency-light surrogate optimization helpers."""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np

from .variants import (
    DeterministicVariantConfig,
    build_plan_rows,
    load_variant_config,
    validate_config,
    write_plan,
)


INTERDIGITAL_FR4_PARAM_COLUMNS = [
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

FILTER_METRIC_COLUMNS = [
    "s21_5g_db",
    "s21_6g_db",
    "s21_8g_db",
    "passband_min_s21_db",
    "passband_ripple_db",
    "worst_s11_6_8_db",
    "worst_s22_6_8_db",
]

DEFAULT_INTERDIGITAL_FR4_TARGETS = {
    "s21_5g_db": -25.0,
    "s21_6g_db": -5.0,
    "s21_8g_db": -5.0,
    "passband_min_s21_db": -5.0,
    "passband_ripple_db": 4.0,
    "worst_s11_6_8_db": -6.0,
    "worst_s22_6_8_db": -6.0,
}

DEFAULT_INTERDIGITAL_FR4_BOUNDS = {
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


def parse_float(value: str | float | int | None) -> float:
    if value is None:
        return float("nan")
    text = str(value).strip()
    return float(text) if text else float("nan")


def row_to_vector(row: dict[str, str], param_columns: Sequence[str] = INTERDIGITAL_FR4_PARAM_COLUMNS) -> np.ndarray:
    return np.array([parse_float(row[key]) for key in param_columns], dtype=float)


def geometry_key(values: np.ndarray) -> str:
    return "|".join(f"{value:.5f}" for value in values)


def aggregate_unique(
    rows: list[dict[str, str]],
    metric_columns: Sequence[str] = FILTER_METRIC_COLUMNS,
) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["geometry_key"], []).append(row)
    output: list[dict[str, str]] = []
    for members in grouped.values():
        best = max(members, key=lambda item: parse_float(item["objective_score"]))
        averaged = dict(best)
        for key in [*metric_columns, "objective_score"]:
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


def objective_from_metrics(
    metrics: np.ndarray,
    targets: dict[str, float] = DEFAULT_INTERDIGITAL_FR4_TARGETS,
) -> np.ndarray:
    s21_5 = metrics[:, 0]
    s21_6 = metrics[:, 1]
    s21_8 = metrics[:, 2]
    pass_min = metrics[:, 3]
    ripple = metrics[:, 4]
    s11 = metrics[:, 5]
    s22 = metrics[:, 6]
    margins = np.column_stack(
        [
            targets["s21_5g_db"] - s21_5,
            s21_6 - targets["s21_6g_db"],
            s21_8 - targets["s21_8g_db"],
            pass_min - targets["passband_min_s21_db"],
            targets["passband_ripple_db"] - ripple,
        ]
    )
    hard_violation = np.sum(np.maximum(0.0, -margins) ** 2, axis=1)
    s11_gap = np.maximum(0.0, s11 - targets["worst_s11_6_8_db"])
    s22_gap = np.maximum(0.0, s22 - targets["worst_s22_6_8_db"])
    worst_return = np.maximum(s11, s22)
    stop_margin = targets["s21_5g_db"] - s21_5
    edge_margin = np.minimum(s21_6 - targets["s21_6g_db"], s21_8 - targets["s21_8g_db"])
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


def symmetric_interdigital_pool(
    rng: np.random.Generator,
    count: int,
    center: np.ndarray,
    param_columns: Sequence[str] = INTERDIGITAL_FR4_PARAM_COLUMNS,
    bounds: dict[str, tuple[float, float]] = DEFAULT_INTERDIGITAL_FR4_BOUNDS,
) -> np.ndarray:
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
    latent_bounds = np.array([bounds[name] for name in latent_names], dtype=float)
    uniform = latent_bounds[:, 0] + latin_hypercube(rng, count // 2, len(latent_names)) * (
        latent_bounds[:, 1] - latent_bounds[:, 0]
    )
    center_latent = np.array([center[param_columns.index(name)] for name in latent_names], dtype=float)
    sigma = (latent_bounds[:, 1] - latent_bounds[:, 0]) / 5.0
    local = rng.normal(center_latent, sigma, size=(count - len(uniform), len(latent_names)))
    local = np.clip(local, latent_bounds[:, 0], latent_bounds[:, 1])
    latent = np.vstack([uniform, local])
    pool = np.empty((len(latent), len(param_columns)), dtype=float)
    pool[:, param_columns.index("L_mm")] = latent[:, 0]
    pool[:, param_columns.index("tap_mm")] = latent[:, 1]
    pool[:, param_columns.index("Egap_mm")] = latent[:, 2]
    pool[:, param_columns.index("S1_mm")] = latent[:, 3]
    pool[:, param_columns.index("S6_mm")] = latent[:, 3]
    pool[:, param_columns.index("S2_mm")] = latent[:, 4]
    pool[:, param_columns.index("S5_mm")] = latent[:, 4]
    pool[:, param_columns.index("S3_mm")] = latent[:, 5]
    pool[:, param_columns.index("S4_mm")] = latent[:, 5]
    pool[:, param_columns.index("W0_mm")] = latent[:, 6]
    pool[:, param_columns.index("feed_len_mm")] = latent[:, 7]
    pool[:, param_columns.index("feed_taper_len_mm")] = latent[:, 8]
    pool[:, param_columns.index("feed_tip_w_mm")] = latent[:, 9]
    pool[:, param_columns.index("feed_overlap_mm")] = latent[:, 10]
    pool[:, param_columns.index("via_diameter_mm")] = bounds["via_diameter_mm"][0]
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


def select_surrogate_candidates(
    rows: list[dict[str, str]],
    count: int,
    pool_count: int,
    seed: int,
    exploration: float,
    param_columns: Sequence[str] = INTERDIGITAL_FR4_PARAM_COLUMNS,
    metric_columns: Sequence[str] = FILTER_METRIC_COLUMNS,
    targets: dict[str, float] = DEFAULT_INTERDIGITAL_FR4_TARGETS,
    bounds: dict[str, tuple[float, float]] = DEFAULT_INTERDIGITAL_FR4_BOUNDS,
) -> tuple[list[dict[str, float]], dict[str, str]]:
    unique_rows = aggregate_unique(rows, metric_columns)
    best = max(unique_rows, key=lambda row: parse_float(row["objective_score"]))
    x_raw = np.vstack([row_to_vector(row, param_columns) for row in unique_rows])
    y_raw = np.array([[parse_float(row[key]) for key in metric_columns] for row in unique_rows], dtype=float)
    x_train, x_mean, x_std = standardize(x_raw)
    rng = np.random.default_rng(seed)
    models = train_ensemble(x_train, y_raw, rng, size=100, ridge=2.0)
    center = row_to_vector(best, param_columns)
    pool_raw = symmetric_interdigital_pool(rng, pool_count, center, param_columns, bounds)
    pool_std = (pool_raw - x_mean) / x_std
    predictions = predict_ensemble(pool_std, models)
    scores = np.stack([objective_from_metrics(predictions[idx], targets) for idx in range(predictions.shape[0])], axis=0)
    mean_metrics = np.mean(predictions, axis=0)
    mean_score = np.mean(scores, axis=0)
    std_score = np.std(scores, axis=0)
    best_score = parse_float(best["objective_score"])
    expected_improvement = np.mean(np.maximum(0.0, scores - best_score), axis=0)
    probability_improve = np.mean(scores > best_score, axis=0)
    known = {geometry_key(row_to_vector(row, param_columns)) for row in unique_rows}
    existing_std = (x_raw - x_mean) / x_std
    distances = np.min(np.linalg.norm(pool_std[:, None, :] - existing_std[None, :, :], axis=2), axis=1)
    acquisition = expected_improvement + exploration * 0.05 * std_score - 0.8 * np.maximum(0.0, distances - 2.0) ** 2

    s21_5 = mean_metrics[:, 0]
    s21_6 = mean_metrics[:, 1]
    s21_8 = mean_metrics[:, 2]
    pass_min = mean_metrics[:, 3]
    ripple = mean_metrics[:, 4]
    feasible_gate = (
        (s21_5 <= targets["s21_5g_db"] + 0.15)
        & (s21_6 >= targets["s21_6g_db"] - 0.10)
        & (s21_8 >= targets["s21_8g_db"] - 0.10)
        & (pass_min >= targets["passband_min_s21_db"] - 0.10)
        & (ripple <= targets["passband_ripple_db"] + 0.10)
        & (distances >= 0.03)
        & (distances <= 4.50)
    )
    order = np.argsort(acquisition)[::-1]
    selected: list[dict[str, float]] = []
    selected_vectors: list[np.ndarray] = []
    bound_array = np.array([bounds[name] for name in param_columns], dtype=float)
    span = bound_array[:, 1] - bound_array[:, 0]
    span[span == 0.0] = 1.0
    for idx in order:
        vector = pool_raw[idx]
        if not feasible_gate[idx] or geometry_key(vector) in known:
            continue
        normalized = (vector - bound_array[:, 0]) / span
        if any(np.linalg.norm(normalized - previous) < 0.22 for previous in selected_vectors):
            continue
        item = {name: float(vector[col]) for col, name in enumerate(param_columns)}
        for col, name in enumerate(metric_columns):
            item[f"pred_{name}"] = float(mean_metrics[idx, col])
        item["pred_objective_score"] = float(mean_score[idx])
        item["pred_objective_std"] = float(std_score[idx])
        item["expected_improvement"] = float(expected_improvement[idx])
        item["probability_improve"] = float(probability_improve[idx])
        item["nearest_train_distance"] = float(distances[idx])
        selected.append(item)
        selected_vectors.append(normalized)
        if len(selected) >= count:
            break
    if len(selected) < count:
        raise ValueError(f"Only selected {len(selected)} candidates; relax gates or increase pool_count.")
    return selected, best
