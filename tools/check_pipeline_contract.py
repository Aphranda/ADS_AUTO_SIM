#!/usr/bin/env python3
"""Validate a standard ADS automation pipeline contract without running ADS/FEM."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SIM_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _SIM_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.config import (
    get_ads_profile,
    get_hfss_profile,
    hfss_profile_names,
    load_pipeline,
    load_project,
    profile_names,
    resolve_pipeline_id,
    validate_pipeline,
)


def repo_root() -> Path:
    return _SIM_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check the layout/import/FEM/scoring pipeline contract.")
    parser.add_argument("--project-id", default="bfp_6_8g_i7_fr4")
    parser.add_argument("--sweep-id", default=None)
    parser.add_argument("--pipeline-id", default=None)
    parser.add_argument("--profile", default=None, choices=profile_names(include_auto=True))
    parser.add_argument("--hfss-profile", default=None, choices=hfss_profile_names(include_auto=True))
    parser.add_argument("--json-out", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    project = load_project(args.project_id, root=root)
    sweep = project.get_sweep(args.sweep_id)
    pipeline_id = resolve_pipeline_id(project, sweep, args.pipeline_id)
    if not pipeline_id:
        raise SystemExit("No pipeline_id found. Set --pipeline-id or add pipeline_id to the project/sweep config.")
    pipeline = load_pipeline(pipeline_id, root=root)
    if pipeline.sweep_id:
        sweep = project.get_sweep(pipeline.sweep_id)
    profile_id = args.profile or pipeline.profile_id or project.default_profile or "company"
    profile = get_ads_profile(profile_id)
    hfss_profile_id = args.hfss_profile or pipeline.hfss.profile or "auto"
    hfss_profile = get_hfss_profile(hfss_profile_id) if "hfss3dlayout" in pipeline.simulation_backends else None
    checks = validate_pipeline(pipeline, project=project, profile=profile, hfss_profile=hfss_profile)
    rows = [
        {
            "name": check.name,
            "ok": check.ok,
            "path": str(check.path) if check.path is not None else "",
            "message": check.message,
        }
        for check in checks
    ]

    print(f"pipeline_id: {pipeline.pipeline_id}")
    print(f"project_id:  {project.project_id}")
    print(f"sweep_id:    {sweep.sweep_id if sweep else ''}")
    print(f"profile_id:  {profile_id}")
    if hfss_profile is not None:
        print(f"hfss_profile:{hfss_profile.name}")
    for row in rows:
        status = "PASS" if row["ok"] else "FAIL"
        suffix = f" [{row['path']}]" if row["path"] else ""
        print(f"{status} {row['name']}: {row['message']}{suffix}")

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(
                {
                    "pipeline_id": pipeline.pipeline_id,
                    "project_id": project.project_id,
                    "sweep_id": sweep.sweep_id if sweep else None,
                    "profile_id": profile_id,
                    "hfss_profile_id": hfss_profile.name if hfss_profile is not None else None,
                    "checks": rows,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"Wrote pipeline check report: {args.json_out}")

    return 0 if all(row["ok"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
