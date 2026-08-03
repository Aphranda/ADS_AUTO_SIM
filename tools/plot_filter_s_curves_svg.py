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


def decorate_axes(ax: plt.Axes, title: str) -> None:
    ax.axvspan(6.0, 8.0, color="#2ca02c", alpha=0.10, label="6-8G passband")
    ax.axvline(5.0, color="#d62728", alpha=0.55, linewidth=1.0, linestyle="--", label="5G stop target")
    ax.axhline(-5.0, color="#2ca02c", alpha=0.45, linewidth=0.9, linestyle=":")
    ax.axhline(-20.0, color="#d62728", alpha=0.45, linewidth=0.9, linestyle=":")
    ax.set_title(title)
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Magnitude (dB)")
    ax.set_xlim(1.0, 10.0)
    ax.set_ylim(-60.0, 2.0)
    ax.grid(True, which="both", linewidth=0.4, alpha=0.35)


def plot_individual(candidate: str, path: Path, out_dir: Path, sparams: list[str]) -> Path:
    freq, traces = load_trace(path)
    fig, ax = plt.subplots(figsize=(8.5, 4.8), constrained_layout=True)
    colors = {"s11": "#9467bd", "s21": "#1f77b4", "s22": "#8c564b"}
    for name in sparams:
        if name in traces:
            ax.plot(freq, traces[name], label=name.upper(), color=colors.get(name), linewidth=1.4)
    decorate_axes(ax, candidate)
    ax.legend(loc="lower left", fontsize=8)
    out = out_dir / f"{candidate}_s_curves.svg"
    fig.savefig(out, format="svg")
    plt.close(fig)
    return out


def plot_overlay(
    sources: list[tuple[str, Path]],
    out_dir: Path,
    max_curves: int | None,
    sweep_id: str,
) -> Path:
    fig, ax = plt.subplots(figsize=(9.5, 5.2), constrained_layout=True)
    selected = sources[:max_curves] if max_curves is not None else sources
    for candidate, path in selected:
        freq, traces = load_trace(path)
        ax.plot(freq, traces["s21"], label=candidate.replace("pixel_qr16_fr4_210um_", ""), linewidth=1.1, alpha=0.82)
    decorate_axes(ax, f"{sweep_id} S21 overlay")
    ax.legend(loc="lower left", fontsize=6, ncol=2)
    out = out_dir / f"{sweep_id}_s21_overlay.svg"
    fig.savefig(out, format="svg")
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
    parser.add_argument("--no-individual", action="store_true")
    parser.add_argument("--no-overlay", action="store_true")
    parser.add_argument("--overlay-max", type=int, default=None)
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
            written.append(plot_individual(candidate, path, out_dir, sparams))
    if not args.no_overlay:
        written.append(plot_overlay(sources, out_dir, args.overlay_max, args.sweep_id))
    print(f"Wrote {len(written)} SVG files to {out_dir}")


if __name__ == "__main__":
    main()
