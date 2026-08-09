#!/usr/bin/env python3
"""Export detailed filter optimization metrics from an S2P file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from simads.scoring.filter_metrics import BandWindow, summarize_filter_s2p


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze S2P metrics useful for filter optimization.")
    parser.add_argument("s2p", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--tdr-csv", type=Path, default=None)
    parser.add_argument("--passband-start-ghz", type=float, default=6.0)
    parser.add_argument("--passband-stop-ghz", type=float, default=8.0)
    parser.add_argument("--tdr-early-max-ns", type=float, default=0.20)
    parser.add_argument("--z0-ohm", type=float, default=50.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = summarize_filter_s2p(
        args.s2p,
        passband=BandWindow(args.passband_start_ghz, args.passband_stop_ghz),
        tdr_csv=args.tdr_csv,
        tdr_early_max_ns=args.tdr_early_max_ns,
        z0_ohm=args.z0_ohm,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
