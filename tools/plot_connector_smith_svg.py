#!/usr/bin/env python3
"""Plot Smith chart SVGs for connector launch S2P files."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from simads.scoring.connector import db, read_s2p


def _clip(points: list[tuple[float, float]]) -> tuple[list[float], list[float]]:
    xs: list[float] = []
    ys: list[float] = []
    for x, y in points:
        if x * x + y * y <= 1.0005:
            xs.append(x)
            ys.append(y)
        else:
            xs.append(math.nan)
            ys.append(math.nan)
    return xs, ys


def _gamma_from_z(z: complex) -> complex:
    return (z - 1.0) / (z + 1.0)


def draw_smith_grid(ax: plt.Axes) -> None:
    ax.add_patch(Circle((0, 0), 1.0, fill=False, color="#303640", linewidth=1.0))
    ax.axhline(0, color="#7b818a", linewidth=0.7, alpha=0.55)
    ax.axvline(0, color="#7b818a", linewidth=0.45, alpha=0.25)

    for r in (0.2, 0.5, 1.0, 2.0, 5.0):
        center = r / (1.0 + r)
        radius = 1.0 / (1.0 + r)
        ax.add_patch(Circle((center, 0), radius, fill=False, color="#9aa1aa", linewidth=0.45, alpha=0.45))
        ax.text(center - radius + 0.015, 0.025, f"r={r:g}", fontsize=6, color="#6f7782")

    r_values = [0.0, 0.2, 0.5, 1.0, 2.0, 5.0, 12.0]
    for x in (0.2, 0.5, 1.0, 2.0, 5.0):
        upper = [_gamma_from_z(complex(r, x)) for r in r_values]
        lower = [_gamma_from_z(complex(r, -x)) for r in r_values]
        ux, uy = _clip([(value.real, value.imag) for value in upper])
        lx, ly = _clip([(value.real, value.imag) for value in lower])
        ax.plot(ux, uy, color="#9aa1aa", linewidth=0.45, alpha=0.45)
        ax.plot(lx, ly, color="#9aa1aa", linewidth=0.45, alpha=0.45)
        if ux and uy:
            ax.text(ux[-2], uy[-2], f"+j{x:g}", fontsize=6, color="#6f7782")
        if lx and ly:
            ax.text(lx[-2], ly[-2], f"-j{x:g}", fontsize=6, color="#6f7782")

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-1.08, 1.08)
    ax.set_ylim(-1.08, 1.08)
    ax.set_xlabel("Re(Gamma)")
    ax.set_ylabel("Im(Gamma)")
    ax.grid(False)


def plot_smith(s2p: Path, out: Path, title: str, band_min: float, band_max: float) -> Path:
    samples = [
        row
        for row in read_s2p(s2p)
        if band_min <= float(row["freq_ghz"]) <= band_max
    ]
    if not samples:
        raise ValueError(f"no samples in {band_min:g}-{band_max:g} GHz for {s2p}")

    fig, ax = plt.subplots(figsize=(7.2, 7.2), constrained_layout=True)
    draw_smith_grid(ax)
    colors = {"s11": "#1f77b4", "s22": "#8172b2"}
    labels = {"s11": "S11", "s22": "S22"}
    worst_name = "s11"
    worst_row = samples[0]
    worst_db = -999.0

    for name in ("s11", "s22"):
        gamma = [complex(row[name]) for row in samples]
        freq = [float(row["freq_ghz"]) for row in samples]
        ax.plot(
            [value.real for value in gamma],
            [value.imag for value in gamma],
            color=colors[name],
            linewidth=1.35,
            label=labels[name],
        )
        ax.scatter(gamma[0].real, gamma[0].imag, color=colors[name], marker="o", s=18)
        ax.scatter(gamma[-1].real, gamma[-1].imag, color=colors[name], marker="s", s=18)
        local_row = max(samples, key=lambda row: db(complex(row[name])))
        local_db = db(complex(local_row[name]))
        if local_db > worst_db:
            worst_db = local_db
            worst_name = name
            worst_row = local_row
        ax.text(gamma[0].real, gamma[0].imag, f" {labels[name]} {freq[0]:g}G", fontsize=7, color=colors[name])
        ax.text(gamma[-1].real, gamma[-1].imag, f" {freq[-1]:g}G", fontsize=7, color=colors[name])

    worst_gamma = complex(worst_row[worst_name])
    worst_freq = float(worst_row["freq_ghz"])
    ax.scatter(worst_gamma.real, worst_gamma.imag, color="#c44e52", marker="x", s=52, linewidth=1.5)
    ax.text(
        -1.04,
        -1.04,
        f"Worst return: {worst_name.upper()} {worst_db:.2f} dB @ {worst_freq:.3g} GHz",
        fontsize=8,
        color="#303640",
    )
    ax.set_title(title)
    ax.legend(loc="upper right", fontsize=8)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="svg", bbox_inches="tight")
    plt.close(fig)
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot connector S11/S22 Smith chart from an S2P file.")
    parser.add_argument("s2p", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--title", default=None)
    parser.add_argument("--band-min-ghz", type=float, default=0.5)
    parser.add_argument("--band-max-ghz", type=float, default=10.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    title = args.title or f"{args.s2p.stem} Smith chart"
    out = plot_smith(args.s2p, args.out, title, args.band_min_ghz, args.band_max_ghz)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
