#!/usr/bin/env python3
"""Score TX_BAND1 filter HFSS trace CSV feedback."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any


PASSBAND = (17.700, 19.325)
HIGH_PASSBAND = (18.800, 19.325)
LO_STOPBAND = (14.400, 15.025)
IMAGE_STOPBAND = (10.100, 13.600)
PASS_CENTER = (PASSBAND[0] + PASSBAND[1]) / 2.0
PASSBAND_INSERTION_LOSS_MAX_DB = 3.0
RETURN_LOSS_MIN_DB = 10.0
STOPBAND_REJECTION_MIN_DB = 40.0
HIGH_RETURN_LOSS_WEIGHT = 2.0
HIGH_EDGE_RETURN_LOSS_WEIGHT = 1.5


def read_trace(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        rows = [{key: float(value) for key, value in row.items()} for row in csv.DictReader(fp)]
    if not rows:
        raise ValueError(f"empty trace CSV: {path}")
    return rows


def _window(rows: list[dict[str, float]], band: tuple[float, float]) -> list[dict[str, float]]:
    return [row for row in rows if band[0] <= row["freq_ghz"] <= band[1]]


def _safe(values: list[float], fn: Any) -> float:
    finite = [value for value in values if math.isfinite(value)]
    return fn(finite) if finite else float("nan")


def _metric_row(rows: list[dict[str, float]], band: tuple[float, float]) -> dict[str, float]:
    selected = _window(rows, band)
    s21 = [row["s21_db"] for row in selected]
    s11 = [row["s11_db"] for row in selected]
    s22 = [row["s22_db"] for row in selected]
    s21_min = _safe(s21, min)
    s21_max = _safe(s21, max)
    return {
        "points": float(len(selected)),
        "s21_min_db": s21_min,
        "s21_max_db": s21_max,
        "s21_avg_db": _safe(s21, lambda values: sum(values) / len(values)),
        "s21_ripple_db": s21_max - s21_min if math.isfinite(s21_min) and math.isfinite(s21_max) else float("nan"),
        "worst_s11_db": _safe(s11, max),
        "worst_s22_db": _safe(s22, max),
    }


def _interp(rows: list[dict[str, float]], freq_ghz: float, column: str) -> float:
    ordered = sorted(rows, key=lambda row: row["freq_ghz"])
    if freq_ghz <= ordered[0]["freq_ghz"]:
        return ordered[0][column]
    if freq_ghz >= ordered[-1]["freq_ghz"]:
        return ordered[-1][column]
    for left, right in zip(ordered, ordered[1:], strict=False):
        lf = left["freq_ghz"]
        rf = right["freq_ghz"]
        if lf <= freq_ghz <= rf and rf > lf:
            alpha = (freq_ghz - lf) / (rf - lf)
            return left[column] + alpha * (right[column] - left[column])
    return float("nan")


def score_trace(path: Path, candidate: str | None = None) -> dict[str, str]:
    rows = read_trace(path)
    pass_metrics = _metric_row(rows, PASSBAND)
    high_pass_metrics = _metric_row(rows, HIGH_PASSBAND)
    lo_metrics = _metric_row(rows, LO_STOPBAND)
    image_metrics = _metric_row(rows, IMAGE_STOPBAND)
    peak = max(rows, key=lambda row: row["s21_db"])
    pass_center_s21 = _interp(rows, PASS_CENTER, "s21_db")
    pass_low_s21 = _interp(rows, PASSBAND[0], "s21_db")
    pass_high_s21 = _interp(rows, PASSBAND[1], "s21_db")
    pass_high_s11 = _interp(rows, PASSBAND[1], "s11_db")
    pass_high_s22 = _interp(rows, PASSBAND[1], "s22_db")

    score = 100.0
    score -= 7.0 * max(0.0, -PASSBAND_INSERTION_LOSS_MAX_DB - pass_metrics["s21_min_db"]) ** 2
    score -= 2.0 * max(0.0, -PASSBAND_INSERTION_LOSS_MAX_DB - peak["s21_db"]) ** 2
    score -= 2.0 * max(0.0, pass_metrics["s21_ripple_db"] - 0.5) ** 2
    score -= 0.9 * max(0.0, lo_metrics["s21_max_db"] + STOPBAND_REJECTION_MIN_DB) ** 2
    if image_metrics["points"] > 0:
        score -= 0.9 * max(0.0, image_metrics["s21_max_db"] + STOPBAND_REJECTION_MIN_DB) ** 2
    score -= 1.2 * max(0.0, pass_metrics["worst_s11_db"] + RETURN_LOSS_MIN_DB) ** 2
    score -= 1.2 * max(0.0, pass_metrics["worst_s22_db"] + RETURN_LOSS_MIN_DB) ** 2
    score -= HIGH_RETURN_LOSS_WEIGHT * max(0.0, high_pass_metrics["worst_s11_db"] + RETURN_LOSS_MIN_DB) ** 2
    score -= HIGH_RETURN_LOSS_WEIGHT * max(0.0, high_pass_metrics["worst_s22_db"] + RETURN_LOSS_MIN_DB) ** 2
    score -= HIGH_EDGE_RETURN_LOSS_WEIGHT * max(0.0, pass_high_s11 + RETURN_LOSS_MIN_DB) ** 2
    score -= HIGH_EDGE_RETURN_LOSS_WEIGHT * max(0.0, pass_high_s22 + RETURN_LOSS_MIN_DB) ** 2
    score -= 18.0 * abs(peak["freq_ghz"] - PASS_CENTER)

    status = "PASS_CANDIDATE"
    notes: list[str] = []
    if pass_metrics["s21_min_db"] < -PASSBAND_INSERTION_LOSS_MAX_DB:
        status = "TUNE"
        notes.append("passband insertion loss/ripple is not acceptable")
    if pass_metrics["worst_s11_db"] > -RETURN_LOSS_MIN_DB or pass_metrics["worst_s22_db"] > -RETURN_LOSS_MIN_DB:
        status = "TUNE"
        notes.append("return loss is not acceptable")
    if high_pass_metrics["worst_s11_db"] > -RETURN_LOSS_MIN_DB or high_pass_metrics["worst_s22_db"] > -RETURN_LOSS_MIN_DB:
        status = "TUNE"
        notes.append("high-frequency return loss is not acceptable")
    if lo_metrics["s21_max_db"] > -STOPBAND_REJECTION_MIN_DB:
        status = "TUNE"
        notes.append("LO stopband rejection is not acceptable")
    if peak["freq_ghz"] > PASS_CENTER + 0.25:
        notes.append("peak is high; lengthen resonators")
    elif peak["freq_ghz"] < PASS_CENTER - 0.25:
        notes.append("peak is low; shorten resonators")
    if pass_low_s21 + 3.0 < pass_high_s21:
        notes.append("low passband edge is weak; increase coupling")

    return {
        "candidate": candidate or path.stem.removesuffix("_hfss_trace"),
        "trace_csv": str(path),
        "status": status,
        "tx_score": f"{score:.3f}",
        "peak_freq_ghz": f"{peak['freq_ghz']:.4f}",
        "peak_s21_db": f"{peak['s21_db']:.4f}",
        "pass_low_s21_db": f"{pass_low_s21:.4f}",
        "pass_center_s21_db": f"{pass_center_s21:.4f}",
        "pass_high_s21_db": f"{pass_high_s21:.4f}",
        "passband_min_s21_db": f"{pass_metrics['s21_min_db']:.4f}",
        "passband_max_s21_db": f"{pass_metrics['s21_max_db']:.4f}",
        "passband_ripple_db": f"{pass_metrics['s21_ripple_db']:.4f}",
        "worst_s11_passband_db": f"{pass_metrics['worst_s11_db']:.4f}",
        "worst_s22_passband_db": f"{pass_metrics['worst_s22_db']:.4f}",
        "worst_s11_high_passband_db": f"{high_pass_metrics['worst_s11_db']:.4f}",
        "worst_s22_high_passband_db": f"{high_pass_metrics['worst_s22_db']:.4f}",
        "worst_high_return_loss_db": f"{max(high_pass_metrics['worst_s11_db'], high_pass_metrics['worst_s22_db']):.4f}",
        "high_return_loss_margin_db": f"{(-RETURN_LOSS_MIN_DB - max(high_pass_metrics['worst_s11_db'], high_pass_metrics['worst_s22_db'])):.4f}",
        "pass_high_s11_db": f"{pass_high_s11:.4f}",
        "pass_high_s22_db": f"{pass_high_s22:.4f}",
        "lo_stopband_max_s21_db": f"{lo_metrics['s21_max_db']:.4f}",
        "image_stopband_points": f"{image_metrics['points']:.0f}",
        "image_stopband_max_s21_db": f"{image_metrics['s21_max_db']:.4f}",
        "note": "; ".join(notes) if notes else "numeric targets met; review mesh and ports",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score TX_BAND1 14-23 GHz HFSS trace CSV feedback.")
    parser.add_argument("trace_csv", nargs="+", type=Path)
    parser.add_argument("--candidate", action="append", default=None)
    parser.add_argument("--out", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = []
    for index, trace in enumerate(args.trace_csv):
        candidate = args.candidate[index] if args.candidate and index < len(args.candidate) else None
        rows.append(score_trace(trace, candidate))
    fieldnames = list(rows[0].keys())
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {args.out}")
        return
    writer = csv.DictWriter(__import__("sys").stdout, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


if __name__ == "__main__":
    main()
