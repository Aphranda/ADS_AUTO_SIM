"""Fit measured BPF marker curves and compare them with simulated S21."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import json
import math
from pathlib import Path
from statistics import mean, stdev
from typing import Any

import numpy as np

from .filter_measurement_compare import read_measured_markers
from .touchstone import read_sparameter_network

try:  # pragma: no cover - exercised through CLI
    from scipy.interpolate import PchipInterpolator
except Exception:  # pragma: no cover - graceful fallback
    PchipInterpolator = None


@dataclass(frozen=True)
class FitOptions:
    freq_min_ghz: float = 5.0
    freq_max_ghz: float = 9.0
    freq_step_ghz: float = 0.01


def _grid(options: FitOptions) -> list[float]:
    count = int(round((options.freq_max_ghz - options.freq_min_ghz) / options.freq_step_ghz))
    return [options.freq_min_ghz + index * options.freq_step_ghz for index in range(count + 1)]


def _fit_values(freqs: list[float], values: list[float], grid: list[float]) -> list[float]:
    if len(freqs) < 2:
        raise ValueError("curve fitting requires at least two marker points")
    if PchipInterpolator is not None and len(freqs) >= 3:
        interpolator = PchipInterpolator(freqs, values, extrapolate=False)
        result = interpolator(grid)
        return [float(value) if np.isfinite(value) else math.nan for value in result]
    result = np.interp(grid, freqs, values)
    return [float(value) for value in result]


def fit_measured_batch(measured_csv: Path, *, options: FitOptions = FitOptions()) -> dict[str, Any]:
    measured = read_measured_markers(measured_csv)
    boards: dict[str, list[tuple[float, float]]] = {}
    for marker in measured:
        boards.setdefault(marker.board_id, []).append((marker.freq_ghz, marker.s21_db))
    if not boards:
        raise ValueError(f"no measured markers found in {measured_csv}")

    grid = _grid(options)
    rows: list[dict[str, Any]] = []
    board_ids = sorted(boards)
    board_curves: dict[str, list[float]] = {}
    marker_table: list[dict[str, Any]] = []
    for board_id in board_ids:
        points = sorted(boards[board_id], key=lambda item: item[0])
        freqs = [freq for freq, _ in points]
        values = [value for _, value in points]
        curve = _fit_values(freqs, values, grid)
        board_curves[board_id] = curve
        marker_table.extend(
            {
                "board_id": board_id,
                "freq_ghz": freq,
                "s21_db": value,
            }
            for freq, value in points
        )

    for index, freq in enumerate(grid):
        point_values = [board_curves[board_id][index] for board_id in board_ids]
        rows.append(
            {
                "freq_ghz": freq,
                **{f"{board_id}_s21_db": board_curves[board_id][index] for board_id in board_ids},
                "mean_s21_db": mean(point_values),
                "std_s21_db": stdev(point_values) if len(point_values) > 1 else 0.0,
                "min_s21_db": min(point_values),
                "max_s21_db": max(point_values),
            }
        )

    return {
        "measured_csv": str(measured_csv),
        "board_ids": board_ids,
        "options": {
            "freq_min_ghz": options.freq_min_ghz,
            "freq_max_ghz": options.freq_max_ghz,
            "freq_step_ghz": options.freq_step_ghz,
            "interpolator": "PCHIP" if PchipInterpolator is not None and len(board_ids) else "linear",
        },
        "marker_table": marker_table,
        "fit_rows": rows,
    }


def compare_fit_to_simulation(
    fit_payload: dict[str, Any],
    simulation_s2p: Path,
    *,
    marker_freqs: list[float] | None = None,
) -> dict[str, Any]:
    network = read_sparameter_network(simulation_s2p).require_nports(2, system="filter")
    rows = fit_payload["fit_rows"]
    if not rows:
        raise ValueError("fit payload has no rows")
    sim_rows: list[dict[str, Any]] = []
    for row in rows:
        freq = float(row["freq_ghz"])
        sim_db = network.interp_db(freq, "s21")
        sim_rows.append(
            {
                "freq_ghz": freq,
                "measured_mean_s21_db": float(row["mean_s21_db"]),
                "sim_s21_db": sim_db,
                "error_db": sim_db - float(row["mean_s21_db"]),
            }
        )

    abs_errors = [abs(row["error_db"]) for row in sim_rows if not math.isnan(row["error_db"])]
    rms = math.sqrt(sum(row["error_db"] ** 2 for row in sim_rows if not math.isnan(row["error_db"])) / len(abs_errors))
    marker_freqs = marker_freqs or [5.0, 6.0, 6.3, 8.0, 9.0]
    marker_rows: list[dict[str, Any]] = []
    by_freq = {round(float(row["freq_ghz"]), 6): row for row in sim_rows}
    for freq in marker_freqs:
        key = round(freq, 6)
        row = by_freq.get(key)
        if row is None:
            continue
        marker_rows.append(row)

    return {
        "simulation_s2p": str(simulation_s2p),
        "dense_compare_rows": sim_rows,
        "marker_compare_rows": marker_rows,
        "summary": {
            "rms_error_db": rms,
            "mean_abs_error_db": mean(abs_errors) if abs_errors else math.nan,
            "max_abs_error_db": max(abs_errors) if abs_errors else math.nan,
            "marker_error_6g_db": next((row["error_db"] for row in marker_rows if round(row["freq_ghz"], 3) == 6.0), math.nan),
            "marker_error_6p3g_db": next((row["error_db"] for row in marker_rows if round(row["freq_ghz"], 3) == 6.3), math.nan),
            "marker_error_8g_db": next((row["error_db"] for row in marker_rows if round(row["freq_ghz"], 3) == 8.0), math.nan),
        },
    }


def write_fit_csv(fit_payload: dict[str, Any], out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    board_ids = fit_payload["board_ids"]
    with out.open("w", newline="", encoding="utf-8") as fp:
        fieldnames = ["freq_ghz", *[f"{board_id}_s21_db" for board_id in board_ids], "mean_s21_db", "std_s21_db", "min_s21_db", "max_s21_db"]
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        for row in fit_payload["fit_rows"]:
            writer.writerow({key: (f"{float(row[key]):.6f}" if key != "freq_ghz" else f"{float(row[key]):.6f}") for key in fieldnames})
    return out


def write_compare_csv(compare_payload: dict[str, Any], out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fp:
        fieldnames = ["freq_ghz", "measured_mean_s21_db", "sim_s21_db", "error_db"]
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        for row in compare_payload["dense_compare_rows"]:
            writer.writerow({key: f"{float(row[key]):.6f}" for key in fieldnames})
    return out


def dump_json(payload: dict[str, Any], out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


__all__ = [
    "FitOptions",
    "compare_fit_to_simulation",
    "dump_json",
    "fit_measured_batch",
    "write_compare_csv",
    "write_fit_csv",
]
