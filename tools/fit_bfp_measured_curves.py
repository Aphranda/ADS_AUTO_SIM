#!/usr/bin/env python3
"""Fit measured BFP marker curves and compare them with simulated S21."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from simads.scoring.filter_curve_fit import (
    FitOptions,
    compare_fit_to_simulation,
    dump_json,
    fit_measured_batch,
    write_compare_csv,
    write_fit_csv,
)
from simads.scoring.touchstone import read_sparameter_network


def _plot_fit_svg(fit_payload: dict[str, object], simulation_s2p: Path, out: Path, title: str) -> Path:
    board_ids: list[str] = list(fit_payload["board_ids"])
    rows = list(fit_payload["fit_rows"])
    network = read_sparameter_network(simulation_s2p).require_nports(2, system="filter")
    grid = [float(row["freq_ghz"]) for row in rows]
    fig, ax = plt.subplots(figsize=(9.6, 5.4), constrained_layout=True)
    palette = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd"]
    for index, board_id in enumerate(board_ids):
        color = palette[index % len(palette)]
        ax.plot(
            grid,
            [float(row[f"{board_id}_s21_db"]) for row in rows],
            color=color,
            linewidth=1.1,
            alpha=0.8,
            label=f"{board_id} fit",
        )
    ax.plot(
        grid,
        [float(row["mean_s21_db"]) for row in rows],
        color="#111111",
        linewidth=2.2,
        label="measured mean fit",
    )
    ax.plot(
        grid,
        [network.interp_db(freq, "s21") for freq in grid],
        color="#d62728",
        linewidth=1.8,
        linestyle="--",
        label="HFSS sim",
    )
    for marker in (5.0, 6.0, 6.3, 8.0, 9.0):
        ax.axvline(marker, color="#909090", linewidth=0.5, linestyle=":", alpha=0.5)
    ax.set_title(title)
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("S21 (dB)")
    ax.grid(True, linewidth=0.4, alpha=0.35)
    ax.legend(loc="best", fontsize=8)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="svg", bbox_inches="tight")
    plt.close(fig)
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fit measured BFP curves and compare them with simulation.")
    parser.add_argument("--measured", type=Path, required=True)
    parser.add_argument("--simulation-s2p", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--freq-min-ghz", type=float, default=5.0)
    parser.add_argument("--freq-max-ghz", type=float, default=9.0)
    parser.add_argument("--freq-step-ghz", type=float, default=0.01)
    parser.add_argument("--title", default="BFP measured curve fit vs HFSS")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    fit_payload = fit_measured_batch(
        args.measured,
        options=FitOptions(args.freq_min_ghz, args.freq_max_ghz, args.freq_step_ghz),
    )
    compare_payload = compare_fit_to_simulation(fit_payload, args.simulation_s2p)
    fit_csv = write_fit_csv(fit_payload, out_dir / f"{args.measured.stem}_fit.csv")
    compare_csv = write_compare_csv(compare_payload, out_dir / f"{args.measured.stem}_fit_vs_sim.csv")
    fit_svg = _plot_fit_svg(fit_payload, args.simulation_s2p, out_dir / f"{args.measured.stem}_fit.svg", args.title)
    dump_json(fit_payload, out_dir / f"{args.measured.stem}_fit.json")
    dump_json(compare_payload, out_dir / f"{args.measured.stem}_fit_vs_sim.json")
    print(f"Wrote {fit_csv}")
    print(f"Wrote {compare_csv}")
    print(f"Wrote {fit_svg}")


if __name__ == "__main__":
    main()
