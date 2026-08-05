#!/usr/bin/env python3
"""Analyze an existing HFSS 3D Layout project and export S-parameters."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
AEDT_VERSION = "2026.1"


def run_post_tools(s2p: Path, score_csv: Path, out_dir: Path, candidate: str, profile: str) -> dict[str, str]:
    trace_csv = out_dir / f"{candidate}_trace.csv"
    analyzer = "analyze_connector_s2p.py" if profile == "connector" else "analyze_filter_s2p.py"
    plotter = "plot_connector_s_curves_svg.py" if profile == "connector" else "plot_filter_s_curves_svg.py"
    subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / analyzer), str(s2p), "--out", str(score_csv)],
        check=True,
    )
    convert_s2p_to_csv(s2p, trace_csv)
    svg_dir = out_dir / "svg"
    svg_dir.mkdir(parents=True, exist_ok=True)
    summary_csv = svg_dir / f"{candidate}_plot_summary.csv"
    write_plot_summary(trace_csv, candidate, summary_csv)
    plot_command = [
        sys.executable,
        str(REPO_ROOT / "tools" / plotter),
        "--summary",
        str(summary_csv),
    ]
    if profile == "filter":
        plot_command.extend(["--results-dir", str(out_dir)])
    plot_command.extend(
        [
            "--out-dir",
            str(svg_dir),
            "--sparams",
            "s11,s21,s22",
            "--no-overlay",
        ]
    )
    subprocess.run(plot_command, check=True)
    return {"score": str(score_csv), "trace_csv": str(trace_csv), "svg_dir": str(svg_dir)}


def convert_s2p_to_csv(s2p: Path, out_csv: Path) -> None:
    sys.path.insert(0, str(REPO_ROOT / "tools"))
    from analyze_connector_s2p import read_s2p_db

    samples = read_s2p_db(s2p)
    import csv

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


def write_plot_summary(trace_csv: Path, candidate: str, summary_csv: Path) -> None:
    import csv

    with summary_csv.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=["candidate", "source"])
        writer.writeheader()
        writer.writerow({"candidate": candidate, "source": str(trace_csv)})


def object_names(items: Any) -> list[str]:
    names: list[str] = []
    for item in items or []:
        names.append(getattr(item, "name", str(item)))
    return names


def run(args: argparse.Namespace) -> dict[str, Any]:
    from ansys.aedt.core import Hfss3dLayout

    args.out_dir.mkdir(parents=True, exist_ok=True)
    app = Hfss3dLayout(
        project=str(args.project),
        design=args.design,
        version=args.version,
        non_graphical=args.non_graphical,
        new_desktop=True,
        close_on_exit=not args.keep_open,
        remove_lock=args.remove_lock,
    )
    try:
        result: dict[str, Any] = {
            "project": str(args.project),
            "design": args.design,
            "ports": object_names(getattr(app, "ports", [])),
            "setup": args.setup,
            "sweep": args.sweep,
            "analyze": not args.export_only,
        }
        if not args.export_only:
            app.analyze_setup(args.setup)
        s2p = args.s2p or args.out_dir / f"{args.candidate}.s2p"
        exported = app.export_touchstone(
            setup=args.setup,
            sweep=args.sweep,
            output_file=str(s2p),
            renormalization=True,
            impedance=50,
        )
        s2p_path = Path(exported or s2p)
        result["s2p"] = str(s2p_path)
        if s2p_path.exists():
            score_csv = args.score_out or args.out_dir / f"{args.candidate}_score.csv"
            result["postprocess_profile"] = args.postprocess_profile
            result.update(run_post_tools(s2p_path, score_csv, args.out_dir, args.candidate, args.postprocess_profile))
        return result
    finally:
        if not args.keep_open:
            app.release_desktop(close_projects=True, close_desktop=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run/export an existing HFSS 3D Layout project without rebuilding geometry.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", default="I7_FR4_HFSS_VERDICT")
    parser.add_argument("--version", default=AEDT_VERSION)
    parser.add_argument("--setup", default="Setup_4to10G")
    parser.add_argument("--sweep", default="Sweep_4to10G_40pt")
    parser.add_argument("--candidate", default="hfss_manual_ports")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--s2p", type=Path, default=None)
    parser.add_argument("--score-out", type=Path, default=None)
    parser.add_argument("--postprocess-profile", choices=["connector", "filter"], default="connector")
    parser.add_argument("--export-only", action="store_true")
    parser.add_argument("--non-graphical", action="store_true")
    parser.add_argument("--keep-open", action="store_true")
    parser.add_argument("--remove-lock", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    text = json.dumps(run(args), ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
