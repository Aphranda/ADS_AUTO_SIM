"""HFSS artifact naming and path helpers."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from simads.hfss_contracts import (
    HFSS_PROJECT_ACTION_ADD,
    HFSS_PROJECT_ACTION_NEW,
    HFSS_PROJECT_ACTIONS,
    HFSS_PROJECT_MODEL_PER_DESIGN,
    HFSS_PROJECT_MODEL_SINGLE_AEDT,
    HFSS_PROJECT_MODELS,
)
from simads.hfss.project import default_project_name, resolve_project_path
from simads.hfss.layout_io import configured_layout_id


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


__all__ = [
    "HFSS_PROJECT_MODEL_PER_DESIGN",
    "HFSS_PROJECT_MODEL_SINGLE_AEDT",
    "HFSS_PROJECT_MODELS",
    "HFSS_PROJECT_ACTION_ADD",
    "HFSS_PROJECT_ACTION_NEW",
    "HFSS_PROJECT_ACTIONS",
    "default_project_name",
    "expected_hfss_outputs",
    "resolve_project_path",
]
