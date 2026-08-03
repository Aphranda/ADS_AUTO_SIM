#!/usr/bin/env python3
"""Run ADS/RFPro filter candidates concurrently in one ADS workspace."""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

_SIM_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _SIM_ROOT / "src"
_TOOLS_ROOT = _SIM_ROOT / "tools"
for _path in (_SRC_ROOT, _TOOLS_ROOT):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from ads_profiles import resolve_ads_python, resolve_host_python, resolve_library, resolve_workspace
from run_ads_filter_sweep import (
    ads_cell_name,
    TARGET_SCORE_VERSIONS,
    apply_project_defaults,
    candidate_output_name,
    cell_name,
    infer_round_id,
    read_plan,
    rebuild_full_summary_from_scores,
    run_command,
    run_layout_gate,
    run_pipeline_gate,
)
from simads.runtime import classify_exception, create_run_id


@dataclass
class RunningCandidate:
    candidate: str
    cell: str
    run_id: str
    run_dir: Path
    score_path: Path
    process: subprocess.Popen[bytes]
    stdout_file: object
    stderr_file: object
    started: float
    stdout_log: Path
    stderr_log: Path


def repo_root() -> Path:
    return _SIM_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ADS/RFPro candidates concurrently in one workspace.")
    parser.add_argument("--plan", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--results-dir", type=Path, default=None)
    parser.add_argument("--summary", type=Path, default=None)
    parser.add_argument(
        "--backend",
        choices=["ads", "auto", "hfss", "both"],
        default="ads",
        help="Parallel runner currently supports ADS/RFPro only.",
    )
    parser.add_argument("--profile", default=None)
    parser.add_argument("--ads-python", type=Path, default=None)
    parser.add_argument("--host-python", type=Path, default=None)
    parser.add_argument("--workspace", type=Path, default=None)
    parser.add_argument("--library", default=None)
    parser.add_argument("--project-id", default="bfp_6_8g_i7_fr4")
    parser.add_argument("--sweep-id", default=None)
    parser.add_argument("--pipeline-id", default=None)
    parser.add_argument("--device-id", default=None)
    parser.add_argument("--round-id", default=None)
    parser.add_argument("--template-cell", default=None)
    parser.add_argument("--setup-view", default=None)
    parser.add_argument("--rfpro-emsetup-view", default=None)
    parser.add_argument("--stackup-config", type=Path, default=None)
    parser.add_argument("--stackup-named-outputs", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--name-stackup-token", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--target-profile", default=None)
    parser.add_argument("--candidates", nargs="*", default=None)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--skip-generate", action="store_true")
    parser.add_argument("--force-import-existing", action="store_true")
    parser.add_argument(
        "--force-generated-dxf-subset",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Force generated-DXF fallback import so configured ground layers become ADS GND planes.",
    )
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--skip-fem", action="store_true")
    parser.add_argument("--score-source", default="rfpro-csv", choices=["rfpro-csv", "fem-dataset"])
    parser.add_argument("--fem-dataset-suffix", default="a")
    parser.add_argument("--export-fem-txt", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--skip-pipeline-check", action="store_true")
    parser.add_argument("--skip-layout-check", action="store_true")
    parser.add_argument("--strict-layout-check", action="store_true")
    parser.add_argument("--layout-topology-check", choices=("auto", "none", "pixel_qr_bpf"), default="auto")
    parser.add_argument("--min-metal-spacing-mm", type=float, default=0.1016)
    parser.add_argument("--max-island-components", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def command_for_candidate(
    args: argparse.Namespace,
    *,
    candidate: str,
    cell: str,
    run_id: str,
    run_dir: Path,
    score_path: Path,
    root: Path,
    workspace: Path,
    library: str,
    ads_python: Path,
    host_python: Path,
) -> list[str]:
    source_cell = cell_name(candidate)
    command = [
        str(host_python),
        str(root / "tools" / "run_ads_filter_candidate.py"),
        candidate,
        "--device-id",
        args.device_id,
        "--profile",
        args.profile,
        "--pipeline-id",
        args.pipeline_id or "",
        "--ads-python",
        str(ads_python),
        "--host-python",
        str(host_python),
        "--workspace",
        str(workspace),
        "--library",
        library,
        "--project-id",
        args.project_id,
        "--round-id",
        args.round_id,
        "--run-id",
        run_id,
        "--run-dir",
        str(run_dir),
        "--template-cell",
        args.template_cell,
        "--setup-view",
        args.setup_view,
        "--dxf",
        str(args.out_dir / f"{source_cell}.dxf"),
        "--params",
        str(args.out_dir / f"{candidate}_params.json"),
        "--cell",
        cell,
        "--overwrite-setup",
        "--out",
        str(args.results_dir / f"{cell}_rfpro.csv"),
        "--score-out",
        str(score_path),
        "--score-source",
        args.score_source,
        "--fem-dataset-suffix",
        args.fem_dataset_suffix,
        "--target-profile",
        args.target_profile,
    ]
    if args.rfpro_emsetup_view is not None:
        command.extend(["--rfpro-emsetup-view", args.rfpro_emsetup_view])
    if args.stackup_config is not None:
        command.extend(["--stackup-config", str(args.stackup_config)])
    if args.force_generated_dxf_subset:
        command.append("--force-generated-dxf-subset")
    if args.export_fem_txt:
        command.extend(["--fem-txt-out", str(args.results_dir / f"{cell}_FEM_{args.fem_dataset_suffix}.txt")])
    existing_layout = workspace / library / cell / "layout"
    if existing_layout.exists() and not args.force_import_existing:
        command.append("--reuse-layout")
    if args.prepare_only:
        command.append("--prepare-only")
    if args.skip_fem:
        command.append("--skip-fem")
    return command


def close_logs(run: RunningCandidate) -> None:
    run.stdout_file.close()
    run.stderr_file.close()


def write_parallel_report(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "candidate",
        "cell",
        "status",
        "returncode",
        "elapsed_s",
        "elapsed_min",
        "run_id",
        "run_dir",
        "stdout_log",
        "stderr_log",
        "score_path",
    ]
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    if args.workers < 1:
        raise SystemExit("--workers must be at least 1")
    if args.backend != "ads":
        raise SystemExit("HFSS backend is supported by tools/run_ads_filter_sweep.py for now; parallel runner is ADS/RFPro only.")

    root = repo_root()
    args._explicit_paths = {
        "out_dir": args.out_dir is not None,
        "results_dir": args.results_dir is not None,
        "summary": args.summary is not None,
    }
    apply_project_defaults(args, root)
    run_pipeline_gate(args)
    ads_python = resolve_ads_python(args.profile, args.ads_python)
    host_python = resolve_host_python(args.profile, args.host_python)
    workspace = resolve_workspace(args.profile, args.workspace)
    library = resolve_library(args.profile, args.library)
    args.round_id = args.round_id or infer_round_id(str(args.plan), str(args.out_dir), str(args.results_dir), str(args.summary))

    rows = read_plan(args.plan)
    selected_source = args.candidates or [row["name"].strip() for row in rows]
    selected = [candidate_output_name(args, candidate) for candidate in selected_source]
    plan_rows = {candidate_output_name(args, row["name"].strip()): row for row in rows}
    score_version = (
        args._pipeline_config.scoring.score_version
        if args._pipeline_config is not None and args.target_profile == args._pipeline_config.scoring.target_profile
        else TARGET_SCORE_VERSIONS[args.target_profile]
    )

    if not args.skip_generate:
        generate_script = (args._pipeline_config.layout.sweep_script if args._pipeline_config else None) or (root / "tools" / "generate_filter_sweep.py")
        generate_command = [str(host_python), str(generate_script), "--plan", str(args.plan), "--out-dir", str(args.out_dir)]
        if args.stackup_config is not None:
            generate_command.extend(["--stackup-config", str(args.stackup_config)])
            generate_command.append("--name-stackup-token" if args.name_stackup_token else "--no-name-stackup-token")
        run_command(
            "Generate candidate DXF/JSON files",
            generate_command,
            root,
            args.dry_run,
        )

    args.results_dir.mkdir(parents=True, exist_ok=True)
    log_dir = args.results_dir / "parallel_logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    pending = list(selected)
    running: list[RunningCandidate] = []
    report_rows: list[dict[str, str]] = []
    failed_rows: list[dict[str, str]] = []
    run_infos: list[dict[str, object]] = []
    sweep_started = time.monotonic()

    while pending or running:
        while pending and len(running) < args.workers:
            candidate = pending.pop(0)
            cell = ads_cell_name(candidate, force_generated_dxf_subset=args.force_generated_dxf_subset)
            run_layout_gate(args, candidate)
            run_id = create_run_id(args.project_id, args.round_id, candidate, args.profile)
            run_dir = args.results_dir / "runs" / run_id
            score_path = args.results_dir / f"{cell}_score.csv"
            stdout_log = log_dir / f"{candidate}_stdout.log"
            stderr_log = log_dir / f"{candidate}_stderr.log"
            command = command_for_candidate(
                args,
                candidate=candidate,
                cell=cell,
                run_id=run_id,
                run_dir=run_dir,
                score_path=score_path,
                root=root,
                workspace=workspace,
                library=library,
                ads_python=ads_python,
                host_python=host_python,
            )
            print(f"[parallel] start {candidate}: {' '.join(command)}", flush=True)
            stdout_file = stdout_log.open("wb")
            stderr_file = stderr_log.open("wb")
            if args.dry_run:
                stdout_file.close()
                stderr_file.close()
                continue
            process = subprocess.Popen(command, cwd=root, stdout=stdout_file, stderr=stderr_file)
            running.append(
                RunningCandidate(
                    candidate=candidate,
                    cell=cell,
                    run_id=run_id,
                    run_dir=run_dir,
                    score_path=score_path,
                    process=process,
                    stdout_file=stdout_file,
                    stderr_file=stderr_file,
                    started=time.monotonic(),
                    stdout_log=stdout_log,
                    stderr_log=stderr_log,
                )
            )
            run_infos.append(
                {
                    "candidate": candidate,
                    "cell": cell,
                    "run_id": run_id,
                    "run_dir": run_dir,
                    "score_path": score_path,
                    "pipeline_id": args.pipeline_id or "",
                }
            )

        still_running: list[RunningCandidate] = []
        for run in running:
            returncode = run.process.poll()
            if returncode is None:
                still_running.append(run)
                continue

            close_logs(run)
            elapsed = time.monotonic() - run.started
            status = "completed" if returncode == 0 else "failed"
            report_rows.append(
                {
                    "candidate": run.candidate,
                    "cell": run.cell,
                    "status": status,
                    "returncode": str(returncode),
                    "elapsed_s": f"{elapsed:.3f}",
                    "elapsed_min": f"{elapsed / 60.0:.3f}",
                    "run_id": run.run_id,
                    "run_dir": str(run.run_dir),
                    "stdout_log": str(run.stdout_log),
                    "stderr_log": str(run.stderr_log),
                    "score_path": str(run.score_path),
                }
            )
            print(f"[parallel] done {run.candidate}: status={status} elapsed={elapsed:.1f}s", flush=True)
            if returncode != 0:
                failed_rows.append(
                    {
                        "candidate": run.candidate,
                        "cell": run.cell,
                        "status": "failed",
                        "error_class": classify_exception(subprocess.CalledProcessError(returncode, run.candidate)),
                        "failed_step": "run_ads_filter_candidate.py",
                        "elapsed_s": f"{elapsed:.1f}",
                        "run_id": run.run_id,
                        "run_dir": str(run.run_dir),
                        "profile_id": args.profile,
                        "pipeline_id": args.pipeline_id or "",
                        "target_profile_id": args.target_profile,
                        "score_version": score_version,
                        "notes": plan_rows.get(run.candidate, {}).get("notes", ""),
                    }
                )
                if not args.continue_on_error:
                    pending.clear()
        running = still_running
        write_parallel_report(args.results_dir / "parallel_run_report.csv", report_rows)
        if running:
            time.sleep(5.0)

    total_elapsed = time.monotonic() - sweep_started
    print(f"[parallel] total elapsed={total_elapsed:.1f}s workers={args.workers}", flush=True)
    write_parallel_report(args.results_dir / "parallel_run_report.csv", report_rows)

    if not args.prepare_only and not args.skip_fem and not args.dry_run:
        rebuild_full_summary_from_scores(
            args,
            failed_rows,
            profile_id=args.profile,
            target_profile_id=args.target_profile,
            score_version=score_version,
        )


if __name__ == "__main__":
    main()
