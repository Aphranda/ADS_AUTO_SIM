#!/usr/bin/env python3
"""Generate band-limited connector TDR CSV and SVG from an S2P file."""

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

from simads.scoring.tdr import compute_tdr_points, summarize_tdr, write_tdr_csv


def plot_tdr(points, out: Path, title: str) -> Path:
    if not points:
        raise ValueError("no TDR points to plot")
    fig, ax = plt.subplots(figsize=(8.5, 4.8), constrained_layout=True)
    time_ns = [point.time_ns for point in points]
    ax.plot(time_ns, [point.s11_z_ohm for point in points], color="#1f77b4", linewidth=1.35, label="S11 input")
    ax.plot(time_ns, [point.s22_z_ohm for point in points], color="#8172b2", linewidth=1.35, label="S22 output")
    ax.axhline(50.0, color="#303640", linewidth=0.9, linestyle=":", alpha=0.75)
    ax.set_title(title)
    ax.set_xlabel("Time (ns)")
    ax.set_ylabel("Band-limited impedance (ohm)")
    ax.grid(True, which="both", linewidth=0.4, alpha=0.35)
    ax.legend(loc="best", fontsize=8)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="svg", bbox_inches="tight")
    plt.close(fig)
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate connector TDR data from Touchstone S11/S22.")
    parser.add_argument("s2p", type=Path)
    parser.add_argument("--csv-out", type=Path, required=True)
    parser.add_argument("--svg-out", type=Path, required=True)
    parser.add_argument("--title", default=None)
    parser.add_argument("--z0-ohm", type=float, default=50.0)
    parser.add_argument("--time-max-ns", type=float, default=5.0)
    parser.add_argument("--n-fft", type=int, default=None)
    parser.add_argument("--low-frequency-fill", choices=["hold", "zero"], default="hold")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    points = compute_tdr_points(
        args.s2p,
        z0_ohm=args.z0_ohm,
        time_max_ns=args.time_max_ns,
        n_fft=args.n_fft,
        low_frequency_fill=args.low_frequency_fill,
    )
    csv_out = write_tdr_csv(points, args.csv_out)
    svg_out = plot_tdr(points, args.svg_out, args.title or f"{args.s2p.stem} band-limited TDR")
    summary = summarize_tdr(points)
    print(f"Wrote {csv_out}")
    print(f"Wrote {svg_out}")
    print(
        "TDR summary: "
        f"S11 {summary['s11_z_min_ohm']:.2f}-{summary['s11_z_max_ohm']:.2f} ohm, "
        f"S22 {summary['s22_z_min_ohm']:.2f}-{summary['s22_z_max_ohm']:.2f} ohm"
    )


if __name__ == "__main__":
    main()
