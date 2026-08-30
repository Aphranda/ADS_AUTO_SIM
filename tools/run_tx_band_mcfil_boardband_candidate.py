#!/usr/bin/env python3
"""Run one TX_BAND1 MCFIL HFSS boardband candidate and append TX feedback."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROJECT = REPO_ROOT / "projects" / "RFSOC_RF" / "TX_Fillter.aedt"
DEFAULT_STACKUP = REPO_ROOT / "config" / "stackups" / "ALUMINA_250UM_MCFIL_2L.json"
DEFAULT_FEEDBACK = REPO_ROOT / "projects" / "RFSOC_RF" / "hfss_runs" / "tx_band1_mcfil_corrected_tx_feedback.csv"
HFSS_RUNNER = REPO_ROOT / "tools" / "hfss" / "run_hfss3dlayout_filter_verdict.py"
TX_SCORER = REPO_ROOT / "tools" / "score_tx_band_filter.py"


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON must contain an object: {path}")
    return data


def layout_id_from_path(path: Path) -> str:
    data = load_json(path)
    return str(data.get("layout_id") or data.get("metadata", {}).get("layout_id") or path.stem.removesuffix("_layout"))


def default_candidate_id(layout_id: str, hidden_graphical: bool) -> str:
    suffix = "p2up_hidden_graphical" if hidden_graphical else "p2up_graphical"
    return f"{layout_id}_{suffix}"


def default_design(layout_id: str) -> str:
    token = layout_id.upper()
    token = token.removeprefix("TX_BAND1_MCFIL_")
    parts = token.split("_")
    if len(parts) >= 3 and parts[0].startswith("R") and parts[1].startswith("CNN"):
        token = "_".join(parts[:2])
    return f"TX_BAND1_MCFIL_{token}"[:80]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def append_feedback(feedback: Path, score_csv: Path, *, replace: bool) -> dict[str, Any]:
    score_rows = read_csv(score_csv)
    if len(score_rows) != 1:
        raise ValueError(f"expected exactly one score row in {score_csv}, got {len(score_rows)}")
    new_row = score_rows[0]
    rows = read_csv(feedback)
    existing_index = next((index for index, row in enumerate(rows) if row.get("candidate") == new_row.get("candidate")), None)
    if existing_index is not None and not replace:
        return {"feedback": str(feedback), "action": "skipped_existing", "candidate": new_row.get("candidate")}
    if existing_index is None:
        rows.append(new_row)
        action = "appended"
    else:
        rows[existing_index] = new_row
        action = "replaced"
    write_csv(feedback, rows)
    return {"feedback": str(feedback), "action": action, "candidate": new_row.get("candidate"), "rows": len(rows)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one TX_BAND1 MCFIL 14-23 GHz boardband HFSS candidate.")
    parser.add_argument("--layout", type=Path, required=True)
    parser.add_argument("--candidate-id", default=None)
    parser.add_argument("--design", default=None)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--feedback", type=Path, default=DEFAULT_FEEDBACK)
    parser.add_argument("--project", type=Path, default=DEFAULT_PROJECT)
    parser.add_argument("--stackup-config", type=Path, default=DEFAULT_STACKUP)
    parser.add_argument("--start-ghz", type=float, default=14.0)
    parser.add_argument("--stop-ghz", type=float, default=23.0)
    parser.add_argument("--points", type=int, default=181)
    parser.add_argument("--adaptive-frequency-ghz", type=float, default=18.5)
    parser.add_argument("--setup", default="Setup_14to23G")
    parser.add_argument("--sweep", default="Sweep_BB_14to23G_181pt")
    parser.add_argument("--sweep-type", default="Interpolating", choices=["Interpolating", "Discrete", "Fast"])
    parser.add_argument("--graphical", action="store_true", default=True)
    parser.add_argument("--attach-existing", action="store_true", help="Reuse an already running AEDT Desktop session.")
    parser.add_argument("--keep-open", action="store_true", help="Leave AEDT open after this candidate.")
    parser.add_argument(
        "--hidden-graphical",
        action="store_true",
        default=False,
        help="Experimental: set ANSYS_DISABLE_DISPLAY=1 while keeping graphical AEDT backend.",
    )
    parser.add_argument("--no-hidden-graphical", action="store_false", dest="hidden_graphical")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-append-feedback", action="store_true")
    parser.add_argument("--replace-feedback", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    layout = args.layout
    layout_id = layout_id_from_path(layout)
    candidate_id = args.candidate_id or default_candidate_id(layout_id, args.hidden_graphical)
    design = args.design or default_design(layout_id)
    out_dir = args.out_dir or REPO_ROOT / "projects" / "RFSOC_RF" / "hfss_runs" / f"{candidate_id}_bb_14_23g"
    trace_csv = out_dir / f"{layout_id}_hfss_trace.csv"
    tx_score = out_dir / f"{candidate_id}_tx_score.csv"

    command = [
        sys.executable,
        str(HFSS_RUNNER),
        "--layout",
        str(layout),
        "--out-dir",
        str(out_dir),
        "--project",
        str(args.project),
        "--project-action",
        "add",
        "--design",
        design,
        "--project-id",
        "RFSOC_RF",
        "--device-id",
        "filter.mcfil",
        "--candidate-id",
        candidate_id,
        "--stackup-config",
        str(args.stackup_config),
        "--start-ghz",
        f"{args.start_ghz:g}",
        "--stop-ghz",
        f"{args.stop_ghz:g}",
        "--points",
        str(args.points),
        "--adaptive-frequency-ghz",
        f"{args.adaptive_frequency_ghz:g}",
        "--setup",
        args.setup,
        "--sweep",
        args.sweep,
        "--sweep-type",
        args.sweep_type,
        "--port-type",
        "aedt-edge",
        "--gnd-boundary-mode",
        "port-edges",
        "--write-manifest",
    ]
    if args.graphical:
        command.append("--graphical")
    if args.attach_existing:
        command.append("--attach-existing")
    if args.keep_open:
        command.append("--keep-open")
    if args.hidden_graphical:
        command.append("--hidden-graphical")
    if args.dry_run:
        command.append("--dry-run")

    subprocess.run(command, cwd=REPO_ROOT, check=True)
    if args.dry_run:
        return
    subprocess.run(
        [
            sys.executable,
            str(TX_SCORER),
            str(trace_csv),
            "--candidate",
            candidate_id,
            "--out",
            str(tx_score),
        ],
        cwd=REPO_ROOT,
        check=True,
    )
    feedback_result = None
    if not args.no_append_feedback:
        feedback_result = append_feedback(args.feedback, tx_score, replace=args.replace_feedback)
    print(
        json.dumps(
            {
                "status": "ok",
                "layout_id": layout_id,
                "candidate_id": candidate_id,
                "design": design,
                "out_dir": str(out_dir),
                "trace_csv": str(trace_csv),
                "tx_score": str(tx_score),
                "feedback": feedback_result,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
