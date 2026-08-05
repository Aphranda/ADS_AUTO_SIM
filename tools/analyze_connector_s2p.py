#!/usr/bin/env python3
"""Score Touchstone S2P files for SMA connector launch simulations."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from simads.scoring.connector import ConnectorScoreProfile, read_s2p_db, score_s2p


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze connector launch S2P files over a full-band frequency range.")
    parser.add_argument("s2p", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, default=None, help="Optional CSV summary path.")
    parser.add_argument("--band-min-ghz", type=float, default=0.5)
    parser.add_argument("--band-max-ghz", type=float, default=10.0)
    parser.add_argument("--profile-id", default="sma_launch_fullband_0p5_10g_v1")
    parser.add_argument("--target-worst-return-db", type=float, default=-10.0)
    parser.add_argument("--target-s21-min-db", type=float, default=-1.5)
    parser.add_argument("--target-s21-avg-db", type=float, default=-0.75)
    parser.add_argument("--target-s21-ripple-db", type=float, default=1.0)
    parser.add_argument("--target-balance-db", type=float, default=1.5)
    return parser.parse_args()


def build_profile(args: argparse.Namespace) -> ConnectorScoreProfile:
    return ConnectorScoreProfile(
        profile_id=args.profile_id,
        band_min_ghz=args.band_min_ghz,
        band_max_ghz=args.band_max_ghz,
        target_worst_return_db=args.target_worst_return_db,
        target_s21_min_db=args.target_s21_min_db,
        target_s21_avg_db=args.target_s21_avg_db,
        target_s21_ripple_db=args.target_s21_ripple_db,
        target_balance_db=args.target_balance_db,
    )


def main() -> None:
    args = parse_args()
    profile = build_profile(args)
    rows = [score_s2p(path, profile) for path in args.s2p]
    fieldnames = list(rows[0].keys())
    if args.out:
        with args.out.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {args.out}")
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
