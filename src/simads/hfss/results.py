"""HFSS result post-processing helpers."""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path
from typing import Any

from simads.hfss.aedt_startup import hidden_subprocess_kwargs

REPO_ROOT = Path(__file__).resolve().parents[3]
POSTPROCESS_PROFILES = {"filter", "connector"}


def _profile_tool(profile: str, *, connector_tool: str, filter_tool: str) -> str:
    if profile not in POSTPROCESS_PROFILES:
        raise ValueError(f"unsupported HFSS postprocess profile: {profile}")
    return connector_tool if profile == "connector" else filter_tool


def convert_s2p_to_csv(s2p: Path, out_csv: Path, *, profile: str = "filter") -> None:
    sys.path.insert(0, str(REPO_ROOT / "tools"))
    if profile == "connector":
        from analyze_connector_s2p import read_s2p_db

        samples = read_s2p_db(s2p)
    elif profile == "filter":
        from analyze_filter_s2p import read_s2p

        samples = read_s2p(s2p)
    else:
        raise ValueError(f"unsupported HFSS postprocess profile: {profile}")

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


def _run_hidden(command: list[str], *, lifecycle: Any | None, operation: str, tool: str | None = None) -> None:
    if lifecycle is None:
        subprocess.run(command, check=True, **hidden_subprocess_kwargs())
        return
    extra = {"tool": tool} if tool else {}
    with lifecycle.timed(operation, **extra):
        subprocess.run(command, check=True, **hidden_subprocess_kwargs())


def run_post_tools(
    s2p: Path,
    score_csv: Path,
    trace_csv: Path,
    svg_dir: Path,
    candidate: str,
    *,
    profile: str = "filter",
    lifecycle: Any | None = None,
) -> dict[str, str]:
    analyzer = _profile_tool(
        profile,
        connector_tool="analyze_connector_s2p.py",
        filter_tool="analyze_filter_s2p.py",
    )
    plotter = _profile_tool(
        profile,
        connector_tool="plot_connector_s_curves_svg.py",
        filter_tool="plot_filter_s_curves_svg.py",
    )
    analyze_command = [sys.executable, str(REPO_ROOT / "tools" / analyzer), str(s2p), "--out", str(score_csv)]
    _run_hidden(analyze_command, lifecycle=lifecycle, operation="score_s2p", tool=analyzer)

    if lifecycle is None:
        convert_s2p_to_csv(s2p, trace_csv, profile=profile)
    else:
        with lifecycle.timed("convert_s2p_to_trace_csv"):
            convert_s2p_to_csv(s2p, trace_csv, profile=profile)

    svg_dir.mkdir(parents=True, exist_ok=True)
    summary_csv = svg_dir / f"{candidate}_plot_summary.csv"
    if lifecycle is None:
        write_plot_summary(trace_csv, candidate, summary_csv)
    else:
        with lifecycle.timed("write_plot_summary"):
            write_plot_summary(trace_csv, candidate, summary_csv)

    plot_command = [
        sys.executable,
        str(REPO_ROOT / "tools" / plotter),
        "--summary",
        str(summary_csv),
    ]
    if profile == "filter":
        plot_command.extend(["--results-dir", str(svg_dir.parent)])
    plot_command.extend(
        [
            "--out-dir",
            str(svg_dir),
            "--sparams",
            "s11,s21,s22",
            "--no-overlay",
        ]
    )
    _run_hidden(plot_command, lifecycle=lifecycle, operation="plot_sparam_svg", tool=plotter)

    artifacts = {"score": str(score_csv), "trace_csv": str(trace_csv), "svg_dir": str(svg_dir)}
    if profile == "connector":
        smith_svg = svg_dir / f"{candidate}_smith.svg"
        smith_plotter = "plot_connector_smith_svg.py"
        smith_command = [
            sys.executable,
            str(REPO_ROOT / "tools" / smith_plotter),
            str(s2p),
            "--out",
            str(smith_svg),
            "--title",
            f"{candidate} Smith chart",
            "--band-min-ghz",
            "0.5",
            "--band-max-ghz",
            "10.0",
        ]
        _run_hidden(smith_command, lifecycle=lifecycle, operation="plot_smith_svg", tool=smith_plotter)
        artifacts["smith_svg"] = str(smith_svg)
    return artifacts


__all__ = ["POSTPROCESS_PROFILES", "convert_s2p_to_csv", "run_post_tools", "write_plot_summary"]
