"""HFSS artifact naming and path helpers."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from simads.hfss.layout_io import configured_layout_id


def default_project_name(layout: dict[str, Any]) -> str:
    return f"{configured_layout_id(layout)}_hfss_verdict"


def resolve_project_path(args: argparse.Namespace, layout: dict[str, Any]) -> Path:
    if args.project:
        return args.project
    project_name = args.project_name or default_project_name(layout)
    return args.workspace_dir / f"{project_name}.aedt"


def expected_hfss_outputs(args: argparse.Namespace, layout: dict[str, Any]) -> dict[str, Path]:
    layout_id = configured_layout_id(layout)
    candidate = f"{layout_id}_hfss"
    svg_dir = args.out_dir / "svg"
    return {
        "project": resolve_project_path(args, layout),
        "s2p": args.s2p or args.out_dir / f"{layout_id}_hfss.s2p",
        "score_csv": args.score_out or args.out_dir / f"{layout_id}_hfss_score.csv",
        "trace_csv": args.out_dir / f"{layout_id}_hfss_trace.csv",
        "summary_csv": svg_dir / f"{candidate}_plot_summary.csv",
        "svg": svg_dir / f"{candidate}_s_curves.svg",
    }


__all__ = ["default_project_name", "expected_hfss_outputs", "resolve_project_path"]
