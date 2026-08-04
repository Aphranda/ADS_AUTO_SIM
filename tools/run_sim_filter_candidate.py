#!/usr/bin/env python3
"""Standard single-candidate simulator entrypoint for ADS and HFSS backends."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

_SIM_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _SIM_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.config import get_hfss_profile, load_pipeline, load_project, resolve_pipeline_id
from simads.hfss_contracts import HFSS_PROJECT_ACTIONS, HFSS_PROJECT_MODELS


def repo_root() -> Path:
    return _SIM_ROOT


def selected_backends(value: str, configured: tuple[str, ...]) -> tuple[str, ...]:
    if value == "auto":
        return configured
    if value == "ads":
        return ("ads_rfpro",)
    if value == "hfss":
        return ("hfss3dlayout",)
    if value == "both":
        return ("ads_rfpro", "hfss3dlayout")
    raise ValueError(f"unsupported backend: {value}")


def hfss_project_name(candidate: str, project_name: str | None) -> str:
    return project_name or f"{candidate}_hfss"


def build_hfss_command(args: argparse.Namespace, pipeline) -> list[str]:
    if args.layout is None:
        raise ValueError("--layout is required for hfss backend")
    hfss_profile = get_hfss_profile(args.hfss_profile or pipeline.hfss.profile or "auto")
    workflow = pipeline.hfss.workflow_script or Path("tools/hfss/run_hfss3dlayout_filter_verdict.py")
    out_dir = args.out_dir or repo_root() / "projects" / pipeline.project_id / "results" / "hfss" / args.candidate
    project_model = args.hfss_project_model or pipeline.hfss.project_model
    project_action = args.hfss_project_action or pipeline.hfss.project_action
    aedt_project = args.hfss_project or pipeline.hfss.aedt_project
    command = [
        str(hfss_profile.host_python),
        str(workflow),
        "--profile",
        hfss_profile.name,
        "--layout",
        str(args.layout),
        "--out-dir",
        str(out_dir),
        "--project-model",
        project_model,
        "--project-action",
        project_action,
        "--design",
        pipeline.hfss.design,
        "--version",
        pipeline.hfss.version,
        "--route",
        pipeline.hfss.route,
        "--port-type",
        pipeline.hfss.port_type,
        "--gnd-boundary-mode",
        pipeline.hfss.gnd_boundary_mode,
        "--start-ghz",
        f"{pipeline.frequency.start_ghz:g}",
        "--stop-ghz",
        f"{pipeline.frequency.stop_ghz:g}",
        "--points",
        str(pipeline.frequency.points),
        "--sweep-type",
        "Interpolating" if pipeline.frequency.plan_type == "Adaptive" else "Discrete",
        "--project-id",
        pipeline.project_id,
        "--pipeline-id",
        pipeline.pipeline_id,
        "--profile-id",
        hfss_profile.name,
        "--candidate-id",
        args.candidate,
        "--device-id",
        args.device_id or pipeline.device_id,
    ]
    if aedt_project is not None:
        command.extend(["--project", str(aedt_project)])
    else:
        command.extend(["--project-name", hfss_project_name(args.candidate, args.project_name)])
    if args.round_id:
        command.extend(["--round-id", args.round_id])
    if pipeline.hfss.workspace_dir is not None:
        command.extend(["--workspace-dir", str(pipeline.hfss.workspace_dir)])
    if pipeline.hfss.stackup_config is not None:
        command.extend(["--stackup-config", str(pipeline.hfss.stackup_config)])
    if pipeline.hfss.non_graphical:
        command.append("--non-graphical")
    override_intersection_check = getattr(args, "hfss_enable_design_intersection_check", None)
    enable_intersection_check = (
        override_intersection_check
        if override_intersection_check is not None
        else pipeline.hfss.enable_design_intersection_check
    )
    if enable_intersection_check is not None:
        command.append(
            "--enable-design-intersection-check"
            if enable_intersection_check
            else "--no-enable-design-intersection-check"
        )
    if args.build_only:
        command.append("--build-only")
    if args.hfss_dry_run:
        command.append("--dry-run")
    if args.write_manifest:
        command.append("--write-manifest")
    if args.run_id:
        command.extend(["--run-id", args.run_id])
    if args.run_dir:
        command.extend(["--run-dir", str(args.run_dir)])
    return command


def build_ads_command(args: argparse.Namespace, pipeline) -> list[str]:
    command = [
        sys.executable,
        str(repo_root() / "tools" / "run_ads_filter_candidate.py"),
        args.candidate,
        "--project-id",
        pipeline.project_id,
        "--pipeline-id",
        pipeline.pipeline_id,
    ]
    if args.device_id:
        command.extend(["--device-id", args.device_id])
    if args.sweep_id:
        command.extend(["--sweep-id", args.sweep_id])
    if args.round_id:
        command.extend(["--round-id", args.round_id])
    if args.profile:
        command.extend(["--profile", args.profile])
    if args.out_dir is not None:
        command.extend(["--out", str(args.out_dir)])
    if args.run_id:
        command.extend(["--run-id", args.run_id])
    if args.run_dir:
        command.extend(["--run-dir", str(args.run_dir)])
    if args.ads_prepare_only:
        command.append("--prepare-only")
    return command


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one filter candidate through the configured simulator backend.")
    parser.add_argument("candidate")
    parser.add_argument("--backend", choices=["auto", "ads", "hfss", "both"], default="auto")
    parser.add_argument("--project-id", default="bfp_6_8g_i7_fr4")
    parser.add_argument("--sweep-id", default=None)
    parser.add_argument("--pipeline-id", default=None)
    parser.add_argument("--round-id", default=None)
    parser.add_argument("--device-id", default=None)
    parser.add_argument("--profile", default=None, help="ADS profile override.")
    parser.add_argument("--hfss-profile", default=None, help="HFSS profile override.")
    parser.add_argument("--layout", type=Path, default=None, help="SIM layout JSON for HFSS backend.")
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--hfss-project", type=Path, default=None, help="HFSS AEDT project path override.")
    parser.add_argument("--hfss-project-model", choices=HFSS_PROJECT_MODELS, default=None, help="HFSS AEDT organization model override.")
    parser.add_argument("--hfss-project-action", choices=HFSS_PROJECT_ACTIONS, default=None, help="HFSS project action override: new or add.")
    parser.add_argument(
        "--hfss-enable-design-intersection-check",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Override HFSS Design Settings > Enable Design-level intersection checks.",
    )
    parser.add_argument("--project-name", default=None, help="HFSS AEDT project name override.")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--run-dir", type=Path, default=None)
    parser.add_argument("--build-only", action="store_true", help="HFSS build-only mode.")
    parser.add_argument("--hfss-dry-run", action="store_true", help="Pass --dry-run to HFSS workflow.")
    parser.add_argument("--ads-prepare-only", action="store_true", help="Pass --prepare-only to ADS runner.")
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Print planned commands without executing them.")
    parser.add_argument("--json-out", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project = load_project(args.project_id, root=repo_root())
    sweep = project.get_sweep(args.sweep_id)
    pipeline_id = resolve_pipeline_id(project, sweep, args.pipeline_id)
    if not pipeline_id:
        raise SystemExit("No pipeline_id found. Set --pipeline-id or configure the project sweep.")
    pipeline = load_pipeline(pipeline_id, root=repo_root())
    commands: list[dict[str, object]] = []
    for backend in selected_backends(args.backend, pipeline.simulation_backends):
        if backend == "ads_rfpro":
            commands.append({"backend": backend, "command": build_ads_command(args, pipeline)})
        elif backend == "hfss3dlayout":
            commands.append({"backend": backend, "command": build_hfss_command(args, pipeline)})
        else:
            raise ValueError(f"pipeline backend is not supported by this runner yet: {backend}")

    payload = {"pipeline_id": pipeline.pipeline_id, "project_id": pipeline.project_id, "candidate": args.candidate, "commands": commands}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.dry_run:
        return 0
    for item in commands:
        subprocess.run(item["command"], cwd=repo_root(), check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
