#!/usr/bin/env python3
"""Compare measured BPF markers with simulated optimization metrics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from simads.scoring.filter_measurement_compare import compare_measurement_to_simulation, write_comparison_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare measured BPF S21 markers against simulated metrics.")
    parser.add_argument("--measured", type=Path, required=True)
    parser.add_argument("--simulation-metrics", type=Path, required=True)
    parser.add_argument("--csv-out", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = compare_measurement_to_simulation(args.measured, args.simulation_metrics)
    write_comparison_csv(payload, args.csv_out)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.csv_out}")
    print(f"Wrote {args.json_out}")


if __name__ == "__main__":
    main()
