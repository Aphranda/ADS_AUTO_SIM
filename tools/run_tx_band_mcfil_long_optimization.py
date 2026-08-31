#!/usr/bin/env python3
"""Long-running TX_BAND1 MCFIL CNN/HFSS optimization loop."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
ITER_ROOT = REPO_ROOT / "projects" / "RFSOC_RF" / "layouts" / "tx_band1_mcfil_iter"
FEEDBACK = REPO_ROOT / "projects" / "RFSOC_RF" / "hfss_runs" / "tx_band1_mcfil_corrected_tx_feedback.csv"
PYTHON = Path(r"D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe")


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def feedback_count(feedback: Path) -> int:
    return len(read_csv(feedback))


def round_dirs() -> list[Path]:
    dirs = [REPO_ROOT / "projects" / "RFSOC_RF" / "layouts" / "tx_band1_mcfil"]
    dirs.extend(sorted(path for path in ITER_ROOT.glob("round*") if path.is_dir()))
    return dirs


def next_round_id() -> int:
    values: list[int] = []
    for path in ITER_ROOT.glob("round*"):
        suffix = path.name.removeprefix("round")
        if suffix.isdigit():
            values.append(int(suffix))
    return max(values, default=0) + 1


def run(command: list[str], *, timeout_s: float | None = None) -> dict[str, Any]:
    try:
        completed = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, timeout=timeout_s)
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")
        return {
            "command": command,
            "returncode": "timeout",
            "timeout_s": timeout_s,
            "stdout_tail": stdout[-4000:],
            "stderr_tail": stderr[-4000:],
        }
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
    }


def generate_round(round_no: int, *, top_k: int, build_top_k: int, seed: int, epochs: int) -> dict[str, Any]:
    out_dir = ITER_ROOT / f"round{round_no}"
    command = [
        str(PYTHON),
        "tools/make_tx_band_mcfil_cnn_iteration.py",
        "--feedback",
        str(FEEDBACK),
        "--out-dir",
        str(out_dir),
        "--round-id",
        f"round{round_no}",
        "--epochs",
        str(epochs),
        "--seed",
        str(seed),
        "--top-k",
        str(top_k),
        "--build-top-k",
        str(build_top_k),
    ]
    for path in round_dirs():
        command.extend(["--params-dir", str(path)])
    result = run(command)
    result["round"] = round_no
    result["plan"] = str(out_dir / f"tx_band1_mcfil_round{round_no}_cnn_candidate_plan.csv")
    return result


def run_hfss_batch(plan: Path, *, batch_size: int, timeout_minutes: float, attach_existing_first: bool) -> dict[str, Any]:
    command = [
        str(PYTHON),
        "tools/run_tx_band_mcfil_boardband_batch.py",
        "--plan",
        str(plan),
        "--limit",
        str(batch_size),
        "--timeout-minutes",
        str(timeout_minutes),
    ]
    if attach_existing_first:
        command.append("--attach-existing-first")
    return run(command, timeout_s=(timeout_minutes * 60.0 + 90.0) * max(1, batch_size))


def prune_low_score(*, score_below: float, keep_top_n: int) -> dict[str, Any]:
    out = REPO_ROOT / "projects" / "RFSOC_RF" / "reports" / "tx_band1_mcfil_prune_long_loop_latest.json"
    command = [
        str(PYTHON),
        "tools/hfss/prune_tx_band_mcfil_low_score_designs.py",
        "--score-below",
        str(score_below),
        "--keep-top-n",
        str(keep_top_n),
        "--execute",
        "--save",
        "--graphical",
        "--attach-existing",
        "--keep-open",
        "--output",
        str(out),
    ]
    return run(command, timeout_s=180.0)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run TX_BAND1 MCFIL rolling CNN/HFSS optimization.")
    parser.add_argument("--target-count", type=int, default=200)
    parser.add_argument("--batch-size", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=12)
    parser.add_argument("--build-top-k", type=int, default=6)
    parser.add_argument("--epochs", type=int, default=1600)
    parser.add_argument("--timeout-minutes", type=float, default=6.0)
    parser.add_argument("--prune-every", type=int, default=2)
    parser.add_argument("--prune-score-below", type=float, default=-100.0)
    parser.add_argument("--keep-top-n", type=int, default=12)
    parser.add_argument("--max-rounds", type=int, default=10)
    parser.add_argument("--attach-existing-first", action="store_true")
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "projects" / "RFSOC_RF" / "reports" / "tx_band1_mcfil_long_optimization_latest.json")
    args = parser.parse_args()

    events: list[dict[str, Any]] = []
    start_count = feedback_count(FEEDBACK)
    current_count = start_count
    round_no = next_round_id()
    for loop_index in range(args.max_rounds):
        if current_count >= args.target_count:
            break
        seed = 20260831 + round_no
        generated = generate_round(round_no, top_k=args.top_k, build_top_k=args.build_top_k, seed=seed, epochs=args.epochs)
        events.append({"step": "generate", **generated})
        if generated["returncode"] != 0:
            break
        plan = Path(generated["plan"])
        batch = run_hfss_batch(
            plan,
            batch_size=args.batch_size,
            timeout_minutes=args.timeout_minutes,
            attach_existing_first=args.attach_existing_first or loop_index > 0,
        )
        events.append({"step": "hfss_batch", "round": round_no, **batch})
        current_count = feedback_count(FEEDBACK)
        if (loop_index + 1) % args.prune_every == 0:
            events.append({"step": "prune", "round": round_no, **prune_low_score(score_below=args.prune_score_below, keep_top_n=args.keep_top_n)})
        if batch["returncode"] != 0:
            break
        round_no += 1

    report = {
        "status": "complete" if current_count >= args.target_count else "partial",
        "target_count": args.target_count,
        "start_feedback_count": start_count,
        "final_feedback_count": current_count,
        "events": events,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] in {"complete", "partial"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
