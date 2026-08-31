#!/usr/bin/env python3
"""Plot TX band filter S-parameter traces as annotated SVG."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HIGH_PASSBAND = (18.800, 19.325)


def read_trace(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return [{key: float(value) for key, value in row.items()} for row in csv.DictReader(fp)]


def values(rows: list[dict[str, float]], column: str) -> list[float]:
    return [row[column] for row in rows]


def rows_in_band(rows: list[dict[str, float]], band: tuple[float, float]) -> list[dict[str, float]]:
    return [row for row in rows if band[0] <= row["freq_ghz"] <= band[1]]


def interp_row(rows: list[dict[str, float]], freq_ghz: float) -> dict[str, float]:
    ordered = sorted(rows, key=lambda row: row["freq_ghz"])
    if freq_ghz <= ordered[0]["freq_ghz"]:
        base = dict(ordered[0])
        base["freq_ghz"] = freq_ghz
        return base
    if freq_ghz >= ordered[-1]["freq_ghz"]:
        base = dict(ordered[-1])
        base["freq_ghz"] = freq_ghz
        return base
    for left, right in zip(ordered, ordered[1:], strict=False):
        lf = left["freq_ghz"]
        rf = right["freq_ghz"]
        if lf <= freq_ghz <= rf and rf > lf:
            alpha = (freq_ghz - lf) / (rf - lf)
            out = {"freq_ghz": freq_ghz}
            for key in left:
                if key == "freq_ghz":
                    continue
                out[key] = left[key] + alpha * (right[key] - left[key])
            return out
    raise ValueError(f"frequency is outside trace range: {freq_ghz}")


def mark_point(
    ax: plt.Axes,
    row: dict[str, float],
    column: str,
    label: str,
    color: str,
    xytext: tuple[float, float],
) -> None:
    x = row["freq_ghz"]
    y = row[column]
    ax.scatter([x], [y], s=30, color=color, edgecolor="#111827", linewidth=0.6, zorder=5)
    ax.annotate(
        label,
        xy=(x, y),
        xytext=xytext,
        textcoords="offset points",
        fontsize=7.0,
        color=color,
        fontweight="bold",
        ha="center",
        va="center",
        arrowprops={"arrowstyle": "-", "color": color, "linewidth": 0.65},
        bbox={"boxstyle": "round,pad=0.16", "facecolor": "white", "edgecolor": color, "alpha": 0.90},
        zorder=6,
    )


def add_marker_table(ax: plt.Axes, markers: list[dict[str, str | float]]) -> None:
    lines = ["Marker parameters", "ID   Trace  Freq(GHz)   Value(dB)  Point"]
    for marker in markers:
        lines.append(
            f"{marker['id']:<4} {marker['trace']:<5} {marker['freq']:>8.3f}   {marker['value']:>8.2f}  {marker['point']}"
        )
    ax.text(
        1.02,
        0.42,
        "\n".join(lines),
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=7.4,
        family="Consolas",
        color="#111827",
        bbox={"boxstyle": "round,pad=0.42", "facecolor": "#f8fafc", "edgecolor": "#cbd5e1", "alpha": 0.98},
    )


def add_score_markers(
    ax: plt.Axes,
    rows: list[dict[str, float]],
    *,
    passband: tuple[float, float],
    lo_stopband: tuple[float, float],
    high_passband: tuple[float, float],
) -> None:
    markers: list[dict[str, str | float]] = []

    def add_marker(
        marker_id: str,
        row: dict[str, float],
        column: str,
        trace: str,
        point: str,
        color: str,
        xytext: tuple[float, float],
    ) -> None:
        mark_point(ax, row, column, marker_id, color, xytext)
        markers.append(
            {
                "id": marker_id,
                "trace": trace,
                "freq": row["freq_ghz"],
                "value": row[column],
                "point": point,
            }
        )

    lo_low = interp_row(rows, lo_stopband[0])
    lo_high = interp_row(rows, lo_stopband[1])
    pass_low = interp_row(rows, passband[0])
    pass_high = interp_row(rows, passband[1])

    add_marker("M1", lo_low, "s21_db", "S21", "LO low", "#ea580c", (-16, -16))
    add_marker("M2", lo_high, "s21_db", "S21", "LO high", "#ea580c", (16, -16))
    add_marker("M3", pass_low, "s21_db", "S21", "pass low", "#b91c1c", (-18, -18))
    add_marker("M4", pass_high, "s21_db", "S21", "pass high", "#b91c1c", (18, -18))
    add_marker("M5", lo_low, "s11_db", "S11", "LO low", "#1d4ed8", (-16, 16))
    add_marker("M6", lo_high, "s11_db", "S11", "LO high", "#1d4ed8", (16, 16))
    add_marker("M7", pass_low, "s11_db", "S11", "pass low", "#2563eb", (-20, 20))
    add_marker("M8", pass_high, "s11_db", "S11", "pass high", "#2563eb", (20, 20))

    add_marker_table(ax, markers)


def plot_trace(
    trace: Path,
    output: Path,
    *,
    title: str,
    passband: tuple[float, float],
    lo_stopband: tuple[float, float],
    image_stopband: tuple[float, float] | None,
    high_passband: tuple[float, float],
    y_min: float,
    y_max: float,
) -> None:
    rows = read_trace(trace)
    if not rows:
        raise ValueError(f"empty trace CSV: {trace}")

    freq = values(rows, "freq_ghz")
    x_min = min(freq)
    x_max = max(freq)
    bands = [passband, lo_stopband]
    if image_stopband is not None:
        bands.append(image_stopband)
    x_min = min([x_min, *[band[0] for band in bands]])
    x_max = max([x_max, *[band[1] for band in bands]])

    fig, ax = plt.subplots(figsize=(12.0, 5.4), constrained_layout=False)
    fig.subplots_adjust(left=0.08, right=0.66, top=0.88, bottom=0.13)
    ax.axvspan(image_stopband[0], image_stopband[1], color="#f97316", alpha=0.10, label="Image stopband") if image_stopband is not None else None
    ax.axvspan(lo_stopband[0], lo_stopband[1], color="#dc2626", alpha=0.12, label="LO stopband")
    if image_stopband is not None:
        ax.text(
            (image_stopband[0] + image_stopband[1]) / 2.0,
            0.96,
            "Image stopband",
            transform=ax.get_xaxis_transform(),
            ha="center",
            va="top",
            fontsize=8,
            color="#c2410c",
            fontweight="bold",
        )
    ax.text(
        (lo_stopband[0] + lo_stopband[1]) / 2.0,
        0.90,
        "LO stopband",
        transform=ax.get_xaxis_transform(),
        ha="center",
        va="top",
        fontsize=8,
        color="#991b1b",
        fontweight="bold",
    )
    ax.axvspan(passband[0], passband[1], color="#16a34a", alpha=0.14, label="TX-F1 passband")
    ax.text(
        (passband[0] + passband[1]) / 2.0,
        0.84,
        "Passband",
        transform=ax.get_xaxis_transform(),
        ha="center",
        va="top",
        fontsize=8,
        color="#166534",
        fontweight="bold",
    )
    ax.axvspan(high_passband[0], high_passband[1], color="#7c3aed", alpha=0.08, label="High RL window")
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

    add_score_markers(ax, rows, passband=passband, lo_stopband=lo_stopband, high_passband=high_passband)

    ax.set_title(title)
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Magnitude (dB)")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.grid(True, which="both", linewidth=0.4, alpha=0.35)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=8)

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
    parser.add_argument("--high-passband", type=parse_band, default=HIGH_PASSBAND)
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
        high_passband=args.high_passband,
        y_min=args.y_min,
        y_max=args.y_max,
    )
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
