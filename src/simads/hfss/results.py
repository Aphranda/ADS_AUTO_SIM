"""HFSS result post-processing helpers."""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def convert_s2p_to_csv(s2p: Path, out_csv: Path) -> None:
    sys.path.insert(0, str(REPO_ROOT / "tools"))
    from analyze_filter_s2p import read_s2p

    samples = read_s2p(s2p)
    with out_csv.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=["freq_ghz", "s11_db", "s21_db", "s12_db", "s22_db"])
        writer.writeheader()
        for freq, s11, s21, s12, s22 in samples:
            writer.writerow(
                {
                    "freq_ghz": f"{freq:.9g}",
                    "s11_db": f"{s11:.6g}",
                    "s21_db": f"{s21:.6g}",
                    "s12_db": f"{s12:.6g}",
                    "s22_db": f"{s22:.6g}",
                }
            )


def write_plot_summary(trace_csv: Path, candidate: str, summary_csv: Path) -> Path:
    with summary_csv.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=["candidate", "source"])
        writer.writeheader()
        writer.writerow({"candidate": candidate, "source": str(trace_csv)})
    return summary_csv


def run_post_tools(s2p: Path, score_csv: Path, trace_csv: Path, svg_dir: Path, candidate: str) -> None:
    subprocess.run([sys.executable, str(REPO_ROOT / "tools" / "analyze_filter_s2p.py"), str(s2p), "--out", str(score_csv)], check=True)
    convert_s2p_to_csv(s2p, trace_csv)
    svg_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools" / "plot_filter_s_curves_svg.py"),
            "--summary",
            str(write_plot_summary(trace_csv, candidate, svg_dir / f"{candidate}_plot_summary.csv")),
            "--results-dir",
            str(svg_dir.parent),
            "--out-dir",
            str(svg_dir),
            "--sparams",
            "s11,s21,s22",
            "--no-overlay",
        ],
        check=True,
    )


__all__ = ["convert_s2p_to_csv", "run_post_tools", "write_plot_summary"]
