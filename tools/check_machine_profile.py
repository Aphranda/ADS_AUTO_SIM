#!/usr/bin/env python3
"""Check SIMADS machine, ADS, and HFSS profile auto-detection."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SIM_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _SIM_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.config import (  # noqa: E402
    detect_machine_profile,
    get_ads_profile,
    get_hfss_profile,
    validate_hfss_profile,
    validate_profile,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check machine-based ADS/HFSS profile detection.")
    parser.add_argument("--machine-profile", default="auto", help="Machine profile name or auto.")
    parser.add_argument("--json-out", type=Path, default=None)
    return parser.parse_args()


def _checks_to_dict(checks: list[object]) -> list[dict[str, object]]:
    return [
        {
            "name": getattr(check, "name"),
            "path": str(getattr(check, "path")) if getattr(check, "path") is not None else None,
            "ok": bool(getattr(check, "ok")),
            "message": getattr(check, "message"),
        }
        for check in checks
    ]


def main() -> int:
    args = parse_args()
    detection = detect_machine_profile()
    ads = get_ads_profile(args.machine_profile)
    hfss = get_hfss_profile(args.machine_profile)
    ads_checks = validate_profile(ads, require_template=False)
    hfss_checks = validate_hfss_profile(hfss)
    payload = {
        "schema_version": "1.0",
        "machine_detection": detection.to_dict(),
        "ads_profile": ads.to_dict(),
        "hfss_profile": hfss.to_dict(),
        "ads_checks": _checks_to_dict(ads_checks),
        "hfss_checks": _checks_to_dict(hfss_checks),
    }

    print(f"Machine: {detection.source}, selected={detection.selected}")
    print(f"ADS:     {args.machine_profile} -> {ads.name}")
    print(f"HFSS:    {args.machine_profile} -> {hfss.name}")
    for group, checks in (("ADS", ads_checks), ("HFSS", hfss_checks)):
        for check in checks:
            status = "OK" if check.ok else "WARN"
            print(f"[{status}] {group}.{check.name}: {check.path} ({check.message})")

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote machine profile report: {args.json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
