"""HFSS solve and Touchstone export helpers."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from simads.hfss.artifacts import expected_hfss_outputs
from simads.hfss.connector import FIXTURE_TYPE as MICROSTRIP_CONNECTOR_FIXTURE_TYPE
from simads.hfss.connector import SINGLE_CONNECTOR_FIXTURE_TYPE
from simads.hfss.layout_io import configured_layout_id
from simads.hfss.results import run_post_tools


@dataclass(frozen=True)
class HfssSolveExportResult:
    setup: str
    sweep: str
    s2p: str
    score: str | None
    trace_csv: str | None
    post_processed: bool

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if data["score"] is None:
            del data["score"]
        if data["trace_csv"] is None:
            del data["trace_csv"]
        return data


def solve_and_export_hfss(app: Any, layout: dict[str, Any], args: argparse.Namespace) -> HfssSolveExportResult:
    outputs = expected_hfss_outputs(args, layout)
    layout_id = configured_layout_id(layout)
    candidate = f"{layout_id}_hfss"

    app.analyze_setup(args.setup)
    exported = app.export_touchstone(
        setup=args.setup,
        sweep=args.sweep,
        output_file=str(outputs["s2p"]),
        renormalization=True,
        impedance=50,
    )
    s2p_path = Path(exported or outputs["s2p"])
    score_csv = outputs["score_csv"]
    trace_csv = outputs["trace_csv"]
    post_processed = False
    if exported or s2p_path.exists():
        fixture_type = layout.get("metadata", {}).get("fixture_type") if isinstance(layout.get("metadata"), dict) else None
        profile = (
            "connector"
            if fixture_type in {MICROSTRIP_CONNECTOR_FIXTURE_TYPE, SINGLE_CONNECTOR_FIXTURE_TYPE}
            else "filter"
        )
        run_post_tools(s2p_path, score_csv, trace_csv, args.out_dir / "svg", candidate, profile=profile)
        post_processed = True
    return HfssSolveExportResult(
        setup=args.setup,
        sweep=args.sweep,
        s2p=str(s2p_path),
        score=str(score_csv) if post_processed else None,
        trace_csv=str(trace_csv) if post_processed else None,
        post_processed=post_processed,
    )


__all__ = ["HfssSolveExportResult", "solve_and_export_hfss"]
