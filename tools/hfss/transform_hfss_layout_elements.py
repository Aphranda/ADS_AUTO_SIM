#!/usr/bin/env python3
"""Generate an HFSS layout JSON candidate by transforming selected elements."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

_SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.hfss.layout_elements import load_layout_element_policy, select_layout_elements, translate_layout_elements
from simads.hfss.layout_io import load_layout


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def transform_layout(args: argparse.Namespace) -> dict[str, Any]:
    layout = load_layout(args.layout)
    policy = load_layout_element_policy(args.element_policy)
    before = select_layout_elements(layout, policy)
    candidate = translate_layout_elements(
        layout,
        policy,
        dx_mm=args.dx_mm,
        dy_mm=args.dy_mm,
        layout_scope=args.scope,
        layout_id=args.layout_id,
        shift_regions=args.shift_region,
    )
    after = select_layout_elements(candidate, policy)
    _write_json(args.out, candidate)
    summary = {
        "layout": str(args.layout),
        "out": str(args.out),
        "layout_id": candidate.get("layout_id"),
        "scope": args.scope,
        "operation": "translate",
        "dx_mm": args.dx_mm,
        "dy_mm": args.dy_mm,
        "shift_regions": list(args.shift_region),
        "selected_before": [str(shape.get("name") or "") for shape in before],
        "selected_after": [str(shape.get("name") or "") for shape in after],
        "selected_count_before": len(before),
        "selected_count_after": len(after),
        "element_policy": policy.to_mapping(),
    }
    if args.summary_out:
        _write_json(args.summary_out, summary)
    return summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transform selected HFSS layout JSON elements into a candidate layout.")
    parser.add_argument("--layout", type=Path, required=True)
    parser.add_argument("--element-policy", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path, default=None)
    parser.add_argument("--layout-id", default=None)
    parser.add_argument("--scope", default="layout-elements")
    parser.add_argument("--dx-mm", type=float, default=0.0)
    parser.add_argument("--dy-mm", type=float, default=0.0)
    parser.add_argument("--shift-region", action="append", default=[])
    return parser.parse_args(argv)


def main() -> int:
    payload = transform_layout(parse_args())
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
