#!/usr/bin/env python3
"""Export an existing AEDT report to CSV through PyAEDT."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from simads.hfss.aedt_startup import apply_grpc_startup_compat, apply_pyaedt_settings


def _metric_summary(csv_path: Path) -> dict[str, Any]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as fp:
        reader = csv.DictReader(fp)
        fields = reader.fieldnames or []
        rows = [{key: float(value) for key, value in row.items()} for row in reader]
    if not fields or not rows:
        return {"rows": len(rows), "columns": fields}
    freq_col = fields[0]
    traces = fields[1:]
    summary: dict[str, Any] = {"rows": len(rows), "columns": fields, "freq_col": freq_col, "traces": {}}
    for trace in traces:
        values = [row[trace] for row in rows]
        min_row = min(rows, key=lambda row: row[trace])
        max_row = max(rows, key=lambda row: row[trace])
        summary["traces"][trace] = {
            "min_db": min(values),
            "min_freq_ghz": min_row[freq_col],
            "max_db": max(values),
            "max_freq_ghz": max_row[freq_col],
            "value_3p55g_db": min(rows, key=lambda row: abs(row[freq_col] - 3.55))[trace],
            "value_8g_db": min(rows, key=lambda row: abs(row[freq_col] - 8.0))[trace],
        }
    return summary


def export_report(args: argparse.Namespace) -> dict[str, Any]:
    apply_grpc_startup_compat()
    from ansys.aedt.core import Hfss3dLayout, settings

    apply_pyaedt_settings(settings)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    app = Hfss3dLayout(
        project=str(args.project),
        design=args.design,
        version=args.version,
        non_graphical=args.non_graphical,
        new_desktop=args.new_desktop,
        close_on_exit=False,
        remove_lock=args.remove_lock,
    )
    try:
        report_names = list(app.post.all_report_names or [])
        exported = Path(app.post.export_report_to_csv(str(args.out_dir), args.report))
        target = args.output or args.out_dir / f"{args.design}_{args.report.replace(' ', '_')}.csv"
        if exported.resolve() != target.resolve():
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                target.unlink()
            shutil.move(str(exported), str(target))
        return {
            "status": "ok",
            "project": str(args.project),
            "design": args.design,
            "report": args.report,
            "available_reports": report_names,
            "csv": str(target),
            "summary": _metric_summary(target),
        }
    finally:
        app.release_desktop(close_projects=bool(args.new_desktop), close_desktop=bool(args.new_desktop))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export an existing HFSS/AEDT report CSV through PyAEDT.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--report", default="S Parameter Plot1")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--version", default="2026.1")
    parser.add_argument("--new-desktop", action="store_true")
    parser.add_argument("--graphical", action="store_false", dest="non_graphical")
    parser.add_argument("--non-graphical", action="store_true", default=True)
    parser.add_argument("--remove-lock", action="store_true")
    parser.add_argument("--json-out", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = export_report(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    print(text)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
