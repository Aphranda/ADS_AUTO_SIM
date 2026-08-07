#!/usr/bin/env python3
"""Unified config-backed S-parameter scoring CLI."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from simads.scoring.interface import score_sparameter_files


DEFAULT_PROFILE_IDS = {
    "filter": "fr4_25db_rl6",
    "connector": "sma_launch_fullband_0p5_10g_v2",
    "sp8t": "sp8t_four_port_connector_isolation_0p5_10g_v1",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score S-parameter files through the unified scoring interface.")
    parser.add_argument("s2p", nargs="+", type=Path)
    parser.add_argument("--system", choices=sorted(DEFAULT_PROFILE_IDS), required=True)
    parser.add_argument("--profile-id", default=None, help="Scoring profile id under config/scoring.")
    parser.add_argument("--profile-path", type=Path, default=None, help="Optional explicit scoring profile JSON.")
    parser.add_argument("--baseline-s2p", type=Path, default=None, help="Baseline S2P for baseline-relative profiles.")
    parser.add_argument("--out", type=Path, default=None, help="Optional CSV summary path.")
    return parser.parse_args()


def profile_id_from_path(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or not data.get("profile_id"):
        raise ValueError(f"profile JSON missing profile_id: {path}")
    return str(data["profile_id"])


def write_rows(rows: list[dict[str, str]], out: Path | None) -> None:
    fieldnames = list(rows[0].keys())
    if out:
        with out.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {out}")
        return
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def main() -> None:
    args = parse_args()
    profile_id = args.profile_id
    if profile_id is None and args.profile_path is not None:
        profile_id = profile_id_from_path(args.profile_path)
    if profile_id is None:
        profile_id = DEFAULT_PROFILE_IDS[args.system]
    rows = score_sparameter_files(
        args.s2p,
        system=args.system,
        profile_id=profile_id,
        profile_path=args.profile_path,
        baseline_path=args.baseline_s2p,
    )
    write_rows(rows, args.out)


if __name__ == "__main__":
    main()
