#!/usr/bin/env python3
"""Prune low-scoring TX_BAND1 MCFIL HFSS designs from an AEDT project."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from simads.hfss.aedt_startup import OperationLifecycle, apply_grpc_startup_compat
from simads.hfss.artifact_names import event_log_path_for_json
from simads.hfss.session import Hfss3dLayoutSessionConfig, open_hfss3dlayout_session

apply_grpc_startup_compat()


DEFAULT_PROJECT = REPO_ROOT / "projects" / "RFSOC_RF" / "TX_Fillter.aedt"
DEFAULT_FEEDBACK = REPO_ROOT / "projects" / "RFSOC_RF" / "hfss_runs" / "tx_band1_mcfil_corrected_tx_feedback.csv"
DEFAULT_KEEP_DESIGNS = {
    "TX_BAND1_MCFIL_ALUMINA_BB_14_23G",
    "TX_BAND1_MCFIL_R1_CNN002",
}


def _clean_design_name(name: Any) -> str:
    text = str(name)
    if ";" in text and text.split(";", 1)[0].isdigit():
        return text.split(";", 1)[1]
    return text


def _design_list(app: Any) -> list[str]:
    names = getattr(app, "design_list", None)
    if names:
        return [_clean_design_name(name) for name in names]
    try:
        raw = app.oproject.GetTopDesignList()
    except Exception:
        raw = []
    return [_clean_design_name(name) for name in raw]


def _delete_design(app: Any, design: str) -> Any:
    if hasattr(app, "delete_design"):
        return app.delete_design(design)
    return app.oproject.DeleteDesign(design)


def _candidate_to_design(candidate: str) -> str | None:
    if candidate == "tx_band1_mcfil_alumina_manual_ports":
        return "TX_BAND1_MCFIL_ALUMINA_BB_14_23G"
    match = re.match(r"tx_band1_mcfil_(r\d+)_cnn(\d+)", candidate, flags=re.IGNORECASE)
    if not match:
        return None
    round_id, cnn_id = match.groups()
    return f"TX_BAND1_MCFIL_{round_id.upper()}_CNN{cnn_id}"


def read_feedback(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def select_prune_designs(
    rows: list[dict[str, str]],
    *,
    score_below: float,
    keep_top_n: int,
    keep_designs: set[str],
) -> tuple[list[dict[str, Any]], set[str]]:
    ranked = sorted(rows, key=lambda row: float(row["tx_score"]), reverse=True)
    kept_by_rank = {
        design
        for row in ranked[:keep_top_n]
        for design in [_candidate_to_design(row.get("candidate", ""))]
        if design
    }
    keep = set(keep_designs) | kept_by_rank
    selected: dict[str, dict[str, Any]] = {}
    for row in rows:
        design = _candidate_to_design(row.get("candidate", ""))
        if not design or design in keep:
            continue
        score = float(row["tx_score"])
        if score >= score_below:
            continue
        current = selected.get(design)
        if current is None or score < float(current["tx_score"]):
            selected[design] = {
                "design": design,
                "candidate": row.get("candidate", ""),
                "tx_score": row["tx_score"],
                "worst_high_return_loss_db": row.get("worst_high_return_loss_db", ""),
                "note": row.get("note", ""),
            }
    return sorted(selected.values(), key=lambda row: float(row["tx_score"])), keep


def prune_designs(args: argparse.Namespace) -> dict[str, Any]:
    rows = read_feedback(args.feedback)
    keep_designs = set(DEFAULT_KEEP_DESIGNS) | set(args.keep_design)
    selected, keep = select_prune_designs(
        rows,
        score_below=args.score_below,
        keep_top_n=args.keep_top_n,
        keep_designs=keep_designs,
    )
    lifecycle = OperationLifecycle(
        "prune_tx_band_mcfil_low_score_designs",
        output=event_log_path_for_json(args.output) if args.output else None,
    )
    payload: dict[str, Any] = {
        "project": str(args.project),
        "feedback": str(args.feedback),
        "score_below": args.score_below,
        "keep_top_n": args.keep_top_n,
        "keep_designs": sorted(keep),
        "planned_delete": selected,
        "execute": bool(args.execute),
    }
    if not args.execute:
        payload["status"] = "dry_run"
        payload["lifecycle"] = lifecycle.finish(status="dry_run")
        return payload

    final_status = "failed"
    try:
        session_config = Hfss3dLayoutSessionConfig(
            label="prune_tx_band_mcfil_low_score_designs",
            project=args.project,
            design=None,
            version=args.version,
            non_graphical=args.non_graphical,
            new_desktop=args.new_desktop,
            close_on_exit=False,
            keep_open=args.keep_open,
            close_projects=args.close_projects,
            close_desktop=args.close_desktop,
            ready_timeout_s=args.ready_timeout_s,
            ready_settle_s=args.ready_settle_s,
            wait_ready=False,
        )
        with open_hfss3dlayout_session(session_config, lifecycle) as session:
            app = session.app
            payload.update(session.metadata())
            before = _design_list(app)
            payload["designs_before"] = before
            existing = set(before)
            deleted: list[dict[str, Any]] = []
            missing: list[str] = []
            skipped_active: list[str] = []
            active_design = _clean_design_name(getattr(app, "design_name", "") or "")
            for row in selected:
                design = row["design"]
                if design not in existing:
                    missing.append(design)
                    continue
                if design == active_design:
                    skipped_active.append(design)
                    continue
                with lifecycle.timed(f"delete_design:{design}"):
                    result = _delete_design(app, design)
                deleted.append({**row, "delete_result": str(result)})
            payload["deleted"] = deleted
            payload["missing"] = missing
            payload["skipped_active"] = skipped_active
            payload["designs_after"] = _design_list(app)
            if args.save:
                with lifecycle.timed("save_project"):
                    payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
            payload["status"] = "ok"
            final_status = "ok"
            return payload
    finally:
        if "lifecycle" not in payload:
            payload["lifecycle"] = lifecycle.finish(status=final_status)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prune low-scoring TX_BAND1 MCFIL HFSS designs.")
    parser.add_argument("--project", type=Path, default=DEFAULT_PROJECT)
    parser.add_argument("--feedback", type=Path, default=DEFAULT_FEEDBACK)
    parser.add_argument("--score-below", type=float, default=-100.0)
    parser.add_argument("--keep-top-n", type=int, default=8)
    parser.add_argument("--keep-design", action="append", default=[])
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--version", default="2026.1")
    parser.add_argument("--non-graphical", action="store_true", default=True)
    parser.add_argument("--graphical", action="store_false", dest="non_graphical")
    parser.add_argument("--new-desktop", action="store_true", default=True)
    parser.add_argument("--attach-existing", action="store_false", dest="new_desktop")
    parser.add_argument("--keep-open", action="store_true")
    parser.add_argument("--close-projects", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--close-desktop", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--ready-timeout-s", type=float, default=120.0)
    parser.add_argument("--ready-settle-s", type=float, default=3.0)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    payload = prune_designs(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if payload.get("status") in {"dry_run", "ok"} else 1


if __name__ == "__main__":
    argv = sys.argv[1:]
    raise SystemExit(main())
