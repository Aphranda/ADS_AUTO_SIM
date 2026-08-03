#!/usr/bin/env python3
"""Rank interdigital candidate plans with a refined-parameter NN surrogate."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

import numpy as np

_SIM_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _SIM_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.nn.interdigital_features import (
    AUX_FEATURES,
    LEGACY_CENTER,
    PARAM_COLUMNS,
    curve_aux_features,
    feature_bundle,
    interdigital_score,
    params_from_plan_row,
)
from simads.nn.interdigital_surrogate import InterdigitalSParamSurrogate, require_torch


def repo_root() -> Path:
    return _SIM_ROOT


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def fmt(value: float) -> str:
    return f"{value:.6g}"


def normalize(values: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    std = np.where(std < 1e-8, 1.0, std)
    return ((values - mean) / std).astype(np.float32)


def candidate_arrays(rows: list[dict[str, str]], norm: dict[str, dict[str, np.ndarray]]) -> tuple[dict[str, np.ndarray], np.ndarray]:
    arrays: dict[str, list[np.ndarray]] = {
        "x_resonator": [],
        "x_gap": [],
        "x_feed": [],
        "x_derived": [],
    }
    raw_vectors: list[np.ndarray] = []
    for row in rows:
        params = params_from_plan_row(row)
        bundle = feature_bundle(params)
        arrays["x_resonator"].append(normalize(bundle.x_resonator, norm["x_resonator"]["mean"], norm["x_resonator"]["std"]))
        arrays["x_gap"].append(normalize(bundle.x_gap, norm["x_gap"]["mean"], norm["x_gap"]["std"]))
        arrays["x_feed"].append(normalize(bundle.x_feed, norm["x_feed"]["mean"], norm["x_feed"]["std"]))
        arrays["x_derived"].append(normalize(bundle.x_derived, norm["x_derived"]["mean"], norm["x_derived"]["std"]))
        raw_vectors.append(bundle.x_raw)
    return {key: np.stack(value, axis=0).astype(np.float32) for key, value in arrays.items()}, np.stack(raw_vectors, axis=0)


def distance_to_center(raw: np.ndarray) -> np.ndarray:
    center = np.asarray([LEGACY_CENTER[key] for key in PARAM_COLUMNS], dtype=np.float32)
    scale = np.maximum(np.abs(center), 0.05)
    return np.sqrt(np.mean(((raw - center) / scale) ** 2, axis=1))


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Rank interdigital plan rows using a trained refined-parameter surrogate.")
    parser.add_argument("--checkpoint", type=Path, default=root / "projects" / "bfp_6_8g_i7_fr4" / "results" / "interdigital_refined_surrogate.pt")
    parser.add_argument("--plan", type=Path, default=root / "projects" / "bfp_6_8g_i7_fr4" / "plans" / "filter_opt_i7_fr4_round8_refined_nn_pool.csv")
    parser.add_argument("--out", type=Path, default=root / "projects" / "bfp_6_8g_i7_fr4" / "results" / "interdigital_round8_refined_nn_ranking.csv")
    parser.add_argument("--top-plan", type=Path, default=root / "projects" / "bfp_6_8g_i7_fr4" / "plans" / "filter_opt_i7_fr4_round8_refined_nn_top8.csv")
    parser.add_argument("--top-count", type=int, default=8)
    parser.add_argument("--guard-s21-5-max-db", type=float, default=-25.0)
    parser.add_argument("--guard-s21-6-min-db", type=float, default=-5.0)
    parser.add_argument("--guard-s21-8-min-db", type=float, default=-5.0)
    parser.add_argument("--guard-passband-min-db", type=float, default=-5.0)
    parser.add_argument("--guard-ripple-max-db", type=float, default=4.0)
    parser.add_argument(
        "--cal-s21-5-offset-db",
        type=float,
        default=0.0,
        help="Add this offset to predicted S21@5G before scoring/guarding, e.g. -1.6 for round10 measured bias.",
    )
    parser.add_argument(
        "--cal-s21-6-offset-db",
        type=float,
        default=0.0,
        help="Add this offset to predicted S21@6G before scoring/guarding.",
    )
    parser.add_argument(
        "--cal-s21-8-offset-db",
        type=float,
        default=0.0,
        help="Add this offset to predicted S21@8G before scoring/guarding.",
    )
    parser.add_argument(
        "--cal-worst-s11-offset-db",
        type=float,
        default=0.0,
        help="Add this offset to predicted worst S11 in 6-8G before scoring.",
    )
    parser.add_argument(
        "--cal-worst-s22-offset-db",
        type=float,
        default=0.0,
        help="Add this offset to predicted worst S22 in 6-8G before scoring.",
    )
    return parser.parse_args()


def calibrated_metrics(metrics: dict[str, float], args: argparse.Namespace) -> dict[str, float]:
    result = dict(metrics)
    result["s21_5g_db"] += args.cal_s21_5_offset_db
    result["s21_6g_db"] += args.cal_s21_6_offset_db
    result["s21_8g_db"] += args.cal_s21_8_offset_db
    result["worst_s11_6_8_db"] += args.cal_worst_s11_offset_db
    result["worst_s22_6_8_db"] += args.cal_worst_s22_offset_db
    return result


def main() -> None:
    torch = require_torch()
    args = parse_args()
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    model = InterdigitalSParamSurrogate(**checkpoint["model_config"])
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    freq_ghz = np.asarray(checkpoint["freq_ghz"], dtype=np.float32)
    y_mean = np.asarray(checkpoint["y_mean"], dtype=np.float32)
    y_std = np.asarray(checkpoint["y_std"], dtype=np.float32)
    norm = checkpoint["normalization"]
    rows = read_csv(args.plan)
    arrays, raw = candidate_arrays(rows, norm)
    inputs = {key: torch.tensor(value, dtype=torch.float32) for key, value in arrays.items()}
    with torch.no_grad():
        pred_norm = model(
            x_resonator=inputs["x_resonator"],
            x_gap=inputs["x_gap"],
            x_feed=inputs["x_feed"],
            x_derived=inputs["x_derived"],
        ).detach().cpu().numpy()
    pred_db = pred_norm * y_std + y_mean
    distances = distance_to_center(raw)
    output_rows: list[dict[str, str]] = []
    has_calibration = any(
        abs(value) > 1e-12
        for value in (
            args.cal_s21_5_offset_db,
            args.cal_s21_6_offset_db,
            args.cal_s21_8_offset_db,
            args.cal_worst_s11_offset_db,
            args.cal_worst_s22_offset_db,
        )
    )
    for idx, row in enumerate(rows):
        aux = curve_aux_features(freq_ghz, pred_db[idx])
        metrics = {feature: float(aux[col]) for col, feature in enumerate(AUX_FEATURES)}
        cal_metrics = calibrated_metrics(metrics, args)
        score = interdigital_score(cal_metrics) - 12.0 * float(distances[idx])
        guard_pass = (
            cal_metrics["s21_5g_db"] <= args.guard_s21_5_max_db
            and cal_metrics["s21_6g_db"] >= args.guard_s21_6_min_db
            and cal_metrics["s21_8g_db"] >= args.guard_s21_8_min_db
            and cal_metrics["passband_min_s21_db"] >= args.guard_passband_min_db
            and cal_metrics["passband_ripple_db"] <= args.guard_ripple_max_db
        )
        out = {
            "rank": "",
            "name": row["name"],
            "pred_score": fmt(score),
            "pred_guard_pass": "true" if guard_pass else "false",
            "distance_to_legacy": fmt(float(distances[idx])),
            **{f"pred_{key}": fmt(value) for key, value in metrics.items()},
            **({f"cal_{key}": fmt(value) for key, value in cal_metrics.items()} if has_calibration else {}),
            **{key: row.get(key, "") for key in PARAM_COLUMNS},
            "metal_layer": row.get("metal_layer", "cond"),
            "via_layer": row.get("via_layer", "pcvia1"),
            "notes": row.get("notes", ""),
        }
        output_rows.append(out)
    output_rows.sort(key=lambda item: (item["pred_guard_pass"] == "true", float(item["pred_score"])), reverse=True)
    for rank, row in enumerate(output_rows, start=1):
        row["rank"] = str(rank)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)
    top = output_rows[: args.top_count]
    args.top_plan.parent.mkdir(parents=True, exist_ok=True)
    with args.top_plan.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=["name", *PARAM_COLUMNS, "metal_layer", "via_layer", "notes"])
        writer.writeheader()
        for row in top:
            writer.writerow(
                {
                    "name": row["name"],
                    **{key: row[key] for key in PARAM_COLUMNS},
                    "metal_layer": row["metal_layer"],
                    "via_layer": row["via_layer"],
                    "notes": (
                        f"refined-NN rank {row['rank']}; score {row['pred_score']}; "
                        f"S21@5/6/8 {row['pred_s21_5g_db']}/{row['pred_s21_6g_db']}/{row['pred_s21_8g_db']} dB; "
                        + (
                            f"cal S21@5/6/8 {row['cal_s21_5g_db']}/{row['cal_s21_6g_db']}/{row['cal_s21_8g_db']} dB; "
                            if has_calibration
                            else ""
                        )
                        +
                        f"S11/S22 {row['pred_worst_s11_6_8_db']}/{row['pred_worst_s22_6_8_db']} dB"
                    ),
                }
            )
    print(f"Wrote ranking: {args.out}")
    print(f"Wrote top plan: {args.top_plan}")
    print("Top candidates:")
    for row in top:
        print(
            f"  #{row['rank']} {row['name']}: score={row['pred_score']} guard={row['pred_guard_pass']} "
            f"S21@5/6/8={row['pred_s21_5g_db']}/{row['pred_s21_6g_db']}/{row['pred_s21_8g_db']} "
            + (
                f"cal={row['cal_s21_5g_db']}/{row['cal_s21_6g_db']}/{row['cal_s21_8g_db']} "
                if has_calibration
                else ""
            )
            +
            f"S11/S22={row['pred_worst_s11_6_8_db']}/{row['pred_worst_s22_6_8_db']}"
        )


if __name__ == "__main__":
    main()
