#!/usr/bin/env python3
"""Build and validate an HTML report asset manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from simads.reports import ReportManifestError, write_report_manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build report_manifest.json for an HTML report directory.")
    parser.add_argument("--report-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--allow-invalid", action="store_true", help="Write manifest even if local references are invalid.")
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    try:
        payload = write_report_manifest(args.report_dir, output_path=args.output, strict=not args.allow_invalid)
    except ReportManifestError as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
