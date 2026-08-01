#!/usr/bin/env python3
"""Inspect or score ADS dataset files produced by FEM/RFPro simulations."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.scoring import (
    DEFAULT_TARGET_PROFILE,
    TARGET_PROFILES,
    TARGET_SCORE_VERSIONS,
    choose_frequency_column,
    choose_sparam_column,
    frequency_to_ghz,
    score_rfpro_csv,
    score_vectors,
    series_to_db,
)


def attach_run_metadata(rows: list[dict[str, str]], args: argparse.Namespace) -> list[dict[str, str]]:
    score_version = args.score_version or TARGET_SCORE_VERSIONS[args.target_profile]
    metadata = {
        "run_id": args.run_id or "",
        "project_id": args.project_id or "",
        "round_id": args.round_id or "",
        "candidate_id": args.candidate_id or "",
        "profile_id": args.profile_id or "",
        "pipeline_id": args.pipeline_id or "",
        "target_profile_id": args.target_profile_id or args.target_profile,
        "score_version": score_version,
        "error_class": args.error_class or "",
        "failed_step": args.failed_step or "",
        "elapsed_s": f"{args.elapsed_s:.3f}" if args.elapsed_s is not None else "",
    }
    return [{**metadata, **row, "target_profile_id": metadata["target_profile_id"]} for row in rows]


def score_dataset(path: Path, inspect: bool, targets: dict[str, float], target_profile: str) -> list[dict[str, str]]:
    import keysight.ads.dataset as dataset

    scores: list[dict[str, str]] = []
    with dataset.open(path) as ds:
        if inspect:
            print(f"{path}")
            print(f"  varblocks: {list(ds.varblock_names)}")
        for block_name in ds.varblock_names:
            block = ds[block_name]
            if inspect:
                print(f"  [{block_name}]")
                print(f"    ivars: {[var.name for var in block.ivars]}")
                print(f"    dvars: {[var.name for var in block.dvars]}")

            df = block.to_dataframe().reset_index()
            columns = list(df.columns)
            freq_col = choose_frequency_column(columns)
            s_cols = {name: choose_sparam_column(columns, name) for name in ("s11", "s21", "s12", "s22")}
            if freq_col is None or s_cols["s21"] is None:
                continue

            freq_ghz = frequency_to_ghz(list(df[freq_col]))
            traces = {
                name: series_to_db(list(df[col]))
                for name, col in s_cols.items()
                if col is not None
            }
            scores.append(score_vectors(freq_ghz, traces, f"{path}:{block_name}", targets, target_profile))
    return scores


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect and score ADS .ds or RFPro CSV S-parameter results.")
    parser.add_argument("results", nargs="+", type=Path)
    parser.add_argument("--inspect", action="store_true")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument(
        "--target-profile",
        default=DEFAULT_TARGET_PROFILE,
        choices=sorted(TARGET_PROFILES),
        help="Scoring target set. fr4_25db uses passband >= -5 dB and S21@5GHz <= -25 dB.",
    )
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--project-id", default=None)
    parser.add_argument("--round-id", default=None)
    parser.add_argument("--candidate-id", default=None)
    parser.add_argument("--profile-id", default=None)
    parser.add_argument("--pipeline-id", default=None)
    parser.add_argument("--target-profile-id", default=None)
    parser.add_argument("--score-version", default=None)
    parser.add_argument("--error-class", default=None)
    parser.add_argument("--failed-step", default=None)
    parser.add_argument("--elapsed-s", type=float, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    targets = TARGET_PROFILES[args.target_profile]
    rows: list[dict[str, str]] = []
    for path in args.results:
        if path.suffix.lower() == ".csv":
            rows.append(score_rfpro_csv(path, targets, args.target_profile))
        else:
            rows.extend(score_dataset(path, args.inspect, targets, args.target_profile))

    if not rows:
        raise SystemExit("No scoreable S-parameter traces found. Re-run with --inspect to see dataset contents.")
    rows = attach_run_metadata(rows, args)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {args.out}")
    else:
        writer = csv.DictWriter(__import__("sys").stdout, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
