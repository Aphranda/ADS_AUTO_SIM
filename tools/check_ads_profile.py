#!/usr/bin/env python3
"""Validate configured ADS automation profiles without launching FEM."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SIM_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _SIM_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.config import detect_machine_profile, get_ads_profile, profile_names, validate_profile


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate ADS profile paths and core fields.")
    parser.add_argument("--profile", default="auto", choices=profile_names(include_auto=True))
    parser.add_argument("--require-template", action="store_true", help="Check template cell directory as well.")
    parser.add_argument("--require-mcp", action="store_true", help="Check the ADS MCP executable as well.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero if any check fails.")
    parser.add_argument("--json-out", type=Path, default=None, help="Optional JSON report path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    profile = get_ads_profile(args.profile)
    detection = detect_machine_profile()
    checks = validate_profile(profile, require_template=args.require_template, require_mcp=args.require_mcp)
    payload = {
        "schema_version": "1.0",
        "requested_profile": args.profile,
        "machine_detection": detection.to_dict(),
        "profile": profile.to_dict(),
        "checks": [
            {
                "name": check.name,
                "path": str(check.path) if check.path is not None else None,
                "ok": check.ok,
                "message": check.message,
            }
            for check in checks
        ],
    }

    print(f"Profile: {args.profile} -> {profile.name}")
    print(f"Machine detection: {detection.source}, selected={detection.selected}")
    for check in checks:
        status = "OK" if check.ok else "WARN"
        print(f"[{status}] {check.name}: {check.path} ({check.message})")

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        with args.json_out.open("w", encoding="utf-8") as fp:
            json.dump(payload, fp, ensure_ascii=False, indent=2)
            fp.write("\n")
        print(f"Wrote profile check report: {args.json_out}")

    failed = [check for check in checks if not check.ok]
    if failed and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
