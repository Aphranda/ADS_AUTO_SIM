#!/usr/bin/env python3
"""Extract broad S-parameter response features from RFPro CSV files."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
import sys

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.config import load_project
from simads.scoring import choose_frequency_column, choose_sparam_column, frequency_to_ghz, interp, series_to_db


SAMPLE_FREQS = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]


def fmt(value: float) -> str:
    return "nan" if math.isnan(value) else f"{value:.2f}"


def avg(values: list[float]) -> float:
    clean = [value for value in values if not math.isnan(value)]
    return sum(clean) / len(clean) if clean else float("nan")


def load_trace(path: Path) -> tuple[list[float], dict[str, list[float]]]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        rows = list(csv.DictReader(fp))
    if not rows:
        raise ValueError(f"empty CSV: {path}")
    columns = list(rows[0])
    freq_col = choose_frequency_column(columns)
    if freq_col is None:
        raise ValueError(f"CSV has no frequency column: {path}")
    s_cols = {name: choose_sparam_column(columns, name) for name in ("s11", "s21", "s12", "s22")}
    if s_cols["s21"] is None:
        raise ValueError(f"CSV has no S21 column: {path}")
    freq = frequency_to_ghz([row[freq_col] for row in rows])
    traces = {
        name: series_to_db([row[col] for row in rows])
        for name, col in s_cols.items()
        if col is not None
    }
    return freq, traces


def threshold_intervals(freq: list[float], s21: list[float], threshold_db: float) -> list[tuple[float, float]]:
    intervals: list[tuple[float, float]] = []
    start: float | None = None
    last_freq: float | None = None
    for f_ghz, value in sorted(zip(freq, s21, strict=False)):
        if value >= threshold_db:
            if start is None:
                start = f_ghz
            last_freq = f_ghz
        elif start is not None and last_freq is not None:
            intervals.append((start, last_freq))
            start = None
            last_freq = None
    if start is not None and last_freq is not None:
        intervals.append((start, last_freq))
    return [(start, stop) for start, stop in intervals if stop - start >= 0.10]


def values_in(freq: list[float], values: list[float], start: float, stop: float) -> list[float]:
    return [value for f_ghz, value in zip(freq, values, strict=False) if start <= f_ghz <= stop]


def classify(intervals: list[tuple[float, float]], low_avg: float, mid_avg: float, high_avg: float, peak_db: float, notch_db: float) -> str:
    if peak_db < -10.0:
        return "attenuating_network"
    if low_avg > -6.0 and high_avg > -6.0 and notch_db < min(low_avg, high_avg) - 8.0:
        return "bandstop_or_notch"
    if not intervals:
        return "no_clear_passband"
    if len(intervals) >= 2:
        return "multiband"
    start, stop = intervals[0]
    if start <= 1.25 and stop >= 9.5:
        return "wideband_through"
    if start <= 1.25:
        return "lowpass_like"
    if stop >= 9.5:
        return "highpass_like"
    return "bandpass_like"


def extract(candidate: str, path: Path, notes: str) -> dict[str, str]:
    freq, traces = load_trace(path)
    s21 = traces["s21"]
    peak_idx = max(range(len(s21)), key=s21.__getitem__)
    min_idx = min(range(len(s21)), key=s21.__getitem__)
    intervals_m6 = threshold_intervals(freq, s21, -6.0)
    intervals_m10 = threshold_intervals(freq, s21, -10.0)
    main_band = max(intervals_m6, key=lambda item: item[1] - item[0]) if intervals_m6 else (float("nan"), float("nan"))
    band_values = values_in(freq, s21, main_band[0], main_band[1]) if intervals_m6 else []
    band_s11 = values_in(freq, traces["s11"], main_band[0], main_band[1]) if intervals_m6 and "s11" in traces else []
    band_s22 = values_in(freq, traces["s22"], main_band[0], main_band[1]) if intervals_m6 and "s22" in traces else []
    low_avg = avg(values_in(freq, s21, 1.0, 3.0))
    mid_avg = avg(values_in(freq, s21, 6.0, 8.0))
    high_avg = avg(values_in(freq, s21, 8.5, 10.0))
    kind = classify(intervals_m6, low_avg, mid_avg, high_avg, s21[peak_idx], s21[min_idx])

    row = {
        "candidate": candidate,
        "response_class": kind,
        "peak_freq_ghz": fmt(freq[peak_idx]),
        "peak_s21_db": fmt(s21[peak_idx]),
        "deepest_notch_freq_ghz": fmt(freq[min_idx]),
        "deepest_notch_s21_db": fmt(s21[min_idx]),
        "main_m6_band_start_ghz": fmt(main_band[0]),
        "main_m6_band_stop_ghz": fmt(main_band[1]),
        "main_m6_band_bw_ghz": fmt(main_band[1] - main_band[0] if intervals_m6 else float("nan")),
        "main_m6_band_min_s21_db": fmt(min(band_values) if band_values else float("nan")),
        "main_m6_band_ripple_db": fmt(max(band_values) - min(band_values) if band_values else float("nan")),
        "main_m6_band_worst_s11_db": fmt(max(band_s11) if band_s11 else float("nan")),
        "main_m6_band_worst_s22_db": fmt(max(band_s22) if band_s22 else float("nan")),
        "low_1_3_avg_s21_db": fmt(low_avg),
        "mid_6_8_avg_s21_db": fmt(mid_avg),
        "high_8p5_10_avg_s21_db": fmt(high_avg),
        "m6_passbands": "|".join(f"{start:.2f}-{stop:.2f}" for start, stop in intervals_m6),
        "m10_passbands": "|".join(f"{start:.2f}-{stop:.2f}" for start, stop in intervals_m10),
        "source": str(path),
        "notes": notes,
    }
    for sample in SAMPLE_FREQS:
        row[f"s21_{sample:g}g_db"] = fmt(interp(freq, s21, sample))
    return row


def load_summary_sources(summary: Path) -> list[tuple[str, Path, str]]:
    with summary.open(newline="", encoding="utf-8-sig") as fp:
        rows = list(csv.DictReader(fp))
    sources: list[tuple[str, Path, str]] = []
    for row in rows:
        source = row.get("source", "").strip()
        if not source:
            continue
        sources.append((row.get("candidate", "").strip(), Path(source), row.get("notes", "").strip()))
    return sources


def resolve_defaults(project_id: str, sweep_id: str | None, root: Path) -> tuple[Path | None, Path | None]:
    try:
        project = load_project(project_id, root=root)
    except FileNotFoundError:
        return None, None
    sweep = project.get_sweep(sweep_id)
    if sweep is None:
        return None, None
    summary = sweep.summary if sweep.summary.is_absolute() else root / sweep.summary
    results = sweep.results_dir if sweep.results_dir.is_absolute() else root / sweep.results_dir
    return summary, results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract response features from RFPro CSV files.")
    parser.add_argument("--project-id", default="pixel_qr_bpf_fr4_210um")
    parser.add_argument("--sweep-id", default=None)
    parser.add_argument("--summary", type=Path, default=None)
    parser.add_argument("--results-dir", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    default_summary, default_results = resolve_defaults(args.project_id, args.sweep_id, root)
    summary = args.summary or default_summary
    results_dir = args.results_dir or default_results
    if summary is not None and summary.exists():
        sources = load_summary_sources(summary)
    elif results_dir is not None:
        sources = [
            (path.stem.removesuffix("_mm_coords_rfpro"), path, "")
            for path in sorted(results_dir.glob("*_rfpro.csv"))
        ]
    else:
        raise SystemExit("Pass --summary/--results-dir or a project sweep that resolves to results.")
    rows = [extract(candidate, source, notes) for candidate, source, notes in sources]
    if not rows:
        raise SystemExit("No RFPro CSV sources found.")
    out_path = args.out or ((results_dir or summary.parent) / "filter_features.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} feature rows: {out_path}")


if __name__ == "__main__":
    main()
