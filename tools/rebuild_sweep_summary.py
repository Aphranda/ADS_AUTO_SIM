#!/usr/bin/env python3
"""Rebuild a sweep summary from per-candidate score CSV files."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

_SIM_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _SIM_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.config import load_pipeline, load_project, resolve_pipeline_id


PREFERRED_FIELDS = [
    "candidate",
    "cell",
    "status",
    "error_class",
    "failed_step",
    "elapsed_s",
    "run_id",
    "profile_id",
    "pipeline_id",
    "target_profile_id",
    "score_version",
    "notes",
]


def repo_root() -> Path:
    return _SIM_ROOT


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fp:
        data = json.load(fp)
    return data if isinstance(data, dict) else {}


def cell_name(candidate: str) -> str:
    return f"{candidate}_mm_coords" if not candidate.endswith("_mm_coords") else candidate


def find_run_dir(results_dir: Path, candidate: str, row: dict[str, str]) -> Path | None:
    run_id = row.get("run_id", "").strip()
    if run_id:
        candidate_path = results_dir / "runs" / run_id
        if candidate_path.exists():
            return candidate_path
    matches = sorted((results_dir / "runs").glob(f"*_{candidate}_*")) if (results_dir / "runs").exists() else []
    return matches[-1] if matches else None


def run_context(run_dir: Path | None) -> dict[str, str]:
    if run_dir is None:
        return {}
    state = read_json(run_dir / "state.json")
    manifest = read_json(run_dir / "run_manifest.json")
    context: dict[str, str] = {"run_dir": str(run_dir)}
    for key in ("run_id", "project_id", "round_id", "candidate_id", "profile_id", "pipeline_id", "target_profile_id", "score_version"):
        value = manifest.get(key)
        if value is not None:
            context[key] = str(value)
    for key in ("run_id", "candidate_id", "profile_id", "status", "failed_step", "error_class", "elapsed_s"):
        value = state.get(key)
        if value is not None:
            context[key] = str(value)
    return context


def ordered_fieldnames(rows: list[dict[str, str]]) -> list[str]:
    seen: set[str] = set()
    fields: list[str] = []
    for key in PREFERRED_FIELDS:
        if any(key in row for row in rows):
            fields.append(key)
            seen.add(key)
    for row in rows:
        for key in row:
            if key not in seen:
                fields.append(key)
                seen.add(key)
    return fields


def build_rows(
    plan_rows: list[dict[str, str]],
    results_dir: Path,
    *,
    profile_id: str,
    pipeline_id: str,
    target_profile_id: str,
    score_version: str,
) -> tuple[list[dict[str, str]], list[str]]:
    rows: list[dict[str, str]] = []
    missing: list[str] = []
    for plan in plan_rows:
        candidate = plan["name"].strip()
        cell = cell_name(candidate)
        score_path = results_dir / f"{cell}_score.csv"
        if not score_path.exists():
            missing.append(candidate)
            continue
        score_rows = read_csv(score_path)
        if not score_rows:
            missing.append(candidate)
            continue
        for score in score_rows:
            context = run_context(find_run_dir(results_dir, candidate, score))
            source = Path(score.get("source", ""))
            score_cell = source.stem.removesuffix("_rfpro") if str(source) else cell
            state_status = context.get("status", "")
            score_status = score.get("status", "scored")
            status = state_status if state_status == "failed" else score_status
            rows.append(
                {
                    **score,
                    "candidate": context.get("candidate_id", score.get("candidate_id", candidate)),
                    "cell": score_cell,
                    "status": status,
                    "error_class": context.get("error_class", score.get("error_class", "")),
                    "failed_step": context.get("failed_step", score.get("failed_step", "")),
                    "elapsed_s": context.get("elapsed_s", score.get("elapsed_s", "")),
                    "run_id": context.get("run_id", score.get("run_id", "")),
                    "run_dir": context.get("run_dir", ""),
                    "profile_id": context.get("profile_id", score.get("profile_id", profile_id)),
                    "pipeline_id": context.get("pipeline_id", score.get("pipeline_id", pipeline_id)),
                    "target_profile_id": context.get("target_profile_id", score.get("target_profile_id", target_profile_id)),
                    "score_version": context.get("score_version", score.get("score_version", score_version)),
                    "notes": plan.get("notes", ""),
                }
            )
    return rows, missing


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise SystemExit("No score rows found. Check --plan and --results-dir.")
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ordered_fieldnames(rows)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_missing(path: Path, missing: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=["candidate", "status"])
        writer.writeheader()
        writer.writerows({"candidate": candidate, "status": "PENDING_SCORE"} for candidate in missing)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rebuild sweep_summary.csv from existing *_score.csv files.")
    parser.add_argument("--project-id", default="pixel_qr_bpf_fr4_210um")
    parser.add_argument("--sweep-id", default=None)
    parser.add_argument("--pipeline-id", default=None)
    parser.add_argument("--plan", type=Path, default=None)
    parser.add_argument("--results-dir", type=Path, default=None)
    parser.add_argument("--summary", type=Path, default=None)
    parser.add_argument("--missing-out", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = repo_root()
    project = load_project(args.project_id, root=root)
    sweep = project.get_sweep(args.sweep_id)
    pipeline_id = resolve_pipeline_id(project, sweep, args.pipeline_id)
    if not pipeline_id:
        raise SystemExit("No pipeline_id found. Set --pipeline-id or configure the project sweep.")
    pipeline = load_pipeline(pipeline_id, root=root)

    plan = args.plan or (sweep.plan if sweep else None)
    results_dir = args.results_dir or (sweep.results_dir if sweep else None)
    summary = args.summary or (sweep.summary if sweep else None)
    if plan is None or results_dir is None or summary is None:
        raise SystemExit("Unable to resolve plan/results-dir/summary. Pass them explicitly.")
    plan = plan if plan.is_absolute() else root / plan
    results_dir = results_dir if results_dir.is_absolute() else root / results_dir
    summary = summary if summary.is_absolute() else root / summary

    rows, missing = build_rows(
        read_csv(plan),
        results_dir,
        profile_id=pipeline.profile_id,
        pipeline_id=pipeline.pipeline_id,
        target_profile_id=pipeline.scoring.target_profile,
        score_version=pipeline.scoring.score_version,
    )
    if args.missing_out:
        missing_out = args.missing_out if args.missing_out.is_absolute() else root / args.missing_out
        write_missing(missing_out, missing)
    if not rows:
        print(f"No scored rows found for {summary}")
        if missing:
            print(f"Missing score rows: {len(missing)}")
        return
    write_csv(summary, rows)
    print(f"Wrote {len(rows)} scored rows: {summary}")
    if missing:
        print(f"Missing score rows: {len(missing)}")


if __name__ == "__main__":
    main()
