#!/usr/bin/env python3
"""Plot SP8T four-port through, return, and isolation traces as SVG."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def load_summary_sources(summary: Path, candidates: set[str] | None) -> list[tuple[str, Path]]:
    rows = read_csv(summary)
    sources: list[tuple[str, Path]] = []
    for row in rows:
        candidate = row.get("candidate", "").strip()
        source = row.get("source", "").strip()
        if not candidate or not source:
            continue
        if candidates is not None and candidate not in candidates:
            continue
        path = Path(source)
        if path.exists():
            sources.append((candidate, path))
    return sources


def _floats(rows: list[dict[str, str]], column: str) -> list[float]:
    return [float(row[column]) for row in rows if row.get(column, "").strip()]


def resolve_x_limits(freq: list[float], x_min: float | None, x_max: float | None) -> tuple[float, float]:
    if not freq:
        raise ValueError("empty frequency axis")
    low = min(freq) if x_min is None else x_min
    high = max(freq) if x_max is None else x_max
    if low >= high:
        raise ValueError(f"invalid x-axis limits: {low:g} >= {high:g}")
    return low, high


def decorate_axes(ax: plt.Axes, title: str, x_min: float, x_max: float) -> None:
    ax.axhline(-1.5, color="#8a8f98", alpha=0.45, linewidth=0.8, linestyle=":")
    ax.axhline(-10.0, color="#8a8f98", alpha=0.45, linewidth=0.8, linestyle=":")
    ax.axhline(-30.0, color="#8a8f98", alpha=0.45, linewidth=0.8, linestyle=":")
    ax.set_title(title)
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Magnitude (dB)")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(-80.0, 2.0)
    ax.grid(True, which="both", linewidth=0.4, alpha=0.35)


def plot_individual(
    candidate: str,
    path: Path,
    out_dir: Path,
    x_min: float | None,
    x_max: float | None,
    show_legend: bool,
) -> Path:
    rows = read_csv(path)
    if not rows:
        raise ValueError(f"empty CSV: {path}")
    freq = _floats(rows, "freq_ghz")
    x_low, x_high = resolve_x_limits(freq, x_min, x_max)
    fig, ax = plt.subplots(figsize=(9.0, 5.0), constrained_layout=True)
    traces = {
        "S21 Port1->Port2": ("s21_db", "#1f77b4", 1.45),
        "S43 Port3->Port4": ("s43_db", "#c44e52", 1.45),
        "Worst return": ("worst_return_db", "#8172b2", 1.1),
        "Near-end isolation P1/P3": ("near_end_isolation_db", "#2ca02c", 1.05),
        "Far-end isolation P2/P4": ("far_end_isolation_db", "#d97706", 1.05),
        "Diagonal isolation": ("diagonal_isolation_db", "#6a1b9a", 1.0),
    }
    for label, (column, color, width) in traces.items():
        if column in rows[0]:
            ax.plot(freq, _floats(rows, column), label=label, color=color, linewidth=width)
    decorate_axes(ax, candidate, x_low, x_high)
    if show_legend:
        ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8)
    out = out_dir / f"{candidate}_sp8t_sparams.svg"
    fig.savefig(out, format="svg", bbox_inches="tight")
    plt.close(fig)
    return out


def plot_overlay(
    sources: list[tuple[str, Path]],
    out_dir: Path,
    label: str,
    x_min: float | None,
    x_max: float | None,
    show_legend: bool,
) -> Path:
    fig, ax = plt.subplots(figsize=(9.5, 5.2), constrained_layout=True)
    all_freq: list[float] = []
    for candidate, path in sources:
        rows = read_csv(path)
        freq = _floats(rows, "freq_ghz")
        all_freq.extend(freq)
        ax.plot(freq, _floats(rows, "s21_db"), label=f"{candidate} S21", linewidth=1.05, alpha=0.85)
        ax.plot(freq, _floats(rows, "s43_db"), label=f"{candidate} S43", linewidth=1.05, alpha=0.65)
    x_low, x_high = resolve_x_limits(all_freq, x_min, x_max)
    decorate_axes(ax, f"{label} SP8T through overlay", x_low, x_high)
    if show_legend:
        ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=6)
    out = out_dir / f"{label}_sp8t_through_overlay.svg"
    fig.savefig(out, format="svg", bbox_inches="tight")
    plt.close(fig)
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate SP8T four-port S-parameter SVGs from trace CSV results.")
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--candidate", action="append", default=None)
    parser.add_argument("--x-min", type=float, default=None)
    parser.add_argument("--x-max", type=float, default=None)
    parser.add_argument("--no-individual", action="store_true")
    parser.add_argument("--no-overlay", action="store_true")
    parser.add_argument("--overlay-label", default="sp8t")
    parser.add_argument("--legend", action=argparse.BooleanOptionalAction, default=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    candidates = set(args.candidate) if args.candidate else None
    sources = load_summary_sources(args.summary, candidates)
    if not args.no_individual:
        for candidate, path in sources:
            plot_individual(candidate, path, args.out_dir, args.x_min, args.x_max, args.legend)
    if not args.no_overlay and len(sources) > 1:
        plot_overlay(sources, args.out_dir, args.overlay_label, args.x_min, args.x_max, args.legend)


if __name__ == "__main__":
    main()
