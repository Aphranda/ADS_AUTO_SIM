#!/usr/bin/env python3
"""Run TX_BAND1 MCFIL boardband candidates while reusing one AEDT session."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SINGLE_RUNNER = REPO_ROOT / "tools" / "run_tx_band_mcfil_boardband_candidate.py"
DEFAULT_FEEDBACK = REPO_ROOT / "projects" / "RFSOC_RF" / "hfss_runs" / "tx_band1_mcfil_corrected_tx_feedback.csv"


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON must contain an object: {path}")
    return data


def layout_id_from_path(path: Path) -> str:
    data = load_json(path)
    return str(data.get("layout_id") or data.get("metadata", {}).get("layout_id") or path.stem.removesuffix("_layout"))


def default_candidate_id(layout_id: str) -> str:
    return f"{layout_id}_p2up_graphical"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def planned_layouts(plan: Path | None, explicit_layouts: list[Path]) -> list[Path]:
    layouts: list[Path] = []
    if plan is not None:
        for row in read_csv(plan):
            value = row.get("layout_json")
            if not value:
                continue
            path = Path(value)
            if not path.is_absolute():
                path = REPO_ROOT / path
            layouts.append(path)
    layouts.extend(explicit_layouts)
    seen: set[Path] = set()
    unique: list[Path] = []
    for layout in layouts:
        resolved = layout.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(resolved)
    return unique


def existing_candidates(feedback: Path) -> set[str]:
    return {str(row.get("candidate") or "") for row in read_csv(feedback)}


def terminate_process_tree(pid: int) -> None:
    try:
        import psutil
    except Exception:
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], check=False, capture_output=True, text=True)
        return
    try:
        parent = psutil.Process(pid)
    except psutil.Error:
        return
    children = parent.children(recursive=True)
    for process in children:
        try:
            process.terminate()
        except psutil.Error:
            pass
    try:
        parent.terminate()
    except psutil.Error:
        pass
    gone, alive = psutil.wait_procs([parent, *children], timeout=8)
    for process in alive:
        try:
            process.kill()
        except psutil.Error:
            pass


def run_candidate_command(command: list[str], *, timeout_s: float) -> subprocess.CompletedProcess[str]:
    process = subprocess.Popen(
        command,
        cwd=REPO_ROOT,
        text=True,
        stdout=None,
        stderr=None,
    )
    try:
        returncode = process.wait(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        terminate_process_tree(process.pid)
        raise
    if returncode != 0:
        raise subprocess.CalledProcessError(returncode, command)
    return subprocess.CompletedProcess(command, returncode)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run TX_BAND1 MCFIL boardband candidates with AEDT session reuse.")
    parser.add_argument("--plan", type=Path, default=None, help="Candidate plan CSV with a layout_json column.")
    parser.add_argument("--layout", type=Path, action="append", default=[], help="Explicit layout JSON. Can be repeated.")
    parser.add_argument("--feedback", type=Path, default=DEFAULT_FEEDBACK)
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of candidates to run after filtering.")
    parser.add_argument("--replace-feedback", action="store_true")
    parser.add_argument("--no-skip-existing", action="store_true")
    parser.add_argument("--attach-existing-first", action="store_true", help="Assume AEDT is already open before the first run.")
    parser.add_argument("--timeout-minutes", type=float, default=6.0, help="Maximum wall time for each candidate before the batch moves on.")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def build_command(layout: Path, *, attach_existing: bool, replace_feedback: bool, dry_run: bool) -> list[str]:
    command = [
        sys.executable,
        str(SINGLE_RUNNER),
        "--layout",
        str(layout),
        "--keep-open",
    ]
    if attach_existing:
        command.append("--attach-existing")
    if replace_feedback:
        command.append("--replace-feedback")
    if dry_run:
        command.append("--dry-run")
    return command


def main() -> None:
    args = parse_args()
    layouts = planned_layouts(args.plan, args.layout)
    if not layouts:
        raise SystemExit("No layouts to run. Provide --plan or --layout.")

    existing = existing_candidates(args.feedback)
    selected: list[tuple[Path, str]] = []
    skipped: list[str] = []
    for layout in layouts:
        candidate = default_candidate_id(layout_id_from_path(layout))
        if candidate in existing and not args.replace_feedback and not args.no_skip_existing:
            skipped.append(candidate)
            continue
        selected.append((layout, candidate))
        if args.limit is not None and len(selected) >= args.limit:
            break

    results: list[dict[str, Any]] = []
    for index, (layout, candidate) in enumerate(selected):
        attach_existing = args.attach_existing_first or index > 0
        command = build_command(
            layout,
            attach_existing=attach_existing,
            replace_feedback=args.replace_feedback,
            dry_run=args.dry_run,
        )
        print(
            json.dumps(
                {
                    "status": "starting",
                    "index": index + 1,
                    "total": len(selected),
                    "candidate": candidate,
                    "layout": str(layout),
                    "attach_existing": attach_existing,
                    "command": command,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        try:
            completed = run_candidate_command(command, timeout_s=args.timeout_minutes * 60.0)
            results.append({"candidate": candidate, "returncode": completed.returncode, "attach_existing": attach_existing})
        except subprocess.TimeoutExpired:
            results.append(
                {
                    "candidate": candidate,
                    "returncode": "timeout",
                    "attach_existing": attach_existing,
                    "timeout_minutes": args.timeout_minutes,
                }
            )
            break
        except subprocess.CalledProcessError as exc:
            results.append({"candidate": candidate, "returncode": exc.returncode, "attach_existing": attach_existing})
            break

    print(
        json.dumps(
            {
                "status": "ok",
                "planned": len(layouts),
                "selected": len(selected),
                "skipped_existing": skipped,
                "results": results,
                "aedt_session_policy": "first run starts/keeps AEDT open; later runs attach to existing AEDT",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
