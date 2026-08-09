"""Compare measured BPF marker data against simulated filter metrics."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import json
import math
from pathlib import Path
from statistics import mean, stdev
from typing import Any


@dataclass(frozen=True)
class MeasuredMarker:
    board_id: str
    freq_ghz: float
    s21_db: float
    source: str


def read_measured_markers(path: Path) -> list[MeasuredMarker]:
    markers: list[MeasuredMarker] = []
    with path.open(newline="", encoding="utf-8") as fp:
        for row in csv.DictReader(fp):
            markers.append(
                MeasuredMarker(
                    board_id=str(row["board_id"]),
                    freq_ghz=float(row["freq_ghz"]),
                    s21_db=float(row["s21_db"]),
                    source=str(row.get("source", "")),
                )
            )
    return markers


def _sim_s21_by_freq(metrics: dict[str, Any]) -> dict[float, float]:
    values: dict[float, float] = {}
    for marker in metrics.get("markers", {}).values():
        if not isinstance(marker, dict):
            continue
        values[round(float(marker["freq_ghz"]), 6)] = float(marker["s21_db"])
    return values


def _frequency_rows(markers: list[MeasuredMarker]) -> dict[float, list[MeasuredMarker]]:
    grouped: dict[float, list[MeasuredMarker]] = {}
    for marker in markers:
        grouped.setdefault(round(marker.freq_ghz, 6), []).append(marker)
    return grouped


def compare_measurement_to_simulation(measured_csv: Path, simulation_metrics_json: Path) -> dict[str, Any]:
    measured = read_measured_markers(measured_csv)
    metrics = json.loads(simulation_metrics_json.read_text(encoding="utf-8"))
    sim = _sim_s21_by_freq(metrics)
    rows: list[dict[str, Any]] = []
    for freq, freq_markers in sorted(_frequency_rows(measured).items()):
        measured_values = [marker.s21_db for marker in freq_markers]
        measured_mean = mean(measured_values)
        measured_std = stdev(measured_values) if len(measured_values) > 1 else 0.0
        sim_s21 = sim.get(freq, math.nan)
        rows.append(
            {
                "freq_ghz": freq,
                "board_count": len(freq_markers),
                "measured_s21_mean_db": measured_mean,
                "measured_s21_std_db": measured_std,
                "measured_s21_min_db": min(measured_values),
                "measured_s21_max_db": max(measured_values),
                "sim_s21_db": sim_s21,
                "sim_minus_measured_mean_db": sim_s21 - measured_mean if not math.isnan(sim_s21) else math.nan,
            }
        )
    return {
        "measured_csv": str(measured_csv),
        "simulation_metrics_json": str(simulation_metrics_json),
        "comparison": rows,
        "summary": summarize_comparison(rows),
    }


def summarize_comparison(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_freq = {round(float(row["freq_ghz"]), 6): row for row in rows}
    delta_6g = float(by_freq.get(6.0, {}).get("sim_minus_measured_mean_db", math.nan))
    delta_6p3g = float(by_freq.get(6.3, {}).get("sim_minus_measured_mean_db", math.nan))
    delta_8g = float(by_freq.get(8.0, {}).get("sim_minus_measured_mean_db", math.nan))
    delta_5g = float(by_freq.get(5.0, {}).get("sim_minus_measured_mean_db", math.nan))
    delta_9g = float(by_freq.get(9.0, {}).get("sim_minus_measured_mean_db", math.nan))
    return {
        "delta_6g_db": delta_6g,
        "delta_6p3g_db": delta_6p3g,
        "delta_8g_db": delta_8g,
        "delta_5g_db": delta_5g,
        "delta_9g_db": delta_9g,
        "batch_spread_max_std_db": max((float(row["measured_s21_std_db"]) for row in rows), default=math.nan),
        "primary_gap": "measured_low_edge_is_higher_than_simulation" if delta_6g > 6.0 else "no_large_low_edge_gap",
        "passband_alignment": "good_above_6p3g" if abs(delta_6p3g) <= 3.0 and abs(delta_8g) <= 3.0 else "needs_full_passband_refit",
        "stopband_alignment": "simulation_underestimates_stopband_rejection"
        if delta_5g > 6.0 and delta_9g > 6.0
        else "mixed_stopband_alignment",
    }


def write_comparison_csv(payload: dict[str, Any], out: Path) -> Path:
    rows = payload["comparison"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fp:
        fieldnames = [
            "freq_ghz",
            "board_count",
            "measured_s21_mean_db",
            "measured_s21_std_db",
            "measured_s21_min_db",
            "measured_s21_max_db",
            "sim_s21_db",
            "sim_minus_measured_mean_db",
        ]
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: f"{float(row[key]):.3f}" if key != "board_count" else row[key]
                    for key in fieldnames
                }
            )
    return out


__all__ = [
    "MeasuredMarker",
    "compare_measurement_to_simulation",
    "read_measured_markers",
    "summarize_comparison",
    "write_comparison_csv",
]
