#!/usr/bin/env python3
"""Plot TX band filter S-parameter traces as annotated SVG."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def read_trace(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return [{key: float(value) for key, value in row.items()} for row in csv.DictReader(fp)]


def values(rows: list[dict[str, float]], column: str) -> list[float]:
    return [row[column] for row in rows]


def plot_trace(
    trace: Path,
    output: Path,
    *,
    title: str,
    passband: tuple[float, float],
    lo_stopband: tuple[float, float],
    image_stopband: tuple[float, float] | None,
    y_min: float,
    y_max: float,
) -> None:
    rows = read_trace(trace)
    if not rows:
        raise ValueError(f"empty trace CSV: {trace}")

    freq = values(rows, "freq_ghz")
    fig, ax = plt.subplots(figsize=(10.0, 5.4), constrained_layout=True)
    ax.axvspan(lo_stopband[0], lo_stopband[1], color="#dc2626", alpha=0.12, label="LO stopband")
    if image_stopband is not None:
        ax.axvspan(image_stopband[0], image_stopband[1], color="#f97316", alpha=0.10, label="Image stopband")
    ax.axvspan(passband[0], passband[1], color="#16a34a", alpha=0.14, label="TX-F1 passband")
    ax.axhline(-2.5, color="#16a34a", alpha=0.75, linewidth=0.9, linestyle=":", label="IL target")
    ax.axhline(-15.0, color="#2563eb", alpha=0.65, linewidth=0.9, linestyle=":", label="RL target")
    ax.axhline(-40.0, color="#dc2626", alpha=0.65, linewidth=0.9, linestyle=":", label="Stop target")

    traces = [
        ("S11", "s11_db", "#2563eb", 1.2),
        ("S21", "s21_db", "#dc2626", 1.5),
        ("S22", "s22_db", "#7c3aed", 1.2),
    ]
    for label, column, color, width in traces:
        if column in rows[0]:
            ax.plot(freq, values(rows, column), label=label, color=color, linewidth=width)

    ax.set_title(title)
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Magnitude (dB)")
    ax.set_xlim(min(freq), max(freq))
    ax.set_ylim(y_min, y_max)
    ax.grid(True, which="both", linewidth=0.4, alpha=0.35)
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8)

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, format="svg", bbox_inches="tight")
    plt.close(fig)


def parse_band(text: str) -> tuple[float, float]:
    parts = [part.strip() for part in text.split(",")]
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("band must be formatted as low,high")
    low, high = float(parts[0]), float(parts[1])
    if low >= high:
        raise argparse.ArgumentTypeError("band low edge must be lower than high edge")
    return low, high


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate TX band annotated S-parameter SVG from trace CSV.")
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--title", default="TX Band Filter HFSS S-Parameters")
    parser.add_argument("--passband", type=parse_band, default=(17.700, 19.325))
    parser.add_argument("--lo-stopband", type=parse_band, default=(14.400, 15.025))
    parser.add_argument("--image-stopband", type=parse_band, default=None)
    parser.add_argument("--y-min", type=float, default=-60.0)
    parser.add_argument("--y-max", type=float, default=2.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    plot_trace(
        args.trace,
        args.out,
        title=args.title,
        passband=args.passband,
        lo_stopband=args.lo_stopband,
        image_stopband=args.image_stopband,
        y_min=args.y_min,
        y_max=args.y_max,
    )
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
