#!/usr/bin/env python3
"""Check AEDT non-graphical startup and write diagnostics even on failure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from simads.hfss.aedt_startup import (
    aedt_automation_lock,
    apply_grpc_startup_compat,
    apply_pyaedt_settings,
    start_aedt_reaper,
    startup_snapshot,
)

apply_grpc_startup_compat()


def _json_default(value: Any) -> str:
    return str(value)


def _ansys_processes() -> list[dict[str, str]]:
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq ansysedt.exe", "/V", "/FO", "CSV"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except Exception as exc:
        return [{"error": repr(exc)}]
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if len(lines) <= 1:
        return []
    import csv

    rows = []
    for row in csv.DictReader(lines):
        rows.append({str(k): str(v) for k, v in row.items()})
    return rows


def run(args: argparse.Namespace) -> dict[str, Any]:
    started = time.monotonic()
    payload: dict[str, Any] = {
        "status": "starting",
        "project": str(args.project) if args.project else None,
        "design": args.design,
        "version": args.version,
        "non_graphical": args.non_graphical,
        "new_desktop": args.new_desktop,
        "remove_lock": args.remove_lock,
        "before_ansysedt_processes": _ansys_processes(),
    }
    try:
        from ansys.aedt.core import Hfss3dLayout, settings

        apply_pyaedt_settings(settings)
        payload["aedt_startup"] = startup_snapshot(settings)
        with aedt_automation_lock("check_aedt_non_graphical_startup") as lock_info:
            payload["aedt_lock"] = lock_info
            app = Hfss3dLayout(
                project=str(args.project) if args.project else None,
                design=args.design,
                version=args.version,
                non_graphical=args.non_graphical,
                new_desktop=args.new_desktop,
                close_on_exit=False,
                remove_lock=args.remove_lock,
            )
            payload["aedt_reaper"] = start_aedt_reaper(
                app,
                label="check_aedt_non_graphical_startup",
                execute=not args.keep_attached,
                script_started=bool(args.new_desktop and args.non_graphical),
            )
            try:
                payload.update(
                    {
                        "status": "ok",
                        "project_name": getattr(app, "project_name", None),
                        "design_name": getattr(app, "design_name", None),
                        "design_type": getattr(app, "design_type", None),
                        "setup_names": list(getattr(app, "setup_names", []) or []),
                        "port_list": list(getattr(app, "port_list", []) or []),
                    }
                )
            finally:
                if not args.keep_attached:
                    app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)
    except BaseException as exc:
        payload.update(
            {
                "status": "failed",
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }
        )
    finally:
        payload["elapsed_s"] = round(time.monotonic() - started, 3)
        payload["after_ansysedt_processes"] = _ansys_processes()
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check AEDT non-graphical startup without modifying a project.")
    parser.add_argument("--project", type=Path, default=None)
    parser.add_argument("--design", default=None)
    parser.add_argument("--version", default="2026.1")
    parser.add_argument("--non-graphical", action="store_true", default=True)
    parser.add_argument("--graphical", action="store_false", dest="non_graphical")
    parser.add_argument("--new-desktop", action="store_true", default=True)
    parser.add_argument("--attach-existing", action="store_false", dest="new_desktop")
    parser.add_argument("--remove-lock", action="store_true")
    parser.add_argument("--keep-attached", action="store_true")
    parser.add_argument("--close-projects", action="store_true", default=True)
    parser.add_argument("--close-desktop", action="store_true", default=True)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = run(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if payload.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
