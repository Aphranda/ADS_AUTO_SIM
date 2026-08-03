#!/usr/bin/env python3
"""Plot RFPro S-parameter curves as SVG files."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.config import load_project
from simads.scoring import choose_frequency_column, choose_sparam_column, frequency_to_ghz, series_to_db


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def resolve_defaults(project_id: str, sweep_id: str | None, root: Path) -> tuple[Path | None, Path | None]:
    project = load_project(project_id, root=root)
    sweep = project.get_sweep(sweep_id)
    if sweep is None:
        return None, None
    summary = sweep.summary if sweep.summary.is_absolute() else root / sweep.summary
    results = sweep.results_dir if sweep.results_dir.is_absolute() else root / sweep.results_dir
    return summary, results


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


def load_trace(path: Path) -> tuple[list[float], dict[str, list[float]]]:
    rows = read_csv(path)
    if not rows:
        raise ValueError(f"empty CSV: {path}")
    columns = list(rows[0])
    freq_col = choose_frequency_column(columns)
    if freq_col is None:
        raise ValueError(f"CSV has no frequency column: {path}")
    freq = frequency_to_ghz([row[freq_col] for row in rows])
    traces: dict[str, list[float]] = {}
    for name in ("s11", "s21", "s22"):
        col = choose_sparam_column(columns, name)
        if col is not None:
            traces[name] = series_to_db([row[col] for row in rows])
    if "s21" not in traces:
        raise ValueError(f"CSV has no S21 column: {path}")
    return freq, traces


def decorate_axes(ax: plt.Axes, title: str, x_min: float, x_max: float) -> None:
    ax.axvspan(6.0, 8.0, color="#7bc96f", alpha=0.14, label="6-8G passband")
    ax.axvline(5.0, color="#d62728", alpha=0.62, linewidth=1.0, linestyle="--", label="5G stop target")
    ax.axhline(-5.0, color="#7bc96f", alpha=0.50, linewidth=0.9, linestyle=":")
    ax.axhline(-20.0, color="#d62728", alpha=0.50, linewidth=0.9, linestyle=":")
    ax.set_title(title)
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Magnitude (dB)")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(-60.0, 2.0)
    ax.grid(True, which="both", linewidth=0.4, alpha=0.35)


def resolve_x_limits(freq: list[float], x_min: float | None, x_max: float | None) -> tuple[float, float]:
    if not freq:
        raise ValueError("empty frequency axis")
    low = min(freq) if x_min is None else x_min
    high = max(freq) if x_max is None else x_max
    if low >= high:
        raise ValueError(f"invalid x-axis limits: {low:g} >= {high:g}")
    return low, high


def plot_individual(
    candidate: str,
    path: Path,
    out_dir: Path,
    sparams: list[str],
    x_min: float | None,
    x_max: float | None,
    show_legend: bool,
) -> Path:
    freq, traces = load_trace(path)
    x_low, x_high = resolve_x_limits(freq, x_min, x_max)
    fig, ax = plt.subplots(figsize=(8.5, 4.8), constrained_layout=True)
    colors = {"s11": "#1f77b4", "s21": "#c44e52", "s22": "#8172b2"}
    for name in sparams:
        if name in traces:
            ax.plot(freq, traces[name], label=name.upper(), color=colors.get(name), linewidth=1.35)
    decorate_axes(ax, candidate, x_low, x_high)
    if show_legend:
        ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8)
    out = out_dir / f"{candidate}_s_curves.svg"
    fig.savefig(out, format="svg", bbox_inches="tight")
    plt.close(fig)
    return out


def plot_overlay(
    sources: list[tuple[str, Path]],
    out_dir: Path,
    max_curves: int | None,
    sweep_id: str,
    x_min: float | None,
    x_max: float | None,
    show_legend: bool,
) -> Path:
    fig, ax = plt.subplots(figsize=(9.5, 5.2), constrained_layout=True)
    selected = sources[:max_curves] if max_curves is not None else sources
    all_freq: list[float] = []
    for candidate, path in selected:
        freq, traces = load_trace(path)
        all_freq.extend(freq)
        ax.plot(freq, traces["s21"], label=candidate.replace("pixel_qr16_fr4_210um_", ""), linewidth=1.1, alpha=0.82)
    x_low, x_high = resolve_x_limits(all_freq, x_min, x_max)
    decorate_axes(ax, f"{sweep_id} S21 overlay", x_low, x_high)
    if show_legend:
        ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=6)
    out = out_dir / f"{sweep_id}_s21_overlay.svg"
    fig.savefig(out, format="svg", bbox_inches="tight")
    plt.close(fig)
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate SVG S-parameter curves from RFPro CSV results.")
    parser.add_argument("--project-id", default="pixel_qr_bpf_fr4_210um")
    parser.add_argument("--sweep-id", default="pixel_qr_bpf_fr4_210um_r3_pixel_mutation_1to10")
    parser.add_argument("--summary", type=Path, default=None)
    parser.add_argument("--results-dir", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--candidate", action="append", default=None, help="Candidate to plot. May be repeated.")
    parser.add_argument("--sparams", default="s21", help="Comma-separated list: s11,s21,s22. Default: s21")
    parser.add_argument("--x-min", type=float, default=None, help="Minimum plotted frequency in GHz. Default: CSV min.")
    parser.add_argument("--x-max", type=float, default=None, help="Maximum plotted frequency in GHz. Default: CSV max.")
    parser.add_argument("--no-individual", action="store_true")
    parser.add_argument("--no-overlay", action="store_true")
    parser.add_argument("--overlay-max", type=int, default=None)
    parser.add_argument(
        "--individual-legend",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Show S-parameter legend on individual SVGs. Default: true.",
    )
    parser.add_argument(
        "--overlay-legend",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Show candidate legend on overlay SVGs. Default: false to avoid label overlap.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = repo_root()
    default_summary, default_results = resolve_defaults(args.project_id, args.sweep_id, root)
    summary = args.summary or default_summary
    results_dir = args.results_dir or default_results
    if summary is None or results_dir is None:
        raise SystemExit("Unable to resolve summary/results-dir.")
    summary = summary if summary.is_absolute() else root / summary
    results_dir = results_dir if results_dir.is_absolute() else root / results_dir
    candidates = set(args.candidate) if args.candidate else None
    sources = load_summary_sources(summary, candidates)
    if not sources:
        raise SystemExit("No RFPro CSV sources found.")
    out_dir = args.out_dir or (results_dir / "svg")
    out_dir.mkdir(parents=True, exist_ok=True)
    sparams = [part.strip().lower() for part in args.sparams.split(",") if part.strip()]

    written: list[Path] = []
    if not args.no_individual:
        for candidate, path in sources:
            written.append(
                plot_individual(
                    candidate,
                    path,
                    out_dir,
                    sparams,
                    args.x_min,
                    args.x_max,
                    args.individual_legend,
                )
            )
    if not args.no_overlay:
        written.append(plot_overlay(sources, out_dir, args.overlay_max, args.sweep_id, args.x_min, args.x_max, args.overlay_legend))
    print(f"Wrote {len(written)} SVG files to {out_dir}")


if __name__ == "__main__":
    main()
