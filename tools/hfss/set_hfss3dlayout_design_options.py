#!/usr/bin/env python3
"""Set HFSS 3D Layout design options on an existing AEDT project."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import shutil
import sys
from typing import Any

_SIM_ROOT = Path(__file__).resolve().parents[2]
_SRC_ROOT = _SIM_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.hfss.build import configure_design_intersection_check


def _json_default(value: Any) -> str:
    return str(value)


def _load_json_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON must be an object: {path}")
    return data


def _designs_from_project_config(path: Path) -> list[str]:
    data = _load_json_object(path)
    hfss = data.get("hfss", {})
    if not isinstance(hfss, dict):
        return []
    simulations = hfss.get("simulations", {})
    if not isinstance(simulations, dict):
        return []
    designs: list[str] = []
    for item in simulations.values():
        if not isinstance(item, dict):
            continue
        design = item.get("design")
        if design and str(design) not in designs:
            designs.append(str(design))
    return designs


def _project_sidecars(project: Path) -> list[Path]:
    paths = [project]
    for suffix in [".aedb", ".aedtresults"]:
        sidecar = project.with_suffix(suffix)
        if sidecar.exists():
            paths.append(sidecar)
    return paths


def _backup_project(project: Path, *, tag: str) -> list[str]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    copied: list[str] = []
    ignore_runtime_locks = shutil.ignore_patterns("*.semaphore", "*.lock", "*.tmp")
    for src in _project_sidecars(project):
        dst = src.with_name(f"{src.stem}.before_{tag}_{stamp}{src.suffix}")
        if src.is_dir():
            shutil.copytree(src, dst, ignore=ignore_runtime_locks)
        else:
            shutil.copy2(src, dst)
        copied.append(str(dst))
    return copied


def set_design_options(args: argparse.Namespace) -> dict[str, Any]:
    from ansys.aedt.core import Hfss3dLayout

    designs = list(dict.fromkeys(args.design))
    if args.project_config is not None:
        for design in _designs_from_project_config(args.project_config):
            if design not in designs:
                designs.append(design)
    if not designs:
        raise ValueError("no design selected; use --design or --project-config")

    backups = [] if args.no_backup else _backup_project(args.project, tag="design_options")
    results: list[dict[str, Any]] = []
    app = None
    for index, design in enumerate(designs):
        app = Hfss3dLayout(
            project=str(args.project),
            design=design,
            version=args.version,
            non_graphical=args.non_graphical,
            new_desktop=args.new_desktop if index == 0 else False,
            close_on_exit=False,
            remove_lock=args.remove_lock,
        )
        try:
            result = configure_design_intersection_check(app, args.enable_design_intersection_check)
            results.append({"design": design, "status": "updated", "design_options": result})
        except Exception as exc:  # pragma: no cover - depends on AEDT COM/gRPC.
            results.append({"design": design, "status": "failed", "error": repr(exc)})
            if not args.continue_on_error:
                raise

    if app is not None and args.save:
        app.save_project()
    if app is not None and not args.keep_open:
        app.release_desktop(close_projects=False, close_desktop=False)

    return {
        "project": str(args.project),
        "project_config": str(args.project_config) if args.project_config else None,
        "backups": backups,
        "save": args.save,
        "keep_open": args.keep_open,
        "enable_design_intersection_check": args.enable_design_intersection_check,
        "designs": results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Set HFSS 3D Layout design options on an existing AEDT project.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--project-config", type=Path, default=None, help="Read design names from config/projects/<id>.json.")
    parser.add_argument("--design", action="append", default=[], help="Design name. Can be repeated.")
    parser.add_argument(
        "--enable-design-intersection-check",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Set HFSS Meshing Method > Enable Design-level intersection checks.",
    )
    parser.add_argument("--version", default="2026.1")
    parser.add_argument("--non-graphical", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--new-desktop", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--remove-lock", action="store_true")
    parser.add_argument("--save", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--keep-open", action="store_true")
    parser.add_argument("--no-backup", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--json-out", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = set_design_options(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    failed = [item for item in payload["designs"] if item.get("status") != "updated"]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
