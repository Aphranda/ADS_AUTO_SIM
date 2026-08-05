#!/usr/bin/env python3
"""Plot a before/after overlay for connector launch S-parameter traces."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


AEDT_S_RE = re.compile(r"dB\(S\(([^,]+),([^)]+)\)\)")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def load_trace_csv(path: Path) -> dict[str, list[float]]:
    rows = read_csv(path)
    if not rows:
        raise ValueError(f"empty CSV: {path}")
    return {
        "freq": [float(row["freq_ghz"]) for row in rows],
        "s11": [float(row["s11_db"]) for row in rows],
        "s21": [float(row["s21_db"]) for row in rows],
        "s22": [float(row["s22_db"]) for row in rows],
    }


def load_aedt_report_csv(path: Path) -> dict[str, list[float]]:
    rows = read_csv(path)
    if not rows:
        raise ValueError(f"empty CSV: {path}")
    columns = list(rows[0])
    freq_col = next((col for col in columns if col.lower().startswith("freq")), None)
    if freq_col is None:
        raise ValueError(f"no frequency column in {path}")

    returns: list[str] = []
    through: list[str] = []
    for col in columns:
        match = AEDT_S_RE.search(col)
        if not match:
            continue
        left, right = match.group(1).strip(), match.group(2).strip()
        if left == right:
            returns.append(col)
        else:
            through.append(col)
    if len(returns) < 2 or not through:
        raise ValueError(f"could not infer S-parameter columns in {path}")

    return {
        "freq": [float(row[freq_col]) for row in rows],
        "s11": [float(row[returns[0]]) for row in rows],
        "s21": [float(row[through[0]]) for row in rows],
        "s22": [float(row[returns[1]]) for row in rows],
    }


def decorate(ax: plt.Axes, title: str) -> None:
    ax.axhline(-3.0, color="#7b818a", alpha=0.45, linewidth=0.8, linestyle=":")
    ax.axhline(-10.0, color="#7b818a", alpha=0.45, linewidth=0.8, linestyle=":")
    ax.axhline(-20.0, color="#7b818a", alpha=0.35, linewidth=0.8, linestyle=":")
    ax.set_title(title)
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Magnitude (dB)")
    ax.set_xlim(0.5, 10.0)
    ax.set_ylim(-30.0, 2.0)
    ax.grid(True, which="both", linewidth=0.4, alpha=0.35)


def plot(before: dict[str, list[float]], after: dict[str, list[float]], out: Path, title: str) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9.5, 5.2), constrained_layout=True)
    colors = {"s11": "#1f77b4", "s21": "#c44e52", "s22": "#8172b2"}
    labels = {"s11": "S11", "s21": "S21", "s22": "S22"}
    for name in ("s11", "s21", "s22"):
        ax.plot(
            before["freq"],
            before[name],
            color=colors[name],
            linewidth=1.15,
            alpha=0.38,
            linestyle=(0, (5, 3)),
            label=f"{labels[name]} before",
        )
        ax.plot(
            after["freq"],
            after[name],
            color=colors[name],
            linewidth=1.45,
            alpha=0.96,
            label=f"{labels[name]} optimized",
        )
    decorate(ax, title)
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8)
    fig.savefig(out, format="svg", bbox_inches="tight")
    plt.close(fig)
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot connector S-parameter before/after overlay.")
    parser.add_argument("--before", type=Path, required=True, help="Unoptimized AEDT report CSV or normalized trace CSV.")
    parser.add_argument("--after", type=Path, required=True, help="Optimized normalized trace CSV.")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--title", default="SINGLE_END_SMA_CPW_30MM connector launch before/after")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    before = load_trace_csv(args.before) if args.before.name.endswith("_trace.csv") else load_aedt_report_csv(args.before)
    after = load_trace_csv(args.after)
    out = plot(before, after, args.out, args.title)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
