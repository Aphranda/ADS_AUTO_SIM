#!/usr/bin/env python3
"""Rebuild a backend-neutral run summary from run manifests."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SIM_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _SIM_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.workflows.backend_summary import build_backend_summary, write_backend_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build backend_summary.csv from run manifests.")
    parser.add_argument("paths", nargs="+", type=Path, help="Run directories or directories containing runs.")
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_backend_summary(args.paths)
    write_backend_summary(args.out, rows)
    print(f"Wrote {len(rows)} backend rows: {args.out}")


if __name__ == "__main__":
    main()
