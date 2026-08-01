#!/usr/bin/env python3
"""Unified candidate proposal entry point.

The first supported strategy is deterministic variants: a side-effect-free
configuration path for migrating old round-specific candidate scripts.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


_SIM_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _SIM_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.optimizer.variants import build_plan_rows, load_variant_config, validate_config, write_plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Propose filter candidates from optimizer configuration.")
    parser.add_argument(
        "--config",
        type=Path,
        default=_SIM_ROOT / "config" / "optimizer" / "i7_fr4_deterministic_variant_probe.json",
        help="Candidate proposal configuration.",
    )
    parser.add_argument("--out-plan", type=Path, default=None, help="Override output plan CSV path.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print rows without writing a plan.")
    parser.add_argument("--validate-only", action="store_true", help="Validate config without writing a plan.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_variant_config(args.config.resolve(), _SIM_ROOT)
    errors = validate_config(config)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    rows = build_plan_rows(config)
    print(f"strategy: {config.strategy}")
    print(f"project: {config.project_id}")
    print(f"device: {config.device_id}")
    print(f"variants: {len(rows)}")

    for row in rows:
        print(f"  {row['name']}: {row.get('notes', '')}")

    if args.validate_only or args.dry_run:
        return 0

    out_plan = args.out_plan.resolve() if args.out_plan else config.plan
    if out_plan is None:
        print("ERROR: no plan configured; pass --out-plan or set plan in config", file=sys.stderr)
        return 1
    write_plan(out_plan, config.output_fields, rows)
    print(f"wrote plan: {out_plan}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
